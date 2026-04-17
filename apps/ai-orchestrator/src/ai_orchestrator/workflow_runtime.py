from __future__ import annotations

# ruff: noqa: F401,F403,F405
"""Workflow orchestration helpers extracted from runtime.py."""

from . import runtime_core as _runtime_core
from .analysis_context_runtime import (
    _extract_protocol_code_hint,
    _looks_like_workflow_resume_follow_up,
)
from .conversation_focus_runtime import (
    _recent_conversation_focus,
    _recent_focus_is_fresh,
    _recent_message_lines,
    _recent_tool_call_entries,
    _recent_trace_focus,
    _recent_workflow_focus,
)
from .public_feature_runtime import _feature_suggestion_replies
from .public_service_routing_runtime import (
    _routing_follow_up_context_message,
    _service_matches_from_message,
)


def _intent_analysis_impl(name: str):
    from . import intent_analysis_runtime as _intent_analysis_runtime

    return getattr(_intent_analysis_runtime, name)


def _contains_any(message: str, terms: set[str] | tuple[str, ...]) -> bool:
    return _intent_analysis_impl('_contains_any')(message, terms)


def _message_matches_term(message: str, term: str) -> bool:
    return _intent_analysis_impl('_message_matches_term')(message, term)


def _normalize_text(message: str | None) -> str:
    return _intent_analysis_impl('_normalize_text')(message)


def _extract_requested_date(message: str):
    from .public_orchestration_runtime import _extract_requested_date as _impl

    return _impl(message)


def _extract_requested_window(message: str):
    from .public_orchestration_runtime import _extract_requested_window as _impl

    return _impl(message)


def _export_runtime_core_namespace() -> None:
    for name, value in vars(_runtime_core).items():
        if name.startswith('__'):
            continue
        globals()[name] = value


_export_runtime_core_namespace()


def _public_act_rules_impl(name: str):
    from . import public_act_rules_runtime as _public_act_rules_runtime

    return getattr(_public_act_rules_runtime, name)


def _is_assistant_identity_query(message: str) -> bool:
    return _public_act_rules_impl('_is_assistant_identity_query')(message)


def _is_auth_guidance_query(message: str) -> bool:
    return _public_act_rules_impl('_is_auth_guidance_query')(message)


def _is_capability_query(message: str) -> bool:
    return _public_act_rules_impl('_is_capability_query')(message)


def _is_follow_up_query(message: str) -> bool:
    return _public_act_rules_impl('_is_follow_up_query')(message)


def _is_greeting_only(message: str) -> bool:
    return _public_act_rules_impl('_is_greeting_only')(message)


def _is_public_feature_query(message: str) -> bool:
    return _public_act_rules_impl('_is_public_feature_query')(message)


def _is_public_pricing_navigation_query(message: str) -> bool:
    return _public_act_rules_impl('_is_public_pricing_navigation_query')(message)


def _is_service_routing_query(message: str) -> bool:
    return _public_act_rules_impl('_is_service_routing_query')(message)


def _requested_public_features(message: str) -> tuple[str, ...]:
    return _public_act_rules_impl('_requested_public_features')(message)


def _detect_visit_booking_action(message: str) -> str | None:
    normalized = _normalize_text(message)
    if any(_message_matches_term(normalized, term) for term in VISIT_CANCEL_TERMS):
        return 'cancel'
    if any(_message_matches_term(normalized, term) for term in VISIT_RESCHEDULE_TERMS):
        return 'reschedule'
    if any(
        _message_matches_term(normalized, phrase)
        for phrase in {'se eu precisar remarcar', 'e se eu precisar remarcar'}
    ):
        return 'reschedule'
    visit_targets = {'visita', 'visita guiada', 'tour'}
    if _contains_any(normalized, {'cancelar', 'desmarcar'}) and _contains_any(
        normalized, visit_targets
    ):
        return 'cancel'
    if _contains_any(normalized, {'remarcar', 'reagendar', 'mudar', 'trocar'}) and _contains_any(
        normalized,
        visit_targets,
    ):
        return 'reschedule'
    return None


def _detect_institutional_request_action(message: str) -> str | None:
    normalized = _normalize_text(message)
    if any(_message_matches_term(normalized, term) for term in INSTITUTIONAL_REQUEST_UPDATE_TERMS):
        return 'append_note'
    if any(
        _message_matches_term(normalized, phrase)
        for phrase in {
            'complementa dizendo que',
            'complementar dizendo que',
            'adiciona dizendo que',
            'acrescenta dizendo que',
        }
    ):
        return 'append_note'
    if _contains_any(
        normalized, {'complementar', 'completar', 'acrescentar', 'adicionar', 'incluir'}
    ) and _contains_any(
        normalized,
        {'pedido', 'solicitacao', 'solicitação', 'protocolo', 'requerimento'},
    ):
        return 'append_note'
    return None


def _extract_institutional_request_update_details(message: str) -> str:
    compact = ' '.join(message.split()).strip()
    patterns = (
        r'^(?:quero\s+)?(?:complementar|completar|acrescentar|adicionar|incluir)\s+(?:ao?\s+)?(?:meu\s+)?(?:pedido|protocolo|requerimento|solicitacao|solicitação)\s*(?:dizendo\s+que|informando\s+que|com|sobre)?\s*',
        r'^(?:complemente|acrescente|adicione)\s+(?:ao?\s+)?(?:meu\s+)?(?:pedido|protocolo|requerimento|solicitacao|solicitação)\s*(?:com|sobre)?\s*',
        r'^(?:complementa|complementar|adiciona|acrescenta)\s+dizendo\s+que\s*',
    )
    details = compact
    for pattern in patterns:
        details = re.sub(pattern, '', details, flags=re.IGNORECASE).strip(' .:-')
    return details or compact


def _detect_institutional_request_target_area(message: str) -> str:
    normalized = _normalize_text(message)
    for term, area in (
        ('direcao', 'direcao'),
        ('direção', 'direcao'),
        ('diretora', 'direcao'),
        ('diretor', 'direcao'),
        ('ouvidoria', 'ouvidoria'),
        ('coordenacao', 'coordenacao'),
        ('coordenação', 'coordenacao'),
        ('financeiro', 'financeiro'),
        ('secretaria', 'secretaria'),
    ):
        if _message_matches_term(normalized, term):
            return area
    return 'direcao'


