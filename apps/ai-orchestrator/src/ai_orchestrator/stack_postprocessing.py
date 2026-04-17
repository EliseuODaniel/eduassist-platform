from __future__ import annotations

from typing import Any

from .grounded_answer_experience import apply_grounded_answer_experience
from .models import MessageResponse, MessageResponseRequest
from .stack_answer_surface_refiner import maybe_refine_stack_response_surface


async def postprocess_stack_response(
    *,
    stack_name: str,
    request: MessageResponseRequest,
    response: MessageResponse,
    settings: Any,
) -> MessageResponse:
    response = await apply_grounded_answer_experience(
        request=request,
        response=response,
        settings=settings,
        stack_name=stack_name,
    )
    return await maybe_refine_stack_response_surface(
        stack_name=stack_name,
        request=request,
        response=response,
        settings=settings,
    )
