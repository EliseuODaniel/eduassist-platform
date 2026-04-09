from __future__ import annotations

from typing import Any


async def generate_langgraph_message_response(*, request: Any, settings: Any, engine_name: str, engine_mode: str) -> Any:
    from .langgraph_message_workflow import run_langgraph_message_workflow
    from .runtime import generate_message_response

    try:
        return await run_langgraph_message_workflow(
            request=request,
            settings=settings,
            engine_name=engine_name,
            engine_mode=engine_mode,
        )
    except Exception:
        # Preserve the historical runtime as a safe fallback while the graph-native
        # response workflow grows path by path.
        return await generate_message_response(
            request=request,
            settings=settings,
            engine_name=engine_name,
            engine_mode=engine_mode,
        )
