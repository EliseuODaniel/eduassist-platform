from __future__ import annotations

from .models import SpecialistSpec


SPECIALIST_REGISTRY: tuple[SpecialistSpec, ...] = (
    SpecialistSpec(
        id="retrieval_planner",
        name="Retrieval Planner",
        description="Escolhe a melhor estrategia de evidencia e quais especialistas o manager deve chamar.",
        supported_domains=["institution", "calendar", "academic", "finance", "support"],
        supported_slices=["public", "protected", "support", "workflow"],
        allowed_tools=[
            "search_public_documents",
            "search_private_documents",
            "get_public_profile_bundle",
            "fetch_academic_policy",
            "run_graph_rag_query",
            "project_public_pricing",
            "fetch_workflow_status",
        ],
        risk_level="high",
        max_context_budget=8,
    ),
    SpecialistSpec(
        id="institution_specialist",
        name="Institution Specialist",
        description="Responde perguntas institucionais publicas, calendario, curriculo, localizacao e diferenciais com grounding forte.",
        supported_domains=["institution", "calendar"],
        supported_slices=["public"],
        allowed_tools=[
            "get_public_profile_bundle",
            "fetch_academic_policy",
            "search_public_documents",
            "run_graph_rag_query",
            "project_public_pricing",
        ],
        max_context_budget=8,
    ),
    SpecialistSpec(
        id="academic_specialist",
        name="Academic Specialist",
        description="Responde sobre notas, frequencia, proximas avaliacoes, timeline de faltas e aprovacao por disciplina.",
        supported_domains=["academic"],
        supported_slices=["protected"],
        allowed_tools=[
            "fetch_actor_identity",
            "fetch_academic_policy",
            "fetch_academic_summary",
            "fetch_upcoming_assessments",
            "fetch_attendance_timeline",
            "calculate_grade_requirement",
        ],
        risk_level="high",
        max_context_budget=6,
    ),
    SpecialistSpec(
        id="finance_specialist",
        name="Finance Specialist",
        description="Responde sobre boletos, vencimentos, contratos, status financeiro e projecoes publicas de custo.",
        supported_domains=["finance"],
        supported_slices=["protected"],
        allowed_tools=[
            "fetch_actor_identity",
            "fetch_financial_summary",
            "project_public_pricing",
        ],
        risk_level="high",
        max_context_budget=6,
    ),
    SpecialistSpec(
        id="workflow_specialist",
        name="Workflow Specialist",
        description="Coordena visitas, protocolos, remarcacoes, cancelamentos e solicitacoes institucionais.",
        supported_domains=["support"],
        supported_slices=["support", "workflow"],
        allowed_tools=[
            "fetch_workflow_status",
            "create_visit_booking",
            "update_visit_booking",
            "create_institutional_request",
            "update_institutional_request",
        ],
        risk_level="high",
        max_context_budget=6,
    ),
    SpecialistSpec(
        id="document_specialist",
        name="Document Specialist",
        description="Responde sobre corpus documental publico e, quando houver autorizacao, usa busca documental filtrada.",
        supported_domains=["institution", "academic", "finance", "support"],
        supported_slices=["public", "protected"],
        allowed_tools=[
            "search_public_documents",
            "search_private_documents",
            "run_graph_rag_query",
        ],
        max_context_budget=10,
    ),
    SpecialistSpec(
        id="judge_specialist",
        name="Judge Specialist",
        description="Valida grounding, completude, contradicoes, necessidade de clarificacao e risco de overclaiming.",
        supported_domains=["institution", "calendar", "academic", "finance", "support"],
        supported_slices=["public", "protected", "support", "workflow"],
        allowed_tools=[],
        risk_level="critical",
        max_context_budget=8,
    ),
)


def get_specialist_registry() -> dict[str, SpecialistSpec]:
    return {spec.id: spec for spec in SPECIALIST_REGISTRY if spec.activation_flag}
