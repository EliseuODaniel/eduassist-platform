from __future__ import annotations

from types import SimpleNamespace

from llama_index.core.postprocessor import LongContextReorder, SentenceEmbeddingOptimizer

from ai_orchestrator.llamaindex_native_runtime import (
    LlamaIndexEarlyPublicAnswer,
    LlamaIndexNativePublicDecision,
    _build_llamaindex_llm,
    _build_llamaindex_node_postprocessors,
    _build_public_document_group_node,
    _build_public_recursive_retriever,
    _compose_semantic_ingress_terminal_answer,
    _deterministic_llamaindex_native_public_decision,
    _extract_public_summary_store_parent_ref_keys,
    _filter_search_to_document_keys,
    _looks_like_open_documentary_bundle_query,
    _should_avoid_llamaindex_public_profile_fast_path,
    _run_public_hybrid_search,
    _resolve_early_llamaindex_public_answer,
    _semantic_ingress_native_public_decision,
    _should_use_llamaindex_teacher_schedule_direct,
    _should_use_llamaindex_teacher_scope_guidance,
    _should_skip_llamaindex_public_fast_paths,
    _should_use_llamaindex_llm_public_resolver,
    _should_use_llamaindex_protected_records_fast_path,
    _should_use_llamaindex_selector_router,
)
from ai_orchestrator.llamaindex_kernel_runtime import _maybe_contextual_public_direct_answer
from ai_orchestrator.llamaindex_kernel import _build_preview as build_llamaindex_kernel_preview
from ai_orchestrator.models import AccessTier, OrchestrationMode, QueryDomain
from ai_orchestrator.path_profiles import PathExecutionProfile


def _request() -> SimpleNamespace:
    return SimpleNamespace(message='Quais sao os diferenciais publicos da escola?')


def _plan() -> SimpleNamespace:
    return SimpleNamespace(
        preview=SimpleNamespace(
            mode=OrchestrationMode.structured_tool,
            selected_tools=[],
            classification=SimpleNamespace(
                access_tier=AccessTier.public,
                domain=QueryDomain.institution,
            ),
        )
    )


def _protected_request(message: str) -> SimpleNamespace:
    return SimpleNamespace(
        message=message,
        telegram_chat_id='1649845499',
    )


def _protected_preview() -> SimpleNamespace:
    return SimpleNamespace(
        selected_tools=[],
        classification=SimpleNamespace(
            access_tier=AccessTier.authenticated,
            domain=QueryDomain.unknown,
        ),
    )


def _guardian_actor() -> dict[str, object]:
    return {
        'linked_students': [
            {'student_id': 'stu-ana', 'full_name': 'Ana Oliveira', 'can_view_academic': True, 'can_view_finance': True},
            {'student_id': 'stu-lucas', 'full_name': 'Lucas Oliveira', 'can_view_academic': True, 'can_view_finance': True},
        ]
    }


def _authenticated_user() -> SimpleNamespace:
    return SimpleNamespace(
        authenticated=True,
        scopes=[],
        role=SimpleNamespace(value='guardian'),
    )


def test_heuristic_public_decision_skips_prompt_router_when_ambiguity_only_enabled() -> None:
    heuristic_decision = LlamaIndexNativePublicDecision(
        conversation_act='highlight',
        answer_mode='documentary',
        required_tools=['hybrid_retrieval'],
    )
    settings = SimpleNamespace(llamaindex_native_prompt_router_ambiguity_only=True)
    assert not _should_use_llamaindex_llm_public_resolver(
        request=_request(),
        plan=_plan(),
        heuristic_decision=heuristic_decision,
        settings=settings,
    )


def test_missing_heuristic_still_allows_prompt_router() -> None:
    settings = SimpleNamespace(llamaindex_native_prompt_router_ambiguity_only=True)
    assert _should_use_llamaindex_llm_public_resolver(
        request=_request(),
        plan=_plan(),
        heuristic_decision=None,
        settings=settings,
    )


def test_deterministic_public_decision_resolves_known_unknown_without_llm() -> None:
    decision = _deterministic_llamaindex_native_public_decision(
        message='Qual e a idade minima para estudar na escola?',
        preview=_plan().preview,
        conversation_context=None,
        school_profile={'school_name': 'Colegio Horizonte'},
    )
    assert decision is not None
    assert decision.answer_mode == 'unpublished'
    assert decision.unpublished_key == 'minimum_age'


