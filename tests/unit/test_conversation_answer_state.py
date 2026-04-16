from __future__ import annotations

from ai_orchestrator.conversation_answer_state import _extract_unknown_student_reference, resolve_answer_focus


def _actor() -> dict[str, object]:
    return {
        'linked_students': [
            {
                'student_id': 'lucas-id',
                'full_name': 'Lucas Oliveira',
                'can_view_academic': True,
                'can_view_finance': True,
            },
            {
                'student_id': 'ana-id',
                'full_name': 'Ana Oliveira',
                'can_view_academic': True,
                'can_view_finance': True,
            },
        ]
    }


def test_resolve_answer_focus_uses_slot_memory_for_finance_followup() -> None:
    focus = resolve_answer_focus(
        request_message='e o financeiro dele como está?',
        actor=_actor(),
        conversation_context={
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
            ]
        },
    )

    assert focus.domain == 'finance'
    assert focus.student_name == 'Lucas Oliveira'
    assert focus.uses_memory is True


def test_resolve_answer_focus_keeps_justification_scope() -> None:
    focus = resolve_answer_focus(
        request_message='é atestado de ficar dormindo, serve?',
        actor=_actor(),
        conversation_context={
            'recent_tool_calls': [
                {
                    'tool_name': 'orchestration.trace',
                    'request_payload': {
                        'slot_memory': {
                            'academic_student_name': 'Lucas Oliveira',
                            'active_task': 'academic:attendance',
                        }
                    },
                }
            ]
        },
    )

    assert focus.domain == 'institution'
    assert focus.topic == 'attendance_justification'


def test_resolve_answer_focus_uses_followup_task_to_keep_student_and_subject() -> None:
    focus = resolve_answer_focus(
        request_message='e dela em história?',
        actor=_actor(),
        conversation_context={
            'recent_messages': [
                {'sender_type': 'user', 'content': 'quais as notas do lucas?'},
                {'sender_type': 'assistant', 'content': 'Notas de Lucas Oliveira...'},
                {'sender_type': 'user', 'content': 'e da ana?'},
            ],
            'recent_tool_calls': [
                {
                    'tool_name': 'orchestration.trace',
                    'request_payload': {
                        'slot_memory': {
                            'academic_student_name': 'Ana Oliveira',
                            'finance_student_name': 'Ana Oliveira',
                            'active_task': 'academic:grades',
                            'academic_attribute': 'grades',
                            'active_subject': 'Historia',
                        }
                    },
                }
            ],
        },
    )

    assert focus.domain == 'academic'
    assert focus.topic == 'grades'
    assert focus.student_name == 'Ana Oliveira'
    assert focus.subject_name == 'Historia'
    assert focus.academic_attribute == 'grades'
    assert focus.uses_memory is True


def test_resolve_answer_focus_uses_finance_slot_for_short_followup() -> None:
    focus = resolve_answer_focus(
        request_message='e o financeiro?',
        actor=_actor(),
        conversation_context={
            'recent_tool_calls': [
                {
                    'tool_name': 'orchestration.trace',
                    'request_payload': {
                        'slot_memory': {
                            'finance_student_name': 'Lucas Oliveira',
                            'active_task': 'finance:billing',
                            'finance_attribute': 'next_due',
                            'finance_status_filter': 'open',
                        }
                    },
                }
            ]
        },
    )

    assert focus.domain == 'finance'
    assert focus.topic == 'student_finance'
    assert focus.student_name == 'Lucas Oliveira'
    assert focus.finance_attribute == 'next_due'
    assert focus.finance_status_filter == 'open'
    assert focus.uses_memory is True


def test_resolve_answer_focus_tracks_public_pricing_followup_from_slot_memory() -> None:
    focus = resolve_answer_focus(
        request_message='E para 20 filhos?',
        actor=_actor(),
        conversation_context={
            'recent_tool_calls': [
                {
                    'tool_name': 'orchestration.trace',
                    'request_payload': {
                        'slot_memory': {
                            'active_task': 'public:pricing',
                            'public_pricing_segment': 'Ensino Medio',
                            'public_pricing_grade_year': '3o ano',
                            'public_pricing_quantity': '20',
                            'public_pricing_price_kind': 'enrollment_fee',
                        }
                    },
                }
            ]
        },
    )

    assert focus.domain == 'public'
    assert focus.topic == 'pricing'
    assert focus.public_pricing_segment == 'Ensino Medio'
    assert focus.public_pricing_grade_year == '3o ano'
    assert focus.public_pricing_quantity == '20'
    assert focus.public_pricing_price_kind == 'enrollment_fee'


