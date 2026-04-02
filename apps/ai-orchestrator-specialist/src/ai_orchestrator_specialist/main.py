from __future__ import annotations

from functools import lru_cache
import logging
from pathlib import Path
import secrets

from fastapi import FastAPI, Header, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict
from eduassist_observability import build_runtime_diagnostics, configure_observability, detect_runtime_mode

from .models import SpecialistSupervisorRequest, SpecialistSupervisorResponse
from .runtime import effective_llm_model_name, resolve_llm_provider, run_specialist_supervisor


_ROOT_ENV_FILE = Path(__file__).resolve().parents[4] / ".env"
logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        case_sensitive=False,
        env_file=("/workspace/.env", str(_ROOT_ENV_FILE), ".env"),
        env_ignore_empty=True,
        extra='ignore',
    )

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
    openai_fast_model: str | None = None
    openai_reasoning_model: str | None = None
    google_api_key: str | None = None
    google_model: str = "gemini-2.5-flash"
    google_fast_model: str | None = None
    google_reasoning_model: str | None = None
    planner_model: str | None = None
    specialist_model: str | None = None
    manager_model: str | None = None
    judge_model: str | None = None
    repair_model: str | None = None
    guardrail_model: str | None = None
    graph_rag_sync_timeout_seconds: float = 12.0
    graph_rag_sync_method: str = "local"
    graph_rag_sync_fallback_enabled: bool = False
    database_url: str = "sqlite+aiosqlite:////workspace/.runtime/specialist_supervisor_memory.db"
    agent_memory_url: str = "sqlite+aiosqlite:////workspace/.runtime/specialist_supervisor_memory.db"
    agent_memory_dir: str | None = None
    public_resource_cache_ttl_seconds: float = 120.0


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


def _specialist_runtime_diagnostics(settings: Settings) -> dict[str, object]:
    llm_provider = resolve_llm_provider(settings)
    runtime_mode = detect_runtime_mode()
    extra_findings: list[dict[str, str]] = []
    if llm_provider == "unconfigured":
        extra_findings.append(
            {
                "level": "blocker",
                "code": "llm_provider_unconfigured",
                "message": "Nenhum provider LLM esta configurado para o specialist supervisor.",
            }
        )
    memory_url = str(settings.agent_memory_url or settings.database_url or "").strip()
    if runtime_mode == "source" and memory_url.startswith("sqlite") and "/workspace/" in memory_url:
        extra_findings.append(
            {
                "level": "warning",
                "code": "sqlite_workspace_path_in_source",
                "message": "Agent memory usa caminho /workspace em runtime source, o que tende a gerar drift fora do container.",
            }
        )
    diagnostics = build_runtime_diagnostics(
        service_name="ai-orchestrator-specialist",
        env_file_candidates=("/workspace/.env", str(_ROOT_ENV_FILE), ".env"),
        service_checks=[
            {"name": "api_core", "endpoint": settings.api_core_url, "required": True},
            {"name": "ai_orchestrator", "endpoint": settings.orchestrator_url, "required": True},
        ],
        secret_checks=[
            {
                "name": "internal_api_token",
                "value": settings.internal_api_token,
                "required": True,
                "placeholder_values": ("dev-internal-token",),
            },
            {"name": "openai_api_key", "value": settings.openai_api_key, "required": False},
            {"name": "google_api_key", "value": settings.google_api_key, "required": False},
        ],
        extra_findings=extra_findings,
    )
    diagnostics["memoryBackend"] = "sqlite" if memory_url.startswith("sqlite") else "sqlalchemy"
    diagnostics["memoryUrl"] = memory_url
    return diagnostics


def _log_runtime_diagnostics(diagnostics: dict[str, object]) -> None:
    warnings = diagnostics.get("warnings") if isinstance(diagnostics.get("warnings"), list) else []
    blockers = diagnostics.get("blockers") if isinstance(diagnostics.get("blockers"), list) else []
    logger.info(
        "ai_orchestrator_specialist_runtime_diagnostics",
        extra={
            "operational_readiness": bool(diagnostics.get("operationalReadiness")),
            "runtime_mode": diagnostics.get("runtimeMode"),
            "source_container_drift_risk": diagnostics.get("sourceContainerDriftRisk"),
            "warning_count": len(warnings),
            "blocker_count": len(blockers),
        },
    )
    for item in warnings:
        if isinstance(item, dict):
            logger.warning("ai_orchestrator_specialist_runtime_warning %s", str(item.get("message") or item.get("code") or "warning"))
    for item in blockers:
        if isinstance(item, dict):
            logger.error("ai_orchestrator_specialist_runtime_blocker %s", str(item.get("message") or item.get("code") or "blocker"))


app = FastAPI(
    title="EduAssist Specialist Supervisor Pilot",
    version="0.1.0",
    summary="Quality-first specialist supervisor service for side-by-side chatbot comparisons.",
)

configure_observability(
    service_name="ai-orchestrator-specialist",
    service_version=app.version,
    environment=get_settings().app_env,
    app=app,
    excluded_urls="/healthz",
)


@app.on_event("startup")
async def log_startup_diagnostics() -> None:
    _log_runtime_diagnostics(_specialist_runtime_diagnostics(get_settings()))


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
    runtime_diagnostics = _specialist_runtime_diagnostics(settings)
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
        "runtimeDiagnostics": runtime_diagnostics,
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


@app.post("/v1/respond-raw")
async def respond_raw(
    request: SpecialistSupervisorRequest,
    x_internal_api_token: str | None = Header(default=None, alias="X-Internal-Api-Token"),
) -> JSONResponse:
    _require_internal_api_token(x_internal_api_token)
    settings = get_settings()
    payload = await run_specialist_supervisor(request=request, settings=settings)
    return JSONResponse(content=jsonable_encoder(payload))
