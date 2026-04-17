from __future__ import annotations

from typing import Any

from .conversation_focus_runtime import _assistant_already_introduced, _normalize_text
from .public_concierge_runtime import _is_acknowledgement_query
from .public_act_rules_runtime import (
    _has_public_multi_intent_signal,
    _looks_like_public_documentary_open_query,
    _match_public_act_rule,
    _matched_public_act_rules,
    _prioritize_public_act_rules,
)
from .runtime_core_constants import (
    ACCESS_SCOPE_TERMS,
    ACKNOWLEDGEMENT_TERMS,
    AUTH_GUIDANCE_TERMS,
    PUBLIC_CAPACITY_DISAMBIGUATION_TERMS,
    PUBLIC_CAPACITY_PARKING_TERMS,
    PUBLIC_CAPACITY_STUDENT_TERMS,
    PUBLIC_OPERATING_HOURS_TERMS,
    PUBLIC_SOCIAL_TERMS,
    PUBLIC_WEB_TERMS,
    TEACHER_RECRUITMENT_TERMS,
    TEACHER_SCOPE_GUIDANCE_TERMS,
)


def _intent_analysis_impl(name: str):
    from . import intent_analysis_runtime as _intent_analysis_runtime

    return getattr(_intent_analysis_runtime, name)


def _contains_any(message: str, terms: set[str] | tuple[str, ...]) -> bool:
    return _intent_analysis_impl('_contains_any')(message, terms)


def _message_matches_term(message: str, term: str) -> bool:
    return _intent_analysis_impl('_message_matches_term')(message, term)


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


def _is_public_social_query(message: str) -> bool:
    normalized = _normalize_text(message)
    return any(_message_matches_term(normalized, term) for term in PUBLIC_SOCIAL_TERMS)


def _looks_like_teacher_internal_scope_query(message: str) -> bool:
    normalized = _normalize_text(message)
    if any(_message_matches_term(normalized, term) for term in TEACHER_SCOPE_GUIDANCE_TERMS):
        return True
    if any(
        _message_matches_term(normalized, term)
        for term in {
            'qual e a minha grade docente',
            'qual é a minha grade docente',
            'qual e minha grade docente',
            'qual é minha grade docente',
            'quais turmas e disciplinas eu tenho',
            'quais turmas e disciplinas eu atendo',
            'quais turmas eu tenho neste ano',
            'quais turmas eu atendo neste ano',
            'quais disciplinas eu tenho neste ano',
            'quais disciplinas eu atendo neste ano',
        }
    ):
        return True
    if not any(
        _message_matches_term(normalized, term) for term in {'professor', 'professora', 'docente'}
    ):
        return False
    if any(
        _message_matches_term(normalized, term)
        for term in {'meus alunos', 'minhas turmas', 'minhas disciplinas'}
    ):
        return True
    return any(
        _message_matches_term(normalized, term)
        for term in {
            'ja sou',
            'já sou',
            'como verifico',
            'como consulto',
            'como vejo',
            'como acesso',
        }
    )


def _is_public_careers_query(message: str) -> bool:
    normalized = _normalize_text(message)
    if _looks_like_teacher_internal_scope_query(message):
        return False
    if _is_public_capacity_query(message):
        return False
    return any(_message_matches_term(normalized, term) for term in TEACHER_RECRUITMENT_TERMS)


def _is_public_capacity_query(message: str) -> bool:
    normalized = _normalize_text(message)
    has_capacity_signal = any(
        _message_matches_term(normalized, term)
        for term in (
            *PUBLIC_CAPACITY_STUDENT_TERMS,
            *PUBLIC_CAPACITY_PARKING_TERMS,
            'vaga',
            'vagas',
        )
    )
    if not has_capacity_signal:
        return False
    if any(_message_matches_term(normalized, term) for term in PUBLIC_CAPACITY_PARKING_TERMS):
        return True
    if any(_message_matches_term(normalized, term) for term in PUBLIC_CAPACITY_STUDENT_TERMS):
        return True
    if any(_message_matches_term(normalized, term) for term in {'vaga', 'vagas'}):
        if any(
            phrase in normalized
            for phrase in {
                'quantas vagas',
                'quanta vaga',
                'tem vagas',
                'tem vaga',
                'ha vagas',
                'há vagas',
            }
        ):
            return True
        if any(
            _message_matches_term(normalized, term) for term in PUBLIC_CAPACITY_DISAMBIGUATION_TERMS
        ):
            return True
        if any(
            _message_matches_term(normalized, term)
            for term in {
                'trabalhar',
                'trabalhe conosco',
                'dar aula',
                'curriculo',
                'currículo',
                'processo seletivo',
            }
        ):
            return False
    return False


