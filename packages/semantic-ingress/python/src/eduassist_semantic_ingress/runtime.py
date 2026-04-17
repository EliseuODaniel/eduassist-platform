from __future__ import annotations

import json
import re
import unicodedata
from typing import Any, Literal

import httpx
from openai import AsyncOpenAI
from pydantic import BaseModel

from eduassist_observability import (
    extract_google_usage,
    extract_openai_usage,
    normalize_gen_ai_provider_name,
    start_gen_ai_client_operation,
)

IngressAct = Literal[
    'none',
    'greeting',
    'assistant_identity',
    'auth_guidance',
    'capabilities',
    'input_clarification',
    'language_preference',
    'scope_boundary',
]
ConfidenceBucket = Literal['low', 'medium', 'high']
TERMINAL_INGRESS_ACTS: tuple[IngressAct, ...] = (
    'greeting',
    'assistant_identity',
    'auth_guidance',
    'capabilities',
    'input_clarification',
    'language_preference',
    'scope_boundary',
)

_ALLOWED_ACTS: tuple[IngressAct, ...] = (
    'none',
    'greeting',
    'assistant_identity',
    'auth_guidance',
    'capabilities',
    'input_clarification',
    'language_preference',
    'scope_boundary',
)
_SHORT_MESSAGE_MAX_TOKENS = 8
_SHORT_MESSAGE_MAX_CHARS = 96
_STRONG_CONTENT_TERMS = {
    'nota',
    'notas',
    'media',
    'medias',
    'média',
    'médias',
    'boletim',
    'frequencia',
    'frequência',
    'falta',
    'faltas',
    'prova',
    'provas',
    'avaliacao',
    'avaliação',
    'financeiro',
    'mensalidade',
    'mensalidades',
    'boleto',
    'boletos',
    'fatura',
    'faturas',
    'pagamento',
    'pagamentos',
    'cadastro',
    'protocolo',
    'secretaria',
    'documentacao',
    'documentação',
    'documento',
    'documentos',
    'visita',
    'rematricula',
    'rematrícula',
    'transferencia',
    'transferência',
    'cancelamento',
    'calendario',
    'calendário',
    'aulas',
    'reuniao',
    'reunião',
    'bullying',
    'comportamento',
    'expulsao',
    'expulsão',
}
_LANGUAGE_PREFERENCE_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(
        r'\b(?:fale|fala|responda|responde|escreva|escreve)\b.*\b(?:portugues|português|ingles|inglês|english|espanhol|spanish)\b'
    ),
    re.compile(
        r'\bquero que\b.*\b(?:fale|fala|responda|responde)\b.*\b(?:portugues|português|ingles|inglês|english|espanhol|spanish)\b'
    ),
    re.compile(
        r'\b(?:prefiro|apenas|so|só)\b.*\b(?:portugues|português|ingles|inglês|english|espanhol|spanish)\b'
    ),
    re.compile(
        r'\b(?:ta|tá|esta|está|ficou|veio)\b.*\bem\b.*\b(?:ingles|inglês|english|portugues|português)\b'
    ),
    re.compile(
        r'\bpor que\b.*\b(?:admissions|termo|palavra|mensagem|resposta|texto)\b.*\b(?:ingles|inglês|english|portugues|português)\b'
    ),
    re.compile(
        r'\b(?:admissions|termo|palavra|mensagem|resposta|texto)\b.*\bem\b.*\b(?:ingles|inglês|english|portugues|português)\b'
    ),
)
_LANGUAGE_PREFERENCE_META_TERMS = {
    'admissions',
    'idioma',
    'lingua',
    'língua',
    'termo',
    'palavra',
    'mensagem',
    'resposta',
    'texto',
}
_LANGUAGE_NAME_TERMS = {
    'portugues',
    'português',
    'ingles',
    'inglês',
    'english',
    'espanhol',
    'spanish',
}
_LANGUAGE_SUBJECT_NEGATIVE_HINTS = {
    'nota',
    'notas',
    'prova',
    'provas',
    'avaliacao',
    'avaliação',
    'disciplina',
    'disciplinas',
    'materia',
    'matéria',
    'aula',
    'aulas',
    'boletim',
    'faltas',
    'frequencia',
    'frequência',
    'aluno',
    'aluna',
    'lucas',
    'ana',
}
_OPAQUE_SHORT_INPUT_EXACT_EXCLUSIONS = {
    'oi',
    'ola',
    'olá',
    'oie',
    'ok',
    'okay',
    'okey',
    'sim',
    'nao',
    'não',
    'obrigado',
    'obrigada',
    'valeu',
}
_OPAQUE_SHORT_INPUT_PREFIX_EXCLUSIONS = (
    'bom dia',
    'boa tarde',
    'boa noite',
    'boa madruga',
    'boa madrugada',
    'boa manha',
    'boa manhã',
    'e ai',
    'e aí',
)
_SCHOOL_SCOPE_TERMS = {
    'escola',
    'colegio',
    'colégio',
    'eduassist',
    'matricula',
    'matrícula',
    'rematricula',
    'rematrícula',
    'financeiro',
    'mensalidade',
    'boleto',
    'fatura',
    'vencimento',
    'vencimentos',
    'parcela',
    'parcelas',
    'segunda via',
    'secretaria',
    'documento',
    'documentos',
    'calendario',
    'calendário',
    'feriado',
    'feriados',
    'aulas',
    'professor',
    'professora',
    'aluno',
    'aluna',
    'estudante',
    'nota',
    'notas',
    'boletim',
    'frequencia',
    'frequência',
    'faltas',
    'prova',
    'provas',
    'disciplina',
    'disciplinas',
    'materia',
    'matéria',
    'bullying',
    'comportamento',
    'conduta',
    'maconha',
    'droga',
    'drogas',
    'fumar',
    'cigarro',
    'vape',
    'alcool',
    'álcool',
    'visita',
    'portal',
    'biblioteca',
    'library',
    'acervo',
    'laboratorio',
    'laboratório',
    'laboratorios',
    'laboratórios',
    'coordenacao',
    'coordenação',
    'coordenador',
    'coordenadora',
    'direcao',
    'direção',
    'diretoria',
    'diretor',
    'diretora',
    'admissions',
    'bncc',
    'curriculo',
    'currículo',
    'conteudo',
    'conteúdo',
    'ensinado',
    'confessional',
    'laica',
    'religiosa',
    'noticia',
    'notícias',
    'ultima aula',
    'última aula',
    'madrugada',
}

