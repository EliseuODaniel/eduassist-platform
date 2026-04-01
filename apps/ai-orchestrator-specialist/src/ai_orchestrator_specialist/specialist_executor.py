from __future__ import annotations

import asyncio
import json
from typing import Any

from agents import Agent, Runner

from .evidence_kernel import build_specialist_execution_prompt
from .models import ExecutionBudget, SpecialistResult, SupervisorPlan


def build_execution_specialists(settings: Any, *, model: Any) -> dict[str, Agent[Any]]:
    from .runtime import (
        _academic_specialist,
        _document_specialist,
        _finance_specialist,
        _institution_specialist,
        _workflow_specialist,
    )

    return {
        "institution_specialist": _institution_specialist(settings, model),
        "academic_specialist": _academic_specialist(settings, model),
        "finance_specialist": _finance_specialist(settings, model),
        "workflow_specialist": _workflow_specialist(settings, model),
        "document_specialist": _document_specialist(settings, model),
    }


async def run_specialist_agent(
    ctx: Any,
    *,
    specialist_id: str,
    plan: SupervisorPlan,
    budget: ExecutionBudget,
    specialists: dict[str, Agent[Any]],
) -> SpecialistResult | None:
    from .runtime import (
        SupervisorHooks,
        _effective_conversation_id,
        _parse_result_model,
        _run_config,
    )

    agent = specialists.get(specialist_id)
    if agent is None:
        return None
    result = await Runner.run(
        agent,
        build_specialist_execution_prompt(ctx, specialist_id=specialist_id, plan=plan),
        context=ctx,
        max_turns=budget.specialist_max_turns,
        hooks=SupervisorHooks(),
        run_config=_run_config(ctx.settings, conversation_id=_effective_conversation_id(ctx.request)),
    )
    specialist_result = _parse_result_model(result, SpecialistResult)
    if specialist_result.specialist_id != specialist_id:
        specialist_result = specialist_result.model_copy(update={"specialist_id": specialist_id})
    return specialist_result


async def execute_planned_specialists(
    ctx: Any,
    *,
    plan: SupervisorPlan,
    budget: ExecutionBudget,
    specialists: dict[str, Agent[Any]] | None = None,
) -> list[SpecialistResult]:
    from .runtime import _agent_model_for_role, _sorted_specialist_ids, logger

    specialist_ids = _sorted_specialist_ids(ctx, list(plan.specialists))
    if not specialist_ids or budget.max_specialists == 0:
        return []
    selected_ids = specialist_ids[: budget.max_specialists]
    if specialists is None:
        model = _agent_model_for_role(ctx.settings, role="specialist")
        specialists = build_execution_specialists(ctx.settings, model=model)
    normalized: dict[str, SpecialistResult] = {}
    batch: list[str] = []
    for index, specialist_id in enumerate(selected_ids, start=1):
        spec = ctx.specialist_registry.get(specialist_id)
        if spec is not None and not bool(getattr(spec, "allow_precompute", True)):
            continue
        batch.append(specialist_id)
        allow_parallel = budget.allow_parallel_specialists and bool(getattr(spec, "allow_parallel", True) if spec is not None else True)
        is_last = index == len(selected_ids)
        if allow_parallel and not is_last:
            continue
        tasks = [
            run_specialist_agent(
                ctx,
                specialist_id=item,
                plan=plan,
                budget=budget,
                specialists=specialists,
            )
            for item in batch
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        for item in results:
            if isinstance(item, Exception):
                logger.exception("specialist_supervisor_specialist_execution_failed", exc_info=item)
                continue
            if isinstance(item, SpecialistResult):
                normalized[item.specialist_id] = item
        batch = []
    return list(normalized.values())
