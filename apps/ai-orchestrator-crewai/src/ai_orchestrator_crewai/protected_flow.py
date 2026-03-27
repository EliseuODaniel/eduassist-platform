from __future__ import annotations

import asyncio
from time import perf_counter
from typing import Any

from pydantic import BaseModel, Field

try:
    import crewai as crewai_pkg  # type: ignore
    from crewai import Agent, Crew, Process, Task  # type: ignore
    from crewai.flow.flow import Flow, listen, router, start  # type: ignore
except Exception:  # pragma: no cover - defensive import
    crewai_pkg = None  # type: ignore[assignment]
    Agent = Crew = Process = Task = Flow = None  # type: ignore[assignment]
    listen = router = start = None  # type: ignore[assignment]

from .listeners import capture_pilot_events, serialize_pilot_events
from .protected_pilot import (
    EvidenceDoc,
    ProtectedPilotAnswer,
    ProtectedPilotJudge,
    ProtectedPilotPlan,
    _auth_required_backstop,
    _build_llm,
    _build_protected_docs,
    _conversation_state_key,
    _extract_unmatched_student_reference,
    _fetch_protected_evidence,
    _identity_backstop,
    _is_explicit_student_selection_message,
    _is_identity_scope_query,
    _is_student_focus_repair,
    _load_actor_context,
    _load_recent_student_name,
    _rank_docs,
    _requires_student,
    _resolve_student,
    _serialize_docs,
    _store_recent_student_name,
    _student_backstop,
    _student_focus_backstop,
)


class ProtectedFlowState(BaseModel):
    message: str = ''
    conversation_id: str | None = None
    telegram_chat_id: int | None = None
    channel: str = 'telegram'
    normalized_message: str = ''
    routing_label: str = 'prepare'
    reason: str = ''
    resolved_student_name: str | None = None
    evidence_source_ids: list[str] = Field(default_factory=list)
    plan: ProtectedPilotPlan | None = None
    answer: ProtectedPilotAnswer | None = None
    judge: ProtectedPilotJudge | None = None
    deterministic_backstop_used: bool = False
    latency_ms: float = 0.0


