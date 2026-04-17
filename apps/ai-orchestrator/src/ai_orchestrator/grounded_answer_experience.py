from __future__ import annotations

import asyncio
import logging
import re
import unicodedata
from datetime import date, datetime
from time import monotonic
from types import SimpleNamespace
from typing import Any
from zoneinfo import ZoneInfo

import httpx
from eduassist_semantic_ingress import is_terminal_ingress_act, looks_like_language_preference_feedback

from .conversation_answer_state import (
    AnswerFocusState,
    build_focus_summary,
    explicit_subject_from_message,
    resolve_answer_focus,
)
from .conversation_answer_state import (
    normalize_text as _focus_normalize_text,
)
from .llm_provider import (
    compose_grounded_answer_experience_with_provider,
    plan_context_repair_with_provider,
)
from .models import (
    AccessTier,
    ConversationChannel,
    MessageResponse,
    MessageResponseRequest,
    OrchestrationMode,
    QueryDomain,
    RetrievalBackend,
    RetrievalProfile,
)
from .public_doc_knowledge import (
    compose_public_canonical_lane_answer,
    compose_public_bolsas_and_processes,
    compose_public_calendar_visibility,
    compose_public_first_month_risks,
    compose_public_health_emergency_bundle,
    compose_public_outings_authorizations,
    compose_public_permanence_and_family_support,
    compose_public_teacher_directory_boundary,
    compose_public_timeline_lifecycle_bundle,
    match_public_canonical_lane as match_shared_public_canonical_lane,
)
from .request_intent_guardrails import looks_like_school_domain_request
from .python_functions_public_knowledge import (
    compose_public_conduct_policy_contextual_answer,
    match_public_canonical_lane as match_python_functions_public_canonical_lane,
)
from .public_known_unknowns import compose_public_known_unknown_answer, detect_public_known_unknown_key
from .retrieval import get_retrieval_service, looks_like_restricted_document_query

logger = logging.getLogger(__name__)
_ANSWER_FOCUS_CACHE_TTL_SECONDS = 900.0
_ANSWER_FOCUS_CACHE: dict[str, dict[str, Any]] = {}
_PUBLIC_CANONICAL_SAFE_LANES = {
    'public_bundle.academic_policy_overview',
    'public_bundle.governance_protocol',
    'public_bundle.conduct_frequency_punctuality',
    'public_bundle.policy_compare',
    'public_bundle.timeline_lifecycle',
    'public_bundle.year_three_phases',
    'public_bundle.family_new_calendar_assessment_enrollment',
    'public_bundle.first_month_risks',
    'public_bundle.process_compare',
    'public_bundle.health_second_call',
    'public_bundle.health_authorizations_bridge',
    'public_bundle.conduct_frequency_recovery',
    'public_bundle.secretaria_portal_credentials',
    'public_bundle.bolsas_and_processes',
    'public_bundle.transversal_year',
    'public_bundle.facilities_study_support',
    'public_bundle.inclusion_accessibility',
    'public_bundle.integral_study_support',
    'public_bundle.transport_uniform_bundle',
    'public_bundle.health_emergency_bundle',
    'public_bundle.outings_authorizations',
    'public_bundle.visibility_boundary',
    'public_bundle.permanence_family_support',
    'public_bundle.teacher_directory_boundary',
    'public_bundle.calendar_week',
}

_QUESTION_SUBJECTS = (
    'historia',
    'matematica',
    'portugues',
    'biologia',
    'quimica',
    'fisica',
    'geografia',
    'ingles',
    'english',
    'redacao',
)
_QUESTION_FINANCE_HINTS = ('fatura', 'boleto', 'mensalidade', 'financeiro', 'pagamento', 'valor')
_QUESTION_ATTENDANCE_HINTS = ('frequencia', 'faltas', 'presenca')
_QUESTION_GRADE_HINTS = ('nota', 'notas', 'media', 'média', 'boletim')
_QUESTION_PUBLIC_PRICING_HINTS = ('mensalidade', 'matricula', 'matrícula', 'taxa de matricula', 'taxa de matrícula', 'preco', 'preço')
_QUESTION_PUBLIC_PRICING_STRONG_HINTS = (
    'mensalidade',
    'taxa de matricula',
    'taxa de matrícula',
    'preco',
    'preço',
    'valor',
    'quanto',
    'custa',
    'pagaria',
    'pagar',
    'simulacao',
    'simulação',
    'desconto',
    'descontos',
    'bolsa',
    'bolsas',
)
_EXPLICIT_LIMITATION_HINTS = (
    'na base atual',
    'na resposta atual',
    'na evidência atual',
    'na evidencia atual',
    'nao consigo confirmar',
    'não consigo confirmar',
    'nao encontrei evidencia',
    'não encontrei evidência',
    'nao tenho evidencia',
    'não tenho evidência',
    'nao consigo afirmar',
    'não consigo afirmar',
    'nao detalha',
    'não detalha',
    'nao detalham',
    'não detalham',
    'informacoes disponiveis nao detalham',
    'informações disponíveis não detalham',
)
_GROUNDING_WEAK_HINTS = (
    'nao encontrei base suficiente',
    'não encontrei base suficiente',
    'nao encontrei evidencia suficiente',
    'não encontrei evidência suficiente',
    'nao encontrei informacao suficiente',
    'não encontrei informação suficiente',
    'nao consegui confirmar',
    'não consegui confirmar',
    'nao consegui localizar',
    'não consegui localizar',
    'nao encontrei',
    'não encontrei',
    'nao tenho base suficiente',
    'não tenho base suficiente',
    'nao tenho informacao suficiente',
    'não tenho informação suficiente',
    'nao ha informacao publicada',
    'não há informação publicada',
    'nao foi possivel responder',
    'não foi possível responder',
    'nao detalha',
    'não detalha',
    'nao detalham',
    'não detalham',
)
_SUBJECT_NAMES = (
    'historia',
    'matematica',
    'portugues',
    'biologia',
    'quimica',
    'fisica',
    'geografia',
    'ingles',
    'lingua inglesa',
    'redacao',
    'filosofia',
    'sociologia',
    'educacao fisica',
    'projeto de vida',
)
_QUESTION_TIMEFRAME_HINTS = ('bimestre', 'b1', 'b2', 'b3', 'b4', 'semestre', 'periodo', 'período')
_PUBLIC_TEMPORAL_START_HINTS = (
    'ja comecaram',
    'já começaram',
    'ja começou',
    'já começou',
    'entao as aulas ja comecaram',
    'então as aulas já começaram',
)
_PUBLIC_TEMPORAL_DISTANCE_HINTS = (
    'ta longe',
    'está longe',
    'falta muito',
    'demora ainda',
)
_PUBLIC_NOTIFICATION_HINTS = (
    'me avisa',
    'me avise',
    'vao me avisar',
    'vão me avisar',
    'vai me avisar',
    'quando chegar perto',
)
_PUBLIC_CAPACITY_HINTS = ('vaga', 'vagas')
_PUBLIC_PARKING_HINTS = ('estacionamento', 'vaga de estacionamento', 'vagas de estacionamento')
_PUBLIC_STUDENT_CAPACITY_HINTS = (
    'aluno',
    'alunos',
    'escola',
    'matricula',
    'matrícula',
    'turma',
    'turmas',
    'segmento',
    'segmentos',
    'capacidade',
    'lotacao',
    'lotação',
)
_CAREERS_RESPONSE_HINTS = (
    'trabalhar',
    'dar aula',
    'talentos@',
    'curriculo',
    'currículo',
    'processo seletivo',
    'candidatar',
)
_PT_MONTHS = {
    'janeiro': 1,
    'fevereiro': 2,
    'marco': 3,
    'março': 3,
    'abril': 4,
    'maio': 5,
    'junho': 6,
    'julho': 7,
    'agosto': 8,
    'setembro': 9,
    'outubro': 10,
    'novembro': 11,
    'dezembro': 12,
}
_PASSING_GRADE_TARGET = 7.0


def _csv_values(raw: str | None) -> set[str]:
    return {
        item.strip().lower()
        for item in str(raw or '').split(',')
        if item.strip()
    }


def _conversation_external_id(request: MessageResponseRequest) -> str | None:
    if request.conversation_id:
        return str(request.conversation_id)
    if request.channel == ConversationChannel.telegram and request.telegram_chat_id is not None:
        return f'telegram:{request.telegram_chat_id}'
    return None


def _cached_focus_slot_memory(conversation_external_id: str | None) -> dict[str, Any] | None:
    if not conversation_external_id:
        return None
    entry = _ANSWER_FOCUS_CACHE.get(conversation_external_id)
    if not isinstance(entry, dict):
        return None
    cached_at = float(entry.get('cached_at') or 0.0)
    if cached_at <= 0 or monotonic() - cached_at > _ANSWER_FOCUS_CACHE_TTL_SECONDS:
        _ANSWER_FOCUS_CACHE.pop(conversation_external_id, None)
        return None
    slot_memory = entry.get('slot_memory')
    return dict(slot_memory) if isinstance(slot_memory, dict) and slot_memory else None


def _merge_conversation_context_with_cached_focus(
    conversation_context: dict[str, Any] | None,
    *,
    cached_slot_memory: dict[str, Any] | None,
) -> dict[str, Any] | None:
    if not cached_slot_memory:
        return conversation_context
    context = dict(conversation_context or {})
    recent_tool_calls = list(context.get('recent_tool_calls') or [])
    recent_tool_calls.append(
        {
            'tool_name': 'orchestration.trace',
            'request_payload': {
                'slot_memory': cached_slot_memory,
            },
        }
    )
    context['recent_tool_calls'] = recent_tool_calls
    return context


def _slot_memory_from_focus(focus: AnswerFocusState) -> dict[str, Any]:
    slot_memory: dict[str, Any] = {}
    if focus.domain == 'public' and focus.topic == 'pricing':
        slot_memory['active_task'] = 'public:pricing'
        if focus.public_pricing_segment:
            slot_memory['public_pricing_segment'] = focus.public_pricing_segment
        if focus.public_pricing_grade_year:
            slot_memory['public_pricing_grade_year'] = focus.public_pricing_grade_year
        if focus.public_pricing_quantity:
            slot_memory['public_pricing_quantity'] = focus.public_pricing_quantity
        if focus.public_pricing_price_kind:
            slot_memory['public_pricing_price_kind'] = focus.public_pricing_price_kind
    elif focus.domain == 'academic':
        slot_memory['active_task'] = 'academic:grades' if focus.topic == 'grades' else (
            'academic:upcoming_assessments' if focus.topic == 'upcoming_assessments' else 'academic:attendance'
        )
        if focus.student_name:
            slot_memory['academic_student_name'] = focus.student_name
        if focus.subject_name:
            slot_memory['active_subject'] = focus.subject_name
        if focus.academic_attribute:
            slot_memory['academic_attribute'] = focus.academic_attribute
    elif focus.domain == 'finance':
        slot_memory['active_task'] = 'finance:billing'
        if focus.student_name:
            slot_memory['finance_student_name'] = focus.student_name
        if focus.finance_attribute:
            slot_memory['finance_attribute'] = focus.finance_attribute
        if focus.finance_status_filter:
            slot_memory['finance_status_filter'] = focus.finance_status_filter
    elif focus.domain == 'institution' and focus.topic == 'attendance_justification':
        slot_memory['active_task'] = 'academic:attendance'
        if focus.student_name:
            slot_memory['academic_student_name'] = focus.student_name
    return slot_memory


def _store_focus_cache(*, conversation_external_id: str | None, focus: AnswerFocusState) -> None:
    if not conversation_external_id:
        return
    slot_memory = _slot_memory_from_focus(focus)
    if not slot_memory:
        return
    _ANSWER_FOCUS_CACHE[conversation_external_id] = {
        'cached_at': monotonic(),
        'slot_memory': slot_memory,
    }


def _normalize_text(value: str | None) -> str:
    return ' '.join(str(value or '').split()).strip()


def _plain_text(value: str | None) -> str:
    normalized = unicodedata.normalize('NFKD', _normalize_text(value))
    return ''.join(char for char in normalized if not unicodedata.combining(char)).lower()


def _contains_any(text: str, options: tuple[str, ...]) -> bool:
    normalized = _plain_text(text)
    return any(option in normalized for option in options)


def _public_segment_matches(row_segment: str | None, requested_segment: str | None) -> bool:
    row_plain = _plain_text(row_segment)
    requested_plain = _plain_text(requested_segment)
    if not row_plain or not requested_plain:
        return False
    return row_plain == requested_plain or requested_plain in row_plain or row_plain in requested_plain


def _extract_requested_subject(message: str) -> str | None:
    canonical = explicit_subject_from_message(message)
    if canonical:
        return _focus_normalize_text(canonical)
    normalized = _plain_text(message)
    for subject in _QUESTION_SUBJECTS:
        if re.search(rf'\b(?:nao e|não é|nao eh|não eh)\s+{re.escape(subject)}\b', normalized):
            continue
        if subject in normalized:
            return subject
    return None


def _looks_like_explicit_limitation(text: str) -> bool:
    return _contains_any(text, _EXPLICIT_LIMITATION_HINTS)


def _looks_like_grounding_weakness(text: str) -> bool:
    return _contains_any(text, _GROUNDING_WEAK_HINTS)


def _looks_like_student_resolution_failure(text: str) -> bool:
    normalized = _plain_text(text)
    return (
        'nao encontrei um aluno chamado' in normalized
        or 'nao encontrei nenhum aluno chamado' in normalized
        or ('nao encontrei' in normalized and 'alunos vinculados' in normalized)
    )


def _contains_monetary_signal(text: str) -> bool:
    return bool(re.search(r'(r\$\s*\d)|(\b\d+[.,]\d{2}\b)', _plain_text(text)))


def _extract_recent_user_messages(conversation_context: dict[str, Any] | None) -> list[str]:
    messages: list[str] = []
    if not isinstance(conversation_context, dict):
        return messages
    for item in conversation_context.get('recent_messages', [])[-8:]:
        if not isinstance(item, dict):
            continue
        if str(item.get('sender_type') or '').strip().lower() != 'user':
            continue
        content = _normalize_text(item.get('content'))
        if content:
            messages.append(content)
    return messages


def _extract_recent_assistant_messages(conversation_context: dict[str, Any] | None) -> list[str]:
    messages: list[str] = []
    if not isinstance(conversation_context, dict):
        return messages
    for item in conversation_context.get('recent_messages', [])[-8:]:
        if not isinstance(item, dict):
            continue
        if str(item.get('sender_type') or '').strip().lower() != 'assistant':
            continue
        content = _normalize_text(item.get('content'))
        if content:
            messages.append(content)
    return messages


def _extract_recent_messages(conversation_context: dict[str, Any] | None) -> list[str]:
    recent_messages: list[str] = []
    if not isinstance(conversation_context, dict):
        return recent_messages
    for item in conversation_context.get('recent_messages', [])[-6:]:
        if not isinstance(item, dict):
            continue
        sender_type = str(item.get('sender_type', 'desconhecido')).strip()
        content = _normalize_text(item.get('content'))
        if content:
            recent_messages.append(f'{sender_type}: {content}')
    return recent_messages


def _build_evidence_lines(response: MessageResponse) -> list[str]:
    lines: list[str] = []
    if response.evidence_pack is not None:
        for support in response.evidence_pack.supports[:8]:
            label = _normalize_text(support.label or support.kind)
            detail = _normalize_text(support.detail)
            excerpt = _normalize_text(support.excerpt)
            fragments = [part for part in (label, detail, excerpt) if part]
            if fragments:
                lines.append(' | '.join(fragments))
    for citation in response.citations[:4]:
        excerpt = _normalize_text(citation.excerpt)
        if excerpt:
            lines.append(f'{citation.document_title}: {excerpt}')
    for event in response.calendar_events[:4]:
        detail = _normalize_text(event.description)
        fragments = [event.title, detail, event.starts_at.isoformat()]
        lines.append(' | '.join(part for part in fragments if part))
    if response.evidence_pack is not None and response.evidence_pack.summary:
        lines.append(_normalize_text(response.evidence_pack.summary))
    return [line for line in lines if line][:10]


def _dedupe_preserve_order(values: list[str]) -> list[str]:
    seen: set[str] = set()
    deduped: list[str] = []
    for value in values:
        normalized = _plain_text(value)
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        deduped.append(value)
    return deduped


def _parse_iso_date_text(value: Any) -> date | None:
    text = _normalize_text(value)
    if not text:
        return None
    try:
        return date.fromisoformat(text[:10])
    except ValueError:
        dates = _extract_dates_from_text(text)
        return dates[0] if dates else None


def _academic_subject_averages_from_summary(summary: dict[str, Any]) -> list[tuple[str, float]]:
    grades = summary.get('grades')
    if not isinstance(grades, list):
        return []
    grouped: dict[str, list[float]] = {}
    display_names: dict[str, str] = {}
    for grade in grades:
        if not isinstance(grade, dict):
            continue
        subject_name = str(grade.get('subject_name') or '').strip()
        if not subject_name:
            continue
        try:
            score = float(grade.get('score', 0) or 0)
            max_score = float(grade.get('max_score', 0) or 0)
        except (TypeError, ValueError):
            continue
        normalized_score = score if max_score <= 0 else (score / max_score) * 10.0
        subject_key = _plain_text(subject_name)
        grouped.setdefault(subject_key, []).append(normalized_score)
        display_names[subject_key] = subject_name
    averages: list[tuple[str, float]] = []
    for subject_key, scores in grouped.items():
        if scores:
            averages.append((display_names[subject_key], sum(scores) / len(scores)))
    averages.sort(key=lambda item: item[0])
    return averages


def _compose_family_academic_focus(summaries: list[dict[str, Any]]) -> str | None:
    if not summaries:
        return None
    lines = ['Panorama academico das contas vinculadas:']
    highest_risk_student_name: str | None = None
    highest_risk_subject_name: str | None = None
    highest_risk_signature: tuple[int, float, str] | None = None
    for summary in summaries:
        student_name = str(summary.get('student_name') or 'Aluno').strip() or 'Aluno'
        averages = _academic_subject_averages_from_summary(summary)
        if not averages:
            lines.append(f'- {student_name}: sem notas consolidadas neste recorte.')
            continue
        preview_items = averages[:4]
        preview = '; '.join(f'{name} {value:.1f}'.replace('.', ',') for name, value in preview_items)
        lines.append(f'- {student_name}: {preview}')
        below_target = [(name, value) for name, value in averages if value < _PASSING_GRADE_TARGET]
        if below_target:
            candidate_subject, candidate_value = min(
                below_target,
                key=lambda item: (item[1], _plain_text(item[0])),
            )
            signature = (1, _PASSING_GRADE_TARGET - candidate_value, student_name)
        else:
            candidate_subject, candidate_value = min(
                averages,
                key=lambda item: (abs(item[1] - _PASSING_GRADE_TARGET), _plain_text(item[0])),
            )
            signature = (0, _PASSING_GRADE_TARGET - candidate_value, student_name)
        if highest_risk_signature is None or signature > highest_risk_signature:
            highest_risk_signature = signature
            highest_risk_student_name = student_name
            highest_risk_subject_name = candidate_subject
    if highest_risk_student_name and highest_risk_subject_name:
        lines.append(
            'Quem hoje exige maior atencao academica e '
            f'{highest_risk_student_name}, principalmente em {highest_risk_subject_name}.'
        )
    return '\n'.join(lines)


