from __future__ import annotations

import base64
import io
import re
import unicodedata
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from time import monotonic
from typing import Any

import httpx
from eduassist_observability import record_counter, record_histogram, set_span_attributes, start_span
from PIL import Image, ImageDraw, ImageFont

from .graph_rag_runtime import graph_rag_workspace_ready, run_graph_rag_query
from .llm_provider import compose_with_provider
from .graph import build_orchestration_graph, to_preview
from .models import (
    CalendarEventCard,
    MessageResponse,
    MessageResponseCitation,
    MessageResponseRequest,
    MessageResponseVisualAsset,
    OrchestrationMode,
    OrchestrationRequest,
    QueryDomain,
    RetrievalBackend,
    UserContext,
    UserRole,
)
from .retrieval import get_retrieval_service


DEFAULT_PUBLIC_HELP = (
    'Posso ajudar com informacoes publicas da escola, como calendario, matricula, '
    'documentos exigidos e regras de atendimento digital.'
)

ATTENDANCE_TERMS = {'frequencia', 'falta', 'faltas', 'presenca', 'presencas'}
GRADE_TERMS = {'nota', 'notas', 'boletim', 'avaliacao', 'avaliacoes', 'prova', 'provas'}
TEACHER_SCHEDULE_TERMS = {
    'horario',
    'grade',
    'agenda',
    'turma',
    'turmas',
    'aula',
    'aulas',
    'disciplina',
    'disciplinas',
    'materia',
    'materias',
}
TEACHER_CLASS_TERMS = {'turma', 'turmas', 'classe', 'classes'}
TEACHER_SUBJECT_TERMS = {'disciplina', 'disciplinas', 'materia', 'materias'}
FINANCE_OPEN_TERMS = {'aberto', 'abertos', 'em aberto', 'pendencia', 'pendencias', 'boleto', 'boletos'}
FINANCE_OVERDUE_TERMS = {'vencido', 'vencidos', 'vencida', 'vencidas', 'atrasado', 'atrasados', 'inadimplencia'}
FINANCE_PAID_TERMS = {
    'pago',
    'pagos',
    'paga',
    'pagas',
    'quitado',
    'quitados',
    'quitada',
    'quitadas',
    'pagamento',
    'pagamentos',
}
FINANCE_SECOND_COPY_TERMS = {'segunda via', '2a via', 'boleto', 'boletos'}
SUBJECT_HINTS = {
    'matematica': {'matematica'},
    'portugues': {'portugues', 'redacao'},
    'biologia': {'biologia', 'bio'},
}
PUBLIC_PRICING_TERMS = {
    'mensalidade',
    'mensalidades',
    'valor',
    'valores',
    'preco',
    'preços',
    'preco',
    'precos',
    'bolsa',
    'bolsas',
    'desconto',
    'descontos',
    'taxa de matricula',
    'taxa de matrícula',
}
PUBLIC_SCHEDULE_TERMS = {
    'horario',
    'horários',
    'horario de aula',
    'horário de aula',
    'turno',
    'turnos',
    'integral',
    'periodo integral',
    'período integral',
}
PUBLIC_CONTACT_TERMS = {
    'telefone',
    'whatsapp',
    'email',
    'contato',
    'fale com',
    'canal oficial',
    'canais oficiais de contato',
    'canais de contato',
    'como entrar em contato',
    'fale conosco',
}
PUBLIC_LOCATION_TERMS = {'endereco', 'endereço', 'cidade', 'estado', 'onde fica', 'localizacao', 'localização'}
PUBLIC_CONFESSIONAL_TERMS = {'confessional', 'laica', 'religiosa'}
PUBLIC_LEADERSHIP_TERMS = {
    'diretora',
    'diretor',
    'direcao',
    'direção',
    'coordenacao',
    'coordenação',
    'lideranca',
    'liderança',
}
PUBLIC_KPI_TERMS = {
    'aprovacao',
    'aprovação',
    'media de aprovacao',
    'média de aprovação',
    'indicador',
    'indicadores',
    'frequencia media',
    'frequência média',
    'familias satisfeitas',
}
PUBLIC_HIGHLIGHT_TERMS = {
    'curiosidade',
    'curiosidades',
    'diferencial',
    'diferenciais',
    'ponto forte',
    'pontos fortes',
    'unica',
    'única',
}
PUBLIC_VISIT_TERMS = {
    'visita',
    'visitas',
    'visita guiada',
    'tour',
    'conhecer a escola',
    'agendar visita',
}
PUBLIC_SEGMENT_TERMS = {
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
}
PUBLIC_ACTIVITY_TERMS = {
    'futebol',
    'futsal',
    'danca',
    'dança',
    'teatro',
    'volei',
    'vôlei',
    'robotica',
    'robótica',
    'atividade extracurricular',
    'atividades extracurriculares',
}
SUPPORT_FINANCE_TERMS = {'financeiro', 'boleto', 'mensalidade', 'pagamento', 'fatura', 'faturas'}
SUPPORT_COORDINATION_TERMS = {'coordenacao', 'pedagogico', 'ocorrencia', 'professor', 'disciplina'}
SUPPORT_SECRETARIAT_TERMS = {'secretaria', 'matricula', 'documento', 'declaracao', 'historico', 'transferencia'}
PUBLIC_ENTITY_HINTS = {
    'diretora': 'diretoria',
    'diretor': 'diretoria',
    'direcao': 'diretoria',
    'direção': 'diretoria',
    'coordenacao': 'coordenacao',
    'coordenação': 'coordenacao',
    'aprovacao': 'indicadores institucionais',
    'aprovação': 'indicadores institucionais',
    'curiosidade': 'diferenciais institucionais',
    'curiosidades': 'diferenciais institucionais',
    'visita': 'visita institucional',
    'tour': 'visita institucional',
    'biblioteca': 'biblioteca',
    'cantina': 'cantina',
    'laboratorio': 'laboratorio',
    'laboratorio de ciencias': 'laboratorio',
    'academia': 'academia',
    'piscina': 'piscina',
    'quadra': 'quadra',
    'quadra de tenis': 'quadra de tenis',
    'tenis': 'tenis',
    'futebol': 'futebol',
    'futsal': 'futebol',
    'volei': 'volei',
    'vôlei': 'volei',
    'danca': 'aulas de danca',
    'dança': 'aulas de danca',
    'teatro': 'teatro',
    'robotica': 'maker',
    'robótica': 'maker',
    'maker': 'maker',
    'espaco maker': 'maker',
    'secretaria': 'secretaria',
    'portaria': 'portaria',
    'cantina': 'cantina',
    'orientacao educacional': 'orientacao educacional',
    'orientação educacional': 'orientacao educacional',
}
PROMPT_DISCLOSURE_TERMS = {
    'prompt',
    'system prompt',
    'prompt do sistema',
    'prompt de sistema',
    'instrucoes internas',
    'instrucoes ocultas',
    'ocultas do sistema',
    'agents.md',
    'policy.rego',
}
PROMPT_BYPASS_TERMS = {
    'ignore todas as instrucoes',
    'ignore as instrucoes',
    'revele',
    'divulgue',
    'mostre o prompt',
    'me diga o prompt',
}
COMPARATIVE_TERMS = {
    'melhor',
    'pior',
    'concorrente',
    'concorrencia',
    'concorrência',
    'comparar',
    'compare',
    'comparacao',
    'comparação',
    'versus',
    'vs',
    'publica',
    'pública',
    'privada',
}
FOLLOW_UP_OPENERS = {
    'e ',
    'e se',
    'e qual',
    'e quais',
    'e quanto',
    'e quando',
    'e como',
    'e onde',
    'e por que',
    'e pq',
}
FOLLOW_UP_REFERENTS = {
    'isso',
    'essa',
    'esse',
    'essas',
    'esses',
    'dela',
    'dele',
    'disso',
    'daquilo',
    'nisso',
}
NEGATIVE_REQUIREMENT_TERMS = {
    'nao preciso',
    'nao precisa',
    'nao e necessario',
    'nao sao necessarios',
    'nao sao necessarias',
    'dispensavel',
    'dispensaveis',
    'dispensado',
    'dispensados',
    'exceto',
}
REQUIREMENT_QUERY_TERMS = {'documento', 'documentos', 'matricula'}
KNOWN_ADMISSIONS_REQUIREMENTS = [
    'ficha cadastral ou formulario cadastral preenchido',
    'documento de identificacao do aluno',
    'CPF do aluno, quando houver',
    'historico escolar',
    'comprovante de residencia',
    'documento de identificacao do responsavel legal',
]
ADMISSIONS_REQUIREMENT_FOCUS = {
    'comprovante de residencia': 'comprovante de residencia',
    'historico escolar': 'historico escolar',
    'cpf': 'CPF do aluno',
    'documento de identificacao do responsavel': 'documento de identificacao do responsavel legal',
    'responsavel legal': 'documento de identificacao do responsavel legal',
    'documento de identificacao do aluno': 'documento de identificacao do aluno',
    'ficha cadastral': 'ficha cadastral ou formulario cadastral preenchido',
    'formulario cadastral': 'ficha cadastral ou formulario cadastral preenchido',
}
QUERY_STOPWORDS = {
    'a', 'o', 'as', 'os', 'de', 'da', 'do', 'das', 'dos', 'e', 'ou', 'para', 'por', 'com',
    'sem', 'no', 'na', 'nos', 'nas', 'um', 'uma', 'uns', 'umas', 'que', 'qual', 'quais',
    'como', 'quando', 'onde', 'porque', 'por que', 'se', 'eu', 'voce', 'vocês', 'me', 'minha',
    'meu', 'minhas', 'meus', 'ainda', 'mais', 'menos', 'sobre', 'preciso', 'precisa',
    'algum', 'alguma', 'alguns', 'algumas', 'existe', 'ha', 'haver', 'escola', 'colegio', 'colégio', 'bot', 'telegram',
    'isso', 'essa', 'esse', 'essas', 'esses', 'dela', 'dele', 'disso', 'daquilo', 'nisso',
    'pergunta', 'anterior', 'usuario', 'assistente', 'resposta', 'ultima', 'última', 'fonte', 'fontes',
}
HIGH_RISK_REASONING_TERMS = {
    'exceto',
    'excecao',
    'exceções',
    'excecao',
    'dispensa',
    'dispensavel',
    'dispensaveis',
    'obrigatorio',
    'obrigatoria',
    'obrigatorias',
    'obrigatorios',
    'ainda',
    'pode',
    'posso',
    'condicao',
    'condicoes',
    'caso',
    'se',
    'depois',
    'antes',
    'prazo',
    'perder',
    'atraso',
}
HIGH_RISK_REASONING_PHRASES = {
    'ainda posso',
    'ainda preciso',
    'posso entregar depois',
    'se eu',
    'caso eu',
    'ha excecao',
    'tem excecao',
}
VISUAL_TERMS = {'grafico', 'gráfico', 'visual', 'grafica', 'gráfico', 'barra', 'comparativo', 'evolucao', 'evolução'}


@dataclass(frozen=True)
class PublicAnswerabilityAssessment:
    enough_support: bool
    salient_terms: set[str]
    matched_terms: set[str]
    unsupported_terms: set[str]
    coverage_ratio: float
    high_risk_reasoning: bool


@dataclass(frozen=True)
class ConversationContextBundle:
    conversation_external_id: str | None
    recent_messages: list[dict[str, Any]]
    message_count: int


def _normalize_text(text: str) -> str:
    normalized = unicodedata.normalize('NFKD', text)
    without_accents = ''.join(char for char in normalized if not unicodedata.combining(char))
    return without_accents.replace('º', 'o').replace('ª', 'a').lower()


def _map_request(request: MessageResponseRequest, user_context: UserContext) -> OrchestrationRequest:
    return OrchestrationRequest(
        message=request.message,
        conversation_id=request.conversation_id,
        user=user_context,
        allow_graph_rag=request.allow_graph_rag,
        allow_handoff=request.allow_handoff,
    )


def _effective_conversation_id(request: MessageResponseRequest) -> str | None:
    if request.conversation_id:
        return request.conversation_id
    if request.channel.value == 'telegram' and request.telegram_chat_id is not None:
        return f'telegram:{request.telegram_chat_id}'
    return None


def _category_for_domain(domain: QueryDomain) -> str | None:
    if domain is QueryDomain.calendar:
        return 'calendar'
    return None


