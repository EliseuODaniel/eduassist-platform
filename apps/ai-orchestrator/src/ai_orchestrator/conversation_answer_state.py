from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from typing import Any

from eduassist_semantic_ingress import looks_like_language_preference_feedback

from .public_known_unknowns import detect_public_known_unknown_key

_FINANCE_TERMS = {
    'fatura',
    'faturas',
    'boleto',
    'boletos',
    'mensalidade',
    'mensalidades',
    'financeiro',
    'pagamento',
    'pagamentos',
    'vencimento',
    'vencimentos',
    'valor',
    'debito',
    'débito',
}
_PUBLIC_PRICING_TERMS = {
    'mensalidade',
    'mensalidades',
    'matricula',
    'matrícula',
    'taxa de matricula',
    'taxa de matrícula',
    'preco',
    'preço',
    'quanto fica',
    'quanto seria',
}
_PUBLIC_PRICING_PRIVATE_HINTS = {
    'meu filho',
    'minha filha',
    'meus filhos',
    'minhas filhas',
    'minha fatura',
    'meu boleto',
    'em aberto',
    'vencimento',
    'vencida',
    'vencido',
    'pago',
    'quitado',
}
_PUBLIC_SEGMENT_HINTS = {
    'ensino medio': 'Ensino Medio',
    'ensino médio': 'Ensino Medio',
    'fundamental ii': 'Ensino Fundamental II',
    'fundamental 2': 'Ensino Fundamental II',
    'periodo integral': 'Periodo integral opcional',
    'período integral': 'Periodo integral opcional',
    'contraturno': 'Periodo integral opcional',
}
_ACADEMIC_GRADE_TERMS = {
    'nota',
    'notas',
    'media',
    'média',
    'boletim',
    'aprovado',
    'aprovacao',
    'aprovação',
    'tirar',
}
_ACADEMIC_UPCOMING_TERMS = {
    'prova',
    'provas',
    'avaliacao',
    'avaliação',
    'avaliacoes',
    'avaliações',
    'entrega',
    'entregas',
}
_ACADEMIC_ATTENDANCE_TERMS = {
    'frequencia',
    'frequência',
    'falta',
    'faltas',
    'presenca',
    'presença',
    'atraso',
    'atrasos',
    'ausencia',
    'ausência',
}
_ADMIN_TERMS = {
    'cadastro',
    'cadastral',
    'documentacao',
    'documentação',
    'documentos',
    'secretaria',
    'comprovante',
    'administrativo',
    'administrativa',
    'pendencia',
    'pendência',
}
_JUSTIFICATION_TERMS = {
    'atestado',
    'justificar',
    'justificativa',
}
_JUSTIFICATION_DECISION_TERMS = {
    'serve',
    'aceita',
    'aceito',
    'pode',
}
_JUSTIFICATION_DOCUMENT_HINTS = {
    'atestado',
    'laudo',
    'declaracao',
    'declaração',
    'documento',
    'documentos',
    'falta',
    'faltas',
    'ausencia',
    'ausência',
    'secretaria',
    'justificar',
    'justificativa',
}
_YES_NO_TERMS = {
    'serve',
    'pode',
    'pode?',
    'tem problema',
    'isso tem problema',
    'aceita',
    'aceito',
    'funciona',
}
_STUDENT_PRONOUN_TERMS = {
    'ele',
    'dele',
    'do dele',
    'dela',
    'ela',
    'nele',
    'nela',
}
_SUBJECT_ALIASES = {
    'fisica': 'Fisica',
    'física': 'Fisica',
    'matematica': 'Matematica',
    'matemática': 'Matematica',
    'portugues': 'Lingua Portuguesa',
    'português': 'Lingua Portuguesa',
    'quimica': 'Quimica',
    'química': 'Quimica',
    'biologia': 'Biologia',
    'historia': 'Historia',
    'história': 'Historia',
    'geografia': 'Geografia',
    'ingles': 'Lingua Inglesa',
    'english': 'Lingua Inglesa',
    'inglês': 'Lingua Inglesa',
    'lingua inglesa': 'Lingua Inglesa',
    'educacao fisica': 'Educacao Fisica',
    'educação física': 'Educacao Fisica',
    'redacao': 'Redacao',
    'redação': 'Redacao',
    'filosofia': 'Filosofia',
    'sociologia': 'Sociologia',
    'tecnologia': 'Tecnologia e Cultura Digital',
    'projeto de vida': 'Projeto de vida',
}
_REPAIR_HINTS = {
    'por que',
    'porque',
    'essa resposta',
    'resposta aqui',
    'era sobre o que',
    'mas voce falou',
    'mas você falou',
    'nao e',
    'não é',
    'nao quero',
    'não quero',
}
_QUESTION_WORDS = {
    'como',
    'serve',
    'qual',
    'quais',
    'quanto',
    'quantas',
    'quantos',
    'que',
    'se',
    'esta',
    'está',
    'tem',
    'fica',
    'ficou',
    'agora',
    'entao',
    'então',
    'antes',
    'depois',
}
_PUBLIC_NON_PRICING_CONTEXT_TERMS = {
    'calendario',
    'calendário',
    'agenda',
    'avaliacao',
    'avaliação',
    'avaliacoes',
    'avaliações',
    'aulas',
    'reuniao',
    'reunião',
    'responsaveis',
    'responsáveis',
    'primeiro bimestre',
    'bimestre',
    'rotina',
    'vida escolar',
}
_FAMILY_REFERENCE_TERMS = {
    'meus filhos',
    'minha familia',
    'minha família',
    'da familia',
    'da família',
    'contas vinculadas',
    'familia',
    'família',
    'dos meus filhos',
    'ambos',
    'todos',
}
_FAMILY_ACADEMIC_AGGREGATE_TERMS = {
    'panorama academico',
    'panorama acadêmico',
    'quadro academico',
    'quadro acadêmico',
    'mais perto da media minima',
    'mais perto da média mínima',
    'limite de aprovacao',
    'limite de aprovação',
    'corte de aprovacao',
    'corte de aprovação',
    'academicamente pior',
    'mais critico academicamente',
    'mais crítico academicamente',
    'qual dos meus filhos esta academicamente pior',
    'qual dos meus filhos está academicamente pior',
    'qual dos meus filhos esta pior',
    'qual dos meus filhos está pior',
}
_FAMILY_FINANCE_AGGREGATE_TERMS = {
    'situacao financeira atual da familia',
    'situação financeira atual da família',
    'resumo financeiro da familia',
    'resumo financeiro da família',
    'vencimentos, atrasos e proximos passos',
    'vencimentos, atrasos e próximos passos',
    'minha situacao financeira',
    'minha situação financeira',
    'situacao financeira como se eu fosse leigo',
    'situação financeira como se eu fosse leigo',
    'separando mensalidade, taxa, atraso e desconto',
    'separando mensalidade taxa atraso e desconto',
}
_NON_ENTITY_FILLER_TERMS = {
    'forma',
    'bem',
    'objetiva',
    'objetivo',
    'objetivamente',
    'resumo',
    'resumidamente',
    'mostre',
    'mostrar',
    'direta',
    'direto',
    'corte',
    'aprovacao',
    'aprovação',
    'cada',
    'filho',
    'filhos',
    'negociar',
    'mensalidade',
    'taxa',
    'desconto',
    'descontos',
    'situacao',
    'situação',
    'financeira',
    'atendimento',
}
_FOCUS_MARKERS = (
    'so ',
    'só ',
    'apenas ',
    'somente ',
    'so a ',
    'só a ',
    'so o ',
    'só o ',
    'olhe so para ',
    'olhe só para ',
    'agora foque so na ',
    'agora foque só na ',
    'foque so na ',
    'foque só na ',
    'fique apenas com ',
    'fique só com ',
    'recorte so ',
    'recorte só ',
    'isole a ',
    'isole o ',
    'corta so para ',
    'corta só para ',
    'corta so para a ',
    'corta só para a ',
    'corta so para o ',
    'corta só para o ',
    'filtre apenas ',
    'agora quero apenas ',
    'agora quero so ',
    'agora quero só ',
)
_GENERIC_SUBJECT_REFERENCE_STUBS = {
    'qual disciplina',
    'que disciplina',
    'quais disciplinas',
    'que disciplinas',
    'qual componente',
    'que componente',
    'qual materia',
    'qual matéria',
    'quais materias',
    'quais matérias',
    'que materia',
    'que matéria',
    'qual componente dela',
    'qual componente dele',
    'qual disciplina dela',
    'qual disciplina dele',
}


