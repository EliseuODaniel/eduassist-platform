from __future__ import annotations

from datetime import datetime
from types import SimpleNamespace

from ai_orchestrator.models import AccessTier, OrchestrationMode, QueryDomain
from ai_orchestrator.runtime import (
    _apply_workflow_follow_up_rescue,
    _apply_authenticated_public_profile_rescue,
    PublicInstitutionPlan,
    ProtectedAttributeRequest,
    _apply_protected_domain_rescue,
    _build_analysis_message,
    _build_conversation_slot_memory,
    _build_public_institution_plan,
    _build_public_profile_context,
    _compose_public_profile_answer,
    _compose_public_pricing_projection_answer,
    _compose_service_routing_answer,
    _compose_academic_attribute_answer,
    _compose_academic_aggregate_answer,
    _compose_academic_difficulty_answer,
    _compose_academic_risk_answer,
    _compose_family_attendance_aggregate_answer,
    _compose_family_admin_aggregate_answer,
    _compose_contextual_public_boundary_answer,
    _compose_meta_repair_follow_up_answer,
    _compose_contextual_public_timeline_followup_answer,
    _compose_admin_finance_combined_answer,
    _compose_admin_finance_block_status_answer,
    _compose_finance_aggregate_answer,
    _compose_family_next_due_answer,
    _compose_visit_booking_action_answer,
    _compose_workflow_status_answer,
    _compose_missing_subject_explanation_answer,
    _detect_finance_attribute_request,
    _explicit_protected_domain_hint,
    _effective_academic_attribute_request,
    _extract_unknown_subject_reference,
    _explicit_unmatched_student_reference,
    _foreign_school_reference,
    _is_high_confidence_public_profile_query,
    _is_greeting_only,
    _is_access_scope_query,
    _is_direct_service_routing_bundle_query,
    _is_service_routing_query,
    _is_public_capacity_query,
    _is_public_careers_query,
    _is_public_curriculum_query,
    _is_public_document_submission_query,
    _is_public_timeline_query,
    _is_public_timeline_lifecycle_query,
    _is_public_year_three_phase_query,
    _is_public_support_navigation_query,
    _is_public_process_compare_query,
    _is_explicit_public_pricing_projection_query,
    _is_public_pricing_context_follow_up,
    _is_public_pricing_navigation_query,
    _should_reuse_public_pricing_slots,
    _looks_like_family_attendance_aggregate_query,
    _looks_like_family_admin_aggregate_query,
    _looks_like_family_academic_aggregate_query,
    _looks_like_family_finance_aggregate_query,
    _looks_like_natural_visit_booking_request,
    _looks_like_workflow_resume_follow_up,
    _looks_like_visit_update_follow_up,
    _looks_like_public_documentary_open_query,
    _public_open_documentary_topic,
    _recent_conversation_focus,
    _recent_workflow_focus,
    _select_linked_student,
    _must_preserve_contextual_public_followup_message,
    _should_polish_structured_answer,
    _should_prioritize_protected_sql_query,
    _should_use_public_open_documentary_synthesis,
    _detect_subject_filter,
    _requested_subject_label_from_message,
    _looks_like_academic_difficulty_query,
    _handle_public_operating_hours,
    _try_public_channel_fast_answer,
    _detect_visit_booking_action,
    _is_public_teacher_directory_follow_up,
)
from ai_orchestrator.python_functions_public_knowledge import match_public_canonical_lane as match_python_functions_public_canonical_lane
from ai_orchestrator.request_intent_guardrails import (
    looks_like_explicit_admin_status_query,
    looks_like_high_confidence_public_school_faq,
)


def _preview(*, reason: str, domain: QueryDomain = QueryDomain.institution) -> SimpleNamespace:
    return SimpleNamespace(
        mode=OrchestrationMode.structured_tool,
        reason=reason,
        needs_authentication=False,
        classification=SimpleNamespace(
            domain=domain,
            access_tier=AccessTier.public,
        ),
    )


def test_public_act_rules_greeting_bridge_remains_available_after_runtime_split() -> None:
    assert _is_greeting_only('oi') is True


def test_langgraph_public_canonical_lane_skips_polish() -> None:
    request = SimpleNamespace(channel=SimpleNamespace(value="telegram"))
    preview = _preview(reason="langgraph_public_canonical_lane:public_bundle.year_three_phases")
    assert _should_polish_structured_answer(preview=preview, request=request) is False


def test_family_finance_aggregate_query_accepts_meus_pagamentos_wording() -> None:
    assert _looks_like_family_finance_aggregate_query('Como estao meus pagamentos?') is True


def test_family_finance_aggregate_query_accepts_meu_financeiro_wording() -> None:
    assert _looks_like_family_finance_aggregate_query('Quero ver meu financeiro') is True


def test_public_document_submission_query_accepts_enrollment_documents_requirement() -> None:
    assert _is_public_document_submission_query('Quais documentos preciso para matricula?') is True


def test_public_timeline_query_accepts_quando_iniciam_as_aulas_prompt() -> None:
    assert _is_public_timeline_query('Quando iniciam as aulas?') is True


def test_compose_family_next_due_answer_prefers_earliest_due_invoice() -> None:
    answer = _compose_family_next_due_answer(
        [
            {
                'student_name': 'Lucas Oliveira',
                'invoices': [
                    {
                        'reference_month': '2026-05',
                        'due_date': '2026-05-10',
                        'amount_due': '1450.00',
                        'status': 'open',
                    }
                ],
            },
            {
                'student_name': 'Ana Oliveira',
                'invoices': [
                    {
                        'reference_month': '2026-04',
                        'due_date': '2026-04-15',
                        'amount_due': '1450.00',
                        'status': 'open',
                    }
                ],
            },
        ]
    )
    assert answer is not None
    lowered = answer.lower()
    assert 'ana oliveira' in lowered
    assert '15 de abril de 2026' in lowered


def test_family_attendance_aggregate_query_rejects_finance_summary_with_atrasos_prompt() -> None:
    prompt = 'De forma bem objetiva, resuma a situacao financeira atual da familia, com vencimentos, atrasos e proximos passos.'
    assert _looks_like_family_attendance_aggregate_query(prompt) is False


def test_natural_visit_booking_request_accepts_quero_visitar_prompt() -> None:
    assert _looks_like_natural_visit_booking_request('Quero visitar a escola na sexta de manha.') is True


def test_detect_visit_booking_action_accepts_trocar_o_horario_followup() -> None:
    assert _detect_visit_booking_action('Se eu precisar trocar o horario depois, por onde remarco?') == 'reschedule'


def test_visit_update_follow_up_accepts_generic_cancel_inside_visit_context() -> None:
    assert _looks_like_visit_update_follow_up('E se eu cancelar, qual e o caminho mais curto?') is True


def test_workflow_resume_follow_up_accepts_resume_after_cancel_wording() -> None:
    assert _looks_like_workflow_resume_follow_up('E se eu quiser retomar depois, por onde volto?') is True


def test_recent_conversation_focus_keeps_visit_after_cancel_followup() -> None:
    focus = _recent_conversation_focus(
        {
            'recent_messages': [
                {'sender_type': 'assistant', 'content': 'Consigo remarcar a visita por aqui. Protocolo: VIS-20260409-403A7D.'},
                {'sender_type': 'user', 'content': 'certo, e se eu cancelar mesmo?'},
                {'sender_type': 'assistant', 'content': 'Se voce cancelar a visita, o protocolo VIS-20260409-403A7D sera cancelado.'},
            ],
            'recent_tool_calls': [],
        }
    )
    assert isinstance(focus, dict)
    assert focus.get('kind') == 'visit'


def test_recent_conversation_focus_keeps_visit_from_protocol_prefix_even_without_word_visita() -> None:
    focus = _recent_conversation_focus(
        {
            'recent_messages': [
                {'sender_type': 'assistant', 'content': 'Se voce cancelar, o protocolo VIS-20260409-403A7D sera cancelado.'},
                {'sender_type': 'user', 'content': 'certo, e se eu cancelar mesmo?'},
            ],
            'recent_tool_calls': [],
        }
    )
    assert isinstance(focus, dict)
    assert focus.get('kind') == 'visit'
    assert focus.get('protocol_code') == 'VIS-20260409-403A7D'


def test_visit_action_answer_uses_backend_cancel_action_for_elliptic_followup() -> None:
    answer = _compose_visit_booking_action_answer(
        {
            'action': 'cancel',
            'item': {
                'protocol_code': 'VIS-20260409-8C0B98',
                'queue_name': 'admissions',
                'linked_ticket_code': 'ATD-20260409-747EA3E6',
                'status': 'cancelled',
            },
        },
        request_message='e se eu cancelar?',
    )
    lowered = answer.lower()
    assert 'cancelad' in lowered
    assert 'protocolo' in lowered


def test_compose_workflow_status_answer_handles_visit_resume_wording() -> None:
    answer = _compose_workflow_status_answer(
        {
            'found': True,
            'item': {
                'workflow_type': 'visit_booking',
                'protocol_code': 'VIS-20260409-8C0B98',
                'queue_name': 'admissions',
                'linked_ticket_code': 'ATD-20260409-747EA3E6',
                'status': 'cancelled',
            },
        },
        protocol_code_hint='VIS-20260409-8C0B98',
        request_message='e se eu quiser retomar depois, por onde volto?',
    )
    lowered = answer.lower()
    assert 'retomar' in lowered
    assert 'novo pedido' in lowered or 'canal institucional' in lowered


def test_workflow_follow_up_rescue_prefers_recent_workflow_over_public_digression() -> None:
    preview = SimpleNamespace(
        mode=OrchestrationMode.structured_tool,
        reason='fato institucional canonico deve vir de fonte estruturada',
        needs_authentication=False,
        selected_tools=['get_public_school_profile'],
        graph_path=['classify_request', 'security_gate', 'route_request'],
        risk_flags=[],
        retrieval_backend=None,
        citations_required=False,
        output_contract='',
        classification=SimpleNamespace(
            domain=QueryDomain.institution,
            access_tier=AccessTier.public,
            confidence=0.78,
            reason='institution',
        ),
    )
    applied = _apply_workflow_follow_up_rescue(
        preview=preview,
        message='e se eu quiser retomar depois, por onde volto?',
        conversation_context={
            'recent_messages': [
                {'sender_type': 'assistant', 'content': 'Pedido de visita registrado para o Colegio Horizonte. Protocolo: VIS-20260409-9A9D1D.'},
                {'sender_type': 'assistant', 'content': 'O horario da biblioteca vai das 7h30 as 18h00.'},
                {'sender_type': 'assistant', 'content': 'Consigo remarcar a visita por aqui. Protocolo: VIS-20260409-9A9D1D.'},
                {'sender_type': 'assistant', 'content': 'Se voce cancelar, o protocolo VIS-20260409-9A9D1D sera cancelado.'},
            ],
            'recent_tool_calls': [
                {
                    'tool_name': 'orchestration.trace',
                    'request_payload': {
                        'selected_tools': ['schedule_school_visit', 'create_support_ticket'],
                        'slot_memory': {
                            'focus_kind': 'visit',
                            'active_task': 'workflow:visit_booking',
                            'protocol_code': 'VIS-20260409-9A9D1D',
                        },
                    },
                },
                {
                    'tool_name': 'orchestration.trace',
                    'request_payload': {
                        'selected_tools': ['get_public_school_profile'],
                        'slot_memory': {
                            'focus_kind': 'public',
                            'active_task': 'public:features',
                            'active_entity': 'biblioteca',
                        },
                    },
                },
                {
                    'tool_name': 'orchestration.trace',
                    'request_payload': {
                        'selected_tools': ['update_visit_booking'],
                        'slot_memory': {
                            'focus_kind': 'visit',
                            'active_task': 'workflow:visit_booking',
                            'protocol_code': 'VIS-20260409-9A9D1D',
                        },
                    },
                },
                {
                    'tool_name': 'orchestration.trace',
                    'request_payload': {
                        'selected_tools': [],
                        'slot_memory': {
                            'focus_kind': 'public',
                            'active_task': 'public:features',
                            'active_entity': 'biblioteca',
                        },
                    },
                },
            ],
        },
    )
    assert applied is True
    assert preview.classification.domain is QueryDomain.support
    assert preview.selected_tools == ['get_workflow_status']
    assert preview.reason == 'workflow_follow_up_rescue:visit_resume'


def test_recent_workflow_focus_prefers_visit_over_newer_public_trace() -> None:
    focus = _recent_workflow_focus(
        {
            'recent_messages': [
                {'sender_type': 'assistant', 'content': 'Pedido de visita registrado para o Colegio Horizonte. Protocolo: VIS-20260409-9A9D1D.'},
                {'sender_type': 'assistant', 'content': 'O horario da biblioteca vai das 7h30 as 18h00.'},
                {'sender_type': 'assistant', 'content': 'Consigo remarcar a visita por aqui. Protocolo: VIS-20260409-9A9D1D.'},
                {'sender_type': 'assistant', 'content': 'Se voce cancelar, o protocolo VIS-20260409-9A9D1D sera cancelado.'},
            ],
            'recent_tool_calls': [
                {
                    'tool_name': 'orchestration.trace',
                    'request_payload': {
                        'selected_tools': ['schedule_school_visit', 'create_support_ticket'],
                        'slot_memory': {
                            'focus_kind': 'visit',
                            'active_task': 'workflow:visit_booking',
                            'protocol_code': 'VIS-20260409-9A9D1D',
                        },
                    },
                },
                {
                    'tool_name': 'orchestration.trace',
                    'request_payload': {
                        'selected_tools': ['get_public_school_profile'],
                        'slot_memory': {
                            'focus_kind': 'public',
                            'active_task': 'public:features',
                            'active_entity': 'biblioteca',
                        },
                    },
                },
            ],
        }
    )
    assert isinstance(focus, dict)
    assert focus.get('kind') == 'visit'


