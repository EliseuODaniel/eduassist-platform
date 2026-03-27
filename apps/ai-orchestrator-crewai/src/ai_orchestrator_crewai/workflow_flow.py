from __future__ import annotations

from time import perf_counter
from typing import Any

from pydantic import BaseModel

try:
    from crewai.flow.persistence import persist  # type: ignore
    from crewai.flow.flow import Flow, listen, router, start  # type: ignore
except Exception:  # pragma: no cover
    Flow = None  # type: ignore[assignment]
    listen = router = start = None  # type: ignore[assignment]
    persist = None  # type: ignore[assignment]

from .flow_persistence import get_sqlite_flow_persistence
from .agentic_rendering import maybe_render_agentic_response

from .workflow_pilot import (
    _contains_any,
    _extract_preferred_date,
    _extract_preferred_window,
    _extract_protocol_code,
    _get_workflow_status,
    _internal_post,
    _normalize_text,
    _request_action_response,
    _request_create_response,
    _request_protocol_response,
    _request_status_response,
    _request_summary_response,
    _visit_action_response,
    _visit_create_response,
    _visit_protocol_response,
    _visit_status_response,
)


class WorkflowFlowState(BaseModel):
    id: str | None = None
    message: str = ''
    conversation_id: str | None = None
    telegram_chat_id: int | None = None
    channel: str = 'telegram'
    normalized_message: str = ''
    routing_label: str = 'prepare'
    reason: str = ''
    protocol_code: str | None = None
    current_item: dict[str, Any] | None = None
    current_type: str = ''
    preferred_window: str | None = None
    preferred_date_iso: str | None = None
    active_protocol_code: str | None = None
    active_workflow_type: str | None = None
    active_preferred_window: str | None = None
    active_preferred_date_iso: str | None = None
    latency_ms: float = 0.0


def _workflow_flow_decorator(target: type[Flow[WorkflowFlowState]]) -> type[Flow[WorkflowFlowState]]:
    if persist is None:
        return target
    persistence = get_sqlite_flow_persistence('workflow')
    if persistence is None:
        return target
    return persist(persistence=persistence, verbose=False)(target)


