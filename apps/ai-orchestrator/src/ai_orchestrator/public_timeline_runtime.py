from __future__ import annotations

from datetime import date
from typing import Any

from .runtime_core_constants import PUBLIC_UTILITY_DATE_TERMS


def _message_matches_term(message: str, term: str) -> bool:
    from .conversation_focus_runtime import _message_matches_term as _impl

    return _impl(message, term)


def _normalize_text(message: str | None) -> str:
    from .conversation_focus_runtime import _normalize_text as _impl

    return _impl(message)


def _recent_messages_mention(
    conversation_context: dict[str, Any] | None,
    terms: set[str],
) -> bool:
    from .conversation_focus_runtime import _recent_messages_mention as _impl

    return _impl(conversation_context, terms)


def _recent_trace_focus(conversation_context: dict[str, Any] | None) -> dict[str, str] | None:
    from .conversation_focus_runtime import _recent_trace_focus as _impl

    return _impl(conversation_context)


def _contains_any(message: str, terms: set[str]) -> bool:
    from .intent_analysis_runtime import _contains_any as _impl

    return _impl(message, terms)


def compose_public_canonical_lane_answer(*args, **kwargs):
    from .public_profile_runtime import compose_public_canonical_lane_answer as _impl

    return _impl(*args, **kwargs)


def _mentions_school_year_start_topic(message: str) -> bool:
    normalized = _normalize_text(message)
    return any(
        _message_matches_term(normalized, term)
        for term in {
            'iniciam as aulas',
            'quando iniciam as aulas',
            'quando comecam as aulas',
            'quando começam as aulas',
            'quando inicia o ano letivo',
            'inicio das aulas',
            'início das aulas',
            'comeco das aulas',
            'começo das aulas',
            'ano letivo',
        }
    )


def _is_explicit_school_year_start_query(message: str) -> bool:
    normalized = _normalize_text(message)
    if not _mentions_school_year_start_topic(message):
        return False
    return any(
        _message_matches_term(normalized, term)
        for term in {
            'quando',
            'qual data',
            'que dia',
            'quando comeca',
            'quando começa',
            'quando inicia',
            'quando iniciam',
            'inicio',
            'início',
            'comeco',
            'começo',
        }
    )


def _is_public_timeline_query(message: str) -> bool:
    normalized = _normalize_text(message)
    if _is_public_timeline_lifecycle_query(message):
        return True
    if _is_public_travel_planning_query(message):
        return True
    if _is_public_year_three_phase_query(message):
        return True
    if _mentions_school_year_start_topic(message):
        return True
    asks_timing = any(
        _message_matches_term(normalized, term)
        for term in {
            'quando',
            'qual data',
            'que dia',
            'quando comeca',
            'quando começa',
            'quando inicia',
            'quando iniciam',
            'comeco',
            'começo',
            'quando fecha',
            'inicio',
            'início',
            'abertura',
            'comeco das aulas',
            'começo das aulas',
            'comecam as aulas',
            'começam as aulas',
            'iniciam as aulas',
            'início das aulas',
        }
    )
    if not asks_timing:
        return False
    return any(
        _message_matches_term(normalized, term)
        for term in {
            'matricula',
            'matrícula',
            'formatura',
            'inicio das aulas',
            'início das aulas',
            'comeco das aulas',
            'começo das aulas',
            'comecam as aulas',
            'começam as aulas',
            'iniciam as aulas',
            'ano letivo',
        }
    )


def _is_public_timeline_lifecycle_query(message: str) -> bool:
    normalized = _normalize_text(message)
    has_before_after = any(
        _message_matches_term(normalized, term)
        for term in {
            'antes da confirmacao da vaga',
            'antes da confirmação da vaga',
            'depois do inicio das aulas',
            'depois do início das aulas',
            'antes ou depois',
            'antes das aulas',
            'depois das aulas',
            'primeira reuniao',
            'primeira reunião',
        }
    )
    has_ordering = any(
        _message_matches_term(normalized, term)
        for term in {'ordene', 'ordem', 'sequencia', 'sequência', 'linha do tempo', 'passo a passo'}
    )
    asks_which_comes_first = any(
        _message_matches_term(normalized, term)
        for term in {'qual vem primeiro', 'o que vem primeiro', 'vem primeiro'}
    )
    mentions_core_milestones = (
        any(_message_matches_term(normalized, term) for term in {'vaga', 'matricula', 'matrícula'})
        and any(
            _message_matches_term(normalized, term)
            for term in {'inicio das aulas', 'início das aulas', 'aulas'}
        )
        and any(
            _message_matches_term(normalized, term)
            for term in {'responsaveis', 'responsáveis', 'reuniao', 'reunião', 'familia', 'família'}
        )
    )
    mentions_marcos_between = (
        _message_matches_term(normalized, 'marcos entre')
        and any(
            _message_matches_term(normalized, term) for term in {'vaga', 'matricula', 'matrícula'}
        )
        and any(
            _message_matches_term(normalized, term)
            for term in {
                'inicio do ano letivo',
                'início do ano letivo',
                'inicio das aulas',
                'início das aulas',
            }
        )
        and any(
            _message_matches_term(normalized, term)
            for term in {
                'reuniao de responsaveis',
                'reunião de responsáveis',
                'responsaveis',
                'responsáveis',
            }
        )
    )
    return (
        has_before_after
        or mentions_marcos_between
        or (
            any(_message_matches_term(normalized, term) for term in {'antes', 'depois'})
            and any(
                _message_matches_term(normalized, term)
                for term in {
                    'vaga',
                    'matricula',
                    'matrícula',
                    'inicio das aulas',
                    'início das aulas',
                    'aulas',
                }
            )
        )
        or ((has_ordering or asks_which_comes_first) and mentions_core_milestones)
    )