def test_workflow_follow_up_rescue_ignores_non_protocol_messages_without_crashing() -> None:
    preview = SimpleNamespace(
        mode=OrchestrationMode.structured_tool,
        reason='dados estruturados devem passar por service deterministico',
        needs_authentication=False,
        selected_tools=['get_student_grades'],
        graph_path=['classify_request', 'security_gate', 'route_request'],
        risk_flags=[],
        retrieval_backend=None,
        citations_required=False,
        output_contract='',
        classification=SimpleNamespace(
            domain=QueryDomain.academic,
            access_tier=AccessTier.authenticated,
            confidence=0.9,
            reason='academic',
        ),
    )
    applied = _apply_workflow_follow_up_rescue(
        preview=preview,
        message='e qual disciplina preocupa mais?',
        conversation_context={
            'recent_messages': [
                {'sender_type': 'assistant', 'content': 'As notas de Lucas Oliveira sao: Matematica 7,7 e Fisica 5,9.'},
            ],
            'recent_tool_calls': [],
        },
    )
    assert applied is False
    assert preview.selected_tools == ['get_student_grades']


def test_public_institution_structured_answer_still_polishes_when_not_canonical_lane() -> None:
    request = SimpleNamespace(channel=SimpleNamespace(value="telegram"))
    preview = _preview(reason="structured_tool:public_profile")
    assert _should_polish_structured_answer(preview=preview, request=request) is True


def _protected_preview() -> SimpleNamespace:
    return SimpleNamespace(
        mode=OrchestrationMode.clarify,
        reason='clarify',
        needs_authentication=True,
        selected_tools=[],
        graph_path=['clarify'],
        risk_flags=[],
        retrieval_backend=None,
        citations_required=False,
        output_contract='',
        classification=SimpleNamespace(
            domain=QueryDomain.unknown,
            access_tier=AccessTier.authenticated,
            confidence=0.5,
            reason='ambiguous',
        ),
    )


def _guardian_actor() -> dict[str, object]:
    return {
        'linked_students': [
            {
                'student_id': 'stu-ana',
                'full_name': 'Ana Oliveira',
                'can_view_academic': True,
                'can_view_finance': True,
            },
            {
                'student_id': 'stu-lucas',
                'full_name': 'Lucas Oliveira',
                'can_view_academic': True,
                'can_view_finance': True,
            },
        ]
    }


def test_protected_domain_rescue_promotes_family_finance_aggregate_from_clarify() -> None:
    preview = _protected_preview()
    applied = _apply_protected_domain_rescue(
        preview=preview,
        actor=_guardian_actor(),
        message='Como esta a situacao financeira da familia neste momento, incluindo atrasos, vencimentos proximos e proximo passo?',
        conversation_context=None,
    )
    assert applied is True
    assert preview.mode is OrchestrationMode.structured_tool
    assert preview.classification.domain is QueryDomain.finance
    assert 'get_financial_summary' in preview.selected_tools


def test_protected_domain_rescue_promotes_academic_followup_from_clarify() -> None:
    preview = _protected_preview()
    applied = _apply_protected_domain_rescue(
        preview=preview,
        actor=_guardian_actor(),
        message='Sem repetir o quadro inteiro, recorte so a Ana e mostre onde o risco academico dela esta mais alto.',
        conversation_context=None,
    )
    assert applied is True
    assert preview.mode is OrchestrationMode.structured_tool
    assert preview.classification.domain is QueryDomain.academic
    assert 'get_student_academic_summary' in preview.selected_tools


def test_protected_sql_query_beats_access_scope_for_family_academic_panorama() -> None:
    assert _should_prioritize_protected_sql_query(
        'Sem sair do escopo do projeto, quero um panorama academico dos meus filhos com quem esta mais perto da media minima.',
        actor=_guardian_actor(),
        conversation_context=None,
    ) is True


def test_protected_sql_query_beats_access_scope_for_admin_finance_combo() -> None:
    assert _should_prioritize_protected_sql_query(
        'Minha documentacao ou cadastro esta bloqueando atendimento financeiro? Quero um panorama combinado de documentacao e financeiro.',
        actor=_guardian_actor(),
        conversation_context=None,
    ) is True


def test_public_pricing_query_does_not_trigger_protected_sql_priority() -> None:
    assert _should_prioritize_protected_sql_query(
        'Qual a mensalidade do ensino medio?',
        actor=_guardian_actor(),
        conversation_context=None,
    ) is False


def test_public_pricing_navigation_query_accepts_hypothetical_family_projection() -> None:
    assert _is_public_pricing_navigation_query('E se eu matricular meus 200 filhos?') is True


def test_public_pricing_navigation_query_accepts_dual_amount_projection() -> None:
    assert _is_public_pricing_navigation_query(
        'Usando a tabela publica, quanto dariam matricula e mensalidade para 3 filhos?'
    ) is True


def test_public_pricing_navigation_query_does_not_steal_process_compare_queries() -> None:
    prompt = 'Compare rematricula, transferencia e cancelamento destacando o que muda na pratica.'
    assert _is_public_process_compare_query(prompt) is True
    assert _is_public_pricing_navigation_query(prompt) is False


def test_explicit_public_pricing_projection_query_detects_dual_amount_hypothetical() -> None:
    prompt = 'Quanto eu pagaria de matricula e por mes para 3 filhos no ensino medio?'
    assert _is_explicit_public_pricing_projection_query(prompt, conversation_context=None) is True


def test_access_scope_query_detects_linked_students_account_wording() -> None:
    assert _is_access_scope_query('Quais alunos estao vinculados a esta conta?') is True


def test_access_scope_query_does_not_trigger_protected_sql_priority() -> None:
    assert _should_prioritize_protected_sql_query(
        'Estou autenticado como quem e com qual escopo? Quero saber o que consigo ver de academico e financeiro.',
        actor=_guardian_actor(),
        conversation_context=None,
    ) is False


def test_public_timeline_lifecycle_query_detects_marcos_entre_prompt() -> None:
    assert _is_public_timeline_lifecycle_query(
        'Quais sao os marcos entre matricula, inicio do ano letivo e reuniao de responsaveis no calendario publico de 2026?'
    ) is True


def test_public_timeline_lifecycle_query_detects_before_after_followup() -> None:
    assert _is_public_timeline_lifecycle_query(
        'E a primeira reuniao acontece antes ou depois das aulas?'
    ) is True


def test_preserve_contextual_public_followup_message_for_order_only_timeline_repair() -> None:
    assert _must_preserve_contextual_public_followup_message(
        request_message='Nao quero o calendario inteiro. Quero so esse recorte em ordem.',
        conversation_context={
            'recent_messages': [
                {'sender_type': 'user', 'content': 'Entre matricula, inicio das aulas e reuniao de responsaveis, como a familia junta isso?'},
            ]
        },
    ) is True


def test_contextual_public_timeline_followup_answer_handles_explicit_before_after_without_recent_context() -> None:
    profile = {
        'public_timeline': [
            {'topic_key': 'school_year_start', 'starts_at': '2026-02-02', 'summary': 'Inicio das aulas em 02/02/2026.'},
            {'topic_key': 'family_meeting', 'starts_at': '2026-02-05', 'summary': 'Primeira reuniao com responsaveis em 05/02/2026.'},
        ]
    }
    answer = _compose_contextual_public_timeline_followup_answer(
        request_message='E a primeira reuniao acontece antes ou depois das aulas?',
        conversation_context=None,
        profile=profile,
    )
    assert answer is not None
    assert 'depois do inicio das aulas' in answer


def test_contextual_public_timeline_followup_answer_handles_order_only_without_recent_context() -> None:
    profile = {
        'public_timeline': [
            {'topic_key': 'admissions_opening', 'summary': 'Matricula comecou em 10/01/2026.'},
            {'topic_key': 'school_year_start', 'summary': 'Inicio das aulas em 02/02/2026.'},
            {'topic_key': 'family_meeting', 'summary': 'Primeira reuniao com responsaveis em 05/02/2026.'},
        ]
    }
    answer = _compose_contextual_public_timeline_followup_answer(
        request_message='Nao quero o calendario inteiro. Quero so esse recorte em ordem.',
        conversation_context=None,
        profile=profile,
    )
    assert answer is not None
    assert 'Matricula' in answer or 'Matrícula' in answer
    assert 'Inicio das aulas' in answer or 'Início das aulas' in answer
    assert '1) Matricula e ingresso' in answer


def test_public_year_three_phase_query_detects_se_eu_dividir_o_ano_prompt() -> None:
    assert _is_public_year_three_phase_query(
        'Se eu dividir o ano em admissao, rotina academica e fechamento, como isso aparece na linha do tempo publica?'
    ) is True


def test_foreign_school_reference_ignores_generic_regularization_phrase() -> None:
    assert _foreign_school_reference(
        message='Quero um retrato das pendencias documentais da Ana e do proximo passo para regularizar tudo.',
        school_profile={'school_name': 'Colégio Horizonte'},
        conversation_context=None,
    ) is None


def test_foreign_school_reference_ignores_confessional_attribute_query() -> None:
    assert _foreign_school_reference(
        message='É um colégio confessional?',
        school_profile={'school_name': 'Colégio Horizonte'},
        conversation_context=None,
    ) is None


def test_high_confidence_public_profile_query_accepts_confessional_attribute_question() -> None:
    assert (
        _is_high_confidence_public_profile_query(
            'É um colégio confessional?',
            school_profile={
                'school_name': 'Colégio Horizonte',
                'confessional_status': 'laica',
            },
            conversation_context=None,
        )
        is True
    )


def test_public_pricing_followup_does_not_trigger_explicit_protected_domain_hint() -> None:
    now_iso = datetime.now().astimezone().isoformat()
    assert _explicit_protected_domain_hint(
        'Quanto seria a matricula para 20 filhos?',
        actor=_guardian_actor(),
        conversation_context={
            'recent_messages': [
                {'sender_type': 'assistant', 'content': 'A mensalidade do Ensino Médio é R$ 1.450,00 e a matrícula é R$ 350,00.', 'created_at': now_iso},
            ],
            'recent_tool_calls': [
                {
                    'tool_name': 'orchestration.trace',
                    'created_at': now_iso,
                    'request_payload': {
                        'slot_memory': {
                            'focus_kind': 'public',
                            'active_task': 'public:pricing',
                            'public_pricing_segment': 'Ensino Medio',
                        }
                    },
                }
            ],
        },
    ) is None


def test_public_capacity_followup_does_not_trigger_explicit_protected_domain_hint() -> None:
    now_iso = datetime.now().astimezone().isoformat()
    assert _explicit_protected_domain_hint(
        'E no estacionamento?',
        actor=_guardian_actor(),
        conversation_context={
            'recent_messages': [
                {'sender_type': 'assistant', 'content': 'A mensalidade do Ensino Médio é R$ 1.450,00 e a matrícula é R$ 350,00.', 'created_at': now_iso},
            ],
            'recent_tool_calls': [
                {
                    'tool_name': 'orchestration.trace',
                    'created_at': now_iso,
                    'request_payload': {
                        'slot_memory': {
                            'focus_kind': 'public',
                            'active_task': 'public:pricing',
                            'public_pricing_segment': 'Ensino Medio',
                        }
                    },
                }
            ],
        },
    ) is None


def test_build_analysis_message_rewrites_onboarding_contact_followup_to_explicit_contact_routing() -> None:
    now_iso = datetime.now().astimezone().isoformat()
    rewritten = _build_analysis_message(
        'E os contatos da secretaria e do financeiro junto com isso?',
        SimpleNamespace(
            conversation_external_id='conv-test',
            message_count=1,
            recent_messages=[
                {'sender_type': 'user', 'content': 'Sou familia nova. Como portal, secretaria e envio de documentos entram na ordem certa antes do inicio das aulas?', 'created_at': now_iso},
            ]
            ,
            recent_tool_calls=[],
        ),
    )
    assert 'como entrar em contato com a secretaria e com o financeiro' in rewritten


def test_build_analysis_message_rewrites_upcoming_assessments_followup_to_recent_student() -> None:
    now_iso = datetime.now().astimezone().isoformat()
    rewritten = _build_analysis_message(
        'E as proximas avaliacoes dela?',
        SimpleNamespace(
            conversation_external_id='conv-test',
            message_count=2,
            recent_messages=[
                {'sender_type': 'user', 'content': 'Agora isola a Ana e me mostra as notas dela.', 'created_at': now_iso},
                {'sender_type': 'assistant', 'content': 'Notas de Ana Oliveira...', 'created_at': now_iso},
            ],
            recent_tool_calls=[
                {
                    'tool_name': 'orchestration.trace',
                    'created_at': now_iso,
                    'request_payload': {
                        'slot_memory': {
                            'focus_kind': 'academic',
                            'active_task': 'academic:grades',
                            'academic_student_name': 'Ana Oliveira',
                        }
                    },
                }
            ],
        ),
    )
    assert 'proximas avaliacoes de Ana Oliveira' in rewritten