def test_deterministic_public_decision_resolves_documentary_bundle_without_llm() -> None:
    decision = _deterministic_llamaindex_native_public_decision(
        message='Compare calendario, agenda de avaliacoes e portal e explique como esses documentos se influenciam.',
        preview=_plan().preview,
        conversation_context=None,
        school_profile={'school_name': 'Colegio Horizonte'},
    )
    assert decision is not None
    assert decision.answer_mode == 'documentary'


def test_deterministic_public_decision_resolves_service_credentials_bundle_without_llm() -> None:
    decision = _deterministic_llamaindex_native_public_decision(
        message='Para resolver portal, credenciais e secretaria, qual e a ordem certa?',
        preview=_plan().preview,
        conversation_context=None,
        school_profile={'school_name': 'Colegio Horizonte'},
    )
    assert decision is not None
    assert decision.answer_mode == 'profile'
    assert decision.focus_hint is not None


def test_selector_router_skips_when_deterministic_decision_already_exists() -> None:
    settings = SimpleNamespace(llamaindex_native_selector_ambiguity_only=True)
    profile = PathExecutionProfile(name='llamaindex', prefer_native_llamaindex_selector=True)
    assert not _should_use_llamaindex_selector_router(
        settings=settings,
        native_decision=LlamaIndexNativePublicDecision(answer_mode='profile', conversation_act='contacts'),
        public_plan=SimpleNamespace(
            conversation_act='contacts',
            required_tools=('get_public_school_profile',),
            secondary_acts=(),
            requested_attribute='service_credentials_bundle',
            requested_channel='secretaria',
            focus_hint='portal, credenciais e secretaria',
        ),
        llm=object(),
        profile=profile,
    )


def test_selector_router_allows_true_ambiguity() -> None:
    settings = SimpleNamespace(llamaindex_native_selector_ambiguity_only=True)
    profile = PathExecutionProfile(name='llamaindex', prefer_native_llamaindex_selector=True)
    assert _should_use_llamaindex_selector_router(
        settings=settings,
        native_decision=None,
        public_plan=SimpleNamespace(
            conversation_act='canonical_fact',
            required_tools=('get_public_school_profile',),
            secondary_acts=(),
            requested_attribute=None,
            requested_channel=None,
            focus_hint=None,
        ),
        llm=object(),
        profile=profile,
    )


def test_build_llamaindex_llm_uses_local_openai_compatible_metadata_for_gemma_profile() -> None:
    settings = SimpleNamespace(
        llm_provider='openai',
        llm_model_profile='gemma4e4b_local',
        openai_api_key='test-key',
        openai_base_url='http://local-llm-gemma4e4b:8080/v1',
        openai_model='ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M',
    )
    llm = _build_llamaindex_llm(settings=settings)
    assert llm is not None
    metadata = llm.metadata
    assert metadata.context_window == 131072
    assert metadata.is_chat_model is True
    assert metadata.is_function_calling_model is False
    assert metadata.model_name == 'ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M'


def test_filter_search_to_document_keys_keeps_only_selected_group_and_hits() -> None:
    group_a = SimpleNamespace(document_title='Manual A', citation=SimpleNamespace(storage_path='a.md'))
    group_b = SimpleNamespace(document_title='Manual B', citation=SimpleNamespace(storage_path='b.md'))
    hit_a = SimpleNamespace(document_title='Manual A', citation=SimpleNamespace(storage_path='a.md'))
    hit_b = SimpleNamespace(document_title='Manual B', citation=SimpleNamespace(storage_path='b.md'))
    search = SimpleNamespace(
        document_groups=[group_a, group_b],
        hits=[hit_a, hit_b],
        model_copy=lambda update: SimpleNamespace(**({'document_groups': [group_a, group_b], 'hits': [hit_a, hit_b]} | update)),
    )
    filtered = _filter_search_to_document_keys(search=search, document_keys={'b.md'})
    assert filtered.document_groups == [group_b]
    assert filtered.hits == [hit_b]


