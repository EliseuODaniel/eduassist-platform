from __future__ import annotations

import logging
import time
from typing import Any

import httpx
from eduassist_observability import canonicalize_evidence_strategy, canonicalize_risk_flags

from ..models import (
    AccessTier,
    IntentClassification,
    MessageResponse,
    OrchestrationMode,
    QueryDomain,
    RetrievalBackend,
)
from ..public_doc_knowledge import compose_public_canonical_lane_answer, match_public_canonical_lane
from ..serving_telemetry import record_stack_outcome
from .base import ResponseEngine, ShadowRunResult

logger = logging.getLogger(__name__)
_REMOTE_PILOT_CLIENTS: dict[tuple[str, float], httpx.AsyncClient] = {}
_REMOTE_PILOT_FAILURES: dict[str, tuple[int, float]] = {}
_PUBLIC_OPEN_DOCUMENTARY_LOCAL_FALLBACK_LANES = {
    "public_bundle.integral_study_support",
    "public_bundle.governance_protocol",
    "public_bundle.health_emergency_bundle",
    "public_bundle.visibility_boundary",
    "public_bundle.permanence_family_support",
}


def _strict_safe_response_text(*, request: Any) -> str:
    if bool(getattr(getattr(request, "user", None), "authenticated", False)):
        return (
            "Nao consegui consolidar essa resposta premium com seguranca agora. "
            "Se quiser, me diga exatamente se voce quer ver notas, frequencia, documentacao, financeiro ou status de protocolo."
        )
    return (
        "Nao consegui concluir essa resposta premium agora. "
        "Se quiser, reformule em uma frase mais direta ou repita em instantes."
    )


def _normalize_query_domain(value: Any) -> QueryDomain:
    raw = str(value or "").strip().lower()
    if raw == "workflow":
        return QueryDomain.support
    try:
        return QueryDomain(raw)
    except Exception:
        return QueryDomain.unknown


def _normalize_access_tier(value: Any) -> AccessTier:
    raw = str(value or "").strip().lower()
    try:
        return AccessTier(raw)
    except Exception:
        return AccessTier.public


def _normalize_mode(value: Any) -> OrchestrationMode:
    raw = str(value or "").strip().lower()
    try:
        return OrchestrationMode(raw)
    except Exception:
        return OrchestrationMode.clarify


def _normalize_retrieval_backend(value: Any) -> RetrievalBackend:
    raw = str(value or "").strip().lower()
    try:
        return RetrievalBackend(raw)
    except Exception:
        return RetrievalBackend.none


def _normalize_remote_answer(answer: dict[str, Any]) -> dict[str, Any]:
    normalized = dict(answer)
    classification = dict(normalized.get("classification") or {})
    classification["domain"] = _normalize_query_domain(classification.get("domain")).value
    classification["access_tier"] = _normalize_access_tier(classification.get("access_tier")).value
    normalized["classification"] = classification
    normalized["mode"] = _normalize_mode(normalized.get("mode")).value
    normalized["retrieval_backend"] = _normalize_retrieval_backend(normalized.get("retrieval_backend")).value
    evidence_pack = dict(normalized.get("evidence_pack") or {})
    if evidence_pack:
        evidence_pack["strategy"] = canonicalize_evidence_strategy(
            evidence_pack.get("strategy"),
            retrieval_backend=normalized["retrieval_backend"],
        )
        normalized["evidence_pack"] = evidence_pack
    normalized["risk_flags"] = canonicalize_risk_flags(normalized.get("risk_flags"))
    normalized['used_llm'] = bool(normalized.get('used_llm', False))
    normalized['llm_stages'] = [str(item).strip() for item in (normalized.get('llm_stages') or []) if str(item).strip()]
    normalized['final_polish_eligible'] = bool(normalized.get('final_polish_eligible', False))
    normalized['final_polish_applied'] = bool(normalized.get('final_polish_applied', False))
    normalized['final_polish_mode'] = str(normalized.get('final_polish_mode') or '')
    normalized['final_polish_reason'] = str(normalized.get('final_polish_reason') or '')
    normalized['final_polish_changed_text'] = bool(normalized.get('final_polish_changed_text', False))
    normalized['final_polish_preserved_fallback'] = bool(normalized.get('final_polish_preserved_fallback', False))
    return normalized


