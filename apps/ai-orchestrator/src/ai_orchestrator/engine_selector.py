from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

from .engines import CrewAIEngine, LangGraphEngine, ResponseEngine, ShadowRunResult

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class EngineBundle:
    mode: str
    primary: ResponseEngine
    shadow: ResponseEngine | None = None


def build_engine_bundle(settings: Any) -> EngineBundle:
    mode = str(getattr(settings, 'orchestrator_engine', 'langgraph') or 'langgraph').strip().lower()
    langgraph_engine = LangGraphEngine()
    crewai_engine = CrewAIEngine(fallback_engine=langgraph_engine)

    if mode == 'crewai':
        return EngineBundle(mode='crewai', primary=crewai_engine)
    if mode == 'shadow':
        return EngineBundle(mode='shadow', primary=langgraph_engine, shadow=crewai_engine)
    return EngineBundle(mode='langgraph', primary=langgraph_engine)


async def maybe_run_shadow(*, bundle: EngineBundle, request: Any, settings: Any) -> ShadowRunResult | None:
    if bundle.shadow is None:
        return None
    try:
        return await bundle.shadow.shadow_compare(request=request, settings=settings)
    except Exception as exc:  # pragma: no cover - defensive guard
        logger.exception('shadow_engine_failed')
        return ShadowRunResult(
            engine_name=getattr(bundle.shadow, 'name', 'shadow'),
            executed=False,
            reason='shadow_failed',
            error=str(exc),
        )
