from __future__ import annotations

import hashlib
import json
import logging
from collections import OrderedDict
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from threading import Lock
from time import monotonic
from typing import Any
from urllib.error import URLError
from urllib.request import Request, urlopen

from .engines.base import ResponseEngine, ShadowRunResult
from .engines.langgraph_engine import LangGraphEngine
from .engines.llamaindex_workflow_engine import LlamaIndexWorkflowEngine
from .engines.python_functions_engine import PythonFunctionsEngine
from .engines.specialist_supervisor_engine import SpecialistSupervisorEngine
from .slice_inference import infer_request_slice

logger = logging.getLogger(__name__)
_REPO_ROOT = Path(__file__).resolve().parents[4]

_EXPERIMENT_AFFINITY: OrderedDict[str, dict[str, Any]] = OrderedDict()
_EXPERIMENT_AFFINITY_LIMIT = 2048
_EXPERIMENT_AFFINITY_TTL_SECONDS = 60 * 60 * 6
_REMOTE_STATUS_CACHE: dict[str, dict[str, Any]] = {}
_RUNTIME_PRIMARY_STACK_OVERRIDE: dict[str, Any] = {
    'value': None,
    'reason': None,
    'operator': None,
    'updated_at': None,
}
_RUNTIME_PRIMARY_STACK_LOCK = Lock()
_RUNTIME_TARGETED_STACK_OVERRIDE: dict[str, Any] = {
    'value': None,
    'reason': None,
    'operator': None,
    'updated_at': None,
    'ttl_seconds': None,
    'expires_at': None,
    'slices': [],
    'telegram_chat_allowlist': [],
    'conversation_allowlist': [],
}
_RUNTIME_TARGETED_STACK_LOCK = Lock()
SUPPORTED_PRIMARY_STACKS = {'langgraph', 'python_functions', 'llamaindex', 'specialist_supervisor'}


@dataclass(frozen=True)
class EngineBundle:
    mode: str
    primary: ResponseEngine
    shadow: ResponseEngine | None = None
    experiment: dict[str, Any] | None = None


@dataclass(frozen=True)
class StackSelection:
    stack: str
    mode: str
    experiment: dict[str, Any] | None = None


def _probe_remote_status_payload(
    *,
    name: str,
    url: str | None,
    token: str,
    ttl_seconds: int,
    timeout_seconds: float = 3.0,
) -> dict[str, Any] | None:
    normalized_url = str(url or '').strip()
    if not normalized_url:
        return None
    cache_key = f'{name}:{normalized_url}'
    now = monotonic()
    cached = _REMOTE_STATUS_CACHE.get(cache_key) or {}
    cached_timestamp = float(cached.get('timestamp', 0.0) or 0.0)
    if cached and now - cached_timestamp < max(1, ttl_seconds):
        payload = cached.get('payload')
        return dict(payload) if isinstance(payload, dict) else None

    payload: dict[str, Any] | None = None
    request = Request(
        f'{normalized_url.rstrip("/")}/v1/status',
        headers={'X-Internal-Api-Token': token},
    )
    try:
        with urlopen(request, timeout=timeout_seconds) as response:
            if response.status == 200:
                loaded = json.load(response)
                if isinstance(loaded, dict):
                    payload = loaded
    except URLError:
        payload = None
    except Exception:
        logger.exception('remote_status_probe_failed', extra={'target': name, 'url': normalized_url})
        payload = None

    _REMOTE_STATUS_CACHE[cache_key] = {
        'timestamp': now,
        'payload': payload,
    }
    return dict(payload) if isinstance(payload, dict) else None


def _normalized_primary_stack(value: str | None) -> str | None:
    normalized = str(value or '').strip().lower()
    if not normalized:
        return None
    if normalized not in SUPPORTED_PRIMARY_STACKS:
        raise ValueError(f'unsupported_primary_stack:{normalized}')
    return normalized


def get_runtime_primary_stack_override() -> dict[str, Any]:
    with _RUNTIME_PRIMARY_STACK_LOCK:
        return dict(_RUNTIME_PRIMARY_STACK_OVERRIDE)


