from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
import re
import shutil
from time import monotonic
from typing import Any
import unicodedata

from eduassist_observability import record_counter, record_histogram, set_span_attributes, start_span
from fastembed import LateInteractionTextEmbedding, TextEmbedding
import numpy as np
import psycopg
from psycopg.rows import dict_row
from qdrant_client import QdrantClient, models

from .model_cache import clear_fastembed_cache
from .models import (
    RetrievalBackend,
    RetrievalCitation,
    RetrievalDocumentGroup,
    RetrievalHit,
    RetrievalProfile,
    RetrievalQueryPlan,
    RetrievalSearchResponse,
    UserContext,
)
from .llamaindex_public_knowledge import match_public_canonical_lane


RRF_K = 60
_STOPWORDS = {
    'a',
    'as',
    'ao',
    'aos',
    'com',
    'como',
    'da',
    'das',
    'de',
    'do',
    'dos',
    'e',
    'ela',
    'ele',
    'em',
    'essa',
    'esse',
    'esta',
    'este',
    'eu',
    'me',
    'minha',
    'meu',
    'na',
    'nas',
    'no',
    'nos',
    'o',
    'os',
    'para',
    'por',
    'qual',
    'quais',
    'se',
    'sobre',
    'tem',
    'tenho',
    'um',
    'uma',
    'voces',
    'vocês',
}
_INTENT_EXPANSIONS = {
    'pricing_lookup': 'mensalidade matricula valores descontos bolsas segmentos',
    'timeline_lookup': 'calendario aulas reuniao pais formatura matricula datas',
    'document_lookup': 'documentacao matricula documentos secretaria email portal',
    'contact_lookup': 'endereco cidade estado cep telefone email secretaria contato',
    'corpus_overview': 'proposta pedagogica diferenciais projeto de vida rotina escolar acompanhamento inclusao vida escolar permanencia familia apoio estudante secretaria portal credenciais documentos',
    'policy_lookup': 'avaliacao recuperacao promocao frequencia pontualidade saude medicacao segunda chamada autorizacoes saidas pedagogicas regras',
    'admissions_lookup': 'matricula rematricula transferencia cancelamento bolsas descontos documentos entrevista acolhimento prazos protocolos',
    'service_overview': 'secretaria portal aplicativo credenciais login senha suporte digital servicos atendimento documentos prazos canais protocolos',
}
_TOPIC_FAMILIES: dict[str, set[str]] = {
    'contacts': {
        'telefone',
        'whatsapp',
        'instagram',
        'site',
        'email',
        'contato',
        'secretaria',
        'direcao',
        'direção',
        'coordenacao',
        'coordenação',
        'financeiro',
    },
    'pricing': {
        'mensalidade',
        'mensalidades',
        'matricula',
        'matrícula',
        'bolsa',
        'bolsas',
        'desconto',
        'descontos',
        'valor',
        'valores',
        'preco',
        'preço',
        'filhos',
    },
    'timeline': {
        'calendario',
        'calendário',
        'aulas',
        'inicio',
        'início',
        'reuniao',
        'reunião',
        'responsaveis',
        'responsáveis',
        'pais',
        'formatura',
        'datas',
    },
    'admissions': {
        'matricula',
        'matrícula',
        'rematricula',
        'rematrícula',
        'transferencia',
        'transferência',
        'cancelamento',
        'documentacao',
        'documentação',
        'visita',
        'acolhimento',
    },
    'policy': {
        'avaliacao',
        'avaliação',
        'recuperacao',
        'recuperação',
        'promocao',
        'promoção',
        'frequencia',
        'frequência',
        'segunda',
        'chamada',
        'regra',
        'regras',
    },
    'services': {
        'portal',
        'credenciais',
        'login',
        'senha',
        'aplicativo',
        'app',
        'servicos',
        'serviços',
        'documentos',
        'documentacao',
        'documentação',
    },
}
_TOPIC_QUERIES: dict[str, str] = {
    'contacts': 'contato secretaria financeiro direcao coordenacao canais oficiais',
    'pricing': 'mensalidade matricula bolsas descontos simulacao comercial publica',
    'timeline': 'calendario matricula inicio das aulas reuniao de responsaveis datas publicadas',
    'admissions': 'matricula rematricula transferencia cancelamento documentos e prazos',
    'policy': 'avaliacao recuperacao promocao frequencia e regras academicas',
    'services': 'portal credenciais secretaria documentos e servicos digitais',
}
_RESTRICTED_DOC_QUERY_TERMS = {
    'procedimento interno',
    'protocolo interno',
    'manual interno',
    'material interno',
    'playbook interno',
    'orientacao interna',
    'orientação interna',
    'documento interno',
    'documentos internos',
    'por dentro',
}
_RESTRICTED_DOC_STOPWORDS = {
    *_STOPWORDS,
    'interna',
    'internas',
    'interno',
    'internos',
    'segundo',
    'diz',
    'orienta',
    'orientam',
    'sobre',
}
_RESTRICTED_DOC_GENERIC_TERMS = {
    'aluno',
    'alunos',
    'ensino',
    'medio',
    'ano',
    'anos',
    'escola',
    'procedimento',
    'protocolo',
    'manual',
    'playbook',
    'interno',
    'interna',
    'internos',
    'orientacao',
    'orientação',
    'documento',
    'documentos',
    'existe',
    'algum',
    'alguma',
    'especifica',
    'específica',
}
_RESTRICTED_DOC_RARE_TERMS = {
    'telegram',
    'escopo',
    'avaliac',
    'professor',
    'negoci',
    'familia',
    'família',
    'hospedagem',
    'internacional',
    'excursao',
    'excursão',
    'viagem',
}


@dataclass(frozen=True)
class RetrievalQueryPlanSpec:
    intent: str
    profile: RetrievalProfile
    normalized_query: str
    query_variants: list[str]
    subqueries: list[str]
    graph_rag_candidate: bool
    category_bias: str | None
    canonical_lane: str | None
    candidate_pool_size: int
    lexical_limit: int
    vector_limit: int
    rerank_limit: int
    max_chunks_per_document: int


