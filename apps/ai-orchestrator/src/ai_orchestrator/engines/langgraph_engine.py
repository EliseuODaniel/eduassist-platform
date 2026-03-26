from __future__ import annotations

from typing import Any

from .base import ResponseEngine


class LangGraphEngine(ResponseEngine):
    name = 'langgraph'
    ready = True

    async def respond(self, *, request: Any, settings: Any) -> Any:
        from ..runtime import generate_message_response

        return await generate_message_response(request=request, settings=settings)
