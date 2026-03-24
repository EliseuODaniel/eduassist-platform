from __future__ import annotations

from functools import lru_cache
import re
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
    'mensalidades',
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
PUBLIC_PRICING_TERMS = {
    'mensalidade',
    'mensalidades',
    'valor',
    'valores',
    'preco',
    'precos',
    'preço',
    'preços',
    'bolsa',
    'bolsas',
    'desconto',
    'descontos',
    'taxa de matricula',
    'taxa de matrícula',
}
PERSONAL_FINANCE_TERMS = {
    'meu filho',
    'minha filha',
    'minha conta',
    'meu boleto',
    'meus boletos',
    'minha mensalidade',
    'meu financeiro',
    'minhas faturas',
    'minhas contas',
    'segunda via',
    'fatura',
    'faturas',
    'boleto',
    'boletos',
    'inadimplencia',
    'inadimplência',
    'vencido',
    'vencida',
    'pagamento',
    'pagamentos',
    'quitado',
    'quitada',
    'todos os alunos',
    'todas as mensalidades',
    'de todos os alunos',
    'de todos os estudantes',
    'todos os contratos',
    'lista de mensalidades',
    'planilha de mensalidades',
}
SUPPORT_TERMS = {'humano', 'atendente', 'suporte', 'protocolo', 'chamado'}
SUPPORT_PHRASES = {
    'falar com',
    'atendimento humano',
    'ajuda humana',
    'me transfira',
    'me encaminhe',
}
VISIT_ACTION_TERMS = {
    'agendar visita',
    'agendamento de visita',
    'marcar visita',
    'quero visitar',
    'quero conhecer a escola',
    'visita guiada',
    'tour',
}
INSTITUTIONAL_REQUEST_TERMS = {
    'solicitacao a direcao',
    'solicitação à direção',
    'solicitacao para a direcao',
    'solicitação para a direção',
    'pedido para a diretora',
    'pedido para a direcao',
    'requerimento',
    'protocolar',
    'protocolo formal',
    'ouvidoria',
}
WORKFLOW_STATUS_TERMS = {
    'status',
    'andamento',
    'situacao',
    'situação',
    'fila',
    'retorno',
    'atualizacao',
    'atualização',
}
WORKFLOW_REFERENT_TERMS = {
    'protocolo',
    'pedido',
    'solicitacao',
    'solicitação',
    'requerimento',
    'visita',
    'tour',
    'chamado',
    'atendimento',
    'direcao',
    'direção',
    'ouvidoria',
}
WORKFLOW_STATUS_OWNERSHIP_TERMS = {
    'meu pedido',
    'minha solicitacao',
    'minha solicitação',
    'meu protocolo',
    'minha visita',
    'essa solicitacao',
    'essa solicitação',
    'esse pedido',
    'esse protocolo',
}
PROTOCOL_CODE_PATTERN = re.compile(r'\b(?:VIS|REQ|ATD)-[A-Z0-9-]+\b', re.IGNORECASE)
GRAPH_RAG_TERMS = {'visao geral', 'compare', 'comparar', 'tendencias', 'corpus', 'relacione'}
TEACHER_SELF_SERVICE_TERMS = {'horario', 'agenda', 'turma', 'turmas', 'disciplina', 'disciplinas', 'materia', 'materias'}
PUBLIC_SERVICE_TERMS = {
    'biblioteca',
    'cantina',
    'laboratorio',
    'laboratorio de ciencias',
    'espaco maker',
    'maker',
    'academia',
    'piscina',
    'quadra',
    'quadra de tenis',
    'tenis',
    'futebol',
    'futsal',
    'volei',
    'esporte',
    'esportes',
    'aula de danca',
    'aulas de danca',
    'danca',
    'danca',
    'atividade extracurricular',
    'atividades extracurriculares',
    'teatro',
    'robotica',
    'robótica',
    'uniforme',
    'almoco',
    'almoço',
    'transporte',
    'van escolar',
    'orientacao educacional',
    'orientação educacional',
    'portaria',
    'secretaria',
    'atendimento',
    'funcionamento',
    'horario de atendimento',
    'o que voce faz',
    'o que você faz',
    'como voce pode me ajudar',
    'como você pode me ajudar',
    'no que voce pode ajudar',
    'no que você pode ajudar',
    'assunto',
    'assuntos',
    'opcoes de assuntos',
    'opções de assuntos',
    'com quem eu falo',
    'pra quem eu falo',
    'para quem eu falo',
    'quem cuida',
    'quem resolve',
    'qual setor',
    'quem e voce',
    'quem é você',
    'voce e quem',
    'você é quem',
    'oi',
    'ola',
    'olá',
    'bom dia',
    'boa tarde',
    'boa noite',
}
INSTITUTION_TERMS = {
    'escola',
    'matricula',
    'documento',
    'documentos',
    'comprovante',
    'comprovantes',
    'historico',
    'historico escolar',
    'cadastro',
    'ficha cadastral',
    'formulario cadastral',
    'regimento',
    'instituicao',
    'endereco',
    'telefone',
    'contato',
    'turno',
    'turnos',
    'horario',
    'horários',
    'horario de aula',
    'horário de aula',
    'fundamental',
    'fundamental ii',
    'ensino medio',
    'ensino médio',
    '6o ano',
    '7o ano',
    '8o ano',
    '9o ano',
    '1o ano',
    '2o ano',
    '3o ano',
    'confessional',
    'laica',
    'religiosa',
    'diretora',
    'diretor',
    'direcao',
    'direção',
    'coordenacao',
    'coordenação',
    'lideranca',
    'liderança',
    'media de aprovacao',
    'média de aprovação',
    'aprovacao',
    'aprovação',
    'indicador',
    'indicadores',
    'curiosidade',
    'curiosidades',
    'diferencial',
    'diferenciais',
    'visita',
    'visitas',
    'tour',
}
PUBLIC_SCHOOL_PROFILE_TERMS = {
    'nome da escola',
    'nome do colegio',
    'nome do colégio',
    'como se chama a escola',
    'como se chama o colegio',
    'como se chama o colégio',
    'telefone da escola',
    'telefone da secretaria',
    'whatsapp da escola',
    'whatsapp da secretaria',
    'email da escola',
    'email da secretaria',
    'canais oficiais de contato',
    'canais de contato',
    'como entrar em contato',
    'fale conosco',
    'endereco da escola',
    'endereço da escola',
    'turno',
    'turnos',
    'horario do ensino medio',
    'horário do ensino médio',
    'horario do fundamental',
    'horário do fundamental',
    'fundamental',
    'fundamental ii',
    'ensino medio',
    'ensino médio',
    '6o ano',
    '7o ano',
    '8o ano',
    '9o ano',
    '1o ano',
    '2o ano',
    '3o ano',
    'periodo integral',
    'período integral',
    'mensalidade',
    'mensalidades',
    'bolsa',
    'desconto',
    'confessional',
    'laica',
    'religiosa',
    'diretora',
    'diretor',
    'direcao',
    'direção',
    'coordenacao',
    'coordenação',
    'lideranca',
    'liderança',
    'aprovacao',
    'aprovação',
    'media de aprovacao',
    'média de aprovação',
    'indicador',
    'indicadores',
    'curiosidade',
    'curiosidades',
    'diferencial',
    'diferenciais',
    'visita',
    'visitas',
    'visita guiada',
    'tour',
    'conhecer a escola',
    'agendar visita',
    'solicitacao a direcao',
    'solicitação à direção',
    'o que voce faz',
    'o que você faz',
    'como voce pode me ajudar',
    'como você pode me ajudar',
    'quais assuntos',
    'opcoes de assuntos',
    'opções de assuntos',
    'com quem eu falo',
    'pra quem eu falo',
    'para quem eu falo',
    'quem cuida',
    'quem resolve',
    'qual setor',
    'quem e voce',
    'quem é você',
    'voce e quem',
    'você é quem',
    'oi',
    'ola',
    'olá',
    'bom dia',
    'boa tarde',
    'boa noite',
    'biblioteca',
    'cantina',
    'laboratorio',
    'academia',
    'piscina',
    'quadra',
    'futebol',
    'danca',
    'dança',
    'teatro',
    'robotica',
    'robótica',
}