def test_extract_public_summary_store_parent_ref_keys_preserves_order_and_deduplicates() -> None:
    points = SimpleNamespace(
        points=[
            SimpleNamespace(payload={'parent_ref_key': 'doc-a::matricula'}),
            SimpleNamespace(payload={'parent_ref_key': 'doc-a::matricula'}),
            SimpleNamespace(payload={'parent_ref_key': 'doc-b::portal'}),
            SimpleNamespace(payload={}),
        ]
    )
    assert _extract_public_summary_store_parent_ref_keys(points) == (
        'doc-a::matricula',
        'doc-b::portal',
    )


def test_run_public_hybrid_search_prefilters_by_summary_store_and_falls_back_when_empty(monkeypatch) -> None:
    calls: list[tuple[str, ...] | None] = []

    class _FakeRetrievalService:
        def hybrid_search(self, *, parent_ref_keys: tuple[str, ...] | None = None, **_: object) -> SimpleNamespace:
            calls.append(parent_ref_keys)
            if parent_ref_keys:
                return SimpleNamespace(hits=[], document_groups=[], model_copy=lambda update: SimpleNamespace(hits=update.get('hits', []), document_groups=update.get('document_groups', [])))
            hit = SimpleNamespace(document_title='Manual A', citation=SimpleNamespace(storage_path='a.md'))
            group = SimpleNamespace(document_title='Manual A', citation=SimpleNamespace(storage_path='a.md'))
            return SimpleNamespace(
                hits=[hit],
                document_groups=[group],
                model_copy=lambda update: SimpleNamespace(
                    hits=update.get('hits', [hit]),
                    document_groups=update.get('document_groups', [group]),
                ),
            )

    monkeypatch.setattr(
        'ai_orchestrator.llamaindex_native_runtime._query_public_summary_store_parent_ref_keys',
        lambda **_: ('doc-a::matricula',),
    )
    monkeypatch.setattr(
        'ai_orchestrator.llamaindex_native_runtime._maybe_apply_public_summary_stage',
        lambda **kwargs: kwargs['search'],
    )
    settings = SimpleNamespace(llamaindex_native_summary_stage_enabled=True)
    result = _run_public_hybrid_search(
        retrieval_service=_FakeRetrievalService(),
        query='compare calendario e matricula',
        settings=settings,
    )
    assert calls == [('doc-a::matricula',), None]
    assert len(result.hits) == 1


def test_clarify_heuristic_keeps_prompt_router_enabled() -> None:
    heuristic_decision = LlamaIndexNativePublicDecision(answer_mode='clarify')
    settings = SimpleNamespace(llamaindex_native_prompt_router_ambiguity_only=True)
    assert _should_use_llamaindex_llm_public_resolver(
        request=_request(),
        plan=_plan(),
        heuristic_decision=heuristic_decision,
        settings=settings,
    )


def test_documentary_prompt_skips_llamaindex_fast_paths() -> None:
    assert _should_skip_llamaindex_public_fast_paths(
        'Com base nos documentos publicos e citando as fontes, compare os processos da escola.'
    )


def test_open_documentary_bundle_query_skips_fast_paths_without_explicit_citation_phrase() -> None:
    heuristic_decision = LlamaIndexNativePublicDecision(
        conversation_act='highlight',
        answer_mode='documentary',
    )
    message = (
        'Compare calendario, agenda de avaliacoes e manual de matricula '
        'e explique como esses documentos se influenciam ao longo do ano.'
    )
    assert _looks_like_open_documentary_bundle_query(message)


def test_documentary_open_query_avoids_llamaindex_public_profile_fast_path() -> None:
    assert _should_avoid_llamaindex_public_profile_fast_path(
        message='Quero entender qual imagem institucional surge quando junto autoridade escolar, atendimento digital e encaminhamento de impasses na base publica.',
        public_plan=SimpleNamespace(conversation_act='highlight'),
        native_decision=LlamaIndexNativePublicDecision(answer_mode='profile', conversation_act='highlight'),
    )


def test_documentary_native_decision_skips_later_canonical_lane_even_without_exact_trigger_phrase() -> None:
    native_decision = LlamaIndexNativePublicDecision(
        conversation_act='highlight',
        answer_mode='documentary',
    )
    assert _should_skip_llamaindex_public_fast_paths(
        'Quais temas atravessam calendario, portal e comunicacao com responsaveis?',
        native_decision=native_decision,
    )


