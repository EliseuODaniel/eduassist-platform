from __future__ import annotations

from contextlib import asynccontextmanager
from functools import lru_cache
import logging
import os
from pathlib import Path
import secrets
from urllib.parse import urlparse, urlunparse

from fastapi import FastAPI, Header, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import BaseModel, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from eduassist_observability import build_runtime_diagnostics, configure_observability, detect_runtime_mode

from .models import SpecialistSupervisorRequest, SpecialistSupervisorResponse
from .telegram_debug_footer import attach_telegram_debug_footer


_ROOT_ENV_FILE = Path(__file__).resolve().parents[4] / ".env"
_INTERNAL_API_TOKEN_PLACEHOLDERS = {"", "dev-internal-token", "change-me-internal-token"}
logger = logging.getLogger(__name__)

_LOCAL_SOURCE_SERVICE_URLS = {
    "api-core": "http://127.0.0.1:8001",
    "ai-orchestrator": "http://127.0.0.1:8002",
    "qdrant": "http://127.0.0.1:6333",
}
_LOCAL_SOURCE_DATABASE_URL = "postgresql://eduassist:eduassist@127.0.0.1:5432/eduassist"
_LOCAL_SOURCE_MEMORY_URL = "sqlite+aiosqlite:///" + str(
    (Path(__file__).resolve().parents[4] / ".runtime" / "specialist_supervisor_memory.db").resolve()
)


def _replace_url_host(value: str, *, replacements: dict[str, str]) -> str:
    normalized = str(value or "").strip()
    if not normalized:
        return normalized
    parsed = urlparse(normalized)
    host = (parsed.hostname or "").strip().lower()
    replacement_host = replacements.get(host)
    if replacement_host is None:
        return normalized
    netloc = replacement_host
    if parsed.port is not None:
        netloc = f"{replacement_host}:{parsed.port}"
    if parsed.username:
        auth = parsed.username
        if parsed.password:
            auth = f"{auth}:{parsed.password}"
        netloc = f"{auth}@{netloc}"
    return urlunparse(parsed._replace(netloc=netloc))


def _normalize_local_service_url(value: str, *, env_name: str) -> str:
    override = str(os.getenv(env_name, "") or "").strip()
    normalized = str(value or "").strip()
    if override:
        return override
    if not normalized:
        return normalized
    parsed = urlparse(normalized)
    host = (parsed.hostname or "").strip().lower()
    replacement = _LOCAL_SOURCE_SERVICE_URLS.get(host)
    if replacement is None:
        return normalized
    replacement_parsed = urlparse(replacement)
    netloc = replacement_parsed.netloc
    if parsed.username:
        auth = parsed.username
        if parsed.password:
            auth = f"{auth}:{parsed.password}"
        netloc = f"{auth}@{netloc}"
    return urlunparse(parsed._replace(scheme=replacement_parsed.scheme, netloc=netloc))


def _normalize_local_database_url(value: str) -> str:
    override = str(os.getenv("DATABASE_URL_LOCAL", "") or "").strip()
    normalized = str(value or "").strip()
    if override:
        return override
    if not normalized:
        return _LOCAL_SOURCE_DATABASE_URL
    return _replace_url_host(
        normalized,
        replacements={
            "postgres": "127.0.0.1",
            "localhost": "127.0.0.1",
        },
    )


def _normalize_local_qdrant_url(value: str) -> str:
    override = str(os.getenv("QDRANT_URL_LOCAL", "") or "").strip()
    normalized = str(value or "").strip()
    if override:
        return override
    if not normalized:
        return _LOCAL_SOURCE_SERVICE_URLS["qdrant"]
    return _replace_url_host(
        normalized,
        replacements={
            "qdrant": "127.0.0.1",
            "localhost": "127.0.0.1",
        },
    )


