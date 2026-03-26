from __future__ import annotations

import hashlib
import logging
from dataclasses import dataclass
from typing import Any

from .engines.base import ResponseEngine, ShadowRunResult
from .engines.crewai_engine import CrewAIEngine, infer_request_slice
from .engines.langgraph_engine import LangGraphEngine

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class EngineBundle:
    mode: str
    primary: ResponseEngine
    shadow: ResponseEngine | None = None
    experiment: dict[str, Any] | None = None


def _parse_csv_items(value: str | None) -> set[str]:
    return {item.strip() for item in str(value or '').split(',') if item.strip()}


def _stable_rollout_bucket(*, request: Any, slice_name: str) -> int:
    conversation_id = str(getattr(request, 'conversation_id', '') or '')
    telegram_chat_id = str(getattr(request, 'telegram_chat_id', '') or '')
    message = str(getattr(request, 'message', '') or '')
    seed = f'{slice_name}|{conversation_id}|{telegram_chat_id}|{message[:64]}'
    digest = hashlib.sha256(seed.encode('utf-8')).hexdigest()
    return int(digest[:8], 16) % 100


def _request_matches_allowlist(*, request: Any, settings: Any) -> bool:
    chat_allowlist = _parse_csv_items(getattr(settings, 'orchestrator_experiment_telegram_chat_allowlist', ''))
    conversation_allowlist = _parse_csv_items(getattr(settings, 'orchestrator_experiment_conversation_allowlist', ''))
    if not chat_allowlist and not conversation_allowlist:
        return True
    chat_id = str(getattr(request, 'telegram_chat_id', '') or '')
    conversation_id = str(getattr(request, 'conversation_id', '') or '')
    return (chat_id and chat_id in chat_allowlist) or (conversation_id and conversation_id in conversation_allowlist)


def _should_route_to_experiment(*, request: Any, settings: Any) -> tuple[bool, dict[str, Any] | None]:
    if not bool(getattr(settings, 'orchestrator_experiment_enabled', False)):
        return False, None
    if str(getattr(settings, 'orchestrator_engine', 'langgraph') or 'langgraph').strip().lower() != 'langgraph':
        return False, None
    if not str(getattr(settings, 'crewai_pilot_url', '') or '').strip():
        return False, None
    slice_name = infer_request_slice(request)
    configured_slices = _parse_csv_items(getattr(settings, 'orchestrator_experiment_slices', ''))
    if configured_slices and slice_name not in configured_slices:
        return False, None
    if not _request_matches_allowlist(request=request, settings=settings):
        return False, None
    rollout_percent = max(0, min(100, int(getattr(settings, 'orchestrator_experiment_rollout_percent', 0) or 0)))
    if rollout_percent <= 0:
        return False, None
    bucket = _stable_rollout_bucket(request=request, slice_name=slice_name)
    enrolled = bucket < rollout_percent
    metadata = {
        'slice': slice_name,
        'bucket': bucket,
        'rollout_percent': rollout_percent,
        'engine': str(getattr(settings, 'orchestrator_experiment_primary_engine', 'crewai') or 'crewai'),
        'enrolled': enrolled,
    }
    return enrolled, metadata


def build_engine_bundle(settings: Any, request: Any | None = None) -> EngineBundle:
    mode = str(getattr(settings, 'orchestrator_engine', 'langgraph') or 'langgraph').strip().lower()
    langgraph_engine = LangGraphEngine()
    crewai_engine = CrewAIEngine(fallback_engine=langgraph_engine)

    if request is not None:
        should_experiment, experiment = _should_route_to_experiment(request=request, settings=settings)
        if should_experiment:
            return EngineBundle(
                mode=f"experiment:{experiment['slice']}:{experiment['engine']}",
                primary=crewai_engine,
                shadow=None,
                experiment=experiment,
            )

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