def _collect_citations(hits: list[Any], limit: int = 3) -> list[MessageResponseCitation]:
    citations: list[MessageResponseCitation] = []
    seen: set[tuple[str, str]] = set()
    for hit in hits:
        document_key = (hit.citation.document_title, hit.citation.version_label)
        if document_key in seen:
            continue
        citations.append(
            MessageResponseCitation(
                document_title=hit.citation.document_title,
                version_label=hit.citation.version_label,
                storage_path=hit.citation.storage_path,
                chunk_id=hit.citation.chunk_id,
                excerpt=hit.text_excerpt,
            )
        )
        seen.add(document_key)
        if len(citations) >= limit:
            break
    return citations


def _render_source_lines(citations: list[MessageResponseCitation]) -> str:
    if not citations:
        return ''
    lines = ['Fontes:']
    for citation in citations:
        lines.append(f'- {citation.document_title} ({citation.version_label})')
    return '\n'.join(lines)


def _format_event_line(event: CalendarEventCard) -> str:
    start = event.starts_at.astimezone().strftime('%d/%m/%Y %H:%M')
    end = event.ends_at.astimezone().strftime('%d/%m/%Y %H:%M')
    if event.description:
        return f'- {start} a {end}: {event.title}. {event.description}'
    return f'- {start} a {end}: {event.title}'


def _contains_any(message: str, terms: set[str]) -> bool:
    lowered = _normalize_text(message)
    return any(_message_matches_term(lowered, term) for term in terms)


def _message_matches_term(message: str, term: str) -> bool:
    normalized_term = _normalize_text(term).strip()
    if not normalized_term:
        return False
    pattern = r'(?<!\w)' + r'\s+'.join(re.escape(part) for part in normalized_term.split()) + r'(?!\w)'
    return re.search(pattern, message) is not None


def _extract_public_entity_hints(message: str) -> set[str]:
    lowered = _normalize_text(message)
    return {canonical for term, canonical in PUBLIC_ENTITY_HINTS.items() if _message_matches_term(lowered, term)}


def _is_prompt_disclosure_probe(message: str) -> bool:
    normalized = _normalize_text(message)
    return any(term in normalized for term in PROMPT_DISCLOSURE_TERMS) or any(
        term in normalized for term in PROMPT_BYPASS_TERMS
    )


def _is_negative_requirement_query(message: str) -> bool:
    normalized = _normalize_text(message)
    has_negative = any(_message_matches_term(normalized, term) for term in NEGATIVE_REQUIREMENT_TERMS)
    has_requirement = any(_message_matches_term(normalized, term) for term in REQUIREMENT_QUERY_TERMS)
    return has_negative and has_requirement


def _is_comparative_query(message: str) -> bool:
    normalized = _normalize_text(message)
    return any(_message_matches_term(normalized, term) for term in COMPARATIVE_TERMS)


def _is_follow_up_query(message: str) -> bool:
    raw = message.strip().lower()
    if raw.startswith('é ') or raw == 'é':
        return False
    normalized = _normalize_text(message).strip()
    if len(normalized) > 180:
        return False
    if any(normalized.startswith(opener) for opener in FOLLOW_UP_OPENERS):
        return True
    return any(_message_matches_term(normalized, term) for term in FOLLOW_UP_REFERENTS)


def _is_public_school_name_query(message: str) -> bool:
    normalized = _normalize_text(message)
    return any(
        term in normalized
        for term in {
            'nome da escola',
            'nome do colegio',
            'nome do colégio',
            'como se chama a escola',
            'como se chama o colegio',
            'como se chama o colégio',
        }
    )


def _select_public_segment(message: str) -> str | None:
    normalized = _normalize_text(message)
    if any(_message_matches_term(normalized, term) for term in {'fundamental', 'fundamental ii', '6o ano', '7o ano', '8o ano', '9o ano'}):
        return 'Ensino Fundamental II'
    if any(_message_matches_term(normalized, term) for term in {'ensino medio', 'ensino médio', 'medio', 'médio', '1o ano', '2o ano', '3o ano'}):
        return 'Ensino Medio'
    return None


def _feature_inventory_map(profile: dict[str, Any]) -> dict[str, dict[str, Any]]:
    inventory = profile.get('feature_inventory')
    if not isinstance(inventory, list):
        return {}
    result: dict[str, dict[str, Any]] = {}
    for item in inventory:
        if not isinstance(item, dict):
            continue
        key = str(item.get('feature_key', '')).strip().lower()
        if not key:
            continue
        result[key] = item
    return result


def _requested_public_features(message: str) -> list[str]:
    normalized = _normalize_text(message)
    feature_order = [
        ('biblioteca', 'biblioteca'),
        ('cantina', 'cantina'),
        ('laboratorio', 'laboratorio'),
        ('laboratorio de ciencias', 'laboratorio'),
        ('maker', 'maker'),
        ('espaco maker', 'maker'),
        ('academia', 'academia'),
        ('piscina', 'piscina'),
        ('quadra de tenis', 'quadra de tenis'),
        ('quadra', 'quadra'),
        ('futebol', 'futebol'),
        ('futsal', 'futebol'),
        ('volei', 'volei'),
        ('vôlei', 'volei'),
        ('danca', 'danca'),
        ('dança', 'danca'),
        ('teatro', 'teatro'),
        ('robotica', 'maker'),
        ('robótica', 'maker'),
        ('orientacao educacional', 'orientacao educacional'),
        ('orientação educacional', 'orientacao educacional'),
    ]
    found: list[str] = []
    for term, canonical in feature_order:
        if _message_matches_term(normalized, term) and canonical not in found:
            found.append(canonical)
    return found


def _contact_value(profile: dict[str, Any], channel: str) -> list[str]:
    contacts = profile.get('contact_channels')
    if not isinstance(contacts, list):
        return []
    values: list[str] = []
    for item in contacts:
        if not isinstance(item, dict):
            continue
        if str(item.get('channel', '')).lower() != channel:
            continue
        label = str(item.get('label', '')).strip()
        value = str(item.get('value', '')).strip()
        if not value:
            continue
        values.append(f'{label}: {value}' if label else value)
    return values


def _leadership_inventory(profile: dict[str, Any]) -> list[dict[str, Any]]:
    leadership = profile.get('leadership_team')
    return [item for item in leadership if isinstance(item, dict)] if isinstance(leadership, list) else []


def _public_kpis(profile: dict[str, Any]) -> list[dict[str, Any]]:
    entries = profile.get('public_kpis')
    return [item for item in entries if isinstance(item, dict)] if isinstance(entries, list) else []


def _public_highlights(profile: dict[str, Any]) -> list[dict[str, Any]]:
    entries = profile.get('highlights')
    return [item for item in entries if isinstance(item, dict)] if isinstance(entries, list) else []


def _public_visit_offers(profile: dict[str, Any]) -> list[dict[str, Any]]:
    entries = profile.get('visit_offers')
    return [item for item in entries if isinstance(item, dict)] if isinstance(entries, list) else []


def _public_service_catalog(profile: dict[str, Any]) -> list[dict[str, Any]]:
    entries = profile.get('service_catalog')
    return [item for item in entries if isinstance(item, dict)] if isinstance(entries, list) else []


def _select_leadership_member(profile: dict[str, Any], message: str) -> dict[str, Any] | None:
    normalized = _normalize_text(message)
    members = _leadership_inventory(profile)
    if not members:
        return None
    for member in members:
        title = _normalize_text(str(member.get('title', '')))
        focus = _normalize_text(str(member.get('focus', '')))
        name = _normalize_text(str(member.get('name', '')))
        if any(
            phrase in normalized
            for phrase in (
                title,
                name,
                'diretora',
                'diretor',
                'coordenador',
                'coordenadora',
                'direcao',
                'direção',
            )
        ):
            return member
    return members[0]


def _select_public_kpis(profile: dict[str, Any], message: str) -> list[dict[str, Any]]:
    normalized = _normalize_text(message)
    entries = _public_kpis(profile)
    if not entries:
        return []
    selected = [
        item
        for item in entries
        if any(
            marker in normalized
            for marker in (
                _normalize_text(str(item.get('label', ''))),
                _normalize_text(str(item.get('metric_key', ''))),
            )
        )
    ]
    return selected or entries[:3]


def _select_public_highlight(profile: dict[str, Any], message: str) -> dict[str, Any] | None:
    normalized = _normalize_text(message)
    entries = _public_highlights(profile)
    if not entries:
        return None
    for item in entries:
        haystack = ' '.join(
            [
                _normalize_text(str(item.get('title', ''))),
                _normalize_text(str(item.get('description', ''))),
                _normalize_text(str(item.get('highlight_key', ''))),
            ]
        )
        if any(token in haystack for token in _extract_salient_terms(message)):
            return item
    if any(
        _message_matches_term(normalized, term)
        for term in {'curiosidade', 'curiosidades', 'unica', 'única', 'diferencial', 'diferenciais'}
    ):
        for item in entries:
            if str(item.get('highlight_key')) == 'maker_integrado':
                return item
    return entries[0]


