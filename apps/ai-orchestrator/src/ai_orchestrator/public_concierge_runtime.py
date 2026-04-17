from __future__ import annotations

from typing import Any

from .analysis_context_runtime import _extract_recent_assistant_message
from .conversation_focus_runtime import _assistant_already_introduced, _normalize_text, _recent_focus_follow_up_line
from .intent_analysis_runtime import _is_assistant_identity_query, _message_matches_term
from .public_contact_runtime import _contact_entries
from .public_organization_runtime import _public_highlights, _select_leadership_member
from .public_service_routing_runtime import (
    _is_generic_service_contact_follow_up,
    _recent_service_match,
    _routing_follow_up_context_message,
    _service_catalog_index,
    _service_matches_from_message,
)


def _compose_concierge_topic_examples(profile: dict[str, Any], limit: int = 5) -> str:
    from .public_profile_runtime import _compose_concierge_topic_examples as _impl

    return _impl(profile, limit=limit)


def _humanize_service_eta(eta: str) -> str:
    from .public_profile_runtime import _humanize_service_eta as _impl

    return _impl(eta)


def _compose_assistant_identity_answer(
    profile: dict[str, Any],
    *,
    conversation_context: dict[str, Any] | None = None,
) -> str:
    from .public_profile_runtime import _compose_assistant_identity_answer as _impl

    return _impl(profile, conversation_context=conversation_context)


def _feature_inventory_map(profile: dict[str, Any]) -> dict[str, dict[str, Any]]:
    from .public_feature_runtime import _feature_inventory_map as _impl

    return _impl(profile)


def _requested_public_features(message: str) -> list[str]:
    from .public_feature_runtime import _requested_public_features as _impl

    return _impl(message)


def _recent_public_feature_key(conversation_context: dict[str, Any] | None) -> str | None:
    from .public_feature_runtime import _recent_public_feature_key as _impl

    return _impl(conversation_context)


def _compose_public_feature_schedule_follow_up(
    *,
    profile: dict[str, Any],
    original_message: str,
    analysis_message: str,
    conversation_context: dict[str, Any] | None,
) -> str | None:
    from .public_profile_runtime import _compose_public_feature_schedule_follow_up as _impl

    return _impl(
        profile=profile,
        original_message=original_message,
        analysis_message=analysis_message,
        conversation_context=conversation_context,
    )


def _compose_public_feature_answer(
    *,
    profile: dict[str, Any],
    original_message: str,
    analysis_message: str,
    conversation_context: dict[str, Any] | None,
) -> str | None:
    from .public_profile_runtime import _compose_public_feature_answer as _impl

    return _impl(
        profile=profile,
        original_message=original_message,
        analysis_message=analysis_message,
        conversation_context=conversation_context,
    )


def _is_public_enrichment_query(message: str) -> bool:
    from .public_commercial_runtime import _is_public_enrichment_query as _impl

    return _impl(message)


def _compose_public_enrichment_answer(context: Any) -> str:
    from .public_commercial_runtime import _compose_public_enrichment_answer as _impl

    return _impl(context)


def _is_follow_up_query(message: str) -> bool:
    from .intent_analysis_runtime import _is_follow_up_query as _impl

    return _impl(message)


def _requested_operating_hours_attribute(
    message: str,
    conversation_context: dict[str, Any] | None = None,
) -> str | None:
    from .intent_analysis_runtime import _requested_operating_hours_attribute as _impl

    return _impl(message, conversation_context)


def _school_subject_reference(reference: str) -> str:
    from .public_profile_runtime import _school_subject_reference as _impl

    return _impl(reference)


def _school_object_reference(reference: str) -> str:
    from .public_profile_runtime import _school_object_reference as _impl

    return _impl(reference)


