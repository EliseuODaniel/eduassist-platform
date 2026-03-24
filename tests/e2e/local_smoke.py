from __future__ import annotations

import sys
from _common import (
    Settings,
    assert_condition,
    extract_trace_id,
    fetch_token,
    grafana_basic_auth_header,
    prometheus_query,
    request,
    telegram_webhook_request,
    trace_span_names,
    wait_for_health,
    wait_for_loki_logs,
    wait_for_prometheus_result,
    wait_for_trace_span,
)


def main() -> int:
    settings = Settings()
    print('Smoke suite starting...')

    for name, url in [
        ('api-core', f'{settings.api_core_url}/healthz'),
        ('ai-orchestrator', f'{settings.ai_orchestrator_url}/healthz'),
        ('telegram-gateway', f'{settings.telegram_gateway_url}/healthz'),
        ('tempo', f'{settings.tempo_url}/ready'),
        ('loki', f'{settings.loki_url}/ready'),
        ('prometheus', f'{settings.prometheus_url}/-/ready'),
    ]:
        wait_for_health(name, url)
        print(f'[ok] health {name}')

    token = fetch_token(settings)
    global_token = fetch_token(settings, username='carla.nogueira')
    print('[ok] keycloak token')

    status, _, payload = request(
        'GET',
        f'{settings.api_core_url}/v1/operations/overview',
        headers={'Authorization': f'Bearer {token}'},
    )
    assert_condition(status == 200 and isinstance(payload, dict), 'operations_overview_failed')
    print('[ok] operations overview')

    global_status, _, global_payload = request(
        'GET',
        f'{settings.api_core_url}/v1/operations/overview',
        headers={'Authorization': f'Bearer {global_token}'},
    )
    assert_condition(
        global_status == 200 and isinstance(global_payload, dict),
        'operations_overview_global_failed',
    )
    handoff_overview = global_payload.get('handoff_overview')
    assert_condition(isinstance(handoff_overview, dict), 'operations_handoff_overview_missing')
    assert_condition(
        isinstance(handoff_overview.get('priorities'), list) and handoff_overview['priorities'],
        'operations_handoff_priorities_missing',
    )
    assert_condition(
        isinstance(handoff_overview.get('aging_buckets'), list)
        and handoff_overview['aging_buckets'],
        'operations_handoff_aging_missing',
    )
    assert_condition(
        handoff_overview.get('oldest_open_ticket_code') is not None,
        'operations_oldest_open_ticket_missing',
    )
    print('[ok] global handoff overview')

    public_status, public_headers, public_payload = telegram_webhook_request(
        settings,
        update_id=9901,
        message_id=1,
        text='quais documentos sao exigidos para matricula?',
        chat_id=777001,
        username='visitante.publico',
        first_name='Visitante',
    )
    assert_condition(
        public_status == 200 and isinstance(public_payload, dict), 'public_webhook_failed'
    )
    assert_condition(
        'reply' in public_payload and 'document' in str(public_payload['reply']).lower(),
        'public_reply_unexpected',
    )
    public_trace_id = extract_trace_id(public_headers)
    print('[ok] public faq')

    library_status, _, library_payload = request(
        'POST',
        f'{settings.ai_orchestrator_url}/v1/messages/respond',
        headers={
            'Content-Type': 'application/json',
            'X-Internal-Api-Token': settings.internal_api_token,
        },
        json_body={
            'message': 'qual o horario da biblioteca? qual o nome da biblioteca?',
            'telegram_chat_id': 777001,
        },
    )
    assert_condition(
        library_status == 200 and isinstance(library_payload, dict), 'public_library_query_failed'
    )
    library_message = str(library_payload.get('message_text', ''))
    assert_condition('Biblioteca Aurora' in library_message, 'public_library_name_missing')
    assert_condition(
        '7h30' in library_message and '18h00' in library_message,
        'public_library_hours_missing',
    )
    assert_condition('reuniao geral de pais' not in library_message.lower(), 'public_library_calendar_leak')
    print('[ok] public library faq')

    graphrag_status, _, graphrag_payload = request(
        'POST',
        f'{settings.ai_orchestrator_url}/v1/messages/respond',
        headers={
            'Content-Type': 'application/json',
            'X-Internal-Api-Token': settings.internal_api_token,
        },
        json_body={
            'message': 'compare os principais temas do calendario e do manual de matricula',
            'telegram_chat_id': 777001,
        },
        timeout=60.0,
    )
    assert_condition(
        graphrag_status == 200 and isinstance(graphrag_payload, dict),
        'graphrag_runtime_failed',
    )
    assert_condition(graphrag_payload.get('mode') == 'graph_rag', 'graphrag_runtime_mode_invalid')
    assert_condition(
        graphrag_payload.get('retrieval_backend') == 'graph_rag',
        'graphrag_runtime_backend_invalid',
    )
    assert_condition(
        'advanced_retrieval_path' in graphrag_payload.get('risk_flags', []),
        'graphrag_runtime_risk_flag_missing',
    )
    assert_condition(
        len(str(graphrag_payload.get('message_text', '')).strip()) > 40,
        'graphrag_runtime_text_missing',
    )
    print('[ok] graphrag runtime')

    school_name_status, _, school_name_payload = request(
        'POST',
        f'{settings.ai_orchestrator_url}/v1/messages/respond',
        headers={
            'Content-Type': 'application/json',
            'X-Internal-Api-Token': settings.internal_api_token,
        },
        json_body={
            'message': 'qual o nome da escola',
            'telegram_chat_id': 777001,
        },
    )
    assert_condition(
        school_name_status == 200 and isinstance(school_name_payload, dict),
        'public_school_name_query_failed',
    )
    assert_condition(
        school_name_payload.get('mode') == 'structured_tool',
        'public_school_name_mode_invalid',
    )
    assert_condition(
        'Colegio Horizonte' in str(school_name_payload.get('message_text', '')),
        'public_school_name_missing',
    )
    print('[ok] public school name')

    negative_docs_status, _, negative_docs_payload = request(
        'POST',
        f'{settings.ai_orchestrator_url}/v1/messages/respond',
        headers={
            'Content-Type': 'application/json',
            'X-Internal-Api-Token': settings.internal_api_token,
        },
        json_body={
            'message': 'quais documentos nao preciso para a matricula?',
            'telegram_chat_id': 777001,
        },
    )
    assert_condition(
        negative_docs_status == 200 and isinstance(negative_docs_payload, dict),
        'negative_docs_query_failed',
    )
    negative_docs_message = str(negative_docs_payload.get('message_text', ''))
    assert_condition(
        'nao e seguro afirmar' in negative_docs_message.lower(),
        'negative_docs_guardrail_missing',
    )
    assert_condition(
        'dispensaveis' in negative_docs_message.lower(),
        'negative_docs_abstention_missing',
    )
    print('[ok] negative requirements abstention')

    exception_status, _, exception_payload = request(
        'POST',
        f'{settings.ai_orchestrator_url}/v1/messages/respond',
        headers={
            'Content-Type': 'application/json',
            'X-Internal-Api-Token': settings.internal_api_token,
        },
        json_body={
            'message': 'existe alguma excecao para comprovante de residencia na matricula?',
            'telegram_chat_id': 777001,
        },
    )
    assert_condition(
        exception_status == 200 and isinstance(exception_payload, dict),
        'public_exception_query_failed',
    )
    exception_message = str(exception_payload.get('message_text', ''))
    assert_condition(
        'comprovante de residencia' in exception_message.lower(),
        'public_exception_focus_missing',
    )
    assert_condition(
        'nao descreve excecoes' in exception_message.lower(),
        'public_exception_abstention_missing',
    )
    print('[ok] public exception abstention')

    comparison_status, _, comparison_payload = request(
        'POST',
        f'{settings.ai_orchestrator_url}/v1/messages/respond',
        headers={
            'Content-Type': 'application/json',
            'X-Internal-Api-Token': settings.internal_api_token,
        },
        json_body={
            'message': 'por que estudar nessa escola e nao na concorrente publica?',
            'telegram_chat_id': 777001,
        },
    )
    assert_condition(
        comparison_status == 200 and isinstance(comparison_payload, dict),
        'public_comparison_query_failed',
    )
    comparison_message = str(comparison_payload.get('message_text', ''))
    assert_condition(
        'nao sustenta uma comparacao justa' in comparison_message.lower(),
        'public_comparison_guardrail_missing',
    )
    assert_condition(
        'diferenciais documentados desta escola' in comparison_message.lower(),
        'public_comparison_followup_missing',
    )
    print('[ok] public comparison abstention')

    threaded_library_one_status, _, threaded_library_one_payload = request(
        'POST',
        f'{settings.ai_orchestrator_url}/v1/messages/respond',
        headers={
            'Content-Type': 'application/json',
            'X-Internal-Api-Token': settings.internal_api_token,
        },
        json_body={
            'message': 'qual o nome da biblioteca?',
            'conversation_id': 'smoke:library-thread',
            'telegram_chat_id': 777001,
        },
    )
    assert_condition(
        threaded_library_one_status == 200 and isinstance(threaded_library_one_payload, dict),
        'threaded_library_first_turn_failed',
    )
    threaded_library_two_status, _, threaded_library_two_payload = request(
        'POST',
        f'{settings.ai_orchestrator_url}/v1/messages/respond',
        headers={
            'Content-Type': 'application/json',
            'X-Internal-Api-Token': settings.internal_api_token,
        },
        json_body={
            'message': 'e qual o horario dela?',
            'conversation_id': 'smoke:library-thread',
            'telegram_chat_id': 777001,
        },
    )
    assert_condition(
        threaded_library_two_status == 200 and isinstance(threaded_library_two_payload, dict),
        'threaded_library_second_turn_failed',
    )
    threaded_library_message = str(threaded_library_two_payload.get('message_text', ''))
    assert_condition(
        '7h30' in threaded_library_message and '18h00' in threaded_library_message,
        'threaded_library_memory_missing',
    )
    print('[ok] conversational memory follow-up')

    protected_status, protected_headers, protected_payload = telegram_webhook_request(
        settings,
        update_id=9902,
        message_id=2,
        text='quero ver as notas do Lucas Oliveira',
        chat_id=555001,
        username='maria.oliveira',
        first_name='Maria',
    )
    assert_condition(
        protected_status == 200 and isinstance(protected_payload, dict), 'protected_webhook_failed'
    )
    assert_condition(
        'Resumo academico de Lucas Oliveira' in str(protected_payload.get('reply', '')),
        'protected_reply_unexpected',
    )
    protected_trace_id = extract_trace_id(protected_headers)
    print('[ok] protected academic')

    handoff_status, handoff_headers, handoff_payload = telegram_webhook_request(
        settings,
        update_id=9903,
        message_id=3,
        text='quero falar com um humano sobre o financeiro',
        chat_id=555001,
        username='maria.oliveira',
        first_name='Maria',
    )
    assert_condition(
        handoff_status == 200 and isinstance(handoff_payload, dict), 'handoff_webhook_failed'
    )
    assert_condition(
        'Protocolo:' in str(handoff_payload.get('reply', '')), 'handoff_reply_unexpected'
    )
    handoff_trace_id = extract_trace_id(handoff_headers)
    print('[ok] human handoff')

    handoff_list_status, _, handoff_list_payload = request(
        'GET',
        f'{settings.api_core_url}/v1/support/handoffs?page=1&limit=1',
        headers={'Authorization': f'Bearer {token}'},
    )
    assert_condition(
        handoff_list_status == 200 and isinstance(handoff_list_payload, dict),
        'support_handoff_list_failed',
    )
    pagination = handoff_list_payload.get('pagination')
    assert_condition(isinstance(pagination, dict), 'support_handoff_pagination_missing')
    assert_condition(pagination.get('page') == 1, 'support_handoff_pagination_page_invalid')
    assert_condition(
        pagination.get('page_size') == 1, 'support_handoff_pagination_page_size_invalid'
    )
    assert_condition(
        int(pagination.get('total_items', 0)) >= 1, 'support_handoff_pagination_total_invalid'
    )
    print('[ok] support handoff pagination')

    dashboard_status, _, dashboard_payload = request(
        'GET',
        f'{settings.grafana_url}/api/search?query=EduAssist%20Tracing%20Overview',
        headers=grafana_basic_auth_header(settings),
    )
    assert_condition(
        dashboard_status == 200 and isinstance(dashboard_payload, list) and dashboard_payload,
        'grafana_dashboard_missing',
    )
    print('[ok] grafana dashboard')

    metrics_dashboard_status, _, metrics_dashboard_payload = request(
        'GET',
        f'{settings.grafana_url}/api/search?query=EduAssist%20Metrics%20Overview',
        headers=grafana_basic_auth_header(settings),
    )
    assert_condition(
        metrics_dashboard_status == 200
        and isinstance(metrics_dashboard_payload, list)
        and metrics_dashboard_payload,
        'grafana_metrics_dashboard_missing',
    )
    print('[ok] grafana metrics dashboard')

    ops_dashboard_status, _, ops_dashboard_payload = request(
        'GET',
        f'{settings.grafana_url}/api/search?query=EduAssist%20Ops%20Control%20Tower',
        headers=grafana_basic_auth_header(settings),
    )
    assert_condition(
        ops_dashboard_status == 200 and isinstance(ops_dashboard_payload, list) and ops_dashboard_payload,
        'grafana_ops_dashboard_missing',
    )
    print('[ok] grafana ops dashboard')

    public_trace = wait_for_trace_span(
        settings, public_trace_id, 'eduassist.retrieval.hybrid_search'
    )
    public_spans = trace_span_names(public_trace)
    assert_condition(
        'eduassist.retrieval.hybrid_search' in public_spans, 'missing_public_retrieval_span'
    )
    print('[ok] tempo retrieval span')

    protected_trace = wait_for_trace_span(settings, protected_trace_id, 'eduassist.policy.decide')
    protected_spans = trace_span_names(protected_trace)
    assert_condition('eduassist.policy.decide' in protected_spans, 'missing_policy_span')
    print('[ok] tempo policy span')

    handoff_trace = wait_for_trace_span(
        settings, handoff_trace_id, 'eduassist.support.create_handoff'
    )
    handoff_spans = trace_span_names(handoff_trace)
    assert_condition('eduassist.support.create_handoff' in handoff_spans, 'missing_handoff_span')
    print('[ok] tempo handoff span')

    loki_payload = wait_for_loki_logs(settings, '{compose_service="telegram-gateway"}')
    loki_results = loki_payload.get('data', {}).get('result', [])
    assert_condition(isinstance(loki_results, list) and loki_results, 'loki_no_gateway_logs')
    print('[ok] loki gateway logs')

    policy_metrics = wait_for_prometheus_result(settings, 'sum(eduassist_policy_decisions_total)')
    retrieval_metrics = wait_for_prometheus_result(
        settings, 'sum(eduassist_retrieval_requests_total)'
    )
    handoff_metrics = wait_for_prometheus_result(
        settings, 'sum(eduassist_support_handoff_events_total)'
    )
    orchestration_metrics = wait_for_prometheus_result(
        settings, 'sum(eduassist_orchestration_responses_total)'
    )
    backlog_metrics = wait_for_prometheus_result(
        settings,
        'sum(eduassist_support_backlog_current{queue_name="all",status="all",sla_state="all"})',
    )
    backlog_age_metrics = wait_for_prometheus_result(
        settings,
        'sum(eduassist_support_backlog_age_current{queue_name="all",bucket_code="all"})',
    )
    priority_metrics = wait_for_prometheus_result(
        settings,
        'sum(eduassist_support_priority_current{queue_name="all",priority_code="all",sla_state="all"})',
    )
    unassigned_metrics = wait_for_prometheus_result(
        settings,
        'sum(eduassist_support_unassigned_current{queue_name="all"})',
    )
    assert_condition(float(policy_metrics[0]['value'][1]) > 0, 'prometheus_policy_metrics_empty')
    assert_condition(
        float(retrieval_metrics[0]['value'][1]) > 0, 'prometheus_retrieval_metrics_empty'
    )
    assert_condition(float(handoff_metrics[0]['value'][1]) > 0, 'prometheus_handoff_metrics_empty')
    assert_condition(
        float(orchestration_metrics[0]['value'][1]) > 0, 'prometheus_orchestration_metrics_empty'
    )
    assert_condition(
        float(backlog_metrics[0]['value'][1]) > 0, 'prometheus_support_backlog_metrics_empty'
    )
    assert_condition(
        float(backlog_age_metrics[0]['value'][1]) > 0,
        'prometheus_support_backlog_age_metrics_empty',
    )
    assert_condition(
        float(priority_metrics[0]['value'][1]) > 0, 'prometheus_support_priority_metrics_empty'
    )
    assert_condition(
        float(unassigned_metrics[0]['value'][1]) >= 0,
        'prometheus_support_unassigned_metrics_missing',
    )
    prometheus_health_payload = prometheus_query(settings, 'up{job="otel-collector"}')
    prometheus_health_result = prometheus_health_payload.get('data', {}).get('result', [])
    assert_condition(
        isinstance(prometheus_health_result, list) and prometheus_health_result,
        'prometheus_otel_scrape_missing',
    )
    print('[ok] prometheus domain metrics')

    print('Smoke suite finished successfully.')
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except AssertionError as exc:
        print(f'[fail] {exc}', file=sys.stderr)
        raise SystemExit(1)