def _compose_public_profile_answer(profile: dict[str, Any], message: str) -> str:
    normalized = _normalize_text(message)
    school_name = str(profile.get('school_name', 'Colegio Horizonte'))
    city = str(profile.get('city', ''))
    state = str(profile.get('state', ''))
    district = str(profile.get('district', ''))
    address_line = str(profile.get('address_line', ''))
    confessional_status = str(profile.get('confessional_status', '')).strip().lower()
    segment = _select_public_segment(message)
    shift_offers = profile.get('shift_offers') if isinstance(profile.get('shift_offers'), list) else []
    tuition_reference = profile.get('tuition_reference') if isinstance(profile.get('tuition_reference'), list) else []
    feature_map = _feature_inventory_map(profile)

    if any(_message_matches_term(normalized, term) for term in PUBLIC_CONTACT_TERMS):
        phone_lines = _contact_value(profile, 'telefone')
        whatsapp_lines = _contact_value(profile, 'whatsapp')
        email_lines = _contact_value(profile, 'email')
        lines = [f'Voce pode falar com o {school_name} por estes canais oficiais:']
        lines.extend(f'- {item}' for item in [*phone_lines, *whatsapp_lines, *email_lines])
        return '\n'.join(lines)

    if any(_message_matches_term(normalized, term) for term in PUBLIC_LOCATION_TERMS):
        location = ', '.join(part for part in [address_line, district, city, state] if part)
        return f'O {school_name} fica em {location}.'

    if any(_message_matches_term(normalized, term) for term in PUBLIC_CONFESSIONAL_TERMS):
        if confessional_status == 'laica':
            return (
                f'O {school_name} e uma escola laica. '
                'A proposta institucional e plural e nao confessional.'
            )
        return f'O perfil publico atual classifica a escola como {confessional_status}.'

    if any(_message_matches_term(normalized, term) for term in PUBLIC_LEADERSHIP_TERMS):
        member = _select_leadership_member(profile, message)
        if member is None:
            return f'A base publica atual nao traz a lideranca institucional detalhada do {school_name}.'
        contact_channel = str(member.get('contact_channel', '')).strip()
        notes = str(member.get('notes', '')).strip()
        lines = [
            f"{member.get('title', 'Lideranca institucional')}: {member.get('name', school_name)}.",
            str(member.get('focus', '')).strip(),
        ]
        if contact_channel:
            lines.append(f'Canal institucional: {contact_channel}.')
        if notes:
            lines.append(notes)
        return ' '.join(line for line in lines if line)

    if any(_message_matches_term(normalized, term) for term in PUBLIC_KPI_TERMS):
        entries = _select_public_kpis(profile, message)
        if not entries:
            return f'A base publica atual nao traz indicadores institucionais publicados do {school_name}.'
        if len(entries) == 1:
            item = entries[0]
            notes = str(item.get('notes', '')).strip()
            return (
                f"{item.get('label', 'Indicador institucional')}: {item.get('value', '--')}{item.get('unit', '')} "
                f"({item.get('reference_period', 'periodo nao informado')}). {notes}".strip()
            )
        lines = ['Indicadores institucionais publicos mais recentes:']
        for item in entries:
            lines.append(
                f"- {item.get('label', 'Indicador')}: {item.get('value', '--')}{item.get('unit', '')} "
                f"({item.get('reference_period', 'periodo nao informado')})"
            )
        return '\n'.join(lines)

    if any(_message_matches_term(normalized, term) for term in PUBLIC_HIGHLIGHT_TERMS):
        item = _select_public_highlight(profile, message)
        if item is None:
            return f'A base publica atual nao traz diferenciais institucionais consolidados do {school_name}.'
        evidence_line = str(item.get('evidence_line', '')).strip()
        intro = 'Diferencial institucional'
        if any(
            _message_matches_term(normalized, term)
            for term in {'curiosidade', 'curiosidades', 'unica', 'única'}
        ):
            intro = 'Uma curiosidade documentada desta escola'
        lines = [f"{intro}: {item.get('title', 'Diferencial institucional')}. {item.get('description', '')}"]
        if evidence_line:
            lines.append(f'Evidencia institucional: {evidence_line}')
        return ' '.join(line for line in lines if line)

    if any(_message_matches_term(normalized, term) for term in PUBLIC_VISIT_TERMS):
        offers = _public_visit_offers(profile)
        services = _public_service_catalog(profile)
        if not offers:
            return f'A base publica atual nao traz janelas de visita institucional do {school_name}.'
        lines = [f'Janelas publicas de visita do {school_name}:']
        for item in offers:
            lines.append(
                '- {title}: {day_label}, das {start_time} as {end_time}, em {location}. {notes}'.format(
                    title=item.get('title', 'Visita institucional'),
                    day_label=item.get('day_label', 'dia util'),
                    start_time=item.get('start_time', '--:--'),
                    end_time=item.get('end_time', '--:--'),
                    location=item.get('location', 'local a confirmar'),
                    notes=str(item.get('notes', '')).strip(),
                ).rstrip()
            )
        visit_service = next(
            (item for item in services if str(item.get('service_key')) == 'visita_institucional'),
            None,
        )
        if visit_service is not None:
            lines.append(
                'Agendamento: {request_channel}. Prazo de confirmacao: {typical_eta}.'.format(
                    request_channel=visit_service.get('request_channel', 'canal institucional'),
                    typical_eta=visit_service.get('typical_eta', 'ate 1 dia util'),
                )
            )
        return '\n'.join(lines)

    if any(_message_matches_term(normalized, term) for term in PUBLIC_PRICING_TERMS):
        relevant_rows = [
            row for row in tuition_reference
            if isinstance(row, dict) and (segment is None or str(row.get('segment')) == segment)
        ]
        if not relevant_rows:
            relevant_rows = [row for row in tuition_reference if isinstance(row, dict)]
        lines = ['Valores publicos de referencia para 2026:']
        for row in relevant_rows:
            lines.append(
                '- {segment} ({shift_label}): mensalidade {monthly_amount} e taxa de matricula {enrollment_fee}. {notes}'.format(
                    segment=row.get('segment', 'Segmento'),
                    shift_label=row.get('shift_label', 'turno'),
                    monthly_amount=row.get('monthly_amount', '0.00'),
                    enrollment_fee=row.get('enrollment_fee', '0.00'),
                    notes=row.get('notes', '').strip(),
                ).rstrip()
            )
        lines.append('Se quiser, eu tambem posso resumir bolsas, descontos comerciais e canais de matricula.')
        return '\n'.join(lines)

    requested_features = _requested_public_features(message)
    if requested_features:
        lines = [f'No perfil publico atual do {school_name}:']
        for feature_key in requested_features:
            item = feature_map.get(feature_key)
            if item is None:
                lines.append(f'- Ainda nao encontrei uma informacao oficial sobre {feature_key}.')
                continue
            label = str(item.get('label', feature_key))
            available = bool(item.get('available'))
            notes = str(item.get('notes', '')).strip()
            if available:
                lines.append(f'- Sim: {label}. {notes}'.rstrip())
            else:
                lines.append(f'- Nao: {label}. {notes}'.rstrip())
        return '\n'.join(lines)

    if any(_message_matches_term(normalized, term) for term in PUBLIC_SCHEDULE_TERMS):
        relevant_rows = [
            row for row in shift_offers
            if isinstance(row, dict) and (segment is None or str(row.get('segment')) == segment)
        ]
        if not relevant_rows:
            relevant_rows = [row for row in shift_offers if isinstance(row, dict)]
        lines = ['Turnos e horarios documentados:']
        for row in relevant_rows:
            lines.append(
                '- {segment} ({shift_label}): {starts_at} as {ends_at}. {notes}'.format(
                    segment=row.get('segment', 'Segmento'),
                    shift_label=row.get('shift_label', 'turno'),
                    starts_at=row.get('starts_at', '--:--'),
                    ends_at=row.get('ends_at', '--:--'),
                    notes=row.get('notes', '').strip(),
                ).rstrip()
            )
        return '\n'.join(lines)

    if any(_message_matches_term(normalized, term) for term in PUBLIC_SEGMENT_TERMS):
        segments = profile.get('segments')
        if not isinstance(segments, list) or not segments:
            return f'O perfil publico atual do {school_name} nao traz os segmentos atendidos.'
        lines = [f'O {school_name} atende hoje estes segmentos:']
        lines.extend(f'- {item}' for item in segments if isinstance(item, str))
        return '\n'.join(lines)

    if _is_public_school_name_query(message):
        return f'O nome oficial da escola e {school_name}.'

    headline = str(profile.get('short_headline', '')).strip()
    if headline:
        return f'{school_name}: {headline}'
    return f'O nome oficial da escola e {school_name}.'


def _compose_negative_requirement_answer() -> str:
    lines = [
        'A base atual informa os documentos exigidos para a matricula, mas nao lista explicitamente quais documentos sao dispensaveis.',
        'Por isso, nao e seguro afirmar o que voce "nao precisa" levar.',
        'O que esta explicitamente exigido hoje e:',
    ]
    lines.extend(f'- {item}' for item in KNOWN_ADMISSIONS_REQUIREMENTS)
    lines.append('Se quiser, eu posso resumir apenas os documentos exigidos ou explicar as etapas da matricula.')
    return '\n'.join(lines)


def _compose_comparative_gap_answer() -> str:
    return (
        'Posso explicar os diferenciais documentados desta escola, mas a base publica atual nao sustenta uma '
        'comparacao justa com uma concorrente especifica sem fontes comparativas confiaveis. '
        'Se quiser, eu posso resumir os pontos fortes documentados desta escola ou fazer uma comparacao limitada '
        'se voce informar qual instituicao deseja considerar.'
    )


def _extract_salient_terms(message: str) -> set[str]:
    normalized = _normalize_text(message)
    tokens = {
        token
        for token in re.findall(r'[a-z0-9]{3,}', normalized)
        if token not in QUERY_STOPWORDS and not token.isdigit()
    }
    if 'matricula' in normalized:
        tokens.add('matricula')
    if 'biblioteca' in normalized:
        tokens.add('biblioteca')
    return tokens


def _extract_public_gap_focus(message: str) -> str | None:
    normalized = _normalize_text(message)
    if _message_matches_term(normalized, 'confessional'):
        return 'se a escola e confessional'

    facility_labels: list[str] = []
    has_tennis_court = _message_matches_term(normalized, 'quadra de tenis')
    for term, label in [
        ('academia', 'academia'),
        ('piscina', 'piscina'),
        ('quadra de tenis', 'quadra de tenis'),
        ('quadra', 'quadra'),
        ('tenis', 'tenis'),
        ('futebol', 'futebol'),
        ('danca', 'aulas de danca'),
        ('dança', 'aulas de danca'),
    ]:
        if has_tennis_court and term in {'quadra', 'tenis'}:
            continue
        if _message_matches_term(normalized, term) and label not in facility_labels:
            facility_labels.append(label)

    if facility_labels:
        if len(facility_labels) == 1:
            return f'se a escola possui {facility_labels[0]}'
        if len(facility_labels) == 2:
            return f'se a escola possui {facility_labels[0]} e {facility_labels[1]}'
        return f"se a escola possui {', '.join(facility_labels[:-1])} e {facility_labels[-1]}"

    return None


def _contains_high_risk_reasoning(message: str) -> bool:
    normalized = _normalize_text(message)
    if any(_message_matches_term(normalized, phrase) for phrase in HIGH_RISK_REASONING_PHRASES):
        return True
    return any(_message_matches_term(normalized, term) for term in HIGH_RISK_REASONING_TERMS)


def _extract_admissions_requirement_focus(message: str) -> str | None:
    normalized = _normalize_text(message)
    for term, label in ADMISSIONS_REQUIREMENT_FOCUS.items():
        if _message_matches_term(normalized, term):
            return label
    return None


def _assess_public_answerability(message: str, retrieval_hits: list[Any], query_hints: set[str]) -> PublicAnswerabilityAssessment:
    salient_terms = _extract_salient_terms(message)
    if query_hints:
        salient_terms = {*(salient_terms), *query_hints}
    if not salient_terms:
        return PublicAnswerabilityAssessment(
            enough_support=bool(retrieval_hits),
            salient_terms=set(),
            matched_terms=set(),
            unsupported_terms=set(),
            coverage_ratio=1.0 if retrieval_hits else 0.0,
            high_risk_reasoning=_contains_high_risk_reasoning(message),
        )

    haystack = ' '.join(
        _normalize_text(
            ' '.join(
                filter(
                    None,
                    [
                        getattr(hit, 'document_title', None),
                        getattr(hit, 'text_excerpt', None),
                        getattr(hit, 'contextual_summary', None),
                    ],
                )
            )
        )
        for hit in retrieval_hits
    )
    matched_terms = {term for term in salient_terms if term in haystack}
    unsupported_terms = salient_terms - matched_terms
    coverage_ratio = len(matched_terms) / len(salient_terms) if salient_terms else 0.0
    high_risk_reasoning = _contains_high_risk_reasoning(message)
    enough_support = bool(retrieval_hits) and coverage_ratio >= (0.75 if high_risk_reasoning else 0.45)
    if high_risk_reasoning and unsupported_terms:
        enough_support = False
    return PublicAnswerabilityAssessment(
        enough_support=enough_support,
        salient_terms=salient_terms,
        matched_terms=matched_terms,
        unsupported_terms=unsupported_terms,
        coverage_ratio=coverage_ratio,
        high_risk_reasoning=high_risk_reasoning,
    )


def _compose_answerability_gap_answer(assessment: PublicAnswerabilityAssessment, message: str) -> str:
    requirement_focus = _extract_admissions_requirement_focus(message)
    if assessment.high_risk_reasoning:
        if requirement_focus and _contains_any(
            message,
            {'excecao', 'dispensa', 'dispensavel', 'dispensaveis', 'nao preciso', 'nao precisa'},
        ):
            return (
                f'A base publica atual registra {requirement_focus} como requisito da matricula, '
                'mas nao descreve excecoes, dispensas ou condicoes especiais para esse item. '
                'Para evitar uma orientacao incorreta, nao vou afirmar que exista uma excecao sem documento oficial especifico. '
                'Se quiser, eu posso resumir apenas os requisitos explicitamente publicados.'
            )
        if assessment.unsupported_terms:
            labels = ', '.join(sorted(assessment.unsupported_terms))
            return (
                'A base publica atual nao sustenta com seguranca todos os pontos dessa pergunta, '
                f'especialmente sobre: {labels}. '
                'Para evitar uma orientacao incorreta, prefiro nao inferir alem do que esta documentado. '
                'Se quiser, eu posso responder apenas o que esta explicitamente registrado na base atual.'
            )
        return (
            'A pergunta exige uma regra, excecao ou condicao que nao esta suficientemente sustentada '
            'pela base publica atual. Posso responder apenas o que estiver explicitamente documentado.'
        )
    return _compose_public_gap_answer(assessment.unsupported_terms, message)


def _extract_recent_user_message(recent_messages: list[dict[str, Any]]) -> str | None:
    for item in reversed(recent_messages):
        if not isinstance(item, dict):
            continue
        if item.get('sender_type') != 'user':
            continue
        content = str(item.get('content', '')).strip()
        if content:
            return content
    return None


def _extract_recent_assistant_message(recent_messages: list[dict[str, Any]]) -> str | None:
    for item in reversed(recent_messages):
        if not isinstance(item, dict):
            continue
        if item.get('sender_type') != 'assistant':
            continue
        content = str(item.get('content', '')).strip()
        if content:
            return content
    return None


def _build_analysis_message(message: str, conversation_context: ConversationContextBundle | None) -> str:
    if conversation_context is None or not conversation_context.recent_messages:
        return message
    if not _is_follow_up_query(message):
        return message

    last_user_message = _extract_recent_user_message(conversation_context.recent_messages)
    last_assistant_message = _extract_recent_assistant_message(conversation_context.recent_messages)
    if not last_user_message and not last_assistant_message:
        return message

    entity_hints = {
        *_extract_public_entity_hints(last_user_message or ''),
        *_extract_public_entity_hints(last_assistant_message or ''),
    }
    if entity_hints:
        referents = ', '.join(sorted(entity_hints))
        return f'{message} sobre {referents}'
    if last_user_message:
        return f'{message} contexto anterior {last_user_message}'
    return message