class ProtectedShadowFlow(Flow[ProtectedFlowState]):
    def __init__(self, *, settings: Any) -> None:
        self.settings = settings
        self._overall_started_at = perf_counter()
        self._actor_context: dict[str, Any] | None = None
        self._actor: dict[str, Any] | None = None
        self._student: dict[str, Any] | None = None
        self._state_key: str | None = None
        self._shortlisted_docs: list[EvidenceDoc] = []
        self._identity_backstop_text: str | None = None
        self._llm: Any = None
        super().__init__(tracing=False)

    @start()
    async def prepare_context(self) -> str:
        self._overall_started_at = perf_counter()
        self.state.normalized_message = ' '.join(self.state.message.strip().lower().split())
        if Crew is None or Agent is None or Task is None or Process is None or Flow is None:
            self.state.routing_label = 'dependency_unavailable'
            self.state.reason = 'crewai_dependency_unavailable'
            return self.state.routing_label

        if self.state.telegram_chat_id is None:
            self.state.routing_label = 'auth_required'
            self.state.reason = 'missing_telegram_chat_id'
            return self.state.routing_label

        self._actor_context = await _load_actor_context(self.settings, self.state.telegram_chat_id)
        self._actor = self._actor_context.get('actor') if isinstance(self._actor_context, dict) else None
        if not isinstance(self._actor, dict) or not self._actor:
            self.state.routing_label = 'auth_required'
            self.state.reason = 'actor_context_missing'
            return self.state.routing_label

        self._state_key = _conversation_state_key(
            conversation_id=self.state.conversation_id,
            telegram_chat_id=self.state.telegram_chat_id,
            channel=self.state.channel,
        )
        recent_student_name = _load_recent_student_name(self._state_key)
        self._student = _resolve_student(self._actor, self.state.message, recent_student_name=recent_student_name)
        self.state.resolved_student_name = self._student.get('full_name') if isinstance(self._student, dict) else None

        self._identity_backstop_text = _identity_backstop(self._actor, self.state.message)
        if self._identity_backstop_text and _is_identity_scope_query(self.state.message):
            self.state.routing_label = 'identity_backstop'
            self.state.reason = 'crewai_protected_identity_backstop'
            return self.state.routing_label

        student_focus_answer = _student_focus_backstop(self.state.message, self._student)
        if _is_explicit_student_selection_message(self.state.message, self.state.resolved_student_name) and student_focus_answer:
            self.state.routing_label = 'student_selection'
            self.state.reason = 'protected_shadow_student_selection'
            return self.state.routing_label
        if _is_student_focus_repair(self.state.message, self.state.resolved_student_name) and student_focus_answer:
            self.state.routing_label = 'student_focus_repair'
            self.state.reason = 'protected_shadow_student_focus_repair'
            return self.state.routing_label

        unmatched_student_reference = _extract_unmatched_student_reference(self._actor, self.state.message)
        if unmatched_student_reference:
            self.state.routing_label = 'unmatched_student_reference'
            self.state.reason = unmatched_student_reference
            return self.state.routing_label

        if _requires_student(self.state.message) and self._student is None and len(self._actor.get('linked_students', []) or []) > 1:
            self.state.routing_label = 'needs_student_clarification'
            self.state.reason = 'student_clarification_required'
            return self.state.routing_label

        evidence = await _fetch_protected_evidence(
            settings=self.settings,
            actor_context=self._actor_context,
            student=self._student,
            telegram_chat_id=self.state.telegram_chat_id,
        )
        docs = _build_protected_docs(evidence)
        self._shortlisted_docs = _rank_docs(self.state.message, docs)
        self.state.evidence_source_ids = [doc.doc_id for doc in self._shortlisted_docs]

        fast_path_answer = self._identity_backstop_text or _student_backstop(self.state.message, self._student, evidence, self._shortlisted_docs)
        if isinstance(fast_path_answer, str) and fast_path_answer.strip():
            self.state.answer = ProtectedPilotAnswer(
                answer_text=fast_path_answer,
                citations=[self._shortlisted_docs[0].doc_id] if self._shortlisted_docs else [],
            )
            self.state.judge = ProtectedPilotJudge(valid=True, reason='deterministic_fast_path', revision_needed=False)
            self.state.routing_label = 'fast_path'
            self.state.reason = 'crewai_protected_fast_path'
            return self.state.routing_label

        self._llm = _build_llm(self.settings)
        if self._llm is None:
            self.state.routing_label = 'llm_unavailable'
            self.state.reason = 'crewai_llm_not_configured'
            return self.state.routing_label

        self.state.routing_label = 'agentic'
        self.state.reason = 'crewai_protected_flow_agentic'
        return self.state.routing_label

    @router(prepare_context)
    def route(self) -> str:
        return self.state.routing_label

    def _base_metadata(self) -> dict[str, Any]:
        return {
            'conversation_id': self.state.conversation_id or f'telegram:{self.state.telegram_chat_id}',
            'slice_name': 'protected',
            'normalized_message': self.state.normalized_message,
            'resolved_student_name': self.state.resolved_student_name,
            'flow_enabled': True,
            'flow_state_id': getattr(self.state, 'id', None),
        }

    @listen('dependency_unavailable')
    def handle_dependency_unavailable(self) -> dict[str, Any]:
        return {
            'engine_name': 'crewai',
            'executed': False,
            'reason': self.state.reason,
            'metadata': self._base_metadata(),
        }

    @listen('auth_required')
    def handle_auth_required(self) -> dict[str, Any]:
        answer = ProtectedPilotAnswer(
            answer_text=_auth_required_backstop(),
        )
        judge = ProtectedPilotJudge(valid=True, reason='auth_required_deterministic', revision_needed=False)
        return {
            'engine_name': 'crewai',
            'executed': True,
            'reason': 'crewai_protected_auth_required',
            'metadata': {
                **self._base_metadata(),
                'answer': answer.model_dump(mode='json'),
                'judge': judge.model_dump(mode='json'),
                'deterministic_backstop_used': True,
                'validation_stack': ['flow_router', 'auth_required_deterministic'],
            },
        }

    @listen('identity_backstop')
    def handle_identity_backstop(self) -> dict[str, Any]:
        answer = ProtectedPilotAnswer(answer_text=str(self._identity_backstop_text or ''))
        judge = ProtectedPilotJudge(valid=True, reason='identity_scope_handled_deterministically', revision_needed=False)
        return {
            'engine_name': 'crewai',
            'executed': True,
            'reason': 'crewai_protected_identity_backstop',
            'metadata': {
                **self._base_metadata(),
                'answer': answer.model_dump(mode='json'),
                'judge': judge.model_dump(mode='json'),
                'deterministic_backstop_used': True,
                'validation_stack': ['flow_router', 'identity_backstop'],
            },
        }

    @listen('student_selection')
    def handle_student_selection(self) -> dict[str, Any]:
        answer = ProtectedPilotAnswer(answer_text=_student_focus_backstop(self.state.message, self._student) or '')
        judge = ProtectedPilotJudge(valid=True, reason='student_selection_handled_deterministically', revision_needed=False)
        if self._state_key:
            _store_recent_student_name(self._state_key, self.state.resolved_student_name)
        return {
            'engine_name': 'crewai',
            'executed': True,
            'reason': 'protected_shadow_student_selection',
            'metadata': {
                **self._base_metadata(),
                'answer': answer.model_dump(mode='json'),
                'judge': judge.model_dump(mode='json'),
                'deterministic_backstop_used': True,
                'validation_stack': ['flow_router', 'student_selection'],
            },
        }

    @listen('student_focus_repair')
    def handle_student_focus_repair(self) -> dict[str, Any]:
        answer = ProtectedPilotAnswer(answer_text=_student_focus_backstop(self.state.message, self._student) or '')
        judge = ProtectedPilotJudge(valid=True, reason='student_focus_repair_handled_deterministically', revision_needed=False)
        if self._state_key:
            _store_recent_student_name(self._state_key, self.state.resolved_student_name)
        return {
            'engine_name': 'crewai',
            'executed': True,
            'reason': 'protected_shadow_student_focus_repair',
            'metadata': {
                **self._base_metadata(),
                'answer': answer.model_dump(mode='json'),
                'judge': judge.model_dump(mode='json'),
                'deterministic_backstop_used': True,
                'validation_stack': ['flow_router', 'student_focus_repair'],
            },
        }

    @listen('unmatched_student_reference')
    def handle_unmatched_student_reference(self) -> dict[str, Any]:
        names = ', '.join(
            str(item.get('full_name', ''))
            for item in self._actor.get('linked_students', [])
            if isinstance(item, dict)
        ) if isinstance(self._actor, dict) else ''
        answer = ProtectedPilotAnswer(
            answer_text=(
                f'Hoje eu nao encontrei {self.state.reason.title()} entre os alunos vinculados a esta conta. '
                f'No momento, os alunos que aparecem aqui sao: {names}. '
                'Se quiser, me diga qual deles voce quer consultar.'
            ),
        )
        judge = ProtectedPilotJudge(valid=True, reason='unmatched_student_handled_deterministically', revision_needed=False)
        return {
            'engine_name': 'crewai',
            'executed': True,
            'reason': 'protected_shadow_unmatched_student_reference',
            'metadata': {
                **self._base_metadata(),
                'answer': answer.model_dump(mode='json'),
                'judge': judge.model_dump(mode='json'),
                'deterministic_backstop_used': True,
                'validation_stack': ['flow_router', 'unmatched_student_reference'],
            },
        }

    @listen('needs_student_clarification')
    def handle_needs_student_clarification(self) -> dict[str, Any]:
        names = ', '.join(
            str(item.get('full_name', ''))
            for item in self._actor.get('linked_students', [])
            if isinstance(item, dict)
        ) if isinstance(self._actor, dict) else ''
        answer = ProtectedPilotAnswer(answer_text=f'Posso te ajudar com {names}. Me diga qual aluno voce quer consultar.')
        judge = ProtectedPilotJudge(valid=True, reason='student_clarification_required', revision_needed=False)
        return {
            'engine_name': 'crewai',
            'executed': True,
            'reason': 'protected_shadow_needs_student_clarification',
            'metadata': {
                **self._base_metadata(),
                'answer': answer.model_dump(mode='json'),
                'judge': judge.model_dump(mode='json'),
                'deterministic_backstop_used': True,
                'validation_stack': ['flow_router', 'student_clarification'],
            },
        }

    @listen('fast_path')
    def handle_fast_path(self) -> dict[str, Any]:
        self.state.latency_ms = round((perf_counter() - self._overall_started_at) * 1000, 1)
        if self._state_key:
            _store_recent_student_name(self._state_key, self.state.resolved_student_name)
        return {
            'engine_name': 'crewai',
            'executed': True,
            'reason': 'crewai_protected_fast_path',
            'metadata': {
                **self._base_metadata(),
                'crewai_installed': True,
                'crewai_version': getattr(crewai_pkg, '__version__', None),
                'agent_roles': [],
                'task_names': [],
                'latency_ms': self.state.latency_ms,
                'plan': None,
                'answer': self.state.answer.model_dump(mode='json') if isinstance(self.state.answer, ProtectedPilotAnswer) else None,
                'judge': self.state.judge.model_dump(mode='json') if isinstance(self.state.judge, ProtectedPilotJudge) else None,
                'evidence_sources': list(self.state.evidence_source_ids),
                'deterministic_backstop_used': True,
                'validation_stack': ['flow_router', 'deterministic_fast_path'],
            },
        }

    @listen('llm_unavailable')
    def handle_llm_unavailable(self) -> dict[str, Any]:
        return {
            'engine_name': 'crewai',
            'executed': False,
            'reason': self.state.reason,
            'metadata': self._base_metadata(),
        }

    @listen('agentic')
    async def handle_agentic(self) -> dict[str, Any]:
        evidence = await _fetch_protected_evidence(
            settings=self.settings,
            actor_context=self._actor_context,
            student=self._student,
            telegram_chat_id=self.state.telegram_chat_id,
        )
        if not self._shortlisted_docs:
            docs = _build_protected_docs(evidence)
            self._shortlisted_docs = _rank_docs(self.state.message, docs)
            self.state.evidence_source_ids = [doc.doc_id for doc in self._shortlisted_docs]
        evidence_bundle = _serialize_docs(self._shortlisted_docs)

        planner = Agent(
            role='Protected question planner',
            goal='Resolve the protected intent, student scope, and attribute using only the shortlisted protected docs.',
            backstory='You plan protected school-support answers carefully and must not leak data between students.',
            llm=self._llm,
            allow_delegation=False,
            verbose=False,
            max_iter=1,
        )
        composer = Agent(
            role='Protected grounded composer',
            goal='Compose a short, human, precise answer in pt-BR using only the shortlisted protected docs.',
            backstory='You never mix students, invent values, or answer outside the linked account scope.',
            llm=self._llm,
            allow_delegation=False,
            verbose=False,
            max_iter=1,
        )
        judge = Agent(
            role='Protected answer judge',
            goal='Reject answers that switch student, actor, amount, enrollment, dates, or statuses beyond the protected docs.',
            backstory='You are strict about entity safety and scope.',
            llm=self._llm,
            allow_delegation=False,
            verbose=False,
            max_iter=1,
        )

        planning_task = Task(
            name='protected_planning',
            description=(
                'Pergunta do usuario: {message}\n'
                'Docs protegidos mais relevantes:\n{evidence_bundle}\n\n'
                'Retorne um plano estruturado com intencao, aluno, dominio, atributo, se precisa de esclarecimento e ids das fontes relevantes.'
            ),
            expected_output='Structured protected plan.',
            agent=planner,
            output_pydantic=ProtectedPilotPlan,
        )
        composition_task = Task(
            name='protected_composition',
            description=(
                'Com base na pergunta do usuario, no plano e nos docs protegidos, responda em pt-BR de forma curta e humana.\n'
                'Nunca misture alunos. Nunca invente notas, faltas, valores, codigos ou datas.'
            ),
            expected_output='Structured protected answer.',
            agent=composer,
            context=[planning_task],
            output_pydantic=ProtectedPilotAnswer,
        )
        judge_task = Task(
            name='protected_judging',
            description=(
                'Revise o plano e a resposta final. Marque como invalida qualquer resposta que troque aluno, ator, codigo, valor, data ou status.'
            ),
            expected_output='Structured protected judge result.',
            agent=judge,
            context=[planning_task, composition_task],
            output_pydantic=ProtectedPilotJudge,
        )

        crew = Crew(
            name='eduassist_protected_shadow_flow',
            agents=[planner, composer, judge],
            tasks=[planning_task, composition_task, judge_task],
            process=Process.sequential,
            verbose=False,
            cache=False,
            memory=False,
            tracing=False,
        )

        with capture_pilot_events('protected') as event_recorder:
            await asyncio.to_thread(crew.kickoff, inputs={'message': self.state.message, 'evidence_bundle': evidence_bundle})

        self.state.latency_ms = round((perf_counter() - self._overall_started_at) * 1000, 1)
        plan = getattr(planning_task.output, 'pydantic', None)
        answer = getattr(composition_task.output, 'pydantic', None)
        verdict = getattr(judge_task.output, 'pydantic', None)

        backstop_answer = self._identity_backstop_text or _student_backstop(self.state.message, self._student, evidence, self._shortlisted_docs)
        backstop_used = False
        if isinstance(backstop_answer, str) and backstop_answer.strip():
            answer = ProtectedPilotAnswer(
                answer_text=backstop_answer,
                citations=[self._shortlisted_docs[0].doc_id] if self._shortlisted_docs else [],
            )
            verdict = ProtectedPilotJudge(valid=True, reason='deterministic_backstop_applied', revision_needed=False)
            backstop_used = True

        self.state.plan = plan if isinstance(plan, ProtectedPilotPlan) else None
        self.state.answer = answer if isinstance(answer, ProtectedPilotAnswer) else None
        self.state.judge = verdict if isinstance(verdict, ProtectedPilotJudge) else None
        self.state.deterministic_backstop_used = backstop_used
        if self._state_key:
            _store_recent_student_name(self._state_key, self.state.resolved_student_name)

        return {
            'engine_name': 'crewai',
            'executed': True,
            'reason': 'crewai_protected_flow_completed',
            'metadata': {
                **self._base_metadata(),
                'crewai_installed': True,
                'crewai_version': getattr(crewai_pkg, '__version__', None),
                'agent_roles': ['planner', 'composer', 'judge'],
                'task_names': ['protected_planning', 'protected_composition', 'protected_judging'],
                'latency_ms': self.state.latency_ms,
                'plan': self.state.plan.model_dump(mode='json') if isinstance(self.state.plan, ProtectedPilotPlan) else None,
                'answer': self.state.answer.model_dump(mode='json') if isinstance(self.state.answer, ProtectedPilotAnswer) else None,
                'judge': self.state.judge.model_dump(mode='json') if isinstance(self.state.judge, ProtectedPilotJudge) else None,
                'evidence_sources': list(self.state.evidence_source_ids),
                'deterministic_backstop_used': backstop_used,
                'validation_stack': ['flow_state', 'pydantic_output', 'judge', 'deterministic_backstop'],
                'event_listener': serialize_pilot_events(event_recorder),
            },
        }