@dataclass(frozen=True)
class AnswerFocusState:
    domain: str | None = None
    topic: str | None = None
    student_name: str | None = None
    student_id: str | None = None
    subject_name: str | None = None
    academic_attribute: str | None = None
    finance_attribute: str | None = None
    finance_status_filter: str | None = None
    public_pricing_segment: str | None = None
    public_pricing_grade_year: str | None = None
    public_pricing_quantity: str | None = None
    public_pricing_price_kind: str | None = None
    active_task: str | None = None
    unknown_student_name: str | None = None
    unknown_subject_name: str | None = None
    asks_yes_no: bool = False
    uses_memory: bool = False
    asks_comparison: bool = False
    asks_single_focus: bool = False
    asks_family_aggregate: bool = False
    is_repair_followup: bool = False
    needs_disambiguation: bool = False


def normalize_text(value: str | None) -> str:
    normalized = unicodedata.normalize('NFKD', str(value or ''))
    without_accents = ''.join(char for char in normalized if not unicodedata.combining(char))
    return ' '.join(without_accents.replace('º', 'o').replace('ª', 'a').lower().split())


def recent_trace_slot_memory(conversation_context: dict[str, Any] | None) -> dict[str, Any] | None:
    if not isinstance(conversation_context, dict):
        return None
    recent_tool_calls = conversation_context.get('recent_tool_calls')
    if not isinstance(recent_tool_calls, list):
        return None
    for item in reversed(recent_tool_calls):
        if not isinstance(item, dict):
            continue
        if str(item.get('tool_name', '')).strip() != 'orchestration.trace':
            continue
        payload = item.get('request_payload')
        if not isinstance(payload, dict):
            continue
        slot_memory = payload.get('slot_memory')
        if isinstance(slot_memory, dict) and slot_memory:
            return slot_memory
    return None


def _recent_slot_value_for_task(
    conversation_context: dict[str, Any] | None,
    *,
    key: str,
    active_task: str,
) -> str | None:
    if not isinstance(conversation_context, dict):
        return None
    recent_tool_calls = conversation_context.get('recent_tool_calls')
    if not isinstance(recent_tool_calls, list):
        return None
    for item in reversed(recent_tool_calls):
        if not isinstance(item, dict):
            continue
        if str(item.get('tool_name', '')).strip() != 'orchestration.trace':
            continue
        payload = item.get('request_payload')
        if not isinstance(payload, dict):
            continue
        slot_memory = payload.get('slot_memory')
        if not isinstance(slot_memory, dict):
            continue
        if str(slot_memory.get('active_task') or '').strip() != active_task:
            continue
        value = str(slot_memory.get(key) or '').strip()
        if value:
            return value
    return None


def _contains_any(message: str, options: set[str]) -> bool:
    normalized = normalize_text(message)
    for term in {normalize_text(term) for term in options}:
        escaped = re.escape(term).replace(r'\ ', r'\s+')
        if re.search(rf'(?<!\w){escaped}(?!\w)', normalized):
            return True
    return False


def _extract_public_pricing_grade_year(message: str) -> str | None:
    normalized = normalize_text(message)
    match = re.search(r'\b(1o|2o|3o|6o|7o|8o|9o)\b', normalized)
    if match:
        return f'{match.group(1)} ano'
    return None


def _detect_public_pricing_price_kind(message: str) -> str | None:
    normalized = normalize_text(message)
    if any(term in normalized for term in ('mensalidade', 'mensalidades')):
        return 'monthly_amount'
    if any(term in normalized for term in ('matricula', 'matrícula', 'taxa de matricula', 'taxa de matrícula')):
        return 'enrollment_fee'
    return None