def _is_public_travel_planning_query(message: str) -> bool:
    normalized = _normalize_text(message)
    return 'viagem' in normalized and any(
        _message_matches_term(normalized, term)
        for term in {'calendario', 'calendário', 'marcos', 'vida escolar', 'datas'}
    )


def _is_public_year_three_phase_query(message: str) -> bool:
    normalized = _normalize_text(message)
    return (
        (
            'tres fases' in normalized
            and all(term in normalized for term in {'admiss', 'rotina', 'fechamento'})
        )
        or (
            all(term in normalized for term in {'admiss', 'rotina academica', 'fechamento'})
            and any(
                _message_matches_term(normalized, term)
                for term in {
                    'distribui',
                    'distribui entre',
                    'olhando so a base publica',
                    'olhando apenas a base publica',
                }
            )
        )
        or (
            all(term in normalized for term in {'admiss', 'rotina academica', 'fechamento'})
            and any(
                _message_matches_term(normalized, term)
                for term in {'se eu dividir o ano', 'dividir o ano', 'dividir o ano escolar'}
            )
        )
    )


def _is_public_calendar_event_query(message: str) -> bool:
    normalized = _normalize_text(message)
    if any(
        _message_matches_term(normalized, term)
        for term in {
            'feriado',
            'feriados',
            'feriado do ano',
            'feriados do ano',
            'feriados desse ano',
            'feriados deste ano',
        }
    ):
        return True
    if any(
        _message_matches_term(normalized, term)
        for term in {
            'proximo evento',
            'próximo evento',
            'proxima reuniao',
            'próxima reunião',
            'reuniao de pais',
            'reunião de pais',
            'reuniao geral',
            'reunião geral',
            'mostra de ciencias',
            'mostra de ciências',
            'plantao pedagogico',
            'plantão pedagógico',
            'visita guiada',
        }
    ):
        return True
    asks_timing = any(
        _message_matches_term(normalized, term)
        for term in {'quando', 'qual data', 'que dia', 'quando vai ser', 'quando acontece'}
    )
    if not asks_timing:
        return False
    return any(
        _message_matches_term(normalized, term)
        for term in {
            'reuniao',
            'reunião',
            'evento',
            'mostra',
            'feira',
            'plantao',
            'plantão',
            'visita guiada',
            'cerimonia',
            'cerimônia',
        }
    )


def _is_public_date_query(message: str) -> bool:
    normalized = _normalize_text(message)
    return any(_message_matches_term(normalized, term) for term in PUBLIC_UTILITY_DATE_TERMS)


def _format_brazilian_date(value: date) -> str:
    month_names = {
        1: 'janeiro',
        2: 'fevereiro',
        3: 'marco',
        4: 'abril',
        5: 'maio',
        6: 'junho',
        7: 'julho',
        8: 'agosto',
        9: 'setembro',
        10: 'outubro',
        11: 'novembro',
        12: 'dezembro',
    }
    return f'{value.day} de {month_names.get(value.month, str(value.month))} de {value.year}'


def _parse_iso_date_value(value: Any) -> date | None:
    if isinstance(value, date):
        return value
    text = str(value or '').strip()
    if not text:
        return None
    try:
        return date.fromisoformat(text[:10])
    except ValueError:
        return None


def _format_public_date_text(value: Any) -> str:
    parsed = _parse_iso_date_value(value)
    if parsed is not None:
        return _format_brazilian_date(parsed)
    return str(value or 'data nao informada').strip() or 'data nao informada'