def _normalize_local_memory_url(value: str) -> str:
    override = str(os.getenv("AGENT_MEMORY_URL_LOCAL", "") or "").strip()
    normalized = str(value or "").strip()
    if override:
        return override
    if not normalized:
        return _LOCAL_SOURCE_MEMORY_URL
    if normalized.startswith("sqlite") and "/workspace/" in normalized:
        return _LOCAL_SOURCE_MEMORY_URL
    if normalized.startswith("postgresql://") or normalized.startswith("postgresql+"):
        return _normalize_local_database_url(normalized)
    return normalized


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        case_sensitive=False,
        env_file=("/workspace/.env", str(_ROOT_ENV_FILE), ".env"),
        env_ignore_empty=True,
        extra='ignore',
    )

    app_env: str = "development"
    log_level: str = "INFO"
    feature_flag_telegram_debug_trace_footer_enabled: bool = False
    port: int = 8000
    llm_model_profile: str | None = None
    llm_provider: str = "auto"
    api_core_url: str = "http://api-core:8000"
    orchestrator_url: str = "http://ai-orchestrator:8000"
    control_plane_orchestrator_url: str | None = None
    internal_api_token: str = "dev-internal-token"
    allow_insecure_internal_api_token: bool = False
    openai_api_key: str | None = None
    openai_base_url: str = "https://api.openai.com/v1"
    openai_model: str = "gpt-5.4"
    openai_api_mode: str = "responses"
    openai_fast_model: str | None = "gpt-5-mini"
    openai_reasoning_model: str | None = "gpt-5.4"
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
    orchestrator_preview_timeout_seconds: float = 2.0
    orchestrator_retrieval_timeout_seconds: float = 3.0
    context_fetch_timeout_seconds: float = 2.0
    public_resource_timeout_seconds: float = 2.0
    database_url: str = "sqlite+aiosqlite:////workspace/.runtime/specialist_supervisor_memory.db"
    agent_memory_url: str = "sqlite+aiosqlite:////workspace/.runtime/specialist_supervisor_memory.db"
    agent_memory_dir: str | None = None
    public_resource_cache_ttl_seconds: float = 120.0
    qdrant_url: str = "http://qdrant:6333"
    qdrant_documents_collection: str = "school_documents"
    document_embedding_model: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    retrieval_enable_query_variants: bool = True
    retrieval_enable_late_interaction_rerank: bool = True
    retrieval_late_interaction_model: str = "answerdotai/answerai-colbert-small-v1"
    retrieval_candidate_pool_size: int = 14
    retrieval_cheap_candidate_pool_size: int = 8
    retrieval_deep_candidate_pool_size: int = 22
    retrieval_rerank_fused_weight: float = 0.35
    retrieval_rerank_late_interaction_weight: float = 0.65

    @model_validator(mode="after")
    def _apply_llm_model_profile(self) -> "Settings":
        profile = str(self.llm_model_profile or "").strip().lower()
        if not profile:
            return self
        if profile in {"gemini_flash_lite", "gemini_2_5_flash_lite", "gemini-2.5-flash-lite"}:
            self.llm_provider = "google"
            if not str(self.google_model or "").strip() or self.google_model == "gemini-2.5-flash":
                self.google_model = "gemini-2.5-flash-lite"
            if not str(self.google_fast_model or "").strip():
                self.google_fast_model = self.google_model
            if not str(self.google_reasoning_model or "").strip():
                self.google_reasoning_model = self.google_model
            return self
        if profile in {"gemma4e4b_local", "gemma_4_e4b_local", "gemma-4-e4b-local"}:
            self.llm_provider = "openai"
            self.openai_api_mode = "chat_completions"
            if not str(self.openai_api_key or "").strip():
                self.openai_api_key = "local-llm"
            if not str(self.openai_base_url or "").strip() or self.openai_base_url == "https://api.openai.com/v1":
                self.openai_base_url = "http://local-llm-gemma4e4b:8080/v1"
            if not str(self.openai_model or "").strip() or self.openai_model == "gpt-5.4":
                self.openai_model = "ggml-org_gemma-4-E4B-it-GGUF_gemma-4-e4b-it-Q4_K_M.gguf"
            if not str(self.openai_fast_model or "").strip() or self.openai_fast_model == "gpt-5-mini":
                self.openai_fast_model = self.openai_model
            if not str(self.openai_reasoning_model or "").strip() or self.openai_reasoning_model == "gpt-5.4":
                self.openai_reasoning_model = self.openai_model
            return self
        return self

    @model_validator(mode="after")
    def _apply_source_mode_network_fallbacks(self) -> "Settings":
        explicit_control_plane = str(self.control_plane_orchestrator_url or "").strip()
        if explicit_control_plane:
            self.orchestrator_url = explicit_control_plane
        if detect_runtime_mode() != "source":
            return self
        self.api_core_url = _normalize_local_service_url(self.api_core_url, env_name="API_CORE_URL_LOCAL")
        self.orchestrator_url = _normalize_local_service_url(self.orchestrator_url, env_name="AI_ORCHESTRATOR_URL_LOCAL")
        if explicit_control_plane:
            self.control_plane_orchestrator_url = self.orchestrator_url
        self.database_url = _normalize_local_database_url(self.database_url)
        self.agent_memory_url = _normalize_local_memory_url(self.agent_memory_url or self.database_url)
        self.qdrant_url = _normalize_local_qdrant_url(self.qdrant_url)
        return self

    @model_validator(mode="after")
    def _validate_internal_api_token(self) -> "Settings":
        token = str(self.internal_api_token or "").strip()
        if token not in _INTERNAL_API_TOKEN_PLACEHOLDERS:
            return self
        if self.allow_insecure_internal_api_token or self.app_env in {"test"}:
            return self
        raise ValueError(
            "internal_api_token must be set to a non-placeholder value; "
            "set INTERNAL_API_TOKEN or explicitly opt into ALLOW_INSECURE_INTERNAL_API_TOKEN=true for isolated tests."
        )


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
    llm_provider = _resolve_llm_provider(settings)
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


