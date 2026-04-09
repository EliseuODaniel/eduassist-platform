from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass
from functools import lru_cache
from time import monotonic
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
from llama_index.core.postprocessor import LongContextReorder, SentenceEmbeddingOptimizer
from llama_index.core.prompts import PromptTemplate
from llama_index.core.query_engine import (
    CitationQueryEngine,
    CustomQueryEngine,
    RouterQueryEngine,
    SubQuestionQueryEngine,
)
from llama_index.core.response_synthesizers import get_response_synthesizer
from llama_index.core.response_synthesizers.type import ResponseMode
from llama_index.core.retrievers import RecursiveRetriever
from llama_index.core.schema import IndexNode, NodeWithScore, QueryBundle, TextNode
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
from qdrant_client import AsyncQdrantClient, QdrantClient, models

from . import runtime as rt
from .llamaindex_kernel import KernelPlan, KernelReflection, KernelRunResult
from .candidate_builder import build_response_candidate
from .candidate_chooser import choose_best_candidate
from .entity_resolution import resolve_entity_hints
from .evidence_pack import (
    build_direct_answer_evidence_pack,
    build_retrieval_evidence_pack,
    build_structured_tool_evidence_pack,
)
from .final_polish_policy import build_final_polish_decision
from .llamaindex_kernel_runtime import (
    _maybe_contextual_public_direct_answer,
    _maybe_hypothetical_public_pricing_answer,
)
from .llamaindex_public_intent_registry import (
    LLAMAINDEX_PUBLIC_INTENT_RULES,
    LlamaIndexPublicIntentRule,
)
from .llamaindex_local_llm import (
    polish_llamaindex_with_provider,
    revise_llamaindex_with_provider,
    verify_llamaindex_answer_against_contract,
)
from .model_cache import configure_model_cache_env
from .llm_provider import _google_model_candidates
from .models import (
    AccessTier,
    IntentClassification,
    MessageEvidenceSupport,
    MessageEvidencePack,
    MessageResponse,
    MessageResponseCitation,
    MessageResponseRequest,
    OrchestrationMode,
    QueryDomain,
    RetrievalBackend,
)
from .path_profiles import PathExecutionProfile, get_path_execution_profile
from .llamaindex_public_knowledge import compose_public_canonical_lane_answer, match_public_canonical_lane
from .llamaindex_public_known_unknowns import (
    compose_public_known_unknown_answer,
    detect_public_known_unknown_key,
)
from .response_cache import get_cached_public_response, store_cached_public_response
from .llamaindex_retrieval import (
    can_read_restricted_documents,
    compose_restricted_document_grounded_answer_for_query,
    compose_restricted_document_no_match_answer,
    get_retrieval_service,
    looks_like_restricted_document_query,
    select_relevant_restricted_hits,
)
from .llamaindex_retrieval_probe import build_public_evidence_probe
from .serving_policy import LoadSnapshot, build_public_serving_policy
from .serving_telemetry import get_stack_telemetry_snapshot, record_stack_outcome

configure_model_cache_env()

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


@dataclass(frozen=True)
class LlamaIndexEarlyPublicAnswer:
    answer_text: str
    reason: str
    canonical_lane: str | None = None


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


def _llamaindex_execution_llm_stages(*, execution_reason: str, semantic_judge_used: bool) -> list[str]:
    stages: list[str] = []
    llm_execution_prefixes = (
        'llamaindex_public_',
        'llamaindex_router_',
        'llamaindex_subquestion_',
        'llamaindex_function_agent',
    )
    explicit_deterministic_reasons = {
        'llamaindex deterministic public fast path',
        'llamaindex deterministic external-live guardrail',
        'llamaindex protected records deterministic fast path',
        'llamaindex restricted-doc retrieval fast path',
        'teacher deterministic native answer',
    }
    normalized = str(execution_reason or '').strip()
    if normalized and normalized not in explicit_deterministic_reasons:
        if normalized.startswith(llm_execution_prefixes) or normalized in {
            'llamaindex_public_profile',
            'llamaindex_public_direct_retrieval',
            'llamaindex_public_citation_query_engine',
        }:
            stages.append('answer_composition')
    if semantic_judge_used:
        stages.append('answer_verifier_judge')
    return stages


def _should_avoid_llamaindex_public_profile_fast_path(
    *,
    message: str,
    public_plan: Any,
    native_decision: LlamaIndexNativePublicDecision | None,
) -> bool:
    if match_public_canonical_lane(message):
        return False
    if rt._looks_like_public_documentary_open_query(message):  # type: ignore[attr-defined]
        return True
    if _has_documentary_retrieval_cues(message) or _looks_like_open_documentary_bundle_query(message):
        return True
    if rt._looks_like_public_explanatory_bundle_query(message):  # type: ignore[attr-defined]
        return True
    if native_decision is not None and native_decision.answer_mode == 'documentary':
        return True
    return bool(public_plan.conversation_act in {'comparative', 'highlight', 'curriculum', 'features'})


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
        effective_conversation_id = rt._effective_conversation_id(request)
        conversation_context_bundle = await rt._fetch_conversation_context(
            settings=settings,
            conversation_external_id=effective_conversation_id,
            channel=request.channel.value,
        )
        conversation_context = rt._conversation_context_payload(conversation_context_bundle)
        preview = plan.preview.model_copy(deep=True)
        preview.mode = OrchestrationMode.deny
        preview.classification = IntentClassification(
            domain=QueryDomain.institution,
            access_tier=AccessTier.public,
            confidence=0.99,
            reason='consulta a documento interno negada por falta de acesso explicito',
        )
        preview.selected_tools = list(dict.fromkeys([*preview.selected_tools, 'search_documents']))
        school_profile = await rt._fetch_public_school_profile(settings=settings)
        message_text = rt._compose_deterministic_answer(
            request_message=request.message,
            preview=preview,
            retrieval_hits=[],
            citations=[],
            calendar_events=[],
            query_hints=set(),
        )
        evidence_pack = build_direct_answer_evidence_pack(
            strategy='deny',
            summary='Resposta bloqueada por regra de acesso antes do retrieval restrito do LlamaIndex.',
            supports=[
                MessageEvidenceSupport(
                    kind='guardrail',
                    label='restricted_documents',
                    detail='consulta a documento interno sem autorizacao',
                )
            ],
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
            answer_verifier_reason='restricted_document_access_denied',
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
            suggested_replies=suggested_replies,
            evidence_pack=evidence_pack,
            needs_authentication=False,
            graph_path=[*preview.graph_path, 'llamaindex:restricted_doc_deny'],
            risk_flags=preview.risk_flags,
            reason='llamaindex_restricted_doc_access_deny',
            used_llm=False,
            llm_stages=[],
        )
        return KernelRunResult(
            plan=plan,
            reflection=KernelReflection(
                grounded=True,
                verifier_reason='restricted_document_access_denied',
                fallback_used=False,
                answer_judge_used=False,
                notes=[
                    'route:deny',
                    f'slice:{plan.slice_name}',
                    'evidence:deny',
                ],
            ),
            response=response.model_dump(mode='json'),
        )
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


_LLAMAINDEX_NATIVE_PUBLIC_FALLBACK_ROUTER_PROMPT = PromptTemplate(
    """
Voce e um fallback semantico para perguntas publicas de uma escola.
As regras deterministicas do runtime nao conseguiram fechar a decisao com confianca suficiente.
Sua tarefa e produzir uma decisao estruturada, estrita e minima para o runtime.

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
- Use esta decisao apenas para desambiguar o que o roteamento deterministico ainda nao resolveu.
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

Resumo da melhor pista deterministica encontrada:
{deterministic_summary}

Contexto recente:
{conversation_context}

Resumo curado do que esta publicado:
{profile_summary}
""".strip()
)


_LLAMAINDEX_NATIVE_UNPUBLISHED_ROUTE_MAP: dict[str, dict[str, str]] = {
    'minimum_age': {
        'conversation_act': 'segments',
        'requested_attribute': 'minimum_age',
        'requested_channel': 'admissions',
        'focus_hint': 'idade minima exata nao publicada; orientar por segmento e canal de admissions',
    },
    'classroom_count': {
        'conversation_act': 'features',
        'requested_attribute': 'classroom_count',
        'focus_hint': 'quantidade de salas de aula nao publicada oficialmente',
    },
    'total_students': {
        'conversation_act': 'kpi',
        'requested_attribute': 'student_count',
        'focus_hint': 'total de alunos nao publicado oficialmente',
    },
    'total_teachers': {
        'conversation_act': 'teacher_directory',
        'requested_attribute': 'teacher_count',
        'focus_hint': 'quantidade total de professores nao publicada oficialmente',
    },
    'library_book_count': {
        'conversation_act': 'features',
        'requested_attribute': 'library_collection_size',
        'focus_hint': 'quantidade total de livros da biblioteca nao publicada oficialmente',
    },
    'cafeteria_menu': {
        'conversation_act': 'features',
        'requested_attribute': 'cafeteria_menu',
        'requested_channel': 'secretaria',
        'focus_hint': 'cantina existe, mas o cardapio detalhado nao esta publicado oficialmente',
    },
}


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


