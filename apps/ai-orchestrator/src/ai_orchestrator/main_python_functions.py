from __future__ import annotations

from .dedicated_stack_app import create_dedicated_stack_app


app = create_dedicated_stack_app(
    stack_name='python_functions',
    service_name='ai-orchestrator-python-functions',
)