def _detect_institutional_request_category(message: str) -> str:
    normalized = _normalize_text(message)
    for term, category in (
        ('bolsa', 'bolsas'),
        ('desconto', 'descontos'),
        ('reclamacao', 'manifestacao'),
        ('reclamação', 'manifestacao'),
        ('sugestao', 'sugestao'),
        ('sugestão', 'sugestao'),
        ('elogio', 'elogio'),
        ('ocorrencia', 'ocorrencia'),
        ('ocorrência', 'ocorrencia'),
    ):
        if _message_matches_term(normalized, term):
            return category
    return 'solicitacao_geral'


def _build_institutional_request_subject(message: str) -> str:
    compact = ' '.join(message.split())
    if len(compact) <= 140:
        return compact
    return f'{compact[:137].rstrip()}...'


async def _create_visit_booking(
    *,
    settings: Any,
    request: MessageResponseRequest,
    actor: dict[str, Any] | None,
) -> dict[str, Any] | None:
    conversation_external_id = request.conversation_id or _effective_conversation_id(request)
    if not conversation_external_id:
        return None
    preferred_date = _extract_requested_date(request.message)
    preferred_window = _extract_requested_window(request.message)
    payload = {
        'conversation_external_id': conversation_external_id,
        'channel': request.channel.value,
        'telegram_chat_id': request.telegram_chat_id,
        'audience_name': str(actor.get('full_name'))
        if isinstance(actor, dict) and actor.get('full_name')
        else None,
        'audience_contact': None,
        'interested_segment': _select_public_segment(request.message),
        'preferred_date': preferred_date.isoformat() if preferred_date else None,
        'preferred_window': preferred_window,
        'attendee_count': 1,
        'notes': request.message,
    }
    response_payload, status_code = await _api_core_post(
        settings=settings,
        path='/v1/internal/workflows/visit-bookings',
        payload=payload,
    )
    if status_code != 200 or response_payload is None:
        return None
    return response_payload


async def _update_visit_booking(
    *,
    settings: Any,
    request: MessageResponseRequest,
    conversation_context: dict[str, Any] | None,
) -> dict[str, Any] | None:
    conversation_external_id = request.conversation_id or _effective_conversation_id(request)
    if not conversation_external_id:
        return None
    action = _detect_visit_booking_action(request.message)
    if action is None:
        recent_focus = _recent_workflow_focus(conversation_context) or _recent_trace_focus(
            conversation_context
        )
        if (
            recent_focus
            and recent_focus.get('kind') == 'visit'
            and _looks_like_visit_update_follow_up(request.message)
        ):
            normalized = _normalize_text(request.message)
            if any(
                _message_matches_term(normalized, term)
                for term in {'cancelar', 'cancela', 'cancelamento', 'desmarcar', 'desmarca'}
            ):
                action = 'cancel'
            else:
                action = 'reschedule'
    if action is None:
        return None
    preferred_date = _extract_requested_date(request.message)
    preferred_window = _extract_requested_window(request.message)
    protocol_code = _extract_protocol_code_hint(request.message, conversation_context)
    if not protocol_code:
        recent_snapshot = _workflow_snapshot_from_context(
            conversation_context,
            workflow_kind_hint='visit_booking',
            protocol_code_hint=None,
        )
        if isinstance(recent_snapshot, dict):
            item = recent_snapshot.get('item')
            if isinstance(item, dict):
                protocol_code = str(item.get('protocol_code', '') or '').strip() or None
    payload = {
        'conversation_external_id': conversation_external_id,
        'channel': request.channel.value,
        'telegram_chat_id': request.telegram_chat_id,
        'protocol_code': protocol_code,
        'action': action,
        'preferred_date': preferred_date.isoformat() if preferred_date else None,
        'preferred_window': preferred_window,
        'notes': request.message,
    }
    response_payload, status_code = await _api_core_post(
        settings=settings,
        path='/v1/internal/workflows/visit-bookings/actions',
        payload=payload,
    )
    if status_code != 200 or response_payload is None:
        return None
    return response_payload


async def _create_institutional_request(
    *,
    settings: Any,
    request: MessageResponseRequest,
    actor: dict[str, Any] | None,
) -> dict[str, Any] | None:
    conversation_external_id = request.conversation_id or _effective_conversation_id(request)
    if not conversation_external_id:
        return None
    payload = {
        'conversation_external_id': conversation_external_id,
        'channel': request.channel.value,
        'telegram_chat_id': request.telegram_chat_id,
        'target_area': _detect_institutional_request_target_area(request.message),
        'category': _detect_institutional_request_category(request.message),
        'subject': _build_institutional_request_subject(request.message),
        'details': request.message,
        'requester_contact': None,
    }
    response_payload, status_code = await _api_core_post(
        settings=settings,
        path='/v1/internal/workflows/institutional-requests',
        payload=payload,
    )
    if status_code != 200 or response_payload is None:
        return None
    return response_payload


async def _update_institutional_request(
    *,
    settings: Any,
    request: MessageResponseRequest,
    conversation_context: dict[str, Any] | None,
) -> dict[str, Any] | None:
    conversation_external_id = request.conversation_id or _effective_conversation_id(request)
    if not conversation_external_id:
        return None
    action = _detect_institutional_request_action(request.message)
    if action is None:
        return None
    protocol_code = _extract_protocol_code_hint(request.message, conversation_context)
    if not protocol_code:
        recent_snapshot = _workflow_snapshot_from_context(
            conversation_context,
            workflow_kind_hint='institutional_request',
            protocol_code_hint=None,
        )
        if isinstance(recent_snapshot, dict):
            item = recent_snapshot.get('item')
            if isinstance(item, dict):
                protocol_code = str(item.get('protocol_code', '') or '').strip() or None
    payload = {
        'conversation_external_id': conversation_external_id,
        'channel': request.channel.value,
        'telegram_chat_id': request.telegram_chat_id,
        'protocol_code': protocol_code,
        'action': action,
        'details': _extract_institutional_request_update_details(request.message),
    }
    response_payload, status_code = await _api_core_post(
        settings=settings,
        path='/v1/internal/workflows/institutional-requests/actions',
        payload=payload,
    )
    if status_code != 200 or response_payload is None:
        return None
    return response_payload


