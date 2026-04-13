from __future__ import annotations

from ai_orchestrator.models import (
    AccessTier,
    MessageResponseRequest,
    OrchestrationMode,
    QueryDomain,
    UserContext,
    UserRole,
)
from ai_orchestrator.python_functions_runtime import build_python_functions_plan
from ai_orchestrator.llamaindex_path_runtime import build_llamaindex_plan


class _Settings:
    graph_rag_enabled = False


def test_python_functions_plan_uses_local_kernel_for_authenticated_academic_query() -> None:
    request = MessageResponseRequest(
        message='Quais sao as proximas provas da Ana?',
        user=UserContext(role=UserRole.guardian, authenticated=True),
    )

    plan = build_python_functions_plan(request=request, settings=_Settings(), mode='python_functions')

    assert plan.__class__.__module__.endswith('python_functions_kernel')
    assert plan.preview.mode is OrchestrationMode.structured_tool
    assert plan.preview.classification.domain is QueryDomain.academic
    assert plan.preview.classification.access_tier is AccessTier.authenticated
    assert 'get_student_upcoming_assessments' in plan.preview.selected_tools


def test_llamaindex_plan_uses_local_kernel_for_public_documentary_query() -> None:
    request = MessageResponseRequest(
        message='Quero uma leitura comparativa entre rematricula, transferencia e cancelamento.',
        user=UserContext(role=UserRole.anonymous, authenticated=False),
    )

    plan = build_llamaindex_plan(request=request, settings=_Settings(), mode='llamaindex')

    assert plan.__class__.__module__.endswith('llamaindex_kernel')
    assert plan.preview.mode is OrchestrationMode.structured_tool
    assert plan.preview.classification.domain is QueryDomain.institution
    assert plan.preview.classification.access_tier is AccessTier.public
    assert 'get_public_school_profile' in plan.preview.selected_tools


def test_python_functions_plan_detects_authenticated_academic_risk_recut() -> None:
    request = MessageResponseRequest(
        message='Quero o mesmo panorama, mas agora isolando a Ana e os pontos academicos que mais preocupam.',
        user=UserContext(role=UserRole.guardian, authenticated=True),
    )

    plan = build_python_functions_plan(request=request, settings=_Settings(), mode='python_functions')

    assert plan.preview.mode is OrchestrationMode.structured_tool
    assert plan.preview.classification.domain is QueryDomain.academic
    assert 'get_student_academic_summary' in plan.preview.selected_tools


def test_llamaindex_plan_detects_authenticated_academic_risk_recut() -> None:
    request = MessageResponseRequest(
        message='Quero o mesmo panorama, mas agora isolando a Ana e os pontos academicos que mais preocupam.',
        user=UserContext(role=UserRole.guardian, authenticated=True),
    )

    plan = build_llamaindex_plan(request=request, settings=_Settings(), mode='llamaindex')

    assert plan.preview.mode is OrchestrationMode.structured_tool
    assert plan.preview.classification.domain is QueryDomain.academic
    assert 'get_student_academic_summary' in plan.preview.selected_tools


def test_python_functions_plan_keeps_authenticated_public_conduct_query_out_of_admin_fallback() -> None:
    request = MessageResponseRequest(
        message='Posso fumar maconha nessa escola?',
        user=UserContext(role=UserRole.guardian, authenticated=True),
    )

    plan = build_python_functions_plan(request=request, settings=_Settings(), mode='python_functions')

    assert plan.preview.mode is OrchestrationMode.structured_tool
    assert plan.preview.classification.domain is QueryDomain.institution
    assert plan.preview.classification.access_tier is AccessTier.public
    assert 'get_public_school_profile' in plan.preview.selected_tools
    assert 'get_administrative_status' not in plan.preview.selected_tools


def test_llamaindex_plan_keeps_authenticated_public_conduct_query_out_of_admin_fallback() -> None:
    request = MessageResponseRequest(
        message='Posso fumar maconha nessa escola?',
        user=UserContext(role=UserRole.guardian, authenticated=True),
    )

    plan = build_llamaindex_plan(request=request, settings=_Settings(), mode='llamaindex')

    assert plan.preview.mode is OrchestrationMode.structured_tool
    assert plan.preview.classification.domain is QueryDomain.institution
    assert plan.preview.classification.access_tier is AccessTier.public
    assert 'get_public_school_profile' in plan.preview.selected_tools
    assert 'get_administrative_status' not in plan.preview.selected_tools