def test_build_analysis_message_keeps_upcoming_scope_when_subject_is_added_later() -> None:
    now_iso = datetime.now().astimezone().isoformat()
    rewritten = _build_analysis_message(
        'E a proxima de matematica?',
        SimpleNamespace(
            conversation_external_id='conv-test',
            message_count=2,
            recent_messages=[
                {'sender_type': 'user', 'content': 'Quais as proximas provas da Ana?', 'created_at': now_iso},
                {'sender_type': 'assistant', 'content': 'Proximas avaliacoes de Ana Oliveira: Matematica - Avaliacao B1 em 10/04/2026.', 'created_at': now_iso},
            ],
            recent_tool_calls=[
                {
                    'tool_name': 'orchestration.trace',
                    'created_at': now_iso,
                    'request_payload': {
                        'slot_memory': {
                            'focus_kind': 'academic',
                            'active_task': 'academic:upcoming',
                            'academic_focus_kind': 'upcoming',
                            'academic_student_name': 'Ana Oliveira',
                        }
                    },
                }
            ],
        ),
    )
    assert 'proximas avaliacoes de Ana Oliveira' in rewritten


def test_build_analysis_message_rewrites_service_routing_followup_to_explicit_one_line_request() -> None:
    now_iso = datetime.now().astimezone().isoformat()
    rewritten = _build_analysis_message(
        'Agora reduz para uma linha por setor, sem explicar o resto da escola.',
        SimpleNamespace(
            conversation_external_id='conv-test',
            message_count=2,
            recent_messages=[
                {'sender_type': 'user', 'content': 'Me diga so os canais de bolsas, financeiro e direcao. Seja objetivo.', 'created_at': now_iso},
                {'sender_type': 'assistant', 'content': 'Hoje estes sao os responsaveis e canais mais diretos por assunto...', 'created_at': now_iso},
            ],
            recent_tool_calls=[
                {
                    'tool_name': 'orchestration.trace',
                    'created_at': now_iso,
                    'request_payload': {
                        'slot_memory': {
                            'kind': 'public',
                            'active_task': 'public:service_routing',
                        }
                    },
                }
            ],
        ),
    )
    assert 'canais de bolsas, financeiro, direcao' in rewritten
    assert 'Uma linha por setor' in rewritten


def test_build_analysis_message_rewrites_onboarding_contact_followup_to_explicit_contacts_request() -> None:
    now_iso = datetime.now().astimezone().isoformat()
    rewritten = _build_analysis_message(
        'E os contatos da secretaria e do financeiro junto com isso?',
        SimpleNamespace(
            conversation_external_id='conv-test',
            message_count=2,
            recent_messages=[
                {'sender_type': 'user', 'content': 'Sou familia nova. Como portal, secretaria e envio de documentos entram na ordem certa antes do inicio das aulas?', 'created_at': now_iso},
                {'sender_type': 'assistant', 'content': 'Primeiro entram portal, secretaria e documentos; depois vem o inicio das aulas.', 'created_at': now_iso},
            ],
            recent_tool_calls=[],
        ),
    )

    assert 'secretaria e com o financeiro' in rewritten


def test_compose_meta_repair_follow_up_answer_prefers_last_assistant_upcoming_topic() -> None:
    now_iso = datetime.now().astimezone().isoformat()
    answer = _compose_meta_repair_follow_up_answer(
        {
            'recent_messages': [
                {'sender_type': 'assistant', 'content': 'Proximas avaliacoes de Lucas Oliveira: Historia - Avaliacao B1 em 2026-04-10.', 'created_at': now_iso},
            ],
            'recent_tool_calls': [
                {
                    'tool_name': 'orchestration.trace',
                    'created_at': now_iso,
                    'request_payload': {
                        'slot_memory': {
                            'active_task': 'academic:grades',
                            'academic_student_name': 'Lucas Oliveira',
                        }
                    },
                }
            ],
        }
    )

    assert answer == 'A resposta anterior estava falando das proximas provas de Lucas Oliveira.'


def test_build_analysis_message_rewrites_restricted_public_outings_followup() -> None:
    now_iso = datetime.now().astimezone().isoformat()
    rewritten = _build_analysis_message(
        'Entao me diga so o que existe de publico sobre esse tipo de saida ou protocolo.',
        SimpleNamespace(
            conversation_external_id='conv-test',
            message_count=2,
            recent_messages=[
                {'sender_type': 'user', 'content': 'Voce encontrou alguma orientacao interna sobre excursao de inverno para o 9 ano?', 'created_at': now_iso},
                {'sender_type': 'assistant', 'content': 'Nao encontrei orientacao interna suficiente sobre excursao de inverno.', 'created_at': now_iso},
            ],
            recent_tool_calls=[],
        ),
    )
    assert 'publico sobre saidas pedagogicas' in rewritten


def test_build_analysis_message_rewrites_restricted_public_outings_followup_to_two_steps() -> None:
    now_iso = datetime.now().astimezone().isoformat()
    rewritten = _build_analysis_message(
        'Resume isso em dois passos praticos.',
        SimpleNamespace(
            conversation_external_id='conv-test',
            message_count=3,
            recent_messages=[
                {'sender_type': 'user', 'content': 'Voce encontrou alguma orientacao interna sobre excursao de inverno para o 9 ano?', 'created_at': now_iso},
                {'sender_type': 'assistant', 'content': 'Nao encontrei orientacao interna suficiente sobre excursao de inverno.', 'created_at': now_iso},
                {'sender_type': 'user', 'content': 'Entao me diga so o que existe de publico sobre esse tipo de saida ou protocolo.', 'created_at': now_iso},
            ],
            recent_tool_calls=[],
        ),
    )
    assert 'Resuma em dois passos praticos' in rewritten


def test_detect_subject_filter_does_not_reuse_previous_subject_when_current_subject_is_missing() -> None:
    summary = {
        'grades': [
            {'subject_name': 'Fisica', 'subject_code': 'FIS', 'score': 6.0},
            {'subject_name': 'Matematica', 'subject_code': 'MAT', 'score': 7.0},
        ]
    }
    conversation_context = {
        'recent_messages': [
            {'sender_type': 'user', 'content': 'Quais sao as notas de fisica?'},
            {'sender_type': 'assistant', 'content': 'Fisica...'},
        ]
    }
    assert _detect_subject_filter(
        'E as notas de danca?',
        summary,
        conversation_context=conversation_context,
        focus_kind='grades',
    ) is None


def test_detect_subject_filter_does_not_reuse_previous_subject_for_full_grade_overview() -> None:
    summary = {
        'grades': [
            {'subject_name': 'Educacao Fisica', 'subject_code': 'EDF', 'score': 6.5},
            {'subject_name': 'Fisica', 'subject_code': 'FIS', 'score': 8.0},
        ]
    }
    conversation_context = {
        'recent_messages': [
            {'sender_type': 'user', 'content': 'Qual a media de educacao fisica do Lucas?'},
            {'sender_type': 'assistant', 'content': 'Educacao Fisica...'},
        ]
    }
    assert _detect_subject_filter(
        'Mande as notas dele.',
        summary,
        conversation_context=conversation_context,
        focus_kind='grades',
    ) is None


def test_requested_subject_label_normalizes_english_alias() -> None:
    assert _requested_subject_label_from_message('Qual a nota de english do Lucas?') == 'Lingua Inglesa'


def test_requested_subject_label_ignores_negated_previous_subject() -> None:
    assert (
        _requested_subject_label_from_message('Nao e fisica, e aulas de danca. Quero saber se isso existe na base.')
        == 'Danca'
    )


def test_compose_academic_attribute_answer_reports_missing_subject_instead_of_repeating_all_grades() -> None:
    answer = _compose_academic_attribute_answer(
        {
            'grades': [
                {'subject_name': 'Fisica', 'item_title': 'B1', 'score': 7.0, 'max_score': 10.0},
                {'subject_name': 'Matematica', 'item_title': 'B1', 'score': 8.0, 'max_score': 10.0},
            ]
        },
        attribute_request=ProtectedAttributeRequest(domain='academic', attribute='grades'),
        student_name='Lucas Oliveira',
        message='Nao e fisica, e aulas de danca. Quero saber se isso existe na base.',
        conversation_context={
            'recent_messages': [
                {'sender_type': 'user', 'content': 'Qual a nota de english do Lucas?'},
                {'sender_type': 'assistant', 'content': 'Notas de Lucas Oliveira...'},
            ]
        },
    )
    assert 'nao encontrei disciplina ou registros de Lucas Oliveira em Danca' in answer


def test_extract_unknown_subject_reference_catches_short_followup_subject() -> None:
    assert _extract_unknown_subject_reference('E de ufologia?') == 'Ufologia'


def test_compose_academic_attribute_answer_reports_unknown_subject_in_short_followup() -> None:
    answer = _compose_academic_attribute_answer(
        {
            'grades': [
                {'subject_name': 'Educacao Fisica', 'item_title': 'B1', 'score': 6.5, 'max_score': 10.0},
                {'subject_name': 'Biologia', 'item_title': 'B1', 'score': 7.5, 'max_score': 10.0},
            ]
        },
        attribute_request=ProtectedAttributeRequest(domain='academic', attribute='grades'),
        student_name='Lucas Oliveira',
        message='E de ufologia?',
        conversation_context={
            'recent_messages': [
                {'sender_type': 'user', 'content': 'Mande as notas dele.'},
                {'sender_type': 'assistant', 'content': 'Notas de Lucas Oliveira...'},
            ]
        },
    )
    assert 'nao encontrei notas de Lucas Oliveira em Ufologia' in answer


def test_effective_academic_attribute_request_inherits_unknown_subject_followup_only_from_academic_context() -> None:
    assert _effective_academic_attribute_request(
        'E de ufologia?',
        conversation_context={
            'recent_tool_calls': [
                {
                    'tool_name': 'orchestration.trace',
                    'request_payload': {
                        'slot_memory': {
                            'active_task': 'academic:grades',
                            'academic_attribute': 'grades',
                        }
                    },
                }
            ]
        },
    ) == ProtectedAttributeRequest(domain='academic', attribute='grades')


def test_explicit_protected_domain_hint_keeps_short_subject_followup_in_academic_domain() -> None:
    actor = _guardian_actor()
    conversation_context = {
        'recent_messages': [
            {'sender_type': 'user', 'content': 'E de ingles?'},
            {'sender_type': 'assistant', 'content': 'Notas de Lucas Oliveira:\n- Disciplina filtrada: Ingles\n- Ingles - Avaliacao B1: 8.90/10.00'},
        ],
        'recent_tool_calls': [
            {
                'tool_name': 'orchestration.trace',
                'request_payload': {
                    'slot_memory': {
                        'kind': 'academic',
                        'active_task': 'academic:grades',
                        'academic_attribute': 'grades',
                        'academic_student_name': 'Lucas Oliveira',
                    }
                },
            }
        ],
    }
    assert _explicit_protected_domain_hint(
        'E de danca?',
        actor=actor,
        conversation_context=conversation_context,
    ) is QueryDomain.academic


def test_explicit_protected_domain_hint_keeps_missing_subject_explanation_followup_in_academic_domain() -> None:
    actor = _guardian_actor()
    conversation_context = {
        'recent_messages': [
            {'sender_type': 'user', 'content': 'Qual a nota de danca?'},
            {
                'sender_type': 'assistant',
                'content': 'Hoje eu nao encontrei notas de Lucas Oliveira em Danca no recorte academico desta conta.',
            },
        ],
        'recent_tool_calls': [
            {
                'tool_name': 'orchestration.trace',
                'request_payload': {
                    'slot_memory': {
                        'kind': 'academic',
                        'active_task': 'academic:grades',
                        'academic_attribute': 'grades',
                        'academic_student_name': 'Lucas Oliveira',
                    }
                },
            }
        ],
    }
    assert _explicit_protected_domain_hint(
        'Por que nao tem?',
        actor=actor,
        conversation_context=conversation_context,
    ) is QueryDomain.academic


def test_compose_missing_subject_explanation_answer_mentions_curricular_vs_activity_boundary() -> None:
    answer = _compose_missing_subject_explanation_answer(
        student_name='Lucas Oliveira',
        subject_label='Danca',
    )
    lowered = answer.lower()
    assert 'atividade/oficina' in lowered
    assert 'lucas oliveira' in lowered


def test_explicit_protected_domain_hint_does_not_steal_public_curriculum_followup() -> None:
    actor = _guardian_actor()
    conversation_context = {
        'recent_tool_calls': [
            {
                'tool_name': 'orchestration.trace',
                'request_payload': {
                    'slot_memory': {
                        'active_task': 'academic:grades',
                        'academic_student_name': 'Lucas Oliveira',
                    }
                },
            }
        ]
    }

    assert _explicit_protected_domain_hint(
        'Tem aula de Física?',
        actor=actor,
        conversation_context=conversation_context,
    ) is None


def test_detect_finance_attribute_request_prefers_open_amount_for_quanto_falta_pagar() -> None:
    assert _detect_finance_attribute_request('Quanto falta pagar do Lucas?') == ProtectedAttributeRequest(
        domain='finance',
        attribute='open_amount',
    )


def test_effective_academic_attribute_request_does_not_inherit_unanchored_difficulty_followup() -> None:
    assert _effective_academic_attribute_request(
        'Mas qual a aula mais dificil de todas?',
        conversation_context={
            'recent_tool_calls': [
                {
                    'tool_name': 'orchestration.trace',
                    'request_payload': {
                        'slot_memory': {
                            'active_task': 'academic:grades',
                            'academic_attribute': 'grades',
                            'academic_student_name': 'Lucas Oliveira',
                        }
                    },
                }
            ]
        },
    ) is None


