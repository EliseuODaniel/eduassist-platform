from __future__ import annotations

from time import perf_counter
from typing import Any

from pydantic import BaseModel

try:
    from crewai.flow.flow import Flow, listen, router, start  # type: ignore
except Exception:  # pragma: no cover
    Flow = None  # type: ignore[assignment]
    listen = router = start = None  # type: ignore[assignment]

from .support_pilot import (
    _detect_queue,
    _extract_ticket_code,
    _get_support_status,
    _handoff_create_response,
    _handoff_protocol_response,
    _handoff_status_response,
    _handoff_summary_response,
    _internal_post,
    _is_protocol_request,
    _is_repair_turn,
    _is_status_request,
    _is_summary_request,
    _repair_response,
    _wants_human_handoff,
)


class SupportFlowState(BaseModel):
    message: str = ''
    conversation_id: str | None = None
    telegram_chat_id: int | None = None
    channel: str = 'telegram'
    normalized_message: str = ''
    routing_label: str = 'prepare'
    reason: str = ''
    ticket_code: str | None = None
    queue_name: str | None = None
    current_item: dict[str, Any] | None = None
    latency_ms: float = 0.0


class SupportShadowFlow(Flow[SupportFlowState]):
    def __init__(self, *, settings: Any) -> None:
        self.settings = settings
        self._overall_started_at = perf_counter()
        super().__init__(tracing=False)

    @start()
    async def prepare_context(self) -> str:
        self._overall_started_at = perf_counter()
        self.state.normalized_message = self.state.message.strip().lower()
        conversation_external_id = str(self.state.conversation_id or '').strip()
        if not conversation_external_id:
            self.state.routing_label = 'missing_conversation'
            self.state.reason = 'missing_conversation_id_for_support'
            return self.state.routing_label

        self.state.ticket_code = _extract_ticket_code(self.state.message)
        support_status = await _get_support_status(
            self.settings,
            conversation_id=conversation_external_id,
            channel=self.state.channel,
            protocol_code=self.state.ticket_code,
        )
        current_item = support_status.get('item') if isinstance(support_status, dict) else None
        self.state.current_item = current_item if isinstance(current_item, dict) else None

        if _is_repair_turn(self.state.message):
            self.state.routing_label = 'repair'
            self.state.reason = 'support_repair'
            return self.state.routing_label

        if _wants_human_handoff(self.state.message):
            self.state.queue_name = _detect_queue(self.state.message)
            self.state.routing_label = 'handoff'
            self.state.reason = 'support_handoff_requested'
            return self.state.routing_label

        if isinstance(self.state.current_item, dict) and (
            _is_protocol_request(self.state.message) or _is_status_request(self.state.message) or _is_summary_request(self.state.message)
        ):
            if _is_protocol_request(self.state.message) and not _is_status_request(self.state.message):
                self.state.routing_label = 'protocol'
                self.state.reason = 'support_protocol'
            elif _is_summary_request(self.state.message):
                self.state.routing_label = 'summary'
                self.state.reason = 'support_summary'
            else:
                self.state.routing_label = 'status'
                self.state.reason = 'support_status'
            return self.state.routing_label

        self.state.routing_label = 'not_supported'
        self.state.reason = 'support_not_supported'
        return self.state.routing_label

    @router(prepare_context)
    def route(self) -> str:
        return self.state.routing_label

    def _base_metadata(self) -> dict[str, Any]:
        return {
            'slice_name': 'support',
            'conversation_id': self.state.conversation_id,
            'normalized_message': self.state.normalized_message,
            'flow_enabled': True,
            'flow_state_id': getattr(self.state, 'id', None),
        }

    def _finish(self, answer_text: str | None = None, *, extra: dict[str, Any] | None = None) -> dict[str, Any]:
        self.state.latency_ms = round((perf_counter() - self._overall_started_at) * 1000, 1)
        metadata = {
            **self._base_metadata(),
            'latency_ms': self.state.latency_ms,
            'validation_stack': ['flow_router', 'deterministic_support'],
        }
        if answer_text is not None:
            metadata['answer'] = {'answer_text': answer_text}
        if extra:
            metadata.update(extra)
        return metadata

    @listen('missing_conversation')
    def handle_missing_conversation(self) -> dict[str, Any]:
        return {
            'engine_name': 'crewai',
            'executed': False,
            'reason': self.state.reason,
            'metadata': self._finish(),
        }

    @listen('repair')
    def handle_repair(self) -> dict[str, Any]:
        return {
            'engine_name': 'crewai',
            'executed': True,
            'reason': 'support_repair',
            'metadata': self._finish(_repair_response()),
        }

    @listen('handoff')
    async def handle_handoff(self) -> dict[str, Any]:
        payload = await _internal_post(
            self.settings,
            '/v1/internal/support/handoffs',
            payload={
                'conversation_external_id': str(self.state.conversation_id or ''),
                'channel': self.state.channel,
                'queue_name': self.state.queue_name,
                'summary': f'Atendimento humano solicitado para {self.state.queue_name}',
                'telegram_chat_id': self.state.telegram_chat_id,
                'user_message': self.state.message,
            },
        )
        item = payload.get('item') if isinstance(payload, dict) else {}
        created = bool(payload.get('created'))
        return {
            'engine_name': 'crewai',
            'executed': True,
            'reason': 'support_handoff_created' if created else 'support_handoff_reused',
            'metadata': self._finish(
                _handoff_create_response(item, created=created),
                extra={
                    'queue_name': self.state.queue_name,
                    'created': created,
                },
            ),
        }

    @listen('protocol')
    def handle_protocol(self) -> dict[str, Any]:
        return {
            'engine_name': 'crewai',
            'executed': True,
            'reason': 'support_protocol',
            'metadata': self._finish(
                _handoff_protocol_response(self.state.current_item or {}),
                extra={'ticket_code': (self.state.current_item or {}).get('protocol_code')},
            ),
        }

    @listen('summary')
    def handle_summary(self) -> dict[str, Any]:
        return {
            'engine_name': 'crewai',
            'executed': True,
            'reason': 'support_summary',
            'metadata': self._finish(
                _handoff_summary_response(self.state.current_item or {}),
                extra={'ticket_code': (self.state.current_item or {}).get('protocol_code')},
            ),
        }

    @listen('status')
    def handle_status(self) -> dict[str, Any]:
        return {
            'engine_name': 'crewai',
            'executed': True,
            'reason': 'support_status',
            'metadata': self._finish(
                _handoff_status_response(self.state.current_item or {}),
                extra={'ticket_code': (self.state.current_item or {}).get('protocol_code')},
            ),
        }

    @listen('not_supported')
    def handle_not_supported(self) -> dict[str, Any]:
        return {
            'engine_name': 'crewai',
            'executed': False,
            'reason': 'support_not_supported',
            'metadata': self._finish(),
        }
