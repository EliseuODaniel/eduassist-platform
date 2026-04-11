from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Callable
from uuid import uuid4

from _common import Settings, assert_condition, request, wait_for_health

STACKS = ("langgraph", "python_functions", "llamaindex", "specialist_supervisor")
GUARDIAN_CHAT_ID = 1649845499
RUN_ID = uuid4().hex[:8]
DEFAULT_OUTPUT = Path(__file__).resolve().parents[2] / "artifacts" / "dedicated-stack-long-memory-report.json"


def _headers(settings: Settings) -> dict[str, str]:
    return {
        "Content-Type": "application/json",
        "X-Internal-Api-Token": settings.internal_api_token,
    }


def _status_requires_auth(stack: str) -> bool:
    return stack == "specialist_supervisor"


def _status(settings: Settings, stack: str) -> dict[str, Any]:
    headers = _headers(settings) if _status_requires_auth(stack) else None
    status, _, payload = request(
        "GET",
        f"{settings.stack_runtime_url(stack)}/v1/status",
        headers=headers,
        timeout=20.0,
    )
    assert_condition(status == 200 and isinstance(payload, dict), f"{stack}:status_failed")
    return payload


def _message_response(
    settings: Settings,
    *,
    stack: str,
    conversation_id: str,
    message: str,
    channel: str,
    telegram_chat_id: int | None = None,
    user: dict[str, Any] | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "message": message,
        "conversation_id": conversation_id,
        "channel": channel,
        "user": user or {"authenticated": False, "role": "anonymous"},
    }
    if telegram_chat_id is not None:
        payload["telegram_chat_id"] = telegram_chat_id
    status, _, body = request(
        "POST",
        f"{settings.stack_runtime_url(stack)}/v1/messages/respond",
        headers=_headers(settings),
        json_body=payload,
        timeout=60.0,
    )
    assert_condition(status == 200 and isinstance(body, dict), f"{stack}:message_failed:{message}")
    return body


def _normalize(value: str) -> str:
    return str(value or "").lower()


def _contains_any(text: str, options: tuple[str, ...]) -> bool:
    lowered = _normalize(text)
    return any(option in lowered for option in options)


def _assert_guardian_public_digression(turns: list[dict[str, Any]]) -> None:
    first = str(turns[0]["message_text"])
    second = str(turns[1]["message_text"])
    third = str(turns[2]["message_text"])
    fourth = str(turns[3]["message_text"])
    fifth = str(turns[4]["message_text"])
    assert_condition("lucas oliveira" in _normalize(first), "guardian_public_digression:first_missing_lucas")
    assert_condition(_contains_any(second, ("fisica", "física", "mais preocup", "menor nota")), "guardian_public_digression:second_missing_concern")
    assert_condition(_contains_any(third, ("aulas", "calend", "comec", "começ")), "guardian_public_digression:third_missing_public")
    assert_condition("lucas oliveira" in _normalize(fourth), "guardian_public_digression:fourth_missing_lucas")
    assert_condition(_contains_any(fourth, ("menor nota", "fisica", "física", "5,")), "guardian_public_digression:fourth_missing_lowest_grade")
    assert_condition(
        _contains_any(fifth, ("ana oliveira", "lucas oliveira", "media minima", "média mínima", "compar")),
        "guardian_public_digression:fifth_missing_comparison",
    )


def _assert_workflow_far_followup(turns: list[dict[str, Any]]) -> None:
    first = str(turns[0]["message_text"])
    second = str(turns[1]["message_text"])
    third = str(turns[2]["message_text"])
    fourth = str(turns[3]["message_text"])
    fifth = str(turns[4]["message_text"])
    assert_condition(_contains_any(first, ("visita", "agend", "secretaria")), "workflow_far_followup:first_missing_visit")
    assert_condition(_contains_any(second, ("biblioteca", "horario", "horário")), "workflow_far_followup:second_missing_library")
    assert_condition(_contains_any(third, ("remarc", "reagend", "canal", "secretaria")), "workflow_far_followup:third_missing_reschedule")
    assert_condition(_contains_any(fourth, ("cancel", "secretaria", "canal")), "workflow_far_followup:fourth_missing_cancel")
    assert_condition(_contains_any(fifth, ("visita", "secretaria", "agend", "canal")), "workflow_far_followup:fifth_missing_resume")


def _assert_family_attention_with_policy_digression(turns: list[dict[str, Any]]) -> None:
    first = str(turns[0]["message_text"])
    second = str(turns[1]["message_text"])
    third = str(turns[2]["message_text"])
    fourth = str(turns[3]["message_text"])
    assert_condition("lucas oliveira" in _normalize(first), "family_attention_policy:first_missing_lucas")
    assert_condition("ana oliveira" in _normalize(first), "family_attention_policy:first_missing_ana")
    assert_condition(_contains_any(second, ("frequencia", "frequência", "horario", "faltas", "pontualidade")), "family_attention_policy:second_missing_policy")
    assert_condition(_contains_any(third, ("atencao", "atenção", "lucas oliveira", "ana oliveira")), "family_attention_policy:third_missing_priority")
    assert_condition("lucas oliveira" in _normalize(fourth), "family_attention_policy:fourth_missing_lucas")
    assert_condition(_contains_any(fourth, ("alerta", "falta", "frequencia", "frequência")), "family_attention_policy:fourth_missing_alert")


