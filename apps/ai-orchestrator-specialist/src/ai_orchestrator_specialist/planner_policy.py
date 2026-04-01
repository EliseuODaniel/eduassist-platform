from __future__ import annotations

import json
from typing import Any

from agents import Agent, ModelSettings, Runner

from .execution_budget import derive_execution_budget
from .models import ExecutionBudget, RetrievalPlannerAdvice, SupervisorPlan


def deterministic_plan_from_retrieval_advice(ctx: Any) -> SupervisorPlan | None:
    from .runtime import _normalize_plan_with_retrieval_advice

    advice = ctx.retrieval_advice
    if advice is None:
        return None
    specialists = [item for item in advice.recommended_specialists if item in ctx.specialist_registry]
    if not specialists and advice.retrieval_strategy not in {"clarify", "deny"}:
        return None
    normalized_plan = _normalize_plan_with_retrieval_advice(
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
    from .runtime import (
        _agent_model_for_role,
        _effective_conversation_id,
        _fallback_specialists_for_domain,
        _normalize_retrieval_advice,
        _preview_classification_dict,
        _retrieval_planner_instructions,
        _run_config,
        logger,
    )

    agent = Agent(
        name="Retrieval Planner Specialist",
        model=_agent_model_for_role(ctx.settings, role="planner"),
        model_settings=ModelSettings(temperature=0.0, verbosity="low"),
        instructions=_retrieval_planner_instructions,
        output_type=RetrievalPlannerAdvice,
    )
    try:
        result = await Runner.run(
            agent,
            f"Mensagem do usuario: {ctx.request.message}",
            context=ctx,
            max_turns=3,
            run_config=_run_config(ctx.settings, conversation_id=_effective_conversation_id(ctx.request)),
        )
        advice = result.final_output_as(RetrievalPlannerAdvice, raise_if_incorrect_type=True)
    except Exception:
        logger.exception("specialist_supervisor_retrieval_planner_failed")
        preview = ctx.preview_hint or {}
        classification = _preview_classification_dict(ctx.preview_hint)
        domain = str(classification.get("domain") or "institution").strip().lower() or "institution"
        retrieval_backend = str(preview.get("retrieval_backend") or "none").strip().lower()
        specialists, strategy = _fallback_specialists_for_domain(domain, retrieval_backend)
        advice = RetrievalPlannerAdvice(
            normalized_query=ctx.request.message.strip(),
            primary_domain=domain,
            retrieval_strategy=strategy,
            recommended_specialists=specialists,
            preferred_category=None,
            evidence_queries=[ctx.request.message.strip()],
            requires_grounding=strategy != "direct_answer",
            rationale="retrieval_planner_fallback_from_preview_hint",
            confidence=0.35,
        )
    normalized = _normalize_retrieval_advice(ctx, advice)
    ctx.retrieval_advice = normalized
    return normalized


async def run_planner(ctx: Any) -> SupervisorPlan:
    from .runtime import (
        _agent_model_for_role,
        _effective_conversation_id,
        _fallback_specialists_for_domain,
        _normalize_plan_with_retrieval_advice,
        _planner_instructions,
        _preview_classification_dict,
        _run_config,
        logger,
    )

    agent = Agent(
        name="Retrieval Planner",
        model=_agent_model_for_role(ctx.settings, role="planner"),
        model_settings=ModelSettings(temperature=0.0, verbosity="low"),
        instructions=_planner_instructions,
        output_type=SupervisorPlan,
    )
    try:
        result = await Runner.run(
            agent,
            f"Mensagem do usuario: {ctx.request.message}",
            context=ctx,
            max_turns=3,
            run_config=_run_config(ctx.settings, conversation_id=_effective_conversation_id(ctx.request)),
        )
        plan = result.final_output_as(SupervisorPlan, raise_if_incorrect_type=True)
    except Exception:
        logger.exception("specialist_supervisor_planner_failed")
        advice = ctx.retrieval_advice
        if advice is not None:
            specialists = [item for item in advice.recommended_specialists if item in ctx.specialist_registry]
            strategy = advice.retrieval_strategy
            domain = advice.primary_domain
        else:
            preview = ctx.preview_hint or {}
            classification = _preview_classification_dict(ctx.preview_hint)
            domain = str(classification.get("domain") or "institution").strip().lower() or "institution"
            retrieval_backend = str(preview.get("retrieval_backend") or "none").strip().lower()
            specialists, strategy = _fallback_specialists_for_domain(domain, retrieval_backend)
        plan = SupervisorPlan(
            request_kind="multi_domain" if advice is not None and advice.secondary_domains else "simple",
            primary_domain=domain,
            secondary_domains=advice.secondary_domains if advice is not None else [],
            specialists=specialists,
            retrieval_strategy=strategy,
            requires_clarification=bool(advice.requires_clarification) if advice is not None else False,
            clarification_question=advice.clarification_question if advice is not None else None,
            should_deny=bool(advice.should_deny) if advice is not None else False,
            denial_reason=advice.denial_reason if advice is not None else None,
            reasoning_summary=advice.rationale if advice is not None and advice.rationale else "planner_fallback_from_preview_hint",
            confidence=advice.confidence if advice is not None else 0.35,
        )
    return _normalize_plan_with_retrieval_advice(ctx, plan, ctx.retrieval_advice)


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
