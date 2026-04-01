from __future__ import annotations

import asyncio
from functools import lru_cache
import json
import logging
import secrets
from pathlib import Path
from time import monotonic
from typing import Any
from urllib.error import URLError
from urllib.request import Request, urlopen

from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from eduassist_observability import build_runtime_diagnostics, configure_observability

from .engine_selector import (
    SUPPORTED_PRIMARY_STACKS,
    build_engine_bundle,
    clear_runtime_targeted_stack_override,
    clear_runtime_primary_stack_override,
    get_experiment_live_promotion_summary,
    get_experiment_rollout_readiness,
    get_primary_stack_resolution,
    get_runtime_targeted_stack_override,
    get_runtime_primary_stack_override,
    get_scorecard_gate_status,
    maybe_run_shadow,
    resolve_primary_stack,
    set_runtime_targeted_stack_override,
    set_runtime_primary_stack_override,
)
from .engines.llamaindex_workflow_engine import LLAMAINDEX_WORKFLOW_AVAILABLE
from .graph import get_graph_blueprint, to_preview
from .graph_rag_runtime import graph_rag_workspace_ready, run_graph_rag_query
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

logger = logging.getLogger(__name__)
REPO_ROOT = Path(__file__).resolve().parents[4]
ROOT_ENV_FILE = REPO_ROOT / '.env'
FOUR_PATH_COMPARISON_REPORT_JSON = REPO_ROOT / 'docs/architecture/four-path-chatbot-comparison-report.json'
FOUR_PATH_SMOKE_REPORT_JSON = REPO_ROOT / 'docs/architecture/four-path-chatbot-smoke-report.json'
_REMOTE_STATUS_CACHE: dict[str, dict[str, Any]] = {}


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        case_sensitive=False,
        env_file=('/workspace/.env', str(ROOT_ENV_FILE), '.env'),
        env_ignore_empty=True,
        extra='ignore',
    )

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
    llamaindex_qdrant_documents_collection: str = 'school_documents_llamaindex'
    llamaindex_native_timeout_seconds: float = 20.0
    document_embedding_model: str = 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'
    warm_retrieval_on_startup: bool = True
    retrieval_enable_query_variants: bool = True
    retrieval_enable_late_interaction_rerank: bool = True
    retrieval_late_interaction_model: str = 'answerdotai/answerai-colbert-small-v1'
    retrieval_candidate_pool_size: int = 12
    strict_framework_isolation_enabled: bool = False
    graph_rag_enabled: bool = False
    graph_rag_workspace: str = '/workspace/artifacts/graphrag/eduassist-public-benchmark'
    graph_rag_response_type: str = 'List of 3-5 concise bullet points in Brazilian Portuguese'
    graph_rag_local_chat_api_base: str = 'http://host.docker.internal:18080/v1'
    graph_rag_local_embedding_api_base: str = 'http://host.docker.internal:11435/v1'
    graph_rag_local_chat_api_key: str = 'llama.cpp'
    graph_rag_local_embedding_api_key: str = 'ollama'
    orchestrator_engine: str = 'langgraph'
    feature_flag_primary_orchestration_stack: str | None = None
    feature_flag_telegram_debug_trace_footer_enabled: bool = False
    crewai_pilot_url: str | None = None
    crewai_pilot_timeout_seconds: float = 30.0
    specialist_supervisor_pilot_url: str | None = None
    specialist_supervisor_pilot_timeout_seconds: float = 75.0
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
    langgraph_hitl_user_traffic_enabled: bool = False
    langgraph_hitl_user_traffic_slices: str = 'support'


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


class RuntimePrimaryStackUpdateRequest(BaseModel):
    stack: str | None = None
    reason: str | None = None
    operator: str | None = None
    clear_override: bool = False


class RuntimeTargetedStackUpdateRequest(BaseModel):
    stack: str | None = None
    reason: str | None = None
    operator: str | None = None
    clear_override: bool = False
    ttl_seconds: int | None = Field(default=None, ge=60, le=86400)
    slices: list[str] = Field(default_factory=list)
    telegram_chat_allowlist: list[str] = Field(default_factory=list)
    conversation_allowlist: list[str] = Field(default_factory=list)


class GraphRagQueryRequest(BaseModel):
    query: str = Field(min_length=3, max_length=4000)


def _normalized_hitl_slices(values: list[str] | None, *, fallback: str) -> list[str]:
    normalized = [str(item).strip() for item in (values or []) if str(item).strip()]
    if normalized:
        return normalized
    return [item.strip() for item in fallback.split(',') if item.strip()] or ['support']


def _csv_count(value: str | None) -> int:
    return len([item.strip() for item in str(value or '').split(',') if item.strip()])