def _is_public_web_query(message: str) -> bool:
    normalized = _normalize_text(message)
    return any(_message_matches_term(normalized, term) for term in PUBLIC_WEB_TERMS)


def _is_public_navigation_query(message: str) -> bool:
    normalized = _normalize_text(message)
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
        'com qual contato eu devo falar',
        'qual contato eu devo usar',
        'qual contato devo usar',
        'por qual canal',
        'como falo com',
        'como falar com',
        'como reporto',
        'como denunciar',
        'quem responde por',
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
    if any(_message_matches_term(normalized, term) for term in ACKNOWLEDGEMENT_TERMS):
        return True
    if any(_message_matches_term(normalized, term) for term in AUTH_GUIDANCE_TERMS):
        return True
    if any(_message_matches_term(normalized, term) for term in ACCESS_SCOPE_TERMS):
        return True
    return any(_message_matches_term(normalized, term) for term in navigation_terms)


def _is_public_operating_hours_query(message: str) -> bool:
    normalized = _normalize_text(message)
    if any(_message_matches_term(normalized, term) for term in PUBLIC_OPERATING_HOURS_TERMS):
        return True
    return _contains_any(
        normalized, {'abre', 'abertura', 'funciona', 'fecha', 'fechamento'}
    ) and _contains_any(
        normalized,
        {'amanha', 'amanhã', 'cedo', 'horas', 'hora', 'horario', 'horário'},
    )


def _compose_language_preference_answer(
    profile: dict[str, Any],
    message: str,
    *,
    conversation_context: dict[str, Any] | None = None,
) -> str:
    normalized = _normalize_text(message)
    school_name = str(profile.get('school_name', 'Colegio Horizonte'))
    if 'admissions' in normalized and any(
        term in normalized for term in {'ingles', 'inglês', 'english'}
    ):
        return (
            f'Voce tem razao em estranhar isso. Aqui no EduAssist do {school_name}, eu vou responder em portugues. '
            'Quando eu mencionar admissions, leia como matricula e atendimento comercial.'
        )
    if any(term in normalized for term in {'portugues', 'português'}) and any(
        term in normalized
        for term in {'fale', 'fala', 'responde', 'responda', 'quero que', 'apenas', 'so', 'só'}
    ):
        return (
            'Perfeito. A partir daqui eu respondo em portugues. '
            'Se eu mencionar admissions, entenda como matricula e atendimento comercial.'
        )
    if _assistant_already_introduced(conversation_context):
        return (
            'Perfeito. Eu sigo em portugues. '
            'Se algum termo sair em ingles, eu reformulo em portugues e explico o setor com nomes locais.'
        )
    return (
        f'Perfeito. Eu sigo em portugues aqui no EduAssist do {school_name}. '
        'Se algum termo sair em ingles, eu reformulo em portugues e explico o setor com nomes locais.'
    )


def _compose_input_clarification_answer(
    profile: dict[str, Any],
    *,
    conversation_context: dict[str, Any] | None = None,
) -> str:
    school_name = str(profile.get('school_name', 'Colegio Horizonte'))
    if _assistant_already_introduced(conversation_context):
        return (
            'Nao consegui interpretar essa mensagem com seguranca. '
            'Se quiser, reformule em uma frase curta dizendo o que voce precisa. '
            'Eu consigo seguir em portugues e normalmente tambem entendo ingles e espanhol. '
            'Se a mensagem era so uma saudacao, pode mandar algo como "oi" ou "bom dia".'
        )
    return (
        f'Nao consegui interpretar essa mensagem com seguranca aqui no EduAssist do {school_name}. '
        'Se quiser, reformule em uma frase curta dizendo o que voce precisa. '
        'Eu consigo seguir em portugues e normalmente tambem entendo ingles e espanhol. '
        'Se a mensagem era so uma saudacao, pode mandar algo como "oi" ou "bom dia".'
    )


