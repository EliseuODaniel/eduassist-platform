from __future__ import annotations

from ai_orchestrator.serving_telemetry import (
    get_stack_telemetry_snapshot,
    record_stack_outcome,
    reset_stack_telemetry,
)


def setup_function() -> None:
    reset_stack_telemetry()


def test_stack_telemetry_aggregates_recent_latency_and_failures() -> None:
    record_stack_outcome(stack_name='llamaindex', latency_ms=100.0, success=True, cache_hit=False, used_llm=False)
    record_stack_outcome(stack_name='llamaindex', latency_ms=200.0, success=False, timeout=True, cache_hit=False, used_llm=True)
    record_stack_outcome(stack_name='llamaindex', latency_ms=300.0, success=True, cache_hit=True, used_llm=True)

    snapshot = get_stack_telemetry_snapshot('llamaindex')
    assert snapshot.recent_request_count == 3
    assert snapshot.recent_p95_latency_ms >= 200.0
    assert snapshot.recent_timeout_rate > 0.0
    assert snapshot.recent_error_rate > 0.0
    assert snapshot.recent_cache_hit_rate > 0.0
    assert snapshot.recent_used_llm_rate > 0.0