def _compose_visit_booking_answer(
    response_payload: dict[str, Any] | None, school_profile: dict[str, Any] | None
) -> str:
    school_name = str((school_profile or {}).get('school_name', 'Colegio Horizonte'))
    if not response_payload:
        return _render_structured_answer_frame(
            StructuredAnswerFrame(
                lead=f'Posso orientar sobre visitas ao {school_name}, mas nao consegui registrar o pedido agora',
                offer='Tente novamente em instantes ou use o canal de admissions',
            )
        )
    item = response_payload.get('item')
    if not isinstance(item, dict):
        return _render_structured_answer_frame(
            StructuredAnswerFrame(
                lead=f'Registrei a intencao de visita ao {school_name}, mas nao consegui recuperar o protocolo agora',
                offer='Use admissions para confirmar o agendamento',
            )
        )
    preferred_date = item.get('preferred_date')
    preferred_window = item.get('preferred_window')
    slot_parts = []
    if preferred_date:
        slot_parts.append(str(preferred_date))
    if preferred_window:
        slot_parts.append(str(preferred_window))
    slot = ' - '.join(slot_parts) if slot_parts else 'janela a confirmar'
    return _render_structured_answer_frame(
        StructuredAnswerFrame(
            lead=f'Pedido de visita registrado para o {school_name}',
            facts=(
                f'Protocolo: {item.get("protocol_code", "indisponivel")}',
                f'Preferencia informada: {slot}',
                f'Fila responsavel: {item.get("queue_name", "admissoes")}',
                f'Ticket operacional: {item.get("linked_ticket_code", "a confirmar")}',
            ),
            next_step='A equipe comercial valida a janela e retorna com a confirmacao',
        )
    )


def _compose_visit_booking_action_answer(
    response_payload: dict[str, Any] | None, *, request_message: str
) -> str:
    action = _detect_visit_booking_action(request_message)
    if action is None and isinstance(response_payload, dict):
        payload_action = str(response_payload.get('action', '') or '').strip().lower()
        if payload_action in {'cancel', 'reschedule'}:
            action = payload_action
    preferred_date = _extract_requested_date(request_message)
    preferred_window = _extract_requested_window(request_message)

    if action == 'reschedule' and preferred_date is None and not preferred_window:
        facts: list[str] = []
        if isinstance(response_payload, dict):
            item = response_payload.get('item')
            if isinstance(item, dict):
                protocol_code = str(item.get('protocol_code', '') or '').strip()
                linked_ticket_code = str(item.get('linked_ticket_code', '') or '').strip()
                if protocol_code:
                    facts.append(f'Protocolo: {protocol_code}')
                if linked_ticket_code:
                    facts.append(f'Ticket operacional: {linked_ticket_code}')
        return _render_structured_answer_frame(
            StructuredAnswerFrame(
                lead='Consigo remarcar a visita por aqui',
                facts=tuple(facts),
                offer='Me diga pelo menos o novo dia ou a janela desejada, por exemplo: "remarque para sexta de manha" ou "troque para 28/03 as 10h"',
            )
        )

    if not response_payload or not isinstance(response_payload, dict):
        return _render_structured_answer_frame(
            StructuredAnswerFrame(
                lead='Nao consegui atualizar a visita agora',
                offer='Se quiser, me passe novamente o protocolo da visita ou o novo horario desejado',
            )
        )

    item = response_payload.get('item')
    if not isinstance(item, dict):
        return 'Localizei a visita, mas nao consegui montar a atualizacao agora.'

    if action is None:
        item_status = str(item.get('status', '') or '').strip().lower()
        if item_status == 'cancelled':
            action = 'cancel'

    protocol_code = str(item.get('protocol_code', 'indisponivel'))
    queue_name = _humanize_workflow_queue(item.get('queue_name'))
    linked_ticket_code = str(item.get('linked_ticket_code', '') or '').strip()
    slot_label = str(item.get('slot_label', '') or '').strip()
    display_slot_label = slot_label
    if preferred_date is not None or preferred_window:
        weekday_label = _weekday_label_for_date(preferred_date)
        if weekday_label and preferred_window:
            display_slot_label = f'{weekday_label} - {preferred_window}'
            if slot_label:
                display_slot_label += f' ({slot_label})'
        elif weekday_label:
            display_slot_label = (
                weekday_label if not slot_label else f'{weekday_label} ({slot_label})'
            )
        elif preferred_window and not slot_label:
            display_slot_label = preferred_window

    if action == 'cancel':
        facts = [f'Protocolo: {protocol_code}']
        if linked_ticket_code:
            facts.append(f'Ticket operacional: {linked_ticket_code}')
        return _render_structured_answer_frame(
            StructuredAnswerFrame(
                lead=f'Visita cancelada no fluxo de {queue_name}',
                facts=tuple(facts),
                offer='Se quiser, eu tambem posso registrar um novo pedido de visita quando voce preferir',
            )
        )

    facts = [f'Protocolo: {protocol_code}']
    if linked_ticket_code:
        facts.append(f'Ticket operacional: {linked_ticket_code}')
    if display_slot_label:
        facts.append(f'Nova preferencia: {display_slot_label}')
    return _render_structured_answer_frame(
        StructuredAnswerFrame(
            lead=f'Pedido de visita atualizado com a fila de {queue_name}',
            facts=tuple(facts),
            next_step='Admissions valida a nova janela e retorna com a confirmacao',
        )
    )


