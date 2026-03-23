from __future__ import annotations

from functools import lru_cache

from fastapi import FastAPI
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

from .graph import build_orchestration_graph, get_graph_blueprint, to_preview
from .models import OrchestrationMode, OrchestrationRequest, RetrievalBackend, RuntimeCapabilities
from .tools import get_tool_contracts


class Settings(BaseSettings):
    model_config = SettingsConfigDict(case_sensitive=False)

    app_env: str = 'development'
    log_level: str = 'INFO'
    port: int = 8000
    llm_provider: str = 'openai'
    openai_base_url: str = 'https://api.openai.com/v1'
    openai_model: str = 'gpt-5.4'
    google_model: str = 'gemini-2.5-pro'
    qdrant_url: str = 'http://qdrant:6333'
    qdrant_documents_collection: str = 'school_documents'
    graph_rag_enabled: bool = False


@lru_cache
def get_settings() -> Settings:
    return Settings()


class HealthResponse(BaseModel):
    status: str
    service: str
    provider: str
    retrieval: str


app = FastAPI(
    title='EduAssist AI Orchestrator',
    version='0.2.0',
    summary='Agentic orchestration runtime bootstrap for EduAssist Platform.',
)


@app.get('/healthz', response_model=HealthResponse)
async def healthz() -> HealthResponse:
    settings = get_settings()
    return HealthResponse(
        status='ok',
        service='ai-orchestrator',
        provider=settings.llm_provider,
        retrieval='qdrant-hybrid-bootstrap',
    )


@app.get('/meta')
async def meta() -> dict[str, object]:
    settings = get_settings()
    return {
        'service': 'ai-orchestrator',
        'environment': settings.app_env,
        'provider': settings.llm_provider,
        'openaiBaseUrl': settings.openai_base_url,
        'openaiModel': settings.openai_model,
        'googleModel': settings.google_model,
        'qdrantUrl': settings.qdrant_url,
        'qdrantDocumentsCollection': settings.qdrant_documents_collection,
        'graphRagEnabled': settings.graph_rag_enabled,
    }


@app.get('/v1/status')
async def status() -> dict[str, object]:
    settings = get_settings()
    return {
        'service': 'ai-orchestrator',
        'ready': True,
        'capabilities': [
            'langgraph-state-machine',
            'tool-routing',
            'qdrant-hybrid-planning',
            'graph-rag-routing',
            'provider-abstraction',
        ],
        'graphRagEnabled': settings.graph_rag_enabled,
    }


@app.get('/v1/capabilities', response_model=RuntimeCapabilities)
async def capabilities() -> RuntimeCapabilities:
    settings = get_settings()
    return RuntimeCapabilities(
        service='ai-orchestrator',
        llm_provider=settings.llm_provider,
        openai_model=settings.openai_model,
        google_model=settings.google_model,
        qdrant_url=settings.qdrant_url,
        graph_rag_enabled=settings.graph_rag_enabled,
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
