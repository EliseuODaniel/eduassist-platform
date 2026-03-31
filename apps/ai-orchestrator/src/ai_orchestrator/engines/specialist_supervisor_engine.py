from __future__ import annotations

import logging
from typing import Any

import httpx

from ..models import AccessTier, IntentClassification, MessageResponse, OrchestrationMode, QueryDomain, RetrievalBackend
from .base import ResponseEngine, ShadowRunResult

logger = logging.getLogger(__name__)


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
    return normalized


class SpecialistSupervisorEngine(ResponseEngine):
    name = "specialist_supervisor"
    ready = False

    async def _call_remote_pilot(self, *, request: Any, settings: Any) -> dict[str, Any] | None:
        pilot_url = str(getattr(settings, "specialist_supervisor_pilot_url", "") or "").strip()
        if not pilot_url:
            return None
        timeout_seconds = float(getattr(settings, "specialist_supervisor_pilot_timeout_seconds", 75.0) or 75.0)
        async with httpx.AsyncClient(timeout=httpx.Timeout(timeout_seconds, connect=5.0)) as client:
            response = await client.post(
                f"{pilot_url.rstrip('/')}/v1/respond",
                headers={
                    "X-Internal-Api-Token": settings.internal_api_token,
                    "Content-Type": "application/json",
                },
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
                },
            )
        response.raise_for_status()
        payload = response.json()
        return payload if isinstance(payload, dict) else None

    async def respond(self, *, request: Any, settings: Any, engine_mode: str | None = None) -> Any:
        strict_isolation = bool(getattr(settings, "strict_framework_isolation_enabled", False))
        try:
            payload = await self._call_remote_pilot(request=request, settings=settings)
        except Exception:
            logger.exception("specialist_supervisor_http_failed")
            payload = None

        answer = payload.get("answer") if isinstance(payload, dict) and isinstance(payload.get("answer"), dict) else None
        if isinstance(answer, dict):
            return MessageResponse.model_validate(_normalize_remote_answer(answer))

        if strict_isolation:
            return MessageResponse(
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
            )

        from ..runtime import generate_message_response

        logger.warning("specialist_supervisor_fallback_to_langgraph")
        return await generate_message_response(
            request=request,
            settings=settings,
            engine_name="specialist_supervisor_stub",
            engine_mode=str(engine_mode or self.name),
        )

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