def _runtime_primary_stack_payload(settings: Settings) -> dict[str, object]:
    resolution = get_primary_stack_resolution(settings)
    runtime_override = resolution.get('runtime_override')
    targeted_override = get_runtime_targeted_stack_override()
    return {
        'orchestratorEngine': settings.orchestrator_engine,
        'primaryStackFeatureFlag': settings.feature_flag_primary_orchestration_stack,
        'resolvedPrimaryStack': resolution.get('resolved'),
        'resolvedPrimaryStackSource': resolution.get('source'),
        'runtimePrimaryStackOverride': runtime_override.get('value') if isinstance(runtime_override, dict) else None,
        'runtimePrimaryStackOverrideReason': runtime_override.get('reason') if isinstance(runtime_override, dict) else None,
        'runtimePrimaryStackOverrideOperator': runtime_override.get('operator') if isinstance(runtime_override, dict) else None,
        'runtimePrimaryStackOverrideUpdatedAt': runtime_override.get('updated_at') if isinstance(runtime_override, dict) else None,
        'runtimeTargetedStackOverride': targeted_override.get('value') if isinstance(targeted_override, dict) else None,
        'runtimeTargetedStackOverrideReason': targeted_override.get('reason') if isinstance(targeted_override, dict) else None,
        'runtimeTargetedStackOverrideOperator': targeted_override.get('operator') if isinstance(targeted_override, dict) else None,
        'runtimeTargetedStackOverrideUpdatedAt': targeted_override.get('updated_at') if isinstance(targeted_override, dict) else None,
        'runtimeTargetedStackOverrideTtlSeconds': targeted_override.get('ttl_seconds') if isinstance(targeted_override, dict) else None,
        'runtimeTargetedStackOverrideExpiresAt': targeted_override.get('expires_at') if isinstance(targeted_override, dict) else None,
        'runtimeTargetedStackOverrideSlices': targeted_override.get('slices') if isinstance(targeted_override, dict) else [],
        'runtimeTargetedStackOverrideTelegramChatAllowlist': targeted_override.get('telegram_chat_allowlist') if isinstance(targeted_override, dict) else [],
        'runtimeTargetedStackOverrideConversationAllowlist': targeted_override.get('conversation_allowlist') if isinstance(targeted_override, dict) else [],
        'strictFrameworkIsolationEnabled': settings.strict_framework_isolation_enabled,
    }


def _probe_remote_status_payload(
    *,
    name: str,
    url: str | None,
    token: str,
    ttl_seconds: int,
    timeout_seconds: float = 3.0,
) -> dict[str, Any] | None:
    normalized_url = str(url or '').strip()
    if not normalized_url:
        return None
    cache_key = f'{name}:{normalized_url}'
    now = monotonic()
    cached = _REMOTE_STATUS_CACHE.get(cache_key) or {}
    cached_timestamp = float(cached.get('timestamp', 0.0) or 0.0)
    if cached and now - cached_timestamp < max(1, ttl_seconds):
        payload = cached.get('payload')
        return dict(payload) if isinstance(payload, dict) else None

    payload: dict[str, Any] | None = None
    request = Request(
        f'{normalized_url.rstrip("/")}/v1/status',
        headers={'X-Internal-Api-Token': token},
    )
    try:
        with urlopen(request, timeout=timeout_seconds) as response:
            if response.status == 200:
                loaded = json.load(response)
                if isinstance(loaded, dict):
                    payload = loaded
    except URLError:
        payload = None
    except Exception:
        logger.exception('remote_status_probe_failed', extra={'target': name, 'url': normalized_url})
        payload = None

    _REMOTE_STATUS_CACHE[cache_key] = {
        'timestamp': now,
        'payload': payload,
    }
    return dict(payload) if isinstance(payload, dict) else None


def _pilot_diagnostics(settings: Settings) -> dict[str, dict[str, Any]]:
    ttl_seconds = max(1, int(settings.orchestrator_experiment_health_ttl_seconds or 15))
    crewai_status = _probe_remote_status_payload(
        name='crewai',
        url=settings.crewai_pilot_url,
        token=settings.internal_api_token,
        ttl_seconds=ttl_seconds,
        timeout_seconds=3.0,
    )
    specialist_status = _probe_remote_status_payload(
        name='specialist_supervisor',
        url=settings.specialist_supervisor_pilot_url,
        token=settings.internal_api_token,
        ttl_seconds=ttl_seconds,
        timeout_seconds=4.0,
    )
    return {
        'crewai': {
            'configured': bool(str(settings.crewai_pilot_url or '').strip()),
            'ready': bool(isinstance(crewai_status, dict) and crewai_status.get('ready')),
            'status': crewai_status,
        },
        'specialist_supervisor': {
            'configured': bool(str(settings.specialist_supervisor_pilot_url or '').strip()),
            'ready': bool(isinstance(specialist_status, dict) and specialist_status.get('ready')),
            'status': specialist_status,
        },
    }


