from __future__ import annotations

from collections import OrderedDict
import hashlib
import logging
from time import monotonic
from dataclasses import dataclass
from typing import Any

from .engines.base import ResponseEngine, ShadowRunResult
from .engines.crewai_engine import CrewAIEngine, infer_request_slice
from .engines.langgraph_engine import LangGraphEngine

logger = logging.getLogger(__name__)

_EXPERIMENT_AFFINITY: OrderedDict[str, dict[str, Any]] = OrderedDict()
_EXPERIMENT_AFFINITY_LIMIT = 2048
_EXPERIMENT_AFFINITY_TTL_SECONDS = 60 * 60 * 6


@dataclass(frozen=True)
class EngineBundle:
    mode: str
    primary: ResponseEngine
    shadow: ResponseEngine | None = None
    experiment: dict[str, Any] | None = None


def _parse_csv_items(value: str | None) -> set[str]:
    return {item.strip() for item in str(value or '').split(',') if item.strip()}


def _parse_slice_rollouts(value: str | None) -> dict[str, int]:
    result: dict[str, int] = {}
    for item in _parse_csv_items(value):
        separator = '=' if '=' in item else ':'
        if separator not in item:
            continue
        slice_name, raw_percent = item.split(separator, 1)
        slice_name = slice_name.strip()
        try:
            result[slice_name] = max(0, min(100, int(raw_percent.strip())))
        except ValueError:
            continue
    return result


def _experiment_affinity_key(request: Any) -> str | None:
    conversation_id = str(getattr(request, 'conversation_id', '') or '').strip()
    if conversation_id:
        return f'conversation:{conversation_id}'
    telegram_chat_id = str(getattr(request, 'telegram_chat_id', '') or '').strip()
    if telegram_chat_id:
        return f'telegram:{telegram_chat_id}'
    return None


def _prune_experiment_affinity() -> None:
    now = monotonic()
    stale_keys = [
        key
        for key, value in _EXPERIMENT_AFFINITY.items()
        if now - float(value.get('timestamp', now)) > _EXPERIMENT_AFFINITY_TTL_SECONDS
    ]
    for key in stale_keys:
        _EXPERIMENT_AFFINITY.pop(key, None)
    while len(_EXPERIMENT_AFFINITY) > _EXPERIMENT_AFFINITY_LIMIT:
        _EXPERIMENT_AFFINITY.popitem(last=False)


def _load_experiment_affinity(request: Any) -> dict[str, Any] | None:
    _prune_experiment_affinity()
    key = _experiment_affinity_key(request)
    if not key:
        return None
    value = _EXPERIMENT_AFFINITY.get(key)
    if value is None:
        return None
    _EXPERIMENT_AFFINITY.move_to_end(key)
    return dict(value)


def _store_experiment_affinity(*, request: Any, metadata: dict[str, Any]) -> None:
    key = _experiment_affinity_key(request)
    if not key:
        return
    record = {
        'slice': metadata.get('slice'),
        'engine': metadata.get('engine'),
        'bucket': metadata.get('bucket'),
        'rollout_percent': metadata.get('rollout_percent'),
        'timestamp': monotonic(),
    }
    _EXPERIMENT_AFFINITY[key] = record
    _EXPERIMENT_AFFINITY.move_to_end(key)
    _prune_experiment_affinity()


def _stable_rollout_bucket(*, request: Any, slice_name: str) -> int:
    conversation_id = str(getattr(request, 'conversation_id', '') or '')
    telegram_chat_id = str(getattr(request, 'telegram_chat_id', '') or '')
    message = str(getattr(request, 'message', '') or '')
    seed = f'{slice_name}|{conversation_id}|{telegram_chat_id}|{message[:64]}'
    digest = hashlib.sha256(seed.encode('utf-8')).hexdigest()
    return int(digest[:8], 16) % 100


def _request_matches_allowlist(*, request: Any, settings: Any, slice_name: str) -> bool:
    chat_allowlist = _parse_csv_items(getattr(settings, 'orchestrator_experiment_telegram_chat_allowlist', ''))
    conversation_allowlist = _parse_csv_items(getattr(settings, 'orchestrator_experiment_conversation_allowlist', ''))
    allowlist_scoped_slices = _parse_csv_items(getattr(settings, 'orchestrator_experiment_allowlist_slices', ''))
    if allowlist_scoped_slices and slice_name not in allowlist_scoped_slices:
        return True
    if not chat_allowlist and not conversation_allowlist:
        return True
    chat_id = str(getattr(request, 'telegram_chat_id', '') or '')
    conversation_id = str(getattr(request, 'conversation_id', '') or '')
    return (chat_id and chat_id in chat_allowlist) or (conversation_id and conversation_id in conversation_allowlist)


