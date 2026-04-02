from __future__ import annotations

import json
from time import monotonic
from typing import Any

from .execution_budget import derive_execution_budget
from .llm_runtime import agent_model_for_role, run_config
from .models import ExecutionBudget, RetrievalPlannerAdvice, SupervisorPlan
from .planner_support import (
    PlannerSupportDeps,
    normalize_plan_with_retrieval_advice,
    run_planner as _run_planner_module,
    run_retrieval_planner as _run_retrieval_planner_module,
)


def _planner_support_deps(ctx: Any) -> PlannerSupportDeps:
    from .runtime import (
        _effective_conversation_id,
        _effective_multi_intent_domains,
        _normalize_string_list,
        _normalize_text,
        _preview_classification_dict,
        _school_name,
        _stringify_payload_value,
    )

    return PlannerSupportDeps(
        normalize_text=_normalize_text,
        stringify_payload_value=_stringify_payload_value,
        normalize_string_list=_normalize_string_list,
        school_name=_school_name,
        preview_classification_dict=_preview_classification_dict,
        effective_multi_intent_domains=_effective_multi_intent_domains,
        run_config=run_config,
        effective_conversation_id=_effective_conversation_id,
        agent_model_for_role=agent_model_for_role,
    )


def deterministic_plan_from_retrieval_advice(ctx: Any) -> SupervisorPlan | None:
    advice = ctx.retrieval_advice
    if advice is None:
        return None
    specialists = [item for item in advice.recommended_specialists if item in ctx.specialist_registry]
    if not specialists and advice.retrieval_strategy not in {"clarify", "deny"}:
        return None
    normalized_plan = normalize_plan_with_retrieval_advice(
        ctx,
        SupervisorPlan(
            request_kind="multi_domain" if advice.secondary_domains else "simple",
            primary_domain=advice.primary_domain,
            secondary_domains=advice.secondary_domains,
            specialists=specialists,
            retrieval_strategy=advice.retrieval_strategy,
            requires_clarification=advice.requires_clarification,
            clarification_question=advice.clarification_question,
            should_deny=advice.should_deny,
            denial_reason=advice.denial_reason,
            reasoning_summary=advice.rationale or "deterministic_plan_from_retrieval_advice",
            confidence=advice.confidence,
        ),
        advice,
        deps=_planner_support_deps(ctx),
        execution_specialists=set(ctx.specialist_registry),
    )
    if normalized_plan.should_deny or normalized_plan.requires_clarification:
        return normalized_plan
    if normalized_plan.request_kind == "multi_domain":
        return normalized_plan
    if normalized_plan.specialists:
        return normalized_plan
    if normalized_plan.retrieval_strategy in {
        "direct_answer",
        "structured_tools",
        "hybrid_retrieval",
        "graph_rag",
        "document_search",
        "workflow_status",
        "pricing_projection",
    } and normalized_plan.confidence >= 0.8:
        return normalized_plan
    return None


async def run_retrieval_planner(ctx: Any) -> RetrievalPlannerAdvice:
    from .runtime import _record_stage_timing, logger

    started = monotonic()
    normalized = await _run_retrieval_planner_module(
        ctx,
        deps=_planner_support_deps(ctx),
        execution_specialists=set(ctx.specialist_registry),
        logger=logger,
    )
    ctx.retrieval_advice = normalized
    _record_stage_timing(ctx, "retrieval_planner", (monotonic() - started) * 1000.0)
    return normalized


async def run_planner(ctx: Any) -> SupervisorPlan:
    from .runtime import _record_stage_timing, logger

    started = monotonic()
    normalized = await _run_planner_module(
        ctx,
        deps=_planner_support_deps(ctx),
        execution_specialists=set(ctx.specialist_registry),
        logger=logger,
    )
    _record_stage_timing(ctx, "planner", (monotonic() - started) * 1000.0)
    return normalized


async def resolve_plan_and_budget(ctx: Any) -> tuple[SupervisorPlan, ExecutionBudget]:
    deterministic = deterministic_plan_from_retrieval_advice(ctx)
    plan = deterministic if deterministic is not None else await run_planner(ctx)
    budget = derive_execution_budget(ctx, plan)
    return plan, budget


def execution_budget_metadata(plan: SupervisorPlan, budget: ExecutionBudget) -> dict[str, Any]:
    return {
        "plan_summary": {
            "primary_domain": plan.primary_domain,
            "secondary_domains": list(plan.secondary_domains),
            "strategy": plan.retrieval_strategy,
            "specialists": list(plan.specialists),
            "request_kind": plan.request_kind,
        },
        "execution_budget": json.loads(budget.model_dump_json()),
    }
