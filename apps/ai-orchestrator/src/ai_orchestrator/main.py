from __future__ import annotations

from functools import lru_cache
import logging
import secrets

from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from eduassist_observability import configure_observability

from .engine_selector import (
    build_engine_bundle,
    get_experiment_live_promotion_summary,
    get_experiment_rollout_readiness,
    get_scorecard_gate_status,
    maybe_run_shadow,
    resolve_primary_stack,
)
from .graph import get_graph_blueprint, to_preview
from .graph_rag_runtime import graph_rag_workspace_ready
from .langgraph_runtime import (
    close_langgraph_runtime,
    get_langgraph_artifacts,
    get_orchestration_state_snapshot,
    get_langgraph_runtime_status,
    invoke_orchestration_graph,
    resume_orchestration_graph,
    resolve_langgraph_thread_id,
    warm_langgraph_runtime,
)
from .models import (
    ConversationChannel,
    AccessTier,
    QueryDomain,
    MessageResponse,
    MessageResponseRequest,
    OrchestrationMode,
    OrchestrationRequest,
    RetrievalBackend,
    RetrievalSearchRequest,
    RetrievalSearchResponse,
    RuntimeCapabilities,
    UserContext,
)
from .retrieval import get_retrieval_service
from .runtime import generate_message_response
from .trace_bridge import persist_shadow_trace
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
    orchestrator_engine: str = 'langgraph'
    feature_flag_primary_orchestration_stack: str | None = None
    crewai_pilot_url: str | None = None
    orchestrator_experiment_enabled: bool = False
    orchestrator_experiment_primary_engine: str = 'crewai'
    orchestrator_experiment_slices: str = ''
    orchestrator_experiment_rollout_percent: int = 0
    orchestrator_experiment_slice_rollouts: str = ''
    orchestrator_experiment_telegram_chat_allowlist: str = ''
    orchestrator_experiment_conversation_allowlist: str = ''
    orchestrator_experiment_allowlist_slices: str = ''
    orchestrator_experiment_require_scorecard: bool = False
    orchestrator_experiment_scorecard_path: str = '/workspace/artifacts/framework-native-scorecard.json'
    orchestrator_experiment_min_primary_engine_score: int = 20
    orchestrator_experiment_require_healthy_pilot: bool = False
    orchestrator_experiment_health_ttl_seconds: int = 15
    langgraph_checkpointer_enabled: bool = True
    langgraph_checkpointer_url: str | None = None
    langgraph_checkpointer_schema: str = 'langgraph_checkpoint'
    langgraph_hitl_enabled: bool = False
    langgraph_hitl_default_slices: str = 'support'


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


class LangGraphHitlRequest(BaseModel):
    message: str
    conversation_id: str | None = None
    telegram_chat_id: int | None = None
    channel: ConversationChannel = ConversationChannel.telegram
    user: UserContext = Field(default_factory=UserContext)
    allow_graph_rag: bool = True
    allow_handoff: bool = True
    target_slices: list[str] = Field(default_factory=lambda: ['support'])


class LangGraphHitlResumeRequest(BaseModel):
    conversation_id: str | None = None
    telegram_chat_id: int | None = None
    channel: ConversationChannel = ConversationChannel.telegram
    resume_value: dict[str, object] | list[object] | str | int | float | bool | None


def _normalized_hitl_slices(values: list[str] | None, *, fallback: str) -> list[str]:
    normalized = [str(item).strip() for item in (values or []) if str(item).strip()]
    if normalized:
        return normalized
    return [item.strip() for item in fallback.split(',') if item.strip()] or ['support']


def _hitl_thread_id(
    *,
    conversation_id: str | None,
    channel: ConversationChannel,
    telegram_chat_id: int | None,
) -> str | None:
    return resolve_langgraph_thread_id(
        conversation_external_id=conversation_id,
        channel=channel.value,
        telegram_chat_id=telegram_chat_id,
    )


def _serialize_interrupt_entry(item: object) -> dict[str, object]:
    if hasattr(item, 'value'):
        value = getattr(item, 'value')
    else:
        value = item
    entry: dict[str, object] = {'value': value}
    interrupt_id = getattr(item, 'id', None)
    if interrupt_id is not None:
        entry['id'] = str(interrupt_id)
    return entry


def _snapshot_interrupt_entries(snapshot: object) -> list[dict[str, object]]:
    entries: list[dict[str, object]] = []
    seen: set[tuple[str | None, str]] = set()

    def _append(item: object) -> None:
        entry = _serialize_interrupt_entry(item)
        key = (
            str(entry.get('id')) if entry.get('id') is not None else None,
            repr(entry.get('value')),
        )
        if key in seen:
            return
        seen.add(key)
        entries.append(entry)

    for item in getattr(snapshot, 'interrupts', None) or ():
        _append(item)
    for task in getattr(snapshot, 'tasks', None) or ():
        for item in getattr(task, 'interrupts', None) or ():
            _append(item)
    return entries


