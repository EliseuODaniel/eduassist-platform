from __future__ import annotations

import logging
from typing import Any

import httpx

from ..crewai.flow import run_public_shadow_flow
from .base import ResponseEngine, ShadowRunResult

logger = logging.getLogger(__name__)


class CrewAIEngine(ResponseEngine):
    name = 'crewai'
    ready = False

    def __init__(self, *, fallback_engine: ResponseEngine | None = None) -> None:
        self._fallback_engine = fallback_engine

    async def respond(self, *, request: Any, settings: Any) -> Any:
        from ..runtime import generate_message_response

        logger.warning('crewai_engine_not_implemented_fallback_to_langgraph')
        return await generate_message_response(
            request=request,
            settings=settings,
            engine_name='crewai_stub',
            engine_mode=str(getattr(settings, 'orchestrator_engine', self.name) or self.name),
        )

    async def shadow_compare(self, *, request: Any, settings: Any) -> ShadowRunResult:
        pilot_url = str(getattr(settings, 'crewai_pilot_url', '') or '').strip()
        if pilot_url:
            try:
                async with httpx.AsyncClient(timeout=20.0) as client:
                    response = await client.post(
                        f'{pilot_url.rstrip("/")}/v1/shadow/public',
                        headers={
                            'X-Internal-Api-Token': settings.internal_api_token,
                            'Content-Type': 'application/json',
                        },
                        json={
                            'message': getattr(request, 'message', ''),
                            'conversation_id': getattr(request, 'conversation_id', None),
                            'telegram_chat_id': getattr(request, 'telegram_chat_id', None),
                            'channel': getattr(getattr(request, 'channel', None), 'value', 'telegram'),
                        },
                    )
                response.raise_for_status()
                payload = response.json()
                if isinstance(payload, dict):
                    return ShadowRunResult(
                        engine_name=str(payload.get('engine_name', self.name) or self.name),
                        executed=bool(payload.get('executed')),
                        reason=str(payload.get('reason', '') or ''),
                        metadata=payload.get('metadata') if isinstance(payload.get('metadata'), dict) else {},
                    )
            except Exception as exc:
                logger.exception('crewai_shadow_http_failed')
                return ShadowRunResult(
                    engine_name=self.name,
                    executed=False,
                    reason='crewai_shadow_http_failed',
                    error=str(exc),
                )

        logger.info('crewai_shadow_public_slice_local_scaffold')
        return await run_public_shadow_flow(request=request, settings=settings)
