from __future__ import annotations

from .specialist_supervisor_types import SpecialistSpec


SPECIALIST_REGISTRY: tuple[SpecialistSpec, ...] = (
    SpecialistSpec(
        id='retrieval_planner',
        name='Retrieval Planner',
        description='Decide a melhor estrategia de evidencia: structured tools, hybrid retrieval, GraphRAG, document search, pricing projection ou clarificacao.',
        supported_domains=('institution', 'calendar', 'academic', 'finance', 'support'),
        supported_slices=('public', 'protected', 'support', 'workflow'),
        allowed_tools=(
            'search_public_documents',
            'search_private_documents',
            'get_public_school_profile',
            'fetch_academic_policy',
            'graph_rag',
            'pricing_projection',
            'workflow_status',
        ),
        risk_level='high',
        max_context_budget=8,
    ),
    SpecialistSpec(
        id='institution_specialist',
        name='Institution Specialist',
        description='Responde perguntas institucionais, curriculo, calendario, localizacao, diferenciacao e canais oficiais.',
        supported_domains=('institution', 'calendar'),
        supported_slices=('public',),
        allowed_tools=(
            'get_public_school_profile',
            'fetch_academic_policy',
            'get_public_timeline',
            'get_public_calendar_events',
            'get_org_directory',
            'get_service_directory',
            'search_public_documents',
            'graph_rag',
            'pricing_projection',
        ),
        max_context_budget=8,
    ),
    SpecialistSpec(
        id='academic_specialist',
        name='Academic Specialist',
        description='Responde perguntas de notas, frequencia, aprovacao, avaliacoes e panorama academico com base no aluno autorizado.',
        supported_domains=('academic',),
        supported_slices=('protected',),
        allowed_tools=(
            'get_actor_identity_context',
            'fetch_academic_policy',
            'get_student_academic_summary',
            'get_student_attendance',
            'get_student_grades',
            'get_student_upcoming_assessments',
            'get_student_attendance_timeline',
            'get_student_administrative_status',
        ),
        risk_level='high',
        max_context_budget=6,
    ),
    SpecialistSpec(
        id='finance_specialist',
        name='Finance Specialist',
        description='Responde perguntas financeiras autorizadas, incluindo boletos, vencimentos, situacao de contrato e projecoes de custo.',
        supported_domains=('finance',),
        supported_slices=('protected',),
        allowed_tools=(
            'get_actor_identity_context',
            'get_financial_summary',
            'pricing_projection',
            'get_administrative_status',
        ),
        risk_level='high',
        max_context_budget=6,
    ),
    SpecialistSpec(
        id='workflow_specialist',
        name='Workflow Specialist',
        description='Coordena protocolos, visitas, remarcacoes, cancelamentos e solicitacoes institucionais.',
        supported_domains=('support',),
        supported_slices=('support', 'workflow'),
        allowed_tools=(
            'get_workflow_status',
            'create_support_ticket',
            'schedule_school_visit',
            'update_visit_booking',
            'create_institutional_request',
            'update_institutional_request',
            'handoff_to_human',
        ),
        risk_level='high',
        max_context_budget=6,
    ),
    SpecialistSpec(
        id='document_specialist',
        name='Document Specialist',
        description='Responde sobre corpus documental, documentos privados/autorizados e buscas com filtros e citacoes.',
        supported_domains=('institution', 'academic', 'finance', 'support'),
        supported_slices=('public', 'protected'),
        allowed_tools=(
            'search_public_documents',
            'search_private_documents',
            'graph_rag',
        ),
        max_context_budget=10,
    ),
    SpecialistSpec(
        id='judge_specialist',
        name='Judge Specialist',
        description='Valida grounding, completude, contradicoes e a necessidade de clarificacao antes da resposta final.',
        supported_domains=('institution', 'calendar', 'academic', 'finance', 'support'),
        supported_slices=('public', 'protected', 'support', 'workflow'),
        allowed_tools=(),
        risk_level='critical',
        max_context_budget=8,
    ),
)


def get_specialist_registry() -> dict[str, SpecialistSpec]:
    return {spec.id: spec for spec in SPECIALIST_REGISTRY if spec.activation_flag}
