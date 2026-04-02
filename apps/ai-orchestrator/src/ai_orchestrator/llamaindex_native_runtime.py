from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass
from functools import lru_cache
from typing import Any

from fastembed import TextEmbedding
from llama_index.core import VectorStoreIndex
from llama_index.core.agent.workflow import AgentWorkflow, FunctionAgent
from llama_index.core.base.base_retriever import BaseRetriever
from llama_index.core.base.embeddings.base import BaseEmbedding
from llama_index.core.base.llms.types import ChatMessage, MessageRole
from llama_index.core.base.response.schema import Response
from llama_index.core.indices.vector_store.retrievers import VectorIndexAutoRetriever
from llama_index.core.memory import Memory
from llama_index.core.prompts import PromptTemplate
from llama_index.core.query_engine import (
    CitationQueryEngine,
    CustomQueryEngine,
    RouterQueryEngine,
    SubQuestionQueryEngine,
)
from llama_index.core.response_synthesizers import get_response_synthesizer
from llama_index.core.response_synthesizers.type import ResponseMode
from llama_index.core.schema import NodeWithScore, QueryBundle, TextNode
from llama_index.core.selectors import EmbeddingSingleSelector, PydanticSingleSelector
from llama_index.core.tools import FunctionTool, QueryEngineTool
from llama_index.core.vector_stores.types import (
    FilterOperator,
    MetadataFilter,
    MetadataFilters,
    MetadataInfo,
    VectorStoreInfo,
)
from pydantic import BaseModel, Field, PrivateAttr
from qdrant_client import AsyncQdrantClient, QdrantClient

from . import runtime as rt
from .agent_kernel import KernelPlan, KernelReflection, KernelRunResult
from .entity_resolution import resolve_entity_hints
from .evidence_pack import (
    build_direct_answer_evidence_pack,
    build_retrieval_evidence_pack,
    build_structured_tool_evidence_pack,
)
from .kernel_runtime import _maybe_hypothetical_public_pricing_answer
from .llamaindex_public_intent_registry import (
    LLAMAINDEX_PUBLIC_INTENT_RULES,
    LlamaIndexPublicIntentRule,
)
from .llm_provider import _google_model_candidates
from .models import (
    AccessTier,
    IntentClassification,
    MessageEvidencePack,
    MessageResponse,
    MessageResponseCitation,
    MessageResponseRequest,
    OrchestrationMode,
    QueryDomain,
    RetrievalBackend,
)
from .path_profiles import PathExecutionProfile, get_path_execution_profile
from .public_doc_knowledge import compose_public_canonical_lane_answer, match_public_canonical_lane
from .public_known_unknowns import (
    compose_public_known_unknown_answer,
    detect_public_known_unknown_key,
)
from .retrieval import (
    can_read_restricted_documents,
    compose_restricted_document_grounded_answer_for_query,
    compose_restricted_document_no_match_answer,
    get_retrieval_service,
    looks_like_restricted_document_query,
    select_relevant_restricted_hits,
)

try:
    from llama_index.llms.openai import OpenAI as LlamaIndexOpenAI

    LLAMAINDEX_OPENAI_AVAILABLE = True
except Exception:  # pragma: no cover - optional dependency
    LlamaIndexOpenAI = None  # type: ignore[assignment]
    LLAMAINDEX_OPENAI_AVAILABLE = False

try:
    from llama_index.llms.google_genai import GoogleGenAI as LlamaIndexGoogleGenAI

    LLAMAINDEX_GOOGLE_GENAI_AVAILABLE = True
except Exception:  # pragma: no cover - optional dependency
    LlamaIndexGoogleGenAI = None  # type: ignore[assignment]
    LLAMAINDEX_GOOGLE_GENAI_AVAILABLE = False

try:
    from llama_index.vector_stores.qdrant import QdrantVectorStore

    LLAMAINDEX_QDRANT_AVAILABLE = True
except Exception:  # pragma: no cover - optional dependency
    QdrantVectorStore = None  # type: ignore[assignment]
    LLAMAINDEX_QDRANT_AVAILABLE = False


@dataclass(frozen=True)
class LlamaIndexPublicExecution:
    answer_text: str
    citations: tuple[MessageResponseCitation, ...]
    selected_tools: tuple[str, ...]
    retrieval_backend: RetrievalBackend
    reason: str
    graph_path: tuple[str, ...]


class LlamaIndexNativePublicDecision(BaseModel):
    conversation_act: str = Field(default='canonical_fact')
    answer_mode: str = Field(default='profile')
    required_tools: list[str] = Field(default_factory=list)
    secondary_acts: list[str] = Field(default_factory=list)
    requested_attribute: str | None = None
    requested_channel: str | None = None
    focus_hint: str | None = None
    unpublished_key: str | None = None
    use_conversation_context: bool = False


def _looks_like_external_live_query(message: str) -> bool:
    normalized = rt._normalize_text(message)
    weather_terms = {'vai chover', 'chover', 'chuva', 'clima', 'previsao do tempo', 'previsão do tempo', 'tempo hoje'}
    news_terms = {'ultima noticia', 'última notícia', 'noticia do mec', 'notícia do mec', 'publicada hoje', 'noticia hoje', 'notícia hoje'}
    return any(rt._message_matches_term(normalized, term) for term in weather_terms | news_terms)


def _compose_external_live_query_answer(message: str) -> str | None:
    normalized = rt._normalize_text(message)
    if any(rt._message_matches_term(normalized, term) for term in {'vai chover', 'chover', 'chuva', 'clima', 'previsao do tempo', 'previsão do tempo', 'tempo hoje'}):
        return (
            'Eu nao consigo consultar previsao do tempo em tempo real por aqui. '
            'Se quiser, eu posso te informar a proxima reuniao geral de pais publicada pela escola e os canais oficiais para acompanhar mudancas de agenda.'
        )
    if any(rt._message_matches_term(normalized, term) for term in {'ultima noticia', 'última notícia', 'noticia do mec', 'notícia do mec', 'publicada hoje', 'noticia hoje', 'notícia hoje'}):
        return (
            'Eu nao consigo consultar noticias externas em tempo real por aqui, incluindo publicacoes do MEC no dia. '
            'Se quiser, eu posso ajudar com normas e comunicados institucionais que ja estejam publicados no corpus da escola.'
        )
    return None


def _can_read_private_documents(*, request: MessageResponseRequest, actor: dict[str, Any] | None) -> bool:
    actor_role = str((actor or {}).get('role_code', '') or '').strip().lower()
    return bool(
        can_read_restricted_documents(request.user)
        or actor_role in {'staff', 'teacher'}
    )


def _looks_like_restricted_doc_query(message: str) -> bool:
    return looks_like_restricted_document_query(message)


def _restricted_doc_hit_to_citation(hit: Any) -> MessageResponseCitation | None:
    citation = getattr(hit, 'citation', None)
    if citation is None:
        return None
    document_title = str(getattr(citation, 'document_title', '') or '').strip()
    chunk_id = str(getattr(citation, 'chunk_id', '') or '').strip()
    if not document_title or not chunk_id:
        return None
    return MessageResponseCitation(
        document_title=document_title,
        version_label=str(getattr(citation, 'version_label', 'atual') or 'atual'),
        storage_path=str(getattr(citation, 'storage_path', 'inline') or 'inline'),
        chunk_id=chunk_id,
        excerpt=str(getattr(hit, 'text_excerpt', '') or getattr(hit, 'contextual_summary', '') or '').strip() or 'evidencia restrita',
    )


def _compose_restricted_doc_grounded_answer(hits: list[Any]) -> str | None:
    if not hits:
        return None
    primary = hits[0]
    primary_title = str(getattr(primary, 'document_title', '') or 'documento interno').strip()
    primary_excerpt = str(getattr(primary, 'text_excerpt', '') or getattr(primary, 'contextual_summary', '') or '').strip()
    lines = [f"Nos documentos internos consultados, a orientacao mais relevante aparece em {primary_title}:"]
    if primary_excerpt:
        lines.append(primary_excerpt)
    seen_titles = {primary_title}
    for hit in hits[1:3]:
        title = str(getattr(hit, 'document_title', '') or '').strip()
        excerpt = str(getattr(hit, 'text_excerpt', '') or getattr(hit, 'contextual_summary', '') or '').strip()
        if not excerpt:
            continue
        label = title if title and title not in seen_titles else 'Complemento interno'
        lines.append(f"{label}: {excerpt}")
        if title:
            seen_titles.add(title)
    return "\n".join(lines)


