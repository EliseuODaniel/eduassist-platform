from __future__ import annotations

import re
from typing import Any

from .conversation_focus_runtime import _assistant_already_introduced, _normalize_text
from .intent_analysis_runtime import _message_matches_term


def _select_public_segment(message: str) -> str | None:
    normalized = _normalize_text(message)
    if any(
        _message_matches_term(normalized, term)
        for term in {
            'fundamental i',
            'anos iniciais',
            '1o ano do fundamental',
            '2o ano do fundamental',
            '3o ano do fundamental',
            '4o ano do fundamental',
            '5o ano do fundamental',
            'primeiro ano do fundamental',
            'segundo ano do fundamental',
            'terceiro ano do fundamental',
            'quarto ano do fundamental',
            'quinto ano do fundamental',
        }
    ):
        return 'Ensino Fundamental I'
    if any(
        _message_matches_term(normalized, term)
        for term in {'fundamental', 'fundamental ii', '6o ano', '7o ano', '8o ano', '9o ano'}
    ):
        return 'Ensino Fundamental II'
    if any(
        _message_matches_term(normalized, term)
        for term in {'ensino medio', 'ensino médio', 'medio', 'médio', '1o ano', '2o ano', '3o ano'}
    ):
        return 'Ensino Medio'
    return None


def _segment_semantic_key(value: str | None) -> str | None:
    normalized = _normalize_text(str(value or '').strip())
    if not normalized:
        return None
    if any(
        _message_matches_term(normalized, term)
        for term in {
            'fundamental i',
            'anos iniciais',
            '1o ano do fundamental',
            '2o ano do fundamental',
            '3o ano do fundamental',
            '4o ano do fundamental',
            '5o ano do fundamental',
            'primeiro ano do fundamental',
            'segundo ano do fundamental',
            'terceiro ano do fundamental',
            'quarto ano do fundamental',
            'quinto ano do fundamental',
        }
    ):
        return 'fundamental_i'
    if any(
        _message_matches_term(normalized, term)
        for term in {'fundamental ii', '6o ano', '7o ano', '8o ano', '9o ano'}
    ):
        return 'fundamental_ii'
    if 'fundamental' in normalized:
        return 'fundamental_ii'
    if any(
        _message_matches_term(normalized, term)
        for term in {
            'ensino medio',
            'ensino médio',
            'medio',
            'médio',
            '1a a 3a serie',
            '1a a 3a série',
            '1o ano',
            '2o ano',
            '3o ano',
        }
    ):
        return 'ensino_medio'
    return normalized


def _public_segment_matches(row_segment: str | None, requested_segment: str | None) -> bool:
    if requested_segment is None:
        return True
    return _segment_semantic_key(row_segment) == _segment_semantic_key(requested_segment)


def _extract_grade_reference(message: str) -> str | None:
    normalized = _normalize_text(message)
    match = re.search(r'\b(6o ano|7o ano|8o ano|9o ano|1o ano|2o ano|3o ano)\b', normalized)
    if not match:
        return None
    return match.group(1)


def _school_subject_reference(reference: str) -> str:
    cleaned = reference.strip()
    if cleaned.startswith(('a ', 'o ')):
        return cleaned
    return f'o {cleaned}'


def _school_object_reference(reference: str) -> str:
    cleaned = reference.strip()
    if cleaned == 'a escola':
        return 'da escola'
    if cleaned.startswith(('a ', 'o ')):
        return f'd{cleaned}'
    return f'de {cleaned}'


def _published_public_segments(profile: dict[str, Any]) -> set[str]:
    return {
        str(item).strip()
        for item in profile.get('segments', [])
        if isinstance(item, str) and str(item).strip()
    }


def _requested_unpublished_public_segment(context: Any) -> str | None:
    requested_segment = (
        _select_public_segment(context.source_message) or context.slot_memory.public_pricing_segment
    )
    if not requested_segment:
        return None
    requested_key = _segment_semantic_key(requested_segment)
    if any(
        _segment_semantic_key(published_segment) == requested_key
        for published_segment in _published_public_segments(context.profile)
    ):
        return None
    return requested_segment


def _compose_public_segment_scope_gap(
    context: Any,
    *,
    requested_segment: str,
    topic: str,
) -> str:
    published_segments = sorted(_published_public_segments(context.profile))
    published_text = (
        ', '.join(published_segments) if published_segments else 'os segmentos hoje publicados'
    )
    return (
        f'Hoje eu nao tenho um detalhamento publico de {topic} para {requested_segment.lower()} em {context.school_reference}. '
        f'Pelo que a escola publica aqui, o recorte institucional coberto hoje e {published_text}.'
    )


def _public_visit_offers(profile: dict[str, Any]) -> list[dict[str, Any]]:
    entries = profile.get('visit_offers')
    return [item for item in entries if isinstance(item, dict)] if isinstance(entries, list) else []


def _public_service_catalog(profile: dict[str, Any]) -> list[dict[str, Any]]:
    entries = profile.get('service_catalog')
    return [item for item in entries if isinstance(item, dict)] if isinstance(entries, list) else []


def _public_feature_inventory(profile: dict[str, Any]) -> list[dict[str, Any]]:
    entries = profile.get('feature_inventory')
    return [item for item in entries if isinstance(item, dict)] if isinstance(entries, list) else []