def _compose_academic_risk_direct_answer(summary: dict[str, Any], *, student_name: str) -> str | None:
    averages = _academic_subject_averages_from_summary(summary)
    if not averages:
        return None
    prioritized = sorted(averages, key=lambda item: (item[1], _plain_text(item[0])))[:4]
    lines = [f'Os pontos academicos que mais preocupam em {student_name} hoje sao:']
    for subject_name, value in prioritized:
        lines.append(f'- {subject_name}: media parcial {value:.1f}'.replace('.', ','))
    return '\n'.join(lines)


def _compose_academic_difficulty_direct_answer(summary: dict[str, Any], *, student_name: str) -> str | None:
    averages = sorted(_academic_subject_averages_from_summary(summary), key=lambda item: (item[1], _plain_text(item[0])))
    if not averages:
        return None
    subject_name, value = averages[0]
    answer = (
        f'Hoje, a disciplina em que {student_name} aparece com a menor media parcial e {subject_name}, '
        f'com {value:.1f}/10.'
    ).replace('.', ',')
    trailing = ', '.join(f'{name} {grade:.1f}'.replace('.', ',') for name, grade in averages[1:3])
    if trailing:
        answer += f' Na sequencia aparecem {trailing}.'
    return answer


def _family_academic_ranking(summaries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    ranked: list[dict[str, Any]] = []
    for summary in summaries:
        student_name = str(summary.get('student_name') or 'Aluno').strip() or 'Aluno'
        averages = _academic_subject_averages_from_summary(summary)
        if not averages:
            continue
        below_target = [(name, value) for name, value in averages if value < _PASSING_GRADE_TARGET]
        if below_target:
            subject_name, value = min(
                below_target,
                key=lambda item: (item[1], _plain_text(item[0])),
            )
            signature = (1, _PASSING_GRADE_TARGET - value, student_name)
        else:
            subject_name, value = min(
                averages,
                key=lambda item: (abs(item[1] - _PASSING_GRADE_TARGET), _plain_text(item[0])),
            )
            signature = (0, _PASSING_GRADE_TARGET - value, student_name)
        ranked.append(
            {
                'student_name': student_name,
                'subject_name': subject_name,
                'value': value,
                'signature': signature,
                'below_target': value < _PASSING_GRADE_TARGET,
            }
        )
    ranked.sort(key=lambda item: item['signature'], reverse=True)
    return ranked


def _looks_like_family_academic_reason_followup(question: str) -> bool:
    normalized = _plain_text(question)
    return any(
        term in normalized
        for term in (
            'principal motivo desse alerta',
            'motivo desse alerta',
            'por que esse alerta',
            'porque esse alerta',
        )
    )


def _looks_like_family_academic_next_in_line_followup(question: str) -> bool:
    normalized = _plain_text(question)
    return any(
        term in normalized
        for term in (
            'logo depois dele',
            'quem vem na fila',
            'quem vem logo depois',
            'quem vem depois dele',
            'quem vem logo depois dele',
        )
    )


def _looks_like_family_academic_priority_followup(question: str) -> bool:
    normalized = _plain_text(question)
    if not any(
        term in normalized
        for term in (
            'academicamente',
            'academico',
            'acadêmico',
            'media minima',
            'média mínima',
            'mais critico',
            'mais crítico',
            'mais perto da media minima',
            'mais perto da média mínima',
        )
    ):
        return False
    return any(
        term in normalized
        for term in (
            'quem esta',
            'quem está',
            'quem dos dois',
            'qual dos dois',
            'qual dos meus filhos',
            'quem hoje',
            'mais critico',
            'mais crítico',
            'mais perto da media minima',
            'mais perto da média mínima',
        )
    )


def _compose_family_academic_alert_reason(summaries: list[dict[str, Any]]) -> str | None:
    ranked = _family_academic_ranking(summaries)
    if not ranked:
        return None
    top = ranked[0]
    student_name = str(top['student_name'])
    subject_name = str(top['subject_name'])
    value = float(top['value'])
    value_text = f'{value:.1f}'.replace('.', ',')
    if bool(top['below_target']):
        return (
            f'O principal motivo do alerta e {student_name} aparecer abaixo da media minima em '
            f'{subject_name}, com media parcial {value_text}/10 neste recorte.'
        )
    return (
        f'O principal motivo do alerta e {student_name} aparecer hoje mais perto da media minima em '
        f'{subject_name}, com media parcial {value_text}/10 neste recorte.'
    )


def _compose_family_academic_next_in_line(summaries: list[dict[str, Any]]) -> str | None:
    ranked = _family_academic_ranking(summaries)
    if len(ranked) < 2:
        return None
    item = ranked[1]
    student_name = str(item['student_name'])
    subject_name = str(item['subject_name'])
    value_text = f"{float(item['value']):.1f}".replace('.', ',')
    return (
        f'Logo depois dele vem {student_name}, principalmente em {subject_name}, '
        f'com media parcial {value_text}/10 neste recorte.'
    )


def _select_next_due_invoice_for_focus(summary: dict[str, Any]) -> dict[str, Any] | None:
    invoices = summary.get('invoices')
    if not isinstance(invoices, list):
        return None
    candidates = [
        item for item in invoices
        if isinstance(item, dict) and str(item.get('status') or '').strip().lower() in {'open', 'overdue'}
    ]
    if not candidates:
        return None
    candidates.sort(
        key=lambda item: (
            _parse_iso_date_text(item.get('due_date')) is None,
            _parse_iso_date_text(item.get('due_date')) or date.max,
            str(item.get('reference_month') or ''),
        )
    )
    return candidates[0]


def _compose_family_finance_focus(summaries: list[dict[str, Any]]) -> str | None:
    if not summaries:
        return None
    lines = ['Resumo financeiro das contas vinculadas:']
    total_open = 0
    total_overdue = 0
    for summary in summaries:
        student_name = str(summary.get('student_name') or 'Aluno').strip() or 'Aluno'
        open_count = int(summary.get('open_invoice_count', 0) or 0)
        overdue_count = int(summary.get('overdue_invoice_count', 0) or 0)
        total_open += open_count
        total_overdue += overdue_count
        next_invoice = _select_next_due_invoice_for_focus(summary)
        details = [f'{open_count} em aberto', f'{overdue_count} vencida(s)']
        if isinstance(next_invoice, dict):
            due_date = _parse_iso_date_text(next_invoice.get('due_date'))
            amount = str(next_invoice.get('amount_due') or '0.00').strip() or '0.00'
            details.append(
                f'proximo vencimento {_format_full_date_br(due_date) if due_date else "data nao informada"} ({amount})'
            )
        lines.append(f"- {student_name}: {', '.join(details)}.")
    lines.insert(1, f'- Total de faturas em aberto: {total_open}')
    lines.insert(2, f'- Total de faturas vencidas: {total_overdue}')
    if total_open or total_overdue:
        lines.append(
            f'- Mensalidade: neste recorte, o financeiro mostra {total_open} cobranca(s) em aberto e {total_overdue} vencida(s) nas faturas escolares.'
        )
        lines.append('- Taxa: nao apareceu taxa separada no resumo financeiro desta conta.')
        lines.append(
            '- Atraso: '
            + (
                'ha faturas vencidas que pedem regularizacao imediata.'
                if total_overdue > 0
                else 'nao ha fatura vencida agora; o foco fica nos proximos vencimentos.'
            )
        )
        lines.append(
            '- Desconto: nao apareceu desconto separado nas faturas deste recorte; se existir negociacao comercial, ela precisa ser confirmada com o financeiro.'
        )
    if total_overdue > 0:
        lines.append(
            '- Proximo passo recomendado: priorizar as faturas vencidas e, se necessario, acionar o financeiro para alinhamento imediato.'
        )
    elif total_open > 0:
        lines.append(
            '- Proximo passo recomendado: acompanhar os vencimentos mais proximos e manter os comprovantes em dia.'
        )
    else:
        lines.append(
            '- Proximo passo recomendado: manter comprovantes organizados e acompanhar apenas os proximos vencimentos do calendario financeiro.'
        )
    return '\n'.join(lines)


def _attendance_totals_for_focus(summary: dict[str, Any]) -> tuple[int, int, int, int]:
    attendance = summary.get('attendance')
    if not isinstance(attendance, list):
        return 0, 0, 0, 0
    present = late = absent = minutes = 0
    for row in attendance:
        if not isinstance(row, dict):
            continue
        present += int(row.get('present_count', 0) or 0)
        late += int(row.get('late_count', 0) or 0)
        absent += int(row.get('absent_count', 0) or 0)
        minutes += int(row.get('absent_minutes', 0) or 0)
    return present, late, absent, minutes


def _attendance_priority_rows_for_focus(summary: dict[str, Any]) -> list[dict[str, Any]]:
    attendance = summary.get('attendance')
    if not isinstance(attendance, list):
        return []
    rows = [row for row in attendance if isinstance(row, dict)]
    rows.sort(
        key=lambda row: (
            -(int(row.get('absent_count', 0) or 0)),
            -(int(row.get('late_count', 0) or 0)),
            -(int(row.get('absent_minutes', 0) or 0)),
            _plain_text(str(row.get('subject_name', ''))),
        )
    )
    return rows


def _compose_family_attendance_focus(summaries: list[dict[str, Any]]) -> str | None:
    if not summaries:
        return None
    lines = ['Panorama de faltas e frequencia das contas vinculadas:']
    strongest_name: str | None = None
    strongest_focus: str | None = None
    strongest_signature: tuple[int, int, int, int] | None = None
    for summary in summaries:
        student_name = str(summary.get('student_name') or 'Aluno').strip() or 'Aluno'
        present, late, absent, minutes = _attendance_totals_for_focus(summary)
        top_row = next(iter(_attendance_priority_rows_for_focus(summary)), None)
        line = (
            f'- {student_name}: {absent} falta(s), {late} atraso(s), '
            f'{present} presenca(s), {minutes} minuto(s) de ausencia.'
        )
        subject_name = None
        if isinstance(top_row, dict):
            subject_name = str(top_row.get('subject_name') or 'disciplina').strip() or 'disciplina'
            subject_absent = int(top_row.get('absent_count', 0) or 0)
            subject_late = int(top_row.get('late_count', 0) or 0)
            line += (
                f' Ponto mais sensivel: {subject_name} '
                f'({subject_absent} falta(s), {subject_late} atraso(s)).'
            )
        lines.append(line)
        signature = (absent, late, minutes, -present)
        if strongest_signature is None or signature > strongest_signature:
            strongest_signature = signature
            strongest_name = student_name
            strongest_focus = subject_name
    if strongest_name:
        closing = f'Quem exige maior atencao agora: {strongest_name}.'
        if strongest_focus:
            closing += f' O ponto mais sensivel aparece em {strongest_focus}.'
        lines.append(closing)
    return '\n'.join(lines)


def _actor_summary(actor: dict[str, Any] | None) -> str:
    if not isinstance(actor, dict):
        return 'sem contexto autenticado adicional'
    linked = actor.get('linked_students')
    if not isinstance(linked, list) or not linked:
        return 'sem alunos vinculados no contexto'
    names = [str(item.get('full_name') or '').strip() for item in linked if isinstance(item, dict)]
    names = [name for name in names if name]
    if not names:
        return 'sem alunos vinculados nomeados'
    return f"alunos_vinculados={', '.join(names[:4])}"


_FINANCE_STUDENT_REFERENCE_STOPWORDS = {
    'mensalidade',
    'mensalidades',
    'pagamento',
    'pagamentos',
    'taxa',
    'taxas',
    'desconto',
    'descontos',
    'atraso',
    'atrasos',
    'restante',
    'financeiro',
    'fatura',
    'faturas',
    'boleto',
    'boletos',
    'atendimento',
    'atendimento humano',
    'impedimento',
    'bloqueio',
}


def _explicit_unmatched_finance_student_reference(
    actor: dict[str, Any] | None,
    message: str,
) -> str | None:
    linked_students = actor.get('linked_students') if isinstance(actor, dict) else None
    if not isinstance(linked_students, list) or not linked_students:
        return None
    normalized = _plain_text(message)
    if not any(term in normalized for term in ('mensalidade', 'financeiro', 'fatura', 'boleto', 'pagamento', 'negociar')):
        return None
    known_names = {
        _plain_text(str(student.get('full_name') or ''))
        for student in linked_students
        if isinstance(student, dict)
    }
    known_first_names = {name.split(' ')[0] for name in known_names if name}
    for pattern in (
        r"\b(?:da|do|de|para|pro|pra)\s+([a-z]{3,}(?:\s+[a-z]{3,})?)\b",
        r"\b(?:aluno|aluna|estudante)\s+([a-z]{3,}(?:\s+[a-z]{3,})?)\b",
    ):
        for match in re.finditer(pattern, normalized):
            candidate = _plain_text(match.group(1))
            if not candidate or candidate in _FINANCE_STUDENT_REFERENCE_STOPWORDS:
                continue
            if any(candidate.startswith(stopword) for stopword in _FINANCE_STUDENT_REFERENCE_STOPWORDS):
                continue
            if candidate in known_names or candidate in known_first_names:
                continue
            return candidate
    return None


def _compose_family_admin_focus(summaries: list[dict[str, Any]]) -> str | None:
    if not summaries:
        return None
    lines = ['Panorama documental das contas vinculadas:']
    pending_students: list[str] = []
    for summary in summaries:
        student_name = str(summary.get('student_name') or 'Aluno').strip() or 'Aluno'
        overall_status = str(summary.get('overall_status') or '').strip().lower()
        next_step = str(summary.get('next_step') or '').strip()
        pending_note = ''
        checklist = summary.get('checklist')
        if isinstance(checklist, list):
            for item in checklist:
                if not isinstance(item, dict):
                    continue
                if str(item.get('status') or '').strip().lower() == 'pending':
                    pending_note = str(item.get('notes') or '').strip()
                    break
        status_label = 'regular'
        if overall_status in {'pending', 'review', 'missing', 'incomplete'}:
            status_label = 'com pendencias'
            pending_students.append(student_name)
        elif overall_status:
            status_label = overall_status
        line = f'- {student_name}: situacao documental {status_label}.'
        if pending_note:
            line += f' Ponto pendente: {pending_note}'
        if next_step:
            line += f' Proximo passo: {next_step}'
        lines.append(line)
    if pending_students:
        if len(pending_students) == 1:
            lines.append(f'Quem ainda tem pendencia documental mais clara neste recorte: {pending_students[0]}.')
        else:
            lines.append('Quem ainda aparece com pendencia documental neste recorte: ' + ', '.join(pending_students) + '.')
    else:
        lines.append('Hoje nao aparece pendencia documental relevante entre os alunos vinculados neste recorte.')
    return '\n'.join(lines)


def _question_mentions_unasked_grade_scope(question: str) -> bool:
    return _contains_any(question, _QUESTION_GRADE_HINTS) or _extract_requested_subject(question) is not None


def _question_mentions_unasked_finance_scope(question: str) -> bool:
    return _contains_any(question, _QUESTION_FINANCE_HINTS)


def _question_mentions_unasked_attendance_scope(question: str) -> bool:
    return _contains_any(question, _QUESTION_ATTENDANCE_HINTS)


def _question_requests_operational_public_synthesis(question: str) -> bool:
    normalized = _plain_text(question)
    return any(
        term in normalized
        for term in (
            'na pratica',
            'de forma concreta',
            'forma concreta',
            'objetivo e grounded',
            'objetivo e grounded',
            'qual ordem',
            'em ordem',
            'ordem evita retrabalho',
            'sem se perder',
            'como se distribuem',
            'como a familia acompanha',
            'como a família acompanha',
            'de que forma',
            'o que fazer',
            'como usar',
            'proximo passo',
            'próximo passo',
        )
    )


def _response_has_operational_actionability(answer: str) -> bool:
    normalized = _plain_text(answer)
    return any(
        term in normalized
        for term in (
            'primeiro',
            'depois',
            'em seguida',
            'por fim',
            'proximo passo',
            'próximo passo',
            'passo a passo',
            'se a familia',
            'se a família',
            'se a necessidade',
            'se o foco',
            'confirma',
            'confirme',
            'valida',
            'valide',
            'aciona',
            'acione',
            'acompanha',
            'acompanhe',
        )
    )


def _question_mentions_upcoming_scope(question: str) -> bool:
    return any(term in _plain_text(question) for term in ('prova', 'avaliac', 'entrega'))


def _question_mentions_public_pricing_scope(question: str) -> bool:
    normalized = _plain_text(question)
    if any(term in normalized for term in _QUESTION_PUBLIC_PRICING_STRONG_HINTS):
        return True
    if any(term in normalized for term in ('matricula', 'matrícula')):
        return any(
            term in normalized
            for term in (
                'taxa',
                'mensalidade',
                'valor',
                'preco',
                'preço',
                'quanto',
                'custa',
                'pagaria',
                'pagar',
                'simulacao',
                'simulação',
                'desconto',
                'descontos',
                'bolsa',
                'bolsas',
                'filhos',
                'criancas',
                'crianças',
            )
        )
    return False


def _looks_like_explicit_public_pricing_projection(question: str) -> bool:
    normalized = _plain_text(question)
    if not _question_mentions_public_pricing_scope(normalized):
        return False
    has_quantity = bool(re.search(r'\b\d+\b', normalized)) or 'filhos' in normalized or 'criancas' in normalized or 'crianças' in normalized
    has_projection = any(
        phrase in normalized
        for phrase in ('quanto eu pagaria', 'quanto daria', 'quanto ficaria', 'quanto sairia', 'para ')
    )
    return has_quantity and has_projection


def _looks_like_family_attendance_aggregate_request(question: str) -> bool:
    normalized = _plain_text(question)
    explicit_terms = (
        'resumo de frequencia dos meus dois filhos',
        'resumo de frequência dos meus dois filhos',
        'resumo de frequencia dos meus filhos',
        'resumo de frequência dos meus filhos',
        'panorama de faltas e frequencia',
        'panorama de faltas e frequência',
        'faltas e frequencia dos meus filhos',
        'faltas e frequência dos meus filhos',
        'frequencia dos meus filhos',
        'frequência dos meus filhos',
        'frequencia dos meus dois filhos',
        'frequência dos meus dois filhos',
        'frequencia dos alunos vinculados',
        'frequência dos alunos vinculados',
        'quem exige maior atencao agora',
        'quem exige maior atenção agora',
        'quem exige mais atencao agora',
        'quem exige mais atenção agora',
        'quem inspira mais atencao',
        'quem inspira mais atenção',
        'principal alerta de frequencia dos meus filhos',
        'principal alerta de frequência dos meus filhos',
    )
    if any(term in normalized for term in explicit_terms):
        return True
    named_comparison = (
        'entre ' in normalized
        and any(
            term in normalized
            for term in (
                'quem esta mais delicado por frequencia',
                'quem está mais delicado por frequência',
                'mais delicado por frequencia',
                'mais delicado por frequência',
                'frequencia hoje',
                'frequência hoje',
                'alerta pesa mais',
            )
        )
    )
    if named_comparison:
        return True
    has_family_anchor = any(
        term in normalized
        for term in (
            'meus dois filhos',
            'dos meus dois filhos',
            'meus filhos',
            'minha familia',
            'meus alunos vinculados',
            'alunos vinculados',
            'contas vinculadas',
        )
    )
    has_attendance_focus = any(term in normalized for term in ('frequencia', 'frequência', 'faltas', 'falta', 'atrasos', 'presenca', 'presença', 'ausencias', 'ausências'))
    has_explicit_academic_focus = any(
        term in normalized
        for term in (
            'componente',
            'componentes',
            'disciplina',
            'disciplinas',
            'materia',
            'materias',
            'nota',
            'notas',
            'media',
            'média',
            'academico',
            'acadêmico',
        )
    )
    has_explicit_finance_focus = any(
        term in normalized
        for term in (
            'financeiro',
            'financeira',
            'situacao financeira',
            'situação financeira',
            'mensalidade',
            'mensalidades',
            'boleto',
            'boletos',
            'fatura',
            'faturas',
            'pagamento',
            'pagamentos',
            'vencimento',
            'vencimentos',
            'proximos passos',
            'próximos passos',
            'comprovantes',
        )
    )
    has_non_ambiguous_attendance_focus = any(
        term in normalized
        for term in ('frequencia', 'frequência', 'faltas', 'falta', 'presenca', 'presença', 'ausencias', 'ausências')
    )
    has_attention_focus = any(
        term in normalized
        for term in (
            'quem inspira mais atencao',
            'quem inspira mais atenção',
            'quem exige maior atencao',
            'quem exige maior atenção',
            'quem exige mais atencao',
            'quem exige mais atenção',
            'maior atencao',
            'maior atenção',
            'mais atencao',
            'mais atenção',
            'principal alerta',
        )
    )
    if has_explicit_academic_focus and not has_attendance_focus:
        return False
    if has_explicit_finance_focus and not has_non_ambiguous_attendance_focus:
        return False
    return has_family_anchor and (has_attendance_focus or has_attention_focus)


def _looks_like_family_finance_aggregate_request(question: str) -> bool:
    normalized = _plain_text(question)
    explicit_terms = (
        'como esta o financeiro da familia',
        'como está o financeiro da família',
        'como estao meus pagamentos',
        'como estão meus pagamentos',
        'meus pagamentos',
        'meus boletos',
        'situacao financeira da familia',
        'situação financeira da família',
        'situacao financeira atual da familia',
        'situação financeira atual da família',
        'resuma a situacao financeira',
        'resuma a situação financeira',
        'resumo financeiro da familia',
        'resumo financeiro da família',
        'financeiro da familia',
        'financeiro da família',
        'financeiro da familia hoje',
        'financeiro da família hoje',
        'quadro financeiro da familia',
        'quadro financeiro da família',
        'contas vinculadas',
        'minha situacao financeira',
        'minha situação financeira',
        'situacao financeira como se eu fosse leigo',
        'situação financeira como se eu fosse leigo',
        'separando mensalidade, taxa, atraso e desconto',
        'separando mensalidade taxa atraso e desconto',
    )
    if any(term in normalized for term in explicit_terms):
        return True
    has_family_anchor = any(
        term in normalized
        for term in (
            'meus filhos',
            'meus dois filhos',
            'minha familia',
            'minha família',
            'familia',
            'família',
            'contas vinculadas',
            'alunos vinculados',
        )
    )
    has_finance_focus = any(
        term in normalized
        for term in (
            'financeiro',
            'pagamentos',
            'boletos',
            'faturas',
            'vencimentos',
            'atrasos',
            'proximos passos',
            'próximos passos',
        )
    )
    if has_family_anchor and any(
        term in normalized
        for term in (
            'mensalidade parcialmente paga',
            'negociar o restante',
            'o que ja aparece',
            'o que já aparece',
            'taxa',
            'atraso',
            'desconto',
        )
    ):
        return True
    return has_family_anchor and has_finance_focus


def _looks_like_access_scope_request(question: str) -> bool:
    normalized = _plain_text(question)
    phrases = (
        'estou autenticado',
        'como quem',
        'qual escopo',
        'o que consigo ver',
        'que consigo ver',
        'qual acesso',
        'que acesso',
        'alunos vinculados',
        'esta conta',
        'essa conta',
    )
    if any(phrase in normalized for phrase in phrases):
        return True
    has_scope_anchor = any(
        phrase in normalized
        for phrase in ('escopo', 'acesso', 'dados', 'consigo acessar', 'posso acessar', 'meu acesso')
    )
    has_account_reference = any(
        phrase in normalized
        for phrase in ('meus filhos', 'meus alunos', 'meus dois alunos', 'por aqui', 'conta')
    )
    has_scope_dimension = any(
        phrase in normalized
        for phrase in ('academico', 'acadêmico', 'financeiro', 'os dois')
    )
    return has_scope_anchor and has_account_reference and has_scope_dimension


def _question_mentions_timeframe_scope(question: str) -> bool:
    return _contains_any(question, _QUESTION_TIMEFRAME_HINTS)


def _looks_like_relationship_followup(question: str) -> bool:
    normalized = _plain_text(question)
    return (
        'como isso se conecta' in normalized
        or 'isso se conecta' in normalized
        or 'como isso se relaciona' in normalized
        or 'como se conecta' in normalized
        or ('e ' in normalized[:4] and 'conecta' in normalized)
    )


def _response_covers_requested_scope(question: str, response_text: str) -> bool:
    question_plain = _plain_text(question)
    response_plain = _plain_text(response_text)
    if (
        any(term in response_plain for term in ('para qual aluno', 'qual aluno', 'voce quer consultar', 'você quer consultar'))
        and any(term in response_plain for term in (' ou ', 'vinculado a esta conta', 'vinculados a esta conta'))
    ):
        return False
    if any(term in question_plain for term in ('bloqueando atendimento', 'nada estiver bloqueando', 'se nada estiver bloqueando', 'bloqueio')):
        if not any(term in response_plain for term in ('bloqueio', 'administrativo', 'documental', 'financeiro por atraso')):
            return False
    timeline_groups = (
        ('matricula', 'matrícula', 'ingresso'),
        ('inicio das aulas', 'início das aulas', 'inicio do ano letivo', 'início do ano letivo'),
        ('reuniao com responsaveis', 'reunião com responsáveis', 'reuniao de pais', 'reunião de pais', 'reuniao de responsaveis'),
    )
    requested_timeline_groups = sum(
        1 for group in timeline_groups if any(term in question_plain for term in group)
    )
    if requested_timeline_groups >= 2:
        covered_timeline_groups = sum(
            1 for group in timeline_groups if any(term in response_plain for term in group)
        )
        if covered_timeline_groups < 2:
            return False
    policy_groups = (
        ('avaliac',),
        ('recuper',),
        ('promo',),
        ('media', 'média'),
        ('frequenc',),
    )
    requested_policy_groups = sum(
        1 for group in policy_groups if any(term in question_plain for term in group)
    )
    if requested_policy_groups >= 3:
        covered_policy_groups = sum(
            1 for group in policy_groups if any(term in response_plain for term in group)
        )
        if covered_policy_groups < 2:
            return False
    if _question_mentions_unasked_finance_scope(question_plain):
        if not (_contains_monetary_signal(response_text) or any(term in response_plain for term in ('fatura', 'boleto', 'financeiro'))):
            return False
    if _looks_like_family_finance_aggregate_request(question_plain):
        if not any(
            term in response_plain
            for term in ('resumo financeiro', 'contas vinculadas', 'fatura', 'boleto', 'vencimento', 'em aberto', 'vencida')
        ):
            return False
    if (
        any(term in question_plain for term in ('documentacao dos meus filhos', 'documentação dos meus filhos', 'pendencia documental', 'pendência documental'))
        or (
            any(term in question_plain for term in ('meus filhos', 'meus dois filhos', 'alunos vinculados'))
            and any(term in question_plain for term in ('documentacao', 'documentação', 'documental', 'pendencia', 'pendência', 'cadastro'))
        )
    ):
        if not any(
            term in response_plain
            for term in ('document', 'cadastro', 'administrativ', 'pendenc', 'comprovante', 'regular')
        ):
            return False
    if _question_mentions_unasked_grade_scope(question_plain):
        requested_subject = _extract_requested_subject(question)
        if requested_subject and requested_subject in response_plain:
            return True
        if not any(term in response_plain for term in ('nota', 'media', 'média')):
            return False
    if _question_mentions_unasked_attendance_scope(question_plain):
        if not any(term in response_plain for term in ('frequ', 'falta', 'presen', 'atraso')):
            return False
    if _question_mentions_upcoming_scope(question_plain):
        if not any(term in response_plain for term in ('prova', 'avaliac', 'entrega')):
            return False
    if _question_mentions_public_pricing_scope(question_plain):
        if not any(term in response_plain for term in ('mensalidade', 'matricula', 'matrícula', 'taxa', 'r$')):
            return False
    if _question_mentions_timeframe_scope(question_plain):
        if not any(term in response_plain for term in ('b1', 'b2', 'b3', 'b4', 'bimestre', 'semestre', 'periodo', 'período')):
            return False
    return True


def _looks_like_service_routing_bundle_request(question: str) -> bool:
    question_plain = _plain_text(question)
    has_channel_language = any(
        marker in question_plain
        for marker in (
            'por qual canal',
            'qual canal',
            'como falar',
            'como eu falo',
            'contato',
            'contatar',
            'setores',
            'canais',
            'setor de bolsas',
            'quem responde por',
            'quem cuida',
            'quem resolve',
            'menu geral',
            'caminho mais curto',
            'por cada frente',
        )
    )
    has_target_sector = sum(
        1
        for marker in ('bolsa', 'financeiro', 'direcao', 'direção')
        if marker in question_plain
    )
    return has_channel_language and has_target_sector >= 2


def _looks_like_service_routing_followup(question: str, conversation_context: dict[str, Any] | None) -> bool:
    normalized = _plain_text(question)
    if not any(
        term in normalized
        for term in (
            'contatos da secretaria',
            'contatos do financeiro',
            'contato da secretaria',
            'contato do financeiro',
            'contatos',
            'contato',
            'uma linha por setor',
            'me diga so os canais',
            'me diga só os canais',
            'canais de',
            'qual desses setores entra primeiro',
            'entra primeiro',
        )
    ):
        return False
    recent_blob = ' '.join(
        _plain_text(item)
        for item in (
            _extract_recent_user_messages(conversation_context)
            + _extract_recent_assistant_messages(conversation_context)
        )[-6:]
    )
    return any(
        term in recent_blob
        for term in (
            'bolsa',
            'financeiro',
            'secretaria',
            'direcao',
            'direção',
            'atendimento comercial',
            'admissoes',
            'admissoes',
        )
    )


def _service_routing_sector_hits(text: str) -> int:
    normalized = _plain_text(text)
    groups = (
        ('atendimento comercial / admissoes', 'admissoes', 'admissoes', 'bolsa', 'bolsas', 'desconto', 'descontos'),
        ('financeiro', 'fatura', 'faturas', 'boleto', 'boletos', 'mensalidade', 'mensalidades'),
        ('direcao', 'direção', 'diretora', 'diretor'),
        ('secretaria', 'documentos', 'declaração', 'declaracao'),
        ('orientacao educacional', 'orientação educacional', 'convivencia', 'convivência', 'bullying'),
    )
    return sum(1 for group in groups if any(term in normalized for term in group))


def _compose_public_service_routing_direct_answer(
    school_profile: dict[str, Any] | None,
    *,
    message: str,
    conversation_context: dict[str, Any] | None,
) -> str | None:
    if not isinstance(school_profile, dict):
        return None
    catalog = school_profile.get('service_catalog')
    if not isinstance(catalog, list):
        return None
    catalog_index = {
        str(item.get('service_key') or '').strip(): item
        for item in catalog
        if isinstance(item, dict) and str(item.get('service_key') or '').strip()
    }
    recent_blob = ' '.join(
        _normalize_text(item)
        for item in (
            _extract_recent_user_messages(conversation_context)
            + _extract_recent_assistant_messages(conversation_context)
        )[-6:]
    )
    normalized = _plain_text(f'{message} {recent_blob}')
    wants_one_line = any(
        term in normalized
        for term in (
            'uma linha por setor',
            'me diga so os canais',
            'me diga só os canais',
            'so os canais',
            'só os canais',
            'seja objetivo',
            'nao me manda menu geral',
            'não me manda menu geral',
            'caminho mais curto',
            'nao a lista completa',
            'não a lista completa',
        )
    )
    wants_priority = any(
        term in normalized
        for term in (
            'qual desses setores entra primeiro',
            'quem entra primeiro',
            'setor entra primeiro',
            'entra primeiro',
        )
    )
    has_documental_pending = any(
        term in normalized
        for term in (
            'documento pendente',
            'documentacao pendente',
            'documentação pendente',
            'pendencia documental',
            'pendência documental',
        )
    )
    requested: list[tuple[str, str]] = []
    if any(term in normalized for term in ('bolsa', 'bolsas', 'desconto', 'descontos', 'matricula', 'matrícula', 'admissoes', 'admissoes', 'atendimento comercial')):
        requested.append(('atendimento_admissoes', 'Atendimento comercial / Admissoes'))
    if any(term in normalized for term in ('financeiro', 'boleto', 'boletos', 'fatura', 'faturas', 'mensalidade', 'mensalidades')):
        requested.append(('financeiro_escolar', 'Financeiro'))
    if any(term in normalized for term in ('direcao', 'direção', 'diretora', 'diretor')):
        requested.append(('solicitacao_direcao', 'Direcao'))
    if any(term in normalized for term in ('bullying', 'orientacao educacional', 'orientação educacional', 'convivencia', 'convivência', 'socioemocional')):
        requested.append(('orientacao_educacional', 'Orientacao educacional'))
    if any(term in normalized for term in ('secretaria', 'documentos', 'declaracao', 'declaração', 'atualizacao cadastral', 'atualização cadastral')):
        requested.append(('secretaria_escolar', 'Secretaria'))
    if not requested:
        return None
    lines: list[str] = []
    labels_in_order: list[str] = []
    if any(service_key == 'solicitacao_direcao' for service_key, _ in requested):
        leadership = school_profile.get('leadership_team')
        if isinstance(leadership, list):
            member = next((item for item in leadership if isinstance(item, dict)), None)
            if isinstance(member, dict):
                title = str(member.get('title') or 'Direcao geral').strip() or 'Direcao geral'
                name = str(member.get('name') or '').strip()
                contact_channel = str(member.get('contact_channel') or '').strip()
                if name and contact_channel:
                    lines.append(f'- {title}: {name}. Canal institucional: {contact_channel}.')
                    labels_in_order.append('Direcao')
    for service_key, label in requested:
        item = catalog_index.get(service_key)
        if not isinstance(item, dict):
            continue
        request_channel = str(item.get('request_channel') or 'canal institucional').strip()
        line = f'- {label}: {request_channel}.'
        if line not in lines:
            lines.append(line)
        labels_in_order.append(label)
    if not lines:
        return None
    if wants_priority:
        if 'Atendimento comercial / Admissoes' in labels_in_order and has_documental_pending:
            return (
                'Se o tema for bolsa com documento pendente, o primeiro setor que entra e Atendimento comercial / '
                'Admissoes. Depois, se houver impacto em contrato ou cobranca, entra o Financeiro. '
                'A Direcao fica como escalonamento institucional se o caso sair da rotina normal.'
            )
        return f'Desses setores, o primeiro passo hoje e {labels_in_order[0]}.'
    if wants_one_line:
        return '\n'.join(lines)
    return '\n'.join(['Hoje estes sao os responsaveis e canais mais diretos por assunto:', *lines])


def _looks_like_public_timeline_order_followup(
    question: str,
    conversation_context: dict[str, Any] | None,
) -> bool:
    normalized = _plain_text(question)
    if not any(
        term in normalized
        for term in (
            'nao quero o calendario inteiro',
            'não quero o calendário inteiro',
            'quero so esse recorte em ordem',
            'quero só esse recorte em ordem',
            'so esse recorte em ordem',
            'só esse recorte em ordem',
            'esse recorte em ordem',
        )
    ):
        return False
    recent_blob = ' '.join(
        _plain_text(item)
        for item in (
            _extract_recent_user_messages(conversation_context)
            + _extract_recent_assistant_messages(conversation_context)
        )[-6:]
    )
    return any(
        term in recent_blob
        for term in ('matricula', 'matrícula', 'aulas', 'reuniao', 'reunião', 'responsaveis', 'responsáveis')
    )


def _looks_like_public_calendar_reset_followup(
    question: str,
    conversation_context: dict[str, Any] | None,
) -> bool:
    normalized = _plain_text(question)
    if not any(
        term in normalized
        for term in (
            'so o calendario publico',
            'quero so o calendario publico',
            'calendario publico da escola',
        )
    ):
        return False
    recent_blob = ' '.join(
        _plain_text(item)
        for item in (
            _extract_recent_user_messages(conversation_context)
            + _extract_recent_assistant_messages(conversation_context)
        )[-8:]
    )
    if any(
        term in recent_blob
        for term in (
            'nota',
            'notas',
            'boletim',
            'frequencia',
            'faltas',
            'financeiro',
            'mensalidade',
            'ana oliveira',
            'lucas oliveira',
        )
    ):
        return True
    return 'calendario' in normalized


def _compose_public_timeline_order_direct_answer(
    school_profile: dict[str, Any] | None,
    *,
    timeline_payload: dict[str, Any] | None,
) -> str | None:
    admissions = _public_timeline_entry(
        school_profile,
        timeline_payload,
        topic_fragments=('admissions_opening', 'matricula', 'ingresso'),
    )
    school_year = _public_timeline_entry(
        school_profile,
        timeline_payload,
        topic_fragments=('school_year_start', 'inicio do ano letivo', 'inicio das aulas'),
    )
    family_meeting = _public_timeline_entry(
        school_profile,
        timeline_payload,
        topic_fragments=('family_meeting', 'reuniao de responsaveis', 'reunião de responsáveis'),
    )
    ordered: list[tuple[str, dict[str, Any] | None]] = [
        ('Matrícula e ingresso', admissions),
        ('Início das aulas', school_year),
        ('Reunião com responsáveis', family_meeting),
    ]
    lines: list[str] = []
    for index, (label, entry) in enumerate(ordered, start=1):
        if not isinstance(entry, dict):
            continue
        summary = str(entry.get('summary') or '').strip()
        if not summary:
            continue
        lines.append(f'{index}) {label}: {summary}')
    return '\n'.join(lines) if lines else None


def _last_assistant_message(conversation_context: dict[str, Any] | None) -> str | None:
    messages = _extract_recent_assistant_messages(conversation_context)
    return messages[-1] if messages else None


def _today_br() -> date:
    return datetime.now(ZoneInfo('America/Sao_Paulo')).date()


def _format_full_date_br(value: date) -> str:
    month_name = (
        'janeiro',
        'fevereiro',
        'março',
        'abril',
        'maio',
        'junho',
        'julho',
        'agosto',
        'setembro',
        'outubro',
        'novembro',
        'dezembro',
    )[value.month - 1]
    return f'{value.day} de {month_name} de {value.year}'


def _extract_dates_from_text(text: str | None) -> list[date]:
    normalized = _normalize_text(text)
    if not normalized:
        return []
    found: list[date] = []
    seen: set[date] = set()
    for day, month, year in re.findall(r'\b(\d{1,2})/(\d{1,2})/(\d{4})\b', normalized):
        try:
            parsed = date(int(year), int(month), int(day))
        except ValueError:
            continue
        if parsed not in seen:
            seen.add(parsed)
            found.append(parsed)
    for year, month, day in re.findall(r'\b(\d{4})-(\d{2})-(\d{2})\b', normalized):
        try:
            parsed = date(int(year), int(month), int(day))
        except ValueError:
            continue
        if parsed not in seen:
            seen.add(parsed)
            found.append(parsed)
    month_pattern = '|'.join(sorted((_plain_text(name) for name in _PT_MONTHS), key=len, reverse=True))
    for day, month_name, year in re.findall(rf'\b(\d{{1,2}})\s+de\s+({month_pattern})\s+de\s+(\d{{4}})\b', _plain_text(normalized)):
        month = _PT_MONTHS.get(month_name)
        if not month:
            continue
        try:
            parsed = date(int(year), int(month), int(day))
        except ValueError:
            continue
        if parsed not in seen:
            seen.add(parsed)
            found.append(parsed)
    return found


def _question_asks_temporal_status(question: str) -> bool:
    return _contains_any(question, _PUBLIC_TEMPORAL_START_HINTS)


def _question_asks_temporal_distance(question: str) -> bool:
    return _contains_any(question, _PUBLIC_TEMPORAL_DISTANCE_HINTS)


def _question_requests_public_notification(question: str) -> bool:
    return _contains_any(question, _PUBLIC_NOTIFICATION_HINTS)


def _question_mentions_today(question: str) -> bool:
    normalized = _plain_text(question)
    return 'que dia e hoje' in normalized or 'qual a data de hoje' in normalized or 'hoje' in normalized


def _public_timeline_entries(
    school_profile: dict[str, Any] | None,
    timeline_payload: dict[str, Any] | None,
) -> list[dict[str, Any]]:
    entries = school_profile.get('public_timeline') if isinstance(school_profile, dict) else None
    if isinstance(entries, list):
        return [item for item in entries if isinstance(item, dict)]
    payload_entries = timeline_payload.get('entries') if isinstance(timeline_payload, dict) else None
    if isinstance(payload_entries, list):
        return [item for item in payload_entries if isinstance(item, dict)]
    return []


def _public_timeline_entry(
    school_profile: dict[str, Any] | None,
    timeline_payload: dict[str, Any] | None,
    *,
    topic_fragments: tuple[str, ...],
) -> dict[str, Any] | None:
    for item in _public_timeline_entries(school_profile, timeline_payload):
        topic_key = _plain_text(item.get('topic_key'))
        title = _plain_text(item.get('title'))
        if any(fragment in topic_key or fragment in title for fragment in topic_fragments):
            return item
    return None


def _public_timeline_entry_date(entry: dict[str, Any] | None) -> str:
    if not isinstance(entry, dict):
        return ''
    event_date_raw = str(entry.get('event_date') or '').strip()
    if event_date_raw:
        try:
            return _format_full_date_br(date.fromisoformat(event_date_raw))
        except ValueError:
            pass
    summary = str(entry.get('summary') or '').strip()
    match = re.search(r'\b\d{1,2}\s+de\s+[a-zç]+\s+de\s+\d{4}\b', _plain_text(summary))
    return match.group(0) if match else ''


def _question_mentions_public_district(question: str) -> bool:
    normalized = _plain_text(question)
    return any(term in normalized for term in ('bairro', 'regiao', 'região')) and any(
        term in normalized for term in ('escola', 'colegio', 'colégio', 'fica', 'endereco', 'endereço')
    )


def _question_mentions_public_bncc(question: str) -> bool:
    normalized = _plain_text(question)
    return 'bncc' in normalized or (
        'ensino medio' in normalized
        and any(term in normalized for term in ('curriculo', 'currículo', 'base curricular'))
    )


def _question_mentions_public_website(question: str) -> bool:
    normalized = _plain_text(question)
    return any(term in normalized for term in ('site oficial', 'website', 'link do site', 'site da escola')) or (
        'site' in normalized and any(term in normalized for term in ('escola', 'colegio', 'colégio'))
    )


def _question_mentions_public_director(question: str) -> bool:
    normalized = _plain_text(question)
    has_role = any(term in normalized for term in ('diretora', 'diretor', 'direcao', 'direção', 'diretoria'))
    has_identity = any(term in normalized for term in ('nome', 'quem', 'comando', 'manda', 'lidera', 'liderança'))
    return has_role and has_identity


def _question_mentions_public_library_identity(question: str) -> bool:
    normalized = _plain_text(question)
    return 'biblioteca' in normalized and any(
        term in normalized for term in ('nome', 'horario', 'horário', 'abre', 'funciona', 'marketing')
    )


def _question_mentions_public_capabilities(question: str) -> bool:
    normalized = _plain_text(question)
    return any(
        term in normalized
        for term in (
            'quais opcoes de assuntos',
            'opcoes de assuntos',
            'opções de assuntos',
            'o que voce faz',
            'o que você faz',
            'como voce pode me ajudar',
            'como você pode me ajudar',
            'quais assuntos',
        )
    )


def _question_mentions_public_admissions_opening(question: str) -> bool:
    normalized = _plain_text(question)
    return any(
        term in normalized
        for term in ('quando abre a matricula', 'quando abre a matrícula', 'abertura da matricula', 'matricula de 2026')
    ) or (
        any(term in normalized for term in ('matricula', 'matrícula'))
        and any(term in normalized for term in ('quando abre', 'quando comeca', 'quando começa', 'abre'))
    )


def _question_mentions_public_school_year_start(question: str) -> bool:
    normalized = _plain_text(question)
    return any(
        term in normalized
        for term in (
            'quando comecam as aulas',
            'quando começam as aulas',
            'quando comeca o ano letivo',
            'quando começa o ano letivo',
            'inicio das aulas',
            'início das aulas',
        )
    )


def _question_mentions_public_family_meeting(question: str) -> bool:
    normalized = _plain_text(question)
    return any(
        term in normalized
        for term in (
            'reuniao de pais',
            'reunião de pais',
            'reuniao de responsaveis',
            'reunião de responsáveis',
            'reuniao de familias',
            'reunião de famílias',
        )
    )


def _question_mentions_visit_reschedule_followup(
    question: str,
    conversation_context: dict[str, Any] | None,
) -> bool:
    normalized = _plain_text(question)
    asks_reschedule = any(
        term in normalized
        for term in (
            'remarcar',
            'reagendar',
            'mudar horario',
            'mudar horário',
            'trocar horario',
            'trocar horário',
            'se eu precisar remarcar',
        )
    )
    if not asks_reschedule:
        return False
    if any(term in normalized for term in ('visita', 'tour')):
        return True
    recent_blob = ' '.join(
        _plain_text(item)
        for item in (
            _extract_recent_user_messages(conversation_context)
            + _extract_recent_assistant_messages(conversation_context)
        )[-6:]
    )
    return any(term in recent_blob for term in ('visita', 'tour', 'pedido de visita', 'protocolo da visita'))


def _question_mentions_visit_resume_followup(
    question: str,
    conversation_context: dict[str, Any] | None,
) -> bool:
    normalized = _plain_text(question)
    asks_resume = any(
        term in normalized
        for term in (
            'retomar',
            'retoma',
            'retomo',
            'voltar',
            'volto',
            'como retomo',
            'como eu retomo',
            'como volto',
            'como eu volto',
            'por onde volto',
            'por onde eu volto',
            'por onde retomo',
            'por onde eu retomo',
        )
    )
    if not asks_resume:
        return False
    if any(term in normalized for term in ('visita', 'tour')):
        return True
    recent_blob = ' '.join(
        _plain_text(item)
        for item in (
            _extract_recent_user_messages(conversation_context)
            + _extract_recent_assistant_messages(conversation_context)
        )[-8:]
    )
    return any(term in recent_blob for term in ('visita', 'tour', 'pedido de visita', 'protocolo da visita'))


def _compose_public_capabilities_direct_answer(
    school_profile: dict[str, Any] | None,
    capabilities_payload: dict[str, Any] | None,
) -> str:
    capability_model = capabilities_payload if isinstance(capabilities_payload, dict) else {}
    school_name = str(
        (capability_model.get('school_name') if isinstance(capability_model, dict) else None)
        or (school_profile or {}).get('school_name')
        or 'Colegio Horizonte'
    ).strip() or 'Colegio Horizonte'
    public_topics = [
        str(item).strip()
        for item in (capability_model.get('public_topics') or [])
        if isinstance(item, str) and str(item).strip()
    ]
    protected_topics = [
        str(item).strip()
        for item in (capability_model.get('protected_topics') or [])
        if isinstance(item, str) and str(item).strip()
    ]
    public_summary = '; '.join(public_topics[:3]) if public_topics else 'matricula, secretaria, financeiro e visitas'
    protected_summary = '; '.join(protected_topics[:2]) if protected_topics else 'notas, faltas e pagamentos'
    return (
        f'Por aqui eu consigo te ajudar com {public_summary} no {school_name}. '
        f'Se sua conta estiver vinculada, eu tambem consigo consultar {protected_summary}.'
    )


def _compose_public_visit_reschedule_direct_answer(
    school_profile: dict[str, Any] | None,
) -> str:
    services = (school_profile or {}).get('service_catalog')
    visit_service = next(
        (
            item
            for item in services
            if isinstance(item, dict) and str(item.get('service_key') or '').strip() == 'visita_institucional'
        ),
        None,
    ) if isinstance(services, list) else None
    request_channel = str((visit_service or {}).get('request_channel') or 'bot, admissions ou whatsapp comercial').strip()
    eta = str((visit_service or {}).get('typical_eta') or 'confirmacao em ate 1 dia util').strip()
    return (
        'Se voce precisar remarcar a visita, me passe o protocolo do pedido ou o novo dia e horario desejados. '
        f'Hoje o canal institucional para isso e {request_channel}, com {eta}.'
    )


def _compose_public_visit_resume_direct_answer(
    school_profile: dict[str, Any] | None,
) -> str:
    services = (school_profile or {}).get('service_catalog')
    visit_service = next(
        (
            item
            for item in services
            if isinstance(item, dict) and str(item.get('service_key') or '').strip() == 'visita_institucional'
        ),
        None,
    ) if isinstance(services, list) else None
    request_channel = str((visit_service or {}).get('request_channel') or 'bot, admissions ou whatsapp comercial').strip()
    eta = str((visit_service or {}).get('typical_eta') or 'confirmacao em ate 1 dia util').strip()
    return (
        'Se voce quiser retomar a visita depois, volte por este mesmo canal institucional ou pela secretaria/admissions. '
        'Se ja existir um protocolo anterior, pode me passar esse codigo; se preferir, eu tambem posso abrir um novo pedido com outro dia e horario. '
        f'Hoje o canal institucional para isso e {request_channel}, com {eta}.'
    )


def _question_mentions_school_capacity(question: str) -> bool:
    normalized = _plain_text(question)
    return any(term in normalized for term in _PUBLIC_CAPACITY_HINTS)


def _question_mentions_parking_capacity(question: str) -> bool:
    normalized = _plain_text(question)
    return any(term in normalized for term in _PUBLIC_PARKING_HINTS)


def _question_mentions_student_capacity(question: str) -> bool:
    normalized = _plain_text(question)
    return any(term in normalized for term in _PUBLIC_STUDENT_CAPACITY_HINTS)


def _looks_like_careers_answer(text: str | None) -> bool:
    normalized = _plain_text(text)
    return any(term in normalized for term in _CAREERS_RESPONSE_HINTS)


def _calendar_topic_label(question: str, *, recent_messages: list[str], response_text: str) -> str:
    question_plain = _plain_text(question)
    if 'formatura' in question_plain or 'cerimonia' in question_plain or 'cerimônia' in question_plain:
        return 'a formatura'
    if 'aulas' in question_plain or 'acolhimento' in question_plain:
        return 'as aulas'
    if 'reuniao' in question_plain or 'reunião' in question_plain:
        return 'a reunião'
    for text in reversed(recent_messages):
        text_plain = _plain_text(text)
        if 'formatura' in text_plain or 'cerimonia' in text_plain or 'cerimônia' in text_plain:
            return 'a formatura'
        if 'aulas' in text_plain or 'acolhimento' in text_plain:
            return 'as aulas'
        if 'reuniao' in text_plain or 'reunião' in text_plain:
            return 'a reunião'
    response_plain = _plain_text(response_text)
    if 'formatura' in response_plain or 'cerimonia' in response_plain or 'cerimônia' in response_plain:
        return 'a formatura'
    if 'aulas' in response_plain or 'acolhimento' in response_plain:
        return 'as aulas'
    if 'reuniao' in response_plain or 'reunião' in response_plain:
        return 'a reunião'
    return 'esse evento'


def _event_date_from_public_context(
    *,
    question: str | None = None,
    response: MessageResponse,
    conversation_context: dict[str, Any] | None,
) -> date | None:
    today = _today_br()
    recent_assistant_messages = list(reversed(_extract_recent_assistant_messages(conversation_context)))
    topic_label = _calendar_topic_label(
        question or '',
        recent_messages=recent_assistant_messages,
        response_text=response.message_text,
    )
    topic_markers: tuple[str, ...]
    if topic_label == 'a formatura':
        topic_markers = ('formatura', 'cerimonia', 'cerimônia')
    elif topic_label == 'as aulas':
        topic_markers = ('aulas', 'acolhimento')
    elif topic_label == 'a reunião':
        topic_markers = ('reuniao', 'reunião')
    else:
        topic_markers = ()
    prioritized_recent = [
        text for text in recent_assistant_messages if any(marker in _plain_text(text) for marker in topic_markers)
    ] if topic_markers else []
    fallback_recent = [text for text in recent_assistant_messages if text not in prioritized_recent]
    candidate_groups = [
        prioritized_recent,
        [response.message_text],
        fallback_recent,
    ]
    grouped_dates: list[list[date]] = []
    for texts in candidate_groups:
        dates_for_group: list[date] = []
        for text in texts:
            dates = _extract_dates_from_text(text)
            if not dates:
                continue
            text_plain = _plain_text(text)
            if ('hoje e' in text_plain or 'hoje é' in text_plain or 'hoje ' in text_plain) and len(dates) > 1:
                non_today_dates = [value for value in dates if value != today]
                if non_today_dates:
                    dates = non_today_dates
            elif ('hoje e' in text_plain or 'hoje é' in text_plain or text_plain.startswith('hoje ')) and len(texts) > 1:
                non_today_dates = [value for value in dates if value != today]
                if non_today_dates:
                    dates = non_today_dates
            dates_for_group.extend(dates)
        grouped_dates.append(dates_for_group)
    candidate_dates: list[date] = []
    for dates in grouped_dates:
        if not dates:
            continue
        deduped_group: list[date] = []
        seen_group: set[date] = set()
        for value in dates:
            if value in seen_group:
                continue
            seen_group.add(value)
            deduped_group.append(value)
        candidate_dates.extend(deduped_group)
    if candidate_dates:
        deduped: list[date] = []
        seen: set[date] = set()
        for value in candidate_dates:
            if value in seen:
                continue
            seen.add(value)
            deduped.append(value)
        if _question_asks_temporal_distance(question or '') or _question_requests_public_notification(question or ''):
            for dates in grouped_dates:
                if not dates:
                    continue
                future_or_today = [value for value in dates if value >= today]
                if future_or_today:
                    return min(future_or_today)
            future_or_today = [value for value in deduped if value >= today]
            if future_or_today:
                return min(future_or_today)
        non_today = [value for value in deduped if value != today]
        if non_today:
            return non_today[0]
        return deduped[0]
    for event in response.calendar_events[:3]:
        dates = _extract_dates_from_text(event.starts_at.isoformat())
        if dates:
            return dates[0]
    return None


def _recent_messages_include_pricing_context(conversation_context: dict[str, Any] | None) -> bool:
    recent = _extract_recent_messages(conversation_context)
    combined = _plain_text(' '.join(recent))
    return any(term in combined for term in ('mensalidade', 'matricula', 'matrícula', 'taxa de matricula', 'taxa de matrícula', 'filhos'))


def _deterministic_public_calendar_followup(
    *,
    request: MessageResponseRequest,
    response: MessageResponse,
    conversation_context: dict[str, Any] | None,
) -> str | None:
    question = request.message
    question_plain = _plain_text(question)
    if not (
        _question_asks_temporal_status(question)
        or _question_asks_temporal_distance(question)
        or _question_requests_public_notification(question)
        or (_question_mentions_today(question) and ('comecam as aulas' in question_plain or 'comecam as aulas' in question_plain))
    ):
        return None
    event_date = _event_date_from_public_context(
        question=question,
        response=response,
        conversation_context=conversation_context,
    )
    if event_date is None:
        return None
    today = _today_br()
    topic_label = _calendar_topic_label(
        question,
        recent_messages=_extract_recent_assistant_messages(conversation_context),
        response_text=response.message_text,
    )
    if _question_requests_public_notification(question):
        return (
            f'Eu nao consigo te avisar automaticamente por aqui quando {topic_label} estiver perto. '
            f'O que eu consigo te dizer hoje e que {topic_label} esta prevista para {_format_full_date_br(event_date)}. '
            'Para confirmar mais perto da data, vale acompanhar o calendario e os canais oficiais da escola ou me perguntar novamente.'
        )
    if _question_mentions_today(question) and ('comecam as aulas' in question_plain or 'começam as aulas' in question_plain):
        return (
            f'Hoje e {_format_full_date_br(today)}. '
            f'{topic_label.capitalize()} estao previstas para {_format_full_date_br(event_date)}.'
            if topic_label == 'as aulas'
            else f'Hoje e {_format_full_date_br(today)}. {topic_label.capitalize()} esta prevista para {_format_full_date_br(event_date)}.'
        )
    if _question_asks_temporal_status(question):
        if event_date <= today:
            if topic_label == 'as aulas':
                return f'Sim. Hoje e {_format_full_date_br(today)} e, como as aulas comecaram em {_format_full_date_br(event_date)}, elas ja comecaram.'
            return f'Sim. Hoje e {_format_full_date_br(today)} e, como {topic_label} estava prevista para {_format_full_date_br(event_date)}, essa data ja passou.'
        if topic_label == 'as aulas':
            return f'Nao. Hoje e {_format_full_date_br(today)} e as aulas estao previstas para {_format_full_date_br(event_date)}.'
        return f'Ainda nao. Hoje e {_format_full_date_br(today)} e {topic_label} esta prevista para {_format_full_date_br(event_date)}.'
    if _question_asks_temporal_distance(question):
        delta_days = (event_date - today).days
        if delta_days > 90:
            distance_text = 'ainda falta bastante tempo'
        elif delta_days > 30:
            distance_text = 'ainda falta um tempo'
        elif delta_days >= 0:
            distance_text = 'ja esta relativamente perto'
        else:
            distance_text = 'essa data ja passou'
        return f'{topic_label.capitalize()} esta prevista para {_format_full_date_br(event_date)}; {distance_text}.'
    return None


def _deterministic_public_capacity_followup(
    *,
    request: MessageResponseRequest,
    response: MessageResponse,
    conversation_context: dict[str, Any] | None,
) -> tuple[str | None, OrchestrationMode | None]:
    question = request.message
    if not (_question_mentions_school_capacity(question) or _question_mentions_parking_capacity(question)):
        return None, None
    if _question_mentions_parking_capacity(question):
        return (
            'Hoje a base publica da escola nao informa a quantidade de vagas de estacionamento. '
            'Se isso for importante para visita, evento ou rotina de acesso, o caminho mais seguro e confirmar com a secretaria ou recepcao.',
            OrchestrationMode.structured_tool,
        )
    if _question_mentions_school_capacity(question):
        return (
            'Hoje a base publica da escola nao divulga um numero fechado de vagas para alunos ou de capacidade total da escola. '
            'A disponibilidade costuma ser confirmada por segmento e turma com admissions ou secretaria, conforme o momento do ciclo de matricula.',
            OrchestrationMode.structured_tool,
        )
    if _question_mentions_student_capacity(question) or _recent_messages_include_pricing_context(conversation_context):
        return (
            'Hoje a base publica da escola nao divulga um numero fechado de vagas para alunos ou de capacidade total da escola. '
            'A disponibilidade costuma ser confirmada por segmento e turma com admissions ou secretaria, conforme o momento do ciclo de matricula.',
            OrchestrationMode.structured_tool,
        )
    if _looks_like_careers_answer(response.message_text):
        return (
            'Quando voce fala em vagas, isso pode significar vagas para alunos, vagas de estacionamento ou vagas para trabalhar na escola. '
            'Se quiser, eu separo isso agora pelo tipo certo.',
            OrchestrationMode.clarify,
        )
    return None, None


def _question_mentions_public_teacher_directory(
    message: str,
    conversation_context: dict[str, Any] | None = None,
) -> bool:
    normalized = _plain_text(message)
    if any(term in normalized for term in ('professor', 'professora', 'docente')):
        return any(
            term in normalized
            for term in (
                'contato',
                'telefone',
                'whatsapp',
                'email',
                'divulga',
                'encaminha',
                'falar com',
                'conversar com',
            )
        )
    if not isinstance(conversation_context, dict):
        return False
    recent_blob = ' '.join(_plain_text(item) for item in _extract_recent_user_messages(conversation_context)[-4:])
    if not any(term in recent_blob for term in ('professor', 'professora', 'docente')):
        return False
    return any(
        term in normalized
        for term in (
            'esse contato',
            'esse canal',
            'divulga esse contato',
            'divulga esse canal',
            'a escola divulga',
            'coordenacao',
            'coordenação',
            'procurar a coordenacao',
            'procurar a coordenação',
            'manda procurar',
        )
    )


def _looks_like_internal_document_query(message: str) -> bool:
    normalized = _plain_text(message)
    if not normalized:
        return False
    if any(
        term in normalized
        for term in (
            'manual interno',
            'material interno',
            'documento interno',
            'documentos internos',
            'protocolo interno',
            'orientacao interna',
            'orientação interna',
        )
    ):
        return True
    return (
        any(term in normalized for term in ('professor', 'professora', 'docente'))
        and any(term in normalized for term in ('manual', 'material', 'protocolo', 'orientacao interna', 'orientação interna'))
    )


def _is_restricted_document_no_match_response(response: MessageResponse) -> bool:
    reason = str(response.reason or '')
    if 'restricted_document_no_match' in reason or 'restricted_doc_no_match' in reason:
        return True
    if response.classification.access_tier == AccessTier.public:
        return False
    text = _plain_text(response.message_text)
    return (
        response.retrieval_backend != RetrievalBackend.none
        and 'nao encontrei' in text
        and any(term in text for term in ('excursao', 'excursão', 'viagem internacional', 'hospedagem', 'pernoite'))
    )


def _question_mentions_public_permanence_support(message: str) -> bool:
    normalized = _plain_text(message)
    if 'famil' not in normalized:
        return False
    if any(
        term in normalized
        for term in ('financeiro', 'pagamentos', 'boletos', 'faturas', 'vencimentos', 'atrasos', 'mensalidade', 'taxa', 'desconto')
    ):
        return False
    return (
        any(term in normalized for term in ('permanencia', 'vida escolar'))
        and any(term in normalized for term in ('apoio', 'acompanh'))
    )


def _question_mentions_public_first_month_risks(message: str) -> bool:
    normalized = _plain_text(message)
    return (
        any(term in normalized for term in ('inicio do ano', 'primeiro mes', 'primeiro mês', 'primeiras semanas'))
        and any(term in normalized for term in ('login', 'document', 'rotina', 'credenciais'))
    )


def _question_mentions_public_visibility_boundary(message: str) -> bool:
    normalized = _plain_text(message)
    return (
        'portal' in normalized
        and any(term in normalized for term in ('login', 'autentic'))
        and any(term in normalized for term in ('autentic', 'calendario', 'calendário'))
    )


def _question_mentions_public_bolsas_and_processes(message: str) -> bool:
    normalized = _plain_text(message)
    return (
        any(term in normalized for term in ('bolsa', 'bolsas', 'desconto', 'descontos'))
        and any(term in normalized for term in ('rematricula', 'rematrícula', 'transferencia', 'transferência', 'cancelamento'))
    )


def _question_mentions_public_health_emergency_bundle(message: str) -> bool:
    normalized = _plain_text(message)
    return (
        any(term in normalized for term in ('medic', 'saude', 'saúde', 'emergenc'))
        and any(term in normalized for term in ('protocolo', 'acompanhamento', 'justific', 'atestado'))
    )


def _question_mentions_public_outings_authorizations(message: str) -> bool:
    normalized = _plain_text(message)
    return (
        any(term in normalized for term in ('saida', 'saída', 'eventos escolares', 'evento escolar', 'pedagogic'))
        and any(term in normalized for term in ('autoriz', 'famil'))
    )


async def _deterministic_public_direct_answer(
    *,
    request: MessageResponseRequest,
    response: MessageResponse,
    school_profile: dict[str, Any],
    settings: Any,
    conversation_context: dict[str, Any] | None,
) -> str | None:
    from .grounded_answer_support_runtime import _deterministic_public_direct_answer as _impl

    return await _impl(
        request=request,
        response=response,
        school_profile=school_profile,
        settings=settings,
        conversation_context=conversation_context,
    )



def _focus_marked_student_from_question(
    actor: dict[str, Any] | None,
    question: str,
) -> dict[str, Any] | None:
    linked_students = actor.get('linked_students') if isinstance(actor, dict) else None
    if not isinstance(linked_students, list):
        return None
    from .student_scope_runtime import _focus_marked_student_from_message

    return _focus_marked_student_from_message(linked_students, question)


def _mentioned_linked_student_names_from_question(
    actor: dict[str, Any] | None,
    question: str,
) -> list[str]:
    linked_students = actor.get('linked_students') if isinstance(actor, dict) else None
    if not isinstance(linked_students, list):
        return []
    normalized = _plain_text(question)
    matches: list[tuple[int, str]] = []
    for student in linked_students:
        if not isinstance(student, dict):
            continue
        full_name = str(student.get('full_name') or '').strip()
        if not full_name:
            continue
        full_name_plain = _plain_text(full_name)
        first_name_plain = full_name_plain.split(' ')[0] if full_name_plain else ''
        position = normalized.find(full_name_plain) if full_name_plain else -1
        if position < 0 and first_name_plain:
            match = re.search(rf'\b{re.escape(first_name_plain)}\b', normalized)
            position = match.start() if match else -1
        if position >= 0:
            matches.append((position, full_name))
    matches.sort(key=lambda item: (item[0], _plain_text(item[1])))
    ordered_names: list[str] = []
    seen: set[str] = set()
    for _position, full_name in matches:
        normalized_name = _plain_text(full_name)
        if normalized_name in seen:
            continue
        seen.add(normalized_name)
        ordered_names.append(full_name)
    return ordered_names


def _looks_like_cross_student_academic_comparison_followup(question: str) -> bool:
    normalized = _plain_text(question)
    has_compare_anchor = any(
        term in normalized
        for term in (
            'compar',
            'compare',
            'comparar',
            'contra',
            'em relacao',
            'em relação',
            'entre ',
            'veredito academico',
            'veredito acadêmico',
        )
    )
    if not has_compare_anchor:
        return False
    if any(term in normalized for term in ('documentacao', 'documentação', 'documental', 'cadastro', 'pendencia', 'pendência', 'administrativ')):
        return False
    has_family_compare = any(
        term in normalized
        for term in (
            ' com ',
            ' com a ',
            ' com o ',
            'isso com',
            'meus filhos',
            'minha filha',
            'meu filho',
            'entre ',
        )
    )
    has_academic_anchor = any(
        term in normalized
        for term in (
            'academ',
            'nota',
            'notas',
            'media',
            'média',
            'disciplina',
            'disciplinas',
            'componente',
            'componentes',
            'bimestre',
            'aprovacao',
            'aprovação',
        )
    )
    return has_family_compare and has_academic_anchor


def _recent_guardian_academic_context(conversation_context: dict[str, Any] | None) -> bool:
    if not isinstance(conversation_context, dict):
        return False
    recent_messages = conversation_context.get('recent_messages')
    if not isinstance(recent_messages, list):
        return False
    blob = ' '.join(str(item.get('content') or '') for item in recent_messages if isinstance(item, dict))
    normalized = _plain_text(blob)
    return any(
        term in normalized
        for term in (
            'nota',
            'notas',
            'media parcial',
            'média parcial',
            'menor nota',
            'mais perto da media minima',
            'mais perto da média mínima',
            'atencao academica',
            'atenção acadêmica',
            'fisica',
            'física',
            'historia',
            'história',
            'matematica',
            'matemática',
            'portugues',
            'português',
            'panorama academico',
            'panorama acadêmico',
        )
    )


def _looks_like_contextual_cross_student_academic_comparison_followup(
    question: str,
    *,
    conversation_context: dict[str, Any] | None,
    mentioned_students: list[str] | None = None,
) -> bool:
    normalized = _plain_text(question)
    has_compare_anchor = any(
        term in normalized
        for term in (
            'compar',
            'compare',
            'comparar',
            'contra',
            'em relacao',
            'em relação',
            'entre ',
            'veredito academico',
            'veredito acadêmico',
        )
    )
    if not has_compare_anchor:
        return False
    if any(term in normalized for term in ('documentacao', 'documentação', 'documental', 'cadastro', 'pendencia', 'pendência', 'administrativ')):
        return False
    has_compare_target = bool(mentioned_students) or any(
        term in normalized
        for term in (' com ', ' com a ', ' com o ', 'isso com', 'meus filhos', 'minha filha', 'meu filho', 'entre ')
    )
    return has_compare_target and _recent_guardian_academic_context(conversation_context)


def _compose_cross_student_academic_comparison_direct(
    summaries: list[dict[str, Any]],
    *,
    preferred_order: list[str] | None = None,
) -> str | None:
    ranking = _family_academic_ranking(summaries)
    if len(ranking) < 2:
        return None
    by_name = {str(item['student_name']): item for item in ranking}
    ordered_names = [name for name in (preferred_order or []) if name in by_name]
    if len(ordered_names) < 2:
        ordered_names = list(by_name.keys())[:2]
    if len(ordered_names) < 2:
        return None
    base = by_name[ordered_names[0]]
    other = by_name[ordered_names[1]]
    most_critical = base if float(base['value']) <= float(other['value']) else other
    base_value = f"{float(base['value']):.1f}".replace('.', ',')
    other_value = f"{float(other['value']):.1f}".replace('.', ',')
    return (
        f"Comparando {base['student_name']} com {other['student_name']}: "
        f"{base['student_name']} tem o ponto academico mais sensivel em {base['subject_name']}, com media parcial {base_value}/10, "
        f"enquanto {other['student_name']} aparece com menor media em {other['subject_name']}, com {other_value}/10. "
        f"Hoje quem esta mais perto da media minima entre os dois e {most_critical['student_name']}, puxado por {most_critical['subject_name']}."
    )


async def _deterministic_protected_academic_direct_answer(
    *,
    request: MessageResponseRequest,
    response: MessageResponse,
    focus: AnswerFocusState,
    actor: dict[str, Any] | None,
    settings: Any,
    conversation_context: dict[str, Any] | None,
) -> str | None:
    from .grounded_answer_support_runtime import _deterministic_protected_academic_direct_answer as _impl

    return await _impl(
        request=request,
        response=response,
        focus=focus,
        actor=actor,
        settings=settings,
        conversation_context=conversation_context,
    )



def _looks_like_attendance_alert_request(question: str) -> bool:
    normalized = _plain_text(question)
    return any(
        term in normalized
        for term in (
            'alerta principal',
            'principal alerta',
            'maior atencao',
            'maior atenção',
            'mais atencao',
            'mais atenção',
            'inspira mais atencao',
            'inspira mais atenção',
            'chama mais atencao',
            'chama mais atenção',
            'chamam atencao',
            'chamam atenção',
            'olhando as faltas',
            'foco principal de frequencia',
            'foco principal de frequência',
            'bate na frequencia',
            'bate na frequência',
            'por que a frequencia',
            'por que a frequência',
            'frequencia dele preocupa',
            'frequência dele preocupa',
            'preocupa mais',
            'preocupa menos',
            'risco mais concreto',
            'risco concreto',
            'mais sensivel',
            'mais sensível',
            'faltas recentes',
            'ausencias recentes',
            'ausências recentes',
            'ponto mais critico da frequencia',
            'ponto mais crítico da frequência',
            'componentes as ausencias pesam mais',
            'componentes as ausências pesam mais',
            'em quais componentes as ausencias pesam mais',
            'em quais componentes as ausências pesam mais',
        )
    )


def _compose_attendance_priority_focus(summary: dict[str, Any], *, student_name: str) -> str | None:
    priority_rows = _attendance_priority_rows_for_focus(summary)
    if not priority_rows:
        return None
    top_row = priority_rows[0]
    subject_name = str(top_row.get('subject_name') or 'disciplina').strip() or 'disciplina'
    absent = int(top_row.get('absent_count', 0) or 0)
    late = int(top_row.get('late_count', 0) or 0)
    present = int(top_row.get('present_count', 0) or 0)
    return (
        f'O principal alerta de frequencia de {student_name} hoje aparece em {subject_name}: '
        f'{absent} falta(s), {late} atraso(s) e {present} presenca(s) neste recorte. '
        'Esse e o foco principal porque concentra a maior combinacao de faltas e atrasos do aluno neste momento. '
        f'Proximo passo: acompanhar {subject_name} nas proximas aulas para verificar se novas faltas ou atrasos continuam pressionando a frequencia.'
    )


def _compose_attendance_next_step_focus(summary: dict[str, Any], *, student_name: str) -> str | None:
    priority_rows = _attendance_priority_rows_for_focus(summary)
    if not priority_rows:
        return None
    top_row = priority_rows[0]
    subject_name = str(top_row.get('subject_name') or 'disciplina').strip() or 'disciplina'
    absent = int(top_row.get('absent_count', 0) or 0)
    late = int(top_row.get('late_count', 0) or 0)
    return (
        f'O proximo passo para {student_name} e acompanhar primeiro {subject_name}, '
        f'porque esse componente concentra {absent} falta(s) e {late} atraso(s) neste recorte. '
        'Na pratica, vale monitorar novas ausencias e alinhar a rotina antes que esse ponto siga acumulando risco.'
    )


def _recent_family_academic_context(conversation_context: dict[str, Any] | None) -> bool:
    if not isinstance(conversation_context, dict):
        return False
    recent_messages = conversation_context.get('recent_messages')
    if not isinstance(recent_messages, list):
        return False
    blob = ' '.join(str(item.get('content') or '') for item in recent_messages if isinstance(item, dict))
    normalized = _plain_text(blob)
    return 'panorama academico das contas vinculadas' in normalized or 'quem hoje exige maior atencao academica e' in normalized


def _recent_family_attendance_context(conversation_context: dict[str, Any] | None) -> bool:
    if not isinstance(conversation_context, dict):
        return False
    recent_messages = conversation_context.get('recent_messages')
    if not isinstance(recent_messages, list):
        return False
    blob = ' '.join(str(item.get('content') or '') for item in recent_messages if isinstance(item, dict))
    normalized = _plain_text(blob)
    return (
        'panorama de faltas e frequencia das contas vinculadas' in normalized
        or 'panorama de frequencia das contas vinculadas' in normalized
        or 'frequencia dos meus filhos' in normalized
        or 'frequência dos meus filhos' in normalized
        or 'frequencia dos meus dois filhos' in normalized
        or 'frequência dos meus dois filhos' in normalized
        or 'quem exige maior atencao agora' in normalized
        or 'quem exige mais atencao agora' in normalized
        or 'quem exige mais atenção agora' in normalized
        or 'principal alerta de frequencia de' in normalized
        or 'principal alerta so do lucas' in normalized
        or 'principal alerta só do lucas' in normalized
        or 'o que eu deveria acompanhar primeiro' in normalized
    )


def _recent_linked_student_name_from_messages(
    conversation_context: dict[str, Any] | None,
    actor: dict[str, Any] | None,
) -> str | None:
    if not isinstance(conversation_context, dict) or not isinstance(actor, dict):
        return None
    recent_messages = conversation_context.get('recent_messages')
    linked_students = actor.get('linked_students')
    if not isinstance(recent_messages, list) or not isinstance(linked_students, list):
        return None
    names: list[tuple[str, str]] = []
    for student in linked_students:
        if not isinstance(student, dict):
            continue
        full_name = str(student.get('full_name') or '').strip()
        if not full_name:
            continue
        names.append((full_name, _plain_text(full_name)))
    for item in reversed(recent_messages):
        if not isinstance(item, dict):
            continue
        content = _plain_text(item.get('content'))
        if not content:
            continue
        for full_name, normalized_full in names:
            if normalized_full and normalized_full in content:
                return full_name
            first_name = normalized_full.split(' ')[0] if normalized_full else ''
            if first_name and re.search(rf'\b{re.escape(first_name)}\b', content):
                return full_name
    return None


def _recent_linked_student_name_for_admin_finance_combo(
    conversation_context: dict[str, Any] | None,
    actor: dict[str, Any] | None,
) -> str | None:
    if not isinstance(conversation_context, dict) or not isinstance(actor, dict):
        return None
    recent_messages = conversation_context.get('recent_messages')
    linked_students = actor.get('linked_students')
    if not isinstance(recent_messages, list) or not isinstance(linked_students, list):
        return None
    combo_terms = (
        'documentacao',
        'documentação',
        'documental',
        'cadastro',
        'financeiro',
        'fatura',
        'faturas',
        'mensalidade',
        'boleto',
        'boletos',
        'panorama combinado',
        'bloqueio',
        'bloqueando atendimento',
    )
    names: list[tuple[str, str]] = []
    for student in linked_students:
        if not isinstance(student, dict):
            continue
        full_name = str(student.get('full_name') or '').strip()
        if not full_name:
            continue
        names.append((full_name, _plain_text(full_name)))
    for item in reversed(recent_messages):
        if not isinstance(item, dict):
            continue
        content = _plain_text(item.get('content'))
        if not content or not any(term in content for term in combo_terms):
            continue
        for full_name, normalized_full in names:
            if normalized_full and normalized_full in content:
                return full_name
            first_name = normalized_full.split(' ')[0] if normalized_full else ''
            if first_name and re.search(rf'\b{re.escape(first_name)}\b', content):
                return full_name
    return _recent_linked_student_name_from_messages(conversation_context, actor)


def _looks_like_attendance_next_step_request(question: str) -> bool:
    normalized = _plain_text(question)
    return any(
        term in normalized
        for term in (
            'o que eu deveria acompanhar primeiro',
            'o que deveria acompanhar primeiro',
            'o que acompanhar primeiro',
            'sem repetir os numeros todos',
            'sem repetir os numeros',
            'proximo passo',
            'próximo passo',
        )
    )


def _looks_like_public_outings_protocol_followup(
    question: str,
    conversation_context: dict[str, Any] | None,
) -> bool:
    if not isinstance(conversation_context, dict):
        return False
    normalized = _plain_text(question)
    recent_blob = _plain_text(
        ' '.join(
            str(item.get('content') or '')
            for item in conversation_context.get('recent_messages') or []
            if isinstance(item, dict)
        )
    )
    has_outings_context = any(
        term in recent_blob
        for term in ('excursao', 'excursão', 'saida pedagogica', 'saída pedagógica', 'viagem', 'autorizacao', 'autorização')
    )
    if not has_outings_context:
        return False
    return any(
        term in normalized
        for term in (
            'o que existe de publico',
            'o que existe de público',
            'esse tipo de saida',
            'esse tipo de saída',
            'protocolo',
            'dois passos praticos',
            'dois passos práticos',
        )
    )


def _compose_public_outings_two_steps() -> str:
    return (
        'Primeiro, confirme pelo canal oficial a atividade, a data e as regras publicas da saida pedagogica. '
        'Depois, envie a autorizacao da familia no prazo e acompanhe as orientacoes de uniforme, saida e retorno.'
    )


async def _deterministic_protected_attendance_direct_answer(
    *,
    request: MessageResponseRequest,
    response: MessageResponse,
    focus: AnswerFocusState,
    actor: dict[str, Any] | None,
    settings: Any,
    conversation_context: dict[str, Any] | None,
) -> str | None:
    from .grounded_answer_support_runtime import _deterministic_protected_attendance_direct_answer as _impl

    return await _impl(
        request=request,
        response=response,
        focus=focus,
        actor=actor,
        settings=settings,
        conversation_context=conversation_context,
    )



async def _deterministic_protected_finance_direct_answer(
    *,
    request: MessageResponseRequest,
    response: MessageResponse,
    actor: dict[str, Any] | None,
    settings: Any,
    conversation_context: dict[str, Any] | None,
) -> str | None:
    from .grounded_answer_support_runtime import _deterministic_protected_finance_direct_answer as _impl

    return await _impl(
        request=request,
        response=response,
        actor=actor,
        settings=settings,
        conversation_context=conversation_context,
    )



def _infer_assistant_message_topic(message: str | None) -> str | None:
    normalized = _plain_text(message)
    if not normalized:
        return None
    if any(term in normalized for term in ('mensalidade', 'matricula', 'taxa de matricula', 'taxa de matrícula')):
        return 'mensalidade e matrícula'
    if any(term in normalized for term in ('fatura', 'boleto', 'financeiro', 'vencimento')) or _contains_monetary_signal(message or ''):
        return 'financeiro'
    if any(term in normalized for term in ('proximas avaliacoes', 'próximas avaliações', 'proximas provas', 'próximas provas', 'avaliacao', 'avaliação', 'entrega')):
        return 'próximas provas'
    if any(term in normalized for term in ('frequencia', 'frequência', 'faltas', 'presenca', 'presença')):
        return 'frequência'
    if any(term in normalized for term in ('nota', 'notas', 'media parcial', 'média parcial', 'boletim')):
        return 'notas'
    if any(term in normalized for term in ('atestado', 'justificar faltas', 'justificativa')):
        return 'justificativa de faltas'
    return None


def _topic_from_active_task(active_task: str | None) -> str | None:
    task = str(active_task or '').strip().lower()
    if task.startswith('academic:upcoming'):
        return 'próximas provas'
    if task.startswith('academic:grades'):
        return 'notas'
    if task.startswith('academic:attendance'):
        return 'frequência'
    if task.startswith('finance:'):
        return 'financeiro'
    if task.startswith('public:pricing'):
        return 'mensalidade e matrícula'
    return None


def _canonical_subject_key(value: str | None) -> str:
    text = _normalize_text(value)
    canonical = explicit_subject_from_message(text)
    return _focus_normalize_text(canonical or text)


def _candidate_mentions_other_subjects(candidate: str, *, requested_subject: str) -> bool:
    candidate_plain = _plain_text(candidate)
    mentioned = [subject for subject in _SUBJECT_NAMES if subject in candidate_plain]
    if not mentioned:
        return False
    allowed = {requested_subject}
    return any(
        subject not in allowed
        and subject not in requested_subject
        and requested_subject not in subject
        for subject in mentioned
    )


def _eligible_reason(
    *,
    request: MessageResponseRequest,
    response: MessageResponse,
    settings: Any,
    stack_name: str,
) -> str | None:
    if not bool(getattr(settings, 'feature_flag_answer_experience_enabled', False)):
        return None
    channel_allowlist = _csv_values(getattr(settings, 'feature_flag_answer_experience_channels', 'telegram'))
    if request.channel.value.lower() not in channel_allowlist:
        return None
    stack_allowlist = _csv_values(getattr(settings, 'feature_flag_answer_experience_stacks', ''))
    if stack_allowlist and stack_name.lower() not in stack_allowlist:
        return None
    if response.mode is OrchestrationMode.deny:
        return None
    if not _normalize_text(response.message_text):
        return None
    access_tier = response.classification.access_tier.value
    if access_tier == 'public' and not bool(getattr(settings, 'feature_flag_answer_experience_public_enabled', True)):
        return None
    if access_tier != 'public' and not bool(getattr(settings, 'feature_flag_answer_experience_protected_enabled', True)):
        return None
    if response.mode == OrchestrationMode.handoff:
        return 'handoff_guidance'
    if response.mode == OrchestrationMode.clarify:
        return 'clarify_repair_grounded_answer'
    min_chars = int(getattr(settings, 'feature_flag_answer_experience_min_chars', 24) or 24)
    if len(_normalize_text(response.message_text)) < min_chars and not response.selected_tools and response.evidence_pack is None:
        return None
    if request.debug_options.get('disable_answer_experience'):
        return None
    if response.classification.access_tier.value != 'public':
        return 'protected_grounded_answer'
    if response.mode == OrchestrationMode.structured_tool:
        return 'structured_grounded_answer'
    if response.retrieval_backend.value != 'none':
        return 'retrieval_grounded_answer'
    return 'general_grounded_answer'


def _answer_experience_pipeline_enabled(
    *,
    request: MessageResponseRequest,
    response: MessageResponse,
    settings: Any,
    stack_name: str,
) -> bool:
    if not bool(getattr(settings, 'feature_flag_answer_experience_enabled', False)):
        return False
    channel_allowlist = _csv_values(getattr(settings, 'feature_flag_answer_experience_channels', 'telegram'))
    if request.channel.value.lower() not in channel_allowlist:
        return False
    stack_allowlist = _csv_values(getattr(settings, 'feature_flag_answer_experience_stacks', ''))
    if stack_allowlist and stack_name.lower() not in stack_allowlist:
        return False
    if response.mode is OrchestrationMode.deny:
        return False
    if not _normalize_text(response.message_text):
        return False
    access_tier = response.classification.access_tier.value
    if access_tier == 'public' and not bool(getattr(settings, 'feature_flag_answer_experience_public_enabled', True)):
        return False
    if access_tier != 'public' and not bool(getattr(settings, 'feature_flag_answer_experience_protected_enabled', True)):
        return False
    if request.debug_options.get('disable_answer_experience'):
        return False
    return True


def _should_attempt_context_repair(
    *,
    request: MessageResponseRequest,
    response: MessageResponse,
    focus: AnswerFocusState,
    actor: dict[str, Any] | None,
) -> bool:
    text = _normalize_text(response.message_text)
    if not text:
        return False
    if (
        _looks_like_internal_document_query(request.message)
        and response.classification.access_tier != AccessTier.public
        and response.retrieval_backend != RetrievalBackend.none
    ):
        return False
    if _is_restricted_document_no_match_response(response):
        return False
    if focus.unknown_student_name or focus.unknown_subject_name or focus.is_repair_followup or focus.needs_disambiguation:
        return True
    linked_students = actor.get('linked_students') if isinstance(actor, dict) else None
    linked_student_count = len(linked_students) if isinstance(linked_students, list) else 0
    if (
        response.classification.access_tier != AccessTier.public
        and _question_mentions_upcoming_scope(request.message)
        and not focus.student_name
        and linked_student_count > 1
    ):
        return True
    if not _response_covers_requested_scope(request.message, text):
        return True
    if response.mode == OrchestrationMode.clarify:
        return True
    if _looks_like_student_resolution_failure(text):
        return True
    if _looks_like_grounding_weakness(text):
        return True
    if (
        response.classification.access_tier == AccessTier.public
        and _looks_like_explicit_limitation(text)
    ):
        support_count = int(response.evidence_pack.support_count) if response.evidence_pack is not None else 0
        if support_count <= 1 or _looks_like_relationship_followup(request.message):
            return True
    if (
        response.classification.access_tier == AccessTier.public
        and response.retrieval_backend == RetrievalBackend.none
        and _looks_like_relationship_followup(request.message)
    ):
        return True
    if (
        response.classification.access_tier == AccessTier.public
        and focus.uses_memory
        and response.retrieval_backend == RetrievalBackend.none
    ):
        support_count = int(response.evidence_pack.support_count) if response.evidence_pack is not None else 0
        selected_tools = {str(item).strip().lower() for item in (response.selected_tools or []) if str(item).strip()}
        if support_count <= 1 and (
            'get_public_school_profile' in selected_tools
            or 'public_profile' in selected_tools
            or 'fetch_academic_policy' in selected_tools
        ):
            return True
    if response.retrieval_backend != RetrievalBackend.none:
        support_count = int(response.evidence_pack.support_count) if response.evidence_pack is not None else 0
        if support_count <= 1 and not response.citations:
            return True
    if request.debug_options.get('disable_context_repair'):
        return False
    return False


def _clarify_after_retry_message(
    *,
    request: MessageResponseRequest,
    focus: AnswerFocusState,
    actor: dict[str, Any] | None,
    conversation_context: dict[str, Any] | None = None,
) -> str | None:
    linked_students = actor.get('linked_students') if isinstance(actor, dict) else None
    linked_names = [
        str(item.get('full_name') or '').strip()
        for item in linked_students or []
        if isinstance(item, dict) and str(item.get('full_name') or '').strip()
    ]
    recent_school_context = False
    if isinstance(conversation_context, dict):
        recent_messages = conversation_context.get('recent_messages')
        if isinstance(recent_messages, list):
            recent_school_context = any(
                looks_like_school_domain_request(str(item.get('content') or ''))
                for item in recent_messages
                if isinstance(item, dict)
            )
    if (
        not looks_like_school_domain_request(request.message)
        and not recent_school_context
        and not focus.uses_memory
        and not focus.is_repair_followup
        and focus.domain in {None, 'unknown', 'public'}
        and focus.topic in {None, 'clarify'}
        and not focus.unknown_student_name
        and not focus.unknown_subject_name
        and not focus.student_name
        and not focus.subject_name
    ):
        return (
            'Nao tenho base confiavel aqui para responder esse tema fora do escopo da escola. '
            'Se quiser, eu posso ajudar com matricula, calendario, regras publicas, visitas, notas, frequencia ou financeiro.'
        )
    if focus.unknown_student_name:
        names = list(linked_names)
        if names:
            if len(names) == 2:
                return f'Não encontrei {focus.unknown_student_name} entre os alunos vinculados. Você quer consultar {names[0]} ou {names[1]}?'
            return f'Não encontrei {focus.unknown_student_name} entre os alunos vinculados. Opções: {", ".join(names[:4])}.'
        return f'Não encontrei {focus.unknown_student_name} no contexto autenticado desta conversa.'
    if focus.unknown_subject_name:
        if focus.student_name:
            return f'Não encontrei a disciplina {focus.unknown_subject_name} para {focus.student_name}. Se quiser, eu posso consultar outra disciplina ou mostrar o boletim completo.'
        return f'Não reconheci a disciplina {focus.unknown_subject_name} neste contexto. Me diga o aluno e a disciplina exatamente como aparecem no boletim.'
    if focus.needs_disambiguation:
        if not focus.student_name and len(linked_names) >= 2 and focus.domain in {'academic', 'finance', 'institution'}:
            pair = f'{linked_names[0]} ou {linked_names[1]}' if len(linked_names) == 2 else ', '.join(linked_names[:4])
            if focus.domain == 'academic' and focus.subject_name:
                return f'Você quer consultar {focus.subject_name} de qual aluno: {pair}?'
            if focus.topic == 'upcoming_assessments':
                return f'Para qual aluno você quer ver as próximas provas: {pair}?'
            if focus.domain == 'finance':
                return f'Para qual aluno você quer consultar o financeiro: {pair}?'
            return f'Para qual aluno você quer consultar isso: {pair}?'
        student_label = focus.student_name or 'o aluno'
        if str(focus.active_task or '').startswith('academic:grades'):
            return f'Você quer a nota, as próximas provas ou a frequência de {student_label}?'
        if str(focus.active_task or '').startswith('academic:upcoming'):
            return f'Você quer saber as próximas provas, as datas ou a disciplina específica de {student_label}?'
        if str(focus.active_task or '').startswith('academic:attendance'):
            return f'Você quer saber a nota, as próximas provas ou a frequência de {student_label}?'
        if str(focus.active_task or '').startswith('finance:'):
            return f'Você quer consultar o financeiro de {student_label}, como próxima fatura, vencimentos ou pagamentos?'
        if str(focus.active_task or '').startswith('public:pricing'):
            return 'Você quer saber a mensalidade, a taxa de matrícula ou fazer uma simulação por quantidade de alunos?'
        return f'Eu ainda não consegui fechar o foco dessa pergunta sobre {student_label}. Você quer nota, próximas provas, frequência ou financeiro?'
    if focus.is_repair_followup:
        if focus.domain == 'academic' and focus.topic == 'grades':
            if focus.student_name and focus.subject_name:
                return f'Você quer só a nota de {focus.subject_name} de {focus.student_name}, ou prefere o boletim completo?'
            if focus.student_name:
                return f'Você quer o boletim completo de {focus.student_name}, ou a nota de uma disciplina específica?'
            if len(linked_names) >= 2:
                pair = f'{linked_names[0]} ou {linked_names[1]}' if len(linked_names) == 2 else ', '.join(linked_names[:4])
                return f'Você quer a nota de qual aluno: {pair}?'
        if focus.domain == 'academic' and focus.topic == 'upcoming_assessments':
            if focus.student_name and focus.subject_name:
                return f'Você quer as próximas provas de {focus.subject_name} para {focus.student_name}, ou quer todas as próximas avaliações dele?'
            if focus.student_name:
                return f'Você quer as próximas provas de {focus.student_name} em geral, ou só de uma disciplina específica?'
        if focus.domain == 'finance' and focus.student_name:
            return f'Você quer a próxima fatura de {focus.student_name}, os vencimentos em aberto ou o histórico de pagamentos?'
        previous_topic = _infer_assistant_message_topic(_last_assistant_message(conversation_context)) or _topic_from_active_task(focus.active_task)
        question_plain = _plain_text(request.message)
        if any(term in question_plain for term in ('essa resposta', 'resposta aqui', 'era sobre o que')):
            if previous_topic:
                return f'A resposta anterior estava falando de {previous_topic}. Se quiser, eu reformulo agora só no foco certo.'
            return 'A resposta anterior parece ter saído do foco. Se quiser, eu reformulo agora só no ponto certo.'
        if any(term in question_plain for term in ('por que', 'porque')):
            if previous_topic:
                return f'Porque a resposta anterior ficou no foco de {previous_topic}. Se quiser, eu corrijo agora só no recorte que você quer.'
            return 'Porque a resposta anterior ficou ampla demais. Se quiser, eu corrijo agora só no recorte certo.'
        return 'Posso corrigir a resposta anterior, mas preciso que você me diga só o foco certo agora: nota, próximas provas, frequência ou financeiro.'
    if (
        request.user.authenticated
        and _question_mentions_upcoming_scope(request.message)
        and isinstance(linked_students, list)
        and len(linked_students) > 1
        and not focus.student_name
    ):
        names = [str(item.get('full_name') or '').strip() for item in linked_students if isinstance(item, dict)]
        names = [name for name in names if name]
        if names:
            if len(names) == 2:
                return f'Para qual aluno você quer consultar isso: {names[0]} ou {names[1]}?'
            return f'Para qual aluno você quer consultar isso? Opções: {", ".join(names[:4])}.'
    question_plain = _plain_text(request.message)
    if _looks_like_relationship_followup(request.message):
        if 'segunda chamada' in question_plain:
            return 'Você quer entender como a segunda chamada se relaciona com a recuperação paralela, ou quer apenas as regras da segunda chamada?'
        return 'Você quer que eu conecte isso ao assunto anterior da conversa, ou prefere só as regras desse item isoladamente?'
    return None


def _answer_experience_changed(original_text: str, candidate_text: str) -> bool:
    return _normalize_text(original_text) != _normalize_text(candidate_text)


def _validated_answer_experience_text(
    *,
    request_message: str,
    original_text: str,
    candidate_text: str,
    focus: AnswerFocusState | None = None,
) -> str | None:
    candidate = _normalize_text(candidate_text)
    original = _normalize_text(original_text)
    if not candidate or candidate.upper() == 'KEEP':
        return None
    question = _plain_text(request_message)
    candidate_plain = _plain_text(candidate)

    requested_subject = _extract_requested_subject(question)
    if requested_subject and requested_subject not in candidate_plain and not _looks_like_explicit_limitation(candidate):
        return None
    if requested_subject and _candidate_mentions_other_subjects(candidate, requested_subject=requested_subject):
        return None

    if _contains_any(question, _QUESTION_FINANCE_HINTS):
        if _contains_monetary_signal(original) and not _contains_monetary_signal(candidate) and not _looks_like_explicit_limitation(candidate):
            return None
        if any(subject in candidate_plain for subject in _SUBJECT_NAMES) or 'nota' in candidate_plain:
            return None

    if _contains_any(question, _QUESTION_ATTENDANCE_HINTS):
        if 'frequ' not in candidate.lower() and 'falta' not in candidate.lower() and not _looks_like_explicit_limitation(candidate):
            return None
        if _question_mentions_unasked_grade_scope(question) is False and ('nota' in candidate_plain or any(subject in candidate_plain for subject in _SUBJECT_NAMES)):
            if not _looks_like_family_attendance_aggregate_request(request_message):
                return None

    if focus is not None:
        if focus.unknown_student_name:
            if 'nao encontrei' not in candidate_plain and 'não encontrei' not in candidate_plain:
                return None
        if focus.unknown_subject_name:
            if (
                ('nota' in candidate_plain or any(subject in candidate_plain for subject in _SUBJECT_NAMES))
                and 'nao encontrei' not in candidate_plain
                and 'não encontrei' not in candidate_plain
                and not _looks_like_explicit_limitation(candidate)
            ):
                return None
        if focus.needs_disambiguation:
            if not (
                focus.asks_family_aggregate
                or _looks_like_family_attendance_aggregate_request(request_message)
            ):
                if not any(term in candidate_plain for term in ('voce quer', 'você quer', 'me diga', 'qual foco', 'qual aluno')):
                    return None
        if focus.is_repair_followup:
            if focus.domain == 'conversation' and (
                any(term in candidate_plain for term in ('nota', 'media', 'média', 'fatura', 'prova', 'avaliac'))
                and not any(term in candidate_plain for term in ('resposta anterior', 'antes', 'corrig', 'expliquei', 'você perguntou', 'voce perguntou'))
            ):
                return None
        if focus.domain == 'academic' and (_contains_monetary_signal(candidate) or any(term in candidate_plain for term in _QUESTION_FINANCE_HINTS)):
            return None
        if focus.domain == 'finance' and ('nota' in candidate_plain or any(subject in candidate_plain for subject in _SUBJECT_NAMES)):
            return None
        if focus.domain == 'public' and focus.topic == 'pricing':
            if any(term in candidate_plain for term in ('fatura', 'boleto', 'alunos vinculados', 'qual aluno')):
                return None
        if focus.domain == 'institution' and focus.topic == 'attendance_justification':
            if 'nota' in candidate_plain or any(subject in candidate_plain for subject in _SUBJECT_NAMES):
                return None
        if focus.topic == 'upcoming_assessments':
            if not any(term in candidate_plain for term in ('avali', 'prova', 'entrega')) and not _looks_like_explicit_limitation(candidate):
                return None
        if focus.student_name:
            requested_student = _plain_text(focus.student_name)
            if requested_student and requested_student.split(' ')[0] not in candidate_plain and not _looks_like_explicit_limitation(candidate):
                if (
                    focus.domain in {'academic', 'finance'}
                    or (focus.domain == 'institution' and focus.topic not in {'attendance_justification'})
                ):
                    return None

    narrow_focus = bool(
        focus is not None and (
            (focus.topic == 'grades' and focus.subject_name)
            or focus.domain == 'finance'
            or (focus.domain == 'public' and focus.topic == 'pricing')
            or focus.topic == 'upcoming_assessments'
        )
    )
    if (
        not narrow_focus
        and len(candidate) < max(20, int(len(original) * 0.2))
        and not _looks_like_explicit_limitation(candidate)
    ):
        return None
    return candidate


def _deterministic_context_repair_plan(
    *,
    request: MessageResponseRequest,
    focus: AnswerFocusState,
    actor: dict[str, Any] | None,
    conversation_context: dict[str, Any] | None = None,
) -> dict[str, Any] | None:
    if looks_like_restricted_document_query(request.message):
        return None
    if not (focus.unknown_student_name or focus.unknown_subject_name or focus.is_repair_followup or focus.needs_disambiguation):
        return None
    message = _clarify_after_retry_message(
        request=request,
        focus=focus,
        actor=actor,
        conversation_context=conversation_context,
    )
    if not message:
        return None
    if focus.unknown_student_name:
        reason = 'unknown_student_reference'
    elif focus.unknown_subject_name:
        reason = 'unknown_subject_reference'
    elif focus.needs_disambiguation:
        reason = 'ambiguous_followup'
    else:
        reason = 'repair_followup'
    return {
        'action': 'clarify',
        'message': message,
        'retry_query': '',
        'confidence': 0.96,
        'reason': reason,
    }


async def _api_core_get(
    *,
    settings: Any,
    path: str,
    params: dict[str, object] | None = None,
) -> dict[str, Any] | None:
    headers = {'X-Internal-Api-Token': settings.internal_api_token}
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(
                f'{settings.api_core_url.rstrip("/")}{path}',
                headers=headers,
                params=params,
            )
        response.raise_for_status()
    except Exception as exc:
        logger.warning('answer_experience_api_core_get_failed', extra={'path': path, 'error': str(exc)})
        return None
    payload = response.json()
    return payload if isinstance(payload, dict) else None


async def _fetch_conversation_context(
    *,
    settings: Any,
    request: MessageResponseRequest,
) -> dict[str, Any] | None:
    conversation_external_id = _conversation_external_id(request)
    if not conversation_external_id:
        return None
    payload = await _api_core_get(
        settings=settings,
        path='/v1/internal/conversations/context',
        params={
            'conversation_external_id': conversation_external_id,
            'channel': request.channel.value,
            'limit': 8,
        },
    )
    return payload if isinstance(payload, dict) else None


async def _fetch_public_school_profile(settings: Any) -> dict[str, Any] | None:
    payload = await _api_core_get(
        settings=settings,
        path='/v1/public/school-profile',
    )
    if not isinstance(payload, dict):
        return None
    profile = payload.get('profile')
    return profile if isinstance(profile, dict) else None


async def _fetch_public_timeline(settings: Any) -> dict[str, Any] | None:
    payload = await _api_core_get(
        settings=settings,
        path='/v1/public/timeline',
    )
    if not isinstance(payload, dict):
        return None
    timeline = payload.get('timeline')
    return timeline if isinstance(timeline, dict) else None


async def _fetch_public_assistant_capabilities(settings: Any) -> dict[str, Any] | None:
    payload = await _api_core_get(
        settings=settings,
        path='/v1/public/assistant-capabilities',
    )
    if not isinstance(payload, dict):
        return None
    capabilities = payload.get('capabilities')
    return capabilities if isinstance(capabilities, dict) else None


async def _fetch_actor_context(
    *,
    settings: Any,
    request: MessageResponseRequest,
) -> dict[str, Any] | None:
    if request.telegram_chat_id is None:
        return None
    payload = await _api_core_get(
        settings=settings,
        path='/v1/internal/identity/context',
        params={'telegram_chat_id': request.telegram_chat_id},
    )
    actor = payload.get('actor') if isinstance(payload, dict) else None
    return actor if isinstance(actor, dict) else None


def _subject_code_from_payload(summary: dict[str, Any] | None, subject_name: str | None) -> str | None:
    if not isinstance(summary, dict) or not subject_name:
        return None
    normalized_subject = _canonical_subject_key(subject_name)
    grades = summary.get('grades')
    if not isinstance(grades, list):
        return None
    for row in grades:
        if not isinstance(row, dict):
            continue
        current_name = _canonical_subject_key(row.get('subject_name'))
        if current_name == normalized_subject:
            subject_code = str(row.get('subject_code') or '').strip()
            if subject_code:
                return subject_code
    return None


def _format_decimal(value: float) -> str:
    return f'{value:.1f}'.replace('.', ',')


def _format_money(value: str | float | int | None) -> str:
    try:
        amount = float(str(value or 0).replace(',', '.'))
    except ValueError:
        return str(value or '')
    return f'R$ {amount:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.')