def _compose_institutional_request_answer(response_payload: dict[str, Any] | None) -> str:
    if not response_payload:
        return _render_structured_answer_frame(
            StructuredAnswerFrame(
                lead='Posso orientar sobre protocolos institucionais, mas nao consegui registrar a solicitacao agora',
                offer='Tente novamente em instantes ou use a secretaria',
            )
        )
    item = response_payload.get('item')
    if not isinstance(item, dict):
        return _render_structured_answer_frame(
            StructuredAnswerFrame(
                lead='Registrei a manifestacao institucional, mas nao consegui recuperar o protocolo neste momento',
                offer='Use a secretaria ou a ouvidoria para confirmar',
            )
        )
    return _render_structured_answer_frame(
        StructuredAnswerFrame(
            lead=f'Solicitacao institucional registrada para {item.get("target_area", "o setor responsavel")}',
            facts=(
                f'Protocolo: {item.get("protocol_code", "indisponivel")}',
                f'Assunto: {item.get("subject", "solicitacao institucional")}',
                f'Fila responsavel: {item.get("queue_name", "atendimento")}',
                f'Ticket operacional: {item.get("linked_ticket_code", "a confirmar")}',
            ),
            next_step='A equipe faz a triagem inicial e segue o retorno pelo fluxo institucional',
        )
    )


def _compose_institutional_request_action_answer(
    response_payload: dict[str, Any] | None,
    *,
    request_message: str,
) -> str:
    detail_text = _extract_institutional_request_update_details(request_message)
    if not detail_text:
        return _render_structured_answer_frame(
            StructuredAnswerFrame(
                lead='Consigo complementar essa solicitacao por aqui',
                offer='Me diga o que precisa ser acrescentado ao protocolo e eu atualizo o pedido',
            )
        )

    if not response_payload or not isinstance(response_payload, dict):
        return _render_structured_answer_frame(
            StructuredAnswerFrame(
                lead='Nao consegui complementar a solicitacao agora',
                offer='Se quiser, me passe novamente o protocolo ou reescreva o complemento em uma frase curta',
            )
        )

    item = response_payload.get('item')
    if not isinstance(item, dict):
        return 'Localizei a solicitacao, mas nao consegui registrar o complemento agora.'

    protocol_code = str(item.get('protocol_code', 'indisponivel'))
    queue_name = _humanize_workflow_queue(item.get('queue_name'))
    linked_ticket_code = str(item.get('linked_ticket_code', '') or '').strip()
    facts = [f'Protocolo: {protocol_code}']
    if linked_ticket_code:
        facts.append(f'Ticket operacional: {linked_ticket_code}')
    facts.append(f'Novo complemento: {detail_text}')
    return _render_structured_answer_frame(
        StructuredAnswerFrame(
            lead=f'Complemento registrado na fila de {queue_name}',
            facts=tuple(facts),
            next_step='A equipe responsavel recebe essa atualizacao no mesmo fluxo do pedido',
        )
    )


def _humanize_workflow_status(status: str) -> str:
    normalized = str(status or '').strip().lower()
    return WORKFLOW_STATUS_LABELS.get(normalized, normalized or 'em analise')


def _humanize_workflow_queue(queue_name: str | None) -> str:
    normalized = str(queue_name or '').strip().lower()
    return WORKFLOW_QUEUE_LABELS.get(normalized, normalized or 'atendimento')


def _format_workflow_timestamp(value: Any) -> str | None:
    if isinstance(value, str):
        raw = value.strip()
        if not raw:
            return None
        try:
            value = datetime.fromisoformat(raw.replace('Z', '+00:00'))
        except ValueError:
            return None
    if not isinstance(value, datetime):
        return None
    reference = datetime.now(tz=value.tzinfo) if value.tzinfo else datetime.now()
    current_date = reference.date()
    target_date = value.date()
    time_label = value.strftime('%H:%M')
    if target_date == current_date:
        return f'hoje as {time_label}'
    if target_date == current_date - timedelta(days=1):
        return f'ontem as {time_label}'
    return value.strftime('%d/%m/%Y as %H:%M')


def _frame_sentence(text: str | None) -> str | None:
    normalized = str(text or '').strip()
    if not normalized:
        return None
    if normalized[-1] not in '.!?':
        normalized = f'{normalized}.'
    return normalized


def _render_structured_answer_frame(frame: StructuredAnswerFrame) -> str:
    parts: list[str] = []
    lead = _frame_sentence(frame.lead)
    if lead:
        parts.append(lead)
    for fact in frame.facts:
        sentence = _frame_sentence(fact)
        if sentence:
            parts.append(sentence)
    next_step = _frame_sentence(frame.next_step)
    if next_step:
        parts.append(next_step)
    offer = _frame_sentence(frame.offer)
    if offer:
        parts.append(offer)
    return ' '.join(parts).strip()


def _render_structured_answer_lines(lines: list[str]) -> str:
    if not lines:
        return ''
    lead = str(lines[0] or '').strip()
    if lead.startswith('- '):
        lead = lead[2:].strip()
    facts: list[str] = []
    next_step: str | None = None
    offer: str | None = None
    for raw in lines[1:]:
        text = str(raw or '').strip()
        if not text:
            continue
        if text.startswith('- '):
            text = text[2:].strip()
        normalized = _normalize_text(text)
        if normalized.startswith('proximo passo:'):
            next_step = text
        elif normalized.startswith('se quiser'):
            offer = text if offer is None else f'{offer} {text}'
        else:
            facts.append(text)
    return _render_structured_answer_frame(
        StructuredAnswerFrame(
            lead=lead,
            facts=tuple(facts),
            next_step=next_step,
            offer=offer,
        )
    )


def _compose_orphan_workflow_follow_up_answer(
    message: str,
    conversation_context: dict[str, Any] | None,
) -> str | None:
    if _recent_conversation_focus(conversation_context):
        return None
    normalized = _normalize_text(message)
    asks_summary = any(
        _message_matches_term(normalized, term)
        for term in {
            'resume pra mim',
            'resuma pra mim',
            'faz um resumo',
            'me da um resumo',
            'me dê um resumo',
        }
    )
    asks_status = any(
        _message_matches_term(normalized, term)
        for term in {
            'esse atendimento',
            'esse pedido',
            'essa fila',
            'esse protocolo',
            'como esta esse atendimento',
            'como está esse atendimento',
            'status',
            'fila',
            'protocolo',
        }
    )
    if asks_summary:
        return (
            'Se voce quer um resumo do atendimento, me passe o protocolo ou relembre se o assunto era visita, direcao, financeiro ou secretaria. '
            'Com isso, eu te devolvo o resumo e o protocolo corretos.'
        )
    if asks_status:
        return (
            'Se voce quer consultar status ou fila de um atendimento, me passe o codigo que comeca com VIS, REQ ou ATD, '
            'ou me relembre qual era o assunto para eu localizar o protocolo correto.'
        )
    return None