def _mark_cross_stack_fallback(response: MessageResponse) -> MessageResponse:
    graph_path = [str(item).strip() for item in response.graph_path if str(item).strip()]
    if not graph_path or graph_path[0] != "specialist_supervisor":
        graph_path = ["specialist_supervisor", "remote_unavailable", "langgraph_fallback", *graph_path]
    else:
        graph_path = ["specialist_supervisor", "remote_unavailable", "langgraph_fallback", *graph_path[1:]]

    risk_flags = list(response.risk_flags)
    for flag in ("dependency_unavailable", "cross_stack_fallback"):
        if flag not in risk_flags:
            risk_flags.append(flag)
    return response.model_copy(
        update={
            "graph_path": graph_path,
            "risk_flags": risk_flags,
        }
    )


def _lane_domain(lane: str) -> QueryDomain:
    if any(marker in lane for marker in {'calendar', 'timeline'}):
        return QueryDomain.calendar
    return QueryDomain.institution


def _local_public_canonical_lane_response(*, request: Any, lane: str) -> MessageResponse | None:
    answer_text = compose_public_canonical_lane_answer(lane, profile=None)
    if not answer_text:
        return None
    domain = _lane_domain(lane)
    return MessageResponse(
        message_text=answer_text,
        mode=OrchestrationMode.structured_tool,
        classification=IntentClassification(
            domain=domain,
            access_tier=AccessTier.public,
            confidence=1.0,
            reason=f"specialist_supervisor_local_public_canonical_lane:{lane}",
        ),
        retrieval_backend=RetrievalBackend.none,
        selected_tools=['get_public_school_profile'],
        citations=[],
        visual_assets=[],
        suggested_replies=[],
        calendar_events=[],
        evidence_pack=None,
        needs_authentication=False,
        graph_path=["specialist_supervisor", "local_public_canonical_lane", lane],
        risk_flags=[],
        reason=f"specialist_supervisor_local_public_canonical_lane:{lane}",
        used_llm=False,
        llm_stages=[],
        final_polish_eligible=False,
        final_polish_applied=False,
        final_polish_mode='skip',
        final_polish_reason='deterministic_answer',
        final_polish_changed_text=False,
        final_polish_preserved_fallback=False,
        candidate_chosen='deterministic',
        candidate_reason=f'public_canonical_lane:{lane}',
        retrieval_probe_topic=None,
        response_cache_hit=False,
        response_cache_kind=None,
    )


def _should_use_local_public_fallback_before_remote(
    *,
    lane: str | None,
    llm_forced_mode: bool,
    pilot_url: str,
) -> bool:
    if not lane:
        return False
    if not llm_forced_mode:
        return True
    if lane not in _PUBLIC_OPEN_DOCUMENTARY_LOCAL_FALLBACK_LANES:
        return False
    if not pilot_url:
        return True
    return _pilot_is_temporarily_open_circuit(pilot_url)


def _pilot_client(*, pilot_url: str, timeout_seconds: float) -> httpx.AsyncClient:
    cache_key = (pilot_url.rstrip("/"), round(float(timeout_seconds), 3))
    client = _REMOTE_PILOT_CLIENTS.get(cache_key)
    if client is not None:
        return client
    limits = httpx.Limits(
        max_keepalive_connections=10,
        max_connections=20,
        keepalive_expiry=30.0,
    )
    client = httpx.AsyncClient(
        timeout=httpx.Timeout(timeout_seconds, connect=3.0),
        limits=limits,
        headers={"Content-Type": "application/json"},
    )
    _REMOTE_PILOT_CLIENTS[cache_key] = client
    return client


def _pilot_is_temporarily_open_circuit(pilot_url: str) -> bool:
    failure_state = _REMOTE_PILOT_FAILURES.get(pilot_url.rstrip("/"))
    if failure_state is None:
        return False
    _count, blocked_until = failure_state
    return blocked_until > time.monotonic()