_SCHOOL_PUBLIC_FACILITY_TERMS = {
    'biblioteca',
    'library',
    'acervo',
    'laboratorio',
    'laboratório',
    'laboratorios',
    'laboratórios',
}

_SCHOOL_PUBLIC_LEADERSHIP_TERMS = {
    'diretor',
    'diretora',
    'diretoria',
    'direcao',
    'direção',
    'coordenador',
    'coordenadora',
    'coordenacao',
    'coordenação',
    'secretaria',
    'professor',
    'professora',
}

_PUBLIC_INFO_INTENT_TERMS = {
    'horario',
    'horário',
    'horarios',
    'horários',
    'funciona',
    'abre',
    'fecha',
    'nome',
    'contato',
    'telefone',
    'email',
    'e-mail',
    'whatsapp',
    'whats',
    'canal',
    'como falar',
    'como falo',
    'falar com',
    'quero falar com',
    'conversar com',
}

_EXPLICIT_NON_SCHOOL_SCOPE_MARKERS = {
    'sem relacao com escola',
    'sem relação com escola',
    'sem relacao com a escola',
    'sem relação com a escola',
    'sem relacao com o colegio',
    'sem relação com o colégio',
    'sem relacao com colegio',
    'sem relação com colégio',
    'fora do tema escolar',
    'fora do tema da escola',
    'fora do escopo da escola',
    'sem ligar para a escola',
    'sem relação com atendimento escolar',
    'sem relacao com atendimento escolar',
}

_PUBLIC_SCHEDULE_INTENT_TERMS = {
    'turno',
    'turnos',
    'turma',
    'turmas',
    'aula',
    'aulas',
    'matutino',
    'matutina',
    'manha',
    'manhã',
    'vespertino',
    'vespertina',
    'noturno',
    'noturna',
    'integral',
    'aula de manha',
    'aula de manhã',
    'aula da manha',
    'aula da manhã',
    'turno da manha',
    'turno da manhã',
    'turno de manha',
    'turno de manhã',
    'horario de aula',
    'horário de aula',
    'horario da aula',
    'horário da aula',
    'horario da manha',
    'horário da manhã',
    'horario do turno',
    'horário do turno',
    'ultima aula',
    'última aula',
}

_PUBLIC_SCHEDULE_TIME_TERMS = {
    'que horas',
    'qual horario',
    'qual horário',
    'horario',
    'horário',
    'horarios',
    'horários',
    'comeca',
    'começa',
    'inicio',
    'início',
    'termina',
    'acaba',
    'fecha',
    'tem',
    'atende',
    'ultima aula',
    'última aula',
    'madrugada',
}

