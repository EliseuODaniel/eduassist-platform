from __future__ import annotations

from typing import Any


def _public_highlights(profile: dict[str, Any]) -> list[dict[str, Any]]:
    from .public_organization_runtime import _public_highlights as _impl

    return _impl(profile)


def _contact_entries(profile: dict[str, Any], channel: str) -> list[dict[str, str]]:
    from .public_contact_runtime import _contact_entries as _impl

    return _impl(profile, channel)


def _service_catalog_index(profile: dict[str, Any]) -> dict[str, dict[str, Any]]:
    from .public_service_routing_runtime import _service_catalog_index as _impl

    return _impl(profile)


def _humanize_service_eta(eta: str) -> str:
    from .public_profile_runtime import _humanize_service_eta as _impl

    return _impl(eta)


def _school_object_reference(school_reference: str) -> str:
    from .public_profile_runtime import _school_object_reference as _impl

    return _impl(school_reference)


def _compose_public_comparative_answer(profile: dict[str, Any]) -> str:
    highlights = _public_highlights(profile)
    highlight_titles = [
        str(item.get('title', '')).strip()
        for item in highlights
        if str(item.get('title', '')).strip()
    ]
    education_model = str(profile.get('education_model', '')).strip()
    headline = str(profile.get('short_headline', '')).strip()
    labels_preview = (
        ', '.join(highlight_titles[:3])
        if highlight_titles
        else 'os diferenciais publicados da escola'
    )
    parts = [
        'Estudar em uma escola publica pode ser uma boa escolha para muitas familias, e eu nao vou te vender uma comparacao vazia.',
        f'No que esta publicado aqui, os diferenciais desta escola passam por {labels_preview}.',
    ]
    if education_model:
        parts.append(f'A proposta pedagogica publicada hoje combina {education_model}.')
    parts.append(
        'Na pratica, isso aparece em acompanhamento mais proximo da aprendizagem, projeto de vida e combinados pedagogicos mais claros.'
    )
    if headline:
        parts.append(headline)
    parts.append(
        'Se quiser, eu posso te mostrar isso de forma mais pratica na rotina, na proposta pedagogica ou no contraturno.'
    )
    return ' '.join(part for part in parts if part).strip()


def _compose_public_comparative_practical_answer(profile: dict[str, Any]) -> str:
    education_model = str(profile.get('education_model', '')).strip()
    highlights = _public_highlights(profile)
    highlight_titles = [
        str(item.get('title', '')).strip()
        for item in highlights
        if str(item.get('title', '')).strip()
    ]
    items = (
        ', '.join(highlight_titles[:3])
        if highlight_titles
        else 'tutoria academica, projeto de vida e acompanhamento proximo'
    )
    parts = [
        'Na pratica, isso muda em uma rotina com aprendizagem por projetos, acompanhamento mais proximo e referencias claras de tutoria academica.',
        f'Os pontos que aparecem hoje de forma mais concreta sao {items}.',
        'Isso aparece no dia a dia em projeto de vida, acompanhamento mais proximo e referencias mais visiveis para familias e estudantes.',
    ]
    if education_model:
        parts.append(f'Isso conversa com uma proposta pedagogica que combina {education_model}.')
    return ' '.join(part for part in parts if part).strip()


def _handle_public_web_presence(context: Any) -> str:
    requested_attribute = str(context.requested_attribute_override or '').strip().lower()
    normalized_message = context.normalized
    if requested_attribute == 'news' or any(
        term in normalized_message
        for term in {
            'ultima noticia',
            'última notícia',
            'noticias da escola',
            'notícias da escola',
        }
    ):
        if context.website_url:
            return (
                f'Hoje eu nao tenho um feed publico de noticias recentes validado aqui para {context.school_reference}. '
                f'O melhor canal oficial para acompanhar novidades e {context.website_url}. '
                'Se quiser, eu tambem posso te passar os canais institucionais de atendimento.'
            )
        return (
            f'Hoje eu nao tenho um feed publico de noticias recentes validado aqui para {context.school_reference}. '
            'Se quiser, eu posso te passar os canais institucionais oficiais para acompanhar atualizacoes.'
        )
    if context.website_url:
        return f'O site oficial {_school_object_reference(context.school_reference)} hoje e {context.website_url}.'
    return (
        f'Hoje eu nao tenho um site oficial publicado no perfil canonico de {context.school_reference}. '
        'Se quiser, eu posso te passar o telefone ou o email da secretaria.'
    )


def _handle_public_social_presence(context: Any) -> str:
    instagram_entries = _contact_entries(context.profile, 'instagram')
    if instagram_entries:
        primary_entry = instagram_entries[0]
        value = str(primary_entry.get('value', '')).strip()
        label = str(primary_entry.get('label', '')).strip()
        if value:
            prefix = f'O {label.lower()} ' if label else 'O Instagram institucional '
            return (
                f'{prefix}{_school_object_reference(context.school_reference)} hoje e {value}. '
                'Se quiser, eu tambem posso te passar o site oficial ou os canais de atendimento.'
            )
    return (
        f'Hoje eu nao tenho um Instagram oficial publicado no perfil canonico de {context.school_reference}. '
        'Se quiser, eu posso te passar o site oficial ou os canais institucionais de contato.'
    )


def _handle_public_comparative(context: Any) -> str:
    return _compose_public_comparative_answer(context.profile)


def _handle_public_careers(context: Any) -> str:
    catalog = _service_catalog_index(context.profile)
    careers_entry = catalog.get('carreiras_docentes')
    if careers_entry is None:
        return (
            f'Hoje eu nao tenho um fluxo publico de recrutamento docente estruturado no perfil canonico de {context.school_reference}. '
            'Se quiser, eu posso te passar os canais institucionais da escola.'
        )
    request_channel = str(careers_entry.get('request_channel', 'canal institucional')).strip()
    typical_eta = _humanize_service_eta(
        str(careers_entry.get('typical_eta', 'prazo nao informado'))
    )
    notes = str(careers_entry.get('notes', '')).strip()
    response = (
        f'Se voce quer se candidatar para dar aula em {context.school_reference}, o caminho mais direto hoje e {request_channel}. '
        f'O prazo tipico e {typical_eta}.'
    )
    if notes:
        response += f' {notes}'
    return response
