from __future__ import annotations

from typing import Any, TypedDict

from langgraph.graph import END, START, StateGraph

from . import runtime as rt
from .langgraph_local_llm import (
    compose_langgraph_with_provider,
    polish_langgraph_with_provider,
    revise_langgraph_with_provider,
    verify_langgraph_answer_against_contract,
)
from .langgraph_runtime import (
    get_langgraph_artifacts,
    invoke_orchestration_graph,
    resolve_langgraph_thread_id,
)
from .models import MessageResponse, OrchestrationMode, QueryDomain, RetrievalBackend, RetrievalProfile
from .public_known_unknowns import compose_public_known_unknown_answer, detect_public_known_unknown_key
from .retrieval import (
    can_read_restricted_documents,
    compose_restricted_document_grounded_answer_for_query,
    compose_restricted_document_no_match_answer,
    get_retrieval_service,
    looks_like_restricted_document_query,
    select_relevant_restricted_hits,
)
from .semantic_ingress_runtime import (
    apply_semantic_ingress_preview,
    apply_turn_frame_preview,
    build_semantic_ingress_public_plan,
    build_turn_frame_public_plan,
    is_terminal_semantic_ingress_plan,
    maybe_resolve_semantic_ingress_plan,
    maybe_resolve_turn_frame,
)


class LangGraphMessageState(TypedDict, total=False):
    request: Any
    settings: Any
    engine_name: str
    engine_mode: str
    actor: dict[str, Any] | None
    effective_user: Any
    effective_conversation_id: str | None
    conversation_context_bundle: Any
    conversation_context: dict[str, Any] | None
    analysis_message: str
    school_profile: dict[str, Any] | None
    preview: Any
    semantic_ingress_plan: Any
    turn_frame: Any
    turn_frame_public_plan: Any
    langgraph_thread_id: str | None
    langgraph_trace_metadata: dict[str, Any] | None
    route: str
    response: MessageResponse | None


def _deterministic_retrieval_fallback(*, citations: list[Any], context_pack: str | None) -> str:
    if context_pack:
        return rt._normalize_response_wording(context_pack)
    if citations:
        lines = [citation.excerpt for citation in citations[:3] if str(citation.excerpt or '').strip()]
        if lines:
            return rt._normalize_response_wording('\n'.join(lines))
    return 'Nao encontrei evidencias publicas suficientes para responder com seguranca.'


def _route_native_path(preview: Any, request_message: str, analysis_message: str | None = None) -> str:
    analysis_message = analysis_message or request_message
    if analysis_message.strip() != str(request_message).strip():
        if rt.match_public_canonical_lane(request_message) or rt.match_public_canonical_lane(analysis_message):
            return 'public_compound'
        if rt._is_public_timeline_query(analysis_message):
            return 'public_compound'
    if (
        preview.classification.access_tier.value == 'public'
        and rt._has_public_multi_intent_signal(request_message)
        and not rt._looks_like_public_documentary_open_query(request_message)
        and any(
            matcher(request_message)
            for matcher in (
                rt._is_service_routing_query,
                rt._matches_public_contact_rule,
                rt._is_public_pricing_navigation_query,
                rt._is_public_timeline_query,
                rt._is_public_calendar_event_query,
                rt._is_public_curriculum_query,
            )
        )
    ):
        return 'public_compound'
    if preview.mode is not OrchestrationMode.hybrid_retrieval:
        return 'delegate_runtime'
    if preview.classification.access_tier.value == 'public':
        return 'public_retrieval'
    if looks_like_restricted_document_query(request_message):
        return 'restricted_retrieval'
    return 'delegate_runtime'


async def _public_compound(state: LangGraphMessageState) -> LangGraphMessageState:
    from .langgraph_public_compound_runtime import _public_compound as _impl

    return await _impl(state)


