from __future__ import annotations

import asyncio
import logging
import re
from time import monotonic
from typing import Any
import unicodedata

import httpx

from .local_retrieval import get_retrieval_service, looks_like_restricted_document_query, retrieve_relevant_restricted_hits_with_fallback
from .models import RetrievalProfile
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
_ORCHESTRATOR_PREVIEW_CACHE: dict[str, dict[str, Any]] = {}
_ORCHESTRATOR_RETRIEVAL_CACHE: dict[str, dict[str, Any]] = {}
_ACTOR_CONTEXT_CACHE: dict[str, dict[str, Any]] = {}
_ACADEMIC_HINTS = ('nota', 'notas', 'media', 'média', 'boletim', 'frequencia', 'frequência', 'falta', 'faltas', 'prova', 'provas', 'avaliacao', 'avaliação')
_FINANCE_HINTS = ('fatura', 'financeiro', 'boleto', 'mensalidade', 'pagamento', 'valor')
_CALENDAR_HINTS = ('calendario', 'calendário', 'inicio das aulas', 'início das aulas', 'reuniao', 'reunião', 'data', 'datas', 'cronograma')
_SUPPORT_HINTS = ('atestado', 'secretaria', 'protocolo', 'documentacao', 'documentação', 'cancelamento', 'transferencia', 'transferência', 'rematricula', 'rematrícula')


def _restricted_retrieval_category(query: str) -> str | None:
    normalized = _normalize_text(query)
    if any(term in normalized for term in ('financeiro', 'quitacao', 'quitação', 'negociacao', 'negociação', 'pagamento', 'inadimplencia', 'inadimplência')):
        return 'finance'
    if any(term in normalized for term in ('professor', 'avaliac', 'pedagog', 'frequencia', 'frequência', 'segunda chamada', 'saude', 'saúde')):
        return 'academic'
    if any(term in normalized for term in ('telegram', 'escopo parcial', 'responsavel', 'responsável', 'autorizacao', 'autorização')):
        return 'identity'
    if any(term in normalized for term in ('transferencia', 'transferência', 'secretaria', 'rematricula', 'rematrícula', 'documento')):
        return 'secretaria'
    return None


def _effective_retrieval_request(
    *,
    query: str,
    visibility: str,
    category: str | None,
    top_k: int,
    profile: str | None,
) -> tuple[str | None, int, str | None]:
    effective_category = category
    effective_top_k = top_k
    effective_profile = profile
    if visibility == 'restricted' and looks_like_restricted_document_query(query):
        effective_category = effective_category or _restricted_retrieval_category(query)
        effective_top_k = max(effective_top_k, 8)
        effective_profile = effective_profile or 'deep'
    elif effective_profile is None and effective_top_k <= 3:
        effective_profile = 'cheap'
    return effective_category, effective_top_k, effective_profile


def _conversation_external_id(ctx: Any) -> str:
    request = ctx.request
    if getattr(request, "conversation_id", None):
        return str(request.conversation_id)
    if getattr(request, "channel", None) == "telegram" and getattr(request, "telegram_chat_id", None) is not None:
        return f"telegram:{request.telegram_chat_id}"
    return f"{request.channel}:anonymous"


def _strip_none(payload: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in payload.items() if value is not None}


def _normalize_text(value: str) -> str:
    normalized = unicodedata.normalize("NFD", value or "")
    normalized = "".join(ch for ch in normalized if unicodedata.category(ch) != "Mn")
    normalized = normalized.lower()
    normalized = re.sub(r"[^a-z0-9\s]", " ", normalized)
    return re.sub(r"\s+", " ", normalized).strip()


def _cache_get(cache: dict[str, dict[str, Any]], cache_key: str, *, allow_stale: bool = False) -> Any | None:
    entry = cache.get(cache_key)
    if not isinstance(entry, dict):
        return None
    expires_at = float(entry.get("expires_at", 0.0) or 0.0)
    if expires_at > monotonic() or allow_stale:
        value = entry.get("value")
        if isinstance(value, dict):
            return dict(value)
        if isinstance(value, list):
            return [dict(item) if isinstance(item, dict) else item for item in value]
        return value
    cache.pop(cache_key, None)
    return None


def _cache_set(cache: dict[str, dict[str, Any]], cache_key: str, value: Any, *, ttl_seconds: float) -> Any:
    cache[cache_key] = {
        "value": value,
        "expires_at": monotonic() + ttl_seconds,
    }
    return value


