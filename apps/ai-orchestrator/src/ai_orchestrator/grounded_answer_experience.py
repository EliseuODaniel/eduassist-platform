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
    RetrievalBackend,
    RetrievalProfile,
)
from .public_doc_knowledge import (
    compose_public_bolsas_and_processes,
    compose_public_calendar_visibility,
    compose_public_first_month_risks,
    compose_public_health_emergency_bundle,
    compose_public_outings_authorizations,
    compose_public_permanence_and_family_support,
    compose_public_teacher_directory_boundary,
)
from .public_known_unknowns import compose_public_known_unknown_answer, detect_public_known_unknown_key
from .retrieval import get_retrieval_service

logger = logging.getLogger(__name__)
_ANSWER_FOCUS_CACHE_TTL_SECONDS = 900.0
_ANSWER_FOCUS_CACHE: dict[str, dict[str, Any]] = {}

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
    closest_student_name: str | None = None
    closest_subject_name: str | None = None
    closest_gap: float | None = None
    for summary in summaries:
        student_name = str(summary.get('student_name') or 'Aluno').strip() or 'Aluno'
        averages = _academic_subject_averages_from_summary(summary)
        if not averages:
            lines.append(f'- {student_name}: sem notas consolidadas neste recorte.')
            continue
        preview_items = averages[:4]
        preview = '; '.join(f'{name} {value:.1f}'.replace('.', ',') for name, value in preview_items)
        lines.append(f'- {student_name}: {preview}')
        candidate_subject, candidate_value = min(
            averages,
            key=lambda item: (abs(item[1] - _PASSING_GRADE_TARGET), item[0]),
        )
        gap = abs(candidate_value - _PASSING_GRADE_TARGET)
        if closest_gap is None or gap < closest_gap:
            closest_gap = gap
            closest_student_name = student_name
            closest_subject_name = candidate_subject
    if closest_student_name and closest_subject_name:
        lines.append(
            f'Quem hoje aparece mais perto da media minima e {closest_student_name}, principalmente em {closest_subject_name}.'
        )
    return '\n'.join(lines)


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


def _question_mentions_unasked_grade_scope(question: str) -> bool:
    return _contains_any(question, _QUESTION_GRADE_HINTS) or _extract_requested_subject(question) is not None


def _question_mentions_unasked_finance_scope(question: str) -> bool:
    return _contains_any(question, _QUESTION_FINANCE_HINTS)


def _question_mentions_unasked_attendance_scope(question: str) -> bool:
    return _contains_any(question, _QUESTION_ATTENDANCE_HINTS)


def _question_mentions_upcoming_scope(question: str) -> bool:
    return any(term in _plain_text(question) for term in ('prova', 'avaliac', 'entrega'))


def _question_mentions_public_pricing_scope(question: str) -> bool:
    return _contains_any(question, _QUESTION_PUBLIC_PRICING_HINTS)


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
    if _question_mentions_unasked_finance_scope(question_plain):
        if not (_contains_monetary_signal(response_text) or any(term in response_plain for term in ('fatura', 'boleto', 'financeiro'))):
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


def _question_mentions_public_teacher_directory(message: str) -> bool:
    normalized = _plain_text(message)
    if not any(term in normalized for term in ('professor', 'professora', 'docente')):
        return False
    return any(term in normalized for term in ('contato', 'telefone', 'whatsapp', 'email', 'divulga', 'encaminha'))


def _question_mentions_public_permanence_support(message: str) -> bool:
    normalized = _plain_text(message)
    if 'famil' not in normalized:
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


