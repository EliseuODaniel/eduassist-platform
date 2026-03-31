from __future__ import annotations

from dataclasses import dataclass

from .agent_kernel import KernelPlan


@dataclass(frozen=True)
class PathExecutionProfile:
    name: str
    prefer_fast_public_path: bool = False
    use_contextual_replan: bool = True
    prefer_specialist_supervisor: bool = False
    prefer_native_llamaindex_selector: bool = False
    prefer_native_llamaindex_subquestions: bool = False
    prefer_native_llamaindex_citation_engine: bool = False
    prefer_native_llamaindex_function_agent: bool = False
    prefer_native_llamaindex_qdrant_autoretriever: bool = False
    notes: tuple[str, ...] = ()


_PROFILES: dict[str, PathExecutionProfile] = {
    'langgraph': PathExecutionProfile(
        name='langgraph',
        notes=('path_family:langgraph', 'state_owner:langgraph'),
    ),
    'crewai': PathExecutionProfile(
        name='crewai',
        notes=('path_family:crewai', 'agent_flow:crewai'),
    ),
    'python_functions': PathExecutionProfile(
        name='python_functions',
        prefer_fast_public_path=True,
        notes=('path_family:python_functions', 'tool_first:deterministic'),
    ),
    'llamaindex': PathExecutionProfile(
        name='llamaindex',
        prefer_fast_public_path=True,
        prefer_native_llamaindex_selector=True,
        prefer_native_llamaindex_subquestions=True,
        prefer_native_llamaindex_citation_engine=True,
        prefer_native_llamaindex_function_agent=True,
        prefer_native_llamaindex_qdrant_autoretriever=True,
        notes=(
            'path_family:llamaindex',
            'native_router:enabled',
            'native_subquestions:enabled',
            'native_citation_engine:enabled',
            'native_function_agent:enabled',
            'native_qdrant_autoretriever:enabled',
        ),
    ),
    'specialist_supervisor': PathExecutionProfile(
        name='specialist_supervisor',
        prefer_specialist_supervisor=True,
        notes=(
            'path_family:specialist_supervisor',
            'manager_pattern:agents_as_tools',
            'quality_first:enabled',
            'judge_loop:enabled',
            'session_memory:enabled',
        ),
    ),
    'shadow': PathExecutionProfile(
        name='shadow',
        notes=('path_family:shadow',),
    ),
}


def get_path_execution_profile(engine_name: str) -> PathExecutionProfile:
    return _PROFILES.get(engine_name, PathExecutionProfile(name=engine_name))


def annotate_plan_for_path(*, plan: KernelPlan, profile: PathExecutionProfile, owner: str) -> KernelPlan:
    notes = list(dict.fromkeys([*plan.plan_notes, *profile.notes, f'path_owner:{owner}']))
    return plan.model_copy(update={'plan_notes': notes})
