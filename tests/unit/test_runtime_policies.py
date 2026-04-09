from __future__ import annotations

from datetime import datetime
from types import SimpleNamespace

from ai_orchestrator.models import AccessTier, OrchestrationMode, QueryDomain
from ai_orchestrator.runtime import (
    ProtectedAttributeRequest,
    _apply_protected_domain_rescue,
    _build_analysis_message,
    _build_conversation_slot_memory,
    _build_public_institution_plan,
    _compose_academic_attribute_answer,
    _compose_academic_risk_answer,
    _compose_admin_finance_combined_answer,
    _explicit_protected_domain_hint,
    _explicit_unmatched_student_reference,
    _is_public_capacity_query,
    _is_public_careers_query,
    _is_public_support_navigation_query,
    _is_public_pricing_context_follow_up,
    _is_public_pricing_navigation_query,
    _looks_like_public_documentary_open_query,
    _public_open_documentary_topic,
    _recent_conversation_focus,
    _select_linked_student,
    _should_polish_structured_answer,
    _should_prioritize_protected_sql_query,
    _should_use_public_open_documentary_synthesis,
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


def test_langgraph_public_canonical_lane_skips_polish() -> None:
    request = SimpleNamespace(channel=SimpleNamespace(value="telegram"))
    preview = _preview(reason="langgraph_public_canonical_lane:public_bundle.year_three_phases")
    assert _should_polish_structured_answer(preview=preview, request=request) is False


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
    assert 'frequencia de Lucas Oliveira' in answer
    assert 'Tecnologia e Cultura Digital' in answer


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
