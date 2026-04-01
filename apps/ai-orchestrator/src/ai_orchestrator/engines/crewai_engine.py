from __future__ import annotations

import logging
import re
from typing import Any
import unicodedata

import httpx

from ..crewai.flow import run_public_shadow_flow
from ..models import (
    AccessTier,
    IntentClassification,
    MessageResponse,
    MessageResponseSuggestedReply,
    OrchestrationMode,
    OrchestrationPreview,
    QueryDomain,
    RetrievalBackend,
)
from .base import ResponseEngine, ShadowRunResult

logger = logging.getLogger(__name__)


def _normalize_shadow_message(value: str) -> str:
    text = unicodedata.normalize('NFKD', str(value or ''))
    text = ''.join(ch for ch in text if not unicodedata.combining(ch))
    text = re.sub(r'[^a-z0-9\s]+', ' ', text.lower())
    return ' '.join(text.split())


def _contains_phrase(message: str, phrase: str) -> bool:
    normalized_message = _normalize_shadow_message(message)
    normalized_phrase = _normalize_shadow_message(phrase)
    if not normalized_message or not normalized_phrase:
        return False
    pattern = r'(?<!\w)' + re.escape(normalized_phrase).replace(r'\ ', r'\s+') + r'(?!\w)'
    return re.search(pattern, normalized_message) is not None


def _is_public_institutional_pricing_query(request: Any) -> bool:
    message = str(getattr(request, 'message', '') or '')
    normalized = _normalize_shadow_message(message)
    if not normalized:
        return False
    pricing_terms = ('mensalidade', 'matricula', 'desconto', 'bolsa', 'pagar', 'valor')
    protected_markers = ('em aberto', 'vencimento', 'boleto', 'fatura', 'lucas', 'ana', 'meus filhos', 'minha filha', 'meu filho')
    if any(_contains_phrase(normalized, marker) for marker in protected_markers):
        return False
    hypothetical_markers = (
        'se eu tiver',
        'se eu tivesse',
        'hipoteticamente',
        'num cenario hipotetico',
    )
    if 'filhos' in normalized and any(_contains_phrase(normalized, marker) for marker in hypothetical_markers):
        return any(_contains_phrase(normalized, term) for term in pricing_terms)
    if 'filhos' in normalized and any(_contains_phrase(normalized, term) for term in ('quanto vou pagar', 'quanto eu pagaria')):
        return any(_contains_phrase(normalized, term) for term in pricing_terms)
    if any(_contains_phrase(normalized, term) for term in pricing_terms):
        institutional_markers = (
            'da escola',
            'na escola',
            'por ano',
            'cada ano',
            'por segmento',
            'cada segmento',
            'ensino medio',
            'ensino fundamental',
            'media do valor',
            'media da mensalidade',
        )
        return any(_contains_phrase(normalized, marker) for marker in institutional_markers)
    return False


def _is_teacher_internal_request(request: Any) -> bool:
    user = getattr(request, 'user', None)
    role = str(getattr(user, 'role', '') or '').strip().lower()
    authenticated = bool(getattr(user, 'authenticated', False))
    if role != 'teacher' and not authenticated:
        return False
    message = str(getattr(request, 'message', '') or '')
    normalized = _normalize_shadow_message(message)
    teacher_internal_terms = (
        'meus alunos',
        'minhas turmas',
        'quais turmas eu atendo',
        'minha grade docente',
        'grade docente',
        'grade docente completa',
        'quais turmas eu tenho',
        'quais disciplinas eu tenho',
        'quais disciplinas eu atendo',
        'quais turmas e disciplinas eu tenho',
        'quais turmas e disciplinas eu atendo',
        'quais classes eu tenho',
        'quais classes eu atendo',
        'rotina docente',
        'minha rotina docente',
        'alocacao docente',
        'alocação docente',
        'filosofia',
        'sociologia',
        'ensino medio',
        'ensino médio',
        'ja sou professor',
        'já sou professor',
        'sou professor do colegio',
        'sou professor do colégio',
    )
    if any(_contains_phrase(normalized, term) for term in teacher_internal_terms):
        return True
    return role == 'teacher' and any(
        _contains_phrase(normalized, term)
        for term in ('turma', 'turmas', 'disciplina', 'disciplinas', 'classe', 'classes', 'grade', 'horario', 'horário')
    )


