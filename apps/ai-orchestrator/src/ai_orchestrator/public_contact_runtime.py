from __future__ import annotations

import re
from typing import Any


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


def _requested_public_attribute(message: str) -> str | None:
    from .public_profile_runtime import _requested_public_attribute as _impl

    return _impl(message)


def _contact_value(profile: dict[str, Any], channel: str) -> list[str]:
    contacts = profile.get('contact_channels')
    if not isinstance(contacts, list):
        return []
    values: list[str] = []
    for item in contacts:
        if not isinstance(item, dict):
            continue
        if str(item.get('channel', '')).lower() != channel:
            continue
        label = str(item.get('label', '')).strip()
        value = str(item.get('value', '')).strip()
        if not value:
            continue
        values.append(f'{label}: {value}' if label else value)
    return values


def _contact_entries(profile: dict[str, Any], channel: str) -> list[dict[str, str]]:
    contacts = profile.get('contact_channels')
    if not isinstance(contacts, list):
        return []
    entries: list[dict[str, str]] = []
    for item in contacts:
        if not isinstance(item, dict):
            continue
        if str(item.get('channel', '')).lower() != channel:
            continue
        label = str(item.get('label', '')).strip()
        value = str(item.get('value', '')).strip()
        if not value:
            continue
        entries.append({'label': label, 'value': value})
    return entries


def _requested_contact_channel(message: str) -> str | None:
    normalized = _normalize_text(message)
    if any(_message_matches_term(normalized, term) for term in {'whatsapp', 'whats', 'zap'}):
        return 'whatsapp'
    if any(_message_matches_term(normalized, term) for term in {'email', 'e-mail', 'mail'}):
        return 'email'
    if any(
        _message_matches_term(normalized, term)
        for term in {'telefone', 'fone', 'ligacao', 'ligação', 'ligar', 'ligo', 'fax'}
    ):
        return 'telefone'
    return None


def _count_public_contact_subjects(message: str) -> int:
    normalized = _normalize_text(message)
    subject_term_groups: tuple[set[str], ...] = (
        {'secretaria', 'secretaria escolar'},
        {'financeiro', 'mensalidade', 'boleto', 'boletos'},
        {'direcao', 'direção', 'diretoria', 'diretor', 'diretora'},
        {'coordenacao', 'coordenação', 'coordenador', 'coordenadora'},
        {'admissoes', 'admissões', 'matricula', 'matrícula', 'tour', 'visita'},
        {'orientacao educacional', 'orientação educacional', 'socioemocional', 'bullying'},
    )
    count = 0
    for terms in subject_term_groups:
        if any(_message_matches_term(normalized, term) for term in terms):
            count += 1
    return count


def _format_contact_origin(label: str | None, channel: str) -> str:
    cleaned = (label or '').strip().lower()
    if not cleaned:
        return ''
    if channel == 'telefone':
        return f'na {cleaned}'
    return f'pela {cleaned}'


def _wants_contact_list(message: str) -> bool:
    normalized = _normalize_text(message)
    return any(
        _message_matches_term(normalized, term)
        for term in {
            'quais',
            'lista',
            'todos',
            'todas',
            'contatos',
            'canais',
            'telefones',
            'emails',
            'e-mails',
        }
    )


def _contact_is_general_school_query(message: str) -> bool:
    normalized = _normalize_text(message)
    return any(
        _message_matches_term(normalized, term)
        for term in {
            'da escola',
            'pra escola',
            'para a escola',
            'do colegio',
            'do colégio',
            'geral',
            'institucional',
            'principal',
        }
    )


