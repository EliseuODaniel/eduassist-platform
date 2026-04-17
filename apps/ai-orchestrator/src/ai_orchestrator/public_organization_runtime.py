from __future__ import annotations

from typing import Any

from .runtime_core_constants import PUBLIC_LEADERSHIP_TERMS


def _message_matches_term(message: str, term: str) -> bool:
    from .conversation_focus_runtime import _message_matches_term as _impl

    return _impl(message, term)


def _normalize_text(message: str | None) -> str:
    from .conversation_focus_runtime import _normalize_text as _impl

    return _impl(message)


def _extract_salient_terms(message: str) -> set[str]:
    from .intent_analysis_runtime import _extract_salient_terms as _impl

    return _impl(message)


def _requested_public_attribute(message: str) -> str | None:
    from .public_profile_runtime import _requested_public_attribute as _impl

    return _impl(message)


def _extract_teacher_subject(message: str) -> str | None:
    from .public_contact_runtime import _extract_teacher_subject as _impl

    return _impl(message)


def _leadership_inventory(profile: dict[str, Any]) -> list[dict[str, Any]]:
    leadership = profile.get('leadership_team')
    return (
        [item for item in leadership if isinstance(item, dict)]
        if isinstance(leadership, list)
        else []
    )


def _public_kpis(profile: dict[str, Any]) -> list[dict[str, Any]]:
    entries = profile.get('public_kpis')
    return [item for item in entries if isinstance(item, dict)] if isinstance(entries, list) else []


def _public_highlights(profile: dict[str, Any]) -> list[dict[str, Any]]:
    entries = profile.get('highlights')
    return [item for item in entries if isinstance(item, dict)] if isinstance(entries, list) else []


def _select_leadership_member(profile: dict[str, Any], message: str) -> dict[str, Any] | None:
    normalized = _normalize_text(message)
    members = _leadership_inventory(profile)
    if not members:
        return None
    for member in members:
        title = _normalize_text(str(member.get('title', '')))
        name = _normalize_text(str(member.get('name', '')))
        if any(
            phrase in normalized
            for phrase in (
                title,
                name,
                'diretora',
                'diretor',
                'coordenador',
                'coordenadora',
                'direcao',
                'direção',
            )
        ):
            return member
    return members[0]


def _is_leadership_specific_query(message: str) -> bool:
    normalized = _normalize_text(message)
    if not any(_message_matches_term(normalized, term) for term in PUBLIC_LEADERSHIP_TERMS):
        return False
    return _requested_public_attribute(message) is not None


def _compose_public_teacher_directory_answer(
    profile: dict[str, Any],
    message: str,
) -> str:
    school_name = str(profile.get('school_name', 'Colegio Horizonte'))
    subject = _extract_teacher_subject(message)
    if subject:
        return (
            f'O {school_name} nao divulga nomes nem contatos diretos de professores por disciplina, como {subject}. '
            'Se quiser, eu posso te indicar a coordenacao pedagogica ou o setor certo para seguir com isso.'
        )
    return (
        f'O {school_name} nao divulga nomes nem contatos diretos de professores individualmente. '
        'Se quiser, eu posso te indicar a coordenacao pedagogica ou o setor certo.'
    )


def _compose_public_leadership_answer(
    profile: dict[str, Any],
    message: str,
    *,
    requested_attribute_override: str | None = None,
) -> str:
    school_name = str(profile.get('school_name', 'Colegio Horizonte'))
    member = _select_leadership_member(profile, message)
    if member is None:
        return (
            f'Hoje o perfil publico do {school_name} nao traz a lideranca institucional detalhada.'
        )

    requested_attribute = requested_attribute_override or _requested_public_attribute(message)
    title = str(member.get('title', 'Lideranca institucional')).strip()
    name = str(member.get('name', school_name)).strip()
    focus = str(member.get('focus', '')).strip()
    contact_channel = str(member.get('contact_channel', '')).strip()
    notes = str(member.get('notes', '')).strip()
    role_reference = f'a {title.lower()}'
    if (
        'diretor' in _normalize_text(message)
        or 'diretora' in _normalize_text(message)
        or 'direcao' in _normalize_text(message)
    ):
        role_reference = 'a direcao geral'

    if requested_attribute == 'name':
        return f'{title}: {name}.'
    if requested_attribute == 'age':
        response = (
            f'{role_reference.capitalize()} da escola hoje e {name}, '
            'mas a escola nao publica a idade dela.'
        )
        if contact_channel:
            response += f' Se voce precisar falar com esse setor, o canal institucional e {contact_channel}.'
        return response
    if requested_attribute == 'whatsapp':
        if contact_channel and '@' not in contact_channel:
            return f'O canal publicado para {role_reference} e {contact_channel}.'
        response = f'A escola nao publica um WhatsApp direto para {role_reference}.'
        if contact_channel:
            response += (
                f' O contato institucional divulgado para esse atendimento e {contact_channel}.'
            )
        return response
    if requested_attribute == 'phone':
        response = f'A escola nao publica um telefone direto para {role_reference}.'
        if contact_channel:
            response += (
                f' O contato institucional divulgado para esse atendimento e {contact_channel}.'
            )
        return response
    if requested_attribute in {'email', 'contact'}:
        if contact_channel:
            response = (
                f'Voce pode falar com {role_reference} pelo canal institucional {contact_channel}.'
            )
            if notes:
                response += f' {notes}'
            return response
        return (
            f'O perfil publico da escola nao traz um canal direto publicado para {role_reference}.'
        )

    lines = [f'{title}: {name}.']
    if focus:
        lines.append(focus)
    if contact_channel:
        lines.append(f'Canal institucional: {contact_channel}.')
    if notes:
        lines.append(notes)
    return ' '.join(line for line in lines if line)