def _snapshot_has_pending_interrupt(snapshot: object) -> bool:
    return bool(_snapshot_interrupt_entries(snapshot))


def _build_hitl_preview(values: dict[str, object]) -> dict[str, object] | None:
    if not values or 'route' not in values or 'classification' not in values:
        return None
    try:
        return to_preview(values).model_dump(mode='json')
    except Exception:
        return None


def _serialize_hitl_state_snapshot(snapshot: object) -> dict[str, object]:
    values = dict(getattr(snapshot, 'values', {}) or {})
    top_level_interrupts = [_serialize_interrupt_entry(item) for item in (getattr(snapshot, 'interrupts', None) or ())]
    active_interrupts = _snapshot_interrupt_entries(snapshot)
    next_nodes = [str(item) for item in (getattr(snapshot, 'next', None) or ())]
    tasks = []
    task_interrupt_count = 0
    for task in getattr(snapshot, 'tasks', None) or ():
        task_interrupts = [_serialize_interrupt_entry(item) for item in (getattr(task, 'interrupts', None) or ())]
        task_interrupt_count += len(task_interrupts)
        tasks.append(
            {
                'name': str(getattr(task, 'name', '')),
                'path': [str(part) for part in (getattr(task, 'path', None) or ())],
                'interrupts': task_interrupts,
            }
        )
    return {
        'values': {
            'route': values.get('route'),
            'slice_name': values.get('slice_name'),
            'reason': values.get('reason'),
            'selected_tools': values.get('selected_tools', []),
            'graph_path': values.get('graph_path', []),
            'risk_flags': values.get('risk_flags', []),
            'output_contract': values.get('output_contract'),
            'hitl_status': values.get('hitl_status'),
        },
        'preview': _build_hitl_preview(values),
        'interrupts': active_interrupts,
        'top_level_interrupt_count': len(top_level_interrupts),
        'interrupt_count': len(active_interrupts),
        'task_interrupt_count': task_interrupt_count,
        'has_pending_interrupt': bool(active_interrupts),
        'next_nodes': next_nodes,
        'tasks': tasks,
        'created_at': str(getattr(snapshot, 'created_at', '') or ''),
    }


def _build_hitl_state_input(request: LangGraphHitlRequest, settings: Settings) -> dict[str, object]:
    return {
        'request': OrchestrationRequest(
            message=request.message,
            conversation_id=request.conversation_id,
            user=request.user,
            allow_graph_rag=request.allow_graph_rag,
            allow_handoff=request.allow_handoff,
        ),
        'hitl_enabled': True,
        'hitl_target_slices': _normalized_hitl_slices(
            request.target_slices,
            fallback=settings.langgraph_hitl_default_slices,
        ),
    }


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


def _warm_retrieval_service(settings: Settings) -> None:
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
    if settings.warm_retrieval_on_startup:
        _warm_retrieval_service(settings)
    warm_langgraph_runtime(settings)


@app.on_event('shutdown')
async def close_runtime_dependencies() -> None:
    close_langgraph_runtime()


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
    langgraph_runtime = get_langgraph_runtime_status(settings)
    scorecard_gate = get_scorecard_gate_status(settings=settings)
    rollout_readiness = get_experiment_rollout_readiness(settings=settings)
    live_promotion_summary = get_experiment_live_promotion_summary(settings=settings)
    return {
        'service': 'ai-orchestrator',
        'environment': settings.app_env,
        'orchestratorEngine': settings.orchestrator_engine,
        'crewaiPilotConfigured': bool(settings.crewai_pilot_url),
        'experimentEnabled': settings.orchestrator_experiment_enabled,
        'experimentPrimaryEngine': settings.orchestrator_experiment_primary_engine,
        'experimentSlices': settings.orchestrator_experiment_slices,
        'experimentRolloutPercent': settings.orchestrator_experiment_rollout_percent,
        'experimentSliceRollouts': settings.orchestrator_experiment_slice_rollouts,
        'experimentAllowlistSlices': settings.orchestrator_experiment_allowlist_slices,
        'experimentRequireScorecard': settings.orchestrator_experiment_require_scorecard,
        'experimentScorecardPath': settings.orchestrator_experiment_scorecard_path,
        'experimentMinPrimaryEngineScore': settings.orchestrator_experiment_min_primary_engine_score,
        'experimentRequireHealthyPilot': settings.orchestrator_experiment_require_healthy_pilot,
        'experimentScorecardGate': scorecard_gate,
        'experimentRolloutReadiness': rollout_readiness,
        'experimentLivePromotionSummary': live_promotion_summary,
        'provider': settings.llm_provider,
        'openaiModel': settings.openai_model,
        'googleModel': settings.google_model,
        'llmConfigured': bool(settings.openai_api_key) or bool(settings.google_api_key),
        'retrievalBackend': 'qdrant-hybrid',
        'graphRagEnabled': settings.graph_rag_enabled,
        'langgraphCheckpointerEnabled': langgraph_runtime['checkpointerConfigured'],
        'langgraphCheckpointerReady': langgraph_runtime['checkpointerInitialized'],
        'langgraphCheckpointerBackend': langgraph_runtime['checkpointerBackend'],
        'langgraphThreadIdEnabled': langgraph_runtime['threadIdEnabled'],
        'langgraphHitlEnabled': settings.langgraph_hitl_enabled,
        'langgraphHitlDefaultSlices': settings.langgraph_hitl_default_slices,
    }