def test_effective_academic_attribute_request_does_not_override_explicit_difficulty_followup() -> None:
    assert _effective_academic_attribute_request(
        'Mas qual a disciplina mais dificil dele?',
        conversation_context={
            'recent_tool_calls': [
                {
                    'tool_name': 'orchestration.trace',
                    'request_payload': {
                        'slot_memory': {
                            'active_task': 'academic:grades',
                            'academic_attribute': 'grades',
                            'academic_student_name': 'Lucas Oliveira',
                        }
                    },
                }
            ]
        },
    ) is None


def test_effective_academic_attribute_request_does_not_override_upcoming_subject_followup() -> None:
    assert _effective_academic_attribute_request(
        'E a proxima de matematica?',
        conversation_context={
            'recent_messages': [
                {
                    'sender_type': 'assistant',
                    'content': 'Proximas avaliacoes de Ana Oliveira: Matematica - Avaliacao B1 em 10/04/2026.',
                }
            ],
            'recent_tool_calls': [
                {
                    'tool_name': 'orchestration.trace',
                    'request_payload': {
                        'slot_memory': {
                            'active_task': 'academic:upcoming',
                            'academic_focus_kind': 'upcoming',
                            'academic_student_name': 'Ana Oliveira',
                        }
                    },
                }
            ],
        },
    ) is None


def test_academic_difficulty_query_requires_anchor() -> None:
    assert _looks_like_academic_difficulty_query(
        'Qual a disciplina mais dificil dele?',
        conversation_context={
            'recent_tool_calls': [
                {
                    'tool_name': 'orchestration.trace',
                    'request_payload': {'slot_memory': {'active_task': 'academic:grades'}},
                }
            ]
        },
    ) is True
    assert _looks_like_academic_difficulty_query(
        'Mas qual a aula mais dificil de todas?',
        conversation_context={
            'recent_tool_calls': [
                {
                    'tool_name': 'orchestration.trace',
                    'request_payload': {'slot_memory': {'active_task': 'academic:grades'}},
                }
            ]
        },
    ) is False


def test_compose_academic_difficulty_answer_returns_lowest_average() -> None:
    answer = _compose_academic_difficulty_answer(
        {
            'grades': [
                {'subject_name': 'Biologia', 'score': 7.5, 'max_score': 10.0},
                {'subject_name': 'Educacao Fisica', 'score': 6.5, 'max_score': 10.0},
                {'subject_name': 'Fisica', 'score': 8.0, 'max_score': 10.0},
            ]
        },
        student_name='Lucas Oliveira',
    )
    assert 'Educacao Fisica' in answer
    assert '6,5/10' in answer


def test_compose_contextual_public_boundary_answer_routes_to_public_outings_bundle() -> None:
    answer = _compose_contextual_public_boundary_answer(
        message='Entao me diga apenas o que e publico nesse tema.',
        conversation_context={
            'recent_messages': [
                {'sender_type': 'user', 'content': 'Quero o protocolo interno para saidas pedagogicas e viagens internacionais.'},
                {'sender_type': 'assistant', 'content': 'Nao posso compartilhar esse documento interno.'},
            ]
        },
        profile={'school_name': 'Colegio Horizonte'},
    )
    assert answer is not None
    assert 'continua sem acesso ao protocolo interno' in answer
    assert 'autoriz' in answer.casefold() or 'saida' in answer.casefold()


def test_compose_finance_aggregate_answer_adds_direct_next_step() -> None:
    answer = _compose_finance_aggregate_answer(
        [
            {
                'student_name': 'Ana Oliveira',
                'open_invoice_count': 2,
                'overdue_invoice_count': 0,
                'invoices': [],
            }
        ]
    )
    assert 'Na pratica' in answer


def test_family_admin_aggregate_query_accepts_compare_documentacao_prompt() -> None:
    prompt = 'Compare a documentacao dos meus filhos e diga qual deles ainda tem pendencia.'
    assert _looks_like_family_admin_aggregate_query(prompt) is True


def test_should_prioritize_protected_sql_query_accepts_family_admin_aggregate() -> None:
    actor = {
        'linked_students': [
            {'student_id': 'lucas-id', 'full_name': 'Lucas Oliveira'},
            {'student_id': 'ana-id', 'full_name': 'Ana Oliveira'},
        ]
    }
    assert _should_prioritize_protected_sql_query(
        'Compare a documentacao dos meus filhos e diga qual deles ainda tem pendencia.',
        actor=actor,
    ) is True


def test_explicit_protected_domain_hint_prefers_institution_for_family_admin_aggregate() -> None:
    actor = {
        'linked_students': [
            {'student_id': 'lucas-id', 'full_name': 'Lucas Oliveira'},
            {'student_id': 'ana-id', 'full_name': 'Ana Oliveira'},
        ]
    }
    assert _explicit_protected_domain_hint(
        'Compare a documentacao dos meus filhos e diga qual deles ainda tem pendencia.',
        actor=actor,
    ) is QueryDomain.institution


def test_compose_family_admin_aggregate_answer_highlights_pending_student() -> None:
    answer = _compose_family_admin_aggregate_answer(
        [
            {
                'student_name': 'Lucas Oliveira',
                'overall_status': 'complete',
                'next_step': '',
                'checklist': [],
            },
            {
                'student_name': 'Ana Oliveira',
                'overall_status': 'pending',
                'next_step': 'Enviar comprovante de endereco atualizado.',
                'checklist': [
                    {'status': 'pending', 'notes': 'Comprovante de endereco nao anexado.'},
                ],
            },
        ]
    )
    lowered = answer.casefold()
    assert 'panorama documental das contas vinculadas' in lowered
    assert 'ana oliveira' in lowered
    assert 'pendencia documental' in lowered or 'pendência documental' in answer.casefold()
    assert 'proximo passo' in lowered or 'próximo passo' in answer.casefold()


def test_build_analysis_message_expands_access_scope_followup_by_student() -> None:
    context = SimpleNamespace(
        recent_messages=[
            {'sender_type': 'user', 'content': 'Quais alunos estao vinculados a esta conta?'},
            {'sender_type': 'assistant', 'content': 'Os alunos vinculados a esta conta hoje sao Lucas Oliveira e Ana Oliveira.'},
        ],
        recent_tool_calls=[
            {
                'tool_name': 'orchestration.trace',
                'request_payload': {
                    'slot_memory': {
                        'kind': 'admin',
                        'active_task': 'admin:access_scope',
                    }
                },
            }
        ],
    )
    analysis = _build_analysis_message('E o que eu consigo ver sobre cada um?', context)
    assert 'escopo academico e financeiro de cada aluno vinculado desta conta' in analysis


def test_explicit_protected_domain_hint_keeps_subject_existence_followup_in_academic_domain() -> None:
    actor = _guardian_actor()
    conversation_context = {
        'recent_messages': [
            {'sender_type': 'user', 'content': 'Qual a nota de english do Lucas?'},
            {'sender_type': 'assistant', 'content': 'Hoje eu nao encontrei notas de Lucas Oliveira em Lingua Inglesa no recorte academico desta conta.'},
        ],
        'recent_tool_calls': [
            {
                'tool_name': 'orchestration.trace',
                'request_payload': {
                    'slot_memory': {
                        'kind': 'academic',
                        'active_task': 'academic:grades',
                        'academic_student_name': 'Lucas Oliveira',
                    }
                },
            }
        ],
    }
    assert (
        _explicit_protected_domain_hint(
            'Nao e fisica, e aulas de danca. Quero saber se isso existe na base.',
            actor=actor,
            conversation_context=conversation_context,
        )
        is QueryDomain.academic
    )


def test_public_pricing_follow_up_reuses_segment_and_quantity_slots() -> None:
    now_iso = datetime.now().astimezone().isoformat()
    plan = _build_public_institution_plan(
        'Quanto seria a matricula para 20 filhos no ensino medio?',
        ['get_public_school_profile'],
        semantic_plan=None,
        conversation_context=None,
        school_profile=None,
    )
    slot_memory = _build_conversation_slot_memory(
        actor=None,
        profile={},
        conversation_context={
            'recent_tool_calls': [
                {
                    'tool_name': 'orchestration.trace',
                    'created_at': now_iso,
                    'request_payload': {
                        'slot_memory': {
                            'focus_kind': 'public',
                            'active_task': 'public:pricing',
                            'public_pricing_segment': 'Ensino Medio',
                            'public_pricing_quantity': '20',
                            'public_pricing_price_kind': 'enrollment_fee',
                        }
                    },
                }
            ]
        },
        request_message='E para 20 filhos?',
        public_plan=plan,
        preview=None,
    )

    assert slot_memory.public_pricing_segment == 'Ensino Medio'
    assert slot_memory.public_pricing_quantity == '20'
    assert slot_memory.public_pricing_price_kind == 'enrollment_fee'


def test_public_pricing_projection_answer_can_return_enrollment_and_monthly_totals() -> None:
    context = SimpleNamespace(
        source_message='Usando a tabela publica, quanto dariam matricula e mensalidade para 3 filhos no ensino medio?',
        normalized='usando a tabela publica quanto dariam matricula e mensalidade para 3 filhos no ensino medio',
        segment='Ensino Medio',
        tuition_reference=[
            {
                'segment': 'Ensino Medio',
                'shift_label': 'Manha',
                'monthly_amount': '1450.00',
                'enrollment_fee': '350.00',
                'notes': 'Desconto para irmaos pode ser analisado pela politica comercial publica.',
            }
        ],
        slot_memory=SimpleNamespace(
            public_pricing_quantity=None,
            public_pricing_price_kind=None,
            public_pricing_segment='Ensino Medio',
            public_pricing_grade_year=None,
        ),
    )

    answer = _compose_public_pricing_projection_answer(context)

    assert answer is not None
    lowered = answer.lower()
    assert 'matricula' in lowered
    assert 'mensalidade' in lowered
    assert 'por mes' in lowered
    assert 'r$ 1.050,00' in lowered
    assert 'r$ 4.350,00' in lowered


def test_public_pricing_projection_answer_handles_matricula_e_por_mes_wording() -> None:
    context = SimpleNamespace(
        source_message='Quanto eu pagaria de matricula e por mes para 3 filhos usando a referencia publica atual?',
        normalized='quanto eu pagaria de matricula e por mes para 3 filhos usando a referencia publica atual',
        segment='Ensino Medio',
        tuition_reference=[
            {
                'segment': 'Ensino Medio',
                'shift_label': 'Manha',
                'monthly_amount': '1450.00',
                'enrollment_fee': '350.00',
                'notes': 'Desconto para irmaos pode ser analisado pela politica comercial publica.',
            }
        ],
        slot_memory=SimpleNamespace(
            public_pricing_quantity=None,
            public_pricing_price_kind=None,
            public_pricing_segment='Ensino Medio',
            public_pricing_grade_year=None,
        ),
    )

    answer = _compose_public_pricing_projection_answer(context)

    assert answer is not None
    lowered = answer.lower()
    assert 'matricula' in lowered
    assert 'mensalidade' in lowered
    assert 'por mes' in lowered
    assert 'r$ 1.050,00' in lowered
    assert 'r$ 4.350,00' in lowered


def test_public_pricing_projection_answer_reuses_public_slots_in_short_followup() -> None:
    context = SimpleNamespace(
        source_message='E para 100 rianças',
        normalized='e para 100 riancas',
        segment='Ensino Medio',
        tuition_reference=[
            {
                'segment': 'Ensino Medio',
                'shift_label': 'Manha',
                'monthly_amount': '1450.00',
                'enrollment_fee': '350.00',
                'notes': 'Desconto para irmaos pode ser analisado pela politica comercial publica.',
            }
        ],
        slot_memory=SimpleNamespace(
            public_pricing_quantity='3',
            public_pricing_price_kind='monthly_amount',
            public_pricing_segment='Ensino Medio',
            public_pricing_grade_year=None,
        ),
    )

    answer = _compose_public_pricing_projection_answer(context)

    assert answer is not None
    lowered = answer.lower()
    assert '100 x' in lowered
    assert 'r$ 145.000,00' in lowered


def test_compose_public_profile_answer_prefers_canonical_process_compare_before_pricing_shortcut() -> None:
    answer = _compose_public_profile_answer(
        {},
        'Quero entender rematricula, transferencia e cancelamento junto com bolsa e valores publicos.',
        actor=None,
        original_message=None,
        conversation_context=None,
        semantic_plan=None,
    )
    normalized = answer.casefold()
    assert 'rematricula' in normalized or 'rematrícula' in normalized
    assert 'transfer' in normalized
    assert 'cancel' in normalized


def test_compose_public_profile_answer_terminal_greeting_ignores_previous_admin_follow_up() -> None:
    answer = _compose_public_profile_answer(
        {'school_name': 'Colegio Horizonte'},
        'bom diazinho',
        actor={'role_code': 'guardian'},
        original_message='bom diazinho',
        conversation_context={
            'recent_messages': [
                {'sender_type': 'assistant', 'content': 'Situacao administrativa do seu cadastro hoje: com pendencias.'},
            ],
            'recent_trace': {'active_task': 'admin:administrative_status'},
        },
        semantic_plan=PublicInstitutionPlan(
            conversation_act='greeting',
            required_tools=('get_public_school_profile',),
            fetch_profile=True,
            semantic_source='semantic_ingress_llm',
            use_conversation_context=False,
        ),
    )
    normalized = answer.casefold()
    assert 'bom dia' in normalized or 'oi' in normalized
    assert 'eduassist' in normalized
    assert 'cadastro' not in normalized


