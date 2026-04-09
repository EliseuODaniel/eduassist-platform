from __future__ import annotations

import argparse
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any

import httpx

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MESSAGES = [
    {"label": "student_activation", "text": "do lucas oliveira então"},
    {"label": "all_grades", "text": "quais as notas do lucas"},
    {"label": "subject_grade", "text": "quais as notas de história do lucas?"},
    {"label": "justification_followup", "text": "é atestado de ficar dormindo, serve?"},
    {"label": "finance_followup", "text": "e o financeiro do lucas como está?"},
]
STACKS = ("langgraph", "python_functions", "llamaindex", "specialist_supervisor")


def _set_override(client: httpx.Client, *, stack: str, conversation_id: str, ttl_seconds: int) -> None:
    response = client.post(
        "/v1/internal/runtime/targeted-stack",
        json={
            "stack": stack,
            "reason": "conversation_regression_replay",
            "operator": "codex",
            "ttl_seconds": ttl_seconds,
            "conversation_allowlist": [conversation_id],
        },
    )
    response.raise_for_status()


def _clear_override(client: httpx.Client) -> None:
    response = client.post(
        "/v1/internal/runtime/targeted-stack",
        json={
            "clear_override": True,
            "reason": "conversation_regression_replay_complete",
            "operator": "codex",
        },
    )
    response.raise_for_status()


def _run_stack(
    *,
    client: httpx.Client,
    stack: str,
    conversation_id: str,
    telegram_chat_id: int,
    messages: list[dict[str, str]],
) -> list[dict[str, Any]]:
    _set_override(client, stack=stack, conversation_id=conversation_id, ttl_seconds=3600)
    outputs: list[dict[str, Any]] = []
    try:
        for item in messages:
            response = client.post(
                "/v1/messages/respond",
                json={
                    "message": item["text"],
                    "conversation_id": conversation_id,
                    "telegram_chat_id": telegram_chat_id,
                    "channel": "telegram",
                    "user": {"role": "guardian", "authenticated": True},
                },
            )
            response.raise_for_status()
            payload = response.json()
            outputs.append(
                {
                    "label": item["label"],
                    "question": item["text"],
                    "message_text": payload.get("message_text"),
                    "mode": payload.get("mode"),
                    "reason": payload.get("reason"),
                    "used_llm": payload.get("used_llm"),
                    "llm_stages": payload.get("llm_stages"),
                    "answer_experience_applied": payload.get("answer_experience_applied"),
                    "answer_experience_reason": payload.get("answer_experience_reason"),
                }
            )
    finally:
        _clear_override(client)
    return outputs


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--base-url",
        default=os.getenv("CONTROL_PLANE_ORCHESTRATOR_URL", "http://127.0.0.1:8002"),
    )
    parser.add_argument("--internal-token", default="dev-internal-token")
    parser.add_argument("--telegram-chat-id", type=int, default=1649845499)
    parser.add_argument(
        "--output",
        default=str(REPO_ROOT / "docs/architecture/telegram-conversation-regression-20260404.json"),
    )
    args = parser.parse_args()

    headers = {"X-Internal-Api-Token": args.internal_token}
    report: dict[str, Any] = {
        "generated_at": datetime.now().isoformat(),
        "telegram_chat_id": args.telegram_chat_id,
        "messages": DEFAULT_MESSAGES,
        "results": {},
    }
    with httpx.Client(base_url=args.base_url, headers=headers, timeout=60.0) as client:
        for stack in STACKS:
            conversation_id = f"telegram-regression:{stack}:{int(datetime.now().timestamp())}"
            report["results"][stack] = _run_stack(
                client=client,
                stack=stack,
                conversation_id=conversation_id,
                telegram_chat_id=args.telegram_chat_id,
                messages=DEFAULT_MESSAGES,
            )

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(str(output_path))


if __name__ == "__main__":
    main()