def _capability_summary_lines(profile: dict[str, Any]) -> list[str]:
    capability_model = profile.get('assistant_capabilities')
    school_name = str(
        (capability_model.get('school_name') if isinstance(capability_model, dict) else None)
        or profile.get('school_name', 'Colegio Horizonte')
    )
    segments_source = (
        capability_model.get('segments')
        if isinstance(capability_model, dict)
        else profile.get('segments', [])
    )
    segments = [str(item) for item in segments_source if isinstance(item, str)]
    segment_summary = ', '.join(segments[:2]).lower() if segments else 'os segmentos atendidos'
    public_topics = [
        str(item)
        for item in (
            capability_model.get('public_topics', []) if isinstance(capability_model, dict) else []
        )
        if isinstance(item, str)
    ]
    protected_topics = [
        str(item)
        for item in (
            capability_model.get('protected_topics', [])
            if isinstance(capability_model, dict)
            else []
        )
        if isinstance(item, str)
    ]
    workflow_topics = [
        str(item)
        for item in (
            capability_model.get('workflow_topics', [])
            if isinstance(capability_model, dict)
            else []
        )
        if isinstance(item, str)
    ]
    lines = [
        f'Posso te ajudar com a rotina institucional do {school_name} em {segment_summary}.',
        'No lado publico, eu cubro: '
        + '; '.join(
            public_topics
            or [
                'matricula, bolsas, visitas, horarios, calendario, biblioteca, uniforme, transporte e vida escolar'
            ]
        )
        + '.',
        'Se sua conta estiver vinculada, eu tambem consigo cuidar de: '
        + '; '.join(protected_topics or ['notas, faltas, boletos e vida financeira'])
        + '.',
        'Quando o assunto pedir acao, eu posso seguir com: '
        + '; '.join(
            workflow_topics
            or [
                'solicitacoes para secretaria, coordenacao, orientacao educacional, financeiro ou direcao'
            ]
        )
        + '.',
        'Se quiser, me diga o tema do jeito que for mais natural e eu sigo com voce.',
    ]
    return lines


def _concierge_topic_examples(profile: dict[str, Any], limit: int = 5) -> list[str]:
    examples: list[str] = []
    capability_model = profile.get('assistant_capabilities')
    capability_topics = (
        capability_model.get('public_topics', []) if isinstance(capability_model, dict) else []
    )
    for item in capability_topics:
        if not isinstance(item, str):
            continue
        label = item.strip().lower()
        if label and label not in examples:
            examples.append(label)
        if len(examples) >= limit:
            return examples

    for service in _public_service_catalog(profile):
        title = str(service.get('title', '')).strip().lower()
        if not title:
            continue
        if 'admis' in title:
            label = 'matricula e visita'
        elif 'finance' in title:
            label = 'financeiro e boletos'
        elif 'secretaria' in title:
            label = 'secretaria e documentos'
        elif 'coorden' in title:
            label = 'coordenacao'
        elif 'orienta' in title:
            label = 'orientacao educacional'
        elif 'dire' in title or 'ouvidoria' in title:
            label = 'direcao e ouvidoria'
        else:
            label = title
        if label not in examples:
            examples.append(label)
        if len(examples) >= limit:
            return examples

    return examples or ['matricula', 'horarios', 'financeiro', 'secretaria', 'visitas']


def _compose_concierge_topic_examples(profile: dict[str, Any], limit: int = 5) -> str:
    examples = _concierge_topic_examples(profile, limit=limit)
    if not examples:
        return 'matricula, horarios, financeiro, secretaria e visitas'
    if len(examples) == 1:
        return examples[0]
    if len(examples) == 2:
        return f'{examples[0]} e {examples[1]}'
    return ', '.join(examples[:-1]) + f' e {examples[-1]}'


def _requested_public_attribute(message: str) -> str | None:
    attributes = _requested_public_attributes(message)
    return attributes[0] if attributes else None


def _requested_public_attributes(message: str) -> tuple[str, ...]:
    normalized = _normalize_text(message)
    ordered_matches: list[str] = []

    def add_if_present(value: str, terms: set[str]) -> None:
        if value in ordered_matches:
            return
        if any(_message_matches_term(normalized, term) for term in terms):
            ordered_matches.append(value)

    add_if_present('close_time', {'fecha', 'fechar', 'fechamento', 'encerra', 'encerramento'})
    add_if_present('open_time', {'abre', 'abertura'})
    add_if_present('whatsapp', {'whatsapp', 'whats', 'zap'})
    add_if_present('email', {'email', 'e-mail', 'mail'})
    add_if_present('phone', {'telefone', 'fone', 'ligacao', 'ligação'})
    add_if_present('age', {'idade', 'quantos anos'})
    add_if_present('name', {'nome', 'quem e', 'quem é'})
    add_if_present('contact', {'contato', 'canal', 'como falo', 'como falar', 'falar com'})
    return tuple(ordered_matches)


def _humanize_service_eta(eta: str) -> str:
    cleaned = eta.strip()
    if not cleaned:
        return 'prazo nao informado'
    normalized = _normalize_text(cleaned)
    if normalized.startswith('retorno em '):
        return cleaned
    if normalized.startswith('protocolo imediato'):
        return cleaned
    return f'retorno em {cleaned}'


def _compose_assistant_identity_answer(
    profile: dict[str, Any],
    *,
    conversation_context: dict[str, Any] | None = None,
) -> str:
    school_name = str(profile.get('school_name', 'Colegio Horizonte'))
    base = (
        f'Voce esta falando com o EduAssist, o assistente institucional do {school_name}. '
        'Eu consigo te orientar por aqui, consultar informacoes da escola e abrir solicitacoes com protocolo. '
        'Se precisar, eu tambem te encaminho para secretaria, matricula e atendimento comercial, coordenacao, orientacao educacional, financeiro ou direcao.'
    )
    return base if _assistant_already_introduced(conversation_context) else base
