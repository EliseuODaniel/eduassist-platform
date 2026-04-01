from __future__ import annotations

from functools import lru_cache
from pathlib import Path
import secrets

from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from .crewai_hitl import HumanFeedbackPending, load_pending_feedback_snapshot
from .flow_persistence import DEFAULT_FLOW_STATE_DIR, build_flow_state_id, get_sqlite_flow_persistence
from .listeners import suppress_crewai_tracing_messages
from .public_pilot import run_public_crewai_pilot
from .protected_pilot import run_protected_crewai_pilot
from .support_pilot import run_support_crewai_pilot
from .workflow_pilot import run_workflow_crewai_pilot

try:
    import crewai  # type: ignore
except Exception:  # pragma: no cover - defensive import
    crewai = None


_ROOT_ENV_FILE = Path(__file__).resolve().parents[4] / '.env'


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        case_sensitive=False,
        env_file=('/workspace/.env', str(_ROOT_ENV_FILE), '.env'),
        env_ignore_empty=True,
        extra='ignore',
    )

    app_env: str = 'development'
    log_level: str = 'INFO'
    port: int = 8000
    api_core_url: str = 'http://api-core:8000'
    orchestrator_url: str = 'http://ai-orchestrator:8000'
    internal_api_token: str = 'dev-internal-token'
    google_api_key: str | None = None
    google_model: str = 'gemini-2.5-flash-preview'
    crewai_flow_state_dir: str = DEFAULT_FLOW_STATE_DIR
    shared_retrieval_enabled: bool = True
    shared_retrieval_top_k: int = 6
    crewai_hitl_enabled: bool = True
    crewai_hitl_default_slices: str = 'protected'
    crewai_hitl_user_traffic_enabled: bool = False
    crewai_hitl_user_traffic_slices: str = 'protected'
    crewai_llm_timeout_seconds: float = 15.0
    crewai_flow_timeout_seconds: float = 20.0
    crewai_public_resource_cache_ttl_seconds: float = 120.0


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


class ShadowPilotRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
    conversation_id: str | None = None
    telegram_chat_id: int | None = None
    channel: str = 'telegram'
    user: dict[str, object] | None = None


class ShadowPilotResponse(BaseModel):
    engine_name: str
    executed: bool
    reason: str
    metadata: dict[str, object] = Field(default_factory=dict)


class CrewAIHitlResumeRequest(BaseModel):
    flow_state_id: str | None = None
    conversation_id: str | None = None
    telegram_chat_id: int | None = None
    channel: str = 'telegram'
    feedback: str = Field(min_length=1, max_length=200)


def _protected_flow_state_id(*, flow_state_id: str | None, conversation_id: str | None, telegram_chat_id: int | None, channel: str) -> str | None:
    if flow_state_id:
        return flow_state_id
    return build_flow_state_id(
        slice_name='protected',
        conversation_id=conversation_id,
        telegram_chat_id=telegram_chat_id,
        channel=channel,
    )


app = FastAPI(
    title='EduAssist CrewAI Pilot',
    version='0.1.0',
    summary='Isolated CrewAI pilot service for side-by-side agent comparisons.',
)


@app.get('/healthz', response_model=HealthResponse)
async def healthz() -> HealthResponse:
    return HealthResponse(status='ok', service='ai-orchestrator-crewai', ready=True)