def _select_public_kpis(profile: dict[str, Any], message: str) -> list[dict[str, Any]]:
    normalized = _normalize_text(message)
    entries = _public_kpis(profile)
    if not entries:
        return []
    selected = [
        item
        for item in entries
        if any(
            marker in normalized
            for marker in (
                _normalize_text(str(item.get('label', ''))),
                _normalize_text(str(item.get('metric_key', ''))),
            )
        )
    ]
    return selected or entries[:3]


def _select_public_highlight(profile: dict[str, Any], message: str) -> dict[str, Any] | None:
    normalized = _normalize_text(message)
    entries = _public_highlights(profile)
    if not entries:
        return None
    for item in entries:
        haystack = ' '.join(
            [
                _normalize_text(str(item.get('title', ''))),
                _normalize_text(str(item.get('description', ''))),
                _normalize_text(str(item.get('highlight_key', ''))),
            ]
        )
        if any(token in haystack for token in _extract_salient_terms(message)):
            return item
    if any(
        _message_matches_term(normalized, term)
        for term in {'curiosidade', 'curiosidades', 'unica', 'única', 'diferencial', 'diferenciais'}
    ):
        for item in entries:
            if str(item.get('highlight_key')) == 'maker_integrado':
                return item
    return entries[0]


def _handle_public_teacher_directory(context: Any) -> str:
    return _compose_public_teacher_directory_answer(context.profile, context.source_message)


def _handle_public_leadership(context: Any) -> str:
    return _compose_public_leadership_answer(
        context.profile,
        context.source_message,
        requested_attribute_override=context.requested_attribute_override,
    )


def _handle_public_kpi(context: Any) -> str:
    entries = _select_public_kpis(context.profile, context.source_message)
    if not entries:
        return f'Hoje o perfil publico de {context.school_reference} nao traz indicadores institucionais publicados.'
    if len(entries) == 1:
        item = entries[0]
        notes = str(item.get('notes', '')).strip()
        return (
            f'Hoje, {item.get("label", "o indicador institucional")} esta em {item.get("value", "--")}{item.get("unit", "")} '
            f'({item.get("reference_period", "periodo nao informado")}). {notes}'.strip()
        )
    lines = [f'Os indicadores publicos mais recentes de {context.school_reference} sao:']
    for item in entries:
        lines.append(
            f'- {item.get("label", "Indicador")}: {item.get("value", "--")}{item.get("unit", "")} '
            f'({item.get("reference_period", "periodo nao informado")})'
        )
    return '\n'.join(lines)


def _handle_public_highlight(context: Any) -> str:
    if any(
        _message_matches_term(context.normalized, term)
        for term in {
            '30 segundos',
            '30s',
            'familia nova',
            'família nova',
            'por que escolher',
            'por que deveria',
        }
    ):
        highlights = _public_highlights(context.profile)
        top_titles = [
            str(item.get('title', '')).strip()
            for item in highlights
            if str(item.get('title', '')).strip()
        ]
        items = (
            ', '.join(top_titles[:3])
            if top_titles
            else 'acompanhamento tutorial, projeto de vida e trilhas academicas'
        )
        headline = str(context.profile.get('short_headline', '')).strip()
        education_model = str(context.profile.get('education_model', '')).strip()
        parts = [
            f'Se eu tivesse 30 segundos para resumir {context.school_reference}, eu diria isto:',
            headline
            or f'{context.school_reference_capitalized} combina aprendizagem por projetos, acompanhamento proximo e trilhas academicas no contraturno.',
            f'Os diferenciais publicados com mais clareza hoje passam por {items}.',
        ]
        if education_model:
            parts.append(f'A proposta pedagogica publicada combina {education_model}.')
        parts.append(
            'Na pratica, isso aparece em aprendizagem por projetos, acompanhamento mais proximo, estudo orientado e contraturno com referencias claras para familias.'
        )
        return ' '.join(part for part in parts if part).strip()
    item = _select_public_highlight(context.profile, context.source_message)
    if item is None:
        return f'Hoje o perfil publico de {context.school_reference} nao traz diferenciais institucionais consolidados.'
    evidence_line = str(item.get('evidence_line', '')).strip()
    intro = 'Um dos diferenciais documentados desta escola'
    if any(
        _message_matches_term(context.normalized, term)
        for term in {'curiosidade', 'curiosidades', 'unica', 'única'}
    ):
        intro = 'Uma curiosidade documentada desta escola'
    title = str(item.get('title', 'Diferencial institucional')).strip()
    description = str(item.get('description', '')).strip()
    lines = [f'{intro} e {title}. {description}'.strip()]
    if evidence_line:
        lines.append(f'Isso aparece de forma bem clara na proposta institucional: {evidence_line}')
    return ' '.join(line for line in lines if line)