async def _maybe_execute_llamaindex_restricted_doc_fast_path(
    *,
    request: MessageResponseRequest,
    settings: Any,
    plan: KernelPlan,
    engine_name: str,
    engine_mode: str,
) -> KernelRunResult | None:
    if not _looks_like_restricted_doc_query(request.message):
        return None
    actor = await rt._fetch_actor_context(settings=settings, telegram_chat_id=request.telegram_chat_id)
    if not _can_read_private_documents(request=request, actor=actor):
        return None
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
    retrieval_result = retrieval_service.hybrid_search(
        query=request.message,
        top_k=3,
        visibility='private',
        category=None,
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


_LLAMAINDEX_NATIVE_PUBLIC_ROUTER_PROMPT = PromptTemplate(
    """
Voce e um roteador semantico para perguntas publicas de uma escola.
Sua tarefa e produzir uma decisao estruturada para o runtime.

Escolha `conversation_act` usando um dos valores:
- greeting
- utility_date
- auth_guidance
- access_scope
- assistant_identity
- capabilities
- service_routing
- document_submission
- careers
- teacher_directory
- leadership
- contacts
- web_presence
- social_presence
- comparative
- pricing
- schedule
- operating_hours
- curriculum
- features
- highlight
- visit
- location
- confessional
- kpi
- segments
- school_name
- timeline
- calendar_events
- canonical_fact

Escolha `answer_mode` usando um dos valores:
- profile: a pergunta e clara e pode ser respondida com fatos publicos estruturados, diretorios ou politicas publicadas.
- documentary: a pergunta e aberta, explicativa, comparativa ou pede sintese melhor respondida por retrieval documental com citacoes.
- pricing: a pergunta trata de valores, bolsas, descontos, matricula ou simulacoes publicas.
- unpublished: a pergunta e clara e publica, mas o detalhe exato pedido nao aparece nos dados publicados.
- clarify: use somente se a pergunta estiver realmente ambigua e sem informacao minima para responder ou marcar como unpublished.

Regras obrigatorias:
- Prefira `unpublished` a `clarify` quando a pergunta for clara, mas o dado nao estiver publicado.
- Prefira `documentary` para "me explique", "por que escolher", "quais os diferenciais", "proposta pedagogica", "com base nos documentos", comparacoes abertas e perguntas que pedem argumento institucional.
- Use `pricing` para bolsa, desconto, mensalidade, taxa de matricula e simulacao comercial publica.
- Se a pergunta pedir contagens ou detalhes exatos nao publicados, use `unpublished`.
- Se a pergunta pedir idade minima e esse dado nao estiver explicitamente publicado, use `unpublished` com `unpublished_key="minimum_age"`.
- Se a pergunta pedir quantidade de salas de aula e isso nao estiver explicitamente publicado, use `unpublished` com `unpublished_key="classroom_count"`.
- Se a pergunta pedir total de alunos, use `unpublished` com `unpublished_key="total_students"`.
- Se a pergunta pedir total de livros, use `unpublished` com `unpublished_key="library_book_count"`.
- Se a pergunta pedir cardapio da cantina e esse dado nao estiver publicado, use `unpublished` com `unpublished_key="cafeteria_menu"`.
- `clarify` deve ser raro.

Mensagem do usuario:
{message}

Preview atual:
{preview_summary}

Contexto recente:
{conversation_context}

Resumo curado do que esta publicado:
{profile_summary}
""".strip()
)


class FastembedSelectorEmbedding(BaseEmbedding):
    _embedder: TextEmbedding | None = PrivateAttr(default=None)

    def __init__(self, *, model_name: str) -> None:
        super().__init__(model_name=model_name)

    @property
    def embedder(self) -> TextEmbedding:
        if self._embedder is None:
            self._embedder = TextEmbedding(model_name=self.model_name)
        return self._embedder

    def _embed_once(self, text: str) -> list[float]:
        return list(next(self.embedder.embed([text])))

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


@lru_cache(maxsize=4)
def _native_qdrant_vector_store(*, qdrant_url: str, collection_name: str) -> Any | None:
    if not LLAMAINDEX_QDRANT_AVAILABLE:
        return None
    client = QdrantClient(url=qdrant_url)
    aclient = AsyncQdrantClient(url=qdrant_url)
    return QdrantVectorStore(
        collection_name=collection_name,
        client=client,
        aclient=aclient,
        text_key='text_content',
    )


@lru_cache(maxsize=16)
def _qdrant_collection_exists(*, qdrant_url: str, collection_name: str) -> bool:
    try:
        client = QdrantClient(url=qdrant_url)
        client.get_collection(collection_name)
        return True
    except Exception:
        return False


def _resolve_llamaindex_qdrant_collection(settings: Any) -> str:
    preferred = str(getattr(settings, 'llamaindex_qdrant_documents_collection', '') or '').strip()
    fallback = str(getattr(settings, 'qdrant_documents_collection', 'school_documents'))
    if preferred and _qdrant_collection_exists(qdrant_url=str(settings.qdrant_url), collection_name=preferred):
        return preferred
    return fallback


def _llamaindex_timeout_seconds(settings: Any | None = None) -> float:
    configured = getattr(settings, 'llamaindex_native_timeout_seconds', 20.0) if settings is not None else 20.0
    try:
        return max(5.0, float(configured))
    except Exception:
        return 20.0


async def _await_with_llamaindex_timeout(awaitable: Any, *, settings: Any | None = None) -> Any:
    return await asyncio.wait_for(awaitable, timeout=_llamaindex_timeout_seconds(settings))


@lru_cache(maxsize=4)
def _native_qdrant_vector_index(*, qdrant_url: str, collection_name: str, embedding_model: str) -> Any | None:
    vector_store = _native_qdrant_vector_store(qdrant_url=qdrant_url, collection_name=collection_name)
    if vector_store is None:
        return None
    return VectorStoreIndex.from_vector_store(
        vector_store=vector_store,
        embed_model=_selector_embedding(embedding_model),
    )


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
                'selected_tools': list(
                    dict.fromkeys([*(list(getattr(resolved_plan, 'required_tools', ()) or ())), 'get_public_school_profile'])
                ),
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

    def _direct_pricing_answer(self, query_str: str) -> tuple[str, Any] | None:
        return _maybe_hypothetical_public_pricing_answer(
            request=self.request,
            plan=KernelPlan(
                stack_name='llamaindex',
                mode='native_public_pricing',
                analysis_message=query_str,
                preview=self.preview,
                slice_name='public',
                entities=resolve_entity_hints(query_str),
            ),
            preview=self.preview,
            school_profile=self.profile,
            conversation_context=self.conversation_context,
        )

    def custom_query(self, query_str: str) -> Response:
        direct_pricing_answer = self._direct_pricing_answer(query_str)
        if direct_pricing_answer:
            answer, pricing_plan = direct_pricing_answer
        else:
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
        preview = self.preview.model_copy(deep=True)
        preview.mode = OrchestrationMode.structured_tool
        preview.reason = 'llamaindex_public_pricing_projection'
        preview.classification = _public_classification_for_act(
            'pricing',
            'roteamento nativo do llamaindex para precificacao publica',
        )
        preview.needs_authentication = False
        direct_pricing_answer = self._direct_pricing_answer(query_str)
        if direct_pricing_answer:
            answer, pricing_plan = direct_pricing_answer
            preview.selected_tools = list(
                dict.fromkeys([*preview.selected_tools, 'get_public_school_profile', 'project_public_pricing'])
            )
        else:
            pricing_plan = self.semantic_plan
            if pricing_plan is not None and pricing_plan.conversation_act != 'pricing':
                pricing_plan = rt.replace(
                    pricing_plan,
                    conversation_act='pricing',
                    secondary_acts=(),
                )
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
            cheap_candidate_pool_size=self.settings.retrieval_cheap_candidate_pool_size,
            deep_candidate_pool_size=self.settings.retrieval_deep_candidate_pool_size,
            rerank_fused_weight=self.settings.retrieval_rerank_fused_weight,
            rerank_late_interaction_weight=self.settings.retrieval_rerank_late_interaction_weight,
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


class PublicHybridCitationRetriever(BaseRetriever):
    _settings: Any = PrivateAttr()
    _original_message: str = PrivateAttr()
    _latest_citations: tuple[MessageResponseCitation, ...] = PrivateAttr(default_factory=tuple)
    _latest_query_plan: Any | None = PrivateAttr(default=None)

    def __init__(self, *, settings: Any, original_message: str, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._settings = settings
        self._original_message = original_message
        self._latest_citations = ()
        self._latest_query_plan = None

    def latest_citations(self) -> tuple[MessageResponseCitation, ...]:
        return tuple(getattr(self, '_latest_citations', ()) or ())

    def _search(self, query_str: str) -> list[NodeWithScore]:
        retrieval_service = get_retrieval_service(
            database_url=self._settings.database_url,
            qdrant_url=self._settings.qdrant_url,
            collection_name=self._settings.qdrant_documents_collection,
            embedding_model=self._settings.document_embedding_model,
            enable_query_variants=self._settings.retrieval_enable_query_variants,
            enable_late_interaction_rerank=self._settings.retrieval_enable_late_interaction_rerank,
            late_interaction_model=self._settings.retrieval_late_interaction_model,
            candidate_pool_size=self._settings.retrieval_candidate_pool_size,
            cheap_candidate_pool_size=self._settings.retrieval_cheap_candidate_pool_size,
            deep_candidate_pool_size=self._settings.retrieval_deep_candidate_pool_size,
            rerank_fused_weight=self._settings.retrieval_rerank_fused_weight,
            rerank_late_interaction_weight=self._settings.retrieval_rerank_late_interaction_weight,
        )
        search = retrieval_service.hybrid_search(
            query=query_str,
            top_k=4,
            visibility='public',
            category=None,
        )
        query_hints = {
            *rt._extract_public_entity_hints(self._original_message),
            *rt._extract_public_entity_hints(query_str),
        }
        retrieval_hits = list(search.hits)
        if rt._retrieval_hits_cover_query_hints(retrieval_hits, query_hints):
            retrieval_hits = rt._filter_retrieval_hits_by_query_hints(retrieval_hits, query_hints)
        public_answerability = rt._assess_public_answerability(query_str, retrieval_hits, query_hints)
        if not public_answerability.enough_support:
            retrieval_hits = []
        citations = rt._collect_citations(retrieval_hits)
        self._latest_citations = tuple(citations)
        self._latest_query_plan = search.query_plan
        return [
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

    def _retrieve(self, query_bundle: QueryBundle) -> list[NodeWithScore]:
        return self._search(query_bundle.query_str)

    async def _aretrieve(self, query_bundle: QueryBundle) -> list[NodeWithScore]:
        return self._search(query_bundle.query_str)


def _should_use_llamaindex_native_public_router(plan: KernelPlan) -> bool:
    preview = plan.preview
    if preview.classification.access_tier is AccessTier.public:
        if preview.classification.domain not in {QueryDomain.institution, QueryDomain.calendar, QueryDomain.unknown}:
            return False
        return preview.mode in {
            OrchestrationMode.structured_tool,
            OrchestrationMode.hybrid_retrieval,
            OrchestrationMode.clarify,
        }
    if preview.mode is not OrchestrationMode.clarify:
        return False
    return preview.classification.domain in {
        QueryDomain.institution,
        QueryDomain.academic,
        QueryDomain.unknown,
    }


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


def _llamaindex_native_fetch_profile_for_act(conversation_act: str) -> bool:
    return conversation_act not in {
        'greeting',
        'utility_date',
        'auth_guidance',
        'access_scope',
        'assistant_identity',
        'capabilities',
        'service_routing',
    }


def _public_classification_for_act(conversation_act: str, reason: str) -> IntentClassification:
    domain = QueryDomain.calendar if conversation_act in {'timeline', 'calendar_events'} else QueryDomain.institution
    return IntentClassification(
        domain=domain,
        access_tier=AccessTier.public,
        confidence=0.9,
        reason=reason,
    )


def _native_public_profile_summary(profile: dict[str, Any]) -> str:
    leadership = [
        {
            'title': str(item.get('title', '')).strip(),
            'name': str(item.get('name', '')).strip(),
        }
        for item in (profile.get('leadership_team') or [])
        if isinstance(item, dict)
    ][:4]
    facilities = [
        {
            'label': str(item.get('label', '')).strip(),
            'available': bool(item.get('available')),
        }
        for item in (profile.get('feature_inventory') or [])
        if isinstance(item, dict)
    ][:12]
    highlights = [
        str(item.get('title', '')).strip()
        for item in (profile.get('highlights') or [])
        if isinstance(item, dict) and str(item.get('title', '')).strip()
    ][:8]
    services = [
        str(item.get('title', '')).strip()
        for item in (profile.get('service_catalog') or [])
        if isinstance(item, dict) and str(item.get('title', '')).strip()
    ][:8]
    summary = {
        'school_name': str(profile.get('school_name', '')).strip(),
        'segments': list(profile.get('segments') or []),
        'shift_offers': [
            {
                'segment': str(item.get('segment', '')).strip(),
                'shift_label': str(item.get('shift_label', '')).strip(),
                'starts_at': str(item.get('starts_at', '')).strip(),
                'ends_at': str(item.get('ends_at', '')).strip(),
            }
            for item in (profile.get('shift_offers') or [])
            if isinstance(item, dict)
        ][:6],
        'interval_schedule': [
            {
                'segment': str(item.get('segment', '')).strip(),
                'label': str(item.get('label', '')).strip(),
                'starts_at': str(item.get('starts_at', '')).strip(),
                'ends_at': str(item.get('ends_at', '')).strip(),
            }
            for item in (profile.get('interval_schedule') or [])
            if isinstance(item, dict)
        ][:6],
        'leadership': leadership,
        'facilities_and_activities': facilities,
        'highlights': highlights,
        'services': services,
        'admissions_highlights': list(profile.get('admissions_highlights') or []),
        'admissions_required_documents': list(profile.get('admissions_required_documents') or []),
        'academic_policy_available': bool(profile.get('academic_policy')),
        'published_gaps': {
            'minimum_age': False,
            'classroom_count': False,
            'total_students': False,
            'library_book_count': False,
            'cafeteria_menu': False,
        },
    }
    return json.dumps(summary, ensure_ascii=False, sort_keys=True)


def _recent_public_context_summary(conversation_context: dict[str, Any] | None) -> str:
    if not isinstance(conversation_context, dict):
        return 'sem contexto recente relevante'
    lines = [
        f'{sender_type}: {content}'
        for sender_type, content in rt._recent_message_lines(conversation_context)[-4:]
    ]
    if not lines:
        return 'sem contexto recente relevante'
    return '\n'.join(lines)


def _llamaindex_public_rule_matches(*, rule: LlamaIndexPublicIntentRule, normalized_message: str) -> bool:
    if rule.none_of and any(rt._message_matches_term(normalized_message, term) for term in rule.none_of):
        return False
    if rule.all_of and not all(rt._message_matches_term(normalized_message, term) for term in rule.all_of):
        return False
    if rule.any_of and not any(rt._message_matches_term(normalized_message, term) for term in rule.any_of):
        return False
    return bool(rule.any_of or rule.all_of)


def _heuristic_llamaindex_native_public_decision(
    *,
    message: str,
    conversation_context: dict[str, Any] | None,
) -> LlamaIndexNativePublicDecision | None:
    normalized_message = rt._normalize_text(message)
    recent_context = _recent_public_context_summary(conversation_context)
    recent_normalized = rt._normalize_text(recent_context)
    matched_rule: LlamaIndexPublicIntentRule | None = None
    for rule in LLAMAINDEX_PUBLIC_INTENT_RULES:
        if _llamaindex_public_rule_matches(rule=rule, normalized_message=normalized_message):
            matched_rule = rule
            break
        if rule.use_conversation_context and rt._is_follow_up_query(message):
            if _llamaindex_public_rule_matches(rule=rule, normalized_message=recent_normalized):
                matched_rule = rule
                break
    if matched_rule is None:
        return None
    return LlamaIndexNativePublicDecision(
        conversation_act=matched_rule.conversation_act,
        answer_mode=matched_rule.answer_mode,
        required_tools=list(matched_rule.required_tools),
        secondary_acts=list(matched_rule.secondary_acts),
        requested_attribute=matched_rule.requested_attribute,
        requested_channel=matched_rule.requested_channel,
        focus_hint=matched_rule.focus_hint,
        unpublished_key=matched_rule.unpublished_key,
        use_conversation_context=matched_rule.use_conversation_context,
    )


def _build_llamaindex_analysis_query(
    *,
    original_message: str,
    analysis_message: str,
    native_decision: LlamaIndexNativePublicDecision | None,
    public_plan: Any,
) -> str:
    parts = [analysis_message]
    requested_attribute = None
    requested_channel = None
    focus_hint = None
    answer_mode = None
    if native_decision is not None:
        requested_attribute = native_decision.requested_attribute
        requested_channel = native_decision.requested_channel
        focus_hint = native_decision.focus_hint
        answer_mode = native_decision.answer_mode
    if requested_attribute is None:
        requested_attribute = getattr(public_plan, 'requested_attribute', None)
    if requested_channel is None:
        requested_channel = getattr(public_plan, 'requested_channel', None)
    if focus_hint is None:
        focus_hint = getattr(public_plan, 'focus_hint', None)
    if focus_hint:
        parts.append(f'Foco da resposta: {focus_hint}.')
    if requested_attribute:
        parts.append(f'Atributo principal pedido: {requested_attribute}.')
    if requested_channel:
        parts.append(f'Canal de referencia caso o dado nao esteja publicado: {requested_channel}.')
    if answer_mode == 'documentary':
        parts.append(
            'Use evidencias documentais publicas do Colegio Horizonte e priorize grounding com citacoes quando disponiveis.'
        )
    elif answer_mode == 'profile':
        parts.append('Prefira fatos publicos estruturados e canonicos da escola.')
    elif answer_mode == 'unpublished':
        parts.append(
            'Se o dado especifico nao estiver publicado, diga explicitamente que a pergunta e valida, mas o dado nao esta publicado oficialmente.'
        )
    normalized_original = rt._normalize_text(original_message)
    normalized_analysis = rt._normalize_text(analysis_message)
    if normalized_original and normalized_original not in normalized_analysis:
        parts.append(f'Pergunta original do usuario: {original_message}')
    return '\n'.join(part for part in parts if part).strip()


def _build_llamaindex_retrieval_query(
    *,
    original_message: str,
    native_decision: LlamaIndexNativePublicDecision | None,
    public_plan: Any,
) -> str:
    focus_hint = None
    requested_attribute = None
    if native_decision is not None:
        focus_hint = native_decision.focus_hint
        requested_attribute = native_decision.requested_attribute
    if focus_hint is None:
        focus_hint = getattr(public_plan, 'focus_hint', None)
    if requested_attribute is None:
        requested_attribute = getattr(public_plan, 'requested_attribute', None)
    fragments = [original_message.strip()]
    if requested_attribute:
        fragments.append(str(requested_attribute).replace('_', ' ').strip())
    if focus_hint:
        fragments.append(str(focus_hint).strip())
    return ' | '.join(fragment for fragment in fragments if fragment).strip()


def _merge_llamaindex_native_public_decisions(
    *,
    llm_decision: LlamaIndexNativePublicDecision | None,
    heuristic_decision: LlamaIndexNativePublicDecision | None,
) -> LlamaIndexNativePublicDecision | None:
    if heuristic_decision is not None:
        return heuristic_decision
    return llm_decision


def _should_trust_llamaindex_native_deterministic_answer(
    *,
    native_decision: LlamaIndexNativePublicDecision | None,
    selected_tool_names: tuple[str, ...],
) -> bool:
    if native_decision is None:
        return False
    if native_decision.answer_mode not in {'profile', 'unpublished'}:
        return False
    deterministic_tools = {'public_profile', 'pricing_projection'}
    effective_tools = {tool_name for tool_name in selected_tool_names if tool_name != 'llamaindex_selector_router'}
    if not effective_tools:
        return False
    return effective_tools.issubset(deterministic_tools)


def _normalize_llamaindex_native_public_decision(
    decision: LlamaIndexNativePublicDecision | None,
) -> LlamaIndexNativePublicDecision | None:
    if decision is None:
        return None
    allowed_acts = set(rt.PUBLIC_SEMANTIC_ACTS)
    allowed_tools = set(rt.PUBLIC_SEMANTIC_TOOLS)
    allowed_modes = {'profile', 'documentary', 'pricing', 'unpublished', 'clarify'}
    conversation_act = str(decision.conversation_act or 'canonical_fact').strip()
    if conversation_act not in allowed_acts:
        conversation_act = 'canonical_fact'
    answer_mode = str(decision.answer_mode or 'profile').strip()
    if answer_mode not in allowed_modes:
        answer_mode = 'profile'
    required_tools = [
        tool_name
        for tool_name in decision.required_tools
        if isinstance(tool_name, str) and tool_name in allowed_tools
    ]
    secondary_acts = [
        act
        for act in decision.secondary_acts
        if isinstance(act, str) and act in allowed_acts and act != conversation_act
    ][:2]
    requested_attribute = str(decision.requested_attribute or '').strip() or None
    requested_channel = str(decision.requested_channel or '').strip() or None
    focus_hint = str(decision.focus_hint or '').strip() or None
    unpublished_key = str(decision.unpublished_key or '').strip() or None
    if answer_mode == 'pricing':
        conversation_act = 'pricing'
    if answer_mode == 'documentary' and conversation_act == 'canonical_fact':
        conversation_act = 'highlight'
    return LlamaIndexNativePublicDecision(
        conversation_act=conversation_act,
        answer_mode=answer_mode,
        required_tools=required_tools,
        secondary_acts=secondary_acts,
        requested_attribute=requested_attribute,
        requested_channel=requested_channel,
        focus_hint=focus_hint,
        unpublished_key=unpublished_key,
        use_conversation_context=bool(decision.use_conversation_context),
    )


async def _resolve_llamaindex_native_public_decision(
    *,
    llm: Any | None,
    settings: Any,
    message: str,
    preview: Any,
    school_profile: dict[str, Any],
    conversation_context: dict[str, Any] | None,
) -> LlamaIndexNativePublicDecision | None:
    if llm is None:
        return None
    try:
        decision = await _await_with_llamaindex_timeout(
            llm.astructured_predict(
                LlamaIndexNativePublicDecision,
                _LLAMAINDEX_NATIVE_PUBLIC_ROUTER_PROMPT,
                message=message,
                preview_summary=json.dumps(
                    {
                        'mode': str(getattr(preview, 'mode', '')),
                        'domain': str(getattr(getattr(preview, 'classification', None), 'domain', '')),
                        'access_tier': str(getattr(getattr(preview, 'classification', None), 'access_tier', '')),
                        'selected_tools': list(getattr(preview, 'selected_tools', []) or []),
                    },
                    ensure_ascii=False,
                    sort_keys=True,
                ),
                conversation_context=_recent_public_context_summary(conversation_context),
                profile_summary=_native_public_profile_summary(school_profile),
            ),
            settings=settings,
        )
    except Exception:
        return None
    return _normalize_llamaindex_native_public_decision(decision)


def _should_run_llamaindex_native_public_resolver(
    *,
    request: MessageResponseRequest,
    plan: KernelPlan,
) -> bool:
    preview = plan.preview
    if preview.classification.access_tier is not AccessTier.public:
        return False
    if preview.classification.domain not in {QueryDomain.institution, QueryDomain.calendar, QueryDomain.unknown}:
        return False
    return True


def _looks_like_llamaindex_value_prop_query(message: str) -> bool:
    normalized = rt._normalize_text(message)
    value_markers = (
        'por que deveria',
        'porque deveria',
        'por que escolher',
        'porque escolher',
        'vale a pena',
        'diferenciais',
        'meus filhos nesse colegio',
        'meus filhos nessa escola',
    )
    school_markers = ('colegio', 'colégio', 'escola', 'filhos')
    return any(marker in normalized for marker in value_markers) and any(
        marker in normalized for marker in school_markers
    )


def _native_public_plan_from_decision(
    *,
    message: str,
    decision: LlamaIndexNativePublicDecision,
    conversation_context: dict[str, Any] | None,
    school_profile: dict[str, Any] | None,
) -> Any:
    semantic_plan = rt.PublicInstitutionPlan(
        conversation_act=decision.conversation_act,
        required_tools=tuple(decision.required_tools),
        fetch_profile=_llamaindex_native_fetch_profile_for_act(decision.conversation_act),
        secondary_acts=tuple(decision.secondary_acts),
        requested_attribute=decision.requested_attribute,
        requested_channel=decision.requested_channel,
        focus_hint=decision.focus_hint,
        semantic_source='llamaindex_native',
        use_conversation_context=decision.use_conversation_context,
    )
    return rt._build_public_institution_plan(
        message,
        list(semantic_plan.required_tools),
        semantic_plan=semantic_plan,
        conversation_context=conversation_context,
        school_profile=school_profile,
    )


def _native_llamaindex_public_unpublished_answer(
    *,
    decision: LlamaIndexNativePublicDecision | None,
    message: str,
    school_profile: dict[str, Any],
) -> str | None:
    school_reference = str(school_profile.get('school_name', 'Colegio Horizonte')).strip() or 'Colegio Horizonte'
    unpublished_key = str(getattr(decision, 'unpublished_key', '') or '').strip()
    if not unpublished_key:
        unpublished_key = detect_public_known_unknown_key(message) or ''
    return compose_public_known_unknown_answer(key=unpublished_key, school_name=school_reference)


def _should_force_llamaindex_documentary_retrieval(
    *,
    message: str,
    public_plan: Any,
    native_decision: LlamaIndexNativePublicDecision | None,
) -> bool:
    if _has_documentary_retrieval_cues(message):
        return True
    if native_decision is not None and native_decision.answer_mode == 'documentary':
        return True
    normalized = rt._normalize_text(message)
    if public_plan.conversation_act not in {'highlight', 'comparative', 'curriculum', 'confessional'}:
        return False
    return any(
        marker in normalized
        for marker in (
            'por que ',
            'porque ',
            'me explique',
            'explique',
            'diferenciais',
            'vale a pena',
            'proposta pedagogica',
            'proposta pedagógica',
            'com base',
        )
    )


def _llamaindex_llm_supports_function_calls(llm: Any | None) -> bool:
    metadata = getattr(llm, 'metadata', None)
    return bool(getattr(metadata, 'is_function_calling_model', False))


def _has_documentary_retrieval_cues(message: str) -> bool:
    normalized = rt._normalize_text(message)
    documentary_cues = (
        'com base nos documentos',
        'nos documentos publicos',
        'nos documentos públicos',
        'com citacoes',
        'com citações',
        'cite as fontes',
        'cite os documentos',
        'mostre as fontes',
    )
    return any(cue in normalized for cue in documentary_cues)


def _should_use_llamaindex_function_agent(*, request: MessageResponseRequest, public_plan: Any) -> bool:
    normalized = rt._normalize_text(request.message)
    if _has_documentary_retrieval_cues(request.message):
        return False
    if _should_use_llamaindex_native_subquestions(request=request, public_plan=public_plan):
        return True
    if public_plan.conversation_act in {'comparative', 'curriculum', 'highlight', 'features', 'pricing'}:
        multi_aspect_markers = (
            ' e como ',
            ' e na ',
            ' e no ',
            ' e qual ',
            ' e quais ',
            ' e existe ',
            ' e isso ',
        )
        marker_hits = sum(1 for marker in multi_aspect_markers if marker in f' {normalized} ')
        if marker_hits >= 2 and len(normalized.split()) >= 12:
            return True
    return normalized.count('?') >= 2


def _build_llamaindex_chat_history(conversation_context: dict[str, Any] | None) -> list[ChatMessage]:
    history: list[ChatMessage] = []
    for sender_type, content in rt._recent_message_lines(conversation_context):
        role = MessageRole.ASSISTANT if sender_type == 'assistant' else MessageRole.USER
        history.append(ChatMessage(role=role, content=content))
    return history


def _route_public_query_tool(
    *,
    request: MessageResponseRequest,
    plan: Any,
    tools: dict[str, QueryEngineTool],
    embedding_model: str,
    llm: Any | None = None,
) -> QueryEngineTool:
    hints = resolve_entity_hints(request.message)
    if hints.domain_hint == 'public_pricing' and hints.is_hypothetical and hints.quantity_hint:
        return tools['pricing_projection']
    if _has_documentary_retrieval_cues(request.message):
        return tools['public_retrieval']

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
        'kpi',
        'canonical_fact',
    }
    if plan.conversation_act in direct_profile_acts:
        return tools['public_profile']

    selection = None
    if llm is not None:
        try:
            selector = PydanticSingleSelector.from_defaults(llm=llm)
            selection = selector.select(
                [tool.metadata for tool in tools.values()],
                request.message,
            )
        except Exception:
            selection = None
    if selection is None:
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


def _build_llamaindex_llm(*, settings: Any) -> Any | None:
    provider = str(getattr(settings, 'llm_provider', 'openai'))
    if provider == 'openai':
        if not LLAMAINDEX_OPENAI_AVAILABLE:
            return None
        if not getattr(settings, 'openai_api_key', None):
            return None
        return LlamaIndexOpenAI(
            model=str(getattr(settings, 'openai_model', 'gpt-5.4')),
            api_key=str(settings.openai_api_key),
            api_base=str(getattr(settings, 'openai_base_url', 'https://api.openai.com/v1')),
            temperature=0,
        )
    if provider in {'google', 'gemini'}:
        if not LLAMAINDEX_GOOGLE_GENAI_AVAILABLE:
            return None
        if not getattr(settings, 'google_api_key', None):
            return None
        for candidate in _google_model_candidates(str(getattr(settings, 'google_model', 'gemini-2.5-flash'))):
            try:
                return LlamaIndexGoogleGenAI(
                    model=str(candidate),
                    api_key=str(settings.google_api_key),
                    temperature=0,
                )
            except Exception:
                continue
        return None
    return None


def _should_use_llamaindex_native_subquestions(*, request: MessageResponseRequest, public_plan: Any) -> bool:
    normalized = rt._normalize_text(request.message)
    if _has_documentary_retrieval_cues(request.message):
        return False
    multi_part_markers = (
        '?',
        ' alem disso ',
        ' além disso ',
        ' e tambem ',
        ' e também ',
        ' por outro lado ',
        ' ao mesmo tempo ',
    )
    marker_hits = sum(1 for marker in multi_part_markers if marker in f' {normalized} ')
    if marker_hits >= 2:
        return True
    if public_plan.conversation_act in {'comparative', 'curriculum', 'highlight'} and len(normalized.split()) >= 10:
        return True
    query_hints = rt._extract_public_entity_hints(request.message)
    return len(query_hints) >= 3 and len(normalized.split()) >= 10


async def _maybe_execute_llamaindex_subquestion_plan(
    *,
    analysis_message: str,
    tools: dict[str, QueryEngineTool],
    llm: Any | None,
    settings: Any | None = None,
) -> tuple[Response, str] | None:
    if llm is None:
        return None
    response_synthesizer = get_response_synthesizer(
        llm=llm,
        response_mode=ResponseMode.COMPACT,
        use_async=True,
        structured_answer_filtering=True,
    )
    try:
        query_engine = SubQuestionQueryEngine.from_defaults(
            query_engine_tools=list(tools.values()),
            llm=llm,
            response_synthesizer=response_synthesizer,
            use_async=True,
            verbose=False,
        )
        response = await _await_with_llamaindex_timeout(query_engine.aquery(analysis_message), settings=settings)
    except Exception:
        return None
    return response, 'llamaindex_subquestion_query_engine'


async def _maybe_execute_llamaindex_router_query_engine(
    *,
    analysis_message: str,
    tools: dict[str, QueryEngineTool],
    llm: Any | None,
    settings: Any | None = None,
) -> tuple[Response, tuple[str, ...]] | None:
    if llm is None:
        return None
    response_synthesizer = get_response_synthesizer(
        llm=llm,
        response_mode=ResponseMode.COMPACT,
        use_async=True,
        structured_answer_filtering=True,
    )
    selector = PydanticSingleSelector.from_defaults(llm=llm)
    query_engine = RouterQueryEngine.from_defaults(
        query_engine_tools=list(tools.values()),
        llm=llm,
        selector=selector,
        summarizer=response_synthesizer,
    )
    try:
        response = await _await_with_llamaindex_timeout(query_engine.aquery(analysis_message), settings=settings)
    except Exception:
        return None
    selected_names = _extract_router_selected_tool_names(response=response, tool_names=tuple(tools.keys()))
    return response, selected_names


def _build_public_retrieval_query_engine(
    *,
    settings: Any,
    preview: Any,
    original_message: str,
    llm: Any | None,
    prefer_citation_engine: bool,
    prefer_native_qdrant_autoretriever: bool,
) -> tuple[Any, PublicHybridCitationRetriever | None]:
    if llm is not None and prefer_native_qdrant_autoretriever and LLAMAINDEX_QDRANT_AVAILABLE:
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
                        MetadataInfo(name='version_label', type='str', description='Versao publicada do documento.'),
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
        ),
        retriever,
    )