_PUBLIC_PRICING_TERMS = {
    'valor da matricula',
    'valor da matrícula',
    'taxa de matricula',
    'taxa de matrícula',
    'mensalidade',
    'mensalidades',
    'quanto custa',
    'quanto fica',
    'preco da matricula',
    'preço da matrícula',
}

_PRIVATE_FINANCE_HINTS = {
    'fatura',
    'faturas',
    'boleto',
    'boletos',
    'em aberto',
    'vencimento',
    'vencida',
    'vencidas',
    'lucas',
    'ana',
    'meu filho',
    'minha filha',
    'contas vinculadas',
}

_PROTECTED_FINANCE_ACTION_HINTS = {
    'paguei',
    'paguei parte',
    'negociar',
    'negociacao',
    'negociação',
    'restante',
    'quitar',
    'quitacao',
    'quitação',
    'parcelar',
    'renegociar',
    'meu financeiro',
    'situacao financeira',
    'situação financeira',
    'minha situacao financeira',
    'minha situação financeira',
    'atraso',
    'atrasos',
    'desconto',
    'descontos',
}

_ENROLLMENT_DOCUMENT_TERMS = {
    'quais documentos preciso',
    'documentos exigidos',
    'documentos sao exigidos',
    'documentos são exigidos',
    'documentos necessarios',
    'documentos necessários',
    'preciso para matricula',
    'preciso para a matricula',
    'preciso para matrícula',
    'preciso para a matrícula',
}

_SCHOOL_YEAR_START_TERMS = {
    'iniciam as aulas',
    'quando iniciam as aulas',
    'quando comecam as aulas',
    'quando começam as aulas',
    'quando inicia o ano letivo',
    'inicio das aulas',
    'início das aulas',
    'comeco das aulas',
    'começo das aulas',
    'ano letivo',
}

_PUBLIC_CURRICULUM_TERMS = {
    'bncc',
    'curriculo',
    'currículo',
    'conteudo ensinado',
    'conteúdo ensinado',
    'o que e bncc',
    'o que é bncc',
    'disciplina de',
    'materia de',
    'matéria de',
}

_PUBLIC_IDENTITY_TERMS = {
    'confessional',
    'laica',
    'religiosa',
    'colegio confessional',
    'colégio confessional',
    'escola confessional',
}

_PUBLIC_NEWS_TERMS = {
    'ultima noticia',
    'última notícia',
    'ultima noticia sobre',
    'última notícia sobre',
    'noticia sobre a escola',
    'notícia sobre a escola',
    'noticias da escola',
    'notícias da escola',
    'noticias do colegio',
    'notícias do colégio',
}


class IngressSemanticPlan(BaseModel):
    conversation_act: IngressAct = 'none'
    use_conversation_context: bool = False
    confidence_bucket: ConfidenceBucket = 'medium'
    reason: str = ''

    @property
    def terminal_fast_path(self) -> bool:
        return is_terminal_ingress_act(self.conversation_act)


def is_terminal_ingress_act(act: str | None) -> bool:
    normalized = str(act or '').strip().lower()
    return normalized in TERMINAL_INGRESS_ACTS


def _is_latin_letter(ch: str) -> bool:
    if not ch:
        return False
    name = unicodedata.name(ch, '')
    return 'LATIN' in name and unicodedata.category(ch).startswith('L')


def _normalize_latin_char(ch: str) -> str:
    decomposed = unicodedata.normalize('NFKD', ch)
    pieces = [piece for piece in decomposed if not unicodedata.combining(piece)]
    return ''.join(pieces) or ch


def normalize_ingress_text(text: str | None) -> str:
    normalized = (
        unicodedata.normalize('NFKC', str(text or '')).lower().replace('º', 'o').replace('ª', 'a')
    )
    chars: list[str] = []
    for ch in normalized:
        category = unicodedata.category(ch)
        if ch.isspace():
            chars.append(' ')
        elif _is_latin_letter(ch):
            chars.append(_normalize_latin_char(ch))
        elif ch.isalnum() or category.startswith('L') or category.startswith('N'):
            chars.append(ch)
        elif category.startswith('M'):
            if chars and not _is_latin_letter(chars[-1][-1]):
                chars.append(ch)
            else:
                continue
        elif unicodedata.combining(ch):
            continue
        else:
            chars.append(' ')
    return re.sub(r'\s+', ' ', ''.join(chars)).strip()


def _compact_raw_text(text: str | None) -> str:
    return re.sub(r'\s+', ' ', str(text or '')).strip()


def _has_letter_or_digit(text: str | None) -> bool:
    return any(ch.isalnum() for ch in str(text or ''))