def test_compose_public_profile_answer_input_clarification_ignores_previous_admin_follow_up() -> None:
    answer = _compose_public_profile_answer(
        {'school_name': 'Colegio Horizonte'},
        'Привет',
        actor={'role_code': 'guardian'},
        original_message='Привет',
        conversation_context={
            'recent_messages': [
                {'sender_type': 'assistant', 'content': 'Situacao administrativa do seu cadastro hoje: com pendencias.'},
            ],
            'recent_trace': {'active_task': 'admin:administrative_status'},
        },
        semantic_plan=PublicInstitutionPlan(
            conversation_act='input_clarification',
            required_tools=('get_public_school_profile',),
            fetch_profile=True,
            semantic_source='semantic_ingress_llm',
            use_conversation_context=False,
        ),
    )
    normalized = answer.casefold()
    assert 'nao consegui interpretar' in normalized or 'não consegui interpretar' in normalized
    assert 'cadastro' not in normalized


def test_compose_public_profile_answer_language_preference_explains_portuguese_label() -> None:
    answer = _compose_public_profile_answer(
        {'school_name': 'Colegio Horizonte'},
        'Por que admissions ta em ingles?',
        actor={'role_code': 'guardian'},
        original_message='Por que admissions ta em ingles?',
        conversation_context=None,
        semantic_plan=PublicInstitutionPlan(
            conversation_act='language_preference',
            required_tools=('get_public_school_profile',),
            fetch_profile=True,
            semantic_source='semantic_ingress_llm',
            use_conversation_context=False,
        ),
    )
    normalized = answer.casefold()
    assert 'portugues' in normalized or 'português' in normalized
    assert 'matricula e atendimento comercial' in normalized
    assert 'admissions' not in normalized


def test_compose_public_profile_answer_language_preference_does_not_confuse_portuguese_with_subject() -> None:
    answer = _compose_public_profile_answer(
        {'school_name': 'Colegio Horizonte'},
        'Quero que so fale portugues',
        actor={'role_code': 'guardian'},
        original_message='Quero que so fale portugues',
        conversation_context={
            'recent_messages': [
                {'sender_type': 'assistant', 'content': 'Você quer consultar Língua Inglesa de qual aluno: Lucas Oliveira ou Ana Oliveira?'},
            ],
            'recent_trace': {'active_task': 'academic:grades'},
        },
        semantic_plan=PublicInstitutionPlan(
            conversation_act='language_preference',
            required_tools=('get_public_school_profile',),
            fetch_profile=True,
            semantic_source='semantic_ingress_llm',
            use_conversation_context=False,
        ),
    )
    normalized = answer.casefold()
    assert 'portugues' in normalized or 'português' in normalized
    assert 'lingua portuguesa' not in normalized
    assert 'ana oliveira' not in normalized


def test_compose_public_profile_answer_refines_library_closing_focus() -> None:
    profile = {
        'school_name': 'Colegio Horizonte',
        'feature_inventory': [
            {
                'feature_key': 'biblioteca',
                'available': True,
                'label': 'Biblioteca Aurora',
                'notes': 'Atendimento ao publico de segunda a sexta, das 7h30 as 18h00.',
            }
        ],
    }
    semantic_plan = PublicInstitutionPlan(
        conversation_act='operating_hours',
        required_tools=('get_public_school_profile',),
        fetch_profile=True,
        semantic_source='semantic_ingress_llm',
        requested_attribute='close_time',
    )
    context = _build_public_profile_context(
        profile,
        'qual horário de fechamento da biblioteca?',
        original_message='qual horário de fechamento da biblioteca?',
        semantic_plan=semantic_plan,
    )

    answer = _handle_public_operating_hours(context)

    assert answer == 'A biblioteca fecha as 18h00.'


def test_compose_public_profile_answer_blocks_external_city_library_query() -> None:
    answer = _compose_public_profile_answer(
        {'school_name': 'Colegio Horizonte'},
        'qual horário de fechamento da biblioteca pública da cidade?',
        original_message='qual horário de fechamento da biblioteca pública da cidade?',
        semantic_plan=PublicInstitutionPlan(
            conversation_act='scope_boundary',
            required_tools=('get_public_school_profile',),
            fetch_profile=True,
            semantic_source='semantic_ingress_llm',
        ),
    )

    normalized = answer.casefold()
    assert 'fora do escopo da escola' in normalized


def test_try_public_channel_fast_answer_blocks_external_city_library_query() -> None:
    answer = _try_public_channel_fast_answer(
        message='qual horário de fechamento da biblioteca pública da cidade?',
        profile={'school_name': 'Colegio Horizonte'},
    )

    assert answer is not None
    assert 'fora do escopo da escola' in answer.casefold()


def test_try_public_channel_fast_answer_prefers_process_compare_lane_before_pricing() -> None:
    answer = _try_public_channel_fast_answer(
        message='Compare rematricula, transferencia e cancelamento destacando o que muda na pratica.',
        profile={},
    )
    assert answer is not None
    normalized = answer.casefold()
    assert 'rematricula' in normalized or 'rematrícula' in normalized
    assert 'transfer' in normalized
    assert 'cancel' in normalized


def test_try_public_channel_fast_answer_projects_enrollment_and_monthly_for_three_children() -> None:
    answer = _try_public_channel_fast_answer(
        message='Quanto eu pagaria de matricula e por mes para 3 filhos no ensino medio?',
        profile={
            'tuition_reference': [
                {
                    'segment': 'Ensino Medio',
                    'shift_label': 'Manha',
                    'monthly_amount': '1450.00',
                    'enrollment_fee': '350.00',
                    'notes': 'Desconto para irmaos pode ser analisado pela politica comercial publica.',
                }
            ]
        },
    )
    assert answer is not None
    lowered = answer.lower()
    assert 'matricula' in lowered
    assert 'mensalidade' in lowered
    assert '3 x' in lowered
    assert 'r$ 1.050,00' in lowered
    assert 'r$ 4.350,00' in lowered


def test_try_public_channel_fast_answer_prefers_enrollment_documents_before_pricing() -> None:
    answer = _try_public_channel_fast_answer(
        message='Quais documentos preciso para matricula?',
        profile={
            'admissions_required_documents': [
                'Formulario cadastral preenchido',
                'Documento de identificacao do aluno',
            ],
            'tuition_reference': [
                {
                    'segment': 'Ensino Medio',
                    'shift_label': 'Manha',
                    'monthly_amount': '1450.00',
                    'enrollment_fee': '350.00',
                }
            ],
        },
    )
    assert answer is not None
    lowered = answer.lower()
    assert 'documentos exigidos' in lowered
    assert 'formulario cadastral preenchido' in lowered
    assert 'mensalidade' not in lowered


def test_try_public_channel_fast_answer_prefers_enrollment_documents_over_inherited_pricing_context() -> None:
    now_iso = datetime.now().astimezone().isoformat()
    answer = _try_public_channel_fast_answer(
        message='Quais documentos preciso para matricula?',
        profile={
            'admissions_required_documents': [
                'Formulario cadastral preenchido',
                'Documento de identificacao do aluno',
            ],
            'tuition_reference': [
                {
                    'segment': 'Ensino Medio',
                    'shift_label': 'Manha',
                    'monthly_amount': '1450.00',
                    'enrollment_fee': '350.00',
                }
            ],
        },
        conversation_context={
            'recent_messages': [
                {'sender_type': 'user', 'content': 'qual valor da matrícula?', 'created_at': now_iso},
                {'sender_type': 'assistant', 'content': 'Valores publicos de referencia para 2026.', 'created_at': now_iso},
            ],
            'recent_tool_calls': [
                {
                    'tool_name': 'orchestration.trace',
                    'created_at': now_iso,
                    'request_payload': {
                        'slot_memory': {
                            'focus_kind': 'public',
                            'active_task': 'public:pricing',
                            'public_pricing_segment': 'Ensino Medio',
                        }
                    },
                }
            ],
        },
    )
    assert answer is not None
    lowered = answer.lower()
    assert 'documentos exigidos' in lowered
    assert 'formulario cadastral preenchido' in lowered
    assert 'mensalidade' not in lowered


def test_try_public_channel_fast_answer_answers_library_existence_queries() -> None:
    answer = _try_public_channel_fast_answer(
        message='Tem biblioteca nessa escola?',
        profile={
            'school_name': 'Colegio Horizonte',
            'feature_inventory': [
                {
                    'feature_key': 'biblioteca',
                    'label': 'Biblioteca Aurora',
                    'available': True,
                    'notes': 'Atendimento ao publico de segunda a sexta, das 7h30 as 18h00.',
                }
            ],
        },
    )
    assert answer is not None
    lowered = answer.lower()
    assert 'biblioteca aurora' in lowered
    assert '7h30' in lowered


def test_try_public_channel_fast_answer_answers_school_year_start_queries() -> None:
    answer = _try_public_channel_fast_answer(
        message='Quando iniciam as aulas?',
        profile={
            'school_name': 'Colegio Horizonte',
            'public_timeline': [
                {
                    'topic_key': 'school_year_start',
                    'summary': 'As aulas comecam em 2 de fevereiro de 2026.',
                    'notes': 'As aulas do Ensino Fundamental II e do Ensino Medio comecam em 2 de fevereiro de 2026.',
                }
            ],
        },
    )
    assert answer is not None
    lowered = answer.lower()
    assert '2 de fevereiro de 2026' in lowered


def test_try_public_channel_fast_answer_answers_morning_class_schedule_queries() -> None:
    answer = _try_public_channel_fast_answer(
        message='Que horas começa a aula de manhã?',
        profile={
            'school_name': 'Colegio Horizonte',
            'shift_offers': [
                {
                    'segment': 'Ensino Fundamental II',
                    'shift_label': 'Manhã',
                    'starts_at': '07:15',
                    'ends_at': '12:30',
                    'notes': 'Turno regular da manhã.',
                },
                {
                    'segment': 'Ensino Medio',
                    'shift_label': 'Manhã',
                    'starts_at': '07:15',
                    'ends_at': '12:50',
                    'notes': 'Turno regular da manhã.',
                },
                {
                    'segment': 'Fundamental II e Ensino Medio',
                    'shift_label': 'Integral opcional',
                    'starts_at': '07:00',
                    'ends_at': '17:30',
                    'notes': 'Contraturno opcional.',
                },
            ],
        },
    )
    assert answer is not None
    lowered = answer.lower()
    assert '07:15' in answer
    assert 'manhã' in lowered or 'manha' in lowered


def test_request_guardrails_keep_enrollment_documents_out_of_admin_status() -> None:
    prompt = 'Quais documentos preciso para matricula?'
    assert looks_like_high_confidence_public_school_faq(prompt) is True
    assert looks_like_explicit_admin_status_query(prompt, authenticated=True) is False


def test_request_guardrails_keep_school_year_start_out_of_admin_status() -> None:
    prompt = 'Quando iniciam as aulas?'
    assert looks_like_high_confidence_public_school_faq(prompt) is True
    assert looks_like_explicit_admin_status_query(prompt, authenticated=True) is False


def test_public_profile_answer_prefers_explicit_school_year_start_over_recent_enrollment_context() -> None:
    answer = _compose_public_profile_answer(
        {
            'school_name': 'Colegio Horizonte',
            'public_timeline': [
                {
                    'topic_key': 'admissions_opening',
                    'summary': 'A matricula de 2026 abre em 6 de outubro de 2025.',
                },
                {
                    'topic_key': 'school_year_start',
                    'summary': 'As aulas comecam em 2 de fevereiro de 2026.',
                },
            ],
        },
        'Quando iniciam as aulas?',
        actor={},
        original_message='Quando iniciam as aulas?',
        conversation_context={
            'recent_messages': [
                {'sender_type': 'user', 'content': 'qual valor da matrícula?'},
                {'sender_type': 'assistant', 'content': 'Valores publicos de referencia para 2026.'},
            ]
        },
    )
    lowered = answer.lower()
    assert '2 de fevereiro de 2026' in lowered
    assert '6 de outubro de 2025' not in lowered


def test_public_profile_answer_prefers_explicit_documents_over_inherited_pricing_semantic_plan() -> None:
    answer = _compose_public_profile_answer(
        {
            'school_name': 'Colegio Horizonte',
            'admissions_required_documents': [
                'Formulario cadastral preenchido',
                'Documento de identificacao do aluno',
            ],
            'tuition_reference': [
                {
                    'segment': 'Ensino Medio',
                    'shift_label': 'Manha',
                    'monthly_amount': '1450.00',
                    'enrollment_fee': '350.00',
                }
            ],
        },
        'Quais documentos preciso para matricula?',
        actor={},
        original_message='Quais documentos preciso para matricula?',
        conversation_context={
            'recent_messages': [
                {'sender_type': 'user', 'content': 'qual valor da matrícula?'},
                {'sender_type': 'assistant', 'content': 'Valores publicos de referencia para 2026.'},
            ],
            'recent_tool_calls': [
                {
                    'tool_name': 'orchestration.trace',
                    'request_payload': {
                        'slot_memory': {
                            'focus_kind': 'public',
                            'active_task': 'public:pricing',
                            'public_pricing_segment': 'Ensino Medio',
                        }
                    },
                }
            ],
        },
        semantic_plan=PublicInstitutionPlan(
            conversation_act='pricing',
            required_tools=('get_public_school_profile',),
            fetch_profile=True,
            secondary_acts=(),
            requested_attribute=None,
            requested_channel=None,
            focus_hint=None,
            semantic_source='llm',
            use_conversation_context=True,
        ),
    )
    lowered = answer.lower()
    assert 'documentos exigidos' in lowered
    assert 'formulario cadastral preenchido' in lowered
    assert 'mensalidade' not in lowered