def _append_path(state: OrchestrationState, node_name: str) -> list[str]:
    return [*state.get('graph_path', []), node_name]


def _normalize_text(text: str) -> str:
    normalized = unicodedata.normalize('NFKD', text)
    without_accents = ''.join(char for char in normalized if not unicodedata.combining(char))
    return without_accents.replace('º', 'o').replace('ª', 'a').lower()


def _message_matches_term(message: str, term: str) -> bool:
    normalized_term = _normalize_text(term).strip()
    if not normalized_term:
        return False
    pattern = r'(?<!\w)' + r'\s+'.join(re.escape(part) for part in normalized_term.split()) + r'(?!\w)'
    return re.search(pattern, message) is not None


def _contains_any(message: str, terms: set[str]) -> bool:
    lowered = _normalize_text(message)
    return any(_message_matches_term(lowered, term) for term in terms)


def _wants_human_support(message: str) -> bool:
    lowered = _normalize_text(message)
    return any(term in lowered for term in SUPPORT_TERMS) or any(
        phrase in lowered for phrase in SUPPORT_PHRASES
    )


def _is_visit_booking_request(message: str) -> bool:
    lowered = _normalize_text(message)
    if any(_message_matches_term(lowered, term) for term in VISIT_ACTION_TERMS):
        return True
    scheduling_verbs = {'agendar', 'agendamento', 'marcar', 'reservar'}
    visit_targets = {'visita', 'visita guiada', 'tour', 'conhecer a escola', 'conhecer o colegio', 'conhecer o colégio'}
    return _contains_any(lowered, scheduling_verbs) and _contains_any(lowered, visit_targets)


