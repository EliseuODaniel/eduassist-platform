from __future__ import annotations

from functools import lru_cache
import secrets

from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

from .models import SpecialistSupervisorRequest, SpecialistSupervisorResponse
from .runtime import effective_llm_model_name, resolve_llm_provider, run_specialist_supervisor


class Settings(BaseSettings):
    model_config = SettingsConfigDict(case_sensitive=False)

    app_env: str = "development"
    log_level: str = "INFO"
    port: int = 8000
    llm_provider: str = "auto"
    api_core_url: str = "http://api-core:8000"
    orchestrator_url: str = "http://ai-orchestrator:8000"
    internal_api_token: str = "dev-internal-token"
    openai_api_key: str | None = None
    openai_base_url: str = "https://api.openai.com/v1"
    openai_model: str = "gpt-5.4"
    google_api_key: str | None = None
    google_model: str = "gemini-2.5-flash"
    database_url: str = "sqlite+aiosqlite:////workspace/.runtime/specialist_supervisor_memory.db"


@lru_cache
def get_settings() -> Settings:
    return Settings()


def _require_internal_api_token(x_internal_api_token: str | None) -> None:
    settings = get_settings()
    if not x_internal_api_token or not secrets.compare_digest(x_internal_api_token, settings.internal_api_token):
        raise HTTPException(status_code=401, detail="invalid_internal_api_token")


class HealthResponse(BaseModel):
    status: str
    service: str
    ready: bool


app = FastAPI(
    title="EduAssist Specialist Supervisor Pilot",
    version="0.1.0",
    summary="Quality-first specialist supervisor service for side-by-side chatbot comparisons.",
)


@app.get("/healthz", response_model=HealthResponse)
async def healthz() -> HealthResponse:
    return HealthResponse(status="ok", service="ai-orchestrator-specialist", ready=True)


@app.get("/v1/status")
async def status(
    x_internal_api_token: str | None = Header(default=None, alias="X-Internal-Api-Token"),
) -> dict[str, object]:
    _require_internal_api_token(x_internal_api_token)
    settings = get_settings()
    llm_provider = resolve_llm_provider(settings)
    return {
        "service": "ai-orchestrator-specialist",
        "ready": True,
        "mode": "quality-first",
        "llmProvider": llm_provider,
        "effectiveModel": effective_llm_model_name(settings),
        "openaiModel": settings.openai_model,
        "googleModel": settings.google_model,
        "llmConfigured": llm_provider != "unconfigured",
        "apiCoreUrl": settings.api_core_url,
        "orchestratorUrl": settings.orchestrator_url,
        "capabilities": [
            "openai-agents-sdk",
            "litellm-provider-fallback",
            "manager-pattern",
            "specialists-as-tools",
            "sqlalchemy-session-memory",
            "planner-manager-judge",
            "shared-hybrid-retrieval-consumer",
            "shared-graphrag-consumer",
            "workflow-and-record-specialists",
        ],
    }


@app.post("/v1/respond", response_model=SpecialistSupervisorResponse)
async def respond(
    request: SpecialistSupervisorRequest,
    x_internal_api_token: str | None = Header(default=None, alias="X-Internal-Api-Token"),
) -> SpecialistSupervisorResponse:
    _require_internal_api_token(x_internal_api_token)
    settings = get_settings()
    payload = await run_specialist_supervisor(request=request, settings=settings)
    return SpecialistSupervisorResponse.model_validate(payload)