def _workflow_snapshot_from_context(
    conversation_context: dict[str, Any] | None,
    *,
    workflow_kind_hint: str | None,
    protocol_code_hint: str | None,
) -> dict[str, Any] | None:
    focus = _recent_trace_focus(conversation_context) or _recent_conversation_focus(
        conversation_context
    )
    if not isinstance(focus, dict):
        return None
    focus_kind = str(focus.get('kind', '') or '').strip()
    active_task = str(focus.get('active_task', '') or '').strip()
    if not _recent_focus_is_fresh(
        conversation_context, focus_kind=focus_kind, active_task=active_task
    ):
        return None

    expected_workflow_types: set[str] = set()
    if workflow_kind_hint:
        expected_workflow_types.add(str(workflow_kind_hint).strip())
    elif focus_kind == 'visit':
        expected_workflow_types.add('visit_booking')
    elif focus_kind == 'request':
        expected_workflow_types.add('institutional_request')
    elif focus_kind == 'support':
        expected_workflow_types.add('support_handoff')

    for item in reversed(_recent_tool_call_entries(conversation_context)):
        tool_name = str(item.get('tool_name', '') or '').strip()
        if tool_name not in {
            'get_workflow_status',
            'schedule_school_visit',
            'update_visit_booking',
            'create_institutional_request',
            'update_institutional_request',
            'create_support_ticket',
            'handoff_to_human',
        }:
            continue
        response_payload = item.get('response_payload')
        if not isinstance(response_payload, dict):
            continue
        snapshot = response_payload.get('item')
        if not isinstance(snapshot, dict):
            continue
        normalized_snapshot = dict(snapshot)
        if tool_name in {'schedule_school_visit', 'update_visit_booking'}:
            normalized_snapshot.setdefault('workflow_type', 'visit_booking')
        elif tool_name in {'create_institutional_request', 'update_institutional_request'}:
            normalized_snapshot.setdefault('workflow_type', 'institutional_request')
        elif tool_name in {'create_support_ticket', 'handoff_to_human'}:
            normalized_snapshot.setdefault('workflow_type', 'support_handoff')
            if not normalized_snapshot.get('protocol_code') and normalized_snapshot.get(
                'ticket_code'
            ):
                normalized_snapshot['protocol_code'] = normalized_snapshot.get('ticket_code')
            if not normalized_snapshot.get('linked_ticket_code') and normalized_snapshot.get(
                'ticket_code'
            ):
                normalized_snapshot['linked_ticket_code'] = normalized_snapshot.get('ticket_code')
        workflow_type = str(normalized_snapshot.get('workflow_type', '') or '').strip()
        if expected_workflow_types and workflow_type not in expected_workflow_types:
            continue
        snapshot_protocol = str(normalized_snapshot.get('protocol_code', '') or '').strip()
        if (
            protocol_code_hint
            and snapshot_protocol
            and snapshot_protocol.upper() != str(protocol_code_hint).strip().upper()
        ):
            continue
        return {'found': True, 'item': normalized_snapshot}
    return None