def set_runtime_primary_stack_override(
    *,
    stack: str | None,
    reason: str | None = None,
    operator: str | None = None,
) -> dict[str, Any]:
    normalized_stack = _normalized_primary_stack(stack)
    with _RUNTIME_PRIMARY_STACK_LOCK:
        if normalized_stack is None:
            _RUNTIME_PRIMARY_STACK_OVERRIDE.update(
                {
                    'value': None,
                    'reason': reason or None,
                    'operator': operator or None,
                    'updated_at': datetime.now(timezone.utc).isoformat(),
                }
            )
        else:
            _RUNTIME_PRIMARY_STACK_OVERRIDE.update(
                {
                    'value': normalized_stack,
                    'reason': reason or None,
                    'operator': operator or None,
                    'updated_at': datetime.now(timezone.utc).isoformat(),
                }
            )
        return dict(_RUNTIME_PRIMARY_STACK_OVERRIDE)


def clear_runtime_primary_stack_override(
    *,
    reason: str | None = None,
    operator: str | None = None,
) -> dict[str, Any]:
    return set_runtime_primary_stack_override(
        stack=None,
        reason=reason,
        operator=operator,
    )


def get_runtime_targeted_stack_override() -> dict[str, Any]:
    with _RUNTIME_TARGETED_STACK_LOCK:
        expires_at_raw = str(_RUNTIME_TARGETED_STACK_OVERRIDE.get('expires_at') or '').strip()
        if _RUNTIME_TARGETED_STACK_OVERRIDE.get('value') and expires_at_raw:
            try:
                expires_at = datetime.fromisoformat(expires_at_raw)
            except ValueError:
                expires_at = None
            if expires_at is not None and expires_at <= datetime.now(timezone.utc):
                _RUNTIME_TARGETED_STACK_OVERRIDE.update(
                    {
                        'value': None,
                        'reason': 'expired_runtime_targeted_stack_override',
                        'operator': 'system',
                        'updated_at': datetime.now(timezone.utc).isoformat(),
                        'ttl_seconds': None,
                        'expires_at': None,
                        'slices': [],
                        'telegram_chat_allowlist': [],
                        'conversation_allowlist': [],
                    }
                )
        return dict(_RUNTIME_TARGETED_STACK_OVERRIDE)


def set_runtime_targeted_stack_override(
    *,
    stack: str | None,
    reason: str | None = None,
    operator: str | None = None,
    ttl_seconds: int | None = None,
    slices: list[str] | None = None,
    telegram_chat_allowlist: list[str] | None = None,
    conversation_allowlist: list[str] | None = None,
) -> dict[str, Any]:
    normalized_stack = _normalized_primary_stack(stack)
    normalized_ttl_seconds: int | None = None
    if ttl_seconds is not None:
        normalized_ttl_seconds = int(ttl_seconds)
        if normalized_ttl_seconds <= 0:
            normalized_ttl_seconds = None
    with _RUNTIME_TARGETED_STACK_LOCK:
        if normalized_stack is None:
            _RUNTIME_TARGETED_STACK_OVERRIDE.update(
                {
                    'value': None,
                    'reason': reason or None,
                    'operator': operator or None,
                    'updated_at': datetime.now(timezone.utc).isoformat(),
                    'ttl_seconds': None,
                    'expires_at': None,
                    'slices': [],
                    'telegram_chat_allowlist': [],
                    'conversation_allowlist': [],
                }
            )
        else:
            updated_at = datetime.now(timezone.utc)
            expires_at = (
                (updated_at + timedelta(seconds=normalized_ttl_seconds)).isoformat()
                if normalized_ttl_seconds
                else None
            )
            _RUNTIME_TARGETED_STACK_OVERRIDE.update(
                {
                    'value': normalized_stack,
                    'reason': reason or None,
                    'operator': operator or None,
                    'updated_at': updated_at.isoformat(),
                    'ttl_seconds': normalized_ttl_seconds,
                    'expires_at': expires_at,
                    'slices': sorted({str(item).strip() for item in (slices or []) if str(item).strip()}),
                    'telegram_chat_allowlist': sorted(
                        {str(item).strip() for item in (telegram_chat_allowlist or []) if str(item).strip()}
                    ),
                    'conversation_allowlist': sorted(
                        {str(item).strip() for item in (conversation_allowlist or []) if str(item).strip()}
                    ),
                }
            )
        return dict(_RUNTIME_TARGETED_STACK_OVERRIDE)


