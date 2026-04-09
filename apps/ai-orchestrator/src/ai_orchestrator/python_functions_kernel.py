from __future__ import annotations

import re
import unicodedata
from typing import Any

from pydantic import BaseModel, Field

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
    'materia',
    'matéria',
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
    'quitada',
    'quitado',
}
CALENDAR_TERMS = {
    'calendario',
    'calendário',
    'evento',
    'eventos',
    'feriado',
    'reuniao',
    'reunião',
    'formatura',
    'data',
    'datas',
}
PUBLIC_PRICING_TERMS = {
    'preco',
    'preço',
    'precos',
    'preços',
    'valor',
    'valores',
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
EXPLANATORY_TERMS = {
    'como funciona',
    'como e',
    'como é',
    'quais sao',
    'quais são',
    'me explique',
    'explique',
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
}
GREETING_TERMS = {'oi', 'ola', 'olá', 'oie', 'bom dia', 'boa tarde', 'boa noite'}
RESTRICTED_DOC_TERMS = {
    'documento interno',
    'documentos internos',
    'playbook',
    'material interno',
    'material interno do professor',
    'manual interno',
    'manual do professor',
    'orientacao interna',
    'orientação interna',
    'procedimento interno',
    'fluxo interno',
    'protocolo interno',
    'escopo parcial',
}


def _normalize(text: str) -> str:
    lowered = unicodedata.normalize('NFKD', str(text or '')).encode('ascii', 'ignore').decode('ascii').lower()
    return re.sub(r'\s+', ' ', lowered).strip()


def _contains_any(text: str, terms: set[str]) -> bool:
    normalized = _normalize(text)
    return any(term in normalized for term in terms)


def _classify_domain(message: str, *, authenticated: bool) -> QueryDomain:
    if authenticated and _contains_any(message, FINANCE_TERMS):
        return QueryDomain.finance
    if _contains_any(message, ACADEMIC_TERMS):
        return QueryDomain.academic
    if _contains_any(message, CALENDAR_TERMS):
        return QueryDomain.calendar
    if _contains_any(message, PROCESS_TERMS | PUBLIC_PRICING_TERMS):
        return QueryDomain.institution
    return QueryDomain.unknown if not authenticated else QueryDomain.institution


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


def _build_preview(*, request: MessageResponseRequest, settings: Any) -> OrchestrationPreview:
    authenticated = bool(request.user.authenticated)
    domain = _classify_domain(request.message, authenticated=authenticated)
    normalized = _normalize(request.message)

    if any(normalized == greeting or normalized.startswith(f'{greeting} ') for greeting in GREETING_TERMS):
        mode = OrchestrationMode.clarify
        reason = 'python_functions_local_greeting'
    elif authenticated and _contains_any(request.message, RESTRICTED_DOC_TERMS):
        if _can_read_restricted_documents(request):
            mode = OrchestrationMode.hybrid_retrieval
            reason = 'python_functions_local_restricted_documents'
        else:
            mode = OrchestrationMode.deny
            reason = 'python_functions_local_restricted_documents_denied'
    elif authenticated:
        mode = OrchestrationMode.structured_tool
        reason = f'python_functions_local_protected:{domain.value}'
    elif domain in {QueryDomain.institution, QueryDomain.calendar} and _contains_any(request.message, EXPLANATORY_TERMS):
        mode = OrchestrationMode.hybrid_retrieval
        reason = f'python_functions_local_public_explanatory:{domain.value}'
    elif domain in {QueryDomain.institution, QueryDomain.calendar, QueryDomain.unknown}:
        mode = OrchestrationMode.structured_tool
        reason = f'python_functions_local_public_direct:{domain.value}'
    else:
        mode = OrchestrationMode.clarify
        reason = 'python_functions_local_clarify'

    access_tier = AccessTier.public
    if authenticated:
        access_tier = AccessTier.sensitive if domain is QueryDomain.finance else AccessTier.authenticated

    if mode is OrchestrationMode.structured_tool:
        selected_tools = (
            _protected_selected_tools_for_domain(domain)
            if authenticated
            else _public_selected_tools_for_message(request.message)
        )
    elif mode is OrchestrationMode.hybrid_retrieval:
        selected_tools = ['search_documents']
    elif mode is OrchestrationMode.deny:
        selected_tools = []
    else:
        selected_tools = []

    output_contract = 'resposta segura, auditavel e orientada por ferramentas'
    if mode is OrchestrationMode.hybrid_retrieval:
        output_contract = 'resposta fundamentada em evidencias recuperadas'
    elif mode is OrchestrationMode.deny:
        output_contract = 'negativa segura para conteudo interno sem permissao'
    elif mode is OrchestrationMode.clarify:
        output_contract = 'pedido de esclarecimento curto e objetivo'

    return OrchestrationPreview(
        mode=mode,
        classification=IntentClassification(
            domain=domain,
            access_tier=access_tier,
            confidence=0.9 if mode is not OrchestrationMode.clarify else 0.65,
            reason=reason,
        ),
        retrieval_backend=RetrievalBackend.qdrant_hybrid if mode is OrchestrationMode.hybrid_retrieval else RetrievalBackend.none,
        selected_tools=selected_tools,
        citations_required=mode is OrchestrationMode.hybrid_retrieval,
        needs_authentication=authenticated and mode is not OrchestrationMode.clarify,
        graph_path=['python_functions:planner', f'domain:{domain.value}', f'mode:{mode.value}'],
        risk_flags=['sensitive_data_path'] if access_tier is AccessTier.sensitive else [],
        reason=reason,
        output_contract=output_contract,
    )


def _execution_steps_for_route(preview: OrchestrationPreview) -> list[KernelExecutionStep]:
    if preview.mode is OrchestrationMode.structured_tool:
        return [
            KernelExecutionStep(name='resolver_contexto', purpose='Carregar contexto e entidades ativas.', stage='plan'),
            KernelExecutionStep(name='executar_servicos', purpose='Consultar servicos estruturados do dominio.', stage='execute'),
            KernelExecutionStep(name='compor_resposta', purpose='Montar resposta objetiva a partir dos dados.', stage='execute'),
        ]
    if preview.mode is OrchestrationMode.hybrid_retrieval:
        return [
            KernelExecutionStep(name='resolver_contexto', purpose='Carregar contexto e entidades ativas.', stage='plan'),
            KernelExecutionStep(name='buscar_evidencias', purpose='Executar busca textual e semantica.', stage='execute'),
            KernelExecutionStep(name='compor_resposta', purpose='Responder com base nas evidencias recuperadas.', stage='execute'),
        ]
    return [
        KernelExecutionStep(name='avaliar_contexto', purpose='Identificar a informacao minima que ainda falta.', stage='plan'),
        KernelExecutionStep(name='pedir_esclarecimento', purpose='Solicitar um recorte curto ao usuario.', stage='execute'),
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
