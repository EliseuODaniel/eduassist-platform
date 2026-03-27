from __future__ import annotations

from contextlib import contextmanager
from contextvars import ContextVar, Token
from dataclasses import dataclass, field
from time import perf_counter
from typing import Any

try:
    from crewai.events import (
        AgentExecutionCompletedEvent,
        AgentExecutionStartedEvent,
        BaseEventListener,
        CrewKickoffCompletedEvent,
        CrewKickoffStartedEvent,
        TaskEvaluationEvent,
        TaskFailedEvent,
        TaskCompletedEvent,
        TaskStartedEvent,
        ToolUsageErrorEvent,
        ToolUsageFinishedEvent,
        ToolUsageStartedEvent,
    )
    from crewai.events.types.llm_guardrail_events import (
        LLMGuardrailCompletedEvent,
        LLMGuardrailStartedEvent,
    )
    from crewai.events.listeners.tracing.utils import set_suppress_tracing_messages
except Exception:  # pragma: no cover - defensive import for local tooling
    BaseEventListener = object  # type: ignore[assignment]
    CrewKickoffStartedEvent = CrewKickoffCompletedEvent = None  # type: ignore[assignment]
    TaskStartedEvent = TaskCompletedEvent = TaskFailedEvent = TaskEvaluationEvent = None  # type: ignore[assignment]
    AgentExecutionStartedEvent = AgentExecutionCompletedEvent = None  # type: ignore[assignment]
    ToolUsageStartedEvent = ToolUsageFinishedEvent = ToolUsageErrorEvent = None  # type: ignore[assignment]
    LLMGuardrailStartedEvent = LLMGuardrailCompletedEvent = None  # type: ignore[assignment]
    set_suppress_tracing_messages = None  # type: ignore[assignment]