def _orchestrator_runtime_diagnostics(settings: Settings) -> dict[str, Any]:
    resolved_stack = str(resolve_primary_stack(settings) or 'langgraph')
    pilot_diagnostics = _pilot_diagnostics(settings)
    extra_findings: list[dict[str, str]] = []

    if settings.graph_rag_enabled and not graph_rag_workspace_ready(settings.graph_rag_workspace):
        extra_findings.append(
            {
                'level': 'warning',
                'code': 'graph_rag_workspace_unready',
                'message': 'GraphRAG esta habilitado, mas o workspace nao esta pronto.',
            }
        )

    if resolved_stack == 'crewai':
        crewai = pilot_diagnostics['crewai']
        if not crewai['configured']:
            extra_findings.append(
                {
                    'level': 'blocker',
                    'code': 'crewai_primary_without_pilot',
                    'message': 'CrewAI esta resolvido como stack primario, mas o pilot URL nao esta configurado.',
                }
            )
        elif not crewai['ready']:
            extra_findings.append(
                {
                    'level': 'blocker',
                    'code': 'crewai_primary_pilot_unready',
                    'message': 'CrewAI esta resolvido como stack primario, mas o piloto remoto nao esta pronto.',
                }
            )

    if resolved_stack == 'specialist_supervisor':
        specialist = pilot_diagnostics['specialist_supervisor']
        if not specialist['configured']:
            extra_findings.append(
                {
                    'level': 'blocker',
                    'code': 'specialist_primary_without_pilot',
                    'message': 'Specialist Supervisor esta resolvido como stack primario, mas o pilot URL nao esta configurado.',
                }
            )
        elif not specialist['ready']:
            extra_findings.append(
                {
                    'level': 'blocker',
                    'code': 'specialist_primary_pilot_unready',
                    'message': 'Specialist Supervisor esta resolvido como stack primario, mas o piloto remoto nao esta pronto.',
                }
            )

    diagnostics = build_runtime_diagnostics(
        service_name='ai-orchestrator',
        env_file_candidates=('/workspace/.env', str(ROOT_ENV_FILE), '.env'),
        service_checks=[
            {'name': 'api_core', 'endpoint': settings.api_core_url, 'required': True},
            {'name': 'qdrant', 'endpoint': settings.qdrant_url, 'required': True},
            {
                'name': 'langgraph_checkpointer',
                'endpoint': settings.langgraph_checkpointer_url,
                'required': False,
                'allow_localhost_in_container': False,
                'allow_service_dns_in_source': False,
            },
            {'name': 'crewai_pilot', 'endpoint': settings.crewai_pilot_url, 'required': False},
            {'name': 'specialist_supervisor_pilot', 'endpoint': settings.specialist_supervisor_pilot_url, 'required': False},
            {
                'name': 'graph_rag_local_chat',
                'endpoint': settings.graph_rag_local_chat_api_base if settings.graph_rag_enabled else None,
                'required': False,
                'allow_localhost_in_container': False,
            },
            {
                'name': 'graph_rag_local_embeddings',
                'endpoint': settings.graph_rag_local_embedding_api_base if settings.graph_rag_enabled else None,
                'required': False,
                'allow_localhost_in_container': False,
            },
        ],
        secret_checks=[
            {
                'name': 'internal_api_token',
                'value': settings.internal_api_token,
                'required': True,
                'placeholder_values': ('dev-internal-token',),
            },
            {
                'name': 'openai_api_key',
                'value': settings.openai_api_key,
                'required': False,
            },
            {
                'name': 'google_api_key',
                'value': settings.google_api_key,
                'required': False,
            },
        ],
        extra_findings=extra_findings,
    )
    diagnostics['pilotReadiness'] = pilot_diagnostics
    diagnostics['resolvedPrimaryStack'] = resolved_stack
    return diagnostics


def _public_runtime_diagnostics_summary(diagnostics: dict[str, Any]) -> dict[str, Any]:
    pilot_readiness = diagnostics.get('pilotReadiness') if isinstance(diagnostics.get('pilotReadiness'), dict) else {}
    summarized_pilots: dict[str, Any] = {}
    for key, value in pilot_readiness.items():
        if not isinstance(value, dict):
            continue
        summarized_pilots[str(key)] = {
            'configured': bool(value.get('configured')),
            'ready': bool(value.get('ready')),
        }
    return {
        'operationalReadiness': bool(diagnostics.get('operationalReadiness')),
        'sourceContainerDriftRisk': diagnostics.get('sourceContainerDriftRisk'),
        'warningCount': len(diagnostics.get('warnings') or []),
        'blockerCount': len(diagnostics.get('blockers') or []),
        'resolvedPrimaryStack': diagnostics.get('resolvedPrimaryStack'),
        'pilotReadiness': summarized_pilots,
    }


def _load_report_json(path: Path) -> dict[str, object] | None:
    try:
        payload = json.loads(path.read_text(encoding='utf-8'))
    except Exception:
        return None
    return payload if isinstance(payload, dict) else None