def test_build_llamaindex_node_postprocessors_returns_native_stack() -> None:
    settings = SimpleNamespace(
        document_embedding_model='sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2',
        llamaindex_native_sentence_optimizer_enabled=True,
        llamaindex_native_sentence_optimizer_percentile_cutoff=0.6,
        llamaindex_native_long_context_reorder_enabled=True,
    )
    postprocessors = _build_llamaindex_node_postprocessors(settings=settings)
    assert any(isinstance(item, SentenceEmbeddingOptimizer) for item in postprocessors)
    assert any(isinstance(item, LongContextReorder) for item in postprocessors)


def test_build_public_document_group_node_preserves_section_context() -> None:
    group = SimpleNamespace(
        document_title='Manual de Matricula',
        document_score=0.92,
        primary_section='Matricula > Documentos',
        primary_summary='documentos exigidos e prazos de envio',
        primary_excerpt='A familia deve enviar os documentos pelo portal ou diretamente para a secretaria.',
        section_titles=['Documentos', 'Prazos'],
        citation=SimpleNamespace(
            version_label='2026.1',
            storage_path='corpus/public/manual-matricula.md',
            chunk_id='chunk-1',
        ),
    )
    node_with_score = _build_public_document_group_node(group)
    assert 'Resumo contextual' in node_with_score.node.text
    assert 'Secoes relacionadas' in node_with_score.node.text
    assert node_with_score.node.metadata['section_path'] == 'Matricula > Documentos'


def test_build_public_recursive_retriever_resolves_children_to_parent_context() -> None:
    hit = SimpleNamespace(
        chunk_id='chunk-1',
        document_title='Manual de Matricula',
        text_excerpt='A familia envia documentos pelo portal.',
        contextual_summary='envio de documentos e secretaria',
        section_path='Matricula > Documentos',
        section_parent='Matricula',
        section_title='Documentos',
        fused_score=0.7,
        rerank_score=0.9,
        citation=SimpleNamespace(
            version_label='2026.1',
            storage_path='corpus/public/manual-matricula.md',
            chunk_id='chunk-1',
        ),
    )
    group = SimpleNamespace(
        document_title='Manual de Matricula',
        document_score=0.92,
        primary_section='Matricula > Documentos',
        primary_summary='documentos exigidos e prazos de envio',
        primary_excerpt='A familia deve enviar os documentos pelo portal ou pela secretaria.',
        section_titles=['Documentos', 'Prazos'],
        citation=SimpleNamespace(
            version_label='2026.1',
            storage_path='corpus/public/manual-matricula.md',
            chunk_id='chunk-1',
        ),
    )
    search = SimpleNamespace(hits=[hit], document_groups=[group])
    retriever = _build_public_recursive_retriever(search=search)
    assert retriever is not None
    nodes = retriever.retrieve('Quais documentos preciso enviar?')
    assert nodes
    assert 'Trecho principal' in nodes[0].node.text
    assert nodes[0].node.metadata['document_title'] == 'Manual de Matricula'


def test_llamaindex_protected_records_fast_path_detects_family_finance_aggregate() -> None:
    assert _should_use_llamaindex_protected_records_fast_path(
        request=_protected_request(
            'Como esta a situacao financeira da familia neste momento, incluindo atrasos, vencimentos proximos e proximo passo?'
        ),
        actor=_guardian_actor(),
        preview=_protected_preview(),
        conversation_context=None,
    )


def test_llamaindex_protected_records_fast_path_detects_family_attendance_aggregate() -> None:
    assert _should_use_llamaindex_protected_records_fast_path(
        request=_protected_request(
            'Me de um panorama de faltas e frequencia dos meus filhos, apontando quem exige maior atencao agora.'
        ),
        actor=_guardian_actor(),
        preview=_protected_preview(),
        conversation_context=None,
    )


def test_llamaindex_protected_records_fast_path_detects_access_scope() -> None:
    assert _should_use_llamaindex_protected_records_fast_path(
        request=_protected_request(
            'Estou autenticado como quem e com qual escopo? Quero saber o que consigo ver de academico e financeiro.'
        ),
        actor=_guardian_actor(),
        preview=_protected_preview(),
        conversation_context=None,
    )