def _message_response_payload(payload: dict[str, object], *, request: SpecialistSupervisorRequest) -> dict[str, object]:
    trace_context = dict(request.trace_context or {})
    if request.conversation_id and not str(trace_context.get("conversation_external_id") or "").strip():
        trace_context["conversation_external_id"] = str(request.conversation_id)
    answer = payload.get("answer") if isinstance(payload.get("answer"), dict) else None
    if not isinstance(answer, dict):
        reason = str(payload.get("reason") or "specialist_supervisor_no_answer")
        return {
            "message_text": "Nao consegui formular uma resposta confiavel agora.",
            "mode": "clarify",
            "classification": {
                "domain": "unknown",
                "access_tier": "public",
                "confidence": 0.0,
                "reason": reason,
            },
            "retrieval_backend": "none",
            "selected_tools": [],
            "citations": [],
            "visual_assets": [],
            "suggested_replies": [],
            "calendar_events": [],
            "evidence_pack": None,
            "needs_authentication": False,
            "graph_path": ["specialist_supervisor", "message_contract_fallback"],
            "risk_flags": ["contract_fallback"],
            "reason": reason,
            "used_llm": False,
            "llm_stages": [],
            "final_polish_eligible": False,
            "final_polish_applied": False,
            "final_polish_mode": "skip",
            "final_polish_reason": "no_specialist_answer",
            "final_polish_changed_text": False,
            "final_polish_preserved_fallback": False,
            "candidate_chosen": "specialist_supervisor",
            "candidate_reason": "specialist_local_contract",
            "retrieval_probe_topic": None,
            "response_cache_hit": False,
            "response_cache_kind": None,
            "answer_experience_eligible": False,
            "answer_experience_applied": False,
            "answer_experience_reason": None,
            "answer_experience_provider": None,
            "answer_experience_model": None,
            "context_repair_applied": False,
            "context_repair_action": None,
            "context_repair_reason": None,
            "retrieval_retry_applied": False,
            "retrieval_retry_reason": None,
            "debug_trace": {
                "specialist": {
                    "service": "ai-orchestrator-specialist",
                    "mode": "quality-first",
                    "reason": reason,
                },
                "trace_context": trace_context,
            },
        }

    graph_path = [str(item).strip() for item in answer.get("graph_path", []) if str(item).strip()]
    if not graph_path:
        graph_path = ["specialist_supervisor", "local_runtime"]
    return {
        "message_text": str(answer.get("message_text") or ""),
        "mode": str(answer.get("mode") or "clarify"),
        "classification": dict(answer.get("classification") or {}),
        "retrieval_backend": str(answer.get("retrieval_backend") or "none"),
        "selected_tools": list(answer.get("selected_tools") or []),
        "citations": list(answer.get("citations") or []),
        "visual_assets": list(answer.get("visual_assets") or []),
        "suggested_replies": list(answer.get("suggested_replies") or []),
        "calendar_events": list(answer.get("calendar_events") or []),
        "evidence_pack": answer.get("evidence_pack"),
        "needs_authentication": bool(answer.get("needs_authentication", False)),
        "graph_path": graph_path,
        "risk_flags": list(answer.get("risk_flags") or []),
        "reason": str(answer.get("reason") or payload.get("reason") or "specialist_local_contract"),
        "used_llm": bool(answer.get("used_llm", False)),
        "llm_stages": list(answer.get("llm_stages") or []),
        "final_polish_eligible": bool(answer.get("final_polish_eligible", False)),
        "final_polish_applied": bool(answer.get("final_polish_applied", False)),
        "final_polish_mode": answer.get("final_polish_mode"),
        "final_polish_reason": answer.get("final_polish_reason"),
        "final_polish_changed_text": bool(answer.get("final_polish_changed_text", False)),
        "final_polish_preserved_fallback": bool(answer.get("final_polish_preserved_fallback", False)),
        "candidate_chosen": "specialist_supervisor",
        "candidate_reason": str(payload.get("reason") or "specialist_local_contract"),
        "retrieval_probe_topic": None,
        "response_cache_hit": False,
        "response_cache_kind": None,
        "answer_experience_eligible": False,
        "answer_experience_applied": False,
        "answer_experience_reason": None,
        "answer_experience_provider": None,
        "answer_experience_model": None,
        "context_repair_applied": False,
        "context_repair_action": None,
        "context_repair_reason": None,
        "retrieval_retry_applied": False,
        "retrieval_retry_reason": None,
        "debug_trace": {
            "specialist": {
                "service": "ai-orchestrator-specialist",
                "mode": "quality-first",
                "reason": str(payload.get("reason") or "specialist_local_contract"),
            },
            "trace_context": trace_context,
        },
    }


