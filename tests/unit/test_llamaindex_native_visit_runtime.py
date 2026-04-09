from __future__ import annotations

import asyncio
from types import SimpleNamespace

from ai_orchestrator.entity_resolution import resolve_entity_hints
from ai_orchestrator.llamaindex_kernel import KernelPlan
from ai_orchestrator.llamaindex_native_runtime import maybe_execute_llamaindex_native_plan
from ai_orchestrator.models import (
    AccessTier,
    IntentClassification,
    MessageResponseRequest,
    OrchestrationMode,
    OrchestrationPreview,
    QueryDomain,
    UserContext,
    UserRole,
)


def _plan() -> KernelPlan:
    return KernelPlan(
        stack_name='llamaindex',
        mode='native',
        slice_name='unit',
        preview=OrchestrationPreview(
            mode=OrchestrationMode.clarify,
            classification=IntentClassification(
                domain=QueryDomain.institution,
                access_tier=AccessTier.public,
                confidence=0.5,
                reason='ambiguous',
            ),
            selected_tools=[],
            reason='clarify',
            output_contract='',
        ),
        entities=resolve_entity_hints(''),
        execution_steps=[],
        plan_notes=[],
    )


def _request(message: str) -> MessageResponseRequest:
    return MessageResponseRequest(
        message=message,
        conversation_id='conv-visit',
        telegram_chat_id=1649845499,
        user=UserContext(
            role=UserRole.guardian,
            authenticated=True,
            linked_student_ids=['stu-lucas'],
            scopes=[],
        ),
    )


def test_llamaindex_native_opens_visit_workflow_for_natural_booking(monkeypatch) -> None:
    async def _restricted_fast_path(**kwargs):
        return None

    async def _fetch_actor_context(**kwargs):
        return {'full_name': 'Maria Oliveira'}

    async def _fetch_conversation_context(**kwargs):
        return {'recent_messages': []}

    async def _fetch_public_school_profile(**kwargs):
        return {'school_name': 'Colegio Horizonte'}

    async def _create_visit_booking(**kwargs):
        return {'item': {'protocol_code': 'VIS-123', 'queue_name': 'admissions', 'linked_ticket_code': 'ATD-1'}}

    async def _persist_turn(**kwargs):
        return None

    async def _persist_trace(**kwargs):
        return None

    monkeypatch.setattr('ai_orchestrator.llamaindex_native_runtime._maybe_execute_llamaindex_restricted_doc_fast_path', _restricted_fast_path)
    monkeypatch.setattr('ai_orchestrator.llamaindex_native_runtime.rt._fetch_actor_context', _fetch_actor_context)
    monkeypatch.setattr('ai_orchestrator.llamaindex_native_runtime.rt._fetch_conversation_context', _fetch_conversation_context)
    monkeypatch.setattr('ai_orchestrator.llamaindex_native_runtime.rt._conversation_context_payload', lambda bundle: {})
    monkeypatch.setattr('ai_orchestrator.llamaindex_native_runtime.rt._recent_conversation_focus', lambda ctx: None)
    monkeypatch.setattr('ai_orchestrator.llamaindex_native_runtime.rt._fetch_public_school_profile', _fetch_public_school_profile)
    monkeypatch.setattr('ai_orchestrator.llamaindex_native_runtime.rt._create_visit_booking', _create_visit_booking)
    monkeypatch.setattr(
        'ai_orchestrator.llamaindex_native_runtime.rt._compose_visit_booking_answer',
        lambda payload, profile: f"Pedido de visita registrado para {profile['school_name']} com protocolo {payload['item']['protocol_code']}.",
    )
    monkeypatch.setattr('ai_orchestrator.llamaindex_native_runtime.rt._build_suggested_replies', lambda **kwargs: [])
    monkeypatch.setattr('ai_orchestrator.llamaindex_native_runtime.rt._persist_conversation_turn', _persist_turn)
    monkeypatch.setattr('ai_orchestrator.llamaindex_native_runtime.rt._persist_operational_trace', _persist_trace)
    monkeypatch.setattr('ai_orchestrator.llamaindex_native_runtime.record_stack_outcome', lambda **kwargs: None)

    result = asyncio.run(
        maybe_execute_llamaindex_native_plan(
            request=_request('Quero visitar a escola na sexta de manha.'),
            settings=SimpleNamespace(),
            plan=_plan(),
            engine_name='llamaindex',
            engine_mode='native',
        )
    )
    assert result is not None
    assert result.response['reason'] == 'llamaindex_visit_booking_request'
    assert result.response['classification']['domain'] == 'support'
    assert 'schedule_school_visit' in result.response['selected_tools']
    assert 'VIS-123' in result.response['message_text']