def test_resolve_answer_focus_does_not_misclassify_family_calendar_bundle_as_pricing() -> None:
    focus = resolve_answer_focus(
        request_message='Pensando no caso pratico, estou chegando agora com meu primeiro filho: como matricula, calendario e agenda de avaliacoes se encaixam no primeiro bimestre?',
        actor=_actor(),
        conversation_context=None,
    )

    assert focus.topic != 'pricing'
    assert focus.public_pricing_segment is None


def test_resolve_answer_focus_recovers_public_pricing_from_historical_trace() -> None:
    focus = resolve_answer_focus(
        request_message='E para 20 filhos?',
        actor=_actor(),
        conversation_context={
            'recent_tool_calls': [
                {
                    'tool_name': 'orchestration.trace',
                    'request_payload': {
                        'slot_memory': {
                            'active_task': 'public:pricing',
                            'public_pricing_segment': 'Ensino Medio',
                            'public_pricing_grade_year': '3o ano',
                            'public_pricing_price_kind': 'enrollment_fee',
                        }
                    },
                },
                {
                    'tool_name': 'orchestration.trace',
                    'request_payload': {
                        'slot_memory': {
                            'active_task': 'academic:student_summary',
                            'public_pricing_quantity': '20',
                        }
                    },
                },
            ]
        },
    )

    assert focus.domain == 'public'
    assert focus.topic == 'pricing'
    assert focus.public_pricing_segment == 'Ensino Medio'
    assert focus.public_pricing_grade_year == '3o ano'
    assert focus.public_pricing_quantity == '20'
    assert focus.public_pricing_price_kind == 'enrollment_fee'


def test_resolve_answer_focus_recovers_public_pricing_from_recent_messages() -> None:
    focus = resolve_answer_focus(
        request_message='E para 20 filhos?',
        actor=_actor(),
        conversation_context={
            'recent_messages': [
                {'sender_type': 'user', 'content': 'Qual a mensalidade do ensino medio?'},
                {
                    'sender_type': 'assistant',
                    'content': 'Para Ensino Medio no turno Manha, a mensalidade pública de referência é R$ 1.450,00 e a taxa de matrícula é R$ 350,00.',
                },
                {'sender_type': 'user', 'content': 'Quanto seria a matricula para 20 filhos?'},
            ],
            'recent_tool_calls': [
                {
                    'tool_name': 'orchestration.trace',
                    'request_payload': {
                        'slot_memory': {
                            'active_task': 'academic:student_summary',
                            'public_pricing_quantity': '20',
                            'public_pricing_price_kind': 'enrollment_fee',
                        }
                    },
                }
            ],
        },
    )

    assert focus.domain == 'public'
    assert focus.topic == 'pricing'
    assert focus.public_pricing_segment == 'Ensino Medio'
    assert focus.public_pricing_quantity == '20'


def test_resolve_answer_focus_does_not_leak_public_pricing_into_justification_followup() -> None:
    focus = resolve_answer_focus(
        request_message='é atestado de ficar dormindo, serve?',
        actor=_actor(),
        conversation_context={
            'recent_messages': [
                {'sender_type': 'user', 'content': 'Qual a mensalidade do ensino medio?'},
                {'sender_type': 'assistant', 'content': 'A mensalidade pública de referência é R$ 1.450,00.'},
            ],
            'recent_tool_calls': [
                {
                    'tool_name': 'orchestration.trace',
                    'request_payload': {
                        'slot_memory': {
                            'active_task': 'public:pricing',
                            'public_pricing_segment': 'Ensino Medio',
                            'public_pricing_price_kind': 'monthly_amount',
                        }
                    },
                }
            ],
        },
    )

    assert focus.domain == 'institution'
    assert focus.topic == 'attendance_justification'


def test_resolve_answer_focus_detects_family_aggregate_without_disambiguation() -> None:
    focus = resolve_answer_focus(
        request_message='De forma bem objetiva, me de um panorama academico dos meus filhos e diga qual deles aparece mais perto da media minima agora.',
        actor=_actor(),
        conversation_context=None,
    )

    assert focus.domain == 'academic'
    assert focus.topic == 'grades'
    assert focus.asks_family_aggregate is True
    assert focus.needs_disambiguation is False