def _compose_public_pedagogical_answer(profile: dict[str, Any], message: str) -> str | None:
    from .public_profile_runtime import PUBLIC_PEDAGOGICAL_TERMS

    normalized = _normalize_text(message)
    education_model = str(profile.get('education_model', '')).strip()
    curriculum_basis = str(profile.get('curriculum_basis', '')).strip()
    highlights = _public_highlights(profile)
    highlight_titles = [
        str(item.get('title', '')).strip()
        for item in highlights
        if str(item.get('title', '')).strip()
    ]
    overview = str(profile.get('short_headline', '')).strip()
    if any(
        _message_matches_term(normalized, phrase)
        for phrase in {
            'proposta pedagogica',
            'proposta pedagógica',
            'projeto pedagogico',
            'projeto pedagógico',
        }
    ):
        parts: list[str] = []
        if education_model:
            parts.append(f'A proposta pedagogica publicada hoje combina {education_model}.')
        if curriculum_basis:
            parts.append(f'No Ensino Medio, isso aparece junto de {curriculum_basis}.')
        if highlight_titles:
            parts.append(
                'Na pratica, isso aparece em frentes como {items}.'.format(
                    items=', '.join(highlight_titles[:3])
                )
            )
        parts.append(
            'Isso se traduz em acompanhamento mais proximo da aprendizagem e em uma proposta pedagogica explicita no dia a dia.'
        )
        return ' '.join(part for part in parts if part).strip() or None
    if _message_matches_term(normalized, 'acolhimento') and any(
        _message_matches_term(normalized, term)
        for term in {
            'disciplina',
            'disciplinas',
            'convivencia',
            'convivência',
            'aprendizagem',
            'rotina',
        }
    ):
        parts = [
            'Pelo que a escola publica hoje, esse equilibrio aparece em uma rotina com acompanhamento proximo e acolhimento estruturado.'
        ]
        if overview:
            parts.append(overview)
        parts.append(
            'Na pratica, isso aparece em orientacao educacional, coordenacao, tutoria academica e projeto de vida, junto de uma jornada de acolhimento para familias e estudantes antes e depois da matricula.'
        )
        return ' '.join(part for part in parts if part).strip()
    if any(_message_matches_term(normalized, term) for term in PUBLIC_PEDAGOGICAL_TERMS):
        parts = []
        if education_model:
            parts.append(f'A proposta pedagogica publicada hoje combina {education_model}.')
        if highlight_titles:
            parts.append(
                'Os diferenciais pedagogicos mais claros aqui passam por {items}.'.format(
                    items=', '.join(highlight_titles[:3])
                )
            )
        return ' '.join(part for part in parts if part).strip() or None
    return None


def _compose_concierge_greeting(
    profile: dict[str, Any],
    message: str,
    conversation_context: dict[str, Any] | None,
) -> str:
    school_name = str(profile.get('school_name', 'Colegio Horizonte'))
    opening = 'Oi.'
    normalized = _normalize_text(message)
    if 'bom dia' in normalized:
        opening = 'Bom dia.'
    elif 'boa tarde' in normalized:
        opening = 'Boa tarde.'
    elif 'boa noite' in normalized:
        opening = 'Boa noite.'

    active_follow_up = _recent_focus_follow_up_line(conversation_context)
    if active_follow_up:
        if _assistant_already_introduced(conversation_context):
            return f'{opening} {active_follow_up}'
        return f'{opening} Voce esta falando com o EduAssist do {school_name}. {active_follow_up}'

    if _assistant_already_introduced(conversation_context):
        return (
            f'{opening} Sou o EduAssist. Pode seguir do jeito que ficar mais facil. '
            'Se quiser, eu continuo por aqui com o mesmo assunto ou com um tema novo.'
        )

    examples = _compose_concierge_topic_examples(profile, limit=4)
    return (
        f'{opening} Voce esta falando com o EduAssist do {school_name}. '
        f'Posso te ajudar com {examples}. '
        'Se sua conta estiver vinculada, eu tambem consigo consultar notas, faltas e financeiro.'
    )


