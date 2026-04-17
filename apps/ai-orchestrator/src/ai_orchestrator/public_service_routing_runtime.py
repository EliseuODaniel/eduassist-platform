from __future__ import annotations

from typing import Any

from .runtime_core_constants import SERVICE_FOLLOW_UP_CONTEXT_TERMS, TEACHER_RECRUITMENT_TERMS


def _extract_recent_assistant_message(recent_messages: list[dict[str, Any]]) -> str | None:
    from .analysis_context_runtime import _extract_recent_assistant_message as _impl

    return _impl(recent_messages)


def _extract_recent_user_message(recent_messages: list[dict[str, Any]]) -> str | None:
    from .analysis_context_runtime import _extract_recent_user_message as _impl

    return _impl(recent_messages)


def _is_greeting_only(message: str) -> bool:
    from .conversation_focus_runtime import _is_greeting_only as _impl

    return _impl(message)


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


def _is_assistant_identity_query(message: str) -> bool:
    from .intent_analysis_runtime import _is_assistant_identity_query as _impl

    return _impl(message)


def _is_capability_query(message: str) -> bool:
    from .intent_analysis_runtime import _is_capability_query as _impl

    return _impl(message)


def _is_follow_up_query(message: str) -> bool:
    from .intent_analysis_runtime import _is_follow_up_query as _impl

    return _impl(message)


def _is_service_routing_query(message: str) -> bool:
    from .intent_analysis_runtime import _is_service_routing_query as _impl

    return _impl(message)


def _service_catalog_index(profile: dict[str, Any]) -> dict[str, dict[str, Any]]:
    entries = profile.get('service_catalog')
    result: dict[str, dict[str, Any]] = {}
    if not isinstance(entries, list):
        return result
    for item in entries:
        if not isinstance(item, dict):
            continue
        key = str(item.get('service_key', '')).strip()
        if key:
            result[key] = item
    return result


def _recent_service_match(
    profile: dict[str, Any],
    conversation_context: dict[str, Any] | None,
) -> dict[str, Any] | None:
    for sender_type, content in reversed(_recent_message_lines(conversation_context)):
        if sender_type not in {'user', 'assistant'}:
            continue
        matches = _service_matches_from_message(profile, content)
        if len(matches) == 1:
            return matches[0]
    return None


def _recent_public_contact_subject(
    profile: dict[str, Any],
    conversation_context: dict[str, Any] | None,
) -> str | None:
    recent_service = _recent_service_match(profile, conversation_context)
    if recent_service is not None:
        title = str(recent_service.get('title', '')).strip()
        if title:
            return title
    for _sender_type, content in reversed(_recent_message_lines(conversation_context)):
        normalized = _normalize_text(content)
        if any(
            _message_matches_term(normalized, term)
            for term in {
                'orientacao educacional',
                'orientação educacional',
                'bullying',
                'socioemocional',
            }
        ):
            return 'Orientacao educacional'
        if any(
            _message_matches_term(normalized, term) for term in {'financeiro', 'boleto', 'boletos'}
        ):
            return 'Financeiro'
        if any(
            _message_matches_term(normalized, term)
            for term in {'diretora', 'diretor', 'direcao', 'direção', 'diretoria'}
        ):
            return 'Direcao'
        if any(_message_matches_term(normalized, term) for term in {'coordenacao', 'coordenação'}):
            return 'Coordenacao'
        if any(
            _message_matches_term(normalized, term)
            for term in {'admissoes', 'admissões', 'matricula', 'matrícula', 'visita', 'tour'}
        ):
            return 'Admissoes'
        if any(_message_matches_term(normalized, term) for term in {'secretaria'}):
            return 'Secretaria'
    return None


def _public_contact_reference_message(
    *,
    profile: dict[str, Any],
    source_message: str,
    analysis_message: str,
    conversation_context: dict[str, Any] | None,
) -> str:
    if not _is_follow_up_query(source_message):
        return source_message
    subject = _recent_public_contact_subject(profile, conversation_context)
    if subject:
        return f'{source_message} sobre {subject}'
    return analysis_message


def _preferred_contact_labels_from_context(
    profile: dict[str, Any],
    source_message: str,
    conversation_context: dict[str, Any] | None,
) -> list[str]:
    normalized = _normalize_text(source_message)
    preferred: list[str] = []

    def add(label: str) -> None:
        cleaned = label.strip()
        if cleaned and cleaned not in preferred:
            preferred.append(cleaned)

    explicit_terms = (
        ('Direcao', {'direcao', 'direção', 'diretoria', 'diretora', 'diretor'}),
        ('Coordenacao', {'coordenacao', 'coordenação', 'coordenador', 'coordenadora'}),
        ('Secretaria', {'secretaria'}),
        (
            'Financeiro',
            {'financeiro', 'boleto', 'boletos', 'mensalidade', 'fatura', 'faturas', 'contrato'},
        ),
        ('Admissoes', {'admissoes', 'admissões', 'matricula', 'matrícula', 'visita', 'tour'}),
        (
            'Orientacao educacional',
            {'orientacao educacional', 'orientação educacional', 'bullying', 'socioemocional'},
        ),
    )
    for label, terms in explicit_terms:
        if any(_message_matches_term(normalized, term) for term in terms):
            add(label)

    recent_service = _recent_service_match(profile, conversation_context)
    if isinstance(recent_service, dict):
        service_key = str(recent_service.get('service_key', '')).strip().lower()
        service_preferences = {
            'orientacao_educacional': 'Orientacao educacional',
            'financeiro_escolar': 'Financeiro',
            'visita_institucional': 'Admissoes',
            'solicitacao_direcao': 'Direcao',
            'secretaria_escolar': 'Secretaria',
        }
        preferred_label = service_preferences.get(service_key)
        if preferred_label:
            add(preferred_label)

    for _sender_type, content in reversed(_recent_message_lines(conversation_context)):
        content_normalized = _normalize_text(content)
        if any(
            _message_matches_term(content_normalized, term)
            for term in {
                'orientacao educacional',
                'orientação educacional',
                'bullying',
                'socioemocional',
            }
        ):
            add('Orientacao educacional')
            break
        if any(
            _message_matches_term(content_normalized, term)
            for term in {'financeiro', 'boleto', 'boletos'}
        ):
            add('Financeiro')
            break
        if any(
            _message_matches_term(content_normalized, term)
            for term in {'diretora', 'diretor', 'direcao', 'direção', 'diretoria'}
        ):
            add('Direcao')
            break
        if any(
            _message_matches_term(content_normalized, term)
            for term in {'coordenacao', 'coordenação'}
        ):
            add('Coordenacao')
            break
        if any(
            _message_matches_term(content_normalized, term)
            for term in {'admissoes', 'admissões', 'matricula', 'matrícula', 'visita', 'tour'}
        ):
            add('Admissoes')
            break
        if any(_message_matches_term(content_normalized, term) for term in {'secretaria'}):
            add('Secretaria')
            break
    return preferred