def _extract_public_pricing_quantity(message: str) -> str | None:
    normalized = normalize_text(message)
    contextual_match = re.search(
        r'(?:\bpara\s+)?\b(\d+)\b\s+(?:filho|filhos|aluno|alunos)\b',
        normalized,
    )
    if contextual_match:
        value = int(contextual_match.group(1))
        return str(value) if value > 0 else None
    bare_quantity_match = re.fullmatch(r'\b(\d+)\b', normalized)
    if bare_quantity_match:
        value = int(bare_quantity_match.group(1))
        return str(value) if 0 < value < 1000 else None
    return None


def _extract_public_pricing_segment(message: str) -> str | None:
    normalized = normalize_text(message)
    for hint, segment in _PUBLIC_SEGMENT_HINTS.items():
        if normalize_text(hint) in normalized:
            return segment
    grade_year = _extract_public_pricing_grade_year(message)
    if grade_year in {'1o ano', '2o ano', '3o ano'}:
        return 'Ensino Medio'
    if grade_year in {'6o ano', '7o ano', '8o ano', '9o ano'}:
        return 'Ensino Fundamental II'
    return None


def _looks_like_public_pricing_query(message: str) -> bool:
    normalized = normalize_text(message)
    explicit_price_intent = any(
        term in normalized
        for term in (
            'mensalidade',
            'preco',
            'preço',
            'taxa de matricula',
            'taxa de matrícula',
            'quanto fica',
            'quanto seria',
            'valor',
        )
    )
    if (
        re.search(r'\b(\d+)\b\s+(?:filho|filhos|aluno|alunos)\b', normalized)
        and any(term in normalized for term in ('matricular', 'inscrever', 'colocar'))
    ):
        return True
    if not explicit_price_intent and any(term in normalized for term in {normalize_text(item) for item in _PUBLIC_NON_PRICING_CONTEXT_TERMS}):
        return False
    if not any(term in normalized for term in {normalize_text(item) for item in _PUBLIC_PRICING_TERMS}):
        return False
    if any(term in normalized for term in {'fatura', 'faturas', 'boleto', 'boletos', 'pagamento', 'pagamentos', 'em aberto', 'vencimento', 'vencida', 'vencido'}):
        return False
    return not any(term in normalized for term in {normalize_text(item) for item in _PUBLIC_PRICING_PRIVATE_HINTS})


def _looks_like_family_finance_aggregate_query(message: str) -> bool:
    normalized = normalize_text(message)
    family_reference = any(term in normalized for term in {normalize_text(item) for item in _FAMILY_REFERENCE_TERMS}) or bool(
        re.search(r'\b(?:meus?|minhas?)\s+(?:\w+\s+){0,2}filh(?:o|os|a|as)\b', normalized)
        or re.search(r'\bdos?\s+meus?\s+(?:\w+\s+){0,2}filh(?:o|os|a|as)\b', normalized)
    )
    if any(term in normalized for term in {normalize_text(item) for item in _FAMILY_FINANCE_AGGREGATE_TERMS}):
        return True
    return family_reference and any(
        term in normalized
        for term in ('financeiro', 'fatura', 'faturas', 'vencimentos', 'atrasos', 'proximos passos', 'próximos passos')
    )


def _looks_like_family_academic_aggregate_query(message: str) -> bool:
    normalized = normalize_text(message)
    family_reference = any(term in normalized for term in {normalize_text(item) for item in _FAMILY_REFERENCE_TERMS}) or bool(
        re.search(r'\b(?:meus?|minhas?)\s+(?:\w+\s+){0,2}filh(?:o|os|a|as)\b', normalized)
        or re.search(r'\bdos?\s+meus?\s+(?:\w+\s+){0,2}filh(?:o|os|a|as)\b', normalized)
    )
    if any(term in normalized for term in {normalize_text(item) for item in _FAMILY_ACADEMIC_AGGREGATE_TERMS}):
        return True
    return family_reference and any(
        term in normalized
        for term in (
            'panorama academico',
            'panorama acadêmico',
            'quadro academico',
            'quadro acadêmico',
            'mais perto da media minima',
            'mais perto da média mínima',
            'limite de aprovacao',
            'limite de aprovação',
            'corte de aprovacao',
            'corte de aprovação',
            'proximas avaliacoes',
            'próximas avaliações',
            'proximas provas',
            'próximas provas',
            'avaliacoes',
            'avaliações',
        )
    )


def _looks_like_family_admin_aggregate_query(message: str) -> bool:
    normalized = normalize_text(message)
    explicit_terms = {
        'documentacao dos meus filhos',
        'documentação dos meus filhos',
        'compare a documentacao dos meus filhos',
        'compare a documentação dos meus filhos',
        'compare a documentacao dos meus filhos e diga qual deles ainda tem pendencia',
        'compare a documentação dos meus filhos e diga qual deles ainda tem pendência',
        'quadro documental dos meus filhos',
        'quadro documental da familia',
        'quadro documental da família',
        'pendencia documental dos meus filhos',
        'pendência documental dos meus filhos',
        'pendencias documentais dos meus filhos',
        'pendências documentais dos meus filhos',
    }
    if any(term in normalized for term in explicit_terms):
        return True
    family_reference = any(term in normalized for term in {normalize_text(item) for item in _FAMILY_REFERENCE_TERMS}) or bool(
        re.search(r'\b(?:meus?|minhas?)\s+(?:\w+\s+){0,2}filh(?:o|os|a|as)\b', normalized)
        or re.search(r'\bdos?\s+meus?\s+(?:\w+\s+){0,2}filh(?:o|os|a|as)\b', normalized)
    )
    return family_reference and any(
        term in normalized
        for term in (
            'documentacao',
            'documentação',
            'documental',
            'documentais',
            'cadastro',
            'pendencia',
            'pendência',
            'pendencias',
            'pendências',
            'comprovante',
            'comprovantes',
            'administrativo',
            'administrativa',
        )
    )


def _looks_like_public_pricing_followup(message: str, *, slot_memory: dict[str, Any] | None) -> bool:
    normalized = normalize_text(message)
    if not normalized:
        return False
    has_public_pricing_context = isinstance(slot_memory, dict) and (
        str(slot_memory.get('active_task') or '').strip() == 'public:pricing'
        or any(
            str(slot_memory.get(key) or '').strip()
            for key in (
                'public_pricing_segment',
                'public_pricing_grade_year',
                'public_pricing_quantity',
                'public_pricing_price_kind',
            )
        )
    )
    if not has_public_pricing_context:
        return False
    return _looks_like_followup(message) or (
        len(normalized) <= 32 and (
            _extract_public_pricing_segment(message) is not None
            or _extract_public_pricing_grade_year(message) is not None
            or _extract_public_pricing_quantity(message) is not None
            or _detect_public_pricing_price_kind(message) is not None
        )
    )


