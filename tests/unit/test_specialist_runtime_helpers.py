from __future__ import annotations

import asyncio
from types import SimpleNamespace

from ai_orchestrator_specialist.models import (
    MessageIntentClassification,
    OperationalMemory,
    ResolvedTurnIntent,
    SupervisorAnswerPayload,
)
from ai_orchestrator_specialist.operational_memory_answers import (
    OperationalMemoryDeps,
    _looks_like_meta_repair_question,
    maybe_operational_memory_follow_up_answer,
)
from ai_orchestrator_specialist.fast_path_answers import (
    FastPathDeps,
    _augment_public_followup_message,
    build_fast_path_answer,
)
from ai_orchestrator_specialist.public_query_patterns import (
    _extract_teacher_subject,
    _looks_like_access_scope_query,
    _looks_like_admin_finance_combo_query,
    _looks_like_calendar_week_query,
    _looks_like_conduct_frequency_punctuality_query,
    _looks_like_health_second_call_query,
    _looks_like_public_academic_policy_overview_query,
    _looks_like_public_doc_bundle_request,
    _looks_like_public_teacher_identity_query,
    _looks_like_process_compare_query,
    _looks_like_service_routing_query,
    _looks_like_timeline_lifecycle_query,
    _looks_like_year_three_phases_query,
)
from ai_orchestrator_specialist.restricted_doc_matching import (
    _internal_doc_hit_score,
    _looks_like_internal_document_query,
)
from ai_orchestrator_specialist.restricted_doc_tool_first import maybe_restricted_document_tool_first_answer
from ai_orchestrator_specialist.resolved_intent_answers import (
    ResolvedIntentDeps,
    maybe_academic_grade_fast_path_answer,
    maybe_resolved_intent_answer,
)
from ai_orchestrator_specialist.protected_answer_helpers import compose_academic_risk_answer
from ai_orchestrator_specialist.protected_answer_helpers import looks_like_academic_risk_followup
from ai_orchestrator_specialist.protected_answer_helpers import compose_finance_aggregate_answer
from ai_orchestrator_specialist.protected_answer_helpers import looks_like_family_attendance_aggregate_query
from ai_orchestrator_specialist.protected_answer_helpers import looks_like_family_finance_aggregate_query
from ai_orchestrator_specialist.protected_answer_helpers import resolved_academic_target_name
from ai_orchestrator_specialist.student_context_helpers import StudentContextDeps, student_hint_from_message, unknown_explicit_student_reference
from ai_orchestrator_specialist.public_doc_knowledge import match_public_canonical_lane
from ai_orchestrator_specialist.public_profile_answers import _compose_timeline_bundle_answer
from ai_orchestrator_specialist.public_profile_answers import _compose_service_routing_fast_answer
from ai_orchestrator_specialist.tool_first_protected_answers import (
    ToolFirstProtectedDeps,
    _compose_attendance_primary_alert,
    maybe_tool_first_protected_answer,
)
from ai_orchestrator_specialist.tool_first_workflows import (
    ToolFirstWorkflowDeps,
    maybe_tool_first_workflow_answer,
)
from ai_orchestrator_specialist.support_workflow_helpers import (
    _detect_support_handoff_queue,
    _looks_like_human_handoff_request,
)
from ai_orchestrator_specialist.public_bundle_fast_paths import (
    _preflight_public_doc_bundle_answer,
    _looks_like_family_new_calendar_enrollment_query,
    _looks_like_first_month_risks_query,
    _looks_like_visibility_boundary_query,
)
from ai_orchestrator_specialist.supervisor_run_flow import _persist_and_dump, _provider_metadata


def test_extract_teacher_subject_stops_at_conjunction() -> None:
    assert _extract_teacher_subject('Qual o nome do professor de matematica ou da coordenacao?') == 'matematica'


def test_extract_teacher_subject_stops_at_followup_clause() -> None:
    assert (
        _extract_teacher_subject('Vocês divulgam o nome ou contato direto do professor de matematica? Se nao, para onde a familia deve ir?')
        == 'matematica'
    )


def test_specialist_access_scope_query_detects_linked_students_account_prompt() -> None:
    assert _looks_like_access_scope_query('Quais alunos estao vinculados a esta conta?')


def test_specialist_service_routing_query_detects_bullying_reporting_prompt() -> None:
    assert _looks_like_service_routing_query('Como reporto um bullying?')


def test_specialist_service_routing_query_detects_direct_channels_prompt() -> None:
    assert _looks_like_service_routing_query('Me diga so os canais de bolsas, financeiro e direcao. Seja objetivo.')


def test_specialist_service_routing_query_detects_menu_geral_compression_prompt() -> None:
    assert _looks_like_service_routing_query('Nao me manda menu geral: quais setores e canais realmente resolvem bolsa, financeiro e direcao?')


def test_specialist_service_routing_query_detects_role_comparison_prompt() -> None:
    assert _looks_like_service_routing_query(
        'Qual a diferenca entre falar com secretaria, coordenacao e orientacao educacional?'
    )


def test_specialist_service_routing_fast_answer_accepts_plural_bolsas_wording() -> None:
    profile = {
        "service_catalog": [
            {
                "service_key": "atendimento_admissoes",
                "title": "Atendimento comercial / Admissoes",
                "request_channel": "bot, admissions, whatsapp comercial ou visita guiada",
            },
            {
                "service_key": "financeiro_escolar",
                "title": "Financeiro",
                "request_channel": "bot, financeiro, portal autenticado ou email institucional",
            },
            {
                "service_key": "solicitacao_direcao",
                "title": "Direcao",
                "request_channel": "bot, ouvidoria ou protocolo institucional",
            },
        ],
        "leadership_team": [
            {
                "title": "Diretora geral",
                "name": "Helena Martins",
                "contact_channel": "direcao@colegiohorizonte.edu.br",
            }
        ],
    }

    answer = _compose_service_routing_fast_answer(
        profile,
        "Me diga so os canais de bolsas, financeiro e direcao. Seja objetivo.",
    )

    assert answer is not None
    assert (
        "Atendimento comercial / Admissoes" in answer
        or "Bolsas / admissoes" in answer
    )
    assert "Financeiro" in answer


def test_specialist_service_routing_fast_answer_prioritizes_admissions_for_document_pending() -> None:
    profile = {
        "service_catalog": [
            {
                "service_key": "atendimento_admissoes",
                "title": "Atendimento comercial / Admissoes",
                "request_channel": "bot, admissions, whatsapp comercial ou visita guiada",
            },
            {
                "service_key": "financeiro_escolar",
                "title": "Financeiro",
                "request_channel": "bot, financeiro, portal autenticado ou email institucional",
            },
            {
                "service_key": "solicitacao_direcao",
                "title": "Direcao",
                "request_channel": "bot, ouvidoria ou protocolo institucional",
            },
        ],
        "leadership_team": [
            {
                "title": "Diretora geral",
                "name": "Helena Martins",
                "contact_channel": "direcao@colegiohorizonte.edu.br",
            }
        ],
    }

    answer = _compose_service_routing_fast_answer(
        profile,
        "Se o tema for bolsa com documento pendente, qual desses setores entra primeiro entre bolsas, financeiro e direcao?",
    )

    assert answer is not None
    assert "primeiro setor" in answer.casefold()
    assert "Atendimento comercial / Admissoes".casefold() in answer.casefold()


def test_specialist_service_routing_fast_answer_compact_mode_deduplicates_direcao() -> None:
    profile = {
        "service_catalog": [
            {
                "service_key": "atendimento_admissoes",
                "request_channel": "bot, admissions, whatsapp comercial ou visita guiada",
            },
            {
                "service_key": "financeiro_escolar",
                "request_channel": "bot, financeiro, portal autenticado ou email institucional",
            },
            {
                "service_key": "solicitacao_direcao",
                "request_channel": "protocolo institucional",
            },
        ],
        "leadership_team": [
            {
                "title": "Diretora geral",
                "name": "Helena Martins",
                "contact_channel": "direcao@colegiohorizonte.edu.br",
            }
        ],
    }

    answer = _compose_service_routing_fast_answer(
        profile,
        "Me diga so os canais de bolsas, financeiro e direcao. Agora reduz para uma linha por setor, sem explicar o resto da escola.",
    )

    assert answer is not None
    assert answer.count("Direcao:") <= 1


def test_specialist_service_routing_fast_answer_accepts_menu_geral_prompt() -> None:
    profile = {
        "service_catalog": [
            {
                "service_key": "atendimento_admissoes",
                "request_channel": "bot, admissions, whatsapp comercial ou visita guiada",
            },
            {
                "service_key": "financeiro_escolar",
                "request_channel": "bot, financeiro, portal autenticado ou email institucional",
            },
            {
                "service_key": "solicitacao_direcao",
                "request_channel": "protocolo institucional",
            },
        ],
        "leadership_team": [
            {
                "title": "Diretora geral",
                "name": "Helena Martins",
                "contact_channel": "direcao@colegiohorizonte.edu.br",
            }
        ],
    }

    answer = _compose_service_routing_fast_answer(
        profile,
        "Nao me manda menu geral: quais setores e canais realmente resolvem bolsa, financeiro e direcao?",
    )

    assert answer is not None
    assert "Financeiro" in answer
    assert "Direcao" in answer
    assert "Atendimento comercial / Admissoes" in answer or "Bolsas / admissoes" in answer


def test_specialist_augment_public_followup_message_rewrites_service_routing_compression() -> None:
    deps = SimpleNamespace(normalize_text=lambda value: str(value or "").casefold())
    rewritten = _augment_public_followup_message(
        "Agora reduz para uma linha por setor, sem explicar o resto da escola.",
        ["me diga so os canais de bolsas, financeiro e direcao. seja objetivo."],
        deps=deps,
    )
    assert "canais de bolsas, financeiro e direcao" in rewritten.casefold()


def test_specialist_augment_public_followup_message_rewrites_restricted_public_outings_followup() -> None:
    deps = SimpleNamespace(normalize_text=lambda value: str(value or "").casefold())
    rewritten = _augment_public_followup_message(
        "Entao me diga so o que existe de publico sobre esse tipo de saida ou protocolo.",
        ["voce encontrou alguma orientacao interna sobre excursao de inverno para o 9 ano?"],
        deps=deps,
    )
    assert "saidas pedagogicas" in rewritten.casefold()


def test_specialist_public_teacher_identity_query_accepts_quero_falar_com_professor() -> None:
    assert _looks_like_public_teacher_identity_query('Quero falar com o professor de matemática.')


def test_specialist_conduct_query_detects_exclusion_prompt() -> None:
    assert _looks_like_conduct_frequency_punctuality_query(
        'Que tipo de comportamento pode levar ao desligamento de um aluno?'
    )


def test_specialist_family_attendance_aggregate_query_accepts_two_children_attention_wording() -> None:
    deps = SimpleNamespace(normalize_text=lambda value: str(value or '').casefold())
    assert looks_like_family_attendance_aggregate_query(
        'Faca um resumo de frequencia dos meus dois filhos e destaque quem inspira mais atencao por faltas.',
        deps=deps,
    ) is True


def test_specialist_family_attendance_aggregate_query_accepts_more_attention_wording() -> None:
    deps = SimpleNamespace(normalize_text=lambda value: str(value or '').casefold())
    assert looks_like_family_attendance_aggregate_query(
        'Me mostre a frequencia dos meus dois filhos e diga quem exige mais atenção agora.',
        deps=deps,
    ) is True


def test_specialist_fast_path_answers_library_hours_even_after_visit_context() -> None:
    profile = {
        "school_name": "Colegio Horizonte",
        "feature_catalog": [
            {
                "name": "Biblioteca Aurora",
                "label": "Biblioteca Aurora",
                "note": "de segunda a sexta, das 7h30 as 18h00",
            }
        ],
        "service_catalog": [
            {
                "service_key": "visita_institucional",
                "request_channel": "bot, admissions ou whatsapp comercial",
            }
        ],
    }
    ctx = SimpleNamespace(
        school_profile=profile,
        actor=None,
        request=SimpleNamespace(
            message="qual o horário da biblioteca?",
            user=SimpleNamespace(authenticated=False),
        ),
        conversation_context={
            "recent_messages": [
                {"sender_type": "user", "content": "quero visitar a escola na sexta de manhã"},
            ]
        },
    )
    deps = FastPathDeps(
        normalize_text=lambda value: str(value or "").casefold(),
        normalized_recent_user_messages=lambda context: [
            str(item.get("content") or "").casefold()
            for item in (context or {}).get("recent_messages", [])
            if isinstance(item, dict) and str(item.get("sender_type") or "").casefold() == "user"
        ],
        is_simple_greeting=lambda message: False,
        is_auth_guidance_query=lambda message: False,
        compose_auth_guidance_answer=lambda profile: "",
        linked_students=lambda *args, **kwargs: [],
        compose_authenticated_scope_answer=lambda actor: "",
        is_assistant_identity_query=lambda message: False,
        compose_assistant_identity_answer=lambda profile: "",
        school_name=lambda profile: "Colegio Horizonte",
        safe_excerpt=lambda text, limit=220: str(text or "")[:limit],
        format_brl=lambda value: str(value),
        hypothetical_children_quantity=lambda message: None,
        pricing_projection=lambda *args, **kwargs: {},
        compose_public_bolsas_and_processes=lambda profile: None,
    )

    answer = build_fast_path_answer(ctx, deps)

    assert answer is not None
    assert answer.reason == "specialist_supervisor_fast_path:library_hours"
    assert "biblioteca aurora" in answer.message_text.casefold()


def test_specialist_fast_path_resets_to_public_calendar_after_protected_digression() -> None:
    profile = {
        "school_name": "Colegio Horizonte",
        "public_timeline": [
            {"topic": "school_year_start", "event_date": "2026-02-02", "summary": "Inicio das aulas do Fundamental II e Ensino Medio."},
            {"topic": "family_meeting", "event_date": "2026-03-28", "summary": "Reuniao geral com familias."},
        ],
    }
    ctx = SimpleNamespace(
        school_profile=profile,
        actor=None,
        request=SimpleNamespace(
            message="não, quero só o calendário público",
            user=SimpleNamespace(authenticated=True),
        ),
        conversation_context={
            "recent_messages": [
                {"sender_type": "user", "content": "quando começam as aulas?"},
                {"sender_type": "user", "content": "e as notas da Ana?"},
            ]
        },
    )
    deps = FastPathDeps(
        normalize_text=lambda value: str(value or "").casefold(),
        normalized_recent_user_messages=lambda context: [
            str(item.get("content") or "").casefold()
            for item in (context or {}).get("recent_messages", [])
            if isinstance(item, dict) and str(item.get("sender_type") or "").casefold() == "user"
        ],
        is_simple_greeting=lambda message: False,
        is_auth_guidance_query=lambda message: False,
        compose_auth_guidance_answer=lambda profile: "",
        linked_students=lambda *args, **kwargs: [],
        compose_authenticated_scope_answer=lambda actor: "",
        is_assistant_identity_query=lambda message: False,
        compose_assistant_identity_answer=lambda profile: "",
        school_name=lambda profile: "Colegio Horizonte",
        safe_excerpt=lambda text, limit=220: str(text or "")[:limit],
        format_brl=lambda value: str(value),
        hypothetical_children_quantity=lambda message: None,
        pricing_projection=lambda *args, **kwargs: {},
        compose_public_bolsas_and_processes=lambda profile: None,
    )

    answer = build_fast_path_answer(ctx, deps)

    assert answer is not None
    assert answer.reason == "specialist_supervisor_fast_path:public_calendar_reset"
    lowered = answer.message_text.casefold()
    assert "inicio das aulas" in lowered or "início das aulas" in lowered
    assert any(term in lowered for term in ("matricula", "reuniao", "famili"))