def _contains_term(normalized_text: str, term: str) -> bool:
    if not term:
        return False
    padded = f' {normalized_text} '
    needle = f' {normalize_ingress_text(term)} '
    return needle in padded


def looks_like_language_preference_feedback(message: str | None) -> bool:
    normalized = normalize_ingress_text(message)
    if not normalized:
        return False
    has_language_name = any(_contains_term(normalized, term) for term in _LANGUAGE_NAME_TERMS)
    if not has_language_name and 'admissions' not in normalized:
        return False
    if any(pattern.search(normalized) for pattern in _LANGUAGE_PREFERENCE_PATTERNS):
        return True
    has_meta_anchor = any(
        _contains_term(normalized, term) for term in _LANGUAGE_PREFERENCE_META_TERMS
    )
    has_academic_hint = any(
        _contains_term(normalized, term) for term in _LANGUAGE_SUBJECT_NEGATIVE_HINTS
    )
    if has_language_name and has_meta_anchor and not has_academic_hint:
        return True
    return False


def looks_like_opaque_short_input(message: str | None) -> bool:
    raw_text = _compact_raw_text(message)
    normalized = normalize_ingress_text(message)
    effective_text = normalized or raw_text
    if not effective_text:
        return False
    if len(effective_text) > 12:
        return False
    parts = effective_text.split()
    if len(parts) > 2:
        return False
    if looks_like_language_preference_feedback(message):
        return False
    lowered = effective_text.strip().lower()
    if lowered in _OPAQUE_SHORT_INPUT_EXACT_EXCLUSIONS:
        return False
    if any(
        lowered == prefix or lowered.startswith(f'{prefix} ')
        for prefix in _OPAQUE_SHORT_INPUT_PREFIX_EXCLUSIONS
    ):
        return False
    if any(_contains_term(normalize_ingress_text(lowered), term) for term in _STRONG_CONTENT_TERMS):
        return False
    if len(parts) == 1 and len(parts[0]) <= 8 and parts[0].isalpha():
        return True
    if not normalized and len(raw_text) <= 4:
        return True
    return False


def looks_like_high_confidence_public_school_faq(message: str | None) -> bool:
    normalized = normalize_ingress_text(message)
    if not normalized:
        return False
    if any(_contains_term(normalized, term) for term in {'feriado', 'feriados'}) and any(
        _contains_term(normalized, term)
        for term in {
            'ano',
            'desse ano',
            'deste ano',
            'este ano',
            'calendario',
            'calendário',
            'ano letivo',
        }
    ):
        return True
    if (
        any(_contains_term(normalized, term) for term in {'calendario', 'calendário', 'agenda', 'eventos'})
        and any(_contains_term(normalized, term) for term in {'familias', 'famílias', 'responsaveis', 'responsáveis'})
        and any(
            _contains_term(normalized, term)
            for term in {
                'publicos',
                'públicos',
                'publico',
                'público',
                'aparecem nesta base',
                'aparecem na base',
                'aparecem agora',
                'nesta base agora',
                'visiveis',
                'visíveis',
                'principais',
                'mais importantes',
            }
        )
    ):
        return True
    has_facility = any(_contains_term(normalized, term) for term in _SCHOOL_PUBLIC_FACILITY_TERMS)
    if has_facility and (
        any(_contains_term(normalized, term) for term in _PUBLIC_INFO_INTENT_TERMS)
        or any(
            _contains_term(normalized, term)
            for term in {
                'tem biblioteca',
                'ha biblioteca',
                'há biblioteca',
                'possui biblioteca',
                'existe biblioteca',
            }
        )
    ):
        return True
    has_leadership = any(
        _contains_term(normalized, term) for term in _SCHOOL_PUBLIC_LEADERSHIP_TERMS
    )
    if has_leadership and any(_contains_term(normalized, term) for term in _PUBLIC_INFO_INTENT_TERMS):
        return True
    if _contains_term(normalized, 'matricula') and any(
        _contains_term(normalized, term) for term in _ENROLLMENT_DOCUMENT_TERMS
    ):
        return True
    if any(_contains_term(normalized, term) for term in _SCHOOL_YEAR_START_TERMS):
        return True
    if any(_contains_term(normalized, term) for term in _PUBLIC_CURRICULUM_TERMS):
        return True
    if any(_contains_term(normalized, term) for term in _PUBLIC_IDENTITY_TERMS):
        return True
    if any(_contains_term(normalized, term) for term in _PUBLIC_NEWS_TERMS) and any(
        _contains_term(normalized, term)
        for term in {'escola', 'colegio', 'colégio', 'colegio horizonte', 'colégio horizonte'}
    ):
        return True
    has_schedule_scope = any(
        _contains_term(normalized, term) for term in _PUBLIC_SCHEDULE_INTENT_TERMS
    )
    if has_schedule_scope and any(
        _contains_term(normalized, term) for term in _PUBLIC_SCHEDULE_TIME_TERMS
    ):
        return True
    if any(_contains_term(normalized, term) for term in _PUBLIC_PRICING_TERMS) and not any(
        _contains_term(normalized, term)
        for term in (*_PRIVATE_FINANCE_HINTS, *_PROTECTED_FINANCE_ACTION_HINTS)
    ):
        return True
    return False