def _is_institutional_request(message: str) -> bool:
    lowered = _normalize_text(message)
    if any(_message_matches_term(lowered, term) for term in INSTITUTIONAL_REQUEST_TERMS):
        return True
    request_verbs = {'solicitar', 'solicitacao', 'solicitação', 'protocolar', 'encaminhar', 'formalizar'}
    leadership_targets = {'direcao', 'direção', 'diretora', 'diretor', 'ouvidoria'}
    return _contains_any(lowered, request_verbs) and _contains_any(lowered, leadership_targets)


def _has_protocol_code(message: str) -> bool:
    return PROTOCOL_CODE_PATTERN.search(message) is not None


def _is_workflow_status_request(message: str) -> bool:
    lowered = _normalize_text(message)
    if _has_protocol_code(message) and _contains_any(lowered, WORKFLOW_STATUS_TERMS | {'protocolo'}):
        return True
    if _contains_any(lowered, WORKFLOW_STATUS_TERMS) and _contains_any(
        lowered,
        WORKFLOW_REFERENT_TERMS | WORKFLOW_STATUS_OWNERSHIP_TERMS,
    ):
        return True
    return False


def _is_structured_support_workflow_request(message: str) -> bool:
    return _is_visit_booking_request(message) or _is_institutional_request(message) or _is_workflow_status_request(message)


def _is_teacher_self_service_request(message: str, role: UserRole) -> bool:
    lowered = _normalize_text(message)
    return role is UserRole.teacher and any(term in lowered for term in TEACHER_SELF_SERVICE_TERMS)


def _is_public_pricing_query(message: str) -> bool:
    lowered = _normalize_text(message)
    if not any(_message_matches_term(lowered, term) for term in PUBLIC_PRICING_TERMS):
        return False
    if any(_message_matches_term(lowered, term) for term in PERSONAL_FINANCE_TERMS):
        return False
    return True


def _is_public_navigation_query(message: str) -> bool:
    lowered = _normalize_text(message)
    navigation_terms = {
        'oi',
        'ola',
        'olá',
        'bom dia',
        'boa tarde',
        'boa noite',
        'o que voce faz',
        'o que você faz',
        'como voce pode me ajudar',
        'como você pode me ajudar',
        'quais assuntos',
        'opcoes de assuntos',
        'opções de assuntos',
        'com quem eu falo',
        'pra quem eu falo',
        'para quem eu falo',
        'quem cuida',
        'quem resolve',
        'qual setor',
        'qual area',
        'qual área',
        'quem e voce',
        'quem é você',
        'voce e quem',
        'você é quem',
    }
    return any(_message_matches_term(lowered, term) for term in navigation_terms)


def _is_public_school_profile_request(message: str) -> bool:
    lowered = _normalize_text(message)
    return _is_public_pricing_query(lowered) or any(
        _message_matches_term(lowered, term) for term in PUBLIC_SCHOOL_PROFILE_TERMS
    )


def classify_request(state: OrchestrationState) -> OrchestrationState:
    request = state['request']
    message = _normalize_text(request.message)

    if _is_structured_support_workflow_request(message):
        classification = IntentClassification(
            domain=QueryDomain.support,
            access_tier=AccessTier.public,
            confidence=0.89,
            reason='mensagem pede uma acao institucional estruturada, como visita ou solicitacao formal',
        )
    elif _wants_human_support(message):
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
    elif _is_public_pricing_query(message):
        classification = IntentClassification(
            domain=QueryDomain.institution,
            access_tier=AccessTier.public,
            confidence=0.86,
            reason='mensagem pede informacao comercial publica da escola, nao financeiro pessoal',
        )
    elif _is_public_navigation_query(message):
        classification = IntentClassification(
            domain=QueryDomain.institution,
            access_tier=AccessTier.public,
            confidence=0.88,
            reason='mensagem pede navegacao institucional, apresentacao do assistente ou direcionamento por setor',
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
    elif _contains_any(message, PUBLIC_SERVICE_TERMS | INSTITUTION_TERMS):
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
    elif classification.domain is QueryDomain.support and _is_structured_support_workflow_request(message):
        route = OrchestrationMode.structured_tool.value
        reason = 'a solicitacao pode ser executada por workflow estruturado com protocolo'
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
    normalized_message = _normalize_text(request.message)

    if classification.domain is QueryDomain.institution:
        selected_tools = ['get_public_school_profile']
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
            selected_tools.append('list_assistant_capabilities')
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
            selected_tools.append('get_service_directory')
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
                'coordenacao',
                'coordenação',
                'lideranca',
                'liderança',
            }
        ):
            selected_tools.append('get_org_directory')
        output_contract = 'fato institucional publico, navegacao de atendimento e orientacao de concierge'
    elif classification.domain is QueryDomain.support:
        if _is_workflow_status_request(request.message):
            selected_tools = ['get_workflow_status']
            output_contract = 'consulta de status de protocolo, visita ou solicitacao institucional ja registrada'
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
