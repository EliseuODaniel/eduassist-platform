from __future__ import annotations

# ruff: noqa: F401,F403,F405
"""Conversation memory and recent-focus helpers extracted from runtime_core.py."""

from . import runtime_core as _runtime_core


def _extract_protocol_code_from_text(text: str | None) -> str | None:
    from .analysis_context_runtime import _extract_protocol_code_from_text as _impl

    return _impl(text)


def _is_public_pricing_navigation_query(message: str) -> bool:
    from .intent_analysis_runtime import _is_public_pricing_navigation_query as _impl

    return _impl(message)


def _extract_recent_assistant_message(recent_messages: list[dict[str, Any]]) -> str | None:
    from .analysis_context_runtime import _extract_recent_assistant_message as _impl

    return _impl(recent_messages)


def _recent_messages_mention(
    conversation_context: dict[str, Any] | None,
    terms: set[str],
) -> bool:
    from .public_profile_runtime import _recent_messages_mention as _impl

    return _impl(conversation_context, terms)


def _export_runtime_core_namespace() -> None:
    for name, value in vars(_runtime_core).items():
        if name.startswith('__'):
            continue
        globals()[name] = value


_export_runtime_core_namespace()


def _normalize_text(text: str) -> str:
    normalized = unicodedata.normalize('NFKD', text)
    without_accents = ''.join(char for char in normalized if not unicodedata.combining(char))
    return without_accents.replace('º', 'o').replace('ª', 'a').lower()


def _message_matches_term(message: str, term: str) -> bool:
    from .intent_analysis_runtime import _message_matches_term as _impl

    return _impl(message, term)


def _is_greeting_only(text: str) -> bool:
    normalized = _normalize_text(text).strip()
    normalized = re.sub(r'[!?.,;:]+', '', normalized)
    normalized = ' '.join(normalized.split())
    return normalized in GREETING_ONLY_TERMS


def _recent_message_lines(conversation_context: dict[str, Any] | None) -> list[tuple[str, str]]:
    lines: list[tuple[str, str]] = []
    if not isinstance(conversation_context, dict):
        return lines
    for item in conversation_context.get('recent_messages', [])[-8:]:
        if not isinstance(item, dict):
            continue
        sender_type = str(item.get('sender_type', '')).strip().lower()
        content = str(item.get('content', '')).strip()
        if sender_type and content:
            lines.append((sender_type, content))
    return lines


def _recent_tool_call_entries(conversation_context: dict[str, Any] | None) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    if not isinstance(conversation_context, dict):
        return entries
    for item in conversation_context.get('recent_tool_calls', [])[-8:]:
        if isinstance(item, dict):
            entries.append(item)
    return entries


def _parse_recent_timestamp(value: Any) -> datetime | None:
    if isinstance(value, datetime):
        return value
    text = str(value or '').strip()
    if not text:
        return None
    normalized = text.replace('Z', '+00:00')
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=datetime.now().astimezone().tzinfo)
    return parsed


def _latest_recent_activity_at(conversation_context: dict[str, Any] | None) -> datetime | None:
    timestamps: list[datetime] = []
    if not isinstance(conversation_context, dict):
        return None
    for item in conversation_context.get('recent_messages', []):
        if not isinstance(item, dict):
            continue
        parsed = _parse_recent_timestamp(item.get('created_at'))
        if parsed is not None:
            timestamps.append(parsed)
    for item in conversation_context.get('recent_tool_calls', []):
        if not isinstance(item, dict):
            continue
        parsed = _parse_recent_timestamp(item.get('created_at'))
        if parsed is not None:
            timestamps.append(parsed)
    if not timestamps:
        return None
    return max(timestamps)


def _focus_ttl_seconds(*, focus_kind: str | None, active_task: str | None) -> int:
    normalized_focus_kind = str(focus_kind or '').strip()
    normalized_active_task = str(active_task or '').strip()
    if normalized_focus_kind in FOCUS_TTL_SECONDS_BY_KIND:
        return FOCUS_TTL_SECONDS_BY_KIND[normalized_focus_kind]
    if normalized_active_task.startswith('workflow:'):
        return FOCUS_TTL_SECONDS_BY_KIND['visit']
    if normalized_active_task.startswith(('finance:', 'academic:')):
        return FOCUS_TTL_SECONDS_BY_KIND['finance']
    if normalized_active_task.startswith('admin:'):
        return FOCUS_TTL_SECONDS_BY_KIND['secretaria']
    if normalized_active_task.startswith('public:'):
        return FOCUS_TTL_SECONDS_BY_KIND['public']
    return FOCUS_TTL_SECONDS_BY_KIND['public']