def looks_like_school_scope_message(message: str | None) -> bool:
    normalized = normalize_ingress_text(message)
    if not normalized:
        return False
    if any(_contains_term(normalized, term) for term in _EXPLICIT_NON_SCHOOL_SCOPE_MARKERS):
        return False
    if looks_like_high_confidence_public_school_faq(message):
        return True
    if any(_contains_term(normalized, term) for term in _SCHOOL_SCOPE_TERMS):
        return True
    has_school_public_facility = any(
        _contains_term(normalized, term) for term in _SCHOOL_PUBLIC_FACILITY_TERMS
    )
    if has_school_public_facility:
        return True
    has_school_public_leadership = any(
        _contains_term(normalized, term) for term in _SCHOOL_PUBLIC_LEADERSHIP_TERMS
    )
    has_public_info_intent = any(
        _contains_term(normalized, term) for term in _PUBLIC_INFO_INTENT_TERMS
    )
    return has_school_public_leadership and has_public_info_intent


def looks_like_scope_boundary_candidate(message: str | None) -> bool:
    raw_text = _compact_raw_text(message)
    normalized = normalize_ingress_text(message)
    effective_text = normalized or raw_text
    if not effective_text:
        return False
    if looks_like_language_preference_feedback(message):
        return False
    if looks_like_opaque_short_input(message):
        return False
    if any(_contains_term(normalized, term) for term in _EXPLICIT_NON_SCHOOL_SCOPE_MARKERS):
        return True
    if looks_like_school_scope_message(message):
        return False
    if len(effective_text) < 6:
        return False
    if len(effective_text.split()) > 18:
        return False
    open_world_topic_terms = (
        'filme',
        'filmes',
        'serie',
        'series',
        'jogo',
        'jogos',
        'receita',
        'receitas',
        'livro',
        'livros',
        'netflix',
        'cinema',
        'restaurante',
        'restaurantes',
    )
    open_world_request_starters = (
        'me ajuda a escolher',
        'me ajuda a decidir',
        'me indica',
        'me recomenda',
        'recomenda',
        'indique',
        'quero uma recomendacao',
        'quero uma recomendação',
        'sugere',
        'sugira',
    )
    if any(_contains_term(normalized, term) for term in open_world_topic_terms) and any(
        normalized.startswith(starter) or starter in normalized for starter in open_world_request_starters
    ):
        return True
    if any(ch == '?' for ch in raw_text):
        return True
    return any(
        _contains_term(normalized, term)
        for term in (
            'qual',
            'quais',
            'quem',
            'como',
            'porque',
            'por que',
            'melhor',
            'pior',
            'pode',
            'posso',
            'devo',
            'vale a pena',
            'recomenda',
            'recomendacao',
            'recomendação',
        )
    )


def should_run_semantic_ingress_classifier(
    *,
    message: str,
    current_domain: str,
    current_access_tier: str,
    current_mode: str,
) -> bool:
    raw_text = _compact_raw_text(message)
    normalized = normalize_ingress_text(message)
    language_feedback = looks_like_language_preference_feedback(message)
    opaque_short_input = looks_like_opaque_short_input(message)
    scope_boundary_candidate = looks_like_scope_boundary_candidate(message)
    if not raw_text:
        return False
    effective_text = normalized or raw_text
    if len(effective_text) > _SHORT_MESSAGE_MAX_CHARS:
        return False
    if len(effective_text.split()) > _SHORT_MESSAGE_MAX_TOKENS:
        return False
    if str(current_domain or '').strip().lower() not in {'institution', 'unknown'} and not (
        language_feedback or opaque_short_input or scope_boundary_candidate
    ):
        return False
    if str(current_mode or '').strip().lower() not in {
        'structured_tool',
        'clarify',
        'hybrid_retrieval',
    }:
        return False
    if str(current_access_tier or '').strip().lower() == 'sensitive':
        return False
    if looks_like_school_scope_message(message) and not (language_feedback or opaque_short_input):
        return False
    if (
        normalized
        and any(_contains_term(normalized, term) for term in _STRONG_CONTENT_TERMS)
        and not (language_feedback or opaque_short_input or scope_boundary_candidate)
    ):
        return False
    if language_feedback:
        return True
    if opaque_short_input:
        return True
    if scope_boundary_candidate:
        return True
    if normalized:
        return True
    return _has_letter_or_digit(raw_text) or len(raw_text) <= _SHORT_MESSAGE_MAX_CHARS


