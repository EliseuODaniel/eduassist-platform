from __future__ import annotations

"""Hybrid retrieval search helpers extracted from local_retrieval.py."""

LOCAL_EXTRACTED_NAMES = {'hybrid_search_impl', 'lexical_search_impl', 'fuse_hits_impl'}

from . import local_retrieval as _native
from .extracted_module_contracts import refresh_extracted_module_contract
from .local_retrieval_search_contract import LOCAL_RETRIEVAL_SEARCH_CONTRACT

def _refresh_native_namespace() -> None:
    refresh_extracted_module_contract(
        native_module=_native,
        namespace=globals(),
        contract_names=LOCAL_RETRIEVAL_SEARCH_CONTRACT,
        local_extracted_names=LOCAL_EXTRACTED_NAMES,
        contract_label='local_retrieval_search_runtime',
    )

def hybrid_search_impl(
    service,
    *,
    query: str,
    top_k: int,
    visibility: str,
    category: str | None = None,
    profile: RetrievalProfile | None = None,
    parent_ref_keys: tuple[str, ...] | None = None,
) -> RetrievalSearchResponse:
    _refresh_native_namespace()
    effective_visibility = _normalize_visibility_filter(visibility)
    effective_category = _normalize_category_filter(category)
    started_at = monotonic()
    query_plan = _build_query_plan(
        query=query,
        top_k=top_k,
        category=category,
        visibility=effective_visibility,
        enable_query_variants=service.enable_query_variants,
        candidate_pool_size=service.candidate_pool_size,
        cheap_candidate_pool_size=service.cheap_candidate_pool_size,
        deep_candidate_pool_size=service.deep_candidate_pool_size,
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
            'eduassist.retrieval.collection': service.collection_name,
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
            lexical_sources[f'lexical:{index}'] = service._lexical_search(
                query=variant,
                top_k=query_plan.lexical_limit,
                visibility=effective_visibility,
                category=effective_category,
                parent_ref_keys=parent_ref_keys,
            )
        for index, variant in enumerate(vector_variants):
            vector_sources[f'vector:{index}'] = service._vector_search(
                query=variant,
                top_k=query_plan.vector_limit,
                visibility=effective_visibility,
                category=effective_category,
                parent_ref_keys=parent_ref_keys,
            )
        for index, subquery in enumerate(query_plan.subqueries[:2]):
            lexical_sources[f'subquery:{index}:lexical'] = service._lexical_search(
                query=subquery,
                top_k=query_plan.lexical_limit,
                visibility=effective_visibility,
                category=effective_category,
                parent_ref_keys=parent_ref_keys,
            )
            vector_sources[f'subquery:{index}:vector'] = service._vector_search(
                query=subquery,
                top_k=query_plan.vector_limit,
                visibility=effective_visibility,
                category=effective_category,
                parent_ref_keys=parent_ref_keys,
            )

        fused_hits = service._fuse_hits(
            lexical_sources=lexical_sources,
            vector_sources=vector_sources,
            top_k=max(top_k, query_plan.rerank_limit),
            category_bias=query_plan.category_bias,
            max_chunks_per_document=query_plan.max_chunks_per_document,
            intent=query_plan.intent,
            normalized_query=query_plan.normalized_query,
        )
        reranked_hits, reranker_applied = service._rerank_hits(
            query=query,
            hits=fused_hits,
            rerank_limit=query_plan.rerank_limit,
            top_k=top_k,
        )
        document_groups = service._build_document_groups(
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
                lexical_sources[f'corrective:{index}:lexical'] = service._lexical_search(
                    query=retry_query,
                    top_k=max(query_plan.lexical_limit, top_k * 4),
                    visibility=effective_visibility,
                    category=effective_category,
                    parent_ref_keys=parent_ref_keys,
                )
                vector_sources[f'corrective:{index}:vector'] = service._vector_search(
                    query=retry_query,
                    top_k=max(query_plan.vector_limit, top_k * 4),
                    visibility=effective_visibility,
                    category=effective_category,
                    parent_ref_keys=parent_ref_keys,
                )
            fused_hits = service._fuse_hits(
                lexical_sources=lexical_sources,
                vector_sources=vector_sources,
                top_k=max(top_k, query_plan.rerank_limit),
                category_bias=query_plan.category_bias,
                max_chunks_per_document=query_plan.max_chunks_per_document,
                intent=query_plan.intent,
                normalized_query=query_plan.normalized_query,
            )
            reranked_hits, reranker_applied = service._rerank_hits(
                query=query,
                hits=fused_hits,
                rerank_limit=query_plan.rerank_limit,
                top_k=top_k,
            )
            document_groups = service._build_document_groups(
                reranked_hits,
                max_groups=max(top_k, 3),
            )
        subquery_coverage = _subquery_coverage_map(
            subqueries=query_plan.subqueries,
            hits=reranked_hits,
        )
        uncovered_subqueries_final = [
            subquery
            for subquery, coverage in subquery_coverage.items()
            if coverage < 0.5
        ]
        coverage_ratio = (
            round(
                sum(subquery_coverage.values()) / max(1, len(subquery_coverage)),
                3,
            )
            if subquery_coverage
            else 1.0
        )
        citation_first_recommended = _should_recommend_citation_first(
            intent=query_plan.intent,
            subqueries=query_plan.subqueries,
            coverage_ratio=coverage_ratio,
            document_groups=document_groups,
        )
        context_pack = service._build_context_pack(document_groups)

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
                'eduassist.retrieval.coverage_ratio': coverage_ratio,
                'eduassist.retrieval.citation_first_recommended': citation_first_recommended,
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
            'citation_first_recommended': str(citation_first_recommended).lower(),
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
                subquery_coverage=subquery_coverage,
                uncovered_subqueries_final=uncovered_subqueries_final,
                coverage_ratio=coverage_ratio,
                citation_first_recommended=citation_first_recommended,
                graph_rag_candidate=query_plan.graph_rag_candidate,
                reranker_applied=reranker_applied,
                corrective_retry_applied=corrective_retry_applied,
                reranker_model=service._last_reranker_model if reranker_applied else None,
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


def lexical_search_impl(
    service,
    *,
    query: str,
    top_k: int,
    visibility: str,
    category: str | None,
    parent_ref_keys: tuple[str, ...] | None = None,
) -> list[dict[str, Any]]:
    _refresh_native_namespace()
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

        with psycopg.connect(service.database_url, row_factory=dict_row) as connection:
            with connection.cursor() as cursor:
                cursor.execute(sql, params)
                rows = cursor.fetchall()

        set_span_attributes(**{'eduassist.retrieval.result_count': len(rows)})
        return [_enrich_hit_metadata(dict(row)) for row in rows]


def fuse_hits_impl(
    service,
    *,
    lexical_sources: dict[str, list[dict[str, Any]]],
    vector_sources: dict[str, list[dict[str, Any]]],
    top_k: int,
    category_bias: str | None,
    max_chunks_per_document: int,
    intent: str,
    normalized_query: str,
) -> list[RetrievalHit]:
    _refresh_native_namespace()
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
                text_excerpt=service._excerpt(item.get('text_content', '')),
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
