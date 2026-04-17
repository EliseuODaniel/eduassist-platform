from __future__ import annotations

from dataclasses import dataclass, field

# ruff: noqa: F401,F403,F405

"""Top-level message response orchestration extracted from runtime.py.

Imported lazily from runtime.py after the shared helper namespace is fully
materialized, so the orchestrator can reuse the existing helper surface while
we continue decomposing the legacy module.
"""

from . import runtime_core as _runtime_core
from .retrieval_capability_policy import resolve_retrieval_execution_policy


def _export_runtime_core_namespace() -> None:
    for name, value in vars(_runtime_core).items():
        if name.startswith('__'):
            continue
        globals()[name] = value


_export_runtime_core_namespace()


@dataclass(slots=True)
class RuntimeRequestState:
    request: MessageResponseRequest
    actor: dict[str, Any] | None
    effective_user: UserContext
    effective_conversation_id: str | None
    conversation_context: Any
    context_payload: dict[str, Any] | None
    analysis_message: str
    school_profile: dict[str, Any] | None
    langgraph_artifacts: Any
    graph: Any
    langgraph_thread_id: str | None


@dataclass(slots=True)
class MessageResponseFlowState:
    retrieval_hits: list[Any] = field(default_factory=list)
    citations: list[MessageResponseCitation] = field(default_factory=list)
    visual_assets: list[MessageResponseVisualAsset] = field(default_factory=list)
    calendar_events: list[CalendarEventCard] = field(default_factory=list)
    query_hints: set[str] = field(default_factory=set)
    retrieval_supported: bool = True
    public_answerability: PublicAnswerabilityAssessment | None = None
    graph_rag_answer: dict[str, str] | None = None
    public_plan: PublicInstitutionPlan | None = None
    deterministic_fallback_text: str | None = None
    rescued_public_plan: PublicInstitutionPlan | None = None
    canonical_lane: str | None = None
    restricted_document_query: bool = False
    llm_text: str | None = None
    llm_stages: list[str] = field(default_factory=list)
    candidate_chosen: str | None = None
    candidate_reason: str | None = None
    retrieval_probe_topic: str | None = None
    response_cache_hit: bool = False
    response_cache_kind: str | None = None
    llm_forced_mode: bool = False
    public_canonical_lane_request: str | None = None


_PROTECTED_FOCUS_TOOLS = {
    'get_student_academic_summary',
    'get_student_upcoming_assessments',
    'get_student_attendance_timeline',
    'get_student_financial_summary',
}


def _coerce_preview_update(preview: Any, **update: Any) -> Any:
    if hasattr(preview, 'model_copy'):
        return preview.model_copy(update=update)
    for field_name, value in update.items():
        setattr(preview, field_name, value)
    return preview


def _preview_uses_protected_scope(preview: Any) -> bool:
    classification = getattr(preview, 'classification', None)
    if classification is None:
        return False
    graph_path = tuple(getattr(preview, 'graph_path', ()) or ())
    if any(str(node).startswith('turn_frame:protected.') for node in graph_path):
        return True
    selected_tools = {
        str(tool_name).strip()
        for tool_name in (getattr(preview, 'selected_tools', None) or [])
        if str(tool_name).strip()
    }
    if selected_tools & _PROTECTED_FOCUS_TOOLS:
        return True
    return (
        getattr(classification, 'domain', None) in {QueryDomain.academic, QueryDomain.finance}
        and getattr(classification, 'access_tier', None) is not AccessTier.public
    )


def _protected_domain_hint_for_message(
    *,
    message: str,
    actor: dict[str, Any] | None,
    conversation_context: dict[str, Any] | None,
) -> QueryDomain | None:
    from .public_orchestration_runtime import _explicit_protected_domain_hint

    return _explicit_protected_domain_hint(
        message,
        actor=actor,
        conversation_context=conversation_context,
    )


def _realign_preview_to_protected_domain(preview: Any, *, protected_domain: QueryDomain) -> Any:
    from .public_orchestration_runtime import (
        _align_protected_preview_tools,
        _protected_selected_tools_for_domain,
    )

    classification = IntentClassification(
        domain=protected_domain,
        access_tier=AccessTier.authenticated,
        confidence=max(
            0.92,
            float(getattr(getattr(preview, 'classification', None), 'confidence', 0.0) or 0.0),
        ),
        reason=f'deterministic_protected_{protected_domain.value}_focus',
    )
    updated_preview = _coerce_preview_update(
        preview,
        mode=OrchestrationMode.structured_tool,
        classification=classification,
        reason=f'deterministic_protected_{protected_domain.value}_focus',
        needs_authentication=True,
    )
    if hasattr(updated_preview, 'model_copy'):
        return _align_protected_preview_tools(updated_preview)
    return _coerce_preview_update(
        updated_preview,
        selected_tools=_protected_selected_tools_for_domain(protected_domain),
    )


def _should_apply_deterministic_scope_boundary(
    *,
    message: str,
    preview: Any,
    actor: dict[str, Any] | None,
    conversation_context: dict[str, Any] | None,
    authenticated: bool,
) -> bool:
    if looks_like_restricted_document_query(message):
        return False
    explicit_open_world = _is_explicit_open_world_scope_boundary_query(message)
    if explicit_open_world:
        return True
    if not (
        looks_like_scope_boundary_candidate(message)
        and not looks_like_school_scope_message(message)
    ):
        return False
    if not authenticated:
        return True
    protected_domain_hint = _protected_domain_hint_for_message(
        message=message,
        actor=actor,
        conversation_context=conversation_context,
    )
    if protected_domain_hint in {QueryDomain.academic, QueryDomain.finance}:
        return False
    return not _preview_uses_protected_scope(preview)


def _build_response(
    *,
    request: MessageResponseRequest,
    preview: Any,
    message_text: str,
    selected_tools: list[str],
    retrieval_backend: RetrievalBackend,
    citations: list[MessageResponseCitation],
    calendar_events: list[CalendarEventCard],
    visual_assets: list[MessageResponseVisualAsset],
    evidence_pack: MessageEvidencePack | None,
    suggested_replies: list[MessageResponseSuggestedReply],
    llm_stages: list[str],
    final_polish_decision: FinalPolishDecision | None = None,
    final_polish_applied: bool = False,
    final_polish_changed_text: bool = False,
    final_polish_preserved_fallback: bool = False,
    candidate_chosen: str | None = None,
    candidate_reason: str | None = None,
    retrieval_probe_topic: str | None = None,
    response_cache_hit: bool = False,
    response_cache_kind: str | None = None,
) -> MessageResponse:
    return MessageResponse(
        message_text=message_text,
        mode=preview.mode,
        classification=preview.classification,
        retrieval_backend=retrieval_backend,
        selected_tools=selected_tools,
        citations=citations,
        visual_assets=visual_assets,
        suggested_replies=suggested_replies,
        calendar_events=calendar_events,
        evidence_pack=evidence_pack,
        needs_authentication=preview.needs_authentication,
        graph_path=preview.graph_path,
        risk_flags=_build_runtime_risk_flags(
            request_message=request.message,
            message_text=message_text,
            preview=preview,
        ),
        reason=preview.reason,
        used_llm=bool(llm_stages),
        llm_stages=list(dict.fromkeys(llm_stages)),
        final_polish_eligible=final_polish_decision.eligible if final_polish_decision else False,
        final_polish_applied=final_polish_applied,
        final_polish_mode=final_polish_decision.mode if final_polish_decision else 'skip',
        final_polish_reason=final_polish_decision.reason
        if final_polish_decision
        else 'early_return',
        final_polish_changed_text=final_polish_changed_text,
        final_polish_preserved_fallback=final_polish_preserved_fallback,
        candidate_chosen=candidate_chosen,
        candidate_reason=candidate_reason,
        retrieval_probe_topic=retrieval_probe_topic,
        response_cache_hit=response_cache_hit,
        response_cache_kind=response_cache_kind,
    )


