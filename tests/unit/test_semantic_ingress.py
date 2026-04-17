from __future__ import annotations

from types import SimpleNamespace

from ai_orchestrator.models import (
    AccessTier,
    IntentClassification,
    OrchestrationMode,
    OrchestrationPreview,
    QueryDomain,
    RetrievalBackend,
)
from ai_orchestrator.semantic_ingress_runtime import (
    apply_semantic_ingress_preview,
    apply_turn_frame_preview,
)
from eduassist_semantic_ingress import (
    build_capability_candidates,
    build_turn_frame_hint,
    derive_focus_frame,
    effective_turn_frame_authenticated,
    resolve_turn_frame_with_provider,
)
from eduassist_semantic_ingress.runtime import (
    _validated_conversation_act,
    IngressSemanticPlan,
    is_terminal_ingress_act,
    looks_like_high_confidence_public_school_faq,
    looks_like_language_preference_feedback,
    looks_like_opaque_short_input,
    looks_like_scope_boundary_candidate,
    looks_like_school_scope_message,
    normalize_ingress_text,
    resolve_semantic_ingress_with_provider,
    should_run_semantic_ingress_classifier,
)


def _preview() -> OrchestrationPreview:
    return OrchestrationPreview(
        mode=OrchestrationMode.structured_tool,
        classification=IntentClassification(
            domain=QueryDomain.institution,
            access_tier=AccessTier.public,
            confidence=0.62,
            reason="local_preview",
        ),
        retrieval_backend=RetrievalBackend.none,
        selected_tools=[],
        graph_path=["test"],
        reason="local_preview",
        output_contract="teste",
    )


def test_normalize_ingress_text_collapses_accents_and_noise() -> None:
    assert normalize_ingress_text("  Boa   Madrugá!!  ") == "boa madruga"


def test_normalize_ingress_text_preserves_non_latin_letters() -> None:
    assert normalize_ingress_text("Привет") == "привет"


def test_normalize_ingress_text_preserves_non_latin_marks() -> None:
    assert normalize_ingress_text("नमस्ते") == "नमस्ते"


def test_should_run_semantic_ingress_classifier_accepts_informal_greeting() -> None:
    assert (
        should_run_semantic_ingress_classifier(
            message="oooie, boa madruga",
            current_domain="institution",
            current_access_tier="public",
            current_mode="structured_tool",
        )
        is True
    )


def test_should_run_semantic_ingress_classifier_accepts_short_non_latin_message() -> None:
    assert (
        should_run_semantic_ingress_classifier(
            message="Привет",
            current_domain="institution",
            current_access_tier="authenticated",
            current_mode="structured_tool",
        )
        is True
    )


def test_should_run_semantic_ingress_classifier_accepts_language_preference_even_when_preview_looks_academic() -> None:
    assert (
        should_run_semantic_ingress_classifier(
            message="Por que admissions ta em ingles",
            current_domain="academic",
            current_access_tier="authenticated",
            current_mode="structured_tool",
        )
        is True
    )


def test_should_run_semantic_ingress_classifier_rejects_real_content_query() -> None:
    assert (
        should_run_semantic_ingress_classifier(
            message="bom comportamento",
            current_domain="institution",
            current_access_tier="public",
            current_mode="structured_tool",
        )
        is False
    )


def test_looks_like_language_preference_feedback_detects_metalinguistic_complaint() -> None:
    assert looks_like_language_preference_feedback("Quero que so fale portugues") is True
    assert looks_like_language_preference_feedback("Por que admissions ta em ingles") is True


def test_looks_like_language_preference_feedback_rejects_real_subject_query() -> None:
    assert looks_like_language_preference_feedback("qual a nota de ingles do Lucas?") is False


def test_looks_like_opaque_short_input_detects_low_signal_token() -> None:
    assert looks_like_opaque_short_input("rai") is True
    assert looks_like_opaque_short_input("hdirlff") is True


def test_looks_like_opaque_short_input_rejects_known_greeting_and_content() -> None:
    assert looks_like_opaque_short_input("oi") is False
    assert looks_like_opaque_short_input("bom dia") is False
    assert looks_like_opaque_short_input("notas") is False


def test_looks_like_school_scope_message_detects_school_policy_query() -> None:
    assert looks_like_school_scope_message("posso fumar maconha nessa escola?") is True
    assert looks_like_school_scope_message("qual a mensalidade da escola?") is True
    assert looks_like_school_scope_message("qual o melhor filme do ano?") is False


