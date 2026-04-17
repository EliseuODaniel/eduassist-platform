from __future__ import annotations

# ruff: noqa: F401,F403,F405

from typing import Any

from . import runtime as rt
from .evidence_pack import (
    build_direct_answer_evidence_pack,
    build_structured_tool_evidence_pack,
)
from .llamaindex_kernel import KernelPlan, KernelReflection, KernelRunResult
from .llamaindex_native_runtime import (
    _compose_external_live_query_answer,
    _looks_like_external_live_query,
    _should_use_llamaindex_protected_records_fast_path,
    _should_use_llamaindex_teacher_schedule_direct,
    _should_use_llamaindex_teacher_scope_guidance,
)
from .llamaindex_native_support_runtime import _build_llamaindex_direct_result
from .models import (
    AccessTier,
    IntentClassification,
    MessageResponse,
    MessageResponseRequest,
    OrchestrationMode,
    QueryDomain,
    RetrievalBackend,
)


async def maybe_execute_llamaindex_native_preflight(
    *,
    request: MessageResponseRequest,
    settings: Any,
    plan: KernelPlan,
    engine_name: str,
    engine_mode: str,
    actor: dict[str, Any] | None,
    effective_conversation_id: str | None,
    conversation_context: dict[str, Any] | None,
    school_profile: dict[str, Any] | None,
    started_at: float,
) -> KernelRunResult | None:
    recent_focus = rt._recent_conversation_focus(conversation_context)
    if (
        recent_focus
        and recent_focus.get('kind') == 'visit'
        and (
            rt._looks_like_visit_update_follow_up(request.message)
            or rt._looks_like_workflow_resume_follow_up(request.message)
        )
    ):
        preview = plan.preview.model_copy(deep=True)
        preview.mode = OrchestrationMode.structured_tool
        preview.classification = IntentClassification(
            domain=QueryDomain.support,
            access_tier=AccessTier.authenticated if request.user.authenticated else AccessTier.public,
            confidence=0.99,
            reason='follow-up de visita deve atualizar workflow antes do roteamento generico llamaindex',
        )
        preview.reason = 'llamaindex_visit_update_followup'
        preview.selected_tools = list(dict.fromkeys([*preview.selected_tools, 'update_visit_booking']))
        preview.needs_authentication = False
        workflow_payload = await rt._update_visit_booking(
            settings=settings,
            request=request,
            conversation_context=conversation_context,
        )
        evidence_pack = build_structured_tool_evidence_pack(
            selected_tools=preview.selected_tools,
            slice_name=plan.slice_name,
            summary='Follow-up de visita resolvido deterministicamente antes do roteamento documental do LlamaIndex.',
        )
        return await _build_llamaindex_direct_result(
            request=request,
            settings=settings,
            plan=plan,
            engine_name=engine_name,
            engine_mode=engine_mode,
            actor=actor,
            conversation_context=conversation_context,
            school_profile=school_profile,
            preview=preview,
            message_text=rt._compose_visit_booking_action_answer(
                workflow_payload,
                request_message=request.message,
            ),
            execution_reason='llamaindex_visit_update_followup',
            evidence_pack=evidence_pack,
            started_at=started_at,
            reason_graph_leaf='visit_update_direct',
        )
    if rt._looks_like_natural_visit_booking_request(request.message):
        visit_preview = plan.preview.model_copy(deep=True)
        visit_preview.mode = OrchestrationMode.structured_tool
        visit_preview.classification = IntentClassification(
            domain=QueryDomain.support,
            access_tier=AccessTier.authenticated if request.user.authenticated else AccessTier.public,
            confidence=0.99,
            reason='pedido natural de visita deve abrir workflow antes do roteamento generico llamaindex',
        )
        visit_preview.reason = 'llamaindex_visit_booking_request'
        visit_preview.selected_tools = list(dict.fromkeys([*visit_preview.selected_tools, 'schedule_school_visit']))
        visit_preview.needs_authentication = False
        workflow_payload = await rt._create_visit_booking(
            settings=settings,
            request=request,
            actor=actor,
        )
        evidence_pack = build_structured_tool_evidence_pack(
            selected_tools=visit_preview.selected_tools,
            slice_name=plan.slice_name,
            summary='Pedido de visita resolvido deterministicamente antes do roteamento documental do LlamaIndex.',
        )
        return await _build_llamaindex_direct_result(
            request=request,
            settings=settings,
            plan=plan,
            engine_name=engine_name,
            engine_mode=engine_mode,
            actor=actor,
            conversation_context=conversation_context,
            school_profile=school_profile,
            preview=visit_preview,
            message_text=rt._compose_visit_booking_answer(workflow_payload, school_profile),
            execution_reason='llamaindex_visit_booking_request',
            evidence_pack=evidence_pack,
            started_at=started_at,
            reason_graph_leaf='visit_booking_direct',
        )
    actor_role = str((actor or {}).get('role_code', '') or '').strip().lower()
    teacher_authenticated = actor_role == 'teacher' or (
        getattr(request.user, 'authenticated', False)
        and getattr(getattr(request.user, 'role', None), 'value', '') == 'teacher'
    )
    teacher_scope_query = rt._is_teacher_scope_guidance_query(
        request.message,
        actor=actor,
        user=request.user,
        conversation_context=conversation_context,
    )
    should_fetch_teacher_schedule = rt._should_fetch_teacher_schedule(
        request.message,
        actor=actor,
        user=request.user,
        conversation_context=conversation_context,
    )
    if _should_use_llamaindex_teacher_schedule_direct(
        teacher_authenticated=teacher_authenticated,
        should_fetch_teacher_schedule=should_fetch_teacher_schedule,
    ) or _should_use_llamaindex_teacher_scope_guidance(
        teacher_scope_query=teacher_scope_query,
        should_fetch_teacher_schedule=should_fetch_teacher_schedule,
    ):
        preview = plan.preview.model_copy(deep=True)
        if _should_use_llamaindex_teacher_schedule_direct(
            teacher_authenticated=teacher_authenticated,
            should_fetch_teacher_schedule=should_fetch_teacher_schedule,
        ):
            message_text = await rt._execute_teacher_protected_specialist(
                settings=settings,
                request=request,
                actor=actor or {},
                conversation_context=conversation_context,
            )
            preview.mode = OrchestrationMode.structured_tool
            preview.classification = IntentClassification(
                domain=QueryDomain.academic,
                access_tier=AccessTier.authenticated,
                confidence=0.99,
                reason='consulta protegida de grade docente atendida pelo runtime nativo do llamaindex',
            )
            preview.selected_tools = list(dict.fromkeys([*preview.selected_tools, 'get_teacher_schedule']))
            preview.needs_authentication = True
            execution_reason = 'llamaindex_teacher_schedule_direct'
            summary = 'Resposta deterministica grounded em service protegido de grade docente.'
        else:
            message_text = rt._compose_teacher_access_scope_answer(
                actor,
                school_name=str((school_profile or {}).get('school_name', 'Colegio Horizonte')),
            )
            preview.mode = OrchestrationMode.structured_tool
            preview.classification = IntentClassification(
                domain=QueryDomain.academic,
                access_tier=AccessTier.authenticated,
                confidence=0.95,
                reason='orientacao de escopo docente atendida pelo runtime nativo do llamaindex',
            )
            preview.selected_tools = list(dict.fromkeys([*preview.selected_tools, 'get_actor_identity_context']))
            preview.needs_authentication = True
            execution_reason = 'llamaindex_teacher_scope_guidance'
            summary = 'Resposta deterministica sobre escopo docente e vinculacao da conta.'
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
            summary=summary,
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
            engine_name=engine_name,
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
            answer_verifier_reason='teacher deterministic native answer',
            answer_verifier_fallback_used=False,
            deterministic_fallback_available=True,
            answer_verifier_judge_used=False,
        )
        response = MessageResponse(
            message_text=rt._normalize_response_wording(message_text),
            mode=preview.mode,
            classification=preview.classification,
            retrieval_backend=RetrievalBackend.none,
            selected_tools=preview.selected_tools,
            citations=[],
            visual_assets=[],
            suggested_replies=suggested_replies,
            calendar_events=[],
            evidence_pack=evidence_pack,
            needs_authentication=preview.needs_authentication,
            graph_path=[
                *preview.graph_path,
                'llamaindex:workflow',
                'llamaindex:teacher',
                f'kernel:{plan.stack_name}',
            ],
            risk_flags=preview.risk_flags,
            reason=execution_reason,
        )
        reflection = KernelReflection(
            grounded=True,
            verifier_reason='teacher protected native path',
            fallback_used=False,
            answer_judge_used=False,
            notes=[
                f'route:{preview.mode.value}',
                f'slice:{plan.slice_name}',
                f'evidence:{evidence_pack.strategy}',
                *plan.plan_notes,
            ],
        )
        return KernelRunResult(
            plan=plan,
            reflection=reflection,
            response=response.model_dump(mode='json'),
        )
    if _looks_like_external_live_query(request.message):
        preview = plan.preview.model_copy(deep=True)
        preview.mode = OrchestrationMode.structured_tool
        preview.classification = IntentClassification(
            domain=QueryDomain.institution,
            access_tier=AccessTier.public,
            confidence=0.98,
            reason='consulta externa em tempo real encerrada deterministicamente antes do routing documental do llamaindex',
        )
        preview.selected_tools = []
        preview.needs_authentication = False
        message_text = rt._normalize_response_wording(_compose_external_live_query_answer(request.message) or '')
        evidence_pack = build_direct_answer_evidence_pack(
            summary='Pergunta externa reconhecida fora do escopo documental e de tempo real do assistente escolar.',
            supports=[],
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
            engine_name=engine_name,
            engine_mode=engine_mode,
            actor=actor,
            preview=preview,
            school_profile=await rt._fetch_public_school_profile(settings=settings),
            conversation_context=conversation_context,
            public_plan=None,
            request_message=request.message,
            message_text=message_text,
            citations_count=0,
            suggested_reply_count=0,
            visual_asset_count=0,
            answer_verifier_valid=True,
            answer_verifier_reason='llamaindex deterministic external-live guardrail',
            answer_verifier_fallback_used=False,
            deterministic_fallback_available=True,
            answer_verifier_judge_used=False,
        )
        response = MessageResponse(
            message_text=message_text,
            mode=preview.mode,
            classification=preview.classification,
            retrieval_backend=RetrievalBackend.none,
            selected_tools=[],
            citations=[],
            visual_assets=[],
            suggested_replies=[],
            calendar_events=[],
            evidence_pack=evidence_pack,
            needs_authentication=False,
            graph_path=[
                *preview.graph_path,
                'llamaindex:external',
                'llamaindex:external_live_guardrail',
                f'kernel:{plan.stack_name}',
            ],
            risk_flags=list(dict.fromkeys([*preview.risk_flags, 'external_live_data_unavailable'])),
            reason='llamaindex_external_live_guardrail',
        )
        reflection = KernelReflection(
            grounded=True,
            verifier_reason='external live query blocked before llamaindex retrieval',
            fallback_used=False,
            answer_judge_used=False,
            notes=[
                f'route:{preview.mode.value}',
                f'slice:{plan.slice_name}',
                'llamaindex:external_live_guardrail',
                f'evidence:{evidence_pack.strategy}',
                *plan.plan_notes,
            ],
        )
        return KernelRunResult(
            plan=plan,
            reflection=reflection,
            response=response.model_dump(mode='json'),
        )
    protected_records_fast_path = _should_use_llamaindex_protected_records_fast_path(
        request=request,
        actor=actor,
        preview=plan.preview,
        conversation_context=conversation_context,
    )
    if protected_records_fast_path:
        preview = plan.preview.model_copy(deep=True)
        rt._apply_protected_domain_rescue(
            preview=preview,
            actor=actor,
            message=request.message,
            conversation_context=conversation_context,
        )
        if not {'get_administrative_status', 'get_student_administrative_status', 'get_actor_identity_context'} & set(preview.selected_tools):
            preview.selected_tools = [*preview.selected_tools, 'get_administrative_status', 'get_student_administrative_status']
        preview.mode = OrchestrationMode.structured_tool
        if preview.classification.domain not in {QueryDomain.academic, QueryDomain.finance}:
            preview.classification = IntentClassification(
                domain=QueryDomain.institution,
                access_tier=AccessTier.authenticated,
                confidence=0.97,
                reason='follow-up administrativo ou de identidade resolvido antes do routing documental pesado do llamaindex',
            )
        preview.needs_authentication = True
        school_profile = await rt._fetch_public_school_profile(settings=settings)
        message_text = await rt._execute_protected_records_specialist(
            settings=settings,
            request=request,
            preview=preview,
            actor=actor,
            conversation_context=conversation_context,
        )
        evidence_pack = build_structured_tool_evidence_pack(
            selected_tools=preview.selected_tools,
            slice_name=plan.slice_name,
            summary='Consulta protegida administrativa ou de identidade resolvida deterministicamente antes do routing pesado do LlamaIndex.',
        )
        suggested_replies = rt._build_suggested_replies(
            request=request,
            preview=preview,
            actor=actor,
            school_profile=school_profile,
            conversation_context=conversation_context,
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
            engine_name=engine_name,
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
            answer_verifier_reason='llamaindex protected records deterministic fast path',
            answer_verifier_fallback_used=False,
            deterministic_fallback_available=True,
            answer_verifier_judge_used=False,
        )
        response = MessageResponse(
            message_text=rt._normalize_response_wording(message_text),
            mode=preview.mode,
            classification=preview.classification,
            retrieval_backend=RetrievalBackend.none,
            selected_tools=preview.selected_tools,
            citations=[],
            visual_assets=[],
            suggested_replies=suggested_replies,
            calendar_events=[],
            evidence_pack=evidence_pack,
            needs_authentication=preview.needs_authentication,
            graph_path=[
                *preview.graph_path,
                'llamaindex:protected',
                'llamaindex:protected_records_fast_path',
                f'kernel:{plan.stack_name}',
            ],
            risk_flags=preview.risk_flags,
            reason='llamaindex_protected_records_fast_path',
        )
        reflection = KernelReflection(
            grounded=True,
            verifier_reason='protected records deterministic fast path',
            fallback_used=False,
            answer_judge_used=False,
            notes=[
                f'route:{preview.mode.value}',
                f'slice:{plan.slice_name}',
                'llamaindex:protected_records_fast_path',
                f'evidence:{evidence_pack.strategy}',
                *plan.plan_notes,
            ],
        )
        return KernelRunResult(
            plan=plan,
            reflection=reflection,
            response=response.model_dump(mode='json'),
        )