def test_specialist_tool_first_workflow_answers_visit_resume_from_recent_context() -> None:
    async def _workflow_status_payload(ctx, workflow_kind: str):
        assert workflow_kind == "visit_booking"
        return {
            "item": {
                "protocol_code": "VIS-123",
                "linked_ticket_code": "ATD-1",
                "slot_label": "sexta-feira, 14h30",
                "status": "cancelled",
            }
        }

    ctx = SimpleNamespace(
        request=SimpleNamespace(
            message="e se eu quiser retomar depois, por onde volto?",
            user=SimpleNamespace(authenticated=False),
            channel=SimpleNamespace(value="api"),
            telegram_chat_id=None,
        ),
        settings=SimpleNamespace(api_core_url="http://api-core:8000", internal_api_token="token"),
        http_client=object(),
    )
    memory = SimpleNamespace(active_domain="support", active_domains={"support"})
    deps = ToolFirstWorkflowDeps(
        http_post=None,
        strip_none=lambda payload: payload,
        effective_conversation_id=lambda request: "conv-visit",
        create_institutional_request_payload=None,
        create_visit_booking_payload=None,
        workflow_status_payload=_workflow_status_payload,
    )

    answer = asyncio.run(
        maybe_tool_first_workflow_answer(
            ctx,
            normalized="e se eu quiser retomar depois, por onde volto?",
            profile={},
            preview_mode="structured_tool",
            memory=memory,
            deps=deps,
        )
    )

    assert answer is not None
    assert answer.reason == "specialist_supervisor_tool_first:visit_resume"
    lowered = answer.message_text.casefold()
    assert "retomar a visita" in lowered
    assert "vis-123" in lowered


def test_admin_finance_combo_query_detects_regularidade_and_finance() -> None:
    assert _looks_like_admin_finance_combo_query(
        'Quero a regularidade documental e a situacao financeira com boletos e mensalidades.'
    )


def test_health_second_call_query_detects_attested_exam_miss() -> None:
    assert _looks_like_health_second_call_query(
        'Se eu perder uma prova por motivo de saude com atestado, como funciona a segunda chamada?'
    )


def test_health_second_call_query_detects_comprovacao_bridge_prompt() -> None:
    assert _looks_like_health_second_call_query(
        'Se o aluno perde uma prova por razao de saude, como a escola amarra comprovacao, segunda chamada e recuperacao no material publico?'
    )


def test_public_academic_policy_overview_query_does_not_steal_health_second_call() -> None:
    assert _looks_like_public_academic_policy_overview_query(
        'De forma bem objetiva, se o aluno perde uma prova por razao de saude, como a escola amarra comprovacao, segunda chamada e recuperacao no material publico?'
    ) is False


def test_specialist_preflight_promotes_health_second_call_lane() -> None:
    payload = _preflight_public_doc_bundle_answer(
        {'school_name': 'Colegio Horizonte'},
        'Se o aluno perde uma prova por razao de saude, como a escola amarra comprovacao, segunda chamada e recuperacao no material publico?',
    )
    assert payload is not None
    assert payload.reason == 'specialist_supervisor_preflight:health_second_call'


def test_calendar_week_query_detects_generic_public_calendar_prompt() -> None:
    assert _looks_like_calendar_week_query(
        'Dentro do calendario publico, quais eventos parecem mais importantes para familias e responsaveis?'
    )


def test_calendar_week_query_accepts_principais_wording() -> None:
    assert _looks_like_calendar_week_query(
        'Quero os principais eventos publicos para familias e responsaveis nesta base escolar.'
    )


def test_timeline_lifecycle_query_detects_marcos_entre_prompt() -> None:
    assert _looks_like_timeline_lifecycle_query(
        'Quais sao os marcos entre matricula, inicio do ano letivo e reuniao de responsaveis no calendario publico de 2026?'
    )


def test_timeline_lifecycle_query_detects_qual_vem_primeiro_prompt() -> None:
    assert _looks_like_timeline_lifecycle_query(
        'No calendario publico de 2026, qual vem primeiro entre matricula, inicio das aulas e encontro inicial com responsaveis?'
    )


def test_specialist_family_new_calendar_query_accepts_parents_starting_school_prompt() -> None:
    assert _looks_like_family_new_calendar_enrollment_query(
        'De forma bem objetiva, para pais estreando na escola, como ler juntos manual de matricula, calendario e agenda de avaliacoes para entender o primeiro bimestre?'
    )


def test_specialist_family_new_calendar_query_accepts_first_enrollment_first_bimester_prompt() -> None:
    assert _looks_like_family_new_calendar_enrollment_query(
        'Estamos fazendo a primeira matricula da familia: como calendario, agenda de avaliacoes e processo de ingresso se organizam no primeiro bimestre?'
    )


def test_specialist_first_month_risks_query_accepts_tropecos_travando_prompt() -> None:
    assert _looks_like_first_month_risks_query(
        'Quais tropecos das primeiras semanas mais acabam travando credenciais, documentos e a rotina da familia?'
    )


def test_specialist_timeline_bundle_handles_explicit_before_after_without_recent_context() -> None:
    profile = {
        'public_timeline': [
            {'topic_key': 'school_year_start', 'starts_at': '2026-02-02', 'summary': 'Inicio das aulas em 02/02/2026.'},
            {'topic_key': 'family_meeting', 'starts_at': '2026-02-05', 'summary': 'Primeira reuniao com responsaveis em 05/02/2026.'},
        ]
    }
    answer = _compose_timeline_bundle_answer(profile, 'E a primeira reuniao acontece antes ou depois das aulas?')
    assert answer is not None
    assert 'depois do inicio das aulas' in answer


def test_specialist_timeline_bundle_handles_order_only_without_recent_context() -> None:
    profile = {
        'public_timeline': [
            {'topic_key': 'admissions_opening', 'summary': 'Matricula comecou em 10/01/2026.'},
            {'topic_key': 'school_year_start', 'summary': 'Inicio das aulas em 02/02/2026.'},
            {'topic_key': 'family_meeting', 'summary': 'Primeira reuniao com responsaveis em 05/02/2026.'},
        ]
    }
    answer = _compose_timeline_bundle_answer(
        profile,
        'Nao quero o calendario inteiro. Quero so esse recorte em ordem.',
    )
    assert answer is not None
    assert '1) Matricula e ingresso' in answer


def test_specialist_timeline_bundle_mentions_assessments_when_prompt_requests_them() -> None:
    profile = {
        'public_timeline': [
            {'topic_key': 'admissions_opening', 'summary': 'Matricula comecou em 10/01/2026.'},
            {'topic_key': 'school_year_start', 'summary': 'Inicio das aulas em 02/02/2026.'},
            {'topic_key': 'family_meeting', 'summary': 'Primeira reuniao com responsaveis em 05/02/2026.'},
        ]
    }
    answer = _compose_timeline_bundle_answer(
        profile,
        'Como matricula, inicio das aulas e avaliacoes se relacionam no comeco do ano?',
    )
    assert answer is not None
    assert 'avaliacoes' in answer.casefold()


def test_year_three_phases_query_detects_se_eu_dividir_o_ano_prompt() -> None:
    assert _looks_like_year_three_phases_query(
        'Se eu dividir o ano em admissao, rotina academica e fechamento, como isso aparece na linha do tempo publica?'
    )


def test_visibility_boundary_query_detects_where_public_content_ends() -> None:
    assert _looks_like_visibility_boundary_query(
        'Nos canais da escola, onde termina o conteudo publico e onde comeca o que exige autenticacao da familia?'
    )


def test_process_compare_query_detects_side_by_side_public_compare() -> None:
    assert _looks_like_process_compare_query(
        'Pensando no caso pratico, se a familia colocar rematricula, transferencia e cancelamento lado a lado, quais diferencas praticas aparecem em papelada e prazos?'
    )


def test_process_compare_query_detects_mudancas_reais_wording() -> None:
    assert _looks_like_process_compare_query(
        'Se eu comparar rematricula, transferencia e cancelamento, quais mudancas reais aparecem em prazos e documentacao?'
    )


def test_public_doc_bundle_request_detects_documentary_open_governance_prompt() -> None:
    assert _looks_like_public_doc_bundle_request(
        'Quero entender como a familia sobe da coordenacao para a lideranca maior quando o impasse sai da rotina normal.'
    )


def test_resolved_intent_attendance_summary_aggregates_linked_students_when_prompt_mentions_filhos() -> None:
    async def _fetch_academic_summary_payload(_ctx, *, student_name_hint=None, **_kwargs):
        if student_name_hint == 'Lucas Oliveira':
            return {
                'summary': {
                    'student_name': 'Lucas Oliveira',
                    'attendance': [
                        {'subject_name': 'Fisica', 'present_count': 9, 'late_count': 2, 'absent_count': 3, 'absent_minutes': 120},
                    ],
                }
            }
        if student_name_hint == 'Ana Oliveira':
            return {
                'summary': {
                    'student_name': 'Ana Oliveira',
                    'attendance': [
                        {'subject_name': 'Fisica', 'present_count': 12, 'late_count': 0, 'absent_count': 1, 'absent_minutes': 50},
                    ],
                }
            }
        return None

    ctx = SimpleNamespace(
        request=SimpleNamespace(
            user=SimpleNamespace(authenticated=True),
            message='Me de um panorama de faltas e frequencia dos meus filhos, apontando quem exige maior atencao agora.',
        ),
        actor={'students': [{'full_name': 'Lucas Oliveira'}, {'full_name': 'Ana Oliveira'}]},
        resolved_turn=ResolvedTurnIntent(
            key='academic.attendance_summary',
            domain='academic',
            subintent='attendance_summary',
            capability='academic.attendance_summary',
            access_tier='authenticated',
            confidence=0.98,
        ),
        operational_memory=OperationalMemory(),
        conversation_context={},
    )
    deps = ResolvedIntentDeps(
        normalize_text=lambda value: str(value or '').casefold(),
        looks_like_subject_followup=lambda _message: False,
        looks_like_academic_risk_followup=lambda _message: False,
        looks_like_family_finance_aggregate_query=lambda _message: False,
        looks_like_family_attendance_aggregate_query=lambda _message: 'frequencia dos meus filhos' in str(_message).casefold(),
        fetch_academic_summary_payload=_fetch_academic_summary_payload,
        fetch_financial_summary_payload=lambda *_args, **_kwargs: None,
        fetch_upcoming_assessments_payload=lambda *_args, **_kwargs: None,
        resolved_academic_target_name=lambda *_args, **_kwargs: None,
        needs_specific_academic_student_clarification=lambda *_args, **_kwargs: True,
        build_academic_student_selection_clarify=lambda *_args, **_kwargs: None,
        compose_academic_risk_answer=lambda _summary: '',
        compose_named_subject_grade_answer=lambda *_args, **_kwargs: None,
        compose_named_grade_answer=lambda _summary: '',
        compose_named_attendance_answer=(
            lambda summary, **_kwargs: f"{summary['student_name']}: {summary['attendance'][0]['absent_count']} faltas e {summary['attendance'][0]['late_count']} atrasos."
        ),
        compose_academic_snapshot_lines=lambda _summary: [],
        compose_academic_aggregate_answer=lambda _summaries: '',
        compose_finance_aggregate_answer=lambda _summaries: '',
        compose_finance_installments_answer=lambda _summary: '',
        linked_students=lambda actor, **_kwargs: list(actor.get('students') or []),
        safe_excerpt=lambda text, **_kwargs: text,
        subject_hint_from_text=lambda _message: None,
        recent_subject_from_context=lambda *_args, **_kwargs: None,
        subject_code_from_hint=lambda *_args, **_kwargs: (None, None),
        student_hint_from_message=lambda *_args, **_kwargs: None,
        is_student_name_only_followup=lambda *_args, **_kwargs: None,
        compose_upcoming_assessments_lines=lambda _summary: [],
    )

    answer = asyncio.run(maybe_resolved_intent_answer(ctx, deps=deps))
    assert answer is not None
    assert answer.reason == 'specialist_supervisor_resolved_intent:attendance_summary_aggregate'
    assert 'Lucas Oliveira' in answer.message_text
    assert 'Ana Oliveira' in answer.message_text
    assert 'Quem exige maior atencao agora: Lucas Oliveira.' in answer.message_text


def test_resolved_intent_recovers_family_academic_next_in_line_from_recent_context() -> None:
    async def _fetch_academic_summary_payload(_ctx, *, student_name_hint=None, **_kwargs):
        if student_name_hint == 'Lucas Oliveira':
            return {
                'summary': {
                    'student_name': 'Lucas Oliveira',
                    'grades': [
                        {'subject_name': 'Fisica', 'score': 5.9},
                        {'subject_name': 'Historia', 'score': 6.8},
                    ],
                }
            }
        if student_name_hint == 'Ana Oliveira':
            return {
                'summary': {
                    'student_name': 'Ana Oliveira',
                    'grades': [
                        {'subject_name': 'Fisica', 'score': 6.4},
                        {'subject_name': 'Historia', 'score': 7.3},
                    ],
                }
            }
        return None

    ctx = SimpleNamespace(
        request=SimpleNamespace(
            user=SimpleNamespace(authenticated=True),
            message='E logo depois dele, quem vem na fila?',
        ),
        actor={'students': [{'full_name': 'Lucas Oliveira'}, {'full_name': 'Ana Oliveira'}]},
        resolved_turn=ResolvedTurnIntent(),
        operational_memory=OperationalMemory(),
        conversation_context={
            'recent_messages': [
                {'sender_type': 'assistant', 'content': 'Panorama academico das contas vinculadas: Lucas Oliveira e Ana Oliveira. Quem hoje exige maior atencao academica e Lucas Oliveira.'},
            ]
        },
    )
    deps = ResolvedIntentDeps(
        normalize_text=lambda value: str(value or '').casefold(),
        looks_like_subject_followup=lambda _message: False,
        looks_like_academic_risk_followup=lambda _message: False,
        looks_like_family_finance_aggregate_query=lambda _message: False,
        looks_like_family_attendance_aggregate_query=lambda _message: False,
        fetch_academic_summary_payload=_fetch_academic_summary_payload,
        fetch_financial_summary_payload=lambda *_args, **_kwargs: None,
        fetch_upcoming_assessments_payload=lambda *_args, **_kwargs: None,
        resolved_academic_target_name=lambda *_args, **_kwargs: None,
        needs_specific_academic_student_clarification=lambda *_args, **_kwargs: False,
        build_academic_student_selection_clarify=lambda *_args, **_kwargs: None,
        compose_academic_risk_answer=lambda _summary: '',
        compose_named_subject_grade_answer=lambda *_args, **_kwargs: None,
        compose_named_grade_answer=lambda _summary: '',
        compose_named_attendance_answer=lambda *_args, **_kwargs: '',
        compose_academic_snapshot_lines=lambda _summary: [],
        compose_academic_aggregate_answer=lambda _summaries: '',
        compose_finance_aggregate_answer=lambda _summaries: '',
        compose_finance_installments_answer=lambda _summary: '',
        linked_students=lambda actor, **_kwargs: list(actor.get('students') or []),
        safe_excerpt=lambda text, **_kwargs: text,
        subject_hint_from_text=lambda _message: None,
        recent_subject_from_context=lambda *_args, **_kwargs: None,
        subject_code_from_hint=lambda *_args, **_kwargs: (None, None),
        student_hint_from_message=lambda *_args, **_kwargs: None,
        is_student_name_only_followup=lambda *_args, **_kwargs: None,
        compose_upcoming_assessments_lines=lambda _summary: [],
    )

    answer = asyncio.run(maybe_resolved_intent_answer(ctx, deps=deps))
    assert answer is not None
    assert answer.reason == 'specialist_supervisor_recent_context:family_academic_next_in_line_followup'
    assert 'Ana Oliveira' in answer.message_text