def _public_meta_shadow_slice(request: Any) -> bool:
    message = str(getattr(request, 'message', '') or '').strip()
    if not message:
        return False
    direct_meta_terms = (
        'ola',
        'olá',
        'oi',
        'bom dia',
        'boa tarde',
        'boa noite',
        'qual seu nome',
        'quem e voce',
        'quem é você',
        'voce e uma llm',
        'você é uma llm',
        'qual llm',
        'qual modelo',
        'com quem eu falo',
        'com quem estou falando',
    )
    return any(_contains_phrase(message, term) for term in direct_meta_terms)


def _is_public_contact_bundle_request(request: Any) -> bool:
    message = str(getattr(request, 'message', '') or '')
    normalized = _normalize_shadow_message(message)
    if not normalized:
        return False
    asks_location = any(_contains_phrase(normalized, term) for term in ('endereco completo', 'onde fica', 'telefone principal'))
    asks_secretaria = any(_contains_phrase(normalized, term) for term in ('secretaria hoje', 'melhor canal', 'canal da secretaria'))
    return asks_location and (asks_secretaria or _contains_phrase(normalized, 'telefone principal'))


def _is_public_service_routing_request(request: Any) -> bool:
    message = str(getattr(request, 'message', '') or '')
    normalized = _normalize_shadow_message(message)
    if not normalized:
        return False
    return any(
        _contains_phrase(normalized, term)
        for term in (
            'com quem eu falo sobre',
            'quem responde por',
            'pra quem eu falo sobre',
            'para quem eu falo sobre',
        )
    )


def _is_public_policy_request(request: Any) -> bool:
    message = str(getattr(request, 'message', '') or '')
    normalized = _normalize_shadow_message(message)
    if not normalized:
        return False
    if 'projeto de vida' in normalized:
        return True
    if any(_contains_phrase(normalized, term) for term in ('politica de avaliacao', 'recuperacao e promocao', 'recuperacao promocao')):
        return True
    if any(_contains_phrase(normalized, term) for term in ('falta', 'faltas', 'frequencia', '75')) and any(
        _contains_phrase(normalized, term) for term in ('politica', 'regra', 'minima', 'o que acontece')
    ):
        return True
    return False


def _is_public_document_submission_request(request: Any) -> bool:
    message = str(getattr(request, 'message', '') or '')
    normalized = _normalize_shadow_message(message)
    if not normalized:
        return False
    if any(
        _contains_phrase(normalized, term)
        for term in (
            'envio de documentos',
            'enviar documentos',
            'mandar documentos',
            'portal institucional',
            'email da secretaria',
            'secretaria presencial',
            'prazos e canais da secretaria',
            'prazo da secretaria para documentos',
            'atualizacoes cadastrais',
            'declaracoes',
        )
    ):
        return True
    return 'secretaria' in normalized and 'documentos' in normalized and any(
        _contains_phrase(normalized, term) for term in ('prazo', 'prazos', 'canal', 'canais')
    )


def _is_public_service_credentials_bundle_request(request: Any) -> bool:
    message = str(getattr(request, 'message', '') or '')
    normalized = _normalize_shadow_message(message)
    if not normalized:
        return False
    return any(_contains_phrase(normalized, term) for term in ('credenciais', 'login', 'senha')) and any(
        _contains_phrase(normalized, term) for term in ('secretaria', 'portal', 'documentos', 'documentacao', 'envio de documentos')
    )


def _is_public_timeline_request(request: Any) -> bool:
    message = str(getattr(request, 'message', '') or '')
    normalized = _normalize_shadow_message(message)
    if not normalized:
        return False
    asks_enrollment = any(_contains_phrase(normalized, term) for term in ('abre a matricula', 'abre a matrícula', 'matricula de 2026'))
    asks_classes = any(_contains_phrase(normalized, term) for term in ('quando comecam as aulas', 'quando começam as aulas', 'inicio das aulas', 'início das aulas'))
    return asks_enrollment or asks_classes


def _is_public_auth_guidance_request(request: Any) -> bool:
    message = str(getattr(request, 'message', '') or '')
    normalized = _normalize_shadow_message(message)
    if not normalized:
        return False
    return any(
        _contains_phrase(normalized, term)
        for term in (
            'como vinculo minha conta',
            'como eu vinculo minha conta',
            'como eu vinculo meu telegram',
            'como vinculo meu telegram',
            'telegram a minha conta da escola',
            'vincular telegram',
            '/start link_',
            'codigo de vinculacao',
        )
    )


