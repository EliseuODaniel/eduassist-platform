from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass
from functools import lru_cache
from time import monotonic as _llamaindex_monotonic
from typing import Any

from fastembed import TextEmbedding
from llama_index.core import VectorStoreIndex
from llama_index.core.agent.workflow import FunctionAgent
from llama_index.core.base.base_retriever import BaseRetriever
from llama_index.core.base.embeddings.base import BaseEmbedding
from llama_index.core.base.llms.types import ChatMessage, LLMMetadata, MessageRole
from llama_index.core.base.response.schema import Response
from llama_index.core.postprocessor import LongContextReorder, SentenceEmbeddingOptimizer
from llama_index.core.prompts import PromptTemplate
from llama_index.core.query_engine import (
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
from pydantic import BaseModel, Field, PrivateAttr

from .retrieval_capability_policy import resolve_retrieval_execution_policy
from qdrant_client import AsyncQdrantClient, QdrantClient, models
from eduassist_semantic_ingress import looks_like_high_confidence_public_school_faq

from . import runtime as rt
from .llamaindex_kernel import KernelPlan, KernelReflection, KernelRunResult
from .evidence_pack import (
    build_direct_answer_evidence_pack as _llamaindex_build_direct_answer_evidence_pack,
    build_retrieval_evidence_pack as _llamaindex_build_retrieval_evidence_pack,
    build_structured_tool_evidence_pack as _llamaindex_build_structured_tool_evidence_pack,
)
from .entity_resolution import resolve_entity_hints
from .llamaindex_kernel_runtime import (
    _maybe_contextual_public_direct_answer as _llamaindex_maybe_contextual_public_direct_answer,
    _maybe_hypothetical_public_pricing_answer,
)
from .llamaindex_public_intent_registry import (
    LLAMAINDEX_PUBLIC_INTENT_RULES,
    LlamaIndexPublicIntentRule,
)
from .model_cache import configure_model_cache_env
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
from .path_profiles import (
    PathExecutionProfile,
    get_path_execution_profile as _llamaindex_get_path_execution_profile,
)
from .llamaindex_public_knowledge import (
    compose_public_canonical_lane_answer,
    compose_public_conduct_policy_contextual_answer,
    match_public_canonical_lane,
)
from .llamaindex_public_known_unknowns import (
    compose_public_known_unknown_answer,
    detect_public_known_unknown_key,
)
from .llamaindex_retrieval import (
    can_read_restricted_documents,
    get_retrieval_service,
    looks_like_restricted_document_query,
)
from .serving_telemetry import record_stack_outcome as _llamaindex_record_stack_outcome

build_direct_answer_evidence_pack = _llamaindex_build_direct_answer_evidence_pack
build_retrieval_evidence_pack = _llamaindex_build_retrieval_evidence_pack
build_structured_tool_evidence_pack = _llamaindex_build_structured_tool_evidence_pack
_maybe_contextual_public_direct_answer = _llamaindex_maybe_contextual_public_direct_answer
get_path_execution_profile = _llamaindex_get_path_execution_profile
monotonic = _llamaindex_monotonic
record_stack_outcome = _llamaindex_record_stack_outcome
_LLAMAINDEX_NATIVE_MODEL_EXPORTS = (
    KernelReflection,
    MessageResponse,
    MessageEvidencePack,
    MessageResponseCitation,
)

configure_model_cache_env()

try:
    from llama_index.llms.openai import OpenAI as LlamaIndexOpenAI

    LLAMAINDEX_OPENAI_AVAILABLE = True
except Exception:  # pragma: no cover - optional dependency
    LlamaIndexOpenAI = None  # type: ignore[assignment]
    LLAMAINDEX_OPENAI_AVAILABLE = False


if LLAMAINDEX_OPENAI_AVAILABLE:
    class _LocalOpenAICompatibleLlamaIndexLLM(LlamaIndexOpenAI):  # type: ignore[misc,valid-type]
        """Relax OpenAI model metadata assumptions for local OpenAI-compatible servers."""

        _eduassist_context_window: int = PrivateAttr(default=131072)
        _eduassist_is_chat_model: bool = PrivateAttr(default=True)
        _eduassist_supports_function_calling: bool = PrivateAttr(default=False)

        def __init__(
            self,
            *args: Any,
            context_window: int = 131072,
            is_chat_model: bool = True,
            supports_function_calling: bool = False,
            **kwargs: Any,
        ) -> None:
            super().__init__(*args, **kwargs)
            self._eduassist_context_window = int(context_window)
            self._eduassist_is_chat_model = bool(is_chat_model)
            self._eduassist_supports_function_calling = bool(supports_function_calling)

        @property
        def _tokenizer(self):  # pragma: no cover - runtime convenience for local OpenAI-compatible models
            return None

        @property
        def metadata(self) -> LLMMetadata:
            return LLMMetadata(
                context_window=self._eduassist_context_window,
                num_output=self.max_tokens or -1,
                is_chat_model=self._eduassist_is_chat_model,
                is_function_calling_model=self._eduassist_supports_function_calling,
                model_name=self.model,
                system_role=MessageRole.SYSTEM,
            )
else:  # pragma: no cover - import-time fallback when llamaindex openai extras are unavailable
    _LocalOpenAICompatibleLlamaIndexLLM = None  # type: ignore[assignment]

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


def _semantic_ingress_native_public_decision(*, public_plan: Any) -> LlamaIndexNativePublicDecision:
    return LlamaIndexNativePublicDecision(
        conversation_act=str(public_plan.conversation_act or 'canonical_fact'),
        answer_mode='profile',
        required_tools=list(public_plan.required_tools),
        secondary_acts=list(public_plan.secondary_acts),
        requested_attribute=public_plan.requested_attribute,
        requested_channel=public_plan.requested_channel,
        focus_hint=public_plan.focus_hint,
        use_conversation_context=bool(public_plan.use_conversation_context),
    )


def _compose_semantic_ingress_terminal_answer(
    *,
    school_profile: dict[str, Any],
    request_message: str,
    actor: dict[str, Any] | None,
    conversation_context: dict[str, Any] | None,
    public_plan: Any,
) -> str:
    act = str(getattr(public_plan, 'conversation_act', '') or '').strip().lower()
    if act == 'input_clarification':
        return rt._compose_input_clarification_answer(
            school_profile,
            conversation_context=conversation_context,
        )
    if act == 'scope_boundary':
        return rt._compose_scope_boundary_answer(
            school_profile,
            conversation_context=conversation_context,
        )
    return str(
        rt._compose_public_profile_answer(
            school_profile,
            request_message,
            actor=actor,
            original_message=request_message,
            conversation_context=conversation_context,
            semantic_plan=public_plan,
        )
        or ''
    ).strip()


def _canonical_lane_answer_for_message(
    *,
    canonical_lane: str,
    message: str,
    school_profile: dict[str, Any] | None,
) -> str | None:
    if canonical_lane == 'public_bundle.conduct_frequency_punctuality':
        return compose_public_conduct_policy_contextual_answer(message, profile=school_profile) or compose_public_canonical_lane_answer(
            canonical_lane,
            profile=school_profile,
        )
    return compose_public_canonical_lane_answer(canonical_lane, profile=school_profile)


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
    from .llamaindex_native_support_runtime import _maybe_execute_llamaindex_restricted_doc_fast_path as _impl

    return await _impl(
        request=request,
        settings=settings,
        plan=plan,
        engine_name=engine_name,
        engine_mode=engine_mode,
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


def _should_use_llamaindex_teacher_schedule_direct(
    *,
    teacher_authenticated: bool,
    should_fetch_teacher_schedule: bool,
) -> bool:
    return teacher_authenticated and should_fetch_teacher_schedule


def _should_use_llamaindex_teacher_scope_guidance(
    *,
    teacher_scope_query: bool,
    should_fetch_teacher_schedule: bool,
) -> bool:
    return teacher_scope_query and not should_fetch_teacher_schedule


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
    actor: dict[str, Any] | None = None,
) -> LlamaIndexEarlyPublicAnswer | None:
    from .llamaindex_native_support_runtime import _resolve_early_llamaindex_public_answer as _impl

    return await _impl(
        request=request,
        plan=plan,
        settings=settings,
        school_profile=school_profile,
        conversation_context=conversation_context,
        actor=actor,
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
        search = _run_public_hybrid_search(
            retrieval_service=retrieval_service,
            query=query_str,
            settings=self.settings,
            preview=self.preview,
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
            preview=None,
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
    preview: rt.PublicPreview,
    message_text: str,
    execution_reason: str,
    evidence_pack: MessageEvidencePack,
    started_at: float,
    reason_graph_leaf: str,
) -> KernelRunResult:
    from .llamaindex_native_support_runtime import _build_llamaindex_direct_result as _impl

    return await _impl(
        request=request,
        settings=settings,
        plan=plan,
        engine_name=engine_name,
        engine_mode=engine_mode,
        actor=actor,
        conversation_context=conversation_context,
        school_profile=school_profile,
        preview=preview,
        message_text=message_text,
        execution_reason=execution_reason,
        evidence_pack=evidence_pack,
        started_at=started_at,
        reason_graph_leaf=reason_graph_leaf,
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
        'scope_boundary',
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
    preview: Any | None = None,
    turn_frame: Any | None = None,
    public_plan: Any | None = None,
) -> Any:
    parent_ref_keys = _query_public_summary_store_parent_ref_keys(query=query, settings=settings)
    retrieval_policy = resolve_retrieval_execution_policy(
        query=query,
        visibility='public',
        baseline_top_k=4,
        preview=preview,
        turn_frame=turn_frame,
        public_plan=public_plan,
    )
    search = retrieval_service.hybrid_search(
        query=query,
        top_k=retrieval_policy.top_k,
        visibility='public',
        category=retrieval_policy.category,
        profile=retrieval_policy.profile,
        parent_ref_keys=parent_ref_keys or None,
    )
    if parent_ref_keys and not list(getattr(search, 'hits', []) or []):
        search = retrieval_service.hybrid_search(
            query=query,
            top_k=retrieval_policy.top_k,
            visibility='public',
            category=retrieval_policy.category,
            profile=retrieval_policy.profile,
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
    if looks_like_high_confidence_public_school_faq(request.message):
        return False
    if match_public_canonical_lane(request.message):
        return False
    authenticated = bool(getattr(getattr(request, 'user', None), 'authenticated', False))
    if not authenticated:
        preview_access_tier = getattr(getattr(preview, 'classification', None), 'access_tier', None)
        authenticated = preview_access_tier in {AccessTier.authenticated, AccessTier.sensitive}
    return rt._should_use_protected_records_fast_path(
        request_message=request.message,
        actor=actor,
        conversation_context=conversation_context,
        authenticated=authenticated,
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
        'scope_boundary',
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
        model = str(getattr(settings, 'openai_model', 'gpt-5.4'))
        api_base = str(getattr(settings, 'openai_base_url', 'https://api.openai.com/v1'))
        llm_profile = str(getattr(settings, 'llm_model_profile', '') or '').strip().lower()
        local_openai_compatible = llm_profile in {
            'gemma4e4b_local',
            'gemma_4_e4b_local',
            'gemma-4-e4b-local',
        } or '127.0.0.1' in api_base or 'local-llm-' in api_base or 'host.docker.internal' in api_base
        if local_openai_compatible:
            return _LocalOpenAICompatibleLlamaIndexLLM(
                model=model,
                api_key=str(settings.openai_api_key),
                api_base=api_base,
                temperature=0,
                context_window=131072,
                is_chat_model=True,
                supports_function_calling=False,
            )
        return LlamaIndexOpenAI(
            model=model,
            api_key=str(settings.openai_api_key),
            api_base=api_base,
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
    from .llamaindex_native_support_runtime import _build_public_retrieval_query_engine as _impl

    return _impl(
        settings=settings,
        preview=preview,
        original_message=original_message,
        llm=llm,
        prefer_citation_engine=prefer_citation_engine,
        prefer_native_qdrant_autoretriever=prefer_native_qdrant_autoretriever,
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
    llm: Any,
    tools: dict[str, QueryEngineTool],
    session_id: str,
    settings: Any,
) -> tuple[str, tuple[str, ...], tuple[MessageResponseCitation, ...], str] | None:
    from .llamaindex_native_support_runtime import _maybe_execute_llamaindex_agent_workflow as _impl

    return await _impl(
        analysis_message=analysis_message,
        conversation_context=conversation_context,
        llm=llm,
        tools=tools,
        session_id=session_id,
        settings=settings,
    )



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
    from .llamaindex_native_plan_runtime import maybe_execute_llamaindex_native_plan as _impl

    return await _impl(
        request=request,
        settings=settings,
        plan=plan,
        engine_name=engine_name,
        engine_mode=engine_mode,
        path_profile=path_profile,
    )