def _recent_focus_is_fresh(
    conversation_context: dict[str, Any] | None,
    *,
    focus_kind: str | None,
    active_task: str | None = None,
) -> bool:
    latest_activity = _latest_recent_activity_at(conversation_context)
    if latest_activity is None:
        return bool(
            _recent_message_lines(conversation_context)
            or _recent_tool_call_entries(conversation_context)
        )
    now = (
        datetime.now(latest_activity.tzinfo)
        if latest_activity.tzinfo is not None
        else datetime.utcnow()
    )
    age_seconds = (now - latest_activity).total_seconds()
    return age_seconds <= _focus_ttl_seconds(focus_kind=focus_kind, active_task=active_task)


def _recent_orchestration_trace_payloads(
    conversation_context: dict[str, Any] | None,
) -> list[dict[str, Any]]:
    payloads: list[dict[str, Any]] = []
    for item in reversed(_recent_tool_call_entries(conversation_context)):
        if str(item.get('tool_name', '')).strip() != 'orchestration.trace':
            continue
        request_payload = item.get('request_payload')
        if isinstance(request_payload, dict):
            payloads.append(request_payload)
    return payloads


def _recent_trace_used_tool(conversation_context: dict[str, Any] | None, tool_name: str) -> bool:
    for payload in _recent_orchestration_trace_payloads(conversation_context):
        selected_tools = payload.get('selected_tools')
        if not isinstance(selected_tools, list):
            continue
        if any(
            str(value).strip() == tool_name for value in selected_tools if isinstance(value, str)
        ):
            return True
    return False


def _recent_teacher_scope_context(conversation_context: dict[str, Any] | None) -> bool:
    if _recent_trace_used_tool(conversation_context, 'get_teacher_schedule'):
        return True
    for sender_type, content in reversed(_recent_message_lines(conversation_context)):
        if sender_type != 'user':
            continue
        if _looks_like_teacher_internal_scope_query(content):
            return True
    return False


def _recent_trace_slot_memory(conversation_context: dict[str, Any] | None) -> dict[str, Any] | None:
    for payload in _recent_orchestration_trace_payloads(conversation_context):
        slot_memory = payload.get('slot_memory')
        if isinstance(slot_memory, dict) and slot_memory:
            return slot_memory
    return None


