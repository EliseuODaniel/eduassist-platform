from __future__ import annotations

from typing import Any

from .conversation_focus_runtime import _recent_conversation_focus
from .public_profile_glue_runtime import _recent_messages_mention
from .public_timeline_runtime import (
    _compose_public_timeline_lifecycle_answer,
    _compose_public_travel_planning_answer,
    _compose_public_year_three_phases_answer,
    _is_explicit_school_year_start_query,
    _is_public_timeline_lifecycle_query,
    _is_public_travel_planning_query,
    _is_public_year_three_phase_query,
    _mentions_school_year_start_topic,
)


def _intent_analysis_impl(name: str):
    from . import intent_analysis_runtime as _intent_analysis_runtime

    return getattr(_intent_analysis_runtime, name)


def _is_follow_up_query(message: str) -> bool:
    return _intent_analysis_impl('_is_follow_up_query')(message)


def _message_matches_term(message: str, term: str) -> bool:
    return _intent_analysis_impl('_message_matches_term')(message, term)


def _handle_public_timeline_impl(context: Any) -> str:
    entries = context.profile.get('public_timeline')
    if not isinstance(entries, list) or not entries:
        return f'Hoje a base publica de {context.school_reference} nao traz um marco institucional estruturado para essa data.'

    normalized = context.normalized

    if _is_public_timeline_lifecycle_query(context.source_message):
        lifecycle_answer = _compose_public_timeline_lifecycle_answer(context.profile)
        if lifecycle_answer:
            return lifecycle_answer
    if _is_public_travel_planning_query(context.source_message):
        travel_answer = _compose_public_travel_planning_answer(context.profile)
        if travel_answer:
            return travel_answer
    if _is_public_year_three_phase_query(context.source_message):
        phases_answer = _compose_public_year_three_phases_answer(context.profile)
        if phases_answer:
            return phases_answer

    def _pick(topic_fragment: str) -> dict[str, Any] | None:
        for item in entries:
            if not isinstance(item, dict):
                continue
            if topic_fragment in str(item.get('topic_key', '')):
                return item
        return None

    wants_enrollment = _message_matches_term(normalized, 'matricula') or _message_matches_term(
        normalized, 'matrícula'
    )
    wants_school_year_start = _mentions_school_year_start_topic(context.source_message)
    explicit_school_year_start_request = _is_explicit_school_year_start_query(
        context.source_message
    )
    wants_family = any(
        _message_matches_term(normalized, term)
        for term in {'responsaveis', 'responsáveis', 'reuniao', 'reunião', 'familia', 'família'}
    )
    if wants_enrollment and wants_school_year_start:
        lines: list[str] = []
        topics: list[str] = ['admissions_opening', 'school_year_start']
        if wants_family:
            topics.append('family_meeting')
        for topic in topics:
            item = _pick(topic)
            if not isinstance(item, dict):
                continue
            summary = str(item.get('summary', '')).strip()
            notes = str(item.get('notes', '')).strip()
            line = f'{summary} {notes}'.strip()
            if line:
                lines.append(line)
        if lines:
            return '\n'.join(lines)

    chosen: dict[str, Any] | None = None
    recent_focus = _recent_conversation_focus(context.conversation_context) or {}
    if _is_follow_up_query(context.source_message) and not explicit_school_year_start_request:
        if _recent_messages_mention(
            context.conversation_context,
            {'comecam as aulas', 'começam as aulas', 'aulas', 'ano letivo'},
        ):
            chosen = _pick('school_year_start')
        elif _recent_messages_mention(
            context.conversation_context,
            {'formatura', 'cerimonia de conclusao', 'cerimônia de conclusão'},
        ):
            chosen = _pick('graduation')
        elif _recent_messages_mention(
            context.conversation_context,
            {'matricula', 'matrícula', 'pre cadastro', 'pré-cadastro'},
        ):
            chosen = _pick('admissions_opening')
    if explicit_school_year_start_request:
        chosen = _pick('school_year_start')
    elif (
        _is_follow_up_query(context.source_message)
        and str(recent_focus.get('kind', '') or '').strip() == 'admissions'
        and (wants_school_year_start or _message_matches_term(normalized, 'aulas'))
    ):
        chosen = _pick('school_year_start')
    elif chosen is None and (
        _message_matches_term(normalized, 'matricula')
        or _message_matches_term(normalized, 'matrícula')
    ):
        chosen = _pick('admissions_opening')
    elif chosen is None and _message_matches_term(normalized, 'formatura'):
        chosen = _pick('graduation')
    elif chosen is None and wants_school_year_start:
        chosen = _pick('school_year_start')

    if chosen is None:
        chosen = next((item for item in entries if isinstance(item, dict)), None)
    if chosen is None:
        return f'Hoje a base publica de {context.school_reference} nao traz um marco institucional estruturado para essa data.'

    summary = str(chosen.get('summary', '')).strip()
    notes = str(chosen.get('notes', '')).strip()
    if notes:
        return f'{summary} {notes}'.strip()
    return summary
