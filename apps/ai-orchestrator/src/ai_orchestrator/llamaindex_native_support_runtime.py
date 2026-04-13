from __future__ import annotations

# ruff: noqa: F401,F403,F405

"""Support helpers extracted from llamaindex_native_runtime.py."""

LOCAL_EXTRACTED_NAMES = {'_maybe_execute_llamaindex_restricted_doc_fast_path', '_resolve_early_llamaindex_public_answer', '_build_llamaindex_direct_result', '_build_public_retrieval_query_engine', '_maybe_execute_llamaindex_agent_workflow'}

from . import llamaindex_native_runtime as _native
from .models import RetrievalProfile

def _refresh_native_namespace() -> None:
    for name, value in vars(_native).items():
        if name.startswith('__') or name in LOCAL_EXTRACTED_NAMES:
            continue
        globals()[name] = value

async def _maybe_execute_llamaindex_restricted_doc_fast_path(
    *,
    request: MessageResponseRequest,
    settings: Any,
    plan: KernelPlan,
    engine_name: str,
    engine_mode: str,
) -> KernelRunResult | None:
    _refresh_native_namespace()
    if not _looks_like_restricted_doc_query(request.message):
        return None
    actor = await rt._fetch_actor_context(settings=settings, telegram_chat_id=request.telegram_chat_id)
    if not _can_read_private_documents(request=request, actor=actor):
        effective_conversation_id = rt._effective_conversation_id(request)
        conversation_context_bundle = await rt._fetch_conversation_context(
            settings=settings,
            conversation_external_id=effective_conversation_id,
            channel=request.channel.value,
        )
        conversation_context = rt._conversation_context_payload(conversation_context_bundle)
        preview = plan.preview.model_copy(deep=True)
        preview.mode = OrchestrationMode.deny
        preview.classification = IntentClassification(
            domain=QueryDomain.institution,
            access_tier=AccessTier.public,
            confidence=0.99,
            reason='consulta a documento interno negada por falta de acesso explicito',
        )
        preview.selected_tools = list(dict.fromkeys([*preview.selected_tools, 'search_documents']))
        school_profile = await rt._fetch_public_school_profile(settings=settings)
        message_text = rt._compose_deterministic_answer(
            request_message=request.message,
            preview=preview,
            retrieval_hits=[],
            citations=[],
            calendar_events=[],
            query_hints=set(),
        )
        evidence_pack = build_direct_answer_evidence_pack(
            strategy='deny',
            summary='Resposta bloqueada por regra de acesso antes do retrieval restrito do LlamaIndex.',
            supports=[
                MessageEvidenceSupport(
                    kind='guardrail',
                    label='restricted_documents',
                    detail='consulta a documento interno sem autorizacao',
                )
            ],
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
            answer_verifier_reason='restricted_document_access_denied',
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
            suggested_replies=suggested_replies,
            evidence_pack=evidence_pack,
            needs_authentication=False,
            graph_path=[*preview.graph_path, 'llamaindex:restricted_doc_deny'],
            risk_flags=preview.risk_flags,
            reason='llamaindex_restricted_doc_access_deny',
            used_llm=False,
            llm_stages=[],
        )
        return KernelRunResult(
            plan=plan,
            reflection=KernelReflection(
                grounded=True,
                verifier_reason='restricted_document_access_denied',
                fallback_used=False,
                answer_judge_used=False,
                notes=[
                    'route:deny',
                    f'slice:{plan.slice_name}',
                    'evidence:deny',
                ],
            ),
            response=response.model_dump(mode='json'),
        )
    effective_conversation_id = rt._effective_conversation_id(request)
    conversation_context_bundle = await rt._fetch_conversation_context(
        settings=settings,
        conversation_external_id=effective_conversation_id,
        channel=request.channel.value,
    )
    conversation_context = rt._conversation_context_payload(conversation_context_bundle)
    preview = plan.preview.model_copy(deep=True)
    preview.mode = OrchestrationMode.hybrid_retrieval
    preview.classification = IntentClassification(
        domain=QueryDomain.institution,
        access_tier=AccessTier.authenticated,
        confidence=0.98,
        reason='consulta autenticada de documento interno resolvida diretamente pelo retrieval restrito compartilhado',
    )
    preview.selected_tools = list(dict.fromkeys([*preview.selected_tools, 'search_documents']))
    preview.needs_authentication = True
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
        query=request.message,
        visibility='restricted',
        baseline_top_k=3,
        preview=preview,
        profile_override=RetrievalProfile.deep,
    )
    retrieval_result = retrieval_service.hybrid_search(
        query=request.message,
        top_k=retrieval_policy.top_k,
        visibility='private',
        category=retrieval_policy.category,
        profile=retrieval_policy.profile,
    )
    relevant_hits = select_relevant_restricted_hits(request.message, list(retrieval_result.hits))
    citations = [
        citation
        for citation in (_restricted_doc_hit_to_citation(hit) for hit in relevant_hits[:3])
        if citation is not None
    ]
    message_text = rt._normalize_response_wording(
        (
            compose_restricted_document_grounded_answer_for_query(request.message, relevant_hits[:3])
            if relevant_hits
            else compose_restricted_document_no_match_answer(request.message)
        )
        or 'Consultei os documentos internos disponiveis, mas nao encontrei orientacao suficiente para responder com seguranca.'
    )
    school_profile = await rt._fetch_public_school_profile(settings=settings)
    evidence_pack = build_retrieval_evidence_pack(
        citations=citations,
        selected_tools=preview.selected_tools,
        retrieval_backend=RetrievalBackend.qdrant_hybrid,
        summary='Resposta grounded em retrieval restrito autenticado antes do workflow pesado do LlamaIndex.',
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
        citations_count=len(citations),
        suggested_reply_count=len(suggested_replies),
        visual_asset_count=0,
        answer_verifier_valid=True,
        answer_verifier_reason='llamaindex restricted-doc retrieval fast path',
        answer_verifier_fallback_used=False,
        deterministic_fallback_available=True,
        answer_verifier_judge_used=False,
    )
    response = MessageResponse(
        message_text=message_text,
        mode=preview.mode,
        classification=preview.classification,
        retrieval_backend=RetrievalBackend.qdrant_hybrid,
        selected_tools=preview.selected_tools,
        citations=citations,
        visual_assets=[],
            suggested_replies=suggested_replies,
            calendar_events=[],
            evidence_pack=evidence_pack,
            needs_authentication=True,
        graph_path=[
            *preview.graph_path,
            'llamaindex:restricted',
            'llamaindex:restricted_doc_fast_path',
            f'kernel:{plan.stack_name}',
        ],
        risk_flags=preview.risk_flags,
        reason='llamaindex_restricted_doc_fast_path' if relevant_hits else 'llamaindex_restricted_doc_no_match',
    )
    reflection = KernelReflection(
        grounded=True,
        verifier_reason='restricted doc retrieval fast path',
        fallback_used=False,
        answer_judge_used=False,
        notes=[
            f'route:{preview.mode.value}',
            f'slice:{plan.slice_name}',
            'llamaindex:restricted_doc_fast_path',
            f'evidence:{evidence_pack.strategy}',
            *plan.plan_notes,
        ],
    )
    return KernelRunResult(
        plan=plan,
        reflection=reflection,
        response=response.model_dump(mode='json'),
    )


