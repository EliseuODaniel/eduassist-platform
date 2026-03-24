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

    greeting_status, _, greeting_payload = request(
        'POST',
        f'{settings.ai_orchestrator_url}/v1/messages/respond',
        headers={
            'Content-Type': 'application/json',
            'X-Internal-Api-Token': settings.internal_api_token,
        },
        json_body={
            'message': 'ola',
            'telegram_chat_id': 777001,
        },
    )
    assert_condition(
        greeting_status == 200 and isinstance(greeting_payload, dict),
        'public_greeting_query_failed',
    )
    greeting_message = str(greeting_payload.get('message_text', ''))
    assert_condition('eduassist' in greeting_message.lower(), 'public_greeting_role_missing')
    assert_condition(
        'colegio horizonte' in greeting_message.lower() or 'estou por aqui' in greeting_message.lower(),
        'public_greeting_school_missing',
    )
    assert_condition('como posso ajudar' not in greeting_message.lower(), 'public_greeting_generic_message')
    print('[ok] public institutional greeting')

    identity_status, _, identity_payload = request(
        'POST',
        f'{settings.ai_orchestrator_url}/v1/messages/respond',
        headers={
            'Content-Type': 'application/json',
            'X-Internal-Api-Token': settings.internal_api_token,
        },
        json_body={
            'message': 'com quem eu falo?',
            'telegram_chat_id': 777001,
        },
    )
    assert_condition(
        identity_status == 200 and isinstance(identity_payload, dict),
        'public_identity_query_failed',
    )
    identity_message = str(identity_payload.get('message_text', ''))
    assert_condition('eduassist' in identity_message.lower(), 'public_identity_name_missing')
    assert_condition('secretaria' in identity_message.lower(), 'public_identity_sector_missing')
    print('[ok] public assistant identity')

    capabilities_status, _, capabilities_payload = request(
        'POST',
        f'{settings.ai_orchestrator_url}/v1/messages/respond',
        headers={
            'Content-Type': 'application/json',
            'X-Internal-Api-Token': settings.internal_api_token,
        },
        json_body={
            'message': 'quais opcoes de assuntos eu tenho aqui?',
            'telegram_chat_id': 777001,
        },
    )
    assert_condition(
        capabilities_status == 200 and isinstance(capabilities_payload, dict),
        'public_capabilities_query_failed',
    )
    capabilities_message = str(capabilities_payload.get('message_text', ''))
    assert_condition('matricula' in capabilities_message.lower(), 'public_capabilities_admissions_missing')
    assert_condition('secretaria' in capabilities_message.lower(), 'public_capabilities_secretaria_missing')
    assert_condition('financeiro' in capabilities_message.lower(), 'public_capabilities_finance_missing')
    print('[ok] public assistant capabilities')

    routing_status, _, routing_payload = request(
        'POST',
        f'{settings.ai_orchestrator_url}/v1/messages/respond',
        headers={
            'Content-Type': 'application/json',
            'X-Internal-Api-Token': settings.internal_api_token,
        },
        json_body={
            'message': 'com quem eu falo sobre boletos?',
            'telegram_chat_id': 777001,
        },
    )
    assert_condition(
        routing_status == 200 and isinstance(routing_payload, dict),
        'public_routing_query_failed',
    )
    routing_message = str(routing_payload.get('message_text', ''))
    assert_condition('financeiro' in routing_message.lower(), 'public_routing_finance_missing')
    assert_condition('prazo' in routing_message.lower(), 'public_routing_eta_missing')
    print('[ok] public service routing')

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

    tuition_status, _, tuition_payload = request(
        'POST',
        f'{settings.ai_orchestrator_url}/v1/messages/respond',
        headers={
            'Content-Type': 'application/json',
            'X-Internal-Api-Token': settings.internal_api_token,
        },
        json_body={
            'message': 'qual a mensalidade do ensino medio?',
            'telegram_chat_id': 777001,
        },
    )
    assert_condition(
        tuition_status == 200 and isinstance(tuition_payload, dict),
        'public_tuition_query_failed',
    )
    assert_condition(tuition_payload.get('mode') == 'structured_tool', 'public_tuition_mode_invalid')
    tuition_message = str(tuition_payload.get('message_text', ''))
    assert_condition('1450.00' in tuition_message, 'public_tuition_amount_missing')
    assert_condition('350.00' in tuition_message, 'public_tuition_enrollment_fee_missing')
    print('[ok] public tuition reference')

    schedule_status, _, schedule_payload = request(
        'POST',
        f'{settings.ai_orchestrator_url}/v1/messages/respond',
        headers={
            'Content-Type': 'application/json',
            'X-Internal-Api-Token': settings.internal_api_token,
        },
        json_body={
            'message': 'qual o horario do ensino medio?',
            'conversation_id': 'smoke:school-schedule-thread',
            'telegram_chat_id': 777001,
        },
    )
    assert_condition(
        schedule_status == 200 and isinstance(schedule_payload, dict),
        'public_schedule_query_failed',
    )
    assert_condition(schedule_payload.get('mode') == 'structured_tool', 'public_schedule_mode_invalid')
    schedule_message = str(schedule_payload.get('message_text', ''))
    assert_condition('07:15' in schedule_message and '12:50' in schedule_message, 'public_schedule_hours_missing')
    followup_schedule_status, _, followup_schedule_payload = request(
        'POST',
        f'{settings.ai_orchestrator_url}/v1/messages/respond',
        headers={
            'Content-Type': 'application/json',
            'X-Internal-Api-Token': settings.internal_api_token,
        },
        json_body={
            'message': 'e o fundamental?',
            'conversation_id': 'smoke:school-schedule-thread',
            'telegram_chat_id': 777001,
        },
    )
    assert_condition(
        followup_schedule_status == 200 and isinstance(followup_schedule_payload, dict),
        'public_schedule_followup_failed',
    )
    followup_schedule_message = str(followup_schedule_payload.get('message_text', ''))
    assert_condition(
        'fundamental ii' in followup_schedule_message.lower(),
        'public_schedule_followup_segment_missing',
    )
    assert_condition(
        '07:15' in followup_schedule_message and '12:30' in followup_schedule_message,
        'public_schedule_followup_hours_missing',
    )
    print('[ok] public schedule canonical')

    ninth_grade_status, _, ninth_grade_payload = request(
        'POST',
        f'{settings.ai_orchestrator_url}/v1/messages/respond',
        headers={
            'Content-Type': 'application/json',
            'X-Internal-Api-Token': settings.internal_api_token,
        },
        json_body={
            'message': 'que horario tem aula pro 9o ano?',
            'telegram_chat_id': 777001,
        },
    )
    assert_condition(
        ninth_grade_status == 200 and isinstance(ninth_grade_payload, dict),
        'public_ninth_grade_query_failed',
    )
    ninth_grade_message = str(ninth_grade_payload.get('message_text', ''))
    assert_condition(
        'ensino fundamental ii' in ninth_grade_message.lower(),
        'public_ninth_grade_segment_missing',
    )
    assert_condition(
        '07:15' in ninth_grade_message and '12:30' in ninth_grade_message,
        'public_ninth_grade_hours_missing',
    )
    print('[ok] public ninth grade schedule')

    director_status, _, director_payload = request(
        'POST',
        f'{settings.ai_orchestrator_url}/v1/messages/respond',
        headers={
            'Content-Type': 'application/json',
            'X-Internal-Api-Token': settings.internal_api_token,
        },
        json_body={
            'message': 'qual o nome da diretora?',
            'telegram_chat_id': 777001,
        },
    )
    assert_condition(
        director_status == 200 and isinstance(director_payload, dict),
        'public_director_query_failed',
    )
    director_message = str(director_payload.get('message_text', ''))
    assert_condition('Helena Martins' in director_message, 'public_director_name_missing')
    assert_condition('Diretora geral' in director_message, 'public_director_title_missing')
    print('[ok] public leadership profile')

    approval_status, _, approval_payload = request(
        'POST',
        f'{settings.ai_orchestrator_url}/v1/messages/respond',
        headers={
            'Content-Type': 'application/json',
            'X-Internal-Api-Token': settings.internal_api_token,
        },
        json_body={
            'message': 'qual a media de aprovacao?',
            'telegram_chat_id': 777001,
        },
    )
    assert_condition(
        approval_status == 200 and isinstance(approval_payload, dict),
        'public_approval_query_failed',
    )
    approval_message = str(approval_payload.get('message_text', ''))
    assert_condition('96.4%' in approval_message, 'public_approval_value_missing')
    print('[ok] public institutional kpi')

    curiosity_status, _, curiosity_payload = request(
        'POST',
        f'{settings.ai_orchestrator_url}/v1/messages/respond',
        headers={
            'Content-Type': 'application/json',
            'X-Internal-Api-Token': settings.internal_api_token,
        },
        json_body={
            'message': 'fale uma curiosidade unica dessa escola',
            'telegram_chat_id': 777001,
        },
    )
    assert_condition(
        curiosity_status == 200 and isinstance(curiosity_payload, dict),
        'public_curiosity_query_failed',
    )
    curiosity_message = str(curiosity_payload.get('message_text', ''))
    assert_condition(
        'curiosidade documentada' in curiosity_message.lower(),
        'public_curiosity_intro_missing',
    )
    assert_condition(
        'espaco maker integrado ao curriculo' in curiosity_message.lower(),
        'public_curiosity_highlight_missing',
    )
    print('[ok] public curiosity highlight')

    visit_status, _, visit_payload = request(
        'POST',
        f'{settings.ai_orchestrator_url}/v1/messages/respond',
        headers={
            'Content-Type': 'application/json',
            'X-Internal-Api-Token': settings.internal_api_token,
        },
        json_body={
            'message': 'quero agendar uma visita para conhecer a escola na quinta a tarde',
            'telegram_chat_id': 777001,
        },
    )
    assert_condition(
        visit_status == 200 and isinstance(visit_payload, dict),
        'public_visit_workflow_failed',
    )
    visit_message = str(visit_payload.get('message_text', ''))
    assert_condition('VIS-' in visit_message, 'public_visit_protocol_missing')
    assert_condition('Ticket operacional' in visit_message, 'public_visit_ticket_missing')
    print('[ok] public visit workflow')

    request_status, _, request_payload = request(
        'POST',
        f'{settings.ai_orchestrator_url}/v1/messages/respond',
        headers={
            'Content-Type': 'application/json',
            'X-Internal-Api-Token': settings.internal_api_token,
        },
        json_body={
            'message': 'quero protocolar uma solicitacao para a direcao sobre ampliacao do horario da biblioteca',
            'telegram_chat_id': 777001,
        },
    )
    assert_condition(
        request_status == 200 and isinstance(request_payload, dict),
        'public_institutional_request_failed',
    )
    institutional_request_message = str(request_payload.get('message_text', ''))
    assert_condition('REQ-' in institutional_request_message, 'public_institutional_request_protocol_missing')
    assert_condition('direcao' in institutional_request_message.lower(), 'public_institutional_request_target_missing')
    print('[ok] public institutional request workflow')

    visual_status, _, visual_payload = request(
        'POST',
        f'{settings.ai_orchestrator_url}/v1/messages/respond',
        headers={
            'Content-Type': 'application/json',
            'X-Internal-Api-Token': settings.internal_api_token,
        },
        json_body={
            'message': 'mostre um grafico da media de aprovacao da escola',
            'telegram_chat_id': 777001,
        },
    )
    assert_condition(
        visual_status == 200 and isinstance(visual_payload, dict),
        'public_visual_query_failed',
    )
    visual_assets = visual_payload.get('visual_assets')
    assert_condition(isinstance(visual_assets, list) and visual_assets, 'public_visual_assets_missing')
    first_visual = visual_assets[0]
    assert_condition(isinstance(first_visual, dict), 'public_visual_asset_invalid')
    assert_condition(first_visual.get('mime_type') == 'image/png', 'public_visual_asset_mime_invalid')
    assert_condition(first_visual.get('base64_data'), 'public_visual_asset_data_missing')
    print('[ok] public visual chart')

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
    assert_condition(not comparison_payload.get('citations'), 'public_comparison_citations_should_be_empty')
    print('[ok] public comparison abstention')

    confessional_status, _, confessional_payload = request(
        'POST',
        f'{settings.ai_orchestrator_url}/v1/messages/respond',
        headers={
            'Content-Type': 'application/json',
            'X-Internal-Api-Token': settings.internal_api_token,
        },
        json_body={
            'message': 'e uma escola confessional?',
            'telegram_chat_id': 777001,
        },
    )
    assert_condition(
        confessional_status == 200 and isinstance(confessional_payload, dict),
        'public_confessional_query_failed',
    )
    assert_condition(
        confessional_payload.get('mode') == 'structured_tool',
        'public_confessional_mode_invalid',
    )
    confessional_message = str(confessional_payload.get('message_text', ''))
    assert_condition(
        'escola laica' in confessional_message.lower(),
        'public_confessional_value_missing',
    )
    assert_condition(
        'nao confessional' in confessional_message.lower(),
        'public_confessional_qualifier_missing',
    )
    print('[ok] public confessional profile')

    facilities_status, _, facilities_payload = request(
        'POST',
        f'{settings.ai_orchestrator_url}/v1/messages/respond',
        headers={
            'Content-Type': 'application/json',
            'X-Internal-Api-Token': settings.internal_api_token,
        },
        json_body={
            'message': 'tem academia, piscina, quadra de tenis, futebol, aulas de danca?',
            'telegram_chat_id': 777001,
        },
    )
    assert_condition(
        facilities_status == 200 and isinstance(facilities_payload, dict),
        'public_facilities_query_failed',
    )
    assert_condition(facilities_payload.get('mode') == 'structured_tool', 'public_facilities_mode_invalid')
    facilities_message = str(facilities_payload.get('message_text', ''))
    assert_condition(
        'nao: piscina' in facilities_message.lower(),
        'public_facilities_pool_missing',
    )
    assert_condition('sim: futsal' in facilities_message.lower(), 'public_facilities_futsal_missing')
    assert_condition('sim: oficina de danca' in facilities_message.lower(), 'public_facilities_dance_missing')
    print('[ok] public facilities profile')

    contacts_status, _, contacts_payload = request(
        'POST',
        f'{settings.ai_orchestrator_url}/v1/messages/respond',
        headers={
            'Content-Type': 'application/json',
            'X-Internal-Api-Token': settings.internal_api_token,
        },
        json_body={
            'message': 'quais canais oficiais de contato?',
            'telegram_chat_id': 777001,
        },
    )
    assert_condition(
        contacts_status == 200 and isinstance(contacts_payload, dict),
        'public_contacts_query_failed',
    )
    assert_condition(contacts_payload.get('mode') == 'structured_tool', 'public_contacts_mode_invalid')
    contacts_message = str(contacts_payload.get('message_text', ''))
    assert_condition('3333-4200' in contacts_message, 'public_contacts_phone_missing')
    assert_condition('97500-2040' in contacts_message, 'public_contacts_whatsapp_missing')
    assert_condition('secretaria@colegiohorizonte.edu.br' in contacts_message, 'public_contacts_email_missing')
    print('[ok] public contacts profile')

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

    expanded_protected_status, _, expanded_protected_payload = telegram_webhook_request(
        settings,
        update_id=9912,
        message_id=12,
        text='quero ver as notas da Sofia Souza',
        chat_id=555003,
        username='fernanda.souza',
        first_name='Fernanda',
    )
    assert_condition(
        expanded_protected_status == 200 and isinstance(expanded_protected_payload, dict),
        'expanded_guardian_webhook_failed',
    )
    assert_condition(
        'Resumo academico de Sofia Souza' in str(expanded_protected_payload.get('reply', '')),
        'expanded_guardian_reply_unexpected',
    )
    print('[ok] expanded guardian academic')

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
