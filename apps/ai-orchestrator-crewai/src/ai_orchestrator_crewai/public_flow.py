from __future__ import annotations

import asyncio
from time import perf_counter
from typing import Any

from pydantic import BaseModel, Field

try:
    import crewai as crewai_pkg  # type: ignore
    from crewai import Agent, Crew, Process, Task  # type: ignore
    from crewai.flow.flow import Flow, listen, router, start  # type: ignore
    from crewai.flow.persistence import persist  # type: ignore
except Exception:  # pragma: no cover - defensive import
    crewai_pkg = None  # type: ignore[assignment]
    Agent = Crew = Process = Task = Flow = None  # type: ignore[assignment]
    listen = router = start = None  # type: ignore[assignment]
    persist = None  # type: ignore[assignment]

from .flow_persistence import build_flow_state_id, get_sqlite_flow_persistence
from .guardrails import (
    extract_literal_anchors,
    require_anchor_overlap,
    require_answer_citations_subset,
    require_nonempty_reason_when_invalid,
    require_pydantic_model,
    require_sources_subset,
)
from .listeners import capture_pilot_events, serialize_pilot_events
from .public_pilot import (
    EvidenceDoc,
    PublicPilotAnswer,
    PublicPilotJudge,
    PublicPilotPlan,
    _augment_public_message_with_state,
    _answer_conflicts_with_backstop,
    _build_evidence_docs,
    _build_llm,
    _deterministic_backstop,
    _direct_contact_fast_answer,
    _direct_capabilities_fast_answer,
    _direct_feature_fast_answer,
    _direct_greeting_fast_answer,
    _extract_task_pydantic,
    _fetch_public_evidence,
    _infer_public_followup_slots,
    _is_public_fast_path_query,
    _query_terms,
    _rank_evidence_docs,
    _select_primary_doc,
    _serialize_evidence_pack,
    _stateful_public_followup_fast_answer,
)


class PublicFlowState(BaseModel):
    id: str | None = None
    message: str = ''
    conversation_id: str | None = None
    telegram_chat_id: int | None = None
    channel: str = 'telegram'
    normalized_message: str = ''
    routing_label: str = 'prepare'
    reason: str = ''
    effective_message: str = ''
    fast_path_answer: str | None = None
    evidence_source_ids: list[str] = Field(default_factory=list)
    plan: PublicPilotPlan | None = None
    answer: PublicPilotAnswer | None = None
    judge: PublicPilotJudge | None = None
    deterministic_backstop_used: bool = False
    active_entity: str | None = None
    active_attribute: str | None = None
    latency_ms: float = 0.0


def _public_flow_decorator(target: type[Flow[PublicFlowState]]) -> type[Flow[PublicFlowState]]:
    if persist is None:
        return target
    persistence = get_sqlite_flow_persistence('public')
    if persistence is None:
        return target
    return persist(persistence=persistence, verbose=False)(target)


