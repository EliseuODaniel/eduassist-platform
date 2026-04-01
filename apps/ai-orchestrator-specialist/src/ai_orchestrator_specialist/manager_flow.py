from __future__ import annotations

from typing import Any

from agents import Agent, ModelSettings, Runner

from .evidence_kernel import build_manager_prompt
from .execution_budget import should_run_judge, should_run_repair, should_use_manager
from .models import ExecutionBudget, JudgeVerdict, ManagerDraft, RepairDraft, SpecialistResult, SupervisorPlan
from .session_memory import build_supervisor_session


def _build_manager_agent(*, settings: Any, model: Any, plan: SupervisorPlan, specialist_tools: list[Any]) -> Agent[Any]:
    from .runtime import _manager_instructions, _manager_result_contract, _supports_tool_json_outputs, _tool_model_settings

    structured = _supports_tool_json_outputs(settings)
    return Agent(
        name="Specialist Supervisor Manager",
        model=model,
        tools=specialist_tools,
        model_settings=_tool_model_settings(settings),
        instructions=_manager_instructions(plan) + ("\n" + _manager_result_contract() if not structured else ""),
        output_type=ManagerDraft if structured else None,
    )


def _build_judge_agent(model: Any) -> Agent[Any]:
    from .runtime import _judge_instructions

    return Agent(
        name="Judge Specialist",
        model=model,
        model_settings=ModelSettings(temperature=0.0, verbosity="low"),
        instructions=_judge_instructions(),
        output_type=JudgeVerdict,
    )


def _build_repair_agent(settings: Any, model: Any) -> Agent[Any]:
    from .runtime import _repair_instructions, _repair_result_contract, _supports_tool_json_outputs

    structured = _supports_tool_json_outputs(settings)
    return Agent(
        name="Repair Specialist",
        model=model,
        model_settings=ModelSettings(temperature=0.0, verbosity="low"),
        instructions=_repair_instructions() + ("\n" + _repair_result_contract() if not structured else ""),
        output_type=RepairDraft if structured else None,
    )


def synthesize_approved_judge(
    *,
    plan: SupervisorPlan,
    draft: ManagerDraft,
    specialist_results: list[SpecialistResult],
    reason: str,
) -> JudgeVerdict:
    confidence = max([plan.confidence, *[item.confidence for item in specialist_results]], default=plan.confidence)
    return JudgeVerdict(
        approved=True,
        revised_answer_text=None,
        needs_clarification=False,
        clarification_question=None,
        grounding_score=min(1.0, max(0.75, confidence)),
        completeness_score=0.92 if str(draft.answer_text or "").strip() else 0.4,
        issues=[],
        recommended_replies=list(draft.suggested_replies or [])[:4],
        rationale=reason,
    )


async def run_manager(
    ctx: Any,
    *,
    plan: SupervisorPlan,
    budget: ExecutionBudget,
    specialists: dict[str, Agent[Any]],
    precomputed_specialist_results: list[SpecialistResult] | None = None,
) -> ManagerDraft:
    from .runtime import (
        SupervisorHooks,
        _agent_model_for_role,
        _effective_conversation_id,
        _parse_result_model,
        _run_config,
        logger,
    )

    specialist_tools = []
    for specialist_id, agent in specialists.items():
        specialist_tools.append(
            agent.as_tool(
                tool_name=specialist_id,
                tool_description=ctx.specialist_registry[specialist_id].description,
                custom_output_extractor=_specialist_output_extractor(),
            )
        )
    manager = _build_manager_agent(
        settings=ctx.settings,
        model=_agent_model_for_role(ctx.settings, role="manager"),
        plan=plan,
        specialist_tools=specialist_tools,
    )
    session = None
    if budget.allow_session_memory:
        try:
            session = build_supervisor_session(
                conversation_id=_effective_conversation_id(ctx.request),
                agent_memory_url=getattr(ctx.settings, "agent_memory_url", ctx.settings.database_url),
                preferred_dir=getattr(ctx.settings, "agent_memory_dir", None),
            )
        except Exception as exc:
            logger.warning("specialist_session_memory_unavailable: %s", exc)
            session = None
    try:
        result = await Runner.run(
            manager,
            build_manager_prompt(ctx, plan=plan, precomputed_specialist_results=precomputed_specialist_results),
            context=ctx,
            max_turns=budget.manager_max_turns,
            hooks=SupervisorHooks(),
            session=session,
            run_config=_run_config(ctx.settings, conversation_id=_effective_conversation_id(ctx.request)),
        )
    except Exception as exc:
        if session is None:
            raise
        logger.warning("specialist_session_memory_runtime_unavailable: %s", exc)
        result = await Runner.run(
            manager,
            build_manager_prompt(ctx, plan=plan, precomputed_specialist_results=precomputed_specialist_results),
            context=ctx,
            max_turns=budget.manager_max_turns,
            hooks=SupervisorHooks(),
            session=None,
            run_config=_run_config(ctx.settings, conversation_id=_effective_conversation_id(ctx.request)),
        )
    return _parse_result_model(result, ManagerDraft)


async def run_manager_stack(
    ctx: Any,
    *,
    plan: SupervisorPlan,
    budget: ExecutionBudget,
    specialists: dict[str, Agent[Any]],
    precomputed_specialist_results: list[SpecialistResult],
) -> tuple[ManagerDraft, JudgeVerdict, tuple[RepairDraft, JudgeVerdict] | None]:
    from .judge_repair_flow import run_judge, run_repair_loop

    draft = await run_manager(
        ctx,
        plan=plan,
        budget=budget,
        specialists=specialists,
        precomputed_specialist_results=precomputed_specialist_results,
    )
    if not should_run_judge(plan, budget, precomputed_specialist_results):
        judge = synthesize_approved_judge(
            plan=plan,
            draft=draft,
            specialist_results=precomputed_specialist_results,
            reason="budgeted_skip_judge",
        )
        return draft, judge, None
    judge = await run_judge(
        ctx,
        plan=plan,
        draft=draft,
        specialist_results=precomputed_specialist_results,
    )
    repair_payload: tuple[RepairDraft, JudgeVerdict] | None = None
    if should_run_repair(plan, budget):
        repaired = await run_repair_loop(
            ctx,
            plan=plan,
            draft=draft,
            judge=judge,
            specialist_results=precomputed_specialist_results,
        )
        if repaired is not None:
            draft, judge, repair = repaired
            repair_payload = (repair, judge)
    return draft, judge, repair_payload


def needs_manager(
    *,
    plan: SupervisorPlan,
    budget: ExecutionBudget,
    specialist_results: list[SpecialistResult],
) -> bool:
    return should_use_manager(plan, budget, specialist_results)


def _specialist_output_extractor() -> Any:
    async def _extract(result: Any) -> str:
        from .runtime import _parse_result_model

        try:
            payload = _parse_result_model(result, SpecialistResult)
            return payload.model_dump_json(ensure_ascii=False)
        except Exception:
            final_output = getattr(result, "final_output", "")
            return final_output if isinstance(final_output, str) else str(final_output)

    return _extract
