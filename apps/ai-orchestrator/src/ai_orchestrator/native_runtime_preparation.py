from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable

from . import runtime as rt
from .path_profiles import PathExecutionProfile, get_path_execution_profile
from .semantic_ingress_runtime import (
    apply_semantic_ingress_preview,
    apply_turn_frame_preview,
    build_semantic_ingress_public_plan,
    build_turn_frame_public_plan,
    is_terminal_semantic_ingress_plan,
    maybe_resolve_semantic_ingress_plan,
    maybe_resolve_turn_frame,
)


@dataclass(slots=True)
class RuntimeExecutionPreparation:
    effective_path_profile: PathExecutionProfile
    actor: dict[str, Any] | None
    effective_conversation_id: str | None
    conversation_context_bundle: Any
    context_payload: dict[str, Any] | None
    analysis_message: str
    school_profile: dict[str, Any] | None
    effective_plan: Any
    preview: Any
    semantic_ingress_plan: Any | None = None
    semantic_ingress_public_plan: Any | None = None
    turn_frame: Any | None = None
    turn_frame_public_plan: Any | None = None
    llm_stages: list[str] = field(default_factory=list)


@dataclass(slots=True)
class RuntimeExecutionAccumulators:
    retrieval_hits: list[Any] = field(default_factory=list)
    citations: list[Any] = field(default_factory=list)
    visual_assets: list[Any] = field(default_factory=list)
    calendar_events: list[Any] = field(default_factory=list)
    retrieval_context_pack: str | None = None
    public_plan: Any | None = None
    deterministic_fallback_text: str | None = None
    query_hints: set[str] = field(default_factory=set)
    semantic_judge_used: bool = False
    llm_stages: list[str] = field(default_factory=list)
    answer_verifier_fallback_used: bool = False


def build_runtime_execution_accumulators(*, llm_stages: list[str] | None = None) -> RuntimeExecutionAccumulators:
    accumulators = RuntimeExecutionAccumulators()
    if llm_stages:
        accumulators.llm_stages.extend(llm_stages)
    return accumulators


