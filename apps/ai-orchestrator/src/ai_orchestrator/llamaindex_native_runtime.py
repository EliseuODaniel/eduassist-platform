from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from typing import Any

from fastembed import TextEmbedding
from llama_index.core.base.embeddings.base import BaseEmbedding
from llama_index.core.base.response.schema import Response
from llama_index.core.query_engine import CustomQueryEngine
from llama_index.core.schema import NodeWithScore, TextNode
from llama_index.core.selectors import EmbeddingSingleSelector
from llama_index.core.tools import QueryEngineTool
from pydantic import PrivateAttr

from . import runtime as rt
from .agent_kernel import KernelPlan, KernelReflection, KernelRunResult
from .entity_resolution import resolve_entity_hints
from .models import (
    AccessTier,
    MessageResponse,
    MessageResponseCitation,
    MessageResponseRequest,
    OrchestrationMode,
    QueryDomain,
    RetrievalBackend,
)
from .retrieval import get_retrieval_service


@dataclass(frozen=True)
class LlamaIndexPublicExecution:
    answer_text: str
    citations: tuple[MessageResponseCitation, ...]
    selected_tools: tuple[str, ...]
    retrieval_backend: RetrievalBackend
    reason: str
    graph_path: tuple[str, ...]


class FastembedSelectorEmbedding(BaseEmbedding):
    _embedder: TextEmbedding = PrivateAttr()

    def __init__(self, *, model_name: str) -> None:
        super().__init__(model_name=model_name)
        self._embedder = TextEmbedding(model_name=model_name)

    def _embed_once(self, text: str) -> list[float]:
        return list(next(self._embedder.embed([text])))

    def _get_query_embedding(self, query: str) -> list[float]:
        return self._embed_once(query)

    async def _aget_query_embedding(self, query: str) -> list[float]:
        return self._get_query_embedding(query)

    def _get_text_embedding(self, text: str) -> list[float]:
        return self._embed_once(text)

    async def _aget_text_embedding(self, text: str) -> list[float]:
        return self._get_text_embedding(text)


@lru_cache(maxsize=4)
def _selector_embedding(model_name: str) -> FastembedSelectorEmbedding:
    return FastembedSelectorEmbedding(model_name=model_name)


class PublicProfileQueryEngine(CustomQueryEngine):
    settings: Any
    request: MessageResponseRequest
    preview: Any
    profile: dict[str, Any]
    actor: dict[str, Any] | None = None
    original_message: str
    conversation_context: dict[str, Any] | None = None
    semantic_plan: Any = None

    def custom_query(self, query_str: str) -> Response:
        resolved_plan = self.semantic_plan
        rule_plan = rt._build_public_institution_plan(
            query_str,
            list(getattr(self.semantic_plan, 'required_tools', ()) or ()),
            semantic_plan=None,
            conversation_context=self.conversation_context,
            school_profile=self.profile,
        )
        if resolved_plan is None or rule_plan.conversation_act != 'canonical_fact':
            resolved_plan = rule_plan
        answer = rt._compose_public_profile_answer(
            self.profile,
            query_str,
            actor=self.actor,
            original_message=self.original_message,
            conversation_context=self.conversation_context,
            semantic_plan=resolved_plan,
        )
        return Response(
            response=answer,
            metadata={
                'selected_tools': ['get_public_school_profile'],
                'reason': 'llamaindex_public_profile',
                'retrieval_backend': RetrievalBackend.none.value,
            },
        )

    async def acustom_query(self, query_str: str) -> Response:
        resolved_plan = self.semantic_plan
        rule_plan = rt._build_public_institution_plan(
            query_str,
            list(getattr(self.semantic_plan, 'required_tools', ()) or ()),
            semantic_plan=None,
            conversation_context=self.conversation_context,
            school_profile=self.profile,
        )
        if resolved_plan is None or rule_plan.conversation_act != 'canonical_fact':
            resolved_plan = rule_plan
        preview = self.preview.model_copy(deep=True)
        preview.selected_tools = list(resolved_plan.required_tools)
        answer = await rt._compose_structured_tool_answer(
            settings=self.settings,
            request=self.request,
            analysis_message=query_str,
            preview=preview,
            actor=self.actor,
            school_profile=self.profile,
            conversation_context=self.conversation_context,
            resolved_public_plan=resolved_plan,
            prefer_fast_public_path=True,
        )
        return Response(
            response=answer,
            metadata={
                'selected_tools': list(dict.fromkeys([*preview.selected_tools, 'get_public_school_profile'])),
                'reason': 'llamaindex_public_profile',
                'retrieval_backend': RetrievalBackend.none.value,
            },
        )