def test_looks_like_school_scope_message_detects_public_school_information_queries() -> None:
    assert looks_like_school_scope_message("Qual o horario da biblioteca?") is True
    assert looks_like_school_scope_message("qual contato do diretor?") is True
    assert looks_like_school_scope_message("Qual o proximo vencimento?") is True
    assert looks_like_school_scope_message("Quais os feriados desse ano?") is True
    assert looks_like_school_scope_message("o que é bncc?") is True
    assert looks_like_school_scope_message("qual o conteúdo ensinado em biologia?") is True
    assert looks_like_school_scope_message("é um colégio confessional?") is True
    assert looks_like_school_scope_message(
        "Quais eventos publicos para familias e responsaveis aparecem nesta base agora?"
    ) is True


def test_looks_like_high_confidence_public_school_faq_detects_public_faq_families() -> None:
    assert looks_like_high_confidence_public_school_faq("tem biblioteca nessa escola?") is True
    assert looks_like_high_confidence_public_school_faq("qual valor da matricula?") is True
    assert looks_like_high_confidence_public_school_faq("quando iniciam as aulas?") is True
    assert looks_like_high_confidence_public_school_faq("que horas começa a aula de manhã?") is True
    assert looks_like_high_confidence_public_school_faq("qual horário da última aula?") is True
    assert looks_like_high_confidence_public_school_faq("tem aula de madrugada?") is True
    assert looks_like_high_confidence_public_school_faq("quais documentos preciso para matricula?") is True
    assert looks_like_high_confidence_public_school_faq("o que é bncc?") is True
    assert looks_like_high_confidence_public_school_faq("qual o conteúdo ensinado em biologia?") is True
    assert looks_like_high_confidence_public_school_faq("é um colégio confessional?") is True
    assert looks_like_high_confidence_public_school_faq(
        "Quais eventos publicos para familias e responsaveis aparecem nesta base agora?"
    ) is True
    assert looks_like_high_confidence_public_school_faq("qual o proximo vencimento?") is False
    assert (
        looks_like_high_confidence_public_school_faq(
            "Explique a minha situacao financeira como se eu fosse leigo, separando mensalidade, taxa, atraso e desconto."
        )
        is False
    )


def test_looks_like_scope_boundary_candidate_detects_out_of_scope_question() -> None:
    assert looks_like_scope_boundary_candidate("Qual o melhor filme do ano?") is True
    assert looks_like_scope_boundary_candidate("Como faco lasanha?") is True
    assert looks_like_scope_boundary_candidate("Me ajuda a escolher um filme para o fim de semana.") is True
    assert (
        looks_like_scope_boundary_candidate(
            "Pensando no caso pratico, fora do tema escolar, qual filme voce acha que mais vale a pena ver agora?"
        )
        is True
    )
    assert looks_like_scope_boundary_candidate("Posso fumar maconha nessa escola?") is False
    assert looks_like_scope_boundary_candidate("Qual o horario da biblioteca?") is False
    assert looks_like_scope_boundary_candidate("qual contato do diretor?") is False
    assert looks_like_scope_boundary_candidate("Quais os feriados desse ano?") is False
    assert looks_like_scope_boundary_candidate("que horas começa a aula de manhã?") is False
    assert looks_like_scope_boundary_candidate("qual horário da última aula?") is False
    assert looks_like_scope_boundary_candidate("tem aula de madrugada?") is False
    assert looks_like_scope_boundary_candidate("o que é bncc?") is False
    assert looks_like_scope_boundary_candidate("qual o conteúdo ensinado em biologia?") is False
    assert looks_like_scope_boundary_candidate("é um colégio confessional?") is False
    assert (
        looks_like_scope_boundary_candidate(
            "Quais eventos publicos para familias e responsaveis aparecem nesta base agora?"
        )
        is False
    )


def test_build_turn_frame_hint_does_not_mark_calendar_week_bundle_as_scope_boundary() -> None:
    frame = build_turn_frame_hint(
        message="Quais eventos publicos para familias e responsaveis aparecem nesta base agora?",
        conversation_context=None,
        preview=None,
        authenticated=False,
    )

    assert frame is None or frame.conversation_act != "scope_boundary"


def test_build_turn_frame_hint_maps_public_holiday_query_to_calendar_events() -> None:
    frame = build_turn_frame_hint(
        message="Quais os feriados desse ano?",
        conversation_context=None,
        preview=None,
        authenticated=False,
    )

    assert frame is not None
    assert frame.capability_id == "public.calendar.events"
    assert frame.domain == "calendar"
    assert frame.public_conversation_act == "calendar_events"