def test_try_public_channel_fast_answer_returns_scope_boundary_for_out_of_scope_question() -> None:
    answer = _try_public_channel_fast_answer(
        message='Qual o melhor filme do ano?',
        profile={'school_name': 'Colegio Horizonte'},
    )

    assert answer is not None
    lowered = answer.lower()
    assert 'fora do escopo da escola' in lowered
    assert 'matricula' in lowered
    assert 'calendario' in lowered


def test_try_public_channel_fast_answer_uses_contextual_conduct_policy_for_substance_question() -> None:
    answer = _try_public_channel_fast_answer(
        message='Posso fumar maconha nessa escola?',
        profile={'school_name': 'Colegio Horizonte'},
    )

    assert answer is not None
    lowered = answer.lower()
    assert 'maconha' in lowered
    assert 'nao aparece como comportamento permitido' in lowered
    assert 'coordenacao' in lowered or 'coordenação' in lowered
    assert 'frequencia minima' not in lowered


def test_public_profile_answer_honors_semantic_auth_guidance_even_when_message_is_short() -> None:
    answer = _compose_public_profile_answer(
        {'school_name': 'Colegio Horizonte'},
        'como vinculo minha conta no telegram?',
        semantic_plan=PublicInstitutionPlan(
            conversation_act='auth_guidance',
            required_tools=('get_public_school_profile',),
            fetch_profile=True,
            semantic_source='semantic_ingress_llm',
            use_conversation_context=False,
        ),
    )

    lowered = answer.lower()
    assert 'vincul' in lowered
    assert 'telegram' in lowered
    assert '/start link_' in lowered


def test_build_public_institution_plan_keeps_teacher_directory_boundary() -> None:
    plan = _build_public_institution_plan(
        'Vocês divulgam o nome ou contato direto do professor de matematica? Se nao, para onde a familia deve ir?',
        ['get_public_school_profile'],
        semantic_plan=None,
        conversation_context=None,
        school_profile=None,
    )
    assert plan.conversation_act == 'teacher_directory'


def test_build_public_institution_plan_treats_quero_falar_com_professor_as_teacher_boundary() -> None:
    plan = _build_public_institution_plan(
        'Quero falar com o professor de matematica.',
        ['get_public_school_profile'],
        semantic_plan=None,
        conversation_context=None,
        school_profile=None,
    )
    assert plan.conversation_act == 'teacher_directory'


def test_public_teacher_directory_followup_keeps_boundary_in_short_followup() -> None:
    conversation_context = {
        'recent_messages': [
            {'sender_type': 'user', 'content': 'Quero falar com o professor de matematica.'},
            {'sender_type': 'assistant', 'content': 'A escola nao divulga contato direto de professor.'},
        ],
        'recent_trace': {'active_task': 'public:teacher_directory', 'kind': 'public'},
    }
    assert _is_public_teacher_directory_follow_up(
        'Ou manda procurar a coordenação?',
        conversation_context,
    ) is True


def test_public_curriculum_query_detects_subject_existence_and_school_scope_difficulty() -> None:
    assert _is_public_curriculum_query('Tem aula de Física?') is True
    assert _is_public_curriculum_query('E quais outras matérias tem?') is True
    assert _is_public_curriculum_query('Qual a matéria mais difícil de aprender no colégio?') is True


def test_public_service_routing_answer_handles_mixed_admissions_finance_and_direction() -> None:
    profile = {
        'service_catalog': [
            {
                'service_key': 'atendimento_admissoes',
                'title': 'Atendimento comercial / Admissoes',
                'request_channel': 'bot, admissions, whatsapp comercial ou visita guiada',
                'typical_eta': 'retorno em ate 1 dia util',
            },
            {
                'service_key': 'financeiro_escolar',
                'title': 'Financeiro',
                'request_channel': 'bot, financeiro, portal autenticado ou email institucional',
                'typical_eta': 'retorno em ate 1 dia util',
            },
            {
                'service_key': 'solicitacao_direcao',
                'title': 'Direcao',
                'request_channel': 'bot, ouvidoria ou protocolo institucional',
                'typical_eta': 'ate 2 dias uteis',
            },
        ],
        'leadership_team': [
            {
                'title': 'Diretora geral',
                'name': 'Helena Martins',
                'contact_channel': 'direcao@colegiohorizonte.edu.br',
            }
        ],
        'contact_channels': [
            {'channel': 'email', 'label': 'Admissoes', 'value': 'admissoes@colegiohorizonte.edu.br'},
            {'channel': 'whatsapp', 'label': 'Atendimento comercial', 'value': '(11) 97500-2040'},
            {'channel': 'email', 'label': 'Financeiro', 'value': 'financeiro@colegiohorizonte.edu.br'},
            {'channel': 'telefone', 'label': 'Financeiro', 'value': '(11) 3333-4203'},
            {'channel': 'email', 'label': 'Direcao', 'value': 'direcao@colegiohorizonte.edu.br'},
        ],
    }

    answer = _compose_service_routing_answer(
        profile,
        'Como entrar em contato com admissoes, financeiro e direcao quando o assunto mistura bolsa e mensalidade?',
    )

    assert 'Admissoes' in answer
    assert 'Financeiro' in answer
    assert 'Direcao' in answer
    assert 'admissoes@colegiohorizonte.edu.br' in answer
    assert '(11) 97500-2040' in answer
    assert 'financeiro@colegiohorizonte.edu.br' in answer
    assert '(11) 3333-4203' in answer


def test_public_service_routing_answer_handles_plural_bolsas_wording() -> None:
    profile = {
        'service_catalog': [
            {
                'service_key': 'atendimento_admissoes',
                'title': 'Atendimento comercial / Admissoes',
                'request_channel': 'bot, admissions, whatsapp comercial ou visita guiada',
                'typical_eta': 'retorno em ate 1 dia util',
            },
            {
                'service_key': 'financeiro_escolar',
                'title': 'Financeiro',
                'request_channel': 'bot, financeiro, portal autenticado ou email institucional',
                'typical_eta': 'retorno em ate 1 dia util',
            },
            {
                'service_key': 'solicitacao_direcao',
                'title': 'Direcao',
                'request_channel': 'bot, ouvidoria ou protocolo institucional',
                'typical_eta': 'ate 2 dias uteis',
            },
        ],
        'leadership_team': [
            {
                'title': 'Diretora geral',
                'name': 'Helena Martins',
                'contact_channel': 'direcao@colegiohorizonte.edu.br',
            }
        ],
        'contact_channels': [
            {'channel': 'email', 'label': 'Admissoes', 'value': 'admissoes@colegiohorizonte.edu.br'},
            {'channel': 'whatsapp', 'label': 'Atendimento comercial', 'value': '(11) 97500-2040'},
            {'channel': 'email', 'label': 'Financeiro', 'value': 'financeiro@colegiohorizonte.edu.br'},
            {'channel': 'telefone', 'label': 'Financeiro', 'value': '(11) 3333-4203'},
            {'channel': 'email', 'label': 'Direcao', 'value': 'direcao@colegiohorizonte.edu.br'},
        ],
    }

    answer = _compose_service_routing_answer(
        profile,
        'Por qual canal eu falo com o setor de bolsas, com o financeiro e com a direcao da escola. Seja objetivo.',
    )

    assert 'Atendimento comercial / Admissoes' in answer
    assert 'Financeiro' in answer
    assert 'Direcao geral' in answer or 'Direcao' in answer


def test_public_profile_answer_handles_curriculum_subject_existence_and_listing() -> None:
    profile = {
        'school_name': 'Colegio Horizonte',
        'curriculum_basis': 'BNCC e aprofundamento academico',
        'curriculum_components': [
            'Língua Portuguesa e produção textual',
            'Matemática',
            'Biologia',
            'Física',
            'Química',
            'História',
            'Geografia',
            'Língua Inglesa',
        ],
    }

    subject_answer = _compose_public_profile_answer(
        profile,
        'Tem aula de Física?',
        original_message='Tem aula de Física?',
    )
    listing_answer = _compose_public_profile_answer(
        profile,
        'E quais outras matérias tem?',
        original_message='E quais outras matérias tem?',
    )
    difficulty_answer = _compose_public_profile_answer(
        profile,
        'Qual a matéria mais difícil de aprender no colégio?',
        original_message='Qual a matéria mais difícil de aprender no colégio?',
    )

    assert 'Sim.' in subject_answer
    assert 'Física' in subject_answer
    assert 'Matemática' in listing_answer or 'Matematica' in listing_answer
    assert 'nao existe uma unica materia oficialmente marcada como "a mais dificil"' in difficulty_answer.lower()


def test_authenticated_public_profile_rescue_promotes_curriculum_query_even_with_account_context() -> None:
    preview = _protected_preview()
    school_profile = {
        'school_name': 'Colegio Horizonte',
        'curriculum_basis': 'BNCC',
        'curriculum_components': ['Matemática', 'Física'],
    }

    applied = _apply_authenticated_public_profile_rescue(
        preview=preview,
        actor=_guardian_actor(),
        message='Tem aula de Física?',
        conversation_context={
            'recent_tool_calls': [
                {
                    'tool_name': 'orchestration.trace',
                    'request_payload': {
                        'slot_memory': {
                            'active_task': 'academic:grades',
                            'academic_student_name': 'Lucas Oliveira',
                        }
                    },
                }
            ]
        },
        school_profile=school_profile,
    )

    assert applied is True
    assert preview.classification.access_tier is AccessTier.public
    assert preview.reason == 'authenticated_public_profile_rescue'
    assert 'get_public_school_profile' in preview.selected_tools


def test_authenticated_public_profile_rescue_promotes_hypothetical_public_pricing() -> None:
    preview = _protected_preview()

    applied = _apply_authenticated_public_profile_rescue(
        preview=preview,
        actor=_guardian_actor(),
        message='Qual o valor da mensalidade pra 100 crianças?',
        conversation_context={
            'recent_tool_calls': [
                {
                    'tool_name': 'orchestration.trace',
                    'request_payload': {
                        'slot_memory': {
                            'active_task': 'academic:student_summary',
                            'academic_student_name': 'Lucas Oliveira',
                        }
                    },
                }
            ]
        },
        school_profile={'school_name': 'Colegio Horizonte'},
    )

    assert applied is True
    assert preview.classification.access_tier is AccessTier.public
    assert preview.reason == 'authenticated_public_profile_rescue'


def test_public_profile_answer_composes_multi_intent_contacts_and_pricing() -> None:
    profile = {
        'school_name': 'Colegio Horizonte',
        'district': 'Centro',
        'city': 'Curitiba',
        'state': 'PR',
        'address_line': 'Rua Exemplo, 100',
        'postal_code': '80000-000',
        'contact_channels': [
            {'label': 'Secretaria', 'channel': 'telefone', 'value': '(41) 3333-0000'},
            {'label': 'Secretaria digital', 'channel': 'whatsapp', 'value': '(41) 99999-0000'},
            {'label': 'Secretaria', 'channel': 'email', 'value': 'secretaria@colegiohorizonte.edu.br'},
        ],
        'service_catalog': [
            {
                'service_key': 'atendimento_admissoes',
                'title': 'Atendimento comercial / Admissoes',
                'request_channel': 'WhatsApp comercial ou visita guiada',
                'typical_eta': 'retorno em ate 1 dia util',
            },
            {
                'service_key': 'financeiro_escolar',
                'title': 'Financeiro',
                'request_channel': 'Portal autenticado ou email institucional',
                'typical_eta': 'retorno em ate 1 dia util',
            },
            {
                'service_key': 'solicitacao_direcao',
                'title': 'Direcao',
                'request_channel': 'Protocolo institucional ou ouvidoria',
                'typical_eta': 'ate 2 dias uteis',
            },
        ],
        'leadership_team': [
            {
                'title': 'Diretora geral',
                'name': 'Helena Martins',
                'contact_channel': 'direcao@colegiohorizonte.edu.br',
            }
        ],
        'tuition_reference': [
            {
                'segment': 'Ensino Medio',
                'shift_label': 'Manha',
                'monthly_amount': '1450.00',
                'enrollment_fee': '350.00',
                'notes': 'Desconto para irmaos pode ser analisado pela politica comercial publica.',
            }
        ],
    }

    answer = _compose_public_profile_answer(
        profile,
        'Quero os contatos de secretaria, financeiro e direcao, junto com mensalidade e bolsa para 3 filhos no ensino medio.',
        semantic_plan=PublicInstitutionPlan(
            conversation_act='service_routing',
            secondary_acts=('contacts', 'pricing'),
            required_tools=('get_public_school_profile', 'get_service_directory'),
            fetch_profile=True,
        ),
    )

    assert 'Setor certo por assunto' in answer
    assert 'Canais gerais da escola' in answer
    assert 'Valores publicos e simulacao' in answer
    assert '3 aluno(s)' in answer