def _is_generic_service_contact_follow_up(message: str) -> bool:
    normalized = _normalize_text(message)
    return any(
        _message_matches_term(normalized, term)
        for term in {
            'com qual contato eu devo falar',
            'qual contato eu devo usar',
            'qual contato devo usar',
            'qual contato',
            'por qual canal',
            'como falo com',
            'como falar com',
            'quem devo procurar',
            'como entro em contato',
        }
    )


def _service_matches_from_message(profile: dict[str, Any], message: str) -> list[dict[str, Any]]:
    normalized = _normalize_text(message)
    catalog = _service_catalog_index(profile)
    service_keys: list[str] = []
    if any(
        _message_matches_term(normalized, term)
        for term in {
            'matricula',
            'bolsa',
            'desconto',
            'admissao',
            'admissoes',
            'atendimento comercial',
            'comercial',
            'visita',
            'tour',
        }
    ):
        service_keys.extend(['atendimento_admissoes', 'visita_institucional'])
    if any(
        _message_matches_term(normalized, term) for term in {'secretaria', 'secretaria escolar'}
    ):
        service_keys.append('secretaria_escolar')
    if any(
        _message_matches_term(normalized, term)
        for term in {
            'documento',
            'documentos',
            'historico',
            'declaração',
            'declaracao',
            'transferencia',
            'uniforme',
        }
    ):
        service_keys.append('secretaria_escolar')
    if any(
        _message_matches_term(normalized, term)
        for term in {
            'coordenacao',
            'coordenação',
            'rotina',
            'aprendizagem',
            'adaptacao',
            'adaptação',
            'professor',
            'faltas',
            'nota',
            'notas',
            'disciplina',
        }
    ):
        service_keys.append('reuniao_coordenacao')
    if any(
        _message_matches_term(normalized, term)
        for term in {
            'emocional',
            'convivencia',
            'convivência',
            'bullying',
            'orientacao',
            'orientação',
            'socioemocional',
        }
    ):
        service_keys.append('orientacao_educacional')
    if any(
        _message_matches_term(normalized, term)
        for term in {
            'mensalidade',
            'boleto',
            'boletos',
            'financeiro',
            'fatura',
            'faturas',
            'pagamento',
            'contrato',
        }
    ):
        service_keys.append('financeiro_escolar')
    if any(
        _message_matches_term(normalized, term)
        for term in {
            'direcao',
            'direção',
            'diretora',
            'ouvidoria',
            'elogio',
            'reclamacao',
            'reclamação',
            'sugestao',
            'sugestão',
        }
    ):
        service_keys.append('solicitacao_direcao')
    if any(
        _message_matches_term(normalized, term)
        for term in {'portal', 'senha', 'acesso', 'telegram', 'bot', 'sistema'}
    ):
        service_keys.append('suporte_digital')
    if any(_message_matches_term(normalized, term) for term in TEACHER_RECRUITMENT_TERMS):
        service_keys.append('carreiras_docentes')
    unique_keys: list[str] = []
    for key in service_keys:
        if key in catalog and key not in unique_keys:
            unique_keys.append(key)
    return [catalog[key] for key in unique_keys]


def _routing_follow_up_context_message(
    message: str,
    conversation_context: dict[str, Any] | None,
) -> str:
    if not isinstance(conversation_context, dict):
        return message
    recent_messages = conversation_context.get('recent_messages', [])
    if not isinstance(recent_messages, list):
        return message
    last_user_message = _extract_recent_user_message(recent_messages)
    last_assistant_message = _extract_recent_assistant_message(recent_messages)
    if not last_user_message:
        return message
    if _normalize_text(last_user_message) == _normalize_text(message):
        return message
    if (
        _is_greeting_only(last_user_message)
        or _is_service_routing_query(last_user_message)
        or _is_capability_query(last_user_message)
        or _is_assistant_identity_query(last_user_message)
    ):
        return message
    normalized_last_user = _normalize_text(last_user_message)
    if not any(
        _message_matches_term(normalized_last_user, term)
        for term in SERVICE_FOLLOW_UP_CONTEXT_TERMS
    ):
        return message
    normalized_last_assistant = _normalize_text(last_assistant_message or '')
    if normalized_last_assistant and not any(
        marker in normalized_last_assistant
        for marker in (
            'autenticacao',
            'vinculo',
            'protocolo',
            'ticket operacional',
            'fila',
            'prazo',
            'setor',
            'canal recomendado',
        )
    ):
        return message
    return f'{message} sobre {last_user_message}'
