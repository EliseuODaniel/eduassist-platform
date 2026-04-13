from __future__ import annotations

# ruff: noqa: F401,F403,F405

LOCAL_EXTRACTED_NAMES = {'_public_retrieval'}

from . import langgraph_message_workflow as _native
from .retrieval_capability_policy import (
    build_retrieval_trace_metadata,
    resolve_retrieval_execution_policy,
)


def _refresh_native_namespace() -> None:
    for name, value in vars(_native).items():
        if name.startswith('__') or name in LOCAL_EXTRACTED_NAMES:
            continue
        globals()[name] = value


async def _public_retrieval(state: LangGraphMessageState) -> LangGraphMessageState:
    _refresh_native_namespace()
    request = state['request']
    settings = state['settings']
    preview = state['preview']
    actor = state['actor']
    conversation_context = state['conversation_context']
    school_profile = state['school_profile']
    analysis_message = state['analysis_message']
    effective_conversation_id = state['effective_conversation_id']

    if rt._is_meta_repair_context_query(request.message):
        meta_repair_answer = rt._compose_meta_repair_follow_up_answer(conversation_context)
        if meta_repair_answer:
            message_text = rt._normalize_response_wording(meta_repair_answer)
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
                public_plan=None,
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
                public_plan=None,
                request_message=request.message,
                message_text=message_text,
                citations_count=0,
                suggested_reply_count=len(suggested_replies),
                visual_asset_count=0,
                answer_verifier_valid=True,
                answer_verifier_reason='langgraph_public_retrieval_meta_repair',
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
                mode=OrchestrationMode.structured_tool,
                classification=preview.classification,
                retrieval_backend=RetrievalBackend.none,
                selected_tools=list(preview.selected_tools),
                citations=[],
                suggested_replies=suggested_replies,
                evidence_pack=evidence_pack,
                needs_authentication=False,
                graph_path=[*list(preview.graph_path), 'langgraph_response_workflow', 'public_retrieval_meta_repair'],
                risk_flags=rt._build_runtime_risk_flags(
                    request_message=request.message,
                    message_text=message_text,
                    preview=preview,
                ),
                reason='langgraph_public_retrieval_meta_repair',
                used_llm=False,
                llm_stages=[],
            )
            return {'response': response}

    public_boundary_answer = rt._compose_contextual_public_boundary_answer(
        message=request.message,
        conversation_context=conversation_context,
        profile=school_profile,
    )
    if public_boundary_answer:
        message_text = rt._normalize_response_wording(public_boundary_answer)
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
            public_plan=None,
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
            public_plan=None,
            request_message=request.message,
            message_text=message_text,
            citations_count=0,
            suggested_reply_count=len(suggested_replies),
            visual_asset_count=0,
            answer_verifier_valid=True,
            answer_verifier_reason='langgraph_public_retrieval_public_boundary',
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
            mode=OrchestrationMode.structured_tool,
            classification=preview.classification,
            retrieval_backend=RetrievalBackend.none,
            selected_tools=list(dict.fromkeys([*preview.selected_tools, 'get_public_school_profile'])),
            citations=[],
            suggested_replies=suggested_replies,
            evidence_pack=evidence_pack,
            needs_authentication=False,
            graph_path=[*list(preview.graph_path), 'langgraph_response_workflow', 'public_retrieval_public_boundary'],
            risk_flags=rt._build_runtime_risk_flags(
                request_message=request.message,
                message_text=message_text,
                preview=preview,
            ),
            reason='langgraph_public_retrieval_public_boundary',
            used_llm=False,
            llm_stages=[],
        )
        return {'response': response}

    known_unknown_key = detect_public_known_unknown_key(analysis_message) or detect_public_known_unknown_key(request.message)
    if known_unknown_key:
        message_text = compose_public_known_unknown_answer(
            key=known_unknown_key,
            school_name=str((school_profile or {}).get('school_name', 'Colegio Horizonte')),
        )
        if message_text:
            message_text = rt._normalize_response_wording(message_text)
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
                public_plan=None,
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
                public_plan=None,
                request_message=request.message,
                message_text=message_text,
                citations_count=0,
                suggested_reply_count=len(suggested_replies),
                visual_asset_count=0,
                answer_verifier_valid=True,
                answer_verifier_reason='langgraph_public_retrieval_known_unknown',
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
                mode=OrchestrationMode.structured_tool,
                classification=preview.classification,
                retrieval_backend=RetrievalBackend.none,
                selected_tools=list(dict.fromkeys([*preview.selected_tools, 'get_public_school_profile'])),
                citations=[],
                suggested_replies=suggested_replies,
                evidence_pack=evidence_pack,
                needs_authentication=False,
                graph_path=[*list(preview.graph_path), 'langgraph_response_workflow', 'public_retrieval_known_unknown'],
                risk_flags=rt._build_runtime_risk_flags(
                    request_message=request.message,
                    message_text=message_text,
                    preview=preview,
                ),
                reason='langgraph_public_retrieval_known_unknown',
                used_llm=False,
                llm_stages=[],
            )
            return {'response': response}

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
    retrieval_policy = resolve_retrieval_execution_policy(
        query=analysis_message,
        visibility='public',
        baseline_top_k=4,
        baseline_category=rt._category_for_domain(preview.classification.domain),
        preview=preview,
        turn_frame=state.get('turn_frame'),
        public_plan=state.get('turn_frame_public_plan'),
    )
    search = retrieval_service.hybrid_search(
        query=analysis_message,
        top_k=retrieval_policy.top_k,
        visibility='public',
        category=retrieval_policy.category,
        profile=retrieval_policy.profile,
    )
    citations = rt._collect_citations(search.hits, limit=3)
    deterministic_fallback_text = _deterministic_retrieval_fallback(
        citations=citations,
        context_pack=search.context_pack,
    )
    draft_text = await compose_langgraph_with_provider(
        settings=settings,
        request_message=request.message,
        analysis_message=analysis_message,
        preview=preview,
        citations=citations,
        calendar_events=[],
        conversation_context=conversation_context,
        school_profile=school_profile,
        context_pack=search.context_pack,
    )
    message_text = draft_text or deterministic_fallback_text
    llm_stages: list[str] = ['answer_composition'] if draft_text else []

    revised = await revise_langgraph_with_provider(
        settings=settings,
        request_message=request.message,
        preview=preview,
        draft_text=message_text,
        conversation_context=conversation_context,
        school_profile=school_profile,
    )
    if revised:
        message_text = revised
        llm_stages.append('answer_revision')

    polished = await polish_langgraph_with_provider(
        settings=settings,
        request_message=request.message,
        preview=preview,
        draft_text=message_text,
        conversation_context=conversation_context,
        school_profile=school_profile,
    )
    if polished:
        message_text = polished
        llm_stages.append('answer_polish')

    verification, semantic_judge_used = await verify_langgraph_answer_against_contract(
        settings=settings,
        request_message=request.message,
        preview=preview,
        candidate_text=message_text,
        deterministic_fallback_text=deterministic_fallback_text,
        public_plan=None,
        slot_memory=rt._build_conversation_slot_memory(
            actor=actor,
            profile=school_profile,
            conversation_context=conversation_context,
            request_message=request.message,
            public_plan=None,
            preview=preview,
        ),
    )
    if not verification.valid:
        message_text = deterministic_fallback_text
        llm_stages = []
    retrieval_trace_metadata = build_retrieval_trace_metadata(
        visibility='public',
        policy=retrieval_policy,
        search=search,
        selected_hit_count=len(search.hits),
        citations_count=len(citations),
        canonical_lane=(search.query_plan.canonical_lane if search.query_plan is not None else None),
    )

    message_text = rt._normalize_response_wording(message_text)
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
        answer_verifier_valid=verification.valid,
        answer_verifier_reason=verification.reason,
        answer_verifier_fallback_used=not verification.valid,
        deterministic_fallback_available=True,
        answer_verifier_judge_used=semantic_judge_used,
        langgraph_trace_metadata=state.get('langgraph_trace_metadata'),
        engine_trace_metadata=retrieval_trace_metadata,
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
        needs_authentication=preview.needs_authentication,
        graph_path=[*list(preview.graph_path), 'langgraph_response_workflow', 'public_retrieval'],
        risk_flags=rt._build_runtime_risk_flags(
            request_message=request.message,
            message_text=message_text,
            preview=preview,
        ),
        reason='langgraph_native_public_retrieval',
        used_llm=bool(llm_stages),
        llm_stages=llm_stages + (['answer_verifier_judge'] if semantic_judge_used else []),
        retrieval_retry_applied=bool(getattr(search.query_plan, 'corrective_retry_applied', False)),
        retrieval_retry_reason='subquery_coverage_retry' if getattr(search.query_plan, 'corrective_retry_applied', False) else None,
    )
    return {'response': response}
