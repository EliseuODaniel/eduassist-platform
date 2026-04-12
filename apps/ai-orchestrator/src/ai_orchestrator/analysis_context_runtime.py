from __future__ import annotations

# ruff: noqa: F401,F403,F405
"""Conversation-context and analysis-message helpers extracted from intent_analysis_runtime.py."""

from . import runtime_core as _runtime_core
from .conversation_focus_runtime import (
    _compose_meta_repair_follow_up_answer,
    _is_meta_repair_context_query,
    _recent_admin_finance_combo_context,
    _recent_conversation_focus,
    _recent_message_lines,
    _recent_slot_value,
    _recent_trace_focus,
    _recent_trace_used_tool,
    _rewrite_restricted_public_protocol_follow_up,
    _rewrite_service_routing_context_follow_up,
)
from .intent_analysis_runtime import (
    _contains_any,
    _detect_admin_attribute_request,
    _is_follow_up_query,
    _is_public_curriculum_context_follow_up,
    _is_public_pricing_context_follow_up,
    _message_matches_term,
    _normalize_text,
    _wants_upcoming_assessments,
)
from .protected_domain_runtime import _requested_subject_label_from_message
from .public_orchestration_runtime import _extract_requested_date, _extract_requested_window
from .student_scope_runtime import _is_discourse_repair_reset_query


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


def _extract_recent_user_message(recent_messages: list[dict[str, Any]]) -> str | None:
    for item in reversed(recent_messages):
        if not isinstance(item, dict):
            continue
        if item.get('sender_type') != 'user':
            continue
        content = str(item.get('content', '')).strip()
        if content:
            return content
    return None


def _extract_recent_assistant_message(recent_messages: list[dict[str, Any]]) -> str | None:
    for item in reversed(recent_messages):
        if not isinstance(item, dict):
            continue
        if item.get('sender_type') != 'assistant':
            continue
        content = str(item.get('content', '')).strip()
        if content:
            return content
    return None


def _extract_protocol_code_from_text(text: str | None) -> str | None:
    if not text:
        return None
    match = PROTOCOL_CODE_PATTERN.search(text)
    if match is None:
        return None
    return match.group(0).upper()


def _extract_protocol_code_hint(
    message: str,
    conversation_context: dict[str, Any] | None,
) -> str | None:
    direct_match = _extract_protocol_code_from_text(message)
    if direct_match:
        return direct_match
    for payload in _recent_orchestration_trace_payloads(conversation_context):
        slot_memory = payload.get('slot_memory')
        if not isinstance(slot_memory, dict):
            continue
        protocol_code = str(slot_memory.get('protocol_code', '') or '').strip()
        if protocol_code:
            return protocol_code
    for _sender_type, content in reversed(_recent_message_lines(conversation_context)):
        code = _extract_protocol_code_from_text(content)
        if code:
            return code
    return None


def _detect_workflow_kind_hint(
    message: str,
    conversation_context: dict[str, Any] | None,
) -> str | None:
    normalized = _normalize_text(message)
    if any(_message_matches_term(normalized, term) for term in WORKFLOW_VISIT_TERMS):
        return 'visit_booking'
    if any(_message_matches_term(normalized, term) for term in WORKFLOW_REQUEST_TERMS):
        return 'institutional_request'
    if any(_message_matches_term(normalized, term) for term in WORKFLOW_HANDOFF_TERMS):
        return 'support_handoff'

    focus = _recent_trace_focus(conversation_context)
    if isinstance(focus, dict):
        focus_kind = str(focus.get('kind', '')).strip()
        if focus_kind == 'visit':
            return 'visit_booking'
        if focus_kind == 'request':
            return 'institutional_request'
        if focus_kind == 'support':
            return 'support_handoff'

    for _sender_type, content in reversed(_recent_message_lines(conversation_context)):
        content_normalized = _normalize_text(content)
        if 'pedido de visita registrado' in content_normalized or 'vis-' in content_normalized:
            return 'visit_booking'
        if (
            'solicitacao institucional registrada' in content_normalized
            or 'req-' in content_normalized
        ):
            return 'institutional_request'
        if (
            'encaminhei sua solicitacao para a fila' in content_normalized
            or 'atd-' in content_normalized
        ):
            return 'support_handoff'
    return None