def _is_acknowledgement_query(message: str) -> bool:
    from .public_profile_runtime import ACKNOWLEDGEMENT_TERMS

    normalized = _normalize_text(message).strip()
    return any(_message_matches_term(normalized, term) for term in ACKNOWLEDGEMENT_TERMS)


def _compose_concierge_acknowledgement(
    *,
    conversation_context: dict[str, Any] | None,
) -> str:
    recent_assistant = _extract_recent_assistant_message(
        conversation_context.get('recent_messages', [])
        if isinstance(conversation_context, dict)
        else []
    )
    recent_normalized = _normalize_text(recent_assistant or '')
    if 'protocolo' in recent_normalized or 'ticket operacional' in recent_normalized:
        return 'Perfeito. Se quiser, eu acompanho o andamento desse atendimento por aqui.'
    if (
        'autenticacao' in recent_normalized
        or 'vinculo' in recent_normalized
        or 'link_' in recent_normalized
    ):
        return 'Combinado. Quando quiser, eu continuo por aqui assim que sua conta estiver vinculada.'
    if 'financeiro' in recent_normalized:
        return 'Combinado. Se quiser, eu sigo com o proximo passo do financeiro ou te direciono para o setor certo.'
    if 'matricula' in recent_normalized or 'visita' in recent_normalized:
        return 'Perfeito. Se quiser, eu continuo daqui e te ajudo com o proximo passo.'
    return 'Por nada. Se quiser, pode seguir com a proxima duvida que eu continuo com voce por aqui.'


def _compose_capability_answer(
    profile: dict[str, Any],
    *,
    conversation_context: dict[str, Any] | None = None,
) -> str:
    public_examples = _compose_concierge_topic_examples(profile, limit=3)
    introduced = _assistant_already_introduced(conversation_context)
    if introduced:
        return (
            f'Por aqui eu consigo te ajudar com {public_examples}. '
            'Tambem consigo seguir com secretaria e documentos quando isso entrar no caminho. '
            'Se sua conta estiver vinculada, eu tambem consulto notas, faltas e financeiro escolar. '
            'Se precisar de uma acao, eu posso abrir visita, protocolo ou te encaminhar para o setor certo.'
        )
    return (
        f'Eu consigo te ajudar com {public_examples}. '
        'Tambem consigo seguir com secretaria e documentos quando isso entrar no caminho. '
        'Se sua conta estiver vinculada, eu tambem posso consultar notas, faltas e o financeiro escolar. '
        'Se fizer sentido, eu ainda abro visita, protocolo ou te direciono para o setor certo.'
    )


def _compose_service_routing_menu(profile: dict[str, Any]) -> str:
    examples = _compose_concierge_topic_examples(profile, limit=6)
    if not examples:
        return 'Hoje eu consigo te encaminhar para matricula, secretaria, coordenacao, orientacao, financeiro ou direcao.'
    if len(examples) <= 3:
        return 'Hoje eu consigo te encaminhar para ' + ', '.join(examples) + '.'
    return 'Hoje eu consigo te encaminhar por aqui para ' + ', '.join(examples[:-1]) + f' e {examples[-1]}.'