def _compose_scope_boundary_answer(
    profile: dict[str, Any],
    *,
    conversation_context: dict[str, Any] | None = None,
) -> str:
    school_name = str(profile.get('school_name', 'Colegio Horizonte'))
    if _assistant_already_introduced(conversation_context):
        return (
            'Nao tenho base confiavel aqui para responder esse tema fora do escopo da escola. '
            'Se quiser, eu posso ajudar com matricula, calendario, regras publicas, visitas, notas, frequencia ou financeiro.'
        )
    return (
        f'Nao tenho base confiavel aqui no EduAssist do {school_name} para responder esse tema fora do escopo da escola. '
        'Se quiser, eu posso ajudar com matricula, calendario, regras publicas, visitas, notas, frequencia ou financeiro.'
    )


def _compose_external_public_facility_boundary_answer(
    profile: dict[str, Any],
    *,
    facility_label: str = 'essa entidade publica externa',
    conversation_context: dict[str, Any] | None = None,
) -> str:
    school_name = str(profile.get('school_name', 'Colegio Horizonte'))
    assistant_prefix = '' if _assistant_already_introduced(conversation_context) else f'No EduAssist do {school_name}, '
    return (
        f'{assistant_prefix}eu consigo responder apenas sobre servicos, documentos e canais da escola. '
        f'Como sua pergunta fala de {facility_label}, esse assunto fica fora do escopo da escola e eu nao tenho base aqui para informar esse dado externo. '
        'Se quiser, eu posso te dizer o equivalente publicado sobre a estrutura ou os canais do colegio.'
    )


def _is_public_calendar_visibility_query(message: str) -> bool:
    normalized = _normalize_text(message)
    if not any(
        _message_matches_term(normalized, term)
        for term in {'eventos do calendario', 'eventos do calendário', 'calendario', 'calendário'}
    ):
        return False
    return any(
        _message_matches_term(normalized, term)
        for term in {
            'publicos',
            'públicos',
            'autenticacao',
            'autenticação',
            'contexto interno',
            'interno',
        }
    )


def _is_public_family_new_calendar_enrollment_query(message: str) -> bool:
    normalized = _normalize_text(message)
    required_groups = (
        {'calendario letivo', 'calendário letivo', 'calendario', 'calendário'},
        {'agenda de avaliacoes', 'agenda de avaliações', 'avaliacoes', 'avaliações', 'simulados'},
        {'manual de matricula', 'manual de matrícula', 'matricula', 'matrícula', 'ingresso'},
    )
    canonical_bundle_match = all(
        any(_message_matches_term(normalized, term) for term in group) for group in required_groups
    )
    onboarding_bundle_match = (
        any(
            _message_matches_term(normalized, term)
            for term in {'portal', 'credenciais', 'secretaria', 'envio de documentos', 'documentos'}
        )
        and any(
            _message_matches_term(normalized, term)
            for term in {
                'inicio das aulas',
                'início das aulas',
                'comeco das aulas',
                'começo das aulas',
                'ordem certa',
            }
        )
        and any(
            _message_matches_term(normalized, term)
            for term in {
                'familia nova',
                'família nova',
                'primeira vez',
                'familia',
                'família',
                'inicio do ano',
                'início do ano',
            }
        )
    )
    if not canonical_bundle_match and not onboarding_bundle_match:
        return False
    return any(
        _message_matches_term(normalized, term)
        for term in {
            'familia nova',
            'família nova',
            'aluno novo',
            'responsavel novo',
            'responsável novo',
        }
    ) or (
        any(
            _message_matches_term(normalized, term)
            for term in {
                'familia',
                'família',
                'casa',
                'primeiro filho',
                'entrando agora',
                'chegando agora',
                'comeco do ano',
                'começo do ano',
                'inicio do ano',
                'início do ano',
            }
        )
        and any(
            _message_matches_term(normalized, term)
            for term in {
                'relacionam',
                'se relacionam',
                'se encaixam',
                'comeco do ano',
                'começo do ano',
            }
        )
    )