def test_service_routing_query_detects_como_entrar_em_contato_prompt() -> None:
    assert _is_service_routing_query(
        'Como entrar em contato com admissoes, financeiro e direcao quando o assunto mistura bolsa e mensalidade?'
    ) is True


def test_direct_service_routing_bundle_query_detects_objective_multi_sector_prompt() -> None:
    assert _is_direct_service_routing_bundle_query(
        'Por qual canal eu falo com o setor de bolsas, com o financeiro e com a direcao da escola. Seja objetivo e grounded.'
    ) is True


def test_direct_service_routing_bundle_query_detects_quem_responde_por_cada_frente_prompt() -> None:
    assert _is_direct_service_routing_bundle_query(
        'Se eu precisar tratar desconto, financeiro e um assunto com a direcao, quem responde por cada frente?'
    ) is True


def test_direct_service_routing_bundle_query_ignores_pricing_projection_mix() -> None:
    assert _is_direct_service_routing_bundle_query(
        'Quero os canais do financeiro e da direcao junto com mensalidade e matricula para 3 filhos.'
    ) is False


def test_public_fast_answer_composes_contacts_and_pricing_for_compound_prompt() -> None:
    profile = {
        'school_name': 'Colégio Horizonte',
        'address_line': 'Rua das Acácias, 1450',
        'district': 'Vila Mariana',
        'city': 'São Paulo',
        'state': 'SP',
        'postal_code': '04567-120',
        'contact_channels': [
            {'channel': 'telefone', 'label': 'Secretaria', 'value': '(11) 3333-4200'},
            {'channel': 'whatsapp', 'label': 'Secretaria digital', 'value': '(11) 97500-2041'},
            {'channel': 'email', 'label': 'Financeiro', 'value': 'financeiro@colegiohorizonte.edu.br'},
            {'channel': 'email', 'label': 'Direcao', 'value': 'direcao@colegiohorizonte.edu.br'},
        ],
        'tuition_reference': [
            {
                'segment': 'Ensino Medio',
                'shift_label': 'Manha',
                'monthly_amount': '1450.00',
                'enrollment_fee': '350.00',
                'notes': 'Ha politica comercial para irmaos e pagamento pontual.',
            }
        ],
    }

    answer = _try_public_channel_fast_answer(
        message='Quero os contatos de secretaria, financeiro e direcao, junto com mensalidade e bolsa para 3 filhos no ensino medio.',
        profile=profile,
    )

    assert answer is not None
    assert 'Canais gerais da escola' in answer
    assert 'Valores publicos e simulacao' in answer
    assert '3 x R$ 1.450,00 = R$ 4.350,00' in answer


def test_public_pricing_short_follow_up_is_detected_from_recent_task() -> None:
    now_iso = datetime.now().astimezone().isoformat()
    conversation_context = {
        'recent_tool_calls': [
            {
                'tool_name': 'orchestration.trace',
                'created_at': now_iso,
                'request_payload': {
                    'slot_memory': {
                        'focus_kind': 'public',
                        'active_task': 'public:pricing',
                        'public_pricing_segment': 'Ensino Medio',
                    }
                },
            }
        ]
    }

    assert _is_public_pricing_context_follow_up('3o', conversation_context=conversation_context) is True
    recent_focus = _recent_conversation_focus(conversation_context)
    assert recent_focus is not None
    assert recent_focus.get('kind') == 'public'
    assert recent_focus.get('active_task') == 'public:pricing'
    assert recent_focus.get('public_pricing_segment') == 'Ensino Medio'


def test_public_pricing_context_follow_up_does_not_steal_explicit_documents_query() -> None:
    now_iso = datetime.now().astimezone().isoformat()
    conversation_context = {
        'recent_tool_calls': [
            {
                'tool_name': 'orchestration.trace',
                'created_at': now_iso,
                'request_payload': {
                    'slot_memory': {
                        'focus_kind': 'public',
                        'active_task': 'public:pricing',
                        'public_pricing_segment': 'Ensino Medio',
                    }
                },
            }
        ]
    }

    prompt = 'Quais documentos preciso para matricula?'
    assert _should_reuse_public_pricing_slots(prompt) is False
    assert _is_public_pricing_context_follow_up(prompt, conversation_context=conversation_context) is False


def test_public_capacity_query_distinguishes_parking_from_careers() -> None:
    assert _is_public_capacity_query('Quantas vagas tem?') is True
    assert _is_public_careers_query('Quantas vagas tem?') is False
    assert _is_public_capacity_query('Quantas vagas tem no estacionamento da escola?') is True
    assert _is_public_careers_query('Quantas vagas tem no estacionamento da escola?') is False


def test_public_pricing_followup_analysis_message_promotes_student_capacity() -> None:
    now_iso = datetime.now().astimezone().isoformat()
    conversation_context = SimpleNamespace(
        conversation_external_id='test',
        message_count=2,
        recent_messages=[
            {'sender_type': 'user', 'content': 'Mensalidade do ensino medio', 'created_at': now_iso},
            {
                'sender_type': 'assistant',
                'content': 'A mensalidade do Ensino Médio é R$ 1.450,00 e a matrícula é R$ 350,00.',
                'created_at': now_iso,
            },
        ],
        recent_tool_calls=[
            {
                'tool_name': 'orchestration.trace',
                'created_at': now_iso,
                'request_payload': {
                    'slot_memory': {
                        'focus_kind': 'public',
                        'active_task': 'public:pricing',
                        'active_entity': 'mensalidade',
                        'public_pricing_segment': 'Ensino Medio',
                    }
                },
            }
        ],
    )

    analysis_message = _build_analysis_message('Quantas vagas tem?', conversation_context)

    assert 'vagas para alunos' in analysis_message
    assert _is_public_capacity_query(analysis_message) is True
    assert _is_public_careers_query(analysis_message) is False


def test_public_capacity_followup_uses_recent_pricing_messages_even_without_slot_memory() -> None:
    now_iso = datetime.now().astimezone().isoformat()
    conversation_context = SimpleNamespace(
        conversation_external_id='test',
        message_count=2,
        recent_messages=[
            {'sender_type': 'user', 'content': 'Mensalidade do ensino medio', 'created_at': now_iso},
            {
                'sender_type': 'assistant',
                'content': 'A mensalidade do Ensino Médio é R$ 1.450,00 e a matrícula é R$ 350,00.',
                'created_at': now_iso,
            },
        ],
        recent_tool_calls=[],
    )

    analysis_message = _build_analysis_message('Quantas vagas tem?', conversation_context)

    assert 'vagas para alunos' in analysis_message
    assert _is_public_careers_query(analysis_message) is False


def test_public_calendar_followup_uses_recent_messages_even_without_active_task() -> None:
    now_iso = datetime.now().astimezone().isoformat()
    conversation_context = SimpleNamespace(
        conversation_external_id='test',
        message_count=2,
        recent_messages=[
            {'sender_type': 'assistant', 'content': 'As aulas começam em 2 de fevereiro de 2026.', 'created_at': now_iso},
        ],
        recent_tool_calls=[],
    )

    analysis_message = _build_analysis_message('Já começaram então?', conversation_context)

    assert 'datas e acompanhamento do evento anterior no calendario institucional' in analysis_message


def test_public_institution_plan_forces_capacity_on_generic_vagas_followup() -> None:
    plan = _build_public_institution_plan(
        'Quantas vagas tem?',
        [],
        conversation_context=None,
        school_profile=None,
    )

    assert plan.conversation_act == 'capacity'
    assert 'get_public_school_profile' in plan.required_tools


def test_public_institution_plan_forces_timeline_on_temporal_followup_with_recent_calendar_messages() -> None:
    now_iso = datetime.now().astimezone().isoformat()
    conversation_context = {
        'conversation_external_id': 'test',
        'message_count': 2,
        'recent_messages': [
            {'sender_type': 'assistant', 'content': 'As aulas começam em 2 de fevereiro de 2026.', 'created_at': now_iso},
        ],
        'recent_tool_calls': [],
    }

    plan = _build_public_institution_plan(
        'Já começaram então?',
        [],
        conversation_context=conversation_context,
        school_profile=None,
    )

    assert plan.conversation_act == 'timeline'
    assert 'get_public_timeline' in plan.required_tools


def test_protected_domain_rescue_promotes_academic_risk_label_from_clarify() -> None:
    preview = _protected_preview()
    applied = _apply_protected_domain_rescue(
        preview=preview,
        actor=_guardian_actor(),
        message='Recorte so a Ana e diga onde o risco academico dela esta mais alto agora.',
        conversation_context=None,
    )
    assert applied is True
    assert preview.mode is OrchestrationMode.structured_tool
    assert preview.classification.domain is QueryDomain.academic
    assert 'get_student_academic_summary' in preview.selected_tools


def test_protected_domain_rescue_promotes_documental_student_admin_from_clarify() -> None:
    preview = _protected_preview()
    applied = _apply_protected_domain_rescue(
        preview=preview,
        actor=_guardian_actor(),
        message='Quero ver o quadro documental da Ana e o que esta pendente.',
        conversation_context=None,
    )
    assert applied is True
    assert preview.mode is OrchestrationMode.structured_tool
    assert preview.classification.domain is QueryDomain.institution
    assert 'get_student_administrative_status' in preview.selected_tools


def test_protected_domain_rescue_does_not_steal_restricted_document_query() -> None:
    preview = _protected_preview()
    applied = _apply_protected_domain_rescue(
        preview=preview,
        actor=_guardian_actor(),
        message='Pelo manual interno do professor, qual e a regra para registro de avaliacoes e comunicacao com foco pedagogico?',
        conversation_context=None,
    )
    assert applied is False
    assert preview.mode is OrchestrationMode.clarify


def test_attendance_prompt_does_not_create_false_unmatched_student_reference() -> None:
    students = _guardian_actor()["linked_students"]
    assert _explicit_unmatched_student_reference(
        students,
        'Recorte so o Lucas e diga onde a frequencia dele esta mais sensivel por faltas recentes.',
        conversation_context=None,
    ) is None


def test_restricted_teacher_manual_prompt_does_not_create_false_unmatched_student_reference() -> None:
    students = _guardian_actor()["linked_students"]
    assert _explicit_unmatched_student_reference(
        students,
        'No manual interno do professor, qual e a regra para registro de avaliacoes e comunicacao pedagogica?',
        conversation_context=None,
    ) is None


def test_access_scope_prompt_does_not_create_false_unmatched_student_reference() -> None:
    students = _guardian_actor()["linked_students"]
    assert _explicit_unmatched_student_reference(
        students,
        'Estou autenticado como quem e com qual escopo academico e financeiro eu consigo ver?',
        conversation_context=None,
    ) is None


def test_select_linked_student_reuses_recent_student_for_finance_followup() -> None:
    student, clarification = _select_linked_student(
        _guardian_actor(),
        'e o financeiro do lucas como está?',
        capability='finance',
        conversation_context={
            'recent_messages': [
                {'sender_type': 'user', 'content': 'quais as notas do lucas'},
                {'sender_type': 'assistant', 'content': 'Notas de Lucas Oliveira...'},
            ],
            'recent_tool_calls': [
                {
                    'tool_name': 'orchestration.trace',
                    'request_payload': {
                        'slot_memory': {
                            'finance_student_name': 'Lucas Oliveira',
                            'academic_student_name': 'Lucas Oliveira',
                            'active_task': 'finance:billing',
                        }
                    },
                }
            ],
        },
    )

    assert clarification is None
    assert student is not None
    assert student['full_name'] == 'Lucas Oliveira'


def test_compose_admin_finance_combined_answer_includes_finance_section() -> None:
    answer = _compose_admin_finance_combined_answer(
        admin_summary={
            'overall_status': 'pending',
            'checklist': [],
            'next_step': 'Atualizar comprovante.',
        },
        finance_summaries=[
            {
                'student_name': 'Ana Oliveira',
                'open_invoice_count': 2,
                'overdue_invoice_count': 0,
                'invoices': [],
            }
        ],
        requested_admin_attribute=None,
    )
    assert answer is not None
    assert 'Financeiro:' in answer


def test_compose_admin_finance_block_status_answer_prefers_admin_block() -> None:
    answer = _compose_admin_finance_block_status_answer(
        admin_summary={'overall_status': 'pending'},
        finance_summaries=[
            {
                'student_name': 'Ana Oliveira',
                'open_invoice_count': 2,
                'overdue_invoice_count': 0,
                'invoices': [],
            }
        ],
    )
    assert answer == 'Hoje ainda existe bloqueio administrativo ou documental neste recorte.'


def test_compose_academic_risk_answer_mentions_media_parcial() -> None:
    answer = _compose_academic_risk_answer(
        {
            'student_name': 'Ana Oliveira',
            'grades': [
                {'subject_name': 'Fisica', 'score': '6.3', 'max_score': '10.0'},
                {'subject_name': 'Historia', 'score': '7.2', 'max_score': '10.0'},
                {'subject_name': 'Matematica', 'score': '7.8', 'max_score': '10.0'},
            ],
        },
        student_name='Ana Oliveira',
    )
    assert 'media parcial' in answer
    assert 'Fisica' in answer