def _compose_workflow_status_answer(
    response_payload: dict[str, Any] | None,
    *,
    protocol_code_hint: str | None,
    request_message: str,
) -> str:
    normalized_request = _normalize_text(request_message)
    asks_status_explicitly = any(
        _message_matches_term(normalized_request, term)
        for term in {
            'qual o status',
            'status',
            'andamento',
            'situacao',
            'fila',
            'como esta esse atendimento',
            'como está esse atendimento',
            'qual o prazo',
            'quando me respondem',
            'quem vai me responder',
        }
    )
    asks_update_explicitly = any(
        _message_matches_term(normalized_request, term)
        for term in {
            'tem alguma atualizacao',
            'tem alguma atualização',
            'alguma atualizacao',
            'alguma atualização',
            'ultima atualizacao',
            'ultima atualização',
            'teve atualizacao',
            'teve atualização',
        }
    )
    asks_next_step = any(
        _message_matches_term(normalized_request, term)
        for term in {
            'qual o proximo passo',
            'qual o próximo passo',
            'proximo passo',
            'próximo passo',
            'e agora',
            'o que acontece agora',
        }
    )
    asks_protocol_only = not asks_status_explicitly and any(
        _message_matches_term(normalized_request, term)
        for term in {
            'qual o protocolo',
            'me passa o protocolo',
            'meu protocolo',
            'numero do protocolo',
            'protocolo',
        }
    )
    asks_summary = any(
        _message_matches_term(normalized_request, term)
        for term in {
            'resume meu pedido',
            'resuma meu pedido',
            'faz um resumo do meu pedido',
            'faz um resumo',
            'o que eu pedi',
            'qual foi meu pedido',
            'resume pra mim',
            'resuma pra mim',
        }
    )
    asks_resume = _looks_like_workflow_resume_follow_up(request_message)

    if not isinstance(response_payload, dict) or not response_payload.get('found'):
        if protocol_code_hint:
            return (
                f'Ainda nao localizei um protocolo ativo com o codigo {protocol_code_hint}. '
                'Se quiser, me encaminhe novamente o codigo completo ou me diga se o assunto era visita, direcao, financeiro ou secretaria.'
            )
        if asks_resume:
            return (
                'Ainda nao encontrei um protocolo recente nesta conversa para retomar esse fluxo. '
                'Se quiser, me diga se o assunto era visita, direcao, financeiro ou secretaria, ou me passe o codigo que comeca com VIS, REQ ou ATD.'
            )
        if asks_summary:
            return (
                'Ainda nao encontrei um protocolo recente nesta conversa para montar o resumo do pedido. '
                'Se quiser, me diga o codigo que comeca com VIS, REQ ou ATD, ou me lembre se o assunto era visita, direcao, financeiro ou secretaria.'
            )
        if asks_status_explicitly or asks_update_explicitly or asks_next_step:
            return (
                'Ainda nao encontrei um protocolo recente nesta conversa para consultar o status da fila. '
                'Se quiser, me diga o codigo que comeca com VIS, REQ ou ATD, ou me lembre se o assunto era visita, direcao, financeiro ou secretaria.'
            )
        return (
            'Ainda nao encontrei um protocolo recente nesta conversa. '
            'Se quiser, me diga o codigo que comeca com VIS, REQ ou ATD, ou me lembre se o assunto era visita, direcao, financeiro ou secretaria.'
        )

    item = response_payload.get('item')
    if not isinstance(item, dict):
        return 'Localizei um protocolo desta conversa, mas nao consegui interpretar o status agora.'

    workflow_type = str(item.get('workflow_type', 'support_handoff'))
    status_label = _humanize_workflow_status(str(item.get('status', '')))
    queue_label = _humanize_workflow_queue(item.get('queue_name'))
    protocol_code = str(item.get('protocol_code', protocol_code_hint or 'indisponivel'))
    linked_ticket_code = str(item.get('linked_ticket_code', '') or '').strip()
    subject = str(item.get('subject', '') or '').strip()
    summary_text = str(item.get('summary', '') or '').strip()
    target_area = str(item.get('target_area', '') or '').strip()
    preferred_date = str(item.get('preferred_date', '') or '').strip()
    preferred_window = str(item.get('preferred_window', '') or '').strip()
    slot_label = str(item.get('slot_label', '') or '').strip()
    updated_at_label = _format_workflow_timestamp(item.get('updated_at'))
    if workflow_type == 'visit_booking':
        if asks_resume:
            lines = [
                'Para retomar a visita, volte por este mesmo canal institucional ou pela secretaria/admissions e eu abro o proximo passo com voce.',
                f'- Ultimo protocolo conhecido: {protocol_code}',
            ]
            if linked_ticket_code:
                lines.append(f'- Ticket operacional anterior: {linked_ticket_code}')
            if slot_label:
                lines.append(f'- Preferencia registrada antes da pausa: {slot_label}')
            elif preferred_date or preferred_window:
                preference = ' - '.join(part for part in [preferred_date, preferred_window] if part)
                lines.append(f'- Preferencia registrada antes da pausa: {preference}')
            lines.append(
                'Se preferir, ja me diga o novo dia e horario desejados para eu abrir outro pedido de visita.'
            )
            return '\n'.join(lines)
        if asks_protocol_only:
            lines = [f'O protocolo da sua visita e {protocol_code}.']
            if linked_ticket_code:
                lines.append(f'- Ticket operacional: {linked_ticket_code}')
            if slot_label:
                lines.append(f'- Preferencia registrada: {slot_label}')
            lines.append(
                'Se quiser, eu tambem posso te dizer o status, remarcar ou cancelar a visita.'
            )
            return _render_structured_answer_lines(lines)
        if asks_summary:
            lines = ['Resumo do seu pedido de visita:']
            if slot_label:
                lines.append(f'- Preferencia registrada: {slot_label}')
            elif preferred_date or preferred_window:
                preference = ' - '.join(part for part in [preferred_date, preferred_window] if part)
                lines.append(f'- Preferencia registrada: {preference}')
            lines.append(f'- Protocolo: {protocol_code}')
            if linked_ticket_code:
                lines.append(f'- Ticket operacional: {linked_ticket_code}')
            lines.append(f'- Status atual: {status_label}')
            lines.append(
                'Se quiser, eu posso remarcar, cancelar ou acompanhar esse pedido com voce.'
            )
            return '\n'.join(lines)
        if asks_update_explicitly:
            lines = [
                f'A ultima atualizacao da sua visita mostra que ela segue {status_label}.',
                f'- Protocolo: {protocol_code}',
            ]
            if updated_at_label:
                lines.append(f'- Ultima movimentacao registrada: {updated_at_label}')
            if linked_ticket_code:
                lines.append(f'- Ticket operacional: {linked_ticket_code}')
            if slot_label:
                lines.append(f'- Preferencia registrada: {slot_label}')
            lines.append(
                'No momento, a equipe comercial ainda precisa validar a janela antes da confirmacao.'
            )
            return '\n'.join(lines)
        if asks_next_step:
            lines = [
                'Proximo passo da sua visita: admissions valida a janela antes de confirmar o horario.',
                f'- Protocolo: {protocol_code}',
            ]
            if updated_at_label:
                lines.append(f'- Ultima movimentacao registrada: {updated_at_label}')
            if slot_label:
                lines.append(f'- Preferencia registrada: {slot_label}')
            lines.append('Se quiser, eu posso remarcar ou cancelar esse pedido por aqui.')
            return '\n'.join(lines)
        lines = [
            f'Seu pedido de visita segue {status_label} com a fila de {queue_label}.',
            f'- Protocolo: {protocol_code}',
        ]
        if linked_ticket_code:
            lines.append(f'- Ticket operacional: {linked_ticket_code}')
        if updated_at_label:
            lines.append(f'- Ultima movimentacao registrada: {updated_at_label}')
        if slot_label:
            lines.append(f'- Preferencia registrada: {slot_label}')
        elif preferred_date or preferred_window:
            preference = ' - '.join(part for part in [preferred_date, preferred_window] if part)
            lines.append(f'- Preferencia registrada: {preference}')
        if any(
            _message_matches_term(normalized_request, term)
            for term in {
                'qual o prazo',
                'quanto tempo demora',
                'quando me respondem',
                'quando vao me responder',
                'quando vão me responder',
            }
        ):
            lines.append(
                'Prazo esperado: admissions costuma validar a janela e retornar em ate 1 dia util.'
            )
        elif any(
            _message_matches_term(normalized_request, term)
            for term in {'quem vai me responder', 'quem vai retornar', 'quem fica com isso'}
        ):
            lines.append(
                'Quem responde: a equipe comercial de admissions devolve a confirmacao por este fluxo.'
            )
        else:
            lines.append(
                'Proximo passo: a equipe comercial valida a janela e retorna com a confirmacao.'
            )
        return _render_structured_answer_lines(lines)

    if workflow_type == 'institutional_request':
        if asks_protocol_only:
            lines = [f'O protocolo da sua solicitacao e {protocol_code}.']
            if linked_ticket_code:
                lines.append(f'- Ticket operacional: {linked_ticket_code}')
            if target_area:
                lines.append(f'- Area responsavel: {target_area}')
            lines.append('Se quiser, eu tambem posso resumir o pedido ou verificar o status atual.')
            return _render_structured_answer_lines(lines)
        if asks_summary:
            lines = ['Resumo da sua solicitacao institucional:']
            if subject:
                lines.append(f'- Assunto: {subject}')
            if target_area:
                lines.append(f'- Area responsavel: {target_area}')
            if summary_text:
                lines.append(f'- Detalhes registrados: {summary_text}')
            lines.append(f'- Protocolo: {protocol_code}')
            if linked_ticket_code:
                lines.append(f'- Ticket operacional: {linked_ticket_code}')
            lines.append(f'- Status atual: {status_label}')
            lines.append(
                'Se quiser, eu tambem posso te dizer o prazo estimado ou quem responde por essa fila.'
            )
            return _render_structured_answer_lines(lines)
        if asks_update_explicitly:
            lines = [
                f'A ultima atualizacao do seu protocolo mostra que ele segue {status_label}.',
                f'- Protocolo: {protocol_code}',
            ]
            if updated_at_label:
                lines.append(f'- Ultima movimentacao registrada: {updated_at_label}')
            if target_area:
                lines.append(f'- Area responsavel: {target_area}')
            if linked_ticket_code:
                lines.append(f'- Ticket operacional: {linked_ticket_code}')
            lines.append(
                f'No momento, a fila de {queue_label} ainda precisa analisar o contexto antes do retorno.'
            )
            return _render_structured_answer_lines(lines)
        if asks_next_step:
            lines = [
                f'Proximo passo do seu protocolo: a fila de {queue_label} analisa o contexto e prepara o retorno.',
                f'- Protocolo: {protocol_code}',
            ]
            if updated_at_label:
                lines.append(f'- Ultima movimentacao registrada: {updated_at_label}')
            if target_area:
                lines.append(f'- Area responsavel: {target_area}')
            lines.append('Se quiser, eu tambem posso resumir o pedido ou registrar um complemento.')
            return _render_structured_answer_lines(lines)
        lines = [
            f'Sua solicitacao institucional segue {status_label} na fila de {queue_label}.',
            f'- Protocolo: {protocol_code}',
        ]
        if subject:
            lines.append(f'- Assunto: {subject}')
        if target_area:
            lines.append(f'- Area responsavel: {target_area}')
        if linked_ticket_code:
            lines.append(f'- Ticket operacional: {linked_ticket_code}')
        if updated_at_label:
            lines.append(f'- Ultima movimentacao registrada: {updated_at_label}')
        if any(
            _message_matches_term(normalized_request, term)
            for term in {
                'qual o prazo',
                'quanto tempo demora',
                'quando me respondem',
                'quando vao me responder',
                'quando vão me responder',
            }
        ):
            lines.append(
                'Prazo esperado: a triagem inicial costuma acontecer em ate 2 dias uteis, conforme a fila responsavel.'
            )
        elif any(
            _message_matches_term(normalized_request, term)
            for term in {'quem vai me responder', 'quem vai retornar', 'quem fica com isso'}
        ):
            lines.append(
                f'Quem responde: a equipe da fila de {queue_label} devolve o retorno pelo fluxo institucional.'
            )
        else:
            lines.append(
                'Proximo passo: a equipe responsavel analisa o contexto e devolve o retorno pelo fluxo institucional.'
            )
        return _render_structured_answer_lines(lines)

    if asks_protocol_only:
        lines = [f'O protocolo atual do seu atendimento e {protocol_code}.']
        if linked_ticket_code and linked_ticket_code != protocol_code:
            lines.append(f'- Ticket operacional: {linked_ticket_code}')
        lines.append(
            'Se quiser, eu posso te dizer o status atual ou resumir o que ja foi registrado.'
        )
        return _render_structured_answer_lines(lines)

    if asks_summary:
        lines = ['Resumo do seu atendimento institucional:']
        if subject:
            lines.append(f'- Assunto: {subject}')
        lines.append(f'- Protocolo: {protocol_code}')
        if linked_ticket_code and linked_ticket_code != protocol_code:
            lines.append(f'- Ticket operacional: {linked_ticket_code}')
        lines.append(f'- Status atual: {status_label}')
        lines.append('Se quiser, eu tambem posso te orientar sobre o proximo passo.')
        return _render_structured_answer_lines(lines)

    lead = (
        f'Status do atendimento: ele segue {status_label} na fila de {queue_label}.'
        if asks_status_explicitly or asks_update_explicitly
        else f'Seu atendimento segue {status_label} na fila de {queue_label}.'
    )
    lines = [
        lead,
        f'- Protocolo: {protocol_code}',
    ]
    if subject:
        lines.append(f'- Resumo: {subject}')
    if linked_ticket_code and linked_ticket_code != protocol_code:
        lines.append(f'- Ticket operacional: {linked_ticket_code}')
    if any(
        _message_matches_term(normalized_request, term)
        for term in {'quem vai me responder', 'quem vai retornar', 'quem fica com isso'}
    ):
        lines.append(f'Quem responde: a equipe da fila de {queue_label} continua esse atendimento.')
    elif any(
        _message_matches_term(normalized_request, term)
        for term in {'qual o prazo', 'quanto tempo demora'}
    ):
        lines.append(
            'Prazo esperado: o retorno depende da fila atual, e eu posso te ajudar a identificar o proximo setor.'
        )
    else:
        lines.append(
            'Se quiser, eu tambem posso te orientar sobre o proximo setor ou resumir o que ja foi registrado.'
        )
    return _render_structured_answer_lines(lines)


