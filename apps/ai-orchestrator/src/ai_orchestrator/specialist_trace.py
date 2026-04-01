from __future__ import annotations

from typing import Any


def _json_safe(value: Any) -> Any:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, dict):
        return {
            str(key): safe_value
            for key, raw_value in value.items()
            if (safe_value := _json_safe(raw_value)) is not None
        }
    if isinstance(value, (list, tuple, set)):
        return [_json_safe(item) for item in value]
    return str(value)


def _build_timeline(
    *,
    graph_path: list[str] | None,
    specialists_used: list[str] | None,
) -> list[dict[str, Any]]:
    timeline: list[dict[str, Any]] = []
    for index, node_name in enumerate(graph_path or [], start=1):
        normalized_name = str(node_name or "").strip()
        if not normalized_name:
            continue
        timeline.append({"index": index, "kind": "stage", "label": normalized_name})
    base_index = len(timeline)
    for offset, specialist_id in enumerate(specialists_used or [], start=1):
        normalized_name = str(specialist_id or "").strip()
        if not normalized_name:
            continue
        timeline.append({"index": base_index + offset, "kind": "specialist", "label": normalized_name})
    return timeline


def build_specialist_trace_sections(metadata: dict[str, Any] | None, *, graph_path: list[str] | None = None) -> dict[str, dict[str, Any]]:
    if not isinstance(metadata, dict):
        metadata = {}
    request_section: dict[str, Any] = {}
    response_section: dict[str, Any] = {}

    retrieval_advice = metadata.get("retrieval_advice")
    if isinstance(retrieval_advice, dict):
        request_section["retrieval_advice"] = {
            key: _json_safe(retrieval_advice.get(key))
            for key in (
                "primary_domain",
                "secondary_domains",
                "retrieval_strategy",
                "recommended_specialists",
                "requires_grounding",
                "requires_clarification",
                "should_deny",
                "confidence",
            )
            if key in retrieval_advice
        }

    plan = metadata.get("plan")
    if isinstance(plan, dict):
        request_section["plan"] = {
            key: _json_safe(plan.get(key))
            for key in (
                "request_kind",
                "primary_domain",
                "secondary_domains",
                "specialists",
                "retrieval_strategy",
                "requires_clarification",
                "should_deny",
                "confidence",
            )
            if key in plan
        }

    judge = metadata.get("judge")
    if isinstance(judge, dict):
        response_section["judge"] = {
            key: _json_safe(judge.get(key))
            for key in (
                "approved",
                "needs_clarification",
                "clarification_question",
                "grounding_score",
                "completeness_score",
                "issues",
            )
            if key in judge
        }

    specialists_used = metadata.get("specialists_used")
    if isinstance(specialists_used, list) and specialists_used:
        response_section["specialists_used"] = _json_safe(specialists_used)

    timeline = _build_timeline(
        graph_path=graph_path,
        specialists_used=specialists_used if isinstance(specialists_used, list) else None,
    )
    if timeline:
        response_section["timeline"] = timeline
        response_section["timeline_kind"] = "specialist_supervisor_stage_specialist_path"
        response_section["terminal_stage"] = timeline[-1]["label"]
        response_section["stage_count"] = len(timeline)

    return {
        "request": request_section,
        "response": response_section,
    }