def _conversation_context_payload(
    conversation_context: ConversationContextBundle | None,
) -> dict[str, Any] | None:
    if conversation_context is None:
        return None
    return {
        'conversation_external_id': getattr(conversation_context, 'conversation_external_id', None),
        'message_count': int(getattr(conversation_context, 'message_count', 0) or 0),
        'recent_messages': list(getattr(conversation_context, 'recent_messages', []) or []),
        'recent_tool_calls': list(getattr(conversation_context, 'recent_tool_calls', []) or []),
    }


def _looks_like_visit_update_follow_up(message: str) -> bool:
    normalized = _normalize_text(message)
    if _extract_requested_date(message) or _extract_requested_window(message):
        return True
    if any(
        _message_matches_term(normalized, term)
        for term in (
            'cancelar',
            'cancela',
            'cancelamento',
            'remarcar',
            'reagendar',
            'trocar horario',
            'trocar o horario',
            'mudar horario',
            'mudar o horario',
        )
    ):
        return True
    if any(
        _message_matches_term(normalized, term)
        for term in (
            *VISIT_CANCEL_TERMS,
            *VISIT_RESCHEDULE_TERMS,
            'qual o protocolo',
            'qual e o protocolo',
            'qual é o protocolo',
            'qual o status',
            'como esta',
            'como está',
            'resume',
            'resuma',
            'agora cancela',
            'agora remarca',
        )
    ):
        return True
    return any(
        _message_matches_term(normalized, term)
        for term in {
            'pode ser',
            'nesse dia',
            'neste dia',
            'naquele dia',
            'esse dia',
            'aquele dia',
            'nessa data',
            'nesta data',
        }
    )


def _looks_like_workflow_resume_follow_up(message: str) -> bool:
    normalized = _normalize_text(message)
    return any(
        _message_matches_term(normalized, term)
        for term in {
            'retomar',
            'retoma',
            'retomo',
            'retomar depois',
            'retomar a visita',
            'retomar o pedido',
            'quero retomar',
            'quero retomar depois',
            'voltar',
            'volto',
            'voltar depois',
            'quero voltar',
            'quero voltar depois',
            'como retomo',
            'como eu retomo',
            'como volto',
            'como eu volto',
            'por onde volto',
            'por onde eu volto',
            'por onde retomo',
            'por onde eu retomo',
            'qual o caminho para voltar',
            'qual o caminho para retomar',
        }
    )


def _looks_like_natural_visit_booking_request(message: str) -> bool:
    normalized = _normalize_text(message)
    explicit_visit_phrases = {
        'quero visitar',
        'visitar a escola',
        'visitar o colegio',
        'visitar o colégio',
        'quero conhecer a escola',
        'conhecer a escola',
        'conhecer o colegio',
        'conhecer o colégio',
    }
    if any(_message_matches_term(normalized, phrase) for phrase in explicit_visit_phrases):
        return True
    visit_targets = {'visita', 'visita guiada', 'tour', 'escola', 'colegio', 'colégio'}
    scheduling_verbs = {'agendar', 'agendamento', 'marcar', 'reservar', 'visitar', 'conhecer'}
    return _contains_any(normalized, scheduling_verbs) and _contains_any(normalized, visit_targets)