async def _http_get(
    client: httpx.AsyncClient,
    *,
    base_url: str,
    path: str,
    token: str,
    params: dict[str, Any] | None = None,
    timeout_seconds: float | None = None,
) -> dict[str, Any] | None:
    response = await client.get(
        f"{base_url.rstrip('/')}{path}",
        params=params,
        headers={"X-Internal-Api-Token": token},
        timeout=(
            httpx.Timeout(timeout_seconds, connect=min(1.0, max(0.3, timeout_seconds / 2.0)))
            if timeout_seconds is not None
            else None
        ),
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
    cache_key = f"actor:{ctx.request.telegram_chat_id}"
    cached_actor = _cache_get(_ACTOR_CONTEXT_CACHE, cache_key)
    if isinstance(cached_actor, dict):
        return cached_actor
    try:
        payload = await _http_get(
            ctx.http_client,
            base_url=ctx.settings.api_core_url,
            path="/v1/internal/identity/context",
            token=ctx.settings.internal_api_token,
            params={"telegram_chat_id": ctx.request.telegram_chat_id},
            timeout_seconds=float(getattr(ctx.settings, "context_fetch_timeout_seconds", 2.0) or 2.0),
        )
    except httpx.HTTPError as exc:
        logger.warning("specialist_supervisor_actor_context_unavailable", extra={"error": str(exc)})
        stale_actor = _cache_get(_ACTOR_CONTEXT_CACHE, cache_key, allow_stale=True)
        return stale_actor if isinstance(stale_actor, dict) else None
    actor = payload.get("actor") if isinstance(payload, dict) else None
    if not isinstance(actor, dict):
        return None
    return _cache_set(_ACTOR_CONTEXT_CACHE, cache_key, actor, ttl_seconds=30.0)


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
            timeout_seconds=float(getattr(ctx.settings, "context_fetch_timeout_seconds", 2.0) or 2.0),
        )
    except httpx.HTTPError as exc:
        logger.warning("specialist_supervisor_conversation_context_unavailable", extra={"error": str(exc)})
        return None
    return payload if isinstance(payload, dict) else None


async def fetch_public_school_profile(ctx: Any) -> dict[str, Any] | None:
    profile = await fetch_public_payload(ctx, "/v1/public/school-profile", "profile")
    if not isinstance(profile, dict):
        return None
    hydrated_profile = dict(profile)
    if not isinstance(hydrated_profile.get("public_timeline"), list):
        timeline = await fetch_public_payload(ctx, "/v1/public/timeline", "timeline")
        timeline_entries = timeline.get("entries") if isinstance(timeline, dict) else None
        if isinstance(timeline_entries, list):
            hydrated_profile["public_timeline"] = timeline_entries
    return hydrated_profile


async def fetch_public_payload(ctx: Any, path: str, key: str) -> Any:
    cache_key = f"{path}:{key}"
    cached = _cache_get(_PUBLIC_RESOURCE_CACHE, cache_key)
    if cached is not None:
        return cached
    try:
        payload = await _http_get(
            ctx.http_client,
            base_url=ctx.settings.api_core_url,
            path=path,
            token=ctx.settings.internal_api_token,
            timeout_seconds=float(getattr(ctx.settings, "public_resource_timeout_seconds", 2.0) or 2.0),
        )
    except httpx.HTTPError as exc:
        logger.warning(
            "specialist_public_payload_unavailable",
            extra={"path": path, "key": key, "error": str(exc)},
        )
        stale_payload = _cache_get(_PUBLIC_RESOURCE_CACHE, cache_key, allow_stale=True)
        if stale_payload is not None:
            logger.info("specialist_public_payload_stale_cache_hit", extra={"path": path, "key": key})
            return stale_payload
        return None
    if not isinstance(payload, dict):
        return None
    value = payload.get(key)
    return _cache_set(
        _PUBLIC_RESOURCE_CACHE,
        cache_key,
        value,
        ttl_seconds=float(getattr(ctx.settings, "public_resource_cache_ttl_seconds", 120.0) or 120.0),
    )


