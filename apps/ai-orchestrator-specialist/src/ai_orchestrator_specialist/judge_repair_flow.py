from __future__ import annotations

import json
from time import monotonic
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
    from .runtime import _agent_model_for_role, _build_judge_agent, _effective_conversation_id, _record_stage_timing, _run_config

    started = monotonic()
    judge = _build_judge_agent(_agent_model_for_role(ctx.settings, role="judge"))
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
    verdict = result.final_output_as(JudgeVerdict, raise_if_incorrect_type=True)
    _record_stage_timing(ctx, "judge", (monotonic() - started) * 1000.0)
    return verdict


async def run_repair_loop(
    ctx: SupervisorRunContext,
    *,
    plan: SupervisorPlan,
    draft: ManagerDraft,
    judge: JudgeVerdict,
    specialist_results: list[SpecialistResult],
) -> tuple[ManagerDraft, JudgeVerdict, RepairDraft] | None:
    from .runtime import _agent_model_for_role, _build_repair_agent, _effective_conversation_id, _parse_result_model, _record_stage_timing, _run_config

    if not specialist_results:
        return None
    repair_needed = (not judge.approved) or bool(judge.issues)
    if not repair_needed or judge.needs_clarification:
        return None
    started = monotonic()
    repair_agent = _build_repair_agent(ctx.settings, _agent_model_for_role(ctx.settings, role="repair"))
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
    _record_stage_timing(ctx, "repair", (monotonic() - started) * 1000.0)
    return repaired_draft, repaired_judge, repair
