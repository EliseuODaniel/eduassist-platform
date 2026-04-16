from __future__ import annotations

import asyncio
from types import SimpleNamespace

from eduassist_semantic_ingress import IngressSemanticPlan, TurnFrame

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
from ai_orchestrator.entity_resolution import resolve_entity_hints
from ai_orchestrator.python_functions_kernel import KernelPlan
from ai_orchestrator.python_functions_kernel_runtime import _maybe_contextual_public_direct_answer
from ai_orchestrator.python_functions_native_runtime import (
    _should_use_python_functions_native_path,
    maybe_execute_python_functions_native_plan,
)


def _plan() -> KernelPlan:
    return KernelPlan(
        stack_name='python_functions',
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


def test_python_functions_native_opens_visit_workflow_for_natural_booking(monkeypatch) -> None:
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

    monkeypatch.setattr('ai_orchestrator.python_functions_native_runtime.rt._fetch_actor_context', _fetch_actor_context)
    monkeypatch.setattr('ai_orchestrator.python_functions_native_runtime.rt._fetch_conversation_context', _fetch_conversation_context)
    monkeypatch.setattr('ai_orchestrator.python_functions_native_runtime.rt._conversation_context_payload', lambda bundle: {})
    monkeypatch.setattr('ai_orchestrator.python_functions_native_runtime.rt._recent_conversation_focus', lambda ctx: None)
    monkeypatch.setattr('ai_orchestrator.python_functions_native_runtime.rt._build_analysis_message', lambda message, bundle: message)
    monkeypatch.setattr('ai_orchestrator.python_functions_native_runtime.rt._fetch_public_school_profile', _fetch_public_school_profile)
    monkeypatch.setattr('ai_orchestrator.python_functions_native_runtime.rt._create_visit_booking', _create_visit_booking)
    monkeypatch.setattr(
        'ai_orchestrator.python_functions_native_runtime.rt._compose_visit_booking_answer',
        lambda payload, profile: f"Pedido de visita registrado para {profile['school_name']} com protocolo {payload['item']['protocol_code']}.",
    )
    monkeypatch.setattr('ai_orchestrator.python_functions_native_runtime.rt._build_suggested_replies', lambda **kwargs: [])
    monkeypatch.setattr('ai_orchestrator.python_functions_native_runtime.rt._persist_conversation_turn', _persist_turn)
    monkeypatch.setattr('ai_orchestrator.python_functions_native_runtime.rt._persist_operational_trace', _persist_trace)
    monkeypatch.setattr('ai_orchestrator.python_functions_native_runtime.record_stack_outcome', lambda **kwargs: None)

    result = asyncio.run(
        maybe_execute_python_functions_native_plan(
            request=_request('Quero visitar a escola na sexta de manha.'),
            settings=SimpleNamespace(),
            plan=_plan(),
            engine_name='python_functions',
            engine_mode='native',
        )
    )
    assert result is not None
    assert result.response['reason'] == 'python_functions_native_visit_booking_request'
    assert result.response['classification']['domain'] == 'support'
    assert 'schedule_school_visit' in result.response['selected_tools']
    assert 'protocolo VIS-123' in result.response['message_text']


def test_python_functions_native_updates_visit_workflow_for_reschedule_followup(monkeypatch) -> None:
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

    monkeypatch.setattr('ai_orchestrator.python_functions_native_runtime.rt._fetch_actor_context', _fetch_actor_context)
    monkeypatch.setattr('ai_orchestrator.python_functions_native_runtime.rt._fetch_conversation_context', _fetch_conversation_context)
    monkeypatch.setattr('ai_orchestrator.python_functions_native_runtime.rt._conversation_context_payload', lambda bundle: {})
    monkeypatch.setattr('ai_orchestrator.python_functions_native_runtime.rt._recent_conversation_focus', lambda ctx: {'kind': 'visit'})
    monkeypatch.setattr('ai_orchestrator.python_functions_native_runtime.rt._build_analysis_message', lambda message, bundle: message)
    monkeypatch.setattr('ai_orchestrator.python_functions_native_runtime.rt._fetch_public_school_profile', _fetch_public_school_profile)
    monkeypatch.setattr('ai_orchestrator.python_functions_native_runtime.rt._update_visit_booking', _update_visit_booking)
    monkeypatch.setattr(
        'ai_orchestrator.python_functions_native_runtime.rt._compose_visit_booking_action_answer',
        lambda payload, request_message: f"Visita atualizada com protocolo {payload['item']['protocol_code']}.",
    )
    monkeypatch.setattr('ai_orchestrator.python_functions_native_runtime.rt._build_suggested_replies', lambda **kwargs: [])
    monkeypatch.setattr('ai_orchestrator.python_functions_native_runtime.rt._persist_conversation_turn', _persist_turn)
    monkeypatch.setattr('ai_orchestrator.python_functions_native_runtime.rt._persist_operational_trace', _persist_trace)
    monkeypatch.setattr('ai_orchestrator.python_functions_native_runtime.record_stack_outcome', lambda **kwargs: None)

    result = asyncio.run(
        maybe_execute_python_functions_native_plan(
            request=_request('Se eu precisar trocar o horario depois, por onde remarco?'),
            settings=SimpleNamespace(),
            plan=_plan(),
            engine_name='python_functions',
            engine_mode='native',
        )
    )
    assert result is not None
    assert result.response['reason'] == 'python_functions_native_visit_update_followup'
    assert result.response['classification']['domain'] == 'support'
    assert 'update_visit_booking' in result.response['selected_tools']
    assert 'VIS-123' in result.response['message_text']


def test_python_functions_native_updates_visit_workflow_for_resume_followup(monkeypatch) -> None:
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

    monkeypatch.setattr('ai_orchestrator.python_functions_native_runtime.rt._fetch_actor_context', _fetch_actor_context)
    monkeypatch.setattr('ai_orchestrator.python_functions_native_runtime.rt._fetch_conversation_context', _fetch_conversation_context)
    monkeypatch.setattr('ai_orchestrator.python_functions_native_runtime.rt._conversation_context_payload', lambda bundle: {})
    monkeypatch.setattr('ai_orchestrator.python_functions_native_runtime.rt._recent_conversation_focus', lambda ctx: {'kind': 'visit'})
    monkeypatch.setattr('ai_orchestrator.python_functions_native_runtime.rt._build_analysis_message', lambda message, bundle: message)
    monkeypatch.setattr('ai_orchestrator.python_functions_native_runtime.rt._fetch_public_school_profile', _fetch_public_school_profile)
    monkeypatch.setattr('ai_orchestrator.python_functions_native_runtime.rt._update_visit_booking', _update_visit_booking)
    monkeypatch.setattr(
        'ai_orchestrator.python_functions_native_runtime.rt._compose_visit_booking_action_answer',
        lambda payload, request_message: f"Para retomar a visita, use o protocolo {payload['item']['protocol_code']}.",
    )
    monkeypatch.setattr('ai_orchestrator.python_functions_native_runtime.rt._build_suggested_replies', lambda **kwargs: [])
    monkeypatch.setattr('ai_orchestrator.python_functions_native_runtime.rt._persist_conversation_turn', _persist_turn)
    monkeypatch.setattr('ai_orchestrator.python_functions_native_runtime.rt._persist_operational_trace', _persist_trace)
    monkeypatch.setattr('ai_orchestrator.python_functions_native_runtime.record_stack_outcome', lambda **kwargs: None)

    result = asyncio.run(
        maybe_execute_python_functions_native_plan(
            request=_request('E se eu quiser retomar depois, por onde volto?'),
            settings=SimpleNamespace(),
            plan=_plan(),
            engine_name='python_functions',
            engine_mode='native',
        )
    )
    assert result is not None
    assert result.response['reason'] == 'python_functions_native_visit_update_followup'
    assert result.response['classification']['domain'] == 'support'
    assert 'update_visit_booking' in result.response['selected_tools']
    assert 'retomar a visita' in result.response['message_text'].lower()


def test_python_functions_native_forces_teacher_boundary_from_public_clarify(monkeypatch) -> None:
    async def _fetch_actor_context(**kwargs):
        return None

    async def _fetch_conversation_context(**kwargs):
        return {'recent_messages': []}

    async def _fetch_public_school_profile(**kwargs):
        return {'school_name': 'Colegio Horizonte'}

    async def _persist_turn(**kwargs):
        return None

    async def _persist_trace(**kwargs):
        return None

    monkeypatch.setattr('ai_orchestrator.python_functions_native_runtime.rt._fetch_actor_context', _fetch_actor_context)
    monkeypatch.setattr('ai_orchestrator.python_functions_native_runtime.rt._fetch_conversation_context', _fetch_conversation_context)
    monkeypatch.setattr('ai_orchestrator.python_functions_native_runtime.rt._conversation_context_payload', lambda bundle: {})
    monkeypatch.setattr('ai_orchestrator.python_functions_native_runtime.rt._recent_conversation_focus', lambda ctx: None)
    monkeypatch.setattr('ai_orchestrator.python_functions_native_runtime.rt._build_analysis_message', lambda message, bundle: message)
    monkeypatch.setattr('ai_orchestrator.python_functions_native_runtime.rt._fetch_public_school_profile', _fetch_public_school_profile)
    monkeypatch.setattr('ai_orchestrator.python_functions_native_runtime.rt._build_suggested_replies', lambda **kwargs: [])
    monkeypatch.setattr('ai_orchestrator.python_functions_native_runtime.rt._persist_conversation_turn', _persist_turn)
    monkeypatch.setattr('ai_orchestrator.python_functions_native_runtime.rt._persist_operational_trace', _persist_trace)
    monkeypatch.setattr('ai_orchestrator.python_functions_native_runtime.record_stack_outcome', lambda **kwargs: None)

    plan = _plan().model_copy(
        update={
            'preview': _plan().preview.model_copy(
                update={
                    'classification': IntentClassification(
                        domain=QueryDomain.academic,
                        access_tier=AccessTier.public,
                        confidence=0.4,
                        reason='ambiguous',
                    ),
                    'reason': 'python_functions_local_clarify',
                }
            )
        }
    )
    request = MessageResponseRequest(
        message='Quero falar com o professor de matematica.',
        conversation_id='conv-teacher',
        channel='api',
        user=UserContext(role=UserRole.anonymous, authenticated=False, linked_student_ids=[], scopes=[]),
    )

    result = asyncio.run(
        maybe_execute_python_functions_native_plan(
            request=request,
            settings=SimpleNamespace(),
            plan=plan,
            engine_name='python_functions',
            engine_mode='native',
        )
    )

    assert result is not None
    assert result.response['reason'] == 'deterministic_teacher_directory_boundary'
    assert 'coordenacao pedagogica' in result.response['message_text'].lower()


def test_python_functions_native_uses_semantic_ingress_plan_before_admin_fallback(monkeypatch) -> None:
    async def _fetch_actor_context(**kwargs):
        return {'full_name': 'Maria Oliveira', 'linked_students': [{'student_id': 'stu-lucas'}]}

    async def _fetch_conversation_context(**kwargs):
        return {'recent_messages': []}

    async def _fetch_public_school_profile(**kwargs):
        return {'school_name': 'Colegio Horizonte'}

    async def _persist_turn(**kwargs):
        return None

    async def _persist_trace(**kwargs):
        return None

    async def _semantic_ingress(**kwargs):
        return IngressSemanticPlan(
            conversation_act='greeting',
            use_conversation_context=False,
            confidence_bucket='high',
            reason='saudacao informal reconhecida',
        )

    async def _no_contextual_public_answer(**kwargs):
        return None

    def _unexpected_rescue(**kwargs):
        raise AssertionError('protected_domain_rescue_should_not_run')

    monkeypatch.setattr('ai_orchestrator.python_functions_native_runtime.rt._fetch_actor_context', _fetch_actor_context)
    monkeypatch.setattr('ai_orchestrator.python_functions_native_runtime.rt._fetch_conversation_context', _fetch_conversation_context)
    monkeypatch.setattr('ai_orchestrator.python_functions_native_runtime.rt._conversation_context_payload', lambda bundle: {})
    monkeypatch.setattr('ai_orchestrator.python_functions_native_runtime.rt._recent_conversation_focus', lambda ctx: None)
    monkeypatch.setattr('ai_orchestrator.python_functions_native_runtime.rt._build_analysis_message', lambda message, bundle: message)
    monkeypatch.setattr('ai_orchestrator.python_functions_native_runtime.rt._fetch_public_school_profile', _fetch_public_school_profile)
    monkeypatch.setattr('ai_orchestrator.python_functions_native_runtime.rt._build_suggested_replies', lambda **kwargs: [])
    monkeypatch.setattr('ai_orchestrator.python_functions_native_runtime.rt._persist_conversation_turn', _persist_turn)
    monkeypatch.setattr('ai_orchestrator.python_functions_native_runtime.rt._persist_operational_trace', _persist_trace)
    monkeypatch.setattr('ai_orchestrator.python_functions_native_runtime.record_stack_outcome', lambda **kwargs: None)
    monkeypatch.setattr('ai_orchestrator.python_functions_native_runtime.rt._apply_protected_domain_rescue', _unexpected_rescue)
    monkeypatch.setattr(
        'ai_orchestrator.python_functions_native_runtime.maybe_resolve_semantic_ingress_plan',
        _semantic_ingress,
    )
    monkeypatch.setattr(
        'ai_orchestrator.python_functions_native_runtime._maybe_contextual_public_direct_answer',
        _no_contextual_public_answer,
    )
    monkeypatch.setattr(
        'ai_orchestrator.python_functions_native_runtime._maybe_public_unpublished_direct_answer',
        lambda **kwargs: None,
    )
    monkeypatch.setattr(
        'ai_orchestrator.python_functions_native_runtime._maybe_hypothetical_public_pricing_answer',
        lambda **kwargs: None,
    )

    result = asyncio.run(
        maybe_execute_python_functions_native_plan(
            request=_request('boa madruga'),
            settings=SimpleNamespace(),
            plan=_plan(),
            engine_name='python_functions',
            engine_mode='native',
        )
    )

    assert result is not None
    assert result.response['reason'] == 'python_functions_native_semantic_ingress:greeting'
    assert 'semantic_ingress_classifier' in result.response['llm_stages']
    lowered = result.response['message_text'].lower()
    assert 'como posso ajudar' in lowered or 'eduassist' in lowered
    assert 'cadastro' not in lowered


def test_python_functions_native_uses_language_preference_semantic_ingress_before_subject_disambiguation(
    monkeypatch,
) -> None:
    async def _fetch_actor_context(**kwargs):
        return {'full_name': 'Maria Oliveira', 'linked_students': [{'student_id': 'stu-lucas'}]}

    async def _fetch_conversation_context(**kwargs):
        return {
            'recent_messages': [
                {'sender_type': 'assistant', 'content': 'Você quer consultar Língua Inglesa de qual aluno: Lucas Oliveira ou Ana Oliveira?'}
            ]
        }

    async def _fetch_public_school_profile(**kwargs):
        return {'school_name': 'Colegio Horizonte'}

    async def _persist_turn(**kwargs):
        return None

    async def _persist_trace(**kwargs):
        return None

    async def _semantic_ingress(**kwargs):
        return IngressSemanticPlan(
            conversation_act='language_preference',
            use_conversation_context=False,
            confidence_bucket='high',
            reason='preferencia de idioma detectada',
        )

    monkeypatch.setattr('ai_orchestrator.python_functions_native_runtime.rt._fetch_actor_context', _fetch_actor_context)
    monkeypatch.setattr('ai_orchestrator.python_functions_native_runtime.rt._fetch_conversation_context', _fetch_conversation_context)
    monkeypatch.setattr('ai_orchestrator.python_functions_native_runtime.rt._conversation_context_payload', lambda bundle: {})
    monkeypatch.setattr('ai_orchestrator.python_functions_native_runtime.rt._recent_conversation_focus', lambda ctx: None)
    monkeypatch.setattr('ai_orchestrator.python_functions_native_runtime.rt._build_analysis_message', lambda message, bundle: message)
    monkeypatch.setattr('ai_orchestrator.python_functions_native_runtime.rt._fetch_public_school_profile', _fetch_public_school_profile)
    monkeypatch.setattr('ai_orchestrator.python_functions_native_runtime.rt._build_suggested_replies', lambda **kwargs: [])
    monkeypatch.setattr('ai_orchestrator.python_functions_native_runtime.rt._persist_conversation_turn', _persist_turn)
    monkeypatch.setattr('ai_orchestrator.python_functions_native_runtime.rt._persist_operational_trace', _persist_trace)
    monkeypatch.setattr('ai_orchestrator.python_functions_native_runtime.record_stack_outcome', lambda **kwargs: None)
    monkeypatch.setattr(
        'ai_orchestrator.python_functions_native_runtime.maybe_resolve_semantic_ingress_plan',
        _semantic_ingress,
    )
    async def _no_contextual_public_answer(**kwargs):
        return None

    def _no_unpublished_public_answer(**kwargs):
        return None

    def _no_hypothetical_public_pricing(**kwargs):
        return None

    monkeypatch.setattr(
        'ai_orchestrator.python_functions_native_runtime._maybe_contextual_public_direct_answer',
        _no_contextual_public_answer,
    )
    monkeypatch.setattr(
        'ai_orchestrator.python_functions_native_runtime._maybe_public_unpublished_direct_answer',
        _no_unpublished_public_answer,
    )
    monkeypatch.setattr(
        'ai_orchestrator.python_functions_native_runtime._maybe_hypothetical_public_pricing_answer',
        _no_hypothetical_public_pricing,
    )

    result = asyncio.run(
        maybe_execute_python_functions_native_plan(
            request=_request('Quero que só fale português'),
            settings=SimpleNamespace(),
            plan=_plan(),
            engine_name='python_functions',
            engine_mode='native',
        )
    )

    assert result is not None
    assert result.response['reason'] == 'python_functions_native_semantic_ingress:language_preference'
    lowered = result.response['message_text'].lower()
    assert 'portugues' in lowered or 'português' in lowered
    assert 'língua portuguesa' not in lowered and 'lingua portuguesa' not in lowered


def test_python_functions_native_uses_input_clarification_semantic_ingress_before_admin_fallback(
    monkeypatch,
) -> None:
    async def _fetch_actor_context(**kwargs):
        return {'full_name': 'Maria Oliveira', 'linked_students': [{'student_id': 'stu-lucas'}]}

    async def _fetch_conversation_context(**kwargs):
        return {'recent_messages': []}

    async def _fetch_public_school_profile(**kwargs):
        return {'school_name': 'Colegio Horizonte'}

    async def _persist_turn(**kwargs):
        return None

    async def _persist_trace(**kwargs):
        return None

    async def _semantic_ingress(**kwargs):
        return IngressSemanticPlan(
            conversation_act='input_clarification',
            use_conversation_context=False,
            confidence_bucket='medium',
            reason='opaque_short_input',
        )

    def _unexpected_rescue(**kwargs):
        raise AssertionError('protected_domain_rescue_should_not_run')

    monkeypatch.setattr('ai_orchestrator.python_functions_native_runtime.rt._fetch_actor_context', _fetch_actor_context)
    monkeypatch.setattr('ai_orchestrator.python_functions_native_runtime.rt._fetch_conversation_context', _fetch_conversation_context)
    monkeypatch.setattr('ai_orchestrator.python_functions_native_runtime.rt._conversation_context_payload', lambda bundle: {})
    monkeypatch.setattr('ai_orchestrator.python_functions_native_runtime.rt._recent_conversation_focus', lambda ctx: None)
    monkeypatch.setattr('ai_orchestrator.python_functions_native_runtime.rt._build_analysis_message', lambda message, bundle: message)
    monkeypatch.setattr('ai_orchestrator.python_functions_native_runtime.rt._fetch_public_school_profile', _fetch_public_school_profile)
    monkeypatch.setattr('ai_orchestrator.python_functions_native_runtime.rt._build_suggested_replies', lambda **kwargs: [])
    monkeypatch.setattr('ai_orchestrator.python_functions_native_runtime.rt._persist_conversation_turn', _persist_turn)
    monkeypatch.setattr('ai_orchestrator.python_functions_native_runtime.rt._persist_operational_trace', _persist_trace)
    monkeypatch.setattr('ai_orchestrator.python_functions_native_runtime.record_stack_outcome', lambda **kwargs: None)
    monkeypatch.setattr('ai_orchestrator.python_functions_native_runtime.rt._apply_protected_domain_rescue', _unexpected_rescue)
    monkeypatch.setattr(
        'ai_orchestrator.python_functions_native_runtime.maybe_resolve_semantic_ingress_plan',
        _semantic_ingress,
    )
    async def _no_contextual_public_answer(**kwargs):
        return None

    monkeypatch.setattr(
        'ai_orchestrator.python_functions_native_runtime._maybe_contextual_public_direct_answer',
        _no_contextual_public_answer,
    )
    monkeypatch.setattr(
        'ai_orchestrator.python_functions_native_runtime._maybe_public_unpublished_direct_answer',
        lambda **kwargs: None,
    )
    monkeypatch.setattr(
        'ai_orchestrator.python_functions_native_runtime._maybe_hypothetical_public_pricing_answer',
        lambda **kwargs: None,
    )

    result = asyncio.run(
        maybe_execute_python_functions_native_plan(
            request=_request('rai'),
            settings=SimpleNamespace(),
            plan=_plan(),
            engine_name='python_functions',
            engine_mode='native',
        )
    )

    assert result is not None
    assert result.response['reason'] == 'python_functions_native_semantic_ingress:input_clarification'
    lowered = result.response['message_text'].lower()
    assert 'nao consegui' in lowered or 'não consegui' in lowered
    assert 'cadastro' not in lowered


def test_python_functions_native_uses_turn_frame_public_auth_guidance_when_semantic_plan_is_absent(
    monkeypatch,
) -> None:
    async def _fetch_actor_context(**kwargs):
        return None

    async def _fetch_conversation_context(**kwargs):
        return {'recent_messages': []}

    async def _fetch_public_school_profile(**kwargs):
        return {'school_name': 'Colegio Horizonte'}

    async def _persist_turn(**kwargs):
        return None

    async def _persist_trace(**kwargs):
        return None

    async def _semantic_ingress(**kwargs):
        return None

    async def _turn_frame(**kwargs):
        return TurnFrame(
            conversation_act='auth_guidance',
            domain='institution',
            access_tier='public',
            scope='public',
            confidence=0.93,
            confidence_bucket='high',
            reason='protected_requires_auth:protected.academic.grades',
            source='heuristic',
            public_conversation_act='auth_guidance',
        )

    async def _no_contextual_public_answer(**kwargs):
        return None

    monkeypatch.setattr('ai_orchestrator.python_functions_native_runtime.rt._fetch_actor_context', _fetch_actor_context)
    monkeypatch.setattr('ai_orchestrator.python_functions_native_runtime.rt._fetch_conversation_context', _fetch_conversation_context)
    monkeypatch.setattr('ai_orchestrator.python_functions_native_runtime.rt._conversation_context_payload', lambda bundle: {})
    monkeypatch.setattr('ai_orchestrator.python_functions_native_runtime.rt._recent_conversation_focus', lambda ctx: None)
    monkeypatch.setattr('ai_orchestrator.python_functions_native_runtime.rt._build_analysis_message', lambda message, bundle: message)
    monkeypatch.setattr('ai_orchestrator.python_functions_native_runtime.rt._fetch_public_school_profile', _fetch_public_school_profile)
    monkeypatch.setattr('ai_orchestrator.python_functions_native_runtime.rt._build_suggested_replies', lambda **kwargs: [])
    monkeypatch.setattr('ai_orchestrator.python_functions_native_runtime.rt._persist_conversation_turn', _persist_turn)
    monkeypatch.setattr('ai_orchestrator.python_functions_native_runtime.rt._persist_operational_trace', _persist_trace)
    monkeypatch.setattr('ai_orchestrator.python_functions_native_runtime.record_stack_outcome', lambda **kwargs: None)
    monkeypatch.setattr('ai_orchestrator.python_functions_native_runtime.maybe_resolve_semantic_ingress_plan', _semantic_ingress)
    monkeypatch.setattr('ai_orchestrator.python_functions_native_plan_runtime.maybe_resolve_turn_frame', _turn_frame)
    monkeypatch.setattr('ai_orchestrator.python_functions_native_runtime._maybe_contextual_public_direct_answer', _no_contextual_public_answer)
    monkeypatch.setattr('ai_orchestrator.python_functions_native_runtime._maybe_public_unpublished_direct_answer', lambda **kwargs: None)
    monkeypatch.setattr('ai_orchestrator.python_functions_native_runtime._maybe_hypothetical_public_pricing_answer', lambda **kwargs: None)

    request = MessageResponseRequest(
        message='Nao estou autenticado e mesmo assim quero consultar meu boletim aqui pelo bot.',
        conversation_id='conv-auth-guidance',
        channel='api',
        user=UserContext(role=UserRole.anonymous, authenticated=False, linked_student_ids=[], scopes=[]),
    )

    result = asyncio.run(
        maybe_execute_python_functions_native_plan(
            request=request,
            settings=SimpleNamespace(),
            plan=_plan(),
            engine_name='python_functions',
            engine_mode='native',
        )
    )

    assert result is not None
    assert result.response['reason'] == 'python_functions_native_semantic_ingress:auth_guidance'
    assert 'vincular sua conta' in result.response['message_text'].lower()


def test_python_functions_contextual_public_direct_answer_refines_library_opening_focus(monkeypatch) -> None:
    monkeypatch.setattr(
        'ai_orchestrator.python_functions_kernel_runtime.rt._llm_forced_mode_enabled',
        lambda **_: False,
    )
    monkeypatch.setattr(
        'ai_orchestrator.python_functions_kernel_runtime.rt._base_profile_supports_fast_public_answer',
        lambda **_: False,
    )
    monkeypatch.setattr(
        'ai_orchestrator.python_functions_kernel_runtime.rt._try_public_channel_fast_answer',
        lambda **_: None,
    )
    monkeypatch.setattr(
        'ai_orchestrator.python_functions_kernel_runtime.rt._compose_public_profile_answer_agentic',
        lambda **_: asyncio.sleep(0, result='A biblioteca abre as 7h30.'),
    )

    result = asyncio.run(
        _maybe_contextual_public_direct_answer(
            request=SimpleNamespace(
                message='que horas abre a biblioteca?',
                user=SimpleNamespace(authenticated=False),
            ),
            analysis_message='que horas abre a biblioteca?',
            preview=SimpleNamespace(
                classification=SimpleNamespace(
                    access_tier=AccessTier.public,
                    domain=QueryDomain.institution,
                ),
            ),
            settings=SimpleNamespace(),
            school_profile={
                'school_name': 'Colegio Horizonte',
                'feature_catalog': [
                    {'name': 'Biblioteca Aurora', 'label': 'Biblioteca Aurora', 'note': 'de segunda a sexta, das 7h30 as 18h00'}
                ],
            },
            conversation_context={'recent_messages': []},
        )
    )

    assert result == 'A biblioteca abre as 7h30.'


def test_python_functions_contextual_public_direct_answer_refines_library_closing_focus(monkeypatch) -> None:
    monkeypatch.setattr(
        'ai_orchestrator.python_functions_kernel_runtime.rt._llm_forced_mode_enabled',
        lambda **_: False,
    )
    monkeypatch.setattr(
        'ai_orchestrator.python_functions_kernel_runtime.rt._base_profile_supports_fast_public_answer',
        lambda **_: False,
    )
    monkeypatch.setattr(
        'ai_orchestrator.python_functions_kernel_runtime.rt._try_public_channel_fast_answer',
        lambda **_: None,
    )
    monkeypatch.setattr(
        'ai_orchestrator.python_functions_kernel_runtime.rt._compose_public_profile_answer_agentic',
        lambda **_: asyncio.sleep(0, result='A biblioteca fecha as 18h00.'),
    )

    result = asyncio.run(
        _maybe_contextual_public_direct_answer(
            request=SimpleNamespace(
                message='qual horário de fechamento da biblioteca?',
                user=SimpleNamespace(authenticated=False),
            ),
            analysis_message='qual horário de fechamento da biblioteca?',
            preview=SimpleNamespace(
                classification=SimpleNamespace(
                    access_tier=AccessTier.public,
                    domain=QueryDomain.institution,
                ),
            ),
            settings=SimpleNamespace(),
            school_profile={
                'school_name': 'Colegio Horizonte',
                'feature_catalog': [
                    {'name': 'Biblioteca Aurora', 'label': 'Biblioteca Aurora', 'note': 'de segunda a sexta, das 7h30 as 18h00'}
                ],
            },
            conversation_context={'recent_messages': []},
        )
    )

    assert result == 'A biblioteca fecha as 18h00.'


def test_python_functions_contextual_public_direct_answer_respects_external_city_library_scope_boundary(
    monkeypatch,
) -> None:
    monkeypatch.setattr(
        'ai_orchestrator.python_functions_kernel_runtime.rt._llm_forced_mode_enabled',
        lambda **_: False,
    )
    monkeypatch.setattr(
        'ai_orchestrator.python_functions_kernel_runtime.rt._compose_external_public_facility_boundary_answer',
        lambda *_args, **_kwargs: 'Boundary seguro.',
    )

    result = asyncio.run(
        _maybe_contextual_public_direct_answer(
            request=SimpleNamespace(
                message='qual horário de fechamento da biblioteca pública da cidade?',
                user=SimpleNamespace(authenticated=False),
            ),
            analysis_message='qual horário de fechamento da biblioteca pública da cidade?',
            preview=SimpleNamespace(
                classification=SimpleNamespace(
                    access_tier=AccessTier.public,
                    domain=QueryDomain.unknown,
                ),
                graph_path=['turn_frame:scope_boundary'],
            ),
            settings=SimpleNamespace(),
            school_profile={
                'school_name': 'Colegio Horizonte',
                'feature_catalog': [
                    {'name': 'Biblioteca Aurora', 'label': 'Biblioteca Aurora', 'note': 'de segunda a sexta, das 7h30 as 18h00'}
                ],
            },
            conversation_context={'recent_messages': []},
        )
    )

    assert result == 'Boundary seguro.'


def test_python_functions_contextual_public_direct_answer_respects_negated_school_library_boundary(
    monkeypatch,
) -> None:
    monkeypatch.setattr(
        'ai_orchestrator.python_functions_kernel_runtime.rt._llm_forced_mode_enabled',
        lambda **_: False,
    )
    monkeypatch.setattr(
        'ai_orchestrator.python_functions_kernel_runtime.rt._compose_external_public_facility_boundary_answer',
        lambda *_args, **_kwargs: 'Boundary seguro.',
    )

    result = asyncio.run(
        _maybe_contextual_public_direct_answer(
            request=SimpleNamespace(
                message='Nao e a biblioteca da escola: me diga o horario da biblioteca publica municipal.',
                user=SimpleNamespace(authenticated=False),
            ),
            analysis_message='Nao e a biblioteca da escola: me diga o horario da biblioteca publica municipal.',
            preview=SimpleNamespace(
                classification=SimpleNamespace(
                    access_tier=AccessTier.public,
                    domain=QueryDomain.unknown,
                ),
                graph_path=['turn_frame:scope_boundary'],
            ),
            settings=SimpleNamespace(),
            school_profile={
                'school_name': 'Colegio Horizonte',
                'feature_catalog': [
                    {'name': 'Biblioteca Aurora', 'label': 'Biblioteca Aurora', 'note': 'de segunda a sexta, das 7h30 as 18h00'}
                ],
            },
            conversation_context={'recent_messages': []},
        )
    )

    assert result == 'Boundary seguro.'


def test_python_functions_contextual_public_direct_answer_skips_restricted_document_queries(monkeypatch) -> None:
    monkeypatch.setattr(
        'ai_orchestrator.python_functions_kernel_runtime.rt._llm_forced_mode_enabled',
        lambda **_: False,
    )

    result = asyncio.run(
        _maybe_contextual_public_direct_answer(
            request=SimpleNamespace(
                message='Na rotina interna de negociacao financeira, quais validacoes antecedem qualquer promessa de quitacao?',
                user=SimpleNamespace(authenticated=True),
            ),
            analysis_message='Na rotina interna de negociacao financeira, quais validacoes antecedem qualquer promessa de quitacao?',
            preview=SimpleNamespace(
                classification=SimpleNamespace(
                    access_tier=AccessTier.public,
                    domain=QueryDomain.institution,
                ),
            ),
            settings=SimpleNamespace(),
            school_profile={'school_name': 'Colegio Horizonte'},
            conversation_context={'recent_messages': []},
        )
    )

    assert result is None


def test_python_functions_contextual_public_direct_answer_does_not_apply_scope_boundary_to_protected_turn_frame(
    monkeypatch,
) -> None:
    monkeypatch.setattr(
        'ai_orchestrator.python_functions_kernel_runtime.rt._llm_forced_mode_enabled',
        lambda **_: False,
    )
    monkeypatch.setattr(
        'ai_orchestrator.python_functions_kernel_runtime.rt.looks_like_scope_boundary_candidate',
        lambda _message: True,
    )
    monkeypatch.setattr(
        'ai_orchestrator.python_functions_kernel_runtime.rt.looks_like_school_scope_message',
        lambda _message: False,
    )

    result = asyncio.run(
        _maybe_contextual_public_direct_answer(
            request=SimpleNamespace(
                message='Entre meus filhos, quem esta mais vulneravel academicamente hoje? Me de um panorama curto.',
                user=SimpleNamespace(authenticated=True),
            ),
            analysis_message='Entre meus filhos, quem esta mais vulneravel academicamente hoje? Me de um panorama curto.',
            preview=SimpleNamespace(
                classification=SimpleNamespace(
                    access_tier=AccessTier.authenticated,
                    domain=QueryDomain.academic,
                ),
                graph_path=['turn_frame:protected.academic.family_comparison'],
            ),
            settings=SimpleNamespace(),
            school_profile={'school_name': 'Colegio Horizonte'},
            conversation_context={'recent_messages': []},
        )
    )

    assert result is None


def test_python_functions_contextual_public_direct_answer_skips_authenticated_academic_domain_without_graph_path(
    monkeypatch,
) -> None:
    monkeypatch.setattr(
        'ai_orchestrator.python_functions_kernel_runtime.rt._llm_forced_mode_enabled',
        lambda **_: False,
    )
    monkeypatch.setattr(
        'ai_orchestrator.python_functions_kernel_runtime.rt.looks_like_scope_boundary_candidate',
        lambda _message: True,
    )
    monkeypatch.setattr(
        'ai_orchestrator.python_functions_kernel_runtime.rt.looks_like_school_scope_message',
        lambda _message: False,
    )

    result = asyncio.run(
        _maybe_contextual_public_direct_answer(
            request=SimpleNamespace(
                message='Entre meus filhos, quem esta mais vulneravel academicamente hoje? Me de um panorama curto.',
                user=SimpleNamespace(authenticated=True),
            ),
            analysis_message='Entre meus filhos, quem esta mais vulneravel academicamente hoje? Me de um panorama curto.',
            preview=SimpleNamespace(
                classification=SimpleNamespace(
                    access_tier=AccessTier.authenticated,
                    domain=QueryDomain.academic,
                ),
                graph_path=[],
            ),
            settings=SimpleNamespace(),
            school_profile={'school_name': 'Colegio Horizonte'},
            conversation_context={'recent_messages': []},
        )
    )

    assert result is None


def test_python_functions_native_path_prioritizes_restricted_turn_frame_even_on_support_clarify() -> None:
    plan = KernelPlan(
        stack_name='python_functions',
        mode='native',
        slice_name='unit',
        preview=OrchestrationPreview(
            mode=OrchestrationMode.clarify,
            classification=IntentClassification(
                domain=QueryDomain.support,
                access_tier=AccessTier.authenticated,
                confidence=0.61,
                reason='ambiguous_support',
            ),
            selected_tools=['retrieve_restricted_documents'],
            graph_path=['python_functions:planner', 'turn_frame:protected.documents.restricted_lookup'],
            reason='turn_frame:protected.documents.restricted_lookup',
            output_contract='',
        ),
        entities=resolve_entity_hints(''),
        execution_steps=[],
        plan_notes=[],
    )

    assert _should_use_python_functions_native_path(plan) is True