@_public_flow_decorator
class PublicShadowFlow(Flow[PublicFlowState]):
    def __init__(self, *, settings: Any, persistence: Any | None = None) -> None:
        self.settings = settings
        self._overall_started_at = perf_counter()
        self._evidence_docs: list[EvidenceDoc] = []
        self._shortlisted_docs: list[EvidenceDoc] = []
        self._llm: Any = None
        super().__init__(persistence=persistence, tracing=False)

    @start()
    async def prepare_context(self) -> str:
        self._overall_started_at = perf_counter()
        self.state.normalized_message = ' '.join(self.state.message.strip().lower().split())
        self.state.effective_message = _augment_public_message_with_state(
            self.state.message,
            active_entity=self.state.active_entity,
            active_attribute=self.state.active_attribute,
        )
        ranking_message = self.state.effective_message or self.state.message
        if Crew is None or Agent is None or Task is None or Process is None or Flow is None:
            self.state.routing_label = 'dependency_unavailable'
            self.state.reason = 'crewai_dependency_unavailable'
            return self.state.routing_label

        evidence = await _fetch_public_evidence(self.settings)
        self._evidence_docs = _build_evidence_docs(evidence)
        self._shortlisted_docs = _rank_evidence_docs(ranking_message, self._evidence_docs)
        self.state.evidence_source_ids = [doc.doc_id for doc in self._shortlisted_docs]

        fast_path_answer = (
            _stateful_public_followup_fast_answer(
                self.state.message,
                active_entity=self.state.active_entity,
                docs=self._evidence_docs,
            )
            or _direct_greeting_fast_answer(self.state.effective_message)
            or _direct_capabilities_fast_answer(self.state.effective_message)
            or _direct_contact_fast_answer(self.state.effective_message, self._evidence_docs)
            or _direct_contact_fast_answer(self.state.effective_message, self._shortlisted_docs)
            or _direct_feature_fast_answer(self.state.effective_message, self._evidence_docs)
            or _direct_feature_fast_answer(self.state.effective_message, self._shortlisted_docs)
            or _deterministic_backstop(self.state.effective_message, None, self._evidence_docs)
            or _deterministic_backstop(self.state.effective_message, None, self._shortlisted_docs)
        )
        if isinstance(fast_path_answer, str) and fast_path_answer.strip() and _is_public_fast_path_query(self.state.effective_message):
            self.state.fast_path_answer = fast_path_answer
            self.state.routing_label = 'fast_path'
            self.state.reason = 'crewai_public_fast_path'
            return self.state.routing_label

        self._llm = _build_llm(self.settings)
        if self._llm is None:
            self.state.routing_label = 'llm_unavailable'
            self.state.reason = 'crewai_llm_not_configured'
            return self.state.routing_label

        self.state.routing_label = 'agentic'
        self.state.reason = 'crewai_public_flow_agentic'
        return self.state.routing_label

    @router(prepare_context)
    def route(self) -> str:
        return self.state.routing_label

    @listen('dependency_unavailable')
    def handle_dependency_unavailable(self) -> dict[str, Any]:
        empty_event_telemetry = serialize_pilot_events(None)
        return {
            'engine_name': 'crewai',
            'executed': False,
            'reason': self.state.reason,
            'metadata': {
                'conversation_id': self.state.conversation_id,
                'slice_name': 'public',
                'normalized_message': self.state.normalized_message,
                'flow_enabled': True,
                'flow_state_id': getattr(self.state, 'id', None),
                'event_listener': empty_event_telemetry,
                'event_summary': empty_event_telemetry.get('summary', {}),
                'task_trace': empty_event_telemetry.get('task_trace', {}),
            },
        }

    @listen('llm_unavailable')
    def handle_llm_unavailable(self) -> dict[str, Any]:
        empty_event_telemetry = serialize_pilot_events(None)
        return {
            'engine_name': 'crewai',
            'executed': False,
            'reason': self.state.reason,
            'metadata': {
                'conversation_id': self.state.conversation_id,
                'slice_name': 'public',
                'normalized_message': self.state.normalized_message,
                'flow_enabled': True,
                'flow_state_id': getattr(self.state, 'id', None),
                'event_listener': empty_event_telemetry,
                'event_summary': empty_event_telemetry.get('summary', {}),
                'task_trace': empty_event_telemetry.get('task_trace', {}),
            },
        }

    @listen('fast_path')
    def handle_fast_path(self) -> dict[str, Any]:
        self.state.latency_ms = round((perf_counter() - self._overall_started_at) * 1000, 1)
        inferred_entity, inferred_attribute = _infer_public_followup_slots(
            self.state.effective_message or self.state.message,
            str(self.state.fast_path_answer or ''),
        )
        if inferred_entity:
            self.state.active_entity = inferred_entity
        if inferred_attribute:
            self.state.active_attribute = inferred_attribute
        answer = PublicPilotAnswer(
            answer_text=str(self.state.fast_path_answer or ''),
            citations=[self._shortlisted_docs[0].doc_id] if self._shortlisted_docs else [],
        )
        judge = PublicPilotJudge(valid=True, reason='deterministic_fast_path', revision_needed=False)
        empty_event_telemetry = serialize_pilot_events(None)
        self.state.answer = answer
        self.state.judge = judge
        self.state.deterministic_backstop_used = True
        return {
            'engine_name': 'crewai',
            'executed': True,
            'reason': 'crewai_public_fast_path',
            'metadata': {
                'conversation_id': self.state.conversation_id,
                'slice_name': 'public',
                'normalized_message': self.state.normalized_message,
                'crewai_installed': True,
                'crewai_version': getattr(crewai_pkg, '__version__', None),
                'agent_roles': [],
                'task_names': [],
                'latency_ms': self.state.latency_ms,
                'plan': None,
                'answer': answer.model_dump(mode='json'),
                'judge': judge.model_dump(mode='json'),
                'evidence_sources': list(self.state.evidence_source_ids),
                'deterministic_backstop_used': True,
                'validation_stack': ['flow_router', 'deterministic_fast_path'],
                'flow_enabled': True,
                'flow_state_id': getattr(self.state, 'id', None),
                'event_listener': empty_event_telemetry,
                'event_summary': empty_event_telemetry.get('summary', {}),
                'task_trace': empty_event_telemetry.get('task_trace', {}),
            },
        }

    @listen('agentic')
    async def handle_agentic(self) -> dict[str, Any]:
        evidence_bundle = _serialize_evidence_pack(self._shortlisted_docs)
        planner = Agent(
            role='Public question planner',
            goal='Identify the exact public-school intent, entity, and attribute the user asked about using only the provided shortlisted evidence docs.',
            backstory='You normalize public school questions into a grounded plan before any answer is written. You must prefer concrete source ids over generic guesses.',
            llm=self._llm,
            allow_delegation=False,
            verbose=False,
            max_iter=1,
        )
        composer = Agent(
            role='Grounded answer composer',
            goal='Write a concise, warm, human answer in pt-BR using only the shortlisted evidence docs and the planner context.',
            backstory='You avoid robotic wording, adjacent-domain leakage, and unsupported claims. When the evidence is explicit, answer directly instead of hedging.',
            llm=self._llm,
            allow_delegation=False,
            verbose=False,
            max_iter=1,
        )
        judge = Agent(
            role='Answer quality judge',
            goal='Check whether the composed answer actually addressed the asked attribute with the right entity and stayed within the evidence.',
            backstory='You reject answers that sound plausible but answer a neighboring question.',
            llm=self._llm,
            allow_delegation=False,
            verbose=False,
            max_iter=1,
        )
        anticipated_backstop = _deterministic_backstop(self.state.message, None, self._shortlisted_docs) or ''

        planning_task = Task(
            name='public_planning',
            description=(
                'Pergunta do usuario: {message}\n'
                'Docs de evidencias publicas mais relevantes:\n{evidence_bundle}\n\n'
                'Retorne um plano estruturado com a intencao principal, entidade, atributo, se precisa de esclarecimento e os ids das fontes mais relevantes.\n'
                'Use apenas os ids dos docs realmente necessarios.\n'
                'Se a pergunta pedir horario, contato, instagram, fax, matricula, inicio das aulas, biblioteca, atividades, estrutura ou endereco, escolha o atributo exato.\n'
                'Se algum doc trouxer um dado literal claro como data, horario, telefone, email, site ou instagram, prefira esse doc especifico no plano.'
            ),
            expected_output='Structured public plan.',
            agent=planner,
            output_pydantic=PublicPilotPlan,
            guardrails=[
                require_pydantic_model(PublicPilotPlan),
                require_sources_subset(
                    model_type=PublicPilotPlan,
                    field_name='relevant_sources',
                    valid_source_ids=self.state.evidence_source_ids,
                ),
            ],
            guardrail_max_retries=1,
        )
        required_public_anchors = extract_literal_anchors(anticipated_backstop)
        composition_task = Task(
            name='public_composition',
            description=(
                'Com base na pergunta do usuario, no plano estruturado e nas evidencias publicas, escreva uma resposta curta, natural e calorosa em portugues do Brasil.\n'
                'Nunca invente fatos. Se a evidencia trouxer um horario, data, nome de espaco, telefone, email, instagram, site ou valor, responda diretamente com esse dado.\n'
                'Nao invente datas aproximadas, faixas de periodo ou canais nao citados.\n'
                'Se houver uma data ou horario explicito nos docs selecionados, reproduza esse dado de forma literal na resposta.\n'
                'Se a informacao nao estiver publicada nos docs, diga isso claramente e ofereca o proximo canal adequado.'
            ),
            expected_output='Structured public answer.',
            agent=composer,
            context=[planning_task],
            output_pydantic=PublicPilotAnswer,
            guardrails=[
                require_pydantic_model(PublicPilotAnswer),
                require_answer_citations_subset(
                    model_type=PublicPilotAnswer,
                    valid_source_ids=self.state.evidence_source_ids,
                ),
                require_anchor_overlap(
                    model_type=PublicPilotAnswer,
                    anchors=required_public_anchors,
                    allow_if_no_anchors=True,
                ),
            ],
            guardrail_max_retries=1,
        )
        judge_task = Task(
            name='public_judging',
            description=(
                'Revise o plano e a resposta final. Marque como invalida qualquer resposta que troque entidade, atributo ou use um dado nao suportado pelos docs.\n'
                'Se a resposta citar uma data, horario, valor, telefone, instagram, email ou site que nao aparece explicitamente nos docs, marque valid=false.\n'
                'Se estiver boa, marque valid=true.'
            ),
            expected_output='Structured judge result.',
            agent=judge,
            context=[planning_task, composition_task],
            output_pydantic=PublicPilotJudge,
            guardrails=[
                require_pydantic_model(PublicPilotJudge),
                require_nonempty_reason_when_invalid(PublicPilotJudge),
            ],
            guardrail_max_retries=1,
        )

        crew = Crew(
            name='eduassist_public_shadow_flow',
            agents=[planner, composer, judge],
            tasks=[planning_task, composition_task, judge_task],
            process=Process.sequential,
            verbose=False,
            cache=False,
            memory=False,
            tracing=False,
        )

        with capture_pilot_events('public') as event_recorder:
            await asyncio.to_thread(
                crew.kickoff,
                inputs={
                    'message': self.state.effective_message or self.state.message,
                    'evidence_bundle': evidence_bundle,
                },
            )

        self.state.latency_ms = round((perf_counter() - self._overall_started_at) * 1000, 1)
        plan = _extract_task_pydantic(planning_task, PublicPilotPlan)
        answer = _extract_task_pydantic(composition_task, PublicPilotAnswer)
        verdict = _extract_task_pydantic(judge_task, PublicPilotJudge)
        backstop_answer = _deterministic_backstop(
            self.state.effective_message or self.state.message,
            plan if isinstance(plan, PublicPilotPlan) else None,
            self._shortlisted_docs,
        )
        backstop_used = False

        if isinstance(answer, PublicPilotAnswer) and backstop_answer:
            should_apply_backstop = _answer_conflicts_with_backstop(
                answer.answer_text,
                backstop_answer,
                self.state.effective_message or self.state.message,
            )
            if isinstance(plan, PublicPilotPlan) and plan.needs_clarification and any(
                term in _query_terms(self.state.effective_message or self.state.message)
                for term in {'telefone', 'fax', 'instagram', 'email', 'site', 'endereco'}
            ):
                should_apply_backstop = True
            if isinstance(verdict, PublicPilotJudge) and not verdict.valid:
                should_apply_backstop = True
            if should_apply_backstop:
                primary_doc = _select_primary_doc(plan if isinstance(plan, PublicPilotPlan) else None, self._shortlisted_docs)
                answer = PublicPilotAnswer(
                    answer_text=backstop_answer,
                    citations=[primary_doc.doc_id] if primary_doc else [],
                )
                verdict = PublicPilotJudge(valid=True, reason='deterministic_backstop_applied', revision_needed=False)
                backstop_used = True

        self.state.plan = plan if isinstance(plan, PublicPilotPlan) else None
        self.state.answer = answer if isinstance(answer, PublicPilotAnswer) else None
        self.state.judge = verdict if isinstance(verdict, PublicPilotJudge) else None
        self.state.deterministic_backstop_used = backstop_used
        if isinstance(self.state.plan, PublicPilotPlan):
            self.state.active_entity = self.state.plan.entity
            self.state.active_attribute = self.state.plan.attribute

        event_listener = serialize_pilot_events(event_recorder)
        metadata: dict[str, Any] = {
            'conversation_id': self.state.conversation_id,
            'slice_name': 'public',
            'normalized_message': self.state.normalized_message,
            'crewai_installed': True,
            'crewai_version': getattr(crewai_pkg, '__version__', None),
            'agent_roles': ['planner', 'composer', 'judge'],
            'task_names': ['public_planning', 'public_composition', 'public_judging'],
            'latency_ms': self.state.latency_ms,
            'plan': self.state.plan.model_dump(mode='json') if isinstance(self.state.plan, PublicPilotPlan) else None,
            'answer': self.state.answer.model_dump(mode='json') if isinstance(self.state.answer, PublicPilotAnswer) else None,
            'judge': self.state.judge.model_dump(mode='json') if isinstance(self.state.judge, PublicPilotJudge) else None,
            'evidence_sources': list(self.state.evidence_source_ids),
            'deterministic_backstop_used': backstop_used,
            'validation_stack': ['flow_state', 'pydantic_output', 'judge', 'deterministic_backstop'],
            'event_listener': event_listener,
            'event_summary': event_listener.get('summary', {}),
            'task_trace': event_listener.get('task_trace', {}),
            'flow_enabled': True,
            'flow_state_id': getattr(self.state, 'id', None),
            'flow_state_persisted': get_sqlite_flow_persistence('public') is not None,
        }

        if isinstance(self.state.judge, PublicPilotJudge) and not self.state.judge.valid:
            return {
                'engine_name': 'crewai',
                'executed': True,
                'reason': 'crewai_public_flow_judge_invalid',
                'metadata': metadata,
            }

        return {
            'engine_name': 'crewai',
            'executed': True,
            'reason': 'crewai_public_flow_completed',
            'metadata': metadata,
        }