def _record_pilot_failure(pilot_url: str) -> None:
    key = pilot_url.rstrip("/")
    count, blocked_until = _REMOTE_PILOT_FAILURES.get(key, (0, 0.0))
    now = time.monotonic()
    new_count = count + 1 if blocked_until <= now else count + 1
    cooldown = 10.0 if new_count == 1 else 20.0 if new_count == 2 else 30.0
    _REMOTE_PILOT_FAILURES[key] = (new_count, now + cooldown if cooldown else 0.0)


def _clear_pilot_failure_state(pilot_url: str) -> None:
    _REMOTE_PILOT_FAILURES.pop(pilot_url.rstrip("/"), None)


class SpecialistSupervisorEngine(ResponseEngine):
    name = "specialist_supervisor"
    ready = False

    async def _call_remote_pilot(self, *, request: Any, settings: Any) -> dict[str, Any] | None:
        pilot_url = str(getattr(settings, "specialist_supervisor_pilot_url", "") or "").strip()
        if not pilot_url:
            return None
        if _pilot_is_temporarily_open_circuit(pilot_url):
            return None
        timeout_seconds = float(getattr(settings, "specialist_supervisor_pilot_timeout_seconds", 18.0) or 18.0)
        client = _pilot_client(pilot_url=pilot_url, timeout_seconds=timeout_seconds)
        response = await client.post(
            f"{pilot_url.rstrip('/')}/v1/respond-raw",
            headers={"X-Internal-Api-Token": settings.internal_api_token},
            json={
                "message": getattr(request, "message", ""),
                "conversation_id": getattr(request, "conversation_id", None),
                "telegram_chat_id": getattr(request, "telegram_chat_id", None),
                "channel": getattr(getattr(request, "channel", None), "value", "telegram"),
                "user": getattr(getattr(request, "user", None), "model_dump", lambda **_: {})(
                    mode="json"
                ),
                "allow_graph_rag": bool(getattr(request, "allow_graph_rag", True)),
                "allow_handoff": bool(getattr(request, "allow_handoff", True)),
                "debug_options": dict(getattr(request, "debug_options", {}) or {}),
                "trace_context": dict(getattr(request, "trace_context", {}) or {}),
            },
        )
        response.raise_for_status()
        payload = response.json()
        _clear_pilot_failure_state(pilot_url)
        return payload if isinstance(payload, dict) else None

    async def respond(self, *, request: Any, settings: Any, engine_mode: str | None = None) -> Any:
        started_at = time.monotonic()
        strict_isolation = bool(getattr(settings, "strict_framework_isolation_enabled", False))
        pilot_url = str(getattr(settings, "specialist_supervisor_pilot_url", "") or "").strip()
        request_user = getattr(request, "user", None)
        is_effectively_public = not bool(getattr(request_user, "authenticated", False))
        llm_forced_mode = bool(getattr(settings, 'feature_flag_final_polish_force_llm', False)) or bool(
            (getattr(request, 'debug_options', {}) or {}).get('llm_forced_mode')
        )
        canonical_lane = None
        if is_effectively_public:
            canonical_lane = match_public_canonical_lane(str(getattr(request, "message", "") or ""))
        if is_effectively_public and _should_use_local_public_fallback_before_remote(
            lane=canonical_lane,
            llm_forced_mode=llm_forced_mode,
            pilot_url=pilot_url,
        ):
            local_public_answer = _local_public_canonical_lane_response(request=request, lane=canonical_lane)
            if local_public_answer is not None:
                record_stack_outcome(
                    stack_name='specialist_supervisor',
                    latency_ms=(time.monotonic() - started_at) * 1000,
                    success=True,
                    timeout=False,
                    cache_hit=False,
                    used_llm=False,
                    candidate_kind=local_public_answer.candidate_chosen,
                )
                return local_public_answer
        try:
            payload = await self._call_remote_pilot(request=request, settings=settings)
        except Exception:
            logger.exception("specialist_supervisor_http_failed")
            if pilot_url:
                _record_pilot_failure(pilot_url)
            payload = None

        answer = payload.get("answer") if isinstance(payload, dict) and isinstance(payload.get("answer"), dict) else None
        if isinstance(answer, dict):
            response = MessageResponse.model_validate(_normalize_remote_answer(answer))
            record_stack_outcome(
                stack_name='specialist_supervisor',
                latency_ms=(time.monotonic() - started_at) * 1000,
                success=True,
                timeout=False,
                cache_hit=bool(response.response_cache_hit),
                used_llm=bool(response.used_llm),
                candidate_kind=response.candidate_chosen,
            )
            return response

        if is_effectively_public and canonical_lane in _PUBLIC_OPEN_DOCUMENTARY_LOCAL_FALLBACK_LANES:
            local_public_answer = _local_public_canonical_lane_response(request=request, lane=canonical_lane)
            if local_public_answer is not None:
                record_stack_outcome(
                    stack_name='specialist_supervisor',
                    latency_ms=(time.monotonic() - started_at) * 1000,
                    success=True,
                    timeout=True,
                    cache_hit=False,
                    used_llm=False,
                    candidate_kind=local_public_answer.candidate_chosen,
                )
                return local_public_answer

        if strict_isolation and not is_effectively_public:
            response = MessageResponse(
                message_text=_strict_safe_response_text(request=request),
                mode=OrchestrationMode.clarify,
                classification=IntentClassification(
                    domain=QueryDomain.unknown,
                    access_tier=AccessTier.public,
                    confidence=0.0,
                    reason="specialist_supervisor_strict_safe_fallback",
                ),
                retrieval_backend=RetrievalBackend.none,
                selected_tools=[],
                citations=[],
                visual_assets=[],
                suggested_replies=[],
                calendar_events=[],
                evidence_pack=None,
                needs_authentication=False,
                graph_path=["specialist_supervisor", "safe_fallback"],
                risk_flags=["dependency_unavailable"],
                reason="specialist_supervisor_strict_safe_fallback",
                used_llm=False,
                llm_stages=[],
            )
            record_stack_outcome(
                stack_name='specialist_supervisor',
                latency_ms=(time.monotonic() - started_at) * 1000,
                success=False,
                timeout=False,
                cache_hit=False,
                used_llm=False,
                candidate_kind=response.candidate_chosen,
            )
            return response

        from ..runtime import generate_message_response

        logger.warning("specialist_supervisor_fallback_to_langgraph")
        fallback_response = await generate_message_response(
            request=request,
            settings=settings,
            engine_name="specialist_supervisor_stub",
            engine_mode=str(engine_mode or self.name),
        )
        if isinstance(fallback_response, MessageResponse):
            marked_response = _mark_cross_stack_fallback(fallback_response)
            record_stack_outcome(
                stack_name='specialist_supervisor',
                latency_ms=(time.monotonic() - started_at) * 1000,
                success=False,
                timeout=True,
                cache_hit=bool(marked_response.response_cache_hit),
                used_llm=bool(marked_response.used_llm),
                candidate_kind=marked_response.candidate_chosen,
            )
            return marked_response
        return fallback_response

    async def shadow_compare(self, *, request: Any, settings: Any) -> ShadowRunResult:
        pilot_url = str(getattr(settings, "specialist_supervisor_pilot_url", "") or "").strip()
        if not pilot_url:
            return ShadowRunResult(
                engine_name=self.name,
                executed=False,
                reason="specialist_supervisor_pilot_unconfigured",
            )
        try:
            payload = await self._call_remote_pilot(request=request, settings=settings)
            return ShadowRunResult(
                engine_name=self.name,
                executed=bool(isinstance(payload, dict) and payload.get("executed")),
                reason=str((payload or {}).get("reason", "") or ""),
                metadata=(payload or {}).get("metadata") if isinstance((payload or {}).get("metadata"), dict) else None,
            )
        except Exception as exc:
            logger.exception("specialist_supervisor_shadow_http_failed")
            return ShadowRunResult(
                engine_name=self.name,
                executed=False,
                reason="specialist_supervisor_shadow_http_failed",
                error=str(exc),
            )