async def _maybe_execute_llamaindex_function_agent(
    *,
    analysis_message: str,
    original_message: str,
    llm: Any | None,
    tools: dict[str, QueryEngineTool],
    settings: Any | None = None,
) -> tuple[str, tuple[str, ...], tuple[MessageResponseCitation, ...], str] | None:
    if llm is None or not _llamaindex_llm_supports_function_calls(llm):
        return None

    used_tool_names: list[str] = []
    captured_citations: list[MessageResponseCitation] = []
    captured_reason = 'llamaindex_function_agent'

    async def _call_tool(tool_name: str, query: str) -> str:
        nonlocal captured_reason
        tool = tools[tool_name]
        response = await _await_with_llamaindex_timeout(tool.query_engine.aquery(query), settings=settings)
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

    def _build_async_tool(tool_name: str):
        async def _tool(query: str) -> str:
            return await _call_tool(tool_name, query)

        return _tool

    function_tools = [
        FunctionTool.from_defaults(
            async_fn=_build_async_tool(tool_name),
            name=tool_name,
            description=tool.metadata.description,
        )
        for tool_name, tool in tools.items()
    ]
    agent = FunctionAgent(
        name='public_assistant',
        description='Resolve perguntas publicas da escola usando ferramentas grounding-first.',
        system_prompt=(
            'Voce responde em portugues do Brasil. Use somente as ferramentas disponiveis. '
            'Prefira a menor quantidade de ferramentas possivel. Nao invente fatos. '
            'Se usar evidencias documentais, preserve os sinais de citacao da propria ferramenta.'
        ),
        tools=function_tools,
        llm=llm,
        allow_parallel_tool_calls=False,
        verbose=False,
    )
    try:
        handler = agent.run(user_msg=analysis_message, max_iterations=5)
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
    selected_tool_names = tuple(dict.fromkeys(used_tool_names)) or ('llamaindex_function_agent',)
    return answer_text, selected_tool_names, tuple(captured_citations), 'llamaindex_function_agent'


