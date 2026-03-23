from __future__ import annotations

from functools import lru_cache
from typing import Any

import psycopg
from fastembed import TextEmbedding
from psycopg.rows import dict_row
from qdrant_client import QdrantClient, models

from .models import RetrievalBackend, RetrievalCitation, RetrievalHit, RetrievalSearchResponse


RRF_K = 60


class RetrievalService:
    def __init__(self, *, database_url: str, qdrant_url: str, collection_name: str, embedding_model: str) -> None:
        self.database_url = database_url
        self.collection_name = collection_name
        self.embedding_model = embedding_model
        self.qdrant = QdrantClient(url=qdrant_url)
        self.embedder = TextEmbedding(model_name=embedding_model)

    def hybrid_search(
        self,
        *,
        query: str,
        top_k: int,
        visibility: str,
        category: str | None = None,
    ) -> RetrievalSearchResponse:
        lexical_hits = self._lexical_search(query=query, top_k=top_k, visibility=visibility, category=category)
        vector_hits = self._vector_search(query=query, top_k=top_k, visibility=visibility, category=category)
        fused_hits = self._fuse_hits(lexical_hits=lexical_hits, vector_hits=vector_hits, top_k=top_k)
        return RetrievalSearchResponse(
            query=query,
            retrieval_backend=RetrievalBackend.qdrant_hybrid,
            total_hits=len(fused_hits),
            hits=fused_hits,
        )

    def collection_status(self) -> dict[str, Any]:
        exists = self.qdrant.collection_exists(self.collection_name)
        if not exists:
            return {'exists': False, 'collection': self.collection_name}

        collection = self.qdrant.get_collection(self.collection_name)
        vectors_config = None
        config = getattr(collection, 'config', None)
        if config is not None:
            params = getattr(config, 'params', None)
            if params is not None:
                vectors_config = getattr(params, 'vectors', None)
        return {
            'exists': True,
            'collection': self.collection_name,
            'points_count': getattr(collection, 'points_count', None),
            'indexed_vectors_count': getattr(collection, 'indexed_vectors_count', None),
            'vectors_config': str(vectors_config) if vectors_config is not None else None,
            'status': str(collection.status),
        }

    def _lexical_search(
        self,
        *,
        query: str,
        top_k: int,
        visibility: str,
        category: str | None,
    ) -> list[dict[str, Any]]:
        conditions = [
            'chunk.visibility = %(visibility)s',
            'document.visibility = %(visibility)s',
            """
            to_tsvector(
              'portuguese',
              coalesce(chunk.contextual_summary, '') || ' ' || chunk.text_content
            ) @@ websearch_to_tsquery('portuguese', %(query)s)
            """.strip(),
        ]
        params: dict[str, Any] = {'query': query, 'top_k': top_k, 'visibility': visibility}
        if category:
            conditions.append('document.category = %(category)s')
            params['category'] = category

        sql = f"""
            select
              chunk.id::text as chunk_id,
              chunk.chunk_index,
              chunk.text_content,
              chunk.contextual_summary,
              document.title as document_title,
              document.category,
              document.audience,
              document.visibility,
              version.version_label,
              version.storage_path,
              ts_rank_cd(
                to_tsvector(
                  'portuguese',
                  coalesce(chunk.contextual_summary, '') || ' ' || chunk.text_content
                ),
                websearch_to_tsquery('portuguese', %(query)s)
              ) as lexical_score
            from documents.document_chunks chunk
            join documents.document_versions version on version.id = chunk.document_version_id
            join documents.documents document on document.id = version.document_id
            where {' and '.join(conditions)}
            order by lexical_score desc, document.title asc, chunk.chunk_index asc
            limit %(top_k)s
        """

        with psycopg.connect(self.database_url, row_factory=dict_row) as connection:
            with connection.cursor() as cursor:
                cursor.execute(sql, params)
                rows = cursor.fetchall()

        return [dict(row) for row in rows]

    def _vector_search(
        self,
        *,
        query: str,
        top_k: int,
        visibility: str,
        category: str | None,
    ) -> list[dict[str, Any]]:
        if not self.qdrant.collection_exists(self.collection_name):
            return []

        vector = next(self.embedder.embed([query])).tolist()
        must_filters = [
            models.FieldCondition(key='visibility', match=models.MatchValue(value=visibility)),
        ]
        if category:
            must_filters.append(models.FieldCondition(key='category', match=models.MatchValue(value=category)))

        response = self.qdrant.query_points(
            collection_name=self.collection_name,
            query=vector,
            query_filter=models.Filter(must=must_filters),
            limit=top_k,
            with_payload=True,
        )
        points = getattr(response, 'points', response)

        hits: list[dict[str, Any]] = []
        for point in points:
            payload = point.payload or {}
            hits.append(
                {
                    'chunk_id': str(payload.get('chunk_id', point.id)),
                    'chunk_index': int(payload.get('chunk_index', 0)),
                    'text_content': str(payload.get('text_content', '')),
                    'contextual_summary': payload.get('contextual_summary'),
                    'document_title': str(payload.get('document_title', 'Documento sem titulo')),
                    'category': str(payload.get('category', 'unknown')),
                    'audience': str(payload.get('audience', 'publico')),
                    'visibility': str(payload.get('visibility', visibility)),
                    'version_label': str(payload.get('version_label', 'v0')),
                    'storage_path': str(payload.get('storage_path', '')),
                    'vector_score': float(point.score or 0.0),
                }
            )
        return hits

    def _fuse_hits(
        self,
        *,
        lexical_hits: list[dict[str, Any]],
        vector_hits: list[dict[str, Any]],
        top_k: int,
    ) -> list[RetrievalHit]:
        combined: dict[str, dict[str, Any]] = {}

        for rank, hit in enumerate(lexical_hits, start=1):
            item = combined.setdefault(hit['chunk_id'], dict(hit))
            item['lexical_score'] = float(hit.get('lexical_score', 0.0))
            item['rrf_score'] = item.get('rrf_score', 0.0) + 1.0 / (RRF_K + rank)

        for rank, hit in enumerate(vector_hits, start=1):
            item = combined.setdefault(hit['chunk_id'], dict(hit))
            item.setdefault('lexical_score', None)
            item['vector_score'] = float(hit.get('vector_score', 0.0))
            item['rrf_score'] = item.get('rrf_score', 0.0) + 1.0 / (RRF_K + rank)
            for key, value in hit.items():
                item.setdefault(key, value)

        fused = sorted(
            combined.values(),
            key=lambda item: (float(item.get('rrf_score', 0.0)), float(item.get('vector_score', 0.0) or 0.0)),
            reverse=True,
        )

        return [
            RetrievalHit(
                chunk_id=item['chunk_id'],
                document_title=item['document_title'],
                category=item['category'],
                audience=item['audience'],
                visibility=item['visibility'],
                text_excerpt=self._excerpt(item.get('text_content', '')),
                contextual_summary=item.get('contextual_summary'),
                fused_score=round(float(item.get('rrf_score', 0.0)), 6),
                lexical_score=(
                    round(float(item['lexical_score']), 6)
                    if item.get('lexical_score') is not None
                    else None
                ),
                vector_score=(
                    round(float(item['vector_score']), 6)
                    if item.get('vector_score') is not None
                    else None
                ),
                citation=RetrievalCitation(
                    document_title=item['document_title'],
                    version_label=item['version_label'],
                    storage_path=item['storage_path'],
                    chunk_id=item['chunk_id'],
                    chunk_index=int(item.get('chunk_index', 0)),
                ),
            )
            for item in fused[:top_k]
        ]

    def _excerpt(self, text: str, max_chars: int = 280) -> str:
        clean = ' '.join(text.split())
        if len(clean) <= max_chars:
            return clean
        return f'{clean[: max_chars - 3].rstrip()}...'


@lru_cache
def get_retrieval_service(
    *,
    database_url: str,
    qdrant_url: str,
    collection_name: str,
    embedding_model: str,
) -> RetrievalService:
    return RetrievalService(
        database_url=database_url,
        qdrant_url=qdrant_url,
        collection_name=collection_name,
        embedding_model=embedding_model,
    )