async def _bootstrap_context(state: LangGraphMessageState) -> LangGraphMessageState:
    request = state['request']
    settings = state['settings']
    actor = await rt._fetch_actor_context(settings=settings, telegram_chat_id=request.telegram_chat_id)
    effective_user = rt._merge_user_context(actor, request.user)
    effective_conversation_id = rt._effective_conversation_id(request)
    conversation_context_bundle = await rt._fetch_conversation_context(
        settings=settings,
        conversation_external_id=effective_conversation_id,
        channel=request.channel.value,
    )
    conversation_context = rt._conversation_context_payload(conversation_context_bundle)
    analysis_message = rt._build_analysis_message(request.message, conversation_context_bundle)
    school_profile = await rt._fetch_public_school_profile(settings=settings)
    langgraph_artifacts = get_langgraph_artifacts(settings)
    langgraph_thread_id = resolve_langgraph_thread_id(
        conversation_external_id=effective_conversation_id,
        channel=request.channel.value,
        telegram_chat_id=request.telegram_chat_id,
    )
    preview_request = request.model_copy(update={'message': analysis_message})
    graph_state = invoke_orchestration_graph(
        graph=langgraph_artifacts.graph,
        state_input=rt._build_preview_state_input(
            request=preview_request,
            user_context=effective_user,
            settings=settings,
        ),
        thread_id=langgraph_thread_id,
    )
    preview = rt.to_preview(graph_state)
    semantic_preview = preview.model_copy(deep=True)
    semantic_ingress_plan = await maybe_resolve_semantic_ingress_plan(
        settings=settings,
        request_message=request.message,
        conversation_context=conversation_context,
        preview=semantic_preview,
        stack_label='langgraph',
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
    route = _route_native_path(preview, request.message, analysis_message)
    if semantic_ingress_plan is not None:
        ingress_base_preview = semantic_preview if is_terminal_semantic_ingress_plan(semantic_ingress_plan) else preview
        preview = apply_semantic_ingress_preview(
            preview=ingress_base_preview,
            plan=semantic_ingress_plan,
            stack_name='langgraph',
        )
        route = 'semantic_ingress'
    turn_frame = None
    turn_frame_public_plan = None
    if semantic_ingress_plan is None or not is_terminal_semantic_ingress_plan(semantic_ingress_plan):
        turn_frame = await maybe_resolve_turn_frame(
            settings=settings,
            request_message=request.message,
            conversation_context=conversation_context,
            preview=preview,
            stack_label='langgraph',
            authenticated=bool(request.user.authenticated),
        )
        if turn_frame is not None:
            preview = apply_turn_frame_preview(
                preview=preview,
                turn_frame=turn_frame,
                stack_name='langgraph',
            )
            turn_frame_public_plan = build_turn_frame_public_plan(turn_frame)
            if route != 'semantic_ingress' and turn_frame.scope == 'public':
                route = 'semantic_ingress'
    langgraph_trace_metadata = rt._capture_langgraph_trace_metadata(
        graph=langgraph_artifacts.graph,
        thread_id=langgraph_thread_id,
        langgraph_artifacts=langgraph_artifacts,
    )
    return {
        'actor': actor,
        'effective_user': effective_user,
        'effective_conversation_id': effective_conversation_id,
        'conversation_context_bundle': conversation_context_bundle,
        'conversation_context': conversation_context,
        'analysis_message': analysis_message,
        'school_profile': school_profile,
        'preview': preview,
        'semantic_ingress_plan': semantic_ingress_plan,
        'turn_frame': turn_frame,
        'turn_frame_public_plan': turn_frame_public_plan,
        'langgraph_thread_id': langgraph_thread_id,
        'langgraph_trace_metadata': langgraph_trace_metadata,
        'route': route,
    }


def _after_bootstrap(state: LangGraphMessageState) -> str:
    return str(state.get('route') or 'delegate_runtime')


async def _delegate_runtime(state: LangGraphMessageState) -> LangGraphMessageState:
    response = await rt.generate_message_response(
        request=state['request'],
        settings=state['settings'],
        engine_name=state['engine_name'],
        engine_mode=state['engine_mode'],
    )
    return {'response': response}


async def _semantic_ingress(state: LangGraphMessageState) -> LangGraphMessageState:
    request = state['request']
    settings = state['settings']
    preview = state['preview']
    actor = state['actor']
    conversation_context = state['conversation_context']
    school_profile = state['school_profile']
    effective_conversation_id = state['effective_conversation_id']
    semantic_ingress_plan = state.get('semantic_ingress_plan')
    turn_frame_public_plan = state.get('turn_frame_public_plan')
    if semantic_ingress_plan is None and turn_frame_public_plan is None:
        return await _delegate_runtime(state)

    public_plan = build_semantic_ingress_public_plan(semantic_ingress_plan) if semantic_ingress_plan is not None else None
    public_plan = public_plan or turn_frame_public_plan
    public_plan_sink: dict[str, Any] = {}
    if semantic_ingress_plan is not None and is_terminal_semantic_ingress_plan(semantic_ingress_plan):
        message_text = rt._compose_public_profile_answer(
            school_profile or {},
            request.message,
            actor=actor,
            original_message=request.message,
            conversation_context=conversation_context,
            semantic_plan=public_plan,
        )
    else:
        message_text = await rt._compose_structured_tool_answer(
            settings=settings,
            request=request,
            analysis_message=request.message,
            preview=preview,
            actor=actor,
            school_profile=school_profile,
            conversation_context=conversation_context,
            public_plan_sink=public_plan_sink,
            resolved_public_plan=public_plan,
            prefer_fast_public_path=False,
        )
    llm_stages = ['semantic_ingress_classifier'] if semantic_ingress_plan is not None else ['turn_frame_classifier']
    if semantic_ingress_plan is None or semantic_ingress_plan.conversation_act != 'language_preference':
        polished_text = await polish_langgraph_with_provider(
            settings=settings,
            request_message=request.message,
            preview=preview,
            draft_text=message_text,
            conversation_context=conversation_context,
            school_profile=school_profile,
        )
        if polished_text:
            message_text = polished_text
            llm_stages.append('structured_polish')
    effective_public_plan = public_plan_sink.get('plan') or public_plan
    suggested_replies = rt._build_suggested_replies(
        request=request,
        preview=preview,
        actor=actor,
        school_profile=school_profile,
        conversation_context=conversation_context,
    )
    evidence_pack = rt._build_runtime_evidence_pack(
        request_message=request.message,
        message_text=message_text,
        preview=preview,
        selected_tools=list(preview.selected_tools),
        citations=[],
        school_profile=school_profile,
        actor=actor,
        conversation_context=conversation_context,
        public_plan=effective_public_plan,
        retrieval_backend=RetrievalBackend.none,
    )
    await rt._persist_operational_trace(
        settings=settings,
        conversation_external_id=effective_conversation_id,
        channel=request.channel.value,
        engine_name=state['engine_name'],
        engine_mode=state['engine_mode'],
        actor=actor,
        preview=preview,
        school_profile=school_profile,
        conversation_context=conversation_context,
        public_plan=effective_public_plan,
        request_message=request.message,
        message_text=message_text,
        citations_count=0,
        suggested_reply_count=len(suggested_replies),
        visual_asset_count=0,
        answer_verifier_valid=True,
        answer_verifier_reason=f'langgraph_semantic_ingress:{semantic_ingress_plan.conversation_act}',
        answer_verifier_fallback_used=False,
        deterministic_fallback_available=True,
        answer_verifier_judge_used=False,
        langgraph_trace_metadata=state.get('langgraph_trace_metadata'),
    )
    await rt._persist_conversation_turn(
        settings=settings,
        conversation_external_id=effective_conversation_id,
        channel=request.channel.value,
        actor=actor,
        user_message=request.message,
        assistant_message=message_text,
    )
    response = MessageResponse(
        message_text=message_text,
        mode=preview.mode,
        classification=preview.classification,
        retrieval_backend=RetrievalBackend.none,
        selected_tools=list(preview.selected_tools),
        citations=[],
        suggested_replies=suggested_replies,
        evidence_pack=evidence_pack,
        needs_authentication=False,
        graph_path=[*list(preview.graph_path), 'langgraph_response_workflow', 'semantic_ingress'],
        risk_flags=rt._build_runtime_risk_flags(
            request_message=request.message,
            message_text=message_text,
            preview=preview,
        ),
        reason=f'langgraph_semantic_ingress:{semantic_ingress_plan.conversation_act}',
        used_llm=True,
        llm_stages=llm_stages,
    )
    return {'response': response}


async def _public_retrieval(state: LangGraphMessageState) -> LangGraphMessageState:
    from .langgraph_public_retrieval_runtime import _public_retrieval as _impl

    return await _impl(state)


async def _restricted_retrieval(state: LangGraphMessageState) -> LangGraphMessageState:
    request = state['request']
    settings = state['settings']
    preview = state['preview']
    actor = state['actor']
    effective_user = state['effective_user']
    conversation_context = state['conversation_context']
    school_profile = state['school_profile']
    effective_conversation_id = state['effective_conversation_id']
    if not can_read_restricted_documents(effective_user):
        return await _delegate_runtime(state)

    retrieval_service = get_retrieval_service(
        database_url=str(settings.database_url),
        qdrant_url=str(settings.qdrant_url),
        collection_name=str(settings.qdrant_documents_collection),
        embedding_model=str(settings.document_embedding_model),
        enable_query_variants=bool(settings.retrieval_enable_query_variants),
        enable_late_interaction_rerank=bool(settings.retrieval_enable_late_interaction_rerank),
        late_interaction_model=str(settings.retrieval_late_interaction_model),
        candidate_pool_size=int(settings.retrieval_candidate_pool_size),
        cheap_candidate_pool_size=int(settings.retrieval_cheap_candidate_pool_size),
        deep_candidate_pool_size=int(settings.retrieval_deep_candidate_pool_size),
        rerank_fused_weight=float(settings.retrieval_rerank_fused_weight),
        rerank_late_interaction_weight=float(settings.retrieval_rerank_late_interaction_weight),
    )
    search = retrieval_service.hybrid_search(
        query=request.message,
        top_k=3,
        visibility='restricted',
        profile=RetrievalProfile.deep,
    )
    relevant_hits = select_relevant_restricted_hits(request.message, list(search.hits))
    citations = rt._collect_citations(relevant_hits[:3], limit=3)
    restricted_reason = 'langgraph_restricted_doc_grounded' if relevant_hits else 'langgraph_restricted_doc_no_match'
    message_text = rt._normalize_response_wording(
        (
            compose_restricted_document_grounded_answer_for_query(request.message, relevant_hits[:3])
            if relevant_hits
            else compose_restricted_document_no_match_answer(request.message)
        )
    )
    suggested_replies = rt._build_suggested_replies(
        request=request,
        preview=preview,
        actor=actor,
        school_profile=school_profile,
        conversation_context=conversation_context,
    )
    evidence_pack = rt._build_runtime_evidence_pack(
        request_message=request.message,
        message_text=message_text,
        preview=preview,
        selected_tools=list(preview.selected_tools),
        citations=citations,
        school_profile=school_profile,
        actor=actor,
        conversation_context=conversation_context,
        public_plan=None,
        retrieval_backend=RetrievalBackend.qdrant_hybrid,
    )
    await rt._persist_operational_trace(
        settings=settings,
        conversation_external_id=effective_conversation_id,
        channel=request.channel.value,
        engine_name=state['engine_name'],
        engine_mode=state['engine_mode'],
        actor=actor,
        preview=preview,
        school_profile=school_profile,
        conversation_context=conversation_context,
        public_plan=None,
        request_message=request.message,
        message_text=message_text,
        citations_count=len(citations),
        suggested_reply_count=len(suggested_replies),
        visual_asset_count=0,
        answer_verifier_valid=True,
        answer_verifier_reason=restricted_reason,
        answer_verifier_fallback_used=False,
        deterministic_fallback_available=True,
        answer_verifier_judge_used=False,
        langgraph_trace_metadata=state.get('langgraph_trace_metadata'),
    )
    await rt._persist_conversation_turn(
        settings=settings,
        conversation_external_id=effective_conversation_id,
        channel=request.channel.value,
        actor=actor,
        user_message=request.message,
        assistant_message=message_text,
    )
    response = MessageResponse(
        message_text=message_text,
        mode=preview.mode,
        classification=preview.classification,
        retrieval_backend=RetrievalBackend.qdrant_hybrid,
        selected_tools=list(preview.selected_tools),
        citations=citations,
        suggested_replies=suggested_replies,
        evidence_pack=evidence_pack,
        needs_authentication=True,
        graph_path=[*list(preview.graph_path), 'langgraph_response_workflow', 'restricted_retrieval'],
        risk_flags=rt._build_runtime_risk_flags(
            request_message=request.message,
            message_text=message_text,
            preview=preview,
        ),
        reason=restricted_reason,
        used_llm=False,
        llm_stages=[],
        retrieval_retry_applied=bool(getattr(search.query_plan, 'corrective_retry_applied', False)),
        retrieval_retry_reason='subquery_coverage_retry' if getattr(search.query_plan, 'corrective_retry_applied', False) else None,
    )
    return {'response': response}


def _build_langgraph_message_workflow() -> Any:
    workflow = StateGraph(LangGraphMessageState)
    workflow.add_node('bootstrap_context', _bootstrap_context)
    workflow.add_node('semantic_ingress', _semantic_ingress)
    workflow.add_node('public_compound', _public_compound)
    workflow.add_node('public_retrieval', _public_retrieval)
    workflow.add_node('restricted_retrieval', _restricted_retrieval)
    workflow.add_node('delegate_runtime', _delegate_runtime)
    workflow.add_edge(START, 'bootstrap_context')
    workflow.add_conditional_edges(
        'bootstrap_context',
        _after_bootstrap,
        {
            'semantic_ingress': 'semantic_ingress',
            'public_compound': 'public_compound',
            'public_retrieval': 'public_retrieval',
            'restricted_retrieval': 'restricted_retrieval',
            'delegate_runtime': 'delegate_runtime',
        },
    )
    workflow.add_edge('semantic_ingress', END)
    workflow.add_edge('public_compound', END)
    workflow.add_edge('public_retrieval', END)
    workflow.add_edge('restricted_retrieval', END)
    workflow.add_edge('delegate_runtime', END)
    return workflow.compile()


_LANGGRAPH_MESSAGE_WORKFLOW = _build_langgraph_message_workflow()


async def run_langgraph_message_workflow(
    *,
    request: Any,
    settings: Any,
    engine_name: str,
    engine_mode: str,
) -> MessageResponse:
    result = await _LANGGRAPH_MESSAGE_WORKFLOW.ainvoke(
        {
            'request': request,
            'settings': settings,
            'engine_name': engine_name,
            'engine_mode': engine_mode,
        }
    )
    response = result.get('response') if isinstance(result, dict) else None
    if isinstance(response, MessageResponse):
        return response
    raise RuntimeError('langgraph_message_workflow_missing_response')