def test_build_capability_candidates_prefers_public_schedule_for_morning_class_query() -> None:
    candidates = build_capability_candidates(
        message="Que horas começa a aula de manhã?",
        conversation_context=None,
        authenticated=True,
    )

    assert candidates
    assert candidates[0].capability_id == "public.schedule.class_start_time"


def test_build_capability_candidates_prefers_public_end_time_for_last_class_query() -> None:
    candidates = build_capability_candidates(
        message="Qual horário da última aula?",
        conversation_context=None,
        authenticated=False,
    )

    assert candidates
    assert candidates[0].capability_id == "public.schedule.class_end_time"


def test_build_capability_candidates_preserves_library_closing_attribute() -> None:
    candidates = build_capability_candidates(
        message="Qual horário de fechamento da biblioteca?",
        conversation_context=None,
        authenticated=False,
    )

    assert candidates
    assert candidates[0].capability_id == "public.facilities.library.hours"
    assert candidates[0].requested_attribute == "close_time"


def test_build_capability_candidates_keeps_grade_followup_with_recent_student_context() -> None:
    candidates = build_capability_candidates(
        message="agora foque só em matemática",
        conversation_context={
            "recent_messages": [
                {"sender_type": "user", "content": "quero um resumo acadêmico do Lucas Oliveira"},
                {"sender_type": "assistant", "content": "Resumo acadêmico de Lucas Oliveira: Matemática 6,2; História 7,4."},
            ]
        },
        authenticated=True,
    )

    assert candidates
    assert candidates[0].capability_id == "protected.academic.grades"


def test_build_turn_frame_hint_marks_external_city_library_query_as_scope_boundary() -> None:
    frame = build_turn_frame_hint(
        message="Qual horário de fechamento da biblioteca pública da cidade?",
        conversation_context=None,
        preview=None,
        authenticated=False,
    )

    assert frame is not None
    assert frame.conversation_act == "scope_boundary"
    assert frame.reason == "external_public_facility_turn_hint"


def test_build_turn_frame_hint_keeps_external_city_library_boundary_even_with_school_name_contrast() -> None:
    frame = build_turn_frame_hint(
        message="Fora do Colegio Horizonte, qual e o horario da biblioteca publica da cidade?",
        conversation_context=None,
        preview=None,
        authenticated=False,
    )

    assert frame is not None
    assert frame.conversation_act == "scope_boundary"
    assert frame.reason == "external_public_facility_turn_hint"


def test_build_capability_candidates_prefers_public_curriculum_for_bncc_query() -> None:
    candidates = build_capability_candidates(
        message="O que é BNCC?",
        conversation_context=None,
        authenticated=False,
    )

    assert candidates
    assert candidates[0].capability_id == "public.curriculum.overview"


def test_derive_focus_frame_uses_recent_public_capability_for_followup() -> None:
    focus = derive_focus_frame(
        conversation_context={
            "messages": [
                {"role": "user", "content": "Qual o horario da biblioteca?"},
                {"role": "assistant", "content": "A biblioteca funciona das 7h30 as 18h00."},
            ]
        },
        authenticated=False,
    )

    assert focus.capability_id == "public.facilities.library.hours"
    assert focus.scope == "public"


def test_derive_focus_frame_prefers_recent_trace_slot_memory_when_available() -> None:
    focus = derive_focus_frame(
        conversation_context={
            "recent_messages": [
                {"sender_type": "user", "content": "E quando fecha?"},
                {"sender_type": "assistant", "content": "A biblioteca funciona em horario comercial."},
            ],
            "recent_tool_calls": [
                {
                    "tool_name": "orchestration.trace",
                    "request_payload": {
                        "slot_memory": {
                            "active_task": "public:operating_hours",
                            "public_entity": "library",
                            "public_attribute": "close_time",
                            "pending_question_type": "follow_up",
                        }
                    },
                }
            ],
        },
        authenticated=False,
    )

    assert focus.source == "recent_trace"
    assert focus.scope == "public"
    assert focus.capability_id == "public.facilities.library.hours"
    assert focus.active_entity == "library"
    assert focus.active_attribute == "close_time"


def test_build_turn_frame_hint_carries_recent_finance_focus_for_next_due_followup() -> None:
    frame = build_turn_frame_hint(
        message="Qual o proximo vencimento?",
        conversation_context={
            "messages": [
                {"role": "user", "content": "Quero ver meu financeiro"},
                {"role": "assistant", "content": "Resumo financeiro da familia."},
            ]
        },
        preview={"mode": "structured_tool", "domain": "finance", "access_tier": "authenticated"},
        authenticated=True,
    )

    assert frame is not None
    assert frame.capability_id == "protected.finance.next_due"
    assert frame.follow_up_of == "protected.finance.summary"


