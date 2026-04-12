from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Any, Awaitable, Callable

import httpx

from .models import (
    MessageIntentClassification,
    SupervisorAnswerPayload,
    SpecialistSupervisorRequest,
    SpecialistSupervisorResponse,
)


@dataclass(frozen=True)
class SupervisorRunFlowDeps:
    run_context_cls: type[Any]
    get_specialist_registry: Callable[[], dict[str, Any]]
    preflight_public_doc_bundle_answer: Callable[[dict[str, Any] | None, str], SupervisorAnswerPayload | None]
    looks_like_internal_document_query: Callable[[str], bool]
    fetch_actor_context: Callable[[Any], Awaitable[dict[str, Any] | None]]
    fetch_conversation_context: Callable[[Any], Awaitable[dict[str, Any] | None]]
    load_operational_memory: Callable[[dict[str, Any] | None], Any]
    resolve_turn_intent: Callable[[Any], Any]
    tool_first_structured_answer: Callable[[Any], Awaitable[SupervisorAnswerPayload | None]]
    persist_final_answer: Callable[..., Awaitable[None]]
    fetch_public_school_profile: Callable[[Any], Awaitable[dict[str, Any] | None]]
    orchestrator_preview: Callable[[Any], Awaitable[dict[str, Any] | None]]
    teacher_scope_fast_path_answer: Callable[[Any], Awaitable[SupervisorAnswerPayload | None]]
    academic_grade_fast_path_answer: Callable[[Any], Awaitable[SupervisorAnswerPayload | None]]
    looks_like_third_party_student_data_request: Callable[[str], bool]
    build_third_party_student_data_denial: Callable[[], SupervisorAnswerPayload]
    operational_memory_follow_up_answer: Callable[[Any], Awaitable[SupervisorAnswerPayload | None]]
    fast_path_answer: Callable[[Any], SupervisorAnswerPayload | None]
    resolved_intent_answer: Callable[[Any], Awaitable[SupervisorAnswerPayload | None]]
    general_knowledge_fast_path_answer: Callable[[Any], Awaitable[SupervisorAnswerPayload | None]]
    resolve_llm_provider: Callable[[Any], str]
    effective_llm_model_name: Callable[[Any], str]
    default_suggested_replies: Callable[[str], list[Any]]
    run_input_guardrail_stage: Callable[[Any], Awaitable[Any]]
    run_retrieval_planner_stage: Callable[[Any], Awaitable[Any]]
    resolve_plan_and_budget: Callable[[Any], Awaitable[tuple[Any, Any]]]
    execution_budget_metadata: Callable[[Any, Any], dict[str, Any]]
    metadata_with_runtime_observability: Callable[[Any, dict[str, Any] | None], dict[str, Any]]
    build_budgeted_execution_specialists: Callable[..., dict[str, Any]]
    agent_model_for_role: Callable[..., Any]
    execute_budgeted_specialists: Callable[..., Awaitable[list[Any]]]
    build_multi_specialist_answer_from_results: Callable[..., SupervisorAnswerPayload | None]
    direct_compose_candidate: Callable[..., Any]
    build_direct_answer_from_specialist: Callable[..., SupervisorAnswerPayload]
    budgeted_no_manager_candidate: Callable[..., Any]
    needs_manager: Callable[..., bool]
    run_manager_stack: Callable[..., Awaitable[tuple[Any, Any, Any]]]
    merge_specialist_results: Callable[[list[Any], list[Any]], list[Any]]
    parse_specialist_results: Callable[[Any], list[Any]]
    grounding_gate_answer: Callable[..., SupervisorAnswerPayload | None]
    build_answer_payload: Callable[..., SupervisorAnswerPayload]
    safe_supervisor_fallback_answer: Callable[..., SupervisorAnswerPayload]
    access_tier_for_domain: Callable[[str, bool], str]
    log_execution_budget: Callable[[Any, Any], None]


