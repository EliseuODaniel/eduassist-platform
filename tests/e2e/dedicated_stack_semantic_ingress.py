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
DEFAULT_OUTPUT = Path(__file__).resolve().parents[2] / "artifacts" / "dedicated-stack-semantic-ingress-report.json"


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
    channel: str,
    conversation_id: str,
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


def _assert_greeting(payload: dict[str, Any]) -> None:
    lowered = _normalize(payload.get("message_text"))
    assert_condition(
        _contains_any(lowered, ("olá", "ola", "bom dia", "boa tarde", "boa noite", "como posso ajudar")),
        "greeting:missing_salutation",
    )
    assert_condition("cadastro" not in lowered, "greeting:unexpected_admin_fallback")


def _assert_identity(payload: dict[str, Any]) -> None:
    lowered = _normalize(payload.get("message_text"))
    assert_condition(_contains_any(lowered, ("eduassist", "assistente", "colegio", "colégio")), "identity:missing_identity")


def _assert_capabilities(payload: dict[str, Any]) -> None:
    lowered = _normalize(payload.get("message_text"))
    assert_condition(
        _contains_any(lowered, ("matricula", "financeiro", "visita", "notas", "faltas", "ajudar")),
        "capabilities:missing_scope",
    )


def _assert_auth_guidance(payload: dict[str, Any]) -> None:
    lowered = _normalize(payload.get("message_text"))
    assert_condition(
        _contains_any(lowered, ("vincul", "telegram", "conta", "responsável", "responsavel")),
        "auth_guidance:missing_linking_guidance",
    )


def _assert_classifier_used(payload: dict[str, Any]) -> None:
    stages = payload.get("llm_stages") or []
    assert_condition(
        isinstance(stages, list) and "semantic_ingress_classifier" in stages,
        "semantic_ingress:classifier_not_used",
    )


def _assert_conduct_policy(payload: dict[str, Any]) -> None:
    lowered = _normalize(payload.get("message_text"))
    assert_condition(
        _contains_any(lowered, ("comportamento", "conduta", "respeito", "bullying", "ocorr")),
        "conduct_policy:missing_policy_language",
    )
    assert_condition("como posso ajudar" not in lowered, "conduct_policy:misrouted_as_greeting")
    assert_condition("cadastro" not in lowered, "conduct_policy:unexpected_admin_fallback")


def _assert_guardian_attendance(payload: dict[str, Any]) -> None:
    lowered = _normalize(payload.get("message_text"))
    assert_condition("lucas oliveira" in lowered, "guardian_attendance:missing_student")
    assert_condition(_contains_any(lowered, ("falt", "frequ", "disciplina", "hist", "fis")), "guardian_attendance:missing_attendance")
    assert_condition("como posso ajudar" not in lowered, "guardian_attendance:misrouted_as_greeting")


def _assert_guardian_grades(payload: dict[str, Any]) -> None:
    lowered = _normalize(payload.get("message_text"))
    assert_condition("lucas oliveira" in lowered or "lucas" in lowered, "guardian_grades:missing_student")
    assert_condition(_contains_any(lowered, ("ingles", "inglês", "nota", "media", "média")), "guardian_grades:missing_grade_signal")
    assert_condition("matricula e atendimento comercial" not in lowered, "guardian_grades:misrouted_as_language_preference")
    assert_condition("cadastro" not in lowered, "guardian_grades:unexpected_admin_fallback")


def _assert_input_clarification(payload: dict[str, Any]) -> None:
    lowered = _normalize(payload.get("message_text"))
    assert_condition(
        _contains_any(lowered, ("nao consegui interpretar", "não consegui interpretar", "reformule", "frase curta")),
        "input_clarification:missing_clarification_language",
    )
    assert_condition("cadastro" not in lowered, "input_clarification:unexpected_admin_fallback")


def _assert_language_preference(payload: dict[str, Any], *, require_localized_label: bool) -> None:
    lowered = _normalize(payload.get("message_text"))
    assert_condition(
        _contains_any(lowered, ("portugues", "português")),
        "language_preference:missing_portuguese_commitment",
    )
    if require_localized_label:
        assert_condition(
            _contains_any(lowered, ("matricula e atendimento comercial", "matrícula e atendimento comercial")),
            "language_preference:missing_localized_admissions_label",
        )
    assert_condition("lingua inglesa" not in lowered, "language_preference:misread_as_subject")
    assert_condition("ana oliveira" not in lowered and "lucas oliveira" not in lowered, "language_preference:unexpected_student_clarify")