def _recent_slot_value(conversation_context: dict[str, Any] | None, key: str) -> str | None:
    slot_memory = _recent_trace_slot_memory(conversation_context)
    if not isinstance(slot_memory, dict):
        return None
    value = slot_memory.get(key)
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _recent_trace_focus(conversation_context: dict[str, Any] | None) -> dict[str, str] | None:
    slot_memory = _recent_trace_slot_memory(conversation_context)
    if isinstance(slot_memory, dict):
        focus_kind = str(slot_memory.get('focus_kind', '') or '').strip()
        protocol_code = str(slot_memory.get('protocol_code', '') or '').strip()
        active_task = str(slot_memory.get('active_task', '') or '').strip()
        active_entity = str(slot_memory.get('active_entity', '') or '').strip()
        pending_question_type = str(slot_memory.get('pending_question_type', '') or '').strip()
        if focus_kind or active_task or active_entity:
            inferred_focus_kind = focus_kind
            if active_task.startswith('public:'):
                inferred_focus_kind = 'public'
            elif not inferred_focus_kind:
                if active_task == 'workflow:visit_booking':
                    inferred_focus_kind = 'visit'
                elif active_task == 'workflow:institutional_request':
                    inferred_focus_kind = 'request'
                elif active_task == 'workflow:human_handoff':
                    inferred_focus_kind = 'support'
                elif active_task.startswith('finance:'):
                    inferred_focus_kind = 'finance'
                elif active_task.startswith('academic:'):
                    inferred_focus_kind = 'academic'
                elif active_task.startswith('admin:'):
                    inferred_focus_kind = 'secretaria'
            if active_task in NON_STICKY_PUBLIC_TASKS:
                return None
            if not _recent_focus_is_fresh(
                conversation_context,
                focus_kind=inferred_focus_kind,
                active_task=active_task,
            ):
                return None
            return {
                key: str(value).strip()
                for key, value in {
                    'kind': inferred_focus_kind,
                    'protocol_code': protocol_code,
                    'active_task': active_task,
                    'active_entity': active_entity,
                    'pending_question_type': pending_question_type,
                    'pending_disambiguation': slot_memory.get('pending_disambiguation'),
                    'public_entity': slot_memory.get('public_entity'),
                    'public_attribute': slot_memory.get('public_attribute'),
                    'public_pricing_segment': slot_memory.get('public_pricing_segment'),
                    'public_pricing_grade_year': slot_memory.get('public_pricing_grade_year'),
                    'public_pricing_quantity': slot_memory.get('public_pricing_quantity'),
                    'public_pricing_price_kind': slot_memory.get('public_pricing_price_kind'),
                    'requested_channel': slot_memory.get('requested_channel'),
                    'time_reference': slot_memory.get('time_reference'),
                    'academic_focus_kind': slot_memory.get('academic_focus_kind'),
                    'academic_attribute': slot_memory.get('academic_attribute'),
                    'academic_student_name': slot_memory.get('academic_student_name'),
                    'admin_attribute': slot_memory.get('admin_attribute'),
                    'student_name': slot_memory.get('student_name'),
                    'finance_status_filter': slot_memory.get('finance_status_filter'),
                    'finance_attribute': slot_memory.get('finance_attribute'),
                    'finance_action': slot_memory.get('finance_action'),
                    'finance_student_name': slot_memory.get('finance_student_name'),
                }.items()
                if str(value or '').strip()
            }
    for payload in _recent_orchestration_trace_payloads(conversation_context):
        selected_tools = payload.get('selected_tools')
        if isinstance(selected_tools, list):
            selected_tool_names = {
                str(tool_name).strip() for tool_name in selected_tools if isinstance(tool_name, str)
            }
            if {
                'schedule_school_visit',
                'update_visit_booking',
                'get_workflow_status',
            } & selected_tool_names:
                return {'kind': 'visit', 'protocol_code': ''}
            if {
                'create_institutional_request',
                'update_institutional_request',
            } & selected_tool_names:
                return {'kind': 'request', 'protocol_code': ''}
            if 'get_financial_summary' in selected_tool_names:
                return {'kind': 'finance', 'protocol_code': ''}
            if 'get_administrative_status' in selected_tool_names:
                return {'kind': 'secretaria', 'protocol_code': ''}
    return None


def _recent_workflow_focus(conversation_context: dict[str, Any] | None) -> dict[str, str] | None:
    if not isinstance(conversation_context, dict):
        return None
    for payload in _recent_orchestration_trace_payloads(conversation_context):
        slot_memory = payload.get('slot_memory')
        if isinstance(slot_memory, dict):
            active_task = str(slot_memory.get('active_task', '') or '').strip()
            protocol_code = str(slot_memory.get('protocol_code', '') or '').strip()
            if active_task == 'workflow:visit_booking':
                return {'kind': 'visit', 'protocol_code': protocol_code}
            if active_task == 'workflow:institutional_request':
                return {'kind': 'request', 'protocol_code': protocol_code}
            if active_task == 'workflow:human_handoff':
                return {'kind': 'support', 'protocol_code': protocol_code}

        selected_tools = payload.get('selected_tools')
        if not isinstance(selected_tools, list):
            continue
        selected_tool_names = {
            str(tool_name).strip() for tool_name in selected_tools if isinstance(tool_name, str)
        }
        if {
            'schedule_school_visit',
            'update_visit_booking',
            'get_workflow_status',
        } & selected_tool_names:
            return {'kind': 'visit', 'protocol_code': ''}
        if {'create_institutional_request', 'update_institutional_request'} & selected_tool_names:
            return {'kind': 'request', 'protocol_code': ''}
        if {'create_support_ticket', 'handoff_to_human'} & selected_tool_names:
            return {'kind': 'support', 'protocol_code': ''}

    for sender_type, content in reversed(_recent_message_lines(conversation_context)):
        if sender_type != 'assistant':
            continue
        normalized = _normalize_text(content)
        protocol_code = _extract_protocol_code_from_text(content) or ''
        if protocol_code.upper().startswith('VIS-'):
            return {'kind': 'visit', 'protocol_code': protocol_code}
        if protocol_code.upper().startswith('REQ-'):
            return {'kind': 'request', 'protocol_code': protocol_code}
        if protocol_code.upper().startswith('ATD-') and any(
            token in normalized for token in {'suporte', 'atendimento', 'fila', 'ticket', 'retorno'}
        ):
            return {'kind': 'support', 'protocol_code': protocol_code}
    return None