def _format_date_iso(value: str | None) -> str | None:
    text = str(value or '').strip()
    if not text:
        return None
    try:
        return datetime.fromisoformat(text).strftime('%d/%m/%Y')
    except ValueError:
        try:
            return datetime.strptime(text, '%Y-%m-%d').strftime('%d/%m/%Y')
        except ValueError:
            return text


def _compose_subject_grade_focus(summary: dict[str, Any], *, student_name: str, subject_name: str) -> str | None:
    grades = summary.get('grades')
    if not isinstance(grades, list):
        return None
    subject_rows = [
        row for row in grades
        if isinstance(row, dict) and _canonical_subject_key(row.get('subject_name')) == _canonical_subject_key(subject_name)
    ]
    if not subject_rows:
        return None
    valid_scores: list[float] = []
    for row in subject_rows:
        try:
            score = float(str(row.get('score') or '0').replace(',', '.'))
            max_score = float(str(row.get('max_score') or '0').replace(',', '.'))
        except ValueError:
            continue
        if max_score > 0:
            valid_scores.append((score / max_score) * 10.0)
    if not valid_scores:
        return None
    average = sum(valid_scores) / len(valid_scores)
    return f'Em {subject_name}, {student_name} está com média parcial de {_format_decimal(average)}/10.'