def _assert_language_preference_with_localized_label(payload: dict[str, Any]) -> None:
    _assert_language_preference(payload, require_localized_label=True)


def _assert_language_preference_portuguese_only(payload: dict[str, Any]) -> None:
    _assert_language_preference(payload, require_localized_label=False)


def _assert_out_of_scope_abstention(payload: dict[str, Any]) -> None:
    lowered = _normalize(payload.get("message_text"))
    assert_condition(
        _contains_any(
            lowered,
            (
                "nao tenho",
                "não tenho",
                "nao consegui",
                "não consegui",
                "fora do escopo",
                "relacionado a escola",
                "relacionado à escola",
                "posso ajudar com matricula",
                "posso ajudar com matrícula",
            ),
        ),
        "out_of_scope:missing_abstention_language",
    )
    assert_condition("cadastro" not in lowered, "out_of_scope:unexpected_admin_fallback")
    assert_condition("escola publica pode ser uma boa escolha" not in lowered, "out_of_scope:unexpected_public_comparative")


@dataclass(frozen=True)
class Scenario:
    name: str
    message: str
    channel: str
    user: dict[str, Any]
    telegram_chat_id: int | None
    validator: Callable[[dict[str, Any]], None]
    expect_classifier: bool = False


SCENARIOS: tuple[Scenario, ...] = (
    Scenario(
        name="greeting_boa_madruga",
        message="boa madruga",
        channel="api",
        user={"authenticated": False, "role": "anonymous"},
        telegram_chat_id=None,
        validator=_assert_greeting,
        expect_classifier=True,
    ),
    Scenario(
        name="greeting_elongated_oooie",
        message="oooie",
        channel="api",
        user={"authenticated": False, "role": "anonymous"},
        telegram_chat_id=None,
        validator=_assert_greeting,
        expect_classifier=True,
    ),
    Scenario(
        name="greeting_authenticated_bom_diazinho",
        message="bom diazinho",
        channel="telegram",
        user={"authenticated": True, "role": "guardian"},
        telegram_chat_id=GUARDIAN_CHAT_ID,
        validator=_assert_greeting,
        expect_classifier=True,
    ),
    Scenario(
        name="greeting_multilingual_privet",
        message="Привет",
        channel="telegram",
        user={"authenticated": True, "role": "guardian"},
        telegram_chat_id=GUARDIAN_CHAT_ID,
        validator=_assert_greeting,
        expect_classifier=True,
    ),
    Scenario(
        name="assistant_identity",
        message="mas afinal quem ta falando comigo aqui msm?",
        channel="api",
        user={"authenticated": False, "role": "anonymous"},
        telegram_chat_id=None,
        validator=_assert_identity,
        expect_classifier=True,
    ),
    Scenario(
        name="capabilities",
        message="o que voce faz por aqui?",
        channel="api",
        user={"authenticated": False, "role": "anonymous"},
        telegram_chat_id=None,
        validator=_assert_capabilities,
        expect_classifier=True,
    ),
    Scenario(
        name="auth_guidance",
        message="como vinculo minha conta no telegram?",
        channel="api",
        user={"authenticated": False, "role": "anonymous"},
        telegram_chat_id=None,
        validator=_assert_auth_guidance,
        expect_classifier=True,
    ),
    Scenario(
        name="input_clarification_noise",
        message="???",
        channel="api",
        user={"authenticated": False, "role": "anonymous"},
        telegram_chat_id=None,
        validator=_assert_input_clarification,
        expect_classifier=True,
    ),
    Scenario(
        name="input_clarification_opaque_short_token_public",
        message="rai",
        channel="api",
        user={"authenticated": False, "role": "anonymous"},
        telegram_chat_id=None,
        validator=_assert_input_clarification,
        expect_classifier=True,
    ),
    Scenario(
        name="input_clarification_opaque_short_token",
        message="rai",
        channel="telegram",
        user={"authenticated": True, "role": "guardian"},
        telegram_chat_id=GUARDIAN_CHAT_ID,
        validator=_assert_input_clarification,
        expect_classifier=True,
    ),
    Scenario(
        name="language_preference_admissions_english",
        message="Por que admissions ta em ingles",
        channel="telegram",
        user={"authenticated": True, "role": "guardian"},
        telegram_chat_id=GUARDIAN_CHAT_ID,
        validator=_assert_language_preference_with_localized_label,
        expect_classifier=True,
    ),
    Scenario(
        name="language_preference_portuguese_only",
        message="Quero que so fale portugues",
        channel="telegram",
        user={"authenticated": True, "role": "guardian"},
        telegram_chat_id=GUARDIAN_CHAT_ID,
        validator=_assert_language_preference_portuguese_only,
        expect_classifier=True,
    ),
    Scenario(
        name="negative_conduct_policy",
        message="bom comportamento",
        channel="api",
        user={"authenticated": False, "role": "anonymous"},
        telegram_chat_id=None,
        validator=_assert_conduct_policy,
    ),
    Scenario(
        name="authenticated_public_conduct_substance",
        message="posso fumar maconha nessa escola?",
        channel="telegram",
        user={"authenticated": True, "role": "guardian"},
        telegram_chat_id=GUARDIAN_CHAT_ID,
        validator=_assert_conduct_policy,
    ),
    Scenario(
        name="public_conduct_substance",
        message="posso fumar maconha nessa escola?",
        channel="api",
        user={"authenticated": False, "role": "anonymous"},
        telegram_chat_id=None,
        validator=_assert_conduct_policy,
    ),
    Scenario(
        name="authenticated_out_of_scope_general_knowledge",
        message="qual o melhor filme do ano?",
        channel="telegram",
        user={"authenticated": True, "role": "guardian"},
        telegram_chat_id=GUARDIAN_CHAT_ID,
        validator=_assert_out_of_scope_abstention,
        expect_classifier=True,
    ),
    Scenario(
        name="public_out_of_scope_general_knowledge",
        message="qual o melhor filme do ano?",
        channel="api",
        user={"authenticated": False, "role": "anonymous"},
        telegram_chat_id=None,
        validator=_assert_out_of_scope_abstention,
        expect_classifier=True,
    ),
    Scenario(
        name="negative_guardian_attendance",
        message="boa parte das faltas do Lucas veio de quais disciplinas?",
        channel="telegram",
        user={"authenticated": True, "role": "guardian"},
        telegram_chat_id=GUARDIAN_CHAT_ID,
        validator=_assert_guardian_attendance,
    ),
    Scenario(
        name="negative_english_subject_grades",
        message="qual a nota de ingles do Lucas?",
        channel="telegram",
        user={"authenticated": True, "role": "guardian"},
        telegram_chat_id=GUARDIAN_CHAT_ID,
        validator=_assert_guardian_grades,
    ),
)