def _extract_json_object(raw: str) -> dict[str, Any] | None:
    text = str(raw or '').strip()
    if not text:
        return None
    if text.startswith('```'):
        text = re.sub(r'^```(?:json)?\s*', '', text)
        text = re.sub(r'\s*```$', '', text)
    try:
        payload = json.loads(text)
        return payload if isinstance(payload, dict) else None
    except Exception:
        pass
    start = text.find('{')
    end = text.rfind('}')
    if start < 0 or end <= start:
        return None
    try:
        payload = json.loads(text[start : end + 1])
    except Exception:
        return None
    return payload if isinstance(payload, dict) else None


def _validated_conversation_act(*, request_message: str, act: str) -> IngressAct:
    normalized_act = str(act or 'none').strip().lower()
    if normalized_act not in _ALLOWED_ACTS:
        normalized_act = 'none'
    if looks_like_school_scope_message(request_message) and normalized_act == 'scope_boundary':
        normalized_act = 'none'
    if looks_like_language_preference_feedback(request_message):
        if normalized_act in {'none', 'input_clarification'}:
            return 'language_preference'
    if looks_like_opaque_short_input(request_message) and normalized_act == 'none':
        return 'input_clarification'
    if looks_like_scope_boundary_candidate(request_message) and normalized_act in {
        'none',
        'input_clarification',
    }:
        return 'scope_boundary'
    return normalized_act  # type: ignore[return-value]


def _recent_messages(conversation_context: dict[str, Any] | None, *, limit: int = 4) -> str:
    if not isinstance(conversation_context, dict):
        return '- nenhuma'
    items = conversation_context.get('recent_messages', [])
    if not isinstance(items, list) or not items:
        return '- nenhuma'
    lines: list[str] = []
    for item in items[-limit:]:
        if not isinstance(item, dict):
            continue
        sender = str(item.get('sender_type') or '').strip().lower() or 'desconhecido'
        content = str(item.get('content') or '').strip()
        if not content:
            continue
        lines.append(f'- {sender}: {content}')
    return '\n'.join(lines) if lines else '- nenhuma'


def _preview_compact(preview: dict[str, Any] | None) -> str:
    if not isinstance(preview, dict):
        return '{}'
    payload = {
        'mode': preview.get('mode'),
        'domain': preview.get('domain'),
        'access_tier': preview.get('access_tier'),
        'reason': preview.get('reason'),
        'selected_tools': preview.get('selected_tools') or [],
    }
    return json.dumps(payload, ensure_ascii=False, sort_keys=True)


def _instructions(stack_label: str) -> str:
    return (
        f'Voce e o classificador semantico de entrada do caminho {stack_label}. '
        'Voce nao responde ao usuario e nao resolve a tarefa. '
        'Sua funcao e classificar o ato conversacional inicial em uma das opcoes permitidas. '
        'Devolva somente JSON com as chaves: conversation_act, use_conversation_context, confidence_bucket, reason. '
        'Atos permitidos: none, greeting, assistant_identity, auth_guidance, capabilities, input_clarification, language_preference, scope_boundary. '
        'Use greeting para saudacoes, inclusive variacoes informais, regionais, abreviadas ou com vogais alongadas como '
        'boa madruga, boa madrugada, boa manha, oooie, oiie, e ai, hallo, привет, नमस्ते. '
        'Use assistant_identity para perguntas como quem e voce, com quem eu falo. '
        'Use capabilities para perguntas como o que voce faz ou como pode me ajudar. '
        'Use auth_guidance para orientacoes de vinculacao da conta e acesso protegido pelo Telegram. '
        'Use language_preference quando a pessoa estiver pedindo para voce falar em portugues, reclamando de termos em ingles, '
        'ou comentando que admissions, resposta, palavra, termo ou mensagem esta em ingles. '
        'Se a pessoa estiver reclamando de idioma, pedindo portugues ou criticando um termo em ingles, nunca use input_clarification. '
        'Use input_clarification quando a mensagem for curta mas estiver pouco clara, em idioma ou alfabeto que voce nao consegue interpretar com confianca, '
        'ou for apenas ruido, simbolos ou texto insuficiente para agir com seguranca. '
        'Use scope_boundary quando a pergunta for compreensivel, mas estiver fora do escopo da escola, do atendimento escolar ou das consultas do assistente. '
        'Exemplos: filmes, jogos, politica geral, receitas, opinioes gerais e qualquer conhecimento externo nao escolar. '
        'Se houver duvida entre none e input_clarification para uma entrada curta e pouco clara, prefira input_clarification. '
        'Use none por padrao quando a mensagem for um pedido de conteudo, politica, cadastro, documentos, notas, financeiro, '
        'calendario, comportamento, bullying ou qualquer assunto operacional real.'
    )