def _dedupe_debug_items(values: list[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for raw in values:
        normalized = str(raw or '').strip()
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        ordered.append(normalized)
    return ordered


def _truncate_debug_list(values: list[str], *, limit: int = 6) -> str:
    if not values:
        return 'none'
    if len(values) <= limit:
        return ', '.join(values)
    hidden = len(values) - limit
    return f"{', '.join(values[:limit])}, +{hidden} more"


def _debug_agents_for_response(*, response: MessageResponse, stack_name: str) -> list[str]:
    candidates: list[str] = []
    for node in response.graph_path:
        token = str(node or '').strip()
        lowered = token.lower()
        if any(
            keyword in lowered
            for keyword in (
                'specialist',
                'planner',
                'manager',
                'judge',
                'composer',
                'critic',
                'router',
                'supervisor',
            )
        ):
            candidates.append(token)
    if not candidates:
        candidates.append(stack_name)
    return _dedupe_debug_items(candidates)


def _debug_resources_for_response(response: MessageResponse) -> list[str]:
    resources: list[str] = []
    resources.extend(f'tool:{tool}' for tool in response.selected_tools)
    if response.evidence_pack is not None:
        for support in response.evidence_pack.supports:
            label = str(support.label or support.kind or 'support').strip()
            kind = str(support.kind or 'support').strip()
            resources.append(f'support:{kind}:{label}')
    for citation in response.citations:
        title = str(citation.document_title or '').strip()
        if title:
            resources.append(f'doc:{title}')
    return _dedupe_debug_items(resources)


def _build_debug_trace(
    *,
    request: MessageResponseRequest,
    response: MessageResponse,
    bundle: Any,
) -> dict[str, Any]:
    stack_name = str(getattr(getattr(bundle, 'primary', None), 'name', '') or 'unknown')
    bundle_mode = str(getattr(bundle, 'mode', '') or stack_name)
    raw_path_nodes = [str(item).strip() for item in (response.graph_path or []) if str(item).strip()]
    path_nodes = list(raw_path_nodes)
    if stack_name == 'langgraph':
        classify_indexes = [index for index, item in enumerate(path_nodes) if item == 'classify_request']
        if len(classify_indexes) > 1:
            path_nodes = path_nodes[classify_indexes[-1]:]
    if not path_nodes or path_nodes[0] != stack_name:
        path_nodes = [stack_name, *path_nodes]
    agents = _debug_agents_for_response(response=response, stack_name=stack_name)
    resources = _debug_resources_for_response(response)
    evidence_pack = response.evidence_pack
    retrieval: dict[str, Any] = {
        'backend': response.retrieval_backend.value,
        'strategy': evidence_pack.strategy if evidence_pack is not None else 'none',
        'source_count': evidence_pack.source_count if evidence_pack is not None else 0,
        'support_count': evidence_pack.support_count if evidence_pack is not None else 0,
        'citation_count': len(response.citations),
    }
    trace: dict[str, Any] = {
        'channel': request.channel.value,
        'stack': stack_name,
        'bundle_mode': bundle_mode,
        'path': path_nodes,
        'raw_path': raw_path_nodes,
        'agents': agents,
        'resources': resources,
        'selected_tools': list(response.selected_tools),
        'retrieval': retrieval,
        'reason': response.reason,
    }
    if isinstance(getattr(bundle, 'experiment', None), dict):
        trace['experiment'] = dict(bundle.experiment)
    return trace


def _format_telegram_debug_footer(trace: dict[str, Any]) -> str:
    path = [str(item).strip() for item in trace.get('path', []) if str(item).strip()]
    agents = [str(item).strip() for item in trace.get('agents', []) if str(item).strip()]
    resources = [str(item).strip() for item in trace.get('resources', []) if str(item).strip()]
    retrieval = trace.get('retrieval') if isinstance(trace.get('retrieval'), dict) else {}
    retrieval_parts = [
        f"backend={str(retrieval.get('backend') or 'none')}",
        f"strategy={str(retrieval.get('strategy') or 'none')}",
        f"sources={int(retrieval.get('source_count') or 0)}",
        f"supports={int(retrieval.get('support_count') or 0)}",
        f"citations={int(retrieval.get('citation_count') or 0)}",
    ]
    lines = [
        '',
        '[debug]',
        f"stack: {trace.get('stack') or 'unknown'}",
        f"bundle: {trace.get('bundle_mode') or 'unknown'}",
        f"path: {' > '.join(path) if path else 'none'}",
        f"agents: {_truncate_debug_list(agents)}",
        f"resources: {_truncate_debug_list(resources)}",
        f"retrieval: {', '.join(retrieval_parts)}",
        f"reason: {str(trace.get('reason') or 'none')}",
    ]
    return '\n'.join(lines)


def _append_telegram_debug_footer(text: str, footer: str) -> str:
    combined = f'{text}{footer}'
    max_length = 4096
    if len(combined) <= max_length:
        return combined
    overflow = len(combined) - max_length
    available_footer = max(0, len(footer) - overflow - len('\n[debug truncated]'))
    if available_footer <= 0:
        return text
    return f"{text}{footer[:available_footer]}\n[debug truncated]"


def _attach_telegram_debug_trace(
    *,
    request: MessageResponseRequest,
    response: MessageResponse,
    bundle: Any,
    settings: Settings,
) -> MessageResponse:
    if request.channel != ConversationChannel.telegram:
        return response
    if not settings.feature_flag_telegram_debug_trace_footer_enabled:
        return response
    trace = _build_debug_trace(request=request, response=response, bundle=bundle)
    footer = _format_telegram_debug_footer(trace)
    return response.model_copy(
        update={
            'message_text': _append_telegram_debug_footer(response.message_text, footer),
            'debug_trace': trace,
        }
    )


def _experimental_stack_readiness(settings: Settings) -> dict[str, dict[str, object]]:
    comparison_payload = _load_report_json(FOUR_PATH_COMPARISON_REPORT_JSON) or {}
    smoke_payload = _load_report_json(FOUR_PATH_SMOKE_REPORT_JSON) or {}
    comparison_summary = comparison_payload.get('summary') if isinstance(comparison_payload.get('summary'), dict) else {}
    comparison_by_stack = comparison_summary.get('by_stack') if isinstance(comparison_summary, dict) else {}
    smoke_by_stack = smoke_payload.get('stacks') if isinstance(smoke_payload.get('stacks'), dict) else {}

    readiness: dict[str, dict[str, object]] = {}
    for stack_name in ('python_functions', 'llamaindex'):
        available = True if stack_name == 'python_functions' else LLAMAINDEX_WORKFLOW_AVAILABLE
        broad = comparison_by_stack.get(stack_name) if isinstance(comparison_by_stack, dict) else {}
        broad = broad if isinstance(broad, dict) else {}
        smoke = smoke_by_stack.get(stack_name) if isinstance(smoke_by_stack, dict) else {}
        smoke = smoke if isinstance(smoke, dict) else {}
        comparison_report_available = bool(broad)
        smoke_report_available = bool(smoke)

        keyword_pass = int(broad.get('keyword_pass') or 0) if comparison_report_available else None
        count = int(broad.get('count') or 0) if comparison_report_available else None
        smoke_passed = int(smoke.get('passed') or 0) if smoke_report_available else None
        smoke_total = int(smoke.get('total') or 0) if smoke_report_available else None
        quality_avg = float(broad.get('quality_avg') or 0.0) if comparison_report_available else None
        ready_for_controlled_runtime = bool(
            available
            and settings.strict_framework_isolation_enabled
            and comparison_report_available
            and smoke_report_available
            and count is not None
            and keyword_pass is not None
            and count > 0
            and keyword_pass == count
            and smoke_total is not None
            and smoke_passed is not None
            and smoke_total > 0
            and smoke_passed == smoke_total
            and quality_avg is not None
            and quality_avg >= 99.0
        )
        readiness[stack_name] = {
            'available': available,
            'strict_isolation_enabled': settings.strict_framework_isolation_enabled,
            'comparison_report_available': comparison_report_available,
            'smoke_report_available': smoke_report_available,
            'broad_benchmark_keyword_pass': keyword_pass,
            'broad_benchmark_total': count,
            'broad_benchmark_quality_avg': quality_avg,
            'broad_benchmark_avg_latency_ms': float(broad.get('avg_latency_ms') or 0.0) if comparison_report_available else None,
            'smoke_passed': smoke_passed,
            'smoke_total': smoke_total,
            'smoke_avg_latency_ms': float(smoke.get('avg_latency_ms') or 0.0) if smoke_report_available else None,
            'ready_for_controlled_runtime': ready_for_controlled_runtime,
            'comparison_report_path': str(FOUR_PATH_COMPARISON_REPORT_JSON),
            'smoke_report_path': str(FOUR_PATH_SMOKE_REPORT_JSON),
        }
    return readiness


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
        service = get_retrieval_service(
            database_url=settings.database_url,
            qdrant_url=settings.qdrant_url,
            collection_name=settings.qdrant_documents_collection,
            embedding_model=settings.document_embedding_model,
            enable_query_variants=settings.retrieval_enable_query_variants,
            enable_late_interaction_rerank=settings.retrieval_enable_late_interaction_rerank,
            late_interaction_model=settings.retrieval_late_interaction_model,
            candidate_pool_size=settings.retrieval_candidate_pool_size,
        )
        service.warm_components()
        logger.info('retrieval_service_warmed')
    except Exception:
        logger.exception('retrieval_service_warmup_failed')


def _warm_langgraph_service(settings: Settings) -> None:
    try:
        warm_langgraph_runtime(settings)
        logger.info('langgraph_runtime_warmed')
    except Exception:
        logger.exception('langgraph_runtime_warmup_failed')


@app.on_event('startup')
async def warm_runtime_dependencies() -> None:
    settings = get_settings()
    if settings.warm_retrieval_on_startup:
        asyncio.create_task(asyncio.to_thread(_warm_retrieval_service, settings))
    asyncio.create_task(asyncio.to_thread(_warm_langgraph_service, settings))


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
    runtime_diagnostics = _orchestrator_runtime_diagnostics(settings)
    return {
        'service': 'ai-orchestrator',
        'environment': settings.app_env,
        **_runtime_primary_stack_payload(settings),
        'crewaiPilotConfigured': bool(settings.crewai_pilot_url),
        'specialistSupervisorPilotConfigured': bool(settings.specialist_supervisor_pilot_url),
        'experimentEnabled': settings.orchestrator_experiment_enabled,
        'experimentPrimaryEngine': settings.orchestrator_experiment_primary_engine,
        'experimentSlices': settings.orchestrator_experiment_slices,
        'experimentRolloutPercent': settings.orchestrator_experiment_rollout_percent,
        'experimentSliceRollouts': settings.orchestrator_experiment_slice_rollouts,
        'experimentAllowlistSlices': settings.orchestrator_experiment_allowlist_slices,
        'experimentTelegramChatAllowlistCount': _csv_count(settings.orchestrator_experiment_telegram_chat_allowlist),
        'experimentConversationAllowlistCount': _csv_count(settings.orchestrator_experiment_conversation_allowlist),
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
        'strictFrameworkIsolationEnabled': settings.strict_framework_isolation_enabled,
        'retrievalQueryVariantsEnabled': settings.retrieval_enable_query_variants,
        'retrievalLateInteractionRerankEnabled': settings.retrieval_enable_late_interaction_rerank,
        'retrievalLateInteractionModel': settings.retrieval_late_interaction_model,
        'langgraphCheckpointerEnabled': langgraph_runtime['checkpointerConfigured'],
        'langgraphCheckpointerReady': langgraph_runtime['checkpointerInitialized'],
        'langgraphCheckpointerBackend': langgraph_runtime['checkpointerBackend'],
        'langgraphThreadIdEnabled': langgraph_runtime['threadIdEnabled'],
        'langgraphHitlEnabled': settings.langgraph_hitl_enabled,
        'langgraphHitlDefaultSlices': settings.langgraph_hitl_default_slices,
        'langgraphHitlUserTrafficEnabled': settings.langgraph_hitl_user_traffic_enabled,
        'langgraphHitlUserTrafficSlices': settings.langgraph_hitl_user_traffic_slices,
        'pythonFunctionsAvailable': True,
        'llamaindexWorkflowAvailable': LLAMAINDEX_WORKFLOW_AVAILABLE,
        'runtimeDiagnostics': runtime_diagnostics,
    }


@app.get('/v1/status')
async def status() -> dict[str, object]:
    settings = get_settings()
    langgraph_runtime = get_langgraph_runtime_status(settings)
    scorecard_gate = get_scorecard_gate_status(settings=settings)
    rollout_readiness = get_experiment_rollout_readiness(settings=settings)
    live_promotion_summary = get_experiment_live_promotion_summary(settings=settings)
    experimental_stack_readiness = _experimental_stack_readiness(settings)
    runtime_diagnostics = _orchestrator_runtime_diagnostics(settings)
    return {
        'service': 'ai-orchestrator',
        'ready': True,
        **_runtime_primary_stack_payload(settings),
        'crewaiPilotConfigured': bool(settings.crewai_pilot_url),
        'specialistSupervisorPilotConfigured': bool(settings.specialist_supervisor_pilot_url),
        'experimentEnabled': settings.orchestrator_experiment_enabled,
        'experimentPrimaryEngine': settings.orchestrator_experiment_primary_engine,
        'experimentSlices': settings.orchestrator_experiment_slices,
        'experimentRolloutPercent': settings.orchestrator_experiment_rollout_percent,
        'experimentSliceRollouts': settings.orchestrator_experiment_slice_rollouts,
        'experimentAllowlistSlices': settings.orchestrator_experiment_allowlist_slices,
        'experimentTelegramChatAllowlistCount': _csv_count(settings.orchestrator_experiment_telegram_chat_allowlist),
        'experimentConversationAllowlistCount': _csv_count(settings.orchestrator_experiment_conversation_allowlist),
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
            'agent-kernel',
            'shared-entity-resolution',
            'tool-routing',
            'qdrant-hybrid-retrieval',
            'query-planned-retrieval',
            'late-interaction-reranking',
            'conversation-memory',
            'graph-rag-routing',
            'provider-abstraction',
            'python-functions-engine',
            'llamaindex-workflow-engine',
            'specialist-supervisor-engine',
        ],
        'supportedEngines': sorted(SUPPORTED_PRIMARY_STACKS),
        'telegramDebugTraceFooterEnabled': settings.feature_flag_telegram_debug_trace_footer_enabled,
        'graphRagEnabled': settings.graph_rag_enabled,
        'graphRagWorkspaceReady': graph_rag_workspace_ready(settings.graph_rag_workspace),
        'strictFrameworkIsolationEnabled': settings.strict_framework_isolation_enabled,
        'retrievalQueryVariantsEnabled': settings.retrieval_enable_query_variants,
        'retrievalLateInteractionRerankEnabled': settings.retrieval_enable_late_interaction_rerank,
        'retrievalLateInteractionModel': settings.retrieval_late_interaction_model,
        'langgraphCheckpointerEnabled': langgraph_runtime['checkpointerConfigured'],
        'langgraphCheckpointerReady': langgraph_runtime['checkpointerInitialized'],
        'langgraphCheckpointerBackend': langgraph_runtime['checkpointerBackend'],
        'langgraphThreadIdEnabled': langgraph_runtime['threadIdEnabled'],
        'langgraphHitlEnabled': settings.langgraph_hitl_enabled,
        'langgraphHitlDefaultSlices': settings.langgraph_hitl_default_slices,
        'langgraphHitlUserTrafficEnabled': settings.langgraph_hitl_user_traffic_enabled,
        'langgraphHitlUserTrafficSlices': settings.langgraph_hitl_user_traffic_slices,
        'pythonFunctionsAvailable': True,
        'llamaindexWorkflowAvailable': LLAMAINDEX_WORKFLOW_AVAILABLE,
        'experimentalStackReadiness': experimental_stack_readiness,
        'runtimeDiagnosticsSummary': _public_runtime_diagnostics_summary(runtime_diagnostics),
    }


@app.get('/v1/internal/runtime/primary-stack')
async def get_runtime_primary_stack(
    x_internal_api_token: str | None = Header(default=None, alias='X-Internal-Api-Token'),
) -> dict[str, object]:
    _require_internal_api_token(x_internal_api_token)
    settings = get_settings()
    return {
        'service': 'ai-orchestrator',
        **_runtime_primary_stack_payload(settings),
        'supportedPrimaryStacks': sorted(SUPPORTED_PRIMARY_STACKS),
    }


@app.post('/v1/internal/runtime/primary-stack')
async def update_runtime_primary_stack(
    request: RuntimePrimaryStackUpdateRequest,
    x_internal_api_token: str | None = Header(default=None, alias='X-Internal-Api-Token'),
) -> dict[str, object]:
    _require_internal_api_token(x_internal_api_token)
    settings = get_settings()
    operator = str(request.operator or 'internal').strip() or 'internal'
    reason = str(request.reason or '').strip() or None
    if request.clear_override:
        override = clear_runtime_primary_stack_override(
            reason=reason or 'runtime_primary_stack_override_cleared',
            operator=operator,
        )
        logger.info(
            'runtime_primary_stack_override_cleared',
            extra={
                'operator': operator,
                'reason': reason,
            },
        )
        action = 'cleared'
    else:
        try:
            override = set_runtime_primary_stack_override(
                stack=request.stack,
                reason=reason or 'runtime_primary_stack_override_set',
                operator=operator,
            )
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        logger.info(
            'runtime_primary_stack_override_updated',
            extra={
                'operator': operator,
                'reason': reason,
                'stack': override.get('value'),
            },
        )
        action = 'updated'
    return {
        'service': 'ai-orchestrator',
        'action': action,
        'override': override,
        **_runtime_primary_stack_payload(settings),
        'supportedPrimaryStacks': sorted(SUPPORTED_PRIMARY_STACKS),
    }


@app.get('/v1/internal/runtime/targeted-stack')
async def get_runtime_targeted_stack(
    x_internal_api_token: str | None = Header(default=None, alias='X-Internal-Api-Token'),
) -> dict[str, object]:
    _require_internal_api_token(x_internal_api_token)
    settings = get_settings()
    return {
        'service': 'ai-orchestrator',
        'targetedOverride': get_runtime_targeted_stack_override(),
        **_runtime_primary_stack_payload(settings),
        'supportedPrimaryStacks': sorted(SUPPORTED_PRIMARY_STACKS),
    }


@app.post('/v1/internal/runtime/targeted-stack')
async def update_runtime_targeted_stack(
    request: RuntimeTargetedStackUpdateRequest,
    x_internal_api_token: str | None = Header(default=None, alias='X-Internal-Api-Token'),
) -> dict[str, object]:
    _require_internal_api_token(x_internal_api_token)
    settings = get_settings()
    operator = str(request.operator or 'internal').strip() or 'internal'
    reason = str(request.reason or '').strip() or None
    if request.clear_override:
        override = clear_runtime_targeted_stack_override(
            reason=reason or 'runtime_targeted_stack_override_cleared',
            operator=operator,
        )
        logger.info(
            'runtime_targeted_stack_override_cleared',
            extra={'operator': operator, 'reason': reason},
        )
        action = 'cleared'
    else:
        try:
            override = set_runtime_targeted_stack_override(
                stack=request.stack,
                reason=reason or 'runtime_targeted_stack_override_set',
                operator=operator,
                ttl_seconds=request.ttl_seconds,
                slices=request.slices,
                telegram_chat_allowlist=request.telegram_chat_allowlist,
                conversation_allowlist=request.conversation_allowlist,
            )
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        logger.info(
            'runtime_targeted_stack_override_updated',
            extra={
                'operator': operator,
                'reason': reason,
                'stack': override.get('value'),
                'ttl_seconds': override.get('ttl_seconds'),
                'expires_at': override.get('expires_at'),
                'slices': override.get('slices'),
                'telegram_chat_allowlist': override.get('telegram_chat_allowlist'),
                'conversation_allowlist': override.get('conversation_allowlist'),
            },
        )
        action = 'updated'
    return {
        'service': 'ai-orchestrator',
        'action': action,
        'targetedOverride': override,
        **_runtime_primary_stack_payload(settings),
        'supportedPrimaryStacks': sorted(SUPPORTED_PRIMARY_STACKS),
    }


@app.get('/v1/capabilities', response_model=RuntimeCapabilities)
async def capabilities() -> RuntimeCapabilities:
    settings = get_settings()
    experimental_stack_readiness = _experimental_stack_readiness(settings)
    return RuntimeCapabilities(
        service='ai-orchestrator',
        llm_provider=settings.llm_provider,
        openai_model=settings.openai_model,
        google_model=settings.google_model,
        llm_configured=bool(settings.openai_api_key) or bool(settings.google_api_key),
        graph_rag_enabled=settings.graph_rag_enabled,
        graph_rag_workspace_ready=graph_rag_workspace_ready(settings.graph_rag_workspace),
        strict_framework_isolation_enabled=settings.strict_framework_isolation_enabled,
        supported_primary_stacks=sorted(SUPPORTED_PRIMARY_STACKS),
        python_functions_available=True,
        llamaindex_workflow_available=LLAMAINDEX_WORKFLOW_AVAILABLE,
        specialist_supervisor_available=bool(settings.specialist_supervisor_pilot_url),
        telegram_debug_trace_footer_enabled=settings.feature_flag_telegram_debug_trace_footer_enabled,
        experimental_stack_readiness=experimental_stack_readiness,
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
        enable_query_variants=settings.retrieval_enable_query_variants,
        enable_late_interaction_rerank=settings.retrieval_enable_late_interaction_rerank,
        late_interaction_model=settings.retrieval_late_interaction_model,
        candidate_pool_size=settings.retrieval_candidate_pool_size,
    )
    return {
        'service': 'ai-orchestrator',
        'retrievalBackend': RetrievalBackend.qdrant_hybrid.value,
        'queryVariantsEnabled': settings.retrieval_enable_query_variants,
        'lateInteractionRerankEnabled': settings.retrieval_enable_late_interaction_rerank,
        'lateInteractionModel': settings.retrieval_late_interaction_model,
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
        enable_query_variants=settings.retrieval_enable_query_variants,
        enable_late_interaction_rerank=settings.retrieval_enable_late_interaction_rerank,
        late_interaction_model=settings.retrieval_late_interaction_model,
        candidate_pool_size=settings.retrieval_candidate_pool_size,
    )
    return service.hybrid_search(
        query=request.query,
        top_k=request.top_k,
        visibility=request.visibility,
        category=request.category,
    )


@app.post('/v1/internal/graphrag/query')
async def graph_rag_query(
    request: GraphRagQueryRequest,
    x_internal_api_token: str | None = Header(default=None, alias='X-Internal-Api-Token'),
) -> dict[str, object]:
    _require_internal_api_token(x_internal_api_token)
    settings = get_settings()
    result = await run_graph_rag_query(settings=settings, query=request.query)
    if result is None:
        return {
            'service': 'ai-orchestrator',
            'graphRagEnabled': settings.graph_rag_enabled,
            'workspaceReady': graph_rag_workspace_ready(settings.graph_rag_workspace),
            'result': None,
        }
    return {
        'service': 'ai-orchestrator',
        'graphRagEnabled': settings.graph_rag_enabled,
        'workspaceReady': graph_rag_workspace_ready(settings.graph_rag_workspace),
        'result': result,
    }


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
    return _attach_telegram_debug_trace(
        request=request,
        response=response,
        bundle=bundle,
        settings=settings,
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
