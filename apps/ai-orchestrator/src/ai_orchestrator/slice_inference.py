from __future__ import annotations

import re
import unicodedata
from typing import Any

from .retrieval import looks_like_restricted_document_query


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
    asks_location = any(_contains_phrase(normalized, term) for term in ('endereco completo', 'onde fica', 'telefone principal'))
    asks_secretaria = any(_contains_phrase(normalized, term) for term in ('secretaria hoje', 'melhor canal', 'canal da secretaria'))
    return asks_location and (asks_secretaria or _contains_phrase(normalized, 'telefone principal'))


def _is_public_service_routing_request(request: Any) -> bool:
    normalized = _normalize_shadow_message(str(getattr(request, 'message', '') or ''))
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
    normalized = _normalize_shadow_message(str(getattr(request, 'message', '') or ''))
    if 'projeto de vida' in normalized:
        return True
    if any(_contains_phrase(normalized, term) for term in ('politica de avaliacao', 'recuperacao e promocao', 'recuperacao promocao')):
        return True
    return any(_contains_phrase(normalized, term) for term in ('falta', 'faltas', 'frequencia', '75')) and any(
        _contains_phrase(normalized, term) for term in ('politica', 'regra', 'minima', 'o que acontece')
    )


def _is_public_document_submission_request(request: Any) -> bool:
    normalized = _normalize_shadow_message(str(getattr(request, 'message', '') or ''))
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
    normalized = _normalize_shadow_message(str(getattr(request, 'message', '') or ''))
    return any(_contains_phrase(normalized, term) for term in ('credenciais', 'login', 'senha')) and any(
        _contains_phrase(normalized, term) for term in ('secretaria', 'portal', 'documentos', 'documentacao', 'envio de documentos')
    )


def _is_public_timeline_request(request: Any) -> bool:
    normalized = _normalize_shadow_message(str(getattr(request, 'message', '') or ''))
    asks_enrollment = any(_contains_phrase(normalized, term) for term in ('abre a matricula', 'abre a matrícula', 'matricula de 2026', 'abertura da matricula'))
    asks_classes = any(
        _contains_phrase(normalized, term)
        for term in (
            'quando comecam as aulas',
            'quando começam as aulas',
            'inicio das aulas',
            'início das aulas',
            'comeco das aulas',
            'começo das aulas',
        )
    )
    asks_family_meeting = any(
        _contains_phrase(normalized, term)
        for term in (
            'reuniao com responsaveis',
            'reunião com responsáveis',
            'responsaveis em 2026',
            'primeira reuniao com responsaveis',
            'primeira reunião com responsáveis',
        )
    )
    return asks_enrollment or asks_classes or asks_family_meeting


def _is_public_auth_guidance_request(request: Any) -> bool:
    normalized = _normalize_shadow_message(str(getattr(request, 'message', '') or ''))
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
    normalized = _normalize_shadow_message(str(getattr(request, 'message', '') or ''))
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
        'familia nova',
        'família nova',
        'primeiro bimestre',
        'do ponto de vista de uma familia nova',
        'impactam o primeiro mes',
        'como se encaixam',
        'visao transversal',
        'visão transversal',
        'ao longo do ano',
    )
    public_doc_markers = (
        'manual de regulamentos',
        'politica de avaliacao',
        'avaliacoes',
        'avaliações',
        'calendario letivo',
        'calendario',
        'calendário',
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
        'vida escolar',
        'responsaveis',
        'familia',
        'biblioteca',
        'laboratorios',
    )
    return any(_contains_phrase(normalized, term) for term in intent_markers) and any(
        _contains_phrase(normalized, term) for term in public_doc_markers
    )


def _is_restricted_document_request(request: Any) -> bool:
    return bool(str(getattr(request, 'message', '') or '')) and looks_like_restricted_document_query(str(getattr(request, 'message', '') or ''))


def _is_protected_access_scope_request(request: Any) -> bool:
    user = getattr(request, 'user', None)
    if not bool(getattr(user, 'authenticated', False)):
        return False
    normalized = _normalize_shadow_message(str(getattr(request, 'message', '') or ''))
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
    if any(_contains_phrase(normalized, term) for term in ('meus filhos', 'por aqui', 'meu acesso')):
        has_scope_anchor = any(
            _contains_phrase(normalized, term)
            for term in ('escopo', 'acesso', 'dados', 'consigo acessar', 'posso acessar')
        )
        has_scope_dimension = any(
            _contains_phrase(normalized, term)
            for term in ('academico', 'acadêmico', 'financeiro', 'os dois')
        )
        if has_scope_anchor and has_scope_dimension:
            return True
    return False


def _is_protected_admin_finance_combo_request(request: Any) -> bool:
    normalized = _normalize_shadow_message(str(getattr(request, 'message', '') or ''))
    asks_admin = any(
        _contains_phrase(normalized, term)
        for term in ('documentacao', 'documentos', 'documental', 'documentais', 'cadastro', 'regular', 'administrativa', 'administrativo', 'parte administrativa')
    )
    asks_finance = any(
        _contains_phrase(normalized, term)
        for term in ('financeiro', 'fatura', 'boleto', 'mensalidade', 'pagamento', 'vencimento', 'bloqueando atendimento', 'bloqueio')
    )
    return asks_admin and asks_finance


def _protected_shadow_slice(request: Any) -> bool:
    message = str(getattr(request, 'message', '') or '')
    if _is_restricted_document_request(request):
        return True
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
        'documental',
        'documentais',
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
    return authenticated and any(_contains_phrase(message, term) for term in followup_terms)


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
    if _is_restricted_document_request(request) or _support_shadow_slice(request):
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
