from __future__ import annotations

import argparse
import sys
from typing import Any
from uuid import uuid4

from _common import Settings, assert_condition, request, wait_for_health

STACKS = ("langgraph", "python_functions", "llamaindex", "specialist_supervisor")
PUBLIC_CHAT_ID = 777001
GUARDIAN_CHAT_ID = 1649845499
GUARDIAN_USER_CONTEXT = {"authenticated": True, "role": "guardian"}
RUN_ID = uuid4().hex[:8]


def _status_requires_auth(stack: str) -> bool:
    return stack == "specialist_supervisor"


def _headers(settings: Settings) -> dict[str, str]:
    return {
        "Content-Type": "application/json",
        "X-Internal-Api-Token": settings.internal_api_token,
    }


def _message_response(
    settings: Settings,
    *,
    stack: str,
    message: str,
    telegram_chat_id: int | None = None,
    public_api: bool = False,
    conversation_id: str | None = None,
    user_context: dict[str, Any] | None = None,
) -> tuple[int, dict[str, str], Any]:
    json_body: dict[str, Any]
    if public_api:
        json_body = {
            "message": message,
            "channel": "api",
            "conversation_id": conversation_id or f"smoke-{RUN_ID}-public-{stack}",
            "user": {"authenticated": False, "role": "anonymous"},
        }
    else:
        assert telegram_chat_id is not None
        json_body = {
            "message": message,
            "telegram_chat_id": telegram_chat_id,
            "conversation_id": conversation_id or f"smoke-{RUN_ID}-telegram-{stack}",
        }
        if user_context:
            json_body["user"] = user_context
    return request(
        "POST",
        f"{settings.stack_runtime_url(stack)}/v1/messages/respond",
        headers=_headers(settings),
        json_body=json_body,
        timeout=45.0,
    )


def _check_status(settings: Settings, stack: str) -> None:
    headers = _headers(settings) if _status_requires_auth(stack) else None
    status, _, payload = request(
        "GET",
        f"{settings.stack_runtime_url(stack)}/v1/status",
        headers=headers,
        timeout=15.0,
    )
    assert_condition(status == 200 and isinstance(payload, dict), f"{stack}_status_failed")
    assert_condition(payload.get("serviceRole") == "dedicated-stack-runtime", f"{stack}_status_role_unexpected")
    assert_condition(payload.get("primaryServingRecommended") is True, f"{stack}_status_primary_flag_unexpected")


def _check_public_admissions(settings: Settings, stack: str) -> None:
    status, _, payload = _message_response(
        settings,
        stack=stack,
        message="quais documentos sao exigidos para matricula?",
        public_api=True,
    )
    assert_condition(
        status == 200 and isinstance(payload, dict),
        f"{stack}_public_admissions_failed:{status}:{type(payload).__name__}",
    )
    message = str(payload.get("message_text", ""))
    lowered = message.lower()
    assert_condition(
        "matricula" in lowered or "matrícula" in lowered,
        f"{stack}_public_admissions_missing_matricula",
    )
    assert_condition(
        any(
            marker in lowered
            for marker in (
                "document",
                "pre-cadastro",
                "pre cadastro",
                "cadastro",
                "secretaria",
                "contrato",
                "envio de documentos",
                "etapas",
            )
        ),
        f"{stack}_public_admissions_missing_admissions_detail",
    )


def _check_public_teacher_boundary(settings: Settings, stack: str) -> None:
    status, _, payload = _message_response(
        settings,
        stack=stack,
        message="quero o nome e o telefone do professor de matematica",
        public_api=True,
    )
    assert_condition(status == 200 and isinstance(payload, dict), f"{stack}_teacher_boundary_failed")
    message = str(payload.get("message_text", ""))
    lowered = message.lower()
    assert_condition("coorden" in lowered, f"{stack}_teacher_boundary_missing_coordination")
    assert_condition("nao divulga" in lowered or "não divulga" in lowered, f"{stack}_teacher_boundary_missing_boundary")


def _check_guardian_ambiguity(settings: Settings, stack: str) -> None:
    status, _, payload = _message_response(
        settings,
        stack=stack,
        message="quero ver minhas notas",
        telegram_chat_id=GUARDIAN_CHAT_ID,
        conversation_id=f"smoke-{RUN_ID}-guardian-ambiguity-{stack}",
        user_context=GUARDIAN_USER_CONTEXT,
    )
    assert_condition(status == 200 and isinstance(payload, dict), f"{stack}_guardian_ambiguity_failed")
    message = str(payload.get("message_text", ""))
    lowered = message.lower()
    assert_condition(
        (
            "mais de um aluno vinculado" in lowered
            or "para qual aluno" in lowered
            or "qual aluno" in lowered
            or "panorama academico das contas vinculadas" in lowered
            or "contas vinculadas" in lowered
        ),
        f"{stack}_guardian_ambiguity_missing_prompt",
    )
    assert_condition("lucas oliveira" in lowered, f"{stack}_guardian_ambiguity_missing_lucas")
    assert_condition("ana oliveira" in lowered, f"{stack}_guardian_ambiguity_missing_ana")


def _check_named_student_grades(settings: Settings, stack: str) -> None:
    status, _, payload = _message_response(
        settings,
        stack=stack,
        message="quais as notas do Lucas Oliveira?",
        telegram_chat_id=GUARDIAN_CHAT_ID,
        conversation_id=f"smoke-{RUN_ID}-named-student-{stack}",
        user_context=GUARDIAN_USER_CONTEXT,
    )
    assert_condition(status == 200 and isinstance(payload, dict), f"{stack}_named_student_failed")
    message = str(payload.get("message_text", ""))
    lowered = message.lower()
    assert_condition("lucas oliveira" in lowered, f"{stack}_named_student_missing_name")
    assert_condition(
        any(subject in lowered for subject in ("biologia", "fisica", "historia", "ingles", "educacao fisica")),
        f"{stack}_named_student_missing_subjects",
    )


def run_stack_smoke(settings: Settings, stack: str) -> None:
    runtime_url = settings.stack_runtime_url(stack)
    wait_for_health("api-core", f"{settings.api_core_url}/healthz")
    wait_for_health(stack, f"{runtime_url}/healthz")
    print(f"[ok] health {stack}")
    _check_status(settings, stack)
    print(f"[ok] status {stack}")
    _check_public_admissions(settings, stack)
    print(f"[ok] public admissions {stack}")
    _check_public_teacher_boundary(settings, stack)
    print(f"[ok] teacher boundary {stack}")
    _check_guardian_ambiguity(settings, stack)
    print(f"[ok] guardian ambiguity {stack}")
    _check_named_student_grades(settings, stack)
    print(f"[ok] named student grades {stack}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Smoke dedicado por stack do EduAssist.")
    parser.add_argument(
        "--stack",
        choices=("all", *STACKS),
        default="all",
        help="Stack dedicada a validar.",
    )
    args = parser.parse_args()

    settings = Settings()
    targets = STACKS if args.stack == "all" else (args.stack,)
    print(f"Dedicated stack smoke starting for: {', '.join(targets)}")
    for stack in targets:
        run_stack_smoke(settings, stack)
    print("Dedicated stack smoke finished successfully.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as exc:
        print(f"[fail] {exc}", file=sys.stderr)
        raise SystemExit(1)
