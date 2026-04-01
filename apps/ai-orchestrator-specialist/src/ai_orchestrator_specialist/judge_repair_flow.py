from __future__ import annotations

import json
from typing import TYPE_CHECKING

from agents import Runner

from .models import JudgeVerdict, ManagerDraft, RepairDraft, SpecialistResult, SupervisorPlan

if TYPE_CHECKING:
    from .runtime import SupervisorRunContext


async def run_judge(
    ctx: SupervisorRunContext,
    *,
    plan: SupervisorPlan,
    draft: ManagerDraft,
    specialist_results: list[SpecialistResult],
) -> JudgeVerdict:
    from .runtime import _agent_model, _build_judge_agent, _effective_conversation_id, _run_config

    judge = _build_judge_agent(_agent_model(ctx.settings))
    prompt = json.dumps(
        {
            "user_message": ctx.request.message,
            "retrieval_advice": ctx.retrieval_advice.model_dump(mode="json") if ctx.retrieval_advice is not None else {},
            "plan": plan.model_dump(mode="json"),
            "operational_memory": ctx.operational_memory.model_dump(mode="json") if ctx.operational_memory is not None else {},
            "manager_draft": draft.model_dump(mode="json"),
            "specialist_results": [item.model_dump(mode="json") for item in specialist_results],
        },
        ensure_ascii=False,
    )
    result = await Runner.run(
        judge,
        prompt,
        context=ctx,
        max_turns=4,
        run_config=_run_config(ctx.settings, conversation_id=_effective_conversation_id(ctx.request)),
    )
    return result.final_output_as(JudgeVerdict, raise_if_incorrect_type=True)


async def run_repair_loop(
    ctx: SupervisorRunContext,
    *,
    plan: SupervisorPlan,
    draft: ManagerDraft,
    judge: JudgeVerdict,
    specialist_results: list[SpecialistResult],
) -> tuple[ManagerDraft, JudgeVerdict, RepairDraft] | None:
    from .runtime import _agent_model, _build_repair_agent, _parse_result_model

    if not specialist_results:
        return None
    repair_needed = (not judge.approved) or bool(judge.issues)
    if not repair_needed or judge.needs_clarification:
        return None
    repair_agent = _build_repair_agent(ctx.settings, _agent_model(ctx.settings))
    prompt = json.dumps(
        {
            "user_message": ctx.request.message,
            "retrieval_advice": ctx.retrieval_advice.model_dump(mode="json") if ctx.retrieval_advice is not None else {},
            "plan": plan.model_dump(mode="json"),
            "manager_draft": draft.model_dump(mode="json"),
            "judge_feedback": judge.model_dump(mode="json"),
            "specialist_results": [item.model_dump(mode="json") for item in specialist_results],
        },
        ensure_ascii=False,
    )
    result = await Runner.run(
        repair_agent,
        prompt,
        context=ctx,
        max_turns=4,
        run_config=_run_config(ctx.settings, conversation_id=_effective_conversation_id(ctx.request)),
    )
    repair = _parse_result_model(result, RepairDraft)
    repaired_draft = ManagerDraft(
        answer_text=repair.answer_text,
        answer_summary=repair.answer_summary,
        specialists_used=repair.specialists_used or draft.specialists_used,
        citations=repair.citations or draft.citations,
        suggested_replies=repair.suggested_replies or draft.suggested_replies,
    )
    repaired_judge = await run_judge(
        ctx,
        plan=plan,
        draft=repaired_draft,
        specialist_results=specialist_results,
    )
    return repaired_draft, repaired_judge, repair