def test_llamaindex_protected_records_fast_path_detects_academic_followup() -> None:
    assert _should_use_llamaindex_protected_records_fast_path(
        request=_protected_request(
            'Sem repetir o quadro inteiro, recorte so a Ana e mostre onde o risco academico dela esta mais alto.'
        ),
        actor=_guardian_actor(),
        preview=_protected_preview(),
        conversation_context=None,
    )


def test_llamaindex_kernel_preview_keeps_public_process_compare_public_when_authenticated() -> None:
    preview = build_llamaindex_kernel_preview(
        request=SimpleNamespace(
            message='Compare rematricula, transferencia e cancelamento destacando o que muda na pratica.',
            user=_authenticated_user(),
        ),
        settings=SimpleNamespace(),
    )
    assert preview.reason.startswith('llamaindex_local_public_')
    assert preview.classification.access_tier == AccessTier.public
    assert 'get_public_school_profile' in preview.selected_tools


def test_llamaindex_kernel_preview_keeps_family_finance_aggregate_protected_when_authenticated() -> None:
    preview = build_llamaindex_kernel_preview(
        request=SimpleNamespace(
            message='Explique a minha situacao financeira como se eu fosse leigo, separando mensalidade, taxa, atraso e desconto.',
            user=_authenticated_user(),
        ),
        settings=SimpleNamespace(),
    )
    assert preview.reason == 'llamaindex_local_protected:finance'
    assert preview.classification.access_tier == AccessTier.sensitive
    assert 'get_financial_summary' in preview.selected_tools
    assert 'project_public_pricing' not in preview.selected_tools


def test_teacher_schedule_direct_runs_without_teacher_scope_guidance_phrase() -> None:
    assert _should_use_llamaindex_teacher_schedule_direct(
        teacher_authenticated=True,
        should_fetch_teacher_schedule=True,
    ) is True
    assert _should_use_llamaindex_teacher_scope_guidance(
        teacher_scope_query=False,
        should_fetch_teacher_schedule=True,
    ) is False


def test_teacher_scope_guidance_only_runs_when_schedule_fetch_is_not_needed() -> None:
    assert _should_use_llamaindex_teacher_schedule_direct(
        teacher_authenticated=True,
        should_fetch_teacher_schedule=False,
    ) is False
    assert _should_use_llamaindex_teacher_scope_guidance(
        teacher_scope_query=True,
        should_fetch_teacher_schedule=False,
    ) is True


async def _resolve_early_public_answer(message: str, monkeypatch) -> LlamaIndexEarlyPublicAnswer | None:
    monkeypatch.setattr(
        'ai_orchestrator.llamaindex_native_runtime.rt._compose_contextual_public_boundary_answer',
        lambda **_: 'Resposta de boundary.',
    )
    monkeypatch.setattr(
        'ai_orchestrator.llamaindex_native_runtime._maybe_contextual_public_direct_answer',
        lambda **_: 'Resposta contextual generica.',
    )
    monkeypatch.setattr(
        'ai_orchestrator.llamaindex_native_runtime.rt._is_explicit_public_pricing_projection_query',
        lambda *_, **__: False,
    )
    return await _resolve_early_llamaindex_public_answer(
        request=SimpleNamespace(message=message, user=_authenticated_user()),
        plan=SimpleNamespace(preview=_plan().preview),
        settings=SimpleNamespace(),
        school_profile={'school_name': 'Colegio Horizonte'},
        conversation_context=None,
    )


def test_early_llamaindex_public_answer_prioritizes_canonical_lane(monkeypatch) -> None:
    monkeypatch.setattr(
        'ai_orchestrator.llamaindex_native_runtime.match_public_canonical_lane',
        lambda message: 'public_bundle.process_compare' if 'rematricula' in message else None,
    )
    monkeypatch.setattr(
        'ai_orchestrator.llamaindex_native_runtime.compose_public_canonical_lane_answer',
        lambda lane, profile=None: 'Comparacao canonica de processo.' if lane == 'public_bundle.process_compare' else None,
    )
    result = __import__('asyncio').run(
        _resolve_early_public_answer(
            'Compare rematricula, transferencia e cancelamento destacando o que muda na pratica.',
            monkeypatch,
        )
    )
    assert result is not None
    assert result.reason == 'canonical_lane'
    assert result.canonical_lane == 'public_bundle.process_compare'
    assert result.answer_text == 'Comparacao canonica de processo.'