def _retrieval_hits_cover_query_hints(retrieval_hits: list[Any], query_hints: set[str]) -> bool:
    if not query_hints:
        return True
    if not retrieval_hits:
        return False

    haystack = ' '.join(
        _normalize_text(
            ' '.join(
                filter(
                    None,
                    [
                        getattr(hit, 'document_title', None),
                        getattr(hit, 'text_excerpt', None),
                        getattr(hit, 'contextual_summary', None),
                    ],
                )
            )
        )
        for hit in retrieval_hits
    )
    return all(hint in haystack for hint in query_hints)


def _filter_retrieval_hits_by_query_hints(retrieval_hits: list[Any], query_hints: set[str]) -> list[Any]:
    if not query_hints:
        return retrieval_hits

    filtered_hits = []
    for hit in retrieval_hits:
        haystack = _normalize_text(
            ' '.join(
                filter(
                    None,
                    [
                        getattr(hit, 'document_title', None),
                        getattr(hit, 'text_excerpt', None),
                        getattr(hit, 'contextual_summary', None),
                    ],
                )
            )
        )
        if any(hint in haystack for hint in query_hints):
            filtered_hits.append(hit)
    return filtered_hits or retrieval_hits


def _compose_public_gap_answer(query_hints: set[str], message: str | None = None) -> str:
    focus = _extract_public_gap_focus(message or '')
    if focus:
        return (
            f'A base publica atual nao informa {focus}. '
            'Se isso for um criterio importante, a base documental precisa ser ampliada ou a escola precisa publicar essa informacao de forma oficial.'
        )
    if query_hints:
        labels = ', '.join(sorted(query_hints))
        return (
            f'Ainda nao encontrei uma resposta suficientemente suportada na base publica sobre {labels}. '
            'Se esse servico existir, preciso que a base documental seja atualizada ou que voce reformule a pergunta '
            'com o nome oficial do setor.'
        )
    return (
        'Ainda nao encontrei uma resposta suficientemente suportada na base publica. '
        'Tente reformular a pergunta com termos como matricula, calendario, secretaria ou atendimento.'
    )


def _extract_term_filter(message: str) -> str | None:
    lowered = _normalize_text(message)
    patterns = {
        'B1': [r'\bb1\b', r'\b1o?\s*bimestre\b', r'\bprimeiro\s*bimestre\b'],
        'B2': [r'\bb2\b', r'\b2o?\s*bimestre\b', r'\bsegundo\s*bimestre\b'],
        'B3': [r'\bb3\b', r'\b3o?\s*bimestre\b', r'\bterceiro\s*bimestre\b'],
        'B4': [r'\bb4\b', r'\b4o?\s*bimestre\b', r'\bquarto\s*bimestre\b'],
    }
    for suffix, candidates in patterns.items():
        if any(re.search(candidate, lowered) for candidate in candidates):
            return suffix
    return None


def _user_role_from_actor(actor: dict[str, Any] | None) -> UserRole:
    role_code = actor.get('role_code') if isinstance(actor, dict) else None
    if isinstance(role_code, str):
        try:
            return UserRole(role_code)
        except ValueError:
            return UserRole.anonymous
    return UserRole.anonymous


def _user_context_from_actor(actor: dict[str, Any] | None) -> UserContext:
    if not actor:
        return UserContext()

    linked_student_ids = actor.get('linked_student_ids')
    if not isinstance(linked_student_ids, list):
        linked_student_ids = []

    return UserContext(
        role=_user_role_from_actor(actor),
        authenticated=True,
        linked_student_ids=[str(student_id) for student_id in linked_student_ids],
        scopes=[],
    )


async def _api_core_get(
    *,
    settings: Any,
    path: str,
    params: dict[str, object] | None = None,
) -> tuple[dict[str, Any] | None, int | None]:
    headers = {'X-Internal-Api-Token': settings.internal_api_token}
    with start_span(
        'eduassist.api_core.get',
        tracer_name='eduassist.ai_orchestrator.runtime',
        **{
            'eduassist.api_core.path': path,
            'eduassist.api_core.has_params': bool(params),
        },
    ):
        try:
            async with httpx.AsyncClient(timeout=12.0) as client:
                response = await client.get(f'{settings.api_core_url}{path}', params=params, headers=headers)
            response.raise_for_status()
            payload = response.json()
            set_span_attributes(**{'http.status_code': response.status_code})
            if isinstance(payload, dict):
                return payload, response.status_code
            return None, response.status_code
        except httpx.HTTPStatusError as exc:
            set_span_attributes(**{'http.status_code': exc.response.status_code})
            return None, exc.response.status_code
        except Exception:
            return None, None


async def _api_core_post(
    *,
    settings: Any,
    path: str,
    payload: dict[str, object],
) -> tuple[dict[str, Any] | None, int | None]:
    headers = {
        'X-Internal-Api-Token': settings.internal_api_token,
        'Content-Type': 'application/json',
    }
    with start_span(
        'eduassist.api_core.post',
        tracer_name='eduassist.ai_orchestrator.runtime',
        **{
            'eduassist.api_core.path': path,
            'eduassist.api_core.has_payload': bool(payload),
        },
    ):
        try:
            async with httpx.AsyncClient(timeout=12.0) as client:
                response = await client.post(f'{settings.api_core_url}{path}', json=payload, headers=headers)
            response.raise_for_status()
            body = response.json()
            set_span_attributes(**{'http.status_code': response.status_code})
            if isinstance(body, dict):
                return body, response.status_code
            return None, response.status_code
        except httpx.HTTPStatusError as exc:
            set_span_attributes(**{'http.status_code': exc.response.status_code})
            return None, exc.response.status_code
        except Exception:
            return None, None


async def _fetch_public_school_profile(settings: Any) -> dict[str, Any] | None:
    payload, status_code = await _api_core_get(
        settings=settings,
        path='/v1/public/school-profile',
    )
    if status_code != 200 or not isinstance(payload, dict):
        return None
    profile = payload.get('profile')
    return profile if isinstance(profile, dict) else None


async def _fetch_conversation_context(
    *,
    settings: Any,
    conversation_external_id: str | None,
    channel: str,
) -> ConversationContextBundle | None:
    if not conversation_external_id:
        return None

    payload, status_code = await _api_core_get(
        settings=settings,
        path='/v1/internal/conversations/context',
        params={
            'conversation_external_id': conversation_external_id,
            'channel': channel,
            'limit': 6,
        },
    )
    if status_code != 200 or not isinstance(payload, dict):
        return None

    recent_messages = payload.get('recent_messages')
    if not isinstance(recent_messages, list):
        recent_messages = []

    return ConversationContextBundle(
        conversation_external_id=conversation_external_id,
        recent_messages=[item for item in recent_messages if isinstance(item, dict)],
        message_count=int(payload.get('message_count', 0) or 0),
    )


async def _persist_conversation_turn(
    *,
    settings: Any,
    conversation_external_id: str | None,
    channel: str,
    actor: dict[str, Any] | None,
    user_message: str,
    assistant_message: str,
) -> None:
    if not conversation_external_id:
        return

    actor_user_id = actor.get('user_id') if isinstance(actor, dict) else None
    payload = {
        'channel': channel,
        'conversation_external_id': conversation_external_id,
        'actor_user_id': actor_user_id,
        'messages': [
            {'sender_type': 'user', 'content': user_message},
            {'sender_type': 'assistant', 'content': assistant_message},
        ],
    }
    await _api_core_post(
        settings=settings,
        path='/v1/internal/conversations/messages',
        payload=payload,
    )


async def _fetch_actor_context(*, settings: Any, telegram_chat_id: int | None) -> dict[str, Any] | None:
    if telegram_chat_id is None:
        return None
    payload, status_code = await _api_core_get(
        settings=settings,
        path='/v1/internal/identity/context',
        params={'telegram_chat_id': telegram_chat_id},
    )
    if status_code != 200 or payload is None:
        return None
    actor = payload.get('actor')
    return actor if isinstance(actor, dict) else None


async def _fetch_public_school_profile(*, settings: Any) -> dict[str, Any] | None:
    payload, status_code = await _api_core_get(
        settings=settings,
        path='/v1/public/school-profile',
    )
    if status_code != 200 or payload is None:
        return None
    profile = payload.get('profile')
    return profile if isinstance(profile, dict) else None


async def _fetch_public_calendar(*, settings: Any) -> list[CalendarEventCard]:
    today = date.today()
    payload, status_code = await _api_core_get(
        settings=settings,
        path='/v1/calendar/public',
        params={
            'date_from': today.isoformat(),
            'date_to': (today + timedelta(days=120)).isoformat(),
            'limit': 6,
        },
    )
    if status_code != 200 or payload is None:
        return []
    events = payload.get('events', [])
    if not isinstance(events, list):
        return []
    return [CalendarEventCard.model_validate(event) for event in events]


def _select_handoff_queue(message: str) -> str:
    normalized = _normalize_text(message)
    if any(term in normalized for term in SUPPORT_FINANCE_TERMS):
        return 'financeiro'
    if any(term in normalized for term in SUPPORT_COORDINATION_TERMS):
        return 'coordenacao'
    if any(term in normalized for term in SUPPORT_SECRETARIAT_TERMS):
        return 'secretaria'
    return 'atendimento'


def _build_handoff_summary(*, request: MessageResponseRequest, actor: dict[str, Any] | None) -> str:
    requester = 'Visitante do bot'
    if actor and isinstance(actor.get('full_name'), str):
        requester = str(actor['full_name'])

    message_excerpt = ' '.join(request.message.split())
    if len(message_excerpt) > 220:
        message_excerpt = f'{message_excerpt[:219].rstrip()}...'

    return f'{requester} solicitou apoio humano pelo canal {request.channel.value}: {message_excerpt}'


async def _create_support_handoff(
    *,
    settings: Any,
    request: MessageResponseRequest,
    actor: dict[str, Any] | None,
) -> dict[str, Any] | None:
    conversation_external_id = request.conversation_id
    if not conversation_external_id:
        conversation_external_id = f'{request.channel.value}:{request.telegram_chat_id or "anonymous"}:handoff'

    payload = {
        'conversation_external_id': conversation_external_id,
        'channel': request.channel.value,
        'queue_name': _select_handoff_queue(request.message),
        'summary': _build_handoff_summary(request=request, actor=actor),
        'telegram_chat_id': request.telegram_chat_id,
        'user_message': request.message,
    }
    response_payload, status_code = await _api_core_post(
        settings=settings,
        path='/v1/internal/support/handoffs',
        payload=payload,
    )
    if status_code != 200 or response_payload is None:
        return None
    return response_payload


def _extract_requested_date(message: str) -> date | None:
    normalized = _normalize_text(message)
    explicit_match = re.search(r'\b(\d{1,2})[/-](\d{1,2})(?:[/-](\d{2,4}))?\b', normalized)
    if explicit_match:
        day = int(explicit_match.group(1))
        month = int(explicit_match.group(2))
        year = explicit_match.group(3)
        if year is None:
            year_value = date.today().year
        else:
            year_value = int(year)
            if year_value < 100:
                year_value += 2000
        try:
            return date(year_value, month, day)
        except ValueError:
            return None

    weekday_map = {
        'segunda': 0,
        'terca': 1,
        'terça': 1,
        'quarta': 2,
        'quinta': 3,
        'sexta': 4,
        'sabado': 5,
        'sábado': 5,
    }
    today = date.today()
    for label, weekday in weekday_map.items():
        if _message_matches_term(normalized, label):
            offset = (weekday - today.weekday()) % 7
            if offset == 0:
                offset = 7
            return today + timedelta(days=offset)
    return None


def _extract_requested_window(message: str) -> str | None:
    normalized = _normalize_text(message)
    time_match = re.search(r'\b(\d{1,2})(?:[:h](\d{2}))\b', normalized)
    if time_match:
        hour = int(time_match.group(1))
        minute = int(time_match.group(2) or 0)
        if 0 <= hour <= 23 and 0 <= minute <= 59:
            return f'{hour:02d}:{minute:02d}'
    if 'manha' in normalized:
        return 'manha'
    if 'tarde' in normalized:
        return 'tarde'
    if 'noite' in normalized:
        return 'noite'
    return None


