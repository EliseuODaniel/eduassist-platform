from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from .entity_resolution import ResolvedEntityHints, resolve_entity_hints
from .graph import (
    OrchestrationState,
    classify_request,
    clarify,
    deny,
    graph_rag_retrieval,
    handoff,
    hybrid_retrieval,
    route_request,
    security_gate,
    select_slice,
    structured_tool_call,
    to_preview,
)
from .models import MessageResponseRequest, OrchestrationPreview, OrchestrationRequest


class KernelExecutionStep(BaseModel):
    name: str
    purpose: str
    stage: str


class KernelPlan(BaseModel):
    stack_name: str
    mode: str
    slice_name: str
    preview: OrchestrationPreview
    entities: ResolvedEntityHints
    execution_steps: list[KernelExecutionStep] = Field(default_factory=list)
    plan_notes: list[str] = Field(default_factory=list)


class KernelReflection(BaseModel):
    grounded: bool = True
    verifier_reason: str | None = None
    fallback_used: bool = False
    answer_judge_used: bool = False
    notes: list[str] = Field(default_factory=list)


class KernelRunResult(BaseModel):
    plan: KernelPlan
    reflection: KernelReflection
    response: dict[str, Any]


def _execution_steps_for_route(preview: OrchestrationPreview) -> list[KernelExecutionStep]:
    if preview.mode.value == 'structured_tool':
        return [
            KernelExecutionStep(name='resolve_context', purpose='Load actor, conversation memory, and active entities.', stage='plan'),
            KernelExecutionStep(name='execute_tools', purpose='Run deterministic tools or structured services selected for this request.', stage='execute'),
            KernelExecutionStep(name='compose_answer', purpose='Compose a grounded response using structured outputs.', stage='execute'),
            KernelExecutionStep(name='verify_answer', purpose='Check coverage, grounding, and access constraints before returning.', stage='reflect'),
        ]
    if preview.mode.value == 'hybrid_retrieval':
        return [
            KernelExecutionStep(name='resolve_context', purpose='Load actor, conversation memory, and active entities.', stage='plan'),
            KernelExecutionStep(name='retrieve_evidence', purpose='Run hybrid retrieval and build a concise evidence pack.', stage='execute'),
            KernelExecutionStep(name='compose_answer', purpose='Draft a grounded response from retrieval evidence.', stage='execute'),
            KernelExecutionStep(name='verify_answer', purpose='Check grounding and fall back safely if needed.', stage='reflect'),
        ]
    if preview.mode.value == 'graph_rag':
        return [
            KernelExecutionStep(name='resolve_context', purpose='Load actor, conversation memory, and active entities.', stage='plan'),
            KernelExecutionStep(name='graph_query', purpose='Run a corpus-level GraphRAG query or a safe fallback search.', stage='execute'),
            KernelExecutionStep(name='verify_answer', purpose='Check the final answer against policy and factual anchors.', stage='reflect'),
        ]
    if preview.mode.value == 'handoff':
        return [
            KernelExecutionStep(name='resolve_context', purpose='Load actor and conversation context.', stage='plan'),
            KernelExecutionStep(name='open_handoff', purpose='Create a human-support handoff with protocol and queue.', stage='execute'),
            KernelExecutionStep(name='verify_answer', purpose='Confirm the handoff response is clear and actionable.', stage='reflect'),
        ]
    return [
        KernelExecutionStep(name='resolve_context', purpose='Load minimal context required for the answer.', stage='plan'),
        KernelExecutionStep(name='safe_response', purpose='Return a deterministic clarify or deny response.', stage='execute'),
        KernelExecutionStep(name='verify_answer', purpose='Confirm the response stays within policy and contract.', stage='reflect'),
    ]


def _build_state(request: MessageResponseRequest) -> OrchestrationState:
    orchestration_request = OrchestrationRequest(
        message=request.message,
        conversation_id=request.conversation_id,
        user=request.user,
        allow_graph_rag=request.allow_graph_rag,
        allow_handoff=request.allow_handoff,
    )
    return {
        'request': orchestration_request,
        'graph_path': [],
        'risk_flags': [],
    }


def build_kernel_plan(*, request: MessageResponseRequest, settings: Any, stack_name: str, mode: str) -> KernelPlan:
    state = _build_state(request)
    state = {**state, **classify_request(state)}
    state = {**state, **security_gate(state)}
    state = {**state, **route_request(state, {'graph_rag_enabled': bool(getattr(settings, 'graph_rag_enabled', False))})}
    state = {**state, **select_slice(state)}

    route = str(state.get('route', 'clarify'))
    if route == 'structured_tool':
        state = {**state, **structured_tool_call(state)}
    elif route == 'hybrid_retrieval':
        state = {**state, **hybrid_retrieval(state)}
    elif route == 'graph_rag':
        state = {**state, **graph_rag_retrieval(state)}
    elif route == 'handoff':
        state = {**state, **handoff(state)}
    elif route == 'deny':
        state = {**state, **deny(state)}
    else:
        state = {**state, **clarify(state)}

    preview = to_preview(state)
    entities = resolve_entity_hints(request.message)
    notes: list[str] = []
    if entities.protocol_code:
        notes.append(f'protocol_hint:{entities.protocol_code}')
    if entities.quantity_hint is not None and entities.is_hypothetical:
        notes.append(f'hypothetical_quantity:{entities.quantity_hint}')
    if entities.domain_hint:
        notes.append(f'entity_domain_hint:{entities.domain_hint}')

    return KernelPlan(
        stack_name=stack_name,
        mode=mode,
        slice_name=str(state.get('slice_name', 'public')),
        preview=preview,
        entities=entities,
        execution_steps=_execution_steps_for_route(preview),
        plan_notes=notes,
    )

