from __future__ import annotations

import re
import unicodedata
from typing import Any

from pydantic import BaseModel, Field
from eduassist_semantic_ingress import build_turn_frame_hint

from .entity_resolution import ResolvedEntityHints, resolve_entity_hints
from .models import (
    AccessTier,
    IntentClassification,
    MessageResponseRequest,
    OrchestrationMode,
    OrchestrationPreview,
    QueryDomain,
    RetrievalBackend,
)
from .public_doc_knowledge import match_public_canonical_lane
from .request_intent_guardrails import (
    looks_like_explicit_admin_status_query,
    looks_like_high_confidence_public_school_faq,
)
from .turn_frame_policy import (
    append_turn_frame_graph_path,
    append_turn_frame_reason,
    turn_frame_access_tier,
    turn_frame_canonical_lane,
    turn_frame_public_selected_tools,
    turn_frame_query_domain,
)


class KernelExecutionStep(BaseModel):
    name: str
    purpose: str
    stage: str


class KernelPlan(BaseModel):
    stack_name: str
    mode: str
    slice_name: str
    preview: OrchestrationPreview
    entities: ResolvedEntityHints
    execution_steps: list[KernelExecutionStep] = Field(default_factory=list)
    plan_notes: list[str] = Field(default_factory=list)


class KernelReflection(BaseModel):
    grounded: bool = True
    verifier_reason: str | None = None
    fallback_used: bool = False
    answer_judge_used: bool = False
    notes: list[str] = Field(default_factory=list)


class KernelRunResult(BaseModel):
    plan: KernelPlan
    reflection: KernelReflection
    response: dict[str, Any]


ACADEMIC_TERMS = {
    'academico',
    'acadêmico',
    'panorama academico',
    'panorama acadêmico',
    'quadro academico',
    'quadro acadêmico',
    'pontos academicos',
    'pontos acadêmicos',
    'preocupacao academica',
    'preocupação acadêmica',
    'preocupacoes academicas',
    'preocupações acadêmicas',
    'nota',
    'notas',
    'boletim',
    'media',
    'média',
    'frequencia',
    'frequência',
    'falta',
    'faltas',
    'avaliacao',
    'avaliação',
    'avaliacoes',
    'avaliações',
    'prova',
    'provas',
    'bimestre',
    'disciplina',
    'disciplinas',
    'historia',
    'história',
    'matematica',
    'matemática',
    'ingles',
    'inglês',
}
FINANCE_TERMS = {
    'financeiro',
    'mensalidade',
    'mensalidades',
    'boleto',
    'boletos',
    'fatura',
    'faturas',
    'pagamento',
    'pagamentos',
    'em aberto',
    'vencimento',
    'vencida',
    'vencidas',
}
CALENDAR_TERMS = {'calendario', 'calendário', 'evento', 'eventos', 'feriado', 'reuniao', 'reunião', 'data', 'datas'}
PUBLIC_PRICING_TERMS = {
    'preco',
    'preço',
    'precos',
    'preços',
    'valor',
    'valores',
    'mensalidade',
    'matricula',
    'matrícula',
    'bolsa',
    'desconto',
}
PROCESS_TERMS = {
    'rematricula',
    'rematrícula',
    'transferencia',
    'transferência',
    'cancelamento',
    'documentacao',
    'documentação',
    'cadastro',
    'visita',
    'secretaria',
    'coordenacao',
    'coordenação',
    'portal',
    'site',
    'instagram',
    'endereco',
    'endereço',
    'horario',
    'horário',
}
PUBLIC_DIRECTORY_TERMS = {
    'contato',
    'contatos',
    'telefone',
    'fone',
    'email',
    'e-mail',
    'whatsapp',
    'diretor',
    'diretora',
    'direcao',
    'direção',
    'diretoria',
    'coordenador',
    'coordenadora',
    'coordenacao',
    'coordenação',
}
PUBLIC_FACT_TERMS = {
    'site',
    'instagram',
    'endereco',
    'endereço',
    'bairro',
    'cep',
    'horario',
    'horário',
    'mensalidade',
    'matricula',
    'matrícula',
    'bolsa',
    'desconto',
}
DOCUMENTARY_TERMS = {
    'como funciona',
    'me explique',
    'explique',
    'quero entender',
    'comparativa',
    'comparar',
    'comparacao',
    'comparação',
    'diferenca',
    'diferença',
    'politica',
    'política',
    'protocolo',
    'orientacao',
    'orientação',
    'regra',
    'regras',
    'documento',
    'documentos',
}
RESTRICTED_DOC_TERMS = {
    'documento interno',
    'documentos internos',
    'playbook',
    'manual interno',
    'manual do professor',
    'procedimento interno',
    'fluxo interno',
    'protocolo interno',
    'escopo parcial',
}
GREETING_TERMS = {'oi', 'ola', 'olá', 'oie', 'bom dia', 'boa tarde', 'boa noite'}


