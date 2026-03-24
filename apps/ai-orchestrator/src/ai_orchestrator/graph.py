from __future__ import annotations

from functools import lru_cache
from typing import TypedDict
import unicodedata

from langgraph.graph import END, START, StateGraph

from .models import (
    AccessTier,
    IntentClassification,
    OrchestrationMode,
    OrchestrationPreview,
    OrchestrationRequest,
    QueryDomain,
    RetrievalBackend,
    UserRole,
)


class OrchestrationState(TypedDict, total=False):
    request: OrchestrationRequest
    classification: IntentClassification
    route: str
    reason: str
    retrieval_backend: str
    selected_tools: list[str]
    citations_required: bool
    needs_authentication: bool
    graph_path: list[str]
    risk_flags: list[str]
    output_contract: str


class GraphRuntimeConfig(TypedDict):
    graph_rag_enabled: bool


PUBLIC_CALENDAR_TERMS = {'calendario', 'feriado', 'evento', 'prova', 'reuniao'}
ACADEMIC_TERMS = {
    'nota',
    'notas',
    'boletim',
    'frequencia',
    'falta',
    'faltas',
    'avaliacao',
    'avaliacoes',
    'turma',
    'turmas',
    'disciplina',
    'disciplinas',
    'materia',
    'materias',
    'bimestre',
}
FINANCE_TERMS = {
    'mensalidade',
    'boleto',
    'boletos',
    'financeiro',
    'pagamento',
    'pagamentos',
    'inadimplencia',
    'bolsa',
    'fatura',
    'faturas',
    'conta',
    'contas',
    'pago',
    'pagos',
    'paga',
    'pagas',
    'quitado',
    'quitados',
    'quitada',
    'quitadas',
    'vencido',
    'vencidos',
    'vencida',
    'vencidas',
    'aberto',
    'abertos',
    'pendencia',
    'pendencias',
}
SUPPORT_TERMS = {'humano', 'atendente', 'suporte', 'protocolo', 'chamado'}
SUPPORT_PHRASES = {
    'falar com',
    'atendimento humano',
    'ajuda humana',
    'me transfira',
    'me encaminhe',
}
GRAPH_RAG_TERMS = {'visao geral', 'compare', 'comparar', 'tendencias', 'corpus', 'relacione'}
TEACHER_SELF_SERVICE_TERMS = {'horario', 'agenda', 'turma', 'turmas', 'disciplina', 'disciplinas', 'materia', 'materias'}
PUBLIC_SERVICE_TERMS = {
    'biblioteca',
    'cantina',
    'laboratorio',
    'laboratorio de ciencias',
    'portaria',
    'secretaria',
    'atendimento',
    'funcionamento',
    'horario de atendimento',
}
INSTITUTION_TERMS = {'escola', 'matricula', 'regimento', 'instituicao', 'endereco'}
PUBLIC_SCHOOL_PROFILE_TERMS = {
    'nome da escola',
    'nome do colegio',
    'nome do colégio',
    'como se chama a escola',
    'como se chama o colegio',
    'como se chama o colégio',
}


def _append_path(state: OrchestrationState, node_name: str) -> list[str]:
    return [*state.get('graph_path', []), node_name]


def _normalize_text(text: str) -> str:
    normalized = unicodedata.normalize('NFKD', text)
    without_accents = ''.join(char for char in normalized if not unicodedata.combining(char))
    return without_accents.lower()


def _contains_any(message: str, terms: set[str]) -> bool:
    lowered = _normalize_text(message)
    return any(term in lowered for term in terms)


def _wants_human_support(message: str) -> bool:
    lowered = _normalize_text(message)
    return any(term in lowered for term in SUPPORT_TERMS) or any(
        phrase in lowered for phrase in SUPPORT_PHRASES
    )


def _is_teacher_self_service_request(message: str, role: UserRole) -> bool:
    lowered = _normalize_text(message)
    return role is UserRole.teacher and any(term in lowered for term in TEACHER_SELF_SERVICE_TERMS)


def _is_public_school_profile_request(message: str) -> bool:
    lowered = _normalize_text(message)
    return any(term in lowered for term in PUBLIC_SCHOOL_PROFILE_TERMS)


