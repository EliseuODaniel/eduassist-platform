from __future__ import annotations

import asyncio
import logging
from time import monotonic
from typing import Any

import httpx

from .models import (
    JudgeVerdict,
    ManagerDraft,
    OperationalMemory,
    RepairDraft,
    RetrievalPlannerAdvice,
    SupervisorAnswerPayload,
    SupervisorPlan,
)

logger = logging.getLogger(__name__)
_PUBLIC_RESOURCE_CACHE: dict[str, dict[str, Any]] = {}


def _conversation_external_id(ctx: Any) -> str:
    request = ctx.request
    if getattr(request, "conversation_id", None):
        return str(request.conversation_id)
    if getattr(request, "channel", None) == "telegram" and getattr(request, "telegram_chat_id", None) is not None:
        return f"telegram:{request.telegram_chat_id}"
    return f"{request.channel}:anonymous"


def _strip_none(payload: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in payload.items() if value is not None}


async def _http_get(
    client: httpx.AsyncClient,
    *,
    base_url: str,
    path: str,
    token: str,
    params: dict[str, Any] | None = None,
) -> dict[str, Any] | None:
    response = await client.get(
        f"{base_url.rstrip('/')}{path}",
        params=params,
        headers={"X-Internal-Api-Token": token},
    )
    response.raise_for_status()
    payload = response.json()
    return payload if isinstance(payload, dict) else None


async def _http_post(
    client: httpx.AsyncClient,
    *,
    base_url: str,
    path: str,
    token: str,
    payload: dict[str, Any],
) -> dict[str, Any] | None:
    response = await client.post(
        f"{base_url.rstrip('/')}{path}",
        headers={
            "X-Internal-Api-Token": token,
            "Content-Type": "application/json",
        },
        json=payload,
    )
    response.raise_for_status()
    body = response.json()
    return body if isinstance(body, dict) else None


async def fetch_actor_context(ctx: Any) -> dict[str, Any] | None:
    if ctx.request.telegram_chat_id is None:
        return None
    try:
        payload = await _http_get(
            ctx.http_client,
            base_url=ctx.settings.api_core_url,
            path="/v1/internal/identity/context",
            token=ctx.settings.internal_api_token,
            params={"telegram_chat_id": ctx.request.telegram_chat_id},
        )
    except httpx.HTTPError as exc:
        logger.warning("specialist_supervisor_actor_context_unavailable", extra={"error": str(exc)})
        return None
    actor = payload.get("actor") if isinstance(payload, dict) else None
    return actor if isinstance(actor, dict) else None


async def fetch_conversation_context(ctx: Any) -> dict[str, Any] | None:
    try:
        payload = await _http_get(
            ctx.http_client,
            base_url=ctx.settings.api_core_url,
            path="/v1/internal/conversations/context",
            token=ctx.settings.internal_api_token,
            params={
                "conversation_external_id": _conversation_external_id(ctx),
                "channel": ctx.request.channel.value,
                "limit": 8,
            },
        )
    except httpx.HTTPError as exc:
        logger.warning("specialist_supervisor_conversation_context_unavailable", extra={"error": str(exc)})
        return None
    return payload if isinstance(payload, dict) else None


async def fetch_public_school_profile(ctx: Any) -> dict[str, Any] | None:
    payload = await _http_get(
        ctx.http_client,
        base_url=ctx.settings.api_core_url,
        path="/v1/public/school-profile",
        token=ctx.settings.internal_api_token,
    )
    profile = payload.get("profile") if isinstance(payload, dict) else None
    return profile if isinstance(profile, dict) else None


async def fetch_public_payload(ctx: Any, path: str, key: str) -> Any:
    cache_key = f"{path}:{key}"
    cached = _PUBLIC_RESOURCE_CACHE.get(cache_key)
    if isinstance(cached, dict):
        expires_at = float(cached.get("expires_at", 0.0) or 0.0)
        if expires_at > monotonic():
            value = cached.get("value")
            if isinstance(value, dict):
                return dict(value)
            if isinstance(value, list):
                return [dict(item) if isinstance(item, dict) else item for item in value]
            return value
        _PUBLIC_RESOURCE_CACHE.pop(cache_key, None)
    payload = await _http_get(
        ctx.http_client,
        base_url=ctx.settings.api_core_url,
        path=path,
        token=ctx.settings.internal_api_token,
    )
    if not isinstance(payload, dict):
        return None
    value = payload.get(key)
    _PUBLIC_RESOURCE_CACHE[cache_key] = {
        "value": value,
        "expires_at": monotonic() + float(getattr(ctx.settings, "public_resource_cache_ttl_seconds", 120.0) or 120.0),
    }
    if isinstance(value, dict):
        return dict(value)
    if isinstance(value, list):
        return [dict(item) if isinstance(item, dict) else item for item in value]
    return value