def clear_runtime_targeted_stack_override(
    *,
    reason: str | None = None,
    operator: str | None = None,
) -> dict[str, Any]:
    return set_runtime_targeted_stack_override(
        stack=None,
        reason=reason,
        operator=operator,
    )


def get_primary_stack_resolution(settings: Any) -> dict[str, Any]:
    runtime_override = get_runtime_primary_stack_override()
    runtime_value = _normalized_primary_stack(runtime_override.get('value'))
    feature_flag_value = _normalized_primary_stack(
        getattr(settings, 'feature_flag_primary_orchestration_stack', '') or None
    )
    env_fallback = _normalized_primary_stack(getattr(settings, 'orchestrator_engine', 'langgraph') or 'langgraph') or 'langgraph'
    if runtime_value:
        resolved = runtime_value
        source = 'runtime_override'
    elif feature_flag_value:
        resolved = feature_flag_value
        source = 'feature_flag'
    else:
        resolved = env_fallback
        source = 'orchestrator_engine'
    return {
        'resolved': resolved,
        'source': source,
        'runtime_override': runtime_override,
        'feature_flag': feature_flag_value,
        'orchestrator_engine': env_fallback,
    }


def resolve_primary_stack(settings: Any) -> str:
    return str(get_primary_stack_resolution(settings).get('resolved') or 'langgraph')


def strict_framework_isolation_enabled(settings: Any) -> bool:
    return bool(getattr(settings, 'strict_framework_isolation_enabled', False))


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


def _request_matches_targeted_allowlist(*, request: Any, override: dict[str, Any], slice_name: str) -> bool:
    scoped_slices = {str(item).strip() for item in (override.get('slices') or []) if str(item).strip()}
    if scoped_slices and slice_name not in scoped_slices:
        return False
    chat_allowlist = {str(item).strip() for item in (override.get('telegram_chat_allowlist') or []) if str(item).strip()}
    conversation_allowlist = {
        str(item).strip() for item in (override.get('conversation_allowlist') or []) if str(item).strip()
    }
    if not chat_allowlist and not conversation_allowlist:
        return False
    chat_id = str(getattr(request, 'telegram_chat_id', '') or '').strip()
    conversation_id = str(getattr(request, 'conversation_id', '') or '').strip()
    return (chat_id and chat_id in chat_allowlist) or (conversation_id and conversation_id in conversation_allowlist)


def _allowlist_identifier_counts(*, settings: Any) -> dict[str, int]:
    return {
        'telegram_chat_count': len(_parse_csv_items(getattr(settings, 'orchestrator_experiment_telegram_chat_allowlist', ''))),
        'conversation_count': len(_parse_csv_items(getattr(settings, 'orchestrator_experiment_conversation_allowlist', ''))),
    }


def _rollout_percent_for_slice(*, settings: Any, slice_name: str) -> int:
    per_slice = _parse_slice_rollouts(getattr(settings, 'orchestrator_experiment_slice_rollouts', ''))
    if slice_name in per_slice:
        return per_slice[slice_name]
    return max(0, min(100, int(getattr(settings, 'orchestrator_experiment_rollout_percent', 0) or 0)))