def _is_public_doc_bundle_request(request: Any) -> bool:
    message = str(getattr(request, 'message', '') or '')
    normalized = _normalize_shadow_message(message)
    if not normalized:
        return False
    intent_markers = (
        'compare',
        'comparar',
        'comparativo',
        'compare o',
        'compare a',
        'sintetize',
        'resuma',
        'explique como',
        'cruze',
        'quais documentos',
        'do ponto de vista de uma familia nova',
        'impactam o primeiro mes',
    )
    public_doc_markers = (
        'manual de regulamentos',
        'politica de avaliacao',
        'calendario letivo',
        'agenda de avaliacoes',
        'manual de matricula',
        'secretaria',
        'portal',
        'credenciais',
        'envio de documentos',
        'protocolo de saude',
        'medicacao',
        'emergencias',
        'segunda chamada',
        'bolsas',
        'descontos',
        'rematricula',
        'transferencia',
        'cancelamento',
        'permanencia',
        'acolhimento familiar',
        'estudo orientado',
        'vida academica',
    )
    return any(_contains_phrase(normalized, term) for term in intent_markers) and any(
        _contains_phrase(normalized, term) for term in public_doc_markers
    )


def _is_protected_access_scope_request(request: Any) -> bool:
    user = getattr(request, 'user', None)
    authenticated = bool(getattr(user, 'authenticated', False))
    if not authenticated:
        return False
    message = str(getattr(request, 'message', '') or '')
    normalized = _normalize_shadow_message(message)
    if not normalized:
        return False
    explicit_phrases = (
        'qual e exatamente o meu escopo',
        'qual e meu escopo',
        'quais dados eu consigo acessar',
        'quais dados dos meus alunos eu consigo acessar',
        'quais dados dos meus dois alunos eu consigo acessar',
        'quais dados dos meus filhos eu consigo acessar',
    )
    if any(_contains_phrase(normalized, phrase) for phrase in explicit_phrases):
        return True
    if 'meus alunos' in normalized or 'meus dois alunos' in normalized:
        return any(
            _contains_phrase(normalized, term)
            for term in ('escopo', 'acesso', 'dados', 'consigo acessar', 'posso acessar')
        )
    return False


def _is_protected_admin_finance_combo_request(request: Any) -> bool:
    message = str(getattr(request, 'message', '') or '')
    normalized = _normalize_shadow_message(message)
    if not normalized:
        return False
    asks_admin = any(_contains_phrase(normalized, term) for term in ('documentacao', 'documentos', 'cadastro', 'regular'))
    asks_finance = any(
        _contains_phrase(normalized, term)
        for term in ('financeiro', 'fatura', 'boleto', 'mensalidade', 'pagamento', 'vencimento', 'bloqueando atendimento', 'bloqueio')
    )
    return asks_admin and asks_finance


def _protected_shadow_slice(request: Any) -> bool:
    message = str(getattr(request, 'message', '') or '')
    if _is_teacher_internal_request(request):
        return True
    if _is_protected_access_scope_request(request):
        return True
    if _is_protected_admin_finance_combo_request(request):
        return True
    if _public_meta_shadow_slice(request):
        return False
    if (
        _is_public_contact_bundle_request(request)
        or _is_public_service_routing_request(request)
        or _is_public_policy_request(request)
        or _is_public_document_submission_request(request)
        or _is_public_service_credentials_bundle_request(request)
        or _is_public_doc_bundle_request(request)
        or _is_public_timeline_request(request)
        or _is_public_auth_guidance_request(request)
    ):
        return False
    if _is_public_institutional_pricing_query(request):
        return False
    protected_terms = (
        'nota',
        'notas',
        'falta',
        'faltas',
        'frequencia',
        'prova',
        'provas',
        'avaliacao',
        'avaliacoes',
        'financeiro',
        'boleto',
        'pagamento',
        'mensalidade',
        'documentacao',
        'documentos',
        'meus filhos',
        'meu filho',
        'minha filha',
        'estou logado',
        'meu acesso',
        'meu cadastro',
        'altero meu cadastro',
        'alterar meu cadastro',
        'como altero',
        'como alterar',
        'cadastro',
        'dados cadastrais',
        'em aberto',
        'valor em aberto',
        'vencimento',
        'matricula',
        'lucas',
        'ana',
    )
    if any(_contains_phrase(message, term) for term in protected_terms):
        return True
    user = getattr(request, 'user', None)
    authenticated = user is not None and bool(getattr(user, 'authenticated', False))
    followup_terms = (
        'e a',
        'e o',
        'e as',
        'e os',
        'e do',
        'e da',
        'e dele',
        'e dela',
        'o que falta',
        'qual valor',
        'qual vencimento',
        'como altero meu cadastro',
        'como alterar meu cadastro',
    )
    if authenticated and any(_contains_phrase(message, term) for term in followup_terms):
        return True
    return False


