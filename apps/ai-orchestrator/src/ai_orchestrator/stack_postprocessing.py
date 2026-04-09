from __future__ import annotations

from typing import Any

from .grounded_answer_experience import apply_grounded_answer_experience
from .models import MessageResponse, MessageResponseRequest


async def postprocess_stack_response(
    *,
    stack_name: str,
    request: MessageResponseRequest,
    response: MessageResponse,
    settings: Any,
) -> MessageResponse:
    return await apply_grounded_answer_experience(
        request=request,
        response=response,
        settings=settings,
        stack_name=stack_name,
    )