def _deterministic_public_direct_answer(
    *,
    request: MessageResponseRequest,
    response: MessageResponse,
    school_profile: dict[str, Any] | None,
) -> str | None:
    if response.classification.access_tier is not AccessTier.public:
        return None
    if _question_mentions_public_teacher_directory(request.message):
        return compose_public_teacher_directory_boundary(school_profile)
    if _question_mentions_public_permanence_support(request.message):
        return compose_public_permanence_and_family_support(school_profile)
    if _question_mentions_public_first_month_risks(request.message):
        return compose_public_first_month_risks(school_profile)
    if _question_mentions_public_visibility_boundary(request.message):
        return compose_public_calendar_visibility(school_profile)
    if _question_mentions_public_bolsas_and_processes(request.message):
        return compose_public_bolsas_and_processes(school_profile)
    if _question_mentions_public_health_emergency_bundle(request.message):
        return compose_public_health_emergency_bundle()
    if _question_mentions_public_outings_authorizations(request.message):
        return compose_public_outings_authorizations()
    known_unknown_key = detect_public_known_unknown_key(request.message)
    if known_unknown_key:
        return compose_public_known_unknown_answer(
            key=known_unknown_key,
            school_name=str((school_profile or {}).get('school_name') or 'Colegio Horizonte'),
        )
    return None