def _explicit_service_routing_lines(profile: dict[str, Any], message: str) -> list[str]:
    normalized = _normalize_text(message)
    catalog = _service_catalog_index(profile)
    lines: list[str] = []

    def add(line: str | None) -> None:
        cleaned = str(line or '').strip()
        if cleaned and cleaned not in lines:
            lines.append(cleaned)

    def contact_suffix(*, label_terms: set[str], include_whatsapp: bool = False) -> str:
        channel_order = (
            ('email', 'telefone', 'whatsapp') if include_whatsapp else ('email', 'telefone')
        )
        snippets: list[str] = []
        normalized_terms = {_normalize_text(term) for term in label_terms if term}
        for channel in channel_order:
            for entry in _contact_entries(profile, channel):
                label = _normalize_text(entry.get('label'))
                if normalized_terms and not any(term in label for term in normalized_terms):
                    continue
                value = str(entry.get('value') or '').strip()
                if not value:
                    continue
                if channel == 'email':
                    snippets.append(f'email {value}')
                elif channel == 'telefone':
                    snippets.append(f'telefone {value}')
                elif channel == 'whatsapp':
                    snippets.append(f'WhatsApp {value}')
        if not snippets:
            return ''
        return ' Contatos diretos: ' + ' | '.join(dict.fromkeys(snippets)) + '.'

    if any(
        _message_matches_term(normalized, term)
        for term in {'direcao', 'direção', 'diretora', 'diretor'}
    ):
        member = _select_leadership_member(profile, 'direcao')
        if isinstance(member, dict):
            title = str(member.get('title') or 'Direcao geral').strip()
            name = str(member.get('name') or '').strip()
            contact_channel = str(member.get('contact_channel') or '').strip()
            normalized_title = _normalize_text(title)
            routing_label = (
                'Direcao geral'
                if any(
                    term in normalized_title
                    for term in {'diretor', 'diretora', 'direcao', 'direção'}
                )
                else title
            )
            if name and contact_channel:
                add(
                    f'- {routing_label}: {name}. Canal institucional: {contact_channel}.'
                    f'{contact_suffix(label_terms={"direcao"}, include_whatsapp=False)}'
                )
            elif name:
                add(f'- {routing_label}: {name}.')
        else:
            item = catalog.get('solicitacao_direcao')
            if isinstance(item, dict):
                add(
                    f'- Direcao: {str(item.get("request_channel") or "canal institucional").strip()}.'
                    f'{contact_suffix(label_terms={"direcao"}, include_whatsapp=False)}'
                )

    explicit_service_map = (
        (
            {
                'atendimento comercial',
                'comercial',
                'bolsa',
                'bolsas',
                'setor de bolsas',
                'desconto',
                'matricula',
                'matrícula',
                'admissoes',
                'admissões',
            },
            'atendimento_admissoes',
            'Atendimento comercial / Admissoes',
        ),
        (
            {'boleto', 'boletos', 'financeiro', 'fatura', 'faturas', 'mensalidade', 'mensalidades'},
            'financeiro_escolar',
            'Financeiro',
        ),
        (
            {
                'bullying',
                'orientacao educacional',
                'orientação educacional',
                'socioemocional',
                'convivencia',
                'convivência',
            },
            'orientacao_educacional',
            'Orientacao educacional',
        ),
        (
            {
                'secretaria',
                'documentos',
                'declaração',
                'declaracao',
                'atualizacao cadastral',
                'atualização cadastral',
            },
            'secretaria_escolar',
            'Secretaria',
        ),
    )
    for terms, service_key, label in explicit_service_map:
        if not any(_message_matches_term(normalized, term) for term in terms):
            continue
        item = catalog.get(service_key)
        extra_contacts = ''
        if service_key == 'atendimento_admissoes':
            extra_contacts = contact_suffix(
                label_terms={'admissoes', 'atendimento comercial'}, include_whatsapp=True
            )
        elif service_key == 'financeiro_escolar':
            extra_contacts = contact_suffix(label_terms={'financeiro'}, include_whatsapp=False)
        if isinstance(item, dict):
            add(
                f'- {label}: {str(item.get("request_channel") or "canal institucional").strip()}.{extra_contacts}'
            )
            continue
        if service_key == 'financeiro_escolar':
            add('- Financeiro: bot, portal autenticado ou e-mail institucional.')
            continue
        if service_key == 'atendimento_admissoes':
            add('- Atendimento comercial / Admissoes: bot, WhatsApp comercial, admissions ou visita agendada.')

    return lines