def _normalize(text: str) -> str:
    lowered = unicodedata.normalize('NFKD', str(text or '')).encode('ascii', 'ignore').decode('ascii').lower()
    return re.sub(r'\s+', ' ', lowered).strip()


def _contains_any(text: str, terms: set[str]) -> bool:
    normalized = _normalize(text)
    return any(term in normalized for term in terms)


def _classify_domain(message: str, *, authenticated: bool) -> QueryDomain:
    if looks_like_high_confidence_public_school_faq(message):
        return QueryDomain.institution
    if authenticated and looks_like_explicit_admin_status_query(message, authenticated=authenticated):
        return QueryDomain.institution
    if authenticated and _contains_any(message, FINANCE_TERMS):
        return QueryDomain.finance
    if _contains_any(message, ACADEMIC_TERMS):
        return QueryDomain.academic
    if _contains_any(message, CALENDAR_TERMS):
        return QueryDomain.calendar
    if match_public_canonical_lane(message) or _contains_any(
        message,
        PROCESS_TERMS | PUBLIC_PRICING_TERMS | PUBLIC_DIRECTORY_TERMS,
    ):
        return QueryDomain.institution
    return QueryDomain.unknown


def _can_read_restricted_documents(request: MessageResponseRequest) -> bool:
    if any(scope == 'documents:restricted:read' for scope in request.user.scopes):
        return True
    return request.user.role.value in {'staff', 'teacher', 'admin', 'coordinator', 'finance'}


def _protected_selected_tools_for_domain(domain: QueryDomain) -> list[str]:
    if domain is QueryDomain.academic:
        return [
            'get_student_academic_summary',
            'get_student_attendance',
            'get_student_grades',
            'get_student_upcoming_assessments',
            'get_student_attendance_timeline',
        ]
    if domain is QueryDomain.finance:
        return ['get_financial_summary']
    return ['get_administrative_status', 'get_student_administrative_status']


def _public_selected_tools_for_message(message: str) -> list[str]:
    tools = ['get_public_school_profile']
    if _contains_any(message, PUBLIC_PRICING_TERMS):
        tools.append('project_public_pricing')
    return tools


def _looks_like_protected_family_finance_request(message: str) -> bool:
    normalized = _normalize(message)
    explicit_terms = (
        'minha situacao financeira',
        'situacao financeira como se eu fosse leigo',
        'separando mensalidade, taxa, atraso e desconto',
        'separando mensalidade taxa atraso e desconto',
    )
    if any(term in normalized for term in explicit_terms):
        return True
    has_family_anchor = any(term in normalized for term in ('meus filhos', 'meus dois filhos', 'familia', 'família', 'contas vinculadas'))
    if has_family_anchor and any(
        term in normalized
        for term in ('negociar o restante', 'mensalidade parcialmente paga', 'o que ja aparece', 'o que já aparece')
    ):
        return True
    return False


def _looks_like_explicit_public_pricing_request(message: str) -> bool:
    normalized = _normalize(message)
    if not _contains_any(message, PUBLIC_PRICING_TERMS):
        return False
    public_anchors = (
        'tabela publica',
        'tabela pública',
        'valor publico',
        'valor público',
        'valores publicos',
        'valores públicos',
        'valor de referencia',
        'valor de referência',
        'valor de tabela',
        'quanto custa',
        'qual a mensalidade do ensino',
        'qual a matricula do ensino',
        'qual a matrícula do ensino',
        'mensalidade do ensino medio',
        'mensalidade do ensino médio',
        'mensalidade do colegio',
        'matricula do colegio',
        'matrícula do colégio',
        'bolsa da escola',
    )
    return any(anchor in normalized for anchor in public_anchors)


