from __future__ import annotations

import re
from typing import Any, Callable

from .public_contact_runtime import _requested_contact_channel


def _intent_analysis_impl(name: str):
    from . import intent_analysis_runtime as _intent_analysis_runtime

    return getattr(_intent_analysis_runtime, name)


def _is_direct_service_routing_bundle_query(message: str) -> bool:
    return _intent_analysis_impl('_is_direct_service_routing_bundle_query')(message)


def _is_public_pricing_navigation_query(message: str) -> bool:
    return _intent_analysis_impl('_is_public_pricing_navigation_query')(message)


def _is_service_routing_query(message: str) -> bool:
    return _intent_analysis_impl('_is_service_routing_query')(message)

_PUBLIC_MULTI_INTENT_LABELS: dict[str, str] = {
    'contacts': 'Canais gerais da escola',
    'service_routing': 'Setor certo por assunto',
    'pricing': 'Valores publicos e simulacao',
    'document_submission': 'Documentos e envio',
    'service_credentials_bundle': 'Portal, credenciais e secretaria',
    'policy_compare': 'Regras academicas e regulamentos',
    'timeline': 'Linha do tempo publica',
    'calendar_events': 'Calendario publico',
}


def _matches_public_contact_rule(message: str) -> bool:
    from .public_profile_runtime import _matches_public_contact_rule as _impl

    return _impl(message)


def _is_public_document_submission_query(message: str) -> bool:
    from .public_document_policy_runtime import _is_public_document_submission_query as _impl

    return _impl(message)


def _is_public_service_credentials_bundle_query(message: str) -> bool:
    from .public_document_policy_runtime import _is_public_service_credentials_bundle_query as _impl

    return _impl(message)


def _is_public_policy_compare_query(message: str) -> bool:
    from .public_document_policy_runtime import _is_public_policy_compare_query as _impl

    return _impl(message)


def _is_public_timeline_query(message: str) -> bool:
    from .public_timeline_runtime import _is_public_timeline_query as _impl

    return _impl(message)


def _is_public_calendar_event_query(message: str) -> bool:
    from .public_timeline_runtime import _is_public_calendar_event_query as _impl

    return _impl(message)


def _has_public_multi_intent_signal(message: str) -> bool:
    from .public_profile_runtime import _has_public_multi_intent_signal as _impl

    return _impl(message)


def _matched_public_act_rules(
    message: str,
    *,
    conversation_context: dict[str, Any] | None = None,
):
    from .public_profile_runtime import _matched_public_act_rules as _impl

    return _impl(message, conversation_context=conversation_context)


def _prioritize_public_act_rules(message: str, matched_rules):
    from .public_profile_runtime import _prioritize_public_act_rules as _impl

    return _impl(message, matched_rules)


def _handle_public_contacts(context: Any) -> str | None:
    from .public_profile_runtime import _handle_public_contacts as _impl

    return _impl(context)


def _handle_public_service_routing(context: Any) -> str:
    from .public_profile_runtime import _handle_public_service_routing as _impl

    return _impl(context)


def _handle_public_pricing(context: Any) -> str:
    from .public_operations_runtime import _handle_public_pricing as _impl

    return _impl(context)


def _handle_public_document_submission(context: Any) -> str:
    from .public_document_policy_runtime import _handle_public_document_submission as _impl

    return _impl(context)


def _compose_public_service_credentials_bundle_answer(profile: dict[str, Any]) -> str:
    from .public_document_policy_runtime import _compose_public_service_credentials_bundle_answer as _impl

    return _impl(profile)


def _compose_public_policy_compare_answer(profile: dict[str, Any]) -> str:
    from .public_document_policy_runtime import _compose_public_policy_compare_answer as _impl

    return _impl(profile)


def _handle_public_timeline(context: Any) -> str | None:
    from .public_profile_runtime import _handle_public_timeline as _impl

    return _impl(context)