def _support_shadow_slice(request: Any) -> bool:
    if _is_protected_access_scope_request(request) or _is_protected_admin_finance_combo_request(request):
        return False
    if (
        _is_public_contact_bundle_request(request)
        or _is_public_service_routing_request(request)
        or _is_public_policy_request(request)
        or _is_public_document_submission_request(request)
        or _is_public_service_credentials_bundle_request(request)
        or _is_public_doc_bundle_request(request)
        or _is_public_timeline_request(request)
        or _is_public_auth_guidance_request(request)
    ):
        return False
    message = str(getattr(request, 'message', '') or '').lower()
    support_terms = (
        'atendente humano',
        'atendimento humano',
        'quero falar com um humano',
        'preciso falar com um humano',
        'como falo com um atendente',
        'quero falar com o setor',
        'quero falar com a secretaria',
        'quero falar com o financeiro',
        'quero falar com a direcao',
        'quero falar com a direção',
        'quero falar com a orientacao',
        'quero falar com a orientação',
        'suporte humano',
        'atendente',
        'humano',
        'ticket operacional',
        'atd-',
    )
    return any(term in message for term in support_terms)


def _workflow_shadow_slice(request: Any) -> bool:
    message = str(getattr(request, 'message', '') or '').lower()
    if _support_shadow_slice(request):
        return False
    followup_terms = (
        'pode ser na',
        'pode ser no',
        'pode ficar para',
        'quinta a tarde',
        'quinta à tarde',
        'sexta de manha',
        'sexta de manhã',
    )
    workflow_terms = (
        'agendar visita',
        'visita',
        'tour',
        'protocolar',
        'protocolo',
        'solicitacao',
        'solicitação',
        'remarcar',
        'reagendar',
        'cancelar a visita',
        'resume meu pedido',
        'status da visita',
        'status do protocolo',
    )
    return any(term in message for term in workflow_terms) or any(term in message for term in followup_terms)


def infer_request_slice(request: Any) -> str:
    if _support_shadow_slice(request):
        return 'support'
    if _workflow_shadow_slice(request):
        return 'workflow'
    if _protected_shadow_slice(request):
        return 'protected'
    return 'public'


def _slice_from_engine_mode(engine_mode: str | None) -> str | None:
    mode = str(engine_mode or '').strip().lower()
    if not mode.startswith('experiment:'):
        return None
    parts = mode.split(':')
    if len(parts) < 3:
        return None
    slice_name = parts[1].strip()
    return slice_name or None


def _resolve_slice_name(*, request: Any, engine_mode: str | None = None) -> str:
    forced_slice = _slice_from_engine_mode(engine_mode)
    if forced_slice:
        return forced_slice
    return infer_request_slice(request)


def _crewai_timeline_labels(metadata: dict[str, Any] | None) -> list[str]:
    if not isinstance(metadata, dict):
        return []
    labels: list[str] = []
    validation_stack = metadata.get('validation_stack')
    if isinstance(validation_stack, list):
        labels.extend(str(item).strip() for item in validation_stack if str(item).strip())
    task_names = metadata.get('task_names')
    if isinstance(task_names, list):
        labels.extend(str(item).strip() for item in task_names if str(item).strip())
    if not labels:
        slice_name = str(metadata.get('slice_name', '') or '').strip()
        if slice_name:
            labels.append(f'{slice_name}_flow')
    return labels


