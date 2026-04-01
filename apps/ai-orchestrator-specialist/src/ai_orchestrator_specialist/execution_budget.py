from __future__ import annotations

import re
import unicodedata
from typing import Any

from .models import ExecutionBudget, SupervisorPlan


def _normalize_text(value: str | None) -> str:
    text = unicodedata.normalize("NFKD", str(value or ""))
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    return re.sub(r"\s+", " ", text.strip().lower())


def _has_any(normalized: str, markers: set[str]) -> bool:
    return any(marker in normalized for marker in markers)


def derive_execution_budget(ctx: Any, plan: SupervisorPlan) -> ExecutionBudget:
    normalized = _normalize_text(getattr(getattr(ctx, "request", None), "message", ""))
    reasons: list[str] = []
    authenticated = bool(getattr(getattr(ctx, "request", None), "user", None) and ctx.request.user.authenticated)
    is_multi_domain = bool(plan.secondary_domains) or plan.request_kind == "multi_domain"
    premium_markers = {
        "resuma",
        "resumo",
        "sintese",
        "sintese",
        "junto com",
        "alem de",
        "além de",
        "compare",
        "panorama",
        "cruzando",
        "ao mesmo tempo",
    }
    creative_or_summary = _has_any(normalized, premium_markers)

    if plan.should_deny or plan.requires_clarification:
        reasons.append("clarify_or_deny")
        return ExecutionBudget(
            tier="cheap",
            planner_mode="deterministic",
            target_latency_ms=500,
            max_specialists=0,
            allow_parallel_specialists=False,
            allow_manager=False,
            allow_judge=False,
            allow_repair=False,
            allow_session_memory=False,
            prefer_direct_answer=True,
            specialist_max_turns=2,
            manager_max_turns=2,
            judge_max_turns=1,
            repair_max_turns=1,
            reasons=reasons,
        )

    if is_multi_domain or plan.request_kind in {"complex", "ambiguous", "sensitive"}:
        reasons.append("multi_or_sensitive")
        if creative_or_summary:
            reasons.append("summary_or_composition")
        return ExecutionBudget(
            tier="premium",
            planner_mode="adaptive",
            target_latency_ms=3000 if authenticated else 2400,
            max_specialists=3,
            allow_parallel_specialists=True,
            allow_manager=True,
            allow_judge=True,
            allow_repair=True,
            allow_session_memory=True,
            prefer_direct_answer=False,
            specialist_max_turns=5,
            manager_max_turns=6,
            judge_max_turns=3,
            repair_max_turns=3,
            reasons=reasons,
        )

    if plan.primary_domain in {"academic", "finance"} and plan.retrieval_strategy == "structured_tools":
        reasons.append("protected_structured_tools")
        return ExecutionBudget(
            tier="standard",
            planner_mode="deterministic",
            target_latency_ms=1500,
            max_specialists=1,
            allow_parallel_specialists=False,
            allow_manager=creative_or_summary,
            allow_judge=False,
            allow_repair=False,
            allow_session_memory=False,
            prefer_direct_answer=True,
            specialist_max_turns=4,
            manager_max_turns=5,
            judge_max_turns=2,
            repair_max_turns=2,
            reasons=reasons + (["summary_or_composition"] if creative_or_summary else []),
        )

    if plan.primary_domain in {"workflow", "support"} and plan.retrieval_strategy in {"structured_tools", "workflow_status"}:
        reasons.append("workflow_tool_lane")
        return ExecutionBudget(
            tier="standard",
            planner_mode="deterministic",
            target_latency_ms=1600,
            max_specialists=1,
            allow_parallel_specialists=False,
            allow_manager=creative_or_summary,
            allow_judge=False,
            allow_repair=False,
            allow_session_memory=False,
            prefer_direct_answer=True,
            specialist_max_turns=4,
            manager_max_turns=5,
            judge_max_turns=2,
            repair_max_turns=2,
            reasons=reasons + (["summary_or_composition"] if creative_or_summary else []),
        )

    if plan.retrieval_strategy == "graph_rag":
        reasons.append("graph_rag")
        return ExecutionBudget(
            tier="standard",
            planner_mode="deterministic",
            target_latency_ms=1800,
            max_specialists=1,
            allow_parallel_specialists=False,
            allow_manager=creative_or_summary,
            allow_judge=False,
            allow_repair=False,
            allow_session_memory=False,
            prefer_direct_answer=not creative_or_summary,
            specialist_max_turns=4,
            manager_max_turns=5,
            judge_max_turns=2,
            repair_max_turns=2,
            reasons=reasons + (["summary_or_composition"] if creative_or_summary else []),
        )

    if plan.primary_domain == "institution" and plan.retrieval_strategy in {
        "direct_answer",
        "document_search",
        "hybrid_retrieval",
        "pricing_projection",
    }:
        reasons.append("institutional_low_risk")
        return ExecutionBudget(
            tier="cheap" if not creative_or_summary else "standard",
            planner_mode="deterministic",
            target_latency_ms=700 if not creative_or_summary else 1200,
            max_specialists=1,
            allow_parallel_specialists=False,
            allow_manager=creative_or_summary,
            allow_judge=False,
            allow_repair=False,
            allow_session_memory=False,
            prefer_direct_answer=not creative_or_summary,
            specialist_max_turns=3,
            manager_max_turns=4,
            judge_max_turns=2,
            repair_max_turns=2,
            reasons=reasons + (["summary_or_composition"] if creative_or_summary else []),
        )

    reasons.append("default_standard")
    return ExecutionBudget(
        tier="standard",
        planner_mode="adaptive" if creative_or_summary else "deterministic",
        target_latency_ms=1800,
        max_specialists=2 if creative_or_summary else 1,
        allow_parallel_specialists=creative_or_summary,
        allow_manager=creative_or_summary,
        allow_judge=False,
        allow_repair=False,
        allow_session_memory=creative_or_summary,
        prefer_direct_answer=not creative_or_summary,
        specialist_max_turns=4,
        manager_max_turns=5,
        judge_max_turns=2,
        repair_max_turns=2,
        reasons=reasons + (["summary_or_composition"] if creative_or_summary else []),
    )


def should_use_manager(plan: SupervisorPlan, budget: ExecutionBudget, specialist_results: list[Any]) -> bool:
    if not budget.allow_manager:
        return False
    if plan.should_deny or plan.requires_clarification:
        return False
    if plan.request_kind == "multi_domain" or len(plan.secondary_domains) > 0:
        return True
    if len(specialist_results) > 1:
        return True
    return not budget.prefer_direct_answer


def should_run_judge(plan: SupervisorPlan, budget: ExecutionBudget, specialist_results: list[Any]) -> bool:
    if not budget.allow_judge:
        return False
    if plan.primary_domain in {"academic", "finance"}:
        return True
    return plan.request_kind in {"complex", "ambiguous", "sensitive", "multi_domain"} or len(specialist_results) > 1


def should_run_repair(plan: SupervisorPlan, budget: ExecutionBudget) -> bool:
    if not budget.allow_repair:
        return False
    return plan.request_kind in {"complex", "ambiguous", "sensitive", "multi_domain"} or plan.primary_domain in {"academic", "finance"}