def _infer_assistant_message_topic(message: str | None) -> str | None:
    normalized = _plain_text(message)
    if not normalized:
        return None
    if any(term in normalized for term in ('mensalidade', 'matricula', 'taxa de matricula', 'taxa de matrícula')):
        return 'mensalidade e matrícula'
    if any(term in normalized for term in ('fatura', 'boleto', 'financeiro', 'vencimento')) or _contains_monetary_signal(message or ''):
        return 'financeiro'
    if any(term in normalized for term in ('proximas avaliacoes', 'próximas avaliações', 'proximas provas', 'próximas provas', 'avaliacao', 'avaliação', 'entrega')):
        return 'próximas avaliações'
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
        return 'próximas avaliações'
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
        previous_topic = _topic_from_active_task(focus.active_task) or _infer_assistant_message_topic(_last_assistant_message(conversation_context))
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
            parts.append(f'No cadastro escolar de {student_name}, não aparece pendência documental relevante.')
        elif overall_status:
            parts.append(f'No cadastro escolar de {student_name}, o status atual está como {overall_status}.')
        if next_step:
            parts.append(next_step)
    if isinstance(finance_summary, dict):
        finance_text = _compose_finance_focus(finance_summary, student_name=student_name)
        if finance_text:
            parts.append(finance_text)
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
        'monthly_amount' if 'mensalidade' in normalized_request or 'valor mensal' in normalized_request else 'enrollment_fee'
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
            and ('mensalidade' in normalized_request or 'mensal' in normalized_request)
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
    school_profile: dict[str, Any] | None = None,
    actor: dict[str, Any] | None = None,
) -> dict[str, Any] | None:
    if focus.topic == 'attendance_justification':
        return {
            'focused_draft': (
                'Para justificar faltas, a escola aceita atestado médico ou odontológico formal. '
                'Um atestado de "ficar dormindo" não serve como justificativa válida. '
                'Se houver dúvida, o documento deve ser apresentado à secretaria da escola.'
            ),
            'evidence_lines': ['Política pública | justificativa de faltas exige documento médico formal'],
        }
    if focus.domain == 'public' and focus.topic == 'known_unknown':
        known_unknown_key = detect_public_known_unknown_key(request.message)
        focused_draft = compose_public_known_unknown_answer(
            key=known_unknown_key or '',
            school_name=str((school_profile or {}).get('school_name') or 'Colegio Horizonte'),
        )
        if focused_draft:
            return {
                'focused_draft': focused_draft,
                'evidence_lines': [f'Conhecido indisponível | {known_unknown_key or "nao_informado"}'],
            }
    if focus.domain == 'public' and focus.topic == 'pricing':
        focused_draft = _compose_public_pricing_focus(
            school_profile=school_profile,
            focus=focus,
            request_message=request.message,
        )
        if not focused_draft:
            return None
        return {
            'focused_draft': focused_draft,
            'evidence_lines': [f'Foco resolvido | {focused_draft}'],
        }
    if request.telegram_chat_id is not None and focus.asks_family_aggregate and not focus.student_id and isinstance(actor, dict):
        linked_students = actor.get('linked_students')
        if isinstance(linked_students, list):
            if focus.topic == 'upcoming_assessments':
                summaries: list[tuple[str, dict[str, Any], dict[str, Any]]] = []
                for student in linked_students:
                    if not isinstance(student, dict):
                        continue
                    student_id = str(student.get('student_id') or '').strip()
                    student_name = str(student.get('full_name') or 'Aluno').strip() or 'Aluno'
                    if not student_id:
                        continue
                    academic_payload = await _api_core_get(
                        settings=settings,
                        path=f'/v1/students/{student_id}/academic-summary',
                        params={'telegram_chat_id': request.telegram_chat_id},
                    )
                    academic_summary = academic_payload.get('summary') if isinstance(academic_payload, dict) else None
                    upcoming_payload = await _api_core_get(
                        settings=settings,
                        path=f'/v1/students/{student_id}/upcoming-assessments',
                        params={'telegram_chat_id': request.telegram_chat_id},
                    )
                    upcoming_summary = upcoming_payload.get('summary') if isinstance(upcoming_payload, dict) else None
                    if isinstance(academic_summary, dict) and isinstance(upcoming_summary, dict):
                        summaries.append((student_name, academic_summary, upcoming_summary))
                focused_draft = _compose_family_upcoming_assessments_focus(summaries)
                if focused_draft:
                    return {
                        'focused_draft': focused_draft,
                        'evidence_lines': [f'Foco agregado | {focused_draft}'],
                    }
            summaries: list[dict[str, Any]] = []
            path_suffix = 'academic-summary' if focus.domain == 'academic' else 'financial-summary'
            for student in linked_students:
                if not isinstance(student, dict):
                    continue
                student_id = str(student.get('student_id') or '').strip()
                if not student_id:
                    continue
                payload = await _api_core_get(
                    settings=settings,
                    path=f'/v1/students/{student_id}/{path_suffix}',
                    params={'telegram_chat_id': request.telegram_chat_id},
                )
                summary = payload.get('summary') if isinstance(payload, dict) else None
                if isinstance(summary, dict):
                    summaries.append(summary)
            focused_draft = (
                _compose_family_academic_focus(summaries)
                if focus.domain == 'academic'
                else _compose_family_finance_focus(summaries)
            )
            if focused_draft:
                return {
                    'focused_draft': focused_draft,
                    'evidence_lines': [f'Foco agregado | {focused_draft}'],
                }
    if request.telegram_chat_id is None or not focus.student_id:
        return None
    base_params = {'telegram_chat_id': request.telegram_chat_id}
    academic_payload = finance_payload = admin_payload = upcoming_payload = None
    needs_academic = focus.domain == 'academic'
    needs_finance = focus.domain == 'finance'
    needs_admin = focus.domain == 'institution' and focus.topic == 'administrative_status'
    needs_combo = focus.domain == 'institution' and focus.topic == 'admin_finance_combo'
    if focus.topic == 'attendance_justification':
        needs_admin = False
    tasks: list[asyncio.Future] = []
    task_names: list[str] = []
    if needs_academic or focus.topic in {'attendance_justification'}:
        tasks.append(_api_core_get(settings=settings, path=f'/v1/students/{focus.student_id}/academic-summary', params=base_params))
        task_names.append('academic')
    if needs_finance or needs_combo:
        tasks.append(_api_core_get(settings=settings, path=f'/v1/students/{focus.student_id}/financial-summary', params=base_params))
        task_names.append('finance')
    if needs_admin or needs_combo:
        tasks.append(_api_core_get(settings=settings, path=f'/v1/students/{focus.student_id}/administrative-status', params=base_params))
        task_names.append('admin')
    results = await asyncio.gather(*tasks) if tasks else []
    for name, payload in zip(task_names, results, strict=False):
        if name == 'academic':
            academic_payload = payload
        elif name == 'finance':
            finance_payload = payload
        elif name == 'admin':
            admin_payload = payload

    academic_summary = academic_payload.get('summary') if isinstance(academic_payload, dict) else None
    finance_summary = finance_payload.get('summary') if isinstance(finance_payload, dict) else None
    admin_summary = admin_payload.get('summary') if isinstance(admin_payload, dict) else None

    if focus.topic == 'upcoming_assessments':
        subject_code = _subject_code_from_payload(academic_summary, focus.subject_name)
        upcoming_payload = await _api_core_get(
            settings=settings,
            path=f'/v1/students/{focus.student_id}/upcoming-assessments',
            params={**base_params, **({'subject_code': subject_code} if subject_code else {})},
        )

    focused_draft: str | None = None
    evidence_lines: list[str] = []
    if isinstance(academic_summary, dict) and focus.unknown_subject_name:
        grades = academic_summary.get('grades')
        available_subjects = [
            str(row.get('subject_name') or '').strip()
            for row in grades or []
            if isinstance(row, dict) and str(row.get('subject_name') or '').strip()
        ]
        available_subjects = list(dict.fromkeys(available_subjects))
        preview = ', '.join(available_subjects[:6])
        focused_draft = (
            f'Não encontrei a disciplina {focus.unknown_subject_name} para {focus.student_name or "o aluno"} neste registro.'
            + (f' As disciplinas disponíveis aqui incluem: {preview}.' if preview else '')
        )
    elif isinstance(academic_summary, dict) and focus.topic == 'grades':
        if _question_mentions_timeframe_scope(request.message):
            focused_draft = _compose_grade_timeframe_focus(
                academic_summary,
                student_name=focus.student_name or 'Aluno',
                subject_name=focus.subject_name,
            )
        if not focused_draft:
            focused_draft = (
                _compose_subject_grade_focus(academic_summary, student_name=focus.student_name or 'Aluno', subject_name=focus.subject_name)
                if focus.subject_name
                else _compose_all_grades_focus(academic_summary, student_name=focus.student_name or 'Aluno')
            )
    elif isinstance(academic_summary, dict) and focus.topic == 'attendance':
        focused_draft = _compose_attendance_focus(academic_summary, student_name=focus.student_name or 'Aluno')
    elif isinstance(upcoming_payload, dict) and focus.topic == 'upcoming_assessments':
        focused_draft = _compose_upcoming_focus(
            upcoming_payload.get('summary') if isinstance(upcoming_payload, dict) else {},
            student_name=focus.student_name or 'Aluno',
            subject_name=focus.subject_name,
            count_only='quant' in _plain_text(request.message),
        )
    elif isinstance(finance_summary, dict) and focus.domain == 'finance':
        focused_draft = _compose_finance_focus(
            finance_summary,
            student_name=focus.student_name or 'Aluno',
            next_only=(
                focus.finance_attribute == 'next_due'
                or any(term in _plain_text(request.message) for term in ('proxima', 'próxima', 'proximo', 'próximo'))
            ),
            status_filter=focus.finance_status_filter,
        )
    elif isinstance(admin_summary, dict) and focus.domain == 'institution' and focus.topic == 'administrative_status':
        focused_draft = _compose_administrative_status_focus(
            admin_summary,
            student_name=focus.student_name or 'Aluno',
        )
    elif focus.domain == 'institution' and isinstance(admin_summary, dict) and isinstance(finance_summary, dict):
        focused_draft = _compose_admin_finance_focus(
            admin_summary=admin_summary,
            finance_summary=finance_summary,
            student_name=focus.student_name or 'Aluno',
        )

    if focused_draft:
        evidence_lines.append(f'Foco resolvido | {focused_draft}')
    if isinstance(finance_summary, dict):
        open_count = str(finance_summary.get('open_invoice_count') or '')
        overdue_count = str(finance_summary.get('overdue_invoice_count') or '')
        evidence_lines.append(f'Financeiro | aberto={open_count} | vencido={overdue_count}')
    if isinstance(admin_summary, dict):
        evidence_lines.append(
            f"Administrativo | status={str(admin_summary.get('overall_status') or '').strip()} | proximo_passo={str(admin_summary.get('next_step') or '').strip()}"
        )
    if isinstance(upcoming_payload, dict):
        summary = upcoming_payload.get('summary')
        assessments = summary.get('assessments') if isinstance(summary, dict) else None
        if isinstance(assessments, list):
            evidence_lines.append(f'Avaliacoes futuras | total={len(assessments)}')
    return {
        'focused_draft': focused_draft,
        'evidence_lines': [line for line in evidence_lines if line],
    }


