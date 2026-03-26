from __future__ import annotations

from functools import lru_cache
import secrets

from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from .public_pilot import run_public_crewai_pilot
from .protected_pilot import run_protected_crewai_pilot

try:
    import crewai  # type: ignore
except Exception:  # pragma: no cover - defensive import
    crewai = None


class Settings(BaseSettings):
    model_config = SettingsConfigDict(case_sensitive=False)

    app_env: str = 'development'
    log_level: str = 'INFO'
    port: int = 8000
    api_core_url: str = 'http://api-core:8000'
    internal_api_token: str = 'dev-internal-token'
    google_api_key: str | None = None
    google_model: str = 'gemini-2.5-flash-preview'


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


class ShadowPilotResponse(BaseModel):
    engine_name: str
    executed: bool
    reason: str
    metadata: dict[str, object] = Field(default_factory=dict)


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
        'slice': 'public+protected',
        'mode': 'pilot',
        'googleModel': settings.google_model,
        'llmConfigured': bool(settings.google_api_key),
        'capabilities': ['public-shadow-slice', 'protected-shadow-slice', 'isolated-dependencies', 'planner-composer-judge'],
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
        settings=settings,
    )
    return ShadowPilotResponse(**result)
