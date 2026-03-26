from __future__ import annotations

import logging
from typing import Any

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
        logger.info('crewai_shadow_public_slice')
        return await run_public_shadow_flow(request=request, settings=settings)