def _linked_students(actor: dict[str, Any] | None) -> list[dict[str, Any]]:
    linked_students = actor.get('linked_students') if isinstance(actor, dict) else None
    if not isinstance(linked_students, list):
        return []
    return [student for student in linked_students if isinstance(student, dict)]


def _find_explicit_student(actor: dict[str, Any] | None, message: str) -> dict[str, Any] | None:
    normalized_message = normalize_text(message)
    for student in _linked_students(actor):
        full_name = str(student.get('full_name') or '').strip()
        normalized_full = normalize_text(full_name)
        if normalized_full and normalized_full in normalized_message:
            return student
        first_name = normalized_full.split(' ')[0] if normalized_full else ''
        if first_name and re.search(rf'\b{re.escape(first_name)}\b', normalized_message):
            return student
    return None


def _find_focus_marked_student(actor: dict[str, Any] | None, message: str) -> dict[str, Any] | None:
    normalized_message = normalize_text(message)
    for student in _linked_students(actor):
        full_name = str(student.get('full_name') or '').strip()
        normalized_full = normalize_text(full_name)
        first_name = normalized_full.split(' ')[0] if normalized_full else ''
        candidate_forms = tuple(value for value in {normalized_full, first_name} if value)
        if not candidate_forms:
            continue
        for candidate in candidate_forms:
            for marker in _FOCUS_MARKERS:
                marker_pattern = re.escape(normalize_text(marker).strip()).replace(r'\ ', r'\s+')
                if re.search(rf'{marker_pattern}\s+{re.escape(candidate)}\b', normalized_message):
                    return student
            if re.search(rf'\b(?:so|só|apenas|somente)\s+(?:a|o)\s+{re.escape(candidate)}\b', normalized_message):
                return student
    return None


def _count_explicit_linked_students(actor: dict[str, Any] | None, message: str) -> int:
    normalized_message = normalize_text(message)
    if not normalized_message:
        return 0
    count = 0
    for student in _linked_students(actor):
        full_name = str(student.get('full_name') or '').strip()
        normalized_full = normalize_text(full_name)
        if normalized_full and normalized_full in normalized_message:
            count += 1
            continue
        first_name = normalized_full.split(' ')[0] if normalized_full else ''
        if first_name and re.search(rf'\b{re.escape(first_name)}\b', normalized_message):
            count += 1
    return count


def _extract_unknown_student_reference(actor: dict[str, Any] | None, message: str) -> str | None:
    normalized_message = normalize_text(message)
    if not normalized_message:
        return None
    if not _linked_students(actor):
        return None
    if (
        _looks_like_family_finance_aggregate_query(message)
        or _looks_like_family_academic_aggregate_query(message)
        or _looks_like_family_admin_aggregate_query(message)
        or _looks_like_public_pricing_query(message)
        or ('escopo' in normalized_message and any(term in normalized_message for term in {'filho', 'filhos', 'academico', 'acadêmico', 'financeiro'}))
    ):
        return None
    if not re.search(
        r'\b(?:nota|notas|prova|provas|avaliac\w*|frequ\w*|fatura|faturas|boleto|boletos|financeir\w*)\b',
        normalized_message,
    ):
        return None
    if re.search(r'\b(?:notas?|provas?|avaliacoes?|avaliações|aulas?)\s+de\b', normalized_message):
        return None
    known_names = {normalize_text(student.get('full_name')) for student in _linked_students(actor)}
    known_first_names = {name.split(' ')[0] for name in known_names if name}
    stopwords = {normalize_text(item) for item in _QUESTION_WORDS | _FINANCE_TERMS | _ACADEMIC_GRADE_TERMS | _ACADEMIC_UPCOMING_TERMS | _ACADEMIC_ATTENDANCE_TERMS | _ADMIN_TERMS}
    stopwords.update(normalize_text(alias) for alias in _SUBJECT_ALIASES)
    stopwords.update(_NON_ENTITY_FILLER_TERMS)
    stopwords.update(
        {
            'professor',
            'professora',
            'docente',
            'manual',
            'interno',
            'material interno',
            'comunicacao pedagogica',
            'comunicação pedagógica',
            'registro de avaliacoes',
            'registro de avaliações',
            'reprovar',
            'comparacao anterior',
            'comparação anterior',
            'veredito academico',
            'veredito acadêmico',
        }
    )
    for pattern in (
        r'\b(?:da|do|de|para|pro|pra)\s+([a-z]{3,}(?:\s+[a-z]{3,})?)\b',
        r'\b(?:aluno|aluna|estudante)\s+([a-z]{3,}(?:\s+[a-z]{3,})?)\b',
    ):
        for match in re.finditer(pattern, normalized_message):
            candidate = normalize_text(match.group(1))
            if not candidate or candidate in known_names or candidate in known_first_names:
                continue
            if candidate in {'cada filho', 'cada um', 'meus filhos', 'dos meus filhos', 'negociar uma', 'situacao financeira', 'situação financeira'}:
                continue
            if candidate in stopwords or any(candidate.startswith(f'{term} ') for term in stopwords):
                continue
            return candidate.title()
    return None


def _find_student_by_name(actor: dict[str, Any] | None, student_name: str | None) -> dict[str, Any] | None:
    normalized_name = normalize_text(student_name)
    if not normalized_name:
        return None
    for student in _linked_students(actor):
        full_name = normalize_text(student.get('full_name'))
        if normalized_name == full_name or normalized_name in full_name:
            return student
        first_name = full_name.split(' ')[0] if full_name else ''
        if normalized_name == first_name:
            return student
    return None


