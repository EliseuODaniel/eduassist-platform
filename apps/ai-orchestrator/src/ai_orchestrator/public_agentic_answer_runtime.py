from __future__ import annotations

from typing import Any


def _public_institution_plan_cls():
    from .public_profile_runtime import PublicInstitutionPlan

    return PublicInstitutionPlan


def _llm_forced_mode_enabled(*, settings: Any) -> bool:
    from .public_profile_runtime import _llm_forced_mode_enabled as _impl

    return _impl(settings=settings)


def _compose_public_profile_answer(
    profile: dict[str, Any],
    message: str,
    *,
    actor: dict[str, Any] | None = None,
    original_message: str | None = None,
    conversation_context: dict[str, Any] | None = None,
    semantic_plan: Any | None = None,
) -> str:
    from .public_profile_runtime import _compose_public_profile_answer as _impl

    return _impl(
        profile,
        message,
        actor=actor,
        original_message=original_message,
        conversation_context=conversation_context,
        semantic_plan=semantic_plan,
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


def _resolve_public_profile_act(context: Any) -> str:
    from .public_profile_intent_runtime import _resolve_public_profile_act as _impl

    return _impl(context)


def match_public_canonical_lane(message: str) -> str | None:
    from .public_profile_runtime import match_public_canonical_lane as _impl

    return _impl(message)


def _should_preserve_deterministic_public_answer(
    *,
    resolved_act: str,
    request_message: str,
    original_message: str | None,
    conversation_context: dict[str, Any] | None,
    deterministic_text: str,
    canonical_lane: str | None,
) -> bool:
    from .public_profile_runtime import _should_preserve_deterministic_public_answer as _impl

    return _impl(
        resolved_act=resolved_act,
        request_message=request_message,
        original_message=original_message,
        conversation_context=conversation_context,
        deterministic_text=deterministic_text,
        canonical_lane=canonical_lane,
    )


def build_public_evidence_bundle(
    profile: dict[str, Any],
    *,
    primary_act: str,
    secondary_acts: tuple[str, ...] | list[str],
    request_message: str,
    focus_hint: str | None,
):
    from .public_profile_runtime import build_public_evidence_bundle as _impl

    return _impl(
        profile,
        primary_act=primary_act,
        secondary_acts=secondary_acts,
        request_message=request_message,
        focus_hint=focus_hint,
    )


async def compose_langgraph_public_grounded_with_provider(
    *,
    settings: Any,
    request_message: str,
    draft_text: str,
    public_plan: dict[str, Any],
    evidence_lines: list[str],
    conversation_context: dict[str, Any] | None,
    school_profile: dict[str, Any],
) -> str | None:
    from .public_profile_runtime import compose_langgraph_public_grounded_with_provider as _impl

    return await _impl(
        settings=settings,
        request_message=request_message,
        draft_text=draft_text,
        public_plan=public_plan,
        evidence_lines=evidence_lines,
        conversation_context=conversation_context,
        school_profile=school_profile,
    )


def _build_public_institution_plan(
    message: str,
    selected_tools: list[str],
    *,
    conversation_context: dict[str, Any] | None = None,
):
    from .public_profile_runtime import _build_public_institution_plan as _impl

    return _impl(message, selected_tools, conversation_context=conversation_context)


def _should_use_public_open_documentary_synthesis(message: str, public_plan: Any) -> bool:
    from .public_profile_runtime import _should_use_public_open_documentary_synthesis as _impl

    return _impl(message, public_plan)


def _access_tier_public():
    from .public_profile_runtime import AccessTier

    return AccessTier.public


async def _compose_public_profile_answer_agentic(
    *,
    settings: Any,
    profile: dict[str, Any],
    actor: dict[str, Any] | None = None,
    message: str,
    original_message: str | None = None,
    conversation_context: dict[str, Any] | None = None,
    semantic_plan: Any | None = None,
    deterministic_text_sink: dict[str, Any] | None = None,
) -> str:
    plan_cls = _public_institution_plan_cls()
    if semantic_plan is not None and not isinstance(semantic_plan, plan_cls):
        semantic_plan = plan_cls(
            conversation_act=str(getattr(semantic_plan, 'conversation_act', 'canonical_fact') or 'canonical_fact'),
            required_tools=tuple(getattr(semantic_plan, 'required_tools', ()) or ()),
            fetch_profile=bool(getattr(semantic_plan, 'fetch_profile', True)),
            secondary_acts=tuple(getattr(semantic_plan, 'secondary_acts', ()) or ()),
            requested_attribute=getattr(semantic_plan, 'requested_attribute', None),
            requested_channel=getattr(semantic_plan, 'requested_channel', None),
            focus_hint=getattr(semantic_plan, 'focus_hint', None),
            semantic_source=str(getattr(semantic_plan, 'semantic_source', 'rules') or 'rules'),
            use_conversation_context=bool(getattr(semantic_plan, 'use_conversation_context', False)),
        )
    llm_forced_mode = _llm_forced_mode_enabled(settings=settings)
    deterministic_text = _compose_public_profile_answer(
        profile,
        message,
        actor=actor,
        original_message=original_message,
        conversation_context=conversation_context,
        semantic_plan=semantic_plan,
    )
    if deterministic_text_sink is not None:
        deterministic_text_sink['deterministic_text'] = deterministic_text
        deterministic_text_sink['agentic_llm_used'] = False
        deterministic_text_sink['agentic_llm_stages'] = []
    context = _build_public_profile_context(
        profile,
        message,
        actor=actor,
        original_message=original_message,
        conversation_context=conversation_context,
        semantic_plan=semantic_plan,
    )
    resolved_act = _resolve_public_profile_act(context)
    canonical_lane = match_public_canonical_lane(
        context.source_message
    ) or match_public_canonical_lane(original_message or message)
    if not llm_forced_mode and _should_preserve_deterministic_public_answer(
        resolved_act=resolved_act,
        request_message=message,
        original_message=original_message,
        conversation_context=conversation_context,
        deterministic_text=deterministic_text,
        canonical_lane=canonical_lane,
    ):
        return deterministic_text

    evidence_bundle = build_public_evidence_bundle(
        profile,
        primary_act=resolved_act,
        secondary_acts=semantic_plan.secondary_acts if semantic_plan is not None else (),
        request_message=original_message or message,
        focus_hint=semantic_plan.focus_hint if semantic_plan is not None else None,
    )
    if evidence_bundle is None:
        return deterministic_text

    plan_payload = {
        'conversation_act': resolved_act,
        'secondary_acts': list(evidence_bundle.secondary_acts),
        'requested_attribute': semantic_plan.requested_attribute if semantic_plan else None,
        'requested_channel': semantic_plan.requested_channel if semantic_plan else None,
        'semantic_source': semantic_plan.semantic_source if semantic_plan else 'rules',
    }
    llm_text = await compose_langgraph_public_grounded_with_provider(
        settings=settings,
        request_message=original_message or message,
        draft_text=deterministic_text,
        public_plan=plan_payload,
        evidence_lines=[fact.text for fact in evidence_bundle.facts],
        conversation_context=conversation_context,
        school_profile=profile,
    )
    if deterministic_text_sink is not None and llm_text:
        deterministic_text_sink['agentic_llm_used'] = True
        deterministic_text_sink['agentic_llm_stages'] = ['answer_composition']
    return llm_text or deterministic_text


async def _maybe_langgraph_open_documentary_candidate(
    *,
    settings: Any,
    engine_name: str,
    request: Any,
    preview: Any,
    school_profile: dict[str, Any] | None,
    conversation_context: dict[str, Any] | None,
    draft_text: str,
) -> str | None:
    if str(engine_name or '').strip().lower() != 'langgraph':
        return None
    if not _llm_forced_mode_enabled(settings=settings):
        return None
    if school_profile is None:
        return None
    if preview.classification.access_tier is not _access_tier_public():
        return None
    public_plan = _build_public_institution_plan(
        request.message,
        list(preview.selected_tools),
        conversation_context=conversation_context,
    )
    if not _should_use_public_open_documentary_synthesis(request.message, public_plan):
        return None
    evidence_bundle = build_public_evidence_bundle(
        school_profile,
        primary_act=public_plan.conversation_act,
        secondary_acts=public_plan.secondary_acts,
        request_message=request.message,
        focus_hint=public_plan.focus_hint,
    )
    if evidence_bundle is None or not evidence_bundle.facts:
        return None
    plan_payload = {
        'conversation_act': public_plan.conversation_act,
        'secondary_acts': list(evidence_bundle.secondary_acts),
        'requested_attribute': public_plan.requested_attribute,
        'requested_channel': public_plan.requested_channel,
        'semantic_source': public_plan.semantic_source,
    }
    llm_text = await compose_langgraph_public_grounded_with_provider(
        settings=settings,
        request_message=request.message,
        draft_text=draft_text,
        public_plan=plan_payload,
        evidence_lines=[fact.text for fact in evidence_bundle.facts],
        conversation_context=conversation_context,
        school_profile=school_profile,
    )
    return llm_text or None