def _public_selected_tools(metadata: dict[str, Any]) -> list[str]:
    plan = metadata.get('plan') if isinstance(metadata.get('plan'), dict) else {}
    relevant_sources = plan.get('relevant_sources') if isinstance(plan.get('relevant_sources'), list) else []
    selected: list[str] = []
    if any(str(source).startswith('timeline.') for source in relevant_sources):
        selected.append('get_public_timeline')
    if any(str(source).startswith('calendar.') for source in relevant_sources):
        selected.append('get_public_calendar_events')
    if any(str(source).startswith(('directory.', 'leadership.')) for source in relevant_sources):
        selected.append('get_org_directory')
    if any(str(source).startswith('service.') for source in relevant_sources):
        selected.append('get_service_directory')
    if not selected or any(
        str(source).startswith(
            (
                'profile.',
                'contact.',
                'feature.',
                'tuition.',
                'visit.',
                'shift.',
                'interval.',
                'policy.',
                'admissions.',
                'highlight.',
            )
        )
        for source in relevant_sources
    ):
        selected.append('get_public_school_profile')
    deduped: list[str] = []
    for tool_name in selected:
        if tool_name not in deduped:
            deduped.append(tool_name)
    return deduped or ['get_public_school_profile']


def _protected_selected_tools(metadata: dict[str, Any]) -> list[str]:
    plan = metadata.get('plan') if isinstance(metadata.get('plan'), dict) else {}
    domain = str(plan.get('domain', '') or '').strip().lower()
    attribute = str(plan.get('attribute', '') or '').strip().lower()
    reason = str(metadata.get('reason', '') or '').strip().lower()
    resolved_student_name = str(metadata.get('resolved_student_name', '') or '').strip()

    if domain == 'finance' or any(term in attribute or term in reason for term in ('finance', 'pagamento', 'boleto', 'mensalidade')):
        return ['get_financial_summary']
    if any(term in attribute or term in reason for term in ('grade', 'grades', 'nota', 'notas')):
        return ['get_student_grades']
    if any(term in attribute or term in reason for term in ('attendance', 'frequencia', 'faltas', 'falta')):
        return ['get_student_attendance']
    if any(term in attribute or term in reason for term in ('assessment', 'assessments', 'provas', 'prova')):
        return ['get_student_upcoming_assessments']
    if resolved_student_name and any(term in attribute or term in reason for term in ('document', 'documents', 'documentacao', 'documentos', 'admin', 'enrollment', 'matricula')):
        return ['get_student_administrative_status']
    if any(term in attribute or term in reason for term in ('identity', 'access', 'scope', 'linked_students', 'filhos', 'logado')):
        return ['get_actor_identity_context']
    if any(term in attribute or term in reason for term in ('cadastro', 'administrative', 'documentacao', 'documentos')):
        return ['get_actor_identity_context', 'get_administrative_status']
    return ['get_actor_identity_context']


def _support_selected_tools(metadata: dict[str, Any]) -> list[str]:
    reason = str(metadata.get('reason', '') or '').strip().lower()
    if any(term in reason for term in ('status', 'protocol', 'summary')):
        return ['get_workflow_status']
    return ['create_support_ticket', 'handoff_to_human']


def _workflow_selected_tools(metadata: dict[str, Any]) -> list[str]:
    reason = str(metadata.get('reason', '') or '').strip().lower()
    if 'visit_create' in reason:
        return ['schedule_school_visit']
    if any(term in reason for term in ('visit_reschedule', 'visit_cancel')):
        return ['update_visit_booking']
    if any(term in reason for term in ('protocol_lookup', 'summary_lookup', 'status_lookup')):
        return ['get_workflow_status']
    if 'request_create' in reason:
        return ['create_institutional_request']
    if 'request_update' in reason:
        return ['update_institutional_request']
    return ['get_workflow_status']