class RetrievalService:
    def __init__(
        self,
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
    ) -> None:
        self.database_url = database_url
        self.collection_name = collection_name
        self.embedding_model = embedding_model
        self.enable_query_variants = enable_query_variants
        self.enable_late_interaction_rerank = enable_late_interaction_rerank
        self.late_interaction_model = late_interaction_model
        self.candidate_pool_size = max(6, candidate_pool_size)
        self.cheap_candidate_pool_size = max(4, cheap_candidate_pool_size)
        self.deep_candidate_pool_size = max(self.candidate_pool_size, deep_candidate_pool_size)
        self.rerank_fused_weight = max(0.0, rerank_fused_weight)
        self.rerank_late_interaction_weight = max(0.0, rerank_late_interaction_weight)
        self.qdrant = QdrantClient(url=qdrant_url)
        self._embedder: TextEmbedding | None = None
        self._late_interaction_embedder: LateInteractionTextEmbedding | None = None

    @property
    def embedder(self) -> TextEmbedding:
        if self._embedder is None:
            self._embedder = _build_embedder(self.embedding_model)
        return self._embedder

    @property
    def late_interaction_embedder(self) -> LateInteractionTextEmbedding | None:
        if not self.enable_late_interaction_rerank or not self.late_interaction_model:
            return None
        if self._late_interaction_embedder is None:
            self._late_interaction_embedder = _build_late_interaction_embedder(self.late_interaction_model)
        return self._late_interaction_embedder

    def warm_components(self) -> None:
        with start_span(
            'eduassist.retrieval.warm_components',
            tracer_name='eduassist.ai_orchestrator.retrieval',
            **{
                'eduassist.retrieval.collection': self.collection_name,
                'eduassist.retrieval.reranker_enabled': self.enable_late_interaction_rerank,
            },
        ):
            next(self.embedder.embed(['warmup retrieval query']))
            reranker = self.late_interaction_embedder
            if reranker is not None:
                next(reranker.embed(['warmup query']))
                next(reranker.embed(['warmup document context']))

    def hybrid_search(
        self,
        *,
        query: str,
        top_k: int,
        visibility: str,
        category: str | None = None,
        profile: RetrievalProfile | None = None,
        parent_ref_keys: tuple[str, ...] | None = None,
    ) -> RetrievalSearchResponse:
        effective_visibility = _normalize_visibility_filter(visibility)
        effective_category = _normalize_category_filter(category)
        started_at = monotonic()
        query_plan = _build_query_plan(
            query=query,
            top_k=top_k,
            category=category,
            visibility=effective_visibility,
            enable_query_variants=self.enable_query_variants,
            candidate_pool_size=self.candidate_pool_size,
            cheap_candidate_pool_size=self.cheap_candidate_pool_size,
            deep_candidate_pool_size=self.deep_candidate_pool_size,
            profile_override=profile,
        )
        corrective_retry_applied = False
        with start_span(
            'eduassist.retrieval.hybrid_search',
            tracer_name='eduassist.ai_orchestrator.retrieval',
            **{
                'eduassist.retrieval.query_length': len(query),
                'eduassist.retrieval.top_k': top_k,
                'eduassist.retrieval.visibility': effective_visibility,
                'eduassist.retrieval.category': effective_category,
                'eduassist.retrieval.requested_visibility': visibility,
                'eduassist.retrieval.requested_category': category,
                'eduassist.retrieval.collection': self.collection_name,
                'eduassist.retrieval.intent': query_plan.intent,
                'eduassist.retrieval.graph_rag_candidate': query_plan.graph_rag_candidate,
                'eduassist.retrieval.variant_count': len(query_plan.query_variants),
                'eduassist.retrieval.subquery_count': len(query_plan.subqueries),
            },
        ):
            lexical_sources: dict[str, list[dict[str, Any]]] = {}
            vector_sources: dict[str, list[dict[str, Any]]] = {}

            lexical_variants = query_plan.query_variants[: min(3, len(query_plan.query_variants))]
            vector_variants = query_plan.query_variants[: min(2, len(query_plan.query_variants))]

            for index, variant in enumerate(lexical_variants):
                lexical_sources[f'lexical:{index}'] = self._lexical_search(
                    query=variant,
                    top_k=query_plan.lexical_limit,
                    visibility=effective_visibility,
                    category=effective_category,
                    parent_ref_keys=parent_ref_keys,
                )
            for index, variant in enumerate(vector_variants):
                vector_sources[f'vector:{index}'] = self._vector_search(
                    query=variant,
                    top_k=query_plan.vector_limit,
                    visibility=effective_visibility,
                    category=effective_category,
                    parent_ref_keys=parent_ref_keys,
                )
            for index, subquery in enumerate(query_plan.subqueries[:2]):
                lexical_sources[f'subquery:{index}:lexical'] = self._lexical_search(
                    query=subquery,
                    top_k=query_plan.lexical_limit,
                    visibility=effective_visibility,
                    category=effective_category,
                    parent_ref_keys=parent_ref_keys,
                )
                vector_sources[f'subquery:{index}:vector'] = self._vector_search(
                    query=subquery,
                    top_k=query_plan.vector_limit,
                    visibility=effective_visibility,
                    category=effective_category,
                    parent_ref_keys=parent_ref_keys,
                )

            fused_hits = self._fuse_hits(
                lexical_sources=lexical_sources,
                vector_sources=vector_sources,
                top_k=max(top_k, query_plan.rerank_limit),
                category_bias=query_plan.category_bias,
                max_chunks_per_document=query_plan.max_chunks_per_document,
                intent=query_plan.intent,
                normalized_query=query_plan.normalized_query,
            )
            reranked_hits, reranker_applied = self._rerank_hits(
                query=query,
                hits=fused_hits,
                rerank_limit=query_plan.rerank_limit,
                top_k=top_k,
            )
            document_groups = self._build_document_groups(
                reranked_hits,
                max_groups=max(top_k, 3),
            )
            uncovered_subqueries = _uncovered_subqueries(
                subqueries=query_plan.subqueries,
                hits=reranked_hits,
            )
            if uncovered_subqueries:
                corrective_retry_applied = True
                for index, subquery in enumerate(uncovered_subqueries[:2]):
                    retry_query = _corrective_retry_query(
                        subquery,
                        intent=query_plan.intent,
                    )
                    lexical_sources[f'corrective:{index}:lexical'] = self._lexical_search(
                        query=retry_query,
                        top_k=max(query_plan.lexical_limit, top_k * 4),
                        visibility=effective_visibility,
                        category=effective_category,
                        parent_ref_keys=parent_ref_keys,
                    )
                    vector_sources[f'corrective:{index}:vector'] = self._vector_search(
                        query=retry_query,
                        top_k=max(query_plan.vector_limit, top_k * 4),
                        visibility=effective_visibility,
                        category=effective_category,
                        parent_ref_keys=parent_ref_keys,
                    )
                fused_hits = self._fuse_hits(
                    lexical_sources=lexical_sources,
                    vector_sources=vector_sources,
                    top_k=max(top_k, query_plan.rerank_limit),
                    category_bias=query_plan.category_bias,
                    max_chunks_per_document=query_plan.max_chunks_per_document,
                    intent=query_plan.intent,
                    normalized_query=query_plan.normalized_query,
                )
                reranked_hits, reranker_applied = self._rerank_hits(
                    query=query,
                    hits=fused_hits,
                    rerank_limit=query_plan.rerank_limit,
                    top_k=top_k,
                )
                document_groups = self._build_document_groups(
                    reranked_hits,
                    max_groups=max(top_k, 3),
                )
            context_pack = self._build_context_pack(document_groups)

            set_span_attributes(
                **{
                    'eduassist.retrieval.lexical_sources': len(lexical_sources),
                    'eduassist.retrieval.vector_sources': len(vector_sources),
                    'eduassist.retrieval.fused_hits': len(fused_hits),
                    'eduassist.retrieval.reranked_hits': len(reranked_hits),
                    'eduassist.retrieval.backend': RetrievalBackend.qdrant_hybrid.value,
                    'eduassist.retrieval.reranker_applied': reranker_applied,
                    'eduassist.retrieval.profile': query_plan.profile.value,
                    'eduassist.retrieval.canonical_lane': query_plan.canonical_lane,
                    'eduassist.retrieval.corrective_retry_applied': corrective_retry_applied,
                }
            )
            metric_attributes = {
                'backend': RetrievalBackend.qdrant_hybrid.value,
                'visibility': effective_visibility,
                'category': effective_category or 'all',
                'intent': query_plan.intent,
                'profile': query_plan.profile.value,
                'reranker_applied': str(reranker_applied).lower(),
                'corrective_retry_applied': str(corrective_retry_applied).lower(),
            }
            record_counter(
                'eduassist_retrieval_requests',
                attributes=metric_attributes,
                description='Hybrid retrieval requests handled by the orchestrator.',
            )
            record_histogram(
                'eduassist_retrieval_latency_ms',
                (monotonic() - started_at) * 1000,
                attributes=metric_attributes,
                description='Hybrid retrieval latency in milliseconds.',
            )
            record_histogram(
                'eduassist_retrieval_fused_hits',
                len(reranked_hits),
                attributes=metric_attributes,
                description='Number of hits returned by the retrieval pipeline.',
            )
            return RetrievalSearchResponse(
                query=query,
                retrieval_backend=RetrievalBackend.qdrant_hybrid,
                total_hits=len(reranked_hits),
                hits=reranked_hits,
                document_groups=document_groups,
                query_plan=RetrievalQueryPlan(
                    intent=query_plan.intent,
                    profile=query_plan.profile,
                    normalized_query=query_plan.normalized_query,
                    query_variants=query_plan.query_variants,
                    subqueries=query_plan.subqueries,
                    graph_rag_candidate=query_plan.graph_rag_candidate,
                    reranker_applied=reranker_applied,
                    corrective_retry_applied=corrective_retry_applied,
                    reranker_model=self.late_interaction_model if reranker_applied else None,
                    category_bias=query_plan.category_bias,
                    canonical_lane=query_plan.canonical_lane,
                    candidate_pool_size=query_plan.candidate_pool_size,
                    lexical_limit=query_plan.lexical_limit,
                    vector_limit=query_plan.vector_limit,
                    rerank_limit=query_plan.rerank_limit,
                    max_chunks_per_document=query_plan.max_chunks_per_document,
                ),
                context_pack=context_pack,
            )

    def collection_status(self) -> dict[str, Any]:
        with start_span(
            'eduassist.retrieval.collection_status',
            tracer_name='eduassist.ai_orchestrator.retrieval',
            **{
                'eduassist.retrieval.collection': self.collection_name,
            },
        ):
            exists = self._collection_exists(self.collection_name)
            set_span_attributes(**{'eduassist.retrieval.collection_exists': exists})
            if not exists:
                return {'exists': False, 'collection': self.collection_name}

            collection = self.qdrant.get_collection(self.collection_name)
            vectors_config = None
            config = getattr(collection, 'config', None)
            if config is not None:
                params = getattr(config, 'params', None)
                if params is not None:
                    vectors_config = getattr(params, 'vectors', None)
            set_span_attributes(
                **{
                    'eduassist.retrieval.points_count': getattr(collection, 'points_count', None),
                    'eduassist.retrieval.indexed_vectors_count': getattr(collection, 'indexed_vectors_count', None),
                    'eduassist.retrieval.status': str(collection.status),
                }
            )
            return {
                'exists': True,
                'collection': self.collection_name,
                'points_count': getattr(collection, 'points_count', None),
                'indexed_vectors_count': getattr(collection, 'indexed_vectors_count', None),
                'vectors_config': str(vectors_config) if vectors_config is not None else None,
                'status': str(collection.status),
                'query_variants_enabled': self.enable_query_variants,
                'late_interaction_rerank_enabled': self.enable_late_interaction_rerank,
                'late_interaction_model': self.late_interaction_model,
                'candidate_pool_size': self.candidate_pool_size,
                'cheap_candidate_pool_size': self.cheap_candidate_pool_size,
                'deep_candidate_pool_size': self.deep_candidate_pool_size,
                'rerank_fused_weight': self.rerank_fused_weight,
                'rerank_late_interaction_weight': self.rerank_late_interaction_weight,
            }

    def _lexical_search(
        self,
        *,
        query: str,
        top_k: int,
        visibility: str,
        category: str | None,
        parent_ref_keys: tuple[str, ...] | None = None,
    ) -> list[dict[str, Any]]:
        with start_span(
            'eduassist.retrieval.lexical_search',
            tracer_name='eduassist.ai_orchestrator.retrieval',
            **{
                'eduassist.retrieval.top_k': top_k,
                'eduassist.retrieval.visibility': visibility,
                'eduassist.retrieval.category': category,
            },
        ):
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
            if parent_ref_keys:
                conditions.append(
                    """
                    exists (
                      select 1
                      from documents.retrieval_labels rl
                      where rl.document_chunk_id = chunk.id
                        and rl.label_type = 'parent_ref_key'
                        and rl.label_value = any(%(parent_ref_keys)s)
                    )
                    """.strip()
                )
                params['parent_ref_keys'] = list(parent_ref_keys)

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
                  coalesce(label_bucket.labels, '{{}}'::jsonb) as labels,
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
                left join lateral (
                  select jsonb_object_agg(label_type, values) as labels
                  from (
                    select label_type, array_agg(label_value order by label_value) as values
                    from documents.retrieval_labels
                    where document_chunk_id = chunk.id
                    group by label_type
                  ) grouped
                ) label_bucket on true
                where {' and '.join(conditions)}
                order by lexical_score desc, document.title asc, chunk.chunk_index asc
                limit %(top_k)s
            """

            with psycopg.connect(self.database_url, row_factory=dict_row) as connection:
                with connection.cursor() as cursor:
                    cursor.execute(sql, params)
                    rows = cursor.fetchall()

            set_span_attributes(**{'eduassist.retrieval.result_count': len(rows)})
            return [_enrich_hit_metadata(dict(row)) for row in rows]

    def _vector_search(
        self,
        *,
        query: str,
        top_k: int,
        visibility: str,
        category: str | None,
        parent_ref_keys: tuple[str, ...] | None = None,
    ) -> list[dict[str, Any]]:
        with start_span(
            'eduassist.retrieval.vector_search',
            tracer_name='eduassist.ai_orchestrator.retrieval',
            **{
                'eduassist.retrieval.top_k': top_k,
                'eduassist.retrieval.visibility': visibility,
                'eduassist.retrieval.category': category,
                'eduassist.retrieval.collection': self.collection_name,
            },
        ):
            if not self._collection_exists(self.collection_name):
                set_span_attributes(**{'eduassist.retrieval.collection_exists': False})
                return []

            set_span_attributes(**{'eduassist.retrieval.collection_exists': True})
            vector = next(self.embedder.embed([query])).tolist()
            must_filters = [
                models.FieldCondition(key='visibility', match=models.MatchValue(value=visibility)),
            ]
            if category:
                must_filters.append(models.FieldCondition(key='category', match=models.MatchValue(value=category)))
            if parent_ref_keys:
                must_filters.append(
                    models.FieldCondition(
                        key='parent_ref_key',
                        match=models.MatchAny(any=list(parent_ref_keys)),
                    )
                )

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
                    _enrich_hit_metadata(
                        {
                            'chunk_id': str(payload.get('chunk_id', point.id)),
                            'chunk_index': int(payload.get('chunk_index', 0)),
                            'text_content': str(payload.get('text_content', '')),
                            'contextual_summary': payload.get('contextual_summary'),
                            'document_title': str(payload.get('document_title', 'Documento sem titulo')),
                            'document_set_slug': payload.get('document_set_slug'),
                            'section_path': payload.get('section_path'),
                            'section_parent': payload.get('section_parent'),
                            'section_title': payload.get('section_title'),
                            'parent_ref_key': payload.get('parent_ref_key'),
                            'labels': payload.get('labels') or {},
                            'category': str(payload.get('category', 'unknown')),
                            'audience': str(payload.get('audience', 'publico')),
                            'visibility': str(payload.get('visibility', visibility)),
                            'version_label': str(payload.get('version_label', 'v0')),
                            'storage_path': str(payload.get('storage_path', '')),
                            'vector_score': float(point.score or 0.0),
                        }
                    )
                )
            set_span_attributes(**{'eduassist.retrieval.result_count': len(hits)})
            return hits

    def _collection_exists(self, collection_name: str) -> bool:
        try:
            self.qdrant.get_collection(collection_name)
            return True
        except Exception:
            return False

    def _fuse_hits(
        self,
        *,
        lexical_sources: dict[str, list[dict[str, Any]]],
        vector_sources: dict[str, list[dict[str, Any]]],
        top_k: int,
        category_bias: str | None,
        max_chunks_per_document: int,
        intent: str,
        normalized_query: str,
    ) -> list[RetrievalHit]:
        with start_span(
            'eduassist.retrieval.fuse_hits',
            tracer_name='eduassist.ai_orchestrator.retrieval',
            **{
                'eduassist.retrieval.lexical_sources': len(lexical_sources),
                'eduassist.retrieval.vector_sources': len(vector_sources),
                'eduassist.retrieval.top_k': top_k,
            },
        ):
            combined: dict[str, dict[str, Any]] = {}

            for source_name, hits in lexical_sources.items():
                for rank, hit in enumerate(hits, start=1):
                    item = combined.setdefault(hit['chunk_id'], dict(hit))
                    item['lexical_score'] = max(float(hit.get('lexical_score', 0.0)), float(item.get('lexical_score', 0.0) or 0.0))
                    item['rrf_score'] = item.get('rrf_score', 0.0) + _source_weight(source_name) * (1.0 / (RRF_K + rank))

            for source_name, hits in vector_sources.items():
                for rank, hit in enumerate(hits, start=1):
                    item = combined.setdefault(hit['chunk_id'], dict(hit))
                    item.setdefault('lexical_score', None)
                    item['vector_score'] = max(float(hit.get('vector_score', 0.0)), float(item.get('vector_score', 0.0) or 0.0))
                    item['rrf_score'] = item.get('rrf_score', 0.0) + _source_weight(source_name) * (1.0 / (RRF_K + rank))
                    for key, value in hit.items():
                        item.setdefault(key, value)

            category_bias_normalized = _normalize_text(category_bias or '')
            query_terms = set(_query_terms(normalized_query))
            ranked = sorted(
                combined.values(),
                key=lambda item: (
                    float(item.get('rrf_score', 0.0))
                    + _category_boost(item=item, category_bias=category_bias_normalized)
                    + _intent_alignment_boost(item=item, intent=intent)
                    + _section_alignment_boost(item=item, query_terms=query_terms),
                    float(item.get('vector_score', 0.0) or 0.0),
                    float(item.get('lexical_score', 0.0) or 0.0),
                ),
                reverse=True,
            )
            diversified = _document_diversified_hits(
                ranked=ranked,
                top_k=top_k,
                max_chunks_per_document=max_chunks_per_document,
            )

            set_span_attributes(**{'eduassist.retrieval.unique_hits': len(diversified)})
            return [
                RetrievalHit(
                    chunk_id=item['chunk_id'],
                    document_title=item['document_title'],
                    document_set_slug=item.get('document_set_slug'),
                    category=item['category'],
                    audience=item['audience'],
                    visibility=item['visibility'],
                    text_excerpt=self._excerpt(item.get('text_content', '')),
                    contextual_summary=item.get('contextual_summary'),
                    section_path=item.get('section_path'),
                    section_parent=item.get('section_parent'),
                    section_title=item.get('section_title'),
                    parent_ref_key=item.get('parent_ref_key'),
                    labels=_normalize_hit_labels(item.get('labels')),
                    fused_score=round(float(item.get('rrf_score', 0.0)), 6),
                    document_score=round(float(item.get('document_score', 0.0) or 0.0), 6),
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
                        section_path=item.get('section_path'),
                    ),
                )
                for item in diversified
            ]

    def _rerank_hits(
        self,
        *,
        query: str,
        hits: list[RetrievalHit],
        rerank_limit: int,
        top_k: int,
    ) -> tuple[list[RetrievalHit], bool]:
        if not self.enable_late_interaction_rerank or not self.late_interaction_model or not hits:
            return hits[:top_k], False
        try:
            reranker = self.late_interaction_embedder
            if reranker is None:
                return hits[:top_k], False
            query_embedding = np.asarray(next(reranker.embed([query])))
            rerank_candidates = hits[: min(rerank_limit, len(hits))]
            document_inputs = [
                _rerank_text_for_hit(hit)
                for hit in rerank_candidates
            ]
            document_embeddings = [np.asarray(item) for item in reranker.embed(document_inputs)]
            rerank_scores = [
                _late_interaction_maxsim(query_embedding, document_embedding)
                for document_embedding in document_embeddings
            ]
        except Exception:
            return hits[:top_k], False

        fused_weight, rerank_weight = _normalized_blend_weights(
            self.rerank_fused_weight,
            self.rerank_late_interaction_weight,
        )
        normalized_fused = _normalize_scores([hit.fused_score for hit in rerank_candidates])
        normalized_rerank = _normalize_scores(rerank_scores)
        rescored: list[tuple[float, RetrievalHit]] = []
        for hit, rerank_score, fused_score, rerank_component in zip(
            rerank_candidates,
            rerank_scores,
            normalized_fused,
            normalized_rerank,
            strict=True,
        ):
            combined_score = (fused_weight * fused_score) + (rerank_weight * rerank_component)
            rescored.append(
                (
                    combined_score,
                    hit.model_copy(
                        update={
                            'rerank_score': round(float(rerank_score), 6),
                            'document_score': round(max(float(hit.document_score or 0.0), combined_score), 6),
                        }
                    ),
                )
            )
        rescored.sort(key=lambda item: item[0], reverse=True)
        reranked_hits = [hit for _, hit in rescored]
        if len(hits) > len(rerank_candidates):
            reranked_hits.extend(hits[len(rerank_candidates):])
        return reranked_hits[:top_k], True

    def _build_document_groups(
        self,
        hits: list[RetrievalHit],
        *,
        max_groups: int = 4,
    ) -> list[RetrievalDocumentGroup]:
        if not hits:
            return []
        grouped: dict[str, list[RetrievalHit]] = {}
        for hit in hits:
            document_key = str(hit.citation.storage_path or hit.document_title or hit.chunk_id)
            grouped.setdefault(document_key, []).append(hit)

        groups: list[RetrievalDocumentGroup] = []
        for document_hits in grouped.values():
            ordered = sorted(
                document_hits,
                key=lambda hit: (
                    float(hit.document_score or 0.0),
                    float(hit.rerank_score or 0.0),
                    float(hit.fused_score or 0.0),
                ),
                reverse=True,
            )
            primary = ordered[0]
            section_titles = [
                section
                for section in dict.fromkeys(
                    section
                    for section in (
                        hit.section_title or hit.section_path or hit.contextual_summary
                        for hit in ordered
                    )
                    if section
                )
            ]
            groups.append(
                RetrievalDocumentGroup(
                    document_title=primary.document_title,
                    document_set_slug=primary.document_set_slug,
                    category=primary.category,
                    audience=primary.audience,
                    visibility=primary.visibility,
                    document_score=round(
                        max(float(primary.document_score or 0.0), float(primary.fused_score or 0.0)),
                        6,
                    ),
                    primary_excerpt=primary.text_excerpt,
                    primary_summary=primary.contextual_summary,
                    primary_section=primary.section_path or primary.section_title,
                    parent_ref_key=primary.parent_ref_key,
                    support_excerpt_count=max(0, len(ordered) - 1),
                    section_titles=section_titles[:4],
                    citation=primary.citation,
                )
            )
        groups.sort(key=lambda item: item.document_score, reverse=True)
        return groups[:max_groups]

    def _build_context_pack(
        self,
        document_groups: list[RetrievalDocumentGroup],
        *,
        max_hits: int = 4,
        max_chars: int = 2200,
    ) -> str | None:
        if not document_groups:
            return None
        sections: list[str] = []
        current_chars = 0
        for group in document_groups[:max_hits]:
            excerpt = str(group.primary_summary or group.primary_excerpt or '').strip()
            if not excerpt:
                continue
            section_label = group.primary_section or group.document_title
            section = f'[{group.document_title} | {section_label}] {excerpt}'
            projected = current_chars + len(section) + 2
            if projected > max_chars and sections:
                break
            sections.append(section[: max(0, max_chars - current_chars)])
            current_chars += len(section) + 2
        if not sections:
            return None
        return '\n\n'.join(sections)

    def _excerpt(self, text: str, max_chars: int = 280) -> str:
        clean = ' '.join(text.split())
        if len(clean) <= max_chars:
            return clean
        return f'{clean[: max_chars - 3].rstrip()}...'


def _normalize_text(value: str) -> str:
    text = unicodedata.normalize('NFKD', str(value or ''))
    text = ''.join(char for char in text if not unicodedata.combining(char))
    text = re.sub(r'\s+', ' ', text.lower()).strip()
    return text


def _query_terms(value: str) -> list[str]:
    normalized = _normalize_text(value)
    return [
        token
        for token in re.findall(r'[a-z0-9]{3,}', normalized)
        if token not in _STOPWORDS
    ]


def _keyword_variant(query: str) -> str | None:
    terms = _query_terms(query)
    if not terms:
        return None
    variant = ' '.join(terms[:10]).strip()
    normalized_variant = _normalize_text(variant)
    if not normalized_variant or normalized_variant == _normalize_text(query):
        return None
    return variant


def _cross_document_variants(query: str) -> list[str]:
    terms = set(_query_terms(query))
    variants: list[str] = []
    if {'rematricula', 'transferencia', 'cancelamento'} & terms:
        variants.append('rematricula transferencia cancelamento prazos documentos')
    if {'bolsas', 'bolsa', 'descontos', 'desconto', 'mensalidades', 'mensalidade'} & terms:
        variants.append('bolsas descontos mensalidades politica comercial admissions')
    if {'secretaria', 'portal', 'credenciais', 'login', 'senha', 'documentos', 'documentacao'} & terms:
        variants.append('secretaria portal credenciais login senha envio de documentos')
    if {'avaliacao', 'recuperacao', 'promocao', 'frequencia', 'faltas', 'segunda', 'chamada'} & terms:
        variants.append('avaliacao recuperacao promocao frequencia faltas segunda chamada regras')
    if {'familia', 'aluno', 'rotina', 'canais', 'servicos', 'servico'} & terms:
        variants.append('familia aluno rotina escolar canais servicos suporte')
    return _dedupe_strings(variants)


def _topic_families_for_query(query: str) -> list[str]:
    terms = set(_query_terms(query))
    normalized = _normalize_text(query)
    families: list[str] = []
    for family, markers in _TOPIC_FAMILIES.items():
        if markers & terms:
            families.append(family)
            continue
        if family == 'timeline' and any(
            phrase in normalized for phrase in ('entre matricula', 'antes das aulas', 'depois da matricula')
        ):
            families.append(family)
    return families


def _decompose_query_into_subqueries(
    query: str,
    *,
    intent: str,
    visibility: str,
) -> list[str]:
    if visibility != 'public':
        return []
    families = _topic_families_for_query(query)
    if len(families) <= 1 and intent not in {'corpus_overview', 'service_overview', 'admissions_lookup'}:
        return []
    hints: list[str] = []
    normalized = _normalize_text(query)
    for family in families:
        base = _TOPIC_QUERIES.get(family)
        if not base:
            continue
        if family == 'pricing':
            children_match = re.search(r'\b(\d+)\s+filh', normalized)
            if children_match:
                base = f'{base} {children_match.group(1)} filhos'
        hints.append(base)
    if intent in {'corpus_overview', 'service_overview'} and 'familia nova' in normalized:
        hints.append('familia nova acolhimento rotina canais portal e suporte')
    return _dedupe_strings(hints)


def _coverage_terms_for_subquery(subquery: str) -> list[str]:
    terms = [term for term in _query_terms(subquery) if len(term) >= 4]
    return terms[:4]


def _hit_haystack(hit: RetrievalHit) -> str:
    return _normalize_text(
        ' '.join(
            part
            for part in (
                hit.document_title,
                hit.contextual_summary or '',
                hit.text_excerpt or '',
                hit.section_title or '',
                hit.section_parent or '',
                hit.section_path or '',
            )
            if part
        )
    )


def _subquery_is_covered(subquery: str, hits: list[RetrievalHit]) -> bool:
    terms = _coverage_terms_for_subquery(subquery)
    if not terms:
        return True
    haystacks = [_hit_haystack(hit) for hit in hits[:6]]
    best_overlap = 0
    for haystack in haystacks:
        overlap = sum(1 for term in terms if term in haystack)
        best_overlap = max(best_overlap, overlap)
    if len(terms) <= 2:
        return best_overlap >= 1
    return best_overlap >= 2


def _uncovered_subqueries(*, subqueries: list[str], hits: list[RetrievalHit]) -> list[str]:
    return [subquery for subquery in subqueries if not _subquery_is_covered(subquery, hits)]


def _corrective_retry_query(subquery: str, *, intent: str) -> str:
    expansion = _INTENT_EXPANSIONS.get(intent, '')
    return ' '.join(part for part in (subquery, expansion) if part).strip()


def _has_synthesis_language(normalized: str, terms: set[str]) -> bool:
    if {
        'panorama',
        'visao',
        'compare',
        'comparacao',
        'comparativo',
        'diferenca',
        'diferencas',
        'diferenciais',
        'sintetize',
        'relacione',
        'cruze',
        'mapeie',
        'explique',
    } & terms:
        return True
    return any(
        phrase in normalized
        for phrase in (
            'visao geral',
            'proposta pedagogica',
            'uma unica explicacao coerente',
            'o que uma familia precisa entender',
            'temas atravessam varios documentos',
            'quando cruzamos',
            'do ponto de vista financeiro e administrativo',
            'guia de sobrevivencia do primeiro mes',
            'de ponta a ponta',
        )
    )


def _has_cross_document_scope(terms: set[str]) -> bool:
    admissions_terms = {
        'rematricula',
        'transferencia',
        'cancelamento',
        'admissao',
        'acolhimento',
        'entrevista',
        'bolsas',
        'bolsa',
        'descontos',
        'desconto',
        'mensalidades',
        'mensalidade',
    }
    policy_terms = {
        'avaliacao',
        'avaliacoes',
        'recuperacao',
        'promocao',
        'frequencia',
        'pontualidade',
        'saude',
        'medicacao',
        'emergencias',
        'segunda',
        'chamada',
    }
    service_terms = {
        'secretaria',
        'portal',
        'aplicativo',
        'credenciais',
        'login',
        'senha',
        'servicos',
        'servico',
        'atendimento',
        'telegram',
        'documentos',
        'documentacao',
    }
    institutional_terms = {
        'familia',
        'aluno',
        'alunos',
        'rotina',
        'escolar',
        'colegio',
        'escola',
        'acolhimento',
        'suporte',
        'apoio',
    }
    return bool(
        admissions_terms & terms
        or policy_terms & terms
        or service_terms & terms
        or institutional_terms & terms
    )


def _intent_for_query(query: str) -> str:
    normalized = _normalize_text(query)
    terms = set(_query_terms(query))
    if (
        any(
            phrase in normalized
            for phrase in (
                'guia de sobrevivencia do primeiro mes',
                'guia de sobrevivência do primeiro mês',
                'o que uma familia precisa entender',
                'o que uma família precisa entender',
                'quando cruzamos',
                'de ponta a ponta',
            )
        )
        and _has_cross_document_scope(terms)
    ):
        return 'corpus_overview'
    if _has_synthesis_language(normalized, terms) and _has_cross_document_scope(terms):
        return 'corpus_overview'
    if (
        {'panorama', 'visao', 'comparar', 'comparacao', 'comparativo', 'diferenca', 'diferenciais', 'sintetize', 'relacione', 'pilares', 'temas'} & terms
        or any(
            phrase in normalized
            for phrase in (
                'visao geral',
                'proposta pedagogica',
                'uma unica explicacao coerente',
                'o que uma familia precisa entender',
                'temas atravessam varios documentos',
                'quando cruzamos',
            )
        )
    ):
        return 'corpus_overview'
    if {'mensalidade', 'matricula', 'desconto', 'bolsa', 'valor', 'preco', 'precos'} & terms:
        return 'pricing_lookup'
    if {'avaliacao', 'avaliacoes', 'recuperacao', 'promocao', 'frequencia', 'pontualidade', 'saude', 'medicacao', 'emergencias', 'segunda', 'chamada'} & terms:
        return 'policy_lookup'
    if {'rematricula', 'transferencia', 'cancelamento', 'admissao', 'acolhimento', 'entrevista'} & terms:
        return 'admissions_lookup'
    if {'calendario', 'aulas', 'reuniao', 'formatura', 'datas', 'quando'} & terms:
        return 'timeline_lookup'
    if {'documentacao', 'documentos', 'documento', 'portal', 'secretaria', 'email'} & terms:
        return 'document_lookup'
    if {'credenciais', 'senha', 'login', 'aplicativo', 'app', 'servicos', 'servico', 'atendimento'} & terms:
        return 'service_overview'
    if {'telefone', 'whatsapp', 'instagram', 'endereco', 'cidade', 'estado', 'cep', 'contato'} & terms or 'onde fica' in normalized:
        return 'contact_lookup'
    return 'fact_lookup'


def _category_bias_for_query(query: str, *, category: str | None, intent: str) -> str | None:
    if category:
        return category
    normalized = _normalize_text(query)
    if intent == 'timeline_lookup':
        return 'calendar'
    if intent == 'pricing_lookup':
        return 'admissions'
    if intent == 'admissions_lookup':
        return 'admissions'
    if intent == 'document_lookup':
        return 'secretaria'
    if intent == 'contact_lookup':
        return 'services'
    if intent == 'policy_lookup':
        return 'policy'
    if intent == 'service_overview':
        if any(term in normalized for term in ('portal', 'aplicativo', 'senha', 'login', 'credenciais')):
            return 'technology'
        if any(term in normalized for term in ('secretaria', 'documentos', 'declaracoes', 'declaracoes', 'cadastro')):
            return 'secretaria'
        return 'services'
    if intent == 'corpus_overview':
        return 'institutional'
    return None


def _graph_rag_candidate(query: str, *, intent: str) -> bool:
    normalized = _normalize_text(query)
    if intent in {'corpus_overview', 'policy_lookup', 'service_overview', 'admissions_lookup'}:
        return any(
            phrase in normalized
            for phrase in (
                'visao geral',
                'panorama',
                'compare',
                'comparacao',
                'comparativo',
                'diferenciais',
                'proposta pedagogica',
                'sintetize',
                'relacione',
                'uma unica explicacao coerente',
                'temas atravessam varios documentos',
                'o que uma familia precisa entender',
                'o que uma família precisa entender',
                'quando cruzamos',
                'do ponto de vista financeiro e administrativo',
                'do ponto de vista de uma familia nova',
                'do ponto de vista de uma família nova',
                'guia de sobrevivencia do primeiro mes',
                'guia de sobrevivência do primeiro mês',
                'primeiro mes',
                'primeiro mês',
                'regras e prazos',
                'muito esquecido',
                'de ponta a ponta',
                'o que muda',
                'destacando o que muda',
            )
        )
    return False


def _select_retrieval_profile(
    *,
    intent: str,
    visibility: str,
    top_k: int,
    canonical_lane: str | None,
    profile_override: RetrievalProfile | None,
) -> RetrievalProfile:
    if profile_override is not None:
        return profile_override
    if canonical_lane:
        return RetrievalProfile.cheap
    if visibility != 'public':
        return RetrievalProfile.deep
    if intent == 'corpus_overview':
        return RetrievalProfile.deep
    if intent == 'policy_lookup':
        return RetrievalProfile.default
    if intent in {'contact_lookup', 'timeline_lookup', 'pricing_lookup'} and top_k <= 4:
        return RetrievalProfile.cheap
    return RetrievalProfile.default


def _build_query_plan(
    *,
    query: str,
    top_k: int,
    category: str | None,
    visibility: str,
    enable_query_variants: bool,
    candidate_pool_size: int,
    cheap_candidate_pool_size: int,
    deep_candidate_pool_size: int,
    profile_override: RetrievalProfile | None,
) -> RetrievalQueryPlanSpec:
    intent = _intent_for_query(query)
    normalized_query = _normalize_text(query)
    canonical_lane = match_public_canonical_lane(query) if visibility == 'public' else None
    subqueries = _decompose_query_into_subqueries(
        query,
        intent=intent,
        visibility=visibility,
    )
    keyword_variant = _keyword_variant(query) if enable_query_variants else None
    variants = [query]
    if keyword_variant:
        variants.append(keyword_variant)
    if enable_query_variants:
        variants.extend(subqueries)
    expansion = _INTENT_EXPANSIONS.get(intent)
    if enable_query_variants and expansion:
        variants.append(f'{query} {expansion}'.strip())
    if enable_query_variants and intent in {'corpus_overview', 'policy_lookup', 'admissions_lookup', 'service_overview'}:
        variants.extend(_cross_document_variants(query))
    deduped_variants = _dedupe_strings(variants)
    profile = _select_retrieval_profile(
        intent=intent,
        visibility=visibility,
        top_k=top_k,
        canonical_lane=canonical_lane,
        profile_override=profile_override,
    )
    plan_pool_size = candidate_pool_size
    lexical_limit = max(top_k * 3, candidate_pool_size)
    vector_limit = max(top_k * 3, candidate_pool_size)
    rerank_limit = max(top_k * 2, min(candidate_pool_size, 10))
    max_chunks_per_document = 2
    if profile is RetrievalProfile.cheap:
        plan_pool_size = cheap_candidate_pool_size
        lexical_limit = max(top_k * 2, cheap_candidate_pool_size)
        vector_limit = max(top_k * 2, cheap_candidate_pool_size)
        rerank_limit = max(top_k, min(cheap_candidate_pool_size, 6))
        max_chunks_per_document = 1
    elif profile is RetrievalProfile.deep:
        plan_pool_size = deep_candidate_pool_size
        lexical_limit = max(top_k * 4, deep_candidate_pool_size)
        vector_limit = max(top_k * 4, deep_candidate_pool_size)
        rerank_limit = max(top_k * 3, min(deep_candidate_pool_size, 14))
        max_chunks_per_document = 1
    elif intent in {'corpus_overview', 'policy_lookup', 'service_overview'}:
        lexical_limit = max(top_k * 4, candidate_pool_size)
        vector_limit = max(top_k * 4, candidate_pool_size)
        rerank_limit = max(top_k * 3, min(candidate_pool_size, 12))
        max_chunks_per_document = 1
    return RetrievalQueryPlanSpec(
        intent=intent,
        profile=profile,
        normalized_query=normalized_query,
        query_variants=deduped_variants,
        subqueries=subqueries,
        graph_rag_candidate=_graph_rag_candidate(query, intent=intent),
        category_bias=_category_bias_for_query(query, category=category, intent=intent),
        canonical_lane=canonical_lane,
        candidate_pool_size=plan_pool_size,
        lexical_limit=lexical_limit,
        vector_limit=vector_limit,
        rerank_limit=rerank_limit,
        max_chunks_per_document=max_chunks_per_document,
    )


def _dedupe_strings(values: list[str]) -> list[str]:
    seen: set[str] = set()
    deduped: list[str] = []
    for value in values:
        text = str(value or '').strip()
        if not text:
            continue
        normalized = _normalize_text(text)
        if normalized in seen:
            continue
        seen.add(normalized)
        deduped.append(text)
    return deduped


def _source_weight(source_name: str) -> float:
    if source_name.startswith('vector:0'):
        return 1.2
    if source_name.startswith('lexical:0'):
        return 1.0
    if source_name.startswith('vector:'):
        return 0.95
    if source_name.startswith('lexical:'):
        return 0.85
    return 1.0


def _category_boost(*, item: dict[str, Any], category_bias: str) -> float:
    if not category_bias:
        return 0.0
    item_category = _normalize_text(str(item.get('category', '') or ''))
    if not item_category:
        return 0.0
    if category_bias in item_category:
        return 0.01
    return 0.0


def _intent_alignment_boost(*, item: dict[str, Any], intent: str) -> float:
    haystack = _normalize_text(
        ' '.join(
            part
            for part in (
                str(item.get('document_title', '') or ''),
                str(item.get('contextual_summary', '') or ''),
                str(item.get('text_content', '') or ''),
            )
            if part
        )
    )
    if not haystack:
        return 0.0
    if intent == 'contact_lookup':
        score = 0.0
        if 'endereco' in haystack:
            score += 0.03
        if any(term in haystack for term in ('cidade', 'estado', 'cep', 'sao paulo')):
            score += 0.015
        return score
    if intent == 'document_lookup':
        return 0.03 if any(term in haystack for term in ('documentacao', 'documentos', 'matricula', 'portal', 'secretaria', 'email')) else 0.0
    if intent == 'timeline_lookup':
        return 0.03 if any(term in haystack for term in ('aulas', 'reuniao', 'formatura', 'matricula', 'calendario')) else 0.0
    if intent == 'pricing_lookup':
        return 0.03 if any(term in haystack for term in ('mensalidade', 'matricula', 'desconto', 'bolsa', 'segmento')) else 0.0
    if intent == 'corpus_overview':
        return 0.03 if any(term in haystack for term in ('proposta pedagogica', 'projeto de vida', 'diferenciais', 'acompanhamento', 'cultura digital')) else 0.0
    return 0.0


def _normalize_scores(values: list[float]) -> list[float]:
    if not values:
        return []
    minimum = min(values)
    maximum = max(values)
    if maximum - minimum <= 1e-9:
        return [1.0 for _ in values]
    return [(value - minimum) / (maximum - minimum) for value in values]


def _normalized_blend_weights(fused_weight: float, rerank_weight: float) -> tuple[float, float]:
    total = fused_weight + rerank_weight
    if total <= 1e-9:
        return 0.4, 0.6
    return fused_weight / total, rerank_weight / total


def _section_metadata_from_summary(summary: str | None, *, fallback_title: str) -> tuple[str | None, str | None, str | None]:
    normalized = str(summary or '').strip()
    if not normalized:
        if not fallback_title:
            return None, None, None
        return fallback_title, None, fallback_title
    parts = [part.strip() for part in normalized.split('>') if part.strip()]
    if not parts:
        return normalized, None, normalized
    section_path = ' > '.join(parts)
    section_parent = parts[-2] if len(parts) >= 2 else None
    section_title = parts[-1]
    return section_path, section_parent, section_title


def _parent_ref_key_from_hit(hit: dict[str, Any]) -> str | None:
    explicit = str(hit.get('parent_ref_key') or '').strip()
    if explicit:
        return explicit
    storage_path = str(hit.get('storage_path') or '').strip()
    document_title = str(hit.get('document_title') or '').strip()
    section_anchor = (
        str(hit.get('section_parent') or '').strip()
        or str(hit.get('section_path') or '').strip()
        or str(hit.get('section_title') or '').strip()
        or document_title
    )
    base = storage_path or document_title
    if not base or not section_anchor:
        return None
    return f'{base}::{section_anchor}'


def _enrich_hit_metadata(hit: dict[str, Any]) -> dict[str, Any]:
    section_path, section_parent, section_title = _section_metadata_from_summary(
        hit.get('section_path') or hit.get('contextual_summary'),
        fallback_title=str(hit.get('document_title') or ''),
    )
    enriched = dict(hit)
    enriched['section_path'] = section_path
    enriched['section_parent'] = hit.get('section_parent') or section_parent
    enriched['section_title'] = hit.get('section_title') or section_title
    enriched['parent_ref_key'] = _parent_ref_key_from_hit(
        {
            **hit,
            'section_path': section_path,
            'section_parent': hit.get('section_parent') or section_parent,
            'section_title': hit.get('section_title') or section_title,
        }
    )
    enriched['labels'] = _normalize_hit_labels(hit.get('labels'))
    return enriched


def _normalize_hit_labels(value: Any) -> dict[str, list[str]]:
    if not isinstance(value, dict):
        return {}
    normalized: dict[str, list[str]] = {}
    for key, items in value.items():
        key_text = str(key or '').strip()
        if not key_text:
            continue
        if isinstance(items, list):
            values = [str(item).strip() for item in items if str(item or '').strip()]
        else:
            values = [str(items).strip()] if str(items or '').strip() else []
        if values:
            normalized[key_text] = values
    return normalized


def looks_like_restricted_document_query(message: str) -> bool:
    normalized = _normalize_text(message)
    return any(term in normalized for term in _RESTRICTED_DOC_QUERY_TERMS)


def can_read_restricted_documents(user: UserContext) -> bool:
    role = str(getattr(user.role, 'value', user.role) or '').strip().lower()
    scopes = {str(item).strip().lower() for item in getattr(user, 'scopes', [])}
    return bool(
        getattr(user, 'authenticated', False)
        and (
            'documents:private:read' in scopes
            or 'documents:restricted:read' in scopes
            or role in {'staff', 'teacher'}
        )
    )


def select_relevant_restricted_hits(query: str, hits: list[Any], *, max_hits: int = 3) -> list[Any]:
    if not hits:
        return []
    scored: list[tuple[float, int, Any]] = []
    for index, hit in enumerate(hits):
        score = _restricted_document_hit_score(query=query, hit=hit)
        if score > 0.18:
            scored.append((score, index, hit))
    if not scored:
        return []
    scored.sort(key=lambda item: (item[0], -item[1]), reverse=True)
    selected: list[Any] = []
    seen_titles: set[str] = set()
    for _, _, hit in scored:
        title = _normalize_text(_hit_value(hit, 'document_title'))
        title_key = title or _normalize_text(_hit_value(hit, 'chunk_id'))
        if title_key in seen_titles:
            continue
        selected.append(hit)
        seen_titles.add(title_key)
        if len(selected) >= max_hits:
            break
    return selected


def compose_restricted_document_grounded_answer(hits: list[Any]) -> str | None:
    if not hits:
        return None
    primary = hits[0]
    primary_title = str(_hit_value(primary, 'document_title') or 'documento interno').strip()
    primary_excerpt = str(
        _hit_value(primary, 'text_excerpt')
        or _hit_value(primary, 'contextual_summary')
        or ''
    ).strip()
    primary_section = ' - '.join(
        str(part).strip()
        for part in (
            _hit_value(primary, 'section_parent'),
            _hit_value(primary, 'section_title'),
        )
        if str(part or '').strip()
    )
    lines = [f"Nos documentos internos consultados, a orientacao mais relevante aparece em {primary_title}:"]
    if primary_section:
        lines.append(f"Secao relevante: {primary_section}.")
    if primary_excerpt:
        lines.append(primary_excerpt)
    seen_titles = {primary_title}
    for hit in hits[1:3]:
        title = str(_hit_value(hit, 'document_title') or '').strip()
        excerpt = str(_hit_value(hit, 'text_excerpt') or _hit_value(hit, 'contextual_summary') or '').strip()
        section = ' - '.join(
            str(part).strip()
            for part in (
                _hit_value(hit, 'section_parent'),
                _hit_value(hit, 'section_title'),
            )
            if str(part or '').strip()
        )
        if not excerpt:
            continue
        label = title if title and title not in seen_titles else 'Complemento interno'
        if section:
            lines.append(f"{label} ({section}): {excerpt}")
        else:
            lines.append(f"{label}: {excerpt}")
        if title:
            seen_titles.add(title)
    return '\n'.join(lines)


def compose_restricted_document_grounded_answer_for_query(query: str, hits: list[Any]) -> str | None:
    base = compose_restricted_document_grounded_answer(hits)
    if not base:
        return None
    normalized = _normalize_text(query)
    if 'professor' in normalized and 'avaliac' in normalized:
        return (
            'Para o pedido sobre o manual interno do professor, o trecho mais relevante sobre '
            'registro de avaliacoes e comunicacao pedagogica e este:\n'
            f'{base}'
        )
    if 'telegram' in normalized and 'escopo' in normalized:
        return (
            'Para o pedido sobre limites de acesso no Telegram para responsaveis com escopo parcial, '
            'o protocolo interno mais relevante e este:\n'
            f'{base}'
        )
    if ('negoci' in normalized or 'financeir' in normalized) and ('familia' in normalized or 'família' in normalized):
        return (
            'Para o pedido sobre o playbook interno de negociacao financeira com a familia, '
            'a orientacao mais relevante e esta:\n'
            f'{base}'
        )
    return base


def compose_restricted_document_no_match_answer(query: str) -> str:
    normalized_query = str(query or '').strip().rstrip(' ?!.')
    normalized = _normalize_text(normalized_query)
    if ('segunda chamada' in normalized or 'motivo de saude' in normalized or 'motivo de saúde' in normalized) and any(
        term in normalized for term in ('procedimento interno', 'orientacao interna', 'orientação interna', 'equipe', 'o que cabe ao publico', 'o que cabe ao público')
    ):
        return (
            'Consultei os documentos internos disponiveis, mas nao encontrei um procedimento interno adicional especifico para esse recorte. '
            'No que fica publico, a escola explica segunda chamada por motivo de saude no material aberto; o que cabe a equipe internamente segue como rotina restrita e nao apareceu com detalhe suficiente nesta base.'
        )
    if 'escopo parcial' in normalized or 'responsaveis com escopo parcial' in normalized or 'responsáveis com escopo parcial' in normalized:
        return (
            'Consultei os documentos internos disponiveis, mas nao encontrei um protocolo interno compartilhavel para responsaveis com escopo parcial. '
            'No que e publico, a diferenca principal e esta: a base aberta explica apenas orientacoes gerais, enquanto regras operacionais de permissao, restricao e encaminhamento continuam internas. '
            'Na pratica, o proximo passo e pedir ao setor responsavel que confirme o procedimento aplicavel ao perfil autorizado.'
        )
    if (
        any(term in normalized for term in ('viagem internacional', 'excursao internacional', 'excursão internacional'))
        and any(term in normalized for term in ('hospedagem', 'pernoite'))
    ):
        return (
            'Nao encontrei uma orientacao restrita especifica sobre excursao ou viagem internacional com hospedagem para o ensino medio nos documentos internos disponiveis. '
            'Na pratica, o proximo passo e consultar o setor responsavel por esse protocolo interno ou eu posso trazer apenas o correspondente publico.'
        )
    if ('negoci' in normalized or 'financeir' in normalized) and ('familia' in normalized or 'família' in normalized):
        return (
            'Consultei os documentos internos disponiveis, mas nao encontrei um criterio interno especifico '
            'de negociacao financeira com a familia para esse recorte. '
            'Na pratica, o proximo passo e validar essa orientacao com o financeiro responsavel.'
        )
    return (
        'Consultei os documentos internos disponiveis, mas nao encontrei uma orientacao restrita '
        f'especifica para: "{normalized_query}". '
        'Na pratica, esta base nao trouxe detalhe interno suficiente para responder com seguranca; '
        'o proximo passo e consultar o setor responsavel ou pedir apenas o material publico correspondente.'
    )


def _hit_value(hit: Any, field_name: str) -> Any:
    if isinstance(hit, dict):
        return hit.get(field_name)
    return getattr(hit, field_name, None)


def _restricted_document_query_terms(query: str) -> list[str]:
    normalized = _normalize_text(query)
    return [
        token
        for token in re.findall(r'[a-z0-9]{3,}', normalized)
        if token not in _RESTRICTED_DOC_STOPWORDS
    ]


def _restricted_document_anchor_terms(query: str) -> set[str]:
    return {
        token
        for token in _restricted_document_query_terms(query)
        if token not in _RESTRICTED_DOC_GENERIC_TERMS
    }


def _restricted_document_rare_terms(query: str) -> set[str]:
    return {
        token
        for token in _restricted_document_query_terms(query)
        if any(token.startswith(marker) or marker.startswith(token) for marker in _RESTRICTED_DOC_RARE_TERMS)
    }


def _restricted_document_hit_score(*, query: str, hit: Any) -> float:
    query_terms = set(_restricted_document_query_terms(query))
    if not query_terms:
        return 0.0
    title = _normalize_text(_hit_value(hit, 'document_title'))
    summary = _normalize_text(_hit_value(hit, 'contextual_summary'))
    excerpt = _normalize_text(_hit_value(hit, 'text_excerpt'))
    section = _normalize_text(
        ' '.join(
            part
            for part in (
                _hit_value(hit, 'section_title'),
                _hit_value(hit, 'section_parent'),
                _hit_value(hit, 'section_path'),
                _hit_value(hit, 'category'),
                _hit_value(hit, 'document_set_slug'),
            )
            if part
        )
    )
    label_terms = ' '.join(
        value
        for values in _normalize_hit_labels(_hit_value(hit, 'labels')).values()
        for value in values
    )
    label_haystack = _normalize_text(label_terms)
    title_terms = {token for token in re.findall(r'[a-z0-9]{3,}', title) if token not in _RESTRICTED_DOC_STOPWORDS}
    title_overlap = len(query_terms & title_terms)
    haystack = ' '.join(part for part in (summary, excerpt, section, label_haystack) if part)
    anchor_terms = _restricted_document_anchor_terms(query)
    if anchor_terms and not any(term in title or term in haystack for term in anchor_terms):
        return 0.0
    rare_terms = _restricted_document_rare_terms(query)
    if rare_terms and not any(term in title or term in haystack for term in rare_terms):
        return 0.0
    evidence_overlap = sum(1 for term in query_terms if term in haystack)
    score = 0.0
    if title and title in _normalize_text(query):
        score += 1.2
    elif title_terms:
        score += min(0.8, 0.3 * (title_overlap / max(1, len(title_terms))) + 0.2 * title_overlap)
    if evidence_overlap:
        score += min(0.7, 0.18 * evidence_overlap)
    if 'telegram' in query_terms and 'telegram' in haystack:
        score += 0.2
    if 'professor' in query_terms and 'professor' in title:
        score += 0.2
    if 'financeira' in query_terms or 'financeiro' in query_terms:
        if any(term in haystack for term in ('finance', 'inadimplencia', 'negociacao', 'negociacao financeira')):
            score += 0.2
    if any(term.startswith('avaliac') for term in query_terms) and 'avaliac' in haystack:
        score += 0.25
    if 'escopo' in query_terms and 'escopo' in haystack:
        score += 0.25
    if any(term in query_terms for term in {'telegram', 'hospedagem', 'internacional', 'excursao', 'viagem'}):
        score += 0.35 * sum(
            1
            for term in {'telegram', 'hospedagem', 'internacional', 'excursao', 'viagem'}
            if term in query_terms and term in haystack
        )
    retrieval_score = float(
        _hit_value(hit, 'document_score')
        or _hit_value(hit, 'rerank_score')
        or _hit_value(hit, 'fused_score')
        or 0.0
    )
    score += min(0.2, max(0.0, retrieval_score))
    return round(score, 6)


def _section_alignment_boost(*, item: dict[str, Any], query_terms: set[str]) -> float:
    if not query_terms:
        return 0.0
    section_haystack = _normalize_text(
        ' '.join(
            part
            for part in (
                str(item.get('section_title', '') or ''),
                str(item.get('section_parent', '') or ''),
                str(item.get('section_path', '') or ''),
            )
            if part
        )
    )
    if not section_haystack:
        return 0.0
    matched = sum(1 for term in query_terms if term in section_haystack)
    if matched <= 0:
        return 0.0
    return min(0.02, 0.005 * matched)


def _document_key_for_item(item: dict[str, Any]) -> str:
    return str(item.get('storage_path', '') or item.get('document_title', '') or item['chunk_id'])


def _document_diversified_hits(
    *,
    ranked: list[dict[str, Any]],
    top_k: int,
    max_chunks_per_document: int,
) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for item in ranked:
        grouped.setdefault(_document_key_for_item(item), []).append(item)

    document_scores: list[tuple[float, str]] = []
    for document_key, items in grouped.items():
        unique_sections = {
            str(item.get('section_path') or item.get('section_title') or item.get('contextual_summary') or '').strip()
            for item in items
            if str(item.get('section_path') or item.get('section_title') or item.get('contextual_summary') or '').strip()
        }
        score = max(float(item.get('rrf_score', 0.0)) for item in items)
        score += 0.01 * min(len(items), 3)
        score += 0.005 * min(len(unique_sections), 2)
        for item in items:
            item['document_score'] = score
        document_scores.append((score, document_key))

    document_scores.sort(reverse=True)
    diversified: list[dict[str, Any]] = []
    for _score, document_key in document_scores:
        for item in grouped[document_key][:max_chunks_per_document]:
            diversified.append(item)
            if len(diversified) >= top_k:
                return diversified
    return diversified


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


def _normalize_visibility_filter(value: str) -> str:
    normalized = _normalize_text(value)
    if normalized in {'private', 'restricted', 'internal'}:
        return 'restricted'
    return 'public'


def _normalize_category_filter(category: str | None) -> str | None:
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
) -> RetrievalService:
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
    )


def _build_embedder(model_name: str) -> TextEmbedding:
    try:
        return TextEmbedding(model_name=model_name)
    except Exception as exc:
        message = str(exc)
        if 'NO_SUCHFILE' not in message and "File doesn't exist" not in message:
            raise
        clear_fastembed_cache()
        return TextEmbedding(model_name=model_name)


def _build_late_interaction_embedder(model_name: str) -> LateInteractionTextEmbedding:
    try:
        return LateInteractionTextEmbedding(model_name=model_name)
    except Exception as exc:
        message = str(exc)
        if 'NO_SUCHFILE' not in message and "File doesn't exist" not in message:
            raise
        clear_fastembed_cache()
        return LateInteractionTextEmbedding(model_name=model_name)