def test_build_turn_frame_hint_detects_protected_administrative_status() -> None:
    frame = build_turn_frame_hint(
        message="Quais pendencias documentais da Ana ainda pedem acao e qual e o proximo passo recomendado?",
        conversation_context=None,
        preview={"mode": "structured_tool", "domain": "institution", "access_tier": "authenticated"},
        authenticated=True,
    )

    assert frame is not None
    assert frame.capability_id == "protected.administrative.status"
    assert frame.domain == "institution"
    assert frame.access_tier == "authenticated"
    assert frame.scope == "protected"


def test_build_turn_frame_hint_detects_protected_access_scope() -> None:
    frame = build_turn_frame_hint(
        message="O que eu consigo consultar aqui no Telegram? Quero meu escopo exato entre academico e financeiro.",
        conversation_context=None,
        preview={"mode": "structured_tool", "domain": "institution", "access_tier": "authenticated"},
        authenticated=True,
    )

    assert frame is not None
    assert frame.capability_id == "protected.account.access_scope"
    assert frame.scope == "protected"


def test_derive_focus_frame_prefers_recent_teacher_schedule_trace() -> None:
    focus = derive_focus_frame(
        conversation_context={
            "recent_messages": [
                {"sender_type": "user", "content": "Sou professor e quero um panorama das minhas turmas e disciplinas deste ano."},
                {"sender_type": "assistant", "content": "Resumo docente de Fernando Azevedo."},
            ],
            "recent_tool_calls": [
                {
                    "tool_name": "orchestration.trace",
                    "request_payload": {
                        "selected_tools": ["get_teacher_schedule"],
                        "slot_memory": {
                            "active_task": "academic:teacher_schedule",
                            "pending_question_type": "follow_up",
                        },
                    },
                }
            ],
        },
        authenticated=True,
    )

    assert focus.capability_id == "protected.teacher.schedule"
    assert focus.scope == "protected"


def test_build_turn_frame_hint_carries_teacher_focus_for_segment_followup() -> None:
    frame = build_turn_frame_hint(
        message="Mantendo o contexto anterior, quero apenas a parte do ensino medio.",
        conversation_context={
            "recent_messages": [
                {"sender_type": "user", "content": "Sou professor e quero um panorama das minhas turmas e disciplinas deste ano."},
                {"sender_type": "assistant", "content": "Resumo docente de Fernando Azevedo."},
            ],
            "recent_tool_calls": [
                {
                    "tool_name": "orchestration.trace",
                    "request_payload": {
                        "selected_tools": ["get_teacher_schedule"],
                        "slot_memory": {
                            "active_task": "academic:teacher_schedule",
                            "pending_question_type": "follow_up",
                        },
                    },
                }
            ],
        },
        preview={"mode": "structured_tool", "domain": "academic", "access_tier": "authenticated"},
        authenticated=True,
    )

    assert frame is not None
    assert frame.capability_id == "protected.teacher.schedule"
    assert frame.follow_up_of == "protected.teacher.schedule"


def test_build_capability_candidates_does_not_let_teacher_followup_alias_override_restricted_doc_prompt() -> None:
    candidates = build_capability_candidates(
        message="No manual interno de hospedagem internacional do ensino medio, qual e o protocolo valido hoje?",
        conversation_context={
            "recent_messages": [
                {"sender_type": "user", "content": "Sou professor e quero um panorama das minhas turmas e disciplinas deste ano."},
                {"sender_type": "assistant", "content": "Resumo docente de Fernando Azevedo."},
            ],
            "recent_tool_calls": [
                {
                    "tool_name": "orchestration.trace",
                    "request_payload": {
                        "selected_tools": ["get_teacher_schedule"],
                        "slot_memory": {
                            "active_task": "academic:teacher_schedule",
                            "pending_question_type": "follow_up",
                        },
                    },
                }
            ],
        },
        authenticated=True,
    )

    assert candidates
    assert candidates[0].capability_id == "protected.documents.restricted_lookup"