async def orchestrator_preview(ctx: Any) -> dict[str, Any] | None:
    try:
        response = await ctx.http_client.post(
            f"{ctx.settings.orchestrator_url.rstrip('/')}/v1/orchestrate/preview",
            timeout=httpx.Timeout(1.5, connect=0.5),
            json={
                "message": ctx.request.message,
                "conversation_id": _conversation_external_id(ctx),
                "user": ctx.request.user.model_dump(mode="json"),
                "allow_graph_rag": ctx.request.allow_graph_rag,
                "allow_handoff": ctx.request.allow_handoff,
            },
        )
        response.raise_for_status()
    except httpx.HTTPError as exc:
        logger.warning("specialist_orchestrator_preview_unavailable: %s", exc)
        return None
    payload = response.json()
    if not isinstance(payload, dict):
        return None
    preview = payload.get("preview")
    return preview if isinstance(preview, dict) else None


async def orchestrator_retrieval_search(
    ctx: Any,
    *,
    query: str,
    visibility: str = "public",
    category: str | None = None,
    top_k: int = 4,
) -> dict[str, Any] | None:
    try:
        response = await ctx.http_client.post(
            f"{ctx.settings.orchestrator_url.rstrip('/')}/v1/retrieval/search",
            timeout=httpx.Timeout(4.0, connect=1.0),
            headers={
                "X-Internal-Api-Token": ctx.settings.internal_api_token,
                "Content-Type": "application/json",
            },
            json=_strip_none(
                {
                    "query": query,
                    "top_k": top_k,
                    "visibility": visibility,
                    "category": category,
                }
            ),
        )
        response.raise_for_status()
        body = response.json()
        return body if isinstance(body, dict) else None
    except httpx.HTTPError as exc:
        logger.warning("specialist_orchestrator_retrieval_unavailable: %s", exc)
        return None


async def orchestrator_graph_rag_query(ctx: Any, *, query: str) -> dict[str, Any] | None:
    try:
        response = await ctx.http_client.post(
            f"{ctx.settings.orchestrator_url.rstrip('/')}/v1/internal/graphrag/query",
            timeout=httpx.Timeout(8.0, connect=1.0),
            headers={
                "X-Internal-Api-Token": ctx.settings.internal_api_token,
                "Content-Type": "application/json",
            },
            json={"query": query},
        )
        response.raise_for_status()
        body = response.json()
        return body if isinstance(body, dict) else None
    except httpx.HTTPError as exc:
        logger.warning("specialist_orchestrator_graphrag_unavailable: %s", exc)
        return None


async def persist_conversation_turn(ctx: Any, assistant_message: str) -> None:
    actor_user_id = ctx.actor.get("user_id") if isinstance(ctx.actor, dict) else None
    try:
        await _http_post(
            ctx.http_client,
            base_url=ctx.settings.api_core_url,
            path="/v1/internal/conversations/messages",
            token=ctx.settings.internal_api_token,
            payload={
                "channel": ctx.request.channel.value,
                "conversation_external_id": _conversation_external_id(ctx),
                "actor_user_id": actor_user_id,
                "messages": [
                    {"sender_type": "user", "content": ctx.request.message},
                    {"sender_type": "assistant", "content": assistant_message},
                ],
            },
        )
    except httpx.HTTPError as exc:
        logger.warning("specialist_supervisor_persist_turn_failed", extra={"error": str(exc)})