def _provider_metadata(
    deps: SupervisorRunFlowDeps,
    settings: Any,
    *,
    used_llm: bool = False,
    llm_stages: list[str] | None = None,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    payload = {
        "provider": deps.resolve_llm_provider(settings),
        "model": deps.effective_llm_model_name(settings),
    }
    normalized_llm_stages = [str(item).strip() for item in (llm_stages or []) if str(item).strip()]
    if used_llm:
        payload["used_llm"] = True
    if normalized_llm_stages:
        payload["llm_stages"] = normalized_llm_stages
    payload.update(extra or {})
    return payload


def _llm_forced_mode(request: SpecialistSupervisorRequest) -> bool:
    return bool((request.debug_options or {}).get('llm_forced_mode'))


async def _persist_and_dump(
    deps: SupervisorRunFlowDeps,
    context: Any,
    *,
    answer: SupervisorAnswerPayload,
    route: str,
    metadata: dict[str, Any] | None = None,
    trace_payload: tuple[Any, Any, Any] | None = None,
    repair_payload: tuple[Any, Any] | None = None,
    timeout_seconds: float | None = None,
) -> dict[str, Any]:
    if metadata is not None:
        metadata = dict(metadata)
        answer_used_llm = bool(metadata['used_llm']) if 'used_llm' in metadata else bool(getattr(answer, 'used_llm', False))
        answer_llm_stages = [
            str(item).strip()
            for item in (metadata['llm_stages'] if 'llm_stages' in metadata else getattr(answer, 'llm_stages', []))
            if str(item).strip()
        ]
        answer = answer.model_copy(update={
            'used_llm': answer_used_llm,
            'llm_stages': list(dict.fromkeys(answer_llm_stages)),
            'final_polish_eligible': bool(metadata['final_polish_eligible']) if 'final_polish_eligible' in metadata else bool(getattr(answer, 'final_polish_eligible', False)),
            'final_polish_applied': bool(metadata['final_polish_applied']) if 'final_polish_applied' in metadata else bool(getattr(answer, 'final_polish_applied', False)),
            'final_polish_mode': str(metadata['final_polish_mode']) if 'final_polish_mode' in metadata else (getattr(answer, 'final_polish_mode', None) or 'skip'),
            'final_polish_reason': str(metadata['final_polish_reason']) if 'final_polish_reason' in metadata else (getattr(answer, 'final_polish_reason', None) or 'quality_first_path'),
            'final_polish_changed_text': bool(metadata['final_polish_changed_text']) if 'final_polish_changed_text' in metadata else bool(getattr(answer, 'final_polish_changed_text', False)),
            'final_polish_preserved_fallback': bool(metadata['final_polish_preserved_fallback']) if 'final_polish_preserved_fallback' in metadata else bool(getattr(answer, 'final_polish_preserved_fallback', False)),
        })
    else:
        answer = answer.model_copy(update={
            'final_polish_eligible': bool(getattr(answer, 'final_polish_eligible', False)),
            'final_polish_applied': bool(getattr(answer, 'final_polish_applied', False)),
            'final_polish_mode': getattr(answer, 'final_polish_mode', None) or 'skip',
            'final_polish_reason': getattr(answer, 'final_polish_reason', None) or 'quality_first_path',
            'final_polish_changed_text': bool(getattr(answer, 'final_polish_changed_text', False)),
            'final_polish_preserved_fallback': bool(getattr(answer, 'final_polish_preserved_fallback', False)),
        })
    await deps.persist_final_answer(
        context,
        answer=answer,
        route=route,
        metadata=metadata,
        trace_payload=trace_payload,
        repair_payload=repair_payload,
        timeout_seconds=timeout_seconds,
    )
    return SpecialistSupervisorResponse(
        reason=answer.reason,
        metadata=metadata or {},
        answer=answer,
    ).model_dump(mode="json")


async def run_specialist_supervisor(
    *,
    request: SpecialistSupervisorRequest,
    settings: Any,
    deps: SupervisorRunFlowDeps,
) -> dict[str, Any]:
    async with httpx.AsyncClient(
        timeout=httpx.Timeout(15.0, connect=2.5),
        limits=httpx.Limits(max_keepalive_connections=20, max_connections=40, keepalive_expiry=30.0),
    ) as client:
        context = deps.run_context_cls(
            request=request,
            settings=settings,
            http_client=client,
            actor=None,
            conversation_context=None,
            operational_memory=None,
            retrieval_advice=None,
            school_profile=None,
            preview_hint=None,
            resolved_turn=None,
            specialist_registry=deps.get_specialist_registry(),
        )

        llm_forced_mode = _llm_forced_mode(request)

        preflight_answer = None if llm_forced_mode else deps.preflight_public_doc_bundle_answer(None, request.message)
        if preflight_answer is not None:
            metadata = _provider_metadata(
                deps,
                settings,
                extra={"preflight_public_doc_bundle": True},
            )
            return await _persist_and_dump(
                deps,
                context,
                answer=preflight_answer,
                route="preflight_public_doc_bundle",
                metadata=metadata | {"preview_hint": None},
                timeout_seconds=1.0,
            )

        if deps.looks_like_internal_document_query(context.request.message):
            context.actor, context.conversation_context = await asyncio.gather(
                deps.fetch_actor_context(context),
                deps.fetch_conversation_context(context),
            )
            context.operational_memory = deps.load_operational_memory(context.conversation_context)
            context.resolved_turn = deps.resolve_turn_intent(context)
            internal_tool_answer = await deps.tool_first_structured_answer(context)
            if internal_tool_answer is not None:
                return await _persist_and_dump(
                    deps,
                    context,
                    answer=internal_tool_answer,
                    route="tool_first_restricted_document",
                    metadata=_provider_metadata(
                        deps,
                        settings,
                        extra={
                            "tool_first": True,
                            "preview_hint": None,
                            "restricted_document_short_circuit": True,
                        },
                    ),
                )

        (
            context.actor,
            context.conversation_context,
            context.school_profile,
            context.preview_hint,
        ) = await asyncio.gather(
            deps.fetch_actor_context(context),
            deps.fetch_conversation_context(context),
            deps.fetch_public_school_profile(context),
            deps.orchestrator_preview(context),
        )
        context.operational_memory = deps.load_operational_memory(context.conversation_context)
        context.resolved_turn = deps.resolve_turn_intent(context)

        teacher_fast_answer = await deps.teacher_scope_fast_path_answer(context)
        if teacher_fast_answer is not None:
            return await _persist_and_dump(
                deps,
                context,
                answer=teacher_fast_answer,
                route="teacher_fast_path",
                metadata=_provider_metadata(
                    deps,
                    settings,
                    extra={"teacher_fast_path": True, "preview_hint": context.preview_hint or {}},
                ),
            )

        academic_fast_answer = await deps.academic_grade_fast_path_answer(context)
        if academic_fast_answer is not None:
            return await _persist_and_dump(
                deps,
                context,
                answer=academic_fast_answer,
                route="academic_fast_path",
                metadata=_provider_metadata(
                    deps,
                    settings,
                    extra={"fast_path": True, "preview_hint": context.preview_hint or {}},
                ),
            )

        if context.request.user.authenticated and deps.looks_like_third_party_student_data_request(context.request.message):
            answer = deps.build_third_party_student_data_denial()
            return await _persist_and_dump(
                deps,
                context,
                answer=answer,
                route="third_party_student_data_guardrail",
                metadata=_provider_metadata(
                    deps,
                    settings,
                    extra={"guardrail": True, "preview_hint": context.preview_hint or {}},
                ),
            )

        memory_follow_up_answer = await deps.operational_memory_follow_up_answer(context)
        if memory_follow_up_answer is not None:
            return await _persist_and_dump(
                deps,
                context,
                answer=memory_follow_up_answer,
                route="operational_memory",
                metadata=_provider_metadata(
                    deps,
                    settings,
                    extra={"operational_memory": True, "preview_hint": context.preview_hint or {}},
                ),
            )

        fast_answer = None if llm_forced_mode and not context.request.user.authenticated else deps.fast_path_answer(context)
        if fast_answer is not None:
            semantic_ingress_payload = (
                context.preview_hint.get("semantic_ingress")
                if isinstance(context.preview_hint, dict)
                else None
            )
            semantic_ingress_used = isinstance(semantic_ingress_payload, dict)
            semantic_ingress_act = (
                str(semantic_ingress_payload.get("conversation_act") or "").strip()
                if semantic_ingress_used
                else ""
            )
            return await _persist_and_dump(
                deps,
                context,
                answer=fast_answer,
                route="fast_path",
                metadata=_provider_metadata(
                    deps,
                    settings,
                    used_llm=semantic_ingress_used,
                    llm_stages=["semantic_ingress_classifier"] if semantic_ingress_used else None,
                    extra={"fast_path": True, "preview_hint": context.preview_hint or {}},
                )
                | (
                    {"semantic_ingress_act": semantic_ingress_act}
                    if semantic_ingress_act
                    else {}
                ),
            )

        if deps.looks_like_internal_document_query(context.request.message):
            internal_tool_answer = await deps.tool_first_structured_answer(context)
            if internal_tool_answer is not None:
                return await _persist_and_dump(
                    deps,
                    context,
                    answer=internal_tool_answer,
                    route="tool_first",
                    metadata=_provider_metadata(
                        deps,
                        settings,
                        extra={"tool_first": True, "preview_hint": context.preview_hint or {}},
                    ),
                )

        resolved_intent_answer = None if llm_forced_mode and not context.request.user.authenticated else await deps.resolved_intent_answer(context)
        if resolved_intent_answer is not None:
            return await _persist_and_dump(
                deps,
                context,
                answer=resolved_intent_answer,
                route="resolved_intent",
                metadata=_provider_metadata(
                    deps,
                    settings,
                    extra={
                        "resolved_intent": True,
                        "preview_hint": context.preview_hint or {},
                        "resolved_turn": context.resolved_turn.model_dump(mode="json") if context.resolved_turn is not None else None,
                    },
                ),
            )

        tool_first_answer = await deps.tool_first_structured_answer(context)
        if tool_first_answer is not None:
            return await _persist_and_dump(
                deps,
                context,
                answer=tool_first_answer,
                route="tool_first",
                metadata=_provider_metadata(
                    deps,
                    settings,
                    extra={"tool_first": True, "preview_hint": context.preview_hint or {}},
                ),
            )

        general_knowledge_answer = None if llm_forced_mode and not context.request.user.authenticated else await deps.general_knowledge_fast_path_answer(context)
        if general_knowledge_answer is not None:
            return await _persist_and_dump(
                deps,
                context,
                answer=general_knowledge_answer,
                route="general_knowledge_fast_path",
                metadata=_provider_metadata(
                    deps,
                    settings,
                    extra={"fast_path": True, "preview_hint": context.preview_hint or {}},
                ),
            )

        if deps.resolve_llm_provider(settings) == "unconfigured":
            answer = SupervisorAnswerPayload(
                message_text="O caminho specialist_supervisor ainda nao esta com um provider LLM configurado neste ambiente.",
                mode="clarify",
                classification=MessageIntentClassification(
                    domain="institution",
                    access_tier="public",
                    confidence=1.0,
                    reason="specialist_supervisor_llm_unconfigured",
                ),
                suggested_replies=deps.default_suggested_replies("institution"),
                graph_path=["specialist_supervisor", "bootstrap"],
                risk_flags=["llm_unconfigured"],
                reason="specialist_supervisor_llm_unconfigured",
            )
            return await _persist_and_dump(
                deps,
                context,
                answer=answer,
                route="bootstrap_unconfigured",
                metadata=_provider_metadata(deps, settings),
            )

        guardrail = await deps.run_input_guardrail_stage(context)
        if guardrail.blocked:
            answer = SupervisorAnswerPayload(
                message_text=guardrail.safe_reply or "Nao posso ajudar com esse pedido.",
                mode="deny",
                classification=MessageIntentClassification(
                    domain="institution",
                    access_tier="public",
                    confidence=1.0,
                    reason=guardrail.reason or "input_guardrail_blocked",
                ),
                reason=guardrail.reason or "input_guardrail_blocked",
                graph_path=["specialist_supervisor", "input_guardrail"],
                risk_flags=["input_guardrail_blocked"],
            )
            return await _persist_and_dump(
                deps,
                context,
                answer=answer,
                route="input_guardrail",
                metadata=_provider_metadata(deps, settings, used_llm=True, llm_stages=['input_guardrail'], extra={"blocked": True}),
            )

        try:
            await deps.run_retrieval_planner_stage(context)
        except Exception:
            pass

        try:
            plan, execution_budget = await deps.resolve_plan_and_budget(context)
            context.execution_budget = execution_budget
            deps.log_execution_budget(plan, execution_budget)
        except Exception:
            answer = deps.safe_supervisor_fallback_answer(
                preview_hint=context.preview_hint,
                authenticated=context.request.user.authenticated,
                reason="specialist_supervisor_planner_safe_fallback",
            )
            return await _persist_and_dump(
                deps,
                context,
                answer=answer,
                route="planner_safe_fallback",
                metadata={"fallback": True},
            )

        plan_metadata = {
            "retrieval_advice": context.retrieval_advice.model_dump(mode="json") if context.retrieval_advice is not None else {},
            "plan": plan.model_dump(mode="json"),
            "preview_hint": context.preview_hint or {},
            **deps.execution_budget_metadata(plan, execution_budget),
        }
        observed_plan_metadata = deps.metadata_with_runtime_observability(context, plan_metadata)

        if plan.should_deny:
            answer = SupervisorAnswerPayload(
                message_text=plan.denial_reason or "Nao consigo atender esse pedido neste contexto.",
                mode="deny",
                classification=MessageIntentClassification(
                    domain=plan.primary_domain,
                    access_tier=deps.access_tier_for_domain(plan.primary_domain, context.request.user.authenticated),
                    confidence=plan.confidence,
                    reason=plan.reasoning_summary,
                ),
                reason=plan.reasoning_summary,
                graph_path=["specialist_supervisor", "planner"],
                risk_flags=["planner_denied"],
            )
            return await _persist_and_dump(
                deps,
                context,
                answer=answer,
                route="planner_denied",
                metadata={**observed_plan_metadata, 'used_llm': True, 'llm_stages': ['planner']},
            )

        if plan.requires_clarification and plan.clarification_question:
            answer = SupervisorAnswerPayload(
                message_text=plan.clarification_question,
                mode="clarify",
                classification=MessageIntentClassification(
                    domain=plan.primary_domain,
                    access_tier=deps.access_tier_for_domain(plan.primary_domain, context.request.user.authenticated),
                    confidence=plan.confidence,
                    reason=plan.reasoning_summary,
                ),
                reason=plan.reasoning_summary,
                graph_path=["specialist_supervisor", "planner"],
                suggested_replies=deps.default_suggested_replies(plan.primary_domain),
                risk_flags=["clarification_required"],
            )
            return await _persist_and_dump(
                deps,
                context,
                answer=answer,
                route="planner_clarify",
                metadata={**observed_plan_metadata, 'used_llm': True, 'llm_stages': ['planner']},
            )

        try:
            execution_specialists = deps.build_budgeted_execution_specialists(
                context.settings,
                model=deps.agent_model_for_role(context.settings, role="specialist"),
            )
            precomputed_specialist_results = await deps.execute_budgeted_specialists(
                context,
                plan=plan,
                budget=execution_budget,
                specialists=execution_specialists,
            )
            specialists_used = [item.specialist_id for item in precomputed_specialist_results]
            direct_metadata = {**plan_metadata, "specialists_used": specialists_used}
            observed_direct_metadata = deps.metadata_with_runtime_observability(context, direct_metadata)

            multi_direct_answer = None
            direct_result = None
            if execution_budget.prefer_direct_answer:
                multi_direct_answer = deps.build_multi_specialist_answer_from_results(
                    context,
                    plan=plan,
                    specialist_results=precomputed_specialist_results,
                )
                if multi_direct_answer is not None:
                    return await _persist_and_dump(
                        deps,
                        context,
                        answer=multi_direct_answer,
                        route="multi_specialist_direct",
                        metadata={**observed_direct_metadata, 'used_llm': True, 'llm_stages': ['specialist_execution']},
                    )
                direct_result = deps.direct_compose_candidate(
                    context,
                    plan=plan,
                    specialist_results=precomputed_specialist_results,
                )
                if direct_result is not None:
                    answer = deps.build_direct_answer_from_specialist(context, plan=plan, result=direct_result)
                    return await _persist_and_dump(
                        deps,
                        context,
                        answer=answer,
                        route="specialist_direct",
                        metadata={**observed_direct_metadata, 'used_llm': True, 'llm_stages': ['specialist_execution']},
                    )

            requires_manager = deps.needs_manager(
                plan=plan,
                budget=execution_budget,
                specialist_results=precomputed_specialist_results,
            )
            if not requires_manager:
                multi_direct_answer = multi_direct_answer or deps.build_multi_specialist_answer_from_results(
                    context,
                    plan=plan,
                    specialist_results=precomputed_specialist_results,
                )
                if multi_direct_answer is not None:
                    return await _persist_and_dump(
                        deps,
                        context,
                        answer=multi_direct_answer,
                        route="multi_specialist_direct",
                        metadata={**observed_direct_metadata, 'used_llm': True, 'llm_stages': ['specialist_execution']},
                    )
                direct_result = direct_result or deps.direct_compose_candidate(
                    context,
                    plan=plan,
                    specialist_results=precomputed_specialist_results,
                )
                if direct_result is not None:
                    answer = deps.build_direct_answer_from_specialist(context, plan=plan, result=direct_result)
                    return await _persist_and_dump(
                        deps,
                        context,
                        answer=answer,
                        route="specialist_direct",
                        metadata={**observed_direct_metadata, 'used_llm': True, 'llm_stages': ['specialist_execution']},
                    )
                budgeted_result = deps.budgeted_no_manager_candidate(
                    context,
                    specialist_results=precomputed_specialist_results,
                )
                if budgeted_result is not None:
                    answer = deps.build_direct_answer_from_specialist(context, plan=plan, result=budgeted_result)
                    answer = answer.model_copy(
                        update={
                            "graph_path": ["specialist_supervisor", "retrieval_planner", "budget_direct", budgeted_result.specialist_id],
                            "risk_flags": [*answer.risk_flags, "budget_degraded"],
                            "reason": f"specialist_supervisor_budget_direct:{budgeted_result.specialist_id}",
                        }
                    )
                    return await _persist_and_dump(
                        deps,
                        context,
                        answer=answer,
                        route="budget_direct",
                        metadata={**observed_direct_metadata, 'used_llm': True, 'llm_stages': ['specialist_execution']},
                    )
                answer = deps.safe_supervisor_fallback_answer(
                    preview_hint=context.preview_hint,
                    authenticated=context.request.user.authenticated,
                    reason="specialist_supervisor_budget_safe_fallback",
                )
                return await _persist_and_dump(
                    deps,
                    context,
                    answer=answer,
                    route="budget_safe_fallback",
                    metadata=deps.metadata_with_runtime_observability(context, {**direct_metadata, "fallback": True, 'used_llm': True, 'llm_stages': ['specialist_execution']}),
                )

            draft, judge, repair_payload = await deps.run_manager_stack(
                context,
                plan=plan,
                budget=execution_budget,
                specialists=execution_specialists,
                precomputed_specialist_results=precomputed_specialist_results,
            )
            specialist_results = deps.merge_specialist_results(
                precomputed_specialist_results,
                deps.parse_specialist_results(context.trace),
            )
            gated_answer = deps.grounding_gate_answer(
                authenticated=context.request.user.authenticated,
                plan=plan,
                judge=judge,
                specialist_results=specialist_results,
            )
            answer = gated_answer or deps.build_answer_payload(
                authenticated=context.request.user.authenticated,
                plan=plan,
                draft=draft,
                judge=judge,
                specialist_results=specialist_results,
            )
        except Exception:
            answer = deps.safe_supervisor_fallback_answer(
                preview_hint=context.preview_hint,
                authenticated=context.request.user.authenticated,
                reason="specialist_supervisor_manager_safe_fallback",
            )
            return await _persist_and_dump(
                deps,
                context,
                answer=answer,
                route="manager_safe_fallback",
                metadata=deps.metadata_with_runtime_observability(context, {**plan_metadata, "fallback": True}),
            )

        final_metadata = deps.metadata_with_runtime_observability(
            context,
            {
                **plan_metadata,
                "judge": judge.model_dump(mode="json"),
                "specialists_used": [item.specialist_id for item in specialist_results],
            },
        )
        return await _persist_and_dump(
            deps,
            context,
            answer=answer,
            route="manager_judge",
            metadata={**final_metadata, 'used_llm': True, 'llm_stages': ['planner', 'specialist_execution', 'manager_judge']},
            trace_payload=(plan, draft, judge),
            repair_payload=repair_payload,
        )
