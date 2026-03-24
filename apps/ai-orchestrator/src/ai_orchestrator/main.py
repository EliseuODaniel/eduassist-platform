from __future__ import annotations

from functools import lru_cache
import logging
import secrets
import threading

from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict
from eduassist_observability import configure_observability

from .graph import build_orchestration_graph, get_graph_blueprint, to_preview
from .graph_rag_runtime import graph_rag_workspace_ready
from .models import (
    MessageResponse,
    MessageResponseRequest,
    OrchestrationMode,
    OrchestrationRequest,
    RetrievalBackend,
    RetrievalSearchRequest,
    RetrievalSearchResponse,
    RuntimeCapabilities,
)
from .retrieval import get_retrieval_service
from .runtime import generate_message_response
from .tools import get_tool_contracts


class Settings(BaseSettings):
    model_config = SettingsConfigDict(case_sensitive=False)

    app_env: str = 'development'
    log_level: str = 'INFO'
    port: int = 8000
    llm_provider: str = 'openai'
    api_core_url: str = 'http://api-core:8000'
    internal_api_token: str = 'dev-internal-token'
    openai_api_key: str | None = None
    openai_base_url: str = 'https://api.openai.com/v1'
    openai_model: str = 'gpt-5.4'
    google_api_key: str | None = None
    google_api_base_url: str = 'https://generativelanguage.googleapis.com/v1beta'
    google_model: str = 'gemini-2.5-flash'
    database_url: str = 'postgresql://eduassist:eduassist@postgres:5432/eduassist'
    qdrant_url: str = 'http://qdrant:6333'
    qdrant_documents_collection: str = 'school_documents'
    document_embedding_model: str = 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'
    warm_retrieval_on_startup: bool = True
    graph_rag_enabled: bool = False
    graph_rag_workspace: str = '/workspace/artifacts/graphrag/eduassist-public-benchmark'
    graph_rag_response_type: str = 'List of 3-5 concise bullet points in Brazilian Portuguese'
    graph_rag_local_chat_api_base: str = 'http://host.docker.internal:18080/v1'
    graph_rag_local_embedding_api_base: str = 'http://host.docker.internal:11435/v1'
    graph_rag_local_chat_api_key: str = 'llama.cpp'
    graph_rag_local_embedding_api_key: str = 'ollama'


@lru_cache
def get_settings() -> Settings:
    return Settings()


def _require_internal_api_token(x_internal_api_token: str | None) -> None:
    settings = get_settings()
    if not x_internal_api_token or not secrets.compare_digest(x_internal_api_token, settings.internal_api_token):
        raise HTTPException(status_code=401, detail='invalid_internal_api_token')


class HealthResponse(BaseModel):
    status: str
    service: str
    ready: bool


app = FastAPI(
    title='EduAssist AI Orchestrator',
    version='0.2.0',
    summary='Agentic orchestration runtime bootstrap for EduAssist Platform.',
)

configure_observability(
    service_name='ai-orchestrator',
    service_version=app.version,
    environment=get_settings().app_env,
    app=app,
    excluded_urls='/healthz,/meta',
)

logger = logging.getLogger(__name__)


def _warm_retrieval_service_in_background(settings: Settings) -> None:
    try:
        get_retrieval_service(
            database_url=settings.database_url,
            qdrant_url=settings.qdrant_url,
            collection_name=settings.qdrant_documents_collection,
            embedding_model=settings.document_embedding_model,
        )
        logger.info('retrieval_service_warmed')
    except Exception:
        logger.exception('retrieval_service_warmup_failed')


@app.on_event('startup')
async def warm_runtime_dependencies() -> None:
    settings = get_settings()
    if not settings.warm_retrieval_on_startup:
        return
    threading.Thread(
        target=_warm_retrieval_service_in_background,
        args=(settings,),
        daemon=True,
        name='retrieval-warmup',
    ).start()


@app.get('/healthz', response_model=HealthResponse)
async def healthz() -> HealthResponse:
    return HealthResponse(
        status='ok',
        service='ai-orchestrator',
        ready=True,
    )


@app.get('/meta')
async def meta(
    x_internal_api_token: str | None = Header(default=None, alias='X-Internal-Api-Token'),
) -> dict[str, object]:
    _require_internal_api_token(x_internal_api_token)
    settings = get_settings()
    return {
        'service': 'ai-orchestrator',
        'environment': settings.app_env,
        'provider': settings.llm_provider,
        'openaiModel': settings.openai_model,
        'googleModel': settings.google_model,
        'llmConfigured': bool(settings.openai_api_key) or bool(settings.google_api_key),
        'retrievalBackend': 'qdrant-hybrid',
        'graphRagEnabled': settings.graph_rag_enabled,
    }