@app.get('/v1/status')
async def status(
    x_internal_api_token: str | None = Header(default=None, alias='X-Internal-Api-Token'),
) -> dict[str, object]:
    _require_internal_api_token(x_internal_api_token)
    settings = get_settings()
    return {
        'service': 'ai-orchestrator-crewai',
        'ready': True,
        'crewaiInstalled': crewai is not None,
        'crewaiVersion': getattr(crewai, '__version__', None),
        'slice': 'public+protected+workflow+support',
        'mode': 'pilot',
        'googleModel': settings.google_model,
        'llmConfigured': bool(settings.google_api_key),
        'sharedRetrievalEnabled': settings.shared_retrieval_enabled,
        'sharedRetrievalTopK': settings.shared_retrieval_top_k,
        'orchestratorUrl': settings.orchestrator_url,
        'capabilities': [
            'public-shadow-flow',
            'protected-shadow-flow',
            'workflow-shadow-flow',
            'support-shadow-flow',
            'isolated-dependencies',
            'planner-composer-judge',
            'flow-state-routing',
            'flow-state-persistence',
            'task-trace-telemetry',
            'task-guardrails',
            'agentic-rendering-for-support-workflow',
            'shared-retrieval-consumer',
            'crewai-hitl-internal',
            'crewai-hitl-user-traffic',
        ],
        'flowStateDir': settings.crewai_flow_state_dir,
        'crewaiHitlEnabled': settings.crewai_hitl_enabled,
        'crewaiHitlDefaultSlices': settings.crewai_hitl_default_slices,
        'crewaiHitlUserTrafficEnabled': settings.crewai_hitl_user_traffic_enabled,
        'crewaiHitlUserTrafficSlices': settings.crewai_hitl_user_traffic_slices,
    }


@app.post('/v1/shadow/public', response_model=ShadowPilotResponse)
async def shadow_public(
    request: ShadowPilotRequest,
    x_internal_api_token: str | None = Header(default=None, alias='X-Internal-Api-Token'),
) -> ShadowPilotResponse:
    _require_internal_api_token(x_internal_api_token)
    settings = get_settings()
    result = await run_public_crewai_pilot(
        message=request.message,
        conversation_id=request.conversation_id,
        telegram_chat_id=request.telegram_chat_id,
        channel=request.channel,
        user_context=request.user,
        settings=settings,
    )
    return ShadowPilotResponse(**result)


@app.post('/v1/shadow/protected', response_model=ShadowPilotResponse)
async def shadow_protected(
    request: ShadowPilotRequest,
    x_internal_api_token: str | None = Header(default=None, alias='X-Internal-Api-Token'),
) -> ShadowPilotResponse:
    _require_internal_api_token(x_internal_api_token)
    settings = get_settings()
    result = await run_protected_crewai_pilot(
        message=request.message,
        conversation_id=request.conversation_id,
        telegram_chat_id=request.telegram_chat_id,
        channel=request.channel,
        user_context=request.user,
        settings=settings,
    )
    return ShadowPilotResponse(**result)


@app.post('/v1/internal/hitl/review/protected')
async def start_protected_hitl_review(
    request: ShadowPilotRequest,
    x_internal_api_token: str | None = Header(default=None, alias='X-Internal-Api-Token'),
) -> dict[str, object]:
    _require_internal_api_token(x_internal_api_token)
    settings = get_settings()
    result = await run_protected_crewai_pilot(
        message=request.message,
        conversation_id=request.conversation_id,
        telegram_chat_id=request.telegram_chat_id,
        channel=request.channel,
        user_context=request.user,
        settings=settings,
        force_hitl=True,
        hitl_target_slices=['protected'],
    )
    metadata = result.get('metadata') if isinstance(result.get('metadata'), dict) else {}
    flow_state_id = str(metadata.get('review_flow_id') or metadata.get('flow_state_id') or '') or None
    snapshot = load_pending_feedback_snapshot(slice_name='protected', flow_id=flow_state_id) if flow_state_id else None
    return {
        'service': 'ai-orchestrator-crewai',
        'status': 'pending' if bool(metadata.get('pending_review')) else 'completed',
        'flow_state_id': flow_state_id,
        'result': result,
        'snapshot': snapshot,
    }


@app.get('/v1/internal/hitl/state/protected')
async def get_protected_hitl_state(
    flow_state_id: str | None = None,
    conversation_id: str | None = None,
    telegram_chat_id: int | None = None,
    channel: str = 'telegram',
    x_internal_api_token: str | None = Header(default=None, alias='X-Internal-Api-Token'),
) -> dict[str, object]:
    _require_internal_api_token(x_internal_api_token)
    resolved_flow_id = _protected_flow_state_id(
        flow_state_id=flow_state_id,
        conversation_id=conversation_id,
        telegram_chat_id=telegram_chat_id,
        channel=channel,
    )
    if not resolved_flow_id:
        raise HTTPException(status_code=400, detail='flow_state_id_or_conversation_required')
    snapshot = load_pending_feedback_snapshot(slice_name='protected', flow_id=resolved_flow_id)
    return {
        'service': 'ai-orchestrator-crewai',
        'flow_state_id': resolved_flow_id,
        'pending': bool(snapshot),
        'snapshot': snapshot,
    }