async def _persist_and_finalize_direct_response(
    *,
    settings: Any,
    request: MessageResponseRequest,
    effective_conversation_id: str | None,
    engine_name: str,
    engine_mode: str,
    actor: dict[str, Any] | None,
    preview: Any,
    school_profile: dict[str, Any] | None,
    conversation_context: dict[str, Any] | None,
    public_plan: PublicInstitutionPlan | None,
    langgraph_trace_metadata: dict[str, Any],
    message_text: str,
    suggested_replies: list[MessageResponseSuggestedReply],
    selected_tools: list[str],
    retrieval_backend: RetrievalBackend,
    answer_verifier_valid: bool,
    answer_verifier_reason: str | None,
    deterministic_fallback_available: bool,
    answer_verifier_judge_used: bool,
    citations: list[MessageResponseCitation] | None = None,
    calendar_events: list[CalendarEventCard] | None = None,
    visual_assets: list[MessageResponseVisualAsset] | None = None,
    llm_stages: list[str] | None = None,
) -> MessageResponse:
    citations = citations or []
    calendar_events = calendar_events or []
    visual_assets = visual_assets or []
    llm_stages = llm_stages or []
    await _persist_operational_trace(
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
        visual_asset_count=len(visual_assets),
        answer_verifier_valid=answer_verifier_valid,
        answer_verifier_reason=answer_verifier_reason,
        answer_verifier_fallback_used=False,
        deterministic_fallback_available=deterministic_fallback_available,
        answer_verifier_judge_used=answer_verifier_judge_used,
        langgraph_trace_metadata=langgraph_trace_metadata,
    )
    await _persist_conversation_turn(
        settings=settings,
        conversation_external_id=effective_conversation_id,
        channel=request.channel.value,
        actor=actor,
        user_message=request.message,
        assistant_message=message_text,
    )
    evidence_pack = _build_runtime_evidence_pack(
        request_message=request.message,
        message_text=message_text,
        preview=preview,
        selected_tools=selected_tools,
        citations=citations,
        school_profile=school_profile,
        actor=actor,
        conversation_context=conversation_context,
        public_plan=public_plan,
        retrieval_backend=retrieval_backend,
    )
    return _build_response(
        request=request,
        preview=preview,
        message_text=message_text,
        selected_tools=selected_tools,
        retrieval_backend=retrieval_backend,
        citations=citations,
        calendar_events=calendar_events,
        visual_assets=visual_assets,
        evidence_pack=evidence_pack,
        suggested_replies=suggested_replies,
        llm_stages=llm_stages,
    )


def _build_runtime_request_state(
    *,
    request: MessageResponseRequest,
    actor: dict[str, Any] | None,
    effective_user: UserContext,
    effective_conversation_id: str | None,
    conversation_context: Any,
    context_payload: dict[str, Any] | None,
    analysis_message: str,
    school_profile: dict[str, Any] | None,
    langgraph_artifacts: Any,
    graph: Any,
    langgraph_thread_id: str | None,
) -> RuntimeRequestState:
    return RuntimeRequestState(
        request=request,
        actor=actor,
        effective_user=effective_user,
        effective_conversation_id=effective_conversation_id,
        conversation_context=conversation_context,
        context_payload=context_payload,
        analysis_message=analysis_message,
        school_profile=school_profile,
        langgraph_artifacts=langgraph_artifacts,
        graph=graph,
        langgraph_thread_id=langgraph_thread_id,
    )


async def _load_runtime_request_state(
    *,
    request: MessageResponseRequest,
    settings: Any,
) -> RuntimeRequestState:
    actor = await _fetch_actor_context(settings=settings, telegram_chat_id=request.telegram_chat_id)
    actor = _build_effective_actor_context(actor, request.user)
    effective_user = _merge_user_context(actor, request.user)
    effective_conversation_id = _effective_conversation_id(request)
    conversation_context = await _fetch_conversation_context(
        settings=settings,
        conversation_external_id=effective_conversation_id,
        channel=request.channel.value,
    )
    context_payload = _conversation_context_payload(conversation_context)
    analysis_message = _build_analysis_message(request.message, conversation_context)
    school_profile = await _fetch_public_school_profile(settings=settings)
    langgraph_artifacts = get_langgraph_artifacts(settings)
    graph = langgraph_artifacts.graph
    langgraph_thread_id = resolve_langgraph_thread_id(
        conversation_external_id=effective_conversation_id,
        channel=request.channel.value,
        telegram_chat_id=request.telegram_chat_id,
    )
    return _build_runtime_request_state(
        request=request,
        actor=actor,
        effective_user=effective_user,
        effective_conversation_id=effective_conversation_id,
        conversation_context=conversation_context,
        context_payload=context_payload,
        analysis_message=analysis_message,
        school_profile=school_profile,
        langgraph_artifacts=langgraph_artifacts,
        graph=graph,
        langgraph_thread_id=langgraph_thread_id,
    )


async def _run_preview_stage(
    *,
    settings: Any,
    request: MessageResponseRequest,
    runtime_state: RuntimeRequestState,
) -> tuple[Any, dict[str, Any], MessageResponse | None]:
    analysis_message = runtime_state.analysis_message
    effective_user = runtime_state.effective_user
    graph = runtime_state.graph
    langgraph_thread_id = runtime_state.langgraph_thread_id
    langgraph_artifacts = runtime_state.langgraph_artifacts
    actor = runtime_state.actor
    school_profile = runtime_state.school_profile
    context_payload = runtime_state.context_payload
    effective_conversation_id = runtime_state.effective_conversation_id
    with start_span(
        'eduassist.orchestration.graph_preview', tracer_name='eduassist.ai_orchestrator.runtime'
    ):
        preview_request = request.model_copy(update={'message': analysis_message})
        state = invoke_orchestration_graph(
            graph=graph,
            state_input=_build_preview_state_input(
                request=preview_request,
                user_context=effective_user,
                settings=settings,
            ),
            thread_id=langgraph_thread_id,
        )
        if isinstance(state, dict) and state.get('__interrupt__'):
            snapshot = (
                get_orchestration_state_snapshot(
                    graph=graph,
                    thread_id=langgraph_thread_id,
                    subgraphs=True,
                )
                if langgraph_thread_id
                else None
            )
            snapshot_values = (
                dict(getattr(snapshot, 'values', {}) or {}) if snapshot is not None else {}
            )
            if snapshot_values:
                preview = to_preview(snapshot_values)
            else:
                preview = OrchestrationPreview(
                    mode=OrchestrationMode.structured_tool,
                    classification=IntentClassification(
                        domain=QueryDomain.support,
                        access_tier=AccessTier.authenticated,
                        confidence=0.9,
                        reason='langgraph_hitl_pending_review',
                    ),
                    reason='langgraph_hitl_pending_review',
                )
            preview.reason = 'langgraph_hitl_pending_review'
            preview.risk_flags = list(dict.fromkeys([*preview.risk_flags, 'pending_human_review']))
            langgraph_trace_metadata = _capture_langgraph_trace_metadata(
                graph=graph,
                thread_id=langgraph_thread_id,
                langgraph_artifacts=langgraph_artifacts,
            )
            message_text = _normalize_response_wording(
                _build_langgraph_pending_review_message(preview=preview)
            )
            suggested_replies = _build_suggested_replies(
                request=request,
                preview=preview,
                actor=actor,
                school_profile=school_profile,
                conversation_context=context_payload,
            )
            direct_response = await _persist_and_finalize_direct_response(
                settings=settings,
                request=request,
                effective_conversation_id=effective_conversation_id,
                engine_name='langgraph',
                engine_mode='langgraph',
                actor=actor,
                preview=preview,
                school_profile=school_profile,
                conversation_context=context_payload,
                public_plan=None,
                langgraph_trace_metadata=langgraph_trace_metadata,
                message_text=message_text,
                suggested_replies=suggested_replies,
                selected_tools=list(preview.selected_tools),
                retrieval_backend=preview.retrieval_backend,
                answer_verifier_valid=True,
                answer_verifier_reason='langgraph_hitl_pending_review',
                deterministic_fallback_available=False,
                answer_verifier_judge_used=False,
            )
            return preview, langgraph_trace_metadata, direct_response
        preview = to_preview(state)
    langgraph_trace_metadata = _capture_langgraph_trace_metadata(
        graph=graph,
        thread_id=langgraph_thread_id,
        langgraph_artifacts=langgraph_artifacts,
    )
    return preview, langgraph_trace_metadata, None