async def _maybe_execute_llamaindex_agent_workflow(
    *,
    analysis_message: str,
    conversation_context: dict[str, Any] | None,
    llm: Any | None,
    tools: dict[str, QueryEngineTool],
    session_id: str,
    settings: Any | None = None,
) -> tuple[str, tuple[str, ...], tuple[MessageResponseCitation, ...], str] | None:
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


def _extract_router_selected_tool_names(*, response: Response, tool_names: tuple[str, ...]) -> tuple[str, ...]:
    metadata = response.metadata or {}
    selector_result = metadata.get('selector_result')
    if selector_result is None:
        return ('llamaindex_router_query_engine',)
    selected_indexes: list[int] = []
    if hasattr(selector_result, 'inds'):
        try:
            selected_indexes.extend(int(index) for index in selector_result.inds)
        except Exception:
            selected_indexes = []
    elif hasattr(selector_result, 'ind'):
        try:
            selected_indexes.append(int(selector_result.ind))
        except Exception:
            selected_indexes = []
    selected_names = [
        tool_names[index]
        for index in selected_indexes
        if 0 <= index < len(tool_names)
    ]
    if not selected_names:
        return ('llamaindex_router_query_engine',)
    return tuple(dict.fromkeys(selected_names))


async def maybe_execute_llamaindex_native_plan(
    *,
    request: MessageResponseRequest,
    settings: Any,
    plan: KernelPlan,
    engine_name: str,
    engine_mode: str,
    path_profile: PathExecutionProfile | None = None,
) -> KernelRunResult | None:
    restricted_doc_fast_path = await _maybe_execute_llamaindex_restricted_doc_fast_path(
        request=request,
        settings=settings,
        plan=plan,
        engine_name=engine_name,
        engine_mode=engine_mode,
    )
    if restricted_doc_fast_path is not None:
        return restricted_doc_fast_path
    effective_path_profile = path_profile or get_path_execution_profile(engine_name)
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
    recent_focus = rt._recent_conversation_focus(conversation_context)
    if recent_focus and recent_focus.get('kind') == 'visit' and rt._looks_like_visit_update_follow_up(request.message):
        return None
    actor_role = str((actor or {}).get('role_code', '') or '').strip().lower()
    teacher_authenticated = actor_role == 'teacher' or (
        getattr(request.user, 'authenticated', False)
        and getattr(getattr(request.user, 'role', None), 'value', '') == 'teacher'
    )
    teacher_scope_query = rt._is_teacher_scope_guidance_query(
        request.message,
        actor=actor,
        user=request.user,
        conversation_context=conversation_context,
    )
    should_fetch_teacher_schedule = rt._should_fetch_teacher_schedule(
        request.message,
        actor=actor,
        user=request.user,
        conversation_context=conversation_context,
    )
    if teacher_scope_query and teacher_authenticated:
        preview = plan.preview.model_copy(deep=True)
        if should_fetch_teacher_schedule:
            message_text = await rt._execute_teacher_protected_specialist(
                settings=settings,
                request=request,
                actor=actor or {},
                conversation_context=conversation_context,
            )
            preview.mode = OrchestrationMode.structured_tool
            preview.classification = IntentClassification(
                domain=QueryDomain.academic,
                access_tier=AccessTier.authenticated,
                confidence=0.99,
                reason='consulta protegida de grade docente atendida pelo runtime nativo do llamaindex',
            )
            preview.selected_tools = list(dict.fromkeys([*preview.selected_tools, 'get_teacher_schedule']))
            preview.needs_authentication = True
            execution_reason = 'llamaindex_teacher_schedule_direct'
            summary = 'Resposta deterministica grounded em service protegido de grade docente.'
        else:
            message_text = rt._compose_teacher_access_scope_answer(
                actor,
                school_name=str(((await rt._fetch_public_school_profile(settings=settings)) or {}).get('school_name', 'Colegio Horizonte')),
            )
            preview.mode = OrchestrationMode.structured_tool
            preview.classification = IntentClassification(
                domain=QueryDomain.academic,
                access_tier=AccessTier.authenticated,
                confidence=0.95,
                reason='orientacao de escopo docente atendida pelo runtime nativo do llamaindex',
            )
            preview.selected_tools = list(dict.fromkeys([*preview.selected_tools, 'get_actor_identity_context']))
            preview.needs_authentication = True
            execution_reason = 'llamaindex_teacher_scope_guidance'
            summary = 'Resposta deterministica sobre escopo docente e vinculacao da conta.'
        suggested_replies = rt._build_suggested_replies(
            request=request,
            preview=preview,
            actor=actor,
            school_profile=await rt._fetch_public_school_profile(settings=settings),
            conversation_context=conversation_context,
        )
        evidence_pack = build_structured_tool_evidence_pack(
            selected_tools=preview.selected_tools,
            slice_name=plan.slice_name,
            summary=summary,
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
            school_profile=await rt._fetch_public_school_profile(settings=settings),
            conversation_context=conversation_context,
            public_plan=None,
            request_message=request.message,
            message_text=message_text,
            citations_count=0,
            suggested_reply_count=len(suggested_replies),
            visual_asset_count=0,
            answer_verifier_valid=True,
            answer_verifier_reason='teacher deterministic native answer',
            answer_verifier_fallback_used=False,
            deterministic_fallback_available=True,
            answer_verifier_judge_used=False,
        )
        response = MessageResponse(
            message_text=rt._normalize_response_wording(message_text),
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
                'llamaindex:teacher',
                f'kernel:{plan.stack_name}',
            ],
            risk_flags=preview.risk_flags,
            reason=execution_reason,
        )
        reflection = KernelReflection(
            grounded=True,
            verifier_reason='teacher protected native path',
            fallback_used=False,
            answer_judge_used=False,
            notes=[
                f'route:{preview.mode.value}',
                f'slice:{plan.slice_name}',
                f'evidence:{evidence_pack.strategy}',
                *plan.plan_notes,
            ],
        )
        return KernelRunResult(
            plan=plan,
            reflection=reflection,
            response=response.model_dump(mode='json'),
        )
    if _looks_like_external_live_query(request.message):
        preview = plan.preview.model_copy(deep=True)
        preview.mode = OrchestrationMode.structured_tool
        preview.classification = IntentClassification(
            domain=QueryDomain.institution,
            access_tier=AccessTier.public,
            confidence=0.98,
            reason='consulta externa em tempo real encerrada deterministicamente antes do routing documental do llamaindex',
        )
        preview.selected_tools = []
        preview.needs_authentication = False
        message_text = rt._normalize_response_wording(_compose_external_live_query_answer(request.message) or '')
        evidence_pack = build_direct_answer_evidence_pack(
            summary='Pergunta externa reconhecida fora do escopo documental e de tempo real do assistente escolar.',
            supports=[],
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
            school_profile=await rt._fetch_public_school_profile(settings=settings),
            conversation_context=conversation_context,
            public_plan=None,
            request_message=request.message,
            message_text=message_text,
            citations_count=0,
            suggested_reply_count=0,
            visual_asset_count=0,
            answer_verifier_valid=True,
            answer_verifier_reason='llamaindex deterministic external-live guardrail',
            answer_verifier_fallback_used=False,
            deterministic_fallback_available=True,
            answer_verifier_judge_used=False,
        )
        response = MessageResponse(
            message_text=message_text,
            mode=preview.mode,
            classification=preview.classification,
            retrieval_backend=RetrievalBackend.none,
            selected_tools=[],
            citations=[],
            visual_assets=[],
            suggested_replies=[],
            calendar_events=[],
            evidence_pack=evidence_pack,
            needs_authentication=False,
            graph_path=[
                *preview.graph_path,
                'llamaindex:external',
                'llamaindex:external_live_guardrail',
                f'kernel:{plan.stack_name}',
            ],
            risk_flags=list(dict.fromkeys([*preview.risk_flags, 'external_live_data_unavailable'])),
            reason='llamaindex_external_live_guardrail',
        )
        reflection = KernelReflection(
            grounded=True,
            verifier_reason='external live query blocked before llamaindex retrieval',
            fallback_used=False,
            answer_judge_used=False,
            notes=[
                f'route:{preview.mode.value}',
                f'slice:{plan.slice_name}',
                'llamaindex:external_live_guardrail',
                f'evidence:{evidence_pack.strategy}',
                *plan.plan_notes,
            ],
        )
        return KernelRunResult(
            plan=plan,
            reflection=reflection,
            response=response.model_dump(mode='json'),
        )
    protected_records_fast_path = (
        request.telegram_chat_id is not None
        and actor is not None
        and (
            rt._is_access_scope_query(request.message)
            or rt._is_access_scope_repair_query(request.message, actor, conversation_context)
            or rt._mentions_personal_admin_status(request.message)
            or rt._detect_admin_attribute_request(request.message, conversation_context=conversation_context) is not None
            or rt._is_private_admin_follow_up(request.message, conversation_context)
            or bool({'get_administrative_status', 'get_student_administrative_status', 'get_actor_identity_context'} & set(plan.preview.selected_tools))
        )
    )
    if protected_records_fast_path:
        preview = plan.preview.model_copy(deep=True)
        if not {'get_administrative_status', 'get_student_administrative_status', 'get_actor_identity_context'} & set(preview.selected_tools):
            preview.selected_tools = [*preview.selected_tools, 'get_administrative_status', 'get_student_administrative_status']
        preview.mode = OrchestrationMode.structured_tool
        preview.classification = IntentClassification(
            domain=QueryDomain.institution,
            access_tier=AccessTier.authenticated,
            confidence=0.97,
            reason='follow-up administrativo ou de identidade resolvido antes do routing documental pesado do llamaindex',
        )
        preview.needs_authentication = True
        school_profile = await rt._fetch_public_school_profile(settings=settings)
        message_text = await rt._execute_protected_records_specialist(
            settings=settings,
            request=request,
            preview=preview,
            actor=actor,
            conversation_context=conversation_context,
        )
        evidence_pack = build_structured_tool_evidence_pack(
            selected_tools=preview.selected_tools,
            slice_name=plan.slice_name,
            summary='Consulta protegida administrativa ou de identidade resolvida deterministicamente antes do routing pesado do LlamaIndex.',
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
            answer_verifier_reason='llamaindex protected records deterministic fast path',
            answer_verifier_fallback_used=False,
            deterministic_fallback_available=True,
            answer_verifier_judge_used=False,
        )
        response = MessageResponse(
            message_text=rt._normalize_response_wording(message_text),
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
                'llamaindex:protected',
                'llamaindex:protected_records_fast_path',
                f'kernel:{plan.stack_name}',
            ],
            risk_flags=preview.risk_flags,
            reason='llamaindex_protected_records_fast_path',
        )
        reflection = KernelReflection(
            grounded=True,
            verifier_reason='protected records deterministic fast path',
            fallback_used=False,
            answer_judge_used=False,
            notes=[
                f'route:{preview.mode.value}',
                f'slice:{plan.slice_name}',
                'llamaindex:protected_records_fast_path',
                f'evidence:{evidence_pack.strategy}',
                *plan.plan_notes,
            ],
        )
        return KernelRunResult(
            plan=plan,
            reflection=reflection,
            response=response.model_dump(mode='json'),
        )
    analysis_message = rt._build_analysis_message(request.message, conversation_context_bundle)
    school_profile = await rt._fetch_public_school_profile(settings=settings)
    if not isinstance(school_profile, dict):
        return None
    if rt._is_public_timeline_query(request.message):
        timeline = await rt._fetch_public_timeline(settings=settings)
        if isinstance(timeline, dict):
            school_profile.setdefault('school_name', timeline.get('school_name'))
            school_profile['public_timeline'] = timeline.get('entries', [])
    if rt._is_public_calendar_event_query(request.message) or rt._is_public_calendar_visibility_query(request.message):
        calendar_events = await rt._fetch_public_calendar_events(settings=settings)
        if calendar_events:
            school_profile['public_calendar_events'] = calendar_events
    early_public_canonical_lane = (
        match_public_canonical_lane(analysis_message)
        or match_public_canonical_lane(request.message)
    )
    fast_public_channel_answer = rt._try_public_channel_fast_answer(
        message=request.message,
        profile=school_profile,
    )
    if fast_public_channel_answer and not early_public_canonical_lane:
        preview = plan.preview.model_copy(deep=True)
        preview.mode = OrchestrationMode.structured_tool
        preview.classification = IntentClassification(
            domain=QueryDomain.institution,
            access_tier=AccessTier.public,
            confidence=0.98,
            reason='consulta publica resolvida deterministicamente antes do routing pesado do llamaindex',
        )
        preview.selected_tools = list(dict.fromkeys([*preview.selected_tools, 'get_public_school_profile']))
        preview.needs_authentication = False
        evidence_pack = build_structured_tool_evidence_pack(
            selected_tools=preview.selected_tools,
            slice_name=plan.slice_name,
            summary='Resposta publica deterministica servida antes do routing documental pesado do LlamaIndex.',
        )
        suggested_replies = rt._build_suggested_replies(
            request=request,
            preview=preview,
            actor=actor,
            school_profile=school_profile,
            conversation_context=conversation_context,
        )
        message_text = rt._normalize_response_wording(fast_public_channel_answer)
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
            answer_verifier_reason='llamaindex deterministic public fast path',
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
            visual_assets=[],
            suggested_replies=suggested_replies,
            calendar_events=[],
            evidence_pack=evidence_pack,
            needs_authentication=preview.needs_authentication,
            graph_path=[
                *preview.graph_path,
                'llamaindex:public',
                'llamaindex:contextual_public_direct',
                f'kernel:{plan.stack_name}',
            ],
            risk_flags=preview.risk_flags,
            reason='contextual_public_direct_answer',
        )
        reflection = KernelReflection(
            grounded=True,
            verifier_reason='llamaindex deterministic public fast path',
            fallback_used=False,
            answer_judge_used=False,
            notes=[
                f'route:{preview.mode.value}',
                f'slice:{plan.slice_name}',
                'llamaindex:contextual_public_direct',
                f'evidence:{evidence_pack.strategy}',
                *plan.plan_notes,
            ],
        )
        return KernelRunResult(
            plan=plan,
            reflection=reflection,
            response=response.model_dump(mode='json'),
        )

    orphan_workflow_follow_up = rt._compose_orphan_workflow_follow_up_answer(
        request.message,
        conversation_context,
    )
    if orphan_workflow_follow_up:
        preview = plan.preview.model_copy(deep=True)
        preview.mode = OrchestrationMode.structured_tool
        preview.classification = IntentClassification(
            domain=QueryDomain.support,
            access_tier=AccessTier.public if not request.user.authenticated else AccessTier.authenticated,
            confidence=0.95,
            reason='follow-up de workflow resgatado do contexto antes do roteamento nativo do llamaindex',
        )
        preview.selected_tools = list(dict.fromkeys([*preview.selected_tools, 'get_workflow_status']))
        evidence_pack = build_structured_tool_evidence_pack(
            selected_tools=preview.selected_tools,
            slice_name=plan.slice_name,
            summary='Follow-up de workflow recuperado do contexto conversacional.',
        )
        response = MessageResponse(
            message_text=orphan_workflow_follow_up,
            mode=preview.mode,
            classification=preview.classification,
            retrieval_backend=RetrievalBackend.none,
            selected_tools=preview.selected_tools,
            citations=[],
            visual_assets=[],
            suggested_replies=[],
            calendar_events=[],
            evidence_pack=evidence_pack,
            needs_authentication=False,
            graph_path=[
                *preview.graph_path,
                'llamaindex:workflow',
                'llamaindex:orphan_workflow_followup',
                f'kernel:{plan.stack_name}',
            ],
            risk_flags=preview.risk_flags,
            reason='llamaindex_orphan_workflow_followup',
        )
        reflection = KernelReflection(
            grounded=True,
            verifier_reason='follow-up de workflow resgatado deterministicamente do contexto',
            fallback_used=False,
            answer_judge_used=False,
            notes=[
                f'route:{preview.mode.value}',
                f'slice:{plan.slice_name}',
                'llamaindex_tool:get_workflow_status',
                f'evidence:{evidence_pack.strategy}',
                *plan.plan_notes,
            ],
        )
        return KernelRunResult(
            plan=plan,
            reflection=reflection,
            response=response.model_dump(mode='json'),
        )

    public_canonical_lane = match_public_canonical_lane(analysis_message) or match_public_canonical_lane(request.message)
    public_canonical_answer = (
        compose_public_canonical_lane_answer(public_canonical_lane, profile=school_profile)
        if public_canonical_lane
        else None
    )
    if public_canonical_answer:
        preview = plan.preview.model_copy(deep=True)
        preview.mode = OrchestrationMode.structured_tool
        preview.classification = _public_classification_for_act(
            'support_routing',
            'pergunta publica canonica resolvida deterministicamente antes do roteador nativo do llamaindex',
        )
        preview.selected_tools = list(dict.fromkeys([*preview.selected_tools, 'get_public_school_profile']))
        evidence_pack = build_structured_tool_evidence_pack(
            selected_tools=preview.selected_tools,
            slice_name=plan.slice_name,
            summary='Resposta publica canonica resolvida por lane deterministica compartilhada.',
        )
        response = MessageResponse(
            message_text=public_canonical_answer,
            mode=preview.mode,
            classification=preview.classification,
            retrieval_backend=RetrievalBackend.none,
            selected_tools=preview.selected_tools,
            citations=[],
            visual_assets=[],
            suggested_replies=[],
            calendar_events=[],
            evidence_pack=evidence_pack,
            needs_authentication=False,
            graph_path=[
                *preview.graph_path,
                'llamaindex:public',
                'llamaindex:canonical_lane',
                public_canonical_lane,
                f'kernel:{plan.stack_name}',
            ],
            risk_flags=preview.risk_flags,
            reason=f'llamaindex_public_canonical_lane:{public_canonical_lane}',
        )
        reflection = KernelReflection(
            grounded=True,
            verifier_reason='llamaindex deterministic canonical public lane',
            fallback_used=False,
            answer_judge_used=False,
            notes=[
                f'route:{preview.mode.value}',
                f'slice:{plan.slice_name}',
                f'canonical_lane:{public_canonical_lane}',
                f'evidence:{evidence_pack.strategy}',
                *plan.plan_notes,
            ],
        )
        return KernelRunResult(
            plan=plan,
            reflection=reflection,
            response=response.model_dump(mode='json'),
        )

    llamaindex_llm = _build_llamaindex_llm(settings=settings)
    llm_native_public_decision = None
    if _should_run_llamaindex_native_public_resolver(request=request, plan=plan):
        llm_native_public_decision = await _resolve_llamaindex_native_public_decision(
            llm=llamaindex_llm,
            settings=settings,
            message=request.message,
            preview=plan.preview,
            school_profile=school_profile,
            conversation_context=conversation_context,
        )
    heuristic_public_decision = _heuristic_llamaindex_native_public_decision(
        message=request.message,
        conversation_context=conversation_context,
    )
    native_public_decision = _merge_llamaindex_native_public_decisions(
        llm_decision=llm_native_public_decision,
        heuristic_decision=heuristic_public_decision,
    )

    public_plan = await rt._resolve_public_institution_plan(
        settings=settings,
        message=request.message,
        preview=plan.preview,
        conversation_context=conversation_context,
        school_profile=school_profile,
    )
    if native_public_decision is not None:
        public_plan = _native_public_plan_from_decision(
            message=request.message,
            decision=native_public_decision,
            conversation_context=conversation_context,
            school_profile=school_profile,
        )
    elif _looks_like_llamaindex_value_prop_query(request.message):
        native_public_decision = LlamaIndexNativePublicDecision(
            conversation_act='highlight',
            answer_mode='documentary',
            required_tools=['get_public_school_profile'],
            use_conversation_context=True,
        )
        public_plan = _native_public_plan_from_decision(
            message=request.message,
            decision=native_public_decision,
            conversation_context=conversation_context,
            school_profile=school_profile,
        )
    preview = plan.preview.model_copy(deep=True)
    preview.selected_tools = list(public_plan.required_tools)
    if (
        preview.mode is OrchestrationMode.clarify
        and native_public_decision is not None
        and native_public_decision.answer_mode != 'clarify'
    ):
        preview.mode = OrchestrationMode.structured_tool
        preview.reason = 'llamaindex_native_public_resolver'
    if native_public_decision is not None and native_public_decision.answer_mode != 'clarify':
        preview.classification = _public_classification_for_act(
            public_plan.conversation_act,
            'roteamento publico nativo do llamaindex resolveu a pergunta sem clarificacao',
        )
        preview.needs_authentication = False
    effective_analysis_message = _build_llamaindex_analysis_query(
        original_message=request.message,
        analysis_message=analysis_message,
        native_decision=native_public_decision,
        public_plan=public_plan,
    )
    effective_retrieval_query = _build_llamaindex_retrieval_query(
        original_message=request.message,
        native_decision=native_public_decision,
        public_plan=public_plan,
    )
    public_canonical_lane = (
        match_public_canonical_lane(effective_analysis_message)
        or match_public_canonical_lane(request.message)
    )
    public_canonical_answer = (
        compose_public_canonical_lane_answer(public_canonical_lane, profile=school_profile)
        if public_canonical_lane
        else None
    )

    descriptions = _tool_descriptions(public_plan)
    native_public_unpublished_answer = _native_llamaindex_public_unpublished_answer(
        decision=native_public_decision,
        message=request.message,
        school_profile=school_profile,
    )
    retrieval_query_engine, citation_retriever = _build_public_retrieval_query_engine(
        settings=settings,
        preview=preview,
        original_message=request.message,
        llm=llamaindex_llm,
        prefer_citation_engine=effective_path_profile.prefer_native_llamaindex_citation_engine,
        prefer_native_qdrant_autoretriever=effective_path_profile.prefer_native_llamaindex_qdrant_autoretriever,
    )
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
            query_engine=retrieval_query_engine,
            name='public_retrieval',
            description=descriptions['public_retrieval'],
        ),
    }
    selected_tool_names: tuple[str, ...] = ('unknown',)
    subquestion_result: tuple[Response, str] | None = None
    router_result: tuple[Response, tuple[str, ...]] | None = None
    tool_response: Response | None = None
    answer_text = ''
    citations: list[MessageResponseCitation] = []
    retrieval_backend = RetrievalBackend.none
    execution_reason = 'llamaindex_native_public_router'
    documentary_direct_retrieval = _should_force_llamaindex_documentary_retrieval(
        message=request.message,
        public_plan=public_plan,
        native_decision=native_public_decision,
    )

    agent_workflow_result = None
    function_agent_result = None
    if public_canonical_answer:
        preview.mode = OrchestrationMode.structured_tool
        preview.reason = f'llamaindex_public_canonical_lane:{public_canonical_lane}'
        preview.classification = _public_classification_for_act(
            public_plan.conversation_act,
            'pergunta publica canonica resolvida por lane deterministica antes do roteador nativo',
        )
        preview.needs_authentication = False
        preview.selected_tools = list(dict.fromkeys([*preview.selected_tools, 'get_public_school_profile']))
        answer_text = public_canonical_answer
        selected_tool_names = ('public_profile',)
        execution_reason = preview.reason
    elif native_public_unpublished_answer:
        preview.mode = OrchestrationMode.structured_tool
        preview.reason = 'llamaindex_public_unpublished_fact'
        preview.classification = _public_classification_for_act(
            public_plan.conversation_act,
            'a pergunta e publica e valida, mas o dado especifico nao esta publicado',
        )
        preview.needs_authentication = False
        preview.selected_tools = list(dict.fromkeys([*preview.selected_tools, 'get_public_school_profile']))
        answer_text = native_public_unpublished_answer
        selected_tool_names = ('public_profile',)
        execution_reason = 'llamaindex_public_unpublished_fact'
    elif native_public_decision is not None and native_public_decision.answer_mode == 'profile':
        direct_profile_answer = rt._compose_public_profile_answer(
            school_profile,
            request.message,
            actor=actor,
            original_message=request.message,
            conversation_context=conversation_context,
            semantic_plan=public_plan,
        )
        direct_profile_answer = str(direct_profile_answer or '').strip()
        if direct_profile_answer and not direct_profile_answer.startswith('Ainda nao encontrei evidencia publica suficiente'):
            preview.mode = OrchestrationMode.structured_tool
            preview.reason = 'llamaindex_public_profile_fast_path'
            preview.needs_authentication = False
            preview.selected_tools = list(dict.fromkeys([*preview.selected_tools, 'get_public_school_profile']))
            answer_text = direct_profile_answer
            selected_tool_names = ('public_profile',)
            execution_reason = 'llamaindex_public_profile_fast_path'
        else:
            selected_tool_names = ('public_profile',)
            try:
                tool_response = await _await_with_llamaindex_timeout(
                    tools['public_profile'].query_engine.aquery(effective_analysis_message),
                    settings=settings,
                )
            except Exception:
                return None
    elif documentary_direct_retrieval:
        selected_tool_names = ('public_retrieval',)
        try:
            tool_response = await _await_with_llamaindex_timeout(
                tools['public_retrieval'].query_engine.aquery(effective_retrieval_query),
                settings=settings,
            )
        except Exception:
            return None
    elif (
        effective_path_profile.prefer_native_llamaindex_function_agent
        and _should_use_llamaindex_function_agent(request=request, public_plan=public_plan)
    ):
        agent_workflow_result = await _maybe_execute_llamaindex_agent_workflow(
            analysis_message=effective_analysis_message,
            conversation_context=conversation_context,
            llm=llamaindex_llm,
            tools=tools,
            session_id=effective_conversation_id,
            settings=settings,
        )
    if agent_workflow_result is not None:
        answer_text, selected_tool_names, workflow_citations, execution_reason = agent_workflow_result
        citations = list(workflow_citations)
        retrieval_backend = RetrievalBackend.qdrant_hybrid if citations else RetrievalBackend.none
    elif (
        effective_path_profile.prefer_native_llamaindex_function_agent
        and _should_use_llamaindex_function_agent(request=request, public_plan=public_plan)
    ):
        function_agent_result = await _maybe_execute_llamaindex_function_agent(
            analysis_message=effective_analysis_message,
            original_message=request.message,
            llm=llamaindex_llm,
            tools=tools,
            settings=settings,
        )
    if native_public_unpublished_answer:
        retrieval_backend = RetrievalBackend.none
    elif documentary_direct_retrieval:
        execution_reason = 'llamaindex_public_direct_retrieval'
    elif function_agent_result is not None:
        answer_text, selected_tool_names, function_agent_citations, execution_reason = function_agent_result
        citations = list(function_agent_citations)
        retrieval_backend = RetrievalBackend.qdrant_hybrid if citations else RetrievalBackend.none
    elif tool_response is None:
        if effective_path_profile.prefer_native_llamaindex_subquestions and _should_use_llamaindex_native_subquestions(
            request=request,
            public_plan=public_plan,
        ):
            subquestion_result = await _maybe_execute_llamaindex_subquestion_plan(
                analysis_message=effective_analysis_message,
                tools=tools,
                llm=llamaindex_llm,
                settings=settings,
            )
        if subquestion_result is not None:
            tool_response, selected_tool_name = subquestion_result
            selected_tool_names = (selected_tool_name,)
            execution_reason = 'llamaindex_subquestion_query_engine'
        elif effective_path_profile.prefer_native_llamaindex_selector and llamaindex_llm is not None:
            router_result = await _maybe_execute_llamaindex_router_query_engine(
                analysis_message=effective_analysis_message,
                tools=tools,
                llm=llamaindex_llm,
                settings=settings,
            )
            if router_result is not None:
                tool_response, selected_tool_names = router_result
                execution_reason = 'llamaindex_router_query_engine'
        else:
            selected_tool = _route_public_query_tool(
                request=request,
                plan=public_plan,
                tools=tools,
                embedding_model=settings.document_embedding_model,
                llm=llamaindex_llm if effective_path_profile.prefer_native_llamaindex_selector else None,
            )
            selected_tool_name = selected_tool.metadata.name
            selected_tool_names = (selected_tool_name,)
            try:
                tool_response = await _await_with_llamaindex_timeout(
                    selected_tool.query_engine.aquery(
                        effective_retrieval_query if selected_tool_name == 'public_retrieval' else effective_analysis_message
                    ),
                    settings=settings,
                )
            except Exception:
                return None
    if tool_response is not None:
        answer_text = str(getattr(tool_response, 'response', '') or str(tool_response)).strip()
        citations = list(_extract_response_citations(tool_response))
        if not citations and citation_retriever is not None:
            citations = list(citation_retriever.latest_citations())
        retrieval_backend = RetrievalBackend(
            str((tool_response.metadata or {}).get('retrieval_backend', RetrievalBackend.none.value))
        )
        execution_reason = str((tool_response.metadata or {}).get('reason', execution_reason))
        if citation_retriever is not None and 'public_retrieval' in selected_tool_names:
            retrieval_backend = RetrievalBackend.qdrant_hybrid
            if execution_reason in {'llamaindex_native_public_router', 'llamaindex_router_query_engine'}:
                execution_reason = 'llamaindex_public_citation_query_engine'
    low_confidence_documentary_answer = (
        answer_text.startswith('Ainda nao encontrei evidencia publica suficiente')
        and public_plan.conversation_act in {'highlight', 'pricing', 'comparative', 'curriculum'}
    )
    if low_confidence_documentary_answer:
        fallback_text = rt._compose_public_profile_answer(
            school_profile,
            request.message,
            actor=actor,
            original_message=request.message,
            conversation_context=conversation_context,
            semantic_plan=public_plan,
        )
        fallback_text = str(fallback_text or '').strip()
        if fallback_text and not fallback_text.startswith('Ainda nao encontrei evidencia publica suficiente'):
            answer_text = fallback_text
            selected_tool_names = tuple(dict.fromkeys([*selected_tool_names, 'public_profile']))
            citations = []
            retrieval_backend = RetrievalBackend.none
            execution_reason = 'llamaindex_public_retrieval_profile_fallback'
    if not answer_text:
        return None

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
    if (
        not verification.valid
        and _should_trust_llamaindex_native_deterministic_answer(
            native_decision=native_public_decision,
            selected_tool_names=selected_tool_names,
        )
    ):
        verification = rt.AnswerVerificationResult(
            valid=True,
            reason='llamaindex_native_deterministic_answer',
        )
        semantic_judge_used = False
    if not verification.valid:
        return None

    if citations:
        sources = rt._render_source_lines(citations)
        if sources and sources not in message_text:
            message_text = f'{message_text}\n\n{sources}'
    message_text = rt._normalize_response_wording(message_text)
    evidence_pack: MessageEvidencePack
    if citations:
        evidence_pack = build_retrieval_evidence_pack(
            citations=citations,
            selected_tools=selected_tool_names,
            retrieval_backend=retrieval_backend,
            summary='Resposta grounded em routing nativo do LlamaIndex com evidencias citadas.',
        )
    else:
        evidence_pack = build_structured_tool_evidence_pack(
            selected_tools=selected_tool_names,
            slice_name=plan.slice_name,
            summary='Resposta grounded em roteamento nativo do LlamaIndex sobre ferramentas publicas.',
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
            'llamaindex_selected_tool': ','.join(selected_tool_names),
            'llamaindex_execution_reason': execution_reason,
            'llamaindex_citation_engine_used': bool(citation_retriever),
            'llamaindex_function_agent_used': execution_reason == 'llamaindex_function_agent',
            'llamaindex_evidence_support_count': evidence_pack.support_count,
        },
    )

    selected_tools = list(
        dict.fromkeys(
            [
                *preview.selected_tools,
                *list(((tool_response.metadata or {}) if tool_response is not None else {}).get('selected_tools', [])),
                'llamaindex_selector_router',
                *selected_tool_names,
            ]
        )
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
        evidence_pack=evidence_pack,
        needs_authentication=preview.needs_authentication,
        graph_path=[
            *preview.graph_path,
            'llamaindex:workflow',
            f'llamaindex:{execution_reason}',
            *[f'llamaindex:tool:{tool_name}' for tool_name in selected_tool_names],
            f'kernel:{plan.stack_name}',
        ],
        risk_flags=preview.risk_flags,
        reason=execution_reason,
    )
    reflection = KernelReflection(
        grounded=verification.valid,
        verifier_reason=verification.reason,
        fallback_used=False,
        answer_judge_used=semantic_judge_used,
        notes=[
            f'route:{preview.mode.value}',
            f'slice:{plan.slice_name}',
            f'llamaindex_tool:{",".join(selected_tool_names)}',
            f'evidence:{evidence_pack.strategy}',
            *plan.plan_notes,
        ],
    )
    return KernelRunResult(
        plan=plan,
        reflection=reflection,
        response=response.model_dump(mode='json'),
    )
