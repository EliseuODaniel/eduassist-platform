from __future__ import annotations

from typing import Any

from .agent_kernel import KernelPlan, KernelRunResult, build_kernel_plan
from .kernel_runtime import execute_kernel_plan
from .llamaindex_native_runtime import maybe_execute_llamaindex_native_plan
from .models import MessageResponseRequest
from .path_profiles import annotate_plan_for_path, get_path_execution_profile


def build_llamaindex_plan(*, request: MessageResponseRequest, settings: Any, mode: str) -> KernelPlan:
    profile = get_path_execution_profile('llamaindex')
    plan = build_kernel_plan(
        request=request,
        settings=settings,
        stack_name='llamaindex',
        mode=mode,
    )
    return annotate_plan_for_path(plan=plan, profile=profile, owner='llamaindex_path_runtime')


def _build_llamaindex_replan(request: MessageResponseRequest, settings: Any, mode: str) -> KernelPlan:
    return build_llamaindex_plan(request=request, settings=settings, mode=mode)


async def execute_llamaindex_plan(
    *,
    request: MessageResponseRequest,
    settings: Any,
    plan: KernelPlan,
    engine_mode: str,
) -> KernelRunResult:
    profile = get_path_execution_profile('llamaindex')
    result = await maybe_execute_llamaindex_native_plan(
        request=request,
        settings=settings,
        plan=plan,
        engine_name='llamaindex',
        engine_mode=engine_mode,
        path_profile=profile,
    )
    if result is not None:
        return result
    return await execute_kernel_plan(
        request=request,
        settings=settings,
        plan=plan,
        engine_name='llamaindex',
        engine_mode=engine_mode,
        path_profile=profile,
        replan_builder=_build_llamaindex_replan,
    )