def _compose_grade_timeframe_focus(
    summary: dict[str, Any],
    *,
    student_name: str,
    subject_name: str | None,
) -> str | None:
    grades = summary.get('grades')
    if not isinstance(grades, list):
        return None
    filtered = [row for row in grades if isinstance(row, dict)]
    if subject_name:
        filtered = [
            row for row in filtered
            if _canonical_subject_key(row.get('subject_name')) == _canonical_subject_key(subject_name)
        ]
    if not filtered:
        return None
    term_codes: list[str] = []
    for row in filtered:
        term_code = str(row.get('term_code') or '').strip()
        item_title = str(row.get('item_title') or '').strip()
        if term_code:
            term_codes.append(term_code)
        elif item_title:
            term_codes.append(item_title)
    term_codes = _dedupe_preserve_order(term_codes)
    if not term_codes:
        return None
    if len(term_codes) == 1:
        scope = f' em {subject_name}' if subject_name else ''
        return f'No recorte atual, as notas de {student_name}{scope} são do {term_codes[0]}.'
    scope = f' em {subject_name}' if subject_name else ''
    return f'No recorte atual, as notas de {student_name}{scope} aparecem em: {", ".join(term_codes[:4])}.'


def _compose_all_grades_focus(summary: dict[str, Any], *, student_name: str) -> str | None:
    grades = summary.get('grades')
    if not isinstance(grades, list):
        return None
    per_subject: dict[str, list[float]] = {}
    for row in grades:
        if not isinstance(row, dict):
            continue
        try:
            score = float(str(row.get('score') or '0').replace(',', '.'))
            max_score = float(str(row.get('max_score') or '0').replace(',', '.'))
        except ValueError:
            continue
        subject_name = str(row.get('subject_name') or '').strip()
        if not subject_name or max_score <= 0:
            continue
        per_subject.setdefault(subject_name, []).append((score / max_score) * 10.0)
    if not per_subject:
        return None
    lines = [f'Notas parciais de {student_name}:']
    for subject_name in sorted(per_subject):
        average = sum(per_subject[subject_name]) / len(per_subject[subject_name])
        lines.append(f'- {subject_name}: {_format_decimal(average)}/10')
    return '\n'.join(lines)