def _assert_late_correction(turns: list[dict[str, Any]]) -> None:
    first = str(turns[0]["message_text"])
    second = str(turns[1]["message_text"])
    third = str(turns[2]["message_text"])
    fourth = str(turns[3]["message_text"])
    assert_condition("ana oliveira" in _normalize(first), "late_correction:first_missing_ana")
    assert_condition(_contains_any(second, ("matematica", "matemática")), "late_correction:second_missing_math")
    assert_condition("lucas oliveira" in _normalize(third), "late_correction:third_missing_lucas")
    assert_condition(_contains_any(fourth, ("ana oliveira", "lucas oliveira", "media minima", "média mínima", "compar")), "late_correction:fourth_missing_compare")


def _assert_teacher_boundary_then_compare(turns: list[dict[str, Any]]) -> None:
    first = str(turns[0]["message_text"])
    second = str(turns[1]["message_text"])
    third = str(turns[2]["message_text"])
    fourth = str(turns[3]["message_text"])
    assert_condition("lucas oliveira" in _normalize(first), "teacher_boundary_compare:first_missing_lucas")
    assert_condition(_contains_any(second, ("menor nota", "fisica", "física", "5,")), "teacher_boundary_compare:second_missing_low_grade")
    lowered = _normalize(third)
    assert_condition("coorden" in lowered, "teacher_boundary_compare:third_missing_coordination")
    assert_condition(
        _contains_any(lowered, ("nao divulga", "não divulga", "contato direto", "contato institucional")),
        "teacher_boundary_compare:third_missing_boundary",
    )
    lowered_fourth = _normalize(fourth)
    assert_condition("lucas oliveira" in lowered_fourth, "teacher_boundary_compare:fourth_missing_lucas")
    assert_condition("ana oliveira" in lowered_fourth, "teacher_boundary_compare:fourth_missing_ana")
    assert_condition(_contains_any(lowered_fourth, ("compar", "media minima", "média mínima", "academ")), "teacher_boundary_compare:fourth_missing_compare")


def _assert_process_compare_after_family_digression(turns: list[dict[str, Any]]) -> None:
    first = str(turns[0]["message_text"])
    second = str(turns[1]["message_text"])
    third = str(turns[2]["message_text"])
    fourth = str(turns[3]["message_text"])
    assert_condition("lucas oliveira" in _normalize(first), "process_after_family:first_missing_lucas")
    assert_condition("ana oliveira" in _normalize(first), "process_after_family:first_missing_ana")
    assert_condition(_contains_any(second, ("atencao", "atenção", "lucas oliveira", "ana oliveira")), "process_after_family:second_missing_priority")
    lowered_third = _normalize(third)
    assert_condition("rematric" in lowered_third, "process_after_family:third_missing_rematricula")
    assert_condition("transfer" in lowered_third, "process_after_family:third_missing_transferencia")
    assert_condition("cancel" in lowered_third, "process_after_family:third_missing_cancelamento")
    lowered_fourth = _normalize(fourth)
    assert_condition("lucas oliveira" in lowered_fourth, "process_after_family:fourth_missing_lucas")
    assert_condition(_contains_any(lowered_fourth, ("alerta", "frequencia", "frequência", "falta")), "process_after_family:fourth_missing_alert")


@dataclass(frozen=True)
class Scenario:
    name: str
    channel: str
    user: dict[str, Any]
    telegram_chat_id: int | None
    prompts: tuple[str, ...]
    validator: Callable[[list[dict[str, Any]]], None]