def _load_scorecard(settings: Any) -> dict[str, Any] | None:
    configured_path = str(getattr(settings, 'orchestrator_experiment_scorecard_path', '') or '').strip()
    candidate_paths: list[Path] = []
    if configured_path:
        candidate_paths.append(Path(configured_path))
    for fallback in (
        _REPO_ROOT / 'artifacts' / 'framework-native-scorecard.json',
        _REPO_ROOT / 'docs' / 'architecture' / 'framework-native-scorecard.json',
    ):
        if fallback not in candidate_paths:
            candidate_paths.append(fallback)
    for fallback in (
        '/workspace/artifacts/framework-native-scorecard.json',
        '/workspace/docs/architecture/framework-native-scorecard.json',
    ):
        path = Path(fallback)
        if path not in candidate_paths:
            candidate_paths.append(path)

    for scorecard_path in candidate_paths:
        try:
            if not scorecard_path.exists():
                continue
            payload = json.loads(scorecard_path.read_text(encoding='utf-8'))
        except Exception:
            logger.exception('experiment_scorecard_read_failed', extra={'scorecard_path': str(scorecard_path)})
            continue
        if isinstance(payload, dict):
            return payload
    return None


def get_scorecard_gate_status(*, settings: Any, primary_engine: str | None = None) -> dict[str, Any]:
    selected_engine = str(primary_engine or resolve_primary_stack(settings)).strip().lower() or 'langgraph'
    scorecard = _load_scorecard(settings)
    if not isinstance(scorecard, dict):
        return {
            'loaded': False,
            'primary_engine': selected_engine,
            'primary_score': None,
            'primary_max_score': None,
            'primary_stack_native_path_passed': False,
            'promotion_gate': None,
        }

    frameworks = scorecard.get('frameworks')
    framework_payload = frameworks.get(selected_engine) if isinstance(frameworks, dict) else None
    promotion_gate = scorecard.get('promotion_gate')
    engine_gate = promotion_gate.get(selected_engine) if isinstance(promotion_gate, dict) else None

    return {
        'loaded': True,
        'generated_at': scorecard.get('generated_at'),
        'primary_engine': selected_engine,
        'primary_score': framework_payload.get('total_score') if isinstance(framework_payload, dict) else None,
        'primary_max_score': framework_payload.get('max_score') if isinstance(framework_payload, dict) else None,
        'primary_stack_native_path_passed': bool(isinstance(framework_payload, dict) and framework_payload.get('primary_stack_native_path_passed')),
        'promotion_gate': engine_gate if isinstance(engine_gate, dict) else None,
        'frameworks': frameworks if isinstance(frameworks, dict) else None,
    }


