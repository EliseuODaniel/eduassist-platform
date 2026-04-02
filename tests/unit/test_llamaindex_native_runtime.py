from __future__ import annotations

from types import SimpleNamespace

from llama_index.core.postprocessor import LongContextReorder, SentenceEmbeddingOptimizer

from ai_orchestrator.llamaindex_native_runtime import (
    LlamaIndexNativePublicDecision,
    _build_llamaindex_node_postprocessors,
    _build_public_document_group_node,
    _build_public_recursive_retriever,
    _looks_like_open_documentary_bundle_query,
    _should_skip_llamaindex_public_fast_paths,
    _should_use_llamaindex_llm_public_resolver,
)
from ai_orchestrator.models import AccessTier, OrchestrationMode, QueryDomain


def _request() -> SimpleNamespace:
    return SimpleNamespace(message='Quais sao os diferenciais publicos da escola?')


def _plan() -> SimpleNamespace:
    return SimpleNamespace(
        preview=SimpleNamespace(
            mode=OrchestrationMode.structured_tool,
            classification=SimpleNamespace(
                access_tier=AccessTier.public,
                domain=QueryDomain.institution,
            ),
        )
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
    assert _should_skip_llamaindex_public_fast_paths(
        message,
        heuristic_decision=heuristic_decision,
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