def _resolve_llm_provider(settings: Settings) -> str:
    from .runtime import resolve_llm_provider

    return resolve_llm_provider(settings)


def _effective_llm_model_name(settings: Settings) -> str:
    from .runtime import effective_llm_model_name

    return effective_llm_model_name(settings)


async def _run_specialist(request: SpecialistSupervisorRequest, settings: Settings) -> dict[str, object]:
    from .runtime import run_specialist_supervisor

    try:
        return await run_specialist_supervisor(request=request, settings=settings)
    except Exception as exc:
        logger.exception("specialist_supervisor_request_failed")
        return {
            "engine_name": "specialist_supervisor",
            "executed": True,
            "reason": "specialist_supervisor_request_failed_fallback",
            "metadata": {
                "provider": _resolve_llm_provider(settings),
                "model": _effective_llm_model_name(settings),
                "request_failed": True,
                "error_type": exc.__class__.__name__,
            },
            "answer": {
                "message_text": (
                    "Tive uma falha interna ao tentar montar essa resposta. "
                    "Para nao te devolver algo inconsistente, fiquei no fallback seguro: "
                    "posso responder apenas o que estiver sustentado no material publico ou reabrir a pergunta em um recorte mais especifico."
                ),
                "mode": "deny",
                "classification": {
                    "domain": "institution",
                    "access_tier": "public",
                    "confidence": 0.45,
                    "reason": "specialist_supervisor_request_failed_fallback",
                },
                "retrieval_backend": "none",
                "selected_tools": [],
                "citations": [],
                "visual_assets": [],
                "suggested_replies": [],
                "calendar_events": [],
                "evidence_pack": {
                    "strategy": "deny",
                    "summary": "Fallback seguro apos falha interna do specialist.",
                    "source_count": 0,
                    "support_count": 1,
                    "supports": [
                        {
                            "kind": "runtime_fallback",
                            "label": "Falha interna controlada",
                            "detail": exc.__class__.__name__,
                        }
                    ],
                },
                "needs_authentication": False,
                "graph_path": ["specialist_supervisor", "fallback", "request_failed"],
                "risk_flags": ["request_failed"],
                "reason": "specialist_supervisor_request_failed_fallback",
                "used_llm": False,
                "llm_stages": [],
                "final_polish_eligible": False,
                "final_polish_applied": False,
                "final_polish_mode": "skip",
                "final_polish_reason": "request_failed_fallback",
                "final_polish_changed_text": False,
                "final_polish_preserved_fallback": True,
            },
        }