def test_resolve_answer_focus_detects_family_upcoming_assessments_when_two_students_are_named() -> None:
    focus = resolve_answer_focus(
        request_message='Resuma as proximas provas e avaliacoes previstas para Lucas e Ana.',
        actor=_actor(),
        conversation_context=None,
    )

    assert focus.domain == 'academic'
    assert focus.topic == 'upcoming_assessments'
    assert focus.asks_family_aggregate is True
    assert focus.student_name is None
    assert focus.needs_disambiguation is False


def test_resolve_answer_focus_detects_public_known_unknown_query() -> None:
    focus = resolve_answer_focus(
        request_message='Quero saber se a escola publica a quantidade total de professores ou se esse dado nao esta disponivel.',
        actor=None,
        conversation_context=None,
    )

    assert focus.domain == 'public'
    assert focus.topic == 'known_unknown'
    assert focus.is_repair_followup is False


def test_resolve_answer_focus_marks_short_ambiguous_followup_for_clarification() -> None:
    focus = resolve_answer_focus(
        request_message='do lucas serve?',
        actor=_actor(),
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
    )

    assert focus.domain == 'conversation'
    assert focus.topic == 'clarify'
    assert focus.student_name == 'Lucas Oliveira'
    assert focus.needs_disambiguation is True


def test_resolve_answer_focus_keeps_grade_domain_for_repair_with_explicit_subject() -> None:
    focus = resolve_answer_focus(
        request_message='por que não falou antes a nota de geografia?',
        actor=_actor(),
        conversation_context={
            'recent_tool_calls': [
                {
                    'tool_name': 'orchestration.trace',
                    'request_payload': {
                        'slot_memory': {
                            'active_task': 'academic:grades',
                            'academic_student_name': 'Lucas Oliveira',
                            'active_subject': 'Historia',
                        }
                    },
                }
            ]
        },
    )

    assert focus.domain == 'academic'
    assert focus.topic == 'grades'
    assert focus.subject_name == 'Geografia'
    assert focus.is_repair_followup is True


def test_resolve_answer_focus_does_not_treat_negated_justification_as_attendance_policy() -> None:
    focus = resolve_answer_focus(
        request_message='não quero justificar, quero saber a nota do lucas',
        actor=_actor(),
        conversation_context={
            'recent_tool_calls': [
                {
                    'tool_name': 'orchestration.trace',
                    'request_payload': {
                        'slot_memory': {
                            'active_task': 'academic:attendance',
                            'academic_student_name': 'Lucas Oliveira',
                        }
                    },
                }
            ]
        },
    )

    assert focus.domain == 'academic'
    assert focus.topic == 'grades'
    assert focus.student_name == 'Lucas Oliveira'


def test_resolve_answer_focus_marks_subject_only_followup_without_student_for_disambiguation() -> None:
    focus = resolve_answer_focus(
        request_message='e de english',
        actor=_actor(),
        conversation_context={
            'recent_tool_calls': [
                {
                    'tool_name': 'orchestration.trace',
                    'request_payload': {
                        'slot_memory': {
                            'active_task': 'academic:grades',
                        }
                    },
                }
            ]
        },
    )

    assert focus.domain == 'academic'
    assert focus.topic == 'grades'
    assert focus.subject_name == 'Lingua Inglesa'
    assert focus.student_name is None
    assert focus.needs_disambiguation is True


def test_resolve_answer_focus_detects_unknown_student_without_reusing_memory() -> None:
    focus = resolve_answer_focus(
        request_message='qual a nota da laura?',
        actor=_actor(),
        conversation_context={
            'recent_tool_calls': [
                {
                    'tool_name': 'orchestration.trace',
                    'request_payload': {
                        'slot_memory': {
                            'academic_student_name': 'Lucas Oliveira',
                            'active_task': 'academic:grades',
                        }
                    },
                }
            ]
        },
    )

    assert focus.domain == 'academic'
    assert focus.topic == 'grades'
    assert focus.student_name is None
    assert focus.unknown_student_name == 'Laura'
    assert focus.uses_memory is False


