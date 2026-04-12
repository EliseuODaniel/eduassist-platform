from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

from _common import (
    Settings,
    assert_condition,
    internal_headers,
    request,
    telegram_webhook_request,
    wait_for_health,
    wait_for_internal_conversation_context,
)


RUN_ID = uuid4().hex[:8]
DEFAULT_OUTPUT = Path(__file__).resolve().parents[2] / "artifacts" / "telegram-gateway-dedicated-smoke-report.json"


def _normalize(value: str) -> str:
    return str(value or "").lower()


def _gateway_status(settings: Settings) -> dict[str, Any]:
    status, _, payload = request(
        "GET",
        f"{settings.telegram_gateway_url}/v1/status",
        headers=internal_headers(settings),
        timeout=20.0,
    )
    assert_condition(status == 200 and isinstance(payload, dict), "telegram_gateway_status_failed")
    return payload


def _runtime_target_from_gateway(status_payload: dict[str, Any]) -> str | None:
    diagnostics = status_payload.get("runtimeDiagnostics")
    if not isinstance(diagnostics, dict):
        return None
    checks = diagnostics.get("checks")
    if not isinstance(checks, list):
        return None
    for item in checks:
        if isinstance(item, dict) and item.get("name") == "ai_orchestrator":
            endpoint = item.get("endpoint")
            return str(endpoint) if isinstance(endpoint, str) and endpoint.strip() else None
    return None


def _assert_gateway_runtime_diagnostics(status_payload: dict[str, Any]) -> None:
    diagnostics = status_payload.get("runtimeDiagnostics")
    assert_condition(isinstance(diagnostics, dict), "telegram_gateway_runtime_diagnostics_missing")
    assert_condition(bool(diagnostics.get("operationalReadiness")), "telegram_gateway_runtime_not_ready")
    blockers = diagnostics.get("blockers")
    assert_condition(not blockers, f"telegram_gateway_runtime_blockers:{blockers}")
    checks = diagnostics.get("checks")
    assert_condition(isinstance(checks, list) and checks, "telegram_gateway_runtime_checks_missing")
    mode_mismatches = [
        str(item.get("name"))
        for item in checks
        if isinstance(item, dict) and str(item.get("status") or "").strip() == "mode_mismatch"
    ]
    assert_condition(not mode_mismatches, f"telegram_gateway_mode_mismatch:{','.join(mode_mismatches)}")


def _recent_message_contents(payload: dict[str, Any]) -> list[str]:
    recent_messages = payload.get("recent_messages")
    if not isinstance(recent_messages, list):
        return []
    contents: list[str] = []
    for item in recent_messages:
        if isinstance(item, dict):
            content = item.get("content")
            if isinstance(content, str):
                contents.append(content)
    return contents


def _context_contains_markers(
    payload: dict[str, Any],
    *,
    prompt: str,
    reply_markers: tuple[str, ...],
) -> bool:
    contents = _recent_message_contents(payload)
    normalized_contents = [_normalize(content) for content in contents]
    normalized_prompt = _normalize(prompt)
    has_prompt = any(normalized_prompt in content for content in normalized_contents)
    has_reply = any(any(marker in content for marker in reply_markers) for content in normalized_contents)
    return has_prompt and has_reply and len(contents) >= 2


def _latest_assistant_reply_for_prompt(payload: dict[str, Any], *, prompt: str) -> str | None:
    recent_messages = payload.get("recent_messages")
    if not isinstance(recent_messages, list):
        return None
    normalized_prompt = _normalize(prompt)
    latest_reply: str | None = None
    for index, item in enumerate(recent_messages):
        if not isinstance(item, dict) or item.get("sender_type") != "user":
            continue
        content = item.get("content")
        if not isinstance(content, str) or _normalize(content) != normalized_prompt:
            continue
        if index + 1 >= len(recent_messages):
            continue
        next_item = recent_messages[index + 1]
        if not isinstance(next_item, dict) or next_item.get("sender_type") != "assistant":
            continue
        next_content = next_item.get("content")
        if isinstance(next_content, str) and next_content.strip():
            latest_reply = next_content
    return latest_reply


def _run_public_flow(settings: Settings) -> dict[str, Any]:
    chat_id = 777100 + int(RUN_ID[:4], 16) % 800
    update_id = 700000 + int(RUN_ID[:5], 16) % 100000
    prompt = "quais documentos sao exigidos para matricula?"
    status, _, payload = telegram_webhook_request(
        settings,
        update_id=update_id,
        message_id=1,
        text=prompt,
        chat_id=chat_id,
        username=f"smoke.public.{RUN_ID}",
        first_name="SmokePublic",
    )
    assert_condition(status == 200 and isinstance(payload, dict), "telegram_public_webhook_failed")
    assert_condition(payload.get("processed") == "orchestrated_message_enqueued", "telegram_public_not_enqueued")

    conversation_external_id = f"telegram:{chat_id}"
    context = wait_for_internal_conversation_context(
        settings,
        conversation_external_id=conversation_external_id,
        channel="telegram",
        limit=8,
        predicate=lambda body: _context_contains_markers(
            body,
            prompt=prompt,
            reply_markers=("matricula", "matrícula", "document", "cadastro", "secretaria"),
        ),
    )
    return {
        "kind": "public",
        "chat_id": chat_id,
        "update_id": update_id,
        "prompt": prompt,
        "conversation_external_id": conversation_external_id,
        "context": context,
    }