@dataclass
class PilotEventRecorder:
    slice_name: str
    started_at: float = field(default_factory=perf_counter)
    counts: dict[str, int] = field(default_factory=dict)
    events: list[dict[str, Any]] = field(default_factory=list)
    task_trace: dict[str, dict[str, Any]] = field(default_factory=dict)
    agent_trace: dict[str, dict[str, Any]] = field(default_factory=dict)
    crew_trace: dict[str, dict[str, Any]] = field(default_factory=dict)
    tool_trace: dict[str, dict[str, Any]] = field(default_factory=dict)
    guardrail_trace: dict[str, dict[str, Any]] = field(default_factory=dict)
    _task_started_at: dict[str, float] = field(default_factory=dict)
    _agent_started_at: dict[str, float] = field(default_factory=dict)
    _crew_started_at: dict[str, float] = field(default_factory=dict)
    _tool_started_at: dict[str, float] = field(default_factory=dict)

    def _elapsed_ms(self, started_at: float | None = None) -> float:
        origin = self.started_at if started_at is None else started_at
        return round((perf_counter() - origin) * 1000, 1)

    def _bucket(self, registry: dict[str, dict[str, Any]], key: str) -> dict[str, Any]:
        if key not in registry:
            registry[key] = {}
        return registry[key]

    def record(self, event_name: str, payload: dict[str, Any] | None = None) -> None:
        self.counts[event_name] = self.counts.get(event_name, 0) + 1
        enriched_payload = {'at_ms': self._elapsed_ms(), **(payload or {})}
        if len(self.events) >= 24:
            return
        self.events.append({'event': event_name, **enriched_payload})

    def _mark_started(
        self,
        *,
        registry: dict[str, dict[str, Any]],
        started_registry: dict[str, float],
        key: str | None,
        counter_key: str,
        payload: dict[str, Any] | None = None,
    ) -> None:
        if not key:
            return
        bucket = self._bucket(registry, key)
        bucket[counter_key] = int(bucket.get(counter_key, 0)) + 1
        bucket['last_started_at_ms'] = self._elapsed_ms()
        if payload:
            bucket.update({name: value for name, value in payload.items() if value is not None})
        started_registry[key] = perf_counter()

    def _mark_finished(
        self,
        *,
        registry: dict[str, dict[str, Any]],
        started_registry: dict[str, float],
        key: str | None,
        counter_key: str,
        payload: dict[str, Any] | None = None,
        duration_ms: float | None = None,
    ) -> None:
        if not key:
            return
        bucket = self._bucket(registry, key)
        bucket[counter_key] = int(bucket.get(counter_key, 0)) + 1
        bucket['last_finished_at_ms'] = self._elapsed_ms()
        if payload:
            bucket.update({name: value for name, value in payload.items() if value is not None})
        if duration_ms is None:
            started_at = started_registry.pop(key, None)
            if started_at is not None:
                duration_ms = self._elapsed_ms(started_at)
        else:
            started_registry.pop(key, None)
        if duration_ms is not None:
            bucket['last_duration_ms'] = round(duration_ms, 1)
            bucket['total_duration_ms'] = round(float(bucket.get('total_duration_ms', 0.0)) + float(duration_ms), 1)

    def mark_task_started(self, task_name: str | None) -> None:
        self._mark_started(
            registry=self.task_trace,
            started_registry=self._task_started_at,
            key=task_name,
            counter_key='started_count',
        )

    def mark_task_completed(self, task_name: str | None) -> None:
        self._mark_finished(
            registry=self.task_trace,
            started_registry=self._task_started_at,
            key=task_name,
            counter_key='completed_count',
        )

    def mark_task_failed(self, task_name: str | None, error: str | None = None) -> None:
        self._mark_finished(
            registry=self.task_trace,
            started_registry=self._task_started_at,
            key=task_name,
            counter_key='failed_count',
            payload={'last_error': error},
        )

    def mark_task_evaluated(self, task_name: str | None, evaluation_type: str | None = None) -> None:
        if not task_name:
            return
        bucket = self._bucket(self.task_trace, task_name)
        bucket['evaluation_count'] = int(bucket.get('evaluation_count', 0)) + 1
        if evaluation_type:
            bucket['last_evaluation_type'] = evaluation_type

    def mark_agent_started(self, agent_role: str | None) -> None:
        self._mark_started(
            registry=self.agent_trace,
            started_registry=self._agent_started_at,
            key=agent_role,
            counter_key='started_count',
        )

    def mark_agent_completed(self, agent_role: str | None) -> None:
        self._mark_finished(
            registry=self.agent_trace,
            started_registry=self._agent_started_at,
            key=agent_role,
            counter_key='completed_count',
        )

    def mark_crew_started(self, crew_name: str | None) -> None:
        self._mark_started(
            registry=self.crew_trace,
            started_registry=self._crew_started_at,
            key=crew_name,
            counter_key='started_count',
        )

    def mark_crew_completed(self, crew_name: str | None) -> None:
        self._mark_finished(
            registry=self.crew_trace,
            started_registry=self._crew_started_at,
            key=crew_name,
            counter_key='completed_count',
        )

    def mark_tool_started(
        self,
        tool_name: str | None,
        *,
        task_name: str | None = None,
        agent_role: str | None = None,
        tool_class: str | None = None,
    ) -> None:
        self._mark_started(
            registry=self.tool_trace,
            started_registry=self._tool_started_at,
            key=tool_name,
            counter_key='started_count',
            payload={
                'last_task_name': task_name,
                'last_agent_role': agent_role,
                'tool_class': tool_class,
            },
        )

    def mark_tool_finished(
        self,
        tool_name: str | None,
        *,
        task_name: str | None = None,
        agent_role: str | None = None,
        tool_class: str | None = None,
        from_cache: bool | None = None,
        duration_ms: float | None = None,
    ) -> None:
        self._mark_finished(
            registry=self.tool_trace,
            started_registry=self._tool_started_at,
            key=tool_name,
            counter_key='completed_count',
            payload={
                'last_task_name': task_name,
                'last_agent_role': agent_role,
                'tool_class': tool_class,
            },
            duration_ms=duration_ms,
        )
        if tool_name and from_cache:
            bucket = self._bucket(self.tool_trace, tool_name)
            bucket['cache_hit_count'] = int(bucket.get('cache_hit_count', 0)) + 1

    def mark_tool_failed(
        self,
        tool_name: str | None,
        *,
        task_name: str | None = None,
        agent_role: str | None = None,
        tool_class: str | None = None,
        error: str | None = None,
    ) -> None:
        self._mark_finished(
            registry=self.tool_trace,
            started_registry=self._tool_started_at,
            key=tool_name,
            counter_key='error_count',
            payload={
                'last_task_name': task_name,
                'last_agent_role': agent_role,
                'tool_class': tool_class,
                'last_error': error,
            },
        )

    def mark_guardrail_started(
        self,
        guardrail_name: str | None,
        *,
        task_name: str | None = None,
        agent_role: str | None = None,
        retry_count: int | None = None,
    ) -> None:
        self._mark_started(
            registry=self.guardrail_trace,
            started_registry={},
            key=guardrail_name,
            counter_key='started_count',
            payload={
                'last_task_name': task_name,
                'last_agent_role': agent_role,
                'last_retry_count': retry_count,
            },
        )

    def mark_guardrail_completed(
        self,
        guardrail_name: str | None,
        *,
        task_name: str | None = None,
        agent_role: str | None = None,
        retry_count: int | None = None,
        success: bool | None = None,
        error: str | None = None,
    ) -> None:
        bucket = self._bucket(self.guardrail_trace, guardrail_name) if guardrail_name else {}
        if guardrail_name:
            bucket['completed_count'] = int(bucket.get('completed_count', 0)) + 1
            bucket['last_finished_at_ms'] = self._elapsed_ms()
            if task_name:
                bucket['last_task_name'] = task_name
            if agent_role:
                bucket['last_agent_role'] = agent_role
            if retry_count is not None:
                bucket['last_retry_count'] = retry_count
            if success is not None:
                bucket['last_success'] = bool(success)
            if error:
                bucket['last_error'] = error


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


