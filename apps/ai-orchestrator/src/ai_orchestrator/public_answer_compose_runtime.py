from __future__ import annotations

from typing import Any

from .conversation_focus_runtime import _normalize_text
from .intent_analysis_runtime import (
    _compose_required_documents_answer,
    _is_follow_up_query,
    _is_positive_requirement_query,
    _is_public_pricing_navigation_query,
    _message_matches_term,
)


def _build_public_profile_context(
    profile: dict[str, Any],
    message: str,
    *,
    actor: dict[str, Any] | None = None,
    original_message: str | None = None,
    conversation_context: dict[str, Any] | None = None,
    semantic_plan: Any | None = None,
):
    from .public_profile_runtime import _build_public_profile_context as _impl

    return _impl(
        profile,
        message,
        actor=actor,
        original_message=original_message,
        conversation_context=conversation_context,
        semantic_plan=semantic_plan,
    )


def _localize_pt_br_surface_labels(text: str) -> str:
    from .public_profile_runtime import _localize_pt_br_surface_labels as _impl

    return _impl(text)


def _compose_scope_boundary_answer(
    profile: dict[str, Any],
    *,
    conversation_context: dict[str, Any] | None = None,
) -> str:
    from .public_profile_intent_runtime import _compose_scope_boundary_answer as _impl

    return _impl(profile, conversation_context=conversation_context)


def _public_profile_handler_registry():
    from .public_profile_runtime import _public_profile_handler_registry as _impl

    return _impl()


def _has_public_multi_intent_signal(message: str) -> bool:
    from .public_profile_runtime import _has_public_multi_intent_signal as _impl

    return _impl(message)


def match_public_canonical_lane(message: str) -> str | None:
    from .public_profile_runtime import match_public_canonical_lane as _impl

    return _impl(message)


def compose_public_canonical_lane_answer(
    canonical_lane: str,
    *,
    profile: dict[str, Any],
) -> str | None:
    from .public_profile_runtime import compose_public_canonical_lane_answer as _impl

    return _impl(canonical_lane, profile=profile)


def _handle_public_pricing(context: Any) -> str:
    from .public_profile_runtime import _handle_public_pricing as _impl

    return _impl(context)


def _compose_public_multi_intent_answer(
    context: Any,
    *,
    semantic_plan: Any | None = None,
) -> str | None:
    from .public_profile_runtime import _compose_public_multi_intent_answer as _impl

    return _impl(context, semantic_plan=semantic_plan)


def _mentions_school_year_start_topic(message: str) -> bool:
    from .public_profile_runtime import _mentions_school_year_start_topic as _impl

    return _impl(message)


def _recent_user_message_mentions(
    conversation_context: dict[str, Any] | None,
    phrases: set[str],
) -> bool:
    from .public_profile_runtime import _recent_user_message_mentions as _impl

    return _impl(conversation_context, phrases)


def _compose_public_school_year_start_answer(
    profile: dict[str, Any],
    school_reference: str,
) -> str | None:
    from .public_profile_runtime import _compose_public_school_year_start_answer as _impl

    return _impl(profile, school_reference)


def _resolve_public_profile_act(context: Any) -> str:
    from .public_profile_intent_runtime import _resolve_public_profile_act as _impl

    return _impl(context)


def _target_public_feature_for_operating_hours(context: Any) -> dict[str, Any] | None:
    from .public_profile_runtime import _target_public_feature_for_operating_hours as _impl

    return _impl(context)


def _try_public_channel_fast_answer(
    profile: dict[str, Any],
    message: str,
    *,
    original_message: str | None = None,
    conversation_context: dict[str, Any] | None = None,
    semantic_plan: Any | None = None,
) -> str | None:
    from .public_profile_runtime import _try_public_channel_fast_answer as _impl

    return _impl(
        profile,
        message,
        original_message=original_message,
        conversation_context=conversation_context,
        semantic_plan=semantic_plan,
    )


def _compose_public_profile_answer_legacy(
    profile: dict[str, Any],
    message: str,
    *,
    original_message: str | None = None,
    conversation_context: dict[str, Any] | None = None,
    semantic_plan: Any | None = None,
) -> str:
    from .public_profile_runtime import _compose_public_profile_answer_legacy as _impl

    return _impl(
        profile,
        message,
        original_message=original_message,
        conversation_context=conversation_context,
        semantic_plan=semantic_plan,
    )


