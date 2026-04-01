from __future__ import annotations

from typing import Any

from . import runtime as rt
from .agent_kernel import KernelPlan, KernelRunResult, build_kernel_plan
from .evidence_pack import build_structured_tool_evidence_pack
from .kernel_runtime import execute_kernel_plan
from .llamaindex_native_runtime import maybe_execute_llamaindex_native_plan
from .models import (
    AccessTier,
    IntentClassification,
    MessageResponse,
    MessageResponseRequest,
    OrchestrationMode,
    QueryDomain,
    RetrievalBackend,
)
from .path_profiles import annotate_plan_for_path, get_path_execution_profile


def build_llamaindex_plan(*, request: MessageResponseRequest, settings: Any, mode: str) -> KernelPlan:
    profile = get_path_execution_profile('llamaindex')
    plan = build_kernel_plan(
        request=request,
        settings=settings,
        stack_name='llamaindex',
        mode=mode,
    )
    return annotate_plan_for_path(plan=plan, profile=profile, owner='llamaindex_path_runtime')


def _build_llamaindex_replan(request: MessageResponseRequest, settings: Any, mode: str) -> KernelPlan:
    return build_llamaindex_plan(request=request, settings=settings, mode=mode)


async def _maybe_execute_llamaindex_student_focus_fast_path(
    *,
    request: MessageResponseRequest,
    settings: Any,
    plan: KernelPlan,
    engine_mode: str,
) -> KernelRunResult | None:
    if request.telegram_chat_id is None:
        return None
    actor = await rt._fetch_actor_context(settings=settings, telegram_chat_id=request.telegram_chat_id)
    if actor is None or not rt._is_student_focus_activation_query(request.message, actor):
        return None
    student = rt._student_focus_candidate(actor, request.message)
    student_name = str((student or {}).get('full_name', '')).strip() or None
    message_text = rt._compose_student_focus_activation_answer(actor, student_name=student_name)
    if not message_text:
        return None
    effective_conversation_id = rt._effective_conversation_id(request)
    conversation_context_bundle = await rt._fetch_conversation_context(
        settings=settings,
        conversation_external_id=effective_conversation_id,
        channel=request.channel.value,
    )
    conversation_context = rt._conversation_context_payload(conversation_context_bundle)
    school_profile = await rt._fetch_public_school_profile(settings=settings)
    preview = plan.preview.model_copy(deep=True)
    preview.mode = OrchestrationMode.structured_tool
    preview.classification = IntentClassification(
        domain=QueryDomain.academic,
        access_tier=AccessTier.authenticated,
        confidence=0.97,
        reason='selecao explicita de aluno resolvida deterministicamente antes do fallback do kernel do llamaindex',
    )
    preview.selected_tools = list(dict.fromkeys([*preview.selected_tools, 'get_student_grades', 'get_student_academic_summary']))
    preview.needs_authentication = True
    suggested_replies = rt._build_suggested_replies(
        request=request,
        preview=preview,
        actor=actor,
        school_profile=school_profile,
        conversation_context=conversation_context,
    )
    evidence_pack = build_structured_tool_evidence_pack(
        selected_tools=preview.selected_tools,
        slice_name=plan.slice_name,
        summary='Follow-up de selecao de aluno resolvido deterministicamente antes do fallback do kernel do LlamaIndex.',
    )
    await rt._persist_conversation_turn(
        settings=settings,
        conversation_external_id=effective_conversation_id,
        channel=request.channel.value,
        actor=actor,
        user_message=request.message,
        assistant_message=message_text,
    )
    await rt._persist_operational_trace(
        settings=settings,
        conversation_external_id=effective_conversation_id,
        channel=request.channel.value,
        engine_name='llamaindex',
        engine_mode=engine_mode,
        actor=actor,
        preview=preview,
        school_profile=school_profile,
        conversation_context=conversation_context,
        public_plan=None,
        request_message=request.message,
        message_text=message_text,
        citations_count=0,
        suggested_reply_count=len(suggested_replies),
        visual_asset_count=0,
        answer_verifier_valid=True,
        answer_verifier_reason='llamaindex deterministic student focus fast path',
        answer_verifier_fallback_used=False,
        deterministic_fallback_available=True,
        answer_verifier_judge_used=False,
    )
    response = MessageResponse(
        message_text=message_text,
        mode=preview.mode,
        classification=preview.classification,
        retrieval_backend=RetrievalBackend.none,
        selected_tools=preview.selected_tools,
        citations=[],
        visual_assets=[],
        suggested_replies=suggested_replies,
        calendar_events=[],
        evidence_pack=evidence_pack,
        needs_authentication=True,
        graph_path=[
            *preview.graph_path,
            'llamaindex:protected',
            'llamaindex:student_focus_fast_path',
            f'kernel:{plan.stack_name}',
        ],
        risk_flags=preview.risk_flags,
        reason='llamaindex_student_focus_fast_path',
    )
    from .agent_kernel import KernelReflection

    reflection = KernelReflection(
        grounded=True,
        verifier_reason='student focus deterministic fast path',
        fallback_used=False,
        answer_judge_used=False,
        notes=[
            f'route:{preview.mode.value}',
            f'slice:{plan.slice_name}',
            'llamaindex:student_focus_fast_path',
            f'evidence:{evidence_pack.strategy}',
            *plan.plan_notes,
        ],
    )
    return KernelRunResult(
        plan=plan,
        reflection=reflection,
        response=response.model_dump(mode='json'),
    )


async def execute_llamaindex_plan(
    *,
    request: MessageResponseRequest,
    settings: Any,
    plan: KernelPlan,
    engine_mode: str,
) -> KernelRunResult:
    profile = get_path_execution_profile('llamaindex')
    fast_path_result = await _maybe_execute_llamaindex_student_focus_fast_path(
        request=request,
        settings=settings,
        plan=plan,
        engine_mode=engine_mode,
    )
    if fast_path_result is not None:
        return fast_path_result
    result = await maybe_execute_llamaindex_native_plan(
        request=request,
        settings=settings,
        plan=plan,
        engine_name='llamaindex',
        engine_mode=engine_mode,
        path_profile=profile,
    )
    if result is not None:
        return result
    return await execute_kernel_plan(
        request=request,
        settings=settings,
        plan=plan,
        engine_name='llamaindex',
        engine_mode=engine_mode,
        path_profile=profile,
        replan_builder=_build_llamaindex_replan,
    )