def test_resolved_intent_recovers_family_academic_reason_from_principal_motivo_wording() -> None:
    async def _fetch_academic_summary_payload(_ctx, *, student_name_hint=None, **_kwargs):
        if student_name_hint == 'Lucas Oliveira':
            return {
                'summary': {
                    'student_name': 'Lucas Oliveira',
                    'grades': [
                        {'subject_name': 'Fisica', 'score': 5.9},
                        {'subject_name': 'Historia', 'score': 6.8},
                    ],
                }
            }
        if student_name_hint == 'Ana Oliveira':
            return {
                'summary': {
                    'student_name': 'Ana Oliveira',
                    'grades': [
                        {'subject_name': 'Fisica', 'score': 6.4},
                        {'subject_name': 'Historia', 'score': 7.3},
                    ],
                }
            }
        return None

    ctx = SimpleNamespace(
        request=SimpleNamespace(
            user=SimpleNamespace(authenticated=True),
            message='Sem repetir o quadro inteiro: qual e o principal motivo desse alerta?',
        ),
        actor={'students': [{'full_name': 'Lucas Oliveira'}, {'full_name': 'Ana Oliveira'}]},
        resolved_turn=ResolvedTurnIntent(),
        operational_memory=OperationalMemory(),
        conversation_context={
            'recent_messages': [
                {'sender_type': 'assistant', 'content': 'Panorama academico das contas vinculadas: Lucas Oliveira e Ana Oliveira. Quem hoje exige maior atencao academica e Lucas Oliveira.'},
            ]
        },
    )
    deps = ResolvedIntentDeps(
        normalize_text=lambda value: str(value or '').casefold(),
        looks_like_subject_followup=lambda _message: False,
        looks_like_academic_risk_followup=lambda _message: False,
        looks_like_family_finance_aggregate_query=lambda _message: False,
        looks_like_family_attendance_aggregate_query=lambda _message: False,
        fetch_academic_summary_payload=_fetch_academic_summary_payload,
        fetch_financial_summary_payload=lambda *_args, **_kwargs: None,
        fetch_upcoming_assessments_payload=lambda *_args, **_kwargs: None,
        resolved_academic_target_name=lambda *_args, **_kwargs: None,
        needs_specific_academic_student_clarification=lambda *_args, **_kwargs: False,
        build_academic_student_selection_clarify=lambda *_args, **_kwargs: None,
        compose_academic_risk_answer=lambda _summary: '',
        compose_named_subject_grade_answer=lambda *_args, **_kwargs: None,
        compose_named_grade_answer=lambda _summary: '',
        compose_named_attendance_answer=lambda *_args, **_kwargs: '',
        compose_academic_snapshot_lines=lambda _summary: [],
        compose_academic_aggregate_answer=lambda _summaries: '',
        compose_finance_aggregate_answer=lambda _summaries: '',
        compose_finance_installments_answer=lambda _summary: '',
        linked_students=lambda actor, **_kwargs: list(actor.get('students') or []),
        safe_excerpt=lambda text, **_kwargs: text,
        subject_hint_from_text=lambda _message: None,
        recent_subject_from_context=lambda *_args, **_kwargs: None,
        subject_code_from_hint=lambda *_args, **_kwargs: (None, None),
        student_hint_from_message=lambda *_args, **_kwargs: None,
        is_student_name_only_followup=lambda *_args, **_kwargs: None,
        compose_upcoming_assessments_lines=lambda _summary: [],
    )

    answer = asyncio.run(maybe_resolved_intent_answer(ctx, deps=deps))
    assert answer is not None
    assert answer.reason == 'specialist_supervisor_recent_context:family_academic_reason_followup'
    assert 'Lucas Oliveira' in answer.message_text


def test_resolved_intent_recovers_attendance_next_step_from_recent_context() -> None:
    async def _fetch_academic_summary_payload(_ctx, *, student_name_hint=None, **_kwargs):
        if student_name_hint == 'Lucas Oliveira':
            return {
                'summary': {
                    'student_name': 'Lucas Oliveira',
                    'attendance': [
                        {'subject_name': 'Biologia', 'present_count': 8, 'late_count': 1, 'absent_count': 3, 'absent_minutes': 90},
                        {'subject_name': 'Historia', 'present_count': 10, 'late_count': 0, 'absent_count': 1, 'absent_minutes': 20},
                    ],
                }
            }
        return None

    ctx = SimpleNamespace(
        request=SimpleNamespace(
            user=SimpleNamespace(authenticated=True),
            message='Sem repetir os numeros todos, o que eu deveria acompanhar primeiro?',
        ),
        actor={'students': [{'full_name': 'Lucas Oliveira'}, {'full_name': 'Ana Oliveira'}]},
        resolved_turn=ResolvedTurnIntent(),
        operational_memory=OperationalMemory(active_student_name='Lucas Oliveira'),
        conversation_context={
            'recent_messages': [
                {'sender_type': 'assistant', 'content': 'Panorama de faltas e frequencia das contas vinculadas: Lucas Oliveira exige maior atencao agora.'},
                {'sender_type': 'user', 'content': 'Me diga so o principal alerta do Lucas.'},
            ]
        },
    )
    deps = ResolvedIntentDeps(
        normalize_text=lambda value: str(value or '').casefold(),
        looks_like_subject_followup=lambda _message: False,
        looks_like_academic_risk_followup=lambda _message: False,
        looks_like_family_finance_aggregate_query=lambda _message: False,
        looks_like_family_attendance_aggregate_query=lambda _message: False,
        fetch_academic_summary_payload=_fetch_academic_summary_payload,
        fetch_financial_summary_payload=lambda *_args, **_kwargs: None,
        fetch_upcoming_assessments_payload=lambda *_args, **_kwargs: None,
        resolved_academic_target_name=lambda *_args, **_kwargs: None,
        needs_specific_academic_student_clarification=lambda _ctx, *, target_name=None, subject_hint=None: not bool(target_name),
        build_academic_student_selection_clarify=lambda *_args, **_kwargs: None,
        compose_academic_risk_answer=lambda _summary: '',
        compose_named_subject_grade_answer=lambda *_args, **_kwargs: None,
        compose_named_grade_answer=lambda _summary: '',
        compose_named_attendance_answer=lambda *_args, **_kwargs: '',
        compose_academic_snapshot_lines=lambda _summary: [],
        compose_academic_aggregate_answer=lambda _summaries: '',
        compose_finance_aggregate_answer=lambda _summaries: '',
        compose_finance_installments_answer=lambda _summary: '',
        linked_students=lambda actor, **_kwargs: list(actor.get('students') or []),
        safe_excerpt=lambda text, **_kwargs: text,
        subject_hint_from_text=lambda _message: None,
        recent_subject_from_context=lambda *_args, **_kwargs: None,
        subject_code_from_hint=lambda *_args, **_kwargs: (None, None),
        student_hint_from_message=lambda *_args, **_kwargs: None,
        is_student_name_only_followup=lambda *_args, **_kwargs: None,
        compose_upcoming_assessments_lines=lambda _summary: [],
    )

    answer = asyncio.run(maybe_resolved_intent_answer(ctx, deps=deps))
    assert answer is not None
    assert answer.reason == 'specialist_supervisor_resolved_intent:attendance_next_step'
    assert 'Lucas Oliveira' in answer.message_text
    assert 'Biologia' in answer.message_text


def test_academic_risk_followup_detects_risco_academico_label() -> None:
    deps = SimpleNamespace(normalize_text=lambda value: value.casefold())
    assert looks_like_academic_risk_followup(
        'Sem repetir o quadro inteiro, recorte so a Ana e mostre onde o risco academico dela esta mais alto.',
        deps=deps,
    )


def test_internal_document_query_and_hit_score_favor_specific_hits() -> None:
    query = 'O protocolo interno para responsaveis com escopo parcial fala algo sobre Telegram?'
    assert _looks_like_internal_document_query(query)
    strong_hit = {
        'title': 'Protocolo interno para responsaveis com escopo parcial no Telegram',
        'summary': 'Limites de acesso e uso do Telegram por responsaveis com escopo parcial.',
        'content': 'Telegram, escopo parcial e regras operacionais.',
        'document_score': 0.4,
    }
    weak_hit = {
        'title': 'Manual interno do professor',
        'summary': 'Registro de avaliacoes.',
        'content': 'Fluxos academicos gerais.',
        'document_score': 0.4,
    }
    assert _internal_doc_hit_score(query, strong_hit) > _internal_doc_hit_score(query, weak_hit)


def test_internal_document_query_matches_material_interno_prompt() -> None:
    assert _looks_like_internal_document_query(
        'No material interno do professor, como a escola orienta o registro de avaliacoes?'
    )


def test_internal_document_query_matches_orientacao_interna_prompt() -> None:
    assert _looks_like_internal_document_query(
        'Existe alguma orientacao interna sobre excursao internacional com hospedagem para o ensino medio?'
    )


def test_human_handoff_request_detects_explicit_secretaria_request() -> None:
    assert _looks_like_human_handoff_request('Quero falar com a secretaria agora.')


def test_human_handoff_request_does_not_steal_documental_status_query() -> None:
    assert not _looks_like_human_handoff_request(
        'Quero ver o quadro documental da Ana e o que esta pendente.'
    )


def test_human_handoff_request_does_not_steal_internal_document_probe() -> None:
    assert not _looks_like_human_handoff_request(
        'Os documentos internos mencionam algum protocolo para excursao internacional com pernoite no ensino medio?'
    )


def test_human_handoff_request_does_not_steal_restricted_finance_playbook_probe() -> None:
    assert not _looks_like_human_handoff_request(
        'Segundo o playbook interno de negociacao financeira, que criterios guiam o atendimento a uma familia?'
    )


def test_human_handoff_request_does_not_steal_bloqueio_de_atendimento_combo() -> None:
    assert not _looks_like_human_handoff_request(
        'Junte documentacao administrativa e financeiro das contas vinculadas e diga se ha bloqueio de atendimento.'
    )


def test_augment_public_followup_message_rewrites_contact_followup_to_explicit_routing() -> None:
    deps = SimpleNamespace(normalize_text=lambda value: str(value or '').casefold())
    rewritten = _augment_public_followup_message(
        'E os contatos da secretaria e do financeiro junto com isso?',
        ['sou familia nova. como portal, secretaria e envio de documentos entram na ordem certa antes do inicio das aulas?'],
        deps=deps,
    )
    assert 'como entrar em contato com a secretaria e com o financeiro' in rewritten


def test_augment_public_followup_message_rewrites_teacher_boundary_followup() -> None:
    deps = SimpleNamespace(normalize_text=lambda value: str(value or '').casefold())
    rewritten = _augment_public_followup_message(
        'Ou manda procurar a coordenação?',
        ['quero falar com o professor de matemática'],
        deps=deps,
    )
    assert 'professor' in rewritten.casefold()
    assert 'coordenacao' in rewritten.casefold()


def test_augment_public_followup_message_rewrites_public_calendar_reset() -> None:
    deps = SimpleNamespace(normalize_text=lambda value: str(value or '').casefold())
    rewritten = _augment_public_followup_message(
        'Não, quero só o calendário público',
        ['quando começam as aulas?', 'e as notas da ana?'],
        deps=deps,
    )
    assert 'calendario publico' in rewritten.casefold()
    assert 'inicio das aulas' in rewritten.casefold()


def test_detect_support_handoff_queue_routes_financial_message() -> None:
    ctx = SimpleNamespace(
        request=SimpleNamespace(message='Preciso falar sobre boletos e mensalidades.'),
        specialist_registry={},
        operational_memory=None,
    )
    assert _detect_support_handoff_queue(ctx) == 'financeiro'


def test_provider_metadata_omits_llm_keys_when_false() -> None:
    deps = SimpleNamespace(
        resolve_llm_provider=lambda _settings: 'openai',
        effective_llm_model_name=lambda _settings: 'gpt-5.4-mini',
    )
    metadata = _provider_metadata(deps, settings=object())
    assert metadata == {'provider': 'openai', 'model': 'gpt-5.4-mini'}


def test_persist_and_dump_preserves_answer_used_llm_when_metadata_is_silent() -> None:
    persisted: dict[str, object] = {}

    async def _persist_final_answer(_context, **kwargs):
        persisted.update(kwargs)

    deps = SimpleNamespace(persist_final_answer=_persist_final_answer)
    context = SimpleNamespace()
    answer = SupervisorAnswerPayload(
        message_text='Resposta gerada por specialist.',
        mode='structured_tool',
        classification=MessageIntentClassification(
            domain='institution',
            access_tier='public',
            confidence=1.0,
            reason='specialist_supervisor_fast_path:general_knowledge',
        ),
        graph_path=['specialist_supervisor', 'fast_path', 'general_knowledge'],
        reason='specialist_supervisor_fast_path:general_knowledge',
        used_llm=True,
        llm_stages=['general_knowledge_fast_path'],
    )

    payload = asyncio.run(
        _persist_and_dump(
            deps,
            context,
            answer=answer,
            route='general_knowledge_fast_path',
            metadata={'provider': 'openai', 'model': 'gpt-5.4-mini'},
        )
    )

    assert persisted['answer'].used_llm is True
    assert persisted['answer'].llm_stages == ['general_knowledge_fast_path']
    assert payload['answer']['used_llm'] is True
    assert payload['answer']['llm_stages'] == ['general_knowledge_fast_path']