def _recent_visit_slot(
    conversation_context: dict[str, Any] | None,
) -> tuple[date | None, str | None]:
    if not isinstance(conversation_context, dict):
        return None, None
    recent_tool_calls = conversation_context.get('recent_tool_calls', [])
    if not isinstance(recent_tool_calls, list):
        return None, None
    for item in recent_tool_calls:
        if not isinstance(item, dict):
            continue
        tool_name = str(item.get('tool_name', '') or '').strip()
        if tool_name not in {'update_visit_booking', 'schedule_school_visit'}:
            continue
        response_payload = item.get('response_payload')
        if not isinstance(response_payload, dict):
            continue
        booking = response_payload.get('item')
        if not isinstance(booking, dict):
            continue
        preferred_date_raw = str(booking.get('preferred_date', '') or '').strip()
        preferred_window = str(booking.get('preferred_window', '') or '').strip() or None
        preferred_date: date | None = None
        if preferred_date_raw:
            try:
                preferred_date = date.fromisoformat(preferred_date_raw)
            except ValueError:
                preferred_date = None
        if preferred_date is not None or preferred_window is not None:
            return preferred_date, preferred_window
    for sender_type, content in reversed(_recent_message_lines(conversation_context)):
        if sender_type != 'assistant':
            continue
        normalized = _normalize_text(content)
        if 'preferencia informada:' not in normalized and 'nova preferencia:' not in normalized:
            continue
        slot_match = re.search(
            r'(?:nova preferencia|preferencia informada):\s*(\d{2}/\d{2}/\d{4})?(?:\s*-\s*)?([a-z0-9:]+)?',
            normalized,
        )
        if not slot_match:
            continue
        preferred_date: date | None = None
        preferred_window: str | None = None
        raw_date = (slot_match.group(1) or '').strip()
        raw_window = (slot_match.group(2) or '').strip()
        if raw_date:
            try:
                preferred_date = datetime.strptime(raw_date, '%d/%m/%Y').date()
            except ValueError:
                preferred_date = None
        if raw_window:
            preferred_window = raw_window
        if preferred_date is not None or preferred_window is not None:
            return preferred_date, preferred_window
    return None, None


def _assistant_already_introduced(conversation_context: dict[str, Any] | None) -> bool:
    for sender_type, content in _recent_message_lines(conversation_context):
        normalized = _normalize_text(content)
        if (
            sender_type == 'assistant'
            and 'eduassist' in normalized
            and 'colegio horizonte' in normalized
        ):
            return True
    return False


def _assistant_message_is_capability_overview(normalized_message: str) -> bool:
    return (
        'voce esta falando com o eduassist' in normalized_message
        or 'você está falando com o eduassist' in normalized_message
        or 'posso te ajudar com' in normalized_message
        or 'posso ajudar com informacoes publicas da escola' in normalized_message
    )


