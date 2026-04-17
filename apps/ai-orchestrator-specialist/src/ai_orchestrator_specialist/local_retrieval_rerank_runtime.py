from __future__ import annotations

# ruff: noqa: F401,F403,F405,F821,E402

"""Reranking and cached retrieval helpers extracted from local_retrieval.py."""

from functools import lru_cache
import shutil

from fastembed import LateInteractionTextEmbedding, TextEmbedding
from fastembed.rerank.cross_encoder import TextCrossEncoder
import numpy as np

LOCAL_EXTRACTED_NAMES = {
    '_rerank_text_for_hit',
    '_late_interaction_maxsim',
    '_late_interaction_scores',
    '_normalize_visibility_filter',
    '_normalize_category_filter',
    'get_retrieval_service',
    '_build_embedder',
    '_build_cross_encoder_reranker',
    '_build_late_interaction_embedder',
}

from . import local_retrieval as _native


def _refresh_native_namespace() -> None:
    for name, value in vars(_native).items():
        if name.startswith('__') or name in LOCAL_EXTRACTED_NAMES:
            continue
        globals()[name] = value


def _rerank_text_for_hit(hit: RetrievalHit) -> str:
    summary = str(hit.contextual_summary or '').strip()
    excerpt = str(hit.text_excerpt or '').strip()
    return f'{hit.document_title}. {summary} {excerpt}'.strip()


def _late_interaction_maxsim(query_embedding: np.ndarray, document_embedding: np.ndarray) -> float:
    if query_embedding.size == 0 or document_embedding.size == 0:
        return 0.0
    if query_embedding.ndim != 2 or document_embedding.ndim != 2:
        return 0.0
    similarity = np.matmul(query_embedding, document_embedding.T)
    if similarity.size == 0:
        return 0.0
    return float(np.max(similarity, axis=1).sum())


def _late_interaction_scores(
    reranker: LateInteractionTextEmbedding,
    *,
    query: str,
    documents: list[str],
) -> list[float]:
    query_embedding = np.asarray(next(reranker.embed([query])))
    document_embeddings = [np.asarray(item) for item in reranker.embed(documents)]
    return [
        _late_interaction_maxsim(query_embedding, document_embedding)
        for document_embedding in document_embeddings
    ]


def _normalize_visibility_filter(value: str) -> str:
    _refresh_native_namespace()
    normalized = _normalize_text(value)
    if normalized in {'private', 'restricted', 'internal'}:
        return 'restricted'
    return 'public'


def _normalize_category_filter(category: str | None) -> str | None:
    _refresh_native_namespace()
    normalized = _normalize_text(category or '')
    if not normalized:
        return None
    if normalized in {'private_docs', 'public_docs', 'graph_rag'}:
        return None
    return normalized


@lru_cache
def get_retrieval_service(
    *,
    database_url: str,
    qdrant_url: str,
    collection_name: str,
    embedding_model: str,
    enable_query_variants: bool,
    enable_late_interaction_rerank: bool,
    late_interaction_model: str,
    candidate_pool_size: int,
    cheap_candidate_pool_size: int,
    deep_candidate_pool_size: int,
    rerank_fused_weight: float,
    rerank_late_interaction_weight: float,
    enable_cross_encoder_rerank: bool = True,
    cross_encoder_model: str = 'jinaai/jina-reranker-v2-base-multilingual',
    rerank_cross_encoder_weight: float = 0.85,
) -> RetrievalService:
    _refresh_native_namespace()
    return RetrievalService(
        database_url=database_url,
        qdrant_url=qdrant_url,
        collection_name=collection_name,
        embedding_model=embedding_model,
        enable_query_variants=enable_query_variants,
        enable_late_interaction_rerank=enable_late_interaction_rerank,
        late_interaction_model=late_interaction_model,
        candidate_pool_size=candidate_pool_size,
        cheap_candidate_pool_size=cheap_candidate_pool_size,
        deep_candidate_pool_size=deep_candidate_pool_size,
        rerank_fused_weight=rerank_fused_weight,
        rerank_late_interaction_weight=rerank_late_interaction_weight,
        enable_cross_encoder_rerank=enable_cross_encoder_rerank,
        cross_encoder_model=cross_encoder_model,
        rerank_cross_encoder_weight=rerank_cross_encoder_weight,
    )


def _build_embedder(model_name: str) -> TextEmbedding:
    try:
        return TextEmbedding(model_name=model_name)
    except Exception as exc:
        message = str(exc)
        if 'NO_SUCHFILE' not in message and "File doesn't exist" not in message:
            raise
        shutil.rmtree('/tmp/fastembed_cache', ignore_errors=True)
        return TextEmbedding(model_name=model_name)


def _build_cross_encoder_reranker(model_name: str) -> TextCrossEncoder:
    try:
        return TextCrossEncoder(model_name=model_name)
    except Exception as exc:
        message = str(exc)
        if 'NO_SUCHFILE' not in message and "File doesn't exist" not in message:
            raise
        shutil.rmtree('/tmp/fastembed_cache', ignore_errors=True)
        return TextCrossEncoder(model_name=model_name)


def _build_late_interaction_embedder(model_name: str) -> LateInteractionTextEmbedding:
    try:
        return LateInteractionTextEmbedding(model_name=model_name)
    except Exception as exc:
        message = str(exc)
        if 'NO_SUCHFILE' not in message and "File doesn't exist" not in message:
            raise
        shutil.rmtree('/tmp/fastembed_cache', ignore_errors=True)
        return LateInteractionTextEmbedding(model_name=model_name)