def _detect_institutional_request_target_area(message: str) -> str:
    normalized = _normalize_text(message)
    for term, area in (
        ('direcao', 'direcao'),
        ('direção', 'direcao'),
        ('diretora', 'direcao'),
        ('diretor', 'direcao'),
        ('ouvidoria', 'ouvidoria'),
        ('coordenacao', 'coordenacao'),
        ('coordenação', 'coordenacao'),
        ('financeiro', 'financeiro'),
        ('secretaria', 'secretaria'),
    ):
        if _message_matches_term(normalized, term):
            return area
    return 'direcao'


def _detect_institutional_request_category(message: str) -> str:
    normalized = _normalize_text(message)
    for term, category in (
        ('bolsa', 'bolsas'),
        ('desconto', 'descontos'),
        ('reclamacao', 'manifestacao'),
        ('reclamação', 'manifestacao'),
        ('sugestao', 'sugestao'),
        ('sugestão', 'sugestao'),
        ('elogio', 'elogio'),
        ('ocorrencia', 'ocorrencia'),
        ('ocorrência', 'ocorrencia'),
    ):
        if _message_matches_term(normalized, term):
            return category
    return 'solicitacao_geral'


def _build_institutional_request_subject(message: str) -> str:
    compact = ' '.join(message.split())
    if len(compact) <= 140:
        return compact
    return f'{compact[:137].rstrip()}...'


async def _create_visit_booking(
    *,
    settings: Any,
    request: MessageResponseRequest,
    actor: dict[str, Any] | None,
) -> dict[str, Any] | None:
    conversation_external_id = request.conversation_id or _effective_conversation_id(request)
    if not conversation_external_id:
        return None
    preferred_date = _extract_requested_date(request.message)
    preferred_window = _extract_requested_window(request.message)
    payload = {
        'conversation_external_id': conversation_external_id,
        'channel': request.channel.value,
        'telegram_chat_id': request.telegram_chat_id,
        'audience_name': str(actor.get('full_name')) if isinstance(actor, dict) and actor.get('full_name') else None,
        'audience_contact': None,
        'interested_segment': _select_public_segment(request.message),
        'preferred_date': preferred_date.isoformat() if preferred_date else None,
        'preferred_window': preferred_window,
        'attendee_count': 1,
        'notes': request.message,
    }
    response_payload, status_code = await _api_core_post(
        settings=settings,
        path='/v1/internal/workflows/visit-bookings',
        payload=payload,
    )
    if status_code != 200 or response_payload is None:
        return None
    return response_payload


async def _create_institutional_request(
    *,
    settings: Any,
    request: MessageResponseRequest,
    actor: dict[str, Any] | None,
) -> dict[str, Any] | None:
    conversation_external_id = request.conversation_id or _effective_conversation_id(request)
    if not conversation_external_id:
        return None
    payload = {
        'conversation_external_id': conversation_external_id,
        'channel': request.channel.value,
        'telegram_chat_id': request.telegram_chat_id,
        'target_area': _detect_institutional_request_target_area(request.message),
        'category': _detect_institutional_request_category(request.message),
        'subject': _build_institutional_request_subject(request.message),
        'details': request.message,
        'requester_contact': None,
    }
    response_payload, status_code = await _api_core_post(
        settings=settings,
        path='/v1/internal/workflows/institutional-requests',
        payload=payload,
    )
    if status_code != 200 or response_payload is None:
        return None
    return response_payload


def _compose_visit_booking_answer(response_payload: dict[str, Any] | None, school_profile: dict[str, Any] | None) -> str:
    school_name = str((school_profile or {}).get('school_name', 'Colegio Horizonte'))
    if not response_payload:
        return (
            f'Posso orientar sobre visitas ao {school_name}, mas nao consegui registrar o pedido agora. '
            'Tente novamente em instantes ou use o canal de admissions.'
        )
    item = response_payload.get('item')
    if not isinstance(item, dict):
        return (
            f'Registrei a intencao de visita ao {school_name}, mas nao consegui recuperar o protocolo agora. '
            'Use admissions para confirmar o agendamento.'
        )
    preferred_date = item.get('preferred_date')
    preferred_window = item.get('preferred_window')
    slot_parts = []
    if preferred_date:
        slot_parts.append(str(preferred_date))
    if preferred_window:
        slot_parts.append(str(preferred_window))
    slot = ' - '.join(slot_parts) if slot_parts else 'janela a confirmar'
    return (
        f"Pedido de visita registrado para o {school_name}. Protocolo: {item.get('protocol_code', 'indisponivel')}. "
        f"Preferencia informada: {slot}. "
        f"Fila responsavel: {item.get('queue_name', 'admissoes')}. "
        f"Ticket operacional: {item.get('linked_ticket_code', 'a confirmar')}. "
        'A equipe comercial valida a janela e retorna com a confirmacao.'
    )


def _compose_institutional_request_answer(response_payload: dict[str, Any] | None) -> str:
    if not response_payload:
        return (
            'Posso orientar sobre protocolos institucionais, mas nao consegui registrar a solicitacao agora. '
            'Tente novamente em instantes ou use a secretaria.'
        )
    item = response_payload.get('item')
    if not isinstance(item, dict):
        return (
            'Registrei a manifestacao institucional, mas nao consegui recuperar o protocolo neste momento. '
            'Use a secretaria ou a ouvidoria para confirmar.'
        )
    return (
        f"Solicitacao institucional registrada para {item.get('target_area', 'o setor responsavel')}. "
        f"Protocolo: {item.get('protocol_code', 'indisponivel')}. "
        f"Assunto: {item.get('subject', 'solicitacao institucional')}. "
        f"Fila responsavel: {item.get('queue_name', 'atendimento')}. "
        f"Ticket operacional: {item.get('linked_ticket_code', 'a confirmar')}. "
        'A equipe faz a triagem inicial e segue o retorno pelo fluxo institucional.'
    )


def _wants_visual_response(message: str) -> bool:
    return _contains_any(message, VISUAL_TERMS)


def _load_font(size: int):
    try:
        return ImageFont.truetype('DejaVuSans.ttf', size=size)
    except Exception:  # pragma: no cover - font availability depends on runtime image
        return ImageFont.load_default()


def _build_visual_asset(*, title: str, subtitle: str, labels: list[str], values: list[float], unit: str) -> MessageResponseVisualAsset | None:
    if not labels or not values or len(labels) != len(values):
        return None

    width, height = 1280, 820
    padding_left, padding_right = 110, 80
    padding_top, padding_bottom = 110, 120
    plot_width = width - padding_left - padding_right
    plot_height = height - padding_top - padding_bottom
    bar_gap = 28
    bar_width = max(48, int((plot_width - bar_gap * (len(values) - 1)) / max(len(values), 1)))
    max_value = max(max(values), 1.0)

    image = Image.new('RGB', (width, height), '#f6f3ee')
    draw = ImageDraw.Draw(image)
    title_font = _load_font(38)
    subtitle_font = _load_font(22)
    axis_font = _load_font(20)
    label_font = _load_font(18)

    draw.text((padding_left, 28), title, font=title_font, fill='#16213a')
    if subtitle:
        draw.text((padding_left, 72), subtitle, font=subtitle_font, fill='#556070')

    axis_x0 = padding_left
    axis_y0 = padding_top
    axis_x1 = padding_left
    axis_y1 = padding_top + plot_height
    axis_x2 = padding_left + plot_width
    axis_y2 = axis_y1
    draw.line((axis_x0, axis_y0, axis_x1, axis_y1), fill='#5c6470', width=3)
    draw.line((axis_x1, axis_y1, axis_x2, axis_y2), fill='#5c6470', width=3)

    palette = ['#0f766e', '#1d4ed8', '#c2410c', '#7c3aed', '#b45309', '#0f172a']
    for index, value in enumerate(values):
        x0 = padding_left + index * (bar_width + bar_gap)
        x1 = x0 + bar_width
        ratio = value / max_value if max_value else 0
        bar_height = int(ratio * (plot_height - 30))
        y0 = padding_top + plot_height - bar_height
        y1 = padding_top + plot_height
        color = palette[index % len(palette)]
        draw.rounded_rectangle((x0, y0, x1, y1), radius=12, fill=color)
        value_label = f'{value:.1f}{unit}'.rstrip('0').rstrip('.') if unit != '%' else f'{value:.1f}%'
        draw.text((x0, y0 - 28), value_label, font=axis_font, fill='#16213a')
        draw.text((x0, y1 + 16), labels[index], font=label_font, fill='#16213a')

    buffer = io.BytesIO()
    image.save(buffer, format='PNG')
    encoded = base64.b64encode(buffer.getvalue()).decode('ascii')
    return MessageResponseVisualAsset(
        title=title,
        mime_type='image/png',
        base64_data=encoded,
        caption=subtitle or title,
    )


def _build_public_kpi_visual(profile: dict[str, Any], message: str) -> list[MessageResponseVisualAsset]:
    entries = _select_public_kpis(profile, message)
    if not entries:
        return []
    labels = [str(item.get('label', 'Indicador'))[:18] for item in entries]
    values = [float(item.get('value', 0.0) or 0.0) for item in entries]
    asset = _build_visual_asset(
        title='Indicadores institucionais',
        subtitle='Painel publico mais recente',
        labels=labels,
        values=values,
        unit='%',
    )
    return [asset] if asset is not None else []


def _build_academic_visual(summary: dict[str, Any], message: str, student_name: str) -> list[MessageResponseVisualAsset]:
    normalized = _normalize_text(message)
    if _contains_any(normalized, ATTENDANCE_TERMS) and not _contains_any(normalized, GRADE_TERMS):
        attendance_rows = summary.get('attendance')
        if not isinstance(attendance_rows, list) or not attendance_rows:
            return []
        labels = [str(item.get('subject_name', 'Disciplina'))[:18] for item in attendance_rows[:6] if isinstance(item, dict)]
        values = []
        for item in attendance_rows[:6]:
            if not isinstance(item, dict):
                continue
            present = float(item.get('present_count', 0) or 0)
            late = float(item.get('late_count', 0) or 0)
            absent = float(item.get('absent_count', 0) or 0)
            total = present + late + absent
            values.append(round(((present + late) / total) * 100, 1) if total else 0.0)
        asset = _build_visual_asset(
            title=f'Frequencia de {student_name}',
            subtitle='Percentual de presenca por disciplina',
            labels=labels,
            values=values,
            unit='%',
        )
        return [asset] if asset is not None else []

    grades = summary.get('grades')
    if not isinstance(grades, list) or not grades:
        return []
    per_subject: dict[str, list[float]] = {}
    for item in grades:
        if not isinstance(item, dict):
            continue
        subject_name = str(item.get('subject_name', 'Disciplina'))
        score = float(item.get('score', 0) or 0)
        max_score = float(item.get('max_score', 0) or 0)
        if max_score <= 0:
            continue
        per_subject.setdefault(subject_name, []).append(round((score / max_score) * 100, 1))
    labels = list(per_subject.keys())[:6]
    values = [round(sum(per_subject[label]) / len(per_subject[label]), 1) for label in labels]
    asset = _build_visual_asset(
        title=f'Notas de {student_name}',
        subtitle='Media percentual por disciplina',
        labels=[label[:18] for label in labels],
        values=values,
        unit='%',
    )
    return [asset] if asset is not None else []


def _build_finance_visual(summary: dict[str, Any], student_name: str) -> list[MessageResponseVisualAsset]:
    open_count = float(summary.get('open_invoice_count', 0) or 0)
    overdue_count = float(summary.get('overdue_invoice_count', 0) or 0)
    invoices = summary.get('invoices')
    paid_count = 0.0
    if isinstance(invoices, list):
        paid_count = float(sum(1 for item in invoices if isinstance(item, dict) and item.get('status') == 'paid'))
    asset = _build_visual_asset(
        title=f'Panorama financeiro de {student_name}',
        subtitle='Distribuicao de faturas na base atual',
        labels=['Em aberto', 'Vencidas', 'Pagas'],
        values=[open_count, overdue_count, paid_count],
        unit='',
    )
    return [asset] if asset is not None else []