def _compose_public_profile_answer(
    profile: dict[str, Any],
    message: str,
    *,
    actor: dict[str, Any] | None = None,
    original_message: str | None = None,
    conversation_context: dict[str, Any] | None = None,
    semantic_plan: Any | None = None,
) -> str:
    context = _build_public_profile_context(
        profile,
        message,
        actor=actor,
        original_message=original_message,
        conversation_context=conversation_context,
        semantic_plan=semantic_plan,
    )
    normalized_source_message = _normalize_text(context.source_message)
    if (
        'biblioteca' in normalized_source_message
        and any(
            _message_matches_term(normalized_source_message, term)
            for term in {
                'biblioteca publica',
                'biblioteca pública',
                'publica da cidade',
                'pública da cidade',
                'da cidade',
                'municipal',
                'prefeitura',
            }
        )
    ):
        return _localize_pt_br_surface_labels(
            _compose_scope_boundary_answer(
                context.profile,
                conversation_context=context.conversation_context,
            )
        )
    if _is_positive_requirement_query(context.source_message) or (
        any(_message_matches_term(normalized_source_message, term) for term in {'documento', 'documentos'})
        and any(
            _message_matches_term(normalized_source_message, term)
            for term in {'matricula', 'matrícula', 'exigido', 'exigidos'}
        )
    ):
        return _localize_pt_br_surface_labels(_compose_required_documents_answer(profile))
    registry = _public_profile_handler_registry()
    if semantic_plan is not None and semantic_plan.conversation_act in {
        'greeting',
        'assistant_identity',
        'auth_guidance',
        'capabilities',
        'input_clarification',
        'language_preference',
        'scope_boundary',
    }:
        semantic_handler = registry.get(semantic_plan.conversation_act)
        if semantic_handler is not None:
            semantic_answer = semantic_handler(context)
            if semantic_answer:
                return _localize_pt_br_surface_labels(semantic_answer)
    semantic_requires_multi_intent = bool(
        semantic_plan is not None
        and (semantic_plan.conversation_act != 'pricing' or bool(semantic_plan.secondary_acts))
    )
    canonical_lane = match_public_canonical_lane(
        context.source_message
    ) or match_public_canonical_lane(original_message or message)
    if canonical_lane:
        lane_answer = compose_public_canonical_lane_answer(canonical_lane, profile=profile)
        if lane_answer:
            return _localize_pt_br_surface_labels(lane_answer)
    if _is_public_pricing_navigation_query(context.source_message) and not (
        semantic_requires_multi_intent or _has_public_multi_intent_signal(context.source_message)
    ):
        pricing_answer = _handle_public_pricing(context)
        if pricing_answer:
            return _localize_pt_br_surface_labels(pricing_answer)
    multi_intent_answer = _compose_public_multi_intent_answer(
        context,
        semantic_plan=semantic_plan,
    )
    if multi_intent_answer:
        return _localize_pt_br_surface_labels(multi_intent_answer)
    if (
        (
            _is_follow_up_query(context.source_message)
            or normalized_source_message.startswith('depois disso')
        )
        and (
            _mentions_school_year_start_topic(context.source_message)
            or _message_matches_term(normalized_source_message, 'aulas')
        )
        and (
            normalized_source_message.startswith('depois disso')
            or _recent_user_message_mentions(
                context.conversation_context,
                {
                    'matricula',
                    'matrícula',
                    'proximo ciclo',
                    'próximo ciclo',
                    'inscricoes',
                    'inscrições',
                },
            )
        )
    ):
        school_year_start_answer = _compose_public_school_year_start_answer(
            profile, context.school_reference
        )
        if school_year_start_answer:
            return _localize_pt_br_surface_labels(school_year_start_answer)
    resolved_act = _resolve_public_profile_act(context)
    handler = registry.get(resolved_act)
    if handler is not None:
        primary_text = handler(context)
        extra_texts: list[str] = []
        if semantic_plan is not None:
            secondary_acts = semantic_plan.secondary_acts[:2]
            if semantic_plan.conversation_act == 'timeline' and not _has_public_multi_intent_signal(
                context.source_message
            ):
                secondary_acts = ()
            for act in secondary_acts:
                if act == resolved_act:
                    continue
                if (
                    resolved_act == 'operating_hours'
                    and act == 'features'
                    and _target_public_feature_for_operating_hours(context) is not None
                ):
                    continue
                extra_handler = registry.get(act)
                if extra_handler is None:
                    continue
                candidate = extra_handler(context).strip()
                if not candidate:
                    continue
                normalized_candidate = _normalize_text(candidate)
                if normalized_candidate in _normalize_text(primary_text):
                    continue
                if any(normalized_candidate in _normalize_text(text) for text in extra_texts):
                    continue
                extra_texts.append(candidate)
        if extra_texts:
            return _localize_pt_br_surface_labels('\n\n'.join([primary_text, *extra_texts]))
        return _localize_pt_br_surface_labels(primary_text)

    fast_public_channel_answer = _try_public_channel_fast_answer(
        message=context.source_message,
        profile=profile,
    )
    if fast_public_channel_answer:
        return _localize_pt_br_surface_labels(fast_public_channel_answer)
    return _localize_pt_br_surface_labels(
        _compose_public_profile_answer_legacy(
            profile,
            message,
            original_message=original_message,
            conversation_context=conversation_context,
            semantic_plan=semantic_plan,
        )
    )