def _compose_public_act_answer(
    context: Any,
    *,
    act: str,
) -> str | None:
    if act == 'contacts':
        return _handle_public_contacts(context)
    if act == 'service_routing':
        return _handle_public_service_routing(context)
    if act == 'pricing':
        return _handle_public_pricing(context)
    if act == 'document_submission':
        return _handle_public_document_submission(context)
    if act == 'service_credentials_bundle':
        return _compose_public_service_credentials_bundle_answer(context.profile)
    if act == 'policy_compare':
        return _compose_public_policy_compare_answer(context.profile)
    if act == 'timeline':
        return _handle_public_timeline(context)
    if act == 'calendar_events':
        return _handle_public_timeline(context)
    return None


def _candidate_public_multi_intent_acts(
    *,
    message: str,
    semantic_plan: Any | None,
    conversation_context: dict[str, Any] | None,
) -> tuple[str, ...]:
    acts: list[str] = []

    explicit_detectors: tuple[tuple[str, Callable[[str], bool]], ...] = (
        (
            'contacts',
            lambda value: (
                _matches_public_contact_rule(value) or _requested_contact_channel(value) is not None
            ),
        ),
        ('service_routing', _is_service_routing_query),
        ('pricing', _is_public_pricing_navigation_query),
        ('document_submission', _is_public_document_submission_query),
        ('service_credentials_bundle', _is_public_service_credentials_bundle_query),
        ('policy_compare', _is_public_policy_compare_query),
        ('timeline', _is_public_timeline_query),
        ('calendar_events', _is_public_calendar_event_query),
    )
    explicit_acts: list[str] = []
    for act, matcher in explicit_detectors:
        if matcher(message) and act not in explicit_acts:
            explicit_acts.append(act)

    has_multi_intent_signal = _has_public_multi_intent_signal(message)
    if semantic_plan is not None:
        semantic_acts = [
            act
            for act in (semantic_plan.conversation_act, *semantic_plan.secondary_acts)
            if isinstance(act, str) and act.strip()
        ]
        if has_multi_intent_signal:
            acts.extend(semantic_acts)
        elif not explicit_acts:
            acts.extend(semantic_acts[:1])
        elif semantic_plan.conversation_act in explicit_acts:
            acts.append(semantic_plan.conversation_act)
    elif has_multi_intent_signal:
        matched_rules = _prioritize_public_act_rules(
            message,
            _matched_public_act_rules(message, conversation_context=conversation_context),
        )
        acts.extend(
            rule.name for rule in matched_rules[:3] if isinstance(rule.name, str) and rule.name
        )

    acts.extend(act for act in explicit_acts if act not in acts)

    ordered: list[str] = []
    seen: set[str] = set()
    for act in acts:
        if act not in _PUBLIC_MULTI_INTENT_LABELS:
            continue
        if act in seen:
            continue
        seen.add(act)
        ordered.append(act)
    return tuple(ordered)


def _compose_public_multi_intent_answer(
    context: Any,
    *,
    semantic_plan: Any | None = None,
) -> str | None:
    if _is_direct_service_routing_bundle_query(context.source_message):
        return None
    acts = _candidate_public_multi_intent_acts(
        message=context.source_message,
        semantic_plan=semantic_plan,
        conversation_context=context.conversation_context,
    )
    if len(acts) < 2:
        return None
    sections: list[tuple[str, str]] = []
    seen_answers: set[str] = set()
    for act in acts[:3]:
        answer = _compose_public_act_answer(context, act=act)
        normalized_answer = re.sub(r'\s+', ' ', str(answer or '').strip())
        if not normalized_answer or normalized_answer in seen_answers:
            continue
        seen_answers.add(normalized_answer)
        sections.append((_PUBLIC_MULTI_INTENT_LABELS[act], normalized_answer.replace('\n', ' ')))
    if len(sections) < 2:
        return None
    intro = (
        'Posso separar esse pedido em duas frentes complementares:'
        if len(sections) == 2
        else 'Posso separar esse pedido em frentes complementares:'
    )
    lines = [intro]
    lines.extend(f'- {label}: {answer}' for label, answer in sections)
    return '\n'.join(lines)
