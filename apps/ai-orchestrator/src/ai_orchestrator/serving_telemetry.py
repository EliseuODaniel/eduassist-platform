from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from statistics import quantiles

_STACK_HISTORY: dict[str, deque[dict[str, float | bool | str]]] = {}
_MAX_HISTORY = 64


@dataclass(frozen=True)
class StackTelemetrySnapshot:
    recent_request_count: int = 0
    recent_p95_latency_ms: float = 0.0
    recent_timeout_rate: float = 0.0
    recent_error_rate: float = 0.0
    recent_cache_hit_rate: float = 0.0
    recent_used_llm_rate: float = 0.0


def reset_stack_telemetry() -> None:
    _STACK_HISTORY.clear()


def record_stack_outcome(
    *,
    stack_name: str,
    latency_ms: float,
    success: bool,
    timeout: bool = False,
    cache_hit: bool = False,
    used_llm: bool = False,
    candidate_kind: str | None = None,
) -> None:
    normalized_stack = str(stack_name or "").strip().lower()
    if not normalized_stack:
        return
    history = _STACK_HISTORY.setdefault(normalized_stack, deque(maxlen=_MAX_HISTORY))
    history.append(
        {
            "latency_ms": max(0.0, float(latency_ms or 0.0)),
            "success": bool(success),
            "timeout": bool(timeout),
            "cache_hit": bool(cache_hit),
            "used_llm": bool(used_llm),
            "candidate_kind": str(candidate_kind or ""),
        }
    )


def get_stack_telemetry_snapshot(stack_name: str) -> StackTelemetrySnapshot:
    normalized_stack = str(stack_name or "").strip().lower()
    history = list(_STACK_HISTORY.get(normalized_stack, ()))
    if not history:
        return StackTelemetrySnapshot()
    latencies = [float(item.get("latency_ms", 0.0) or 0.0) for item in history]
    if len(latencies) >= 2:
        try:
            recent_p95_latency_ms = float(quantiles(latencies, n=100, method="inclusive")[94])
        except Exception:
            recent_p95_latency_ms = max(latencies)
    else:
        recent_p95_latency_ms = latencies[0]
    count = len(history)
    return StackTelemetrySnapshot(
        recent_request_count=count,
        recent_p95_latency_ms=recent_p95_latency_ms,
        recent_timeout_rate=sum(1 for item in history if item.get("timeout")) / count,
        recent_error_rate=sum(1 for item in history if not item.get("success")) / count,
        recent_cache_hit_rate=sum(1 for item in history if item.get("cache_hit")) / count,
        recent_used_llm_rate=sum(1 for item in history if item.get("used_llm")) / count,
    )