def get_experiment_rollout_readiness(*, settings: Any) -> dict[str, Any]:
    candidate_engine = str(getattr(settings, 'orchestrator_experiment_primary_engine', 'python_functions') or 'python_functions').strip().lower()
    if candidate_engine not in SUPPORTED_PRIMARY_STACKS:
        candidate_engine = 'python_functions'
    configured_slices = sorted(_parse_csv_items(getattr(settings, 'orchestrator_experiment_slices', '')))
    allowlist_scoped_slices = sorted(_parse_csv_items(getattr(settings, 'orchestrator_experiment_allowlist_slices', '')))
    gate_status = get_scorecard_gate_status(settings=settings, primary_engine=candidate_engine)
    promotion_gate = gate_status.get('promotion_gate') if isinstance(gate_status, dict) else None
    slice_eligibility = promotion_gate.get('slice_eligibility') if isinstance(promotion_gate, dict) else None
    if not isinstance(slice_eligibility, dict):
        slice_eligibility = {}
    pilot_status = None
    pilot_ready = True
    if candidate_engine == 'specialist_supervisor':
        pilot_status = _probe_remote_status_payload(
            name='specialist_supervisor',
            url=str(getattr(settings, 'specialist_supervisor_pilot_url', '') or '').strip(),
            token=str(getattr(settings, 'internal_api_token', '') or ''),
            ttl_seconds=max(1, int(getattr(settings, 'orchestrator_experiment_health_ttl_seconds', 15) or 15)),
            timeout_seconds=4.0,
        )
        pilot_ready = bool(isinstance(pilot_status, dict) and pilot_status.get('ready'))
    allowlist_counts = _allowlist_identifier_counts(settings=settings)

    known_slices = {'public', 'protected', 'support', 'workflow'}
    known_slices.update(str(item).strip() for item in configured_slices if str(item).strip())
    known_slices.update(str(item).strip() for item in slice_eligibility.keys() if str(item).strip())

    per_slice: dict[str, Any] = {}
    promotable_now: list[str] = []
    blocked_now: dict[str, str] = {}
    currently_enrolled: list[str] = []

    for slice_name in sorted(known_slices):
        eligibility = slice_eligibility.get(slice_name) if isinstance(slice_eligibility.get(slice_name), dict) else {}
        scorecard_eligible = bool(eligibility.get('eligible', False))
        reason = str(eligibility.get('reason', '') or '').strip()
        pilot_live_gate_ok = True if candidate_engine != 'specialist_supervisor' else pilot_ready
        pilot_live_gate_reason = '' if pilot_live_gate_ok else 'Specialist Supervisor pilot is not healthy right now.'
        eligible = scorecard_eligible and pilot_live_gate_ok
        effective_reason = reason
        if scorecard_eligible and not pilot_live_gate_ok:
            effective_reason = pilot_live_gate_reason or 'Slice is blocked by the current live pilot gate.'
        enrolled = slice_name in configured_slices
        rollout_percent = _rollout_percent_for_slice(settings=settings, slice_name=slice_name)
        allowlist_only = slice_name in allowlist_scoped_slices
        live = enrolled and rollout_percent > 0
        per_slice[slice_name] = {
            'eligible': eligible,
            'reason': effective_reason,
            'scorecard_eligible': scorecard_eligible,
            'pilot_live_gate_ok': pilot_live_gate_ok,
            'pilot_live_gate_reason': pilot_live_gate_reason,
            'configured': enrolled,
            'configured_rollout_percent': rollout_percent,
            'allowlist_only': allowlist_only,
            'live': live,
        }
        if eligible:
            promotable_now.append(slice_name)
        else:
            blocked_now[slice_name] = effective_reason or f'{slice_name} is not eligible under the current scorecard gate.'
        if enrolled:
            currently_enrolled.append(slice_name)

    recommended_next_promotions = [
        slice_name
        for slice_name in promotable_now
        if not per_slice.get(slice_name, {}).get('live')
    ]

    return {
        'candidate_engine': candidate_engine,
        'scorecard_loaded': bool(gate_status.get('loaded')),
        'scorecard_enforced': bool(getattr(settings, 'orchestrator_experiment_require_scorecard', False)),
        'pilot_health_enforced': bool(getattr(settings, 'orchestrator_experiment_require_healthy_pilot', False)),
        'pilot_ready': pilot_ready,
        'pilot_status': pilot_status if isinstance(pilot_status, dict) else None,
        'allowlist_identifier_counts': allowlist_counts,
        'primary_stack_native_path_passed': bool(gate_status.get('primary_stack_native_path_passed')),
        'gate_eligible': bool(isinstance(promotion_gate, dict) and promotion_gate.get('eligible', False)),
        'configured_slices': currently_enrolled,
        'promotable_now': promotable_now,
        'blocked_now': blocked_now,
        'recommended_next_promotions': recommended_next_promotions,
        'per_slice': per_slice,
    }