def test_compose_attendance_attribute_answer_mentions_frequencia_and_subject() -> None:
    answer = _compose_academic_attribute_answer(
        {
            'attendance': [
                {
                    'subject_name': 'Tecnologia e Cultura Digital',
                    'present_count': 19,
                    'late_count': 7,
                    'absent_count': 6,
                }
            ]
        },
        attribute_request=ProtectedAttributeRequest(domain='academic', attribute='attendance'),
        student_name='Lucas Oliveira',
        message='Recorte so o Lucas e diga onde a frequencia dele esta mais sensivel por faltas recentes.',
    )
    assert 'principal alerta de frequencia de Lucas Oliveira' in answer
    assert 'Tecnologia e Cultura Digital' in answer


def test_compose_attendance_attribute_answer_surfaces_principal_alerta() -> None:
    answer = _compose_academic_attribute_answer(
        {
            'attendance': [
                {
                    'subject_name': 'Tecnologia e Cultura Digital',
                    'present_count': 19,
                    'late_count': 7,
                    'absent_count': 6,
                }
            ]
        },
        attribute_request=ProtectedAttributeRequest(domain='academic', attribute='attendance'),
        student_name='Lucas Oliveira',
        message='Hoje, qual e o principal alerta de frequencia do Lucas olhando as faltas registradas?',
    )
    assert 'principal alerta de frequencia de Lucas Oliveira' in answer
    assert 'Tecnologia e Cultura Digital' in answer
    assert 'maior combinacao de faltas e atrasos' in answer


def test_compose_attendance_attribute_answer_explains_why_frequency_concerns_student() -> None:
    answer = _compose_academic_attribute_answer(
        {
            'attendance': [
                {
                    'subject_name': 'Fisica',
                    'present_count': 18,
                    'late_count': 3,
                    'absent_count': 5,
                },
                {
                    'subject_name': 'Matematica',
                    'present_count': 20,
                    'late_count': 1,
                    'absent_count': 2,
                },
            ]
        },
        attribute_request=ProtectedAttributeRequest(domain='academic', attribute='attendance'),
        student_name='Lucas Oliveira',
        message='Continuando a analise, isole o Lucas e mostre por que a frequencia dele preocupa mais ou menos.',
    )
    assert 'principal alerta de frequencia de Lucas Oliveira' in answer
    assert 'Fisica' in answer
    assert 'maior combinacao de faltas e atrasos' in answer


def test_family_attendance_aggregate_query_is_not_treated_as_generic_academic_aggregate() -> None:
    prompt = 'Me de um panorama de faltas e frequencia dos meus filhos, apontando quem exige maior atencao agora.'
    assert _looks_like_family_attendance_aggregate_query(prompt) is True
    assert _should_prioritize_protected_sql_query(
        prompt,
        actor=_guardian_actor(),
        conversation_context=None,
    ) is True


def test_family_academic_aggregate_query_accepts_academicamente_pior_prompt() -> None:
    prompt = 'Sem me dar tabela, qual dos meus filhos esta academicamente pior hoje e em qual disciplina isso fica mais claro?'
    assert _looks_like_family_academic_aggregate_query(prompt) is True


def test_select_linked_student_accepts_focus_marked_ana_after_negated_lucas() -> None:
    student, clarification = _select_linked_student(
        _guardian_actor(),
        'Sem repetir o Lucas, corta so para a Ana e me diga qual componente dela acende mais alerta agora.',
        capability='academic',
        conversation_context={
            'recent_messages': [
                {
                    'sender_type': 'assistant',
                    'content': 'Panorama academico das contas vinculadas:\n- Lucas Oliveira: Fisica 5,9; Matematica 7,4\n- Ana Oliveira: Historia 6,8; Portugues 7,1\nQuem hoje exige maior atencao academica e Lucas Oliveira, principalmente em Fisica.',
                }
            ],
        },
    )
    assert clarification is None
    assert student is not None
    assert student['full_name'] == 'Ana Oliveira'


def test_compose_attendance_attribute_answer_handles_chamam_atencao_prompt() -> None:
    answer = _compose_academic_attribute_answer(
        {
            'attendance': [
                {
                    'subject_name': 'Tecnologia e Cultura Digital',
                    'present_count': 19,
                    'late_count': 7,
                    'absent_count': 6,
                }
            ]
        },
        attribute_request=ProtectedAttributeRequest(domain='academic', attribute='attendance'),
        student_name='Lucas Oliveira',
        message='No Lucas, quais faltas ou ausencias mais chamam atencao agora e como isso bate na frequencia dele?',
    )
    assert 'principal alerta de frequencia de Lucas Oliveira' in answer
    assert 'Tecnologia e Cultura Digital' in answer
    assert 'Proximo passo:' in answer


def test_direct_service_routing_bundle_query_detects_nao_me_manda_menu_geral_prompt() -> None:
    assert _is_direct_service_routing_bundle_query(
        'Nao me manda menu geral: quais setores e canais realmente resolvem bolsa, financeiro e direcao?'
    ) is True


def test_family_attendance_aggregate_query_accepts_two_children_attention_wording() -> None:
    prompt = 'Faca um resumo de frequencia dos meus dois filhos e destaque quem inspira mais atencao por faltas.'
    assert _looks_like_family_attendance_aggregate_query(prompt) is True
    assert _should_prioritize_protected_sql_query(
        prompt,
        actor=_guardian_actor(),
        conversation_context=None,
    ) is True


def test_family_attendance_aggregate_query_accepts_more_attention_wording() -> None:
    prompt = 'Me mostre a frequencia dos meus dois filhos e diga quem exige mais atenção agora.'
    assert _looks_like_family_attendance_aggregate_query(prompt) is True
    assert _should_prioritize_protected_sql_query(
        prompt,
        actor=_guardian_actor(),
        conversation_context=None,
    ) is True


def test_family_attendance_aggregate_query_rejects_academic_components_followup() -> None:
    prompt = (
        'Sem sair do escopo do projeto, depois do panorama dos meus filhos, '
        'fique apenas com a Ana e diga quais componentes merecem mais atencao agora.'
    )
    assert _looks_like_family_attendance_aggregate_query(prompt) is False


def test_compose_family_attendance_aggregate_answer_points_to_highest_attention_student() -> None:
    answer = _compose_family_attendance_aggregate_answer(
        [
            {
                'student_name': 'Lucas Oliveira',
                'attendance': [
                    {'subject_name': 'Fisica', 'present_count': 9, 'late_count': 2, 'absent_count': 3, 'absent_minutes': 120},
                ],
            },
            {
                'student_name': 'Ana Oliveira',
                'attendance': [
                    {'subject_name': 'Fisica', 'present_count': 12, 'late_count': 0, 'absent_count': 1, 'absent_minutes': 50},
                ],
            },
        ]
    )
    assert 'Lucas Oliveira' in answer
    assert 'Quem exige maior atencao agora: Lucas Oliveira.' in answer


def test_compose_academic_aggregate_answer_uses_true_lowest_subject_when_below_target() -> None:
    answer = _compose_academic_aggregate_answer(
        [
            {
                'student_name': 'Lucas Oliveira',
                'grades': [
                    {'subject_name': 'Fisica', 'score': '5.9', 'max_score': '10.0'},
                    {'subject_name': 'Historia', 'score': '6.7', 'max_score': '10.0'},
                ],
            },
            {
                'student_name': 'Ana Oliveira',
                'grades': [
                    {'subject_name': 'Fisica', 'score': '6.4', 'max_score': '10.0'},
                    {'subject_name': 'Historia', 'score': '7.2', 'max_score': '10.0'},
                ],
            },
        ]
    )
    assert 'Quem hoje exige maior atencao academica e Lucas Oliveira, principalmente em Fisica.' in answer


def test_public_explanatory_bundle_query_does_not_trigger_support_navigation_rescue() -> None:
    assert _is_public_support_navigation_query(
        'Se eu quiser entender o suporte ao aluno alem da sala regular, como periodo integral e estudo orientado se completam no material publico da escola?'
    ) is False


def test_explicit_protected_domain_hint_ignores_public_canonical_conduct_prompt() -> None:
    hinted = _explicit_protected_domain_hint(
        'Como frequencia, pontualidade e convivencia aparecem como um mesmo eixo de acompanhamento estudantil no regulamento publico?',
        actor=_guardian_actor(),
        conversation_context=None,
    )
    assert hinted is None


def test_explicit_protected_domain_hint_ignores_public_bullying_policy_prompt_even_after_admin_context() -> None:
    conversation_context = {
        'recent_messages': [
            {'sender_type': 'assistant', 'content': 'Situacao administrativa do seu cadastro hoje: com pendencias.'},
        ],
        'recent_tool_calls': [
            {
                'tool_name': 'orchestration_trace',
                'status': 'succeeded',
                'response_payload': {
                    'active_task': 'admin:administrative_status',
                    'active_entity': 'seu cadastro',
                    'kind': 'secretaria',
                },
            }
        ],
    }
    prompt = 'O que a escola pensa sobre bullying?'
    assert match_python_functions_public_canonical_lane(prompt) == 'public_bundle.conduct_frequency_punctuality'
    assert _explicit_protected_domain_hint(
        prompt,
        actor=_guardian_actor(),
        conversation_context=conversation_context,
    ) is None


def test_explicit_unmatched_student_reference_ignores_public_safety_policy_terms() -> None:
    students = _guardian_actor()["linked_students"]
    assert _explicit_unmatched_student_reference(
        students,
        'O que acontece se um aluno tacar bomba na escola?',
        conversation_context=None,
    ) is None


def test_public_documentary_open_query_blocks_generic_profile_leak() -> None:
    assert _looks_like_public_documentary_open_query(
        'Quero entender como a escola costura atividade externa, autorizacoes de familia e saude do estudante na base publica.'
    ) is True


def test_public_open_documentary_topic_detects_extended_day() -> None:
    assert (
        _public_open_documentary_topic(
            'Sem repetir slogans, que arquitetura de rotina escolar aparece quando se combinam turno estendido, oficinas, refeicao, estudo acompanhado e permanencia no contraturno?'
        )
        == 'extended_day_ecosystem'
    )


def test_public_open_documentary_plan_promotes_candidate_synthesis() -> None:
    plan = _build_public_institution_plan(
        'Se uma familia precisa entender por onde um tema caminha dentro da escola, que trilha institucional os documentos publicos sugerem entre secretaria, coordenacao, direcao e canais oficiais?',
        ['get_public_school_profile'],
        semantic_plan=None,
        conversation_context=None,
        school_profile=None,
    )
    assert plan.semantic_source == 'open_documentary_rules'
    assert plan.conversation_act == 'canonical_fact'
    assert _should_use_public_open_documentary_synthesis(
        'Se uma familia precisa entender por onde um tema caminha dentro da escola, que trilha institucional os documentos publicos sugerem entre secretaria, coordenacao, direcao e canais oficiais?',
        plan,
    ) is True


from ai_orchestrator.models import IntentClassification, MessageResponse, RetrievalBackend


def test_message_response_supports_explicit_llm_debug_fields() -> None:
    response = MessageResponse(
        message_text='ok',
        mode=OrchestrationMode.structured_tool,
        classification=IntentClassification(
            domain=QueryDomain.institution,
            access_tier=AccessTier.public,
            confidence=1.0,
            reason='test',
        ),
        retrieval_backend=RetrievalBackend.none,
        reason='test_reason',
        used_llm=True,
        llm_stages=['answer_composition'],
        candidate_chosen='documentary_synthesis',
        candidate_reason='documentary_candidate_selected',
        retrieval_probe_topic='governance_channels',
        response_cache_hit=True,
        response_cache_kind='semantic',
    )
    assert response.used_llm is True
    assert response.llm_stages == ['answer_composition']
    assert response.candidate_chosen == 'documentary_synthesis'
    assert response.response_cache_hit is True


def test_explicit_unmatched_student_reference_ignores_family_scope_phrase_cada_filho() -> None:
    students = _guardian_actor()["linked_students"]
    assert _explicit_unmatched_student_reference(
        students,
        'Qual e exatamente o meu escopo: posso ver academico, financeiro ou os dois para cada filho?',
        conversation_context=None,
    ) is None


def test_family_finance_aggregate_query_detects_leigo_breakdown_prompt() -> None:
    prompt = 'Explique a minha situacao financeira como se eu fosse leigo, separando mensalidade, taxa, atraso e desconto dos meus filhos.'
    assert _looks_like_family_finance_aggregate_query(prompt) is True


def test_family_finance_aggregate_query_rejects_third_party_partial_payment_prompt_without_family_anchor() -> None:
    prompt = 'Paguei parte da mensalidade do Joao e preciso negociar o restante; o que ja aparece e qual o proximo passo?'
    assert _looks_like_family_finance_aggregate_query(prompt) is False


def test_explicit_protected_domain_hint_promotes_family_admin_aggregate_even_without_recent_focus() -> None:
    assert _explicit_protected_domain_hint(
        'Compare a documentacao dos meus filhos e diga qual deles ainda tem pendencia.',
        actor=_guardian_actor(),
        conversation_context=None,
    ) is QueryDomain.institution


def test_public_pricing_navigation_query_rejects_partial_payment_negotiation_prompt() -> None:
    prompt = 'Paguei parte da mensalidade do Joao e preciso negociar o restante; o que ja aparece e qual o proximo passo?'
    assert _is_public_pricing_navigation_query(prompt) is False


def test_should_prioritize_protected_sql_query_for_partial_payment_negotiation() -> None:
    prompt = 'Paguei parte da mensalidade do Joao e preciso negociar o restante; o que ja aparece e qual o proximo passo?'
    assert _should_prioritize_protected_sql_query(
        prompt,
        actor=_guardian_actor(),
        conversation_context=None,
    ) is True
