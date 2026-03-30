from __future__ import annotations

from typing import Any

from . import runtime as rt
from .agent_kernel import KernelPlan, KernelReflection, KernelRunResult
from .graph_rag_runtime import run_graph_rag_query
from .llm_provider import compose_with_provider, polish_structured_with_provider, revise_with_provider
from .models import (
    AccessTier,
    MessageResponse,
    MessageResponseCitation,
    MessageResponseRequest,
    OrchestrationMode,
    QueryDomain,
)
from .retrieval import get_retrieval_service


async def execute_kernel_plan(
    *,
    request: MessageResponseRequest,
    settings: Any,
    plan: KernelPlan,
    engine_name: str,
    engine_mode: str,
) -> KernelRunResult:
    actor = await rt._fetch_actor_context(settings=settings, telegram_chat_id=request.telegram_chat_id)
    effective_conversation_id = rt._effective_conversation_id(request)
    conversation_context = await rt._fetch_conversation_context(
        settings=settings,
        conversation_external_id=effective_conversation_id,
        channel=request.channel.value,
    )
    context_payload = rt._conversation_context_payload(conversation_context)
    analysis_message = rt._build_analysis_message(request.message, conversation_context)
    school_profile = await rt._fetch_public_school_profile(settings=settings)
    preview = plan.preview.model_copy(deep=True)

    retrieval_hits: list[Any] = []
    citations: list[MessageResponseCitation] = []
    visual_assets = []
    calendar_events = []
    public_plan = None
    deterministic_fallback_text: str | None = None
    query_hints: set[str] = set()
    semantic_judge_used = False
    answer_verifier_fallback_used = False

    if preview.mode is OrchestrationMode.structured_tool:
        public_plan_sink: dict[str, Any] = {}
        message_text = await rt._compose_structured_tool_answer(
            settings=settings,
            request=request,
            analysis_message=analysis_message,
            preview=preview,
            actor=actor,
            school_profile=school_profile,
            conversation_context=context_payload,
            public_plan_sink=public_plan_sink,
            resolved_public_plan=None,
        )
        public_plan = public_plan_sink.get('plan')
        deterministic_fallback_text = str(public_plan_sink.get('deterministic_text') or message_text)
    elif preview.mode is OrchestrationMode.handoff:
        handoff_payload = await rt._create_support_handoff(
            settings=settings,
            request=request,
            actor=actor,
        )
        message_text = rt._compose_handoff_answer(handoff_payload)
        deterministic_fallback_text = message_text
    elif preview.mode is OrchestrationMode.graph_rag:
        graph_rag_answer = await run_graph_rag_query(
            settings=settings,
            query=analysis_message,
        )
        if graph_rag_answer is not None:
            message_text = str(graph_rag_answer.get('text', '') or '')
        else:
            retrieval_service = get_retrieval_service(
                database_url=settings.database_url,
                qdrant_url=settings.qdrant_url,
                collection_name=settings.qdrant_documents_collection,
                embedding_model=settings.document_embedding_model,
                enable_query_variants=settings.retrieval_enable_query_variants,
                enable_late_interaction_rerank=settings.retrieval_enable_late_interaction_rerank,
                late_interaction_model=settings.retrieval_late_interaction_model,
                candidate_pool_size=settings.retrieval_candidate_pool_size,
            )
            search = retrieval_service.hybrid_search(
                query=analysis_message,
                top_k=4,
                visibility='public',
                category=None,
            )
            retrieval_hits = list(search.hits)
            citations = rt._collect_citations(retrieval_hits)
            deterministic_fallback_text = rt._compose_deterministic_answer(
                request_message=request.message,
                preview=preview,
                retrieval_hits=retrieval_hits,
                citations=citations,
                calendar_events=calendar_events,
                query_hints=query_hints,
            )
            llm_text = await compose_with_provider(
                settings=settings,
                request_message=request.message,
                analysis_message=analysis_message,
                preview=preview,
                citations=citations,
                calendar_events=calendar_events,
                conversation_context=context_payload,
                school_profile=school_profile,
            )
            message_text = llm_text or deterministic_fallback_text
    elif preview.mode is OrchestrationMode.hybrid_retrieval:
        retrieval_service = get_retrieval_service(
            database_url=settings.database_url,
            qdrant_url=settings.qdrant_url,
            collection_name=settings.qdrant_documents_collection,
            embedding_model=settings.document_embedding_model,
            enable_query_variants=settings.retrieval_enable_query_variants,
            enable_late_interaction_rerank=settings.retrieval_enable_late_interaction_rerank,
            late_interaction_model=settings.retrieval_late_interaction_model,
            candidate_pool_size=settings.retrieval_candidate_pool_size,
        )
        search = retrieval_service.hybrid_search(
            query=analysis_message,
            top_k=4,
            visibility='public',
            category=None,
        )
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
            llm_text = await compose_with_provider(
                settings=settings,
                request_message=request.message,
                analysis_message=analysis_message,
                preview=preview,
                citations=citations,
                calendar_events=calendar_events,
                conversation_context=context_payload,
                school_profile=school_profile,
            )
            message_text = llm_text or deterministic_fallback_text
    else:
        message_text = rt._compose_deterministic_answer(
            request_message=request.message,
            preview=preview,
            retrieval_hits=retrieval_hits,
            citations=citations,
            calendar_events=calendar_events,
            query_hints=query_hints,
        )
        deterministic_fallback_text = message_text

    if rt._should_polish_structured_answer(preview=preview, request=request):
        polished_text = await polish_structured_with_provider(
            settings=settings,
            request_message=request.message,
            preview=preview,
            draft_text=message_text,
            conversation_context=context_payload,
            school_profile=school_profile,
        )
        polished_text = rt._preserve_capability_anchor_terms(
            original_text=message_text,
            polished_text=polished_text,
            request_message=request.message,
        )
        if polished_text:
            message_text = polished_text

    if settings.llm_provider == 'openai' and rt._should_run_response_critic(preview=preview, request=request):
        revised_text = await revise_with_provider(
            settings=settings,
            request_message=request.message,
            preview=preview,
            draft_text=message_text,
            conversation_context=context_payload,
            school_profile=school_profile,
        )
        if revised_text:
            message_text = revised_text

    verifier_slot_memory = rt._build_conversation_slot_memory(
        actor=actor,
        profile=school_profile,
        conversation_context=context_payload,
        request_message=request.message,
        public_plan=public_plan,
        preview=preview,
    )
    verification, semantic_judge_used = await rt._verify_answer_against_contract_async(
        settings=settings,
        request_message=request.message,
        preview=preview,
        candidate_text=message_text,
        deterministic_fallback_text=deterministic_fallback_text,
        public_plan=public_plan,
        slot_memory=verifier_slot_memory,
    )
    if not verification.valid and deterministic_fallback_text:
        message_text = deterministic_fallback_text
        answer_verifier_fallback_used = True

    if citations:
        sources = rt._render_source_lines(citations)
        if sources and sources not in message_text:
            message_text = f'{message_text}\n\n{sources}'
    message_text = rt._normalize_response_wording(message_text)

    visual_assets = await rt._maybe_build_visual_assets(
        settings=settings,
        request=request,
        preview=preview,
        actor=actor,
        school_profile=school_profile,
        conversation_context=context_payload,
    )
    suggested_replies = rt._build_suggested_replies(
        request=request,
        preview=preview,
        actor=actor,
        school_profile=school_profile,
        conversation_context=context_payload,
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
        conversation_context=context_payload,
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
        langgraph_trace_metadata={},
    )

    selected_tools = list(preview.selected_tools)
    if (
        preview.mode is OrchestrationMode.structured_tool
        and preview.classification.domain is QueryDomain.institution
        and preview.classification.access_tier is AccessTier.public
        and 'get_public_school_profile' not in selected_tools
    ):
        selected_tools = [*selected_tools, 'get_public_school_profile']

    response = MessageResponse(
        message_text=message_text,
        mode=preview.mode,
        classification=preview.classification,
        retrieval_backend=preview.retrieval_backend,
        selected_tools=selected_tools,
        citations=citations,
        visual_assets=visual_assets,
        suggested_replies=suggested_replies,
        calendar_events=calendar_events,
        needs_authentication=preview.needs_authentication,
        graph_path=[*preview.graph_path, f'kernel:{plan.stack_name}'],
        risk_flags=preview.risk_flags,
        reason=preview.reason,
    )
    reflection = KernelReflection(
        grounded=verification.valid,
        verifier_reason=verification.reason,
        fallback_used=answer_verifier_fallback_used,
        answer_judge_used=semantic_judge_used,
        notes=[
            f'route:{preview.mode.value}',
            f'slice:{plan.slice_name}',
            *plan.plan_notes,
        ],
    )
    return KernelRunResult(
        plan=plan,
        reflection=reflection,
        response=response.model_dump(mode='json'),
    )