def _compose_service_routing_answer(
    profile: dict[str, Any],
    message: str,
    *,
    conversation_context: dict[str, Any] | None = None,
) -> str:
    message_for_matching = _routing_follow_up_context_message(message, conversation_context)
    explicit_lines = _explicit_service_routing_lines(profile, message_for_matching)
    if explicit_lines:
        return '\n'.join(
            ['Hoje estes sao os responsaveis e canais mais diretos por assunto:', *explicit_lines]
        )
    matches = _service_matches_from_message(profile, message_for_matching)
    recent_match = None
    if not matches and _is_generic_service_contact_follow_up(message):
        recent_match = _recent_service_match(profile, conversation_context)
    if recent_match is not None:
        matches = [recent_match]
    if not matches:
        if _is_assistant_identity_query(message):
            return _compose_assistant_identity_answer(
                profile,
                conversation_context=conversation_context,
            )
        return (
            'Voce fala comigo, o EduAssist. Eu consigo te orientar e te encaminhar para secretaria, matricula e atendimento comercial, '
            f'coordenacao, orientacao educacional, financeiro ou direcao. {_compose_service_routing_menu(profile)} '
            'Se quiser, me diga o assunto em uma frase curta e eu te indico o melhor caminho sem voce precisar adivinhar o setor.'
        )
    if len(matches) == 1:
        item = matches[0]
        eta = _humanize_service_eta(str(item.get('typical_eta', 'prazo nao informado')))
        if _is_generic_service_contact_follow_up(message):
            response = (
                f'Voce pode falar com {item.get("title", "o setor institucional")} '
                f'por {item.get("request_channel", "canal institucional")}.'
            )
            if eta and eta != 'prazo nao informado':
                response += f' O prazo tipico e {eta}.'
            notes = str(item.get('notes', '')).strip()
            if notes:
                response += f' {notes}'
            response += ' Se quiser, eu sigo por aqui com a solicitacao certa.'
            return response
        return (
            f'Para tratar esse assunto, o caminho mais direto e {item.get("title", "o setor institucional")}. '
            f'Voce pode acionar por {item.get("request_channel", "canal institucional")}, e o prazo tipico e {eta}. '
            f'{str(item.get("notes", "")).strip()} '
            'Se preferir, eu mesmo ja posso seguir por aqui com a solicitacao certa.'
        )
    lines = ['Para esse tema, estes caminhos costumam funcionar melhor:']
    for item in matches[:3]:
        lines.append(
            '- {title}: {request_channel}. Prazo tipico: {typical_eta}.'.format(
                title=item.get('title', 'Setor institucional'),
                request_channel=item.get('request_channel', 'canal institucional'),
                typical_eta=item.get('typical_eta', 'nao informado'),
            )
        )
    lines.append('Se quiser, eu tambem posso seguir por aqui e abrir a solicitacao certa.')
    return '\n'.join(lines)


def _handle_public_acknowledgement(context: Any) -> str:
    return _compose_concierge_acknowledgement(conversation_context=context.conversation_context)


def _handle_public_greeting(context: Any) -> str:
    return _compose_concierge_greeting(
        context.profile, context.source_message, context.conversation_context
    )


def _handle_public_service_routing(context: Any) -> str:
    return _compose_service_routing_answer(
        context.profile,
        context.source_message,
        conversation_context=context.conversation_context,
    )


def _handle_public_capabilities(context: Any) -> str:
    return _compose_capability_answer(
        context.profile,
        conversation_context=context.conversation_context,
    )


def _target_public_feature_for_operating_hours(context: Any) -> dict[str, Any] | None:
    feature_map = _feature_inventory_map(context.profile)
    requested_features = _requested_public_features(context.source_message)
    if not requested_features and _is_follow_up_query(context.source_message):
        recent_feature = _recent_public_feature_key(context.conversation_context)
        if recent_feature:
            requested_features = [recent_feature]
    if not requested_features and context.semantic_plan and context.semantic_plan.focus_hint:
        requested_features = _requested_public_features(context.semantic_plan.focus_hint)
    if len(requested_features) != 1:
        return None
    feature_entry = feature_map.get(requested_features[0])
    return (
        feature_entry
        if isinstance(feature_entry, dict) and bool(feature_entry.get('available'))
        else None
    )