class PublicPricingProjectionQueryEngine(CustomQueryEngine):
    settings: Any
    request: MessageResponseRequest
    preview: Any
    profile: dict[str, Any]
    actor: dict[str, Any] | None = None
    original_message: str
    conversation_context: dict[str, Any] | None = None
    semantic_plan: Any = None

    def custom_query(self, query_str: str) -> Response:
        pricing_plan = self.semantic_plan
        if pricing_plan is not None and pricing_plan.conversation_act != 'pricing':
            pricing_plan = rt.replace(
                pricing_plan,
                conversation_act='pricing',
                secondary_acts=(),
            )
        answer = rt._compose_public_profile_answer(
            self.profile,
            query_str,
            actor=self.actor,
            original_message=self.original_message,
            conversation_context=self.conversation_context,
            semantic_plan=pricing_plan,
        )
        return Response(
            response=answer,
            metadata={
                'selected_tools': ['get_public_school_profile', 'project_public_pricing'],
                'reason': 'llamaindex_public_pricing_projection',
                'retrieval_backend': RetrievalBackend.none.value,
            },
        )

    async def acustom_query(self, query_str: str) -> Response:
        pricing_plan = self.semantic_plan
        if pricing_plan is not None and pricing_plan.conversation_act != 'pricing':
            pricing_plan = rt.replace(
                pricing_plan,
                conversation_act='pricing',
                secondary_acts=(),
            )
        preview = self.preview.model_copy(deep=True)
        preview.selected_tools = list(getattr(pricing_plan, 'required_tools', ()) or preview.selected_tools)
        answer = await rt._compose_structured_tool_answer(
            settings=self.settings,
            request=self.request,
            analysis_message=query_str,
            preview=preview,
            actor=self.actor,
            school_profile=self.profile,
            conversation_context=self.conversation_context,
            resolved_public_plan=pricing_plan,
            prefer_fast_public_path=True,
        )
        return Response(
            response=answer,
            metadata={
                'selected_tools': list(dict.fromkeys([*preview.selected_tools, 'project_public_pricing'])),
                'reason': 'llamaindex_public_pricing_projection',
                'retrieval_backend': RetrievalBackend.none.value,
            },
        )


class PublicRetrievalQueryEngine(CustomQueryEngine):
    settings: Any
    preview: Any
    original_message: str

    def custom_query(self, query_str: str) -> Response:
        retrieval_service = get_retrieval_service(
            database_url=self.settings.database_url,
            qdrant_url=self.settings.qdrant_url,
            collection_name=self.settings.qdrant_documents_collection,
            embedding_model=self.settings.document_embedding_model,
            enable_query_variants=self.settings.retrieval_enable_query_variants,
            enable_late_interaction_rerank=self.settings.retrieval_enable_late_interaction_rerank,
            late_interaction_model=self.settings.retrieval_late_interaction_model,
            candidate_pool_size=self.settings.retrieval_candidate_pool_size,
        )
        search = retrieval_service.hybrid_search(
            query=query_str,
            top_k=4,
            visibility='public',
            category=None,
        )
        query_hints = {
            *rt._extract_public_entity_hints(self.original_message),
            *rt._extract_public_entity_hints(query_str),
        }
        retrieval_hits = list(search.hits)
        if rt._retrieval_hits_cover_query_hints(retrieval_hits, query_hints):
            retrieval_hits = rt._filter_retrieval_hits_by_query_hints(retrieval_hits, query_hints)
        citations = rt._collect_citations(retrieval_hits)
        if not retrieval_hits:
            answer = rt._compose_public_gap_answer(query_hints)
        else:
            public_answerability = rt._assess_public_answerability(query_str, retrieval_hits, query_hints)
            if not public_answerability.enough_support:
                answer = rt._compose_answerability_gap_answer(public_answerability, self.original_message)
            else:
                answer = rt._compose_deterministic_answer(
                    request_message=self.original_message,
                    preview=self.preview,
                    retrieval_hits=retrieval_hits,
                    citations=citations,
                    calendar_events=[],
                    query_hints=query_hints,
                )
        source_nodes = [
            NodeWithScore(
                node=TextNode(
                    text=hit.text_excerpt,
                    extra_info={
                        'document_title': hit.document_title,
                        'version_label': hit.citation.version_label,
                        'storage_path': hit.citation.storage_path,
                        'chunk_id': hit.citation.chunk_id,
                    },
                ),
                score=hit.rerank_score or hit.fused_score,
            )
            for hit in retrieval_hits[:4]
        ]
        return Response(
            response=answer,
            source_nodes=source_nodes,
            metadata={
                'selected_tools': ['hybrid_retrieval'],
                'reason': 'llamaindex_public_retrieval',
                'retrieval_backend': RetrievalBackend.qdrant_hybrid.value,
                'citations': [citation.model_dump(mode='json') for citation in citations],
            },
        )