async def _maybe_build_visual_assets(
    *,
    settings: Any,
    request: MessageResponseRequest,
    preview: Any,
    actor: dict[str, Any] | None,
    school_profile: dict[str, Any] | None,
) -> list[MessageResponseVisualAsset]:
    if not _wants_visual_response(request.message):
        return []

    if preview.classification.domain is QueryDomain.institution:
        profile = school_profile or await _fetch_public_school_profile(settings=settings)
        if profile is None:
            return []
        return _build_public_kpi_visual(profile, request.message)

    if request.telegram_chat_id is None:
        return []

    actor = actor or await _fetch_actor_context(settings=settings, telegram_chat_id=request.telegram_chat_id)
    if actor is None:
        return []

    student, clarification = _select_linked_student(actor, request.message)
    if clarification is not None or student is None:
        return []
    student_id = student.get('student_id')
    student_name = str(student.get('full_name', 'Aluno'))
    if not isinstance(student_id, str):
        return []

    if preview.classification.domain is QueryDomain.academic:
        payload, status_code = await _api_core_get(
            settings=settings,
            path=f'/v1/students/{student_id}/academic-summary',
            params={'telegram_chat_id': request.telegram_chat_id},
        )
        if status_code != 200 or not isinstance(payload, dict):
            return []
        summary = payload.get('summary')
        if not isinstance(summary, dict):
            return []
        return _build_academic_visual(summary, request.message, student_name)

    if preview.classification.domain is QueryDomain.finance:
        payload, status_code = await _api_core_get(
            settings=settings,
            path=f'/v1/students/{student_id}/financial-summary',
            params={'telegram_chat_id': request.telegram_chat_id},
        )
        if status_code != 200 or not isinstance(payload, dict):
            return []
        summary = payload.get('summary')
        if not isinstance(summary, dict):
            return []
        return _build_finance_visual(summary, student_name)

    return []


def _compose_handoff_answer(handoff_payload: dict[str, Any] | None) -> str:
    if not handoff_payload:
        return (
            'Posso seguir com orientacoes publicas por aqui, mas nao consegui registrar o '
            'encaminhamento humano agora. Tente novamente em instantes ou use a secretaria.'
        )

    item = handoff_payload.get('item')
    if not isinstance(item, dict):
        return (
            'Registrei a necessidade de atendimento humano, mas nao consegui recuperar o protocolo. '
            'Use a secretaria para confirmar a fila.'
        )

    queue_name = str(item.get('queue_name', 'atendimento'))
    ticket_code = str(item.get('ticket_code', 'protocolo indisponivel'))
    status = str(item.get('status', 'queued'))
    created = bool(handoff_payload.get('created', False))

    if created:
        return (
            f'Encaminhei sua solicitacao para a fila de {queue_name}. '
            f'Protocolo: {ticket_code}. Status atual: {status}. '
            'A equipe humana podera continuar esse atendimento no portal operacional.'
        )

    return (
        f'Sua solicitacao ja estava registrada na fila de {queue_name}. '
        f'Protocolo: {ticket_code}. Status atual: {status}.'
    )


def _linked_students(actor: dict[str, Any] | None) -> list[dict[str, Any]]:
    if not actor:
        return []
    linked_students = actor.get('linked_students')
    if not isinstance(linked_students, list):
        return []
    return [student for student in linked_students if isinstance(student, dict)]


def _eligible_students(actor: dict[str, Any] | None, *, capability: str) -> list[dict[str, Any]]:
    students = _linked_students(actor)
    if capability == 'academic':
        return [student for student in students if bool(student.get('can_view_academic', False))]
    if capability == 'finance':
        return [student for student in students if bool(student.get('can_view_finance', False))]
    return students


def _select_linked_student(actor: dict[str, Any] | None, message: str) -> tuple[dict[str, Any] | None, str | None]:
    students = _linked_students(actor)
    if not students:
        return None, 'Nao encontrei um aluno vinculado a esta conta para essa consulta.'

    if len(students) == 1:
        return students[0], None

    normalized_message = _normalize_text(message)
    matches: list[dict[str, Any]] = []
    for student in students:
        full_name = str(student.get('full_name', ''))
        enrollment_code = str(student.get('enrollment_code', ''))
        normalized_name = _normalize_text(full_name)
        if normalized_name and normalized_name in normalized_message:
            matches.append(student)
            continue
        if enrollment_code and enrollment_code.lower() in normalized_message:
            matches.append(student)

    unique_matches = {str(item.get('student_id')): item for item in matches}
    if len(unique_matches) == 1:
        return next(iter(unique_matches.values())), None

    options = ', '.join(
        f"{student.get('full_name', 'Aluno')} ({student.get('enrollment_code', 'sem codigo')})"
        for student in students
    )
    return None, f'Sua conta tem mais de um aluno vinculado. Diga qual aluno deseja consultar: {options}.'


def _detect_subject_filter(message: str, summary: dict[str, Any]) -> str | None:
    lowered = _normalize_text(message)
    available_subjects: dict[str, str] = {}

    for key in ('grades', 'attendance'):
        rows = summary.get(key)
        if not isinstance(rows, list):
            continue
        for row in rows:
            if not isinstance(row, dict):
                continue
            subject_name = row.get('subject_name')
            if not isinstance(subject_name, str):
                continue
            normalized_subject = _normalize_text(subject_name)
            available_subjects[normalized_subject] = subject_name

    for normalized_subject in available_subjects:
        if normalized_subject in lowered:
            return normalized_subject
        for hint in SUBJECT_HINTS.get(normalized_subject, set()):
            if hint in lowered:
                return normalized_subject

    return None


def _filter_grade_rows(summary: dict[str, Any], *, subject_filter: str | None, term_filter: str | None) -> list[dict[str, Any]]:
    grades = summary.get('grades')
    if not isinstance(grades, list):
        return []

    filtered: list[dict[str, Any]] = []
    for grade in grades:
        if not isinstance(grade, dict):
            continue
        subject_name = _normalize_text(str(grade.get('subject_name', '')))
        term_code = str(grade.get('term_code', ''))
        if subject_filter and subject_name != subject_filter:
            continue
        if term_filter and not term_code.endswith(term_filter):
            continue
        filtered.append(grade)
    return filtered


def _filter_attendance_rows(summary: dict[str, Any], *, subject_filter: str | None) -> list[dict[str, Any]]:
    attendance = summary.get('attendance')
    if not isinstance(attendance, list):
        return []

    filtered: list[dict[str, Any]] = []
    for row in attendance:
        if not isinstance(row, dict):
            continue
        subject_name = _normalize_text(str(row.get('subject_name', '')))
        if subject_filter and subject_name != subject_filter:
            continue
        filtered.append(row)
    return filtered


def _format_grades(summary: dict[str, Any]) -> list[str]:
    grades = summary.get('grades')
    if not isinstance(grades, list) or not grades:
        return ['- Ainda nao ha lancamentos de notas no periodo consultado.']
    lines = []
    for grade in grades[:4]:
        if not isinstance(grade, dict):
            continue
        lines.append(
            '- {subject_name} - {item_title}: {score}/{max_score}'.format(
                subject_name=grade.get('subject_name', 'Disciplina'),
                item_title=grade.get('item_title', 'Atividade'),
                score=grade.get('score', '?'),
                max_score=grade.get('max_score', '?'),
            )
        )
    return lines or ['- Ainda nao ha lancamentos de notas no periodo consultado.']


def _format_attendance(summary: dict[str, Any]) -> list[str]:
    attendance = summary.get('attendance')
    if not isinstance(attendance, list) or not attendance:
        return ['- Ainda nao ha registros consolidados de frequencia.']
    lines = []
    for row in attendance[:4]:
        if not isinstance(row, dict):
            continue
        lines.append(
            '- {subject_name}: {present} presencas, {late} atrasos, {absent} faltas ({minutes} min)'.format(
                subject_name=row.get('subject_name', 'Disciplina'),
                present=row.get('present_count', 0),
                late=row.get('late_count', 0),
                absent=row.get('absent_count', 0),
                minutes=row.get('absent_minutes', 0),
            )
        )
    return lines or ['- Ainda nao ha registros consolidados de frequencia.']


def _format_invoices(summary: dict[str, Any]) -> list[str]:
    invoices = summary.get('invoices')
    if not isinstance(invoices, list) or not invoices:
        return ['- Nenhuma fatura encontrada para o contrato atual.']
    lines = []
    for invoice in invoices[:4]:
        if not isinstance(invoice, dict):
            continue
        lines.append(
            '- {reference_month}: vencimento {due_date}, status {status}, valor {amount_due}'.format(
                reference_month=invoice.get('reference_month', '---'),
                due_date=invoice.get('due_date', '---'),
                status=invoice.get('status', 'desconhecido'),
                amount_due=invoice.get('amount_due', '0.00'),
            )
        )
    return lines or ['- Nenhuma fatura encontrada para o contrato atual.']


def _filter_invoice_rows(summary: dict[str, Any], *, status_filter: set[str] | None) -> list[dict[str, Any]]:
    invoices = summary.get('invoices')
    if not isinstance(invoices, list):
        return []
    if not status_filter:
        return [invoice for invoice in invoices if isinstance(invoice, dict)]
    filtered: list[dict[str, Any]] = []
    for invoice in invoices:
        if not isinstance(invoice, dict):
            continue
        status = str(invoice.get('status', '')).lower()
        if status in status_filter:
            filtered.append(invoice)
    return filtered


def _detect_finance_status_filter(message: str) -> set[str] | None:
    lowered = _normalize_text(message)
    if any(term in lowered for term in FINANCE_OVERDUE_TERMS):
        return {'overdue'}
    if any(term in lowered for term in FINANCE_PAID_TERMS):
        return {'paid'}
    if any(term in lowered for term in FINANCE_OPEN_TERMS):
        return {'open', 'overdue'}
    return None


def _format_invoice_lines(invoices: list[dict[str, Any]]) -> list[str]:
    if not invoices:
        return ['- Nenhuma fatura compativel com esse filtro foi encontrada.']
    lines = []
    for invoice in invoices[:6]:
        lines.append(
            '- {reference_month}: vencimento {due_date}, status {status}, valor {amount_due}'.format(
                reference_month=invoice.get('reference_month', '---'),
                due_date=invoice.get('due_date', '---'),
                status=invoice.get('status', 'desconhecido'),
                amount_due=invoice.get('amount_due', '0.00'),
            )
        )
    return lines


def _format_assignments(summary: dict[str, Any]) -> list[str]:
    assignments = summary.get('assignments')
    if not isinstance(assignments, list) or not assignments:
        return ['- Nenhuma alocacao docente encontrada.']
    lines = []
    for assignment in assignments[:6]:
        if not isinstance(assignment, dict):
            continue
        lines.append(
            '- {class_name} - {subject_name} ({academic_year})'.format(
                class_name=assignment.get('class_name', 'Turma'),
                subject_name=assignment.get('subject_name', 'Disciplina'),
                academic_year=assignment.get('academic_year', '---'),
            )
        )
    return lines or ['- Nenhuma alocacao docente encontrada.']


def _format_unique_classes(summary: dict[str, Any]) -> list[str]:
    assignments = summary.get('assignments')
    if not isinstance(assignments, list) or not assignments:
        return ['- Nenhuma turma encontrada.']
    seen: set[str] = set()
    lines: list[str] = []
    for assignment in assignments:
        if not isinstance(assignment, dict):
            continue
        class_name = str(assignment.get('class_name', 'Turma'))
        if class_name in seen:
            continue
        seen.add(class_name)
        lines.append(f'- {class_name}')
    return lines or ['- Nenhuma turma encontrada.']


def _format_unique_subjects(summary: dict[str, Any]) -> list[str]:
    assignments = summary.get('assignments')
    if not isinstance(assignments, list) or not assignments:
        return ['- Nenhuma disciplina encontrada.']
    seen: set[str] = set()
    lines: list[str] = []
    for assignment in assignments:
        if not isinstance(assignment, dict):
            continue
        subject_name = str(assignment.get('subject_name', 'Disciplina'))
        if subject_name in seen:
            continue
        seen.add(subject_name)
        lines.append(f'- {subject_name}')
    return lines or ['- Nenhuma disciplina encontrada.']


def _compose_structured_deny(actor: dict[str, Any] | None) -> str:
    if actor is None:
        return (
            'Essa consulta depende de autenticacao e vinculo da sua conta no Telegram. '
            'Use o portal da escola para gerar o codigo de vinculacao e depois envie o comando '
            '`/start link_<codigo>` ao bot.'
        )
    return 'Nao consegui autorizar essa consulta neste contexto. Se precisar, use o portal autenticado da escola.'