@asynccontextmanager
async def _app_lifespan(_: FastAPI):
    _log_runtime_diagnostics(_specialist_runtime_diagnostics(get_settings()))
    yield


app = FastAPI(
    title="EduAssist Specialist Supervisor Pilot",
    version="0.1.0",
    summary="Quality-first specialist supervisor service for side-by-side chatbot comparisons.",
    lifespan=_app_lifespan,
)

configure_observability(
    service_name="ai-orchestrator-specialist",
    service_version=app.version,
    environment=get_settings().app_env,
    app=app,
    excluded_urls="/healthz",
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
    llm_provider = _resolve_llm_provider(settings)
    runtime_diagnostics = _specialist_runtime_diagnostics(settings)
    return {
        "service": "ai-orchestrator-specialist",
        "ready": True,
        "serviceRole": "dedicated-stack-runtime",
        "primaryServingRecommended": True,
        "mode": "quality-first",
        "llmModelProfile": settings.llm_model_profile,
        "llmProvider": llm_provider,
        "effectiveModel": _effective_llm_model_name(settings),
        "openaiApiMode": settings.openai_api_mode,
        "openaiModel": settings.openai_model,
        "googleModel": settings.google_model,
        "llmConfigured": llm_provider != "unconfigured",
        "apiCoreUrl": settings.api_core_url,
        "orchestratorUrl": settings.orchestrator_url,
        "controlPlaneOrchestratorUrl": settings.orchestrator_url,
        "controlPlanePurpose": [
            "shared-graphrag-consumer",
            "router-internal-endpoints",
        ],
        "runtimeDiagnostics": runtime_diagnostics,
        "capabilities": [
            "openai-agents-sdk",
            "litellm-provider-fallback",
            "manager-pattern",
            "specialists-as-tools",
            "sqlalchemy-session-memory",
            "planner-manager-judge",
            "specialist-local-hybrid-retrieval",
            "shared-graphrag-consumer",
            "workflow-and-record-specialists",
            "message-response-contract",
        ],
    }


@app.post("/v1/respond", response_model=SpecialistSupervisorResponse)
async def respond(
    request: SpecialistSupervisorRequest,
    x_internal_api_token: str | None = Header(default=None, alias="X-Internal-Api-Token"),
) -> SpecialistSupervisorResponse:
    _require_internal_api_token(x_internal_api_token)
    settings = get_settings()
    payload = await _run_specialist(request=request, settings=settings)
    return SpecialistSupervisorResponse.model_validate(payload)


@app.post("/v1/respond-raw")
async def respond_raw(
    request: SpecialistSupervisorRequest,
    x_internal_api_token: str | None = Header(default=None, alias="X-Internal-Api-Token"),
) -> JSONResponse:
    _require_internal_api_token(x_internal_api_token)
    settings = get_settings()
    payload = await _run_specialist(request=request, settings=settings)
    return JSONResponse(content=jsonable_encoder(payload))


@app.post("/v1/messages/respond")
async def respond_message_contract(
    request: SpecialistSupervisorRequest,
    x_internal_api_token: str | None = Header(default=None, alias="X-Internal-Api-Token"),
) -> JSONResponse:
    _require_internal_api_token(x_internal_api_token)
    settings = get_settings()
    payload = await _run_specialist(request=request, settings=settings)
    message_payload = _message_response_payload(payload, request=request)
    message_payload = attach_telegram_debug_footer(message_payload, request=request, settings=settings)
    return JSONResponse(content=jsonable_encoder(message_payload))
