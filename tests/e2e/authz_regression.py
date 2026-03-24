from __future__ import annotations

import sys

from _common import (
    Settings,
    assert_condition,
    extract_trace_id,
    fetch_token,
    request,
    telegram_webhook_request,
    trace_span_names,
    wait_for_health,
    wait_for_trace_span,
)


LUCAS_STUDENT_ID = "53d70582-36f3-4052-b29c-ede23dec42ff"


def main() -> int:
    settings = Settings()
    print("Authz regression starting...")

    for name, url in [
        ("api-core", f"{settings.api_core_url}/healthz"),
        ("ai-orchestrator", f"{settings.ai_orchestrator_url}/healthz"),
        ("telegram-gateway", f"{settings.telegram_gateway_url}/healthz"),
        ("tempo", f"{settings.tempo_url}/ready"),
    ]:
        wait_for_health(name, url)
        print(f"[ok] health {name}")

    anonymous_status, anonymous_headers, anonymous_payload = telegram_webhook_request(
        settings,
        update_id=9951,
        message_id=51,
        text="quero ver minhas notas",
        chat_id=777001,
        username="visitante.publico",
        first_name="Visitante",
    )
    assert_condition(anonymous_status == 200 and isinstance(anonymous_payload, dict), "anonymous_deny_request_failed")
    anonymous_reply = str(anonymous_payload.get("reply", ""))
    assert_condition("autentic" in anonymous_reply.lower(), "anonymous_deny_reply_unexpected")
    anonymous_trace_id = extract_trace_id(anonymous_headers)
    anonymous_trace = wait_for_trace_span(settings, anonymous_trace_id, "eduassist.orchestration.message_response")
    assert_condition(
        "eduassist.orchestration.message_response" in trace_span_names(anonymous_trace),
        "anonymous_deny_trace_missing",
    )
    print("[ok] anonymous deny")

    ambiguous_status, ambiguous_headers, ambiguous_payload = telegram_webhook_request(
        settings,
        update_id=9952,
        message_id=52,
        text="quero ver minhas notas",
        chat_id=555001,
        username="maria.oliveira",
        first_name="Maria",
    )
    assert_condition(ambiguous_status == 200 and isinstance(ambiguous_payload, dict), "ambiguity_request_failed")
    ambiguous_reply = str(ambiguous_payload.get("reply", ""))
    assert_condition("mais de um aluno vinculado" in ambiguous_reply.lower(), "ambiguity_reply_unexpected")
    assert_condition("Lucas Oliveira" in ambiguous_reply and "Ana Oliveira" in ambiguous_reply, "ambiguity_options_missing")
    ambiguous_trace_id = extract_trace_id(ambiguous_headers)
    ambiguous_trace = wait_for_trace_span(settings, ambiguous_trace_id, "eduassist.orchestration.structured_tool")
    assert_condition(
        "eduassist.orchestration.structured_tool" in trace_span_names(ambiguous_trace),
        "ambiguity_trace_missing",
    )
    print("[ok] guardian ambiguity")

    teacher_token = fetch_token(settings, username="helena.rocha")

    forbidden_status, forbidden_headers, forbidden_payload = request(
        "GET",
        f"{settings.api_core_url}/v1/students/{LUCAS_STUDENT_ID}/financial-summary",
        headers={"Authorization": f"Bearer {teacher_token}"},
    )
    assert_condition(forbidden_status == 403 and isinstance(forbidden_payload, dict), "teacher_finance_forbidden_failed")
    assert_condition(forbidden_payload.get("detail") == "no_matching_policy", "teacher_finance_forbidden_detail_unexpected")
    forbidden_trace_id = extract_trace_id(forbidden_headers)
    forbidden_trace = wait_for_trace_span(settings, forbidden_trace_id, "eduassist.policy.decide")
    assert_condition("eduassist.policy.decide" in trace_span_names(forbidden_trace), "forbidden_policy_trace_missing")
    print("[ok] teacher finance forbidden")

    invalid_secret_status, invalid_secret_headers, invalid_secret_payload = telegram_webhook_request(
        settings,
        update_id=9953,
        message_id=53,
        text="oi",
        chat_id=777001,
        username="visitante.publico",
        first_name="Visitante",
        secret="wrong-secret",
    )
    assert_condition(invalid_secret_status == 401 and isinstance(invalid_secret_payload, dict), "invalid_secret_request_failed")
    assert_condition(
        invalid_secret_payload.get("detail") == "Invalid Telegram webhook secret.",
        "invalid_secret_detail_unexpected",
    )
    extract_trace_id(invalid_secret_headers)
    print("[ok] invalid webhook secret")

    unauth_status, _, unauth_payload = request("GET", f"{settings.api_core_url}/v1/operations/overview")
    assert_condition(unauth_status == 401 and isinstance(unauth_payload, dict), "operations_unauth_failed")
    assert_condition(unauth_payload.get("detail") == "bearer_token_required", "operations_unauth_detail_unexpected")
    print("[ok] operations bearer required")

    guardian_token = fetch_token(settings, username="maria.oliveira")
    operator_token = fetch_token(settings, username="carla.nogueira")

    handoff_list_status, _, handoff_list_payload = request(
        "GET",
        f"{settings.api_core_url}/v1/support/handoffs?page=1&limit=5",
        headers={"Authorization": f"Bearer {guardian_token}"},
    )
    assert_condition(
        handoff_list_status == 200 and isinstance(handoff_list_payload, dict),
        "support_self_list_failed",
    )
    items = handoff_list_payload.get("items", [])
    assert_condition(isinstance(items, list) and items, "support_self_list_empty")
    handoff_id = items[0].get("handoff_id")
    conversation_id = items[0].get("conversation_id")
    assert_condition(isinstance(handoff_id, str) and len(handoff_id) > 20, "support_self_handoff_id_missing")
    assert_condition(
        isinstance(conversation_id, str) and len(conversation_id) > 20,
        "support_self_conversation_id_missing",
    )

    note_text = "Nota interna confidencial de operacao"
    update_status, _, update_payload = request(
        "PATCH",
        f"{settings.api_core_url}/v1/support/handoffs/{handoff_id}",
        headers={"Authorization": f"Bearer {operator_token}"},
        json_body={"operator_note": note_text},
    )
    assert_condition(
        update_status == 200 and isinstance(update_payload, dict),
        "support_operator_note_update_failed",
    )

    self_detail_status, _, self_detail_payload = request(
        "GET",
        f"{settings.api_core_url}/v1/support/handoffs/{handoff_id}",
        headers={"Authorization": f"Bearer {guardian_token}"},
    )
    assert_condition(
        self_detail_status == 200 and isinstance(self_detail_payload, dict),
        "support_self_detail_failed",
    )
    self_messages = self_detail_payload.get("messages", [])
    assert_condition(isinstance(self_messages, list), "support_self_detail_messages_missing")
    self_joined = " ".join(str(message.get("content", "")) for message in self_messages if isinstance(message, dict))
    assert_condition(note_text not in self_joined, "support_self_detail_leaked_operator_note")

    operator_detail_status, _, operator_detail_payload = request(
        "GET",
        f"{settings.api_core_url}/v1/support/handoffs/{handoff_id}",
        headers={"Authorization": f"Bearer {operator_token}"},
    )
    assert_condition(
        operator_detail_status == 200 and isinstance(operator_detail_payload, dict),
        "support_operator_detail_failed",
    )
    operator_messages = operator_detail_payload.get("messages", [])
    assert_condition(isinstance(operator_messages, list), "support_operator_detail_messages_missing")
    operator_joined = " ".join(
        str(message.get("content", "")) for message in operator_messages if isinstance(message, dict)
    )
    assert_condition(note_text in operator_joined, "support_operator_detail_missing_note")
    print("[ok] support operator note hidden from self scope")

    print("Authz regression finished successfully.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as exc:
        print(f"[fail] {exc}", file=sys.stderr)
        raise SystemExit(1)
