from __future__ import annotations

from datetime import date
from typing import Any, Callable

from .public_profile_routes_runtime import (
    _handle_public_contacts_impl,
    _handle_public_timeline_impl,
)
from .student_scope_runtime import _compose_public_access_scope_answer


def _compose_input_clarification_answer(
    profile: dict[str, Any],
    *,
    conversation_context: dict[str, Any] | None = None,
) -> str:
    from .public_profile_intent_runtime import _compose_input_clarification_answer as _impl

    return _impl(profile, conversation_context=conversation_context)


def _compose_scope_boundary_answer(
    profile: dict[str, Any],
    *,
    conversation_context: dict[str, Any] | None = None,
) -> str:
    from .public_profile_intent_runtime import _compose_scope_boundary_answer as _impl

    return _impl(profile, conversation_context=conversation_context)


def _format_brazilian_date(value: date) -> str:
    from .public_timeline_runtime import _format_brazilian_date as _impl

    return _impl(value)


def _compose_language_preference_answer(
    profile: dict[str, Any],
    message: str,
    *,
    conversation_context: dict[str, Any] | None = None,
) -> str:
    from .public_profile_intent_runtime import _compose_language_preference_answer as _impl

    return _impl(profile, message, conversation_context=conversation_context)


def _compose_assistant_identity_answer(
    profile: dict[str, Any],
    *,
    conversation_context: dict[str, Any] | None = None,
) -> str:
    from .public_profile_runtime import _compose_assistant_identity_answer as _impl

    return _impl(profile, conversation_context=conversation_context)


def _public_visit_offers(profile: dict[str, Any]) -> list[dict[str, Any]]:
    from .public_profile_runtime import _public_visit_offers as _impl

    return _impl(profile)


def _public_service_catalog(profile: dict[str, Any]) -> list[dict[str, Any]]:
    from .public_profile_runtime import _public_service_catalog as _impl

    return _impl(profile)


def _school_subject_reference(reference: str) -> str:
    from .public_profile_runtime import _school_subject_reference as _impl

    return _impl(reference)


def _handle_public_acknowledgement(context: Any) -> str:
    from .public_profile_runtime import _handle_public_acknowledgement as _impl

    return _impl(context)


def _handle_public_greeting(context: Any) -> str:
    from .public_profile_runtime import _handle_public_greeting as _impl

    return _impl(context)


def _handle_public_service_routing(context: Any) -> str:
    from .public_profile_runtime import _handle_public_service_routing as _impl

    return _impl(context)


def _handle_public_capabilities(context: Any) -> str:
    from .public_profile_runtime import _handle_public_capabilities as _impl

    return _impl(context)


def _handle_public_service_credentials_bundle(context: Any) -> str:
    from .public_profile_runtime import _handle_public_service_credentials_bundle as _impl

    return _impl(context)


def _handle_public_document_submission(context: Any) -> str:
    from .public_profile_runtime import _handle_public_document_submission as _impl

    return _impl(context)


def _handle_public_policy(context: Any) -> str:
    from .public_profile_runtime import _handle_public_policy as _impl

    return _impl(context)


def _handle_public_policy_compare(context: Any) -> str:
    from .public_profile_runtime import _handle_public_policy_compare as _impl

    return _impl(context)


def _handle_public_capacity(context: Any) -> str:
    from .public_profile_runtime import _handle_public_capacity as _impl

    return _impl(context)


def _handle_public_careers(context: Any) -> str:
    from .public_profile_runtime import _handle_public_careers as _impl

    return _impl(context)


def _handle_public_teacher_directory(context: Any) -> str:
    from .public_profile_runtime import _handle_public_teacher_directory as _impl

    return _impl(context)


def _handle_public_leadership(context: Any) -> str:
    from .public_profile_runtime import _handle_public_leadership as _impl

    return _impl(context)


def _handle_public_web_presence(context: Any) -> str:
    from .public_profile_runtime import _handle_public_web_presence as _impl

    return _impl(context)


def _handle_public_social_presence(context: Any) -> str:
    from .public_profile_runtime import _handle_public_social_presence as _impl

    return _impl(context)


def _handle_public_comparative(context: Any) -> str:
    from .public_profile_runtime import _handle_public_comparative as _impl

    return _impl(context)


def _handle_public_operating_hours(context: Any) -> str:
    from .public_profile_runtime import _handle_public_operating_hours as _impl

    return _impl(context)


def _handle_public_calendar_events(context: Any) -> str:
    from .public_profile_runtime import _handle_public_calendar_events as _impl

    return _impl(context)


def _handle_public_curriculum(context: Any) -> str:
    from .public_profile_runtime import _handle_public_curriculum as _impl

    return _impl(context)


def _handle_public_kpi(context: Any) -> str:
    from .public_profile_runtime import _handle_public_kpi as _impl

    return _impl(context)


def _handle_public_highlight(context: Any) -> str:
    from .public_profile_runtime import _handle_public_highlight as _impl

    return _impl(context)


def _handle_public_pricing(context: Any) -> str:
    from .public_profile_runtime import _handle_public_pricing as _impl

    return _impl(context)


def _handle_public_schedule(context: Any) -> str:
    from .public_profile_runtime import _handle_public_schedule as _impl

    return _impl(context)


def _handle_public_features(context: Any) -> str:
    from .public_profile_runtime import _handle_public_features as _impl

    return _impl(context)


def _handle_public_segments(context: Any) -> str:
    from .public_profile_runtime import _handle_public_segments as _impl

    return _impl(context)


def _handle_public_input_clarification(context: Any) -> str:
    return _compose_input_clarification_answer(
        context.profile,
        conversation_context=context.conversation_context,
    )