@app.get('/v1/status')
async def status() -> dict[str, object]:
    settings = get_settings()
    langgraph_runtime = get_langgraph_runtime_status(settings)
    scorecard_gate = get_scorecard_gate_status(settings=settings)
    rollout_readiness = get_experiment_rollout_readiness(settings=settings)
    live_promotion_summary = get_experiment_live_promotion_summary(settings=settings)
    return {
        'service': 'ai-orchestrator',
        'ready': True,
        'orchestratorEngine': settings.orchestrator_engine,
        'primaryStackFeatureFlag': settings.feature_flag_primary_orchestration_stack,
        'resolvedPrimaryStack': resolve_primary_stack(settings),
        'crewaiPilotConfigured': bool(settings.crewai_pilot_url),
        'experimentEnabled': settings.orchestrator_experiment_enabled,
        'experimentPrimaryEngine': settings.orchestrator_experiment_primary_engine,
        'experimentSlices': settings.orchestrator_experiment_slices,
        'experimentRolloutPercent': settings.orchestrator_experiment_rollout_percent,
        'experimentSliceRollouts': settings.orchestrator_experiment_slice_rollouts,
        'experimentAllowlistSlices': settings.orchestrator_experiment_allowlist_slices,
        'experimentRequireScorecard': settings.orchestrator_experiment_require_scorecard,
        'experimentScorecardPath': settings.orchestrator_experiment_scorecard_path,
        'experimentMinPrimaryEngineScore': settings.orchestrator_experiment_min_primary_engine_score,
        'experimentRequireHealthyPilot': settings.orchestrator_experiment_require_healthy_pilot,
        'experimentScorecardGate': scorecard_gate,
        'experimentRolloutReadiness': rollout_readiness,
        'experimentLivePromotionSummary': live_promotion_summary,
        'llmProvider': settings.llm_provider,
        'llmConfigured': bool(settings.openai_api_key) or bool(settings.google_api_key),
        'capabilities': [
            'langgraph-state-machine',
            'langgraph-thread-id',
            'langgraph-hitl-internal',
            'engine-selector',
            'tool-routing',
            'qdrant-hybrid-retrieval',
            'conversation-memory',
            'graph-rag-routing',
            'provider-abstraction',
        ],
        'supportedEngines': ['langgraph', 'shadow', 'crewai'],
        'graphRagEnabled': settings.graph_rag_enabled,
        'graphRagWorkspaceReady': graph_rag_workspace_ready(settings.graph_rag_workspace),
        'langgraphCheckpointerEnabled': langgraph_runtime['checkpointerConfigured'],
        'langgraphCheckpointerReady': langgraph_runtime['checkpointerInitialized'],
        'langgraphCheckpointerBackend': langgraph_runtime['checkpointerBackend'],
        'langgraphThreadIdEnabled': langgraph_runtime['threadIdEnabled'],
        'langgraphHitlEnabled': settings.langgraph_hitl_enabled,
        'langgraphHitlDefaultSlices': settings.langgraph_hitl_default_slices,
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
    bundle = build_engine_bundle(settings, request=request)
    response = await bundle.primary.respond(request=request, settings=settings, engine_mode=bundle.mode)
    shadow_result = await maybe_run_shadow(bundle=bundle, request=request, settings=settings)
    if shadow_result is not None:
        await persist_shadow_trace(
            settings=settings,
            request=request,
            primary_engine_name=bundle.primary.name,
            primary_engine_mode=bundle.mode,
            shadow_result=shadow_result,
        )
    return response


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
    graph = get_langgraph_artifacts(settings).graph
    thread_id = resolve_langgraph_thread_id(
        conversation_external_id=request.conversation_id,
        channel='api',
    )
    state = invoke_orchestration_graph(
        graph=graph,
        state_input={'request': request},
        thread_id=thread_id,
    )
    preview = to_preview(state)
    return {
        'service': 'ai-orchestrator',
        'preview': preview.model_dump(mode='json'),
    }


@app.post('/v1/internal/hitl/review')
async def start_hitl_review(
    request: LangGraphHitlRequest,
    x_internal_api_token: str | None = Header(default=None, alias='X-Internal-Api-Token'),
) -> dict[str, object]:
    _require_internal_api_token(x_internal_api_token)
    settings = get_settings()
    graph = get_langgraph_artifacts(settings).graph
    thread_id = _hitl_thread_id(
        conversation_id=request.conversation_id,
        channel=request.channel,
        telegram_chat_id=request.telegram_chat_id,
    )
    result = invoke_orchestration_graph(
        graph=graph,
        state_input=_build_hitl_state_input(request, settings),
        thread_id=thread_id,
        version='v1',
    )
    snapshot = get_orchestration_state_snapshot(
        graph=graph,
        thread_id=thread_id,
        subgraphs=True,
    ) if thread_id else None
    serialized_snapshot = _serialize_hitl_state_snapshot(snapshot) if snapshot is not None else None
    if isinstance(result, dict) and result.get('__interrupt__'):
        return {
            'service': 'ai-orchestrator',
            'status': 'pending',
            'thread_id': thread_id,
            'interrupts': serialized_snapshot['interrupts'] if serialized_snapshot is not None else [_serialize_interrupt_entry(item) for item in result.get('__interrupt__', [])],
            'snapshot': serialized_snapshot,
        }
    return {
        'service': 'ai-orchestrator',
        'status': 'completed',
        'thread_id': thread_id,
        'preview': (
            serialized_snapshot['preview']
            if serialized_snapshot is not None
            else _build_hitl_preview(result if isinstance(result, dict) else {})
        ),
        'snapshot': serialized_snapshot,
    }


@app.get('/v1/internal/hitl/state')
async def get_hitl_state(
    conversation_id: str | None = None,
    telegram_chat_id: int | None = None,
    channel: ConversationChannel = ConversationChannel.telegram,
    x_internal_api_token: str | None = Header(default=None, alias='X-Internal-Api-Token'),
) -> dict[str, object]:
    _require_internal_api_token(x_internal_api_token)
    settings = get_settings()
    graph = get_langgraph_artifacts(settings).graph
    thread_id = _hitl_thread_id(
        conversation_id=conversation_id,
        channel=channel,
        telegram_chat_id=telegram_chat_id,
    )
    if not thread_id:
        raise HTTPException(status_code=400, detail='conversation_id_or_telegram_chat_id_required')
    snapshot = get_orchestration_state_snapshot(
        graph=graph,
        thread_id=thread_id,
        subgraphs=True,
    )
    serialized = _serialize_hitl_state_snapshot(snapshot)
    return {
        'service': 'ai-orchestrator',
        'thread_id': thread_id,
        'pending': bool(serialized['has_pending_interrupt']),
        'snapshot': serialized,
    }


@app.post('/v1/internal/hitl/resume')
async def resume_hitl_review(
    request: LangGraphHitlResumeRequest,
    x_internal_api_token: str | None = Header(default=None, alias='X-Internal-Api-Token'),
) -> dict[str, object]:
    _require_internal_api_token(x_internal_api_token)
    settings = get_settings()
    graph = get_langgraph_artifacts(settings).graph
    thread_id = _hitl_thread_id(
        conversation_id=request.conversation_id,
        channel=request.channel,
        telegram_chat_id=request.telegram_chat_id,
    )
    if not thread_id:
        raise HTTPException(status_code=400, detail='conversation_id_or_telegram_chat_id_required')
    result = resume_orchestration_graph(
        graph=graph,
        thread_id=thread_id,
        resume_value=request.resume_value,
        version='v1',
    )
    snapshot = get_orchestration_state_snapshot(
        graph=graph,
        thread_id=thread_id,
        subgraphs=True,
    )
    serialized_snapshot = _serialize_hitl_state_snapshot(snapshot)
    if isinstance(result, dict) and result.get('__interrupt__'):
        return {
            'service': 'ai-orchestrator',
            'status': 'pending',
            'thread_id': thread_id,
            'interrupts': serialized_snapshot['interrupts'],
            'snapshot': serialized_snapshot,
        }
    return {
        'service': 'ai-orchestrator',
        'status': 'completed',
        'thread_id': thread_id,
        'preview': serialized_snapshot['preview'] or _build_hitl_preview(result if isinstance(result, dict) else {}),
        'snapshot': serialized_snapshot,
    }