def _recent_subject_from_messages(conversation_context: dict[str, Any] | None) -> str | None:
    if not isinstance(conversation_context, dict):
        return None
    recent_messages = conversation_context.get('recent_messages')
    if not isinstance(recent_messages, list):
        return None
    for item in reversed(recent_messages):
        if not isinstance(item, dict):
            continue
        content = str(item.get('content') or '')
        subject = explicit_subject_from_message(content)
        if subject:
            return subject
    return None


def _recent_assistant_mentions_upcoming(conversation_context: dict[str, Any] | None) -> bool:
    if not isinstance(conversation_context, dict):
        return False
    recent_messages = conversation_context.get('recent_messages')
    if not isinstance(recent_messages, list):
        return False
    for item in reversed(recent_messages):
        if not isinstance(item, dict):
            continue
        if str(item.get('sender_type') or '').strip().lower() != 'assistant':
            continue
        content = normalize_text(item.get('content'))
        if any(term in content for term in ('proximas avaliacoes', 'proximas provas', 'avaliacao futura', 'avaliacoes futuras')):
            return True
    return False


def _recent_public_pricing_value_from_messages(
    conversation_context: dict[str, Any] | None,
    *,
    extractor: Any,
) -> str | None:
    if not isinstance(conversation_context, dict):
        return None
    recent_messages = conversation_context.get('recent_messages')
    if not isinstance(recent_messages, list):
        return None
    for item in reversed(recent_messages):
        if not isinstance(item, dict):
            continue
        if str(item.get('sender_type') or '').strip().lower() != 'user':
            continue
        content = str(item.get('content') or '')
        value = extractor(content)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return None


def explicit_subject_from_message(message: str | None) -> str | None:
    if looks_like_language_preference_feedback(message):
        return None
    normalized = normalize_text(message)
    for alias, canonical in sorted(_SUBJECT_ALIASES.items(), key=lambda item: len(item[0]), reverse=True):
        normalized_alias = normalize_text(alias)
        if normalized_alias in normalized:
            if re.search(rf'\b(?:nao e|não é|nao eh|não eh)\s+{re.escape(normalized_alias)}\b', normalized):
                continue
            return canonical
    return None


def _extract_unknown_subject_reference(message: str | None, actor: dict[str, Any] | None) -> str | None:
    normalized = normalize_text(message)
    if not normalized:
        return None
    if explicit_subject_from_message(message):
        return None
    if not any(term in normalized for term in ('nota', 'notas', 'prova', 'provas', 'avaliac', 'entrega', 'disciplin', 'materia', 'matéria', 'aulas de')):
        return None
    known_student_names = {normalize_text(student.get('full_name')) for student in _linked_students(actor)}
    known_student_first_names = {name.split(' ')[0] for name in known_student_names if name}
    stopwords = {normalize_text(item) for item in _QUESTION_WORDS | _FINANCE_TERMS | _ACADEMIC_GRADE_TERMS | _ACADEMIC_UPCOMING_TERMS | _ACADEMIC_ATTENDANCE_TERMS}
    stopwords.update(normalize_text(alias) for alias in _SUBJECT_ALIASES)
    stopwords.update(_NON_ENTITY_FILLER_TERMS)
    patterns = (
        r'\baulas?\s+de\s+([a-z]{3,}(?:\s+[a-z]{3,})?)\b',
        r'\b(?:notas?|provas?|avaliacoes?|avaliações|entregas?)\s+de\s+([a-z]{3,}(?:\s+[a-z]{3,})?)\b',
        r'\bem\s+([a-z]{3,}(?:\s+[a-z]{3,})?)\b',
    )
    for pattern in patterns:
        match = re.search(pattern, normalized)
        if not match:
            continue
        candidate = normalize_text(match.group(1))
        if candidate in _GENERIC_SUBJECT_REFERENCE_STUBS:
            continue
        if not candidate or candidate in stopwords or candidate in known_student_names or candidate in known_student_first_names:
            continue
        return candidate.title()
    return None


def _recent_memory_subject(slot_memory: dict[str, Any] | None) -> str | None:
    if not isinstance(slot_memory, dict):
        return None
    subject = str(slot_memory.get('active_subject') or '').strip()
    return subject or None


def _looks_like_followup(message: str) -> bool:
    normalized = normalize_text(message)
    if len(normalized) > 180:
        return False
    return (
        any(normalized.startswith(prefix) for prefix in ('e ', 'mas ', 'entao ', 'então ', 'e o ', 'e a '))
        or any(token in normalized.split() for token in {'isso', 'essa', 'esse', 'aquilo'})
        or any(term in normalized.split() for term in _STUDENT_PRONOUN_TERMS)
    )


def _looks_like_repair_followup(message: str) -> bool:
    normalized = normalize_text(message)
    for hint in {normalize_text(item) for item in _REPAIR_HINTS}:
        escaped = re.escape(hint).replace(r'\ ', r'\s+')
        if re.search(rf'(?<!\w){escaped}(?!\w)', normalized):
            return True
    return False


def _looks_like_student_correction_followup(message: str) -> bool:
    normalized = normalize_text(message)
    if not normalized or len(normalized) > 48:
        return False
    return bool(
        re.match(r'^(?:nao|não)(?:\s+e|\s+eh)?(?:,\s*|\s+)(?:do|da)\s+[a-z]{3,}(?:\s+[a-z]{3,})?(?:\??)?$', normalized)
        or re.match(r'^(?:do|da)\s+[a-z]{3,}(?:\s+[a-z]{3,})?(?:\??)?$', normalized)
    )


def _looks_like_attendance_justification_query(message: str, *, slot_memory: dict[str, Any] | None) -> bool:
    normalized = normalize_text(message)
    if not normalized:
        return False
    if (
        any(term in normalized for term in {'nao quero justificar', 'não quero justificar', 'nao quero justificativa', 'não quero justificativa'})
        and any(term in normalized for term in {'nota', 'notas', 'media', 'média', 'boletim'})
    ):
        return False
    if any(term in normalized for term in {normalize_text(item) for item in _JUSTIFICATION_TERMS}):
        return True
    if not any(term in normalized for term in {normalize_text(item) for item in _JUSTIFICATION_DECISION_TERMS}):
        return False
    if any(term in normalized for term in {normalize_text(item) for item in _JUSTIFICATION_DOCUMENT_HINTS}):
        return True
    active_task = str((slot_memory or {}).get('active_task') or '').strip()
    return bool(active_task.startswith('academic:attendance') and any(term in normalized for term in {'isso', 'esse', 'essa', 'ele', 'ela', 'dele', 'dela'}))