def test_python_functions_plan_keeps_public_conduct_query_public_when_not_authenticated() -> None:
    request = MessageResponseRequest(
        message='Posso fumar maconha nessa escola?',
        user=UserContext(role=UserRole.anonymous, authenticated=False),
    )

    plan = build_python_functions_plan(request=request, settings=_Settings(), mode='python_functions')

    assert plan.preview.mode is OrchestrationMode.structured_tool
    assert plan.preview.classification.domain is QueryDomain.institution
    assert plan.preview.classification.access_tier is AccessTier.public
    assert 'get_public_school_profile' in plan.preview.selected_tools
    assert 'get_administrative_status' not in plan.preview.selected_tools


def test_llamaindex_plan_keeps_public_conduct_query_public_when_not_authenticated() -> None:
    request = MessageResponseRequest(
        message='Posso fumar maconha nessa escola?',
        user=UserContext(role=UserRole.anonymous, authenticated=False),
    )

    plan = build_llamaindex_plan(request=request, settings=_Settings(), mode='llamaindex')

    assert plan.preview.mode is OrchestrationMode.structured_tool
    assert plan.preview.classification.domain is QueryDomain.institution
    assert plan.preview.classification.access_tier is AccessTier.public
    assert 'get_public_school_profile' in plan.preview.selected_tools
    assert 'get_administrative_status' not in plan.preview.selected_tools


def test_python_functions_plan_treats_leadership_contact_query_as_public_institution() -> None:
    request = MessageResponseRequest(
        message='qual contato do diretor?',
        user=UserContext(role=UserRole.guardian, authenticated=True),
    )

    plan = build_python_functions_plan(request=request, settings=_Settings(), mode='python_functions')

    assert plan.preview.mode is OrchestrationMode.structured_tool
    assert plan.preview.classification.domain is QueryDomain.institution
    assert plan.preview.classification.access_tier is AccessTier.public
    assert 'get_public_school_profile' in plan.preview.selected_tools


def test_llamaindex_plan_treats_leadership_contact_query_as_public_institution() -> None:
    request = MessageResponseRequest(
        message='qual contato do diretor?',
        user=UserContext(role=UserRole.guardian, authenticated=True),
    )

    plan = build_llamaindex_plan(request=request, settings=_Settings(), mode='llamaindex')

    assert plan.preview.mode is OrchestrationMode.structured_tool
    assert plan.preview.classification.domain is QueryDomain.institution
    assert plan.preview.classification.access_tier is AccessTier.public
    assert 'get_public_school_profile' in plan.preview.selected_tools


def test_python_functions_plan_keeps_authenticated_enrollment_documents_query_public() -> None:
    request = MessageResponseRequest(
        message='Quais documentos preciso para matricula?',
        user=UserContext(role=UserRole.guardian, authenticated=True),
    )

    plan = build_python_functions_plan(request=request, settings=_Settings(), mode='python_functions')

    assert plan.preview.mode is OrchestrationMode.structured_tool
    assert plan.preview.classification.domain is QueryDomain.institution
    assert plan.preview.classification.access_tier is AccessTier.public
    assert 'get_public_school_profile' in plan.preview.selected_tools
    assert 'get_administrative_status' not in plan.preview.selected_tools


def test_llamaindex_plan_keeps_authenticated_enrollment_documents_query_public() -> None:
    request = MessageResponseRequest(
        message='Quais documentos preciso para matricula?',
        user=UserContext(role=UserRole.guardian, authenticated=True),
    )

    plan = build_llamaindex_plan(request=request, settings=_Settings(), mode='llamaindex')

    assert plan.preview.mode is OrchestrationMode.structured_tool
    assert plan.preview.classification.domain is QueryDomain.institution
    assert plan.preview.classification.access_tier is AccessTier.public
    assert 'get_public_school_profile' in plan.preview.selected_tools
    assert 'get_administrative_status' not in plan.preview.selected_tools


def test_python_functions_plan_keeps_authenticated_school_year_start_query_public() -> None:
    request = MessageResponseRequest(
        message='Quando iniciam as aulas?',
        user=UserContext(role=UserRole.guardian, authenticated=True),
    )

    plan = build_python_functions_plan(request=request, settings=_Settings(), mode='python_functions')

    assert plan.preview.mode is OrchestrationMode.structured_tool
    assert plan.preview.classification.access_tier is AccessTier.public
    assert 'get_public_school_profile' in plan.preview.selected_tools
    assert 'get_administrative_status' not in plan.preview.selected_tools


def test_llamaindex_plan_keeps_authenticated_school_year_start_query_public() -> None:
    request = MessageResponseRequest(
        message='Quando iniciam as aulas?',
        user=UserContext(role=UserRole.guardian, authenticated=True),
    )

    plan = build_llamaindex_plan(request=request, settings=_Settings(), mode='llamaindex')

    assert plan.preview.mode is OrchestrationMode.structured_tool
    assert plan.preview.classification.access_tier is AccessTier.public
    assert 'get_public_school_profile' in plan.preview.selected_tools
    assert 'get_administrative_status' not in plan.preview.selected_tools


