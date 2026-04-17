from __future__ import annotations

import re
from datetime import datetime
from typing import Any
from zoneinfo import ZoneInfo


def _message_matches_term(message: str, term: str) -> bool:
    from .conversation_focus_runtime import _message_matches_term as _impl

    return _impl(message, term)


def _normalize_text(message: str | None) -> str:
    from .conversation_focus_runtime import _normalize_text as _impl

    return _impl(message)


def _event_query_tokens(message: str, focus_hint: str | None = None) -> set[str]:
    source = _normalize_text(' '.join(part for part in [focus_hint or '', message] if part).strip())
    tokens = {
        token
        for token in re.findall(r'[a-z0-9]{3,}', source)
        if token
        not in {
            'quando',
            'qual',
            'quais',
            'que',
            'dia',
            'data',
            'proximo',
            'proxima',
            'proximoa',
            'evento',
            'eventos',
            'publico',
            'publicos',
            'amanha',
            'hoje',
            'ano',
            'desse',
            'deste',
            'este',
            'escola',
            'colegio',
        }
    }
    return tokens


def _format_event_datetime_br(value: str | None) -> str | None:
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace('Z', '+00:00'))
    except Exception:
        return None
    return parsed.astimezone(ZoneInfo('America/Sao_Paulo')).strftime('%d/%m/%Y às %Hh%M')


def _select_public_calendar_events(
    *,
    events: list[dict[str, Any]],
    message: str,
    focus_hint: str | None,
) -> list[dict[str, Any]]:
    normalized = _normalize_text(message)
    holiday_query = any(_message_matches_term(normalized, term) for term in {'feriado', 'feriados'})
    tokens = _event_query_tokens(message, focus_hint)
    scored: list[tuple[int, dict[str, Any]]] = []
    for event in events:
        haystack = _normalize_text(
            ' '.join(
                str(event.get(key, '')).strip()
                for key in ('title', 'description', 'category', 'audience')
            )
        )
        score = 0
        for token in tokens:
            if token in haystack:
                score += 2
        if any(
            _message_matches_term(normalized, term)
            for term in {'reuniao', 'reunião', 'pais', 'responsaveis', 'responsáveis'}
        ) and ('meeting' in haystack or 'reuniao' in haystack or 'responsaveis' in haystack):
            score += 3
        if any(
            _message_matches_term(normalized, term) for term in {'mostra', 'ciencias', 'ciências'}
        ) and ('mostra' in haystack or 'ciencias' in haystack):
            score += 3
        if any(
            _message_matches_term(normalized, term) for term in {'visita', 'tour', 'guiada'}
        ) and ('visita' in haystack or 'open_house' in haystack):
            score += 3
        if any(
            _message_matches_term(normalized, term) for term in {'feriado', 'feriados'}
        ) and any(term in haystack for term in {'feriado', 'holiday', 'recesso'}):
            score += 4
        if score > 0:
            scored.append((score, event))
    if scored:
        scored.sort(
            key=lambda item: (
                -item[0],
                str(item[1].get('starts_at', '')),
                str(item[1].get('title', '')),
            )
        )
        return [item for _score, item in scored[:2]]
    if holiday_query:
        return []
    sorted_events = sorted(
        events,
        key=lambda event: (
            str(event.get('starts_at', '')),
            str(event.get('title', '')),
        ),
    )
    return sorted_events[:2]


def _handle_public_calendar_events(context: Any) -> str:
    events = context.profile.get('public_calendar_events')
    holiday_query = any(
        _message_matches_term(_normalize_text(context.source_message), term)
        for term in {'feriado', 'feriados'}
    )
    if not isinstance(events, list) or not events:
        if holiday_query:
            return (
                f'Hoje eu nao tenho uma lista oficial de feriados publicada no calendario publico de '
                f'{context.school_reference}.'
            )
        return f'Hoje a base publica de eventos de {context.school_reference} nao trouxe agenda estruturada para esse pedido.'

    selected = _select_public_calendar_events(
        events=[item for item in events if isinstance(item, dict)],
        message=context.source_message,
        focus_hint=context.semantic_plan.focus_hint if context.semantic_plan else None,
    )
    if not selected:
        if holiday_query:
            return (
                f'Hoje eu ainda nao tenho uma lista oficial de feriados publicada no calendario publico de '
                f'{context.school_reference}. O que esta disponivel aqui sao eventos publicos como inicio das aulas, '
                'reunioes e visitas.'
            )
        return f'Hoje eu nao encontrei um evento publico especifico para esse pedido em {context.school_reference}.'

    if len(selected) == 1:
        item = selected[0]
        title = str(item.get('title', 'Evento publico')).strip()
        description = str(item.get('description', '')).strip()
        starts_at = _format_event_datetime_br(item.get('starts_at'))
        ends_at = _format_event_datetime_br(item.get('ends_at'))
        time_part = f'{starts_at}' if starts_at else 'data ainda nao informada'
        if starts_at and ends_at:
            time_part = f'{starts_at} até {ends_at.split(" às ")[-1]}'
        response = f'{title}: {time_part}.'
        if description:
            response += f' {description}'
        return response

    lines = ['Encontrei estes proximos eventos publicos relacionados a esse assunto:']
    for item in selected:
        title = str(item.get('title', 'Evento publico')).strip()
        starts_at = _format_event_datetime_br(item.get('starts_at')) or 'data ainda nao informada'
        lines.append(f'- {title}: {starts_at}.')
    return '\n'.join(lines)
