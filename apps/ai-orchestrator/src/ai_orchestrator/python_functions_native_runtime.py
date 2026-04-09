from __future__ import annotations

from time import monotonic
from typing import Any

from . import runtime as rt
from .python_functions_kernel import KernelPlan, KernelReflection, KernelRunResult
from .candidate_builder import build_response_candidate
from .candidate_chooser import choose_best_candidate
from .evidence_pack import (
    build_direct_answer_evidence_pack,
    build_retrieval_evidence_pack,
    build_structured_tool_evidence_pack,
)
from .final_polish_policy import build_final_polish_decision
from .python_functions_kernel_runtime import (
    _maybe_contextual_public_direct_answer,
    _maybe_hypothetical_public_pricing_answer,
    _maybe_public_unpublished_direct_answer,
)
from .python_functions_local_llm import (
    compose_python_functions_with_provider,
    polish_python_functions_with_provider,
    revise_python_functions_with_provider,
    verify_python_functions_answer_against_contract,
)
from .models import (
    AccessTier,
    IntentClassification,
    MessageEvidenceSupport,
    MessageResponse,
    MessageResponseCitation,
    OrchestrationMode,
    QueryDomain,
    RetrievalBackend,
    RetrievalProfile,
)
from .path_profiles import PathExecutionProfile, get_path_execution_profile
from .python_functions_public_knowledge import (
    compose_public_canonical_lane_answer,
    compose_public_conduct_policy_contextual_answer,
    match_public_canonical_lane,
)
from .response_cache import store_cached_public_response
from .python_functions_retrieval import (
    can_read_restricted_documents,
    compose_restricted_document_grounded_answer_for_query,
    compose_restricted_document_no_match_answer,
    get_retrieval_service,
    looks_like_restricted_document_query,
    select_relevant_restricted_hits,
)
from .python_functions_retrieval_probe import build_public_evidence_probe
from .serving_policy import LoadSnapshot, build_public_serving_policy
from .serving_telemetry import get_stack_telemetry_snapshot, record_stack_outcome


def _should_use_python_functions_native_path(plan: KernelPlan) -> bool:
    preview = plan.preview
    if preview.mode is OrchestrationMode.structured_tool:
        return True
    if (
        preview.mode is OrchestrationMode.hybrid_retrieval
        and preview.classification.access_tier is AccessTier.authenticated
        and 'documento interno' in str(preview.reason).lower()
    ):
        return True
    if preview.classification.access_tier is AccessTier.public:
        if preview.classification.domain not in {QueryDomain.institution, QueryDomain.calendar, QueryDomain.unknown}:
            return False
        return preview.mode in {OrchestrationMode.hybrid_retrieval, OrchestrationMode.clarify}
    if preview.mode is not OrchestrationMode.clarify:
        return False
    return preview.classification.domain in {
        QueryDomain.institution,
        QueryDomain.academic,
        QueryDomain.unknown,
    }


def _should_force_public_teacher_boundary_native_path(
    *,
    request: Any,
    plan: KernelPlan,
    conversation_context: dict[str, Any] | None,
) -> bool:
    preview = plan.preview
    if preview.classification.access_tier is not AccessTier.public:
        return False
    if preview.mode is not OrchestrationMode.clarify:
        return False
    return rt._is_public_teacher_identity_query(request.message) or rt._is_public_teacher_directory_follow_up(
        request.message,
        conversation_context,
    )


async def _build_python_functions_direct_result(
    *,
    request: Any,
    settings: Any,
    plan: KernelPlan,
    engine_name: str,
    engine_mode: str,
    actor: dict[str, Any] | None,
    conversation_context: dict[str, Any] | None,
    school_profile: dict[str, Any] | None,
    preview: Any,
    message_text: str,
    execution_reason: str,
    evidence_pack: Any,
    started_at: float,
    reason_graph_leaf: str,
) -> KernelRunResult:
    effective_conversation_id = rt._effective_conversation_id(request)
    suggested_replies = rt._build_suggested_replies(
        request=request,
        preview=preview,
        actor=actor,
        school_profile=school_profile,
        conversation_context=conversation_context,
    )
    normalized_text = rt._normalize_response_wording(message_text)
    await rt._persist_conversation_turn(
        settings=settings,
        conversation_external_id=effective_conversation_id,
        channel=request.channel.value,
        actor=actor,
        user_message=request.message,
        assistant_message=normalized_text,
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
        message_text=normalized_text,
        citations_count=0,
        suggested_reply_count=len(suggested_replies),
        visual_asset_count=0,
        answer_verifier_valid=True,
        answer_verifier_reason=execution_reason,
        answer_verifier_fallback_used=False,
        deterministic_fallback_available=True,
        answer_verifier_judge_used=False,
        langgraph_trace_metadata={
            'python_functions_native_reason': execution_reason,
            'python_functions_evidence_strategy': evidence_pack.strategy if evidence_pack is not None else '',
            'python_functions_evidence_support_count': evidence_pack.support_count if evidence_pack is not None else 0,
        },
    )
    selected_tools = list(
        dict.fromkeys(
            [
                *preview.selected_tools,
                'python_functions_native_runtime',
            ]
        )
    )
    response = MessageResponse(
        message_text=normalized_text,
        mode=preview.mode,
        classification=preview.classification,
        retrieval_backend=RetrievalBackend.none,
        selected_tools=selected_tools,
        citations=[],
        visual_assets=[],
        suggested_replies=suggested_replies,
        calendar_events=[],
        evidence_pack=evidence_pack,
        needs_authentication=preview.needs_authentication,
        graph_path=[
            *preview.graph_path,
            'python_functions:native_runtime',
            f'python_functions:{reason_graph_leaf}',
            f'kernel:{plan.stack_name}',
        ],
        risk_flags=preview.risk_flags,
        reason=execution_reason,
        used_llm=False,
        llm_stages=[],
        candidate_chosen='deterministic',
        candidate_reason=execution_reason,
    )
    record_stack_outcome(
        stack_name='python_functions',
        latency_ms=(monotonic() - started_at) * 1000,
        success=True,
        timeout=False,
        cache_hit=False,
        used_llm=False,
        candidate_kind='deterministic',
    )
    reflection = KernelReflection(
        grounded=True,
        verifier_reason=execution_reason,
        fallback_used=False,
        answer_judge_used=False,
        notes=[
            f'route:{preview.mode.value}',
            f'slice:{plan.slice_name}',
            f'evidence:{evidence_pack.strategy}' if evidence_pack is not None else 'evidence:none',
            *plan.plan_notes,
        ],
    )
    return KernelRunResult(
        plan=plan.model_copy(update={'preview': preview}),
        reflection=reflection,
        response=response.model_dump(mode='json'),
    )


