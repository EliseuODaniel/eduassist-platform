from __future__ import annotations

import logging
from typing import Any

from .base import ResponseEngine, ShadowRunResult

logger = logging.getLogger(__name__)


class CrewAIEngine(ResponseEngine):
    name = 'crewai'
    ready = False

    def __init__(self, *, fallback_engine: ResponseEngine) -> None:
        self._fallback_engine = fallback_engine

    async def respond(self, *, request: Any, settings: Any) -> Any:
        logger.warning('crewai_engine_not_implemented_fallback_to_langgraph')
        return await self._fallback_engine.respond(request=request, settings=settings)

    async def shadow_compare(self, *, request: Any, settings: Any) -> ShadowRunResult:
        logger.info('crewai_shadow_not_implemented')
        return ShadowRunResult(
            engine_name=self.name,
            executed=False,
            reason='crewai_not_implemented',
        )