async def orchestrator_preview(ctx: Any) -> dict[str, Any] | None:
    from .semantic_ingress_runtime import (
        apply_semantic_ingress_preview_hint,
        maybe_resolve_semantic_ingress_plan,
        maybe_resolve_turn_frame,
        resolve_turn_frame_authenticated_flag,
    )

    user = getattr(ctx.request, "user", None)
    user_role = getattr(user, "role", None)
    user_scopes = getattr(user, "scopes", ()) or ()
    cache_key = "|".join(
        (
            str(_conversation_external_id(ctx)),
            str(ctx.request.message),
            str(getattr(user, "authenticated", False)),
            str(getattr(user_role, "value", user_role)),
            ",".join(sorted(str(item) for item in user_scopes)),
            str(ctx.request.allow_graph_rag),
            str(ctx.request.allow_handoff),
        )
    )
    cached_preview = _cache_get(
        _ORCHESTRATOR_PREVIEW_CACHE,
        cache_key,
    )
    if isinstance(cached_preview, dict):
        return cached_preview
    message = _normalize_text(str(ctx.request.message or ""))
    domain = "institution"
    mode = "hybrid_retrieval"
    retrieval_backend = "qdrant_hybrid"
    access_tier = "public"

    if any(hint in message for hint in _FINANCE_HINTS):
        domain = "finance"
    elif any(hint in message for hint in _ACADEMIC_HINTS):
        domain = "academic"
    elif any(hint in message for hint in _CALENDAR_HINTS):
        domain = "calendar"
    elif any(hint in message for hint in _SUPPORT_HINTS):
        domain = "support"

    if domain in {"finance", "academic"} and bool(getattr(user, "authenticated", False)):
        access_tier = "authenticated"
        mode = "structured_tool"
        retrieval_backend = "none"
    elif domain == "support":
        mode = "structured_tool"
        retrieval_backend = "none"

    preview = {
        "mode": mode,
        "classification": {
            "domain": domain,
            "access_tier": access_tier,
            "confidence": 0.55,
            "reason": "specialist_local_preview_hint",
        },
        "retrieval_backend": retrieval_backend,
        "selected_tools": [],
        "graph_path": ["specialist_supervisor", "local_preview_hint"],
        "reason": "specialist_local_preview_hint",
    }
    semantic_ingress_plan = await maybe_resolve_semantic_ingress_plan(
        settings=ctx.settings,
        request_message=ctx.request.message,
        conversation_context=getattr(ctx, "conversation_context", None),
        preview_hint=preview,
    )
    if semantic_ingress_plan is not None:
        preview = apply_semantic_ingress_preview_hint(
            preview_hint=preview,
            plan=semantic_ingress_plan,
        )
    turn_frame_authenticated = resolve_turn_frame_authenticated_flag(
        request_message=ctx.request.message,
        authenticated=bool(getattr(user, "authenticated", False)),
        actor=getattr(ctx, "actor", None),
    )
    turn_frame = await maybe_resolve_turn_frame(
        settings=ctx.settings,
        request_message=ctx.request.message,
        conversation_context=getattr(ctx, "conversation_context", None),
        preview_hint=preview,
        authenticated=turn_frame_authenticated,
    )
    if isinstance(turn_frame, dict):
        preview["turn_frame"] = turn_frame
        capability_id = str(turn_frame.get("capability_id") or "").strip()
        capability_domain = str(turn_frame.get("domain") or "").strip()
        capability_access_tier = str(turn_frame.get("access_tier") or "").strip()
        capability_scope = str(turn_frame.get("scope") or "").strip()
        public_conversation_act = str(turn_frame.get("public_conversation_act") or "").strip()
        if capability_id:
            preview["reason"] = f"specialist_turn_frame:{capability_id}"
            preview["graph_path"] = [
                *list(preview.get("graph_path") or ["specialist_supervisor", "local_preview_hint"]),
                f"turn_frame:{capability_id}",
            ]
        if capability_scope == "public" and capability_id:
            preview["mode"] = "structured_tool"
            preview["retrieval_backend"] = "none"
            selected_tools = ["get_public_profile_bundle"]
            if public_conversation_act == "pricing":
                selected_tools.append("project_public_pricing")
            preview["selected_tools"] = list(dict.fromkeys(selected_tools))
        elif capability_scope == "protected" and capability_id:
            preview["mode"] = "structured_tool"
            preview["retrieval_backend"] = "none"
            selected_tools: list[str] = []
            if capability_domain == "finance":
                selected_tools.append("fetch_financial_summary")
            elif capability_domain == "academic":
                selected_tools.append("fetch_academic_summary")
            preview["selected_tools"] = list(dict.fromkeys(selected_tools))
        classification = preview.get("classification") if isinstance(preview.get("classification"), dict) else {}
        if capability_domain:
            classification["domain"] = capability_domain
        if capability_access_tier:
            classification["access_tier"] = capability_access_tier
        if capability_id:
            classification["reason"] = f"specialist_turn_frame:{capability_id}"
        preview["classification"] = classification
    return _cache_set(
        _ORCHESTRATOR_PREVIEW_CACHE,
        cache_key,
        preview,
        ttl_seconds=float(getattr(ctx.settings, "orchestrator_preview_cache_ttl_seconds", 20.0) or 20.0),
    )