def _event_task_name(event: Any) -> str | None:
    task = getattr(event, 'task', None)
    if task is not None:
        return _safe_str(getattr(task, 'name', None)) or _safe_str(getattr(task, 'description', None))
    return _safe_str(getattr(event, 'task_name', None))


def _event_crew_name(event: Any) -> str | None:
    return _safe_str(getattr(event, 'crew_name', None))


def _event_agent_role(event: Any) -> str | None:
    agent = getattr(event, 'agent', None)
    return _safe_str(getattr(agent, 'role', None)) or _safe_str(getattr(event, 'agent_role', None))


def _event_guardrail_name(event: Any) -> str | None:
    guardrail = getattr(event, 'guardrail', None)
    if callable(guardrail):
        return _safe_str(getattr(guardrail, '__name__', None)) or _safe_str(guardrail)
    return _safe_str(guardrail)


def _event_guardrail_task_name(event: Any) -> str | None:
    task = getattr(event, 'from_task', None)
    if task is not None:
        return _safe_str(getattr(task, 'name', None)) or _safe_str(getattr(task, 'description', None))
    return _safe_str(getattr(event, 'task_name', None))


def _event_guardrail_agent_role(event: Any) -> str | None:
    agent = getattr(event, 'from_agent', None)
    if agent is not None:
        return _safe_str(getattr(agent, 'role', None))
    return _safe_str(getattr(event, 'agent_role', None))


def _tool_duration_ms(event: Any) -> float | None:
    started_at = getattr(event, 'started_at', None)
    finished_at = getattr(event, 'finished_at', None)
    if started_at is None or finished_at is None:
        return None
    try:
        return round((finished_at - started_at).total_seconds() * 1000, 1)
    except Exception:
        return None