def test_operational_memory_does_not_reuse_subject_answer_for_unrelated_admin_finance_prompt() -> None:
    async def _unexpected_fetch(*_args, **_kwargs):
        raise AssertionError("operational memory should not fetch stale academic context for a new admin+finance turn")

    ctx = SimpleNamespace(
        request=SimpleNamespace(
            user=SimpleNamespace(authenticated=True),
            message='Minha documentação cadastral ainda pode travar algum atendimento administrativo ou financeiro?',
        ),
        actor=None,
        operational_memory=OperationalMemory(
            active_domain='academic',
            active_student_name='Lucas Oliveira',
            active_subject='Historia',
        ),
    )
    deps = OperationalMemoryDeps(
        normalize_text=lambda value: str(value or '').casefold(),
        looks_like_public_doc_bundle_request=lambda _message: False,
        is_student_name_only_followup=lambda *_args, **_kwargs: None,
        effective_multi_intent_domains=lambda *_args, **_kwargs: ['finance'],
        subject_hint_from_text=lambda _message: None,
        looks_like_subject_followup=lambda _message: False,
        looks_like_student_pronoun_followup=lambda _message: False,
        student_hint_from_message=lambda *_args, **_kwargs: None,
        fetch_academic_summary_payload=_unexpected_fetch,
        fetch_financial_summary_payload=_unexpected_fetch,
        fetch_upcoming_assessments_payload=_unexpected_fetch,
        build_academic_finance_combo_payload=lambda **_kwargs: None,
        build_grade_requirement_answer=lambda **_kwargs: None,
        compose_academic_risk_answer=lambda _summary: '',
        compose_named_subject_grade_answer=lambda *_args, **_kwargs: None,
        compose_upcoming_assessments_lines=lambda _summary: [],
        safe_excerpt=lambda text, **_kwargs: text,
        looks_like_academic_risk_followup=lambda _message: False,
        looks_like_other_student_followup=lambda _message: False,
        other_linked_student=lambda *_args, **_kwargs: None,
        compose_admin_status_answer=lambda _summary: '',
        compose_named_grade_answer=lambda _summary: '',
        compose_finance_installments_answer=lambda _summary: '',
    )

    answer = asyncio.run(maybe_operational_memory_follow_up_answer(ctx, deps=deps))
    assert answer is None


def test_operational_memory_does_not_reuse_subject_answer_for_greeting() -> None:
    async def _unexpected_fetch(*_args, **_kwargs):
        raise AssertionError("operational memory should not fetch stale academic context for a greeting")

    ctx = SimpleNamespace(
        request=SimpleNamespace(
            user=SimpleNamespace(authenticated=True),
            message='oi',
        ),
        actor=None,
        operational_memory=OperationalMemory(
            active_domain='academic',
            active_student_name='Lucas Oliveira',
            active_subject='Historia',
        ),
    )
    deps = OperationalMemoryDeps(
        normalize_text=lambda value: str(value or '').casefold(),
        looks_like_public_doc_bundle_request=lambda _message: False,
        is_student_name_only_followup=lambda *_args, **_kwargs: None,
        effective_multi_intent_domains=lambda *_args, **_kwargs: [],
        subject_hint_from_text=lambda _message: None,
        looks_like_subject_followup=lambda _message: False,
        looks_like_student_pronoun_followup=lambda _message: False,
        student_hint_from_message=lambda *_args, **_kwargs: None,
        fetch_academic_summary_payload=_unexpected_fetch,
        fetch_financial_summary_payload=_unexpected_fetch,
        fetch_upcoming_assessments_payload=_unexpected_fetch,
        build_academic_finance_combo_payload=lambda **_kwargs: None,
        build_grade_requirement_answer=lambda **_kwargs: None,
        compose_academic_risk_answer=lambda _summary: '',
        compose_named_subject_grade_answer=lambda *_args, **_kwargs: None,
        compose_upcoming_assessments_lines=lambda _summary: [],
        safe_excerpt=lambda text, **_kwargs: text,
        looks_like_academic_risk_followup=lambda _message: False,
        looks_like_other_student_followup=lambda _message: False,
        other_linked_student=lambda *_args, **_kwargs: None,
        compose_admin_status_answer=lambda _summary: '',
        compose_named_grade_answer=lambda _summary: '',
        compose_finance_installments_answer=lambda _summary: '',
    )

    answer = asyncio.run(maybe_operational_memory_follow_up_answer(ctx, deps=deps))
    assert answer is None


def test_operational_memory_builds_cross_student_academic_comparison_after_public_digression() -> None:
    summaries = {
        "Lucas Oliveira": {
            "student_name": "Lucas Oliveira",
            "grades": [
                {"subject_name": "Fisica", "score": "5.9"},
                {"subject_name": "Matematica", "score": "7.7"},
            ],
        },
        "Ana Oliveira": {
            "student_name": "Ana Oliveira",
            "grades": [
                {"subject_name": "Fisica", "score": "6.3"},
                {"subject_name": "Matematica", "score": "7.8"},
            ],
        },
    }

    async def _fetch_academic_summary_payload(_ctx, *, student_name_hint=None, **_kwargs):
        if student_name_hint in summaries:
            return {"summary": summaries[student_name_hint]}
        return None

    async def _unexpected_fetch(*_args, **_kwargs):
        raise AssertionError("financial and upcoming fetches are not expected in this comparison follow-up")

    ctx = SimpleNamespace(
        request=SimpleNamespace(
            user=SimpleNamespace(authenticated=True),
            message='e compara isso com a Ana',
        ),
        actor=None,
        operational_memory=OperationalMemory(
            active_domain='academic',
            active_student_name='Lucas Oliveira',
            active_student_id='stu-lucas',
        ),
    )
    deps = OperationalMemoryDeps(
        normalize_text=lambda value: str(value or '').casefold(),
        looks_like_public_doc_bundle_request=lambda _message: False,
        is_student_name_only_followup=lambda *_args, **_kwargs: None,
        effective_multi_intent_domains=lambda *_args, **_kwargs: [],
        subject_hint_from_text=lambda _message: None,
        looks_like_subject_followup=lambda _message: False,
        looks_like_student_pronoun_followup=lambda _message: False,
        student_hint_from_message=lambda *_args, **_kwargs: 'Ana Oliveira',
        fetch_academic_summary_payload=_fetch_academic_summary_payload,
        fetch_financial_summary_payload=_unexpected_fetch,
        fetch_upcoming_assessments_payload=_unexpected_fetch,
        build_academic_finance_combo_payload=lambda **_kwargs: None,
        build_grade_requirement_answer=lambda **_kwargs: None,
        compose_academic_risk_answer=lambda _summary: '',
        compose_named_subject_grade_answer=lambda *_args, **_kwargs: None,
        compose_upcoming_assessments_lines=lambda _summary: [],
        safe_excerpt=lambda text, **_kwargs: text,
        looks_like_academic_risk_followup=lambda _message: False,
        looks_like_other_student_followup=lambda _message: False,
        other_linked_student=lambda *_args, **_kwargs: {"student_id": "stu-ana", "full_name": "Ana Oliveira"},
        compose_admin_status_answer=lambda _summary: '',
        compose_named_grade_answer=lambda _summary: '',
        compose_finance_installments_answer=lambda _summary: '',
    )

    answer = asyncio.run(maybe_operational_memory_follow_up_answer(ctx, deps=deps))

    assert answer is not None
    assert answer.reason == 'specialist_supervisor_memory:cross_student_academic_comparison'
    lowered = answer.message_text.casefold()
    assert 'comparando lucas oliveira com ana oliveira' in lowered
    assert 'media minima' in lowered or 'média mínima' in lowered


def test_operational_memory_builds_cross_student_academic_comparison_with_two_names_after_public_turn() -> None:
    summaries = {
        "Lucas Oliveira": {
            "student_name": "Lucas Oliveira",
            "grades": [
                {"subject_name": "Fisica", "score": "5.9"},
                {"subject_name": "Matematica", "score": "7.7"},
            ],
        },
        "Ana Oliveira": {
            "student_name": "Ana Oliveira",
            "grades": [
                {"subject_name": "Fisica", "score": "6.4"},
                {"subject_name": "Matematica", "score": "7.4"},
            ],
        },
    }

    async def _fetch_academic_summary_payload(_ctx, *, student_name_hint=None, **_kwargs):
        if student_name_hint in summaries:
            return {"summary": summaries[student_name_hint]}
        return None

    async def _unexpected_fetch(*_args, **_kwargs):
        raise AssertionError("financial and upcoming fetches are not expected in this comparison follow-up")

    ctx = SimpleNamespace(
        request=SimpleNamespace(
            user=SimpleNamespace(authenticated=True),
            message='voltando aos meus filhos, compara o Lucas com a Ana',
        ),
        actor={
            "linked_students": [
                {"student_id": "stu-lucas", "full_name": "Lucas Oliveira", "can_view_academic": True},
                {"student_id": "stu-ana", "full_name": "Ana Oliveira", "can_view_academic": True},
            ]
        },
        operational_memory=OperationalMemory(
            active_domain='public',
            active_student_name='Lucas Oliveira',
            active_student_id='stu-lucas',
        ),
    )
    deps = OperationalMemoryDeps(
        normalize_text=lambda value: str(value or '').casefold(),
        looks_like_public_doc_bundle_request=lambda _message: False,
        is_student_name_only_followup=lambda *_args, **_kwargs: None,
        effective_multi_intent_domains=lambda *_args, **_kwargs: [],
        subject_hint_from_text=lambda _message: None,
        looks_like_subject_followup=lambda _message: False,
        looks_like_student_pronoun_followup=lambda _message: False,
        student_hint_from_message=lambda *_args, **_kwargs: 'Lucas Oliveira',
        fetch_academic_summary_payload=_fetch_academic_summary_payload,
        fetch_financial_summary_payload=_unexpected_fetch,
        fetch_upcoming_assessments_payload=_unexpected_fetch,
        build_academic_finance_combo_payload=lambda **_kwargs: None,
        build_grade_requirement_answer=lambda **_kwargs: None,
        compose_academic_risk_answer=lambda _summary: '',
        compose_named_subject_grade_answer=lambda *_args, **_kwargs: None,
        compose_upcoming_assessments_lines=lambda _summary: [],
        safe_excerpt=lambda text, **_kwargs: text,
        looks_like_academic_risk_followup=lambda _message: False,
        looks_like_other_student_followup=lambda _message: False,
        other_linked_student=lambda *_args, **_kwargs: {"student_id": "stu-ana", "full_name": "Ana Oliveira"},
        compose_admin_status_answer=lambda _summary: '',
        compose_named_grade_answer=lambda _summary: '',
        compose_finance_installments_answer=lambda _summary: '',
    )

    answer = asyncio.run(maybe_operational_memory_follow_up_answer(ctx, deps=deps))

    assert answer is not None
    assert answer.reason == 'specialist_supervisor_memory:cross_student_academic_comparison'
    lowered = answer.message_text.casefold()
    assert 'comparando lucas oliveira com ana oliveira' in lowered
    assert 'media minima' in lowered or 'média mínima' in lowered


def test_tool_first_protected_family_academic_aggregate_does_not_clarify() -> None:
    actor = {
        "linked_students": [
            {"student_id": "stu-lucas", "full_name": "Lucas Oliveira", "can_view_academic": True},
            {"student_id": "stu-ana", "full_name": "Ana Oliveira", "can_view_academic": True},
        ]
    }
    summaries = {
        "Lucas Oliveira": {"student_name": "Lucas Oliveira"},
        "Ana Oliveira": {"student_name": "Ana Oliveira"},
    }

    async def _fetch_academic_summary_payload(_ctx, *, student_name_hint=None, **_kwargs):
        if student_name_hint in summaries:
            return {"summary": summaries[student_name_hint]}
        return None

    async def _unused_fetch(*_args, **_kwargs):
        raise AssertionError("this path should stay on academic family aggregate only")

    ctx = SimpleNamespace(
        request=SimpleNamespace(
            message='Resuma o quadro academico dos meus dois filhos e diga quem esta mais perto do limite de aprovacao.',
            user=SimpleNamespace(authenticated=True),
        ),
        actor=actor,
        resolved_turn=None,
    )
    deps = ToolFirstProtectedDeps(
        normalize_text=lambda value: str(value or '').casefold(),
        contains_any=lambda message, terms: any(term in str(message).casefold() for term in terms),
        looks_like_admin_finance_combo_query=lambda _message: False,
        looks_like_family_finance_aggregate_query=lambda _message: False,
        unknown_explicit_student_reference=lambda *_args, **_kwargs: None,
        student_hint_from_message=lambda *_args, **_kwargs: None,
        looks_like_student_pronoun_followup=lambda _message: False,
        fetch_financial_summary_payload=_unused_fetch,
        linked_students=lambda actor, capability="academic": [
            student
            for student in actor.get("linked_students", [])
            if capability != "academic" or student.get("can_view_academic")
        ],
        compose_finance_installments_answer=lambda _summary: "",
        compose_finance_aggregate_answer=lambda _summaries: "",
        looks_like_academic_risk_followup=lambda _message: False,
        looks_like_family_academic_aggregate_query=lambda _message: True,
        looks_like_family_attendance_aggregate_query=lambda _message: False,
        looks_like_upcoming_assessments_query=lambda _message: False,
        looks_like_attendance_timeline_query=lambda _message: False,
        subject_hint_from_text=lambda _message: None,
        looks_like_subject_followup=lambda _message: False,
        resolved_academic_target_name=lambda *_args, **_kwargs: None,
        needs_specific_academic_student_clarification=lambda *_args, **_kwargs: True,
        build_academic_student_selection_clarify=lambda *_args, **_kwargs: SupervisorAnswerPayload(
            message_text="clarify",
            mode="clarify",
            classification=MessageIntentClassification(
                domain="academic",
                access_tier="protected",
                confidence=1.0,
                reason="clarify",
            ),
            graph_path=["clarify"],
            reason="clarify",
        ),
        fetch_academic_summary_payload=_fetch_academic_summary_payload,
        fetch_upcoming_assessments_payload=_unused_fetch,
        fetch_attendance_timeline_payload=_unused_fetch,
        compose_academic_risk_answer=lambda _summary: "",
        compose_named_subject_grade_answer=lambda *_args, **_kwargs: None,
        compose_named_grade_answer=lambda _summary: "",
        compose_named_attendance_answer=lambda *_args, **_kwargs: None,
        compose_academic_snapshot_lines=lambda summary: [f"- {summary['student_name']}: resumo"],
        compose_academic_aggregate_answer=lambda summaries: "Panorama academico das contas vinculadas:\n- Lucas Oliveira: resumo\n- Ana Oliveira: resumo\nQuem hoje exige maior atencao academica e Lucas Oliveira, principalmente em Fisica.",
        compose_upcoming_assessments_lines=lambda _summary: [],
        compose_attendance_timeline_lines=lambda _summary: [],
        safe_excerpt=lambda text, **_kwargs: text,
        http_get=_unused_fetch,
        compose_actor_admin_status_answer=lambda _summary: "",
        recent_student_from_context_with_memory=lambda *_args, **_kwargs: None,
        compose_admin_status_answer=lambda _summary: "",
        find_student_by_hint=lambda *_args, **_kwargs: None,
    )

    answer = asyncio.run(
        maybe_tool_first_protected_answer(
            ctx,
            normalized=str(ctx.request.message).casefold(),
            preview={},
            memory=OperationalMemory(),
            deps=deps,
        )
    )

    assert answer is not None
    assert answer.mode == "structured_tool"
    assert answer.reason == "specialist_supervisor_tool_first:academic_summary_aggregate"
    assert "Lucas Oliveira" in answer.message_text
    assert "Ana Oliveira" in answer.message_text
    assert "Quem hoje exige maior atencao academica e Lucas Oliveira" in answer.message_text