def test_python_functions_plan_treats_morning_class_schedule_query_as_public_institution() -> None:
    request = MessageResponseRequest(
        message='Que horas começa a aula de manhã?',
        user=UserContext(role=UserRole.guardian, authenticated=True),
    )

    plan = build_python_functions_plan(request=request, settings=_Settings(), mode='python_functions')

    assert plan.preview.mode is OrchestrationMode.structured_tool
    assert plan.preview.classification.domain is QueryDomain.institution
    assert plan.preview.classification.access_tier is AccessTier.public
    assert 'get_public_school_profile' in plan.preview.selected_tools
    assert 'get_administrative_status' not in plan.preview.selected_tools


def test_llamaindex_plan_treats_morning_class_schedule_query_as_public_institution() -> None:
    request = MessageResponseRequest(
        message='Que horas começa a aula de manhã?',
        user=UserContext(role=UserRole.guardian, authenticated=True),
    )

    plan = build_llamaindex_plan(request=request, settings=_Settings(), mode='llamaindex')

    assert plan.preview.mode is OrchestrationMode.structured_tool
    assert plan.preview.classification.domain is QueryDomain.institution
    assert plan.preview.classification.access_tier is AccessTier.public
    assert 'get_public_school_profile' in plan.preview.selected_tools
    assert 'get_administrative_status' not in plan.preview.selected_tools


def test_python_functions_plan_clarifies_authenticated_off_scope_query_instead_of_admin_fallback() -> None:
    request = MessageResponseRequest(
        message='Qual o melhor filme do ano?',
        user=UserContext(role=UserRole.guardian, authenticated=True),
    )

    plan = build_python_functions_plan(request=request, settings=_Settings(), mode='python_functions')

    assert plan.preview.mode is OrchestrationMode.clarify
    assert plan.preview.classification.domain is QueryDomain.unknown
    assert plan.preview.selected_tools == []


def test_llamaindex_plan_clarifies_authenticated_off_scope_query_instead_of_admin_fallback() -> None:
    request = MessageResponseRequest(
        message='Qual o melhor filme do ano?',
        user=UserContext(role=UserRole.guardian, authenticated=True),
    )

    plan = build_llamaindex_plan(request=request, settings=_Settings(), mode='llamaindex')

    assert plan.preview.mode is OrchestrationMode.clarify
    assert plan.preview.classification.domain is QueryDomain.unknown
    assert plan.preview.selected_tools == []


def test_python_functions_plan_clarifies_authenticated_opaque_input_instead_of_admin_fallback() -> None:
    request = MessageResponseRequest(
        message='rai',
        user=UserContext(role=UserRole.guardian, authenticated=True),
    )

    plan = build_python_functions_plan(request=request, settings=_Settings(), mode='python_functions')

    assert plan.preview.mode is OrchestrationMode.clarify
    assert plan.preview.classification.domain is QueryDomain.unknown
    assert plan.preview.selected_tools == []


def test_llamaindex_plan_clarifies_authenticated_opaque_input_instead_of_admin_fallback() -> None:
    request = MessageResponseRequest(
        message='rai',
        user=UserContext(role=UserRole.guardian, authenticated=True),
    )

    plan = build_llamaindex_plan(request=request, settings=_Settings(), mode='llamaindex')

    assert plan.preview.mode is OrchestrationMode.clarify
    assert plan.preview.classification.domain is QueryDomain.unknown
    assert plan.preview.selected_tools == []


def test_python_functions_plan_denies_teacher_internal_material_for_guardian() -> None:
    request = MessageResponseRequest(
        message='No material interno do professor, como a escola orienta o registro de avaliacoes e a comunicacao pedagogica?',
        user=UserContext(role=UserRole.guardian, authenticated=True),
    )

    plan = build_python_functions_plan(request=request, settings=_Settings(), mode='python_functions')

    assert plan.preview.mode is OrchestrationMode.deny
    assert plan.preview.reason == 'python_functions_local_restricted_documents_denied'


def test_python_functions_plan_denies_internal_international_trip_guidance_for_guardian() -> None:
    request = MessageResponseRequest(
        message='Existe orientacao interna para viagem internacional com hospedagem envolvendo turmas do ensino medio?',
        user=UserContext(role=UserRole.guardian, authenticated=True),
    )

    plan = build_python_functions_plan(request=request, settings=_Settings(), mode='python_functions')

    assert plan.preview.mode is OrchestrationMode.deny
    assert plan.preview.reason == 'python_functions_local_restricted_documents_denied'
