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


def _build_node_timeline(graph_path: list[str] | None) -> list[dict[str, Any]]:
    timeline: list[dict[str, Any]] = []
    for index, node_name in enumerate(graph_path or [], start=1):
        normalized_name = str(node_name or '').strip()
        if not normalized_name:
            continue
        timeline.append(
            {
                'index': index,
                'kind': 'node',
                'label': normalized_name,
            }
        )
    return timeline


def build_langgraph_trace_sections(
    metadata: dict[str, Any] | None,
    *,
    graph_path: list[str] | None = None,
) -> dict[str, dict[str, Any]]:
    if not isinstance(metadata, dict):
        metadata = {}

    request_section: dict[str, Any] = {}
    response_section: dict[str, Any] = {}

    for field_name in (
        'thread_id',
        'checkpointer_enabled',
        'checkpointer_backend',
        'state_available',
        'state_fetch_error',
        'state_fetch_error_message',
        'checkpoint_id',
        'checkpoint_ns',
        'state_route',
        'state_slice_name',
        'hitl_status',
        'created_at',
        'next_nodes',
        'task_names',
        'top_level_interrupt_count',
        'task_interrupt_count',
        'has_pending_interrupt',
        'snapshot_metadata',
    ):
        if field_name in metadata:
            request_section[field_name] = _json_safe(metadata.get(field_name))

    timeline = _build_node_timeline(graph_path)
    if timeline:
        response_section['timeline'] = timeline
        response_section['timeline_kind'] = 'langgraph_node_path'
        response_section['terminal_node'] = timeline[-1]['label']
        response_section['node_count'] = len(timeline)

    if 'task_names' in metadata:
        response_section['task_names'] = _json_safe(metadata.get('task_names'))
    if 'next_nodes' in metadata:
        response_section['next_nodes'] = _json_safe(metadata.get('next_nodes'))
    if 'has_pending_interrupt' in metadata:
        response_section['has_pending_interrupt'] = bool(metadata.get('has_pending_interrupt'))
    if 'hitl_status' in metadata:
        response_section['hitl_status'] = _json_safe(metadata.get('hitl_status'))

    return {
        'request': request_section,
        'response': response_section,
    }
