from __future__ import annotations

from time import perf_counter
from typing import Any

from pydantic import BaseModel

try:
    from crewai.flow.flow import Flow, listen, router, start  # type: ignore
except Exception:  # pragma: no cover
    Flow = None  # type: ignore[assignment]
    listen = router = start = None  # type: ignore[assignment]

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
    latency_ms: float = 0.0


class WorkflowShadowFlow(Flow[WorkflowFlowState]):
    def __init__(self, *, settings: Any) -> None:
        self.settings = settings
        self._overall_started_at = perf_counter()
        super().__init__(tracing=False)

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
        preferred_date = _extract_preferred_date(self.state.message)
        self.state.preferred_date_iso = preferred_date.isoformat() if preferred_date else None
        self.state.preferred_window = _extract_preferred_window(self.state.message)

        workflow_status = await _get_workflow_status(
            self.settings,
            conversation_id=conversation_external_id,
            channel=self.state.channel,
            protocol_code=self.state.protocol_code,
        )
        current_item = workflow_status.get('item') if isinstance(workflow_status, dict) else None
        self.state.current_item = current_item if isinstance(current_item, dict) else None
        self.state.current_type = str((self.state.current_item or {}).get('workflow_type') or '').strip()

        normalized = self.state.normalized_message
        visit_terms = {'visita', 'tour', 'conhecer a escola'}
        request_terms = {'direcao', 'direção', 'protocolo', 'protocolar', 'solicitacao', 'solicitação', 'pedido'}

        if _contains_any(normalized, visit_terms) and _contains_any(normalized, {'cancelar', 'desmarcar'}):
            self.state.routing_label = 'visit_cancel'
            self.state.reason = 'workflow_visit_cancel'
            return self.state.routing_label

        if _contains_any(normalized, visit_terms) and _contains_any(normalized, {'remarcar', 'reagendar', 'mudar'}):
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
        return {
            'engine_name': 'crewai',
            'executed': True,
            'reason': 'workflow_visit_cancel',
            'metadata': self._finish(_visit_action_response(item, action='cancel'), extra={'workflow_type': 'visit'}),
        }

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
        return {
            'engine_name': 'crewai',
            'executed': True,
            'reason': 'workflow_visit_reschedule',
            'metadata': self._finish(_visit_action_response(item, action='reschedule'), extra={'workflow_type': 'visit'}),
        }

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
        return {
            'engine_name': 'crewai',
            'executed': True,
            'reason': 'workflow_visit_create',
            'metadata': self._finish(_visit_create_response(item), extra={'workflow_type': 'visit'}),
        }

    @listen('lookup_not_found')
    def handle_lookup_not_found(self) -> dict[str, Any]:
        return {
            'engine_name': 'crewai',
            'executed': True,
            'reason': 'workflow_not_found',
            'metadata': self._finish('Nao encontrei um protocolo ativo nesta conversa para retomar agora.', extra={'workflow_type': 'unknown'}),
        }

    @listen('protocol_lookup')
    def handle_protocol_lookup(self) -> dict[str, Any]:
        item = self.state.current_item or {}
        text = _visit_protocol_response(item) if self.state.current_type == 'visit_booking' else _request_protocol_response(item)
        return {
            'engine_name': 'crewai',
            'executed': True,
            'reason': 'workflow_protocol_lookup',
            'metadata': self._finish(text, extra={'workflow_type': self.state.current_type}),
        }

    @listen('summary_lookup')
    def handle_summary_lookup(self) -> dict[str, Any]:
        item = self.state.current_item or {}
        text = _request_summary_response(item) if self.state.current_type == 'institutional_request' else _visit_status_response(item)
        return {
            'engine_name': 'crewai',
            'executed': True,
            'reason': 'workflow_summary_lookup',
            'metadata': self._finish(text, extra={'workflow_type': self.state.current_type}),
        }

    @listen('status_lookup')
    def handle_status_lookup(self) -> dict[str, Any]:
        item = self.state.current_item or {}
        text = _visit_status_response(item) if self.state.current_type == 'visit_booking' else _request_status_response(item)
        return {
            'engine_name': 'crewai',
            'executed': True,
            'reason': 'workflow_status_lookup',
            'metadata': self._finish(text, extra={'workflow_type': self.state.current_type}),
        }

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
        return {
            'engine_name': 'crewai',
            'executed': True,
            'reason': 'workflow_request_create',
            'metadata': self._finish(_request_create_response(item, subject=self.state.message), extra={'workflow_type': 'request'}),
        }

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
        return {
            'engine_name': 'crewai',
            'executed': True,
            'reason': 'workflow_request_update',
            'metadata': self._finish(_request_action_response(item, detail=detail), extra={'workflow_type': 'request'}),
        }

    @listen('not_supported')
    def handle_not_supported(self) -> dict[str, Any]:
        return {'engine_name': 'crewai', 'executed': False, 'reason': 'workflow_not_supported', 'metadata': self._finish()}