async def _compose_structured_tool_answer(
    *,
    settings: Any,
    request: MessageResponseRequest,
    analysis_message: str,
    preview: Any,
    actor: dict[str, Any] | None,
    school_profile: dict[str, Any] | None,
) -> str:
    if preview.classification.domain is QueryDomain.institution:
        profile = school_profile or await _fetch_public_school_profile(settings=settings)
        if profile is None:
            return _compose_public_gap_answer(set())
        return _compose_public_profile_answer(profile, analysis_message)

    if preview.classification.domain is QueryDomain.support:
        if 'schedule_school_visit' in preview.selected_tools:
            workflow_payload = await _create_visit_booking(
                settings=settings,
                request=request,
                actor=actor,
            )
            return _compose_visit_booking_answer(workflow_payload, school_profile)
        workflow_payload = await _create_institutional_request(
            settings=settings,
            request=request,
            actor=actor,
        )
        return _compose_institutional_request_answer(workflow_payload)

    if request.telegram_chat_id is None:
        return _compose_structured_deny(actor)

    actor = actor or await _fetch_actor_context(settings=settings, telegram_chat_id=request.telegram_chat_id)
    if actor is None:
        return _compose_structured_deny(actor)

    role_code = str(actor.get('role_code', 'anonymous'))
    message = request.message
    normalized_message = _normalize_text(message)

    if preview.classification.domain is QueryDomain.academic and role_code == 'teacher':
        if not _contains_any(message, TEACHER_SCHEDULE_TERMS):
            return (
                'No Telegram, o fluxo protegido do professor nesta etapa cobre horario e turmas. '
                'Pergunte por exemplo: "qual meu horario?" ou "quais sao minhas turmas?".'
            )
        payload, status_code = await _api_core_get(
            settings=settings,
            path='/v1/teachers/me/schedule',
            params={'telegram_chat_id': request.telegram_chat_id},
        )
        if status_code != 200 or payload is None:
            return 'Nao consegui consultar sua grade docente agora. Tente novamente em instantes.'
        summary = payload.get('summary', {})
        teacher_name = summary.get('teacher_name', actor.get('full_name', 'Professor'))
        if not isinstance(summary, dict):
            return 'Nao consegui interpretar o retorno da grade docente.'

        if _contains_any(message, TEACHER_CLASS_TERMS) and not _contains_any(message, TEACHER_SUBJECT_TERMS):
            lines = [f'Turmas de {teacher_name}:', *_format_unique_classes(summary)]
            return '\n'.join(lines)

        if _contains_any(message, TEACHER_SUBJECT_TERMS) and not _contains_any(message, TEACHER_CLASS_TERMS):
            lines = [f'Disciplinas de {teacher_name}:', *_format_unique_subjects(summary)]
            return '\n'.join(lines)

        assignments = _format_assignments(summary)
        lines = [f'Grade docente de {teacher_name}:', *assignments]
        if 'horario' in normalized_message or 'agenda' in normalized_message:
            lines.append(
                'Nesta base mockada atual, o detalhamento por bloco de horario ainda nao foi modelado; '
                'por enquanto eu mostro suas alocacoes de turmas e disciplinas.'
            )
        return '\n'.join(lines)

    if preview.classification.domain in {QueryDomain.academic, QueryDomain.finance}:
        if preview.classification.domain is QueryDomain.finance:
            requested_status = _detect_finance_status_filter(message)
            if len(_eligible_students(actor, capability='finance')) > 1:
                student, clarification = _select_linked_student(actor, message)
                if student is None and clarification is not None:
                    summaries: list[dict[str, Any]] = []
                    for candidate in _eligible_students(actor, capability='finance'):
                        candidate_id = candidate.get('student_id')
                        if not isinstance(candidate_id, str):
                            continue
                        payload, status_code = await _api_core_get(
                            settings=settings,
                            path=f'/v1/students/{candidate_id}/financial-summary',
                            params={'telegram_chat_id': request.telegram_chat_id},
                        )
                        if status_code == 200 and isinstance(payload, dict):
                            summary = payload.get('summary')
                            if isinstance(summary, dict):
                                summaries.append(summary)

                    if summaries and not any(
                        _normalize_text(str(student.get('full_name', ''))) in normalized_message
                        for student in _eligible_students(actor, capability='finance')
                    ):
                        lines = ['Panorama financeiro das contas vinculadas:']
                        total_open = 0
                        total_overdue = 0
                        for summary in summaries:
                            open_count = int(summary.get('open_invoice_count', 0) or 0)
                            overdue_count = int(summary.get('overdue_invoice_count', 0) or 0)
                            total_open += open_count
                            total_overdue += overdue_count
                            filtered_invoices = _filter_invoice_rows(summary, status_filter=requested_status)
                            status_line = (
                                f"- {summary.get('student_name', 'Aluno')}: "
                                f"{open_count} em aberto, {overdue_count} vencidas"
                            )
                            lines.append(status_line)
                            for invoice_line in _format_invoice_lines(filtered_invoices)[:2]:
                                lines.append(f'  {invoice_line[2:]}' if invoice_line.startswith('- ') else invoice_line)
                        lines.insert(1, f'- Total de faturas em aberto: {total_open}')
                        lines.insert(2, f'- Total de faturas vencidas: {total_overdue}')
                        if any(term in normalized_message for term in FINANCE_SECOND_COPY_TERMS):
                            lines.append(
                                'A emissao automatica de segunda via ainda entra na proxima etapa; '
                                'por enquanto eu consigo informar a situacao das faturas.'
                            )
                        return '\n'.join(lines)

        student, clarification = _select_linked_student(actor, message)
        if clarification is not None:
            return clarification
        if student is None:
            return 'Nao encontrei um aluno elegivel para essa consulta no Telegram.'

        student_id = student.get('student_id')
        student_name = student.get('full_name', 'Aluno')
        if not isinstance(student_id, str):
            return 'Nao consegui identificar o aluno desta consulta. Tente novamente pelo portal.'

        if preview.classification.domain is QueryDomain.academic:
            payload, status_code = await _api_core_get(
                settings=settings,
                path=f'/v1/students/{student_id}/academic-summary',
                params={'telegram_chat_id': request.telegram_chat_id},
            )
            if status_code == 403:
                return 'Seu perfil nao tem permissao para consultar esses dados academicos.'
            if status_code != 200 or payload is None:
                return 'Nao consegui consultar os dados academicos agora. Tente novamente em instantes.'

            summary = payload.get('summary', {})
            if not isinstance(summary, dict):
                return 'Nao consegui interpretar o retorno academico desta consulta.'

            term_filter = _extract_term_filter(message)
            subject_filter = _detect_subject_filter(message, summary)
            filtered_grades = _filter_grade_rows(summary, subject_filter=subject_filter, term_filter=term_filter)
            filtered_attendance = _filter_attendance_rows(summary, subject_filter=subject_filter)
            filtered_summary = dict(summary)
            filtered_summary['grades'] = filtered_grades
            filtered_summary['attendance'] = filtered_attendance

            focus_attendance = _contains_any(message, ATTENDANCE_TERMS) and not _contains_any(message, GRADE_TERMS)
            lines = [
                f'Resumo academico de {student_name}:',
                f"- Turma: {summary.get('class_name', 'nao informada')}",
                f"- Serie atual: {summary.get('grade_level', 'nao informada')}",
            ]
            if subject_filter:
                lines.append(f"- Disciplina filtrada: {subject_filter.title()}")
            if term_filter:
                lines.append(f'- Bimestre filtrado: {term_filter[-1]}')
            if focus_attendance:
                lines.append('Frequencia:')
                lines.extend(_format_attendance(filtered_summary))
                lines.append('Notas mais recentes:')
                lines.extend(_format_grades(filtered_summary))
            else:
                lines.append('Notas mais recentes:')
                lines.extend(_format_grades(filtered_summary))
                lines.append('Frequencia:')
                lines.extend(_format_attendance(filtered_summary))
            return '\n'.join(lines)

        payload, status_code = await _api_core_get(
            settings=settings,
            path=f'/v1/students/{student_id}/financial-summary',
            params={'telegram_chat_id': request.telegram_chat_id},
        )
        if status_code == 403:
            return 'Seu perfil nao tem permissao para consultar esses dados financeiros.'
        if status_code != 200 or payload is None:
            return 'Nao consegui consultar o resumo financeiro agora. Tente novamente em instantes.'

        summary = payload.get('summary', {})
        if not isinstance(summary, dict):
            return 'Nao consegui interpretar o retorno financeiro desta consulta.'

        requested_status = _detect_finance_status_filter(message)
        filtered_invoices = _filter_invoice_rows(summary, status_filter=requested_status)
        lines = [
            f"Resumo financeiro de {summary.get('student_name', student_name)}:",
            f"- Contrato: {summary.get('contract_code', 'nao informado')}",
            f"- Responsavel financeiro: {summary.get('guardian_name', 'nao informado')}",
            f"- Mensalidade base: {summary.get('monthly_amount', '0.00')}",
            f"- Faturas em aberto: {summary.get('open_invoice_count', 0)}",
            f"- Faturas vencidas: {summary.get('overdue_invoice_count', 0)}",
        ]
        if requested_status == {'paid'}:
            lines.append('Faturas pagas:')
        elif requested_status == {'overdue'}:
            lines.append('Faturas vencidas:')
        elif requested_status == {'open', 'overdue'}:
            lines.append('Faturas em aberto ou vencidas:')
        else:
            lines.append('Ultimas faturas:')
        lines.extend(_format_invoice_lines(filtered_invoices))
        if any(term in normalized_message for term in FINANCE_SECOND_COPY_TERMS):
            lines.append(
                'A emissao automatica de segunda via ainda entra na proxima etapa; '
                'por enquanto eu consigo informar a situacao e os vencimentos.'
            )
        return '\n'.join(lines)

    return (
        'Esse fluxo protegido ainda nao foi concluido para este perfil no Telegram. '
        'Por enquanto, use o portal autenticado da escola.'
    )


def _compose_deterministic_answer(
    *,
    preview: Any,
    retrieval_hits: list[Any],
    citations: list[MessageResponseCitation],
    calendar_events: list[CalendarEventCard],
    query_hints: set[str],
) -> str:
    if preview.mode is OrchestrationMode.deny:
        return (
            'Essa consulta depende de autenticacao e vinculo da sua conta no Telegram. '
            'Use o portal da escola para gerar o codigo de vinculacao e depois envie o comando '
            '`/start link_<codigo>` ao bot.'
        )

    if preview.mode is OrchestrationMode.clarify:
        return (
            f'{DEFAULT_PUBLIC_HELP} Se quiser, pergunte por exemplo: '
            '"quais documentos preciso para a matricula?" ou '
            '"quando acontece a reuniao de pais?".'
        )

    if preview.mode is OrchestrationMode.handoff:
        return (
            'Posso seguir com orientacoes publicas por aqui, mas o handoff humano ainda sera '
            'conectado na proxima etapa. Por enquanto, use a secretaria ou o portal institucional.'
        )

    sections: list[str] = []

    if preview.classification.domain is QueryDomain.calendar and calendar_events:
        sections.append('Encontrei estes proximos eventos publicos no calendario escolar:')
        sections.extend(_format_event_line(event) for event in calendar_events[:3])

    if retrieval_hits:
        intro = 'Segundo a base institucional atual:'
        if preview.classification.domain is QueryDomain.calendar and sections:
            intro = 'Tambem localizei estas referencias na base documental:'
        sections.append(intro)
        sections.extend(f'- {hit.text_excerpt}' for hit in retrieval_hits[:2])

    if not sections:
        return _compose_public_gap_answer(query_hints)

    source_lines = _render_source_lines(citations)
    if source_lines:
        sections.append(source_lines)
    return '\n'.join(sections)


