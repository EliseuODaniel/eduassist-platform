from __future__ import annotations

from typing import Any

from . import runtime as rt
from .agent_kernel import KernelPlan, KernelReflection, KernelRunResult
from .evidence_pack import build_retrieval_evidence_pack, build_structured_tool_evidence_pack
from .kernel_runtime import (
    _maybe_contextual_public_direct_answer,
    _maybe_hypothetical_public_pricing_answer,
    _maybe_public_unpublished_direct_answer,
)
from .llm_provider import compose_with_provider
from .models import (
    AccessTier,
    MessageResponse,
    MessageResponseCitation,
    OrchestrationMode,
    QueryDomain,
    RetrievalBackend,
)
from .path_profiles import PathExecutionProfile, get_path_execution_profile
from .retrieval import get_retrieval_service


def _should_use_python_functions_native_path(plan: KernelPlan) -> bool:
    preview = plan.preview
    if preview.mode is OrchestrationMode.structured_tool:
        return True
    if preview.classification.access_tier is not AccessTier.public:
        return False
    if preview.classification.domain not in {QueryDomain.institution, QueryDomain.calendar}:
        return False
    return preview.mode is OrchestrationMode.hybrid_retrieval


async def maybe_execute_python_functions_native_plan(
    *,
    request: Any,
    settings: Any,
    plan: KernelPlan,
    engine_name: str,
    engine_mode: str,
    path_profile: PathExecutionProfile | None = None,
) -> KernelRunResult | None:
    effective_path_profile = path_profile or get_path_execution_profile(engine_name)
    if not _should_use_python_functions_native_path(plan):
        return None

    actor = await rt._fetch_actor_context(settings=settings, telegram_chat_id=request.telegram_chat_id)
    effective_conversation_id = rt._effective_conversation_id(request)
    conversation_context_bundle = await rt._fetch_conversation_context(
        settings=settings,
        conversation_external_id=effective_conversation_id,
        channel=request.channel.value,
    )
    conversation_context = rt._conversation_context_payload(conversation_context_bundle)
    analysis_message = rt._build_analysis_message(request.message, conversation_context_bundle)
    school_profile = await rt._fetch_public_school_profile(settings=settings)
    preview = plan.preview.model_copy(deep=True)

    retrieval_hits: list[Any] = []
    citations: list[MessageResponseCitation] = []
    calendar_events = []
    public_plan = None
    deterministic_fallback_text: str | None = None
    query_hints: set[str] = set()
    semantic_judge_used = False
    answer_verifier_fallback_used = False
    evidence_pack = None

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

    execution_reason = 'python_functions_native_public'

    if contextual_public_answer:
        message_text = contextual_public_answer
        deterministic_fallback_text = contextual_public_answer
        preview = preview.model_copy(
            update={
                'mode': OrchestrationMode.structured_tool,
                'reason': 'python_functions_native_contextual_public_answer',
                'selected_tools': list(dict.fromkeys([*preview.selected_tools, 'get_public_school_profile'])),
            }
        )
        execution_reason = 'python_functions_native_contextual_public_answer'
        evidence_pack = build_structured_tool_evidence_pack(
            selected_tools=preview.selected_tools,
            slice_name=plan.slice_name,
            summary='Resposta direta grounded em fatos publicos canonicos.',
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
                conversation_context=conversation_context,
                school_profile=school_profile,
            )
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

    verifier_slot_memory = rt._build_conversation_slot_memory(
        actor=actor,
        profile=school_profile,
        conversation_context=conversation_context,
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
    retrieval_backend = preview.retrieval_backend
    if preview.mode is OrchestrationMode.hybrid_retrieval:
        retrieval_backend = RetrievalBackend.qdrant_hybrid

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
