from __future__ import annotations

import argparse
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any

import httpx

REPO_ROOT = Path(__file__).resolve().parents[2]
STACKS = ("langgraph", "python_functions", "llamaindex", "specialist_supervisor")
SCENARIOS = {
    "academic_finance_followup": [
        {"label": "student_activation", "text": "do lucas oliveira então"},
        {"label": "all_grades", "text": "quais as notas do lucas"},
        {"label": "subject_grade", "text": "qual a nota de história do lucas?"},
        {"label": "justification_followup", "text": "é atestado de ficar dormindo, serve?"},
        {"label": "finance_followup", "text": "e o financeiro do lucas como está?"},
    ],
    "public_pricing_followup": [
        {"label": "pricing_reference", "text": "Qual a mensalidade do ensino medio?"},
        {"label": "pricing_projection", "text": "Quanto seria a matricula para 20 filhos?"},
        {"label": "pricing_grade_followup", "text": "3o"},
        {"label": "pricing_quantity_followup", "text": "E para 20 filhos?"},
    ],
    "public_capacity_followup": [
        {"label": "pricing_reference", "text": "Mensalidade do ensino medio"},
        {"label": "hypothetical_family_projection", "text": "E se eu matricular meus 200 filhos?"},
        {"label": "generic_capacity", "text": "Quantas vagas tem?"},
        {"label": "parking_capacity", "text": "E no estacionamento?"},
        {"label": "parking_capacity_explicit", "text": "Quantas vagas tem no estacionamento da escola?"},
        {"label": "student_capacity_explicit", "text": "E de alunos? Tem quantas vagas na escola"},
    ],
    "public_calendar_temporal_followup": [
        {"label": "class_start_date", "text": "Quando começam as aulas?"},
        {"label": "classes_started", "text": "Já começaram então?"},
        {"label": "today_date", "text": "Mas que dia é hoje?"},
        {"label": "classes_started_repair", "text": "Entao as aulas ja comecaram"},
        {"label": "today_and_start_date", "text": "Que dia é hoje e que dia comecam as aulas?"},
    ],
    "public_notification_followup": [
        {"label": "graduation", "text": "Formatura"},
        {"label": "event_distance", "text": "Ta longe ainda"},
        {"label": "will_notify", "text": "Vão me avisar?"},
        {"label": "notify_request", "text": "Me avisa a data da formatura quando chegar perto"},
    ],
    "entity_and_subject_repair": [
        {"label": "unknown_student", "text": "qual a nota da laura"},
        {"label": "ambiguous_student_followup", "text": "do lucas serve"},
        {"label": "student_grades", "text": "não quero justificar, quero saber a nota do lucas"},
        {"label": "single_subject", "text": "só de geografia"},
        {"label": "repair_meta", "text": "por que não falou antes a nota de geografia?"},
    ],
    "subject_alias_and_unsupported_subject": [
        {"label": "english_short", "text": "e de english"},
        {"label": "english_explicit", "text": "quero saber a nota de english do lucas"},
        {"label": "unknown_subject", "text": "e as notas de dança"},
        {"label": "unknown_subject_correction", "text": "não é física, é aulas de dança, as notas"},
    ],
    "upcoming_assessments_repair": [
        {"label": "upcoming_all", "text": "e quais as próximas provas do lucas"},
        {"label": "upcoming_history", "text": "e de história quais as próximas provas dele"},
        {"label": "resume_student", "text": "do lucas, estou falando dele"},
        {"label": "upcoming_dates", "text": "datas das provas"},
        {"label": "repair_previous_answer", "text": "mas você falou as próximas datas das provas dele de física"},
        {"label": "repair_scope_question", "text": "e essa resposta aqui era sobre o que então?"},
    ],
}