def test_contextual_public_direct_answer_skips_admin_finance_block_followup(monkeypatch) -> None:
    monkeypatch.setattr(
        'ai_orchestrator.llamaindex_kernel_runtime.rt._llm_forced_mode_enabled',
        lambda **_: False,
    )
    result = __import__('asyncio').run(
        _maybe_contextual_public_direct_answer(
            request=SimpleNamespace(
                message='Se nada estiver bloqueando, fala isso de forma direta.',
                user=_authenticated_user(),
            ),
            analysis_message='Se nada estiver bloqueando, fala isso de forma direta.',
            preview=SimpleNamespace(
                classification=SimpleNamespace(
                    access_tier=AccessTier.public,
                    domain=QueryDomain.institution,
                ),
            ),
            settings=SimpleNamespace(),
            school_profile={'school_name': 'Colegio Horizonte'},
            conversation_context={
                'recent_messages': [
                    {
                        'sender_type': 'user',
                        'content': 'Minha documentacao ou cadastro esta bloqueando atendimento financeiro? Quero um panorama combinado de documentacao e financeiro.',
                    },
                    {
                        'sender_type': 'assistant',
                        'content': 'Na documentacao e no cadastro escolar de Ana Oliveira, o status atual esta como pending. No financeiro, Ana Oliveira esta com 2 faturas em aberto.',
                    },
                ]
            },
        )
    )
    assert result is None


def test_semantic_ingress_native_public_decision_preserves_public_contract() -> None:
    public_plan = SimpleNamespace(
        conversation_act='greeting',
        required_tools=('get_public_school_profile', 'list_assistant_capabilities'),
        secondary_acts=(),
        requested_attribute=None,
        requested_channel=None,
        focus_hint=None,
        use_conversation_context=False,
    )

    decision = _semantic_ingress_native_public_decision(public_plan=public_plan)

    assert decision.conversation_act == 'greeting'
    assert decision.answer_mode == 'profile'
    assert decision.required_tools == ['get_public_school_profile', 'list_assistant_capabilities']


def test_semantic_ingress_native_public_decision_keeps_identity_contract() -> None:
    public_plan = SimpleNamespace(
        conversation_act='assistant_identity',
        required_tools=('get_public_school_profile', 'get_org_directory'),
        secondary_acts=(),
        requested_attribute=None,
        requested_channel=None,
        focus_hint=None,
        use_conversation_context=True,
    )

    decision = _semantic_ingress_native_public_decision(public_plan=public_plan)

    assert decision.conversation_act == 'assistant_identity'
    assert decision.answer_mode == 'profile'
    assert decision.required_tools == ['get_public_school_profile', 'get_org_directory']
    assert decision.use_conversation_context is True


def test_semantic_ingress_native_public_decision_keeps_input_clarification_contract() -> None:
    public_plan = SimpleNamespace(
        conversation_act='input_clarification',
        required_tools=('get_public_school_profile',),
        secondary_acts=(),
        requested_attribute=None,
        requested_channel=None,
        focus_hint=None,
        use_conversation_context=False,
    )

    decision = _semantic_ingress_native_public_decision(public_plan=public_plan)

    assert decision.conversation_act == 'input_clarification'
    assert decision.answer_mode == 'profile'
    assert decision.required_tools == ['get_public_school_profile']


def test_compose_semantic_ingress_terminal_answer_uses_safe_input_clarification_contract() -> None:
    public_plan = SimpleNamespace(
        conversation_act='input_clarification',
    )

    answer = _compose_semantic_ingress_terminal_answer(
        school_profile={'school_name': 'Colegio Horizonte'},
        request_message='???',
        actor=None,
        conversation_context=None,
        public_plan=public_plan,
    )

    lowered = answer.lower()
    assert 'nao consegui interpretar' in lowered or 'não consegui interpretar' in lowered
    assert 'reformule' in lowered
    assert 'cadastro' not in lowered