def _compose_finance_focus(
    summary: dict[str, Any],
    *,
    student_name: str,
    next_only: bool = False,
    status_filter: str | None = None,
) -> str | None:
    invoices = summary.get('invoices')
    if not isinstance(invoices, list):
        return None
    normalized_invoices = [item for item in invoices if isinstance(item, dict)]
    status_values = {
        part.strip().lower()
        for part in str(status_filter or '').split(',')
        if part.strip()
    }
    if status_values == {'paid'}:
        paid_invoices = [item for item in normalized_invoices if str(item.get('status') or '').strip() == 'paid']
        if not paid_invoices:
            return f'No momento, eu não encontrei pagamentos liquidados para {student_name}.'
        latest_paid = sorted(paid_invoices, key=lambda item: str(item.get('paid_at') or item.get('due_date') or ''))[-1]
        amount = _format_money(latest_paid.get('amount_due') or latest_paid.get('amount_paid'))
        reference = str(latest_paid.get('reference_month') or '').strip()
        return f'O último pagamento identificado de {student_name} foi de {amount}' + (f', referente a {reference}.' if reference else '.')
    if status_values == {'overdue'}:
        overdue_invoices = [item for item in normalized_invoices if str(item.get('status') or '').strip() == 'overdue']
        overdue_invoices.sort(key=lambda item: str(item.get('due_date') or ''))
        if not overdue_invoices:
            return f'No momento, {student_name} não tem faturas vencidas.'
        first_overdue = overdue_invoices[0]
        amount = _format_money(first_overdue.get('amount_due'))
        due_date = _format_date_iso(str(first_overdue.get('due_date') or ''))
        due_suffix = f', vencida desde {due_date}' if due_date else ''
        return f'{student_name} está com {len(overdue_invoices)} fatura(s) vencida(s). A mais antiga está em {amount}{due_suffix}.'
    open_invoices = [item for item in normalized_invoices if str(item.get('status') or '').strip() == 'open']
    open_invoices.sort(key=lambda item: str(item.get('due_date') or ''))
    if next_only:
        next_invoice = open_invoices[0] if open_invoices else None
        if next_invoice is None:
            return f'No momento, {student_name} não tem fatura em aberto.'
        amount = _format_money(next_invoice.get('amount_due'))
        due_date = _format_date_iso(str(next_invoice.get('due_date') or ''))
        reference = str(next_invoice.get('reference_month') or '').strip()
        suffix = f', referente a {reference}' if reference else ''
        due_suffix = f', com vencimento em {due_date}' if due_date else ''
        return f'A próxima fatura de {student_name} está em {amount}{suffix}{due_suffix}.'
    if not open_invoices:
        return f'No momento, {student_name} não tem faturas em aberto.'
    next_invoice = open_invoices[0]
    amount = _format_money(next_invoice.get('amount_due'))
    due_date = _format_date_iso(str(next_invoice.get('due_date') or ''))
    due_suffix = f' e vence em {due_date}' if due_date else ''
    return (
        f'{student_name} está com {len(open_invoices)} fatura(s) em aberto. '
        f'A mais próxima está em {amount}{due_suffix}.'
    )