def _timeline_entry(profile: dict[str, Any], topic_fragment: str) -> dict[str, Any] | None:
    entries = profile.get('public_timeline')
    if not isinstance(entries, list):
        return None
    for item in entries:
        if not isinstance(item, dict):
            continue
        if topic_fragment in str(item.get('topic_key', '')):
            return item
    return None


def _timeline_event_date(item: dict[str, Any] | None) -> str:
    if not isinstance(item, dict):
        return ''
    return str(item.get('event_date') or item.get('starts_at') or '').strip()


def _compose_public_timeline_lifecycle_answer(profile: dict[str, Any]) -> str | None:
    admissions = _timeline_entry(profile, 'admissions_opening')
    school_year = _timeline_entry(profile, 'school_year_start')
    family_meeting = _timeline_entry(profile, 'family_meeting')
    if (
        not isinstance(admissions, dict)
        and not isinstance(school_year, dict)
        and not isinstance(family_meeting, dict)
    ):
        return None
    school_year_date = _timeline_event_date(school_year) if isinstance(school_year, dict) else ''
    family_date = _timeline_event_date(family_meeting) if isinstance(family_meeting, dict) else ''
    if school_year_date and family_date:
        ordering = 'depois' if family_date >= school_year_date else 'antes'
        parts = [f'A primeira reuniao com responsaveis acontece {ordering} do inicio das aulas.']
    else:
        parts: list[str] = []
    if isinstance(admissions, dict):
        admission_text = f'{str(admissions.get("summary", "")).strip()} {str(admissions.get("notes", "")).strip()}'.strip()
        if admission_text:
            parts.append(f'1) Matricula e ingresso: {admission_text}')
    if isinstance(school_year, dict):
        school_year_text = f'{str(school_year.get("summary", "")).strip()} {str(school_year.get("notes", "")).strip()}'.strip()
        if school_year_text:
            parts.append(f'2) Inicio das aulas: {school_year_text}')
    if isinstance(family_meeting, dict):
        family_meeting_text = f'{str(family_meeting.get("summary", "")).strip()} {str(family_meeting.get("notes", "")).strip()}'.strip()
        if family_meeting_text:
            parts.append(f'3) Primeira reuniao com responsaveis: {family_meeting_text}')
    if len(parts) > 1:
        parts.append(
            'Na pratica, esse e o recorte publico em ordem: matricula primeiro, aulas depois e reuniao com as familias na sequencia.'
        )
    answer = ' '.join(part for part in parts if part).strip()
    if answer and len(parts) >= 3:
        return answer
    return compose_public_canonical_lane_answer('public_bundle.timeline_lifecycle', profile=profile)


def _compose_public_timeline_before_after_answer(profile: dict[str, Any]) -> str | None:
    school_year = _timeline_entry(profile, 'school_year_start')
    family_meeting = _timeline_entry(profile, 'family_meeting')
    if not isinstance(school_year, dict) or not isinstance(family_meeting, dict):
        return None
    school_year_date = _timeline_event_date(school_year)
    family_date = _timeline_event_date(family_meeting)
    ordering = (
        'depois'
        if school_year_date and family_date and family_date >= school_year_date
        else 'antes'
    )
    school_year_text = str(school_year.get('summary', '')).strip()
    family_text = str(family_meeting.get('summary', '')).strip()
    parts = [f'A primeira reuniao com responsaveis acontece {ordering} do inicio das aulas.']
    if school_year_text:
        parts.append(f'Inicio das aulas: {school_year_text}')
    if family_text:
        parts.append(f'Primeira reuniao: {family_text}')
    return ' '.join(parts).strip() or None


def _compose_public_timeline_order_only_answer(profile: dict[str, Any]) -> str | None:
    admissions = _timeline_entry(profile, 'admissions_opening')
    school_year = _timeline_entry(profile, 'school_year_start')
    family_meeting = _timeline_entry(profile, 'family_meeting')
    parts: list[str] = []
    if isinstance(admissions, dict):
        summary = str(admissions.get('summary', '')).strip()
        if summary:
            parts.append(f'1) Matricula e ingresso: {summary}')
    if isinstance(school_year, dict):
        summary = str(school_year.get('summary', '')).strip()
        if summary:
            parts.append(f'2) Inicio das aulas: {summary}')
    if isinstance(family_meeting, dict):
        summary = str(family_meeting.get('summary', '')).strip()
        if summary:
            parts.append(f'3) Primeira reuniao com responsaveis: {summary}')
    if parts:
        parts.append(
            'Em ordem pratica, o recorte fica assim: matricula primeiro, aulas depois e reuniao com as familias na sequencia.'
        )
    return ' '.join(parts).strip() if parts else None