SCENARIOS: tuple[Scenario, ...] = (
    Scenario(
        name="guardian_public_digression_return",
        channel="telegram",
        telegram_chat_id=GUARDIAN_CHAT_ID,
        user={"authenticated": True, "role": "guardian"},
        prompts=(
            "quais as notas do Lucas Oliveira?",
            "e qual disciplina preocupa mais?",
            "agora me lembra quando começam as aulas?",
            "voltando ao Lucas, qual foi a menor nota dele?",
            "e compara isso com a Ana",
        ),
        validator=_assert_guardian_public_digression,
    ),
    Scenario(
        name="workflow_resume_after_far_digression",
        channel="api",
        telegram_chat_id=None,
        user={"authenticated": False, "role": "anonymous"},
        prompts=(
            "quero visitar a escola na sexta de manhã",
            "qual o horário da biblioteca?",
            "e se eu precisar remarcar a visita?",
            "certo, e se eu cancelar mesmo?",
            "e se eu quiser retomar depois, por onde volto?",
        ),
        validator=_assert_workflow_far_followup,
    ),
    Scenario(
        name="family_attention_with_policy_digression",
        channel="telegram",
        telegram_chat_id=GUARDIAN_CHAT_ID,
        user={"authenticated": True, "role": "guardian"},
        prompts=(
            "me mostra a frequência dos meus dois filhos",
            "agora me explica a política pública de frequência da escola",
            "voltando aos meus filhos, quem exige mais atenção?",
            "e qual o principal alerta só do Lucas?",
        ),
        validator=_assert_family_attention_with_policy_digression,
    ),
    Scenario(
        name="late_student_correction_after_subject_followup",
        channel="telegram",
        telegram_chat_id=GUARDIAN_CHAT_ID,
        user={"authenticated": True, "role": "guardian"},
        prompts=(
            "quais as próximas provas da Ana?",
            "e a próxima de matemática?",
            "não, do Lucas",
            "e agora quem dos dois está mais perto da média mínima?",
        ),
        validator=_assert_late_correction,
    ),
    Scenario(
        name="teacher_boundary_then_family_compare",
        channel="telegram",
        telegram_chat_id=GUARDIAN_CHAT_ID,
        user={"authenticated": True, "role": "guardian"},
        prompts=(
            "quais as notas do Lucas Oliveira?",
            "e qual foi a menor nota dele?",
            "agora me diz se a escola divulga contato direto do professor de matemática",
            "voltando aos meus filhos, compara o Lucas com a Ana",
        ),
        validator=_assert_teacher_boundary_then_compare,
    ),
    Scenario(
        name="process_compare_after_family_digression",
        channel="telegram",
        telegram_chat_id=GUARDIAN_CHAT_ID,
        user={"authenticated": True, "role": "guardian"},
        prompts=(
            "me mostra a frequência dos meus dois filhos",
            "quem exige mais atenção?",
            "agora esquece meu caso: sem falar de preço, o que muda entre rematrícula, transferência e cancelamento?",
            "voltando ao meu caso, qual é o principal alerta só do Lucas?",
        ),
        validator=_assert_process_compare_after_family_digression,
    ),
)


def _run_scenario(settings: Settings, *, stack: str, scenario: Scenario) -> dict[str, Any]:
    conversation_id = f"long-memory-{RUN_ID}-{stack}-{scenario.name}"
    turns: list[dict[str, Any]] = []
    request_channel = scenario.channel
    if (
        stack == "specialist_supervisor"
        and scenario.channel == "telegram"
        and scenario.telegram_chat_id is not None
    ):
        request_channel = "api"
    for index, prompt in enumerate(scenario.prompts, start=1):
        response = _message_response(
            settings,
            stack=stack,
            conversation_id=conversation_id,
            message=prompt,
            channel=request_channel,
            telegram_chat_id=scenario.telegram_chat_id,
            user=scenario.user,
        )
        message_text = str(response.get("message_text", ""))
        assert_condition(message_text.strip(), f"{stack}:{scenario.name}:turn_{index}_empty")
        turns.append(
            {
                "turn": index,
                "prompt": prompt,
                "message_text": message_text,
                "mode": response.get("mode"),
                "reason": response.get("reason"),
                "graph_path": response.get("graph_path"),
            }
        )
    scenario.validator(turns)
    return {
        "scenario": scenario.name,
        "conversation_id": conversation_id,
        "turns": turns,
        "passed": True,
    }


def run_stack(settings: Settings, stack: str) -> dict[str, Any]:
    wait_for_health("api-core", f"{settings.api_core_url}/healthz")
    wait_for_health(stack, f"{settings.stack_runtime_url(stack)}/healthz")
    status = _status(settings, stack)
    assert_condition(status.get("serviceRole") == "dedicated-stack-runtime", f"{stack}:status_service_role")
    results = [_run_scenario(settings, stack=stack, scenario=scenario) for scenario in SCENARIOS]
    return {
        "stack": stack,
        "status": {
            "serviceRole": status.get("serviceRole"),
            "primaryServingRecommended": status.get("primaryServingRecommended"),
        },
        "passed": True,
        "scenarios": results,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Long-memory E2E battery for dedicated stack runtimes.")
    parser.add_argument("--stack", default="all", choices=[*STACKS, "all"])
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    settings = Settings()
    targets = STACKS if args.stack == "all" else (args.stack,)
    report = {
        "generated_at": datetime.now(UTC).isoformat(),
        "run_id": RUN_ID,
        "targets": list(targets),
        "results": [],
    }
    for stack in targets:
        print(f"[run] {stack}")
        result = run_stack(settings, stack)
        report["results"].append(result)
        print(f"[ok] {stack}")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Dedicated stack long-memory battery finished successfully. Report: {args.output}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as exc:
        print(f"[fail] {exc}", file=sys.stderr)
        raise SystemExit(1)
