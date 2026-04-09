from __future__ import annotations

from types import SimpleNamespace

from ai_orchestrator.engine_selector import (
    SUPPORTED_PRIMARY_STACKS,
    resolve_primary_stack,
    resolve_stack_selection,
)
from ai_orchestrator.main import Settings


def test_supported_primary_stacks_excludes_crewai() -> None:
    assert SUPPORTED_PRIMARY_STACKS == {'langgraph', 'python_functions', 'llamaindex', 'specialist_supervisor'}


def test_resolve_primary_stack_prefers_feature_flag_active_paths() -> None:
    settings = Settings(
        feature_flag_primary_orchestration_stack='python_functions',
        orchestrator_engine='langgraph',
    )
    assert resolve_primary_stack(settings) == 'python_functions'


def test_resolve_stack_selection_returns_targeted_stack_without_engine_instantiation() -> None:
    settings = Settings(
        feature_flag_primary_orchestration_stack='langgraph',
        orchestrator_engine='langgraph',
    )
    request = SimpleNamespace(
        message='quero ver as notas do Lucas',
        conversation_id='conv-1',
        telegram_chat_id=1649845499,
        channel='telegram',
        user=SimpleNamespace(authenticated=True, role='guardian', scopes=[]),
    )

    from ai_orchestrator.engine_selector import set_runtime_targeted_stack_override, clear_runtime_targeted_stack_override

    try:
        set_runtime_targeted_stack_override(
            stack='python_functions',
            reason='test',
            operator='pytest',
            telegram_chat_allowlist=['1649845499'],
        )
        selection = resolve_stack_selection(settings=settings, request=request)
        assert selection.stack == 'python_functions'
        assert selection.mode.startswith('targeted:')
    finally:
        clear_runtime_targeted_stack_override(reason='cleanup', operator='pytest')
