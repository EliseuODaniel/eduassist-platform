from __future__ import annotations

import asyncio
import json
from datetime import datetime, timezone
from types import SimpleNamespace

from ai_orchestrator import runtime as rt
from ai_orchestrator.models import (
    AccessTier,
    ConversationChannel,
    IntentClassification,
    MessageResponseRequest,
    OrchestrationMode,
    OrchestrationPreview,
    QueryDomain,
    RetrievalBackend,
    UserContext,
)


def _preview(*, mode: OrchestrationMode, domain: QueryDomain, tools: list[str] | None = None) -> OrchestrationPreview:
    access_tier = AccessTier.authenticated if domain in {QueryDomain.academic, QueryDomain.finance} else AccessTier.public
    return OrchestrationPreview(
        mode=mode,
        classification=IntentClassification(
            domain=domain,
            access_tier=access_tier,
            confidence=0.7,
            reason='probe',
        ),
        retrieval_backend=RetrievalBackend.none,
        selected_tools=tools or [],
        citations_required=False,
        needs_authentication=False,
        graph_path=[],
        risk_flags=[],
        reason='probe',
        output_contract='text',
    )


def _recent_context_with_slot_memory(slot_memory: dict[str, object]) -> dict[str, object]:
    now = datetime.now(timezone.utc).isoformat()
    return {
        'recent_messages': [
            {'sender_type': 'user', 'content': 'faltas do lucas', 'created_at': now},
            {'sender_type': 'assistant', 'content': 'Lucas Oliveira tem 6 faltas e 7 atrasos.', 'created_at': now},
        ],
        'recent_tool_calls': [
            {
                'tool_name': 'orchestration.trace',
                'created_at': now,
                'request_payload': {
                    'selected_tools': ['get_student_academic_summary'],
                    'slot_memory': slot_memory,
                },
            }
        ],
    }


