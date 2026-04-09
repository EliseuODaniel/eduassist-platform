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
    assert plan.preview.mode is OrchestrationMode.hybrid_retrieval
    assert plan.preview.classification.domain is QueryDomain.institution
    assert plan.preview.classification.access_tier is AccessTier.public
    assert plan.preview.selected_tools == ['search_documents']


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
