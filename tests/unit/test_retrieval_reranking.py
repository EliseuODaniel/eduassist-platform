from __future__ import annotations

from ai_orchestrator.models import RetrievalCitation, RetrievalHit
from ai_orchestrator.retrieval import RetrievalService as OrchestratorRetrievalService
from ai_orchestrator_specialist.local_retrieval import RetrievalService as SpecialistRetrievalService


class _FakeLateInteractionReranker:
    def embed(self, texts: list[str]):
        for text in texts:
            normalized = str(text).lower()
            if 'calendario' in normalized:
                yield [[1.0, 0.0]]
            elif 'financeiro' in normalized or 'boleto' in normalized:
                yield [[0.1, 1.0]]
            else:
                yield [[0.5, 0.5]]


class _FakeCrossEncoderReranker:
    def rerank(self, *, query: str, documents: list[str]):
        del query
        for document in documents:
            normalized = str(document).lower()
            if 'calendario' in normalized:
                yield 0.95
            elif 'financeiro' in normalized or 'boleto' in normalized:
                yield 0.15
            else:
                yield 0.4


def _hit(*, chunk_id: str, title: str, excerpt: str, fused_score: float) -> RetrievalHit:
    return RetrievalHit(
        chunk_id=chunk_id,
        document_title=title,
        category='public_docs',
        audience='familias',
        visibility='public',
        text_excerpt=excerpt,
        contextual_summary=excerpt,
        fused_score=fused_score,
        citation=RetrievalCitation(
            document_title=title,
            version_label='v1',
            storage_path=f'/docs/{chunk_id}.md',
            chunk_id=chunk_id,
            chunk_index=0,
        ),
    )


def _make_service(service_cls):
    service = service_cls.__new__(service_cls)
    service.enable_late_interaction_rerank = True
    service.late_interaction_model = 'answerdotai/answerai-colbert-small-v1'
    service.enable_cross_encoder_rerank = True
    service.cross_encoder_model = 'jinaai/jina-reranker-v2-base-multilingual'
    service.rerank_fused_weight = 0.35
    service.rerank_late_interaction_weight = 0.65
    service.rerank_cross_encoder_weight = 0.85
    service._late_interaction_embedder = _FakeLateInteractionReranker()
    service._cross_encoder_reranker = _FakeCrossEncoderReranker()
    service._last_reranker_model = None
    return service


def _assert_combined_rerank(service_cls) -> None:
    service = _make_service(service_cls)
    hits = [
        _hit(
            chunk_id='finance',
            title='Financeiro',
            excerpt='Financeiro com boletos e pendencias.',
            fused_score=0.92,
        ),
        _hit(
            chunk_id='calendar',
            title='Calendario institucional',
            excerpt='Calendario com datas e eventos escolares.',
            fused_score=0.74,
        ),
    ]

    reranked, reranker_applied = service._rerank_hits(
        query='Quais datas importantes aparecem no calendario?',
        hits=hits,
        rerank_limit=2,
        top_k=2,
    )

    assert reranker_applied is True
    assert [hit.chunk_id for hit in reranked] == ['calendar', 'finance']
    assert service._last_reranker_model == (
        'answerdotai/answerai-colbert-small-v1 + jinaai/jina-reranker-v2-base-multilingual'
    )
    assert reranked[0].rerank_score == 0.95
    assert reranked[0].document_score is not None


def test_orchestrator_retrieval_combines_late_interaction_and_cross_encoder() -> None:
    _assert_combined_rerank(OrchestratorRetrievalService)


def test_specialist_retrieval_combines_late_interaction_and_cross_encoder() -> None:
    _assert_combined_rerank(SpecialistRetrievalService)