def _compose_admin_finance_focus(
    *,
    admin_summary: dict[str, Any] | None,
    finance_summary: dict[str, Any] | None,
    student_name: str,
) -> str | None:
    parts: list[str] = []
    if isinstance(admin_summary, dict):
        overall_status = str(admin_summary.get('overall_status') or '').strip()
        next_step = str(admin_summary.get('next_step') or '').strip()
        if overall_status == 'complete':
            parts.append(f'Na documentacao e no cadastro escolar de {student_name}, nao aparece pendencia documental relevante.')
        elif overall_status:
            parts.append(f'Na documentacao e no cadastro escolar de {student_name}, o status atual esta como {overall_status}.')
        if next_step:
            parts.append(next_step)
    if isinstance(finance_summary, dict):
        finance_text = _compose_finance_focus(finance_summary, student_name=student_name)
        if finance_text:
            finance_lead = finance_text[0].lower() + finance_text[1:] if len(finance_text) > 1 else finance_text.lower()
            parts.append(f'No financeiro, {finance_lead}')
    if not parts:
        return None
    return ' '.join(parts)


def _compose_public_pricing_focus(
    *,
    school_profile: dict[str, Any] | None,
    focus: AnswerFocusState,
    request_message: str,
) -> str | None:
    if not isinstance(school_profile, dict):
        return None
    tuition_reference = school_profile.get('tuition_reference')
    if not isinstance(tuition_reference, list):
        return None
    requested_segment = focus.public_pricing_segment
    if not requested_segment and focus.public_pricing_grade_year in {'1o ano', '2o ano', '3o ano'}:
        requested_segment = 'Ensino Medio'
    if not requested_segment and focus.public_pricing_grade_year in {'6o ano', '7o ano', '8o ano', '9o ano'}:
        requested_segment = 'Ensino Fundamental II'
    relevant_rows = [row for row in tuition_reference if isinstance(row, dict)]
    if requested_segment:
        requested_only = [
            row for row in relevant_rows
            if _public_segment_matches(row.get('segment'), requested_segment)
        ]
        if requested_only:
            relevant_rows = requested_only
    if not relevant_rows:
        return None
    quantity = int(focus.public_pricing_quantity) if str(focus.public_pricing_quantity or '').isdigit() else None
    normalized_request = _plain_text(request_message)
    amount_key = focus.public_pricing_price_kind or (
        'monthly_amount'
        if any(
            term in normalized_request
            for term in ('mensalidade', 'valor mensal', 'por mes', 'por mês', 'quanto fica por mes', 'quanto fica por mês')
        )
        else 'enrollment_fee'
    )
    display_segment_label = None
    if relevant_rows:
        display_segment_label = str(relevant_rows[0].get('segment') or requested_segment or 'esse segmento').strip()
    grade_year_label = _normalize_text(focus.public_pricing_grade_year)
    if grade_year_label and display_segment_label:
        display_segment_label = f'{grade_year_label} do {display_segment_label}'
    if quantity and quantity > 0:
        first_row = relevant_rows[0]
        try:
            per_student = float(str(first_row.get(amount_key) or '0').replace(',', '.'))
        except ValueError:
            return None
        asks_both_totals = (
            ('matricula' in normalized_request or 'matrícula' in normalized_request)
            and any(
                term in normalized_request
                for term in ('mensalidade', 'mensal', 'por mes', 'por mês', 'quanto fica por mes', 'quanto fica por mês')
            )
        )
        if asks_both_totals:
            try:
                enrollment_fee = float(str(first_row.get('enrollment_fee') or '0').replace(',', '.'))
                monthly_amount = float(str(first_row.get('monthly_amount') or '0').replace(',', '.'))
            except ValueError:
                return None
            if enrollment_fee <= 0 and monthly_amount <= 0:
                return None
            parts = []
            if enrollment_fee > 0:
                parts.append(
                    f'a taxa total de matrícula fica {quantity} x {_format_money(enrollment_fee)} = {_format_money(enrollment_fee * quantity)}'
                )
            if monthly_amount > 0:
                parts.append(
                    f'a mensalidade de referência por mes fica {quantity} x {_format_money(monthly_amount)} = {_format_money(monthly_amount * quantity)}'
                )
            if not parts:
                return None
            return (
                f'Para {quantity} aluno(s) em {display_segment_label or "esse segmento"}, '
                + ' e '.join(parts)
                + '.'
            )
        if per_student <= 0:
            return None
        total_amount = per_student * quantity
        amount_label = 'mensalidade' if amount_key == 'monthly_amount' else 'taxa de matrícula'
        return (
            f'Para {quantity} aluno(s) em {display_segment_label or "esse segmento"}, usando o valor público de referência de {amount_label}, '
            f'a simulação fica {quantity} x {_format_money(per_student)} = {_format_money(total_amount)}.'
        )
    if len(relevant_rows) == 1:
        row = relevant_rows[0]
        segment_label = display_segment_label or str(row.get('segment') or requested_segment or 'esse segmento').strip()
        shift_label = str(row.get('shift_label') or 'turno regular').strip()
        return (
            f'Para {segment_label} no turno {shift_label}, a mensalidade pública de referência é '
            f'{_format_money(row.get("monthly_amount"))} e a taxa de matrícula é {_format_money(row.get("enrollment_fee"))}.'
        )
    lines = ['Valores públicos de referência:']
    for row in relevant_rows[:4]:
        lines.append(
            f'- {str(row.get("segment") or "Segmento").strip()} ({str(row.get("shift_label") or "turno").strip()}): '
            f'mensalidade {_format_money(row.get("monthly_amount"))} e matrícula {_format_money(row.get("enrollment_fee"))}.'
        )
    return '\n'.join(lines)