def _recent_conversation_focus(
    conversation_context: dict[str, Any] | None,
) -> dict[str, str] | None:
    trace_focus = _recent_trace_focus(conversation_context)
    if trace_focus:
        return trace_focus
    if not _recent_focus_is_fresh(conversation_context, focus_kind='public'):
        return None
    last_user_message: str | None = None
    for sender_type, content in reversed(_recent_message_lines(conversation_context)):
        normalized = _normalize_text(content)
        protocol_code = _extract_protocol_code_from_text(content) or ''
        if sender_type == 'assistant':
            if _assistant_message_is_capability_overview(normalized):
                continue
            if protocol_code.upper().startswith('VIS-'):
                return {'kind': 'visit', 'protocol_code': protocol_code}
            if protocol_code.upper().startswith('REQ-'):
                return {'kind': 'request', 'protocol_code': protocol_code}
            if protocol_code.upper().startswith('ATD-') and any(
                token in normalized
                for token in {'suporte', 'atendimento', 'fila', 'ticket', 'retorno'}
            ):
                return {'kind': 'support', 'protocol_code': protocol_code}
            if (
                'pedido de visita registrado' in normalized
                or 'pedido de visita segue' in normalized
                or 'visita cancelada' in normalized
            ):
                return {'kind': 'visit', 'protocol_code': protocol_code or ''}
            if 'visita' in normalized and any(
                token in normalized
                for token in {
                    'protocolo',
                    'remarcar',
                    'reagendar',
                    'cancelar',
                    'cancelado',
                    'pedido',
                }
            ):
                return {'kind': 'visit', 'protocol_code': protocol_code or ''}
            if (
                'solicitacao institucional registrada' in normalized
                or 'sua solicitacao institucional' in normalized
            ):
                return {'kind': 'request', 'protocol_code': protocol_code or ''}
            if (
                'mensalidade publica de referencia' in normalized
                or 'taxa publica de matricula' in normalized
            ):
                return {
                    'kind': 'public',
                    'protocol_code': '',
                    'active_task': 'public:pricing',
                    'active_entity': 'mensalidade',
                }
            if 'financeiro' in normalized and any(
                token in normalized for token in {'boleto', 'fatura', 'contrato'}
            ):
                return {'kind': 'finance', 'protocol_code': protocol_code or ''}
            if 'secretaria' in normalized:
                return {'kind': 'secretaria', 'protocol_code': protocol_code or ''}
            if 'matricula' in normalized:
                return {'kind': 'admissions', 'protocol_code': protocol_code or ''}
        elif sender_type == 'user' and last_user_message is None:
            last_user_message = content

    if not last_user_message:
        return None

    normalized_user = _normalize_text(last_user_message)
    if _is_public_pricing_navigation_query(last_user_message):
        return {
            'kind': 'public',
            'protocol_code': '',
            'active_task': 'public:pricing',
            'active_entity': 'mensalidade',
        }
    if any(
        _message_matches_term(normalized_user, term)
        for term in {'visita', 'tour', 'conhecer a escola'}
    ):
        return {'kind': 'visit', 'protocol_code': ''}
    if any(
        _message_matches_term(normalized_user, term)
        for term in {'direcao', 'direção', 'protocolo', 'solicitacao'}
    ):
        return {'kind': 'request', 'protocol_code': ''}
    if any(
        _message_matches_term(normalized_user, term)
        for term in {'boleto', 'fatura', 'mensalidade', 'financeiro'}
    ):
        return {'kind': 'finance', 'protocol_code': ''}
    if any(
        _message_matches_term(normalized_user, term)
        for term in {'documento', 'historico', 'secretaria'}
    ):
        return {'kind': 'secretaria', 'protocol_code': ''}
    if any(
        _message_matches_term(normalized_user, term) for term in {'matricula', 'bolsa', 'desconto'}
    ):
        return {'kind': 'admissions', 'protocol_code': ''}
    return None


def _recent_focus_follow_up_line(conversation_context: dict[str, Any] | None) -> str | None:
    focus = _recent_conversation_focus(conversation_context)
    if not focus:
        return None
    protocol_code = focus.get('protocol_code', '').strip()
    suffix = f' com protocolo {protocol_code}' if protocol_code else ''
    kind = focus.get('kind')
    if kind == 'visit':
        return f'Se quiser, eu retomo sua visita{suffix} e sigo daqui.'
    if kind == 'request':
        return f'Se quiser, eu retomo sua solicitacao institucional{suffix} e te digo status, prazo ou proximo passo.'
    return None


