from __future__ import annotations

from typing import Any

from ..models import MessageResponse
from ..python_functions_runtime import build_python_functions_plan, execute_python_functions_plan
from .base import ResponseEngine


class PythonFunctionsEngine(ResponseEngine):
    name = 'python_functions'
    ready = True

    async def respond(self, *, request: Any, settings: Any, engine_mode: str | None = None) -> MessageResponse:
        mode = str(engine_mode or self.name)
        plan = build_python_functions_plan(
            request=request,
            settings=settings,
            mode=mode,
        )
        result = await execute_python_functions_plan(
            request=request,
            settings=settings,
            plan=plan,
            engine_mode=mode,
        )
        return MessageResponse.model_validate(result.response)