def _build_retrieval_service(*, settings: Any) -> Any:
    return get_retrieval_service(
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


async def _finalize_direct_guardrail_response(
    *,
    settings: Any,
    request: MessageResponseRequest,
    engine_name: str,
    engine_mode: str,
    effective_conversation_id: str | None,
    actor: dict[str, Any] | None,
    preview: Any,
    school_profile: dict[str, Any] | None,
    conversation_context: dict[str, Any] | None,
    langgraph_trace_metadata: dict[str, Any],
    message_text: str,
    answer_verifier_valid: bool,
    answer_verifier_reason: str | None,
    deterministic_fallback_available: bool,
    answer_verifier_judge_used: bool,
) -> MessageResponse:
    normalized_text = _normalize_response_wording(message_text)
    suggested_replies = _build_suggested_replies(
        request=request,
        preview=preview,
        actor=actor,
        school_profile=school_profile,
        conversation_context=conversation_context,
    )
    return await _persist_and_finalize_direct_response(
        settings=settings,
        request=request,
        effective_conversation_id=effective_conversation_id,
        engine_name=engine_name,
        engine_mode=engine_mode,
        actor=actor,
        preview=preview,
        school_profile=school_profile,
        conversation_context=conversation_context,
        public_plan=None,
        langgraph_trace_metadata=langgraph_trace_metadata,
        message_text=normalized_text,
        suggested_replies=suggested_replies,
        selected_tools=list(preview.selected_tools),
        retrieval_backend=preview.retrieval_backend,
        answer_verifier_valid=answer_verifier_valid,
        answer_verifier_reason=answer_verifier_reason,
        deterministic_fallback_available=deterministic_fallback_available,
        answer_verifier_judge_used=answer_verifier_judge_used,
    )


async def _run_preflight_stage(
    *,
    settings: Any,
    request: MessageResponseRequest,
    preview: Any,
    actor: dict[str, Any] | None,
    effective_user: UserContext,
    effective_conversation_id: str | None,
    context_payload: dict[str, Any] | None,
    school_profile: dict[str, Any] | None,
    langgraph_trace_metadata: dict[str, Any],
    engine_name: str,
    engine_mode: str,
) -> tuple[MessageResponseFlowState, MessageResponse | None]:
    flow_state = MessageResponseFlowState()

    explicit_teacher_boundary_rescue = (
        preview.classification.access_tier is AccessTier.public
        and preview.mode is OrchestrationMode.clarify
        and (
            _is_public_teacher_identity_query(request.message)
            or _is_public_teacher_directory_follow_up(request.message, context_payload)
        )
    )
    if _is_public_semantic_rescue_candidate(preview) or explicit_teacher_boundary_rescue:
        flow_state.rescued_public_plan = await _resolve_public_institution_plan(
            settings=settings,
            message=request.message,
            preview=preview,
            conversation_context=context_payload,
            school_profile=school_profile,
        )
        if _should_apply_public_semantic_rescue(
            preview=preview, plan=flow_state.rescued_public_plan
        ):
            preview.mode = OrchestrationMode.structured_tool
            preview.reason = (
                'planejamento semantico publico encontrou um ato estruturado mais adequado ao turno'
            )
            preview.selected_tools = list(flow_state.rescued_public_plan.required_tools)
            set_span_attributes(
                **{
                    'eduassist.orchestration.semantic_rescue_applied': True,
                    'eduassist.orchestration.semantic_rescue_act': flow_state.rescued_public_plan.conversation_act,
                    'eduassist.orchestration.semantic_rescue_source': flow_state.rescued_public_plan.semantic_source,
                }
            )
        else:
            set_span_attributes(
                **{
                    'eduassist.orchestration.semantic_rescue_applied': False,
                }
            )

    if _apply_workflow_follow_up_rescue(
        preview=preview,
        message=request.message,
        conversation_context=context_payload,
    ):
        set_span_attributes(
            **{
                'eduassist.orchestration.workflow_follow_up_rescue_applied': True,
                'eduassist.orchestration.workflow_follow_up_rescue_domain': preview.classification.domain.value,
            }
        )
    elif _apply_public_support_rescue(
        preview=preview,
        message=request.message,
        conversation_context=context_payload,
        school_profile=school_profile,
    ):
        set_span_attributes(
            **{
                'eduassist.orchestration.public_support_rescue_applied': True,
                'eduassist.orchestration.public_support_rescue_domain': preview.classification.domain.value,
            }
        )
    elif _apply_authenticated_public_profile_rescue(
        preview=preview,
        actor=actor,
        message=request.message,
        conversation_context=context_payload,
        school_profile=school_profile,
    ):
        set_span_attributes(
            **{
                'eduassist.orchestration.authenticated_public_profile_rescue_applied': True,
                'eduassist.orchestration.authenticated_public_profile_rescue_domain': preview.classification.domain.value,
            }
        )
    elif _apply_teacher_role_rescue(
        preview=preview,
        actor=actor,
        user=effective_user,
        message=request.message,
        conversation_context=context_payload,
    ):
        set_span_attributes(
            **{
                'eduassist.orchestration.teacher_role_rescue_applied': True,
            }
        )
    elif _apply_student_disambiguation_rescue(
        preview=preview,
        actor=actor,
        message=request.message,
        conversation_context=context_payload,
    ):
        set_span_attributes(
            **{
                'eduassist.orchestration.student_disambiguation_rescue_applied': True,
                'eduassist.orchestration.student_disambiguation_rescue_domain': preview.classification.domain.value,
            }
        )
    elif _apply_protected_domain_rescue(
        preview=preview,
        actor=actor,
        message=request.message,
        conversation_context=context_payload,
    ):
        set_span_attributes(
            **{
                'eduassist.orchestration.protected_domain_rescue_applied': True,
                'eduassist.orchestration.protected_domain_rescue_domain': preview.classification.domain.value,
            }
        )

    protected_domain_hint = None
    if effective_user.authenticated:
        protected_domain_hint = _protected_domain_hint_for_message(
            message=request.message,
            actor=actor,
            conversation_context=context_payload,
        )
        if protected_domain_hint in {QueryDomain.academic, QueryDomain.finance}:
            preview = _realign_preview_to_protected_domain(
                preview,
                protected_domain=protected_domain_hint,
            )
            set_span_attributes(
                **{
                    'eduassist.orchestration.protected_focus_override_applied': True,
                    'eduassist.orchestration.protected_focus_override_domain': protected_domain_hint.value,
                }
            )

    if _should_apply_deterministic_scope_boundary(
        message=request.message,
        preview=preview,
        actor=actor,
        conversation_context=context_payload,
        authenticated=bool(effective_user.authenticated),
    ):
        preview.mode = OrchestrationMode.structured_tool
        preview.classification = IntentClassification(
            domain=QueryDomain.institution,
            access_tier=AccessTier.public,
            confidence=0.99,
            reason='deterministic_scope_boundary',
        )
        preview.selected_tools = list(dict.fromkeys([*preview.selected_tools, 'get_public_school_profile']))
        preview.needs_authentication = False
        message_text = _compose_scope_boundary_answer(
            school_profile or {},
            conversation_context=context_payload,
        )
        return flow_state, await _finalize_direct_guardrail_response(
            settings=settings,
            request=request,
            engine_name=engine_name,
            engine_mode=engine_mode,
            effective_conversation_id=effective_conversation_id,
            actor=actor,
            preview=preview,
            school_profile=school_profile,
            conversation_context=context_payload,
            langgraph_trace_metadata=langgraph_trace_metadata,
            message_text=message_text,
            answer_verifier_valid=True,
            answer_verifier_reason='deterministic_scope_boundary',
            deterministic_fallback_available=True,
            answer_verifier_judge_used=False,
        )

    linked_students = _linked_students(actor)
    unmatched_student_reference = (
        _explicit_unmatched_student_reference(
            linked_students,
            request.message,
            conversation_context=context_payload,
        )
        if linked_students
        else None
    )
    foreign_school_reference = (
        None
        if unmatched_student_reference
        else _foreign_school_reference(
            message=request.message,
            school_profile=school_profile,
            conversation_context=context_payload,
        )
    )
    if foreign_school_reference:
        set_span_attributes(
            **{
                'eduassist.orchestration.used_llm': False,
                'eduassist.orchestration.answer_guardrail': 'foreign_school_redirect',
            }
        )
        message_text = _compose_foreign_school_redirect(
            school_profile=school_profile,
            foreign_school_reference=foreign_school_reference,
        )
        verification, semantic_judge_used = await _verify_answer_against_contract_async(
            settings=settings,
            request_message=request.message,
            preview=preview,
            candidate_text=message_text,
            deterministic_fallback_text=message_text,
            public_plan=None,
            slot_memory=_build_conversation_slot_memory(
                actor=actor,
                profile=school_profile,
                conversation_context=context_payload,
                request_message=request.message,
                public_plan=None,
                preview=preview,
            ),
        )
        set_span_attributes(
            **{
                'eduassist.orchestration.answer_verifier_valid': verification.valid,
                'eduassist.orchestration.answer_verifier_reason': verification.reason or '',
                'eduassist.orchestration.answer_verifier_judge_used': semantic_judge_used,
            }
        )
        return flow_state, await _finalize_direct_guardrail_response(
            settings=settings,
            request=request,
            engine_name=engine_name,
            engine_mode=engine_mode,
            effective_conversation_id=effective_conversation_id,
            actor=actor,
            preview=preview,
            school_profile=school_profile,
            conversation_context=context_payload,
            langgraph_trace_metadata=langgraph_trace_metadata,
            message_text=message_text,
            answer_verifier_valid=verification.valid,
            answer_verifier_reason=verification.reason,
            deterministic_fallback_available=True,
            answer_verifier_judge_used=semantic_judge_used,
        )

    flow_state.llm_forced_mode = _llm_forced_mode_enabled(settings=settings, request=request)
    public_known_unknown_answer = None
    if (
        preview.classification.domain is QueryDomain.institution
        and preview.classification.access_tier is AccessTier.public
        and not flow_state.llm_forced_mode
    ):
        public_known_unknown_key = detect_public_known_unknown_key(request.message)
        if public_known_unknown_key:
            public_known_unknown_answer = compose_public_known_unknown_answer(
                key=public_known_unknown_key,
                school_name=_school_name_from_profile(school_profile),
            )
    if public_known_unknown_answer:
        set_span_attributes(
            **{
                'eduassist.orchestration.used_llm': False,
                'eduassist.orchestration.answer_guardrail': 'public_known_unknown_direct',
            }
        )
        return flow_state, await _finalize_direct_guardrail_response(
            settings=settings,
            request=request,
            engine_name=engine_name,
            engine_mode=engine_mode,
            effective_conversation_id=effective_conversation_id,
            actor=actor,
            preview=preview,
            school_profile=school_profile,
            conversation_context=context_payload,
            langgraph_trace_metadata=langgraph_trace_metadata,
            message_text=public_known_unknown_answer,
            answer_verifier_valid=True,
            answer_verifier_reason='deterministic_public_known_unknown',
            deterministic_fallback_available=True,
            answer_verifier_judge_used=False,
        )

    flow_state.public_canonical_lane_request = (
        None if flow_state.llm_forced_mode else match_public_canonical_lane(request.message)
    )
    fast_public_channel_answer = None
    if (
        preview.classification.domain is QueryDomain.institution
        and preview.classification.access_tier is AccessTier.public
        and not flow_state.public_canonical_lane_request
        and not flow_state.llm_forced_mode
        and _base_profile_supports_fast_public_answer(
            message=request.message,
            profile=school_profile,
        )
    ):
        fast_public_channel_answer = _try_public_channel_fast_answer(
            message=request.message,
            profile=school_profile,
        )
    if fast_public_channel_answer:
        set_span_attributes(
            **{
                'eduassist.orchestration.used_llm': False,
                'eduassist.orchestration.answer_guardrail': 'public_fast_path_structured',
            }
        )
        return flow_state, await _finalize_direct_guardrail_response(
            settings=settings,
            request=request,
            engine_name=engine_name,
            engine_mode=engine_mode,
            effective_conversation_id=effective_conversation_id,
            actor=actor,
            preview=preview,
            school_profile=school_profile,
            conversation_context=context_payload,
            langgraph_trace_metadata=langgraph_trace_metadata,
            message_text=fast_public_channel_answer,
            answer_verifier_valid=True,
            answer_verifier_reason='deterministic_public_fast_path',
            deterministic_fallback_available=True,
            answer_verifier_judge_used=False,
        )

    return flow_state, None


async def _run_retrieval_stage(
    *,
    settings: Any,
    request: MessageResponseRequest,
    analysis_message: str,
    preview: Any,
    effective_user: UserContext,
    school_profile: dict[str, Any] | None,
    flow_state: MessageResponseFlowState,
) -> None:
    if preview.mode is OrchestrationMode.hybrid_retrieval:
        with start_span(
            'eduassist.orchestration.public_retrieval',
            tracer_name='eduassist.ai_orchestrator.runtime',
        ):
            retrieval_service = _build_retrieval_service(settings=settings)
            flow_state.restricted_document_query = (
                looks_like_restricted_document_query(request.message)
                and can_read_restricted_documents(effective_user)
            )
            if flow_state.restricted_document_query:
                restricted_policy = resolve_retrieval_execution_policy(
                    query=analysis_message,
                    visibility='restricted',
                    baseline_top_k=5,
                    preview=preview,
                )
                search = retrieval_service.hybrid_search(
                    query=analysis_message,
                    top_k=restricted_policy.top_k,
                    visibility='restricted',
                    category=restricted_policy.category,
                    profile=restricted_policy.profile,
                )
                flow_state.retrieval_hits = select_relevant_restricted_hits(
                    analysis_message, list(search.hits)
                )
                flow_state.citations = _collect_citations(flow_state.retrieval_hits)
                flow_state.retrieval_supported = bool(flow_state.retrieval_hits)
                set_span_attributes(
                    **{
                        'eduassist.retrieval.hit_count': len(flow_state.retrieval_hits),
                        'eduassist.retrieval.citation_count': len(flow_state.citations),
                        'eduassist.retrieval.query_hint_count': 0,
                        'eduassist.retrieval.hints_supported': flow_state.retrieval_supported,
                        'eduassist.retrieval.restricted_document_query': True,
                    }
                )
            else:
                public_retrieval_policy = resolve_retrieval_execution_policy(
                    query=analysis_message,
                    visibility='public',
                    baseline_top_k=4,
                    baseline_category=_category_for_domain(preview.classification.domain),
                    preview=preview,
                )
                search = retrieval_service.hybrid_search(
                    query=analysis_message,
                    top_k=public_retrieval_policy.top_k,
                    visibility='public',
                    category=public_retrieval_policy.category,
                    profile=public_retrieval_policy.profile,
                )
                flow_state.canonical_lane = (
                    (search.query_plan.canonical_lane if search.query_plan is not None else None)
                    or match_public_canonical_lane(request.message)
                    or match_public_canonical_lane(analysis_message)
                )
                flow_state.retrieval_hits = search.hits
                flow_state.query_hints = {
                    *_extract_public_entity_hints(request.message),
                    *_extract_public_entity_hints(analysis_message),
                }
                flow_state.retrieval_supported = _retrieval_hits_cover_query_hints(
                    flow_state.retrieval_hits, flow_state.query_hints
                )
                if flow_state.retrieval_supported:
                    flow_state.retrieval_hits = _filter_retrieval_hits_by_query_hints(
                        flow_state.retrieval_hits, flow_state.query_hints
                    )
                flow_state.citations = _collect_citations(flow_state.retrieval_hits)
                set_span_attributes(
                    **{
                        'eduassist.retrieval.hit_count': len(flow_state.retrieval_hits),
                        'eduassist.retrieval.citation_count': len(flow_state.citations),
                        'eduassist.retrieval.query_hint_count': len(flow_state.query_hints),
                        'eduassist.retrieval.hints_supported': flow_state.retrieval_supported,
                    }
                )
                if not flow_state.retrieval_supported:
                    flow_state.retrieval_hits = []
                    flow_state.citations = []
                flow_state.public_answerability = _assess_public_answerability(
                    analysis_message,
                    flow_state.retrieval_hits,
                    flow_state.query_hints,
                )
                set_span_attributes(
                    **{
                        'eduassist.retrieval.answerability_coverage_ratio': flow_state.public_answerability.coverage_ratio,
                        'eduassist.retrieval.answerability_high_risk': flow_state.public_answerability.high_risk_reasoning,
                        'eduassist.retrieval.answerability_supported_terms': len(flow_state.public_answerability.matched_terms),
                        'eduassist.retrieval.answerability_unsupported_terms': len(flow_state.public_answerability.unsupported_terms),
                    }
                )

                if preview.classification.domain is QueryDomain.calendar:
                    flow_state.calendar_events = await _fetch_public_calendar(settings=settings)
                    set_span_attributes(
                        **{'eduassist.calendar.event_count': len(flow_state.calendar_events)}
                    )
    elif preview.mode is OrchestrationMode.graph_rag:
        with start_span(
            'eduassist.orchestration.graph_rag', tracer_name='eduassist.ai_orchestrator.runtime'
        ):
            set_span_attributes(
                **{
                    'eduassist.graph_rag.workspace_ready': graph_rag_workspace_ready(
                        settings.graph_rag_workspace
                    ),
                }
            )
            flow_state.graph_rag_answer = await run_graph_rag_query(
                settings=settings,
                query=analysis_message,
            )
            if flow_state.graph_rag_answer is not None:
                set_span_attributes(
                    **{
                        'eduassist.graph_rag.method': flow_state.graph_rag_answer.get('method'),
                        'eduassist.graph_rag.response_length': len(
                            flow_state.graph_rag_answer.get('text', '')
                        ),
                    }
                )
            else:
                retrieval_service = _build_retrieval_service(settings=settings)
                graph_rag_fallback_policy = resolve_retrieval_execution_policy(
                    query=analysis_message,
                    visibility='public',
                    baseline_top_k=4,
                    preview=preview,
                )
                search = retrieval_service.hybrid_search(
                    query=analysis_message,
                    top_k=graph_rag_fallback_policy.top_k,
                    visibility='public',
                    category=graph_rag_fallback_policy.category,
                    profile=graph_rag_fallback_policy.profile,
                )
                flow_state.canonical_lane = (
                    search.query_plan.canonical_lane if search.query_plan is not None else None
                )
                flow_state.retrieval_hits = search.hits
                flow_state.citations = _collect_citations(flow_state.retrieval_hits)
                set_span_attributes(
                    **{
                        'eduassist.graph_rag.fallback': True,
                        'eduassist.retrieval.hit_count': len(flow_state.retrieval_hits),
                        'eduassist.retrieval.citation_count': len(flow_state.citations),
                    }
                )




async def _finalize_message_response(
    *,
    settings: Any,
    request: MessageResponseRequest,
    engine_name: str,
    engine_mode: str,
    started_at: float,
    actor: dict[str, Any] | None,
    effective_user: UserContext,
    effective_conversation_id: str | None,
    preview: Any,
    school_profile: dict[str, Any] | None,
    conversation_context: dict[str, Any] | None,
    langgraph_trace_metadata: dict[str, Any],
    message_text: str,
    citations: list[MessageResponseCitation],
    calendar_events: list[CalendarEventCard],
    public_plan: PublicInstitutionPlan | None,
    deterministic_fallback_text: str | None,
    llm_stages: list[str],
    candidate_chosen: str | None,
    candidate_reason: str | None,
    retrieval_probe_topic: str | None,
    response_cache_hit: bool,
    response_cache_kind: str | None,
) -> MessageResponse:
    retrieval_backend = preview.retrieval_backend
    if preview.mode is OrchestrationMode.hybrid_retrieval:
        retrieval_backend = RetrievalBackend.qdrant_hybrid

    if 'answer_composition' not in llm_stages:
        candidate_text = await _maybe_langgraph_open_documentary_candidate(
            settings=settings,
            engine_name=engine_name,
            request=request,
            preview=preview,
            school_profile=school_profile,
            conversation_context=conversation_context,
            draft_text=message_text,
        )
        if candidate_text:
            llm_stages.append('answer_composition')
            message_text = candidate_text

    final_polish_decision = build_final_polish_decision(
        settings=settings,
        stack_name=engine_name,
        request=request,
        preview=preview,
        response_reason=preview.reason,
        llm_stages=llm_stages,
        citations_count=len(citations),
        support_count=0,
        retrieval_backend=retrieval_backend,
    )
    final_polish_applied = False
    final_polish_changed_text = False
    final_polish_preserved_fallback = False

    if final_polish_decision.apply_polish:
        original_structured_text = message_text
        raw_polished_text = await polish_langgraph_with_provider(
            settings=settings,
            request_message=request.message,
            preview=preview,
            draft_text=message_text,
            conversation_context=conversation_context,
            school_profile=school_profile,
        )
        set_span_attributes(
            **{
                'eduassist.orchestration.structured_polish_used': bool(raw_polished_text),
            }
        )
        polished_text = _preserve_capability_anchor_terms(
            original_text=original_structured_text,
            polished_text=raw_polished_text,
            request_message=request.message,
        )
        final_polish_preserved_fallback = bool(
            raw_polished_text
            and polished_text == original_structured_text
            and _normalize_text(raw_polished_text) != _normalize_text(original_structured_text)
        )
        if polished_text:
            llm_stages.append('structured_polish')
            final_polish_applied = True
            final_polish_changed_text = _normalize_text(polished_text) != _normalize_text(
                original_structured_text
            )
            message_text = polished_text

    if final_polish_decision.run_response_critic:
        revised_text = await revise_langgraph_with_provider(
            settings=settings,
            request_message=request.message,
            preview=preview,
            draft_text=message_text,
            conversation_context=conversation_context,
            school_profile=school_profile,
        )
        set_span_attributes(
            **{
                'eduassist.orchestration.response_critic_used': bool(revised_text),
            }
        )
        if revised_text:
            llm_stages.append('response_critic')
            message_text = revised_text

    verifier_slot_memory = _build_conversation_slot_memory(
        actor=actor,
        profile=school_profile,
        conversation_context=conversation_context,
        request_message=request.message,
        public_plan=public_plan,
        preview=preview,
    )
    verification, semantic_judge_used = await verify_langgraph_answer_against_contract(
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
    set_span_attributes(
        **{
            'eduassist.orchestration.answer_verifier_valid': verification.valid,
            'eduassist.orchestration.answer_verifier_reason': verification.reason or '',
            'eduassist.orchestration.answer_verifier_judge_used': semantic_judge_used,
        }
    )
    answer_verifier_fallback_used = False
    if not verification.valid and deterministic_fallback_text:
        message_text = deterministic_fallback_text
        answer_verifier_fallback_used = True

    if citations:
        sources = _render_source_lines(citations)
        if sources and sources not in message_text:
            message_text = f'{message_text}\n\n{sources}'
    message_text = _normalize_response_wording(message_text)

    visual_assets = await _maybe_build_visual_assets(
        settings=settings,
        request=request,
        preview=preview,
        actor=actor,
        school_profile=school_profile,
        conversation_context=conversation_context,
    )
    suggested_replies = _build_suggested_replies(
        request=request,
        preview=preview,
        actor=actor,
        school_profile=school_profile,
        conversation_context=conversation_context,
    )

    await _persist_conversation_turn(
        settings=settings,
        conversation_external_id=effective_conversation_id,
        channel=request.channel.value,
        actor=actor,
        user_message=request.message,
        assistant_message=message_text,
    )
    await _persist_operational_trace(
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
        visual_asset_count=len(visual_assets),
        answer_verifier_valid=verification.valid,
        answer_verifier_reason=verification.reason,
        answer_verifier_fallback_used=answer_verifier_fallback_used,
        deterministic_fallback_available=bool(deterministic_fallback_text),
        answer_verifier_judge_used=semantic_judge_used,
        langgraph_trace_metadata=langgraph_trace_metadata,
    )

    set_span_attributes(
        **{
            'eduassist.response.length': len(message_text),
            'eduassist.response.visual_asset_count': len(visual_assets),
            'eduassist.response.suggested_reply_count': len(suggested_replies),
        }
    )
    metric_attributes = {
        'engine_name': engine_name,
        'engine_mode': engine_mode,
        'mode': preview.mode.value,
        'domain': preview.classification.domain.value,
        'channel': request.channel.value,
        'authenticated': effective_user.authenticated,
        'retrieval_backend': preview.retrieval_backend.value,
    }
    record_counter(
        'eduassist_orchestration_responses',
        attributes=metric_attributes,
        description='Responses emitted by the AI orchestrator.',
    )
    record_histogram(
        'eduassist_orchestration_latency_ms',
        (monotonic() - started_at) * 1000,
        attributes=metric_attributes,
        description='End-to-end orchestration latency in milliseconds.',
    )
    record_histogram(
        'eduassist_orchestration_response_length',
        len(message_text),
        attributes=metric_attributes,
        description='Length of final responses emitted by the AI orchestrator.',
    )
    selected_tools = list(preview.selected_tools)
    if (
        preview.mode is OrchestrationMode.structured_tool
        and preview.classification.domain is QueryDomain.institution
        and preview.classification.access_tier is AccessTier.public
        and 'get_administrative_status' not in preview.selected_tools
        and 'get_student_administrative_status' not in preview.selected_tools
        and 'get_actor_identity_context' not in preview.selected_tools
    ):
        if public_plan is not None:
            selected_tools = list(public_plan.required_tools)
        else:
            selected_tools = _build_public_institution_plan(
                request.message,
                list(preview.selected_tools),
            ).required_tools
        if 'get_public_school_profile' not in selected_tools:
            selected_tools = [*selected_tools, 'get_public_school_profile']
    selected_tools = list(selected_tools)
    evidence_pack = _build_runtime_evidence_pack(
        request_message=request.message,
        message_text=message_text,
        preview=preview,
        selected_tools=selected_tools,
        citations=citations,
        school_profile=school_profile,
        actor=actor,
        conversation_context=conversation_context,
        public_plan=public_plan,
        retrieval_backend=retrieval_backend,
    )
    set_span_attributes(
        **{
            'eduassist.orchestration.candidate_chosen': candidate_chosen or '',
            'eduassist.orchestration.candidate_reason': candidate_reason or '',
            'eduassist.orchestration.retrieval_probe_topic': retrieval_probe_topic or '',
            'eduassist.orchestration.response_cache_hit': response_cache_hit,
            'eduassist.orchestration.response_cache_kind': response_cache_kind or '',
        }
    )
    response = _build_response(
        request=request,
        preview=preview,
        message_text=message_text,
        selected_tools=selected_tools,
        retrieval_backend=retrieval_backend,
        citations=citations,
        calendar_events=calendar_events,
        visual_assets=visual_assets,
        evidence_pack=evidence_pack,
        suggested_replies=suggested_replies,
        llm_stages=llm_stages,
        final_polish_decision=final_polish_decision,
        final_polish_applied=final_polish_applied,
        final_polish_changed_text=final_polish_changed_text,
        final_polish_preserved_fallback=final_polish_preserved_fallback,
        candidate_chosen=candidate_chosen,
        candidate_reason=candidate_reason,
        retrieval_probe_topic=retrieval_probe_topic,
        response_cache_hit=response_cache_hit,
        response_cache_kind=response_cache_kind,
    )
    record_stack_outcome(
        stack_name='langgraph',
        latency_ms=(monotonic() - started_at) * 1000,
        success=True,
        timeout=False,
        cache_hit=response_cache_hit,
        used_llm=bool(llm_stages),
        candidate_kind=candidate_chosen,
    )
    return response




async def generate_message_response(
    *,
    request: MessageResponseRequest,
    settings: Any,
    engine_name: str = 'langgraph',
    engine_mode: str = 'langgraph',
) -> MessageResponse:
    started_at = monotonic()
    with start_span(
        'eduassist.orchestration.message_response',
        tracer_name='eduassist.ai_orchestrator.runtime',
        **{
            'eduassist.channel': request.channel.value,
            'eduassist.request.message_length': len(request.message),
            'eduassist.request.has_telegram_chat': request.telegram_chat_id is not None,
            'eduassist.orchestration.allow_graph_rag': request.allow_graph_rag,
            'eduassist.orchestration.allow_handoff': request.allow_handoff,
            'eduassist.orchestration.engine_name': engine_name,
            'eduassist.orchestration.engine_mode': engine_mode,
        },
    ):
        runtime_state = await _load_runtime_request_state(request=request, settings=settings)
        actor = runtime_state.actor
        effective_user = runtime_state.effective_user
        effective_conversation_id = runtime_state.effective_conversation_id
        conversation_context = runtime_state.conversation_context
        context_payload = runtime_state.context_payload
        analysis_message = runtime_state.analysis_message
        school_profile = runtime_state.school_profile
        langgraph_artifacts = runtime_state.langgraph_artifacts
        langgraph_thread_id = runtime_state.langgraph_thread_id
        set_span_attributes(
            **{
                'eduassist.actor.role': effective_user.role.value,
                'eduassist.actor.authenticated': effective_user.authenticated,
                'eduassist.actor.linked_student_count': len(effective_user.linked_student_ids),
                'eduassist.conversation.has_memory': conversation_context is not None
                and conversation_context.message_count > 0,
                'eduassist.conversation.message_count': conversation_context.message_count
                if conversation_context
                else 0,
                'eduassist.orchestration.analysis_message_expanded': analysis_message
                != request.message,
            }
        )

        preview, langgraph_trace_metadata, direct_response = await _run_preview_stage(
            settings=settings,
            request=request,
            runtime_state=runtime_state,
        )
        if direct_response is not None:
            record_stack_outcome(
                stack_name='langgraph',
                latency_ms=(monotonic() - started_at) * 1000,
                success=True,
                timeout=False,
                cache_hit=False,
                used_llm=False,
                candidate_kind='deterministic',
            )
            return direct_response
        set_span_attributes(
            **{
                'eduassist.orchestration.mode': preview.mode.value,
                'eduassist.orchestration.domain': preview.classification.domain.value,
                'eduassist.orchestration.access_tier': preview.classification.access_tier.value,
                'eduassist.orchestration.needs_authentication': preview.needs_authentication,
                'eduassist.orchestration.selected_tools': preview.selected_tools,
                'eduassist.orchestration.graph_path': preview.graph_path,
                'eduassist.orchestration.retrieval_backend': preview.retrieval_backend.value,
                'eduassist.orchestration.langgraph_thread_id': langgraph_thread_id or '',
                'eduassist.orchestration.langgraph_checkpointer_enabled': langgraph_artifacts.checkpointer_enabled,
                'eduassist.orchestration.langgraph_checkpointer_backend': langgraph_artifacts.checkpointer_backend
                or '',
                'eduassist.orchestration.langgraph_state_available': bool(
                    langgraph_trace_metadata.get('state_available')
                ),
                'eduassist.orchestration.langgraph_state_fetch_error': str(
                    langgraph_trace_metadata.get('state_fetch_error', '') or ''
                ),
                'eduassist.orchestration.langgraph_checkpoint_id': str(
                    langgraph_trace_metadata.get('checkpoint_id', '') or ''
                ),
            }
        )

        flow_state, direct_response = await _run_preflight_stage(
            settings=settings,
            request=request,
            preview=preview,
            actor=actor,
            effective_user=effective_user,
            effective_conversation_id=effective_conversation_id,
            context_payload=context_payload,
            school_profile=school_profile,
            langgraph_trace_metadata=langgraph_trace_metadata,
            engine_name=engine_name,
            engine_mode=engine_mode,
        )
        if direct_response is not None:
            record_stack_outcome(
                stack_name='langgraph',
                latency_ms=(monotonic() - started_at) * 1000,
                success=True,
                timeout=False,
                cache_hit=False,
                used_llm=False,
                candidate_kind='deterministic',
            )
            return direct_response

        await _run_retrieval_stage(
            settings=settings,
            request=request,
            analysis_message=analysis_message,
            preview=preview,
            effective_user=effective_user,
            school_profile=school_profile,
            flow_state=flow_state,
        )

        retrieval_hits = flow_state.retrieval_hits
        citations = flow_state.citations
        calendar_events = flow_state.calendar_events
        query_hints = flow_state.query_hints
        retrieval_supported = flow_state.retrieval_supported
        public_answerability = flow_state.public_answerability
        graph_rag_answer = flow_state.graph_rag_answer
        public_plan = flow_state.public_plan
        deterministic_fallback_text = flow_state.deterministic_fallback_text
        rescued_public_plan = flow_state.rescued_public_plan
        canonical_lane = flow_state.canonical_lane
        restricted_document_query = flow_state.restricted_document_query
        public_canonical_lane_request = flow_state.public_canonical_lane_request

        llm_text: str | None = None
        llm_stages: list[str] = []
        candidate_chosen: str | None = None
        candidate_reason: str | None = None
        retrieval_probe_topic: str | None = None
        response_cache_hit = False
        response_cache_kind: str | None = None

        if preview.mode is OrchestrationMode.structured_tool:
            with start_span(
                'eduassist.orchestration.structured_tool',
                tracer_name='eduassist.ai_orchestrator.runtime',
            ):
                if public_canonical_lane_request:
                    lane_answer = compose_public_canonical_lane_answer(
                        public_canonical_lane_request,
                        profile=school_profile,
                    )
                    if lane_answer:
                        preview = preview.model_copy(
                            update={
                                'reason': f'langgraph_public_canonical_lane:{public_canonical_lane_request}',
                                'selected_tools': list(
                                    dict.fromkeys(
                                        [*preview.selected_tools, 'get_public_school_profile']
                                    )
                                ),
                            }
                        )
                        message_text = lane_answer
                        deterministic_fallback_text = lane_answer
                        candidate_chosen = 'deterministic'
                        candidate_reason = f'public_canonical_lane:{public_canonical_lane_request}'
                        retrieval_probe_topic = None
                        response_cache_hit = False
                        response_cache_kind = None
                    else:
                        public_plan_sink: dict[str, Any] = {}
                        message_text = await _compose_structured_tool_answer(
                            settings=settings,
                            request=request,
                            analysis_message=analysis_message,
                            preview=preview,
                            actor=actor,
                            school_profile=school_profile,
                            conversation_context=context_payload,
                            public_plan_sink=public_plan_sink,
                            resolved_public_plan=rescued_public_plan,
                        )
                        public_plan = public_plan_sink.get('plan')
                        deterministic_fallback_text = str(
                            public_plan_sink.get('deterministic_text') or message_text
                        )
                        candidate_chosen = public_plan_sink.get('candidate_chosen')
                        candidate_reason = public_plan_sink.get('candidate_reason')
                        retrieval_probe_topic = public_plan_sink.get('retrieval_probe_topic')
                        response_cache_hit = bool(public_plan_sink.get('response_cache_hit'))
                        response_cache_kind = public_plan_sink.get('response_cache_kind')
                        llm_stages.extend(list(public_plan_sink.get('agentic_llm_stages', [])))
                else:
                    public_plan_sink: dict[str, Any] = {}
                    message_text = await _compose_structured_tool_answer(
                        settings=settings,
                        request=request,
                        analysis_message=analysis_message,
                        preview=preview,
                        actor=actor,
                        school_profile=school_profile,
                        conversation_context=context_payload,
                        public_plan_sink=public_plan_sink,
                        resolved_public_plan=rescued_public_plan,
                    )
                    public_plan = public_plan_sink.get('plan')
                    deterministic_fallback_text = str(
                        public_plan_sink.get('deterministic_text') or message_text
                    )
                    candidate_chosen = public_plan_sink.get('candidate_chosen')
                    candidate_reason = public_plan_sink.get('candidate_reason')
                    retrieval_probe_topic = public_plan_sink.get('retrieval_probe_topic')
                    response_cache_hit = bool(public_plan_sink.get('response_cache_hit'))
                    response_cache_kind = public_plan_sink.get('response_cache_kind')
                    llm_stages.extend(list(public_plan_sink.get('agentic_llm_stages', [])))
        elif preview.mode is OrchestrationMode.handoff:
            with start_span(
                'eduassist.orchestration.handoff', tracer_name='eduassist.ai_orchestrator.runtime'
            ):
                handoff_payload = await _create_support_handoff(
                    settings=settings,
                    request=request,
                    actor=actor,
                )
                if isinstance(handoff_payload, dict):
                    item = handoff_payload.get('item')
                    if isinstance(item, dict):
                        set_span_attributes(
                            **{
                                'eduassist.queue.name': item.get('queue_name'),
                                'eduassist.support.status': item.get('status'),
                                'eduassist.support.priority': item.get('priority_code'),
                                'eduassist.support.sla_state': item.get('sla_state'),
                            }
                        )
                message_text = _compose_handoff_answer(handoff_payload)
                deterministic_fallback_text = message_text
        elif preview.mode is OrchestrationMode.graph_rag and graph_rag_answer is not None:
            set_span_attributes(
                **{
                    'eduassist.orchestration.used_llm': False,
                    'eduassist.orchestration.graph_rag_live': True,
                }
            )
            message_text = graph_rag_answer['text']
        elif preview.mode is OrchestrationMode.deny:
            set_span_attributes(
                **{
                    'eduassist.orchestration.used_llm': False,
                    'eduassist.orchestration.answer_guardrail': 'deterministic_deny',
                }
            )
            message_text = _compose_deterministic_answer(
                request_message=request.message,
                preview=preview,
                retrieval_hits=retrieval_hits,
                citations=[],
                calendar_events=calendar_events,
                query_hints=query_hints,
            )
            deterministic_fallback_text = message_text
        else:
            with start_span(
                'eduassist.orchestration.answer_composition',
                tracer_name='eduassist.ai_orchestrator.runtime',
            ):
                deterministic_answer_candidate: str | None = None
                if _is_greeting_only(request.message):
                    set_span_attributes(
                        **{
                            'eduassist.orchestration.used_llm': False,
                            'eduassist.orchestration.answer_guardrail': 'institutional_greeting',
                        }
                    )
                    citations = []
                    message_text = _compose_concierge_greeting(
                        school_profile,
                        request.message,
                        context_payload,
                    )
                    deterministic_answer_candidate = message_text
                elif (
                    preview.mode is OrchestrationMode.hybrid_retrieval and restricted_document_query
                ):
                    set_span_attributes(
                        **{
                            'eduassist.orchestration.used_llm': False,
                            'eduassist.orchestration.answer_guardrail': 'restricted_document_search',
                        }
                    )
                    if retrieval_hits:
                        message_text = (
                            compose_restricted_document_grounded_answer_for_query(
                                request.message,
                                retrieval_hits,
                            )
                            or ''
                        )
                        deterministic_answer_candidate = message_text
                        preview = preview.model_copy(
                            update={'reason': 'langgraph_restricted_document_search'}
                        )
                    else:
                        citations = []
                        message_text = compose_restricted_document_no_match_answer(request.message)
                        deterministic_answer_candidate = message_text
                        preview = preview.model_copy(
                            update={'reason': 'langgraph_restricted_document_no_match'}
                        )
                elif preview.mode is OrchestrationMode.hybrid_retrieval and canonical_lane:
                    lane_answer = compose_public_canonical_lane_answer(
                        canonical_lane,
                        profile=school_profile,
                    )
                    if lane_answer:
                        set_span_attributes(
                            **{
                                'eduassist.orchestration.used_llm': False,
                                'eduassist.orchestration.answer_guardrail': 'public_canonical_lane',
                                'eduassist.retrieval.canonical_lane': canonical_lane,
                            }
                        )
                        citations = []
                        message_text = lane_answer
                        deterministic_answer_candidate = message_text
                    else:
                        deterministic_answer_candidate = None
                elif preview.mode is OrchestrationMode.hybrid_retrieval and not retrieval_supported:
                    set_span_attributes(**{'eduassist.orchestration.used_llm': False})
                    citations = []
                    message_text = _compose_public_gap_answer(query_hints, request.message)
                    deterministic_answer_candidate = message_text
                elif (
                    preview.mode is OrchestrationMode.hybrid_retrieval
                    and _is_negative_requirement_query(request.message)
                ):
                    set_span_attributes(
                        **{
                            'eduassist.orchestration.used_llm': False,
                            'eduassist.orchestration.answer_guardrail': 'negative_requirement_abstention',
                        }
                    )
                    message_text = _compose_negative_requirement_answer()
                    deterministic_answer_candidate = message_text
                elif preview.mode is OrchestrationMode.hybrid_retrieval and _is_comparative_query(
                    request.message
                ):
                    set_span_attributes(
                        **{
                            'eduassist.orchestration.used_llm': False,
                            'eduassist.orchestration.answer_guardrail': 'comparative_abstention',
                        }
                    )
                    citations = []
                    message_text = _compose_comparative_gap_answer(school_profile)
                    deterministic_answer_candidate = message_text
                elif (
                    preview.mode is OrchestrationMode.hybrid_retrieval
                    and public_answerability is not None
                    and not public_answerability.enough_support
                ):
                    set_span_attributes(
                        **{
                            'eduassist.orchestration.used_llm': False,
                            'eduassist.orchestration.answer_guardrail': 'answerability_abstention',
                        }
                    )
                    if not public_answerability.high_risk_reasoning:
                        citations = []
                    message_text = _compose_answerability_gap_answer(
                        public_answerability, request.message
                    )
                    deterministic_answer_candidate = message_text
                elif preview.mode is OrchestrationMode.clarify and _is_prompt_disclosure_probe(
                    request.message
                ):
                    set_span_attributes(
                        **{
                            'eduassist.orchestration.used_llm': False,
                            'eduassist.orchestration.safe_clarify_guardrail': True,
                        }
                    )
                    message_text = (
                        f'{DEFAULT_PUBLIC_HELP} '
                        'Nao posso ajudar com detalhes internos de configuracao do sistema.'
                    )
                    deterministic_answer_candidate = message_text
                elif preview.mode is OrchestrationMode.clarify:
                    fast_public_channel_answer = None
                    if _base_profile_supports_fast_public_answer(
                        message=request.message,
                        profile=school_profile,
                    ):
                        fast_public_channel_answer = _try_public_channel_fast_answer(
                            message=request.message,
                            profile=school_profile,
                        )
                    if fast_public_channel_answer:
                        set_span_attributes(
                            **{
                                'eduassist.orchestration.used_llm': False,
                                'eduassist.orchestration.answer_guardrail': 'public_fast_path_clarify',
                            }
                        )
                        message_text = fast_public_channel_answer
                        deterministic_answer_candidate = fast_public_channel_answer
                    else:
                        clarify_slot_memory = _build_conversation_slot_memory(
                            actor=actor,
                            profile=school_profile,
                            conversation_context=context_payload,
                            request_message=request.message,
                            public_plan=public_plan,
                            preview=preview,
                        )
                        contextual_clarify = _compose_contextual_clarify_answer(
                            request_message=request.message,
                            actor=actor,
                            conversation_context=context_payload,
                            slot_memory=clarify_slot_memory,
                        )
                        if contextual_clarify:
                            set_span_attributes(
                                **{
                                    'eduassist.orchestration.used_llm': False,
                                    'eduassist.orchestration.answer_guardrail': 'contextual_clarify',
                                }
                            )
                            message_text = contextual_clarify
                            deterministic_answer_candidate = contextual_clarify
                        else:
                            deterministic_answer_candidate = _compose_deterministic_answer(
                                request_message=request.message,
                                preview=preview,
                                retrieval_hits=retrieval_hits,
                                citations=citations,
                                calendar_events=calendar_events,
                                query_hints=query_hints,
                            )
                            llm_text = await compose_langgraph_with_provider(
                                settings=settings,
                                request_message=request.message,
                                analysis_message=analysis_message,
                                preview=preview,
                                citations=citations,
                                calendar_events=calendar_events,
                                conversation_context=context_payload,
                                school_profile=school_profile,
                            )
                            if llm_text:
                                llm_stages.append('answer_composition')
                            set_span_attributes(
                                **{
                                    'eduassist.orchestration.used_llm': bool(llm_text),
                                    'eduassist.orchestration.llm_provider': settings.llm_provider,
                                }
                            )
                            message_text = llm_text or deterministic_answer_candidate
                else:
                    deterministic_answer_candidate = _compose_deterministic_answer(
                        request_message=request.message,
                        preview=preview,
                        retrieval_hits=retrieval_hits,
                        citations=citations,
                        calendar_events=calendar_events,
                        query_hints=query_hints,
                    )
                    llm_text = await compose_langgraph_with_provider(
                        settings=settings,
                        request_message=request.message,
                        analysis_message=analysis_message,
                        preview=preview,
                        citations=citations,
                        calendar_events=calendar_events,
                        conversation_context=context_payload,
                        school_profile=school_profile,
                    )
                    if llm_text:
                        llm_stages.append('answer_composition')
                    set_span_attributes(
                        **{
                            'eduassist.orchestration.used_llm': bool(llm_text),
                            'eduassist.orchestration.llm_provider': settings.llm_provider,
                        }
                    )
                    message_text = llm_text or deterministic_answer_candidate
                deterministic_fallback_text = deterministic_answer_candidate

        return await _finalize_message_response(
            settings=settings,
            request=request,
            engine_name=engine_name,
            engine_mode=engine_mode,
            started_at=started_at,
            actor=actor,
            effective_user=effective_user,
            effective_conversation_id=effective_conversation_id,
            preview=preview,
            school_profile=school_profile,
            conversation_context=context_payload,
            langgraph_trace_metadata=langgraph_trace_metadata,
            message_text=message_text,
            citations=citations,
            calendar_events=calendar_events,
            public_plan=public_plan,
            deterministic_fallback_text=deterministic_fallback_text,
            llm_stages=llm_stages,
            candidate_chosen=candidate_chosen,
            candidate_reason=candidate_reason,
            retrieval_probe_topic=retrieval_probe_topic,
            response_cache_hit=response_cache_hit,
            response_cache_kind=response_cache_kind,
        )