class PilotEventListener(BaseEventListener):
    def setup_listeners(self, crewai_event_bus) -> None:  # type: ignore[override]
        if CrewKickoffStartedEvent is not None:
            @crewai_event_bus.on(CrewKickoffStartedEvent)
            def on_crew_started(source, event) -> None:  # pragma: no cover - event bus callback
                crew_name = _event_crew_name(event)
                _record_event(
                    'crew_started',
                    {'crew_name': crew_name},
                )
                recorder = _ACTIVE_RECORDER.get()
                if recorder is not None:
                    recorder.mark_crew_started(crew_name)

        if CrewKickoffCompletedEvent is not None:
            @crewai_event_bus.on(CrewKickoffCompletedEvent)
            def on_crew_completed(source, event) -> None:  # pragma: no cover - event bus callback
                crew_name = _event_crew_name(event)
                _record_event(
                    'crew_completed',
                    {'crew_name': crew_name},
                )
                recorder = _ACTIVE_RECORDER.get()
                if recorder is not None:
                    recorder.mark_crew_completed(crew_name)

        if TaskStartedEvent is not None:
            @crewai_event_bus.on(TaskStartedEvent)
            def on_task_started(source, event) -> None:  # pragma: no cover - event bus callback
                task_name = _event_task_name(event)
                _record_event(
                    'task_started',
                    {'task_name': task_name},
                )
                recorder = _ACTIVE_RECORDER.get()
                if recorder is not None:
                    recorder.mark_task_started(task_name)

        if TaskCompletedEvent is not None:
            @crewai_event_bus.on(TaskCompletedEvent)
            def on_task_completed(source, event) -> None:  # pragma: no cover - event bus callback
                task_name = _event_task_name(event)
                _record_event(
                    'task_completed',
                    {'task_name': task_name},
                )
                recorder = _ACTIVE_RECORDER.get()
                if recorder is not None:
                    recorder.mark_task_completed(task_name)

        if TaskFailedEvent is not None:
            @crewai_event_bus.on(TaskFailedEvent)
            def on_task_failed(source, event) -> None:  # pragma: no cover - event bus callback
                task_name = _event_task_name(event)
                error = _safe_str(getattr(event, 'error', None))
                _record_event(
                    'task_failed',
                    {'task_name': task_name, 'error': error},
                )
                recorder = _ACTIVE_RECORDER.get()
                if recorder is not None:
                    recorder.mark_task_failed(task_name, error=error)

        if TaskEvaluationEvent is not None:
            @crewai_event_bus.on(TaskEvaluationEvent)
            def on_task_evaluation(source, event) -> None:  # pragma: no cover - event bus callback
                task_name = _event_task_name(event)
                evaluation_type = _safe_str(getattr(event, 'evaluation_type', None))
                _record_event(
                    'task_evaluation',
                    {'task_name': task_name, 'evaluation_type': evaluation_type},
                )
                recorder = _ACTIVE_RECORDER.get()
                if recorder is not None:
                    recorder.mark_task_evaluated(task_name, evaluation_type=evaluation_type)

        if AgentExecutionStartedEvent is not None:
            @crewai_event_bus.on(AgentExecutionStartedEvent)
            def on_agent_started(source, event) -> None:  # pragma: no cover - event bus callback
                agent_role = _event_agent_role(event)
                _record_event(
                    'agent_started',
                    {'agent_role': agent_role},
                )
                recorder = _ACTIVE_RECORDER.get()
                if recorder is not None:
                    recorder.mark_agent_started(agent_role)

        if AgentExecutionCompletedEvent is not None:
            @crewai_event_bus.on(AgentExecutionCompletedEvent)
            def on_agent_completed(source, event) -> None:  # pragma: no cover - event bus callback
                agent_role = _event_agent_role(event)
                _record_event(
                    'agent_completed',
                    {'agent_role': agent_role},
                )
                recorder = _ACTIVE_RECORDER.get()
                if recorder is not None:
                    recorder.mark_agent_completed(agent_role)

        if ToolUsageStartedEvent is not None:
            @crewai_event_bus.on(ToolUsageStartedEvent)
            def on_tool_started(source, event) -> None:  # pragma: no cover - event bus callback
                tool_name = _safe_str(getattr(event, 'tool_name', None))
                task_name = _safe_str(getattr(event, 'task_name', None))
                agent_role = _safe_str(getattr(event, 'agent_role', None))
                tool_class = _safe_str(getattr(event, 'tool_class', None))
                _record_event(
                    'tool_started',
                    {
                        'tool_name': tool_name,
                        'task_name': task_name,
                        'agent_role': agent_role,
                    },
                )
                recorder = _ACTIVE_RECORDER.get()
                if recorder is not None:
                    recorder.mark_tool_started(
                        tool_name,
                        task_name=task_name,
                        agent_role=agent_role,
                        tool_class=tool_class,
                    )

        if ToolUsageFinishedEvent is not None:
            @crewai_event_bus.on(ToolUsageFinishedEvent)
            def on_tool_finished(source, event) -> None:  # pragma: no cover - event bus callback
                tool_name = _safe_str(getattr(event, 'tool_name', None))
                task_name = _safe_str(getattr(event, 'task_name', None))
                agent_role = _safe_str(getattr(event, 'agent_role', None))
                tool_class = _safe_str(getattr(event, 'tool_class', None))
                from_cache = getattr(event, 'from_cache', None)
                _record_event(
                    'tool_finished',
                    {
                        'tool_name': tool_name,
                        'task_name': task_name,
                        'agent_role': agent_role,
                        'from_cache': from_cache,
                    },
                )
                recorder = _ACTIVE_RECORDER.get()
                if recorder is not None:
                    recorder.mark_tool_finished(
                        tool_name,
                        task_name=task_name,
                        agent_role=agent_role,
                        tool_class=tool_class,
                        from_cache=bool(from_cache) if from_cache is not None else None,
                        duration_ms=_tool_duration_ms(event),
                    )

        if ToolUsageErrorEvent is not None:
            @crewai_event_bus.on(ToolUsageErrorEvent)
            def on_tool_error(source, event) -> None:  # pragma: no cover - event bus callback
                tool_name = _safe_str(getattr(event, 'tool_name', None))
                task_name = _safe_str(getattr(event, 'task_name', None))
                agent_role = _safe_str(getattr(event, 'agent_role', None))
                tool_class = _safe_str(getattr(event, 'tool_class', None))
                error = _safe_str(getattr(event, 'error', None))
                _record_event(
                    'tool_error',
                    {
                        'tool_name': tool_name,
                        'task_name': task_name,
                        'agent_role': agent_role,
                        'error': error,
                    },
                )
                recorder = _ACTIVE_RECORDER.get()
                if recorder is not None:
                    recorder.mark_tool_failed(
                        tool_name,
                        task_name=task_name,
                        agent_role=agent_role,
                        tool_class=tool_class,
                        error=error,
                    )

        if LLMGuardrailStartedEvent is not None:
            @crewai_event_bus.on(LLMGuardrailStartedEvent)
            def on_guardrail_started(source, event) -> None:  # pragma: no cover - event bus callback
                guardrail_name = _event_guardrail_name(event)
                task_name = _event_guardrail_task_name(event)
                agent_role = _event_guardrail_agent_role(event)
                retry_count = getattr(event, 'retry_count', None)
                _record_event(
                    'guardrail_started',
                    {
                        'guardrail_name': guardrail_name,
                        'task_name': task_name,
                        'agent_role': agent_role,
                        'retry_count': retry_count,
                    },
                )
                recorder = _ACTIVE_RECORDER.get()
                if recorder is not None:
                    recorder.mark_guardrail_started(
                        guardrail_name,
                        task_name=task_name,
                        agent_role=agent_role,
                        retry_count=int(retry_count) if isinstance(retry_count, int) else None,
                    )

        if LLMGuardrailCompletedEvent is not None:
            @crewai_event_bus.on(LLMGuardrailCompletedEvent)
            def on_guardrail_completed(source, event) -> None:  # pragma: no cover - event bus callback
                guardrail_name = _event_guardrail_name(event)
                task_name = _event_guardrail_task_name(event)
                agent_role = _event_guardrail_agent_role(event)
                retry_count = getattr(event, 'retry_count', None)
                success = getattr(event, 'success', None)
                error = _safe_str(getattr(event, 'error', None))
                _record_event(
                    'guardrail_completed',
                    {
                        'guardrail_name': guardrail_name,
                        'task_name': task_name,
                        'agent_role': agent_role,
                        'retry_count': retry_count,
                        'success': success,
                        'error': error,
                    },
                )
                recorder = _ACTIVE_RECORDER.get()
                if recorder is not None:
                    recorder.mark_guardrail_completed(
                        guardrail_name,
                        task_name=task_name,
                        agent_role=agent_role,
                        retry_count=int(retry_count) if isinstance(retry_count, int) else None,
                        success=bool(success) if success is not None else None,
                        error=error,
                    )