def _rollout_percent_for_slice(*, settings: Any, slice_name: str) -> int:
    per_slice = _parse_slice_rollouts(getattr(settings, 'orchestrator_experiment_slice_rollouts', ''))
    if slice_name in per_slice:
        return per_slice[slice_name]
    return max(0, min(100, int(getattr(settings, 'orchestrator_experiment_rollout_percent', 0) or 0)))


def _should_reuse_affinity(*, request: Any, inferred_slice: str, affinity_slice: str) -> bool:
    if affinity_slice == inferred_slice:
        return True
    message = str(getattr(request, 'message', '') or '').strip().lower()
    if affinity_slice == 'support':
        followup_terms = (
            'protocolo',
            'status',
            'resume meu atendimento',
            'resume o atendimento',
            'resuma meu atendimento',
            'resuma o atendimento',
            'meu atendimento',
            'meu pedido',
            'cheguei agora',
            'eu cheguei agora',
            'mas eu cheguei agora',
            'acompanhar',
            'acompanha',
            'fila',
            'ticket',
            'atd-',
        )
        if any(term in message for term in followup_terms):
            return True
    if affinity_slice == 'workflow':
        followup_terms = (
            'protocolo',
            'status',
            'remarcar',
            'reagendar',
            'cancelar',
            'quinta',
            'sexta',
            'manha',
            'manhã',
            'tarde',
            'nesse dia',
            'pode ser',
        )
        if any(term in message for term in followup_terms):
            return True
    return False


def _should_route_to_experiment(*, request: Any, settings: Any) -> tuple[bool, dict[str, Any] | None]:
    if not bool(getattr(settings, 'orchestrator_experiment_enabled', False)):
        return False, None
    if str(getattr(settings, 'orchestrator_engine', 'langgraph') or 'langgraph').strip().lower() != 'langgraph':
        return False, None
    if not str(getattr(settings, 'crewai_pilot_url', '') or '').strip():
        return False, None
    inferred_slice = infer_request_slice(request)
    configured_slices = _parse_csv_items(getattr(settings, 'orchestrator_experiment_slices', ''))
    affinity = _load_experiment_affinity(request)
    slice_name = inferred_slice
    selection_source = 'inference'
    if (
        affinity
        and str(affinity.get('slice', '') or '')
        and str(affinity.get('slice', '') or '') != inferred_slice
        and (not configured_slices or str(affinity.get('slice', '') or '') in configured_slices)
        and _should_reuse_affinity(
            request=request,
            inferred_slice=inferred_slice,
            affinity_slice=str(affinity.get('slice', '') or ''),
        )
    ):
        slice_name = str(affinity.get('slice', '') or inferred_slice)
        selection_source = 'affinity'
    if configured_slices and slice_name not in configured_slices:
        if not (
            affinity
            and str(affinity.get('slice', '') or '') in configured_slices
            and _should_reuse_affinity(
                request=request,
                inferred_slice=inferred_slice,
                affinity_slice=str(affinity.get('slice', '') or ''),
            )
        ):
            return False, None
        slice_name = str(affinity.get('slice', '') or inferred_slice)
        selection_source = 'affinity'
    if not _request_matches_allowlist(request=request, settings=settings, slice_name=slice_name):
        return False, None
    rollout_percent = _rollout_percent_for_slice(settings=settings, slice_name=slice_name)
    if rollout_percent <= 0:
        return False, None
    if (
        affinity
        and str(affinity.get('slice', '') or '') == slice_name
        and _should_reuse_affinity(
            request=request,
            inferred_slice=inferred_slice,
            affinity_slice=slice_name,
        )
    ):
        bucket = int(affinity.get('bucket', 0) or 0)
        enrolled = bucket < rollout_percent
        selection_source = 'affinity'
    else:
        bucket = _stable_rollout_bucket(request=request, slice_name=slice_name)
        enrolled = bucket < rollout_percent
    metadata = {
        'slice': slice_name,
        'inferred_slice': inferred_slice,
        'bucket': bucket,
        'rollout_percent': rollout_percent,
        'engine': str(getattr(settings, 'orchestrator_experiment_primary_engine', 'crewai') or 'crewai'),
        'enrolled': enrolled,
        'selection_source': selection_source,
    }
    if enrolled:
        _store_experiment_affinity(request=request, metadata=metadata)
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