async def prepare_runtime_execution(
    *,
    request: Any,
    settings: Any,
    plan: Any,
    engine_name: str,
    path_profile: PathExecutionProfile | None,
    build_plan_fn: Callable[..., Any],
    select_better_plan: Callable[..., Any],
    needs_contextual_replan: Callable[..., bool],
    prefer_contextual_tie: Callable[..., bool],
    replan_builder: Callable[[Any, Any, str], Any] | None = None,
    explicit_domain_override_resolver: Callable[..., Any | None] | None = None,
    contextual_replan_guard: Callable[..., bool] | None = None,
    use_semantic_ingress: bool = False,
    semantic_stack_label: str | None = None,
    protected_rescue_predicate: Callable[..., bool] | None = None,
) -> RuntimeExecutionPreparation:
    effective_path_profile = path_profile or get_path_execution_profile(engine_name)
    actor = await rt._fetch_actor_context(settings=settings, telegram_chat_id=request.telegram_chat_id)
    effective_conversation_id = rt._effective_conversation_id(request)
    conversation_context_bundle = await rt._fetch_conversation_context(
        settings=settings,
        conversation_external_id=effective_conversation_id,
        channel=request.channel.value,
    )
    context_payload = rt._conversation_context_payload(conversation_context_bundle)
    analysis_message = rt._build_analysis_message(request.message, conversation_context_bundle)
    school_profile = await rt._fetch_public_school_profile(settings=settings)
    effective_plan = plan

    skip_contextual_replan = False
    if contextual_replan_guard is not None:
        skip_contextual_replan = bool(
            contextual_replan_guard(request=request, conversation_context=context_payload)
        )

    if effective_path_profile.use_contextual_replan and not skip_contextual_replan and needs_contextual_replan(
        request=request,
        plan=plan,
        analysis_message=analysis_message,
    ):
        contextual_request = request.model_copy(update={'message': analysis_message})
        if replan_builder is not None:
            candidate_plan = replan_builder(contextual_request, settings, plan.mode)
        else:
            candidate_plan = build_plan_fn(
                request=contextual_request,
                settings=settings,
                stack_name=plan.stack_name,
                mode=plan.mode,
            )
        effective_plan = select_better_plan(current=plan, candidate=candidate_plan)
        if effective_plan is plan and prefer_contextual_tie(
            request=request,
            current=plan,
            candidate=candidate_plan,
        ):
            effective_plan = candidate_plan
        if effective_plan is candidate_plan:
            effective_plan = candidate_plan.model_copy(
                update={'plan_notes': [*plan.plan_notes, 'contextual_replan']}
            )

    if explicit_domain_override_resolver is not None:
        explicit_domain_override = explicit_domain_override_resolver(
            request=request,
            settings=settings,
            current=effective_plan,
            replan_builder=replan_builder,
        )
        if explicit_domain_override is not None:
            effective_plan = explicit_domain_override

    preview = effective_plan.preview.model_copy(deep=True)
    semantic_ingress_plan = None
    semantic_ingress_public_plan = None
    turn_frame = None
    turn_frame_public_plan = None
    llm_stages: list[str] = []

    if use_semantic_ingress and semantic_stack_label:
        semantic_preview = preview.model_copy(deep=True)
        semantic_ingress_plan = await maybe_resolve_semantic_ingress_plan(
            settings=settings,
            request_message=request.message,
            conversation_context=context_payload,
            preview=semantic_preview,
            stack_label=semantic_stack_label,
        )

        should_apply_rescue = actor is not None and bool(getattr(request.user, 'authenticated', False))
        if should_apply_rescue and (semantic_ingress_plan is None or not is_terminal_semantic_ingress_plan(semantic_ingress_plan)):
            if protected_rescue_predicate is not None:
                should_apply_rescue = bool(
                    protected_rescue_predicate(
                        request=request,
                        actor=actor,
                        conversation_context=context_payload,
                        semantic_ingress_plan=semantic_ingress_plan,
                    )
                )
            if should_apply_rescue:
                rt._apply_protected_domain_rescue(
                    preview=preview,
                    actor=actor,
                    message=request.message,
                    conversation_context=context_payload,
                )

        if semantic_ingress_plan is not None:
            ingress_base_preview = semantic_preview if is_terminal_semantic_ingress_plan(semantic_ingress_plan) else preview
            preview = apply_semantic_ingress_preview(
                preview=ingress_base_preview,
                plan=semantic_ingress_plan,
                stack_name=semantic_stack_label,
            )
            effective_plan = effective_plan.model_copy(
                update={
                    'plan_notes': [
                        *effective_plan.plan_notes,
                        f'semantic_ingress:{semantic_ingress_plan.conversation_act}',
                    ]
                }
            )
            semantic_ingress_public_plan = build_semantic_ingress_public_plan(semantic_ingress_plan)
            llm_stages.append('semantic_ingress_classifier')
    if semantic_ingress_plan is None or not is_terminal_semantic_ingress_plan(semantic_ingress_plan):
        turn_frame = await maybe_resolve_turn_frame(
            settings=settings,
            request_message=request.message,
            conversation_context=context_payload,
            preview=preview,
            stack_label=semantic_stack_label or engine_name,
            authenticated=bool(getattr(request.user, "authenticated", False)),
        )
        if turn_frame is not None:
            preview = apply_turn_frame_preview(
                preview=preview,
                turn_frame=turn_frame,
                stack_name=semantic_stack_label or engine_name,
            )
            turn_frame_public_plan = build_turn_frame_public_plan(turn_frame)
            effective_plan = effective_plan.model_copy(
                update={
                    'plan_notes': [
                        *effective_plan.plan_notes,
                        f'turn_frame:{getattr(turn_frame, "capability_id", None) or getattr(turn_frame, "conversation_act", "none")}',
                    ]
                }
            )
            llm_stages.append('turn_frame_classifier')
    else:
        should_apply_rescue = actor is not None and bool(getattr(request.user, 'authenticated', False))
        if should_apply_rescue and (protected_rescue_predicate is None or protected_rescue_predicate(
            request=request,
            actor=actor,
            conversation_context=context_payload,
            semantic_ingress_plan=None,
        )):
            rt._apply_protected_domain_rescue(
                preview=preview,
                actor=actor,
                message=request.message,
                conversation_context=context_payload,
            )

    return RuntimeExecutionPreparation(
        effective_path_profile=effective_path_profile,
        actor=actor,
        effective_conversation_id=effective_conversation_id,
        conversation_context_bundle=conversation_context_bundle,
        context_payload=context_payload,
        analysis_message=analysis_message,
        school_profile=school_profile,
        effective_plan=effective_plan,
        preview=preview,
        semantic_ingress_plan=semantic_ingress_plan,
        semantic_ingress_public_plan=semantic_ingress_public_plan,
        turn_frame=turn_frame,
        turn_frame_public_plan=turn_frame_public_plan,
        llm_stages=llm_stages,
    )