def _should_use_llamaindex_native_public_router(plan: KernelPlan) -> bool:
    preview = plan.preview
    if preview.classification.access_tier is not AccessTier.public:
        return False
    if preview.classification.domain not in {QueryDomain.institution, QueryDomain.calendar}:
        return False
    return preview.mode in {OrchestrationMode.structured_tool, OrchestrationMode.hybrid_retrieval}


def _tool_descriptions(plan: Any) -> dict[str, str]:
    return {
        'public_profile': (
            'Use para fatos publicos estruturados da escola: endereco, contato, biblioteca, horarios, '
            'documentos de matricula, calendario, visitas, segmentos, precos publicados e servicos.'
        ),
        'pricing_projection': (
            'Use para simulacoes publicas e hipoteticas de preco com quantidade de filhos ou dependentes, '
            'taxa de matricula, mensalidade e observacoes comerciais publicadas.'
        ),
        'public_retrieval': (
            'Use para perguntas institucionais que pedem sintese documental, proposta pedagogica, '
            'comparacoes, diferenciais, regras e respostas que dependem de recuperar evidencias textuais.'
        ),
    }


def _extract_response_citations(response: Response) -> tuple[MessageResponseCitation, ...]:
    metadata = response.metadata or {}
    raw_citations = metadata.get('citations')
    citations: list[MessageResponseCitation] = []
    if isinstance(raw_citations, list):
        for item in raw_citations:
            if not isinstance(item, dict):
                continue
            try:
                citations.append(MessageResponseCitation.model_validate(item))
            except Exception:
                continue
    if citations:
        return tuple(citations)
    for node_with_score in getattr(response, 'source_nodes', []) or []:
        node = getattr(node_with_score, 'node', None)
        if node is None:
            continue
        extra_info = getattr(node, 'extra_info', {}) or {}
        try:
            citations.append(
                MessageResponseCitation(
                    document_title=str(extra_info.get('document_title', 'Documento institucional')),
                    version_label=str(extra_info.get('version_label', 'desconhecida')),
                    storage_path=str(extra_info.get('storage_path', '')),
                    chunk_id=str(extra_info.get('chunk_id', '')),
                    excerpt=str(getattr(node, 'text', '') or ''),
                )
            )
        except Exception:
            continue
    return tuple(citations)


def _route_public_query_tool(
    *,
    request: MessageResponseRequest,
    plan: Any,
    tools: dict[str, QueryEngineTool],
    embedding_model: str,
) -> QueryEngineTool:
    hints = resolve_entity_hints(request.message)
    if hints.domain_hint == 'public_pricing' and hints.is_hypothetical and hints.quantity_hint:
        return tools['pricing_projection']

    direct_profile_acts = {
        'pricing',
        'timeline',
        'calendar_events',
        'comparative',
        'curriculum',
        'confessional',
        'highlight',
        'contacts',
        'leadership',
        'location',
        'schedule',
        'features',
        'segments',
        'document_submission',
        'visit',
        'operating_hours',
        'teacher_directory',
        'service_routing',
        'assistant_identity',
        'capabilities',
        'greeting',
        'school_name',
        'web_presence',
        'social_presence',
        'careers',
        'auth_guidance',
        'access_scope',
        'utility_date',
    }
    if plan.conversation_act in direct_profile_acts:
        return tools['public_profile']

    selector = EmbeddingSingleSelector.from_defaults(
        embed_model=_selector_embedding(embedding_model),
    )
    selection = selector.select(
        [tool.metadata for tool in tools.values()],
        request.message,
    )
    selected_index = 0
    if getattr(selection, 'selections', None):
        selected_index = selection.selections[0].index
    tool_names = list(tools.keys())
    selected_index = max(0, min(selected_index, len(tool_names) - 1))
    return tools[tool_names[selected_index]]


