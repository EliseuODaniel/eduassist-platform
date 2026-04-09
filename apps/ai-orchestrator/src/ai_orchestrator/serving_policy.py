from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .models import MessageResponseRequest
from .retrieval_aware_router import EvidenceProbe


@dataclass(frozen=True)
class LoadSnapshot:
    llm_forced_mode: bool = False
    specialist_pilot_circuit_open: bool = False
    specialist_recent_failures: int = 0
    llamaindex_expensive_mode: bool = False
    recent_request_count: int = 0
    recent_p95_latency_ms: float = 0.0
    recent_timeout_rate: float = 0.0
    recent_error_rate: float = 0.0
    recent_cache_hit_rate: float = 0.0
    recent_used_llm_rate: float = 0.0


@dataclass(frozen=True)
class ServingDecision:
    allow_documentary_synthesis: bool
    allow_premium_candidate: bool
    prefer_low_latency: bool
    prefer_cache: bool
    prefer_deterministic: bool
    documentary_cost_penalty: float
    premium_cost_penalty: float
    reason: str


def build_public_serving_policy(
    *,
    settings: Any,
    stack_name: str,
    request: MessageResponseRequest,
    probe: EvidenceProbe,
    load_snapshot: LoadSnapshot,
) -> ServingDecision:
    normalized_stack = str(stack_name or "").strip().lower()
    llm_forced_mode = load_snapshot.llm_forced_mode
    prefer_cache = bool(getattr(settings, "public_response_cache_enabled", True)) and not llm_forced_mode
    prefer_low_latency = normalized_stack in {"python_functions", "specialist_supervisor"} and not llm_forced_mode
    prefer_deterministic = bool(
        probe.canonical_lane and probe.bundle_confidence >= 0.6 and not llm_forced_mode
    )
    allow_documentary_synthesis = bool(
        llm_forced_mode
        or probe.summary_store_hits >= 1
        or probe.document_group_count >= 2
        or probe.section_diversity >= 2
        or probe.topic in {"extended_day_ecosystem", "governance_channels", "health_reorganization"}
    )
    documentary_cost_penalty = 0.0
    premium_cost_penalty = 1.4
    allow_premium_candidate = normalized_stack == "specialist_supervisor"

    if normalized_stack == "llamaindex":
        documentary_cost_penalty = 1.0 if probe.summary_store_hits == 0 and probe.document_group_count < 2 else 0.2
        if load_snapshot.recent_p95_latency_ms >= 4000.0 or load_snapshot.recent_timeout_rate >= 0.15:
            documentary_cost_penalty += 1.2
            prefer_deterministic = prefer_deterministic or not llm_forced_mode
            allow_documentary_synthesis = allow_documentary_synthesis and (
                llm_forced_mode or probe.summary_store_hits >= 1 or probe.topic_match_score >= 0.4
            )
    elif normalized_stack == "langgraph":
        documentary_cost_penalty = 0.3 if allow_documentary_synthesis else 1.0
        if load_snapshot.recent_p95_latency_ms >= 2500.0:
            documentary_cost_penalty += 0.4
    elif normalized_stack == "python_functions":
        documentary_cost_penalty = 0.4 if allow_documentary_synthesis else 1.2
        if load_snapshot.recent_p95_latency_ms >= 2500.0:
            documentary_cost_penalty += 0.5
    elif normalized_stack == "specialist_supervisor":
        documentary_cost_penalty = 0.2
        if load_snapshot.specialist_pilot_circuit_open or load_snapshot.specialist_recent_failures > 0:
            allow_premium_candidate = False
            premium_cost_penalty = 6.0
        else:
            premium_cost_penalty = 2.5
        if load_snapshot.recent_timeout_rate >= 0.1 or load_snapshot.recent_error_rate >= 0.1:
            allow_premium_candidate = False
            premium_cost_penalty = max(premium_cost_penalty, 6.0)

    if load_snapshot.recent_cache_hit_rate >= 0.2 and not llm_forced_mode:
        prefer_cache = True

    reason_parts = []
    if prefer_deterministic:
        reason_parts.append("prefer_deterministic")
    if allow_documentary_synthesis:
        reason_parts.append("allow_documentary")
    if prefer_cache:
        reason_parts.append("prefer_cache")
    if not allow_premium_candidate:
        reason_parts.append("premium_blocked")
    if load_snapshot.recent_request_count:
        reason_parts.append(
            f"telemetry:p95={load_snapshot.recent_p95_latency_ms:.0f}/timeout={load_snapshot.recent_timeout_rate:.2f}/error={load_snapshot.recent_error_rate:.2f}"
        )
    return ServingDecision(
        allow_documentary_synthesis=allow_documentary_synthesis,
        allow_premium_candidate=allow_premium_candidate,
        prefer_low_latency=prefer_low_latency,
        prefer_cache=prefer_cache,
        prefer_deterministic=prefer_deterministic,
        documentary_cost_penalty=documentary_cost_penalty,
        premium_cost_penalty=premium_cost_penalty,
        reason=",".join(reason_parts) or "default_serving_policy",
    )
