from __future__ import annotations

import logging
import secrets
from typing import Any

from eduassist_observability import (
    bridge_spiffe_identity_to_internal_token,
    build_runtime_diagnostics,
    configure_observability,
)
from fastapi import FastAPI, Header, HTTPException, Request

from .channel_reply_formatting import format_reply_for_channel
from .debug_trace_footer import attach_telegram_debug_trace_for_stack
from .graph_rag_runtime import graph_rag_workspace_ready
from .models import ConversationChannel, MessageResponse, MessageResponseRequest, OrchestrationMode
from .service_settings import Settings, get_settings
from .stack_postprocessing import postprocess_stack_response
from .stack_runtime_profiles import build_stack_local_settings, stack_runtime_overrides

logger = logging.getLogger(__name__)


def _require_internal_api_token(x_internal_api_token: str | None) -> None:
    settings = get_settings()
    if not x_internal_api_token or not secrets.compare_digest(x_internal_api_token, settings.internal_api_token):
        raise HTTPException(status_code=401, detail='invalid_internal_api_token')


def _stack_capabilities(stack_name: str) -> list[str]:
    if stack_name == 'langgraph':
        return [
            'langgraph-state-machine',
            'langgraph-thread-memory',
            'langgraph-hitl',
            'stack-local-postprocess',
        ]
    if stack_name == 'python_functions':
        return [
            'deterministic-routing',
            'typed-tools',
            'stack-local-postprocess',
        ]
    if stack_name == 'llamaindex':
        return [
            'llamaindex-workflow',
            'document-retrieval',
            'response-synthesis',
            'stack-local-postprocess',
        ]
    return ['stack-local-postprocess']


def _engine_for_stack(stack_name: str) -> Any:
    if stack_name == 'langgraph':
        from .engines.langgraph_engine import LangGraphEngine

        return LangGraphEngine()
    if stack_name == 'python_functions':
        from .engines.python_functions_engine import PythonFunctionsEngine

        return PythonFunctionsEngine()
    if stack_name == 'llamaindex':
        from .engines.llamaindex_workflow_engine import LlamaIndexWorkflowEngine

        return LlamaIndexWorkflowEngine()
    raise ValueError(f'unsupported_stack:{stack_name}')


def _llamaindex_workflow_available_for(stack_name: str) -> bool:
    if stack_name != 'llamaindex':
        return False
    from .engines.llamaindex_workflow_engine import LLAMAINDEX_WORKFLOW_AVAILABLE

    return bool(LLAMAINDEX_WORKFLOW_AVAILABLE)


def _dedicated_runtime_diagnostics(*, stack_name: str, settings: Settings) -> dict[str, object]:
    extra_findings: list[dict[str, str]] = []
    if settings.graph_rag_enabled and not graph_rag_workspace_ready(settings.graph_rag_workspace):
        extra_findings.append(
            {
                "level": "warning",
                "code": "graph_rag_workspace_unready",
                "message": "GraphRAG esta habilitado, mas o workspace nao esta pronto.",
            }
        )
    diagnostics = build_runtime_diagnostics(
        service_name=f"ai-orchestrator-{stack_name}",
        env_file_candidates=("/workspace/.env", ".env"),
        service_checks=[
            {"name": "api_core", "endpoint": settings.api_core_url, "required": True},
            {"name": "qdrant", "endpoint": settings.qdrant_url, "required": True},
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
    diagnostics["stack"] = stack_name
    return diagnostics


def create_dedicated_stack_app(*, stack_name: str, service_name: str) -> FastAPI:
    app = FastAPI(
        title=f'EduAssist {service_name}',
        version='0.1.0',
        summary=f'Dedicated {stack_name} orchestration service.',
    )

    @app.middleware('http')
    async def _bridge_internal_workload_identity(request: Request, call_next):
        settings = build_stack_local_settings(base_settings=get_settings(), stack_name=stack_name)
        decision = bridge_spiffe_identity_to_internal_token(
            request.scope,
            expected_token=settings.internal_api_token,
            mode=settings.internal_workload_identity_mode,
            allowed_spiffe_ids=settings.internal_spiffe_allowed_ids,
        )
        if decision.authenticated and decision.mechanism == 'spiffe_id':
            request.state.internal_workload_identity = {
                'mechanism': decision.mechanism,
                'spiffe_id': decision.spiffe_id,
            }
        return await call_next(request)

    configure_observability(
        service_name=service_name,
        service_version=app.version,
        environment=get_settings().app_env,
        app=app,
        excluded_urls='/healthz',
    )

    @app.get('/healthz')
    async def healthz() -> dict[str, object]:
        return {
            'status': 'ok',
            'service': service_name,
            'ready': True,
        }

    @app.get('/v1/status')
    async def status() -> dict[str, object]:
        settings = build_stack_local_settings(base_settings=get_settings(), stack_name=stack_name)
        engine = _engine_for_stack(stack_name)
        runtime_diagnostics = _dedicated_runtime_diagnostics(stack_name=stack_name, settings=settings)
        return {
            'service': service_name,
            'ready': bool(getattr(engine, 'ready', True)),
            'serviceRole': 'dedicated-stack-runtime',
            'primaryServingRecommended': True,
            'stack': stack_name,
            'mode': 'stack-local',
            'llmModelProfile': settings.llm_model_profile,
            'llmProvider': settings.llm_provider,
            'llmConfigured': bool(settings.openai_api_key) or bool(settings.google_api_key),
            'openaiApiMode': settings.openai_api_mode,
            'openaiModel': settings.openai_model,
            'googleModel': settings.google_model,
            'graphRagEnabled': settings.graph_rag_enabled,
            'graphRagWorkspaceReady': graph_rag_workspace_ready(settings.graph_rag_workspace),
            'strictFrameworkIsolationEnabled': True,
            'llamaindexWorkflowAvailable': _llamaindex_workflow_available_for(stack_name),
            'capabilities': _stack_capabilities(stack_name),
            'postprocessMode': 'stack_local_native',
            'telegramDebugTraceFooterEnabled': bool(settings.feature_flag_telegram_debug_trace_footer_enabled),
            'stackLocalOverrides': stack_runtime_overrides(stack_name),
            'runtimeDiagnostics': runtime_diagnostics,
        }

    @app.post('/v1/messages/respond', response_model=MessageResponse)
    async def message_response(
        request: MessageResponseRequest,
        x_internal_api_token: str | None = Header(default=None, alias='X-Internal-Api-Token'),
    ) -> MessageResponse:
        _require_internal_api_token(x_internal_api_token)
        settings = build_stack_local_settings(base_settings=get_settings(), stack_name=stack_name)
        engine = _engine_for_stack(stack_name)
        response = await engine.respond(request=request, settings=settings, engine_mode=stack_name)
        response = await postprocess_stack_response(
            stack_name=stack_name,
            request=request,
            response=response,
            settings=settings,
        )
        if (
            request.channel == ConversationChannel.telegram
            and response.mode == OrchestrationMode.clarify
            and not bool(getattr(response, 'answer_experience_eligible', False))
        ):
            response = await postprocess_stack_response(
                stack_name=stack_name,
                request=request,
                response=response,
                settings=settings,
            )
        response = attach_telegram_debug_trace_for_stack(
            request=request,
            response=response,
            stack_name=stack_name,
            settings=settings,
        )
        return response.model_copy(
            update={
                'message_text': format_reply_for_channel(
                    text=response.message_text,
                    channel=request.channel.value,
                )
            }
        )

    return app
