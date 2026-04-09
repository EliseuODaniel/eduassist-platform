from __future__ import annotations

from typing import Any

from .python_functions_kernel import KernelPlan, KernelRunResult, build_kernel_plan
from .python_functions_kernel_runtime import execute_kernel_plan
from .models import MessageResponseRequest
from .path_profiles import annotate_plan_for_path, get_path_execution_profile
from .python_functions_native_runtime import maybe_execute_python_functions_native_plan


def build_python_functions_plan(*, request: MessageResponseRequest, settings: Any, mode: str) -> KernelPlan:
    profile = get_path_execution_profile('python_functions')
    plan = build_kernel_plan(
        request=request,
        settings=settings,
        stack_name='python_functions',
        mode=mode,
    )
    return annotate_plan_for_path(plan=plan, profile=profile, owner='python_functions_runtime')


def _build_python_functions_replan(request: MessageResponseRequest, settings: Any, mode: str) -> KernelPlan:
    return build_python_functions_plan(request=request, settings=settings, mode=mode)


async def execute_python_functions_plan(
    *,
    request: MessageResponseRequest,
    settings: Any,
    plan: KernelPlan,
    engine_mode: str,
) -> KernelRunResult:
    profile = get_path_execution_profile('python_functions')
    result = await maybe_execute_python_functions_native_plan(
        request=request,
        settings=settings,
        plan=plan,
        engine_name='python_functions',
        engine_mode=engine_mode,
        path_profile=profile,
    )
    if result is not None:
        return result
    return await execute_kernel_plan(
        request=request,
        settings=settings,
        plan=plan,
        engine_name='python_functions',
        engine_mode=engine_mode,
        path_profile=profile,
        replan_builder=_build_python_functions_replan,
    )