def test_resolve_answer_focus_detects_unknown_subject_without_reusing_old_subject() -> None:
    focus = resolve_answer_focus(
        request_message='e as notas de dança?',
        actor=_actor(),
        conversation_context={
            'recent_tool_calls': [
                {
                    'tool_name': 'orchestration.trace',
                    'request_payload': {
                        'slot_memory': {
                            'academic_student_name': 'Lucas Oliveira',
                            'active_task': 'academic:grades',
                            'active_subject': 'Fisica',
                        }
                    },
                }
            ]
        },
    )

    assert focus.domain == 'academic'
    assert focus.topic == 'grades'
    assert focus.student_name == 'Lucas Oliveira'
    assert focus.subject_name is None
    assert focus.unknown_subject_name == 'Danca'
    assert focus.uses_memory is True


def test_resolve_answer_focus_ignores_interrogative_subject_placeholder_on_family_followup() -> None:
    focus = resolve_answer_focus(
        request_message='Pensando no caso pratico, agora quero apenas a Ana: em quais materias ela aparece mais exposta?',
        actor=_actor(),
        conversation_context={
            'recent_tool_calls': [
                {
                    'tool_name': 'orchestration.trace',
                    'request_payload': {
                        'slot_memory': {
                            'academic_student_name': 'Ana Oliveira',
                            'active_task': 'academic:grades',
                        }
                    },
                }
            ]
        },
    )

    assert focus.domain == 'academic'
    assert focus.student_name == 'Ana Oliveira'
    assert focus.unknown_subject_name is None


def test_resolve_answer_focus_marks_meta_repair_followup() -> None:
    focus = resolve_answer_focus(
        request_message='essa resposta aqui era sobre o que então?',
        actor=_actor(),
        conversation_context={
            'recent_tool_calls': [
                {
                    'tool_name': 'orchestration.trace',
                    'request_payload': {
                        'slot_memory': {
                            'academic_student_name': 'Lucas Oliveira',
                            'active_task': 'academic:upcoming_assessments',
                        }
                    },
                }
            ]
        },
    )

    assert focus.domain == 'conversation'
    assert focus.topic == 'repair'
    assert focus.is_repair_followup is True
    assert focus.public_pricing_segment is None