def _is_private_admin_follow_up(
    message: str,
    conversation_context: dict[str, Any] | None,
) -> bool:
    normalized = _normalize_text(message)
    if not any(
        _message_matches_term(normalized, term)
        for term in {
            'documentacao',
            'documentação',
            'documentos',
            'cadastro',
            'email',
            'telefone',
            'dados cadastrais',
        }
    ):
        return False
    focus = _recent_conversation_focus(conversation_context)
    if not isinstance(focus, dict):
        return False
    if focus.get('kind') == 'finance':
        return True
    active_task = str(focus.get('active_task', '') or '').strip()
    return active_task.startswith('finance:') or active_task.startswith('admin:')


def _is_admin_finance_combined_query(message: str) -> bool:
    normalized = _normalize_text(message)
    mentions_admin = any(
        _message_matches_term(normalized, term)
        for term in {
            'documentacao',
            'documentação',
            'documentos',
            'cadastro',
            'regular',
            'regularidade',
            'pendencia',
            'pendência',
            'administrativo',
            'administrativa',
            'documental',
        }
    )
    mentions_finance = any(
        _message_matches_term(normalized, term)
        for term in {
            'financeiro',
            'situacao financeira',
            'situação financeira',
            'boleto',
            'boletos',
            'mensalidade',
            'mensalidades',
            'fatura',
            'faturas',
            'bloqueando atendimento',
            'bloqueio',
            'vencimento',
            'atraso',
            'atrasos',
        }
    )
    return mentions_admin and mentions_finance


def _recent_admin_finance_combo_context(
    conversation_context: dict[str, Any] | None,
) -> bool:
    if not isinstance(conversation_context, dict):
        return False
    recent_blob = ' '.join(
        _normalize_text(content)
        for _sender_type, content in _recent_message_lines(conversation_context)
    )
    mentions_admin = any(
        term in recent_blob
        for term in {
            'documentacao',
            'documentação',
            'cadastro',
            'pendencia',
            'pendência',
            'administrativo',
            'administrativa',
        }
    )
    mentions_finance = any(
        term in recent_blob
        for term in {
            'financeiro',
            'fatura',
            'faturas',
            'mensalidade',
            'mensalidades',
            'boleto',
            'boletos',
            'bloqueando atendimento',
            'bloqueio',
        }
    )
    return mentions_admin and mentions_finance


def _is_meta_repair_context_query(message: str) -> bool:
    normalized = _normalize_text(message)
    return any(
        _message_matches_term(normalized, term)
        for term in {
            'essa resposta era sobre o que',
            'essa resposta era sobre o que entao',
            'essa resposta era sobre o que então',
            'era sobre o que',
            'resposta aqui era sobre o que',
        }
    )


def _compose_meta_repair_follow_up_answer(
    conversation_context: dict[str, Any] | None,
) -> str | None:
    recent_focus = _recent_trace_focus(conversation_context) or _recent_conversation_focus(
        conversation_context
    )
    if not isinstance(recent_focus, dict):
        return None
    active_task = str(recent_focus.get('active_task', '') or '').strip()
    active_entity = str(
        recent_focus.get('academic_student_name')
        or recent_focus.get('finance_student_name')
        or recent_focus.get('student_name')
        or recent_focus.get('active_entity')
        or ''
    ).strip()
    scope = f' de {active_entity}' if active_entity else ''
    recent_messages = (
        conversation_context.get('recent_messages')
        if isinstance(conversation_context, dict)
        else None
    )
    last_assistant_message = (
        _extract_recent_assistant_message(recent_messages)
        if isinstance(recent_messages, list)
        else None
    )
    last_assistant_normalized = _normalize_text(last_assistant_message or '')
    if any(
        term in last_assistant_normalized
        for term in {
            'proximas avaliacoes',
            'próximas avaliações',
            'proximas provas',
            'próximas provas',
            'avaliacao',
            'avaliação',
        }
    ):
        return f'A resposta anterior estava falando das proximas provas{scope}.'
    if any(
        term in last_assistant_normalized
        for term in {'frequencia', 'frequência', 'faltas', 'presenca', 'presença', 'atraso'}
    ):
        return f'A resposta anterior estava falando da frequencia{scope}.'
    if any(
        term in last_assistant_normalized
        for term in {'nota', 'notas', 'media parcial', 'média parcial', 'boletim'}
    ):
        return f'A resposta anterior estava falando das notas{scope}.'
    if any(
        term in last_assistant_normalized
        for term in {'financeiro', 'fatura', 'boleto', 'vencimento', 'mensalidade'}
    ):
        return f'A resposta anterior estava falando do financeiro{scope}.'
    if active_task == 'academic:upcoming':
        return f'A resposta anterior estava falando das proximas provas{scope}.'
    if active_task in {'academic:attendance', 'academic:attendance_timeline'}:
        return f'A resposta anterior estava falando da frequencia{scope}.'
    if active_task == 'academic:grades':
        return f'A resposta anterior estava falando das notas{scope}.'
    if active_task.startswith('finance:'):
        return f'A resposta anterior estava falando do financeiro{scope}.'
    if active_task == 'admin:student_administrative_status':
        return f'A resposta anterior estava falando da documentacao{scope}.'
    if active_task.startswith('admin:'):
        return 'A resposta anterior estava falando do seu cadastro administrativo.'
    if active_task == 'public:timeline':
        return 'A resposta anterior estava falando da linha do tempo publica da escola.'
    if active_task == 'public:pricing':
        return 'A resposta anterior estava falando dos valores publicos de matricula e mensalidade.'
    return None


