from __future__ import annotations

import re
import unicodedata

from .public_bundle_fast_paths import (
    _looks_like_family_new_calendar_enrollment_query,
    _looks_like_first_month_risks_query,
    _looks_like_process_compare_query,
    _looks_like_public_graph_rag_query,
)


def _normalize_text(value: str) -> str:
    text = unicodedata.normalize('NFKD', str(value or ''))
    text = ''.join(char for char in text if not unicodedata.combining(char))
    text = re.sub(r'\s+', ' ', text.lower()).strip()
    return text


def _looks_like_access_scope_query(message: str) -> bool:
    normalized = _normalize_text(message)
    terms = {
        'estou logado como',
        'estou logado como quem',
        'quem sou eu aqui',
        'quais alunos eu tenho vinculados',
        'quais alunos tenho vinculados',
        'quais alunos estao vinculados a esta conta',
        'quais alunos estão vinculados a esta conta',
        'quais alunos estao vinculados nesta conta',
        'quais alunos estão vinculados nesta conta',
        'alunos vinculados',
        'qual meu acesso',
        'qual e o meu escopo',
        'qual é o meu escopo',
        'meu escopo',
        'escopo da minha conta',
        'que dados eu posso ver',
        'que dados posso ver',
        'o que eu consigo ver',
        'o que consigo ver',
        'o que eu consigo ver sobre cada um',
        'o que consigo ver sobre cada aluno',
        'o que posso consultar aqui',
        'qual e exatamente o meu escopo',
        'qual é exatamente o meu escopo',
        'academico, financeiro',
        'acadêmico, financeiro',
        'academico, financeiro ou os dois',
        'acadêmico, financeiro ou os dois',
        'academico e financeiro',
        'acadêmico e financeiro',
        'quais dados eu consigo acessar',
        'quais dados consigo acessar',
        'quais dados dos meus alunos eu consigo acessar',
        'quais dados dos meus dois alunos eu consigo acessar',
        'quais dados dos meus filhos eu consigo acessar',
    }
    return any(term in normalized for term in terms)


def _looks_like_actor_admin_status_query(message: str) -> bool:
    normalized = _normalize_text(message)
    admin_anchor = any(
        term in normalized
        for term in {
            'documentacao',
            'documentação',
            'documental',
            'documentais',
            'cadastro',
            'cadastral',
            'administrativo',
            'administrativa',
        }
    )
    if not admin_anchor:
        return False
    return any(
        term in normalized
        for term in {
            'atualizado',
            'atualizados',
            'regular',
            'regularizado',
            'situacao',
            'situação',
            'ok',
            'checklist',
            'o que falta',
            'falta',
            'pendenc',
            'resuma',
            'resumo',
            'proximo passo',
            'próximo passo',
            'acao recomendada',
            'ação recomendada',
        }
    )


def _looks_like_admin_finance_combo_query(message: str) -> bool:
    normalized = _normalize_text(message)
    admin_terms = {
        'documentacao',
        'documentação',
        'documental',
        'administrativo',
        'administrativa',
        'cadastro',
        'regular',
        'regularidade',
        'pendencia',
        'pendência',
    }
    finance_terms = {
        'financeiro',
        'bloque',
        'bloqueando atendimento',
        'boleto',
        'boletos',
        'mensalidade',
        'mensalidades',
        'fatura',
        'faturas',
    }
    return any(term in normalized for term in admin_terms) and any(term in normalized for term in finance_terms)


def _looks_like_service_routing_query(message: str) -> bool:
    normalized = _normalize_text(message)
    return any(
        term in normalized
        for term in {
            'com quem eu falo sobre',
            'quem responde por',
            'qual setor',
            'qual area',
            'qual área',
            'como falo com',
            'como falar com',
            'como entro em contato',
            'como entrar em contato',
            'como faco para entrar em contato',
            'como faço para entrar em contato',
            'por qual canal',
            'como reporto',
            'como denunciar',
            'como denuncio',
            'onde reporto',
            'onde denuncio',
            'a quem reporto',
            'me diga so os canais',
            'me diga só os canais',
            'canais de',
            'uma linha por setor',
            'qual desses setores entra primeiro',
        }
    )


def _looks_like_public_teacher_identity_query(message: str) -> bool:
    normalized = _normalize_text(message)
    if not any(term in normalized for term in {'prof', 'professor', 'professora', 'docente'}):
        return False
    return any(
        term in normalized
        for term in {
            'nome',
            'telefone',
            'contato',
            'canal',
            'como falar',
            'como falo',
            'falar com',
            'quero falar com',
            'conversar com',
            'falar direto com',
            'falar diretamente com',
        }
    )


def _extract_teacher_subject(message: str) -> str | None:
    normalized = _normalize_text(message)
    patterns = [
        r'prof(?:essor|essora)?\s+de\s+(.+)',
        r'docente\s+de\s+(.+)',
    ]
    for pattern in patterns:
        match = re.search(pattern, normalized)
        if not match:
            continue
        subject = re.split(
            r'\b(?:ou|e|mas|pela?|pelo|se|senao|senão|para)\b|[?!,;.:]',
            match.group(1),
            maxsplit=1,
        )[0].strip(' ?.')
        subject = re.sub(r'\b(?:se nao|senão|senao)\b.*$', '', subject).strip(' ?.')
        if len(subject.split()) > 3:
            subject = ' '.join(subject.split()[:3]).strip(' ?.')
        if subject:
            return subject
    return None