def _build_preview(*, request: MessageResponseRequest, settings: Any) -> OrchestrationPreview:
    turn_frame = build_turn_frame_hint(
        message=request.message,
        conversation_context=None,
        preview=None,
        authenticated=bool(request.user.authenticated),
    )
    authenticated = bool(request.user.authenticated)
    canonical_lane = match_public_canonical_lane(request.message)
    if canonical_lane is None and turn_frame is not None and turn_frame.scope == "public":
        canonical_lane = turn_frame_canonical_lane(turn_frame)
    domain = _classify_domain(request.message, authenticated=authenticated)
    turn_frame_domain = turn_frame_query_domain(turn_frame) if turn_frame is not None else None
    if turn_frame_domain is not None:
        domain = turn_frame_domain
    normalized = _normalize(request.message)
    explicit_admin_request = looks_like_explicit_admin_status_query(
        request.message,
        authenticated=authenticated,
    )
    authenticated_public_profile_request = authenticated and (
        looks_like_high_confidence_public_school_faq(request.message)
        or match_public_canonical_lane(request.message) is not None
        or _contains_any(request.message, PROCESS_TERMS | PUBLIC_DIRECTORY_TERMS)
        or _looks_like_explicit_public_pricing_request(request.message)
        or (
            _contains_any(request.message, DOCUMENTARY_TERMS)
            and any(term in normalized for term in ('escola', 'colegio', 'colegio horizonte'))
        )
        or any(
            phrase in normalized
            for phrase in (
                'politica publica da escola',
                'politica publica do colegio',
                'protocolo publico da escola',
            )
        )
    ) and not _looks_like_protected_family_finance_request(request.message) and not explicit_admin_request

    if canonical_lane is not None:
        mode = OrchestrationMode.structured_tool
        reason = f'llamaindex_local_public_canonical:{canonical_lane}'
        domain = QueryDomain.institution
    elif any(normalized == greeting or normalized.startswith(f'{greeting} ') for greeting in GREETING_TERMS):
        mode = OrchestrationMode.clarify
        reason = 'llamaindex_local_greeting'
    elif authenticated and _contains_any(request.message, RESTRICTED_DOC_TERMS):
        if _can_read_restricted_documents(request):
            mode = OrchestrationMode.hybrid_retrieval
            reason = 'llamaindex_local_restricted_documents'
        else:
            mode = OrchestrationMode.deny
            reason = 'llamaindex_local_restricted_documents_denied'
    elif authenticated and explicit_admin_request:
        mode = OrchestrationMode.structured_tool
        reason = 'llamaindex_local_protected:institution'
    elif authenticated_public_profile_request:
        mode = OrchestrationMode.structured_tool
        reason = 'llamaindex_local_public_fact:institution'
    elif authenticated:
        if domain in {QueryDomain.academic, QueryDomain.finance}:
            mode = OrchestrationMode.structured_tool
            reason = f'llamaindex_local_protected:{domain.value}'
        else:
            mode = OrchestrationMode.clarify
            reason = 'llamaindex_local_clarify'
    elif _contains_any(request.message, DOCUMENTARY_TERMS):
        mode = OrchestrationMode.hybrid_retrieval
        reason = f'llamaindex_local_public_documentary:{domain.value}'
    elif _contains_any(request.message, PUBLIC_FACT_TERMS | PUBLIC_DIRECTORY_TERMS | CALENDAR_TERMS):
        mode = OrchestrationMode.structured_tool
        reason = f'llamaindex_local_public_fact:{domain.value}'
    elif domain is QueryDomain.unknown:
        mode = OrchestrationMode.clarify
        reason = 'llamaindex_local_public_unknown_safe_clarify'
    else:
        mode = OrchestrationMode.hybrid_retrieval
        reason = f'llamaindex_local_public_default:{domain.value}'

    public_institution_request = authenticated_public_profile_request or (
        match_public_canonical_lane(request.message) is not None
        or
        _contains_any(request.message, PROCESS_TERMS | PUBLIC_DIRECTORY_TERMS)
        or _looks_like_explicit_public_pricing_request(request.message)
    ) and not _looks_like_protected_family_finance_request(request.message)
    access_tier = AccessTier.public
    if authenticated and not public_institution_request:
        if explicit_admin_request or domain is QueryDomain.academic:
            access_tier = AccessTier.authenticated
        elif domain is QueryDomain.finance:
            access_tier = AccessTier.sensitive
    turn_frame_access = turn_frame_access_tier(turn_frame) if turn_frame is not None else None
    if turn_frame_access is not None:
        access_tier = turn_frame_access

    if mode is OrchestrationMode.structured_tool:
        selected_tools = (
            _protected_selected_tools_for_domain(domain)
            if authenticated and access_tier is not AccessTier.public
            else _public_selected_tools_for_message(request.message)
        )
        if turn_frame is not None and turn_frame.scope == "public":
            selected_tools = turn_frame_public_selected_tools(turn_frame)
    elif mode is OrchestrationMode.hybrid_retrieval:
        selected_tools = ['search_documents']
    elif mode is OrchestrationMode.deny:
        selected_tools = []
    else:
        selected_tools = []

    output_contract = 'resposta com linguagem natural sustentada por consulta local do workflow'
    if mode is OrchestrationMode.hybrid_retrieval:
        output_contract = 'resposta sustentada por recuperacao de trechos e composicao do workflow'
    elif mode is OrchestrationMode.deny:
        output_contract = 'negativa segura para conteudo interno sem permissao'
    elif mode is OrchestrationMode.clarify:
        output_contract = 'pedido curto de esclarecimento'

    preview_reason = append_turn_frame_reason(reason, turn_frame)

    return OrchestrationPreview(
        mode=mode,
        classification=IntentClassification(
            domain=domain,
            access_tier=access_tier,
            confidence=0.88 if mode is not OrchestrationMode.clarify else 0.64,
            reason=preview_reason,
        ),
        retrieval_backend=RetrievalBackend.qdrant_hybrid if mode is OrchestrationMode.hybrid_retrieval else RetrievalBackend.none,
        selected_tools=selected_tools,
        citations_required=mode is OrchestrationMode.hybrid_retrieval,
        needs_authentication=access_tier is not AccessTier.public and mode is not OrchestrationMode.clarify,
        graph_path=append_turn_frame_graph_path([
            'llamaindex:planner',
            f'domain:{domain.value}',
            f'mode:{mode.value}',
        ], turn_frame),
        risk_flags=['sensitive_data_path'] if access_tier is AccessTier.sensitive else [],
        reason=preview_reason,
        output_contract=output_contract,
    )