def test_build_turn_frame_hint_preserves_attendance_focus_for_named_student_followup() -> None:
    frame = build_turn_frame_hint(
        message="Mantendo o contexto, corta para o Lucas e resume qual e o risco mais concreto dele em frequencia.",
        conversation_context={
            "recent_messages": [
                {
                    "sender_type": "assistant",
                    "content": (
                        "Panorama de faltas e frequencia das contas vinculadas:\n"
                        "- Lucas Oliveira: 6 faltas e 7 atrasos.\n"
                        "- Ana Oliveira: 2 faltas e 1 atraso.\n"
                        "Quem exige maior atencao agora: Lucas Oliveira."
                    ),
                }
            ],
            "recent_tool_calls": [
                {
                    "tool_name": "orchestration.trace",
                    "request_payload": {
                        "selected_tools": ["get_student_attendance", "get_student_attendance_timeline"],
                        "slot_memory": {
                            "active_task": "academic:attendance",
                            "academic_student_name": "Lucas Oliveira",
                            "pending_question_type": "attribute_query",
                        },
                    },
                }
            ],
        },
        preview={"mode": "structured_tool", "domain": "academic", "access_tier": "authenticated"},
        authenticated=True,
    )

    assert frame is not None
    assert frame.capability_id == "protected.academic.attendance"
    assert frame.follow_up_of == "protected.academic.attendance"


def test_build_turn_frame_hint_backfills_family_comparison_from_recent_messages_when_trace_is_generic() -> None:
    frame = build_turn_frame_hint(
        message="Pensando no caso pratico, agora quero apenas a Ana: em quais materias ela aparece mais exposta?",
        conversation_context={
            "recent_messages": [
                {
                    "sender_type": "user",
                    "content": "Sem me dar tabela, qual dos meus filhos esta academicamente pior hoje e em qual disciplina isso fica mais claro?",
                },
                {
                    "sender_type": "assistant",
                    "content": (
                        "Panorama academico das contas vinculadas:\n"
                        "- Lucas Oliveira: Fisica 5,9; Matematica 7,4\n"
                        "- Ana Oliveira: Historia 6,8; Portugues 7,1\n"
                        "Quem hoje exige maior atencao academica e Lucas Oliveira, principalmente em Fisica."
                    ),
                },
            ],
            "recent_tool_calls": [
                {
                    "tool_name": "orchestration.trace",
                    "request_payload": {
                        "slot_memory": {
                            "active_task": "academic:family_panorama",
                            "pending_question_type": "follow_up",
                        },
                    },
                }
            ],
        },
        preview={"mode": "structured_tool", "domain": "academic", "access_tier": "authenticated"},
        authenticated=True,
    )

    assert frame is not None
    assert frame.capability_id == "protected.academic.family_comparison"
    assert frame.scope == "protected"
    assert frame.follow_up_of == "protected.academic.family_comparison"


def test_derive_focus_frame_recovers_family_comparison_from_recent_assistant_summary() -> None:
    focus = derive_focus_frame(
        conversation_context={
            "recent_messages": [
                {
                    "sender_type": "assistant",
                    "content": (
                        "Panorama academico das contas vinculadas:\n"
                        "- Lucas Oliveira: Biologia 7,9; Educacao Fisica 6,5; Filosofia 7,1; Fisica 5,9\n"
                        "- Ana Oliveira: Biologia 8,0; Educacao Fisica 7,0; Filosofia 7,5; Fisica 6,4\n"
                        "Quem hoje exige maior atencao academica e Lucas Oliveira, principalmente em Fisica."
                    ),
                }
            ]
        },
        authenticated=True,
    )

    assert focus.capability_id == "protected.academic.family_comparison"
    assert focus.domain == "academic"
    assert focus.scope == "protected"


def test_build_turn_frame_hint_keeps_protected_admin_query_as_capability_not_scope_boundary() -> None:
    frame = build_turn_frame_hint(
        message="Pensando no caso pratico, no cadastro da Ana, quais pendencias administrativas continuam abertas e que acao vem agora?",
        conversation_context=None,
        preview={"mode": "structured_tool", "domain": "institution", "access_tier": "authenticated"},
        authenticated=True,
    )

    assert frame is not None
    assert frame.capability_id == "protected.administrative.status"
    assert frame.scope == "protected"
    assert frame.conversation_act == "none"


def test_build_turn_frame_hint_redirects_unauthenticated_grade_query_to_auth_guidance() -> None:
    frame = build_turn_frame_hint(
        message="Nao estou autenticado e mesmo assim quero consultar meu boletim aqui pelo bot.",
        conversation_context=None,
        preview={"mode": "clarify", "domain": "academic", "access_tier": "public"},
        authenticated=False,
    )

    assert frame is not None
    assert frame.scope == "public"
    assert frame.public_conversation_act == "auth_guidance"
    assert frame.reason.startswith("protected_requires_auth:")


