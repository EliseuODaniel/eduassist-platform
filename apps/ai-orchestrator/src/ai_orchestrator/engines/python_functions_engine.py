from __future__ import annotations

from typing import Any

from ..agent_kernel import build_kernel_plan
from ..kernel_runtime import execute_kernel_plan
from ..models import MessageResponse
from .base import ResponseEngine


class PythonFunctionsEngine(ResponseEngine):
    name = 'python_functions'
    ready = True

    async def respond(self, *, request: Any, settings: Any, engine_mode: str | None = None) -> MessageResponse:
        mode = str(engine_mode or self.name)
        plan = build_kernel_plan(
            request=request,
            settings=settings,
            stack_name=self.name,
            mode=mode,
        )
        result = await execute_kernel_plan(
            request=request,
            settings=settings,
            plan=plan,
            engine_name=self.name,
            engine_mode=mode,
        )
        return MessageResponse.model_validate(result.response)

