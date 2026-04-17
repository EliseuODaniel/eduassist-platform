from __future__ import annotations

import re
from decimal import Decimal, InvalidOperation
from typing import Any

from .conversation_focus_runtime import _normalize_text


def _intent_analysis_impl(name: str):
    from . import intent_analysis_runtime as _intent_analysis_runtime

    return getattr(_intent_analysis_runtime, name)


def _message_matches_term(message: str, term: str) -> bool:
    return _intent_analysis_impl('_message_matches_term')(message, term)


def _requested_unpublished_public_segment(context: Any) -> str | None:
    from .public_profile_runtime import _requested_unpublished_public_segment as _impl

    return _impl(context)


def _compose_public_segment_scope_gap(
    context: Any,
    *,
    requested_segment: str,
    topic: str,
) -> str:
    from .public_profile_runtime import _compose_public_segment_scope_gap as _impl

    return _impl(context, requested_segment=requested_segment, topic=topic)


def _build_public_profile_context(
    profile: dict[str, Any],
    message: str,
    *,
    conversation_context: dict[str, Any] | None = None,
    semantic_plan: Any | None = None,
) -> Any:
    from .public_profile_runtime import _build_public_profile_context as _impl

    return _impl(
        profile,
        message,
        conversation_context=conversation_context,
        semantic_plan=semantic_plan,
    )


def _public_segment_matches(row_segment: str | None, requested_segment: str | None) -> bool:
    from .public_profile_runtime import _public_segment_matches as _impl

    return _impl(row_segment, requested_segment)


def _extract_grade_reference(message: str) -> str | None:
    from .public_profile_runtime import _extract_grade_reference as _impl

    return _impl(message)


def _humanize_service_eta(eta: str) -> str:
    from .public_profile_runtime import _humanize_service_eta as _impl

    return _impl(eta)


def _is_public_scholarship_query(message: str) -> bool:
    from .public_commercial_runtime import _is_public_scholarship_query as _impl

    return _impl(message)


def _compose_public_scholarship_answer(context: Any) -> str:
    from .public_commercial_runtime import _compose_public_scholarship_answer as _impl

    return _impl(context)


def _compose_public_pricing_projection_answer_impl(context: Any) -> str | None:
    from .public_profile_routes_runtime import _compose_public_pricing_projection_answer_impl as _impl

    return _impl(context)


def _parse_public_money(value: Any) -> Decimal | None:
    if value is None:
        return None
    if isinstance(value, Decimal):
        return value
    if isinstance(value, (int, float)):
        return Decimal(str(value))
    text = str(value).strip()
    if not text:
        return None
    cleaned = re.sub(r'[^0-9,.\-]', '', text)
    if not cleaned:
        return None
    if ',' in cleaned and '.' in cleaned:
        if cleaned.rfind(',') > cleaned.rfind('.'):
            cleaned = cleaned.replace('.', '').replace(',', '.')
        else:
            cleaned = cleaned.replace(',', '')
    elif ',' in cleaned:
        cleaned = cleaned.replace('.', '').replace(',', '.')
    try:
        return Decimal(cleaned)
    except InvalidOperation:
        return None


def _format_brl(value: Any) -> str:
    amount = _parse_public_money(value)
    if amount is None:
        return str(value)
    quantized = amount.quantize(Decimal('0.01'))
    formatted = f'{quantized:,.2f}'
    formatted = formatted.replace(',', 'X').replace('.', ',').replace('X', '.')
    return f'R$ {formatted}'


def _is_public_pricing_projection_context(candidate: Any) -> bool:
    try:
        from .public_profile_runtime import PublicProfileContext
    except Exception:
        PublicProfileContext = None
    return (PublicProfileContext is not None and isinstance(candidate, PublicProfileContext)) or (
        hasattr(candidate, 'source_message')
        and hasattr(candidate, 'normalized')
        and hasattr(candidate, 'slot_memory')
        and hasattr(candidate, 'tuition_reference')
    )


def _compose_public_pricing_projection_answer(
    profile_or_context: dict[str, Any] | Any,
    message: str | None = None,
    *,
    conversation_context: dict[str, Any] | None = None,
    semantic_plan: Any | None = None,
) -> str | None:
    if message is None and _is_public_pricing_projection_context(profile_or_context):
        return _compose_public_pricing_projection_answer_impl(profile_or_context)
    if message is None or not isinstance(profile_or_context, dict):
        raise TypeError('profile + message ou PublicProfileContext sao obrigatorios')
    context = _build_public_profile_context(
        profile_or_context,
        message,
        conversation_context=conversation_context,
        semantic_plan=semantic_plan,
    )
    return _compose_public_pricing_projection_answer_impl(context)


