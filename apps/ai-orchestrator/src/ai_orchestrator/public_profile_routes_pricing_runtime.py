from __future__ import annotations

import re
from typing import Any

from .intent_analysis_runtime import (
    _detect_public_pricing_price_kind,
    _message_matches_term,
    _normalize_text,
    _should_reuse_public_pricing_slots,
)
from .public_operations_runtime import _format_brl, _parse_public_money
from .public_profile_support_runtime import _public_segment_matches


def _compose_public_pricing_projection_answer_impl(context: Any) -> str | None:
    from .runtime_core import resolve_entity_hints

    hints = resolve_entity_hints(context.source_message)
    quantity = hints.quantity_hint
    if quantity is None:
        numeric_match = re.search(r'\b(\d{1,4})\b', context.normalized)
        if numeric_match:
            quantity = int(numeric_match.group(1))
    reuse_pricing_slots = _should_reuse_public_pricing_slots(context.source_message)
    if quantity is None and reuse_pricing_slots:
        slot_quantity = str(context.slot_memory.public_pricing_quantity or '').strip()
        if slot_quantity.isdigit():
            quantity = int(slot_quantity)
    normalized = context.normalized
    explicit_projection_request = quantity is not None and any(
        _message_matches_term(normalized, term)
        for term in {
            'mensalidade',
            'mensalidades',
            'matricula',
            'matrícula',
            'pagar',
            'pagaria',
            'filhos',
            'alunos',
        }
    )
    if (
        (not hints.is_hypothetical and not reuse_pricing_slots and not explicit_projection_request)
        or quantity is None
        or quantity <= 0
    ):
        return None

    amount_key = (
        _detect_public_pricing_price_kind(context.source_message)
        or context.slot_memory.public_pricing_price_kind
    )
    wants_enrollment_fee = any(
        _message_matches_term(normalized, term)
        for term in {'matricula', 'matrícula', 'taxa de matricula', 'taxa de matrícula'}
    )
    wants_monthly_amount = any(
        _message_matches_term(normalized, term)
        for term in {
            'mensalidade',
            'mensalidades',
            'por mes',
            'por mês',
            'total por mes',
            'total por mês',
            'mensal',
            'todo mes',
            'todo mês',
            'manter',
        }
    )
    wants_both_amounts = wants_enrollment_fee and wants_monthly_amount
    if (
        not wants_both_amounts
        and quantity is not None
        and any(
            _message_matches_term(normalized, term)
            for term in {
                'matricula e o total por mes',
                'matrícula e o total por mês',
                'matricular e manter',
                'matricula e mensalidade',
                'matrícula e mensalidade',
            }
        )
    ):
        wants_both_amounts = True
    if amount_key not in {'monthly_amount', 'enrollment_fee'}:
        amount_key = (
            'monthly_amount'
            if wants_monthly_amount and not wants_enrollment_fee
            else 'enrollment_fee'
        )
    amount_label = (
        'mensalidade publica de referencia'
        if amount_key == 'monthly_amount'
        else 'taxa publica de matricula'
    )

    requested_segment = context.segment or context.slot_memory.public_pricing_segment
    requested_grade_year = context.slot_memory.public_pricing_grade_year
    if not requested_segment and requested_grade_year in {'1o ano', '2o ano', '3o ano'}:
        requested_segment = 'Ensino Medio'
    if not requested_segment and requested_grade_year in {'6o ano', '7o ano', '8o ano', '9o ano'}:
        requested_segment = 'Ensino Fundamental II'
    relevant_rows = [
        row
        for row in context.tuition_reference
        if isinstance(row, dict)
        and _public_segment_matches(str(row.get('segment')), requested_segment)
    ]
    if not relevant_rows:
        relevant_rows = [row for row in context.tuition_reference if isinstance(row, dict)]

    projected_rows: list[dict[str, Any]] = []
    sibling_discount_note: str | None = None
    for row in relevant_rows:
        monthly_amount = _parse_public_money(row.get('monthly_amount'))
        enrollment_fee = _parse_public_money(row.get('enrollment_fee'))
        requested_amount = monthly_amount if amount_key == 'monthly_amount' else enrollment_fee
        if wants_both_amounts:
            if (
                monthly_amount is None
                or monthly_amount <= 0
                or enrollment_fee is None
                or enrollment_fee <= 0
            ):
                continue
        elif requested_amount is None or requested_amount <= 0:
            continue
        notes = str(row.get('notes', '')).strip()
        if not sibling_discount_note and any(
            _message_matches_term(_normalize_text(notes), term)
            for term in {
                'irmaos',
                'irmãos',
                'pagamento pontual',
                'politica comercial',
                'política comercial',
                'desconto',
            }
        ):
            sibling_discount_note = notes
        projected_rows.append(
            {
                'segment': str(row.get('segment', 'Segmento')).strip(),
                'shift_label': str(row.get('shift_label', 'turno')).strip(),
                'amount': requested_amount,
                'monthly_amount': monthly_amount,
                'enrollment_fee': enrollment_fee,
                'notes': notes,
            }
        )

    if not projected_rows:
        return None

    if wants_both_amounts:
        unique_pairs = {(row['monthly_amount'], row['enrollment_fee']) for row in projected_rows}
        if len(unique_pairs) == 1:
            per_student_monthly, per_student_enrollment = next(iter(unique_pairs))
            assert per_student_monthly is not None
            assert per_student_enrollment is not None
            total_monthly = per_student_monthly * quantity
            total_enrollment = per_student_enrollment * quantity
            shared_scope = 'nos segmentos publicados que usam essa mesma referencia'
            if len(projected_rows) == 1:
                shared_scope = f'em {projected_rows[0]["segment"]}'
                if requested_grade_year:
                    shared_scope = f'no {requested_grade_year} de {projected_rows[0]["segment"]}'
            lines = [
                (
                    f'Para {quantity} aluno(s), se eu usar os valores publicos hoje publicados {shared_scope}, '
                    f'a matricula fica {quantity} x {_format_brl(per_student_enrollment)} = {_format_brl(total_enrollment)} '
                    f'e a mensalidade por mes fica {quantity} x {_format_brl(per_student_monthly)} = {_format_brl(total_monthly)}.'
                )
            ]
        else:
            lines = [
                'Hoje a escola publica mais de uma referencia combinada de matricula e mensalidade. Para essa simulacao, os totais por segmento ficam assim:'
            ]
            for row in projected_rows[:4]:
                monthly_amount = row['monthly_amount']
                enrollment_fee = row['enrollment_fee']
                if monthly_amount is None or enrollment_fee is None:
                    continue
                lines.append(
                    f'- {row["segment"]} ({row["shift_label"]}): matricula {quantity} x {_format_brl(enrollment_fee)} = {_format_brl(enrollment_fee * quantity)}; '
                    f'mensalidade por mes {quantity} x {_format_brl(monthly_amount)} = {_format_brl(monthly_amount * quantity)}.'
                )
    else:
        unique_amounts = {row['amount'] for row in projected_rows}
        if len(unique_amounts) == 1:
            per_student = projected_rows[0]['amount']
            total_amount = per_student * quantity
            shared_scope = 'nos segmentos publicados que usam essa mesma referencia'
            if len(projected_rows) == 1:
                shared_scope = f'em {projected_rows[0]["segment"]}'
                if requested_grade_year:
                    shared_scope = f'no {requested_grade_year} de {projected_rows[0]["segment"]}'
            lines = [
                f'Para {quantity} aluno(s), se eu usar a {amount_label} hoje publicada {shared_scope}, a simulacao fica {quantity} x {_format_brl(per_student)} = {_format_brl(total_amount)}.'
            ]
        else:
            lines = [
                f'Hoje a escola publica mais de uma referencia de {amount_label}. Para {quantity} alunos, a simulacao por segmento fica assim:'
            ]
            for row in projected_rows[:4]:
                total_amount = row['amount'] * quantity
                lines.append(
                    f'- {row["segment"]} ({row["shift_label"]}): {quantity} x {_format_brl(row["amount"])} = {_format_brl(total_amount)}.'
                )

    lines.append(
        'Essa conta usa apenas os valores publicos de referencia e nao inclui material, uniforme ou condicao comercial nao detalhada na base.'
    )
    if sibling_discount_note:
        lines.append(f'A base publica tambem menciona: {sibling_discount_note}')
    return '\n'.join(lines)