def test_llamaindex_native_updates_visit_workflow_for_reschedule_followup(monkeypatch) -> None:
    async def _restricted_fast_path(**kwargs):
        return None

    async def _fetch_actor_context(**kwargs):
        return {'full_name': 'Maria Oliveira'}

    async def _fetch_conversation_context(**kwargs):
        return {'recent_messages': []}

    async def _fetch_public_school_profile(**kwargs):
        return {'school_name': 'Colegio Horizonte'}

    async def _update_visit_booking(**kwargs):
        return {'item': {'protocol_code': 'VIS-123', 'queue_name': 'admissions', 'linked_ticket_code': 'ATD-1'}}

    async def _persist_turn(**kwargs):
        return None

    async def _persist_trace(**kwargs):
        return None

    monkeypatch.setattr('ai_orchestrator.llamaindex_native_runtime._maybe_execute_llamaindex_restricted_doc_fast_path', _restricted_fast_path)
    monkeypatch.setattr('ai_orchestrator.llamaindex_native_runtime.rt._fetch_actor_context', _fetch_actor_context)
    monkeypatch.setattr('ai_orchestrator.llamaindex_native_runtime.rt._fetch_conversation_context', _fetch_conversation_context)
    monkeypatch.setattr('ai_orchestrator.llamaindex_native_runtime.rt._conversation_context_payload', lambda bundle: {})
    monkeypatch.setattr('ai_orchestrator.llamaindex_native_runtime.rt._recent_conversation_focus', lambda ctx: {'kind': 'visit'})
    monkeypatch.setattr('ai_orchestrator.llamaindex_native_runtime.rt._fetch_public_school_profile', _fetch_public_school_profile)
    monkeypatch.setattr('ai_orchestrator.llamaindex_native_runtime.rt._update_visit_booking', _update_visit_booking)
    monkeypatch.setattr(
        'ai_orchestrator.llamaindex_native_runtime.rt._compose_visit_booking_action_answer',
        lambda payload, request_message: f"Visita atualizada com protocolo {payload['item']['protocol_code']}.",
    )
    monkeypatch.setattr('ai_orchestrator.llamaindex_native_runtime.rt._build_suggested_replies', lambda **kwargs: [])
    monkeypatch.setattr('ai_orchestrator.llamaindex_native_runtime.rt._persist_conversation_turn', _persist_turn)
    monkeypatch.setattr('ai_orchestrator.llamaindex_native_runtime.rt._persist_operational_trace', _persist_trace)
    monkeypatch.setattr('ai_orchestrator.llamaindex_native_runtime.record_stack_outcome', lambda **kwargs: None)

    result = asyncio.run(
        maybe_execute_llamaindex_native_plan(
            request=_request('Se eu precisar trocar o horario depois, por onde remarco?'),
            settings=SimpleNamespace(),
            plan=_plan(),
            engine_name='llamaindex',
            engine_mode='native',
        )
    )
    assert result is not None
    assert result.response['reason'] == 'llamaindex_visit_update_followup'
    assert result.response['classification']['domain'] == 'support'
    assert 'update_visit_booking' in result.response['selected_tools']
    assert 'VIS-123' in result.response['message_text']


def test_llamaindex_native_updates_visit_workflow_for_resume_followup(monkeypatch) -> None:
    async def _restricted_fast_path(**kwargs):
        return None

    async def _fetch_actor_context(**kwargs):
        return {'full_name': 'Maria Oliveira'}

    async def _fetch_conversation_context(**kwargs):
        return {'recent_messages': []}

    async def _fetch_public_school_profile(**kwargs):
        return {'school_name': 'Colegio Horizonte'}

    async def _update_visit_booking(**kwargs):
        return {'item': {'protocol_code': 'VIS-123', 'queue_name': 'admissions', 'linked_ticket_code': 'ATD-1'}}

    async def _persist_turn(**kwargs):
        return None

    async def _persist_trace(**kwargs):
        return None

    monkeypatch.setattr('ai_orchestrator.llamaindex_native_runtime._maybe_execute_llamaindex_restricted_doc_fast_path', _restricted_fast_path)
    monkeypatch.setattr('ai_orchestrator.llamaindex_native_runtime.rt._fetch_actor_context', _fetch_actor_context)
    monkeypatch.setattr('ai_orchestrator.llamaindex_native_runtime.rt._fetch_conversation_context', _fetch_conversation_context)
    monkeypatch.setattr('ai_orchestrator.llamaindex_native_runtime.rt._conversation_context_payload', lambda bundle: {})
    monkeypatch.setattr('ai_orchestrator.llamaindex_native_runtime.rt._recent_conversation_focus', lambda ctx: {'kind': 'visit'})
    monkeypatch.setattr('ai_orchestrator.llamaindex_native_runtime.rt._fetch_public_school_profile', _fetch_public_school_profile)
    monkeypatch.setattr('ai_orchestrator.llamaindex_native_runtime.rt._update_visit_booking', _update_visit_booking)
    monkeypatch.setattr(
        'ai_orchestrator.llamaindex_native_runtime.rt._compose_visit_booking_action_answer',
        lambda payload, request_message: f"Para retomar a visita, use o protocolo {payload['item']['protocol_code']}.",
    )
    monkeypatch.setattr('ai_orchestrator.llamaindex_native_runtime.rt._build_suggested_replies', lambda **kwargs: [])
    monkeypatch.setattr('ai_orchestrator.llamaindex_native_runtime.rt._persist_conversation_turn', _persist_turn)
    monkeypatch.setattr('ai_orchestrator.llamaindex_native_runtime.rt._persist_operational_trace', _persist_trace)
    monkeypatch.setattr('ai_orchestrator.llamaindex_native_runtime.record_stack_outcome', lambda **kwargs: None)

    result = asyncio.run(
        maybe_execute_llamaindex_native_plan(
            request=_request('E se eu quiser retomar depois, por onde volto?'),
            settings=SimpleNamespace(),
            plan=_plan(),
            engine_name='llamaindex',
            engine_mode='native',
        )
    )
    assert result is not None
    assert result.response['reason'] == 'llamaindex_visit_update_followup'
    assert result.response['classification']['domain'] == 'support'
    assert 'update_visit_booking' in result.response['selected_tools']
    assert 'retomar a visita' in result.response['message_text'].lower()
