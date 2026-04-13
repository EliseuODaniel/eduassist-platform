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


def build_engine_trace_sections(
    metadata: dict[str, Any] | None,
    *,
    graph_path: list[str] | None = None,
) -> dict[str, dict[str, Any]]:
    if not isinstance(metadata, dict):
        metadata = {}

    request_section: dict[str, Any] = {}
    response_section: dict[str, Any] = {}

    retrieval_policy = metadata.get("retrieval_policy")
    if isinstance(retrieval_policy, dict):
        request_section["retrieval_policy"] = _json_safe(retrieval_policy)

    retrieval_result = metadata.get("retrieval_result")
    if isinstance(retrieval_result, dict):
        response_section["retrieval_result"] = _json_safe(retrieval_result)

    if graph_path:
        response_section["timeline"] = [
            {"index": index, "kind": "stage", "label": str(node_name)}
            for index, node_name in enumerate(graph_path, start=1)
            if str(node_name or "").strip()
        ]
        if response_section["timeline"]:
            response_section["timeline_kind"] = "engine_stage_path"
            response_section["terminal_stage"] = response_section["timeline"][-1]["label"]
            response_section["stage_count"] = len(response_section["timeline"])

    return {
        "request": request_section,
        "response": response_section,
    }