def get_experiment_live_promotion_summary(*, settings: Any) -> dict[str, Any]:
    resolved_primary_stack = resolve_primary_stack(settings)
    candidate_engine = str(getattr(settings, 'orchestrator_experiment_primary_engine', 'python_functions') or 'python_functions').strip().lower()
    if candidate_engine not in SUPPORTED_PRIMARY_STACKS:
        candidate_engine = 'python_functions'
    readiness = get_experiment_rollout_readiness(settings=settings)
    experiment_enabled = bool(getattr(settings, 'orchestrator_experiment_enabled', False))
    pilot_url = str(getattr(settings, 'specialist_supervisor_pilot_url', '') or '').strip() if candidate_engine == 'specialist_supervisor' else ''
    pilot_configured = bool(pilot_url)
    pilot_status = readiness.get('pilot_status') if isinstance(readiness, dict) else None
    if candidate_engine == 'specialist_supervisor' and pilot_configured and not isinstance(pilot_status, dict):
        pilot_status = _probe_remote_status_payload(
            name='specialist_supervisor',
            url=pilot_url,
            token=str(getattr(settings, 'internal_api_token', '') or ''),
            ttl_seconds=max(1, int(getattr(settings, 'orchestrator_experiment_health_ttl_seconds', 15) or 15)),
            timeout_seconds=4.0,
        )
    pilot_ready = bool(isinstance(pilot_status, dict) and pilot_status.get('ready'))

    experiment_active = experiment_enabled and resolved_primary_stack == 'langgraph'

    advisory_by_slice: dict[str, Any] = {}
    promotable_now: list[str] = []
    blocked_now: dict[str, str] = {}
    maintain_now: list[str] = []

    per_slice = readiness.get('per_slice')
    if not isinstance(per_slice, dict):
        per_slice = {}

    for slice_name, payload in sorted(per_slice.items()):
        if not isinstance(payload, dict):
            continue
        eligible = bool(payload.get('eligible', False))
        configured = bool(payload.get('configured', False))
        live = bool(payload.get('live', False))
        rollout_percent = int(payload.get('configured_rollout_percent', 0) or 0)
        allowlist_only = bool(payload.get('allowlist_only', False))
        reason = str(payload.get('reason', '') or '').strip()
        pilot_live_gate_ok = bool(payload.get('pilot_live_gate_ok', True))
        pilot_live_gate_reason = str(payload.get('pilot_live_gate_reason', '') or '').strip()

        blocked_reasons: list[str] = []
        action = 'blocked'
        if not eligible:
            blocked_reasons.append(reason or 'Slice is not eligible under the current scorecard gate.')
        if not experiment_enabled:
            blocked_reasons.append('Experiment is disabled in runtime settings.')
        if resolved_primary_stack != 'langgraph':
            blocked_reasons.append('Live experiment routing only applies while LangGraph remains the resolved primary stack.')
        if candidate_engine == 'specialist_supervisor' and not pilot_configured:
            blocked_reasons.append('Specialist Supervisor pilot URL is not configured.')
        if candidate_engine == 'specialist_supervisor' and pilot_configured and not pilot_ready:
            blocked_reasons.append('Specialist Supervisor pilot is not healthy right now.')
        if candidate_engine == 'specialist_supervisor' and pilot_ready and not pilot_live_gate_ok:
            live_gate_reason = pilot_live_gate_reason or 'Specialist Supervisor pilot live gate is not open for this slice.'
            if live_gate_reason not in blocked_reasons:
                blocked_reasons.append(live_gate_reason)
        if blocked_reasons:
            blocked_reasons = list(dict.fromkeys(blocked_reasons))

        if blocked_reasons:
            action = 'blocked'
        elif live:
            if allowlist_only:
                action = 'maintain_controlled'
            elif rollout_percent < 100:
                action = 'expand_gradually'
            else:
                action = 'maintain_live'
        elif configured and rollout_percent <= 0:
            action = 'activate_configured_slice'
        elif eligible and not configured:
            action = 'start_controlled_canary' if slice_name in {'support', 'workflow'} else 'start_tiny_rollout'

        summary = {
            'eligible': eligible,
            'configured': configured,
            'live': live,
            'allowlist_only': allowlist_only,
            'configured_rollout_percent': rollout_percent,
            'action': action,
            'pilot_live_gate_ok': pilot_live_gate_ok,
            'pilot_live_gate_reason': pilot_live_gate_reason,
            'blocked_reasons': blocked_reasons,
        }
        advisory_by_slice[slice_name] = summary

        if action in {'expand_gradually', 'activate_configured_slice', 'start_controlled_canary', 'start_tiny_rollout'}:
            promotable_now.append(slice_name)
        elif action in {'maintain_controlled', 'maintain_live'}:
            maintain_now.append(slice_name)
        elif blocked_reasons:
            blocked_now[slice_name] = '; '.join(blocked_reasons)

    return {
        'resolved_primary_stack': resolved_primary_stack,
        'experiment_enabled': experiment_enabled,
        'experiment_active': experiment_active,
        'candidate_engine': candidate_engine,
        'pilot_configured': pilot_configured,
        'pilot_ready': pilot_ready,
        'pilot_status': pilot_status if isinstance(pilot_status, dict) else None,
        'scorecard_loaded': bool(readiness.get('scorecard_loaded')),
        'primary_stack_native_path_passed': bool(readiness.get('primary_stack_native_path_passed')),
        'promotable_now': promotable_now,
        'maintain_now': maintain_now,
        'blocked_now': blocked_now,
        'advisory_by_slice': advisory_by_slice,
    }