def test_effective_turn_frame_authenticated_uses_actor_context_without_explicit_auth_downgrade() -> None:
    assert (
        effective_turn_frame_authenticated(
            authenticated=False,
            actor_present=True,
            message="Pensando no caso pratico, no cadastro da Ana, quais pendencias administrativas continuam abertas?",
        )
        is True
    )
    assert (
        effective_turn_frame_authenticated(
            authenticated=False,
            actor_present=True,
            message="Nao estou autenticado e mesmo assim quero consultar meu boletim aqui pelo bot.",
        )
        is False
    )


def test_apply_turn_frame_preview_maps_protected_admin_tools() -> None:
    preview = _preview().model_copy(
        update={
            "classification": IntentClassification(
                domain=QueryDomain.unknown,
                access_tier=AccessTier.public,
                confidence=0.4,
                reason="before",
            ),
            "selected_tools": ["get_financial_summary"],
        }
    )

    updated = apply_turn_frame_preview(
        preview=preview,
        turn_frame=SimpleNamespace(
            capability_id="protected.administrative.status",
            conversation_act="protected_answer",
            scope="protected",
            access_tier="authenticated",
            domain="institution",
            confidence=0.92,
            needs_clarification=False,
            public_conversation_act=None,
            follow_up_of=None,
        ),
        stack_name="python_functions",
    )

    assert updated.classification.access_tier is AccessTier.authenticated
    assert "get_student_administrative_status" in updated.selected_tools
    assert "get_administrative_status" in updated.selected_tools


def test_apply_turn_frame_preview_maps_access_scope_tools() -> None:
    updated = apply_turn_frame_preview(
        preview=_preview(),
        turn_frame=SimpleNamespace(
            capability_id="protected.account.access_scope",
            conversation_act="none",
            scope="protected",
            access_tier="authenticated",
            domain="institution",
            confidence=0.93,
            needs_clarification=False,
            public_conversation_act=None,
            follow_up_of=None,
        ),
        stack_name="python_functions",
    )

    assert updated.classification.domain is QueryDomain.institution
    assert updated.classification.access_tier is AccessTier.authenticated
    assert updated.selected_tools == ["get_actor_identity_context"]


def test_apply_turn_frame_preview_maps_teacher_schedule_tools() -> None:
    updated = apply_turn_frame_preview(
        preview=_preview(),
        turn_frame=SimpleNamespace(
            capability_id="protected.teacher.schedule",
            conversation_act="none",
            scope="protected",
            access_tier="authenticated",
            domain="academic",
            confidence=0.93,
            needs_clarification=False,
            public_conversation_act=None,
            follow_up_of="protected.teacher.schedule",
        ),
        stack_name="python_functions",
    )

    assert updated.classification.domain is QueryDomain.academic
    assert updated.classification.access_tier is AccessTier.authenticated
    assert updated.selected_tools == ["get_teacher_schedule"]


def test_resolve_turn_frame_with_provider_keeps_deterministic_high_confidence_path_without_llm(monkeypatch) -> None:
    async def fake_router(**_kwargs) -> str | None:
        raise AssertionError("router llm should not run for high-confidence deterministic turn")

    monkeypatch.setattr("eduassist_semantic_ingress.turn_router._turn_router_text_call", fake_router)

    import asyncio

    frame = asyncio.run(
        resolve_turn_frame_with_provider(
            settings=SimpleNamespace(),
            stack_label="python_functions",
            request_message="Qual o horario da biblioteca?",
            conversation_context=None,
            preview={"mode": "structured_tool", "domain": "institution", "access_tier": "public"},
            authenticated=False,
        )
    )

    assert frame is not None
    assert frame.capability_id == "public.facilities.library.hours"


def test_resolve_turn_frame_with_provider_uses_llm_to_disambiguate_candidates(monkeypatch) -> None:
    async def fake_router(**_kwargs) -> str:
        return (
            '{"capability_id":"public.facilities.library.hours","confidence_bucket":"high",'
            '"needs_clarification":false,"follow_up_of":"public.facilities.library.hours","reason":"followup biblioteca"}'
        )

    monkeypatch.setattr("eduassist_semantic_ingress.turn_router._turn_router_text_call", fake_router)

    import asyncio

    frame = asyncio.run(
        resolve_turn_frame_with_provider(
            settings=SimpleNamespace(),
            stack_label="specialist_supervisor",
            request_message="E que horas fecha?",
            conversation_context={
                "messages": [
                    {"role": "user", "content": "Qual o horario da biblioteca?"},
                    {"role": "assistant", "content": "A biblioteca funciona das 7h30 as 18h00."},
                ]
            },
            preview={"mode": "structured_tool", "domain": "institution", "access_tier": "public"},
            authenticated=False,
        )
    )

    assert frame is not None
    assert frame.capability_id == "public.facilities.library.hours"
    assert frame.follow_up_of == "public.facilities.library.hours"


