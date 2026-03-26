from __future__ import annotations

from typing import Any

import httpx
from eduassist_observability import set_span_attributes, start_span

from .engines.base import ShadowRunResult


def _effective_conversation_id(request: Any) -> str | None:
    conversation_id = getattr(request, 'conversation_id', None)
    if conversation_id:
        return str(conversation_id)
    channel = getattr(getattr(request, 'channel', None), 'value', None)
    telegram_chat_id = getattr(request, 'telegram_chat_id', None)
    if channel == 'telegram' and telegram_chat_id is not None:
        return f'telegram:{telegram_chat_id}'
    return None


async def _api_core_post(
    *,
    settings: Any,
    path: str,
    payload: dict[str, object],
) -> tuple[dict[str, Any] | None, int | None]:
    headers = {
        'X-Internal-Api-Token': settings.internal_api_token,
        'Content-Type': 'application/json',
    }
    with start_span(
        'eduassist.api_core.post.shadow',
        tracer_name='eduassist.ai_orchestrator.trace_bridge',
        **{
            'eduassist.api_core.path': path,
            'eduassist.api_core.has_payload': bool(payload),
        },
    ):
        try:
            async with httpx.AsyncClient(timeout=12.0) as client:
                response = await client.post(f'{settings.api_core_url}{path}', json=payload, headers=headers)
            response.raise_for_status()
            body = response.json()
            set_span_attributes(**{'http.status_code': response.status_code})
            if isinstance(body, dict):
                return body, response.status_code
            return None, response.status_code
        except httpx.HTTPStatusError as exc:
            set_span_attributes(**{'http.status_code': exc.response.status_code})
            return None, exc.response.status_code
        except Exception:
            return None, None


async def persist_shadow_trace(
    *,
    settings: Any,
    request: Any,
    primary_engine_name: str,
    primary_engine_mode: str,
    shadow_result: ShadowRunResult,
) -> None:
    conversation_external_id = _effective_conversation_id(request)
    if not conversation_external_id:
        return

    payload = {
        'channel': getattr(getattr(request, 'channel', None), 'value', 'telegram'),
        'conversation_external_id': conversation_external_id,
        'actor_user_id': None,
        'tool_calls': [
            {
                'tool_name': 'orchestration.shadow',
                'status': 'ok' if shadow_result.executed else 'skipped',
                'request_payload': {
                    'primary_engine_name': primary_engine_name,
                    'primary_engine_mode': primary_engine_mode,
                    'shadow_engine_name': shadow_result.engine_name,
                    'request_message': getattr(request, 'message', ''),
                },
                'response_payload': {
                    'executed': shadow_result.executed,
                    'reason': shadow_result.reason,
                    'error': shadow_result.error,
                    'metadata': shadow_result.metadata or {},
                },
            }
        ],
    }
    await _api_core_post(
        settings=settings,
        path='/v1/internal/conversations/tool-calls',
        payload=payload,
    )