def test_operational_memory_does_not_treat_student_plus_verb_as_name_only_followup() -> None:
    async def _unexpected_fetch(*_args, **_kwargs):
        raise AssertionError("student+verb follow-up should not resolve directly through operational memory")

    ctx = SimpleNamespace(
        request=SimpleNamespace(
            user=SimpleNamespace(authenticated=True),
            message='do lucas serve',
        ),
        actor=None,
        operational_memory=OperationalMemory(
            active_domain='academic',
            active_student_name='Lucas Oliveira',
            active_subject='Historia',
            pending_kind='academic_subject',
        ),
    )
    deps = OperationalMemoryDeps(
        normalize_text=lambda value: str(value or '').casefold(),
        looks_like_public_doc_bundle_request=lambda _message: False,
        is_student_name_only_followup=lambda *_args, **_kwargs: None,
        effective_multi_intent_domains=lambda *_args, **_kwargs: [],
        subject_hint_from_text=lambda _message: None,
        looks_like_subject_followup=lambda _message: False,
        looks_like_student_pronoun_followup=lambda _message: False,
        student_hint_from_message=lambda *_args, **_kwargs: None,
        fetch_academic_summary_payload=_unexpected_fetch,
        fetch_financial_summary_payload=_unexpected_fetch,
        fetch_upcoming_assessments_payload=_unexpected_fetch,
        build_academic_finance_combo_payload=lambda **_kwargs: None,
        build_grade_requirement_answer=lambda **_kwargs: None,
        compose_academic_risk_answer=lambda _summary: '',
        compose_named_subject_grade_answer=lambda *_args, **_kwargs: None,
        compose_upcoming_assessments_lines=lambda _summary: [],
        safe_excerpt=lambda text, **_kwargs: text,
        looks_like_academic_risk_followup=lambda _message: False,
        looks_like_other_student_followup=lambda _message: False,
        other_linked_student=lambda *_args, **_kwargs: None,
        compose_admin_status_answer=lambda _summary: '',
        compose_named_grade_answer=lambda _summary: '',
        compose_finance_installments_answer=lambda _summary: '',
    )

    answer = asyncio.run(maybe_operational_memory_follow_up_answer(ctx, deps=deps))
    assert answer is None


def test_tool_first_protected_attendance_aggregate_wins_before_academic_aggregate() -> None:
    actor = {
        "linked_students": [
            {"full_name": "Lucas Oliveira", "can_view_academic": True},
            {"full_name": "Ana Oliveira", "can_view_academic": True},
        ]
    }

    async def _fetch_academic_summary_payload(_ctx, *, student_name_hint=None, **_kwargs):
        rows = {
            "Lucas Oliveira": {
                "student_name": "Lucas Oliveira",
                "attendance": [{"subject_name": "Fisica", "present_count": 8, "late_count": 2, "absent_count": 3}],
            },
            "Ana Oliveira": {
                "student_name": "Ana Oliveira",
                "attendance": [{"subject_name": "Fisica", "present_count": 11, "late_count": 0, "absent_count": 1}],
            },
        }
        if student_name_hint in rows:
            return {"summary": rows[student_name_hint]}
        return None

    async def _unused_fetch(*_args, **_kwargs):
        return None

    ctx = SimpleNamespace(
        request=SimpleNamespace(
            message='Quero um panorama de frequencia dos meus filhos e quem esta mais vulneravel por faltas.',
            user=SimpleNamespace(authenticated=True),
        ),
        actor=actor,
        resolved_turn=None,
    )
    deps = ToolFirstProtectedDeps(
        normalize_text=lambda value: str(value or '').casefold(),
        contains_any=lambda message, terms: any(term in str(message).casefold() for term in terms),
        looks_like_admin_finance_combo_query=lambda _message: False,
        looks_like_family_finance_aggregate_query=lambda _message: False,
        unknown_explicit_student_reference=lambda *_args, **_kwargs: None,
        student_hint_from_message=lambda *_args, **_kwargs: None,
        looks_like_student_pronoun_followup=lambda _message: False,
        fetch_financial_summary_payload=_unused_fetch,
        linked_students=lambda actor, capability="academic": list(actor.get("linked_students", [])),
        compose_finance_installments_answer=lambda _summary: "",
        compose_finance_aggregate_answer=lambda _summaries: "",
        looks_like_academic_risk_followup=lambda _message: False,
        looks_like_family_academic_aggregate_query=lambda _message: True,
        looks_like_family_attendance_aggregate_query=lambda _message: True,
        looks_like_upcoming_assessments_query=lambda _message: False,
        looks_like_attendance_timeline_query=lambda _message: False,
        subject_hint_from_text=lambda _message: None,
        looks_like_subject_followup=lambda _message: False,
        resolved_academic_target_name=lambda *_args, **_kwargs: None,
        needs_specific_academic_student_clarification=lambda *_args, **_kwargs: True,
        build_academic_student_selection_clarify=lambda *_args, **_kwargs: None,
        fetch_academic_summary_payload=_fetch_academic_summary_payload,
        fetch_upcoming_assessments_payload=_unused_fetch,
        fetch_attendance_timeline_payload=_unused_fetch,
        compose_academic_risk_answer=lambda _summary: "",
        compose_named_subject_grade_answer=lambda *_args, **_kwargs: None,
        compose_named_grade_answer=lambda _summary: "",
        compose_named_attendance_answer=lambda summary, **_kwargs: f"Na frequencia de {summary['student_name']}, eu encontrei {summary['attendance'][0]['absent_count']} faltas e {summary['attendance'][0]['late_count']} atraso(s) neste recorte.",
        compose_academic_snapshot_lines=lambda summary: [f"- {summary['student_name']}: resumo"],
        compose_academic_aggregate_answer=lambda _summaries: "Panorama academico agregado",
        compose_upcoming_assessments_lines=lambda _summary: [],
        compose_attendance_timeline_lines=lambda _summary: [],
        safe_excerpt=lambda text, **_kwargs: text,
        http_get=_unused_fetch,
        compose_actor_admin_status_answer=lambda _summary: "",
        recent_student_from_context_with_memory=lambda *_args, **_kwargs: None,
        compose_admin_status_answer=lambda _summary: "",
        find_student_by_hint=lambda *_args, **_kwargs: None,
    )

    answer = asyncio.run(
        maybe_tool_first_protected_answer(
            ctx,
            normalized=str(ctx.request.message).casefold(),
            preview={},
            memory=OperationalMemory(),
            deps=deps,
        )
    )

    assert answer is not None
    assert answer.reason == "specialist_supervisor_tool_first:attendance_summary_aggregate"
    assert "Lucas Oliveira" in answer.message_text
    assert "Ana Oliveira" in answer.message_text
    assert "Quem exige maior atencao agora: Lucas Oliveira." in answer.message_text


def test_operational_memory_resumes_upcoming_assessments_student_selection() -> None:
    async def _fetch_upcoming(*_args, **_kwargs):
        return {
            'student': {'student_id': 'lucas-id', 'full_name': 'Lucas Oliveira'},
            'summary': {
                'assessments': [
                    {'subject_name': 'Historia', 'item_title': 'B2', 'due_date': '2026-04-10'},
                    {'subject_name': 'Fisica', 'item_title': 'B2', 'due_date': '2026-04-11'},
                ]
            },
        }

    ctx = SimpleNamespace(
        request=SimpleNamespace(
            user=SimpleNamespace(authenticated=True),
            message='do lucas',
        ),
        actor=None,
        operational_memory=OperationalMemory(
            active_domain='academic',
            active_topic='upcoming_assessments',
            active_subject='Historia',
            pending_kind='upcoming_assessments_student_selection',
        ),
    )
    deps = OperationalMemoryDeps(
        normalize_text=lambda value: str(value or '').casefold(),
        looks_like_public_doc_bundle_request=lambda _message: False,
        is_student_name_only_followup=lambda *_args, **_kwargs: 'Lucas Oliveira',
        effective_multi_intent_domains=lambda *_args, **_kwargs: [],
        subject_hint_from_text=lambda _message: None,
        looks_like_subject_followup=lambda _message: False,
        looks_like_student_pronoun_followup=lambda _message: False,
        student_hint_from_message=lambda *_args, **_kwargs: None,
        fetch_academic_summary_payload=lambda *_args, **_kwargs: None,
        fetch_financial_summary_payload=lambda *_args, **_kwargs: None,
        fetch_upcoming_assessments_payload=_fetch_upcoming,
        build_academic_finance_combo_payload=lambda **_kwargs: None,
        build_grade_requirement_answer=lambda **_kwargs: None,
        compose_academic_risk_answer=lambda _summary: '',
        compose_named_subject_grade_answer=lambda *_args, **_kwargs: None,
        compose_upcoming_assessments_lines=lambda summary: [
            f"- {item['subject_name']} - {item['item_title']}: {item['due_date']}" for item in summary.get('assessments', [])
        ] or ['- Nao encontrei proximas avaliacoes registradas neste recorte.'],
        safe_excerpt=lambda text, **_kwargs: text,
        looks_like_academic_risk_followup=lambda _message: False,
        looks_like_other_student_followup=lambda _message: False,
        other_linked_student=lambda *_args, **_kwargs: None,
        compose_admin_status_answer=lambda _summary: '',
        compose_named_grade_answer=lambda _summary: '',
        compose_finance_installments_answer=lambda _summary: '',
    )

    answer = asyncio.run(maybe_operational_memory_follow_up_answer(ctx, deps=deps))
    assert answer is not None
    assert 'Proximas avaliacoes de Lucas Oliveira' in answer.message_text
    assert 'Historia - B2' in answer.message_text
    assert 'Fisica - B2' not in answer.message_text


def test_specialist_fast_path_handles_academic_risk_recut_for_named_student() -> None:
    async def _fetch_academic_summary_payload(_ctx, *, student_name_hint=None, **_kwargs):
        assert student_name_hint == 'Ana Oliveira'
        return {
            'summary': {
                'student_name': 'Ana Oliveira',
            }
        }

    ctx = SimpleNamespace(
        request=SimpleNamespace(
            user=SimpleNamespace(authenticated=True),
            message='Quero o mesmo panorama, mas agora isolando a Ana e os pontos academicos que mais preocupam.',
        ),
        actor={'linked_students': [{'full_name': 'Ana Oliveira'}]},
        conversation_context={},
    )
    deps = ResolvedIntentDeps(
        normalize_text=lambda value: str(value or '').casefold(),
        looks_like_subject_followup=lambda _message: False,
        looks_like_academic_risk_followup=lambda _message: True,
        looks_like_family_finance_aggregate_query=lambda _message: False,
        looks_like_family_attendance_aggregate_query=lambda _message: False,
        fetch_academic_summary_payload=_fetch_academic_summary_payload,
        fetch_financial_summary_payload=lambda *_args, **_kwargs: None,
        fetch_upcoming_assessments_payload=lambda *_args, **_kwargs: None,
        resolved_academic_target_name=lambda *_args, **_kwargs: 'Ana Oliveira',
        needs_specific_academic_student_clarification=lambda *_args, **_kwargs: False,
        build_academic_student_selection_clarify=lambda *_args, **_kwargs: None,
        compose_academic_risk_answer=lambda summary: f"Os pontos de maior risco academico de {summary['student_name']} hoje sao:\\n- Fisica: media parcial 6,4",
        compose_named_subject_grade_answer=lambda *_args, **_kwargs: None,
        compose_named_grade_answer=lambda _summary: '',
        compose_named_attendance_answer=lambda *_args, **_kwargs: None,
        compose_academic_snapshot_lines=lambda _summary: [],
        compose_academic_aggregate_answer=lambda _summaries: '',
        compose_finance_aggregate_answer=lambda _summaries: '',
        compose_finance_installments_answer=lambda _summary: '',
        linked_students=lambda *_args, **_kwargs: [],
        safe_excerpt=lambda text, **_kwargs: text,
        subject_hint_from_text=lambda _message: None,
        recent_subject_from_context=lambda *_args, **_kwargs: None,
        subject_code_from_hint=lambda *_args, **_kwargs: (None, None),
        student_hint_from_message=lambda *_args, **_kwargs: 'Ana Oliveira',
        is_student_name_only_followup=lambda *_args, **_kwargs: None,
        compose_upcoming_assessments_lines=lambda _summary: [],
    )

    answer = asyncio.run(maybe_academic_grade_fast_path_answer(ctx, deps=deps))

    assert answer is not None
    assert answer.reason == 'specialist_supervisor_fast_path:academic_risk'
    assert 'Ana Oliveira' in answer.message_text


def test_operational_memory_meta_repair_explains_previous_subject() -> None:
    ctx = SimpleNamespace(
        request=SimpleNamespace(
            user=SimpleNamespace(authenticated=True),
            message='Essa resposta era sobre o que entao?',
        ),
        actor=None,
        operational_memory=OperationalMemory(
            active_domain='academic',
            active_student_name='Lucas Oliveira',
            active_subject='Historia',
        ),
    )
    deps = OperationalMemoryDeps(
        normalize_text=lambda value: str(value or '').casefold(),
        looks_like_public_doc_bundle_request=lambda _message: False,
        is_student_name_only_followup=lambda *_args, **_kwargs: None,
        effective_multi_intent_domains=lambda *_args, **_kwargs: [],
        subject_hint_from_text=lambda _message: None,
        looks_like_subject_followup=lambda _message: False,
        looks_like_student_pronoun_followup=lambda _message: False,
        student_hint_from_message=lambda *_args, **_kwargs: None,
        fetch_academic_summary_payload=lambda *_args, **_kwargs: None,
        fetch_financial_summary_payload=lambda *_args, **_kwargs: None,
        fetch_upcoming_assessments_payload=lambda *_args, **_kwargs: None,
        build_academic_finance_combo_payload=lambda *_args, **_kwargs: None,
        build_grade_requirement_answer=lambda *_args, **_kwargs: None,
        compose_academic_risk_answer=lambda _summary: None,
        compose_named_subject_grade_answer=lambda *_args, **_kwargs: None,
        compose_upcoming_assessments_lines=lambda _summary: [],
        safe_excerpt=lambda text, **_kwargs: text,
        looks_like_academic_risk_followup=lambda _message: False,
        looks_like_other_student_followup=lambda _message: False,
        other_linked_student=lambda *_args, **_kwargs: None,
        compose_admin_status_answer=lambda _summary: '',
        compose_named_grade_answer=lambda _summary: '',
        compose_finance_installments_answer=lambda _summary: '',
    )

    answer = asyncio.run(maybe_operational_memory_follow_up_answer(ctx, deps=deps))

    assert answer is not None
    assert answer.reason == 'specialist_supervisor_memory:meta_repair'
    assert 'Lucas Oliveira' in answer.message_text
    assert 'Historia' in answer.message_text