def _build_analysis_message(
    message: str, conversation_context: ConversationContextBundle | None
) -> str:
    if conversation_context is None:
        return message

    context_payload = _conversation_context_payload(conversation_context)
    if _is_discourse_repair_reset_query(message, context_payload):
        return message
    recent_focus = _recent_conversation_focus(context_payload)
    active_task = str((recent_focus or {}).get('active_task', '') or '').strip()
    normalized_message = _normalize_text(message)
    if _is_meta_repair_context_query(message):
        return f'{message} sobre o assunto da resposta anterior, sem repetir os dados'
    service_routing_followup = _rewrite_service_routing_context_follow_up(
        message,
        conversation_context=context_payload,
    )
    if service_routing_followup:
        return service_routing_followup
    restricted_public_followup = _rewrite_restricted_public_protocol_follow_up(
        message,
        conversation_context=context_payload,
    )
    if restricted_public_followup:
        return restricted_public_followup
    recent_student_name = str(
        (recent_focus or {}).get('academic_student_name')
        or (recent_focus or {}).get('finance_student_name')
        or (recent_focus or {}).get('student_name')
        or ''
    ).strip()
    if (
        _recent_trace_used_tool(context_payload, 'get_administrative_status')
        and _detect_admin_attribute_request(message, context_payload) is not None
    ):
        return f'{message} sobre dados cadastrais do seu cadastro'
    onboarding_context = _recent_messages_mention(
        context_payload,
        {
            'portal',
            'secretaria',
            'credenciais',
            'envio de documentos',
            'documentos',
            'matricula',
            'matrícula',
        },
    )
    if onboarding_context and any(
        _message_matches_term(normalized_message, term)
        for term in {'contatos', 'contato', 'secretaria', 'financeiro', 'junto com isso'}
    ):
        return (
            'como entrar em contato com a secretaria e com o financeiro '
            'no fluxo publico de portal, secretaria e envio de documentos'
        )
    if onboarding_context and any(
        _message_matches_term(normalized_message, term)
        for term in {
            'antes do inicio das aulas',
            'antes do início das aulas',
            'ordem certa',
            'em ordem',
            'sequencia',
            'sequência',
            'proximo marco com as familias',
            'próximo marco com as famílias',
            'proximo marco com os responsaveis',
            'próximo marco com os responsáveis',
        }
    ):
        return (
            f'{message} sobre a linha do tempo publica entre matricula, envio de documentos, portal, '
            'inicio das aulas e reuniao com responsaveis'
        )
    if (
        onboarding_context
        and any(
            _message_matches_term(normalized_message, term)
            for term in {
                'depois disso',
                'qual o proximo marco',
                'qual o próximo marco',
                'marco publico com as familias',
                'marco público com as famílias',
            }
        )
        and any(
            _message_matches_term(normalized_message, term)
            for term in {
                'familias',
                'famílias',
                'responsaveis',
                'responsáveis',
                'reuniao',
                'reunião',
            }
        )
    ):
        return (
            f'{message} sobre a linha do tempo publica entre matricula, envio de documentos, inicio das aulas '
            'e o proximo marco com as familias'
        )
    recent_pricing_context = recent_focus and active_task == 'public:pricing'
    if not recent_pricing_context:
        recent_pricing_context = _recent_messages_mention(
            context_payload,
            {
                'mensalidade',
                'matricula',
                'matrícula',
                'taxa de matricula',
                'taxa de matrícula',
                'ensino medio',
                'ensino médio',
                'fundamental ii',
            },
        )
    if recent_pricing_context and (
        _is_public_pricing_context_follow_up(message, conversation_context=context_payload)
        or any(
            _message_matches_term(normalized_message, term)
            for term in {'vaga', 'vagas', 'estacionamento'}
        )
    ):
        if any(
            _message_matches_term(normalized_message, term)
            for term in PUBLIC_CAPACITY_PARKING_TERMS
        ):
            return f'{message} sobre vagas de estacionamento na escola'
        return f'{message} sobre vagas para alunos e disponibilidade de matricula na escola'
    if any(
        _message_matches_term(normalized_message, term)
        for term in {
            'apenas o que e publico nesse tema',
            'apenas o que é publico nesse tema',
            'so o que e publico nesse tema',
            'só o que é público nesse tema',
        }
    ):
        if _recent_messages_mention(
            context_payload,
            {'transporte', 'uniforme', 'refeicao', 'refeição', 'cantina', 'almoco', 'almoço'},
        ):
            return f'{message} sobre transporte, uniforme e refeicoes na documentacao publica da escola'
        if _recent_messages_mention(
            context_payload,
            {'atestado', 'saude', 'saúde', 'segunda chamada', 'recuperacao', 'recuperação'},
        ):
            return f'{message} sobre atestado de saude, segunda chamada e recuperacao na documentacao publica da escola'
        if _recent_messages_mention(
            context_payload,
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
            return f'{message} sobre saidas pedagogicas, viagens e autorizacoes na documentacao publica da escola'
    if (
        _is_follow_up_query(message)
        and _recent_admin_finance_combo_context(context_payload)
        and any(
            _message_matches_term(normalized_message, term)
            for term in {
                'regularizar',
                'proximo passo',
                'próximo passo',
                'em aberto',
                'bloqueio',
                'bloqueando atendimento',
                'nada estiver bloqueando',
                'se nada estiver bloqueando',
                'fala isso de forma direta',
            }
        )
    ):
        return (
            f'{message} sobre documentacao e financeiro no panorama combinado da conta, '
            'dizendo claramente se ha bloqueio de atendimento'
        )
    recent_calendar_context = recent_focus and active_task in {
        'public:timeline',
        'public:calendar_events',
    }
    if not recent_calendar_context:
        recent_calendar_context = _recent_messages_mention(
            context_payload,
            {
                'aulas',
                'comecam as aulas',
                'começam as aulas',
                'formatura',
                'reuniao com responsaveis',
                'reunião com responsáveis',
                'calendario',
                'calendário',
            },
        )
    if recent_calendar_context and any(
        _message_matches_term(normalized_message, term)
        for term in {
            'ja comecaram',
            'já começaram',
            'ta longe',
            'está longe',
            'vai me avisar',
            'vao me avisar',
            'vão me avisar',
            'me avisa',
            'me avise',
            'quando chegar perto',
        }
    ):
        return (
            f'{message} sobre datas e acompanhamento do evento anterior no calendario institucional'
        )
    if recent_calendar_context and any(
        _message_matches_term(normalized_message, term)
        for term in {
            'antes ou depois das aulas',
            'a matricula entra onde',
            'a matrícula entra onde',
            'quero so esse recorte em ordem',
            'quero só esse recorte em ordem',
            'so esse recorte em ordem',
            'só esse recorte em ordem',
        }
    ):
        if any(
            _message_matches_term(normalized_message, term)
            for term in {
                'antes ou depois das aulas',
                'a primeira reuniao acontece antes ou depois',
                'primeira reuniao',
            }
        ):
            return (
                'a primeira reuniao com responsaveis acontece antes ou depois do inicio das aulas '
                'na linha do tempo publica entre matricula, inicio das aulas e reuniao inicial com os responsaveis'
            )
        return (
            'ordenar a linha do tempo publica entre matricula, inicio das aulas '
            'e reuniao inicial com os responsaveis'
        )
    if (
        recent_focus
        and recent_focus.get('kind') == 'visit'
        and _looks_like_visit_update_follow_up(message)
    ):
        return f'remarcar visita: {message}'
    if not conversation_context.recent_messages:
        return message
    if not _is_follow_up_query(message):
        return message

    last_user_message = _extract_recent_user_message(conversation_context.recent_messages)
    last_assistant_message = _extract_recent_assistant_message(conversation_context.recent_messages)
    if not last_user_message and not last_assistant_message:
        return message

    if recent_focus:
        normalized_student_name = _normalize_text(recent_student_name)
        if (
            recent_student_name
            and normalized_student_name
            and normalized_student_name in normalized_message
        ):
            if (
                active_task.startswith('academic:')
                or str(recent_focus.get('kind') or '') == 'academic'
            ):
                return f'{message} sobre panorama academico de {recent_student_name}'
            if (
                active_task.startswith('finance:')
                or str(recent_focus.get('kind') or '') == 'finance'
            ):
                return f'{message} sobre panorama financeiro de {recent_student_name}'
        if (
            recent_student_name
            and active_task.startswith('academic:')
            and _wants_upcoming_assessments(message)
        ):
            return f'{message} sobre proximas avaliacoes de {recent_student_name}'
        if (
            recent_student_name
            and active_task.startswith('academic:')
            and _requested_subject_label_from_message(message) is not None
            and not any(
                _message_matches_term(normalized_message, term)
                for term in {
                    'frequencia',
                    'frequência',
                    'faltas',
                    'provas',
                    'avaliacoes',
                    'avaliações',
                }
            )
        ):
            if (
                active_task == 'academic:upcoming'
                or str(recent_focus.get('academic_focus_kind') or '').strip() == 'upcoming'
                or any(
                    term in _normalize_text(last_assistant_message or '')
                    for term in {
                        'proximas avaliacoes',
                        'próximas avaliações',
                        'proximas provas',
                        'próximas provas',
                    }
                )
            ):
                return f'{message} sobre proximas avaliacoes de {recent_student_name}'
            return f'{message} sobre notas de {recent_student_name}'
        if active_task == 'public:document_submission':
            return f'{message} sobre envio de documentos pela secretaria ou portal institucional'
        if active_task == 'admin:access_scope' and any(
            _message_matches_term(normalized_message, term)
            for term in {'cada um', 'sobre cada um', 'sobre cada aluno', 'o que eu consigo ver'}
        ):
            return f'{message} sobre o escopo academico e financeiro de cada aluno vinculado desta conta'
        if active_task == 'workflow:human_handoff' and any(
            _message_matches_term(_normalize_text(message), term)
            for term in {'abre pra', 'abre para', 'encaminha pra', 'encaminha para'}
        ):
            return f'abrir atendimento humano para {message}'
        if active_task.startswith(('admin:', 'finance:', 'academic:', 'workflow:')):
            context_phrase = _follow_up_context_phrase(
                active_task,
                recent_focus.get('active_entity'),
            )
            if context_phrase:
                return f'{message} sobre {context_phrase}'

    entity_hints = {
        *_extract_public_entity_hints(last_user_message or ''),
        *_extract_public_entity_hints(last_assistant_message or ''),
    }
    if entity_hints:
        referents = ', '.join(sorted(entity_hints))
        return f'{message} sobre {referents}'
    if recent_focus:
        context_phrase = _follow_up_context_phrase(
            recent_focus.get('active_task'),
            recent_focus.get('active_entity'),
        )
        if context_phrase:
            return f'{message} sobre {context_phrase}'
        active_entity = recent_focus.get('active_entity')
        if active_entity:
            return f'{message} sobre {active_entity}'
    if last_user_message:
        return f'{message} contexto anterior {last_user_message}'
    return message


def _retrieval_hits_cover_query_hints(retrieval_hits: list[Any], query_hints: set[str]) -> bool:
    if not query_hints:
        return True
    if not retrieval_hits:
        return False

    haystack = ' '.join(
        _normalize_text(
            ' '.join(
                filter(
                    None,
                    [
                        getattr(hit, 'document_title', None),
                        getattr(hit, 'text_excerpt', None),
                        getattr(hit, 'contextual_summary', None),
                    ],
                )
            )
        )
        for hit in retrieval_hits
    )
    return all(hint in haystack for hint in query_hints)


def _filter_retrieval_hits_by_query_hints(
    retrieval_hits: list[Any], query_hints: set[str]
) -> list[Any]:
    if not query_hints:
        return retrieval_hits

    filtered_hits = []
    for hit in retrieval_hits:
        haystack = _normalize_text(
            ' '.join(
                filter(
                    None,
                    [
                        getattr(hit, 'document_title', None),
                        getattr(hit, 'text_excerpt', None),
                        getattr(hit, 'contextual_summary', None),
                    ],
                )
            )
        )
        if any(hint in haystack for hint in query_hints):
            filtered_hits.append(hit)
    return filtered_hits or retrieval_hits


