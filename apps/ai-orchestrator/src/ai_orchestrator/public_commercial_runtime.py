from __future__ import annotations

from typing import Any

from .conversation_focus_runtime import _normalize_text
from .intent_analysis_runtime import _message_matches_term


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


def _public_service_catalog(profile: dict[str, Any]) -> list[dict[str, Any]]:
    from .public_profile_runtime import _public_service_catalog as _impl

    return _impl(profile)


def _humanize_service_eta(eta: str) -> str:
    from .public_profile_runtime import _humanize_service_eta as _impl

    return _impl(eta)


def _public_segment_matches(row_segment: str | None, requested_segment: str | None) -> bool:
    from .public_profile_runtime import _public_segment_matches as _impl

    return _impl(row_segment, requested_segment)


def _public_feature_inventory(profile: dict[str, Any]) -> list[dict[str, Any]]:
    from .public_profile_runtime import _public_feature_inventory as _impl

    return _impl(profile)


def _school_subject_reference(reference: str) -> str:
    from .public_profile_runtime import _school_subject_reference as _impl

    return _impl(reference)


def _is_public_scholarship_query(message: str) -> bool:
    from .public_profile_runtime import PUBLIC_SCHOLARSHIP_TERMS

    normalized = _normalize_text(message)
    return any(_message_matches_term(normalized, term) for term in PUBLIC_SCHOLARSHIP_TERMS)


def _is_public_enrichment_query(message: str) -> bool:
    from .public_profile_runtime import PUBLIC_ENRICHMENT_TERMS

    normalized = _normalize_text(message)
    return any(_message_matches_term(normalized, term) for term in PUBLIC_ENRICHMENT_TERMS)


def _compose_public_scholarship_answer(context: Any) -> str:
    requested_unpublished_segment = _requested_unpublished_public_segment(context)
    if requested_unpublished_segment:
        return _compose_public_segment_scope_gap(
            context,
            requested_segment=requested_unpublished_segment,
            topic='bolsas e descontos',
        )
    service = next(
        (
            item
            for item in _public_service_catalog(context.profile)
            if str(item.get('service_key', '')).strip() == 'atendimento_admissoes'
        ),
        None,
    )
    relevant_rows = [
        row
        for row in context.tuition_reference
        if isinstance(row, dict)
        and (context.segment is None or str(row.get('segment')) == context.segment)
    ]
    if not relevant_rows:
        relevant_rows = [row for row in context.tuition_reference if isinstance(row, dict)]

    policy_notes: list[str] = []
    for row in relevant_rows:
        notes = str(row.get('notes', '')).strip()
        normalized_notes = _normalize_text(notes)
        if notes and any(
            _message_matches_term(normalized_notes, term)
            for term in {
                'irmaos',
                'irmãos',
                'pagamento pontual',
                'politica comercial',
                'política comercial',
            }
        ):
            policy_notes.append(notes)
    lines = [
        f'Hoje, pelo que {context.school_reference} publica, bolsas e descontos entram no atendimento comercial de matricula.',
    ]
    if policy_notes:
        lines.append(f'A referencia comercial atual tambem menciona {policy_notes[0].lower()}')
    else:
        lines.append(
            'A base publica confirma que esse tema passa pelo canal comercial, junto com simulacao financeira e processo de ingresso.'
        )
    if isinstance(service, dict):
        request_channel = str(service.get('request_channel', 'canal institucional')).strip()
        eta = _humanize_service_eta(str(service.get('typical_eta', 'retorno em ate 1 dia util')))
        notes = str(service.get('notes', '')).strip()
        lines.append(
            f'O caminho mais direto hoje e {service.get("title", "matricula e atendimento comercial")} por {request_channel}, com {eta}.'
        )
        if notes:
            lines.append(notes)
    return ' '.join(line.strip() for line in lines if line and line.strip())


def _compose_public_enrichment_answer(context: Any) -> str:
    requested_unpublished_segment = _requested_unpublished_public_segment(context)
    if requested_unpublished_segment:
        return _compose_public_segment_scope_gap(
            context,
            requested_segment=requested_unpublished_segment,
            topic='atividades complementares',
        )
    relevant_rows = [
        row
        for row in context.shift_offers
        if isinstance(row, dict)
        and _public_segment_matches(str(row.get('segment')), context.segment)
    ]
    if not relevant_rows:
        relevant_rows = [row for row in context.shift_offers if isinstance(row, dict)]

    available_features = _public_feature_inventory(context.profile)
    enrichment_labels: list[str] = []
    for key in ('biblioteca', 'danca', 'teatro', 'futebol', 'volei', 'maker', 'laboratorio'):
        item = next(
            (
                feature
                for feature in available_features
                if str(feature.get('feature_key', '')).strip() == key
                and bool(feature.get('available'))
            ),
            None,
        )
        if not isinstance(item, dict):
            continue
        label = str(item.get('label', '')).strip()
        if label and label not in enrichment_labels:
            enrichment_labels.append(label)

    if len(relevant_rows) == 1:
        row = relevant_rows[0]
        lines = [
            f'Hoje {_school_subject_reference(context.school_reference)} divulga atividades complementares no {str(row.get("segment", "segmento")).lower()}.',
            str(row.get('notes', '')).strip(),
        ]
    else:
        lines = [
            f'Hoje {_school_subject_reference(context.school_reference)} divulga atividades complementares no contraturno de forma assim:'
        ]
        for row in relevant_rows[:3]:
            segment = str(row.get('segment', 'Segmento')).strip()
            notes = str(row.get('notes', '')).strip()
            if notes:
                lines.append(f'- {segment}: {notes}')
    if enrichment_labels:
        labels_preview = ', '.join(enrichment_labels[:6])
        lines.append(f'Entre as ofertas que aparecem com mais clareza hoje estao {labels_preview}.')
    return ' '.join(line.strip() for line in lines if line and line.strip())