async def maybe_execute_python_functions_native_plan(
    *,
    request: Any,
    settings: Any,
    plan: KernelPlan,
    engine_name: str,
    engine_mode: str,
    path_profile: PathExecutionProfile | None = None,
) -> KernelRunResult | None:
    started_at = monotonic()
    effective_path_profile = path_profile or get_path_execution_profile(engine_name)
    actor = await rt._fetch_actor_context(settings=settings, telegram_chat_id=request.telegram_chat_id)
    effective_conversation_id = rt._effective_conversation_id(request)
    conversation_context_bundle = await rt._fetch_conversation_context(
        settings=settings,
        conversation_external_id=effective_conversation_id,
        channel=request.channel.value,
    )
    conversation_context = rt._conversation_context_payload(conversation_context_bundle)
    if not _should_use_python_functions_native_path(plan) and not _should_force_public_teacher_boundary_native_path(
        request=request,
        plan=plan,
        conversation_context=conversation_context,
    ):
        return None
    recent_focus = rt._recent_conversation_focus(conversation_context)
    analysis_message = rt._build_analysis_message(request.message, conversation_context_bundle)
    school_profile = await rt._fetch_public_school_profile(settings=settings)
    preview = plan.preview.model_copy(deep=True)
    if actor is not None and request.user.authenticated:
        rt._apply_protected_domain_rescue(
            preview=preview,
            actor=actor,
            message=request.message,
            conversation_context=conversation_context,
        )
    if looks_like_restricted_document_query(request.message) and not can_read_restricted_documents(request.user):
        preview.mode = OrchestrationMode.deny
        preview.classification = IntentClassification(
            domain=QueryDomain.institution,
            access_tier=AccessTier.public,
            confidence=0.99,
            reason='python_functions_native_restricted_access_denied',
        )
        preview.selected_tools = list(dict.fromkeys([*preview.selected_tools, 'search_documents']))
        preview.needs_authentication = False
    elif (
        recent_focus
        and recent_focus.get('kind') == 'visit'
        and (
            rt._looks_like_visit_update_follow_up(request.message)
            or rt._looks_like_workflow_resume_follow_up(request.message)
        )
    ):
        preview.mode = OrchestrationMode.structured_tool
        preview.classification = IntentClassification(
            domain=QueryDomain.support,
            access_tier=AccessTier.authenticated if request.user.authenticated else AccessTier.public,
            confidence=0.99,
            reason='follow-up de visita deve atualizar workflow antes do roteamento generico python_functions',
        )
        preview.reason = 'python_functions_native_visit_update_followup'
        preview.selected_tools = list(dict.fromkeys([*preview.selected_tools, 'update_visit_booking']))
        preview.needs_authentication = False
        workflow_payload = await rt._update_visit_booking(
            settings=settings,
            request=request,
            conversation_context=conversation_context,
        )
        message_text = rt._compose_visit_booking_action_answer(
            workflow_payload,
            request_message=request.message,
        )
        evidence_pack = build_structured_tool_evidence_pack(
            selected_tools=preview.selected_tools,
            slice_name=plan.slice_name,
            summary='Follow-up de visita resolvido deterministicamente antes do roteamento generico do python_functions.',
        )
        return await _build_python_functions_direct_result(
            request=request,
            settings=settings,
            plan=plan,
            engine_name=engine_name,
            engine_mode=engine_mode,
            actor=actor,
            conversation_context=conversation_context,
            school_profile=school_profile,
            preview=preview,
            message_text=message_text,
            execution_reason='python_functions_native_visit_update_followup',
            evidence_pack=evidence_pack,
            started_at=started_at,
            reason_graph_leaf='visit_update_direct',
        )
    elif rt._looks_like_natural_visit_booking_request(request.message):
        preview.mode = OrchestrationMode.structured_tool
        preview.classification = IntentClassification(
            domain=QueryDomain.support,
            access_tier=AccessTier.authenticated if request.user.authenticated else AccessTier.public,
            confidence=0.99,
            reason='pedido natural de visita deve abrir workflow antes do roteamento generico python_functions',
        )
        preview.reason = 'python_functions_native_visit_booking_request'
        preview.selected_tools = list(dict.fromkeys([*preview.selected_tools, 'schedule_school_visit']))
        preview.needs_authentication = False
        workflow_payload = await rt._create_visit_booking(
            settings=settings,
            request=request,
            actor=actor,
        )
        message_text = rt._compose_visit_booking_answer(workflow_payload, school_profile)
        evidence_pack = build_structured_tool_evidence_pack(
            selected_tools=preview.selected_tools,
            slice_name=plan.slice_name,
            summary='Pedido de visita resolvido deterministicamente antes do roteamento generico do python_functions.',
        )
        return await _build_python_functions_direct_result(
            request=request,
            settings=settings,
            plan=plan,
            engine_name=engine_name,
            engine_mode=engine_mode,
            actor=actor,
            conversation_context=conversation_context,
            school_profile=school_profile,
            preview=preview,
            message_text=message_text,
            execution_reason='python_functions_native_visit_booking_request',
            evidence_pack=evidence_pack,
            started_at=started_at,
            reason_graph_leaf='visit_booking_direct',
        )

    retrieval_hits: list[Any] = []
    citations: list[MessageResponseCitation] = []
    calendar_events = []
    retrieval_context_pack: str | None = None
    public_plan = None
    deterministic_fallback_text: str | None = None
    query_hints: set[str] = set()
    semantic_judge_used = False
    llm_stages: list[str] = []
    answer_verifier_fallback_used = False
    evidence_pack = None

    teacher_scope_answer = None
    teacher_schedule_answer = None
    authenticated_account_scope_answer = None
    has_authenticated_actor = bool(actor and rt._linked_students(actor))
    actor_role = str((actor or {}).get('role_code', '') or '').strip().lower()
    teacher_authenticated = actor_role == 'teacher' or (
        getattr(request.user, 'authenticated', False)
        and getattr(getattr(request.user, 'role', None), 'value', '') == 'teacher'
    )
    should_fetch_teacher_schedule = rt._should_fetch_teacher_schedule(
        request.message,
        actor=actor,
        user=request.user,
        conversation_context=conversation_context,
    )
    if rt._is_teacher_scope_guidance_query(request.message, actor=actor, user=request.user, conversation_context=conversation_context) and not should_fetch_teacher_schedule:
        teacher_scope_answer = rt._compose_teacher_access_scope_answer(
            actor,
            school_name=str(school_profile.get('school_name', 'Colegio Horizonte')),
        )
    elif teacher_authenticated and should_fetch_teacher_schedule:
        teacher_schedule_answer = await rt._execute_teacher_protected_specialist(
            settings=settings,
            request=request,
            actor=actor or {},
            conversation_context=conversation_context,
        )
    elif (
        has_authenticated_actor
        and rt._is_access_scope_query(request.message)
        and not rt._should_prioritize_protected_sql_query(
            request.message,
            actor=actor,
            conversation_context=conversation_context,
        )
    ):
        authenticated_account_scope_answer = rt._compose_account_context_answer(
            actor,
            request_message=request.message,
            conversation_context=conversation_context,
        )
    elif has_authenticated_actor and rt._is_actor_identity_query(request.message):
        authenticated_account_scope_answer = rt._compose_actor_identity_answer(actor)

    meta_repair_answer = None
    if teacher_scope_answer is None and authenticated_account_scope_answer is None and rt._is_meta_repair_context_query(request.message):
        meta_repair_answer = rt._compose_meta_repair_follow_up_answer(conversation_context)

    protected_family_attendance_answer = None
    if (
        teacher_scope_answer is None
        and authenticated_account_scope_answer is None
        and meta_repair_answer is None
        and has_authenticated_actor
        and request.telegram_chat_id is not None
        and rt._looks_like_family_attendance_aggregate_query(request.message)
    ):
        family_preview = preview.model_copy(
            update={
                'mode': OrchestrationMode.structured_tool,
                'classification': IntentClassification(
                    domain=QueryDomain.academic,
                    access_tier=AccessTier.authenticated,
                    confidence=0.99,
                    reason='panorama familiar de frequencia resolvido antes do roteamento generico python_functions',
                ),
                'reason': 'python_functions_native_family_attendance_aggregate',
                'selected_tools': list(dict.fromkeys([*preview.selected_tools, 'get_student_attendance', 'get_student_academic_summary'])),
                'needs_authentication': True,
            }
        )
        protected_family_attendance_answer = await rt._execute_protected_records_specialist(
            settings=settings,
            request=request,
            preview=family_preview,
            actor=actor,
            conversation_context=conversation_context,
        )

    early_public_canonical_lane = None
    early_public_canonical_answer = None
    if teacher_scope_answer is None and authenticated_account_scope_answer is None and meta_repair_answer is None:
        if rt._is_public_teacher_identity_query(request.message) or rt._is_public_teacher_directory_follow_up(
            request.message,
            conversation_context,
        ):
            early_public_canonical_lane = 'public_bundle.teacher_directory_boundary'
        else:
            early_public_canonical_lane = (
                match_public_canonical_lane(analysis_message)
                or match_public_canonical_lane(request.message)
            )
        if early_public_canonical_lane:
            early_public_canonical_answer = (
                compose_public_conduct_policy_contextual_answer(
                    request.message,
                    profile=school_profile,
                )
                if early_public_canonical_lane == 'public_bundle.conduct_frequency_punctuality'
                else None
            ) or compose_public_canonical_lane_answer(
                early_public_canonical_lane,
                profile=school_profile,
            )

    contextual_public_answer = None
    unpublished_public_answer = None
    hypothetical_public_pricing_direct = None
    if teacher_scope_answer is None and authenticated_account_scope_answer is None and meta_repair_answer is None:
        contextual_public_answer = await _maybe_contextual_public_direct_answer(
            request=request,
            analysis_message=analysis_message,
            preview=preview,
            settings=settings,
            school_profile=school_profile,
            conversation_context=conversation_context,
        )
        unpublished_public_answer = _maybe_public_unpublished_direct_answer(
            request=request,
            preview=preview,
        )
        hypothetical_public_pricing_direct = _maybe_hypothetical_public_pricing_answer(
            request=request,
            plan=plan,
            preview=preview,
            school_profile=school_profile,
            conversation_context=conversation_context,
        )
        if (
            hypothetical_public_pricing_direct is None
            and isinstance(school_profile, dict)
            and rt._is_explicit_public_pricing_projection_query(
                request.message,
                conversation_context=conversation_context,
            )
        ):
            pricing_plan = rt._build_public_institution_plan(
                request.message,
                list(preview.selected_tools),
                semantic_plan=None,
                conversation_context=conversation_context,
                school_profile=school_profile,
            )
            if pricing_plan.conversation_act != 'pricing':
                pricing_plan = rt.replace(
                    pricing_plan,
                    conversation_act='pricing',
                    secondary_acts=tuple(act for act in pricing_plan.secondary_acts if act != 'pricing'),
                )
            pricing_projection_answer = rt._compose_public_profile_answer(
                school_profile,
                request.message,
                actor=None,
                original_message=request.message,
                conversation_context=conversation_context,
                semantic_plan=pricing_plan,
            )
            if pricing_projection_answer and 'R$' in pricing_projection_answer:
                hypothetical_public_pricing_direct = (pricing_projection_answer, pricing_plan)

    execution_reason = 'python_functions_native_public'

    if teacher_scope_answer:
        message_text = teacher_scope_answer
        deterministic_fallback_text = teacher_scope_answer
        preview = preview.model_copy(
            update={
                'mode': OrchestrationMode.structured_tool,
                'reason': 'python_functions_native_teacher_scope_guidance',
                'selected_tools': list(dict.fromkeys([*preview.selected_tools, 'get_actor_identity_context'])),
            }
        )
        execution_reason = 'python_functions_native_teacher_scope_guidance'
        evidence_pack = build_structured_tool_evidence_pack(
            selected_tools=preview.selected_tools,
            slice_name=plan.slice_name,
            summary='Resposta deterministica sobre escopo docente e vinculacao da conta.',
        )
    elif teacher_schedule_answer:
        message_text = teacher_schedule_answer
        deterministic_fallback_text = teacher_schedule_answer
        preview = preview.model_copy(
            update={
                'mode': OrchestrationMode.structured_tool,
                'classification': IntentClassification(
                    domain=QueryDomain.academic,
                    access_tier=AccessTier.authenticated,
                    confidence=0.99,
                    reason='consulta protegida de turmas, disciplinas e grade docente atendida pelo runtime nativo python_functions',
                ),
                'reason': 'python_functions_native_teacher_schedule',
                'selected_tools': list(dict.fromkeys([*preview.selected_tools, 'get_teacher_schedule'])),
                'needs_authentication': True,
            }
        )
        execution_reason = 'python_functions_native_teacher_schedule'
        evidence_pack = build_structured_tool_evidence_pack(
            selected_tools=preview.selected_tools,
            slice_name=plan.slice_name,
            summary='Resposta deterministica grounded em service protegido de grade docente.',
        )
    elif authenticated_account_scope_answer:
        message_text = authenticated_account_scope_answer
        deterministic_fallback_text = authenticated_account_scope_answer
        preview = preview.model_copy(
            update={
                'mode': OrchestrationMode.structured_tool,
                'reason': 'python_functions_native_authenticated_account_scope',
                'selected_tools': list(dict.fromkeys([*preview.selected_tools, 'get_actor_identity_context'])),
            }
        )
        execution_reason = 'python_functions_native_authenticated_account_scope'
        evidence_pack = build_structured_tool_evidence_pack(
            selected_tools=preview.selected_tools,
            slice_name=plan.slice_name,
            summary='Resposta deterministica sobre escopo autenticado e identidade da conta.',
        )
    elif meta_repair_answer:
        message_text = meta_repair_answer
        deterministic_fallback_text = meta_repair_answer
        preview = preview.model_copy(
            update={
                'mode': OrchestrationMode.structured_tool,
                'reason': 'python_functions_native_meta_repair',
                'selected_tools': list(preview.selected_tools),
            }
        )
        execution_reason = 'python_functions_native_meta_repair'
        evidence_pack = build_structured_tool_evidence_pack(
            selected_tools=preview.selected_tools,
            slice_name=plan.slice_name,
            summary='Resposta deterministica de reparo contextual sobre o turno anterior.',
        )
    elif protected_family_attendance_answer:
        message_text = protected_family_attendance_answer
        deterministic_fallback_text = protected_family_attendance_answer
        preview = preview.model_copy(
            update={
                'mode': OrchestrationMode.structured_tool,
                'classification': IntentClassification(
                    domain=QueryDomain.academic,
                    access_tier=AccessTier.authenticated,
                    confidence=0.99,
                    reason='panorama familiar de frequencia resolvido deterministicamente no runtime nativo python_functions',
                ),
                'reason': 'python_functions_native_family_attendance_aggregate',
                'selected_tools': list(dict.fromkeys([*preview.selected_tools, 'get_student_attendance', 'get_student_academic_summary'])),
                'needs_authentication': True,
            }
        )
        execution_reason = 'python_functions_native_family_attendance_aggregate'
        evidence_pack = build_structured_tool_evidence_pack(
            selected_tools=preview.selected_tools,
            slice_name=plan.slice_name,
            summary='Panorama familiar de frequencia resolvido deterministicamente antes do roteamento generico.',
        )
    elif early_public_canonical_answer:
        message_text = early_public_canonical_answer
        deterministic_fallback_text = early_public_canonical_answer
        preview = preview.model_copy(
            update={
                'mode': OrchestrationMode.structured_tool,
                'classification': IntentClassification(
                    domain=QueryDomain.institution,
                    access_tier=AccessTier.public,
                    confidence=0.99,
                    reason='lane publica canonica resolvida antes do roteamento estruturado python_functions',
                ),
                'reason': f'python_functions_native_canonical_lane:{early_public_canonical_lane}',
                'selected_tools': list(dict.fromkeys([*preview.selected_tools, 'get_public_school_profile'])),
                'needs_authentication': False,
            }
        )
        execution_reason = preview.reason
        evidence_pack = build_structured_tool_evidence_pack(
            selected_tools=preview.selected_tools,
            slice_name=plan.slice_name,
            summary='Resposta canônica pública resolvida antes do roteamento estruturado genérico.',
        )
    elif hypothetical_public_pricing_direct:
        message_text, public_plan = hypothetical_public_pricing_direct
        deterministic_fallback_text = message_text
        preview = preview.model_copy(
            update={
                'mode': OrchestrationMode.structured_tool,
                'reason': 'python_functions_native_pricing_projection',
                'selected_tools': list(
                    dict.fromkeys([*preview.selected_tools, 'get_public_school_profile', 'project_public_pricing'])
                ),
            }
        )
        execution_reason = 'python_functions_native_pricing_projection'
        evidence_pack = build_structured_tool_evidence_pack(
            selected_tools=preview.selected_tools,
            slice_name=plan.slice_name,
            summary='Resposta grounded em simulacao publica deterministica de precificacao.',
        )
    elif contextual_public_answer:
        contextual_public_reason = (
            'python_functions_native_public_compound'
            if rt._has_public_multi_intent_signal(request.message)
            else 'python_functions_native_contextual_public_answer'
        )
        message_text = contextual_public_answer
        deterministic_fallback_text = contextual_public_answer
        preview = preview.model_copy(
            update={
                'mode': OrchestrationMode.structured_tool,
                'reason': contextual_public_reason,
                'selected_tools': list(dict.fromkeys([*preview.selected_tools, 'get_public_school_profile'])),
            }
        )
        execution_reason = contextual_public_reason
        evidence_pack = build_structured_tool_evidence_pack(
            selected_tools=preview.selected_tools,
            slice_name=plan.slice_name,
            summary=(
                'Resposta direta grounded em fatos publicos canonicos com decomposicao semantica de pedido composto.'
                if contextual_public_reason == 'python_functions_native_public_compound'
                else 'Resposta direta grounded em fatos publicos canonicos.'
            ),
        )
    elif unpublished_public_answer:
        message_text = unpublished_public_answer
        deterministic_fallback_text = unpublished_public_answer
        preview = preview.model_copy(
            update={
                'mode': OrchestrationMode.structured_tool,
                'reason': 'python_functions_native_public_unpublished_fact',
                'selected_tools': list(dict.fromkeys([*preview.selected_tools, 'get_public_school_profile'])),
            }
        )
        execution_reason = 'python_functions_native_public_unpublished_fact'
        evidence_pack = build_structured_tool_evidence_pack(
            selected_tools=preview.selected_tools,
            slice_name=plan.slice_name,
            summary='Pergunta publica valida, mas o dado solicitado nao esta publicado oficialmente.',
        )
    elif preview.mode is OrchestrationMode.deny:
        message_text = rt._compose_deterministic_answer(
            request_message=request.message,
            preview=preview,
            retrieval_hits=[],
            citations=[],
            calendar_events=[],
            query_hints=set(),
        )
        deterministic_fallback_text = message_text
        execution_reason = 'python_functions_native_access_deny'
        evidence_pack = build_direct_answer_evidence_pack(
            strategy='deny',
            summary='Resposta bloqueada por regra de acesso antes da composicao documental.',
            supports=[
                MessageEvidenceSupport(
                    kind='guardrail',
                    label='restricted_documents',
                    detail='consulta a documento interno sem autorizacao',
                )
            ],
        )
    elif preview.mode is OrchestrationMode.structured_tool:
        public_plan_sink: dict[str, Any] = {}
        resolved_public_plan = None
        if analysis_message.strip() != str(request.message).strip():
            try:
                resolved_public_plan = await rt._resolve_public_institution_plan(
                    settings=settings,
                    message=analysis_message,
                    preview=preview,
                    conversation_context=conversation_context,
                    school_profile=school_profile,
                )
            except Exception:
                resolved_public_plan = None
        message_text = await rt._compose_structured_tool_answer(
            settings=settings,
            request=request,
            analysis_message=analysis_message,
            preview=preview,
            actor=actor,
            school_profile=school_profile,
            conversation_context=conversation_context,
            public_plan_sink=public_plan_sink,
            resolved_public_plan=resolved_public_plan,
            prefer_fast_public_path=effective_path_profile.prefer_fast_public_path,
        )
        public_plan = public_plan_sink.get('plan')
        deterministic_fallback_text = str(public_plan_sink.get('deterministic_text') or message_text)
        execution_reason = f'python_functions_native_structured:{preview.classification.domain.value}'
        evidence_pack = build_structured_tool_evidence_pack(
            selected_tools=preview.selected_tools,
            slice_name=plan.slice_name,
            summary=f'Resposta grounded em tools estruturadas do dominio {preview.classification.domain.value}.',
        )
    elif preview.mode is OrchestrationMode.hybrid_retrieval:
        used_canonical_lane = False
        restricted_document_query = (
            preview.classification.access_tier is AccessTier.authenticated
            and looks_like_restricted_document_query(request.message)
            and can_read_restricted_documents(request.user)
        )
        canonical_lane = (
            match_public_canonical_lane(analysis_message)
            if preview.classification.access_tier is AccessTier.public
            else None
        ) or (
            match_public_canonical_lane(request.message)
            if preview.classification.access_tier is AccessTier.public
            else None
        )
        if canonical_lane:
            lane_answer = (
                compose_public_conduct_policy_contextual_answer(
                    request.message,
                    profile=school_profile,
                )
                if canonical_lane == 'public_bundle.conduct_frequency_punctuality'
                else None
            ) or compose_public_canonical_lane_answer(canonical_lane, profile=school_profile)
            if lane_answer:
                message_text = lane_answer
                deterministic_fallback_text = message_text
                preview = preview.model_copy(
                    update={
                        'reason': f'python_functions_native_canonical_lane:{canonical_lane}',
                    }
                )
                execution_reason = preview.reason
                used_canonical_lane = True
                evidence_pack = build_direct_answer_evidence_pack(
                    summary='Resposta canônica grounded em um bundle documental público conhecido.',
                    supports=[
                        MessageEvidenceSupport(
                            kind='canonical_lane',
                            label=canonical_lane,
                            detail='Lane canônica pública selecionada antes do retrieval pesado.',
                        )
                    ],
                )
                retrieval_hits = []
                citations = []
        if restricted_document_query:
            retrieval_service = get_retrieval_service(
                database_url=settings.database_url,
                qdrant_url=settings.qdrant_url,
                collection_name=settings.qdrant_documents_collection,
                embedding_model=settings.document_embedding_model,
                enable_query_variants=settings.retrieval_enable_query_variants,
                enable_late_interaction_rerank=settings.retrieval_enable_late_interaction_rerank,
                late_interaction_model=settings.retrieval_late_interaction_model,
                candidate_pool_size=settings.retrieval_candidate_pool_size,
                cheap_candidate_pool_size=settings.retrieval_cheap_candidate_pool_size,
                deep_candidate_pool_size=settings.retrieval_deep_candidate_pool_size,
                rerank_fused_weight=settings.retrieval_rerank_fused_weight,
                rerank_late_interaction_weight=settings.retrieval_rerank_late_interaction_weight,
            )
            search = retrieval_service.hybrid_search(
                query=analysis_message,
                top_k=5,
                visibility='restricted',
                category=None,
            )
            retrieval_context_pack = search.context_pack
            retrieval_hits = select_relevant_restricted_hits(analysis_message, list(search.hits))
            citations = rt._collect_citations(retrieval_hits)
            if retrieval_hits:
                message_text = compose_restricted_document_grounded_answer_for_query(
                    request.message,
                    retrieval_hits,
                ) or ''
                deterministic_fallback_text = message_text
                execution_reason = 'python_functions_native_restricted_document_search'
            else:
                message_text = compose_restricted_document_no_match_answer(request.message)
                deterministic_fallback_text = message_text
                execution_reason = 'python_functions_native_restricted_document_no_match'
            evidence_pack = build_retrieval_evidence_pack(
                citations=citations,
                selected_tools=preview.selected_tools,
                retrieval_backend=RetrievalBackend.qdrant_hybrid,
                summary='Resposta grounded em retrieval restrito autenticado no runtime nativo python_functions.',
            )
        elif not used_canonical_lane:
            retrieval_service = get_retrieval_service(
                database_url=settings.database_url,
                qdrant_url=settings.qdrant_url,
                collection_name=settings.qdrant_documents_collection,
                embedding_model=settings.document_embedding_model,
                enable_query_variants=settings.retrieval_enable_query_variants,
                enable_late_interaction_rerank=settings.retrieval_enable_late_interaction_rerank,
                late_interaction_model=settings.retrieval_late_interaction_model,
                candidate_pool_size=settings.retrieval_candidate_pool_size,
                cheap_candidate_pool_size=settings.retrieval_cheap_candidate_pool_size,
                deep_candidate_pool_size=settings.retrieval_deep_candidate_pool_size,
                rerank_fused_weight=settings.retrieval_rerank_fused_weight,
                rerank_late_interaction_weight=settings.retrieval_rerank_late_interaction_weight,
            )
            search = retrieval_service.hybrid_search(
                query=analysis_message,
                top_k=4,
                visibility='public',
                category=None,
            )
            retrieval_context_pack = search.context_pack
            query_hints = {
                *rt._extract_public_entity_hints(request.message),
                *rt._extract_public_entity_hints(analysis_message),
            }
            retrieval_hits = list(search.hits)
            if rt._retrieval_hits_cover_query_hints(retrieval_hits, query_hints):
                retrieval_hits = rt._filter_retrieval_hits_by_query_hints(retrieval_hits, query_hints)
            citations = rt._collect_citations(retrieval_hits)
            public_answerability = rt._assess_public_answerability(
                analysis_message,
                retrieval_hits,
                query_hints,
            )
            if preview.classification.domain is QueryDomain.calendar:
                calendar_events = await rt._fetch_public_calendar(settings=settings)

            if not retrieval_hits:
                message_text = rt._compose_public_gap_answer(query_hints)
                deterministic_fallback_text = message_text
            elif not public_answerability.enough_support:
                message_text = rt._compose_answerability_gap_answer(public_answerability, request.message)
                deterministic_fallback_text = message_text
            else:
                deterministic_fallback_text = rt._compose_deterministic_answer(
                    request_message=request.message,
                    preview=preview,
                    retrieval_hits=retrieval_hits,
                    citations=citations,
                    calendar_events=calendar_events,
                    query_hints=query_hints,
                )
                llm_text = await compose_python_functions_with_provider(
                    settings=settings,
                    request_message=request.message,
                    analysis_message=analysis_message,
                    preview=preview,
                    citations=citations,
                    calendar_events=calendar_events,
                    conversation_context=conversation_context,
                    school_profile=school_profile,
                    context_pack=retrieval_context_pack,
                )
                if llm_text:
                    llm_stages.append('answer_composition')
                message_text = llm_text or deterministic_fallback_text
            execution_reason = 'python_functions_native_public_retrieval'
            evidence_pack = build_retrieval_evidence_pack(
                citations=citations,
                selected_tools=preview.selected_tools,
                retrieval_backend=RetrievalBackend.qdrant_hybrid,
                summary='Resposta grounded em retrieval hibrida com reranqueamento compartilhado.',
            )
    else:  # pragma: no cover - native path is intentionally bounded
        return None

    retrieval_backend = preview.retrieval_backend
    if preview.mode is OrchestrationMode.hybrid_retrieval:
        retrieval_backend = RetrievalBackend.qdrant_hybrid

    final_polish_decision = build_final_polish_decision(
        settings=settings,
        stack_name=engine_name,
        request=request,
        preview=preview,
        response_reason=execution_reason,
        llm_stages=llm_stages,
        citations_count=len(citations),
        support_count=0,
        retrieval_backend=retrieval_backend,
    )
    final_polish_applied = False
    final_polish_changed_text = False
    final_polish_preserved_fallback = False
    if final_polish_decision.apply_polish:
        original_text = message_text
        raw_polished_text = await polish_python_functions_with_provider(
            settings=settings,
            request_message=request.message,
            preview=preview,
            draft_text=message_text,
            conversation_context=conversation_context,
            school_profile=school_profile,
        )
        polished_text = rt._preserve_capability_anchor_terms(
            original_text=original_text,
            polished_text=raw_polished_text,
            request_message=request.message,
        )
        final_polish_preserved_fallback = bool(
            raw_polished_text
            and polished_text == original_text
            and rt._normalize_text(raw_polished_text) != rt._normalize_text(original_text)
        )
        if polished_text:
            llm_stages.append('structured_polish')
            final_polish_applied = True
            final_polish_changed_text = rt._normalize_text(polished_text) != rt._normalize_text(original_text)
            message_text = polished_text
    if final_polish_decision.run_response_critic:
        revised_text = await revise_python_functions_with_provider(
            settings=settings,
            request_message=request.message,
            preview=preview,
            draft_text=message_text,
            conversation_context=conversation_context,
            school_profile=school_profile,
        )
        if revised_text:
            llm_stages.append('response_critic')
            message_text = revised_text

    verifier_slot_memory = rt._build_conversation_slot_memory(
        actor=actor,
        profile=school_profile,
        conversation_context=conversation_context,
        request_message=request.message,
        public_plan=public_plan,
        preview=preview,
    )
    verification, semantic_judge_used = await verify_python_functions_answer_against_contract(
        settings=settings,
        request_message=request.message,
        preview=preview,
        candidate_text=message_text,
        deterministic_fallback_text=deterministic_fallback_text,
        public_plan=public_plan,
        slot_memory=verifier_slot_memory,
    )
    if semantic_judge_used and 'answer_verifier_judge' not in llm_stages:
        llm_stages.append('answer_verifier_judge')
    if not verification.valid and deterministic_fallback_text:
        message_text = deterministic_fallback_text
        answer_verifier_fallback_used = True

    if citations:
        sources = rt._render_source_lines(citations)
        if sources and sources not in message_text:
            message_text = f'{message_text}\n\n{sources}'
    message_text = rt._normalize_response_wording(message_text)
    llm_forced_mode = rt._llm_forced_mode_enabled(settings=settings, request=request)

    candidate_chosen = 'documentary_synthesis' if llm_stages else 'deterministic'
    candidate_reason = execution_reason
    retrieval_probe_topic = None
    response_cache_hit = False
    response_cache_kind = None

    if (
        getattr(settings, 'candidate_chooser_enabled', True)
        and preview.classification.access_tier is AccessTier.public
        and deterministic_fallback_text
    ):
        canonical_lane = match_public_canonical_lane(request.message)
        retrieval_probe_search = None
        if retrieval_hits:
            retrieval_probe_search = type('RetrievalProbeSearch', (), {'hits': retrieval_hits, 'document_groups': [], 'query_plan': None})()
        elif (
            canonical_lane is None
            and getattr(settings, 'retrieval_aware_routing_enabled', True)
            and rt._looks_like_public_documentary_open_query(request.message)
        ):
            try:
                retrieval_service = get_retrieval_service(
                    database_url=settings.database_url,
                    qdrant_url=settings.qdrant_url,
                    collection_name=settings.qdrant_documents_collection,
                    embedding_model=settings.document_embedding_model,
                    enable_query_variants=settings.retrieval_enable_query_variants,
                    enable_late_interaction_rerank=settings.retrieval_enable_late_interaction_rerank,
                    late_interaction_model=settings.retrieval_late_interaction_model,
                    candidate_pool_size=settings.retrieval_candidate_pool_size,
                    cheap_candidate_pool_size=settings.retrieval_cheap_candidate_pool_size,
                    deep_candidate_pool_size=settings.retrieval_deep_candidate_pool_size,
                    rerank_fused_weight=settings.retrieval_rerank_fused_weight,
                    rerank_late_interaction_weight=settings.retrieval_rerank_late_interaction_weight,
                )
                retrieval_probe_search = retrieval_service.hybrid_search(
                    query=analysis_message,
                    top_k=3,
                    visibility='public',
                    category='public_docs',
                    profile=RetrievalProfile.cheap,
                )
            except Exception:
                retrieval_probe_search = None
        probe = build_public_evidence_probe(
            message=request.message,
            canonical_lane=canonical_lane,
            primary_act=public_plan.conversation_act if public_plan is not None else 'canonical_fact',
            secondary_acts=public_plan.secondary_acts if public_plan is not None else (),
            evidence_pack=evidence_pack,
            retrieval_search=retrieval_probe_search,
        )
        retrieval_probe_topic = probe.topic
        telemetry_snapshot = get_stack_telemetry_snapshot('python_functions')
        serving_policy = build_public_serving_policy(
            settings=settings,
            stack_name='python_functions',
            request=request,
            probe=probe,
            load_snapshot=LoadSnapshot(
                llm_forced_mode=llm_forced_mode,
                recent_request_count=telemetry_snapshot.recent_request_count,
                recent_p95_latency_ms=telemetry_snapshot.recent_p95_latency_ms,
                recent_timeout_rate=telemetry_snapshot.recent_timeout_rate,
                recent_error_rate=telemetry_snapshot.recent_error_rate,
                recent_cache_hit_rate=telemetry_snapshot.recent_cache_hit_rate,
                recent_used_llm_rate=telemetry_snapshot.recent_used_llm_rate,
            ),
        )
        deterministic_candidate = build_response_candidate(
            kind='deterministic',
            text=deterministic_fallback_text,
            reason='python_functions_deterministic_fallback',
            retrieval_backend=RetrievalBackend.none,
            selected_tools=tuple(preview.selected_tools),
            source_count=max(1, len(citations)),
            support_count=evidence_pack.support_count if evidence_pack is not None else 0,
        )
        current_candidate = build_response_candidate(
            kind='documentary_synthesis' if llm_stages else 'deterministic',
            text=message_text,
            reason=execution_reason,
            used_llm=bool(llm_stages),
            llm_stages=tuple(llm_stages),
            retrieval_backend=retrieval_backend,
            selected_tools=tuple(preview.selected_tools),
            source_count=max(1, len(citations)),
            support_count=evidence_pack.support_count if evidence_pack is not None else 0,
        )
        chosen_candidate = choose_best_candidate(
            candidates=[candidate for candidate in (deterministic_candidate, current_candidate) if candidate is not None],
            probe=probe,
            policy=serving_policy,
        )
        if chosen_candidate is not None:
            message_text = chosen_candidate.candidate.text
            candidate_chosen = chosen_candidate.candidate.kind
            candidate_reason = chosen_candidate.chooser_reason
            if getattr(settings, 'public_response_cache_enabled', True) and serving_policy.prefer_cache:
                store_cached_public_response(
                    message=request.message,
                    text=message_text,
                    canonical_lane=canonical_lane,
                    topic=probe.topic,
                    evidence_fingerprint=probe.evidence_fingerprint,
                    candidate_kind=candidate_chosen,
                    reason=candidate_reason,
                    ttl_seconds=float(getattr(settings, 'public_response_cache_ttl_seconds', 300.0)),
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
        public_plan=public_plan,
        request_message=request.message,
        message_text=message_text,
        citations_count=len(citations),
        suggested_reply_count=len(suggested_replies),
        visual_asset_count=0,
        answer_verifier_valid=verification.valid,
        answer_verifier_reason=verification.reason,
        answer_verifier_fallback_used=answer_verifier_fallback_used,
        deterministic_fallback_available=bool(deterministic_fallback_text),
        answer_verifier_judge_used=semantic_judge_used,
        langgraph_trace_metadata={
            'python_functions_native_reason': execution_reason,
            'python_functions_evidence_strategy': evidence_pack.strategy if evidence_pack else '',
            'python_functions_evidence_support_count': evidence_pack.support_count if evidence_pack else 0,
        },
    )

    selected_tools = list(
        dict.fromkeys(
            [
                *preview.selected_tools,
                'python_functions_native_runtime',
            ]
        )
    )
    response = MessageResponse(
        message_text=message_text,
        mode=preview.mode,
        classification=preview.classification,
        retrieval_backend=retrieval_backend,
        selected_tools=selected_tools,
        citations=citations,
        visual_assets=[],
        suggested_replies=suggested_replies,
        calendar_events=calendar_events,
        evidence_pack=evidence_pack,
        needs_authentication=preview.needs_authentication,
        graph_path=[
            *preview.graph_path,
            'python_functions:native_runtime',
            f'kernel:{plan.stack_name}',
        ],
        risk_flags=preview.risk_flags,
        reason=execution_reason,
        used_llm=bool(llm_stages),
        llm_stages=list(dict.fromkeys(llm_stages)),
        final_polish_eligible=final_polish_decision.eligible,
        final_polish_applied=final_polish_applied,
        final_polish_mode=final_polish_decision.mode,
        final_polish_reason=final_polish_decision.reason,
        final_polish_changed_text=final_polish_changed_text,
        final_polish_preserved_fallback=final_polish_preserved_fallback,
        candidate_chosen=candidate_chosen,
        candidate_reason=candidate_reason,
        retrieval_probe_topic=retrieval_probe_topic,
        response_cache_hit=response_cache_hit,
        response_cache_kind=response_cache_kind,
    )
    record_stack_outcome(
        stack_name='python_functions',
        latency_ms=(monotonic() - started_at) * 1000,
        success=True,
        timeout=False,
        cache_hit=response_cache_hit,
        used_llm=bool(llm_stages),
        candidate_kind=candidate_chosen,
    )
    reflection = KernelReflection(
        grounded=verification.valid,
        verifier_reason=verification.reason,
        fallback_used=answer_verifier_fallback_used,
        answer_judge_used=semantic_judge_used,
        notes=[
            f'route:{preview.mode.value}',
            f'slice:{plan.slice_name}',
            f'evidence:{evidence_pack.strategy}' if evidence_pack is not None else 'evidence:none',
            *plan.plan_notes,
        ],
    )
    return KernelRunResult(
        plan=plan,
        reflection=reflection,
        response=response.model_dump(mode='json'),
    )