def _slice_allowed_by_scorecard(*, settings: Any, slice_name: str, primary_engine: str) -> bool:
    if not bool(getattr(settings, 'orchestrator_experiment_require_scorecard', False)):
        return True
    scorecard = _load_scorecard(settings)
    if not isinstance(scorecard, dict):
        return False
    frameworks = scorecard.get('frameworks')
    if not isinstance(frameworks, dict):
        return False
    primary_payload = frameworks.get(primary_engine)
    if not isinstance(primary_payload, dict):
        return False
    total_score = int(primary_payload.get('total_score') or 0)
    minimum_score = int(getattr(settings, 'orchestrator_experiment_min_primary_engine_score', 20) or 20)
    if total_score < minimum_score:
        return False
    if not bool(primary_payload.get('primary_stack_native_path_passed', False)):
        return False
    promotion_gate = scorecard.get('promotion_gate')
    if isinstance(promotion_gate, dict):
        engine_gate = promotion_gate.get(primary_engine)
        if isinstance(engine_gate, dict):
            if not bool(engine_gate.get('eligible', False)):
                return False
            if bool(engine_gate.get('primary_stack_native_path_required', False)) and not bool(primary_payload.get('primary_stack_native_path_passed', False)):
                return False
            recommended = engine_gate.get('recommended_canary_slices')
            if isinstance(recommended, list) and recommended:
                return slice_name in {str(item).strip() for item in recommended if str(item).strip()}
    recommended = primary_payload.get('recommended_canary_slices')
    if isinstance(recommended, list) and recommended:
        return slice_name in {str(item).strip() for item in recommended if str(item).strip()}
    return False


def _probe_pilot_health(*, settings: Any) -> bool:
    candidate_engine = str(getattr(settings, 'orchestrator_experiment_primary_engine', 'python_functions') or 'python_functions').strip().lower()
    if candidate_engine != 'specialist_supervisor':
        return True
    payload = _probe_remote_status_payload(
        name='specialist_supervisor',
        url=str(getattr(settings, 'specialist_supervisor_pilot_url', '') or '').strip(),
        token=str(getattr(settings, 'internal_api_token', '') or ''),
        ttl_seconds=max(1, int(getattr(settings, 'orchestrator_experiment_health_ttl_seconds', 15) or 15)),
        timeout_seconds=4.0,
    )
    return bool(isinstance(payload, dict) and payload.get('ready'))