def test_resolve_answer_focus_keeps_upcoming_scope_when_subject_refines_previous_upcoming_turn() -> None:
    focus = resolve_answer_focus(
        request_message='e a próxima de matemática?',
        actor=_actor(),
        conversation_context={
            'recent_messages': [
                {'sender_type': 'user', 'content': 'quais as próximas provas da Ana?'},
                {
                    'sender_type': 'assistant',
                    'content': 'Próximas avaliações de Ana Oliveira:\n- Matemática: Avaliação B1 em 10/04/2026.',
                },
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
    )

    assert focus.domain == 'academic'
    assert focus.topic == 'upcoming_assessments'
    assert focus.student_name == 'Ana Oliveira'
    assert focus.subject_name == 'Matematica'
    assert focus.needs_disambiguation is False


def test_resolve_answer_focus_treats_explicit_student_correction_as_same_upcoming_flow() -> None:
    focus = resolve_answer_focus(
        request_message='não, do Lucas',
        actor=_actor(),
        conversation_context={
            'recent_messages': [
                {'sender_type': 'user', 'content': 'quais as próximas provas da Ana?'},
                {
                    'sender_type': 'assistant',
                    'content': 'Próximas avaliações de Ana Oliveira:\n- Matemática: Avaliação B1 em 10/04/2026.',
                },
                {'sender_type': 'user', 'content': 'e a próxima de matemática?'},
                {
                    'sender_type': 'assistant',
                    'content': 'Próximas avaliações de Ana Oliveira:\n- Matemática: Avaliação B1 em 10/04/2026.',
                },
            ],
            'recent_tool_calls': [
                {
                    'tool_name': 'orchestration.trace',
                    'request_payload': {
                        'slot_memory': {
                            'active_task': 'academic:upcoming',
                            'academic_focus_kind': 'upcoming',
                            'academic_student_name': 'Ana Oliveira',
                            'active_subject': 'Matematica',
                        }
                    },
                }
            ],
        },
    )

    assert focus.domain == 'academic'
    assert focus.topic == 'upcoming_assessments'
    assert focus.student_name == 'Lucas Oliveira'
    assert focus.subject_name == 'Matematica'
    assert focus.needs_disambiguation is False


def test_resolve_answer_focus_does_not_inherit_single_student_memory_for_family_comparison() -> None:
    focus = resolve_answer_focus(
        request_message='e agora quem dos dois está mais perto da média mínima?',
        actor=_actor(),
        conversation_context={
            'recent_messages': [
                {
                    'sender_type': 'assistant',
                    'content': 'Próximas avaliações de Lucas Oliveira:\n- Matemática: Avaliação B1 em 10/04/2026.',
                },
                {'sender_type': 'user', 'content': 'não, do Lucas'},
                {
                    'sender_type': 'assistant',
                    'content': 'Próximas avaliações de Ana Oliveira:\n- Matemática: Avaliação B1 em 10/04/2026.',
                },
                {'sender_type': 'user', 'content': 'e a próxima de matemática?'},
            ],
            'recent_tool_calls': [
                {
                    'tool_name': 'orchestration.trace',
                    'request_payload': {
                        'slot_memory': {
                            'active_task': 'academic:upcoming_assessments',
                            'academic_student_name': 'Lucas Oliveira',
                            'active_subject': 'Matematica',
                        }
                    },
                }
            ],
        },
    )

    assert focus.domain == 'academic'
    assert focus.topic == 'grades'
    assert focus.asks_family_aggregate is True
    assert focus.student_name is None
    assert focus.subject_name is None


def test_resolve_answer_focus_does_not_leak_public_pricing_into_finance_followup() -> None:
    focus = resolve_answer_focus(
        request_message='e o financeiro do lucas como está?',
        actor=_actor(),
        conversation_context={
            'recent_tool_calls': [
                {
                    'tool_name': 'orchestration.trace',
                    'request_payload': {
                        'slot_memory': {
                            'active_task': 'public:pricing',
                            'public_pricing_segment': 'Ensino Medio',
                            'public_pricing_quantity': '20',
                        }
                    },
                }
            ],
        },
    )

    assert focus.domain == 'finance'
    assert focus.topic == 'student_finance'
    assert focus.student_name == 'Lucas Oliveira'
    assert focus.public_pricing_quantity is None


def test_resolve_answer_focus_does_not_inherit_quantity_for_direct_public_pricing_question() -> None:
    focus = resolve_answer_focus(
        request_message='Qual a mensalidade do ensino medio?',
        actor=_actor(),
        conversation_context={
            'recent_messages': [
                {'sender_type': 'user', 'content': 'Quanto seria a matricula para 20 filhos?'},
                {'sender_type': 'assistant', 'content': 'A simulação fica 20 x R$ 350,00 = R$ 7.000,00.'},
                {'sender_type': 'assistant', 'content': 'Calendário 2026 disponível.'},
            ],
            'recent_tool_calls': [
                {
                    'tool_name': 'orchestration.trace',
                    'request_payload': {
                        'slot_memory': {
                            'active_task': 'public:pricing',
                            'public_pricing_segment': 'Ensino Medio',
                            'public_pricing_quantity': '20',
                            'public_pricing_price_kind': 'enrollment_fee',
                        }
                    },
                }
            ],
        },
    )

    assert focus.domain == 'public'
    assert focus.topic == 'pricing'
    assert focus.public_pricing_segment == 'Ensino Medio'
    assert focus.public_pricing_price_kind == 'monthly_amount'
    assert focus.public_pricing_quantity is None


def test_resolve_answer_focus_inherits_public_pricing_segment_for_direct_projection_followup() -> None:
    focus = resolve_answer_focus(
        request_message='Quanto seria a matricula para 20 filhos?',
        actor=_actor(),
        conversation_context={
            'recent_tool_calls': [
                {
                    'tool_name': 'orchestration.trace',
                    'request_payload': {
                        'slot_memory': {
                            'active_task': 'public:pricing',
                            'public_pricing_segment': 'Ensino Medio',
                            'public_pricing_grade_year': '3o ano',
                            'public_pricing_price_kind': 'monthly_amount',
                        }
                    },
                }
            ],
        },
    )

    assert focus.domain == 'public'
    assert focus.topic == 'pricing'
    assert focus.public_pricing_segment == 'Ensino Medio'
    assert focus.public_pricing_grade_year == '3o ano'
    assert focus.public_pricing_quantity == '20'
    assert focus.public_pricing_price_kind == 'enrollment_fee'


def test_extract_unknown_student_reference_skips_admin_finance_combo_prompt() -> None:
    prompt = (
        'De forma bem objetiva, quero um quadro unico de documentacao e financeiro '
        'para saber se alguma pendencia esta bloqueando atendimento.'
    )

    assert _extract_unknown_student_reference(_actor(), prompt) is None