def _select_primary_contact_entry(
    profile: dict[str, Any],
    channel: str,
    message: str,
    *,
    preferred_labels: list[str] | None = None,
) -> dict[str, str] | None:
    entries = _contact_entries(profile, channel)
    if not entries:
        return None

    normalized = _normalize_text(message)
    normalized_preferred = [_normalize_text(label) for label in preferred_labels or [] if label]
    for entry in entries:
        label = _normalize_text(entry.get('label', ''))
        if label and label in normalized:
            return entry

    for preferred_label in normalized_preferred:
        for entry in entries:
            label = _normalize_text(entry.get('label', ''))
            if label == preferred_label:
                return entry

    label_aliases = {
        'direcao': {'direcao', 'direção', 'diretoria', 'diretora', 'diretor'},
        'secretaria': {'secretaria', 'secretaria escolar', 'secretaria digital'},
        'orientacao educacional': {
            'orientacao educacional',
            'orientação educacional',
            'bullying',
            'socioemocional',
        },
        'financeiro': {
            'financeiro',
            'boleto',
            'boletos',
            'mensalidade',
            'fatura',
            'faturas',
            'contrato',
        },
        'admissoes': {'admissoes', 'admissões', 'matricula', 'matrícula', 'visita', 'tour'},
    }
    for entry in entries:
        label = _normalize_text(entry.get('label', ''))
        aliases = label_aliases.get(label, set())
        if aliases and any(_message_matches_term(normalized, alias) for alias in aliases):
            return entry

    if _contact_is_general_school_query(message):
        priorities_by_channel = {
            'telefone': ['secretaria'],
            'email': ['secretaria'],
            'whatsapp': ['secretaria digital', 'atendimento comercial'],
        }
        for preferred_label in priorities_by_channel.get(channel, []):
            for entry in entries:
                if _normalize_text(entry.get('label', '')) == preferred_label:
                    return entry

    return entries[0]


def _is_public_teacher_identity_query(message: str) -> bool:
    normalized = _normalize_text(message)
    if not any(
        _message_matches_term(normalized, term)
        for term in {'prof', 'professor', 'professora', 'docente'}
    ):
        return False
    if _requested_public_attribute(message) in {'name', 'whatsapp', 'email', 'phone', 'contact'}:
        return True
    if (
        any(_message_matches_term(normalized, term) for term in {'nome', 'contato', 'canal'})
        and any(
            _message_matches_term(normalized, term)
            for term in {'publico', 'público', 'coordenacao', 'coordenação'}
        )
    ):
        return True
    return any(
        _message_matches_term(normalized, term)
        for term in {
            'falar com',
            'quero falar com',
            'conversar com',
            'falar direto com',
            'falar diretamente com',
        }
    )


def _is_public_teacher_directory_follow_up(
    message: str,
    conversation_context: dict[str, Any] | None,
) -> bool:
    normalized = _normalize_text(message)
    if not normalized:
        return False
    recent_focus = _recent_trace_focus(conversation_context) or {}
    if isinstance(recent_focus, dict):
        active_task = str(recent_focus.get('active_task', '') or '').strip()
        if active_task == 'public:teacher_directory':
            return any(
                _message_matches_term(normalized, term)
                for term in {
                    'esse contato',
                    'esse canal',
                    'divulga esse contato',
                    'divulga esse canal',
                    'coordenação',
                    'coordenacao',
                    'procurar a coordenação',
                    'procurar a coordenacao',
                    'manda procurar',
                }
            )
    if not _recent_messages_mention(conversation_context, {'professor', 'professora', 'docente'}):
        return False
    return any(
        _message_matches_term(normalized, term)
        for term in {
            'esse contato',
            'esse canal',
            'divulga esse contato',
            'divulga esse canal',
            'a escola divulga',
            'coordenação',
            'coordenacao',
            'procurar a coordenação',
            'procurar a coordenacao',
            'manda procurar',
        }
    )


def _extract_teacher_subject(message: str) -> str | None:
    normalized = _normalize_text(message)
    patterns = [
        r'prof(?:essor|essora)?\s+de\s+(.+)',
        r'docente\s+de\s+(.+)',
    ]
    for pattern in patterns:
        match = re.search(pattern, normalized)
        if not match:
            continue
        subject = re.split(
            r'\b(?:ou|e|mas|pela?|pelo|se|senao|senão|para)\b|[?!,;.:]',
            match.group(1),
            maxsplit=1,
        )[0].strip(' ?.')
        subject = re.sub(r'\b(?:se nao|senão|senao)\b.*$', '', subject).strip(' ?.')
        if len(subject.split()) > 3:
            subject = ' '.join(subject.split()[:3]).strip(' ?.')
        if subject:
            return subject
    return None