def _answer_experience_settings(settings: Any) -> Any:
    provider = str(getattr(settings, 'answer_experience_provider', '') or getattr(settings, 'llm_provider', 'google')).strip()
    return SimpleNamespace(
        llm_provider=provider,
        openai_api_key=getattr(settings, 'answer_experience_openai_api_key', None) or getattr(settings, 'openai_api_key', None),
        openai_base_url=getattr(settings, 'answer_experience_openai_base_url', None) or getattr(settings, 'openai_base_url', None),
        openai_model=getattr(settings, 'answer_experience_openai_model', None) or getattr(settings, 'openai_model', None),
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
    if focus.needs_disambiguation:
        return False
    if focus.asks_family_aggregate:
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


async def apply_grounded_answer_experience(
    *,
    request: MessageResponseRequest,
    response: MessageResponse,
    settings: Any,
    stack_name: str,
    forced_reason: str | None = None,
) -> MessageResponse:
    reason = forced_reason or _eligible_reason(
        request=request,
        response=response,
        settings=settings,
        stack_name=stack_name,
    )
    if not _answer_experience_pipeline_enabled(
        request=request,
        response=response,
        settings=settings,
        stack_name=stack_name,
    ):
        return response
    base_reason = reason or 'contextual_answer_repair'

    conversation_external_id = _conversation_external_id(request)
    conversation_context, school_profile, actor = await asyncio.gather(
        _fetch_conversation_context(settings=settings, request=request),
        _fetch_public_school_profile(settings),
        _fetch_actor_context(settings=settings, request=request),
    )
    conversation_context = _merge_conversation_context_with_cached_focus(
        conversation_context,
        cached_slot_memory=_cached_focus_slot_memory(conversation_external_id),
    )
    focus = resolve_answer_focus(
        request_message=request.message,
        actor=actor,
        conversation_context=conversation_context,
    )
    _store_focus_cache(
        conversation_external_id=conversation_external_id,
        focus=focus,
    )
    supplemental = await _build_supplemental_focus(
        settings=settings,
        request=request,
        focus=focus,
        school_profile=school_profile,
        actor=actor,
    )
    provider_settings = _answer_experience_settings(settings)
    actor_summary = _actor_summary(actor)
    evidence_lines = _dedupe_preserve_order(
        [*(supplemental or {}).get('evidence_lines', []), *_build_evidence_lines(response)]
    )
    recent_messages = _filtered_recent_messages(conversation_context=conversation_context, focus=focus)
    recent_user_messages = _extract_recent_user_messages(conversation_context)
    supplemental_focused_draft = str((supplemental or {}).get('focused_draft') or '')
    effective_draft_text = supplemental_focused_draft or response.message_text

    deterministic_public_calendar = _deterministic_public_calendar_followup(
        request=request,
        response=response,
        conversation_context=conversation_context,
    )
    if deterministic_public_calendar:
        return response.model_copy(
            update={
                'message_text': deterministic_public_calendar,
                'answer_experience_eligible': True,
                'answer_experience_applied': _answer_experience_changed(response.message_text, deterministic_public_calendar),
                'answer_experience_reason': f'{base_reason}:public_temporal_followup',
                'answer_experience_provider': provider_settings.llm_provider,
                'answer_experience_model': provider_settings.google_model if provider_settings.llm_provider in {'google', 'gemini'} else provider_settings.openai_model,
            }
        )

    deterministic_public_capacity, deterministic_capacity_mode = _deterministic_public_capacity_followup(
        request=request,
        response=response,
        conversation_context=conversation_context,
    )
    if deterministic_public_capacity:
        return response.model_copy(
            update={
                'message_text': deterministic_public_capacity,
                'mode': deterministic_capacity_mode or response.mode,
                'answer_experience_eligible': True,
                'answer_experience_applied': _answer_experience_changed(response.message_text, deterministic_public_capacity),
                'answer_experience_reason': f'{base_reason}:public_capacity_followup',
                'answer_experience_provider': provider_settings.llm_provider,
                'answer_experience_model': provider_settings.google_model if provider_settings.llm_provider in {'google', 'gemini'} else provider_settings.openai_model,
            }
        )

    deterministic_public_direct = _deterministic_public_direct_answer(
        request=request,
        response=response,
        school_profile=school_profile,
    )
    if deterministic_public_direct:
        return response.model_copy(
            update={
                'message_text': deterministic_public_direct,
                'mode': OrchestrationMode.structured_tool,
                'answer_experience_eligible': True,
                'answer_experience_applied': _answer_experience_changed(response.message_text, deterministic_public_direct),
                'answer_experience_reason': f'{base_reason}:public_direct_answer',
                'answer_experience_provider': provider_settings.llm_provider,
                'answer_experience_model': provider_settings.google_model if provider_settings.llm_provider in {'google', 'gemini'} else provider_settings.openai_model,
            }
        )

    if _should_prefer_supplemental_focus(
        request_message=request.message,
        original_text=response.message_text,
        focus=focus,
        supplemental_focused_draft=supplemental_focused_draft,
    ):
        validated_direct = _validated_answer_experience_text(
            request_message=request.message,
            original_text=response.message_text,
            candidate_text=supplemental_focused_draft,
            focus=focus,
        )
        if validated_direct:
            resolved_mode = (
                OrchestrationMode.structured_tool
                if response.mode == OrchestrationMode.clarify
                else response.mode
            )
            return response.model_copy(
                update={
                    'message_text': validated_direct,
                    'mode': resolved_mode,
                    'used_llm': bool(response.used_llm),
                    'answer_experience_eligible': True,
                    'answer_experience_applied': _answer_experience_changed(response.message_text, validated_direct),
                    'answer_experience_reason': f'{base_reason}:supplemental_focus_direct',
                    'answer_experience_provider': provider_settings.llm_provider,
                    'answer_experience_model': provider_settings.google_model if provider_settings.llm_provider in {'google', 'gemini'} else provider_settings.openai_model,
                }
            )

    if _context_repair_enabled(settings=settings, stack_name=stack_name) and _should_attempt_context_repair(
        request=request,
        response=response,
        focus=focus,
        actor=actor,
    ):
        deterministic_plan = _deterministic_context_repair_plan(
            request=request,
            focus=focus,
            actor=actor,
            conversation_context=conversation_context,
        )
        repair_plan = _normalize_context_repair_plan(
            await plan_context_repair_with_provider(
                settings=provider_settings,
                request_message=request.message,
                draft_text=effective_draft_text,
                mode=response.mode.value,
                domain=response.classification.domain.value,
                access_tier=response.classification.access_tier.value,
                selected_tools=list(response.selected_tools),
                evidence_lines=evidence_lines,
                recent_messages=recent_messages,
                school_profile=school_profile,
                reason=response.reason,
                focus_summary=build_focus_summary(focus),
                actor_summary=actor_summary,
            )
        )
        if deterministic_plan is not None:
            if focus.unknown_student_name or focus.unknown_subject_name or focus.is_repair_followup or focus.needs_disambiguation:
                repair_plan = deterministic_plan
            elif repair_plan is None:
                repair_plan = deterministic_plan
            else:
                current_action = str(repair_plan.get('action') or 'keep')
                current_confidence = float(repair_plan.get('confidence') or 0.0)
                if current_action in {'keep', 'unavailable'} or current_confidence < 0.8:
                    repair_plan = deterministic_plan
        if repair_plan is None and response.mode == OrchestrationMode.clarify:
            retry_query = _fallback_retry_query(
                request=request,
                focus=focus,
                recent_user_messages=recent_user_messages,
            )
            repair_plan = {
                'action': 'retry_retrieval' if _retry_visibility_for_response(response) else 'clarify',
                'message': 'Você pode me dizer exatamente qual aluno, disciplina ou período devo considerar?',
                'retry_query': retry_query,
                'confidence': 0.45,
                'reason': 'fallback_context_repair',
            }
        elif repair_plan is None:
            repair_plan = {'action': 'keep', 'message': '', 'retry_query': '', 'confidence': 0.0, 'reason': 'planner_unavailable'}

        action = str(repair_plan.get('action') or 'keep')
        planner_message = _normalize_text(repair_plan.get('message'))
        retry_query = _normalize_text(repair_plan.get('retry_query')) or _fallback_retry_query(
            request=request,
            focus=focus,
            recent_user_messages=recent_user_messages,
        )
        confidence = float(repair_plan.get('confidence') or 0.0)
        planner_reason = _normalize_text(repair_plan.get('reason')) or action
        should_retry_before_unavailable = (
            action in {'retry_retrieval', 'unavailable'}
            and _retry_visibility_for_response(response) is not None
            and (action != 'unavailable' or confidence < 0.9)
        )
        if should_retry_before_unavailable:
            retry_response = await _attempt_second_retrieval(
                settings=settings,
                request=request,
                response=response,
                retry_query=retry_query,
                focus=focus,
                recent_messages=recent_messages,
                school_profile=school_profile,
                provider_settings=provider_settings,
                actor_summary=actor_summary,
            )
            if retry_response is not None:
                return retry_response
            clarify_after_retry = _clarify_after_retry_message(
                request=request,
                focus=focus,
                actor=actor,
                conversation_context=conversation_context,
            )
            if clarify_after_retry:
                llm_stages = [str(item).strip() for item in (response.llm_stages or []) if str(item).strip()]
                if 'context_repair_planner' not in llm_stages:
                    llm_stages.append('context_repair_planner')
                return response.model_copy(
                    update={
                        'message_text': clarify_after_retry,
                        'mode': OrchestrationMode.clarify,
                        'used_llm': True,
                        'llm_stages': llm_stages,
                        'answer_experience_eligible': True,
                        'answer_experience_applied': True,
                        'answer_experience_reason': f'{base_reason}:context_repair_clarify_after_retry',
                        'answer_experience_provider': provider_settings.llm_provider,
                        'answer_experience_model': provider_settings.google_model if provider_settings.llm_provider in {'google', 'gemini'} else provider_settings.openai_model,
                        'context_repair_applied': True,
                        'context_repair_action': 'clarify',
                        'context_repair_reason': 'retry_failed_clarify',
                    }
                )
        if action == 'clarify' and planner_message:
            llm_stages = [str(item).strip() for item in (response.llm_stages or []) if str(item).strip()]
            if 'context_repair_planner' not in llm_stages:
                llm_stages.append('context_repair_planner')
            return response.model_copy(
                update={
                    'message_text': planner_message,
                    'mode': OrchestrationMode.clarify,
                    'used_llm': True,
                    'llm_stages': llm_stages,
                    'answer_experience_eligible': True,
                    'answer_experience_applied': True,
                    'answer_experience_reason': f'{base_reason}:context_repair_clarify',
                    'answer_experience_provider': provider_settings.llm_provider,
                    'answer_experience_model': provider_settings.google_model if provider_settings.llm_provider in {'google', 'gemini'} else provider_settings.openai_model,
                    'context_repair_applied': True,
                    'context_repair_action': 'clarify',
                    'context_repair_reason': planner_reason,
                }
            )
        if action == 'unavailable' and planner_message and confidence >= 0.9:
            llm_stages = [str(item).strip() for item in (response.llm_stages or []) if str(item).strip()]
            if 'context_repair_planner' not in llm_stages:
                llm_stages.append('context_repair_planner')
            return response.model_copy(
                update={
                    'message_text': planner_message,
                    'used_llm': True,
                    'llm_stages': llm_stages,
                    'answer_experience_eligible': True,
                    'answer_experience_applied': True,
                    'answer_experience_reason': f'{base_reason}:context_repair_unavailable',
                    'answer_experience_provider': provider_settings.llm_provider,
                    'answer_experience_model': provider_settings.google_model if provider_settings.llm_provider in {'google', 'gemini'} else provider_settings.openai_model,
                    'context_repair_applied': True,
                    'context_repair_action': 'unavailable',
                    'context_repair_reason': planner_reason,
                }
            )
    if not reason:
        return response
    candidate_text = await compose_grounded_answer_experience_with_provider(
        settings=provider_settings,
        request_message=request.message,
        draft_text=effective_draft_text,
        mode=response.mode.value,
        domain=response.classification.domain.value,
        access_tier=response.classification.access_tier.value,
        selected_tools=list(response.selected_tools),
        evidence_lines=evidence_lines,
        recent_messages=recent_messages,
        school_profile=school_profile,
        reason=response.reason,
        focus_summary=build_focus_summary(focus),
    )
    validated_text = _validated_answer_experience_text(
        request_message=request.message,
        original_text=effective_draft_text,
        candidate_text=candidate_text or '',
        focus=focus,
    )
    if not validated_text:
        supplemental_fallback = _validated_answer_experience_text(
            request_message=request.message,
            original_text=response.message_text,
            candidate_text=supplemental_focused_draft,
            focus=focus,
        )
        if supplemental_fallback:
            llm_stages = [str(item).strip() for item in (response.llm_stages or []) if str(item).strip()]
            used_llm = bool(candidate_text) or bool(response.used_llm)
            if used_llm and 'grounded_answer_experience' not in llm_stages:
                llm_stages.append('grounded_answer_experience')
            return response.model_copy(
            update={
                'message_text': supplemental_fallback,
                'used_llm': used_llm,
                    'llm_stages': llm_stages,
                    'answer_experience_eligible': True,
                'answer_experience_applied': _answer_experience_changed(response.message_text, supplemental_fallback),
                'answer_experience_reason': f'{base_reason}:supplemental_focus_fallback',
                'answer_experience_provider': provider_settings.llm_provider,
                'answer_experience_model': provider_settings.google_model if provider_settings.llm_provider in {'google', 'gemini'} else provider_settings.openai_model,
                'context_repair_applied': bool(getattr(response, 'context_repair_applied', False)),
                'context_repair_action': getattr(response, 'context_repair_action', None),
                'context_repair_reason': getattr(response, 'context_repair_reason', None),
                'retrieval_retry_applied': bool(getattr(response, 'retrieval_retry_applied', False)),
                'retrieval_retry_reason': getattr(response, 'retrieval_retry_reason', None),
            }
        )
        return response.model_copy(
            update={
                'answer_experience_eligible': True,
                'answer_experience_applied': False,
                'answer_experience_reason': f'{base_reason}:fallback_to_original',
                'answer_experience_provider': provider_settings.llm_provider,
                'answer_experience_model': provider_settings.google_model if provider_settings.llm_provider in {'google', 'gemini'} else provider_settings.openai_model,
            }
        )

    llm_stages = [str(item).strip() for item in (response.llm_stages or []) if str(item).strip()]
    if 'grounded_answer_experience' not in llm_stages:
        llm_stages.append('grounded_answer_experience')
    return response.model_copy(
        update={
            'message_text': validated_text,
            'used_llm': True,
            'llm_stages': llm_stages,
            'answer_experience_eligible': True,
            'answer_experience_applied': _answer_experience_changed(response.message_text, validated_text),
            'answer_experience_reason': base_reason,
            'answer_experience_provider': provider_settings.llm_provider,
            'answer_experience_model': provider_settings.google_model if provider_settings.llm_provider in {'google', 'gemini'} else provider_settings.openai_model,
            'context_repair_applied': bool(getattr(response, 'context_repair_applied', False)),
            'context_repair_action': getattr(response, 'context_repair_action', None),
            'context_repair_reason': getattr(response, 'context_repair_reason', None),
            'retrieval_retry_applied': bool(getattr(response, 'retrieval_retry_applied', False)),
            'retrieval_retry_reason': getattr(response, 'retrieval_retry_reason', None),
        }
    )