def _is_public_only_theme_follow_up(message: str) -> bool:
    normalized = _normalize_text(message)
    return any(
        _message_matches_term(normalized, term)
        for term in {
            'apenas o que e publico nesse tema',
            'apenas o que é publico nesse tema',
            'apenas o que e publico',
            'apenas o que é publico',
            'so o que e publico nesse tema',
            'só o que é público nesse tema',
            'so o que e publico',
            'só o que é público',
            'o que e publico nesse tema',
            'o que é público nesse tema',
            'o que existe de publico sobre esse tipo de saida',
            'o que existe de público sobre esse tipo de saída',
            'o que existe de publico sobre esse tipo de saida ou protocolo',
            'o que existe de público sobre esse tipo de saída ou protocolo',
        }
    )


def _recent_messages_blob(conversation_context: dict[str, Any] | None) -> str:
    if not isinstance(conversation_context, dict):
        return ''
    return ' '.join(
        str(content or '') for _sender_type, content in _recent_message_lines(conversation_context)
    )


def _is_service_routing_context_follow_up(
    message: str,
    *,
    conversation_context: dict[str, Any] | None,
) -> bool:
    recent_focus = _recent_trace_focus(conversation_context) or _recent_conversation_focus(
        conversation_context
    )
    normalized = _normalize_text(message)
    active_task = (
        str((recent_focus or {}).get('active_task', '') or '').strip()
        if isinstance(recent_focus, dict)
        else ''
    )
    if active_task not in {'public:contacts', 'public:service_routing'}:
        recent_blob = _normalize_text(_recent_messages_blob(conversation_context))
        asks_direct_contacts = any(
            _message_matches_term(normalized, term)
            for term in {
                'contatos da secretaria',
                'contatos do financeiro',
                'contato da secretaria',
                'contato do financeiro',
                'contatos',
                'contato',
            }
        )
        if not (
            asks_direct_contacts
            and any(
                term in recent_blob
                for term in {
                    'portal',
                    'secretaria',
                    'financeiro',
                    'bolsa',
                    'bolsas',
                    'direcao',
                    'direção',
                }
            )
        ):
            return False
    return any(
        _message_matches_term(normalized, term)
        for term in {
            'contatos da secretaria',
            'contatos do financeiro',
            'contato da secretaria',
            'contato do financeiro',
            'contatos',
            'contato',
            'uma linha por setor',
            'sem explicar o resto da escola',
            'seja objetivo',
            'seja objetiva',
            'qual desses setores entra primeiro',
            'qual setor entra primeiro',
            'entra primeiro',
        }
    )