def _build_crewai_preview(*, slice_name: str, metadata: dict[str, Any], payload_reason: str) -> OrchestrationPreview:
    selected_tools: list[str]
    domain = QueryDomain.institution
    access_tier = AccessTier.public
    needs_authentication = False
    mode = OrchestrationMode.structured_tool
    risk_flags: list[str] = []

    if slice_name == 'public':
        selected_tools = _public_selected_tools(metadata)
        if {'get_public_timeline', 'get_public_calendar_events'} & set(selected_tools):
            domain = QueryDomain.calendar
    elif slice_name == 'protected':
        selected_tools = _protected_selected_tools(metadata)
        needs_authentication = 'auth_required' in payload_reason
        if 'get_financial_summary' in selected_tools:
            domain = QueryDomain.finance
            access_tier = AccessTier.sensitive
        elif {'get_student_grades', 'get_student_attendance', 'get_student_upcoming_assessments'} & set(selected_tools):
            domain = QueryDomain.academic
            access_tier = AccessTier.authenticated
        else:
            domain = QueryDomain.institution
            access_tier = AccessTier.authenticated
        if needs_authentication:
            mode = OrchestrationMode.deny
    elif slice_name == 'support':
        selected_tools = _support_selected_tools(metadata)
        domain = QueryDomain.support
    else:
        selected_tools = _workflow_selected_tools(metadata)
        domain = QueryDomain.support

    if 'pending_review' in payload_reason or bool(metadata.get('pending_review')):
        risk_flags = ['pending_human_review']
    elif 'review_rejected' in payload_reason or bool(metadata.get('review_rejected')):
        risk_flags = ['human_review_rejected']
        mode = OrchestrationMode.deny

    return OrchestrationPreview(
        mode=mode,
        classification=IntentClassification(
            domain=domain,
            access_tier=access_tier,
            confidence=0.9,
            reason=payload_reason or f'crewai_{slice_name}_primary',
        ),
        retrieval_backend=RetrievalBackend.none,
        selected_tools=selected_tools,
        citations_required=False,
        needs_authentication=needs_authentication,
        graph_path=_crewai_timeline_labels(metadata),
        risk_flags=risk_flags,
        reason=payload_reason or f'crewai_{slice_name}_primary',
        output_contract='Feature-flagged CrewAI primary response with native Flow/task trace metadata.',
    )


def _dedupe_reply_texts(values: list[str]) -> list[MessageResponseSuggestedReply]:
    seen: set[str] = set()
    replies: list[MessageResponseSuggestedReply] = []
    for value in values:
        text = str(value or '').strip()
        if not text:
            continue
        normalized = text.lower()
        if normalized in seen:
            continue
        seen.add(normalized)
        replies.append(MessageResponseSuggestedReply(text=text[:80]))
    return replies[:4]


def _build_crewai_suggested_replies(*, slice_name: str, metadata: dict[str, Any], preview: OrchestrationPreview) -> list[MessageResponseSuggestedReply]:
    reason = str(metadata.get('reason', '') or '').strip().lower()
    selected_tools = list(preview.selected_tools)
    if slice_name == 'support':
        if 'get_workflow_status' in selected_tools:
            return _dedupe_reply_texts(['Qual o status atual?', 'Qual o protocolo?', 'Quem vai me responder?', 'Resume meu atendimento'])
        return _dedupe_reply_texts(['Qual o protocolo?', 'Quero falar com o financeiro', 'Quero falar com a secretaria', 'Como acompanho isso?'])
    if slice_name == 'workflow':
        if 'schedule_school_visit' in selected_tools:
            return _dedupe_reply_texts(['Qual o protocolo da visita?', 'Qual o status da visita?', 'Quero remarcar a visita', 'Quero cancelar a visita'])
        if 'update_visit_booking' in selected_tools:
            return _dedupe_reply_texts(['Qual o status da visita?', 'Qual o protocolo da visita?', 'Quero cancelar a visita', 'Quero remarcar de novo'])
        if 'create_institutional_request' in selected_tools or 'update_institutional_request' in selected_tools:
            return _dedupe_reply_texts(['Qual o protocolo?', 'Qual o status do meu pedido?', 'Quem vai me responder?', 'Quero complementar meu pedido'])
        return _dedupe_reply_texts(['Qual o protocolo?', 'Qual o status?', 'Quem vai me responder?', 'E agora?'])
    if slice_name == 'protected':
        if 'get_financial_summary' in selected_tools:
            return _dedupe_reply_texts(['Qual o proximo pagamento?', 'Qual valor esta em aberto?', 'Quero ver os boletos', 'E do outro aluno?'])
        if 'get_student_grades' in selected_tools:
            return _dedupe_reply_texts(['E as faltas?', 'E as proximas provas?', 'Quero ver a matricula', 'E do outro aluno?'])
        if 'get_student_attendance' in selected_tools:
            return _dedupe_reply_texts(['E as notas?', 'Quais as proximas provas?', 'Quero ver as datas das faltas', 'E do outro aluno?'])
        if 'get_student_administrative_status' in selected_tools:
            return _dedupe_reply_texts(['E a matricula?', 'Quais documentos faltam?', 'Qual meu acesso?', 'Quais meus filhos?'])
        if any(tool in selected_tools for tool in ('get_actor_identity_context', 'get_administrative_status')):
            if 'logado' in reason or 'identity' in reason or 'access' in reason:
                return _dedupe_reply_texts(['Quais meus filhos?', 'Qual meu acesso?', 'Qual a documentacao do Lucas?', 'Como altero meu cadastro?'])
            return _dedupe_reply_texts(['Qual meu acesso?', 'Quais meus filhos?', 'Como altero meu cadastro?', 'Qual a documentacao do Lucas?'])
    if slice_name == 'public':
        if 'get_public_timeline' in selected_tools:
            return _dedupe_reply_texts(['Quando comecam as aulas?', 'Quando e a reuniao de pais?', 'Como agendo uma visita?', 'Qual o horario da biblioteca?'])
        if 'get_public_calendar_events' in selected_tools:
            return _dedupe_reply_texts(['Quando comecam as aulas?', 'Quando e a formatura?', 'Qual o horario da biblioteca?', 'Como agendo uma visita?'])
        return _dedupe_reply_texts(['Qual o horario da biblioteca?', 'Como agendo uma visita?', 'Qual o site da escola?', 'Quais atividades complementares existem?'])
    return _dedupe_reply_texts(['Como posso te ajudar?', 'Qual o proximo passo?', 'Quero mais detalhes', 'Pode continuar'])


