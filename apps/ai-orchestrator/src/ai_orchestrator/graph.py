from __future__ import annotations

import re
import unicodedata
from functools import lru_cache
from typing import TypedDict

from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt

from .entity_resolution import resolve_entity_hints
from .models import (
    AccessTier,
    IntentClassification,
    OrchestrationMode,
    OrchestrationPreview,
    OrchestrationRequest,
    QueryDomain,
    RetrievalBackend,
    UserRole,
)
from .public_doc_knowledge import match_public_canonical_lane


class OrchestrationState(TypedDict, total=False):
    request: OrchestrationRequest
    classification: IntentClassification
    route: str
    slice_name: str
    reason: str
    retrieval_backend: str
    selected_tools: list[str]
    citations_required: bool
    needs_authentication: bool
    graph_path: list[str]
    risk_flags: list[str]
    output_contract: str
    hitl_enabled: bool
    hitl_target_slices: list[str]
    hitl_status: str
    hitl_resume_payload: object


class GraphRuntimeConfig(TypedDict):
    graph_rag_enabled: bool


PUBLIC_CALENDAR_TERMS = {'calendario', 'feriado', 'evento', 'prova', 'reuniao', 'formatura'}
ACADEMIC_TERMS = {
    'nota',
    'notas',
    'boletim',
    'frequencia',
    'falta',
    'faltas',
    'avaliacao',
    'avaliacoes',
    'turma',
    'turmas',
    'disciplina',
    'disciplinas',
    'materia',
    'materias',
    'bimestre',
    'media',
    'média',
    'desempenho',
    'vulneravel',
    'vulnerável',
    'componentes',
    'fragilizada',
    'fragilizado',
    'exposta',
    'exposto',
}
ACADEMIC_IDENTITY_TERMS = {
    'qual a matricula',
    'qual a matrícula',
    'minha matricula',
    'minha matrícula',
    'matricula do',
    'matrícula do',
    'codigo de matricula',
    'código de matrícula',
    'numero da matricula',
    'número da matrícula',
    'numero do aluno',
    'número do aluno',
    'codigo do aluno',
    'código do aluno',
    'registro academico',
    'registro acadêmico',
    'ra do aluno',
}
FINANCE_TERMS = {
    'mensalidade',
    'mensalidades',
    'boleto',
    'boletos',
    'financeiro',
    'pagamento',
    'pagamentos',
    'inadimplencia',
    'bolsa',
    'fatura',
    'faturas',
    'conta',
    'contas',
    'pago',
    'pagos',
    'paga',
    'pagas',
    'quitado',
    'quitados',
    'quitada',
    'quitadas',
    'vencido',
    'vencidos',
    'vencida',
    'vencidas',
    'aberto',
    'abertos',
    'pendencia',
    'pendencias',
}
PERSONAL_FINANCE_CONTEXT_TERMS = {
    'meu',
    'minha',
    'meus',
    'minhas',
    'tenho',
    'estou',
    'quero ver',
    'qual proximo pagamento',
    'qual próximo pagamento',
    'proximo pagamento',
    'próximo pagamento',
    'proxima mensalidade',
    'próxima mensalidade',
    'proximo vencimento',
    'próximo vencimento',
    'atrasada',
    'atrasadas',
    'vencida',
    'vencidas',
    'em aberto',
    'situacao financeira',
    'situação financeira',
    'vencimentos',
    'atrasos',
    'proximos passos',
    'próximos passos',
}
PUBLIC_PRICING_TERMS = {
    'mensalidade',
    'mensalidades',
    'valor',
    'valores',
    'preco',
    'precos',
    'preço',
    'preços',
    'bolsa',
    'bolsas',
    'desconto',
    'descontos',
    'taxa de matricula',
    'taxa de matrícula',
}
PUBLIC_WEB_TERMS = {
    'site',
    'site oficial',
    'website',
    'pagina oficial',
    'página oficial',
    'portal institucional',
    'link do site',
    'qual site',
}
PUBLIC_SOCIAL_TERMS = {
    'instagram',
    'insta',
    'rede social',
    'redes sociais',
    'perfil oficial',
    'perfil no instagram',
}
PUBLIC_CAREERS_TERMS = {
    'trabalhar',
    'trabalhe conosco',
    'dar aula',
    'sou professor',
    'sou professora',
    'quero dar aula',
    'quero trabalhar',
    'vaga',
    'vagas',
    'curriculo',
    'currículo',
    'enviar curriculo',
    'enviar currículo',
    'processo seletivo',
}
COMPARATIVE_TERMS = {
    'melhor que',
    'pior que',
    'concorrencia',
    'concorrência',
    'concorrente',
    'comparado com',
    'comparada com',
    'comparar com',
    'comparacao com',
    'comparação com',
    'publica',
    'pública',
    'privada',
    'pagar se posso estudar na publica',
    'pagar se posso estudar na pública',
}
PUBLIC_CURRICULUM_TERMS = {
    'base curricular',
    'bncc',
    'segue a bncc',
    'seguir a bncc',
    'curriculo',
    'currículo',
    'proposta pedagogica',
    'proposta pedagógica',
    'projeto pedagogico',
    'projeto pedagógico',
    'aprendizagem por projetos',
    'componentes curriculares',
    'componente curricular',
    'materias do ensino medio',
    'matérias do ensino médio',
    'materias sao ensinadas',
    'matérias são ensinadas',
    'disciplinas do ensino medio',
    'disciplinas do ensino médio',
}
PUBLIC_OPERATING_HOURS_TERMS = {
    'horario de funcionamento',
    'horário de funcionamento',
    'horario de atendimento',
    'horário de atendimento',
    'que horas abre',
    'que horas fecha',
    'abre amanha',
    'abre amanhã',
    'funciona quando',
}
PUBLIC_LOCATION_TERMS = {
    'endereco',
    'endereço',
    'bairro',
    'qual bairro',
    'em qual bairro',
    'onde fica',
    'localizacao',
    'localização',
    'cep',
}
PUBLIC_UTILITY_TERMS = {
    'que dia e hoje',
    'que dia é hoje',
    'qual a data de hoje',
    'hoje e que dia',
    'hoje é que dia',
}
PERSONAL_FINANCE_TERMS = {
    'meu filho',
    'minha filha',
    'minha conta',
    'meu boleto',
    'meus boletos',
    'minha mensalidade',
    'meu financeiro',
    'minhas faturas',
    'minhas contas',
    'segunda via',
    'fatura',
    'faturas',
    'boleto',
    'boletos',
    'inadimplencia',
    'inadimplência',
    'vencido',
    'vencida',
    'pagamento',
    'pagamentos',
    'quitado',
    'quitada',
    'todos os alunos',
    'todas as mensalidades',
    'de todos os alunos',
    'de todos os estudantes',
    'todos os contratos',
    'lista de mensalidades',
    'planilha de mensalidades',
}
PERSONAL_FINANCE_ATTRIBUTE_TERMS = {
    'numero do boleto',
    'número do boleto',
    'codigo do boleto',
    'código do boleto',
    'identificador do boleto',
    'numero da fatura',
    'número da fatura',
    'codigo do contrato',
    'código do contrato',
    'numero do contrato',
    'número do contrato',
    'contrato financeiro',
}
PERSONAL_ADMIN_TERMS = {
    'documentacao',
    'documentação',
    'documentos',
    'documental',
    'documentais',
    'documentacao atualizada',
    'documentação atualizada',
    'documentacao completa',
    'documentação completa',
    'pendencia documental',
    'pendência documental',
    'pendencias documentais',
    'pendências documentais',
    'meu cadastro',
    'meus dados cadastrais',
    'dados cadastrais',
    'atualizar email',
    'alterar email',
    'mudar email',
    'corrigir email',
    'email no meu cadastro',
    'endereco de email',
    'endereço de email',
    'telefone no cadastro',
}
SUPPORT_TERMS = {'humano', 'atendente', 'suporte', 'protocolo', 'chamado'}
SUPPORT_PHRASES = {
    'atendimento humano',
    'ajuda humana',
    'me transfira',
    'me encaminhe',
    'quero secretaria',
    'quero financeiro',
    'mudei de ideia, quero secretaria',
    'mudei de ideia, quero financeiro',
}
ACKNOWLEDGEMENT_TERMS = {
    'obrigado',
    'obrigada',
    'valeu',
    'perfeito',
    'entendi',
    'beleza',
    'ok',
    'ok obrigado',
    'ok obrigada',
}
AUTH_GUIDANCE_TERMS = {
    'como vinculo minha conta',
    'como vincular minha conta',
    'como faco o vinculo',
    'como faço o vinculo',
    'como fazer o vinculo',
    'como eu vinculo minha conta',
    'como acesso minhas notas aqui',
    'como vejo minhas notas aqui',
    'como consulto meus dados aqui',
}
ACCESS_SCOPE_TERMS = {
    'qual meu acesso',
    'a que dados',
    'que dados eu posso ver',
    'que dados posso ver',
    'o que eu consigo ver',
    'o que consigo ver',
    'o que eu consigo acessar',
    'o que consigo acessar',
    'o que posso consultar aqui',
    'que informacoes consigo obter',
    'que informações consigo obter',
    'qual acesso eu tenho',
}
LINKED_STUDENTS_TERMS = {
    'quais meus filhos',
    'quais sao meus filhos',
    'quais são meus filhos',
    'quem sao meus filhos',
    'quem são meus filhos',
    'quais filhos tenho',
    'filhos matriculados',
    'filhos vinculados',
    'alunos vinculados',
    'quem esta vinculado',
    'quem está vinculado',
}
ACTOR_IDENTITY_TERMS = {
    'estou logado como',
    'com qual nome estou logado',
    'com que nome estou logado',
    'qual nome estou usando aqui',
    'qual meu nome aqui',
    'quem esta logado',
    'quem está logado',
    'quem sou eu aqui',
}
VISIT_ACTION_TERMS = {
    'agendar visita',
    'agendamento de visita',
    'marcar visita',
    'quero visitar',
    'quero conhecer a escola',
    'visita guiada',
    'tour',
}
VISIT_UPDATE_TERMS = {
    'remarcar visita',
    'remarcar a visita',
    'reagendar visita',
    'reagendar a visita',
    'atualizar visita',
    'atualizar a visita',
    'ajustar visita',
    'ajustar a visita',
    'mudar a visita',
    'mudar horario da visita',
    'mudar o horario da visita',
    'mudar horario da minha visita',
    'trocar horario da visita',
    'trocar o horario da visita',
    'trocar o horario',
    'mudar o horario',
    'cancelar visita',
    'cancelar a visita',
    'desmarcar visita',
    'desmarcar a visita',
    'se eu precisar remarcar',
    'e se eu precisar remarcar',
}
INSTITUTIONAL_REQUEST_TERMS = {
    'solicitacao a direcao',
    'solicitação à direção',
    'solicitacao para a direcao',
    'solicitação para a direção',
    'pedido para a diretora',
    'pedido para a direcao',
    'requerimento',
    'protocolar',
    'protocolo formal',
    'ouvidoria',
}
INSTITUTIONAL_REQUEST_UPDATE_TERMS = {
    'complementar pedido',
    'complementar meu pedido',
    'complementar protocolo',
    'complementar minha solicitacao',
    'acrescentar ao protocolo',
    'adicionar ao protocolo',
    'incluir no protocolo',
    'complemente meu pedido',
    'complementa dizendo que',
    'complementar dizendo que',
    'adiciona dizendo que',
    'acrescenta dizendo que',
}
WORKFLOW_STATUS_TERMS = {
    'status',
    'andamento',
    'situacao',
    'situação',
    'como esta',
    'como está',
    'como anda',
    'fila',
    'retorno',
    'atualizacao',
    'atualização',
}
WORKFLOW_REFERENT_TERMS = {
    'protocolo',
    'pedido',
    'solicitacao',
    'solicitação',
    'requerimento',
    'visita',
    'tour',
    'chamado',
    'atendimento',
    'direcao',
    'direção',
    'ouvidoria',
}
WORKFLOW_STATUS_OWNERSHIP_TERMS = {
    'meu pedido',
    'minha solicitacao',
    'minha solicitação',
    'meu protocolo',
    'minha visita',
    'essa solicitacao',
    'essa solicitação',
    'esse pedido',
    'esse protocolo',
    'esse atendimento',
    'essa fila',
}
WORKFLOW_FOLLOW_UP_TERMS = {
    'e agora',
    'e depois',
    'e dai',
    'e daí',
    'tem alguma atualizacao',
    'tem alguma atualização',
    'alguma atualizacao',
    'alguma atualização',
    'qual o prazo',
    'qual o próximo passo',
    'qual o proximo passo',
    'proximo passo',
    'próximo passo',
    'quanto tempo demora',
    'quando me respondem',
    'quando vao me responder',
    'quando vão me responder',
    'quem vai me responder',
    'quem vai retornar',
    'quem fica com isso',
    'o que acontece agora',
    'qual o protocolo',
    'me fala o protocolo',
    'me passa o protocolo',
    'meu protocolo',
    'resume meu pedido',
    'resuma meu pedido',
    'resume pra mim',
    'resuma pra mim',
    'faz um resumo',
    'me da um resumo',
    'o que eu pedi',
    'qual foi meu pedido',
}
RESTRICTED_DOCUMENT_TERMS = {
    'procedimento interno',
    'protocolo interno',
    'manual interno',
    'material interno',
    'playbook interno',
    'orientacao interna',
    'orientação interna',
    'documento interno',
    'documentos internos',
    'por dentro',
}
PROTOCOL_CODE_PATTERN = re.compile(
    r'\b(?:VIS|REQ)-\d{8}-[A-Z0-9]{6}\b|\bATD-\d{8}-[A-Z0-9]{8}\b',
    re.IGNORECASE,
)
GRAPH_RAG_TERMS = {
    'visao geral',
    'compare',
    'comparar',
    'comparacao',
    'comparação',
    'comparativo',
    'tendencias',
    'corpus',
    'relacione',
    'sintetize',
    'pilares',
    'ponto de vista',
    'quando cruzamos',
    'de ponta a ponta',
    'o que muda',
}
GRAPH_RAG_DOCUMENT_TERMS = {
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
TEACHER_SELF_SERVICE_TERMS = {'horario', 'agenda', 'turma', 'turmas', 'disciplina', 'disciplinas', 'materia', 'materias'}
PUBLIC_SERVICE_TERMS = {
    'biblioteca',
    'cantina',
    'laboratorio',
    'laboratorio de ciencias',
    'espaco maker',
    'maker',
    'academia',
    'piscina',
    'quadra',
    'quadra de tenis',
    'tenis',
    'futebol',
    'futsal',
    'volei',
    'esporte',
    'esportes',
    'aula de danca',
    'aulas de danca',
    'danca',
    'atividade extracurricular',
    'atividades extracurriculares',
    'teatro',
    'robotica',
    'robótica',
    'uniforme',
    'almoco',
    'almoço',
    'transporte',
    'van escolar',
    'orientacao educacional',
    'orientação educacional',
    'portaria',
    'secretaria',
    'atendimento',
    'funcionamento',
    'horario de atendimento',
    'o que voce faz',
    'o que você faz',
    'como voce pode me ajudar',
    'como você pode me ajudar',
    'no que voce pode ajudar',
    'no que você pode ajudar',
    'assunto',
    'assuntos',
    'opcoes de assuntos',
    'opções de assuntos',
    'com quem eu falo',
    'pra quem eu falo',
    'para quem eu falo',
    'quem cuida',
    'quem resolve',
    'qual setor',
    'quem e voce',
    'quem é você',
    'voce e quem',
    'você é quem',
    'oi',
    'ola',
    'olá',
    'bom dia',
    'boa tarde',
    'boa noite',
}
INSTITUTION_TERMS = {
    'escola',
    'matricula',
    'documento',
    'documentos',
    'comprovante',
    'comprovantes',
    'historico',
    'historico escolar',
    'cadastro',
    'ficha cadastral',
    'formulario cadastral',
    'regimento',
    'instituicao',
    'endereco',
    'telefone',
    'contato',
    'turno',
    'turnos',
    'horario',
    'horários',
    'horario de aula',
    'horário de aula',
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
    'confessional',
    'laica',
    'religiosa',
    'diretora',
    'diretor',
    'direcao',
    'direção',
    'coordenacao',
    'coordenação',
    'lideranca',
    'liderança',
    'media de aprovacao',
    'média de aprovação',
    'aprovacao',
    'aprovação',
    'indicador',
    'indicadores',
    'curiosidade',
    'curiosidades',
    'diferencial',
    'diferenciais',
    'visita',
    'visitas',
    'tour',
}
PUBLIC_SCHOOL_PROFILE_TERMS = {
    'nome da escola',
    'nome do colegio',
    'nome do colégio',
    'como se chama a escola',
    'como se chama o colegio',
    'como se chama o colégio',
    'telefone da escola',
    'telefone da secretaria',
    'whatsapp da escola',
    'whatsapp da secretaria',
    'email da escola',
    'email da secretaria',
    'fax',
    'site',
    'site oficial',
    'instagram',
    'insta',
    'website',
    'pagina oficial',
    'página oficial',
    'link do site',
    'canais oficiais de contato',
    'canais de contato',
    'como entrar em contato',
    'como ligo',
    'como ligar',
    'ligar para a escola',
    'ligo pra escola',
    'fale conosco',
    'endereco da escola',
    'endereço da escola',
    'horario de funcionamento',
    'horário de funcionamento',
    'que horas abre',
    'que horas fecha',
    'turno',
    'turnos',
    'horario do ensino medio',
    'horário do ensino médio',
    'horario do fundamental',
    'horário do fundamental',
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
    'periodo integral',
    'período integral',
    'mensalidade',
    'mensalidades',
    'bolsa',
    'desconto',
    'confessional',
    'laica',
    'religiosa',
    'diretora',
    'diretor',
    'direcao',
    'direção',
    'coordenacao',
    'coordenação',
    'lideranca',
    'liderança',
    'aprovacao',
    'aprovação',
    'media de aprovacao',
    'média de aprovação',
    'indicador',
    'indicadores',
    'base curricular',
    'curriculo',
    'currículo',
    'componentes curriculares',
    'materias do ensino medio',
    'matérias do ensino médio',
    'disciplinas do ensino medio',
    'disciplinas do ensino médio',
    'segmentos',
    'segmento',
    'quais segmentos',
    'segmentos atendidos',
    'segmentos a escola atende',
    'curiosidade',
    'curiosidades',
    'diferencial',
    'diferenciais',
    'visita',
    'visitas',
    'visita guiada',
    'tour',
    'conhecer a escola',
    'agendar visita',
    'solicitacao a direcao',
    'solicitação à direção',
    'o que voce faz',
    'o que você faz',
    'como voce pode me ajudar',
    'como você pode me ajudar',
    'quais assuntos',
    'opcoes de assuntos',
    'opções de assuntos',
    'com quem eu falo',
    'pra quem eu falo',
    'para quem eu falo',
    'quem cuida',
    'quem resolve',
    'qual setor',
    'quem e voce',
    'quem é você',
    'voce e quem',
    'você é quem',
    'oi',
    'ola',
    'olá',
    'bom dia',
    'boa tarde',
    'boa noite',
    'biblioteca',
    'cantina',
    'laboratorio',
    'academia',
    'piscina',
    'quadra',
    'futebol',
    'danca',
    'dança',
    'teatro',
    'robotica',
    'robótica',
    '30 segundos',
    '30s',
    'familia nova',
    'família nova',
    'por que escolher',
    'por que deveria',
}


def _is_public_web_presence_query(message: str) -> bool:
    lowered = _normalize_text(message)
    return any(_message_matches_term(lowered, term) for term in PUBLIC_WEB_TERMS)


def _is_public_social_query(message: str) -> bool:
    lowered = _normalize_text(message)
    return any(_message_matches_term(lowered, term) for term in PUBLIC_SOCIAL_TERMS)


def _is_public_careers_query(message: str) -> bool:
    lowered = _normalize_text(message)
    return any(_message_matches_term(lowered, term) for term in PUBLIC_CAREERS_TERMS)


def _is_public_comparative_query(message: str) -> bool:
    lowered = _normalize_text(message)
    return any(_message_matches_term(lowered, term) for term in COMPARATIVE_TERMS)


def _is_public_curriculum_query(message: str) -> bool:
    lowered = _normalize_text(message)
    if any(_message_matches_term(lowered, term) for term in PUBLIC_CURRICULUM_TERMS):
        return True
    if _message_matches_term(lowered, 'acolhimento') and any(
        _message_matches_term(lowered, term)
        for term in {'disciplina', 'disciplinas', 'convivencia', 'convivência', 'aprendizagem', 'rotina'}
    ):
        return True
    return any(_message_matches_term(lowered, term) for term in {'materia', 'materias', 'disciplina', 'disciplinas'}) and any(
        _message_matches_term(lowered, term)
        for term in {
            'ensino medio',
            'ensino médio',
            'fundamental',
            'fundamental i',
            'fundamental ii',
            'anos iniciais',
            'base curricular',
            'curriculo',
            'currículo',
        }
    )


def _is_public_policy_query(message: str) -> bool:
    lowered = _normalize_text(message)
    explicit_terms = {
        'politica de avaliacao',
        'política de avaliação',
        'avaliacao, recuperacao e promocao',
        'avaliação, recuperação e promoção',
        'media de aprovacao',
        'média de aprovação',
        'nota de aprovacao',
        'nota de aprovação',
        'projeto de vida',
        'frequencia minima',
        'frequência mínima',
        '75%',
    }
    if any(_message_matches_term(lowered, term) for term in explicit_terms):
        return True
    if any(
        _message_matches_term(lowered, term)
        for term in {'avaliacao', 'avaliação', 'recuperacao', 'recuperação', 'promocao', 'promoção', 'aprovacao', 'aprovação'}
    ):
        return any(
            _message_matches_term(lowered, term)
            for term in {'politica', 'política', 'como funciona', 'regra', 'regras', 'funciona'}
        )
    if any(_message_matches_term(lowered, term) for term in {'falta', 'faltas', 'frequencia', 'frequência'}):
        return any(
            _message_matches_term(lowered, term)
            for term in {'politica', 'política', 'regra', 'regras', '75%', 'minima', 'mínima', 'o que acontece'}
        )
    return False


def _is_public_operating_hours_query(message: str) -> bool:
    lowered = _normalize_text(message)
    if any(_message_matches_term(lowered, term) for term in PUBLIC_OPERATING_HOURS_TERMS):
        return True
    return _contains_any(lowered, {'abre', 'abertura', 'funciona', 'fecha', 'fechamento'}) and _contains_any(
        lowered,
        {'amanha', 'amanhã', 'cedo', 'horas', 'hora', 'horario', 'horário'},
    )


def _is_public_location_query(message: str) -> bool:
    lowered = _normalize_text(message)
    return any(_message_matches_term(lowered, term) for term in PUBLIC_LOCATION_TERMS)


def _is_public_contact_phrase_query(message: str) -> bool:
    lowered = _normalize_text(message)
    return any(
        _message_matches_term(lowered, term)
        for term in {'como ligo', 'como ligar', 'ligo pra escola', 'ligar para a escola', 'numero da escola', 'número da escola'}
    )


def _is_public_contact_channel_query(message: str) -> bool:
    lowered = _normalize_text(message)
    return any(
        _message_matches_term(lowered, term)
        for term in {
            'telefone da escola',
            'telefone do colegio',
            'telefone do colégio',
            'numero do telefone',
            'número do telefone',
            'qual o telefone',
            'qual telefone',
            'fax',
            'caixa postal',
            'whatsapp da escola',
            'email da escola',
        }
    )


def _is_public_utility_query(message: str) -> bool:
    lowered = _normalize_text(message)
    return any(_message_matches_term(lowered, term) for term in PUBLIC_UTILITY_TERMS)


def _append_path(state: OrchestrationState, node_name: str) -> list[str]:
    return [*state.get('graph_path', []), node_name]


def _append_unique_risk_flags(state: OrchestrationState, *flags: str) -> list[str]:
    existing: list[str] = []
    seen_existing: set[str] = set()
    for flag in state.get('risk_flags', []):
        normalized = str(flag).strip()
        if not normalized or normalized in seen_existing:
            continue
        existing.append(normalized)
        seen_existing.add(normalized)
    seen = set(existing)
    for flag in flags:
        normalized = str(flag).strip()
        if not normalized or normalized in seen:
            continue
        existing.append(normalized)
        seen.add(normalized)
    return existing


def _normalize_text(text: str) -> str:
    normalized = unicodedata.normalize('NFKD', text)
    without_accents = ''.join(char for char in normalized if not unicodedata.combining(char))
    return without_accents.replace('º', 'o').replace('ª', 'a').lower()


def _message_matches_term(message: str, term: str) -> bool:
    normalized_term = _normalize_text(term).strip()
    if not normalized_term:
        return False
    pattern = r'(?<!\w)' + r'\s+'.join(re.escape(part) for part in normalized_term.split()) + r'(?!\w)'
    return re.search(pattern, message) is not None


def _contains_any(message: str, terms: set[str]) -> bool:
    lowered = _normalize_text(message)
    return any(_message_matches_term(lowered, term) for term in terms)


def _is_restricted_document_query(message: str) -> bool:
    normalized = _normalize_text(message)
    if any(
        _message_matches_term(normalized, term)
        for term in {
            'sem recorrer a material interno',
            'sem precisar recorrer a material interno',
            'sem recorrer a documentos internos',
            'sem precisar recorrer a documentos internos',
        }
    ):
        return False
    return any(_message_matches_term(normalized, term) for term in RESTRICTED_DOCUMENT_TERMS)


def _can_read_restricted_documents(request: OrchestrationRequest) -> bool:
    role = str(getattr(request.user.role, 'value', request.user.role) or '').strip().lower()
    scopes = {str(item).strip().lower() for item in request.user.scopes}
    return bool(
        request.user.authenticated
        and (
            'documents:private:read' in scopes
            or 'documents:restricted:read' in scopes
            or role in {'staff', 'teacher'}
        )
    )


def _wants_human_support(message: str) -> bool:
    lowered = _normalize_text(message)
    return any(term in lowered for term in SUPPORT_TERMS) or any(
        phrase in lowered for phrase in SUPPORT_PHRASES
    )


def _is_visit_booking_request(message: str) -> bool:
    lowered = _normalize_text(message)
    if any(_message_matches_term(lowered, term) for term in VISIT_ACTION_TERMS):
        return True
    scheduling_verbs = {'agendar', 'agendamento', 'marcar', 'reservar', 'visitar', 'conhecer'}
    visit_targets = {
        'visita',
        'visita guiada',
        'tour',
        'conhecer a escola',
        'conhecer o colegio',
        'conhecer o colégio',
        'visitar a escola',
        'visitar o colegio',
        'visitar o colégio',
    }
    return _contains_any(lowered, scheduling_verbs) and _contains_any(lowered, visit_targets)


def _is_visit_booking_update_request(message: str) -> bool:
    lowered = _normalize_text(message)
    if any(_message_matches_term(lowered, term) for term in VISIT_UPDATE_TERMS):
        return True
    reschedule_verbs = {'remarcar', 'reagendar', 'mudar', 'trocar'}
    cancel_verbs = {'cancelar', 'desmarcar'}
    visit_targets = {'visita', 'visita guiada', 'tour'}
    if any(_message_matches_term(lowered, phrase) for phrase in {'se eu precisar remarcar', 'e se eu precisar remarcar'}):
        return True
    return (_contains_any(lowered, reschedule_verbs) or _contains_any(lowered, cancel_verbs)) and _contains_any(
        lowered,
        visit_targets,
    )


def _is_institutional_request(message: str) -> bool:
    lowered = _normalize_text(message)
    if any(_message_matches_term(lowered, term) for term in INSTITUTIONAL_REQUEST_TERMS):
        return True
    request_verbs = {'solicitar', 'solicitacao', 'solicitação', 'protocolar', 'encaminhar', 'formalizar'}
    leadership_targets = {'direcao', 'direção', 'diretora', 'diretor', 'ouvidoria'}
    return _contains_any(lowered, request_verbs) and _contains_any(lowered, leadership_targets)


def _is_institutional_request_update(message: str) -> bool:
    lowered = _normalize_text(message)
    if any(_message_matches_term(lowered, term) for term in INSTITUTIONAL_REQUEST_UPDATE_TERMS):
        return True
    update_verbs = {'complementar', 'completar', 'acrescentar', 'adicionar', 'incluir'}
    referents = {'pedido', 'solicitacao', 'solicitação', 'protocolo', 'requerimento'}
    if any(_message_matches_term(lowered, phrase) for phrase in {'complementa dizendo que', 'complementar dizendo que', 'adiciona dizendo que', 'acrescenta dizendo que'}):
        return True
    return _contains_any(lowered, update_verbs) and _contains_any(lowered, referents)


def _has_protocol_code(message: str) -> bool:
    return PROTOCOL_CODE_PATTERN.search(message) is not None


def _is_workflow_status_request(message: str) -> bool:
    lowered = _normalize_text(message)
    if _has_protocol_code(message) and _contains_any(lowered, WORKFLOW_STATUS_TERMS | {'protocolo'}):
        return True
    if _contains_any(lowered, WORKFLOW_FOLLOW_UP_TERMS):
        return True
    if _contains_any(lowered, WORKFLOW_STATUS_TERMS) and _contains_any(
        lowered,
        WORKFLOW_REFERENT_TERMS | WORKFLOW_STATUS_OWNERSHIP_TERMS,
    ):
        return True
    return False


def _is_structured_support_workflow_request(message: str) -> bool:
    return (
        _is_visit_booking_request(message)
        or _is_visit_booking_update_request(message)
        or _is_institutional_request_update(message)
        or _is_institutional_request(message)
        or _is_workflow_status_request(message)
    )


def _is_teacher_self_service_request(message: str, role: UserRole) -> bool:
    lowered = _normalize_text(message)
    return role is UserRole.teacher and any(term in lowered for term in TEACHER_SELF_SERVICE_TERMS)


def _is_public_pricing_query(message: str) -> bool:
    lowered = _normalize_text(message)
    hints = resolve_entity_hints(message)
    has_public_pricing_terms = any(_message_matches_term(lowered, term) for term in PUBLIC_PRICING_TERMS)
    if not has_public_pricing_terms:
        has_public_pricing_terms = (
            hints.is_hypothetical
            and bool(hints.quantity_hint)
            and any(_message_matches_term(lowered, term) for term in {'matricula', 'matrícula'})
        )
    if not has_public_pricing_terms:
        return False
    if any(_message_matches_term(lowered, term) for term in PERSONAL_FINANCE_TERMS):
        return False
    if any(_message_matches_term(lowered, term) for term in PERSONAL_FINANCE_CONTEXT_TERMS):
        return False
    return True


def _is_authenticated_personal_finance_query(message: str, *, authenticated: bool) -> bool:
    if not authenticated:
        return False
    lowered = _normalize_text(message)
    if any(
        _message_matches_term(lowered, term)
        for term in {
            'situacao financeira da familia',
            'situação financeira da família',
            'situacao financeira atual da familia',
            'situação financeira atual da família',
            'resuma a situacao financeira',
            'resuma a situação financeira',
            'quadro financeiro da familia',
            'quadro financeiro da família',
            'vencimentos',
            'por vencer',
            'vence',
            'venceu',
            'atrasos',
            'proximos passos',
            'próximos passos',
        }
    ):
        return True
    if not any(_message_matches_term(lowered, term) for term in FINANCE_TERMS):
        return False
    if any(_message_matches_term(lowered, term) for term in PERSONAL_FINANCE_TERMS):
        return True
    return any(_message_matches_term(lowered, term) for term in PERSONAL_FINANCE_CONTEXT_TERMS)


def _is_public_timeline_query(message: str) -> bool:
    lowered = _normalize_text(message)
    if (
        any(_message_matches_term(lowered, term) for term in {'antes da confirmacao da vaga', 'antes da confirmação da vaga', 'depois do inicio das aulas', 'depois do início das aulas'})
        or ('viagem' in lowered and any(_message_matches_term(lowered, term) for term in {'calendario', 'calendário', 'marcos', 'vida escolar'}))
        or ('tres fases' in lowered and all(term in lowered for term in {'admiss', 'rotina', 'fechamento'}))
    ):
        return True
    asks_timing = any(
        _message_matches_term(lowered, term)
        for term in {
            'quando',
            'qual data',
            'que dia',
            'quando comeca',
            'quando começa',
            'comeco',
            'começo',
            'quando fecha',
            'inicio',
            'início',
            'abertura',
            'comeco das aulas',
            'começo das aulas',
            'comecam as aulas',
            'começam as aulas',
        }
    )
    if not asks_timing:
        return False
    return any(
        _message_matches_term(lowered, term)
        for term in {
            'matricula',
            'matrícula',
            'formatura',
            'inicio das aulas',
            'início das aulas',
            'comeco das aulas',
            'começo das aulas',
            'comecam as aulas',
            'começam as aulas',
            'ano letivo',
        }
    )


def _is_public_calendar_event_query(message: str) -> bool:
    lowered = _normalize_text(message)
    if any(
        _message_matches_term(lowered, term)
        for term in {
            'proximo evento',
            'próximo evento',
            'proxima reuniao',
            'próxima reunião',
            'reuniao de pais',
            'reunião de pais',
            'mostra de ciencias',
            'mostra de ciências',
            'plantao pedagogico',
            'plantão pedagógico',
            'visita guiada',
        }
    ):
        return True
    asks_timing = any(
        _message_matches_term(lowered, term)
        for term in {'quando', 'qual data', 'que dia', 'quando vai ser', 'quando acontece'}
    )
    if not asks_timing:
        return False
    return any(
        _message_matches_term(lowered, term)
        for term in {
            'reuniao',
            'reunião',
            'evento',
            'mostra',
            'feira',
            'plantao',
            'plantão',
            'visita guiada',
            'cerimonia',
            'cerimônia',
        }
    )


def _is_public_navigation_query(message: str) -> bool:
    lowered = _normalize_text(message)
    navigation_terms = {
        'oi',
        'ola',
        'olá',
        'bom dia',
        'boa tarde',
        'boa noite',
        'o que voce faz',
        'o que você faz',
        'o que esta fazendo',
        'o que está fazendo',
        'o que ta fazendo',
        'o que tá fazendo',
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
        'qual a diferenca entre falar com',
        'qual a diferença entre falar com',
        'diferenca entre secretaria',
        'diferença entre secretaria',
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
    if any(_message_matches_term(lowered, term) for term in ACKNOWLEDGEMENT_TERMS):
        return True
    if any(_message_matches_term(lowered, term) for term in AUTH_GUIDANCE_TERMS):
        return True
    if any(_message_matches_term(lowered, term) for term in ACCESS_SCOPE_TERMS):
        return True
    return any(_message_matches_term(lowered, term) for term in navigation_terms)


def _is_public_staff_directory_query(message: str) -> bool:
    lowered = _normalize_text(message)
    if not any(
        _message_matches_term(lowered, term)
        for term in {'prof', 'professor', 'professora', 'docente'}
    ):
        return False
    return any(
        _message_matches_term(lowered, term)
        for term in {'nome', 'contato', 'telefone', 'whatsapp', 'whats', 'email', 'fale com'}
    )


def _is_cross_document_public_query(message: str) -> bool:
    if (
        _is_public_policy_compare_query(message)
        or _is_public_family_new_calendar_enrollment_query(message)
        or _is_public_service_credentials_bundle_query(message)
        or _is_public_permanence_family_query(message)
        or _is_public_first_month_risks_query(message)
        or _is_public_process_compare_query(message)
    ):
        return False
    lowered = _normalize_text(message)
    has_synthesis_signal = any(_message_matches_term(lowered, term) for term in GRAPH_RAG_TERMS) or any(
        phrase in lowered
        for phrase in (
            'o que uma familia precisa entender',
            'o que uma família precisa entender',
            'uma unica explicacao coerente',
            'uma única explicação coerente',
            'temas atravessam varios documentos',
            'temas atravessam vários documentos',
            'guia de sobrevivencia do primeiro mes',
            'guia de sobrevivência do primeiro mês',
        )
    )
    if not has_synthesis_signal:
        return False
    return any(_message_matches_term(lowered, term) for term in GRAPH_RAG_DOCUMENT_TERMS)


def _is_public_policy_compare_query(message: str) -> bool:
    lowered = _normalize_text(message)
    mentions_compare = any(
        _message_matches_term(lowered, term)
        for term in {'compare', 'comparar', 'comparacao', 'comparação', 'como os dois se complementam'}
    )
    mentions_general_rules = any(
        _message_matches_term(lowered, term)
        for term in {'manual de regulamentos gerais', 'regulamentos gerais', 'manual geral'}
    )
    mentions_eval_policy = any(
        _message_matches_term(lowered, term)
        for term in {'politica de avaliacao', 'política de avaliação', 'avaliacao e promocao', 'avaliação e promoção'}
    )
    return mentions_compare and mentions_general_rules and mentions_eval_policy


def _is_public_family_new_calendar_enrollment_query(message: str) -> bool:
    lowered = _normalize_text(message)
    required_groups = (
        {'calendario letivo', 'calendário letivo', 'calendario', 'calendário'},
        {'agenda de avaliacoes', 'agenda de avaliações', 'avaliacoes', 'avaliações', 'simulados'},
        {'manual de matricula', 'manual de matrícula', 'matricula', 'matrícula', 'ingresso'},
    )
    if not all(any(_message_matches_term(lowered, term) for term in group) for group in required_groups):
        return False
    return any(
        _message_matches_term(lowered, term)
        for term in {
            'familia nova',
            'família nova',
            'aluno novo',
            'responsavel novo',
            'responsável novo',
            'primeira vez',
            'vai entrar este ano',
            'vai entrar pela primeira vez',
        }
    ) or (
        any(
            _message_matches_term(lowered, term)
            for term in {'familia', 'família', 'responsaveis', 'responsáveis', 'casa', 'primeiro filho'}
        )
        and any(
            _message_matches_term(lowered, term)
            for term in {'entrando agora', 'chegando agora', 'inicio do ano', 'início do ano', 'primeiro bimestre', 'comeco do ano', 'começo do ano'}
        )
    )


def _is_public_service_credentials_bundle_query(message: str) -> bool:
    lowered = _normalize_text(message)
    if (
        'credenciais' not in lowered
        and 'credencial' not in lowered
        and 'login' not in lowered
        and 'senha' not in lowered
        and 'aplicativo' not in lowered
        and 'app' not in lowered
    ):
        return False
    return any(
        _message_matches_term(lowered, term)
        for term in {'secretaria', 'portal', 'aplicativo', 'app', 'documentos', 'documentacao', 'documentação', 'cadastro'}
    )


def _is_public_permanence_family_query(message: str) -> bool:
    lowered = _normalize_text(message)
    family_terms = {
        'acompanhamento da familia',
        'acompanhamento da família',
        'familia',
        'família',
        'responsaveis',
        'responsáveis',
        'acompanhe',
    }
    permanence_terms = {
        'permanencia',
        'permanência',
        'vida escolar',
        'apoio',
        'orientacao',
        'orientação',
    }
    return (
        any(_message_matches_term(lowered, term) for term in family_terms)
        and sum(1 for term in permanence_terms if _message_matches_term(lowered, term)) >= 2
    )


def _is_public_first_month_risks_query(message: str) -> bool:
    lowered = _normalize_text(message)
    return any(
        _message_matches_term(lowered, term)
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
    ) and any(
        _message_matches_term(lowered, term)
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
    ) and any(
        _message_matches_term(lowered, term)
        for term in {'credenciais', 'documentos', 'documentacao', 'documentação', 'rotina', 'papelada'}
    )


def _is_public_process_compare_query(message: str) -> bool:
    lowered = _normalize_text(message)
    return any(_message_matches_term(lowered, term) for term in {'rematricula', 'rematrícula'}) and any(
        _message_matches_term(lowered, term) for term in {'transferencia', 'transferência', 'cancelamento'}
    ) and any(
        _message_matches_term(lowered, term) for term in {'compare', 'comparar', 'destacando', 'o que muda'}
    )


def _is_public_health_second_call_query(message: str) -> bool:
    lowered = _normalize_text(message)
    return (
        any(_message_matches_term(lowered, term) for term in {'saude', 'saúde', 'atestado', 'atestado medico', 'atestado médico'})
        and any(_message_matches_term(lowered, term) for term in {'segunda chamada', 'segunda', 'recuperacao', 'recuperação'})
    )


def _is_public_conduct_frequency_recovery_query(message: str) -> bool:
    lowered = _normalize_text(message)
    return (
        any(_message_matches_term(lowered, term) for term in {'disciplina', 'regulamentos', 'regulamento', 'convivencia', 'convivência'})
        and any(_message_matches_term(lowered, term) for term in {'frequencia', 'frequência'})
        and any(_message_matches_term(lowered, term) for term in {'recuperacao', 'recuperação'})
    )


def _is_public_transversal_year_query(message: str) -> bool:
    lowered = _normalize_text(message)
    return (
        any(
            _message_matches_term(lowered, term)
            for term in {
                'responsaveis',
                'responsáveis',
                'responsavel',
                'responsável',
                'familia',
                'família',
                'comunicacao com responsaveis',
                'comunicação com responsáveis',
            }
        )
        and any(
            _message_matches_term(lowered, term)
            for term in {
                'avaliacoes',
                'avaliações',
                'avaliacao',
                'avaliação',
                'agenda avaliativa',
                'agenda de avaliacoes',
                'agenda de avaliações',
            }
        )
        and any(
            _message_matches_term(lowered, term)
            for term in {
                'estudo orientado',
                'canais digitais',
                'portal',
                'telegram',
                'digitais',
                'meios digitais',
                'meios oficiais',
                'canais oficiais',
                'comunicacao digital',
                'comunicação digital',
            }
        )
    )


def _is_public_facilities_study_query(message: str) -> bool:
    lowered = _normalize_text(message)
    return (
        any(_message_matches_term(lowered, term) for term in {'biblioteca', 'laboratorios', 'laboratórios', 'laboratorio', 'laboratório'})
        and any(_message_matches_term(lowered, term) for term in {'estudo', 'apoio', 'ensino medio', 'ensino médio'})
    )


def _is_public_calendar_visibility_bundle_query(message: str) -> bool:
    lowered = _normalize_text(message)
    if not any(
        _message_matches_term(lowered, term)
        for term in {'portal', 'canais digitais', 'canais da escola', 'canais oficiais', 'calendario', 'calendário'}
    ):
        return False
    return any(
        _message_matches_term(lowered, term)
        for term in {
            'autenticacao',
            'autenticação',
            'autenticado',
            'autenticada',
            'login',
            'senha',
            'publico',
            'público',
            'conteudo publico',
            'conteúdo público',
            'publica',
            'pública',
            'aparece depois',
            'onde termina',
            'onde comeca',
            'onde começa',
            'sem autenticacao',
            'sem autenticação',
        }
    )


def _is_known_public_doc_bundle_query(message: str) -> bool:
    return (
        match_public_canonical_lane(message) is not None
        or (
        _is_public_policy_compare_query(message)
        or _is_public_family_new_calendar_enrollment_query(message)
        or _is_public_calendar_visibility_bundle_query(message)
        or _is_public_service_credentials_bundle_query(message)
        or _is_public_permanence_family_query(message)
        or _is_public_first_month_risks_query(message)
        or _is_public_process_compare_query(message)
        or _is_public_health_second_call_query(message)
        or _is_public_conduct_frequency_recovery_query(message)
        or _is_public_transversal_year_query(message)
        or _is_public_facilities_study_query(message)
        )
    )


def _is_admin_finance_combined_query(message: str) -> bool:
    lowered = _normalize_text(message)
    mentions_admin = any(_message_matches_term(lowered, term) for term in PERSONAL_ADMIN_TERMS) or any(
        _message_matches_term(lowered, term)
        for term in {'regular', 'regularidade', 'administrativo', 'administrativa'}
    )
    mentions_finance = any(_message_matches_term(lowered, term) for term in FINANCE_TERMS) or any(
        _message_matches_term(lowered, term)
        for term in PERSONAL_FINANCE_CONTEXT_TERMS
    )
    return mentions_admin and mentions_finance


def _is_public_school_profile_request(message: str) -> bool:
    lowered = _normalize_text(message)
    if _is_public_timeline_query(lowered):
        return False
    if _is_cross_document_public_query(lowered):
        return False
    return (
        _is_public_pricing_query(lowered)
        or _is_public_feature_query(lowered)
        or _is_public_social_query(lowered)
        or _is_public_careers_query(lowered)
        or _is_public_comparative_query(lowered)
        or _is_public_staff_directory_query(lowered)
        or _is_public_document_submission_query(lowered)
        or _is_public_web_presence_query(lowered)
        or _is_public_curriculum_query(lowered)
        or _is_public_policy_query(lowered)
        or _is_public_policy_compare_query(lowered)
        or _is_public_family_new_calendar_enrollment_query(lowered)
        or _is_public_calendar_visibility_bundle_query(lowered)
        or _is_public_service_credentials_bundle_query(lowered)
        or _is_public_permanence_family_query(lowered)
        or _is_public_first_month_risks_query(lowered)
        or _is_public_process_compare_query(lowered)
        or _is_public_health_second_call_query(lowered)
        or _is_public_conduct_frequency_recovery_query(lowered)
        or _is_public_transversal_year_query(lowered)
        or _is_public_facilities_study_query(lowered)
        or _is_public_operating_hours_query(lowered)
        or _is_public_location_query(lowered)
        or _is_public_contact_phrase_query(lowered)
        or _is_public_contact_channel_query(lowered)
        or any(_message_matches_term(lowered, term) for term in PUBLIC_SCHOOL_PROFILE_TERMS)
    )


def _is_public_document_submission_query(message: str) -> bool:
    lowered = _normalize_text(message)
    explicit_terms = {
        'documentos online',
        'documento online',
        'envio de documentos',
        'enviar documentos',
        'mandar documentos',
        'envio digital',
        'aceita documentos online',
        'aceita envio online',
        'aceita envio digital',
        'por onde envio meus documentos',
        'como envio meus documentos',
        'canal de documentos',
        'enviar por fax',
        'mandar por fax',
        'enviar por telegrama',
        'mandar por telegrama',
        'enviar por caixa postal',
        'mandar por caixa postal',
        'posso enviar por fax',
        'posso enviar documentos por fax',
        'posso mandar documentos por fax',
        'posso mandar por telegrama',
        'posso enviar por telegrama',
        'prazos e canais da secretaria',
        'prazo da secretaria para documentos',
        'prazos para secretaria receber documentos',
        'canais da secretaria para documentos',
        'declaracoes e atualizacoes cadastrais',
        'declarações e atualizações cadastrais',
        'atualizacoes cadastrais',
        'atualizações cadastrais',
    }
    if any(_message_matches_term(lowered, term) for term in explicit_terms):
        return True
    document_terms = {'documento', 'documentos', 'matricula', 'matrícula', 'cadastro'}
    digital_terms = {'online', 'digital', 'portal', 'email', 'e-mail', 'enviar', 'envio'}
    special_channel_terms = {'fax', 'telegrama', 'caixa postal'}
    if any(_message_matches_term(lowered, term) for term in document_terms) and any(
        _message_matches_term(lowered, term) for term in special_channel_terms
    ):
        return True
    return any(_message_matches_term(lowered, term) for term in document_terms) and any(
        _message_matches_term(lowered, term) for term in digital_terms
    )


def _is_public_feature_query(message: str) -> bool:
    lowered = _normalize_text(message)
    feature_terms = {
        'biblioteca',
        'cantina',
        'laboratorio',
        'maker',
        'espaco maker',
        'academia',
        'piscina',
        'quadra',
        'quadra de tenis',
        'futebol',
        'futsal',
        'volei',
        'vôlei',
        'danca',
        'dança',
        'teatro',
        'robotica',
        'robótica',
        'orientacao educacional',
        'orientação educacional',
    }
    if any(_message_matches_term(lowered, term) for term in feature_terms):
        return True
    return any(
        _message_matches_term(lowered, term)
        for term in {
            'estrutura',
            'infraestrutura',
            'espaco',
            'espaço',
            'espacos',
            'espaços',
            'campus',
            'aula de',
            'oficina de',
            'curso de',
            'atividade de',
            'clube de',
            'atividade',
            'atividades',
            'contraturno',
            'aulas complementares',
            'atividades complementares',
            'complementares',
            'monitoria',
            'monitorias',
            'plantao',
            'plantão',
            'estudo orientado',
            'trilhas',
            'trilhas academicas',
            'trilhas acadêmicas',
        }
    )


def _is_public_attribute_followup_query(message: str) -> bool:
    lowered = _normalize_text(message)
    attribute_terms = {
        'email',
        'e-mail',
        'telefone',
        'fone',
        'whatsapp',
        'whats',
        'zap',
        'horario',
        'horário',
        'funciona quando',
    }
    if not any(_message_matches_term(lowered, term) for term in attribute_terms):
        return False
    return lowered.startswith('e ') or ' sobre ' in lowered


def _is_authenticated_admin_query(message: str, *, authenticated: bool) -> bool:
    if not authenticated:
        return False
    lowered = _normalize_text(message)
    if _is_public_contact_phrase_query(lowered) or _is_public_contact_channel_query(lowered):
        return False
    admin_markers_present = any(
        _message_matches_term(lowered, term)
        for term in {
            'documentacao',
            'documentação',
            'documentos',
            'documental',
            'documentais',
            'status documental',
            'pendencia documental',
            'pendência documental',
            'pendencias documentais',
            'pendências documentais',
            'pendencia administrativa',
            'pendência administrativa',
            'pendencias administrativas',
            'pendências administrativas',
            'cadastro',
            'dados cadastrais',
            'email',
            'telefone',
            'proximo passo',
            'próximo passo',
            'proximo passo recomendado',
            'próximo passo recomendado',
            'exige acao',
            'exigem acao',
        }
    ) or any(_message_matches_term(lowered, term) for term in PERSONAL_ADMIN_TERMS)
    if any(_message_matches_term(lowered, term) for term in FINANCE_TERMS) and not admin_markers_present:
        return False
    if (_message_matches_term(lowered, 'matricula') or _message_matches_term(lowered, 'matrícula')) and not admin_markers_present:
        return False
    if admin_markers_present:
        return True
    return False


def _is_authenticated_actor_identity_query(message: str, *, authenticated: bool) -> bool:
    if not authenticated:
        return False
    lowered = _normalize_text(message)
    return any(_message_matches_term(lowered, term) for term in ACTOR_IDENTITY_TERMS)


def _is_authenticated_access_scope_query(message: str, *, authenticated: bool) -> bool:
    if not authenticated:
        return False
    lowered = _normalize_text(message)
    return any(_message_matches_term(lowered, term) for term in ACCESS_SCOPE_TERMS)


def _is_authenticated_linked_students_query(message: str, *, authenticated: bool) -> bool:
    if not authenticated:
        return False
    lowered = _normalize_text(message)
    return any(_message_matches_term(lowered, term) for term in LINKED_STUDENTS_TERMS)


def _is_authenticated_student_assessment_query(message: str, *, authenticated: bool) -> bool:
    if not authenticated:
        return False
    lowered = _normalize_text(message)
    if _is_cross_document_public_query(lowered) or _is_known_public_doc_bundle_query(lowered):
        return False
    if _message_matches_term(lowered, 'calendario'):
        return False
    if any(
        _message_matches_term(lowered, term)
        for term in {
            'panorama academico',
            'panorama acadêmico',
            'quadro academico',
            'quadro acadêmico',
            'situacao academica',
            'situação acadêmica',
            'media minima',
            'média mínima',
            'limite de aprovacao',
            'limite de aprovação',
            'mais perto da media',
            'mais perto da média',
            'mais perto do limite',
            'mais proximo do limite',
            'mais próximo do limite',
            'mais perto da aprovacao',
            'mais perto da aprovação',
            'componentes',
            'mais vulneravel',
            'mais vulnerável',
            'mais exposto',
            'mais exposta',
            'maior risco',
            'pontos de maior risco',
            'pontos academicos que mais preocupam',
            'pontos acadêmicos que mais preocupam',
            'pontos academicos',
            'pontos acadêmicos',
            'mais preocupam',
            'preocupacao academica',
            'preocupação acadêmica',
            'preocupacoes academicas',
            'preocupações acadêmicas',
            'esta mais vulneravel',
            'está mais vulnerável',
            'meus dois filhos',
            'meus filhos',
        }
    ):
        return True
    return any(
        _message_matches_term(lowered, term)
        for term in {'prova', 'provas', 'avaliacao', 'avaliacoes', 'avaliação', 'avaliações'}
    )


def _is_authenticated_student_registry_query(message: str, *, authenticated: bool) -> bool:
    if not authenticated:
        return False
    lowered = _normalize_text(message)
    if _is_cross_document_public_query(lowered) or _is_known_public_doc_bundle_query(lowered):
        return False
    return any(_message_matches_term(lowered, term) for term in ACADEMIC_IDENTITY_TERMS)


def _is_authenticated_finance_attribute_query(message: str, *, authenticated: bool) -> bool:
    if not authenticated:
        return False
    lowered = _normalize_text(message)
    return any(_message_matches_term(lowered, term) for term in PERSONAL_FINANCE_ATTRIBUTE_TERMS)


def classify_request(state: OrchestrationState) -> OrchestrationState:
    from .graph_classification_runtime import classify_request as _impl

    return _impl(state)



def security_gate(state: OrchestrationState) -> OrchestrationState:
    request = state['request']
    classification = state['classification']
    risk_flags = list(state.get('risk_flags', []))
    needs_authentication = (
        classification.access_tier in {AccessTier.authenticated, AccessTier.sensitive}
        and not request.user.authenticated
    )

    if classification.access_tier is AccessTier.sensitive:
        risk_flags.append('sensitive_data_path')
    if request.user.role is UserRole.anonymous and classification.domain in {
        QueryDomain.academic,
        QueryDomain.finance,
    }:
        risk_flags.append('anonymous_user_requested_protected_domain')

    return {
        'needs_authentication': needs_authentication,
        'risk_flags': risk_flags,
        'graph_path': _append_path(state, 'security_gate'),
    }


def route_request(state: OrchestrationState, runtime: GraphRuntimeConfig) -> OrchestrationState:
    from .graph_classification_runtime import route_request as _impl

    return _impl(state, runtime)



def select_slice(state: OrchestrationState) -> OrchestrationState:
    route = state['route']
    classification = state['classification']
    request = state['request']
    normalized_message = _normalize_text(request.message)
    support_public_rescue = (
        classification.domain is QueryDomain.support
        and route == OrchestrationMode.structured_tool.value
        and (
            _is_public_school_profile_request(normalized_message)
            or _is_public_navigation_query(normalized_message)
            or _is_public_timeline_query(normalized_message)
            or _is_public_calendar_event_query(normalized_message)
        )
    )

    if route == OrchestrationMode.deny.value:
        slice_name = 'deny'
    elif route == OrchestrationMode.clarify.value:
        slice_name = 'clarify'
    elif support_public_rescue:
        slice_name = 'public'
    elif classification.domain is QueryDomain.support:
        slice_name = 'support'
    elif classification.domain in {QueryDomain.academic, QueryDomain.finance} or classification.access_tier in {
        AccessTier.authenticated,
        AccessTier.sensitive,
    }:
        slice_name = 'protected'
    else:
        slice_name = 'public'

    return {
        'slice_name': slice_name,
        'graph_path': _append_path(state, 'select_slice'),
    }


def hybrid_retrieval(state: OrchestrationState) -> OrchestrationState:
    classification = state['classification']
    selected_tools = ['search_public_documents']

    if classification.domain is QueryDomain.calendar:
        selected_tools.append('get_school_calendar')

    return {
        'retrieval_backend': RetrievalBackend.qdrant_hybrid.value,
        'selected_tools': selected_tools,
        'citations_required': True,
        'output_contract': 'resposta com citacoes documentais e, quando houver, calendario estruturado consolidado',
        'graph_path': _append_path(state, 'hybrid_retrieval'),
    }


def graph_rag_retrieval(state: OrchestrationState) -> OrchestrationState:
    return {
        'retrieval_backend': RetrievalBackend.graph_rag.value,
        'selected_tools': ['search_public_documents'],
        'citations_required': True,
        'risk_flags': [*state.get('risk_flags', []), 'advanced_retrieval_path'],
        'output_contract': 'resposta sintetica com citacoes e suporte multi-documento via artefatos de graph rag',
        'graph_path': _append_path(state, 'graph_rag_retrieval'),
    }


def structured_tool_call(state: OrchestrationState) -> OrchestrationState:
    from .graph_execution_runtime import structured_tool_call as _impl

    return _impl(state)



def handoff(state: OrchestrationState) -> OrchestrationState:
    return {
        'retrieval_backend': RetrievalBackend.none.value,
        'selected_tools': ['create_support_ticket', 'handoff_to_human'],
        'citations_required': False,
        'output_contract': 'encaminhamento humano com resumo seguro e protocolo de atendimento',
        'graph_path': _append_path(state, 'handoff'),
    }


def deny(state: OrchestrationState) -> OrchestrationState:
    return {
        'retrieval_backend': RetrievalBackend.none.value,
        'selected_tools': [],
        'citations_required': False,
        'risk_flags': [*state.get('risk_flags', []), 'authentication_required'],
        'output_contract': 'negacao segura com orientacao de autenticacao ou vinculo',
        'graph_path': _append_path(state, 'deny'),
    }


def clarify(state: OrchestrationState) -> OrchestrationState:
    return {
        'retrieval_backend': RetrievalBackend.none.value,
        'selected_tools': [],
        'citations_required': False,
        'output_contract': 'pedido de clarificacao objetiva para reduzir ambiguidade',
        'graph_path': _append_path(state, 'clarify'),
    }


def to_preview(state: OrchestrationState) -> OrchestrationPreview:
    return OrchestrationPreview(
        mode=OrchestrationMode(state['route']),
        classification=state['classification'],
        retrieval_backend=RetrievalBackend(state.get('retrieval_backend', RetrievalBackend.none.value)),
        selected_tools=state.get('selected_tools', []),
        citations_required=state.get('citations_required', False),
        needs_authentication=state.get('needs_authentication', False),
        graph_path=state.get('graph_path', []),
        risk_flags=state.get('risk_flags', []),
        reason=state.get('reason', 'sem razao registrada'),
        output_contract=state.get('output_contract', 'sem contrato definido'),
    )


@lru_cache
def get_graph_blueprint() -> dict[str, object]:
    from .graph_execution_runtime import get_graph_blueprint as _impl

    return _impl()



def _enter_public_slice(state: OrchestrationState) -> OrchestrationState:
    return {
        'slice_name': 'public',
        'graph_path': _append_path(state, 'public_slice'),
    }


def _public_slice_route(state: OrchestrationState) -> str:
    route = state['route']
    if route in {
        OrchestrationMode.hybrid_retrieval.value,
        OrchestrationMode.graph_rag.value,
        OrchestrationMode.structured_tool.value,
    }:
        return route
    return OrchestrationMode.structured_tool.value


def _build_public_slice_subgraph() -> object:
    workflow = StateGraph(OrchestrationState)
    workflow.add_node('enter_public_slice', _enter_public_slice)
    workflow.add_node('hybrid_retrieval', hybrid_retrieval)
    workflow.add_node('graph_rag_retrieval', graph_rag_retrieval)
    workflow.add_node('structured_tool_call', structured_tool_call)
    workflow.add_edge(START, 'enter_public_slice')
    workflow.add_conditional_edges(
        'enter_public_slice',
        _public_slice_route,
        {
            OrchestrationMode.hybrid_retrieval.value: 'hybrid_retrieval',
            OrchestrationMode.graph_rag.value: 'graph_rag_retrieval',
            OrchestrationMode.structured_tool.value: 'structured_tool_call',
        },
    )
    workflow.add_edge('hybrid_retrieval', END)
    workflow.add_edge('graph_rag_retrieval', END)
    workflow.add_edge('structured_tool_call', END)
    return workflow.compile()


def _enter_protected_slice(state: OrchestrationState) -> OrchestrationState:
    return {
        'slice_name': 'protected',
        'graph_path': _append_path(state, 'protected_slice'),
    }


def _build_protected_slice_subgraph() -> object:
    workflow = StateGraph(OrchestrationState)
    workflow.add_node('enter_protected_slice', _enter_protected_slice)
    workflow.add_node('structured_tool_call', structured_tool_call)
    workflow.add_node('protected_human_review', protected_human_review)
    workflow.add_node('protected_review_approved', protected_review_approved)
    workflow.add_node('protected_review_cancelled', protected_review_cancelled)
    workflow.add_edge(START, 'enter_protected_slice')
    workflow.add_edge('enter_protected_slice', 'structured_tool_call')
    workflow.add_conditional_edges(
        'structured_tool_call',
        _protected_post_action_route,
        {
            'review': 'protected_human_review',
            'complete': END,
        },
    )
    workflow.add_edge('protected_review_approved', END)
    workflow.add_edge('protected_review_cancelled', END)
    return workflow.compile()


def _enter_support_slice(state: OrchestrationState) -> OrchestrationState:
    return {
        'slice_name': 'support',
        'graph_path': _append_path(state, 'support_slice'),
    }


def _support_slice_route(state: OrchestrationState) -> str:
    if state['route'] == OrchestrationMode.handoff.value:
        return OrchestrationMode.handoff.value
    return OrchestrationMode.structured_tool.value


def _hitl_enabled_for_slice(state: OrchestrationState, slice_name: str) -> bool:
    if not bool(state.get('hitl_enabled')):
        return False
    target_slices = [str(item).strip() for item in state.get('hitl_target_slices', []) if str(item).strip()]
    if not target_slices:
        target_slices = ['support']
    return slice_name in set(target_slices)


def _support_post_action_route(state: OrchestrationState) -> str:
    if _hitl_enabled_for_slice(state, 'support') and state.get('route') in {
        OrchestrationMode.structured_tool.value,
        OrchestrationMode.handoff.value,
    }:
        return 'review'
    return 'complete'


_PROTECTED_HITL_SAFE_TOOLS = {
    'get_actor_identity_context',
    'get_administrative_status',
    'get_student_administrative_status',
}


def _protected_hitl_eligible(state: OrchestrationState) -> bool:
    if state.get('route') != OrchestrationMode.structured_tool.value:
        return False
    classification = state.get('classification')
    if not isinstance(classification, IntentClassification):
        return False
    if classification.domain is not QueryDomain.institution:
        return False
    if classification.access_tier is AccessTier.public:
        return False
    selected_tools = {
        str(tool_name).strip()
        for tool_name in state.get('selected_tools', [])
        if str(tool_name).strip()
    }
    return bool(selected_tools) and selected_tools.issubset(_PROTECTED_HITL_SAFE_TOOLS)


def _protected_post_action_route(state: OrchestrationState) -> str:
    if _hitl_enabled_for_slice(state, 'protected') and _protected_hitl_eligible(state):
        return 'review'
    return 'complete'


def _support_hitl_interrupt_payload(state: OrchestrationState) -> dict[str, object]:
    request = state['request']
    return {
        'kind': 'support_action_review',
        'question': 'Aprovar a execucao desta acao sensivel de atendimento?',
        'message': request.message,
        'conversation_id': request.conversation_id,
        'route': state.get('route'),
        'reason': state.get('reason'),
        'selected_tools': list(state.get('selected_tools', [])),
        'graph_path': list(state.get('graph_path', [])),
        'output_contract': state.get('output_contract'),
        'risk_flags': list(state.get('risk_flags', [])),
    }


def _protected_hitl_interrupt_payload(state: OrchestrationState) -> dict[str, object]:
    request = state['request']
    classification = state.get('classification')
    return {
        'kind': 'protected_record_review',
        'question': 'Aprovar a liberacao desta consulta protegida de baixo risco?',
        'message': request.message,
        'conversation_id': request.conversation_id,
        'route': state.get('route'),
        'reason': state.get('reason'),
        'selected_tools': list(state.get('selected_tools', [])),
        'graph_path': list(state.get('graph_path', [])),
        'output_contract': state.get('output_contract'),
        'risk_flags': list(state.get('risk_flags', [])),
        'classification': (
            {
                'domain': classification.domain.value,
                'access_tier': classification.access_tier.value,
                'confidence': classification.confidence,
            }
            if isinstance(classification, IntentClassification)
            else None
        ),
    }


def _is_hitl_approved(resume_value: object) -> bool:
    if isinstance(resume_value, bool):
        return resume_value
    if isinstance(resume_value, dict):
        raw_value = resume_value.get('approved')
        if isinstance(raw_value, bool):
            return raw_value
        return str(raw_value or '').strip().lower() in {'true', '1', 'yes', 'y', 'sim', 'approve', 'approved'}
    return str(resume_value or '').strip().lower() in {'true', '1', 'yes', 'y', 'sim', 'approve', 'approved'}


def support_human_review(state: OrchestrationState) -> Command[str]:
    review_payload = _support_hitl_interrupt_payload(state)
    resume_value = interrupt(review_payload)
    approved = _is_hitl_approved(resume_value)
    next_node = 'support_review_approved' if approved else 'support_review_cancelled'
    return Command(
        update={
            'hitl_status': 'approved' if approved else 'rejected',
            'hitl_resume_payload': resume_value,
            'graph_path': _append_path(state, 'support_human_review'),
            'risk_flags': _append_unique_risk_flags(
                state,
                'human_review_required',
                'human_review_approved' if approved else 'human_review_rejected',
            ),
        },
        goto=next_node,
    )


def protected_human_review(state: OrchestrationState) -> Command[str]:
    review_payload = _protected_hitl_interrupt_payload(state)
    resume_value = interrupt(review_payload)
    approved = _is_hitl_approved(resume_value)
    next_node = 'protected_review_approved' if approved else 'protected_review_cancelled'
    return Command(
        update={
            'hitl_status': 'approved' if approved else 'rejected',
            'hitl_resume_payload': resume_value,
            'graph_path': _append_path(state, 'protected_human_review'),
            'risk_flags': _append_unique_risk_flags(
                state,
                'human_review_required',
                'human_review_approved' if approved else 'human_review_rejected',
            ),
        },
        goto=next_node,
    )


def support_review_approved(state: OrchestrationState) -> OrchestrationState:
    return {
        'hitl_status': 'approved',
        'graph_path': _append_path(state, 'support_review_approved'),
    }


def protected_review_approved(state: OrchestrationState) -> OrchestrationState:
    return {
        'hitl_status': 'approved',
        'graph_path': _append_path(state, 'protected_review_approved'),
    }


def support_review_cancelled(state: OrchestrationState) -> OrchestrationState:
    return {
        'route': OrchestrationMode.deny.value,
        'retrieval_backend': RetrievalBackend.none.value,
        'selected_tools': [],
        'citations_required': False,
        'reason': 'acao sensivel bloqueada por revisao humana antes da execucao',
        'output_contract': 'execucao bloqueada por revisao humana com trilha auditavel',
        'hitl_status': 'rejected',
        'graph_path': _append_path(state, 'support_review_cancelled'),
    }


def protected_review_cancelled(state: OrchestrationState) -> OrchestrationState:
    return {
        'route': OrchestrationMode.deny.value,
        'retrieval_backend': RetrievalBackend.none.value,
        'selected_tools': [],
        'citations_required': False,
        'reason': 'consulta protegida bloqueada por revisao humana antes da execucao',
        'output_contract': 'consulta protegida bloqueada por revisao humana com trilha auditavel',
        'hitl_status': 'rejected',
        'graph_path': _append_path(state, 'protected_review_cancelled'),
    }


def _build_support_slice_subgraph() -> object:
    workflow = StateGraph(OrchestrationState)
    workflow.add_node('enter_support_slice', _enter_support_slice)
    workflow.add_node('structured_tool_call', structured_tool_call)
    workflow.add_node('handoff', handoff)
    workflow.add_node('support_human_review', support_human_review)
    workflow.add_node('support_review_approved', support_review_approved)
    workflow.add_node('support_review_cancelled', support_review_cancelled)
    workflow.add_edge(START, 'enter_support_slice')
    workflow.add_conditional_edges(
        'enter_support_slice',
        _support_slice_route,
        {
            OrchestrationMode.structured_tool.value: 'structured_tool_call',
            OrchestrationMode.handoff.value: 'handoff',
        },
    )
    workflow.add_conditional_edges(
        'structured_tool_call',
        _support_post_action_route,
        {
            'review': 'support_human_review',
            'complete': END,
        },
    )
    workflow.add_conditional_edges(
        'handoff',
        _support_post_action_route,
        {
            'review': 'support_human_review',
            'complete': END,
        },
    )
    workflow.add_edge('support_review_approved', END)
    workflow.add_edge('support_review_cancelled', END)
    return workflow.compile()


def build_orchestration_graph(graph_rag_enabled: bool, *, checkpointer: object | None = None) -> object:
    workflow = StateGraph(OrchestrationState)
    runtime: GraphRuntimeConfig = {'graph_rag_enabled': graph_rag_enabled}
    public_slice = _build_public_slice_subgraph()
    protected_slice = _build_protected_slice_subgraph()
    support_slice = _build_support_slice_subgraph()

    workflow.add_node('classify_request', classify_request)
    workflow.add_node('security_gate', security_gate)
    workflow.add_node('route_request', lambda state: route_request(state, runtime))
    workflow.add_node('select_slice', select_slice)
    workflow.add_node('public_slice', public_slice)
    workflow.add_node('protected_slice', protected_slice)
    workflow.add_node('support_slice', support_slice)
    workflow.add_node('deny', deny)
    workflow.add_node('clarify', clarify)

    workflow.add_edge(START, 'classify_request')
    workflow.add_edge('classify_request', 'security_gate')
    workflow.add_edge('security_gate', 'route_request')
    workflow.add_edge('route_request', 'select_slice')
    workflow.add_conditional_edges(
        'select_slice',
        lambda state: state['slice_name'],
        {
            'public': 'public_slice',
            'protected': 'protected_slice',
            'support': 'support_slice',
            'deny': 'deny',
            'clarify': 'clarify',
        },
    )
    workflow.add_edge('public_slice', END)
    workflow.add_edge('protected_slice', END)
    workflow.add_edge('support_slice', END)
    workflow.add_edge('deny', END)
    workflow.add_edge('clarify', END)
    return workflow.compile(checkpointer=checkpointer)