async def orchestrator_retrieval_search(
    ctx: Any,
    *,
    query: str,
    visibility: str = "public",
    category: str | None = None,
    top_k: int = 4,
    profile: str | None = None,
) -> dict[str, Any] | None:
    effective_category, effective_top_k, effective_profile = _effective_retrieval_request(
        query=query,
        visibility=visibility,
        category=category,
        top_k=top_k,
        profile=profile,
    )
    cache_key = "|".join(
        (
            str(query),
            str(visibility),
            str(effective_category or ""),
            str(effective_top_k),
            str(effective_profile or ""),
        )
    )
    cached_payload = _cache_get(_ORCHESTRATOR_RETRIEVAL_CACHE, cache_key)
    if isinstance(cached_payload, dict):
        return cached_payload
    try:
        remote_body: dict[str, Any] | None = None
        orchestrator_url = str(getattr(ctx.settings, "orchestrator_url", "") or "").strip().rstrip("/")
        if orchestrator_url:
            try:
                response = await ctx.http_client.post(
                    f"{orchestrator_url}/v1/retrieval/search",
                    json={
                        "query": query,
                        "top_k": effective_top_k,
                        "visibility": visibility,
                        "category": effective_category,
                        "profile": effective_profile,
                    },
                    timeout=float(getattr(ctx.settings, "orchestrator_timeout_seconds", 20.0) or 20.0),
                )
                response.raise_for_status()
                payload = response.json()
                if isinstance(payload, dict):
                    remote_body = payload
            except Exception as exc:
                logger.info("specialist_remote_retrieval_unavailable: %s", exc)

        retrieval_service = get_retrieval_service(
            database_url=str(ctx.settings.database_url),
            qdrant_url=str(ctx.settings.qdrant_url),
            collection_name=str(ctx.settings.qdrant_documents_collection),
            embedding_model=str(ctx.settings.document_embedding_model),
            enable_query_variants=bool(ctx.settings.retrieval_enable_query_variants),
            enable_late_interaction_rerank=bool(ctx.settings.retrieval_enable_late_interaction_rerank),
            late_interaction_model=str(ctx.settings.retrieval_late_interaction_model),
            candidate_pool_size=int(ctx.settings.retrieval_candidate_pool_size),
            cheap_candidate_pool_size=int(ctx.settings.retrieval_cheap_candidate_pool_size),
            deep_candidate_pool_size=int(ctx.settings.retrieval_deep_candidate_pool_size),
            rerank_fused_weight=float(ctx.settings.retrieval_rerank_fused_weight),
            rerank_late_interaction_weight=float(ctx.settings.retrieval_rerank_late_interaction_weight),
        )
        if isinstance(remote_body, dict):
            body = remote_body
        else:
            retrieval_profile = RetrievalProfile(effective_profile) if effective_profile else None
            search_response = retrieval_service.hybrid_search(
                query=query,
                top_k=effective_top_k,
                visibility=visibility,
                category=effective_category,
                profile=retrieval_profile,
            )
            body = search_response.model_dump(mode="json")
        if visibility == "restricted" and looks_like_restricted_document_query(query):
            fallback_hits = retrieve_relevant_restricted_hits_with_fallback(
                retrieval_service,
                query=query,
                hits=list(body.get("hits") or []),
                top_k=min(effective_top_k, 4),
                visibility=visibility,
                category=effective_category,
            )
            if fallback_hits:
                body["hits"] = [
                    hit.model_dump(mode="json") if hasattr(hit, "model_dump") else dict(hit)
                    for hit in fallback_hits
                ]
        return _cache_set(
            _ORCHESTRATOR_RETRIEVAL_CACHE,
            cache_key,
            body,
            ttl_seconds=float(getattr(ctx.settings, "orchestrator_retrieval_cache_ttl_seconds", 45.0) or 45.0),
        )
    except Exception as exc:
        logger.warning("specialist_local_retrieval_unavailable: %s", exc)
        stale_payload = _cache_get(_ORCHESTRATOR_RETRIEVAL_CACHE, cache_key, allow_stale=True)
        if isinstance(stale_payload, dict):
            logger.info("specialist_local_retrieval_stale_cache_hit")
            return stale_payload
        return None


async def orchestrator_graph_rag_query(ctx: Any, *, query: str) -> dict[str, Any] | None:
    timeout_seconds = float(getattr(ctx.settings, "graph_rag_sync_timeout_seconds", 12.0) or 12.0)
    preferred_method = str(getattr(ctx.settings, "graph_rag_sync_method", "local") or "local").strip().lower()
    fallback_enabled = bool(getattr(ctx.settings, "graph_rag_sync_fallback_enabled", False))
    try:
        response = await ctx.http_client.post(
            f"{ctx.settings.orchestrator_url.rstrip('/')}/v1/internal/graphrag/query",
            timeout=httpx.Timeout(timeout_seconds + 2.0, connect=1.0),
            headers={
                "X-Internal-Api-Token": ctx.settings.internal_api_token,
                "Content-Type": "application/json",
            },
            json={
                "query": query,
                "preferred_method": preferred_method if preferred_method in {"local", "global", "drift"} else None,
                "max_seconds": max(3, int(round(timeout_seconds))),
                "fallback_enabled": fallback_enabled,
            },
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
                            "stage_timings_ms": ctx.trace.stage_timings_ms,
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
                            "stage_timings_ms": ctx.trace.stage_timings_ms,
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
