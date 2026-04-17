from __future__ import annotations

# ruff: noqa: F401,F403,F405

LOCAL_EXTRACTED_NAMES = {'classify_request', 'route_request'}

from . import graph as _native
from .extracted_module_contracts import refresh_extracted_module_contract
from .graph_classification_contract import GRAPH_CLASSIFICATION_CONTRACT


def _refresh_native_namespace() -> None:
    refresh_extracted_module_contract(
        native_module=_native,
        namespace=globals(),
        contract_names=GRAPH_CLASSIFICATION_CONTRACT,
        local_extracted_names=LOCAL_EXTRACTED_NAMES,
        contract_label='graph_classification_runtime',
    )


def classify_request(state: OrchestrationState) -> OrchestrationState:
    _refresh_native_namespace()
    request = state['request']
    message = _normalize_text(request.message)

    if _is_authenticated_actor_identity_query(message, authenticated=request.user.authenticated):
        classification = IntentClassification(
            domain=QueryDomain.institution,
            access_tier=AccessTier.authenticated,
            confidence=0.92,
            reason='mensagem autenticada pede identidade da conta atual ou o nome do perfil logado',
        )
    elif _is_authenticated_access_scope_query(message, authenticated=request.user.authenticated):
        classification = IntentClassification(
            domain=QueryDomain.institution,
            access_tier=AccessTier.authenticated,
            confidence=0.93,
            reason='mensagem autenticada pede escopo de acesso, dados liberados e capacidade da conta vinculada',
        )
    elif _is_authenticated_linked_students_query(message, authenticated=request.user.authenticated):
        classification = IntentClassification(
            domain=QueryDomain.institution,
            access_tier=AccessTier.authenticated,
            confidence=0.93,
            reason='mensagem autenticada pede a lista de alunos vinculados a esta conta',
        )
    elif _is_authenticated_admin_query(message, authenticated=request.user.authenticated):
        classification = IntentClassification(
            domain=QueryDomain.institution,
            access_tier=AccessTier.authenticated,
            confidence=0.9,
            reason='mensagem autenticada pede status cadastral, documentacao pessoal ou atualizacao administrativa',
        )
    elif _is_authenticated_personal_finance_query(message, authenticated=request.user.authenticated):
        classification = IntentClassification(
            domain=QueryDomain.finance,
            access_tier=AccessTier.sensitive,
            confidence=0.91,
            reason='mensagem autenticada pede situacao financeira pessoal, vencimentos ou proximos passos da familia',
        )
    elif _is_admin_finance_combined_query(message) and request.user.authenticated:
        classification = IntentClassification(
            domain=QueryDomain.finance,
            access_tier=AccessTier.sensitive,
            confidence=0.95,
            reason='mensagem autenticada combina pendencias administrativas e situacao financeira no mesmo pedido',
        )
    elif _is_authenticated_student_assessment_query(message, authenticated=request.user.authenticated):
        classification = IntentClassification(
            domain=QueryDomain.academic,
            access_tier=AccessTier.authenticated,
            confidence=0.92,
            reason='mensagem autenticada pede panorama academico, vulnerabilidades ou componentes de aluno vinculado',
        )
    elif _is_structured_support_workflow_request(message):
        classification = IntentClassification(
            domain=QueryDomain.support,
            access_tier=AccessTier.public,
            confidence=0.89,
            reason='mensagem pede uma acao institucional estruturada, como visita ou solicitacao formal',
        )
    elif _is_restricted_document_query(message):
        classification = IntentClassification(
            domain=QueryDomain.institution,
            access_tier=AccessTier.authenticated,
            confidence=0.98,
            reason='mensagem pede consulta a documento interno e deve seguir politica de acesso restrito',
        )
    elif _wants_human_support(message):
        classification = IntentClassification(
            domain=QueryDomain.support,
            access_tier=AccessTier.public,
            confidence=0.92,
            reason='mensagem contem termos de atendimento humano ou suporte',
        )
    elif _is_cross_document_public_query(message) or _is_known_public_doc_bundle_query(message):
        classification = IntentClassification(
            domain=QueryDomain.institution,
            access_tier=AccessTier.public,
            confidence=0.97,
            reason='mensagem pede sintese publica multi-documento e nao deve herdar contexto autenticado de aluno',
        )
    elif _is_teacher_self_service_request(message, request.user.role):
        classification = IntentClassification(
            domain=QueryDomain.academic,
            access_tier=AccessTier.authenticated,
            confidence=0.94,
            reason='mensagem indica autoatendimento docente sobre turmas, disciplinas ou horario',
        )
    elif _is_authenticated_student_assessment_query(message, authenticated=request.user.authenticated):
        classification = IntentClassification(
            domain=QueryDomain.academic,
            access_tier=AccessTier.authenticated,
            confidence=0.91,
            reason='mensagem autenticada pede avaliacoes, provas ou agenda academica de aluno vinculado',
        )
    elif _is_authenticated_student_registry_query(message, authenticated=request.user.authenticated):
        classification = IntentClassification(
            domain=QueryDomain.academic,
            access_tier=AccessTier.authenticated,
            confidence=0.9,
            reason='mensagem autenticada pede identificador academico ou matricula de aluno vinculado',
        )
    elif _is_authenticated_finance_attribute_query(message, authenticated=request.user.authenticated):
        classification = IntentClassification(
            domain=QueryDomain.finance,
            access_tier=AccessTier.sensitive,
            confidence=0.9,
            reason='mensagem autenticada pede identificador financeiro sensivel, como boleto ou contrato',
        )
    elif _is_authenticated_personal_finance_query(message, authenticated=request.user.authenticated):
        classification = IntentClassification(
            domain=QueryDomain.finance,
            access_tier=AccessTier.sensitive,
            confidence=0.89,
            reason='mensagem autenticada pede situacao financeira pessoal, vencimentos ou mensalidades de aluno vinculado',
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
    elif _is_public_staff_directory_query(message):
        classification = IntentClassification(
            domain=QueryDomain.institution,
            access_tier=AccessTier.public,
            confidence=0.8,
            reason='mensagem pede informacao publica sobre nomes ou contatos de profissionais da escola',
        )
    elif _is_public_feature_query(message):
        classification = IntentClassification(
            domain=QueryDomain.institution,
            access_tier=AccessTier.public,
            confidence=0.82,
            reason='mensagem pergunta sobre estrutura, oferta ou atividades publicas da escola',
        )
    elif _contains_any(message, PUBLIC_CALENDAR_TERMS) or _is_public_timeline_query(message):
        classification = IntentClassification(
            domain=QueryDomain.calendar,
            access_tier=AccessTier.public,
            confidence=0.84,
            reason='mensagem contem termos de calendario e eventos escolares',
        )
    elif _is_public_school_profile_request(message) or _is_public_utility_query(message):
        classification = IntentClassification(
            domain=QueryDomain.institution,
            access_tier=AccessTier.public,
            confidence=0.84,
            reason='mensagem pede um fato publico canonico, um dado operacional ou uma referencia institucional estruturada',
        )
    elif _is_public_policy_query(message):
        classification = IntentClassification(
            domain=QueryDomain.institution,
            access_tier=AccessTier.public,
            confidence=0.86,
            reason='mensagem pede regra institucional publica, politica escolar ou criterio pedagogico divulgado',
        )
    elif _is_public_attribute_followup_query(message):
        classification = IntentClassification(
            domain=QueryDomain.institution,
            access_tier=AccessTier.public,
            confidence=0.79,
            reason='mensagem curta depende de contexto recente para resolver atributo publico institucional',
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

def route_request(state: OrchestrationState, runtime: GraphRuntimeConfig) -> OrchestrationState:
    _refresh_native_namespace()
    from .runtime_core import (
        looks_like_school_scope_message as _looks_like_school_scope_message_local,
        looks_like_scope_boundary_candidate as _looks_like_scope_boundary_candidate_local,
    )

    request = state['request']
    classification = state['classification']
    message = request.message.lower()
    support_public_rescue = (
        classification.domain is QueryDomain.support
        and (
            _is_public_school_profile_request(message)
            or _is_public_navigation_query(message)
            or _is_public_timeline_query(message)
            or _is_public_calendar_event_query(message)
        )
    )

    if _is_restricted_document_query(message) and not _can_read_restricted_documents(request):
        route = OrchestrationMode.deny.value
        reason = 'documentos internos exigem perfil com autorizacao explicita para leitura restrita'
    elif _is_restricted_document_query(message):
        route = OrchestrationMode.hybrid_retrieval.value
        reason = 'consulta autenticada de documento interno deve usar retrieval restrito com grounding'
    elif _looks_like_scope_boundary_candidate_local(message) and not _looks_like_school_scope_message_local(message):
        route = OrchestrationMode.structured_tool.value
        reason = 'mensagem explicitamente fora do escopo escolar e deve responder por boundary deterministico'
    elif _is_known_public_doc_bundle_query(message):
        route = OrchestrationMode.structured_tool.value
        reason = 'bundle publico canonico deve seguir lane publica mesmo se a classificacao superestimar autenticacao'
    elif classification.domain is QueryDomain.unknown:
        route = OrchestrationMode.clarify.value
        reason = 'a intencao esta ambigua e exige clarificacao antes de recuperar contexto'
    elif state.get('needs_authentication'):
        route = OrchestrationMode.deny.value
        reason = 'a consulta exige autenticacao ou vinculo antes de qualquer acesso'
    elif support_public_rescue:
        route = OrchestrationMode.structured_tool.value
        reason = 'consulta publica de navegacao e canais foi resgatada do dominio support'
    elif classification.domain is QueryDomain.support and _is_structured_support_workflow_request(message):
        route = OrchestrationMode.structured_tool.value
        reason = 'a solicitacao pode ser executada por workflow estruturado com protocolo'
    elif classification.domain is QueryDomain.support and request.allow_handoff:
        route = OrchestrationMode.handoff.value
        reason = 'o usuario demonstrou necessidade de atendimento humano ou operacional'
    elif classification.domain in {QueryDomain.academic, QueryDomain.finance}:
        route = OrchestrationMode.structured_tool.value
        reason = 'dados estruturados devem passar por service deterministico'
    elif classification.domain is QueryDomain.calendar and (
        _is_public_timeline_query(message) or _is_public_calendar_event_query(message)
    ):
        route = OrchestrationMode.structured_tool.value
        reason = 'datas institucionais publicas devem vir de leitura estruturada e auditavel'
    elif classification.domain is QueryDomain.institution and _is_authenticated_admin_query(
        _normalize_text(message),
        authenticated=request.user.authenticated,
    ):
        route = OrchestrationMode.structured_tool.value
        reason = 'status administrativo autenticado exige service deterministico'
    elif classification.domain is QueryDomain.institution and _is_authenticated_actor_identity_query(
        _normalize_text(message),
        authenticated=request.user.authenticated,
    ):
        route = OrchestrationMode.structured_tool.value
        reason = 'identidade da conta autenticada exige leitura protegida e minimizada'
    elif classification.domain is QueryDomain.institution and (
        _is_authenticated_access_scope_query(
            _normalize_text(message),
            authenticated=request.user.authenticated,
        )
        or _is_authenticated_linked_students_query(
            _normalize_text(message),
            authenticated=request.user.authenticated,
        )
    ):
        route = OrchestrationMode.structured_tool.value
        reason = 'capacidade da conta autenticada e alunos vinculados exigem leitura protegida e minimizada'
    elif (
        _is_known_public_doc_bundle_query(message)
        or (
            classification.domain is QueryDomain.institution
            and (
                _is_public_school_profile_request(message)
                or _is_public_navigation_query(message)
                or _is_public_document_submission_query(message)
                or _is_public_attribute_followup_query(message)
                or _is_public_utility_query(message)
            )
        )
    ):
        route = OrchestrationMode.structured_tool.value
        reason = 'fato institucional canonico deve vir de fonte estruturada'
    elif runtime['graph_rag_enabled'] and request.allow_graph_rag and (
        _contains_any(message, GRAPH_RAG_TERMS) or _is_cross_document_public_query(message)
    ):
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