@app.get('/v1/status')
async def status() -> dict[str, object]:
    settings = get_settings()
    return {
        'service': 'ai-orchestrator',
        'ready': True,
        'llmProvider': settings.llm_provider,
        'llmConfigured': bool(settings.openai_api_key) or bool(settings.google_api_key),
        'capabilities': [
            'langgraph-state-machine',
            'tool-routing',
            'qdrant-hybrid-retrieval',
            'conversation-memory',
            'graph-rag-routing',
            'provider-abstraction',
        ],
        'graphRagEnabled': settings.graph_rag_enabled,
        'graphRagWorkspaceReady': graph_rag_workspace_ready(settings.graph_rag_workspace),
    }


@app.get('/v1/capabilities', response_model=RuntimeCapabilities)
async def capabilities() -> RuntimeCapabilities:
    settings = get_settings()
    return RuntimeCapabilities(
        service='ai-orchestrator',
        llm_provider=settings.llm_provider,
        openai_model=settings.openai_model,
        google_model=settings.google_model,
        llm_configured=bool(settings.openai_api_key) or bool(settings.google_api_key),
        graph_rag_enabled=settings.graph_rag_enabled,
        graph_rag_workspace_ready=graph_rag_workspace_ready(settings.graph_rag_workspace),
        available_modes=[
            OrchestrationMode.hybrid_retrieval,
            OrchestrationMode.graph_rag,
            OrchestrationMode.structured_tool,
            OrchestrationMode.handoff,
            OrchestrationMode.clarify,
            OrchestrationMode.deny,
        ],
        retrieval_backends=[
            RetrievalBackend.qdrant_hybrid,
            RetrievalBackend.graph_rag,
            RetrievalBackend.none,
        ],
    )


@app.get('/v1/retrieval/status')
async def retrieval_status() -> dict[str, object]:
    settings = get_settings()
    service = get_retrieval_service(
        database_url=settings.database_url,
        qdrant_url=settings.qdrant_url,
        collection_name=settings.qdrant_documents_collection,
        embedding_model=settings.document_embedding_model,
    )
    return {
        'service': 'ai-orchestrator',
        'retrievalBackend': RetrievalBackend.qdrant_hybrid.value,
        'qdrant': service.collection_status(),
    }


@app.post('/v1/retrieval/search', response_model=RetrievalSearchResponse)
async def retrieval_search(request: RetrievalSearchRequest) -> RetrievalSearchResponse:
    settings = get_settings()
    service = get_retrieval_service(
        database_url=settings.database_url,
        qdrant_url=settings.qdrant_url,
        collection_name=settings.qdrant_documents_collection,
        embedding_model=settings.document_embedding_model,
    )
    return service.hybrid_search(
        query=request.query,
        top_k=request.top_k,
        visibility=request.visibility,
        category=request.category,
    )


@app.post('/v1/messages/respond', response_model=MessageResponse)
async def message_response(
    request: MessageResponseRequest,
    x_internal_api_token: str | None = Header(default=None, alias='X-Internal-Api-Token'),
) -> MessageResponse:
    _require_internal_api_token(x_internal_api_token)
    settings = get_settings()
    return await generate_message_response(request=request, settings=settings)


@app.get('/v1/tools')
async def tools() -> dict[str, object]:
    contracts = get_tool_contracts()
    return {
        'service': 'ai-orchestrator',
        'count': len(contracts),
        'tools': [tool.model_dump(mode='json') for tool in contracts],
    }


@app.get('/v1/graph')
async def graph_definition() -> dict[str, object]:
    settings = get_settings()
    return {
        'service': 'ai-orchestrator',
        'graphRagEnabled': settings.graph_rag_enabled,
        'blueprint': get_graph_blueprint(),
    }


@app.post('/v1/orchestrate/preview')
async def preview_orchestration(request: OrchestrationRequest) -> dict[str, object]:
    settings = get_settings()
    graph = build_orchestration_graph(settings.graph_rag_enabled)
    state = graph.invoke({'request': request})
    preview = to_preview(state)
    return {
        'service': 'ai-orchestrator',
        'preview': preview.model_dump(mode='json'),
    }