async def persist_trace(
    ctx: Any,
    *,
    retrieval_advice: RetrievalPlannerAdvice | None,
    plan: SupervisorPlan,
    draft: ManagerDraft,
    judge: JudgeVerdict,
    answer: SupervisorAnswerPayload,
    operational_memory: OperationalMemory,
    repair_payload: tuple[RepairDraft, JudgeVerdict] | None = None,
) -> None:
    actor_user_id = ctx.actor.get("user_id") if isinstance(ctx.actor, dict) else None
    try:
        await _http_post(
            ctx.http_client,
            base_url=ctx.settings.api_core_url,
            path="/v1/internal/conversations/tool-calls",
            token=ctx.settings.internal_api_token,
            payload={
                "channel": ctx.request.channel.value,
                "conversation_external_id": _conversation_external_id(ctx),
                "actor_user_id": actor_user_id,
                "tool_calls": [
                    {
                        "tool_name": "specialist_supervisor.trace",
                        "status": "ok",
                        "request_payload": {
                            "message": ctx.request.message,
                            "preview_hint": ctx.preview_hint or {},
                        },
                        "response_payload": {
                            "retrieval_advice": retrieval_advice.model_dump(mode="json") if retrieval_advice is not None else None,
                            "resolved_turn": ctx.resolved_turn.model_dump(mode="json") if ctx.resolved_turn is not None else None,
                            "plan": plan.model_dump(mode="json"),
                            "draft": draft.model_dump(mode="json"),
                            "judge": judge.model_dump(mode="json"),
                            "repair": repair_payload[0].model_dump(mode="json") if repair_payload is not None else None,
                            "repair_judge": repair_payload[1].model_dump(mode="json") if repair_payload is not None else None,
                            "answer": answer.model_dump(mode="json"),
                            "operational_memory": operational_memory.model_dump(mode="json"),
                            "agent_events": ctx.trace.agent_events,
                            "tool_events": ctx.trace.tool_events,
                        },
                    }
                ],
            },
        )
    except httpx.HTTPError as exc:
        logger.warning("specialist_supervisor_persist_trace_failed", extra={"error": str(exc)})


async def persist_light_trace(
    ctx: Any,
    *,
    answer: SupervisorAnswerPayload,
    route: str,
    metadata: dict[str, Any] | None = None,
    operational_memory: OperationalMemory,
) -> None:
    actor_user_id = ctx.actor.get("user_id") if isinstance(ctx.actor, dict) else None
    try:
        await _http_post(
            ctx.http_client,
            base_url=ctx.settings.api_core_url,
            path="/v1/internal/conversations/tool-calls",
            token=ctx.settings.internal_api_token,
            payload={
                "channel": ctx.request.channel.value,
                "conversation_external_id": _conversation_external_id(ctx),
                "actor_user_id": actor_user_id,
                "tool_calls": [
                    {
                        "tool_name": "specialist_supervisor.trace",
                        "status": "ok",
                        "request_payload": {
                            "message": ctx.request.message,
                            "preview_hint": ctx.preview_hint or {},
                            "route": route,
                        },
                        "response_payload": {
                            "route": route,
                            "metadata": metadata or {},
                            "resolved_turn": ctx.resolved_turn.model_dump(mode="json") if ctx.resolved_turn is not None else None,
                            "operational_memory": operational_memory.model_dump(mode="json"),
                            "answer": answer.model_dump(mode="json"),
                            "agent_events": ctx.trace.agent_events,
                            "tool_events": ctx.trace.tool_events,
                        },
                    }
                ],
            },
        )
    except httpx.HTTPError as exc:
        logger.warning("specialist_supervisor_persist_light_trace_failed", extra={"error": str(exc)})


async def persist_final_answer(
    ctx: Any,
    *,
    answer: SupervisorAnswerPayload,
    route: str,
    operational_memory: OperationalMemory,
    metadata: dict[str, Any] | None = None,
    trace_payload: tuple[SupervisorPlan, ManagerDraft, JudgeVerdict] | None = None,
    repair_payload: tuple[RepairDraft, JudgeVerdict] | None = None,
    timeout_seconds: float | None = None,
) -> None:
    ctx.operational_memory = operational_memory

    async def _persist() -> None:
        await persist_conversation_turn(ctx, answer.message_text)
        if trace_payload is not None:
            plan, draft, judge = trace_payload
            await persist_trace(
                ctx,
                retrieval_advice=ctx.retrieval_advice,
                plan=plan,
                draft=draft,
                judge=judge,
                answer=answer,
                operational_memory=operational_memory,
                repair_payload=repair_payload,
            )
            return
        await persist_light_trace(
            ctx,
            answer=answer,
            route=route,
            metadata=metadata,
            operational_memory=operational_memory,
        )

    if timeout_seconds is None:
        await _persist()
        return

    try:
        await asyncio.wait_for(_persist(), timeout=timeout_seconds)
    except TimeoutError:
        logger.warning(
            "specialist_supervisor_persist_final_timeout",
            extra={"route": route, "timeout_seconds": timeout_seconds},
        )