def test_operational_memory_subject_followup_reports_missing_named_subject() -> None:
    async def _fetch_academic_summary_payload(_ctx, *, student_name_hint=None, **_kwargs):
        assert student_name_hint == 'Lucas Oliveira'
        return {
            'student': {'full_name': 'Lucas Oliveira'},
            'summary': {'student_name': 'Lucas Oliveira', 'grades': []},
        }

    ctx = SimpleNamespace(
        request=SimpleNamespace(
            user=SimpleNamespace(authenticated=True),
            message='E as notas de danca?',
        ),
        actor=None,
        operational_memory=OperationalMemory(
            active_domain='academic',
            active_student_name='Lucas Oliveira',
            active_subject='Historia',
        ),
    )
    deps = OperationalMemoryDeps(
        normalize_text=lambda value: str(value or '').casefold(),
        looks_like_public_doc_bundle_request=lambda _message: False,
        is_student_name_only_followup=lambda *_args, **_kwargs: None,
        effective_multi_intent_domains=lambda *_args, **_kwargs: [],
        subject_hint_from_text=lambda _message: 'Danca',
        looks_like_subject_followup=lambda _message: True,
        looks_like_student_pronoun_followup=lambda _message: False,
        student_hint_from_message=lambda *_args, **_kwargs: None,
        fetch_academic_summary_payload=_fetch_academic_summary_payload,
        fetch_financial_summary_payload=lambda *_args, **_kwargs: None,
        fetch_upcoming_assessments_payload=lambda *_args, **_kwargs: None,
        build_academic_finance_combo_payload=lambda *_args, **_kwargs: None,
        build_grade_requirement_answer=lambda *_args, **_kwargs: None,
        compose_academic_risk_answer=lambda _summary: None,
        compose_named_subject_grade_answer=lambda *_args, **_kwargs: None,
        compose_upcoming_assessments_lines=lambda _summary: [],
        safe_excerpt=lambda text, **_kwargs: text,
        looks_like_academic_risk_followup=lambda _message: False,
        looks_like_other_student_followup=lambda _message: False,
        other_linked_student=lambda *_args, **_kwargs: None,
        compose_admin_status_answer=lambda _summary: '',
        compose_named_grade_answer=lambda _summary: 'Panorama academico anterior',
        compose_finance_installments_answer=lambda _summary: '',
    )

    answer = asyncio.run(maybe_operational_memory_follow_up_answer(ctx, deps=deps))

    assert answer is not None
    assert answer.reason == 'specialist_supervisor_memory:subject_followup'
    assert 'nao encontrei notas de Lucas Oliveira em Danca' in answer.message_text


def test_operational_memory_meta_repair_does_not_trigger_on_subject_correction_phrase() -> None:
    deps = OperationalMemoryDeps(
        normalize_text=lambda value: str(value or '').casefold(),
        looks_like_public_doc_bundle_request=lambda _message: False,
        is_student_name_only_followup=lambda *_args, **_kwargs: None,
        effective_multi_intent_domains=lambda *_args, **_kwargs: [],
        subject_hint_from_text=lambda _message: 'Danca',
        looks_like_subject_followup=lambda _message: True,
        looks_like_student_pronoun_followup=lambda _message: False,
        student_hint_from_message=lambda *_args, **_kwargs: None,
        fetch_academic_summary_payload=lambda *_args, **_kwargs: None,
        fetch_financial_summary_payload=lambda *_args, **_kwargs: None,
        fetch_upcoming_assessments_payload=lambda *_args, **_kwargs: None,
        build_academic_finance_combo_payload=lambda *_args, **_kwargs: None,
        build_grade_requirement_answer=lambda *_args, **_kwargs: None,
        compose_academic_risk_answer=lambda _summary: None,
        compose_named_subject_grade_answer=lambda *_args, **_kwargs: None,
        compose_upcoming_assessments_lines=lambda _summary: [],
        safe_excerpt=lambda text, **_kwargs: text,
        looks_like_academic_risk_followup=lambda _message: False,
        looks_like_other_student_followup=lambda _message: False,
        other_linked_student=lambda *_args, **_kwargs: None,
        compose_admin_status_answer=lambda _summary: '',
        compose_named_grade_answer=lambda _summary: 'Panorama academico anterior',
        compose_finance_installments_answer=lambda _summary: '',
    )
    assert _looks_like_meta_repair_question(
        'Nao e fisica, e aulas de danca. Quero saber se isso existe na base.',
        deps=deps,
    ) is False


def test_operational_memory_meta_repair_does_not_trigger_on_attendance_why_question() -> None:
    deps = OperationalMemoryDeps(
        normalize_text=lambda value: str(value or '').casefold(),
        looks_like_public_doc_bundle_request=lambda _message: False,
        is_student_name_only_followup=lambda *_args, **_kwargs: None,
        effective_multi_intent_domains=lambda *_args, **_kwargs: [],
        subject_hint_from_text=lambda _message: None,
        looks_like_subject_followup=lambda _message: False,
        looks_like_student_pronoun_followup=lambda _message: False,
        student_hint_from_message=lambda *_args, **_kwargs: None,
        fetch_academic_summary_payload=lambda *_args, **_kwargs: None,
        fetch_financial_summary_payload=lambda *_args, **_kwargs: None,
        fetch_upcoming_assessments_payload=lambda *_args, **_kwargs: None,
        build_academic_finance_combo_payload=lambda *_args, **_kwargs: None,
        build_grade_requirement_answer=lambda *_args, **_kwargs: None,
        compose_academic_risk_answer=lambda _summary: None,
        compose_named_subject_grade_answer=lambda *_args, **_kwargs: None,
        compose_upcoming_assessments_lines=lambda _summary: [],
        safe_excerpt=lambda text, **_kwargs: text,
        looks_like_academic_risk_followup=lambda _message: False,
        looks_like_other_student_followup=lambda _message: False,
        other_linked_student=lambda *_args, **_kwargs: None,
        compose_admin_status_answer=lambda _summary: '',
        compose_named_grade_answer=lambda _summary: '',
        compose_finance_installments_answer=lambda _summary: '',
    )
    assert _looks_like_meta_repair_question(
        'Continuando a analise, isole o Lucas e mostre por que a frequencia dele preocupa mais ou menos.',
        deps=deps,
    ) is False


def test_specialist_attendance_primary_alert_explains_why_frequency_concerns_student() -> None:
    answer = _compose_attendance_primary_alert(
        {
            'student_name': 'Lucas Oliveira',
            'attendance': [
                {'subject_name': 'Fisica', 'absent_count': 5, 'late_count': 3, 'present_count': 18},
                {'subject_name': 'Matematica', 'absent_count': 2, 'late_count': 1, 'present_count': 20},
            ],
        },
        deps=SimpleNamespace(normalize_text=lambda value: str(value or '').casefold()),
    )
    assert answer is not None
    assert 'Lucas Oliveira' in answer
    assert 'Fisica' in answer
    assert 'maior combinacao de faltas e atrasos' in answer
    assert 'Proximo passo:' in answer


def test_specialist_resolved_intent_attendance_primary_alert_accepts_chamam_atencao_prompt() -> None:
    async def _fetch_academic_summary_payload(_ctx, *, student_name_hint=None, **_kwargs):
        return {
            'summary': {
                'student_name': student_name_hint or 'Lucas Oliveira',
                'attendance': [
                    {'subject_name': 'Fisica', 'absent_count': 5, 'late_count': 3, 'present_count': 18},
                    {'subject_name': 'Matematica', 'absent_count': 2, 'late_count': 1, 'present_count': 20},
                ],
            }
        }

    ctx = SimpleNamespace(
        request=SimpleNamespace(
            user=SimpleNamespace(authenticated=True),
            message='No Lucas, quais faltas ou ausencias mais chamam atencao agora e como isso bate na frequencia dele?',
        ),
        actor={'students': [{'full_name': 'Lucas Oliveira'}, {'full_name': 'Ana Oliveira'}]},
        resolved_turn=ResolvedTurnIntent(
            key='academic.attendance_summary',
            domain='academic',
            subintent='attendance_summary',
            capability='academic.attendance_summary',
            access_tier='authenticated',
            confidence=0.98,
        ),
        operational_memory=OperationalMemory(active_student_name='Lucas Oliveira'),
        conversation_context={},
    )
    deps = ResolvedIntentDeps(
        normalize_text=lambda value: str(value or '').casefold(),
        looks_like_subject_followup=lambda _message: False,
        looks_like_academic_risk_followup=lambda _message: False,
        looks_like_family_finance_aggregate_query=lambda _message: False,
        looks_like_family_attendance_aggregate_query=lambda _message: False,
        fetch_academic_summary_payload=_fetch_academic_summary_payload,
        fetch_financial_summary_payload=lambda *_args, **_kwargs: None,
        fetch_upcoming_assessments_payload=lambda *_args, **_kwargs: None,
        resolved_academic_target_name=lambda *_args, **_kwargs: 'Lucas Oliveira',
        needs_specific_academic_student_clarification=lambda *_args, **_kwargs: False,
        build_academic_student_selection_clarify=lambda *_args, **_kwargs: None,
        compose_academic_risk_answer=lambda _summary: '',
        compose_named_subject_grade_answer=lambda *_args, **_kwargs: None,
        compose_named_grade_answer=lambda _summary: '',
        compose_named_attendance_answer=lambda *_args, **_kwargs: None,
        compose_academic_snapshot_lines=lambda _summary: [],
        compose_academic_aggregate_answer=lambda _summaries: '',
        compose_finance_aggregate_answer=lambda _summaries: '',
        compose_finance_installments_answer=lambda _summary: '',
        linked_students=lambda actor, **_kwargs: list(actor.get('students') or []),
        safe_excerpt=lambda text, **_kwargs: text,
        subject_hint_from_text=lambda _message: None,
        recent_subject_from_context=lambda *_args, **_kwargs: None,
        subject_code_from_hint=lambda *_args, **_kwargs: (None, None),
        student_hint_from_message=lambda *_args, **_kwargs: 'Lucas Oliveira',
        is_student_name_only_followup=lambda *_args, **_kwargs: None,
        compose_upcoming_assessments_lines=lambda _summary: [],
    )

    answer = asyncio.run(maybe_resolved_intent_answer(ctx, deps=deps))
    assert answer is not None
    assert 'principal alerta de frequencia de Lucas Oliveira' in answer.message_text
    assert 'Fisica' in answer.message_text


def test_restricted_document_denial_mentions_access_boundary() -> None:
    ctx = SimpleNamespace(
        request=SimpleNamespace(
            message='Quero o protocolo interno para viagem internacional.',
            user=SimpleNamespace(authenticated=True, scopes=[], role='guardian'),
        )
    )
    answer = asyncio.run(maybe_restricted_document_tool_first_answer(ctx, profile={}))
    assert answer is not None
    assert answer.reason == 'specialist_supervisor_tool_first:restricted_document_denied'
    assert 'acesso' in answer.message_text.casefold()


def test_restricted_document_denial_for_partial_scope_mentions_public_internal_split() -> None:
    ctx = SimpleNamespace(
        request=SimpleNamespace(
            message='Quero o protocolo interno para responsaveis com escopo parcial.',
            user=SimpleNamespace(authenticated=True, scopes=[], role='guardian'),
        )
    )
    answer = asyncio.run(maybe_restricted_document_tool_first_answer(ctx, profile={}))
    assert answer is not None
    lowered = answer.message_text.casefold()
    assert 'escopo parcial' in lowered
    assert 'orientacoes gerais' in lowered or 'orientações gerais' in answer.message_text.casefold()
    assert 'regras operacionais de permissao' in lowered or 'regras operacionais de permissão' in answer.message_text.casefold()
    assert 'proximo passo' in lowered or 'próximo passo' in answer.message_text.casefold()


def test_specialist_compose_finance_aggregate_answer_adds_layman_categories() -> None:
    answer = compose_finance_aggregate_answer(
        [
            {
                'student_name': 'Lucas Oliveira',
                'open_invoice_count': 1,
                'overdue_invoice_count': 0,
                'invoices': [],
            }
        ],
        deps=SimpleNamespace(normalize_text=lambda value: str(value or '').casefold()),
    )
    lowered = answer.casefold()
    assert 'mensalidade' in lowered
    assert 'taxa' in lowered
    assert 'atraso' in lowered
    assert 'desconto' in lowered


def test_tool_first_finance_denies_unlinked_student_name() -> None:
    async def _unused_fetch(*_args, **_kwargs):
        raise AssertionError('third-party denial should trigger before any finance fetch')

    ctx = SimpleNamespace(
        request=SimpleNamespace(
            message='Paguei parte da mensalidade do Joao e quero negociar o restante.',
            user=SimpleNamespace(authenticated=True),
        ),
        actor={'linked_students': [{'full_name': 'Lucas Oliveira'}, {'full_name': 'Ana Oliveira'}]},
        resolved_turn=None,
        conversation_context={},
    )
    deps = ToolFirstProtectedDeps(
        normalize_text=lambda value: str(value or '').casefold(),
        contains_any=lambda message, terms: any(term in str(message).casefold() for term in terms),
        looks_like_admin_finance_combo_query=lambda _message: False,
        looks_like_family_finance_aggregate_query=lambda _message: False,
        unknown_explicit_student_reference=lambda _actor, _message: 'Joao',
        student_hint_from_message=lambda *_args, **_kwargs: None,
        looks_like_student_pronoun_followup=lambda _message: False,
        fetch_financial_summary_payload=_unused_fetch,
        linked_students=lambda actor, capability='finance': list(actor.get('linked_students') or []),
        compose_finance_installments_answer=lambda _summary: '',
        compose_finance_aggregate_answer=lambda _summaries: '',
        looks_like_academic_risk_followup=lambda _message: False,
        looks_like_family_academic_aggregate_query=lambda _message: False,
        looks_like_family_attendance_aggregate_query=lambda _message: False,
        looks_like_upcoming_assessments_query=lambda _message: False,
        looks_like_attendance_timeline_query=lambda _message: False,
        subject_hint_from_text=lambda _message: None,
        looks_like_subject_followup=lambda _message: False,
        resolved_academic_target_name=lambda *_args, **_kwargs: None,
        needs_specific_academic_student_clarification=lambda *_args, **_kwargs: False,
        build_academic_student_selection_clarify=lambda *_args, **_kwargs: None,
        fetch_academic_summary_payload=_unused_fetch,
        fetch_upcoming_assessments_payload=_unused_fetch,
        fetch_attendance_timeline_payload=_unused_fetch,
        compose_academic_risk_answer=lambda _summary: '',
        compose_named_subject_grade_answer=lambda *_args, **_kwargs: None,
        compose_named_grade_answer=lambda _summary: '',
        compose_named_attendance_answer=lambda *_args, **_kwargs: None,
        compose_academic_snapshot_lines=lambda _summary: [],
        compose_academic_aggregate_answer=lambda _summaries: '',
        compose_upcoming_assessments_lines=lambda _summary: [],
        compose_attendance_timeline_lines=lambda _summary: [],
        safe_excerpt=lambda text, **_kwargs: text,
        http_get=_unused_fetch,
        compose_actor_admin_status_answer=lambda _summary: '',
        recent_student_from_context_with_memory=lambda *_args, **_kwargs: None,
        compose_admin_status_answer=lambda _summary: '',
        find_student_by_hint=lambda *_args, **_kwargs: None,
    )

    answer = asyncio.run(
        maybe_tool_first_protected_answer(
            ctx,
            normalized=str(ctx.request.message).casefold(),
            preview={'classification': {'domain': 'finance'}},
            memory=OperationalMemory(),
            deps=deps,
        )
    )

    assert answer is not None
    assert answer.reason == 'specialist_supervisor_tool_first:finance_third_party_denied'
    lowered = answer.message_text.casefold()
    assert 'o que ja aparece:' in lowered
    assert 'nao posso confirmar nem expor o financeiro' in lowered
    assert 'joao' in lowered
    assert 'lucas oliveira' in lowered
    assert 'regularize primeiro o vinculo com a secretaria' in lowered
    assert 'me diga qual deles' in lowered
    assert 'canal oficial' in lowered