async def _resolve_early_llamaindex_public_answer(
    *,
    request: MessageResponseRequest,
    plan: KernelPlan,
    settings: Any,
    school_profile: dict[str, Any] | None,
    conversation_context: dict[str, Any] | None,
) -> LlamaIndexEarlyPublicAnswer | None:
    _refresh_native_namespace()
    if not isinstance(school_profile, dict):
        return None

    canonical_lane = match_public_canonical_lane(request.message)
    if canonical_lane:
        canonical_answer = _canonical_lane_answer_for_message(
            canonical_lane=canonical_lane,
            message=request.message,
            school_profile=school_profile,
        )
        if canonical_answer:
            return LlamaIndexEarlyPublicAnswer(
                answer_text=canonical_answer,
                reason='canonical_lane',
                canonical_lane=canonical_lane,
            )

    boundary_answer = rt._compose_contextual_public_boundary_answer(
        message=request.message,
        conversation_context=conversation_context,
        profile=school_profile,
    )
    if boundary_answer:
        return LlamaIndexEarlyPublicAnswer(
            answer_text=boundary_answer,
            reason='contextual_boundary',
        )

    normalized_message = rt._normalize_text(request.message)
    if 'biblioteca' in normalized_message and any(
        rt._message_matches_term(normalized_message, term)
        for term in {
            'biblioteca publica',
            'biblioteca pública',
            'publica da cidade',
            'pública da cidade',
            'da cidade',
            'municipal',
            'prefeitura',
        }
    ):
        return LlamaIndexEarlyPublicAnswer(
            answer_text=rt._compose_scope_boundary_answer(
                school_profile or {},
                conversation_context=conversation_context,
            ),
            reason='contextual_boundary',
        )

    if rt._is_explicit_public_pricing_projection_query(
        request.message,
        conversation_context=conversation_context,
    ):
        pricing_plan = rt._build_public_institution_plan(
            request.message,
            list(plan.preview.selected_tools),
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
            return LlamaIndexEarlyPublicAnswer(
                answer_text=pricing_projection_answer,
                reason='pricing_projection',
            )

    contextual_direct_answer = await _maybe_contextual_public_direct_answer(
        request=request,
        analysis_message=request.message,
        preview=plan.preview,
        settings=settings,
        school_profile=school_profile,
        conversation_context=conversation_context,
    )
    if contextual_direct_answer:
        return LlamaIndexEarlyPublicAnswer(
            answer_text=contextual_direct_answer,
            reason='contextual_direct',
        )

    return None


async def _build_llamaindex_direct_result(
    *,
    request: MessageResponseRequest,
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
    _refresh_native_namespace()
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
    )
    response = MessageResponse(
        message_text=normalized_text,
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
            f'llamaindex:{reason_graph_leaf}',
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
        stack_name='llamaindex',
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


def _build_public_retrieval_query_engine(
    *,
    settings: Any,
    preview: Any,
    original_message: str,
    llm: Any | None,
    prefer_citation_engine: bool,
    prefer_native_qdrant_autoretriever: bool,
) -> tuple[Any, PublicHybridCitationRetriever | None]:
    _refresh_native_namespace()
    node_postprocessors = _build_llamaindex_node_postprocessors(settings=settings)
    prefer_recursive_retriever = bool(getattr(settings, 'llamaindex_native_recursive_retriever_enabled', True))
    if (
        llm is not None
        and prefer_native_qdrant_autoretriever
        and LLAMAINDEX_QDRANT_AVAILABLE
        and not prefer_recursive_retriever
    ):
        try:
            collection_name = _resolve_llamaindex_qdrant_collection(settings)
            index = _native_qdrant_vector_index(
                qdrant_url=str(settings.qdrant_url),
                collection_name=collection_name,
                embedding_model=str(settings.document_embedding_model),
            )
            if index is not None:
                vector_store_info = VectorStoreInfo(
                    content_info='Documentos publicos institucionais, FAQs, canais, proposta pedagogica e calendario da escola.',
                    metadata_info=[
                        MetadataInfo(name='visibility', type='str', description='Visibilidade do documento, como public ou private.'),
                        MetadataInfo(name='category', type='str', description='Categoria documental, como faq, policy, calendar ou institutional.'),
                        MetadataInfo(name='document_title', type='str', description='Titulo humano do documento.'),
                        MetadataInfo(name='audience', type='str', description='Publico-alvo do documento.'),
                        MetadataInfo(name='document_set_slug', type='str', description='Conjunto documental ao qual o documento pertence.'),
                        MetadataInfo(name='version_label', type='str', description='Versao publicada do documento.'),
                        MetadataInfo(name='section_parent', type='str', description='Secao pai da passagem recuperada.'),
                        MetadataInfo(name='section_title', type='str', description='Titulo da secao mais especifica da passagem recuperada.'),
                    ],
                )
                retriever = VectorIndexAutoRetriever(
                    index=index,
                    vector_store_info=vector_store_info,
                    llm=llm,
                    similarity_top_k=4,
                    max_top_k=8,
                    extra_filters=MetadataFilters(
                        filters=[
                            MetadataFilter(key='visibility', value='public', operator=FilterOperator.EQ),
                        ]
                    ),
                    verbose=False,
                )
                response_synthesizer = get_response_synthesizer(
                    llm=llm,
                    response_mode=ResponseMode.COMPACT,
                    use_async=True,
                    structured_answer_filtering=True,
                )
                return (
                    CitationQueryEngine(
                        retriever=retriever,
                        llm=llm,
                        response_synthesizer=response_synthesizer,
                        citation_chunk_size=384,
                        citation_chunk_overlap=32,
                        node_postprocessors=node_postprocessors,
                    ),
                    None,
                )
        except Exception:
            pass
    if llm is None or not prefer_citation_engine:
        return (
            PublicRetrievalQueryEngine(
                settings=settings,
                preview=preview,
                original_message=original_message,
            ),
            None,
        )
    retriever = PublicHybridCitationRetriever(
        settings=settings,
        original_message=original_message,
    )
    response_synthesizer = get_response_synthesizer(
        llm=llm,
        response_mode=ResponseMode.COMPACT,
        use_async=True,
        structured_answer_filtering=True,
    )
    return (
        CitationQueryEngine(
            retriever=retriever,
            llm=llm,
            response_synthesizer=response_synthesizer,
            citation_chunk_size=384,
            citation_chunk_overlap=32,
            node_postprocessors=node_postprocessors,
        ),
        retriever,
    )


async def _maybe_execute_llamaindex_agent_workflow(
    *,
    analysis_message: str,
    conversation_context: dict[str, Any] | None,
    llm: Any | None,
    tools: dict[str, QueryEngineTool],
    session_id: str,
    settings: Any | None = None,
) -> tuple[str, tuple[str, ...], tuple[MessageResponseCitation, ...], str] | None:
    _refresh_native_namespace()
    if llm is None or not _llamaindex_llm_supports_function_calls(llm):
        return None

    used_tool_names: list[str] = []
    captured_citations: list[MessageResponseCitation] = []
    captured_reason = 'llamaindex_agent_workflow'

    async def _call_tool(tool_name: str, query: str) -> str:
        nonlocal captured_reason
        response = await _await_with_llamaindex_timeout(tools[tool_name].query_engine.aquery(query), settings=settings)
        used_tool_names.append(tool_name)
        captured_reason = str((response.metadata or {}).get('reason', captured_reason))
        extracted = list(_extract_response_citations(response))
        for citation in extracted:
            if citation not in captured_citations:
                captured_citations.append(citation)
        answer = str(getattr(response, 'response', '') or str(response)).strip()
        if extracted:
            sources = rt._render_source_lines(extracted)
            if sources and sources not in answer:
                answer = f'{answer}\n\n{sources}'
        return answer

    def _tool(tool_name: str, description: str) -> FunctionTool:
        async def _run(query: str) -> str:
            return await _call_tool(tool_name, query)

        return FunctionTool.from_defaults(async_fn=_run, name=tool_name, description=description)

    manager = FunctionAgent(
        name='manager',
        description='Gerencia a conversa publica e decide qual especialista deve assumir.',
        system_prompt=(
            'Voce e o manager publico. Decida qual especialista deve assumir a pergunta. '
            'Use handoff quando a pergunta pedir fatos institucionais, precificacao ou sintese documental. '
            'Nao invente fatos e finalize com a resposta grounded do especialista.'
        ),
        llm=llm,
        can_handoff_to=['profile_specialist', 'pricing_specialist', 'retrieval_specialist'],
        verbose=False,
    )
    profile_specialist = FunctionAgent(
        name='profile_specialist',
        description='Especialista em fatos publicos estruturados da escola.',
        system_prompt='Use apenas a tool public_profile para responder fatos institucionais canonicos.',
        tools=[_tool('public_profile', tools['public_profile'].metadata.description)],
        llm=llm,
        can_handoff_to=['manager'],
        allow_parallel_tool_calls=False,
        verbose=False,
    )
    pricing_specialist = FunctionAgent(
        name='pricing_specialist',
        description='Especialista em simulacoes e perguntas publicas de precificacao.',
        system_prompt='Use apenas a tool pricing_projection para precos, matricula, quantidade de filhos e cenarios hipoteticos.',
        tools=[_tool('pricing_projection', tools['pricing_projection'].metadata.description)],
        llm=llm,
        can_handoff_to=['manager'],
        allow_parallel_tool_calls=False,
        verbose=False,
    )
    retrieval_specialist = FunctionAgent(
        name='retrieval_specialist',
        description='Especialista em sintese documental publica com citacoes.',
        system_prompt='Use apenas a tool public_retrieval para perguntas abertas, comparativas e documentais. Preserve citacoes quando existirem.',
        tools=[_tool('public_retrieval', tools['public_retrieval'].metadata.description)],
        llm=llm,
        can_handoff_to=['manager'],
        allow_parallel_tool_calls=False,
        verbose=False,
    )
    workflow = AgentWorkflow(
        agents=[manager, profile_specialist, pricing_specialist, retrieval_specialist],
        root_agent='manager',
    )
    memory = Memory.from_defaults(
        session_id=session_id,
        chat_history=_build_llamaindex_chat_history(conversation_context),
        token_limit=6000,
    )
    try:
        handler = workflow.run(
            user_msg=analysis_message,
            memory=memory,
            max_iterations=6,
        )
        result = await _await_with_llamaindex_timeout(handler, settings=settings)
    except Exception:
        return None
    answer_text = str(result).strip()
    if not answer_text:
        return None
    if captured_citations:
        sources = rt._render_source_lines(captured_citations)
        if sources and sources not in answer_text:
            answer_text = f'{answer_text}\n\n{sources}'
    selected_tool_names = tuple(dict.fromkeys(used_tool_names)) or ('llamaindex_agent_workflow',)
    return answer_text, selected_tool_names, tuple(captured_citations), 'llamaindex_agent_workflow'
