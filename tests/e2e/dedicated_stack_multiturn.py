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
DEFAULT_OUTPUT = Path(__file__).resolve().parents[2] / "artifacts" / "dedicated-stack-multiturn-report.json"


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


def _assert_public_protected_public(turns: list[dict[str, Any]]) -> None:
    first = str(turns[0]["message_text"])
    second = str(turns[1]["message_text"])
    third = str(turns[2]["message_text"])
    assert_condition(_contains_any(first, ("calend", "inicio das aulas", "comec", "começ")), "public_protected_public:first_missing_calendar")
    assert_condition("ana oliveira" in _normalize(second), "public_protected_public:second_missing_ana")
    assert_condition(_contains_any(third, ("calend", "aulas", "public")), "public_protected_public:third_missing_public_calendar")


def _assert_student_switch(turns: list[dict[str, Any]]) -> None:
    first = str(turns[0]["message_text"])
    second = str(turns[1]["message_text"])
    third = str(turns[2]["message_text"])
    assert_condition("ana oliveira" in _normalize(first), "student_switch:first_missing_ana")
    assert_condition("lucas oliveira" in _normalize(second), "student_switch:second_missing_lucas")
    assert_condition(
        _contains_any(third, ("lucas oliveira", "ana oliveira")),
        "student_switch:third_missing_student_name",
    )
    assert_condition(
        _contains_any(third, ("media minima", "média mínima", "fisica", "física", "mais perto")),
        "student_switch:third_missing_comparison",
    )


def _assert_teacher_boundary(turns: list[dict[str, Any]]) -> None:
    joined = " ".join(str(turn["message_text"]) for turn in turns)
    lowered = _normalize(joined)
    assert_condition("coorden" in lowered, "teacher_boundary:missing_coordination")
    assert_condition(
        _contains_any(lowered, ("nao divulga", "não divulga", "secretaria", "contato institucional")),
        "teacher_boundary:missing_boundary",
    )


def _assert_visit_workflow(turns: list[dict[str, Any]]) -> None:
    first = str(turns[0]["message_text"])
    second = str(turns[1]["message_text"])
    third = str(turns[2]["message_text"])
    assert_condition(_contains_any(first, ("visita", "agend", "secretaria")), "visit_workflow:first_missing_visit")
    assert_condition(_contains_any(second, ("remarc", "secretaria", "canal")), "visit_workflow:second_missing_reschedule")
    assert_condition(_contains_any(third, ("cancel", "secretaria", "canal")), "visit_workflow:third_missing_cancel")


def _assert_family_attention(turns: list[dict[str, Any]]) -> None:
    first = str(turns[0]["message_text"])
    second = str(turns[1]["message_text"])
    third = str(turns[2]["message_text"])
    assert_condition("lucas oliveira" in _normalize(first), "family_attention:first_missing_lucas")
    assert_condition("ana oliveira" in _normalize(first), "family_attention:first_missing_ana")
    assert_condition(
        _contains_any(second, ("lucas oliveira", "ana oliveira", "atencao", "atenção")),
        "family_attention:second_missing_attention",
    )
    assert_condition("lucas oliveira" in _normalize(third), "family_attention:third_missing_lucas")
    assert_condition(_contains_any(third, ("frequencia", "frequência", "alerta", "falta")), "family_attention:third_missing_alert")


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
        name="public_protected_public_reset",
        channel="telegram",
        telegram_chat_id=GUARDIAN_CHAT_ID,
        user={"authenticated": True, "role": "guardian"},
        prompts=(
            "quando começam as aulas?",
            "e as notas da Ana?",
            "não, quero só o calendário público",
        ),
        validator=_assert_public_protected_public,
    ),
    Scenario(
        name="student_switch_and_compare",
        channel="telegram",
        telegram_chat_id=GUARDIAN_CHAT_ID,
        user={"authenticated": True, "role": "guardian"},
        prompts=(
            "quais as próximas provas da Ana?",
            "e do Lucas?",
            "e qual dos dois está mais perto da média mínima?",
        ),
        validator=_assert_student_switch,
    ),
    Scenario(
        name="teacher_boundary_multiturn",
        channel="api",
        telegram_chat_id=None,
        user={"authenticated": False, "role": "anonymous"},
        prompts=(
            "quero falar com o professor de matemática",
            "a escola divulga esse contato?",
            "ou manda procurar a coordenação?",
        ),
        validator=_assert_teacher_boundary,
    ),
    Scenario(
        name="visit_workflow_followup",
        channel="api",
        telegram_chat_id=None,
        user={"authenticated": False, "role": "anonymous"},
        prompts=(
            "quero visitar a escola na sexta de manhã",
            "se eu precisar trocar o horário depois, por onde remarco?",
            "e se eu cancelar?",
        ),
        validator=_assert_visit_workflow,
    ),
    Scenario(
        name="family_attention_priority",
        channel="telegram",
        telegram_chat_id=GUARDIAN_CHAT_ID,
        user={"authenticated": True, "role": "guardian"},
        prompts=(
            "me mostra a frequência dos meus dois filhos",
            "quem exige mais atenção agora?",
            "e qual o principal alerta só do Lucas?",
        ),
        validator=_assert_family_attention,
    ),
)


def _run_scenario(settings: Settings, *, stack: str, scenario: Scenario) -> dict[str, Any]:
    conversation_id = f"multiturn-{RUN_ID}-{stack}-{scenario.name}"
    turns: list[dict[str, Any]] = []
    request_channel = scenario.channel
    # The specialist binds Telegram recent-context memory to `telegram:{chat_id}`.
    # For protected E2E scenarios we still need actor resolution by Telegram chat id,
    # but we want multi-turn isolation scoped to the synthetic conversation id.
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
    assert_condition(status.get("serviceRole") == "dedicated-stack-runtime", f"{stack}:status_role_unexpected")
    scenarios = [_run_scenario(settings, stack=stack, scenario=scenario) for scenario in SCENARIOS]
    return {
        "stack": stack,
        "status": {
            "serviceRole": status.get("serviceRole"),
            "primaryServingRecommended": status.get("primaryServingRecommended"),
        },
        "passed": True,
        "scenarios": scenarios,
    }


def _write_report(path: Path, report: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="E2E multi-turn dedicada por stack do EduAssist.")
    parser.add_argument("--stack", choices=("all", *STACKS), default="all")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    settings = Settings()
    targets = STACKS if args.stack == "all" else (args.stack,)
    report: dict[str, Any] = {
        "generated_at": datetime.now(UTC).isoformat(),
        "run_id": RUN_ID,
        "targets": list(targets),
        "results": [],
    }

    print(f"Dedicated multi-turn smoke starting for: {', '.join(targets)}")
    for stack in targets:
        result = run_stack(settings, stack)
        report["results"].append(result)
        print(f"[ok] multiturn {stack}")

    _write_report(args.output, report)
    print(f"Dedicated multi-turn smoke finished successfully. Report: {args.output}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as exc:
        print(f"[fail] {exc}", file=sys.stderr)
        raise SystemExit(1)
