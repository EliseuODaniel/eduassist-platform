from __future__ import annotations

from importlib.util import find_spec
from typing import Any

from .agents import build_public_agent_specs
from .state import CrewAIPublicFlowState
from .tasks import build_public_task_specs
from ..engines.base import ShadowRunResult


def _effective_conversation_id(request: Any) -> str | None:
    conversation_id = getattr(request, 'conversation_id', None)
    if conversation_id:
        return str(conversation_id)
    channel = getattr(getattr(request, 'channel', None), 'value', None)
    telegram_chat_id = getattr(request, 'telegram_chat_id', None)
    if channel == 'telegram' and telegram_chat_id is not None:
        return f'telegram:{telegram_chat_id}'
    return None


def _normalize_text(value: str) -> str:
    return ' '.join(str(value or '').strip().lower().split())


def _crewai_dependency_status() -> tuple[bool, str]:
    if find_spec('crewai') is not None:
        return True, ''
    return False, 'crewai_dependency_unavailable_or_blocked'


def _build_public_flow_state(request: Any) -> CrewAIPublicFlowState:
    dependency_available, dependency_reason = _crewai_dependency_status()
    message = str(getattr(request, 'message', '') or '')
    state = CrewAIPublicFlowState(
        conversation_id=_effective_conversation_id(request),
        message=message,
        normalized_message=_normalize_text(message),
        dependency_available=dependency_available,
        dependency_reason=dependency_reason,
    )
    state.evidence_summary = {
        'agent_count': '3',
        'task_count': '3',
        'agent_roles': ','.join(spec.role for spec in build_public_agent_specs()),
        'task_names': ','.join(spec.name for spec in build_public_task_specs()),
    }
    return state


async def run_public_shadow_flow(*, request: Any, settings: Any) -> ShadowRunResult:
    del settings
    state = _build_public_flow_state(request)
    if not state.dependency_available:
        return ShadowRunResult(
            engine_name='crewai',
            executed=False,
            reason=state.dependency_reason,
            metadata=state.model_dump(mode='json'),
        )

    return ShadowRunResult(
        engine_name='crewai',
        executed=False,
        reason='crewai_public_flow_scaffold_only',
        metadata=state.model_dump(mode='json'),
    )