def classify_request(state: OrchestrationState) -> OrchestrationState:
    request = state['request']
    message = _normalize_text(request.message)

    if _wants_human_support(message):
        classification = IntentClassification(
            domain=QueryDomain.support,
            access_tier=AccessTier.public,
            confidence=0.92,
            reason='mensagem contem termos de atendimento humano ou suporte',
        )
    elif _is_teacher_self_service_request(message, request.user.role):
        classification = IntentClassification(
            domain=QueryDomain.academic,
            access_tier=AccessTier.authenticated,
            confidence=0.94,
            reason='mensagem indica autoatendimento docente sobre turmas, disciplinas ou horario',
        )
    elif _contains_any(message, FINANCE_TERMS):
        classification = IntentClassification(
            domain=QueryDomain.finance,
            access_tier=AccessTier.sensitive,
            confidence=0.91,
            reason='mensagem contem termos financeiros com potencial de dado sensivel',
        )
    elif _contains_any(message, ACADEMIC_TERMS):
        classification = IntentClassification(
            domain=QueryDomain.academic,
            access_tier=AccessTier.authenticated,
            confidence=0.9,
            reason='mensagem contem termos academicos dependentes de vinculo escolar',
        )
    elif _contains_any(message, PUBLIC_CALENDAR_TERMS):
        classification = IntentClassification(
            domain=QueryDomain.calendar,
            access_tier=AccessTier.public,
            confidence=0.84,
            reason='mensagem contem termos de calendario e eventos escolares',
        )
    elif _contains_any(message, PUBLIC_SERVICE_TERMS) or any(term in message for term in INSTITUTION_TERMS):
        classification = IntentClassification(
            domain=QueryDomain.institution,
            access_tier=AccessTier.public,
            confidence=0.78,
            reason='mensagem aparenta ser institucional, de servico escolar ou de faq publica',
        )
    else:
        classification = IntentClassification(
            domain=QueryDomain.unknown,
            access_tier=AccessTier.public,
            confidence=0.35,
            reason='mensagem nao tem sinal suficiente para dominio unico',
        )

    return {
        'classification': classification,
        'graph_path': _append_path(state, 'classify_request'),
    }


def security_gate(state: OrchestrationState) -> OrchestrationState:
    request = state['request']
    classification = state['classification']
    risk_flags = list(state.get('risk_flags', []))
    needs_authentication = (
        classification.access_tier in {AccessTier.authenticated, AccessTier.sensitive}
        and not request.user.authenticated
    )

    if classification.access_tier is AccessTier.sensitive:
        risk_flags.append('sensitive_data_path')
    if request.user.role is UserRole.anonymous and classification.domain in {
        QueryDomain.academic,
        QueryDomain.finance,
    }:
        risk_flags.append('anonymous_user_requested_protected_domain')

    return {
        'needs_authentication': needs_authentication,
        'risk_flags': risk_flags,
        'graph_path': _append_path(state, 'security_gate'),
    }


def route_request(state: OrchestrationState, runtime: GraphRuntimeConfig) -> OrchestrationState:
    request = state['request']
    classification = state['classification']
    message = request.message.lower()

    if classification.domain is QueryDomain.unknown:
        route = OrchestrationMode.clarify.value
        reason = 'a intencao esta ambigua e exige clarificacao antes de recuperar contexto'
    elif state.get('needs_authentication'):
        route = OrchestrationMode.deny.value
        reason = 'a consulta exige autenticacao ou vinculo antes de qualquer acesso'
    elif classification.domain is QueryDomain.support and request.allow_handoff:
        route = OrchestrationMode.handoff.value
        reason = 'o usuario demonstrou necessidade de atendimento humano ou operacional'
    elif classification.domain in {QueryDomain.academic, QueryDomain.finance}:
        route = OrchestrationMode.structured_tool.value
        reason = 'dados estruturados devem passar por service deterministico'
    elif classification.domain is QueryDomain.institution and _is_public_school_profile_request(message):
        route = OrchestrationMode.structured_tool.value
        reason = 'fato institucional canonico deve vir de fonte estruturada'
    elif runtime['graph_rag_enabled'] and request.allow_graph_rag and _contains_any(message, GRAPH_RAG_TERMS):
        route = OrchestrationMode.graph_rag.value
        reason = 'a pergunta pede visao global ou conexoes multi-documento'
    else:
        route = OrchestrationMode.hybrid_retrieval.value
        reason = 'retrieval hibrido e o caminho padrao para faq e documentos'

    return {
        'route': route,
        'reason': reason,
        'graph_path': _append_path(state, 'route_request'),
    }


def hybrid_retrieval(state: OrchestrationState) -> OrchestrationState:
    classification = state['classification']
    selected_tools = ['search_public_documents']

    if classification.domain is QueryDomain.calendar:
        selected_tools.append('get_school_calendar')

    return {
        'retrieval_backend': RetrievalBackend.qdrant_hybrid.value,
        'selected_tools': selected_tools,
        'citations_required': True,
        'output_contract': 'resposta com citacoes documentais e, quando houver, calendario estruturado consolidado',
        'graph_path': _append_path(state, 'hybrid_retrieval'),
    }


def graph_rag_retrieval(state: OrchestrationState) -> OrchestrationState:
    return {
        'retrieval_backend': RetrievalBackend.graph_rag.value,
        'selected_tools': ['search_public_documents'],
        'citations_required': True,
        'risk_flags': [*state.get('risk_flags', []), 'advanced_retrieval_path'],
        'output_contract': 'resposta sintetica com citacoes e suporte multi-documento via artefatos de graph rag',
        'graph_path': _append_path(state, 'graph_rag_retrieval'),
    }


