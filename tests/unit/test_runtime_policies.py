from __future__ import annotations

from types import SimpleNamespace

from ai_orchestrator.models import AccessTier, OrchestrationMode, QueryDomain
from ai_orchestrator.runtime import (
    _apply_protected_domain_rescue,
    _explicit_protected_domain_hint,
    _is_public_support_navigation_query,
    _looks_like_public_documentary_open_query,
    _should_polish_structured_answer,
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
    )
    assert response.used_llm is True
    assert response.llm_stages == ['answer_composition']