def _compose_upcoming_focus(
    summary: dict[str, Any],
    *,
    student_name: str,
    subject_name: str | None,
    count_only: bool,
) -> str | None:
    assessments = summary.get('assessments')
    if not isinstance(assessments, list):
        return None
    filtered = [item for item in assessments if isinstance(item, dict)]
    if subject_name:
        filtered = [
            item for item in filtered
            if _focus_normalize_text(item.get('subject_name')) == _focus_normalize_text(subject_name)
        ]
    filtered.sort(key=lambda item: str(item.get('due_date') or ''))
    if count_only:
        if subject_name:
            return f'Até o momento, {student_name} tem {len(filtered)} avaliação(ões) futura(s) registrada(s) em {subject_name}.'
        return f'Até o momento, {student_name} tem {len(filtered)} avaliação(ões) futura(s) registrada(s).'
    if not filtered:
        if subject_name:
            return f'No momento, eu não encontrei próximas avaliações de {subject_name} para {student_name}.'
        return f'No momento, eu não encontrei próximas avaliações registradas para {student_name}.'
    lines = [f'Próximas avaliações de {student_name}:']
    for item in filtered[:5]:
        subject = str(item.get('subject_name') or '').strip()
        title = str(item.get('item_title') or 'Avaliação').strip()
        due_date = _format_date_iso(str(item.get('due_date') or ''))
        prefix = f'- {subject}: ' if subject else '- '
        lines.append(f'{prefix}{title}' + (f' em {due_date}' if due_date else ''))
    return '\n'.join(lines)