def _looks_like_policy_compare_query(message: str) -> bool:
    normalized = _normalize_text(message)
    return (
        any(term in normalized for term in {'compare', 'comparar', 'comparacao', 'comparação'})
        and any(term in normalized for term in {'regulamentos gerais', 'manual geral', 'manual de regulamentos'})
        and any(term in normalized for term in {'politica de avaliacao', 'política de avaliação', 'avaliacao e promocao'})
    )


def _looks_like_service_credentials_bundle_query(message: str) -> bool:
    normalized = _normalize_text(message)
    if (
        _looks_like_family_new_calendar_enrollment_query(message)
        or _looks_like_first_month_risks_query(message)
        or _looks_like_process_compare_query(message)
    ):
        return False
    has_credentials = any(term in normalized for term in {'credenciais', 'credencial', 'login', 'senha'})
    has_service_anchor = any(term in normalized for term in {'secretaria', 'portal', 'documentos', 'documentacao', 'documentação'})
    return has_credentials and has_service_anchor


def _looks_like_cross_document_public_query(message: str) -> bool:
    normalized = _normalize_text(message)
    has_synthesis_signal = any(
        term in normalized
        for term in {
            'compare',
            'comparar',
            'comparacao',
            'comparação',
            'comparativo',
            'sintetize',
            'relacione',
            'pilares',
            'ponto de vista',
            'quando cruzamos',
            'de ponta a ponta',
            'o que muda',
            'destacando',
        }
    ) or any(
        phrase in normalized
        for phrase in {
            'o que uma familia precisa entender',
            'o que uma família precisa entender',
            'uma unica explicacao coerente',
            'uma única explicação coerente',
            'guia de sobrevivencia do primeiro mes',
            'guia de sobrevivência do primeiro mês',
        }
    )
    if not has_synthesis_signal:
        return False
    return any(
        term in normalized
        for term in {
            'calendario',
            'calendário',
            'agenda',
            'manual',
            'regulamentos',
            'politica',
            'política',
            'proposta pedagogica',
            'proposta pedagógica',
            'portal',
            'credenciais',
            'documentos',
            'rematricula',
            'rematrícula',
            'transferencia',
            'transferência',
            'cancelamento',
            'avaliacao',
            'avaliação',
            'recuperacao',
            'recuperação',
            'vida escolar',
            'inclusao',
            'inclusão',
        }
    )


def _looks_like_public_doc_bundle_request(message: str) -> bool:
    normalized = _normalize_text(message)
    documentary_open = (
        any(
            phrase in normalized
            for phrase in {
                'quero entender',
                'me explique',
                'como a escola',
                'como a familia',
                'como a família',
                'qual imagem institucional',
                'quais evidencias',
                'quais evidências',
                'que evidencias',
                'que evidências',
                'que leitura integrada',
            }
        )
        and sum(
            1
            for term in {
                'inclus',
                'acessib',
                'seguran',
                'apoio',
                'estudo orientado',
                'contraturno',
                'turno estendido',
                'atividade externa',
                'autoriz',
                'transporte',
                'uniforme',
                'refeicao',
                'refeição',
                'governan',
                'lideranca maior',
                'liderança maior',
                'direcao',
                'direção',
                'coordenacao',
                'coordenação',
                'impasse',
                'devolut',
                'recompos',
                'responsaveis',
                'responsáveis',
            }
            if term in normalized
        ) >= 2
    )
    return (
        _looks_like_cross_document_public_query(message)
        or _looks_like_family_new_calendar_enrollment_query(message)
        or _looks_like_public_graph_rag_query(message)
        or _looks_like_service_credentials_bundle_query(message)
        or _looks_like_policy_compare_query(message)
        or documentary_open
    )


def _looks_like_project_of_life_query(message: str) -> bool:
    return 'projeto de vida' in _normalize_text(message)


def _looks_like_attendance_policy_query(message: str) -> bool:
    normalized = _normalize_text(message)
    if not any(term in normalized for term in {'falta', 'faltas', 'frequencia', 'frequência', 'presenca', 'presença'}):
        return False
    return any(
        term in normalized
        for term in {
            'primeira aula',
            'metade das aulas',
            'limite de faltas',
            'limite de frequencia',
            'limite de frequência',
            'frequencia minima',
            'frequência mínima',
            'o que acontece',
            'quantas faltas',
            'abaixo de 75',
            '75%',
        }
    )


def _looks_like_passing_policy_query(message: str) -> bool:
    normalized = _normalize_text(message)
    return any(
        term in normalized
        for term in {
            'nota de aprovacao',
            'nota de aprovação',
            'media de aprovacao',
            'média de aprovação',
            'media para passar',
            'média para passar',
            'qual a nota de aprovacao',
            'qual a nota de aprovação',
            'qual nota preciso tirar para aprovacao',
            'qual nota preciso tirar para aprovação',
        }
    )