def _run_scenario(settings: Settings, *, stack: str, scenario: Scenario) -> dict[str, Any]:
    request_channel = scenario.channel
    if stack == "specialist_supervisor" and scenario.channel == "telegram" and scenario.telegram_chat_id is not None:
        request_channel = "api"
    conversation_id = f"semantic-ingress-{RUN_ID}-{stack}-{scenario.name}"
    payload = _message_response(
        settings,
        stack=stack,
        message=scenario.message,
        channel=request_channel,
        conversation_id=conversation_id,
        telegram_chat_id=scenario.telegram_chat_id,
        user=scenario.user,
    )
    scenario.validator(payload)
    if scenario.expect_classifier:
        _assert_classifier_used(payload)
    return {
        "scenario": scenario.name,
        "conversation_id": conversation_id,
        "message": scenario.message,
        "message_text": payload.get("message_text"),
        "reason": payload.get("reason"),
        "llm_stages": payload.get("llm_stages") or [],
    }


def run_stack_suite(settings: Settings, *, stack: str) -> dict[str, Any]:
    wait_for_health("api-core", f"{settings.api_core_url}/healthz")
    wait_for_health(stack, f"{settings.stack_runtime_url(stack)}/healthz")
    results: list[dict[str, Any]] = []
    for scenario in SCENARIOS:
        results.append(_run_scenario(settings, stack=stack, scenario=scenario))
        print(f"[ok] {stack} -> {scenario.name}")
    return {
        "stack": stack,
        "results": results,
        "passed": len(results),
        "total": len(SCENARIOS),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Bateria cross-stack do semantic ingress classifier.")
    parser.add_argument(
        "--stack",
        choices=("all", *STACKS),
        default="all",
        help="Stack dedicada a validar.",
    )
    parser.add_argument(
        "--output",
        default=str(DEFAULT_OUTPUT),
        help="Arquivo JSON de saida.",
    )
    args = parser.parse_args()

    settings = Settings()
    targets = STACKS if args.stack == "all" else (args.stack,)
    report = {
        "generated_at": datetime.now(UTC).isoformat(),
        "run_id": RUN_ID,
        "stacks": [],
    }
    for stack in targets:
        report["stacks"].append(run_stack_suite(settings, stack=stack))
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Semantic ingress battery finished successfully. Report: {output_path}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as exc:
        print(f"[fail] {exc}", file=sys.stderr)
        raise SystemExit(1)