def structured_tool_call(state: OrchestrationState) -> OrchestrationState:
    classification = state['classification']
    request = state['request']

    if classification.domain is QueryDomain.institution:
        selected_tools = ['get_public_school_profile']
        output_contract = 'fato institucional publico canonico e verificavel'
    elif classification.domain is QueryDomain.academic:
        if request.user.role is UserRole.teacher:
            selected_tools = ['get_teacher_schedule']
            output_contract = 'grade docente e informacoes operacionais permitidas ao professor'
        else:
            selected_tools = ['get_student_academic_summary', 'get_student_attendance', 'get_student_grades']
            output_contract = 'dados academicos autorizados, auditaveis e minimizados'
    else:
        selected_tools = ['get_financial_summary']
        output_contract = 'dados financeiros autorizados, auditaveis e com trilha reforcada'

    return {
        'retrieval_backend': RetrievalBackend.none.value,
        'selected_tools': selected_tools,
        'citations_required': False,
        'output_contract': output_contract,
        'graph_path': _append_path(state, 'structured_tool_call'),
    }


def handoff(state: OrchestrationState) -> OrchestrationState:
    return {
        'retrieval_backend': RetrievalBackend.none.value,
        'selected_tools': ['create_support_ticket', 'handoff_to_human'],
        'citations_required': False,
        'output_contract': 'encaminhamento humano com resumo seguro e protocolo de atendimento',
        'graph_path': _append_path(state, 'handoff'),
    }


def deny(state: OrchestrationState) -> OrchestrationState:
    return {
        'retrieval_backend': RetrievalBackend.none.value,
        'selected_tools': [],
        'citations_required': False,
        'risk_flags': [*state.get('risk_flags', []), 'authentication_required'],
        'output_contract': 'negacao segura com orientacao de autenticacao ou vinculo',
        'graph_path': _append_path(state, 'deny'),
    }


def clarify(state: OrchestrationState) -> OrchestrationState:
    return {
        'retrieval_backend': RetrievalBackend.none.value,
        'selected_tools': [],
        'citations_required': False,
        'output_contract': 'pedido de clarificacao objetiva para reduzir ambiguidade',
        'graph_path': _append_path(state, 'clarify'),
    }


def to_preview(state: OrchestrationState) -> OrchestrationPreview:
    return OrchestrationPreview(
        mode=OrchestrationMode(state['route']),
        classification=state['classification'],
        retrieval_backend=RetrievalBackend(state.get('retrieval_backend', RetrievalBackend.none.value)),
        selected_tools=state.get('selected_tools', []),
        citations_required=state.get('citations_required', False),
        needs_authentication=state.get('needs_authentication', False),
        graph_path=state.get('graph_path', []),
        risk_flags=state.get('risk_flags', []),
        reason=state.get('reason', 'sem razao registrada'),
        output_contract=state.get('output_contract', 'sem contrato definido'),
    )


@lru_cache
def get_graph_blueprint() -> dict[str, object]:
    return {
        'entrypoint': 'classify_request',
        'nodes': [
            'classify_request',
            'security_gate',
            'route_request',
            'hybrid_retrieval',
            'graph_rag_retrieval',
            'structured_tool_call',
            'handoff',
            'deny',
            'clarify',
        ],
        'terminal_routes': [
            OrchestrationMode.hybrid_retrieval.value,
            OrchestrationMode.graph_rag.value,
            OrchestrationMode.structured_tool.value,
            OrchestrationMode.handoff.value,
            OrchestrationMode.deny.value,
            OrchestrationMode.clarify.value,
        ],
    }


@lru_cache
def build_orchestration_graph(graph_rag_enabled: bool) -> object:
    workflow = StateGraph(OrchestrationState)
    runtime: GraphRuntimeConfig = {'graph_rag_enabled': graph_rag_enabled}

    workflow.add_node('classify_request', classify_request)
    workflow.add_node('security_gate', security_gate)
    workflow.add_node('route_request', lambda state: route_request(state, runtime))
    workflow.add_node('hybrid_retrieval', hybrid_retrieval)
    workflow.add_node('graph_rag_retrieval', graph_rag_retrieval)
    workflow.add_node('structured_tool_call', structured_tool_call)
    workflow.add_node('handoff', handoff)
    workflow.add_node('deny', deny)
    workflow.add_node('clarify', clarify)

    workflow.add_edge(START, 'classify_request')
    workflow.add_edge('classify_request', 'security_gate')
    workflow.add_edge('security_gate', 'route_request')
    workflow.add_conditional_edges(
        'route_request',
        lambda state: state['route'],
        {
            OrchestrationMode.hybrid_retrieval.value: 'hybrid_retrieval',
            OrchestrationMode.graph_rag.value: 'graph_rag_retrieval',
            OrchestrationMode.structured_tool.value: 'structured_tool_call',
            OrchestrationMode.handoff.value: 'handoff',
            OrchestrationMode.deny.value: 'deny',
            OrchestrationMode.clarify.value: 'clarify',
        },
    )
    workflow.add_edge('hybrid_retrieval', END)
    workflow.add_edge('graph_rag_retrieval', END)
    workflow.add_edge('structured_tool_call', END)
    workflow.add_edge('handoff', END)
    workflow.add_edge('deny', END)
    workflow.add_edge('clarify', END)
    return workflow.compile()