def _looks_like_short_ambiguous_followup(
    message: str,
    *,
    explicit_student: dict[str, Any] | None,
    explicit_subject: str | None,
    unknown_student: str | None,
    unknown_subject: str | None,
    asks_finance: bool,
    asks_admin: bool,
    asks_attendance: bool,
    asks_grade: bool,
    asks_upcoming: bool,
    asks_justification: bool,
    asks_public_pricing: bool,
) -> bool:
    normalized = normalize_text(message)
    if not normalized or len(normalized) > 48:
        return False
    if asks_finance or asks_admin or asks_attendance or asks_grade or asks_upcoming or asks_justification or asks_public_pricing:
        return False
    if explicit_subject or unknown_subject:
        return False
    if not (
        explicit_student
        or unknown_student
        or re.search(r'\b(?:ele|ela|dele|dela)\b', normalized)
        or re.search(r'^(?:e\s+)?(?:do|da)\s+[a-z]{3,}(?:\s+[a-z]{3,})?(?:\s+\w+)?\??$', normalized)
    ):
        return False
    return (
        any(term in normalized for term in {'serve', 'isso', 'esse', 'essa', 'assim'})
        or normalized in {'e dele?', 'e dela?', 'dele?', 'dela?'}
        or bool(re.search(r'^(?:e\s+)?(?:do|da)\s+[a-z]{3,}(?:\s+[a-z]{3,})?(?:\s+serve)?\??$', normalized))
    )


