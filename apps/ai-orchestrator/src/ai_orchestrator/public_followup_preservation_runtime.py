from __future__ import annotations

from typing import Any

from .conversation_focus_runtime import _normalize_text


def _intent_analysis_impl(name: str):
    from . import intent_analysis_runtime as _intent_analysis_runtime

    return getattr(_intent_analysis_runtime, name)


def _is_explicit_public_pricing_projection_query(
    message: str,
    *,
    conversation_context: dict[str, Any] | None = None,
) -> bool:
    return _intent_analysis_impl('_is_explicit_public_pricing_projection_query')(
        message,
        conversation_context=conversation_context,
    )


def _message_matches_term(message: str, term: str) -> bool:
    return _intent_analysis_impl('_message_matches_term')(message, term)

_ACTION_READY_CANONICAL_PUBLIC_LANES = {
    'public_bundle.academic_policy_overview',
    'public_bundle.governance_protocol',
    'public_bundle.facilities_study_support',
    'public_bundle.secretaria_portal_credentials',
    'public_bundle.first_month_risks',
    'public_bundle.family_new_calendar_assessment_enrollment',
    'public_bundle.timeline_lifecycle',
    'public_bundle.bolsas_and_processes',
    'public_bundle.transport_uniform_bundle',
    'public_bundle.outings_authorizations',
    'public_bundle.permanence_family_support',
    'public_bundle.health_emergency_bundle',
}


def _is_public_year_three_phase_query(message: str) -> bool:
    from .public_profile_runtime import _is_public_year_three_phase_query as _impl

    return _impl(message)


def _is_public_timeline_lifecycle_query(message: str) -> bool:
    from .public_profile_runtime import _is_public_timeline_lifecycle_query as _impl

    return _impl(message)


def _recent_messages_mention(
    conversation_context: dict[str, Any] | None,
    phrases: set[str],
) -> bool:
    from .public_profile_runtime import _recent_messages_mention as _impl

    return _impl(conversation_context, phrases)


def _should_prefer_raw_public_followup_message(
    *,
    request_message: str,
    analysis_message: str,
    conversation_context: dict[str, Any] | None,
) -> bool:
    if str(request_message or '').strip() == str(analysis_message or '').strip():
        return False
    normalized = _normalize_text(request_message)
    if _is_public_year_three_phase_query(request_message):
        return True
    if _is_public_timeline_lifecycle_query(request_message):
        return True
    if any(
        _message_matches_term(normalized, term)
        for term in {
            'so esse recorte',
            'só esse recorte',
            'nao quero o calendario inteiro',
            'não quero o calendário inteiro',
            'recorte em ordem',
            'antes ou depois',
        }
    ):
        return True
    if any(
        term in normalized for term in {'contatos', 'contato', 'financeiro', 'junto com isso'}
    ) and _recent_messages_mention(
        conversation_context,
        {
            'portal',
            'credenciais',
            'documentos',
            'documentacao',
            'documentação',
            'secretaria',
            'matricula',
            'matrícula',
        },
    ):
        return True
    if any(
        _message_matches_term(normalized, term)
        for term in {'sobre cada um', 'sobre cada aluno', 'o que eu consigo ver sobre cada um'}
    ):
        return True
    return False


def _must_preserve_contextual_public_followup_message(
    *,
    request_message: str,
    conversation_context: dict[str, Any] | None,
) -> bool:
    normalized = _normalize_text(request_message)
    if _is_public_year_three_phase_query(request_message):
        return True
    if _is_public_timeline_lifecycle_query(request_message):
        return True
    if any(
        _message_matches_term(normalized, term)
        for term in {
            'so esse recorte',
            'só esse recorte',
            'nao quero o calendario inteiro',
            'não quero o calendário inteiro',
            'recorte em ordem',
            'antes ou depois',
        }
    ):
        return True
    if any(
        _message_matches_term(normalized, term)
        for term in {'sobre cada um', 'sobre cada aluno', 'o que eu consigo ver sobre cada um'}
    ):
        return True
    if any(
        term in normalized for term in {'contatos', 'contato', 'financeiro', 'junto com isso'}
    ) and _recent_messages_mention(
        conversation_context,
        {
            'portal',
            'credenciais',
            'documentos',
            'documentacao',
            'documentação',
            'secretaria',
            'matricula',
            'matrícula',
        },
    ):
        return True
    return False


