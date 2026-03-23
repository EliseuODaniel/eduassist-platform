from __future__ import annotations

import sys
from _common import (
    Settings,
    assert_condition,
    extract_trace_id,
    fetch_token,
    grafana_basic_auth_header,
    request,
    telegram_webhook_request,
    trace_span_names,
    wait_for_health,
    wait_for_loki_logs,
    wait_for_trace_span,
)


def main() -> int:
    settings = Settings()
    print("Smoke suite starting...")

    for name, url in [
        ("api-core", f"{settings.api_core_url}/healthz"),
        ("ai-orchestrator", f"{settings.ai_orchestrator_url}/healthz"),
        ("telegram-gateway", f"{settings.telegram_gateway_url}/healthz"),
        ("tempo", f"{settings.tempo_url}/ready"),
        ("loki", f"{settings.loki_url}/ready"),
    ]:
        wait_for_health(name, url)
        print(f"[ok] health {name}")

    token = fetch_token(settings)
    print("[ok] keycloak token")

    status, _, payload = request(
        "GET",
        f"{settings.api_core_url}/v1/operations/overview",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert_condition(status == 200 and isinstance(payload, dict), "operations_overview_failed")
    print("[ok] operations overview")

    public_status, public_headers, public_payload = telegram_webhook_request(
        settings,
        update_id=9901,
        message_id=1,
        text="quais documentos sao exigidos para matricula?",
        chat_id=777001,
        username="visitante.publico",
        first_name="Visitante",
    )
    assert_condition(public_status == 200 and isinstance(public_payload, dict), "public_webhook_failed")
    assert_condition("reply" in public_payload and "document" in str(public_payload["reply"]).lower(), "public_reply_unexpected")
    public_trace_id = extract_trace_id(public_headers)
    print("[ok] public faq")

    protected_status, protected_headers, protected_payload = telegram_webhook_request(
        settings,
        update_id=9902,
        message_id=2,
        text="quero ver as notas do Lucas Oliveira",
        chat_id=555001,
        username="maria.oliveira",
        first_name="Maria",
    )
    assert_condition(protected_status == 200 and isinstance(protected_payload, dict), "protected_webhook_failed")
    assert_condition("Resumo academico de Lucas Oliveira" in str(protected_payload.get("reply", "")), "protected_reply_unexpected")
    protected_trace_id = extract_trace_id(protected_headers)
    print("[ok] protected academic")

    handoff_status, handoff_headers, handoff_payload = telegram_webhook_request(
        settings,
        update_id=9903,
        message_id=3,
        text="quero falar com um humano sobre o financeiro",
        chat_id=555001,
        username="maria.oliveira",
        first_name="Maria",
    )
    assert_condition(handoff_status == 200 and isinstance(handoff_payload, dict), "handoff_webhook_failed")
    assert_condition("Protocolo:" in str(handoff_payload.get("reply", "")), "handoff_reply_unexpected")
    handoff_trace_id = extract_trace_id(handoff_headers)
    print("[ok] human handoff")

    dashboard_status, _, dashboard_payload = request(
        "GET",
        f"{settings.grafana_url}/api/search?query=EduAssist%20Tracing%20Overview",
        headers=grafana_basic_auth_header(settings),
    )
    assert_condition(
        dashboard_status == 200 and isinstance(dashboard_payload, list) and dashboard_payload,
        "grafana_dashboard_missing",
    )
    print("[ok] grafana dashboard")

    public_trace = wait_for_trace_span(settings, public_trace_id, "eduassist.retrieval.hybrid_search")
    public_spans = trace_span_names(public_trace)
    assert_condition("eduassist.retrieval.hybrid_search" in public_spans, "missing_public_retrieval_span")
    print("[ok] tempo retrieval span")

    protected_trace = wait_for_trace_span(settings, protected_trace_id, "eduassist.policy.decide")
    protected_spans = trace_span_names(protected_trace)
    assert_condition("eduassist.policy.decide" in protected_spans, "missing_policy_span")
    print("[ok] tempo policy span")

    handoff_trace = wait_for_trace_span(settings, handoff_trace_id, "eduassist.support.create_handoff")
    handoff_spans = trace_span_names(handoff_trace)
    assert_condition("eduassist.support.create_handoff" in handoff_spans, "missing_handoff_span")
    print("[ok] tempo handoff span")

    loki_payload = wait_for_loki_logs(settings, '{compose_service="telegram-gateway"}')
    loki_results = loki_payload.get("data", {}).get("result", [])
    assert_condition(isinstance(loki_results, list) and loki_results, "loki_no_gateway_logs")
    print("[ok] loki gateway logs")

    print("Smoke suite finished successfully.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as exc:
        print(f"[fail] {exc}", file=sys.stderr)
        raise SystemExit(1)