def _rewrite_service_routing_context_follow_up(
    message: str,
    *,
    conversation_context: dict[str, Any] | None,
) -> str | None:
    if not _is_service_routing_context_follow_up(
        message, conversation_context=conversation_context
    ):
        return None
    blob = _normalize_text(_recent_messages_blob(conversation_context))
    combined = f'{blob} {_normalize_text(message)}'.strip()
    sectors: list[str] = []
    if any(term in combined for term in {'bolsa', 'bolsas', 'desconto', 'descontos'}):
        sectors.append('bolsas')
    if 'financeiro' in combined or any(
        term in combined for term in {'mensalidade', 'fatura', 'boleto'}
    ):
        sectors.append('financeiro')
    if any(term in combined for term in {'direcao', 'direção', 'diretora', 'diretor'}):
        sectors.append('direcao')
    if any(term in combined for term in {'secretaria'}):
        sectors.append('secretaria')
    if not sectors:
        return None
    normalized = _normalize_text(message)
    if any(
        _message_matches_term(normalized, term)
        for term in {
            'qual desses setores entra primeiro',
            'qual setor entra primeiro',
            'entra primeiro',
        }
    ):
        if 'bolsas' in sectors:
            return (
                'Se o tema for bolsa com documento pendente, qual setor entra primeiro '
                f'entre {", ".join(sectors)}? Seja objetivo.'
            )
    if any(
        _message_matches_term(normalized, term)
        for term in {
            'contatos da secretaria',
            'contatos do financeiro',
            'contato da secretaria',
            'contato do financeiro',
            'contatos',
            'contato',
        }
    ):
        if 'secretaria' in sectors and 'financeiro' in sectors:
            return 'Me diga como entrar em contato com a secretaria e com o financeiro dentro desse mesmo fluxo de onboarding.'
        return (
            f'Me diga os contatos de {", ".join(sectors)} dentro desse mesmo fluxo de onboarding.'
        )
    return f'Me diga so os canais de {", ".join(sectors)}. Uma linha por setor, sem explicar o resto da escola.'


def _recent_restricted_outings_no_match_context(
    conversation_context: dict[str, Any] | None,
) -> bool:
    blob = _normalize_text(_recent_messages_blob(conversation_context))
    if not blob:
        return False
    has_no_match = any(
        term in blob for term in {'nao encontrei', 'não encontrei', 'sem match', 'sem evidencia'}
    )
    has_outings = any(
        term in blob
        for term in {
            'excursao',
            'excursão',
            'saida pedagogica',
            'saída pedagógica',
            'viagem',
            'autorizacao',
            'autorização',
        }
    )
    return has_no_match and has_outings


def _rewrite_restricted_public_protocol_follow_up(
    message: str,
    *,
    conversation_context: dict[str, Any] | None,
) -> str | None:
    if not _recent_restricted_outings_no_match_context(conversation_context):
        return None
    normalized = _normalize_text(message)
    if _is_public_only_theme_follow_up(message):
        return 'Me diga so o que existe de publico sobre saidas pedagogicas, viagens e protocolo de autorizacao da escola.'
    if any(
        _message_matches_term(normalized, term)
        for term in {
            'resume isso em dois passos praticos',
            'resuma isso em dois passos praticos',
            'resume em dois passos praticos',
        }
    ):
        return 'Resuma em dois passos praticos o que existe de publico sobre saidas pedagogicas, viagens e autorizacoes da escola.'
    return None


def _compose_contextual_public_boundary_answer(
    *,
    message: str,
    conversation_context: dict[str, Any] | None,
    profile: dict[str, Any] | None,
) -> str | None:
    if not isinstance(profile, dict) or not _is_public_only_theme_follow_up(message):
        return None

    public_answer: str | None = None
    if _recent_messages_mention(
        conversation_context,
        {'transporte', 'uniforme', 'refeicao', 'refeição', 'cantina', 'almoco', 'almoço'},
    ):
        public_answer = compose_public_transport_uniform_bundle()
    elif _recent_messages_mention(
        conversation_context,
        {'atestado', 'saude', 'saúde', 'segunda chamada', 'recuperacao', 'recuperação'},
    ):
        public_answer = compose_public_health_second_call()
    elif _recent_messages_mention(
        conversation_context,
        {
            'viagem internacional',
            'viagem',
            'saidas pedagogicas',
            'saídas pedagógicas',
            'autorizacao',
            'autorização',
            'protocolo interno',
        },
    ):
        public_answer = compose_public_outings_authorizations()

    if not public_answer:
        return None
    return (
        'Restrito: esse trecho continua sem acesso ao protocolo interno desse tema. '
        f'Publico: {public_answer}'
    )
