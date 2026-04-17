from __future__ import annotations

# ruff: noqa: F401,F403,F405

LOCAL_EXTRACTED_NAMES = {'maybe_execute_python_functions_native_plan'}

from . import python_functions_native_runtime as _native
from .retrieval_capability_policy import (
    build_retrieval_trace_metadata,
    resolve_retrieval_execution_policy,
)
from .semantic_ingress_runtime import (
    apply_turn_frame_preview,
    build_turn_frame_public_plan,
    maybe_resolve_turn_frame,
    resolve_turn_frame_authenticated_flag,
)
from .turn_frame_policy import (
    is_external_public_facility_turn_frame,
    is_restricted_document_turn_frame,
    is_scope_boundary_turn_frame,
)


def _refresh_native_namespace() -> None:
    for name, value in vars(_native).items():
        if name.startswith('__') or name in LOCAL_EXTRACTED_NAMES:
            continue
        globals()[name] = value


async def maybe_execute_python_functions_native_plan(
    *,
    request: Any,
    settings: Any,
    plan: KernelPlan,
    engine_name: str,
    engine_mode: str,
    path_profile: PathExecutionProfile | None = None,
) -> KernelRunResult | None:
    _refresh_native_namespace()
    started_at = monotonic()
    effective_path_profile = path_profile or get_path_execution_profile(engine_name)
    actor = await rt._fetch_actor_context(settings=settings, telegram_chat_id=request.telegram_chat_id)
    actor = rt._build_effective_actor_context(actor, request.user)
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
    from .public_orchestration_runtime import _resolve_deterministic_public_guardrail_answer

    preview = plan.preview.model_copy(deep=True)
    semantic_preview = preview.model_copy(deep=True)
    semantic_ingress_plan = await maybe_resolve_semantic_ingress_plan(
        settings=settings,
        request_message=request.message,
        conversation_context=conversation_context,
        preview=semantic_preview,
        stack_label='python_functions',
    )
    if (
        (semantic_ingress_plan is None or not is_terminal_semantic_ingress_plan(semantic_ingress_plan))
        and actor is not None
        and request.user.authenticated
        and not rt._is_high_confidence_public_profile_query(
            request.message,
            conversation_context=conversation_context,
            school_profile=school_profile,
        )
    ):
        rt._apply_protected_domain_rescue(
            preview=preview,
            actor=actor,
            message=request.message,
            conversation_context=conversation_context,
        )
    if semantic_ingress_plan is not None:
        ingress_base_preview = semantic_preview if is_terminal_semantic_ingress_plan(semantic_ingress_plan) else preview
        preview = apply_semantic_ingress_preview(
            preview=ingress_base_preview,
            plan=semantic_ingress_plan,
            stack_name='python_functions',
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
    retrieval_trace_metadata: dict[str, Any] | None = None
    semantic_judge_used = False
    llm_stages: list[str] = []
    answer_verifier_fallback_used = False
    semantic_ingress_public_plan = (
        build_semantic_ingress_public_plan(semantic_ingress_plan)
        if semantic_ingress_plan is not None
        else None
    )
    turn_frame = None
    turn_frame_public_plan = None
    turn_frame_authenticated = resolve_turn_frame_authenticated_flag(
        request_message=request.message,
        authenticated=bool(getattr(request.user, 'authenticated', False)),
        actor=actor,
    )
    if semantic_ingress_plan is not None:
        llm_stages.append('semantic_ingress_classifier')
    if semantic_ingress_plan is None or not is_terminal_semantic_ingress_plan(semantic_ingress_plan):
        turn_frame = await maybe_resolve_turn_frame(
            settings=settings,
            request_message=request.message,
            conversation_context=conversation_context,
            preview=preview,
            stack_label='python_functions',
            authenticated=turn_frame_authenticated,
        )
        if turn_frame is not None:
            preview = apply_turn_frame_preview(
                preview=preview,
                turn_frame=turn_frame,
                stack_name='python_functions',
            )
            turn_frame_public_plan = build_turn_frame_public_plan(turn_frame)
            llm_stages.append('turn_frame_classifier')
            if (
                is_restricted_document_turn_frame(turn_frame)
                and can_read_restricted_documents(request.user)
            ):
                preview = preview.model_copy(
                    update={
                        'mode': OrchestrationMode.hybrid_retrieval,
                        'classification': IntentClassification(
                            domain=QueryDomain.institution,
                            access_tier=AccessTier.sensitive,
                            confidence=max(0.92, float(getattr(turn_frame, 'confidence', 0.92) or 0.92)),
                            reason='python_functions_turn_frame:restricted_document',
                        ),
                        'reason': 'python_functions_turn_frame:restricted_document',
                        'selected_tools': list(dict.fromkeys([*preview.selected_tools, 'search_documents'])),
                        'needs_authentication': True,
                    }
                )
    evidence_pack = None
    semantic_ingress_terminal_answer = None
    external_turn_boundary_answer = None
    generic_turn_boundary_answer = None
    if (
        semantic_ingress_public_plan is not None
        and is_terminal_semantic_ingress_plan(semantic_ingress_plan)
    ):
        semantic_ingress_terminal_answer = str(
            await rt._compose_public_profile_answer_agentic(
                settings=settings,
                profile=school_profile,
                actor=actor,
                message=request.message,
                original_message=request.message,
                conversation_context=conversation_context,
                semantic_plan=semantic_ingress_public_plan,
            )
            or ''
        ).strip()
    elif (
        turn_frame_public_plan is not None
        and turn_frame is not None
        and getattr(turn_frame, 'scope', '') == 'public'
        and not is_scope_boundary_turn_frame(turn_frame)
    ):
        semantic_ingress_terminal_answer = str(
            rt._compose_public_profile_answer(
                school_profile,
                request.message,
                actor=actor,
                original_message=request.message,
                conversation_context=conversation_context,
                semantic_plan=turn_frame_public_plan,
            )
            or ''
        ).strip()
    elif (
        turn_frame is not None
        and is_external_public_facility_turn_frame(turn_frame)
    ):
        external_turn_boundary_answer = rt._compose_external_public_facility_boundary_answer(
            school_profile,
            facility_label='uma biblioteca publica externa',
            conversation_context=conversation_context,
        )
    elif (
        turn_frame is not None
        and is_scope_boundary_turn_frame(turn_frame)
        and not (
            is_restricted_document_turn_frame(turn_frame)
            and can_read_restricted_documents(request.user)
        )
    ):
        generic_turn_boundary_answer = rt._compose_scope_boundary_answer(
            school_profile,
            conversation_context=conversation_context,
        )

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
    restricted_document_query = bool(
        looks_like_restricted_document_query(request.message)
        and can_read_restricted_documents(request.user)
    )
    protected_domain_hint = (
        rt._explicit_protected_domain_hint(
            request.message,
            actor=actor,
            conversation_context=conversation_context,
        )
        if getattr(request.user, 'authenticated', False)
        else None
    )
    protected_attendance_focus_followup = bool(
        getattr(request.user, 'authenticated', False)
        and (
            rt._looks_like_family_attendance_student_focus_followup(
                actor,
                request.message,
                conversation_context=conversation_context,
            )
            or (
                actor
                and (
                    rt._matching_students_in_text(rt._linked_students(actor), request.message)
                    or rt._student_focus_candidate(actor, request.message)
                )
                and any(
                    rt._message_matches_term(rt._normalize_text(request.message), term)
                    for term in {
                        'mantendo o contexto',
                        'continuando a analise',
                        'continuando a análise',
                        'recorte so',
                        'recorte só',
                        'corta para',
                        'isole',
                    }
                )
                and any(
                    rt._message_matches_term(rt._normalize_text(request.message), term)
                    for term in {
                        'frequencia',
                        'frequência',
                        'faltas',
                        'falta',
                        'ausencias',
                        'ausências',
                        'presenca',
                        'presença',
                        'atrasos',
                        'risco',
                        'mais concreto',
                        'principal alerta',
                    }
                )
            )
        )
    )
    normalized_request_message = rt._normalize_text(request.message)
    explicit_protected_academic_request = bool(
        getattr(request.user, 'authenticated', False)
        and (
            rt._looks_like_family_academic_aggregate_query(request.message)
            or rt._looks_like_academic_progression_query(
                request.message,
                conversation_context=conversation_context,
            )
        )
    )
    protected_message_override = any(
        term in normalized_request_message
        for term in {
            'mais vulneravel',
            'mais vulnerável',
            'qual materia esta melhor',
            'qual matéria está melhor',
            'qual materia esta pior',
            'qual matéria está pior',
            'o que falta para fechar a media',
            'o que falta para fechar a média',
            'mantendo o contexto',
            'corta para',
            'recorte so',
            'recorte só',
            'resuma',
            'resume',
        }
    ) and any(
        term in normalized_request_message
        for term in {
            'frequencia',
            'frequência',
            'risco',
            'media minima',
            'média mínima',
            'fisica',
            'física',
        }
    )
    protected_contextual_skip = bool(
        getattr(request.user, 'authenticated', False)
        and (
            protected_message_override
            or rt._should_skip_public_contextual_answer(
                request.message,
                actor=actor,
                conversation_context=conversation_context,
            )
        )
    )
    forced_protected_domain = protected_domain_hint
    turn_frame_scope = str(getattr(turn_frame, 'scope', '') or '').strip().lower()
    turn_frame_domain = str(getattr(turn_frame, 'domain', '') or '').strip().lower()
    if forced_protected_domain not in {QueryDomain.academic, QueryDomain.finance}:
        if turn_frame_scope and turn_frame_scope != 'public':
            if turn_frame_domain == QueryDomain.academic.value:
                forced_protected_domain = QueryDomain.academic
            elif turn_frame_domain == QueryDomain.finance.value:
                forced_protected_domain = QueryDomain.finance
    if (
        forced_protected_domain not in {QueryDomain.academic, QueryDomain.finance}
        and bool(getattr(request.user, 'authenticated', False))
        and (
            explicit_protected_academic_request
            or rt._looks_like_family_attendance_aggregate_query(request.message)
            or protected_attendance_focus_followup
            or protected_message_override
        )
    ):
        forced_protected_domain = QueryDomain.academic
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

    if forced_protected_domain in {QueryDomain.academic, QueryDomain.finance}:
        preview = preview.model_copy(
            update={
                'mode': OrchestrationMode.structured_tool,
                'classification': IntentClassification(
                    domain=forced_protected_domain,
                    access_tier=AccessTier.authenticated,
                    confidence=max(
                        0.92,
                        float(getattr(preview.classification, 'confidence', 0.0) or 0.0),
                    ),
                    reason=f'python_functions_native_protected_focus:{forced_protected_domain.value}',
                ),
                'reason': f'python_functions_native_protected_focus:{forced_protected_domain.value}',
                'needs_authentication': True,
            }
        )
    preview = rt._align_protected_preview_tools(preview)
    preview_graph_path = tuple(getattr(preview, 'graph_path', ()) or ())
    protected_preview_context = (
        bool(getattr(request.user, 'authenticated', False))
        and (
            preview.classification.domain in {QueryDomain.academic, QueryDomain.finance}
            or any(str(node).startswith('turn_frame:protected.') for node in preview_graph_path)
        )
    )
    public_surface_context = (
        preview.classification.access_tier is AccessTier.public
        or not bool(getattr(request.user, 'authenticated', False))
    ) and not protected_preview_context and protected_domain_hint is None and not protected_contextual_skip
    deterministic_public_guardrail = None
    if (
        teacher_scope_answer is None
        and authenticated_account_scope_answer is None
        and meta_repair_answer is None
        and public_surface_context
        and not protected_attendance_focus_followup
        and not restricted_document_query
    ):
        deterministic_public_guardrail = _resolve_deterministic_public_guardrail_answer(
            request.message,
            school_profile=school_profile,
            conversation_context=conversation_context,
        )

    early_public_canonical_lane = None
    early_public_canonical_answer = None
    if (
        teacher_scope_answer is None
        and authenticated_account_scope_answer is None
        and meta_repair_answer is None
        and public_surface_context
        and deterministic_public_guardrail is None
        and not restricted_document_query
    ):
        if rt._is_public_teacher_identity_query(request.message) or rt._is_public_teacher_directory_follow_up(
            request.message,
            conversation_context,
        ):
            early_public_canonical_lane = 'public_bundle.teacher_directory_boundary'
        else:
            early_public_canonical_lane = (
                match_public_canonical_lane(request.message)
                if not protected_attendance_focus_followup and not protected_contextual_skip
                else None
            ) or (
                match_public_canonical_lane(analysis_message)
                if not protected_attendance_focus_followup and not protected_contextual_skip
                else None
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
    if (
        teacher_scope_answer is None
        and authenticated_account_scope_answer is None
        and meta_repair_answer is None
        and public_surface_context
        and deterministic_public_guardrail is None
        and not protected_attendance_focus_followup
        and not restricted_document_query
    ):
        contextual_public_answer = await _maybe_contextual_public_direct_answer(
            request=request,
            analysis_message=analysis_message,
            preview=preview,
            settings=settings,
            school_profile=school_profile,
            conversation_context=conversation_context,
            actor=actor,
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

    if deterministic_public_guardrail is not None:
        message_text = deterministic_public_guardrail.answer_text
        deterministic_fallback_text = deterministic_public_guardrail.answer_text
        preview = preview.model_copy(
            update={
                'mode': OrchestrationMode.structured_tool,
                'classification': IntentClassification(
                    domain=QueryDomain.institution,
                    access_tier=AccessTier.public,
                    confidence=0.99,
                    reason=deterministic_public_guardrail.reason,
                ),
                'reason': deterministic_public_guardrail.reason,
                'selected_tools': list(
                    dict.fromkeys([*preview.selected_tools, *list(deterministic_public_guardrail.selected_tools)])
                ),
                'needs_authentication': False,
            }
        )
        execution_reason = deterministic_public_guardrail.reason
        evidence_pack = build_direct_answer_evidence_pack(
            strategy='deterministic_public_guardrail',
            summary='Resposta pública determinística resolvida antes do roteamento generativo do python_functions.',
            supports=[
                MessageEvidenceSupport(
                    kind='policy',
                    label=deterministic_public_guardrail.reason,
                    detail='Boundary ou fato público não publicado resolvido por preflight determinístico.',
                )
            ],
        )
    elif external_turn_boundary_answer:
        message_text = external_turn_boundary_answer
        deterministic_fallback_text = external_turn_boundary_answer
        preview = preview.model_copy(
            update={
                'mode': OrchestrationMode.structured_tool,
                'classification': IntentClassification(
                    domain=QueryDomain.unknown,
                    access_tier=AccessTier.public,
                    confidence=0.99,
                    reason='python_functions_native_external_public_facility_boundary',
                ),
                'reason': 'python_functions_native_external_public_facility_boundary',
                'selected_tools': list(dict.fromkeys([*preview.selected_tools, 'get_public_school_profile'])),
                'needs_authentication': False,
            }
        )
        execution_reason = preview.reason
        evidence_pack = build_direct_answer_evidence_pack(
            strategy='scope_boundary',
            summary='Consulta explicita sobre entidade publica externa mantida fora do escopo institucional da escola.',
            supports=[
                MessageEvidenceSupport(
                    kind='policy',
                    label='external_public_facility_boundary',
                    detail='turn_frame marcou biblioteca publica externa como fora do escopo da escola',
                )
            ],
        )
    elif generic_turn_boundary_answer:
        message_text = generic_turn_boundary_answer
        deterministic_fallback_text = generic_turn_boundary_answer
        preview = preview.model_copy(
            update={
                'mode': OrchestrationMode.structured_tool,
                'classification': IntentClassification(
                    domain=QueryDomain.unknown,
                    access_tier=AccessTier.public,
                    confidence=max(0.88, float(getattr(turn_frame, 'confidence', 0.88) or 0.88)),
                    reason='python_functions_turn_frame:scope_boundary',
                ),
                'reason': 'python_functions_turn_frame:scope_boundary',
                'selected_tools': list(dict.fromkeys([*preview.selected_tools, 'get_public_school_profile'])),
                'needs_authentication': False,
            }
        )
        execution_reason = preview.reason
        evidence_pack = build_direct_answer_evidence_pack(
            strategy='scope_boundary',
            summary='Consulta fora do escopo escolar encerrada deterministicamente pelo turn frame compartilhado.',
            supports=[
                MessageEvidenceSupport(
                    kind='policy',
                    label='scope_boundary',
                    detail='turn_frame marcou a pergunta como fora do escopo da escola',
                )
            ],
        )
    elif semantic_ingress_terminal_answer:
        message_text = semantic_ingress_terminal_answer
        public_plan = semantic_ingress_public_plan or turn_frame_public_plan
        public_act = str(getattr(public_plan, 'conversation_act', '') or '').strip() or 'public_answer'
        deterministic_fallback_text = semantic_ingress_terminal_answer
        preview = preview.model_copy(
            update={
                'mode': OrchestrationMode.structured_tool,
                'classification': IntentClassification(
                    domain=QueryDomain.institution,
                    access_tier=AccessTier.public,
                    confidence=0.99,
                    reason=f'python_functions_native_semantic_ingress:{public_act}',
                ),
                'reason': f'python_functions_native_semantic_ingress:{public_act}',
                'selected_tools': list(dict.fromkeys([*preview.selected_tools, *list(getattr(public_plan, 'required_tools', ()))])),
                'needs_authentication': False,
            }
        )
        execution_reason = preview.reason
        evidence_pack = build_structured_tool_evidence_pack(
            selected_tools=preview.selected_tools,
            slice_name=plan.slice_name,
            summary='Ato terminal do semantic ingress resolvido deterministicamente antes do fallback institucional estruturado.',
        )
    elif teacher_scope_answer:
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
        if isinstance(school_profile, dict):
            resolved_public_plan = semantic_ingress_public_plan or turn_frame_public_plan
            if resolved_public_plan is None:
                resolved_public_plan = rt._build_public_institution_plan(
                    request.message,
                    list(dict.fromkeys([*preview.selected_tools, 'get_public_school_profile'])),
                    conversation_context=conversation_context,
                    school_profile=school_profile,
                )
            composed_public_answer = await rt._compose_public_profile_answer_agentic(
                settings=settings,
                profile=school_profile,
                actor=actor,
                message=request.message,
                original_message=request.message,
                conversation_context=conversation_context,
                semantic_plan=resolved_public_plan,
            )
            if composed_public_answer:
                message_text = composed_public_answer
                deterministic_fallback_text = composed_public_answer
                llm_stages.append('public_answer_composer')
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
        preserve_contextual_public_answer = bool(
            any(
                marker in rt._normalize_text(contextual_public_answer)
                for marker in ('fora do escopo da escola', 'nao tenho base aqui para informar esse dado externo')
            )
        )
        if isinstance(school_profile, dict):
            resolved_public_plan = semantic_ingress_public_plan or turn_frame_public_plan
            if resolved_public_plan is None:
                resolved_public_plan = rt._build_public_institution_plan(
                    request.message,
                    list(dict.fromkeys([*preview.selected_tools, 'get_public_school_profile'])),
                    conversation_context=conversation_context,
                    school_profile=school_profile,
                )
            if not preserve_contextual_public_answer:
                composed_public_answer = await rt._compose_public_profile_answer_agentic(
                    settings=settings,
                    profile=school_profile,
                    actor=actor,
                    message=request.message,
                    original_message=request.message,
                    conversation_context=conversation_context,
                    semantic_plan=resolved_public_plan,
                )
                if composed_public_answer:
                    message_text = composed_public_answer
                    deterministic_fallback_text = composed_public_answer
                    llm_stages.append('public_answer_composer')
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
        resolved_public_plan = semantic_ingress_public_plan or turn_frame_public_plan
        if resolved_public_plan is None and analysis_message.strip() != str(request.message).strip():
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
        canonical_lane = (
            match_public_canonical_lane(request.message)
            if (
                preview.classification.access_tier is AccessTier.public
                and not protected_attendance_focus_followup
                and not protected_contextual_skip
                and not restricted_document_query
            )
            else None
        ) or (
            match_public_canonical_lane(analysis_message)
            if (
                preview.classification.access_tier is AccessTier.public
                and not protected_attendance_focus_followup
                and not protected_contextual_skip
                and not restricted_document_query
            )
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
            restricted_policy = resolve_retrieval_execution_policy(
                query=analysis_message,
                visibility='restricted',
                baseline_top_k=5,
                preview=preview,
                turn_frame=turn_frame,
                public_plan=semantic_ingress_public_plan or turn_frame_public_plan,
            )
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
            enable_cross_encoder_rerank=settings.retrieval_enable_cross_encoder_rerank,
            cross_encoder_model=settings.retrieval_cross_encoder_model,
            rerank_cross_encoder_weight=settings.retrieval_rerank_cross_encoder_weight,
            )
            search = retrieval_service.hybrid_search(
                query=analysis_message,
                top_k=restricted_policy.top_k,
                visibility='restricted',
                category=restricted_policy.category,
                profile=restricted_policy.profile,
            )
            retrieval_context_pack = search.context_pack
            retrieval_hits = retrieve_relevant_restricted_hits_with_fallback(
                retrieval_service,
                query=analysis_message,
                hits=list(search.hits),
                top_k=restricted_policy.top_k,
                visibility='restricted',
                category=restricted_policy.category,
            )
            citations = rt._collect_citations(retrieval_hits)
            retrieval_trace_metadata = build_retrieval_trace_metadata(
                visibility='restricted',
                policy=restricted_policy,
                search=search,
                selected_hit_count=len(retrieval_hits),
                citations_count=len(citations),
            )
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
            public_retrieval_policy = resolve_retrieval_execution_policy(
                query=analysis_message,
                visibility='public',
                baseline_top_k=4,
                preview=preview,
                turn_frame=turn_frame,
                public_plan=semantic_ingress_public_plan or turn_frame_public_plan,
            )
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
            enable_cross_encoder_rerank=settings.retrieval_enable_cross_encoder_rerank,
            cross_encoder_model=settings.retrieval_cross_encoder_model,
            rerank_cross_encoder_weight=settings.retrieval_rerank_cross_encoder_weight,
            )
            search = retrieval_service.hybrid_search(
                query=analysis_message,
                top_k=public_retrieval_policy.top_k,
                visibility='public',
                category=public_retrieval_policy.category,
                profile=public_retrieval_policy.profile,
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
            retrieval_trace_metadata = build_retrieval_trace_metadata(
                visibility='public',
                policy=public_retrieval_policy,
                search=search,
                selected_hit_count=len(retrieval_hits),
                citations_count=len(citations),
                query_hints=query_hints,
                hints_supported=rt._retrieval_hits_cover_query_hints(search.hits, query_hints),
                canonical_lane=canonical_lane,
                answerability=public_answerability,
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
    if (
        not verification.valid
        and deterministic_fallback_text
        and 'public_answer_composer' not in llm_stages
    ):
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
        and 'public_answer_composer' not in llm_stages
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
            enable_cross_encoder_rerank=settings.retrieval_enable_cross_encoder_rerank,
            cross_encoder_model=settings.retrieval_cross_encoder_model,
            rerank_cross_encoder_weight=settings.retrieval_rerank_cross_encoder_weight,
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
        engine_trace_metadata=retrieval_trace_metadata,
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