async def generate_message_response(*, request: MessageResponseRequest, settings: Any) -> MessageResponse:
    started_at = monotonic()
    with start_span(
        'eduassist.orchestration.message_response',
        tracer_name='eduassist.ai_orchestrator.runtime',
        **{
            'eduassist.channel': request.channel.value,
            'eduassist.request.message_length': len(request.message),
            'eduassist.request.has_telegram_chat': request.telegram_chat_id is not None,
            'eduassist.orchestration.allow_graph_rag': request.allow_graph_rag,
            'eduassist.orchestration.allow_handoff': request.allow_handoff,
        },
    ):
        actor = await _fetch_actor_context(settings=settings, telegram_chat_id=request.telegram_chat_id)
        effective_user = _user_context_from_actor(actor) if actor else request.user
        effective_conversation_id = _effective_conversation_id(request)
        conversation_context = await _fetch_conversation_context(
            settings=settings,
            conversation_external_id=effective_conversation_id,
            channel=request.channel.value,
        )
        analysis_message = _build_analysis_message(request.message, conversation_context)
        school_profile = await _fetch_public_school_profile(settings=settings)
        set_span_attributes(
            **{
                'eduassist.actor.role': effective_user.role.value,
                'eduassist.actor.authenticated': effective_user.authenticated,
                'eduassist.actor.linked_student_count': len(effective_user.linked_student_ids),
                'eduassist.conversation.has_memory': conversation_context is not None and conversation_context.message_count > 0,
                'eduassist.conversation.message_count': conversation_context.message_count if conversation_context else 0,
                'eduassist.orchestration.analysis_message_expanded': analysis_message != request.message,
            }
        )

        graph = build_orchestration_graph(settings.graph_rag_enabled)
        with start_span('eduassist.orchestration.graph_preview', tracer_name='eduassist.ai_orchestrator.runtime'):
            preview_request = request.model_copy(update={'message': analysis_message})
            state = graph.invoke({'request': _map_request(preview_request, effective_user)})
            preview = to_preview(state)
        set_span_attributes(
            **{
                'eduassist.orchestration.mode': preview.mode.value,
                'eduassist.orchestration.domain': preview.classification.domain.value,
                'eduassist.orchestration.access_tier': preview.classification.access_tier.value,
                'eduassist.orchestration.needs_authentication': preview.needs_authentication,
                'eduassist.orchestration.selected_tools': preview.selected_tools,
                'eduassist.orchestration.graph_path': preview.graph_path,
                'eduassist.orchestration.retrieval_backend': preview.retrieval_backend.value,
            }
        )

        retrieval_hits: list[Any] = []
        citations: list[MessageResponseCitation] = []
        visual_assets: list[MessageResponseVisualAsset] = []
        calendar_events: list[CalendarEventCard] = []
        query_hints: set[str] = set()
        retrieval_supported = True
        public_answerability: PublicAnswerabilityAssessment | None = None
        graph_rag_answer: dict[str, str] | None = None

        if preview.mode is OrchestrationMode.hybrid_retrieval:
            with start_span('eduassist.orchestration.public_retrieval', tracer_name='eduassist.ai_orchestrator.runtime'):
                retrieval_service = get_retrieval_service(
                    database_url=settings.database_url,
                    qdrant_url=settings.qdrant_url,
                    collection_name=settings.qdrant_documents_collection,
                    embedding_model=settings.document_embedding_model,
                )
                search = retrieval_service.hybrid_search(
                    query=analysis_message,
                    top_k=4,
                    visibility='public',
                    category=_category_for_domain(preview.classification.domain),
                )
                retrieval_hits = search.hits
                query_hints = {
                    *_extract_public_entity_hints(request.message),
                    *_extract_public_entity_hints(analysis_message),
                }
                retrieval_supported = _retrieval_hits_cover_query_hints(retrieval_hits, query_hints)
                if retrieval_supported:
                    retrieval_hits = _filter_retrieval_hits_by_query_hints(retrieval_hits, query_hints)
                citations = _collect_citations(retrieval_hits)
                set_span_attributes(
                    **{
                        'eduassist.retrieval.hit_count': len(retrieval_hits),
                        'eduassist.retrieval.citation_count': len(citations),
                        'eduassist.retrieval.query_hint_count': len(query_hints),
                        'eduassist.retrieval.hints_supported': retrieval_supported,
                    }
                )
                if not retrieval_supported:
                    retrieval_hits = []
                    citations = []
                public_answerability = _assess_public_answerability(
                    analysis_message,
                    retrieval_hits,
                    query_hints,
                )
                set_span_attributes(
                    **{
                        'eduassist.retrieval.answerability_coverage_ratio': public_answerability.coverage_ratio,
                        'eduassist.retrieval.answerability_high_risk': public_answerability.high_risk_reasoning,
                        'eduassist.retrieval.answerability_supported_terms': len(public_answerability.matched_terms),
                        'eduassist.retrieval.answerability_unsupported_terms': len(public_answerability.unsupported_terms),
                    }
                )

                if preview.classification.domain is QueryDomain.calendar:
                    calendar_events = await _fetch_public_calendar(settings=settings)
                    set_span_attributes(**{'eduassist.calendar.event_count': len(calendar_events)})
        elif preview.mode is OrchestrationMode.graph_rag:
            with start_span('eduassist.orchestration.graph_rag', tracer_name='eduassist.ai_orchestrator.runtime'):
                set_span_attributes(
                    **{
                        'eduassist.graph_rag.workspace_ready': graph_rag_workspace_ready(settings.graph_rag_workspace),
                    }
                )
                graph_rag_answer = await run_graph_rag_query(
                    settings=settings,
                    query=analysis_message,
                )
                if graph_rag_answer is not None:
                    set_span_attributes(
                        **{
                            'eduassist.graph_rag.method': graph_rag_answer.get('method'),
                            'eduassist.graph_rag.response_length': len(graph_rag_answer.get('text', '')),
                        }
                    )
                else:
                    retrieval_service = get_retrieval_service(
                        database_url=settings.database_url,
                        qdrant_url=settings.qdrant_url,
                        collection_name=settings.qdrant_documents_collection,
                        embedding_model=settings.document_embedding_model,
                    )
                    search = retrieval_service.hybrid_search(
                        query=analysis_message,
                        top_k=4,
                        visibility='public',
                        category=None,
                    )
                    retrieval_hits = search.hits
                    citations = _collect_citations(retrieval_hits)
                    set_span_attributes(
                        **{
                            'eduassist.graph_rag.fallback': True,
                            'eduassist.retrieval.hit_count': len(retrieval_hits),
                            'eduassist.retrieval.citation_count': len(citations),
                        }
                    )

        if preview.mode is OrchestrationMode.structured_tool:
            with start_span('eduassist.orchestration.structured_tool', tracer_name='eduassist.ai_orchestrator.runtime'):
                message_text = await _compose_structured_tool_answer(
                    settings=settings,
                    request=request,
                    analysis_message=analysis_message,
                    preview=preview,
                    actor=actor,
                    school_profile=school_profile,
                )
        elif preview.mode is OrchestrationMode.handoff:
            with start_span('eduassist.orchestration.handoff', tracer_name='eduassist.ai_orchestrator.runtime'):
                handoff_payload = await _create_support_handoff(
                    settings=settings,
                    request=request,
                    actor=actor,
                )
                if isinstance(handoff_payload, dict):
                    item = handoff_payload.get('item')
                    if isinstance(item, dict):
                        set_span_attributes(
                            **{
                                'eduassist.queue.name': item.get('queue_name'),
                                'eduassist.support.status': item.get('status'),
                                'eduassist.support.priority': item.get('priority_code'),
                                'eduassist.support.sla_state': item.get('sla_state'),
                            }
                        )
                message_text = _compose_handoff_answer(handoff_payload)
        elif preview.mode is OrchestrationMode.graph_rag and graph_rag_answer is not None:
            set_span_attributes(
                **{
                    'eduassist.orchestration.used_llm': False,
                    'eduassist.orchestration.graph_rag_live': True,
                }
            )
            message_text = graph_rag_answer['text']
        elif preview.mode is OrchestrationMode.deny:
            set_span_attributes(
                **{
                    'eduassist.orchestration.used_llm': False,
                    'eduassist.orchestration.answer_guardrail': 'deterministic_deny',
                }
            )
            message_text = _compose_deterministic_answer(
                preview=preview,
                retrieval_hits=retrieval_hits,
                citations=[],
                calendar_events=calendar_events,
                query_hints=query_hints,
            )
        else:
            with start_span('eduassist.orchestration.answer_composition', tracer_name='eduassist.ai_orchestrator.runtime'):
                if preview.mode is OrchestrationMode.hybrid_retrieval and not retrieval_supported:
                    set_span_attributes(**{'eduassist.orchestration.used_llm': False})
                    citations = []
                    message_text = _compose_public_gap_answer(query_hints, request.message)
                elif preview.mode is OrchestrationMode.hybrid_retrieval and _is_negative_requirement_query(request.message):
                    set_span_attributes(
                        **{
                            'eduassist.orchestration.used_llm': False,
                            'eduassist.orchestration.answer_guardrail': 'negative_requirement_abstention',
                        }
                    )
                    message_text = _compose_negative_requirement_answer()
                elif preview.mode is OrchestrationMode.hybrid_retrieval and _is_comparative_query(request.message):
                    set_span_attributes(
                        **{
                            'eduassist.orchestration.used_llm': False,
                            'eduassist.orchestration.answer_guardrail': 'comparative_abstention',
                        }
                    )
                    citations = []
                    message_text = _compose_comparative_gap_answer()
                elif (
                    preview.mode is OrchestrationMode.hybrid_retrieval
                    and public_answerability is not None
                    and not public_answerability.enough_support
                ):
                    set_span_attributes(
                        **{
                            'eduassist.orchestration.used_llm': False,
                            'eduassist.orchestration.answer_guardrail': 'answerability_abstention',
                        }
                    )
                    if not public_answerability.high_risk_reasoning:
                        citations = []
                    message_text = _compose_answerability_gap_answer(public_answerability, request.message)
                elif preview.mode is OrchestrationMode.clarify and _is_prompt_disclosure_probe(request.message):
                    set_span_attributes(
                        **{
                            'eduassist.orchestration.used_llm': False,
                            'eduassist.orchestration.safe_clarify_guardrail': True,
                        }
                    )
                    message_text = (
                        f'{DEFAULT_PUBLIC_HELP} '
                        'Nao posso ajudar com detalhes internos de configuracao do sistema.'
                    )
                else:
                    llm_text = await compose_with_provider(
                        settings=settings,
                        request_message=request.message,
                        analysis_message=analysis_message,
                        preview=preview,
                        citations=citations,
                        calendar_events=calendar_events,
                        conversation_context=(
                            {
                                'conversation_external_id': conversation_context.conversation_external_id,
                                'message_count': conversation_context.message_count,
                                'recent_messages': conversation_context.recent_messages,
                            }
                            if conversation_context
                            else None
                        ),
                        school_profile=school_profile,
                    )
                    set_span_attributes(
                        **{
                            'eduassist.orchestration.used_llm': bool(llm_text),
                            'eduassist.orchestration.llm_provider': settings.llm_provider,
                        }
                    )
                    message_text = llm_text or _compose_deterministic_answer(
                        preview=preview,
                        retrieval_hits=retrieval_hits,
                        citations=citations,
                        calendar_events=calendar_events,
                        query_hints=query_hints,
                    )

        if citations:
            sources = _render_source_lines(citations)
            if sources and sources not in message_text:
                message_text = f'{message_text}\n\n{sources}'

        visual_assets = await _maybe_build_visual_assets(
            settings=settings,
            request=request,
            preview=preview,
            actor=actor,
            school_profile=school_profile,
        )

        await _persist_conversation_turn(
            settings=settings,
            conversation_external_id=effective_conversation_id,
            channel=request.channel.value,
            actor=actor,
            user_message=request.message,
            assistant_message=message_text,
        )

        set_span_attributes(
            **{
                'eduassist.response.length': len(message_text),
                'eduassist.response.visual_asset_count': len(visual_assets),
            }
        )
        metric_attributes = {
            'mode': preview.mode.value,
            'domain': preview.classification.domain.value,
            'channel': request.channel.value,
            'authenticated': effective_user.authenticated,
            'retrieval_backend': preview.retrieval_backend.value,
        }
        record_counter(
            'eduassist_orchestration_responses',
            attributes=metric_attributes,
            description='Responses emitted by the AI orchestrator.',
        )
        record_histogram(
            'eduassist_orchestration_latency_ms',
            (monotonic() - started_at) * 1000,
            attributes=metric_attributes,
            description='End-to-end orchestration latency in milliseconds.',
        )
        record_histogram(
            'eduassist_orchestration_response_length',
            len(message_text),
            attributes=metric_attributes,
            description='Length of final responses emitted by the AI orchestrator.',
        )
        return MessageResponse(
            message_text=message_text,
            mode=preview.mode,
            classification=preview.classification,
            retrieval_backend=preview.retrieval_backend,
            selected_tools=preview.selected_tools,
            citations=citations,
            visual_assets=visual_assets,
            calendar_events=calendar_events,
            needs_authentication=preview.needs_authentication,
            graph_path=preview.graph_path,
            risk_flags=preview.risk_flags,
            reason=preview.reason,
        )