def _looks_like_calendar_week_query(message: str) -> bool:
    normalized = _normalize_text(message)
    return (
        any(term in normalized for term in {'calendario publico', 'calendário público', 'calendario', 'calendário', 'eventos'})
        and any(term in normalized for term in {'familias', 'famílias', 'responsaveis', 'responsáveis'})
        and any(term in normalized for term in {'desta semana', 'esta semana', 'mais importantes', 'mais relevantes', 'importantes', 'principais', 'visiveis', 'visíveis'})
    )


def _looks_like_timeline_lifecycle_query(message: str) -> bool:
    normalized = _normalize_text(message)
    has_between_markers = 'marcos entre' in normalized or 'entre matricula' in normalized
    has_enrollment = any(term in normalized for term in {'matricula', 'matrícula', 'vaga', 'vagas'})
    has_school_start = any(term in normalized for term in {'inicio do ano letivo', 'início do ano letivo', 'inicio das aulas', 'início das aulas'})
    has_family_meeting = any(term in normalized for term in {'reuniao de responsaveis', 'reunião de responsáveis', 'reuniao de familias', 'reunião de famílias', 'responsaveis', 'responsáveis'})
    asks_before_after = any(term in normalized for term in {'antes ou depois', 'antes das aulas', 'depois das aulas', 'primeira reuniao', 'primeira reunião'})
    asks_order_only = 'calendario inteiro' in normalized and any(term in normalized for term in {'recorte em ordem', 'so esse recorte', 'só esse recorte'})
    return (
        has_between_markers and has_enrollment and has_school_start and has_family_meeting
    ) or (
        asks_before_after and has_school_start and has_family_meeting
    ) or asks_order_only


def _looks_like_first_bimester_timeline_query(message: str) -> bool:
    normalized = _normalize_text(message)
    return 'primeiro bimestre' in normalized and any(term in normalized for term in {'linha do tempo', 'datas', 'importam'})


def _looks_like_eval_calendar_query(message: str) -> bool:
    normalized = _normalize_text(message)
    return any(term in normalized for term in {'reunioes de pais', 'reuniões de pais', 'simulados', 'semanas de prova', 'semana de prova'})


def _looks_like_travel_planning_query(message: str) -> bool:
    normalized = _normalize_text(message)
    return 'viagem' in normalized and any(term in normalized for term in {'calendario', 'calendário', 'vida escolar', 'marcos'})


def _looks_like_year_three_phases_query(message: str) -> bool:
    normalized = _normalize_text(message)
    return (
        'tres fases' in normalized and all(term in normalized for term in {'admiss', 'rotina', 'fechamento'})
    ) or (
        all(term in normalized for term in {'admiss', 'rotina academica', 'fechamento'})
        and any(term in normalized for term in {'distribui', 'distribui entre', 'olhando so a base publica', 'olhando apenas a base publica', 'se eu dividir o ano', 'dividir o ano'})
    )


def _looks_like_enrollment_documents_query(message: str) -> bool:
    normalized = _normalize_text(message)
    return any(term in normalized for term in {'documentos exigidos', 'documentos sao exigidos', 'documentos são exigidos'}) and 'matricula' in normalized


def _looks_like_public_academic_policy_overview_query(message: str) -> bool:
    normalized = _normalize_text(message)
    return any(term in normalized for term in {'politica de avaliacao', 'política de avaliação', 'recuperacao', 'promoção', 'promocao'}) and 'escola' in normalized


def _looks_like_conduct_frequency_punctuality_query(message: str) -> bool:
    normalized = _normalize_text(message)
    conduct_terms = {
        'convivencia',
        'convivência',
        'frequencia',
        'frequência',
        'pontualidade',
        'bullying',
        'assedio',
        'assédio',
        'agressao',
        'agressão',
        'intimidacao',
        'intimidação',
        'discriminacao',
        'discriminação',
        'bom comportamento',
        'mal comportamento',
        'comportamento',
        'expulsao',
        'expulsão',
        'exclusao',
        'exclusão',
        'desligamento',
        'desligar',
        'bomba',
        'explosivo',
        'explosivos',
        'seguranca',
        'segurança',
    }
    return any(term in normalized for term in conduct_terms)


def _looks_like_bolsas_and_processes_query(message: str) -> bool:
    normalized = _normalize_text(message)
    return any(term in normalized for term in {'bolsas', 'descontos'}) and any(
        term in normalized for term in {'rematricula', 'rematrícula', 'transferencia', 'transferência', 'cancelamento'}
    )


def _looks_like_health_second_call_query(message: str) -> bool:
    normalized = _normalize_text(message)
    return any(term in normalized for term in {'saude', 'saúde', 'atestado', 'motivo de saude', 'motivo de saúde'}) and any(
        term in normalized for term in {'perder uma prova', 'perdi uma prova', 'segunda chamada'}
    )
