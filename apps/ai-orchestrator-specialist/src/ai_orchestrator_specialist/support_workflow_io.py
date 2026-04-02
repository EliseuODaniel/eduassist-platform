from __future__ import annotations

import re
from typing import Any, Awaitable, Callable


def _normalize_text(value: str | None) -> str:
    return re.sub(r"\s+", " ", str(value or "").strip().lower())


def _strip_none(payload: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in payload.items() if value is not None}


async def _create_visit_booking_payload(
    ctx: Any,
    *,
    http_post: Callable[..., Awaitable[dict[str, Any] | None]],
    effective_conversation_id: Callable[[Any], str],
) -> dict[str, Any]:
    normalized = _normalize_text(ctx.request.message)
    preferred_window = None
    for term in ("quinta a tarde", "quinta de tarde", "quinta-feira a tarde", "manha", "tarde", "noite"):
        if term in normalized:
            preferred_window = term
            break
    payload = await http_post(
        ctx.http_client,
        base_url=ctx.settings.api_core_url,
        path="/v1/internal/workflows/visit-bookings",
        token=ctx.settings.internal_api_token,
        payload=_strip_none(
            {
                "conversation_external_id": effective_conversation_id(ctx.request),
                "channel": ctx.request.channel.value,
                "telegram_chat_id": ctx.request.telegram_chat_id,
                "preferred_window": preferred_window,
                "notes": ctx.request.message,
            }
        ),
    )
    return payload or {"created": False}


async def _create_institutional_request_payload(
    ctx: Any,
    *,
    target_area: str,
    category: str = "handoff",
    http_post: Callable[..., Awaitable[dict[str, Any] | None]],
    effective_conversation_id: Callable[[Any], str],
) -> dict[str, Any]:
    payload = await http_post(
        ctx.http_client,
        base_url=ctx.settings.api_core_url,
        path="/v1/internal/workflows/institutional-requests",
        token=ctx.settings.internal_api_token,
        payload=_strip_none(
            {
                "conversation_external_id": effective_conversation_id(ctx.request),
                "channel": ctx.request.channel.value,
                "telegram_chat_id": ctx.request.telegram_chat_id,
                "target_area": target_area,
                "category": category,
                "subject": ctx.request.message,
                "details": ctx.request.message,
            }
        ),
    )
    return payload or {"created": False}


async def _create_support_handoff_payload(
    ctx: Any,
    *,
    queue_name: str,
    summary: str | None = None,
    build_support_handoff_summary: Callable[..., str],
    http_post: Callable[..., Awaitable[dict[str, Any] | None]],
    effective_conversation_id: Callable[[Any], str],
) -> dict[str, Any]:
    payload = await http_post(
        ctx.http_client,
        base_url=ctx.settings.api_core_url,
        path="/v1/internal/support/handoffs",
        token=ctx.settings.internal_api_token,
        payload=_strip_none(
            {
                "conversation_external_id": effective_conversation_id(ctx.request),
                "channel": ctx.request.channel.value,
                "queue_name": queue_name,
                "summary": summary or build_support_handoff_summary(ctx, queue_name=queue_name),
                "telegram_chat_id": ctx.request.telegram_chat_id,
                "user_message": ctx.request.message,
            }
        ),
    )
    return payload or {"created": False}


async def _workflow_status_payload(
    ctx: Any,
    *,
    workflow_kind: str | None = None,
    protocol_code_hint: str | None = None,
    http_get: Callable[..., Awaitable[dict[str, Any] | None]],
    effective_conversation_id: Callable[[Any], str],
) -> dict[str, Any]:
    payload = await http_get(
        ctx.http_client,
        base_url=ctx.settings.api_core_url,
        path="/v1/internal/workflows/status",
        token=ctx.settings.internal_api_token,
        params=_strip_none(
            {
                "conversation_external_id": effective_conversation_id(ctx.request),
                "channel": ctx.request.channel.value,
                "workflow_kind": workflow_kind,
                "protocol_code": protocol_code_hint,
            }
        ),
    )
    return payload or {"found": False, "item": None}