def test_resolve_semantic_ingress_with_provider_parses_structured_payload(monkeypatch) -> None:
    async def fake_text_call(**_kwargs) -> str:
        return (
            '{"conversation_act":"greeting","use_conversation_context":false,'
            '"confidence_bucket":"high","reason":"saudacao informal"}'
        )

    monkeypatch.setattr("eduassist_semantic_ingress.runtime._text_call", fake_text_call)

    import asyncio

    plan = asyncio.run(
        resolve_semantic_ingress_with_provider(
            settings=SimpleNamespace(),
            stack_label="python_functions",
            request_message="boa madruga",
            conversation_context=None,
            preview={"mode": "structured_tool", "domain": "institution", "access_tier": "public"},
        )
    )

    assert plan is not None
    assert plan.conversation_act == "greeting"
    assert plan.confidence_bucket == "high"
    assert plan.terminal_fast_path is True


def test_resolve_semantic_ingress_with_provider_coerces_language_preference_when_model_returns_input_clarification(
    monkeypatch,
) -> None:
    async def fake_text_call(**_kwargs) -> str:
        return (
            '{"conversation_act":"input_clarification","use_conversation_context":false,'
            '"confidence_bucket":"low","reason":"mensagem curta"}'
        )

    monkeypatch.setattr("eduassist_semantic_ingress.runtime._text_call", fake_text_call)

    import asyncio

    plan = asyncio.run(
        resolve_semantic_ingress_with_provider(
            settings=SimpleNamespace(),
            stack_label="langgraph",
            request_message="Por que admissions ta em ingles",
            conversation_context=None,
            preview={"mode": "structured_tool", "domain": "academic", "access_tier": "public"},
        )
    )

    assert plan is not None
    assert plan.conversation_act == "language_preference"
    assert plan.confidence_bucket == "high"
    assert "metalingu" in plan.reason


def test_resolve_semantic_ingress_with_provider_falls_back_to_input_clarification_for_opaque_short_input(
    monkeypatch,
) -> None:
    async def fake_text_call(**_kwargs) -> str | None:
        return None

    monkeypatch.setattr("eduassist_semantic_ingress.runtime._text_call", fake_text_call)

    import asyncio

    plan = asyncio.run(
        resolve_semantic_ingress_with_provider(
            settings=SimpleNamespace(),
            stack_label="python_functions",
            request_message="rai",
            conversation_context=None,
            preview={"mode": "structured_tool", "domain": "academic", "access_tier": "authenticated"},
        )
    )

    assert plan is not None
    assert plan.conversation_act == "input_clarification"
    assert plan.reason == "opaque_short_input_fallback"


def test_resolve_semantic_ingress_with_provider_falls_back_to_input_clarification_for_public_opaque_short_input(
    monkeypatch,
) -> None:
    async def fake_text_call(**_kwargs) -> str | None:
        return None

    monkeypatch.setattr("eduassist_semantic_ingress.runtime._text_call", fake_text_call)

    import asyncio

    plan = asyncio.run(
        resolve_semantic_ingress_with_provider(
            settings=SimpleNamespace(),
            stack_label="python_functions",
            request_message="rai",
            conversation_context=None,
            preview={"mode": "structured_tool", "domain": "institution", "access_tier": "public"},
        )
    )

    assert plan is not None
    assert plan.conversation_act == "input_clarification"
    assert plan.reason == "opaque_short_input_fallback"


def test_resolve_semantic_ingress_with_provider_falls_back_to_scope_boundary_for_out_of_scope_question(
    monkeypatch,
) -> None:
    async def fake_text_call(**_kwargs) -> str | None:
        return None

    monkeypatch.setattr("eduassist_semantic_ingress.runtime._text_call", fake_text_call)

    import asyncio

    plan = asyncio.run(
        resolve_semantic_ingress_with_provider(
            settings=SimpleNamespace(),
            stack_label="python_functions",
            request_message="Qual o melhor filme do ano?",
            conversation_context=None,
            preview={"mode": "structured_tool", "domain": "unknown", "access_tier": "authenticated"},
        )
    )

    assert plan is not None
    assert plan.conversation_act == "scope_boundary"
    assert plan.reason == "scope_boundary_fallback"