def _prompt(
    *,
    request_message: str,
    conversation_context: dict[str, Any] | None,
    preview: dict[str, Any] | None,
) -> str:
    return (
        'Classifique esta mensagem curta.\n\n'
        f'Preview atual:\n{_preview_compact(preview)}\n\n'
        f'Historico recente:\n{_recent_messages(conversation_context)}\n\n'
        f'Mensagem do usuario:\n{request_message}\n\n'
        'Exemplos positivos:\n'
        '- boa madruga -> greeting\n'
        '- boa madrugada -> greeting\n'
        '- oooie -> greeting\n'
        '- hallo -> greeting\n'
        '- привет -> greeting\n'
        '- नमस्ते -> greeting\n'
        '- quem e voce -> assistant_identity\n'
        '- o que voce faz -> capabilities\n'
        '- como vinculo minha conta -> auth_guidance\n'
        '- por que admissions ta em ingles -> language_preference\n'
        '- quero que so fale portugues -> language_preference\n'
        '- ??? -> input_clarification\n'
        '- rai -> input_clarification\n'
        '- qual o melhor filme do ano -> scope_boundary\n'
        '- qual o melhor jogo do ano -> scope_boundary\n'
        '- ghjkl -> input_clarification se nao houver confianca para interpretar\n\n'
        'Exemplos negativos:\n'
        '- bom comportamento -> none\n'
        '- boa parte das faltas -> none\n'
        '- qual a nota de ingles do Lucas -> none\n'
        '- meu cadastro -> none\n'
        '- situacao administrativa -> none\n'
        '- calendario publico -> none'
    )


def _llm_model_profile(settings: Any) -> str | None:
    return str(getattr(settings, 'llm_model_profile', '') or '').strip() or None


def _normalize_google_model(model_name: str | None) -> str:
    normalized = str(model_name or 'gemini-2.5-flash').strip()
    if normalized.endswith('-preview'):
        normalized = normalized.removesuffix('-preview')
    if normalized.startswith('models/'):
        return normalized
    if normalized.startswith('gemini/'):
        return f'models/{normalized.split("/", 1)[1]}'
    return f'models/{normalized}'