async def maybe_execute_llamaindex_native_plan(
    *,
    request: MessageResponseRequest,
    settings: Any,
    plan: KernelPlan,
    engine_name: str,
    engine_mode: str,
) -> KernelRunResult | None:
    if not _should_use_llamaindex_native_public_router(plan):
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
    if not isinstance(school_profile, dict):
        return None

    public_plan = await rt._resolve_public_institution_plan(
        settings=settings,
        message=request.message,
        preview=plan.preview,
        conversation_context=conversation_context,
        school_profile=school_profile,
    )
    preview = plan.preview.model_copy(deep=True)
    preview.selected_tools = list(public_plan.required_tools)

    descriptions = _tool_descriptions(public_plan)
    tools = {
        'public_profile': QueryEngineTool.from_defaults(
            query_engine=PublicProfileQueryEngine(
                settings=settings,
                request=request,
                preview=preview,
                profile=school_profile,
                actor=actor,
                original_message=request.message,
                conversation_context=conversation_context,
                semantic_plan=public_plan,
            ),
            name='public_profile',
            description=descriptions['public_profile'],
        ),
        'pricing_projection': QueryEngineTool.from_defaults(
            query_engine=PublicPricingProjectionQueryEngine(
                settings=settings,
                request=request,
                preview=preview,
                profile=school_profile,
                actor=actor,
                original_message=request.message,
                conversation_context=conversation_context,
                semantic_plan=public_plan,
            ),
            name='pricing_projection',
            description=descriptions['pricing_projection'],
        ),
        'public_retrieval': QueryEngineTool.from_defaults(
            query_engine=PublicRetrievalQueryEngine(
                settings=settings,
                preview=preview,
                original_message=request.message,
            ),
            name='public_retrieval',
            description=descriptions['public_retrieval'],
        ),
    }
    selected_tool = _route_public_query_tool(
        request=request,
        plan=public_plan,
        tools=tools,
        embedding_model=settings.document_embedding_model,
    )
    tool_response = await selected_tool.query_engine.aquery(analysis_message)
    answer_text = str(getattr(tool_response, 'response', '') or str(tool_response)).strip()
    if not answer_text:
        return None

    citations = list(_extract_response_citations(tool_response))
    message_text = answer_text
    verification_slot_memory = rt._build_conversation_slot_memory(
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
        deterministic_fallback_text=answer_text,
        public_plan=public_plan,
        slot_memory=verification_slot_memory,
    )
    if not verification.valid:
        return None

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
        answer_verifier_fallback_used=False,
        deterministic_fallback_available=True,
        answer_verifier_judge_used=semantic_judge_used,
        langgraph_trace_metadata={
            'llamaindex_selected_tool': selected_tool.metadata.name,
        },
    )

    selected_tools = list(
        dict.fromkeys(
            [
                *preview.selected_tools,
                *list((tool_response.metadata or {}).get('selected_tools', [])),
                'llamaindex_selector_router',
            ]
        )
    )
    retrieval_backend = RetrievalBackend(
        str((tool_response.metadata or {}).get('retrieval_backend', RetrievalBackend.none.value))
    )
    response = MessageResponse(
        message_text=message_text,
        mode=preview.mode,
        classification=preview.classification,
        retrieval_backend=retrieval_backend,
        selected_tools=selected_tools,
        citations=citations,
        visual_assets=[],
        suggested_replies=suggested_replies,
        calendar_events=[],
        needs_authentication=preview.needs_authentication,
        graph_path=[
            *preview.graph_path,
            'llamaindex:workflow',
            'llamaindex:selector_router',
            f'llamaindex:tool:{selected_tool.metadata.name}',
            f'kernel:{plan.stack_name}',
        ],
        risk_flags=preview.risk_flags,
        reason='llamaindex_native_public_router',
    )
    reflection = KernelReflection(
        grounded=verification.valid,
        verifier_reason=verification.reason,
        fallback_used=False,
        answer_judge_used=semantic_judge_used,
        notes=[
            f'route:{preview.mode.value}',
            f'slice:{plan.slice_name}',
            f'llamaindex_tool:{selected_tool.metadata.name}',
            *plan.plan_notes,
        ],
    )
    return KernelRunResult(
        plan=plan,
        reflection=reflection,
        response=response.model_dump(mode='json'),
    )