def test_resolved_academic_target_name_accepts_alternate_student_name_for_short_followup() -> None:
    deps = SimpleNamespace(
        normalize_text=lambda value: str(value or '').casefold(),
        unknown_explicit_student_reference=lambda *_args, **_kwargs: None,
        student_hint_from_message=lambda *_args, **_kwargs: None,
        is_student_name_only_followup=lambda *_args, **_kwargs: None,
        looks_like_student_pronoun_followup=lambda _message: False,
        looks_like_subject_followup=lambda _message: False,
        subject_hint_from_text=lambda _message: None,
    )
    ctx = SimpleNamespace(
        request=SimpleNamespace(message='E da Ana?'),
        operational_memory=OperationalMemory(active_student_name='Lucas Oliveira'),
        actor=None,
    )
    resolved = SimpleNamespace(referenced_student_name=None, alternate_student_name='Ana Oliveira')
    assert resolved_academic_target_name(ctx, resolved=resolved, deps=deps) == 'Ana Oliveira'


def test_academic_risk_followup_detects_pontos_que_mais_preocupam() -> None:
    assert looks_like_academic_risk_followup(
        'Quero isolar a Ana e os pontos academicos que mais preocupam.',
        deps=SimpleNamespace(normalize_text=lambda value: str(value or '').casefold()),
    )


def test_academic_risk_followup_detects_componentes_merecem_mais_atencao() -> None:
    assert looks_like_academic_risk_followup(
        'Fique apenas com a Ana e diga quais componentes merecem mais atencao agora.',
        deps=SimpleNamespace(normalize_text=lambda value: str(value or '').casefold()),
    )


def test_academic_risk_followup_detects_acende_mais_alerta_prompt() -> None:
    assert looks_like_academic_risk_followup(
        'Sem repetir o Lucas, corta so para a Ana e me diga qual componente dela acende mais alerta agora.',
        deps=SimpleNamespace(normalize_text=lambda value: str(value or '').casefold()),
    )


def test_academic_risk_followup_detects_disciplina_preocupa_mais_prompt() -> None:
    assert looks_like_academic_risk_followup(
        'e qual disciplina preocupa mais?',
        deps=SimpleNamespace(normalize_text=lambda value: str(value or '').casefold()),
    )


def test_compose_academic_risk_answer_mentions_concern_and_lowest_grade() -> None:
    summary = {
        'student_name': 'Lucas Oliveira',
        'grades': [
            {'subject_name': 'Fisica', 'score': '5.9'},
            {'subject_name': 'Matematica', 'score': '7.7'},
            {'subject_name': 'Portugues', 'score': '8.3'},
        ],
    }
    text = compose_academic_risk_answer(
        summary,
        deps=SimpleNamespace(
            normalize_text=lambda value: str(value or '').casefold(),
            subject_code_from_hint=lambda *_args, **_kwargs: (None, None),
        ),
    )
    assert text is not None
    lowered = text.casefold()
    assert 'preocupam academicamente' in lowered
    assert 'menor nota parcial' in lowered
    assert 'fisica' in lowered


def test_student_hint_from_message_prefers_focus_marked_student() -> None:
    deps = StudentContextDeps(
        normalize_text=lambda value: str(value or '').casefold(),
        linked_students=lambda _actor, capability='academic': [
            {'student_id': 'stu-lucas', 'full_name': 'Lucas Oliveira'},
            {'student_id': 'stu-ana', 'full_name': 'Ana Oliveira'},
        ],
        http_get=lambda **kwargs: None,
    )

    assert (
        student_hint_from_message(
            {'linked_students': [{'student_id': 'stu-lucas', 'full_name': 'Lucas Oliveira'}, {'student_id': 'stu-ana', 'full_name': 'Ana Oliveira'}]},
            'Sem repetir o Lucas, corta so para a Ana e me diga qual componente dela acende mais alerta agora.',
            deps=deps,
        )
        == 'Ana Oliveira'
    )


def test_resolved_academic_target_name_prefers_explicit_student_over_alternate_memory() -> None:
    deps = SimpleNamespace(
        normalize_text=lambda value: str(value or '').casefold(),
        student_hint_from_message=lambda _actor, _message: 'Ana Oliveira',
        is_student_name_only_followup=lambda _actor, _message: None,
        unknown_explicit_student_reference=lambda _actor, _message: None,
        looks_like_student_pronoun_followup=lambda _message: False,
        looks_like_subject_followup=lambda _message: False,
        subject_hint_from_text=lambda _message: None,
    )
    ctx = SimpleNamespace(
        request=SimpleNamespace(message='Sem repetir o Lucas, corta so para a Ana e me diga qual componente dela acende mais alerta agora.'),
        operational_memory=OperationalMemory(active_student_name='Lucas Oliveira', alternate_student_name='Lucas Oliveira'),
        actor=None,
    )
    resolved = SimpleNamespace(referenced_student_name=None, alternate_student_name='Lucas Oliveira')

    assert resolved_academic_target_name(ctx, resolved=resolved, deps=deps) == 'Ana Oliveira'


def test_specialist_family_attendance_aggregate_query_rejects_academic_components_followup() -> None:
    assert looks_like_family_attendance_aggregate_query(
        'Sem sair do escopo do projeto, depois do panorama dos meus filhos, fique apenas com a Ana e diga quais componentes merecem mais atencao agora.',
        deps=SimpleNamespace(normalize_text=lambda value: str(value or '').casefold()),
    ) is False


def test_resolved_intent_skips_public_pricing_query() -> None:
    ctx = SimpleNamespace(
        request=SimpleNamespace(
            user=SimpleNamespace(authenticated=True),
            message='Qual a mensalidade do ensino medio?',
        ),
        actor=None,
        conversation_context={'recent_messages': []},
        resolved_turn=SimpleNamespace(domain='finance', capability='finance.student_summary', confidence=0.97),
    )
    deps = ResolvedIntentDeps(
        normalize_text=lambda value: str(value or '').casefold(),
        looks_like_subject_followup=lambda _message: False,
        looks_like_academic_risk_followup=lambda _message: False,
        looks_like_family_finance_aggregate_query=lambda _message: False,
        looks_like_family_attendance_aggregate_query=lambda _message: False,
        fetch_academic_summary_payload=lambda *_args, **_kwargs: None,
        fetch_financial_summary_payload=lambda *_args, **_kwargs: None,
        fetch_upcoming_assessments_payload=lambda *_args, **_kwargs: None,
        resolved_academic_target_name=lambda *_args, **_kwargs: None,
        needs_specific_academic_student_clarification=lambda *_args, **_kwargs: False,
        build_academic_student_selection_clarify=lambda *_args, **_kwargs: None,
        compose_academic_risk_answer=lambda _summary: '',
        compose_named_subject_grade_answer=lambda *_args, **_kwargs: None,
        compose_named_grade_answer=lambda _summary: '',
        compose_named_attendance_answer=lambda *_args, **_kwargs: None,
        compose_academic_snapshot_lines=lambda _summary: [],
        compose_academic_aggregate_answer=lambda _summaries: '',
        compose_finance_aggregate_answer=lambda _summaries: '',
        compose_finance_installments_answer=lambda _summary: '',
        linked_students=lambda *_args, **_kwargs: [],
        safe_excerpt=lambda text, **_kwargs: text,
        subject_hint_from_text=lambda _message: None,
        recent_subject_from_context=lambda *_args, **_kwargs: None,
        subject_code_from_hint=lambda *_args, **_kwargs: (None, None),
        student_hint_from_message=lambda *_args, **_kwargs: None,
        is_student_name_only_followup=lambda *_args, **_kwargs: None,
        compose_upcoming_assessments_lines=lambda _summary: [],
    )

    answer = asyncio.run(maybe_resolved_intent_answer(ctx, deps=deps))
    assert answer is None


def test_resolved_intent_student_grades_defers_when_prompt_is_family_attendance_aggregate() -> None:
    ctx = SimpleNamespace(
        request=SimpleNamespace(
            user=SimpleNamespace(authenticated=True),
            message='Me de um panorama de faltas e frequencia dos meus filhos, apontando quem exige maior atencao agora.',
        ),
        actor={'students': [{'full_name': 'Lucas Oliveira'}, {'full_name': 'Ana Oliveira'}]},
        conversation_context={},
        resolved_turn=ResolvedTurnIntent(
            key='academic.student_grades',
            domain='academic',
            subintent='student_grades',
            capability='academic.student_grades',
            access_tier='authenticated',
            confidence=0.98,
        ),
        operational_memory=OperationalMemory(),
    )
    deps = ResolvedIntentDeps(
        normalize_text=lambda value: str(value or '').casefold(),
        looks_like_subject_followup=lambda _message: False,
        looks_like_academic_risk_followup=lambda _message: False,
        looks_like_family_finance_aggregate_query=lambda _message: False,
        looks_like_family_attendance_aggregate_query=lambda _message: True,
        fetch_academic_summary_payload=lambda *_args, **_kwargs: None,
        fetch_financial_summary_payload=lambda *_args, **_kwargs: None,
        fetch_upcoming_assessments_payload=lambda *_args, **_kwargs: None,
        resolved_academic_target_name=lambda *_args, **_kwargs: None,
        needs_specific_academic_student_clarification=lambda *_args, **_kwargs: False,
        build_academic_student_selection_clarify=lambda *_args, **_kwargs: None,
        compose_academic_risk_answer=lambda _summary: '',
        compose_named_subject_grade_answer=lambda *_args, **_kwargs: None,
        compose_named_grade_answer=lambda _summary: '',
        compose_named_attendance_answer=lambda *_args, **_kwargs: None,
        compose_academic_snapshot_lines=lambda _summary: [],
        compose_academic_aggregate_answer=lambda _summaries: '',
        compose_finance_aggregate_answer=lambda _summaries: '',
        compose_finance_installments_answer=lambda _summary: '',
        linked_students=lambda *_args, **_kwargs: [],
        safe_excerpt=lambda text, **_kwargs: text,
        subject_hint_from_text=lambda _message: None,
        recent_subject_from_context=lambda *_args, **_kwargs: None,
        subject_code_from_hint=lambda *_args, **_kwargs: (None, None),
        student_hint_from_message=lambda *_args, **_kwargs: None,
        is_student_name_only_followup=lambda *_args, **_kwargs: None,
        compose_upcoming_assessments_lines=lambda _summary: [],
    )

    answer = asyncio.run(maybe_resolved_intent_answer(ctx, deps=deps))
    assert answer is None


def test_fast_path_public_pricing_follow_up_keeps_recent_segment() -> None:
    ctx = SimpleNamespace(
        request=SimpleNamespace(
            user=SimpleNamespace(authenticated=False),
            message='E para 20 filhos?',
        ),
        actor=None,
        school_profile={
            'tuition_reference': [
                {
                    'segment': 'Ensino Medio',
                    'shift_label': 'Manha',
                    'monthly_amount': '1450.00',
                    'enrollment_fee': '650.00',
                    'notes': 'Valor publico de referencia.',
                },
                {
                    'segment': 'Ensino Fundamental II',
                    'shift_label': 'Manha',
                    'monthly_amount': '980.00',
                    'enrollment_fee': '350.00',
                    'notes': 'Valor publico alternativo.',
                },
            ]
        },
        conversation_context={
            'recent_messages': [
                {'sender_type': 'user', 'content': 'Qual a mensalidade do ensino medio?'},
                {'sender_type': 'assistant', 'content': '...'},
                {'sender_type': 'user', 'content': 'Quanto seria a matricula para 20 filhos no ensino medio?'},
            ]
        },
    )

    def _normalized_recent_user_messages(conversation_context: dict[str, object] | None) -> list[str]:
        messages = conversation_context.get('recent_messages') if isinstance(conversation_context, dict) else []
        return [
            str(item.get('content') or '').casefold()
            for item in messages
            if isinstance(item, dict) and item.get('sender_type') == 'user'
        ]

    deps = FastPathDeps(
        normalize_text=lambda value: str(value or '').casefold(),
        normalized_recent_user_messages=_normalized_recent_user_messages,
        is_simple_greeting=lambda _message: False,
        is_auth_guidance_query=lambda _message: False,
        compose_auth_guidance_answer=lambda _profile: '',
        linked_students=lambda *_args, **_kwargs: [],
        compose_authenticated_scope_answer=lambda _actor: '',
        is_assistant_identity_query=lambda _message: False,
        compose_assistant_identity_answer=lambda _profile: '',
        school_name=lambda _profile: 'Colegio Horizonte',
        safe_excerpt=lambda text, **_kwargs: text,
        format_brl=lambda value: f"R$ {float(value):,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'),
        hypothetical_children_quantity=lambda message: 20 if '20' in str(message) else None,
        pricing_projection=lambda profile, quantity, segment_hint=None: {
            'quantity': quantity,
            'segment': segment_hint or 'Ensino Medio',
            'shift_label': 'Manha',
            'per_student_enrollment_fee': '650.00',
            'per_student_monthly_amount': '1450.00',
            'total_enrollment_fee': '13000.00',
            'total_monthly_amount': '29000.00',
            'notes': 'Valor publico de referencia.',
        },
        compose_public_bolsas_and_processes=lambda _profile: None,
    )

    answer = build_fast_path_answer(ctx, deps)
    assert answer is not None
    assert answer.reason == 'specialist_supervisor_fast_path:pricing_projection'
    assert 'Ensino Medio' in answer.message_text
    assert 'R$ 13.000,00' in answer.message_text


def test_fast_path_handles_public_multi_intent_contacts_and_pricing() -> None:
    ctx = SimpleNamespace(
        request=SimpleNamespace(
            user=SimpleNamespace(authenticated=False),
            message='Quero os contatos de secretaria, financeiro e direcao, junto com mensalidade e bolsa para 3 filhos no ensino medio.',
        ),
        actor=None,
        school_profile={
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
                {'service_key': 'atendimento_admissoes', 'request_channel': 'WhatsApp comercial'},
                {'service_key': 'financeiro_escolar', 'request_channel': 'Portal autenticado'},
                {'service_key': 'solicitacao_direcao', 'request_channel': 'Protocolo institucional'},
            ],
            'leadership_team': [
                {'title': 'Diretora geral', 'name': 'Helena Martins', 'contact_channel': 'direcao@colegiohorizonte.edu.br'},
            ],
            'tuition_reference': [
                {
                    'segment': 'Ensino Medio',
                    'shift_label': 'Manha',
                    'monthly_amount': '1450.00',
                    'enrollment_fee': '350.00',
                    'notes': 'Valor publico de referencia.',
                }
            ],
        },
        conversation_context={'recent_messages': []},
    )

    deps = FastPathDeps(
        normalize_text=lambda value: str(value or '').casefold(),
        normalized_recent_user_messages=lambda _context: [],
        is_simple_greeting=lambda _message: False,
        is_auth_guidance_query=lambda _message: False,
        compose_auth_guidance_answer=lambda _profile: '',
        linked_students=lambda *_args, **_kwargs: [],
        compose_authenticated_scope_answer=lambda _actor: '',
        is_assistant_identity_query=lambda _message: False,
        compose_assistant_identity_answer=lambda _profile: '',
        school_name=lambda _profile: 'Colegio Horizonte',
        safe_excerpt=lambda text, **_kwargs: text,
        format_brl=lambda value: f"R$ {float(value):,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'),
        hypothetical_children_quantity=lambda message: 3 if '3' in str(message) else None,
        pricing_projection=lambda profile, quantity, segment_hint=None: {
            'quantity': quantity,
            'segment': segment_hint or 'Ensino Medio',
            'shift_label': 'Manha',
            'per_student_enrollment_fee': '350.00',
            'per_student_monthly_amount': '1450.00',
            'total_enrollment_fee': '1050.00',
            'total_monthly_amount': '4350.00',
            'notes': 'Valor publico de referencia.',
        },
        compose_public_bolsas_and_processes=lambda _profile: 'Bolsas e descontos comerciais podem ser analisados pela politica comercial publica.',
    )

    answer = build_fast_path_answer(ctx, deps)

    assert answer is not None
    assert answer.reason == 'specialist_supervisor_fast_path:public_multi_intent'
    assert 'Canais gerais da escola' in answer.message_text
    assert 'Valores publicos e simulacao' in answer.message_text


