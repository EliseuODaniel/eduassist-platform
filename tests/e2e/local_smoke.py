from __future__ import annotations

import re
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


def _extract_protocol(message: str, prefix: str) -> str:
    match = re.search(rf'{re.escape(prefix)}-\d{{8}}-[A-Z0-9]+', message)
    assert_condition(match is not None, f'missing_protocol:{prefix}')
    return str(match.group(0))


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

    help_status, _, help_payload = telegram_webhook_request(
        settings,
        update_id=9902,
        message_id=2,
        text='/help',
        chat_id=777001,
        username='visitante.publico',
        first_name='Visitante',
    )
    assert_condition(help_status == 200 and isinstance(help_payload, dict), 'help_webhook_failed')
    assert_condition(help_payload.get('processed') == 'orchestrated_message', 'help_still_static')
    help_reply = str(help_payload.get('reply', ''))
    assert_condition('matricula' in help_reply.lower(), 'help_reply_topics_missing')
    assert_condition('financeiro' in help_reply.lower(), 'help_reply_finance_missing')
    help_reply_markup = help_payload.get('reply_markup')
    assert_condition(isinstance(help_reply_markup, dict), 'help_reply_markup_missing')
    help_keyboard = help_reply_markup.get('keyboard')
    assert_condition(isinstance(help_keyboard, list) and help_keyboard, 'help_reply_keyboard_missing')
    print('[ok] telegram help via orchestrator')

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
    greeting_suggestions = greeting_payload.get('suggested_replies')
    assert_condition(isinstance(greeting_suggestions, list) and greeting_suggestions, 'public_greeting_suggestions_missing')
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

    call_status, _, call_payload = request(
        'POST',
        f'{settings.ai_orchestrator_url}/v1/messages/respond',
        headers={
            'Content-Type': 'application/json',
            'X-Internal-Api-Token': settings.internal_api_token,
        },
        json_body={
            'message': 'como ligo pra escola?',
            'telegram_chat_id': 777001,
        },
    )
    assert_condition(call_status == 200 and isinstance(call_payload, dict), 'public_call_query_failed')
    call_message = str(call_payload.get('message_text', ''))
    assert_condition('(11) 3333-4200' in call_message, 'public_call_phone_missing')
    assert_condition('ainda nao encontrei' not in call_message.lower(), 'public_call_gap_message')
    print('[ok] public phone phrasing')

    phone_fax_status, _, phone_fax_payload = request(
        'POST',
        f'{settings.ai_orchestrator_url}/v1/messages/respond',
        headers={
            'Content-Type': 'application/json',
            'X-Internal-Api-Token': settings.internal_api_token,
        },
        json_body={
            'message': 'qual o telefone e o fax?',
            'telegram_chat_id': 777001,
        },
    )
    assert_condition(
        phone_fax_status == 200 and isinstance(phone_fax_payload, dict),
        'public_phone_fax_query_failed',
    )
    phone_fax_message = str(phone_fax_payload.get('message_text', ''))
    assert_condition('(11) 3333-4200' in phone_fax_message, 'public_phone_fax_phone_missing')
    assert_condition('nao publica numero de fax' in phone_fax_message.lower(), 'public_phone_fax_gap_missing')
    assert_condition('none' not in phone_fax_message.lower(), 'public_phone_fax_none_leak')
    print('[ok] public phone and fax query')

    address_status, _, address_payload = request(
        'POST',
        f'{settings.ai_orchestrator_url}/v1/messages/respond',
        headers={
            'Content-Type': 'application/json',
            'X-Internal-Api-Token': settings.internal_api_token,
        },
        json_body={
            'message': 'qual o endereco?',
            'telegram_chat_id': 777001,
        },
    )
    assert_condition(address_status == 200 and isinstance(address_payload, dict), 'public_address_query_failed')
    address_message = str(address_payload.get('message_text', ''))
    assert_condition('Rua das Acacias' in address_message, 'public_address_street_missing')
    assert_condition('CEP 04567-120' in address_message, 'public_address_cep_missing')
    print('[ok] public short address query')

    site_address_status, _, site_address_payload = request(
        'POST',
        f'{settings.ai_orchestrator_url}/v1/messages/respond',
        headers={
            'Content-Type': 'application/json',
            'X-Internal-Api-Token': settings.internal_api_token,
        },
        json_body={
            'message': 'qual o site e o endereco da escola?',
            'telegram_chat_id': 777001,
        },
    )
    assert_condition(
        site_address_status == 200 and isinstance(site_address_payload, dict),
        'public_site_address_query_failed',
    )
    site_address_message = str(site_address_payload.get('message_text', ''))
    assert_condition('https://www.colegiohorizonte.edu.br' in site_address_message, 'public_site_address_site_missing')
    assert_condition('Rua das Acacias' in site_address_message, 'public_site_address_street_missing')
    print('[ok] public site and address multi-intent query')

    segments_status, _, segments_payload = request(
        'POST',
        f'{settings.ai_orchestrator_url}/v1/messages/respond',
        headers={
            'Content-Type': 'application/json',
            'X-Internal-Api-Token': settings.internal_api_token,
        },
        json_body={
            'message': 'quais segmentos a escola atende?',
            'telegram_chat_id': 777001,
        },
    )
    assert_condition(
        segments_status == 200 and isinstance(segments_payload, dict),
        'public_segments_query_failed',
    )
    segments_message = str(segments_payload.get('message_text', ''))
    assert_condition('ensino fundamental ii' in segments_message.lower(), 'public_segments_fundamental_missing')
    assert_condition('ensino medio' in segments_message.lower(), 'public_segments_medio_missing')
    print('[ok] public segments query')

    school_name_segments_status, _, school_name_segments_payload = request(
        'POST',
        f'{settings.ai_orchestrator_url}/v1/messages/respond',
        headers={
            'Content-Type': 'application/json',
            'X-Internal-Api-Token': settings.internal_api_token,
        },
        json_body={
            'message': 'qual o nome da escola e quais segmentos ela atende?',
            'telegram_chat_id': 777001,
        },
    )
    assert_condition(
        school_name_segments_status == 200 and isinstance(school_name_segments_payload, dict),
        'public_school_name_segments_query_failed',
    )
    school_name_segments_message = str(school_name_segments_payload.get('message_text', ''))
    assert_condition('nome oficial da escola' in school_name_segments_message.lower(), 'public_school_name_segments_name_missing')
    assert_condition('ensino fundamental ii' in school_name_segments_message.lower(), 'public_school_name_segments_fundamental_missing')
    print('[ok] public school name plus segments multi-intent query')

    curriculum_status, _, curriculum_payload = request(
        'POST',
        f'{settings.ai_orchestrator_url}/v1/messages/respond',
        headers={
            'Content-Type': 'application/json',
            'X-Internal-Api-Token': settings.internal_api_token,
        },
        json_body={
            'message': 'quais materias sao ensinadas no ensino medio?',
            'telegram_chat_id': 777001,
        },
    )
    assert_condition(curriculum_status == 200 and isinstance(curriculum_payload, dict), 'public_curriculum_query_failed')
    curriculum_message = str(curriculum_payload.get('message_text', ''))
    assert_condition('matematica' in curriculum_message.lower(), 'public_curriculum_math_missing')
    assert_condition('biologia' in curriculum_message.lower(), 'public_curriculum_biology_missing')
    assert_condition('sua conta tem mais de um aluno vinculado' not in curriculum_message.lower(), 'public_curriculum_wrongly_protected')
    print('[ok] public curriculum query')

    opening_hours_status, _, opening_hours_payload = request(
        'POST',
        f'{settings.ai_orchestrator_url}/v1/messages/respond',
        headers={
            'Content-Type': 'application/json',
            'X-Internal-Api-Token': settings.internal_api_token,
        },
        json_body={
            'message': 'que horas amanha cedo a escola abre?',
            'telegram_chat_id': 777001,
            'conversation_id': 'smoke:operating-hours-thread',
        },
    )
    assert_condition(
        opening_hours_status == 200 and isinstance(opening_hours_payload, dict),
        'public_opening_hours_query_failed',
    )
    opening_hours_message = str(opening_hours_payload.get('message_text', ''))
    assert_condition('7h00' in opening_hours_message, 'public_opening_hours_missing')
    assert_condition('ainda nao encontrei' not in opening_hours_message.lower(), 'public_opening_hours_gap_message')
    print('[ok] public colloquial opening hours query')

    closing_hours_status, _, closing_hours_payload = request(
        'POST',
        f'{settings.ai_orchestrator_url}/v1/messages/respond',
        headers={
            'Content-Type': 'application/json',
            'X-Internal-Api-Token': settings.internal_api_token,
        },
        json_body={
            'message': 'e fecha que horas?',
            'telegram_chat_id': 777001,
            'conversation_id': 'smoke:operating-hours-thread',
        },
    )
    assert_condition(
        closing_hours_status == 200 and isinstance(closing_hours_payload, dict),
        'public_closing_hours_followup_failed',
    )
    closing_hours_message = str(closing_hours_payload.get('message_text', ''))
    assert_condition('17h30' in closing_hours_message, 'public_closing_hours_missing')
    assert_condition('fecha as 17h30' in closing_hours_message.lower(), 'public_closing_hours_phrase_missing')
    print('[ok] public colloquial closing hours follow-up')

    admissions_timeline_status, _, admissions_timeline_payload = request(
        'POST',
        f'{settings.ai_orchestrator_url}/v1/messages/respond',
        headers={
            'Content-Type': 'application/json',
            'X-Internal-Api-Token': settings.internal_api_token,
        },
        json_body={
            'message': 'quando começa a matrícula?',
            'telegram_chat_id': 777001,
            'conversation_id': 'smoke:timeline-thread',
        },
    )
    assert_condition(
        admissions_timeline_status == 200 and isinstance(admissions_timeline_payload, dict),
        'public_admissions_timeline_failed',
    )
    admissions_timeline_message = str(admissions_timeline_payload.get('message_text', ''))
    assert_condition(
        admissions_timeline_payload.get('mode') == 'structured_tool',
        'public_admissions_timeline_mode_invalid',
    )
    assert_condition(
        admissions_timeline_payload.get('classification', {}).get('domain') == 'calendar',
        'public_admissions_timeline_domain_invalid',
    )
    assert_condition(
        'get_public_timeline' in admissions_timeline_payload.get('selected_tools', []),
        'public_admissions_timeline_tool_missing',
    )
    assert_condition(
        '6 de outubro de 2025' in admissions_timeline_message,
        'public_admissions_timeline_date_missing',
    )
    print('[ok] public admissions timeline query')

    graduation_timeline_status, _, graduation_timeline_payload = request(
        'POST',
        f'{settings.ai_orchestrator_url}/v1/messages/respond',
        headers={
            'Content-Type': 'application/json',
            'X-Internal-Api-Token': settings.internal_api_token,
        },
        json_body={
            'message': 'quando é a formatura do ensino fundamental?',
            'telegram_chat_id': 777001,
            'conversation_id': 'smoke:timeline-thread',
        },
    )
    assert_condition(
        graduation_timeline_status == 200 and isinstance(graduation_timeline_payload, dict),
        'public_graduation_timeline_failed',
    )
    graduation_timeline_message = str(graduation_timeline_payload.get('message_text', ''))
    assert_condition(
        graduation_timeline_payload.get('mode') == 'structured_tool',
        'public_graduation_timeline_mode_invalid',
    )
    assert_condition(
        graduation_timeline_payload.get('classification', {}).get('domain') == 'calendar',
        'public_graduation_timeline_domain_invalid',
    )
    assert_condition(
        'get_public_timeline' in graduation_timeline_payload.get('selected_tools', []),
        'public_graduation_timeline_tool_missing',
    )
    assert_condition(
        '12 de dezembro de 2026' in graduation_timeline_message,
        'public_graduation_timeline_date_missing',
    )
    assert_condition(
        'segmentos' not in graduation_timeline_message.lower(),
        'public_graduation_timeline_segments_leak',
    )
    print('[ok] public graduation timeline query')

    school_year_start_status, _, school_year_start_payload = request(
        'POST',
        f'{settings.ai_orchestrator_url}/v1/messages/respond',
        headers={
            'Content-Type': 'application/json',
            'X-Internal-Api-Token': settings.internal_api_token,
        },
        json_body={
            'message': 'e quando começam as aulas?',
            'telegram_chat_id': 777001,
            'conversation_id': 'smoke:timeline-thread',
        },
    )
    assert_condition(
        school_year_start_status == 200 and isinstance(school_year_start_payload, dict),
        'public_school_year_start_timeline_failed',
    )
    school_year_start_message = str(school_year_start_payload.get('message_text', ''))
    assert_condition(
        school_year_start_payload.get('mode') == 'structured_tool',
        'public_school_year_start_timeline_mode_invalid',
    )
    assert_condition(
        'get_public_timeline' in school_year_start_payload.get('selected_tools', []),
        'public_school_year_start_timeline_tool_missing',
    )
    assert_condition(
        '2 de fevereiro de 2026' in school_year_start_message,
        'public_school_year_start_timeline_date_missing',
    )
    print('[ok] public school year start timeline follow-up')

    thanks_status, _, thanks_payload = request(
        'POST',
        f'{settings.ai_orchestrator_url}/v1/messages/respond',
        headers={
            'Content-Type': 'application/json',
            'X-Internal-Api-Token': settings.internal_api_token,
        },
        json_body={
            'message': 'obrigado',
            'telegram_chat_id': 777001,
        },
    )
    assert_condition(
        thanks_status == 200 and isinstance(thanks_payload, dict),
        'public_acknowledgement_query_failed',
    )
    thanks_message = str(thanks_payload.get('message_text', ''))
    assert_condition('por nada' in thanks_message.lower() or 'perfeito' in thanks_message.lower(), 'public_acknowledgement_missing')
    print('[ok] public acknowledgement turn')

    auth_help_status, _, auth_help_payload = request(
        'POST',
        f'{settings.ai_orchestrator_url}/v1/messages/respond',
        headers={
            'Content-Type': 'application/json',
            'X-Internal-Api-Token': settings.internal_api_token,
        },
        json_body={
            'message': 'como vinculo minha conta?',
            'telegram_chat_id': 777001,
        },
    )
    assert_condition(
        auth_help_status == 200 and isinstance(auth_help_payload, dict),
        'public_auth_guidance_failed',
    )
    auth_help_message = str(auth_help_payload.get('message_text', ''))
    assert_condition('/start link_' in auth_help_message, 'public_auth_guidance_link_missing')
    print('[ok] public auth guidance')

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
            'conversation_id': 'smoke:service-routing-thread',
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

    _, _, _ = request(
        'POST',
        f'{settings.ai_orchestrator_url}/v1/messages/respond',
        headers={
            'Content-Type': 'application/json',
            'X-Internal-Api-Token': settings.internal_api_token,
        },
        json_body={
            'message': 'quero resolver um boleto',
            'telegram_chat_id': 777002,
        },
    )
    routing_follow_up_status, _, routing_follow_up_payload = request(
        'POST',
        f'{settings.ai_orchestrator_url}/v1/messages/respond',
        headers={
            'Content-Type': 'application/json',
            'X-Internal-Api-Token': settings.internal_api_token,
        },
        json_body={
            'message': 'com quem eu falo?',
            'telegram_chat_id': 777002,
        },
    )
    assert_condition(
        routing_follow_up_status == 200 and isinstance(routing_follow_up_payload, dict),
        'public_routing_followup_failed',
    )
    routing_follow_up_message = str(routing_follow_up_payload.get('message_text', ''))
    assert_condition('financeiro' in routing_follow_up_message.lower(), 'public_routing_followup_finance_missing')
    print('[ok] public service routing follow-up')

    bullying_status, _, bullying_payload = request(
        'POST',
        f'{settings.ai_orchestrator_url}/v1/messages/respond',
        headers={
            'Content-Type': 'application/json',
            'X-Internal-Api-Token': settings.internal_api_token,
        },
        json_body={
            'message': 'como reporto um bullying?',
            'telegram_chat_id': 777003,
            'conversation_id': 'smoke:bullying-routing-thread',
        },
    )
    assert_condition(
        bullying_status == 200 and isinstance(bullying_payload, dict),
        'public_bullying_routing_failed',
    )
    bullying_message = str(bullying_payload.get('message_text', ''))
    assert_condition('orientacao educacional' in bullying_message.lower(), 'public_bullying_sector_missing')
    bullying_follow_up_status, _, bullying_follow_up_payload = request(
        'POST',
        f'{settings.ai_orchestrator_url}/v1/messages/respond',
        headers={
            'Content-Type': 'application/json',
            'X-Internal-Api-Token': settings.internal_api_token,
        },
        json_body={
            'message': 'mas com qual contato eu devo falar',
            'telegram_chat_id': 777003,
            'conversation_id': 'smoke:bullying-routing-thread',
        },
    )
    assert_condition(
        bullying_follow_up_status == 200 and isinstance(bullying_follow_up_payload, dict),
        'public_bullying_followup_failed',
    )
    bullying_follow_up_message = str(bullying_follow_up_payload.get('message_text', ''))
    assert_condition(
        'orientacao educacional' in bullying_follow_up_message.lower(),
        'public_bullying_followup_sector_missing',
    )
    assert_condition(
        'bot, orientacao educacional ou secretaria' in bullying_follow_up_message.lower(),
        'public_bullying_followup_channel_missing',
    )
    assert_condition(
        bullying_follow_up_message.lower().startswith('voce pode falar com'),
        'public_bullying_followup_direct_contact_missing',
    )
    bullying_phone_follow_up_status, _, bullying_phone_follow_up_payload = request(
        'POST',
        f'{settings.ai_orchestrator_url}/v1/messages/respond',
        headers={
            'Content-Type': 'application/json',
            'X-Internal-Api-Token': settings.internal_api_token,
        },
        json_body={
            'message': 'e o telefone?',
            'telegram_chat_id': 777003,
            'conversation_id': 'smoke:bullying-routing-thread',
        },
    )
    assert_condition(
        bullying_phone_follow_up_status == 200 and isinstance(bullying_phone_follow_up_payload, dict),
        'public_bullying_phone_followup_failed',
    )
    bullying_phone_follow_up_message = str(bullying_phone_follow_up_payload.get('message_text', ''))
    assert_condition('(11) 3333-4202' in bullying_phone_follow_up_message, 'public_bullying_phone_followup_missing')
    print('[ok] public bullying phone follow-up')
    print('[ok] public bullying routing follow-up')

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

    _, _, _ = request(
        'POST',
        f'{settings.ai_orchestrator_url}/v1/messages/respond',
        headers={
            'Content-Type': 'application/json',
            'X-Internal-Api-Token': settings.internal_api_token,
        },
        json_body={
            'message': 'essa escola tem biblioteca?',
            'telegram_chat_id': 777004,
            'conversation_id': 'smoke:library-followup-thread',
        },
    )
    library_follow_up_status, _, library_follow_up_payload = request(
        'POST',
        f'{settings.ai_orchestrator_url}/v1/messages/respond',
        headers={
            'Content-Type': 'application/json',
            'X-Internal-Api-Token': settings.internal_api_token,
        },
        json_body={
            'message': 'e qual o horario?',
            'telegram_chat_id': 777004,
            'conversation_id': 'smoke:library-followup-thread',
        },
    )
    assert_condition(
        library_follow_up_status == 200 and isinstance(library_follow_up_payload, dict),
        'public_library_followup_failed',
    )
    library_follow_up_message = str(library_follow_up_payload.get('message_text', ''))
    assert_condition('biblioteca aurora' in library_follow_up_message.lower(), 'public_library_followup_label_missing')
    assert_condition('7h30' in library_follow_up_message.lower(), 'public_library_followup_schedule_missing')
    print('[ok] public library schedule follow-up')

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

    _, _, _ = request(
        'POST',
        f'{settings.ai_orchestrator_url}/v1/messages/respond',
        headers={
            'Content-Type': 'application/json',
            'X-Internal-Api-Token': settings.internal_api_token,
        },
        json_body={
            'message': 'qual o nome da diretora?',
            'telegram_chat_id': 777005,
            'conversation_id': 'smoke:leadership-followup-thread',
        },
    )
    director_email_follow_up_status, _, director_email_follow_up_payload = request(
        'POST',
        f'{settings.ai_orchestrator_url}/v1/messages/respond',
        headers={
            'Content-Type': 'application/json',
            'X-Internal-Api-Token': settings.internal_api_token,
        },
        json_body={
            'message': 'e o email?',
            'telegram_chat_id': 777005,
            'conversation_id': 'smoke:leadership-followup-thread',
        },
    )
    assert_condition(
        director_email_follow_up_status == 200 and isinstance(director_email_follow_up_payload, dict),
        'public_director_email_followup_failed',
    )
    director_email_follow_up_message = str(director_email_follow_up_payload.get('message_text', ''))
    assert_condition(
        'direcao@colegiohorizonte.edu.br' in director_email_follow_up_message.lower(),
        'public_director_email_followup_missing',
    )
    print('[ok] public leadership email follow-up')

    director_age_status, _, director_age_payload = request(
        'POST',
        f'{settings.ai_orchestrator_url}/v1/messages/respond',
        headers={
            'Content-Type': 'application/json',
            'X-Internal-Api-Token': settings.internal_api_token,
        },
        json_body={
            'message': 'qual idade do diretor?',
            'telegram_chat_id': 777001,
        },
    )
    assert_condition(
        director_age_status == 200 and isinstance(director_age_payload, dict),
        'public_director_age_query_failed',
    )
    director_age_message = str(director_age_payload.get('message_text', ''))
    assert_condition('nao publica a idade' in director_age_message.lower(), 'public_director_age_gap_missing')
    assert_condition('helena martins' in director_age_message.lower(), 'public_director_age_identity_missing')
    print('[ok] public leadership age gap')

    director_whatsapp_status, _, director_whatsapp_payload = request(
        'POST',
        f'{settings.ai_orchestrator_url}/v1/messages/respond',
        headers={
            'Content-Type': 'application/json',
            'X-Internal-Api-Token': settings.internal_api_token,
        },
        json_body={
            'message': 'qual o whats do diretor?',
            'telegram_chat_id': 777001,
        },
    )
    assert_condition(
        director_whatsapp_status == 200 and isinstance(director_whatsapp_payload, dict),
        'public_director_whatsapp_query_failed',
    )
    director_whatsapp_message = str(director_whatsapp_payload.get('message_text', ''))
    assert_condition(
        'nao publica um whatsapp direto' in director_whatsapp_message.lower(),
        'public_director_whatsapp_gap_missing',
    )
    assert_condition(
        'direcao@colegiohorizonte.edu.br' in director_whatsapp_message.lower(),
        'public_director_whatsapp_email_missing',
    )
    print('[ok] public leadership contact gap')

    teacher_name_status, _, teacher_name_payload = request(
        'POST',
        f'{settings.ai_orchestrator_url}/v1/messages/respond',
        headers={
            'Content-Type': 'application/json',
            'X-Internal-Api-Token': settings.internal_api_token,
        },
        json_body={
            'message': 'qual o nome do prof de educacao fisica?',
            'telegram_chat_id': 777001,
        },
    )
    assert_condition(
        teacher_name_status == 200 and isinstance(teacher_name_payload, dict),
        'public_teacher_name_query_failed',
    )
    teacher_name_message = str(teacher_name_payload.get('message_text', ''))
    assert_condition(
        'nao divulga nomes nem contatos diretos de professores' in teacher_name_message.lower(),
        'public_teacher_name_privacy_missing',
    )
    assert_condition(
        'educacao fisica' in teacher_name_message.lower(),
        'public_teacher_name_subject_missing',
    )
    print('[ok] public teacher directory gap')

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
            'conversation_id': 'smoke:visit-thread',
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

    visit_status_status, _, visit_status_payload = request(
        'POST',
        f'{settings.ai_orchestrator_url}/v1/messages/respond',
        headers={
            'Content-Type': 'application/json',
            'X-Internal-Api-Token': settings.internal_api_token,
        },
        json_body={
            'message': 'e o status da visita?',
            'telegram_chat_id': 777001,
            'conversation_id': 'smoke:visit-thread',
        },
    )
    assert_condition(
        visit_status_status == 200 and isinstance(visit_status_payload, dict),
        'public_visit_status_failed',
    )
    visit_status_message = str(visit_status_payload.get('message_text', ''))
    assert_condition('VIS-' in visit_status_message, 'public_visit_status_protocol_missing')
    assert_condition('fila' in visit_status_message.lower(), 'public_visit_status_queue_missing')
    print('[ok] public visit workflow status')

    visit_update_status, _, visit_update_payload = request(
        'POST',
        f'{settings.ai_orchestrator_url}/v1/messages/respond',
        headers={
            'Content-Type': 'application/json',
            'X-Internal-Api-Token': settings.internal_api_token,
        },
        json_body={
            'message': 'tem alguma atualizacao da visita?',
            'telegram_chat_id': 777001,
            'conversation_id': 'smoke:visit-thread',
        },
    )
    assert_condition(
        visit_update_status == 200 and isinstance(visit_update_payload, dict),
        'public_visit_update_failed',
    )
    visit_update_message = str(visit_update_payload.get('message_text', ''))
    assert_condition('ultima atualizacao da sua visita' in visit_update_message.lower(), 'public_visit_update_intro_missing')
    assert_condition('ultima movimentacao registrada' in visit_update_message.lower(), 'public_visit_update_timestamp_missing')
    print('[ok] public visit workflow update')

    visit_protocol_status, _, visit_protocol_payload = request(
        'POST',
        f'{settings.ai_orchestrator_url}/v1/messages/respond',
        headers={
            'Content-Type': 'application/json',
            'X-Internal-Api-Token': settings.internal_api_token,
        },
        json_body={
            'message': 'qual o protocolo da visita?',
            'telegram_chat_id': 777001,
            'conversation_id': 'smoke:visit-thread',
        },
    )
    assert_condition(
        visit_protocol_status == 200 and isinstance(visit_protocol_payload, dict),
        'public_visit_protocol_followup_failed',
    )
    visit_protocol_message = str(visit_protocol_payload.get('message_text', ''))
    assert_condition('VIS-' in visit_protocol_message, 'public_visit_protocol_followup_missing')
    assert_condition('protocolo da sua visita' in visit_protocol_message.lower(), 'public_visit_protocol_followup_intro_missing')
    print('[ok] public visit workflow protocol follow-up')

    visit_reschedule_status, _, visit_reschedule_payload = request(
        'POST',
        f'{settings.ai_orchestrator_url}/v1/messages/respond',
        headers={
            'Content-Type': 'application/json',
            'X-Internal-Api-Token': settings.internal_api_token,
        },
        json_body={
            'message': 'quero remarcar a visita para sexta de manha',
            'telegram_chat_id': 777001,
            'conversation_id': 'smoke:visit-thread',
        },
    )
    assert_condition(
        visit_reschedule_status == 200 and isinstance(visit_reschedule_payload, dict),
        'public_visit_reschedule_failed',
    )
    visit_reschedule_message = str(visit_reschedule_payload.get('message_text', ''))
    assert_condition('Pedido de visita atualizado' in visit_reschedule_message, 'public_visit_reschedule_intro_missing')
    assert_condition('Nova preferencia' in visit_reschedule_message, 'public_visit_reschedule_preference_missing')
    print('[ok] public visit workflow reschedule')

    visit_stateful_status, _, visit_stateful_payload = request(
        'POST',
        f'{settings.ai_orchestrator_url}/v1/messages/respond',
        headers={
            'Content-Type': 'application/json',
            'X-Internal-Api-Token': settings.internal_api_token,
        },
        json_body={
            'message': 'Agendar visita',
            'telegram_chat_id': 777001,
            'conversation_id': 'smoke:visit-stateful-thread',
        },
    )
    assert_condition(
        visit_stateful_status == 200 and isinstance(visit_stateful_payload, dict),
        'public_visit_stateful_seed_failed',
    )
    visit_stateful_message = str(visit_stateful_payload.get('message_text', ''))
    visit_stateful_protocol = _extract_protocol(visit_stateful_message, 'VIS')
    assert_condition('janela a confirmar' in visit_stateful_message.lower(), 'public_visit_stateful_seed_window_missing')

    visit_stateful_tuesday_status, _, visit_stateful_tuesday_payload = request(
        'POST',
        f'{settings.ai_orchestrator_url}/v1/messages/respond',
        headers={
            'Content-Type': 'application/json',
            'X-Internal-Api-Token': settings.internal_api_token,
        },
        json_body={
            'message': 'quero terça de manhã',
            'telegram_chat_id': 777001,
            'conversation_id': 'smoke:visit-stateful-thread',
        },
    )
    assert_condition(
        visit_stateful_tuesday_status == 200 and isinstance(visit_stateful_tuesday_payload, dict),
        'public_visit_stateful_tuesday_failed',
    )
    visit_stateful_tuesday_message = str(visit_stateful_tuesday_payload.get('message_text', ''))
    assert_condition(visit_stateful_protocol in visit_stateful_tuesday_message, 'public_visit_stateful_tuesday_protocol_missing')
    assert_condition('Nova preferencia:' in visit_stateful_tuesday_message, 'public_visit_stateful_tuesday_preference_missing')
    assert_condition('- manha' in visit_stateful_tuesday_message, 'public_visit_stateful_tuesday_window_missing')

    visit_stateful_explicit_status, _, visit_stateful_explicit_payload = request(
        'POST',
        f'{settings.ai_orchestrator_url}/v1/messages/respond',
        headers={
            'Content-Type': 'application/json',
            'X-Internal-Api-Token': settings.internal_api_token,
        },
        json_body={
            'message': 'quero em 01/01/2024',
            'telegram_chat_id': 777001,
            'conversation_id': 'smoke:visit-stateful-thread',
        },
    )
    assert_condition(
        visit_stateful_explicit_status == 200 and isinstance(visit_stateful_explicit_payload, dict),
        'public_visit_stateful_explicit_date_failed',
    )
    visit_stateful_explicit_message = str(visit_stateful_explicit_payload.get('message_text', ''))
    assert_condition(visit_stateful_protocol in visit_stateful_explicit_message, 'public_visit_stateful_explicit_protocol_missing')
    assert_condition('01/01/2024 - manha' in visit_stateful_explicit_message, 'public_visit_stateful_explicit_date_missing')

    visit_stateful_implicit_status, _, visit_stateful_implicit_payload = request(
        'POST',
        f'{settings.ai_orchestrator_url}/v1/messages/respond',
        headers={
            'Content-Type': 'application/json',
            'X-Internal-Api-Token': settings.internal_api_token,
        },
        json_body={
            'message': 'então pode ser nesse dia',
            'telegram_chat_id': 777001,
            'conversation_id': 'smoke:visit-stateful-thread',
        },
    )
    assert_condition(
        visit_stateful_implicit_status == 200 and isinstance(visit_stateful_implicit_payload, dict),
        'public_visit_stateful_implicit_date_failed',
    )
    visit_stateful_implicit_message = str(visit_stateful_implicit_payload.get('message_text', ''))
    assert_condition(visit_stateful_protocol in visit_stateful_implicit_message, 'public_visit_stateful_implicit_protocol_missing')
    assert_condition('01/01/2024 - manha' in visit_stateful_implicit_message, 'public_visit_stateful_implicit_date_missing')
    print('[ok] public visit workflow stateful follow-up')

    visit_cancel_status, _, visit_cancel_payload = request(
        'POST',
        f'{settings.ai_orchestrator_url}/v1/messages/respond',
        headers={
            'Content-Type': 'application/json',
            'X-Internal-Api-Token': settings.internal_api_token,
        },
        json_body={
            'message': 'quero cancelar a visita',
            'telegram_chat_id': 777001,
            'conversation_id': 'smoke:visit-thread',
        },
    )
    assert_condition(
        visit_cancel_status == 200 and isinstance(visit_cancel_payload, dict),
        'public_visit_cancel_failed',
    )
    visit_cancel_message = str(visit_cancel_payload.get('message_text', ''))
    assert_condition('Visita cancelada' in visit_cancel_message, 'public_visit_cancel_intro_missing')
    assert_condition('VIS-' in visit_cancel_message, 'public_visit_cancel_protocol_missing')
    print('[ok] public visit workflow cancel')

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
            'conversation_id': 'smoke:request-thread',
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

    request_update_status, _, request_update_payload = request(
        'POST',
        f'{settings.ai_orchestrator_url}/v1/messages/respond',
        headers={
            'Content-Type': 'application/json',
            'X-Internal-Api-Token': settings.internal_api_token,
        },
        json_body={
            'message': 'quero complementar meu pedido dizendo que preciso de resposta ainda esta semana',
            'telegram_chat_id': 777001,
            'conversation_id': 'smoke:request-thread',
        },
    )
    assert_condition(
        request_update_status == 200 and isinstance(request_update_payload, dict),
        'public_institutional_request_update_failed',
    )
    request_update_message = str(request_update_payload.get('message_text', ''))
    assert_condition('Complemento registrado' in request_update_message, 'public_request_update_intro_missing')
    assert_condition('REQ-' in request_update_message, 'public_request_update_protocol_missing')
    assert_condition('resposta ainda esta semana' in request_update_message.lower(), 'public_request_update_details_missing')
    print('[ok] public institutional request update')

    request_status_status, _, request_status_payload = request(
        'POST',
        f'{settings.ai_orchestrator_url}/v1/messages/respond',
        headers={
            'Content-Type': 'application/json',
            'X-Internal-Api-Token': settings.internal_api_token,
        },
        json_body={
            'message': 'qual o status do meu protocolo?',
            'telegram_chat_id': 777001,
            'conversation_id': 'smoke:request-thread',
        },
    )
    assert_condition(
        request_status_status == 200 and isinstance(request_status_payload, dict),
        'public_institutional_request_status_failed',
    )
    request_status_message = str(request_status_payload.get('message_text', ''))
    assert_condition('REQ-' in request_status_message, 'public_request_status_protocol_missing')
    assert_condition('direcao' in request_status_message.lower(), 'public_request_status_target_missing')
    print('[ok] public institutional request status')

    request_update_info_status, _, request_update_info_payload = request(
        'POST',
        f'{settings.ai_orchestrator_url}/v1/messages/respond',
        headers={
            'Content-Type': 'application/json',
            'X-Internal-Api-Token': settings.internal_api_token,
        },
        json_body={
            'message': 'tem alguma atualizacao?',
            'telegram_chat_id': 777001,
            'conversation_id': 'smoke:request-thread',
        },
    )
    assert_condition(
        request_update_info_status == 200 and isinstance(request_update_info_payload, dict),
        'public_request_update_info_failed',
    )
    request_update_info_message = str(request_update_info_payload.get('message_text', ''))
    assert_condition('ultima atualizacao do seu protocolo' in request_update_info_message.lower(), 'public_request_update_info_intro_missing')
    assert_condition('ultima movimentacao registrada' in request_update_info_message.lower(), 'public_request_update_info_timestamp_missing')
    request_update_info_suggestions = request_update_info_payload.get('suggested_replies')
    assert_condition(
        isinstance(request_update_info_suggestions, list) and any(
            'proximo passo' in str(item.get('text', '')).lower()
            for item in request_update_info_suggestions
            if isinstance(item, dict)
        ),
        'public_request_update_info_suggestions_missing',
    )
    print('[ok] public institutional request update info')

    request_protocol_status, _, request_protocol_payload = request(
        'POST',
        f'{settings.ai_orchestrator_url}/v1/messages/respond',
        headers={
            'Content-Type': 'application/json',
            'X-Internal-Api-Token': settings.internal_api_token,
        },
        json_body={
            'message': 'qual o protocolo?',
            'telegram_chat_id': 777001,
            'conversation_id': 'smoke:request-thread',
        },
    )
    assert_condition(
        request_protocol_status == 200 and isinstance(request_protocol_payload, dict),
        'public_request_protocol_followup_failed',
    )
    request_protocol_message = str(request_protocol_payload.get('message_text', ''))
    assert_condition('REQ-' in request_protocol_message, 'public_request_protocol_followup_missing')
    assert_condition('protocolo da sua solicitacao' in request_protocol_message.lower(), 'public_request_protocol_followup_intro_missing')
    print('[ok] public institutional request protocol follow-up')

    request_summary_status, _, request_summary_payload = request(
        'POST',
        f'{settings.ai_orchestrator_url}/v1/messages/respond',
        headers={
            'Content-Type': 'application/json',
            'X-Internal-Api-Token': settings.internal_api_token,
        },
        json_body={
            'message': 'resume meu pedido',
            'telegram_chat_id': 777001,
            'conversation_id': 'smoke:request-thread',
        },
    )
    assert_condition(
        request_summary_status == 200 and isinstance(request_summary_payload, dict),
        'public_request_summary_followup_failed',
    )
    request_summary_message = str(request_summary_payload.get('message_text', ''))
    assert_condition('Resumo da sua solicitacao institucional' in request_summary_message, 'public_request_summary_intro_missing')
    assert_condition('direcao' in request_summary_message.lower(), 'public_request_summary_target_missing')
    assert_condition('resposta ainda esta semana' in request_summary_message.lower(), 'public_request_summary_update_missing')
    print('[ok] public institutional request summary follow-up')

    contextual_greeting_status, _, contextual_greeting_payload = request(
        'POST',
        f'{settings.ai_orchestrator_url}/v1/messages/respond',
        headers={
            'Content-Type': 'application/json',
            'X-Internal-Api-Token': settings.internal_api_token,
        },
        json_body={
            'message': 'oi',
            'telegram_chat_id': 777001,
            'conversation_id': 'smoke:request-thread',
        },
    )
    assert_condition(
        contextual_greeting_status == 200 and isinstance(contextual_greeting_payload, dict),
        'public_contextual_greeting_failed',
    )
    contextual_greeting_message = str(contextual_greeting_payload.get('message_text', ''))
    assert_condition('retomo sua solicitacao institucional' in contextual_greeting_message.lower(), 'public_contextual_greeting_resume_missing')
    assert_condition('REQ-' in contextual_greeting_message, 'public_contextual_greeting_protocol_missing')
    print('[ok] public contextual greeting after workflow')

    request_eta_status, _, request_eta_payload = request(
        'POST',
        f'{settings.ai_orchestrator_url}/v1/messages/respond',
        headers={
            'Content-Type': 'application/json',
            'X-Internal-Api-Token': settings.internal_api_token,
        },
        json_body={
            'message': 'qual o prazo?',
            'telegram_chat_id': 777001,
            'conversation_id': 'smoke:request-thread',
        },
    )
    assert_condition(
        request_eta_status == 200 and isinstance(request_eta_payload, dict),
        'public_institutional_request_eta_failed',
    )
    request_eta_message = str(request_eta_payload.get('message_text', ''))
    assert_condition('2 dias uteis' in request_eta_message.lower(), 'public_request_eta_missing')
    request_eta_suggestions = request_eta_payload.get('suggested_replies')
    assert_condition(isinstance(request_eta_suggestions, list) and request_eta_suggestions, 'public_request_eta_suggestions_missing')
    assert_condition(
        any(
            keyword in str(item.get('text', '')).lower()
            for keyword in {'complementar meu pedido', 'resume meu pedido'}
            for item in request_eta_suggestions
            if isinstance(item, dict)
        ),
        'public_request_eta_suggestions_not_contextual',
    )
    print('[ok] public institutional request eta')

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
        'nao' in facilities_message.lower() and 'piscina' in facilities_message.lower(),
        'public_facilities_pool_missing',
    )
    assert_condition('futsal' in facilities_message.lower(), 'public_facilities_futsal_missing')
    assert_condition('danca' in facilities_message.lower(), 'public_facilities_dance_missing')
    print('[ok] public facilities profile')

    feature_thread_one_status, _, feature_thread_one_payload = request(
        'POST',
        f'{settings.ai_orchestrator_url}/v1/messages/respond',
        headers={
            'Content-Type': 'application/json',
            'X-Internal-Api-Token': settings.internal_api_token,
        },
        json_body={
            'message': 'essa escola tem biblioteca?',
            'telegram_chat_id': 777001,
            'conversation_id': 'smoke:feature-thread',
        },
    )
    assert_condition(
        feature_thread_one_status == 200 and isinstance(feature_thread_one_payload, dict),
        'public_feature_thread_one_failed',
    )
    feature_thread_one_message = str(feature_thread_one_payload.get('message_text', ''))
    assert_condition(feature_thread_one_message.lower().startswith('sim.'), 'public_feature_library_tone_missing')
    assert_condition('biblioteca aurora' in feature_thread_one_message.lower(), 'public_feature_library_missing')
    feature_thread_one_suggestions = feature_thread_one_payload.get('suggested_replies')
    assert_condition(
        isinstance(feature_thread_one_suggestions, list) and any(
            'biblioteca' in str(item.get('text', '')).lower()
            for item in feature_thread_one_suggestions
            if isinstance(item, dict)
        ),
        'public_feature_library_suggestions_missing',
    )
    print('[ok] public feature library answer')

    feature_thread_two_status, _, feature_thread_two_payload = request(
        'POST',
        f'{settings.ai_orchestrator_url}/v1/messages/respond',
        headers={
            'Content-Type': 'application/json',
            'X-Internal-Api-Token': settings.internal_api_token,
        },
        json_body={
            'message': 'por que nao tem aula de danca?',
            'telegram_chat_id': 777001,
            'conversation_id': 'smoke:feature-thread',
        },
    )
    assert_condition(
        feature_thread_two_status == 200 and isinstance(feature_thread_two_payload, dict),
        'public_feature_thread_two_failed',
    )
    feature_thread_two_message = str(feature_thread_two_payload.get('message_text', ''))
    assert_condition('na verdade' in feature_thread_two_message.lower(), 'public_feature_dance_reframe_missing')
    assert_condition('tem sim' in feature_thread_two_message.lower(), 'public_feature_dance_correction_missing')
    assert_condition('danca' in feature_thread_two_message.lower(), 'public_feature_dance_missing')
    print('[ok] public feature false-negative correction')

    feature_thread_three_status, _, feature_thread_three_payload = request(
        'POST',
        f'{settings.ai_orchestrator_url}/v1/messages/respond',
        headers={
            'Content-Type': 'application/json',
            'X-Internal-Api-Token': settings.internal_api_token,
        },
        json_body={
            'message': 'e aula de computacao e robotica?',
            'telegram_chat_id': 777001,
            'conversation_id': 'smoke:feature-thread',
        },
    )
    assert_condition(
        feature_thread_three_status == 200 and isinstance(feature_thread_three_payload, dict),
        'public_feature_thread_three_failed',
    )
    feature_thread_three_message = str(feature_thread_three_payload.get('message_text', ''))
    assert_condition('espaco maker' in feature_thread_three_message.lower(), 'public_feature_robotics_missing')
    assert_condition('danca' not in feature_thread_three_message.lower(), 'public_feature_robotics_contaminated')
    print('[ok] public feature robotics follow-up')

    feature_thread_four_status, _, feature_thread_four_payload = request(
        'POST',
        f'{settings.ai_orchestrator_url}/v1/messages/respond',
        headers={
            'Content-Type': 'application/json',
            'X-Internal-Api-Token': settings.internal_api_token,
        },
        json_body={
            'message': 'e aula de fisica quantica avancada?',
            'telegram_chat_id': 777001,
            'conversation_id': 'smoke:feature-thread',
        },
    )
    assert_condition(
        feature_thread_four_status == 200 and isinstance(feature_thread_four_payload, dict),
        'public_feature_thread_four_failed',
    )
    feature_thread_four_message = str(feature_thread_four_payload.get('message_text', ''))
    assert_condition('nao encontrei uma referencia publica especifica' in feature_thread_four_message.lower(), 'public_feature_unknown_gap_missing')
    assert_condition('fisica quantica avancada' in feature_thread_four_message.lower(), 'public_feature_unknown_focus_missing')
    print('[ok] public feature unknown gap')

    feature_generic_status, _, feature_generic_payload = request(
        'POST',
        f'{settings.ai_orchestrator_url}/v1/messages/respond',
        headers={
            'Content-Type': 'application/json',
            'X-Internal-Api-Token': settings.internal_api_token,
        },
        json_body={
            'message': 'quais atividades tem?',
            'telegram_chat_id': 777001,
        },
    )
    assert_condition(
        feature_generic_status == 200 and isinstance(feature_generic_payload, dict),
        'public_feature_generic_failed',
    )
    assert_condition(feature_generic_payload.get('mode') == 'structured_tool', 'public_feature_generic_mode_invalid')
    feature_generic_message = str(feature_generic_payload.get('message_text', ''))
    assert_condition('atividades e espacos' in feature_generic_message.lower(), 'public_feature_generic_summary_missing')
    assert_condition('biblioteca' in feature_generic_message.lower(), 'public_feature_generic_library_missing')
    print('[ok] public feature generic inventory')

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

    secretary_status, _, secretary_payload = request(
        'POST',
        f'{settings.ai_orchestrator_url}/v1/messages/respond',
        headers={
            'Content-Type': 'application/json',
            'X-Internal-Api-Token': settings.internal_api_token,
        },
        json_body={
            'message': 'como falo com a secretaria?',
            'telegram_chat_id': 777001,
        },
    )
    assert_condition(
        secretary_status == 200 and isinstance(secretary_payload, dict),
        'public_secretary_routing_failed',
    )
    secretary_message = str(secretary_payload.get('message_text', ''))
    assert_condition('secretaria escolar e documentos' in secretary_message.lower(), 'public_secretary_routing_sector_missing')
    assert_condition('email institucional ou portal' in secretary_message.lower(), 'public_secretary_routing_channel_missing')
    print('[ok] public secretary routing')

    online_docs_status, _, online_docs_payload = request(
        'POST',
        f'{settings.ai_orchestrator_url}/v1/messages/respond',
        headers={
            'Content-Type': 'application/json',
            'X-Internal-Api-Token': settings.internal_api_token,
        },
        json_body={
            'message': 'aceita documentos online?',
            'telegram_chat_id': 777001,
        },
    )
    assert_condition(
        online_docs_status == 200 and isinstance(online_docs_payload, dict),
        'public_online_docs_query_failed',
    )
    assert_condition(online_docs_payload.get('mode') == 'structured_tool', 'public_online_docs_mode_invalid')
    online_docs_message = str(online_docs_payload.get('message_text', ''))
    assert_condition('portal institucional' in online_docs_message.lower(), 'public_online_docs_portal_missing')
    assert_condition('email da secretaria' in online_docs_message.lower() or 'secretaria@colegiohorizonte.edu.br' in online_docs_message.lower(), 'public_online_docs_email_missing')
    print('[ok] public online document submission')

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
        chat_id=1649845499,
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

    protected_followup_status, _, protected_followup_payload = telegram_webhook_request(
        settings,
        update_id=9904,
        message_id=4,
        text='e a frequencia?',
        chat_id=1649845499,
        username='maria.oliveira',
        first_name='Maria',
    )
    assert_condition(
        protected_followup_status == 200 and isinstance(protected_followup_payload, dict),
        'protected_followup_webhook_failed',
    )
    protected_followup_reply = str(protected_followup_payload.get('reply', ''))
    assert_condition(
        'Resumo academico de Lucas Oliveira' in protected_followup_reply,
        'protected_followup_student_memory_missing',
    )
    assert_condition(
        'Frequencia' in protected_followup_reply,
        'protected_followup_attendance_missing',
    )
    protected_followup_suggestions = (
        protected_followup_payload.get('orchestration', {}).get('suggested_replies')
        if isinstance(protected_followup_payload.get('orchestration'), dict)
        else None
    )
    assert_condition(
        isinstance(protected_followup_suggestions, list) and any(
            'lucas' in str(item.get('text', '')).lower()
            for item in protected_followup_suggestions
            if isinstance(item, dict)
        ),
        'protected_followup_suggestions_not_contextual',
    )
    print('[ok] protected academic follow-up memory')

    protected_finance_followup_status, _, protected_finance_followup_payload = telegram_webhook_request(
        settings,
        update_id=9905,
        message_id=5,
        text='e o financeiro?',
        chat_id=1649845499,
        username='maria.oliveira',
        first_name='Maria',
    )
    assert_condition(
        protected_finance_followup_status == 200 and isinstance(protected_finance_followup_payload, dict),
        'protected_finance_followup_webhook_failed',
    )
    protected_finance_followup_reply = str(protected_finance_followup_payload.get('reply', ''))
    assert_condition(
        'Resumo financeiro de Lucas Oliveira' in protected_finance_followup_reply,
        'protected_finance_followup_student_memory_missing',
    )
    protected_finance_suggestions = (
        protected_finance_followup_payload.get('orchestration', {}).get('suggested_replies')
        if isinstance(protected_finance_followup_payload.get('orchestration'), dict)
        else None
    )
    assert_condition(
        isinstance(protected_finance_suggestions, list) and any(
            'lucas' in str(item.get('text', '')).lower()
            for item in protected_finance_suggestions
            if isinstance(item, dict)
        ),
        'protected_finance_followup_suggestions_not_contextual',
    )
    print('[ok] protected finance follow-up memory')

    academic_registry_seed_status, _, academic_registry_seed_payload = request(
        'POST',
        f'{settings.ai_orchestrator_url}/v1/messages/respond',
        headers={
            'Content-Type': 'application/json',
            'X-Internal-Api-Token': settings.internal_api_token,
        },
        json_body={
            'message': 'quero ver as notas do Lucas Oliveira',
            'telegram_chat_id': 1649845499,
            'conversation_id': 'smoke:guardian-registry-thread',
        },
    )
    assert_condition(
        academic_registry_seed_status == 200 and isinstance(academic_registry_seed_payload, dict),
        'protected_registry_seed_failed',
    )
    academic_registry_followup_status, _, academic_registry_followup_payload = request(
        'POST',
        f'{settings.ai_orchestrator_url}/v1/messages/respond',
        headers={
            'Content-Type': 'application/json',
            'X-Internal-Api-Token': settings.internal_api_token,
        },
        json_body={
            'message': 'e a matricula?',
            'telegram_chat_id': 1649845499,
            'conversation_id': 'smoke:guardian-registry-thread',
        },
    )
    assert_condition(
        academic_registry_followup_status == 200 and isinstance(academic_registry_followup_payload, dict),
        'protected_registry_followup_failed',
    )
    academic_registry_followup_message = str(academic_registry_followup_payload.get('message_text', ''))
    assert_condition('MAT-2026-001' in academic_registry_followup_message, 'protected_registry_enrollment_missing')
    assert_condition('Lucas Oliveira' in academic_registry_followup_message, 'protected_registry_student_missing')
    print('[ok] protected academic registry follow-up')

    finance_identifier_seed_status, _, finance_identifier_seed_payload = request(
        'POST',
        f'{settings.ai_orchestrator_url}/v1/messages/respond',
        headers={
            'Content-Type': 'application/json',
            'X-Internal-Api-Token': settings.internal_api_token,
        },
        json_body={
            'message': 'preciso da segunda via do boleto da Ana Oliveira',
            'telegram_chat_id': 1649845499,
            'conversation_id': 'smoke:guardian-finance-identifier-thread',
        },
    )
    assert_condition(
        finance_identifier_seed_status == 200 and isinstance(finance_identifier_seed_payload, dict),
        'protected_finance_identifier_seed_failed',
    )
    finance_identifier_seed_message = str(finance_identifier_seed_payload.get('message_text', ''))
    assert_condition('segunda via' in finance_identifier_seed_message.lower(), 'protected_finance_identifier_seed_copy_missing')

    finance_identifier_followup_status, _, finance_identifier_followup_payload = request(
        'POST',
        f'{settings.ai_orchestrator_url}/v1/messages/respond',
        headers={
            'Content-Type': 'application/json',
            'X-Internal-Api-Token': settings.internal_api_token,
        },
        json_body={
            'message': 'qual o numero do boleto?',
            'telegram_chat_id': 1649845499,
            'conversation_id': 'smoke:guardian-finance-identifier-thread',
        },
    )
    assert_condition(
        finance_identifier_followup_status == 200 and isinstance(finance_identifier_followup_payload, dict),
        'protected_finance_identifier_followup_failed',
    )
    finance_identifier_followup_message = str(finance_identifier_followup_payload.get('message_text', ''))
    assert_condition(
        '4a935c4e-eafd-405e-8a54-007ae82f6698' in finance_identifier_followup_message,
        'protected_finance_identifier_missing',
    )
    assert_condition('segunda via' in finance_identifier_followup_message.lower(), 'protected_finance_identifier_copy_context_missing')
    print('[ok] protected finance identifier follow-up')

    finance_contract_status, _, finance_contract_payload = request(
        'POST',
        f'{settings.ai_orchestrator_url}/v1/messages/respond',
        headers={
            'Content-Type': 'application/json',
            'X-Internal-Api-Token': settings.internal_api_token,
        },
        json_body={
            'message': 'qual o codigo do contrato da Ana Oliveira?',
            'telegram_chat_id': 1649845499,
            'conversation_id': 'smoke:guardian-finance-contract-thread',
        },
    )
    assert_condition(
        finance_contract_status == 200 and isinstance(finance_contract_payload, dict),
        'protected_finance_contract_failed',
    )
    finance_contract_message = str(finance_contract_payload.get('message_text', ''))
    assert_condition('CTR-2026-002' in finance_contract_message, 'protected_finance_contract_code_missing')
    print('[ok] protected finance contract code')

    finance_overdue_status, _, finance_overdue_payload = request(
        'POST',
        f'{settings.ai_orchestrator_url}/v1/messages/respond',
        headers={
            'Content-Type': 'application/json',
            'X-Internal-Api-Token': settings.internal_api_token,
        },
        json_body={
            'message': 'tenho boletos atrasados?',
            'telegram_chat_id': 1649845499,
            'conversation_id': 'smoke:guardian-finance-status-thread',
        },
    )
    assert_condition(
        finance_overdue_status == 200 and isinstance(finance_overdue_payload, dict),
        'protected_finance_overdue_failed',
    )
    finance_overdue_message = str(finance_overdue_payload.get('message_text', ''))
    assert_condition(
        'hoje nao ha faturas vencidas' in finance_overdue_message.lower(),
        'protected_finance_overdue_empty_state_missing',
    )
    print('[ok] protected finance overdue empty state')

    finance_open_status, _, finance_open_payload = request(
        'POST',
        f'{settings.ai_orchestrator_url}/v1/messages/respond',
        headers={
            'Content-Type': 'application/json',
            'X-Internal-Api-Token': settings.internal_api_token,
        },
        json_body={
            'message': 'quais boletos da Ana Oliveira estao em aberto?',
            'telegram_chat_id': 1649845499,
            'conversation_id': 'smoke:guardian-finance-open-thread',
        },
    )
    assert_condition(
        finance_open_status == 200 and isinstance(finance_open_payload, dict),
        'protected_finance_open_failed',
    )
    finance_open_message = str(finance_open_payload.get('message_text', ''))
    assert_condition(
        'status em aberto' in finance_open_message.lower(),
        'protected_finance_open_status_wording_missing',
    )
    print('[ok] protected finance open invoice wording')

    subject_slot_seed_status, _, subject_slot_seed_payload = request(
        'POST',
        f'{settings.ai_orchestrator_url}/v1/messages/respond',
        headers={
            'Content-Type': 'application/json',
            'X-Internal-Api-Token': settings.internal_api_token,
        },
        json_body={
            'message': 'quais as minhas notas de fisica?',
            'telegram_chat_id': 1649845499,
            'conversation_id': 'smoke:guardian-physics-thread',
        },
    )
    assert_condition(
        subject_slot_seed_status == 200 and isinstance(subject_slot_seed_payload, dict),
        'protected_subject_slot_seed_failed',
    )
    assert_condition(
        'mais de um aluno vinculado' in str(subject_slot_seed_payload.get('message_text', '')).lower(),
        'protected_subject_slot_seed_clarification_missing',
    )
    subject_slot_followup_status, _, subject_slot_followup_payload = request(
        'POST',
        f'{settings.ai_orchestrator_url}/v1/messages/respond',
        headers={
            'Content-Type': 'application/json',
            'X-Internal-Api-Token': settings.internal_api_token,
        },
        json_body={
            'message': 'quais as notas do Lucas Oliveira?',
            'telegram_chat_id': 1649845499,
            'conversation_id': 'smoke:guardian-physics-thread',
        },
    )
    assert_condition(
        subject_slot_followup_status == 200 and isinstance(subject_slot_followup_payload, dict),
        'protected_subject_slot_followup_failed',
    )
    subject_slot_followup_message = str(subject_slot_followup_payload.get('message_text', ''))
    assert_condition('lucas oliveira' in subject_slot_followup_message.lower(), 'protected_subject_slot_student_missing')
    assert_condition('disciplina filtrada: fisica' in subject_slot_followup_message.lower(), 'protected_subject_slot_subject_missing')
    print('[ok] protected academic subject slot memory')

    upcoming_status, _, upcoming_payload = request(
        'POST',
        f'{settings.ai_orchestrator_url}/v1/messages/respond',
        headers={
            'Content-Type': 'application/json',
            'X-Internal-Api-Token': settings.internal_api_token,
        },
        json_body={
            'message': 'quais as proximas provas do Lucas Oliveira?',
            'telegram_chat_id': 1649845499,
            'conversation_id': 'smoke:guardian-upcoming-thread',
        },
    )
    assert_condition(
        upcoming_status == 200 and isinstance(upcoming_payload, dict),
        'protected_upcoming_assessments_failed',
    )
    upcoming_message = str(upcoming_payload.get('message_text', ''))
    assert_condition('proximas avaliacoes de lucas oliveira' in upcoming_message.lower(), 'protected_upcoming_header_missing')
    assert_condition('2026-' in upcoming_message, 'protected_upcoming_dates_missing')
    print('[ok] protected upcoming assessments')

    attendance_timeline_status, _, attendance_timeline_payload = request(
        'POST',
        f'{settings.ai_orchestrator_url}/v1/messages/respond',
        headers={
            'Content-Type': 'application/json',
            'X-Internal-Api-Token': settings.internal_api_token,
        },
        json_body={
            'message': 'qual data foram as faltas do Lucas Oliveira?',
            'telegram_chat_id': 1649845499,
            'conversation_id': 'smoke:guardian-attendance-thread',
        },
    )
    assert_condition(
        attendance_timeline_status == 200 and isinstance(attendance_timeline_payload, dict),
        'protected_attendance_timeline_failed',
    )
    attendance_timeline_message = str(attendance_timeline_payload.get('message_text', ''))
    assert_condition(
        'registros de frequencia de lucas oliveira' in attendance_timeline_message.lower(),
        'protected_attendance_timeline_header_missing',
    )
    assert_condition('2026-' in attendance_timeline_message, 'protected_attendance_timeline_dates_missing')
    print('[ok] protected attendance timeline')

    combined_status, _, combined_payload = request(
        'POST',
        f'{settings.ai_orchestrator_url}/v1/messages/respond',
        headers={
            'Content-Type': 'application/json',
            'X-Internal-Api-Token': settings.internal_api_token,
        },
        json_body={
            'message': 'quero saber se estou com a documentacao atualizada e completa e se meus boletos estao pagos ou atrasados',
            'telegram_chat_id': 1649845499,
            'conversation_id': 'smoke:guardian-admin-finance-thread',
        },
    )
    assert_condition(
        combined_status == 200 and isinstance(combined_payload, dict),
        'protected_finance_admin_combined_failed',
    )
    combined_message = str(combined_payload.get('message_text', ''))
    assert_condition('resumo financeiro' in combined_message.lower(), 'protected_finance_admin_finance_missing')
    assert_condition('cadastro e documentacao' in combined_message.lower(), 'protected_finance_admin_admin_missing')
    print('[ok] protected finance + documentation multi-intent')

    documentation_followup_status, _, documentation_followup_payload = request(
        'POST',
        f'{settings.ai_orchestrator_url}/v1/messages/respond',
        headers={
            'Content-Type': 'application/json',
            'X-Internal-Api-Token': settings.internal_api_token,
        },
        json_body={
            'message': 'e a documentacao, nao respondeu',
            'telegram_chat_id': 1649845499,
            'conversation_id': 'smoke:guardian-admin-finance-thread',
        },
    )
    assert_condition(
        documentation_followup_status == 200 and isinstance(documentation_followup_payload, dict),
        'protected_documentation_followup_failed',
    )
    documentation_followup_message = str(documentation_followup_payload.get('message_text', ''))
    assert_condition('situacao administrativa' in documentation_followup_message.lower(), 'protected_documentation_followup_status_missing')
    print('[ok] protected documentation follow-up')

    profile_update_status, _, profile_update_payload = request(
        'POST',
        f'{settings.ai_orchestrator_url}/v1/messages/respond',
        headers={
            'Content-Type': 'application/json',
            'X-Internal-Api-Token': settings.internal_api_token,
        },
        json_body={
            'message': 'como altero o endereco de email no meu cadastro?',
            'telegram_chat_id': 1649845499,
            'conversation_id': 'smoke:guardian-admin-thread',
        },
    )
    assert_condition(
        profile_update_status == 200 and isinstance(profile_update_payload, dict),
        'protected_profile_update_guidance_failed',
    )
    profile_update_message = str(profile_update_payload.get('message_text', ''))
    assert_condition('email cadastral' in profile_update_message.lower(), 'protected_profile_update_email_missing')
    assert_condition('secretaria escolar' in profile_update_message.lower(), 'protected_profile_update_secretaria_missing')
    print('[ok] protected profile update guidance')

    profile_phone_status, _, profile_phone_payload = request(
        'POST',
        f'{settings.ai_orchestrator_url}/v1/messages/respond',
        headers={
            'Content-Type': 'application/json',
            'X-Internal-Api-Token': settings.internal_api_token,
        },
        json_body={
            'message': 'e o telefone?',
            'telegram_chat_id': 1649845499,
            'conversation_id': 'smoke:guardian-admin-thread',
        },
    )
    assert_condition(
        profile_phone_status == 200 and isinstance(profile_phone_payload, dict),
        'protected_profile_update_phone_followup_failed',
    )
    profile_phone_message = str(profile_phone_payload.get('message_text', ''))
    assert_condition('+55 11 98888-1001' in profile_phone_message, 'protected_profile_update_phone_missing')
    assert_condition('telefone cadastral atual' in profile_phone_message.lower(), 'protected_profile_update_phone_label_missing')
    print('[ok] protected profile update phone follow-up')

    profile_documents_status, _, profile_documents_payload = request(
        'POST',
        f'{settings.ai_orchestrator_url}/v1/messages/respond',
        headers={
            'Content-Type': 'application/json',
            'X-Internal-Api-Token': settings.internal_api_token,
        },
        json_body={
            'message': 'e os documentos?',
            'telegram_chat_id': 1649845499,
            'conversation_id': 'smoke:guardian-admin-thread',
        },
    )
    assert_condition(
        profile_documents_status == 200 and isinstance(profile_documents_payload, dict),
        'protected_profile_update_documents_followup_failed',
    )
    profile_documents_message = str(profile_documents_payload.get('message_text', ''))
    assert_condition('situacao documental' in profile_documents_message.lower(), 'protected_profile_update_documents_heading_missing')
    assert_condition('documentacao administrativa' in profile_documents_message.lower(), 'protected_profile_update_documents_detail_missing')
    print('[ok] protected profile update documents follow-up')

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
        chat_id=1649845499,
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
