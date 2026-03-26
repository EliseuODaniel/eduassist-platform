from __future__ import annotations

import asyncio
import json
from time import perf_counter
from typing import Any

import httpx
from pydantic import BaseModel, Field

try:
    import crewai as crewai_pkg  # type: ignore
    from crewai import Agent, Crew, LLM, Process, Task  # type: ignore
except Exception:  # pragma: no cover - defensive import
    crewai_pkg = None  # type: ignore[assignment]
    Agent = Crew = LLM = Process = Task = None  # type: ignore[assignment]


class PublicPilotPlan(BaseModel):
    intent: str = Field(min_length=1)
    entity: str = Field(default='school')
    attribute: str = Field(default='general')
    needs_clarification: bool = False
    clarification_question: str | None = None
    relevant_sources: list[str] = Field(default_factory=list)


class PublicPilotAnswer(BaseModel):
    answer_text: str = Field(min_length=1)
    citations: list[str] = Field(default_factory=list)


class PublicPilotJudge(BaseModel):
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


async def _fetch_public_evidence(settings: Any) -> dict[str, Any]:
    base_url = str(getattr(settings, 'api_core_url', 'http://api-core:8000')).rstrip('/')
    async with httpx.AsyncClient(timeout=15.0) as client:
        responses = await asyncio.gather(
            client.get(f'{base_url}/v1/public/school-profile'),
            client.get(f'{base_url}/v1/public/org-directory'),
            client.get(f'{base_url}/v1/public/timeline'),
            client.get(f'{base_url}/v1/calendar/public'),
        )
    payloads: dict[str, Any] = {}
    names = ('school_profile', 'org_directory', 'timeline', 'calendar_events')
    for name, response in zip(names, responses, strict=True):
        response.raise_for_status()
        payloads[name] = response.json()
    return payloads


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
    return LLM(
        model=model_name,
        api_key=api_key,
        temperature=0.15,
        max_tokens=700,
    )


def _extract_task_pydantic(task: Any, model_type: type[BaseModel]) -> BaseModel | None:
    output = getattr(task, 'output', None)
    candidate = getattr(output, 'pydantic', None)
    if isinstance(candidate, model_type):
        return candidate
    return None


async def run_public_crewai_pilot(
    *,
    message: str,
    conversation_id: str | None,
    telegram_chat_id: int | None,
    channel: str,
    settings: Any,
) -> dict[str, Any]:
    normalized_message = ' '.join(message.strip().lower().split())
    if Crew is None or Agent is None or Task is None or Process is None:
        return {
            'engine_name': 'crewai',
            'executed': False,
            'reason': 'crewai_dependency_unavailable',
            'metadata': {
                'slice_name': 'public',
                'normalized_message': normalized_message,
            },
        }

    llm = _build_llm(settings)
    if llm is None:
        return {
            'engine_name': 'crewai',
            'executed': False,
            'reason': 'crewai_llm_not_configured',
            'metadata': {
                'slice_name': 'public',
                'normalized_message': normalized_message,
            },
        }

    evidence = await _fetch_public_evidence(settings)
    evidence_bundle = json.dumps(evidence, ensure_ascii=False, indent=2)

    planner = Agent(
        role='Public question planner',
        goal='Identify the exact public-school intent, entity, and attribute the user asked about using only the provided evidence bundle.',
        backstory='You normalize public school questions into a grounded plan before any answer is written.',
        llm=llm,
        allow_delegation=False,
        verbose=False,
        max_iter=1,
    )
    composer = Agent(
        role='Grounded answer composer',
        goal='Write a concise, warm, human answer in pt-BR using only the supported public evidence and the planner context.',
        backstory='You avoid robotic wording, adjacent-domain leakage, and unsupported claims.',
        llm=llm,
        allow_delegation=False,
        verbose=False,
        max_iter=1,
    )
    judge = Agent(
        role='Answer quality judge',
        goal='Check whether the composed answer actually addressed the asked attribute with the right entity and stayed within the evidence.',
        backstory='You reject answers that sound plausible but answer a neighboring question.',
        llm=llm,
        allow_delegation=False,
        verbose=False,
        max_iter=1,
    )

    planning_task = Task(
        name='public_planning',
        description=(
            'Pergunta do usuario: {message}\n'
            'Bundle de evidencias publicas:\n{evidence_bundle}\n\n'
            'Retorne um plano estruturado com a intencao principal, entidade, atributo, se precisa de esclarecimento e as fontes mais relevantes.'
        ),
        expected_output='Structured public plan.',
        agent=planner,
        output_pydantic=PublicPilotPlan,
    )
    composition_task = Task(
        name='public_composition',
        description=(
            'Com base na pergunta do usuario, no plano estruturado e nas evidencias publicas, escreva uma resposta curta, natural e calorosa em portugues do Brasil.\n'
            'Nunca invente fatos. Se a informacao nao estiver publicada, diga isso claramente e ofereca o proximo canal adequado.'
        ),
        expected_output='Structured public answer.',
        agent=composer,
        context=[planning_task],
        output_pydantic=PublicPilotAnswer,
    )
    judge_task = Task(
        name='public_judging',
        description=(
            'Revise o plano e a resposta final. Marque como invalida qualquer resposta que troque entidade, atributo ou use um dado nao suportado.\n'
            'Se estiver boa, marque valid=true.'
        ),
        expected_output='Structured judge result.',
        agent=judge,
        context=[planning_task, composition_task],
        output_pydantic=PublicPilotJudge,
    )

    crew = Crew(
        name='eduassist_public_shadow',
        agents=[planner, composer, judge],
        tasks=[planning_task, composition_task, judge_task],
        process=Process.sequential,
        verbose=False,
        cache=False,
        memory=False,
        tracing=False,
    )

    started_at = perf_counter()
    await asyncio.to_thread(
        crew.kickoff,
        inputs={
            'message': message,
            'evidence_bundle': evidence_bundle,
        },
    )
    latency_ms = round((perf_counter() - started_at) * 1000, 1)

    plan = _extract_task_pydantic(planning_task, PublicPilotPlan)
    answer = _extract_task_pydantic(composition_task, PublicPilotAnswer)
    verdict = _extract_task_pydantic(judge_task, PublicPilotJudge)

    metadata: dict[str, Any] = {
        'conversation_id': conversation_id or (
            f'telegram:{telegram_chat_id}' if channel == 'telegram' and telegram_chat_id is not None else None
        ),
        'slice_name': 'public',
        'normalized_message': normalized_message,
        'crewai_installed': True,
        'crewai_version': getattr(crewai_pkg, '__version__', None),
        'agent_roles': ['planner', 'composer', 'judge'],
        'task_names': ['public_planning', 'public_composition', 'public_judging'],
        'latency_ms': latency_ms,
        'plan': plan.model_dump(mode='json') if isinstance(plan, PublicPilotPlan) else None,
        'answer': answer.model_dump(mode='json') if isinstance(answer, PublicPilotAnswer) else None,
        'judge': verdict.model_dump(mode='json') if isinstance(verdict, PublicPilotJudge) else None,
        'evidence_sources': list(evidence.keys()),
    }

    if isinstance(verdict, PublicPilotJudge) and not verdict.valid:
        return {
            'engine_name': 'crewai',
            'executed': True,
            'reason': 'crewai_public_pilot_judge_invalid',
            'metadata': metadata,
        }

    return {
        'engine_name': 'crewai',
        'executed': True,
        'reason': 'crewai_public_pilot_completed',
        'metadata': metadata,
    }
