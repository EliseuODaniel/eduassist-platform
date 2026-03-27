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


def _build_crewai_timeline(metadata: dict[str, Any]) -> list[dict[str, Any]]:
    timeline: list[dict[str, Any]] = []
    validation_stack = metadata.get('validation_stack')
    if isinstance(validation_stack, list):
        for index, step_name in enumerate(validation_stack, start=1):
            normalized_name = str(step_name or '').strip()
            if not normalized_name:
                continue
            timeline.append(
                {
                    'index': index,
                    'kind': 'stage',
                    'label': normalized_name,
                }
            )

    task_names = metadata.get('task_names')
    if isinstance(task_names, list):
        base_index = len(timeline)
        for offset, task_name in enumerate(task_names, start=1):
            normalized_name = str(task_name or '').strip()
            if not normalized_name:
                continue
            timeline.append(
                {
                    'index': base_index + offset,
                    'kind': 'task',
                    'label': normalized_name,
                }
            )
    return timeline


def build_crewai_trace_sections(metadata: dict[str, Any] | None) -> dict[str, dict[str, Any]]:
    if not isinstance(metadata, dict):
        return {'request': {}, 'response': {}}

    request_section: dict[str, Any] = {}
    response_section: dict[str, Any] = {}

    for field_name in (
        'slice_name',
        'flow_enabled',
        'flow_state_id',
        'flow_state_persisted',
        'pending_review',
        'review_flow_id',
        'review_required',
        'agent_roles',
        'task_names',
        'validation_stack',
    ):
        if field_name in metadata:
            request_section[field_name] = _json_safe(metadata.get(field_name))

    for field_name in (
        'latency_ms',
        'deterministic_backstop_used',
        'review_rejected',
    ):
        if field_name in metadata:
            response_section[field_name] = _json_safe(metadata.get(field_name))

    if 'review_message' in metadata:
        response_section['review_message'] = _json_safe(metadata.get('review_message'))

    judge = metadata.get('judge')
    if isinstance(judge, dict):
        response_section['judge'] = {
            key: _json_safe(judge.get(key))
            for key in ('valid', 'reason', 'revision_needed')
            if key in judge
        }

    event_summary = metadata.get('event_summary')
    if isinstance(event_summary, dict) and event_summary:
        response_section['event_summary'] = _json_safe(event_summary)

    task_trace = metadata.get('task_trace')
    if isinstance(task_trace, dict) and task_trace:
        response_section['task_trace'] = _json_safe(task_trace)

    event_listener = metadata.get('event_listener')
    if isinstance(event_listener, dict):
        counts = event_listener.get('counts')
        if isinstance(counts, dict) and counts:
            response_section['event_counts'] = _json_safe(counts)

    timeline = _build_crewai_timeline(metadata)
    if timeline:
        response_section['timeline'] = timeline
        response_section['timeline_kind'] = 'crewai_stage_task_path'
        response_section['terminal_stage'] = timeline[-1]['label']
        response_section['stage_count'] = len(timeline)

    return {
        'request': request_section,
        'response': response_section,
    }
