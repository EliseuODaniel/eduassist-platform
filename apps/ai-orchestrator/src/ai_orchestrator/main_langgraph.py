from __future__ import annotations

from .dedicated_stack_app import create_dedicated_stack_app


app = create_dedicated_stack_app(
    stack_name='langgraph',
    service_name='ai-orchestrator-langgraph',
)