def _set_override(client: httpx.Client, *, stack: str, conversation_id: str, ttl_seconds: int) -> None:
    try:
        response = client.post(
            "/v1/internal/runtime/targeted-stack",
            json={
                "stack": stack,
                "reason": "telegram_real_world_regression",
                "operator": "codex",
                "ttl_seconds": ttl_seconds,
                "conversation_allowlist": [conversation_id],
            },
        )
        response.raise_for_status()
    except httpx.HTTPError:
        return


def _clear_override(client: httpx.Client) -> None:
    try:
        response = client.post(
            "/v1/internal/runtime/targeted-stack",
            json={
                "clear_override": True,
                "reason": "telegram_real_world_regression_complete",
                "operator": "codex",
            },
        )
        response.raise_for_status()
    except httpx.HTTPError:
        return


def _run_conversation(
    *,
    client: httpx.Client,
    conversation_id: str,
    telegram_chat_id: int,
    messages: list[dict[str, str]],
) -> list[dict[str, Any]]:
    outputs: list[dict[str, Any]] = []
    for item in messages:
        try:
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
            error_kind = None
        except httpx.TimeoutException as exc:
            payload = {}
            error_kind = f"timeout:{exc.__class__.__name__}"
        except httpx.HTTPError as exc:
            payload = {}
            error_kind = f"http_error:{exc.__class__.__name__}"
        outputs.append(
            {
                "label": item["label"],
                "question": item["text"],
                "message_text": payload.get("message_text"),
                "mode": payload.get("mode"),
                "reason": payload.get("reason"),
                "graph_path": payload.get("graph_path"),
                "used_llm": payload.get("used_llm"),
                "llm_stages": payload.get("llm_stages"),
                "answer_experience_applied": payload.get("answer_experience_applied"),
                "answer_experience_reason": payload.get("answer_experience_reason"),
                "context_repair_applied": payload.get("context_repair_applied"),
                "context_repair_action": payload.get("context_repair_action"),
                "error": error_kind,
            }
        )
    return outputs


def _run_stack(
    *,
    client: httpx.Client,
    stack: str,
    base_conversation_id: str,
    telegram_chat_id: int,
) -> dict[str, Any]:
    result: dict[str, Any] = {}
    try:
        for scenario_name, messages in SCENARIOS.items():
            conversation_id = f"{base_conversation_id}:{stack}:{scenario_name}"
            _set_override(client, stack=stack, conversation_id=conversation_id, ttl_seconds=3600)
            result[scenario_name] = _run_conversation(
                client=client,
                conversation_id=conversation_id,
                telegram_chat_id=telegram_chat_id,
                messages=messages,
            )
    finally:
        _clear_override(client)
    return result


def _write_report(output_path: Path, report: dict[str, Any]) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--base-url",
        default=os.getenv("CONTROL_PLANE_ORCHESTRATOR_URL", "http://127.0.0.1:8002"),
    )
    parser.add_argument("--internal-token", default="dev-internal-token")
    parser.add_argument("--telegram-chat-id", type=int, default=1649845499)
    parser.add_argument("--timeout-seconds", type=float, default=25.0)
    parser.add_argument(
        "--output",
        default=str(REPO_ROOT / "docs/architecture/telegram-real-world-regression-20260404.json"),
    )
    args = parser.parse_args()

    headers = {"X-Internal-Api-Token": args.internal_token}
    report: dict[str, Any] = {
        "generated_at": datetime.now().isoformat(),
        "telegram_chat_id": args.telegram_chat_id,
        "scenarios": SCENARIOS,
        "results": {},
    }
    output_path = Path(args.output)
    with httpx.Client(base_url=args.base_url, headers=headers, timeout=args.timeout_seconds) as client:
        for stack in STACKS:
            base_conversation_id = f"telegram-real-world:{int(datetime.now().timestamp())}"
            report["results"][stack] = _run_stack(
                client=client,
                stack=stack,
                base_conversation_id=base_conversation_id,
                telegram_chat_id=args.telegram_chat_id,
            )
            _write_report(output_path, report)

    _write_report(output_path, report)
    print(str(output_path))


if __name__ == "__main__":
    main()