def _execution_steps_for_route(preview: OrchestrationPreview) -> list[KernelExecutionStep]:
    if preview.mode is OrchestrationMode.structured_tool:
        return [
            KernelExecutionStep(name='resolver_contexto', purpose='Ler contexto de conversa e entidades ativas.', stage='plan'),
            KernelExecutionStep(name='consultar_servicos', purpose='Consultar dados estruturados da escola.', stage='execute'),
            KernelExecutionStep(name='sintetizar', purpose='Montar resposta curta com foco no pedido.', stage='execute'),
        ]
    if preview.mode is OrchestrationMode.hybrid_retrieval:
        return [
            KernelExecutionStep(name='resolver_contexto', purpose='Ler contexto de conversa e entidades ativas.', stage='plan'),
            KernelExecutionStep(name='recuperar', purpose='Executar recuperacao textual e vetorial do LlamaIndex.', stage='execute'),
            KernelExecutionStep(name='sintetizar', purpose='Compor resposta com trechos citaveis.', stage='execute'),
        ]
    return [
        KernelExecutionStep(name='avaliar_ambiguidade', purpose='Checar o recorte minimo que ainda falta.', stage='plan'),
        KernelExecutionStep(name='clarificar', purpose='Pedir uma informacao complementar simples.', stage='execute'),
    ]


def build_kernel_plan(*, request: MessageResponseRequest, settings: Any, stack_name: str, mode: str) -> KernelPlan:
    preview = _build_preview(request=request, settings=settings)
    entities = resolve_entity_hints(request.message)
    notes: list[str] = []
    if entities.protocol_code:
        notes.append(f'protocol_hint:{entities.protocol_code}')
    if entities.quantity_hint is not None and entities.is_hypothetical:
        notes.append(f'hypothetical_quantity:{entities.quantity_hint}')
    if entities.domain_hint:
        notes.append(f'entity_domain_hint:{entities.domain_hint}')

    slice_name = 'public'
    if preview.classification.access_tier is AccessTier.sensitive:
        slice_name = 'restricted'
    elif preview.classification.access_tier is AccessTier.authenticated:
        slice_name = 'protected'

    return KernelPlan(
        stack_name=stack_name,
        mode=mode,
        slice_name=slice_name,
        preview=preview,
        entities=entities,
        execution_steps=_execution_steps_for_route(preview),
        plan_notes=notes,
    )