def test_fast_path_handles_access_scope_followup_per_student_without_strict_recent_marker() -> None:
    ctx = SimpleNamespace(
        request=SimpleNamespace(
            user=SimpleNamespace(authenticated=True),
            message='E o que eu consigo ver sobre cada um?',
        ),
        actor={'actor_type': 'guardian'},
        school_profile={},
        conversation_context={
            'recent_messages': [
                {'sender_type': 'user', 'content': 'Quais alunos estao vinculados a esta conta?'},
            ]
        },
    )

    students = [
        {'full_name': 'Lucas Oliveira', 'can_view_academic': True, 'can_view_finance': True},
        {'full_name': 'Ana Oliveira', 'can_view_academic': True, 'can_view_finance': True},
    ]

    deps = FastPathDeps(
        normalize_text=lambda value: str(value or '').casefold(),
        normalized_recent_user_messages=lambda _context: ['quais alunos estao vinculados a esta conta'],
        is_simple_greeting=lambda _message: False,
        is_auth_guidance_query=lambda _message: False,
        compose_auth_guidance_answer=lambda _profile: '',
        linked_students=lambda *_args, **_kwargs: students,
        compose_authenticated_scope_answer=lambda _actor: 'fallback',
        is_assistant_identity_query=lambda _message: False,
        compose_assistant_identity_answer=lambda _profile: '',
        school_name=lambda _profile: 'Colegio Horizonte',
        safe_excerpt=lambda text, **_kwargs: text,
        format_brl=lambda value: str(value),
        hypothetical_children_quantity=lambda _message: None,
        pricing_projection=lambda *_args, **_kwargs: {},
        compose_public_bolsas_and_processes=lambda _profile: None,
    )

    answer = build_fast_path_answer(ctx, deps)

    assert answer is not None
    assert answer.reason == 'specialist_supervisor_fast_path:access_scope_followup'
    assert 'Por aluno vinculado' in answer.message_text
    assert 'Lucas Oliveira' in answer.message_text
    assert 'Ana Oliveira' in answer.message_text


def test_fast_path_handles_public_capabilities_menu() -> None:
    ctx = SimpleNamespace(
        request=SimpleNamespace(
            user=SimpleNamespace(authenticated=False),
            message='Quais opcoes de assuntos eu tenho aqui?',
        ),
        actor=None,
        school_profile={
            'school_name': 'Colegio Horizonte',
            'assistant_capabilities': {
                'public_topics': ['matricula, secretaria, financeiro e visitas'],
                'protected_topics': ['notas, faltas e pagamentos'],
            },
        },
        conversation_context={'recent_messages': []},
    )

    deps = FastPathDeps(
        normalize_text=lambda value: str(value or '').casefold(),
        normalized_recent_user_messages=lambda _context: [],
        is_simple_greeting=lambda _message: False,
        is_auth_guidance_query=lambda _message: False,
        compose_auth_guidance_answer=lambda _profile: '',
        linked_students=lambda *_args, **_kwargs: [],
        compose_authenticated_scope_answer=lambda _actor: '',
        is_assistant_identity_query=lambda _message: False,
        compose_assistant_identity_answer=lambda _profile: '',
        school_name=lambda _profile: 'Colegio Horizonte',
        safe_excerpt=lambda text, **_kwargs: text,
        format_brl=lambda value: str(value),
        hypothetical_children_quantity=lambda _message: None,
        pricing_projection=lambda *_args, **_kwargs: {},
        compose_public_bolsas_and_processes=lambda _profile: None,
    )

    answer = build_fast_path_answer(ctx, deps)

    assert answer is not None
    assert answer.reason == 'specialist_supervisor_fast_path:capabilities'
    lowered = answer.message_text.lower()
    assert 'matricula' in lowered
    assert 'secretaria' in lowered
    assert 'financeiro' in lowered


def test_fast_path_handles_public_admissions_opening_date() -> None:
    ctx = SimpleNamespace(
        request=SimpleNamespace(
            user=SimpleNamespace(authenticated=False),
            message='Quando abre a matricula de 2026?',
        ),
        actor=None,
        school_profile={
            'school_name': 'Colegio Horizonte',
            'public_timeline': [
                {
                    'topic_key': 'admissions_opening_2026',
                    'summary': 'O ciclo publico de matricula para 2026 foi aberto em 6 de outubro de 2025.',
                    'event_date': '2025-10-06',
                }
            ],
        },
        conversation_context={'recent_messages': []},
    )

    deps = FastPathDeps(
        normalize_text=lambda value: str(value or '').casefold(),
        normalized_recent_user_messages=lambda _context: [],
        is_simple_greeting=lambda _message: False,
        is_auth_guidance_query=lambda _message: False,
        compose_auth_guidance_answer=lambda _profile: '',
        linked_students=lambda *_args, **_kwargs: [],
        compose_authenticated_scope_answer=lambda _actor: '',
        is_assistant_identity_query=lambda _message: False,
        compose_assistant_identity_answer=lambda _profile: '',
        school_name=lambda _profile: 'Colegio Horizonte',
        safe_excerpt=lambda text, **_kwargs: text,
        format_brl=lambda value: str(value),
        hypothetical_children_quantity=lambda _message: None,
        pricing_projection=lambda *_args, **_kwargs: {},
        compose_public_bolsas_and_processes=lambda _profile: None,
    )

    answer = build_fast_path_answer(ctx, deps)

    assert answer is not None
    assert answer.reason == 'specialist_supervisor_fast_path:admissions_opening'
    assert '6 de outubro de 2025' in answer.message_text


def test_fast_path_handles_visit_reschedule_followup_with_protocol_guidance() -> None:
    ctx = SimpleNamespace(
        request=SimpleNamespace(
            user=SimpleNamespace(authenticated=False),
            message='Se eu precisar remarcar, como faco?',
        ),
        actor=None,
        school_profile={
            'service_catalog': [
                {
                    'service_key': 'visita_institucional',
                    'request_channel': 'bot, admissions ou whatsapp comercial',
                    'typical_eta': 'confirmacao em ate 1 dia util',
                }
            ],
        },
        conversation_context={'recent_messages': []},
    )

    deps = FastPathDeps(
        normalize_text=lambda value: str(value or '').casefold(),
        normalized_recent_user_messages=lambda _context: ['quero agendar uma visita na quinta a tarde'],
        is_simple_greeting=lambda _message: False,
        is_auth_guidance_query=lambda _message: False,
        compose_auth_guidance_answer=lambda _profile: '',
        linked_students=lambda *_args, **_kwargs: [],
        compose_authenticated_scope_answer=lambda _actor: '',
        is_assistant_identity_query=lambda _message: False,
        compose_assistant_identity_answer=lambda _profile: '',
        school_name=lambda _profile: 'Colegio Horizonte',
        safe_excerpt=lambda text, **_kwargs: text,
        format_brl=lambda value: str(value),
        hypothetical_children_quantity=lambda _message: None,
        pricing_projection=lambda *_args, **_kwargs: {},
        compose_public_bolsas_and_processes=lambda _profile: None,
    )

    answer = build_fast_path_answer(ctx, deps)

    assert answer is not None
    assert answer.reason == 'specialist_supervisor_fast_path:visit_reschedule'
    lowered = answer.message_text.lower()
    assert 'remarcar a visita' in lowered
    assert 'protocolo' in lowered


def test_fast_path_handles_bullying_service_routing() -> None:
    ctx = SimpleNamespace(
        request=SimpleNamespace(
            user=SimpleNamespace(authenticated=False),
            message='Como reporto um bullying?',
        ),
        actor=None,
        school_profile={
            'service_catalog': [
                {
                    'service_key': 'orientacao_educacional',
                    'service_name': 'Orientacao educacional',
                    'request_channel': 'bot, orientacao educacional ou secretaria',
                    'typical_eta': 'retorno em ate 1 dia util',
                }
            ],
        },
        conversation_context={'recent_messages': []},
    )

    deps = FastPathDeps(
        normalize_text=lambda value: str(value or '').casefold(),
        normalized_recent_user_messages=lambda _context: [],
        is_simple_greeting=lambda _message: False,
        is_auth_guidance_query=lambda _message: False,
        compose_auth_guidance_answer=lambda _profile: '',
        linked_students=lambda *_args, **_kwargs: [],
        compose_authenticated_scope_answer=lambda _actor: '',
        is_assistant_identity_query=lambda _message: False,
        compose_assistant_identity_answer=lambda _profile: '',
        school_name=lambda _profile: 'Colegio Horizonte',
        safe_excerpt=lambda text, **_kwargs: text,
        format_brl=lambda value: str(value),
        hypothetical_children_quantity=lambda _message: None,
        pricing_projection=lambda *_args, **_kwargs: {},
        compose_public_bolsas_and_processes=lambda _profile: None,
    )

    answer = build_fast_path_answer(ctx, deps)

    assert answer is not None
    assert answer.reason == 'specialist_supervisor_fast_path:service_routing'
    lowered = answer.message_text.lower()
    assert 'orientacao educacional' in lowered
    assert 'bot' in lowered


def test_human_handoff_request_does_not_steal_role_comparison_prompt() -> None:
    assert not _looks_like_human_handoff_request(
        'Qual a diferenca entre falar com secretaria, coordenacao e orientacao educacional?'
    )


def test_specialist_preflight_promotes_policy_compare_lane() -> None:
    payload = _preflight_public_doc_bundle_answer(
        {"school_name": "Colegio Horizonte"},
        'Compare o manual de regulamentos gerais com a politica de avaliacao e explique como os dois se complementam.',
    )
    assert payload is not None
    assert payload.reason == 'specialist_supervisor_preflight:policy_compare'


def test_specialist_preflight_promotes_permanence_family_support_lane() -> None:
    payload = _preflight_public_doc_bundle_answer(
        {"school_name": "Colegio Horizonte"},
        'Quais temas atravessam varios documentos publicos quando o assunto e permanencia escolar e acompanhamento da familia?',
    )
    assert payload is not None
    assert payload.reason == 'specialist_supervisor_preflight:permanence_family_support'


def test_specialist_public_lane_matches_access_scope_compare_prompt() -> None:
    prompt = 'Compare a orientacao publica e a interna sobre acessos diferentes entre responsaveis e destaque o que muda de linguagem e de acao.'
    assert match_public_canonical_lane(prompt) == 'public_bundle.access_scope_compare'


def test_specialist_family_finance_aggregate_query_rejects_third_party_partial_payment_prompt_without_family_anchor() -> None:
    deps = SimpleNamespace(normalize_text=lambda text: str(text or '').casefold())
    prompt = 'Paguei parte da mensalidade do Joao e preciso negociar o restante; o que ja aparece e qual o proximo passo?'
    assert looks_like_family_finance_aggregate_query(prompt, deps=deps) is False


def test_specialist_unknown_student_reference_skips_finance_noun_and_returns_actual_name() -> None:
    actor = {
        'linked_students': [
            {'student_id': 'lucas-id', 'full_name': 'Lucas Oliveira'},
            {'student_id': 'ana-id', 'full_name': 'Ana Oliveira'},
        ]
    }
    deps = StudentContextDeps(
        normalize_text=lambda text: str(text or '').casefold(),
        linked_students=lambda _actor, capability='academic': actor['linked_students'],
        http_get=lambda **kwargs: None,
    )
    prompt = 'Paguei parte da mensalidade do Joao e preciso negociar o restante; o que ja aparece e qual o proximo passo?'
    assert unknown_explicit_student_reference(actor, prompt, deps=deps) == 'joao'


def test_resolved_finance_summary_denies_unlinked_student_name() -> None:
    async def _fetch_financial_summary_payload(_ctx, *, student_name_hint=None, **_kwargs):
        return {"summary": {"student_name": student_name_hint or "Aluno", "open_invoice_count": 1, "overdue_invoice_count": 0}}

    ctx = SimpleNamespace(
        request=SimpleNamespace(
            user=SimpleNamespace(authenticated=True),
            message='Sou a Helena e quero ver o financeiro do Rafael.',
        ),
        actor={'students': [{'full_name': 'Lucas Oliveira'}, {'full_name': 'Ana Oliveira'}]},
        resolved_turn=ResolvedTurnIntent(
            key='finance.student_summary',
            domain='finance',
            subintent='student_summary',
            capability='finance.student_summary',
            access_tier='authenticated',
            confidence=0.99,
            referenced_student_name='Rafael',
        ),
        operational_memory=OperationalMemory(),
        conversation_context={},
    )
    deps = ResolvedIntentDeps(
        normalize_text=lambda value: str(value or '').casefold(),
        looks_like_subject_followup=lambda _message: False,
        looks_like_academic_risk_followup=lambda _message: False,
        looks_like_family_finance_aggregate_query=lambda _message: False,
        looks_like_family_attendance_aggregate_query=lambda _message: False,
        fetch_academic_summary_payload=lambda *_args, **_kwargs: None,
        fetch_financial_summary_payload=_fetch_financial_summary_payload,
        fetch_upcoming_assessments_payload=lambda *_args, **_kwargs: None,
        resolved_academic_target_name=lambda *_args, **_kwargs: None,
        needs_specific_academic_student_clarification=lambda *_args, **_kwargs: False,
        build_academic_student_selection_clarify=lambda *_args, **_kwargs: None,
        compose_academic_risk_answer=lambda _summary: '',
        compose_named_subject_grade_answer=lambda *_args, **_kwargs: None,
        compose_named_grade_answer=lambda _summary: '',
        compose_named_attendance_answer=lambda *_args, **_kwargs: '',
        compose_academic_snapshot_lines=lambda _summary: [],
        compose_academic_aggregate_answer=lambda _summaries: '',
        compose_finance_aggregate_answer=lambda _summaries: '',
        compose_finance_installments_answer=lambda _summary: '',
        linked_students=lambda actor, **_kwargs: list(actor.get('students') or []),
        safe_excerpt=lambda text, **_kwargs: text,
        subject_hint_from_text=lambda _message: None,
        recent_subject_from_context=lambda *_args, **_kwargs: None,
        subject_code_from_hint=lambda *_args, **_kwargs: (None, None),
        student_hint_from_message=lambda *_args, **_kwargs: None,
        is_student_name_only_followup=lambda *_args, **_kwargs: None,
        compose_upcoming_assessments_lines=lambda _summary: [],
    )

    answer = asyncio.run(maybe_resolved_intent_answer(ctx, deps=deps))
    assert answer is not None
    assert answer.mode == 'deny'
    assert 'Rafael' in answer.message_text
    assert 'Lucas Oliveira' in answer.message_text