def _is_public_timeline_before_after_query(message: str) -> bool:
    normalized = _normalize_text(message)
    return any(
        _message_matches_term(normalized, term)
        for term in {
            'antes ou depois',
            'antes das aulas',
            'depois das aulas',
            'primeira reuniao',
            'primeira reunião',
        }
    )


def _compose_contextual_public_timeline_followup_answer(
    *,
    request_message: str,
    conversation_context: dict[str, Any] | None,
    profile: dict[str, Any] | None,
) -> str | None:
    if not isinstance(profile, dict):
        return None
    normalized = _normalize_text(request_message)
    asks_before_after = any(
        _message_matches_term(normalized, term)
        for term in {
            'antes ou depois',
            'primeira reuniao',
            'primeira reunião',
            'antes das aulas',
            'depois das aulas',
        }
    )
    asks_order_only = any(
        _message_matches_term(normalized, term)
        for term in {
            'so esse recorte',
            'só esse recorte',
            'nao quero o calendario inteiro',
            'não quero o calendário inteiro',
            'recorte em ordem',
        }
    )
    if asks_before_after:
        direct_before_after = _compose_public_timeline_before_after_answer(profile)
        if direct_before_after:
            return direct_before_after
    if asks_order_only:
        direct_order_only = _compose_public_timeline_order_only_answer(profile)
        if direct_order_only:
            return direct_order_only
    recent_focus = _recent_trace_focus(conversation_context) or {}
    active_task = str(recent_focus.get('active_task', '') or '').strip()
    timeline_thread_active = active_task in {'public:timeline', 'public:calendar_events'}
    timeline_recent_context = timeline_thread_active or _recent_messages_mention(
        conversation_context,
        {'matricula', 'matrícula', 'aulas', 'reuniao', 'reunião', 'responsaveis', 'responsáveis'},
    )
    if asks_before_after and (
        timeline_recent_context
        or any(
            _message_matches_term(normalized, term)
            for term in {'aulas', 'reuniao', 'reunião', 'responsaveis', 'responsáveis'}
        )
    ):
        return _compose_public_timeline_before_after_answer(profile)
    if asks_order_only and timeline_recent_context:
        return _compose_public_timeline_order_only_answer(profile)
    return None


def _compose_public_travel_planning_answer(profile: dict[str, Any]) -> str | None:
    admissions = _timeline_entry(profile, 'admissions_opening')
    school_year = _timeline_entry(profile, 'school_year_start')
    graduation = _timeline_entry(profile, 'graduation')
    milestones: list[str] = []
    for item in (admissions, school_year, graduation):
        if not isinstance(item, dict):
            continue
        summary = str(item.get('summary', '')).strip()
        if summary:
            milestones.append(f'- {summary}')
    if not milestones:
        return None
    return (
        'Para planejar uma viagem sem atrapalhar a vida escolar, vale observar estes marcos publicos antes de fechar datas:\n'
        + '\n'.join(milestones)
    )


def _compose_public_year_three_phases_answer(profile: dict[str, Any]) -> str | None:
    admissions = _timeline_entry(profile, 'admissions_opening')
    school_year = _timeline_entry(profile, 'school_year_start')
    graduation = _timeline_entry(profile, 'graduation')
    parts: list[str] = []
    if isinstance(admissions, dict):
        summary = str(admissions.get('summary', '')).strip()
        if summary:
            parts.append(f'Admissao: {summary}')
    if isinstance(school_year, dict):
        summary = str(school_year.get('summary', '')).strip()
        if summary:
            parts.append(f'Rotina academica: {summary}')
    if isinstance(graduation, dict):
        summary = str(graduation.get('summary', '')).strip()
        if summary:
            parts.append(f'Fechamento: {summary}')
    if parts:
        parts.append(
            'Em ordem pratica, primeiro entra a admissao, depois a rotina academica e, por fim, o fechamento com os marcos finais.'
        )
    answer = '\n'.join(parts).strip() if parts else ''
    if answer and len(parts) >= 4:
        return answer
    return compose_public_canonical_lane_answer('public_bundle.year_three_phases', profile=profile)


def _compose_public_school_year_start_answer(
    profile: dict[str, Any], school_reference: str
) -> str | None:
    del school_reference
    entries = profile.get('public_timeline')
    if not isinstance(entries, list):
        return None
    for item in entries:
        if not isinstance(item, dict):
            continue
        if 'school_year_start' not in str(item.get('topic_key', '')):
            continue
        summary = str(item.get('summary', '')).strip()
        notes = str(item.get('notes', '')).strip()
        if summary and notes:
            return f'{summary} {notes}'.strip()
        if summary:
            return summary
    return None
