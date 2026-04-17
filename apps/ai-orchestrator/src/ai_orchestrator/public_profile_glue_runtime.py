from __future__ import annotations

import re

from .conversation_focus_runtime import _normalize_text, _recent_message_lines
from .public_feature_runtime import (
    _feature_inventory_map,
    _is_public_feature_query,
    _recent_public_feature_key,
    _requested_public_features,
)
from .runtime_core import _llm_forced_mode_enabled
from .runtime_core_constants import PUBLIC_SCHEDULE_TERMS
from .public_act_rules_runtime import _matches_public_contact_rule


def _intent_analysis_impl(name: str):
    from . import intent_analysis_runtime as _intent_analysis_runtime

    return getattr(_intent_analysis_runtime, name)


def _is_follow_up_query(message: str) -> bool:
    return _intent_analysis_impl('_is_follow_up_query')(message)


def _message_matches_term(message: str, term: str) -> bool:
    return _intent_analysis_impl('_message_matches_term')(message, term)


def _compose_public_feature_schedule_follow_up(
    *,
    profile: dict[str, object],
    original_message: str,
    analysis_message: str,
    conversation_context: dict[str, object] | None,
) -> str | None:
    if not any(
        _message_matches_term(_normalize_text(original_message), term)
        for term in PUBLIC_SCHEDULE_TERMS | {'funciona quando', 'isso funciona quando'}
    ):
        return None
    requested_features = _requested_public_features(original_message)
    if (
        not requested_features
        and _is_follow_up_query(original_message)
        and not _is_public_feature_query(original_message)
    ):
        requested_features = _requested_public_features(analysis_message)
    if not requested_features and _is_follow_up_query(original_message):
        recent_feature = _recent_public_feature_key(conversation_context)
        if recent_feature:
            requested_features = [recent_feature]
    if len(requested_features) != 1:
        return None
    item = _feature_inventory_map(profile).get(requested_features[0])
    if item is None or not bool(item.get('available')):
        return None
    label = str(item.get('label', requested_features[0])).strip()
    notes = str(item.get('notes', '')).strip()
    if not notes:
        return None
    normalized_notes = _normalize_text(notes)
    if not any(
        marker in normalized_notes
        for marker in (
            'segunda',
            'terca',
            'terça',
            'quarta',
            'quinta',
            'sexta',
            'sabado',
            'sábado',
            'domingo',
            'contraturno',
            '7h',
            '8h',
            '9h',
            '10h',
            '11h',
            '12h',
            '13h',
            '14h',
            '15h',
            '16h',
            '17h',
            '18h',
        )
    ):
        return None
    return f'O horario de {label} hoje funciona assim: {notes}'


def _localize_pt_br_surface_labels(text: str) -> str:
    localized = str(text or '')
    localized = re.sub(
        r'(?i)\badmissions\b',
        'matricula e atendimento comercial',
        localized,
    )
    localized = localized.replace(
        'secretaria/matricula e atendimento comercial',
        'secretaria ou matricula e atendimento comercial',
    )
    localized = localized.replace(
        'secretaria / matricula e atendimento comercial',
        'secretaria ou matricula e atendimento comercial',
    )
    return localized


def _recent_user_message_mentions(
    conversation_context: dict[str, object] | None,
    terms: set[str],
) -> bool:
    if not isinstance(conversation_context, dict):
        return False
    seen_current_user = False
    for sender_type, content in reversed(_recent_message_lines(conversation_context)):
        if sender_type != 'user':
            continue
        if not seen_current_user:
            seen_current_user = True
            continue
        normalized = _normalize_text(content)
        if any(_message_matches_term(normalized, term) for term in terms):
            return True
    return False


def _recent_messages_mention(
    conversation_context: dict[str, object] | None,
    terms: set[str],
) -> bool:
    for _sender_type, content in reversed(_recent_message_lines(conversation_context)):
        normalized = _normalize_text(content)
        if any(_message_matches_term(normalized, term) for term in terms):
            return True
    return False