def _handle_public_scope_boundary(context: Any) -> str:
    return _compose_scope_boundary_answer(
        context.profile,
        conversation_context=context.conversation_context,
    )


def _handle_public_utility_date(_: Any) -> str:
    return f'Hoje e {_format_brazilian_date(date.today())}.'


def _handle_public_auth_guidance(_: Any) -> str:
    return (
        'Para consultas protegidas, como notas, faltas e financeiro, voce precisa vincular sua conta do Telegram ao portal da escola. '
        'No portal autenticado, gere o codigo de vinculacao e depois envie aqui o comando `/start link_<codigo>`. '
        'Depois disso, eu passo a consultar seus dados autorizados por este canal.'
    )


def _handle_public_language_preference(context: Any) -> str:
    return _compose_language_preference_answer(
        context.profile,
        context.source_message,
        conversation_context=context.conversation_context,
    )


def _handle_public_access_scope(context: Any) -> str:
    return _compose_public_access_scope_answer(
        context.actor,
        school_name=context.school_name,
    )


def _handle_public_assistant_identity(context: Any) -> str:
    return _compose_assistant_identity_answer(
        context.profile,
        conversation_context=context.conversation_context,
    )


def _handle_public_contacts(context: Any) -> str | None:
    return _handle_public_contacts_impl(context)


def _handle_public_timeline(context: Any) -> str | None:
    return _handle_public_timeline_impl(context)


def _handle_public_location(context: Any) -> str:
    location = ', '.join(
        part
        for part in [context.address_line, context.district, context.city, context.state]
        if part
    )
    if context.postal_code:
        location = f'{location}, CEP {context.postal_code}'
    return f'{context.school_reference_capitalized} fica em {location}.'


def _handle_public_confessional(context: Any) -> str:
    if context.confessional_status == 'laica':
        return (
            f'{context.school_reference_capitalized} e uma escola laica. '
            'A proposta institucional e plural e nao confessional.'
        )
    return f'Hoje o perfil publico classifica {context.school_reference} como {context.confessional_status}.'


def _handle_public_visit(context: Any) -> str:
    offers = _public_visit_offers(context.profile)
    services = _public_service_catalog(context.profile)
    if not offers:
        return f'Hoje o perfil publico de {context.school_reference} nao traz janelas de visita institucional.'
    lines = [
        f'Hoje {_school_subject_reference(context.school_reference)} publica estas janelas de visita:'
    ]
    for item in offers:
        lines.append(
            '- {title}: {day_label}, das {start_time} as {end_time}, em {location}. {notes}'.format(
                title=item.get('title', 'Visita institucional'),
                day_label=item.get('day_label', 'dia util'),
                start_time=item.get('start_time', '--:--'),
                end_time=item.get('end_time', '--:--'),
                location=item.get('location', 'local a confirmar'),
                notes=str(item.get('notes', '')).strip(),
            ).rstrip()
        )
    visit_service = next(
        (item for item in services if str(item.get('service_key')) == 'visita_institucional'),
        None,
    )
    if visit_service is not None:
        lines.append(
            'Agendamento: {request_channel}. Prazo de confirmacao: {typical_eta}.'.format(
                request_channel=visit_service.get('request_channel', 'canal institucional'),
                typical_eta=visit_service.get('typical_eta', 'ate 1 dia util'),
            )
        )
    return '\n'.join(lines)


def _handle_public_school_name(context: Any) -> str:
    return f'O nome oficial da escola e {context.school_name}.'


NON_AGENTIC_PUBLIC_COMPOSITION_ACTS = {
    'greeting',
    'input_clarification',
    'scope_boundary',
    'utility_date',
    'auth_guidance',
    'access_scope',
    'language_preference',
    'assistant_identity',
    'capabilities',
}


def _public_profile_handler_registry() -> dict[str, Callable[[Any], str]]:
    return {
        'acknowledgement': _handle_public_acknowledgement,
        'greeting': _handle_public_greeting,
        'input_clarification': _handle_public_input_clarification,
        'scope_boundary': _handle_public_scope_boundary,
        'utility_date': _handle_public_utility_date,
        'auth_guidance': _handle_public_auth_guidance,
        'access_scope': _handle_public_access_scope,
        'language_preference': _handle_public_language_preference,
        'assistant_identity': _handle_public_assistant_identity,
        'service_routing': _handle_public_service_routing,
        'service_credentials_bundle': _handle_public_service_credentials_bundle,
        'capabilities': _handle_public_capabilities,
        'document_submission': _handle_public_document_submission,
        'policy': _handle_public_policy,
        'policy_compare': _handle_public_policy_compare,
        'capacity': _handle_public_capacity,
        'careers': _handle_public_careers,
        'teacher_directory': _handle_public_teacher_directory,
        'leadership': _handle_public_leadership,
        'web_presence': _handle_public_web_presence,
        'social_presence': _handle_public_social_presence,
        'comparative': _handle_public_comparative,
        'contacts': _handle_public_contacts,
        'operating_hours': _handle_public_operating_hours,
        'timeline': _handle_public_timeline,
        'calendar_events': _handle_public_calendar_events,
        'location': _handle_public_location,
        'confessional': _handle_public_confessional,
        'curriculum': _handle_public_curriculum,
        'kpi': _handle_public_kpi,
        'highlight': _handle_public_highlight,
        'visit': _handle_public_visit,
        'pricing': _handle_public_pricing,
        'schedule': _handle_public_schedule,
        'features': _handle_public_features,
        'segments': _handle_public_segments,
        'school_name': _handle_public_school_name,
    }
