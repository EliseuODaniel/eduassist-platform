from __future__ import annotations

import asyncio
import logging
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
    require_answer_citations_subset,
    require_no_forbidden_entities,
    require_nonempty_reason_when_invalid,
    require_pydantic_model,
    require_sources_subset,
)
from .crewai_hitl import (
    HumanFeedbackPending,
    PendingFeedbackContext,
    async_feedback_supported,
    feedback_is_approved,
    feedback_is_rejected,
)
from .listeners import capture_pilot_events, serialize_pilot_events
from .protected_pilot import (
    EvidenceDoc,
    ProtectedPilotAnswer,
    ProtectedPilotJudge,
    ProtectedPilotPlan,
    _augment_protected_message_with_state,
    _auth_required_backstop,
    _build_llm,
    _build_protected_docs,
    _extract_unmatched_student_reference,
    _fetch_protected_evidence,
    _extract_task_pydantic,
    _infer_fast_path_plan,
    _identity_backstop,
    _is_explicit_student_selection_message,
    _is_identity_scope_query,
    _is_student_focus_repair,
    _load_actor_context,
    _rank_docs,
    _requires_student,
    _resolve_student,
    _serialize_docs,
    _student_backstop,
    _student_focus_backstop,
)

logger = logging.getLogger(__name__)


class ProtectedFlowState(BaseModel):
    id: str | None = None
    message: str = ''
    conversation_id: str | None = None
    telegram_chat_id: int | None = None
    channel: str = 'telegram'
    normalized_message: str = ''
    effective_message: str = ''
    routing_label: str = 'prepare'
    reason: str = ''
    resolved_student_name: str | None = None
    evidence_source_ids: list[str] = Field(default_factory=list)
    plan: ProtectedPilotPlan | None = None
    answer: ProtectedPilotAnswer | None = None
    judge: ProtectedPilotJudge | None = None
    deterministic_backstop_used: bool = False
    active_student_name: str | None = None
    active_domain: str | None = None
    active_attribute: str | None = None
    hitl_enabled: bool = False
    hitl_target_slices: list[str] = Field(default_factory=list)
    pending_review_required: bool = False
    post_review_route: str | None = None
    latency_ms: float = 0.0


def _protected_flow_decorator(target: type[Flow[ProtectedFlowState]]) -> type[Flow[ProtectedFlowState]]:
    if persist is None:
        return target
    persistence = get_sqlite_flow_persistence('protected')
    if persistence is None:
        return target
    return persist(persistence=persistence, verbose=False)(target)