@app.post('/v1/internal/hitl/resume/protected')
async def resume_protected_hitl_review(
    request: CrewAIHitlResumeRequest,
    x_internal_api_token: str | None = Header(default=None, alias='X-Internal-Api-Token'),
) -> dict[str, object]:
    _require_internal_api_token(x_internal_api_token)
    settings = get_settings()
    resolved_flow_id = _protected_flow_state_id(
        flow_state_id=request.flow_state_id,
        conversation_id=request.conversation_id,
        telegram_chat_id=request.telegram_chat_id,
        channel=request.channel,
    )
    if not resolved_flow_id:
        raise HTTPException(status_code=400, detail='flow_state_id_or_conversation_required')

    from .protected_flow import ProtectedShadowFlow

    persistence = get_sqlite_flow_persistence('protected')
    if persistence is None:
        raise HTTPException(status_code=503, detail='protected_hitl_persistence_unavailable')
    try:
        flow = ProtectedShadowFlow.from_pending(
            resolved_flow_id,
            persistence=persistence,
            settings=settings,
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    with suppress_crewai_tracing_messages():
        result = await flow.resume_async(request.feedback)

    if HumanFeedbackPending is not None and isinstance(result, HumanFeedbackPending):
        snapshot = load_pending_feedback_snapshot(slice_name='protected', flow_id=resolved_flow_id)
        return {
            'service': 'ai-orchestrator-crewai',
            'status': 'pending',
            'flow_state_id': resolved_flow_id,
            'snapshot': snapshot,
        }
    if isinstance(result, dict):
        snapshot = load_pending_feedback_snapshot(slice_name='protected', flow_id=resolved_flow_id)
        return {
            'service': 'ai-orchestrator-crewai',
            'status': 'completed',
            'flow_state_id': resolved_flow_id,
            'result': result,
            'snapshot': snapshot,
        }
    return {
        'service': 'ai-orchestrator-crewai',
        'status': 'completed',
        'flow_state_id': resolved_flow_id,
        'result': {
            'engine_name': 'crewai',
            'executed': False,
            'reason': 'crewai_protected_hitl_resume_unexpected_output',
            'metadata': {},
        },
        'snapshot': load_pending_feedback_snapshot(slice_name='protected', flow_id=resolved_flow_id),
    }


@app.post('/v1/shadow/workflow', response_model=ShadowPilotResponse)
async def shadow_workflow(
    request: ShadowPilotRequest,
    x_internal_api_token: str | None = Header(default=None, alias='X-Internal-Api-Token'),
) -> ShadowPilotResponse:
    _require_internal_api_token(x_internal_api_token)
    settings = get_settings()
    result = await run_workflow_crewai_pilot(
        message=request.message,
        conversation_id=request.conversation_id,
        telegram_chat_id=request.telegram_chat_id,
        channel=request.channel,
        user_context=request.user,
        settings=settings,
    )
    return ShadowPilotResponse(**result)


@app.post('/v1/shadow/support', response_model=ShadowPilotResponse)
async def shadow_support(
    request: ShadowPilotRequest,
    x_internal_api_token: str | None = Header(default=None, alias='X-Internal-Api-Token'),
) -> ShadowPilotResponse:
    _require_internal_api_token(x_internal_api_token)
    settings = get_settings()
    result = await run_support_crewai_pilot(
        message=request.message,
        conversation_id=request.conversation_id,
        telegram_chat_id=request.telegram_chat_id,
        channel=request.channel,
        settings=settings,
    )
    return ShadowPilotResponse(**result)
