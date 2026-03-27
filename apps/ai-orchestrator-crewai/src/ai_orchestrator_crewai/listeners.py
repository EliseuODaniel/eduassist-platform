from __future__ import annotations

from contextlib import contextmanager
from contextvars import ContextVar, Token
from dataclasses import dataclass, field
from typing import Any

try:
    from crewai.events import (
        AgentExecutionCompletedEvent,
        AgentExecutionStartedEvent,
        BaseEventListener,
        CrewKickoffCompletedEvent,
        CrewKickoffStartedEvent,
        TaskCompletedEvent,
        TaskStartedEvent,
    )
except Exception:  # pragma: no cover - defensive import for local tooling
    BaseEventListener = object  # type: ignore[assignment]
    CrewKickoffStartedEvent = CrewKickoffCompletedEvent = None  # type: ignore[assignment]
    TaskStartedEvent = TaskCompletedEvent = None  # type: ignore[assignment]
    AgentExecutionStartedEvent = AgentExecutionCompletedEvent = None  # type: ignore[assignment]


@dataclass
class PilotEventRecorder:
    slice_name: str
    counts: dict[str, int] = field(default_factory=dict)
    events: list[dict[str, Any]] = field(default_factory=list)

    def record(self, event_name: str, payload: dict[str, Any] | None = None) -> None:
        self.counts[event_name] = self.counts.get(event_name, 0) + 1
        if len(self.events) >= 24:
            return
        self.events.append({'event': event_name, **(payload or {})})


_ACTIVE_RECORDER: ContextVar[PilotEventRecorder | None] = ContextVar('crewai_pilot_event_recorder', default=None)


def _safe_str(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _record_event(event_name: str, payload: dict[str, Any] | None = None) -> None:
    recorder = _ACTIVE_RECORDER.get()
    if recorder is None:
        return
    recorder.record(event_name, payload)


class PilotEventListener(BaseEventListener):
    def setup_listeners(self, crewai_event_bus) -> None:  # type: ignore[override]
        if CrewKickoffStartedEvent is not None:
            @crewai_event_bus.on(CrewKickoffStartedEvent)
            def on_crew_started(source, event) -> None:  # pragma: no cover - event bus callback
                _record_event(
                    'crew_started',
                    {'crew_name': _safe_str(getattr(event, 'crew_name', None))},
                )

        if CrewKickoffCompletedEvent is not None:
            @crewai_event_bus.on(CrewKickoffCompletedEvent)
            def on_crew_completed(source, event) -> None:  # pragma: no cover - event bus callback
                _record_event(
                    'crew_completed',
                    {'crew_name': _safe_str(getattr(event, 'crew_name', None))},
                )

        if TaskStartedEvent is not None:
            @crewai_event_bus.on(TaskStartedEvent)
            def on_task_started(source, event) -> None:  # pragma: no cover - event bus callback
                _record_event(
                    'task_started',
                    {'task_name': _safe_str(getattr(event, 'task_name', None))},
                )

        if TaskCompletedEvent is not None:
            @crewai_event_bus.on(TaskCompletedEvent)
            def on_task_completed(source, event) -> None:  # pragma: no cover - event bus callback
                _record_event(
                    'task_completed',
                    {'task_name': _safe_str(getattr(event, 'task_name', None))},
                )

        if AgentExecutionStartedEvent is not None:
            @crewai_event_bus.on(AgentExecutionStartedEvent)
            def on_agent_started(source, event) -> None:  # pragma: no cover - event bus callback
                agent = getattr(event, 'agent', None)
                _record_event(
                    'agent_started',
                    {'agent_role': _safe_str(getattr(agent, 'role', None))},
                )

        if AgentExecutionCompletedEvent is not None:
            @crewai_event_bus.on(AgentExecutionCompletedEvent)
            def on_agent_completed(source, event) -> None:  # pragma: no cover - event bus callback
                agent = getattr(event, 'agent', None)
                _record_event(
                    'agent_completed',
                    {'agent_role': _safe_str(getattr(agent, 'role', None))},
                )


@contextmanager
def capture_pilot_events(slice_name: str):
    recorder = PilotEventRecorder(slice_name=slice_name)
    token: Token = _ACTIVE_RECORDER.set(recorder)
    try:
        yield recorder
    finally:
        _ACTIVE_RECORDER.reset(token)


def serialize_pilot_events(recorder: PilotEventRecorder | None) -> dict[str, Any]:
    if recorder is None:
        return {'counts': {}, 'events': []}
    return {
        'counts': dict(recorder.counts),
        'events': list(recorder.events),
    }


try:  # pragma: no cover - registration side effect
    _pilot_listener = PilotEventListener()
except Exception:
    _pilot_listener = None