def _handle_public_pricing(context: Any) -> str:
    pricing_projection_answer = _compose_public_pricing_projection_answer(context)
    if pricing_projection_answer:
        return pricing_projection_answer
    if _is_public_scholarship_query(context.source_message):
        return _compose_public_scholarship_answer(context)
    requested_unpublished_segment = _requested_unpublished_public_segment(context)
    if requested_unpublished_segment:
        return _compose_public_segment_scope_gap(
            context,
            requested_segment=requested_unpublished_segment,
            topic='mensalidades publicas',
        )
    requested_segment = context.segment or context.slot_memory.public_pricing_segment
    relevant_rows = [
        row
        for row in context.tuition_reference
        if isinstance(row, dict)
        and _public_segment_matches(str(row.get('segment')), requested_segment)
    ]
    if not relevant_rows:
        relevant_rows = [row for row in context.tuition_reference if isinstance(row, dict)]
    if len(relevant_rows) == 1:
        row = relevant_rows[0]
        return (
            f'Para {row.get("segment", "esse segmento")} no turno {row.get("shift_label", "regular")}, '
            f'a mensalidade publica de referencia em 2026 e {_format_brl(row.get("monthly_amount", "0.00"))} '
            f'e a taxa de matricula e {_format_brl(row.get("enrollment_fee", "0.00"))}. '
            f'{str(row.get("notes", "")).strip()} '
            'Se quiser, eu tambem posso resumir bolsas, descontos comerciais e canais de matricula.'
        ).strip()
    lines = ['Valores publicos de referencia para 2026:']
    for row in relevant_rows:
        lines.append(
            '- {segment} ({shift_label}): mensalidade {monthly_amount} e taxa de matricula {enrollment_fee}. {notes}'.format(
                segment=row.get('segment', 'Segmento'),
                shift_label=row.get('shift_label', 'turno'),
                monthly_amount=_format_brl(row.get('monthly_amount', '0.00')),
                enrollment_fee=_format_brl(row.get('enrollment_fee', '0.00')),
                notes=row.get('notes', '').strip(),
            ).rstrip()
        )
    lines.append(
        'Se quiser, eu tambem posso resumir bolsas, descontos comerciais e canais de matricula.'
    )
    return '\n'.join(lines)