def test_validated_conversation_act_rejects_scope_boundary_for_school_scope_message() -> None:
    assert _validated_conversation_act(
        request_message="Posso fumar maconha nessa escola?",
        act="scope_boundary",
    ) == "none"
    assert _validated_conversation_act(
        request_message="Qual o horario da biblioteca?",
        act="scope_boundary",
    ) == "none"
    assert _validated_conversation_act(
        request_message="qual contato do diretor?",
        act="scope_boundary",
    ) == "none"


def test_should_run_semantic_ingress_classifier_accepts_opaque_short_input_even_when_preview_looks_academic() -> None:
    assert (
        should_run_semantic_ingress_classifier(
            message="rai",
            current_domain="academic",
            current_access_tier="authenticated",
            current_mode="structured_tool",
        )
        is True
    )


def test_should_run_semantic_ingress_classifier_skips_school_scope_content_query() -> None:
    assert (
        should_run_semantic_ingress_classifier(
            message="Posso fumar maconha nessa escola?",
            current_domain="institution",
            current_access_tier="public",
            current_mode="structured_tool",
        )
        is False
    )


def test_terminal_ingress_helper_marks_terminal_acts() -> None:
    assert is_terminal_ingress_act("greeting") is True
    assert is_terminal_ingress_act("assistant_identity") is True
    assert is_terminal_ingress_act("capabilities") is True
    assert is_terminal_ingress_act("auth_guidance") is True
    assert is_terminal_ingress_act("input_clarification") is True
    assert is_terminal_ingress_act("language_preference") is True
    assert is_terminal_ingress_act("scope_boundary") is True
    assert is_terminal_ingress_act("none") is False


def test_apply_semantic_ingress_preview_rewrites_to_public_structured_tool() -> None:
    preview = _preview()
    preview.selected_tools = ["get_administrative_status"]
    preview = apply_semantic_ingress_preview(
        preview=preview,
        plan=IngressSemanticPlan(conversation_act="greeting", reason="saudacao informal"),
        stack_name="python_functions",
    )

    assert preview.mode is OrchestrationMode.structured_tool
    assert preview.classification.domain is QueryDomain.institution
    assert preview.classification.access_tier is AccessTier.public
    assert preview.reason == "python_functions_semantic_ingress:greeting"
    assert "semantic_ingress:greeting" in preview.graph_path
    assert "get_public_school_profile" in preview.selected_tools
    assert "get_administrative_status" not in preview.selected_tools


def test_apply_semantic_ingress_preview_rewrites_unclear_input_to_safe_public_path() -> None:
    preview = _preview()
    preview.selected_tools = ["get_administrative_status"]
    preview = apply_semantic_ingress_preview(
        preview=preview,
        plan=IngressSemanticPlan(conversation_act="input_clarification", reason="idioma incerto"),
        stack_name="python_functions",
    )

    assert preview.reason == "python_functions_semantic_ingress:input_clarification"
    assert "semantic_ingress:input_clarification" in preview.graph_path
    assert "get_public_school_profile" in preview.selected_tools
    assert "get_administrative_status" not in preview.selected_tools


def test_apply_semantic_ingress_preview_rewrites_language_preference_to_safe_public_path() -> None:
    preview = _preview()
    preview.selected_tools = ["get_student_grades"]
    preview = apply_semantic_ingress_preview(
        preview=preview,
        plan=IngressSemanticPlan(conversation_act="language_preference", reason="metalinguagem"),
        stack_name="python_functions",
    )

    assert preview.reason == "python_functions_semantic_ingress:language_preference"
    assert "semantic_ingress:language_preference" in preview.graph_path
    assert "get_public_school_profile" in preview.selected_tools
    assert "get_student_grades" not in preview.selected_tools


def test_apply_semantic_ingress_preview_rewrites_scope_boundary_to_safe_public_path() -> None:
    preview = _preview()
    preview.selected_tools = ["get_administrative_status"]
    preview = apply_semantic_ingress_preview(
        preview=preview,
        plan=IngressSemanticPlan(conversation_act="scope_boundary", reason="fora do escopo"),
        stack_name="python_functions",
    )

    assert preview.reason == "python_functions_semantic_ingress:scope_boundary"
    assert "semantic_ingress:scope_boundary" in preview.graph_path
    assert "get_public_school_profile" in preview.selected_tools
    assert "get_administrative_status" not in preview.selected_tools