async def main() -> None:
    results: dict[str, object] = {}

    internal_teacher_query = 'eu sou professor, como verifico a situação dos meus alunos?'
    results['internal_teacher_is_not_careers'] = rt._is_public_careers_query(internal_teacher_query)
    results['internal_teacher_scope_detected'] = rt._is_teacher_scope_guidance_query(internal_teacher_query)

    actor_guardian = {
        'full_name': 'Eliseu Daniel',
        'role_code': 'guardian',
        'linked_students': [
            {
                'student_id': 'stu-lucas',
                'full_name': 'Lucas Oliveira',
                'can_view_finance': True,
                'can_view_academic': True,
            }
        ],
    }
    actor_teacher = {
        'full_name': 'Marina Lopes',
        'role_code': 'teacher',
        'linked_students': [],
    }

    teacher_scope_answer = rt._compose_teacher_access_scope_answer(actor_guardian)
    results['teacher_scope_answer'] = teacher_scope_answer

    finance_preview = _preview(
        mode=OrchestrationMode.structured_tool,
        domain=QueryDomain.institution,
        tools=['get_administrative_status', 'get_student_administrative_status'],
    )
    finance_context = _recent_context_with_slot_memory(
        {
            'focus_kind': 'academic',
            'active_task': 'academic:attendance',
            'active_entity': 'Lucas Oliveira',
            'academic_attribute': 'attendance',
        }
    )
    finance_rescued = rt._apply_protected_domain_rescue(
        preview=finance_preview,
        actor=actor_guardian,
        message='e como está o financeiro do lucas',
        conversation_context=finance_context,
    )
    results['finance_rescue_applied'] = finance_rescued
    results['finance_rescue_domain'] = finance_preview.classification.domain.value
    results['finance_rescue_tools'] = list(finance_preview.selected_tools)

    original_api_core_get = rt._api_core_get

    async def _fake_api_core_get(*, settings, path, params=None):
        if path == '/v1/actors/me/administrative-status':
            return {'summary': {'status': 'regular'}}, 200
        if path.endswith('/financial-summary'):
            return (
                {
                    'summary': {
                        'student_name': 'Lucas Oliveira',
                        'contract_code': 'CTR-1001',
                        'guardian_name': 'Eliseu Daniel',
                        'monthly_amount': '950.00',
                        'open_invoice_count': 1,
                        'overdue_invoice_count': 0,
                        'invoices': [
                            {
                                'invoice_id': 'INV-001',
                                'status': 'open',
                                'due_date': '2026-04-10',
                                'amount': '950.00',
                            }
                        ],
                    }
                },
                200,
            )
        if path == '/v1/teachers/me/schedule':
            return (
                {
                    'summary': {
                        'teacher_name': 'Marina Lopes',
                        'assignments': [
                            {'class_name': '9A', 'subject_name': 'Historia', 'academic_year': 2026}
                        ],
                    }
                },
                200,
            )
        raise AssertionError(f'unexpected path: {path}')

    rt._api_core_get = _fake_api_core_get
    try:
        finance_answer = await rt._compose_structured_tool_answer(
            settings=SimpleNamespace(),
            request=MessageResponseRequest(
                message='e como está o financeiro do lucas',
                telegram_chat_id=1649845499,
                conversation_id='probe-python-functions-root-finance',
                channel=ConversationChannel.telegram,
                user=UserContext(authenticated=True, role='guardian'),
            ),
            analysis_message='e como está o financeiro do lucas sobre frequencia de Lucas Oliveira',
            preview=finance_preview,
            actor=actor_guardian,
            school_profile={},
            conversation_context=finance_context,
        )
        results['finance_answer'] = finance_answer

        teacher_answer = await rt._compose_structured_tool_answer(
            settings=SimpleNamespace(),
            request=MessageResponseRequest(
                message='eu sou professor, como verifico a situação dos meus alunos?',
                telegram_chat_id=1649845499,
                conversation_id='probe-python-functions-root-teacher',
                channel=ConversationChannel.telegram,
                user=UserContext(authenticated=True, role='guardian'),
            ),
            analysis_message='eu sou professor, como verifico a situação dos meus alunos?',
            preview=_preview(mode=OrchestrationMode.structured_tool, domain=QueryDomain.institution, tools=['get_service_directory']),
            actor=actor_guardian,
            school_profile={'school_name': 'Colegio Horizonte'},
            conversation_context={},
        )
        results['teacher_query_answer'] = teacher_answer

        teacher_role_preview = _preview(
            mode=OrchestrationMode.structured_tool,
            domain=QueryDomain.institution,
            tools=['get_service_directory'],
        )
        teacher_role_rescue = rt._apply_teacher_role_rescue(
            preview=teacher_role_preview,
            actor=actor_teacher,
            message='qual meu horario?',
        )
        results['teacher_role_rescue_applied'] = teacher_role_rescue
        results['teacher_role_rescue_domain'] = teacher_role_preview.classification.domain.value
        results['teacher_role_rescue_tools'] = list(teacher_role_preview.selected_tools)

        teacher_schedule_answer = await rt._execute_teacher_protected_specialist(
            settings=SimpleNamespace(),
            request=MessageResponseRequest(
                message='qual meu horario?',
                telegram_chat_id=1649845499,
                conversation_id='probe-python-functions-root-teacher-schedule',
                channel=ConversationChannel.telegram,
                user=UserContext(authenticated=True, role='teacher'),
            ),
            actor=actor_teacher,
        )
        results['teacher_schedule_answer'] = teacher_schedule_answer

        schedule_context = rt.PublicProfileContext(
            profile={
                'school_name': 'Colegio Horizonte',
                'segments': ['Ensino Fundamental II', 'Ensino Medio'],
            },
            actor=None,
            message='Horario do 9o ano',
            source_message='Horario do 9o ano',
            normalized='horario do 9o ano',
            analysis_normalized='horario do 9o ano',
            school_name='Colegio Horizonte',
            school_reference='o Colegio Horizonte',
            school_reference_capitalized='O Colegio Horizonte',
            city='Porto Alegre',
            state='RS',
            district='Centro',
            address_line='Rua Exemplo, 100',
            postal_code='90000-000',
            website_url='https://colegiohorizonte.edu.br',
            fax_number='',
            curriculum_basis='',
            curriculum_components=(),
            confessional_status='laica',
            segment='Ensino Fundamental II',
            schedule_context_normalized='horario do 9o ano',
            shift_offers=(
                {
                    'segment': 'Ensino Fundamental II',
                    'shift_label': 'Manha',
                    'starts_at': '07:15',
                    'ends_at': '12:30',
                    'notes': 'Oficinas e estudo orientado no contraturno.',
                },
                {
                    'segment': 'Fundamental II e Ensino Medio',
                    'shift_label': 'Integral opcional',
                    'starts_at': '07:00',
                    'ends_at': '17:30',
                    'notes': 'Inclui almoco e acompanhamento no contraturno.',
                },
            ),
            tuition_reference=(),
            semantic_act='schedule',
            contact_reference_message='',
            preferred_contact_labels=(),
            requested_channel=None,
            requested_attribute_override=None,
            slot_memory=rt.ConversationSlotMemory(),
            conversation_context=None,
            semantic_plan=None,
        )
        schedule_answer = rt._handle_public_schedule(schedule_context)
        results['grade_schedule_scope_answer'] = schedule_answer
    finally:
        rt._api_core_get = original_api_core_get

    assert results['internal_teacher_is_not_careers'] is False
    assert results['internal_teacher_scope_detected'] is True
    assert 'perfil docente' in str(results['teacher_scope_answer']).lower()
    assert results['finance_rescue_applied'] is True
    assert results['finance_rescue_domain'] == 'finance'
    assert 'Resumo financeiro de Lucas Oliveira' in str(results['finance_answer'])
    assert 'perfil docente' in str(results['teacher_query_answer']).lower()
    assert results['teacher_role_rescue_applied'] is True
    assert results['teacher_role_rescue_domain'] == 'academic'
    assert 'Grade docente de Marina Lopes:' in str(results['teacher_schedule_answer'])
    assert 'nao detalham o horario especifico do 9o ano' in str(results['grade_schedule_scope_answer']).lower()

    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    asyncio.run(main())
