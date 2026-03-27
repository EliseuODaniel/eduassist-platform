from __future__ import annotations

import asyncio
from typing import Any

from pydantic import BaseModel, Field

try:
    import crewai as crewai_pkg  # type: ignore
    from crewai import Agent, Crew, LLM, Process, Task  # type: ignore
except Exception:  # pragma: no cover
    crewai_pkg = None  # type: ignore[assignment]
    Agent = Crew = LLM = Process = Task = None  # type: ignore[assignment]

from .guardrails import (
    extract_literal_anchors,
    require_anchor_overlap,
    require_nonempty_reason_when_invalid,
    require_pydantic_model,
)
from .listeners import capture_pilot_events, serialize_pilot_events, suppress_crewai_tracing_messages


class RenderedAnswer(BaseModel):
    answer_text: str = Field(min_length=1)


class RenderedJudge(BaseModel):
    valid: bool
    reason: str = ''
    revision_needed: bool = False


def _crewai_google_model(configured_model: str) -> str:
    base = str(configured_model or '').strip()
    if base.startswith('models/'):
        base = base.split('/', 1)[1]
    if base.startswith('gemini/'):
        base = base.split('/', 1)[1]
    if '-preview' in base:
        return 'gemini-2.5-flash'
    return base or 'gemini-2.5-flash'


def _build_llm(settings: Any) -> Any:
    if LLM is None:
        return None
    model_name = _crewai_google_model(
        str(getattr(settings, 'google_model', 'gemini-2.5-flash-preview') or 'gemini-2.5-flash-preview')
    )
    if not model_name.startswith('gemini/'):
        model_name = f'gemini/{model_name}'
    api_key = getattr(settings, 'google_api_key', None)
    if not api_key:
        return None
    return LLM(model=model_name, api_key=api_key, temperature=0.1, max_tokens=500)


def deterministic_render_result(
    *,
    deterministic_answer: str,
    validation_stack: list[str] | None = None,
    judge_reason: str = 'deterministic_fast_path',
) -> dict[str, Any]:
    empty = serialize_pilot_events(None)
    return {
        'answer_text': deterministic_answer,
        'used_agentic': False,
        'deterministic_backstop_used': True,
        'event_listener': empty,
        'event_summary': empty.get('summary', {}),
        'task_trace': empty.get('task_trace', {}),
        'agent_roles': [],
        'task_names': [],
        'judge': RenderedJudge(valid=True, reason=judge_reason).model_dump(mode='json'),
        'validation_stack': validation_stack or ['operation_result', 'deterministic_fast_path'],
        'crewai_version': getattr(crewai_pkg, '__version__', None),
    }


async def maybe_render_agentic_response(
    *,
    slice_name: str,
    settings: Any,
    user_message: str,
    deterministic_answer: str,
    instructions: str,
    required_anchors: list[str] | None = None,
) -> dict[str, Any]:
    llm = _build_llm(settings)
    if Crew is None or Agent is None or Task is None or Process is None or llm is None:
        return deterministic_render_result(
            deterministic_answer=deterministic_answer,
            validation_stack=['operation_result', 'deterministic_backstop'],
            judge_reason='llm_unavailable_backstop',
        )

    anchor_terms = extract_literal_anchors(deterministic_answer)
    if required_anchors:
        for item in required_anchors:
            if item and item not in anchor_terms:
                anchor_terms.append(item)

    composer = Agent(
        role=f'{slice_name} response composer',
        goal='Rewrite deterministic institutional outputs into concise, warm pt-BR answers without changing any factual detail.',
        backstory='You make operational answers feel human while preserving all literal protocol, queue, status, date, window, and ticket facts.',
        llm=llm,
        allow_delegation=False,
        verbose=False,
        max_iter=1,
    )
    judge = Agent(
        role=f'{slice_name} response judge',
        goal='Reject rewritten answers that lose or alter factual anchors from the deterministic backstop.',
        backstory='You are strict about protocol numbers, ticket ids, queue names, statuses, dates, and requested windows.',
        llm=llm,
        allow_delegation=False,
        verbose=False,
        max_iter=1,
    )
    composition_task = Task(
        name=f'{slice_name}_composition',
        description=(
            'Mensagem do usuario: {user_message}\n'
            'Resposta deterministica validada:\n{deterministic_answer}\n\n'
            f'{instructions}\n'
            'Preserve literalmente todos os codigos, datas, horarios, filas, status e canais oficiais presentes na resposta deterministica.\n'
            'Nao invente informacoes, nao remova ancoras factuais e nao acrescente detalhes nao presentes.'
        ),
        expected_output='Structured rendered answer.',
        agent=composer,
        output_pydantic=RenderedAnswer,
        guardrails=[
            require_pydantic_model(RenderedAnswer),
            require_anchor_overlap(
                model_type=RenderedAnswer,
                anchors=anchor_terms,
                allow_if_no_anchors=True,
            ),
        ],
        guardrail_max_retries=1,
    )
    judge_task = Task(
        name=f'{slice_name}_judging',
        description=(
            'Pergunta do usuario: {user_message}\n'
            'Resposta deterministica validada:\n{deterministic_answer}\n'
            'Use a resposta reescrita produzida na task anterior como contexto principal desta validacao.\n\n'
            'Marque valid=false se a resposta reescrita perder ou alterar qualquer ancora factual da resposta deterministica.'
        ),
        expected_output='Structured rendered judge.',
        agent=judge,
        context=[composition_task],
        output_pydantic=RenderedJudge,
        guardrails=[
            require_pydantic_model(RenderedJudge),
            require_nonempty_reason_when_invalid(RenderedJudge),
        ],
        guardrail_max_retries=1,
    )
    crew = Crew(
        name=f'eduassist_{slice_name}_renderer',
        agents=[composer, judge],
        tasks=[composition_task, judge_task],
        process=Process.sequential,
        verbose=False,
        cache=False,
        memory=False,
        tracing=False,
    )

    with capture_pilot_events(slice_name) as event_recorder:
        with suppress_crewai_tracing_messages():
            await asyncio.to_thread(
                crew.kickoff,
                inputs={
                    'user_message': user_message,
                    'deterministic_answer': deterministic_answer,
                },
            )

    answer = getattr(getattr(composition_task, 'output', None), 'pydantic', None)
    verdict = getattr(getattr(judge_task, 'output', None), 'pydantic', None)
    event_listener = serialize_pilot_events(event_recorder)
    answer_text = deterministic_answer
    backstop_used = True
    if isinstance(answer, RenderedAnswer) and isinstance(verdict, RenderedJudge) and verdict.valid:
        answer_text = answer.answer_text
        backstop_used = False

    return {
        'answer_text': answer_text,
        'used_agentic': True,
        'deterministic_backstop_used': backstop_used,
        'event_listener': event_listener,
        'event_summary': event_listener.get('summary', {}),
        'task_trace': event_listener.get('task_trace', {}),
        'agent_roles': ['composer', 'judge'],
        'task_names': [f'{slice_name}_composition', f'{slice_name}_judging'],
        'judge': verdict.model_dump(mode='json') if isinstance(verdict, RenderedJudge) else RenderedJudge(valid=True, reason='renderer_fallback').model_dump(mode='json'),
        'validation_stack': ['flow_state', 'operation_result', 'pydantic_output', 'task_guardrail', 'judge', 'deterministic_backstop'],
        'crewai_version': getattr(crewai_pkg, '__version__', None),
    }