@contextmanager
def capture_pilot_events(slice_name: str):
    recorder = PilotEventRecorder(slice_name=slice_name)
    token: Token = _ACTIVE_RECORDER.set(recorder)
    try:
        yield recorder
    finally:
        _ACTIVE_RECORDER.reset(token)


@contextmanager
def suppress_crewai_tracing_messages():
    if set_suppress_tracing_messages is None:
        yield
        return
    token = set_suppress_tracing_messages(True)
    try:
        yield
    finally:
        try:
            _ = token
            set_suppress_tracing_messages(False)
        except Exception:
            pass


def serialize_pilot_events(recorder: PilotEventRecorder | None) -> dict[str, Any]:
    if recorder is None:
        return {'counts': {}, 'events': [], 'summary': {}, 'task_trace': {'tasks': {}, 'agents': {}, 'crews': {}, 'tools': {}}}
    return {
        'counts': dict(recorder.counts),
        'events': list(recorder.events),
        'summary': {
            'slice_name': recorder.slice_name,
            'elapsed_ms': recorder._elapsed_ms(),
            'captured_event_samples': len(recorder.events),
            'total_event_count': int(sum(recorder.counts.values())),
            'task_count': len(recorder.task_trace),
            'agent_count': len(recorder.agent_trace),
            'crew_count': len(recorder.crew_trace),
            'tool_count': len(recorder.tool_trace),
            'guardrail_count': len(recorder.guardrail_trace),
        },
        'task_trace': {
            'tasks': dict(recorder.task_trace),
            'agents': dict(recorder.agent_trace),
            'crews': dict(recorder.crew_trace),
            'tools': dict(recorder.tool_trace),
            'guardrails': dict(recorder.guardrail_trace),
        },
    }


try:  # pragma: no cover - registration side effect
    _pilot_listener = PilotEventListener()
except Exception:
    _pilot_listener = None