def _run_guardian_flow(settings: Settings, *, guardian_chat_id: int) -> dict[str, Any]:
    update_id = 800000 + int(RUN_ID[:5], 16) % 100000
    prompt = "quais as notas do Lucas Oliveira?"
    status, _, payload = telegram_webhook_request(
        settings,
        update_id=update_id,
        message_id=2,
        text=prompt,
        chat_id=guardian_chat_id,
        username="guardian.smoke",
        first_name="GuardianSmoke",
    )
    assert_condition(status == 200 and isinstance(payload, dict), "telegram_guardian_webhook_failed")
    assert_condition(payload.get("processed") == "orchestrated_message_enqueued", "telegram_guardian_not_enqueued")

    conversation_external_id = f"telegram:{guardian_chat_id}"
    context = wait_for_internal_conversation_context(
        settings,
        conversation_external_id=conversation_external_id,
        channel="telegram",
        limit=8,
        predicate=lambda body: _context_contains_markers(
            body,
            prompt=prompt,
            reply_markers=("lucas oliveira", "biologia", "fisica", "física", "ingles", "inglês"),
        ),
    )
    return {
        "kind": "protected_guardian",
        "chat_id": guardian_chat_id,
        "update_id": update_id,
        "prompt": prompt,
        "conversation_external_id": conversation_external_id,
        "context": context,
    }


def _run_guardian_semantic_ingress_flow(settings: Settings, *, guardian_chat_id: int) -> dict[str, Any]:
    update_id = 810000 + int(RUN_ID[:5], 16) % 100000
    prompt = "bom diazinho"
    status, _, payload = telegram_webhook_request(
        settings,
        update_id=update_id,
        message_id=3,
        text=prompt,
        chat_id=guardian_chat_id,
        username="guardian.semantic",
        first_name="GuardianSemantic",
    )
    assert_condition(status == 200 and isinstance(payload, dict), "telegram_guardian_semantic_webhook_failed")
    assert_condition(payload.get("processed") == "orchestrated_message_enqueued", "telegram_guardian_semantic_not_enqueued")

    conversation_external_id = f"telegram:{guardian_chat_id}"
    context = wait_for_internal_conversation_context(
        settings,
        conversation_external_id=conversation_external_id,
        channel="telegram",
        limit=8,
        predicate=lambda body: _context_contains_markers(
            body,
            prompt=prompt,
            reply_markers=("olá", "ola", "bom dia", "como posso ajudar"),
        ),
    )
    latest_reply = _latest_assistant_reply_for_prompt(context, prompt=prompt)
    assert_condition(isinstance(latest_reply, str) and latest_reply.strip(), "telegram_guardian_semantic_reply_missing")
    normalized_reply = _normalize(latest_reply)
    assert_condition(
        any(marker in normalized_reply for marker in ("olá", "ola", "bom dia", "como posso ajudar")),
        "telegram_guardian_semantic_reply_not_greeting",
    )
    assert_condition("cadastro" not in normalized_reply, "telegram_guardian_semantic_admin_fallback")
    return {
        "kind": "protected_guardian_semantic_ingress",
        "chat_id": guardian_chat_id,
        "update_id": update_id,
        "prompt": prompt,
        "conversation_external_id": conversation_external_id,
        "context": context,
        "reply": latest_reply,
    }


def _write_report(path: Path, report: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Smoke do caminho real telegram-gateway -> runtime dedicado -> api-core.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--guardian-chat-id", type=int, default=None)
    args = parser.parse_args()

    settings = Settings()
    print("Telegram dedicated smoke starting...")
    wait_for_health("api-core", f"{settings.api_core_url}/healthz")
    wait_for_health("telegram-gateway", f"{settings.telegram_gateway_url}/healthz")
    print("[ok] health api-core and telegram-gateway")

    gateway_status = _gateway_status(settings)
    _assert_gateway_runtime_diagnostics(gateway_status)
    runtime_target = _runtime_target_from_gateway(gateway_status)
    print(f"[ok] telegram-gateway status runtime_target={runtime_target or 'unknown'}")

    report: dict[str, Any] = {
        "generated_at": datetime.now(UTC).isoformat(),
        "run_id": RUN_ID,
        "gateway_status": gateway_status,
        "runtime_target": runtime_target,
        "flows": [],
    }

    public_flow = _run_public_flow(settings)
    report["flows"].append(public_flow)
    print("[ok] public gateway flow persisted in api-core")

    if args.guardian_chat_id is not None:
        guardian_flow = _run_guardian_flow(settings, guardian_chat_id=args.guardian_chat_id)
        report["flows"].append(guardian_flow)
        print("[ok] protected guardian gateway flow persisted in api-core")
        guardian_semantic_flow = _run_guardian_semantic_ingress_flow(settings, guardian_chat_id=args.guardian_chat_id)
        report["flows"].append(guardian_semantic_flow)
        print("[ok] protected guardian semantic-ingress flow persisted in api-core")
    else:
        print("[skip] protected guardian flow disabled (use --guardian-chat-id to enable real Telegram-linked validation)")

    _write_report(args.output, report)
    print(f"Telegram dedicated smoke finished successfully. Report: {args.output}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as exc:
        print(f"[fail] {exc}", file=sys.stderr)
        raise SystemExit(1)
