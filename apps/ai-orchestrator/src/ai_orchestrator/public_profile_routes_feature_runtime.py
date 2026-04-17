from __future__ import annotations

from typing import Any

from .intent_analysis_runtime import _is_follow_up_query, _message_matches_term, _normalize_text
from .public_feature_runtime import (
    _asks_why_feature_is_missing,
    _extract_feature_gap_focus,
    _feature_inventory_map,
    _is_public_feature_query,
    _recent_public_feature_key,
    _requested_public_features,
)
from .public_profile_support_runtime import _requested_public_attributes
from .public_timeline_runtime import _recent_trace_focus


def _compose_public_feature_answer_impl(
    *,
    profile: dict[str, Any],
    original_message: str,
    analysis_message: str,
    conversation_context: dict[str, Any] | None = None,
) -> str | None:
    feature_map = _feature_inventory_map(profile)
    school_name = str(profile.get('school_name', 'Colegio Horizonte'))
    requested_features = _requested_public_features(original_message)
    requested_attributes = set(_requested_public_attributes(original_message))
    recent_focus = _recent_trace_focus(conversation_context) or {}
    feature_followup_context = (
        isinstance(recent_focus, dict)
        and str(recent_focus.get('active_task', '')).strip() == 'public:features'
    )
    if (
        not requested_features
        and 'name' in requested_attributes
        and _is_follow_up_query(original_message)
    ):
        recent_feature = _recent_public_feature_key(conversation_context)
        if recent_feature:
            requested_features = [recent_feature]
    if (
        not requested_features
        and _is_follow_up_query(original_message)
        and not _is_public_feature_query(original_message)
    ):
        focus = _extract_feature_gap_focus(original_message)
        if (
            feature_followup_context
            and focus
            and focus not in {'atividade', 'atividades', 'contraturno'}
        ):
            return (
                f'Nao vi uma referencia oficial sobre {focus} no perfil publico do {school_name}. '
                'Se quiser, eu posso te mostrar o que esta documentado sobre estrutura e atividades.'
            )
        requested_features = _requested_public_features(analysis_message)
    if not requested_features and _is_follow_up_query(original_message):
        recent_feature = _recent_public_feature_key(conversation_context)
        if recent_feature:
            requested_features = [recent_feature]
    asks_why_absent = _asks_why_feature_is_missing(original_message)
    if not requested_features and _is_public_feature_query(original_message):
        generic_activity_query = any(
            _message_matches_term(_normalize_text(original_message), term)
            for term in {'atividade', 'atividades', 'contraturno'}
        ) and not any(
            _message_matches_term(_normalize_text(original_message), term)
            for term in {'aula de', 'oficina de', 'curso de', 'clube de', 'atividade de'}
        )
        generic_structure_query = any(
            _message_matches_term(_normalize_text(original_message), term)
            for term in {
                'estrutura',
                'infraestrutura',
                'espaco',
                'espaço',
                'espacos',
                'espaços',
                'campus',
            }
        )
        focus = _extract_feature_gap_focus(original_message)
        if (
            focus
            and not generic_activity_query
            and not generic_structure_query
            and focus not in {'atividade', 'atividades', 'contraturno'}
        ):
            return (
                f'Nao vi uma referencia oficial sobre {focus} no perfil publico do {school_name}. '
                'Se voce quiser, eu posso te dizer quais atividades e espacos aparecem oficialmente.'
            )
        available_items: list[str] = []
        for feature_key in (
            'biblioteca',
            'maker',
            'quadra',
            'futebol',
            'volei',
            'danca',
            'teatro',
            'cantina',
            'orientacao educacional',
        ):
            item = feature_map.get(feature_key)
            if not item or not bool(item.get('available')):
                continue
            label = str(item.get('label', feature_key)).strip().lower()
            if label and label not in available_items:
                available_items.append(label)
        if available_items:
            preview = ', '.join(available_items[:5])
            return (
                f'Hoje, a estrutura do {school_name} inclui atividades e espacos como {preview}. '
                'Se quiser, eu posso te detalhar qualquer um deles.'
            )
        return (
            f'Hoje o perfil publico do {school_name} nao traz esse detalhe de estrutura ou atividade. '
            'Se quiser, eu posso te mostrar o que esta oficialmente documentado.'
        )
    if not requested_features:
        return None
    if len(requested_features) == 1:
        feature_key = requested_features[0]
        item = feature_map.get(feature_key)
        if item is None:
            return (
                f'Nao vi uma referencia oficial sobre {feature_key} no perfil publico do {school_name}. '
                'Se quiser, eu posso te mostrar o que esta documentado sobre estrutura e atividades.'
            )
        label = str(item.get('label', feature_key)).strip()
        notes = str(item.get('notes', '')).strip()
        available = bool(item.get('available'))
        if available and 'name' in requested_attributes:
            return f'O nome desse espaco e {label}.'
        if available:
            if asks_why_absent:
                return f'Na verdade, o {school_name} tem sim {label}. {notes}'.strip()
            if feature_key == 'biblioteca':
                return f'Sim. O {school_name} tem a {label}. {notes}'.strip()
            return f'Sim. O {school_name} oferece {label}. {notes}'.strip()
        if asks_why_absent:
            return f'Hoje o {school_name} nao oferece {label}. {notes}'.strip()
        return f'Nao. O {school_name} nao oferece {label}. {notes}'.strip()

    lines = [f'Sobre estrutura e atividades do {school_name}:']
    for feature_key in requested_features:
        item = feature_map.get(feature_key)
        if item is None:
            lines.append(f'- Ainda nao encontrei uma informacao oficial sobre {feature_key}.')
            continue
        label = str(item.get('label', feature_key)).strip()
        notes = str(item.get('notes', '')).strip()
        available = bool(item.get('available'))
        if available:
            lines.append(f'- Sim: {label}. {notes}'.rstrip())
        else:
            lines.append(f'- Nao: {label}. {notes}'.rstrip())
    return '\n'.join(lines)