def resolve_answer_focus(
    *,
    request_message: str,
    actor: dict[str, Any] | None,
    conversation_context: dict[str, Any] | None,
) -> AnswerFocusState:
    normalized = normalize_text(request_message)
    slot_memory = recent_trace_slot_memory(conversation_context)
    active_task = str((slot_memory or {}).get('active_task') or '').strip() or None
    slot_academic_attribute = str((slot_memory or {}).get('academic_attribute') or '').strip() or None
    slot_finance_attribute = str((slot_memory or {}).get('finance_attribute') or '').strip() or None
    slot_finance_status_filter = str((slot_memory or {}).get('finance_status_filter') or '').strip() or None
    slot_public_pricing_segment = str((slot_memory or {}).get('public_pricing_segment') or '').strip() or None
    slot_public_pricing_grade_year = str((slot_memory or {}).get('public_pricing_grade_year') or '').strip() or None
    slot_public_pricing_quantity = str((slot_memory or {}).get('public_pricing_quantity') or '').strip() or None
    slot_public_pricing_price_kind = str((slot_memory or {}).get('public_pricing_price_kind') or '').strip() or None
    historical_public_pricing_segment = _recent_slot_value_for_task(
        conversation_context,
        key='public_pricing_segment',
        active_task='public:pricing',
    )
    historical_public_pricing_grade_year = _recent_slot_value_for_task(
        conversation_context,
        key='public_pricing_grade_year',
        active_task='public:pricing',
    )
    historical_public_pricing_quantity = _recent_slot_value_for_task(
        conversation_context,
        key='public_pricing_quantity',
        active_task='public:pricing',
    )
    historical_public_pricing_price_kind = _recent_slot_value_for_task(
        conversation_context,
        key='public_pricing_price_kind',
        active_task='public:pricing',
    )
    message_public_pricing_segment = _recent_public_pricing_value_from_messages(
        conversation_context,
        extractor=_extract_public_pricing_segment,
    )
    message_public_pricing_grade_year = _recent_public_pricing_value_from_messages(
        conversation_context,
        extractor=_extract_public_pricing_grade_year,
    )
    message_public_pricing_quantity = _recent_public_pricing_value_from_messages(
        conversation_context,
        extractor=_extract_public_pricing_quantity,
    )
    message_public_pricing_price_kind = _recent_public_pricing_value_from_messages(
        conversation_context,
        extractor=_detect_public_pricing_price_kind,
    )
    focus_marked_student = _find_focus_marked_student(actor, request_message)
    focus_marked_student_used = focus_marked_student is not None
    explicit_student = focus_marked_student or _find_explicit_student(actor, request_message)
    explicit_linked_student_count = _count_explicit_linked_students(actor, request_message)
    if explicit_linked_student_count >= 2 and focus_marked_student is None:
        explicit_student = None
    explicit_subject = explicit_subject_from_message(request_message)
    unknown_student = None if explicit_student else _extract_unknown_student_reference(actor, request_message)
    unknown_subject = None if explicit_subject else _extract_unknown_subject_reference(request_message, actor)
    repair_followup = _looks_like_repair_followup(request_message)
    asks_finance = _contains_any(request_message, _FINANCE_TERMS)
    asks_admin = _contains_any(request_message, _ADMIN_TERMS)
    asks_attendance = _contains_any(request_message, _ACADEMIC_ATTENDANCE_TERMS)
    asks_grade_terms = _contains_any(request_message, _ACADEMIC_GRADE_TERMS)
    asks_upcoming = _contains_any(request_message, _ACADEMIC_UPCOMING_TERMS)
    slot_focus_kind = str((slot_memory or {}).get('academic_focus_kind') or '').strip()
    upcoming_context_active = bool(
        (active_task and active_task.startswith('academic:upcoming'))
        or slot_focus_kind == 'upcoming'
        or _recent_assistant_mentions_upcoming(conversation_context)
    )
    if explicit_subject is not None and not (asks_grade_terms or asks_upcoming or asks_attendance) and upcoming_context_active:
        asks_upcoming = True
    asks_grade = asks_grade_terms or (explicit_subject is not None and not asks_upcoming and not asks_attendance)
    asks_justification = _looks_like_attendance_justification_query(request_message, slot_memory=slot_memory)
    asks_comparison = any(term in normalized for term in ('compare', 'compar', 'diferenca', 'diferença', 'entre '))
    asks_yes_no = normalized.endswith('?') and any(term in normalized for term in {normalize_text(item) for item in _YES_NO_TERMS})
    asks_family_finance_aggregate = _looks_like_family_finance_aggregate_query(request_message)
    asks_family_academic_aggregate = _looks_like_family_academic_aggregate_query(request_message)
    asks_family_admin_aggregate = _looks_like_family_admin_aggregate_query(request_message)
    if explicit_linked_student_count >= 2:
        if asks_finance:
            asks_family_finance_aggregate = True
        if asks_grade or asks_upcoming or asks_attendance:
            asks_family_academic_aggregate = True
        if asks_admin:
            asks_family_admin_aggregate = True
    asks_family_aggregate = asks_family_finance_aggregate or asks_family_academic_aggregate or asks_family_admin_aggregate
    if asks_family_aggregate and explicit_student is None:
        unknown_student = None
    direct_public_pricing = _looks_like_public_pricing_query(request_message)
    followup_public_pricing = _looks_like_public_pricing_followup(
        request_message,
        slot_memory={
            **(slot_memory or {}),
            'public_pricing_segment': slot_public_pricing_segment or historical_public_pricing_segment,
            'public_pricing_grade_year': slot_public_pricing_grade_year or historical_public_pricing_grade_year,
            'public_pricing_quantity': slot_public_pricing_quantity or historical_public_pricing_quantity,
            'public_pricing_price_kind': slot_public_pricing_price_kind or historical_public_pricing_price_kind,
        },
    )
    asks_public_pricing = direct_public_pricing or (
        followup_public_pricing and not any((asks_finance, asks_admin, asks_attendance, asks_grade, asks_upcoming, asks_justification))
    )

    known_unknown_key = detect_public_known_unknown_key(request_message)
    if known_unknown_key:
        repair_followup = False

    domain: str | None = None
    topic: str | None = None
    if known_unknown_key:
        domain = 'public'
        topic = 'known_unknown'
    elif asks_public_pricing:
        domain = 'public'
        topic = 'pricing'
    elif asks_family_finance_aggregate:
        domain = 'finance'
        topic = 'student_finance'
    elif asks_family_academic_aggregate:
        domain = 'academic'
        if asks_upcoming:
            topic = 'upcoming_assessments'
        elif asks_attendance:
            topic = 'attendance'
        else:
            topic = 'grades'
    elif asks_finance and asks_admin:
        domain = 'institution'
        topic = 'admin_finance_combo'
    elif asks_finance:
        domain = 'finance'
        topic = 'student_finance'
    elif asks_justification:
        domain = 'institution'
        topic = 'attendance_justification'
    elif asks_upcoming:
        domain = 'academic'
        topic = 'upcoming_assessments'
    elif asks_attendance:
        domain = 'academic'
        topic = 'attendance'
    elif asks_grade:
        domain = 'academic'
        topic = 'grades'
    elif asks_admin:
        domain = 'institution'
        topic = 'administrative_status'
    elif repair_followup:
        domain = 'conversation'
        topic = 'repair'

    linked_students = _linked_students(actor)

    needs_disambiguation = _looks_like_short_ambiguous_followup(
        request_message,
        explicit_student=explicit_student,
        explicit_subject=explicit_subject,
        unknown_student=unknown_student,
        unknown_subject=unknown_subject,
        asks_finance=asks_finance,
        asks_admin=asks_admin,
        asks_attendance=asks_attendance,
        asks_grade=asks_grade,
        asks_upcoming=asks_upcoming,
        asks_justification=asks_justification,
        asks_public_pricing=asks_public_pricing,
    )
    if domain is None and needs_disambiguation:
        domain = 'conversation'
        topic = 'clarify'

    uses_memory = False
    student = explicit_student
    if student is None and unknown_student is None and not asks_family_aggregate:
        slot_candidate: str | None = None
        if domain == 'finance':
            slot_candidate = str((slot_memory or {}).get('finance_student_name') or '').strip() or None
        elif domain in {'academic', 'institution'}:
            slot_candidate = (
                str((slot_memory or {}).get('academic_student_name') or '').strip()
                or str((slot_memory or {}).get('finance_student_name') or '').strip()
                or None
            )
        if slot_candidate and (_looks_like_followup(request_message) or domain in {'academic', 'finance', 'institution'}):
            student = _find_student_by_name(actor, slot_candidate)
            uses_memory = student is not None
        if student is None and len(_linked_students(actor)) == 1 and domain in {'academic', 'finance', 'institution'}:
            student = _linked_students(actor)[0]

    subject_name = explicit_subject
    if (
        subject_name is None
        and unknown_subject is None
        and not repair_followup
        and not asks_family_aggregate
        and not focus_marked_student_used
        and _looks_like_followup(request_message)
    ):
        subject_name = _recent_memory_subject(slot_memory) or _recent_subject_from_messages(conversation_context)
        uses_memory = uses_memory or bool(subject_name)

    correction_followup = _looks_like_student_correction_followup(request_message)

    if domain is None and not repair_followup and (_looks_like_followup(request_message) or correction_followup) and isinstance(slot_memory, dict):
        if active_task == 'public:pricing':
            domain = 'public'
            topic = 'pricing'
        elif active_task and active_task.startswith('finance:'):
            domain = 'finance'
            topic = 'student_finance'
        elif active_task and active_task.startswith('academic:attendance'):
            domain = 'academic'
            topic = 'attendance'
        elif active_task and active_task.startswith('academic:upcoming'):
            domain = 'academic'
            topic = 'upcoming_assessments'
        elif active_task and active_task.startswith('academic:'):
            domain = 'academic'
            topic = 'grades'
        elif active_task and active_task.startswith('admin:'):
            domain = 'institution'
            topic = 'administrative_status'
        if student is None and domain in {'academic', 'finance', 'institution'} and not asks_family_aggregate:
            slot_candidate = None
            if domain == 'finance':
                slot_candidate = str((slot_memory or {}).get('finance_student_name') or '').strip() or None
            elif domain == 'academic':
                slot_candidate = str((slot_memory or {}).get('academic_student_name') or '').strip() or None
            else:
                slot_candidate = (
                    str((slot_memory or {}).get('academic_student_name') or '').strip()
                    or str((slot_memory or {}).get('finance_student_name') or '').strip()
                    or None
                )
            if slot_candidate:
                student = _find_student_by_name(actor, slot_candidate)
                uses_memory = uses_memory or student is not None
            if student is None and len(_linked_students(actor)) == 1:
                student = _linked_students(actor)[0]
        if (
            subject_name is None
            and unknown_subject is None
            and domain == 'academic'
            and not asks_family_aggregate
            and not focus_marked_student_used
        ):
            subject_name = _recent_memory_subject(slot_memory) or _recent_subject_from_messages(conversation_context)
            uses_memory = uses_memory or bool(subject_name)

    if asks_family_aggregate:
        student = None
        unknown_student = None
        if explicit_subject is None and unknown_subject is None:
            subject_name = None

    if (
        not needs_disambiguation
        and student is None
        and unknown_student is None
        and len(linked_students) > 1
        and domain in {'academic', 'finance', 'institution'}
        and not asks_family_aggregate
    ):
        if (
            domain == 'academic'
            and (
                explicit_subject is not None
                or asks_grade
                or asks_upcoming
                or asks_attendance
                or _looks_like_followup(request_message)
            )
        ):
            needs_disambiguation = True
        elif domain == 'finance' and (asks_finance or _looks_like_followup(request_message)):
            needs_disambiguation = True

    academic_attribute = slot_academic_attribute if domain == 'academic' else None
    finance_attribute = slot_finance_attribute if domain == 'finance' else None
    finance_status_filter = slot_finance_status_filter if domain == 'finance' else None
    public_pricing_is_followup = domain == 'public' and topic == 'pricing' and not direct_public_pricing
    public_pricing_can_inherit_segment = (
        domain == 'public'
        and topic == 'pricing'
        and (
            public_pricing_is_followup
            or (
                direct_public_pricing
                and _extract_public_pricing_segment(request_message) is None
                and _extract_public_pricing_grade_year(request_message) is None
            )
        )
    )
    public_pricing_can_inherit_price_kind = (
        domain == 'public'
        and topic == 'pricing'
        and (public_pricing_is_followup or (direct_public_pricing and _detect_public_pricing_price_kind(request_message) is None))
    )
    public_pricing_segment = (
        _extract_public_pricing_segment(request_message)
        or (
            (slot_public_pricing_segment or historical_public_pricing_segment or message_public_pricing_segment)
            if public_pricing_can_inherit_segment
            else None
        )
    )
    public_pricing_grade_year = (
        _extract_public_pricing_grade_year(request_message)
        or (
            (slot_public_pricing_grade_year or historical_public_pricing_grade_year or message_public_pricing_grade_year)
            if public_pricing_can_inherit_segment
            else None
        )
    )
    public_pricing_quantity = (
        _extract_public_pricing_quantity(request_message)
        or (
            (slot_public_pricing_quantity or historical_public_pricing_quantity or message_public_pricing_quantity)
            if public_pricing_is_followup
            else None
        )
    )
    public_pricing_price_kind = (
        _detect_public_pricing_price_kind(request_message)
        or (
            (slot_public_pricing_price_kind or historical_public_pricing_price_kind or message_public_pricing_price_kind)
            if public_pricing_can_inherit_price_kind
            else None
        )
    )

    return AnswerFocusState(
        domain=domain,
        topic=topic,
        student_name=str(student.get('full_name') or '').strip() or None if isinstance(student, dict) else None,
        student_id=str(student.get('student_id') or '').strip() or None if isinstance(student, dict) else None,
        subject_name=subject_name,
        academic_attribute=academic_attribute,
        finance_attribute=finance_attribute,
        finance_status_filter=finance_status_filter,
        public_pricing_segment=public_pricing_segment,
        public_pricing_grade_year=public_pricing_grade_year,
        public_pricing_quantity=public_pricing_quantity,
        public_pricing_price_kind=public_pricing_price_kind,
        active_task=active_task,
        unknown_student_name=unknown_student,
        unknown_subject_name=unknown_subject,
        asks_yes_no=asks_yes_no,
        uses_memory=uses_memory,
        asks_comparison=asks_comparison,
        asks_single_focus=bool(student or subject_name or unknown_student or unknown_subject or asks_yes_no),
        asks_family_aggregate=asks_family_aggregate,
        is_repair_followup=repair_followup,
        needs_disambiguation=needs_disambiguation,
    )