def _contextualize_public_followup_message(
    *,
    request_message: str,
    analysis_message: str,
    conversation_context: dict[str, Any] | None,
) -> str:
    base_message = (
        analysis_message
        if str(analysis_message or '').strip() != str(request_message or '').strip()
        else request_message
    )
    normalized = _normalize_text(request_message)
    if _is_public_year_three_phase_query(request_message):
        return request_message
    if _recent_messages_mention(
        conversation_context,
        {'matricula', 'matrícula', 'aulas', 'reuniao', 'reunião', 'responsaveis', 'responsáveis'},
    ) and any(
        _message_matches_term(normalized, term)
        for term in {
            'antes ou depois',
            'primeira reuniao',
            'primeira reunião',
            'so esse recorte',
            'só esse recorte',
            'nao quero o calendario inteiro',
            'não quero o calendário inteiro',
            'recorte em ordem',
            'dividir o ano',
            'admissao',
            'admissão',
            'rotina academica',
            'rotina acadêmica',
            'fechamento',
        }
    ):
        return (
            f'{request_message} sobre matricula, inicio das aulas e reuniao com responsaveis '
            'na linha do tempo publica da escola'
        ).strip()
    if _recent_messages_mention(
        conversation_context,
        {
            'portal',
            'credenciais',
            'documentos',
            'documentacao',
            'documentação',
            'secretaria',
            'matricula',
            'matrícula',
        },
    ) and any(
        term in normalized for term in {'contatos', 'contato', 'financeiro', 'junto com isso'}
    ):
        return (
            f'{request_message} sobre secretaria, financeiro, portal, credenciais e envio de documentos '
            'no fluxo publico para familias novas'
        ).strip()
    if _should_prefer_raw_public_followup_message(
        request_message=request_message,
        analysis_message=analysis_message,
        conversation_context=conversation_context,
    ):
        return request_message
    return base_message


def _non_agentic_public_composition_acts() -> tuple[str, ...]:
    from .public_profile_runtime import NON_AGENTIC_PUBLIC_COMPOSITION_ACTS

    return NON_AGENTIC_PUBLIC_COMPOSITION_ACTS


def _should_preserve_deterministic_public_answer(
    *,
    resolved_act: str,
    request_message: str,
    original_message: str | None,
    conversation_context: dict[str, Any] | None,
    deterministic_text: str,
    canonical_lane: str | None,
) -> bool:
    if resolved_act in _non_agentic_public_composition_acts():
        return True
    if _is_explicit_public_pricing_projection_query(
        original_message or request_message,
        conversation_context=conversation_context,
    ):
        return True
    normalized_message = _normalize_text(original_message or request_message)
    normalized_deterministic = _normalize_text(deterministic_text)
    if (
        '/start link_<codigo>' in deterministic_text
        or '/start link_<código>' in deterministic_text
        or 'portal autenticado' in normalized_deterministic
    ):
        return True
    if canonical_lane not in _ACTION_READY_CANONICAL_PUBLIC_LANES:
        return False
    if any(
        _message_matches_term(normalized_message, term)
        for term in {
            'como',
            'de que forma',
            'na pratica',
            'na prática',
            'passo a passo',
            'conectados',
            'conectado',
            'protocolo',
            'fluxo',
            'suporte',
            'apoio',
            'encaminhamento',
        }
    ):
        return True
    return any(
        hint in normalized_deterministic
        for hint in {
            'na pratica',
            'proximo passo',
            'protocolo formal',
            'passo a passo',
            'primeiro',
            'depois',
            'por fim',
        }
    )
