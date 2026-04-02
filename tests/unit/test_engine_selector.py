from __future__ import annotations

from ai_orchestrator.engine_selector import SUPPORTED_PRIMARY_STACKS, resolve_primary_stack
from ai_orchestrator.main import Settings


def test_supported_primary_stacks_excludes_crewai() -> None:
    assert SUPPORTED_PRIMARY_STACKS == {'langgraph', 'python_functions', 'llamaindex', 'specialist_supervisor'}


def test_resolve_primary_stack_prefers_feature_flag_active_paths() -> None:
    settings = Settings(
        feature_flag_primary_orchestration_stack='python_functions',
        orchestrator_engine='langgraph',
    )
    assert resolve_primary_stack(settings) == 'python_functions'