@lru_cache(maxsize=4)
def _qdrant_client(*, qdrant_url: str) -> QdrantClient:
    return QdrantClient(url=qdrant_url)


def _resolve_llamaindex_qdrant_collection(settings: Any) -> str:
    preferred = str(getattr(settings, 'llamaindex_qdrant_documents_collection', '') or '').strip()
    fallback = str(getattr(settings, 'qdrant_documents_collection', 'school_documents'))
    if preferred and _qdrant_collection_exists(qdrant_url=str(settings.qdrant_url), collection_name=preferred):
        return preferred
    return fallback


def _resolve_llamaindex_qdrant_summary_collection(settings: Any) -> str | None:
    preferred = str(getattr(settings, 'llamaindex_qdrant_document_summaries_collection', '') or '').strip()
    fallback = str(getattr(settings, 'qdrant_document_summaries_collection', 'school_document_summaries') or '').strip()
    qdrant_url = str(settings.qdrant_url)
    if preferred and _qdrant_collection_exists(qdrant_url=qdrant_url, collection_name=preferred):
        return preferred
    if fallback and _qdrant_collection_exists(qdrant_url=qdrant_url, collection_name=fallback):
        return fallback
    return None


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


async def _resolve_early_llamaindex_public_answer(
    *,
    request: MessageResponseRequest,
    plan: KernelPlan,
    settings: Any,
    school_profile: dict[str, Any] | None,
    conversation_context: dict[str, Any] | None,
) -> LlamaIndexEarlyPublicAnswer | None:
    if not isinstance(school_profile, dict):
        return None

    canonical_lane = match_public_canonical_lane(request.message)
    if canonical_lane:
        canonical_answer = compose_public_canonical_lane_answer(canonical_lane, profile=school_profile)
        if canonical_answer:
            return LlamaIndexEarlyPublicAnswer(
                answer_text=canonical_answer,
                reason='canonical_lane',
                canonical_lane=canonical_lane,
            )

    boundary_answer = rt._compose_contextual_public_boundary_answer(
        message=request.message,
        conversation_context=conversation_context,
        profile=school_profile,
    )
    if boundary_answer:
        return LlamaIndexEarlyPublicAnswer(
            answer_text=boundary_answer,
            reason='contextual_boundary',
        )

    if rt._is_explicit_public_pricing_projection_query(
        request.message,
        conversation_context=conversation_context,
    ):
        pricing_plan = rt._build_public_institution_plan(
            request.message,
            list(plan.preview.selected_tools),
            semantic_plan=None,
            conversation_context=conversation_context,
            school_profile=school_profile,
        )
        if pricing_plan.conversation_act != 'pricing':
            pricing_plan = rt.replace(
                pricing_plan,
                conversation_act='pricing',
                secondary_acts=tuple(act for act in pricing_plan.secondary_acts if act != 'pricing'),
            )
        pricing_projection_answer = rt._compose_public_profile_answer(
            school_profile,
            request.message,
            actor=None,
            original_message=request.message,
            conversation_context=conversation_context,
            semantic_plan=pricing_plan,
        )
        if pricing_projection_answer and 'R$' in pricing_projection_answer:
            return LlamaIndexEarlyPublicAnswer(
                answer_text=pricing_projection_answer,
                reason='pricing_projection',
            )

    contextual_direct_answer = await _maybe_contextual_public_direct_answer(
        request=request,
        analysis_message=request.message,
        preview=plan.preview,
        settings=settings,
        school_profile=school_profile,
        conversation_context=conversation_context,
    )
    if contextual_direct_answer:
        return LlamaIndexEarlyPublicAnswer(
            answer_text=contextual_direct_answer,
            reason='contextual_direct',
        )

    return None


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
        search = _run_public_hybrid_search(
            retrieval_service=retrieval_service,
            query=query_str,
            settings=self.settings,
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
        use_document_groups = bool(search.document_groups) and len(retrieval_hits) == len(search.hits)
        source_search = search if use_document_groups else search.model_copy(update={'hits': retrieval_hits, 'document_groups': []})
        source_nodes = _build_public_retrieval_source_nodes(search=source_search)
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

    def latest_query_plan(self) -> Any | None:
        return getattr(self, '_latest_query_plan', None)

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
        search = _run_public_hybrid_search(
            retrieval_service=retrieval_service,
            query=query_str,
            settings=self._settings,
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
        if not retrieval_hits:
            return []
        if bool(getattr(self._settings, 'llamaindex_native_recursive_retriever_enabled', True)):
            enriched_search = search.model_copy(update={'hits': retrieval_hits})
            recursive_retriever = _build_public_recursive_retriever(search=enriched_search)
            if recursive_retriever is not None:
                return recursive_retriever.retrieve(query_str)
        use_document_groups = bool(search.document_groups) and len(retrieval_hits) == len(search.hits)
        enriched_search = (
            search
            if use_document_groups
            else search.model_copy(update={'hits': retrieval_hits, 'document_groups': []})
        )
        return _build_public_retrieval_source_nodes(search=enriched_search)

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


async def _build_llamaindex_direct_result(
    *,
    request: MessageResponseRequest,
    settings: Any,
    plan: KernelPlan,
    engine_name: str,
    engine_mode: str,
    actor: dict[str, Any] | None,
    conversation_context: dict[str, Any] | None,
    school_profile: dict[str, Any] | None,
    preview: Any,
    message_text: str,
    execution_reason: str,
    evidence_pack: Any,
    started_at: float,
    reason_graph_leaf: str,
) -> KernelRunResult:
    effective_conversation_id = rt._effective_conversation_id(request)
    suggested_replies = rt._build_suggested_replies(
        request=request,
        preview=preview,
        actor=actor,
        school_profile=school_profile,
        conversation_context=conversation_context,
    )
    normalized_text = rt._normalize_response_wording(message_text)
    await rt._persist_conversation_turn(
        settings=settings,
        conversation_external_id=effective_conversation_id,
        channel=request.channel.value,
        actor=actor,
        user_message=request.message,
        assistant_message=normalized_text,
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
        message_text=normalized_text,
        citations_count=0,
        suggested_reply_count=len(suggested_replies),
        visual_asset_count=0,
        answer_verifier_valid=True,
        answer_verifier_reason=execution_reason,
        answer_verifier_fallback_used=False,
        deterministic_fallback_available=True,
        answer_verifier_judge_used=False,
    )
    response = MessageResponse(
        message_text=normalized_text,
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
            f'llamaindex:{reason_graph_leaf}',
            f'kernel:{plan.stack_name}',
        ],
        risk_flags=preview.risk_flags,
        reason=execution_reason,
        used_llm=False,
        llm_stages=[],
        candidate_chosen='deterministic',
        candidate_reason=execution_reason,
    )
    record_stack_outcome(
        stack_name='llamaindex',
        latency_ms=(monotonic() - started_at) * 1000,
        success=True,
        timeout=False,
        cache_hit=False,
        used_llm=False,
        candidate_kind='deterministic',
    )
    reflection = KernelReflection(
        grounded=True,
        verifier_reason=execution_reason,
        fallback_used=False,
        answer_judge_used=False,
        notes=[
            f'route:{preview.mode.value}',
            f'slice:{plan.slice_name}',
            f'evidence:{evidence_pack.strategy}' if evidence_pack is not None else 'evidence:none',
            *plan.plan_notes,
        ],
    )
    return KernelRunResult(
        plan=plan.model_copy(update={'preview': preview}),
        reflection=reflection,
        response=response.model_dump(mode='json'),
    )


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


def _llamaindex_public_plan_has_deterministic_signal(public_plan: Any) -> bool:
    required_tools = tuple(getattr(public_plan, 'required_tools', ()) or ())
    secondary_acts = tuple(getattr(public_plan, 'secondary_acts', ()) or ())
    requested_attribute = str(getattr(public_plan, 'requested_attribute', '') or '').strip()
    requested_channel = str(getattr(public_plan, 'requested_channel', '') or '').strip()
    focus_hint = str(getattr(public_plan, 'focus_hint', '') or '').strip()
    conversation_act = str(getattr(public_plan, 'conversation_act', '') or '').strip()
    if conversation_act and conversation_act != 'canonical_fact':
        return True
    if requested_attribute or requested_channel or focus_hint:
        return True
    if secondary_acts:
        return True
    return bool(set(required_tools) - {'get_public_school_profile'})


def _llamaindex_unpublished_decision_for_key(key: str) -> LlamaIndexNativePublicDecision | None:
    route = _LLAMAINDEX_NATIVE_UNPUBLISHED_ROUTE_MAP.get(str(key or '').strip())
    if route is None:
        return None
    return LlamaIndexNativePublicDecision(
        conversation_act=route.get('conversation_act', 'canonical_fact'),
        answer_mode='unpublished',
        required_tools=['get_public_school_profile'],
        requested_attribute=route.get('requested_attribute') or None,
        requested_channel=route.get('requested_channel') or None,
        focus_hint=route.get('focus_hint') or None,
        unpublished_key=str(key or '').strip() or None,
        use_conversation_context=False,
    )


def _llamaindex_infer_answer_mode_from_public_plan(*, message: str, public_plan: Any) -> str:
    required_tools = set(getattr(public_plan, 'required_tools', ()) or ())
    conversation_act = str(getattr(public_plan, 'conversation_act', '') or '').strip()
    if 'project_public_pricing' in required_tools or conversation_act == 'pricing':
        return 'pricing'
    if _has_documentary_retrieval_cues(message) or _looks_like_open_documentary_bundle_query(message):
        return 'documentary'
    normalized = rt._normalize_text(message)
    if conversation_act in {'highlight', 'comparative', 'curriculum', 'confessional'} and any(
        marker in normalized
        for marker in (
            'por que ',
            'porque ',
            'me explique',
            'explique',
            'compare',
            'comparar',
            'comparacao',
            'comparação',
            'sintetize',
            'sintetiza',
            'relacione',
            'conecte',
            'diferenciais',
            'vale a pena',
            'proposta pedagogica',
            'proposta pedagógica',
        )
    ):
        return 'documentary'
    return 'profile'


def _llamaindex_decision_from_public_plan(
    *,
    message: str,
    public_plan: Any,
) -> LlamaIndexNativePublicDecision | None:
    if not _llamaindex_public_plan_has_deterministic_signal(public_plan):
        return None
    return LlamaIndexNativePublicDecision(
        conversation_act=str(getattr(public_plan, 'conversation_act', 'canonical_fact') or 'canonical_fact'),
        answer_mode=_llamaindex_infer_answer_mode_from_public_plan(message=message, public_plan=public_plan),
        required_tools=list(getattr(public_plan, 'required_tools', ()) or ()),
        secondary_acts=list(getattr(public_plan, 'secondary_acts', ()) or ()),
        requested_attribute=str(getattr(public_plan, 'requested_attribute', '') or '').strip() or None,
        requested_channel=str(getattr(public_plan, 'requested_channel', '') or '').strip() or None,
        focus_hint=str(getattr(public_plan, 'focus_hint', '') or '').strip() or None,
        use_conversation_context=bool(getattr(public_plan, 'use_conversation_context', False)),
    )


def _deterministic_llamaindex_native_public_decision(
    *,
    message: str,
    preview: Any,
    conversation_context: dict[str, Any] | None,
    school_profile: dict[str, Any],
) -> LlamaIndexNativePublicDecision | None:
    known_unknown_key = detect_public_known_unknown_key(message)
    if known_unknown_key:
        return _normalize_llamaindex_native_public_decision(
            _llamaindex_unpublished_decision_for_key(known_unknown_key)
        )
    heuristic_decision = _heuristic_llamaindex_native_public_decision(
        message=message,
        conversation_context=conversation_context,
    )
    if heuristic_decision is not None:
        return _normalize_llamaindex_native_public_decision(heuristic_decision)
    public_plan = rt._build_public_institution_plan(
        message,
        list(getattr(preview, 'selected_tools', ()) or ()),
        semantic_plan=None,
        conversation_context=conversation_context,
        school_profile=school_profile,
    )
    plan_decision = _llamaindex_decision_from_public_plan(message=message, public_plan=public_plan)
    if plan_decision is not None:
        return _normalize_llamaindex_native_public_decision(plan_decision)
    if _looks_like_llamaindex_value_prop_query(message):
        return _normalize_llamaindex_native_public_decision(
            LlamaIndexNativePublicDecision(
                conversation_act='highlight',
                answer_mode='documentary',
                required_tools=['get_public_school_profile'],
                focus_hint='diferenciais institucionais, proposta pedagogica e evidencias documentais publicas',
                use_conversation_context=True,
            )
        )
    return None


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


def _should_use_llamaindex_llm_public_resolver(
    *,
    request: MessageResponseRequest,
    plan: KernelPlan,
    heuristic_decision: LlamaIndexNativePublicDecision | None,
    settings: Any,
) -> bool:
    if not _should_run_llamaindex_native_public_resolver(request=request, plan=plan):
        return False
    if not bool(getattr(settings, 'llamaindex_native_prompt_router_ambiguity_only', True)):
        return True
    if heuristic_decision is None:
        return True
    return heuristic_decision.answer_mode == 'clarify'


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


def _should_use_llamaindex_selector_router(
    *,
    settings: Any,
    native_decision: LlamaIndexNativePublicDecision | None,
    public_plan: Any,
    llm: Any | None,
    profile: PathExecutionProfile,
) -> bool:
    if llm is None or not profile.prefer_native_llamaindex_selector:
        return False
    if bool(getattr(settings, 'llamaindex_native_selector_ambiguity_only', True)):
        if native_decision is not None and native_decision.answer_mode != 'clarify':
            return False
        if _llamaindex_public_plan_has_deterministic_signal(public_plan):
            return False
    return True


def _build_llamaindex_node_postprocessors(*, settings: Any) -> list[Any]:
    postprocessors: list[Any] = []
    if bool(getattr(settings, 'llamaindex_native_sentence_optimizer_enabled', True)):
        percentile_cutoff = float(getattr(settings, 'llamaindex_native_sentence_optimizer_percentile_cutoff', 0.55) or 0.55)
        percentile_cutoff = min(max(percentile_cutoff, 0.1), 0.95)
        postprocessors.append(
            SentenceEmbeddingOptimizer(
                embed_model=_selector_embedding(str(settings.document_embedding_model)),
                percentile_cutoff=percentile_cutoff,
            )
        )
    if bool(getattr(settings, 'llamaindex_native_long_context_reorder_enabled', True)):
        postprocessors.append(LongContextReorder())
    return postprocessors


def _build_public_document_group_node(group: Any) -> NodeWithScore:
    section_titles = [str(item).strip() for item in list(getattr(group, 'section_titles', []) or []) if str(item).strip()]
    section_label = str(getattr(group, 'primary_section', '') or '').strip()
    summary = str(getattr(group, 'primary_summary', '') or '').strip()
    excerpt = str(getattr(group, 'primary_excerpt', '') or '').strip()
    text_parts = [f'Documento: {group.document_title}']
    if section_label:
        text_parts.append(f'Secao principal: {section_label}')
    if summary:
        text_parts.append(f'Resumo contextual: {summary}')
    if excerpt:
        text_parts.append(f'Trecho principal: {excerpt}')
    if section_titles:
        text_parts.append(f'Secoes relacionadas: {", ".join(section_titles[:4])}')
    citation = getattr(group, 'citation', None)
    return NodeWithScore(
        node=TextNode(
            text='\n'.join(text_parts).strip(),
            metadata={
                'document_title': group.document_title,
                'version_label': str(getattr(citation, 'version_label', '') or ''),
                'storage_path': str(getattr(citation, 'storage_path', '') or ''),
                'chunk_id': str(getattr(citation, 'chunk_id', '') or ''),
                'contextual_summary': summary,
                'section_path': section_label,
                'section_title': section_titles[0] if section_titles else section_label,
                'parent_ref_key': str(
                    getattr(group, 'parent_ref_key', '')
                    or f"{str(getattr(citation, 'storage_path', '') or group.document_title)}::{section_label or group.document_title}"
                ),
            },
        ),
        score=float(getattr(group, 'document_score', 0.0) or 0.0),
    )


def _build_public_retrieval_hit_node(hit: Any) -> NodeWithScore:
    section_path = str(getattr(hit, 'section_path', '') or '').strip()
    section_title = str(getattr(hit, 'section_title', '') or '').strip()
    summary = str(getattr(hit, 'contextual_summary', '') or '').strip()
    excerpt = str(getattr(hit, 'text_excerpt', '') or '').strip()
    text_parts = [f'Documento: {hit.document_title}']
    if section_path:
        text_parts.append(f'Secao: {section_path}')
    if summary:
        text_parts.append(f'Resumo contextual: {summary}')
    if excerpt:
        text_parts.append(f'Trecho: {excerpt}')
    return NodeWithScore(
        node=TextNode(
            text='\n'.join(text_parts).strip(),
            metadata={
                'document_title': hit.document_title,
                'version_label': hit.citation.version_label,
                'storage_path': hit.citation.storage_path,
                'chunk_id': hit.citation.chunk_id,
                'contextual_summary': summary,
                'section_path': section_path,
                'section_parent': str(getattr(hit, 'section_parent', '') or ''),
                'section_title': section_title,
                'parent_ref_key': str(getattr(hit, 'parent_ref_key', '') or ''),
            },
        ),
        score=float(getattr(hit, 'rerank_score', None) or getattr(hit, 'fused_score', 0.0) or 0.0),
    )


def _build_public_retrieval_source_nodes(*, search: Any) -> list[NodeWithScore]:
    document_groups = list(getattr(search, 'document_groups', []) or [])
    if document_groups:
        return [_build_public_document_group_node(group) for group in document_groups[:4]]
    retrieval_hits = list(getattr(search, 'hits', []) or [])
    return [_build_public_retrieval_hit_node(hit) for hit in retrieval_hits[:4]]


def _normalize_recursive_node_id(value: str) -> str:
    normalized = rt._normalize_text(value)
    slug = ''.join(char if char.isalnum() else '-' for char in normalized).strip('-')
    return slug or 'node'


class _StaticRecursiveEntryRetriever(BaseRetriever):
    _nodes: tuple[NodeWithScore, ...] = PrivateAttr(default_factory=tuple)

    def __init__(self, *, nodes: list[NodeWithScore], **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._nodes = tuple(nodes)

    def _retrieve(self, query_bundle: QueryBundle) -> list[NodeWithScore]:
        return list(self._nodes)

    async def _aretrieve(self, query_bundle: QueryBundle) -> list[NodeWithScore]:
        return list(self._nodes)


def _build_public_recursive_parent_node(*, hit: Any, group: Any | None) -> TextNode:
    parent_ref_key = str(getattr(hit, 'parent_ref_key', '') or '').strip()
    if group is not None:
        parent = _build_public_document_group_node(group).node
        group_parent_ref_key = str(
            getattr(group, 'parent_ref_key', '')
            or getattr(parent, 'metadata', {}).get('parent_ref_key', '')
            or parent_ref_key
        ).strip()
        return TextNode(
            id_=f"public-parent::{_normalize_recursive_node_id(group_parent_ref_key or hit.document_title)}",
            text=parent.text,
            metadata=dict(parent.metadata or {}),
        )
    parent = _build_public_retrieval_hit_node(hit).node
    return TextNode(
        id_=f"public-parent::{_normalize_recursive_node_id(parent_ref_key or str(hit.chunk_id))}",
        text=parent.text,
        metadata=dict(parent.metadata or {}),
    )


def _build_public_recursive_retriever(
    *,
    search: Any,
) -> RecursiveRetriever | None:
    retrieval_hits = list(getattr(search, 'hits', []) or [])
    if not retrieval_hits:
        return None
    group_by_key = {
        _document_group_lookup_key(group): group
        for group in list(getattr(search, 'document_groups', []) or [])
    }
    parent_nodes: dict[str, TextNode] = {}
    child_nodes: list[NodeWithScore] = []
    for hit in retrieval_hits[:6]:
        group = group_by_key.get(_retrieval_hit_lookup_key(hit))
        parent_node = _build_public_recursive_parent_node(hit=hit, group=group)
        parent_nodes[parent_node.node_id] = parent_node
        child_text = str(hit.contextual_summary or hit.section_title or hit.text_excerpt or '').strip()
        if not child_text:
            child_text = str(hit.text_excerpt or '').strip()
        child_node = IndexNode(
            id_=f"public-child::{_normalize_recursive_node_id(str(hit.chunk_id))}",
            text=child_text,
            index_id=parent_node.node_id,
            metadata={
                'document_title': hit.document_title,
                'version_label': hit.citation.version_label,
                'storage_path': hit.citation.storage_path,
                'chunk_id': hit.citation.chunk_id,
                'section_path': hit.section_path,
                'section_title': hit.section_title,
                'parent_ref_key': str(getattr(hit, 'parent_ref_key', '') or ''),
            },
        )
        child_nodes.append(
            NodeWithScore(
                node=child_node,
                score=float(getattr(hit, 'rerank_score', None) or getattr(hit, 'fused_score', 0.0) or 0.0),
            )
        )
    if not child_nodes or not parent_nodes:
        return None
    return RecursiveRetriever(
        root_id='public_recursive_entry',
        retriever_dict={'public_recursive_entry': _StaticRecursiveEntryRetriever(nodes=child_nodes)},
        node_dict=parent_nodes,
        verbose=False,
    )


def _document_group_lookup_key(group: Any) -> str:
    citation = getattr(group, 'citation', None)
    storage_path = str(getattr(citation, 'storage_path', '') or '').strip()
    return storage_path or str(getattr(group, 'document_title', '') or '').strip()


def _retrieval_hit_lookup_key(hit: Any) -> str:
    citation = getattr(hit, 'citation', None)
    storage_path = str(getattr(citation, 'storage_path', '') or '').strip()
    return storage_path or str(getattr(hit, 'document_title', '') or '').strip()


def _filter_search_to_document_keys(*, search: Any, document_keys: set[str]) -> Any:
    if not document_keys:
        return search
    filtered_groups = [
        group
        for group in list(getattr(search, 'document_groups', []) or [])
        if _document_group_lookup_key(group) in document_keys
    ]
    filtered_hits = [
        hit
        for hit in list(getattr(search, 'hits', []) or [])
        if _retrieval_hit_lookup_key(hit) in document_keys
    ]
    if not filtered_groups and not filtered_hits:
        return search
    return search.model_copy(update={'document_groups': filtered_groups, 'hits': filtered_hits})


def _extract_public_summary_store_parent_ref_keys(points: Any) -> tuple[str, ...]:
    ordered: list[str] = []
    seen: set[str] = set()
    for point in list(getattr(points, 'points', points) or []):
        payload = getattr(point, 'payload', None) or {}
        parent_ref_key = str(payload.get('parent_ref_key', '') or '').strip()
        if not parent_ref_key or parent_ref_key in seen:
            continue
        seen.add(parent_ref_key)
        ordered.append(parent_ref_key)
    return tuple(ordered)


def _query_public_summary_store_parent_ref_keys(*, query: str, settings: Any) -> tuple[str, ...]:
    if not bool(getattr(settings, 'llamaindex_native_summary_stage_enabled', True)):
        return ()
    collection_name = _resolve_llamaindex_qdrant_summary_collection(settings)
    if not collection_name:
        return ()
    top_k = int(getattr(settings, 'llamaindex_native_summary_stage_top_k', 2) or 2)
    top_k = max(1, top_k)
    try:
        vector = _selector_embedding(str(settings.document_embedding_model))._get_query_embedding(query)
        response = _qdrant_client(qdrant_url=str(settings.qdrant_url)).query_points(
            collection_name=collection_name,
            query=vector,
            query_filter=models.Filter(
                must=[
                    models.FieldCondition(
                        key='visibility',
                        match=models.MatchValue(value='public'),
                    )
                ]
            ),
            limit=top_k,
            with_payload=True,
        )
    except Exception:
        return ()
    return _extract_public_summary_store_parent_ref_keys(response)


def _run_public_hybrid_search(
    *,
    retrieval_service: Any,
    query: str,
    settings: Any,
) -> Any:
    parent_ref_keys = _query_public_summary_store_parent_ref_keys(query=query, settings=settings)
    search = retrieval_service.hybrid_search(
        query=query,
        top_k=4,
        visibility='public',
        category=None,
        parent_ref_keys=parent_ref_keys or None,
    )
    if parent_ref_keys and not list(getattr(search, 'hits', []) or []):
        search = retrieval_service.hybrid_search(
            query=query,
            top_k=4,
            visibility='public',
            category=None,
        )
    return _maybe_apply_public_summary_stage(search=search, query=query, settings=settings)


def _select_public_document_keys_by_summary(*, search: Any, query: str, settings: Any) -> set[str]:
    groups = list(getattr(search, 'document_groups', []) or [])
    if not groups:
        return set()
    top_k = int(getattr(settings, 'llamaindex_native_summary_stage_top_k', 2) or 2)
    top_k = max(1, min(top_k, len(groups)))
    if len(groups) <= top_k:
        return {_document_group_lookup_key(group) for group in groups}
    summary_nodes = [_build_public_document_group_node(group).node for group in groups]
    try:
        index = VectorStoreIndex(nodes=summary_nodes, embed_model=_selector_embedding(str(settings.document_embedding_model)))
        retriever = index.as_retriever(similarity_top_k=top_k)
        selected = retriever.retrieve(query)
    except Exception:
        return set()
    document_keys: set[str] = set()
    for item in selected:
        node = getattr(item, 'node', item)
        metadata = getattr(node, 'metadata', {}) or {}
        storage_path = str(metadata.get('storage_path', '') or '').strip()
        document_title = str(metadata.get('document_title', '') or '').strip()
        key = storage_path or document_title
        if key:
            document_keys.add(key)
    return document_keys


def _maybe_apply_public_summary_stage(*, search: Any, query: str, settings: Any) -> Any:
    if not bool(getattr(settings, 'llamaindex_native_summary_stage_enabled', True)):
        return search
    if not getattr(search, 'document_groups', None):
        return search
    document_keys = _select_public_document_keys_by_summary(search=search, query=query, settings=settings)
    if not document_keys:
        return search
    return _filter_search_to_document_keys(search=search, document_keys=document_keys)


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


def _llamaindex_public_plan_summary(public_plan: Any | None) -> str:
    if public_plan is None:
        return 'sem pista deterministica confiavel'
    summary = {
        'conversation_act': str(getattr(public_plan, 'conversation_act', '') or '').strip(),
        'required_tools': list(getattr(public_plan, 'required_tools', ()) or ()),
        'secondary_acts': list(getattr(public_plan, 'secondary_acts', ()) or ()),
        'requested_attribute': str(getattr(public_plan, 'requested_attribute', '') or '').strip(),
        'requested_channel': str(getattr(public_plan, 'requested_channel', '') or '').strip(),
        'focus_hint': str(getattr(public_plan, 'focus_hint', '') or '').strip(),
        'use_conversation_context': bool(getattr(public_plan, 'use_conversation_context', False)),
    }
    return json.dumps(summary, ensure_ascii=False, sort_keys=True)


async def _resolve_llamaindex_native_public_decision(
    *,
    llm: Any | None,
    settings: Any,
    message: str,
    preview: Any,
    school_profile: dict[str, Any],
    conversation_context: dict[str, Any] | None,
    deterministic_plan: Any | None = None,
) -> LlamaIndexNativePublicDecision | None:
    if llm is None:
        return None
    try:
        decision = await _await_with_llamaindex_timeout(
            llm.astructured_predict(
                LlamaIndexNativePublicDecision,
                _LLAMAINDEX_NATIVE_PUBLIC_FALLBACK_ROUTER_PROMPT,
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
                deterministic_summary=_llamaindex_public_plan_summary(deterministic_plan),
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


def _looks_like_open_documentary_bundle_query(message: str) -> bool:
    normalized = rt._normalize_text(message)
    if not any(
        marker in normalized
        for marker in (
            'compare',
            'comparar',
            'comparacao',
            'comparação',
            'sintetize',
            'sintetiza',
            'sintese',
            'síntese',
            'relacione',
            'relaciona',
            'conecte',
            'conecta',
            'mapa de dependencias',
            'mapa de dependências',
            'atravessam',
            'temas em comum',
            'como se influenciam',
            'quero entender',
            'qual imagem institucional',
            'que leitura integrada',
            'quais evidencias',
            'quais evidências',
            'que evidencias',
            'que evidências',
        )
    ):
        return False
    document_markers = (
        'calendario',
        'calendário',
        'agenda',
        'manual',
        'regulamentos',
        'regulamento',
        'avaliacoes',
        'avaliações',
        'portal',
        'credenciais',
        'secretaria',
        'apoio',
        'biblioteca',
        'laboratorios',
        'laboratórios',
        'familia',
        'família',
        'responsaveis',
        'responsáveis',
        'comunicacao',
        'comunicação',
        'documentos',
        'seguranca',
        'segurança',
        'saude',
        'saúde',
        'autorizacoes',
        'autorizações',
        'transporte',
        'uniforme',
        'refeicao',
        'refeição',
        'governanca',
        'governança',
        'direcao',
        'direção',
        'coordenacao',
        'coordenação',
    )
    hits = sum(1 for marker in document_markers if marker in normalized)
    return hits >= 2


def _should_skip_llamaindex_public_fast_paths(
    message: str,
    *,
    heuristic_decision: LlamaIndexNativePublicDecision | None = None,
    native_decision: LlamaIndexNativePublicDecision | None = None,
) -> bool:
    if _has_documentary_retrieval_cues(message):
        return True
    if _looks_like_open_documentary_bundle_query(message):
        return True
    if heuristic_decision is not None and heuristic_decision.answer_mode == 'documentary':
        return True
    if native_decision is not None and native_decision.answer_mode == 'documentary':
        return True
    return False


def _should_use_llamaindex_protected_records_fast_path(
    *,
    request: MessageResponseRequest,
    actor: dict[str, Any] | None,
    preview: Any,
    conversation_context: dict[str, Any] | None,
) -> bool:
    if request.telegram_chat_id is None or actor is None:
        return False
    if match_public_canonical_lane(request.message):
        return False
    if (
        rt._is_access_scope_query(request.message)
        or rt._is_access_scope_repair_query(request.message, actor, conversation_context)
        or rt._looks_like_family_attendance_aggregate_query(request.message)
        or rt._mentions_personal_admin_status(request.message)
        or rt._detect_admin_attribute_request(request.message, conversation_context=conversation_context) is not None
        or rt._is_private_admin_follow_up(request.message, conversation_context)
        or bool({'get_administrative_status', 'get_student_administrative_status', 'get_actor_identity_context'} & set(preview.selected_tools))
    ):
        return True
    protected_domain_hint = rt._explicit_protected_domain_hint(
        request.message,
        actor=actor,
        conversation_context=conversation_context,
    )
    return protected_domain_hint in {QueryDomain.academic, QueryDomain.finance}


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
        'material publico',
        'material público',
        'base publica',
        'base pública',
        'documentacao publica',
        'documentação pública',
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
    node_postprocessors = _build_llamaindex_node_postprocessors(settings=settings)
    prefer_recursive_retriever = bool(getattr(settings, 'llamaindex_native_recursive_retriever_enabled', True))
    if (
        llm is not None
        and prefer_native_qdrant_autoretriever
        and LLAMAINDEX_QDRANT_AVAILABLE
        and not prefer_recursive_retriever
    ):
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
                        MetadataInfo(name='document_set_slug', type='str', description='Conjunto documental ao qual o documento pertence.'),
                        MetadataInfo(name='version_label', type='str', description='Versao publicada do documento.'),
                        MetadataInfo(name='section_parent', type='str', description='Secao pai da passagem recuperada.'),
                        MetadataInfo(name='section_title', type='str', description='Titulo da secao mais especifica da passagem recuperada.'),
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
                        node_postprocessors=node_postprocessors,
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
            node_postprocessors=node_postprocessors,
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
    started_at = monotonic()
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
    school_profile = await rt._fetch_public_school_profile(settings=settings)
    if recent_focus and recent_focus.get('kind') == 'visit' and rt._looks_like_visit_update_follow_up(request.message):
        preview = plan.preview.model_copy(deep=True)
        preview.mode = OrchestrationMode.structured_tool
        preview.classification = IntentClassification(
            domain=QueryDomain.support,
            access_tier=AccessTier.authenticated if request.user.authenticated else AccessTier.public,
            confidence=0.99,
            reason='follow-up de visita deve atualizar workflow antes do roteamento generico llamaindex',
        )
        preview.reason = 'llamaindex_visit_update_followup'
        preview.selected_tools = list(dict.fromkeys([*preview.selected_tools, 'update_visit_booking']))
        preview.needs_authentication = False
        workflow_payload = await rt._update_visit_booking(
            settings=settings,
            request=request,
            conversation_context=conversation_context,
        )
        evidence_pack = build_structured_tool_evidence_pack(
            selected_tools=preview.selected_tools,
            slice_name=plan.slice_name,
            summary='Follow-up de visita resolvido deterministicamente antes do roteamento documental do LlamaIndex.',
        )
        return await _build_llamaindex_direct_result(
            request=request,
            settings=settings,
            plan=plan,
            engine_name=engine_name,
            engine_mode=engine_mode,
            actor=actor,
            conversation_context=conversation_context,
            school_profile=school_profile,
            preview=preview,
            message_text=rt._compose_visit_booking_action_answer(
                workflow_payload,
                request_message=request.message,
            ),
            execution_reason='llamaindex_visit_update_followup',
            evidence_pack=evidence_pack,
            started_at=started_at,
            reason_graph_leaf='visit_update_direct',
        )
    if rt._looks_like_natural_visit_booking_request(request.message):
        visit_preview = plan.preview.model_copy(deep=True)
        visit_preview.mode = OrchestrationMode.structured_tool
        visit_preview.classification = IntentClassification(
            domain=QueryDomain.support,
            access_tier=AccessTier.authenticated if request.user.authenticated else AccessTier.public,
            confidence=0.99,
            reason='pedido natural de visita deve abrir workflow antes do roteamento generico llamaindex',
        )
        visit_preview.reason = 'llamaindex_visit_booking_request'
        visit_preview.selected_tools = list(dict.fromkeys([*visit_preview.selected_tools, 'schedule_school_visit']))
        visit_preview.needs_authentication = False
        workflow_payload = await rt._create_visit_booking(
            settings=settings,
            request=request,
            actor=actor,
        )
        evidence_pack = build_structured_tool_evidence_pack(
            selected_tools=visit_preview.selected_tools,
            slice_name=plan.slice_name,
            summary='Pedido de visita resolvido deterministicamente antes do roteamento documental do LlamaIndex.',
        )
        return await _build_llamaindex_direct_result(
            request=request,
            settings=settings,
            plan=plan,
            engine_name=engine_name,
            engine_mode=engine_mode,
            actor=actor,
            conversation_context=conversation_context,
            school_profile=school_profile,
            preview=visit_preview,
            message_text=rt._compose_visit_booking_answer(workflow_payload, school_profile),
            execution_reason='llamaindex_visit_booking_request',
            evidence_pack=evidence_pack,
            started_at=started_at,
            reason_graph_leaf='visit_booking_direct',
        )
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
                school_name=str((school_profile or {}).get('school_name', 'Colegio Horizonte')),
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
            school_profile=school_profile,
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
            school_profile=school_profile,
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
    protected_records_fast_path = _should_use_llamaindex_protected_records_fast_path(
        request=request,
        actor=actor,
        preview=plan.preview,
        conversation_context=conversation_context,
    )
    if protected_records_fast_path:
        preview = plan.preview.model_copy(deep=True)
        rt._apply_protected_domain_rescue(
            preview=preview,
            actor=actor,
            message=request.message,
            conversation_context=conversation_context,
        )
        if not {'get_administrative_status', 'get_student_administrative_status', 'get_actor_identity_context'} & set(preview.selected_tools):
            preview.selected_tools = [*preview.selected_tools, 'get_administrative_status', 'get_student_administrative_status']
        preview.mode = OrchestrationMode.structured_tool
        if preview.classification.domain not in {QueryDomain.academic, QueryDomain.finance}:
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
    contextual_public_profile = school_profile
    early_public_answer = await _resolve_early_llamaindex_public_answer(
        request=request,
        plan=plan,
        settings=settings,
        school_profile=contextual_public_profile if isinstance(contextual_public_profile, dict) else None,
        conversation_context=conversation_context,
    )
    if early_public_answer:
        preview = plan.preview.model_copy(deep=True)
        preview.mode = OrchestrationMode.structured_tool
        preview.classification = IntentClassification(
            domain=QueryDomain.institution,
            access_tier=AccessTier.public,
            confidence=0.98,
            reason='consulta publica contextual resolvida antes do routing protegido do llamaindex',
        )
        preview.selected_tools = list(dict.fromkeys([*preview.selected_tools, 'get_public_school_profile']))
        preview.needs_authentication = False
        evidence_pack = build_structured_tool_evidence_pack(
            selected_tools=preview.selected_tools,
            slice_name=plan.slice_name,
            summary='Resposta publica contextual resolvida antes do caminho protegido do LlamaIndex.',
        )
        suggested_replies = rt._build_suggested_replies(
            request=request,
            preview=preview,
            actor=actor,
            school_profile=contextual_public_profile if isinstance(contextual_public_profile, dict) else {},
            conversation_context=conversation_context,
        )
        message_text = rt._normalize_response_wording(early_public_answer.answer_text)
        early_reason_label = {
            'canonical_lane': (
                f'llamaindex canonical public lane fast path:{early_public_answer.canonical_lane}'
                if early_public_answer.canonical_lane
                else 'llamaindex canonical public lane fast path'
            ),
            'contextual_boundary': 'llamaindex contextual public boundary fast path',
            'pricing_projection': 'llamaindex contextual public pricing fast path',
            'contextual_direct': 'llamaindex contextual public direct fast path',
        }.get(early_public_answer.reason, 'llamaindex contextual public direct fast path')
        early_graph_marker = {
            'canonical_lane': (
                f'llamaindex:canonical_public_lane_fast_path:{early_public_answer.canonical_lane}'
                if early_public_answer.canonical_lane
                else 'llamaindex:canonical_public_lane_fast_path'
            ),
            'contextual_boundary': 'llamaindex:contextual_public_boundary_fast_path',
            'pricing_projection': 'llamaindex:contextual_public_pricing_fast_path',
            'contextual_direct': 'llamaindex:contextual_public_direct_fast_path',
        }.get(early_public_answer.reason, 'llamaindex:contextual_public_direct_fast_path')
        early_response_reason = {
            'canonical_lane': (
                f'llamaindex_public_canonical_lane:{early_public_answer.canonical_lane}'
                if early_public_answer.canonical_lane
                else 'llamaindex_canonical_public_lane_fast_path'
            ),
            'contextual_boundary': 'llamaindex_contextual_public_boundary_fast_path',
            'pricing_projection': 'llamaindex_contextual_public_pricing_fast_path',
            'contextual_direct': 'llamaindex_contextual_public_direct_fast_path',
        }.get(early_public_answer.reason, 'llamaindex_contextual_public_direct_fast_path')
        early_candidate_reason = {
            'canonical_lane': (
                f'public_canonical_lane:{early_public_answer.canonical_lane}'
                if early_public_answer.canonical_lane
                else 'canonical_public_lane_fast_path'
            ),
            'contextual_boundary': 'contextual_public_boundary_fast_path',
            'pricing_projection': 'contextual_public_pricing_fast_path',
            'contextual_direct': 'contextual_public_direct_fast_path',
        }.get(early_public_answer.reason, 'contextual_public_direct_fast_path')
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
            school_profile=contextual_public_profile if isinstance(contextual_public_profile, dict) else {},
            conversation_context=conversation_context,
            public_plan=None,
            request_message=request.message,
            message_text=message_text,
            citations_count=0,
            suggested_reply_count=len(suggested_replies),
            visual_asset_count=0,
            answer_verifier_valid=True,
            answer_verifier_reason=early_reason_label,
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
                early_graph_marker,
                f'kernel:{plan.stack_name}',
            ],
            risk_flags=preview.risk_flags,
            reason=early_response_reason,
            candidate_chosen='deterministic',
            candidate_reason=early_candidate_reason,
            retrieval_probe_topic=None,
            response_cache_hit=False,
            response_cache_kind=None,
        )
        reflection = KernelReflection(
            grounded=True,
            verifier_reason=early_reason_label,
            fallback_used=False,
            answer_judge_used=False,
            notes=[
                f'route:{preview.mode.value}',
                f'slice:{plan.slice_name}',
                early_graph_marker,
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
    early_public_canonical_answer = (
        compose_public_canonical_lane_answer(early_public_canonical_lane, profile=school_profile)
        if early_public_canonical_lane
        else None
    )
    if early_public_canonical_answer:
        preview = plan.preview.model_copy(deep=True)
        preview.mode = OrchestrationMode.structured_tool
        preview.classification = IntentClassification(
            domain=QueryDomain.institution,
            access_tier=AccessTier.public,
            confidence=0.99,
            reason='lane publica canonica resolvida antes do roteamento pesado do llamaindex',
        )
        preview.selected_tools = list(dict.fromkeys([*preview.selected_tools, 'get_public_school_profile']))
        preview.needs_authentication = False
        evidence_pack = build_structured_tool_evidence_pack(
            selected_tools=preview.selected_tools,
            slice_name=plan.slice_name,
            summary='Resposta canônica pública resolvida antes do roteamento pesado do LlamaIndex.',
        )
        suggested_replies = rt._build_suggested_replies(
            request=request,
            preview=preview,
            actor=actor,
            school_profile=school_profile,
            conversation_context=conversation_context,
        )
        message_text = rt._normalize_response_wording(early_public_canonical_answer)
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
            answer_verifier_reason='llamaindex canonical public lane fast path',
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
                f'llamaindex:canonical_lane:{early_public_canonical_lane}',
                f'kernel:{plan.stack_name}',
            ],
            risk_flags=preview.risk_flags,
            reason=f'llamaindex_public_canonical_lane:{early_public_canonical_lane}',
            candidate_chosen='deterministic',
            candidate_reason=f'public_canonical_lane:{early_public_canonical_lane}',
            retrieval_probe_topic=None,
            response_cache_hit=False,
            response_cache_kind=None,
        )
        reflection = KernelReflection(
            grounded=True,
            verifier_reason='llamaindex canonical public lane fast path',
            fallback_used=False,
            answer_judge_used=False,
            notes=[
                f'route:{preview.mode.value}',
                f'slice:{plan.slice_name}',
                f'canonical_lane:{early_public_canonical_lane}',
                f'evidence:{evidence_pack.strategy}',
                *plan.plan_notes,
            ],
        )
        return KernelRunResult(
            plan=plan,
            reflection=reflection,
            response=response.model_dump(mode='json'),
        )
    deterministic_public_decision = _deterministic_llamaindex_native_public_decision(
        message=request.message,
        preview=plan.preview,
        conversation_context=conversation_context,
        school_profile=school_profile,
    )
    skip_fast_paths = _should_skip_llamaindex_public_fast_paths(
        request.message,
        heuristic_decision=deterministic_public_decision,
    )
    early_known_unknown_key = detect_public_known_unknown_key(analysis_message) or detect_public_known_unknown_key(request.message)
    early_public_canonical_lane = (
        match_public_canonical_lane(analysis_message)
        or match_public_canonical_lane(request.message)
    ) if not skip_fast_paths else None
    contextual_fast_public_answer = None
    fast_public_channel_answer = None
    if not skip_fast_paths:
        contextual_fast_public_answer = await _maybe_contextual_public_direct_answer(
            request=request,
            analysis_message=analysis_message,
            preview=plan.preview,
            settings=settings,
            school_profile=school_profile,
            conversation_context=conversation_context,
        )
        fast_public_channel_answer = contextual_fast_public_answer
    if not fast_public_channel_answer and not skip_fast_paths:
        fast_public_channel_answer = rt._try_public_channel_fast_answer(
            message=request.message,
            profile=school_profile,
        )
    if fast_public_channel_answer and (contextual_fast_public_answer is not None or not early_public_canonical_lane):
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
            candidate_chosen='deterministic',
            candidate_reason='contextual_public_direct_answer',
            retrieval_probe_topic=None,
            response_cache_hit=False,
            response_cache_kind=None,
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

    orphan_workflow_follow_up = None
    if not early_public_canonical_lane and not early_known_unknown_key and not rt._is_service_routing_query(request.message):
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

    llm_forced_mode = rt._llm_forced_mode_enabled(settings=settings, request=request)
    public_canonical_lane = None if llm_forced_mode else (match_public_canonical_lane(analysis_message) or match_public_canonical_lane(request.message))
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
            candidate_chosen='deterministic',
            candidate_reason=f'public_canonical_lane:{public_canonical_lane}',
            retrieval_probe_topic=None,
            response_cache_hit=False,
            response_cache_kind=None,
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
    if _should_use_llamaindex_llm_public_resolver(
        request=request,
        plan=plan,
        heuristic_decision=deterministic_public_decision,
        settings=settings,
    ):
        deterministic_public_plan = rt._build_public_institution_plan(
            request.message,
            list(getattr(plan.preview, 'selected_tools', ()) or ()),
            semantic_plan=None,
            conversation_context=conversation_context,
            school_profile=school_profile,
        )
        llm_native_public_decision = await _resolve_llamaindex_native_public_decision(
            llm=llamaindex_llm,
            settings=settings,
            message=request.message,
            preview=plan.preview,
            school_profile=school_profile,
            conversation_context=conversation_context,
            deterministic_plan=deterministic_public_plan,
        )
    native_public_decision = _merge_llamaindex_native_public_decisions(
        llm_decision=llm_native_public_decision,
        heuristic_decision=deterministic_public_decision,
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
    skip_fast_paths = _should_skip_llamaindex_public_fast_paths(
        request.message,
        heuristic_decision=deterministic_public_decision,
        native_decision=native_public_decision,
    )
    public_canonical_lane = (
        (
            match_public_canonical_lane(effective_analysis_message)
            or match_public_canonical_lane(request.message)
        )
        if not skip_fast_paths and not llm_forced_mode
        else None
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
    summary_store_hits = 0
    if (
        getattr(settings, 'retrieval_aware_routing_enabled', True)
        and public_canonical_lane is None
        and (
            rt._looks_like_public_documentary_open_query(request.message)
            or _has_documentary_retrieval_cues(request.message)
            or _looks_like_open_documentary_bundle_query(request.message)
        )
    ):
        try:
            summary_store_hits = len(
                _query_public_summary_store_parent_ref_keys(
                    query=effective_retrieval_query,
                    settings=settings,
                )
            )
        except Exception:
            summary_store_hits = 0
    llamaindex_probe = build_public_evidence_probe(
        message=request.message,
        canonical_lane=public_canonical_lane,
        primary_act=public_plan.conversation_act,
        secondary_acts=public_plan.secondary_acts,
        evidence_pack=None,
        retrieval_search=None,
        summary_store_hits=summary_store_hits,
    )
    telemetry_snapshot = get_stack_telemetry_snapshot('llamaindex')
    llamaindex_serving_policy = build_public_serving_policy(
        settings=settings,
        stack_name='llamaindex',
        request=request,
        probe=llamaindex_probe,
        load_snapshot=LoadSnapshot(
            llm_forced_mode=llm_forced_mode,
            recent_request_count=telemetry_snapshot.recent_request_count,
            recent_p95_latency_ms=telemetry_snapshot.recent_p95_latency_ms,
            recent_timeout_rate=telemetry_snapshot.recent_timeout_rate,
            recent_error_rate=telemetry_snapshot.recent_error_rate,
            recent_cache_hit_rate=telemetry_snapshot.recent_cache_hit_rate,
            recent_used_llm_rate=telemetry_snapshot.recent_used_llm_rate,
        ),
    )
    if (
        getattr(settings, 'public_response_cache_enabled', True)
        and llamaindex_serving_policy.prefer_cache
        and not llm_forced_mode
    ):
        semantic_threshold = float(
            getattr(settings, 'public_response_semantic_jaccard_threshold', 0.84)
            if getattr(settings, 'public_response_semantic_cache_enabled', True)
            else 1.01
        )
        cached_public_response = get_cached_public_response(
            message=request.message,
            canonical_lane=public_canonical_lane,
            topic=llamaindex_probe.topic,
            evidence_fingerprint=llamaindex_probe.evidence_fingerprint,
            semantic_threshold=semantic_threshold,
        )
        if cached_public_response is not None:
            response = MessageResponse(
                message_text=cached_public_response.text,
                mode=preview.mode,
                classification=preview.classification,
                retrieval_backend=RetrievalBackend.none,
                selected_tools=list(dict.fromkeys([*preview.selected_tools, 'llamaindex_selector_router'])),
                citations=[],
                visual_assets=[],
                suggested_replies=[],
                calendar_events=[],
                evidence_pack=build_structured_tool_evidence_pack(
                    selected_tools=preview.selected_tools,
                    slice_name=plan.slice_name,
                    summary='Resposta publica reaproveitada do cache semantico do caminho LlamaIndex.',
                ),
                needs_authentication=preview.needs_authentication,
                graph_path=[*preview.graph_path, 'llamaindex:cache', cached_public_response.cache_kind],
                risk_flags=preview.risk_flags,
                reason=f'llamaindex_cache:{cached_public_response.reason or cached_public_response.cache_kind}',
                used_llm=False,
                llm_stages=[],
                final_polish_eligible=False,
                final_polish_applied=False,
                final_polish_mode='skip',
                final_polish_reason='cache_hit',
                final_polish_changed_text=False,
                final_polish_preserved_fallback=False,
                candidate_chosen=cached_public_response.candidate_kind or 'deterministic',
                candidate_reason=f'cache:{cached_public_response.reason or cached_public_response.cache_kind}',
                retrieval_probe_topic=llamaindex_probe.topic,
                response_cache_hit=True,
                response_cache_kind=cached_public_response.cache_kind,
            )
            record_stack_outcome(
                stack_name='llamaindex',
                latency_ms=(monotonic() - started_at) * 1000,
                success=True,
                timeout=False,
                cache_hit=True,
                used_llm=False,
                candidate_kind=response.candidate_chosen,
            )
            return KernelRunResult(
                plan=plan,
                reflection=KernelReflection(
                    grounded=True,
                    verifier_reason='cache_hit',
                    fallback_used=False,
                    answer_judge_used=False,
                    notes=['route:structured_tool', 'cache:semantic_or_exact', *plan.plan_notes],
                ),
                response=response.model_dump(mode='json'),
            )
    documentary_direct_retrieval = _should_force_llamaindex_documentary_retrieval(
        message=request.message,
        public_plan=public_plan,
        native_decision=native_public_decision,
    )
    if (
        getattr(settings, 'retrieval_aware_routing_enabled', True)
        and not llamaindex_serving_policy.allow_documentary_synthesis
        and not llm_forced_mode
    ):
        documentary_direct_retrieval = False

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
        if (
            direct_profile_answer
            and not llm_forced_mode
            and not direct_profile_answer.startswith('Ainda nao encontrei evidencia publica suficiente')
            and not _should_avoid_llamaindex_public_profile_fast_path(
                message=request.message,
                public_plan=public_plan,
                native_decision=native_public_decision,
            )
        ):
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
                tool_response = None
    elif documentary_direct_retrieval:
        selected_tool_names = ('public_retrieval',)
        try:
            tool_response = await _await_with_llamaindex_timeout(
                tools['public_retrieval'].query_engine.aquery(effective_retrieval_query),
                settings=settings,
            )
        except Exception:
            tool_response = None
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
        elif _should_use_llamaindex_selector_router(
            settings=settings,
            native_decision=native_public_decision,
            public_plan=public_plan,
            llm=llamaindex_llm,
            profile=effective_path_profile,
        ):
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
                llm=None,
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
                tool_response = None
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
            latest_query_plan = citation_retriever.latest_query_plan()
            if execution_reason in {'llamaindex_native_public_router', 'llamaindex_router_query_engine'}:
                if bool(getattr(latest_query_plan, 'citation_first_recommended', False)):
                    execution_reason = 'llamaindex_public_citation_first'
                else:
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
    if not answer_text and not llm_forced_mode:
        deterministic_public_fallback = rt._compose_public_profile_answer(
            school_profile,
            request.message,
            actor=actor,
            original_message=request.message,
            conversation_context=conversation_context,
            semantic_plan=public_plan,
        )
        deterministic_public_fallback = str(deterministic_public_fallback or '').strip()
        if (
            deterministic_public_fallback
            and not deterministic_public_fallback.startswith('Ainda nao encontrei evidencia publica suficiente')
        ):
            answer_text = deterministic_public_fallback
            selected_tool_names = tuple(dict.fromkeys([*selected_tool_names, 'public_profile']))
            citations = []
            retrieval_backend = RetrievalBackend.none
            execution_reason = 'llamaindex_deterministic_public_fallback'
    if not answer_text:
        fallback_text = await _maybe_contextual_public_direct_answer(
            request=request,
            analysis_message=analysis_message,
            preview=preview,
            settings=settings,
            school_profile=school_profile,
            conversation_context=conversation_context,
        )
        if fallback_text:
            answer_text = fallback_text
            citations = []
            retrieval_backend = RetrievalBackend.none
            execution_reason = 'contextual_public_direct_answer'
    if not answer_text:
        return None

    message_text = answer_text
    llm_stages = _llamaindex_execution_llm_stages(
        execution_reason=execution_reason,
        semantic_judge_used=False,
    )
    final_polish_decision = build_final_polish_decision(
        settings=settings,
        stack_name=engine_name,
        request=request,
        preview=preview,
        response_reason=execution_reason,
        llm_stages=llm_stages,
        citations_count=len(citations),
        support_count=0,
        retrieval_backend=retrieval_backend,
    )
    final_polish_applied = False
    final_polish_changed_text = False
    final_polish_preserved_fallback = False
    if final_polish_decision.apply_polish:
        original_text = message_text
        raw_polished_text = await polish_llamaindex_with_provider(
            settings=settings,
            request_message=request.message,
            preview=preview,
            draft_text=message_text,
            conversation_context=conversation_context,
            school_profile=school_profile,
        )
        polished_text = rt._preserve_capability_anchor_terms(
            original_text=original_text,
            polished_text=raw_polished_text,
            request_message=request.message,
        )
        final_polish_preserved_fallback = bool(
            raw_polished_text
            and polished_text == original_text
            and rt._normalize_text(raw_polished_text) != rt._normalize_text(original_text)
        )
        if polished_text:
            llm_stages.append('structured_polish')
            final_polish_applied = True
            final_polish_changed_text = rt._normalize_text(polished_text) != rt._normalize_text(original_text)
            message_text = polished_text
    if final_polish_decision.run_response_critic:
        revised_text = await revise_llamaindex_with_provider(
            settings=settings,
            request_message=request.message,
            preview=preview,
            draft_text=message_text,
            conversation_context=conversation_context,
            school_profile=school_profile,
        )
        if revised_text:
            llm_stages.append('response_critic')
            message_text = revised_text

    verification_slot_memory = rt._build_conversation_slot_memory(
        actor=actor,
        profile=school_profile,
        conversation_context=conversation_context,
        request_message=request.message,
        public_plan=public_plan,
        preview=preview,
    )
    verification, semantic_judge_used = await verify_llamaindex_answer_against_contract(
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
    llm_stages = _llamaindex_execution_llm_stages(
        execution_reason=execution_reason,
        semantic_judge_used=semantic_judge_used,
    ) + [stage for stage in llm_stages if stage in {'structured_polish', 'response_critic'}]
    llm_stages = list(dict.fromkeys(llm_stages))
    deterministic_candidate_text = rt._compose_public_profile_answer(
        school_profile,
        request.message,
        actor=actor,
        original_message=request.message,
        conversation_context=conversation_context,
        semantic_plan=public_plan,
    )
    deterministic_candidate_text = str(deterministic_candidate_text or '').strip()
    candidate_chosen = 'documentary_synthesis' if llm_stages else 'deterministic'
    candidate_reason = execution_reason
    retrieval_probe_topic = llamaindex_probe.topic
    response_cache_hit = False
    response_cache_kind = None
    if deterministic_candidate_text and getattr(settings, 'candidate_chooser_enabled', True):
        deterministic_candidate = build_response_candidate(
            kind='deterministic',
            text=deterministic_candidate_text,
            reason='llamaindex_deterministic_fallback',
            retrieval_backend=RetrievalBackend.none,
            selected_tools=tuple(selected_tools),
            source_count=max(1, len(citations)),
            support_count=evidence_pack.support_count,
        )
        current_candidate = build_response_candidate(
            kind='documentary_synthesis' if llm_stages else 'deterministic',
            text=message_text,
            reason=execution_reason,
            used_llm=bool(llm_stages),
            llm_stages=tuple(llm_stages),
            retrieval_backend=retrieval_backend,
            selected_tools=tuple(selected_tools),
            source_count=max(1, len(citations)),
            support_count=evidence_pack.support_count,
        )
        chosen_candidate = choose_best_candidate(
            candidates=[candidate for candidate in (deterministic_candidate, current_candidate) if candidate is not None],
            probe=llamaindex_probe,
            policy=llamaindex_serving_policy,
        )
        if chosen_candidate is not None:
            message_text = chosen_candidate.candidate.text
            candidate_chosen = chosen_candidate.candidate.kind
            candidate_reason = chosen_candidate.chooser_reason
    if getattr(settings, 'public_response_cache_enabled', True) and llamaindex_serving_policy.prefer_cache:
        store_cached_public_response(
            message=request.message,
            text=message_text,
            canonical_lane=public_canonical_lane,
            topic=llamaindex_probe.topic,
            evidence_fingerprint=llamaindex_probe.evidence_fingerprint,
            candidate_kind=candidate_chosen,
            reason=candidate_reason,
            ttl_seconds=float(getattr(settings, 'public_response_cache_ttl_seconds', 300.0)),
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
        used_llm=bool(llm_stages),
        llm_stages=llm_stages,
        final_polish_eligible=final_polish_decision.eligible,
        final_polish_applied=final_polish_applied,
        final_polish_mode=final_polish_decision.mode,
        final_polish_reason=final_polish_decision.reason,
        final_polish_changed_text=final_polish_changed_text,
        final_polish_preserved_fallback=final_polish_preserved_fallback,
        candidate_chosen=candidate_chosen,
        candidate_reason=candidate_reason,
        retrieval_probe_topic=retrieval_probe_topic,
        response_cache_hit=response_cache_hit,
        response_cache_kind=response_cache_kind,
    )
    record_stack_outcome(
        stack_name='llamaindex',
        latency_ms=(monotonic() - started_at) * 1000,
        success=True,
        timeout=False,
        cache_hit=response_cache_hit,
        used_llm=bool(llm_stages),
        candidate_kind=candidate_chosen,
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