def _pilot_ready(*, settings: Any) -> bool:
    if not bool(getattr(settings, 'orchestrator_experiment_require_healthy_pilot', False)):
        return True
    return _probe_pilot_health(settings=settings)


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
    if strict_framework_isolation_enabled(settings):
        return False, None
    if not bool(getattr(settings, 'orchestrator_experiment_enabled', False)):
        return False, None
    if resolve_primary_stack(settings) != 'langgraph':
        return False, None
    candidate_engine = str(getattr(settings, 'orchestrator_experiment_primary_engine', 'python_functions') or 'python_functions').strip().lower()
    if candidate_engine not in SUPPORTED_PRIMARY_STACKS or candidate_engine == 'langgraph':
        return False, None
    if candidate_engine == 'specialist_supervisor' and not str(getattr(settings, 'specialist_supervisor_pilot_url', '') or '').strip():
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
        'engine': candidate_engine,
        'enrolled': enrolled,
        'selection_source': selection_source,
    }
    if not _slice_allowed_by_scorecard(
        settings=settings,
        slice_name=slice_name,
        primary_engine=str(metadata['engine']),
    ):
        return False, None
    if candidate_engine == 'specialist_supervisor':
        specialist_ready = bool(
            isinstance(
                _probe_remote_status_payload(
                    name='specialist_supervisor',
                    url=str(getattr(settings, 'specialist_supervisor_pilot_url', '') or '').strip(),
                    token=str(getattr(settings, 'internal_api_token', '') or ''),
                    ttl_seconds=max(1, int(getattr(settings, 'orchestrator_experiment_health_ttl_seconds', 15) or 15)),
                    timeout_seconds=4.0,
                ),
                dict,
            )
        )
        if not specialist_ready:
            return False, None
    if not _pilot_ready(settings=settings):
        return False, None
    if enrolled:
        _store_experiment_affinity(request=request, metadata=metadata)
    return enrolled, metadata


def _targeted_runtime_stack_for_request(*, request: Any) -> dict[str, Any] | None:
    override = get_runtime_targeted_stack_override()
    stack_value = _normalized_primary_stack(override.get('value'))
    if not stack_value:
        return None
    slice_name = infer_request_slice(request)
    if not _request_matches_targeted_allowlist(request=request, override=override, slice_name=slice_name):
        return None
    return {
        'stack': stack_value,
        'slice': slice_name,
        'reason': str(override.get('reason') or ''),
        'operator': str(override.get('operator') or ''),
        'updated_at': str(override.get('updated_at') or ''),
        'slices': list(override.get('slices') or []),
        'telegram_chat_allowlist': list(override.get('telegram_chat_allowlist') or []),
        'conversation_allowlist': list(override.get('conversation_allowlist') or []),
    }


def build_engine_bundle(settings: Any, request: Any | None = None) -> EngineBundle:
    selection = resolve_stack_selection(settings=settings, request=request)
    mode = selection.stack
    langgraph_engine = LangGraphEngine()
    python_functions_engine = PythonFunctionsEngine()
    llamaindex_engine = LlamaIndexWorkflowEngine()
    specialist_supervisor_engine = SpecialistSupervisorEngine()
    if mode == 'python_functions':
        return EngineBundle(mode=selection.mode, primary=python_functions_engine, experiment=selection.experiment)
    if mode == 'llamaindex':
        return EngineBundle(mode=selection.mode, primary=llamaindex_engine, experiment=selection.experiment)
    if mode == 'specialist_supervisor':
        return EngineBundle(mode=selection.mode, primary=specialist_supervisor_engine, experiment=selection.experiment)
    return EngineBundle(mode=selection.mode, primary=langgraph_engine, experiment=selection.experiment)


def resolve_stack_selection(settings: Any, request: Any | None = None) -> StackSelection:
    mode = resolve_primary_stack(settings)
    strict_mode = strict_framework_isolation_enabled(settings)

    if request is not None and not get_runtime_primary_stack_override().get('value'):
        targeted = _targeted_runtime_stack_for_request(request=request)
        if targeted is not None:
            targeted_stack = str(targeted['stack'] or 'langgraph')
            return StackSelection(
                stack=targeted_stack,
                mode=f"targeted:{targeted['slice']}:{targeted_stack}",
                experiment=targeted,
            )

    if request is not None and not strict_mode:
        should_experiment, experiment = _should_route_to_experiment(request=request, settings=settings)
        if should_experiment and experiment is not None:
            experiment_engine = str(experiment.get('engine') or 'python_functions')
            return StackSelection(
                stack=experiment_engine,
                mode=f"experiment:{experiment['slice']}:{experiment_engine}",
                experiment=experiment,
            )

    return StackSelection(stack=mode, mode=mode, experiment=None)


async def maybe_run_shadow(*, bundle: EngineBundle, request: Any, settings: Any) -> ShadowRunResult | None:
    return None