async def _text_call(
    *,
    settings: Any,
    stack_label: str,
    request_message: str,
    conversation_context: dict[str, Any] | None,
    preview: dict[str, Any] | None,
) -> str | None:
    instructions = _instructions(stack_label)
    prompt = _prompt(
        request_message=request_message,
        conversation_context=conversation_context,
        preview=preview,
    )
    provider = str(getattr(settings, 'llm_provider', 'openai') or 'openai').strip().lower()
    if provider == 'openai' and getattr(settings, 'openai_api_key', None):
        openai_base_url = str(getattr(settings, 'openai_base_url', 'https://api.openai.com/v1'))
        openai_model = str(getattr(settings, 'openai_model', 'gpt-5.4'))
        provider_name = normalize_gen_ai_provider_name('openai', base_url=openai_base_url)
        with start_gen_ai_client_operation(
            provider_name=provider_name,
            operation_name='semantic_classification',
            request_model=openai_model,
            base_url=openai_base_url,
            llm_model_profile=_llm_model_profile(settings),
        ) as operation:
            try:
                client = AsyncOpenAI(
                    api_key=settings.openai_api_key,
                    base_url=openai_base_url,
                )
                response = await client.responses.create(
                    model=openai_model,
                    instructions=instructions,
                    input=prompt,
                )
                text = (response.output_text or '').strip()
            except Exception as exc:
                operation.finish(error_type=exc.__class__.__name__)
                return None
            operation.finish(
                usage=extract_openai_usage(
                    response,
                    request_model=openai_model,
                    provider_name=provider_name,
                )
            )
        return text or None

    if provider in {'google', 'gemini', 'litellm'} and getattr(settings, 'google_api_key', None):
        model_name = _normalize_google_model(getattr(settings, 'google_model', 'gemini-2.5-flash'))
        endpoint = str(
            getattr(
                settings, 'google_api_base_url', 'https://generativelanguage.googleapis.com/v1beta'
            )
        ).rstrip('/')
        payload = {
            'system_instruction': {'parts': [{'text': instructions}]},
            'contents': [{'role': 'user', 'parts': [{'text': prompt}]}],
            'generationConfig': {
                'temperature': 0.0,
                'topP': 0.9,
                'maxOutputTokens': 180,
            },
        }
        url = f'{endpoint}/{model_name}:generateContent'
        provider_name = normalize_gen_ai_provider_name('google', base_url=endpoint)
        with start_gen_ai_client_operation(
            provider_name=provider_name,
            operation_name='semantic_classification',
            request_model=model_name,
            base_url=endpoint,
            request_temperature=0.0,
            request_max_tokens=180,
            request_top_p=0.9,
            llm_model_profile=_llm_model_profile(settings),
        ) as operation:
            try:
                async with httpx.AsyncClient(timeout=20.0) as client:
                    response = await client.post(
                        url,
                        params={'key': str(settings.google_api_key)},
                        json=payload,
                    )
                    response.raise_for_status()
                    body = response.json()
            except Exception as exc:
                operation.finish(error_type=exc.__class__.__name__)
                return None
            if not isinstance(body, dict):
                operation.finish(error_type='invalid_payload')
                return None
            operation.finish(usage=extract_google_usage(body, request_model=model_name))
        candidates = body.get('candidates') if isinstance(body, dict) else None
        if not isinstance(candidates, list):
            return None
        fragments: list[str] = []
        for candidate in candidates:
            if not isinstance(candidate, dict):
                continue
            content = candidate.get('content')
            parts = content.get('parts') if isinstance(content, dict) else None
            if not isinstance(parts, list):
                continue
            for part in parts:
                if isinstance(part, dict):
                    text = str(part.get('text') or '').strip()
                    if text:
                        fragments.append(text)
        return '\n'.join(fragments).strip() or None
    return None


async def resolve_semantic_ingress_with_provider(
    *,
    settings: Any,
    stack_label: str,
    request_message: str,
    conversation_context: dict[str, Any] | None,
    preview: dict[str, Any] | None,
) -> IngressSemanticPlan | None:
    text = await _text_call(
        settings=settings,
        stack_label=stack_label,
        request_message=request_message,
        conversation_context=conversation_context,
        preview=preview,
    )
    if not text:
        if looks_like_opaque_short_input(request_message):
            return IngressSemanticPlan(
                conversation_act='input_clarification',
                use_conversation_context=False,
                confidence_bucket='medium',
                reason='opaque_short_input_fallback',
            )
        if looks_like_scope_boundary_candidate(request_message):
            return IngressSemanticPlan(
                conversation_act='scope_boundary',
                use_conversation_context=False,
                confidence_bucket='medium',
                reason='scope_boundary_fallback',
            )
        return None
    payload = _extract_json_object(text)
    if not isinstance(payload, dict):
        if looks_like_opaque_short_input(request_message):
            return IngressSemanticPlan(
                conversation_act='input_clarification',
                use_conversation_context=False,
                confidence_bucket='medium',
                reason='opaque_short_input_non_json_fallback',
            )
        if looks_like_scope_boundary_candidate(request_message):
            return IngressSemanticPlan(
                conversation_act='scope_boundary',
                use_conversation_context=False,
                confidence_bucket='medium',
                reason='scope_boundary_non_json_fallback',
            )
        return None
    act = _validated_conversation_act(
        request_message=request_message,
        act=str(payload.get('conversation_act') or 'none'),
    )
    confidence_bucket = str(payload.get('confidence_bucket') or 'medium').strip().lower()
    if confidence_bucket not in {'low', 'medium', 'high'}:
        confidence_bucket = 'medium'
    reason = str(payload.get('reason') or '').strip()
    if act == 'language_preference' and looks_like_language_preference_feedback(request_message):
        if 'metalingu' not in normalize_ingress_text(reason):
            reason = 'metalinguistic_language_feedback'
        if confidence_bucket == 'low':
            confidence_bucket = 'high'
    if act == 'input_clarification' and looks_like_opaque_short_input(request_message):
        if 'opaque' not in normalize_ingress_text(reason):
            reason = 'opaque_short_input'
        if confidence_bucket == 'low':
            confidence_bucket = 'medium'
    return IngressSemanticPlan(
        conversation_act=act,  # type: ignore[arg-type]
        use_conversation_context=bool(payload.get('use_conversation_context', False)),
        confidence_bucket=confidence_bucket,  # type: ignore[arg-type]
        reason=reason,
    )
