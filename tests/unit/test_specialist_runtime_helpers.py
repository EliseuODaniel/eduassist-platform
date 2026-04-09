from __future__ import annotations

import asyncio
from types import SimpleNamespace

from ai_orchestrator_specialist.models import (
    MessageIntentClassification,
    OperationalMemory,
    SupervisorAnswerPayload,
)
from ai_orchestrator_specialist.operational_memory_answers import (
    OperationalMemoryDeps,
    maybe_operational_memory_follow_up_answer,
)
from ai_orchestrator_specialist.fast_path_answers import (
    FastPathDeps,
    build_fast_path_answer,
)
from ai_orchestrator_specialist.public_query_patterns import (
    _extract_teacher_subject,
    _looks_like_admin_finance_combo_query,
    _looks_like_calendar_week_query,
    _looks_like_health_second_call_query,
    _looks_like_public_doc_bundle_request,
    _looks_like_process_compare_query,
)
from ai_orchestrator_specialist.restricted_doc_matching import (
    _internal_doc_hit_score,
    _looks_like_internal_document_query,
)
from ai_orchestrator_specialist.resolved_intent_answers import (
    ResolvedIntentDeps,
    maybe_resolved_intent_answer,
)
from ai_orchestrator_specialist.protected_answer_helpers import looks_like_academic_risk_followup
from ai_orchestrator_specialist.support_workflow_helpers import (
    _detect_support_handoff_queue,
    _looks_like_human_handoff_request,
)
from ai_orchestrator_specialist.supervisor_run_flow import _persist_and_dump, _provider_metadata


def test_extract_teacher_subject_stops_at_conjunction() -> None:
    assert _extract_teacher_subject('Qual o nome do professor de matematica ou da coordenacao?') == 'matematica'


def test_extract_teacher_subject_stops_at_followup_clause() -> None:
    assert (
        _extract_teacher_subject('Vocês divulgam o nome ou contato direto do professor de matematica? Se nao, para onde a familia deve ir?')
        == 'matematica'
    )


def test_admin_finance_combo_query_detects_regularidade_and_finance() -> None:
    assert _looks_like_admin_finance_combo_query(
        'Quero a regularidade documental e a situacao financeira com boletos e mensalidades.'
    )


def test_health_second_call_query_detects_attested_exam_miss() -> None:
    assert _looks_like_health_second_call_query(
        'Se eu perder uma prova por motivo de saude com atestado, como funciona a segunda chamada?'
    )


def test_calendar_week_query_detects_generic_public_calendar_prompt() -> None:
    assert _looks_like_calendar_week_query(
        'Dentro do calendario publico, quais eventos parecem mais importantes para familias e responsaveis?'
    )


def test_process_compare_query_detects_side_by_side_public_compare() -> None:
    assert _looks_like_process_compare_query(
        'Pensando no caso pratico, se a familia colocar rematricula, transferencia e cancelamento lado a lado, quais diferencas praticas aparecem em papelada e prazos?'
    )


def test_public_doc_bundle_request_detects_documentary_open_governance_prompt() -> None:
    assert _looks_like_public_doc_bundle_request(
        'Quero entender como a familia sobe da coordenacao para a lideranca maior quando o impasse sai da rotina normal.'
    )


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
        fetch_academic_summary_payload=lambda *_args, **_kwargs: None,
        fetch_financial_summary_payload=lambda *_args, **_kwargs: None,
        resolved_academic_target_name=lambda *_args, **_kwargs: None,
        needs_specific_academic_student_clarification=lambda *_args, **_kwargs: False,
        build_academic_student_selection_clarify=lambda *_args, **_kwargs: None,
        compose_academic_risk_answer=lambda _summary: '',
        compose_named_subject_grade_answer=lambda *_args, **_kwargs: None,
        compose_named_grade_answer=lambda _summary: '',
        compose_named_attendance_answer=lambda *_args, **_kwargs: None,
        compose_academic_snapshot_lines=lambda _summary: [],
        compose_finance_aggregate_answer=lambda _summaries: '',
        compose_finance_installments_answer=lambda _summary: '',
        linked_students=lambda *_args, **_kwargs: [],
        safe_excerpt=lambda text, **_kwargs: text,
        subject_hint_from_text=lambda _message: None,
        recent_subject_from_context=lambda *_args, **_kwargs: None,
        subject_code_from_hint=lambda *_args, **_kwargs: (None, None),
        student_hint_from_message=lambda *_args, **_kwargs: None,
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
