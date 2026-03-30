from __future__ import annotations

from typing import Any

from ..agent_kernel import KernelPlan
from ..llamaindex_path_runtime import build_llamaindex_plan, execute_llamaindex_plan
from ..models import MessageResponse
from .base import ResponseEngine

try:
    from llama_index.core.workflow import Context, Event, StartEvent, StopEvent, Workflow, step

    LLAMAINDEX_WORKFLOW_AVAILABLE = True
except Exception:  # pragma: no cover - optional dependency
    Context = Event = StartEvent = StopEvent = Workflow = None  # type: ignore[assignment]
    step = None  # type: ignore[assignment]
    LLAMAINDEX_WORKFLOW_AVAILABLE = False


if LLAMAINDEX_WORKFLOW_AVAILABLE:

    class PlanBuiltEvent(Event):
        plan: KernelPlan


    class ResponseReadyEvent(Event):
        response_payload: dict[str, Any]


    class LlamaIndexOrchestrationWorkflow(Workflow):
        def __init__(self, *, request: Any, settings: Any, engine_name: str, engine_mode: str) -> None:
            super().__init__(timeout=120, verbose=False)
            self.request = request
            self.settings = settings
            self.engine_name = engine_name
            self.engine_mode = engine_mode

        @step
        async def plan(self, ctx: Context, ev: StartEvent) -> PlanBuiltEvent:
            plan = build_llamaindex_plan(
                request=self.request,
                settings=self.settings,
                mode=self.engine_mode,
            )
            await ctx.store.set('kernel_plan', plan.model_dump(mode='json'))
            return PlanBuiltEvent(plan=plan)

        @step
        async def execute(self, ctx: Context, ev: PlanBuiltEvent) -> ResponseReadyEvent:
            result = await execute_llamaindex_plan(
                request=self.request,
                settings=self.settings,
                plan=ev.plan,
                engine_mode=self.engine_mode,
            )
            await ctx.store.set('kernel_reflection', result.reflection.model_dump(mode='json'))
            return ResponseReadyEvent(response_payload=result.response)

        @step
        async def reflect(self, ctx: Context, ev: ResponseReadyEvent) -> StopEvent:
            return StopEvent(result=ev.response_payload)


class LlamaIndexWorkflowEngine(ResponseEngine):
    name = 'llamaindex'
    ready = LLAMAINDEX_WORKFLOW_AVAILABLE

    async def respond(self, *, request: Any, settings: Any, engine_mode: str | None = None) -> MessageResponse:
        mode = str(engine_mode or self.name)
        if not LLAMAINDEX_WORKFLOW_AVAILABLE:
            return MessageResponse(
                message_text='O caminho LlamaIndex ainda nao esta disponivel neste runtime. Reconstrua o ambiente com as dependencias novas para ativar este modo.',
                mode='clarify',  # type: ignore[arg-type]
                classification={
                    'domain': 'unknown',
                    'access_tier': 'public',
                    'confidence': 0.0,
                    'reason': 'llamaindex_dependency_unavailable',
                },  # type: ignore[arg-type]
                reason='llamaindex_dependency_unavailable',
                selected_tools=[],
                graph_path=['kernel:llamaindex', 'dependency_unavailable'],
                retrieval_backend='none',  # type: ignore[arg-type]
                needs_authentication=False,
                citations=[],
                calendar_events=[],
                visual_assets=[],
                risk_flags=['dependency_unavailable'],
                suggested_replies=[],
            )
        workflow = LlamaIndexOrchestrationWorkflow(
            request=request,
            settings=settings,
            engine_name=self.name,
            engine_mode=mode,
        )
        response_payload = await workflow.run()
        return MessageResponse.model_validate(response_payload)