def _strict_safe_response_text(*, slice_name: str) -> str:
    if slice_name == 'public':
        return 'Nao consegui concluir essa resposta agora pelo caminho principal configurado. Tente reformular em uma frase mais direta ou repetir em instantes.'
    if slice_name == 'protected':
        return 'Nao consegui consolidar essa consulta com seguranca agora. Se quiser, me diga exatamente se voce quer ver notas, frequencia, documentacao ou financeiro.'
    if slice_name == 'support':
        return 'Nao consegui concluir esse atendimento agora. Se quiser, eu posso tentar de novo ou voce pode me dizer se quer secretaria, financeiro, orientacao ou direcao.'
    return 'Nao consegui concluir essa acao agora. Se quiser, me diga se voce quer consultar status, protocolo, remarcar ou cancelar.'


class CrewAIEngine(ResponseEngine):
    name = 'crewai'
    ready = False

    def __init__(self, *, fallback_engine: ResponseEngine | None = None) -> None:
        self._fallback_engine = fallback_engine

    async def _call_remote_pilot(self, *, request: Any, settings: Any, slice_name: str) -> dict[str, Any] | None:
        pilot_url = str(getattr(settings, 'crewai_pilot_url', '') or '').strip()
        if not pilot_url:
            return None
        timeout_seconds = float(getattr(settings, 'crewai_pilot_timeout_seconds', 90.0) or 90.0)
        async with httpx.AsyncClient(timeout=httpx.Timeout(timeout_seconds, connect=5.0)) as client:
            response = await client.post(
                f'{pilot_url.rstrip("/")}/v1/shadow/{slice_name}',
                headers={
                    'X-Internal-Api-Token': settings.internal_api_token,
                    'Content-Type': 'application/json',
                },
                json={
                    'message': getattr(request, 'message', ''),
                    'conversation_id': getattr(request, 'conversation_id', None),
                    'telegram_chat_id': getattr(request, 'telegram_chat_id', None),
                    'channel': getattr(getattr(request, 'channel', None), 'value', 'telegram'),
                    'user': getattr(getattr(request, 'user', None), 'model_dump', lambda **_: None)(mode='json'),
                },
            )
        response.raise_for_status()
        payload = response.json()
        return payload if isinstance(payload, dict) else None

    async def respond(self, *, request: Any, settings: Any, engine_mode: str | None = None) -> Any:
        from ..runtime import (
            _conversation_context_payload,
            _effective_conversation_id,
            _fetch_actor_context,
            _fetch_conversation_context,
            _fetch_public_school_profile,
            _persist_conversation_turn,
            _persist_operational_trace,
        )

        slice_name = _resolve_slice_name(request=request, engine_mode=engine_mode)
        strict_isolation = bool(getattr(settings, 'strict_framework_isolation_enabled', False))
        try:
            payload = await self._call_remote_pilot(request=request, settings=settings, slice_name=slice_name)
        except Exception:
            logger.exception('crewai_primary_http_failed')
            payload = None
        answer_text = ''
        crewai_metadata: dict[str, Any] | None = None
        payload_reason = ''
        if isinstance(payload, dict):
            payload_reason = str(payload.get('reason', '') or '').strip()
            metadata = payload.get('metadata')
            if isinstance(metadata, dict):
                crewai_metadata = {'reason': payload_reason, **metadata}
                answer = metadata.get('answer')
                if isinstance(answer, dict) and isinstance(answer.get('answer_text'), str):
                    answer_text = str(answer['answer_text'])
        if not answer_text:
            if strict_isolation:
                payload_reason = payload_reason or 'crewai_primary_strict_safe_fallback'
                crewai_metadata = {
                    **(crewai_metadata or {}),
                    'reason': payload_reason,
                    'strict_framework_isolation': True,
                    'cross_stack_fallback_used': False,
                    'safe_fallback_used': True,
                }
                answer_text = _strict_safe_response_text(slice_name=slice_name)
            else:
                from ..runtime import generate_message_response

                logger.warning('crewai_engine_primary_fallback_to_langgraph')
                return await generate_message_response(
                    request=request,
                    settings=settings,
                    engine_name='crewai_stub',
                    engine_mode=str(engine_mode or self.name),
                )

        actor = await _fetch_actor_context(settings=settings, telegram_chat_id=getattr(request, 'telegram_chat_id', None))
        effective_conversation_id = _effective_conversation_id(request)
        conversation_context = await _fetch_conversation_context(
            settings=settings,
            conversation_external_id=effective_conversation_id,
            channel=request.channel.value,
        )
        context_payload = _conversation_context_payload(conversation_context)
        preview = _build_crewai_preview(
            slice_name=slice_name,
            metadata=crewai_metadata or {},
            payload_reason=payload_reason,
        )
        school_profile = (
            await _fetch_public_school_profile(settings=settings)
            if slice_name == 'public' or preview.classification.domain in {QueryDomain.institution, QueryDomain.calendar}
            else None
        )
        suggested_replies = _build_crewai_suggested_replies(
            slice_name=slice_name,
            metadata=crewai_metadata or {},
            preview=preview,
        )
        await _persist_conversation_turn(
            settings=settings,
            conversation_external_id=effective_conversation_id,
            channel=request.channel.value,
            actor=actor,
            user_message=request.message,
            assistant_message=answer_text,
        )
        await _persist_operational_trace(
            settings=settings,
            conversation_external_id=effective_conversation_id,
            channel=request.channel.value,
            engine_name=self.name,
            engine_mode=str(engine_mode or self.name),
            actor=actor,
            preview=preview,
            school_profile=school_profile,
            conversation_context=context_payload,
            public_plan=None,
            request_message=request.message,
            message_text=answer_text,
            citations_count=0,
            suggested_reply_count=len(suggested_replies),
            visual_asset_count=0,
            answer_verifier_valid=True,
            answer_verifier_reason='',
            answer_verifier_fallback_used=False,
            deterministic_fallback_available=False,
            answer_verifier_judge_used=False,
            engine_trace_metadata=crewai_metadata,
        )
        return MessageResponse(
            message_text=answer_text,
            mode=preview.mode,
            classification=preview.classification,
            retrieval_backend=preview.retrieval_backend,
            selected_tools=preview.selected_tools,
            citations=[],
            visual_assets=[],
            suggested_replies=suggested_replies,
            calendar_events=[],
            needs_authentication=preview.needs_authentication,
            graph_path=preview.graph_path,
            risk_flags=preview.risk_flags,
            reason=preview.reason,
        )

    async def shadow_compare(self, *, request: Any, settings: Any) -> ShadowRunResult:
        pilot_url = str(getattr(settings, 'crewai_pilot_url', '') or '').strip()
        if pilot_url:
            slice_name = _resolve_slice_name(request=request)
            try:
                payload = await self._call_remote_pilot(request=request, settings=settings, slice_name=slice_name)
                if isinstance(payload, dict):
                    metadata = payload.get('metadata') if isinstance(payload.get('metadata'), dict) else {}
                    metadata = {'shadow_slice': slice_name, **metadata}
                    return ShadowRunResult(
                        engine_name=str(payload.get('engine_name', self.name) or self.name),
                        executed=bool(payload.get('executed')),
                        reason=str(payload.get('reason', '') or ''),
                        metadata=metadata,
                    )
            except Exception as exc:
                logger.exception('crewai_shadow_http_failed')
                return ShadowRunResult(
                    engine_name=self.name,
                    executed=False,
                    reason='crewai_shadow_http_failed',
                    error=str(exc),
                )

        logger.info('crewai_shadow_public_slice_local_scaffold')
        return await run_public_shadow_flow(request=request, settings=settings)