def _dedupe_suggested_replies(
    texts: list[str], *, limit: int = 4
) -> list[MessageResponseSuggestedReply]:
    seen: set[str] = set()
    items: list[MessageResponseSuggestedReply] = []
    for text in texts:
        label = str(text or '').strip()
        if not label:
            continue
        normalized = _normalize_text(label)
        if normalized in seen:
            continue
        seen.add(normalized)
        items.append(MessageResponseSuggestedReply(text=label[:80]))
        if len(items) >= limit:
            break
    return items


def _default_public_suggested_replies() -> list[str]:
    return [
        'Mensalidade do ensino medio',
        'Horario do 9o ano',
        'Agendar visita',
        'Como vinculo minha conta?',
    ]


def _institution_suggested_replies(
    *,
    request: MessageResponseRequest,
    preview: Any,
    school_profile: dict[str, Any] | None,
    conversation_context: dict[str, Any] | None,
) -> list[str]:
    _export_runtime_core_namespace()
    normalized = _normalize_text(request.message)
    profile = school_profile or {}
    recent_focus = _recent_conversation_focus(conversation_context)
    if (
        preview.mode is OrchestrationMode.structured_tool
        and 'get_administrative_status' in preview.selected_tools
    ):
        return [
            'Falar com a secretaria',
            'Por onde envio meus documentos?',
            'Como altero meu email cadastral?',
            'Tem boleto em aberto?',
        ]
    if (
        _is_greeting_only(request.message)
        or _is_capability_query(request.message)
        or _is_auth_guidance_query(request.message)
    ):
        if recent_focus:
            kind = recent_focus.get('kind')
            if kind == 'visit':
                return [
                    'Qual o status da visita?',
                    'Quero remarcar a visita',
                    'Quero cancelar a visita',
                    'Qual o protocolo da visita?',
                ]
            if kind == 'request':
                return [
                    'Qual o status do meu protocolo?',
                    'Qual o prazo?',
                    'Quem vai me responder?',
                    'Resume meu pedido',
                ]
            if kind == 'finance':
                return [
                    'Como vinculo minha conta?',
                    'Mensalidade do ensino medio',
                    'Quero falar sobre contrato',
                    'Falar com o financeiro',
                ]
        return _default_public_suggested_replies()
    if _is_assistant_identity_query(request.message):
        if recent_focus and recent_focus.get('kind') == 'visit':
            return [
                'Qual o status da visita?',
                'Quero remarcar a visita',
                'Quero cancelar a visita',
                'Qual o protocolo da visita?',
            ]
        if recent_focus and recent_focus.get('kind') == 'request':
            return [
                'Qual o status do meu protocolo?',
                'Qual o prazo?',
                'Quem vai me responder?',
                'Resume meu pedido',
            ]
        return [
            'Quais opcoes de assuntos eu tenho aqui?',
            'Falar com a secretaria',
            'Agendar visita',
            'Como vinculo minha conta?',
        ]
    if _is_service_routing_query(request.message):
        message_for_matching = _routing_follow_up_context_message(
            request.message, conversation_context
        )
        matches = _service_matches_from_message(profile, message_for_matching)
        if matches:
            service_key = str(matches[0].get('service_key', '')).strip().lower()
            if service_key == 'financeiro_escolar':
                return [
                    'Como vinculo minha conta?',
                    'Mensalidade do ensino medio',
                    'Quero falar sobre contrato',
                    'Agendar visita',
                ]
            if service_key == 'secretaria_escolar':
                return [
                    'Quais documentos preciso para matricula?',
                    'Preciso de historico escolar',
                    'Quero falar com a secretaria',
                    'Agendar visita',
                ]
            if service_key == 'visita_institucional':
                return [
                    'Quero agendar uma visita',
                    'Qual o horario do 9o ano?',
                    'Mensalidade do ensino medio',
                    'Como vinculo minha conta?',
                ]
            if service_key == 'orientacao_educacional':
                return [
                    'Quero registrar esse caso',
                    'Como falo com a direcao?',
                    'Qual o prazo de retorno?',
                    'Quais opcoes de assuntos eu tenho aqui?',
                ]
            if service_key == 'solicitacao_direcao':
                return [
                    'Quero protocolar uma solicitacao',
                    'Qual o nome da diretora?',
                    'Qual o status do meu protocolo?',
                    'Agendar visita',
                ]
        return [
            'Falar com a secretaria',
            'Falar com o financeiro',
            'Agendar visita',
            'Como vinculo minha conta?',
        ]
    if any(_message_matches_term(normalized, term) for term in PUBLIC_LEADERSHIP_TERMS):
        return [
            'Qual o email da direcao?',
            'Quero protocolar uma solicitacao',
            'Quais opcoes de assuntos eu tenho aqui?',
            'Agendar visita',
        ]
    if any(_message_matches_term(normalized, term) for term in PUBLIC_CONTACT_TERMS):
        return [
            'Falar com a secretaria',
            'Agendar visita',
            'Mensalidade do ensino medio',
            'Como vinculo minha conta?',
        ]
    if any(_message_matches_term(normalized, term) for term in PUBLIC_KPI_TERMS):
        return [
            'Mostre um grafico da media de aprovacao',
            'Fale uma curiosidade da escola',
            'Qual o nome da diretora?',
            'Agendar visita',
        ]
    if any(_message_matches_term(normalized, term) for term in PUBLIC_HIGHLIGHT_TERMS):
        return [
            'Qual a media de aprovacao?',
            'A escola e laica ou confessional?',
            'Qual o horario do 9o ano?',
            'Agendar visita',
        ]
    if any(_message_matches_term(normalized, term) for term in PUBLIC_VISIT_TERMS):
        return [
            'Quero agendar uma visita',
            'Qual o status da visita?',
            'Qual o prazo?',
            'Quem vai me responder?',
        ]
    if _is_public_pricing_navigation_query(request.message):
        return [
            'Como vinculo minha conta?',
            'Quais bolsas a escola oferece?',
            'Agendar visita',
            'Qual o horario do 9o ano?',
        ]
    feature_keys = _requested_public_features(request.message)
    if (
        not feature_keys
        and _is_follow_up_query(request.message)
        and not _is_public_feature_query(request.message)
    ):
        feature_keys = _requested_public_features(
            _routing_follow_up_context_message(request.message, conversation_context)
        )
    if feature_keys or _is_public_feature_query(request.message):
        return _feature_suggestion_replies(feature_keys)
    if preview.mode is OrchestrationMode.hybrid_retrieval:
        if 'matricula' in normalized:
            return [
                'Qual a mensalidade do ensino medio?',
                'Quero agendar uma visita',
                'Qual o horario do 9o ano?',
                'Como vinculo minha conta?',
            ]
        return _default_public_suggested_replies()
    return _default_public_suggested_replies()