def _handle_public_operating_hours(context: Any) -> str:
    requested_attribute = (
        context.requested_attribute_override
        or _requested_operating_hours_attribute(
            context.source_message,
            context.conversation_context,
        )
    )
    requested_attributes = set(context.requested_attributes)
    feature_entry = _target_public_feature_for_operating_hours(context)
    if feature_entry is not None:
        label = str(feature_entry.get('label', 'esse espaco')).strip() or 'esse espaco'
        notes = str(feature_entry.get('notes', '')).strip()
        feature_key = str(feature_entry.get('feature_key', '')).strip().lower()
        feature_reference = 'A biblioteca' if feature_key == 'biblioteca' else f'O espaco {label}'
        if notes:
            normalized_notes = _normalize_text(notes)
            hours_match = re.search(r'das\s+[0-9h:]+\s+as\s+[0-9h:]+', normalized_notes)
            hours_text = hours_match.group(0) if hours_match else None
            if feature_key == 'biblioteca' and hours_text:
                library_open_match = re.search(r'das\s+([0-9h:]+)\s+as\s+([0-9h:]+)', hours_text)
                library_open_time = library_open_match.group(1) if library_open_match else None
                library_close_time = library_open_match.group(2) if library_open_match else None
                if requested_attribute == 'open_time' and library_open_time:
                    return f'A biblioteca abre as {library_open_time}.'
                if requested_attribute == 'close_time' and library_close_time:
                    return f'A biblioteca fecha as {library_close_time}.'
            if 'name' in requested_attributes:
                if feature_key == 'biblioteca' and hours_text:
                    return f'A Biblioteca {label} funciona das 7h30 as 18h00.'
                return f'{feature_reference} se chama {label}. Pelo perfil publico, {notes}'
            if feature_key == 'biblioteca' and hours_text:
                return f'A Biblioteca {label} funciona das 7h30 as 18h00.'
            return f'Pelo perfil publico, {label} funciona assim hoje: {notes}'
    if requested_attribute == 'open_time':
        return (
            f'O atendimento presencial {_school_object_reference(context.school_reference)} abre as 7h00, de segunda a sexta-feira. '
            'Se voce estiver falando da biblioteca, ela abre as 7h30.'
        )
    if requested_attribute == 'close_time':
        return (
            f'O atendimento presencial {_school_object_reference(context.school_reference)} fecha as 17h30, de segunda a sexta-feira. '
            'Se voce estiver falando da biblioteca, ela fecha as 18h00.'
        )
    return (
        f'O atendimento presencial {_school_object_reference(context.school_reference)} abre as 7h00 e segue ate as 17h30, de segunda a sexta-feira. '
        'Se voce estiver falando da biblioteca, ela funciona das 7h30 as 18h00.'
    )


def _handle_public_features(context: Any) -> str:
    if _is_public_enrichment_query(context.source_message):
        return _compose_public_enrichment_answer(context)
    feature_schedule_follow_up = _compose_public_feature_schedule_follow_up(
        profile=context.profile,
        original_message=context.source_message,
        analysis_message=context.message,
        conversation_context=context.conversation_context,
    )
    if feature_schedule_follow_up:
        return feature_schedule_follow_up
    feature_answer = _compose_public_feature_answer(
        profile=context.profile,
        original_message=context.source_message,
        analysis_message=context.message,
        conversation_context=context.conversation_context,
    )
    if feature_answer:
        return feature_answer
    return (
        f'Hoje o perfil publico de {context.school_reference} nao traz esse detalhe de estrutura ou atividade. '
        'Se quiser, eu posso te mostrar o que esta oficialmente documentado.'
    )