@_protected_flow_decorator
class ProtectedShadowFlow(Flow[ProtectedFlowState]):
    def __init__(self, *, settings: Any, persistence: Any | None = None) -> None:
        self.settings = settings
        self._overall_started_at = perf_counter()
        self._actor_context: dict[str, Any] | None = None
        self._actor: dict[str, Any] | None = None
        self._student: dict[str, Any] | None = None
        self._shortlisted_docs: list[EvidenceDoc] = []
        self._identity_backstop_text: str | None = None
        self._llm: Any = None
        super().__init__(persistence=persistence, tracing=False)

    def _protected_hitl_enabled(self) -> bool:
        if not self.state.hitl_enabled:
            return False
        targets = {str(item or '').strip().lower() for item in (self.state.hitl_target_slices or ['protected']) if str(item or '').strip()}
        return 'protected' in targets or not targets

    def _queue_human_review(self, *, next_route: str, reason: str) -> str:
        self.state.pending_review_required = True
        self.state.post_review_route = next_route
        self.state.routing_label = 'human_review'
        self.state.reason = reason
        return self.state.routing_label

    def _pending_review_answer_text(self) -> str:
        if self.state.resolved_student_name:
            return (
                f'A consulta protegida sobre {self.state.resolved_student_name} ficou pendente de revisao humana antes da liberacao final. '
                'Assim que a validacao for concluida, eu continuo desta mesma conversa.'
            )
        return (
            'Essa consulta protegida ficou pendente de revisao humana antes da liberacao final. '
            'Assim que a validacao for concluida, eu continuo desta mesma conversa.'
        )

    def _pending_review_payload(self) -> dict[str, Any]:
        return {
            'slice_name': 'protected',
            'conversation_id': self.state.conversation_id or f'telegram:{self.state.telegram_chat_id}',
            'message': self.state.message,
            'normalized_message': self.state.normalized_message,
            'resolved_student_name': self.state.resolved_student_name,
            'post_review_route': self.state.post_review_route,
            'plan': self.state.plan.model_dump(mode='json') if isinstance(self.state.plan, ProtectedPilotPlan) else None,
            'answer': self.state.answer.model_dump(mode='json') if isinstance(self.state.answer, ProtectedPilotAnswer) else None,
            'evidence_sources': list(self.state.evidence_source_ids),
        }

    def _build_pending_review_response(self) -> dict[str, Any]:
        pending_answer = ProtectedPilotAnswer(answer_text=self._pending_review_answer_text())
        return {
            'engine_name': 'crewai',
            'executed': True,
            'reason': 'crewai_protected_pending_review',
            'metadata': {
                **self._base_metadata(),
                'answer': pending_answer.model_dump(mode='json'),
                'judge': ProtectedPilotJudge(valid=True, reason='pending_human_review', revision_needed=False).model_dump(mode='json'),
                'pending_review': True,
                'review_flow_id': getattr(self.state, 'id', None),
                'review_message': self._pending_review_answer_text(),
                'review_required': True,
                'deterministic_backstop_used': bool(self.state.answer),
                'validation_stack': ['flow_state', 'human_review_pending'],
            },
        }

    def _build_rejected_review_response(self, feedback_text: str | None = None) -> dict[str, Any]:
        feedback_note = f' Feedback registrado: {feedback_text}.' if feedback_text else ''
        answer = ProtectedPilotAnswer(
            answer_text=(
                'Essa consulta protegida nao foi liberada apos a revisao humana, entao eu nao vou expor o dado por aqui.'
                f'{feedback_note}'
            )
        )
        judge = ProtectedPilotJudge(valid=True, reason='protected_review_rejected', revision_needed=False)
        return {
            'engine_name': 'crewai',
            'executed': True,
            'reason': 'crewai_protected_review_rejected',
            'metadata': {
                **self._base_metadata(),
                'answer': answer.model_dump(mode='json'),
                'judge': judge.model_dump(mode='json'),
                'pending_review': False,
                'review_required': False,
                'review_rejected': True,
                'deterministic_backstop_used': False,
                'validation_stack': ['flow_state', 'human_review', 'review_rejected'],
            },
        }

    def _build_fast_path_response(self, *, reason: str) -> dict[str, Any]:
        self.state.latency_ms = round((perf_counter() - self._overall_started_at) * 1000, 1)
        if self.state.resolved_student_name:
            self.state.active_student_name = self.state.resolved_student_name
        return {
            'engine_name': 'crewai',
            'executed': True,
            'reason': reason,
            'metadata': {
                **self._base_metadata(),
                'crewai_installed': True,
                'crewai_version': getattr(crewai_pkg, '__version__', None),
                'agent_roles': [],
                'task_names': [],
                'latency_ms': self.state.latency_ms,
                'plan': self.state.plan.model_dump(mode='json') if isinstance(self.state.plan, ProtectedPilotPlan) else None,
                'answer': self.state.answer.model_dump(mode='json') if isinstance(self.state.answer, ProtectedPilotAnswer) else None,
                'judge': self.state.judge.model_dump(mode='json') if isinstance(self.state.judge, ProtectedPilotJudge) else None,
                'evidence_sources': list(self.state.evidence_source_ids),
                'deterministic_backstop_used': True,
                'validation_stack': ['flow_router', 'deterministic_fast_path'],
            },
        }

    def _agentic_recovery_answer_text(self) -> str:
        target_name = str(self.state.resolved_student_name or '').strip()
        if target_name:
            return (
                f'Eu nao consegui consolidar essa consulta protegida com seguranca agora sobre {target_name}. '
                'Se quiser, me diga exatamente se voce quer notas, faltas, provas, documentacao, matricula ou financeiro.'
            )
        return (
            'Eu nao consegui consolidar essa consulta protegida com seguranca agora. '
            'Se quiser, me diga qual aluno e qual dado voce quer consultar.'
        )

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

        recent_student_name = self.state.active_student_name
        self._student = _resolve_student(self._actor, self.state.message, recent_student_name=recent_student_name)
        self.state.resolved_student_name = self._student.get('full_name') if isinstance(self._student, dict) else None
        self.state.effective_message = _augment_protected_message_with_state(
            self.state.message,
            active_student_name=self.state.resolved_student_name or self.state.active_student_name,
            active_domain=self.state.active_domain,
            active_attribute=self.state.active_attribute,
        )

        self._identity_backstop_text = _identity_backstop(self._actor, self.state.message)
        if self._identity_backstop_text and _is_identity_scope_query(self.state.message):
            self.state.plan = _infer_fast_path_plan(self.state.message, self._student)
            self.state.answer = ProtectedPilotAnswer(
                answer_text=self._identity_backstop_text,
                citations=['identity.actor'],
            )
            self.state.judge = ProtectedPilotJudge(valid=True, reason='identity_scope_handled_deterministically', revision_needed=False)
            if isinstance(self.state.plan, ProtectedPilotPlan):
                self.state.active_domain = self.state.plan.domain
                self.state.active_attribute = self.state.plan.attribute
            if self._protected_hitl_enabled() and async_feedback_supported():
                return self._queue_human_review(
                    next_route='identity_backstop',
                    reason='crewai_protected_pending_review',
                )
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
        self._shortlisted_docs = _rank_docs(self.state.effective_message or self.state.message, docs)
        self.state.evidence_source_ids = [doc.doc_id for doc in self._shortlisted_docs]

        fast_path_answer = self._identity_backstop_text or _student_backstop(
            self.state.effective_message or self.state.message,
            self._student,
            evidence,
            self._shortlisted_docs,
        )
        if isinstance(fast_path_answer, str) and fast_path_answer.strip():
            self.state.plan = _infer_fast_path_plan(self.state.effective_message or self.state.message, self._student)
            self.state.answer = ProtectedPilotAnswer(
                answer_text=fast_path_answer,
                citations=[self._shortlisted_docs[0].doc_id] if self._shortlisted_docs else [],
            )
            self.state.judge = ProtectedPilotJudge(valid=True, reason='deterministic_fast_path', revision_needed=False)
            if isinstance(self.state.plan, ProtectedPilotPlan):
                self.state.active_domain = self.state.plan.domain
                self.state.active_attribute = self.state.plan.attribute
            if self._protected_hitl_enabled() and async_feedback_supported():
                return self._queue_human_review(
                    next_route='fast_path',
                    reason='crewai_protected_pending_review',
                )
            self.state.routing_label = 'fast_path'
            self.state.reason = 'crewai_protected_fast_path'
            return self.state.routing_label

        self._llm = _build_llm(self.settings)
        if self._llm is None:
            self.state.routing_label = 'llm_unavailable'
            self.state.reason = 'crewai_llm_not_configured'
            return self.state.routing_label

        if self._protected_hitl_enabled() and async_feedback_supported():
            return self._queue_human_review(
                next_route='agentic',
                reason='crewai_protected_pending_review',
            )

        self.state.routing_label = 'agentic'
        self.state.reason = 'crewai_protected_flow_agentic'
        return self.state.routing_label

    @router(prepare_context)
    def route(self) -> str:
        return self.state.routing_label

    def _base_metadata(self) -> dict[str, Any]:
        empty_event_telemetry = serialize_pilot_events(None)
        return {
            'conversation_id': self.state.conversation_id or f'telegram:{self.state.telegram_chat_id}',
            'slice_name': 'protected',
            'normalized_message': self.state.normalized_message,
            'resolved_student_name': self.state.resolved_student_name,
            'flow_enabled': True,
            'flow_state_id': getattr(self.state, 'id', None),
            'event_listener': empty_event_telemetry,
            'event_summary': empty_event_telemetry.get('summary', {}),
            'task_trace': empty_event_telemetry.get('task_trace', {}),
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
        if self.state.resolved_student_name:
            self.state.active_student_name = self.state.resolved_student_name
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
        if self.state.resolved_student_name:
            self.state.active_student_name = self.state.resolved_student_name
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

    @listen('human_review')
    def request_human_review(self) -> dict[str, Any]:
        if HumanFeedbackPending is None or PendingFeedbackContext is None:
            return self._build_pending_review_response()
        context = PendingFeedbackContext(
            flow_id=str(getattr(self.state, 'id', '') or ''),
            flow_class=f'{self.__class__.__module__}.{self.__class__.__name__}',
            method_name='request_human_review',
            method_output=self._pending_review_payload(),
            message=(
                'Revisao humana pendente para uma consulta protegida. '
                'Responda com "approved" para liberar ou "rejected" para bloquear.'
            ),
            metadata={
                'slice_name': 'protected',
                'conversation_id': self.state.conversation_id or f'telegram:{self.state.telegram_chat_id}',
                'post_review_route': self.state.post_review_route,
                'resolved_student_name': self.state.resolved_student_name,
            },
        )
        raise HumanFeedbackPending(context=context)

    @listen('request_human_review')
    async def handle_human_review_decision(self, feedback_result: Any) -> dict[str, Any]:
        feedback_text = str(getattr(feedback_result, 'feedback', '') or '').strip()
        if feedback_is_approved(feedback_text):
            next_route = str(self.state.post_review_route or '').strip()
            if next_route == 'agentic':
                return await self._run_agentic_path(reason='crewai_protected_review_approved')
            if next_route == 'identity_backstop':
                return self._build_fast_path_response(reason='crewai_protected_review_approved')
            if next_route == 'fast_path':
                return self._build_fast_path_response(reason='crewai_protected_review_approved')
            return self._build_fast_path_response(reason='crewai_protected_review_approved')
        if feedback_is_rejected(feedback_text):
            return self._build_rejected_review_response(feedback_text)
        return self._build_rejected_review_response(feedback_text or 'no_explicit_decision')

    @listen('fast_path')
    def handle_fast_path(self) -> dict[str, Any]:
        return self._build_fast_path_response(reason='crewai_protected_fast_path')

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
        return await self._run_agentic_path(reason='crewai_protected_flow_completed')

    async def _run_agentic_path(self, *, reason: str) -> dict[str, Any]:
        evidence = await _fetch_protected_evidence(
            settings=self.settings,
            actor_context=self._actor_context,
            student=self._student,
            telegram_chat_id=self.state.telegram_chat_id,
        )
        if not self._shortlisted_docs:
            docs = _build_protected_docs(evidence)
            self._shortlisted_docs = _rank_docs(self.state.effective_message or self.state.message, docs)
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
        linked_student_names = [
            str(item.get('full_name', '')).strip()
            for item in (self._actor or {}).get('linked_students', [])
            if isinstance(item, dict) and str(item.get('full_name', '')).strip()
        ]
        forbidden_student_names = [
            name
            for name in linked_student_names
            if not self.state.resolved_student_name
            or name.casefold() != str(self.state.resolved_student_name).casefold()
        ]

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
            guardrails=[
                require_pydantic_model(ProtectedPilotPlan),
                require_sources_subset(
                    model_type=ProtectedPilotPlan,
                    field_name='relevant_sources',
                    valid_source_ids=self.state.evidence_source_ids,
                ),
            ],
            guardrail_max_retries=1,
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
            guardrails=[
                require_pydantic_model(ProtectedPilotAnswer),
                require_answer_citations_subset(
                    model_type=ProtectedPilotAnswer,
                    valid_source_ids=self.state.evidence_source_ids,
                ),
                require_no_forbidden_entities(
                    model_type=ProtectedPilotAnswer,
                    forbidden_names=forbidden_student_names,
                ),
            ],
            guardrail_max_retries=1,
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
            guardrails=[
                require_pydantic_model(ProtectedPilotJudge),
                require_nonempty_reason_when_invalid(ProtectedPilotJudge),
            ],
            guardrail_max_retries=1,
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

        kickoff_failed_reason: str | None = None
        with capture_pilot_events('protected') as event_recorder:
            try:
                await asyncio.wait_for(
                    asyncio.to_thread(
                        crew.kickoff,
                        inputs={
                            'message': self.state.effective_message or self.state.message,
                            'evidence_bundle': evidence_bundle,
                        },
                    ),
                    timeout=11.0,
                )
            except asyncio.TimeoutError:
                kickoff_failed_reason = 'crewai_protected_flow_timeout'
            except Exception:
                kickoff_failed_reason = 'crewai_protected_flow_error'
                logger.exception('crewai_protected_flow_kickoff_failed')

        self.state.latency_ms = round((perf_counter() - self._overall_started_at) * 1000, 1)
        plan = _extract_task_pydantic(planning_task, ProtectedPilotPlan)
        answer = _extract_task_pydantic(composition_task, ProtectedPilotAnswer)
        verdict = _extract_task_pydantic(judge_task, ProtectedPilotJudge)

        backstop_answer = self._identity_backstop_text or _student_backstop(
            self.state.effective_message or self.state.message,
            self._student,
            evidence,
            self._shortlisted_docs,
        )
        backstop_used = False
        if isinstance(backstop_answer, str) and backstop_answer.strip():
            answer = ProtectedPilotAnswer(
                answer_text=backstop_answer,
                citations=[self._shortlisted_docs[0].doc_id] if self._shortlisted_docs else [],
            )
            verdict = ProtectedPilotJudge(
                valid=True,
                reason=kickoff_failed_reason or 'deterministic_backstop_applied',
                revision_needed=False,
            )
            backstop_used = True
        elif kickoff_failed_reason:
            answer = ProtectedPilotAnswer(
                answer_text=self._agentic_recovery_answer_text(),
                citations=[],
            )
            verdict = ProtectedPilotJudge(valid=True, reason=kickoff_failed_reason, revision_needed=False)

        self.state.plan = plan if isinstance(plan, ProtectedPilotPlan) else None
        self.state.answer = answer if isinstance(answer, ProtectedPilotAnswer) else None
        self.state.judge = verdict if isinstance(verdict, ProtectedPilotJudge) else None
        self.state.deterministic_backstop_used = backstop_used
        if self.state.resolved_student_name:
            self.state.active_student_name = self.state.resolved_student_name
        if isinstance(self.state.plan, ProtectedPilotPlan):
            self.state.active_domain = self.state.plan.domain
            self.state.active_attribute = self.state.plan.attribute

        event_listener = serialize_pilot_events(event_recorder)
        metadata = {
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
            'event_listener': event_listener,
            'event_summary': event_listener.get('summary', {}),
            'task_trace': event_listener.get('task_trace', {}),
            'flow_state_id': getattr(self.state, 'id', None),
            'flow_state_persisted': get_sqlite_flow_persistence('protected') is not None,
            'kickoff_failed_reason': kickoff_failed_reason,
        }
        if kickoff_failed_reason and isinstance(self.state.answer, ProtectedPilotAnswer):
            return {
                'engine_name': 'crewai',
                'executed': True,
                'reason': kickoff_failed_reason,
                'metadata': metadata,
            }
        if isinstance(self.state.judge, ProtectedPilotJudge) and not self.state.judge.valid:
            return {
                'engine_name': 'crewai',
                'executed': True,
                'reason': 'crewai_protected_flow_judge_invalid',
                'metadata': metadata,
            }
        return {
            'engine_name': 'crewai',
            'executed': True,
            'reason': reason,
            'metadata': metadata,
        }
