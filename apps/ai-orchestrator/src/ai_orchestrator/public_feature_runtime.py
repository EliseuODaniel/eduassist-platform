from __future__ import annotations

import re
from typing import Any

from .runtime_core_constants import PUBLIC_ENRICHMENT_TERMS


def _message_matches_term(message: str, term: str) -> bool:
    from .conversation_focus_runtime import _message_matches_term as _impl

    return _impl(message, term)


def _normalize_text(message: str | None) -> str:
    from .conversation_focus_runtime import _normalize_text as _impl

    return _impl(message)


def _recent_message_lines(
    conversation_context: dict[str, Any] | None,
) -> list[tuple[str, str]]:
    from .conversation_focus_runtime import _recent_message_lines as _impl

    return _impl(conversation_context)


def _extract_salient_terms(message: str) -> set[str]:
    from .intent_analysis_runtime import _extract_salient_terms as _impl

    return _impl(message)


def _feature_inventory_map(profile: dict[str, Any]) -> dict[str, dict[str, Any]]:
    inventory = profile.get('feature_inventory')
    if not isinstance(inventory, list):
        return {}
    result: dict[str, dict[str, Any]] = {}
    for item in inventory:
        if not isinstance(item, dict):
            continue
        key = str(item.get('feature_key', '')).strip().lower()
        if not key:
            continue
        result[key] = item
    return result


def _requested_public_features(message: str) -> list[str]:
    normalized = _normalize_text(message)
    feature_order = [
        ('biblioteca', 'biblioteca'),
        ('cantina', 'cantina'),
        ('laboratorio', 'laboratorio'),
        ('laboratorio de ciencias', 'laboratorio'),
        ('maker', 'maker'),
        ('espaco maker', 'maker'),
        ('academia', 'academia'),
        ('piscina', 'piscina'),
        ('quadra de tenis', 'quadra de tenis'),
        ('quadra', 'quadra'),
        ('futebol', 'futebol'),
        ('futsal', 'futebol'),
        ('volei', 'volei'),
        ('vôlei', 'volei'),
        ('danca', 'danca'),
        ('dança', 'danca'),
        ('teatro', 'teatro'),
        ('robotica', 'maker'),
        ('robótica', 'maker'),
        ('orientacao educacional', 'orientacao educacional'),
        ('orientação educacional', 'orientacao educacional'),
    ]
    found: list[str] = []
    for term, canonical in feature_order:
        if _message_matches_term(normalized, term) and canonical not in found:
            found.append(canonical)
    return found


def _is_public_feature_query(message: str) -> bool:
    normalized = _normalize_text(message)
    if _requested_public_features(message):
        return True
    return any(
        _message_matches_term(normalized, term)
        for term in {
            'estrutura',
            'infraestrutura',
            'espaco',
            'espaço',
            'espacos',
            'espaços',
            'campus',
            'aula de',
            'oficina de',
            'curso de',
            'atividade de',
            'clube de',
            'atividade',
            'atividades',
            'contraturno',
            *PUBLIC_ENRICHMENT_TERMS,
        }
    )


def _asks_why_feature_is_missing(message: str) -> bool:
    normalized = _normalize_text(message)
    return any(
        _message_matches_term(normalized, term)
        for term in {
            'por que nao tem',
            'por que não tem',
            'por que nao possui',
            'por que não possui',
            'por que nao oferece',
            'por que não oferece',
            'por que nao existe',
            'por que não existe',
        }
    )


def _extract_feature_gap_focus(message: str) -> str | None:
    normalized = _normalize_text(message)
    cleaned = re.sub(
        r'^(?:e\s+)?(?:essa escola|o colegio|o col[eé]gio|a escola)?\s*(?:tem|possui|oferece|tem aula de|aula de|oficina de|curso de|atividade de|por que nao tem|por que nao possui|por que nao oferece|por que nao existe)\s+',
        '',
        normalized,
    ).strip(' ?.')
    if cleaned.startswith('e '):
        cleaned = cleaned[2:].strip()
    if cleaned:
        return cleaned
    salient = sorted(_extract_salient_terms(message))
    if salient:
        return ' '.join(salient[:4])
    return None


def _feature_suggestion_replies(feature_keys: list[str]) -> list[str]:
    if 'biblioteca' in feature_keys:
        return [
            'Qual o horario da biblioteca?',
            'Qual o endereco da escola?',
            'Quero agendar uma visita',
            'Quais atividades a escola oferece?',
        ]
    if any(
        key in feature_keys
        for key in {'maker', 'danca', 'futebol', 'volei', 'teatro', 'laboratorio'}
    ):
        return [
            'Quais atividades no contraturno a escola oferece?',
            'Tem horarios dessas atividades?',
            'Quero agendar uma visita',
            'Qual o horario do 9o ano?',
        ]
    return [
        'Quais atividades a escola oferece?',
        'Quero agendar uma visita',
        'Qual o horario do 9o ano?',
        'Como vinculo minha conta?',
    ]


def _recent_public_feature_key(conversation_context: dict[str, Any] | None) -> str | None:
    for _sender_type, content in reversed(_recent_message_lines(conversation_context)):
        features = _requested_public_features(content)
        if len(features) == 1:
            return features[0]
        normalized = _normalize_text(content)
        for feature_key in (
            'biblioteca',
            'cantina',
            'laboratorio',
            'maker',
            'quadra',
            'piscina',
            'futebol',
            'volei',
            'teatro',
            'danca',
        ):
            if _message_matches_term(normalized, feature_key):
                return feature_key
    return None