def _is_public_health_second_call_query(message: str) -> bool:
    normalized = _normalize_text(message)
    return (
        any(
            _message_matches_term(normalized, term)
            for term in {
                'saude',
                'saúde',
                'motivo de saude',
                'motivo de saúde',
                'atestado',
                'comprovacao',
                'comprovação',
                'justificativa',
            }
        )
        and any(
            _message_matches_term(normalized, term)
            for term in {'segunda chamada', 'perder uma prova', 'perdi uma prova', 'prova'}
        )
        and any(
            _message_matches_term(normalized, term)
            for term in {'recuperacao', 'recuperação', 'avaliacao', 'avaliação', 'segunda chamada'}
        )
    )


def _is_public_permanence_family_query(message: str) -> bool:
    normalized = _normalize_text(message)
    return 'permanencia escolar' in normalized and any(
        _message_matches_term(normalized, term)
        for term in {
            'acompanhamento da familia',
            'acompanhamento da família',
            'responsaveis',
            'responsáveis',
        }
    )


def _is_public_health_authorization_bridge_query(message: str) -> bool:
    normalized = _normalize_text(message)
    required_terms = {
        'saude',
        'saúde',
        'medicacao',
        'medicação',
        'segunda chamada',
        'saidas pedagogicas',
        'saídas pedagógicas',
        'autorizacoes',
        'autorizações',
    }
    hits = sum(1 for term in required_terms if _message_matches_term(normalized, term))
    return hits >= 5


def _is_public_first_month_risks_query(message: str) -> bool:
    normalized = _normalize_text(message)
    return (
        any(
            _message_matches_term(normalized, term)
            for term in {
                'primeiro mes',
                'primeiro mês',
                'comeco do ano',
                'começo do ano',
                'primeiras semanas',
                'arranque do ano',
                'arranque do ano letivo',
                'inicio do ano letivo',
                'início do ano letivo',
            }
        )
        and any(
            _message_matches_term(normalized, term)
            for term in {
                'riscos',
                'esquecido',
                'prazo',
                'prazos',
                'deslizes',
                'descuidos',
                'erros',
                'baguncam',
                'bagunçam',
                'problemas',
                'explodem',
                'explodir',
            }
        )
        and any(
            _message_matches_term(normalized, term)
            for term in {
                'credenciais',
                'documentos',
                'documentacao',
                'documentação',
                'rotina',
                'papelada',
            }
        )
    )


def _is_public_process_compare_query(message: str) -> bool:
    normalized = _normalize_text(message)
    return (
        any(_message_matches_term(normalized, term) for term in {'rematricula', 'rematrícula'})
        and any(
            _message_matches_term(normalized, term)
            for term in {'transferencia', 'transferência', 'cancelamento'}
        )
        and any(
            _message_matches_term(normalized, term)
            for term in {'compare', 'comparar', 'destacando', 'o que muda'}
        )
    )


def _is_public_bolsas_and_processes_query(message: str) -> bool:
    normalized = _normalize_text(message)
    return any(
        _message_matches_term(normalized, term)
        for term in {'bolsa', 'bolsas', 'desconto', 'descontos'}
    ) and any(
        _message_matches_term(normalized, term)
        for term in {'rematricula', 'rematrícula', 'transferencia', 'transferência', 'cancelamento'}
    )


def _resolve_public_profile_act(context: Any) -> str:
    if _is_acknowledgement_query(context.source_message):
        return 'acknowledgement'
    if _looks_like_public_documentary_open_query(context.source_message):
        return 'canonical_fact'
    matched_rule = next(
        iter(
            _prioritize_public_act_rules(
                context.source_message,
                _matched_public_act_rules(
                    context.source_message,
                    conversation_context=context.conversation_context,
                ),
            )
        ),
        None,
    ) or _match_public_act_rule(context.source_message)
    if context.semantic_act and context.semantic_act != 'canonical_fact':
        if matched_rule is not None and matched_rule.name != context.semantic_act:
            return matched_rule.name
        if context.semantic_act in {
            'comparative',
            'highlight',
            'features',
        } and _looks_like_public_documentary_open_query(context.source_message):
            return 'canonical_fact'
        return context.semantic_act
    if matched_rule is not None:
        if matched_rule.name in {
            'comparative',
            'highlight',
            'features',
        } and _looks_like_public_documentary_open_query(context.source_message):
            return 'canonical_fact'
        return matched_rule.name
    return 'canonical_fact'
