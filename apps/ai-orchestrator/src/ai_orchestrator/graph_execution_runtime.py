from __future__ import annotations

# ruff: noqa: F401,F403,F405

LOCAL_EXTRACTED_NAMES = {'structured_tool_call', 'get_graph_blueprint'}

from . import graph as _native
from .extracted_module_contracts import refresh_extracted_module_contract
from .graph_execution_contract import GRAPH_EXECUTION_CONTRACT


def _refresh_native_namespace() -> None:
    refresh_extracted_module_contract(
        native_module=_native,
        namespace=globals(),
        contract_names=GRAPH_EXECUTION_CONTRACT,
        local_extracted_names=LOCAL_EXTRACTED_NAMES,
        contract_label='graph_execution_runtime',
    )


def structured_tool_call(state: OrchestrationState) -> OrchestrationState:
    _refresh_native_namespace()
    classification = state['classification']
    request = state['request']
    normalized_message = _normalize_text(request.message)

    if classification.domain is QueryDomain.institution:
        selected_tools = ['get_public_school_profile']
        def add_institution_tool(tool_name: str) -> None:
            if tool_name not in selected_tools:
                selected_tools.append(tool_name)

        if _is_public_navigation_query(normalized_message):
            add_institution_tool('get_service_directory')
        if any(
            _message_matches_term(normalized_message, term)
            for term in ACCESS_SCOPE_TERMS
        ):
            add_institution_tool('list_assistant_capabilities')
        if any(
            _message_matches_term(normalized_message, term)
            for term in {
                'o que voce faz',
                'o que você faz',
                'como voce pode me ajudar',
                'como você pode me ajudar',
                'no que voce pode ajudar',
                'no que você pode ajudar',
                'quais assuntos',
                'assuntos',
                'opcoes de assuntos',
                'opções de assuntos',
                'oi',
                'ola',
                'olá',
                'bom dia',
                'boa tarde',
                'boa noite',
            }
        ):
            add_institution_tool('list_assistant_capabilities')
        if any(
            _message_matches_term(normalized_message, term)
            for term in {
                'com quem eu falo',
                'pra quem eu falo',
                'para quem eu falo',
                'quem cuida',
                'quem resolve',
                'qual setor',
            }
        ):
            add_institution_tool('get_service_directory')
        if _is_public_document_submission_query(normalized_message):
            add_institution_tool('get_service_directory')
        if any(
            _message_matches_term(normalized_message, term)
            for term in {
                'quem e voce',
                'quem é você',
                'voce e quem',
                'você é quem',
                'diretora',
                'diretor',
                'direcao',
                'direção',
                'diretoria',
                'coordenacao',
                'coordenação',
                'lideranca',
                'liderança',
            }
        ):
            add_institution_tool('get_org_directory')
        output_contract = 'fato institucional publico, navegacao de atendimento e orientacao de concierge'
    elif classification.domain is QueryDomain.calendar and (
        _is_public_timeline_query(normalized_message) or _is_public_calendar_event_query(normalized_message)
    ):
        if _is_public_calendar_event_query(normalized_message):
            selected_tools = ['get_public_calendar_events']
            output_contract = 'eventos publicos estruturados do calendario escolar'
        else:
            selected_tools = ['get_public_timeline']
            output_contract = 'datas institucionais publicas e marcos do calendario em fonte estruturada'
    elif classification.domain is QueryDomain.support:
        if _is_workflow_status_request(request.message):
            selected_tools = ['get_workflow_status']
            output_contract = 'consulta de status de protocolo, visita ou solicitacao institucional ja registrada'
        elif _is_visit_booking_update_request(request.message):
            selected_tools = ['update_visit_booking']
            output_contract = 'atualizacao de visita institucional existente, com remarcacao ou cancelamento'
        elif _is_institutional_request_update(request.message):
            selected_tools = ['update_institutional_request']
            output_contract = 'atualizacao de solicitacao institucional existente, com complemento auditavel e mesmo protocolo'
        elif _is_visit_booking_request(request.message):
            selected_tools = ['schedule_school_visit', 'create_support_ticket']
            output_contract = 'agendamento ou pre-agendamento de visita institucional com protocolo e fila comercial'
        else:
            selected_tools = ['create_institutional_request', 'create_support_ticket']
            output_contract = 'solicitacao institucional formal com protocolo, fila e contexto auditavel'
    elif classification.domain is QueryDomain.academic:
        if request.user.role is UserRole.teacher:
            selected_tools = ['get_teacher_schedule']
            output_contract = 'grade docente e informacoes operacionais permitidas ao professor'
        else:
            selected_tools = [
                'get_student_academic_summary',
                'get_student_attendance',
                'get_student_grades',
                'get_student_upcoming_assessments',
                'get_student_attendance_timeline',
            ]
            output_contract = 'dados academicos autorizados, auditaveis e minimizados'
    else:
        selected_tools = ['get_financial_summary']
        if request.user.authenticated and (
            _is_admin_finance_combined_query(normalized_message)
            or any(_message_matches_term(normalized_message, term) for term in PERSONAL_ADMIN_TERMS)
        ):
            selected_tools.append('get_administrative_status')
        output_contract = 'dados financeiros autorizados, auditaveis e com trilha reforcada'

    if classification.domain is QueryDomain.institution and request.user.authenticated:
        if _is_authenticated_actor_identity_query(normalized_message, authenticated=True):
            selected_tools = ['get_actor_identity_context']
            output_contract = 'identidade da conta autenticada, papel atual e alunos vinculados'
        elif _is_authenticated_access_scope_query(normalized_message, authenticated=True):
            selected_tools = ['get_actor_identity_context']
            output_contract = 'escopo autenticado da conta, dados liberados e alunos vinculados'
        elif _is_authenticated_linked_students_query(normalized_message, authenticated=True):
            selected_tools = ['get_actor_identity_context']
            output_contract = 'lista de alunos vinculados e capacidade disponivel para consulta protegida'
        elif _is_authenticated_admin_query(normalized_message, authenticated=True):
            selected_tools = ['get_administrative_status', 'get_student_administrative_status']
            output_contract = 'status administrativo autenticado, com escopo do proprio usuario ou de aluno vinculado'

    return {
        'retrieval_backend': RetrievalBackend.none.value,
        'selected_tools': selected_tools,
        'citations_required': False,
        'output_contract': output_contract,
        'graph_path': _append_path(state, 'structured_tool_call'),
    }

def get_graph_blueprint() -> dict[str, object]:
    return {
        'entrypoint': 'classify_request',
        'nodes': [
            'classify_request',
            'security_gate',
            'route_request',
            'select_slice',
            'public_slice',
            'protected_slice',
            'support_slice',
            'deny',
            'clarify',
        ],
        'subgraphs': {
            'public_slice': ['hybrid_retrieval', 'graph_rag_retrieval', 'structured_tool_call'],
            'protected_slice': [
                'structured_tool_call',
                'protected_human_review',
                'protected_review_approved',
                'protected_review_cancelled',
            ],
            'support_slice': [
                'structured_tool_call',
                'handoff',
                'support_human_review',
                'support_review_approved',
                'support_review_cancelled',
            ],
        },
        'terminal_routes': [
            OrchestrationMode.hybrid_retrieval.value,
            OrchestrationMode.graph_rag.value,
            OrchestrationMode.structured_tool.value,
            OrchestrationMode.handoff.value,
            OrchestrationMode.deny.value,
            OrchestrationMode.clarify.value,
        ],
    }