def _handle_public_schedule(context: Any) -> str:
    try:
        from .public_profile_runtime import PUBLIC_CAPACITY_PARKING_TERMS
    except Exception:
        PUBLIC_CAPACITY_PARKING_TERMS = ()

    requested_unpublished_segment = _requested_unpublished_public_segment(context)
    if requested_unpublished_segment:
        return _compose_public_segment_scope_gap(
            context,
            requested_segment=requested_unpublished_segment,
            topic='horarios',
        )
    grade_reference = _extract_grade_reference(context.source_message)
    normalized_message = _normalize_text(context.source_message)
    requested_shift: str | None = None
    if any(term in normalized_message for term in {'manha', 'manhã', 'matutino', 'matutina'}):
        requested_shift = 'manha'
    elif any(term in normalized_message for term in {'vespertino', 'vespertina', 'tarde'}):
        requested_shift = 'vespertino'
    elif any(term in normalized_message for term in {'noturno', 'noturna', 'noite'}):
        requested_shift = 'noturno'
    elif 'integral' in normalized_message:
        requested_shift = 'integral'
    asks_end = any(
        term in normalized_message
        for term in {'fecha', 'termina', 'acabam', 'acaba', 'ultima aula', 'última aula'}
    )
    asks_start = any(
        term in normalized_message
        for term in {'que horas', 'comeca', 'começa', 'inicio', 'início'}
    )
    if 'madrugada' in normalized_message:
        lines = [
            f'Hoje {context.school_reference} nao publica turnos regulares de madrugada.',
            'Os turnos documentados atualmente sao:',
        ]
        for row in [row for row in context.shift_offers if isinstance(row, dict)]:
            lines.append(
                '- {segment} ({shift_label}): {starts_at} as {ends_at}. {notes}'.format(
                    segment=row.get('segment', 'Segmento'),
                    shift_label=row.get('shift_label', 'turno'),
                    starts_at=row.get('starts_at', '--:--'),
                    ends_at=row.get('ends_at', '--:--'),
                    notes=row.get('notes', '').strip(),
                ).rstrip()
            )
        return '\n'.join(lines)
    relevant_rows = [
        row
        for row in context.shift_offers
        if isinstance(row, dict)
        and _public_segment_matches(str(row.get('segment')), context.segment)
        and (
            requested_shift is None
            or (
                requested_shift == 'manha'
                and any(
                    term in _normalize_text(str(row.get('shift_label')))
                    for term in {'manha', 'manhã', 'matut'}
                )
            )
            or (
                requested_shift != 'manha'
                and requested_shift in _normalize_text(str(row.get('shift_label')))
            )
        )
    ]
    if not relevant_rows:
        relevant_rows = [
            row
            for row in context.shift_offers
            if isinstance(row, dict)
            and (
                requested_shift is None
                or (
                    requested_shift == 'manha'
                    and any(
                        term in _normalize_text(str(row.get('shift_label')))
                        for term in {'manha', 'manhã', 'matut'}
                    )
                )
                or (
                    requested_shift != 'manha'
                    and requested_shift in _normalize_text(str(row.get('shift_label')))
                )
            )
        ]
    if not relevant_rows:
        relevant_rows = [row for row in context.shift_offers if isinstance(row, dict)]
    if requested_shift == 'manha':
        morning_rows = [
            row
            for row in relevant_rows
            if any(
                term in _normalize_text(str(row.get('shift_label')))
                for term in {'manha', 'manhã', 'matut'}
            )
        ]
        if morning_rows:
            relevant_rows = morning_rows
    if len(relevant_rows) == 1:
        row = relevant_rows[0]
        if grade_reference:
            return (
                f'O {grade_reference} fica em {row.get("segment", "esse segmento")}. '
                f'As atividades do turno {row.get("shift_label", "regular").lower()} vao de {row.get("starts_at", "--:--")} a {row.get("ends_at", "--:--")}. '
                f'{str(row.get("notes", "")).strip()}'
            ).strip()
        return (
            f'Para {row.get("segment", "esse segmento")}, as atividades no turno {row.get("shift_label", "regular").lower()} '
            f'vao de {row.get("starts_at", "--:--")} a {row.get("ends_at", "--:--")}. '
            f'{str(row.get("notes", "")).strip()}'
        ).strip()
    if grade_reference and context.segment:
        lines = [
            f'Hoje os canais publicos do {context.school_name} nao detalham o horario especifico do {grade_reference}.',
            f'O recorte publicado para esse pedido fica em {context.segment}:',
        ]
        for row in relevant_rows:
            lines.append(
                '- {segment} ({shift_label}): {starts_at} as {ends_at}. {notes}'.format(
                    segment=row.get('segment', 'Segmento'),
                    shift_label=row.get('shift_label', 'turno'),
                    starts_at=row.get('starts_at', '--:--'),
                    ends_at=row.get('ends_at', '--:--'),
                    notes=row.get('notes', '').strip(),
                ).rstrip()
            )
        return '\n'.join(lines)
    if requested_shift == 'manha' and asks_start:
        lines = ['Horarios de inicio documentados para o turno da manha:']
    elif requested_shift == 'manha' and asks_end:
        lines = ['Horarios de encerramento documentados para o turno da manha:']
    elif asks_end:
        lines = ['Horarios de encerramento documentados:']
    elif asks_start:
        lines = ['Horarios de inicio documentados:']
    else:
        lines = ['Turnos e horarios documentados:']
    for row in relevant_rows:
        lines.append(
            '- {segment} ({shift_label}): {starts_at} as {ends_at}. {notes}'.format(
                segment=row.get('segment', 'Segmento'),
                shift_label=row.get('shift_label', 'turno'),
                starts_at=row.get('starts_at', '--:--'),
                ends_at=row.get('ends_at', '--:--'),
                notes=row.get('notes', '').strip(),
            ).rstrip()
        )
    return '\n'.join(lines)


def _handle_public_capacity(context: Any) -> str:
    from .public_profile_runtime import PUBLIC_CAPACITY_PARKING_TERMS

    normalized = _normalize_text(context.source_message)
    if any(_message_matches_term(normalized, term) for term in PUBLIC_CAPACITY_PARKING_TERMS):
        return (
            f'Hoje a base publica de {context.school_reference} nao informa a quantidade de vagas de estacionamento. '
            'Se a sua necessidade for visita, evento ou rotina de acesso, o caminho mais seguro e confirmar isso com a secretaria ou recepcao antes.'
        )
    if any(
        _message_matches_term(normalized, term)
        for term in {
            'aluno',
            'alunos',
            'escola',
            'matricula',
            'matrícula',
            'turma',
            'turmas',
            'segmento',
            'segmentos',
        }
    ):
        return (
            f'Hoje a base publica de {context.school_reference} nao publica um numero fechado de vagas para alunos ou de capacidade total da escola. '
            'A disponibilidade costuma ser confirmada por segmento e turma com admissions ou secretaria, conforme o momento do ciclo de matricula.'
        )
    return (
        'Quando voce fala em vagas, isso pode significar vagas para alunos, vagas de estacionamento ou vagas para trabalhar na escola. '
        'Se quiser, eu separo isso por tipo agora.'
    )


def _handle_public_segments(context: Any) -> str:
    segments = context.profile.get('segments')
    if not isinstance(segments, list) or not segments:
        return f'Hoje o perfil publico de {context.school_reference} nao traz os segmentos atendidos.'
    lines = [f'Hoje {context.school_reference} atende estes segmentos:']
    lines.extend(f'- {item}' for item in segments if isinstance(item, str))
    return '\n'.join(lines)