def build_focus_summary(focus: AnswerFocusState) -> str:
    bits: list[str] = []
    if focus.domain:
        bits.append(f'dominio={focus.domain}')
    if focus.topic:
        bits.append(f'topico={focus.topic}')
    if focus.student_name:
        bits.append(f'aluno={focus.student_name}')
    if focus.subject_name:
        bits.append(f'disciplina={focus.subject_name}')
    if focus.academic_attribute:
        bits.append(f'academic_attribute={focus.academic_attribute}')
    if focus.finance_attribute:
        bits.append(f'finance_attribute={focus.finance_attribute}')
    if focus.finance_status_filter:
        bits.append(f'finance_status={focus.finance_status_filter}')
    if focus.public_pricing_segment:
        bits.append(f'pricing_segment={focus.public_pricing_segment}')
    if focus.public_pricing_grade_year:
        bits.append(f'pricing_grade_year={focus.public_pricing_grade_year}')
    if focus.public_pricing_quantity:
        bits.append(f'pricing_quantity={focus.public_pricing_quantity}')
    if focus.public_pricing_price_kind:
        bits.append(f'pricing_kind={focus.public_pricing_price_kind}')
    if focus.active_task:
        bits.append(f'active_task={focus.active_task}')
    if focus.unknown_student_name:
        bits.append(f'aluno_desconhecido={focus.unknown_student_name}')
    if focus.unknown_subject_name:
        bits.append(f'disciplina_desconhecida={focus.unknown_subject_name}')
    if focus.asks_yes_no:
        bits.append('formato=yes_no')
    if focus.asks_comparison:
        bits.append('formato=comparativo')
    if focus.asks_single_focus:
        bits.append('escopo=estreito')
    if focus.asks_family_aggregate:
        bits.append('escopo=familia_agregada')
    if focus.uses_memory:
        bits.append('memoria=sim')
    if focus.is_repair_followup:
        bits.append('repair=sim')
    if focus.needs_disambiguation:
        bits.append('ambiguo=sim')
    return ', '.join(bits) if bits else 'sem foco explicito'