def _compose_attendance_focus(summary: dict[str, Any], *, student_name: str) -> str | None:
    attendance = summary.get('attendance')
    if not isinstance(attendance, list):
        return None
    present = late = absent = 0
    for row in attendance:
        if not isinstance(row, dict):
            continue
        present += int(row.get('present_count') or 0)
        late += int(row.get('late_count') or 0)
        absent += int(row.get('absent_count') or 0)
    return (
        f'No recorte atual, {student_name} tem {present} presença(s), {absent} falta(s) e {late} atraso(s) registrados.'
    )


def _compose_administrative_status_focus(summary: dict[str, Any], *, student_name: str) -> str | None:
    checklist = summary.get('checklist')
    pending_note = ''
    if isinstance(checklist, list):
        for item in checklist:
            if not isinstance(item, dict):
                continue
            if str(item.get('status') or '').strip().lower() == 'pending':
                pending_note = str(item.get('notes') or '').strip()
                break
    next_step = str(summary.get('next_step') or '').strip()
    lines = [f'{student_name} ainda tem pendencias na documentacao.']
    if pending_note:
        lines.append(pending_note)
    if next_step:
        lines.append(f'Proximo passo: {next_step}')
    return ' '.join(line for line in lines if line)


def _compose_family_upcoming_assessments_focus(
    summaries: list[tuple[str, dict[str, Any], dict[str, Any]]]
) -> str | None:
    if not summaries:
        return None
    lines = ['Próximas avaliações das contas vinculadas:']
    for student_name, academic_summary, upcoming_summary in summaries:
        class_name = str(academic_summary.get('class_name') or 'não informada').strip() or 'não informada'
        lines.append(f'- {student_name} ({class_name})')
        for entry in _compose_upcoming_focus(
            upcoming_summary,
            student_name=student_name,
            subject_name=None,
            count_only=False,
        ).splitlines()[1:5]:
            if entry.strip():
                lines.append(f'  {entry}')
    return '\n'.join(lines)


async def _build_supplemental_focus(
    *,
    settings: Any,
    request: MessageResponseRequest,
    focus: AnswerFocusState,
    school_profile: dict[str, Any],
    actor: dict[str, Any] | None,
    conversation_context: dict[str, Any] | None,
) -> dict[str, Any]:
    from .grounded_answer_support_runtime import _build_supplemental_focus as _impl

    return await _impl(
        settings=settings,
        request=request,
        focus=focus,
        school_profile=school_profile,
        actor=actor,
        conversation_context=conversation_context,
    )



def _answer_experience_settings(settings: Any) -> Any:
    provider = str(getattr(settings, 'answer_experience_provider', '') or getattr(settings, 'llm_provider', 'google')).strip()
    return SimpleNamespace(
        llm_provider=provider,
        openai_api_key=getattr(settings, 'answer_experience_openai_api_key', None) or getattr(settings, 'openai_api_key', None),
        openai_base_url=getattr(settings, 'answer_experience_openai_base_url', None) or getattr(settings, 'openai_base_url', None),
        openai_model=getattr(settings, 'answer_experience_openai_model', None) or getattr(settings, 'openai_model', None),
        openai_api_mode=getattr(settings, 'answer_experience_openai_api_mode', None) or getattr(settings, 'openai_api_mode', 'responses'),
        google_api_key=getattr(settings, 'answer_experience_google_api_key', None) or getattr(settings, 'google_api_key', None),
        google_api_base_url=getattr(settings, 'answer_experience_google_api_base_url', None) or getattr(settings, 'google_api_base_url', None),
        google_model=getattr(settings, 'answer_experience_google_model', None) or getattr(settings, 'google_model', None),
    )


def _context_repair_enabled(*, settings: Any, stack_name: str) -> bool:
    if not bool(getattr(settings, 'feature_flag_context_repair_enabled', True)):
        return False
    stack_allowlist = _csv_values(getattr(settings, 'feature_flag_context_repair_stacks', ''))
    if stack_allowlist and stack_name.lower() not in stack_allowlist:
        return False
    return True


def _normalize_context_repair_plan(plan: dict[str, Any] | None) -> dict[str, Any] | None:
    if not isinstance(plan, dict):
        return None
    action = str(plan.get('action') or '').strip().lower()
    if action not in {'keep', 'clarify', 'retry_retrieval', 'unavailable'}:
        return None
    message = _normalize_text(plan.get('message'))
    retry_query = _normalize_text(plan.get('retry_query'))
    try:
        confidence = float(plan.get('confidence') or 0.0)
    except Exception:
        confidence = 0.0
    confidence = max(0.0, min(confidence, 1.0))
    reason = _normalize_text(plan.get('reason'))
    return {
        'action': action,
        'message': message,
        'retry_query': retry_query,
        'confidence': confidence,
        'reason': reason,
    }


def _retry_visibility_for_response(response: MessageResponse) -> str | None:
    if response.classification.access_tier == AccessTier.public:
        return 'public'
    if response.retrieval_backend != RetrievalBackend.none:
        return 'restricted'
    return None


def _fallback_retry_query(
    *,
    request: MessageResponseRequest,
    focus: AnswerFocusState,
    recent_user_messages: list[str],
) -> str:
    parts: list[str] = [request.message]
    request_plain = _plain_text(request.message)
    if focus.student_name:
        parts.append(f'aluno {focus.student_name}')
    if focus.subject_name:
        parts.append(f'disciplina {focus.subject_name}')
    if focus.topic:
        parts.append(f'topico {focus.topic}')
    if any(term in request_plain for term in ('novidade', 'novidades', 'festa', 'festas', 'evento', 'eventos', 'formatura')):
        parts.append('eventos festas formatura calendario escolar 2026')
    if recent_user_messages:
        parts.append(f'contexto recente: {recent_user_messages[-1]}')
    return ' | '.join(part for part in parts if _normalize_text(part))


def _build_retry_evidence(search: Any) -> tuple[str | None, list[str]]:
    document_groups = list(getattr(search, 'document_groups', []) or [])
    hits = list(getattr(search, 'hits', []) or [])
    evidence_lines: list[str] = []
    draft_lines: list[str] = []
    for group in document_groups[:4]:
        title = _normalize_text(getattr(group, 'document_title', None))
        section = _normalize_text(getattr(group, 'primary_section', None))
        summary = _normalize_text(getattr(group, 'primary_summary', None) or getattr(group, 'primary_excerpt', None))
        if title or summary:
            evidence_lines.append(' | '.join(part for part in (title, section, summary) if part))
        if summary:
            draft_lines.append(f'- {summary}')
    if not draft_lines:
        for hit in hits[:4]:
            title = _normalize_text(getattr(hit, 'document_title', None))
            section = _normalize_text(getattr(hit, 'section_title', None) or getattr(hit, 'section_path', None))
            excerpt = _normalize_text(getattr(hit, 'contextual_summary', None) or getattr(hit, 'text_excerpt', None))
            if title or excerpt:
                evidence_lines.append(' | '.join(part for part in (title, section, excerpt) if part))
            if excerpt:
                draft_lines.append(f'- {excerpt}')
    draft_text = None
    if draft_lines:
        draft_text = 'Segunda tentativa de busca encontrou estes pontos:\n' + '\n'.join(draft_lines[:4])
    return draft_text, _dedupe_preserve_order(evidence_lines)


def _retry_search_has_signal(search: Any) -> bool:
    if search is None:
        return False
    document_groups = list(getattr(search, 'document_groups', []) or [])
    hits = list(getattr(search, 'hits', []) or [])
    return bool(document_groups or hits)


async def _attempt_second_retrieval(
    *,
    settings: Any,
    request: MessageResponseRequest,
    response: MessageResponse,
    retry_query: str,
    focus: AnswerFocusState,
    recent_messages: list[str],
    school_profile: dict[str, Any] | None,
    provider_settings: Any,
    actor_summary: str,
) -> MessageResponse | None:
    visibility = _retry_visibility_for_response(response)
    if not visibility:
        return None
    retrieval_service = get_retrieval_service(
        database_url=settings.database_url,
        qdrant_url=settings.qdrant_url,
        collection_name=settings.qdrant_documents_collection,
        embedding_model=settings.document_embedding_model,
        enable_query_variants=settings.retrieval_enable_query_variants,
        enable_late_interaction_rerank=settings.retrieval_enable_late_interaction_rerank,
        late_interaction_model=settings.retrieval_late_interaction_model,
        candidate_pool_size=settings.retrieval_candidate_pool_size,
        cheap_candidate_pool_size=settings.retrieval_cheap_candidate_pool_size,
        deep_candidate_pool_size=settings.retrieval_deep_candidate_pool_size,
        rerank_fused_weight=settings.retrieval_rerank_fused_weight,
        rerank_late_interaction_weight=settings.retrieval_rerank_late_interaction_weight,
        enable_cross_encoder_rerank=bool(
            getattr(settings, 'retrieval_enable_cross_encoder_rerank', False)
        ),
        cross_encoder_model=getattr(
            settings,
            'retrieval_cross_encoder_model',
            'jinaai/jina-reranker-v2-base-multilingual',
        ),
        rerank_cross_encoder_weight=float(
            getattr(settings, 'retrieval_rerank_cross_encoder_weight', 0.0) or 0.0
        ),
    )
    search = retrieval_service.hybrid_search(
        query=retry_query,
        top_k=int(getattr(settings, 'feature_flag_context_repair_retry_top_k', 6) or 6),
        visibility=visibility,
        category=None,
        profile=RetrievalProfile.deep,
    )
    if not _retry_search_has_signal(search):
        return None
    draft_text, retry_evidence_lines = _build_retry_evidence(search)
    if not draft_text:
        return None
    candidate_text = await compose_grounded_answer_experience_with_provider(
        settings=provider_settings,
        request_message=request.message,
        draft_text=draft_text,
        mode=response.mode.value,
        domain=response.classification.domain.value,
        access_tier=response.classification.access_tier.value,
        selected_tools=list(response.selected_tools),
        evidence_lines=retry_evidence_lines,
        recent_messages=recent_messages,
        school_profile=school_profile,
        reason=f'{response.reason} | second_retrieval_retry',
        focus_summary=build_focus_summary(focus),
    )
    validated = _validated_answer_experience_text(
        request_message=request.message,
        original_text=response.message_text,
        candidate_text=candidate_text or '',
        focus=focus,
    )
    if not validated or _looks_like_grounding_weakness(validated) or _looks_like_explicit_limitation(validated):
        return None
    llm_stages = [str(item).strip() for item in (response.llm_stages or []) if str(item).strip()]
    for stage in ('context_repair_planner', 'retrieval_retry_answer'):
        if stage not in llm_stages:
            llm_stages.append(stage)
    return response.model_copy(
        update={
            'message_text': validated,
            'used_llm': True,
            'llm_stages': llm_stages,
            'answer_experience_eligible': True,
            'answer_experience_applied': True,
            'answer_experience_reason': 'context_repair:second_retrieval_retry',
            'answer_experience_provider': provider_settings.llm_provider,
            'answer_experience_model': provider_settings.google_model if provider_settings.llm_provider in {'google', 'gemini'} else provider_settings.openai_model,
            'context_repair_applied': True,
            'context_repair_action': 'retry_retrieval',
            'context_repair_reason': 'second_retrieval_retry',
            'retrieval_retry_applied': True,
            'retrieval_retry_reason': retry_query,
        }
    )


def _terminal_semantic_ingress_act(response: MessageResponse) -> str | None:
    reason = _normalize_text(getattr(response, 'reason', ''))
    prefixes = (
        'python_functions_semantic_ingress:',
        'python_functions_native_semantic_ingress:',
        'llamaindex_semantic_ingress:',
        'llamaindex_native_semantic_ingress:',
        'langgraph_semantic_ingress:',
        'specialist_semantic_ingress:',
        'specialist_supervisor_fast_path:',
    )
    for prefix in prefixes:
        if reason.startswith(prefix):
            act = reason.removeprefix(prefix).split('|', 1)[0].strip()
            if is_terminal_ingress_act(act):
                return act
    for item in list(getattr(response, 'graph_path', []) or []):
        normalized = _normalize_text(item)
        if 'semantic_ingress:' not in normalized:
            continue
        act = normalized.rsplit('semantic_ingress:', 1)[-1].strip()
        if is_terminal_ingress_act(act):
            return act
    return None


def _response_has_terminal_semantic_ingress(response: MessageResponse) -> bool:
    return _terminal_semantic_ingress_act(response) is not None


def _localize_surface_labels_for_request(*, request_message: str, text: str) -> str:
    localized = str(text or '').strip()
    if not localized:
        return localized
    if looks_like_language_preference_feedback(request_message):
        localized = re.sub(r'(?i)\badmissions\b', 'matricula e atendimento comercial', localized)
        localized = re.sub(r'(?i)\bsales\b', 'atendimento comercial', localized)
        localized = localized.replace(
            'matricula e atendimento comercial e atendimento comercial',
            'matricula e atendimento comercial',
        )
    return localized


def _filtered_recent_messages(
    *,
    conversation_context: dict[str, Any] | None,
    focus: AnswerFocusState,
) -> list[str]:
    recent_messages = _extract_recent_messages(conversation_context)
    if not recent_messages:
        return recent_messages
    if focus.domain == 'finance':
        filtered = [line for line in recent_messages if 'nota' not in _plain_text(line) and not any(subject in _plain_text(line) for subject in _SUBJECT_NAMES)]
        return filtered[-4:] or recent_messages[-4:]
    if focus.domain == 'institution' and focus.topic == 'attendance_justification':
        filtered = [line for line in recent_messages if 'nota' not in _plain_text(line) and 'media' not in _plain_text(line)]
        return filtered[-4:] or recent_messages[-4:]
    return recent_messages[-4:]


def _should_prefer_supplemental_focus(
    *,
    request_message: str,
    original_text: str,
    focus: AnswerFocusState,
    supplemental_focused_draft: str | None,
) -> bool:
    if not _normalize_text(supplemental_focused_draft):
        return False
    if focus.needs_disambiguation and not _looks_like_family_attendance_aggregate_request(request_message):
        return False
    if focus.asks_family_aggregate or _looks_like_family_attendance_aggregate_request(request_message):
        return True
    if focus.domain == 'public' and focus.topic == 'known_unknown':
        return True
    if focus.unknown_subject_name:
        return True
    if _looks_like_student_resolution_failure(original_text):
        return True
    if focus.domain == 'finance':
        return True
    if focus.domain == 'public' and focus.topic == 'pricing':
        return True
    if focus.topic in {'upcoming_assessments', 'attendance', 'admin_finance_combo', 'administrative_status'}:
        return True
    if focus.topic == 'grades' and focus.subject_name:
        return True
    if focus.domain == 'institution' and focus.topic == 'attendance_justification':
        return True
    return False


def _preserve_deterministic_answer_surface(
    *,
    request: MessageResponseRequest,
    response: MessageResponse,
    focus: AnswerFocusState,
    actor: dict[str, Any] | None,
    conversation_context: dict[str, Any] | None,
) -> str | None:
    from .grounded_answer_support_runtime import _preserve_deterministic_answer_surface as _impl

    return _impl(
        request=request,
        response=response,
        focus=focus,
        actor=actor,
        conversation_context=conversation_context,
    )



async def apply_grounded_answer_experience(
    *,
    request: MessageResponseRequest,
    response: MessageResponse,
    settings: Any,
    stack_name: str,
    forced_reason: str | None = None,
) -> MessageResponse:
    from .public_orchestration_runtime import (
        _compose_scope_boundary_answer as _compose_scope_boundary_answer_local,
    )
    from .grounded_answer_pipeline_runtime import apply_grounded_answer_experience as _impl

    normalized_message = _normalize_text(request.message)
    if any(
        term in normalized_message
        for term in {
            'sem relacao com escola',
            'sem relacao com a escola',
            'fora do tema escolar',
            'fora do tema da escola',
            'fora do escopo da escola',
            'fora do contexto da escola',
            'sem relacao com o colegio',
            'sem relacao com o colégio',
            'sem relacao com o colegio horizonte',
            'sem relacao com o colégio horizonte',
            'nada a ver com escola',
            'nada a ver com a escola',
            'sem relacao com ensino',
        }
    ):
        base_reason = forced_reason or str(
            getattr(response, 'answer_experience_reason', None)
            or getattr(response, 'reason', None)
            or 'contextual_answer_repair'
        )
        return response.model_copy(
            update={
                'message_text': _compose_scope_boundary_answer_local({}, conversation_context=None),
                'answer_experience_eligible': True,
                'answer_experience_applied': True,
                'answer_experience_reason': f'{base_reason}:explicit_open_world_scope_boundary',
            }
        )

    return await _impl(
        request=request,
        response=response,
        settings=settings,
        stack_name=stack_name,
        forced_reason=forced_reason,
    )