@_workflow_flow_decorator
class WorkflowShadowFlow(Flow[WorkflowFlowState]):
    def __init__(self, *, settings: Any, persistence: Any | None = None) -> None:
        self.settings = settings
        self._overall_started_at = perf_counter()
        super().__init__(persistence=persistence, tracing=False)

    @start()
    async def prepare_context(self) -> str:
        self._overall_started_at = perf_counter()
        self.state.normalized_message = _normalize_text(self.state.message)
        conversation_external_id = str(self.state.conversation_id or '').strip()
        if not conversation_external_id:
            self.state.routing_label = 'missing_conversation'
            self.state.reason = 'missing_conversation_id_for_workflow'
            return self.state.routing_label

        self.state.protocol_code = _extract_protocol_code(self.state.message)
        if not self.state.protocol_code and self.state.active_protocol_code:
            self.state.protocol_code = self.state.active_protocol_code
        preferred_date = _extract_preferred_date(self.state.message)
        self.state.preferred_date_iso = preferred_date.isoformat() if preferred_date else None
        self.state.preferred_window = _extract_preferred_window(self.state.message)
        if not self.state.preferred_date_iso and self.state.active_preferred_date_iso:
            self.state.preferred_date_iso = self.state.active_preferred_date_iso
        if not self.state.preferred_window and self.state.active_preferred_window:
            self.state.preferred_window = self.state.active_preferred_window

        workflow_status = await _get_workflow_status(
            self.settings,
            conversation_id=conversation_external_id,
            channel=self.state.channel,
            protocol_code=self.state.protocol_code,
        )
        current_item = workflow_status.get('item') if isinstance(workflow_status, dict) else None
        self.state.current_item = current_item if isinstance(current_item, dict) else None
        if not isinstance(self.state.current_item, dict) and self.state.active_protocol_code:
            workflow_status = await _get_workflow_status(
                self.settings,
                conversation_id=conversation_external_id,
                channel=self.state.channel,
                protocol_code=self.state.active_protocol_code,
            )
            current_item = workflow_status.get('item') if isinstance(workflow_status, dict) else None
            self.state.current_item = current_item if isinstance(current_item, dict) else None
        self.state.current_type = str((self.state.current_item or {}).get('workflow_type') or '').strip()
        if not self.state.current_type and self.state.active_workflow_type:
            self.state.current_type = self.state.active_workflow_type
        if isinstance(self.state.current_item, dict):
            self.state.active_protocol_code = str(
                self.state.current_item.get('protocol_code') or self.state.active_protocol_code or ''
            ).strip() or self.state.active_protocol_code
            self.state.active_workflow_type = self.state.current_type or self.state.active_workflow_type
            preferred_date_value = str(self.state.current_item.get('preferred_date') or '').strip()
            if preferred_date_value:
                self.state.active_preferred_date_iso = preferred_date_value
            preferred_window_value = str(self.state.current_item.get('preferred_window') or '').strip()
            if preferred_window_value:
                self.state.active_preferred_window = preferred_window_value

        normalized = self.state.normalized_message
        visit_terms = {'visita', 'tour', 'conhecer a escola'}
        request_terms = {'direcao', 'direção', 'protocolo', 'protocolar', 'solicitacao', 'solicitação', 'pedido'}

        if _contains_any(normalized, visit_terms) and _contains_any(normalized, {'cancelar', 'desmarcar'}):
            self.state.routing_label = 'visit_cancel'
            self.state.reason = 'workflow_visit_cancel'
            return self.state.routing_label

        if (
            (_contains_any(normalized, visit_terms) or self.state.current_type == 'visit_booking')
            and _contains_any(normalized, {'remarcar', 'reagendar', 'mudar'})
        ):
            if _contains_any(normalized, {'se eu precisar', 'se precisar', 'caso precise'}):
                self.state.routing_label = 'visit_reschedule_guidance'
                self.state.reason = 'workflow_visit_reschedule_guidance'
                return self.state.routing_label
            self.state.routing_label = 'visit_reschedule'
            self.state.reason = 'workflow_visit_reschedule'
            return self.state.routing_label

        if _contains_any(normalized, visit_terms) and _contains_any(normalized, {'agendar', 'marcar', 'quero'}) and 'visita' in normalized:
            self.state.routing_label = 'visit_create'
            self.state.reason = 'workflow_visit_create'
            return self.state.routing_label

        if _contains_any(normalized, {'status', 'andamento'}) or 'qual o protocolo' in normalized or 'resume meu pedido' in normalized:
            if not isinstance(self.state.current_item, dict):
                self.state.routing_label = 'lookup_not_found'
                self.state.reason = 'workflow_not_found'
                return self.state.routing_label
            if 'qual o protocolo' in normalized:
                self.state.routing_label = 'protocol_lookup'
                self.state.reason = 'workflow_protocol_lookup'
            elif 'resume meu pedido' in normalized:
                self.state.routing_label = 'summary_lookup'
                self.state.reason = 'workflow_summary_lookup'
            else:
                self.state.routing_label = 'status_lookup'
                self.state.reason = 'workflow_status_lookup'
            return self.state.routing_label

        if _contains_any(normalized, request_terms) and _contains_any(normalized, {'protocolar', 'solicitacao', 'solicitação', 'pedido'}):
            self.state.routing_label = 'request_create'
            self.state.reason = 'workflow_request_create'
            return self.state.routing_label

        if _contains_any(normalized, {'complementar', 'acrescentar', 'adicionar', 'incluir'}) and self.state.current_type == 'institutional_request':
            self.state.routing_label = 'request_update'
            self.state.reason = 'workflow_request_update'
            return self.state.routing_label

        self.state.routing_label = 'not_supported'
        self.state.reason = 'workflow_not_supported'
        return self.state.routing_label

    @router(prepare_context)
    def route(self) -> str:
        return self.state.routing_label

    def _base_metadata(self) -> dict[str, Any]:
        return {
            'slice_name': 'workflow',
            'conversation_id': self.state.conversation_id,
            'normalized_message': self.state.normalized_message,
            'workflow_type': self.state.current_type or None,
            'flow_enabled': True,
            'flow_state_id': getattr(self.state, 'id', None),
            'flow_state_persisted': get_sqlite_flow_persistence('workflow') is not None,
            'active_protocol_code': self.state.active_protocol_code,
            'active_workflow_type': self.state.active_workflow_type,
        }

    def _finish(self, answer_text: str | None = None, *, extra: dict[str, Any] | None = None) -> dict[str, Any]:
        self.state.latency_ms = round((perf_counter() - self._overall_started_at) * 1000, 1)
        metadata = {
            **self._base_metadata(),
            'latency_ms': self.state.latency_ms,
            'validation_stack': ['flow_router', 'deterministic_workflow'],
        }
        if answer_text is not None:
            metadata['answer'] = {'answer_text': answer_text}
        if extra:
            metadata.update(extra)
        return metadata

    async def _finalize_workflow_answer(
        self,
        *,
        answer_text: str,
        reason: str,
        extra: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        rendered = await maybe_render_agentic_response(
            slice_name='workflow',
            settings=self.settings,
            user_message=self.state.message,
            deterministic_answer=answer_text,
            instructions=(
                'Reescreva a resposta operacional com tom humano e claro, preservando literalmente protocolos, tickets, status, datas, janelas e proximo passo.'
            ),
            required_anchors=[
                str(self.state.active_protocol_code or ''),
                str(self.state.active_preferred_date_iso or ''),
                str(self.state.active_preferred_window or ''),
            ],
        )
        metadata_extra = {
            'crewai_installed': bool(Flow is not None),
            'agent_roles': rendered.get('agent_roles', []),
            'task_names': rendered.get('task_names', []),
            'event_listener': rendered.get('event_listener', {}),
            'event_summary': rendered.get('event_summary', {}),
            'task_trace': rendered.get('task_trace', {}),
            'judge': rendered.get('judge'),
            'deterministic_backstop_used': bool(rendered.get('deterministic_backstop_used', False)),
            'validation_stack': rendered.get('validation_stack', ['operation_result', 'deterministic_backstop']),
            'crewai_version': rendered.get('crewai_version'),
        }
        if extra:
            metadata_extra.update(extra)
        return {
            'engine_name': 'crewai',
            'executed': True,
            'reason': reason,
            'metadata': self._finish(str(rendered.get('answer_text', answer_text) or answer_text), extra=metadata_extra),
        }

    @listen('missing_conversation')
    def handle_missing_conversation(self) -> dict[str, Any]:
        return {'engine_name': 'crewai', 'executed': False, 'reason': self.state.reason, 'metadata': self._finish()}

    @listen('visit_cancel')
    async def handle_visit_cancel(self) -> dict[str, Any]:
        payload = await _internal_post(
            self.settings,
            '/v1/internal/workflows/visit-bookings/actions',
            payload={
                'conversation_external_id': str(self.state.conversation_id or ''),
                'channel': self.state.channel,
                'telegram_chat_id': self.state.telegram_chat_id,
                'protocol_code': self.state.protocol_code or (self.state.current_item or {}).get('protocol_code'),
                'action': 'cancel',
                'notes': self.state.message,
            },
        )
        item = payload.get('item', {})
        self.state.active_protocol_code = str(item.get('protocol_code') or '').strip() or self.state.active_protocol_code
        self.state.active_workflow_type = 'visit_booking'
        return await self._finalize_workflow_answer(
            answer_text=_visit_action_response(item, action='cancel'),
            reason='workflow_visit_cancel',
            extra={'workflow_type': 'visit'},
        )

    @listen('visit_reschedule')
    async def handle_visit_reschedule(self) -> dict[str, Any]:
        payload = await _internal_post(
            self.settings,
            '/v1/internal/workflows/visit-bookings/actions',
            payload={
                'conversation_external_id': str(self.state.conversation_id or ''),
                'channel': self.state.channel,
                'telegram_chat_id': self.state.telegram_chat_id,
                'protocol_code': self.state.protocol_code or (self.state.current_item or {}).get('protocol_code'),
                'action': 'reschedule',
                'preferred_date': self.state.preferred_date_iso,
                'preferred_window': self.state.preferred_window,
                'notes': self.state.message,
            },
        )
        item = payload.get('item', {})
        self.state.active_protocol_code = str(item.get('protocol_code') or '').strip() or self.state.active_protocol_code
        self.state.active_workflow_type = 'visit_booking'
        self.state.active_preferred_date_iso = str(item.get('preferred_date') or self.state.preferred_date_iso or '').strip() or self.state.active_preferred_date_iso
        self.state.active_preferred_window = str(item.get('preferred_window') or self.state.preferred_window or '').strip() or self.state.active_preferred_window
        return await self._finalize_workflow_answer(
            answer_text=_visit_action_response(item, action='reschedule'),
            reason='workflow_visit_reschedule',
            extra={'workflow_type': 'visit'},
        )

    @listen('visit_reschedule_guidance')
    async def handle_visit_reschedule_guidance(self) -> dict[str, Any]:
        item = self.state.current_item or {}
        protocol_code = str(item.get('protocol_code') or self.state.active_protocol_code or '').strip()
        answer_text = (
            f'Se voce precisar remarcar, me passe o protocolo {protocol_code} ou o novo horario desejado '
            'que eu sigo com essa atualizacao para a fila de admissoes.'
            if protocol_code
            else 'Se voce precisar remarcar, me passe o protocolo da visita ou o novo horario desejado que eu sigo com essa atualizacao.'
        )
        return await self._finalize_workflow_answer(
            answer_text=answer_text,
            reason='workflow_visit_reschedule_guidance',
            extra={'workflow_type': 'visit'},
        )

    @listen('visit_create')
    async def handle_visit_create(self) -> dict[str, Any]:
        payload = await _internal_post(
            self.settings,
            '/v1/internal/workflows/visit-bookings',
            payload={
                'conversation_external_id': str(self.state.conversation_id or ''),
                'channel': self.state.channel,
                'telegram_chat_id': self.state.telegram_chat_id,
                'preferred_date': self.state.preferred_date_iso,
                'preferred_window': self.state.preferred_window,
                'notes': self.state.message,
            },
        )
        item = payload.get('item', {})
        self.state.active_protocol_code = str(item.get('protocol_code') or '').strip() or self.state.active_protocol_code
        self.state.active_workflow_type = 'visit_booking'
        self.state.active_preferred_date_iso = str(item.get('preferred_date') or self.state.preferred_date_iso or '').strip() or self.state.active_preferred_date_iso
        self.state.active_preferred_window = str(item.get('preferred_window') or self.state.preferred_window or '').strip() or self.state.active_preferred_window
        return await self._finalize_workflow_answer(
            answer_text=_visit_create_response(item),
            reason='workflow_visit_create',
            extra={'workflow_type': 'visit'},
        )

    @listen('lookup_not_found')
    def handle_lookup_not_found(self) -> dict[str, Any]:
        return {
            'engine_name': 'crewai',
            'executed': True,
            'reason': 'workflow_not_found',
            'metadata': self._finish('Nao encontrei um protocolo ativo nesta conversa para retomar agora.', extra={'workflow_type': 'unknown'}),
        }

    @listen('protocol_lookup')
    async def handle_protocol_lookup(self) -> dict[str, Any]:
        item = self.state.current_item or {}
        self.state.active_protocol_code = str(item.get('protocol_code') or '').strip() or self.state.active_protocol_code
        self.state.active_workflow_type = self.state.current_type or self.state.active_workflow_type
        text = _visit_protocol_response(item) if self.state.current_type == 'visit_booking' else _request_protocol_response(item)
        return await self._finalize_workflow_answer(
            answer_text=text,
            reason='workflow_protocol_lookup',
            extra={'workflow_type': self.state.current_type},
        )

    @listen('summary_lookup')
    async def handle_summary_lookup(self) -> dict[str, Any]:
        item = self.state.current_item or {}
        self.state.active_protocol_code = str(item.get('protocol_code') or '').strip() or self.state.active_protocol_code
        self.state.active_workflow_type = self.state.current_type or self.state.active_workflow_type
        text = _request_summary_response(item) if self.state.current_type == 'institutional_request' else _visit_status_response(item)
        return await self._finalize_workflow_answer(
            answer_text=text,
            reason='workflow_summary_lookup',
            extra={'workflow_type': self.state.current_type},
        )

    @listen('status_lookup')
    async def handle_status_lookup(self) -> dict[str, Any]:
        item = self.state.current_item or {}
        self.state.active_protocol_code = str(item.get('protocol_code') or '').strip() or self.state.active_protocol_code
        self.state.active_workflow_type = self.state.current_type or self.state.active_workflow_type
        text = _visit_status_response(item) if self.state.current_type == 'visit_booking' else _request_status_response(item)
        return await self._finalize_workflow_answer(
            answer_text=text,
            reason='workflow_status_lookup',
            extra={'workflow_type': self.state.current_type},
        )

    @listen('request_create')
    async def handle_request_create(self) -> dict[str, Any]:
        payload = await _internal_post(
            self.settings,
            '/v1/internal/workflows/institutional-requests',
            payload={
                'conversation_external_id': str(self.state.conversation_id or ''),
                'channel': self.state.channel,
                'telegram_chat_id': self.state.telegram_chat_id,
                'target_area': 'direcao' if _contains_any(self.state.normalized_message, {'direcao', 'direção'}) else 'atendimento',
                'category': 'solicitacao_institucional',
                'subject': self.state.message,
                'details': self.state.message,
            },
        )
        item = payload.get('item', {})
        self.state.active_protocol_code = str(item.get('protocol_code') or '').strip() or self.state.active_protocol_code
        self.state.active_workflow_type = 'institutional_request'
        return await self._finalize_workflow_answer(
            answer_text=_request_create_response(item, subject=self.state.message),
            reason='workflow_request_create',
            extra={'workflow_type': 'request'},
        )

    @listen('request_update')
    async def handle_request_update(self) -> dict[str, Any]:
        payload = await _internal_post(
            self.settings,
            '/v1/internal/workflows/institutional-requests/actions',
            payload={
                'conversation_external_id': str(self.state.conversation_id or ''),
                'channel': self.state.channel,
                'telegram_chat_id': self.state.telegram_chat_id,
                'protocol_code': self.state.protocol_code or (self.state.current_item or {}).get('protocol_code'),
                'action': 'add_details',
                'details': self.state.message,
            },
        )
        item = payload.get('item', {})
        detail = self.state.message.replace('quero complementar meu pedido dizendo que', '').strip() or self.state.message
        self.state.active_protocol_code = str(item.get('protocol_code') or '').strip() or self.state.active_protocol_code
        self.state.active_workflow_type = 'institutional_request'
        return await self._finalize_workflow_answer(
            answer_text=_request_action_response(item, detail=detail),
            reason='workflow_request_update',
            extra={'workflow_type': 'request'},
        )

    @listen('not_supported')
    def handle_not_supported(self) -> dict[str, Any]:
        return {'engine_name': 'crewai', 'executed': False, 'reason': 'workflow_not_supported', 'metadata': self._finish()}
