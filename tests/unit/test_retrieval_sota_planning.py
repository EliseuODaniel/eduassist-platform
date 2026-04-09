from __future__ import annotations

from ai_orchestrator import retrieval as core_retrieval
from ai_orchestrator import python_functions_retrieval
from ai_orchestrator import llamaindex_retrieval
from ai_orchestrator.langgraph_message_workflow import _route_native_path
from ai_orchestrator.models import (
    AccessTier,
    IntentClassification,
    OrchestrationMode,
    OrchestrationPreview,
    QueryDomain,
    RetrievalBackend,
)
from ai_orchestrator_specialist import local_retrieval as specialist_retrieval


def _public_preview(*, mode: OrchestrationMode = OrchestrationMode.hybrid_retrieval) -> OrchestrationPreview:
    return OrchestrationPreview(
        mode=mode,
        classification=IntentClassification(
            domain=QueryDomain.institution,
            access_tier=AccessTier.public,
            confidence=0.9,
            reason='test',
        ),
        reason='test',
        selected_tools=['search_documents'],
        graph_path=['test'],
        retrieval_backend=RetrievalBackend.qdrant_hybrid,
        output_contract='teste',
    )


def test_compound_public_query_builds_subqueries_in_all_retrieval_services() -> None:
    query = 'Quero os contatos de secretaria, financeiro e direcao, junto com mensalidade e bolsa para 3 filhos.'

    core_plan = core_retrieval._build_query_plan(
        query=query,
        top_k=4,
        category=None,
        visibility='public',
        enable_query_variants=True,
        candidate_pool_size=8,
        cheap_candidate_pool_size=6,
        deep_candidate_pool_size=12,
        profile_override=None,
    )
    python_plan = python_functions_retrieval._build_query_plan(
        query=query,
        top_k=4,
        category=None,
        visibility='public',
        enable_query_variants=True,
        candidate_pool_size=8,
        cheap_candidate_pool_size=6,
        deep_candidate_pool_size=12,
        profile_override=None,
    )
    llamaindex_plan = llamaindex_retrieval._build_query_plan(
        query=query,
        top_k=4,
        category=None,
        visibility='public',
        enable_query_variants=True,
        candidate_pool_size=8,
        cheap_candidate_pool_size=6,
        deep_candidate_pool_size=12,
        profile_override=None,
    )
    specialist_plan = specialist_retrieval._build_query_plan(
        query=query,
        top_k=4,
        category=None,
        visibility='public',
        enable_query_variants=True,
        candidate_pool_size=8,
        cheap_candidate_pool_size=6,
        deep_candidate_pool_size=12,
        profile_override=None,
    )

    for plan in (core_plan, python_plan, llamaindex_plan, specialist_plan):
        assert plan.subqueries
        assert any('contato' in item for item in plan.subqueries)
        assert any('mensalidade' in item for item in plan.subqueries)


def test_langgraph_native_route_prefers_public_retrieval_for_public_documentary_queries() -> None:
    preview = _public_preview()

    route = _route_native_path(
        preview,
        'Explique como funciona a rematricula e os principais documentos exigidos.',
    )

    assert route == 'public_retrieval'
