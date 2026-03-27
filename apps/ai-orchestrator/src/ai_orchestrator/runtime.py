from __future__ import annotations

import base64
import io
import re
import unicodedata
from dataclasses import dataclass, field, replace
from datetime import date, datetime, timedelta
from time import monotonic
from typing import Any, Callable
from zoneinfo import ZoneInfo

import httpx
from eduassist_observability import record_counter, record_histogram, set_span_attributes, start_span
from PIL import Image, ImageDraw, ImageFont

from .graph_rag_runtime import graph_rag_workspace_ready, run_graph_rag_query
from .langgraph_trace import build_langgraph_trace_sections
from .llm_provider import (
    compose_with_provider,
    compose_public_grounded_with_provider,
    judge_answer_relevance_with_provider,
    polish_structured_with_provider,
    resolve_public_semantic_with_provider,
    revise_with_provider,
)
from .graph import to_preview
from .crewai_trace import build_crewai_trace_sections
from .langgraph_runtime import (
    get_langgraph_artifacts,
    get_orchestration_state_snapshot,
    invoke_orchestration_graph,
    resolve_langgraph_thread_id,
)
from .models import (
    AccessTier,
    CalendarEventCard,
    IntentClassification,
    MessageResponse,
    MessageResponseCitation,
    MessageResponseRequest,
    MessageResponseSuggestedReply,
    MessageResponseVisualAsset,
    OrchestrationMode,
    OrchestrationPreview,
    OrchestrationRequest,
    QueryDomain,
    RetrievalBackend,
    UserContext,
    UserRole,
)
from .public_agentic_engine import build_public_evidence_bundle
from .retrieval import get_retrieval_service


DEFAULT_PUBLIC_HELP = (
    'Posso ajudar com informacoes publicas da escola, como calendario, matricula, '
    'documentos exigidos e regras de atendimento digital.'
)

ATTENDANCE_TERMS = {'frequencia', 'falta', 'faltas', 'presenca', 'presencas'}
GRADE_TERMS = {'nota', 'notas', 'boletim', 'avaliacao', 'avaliacoes', 'prova', 'provas'}
UPCOMING_ASSESSMENT_TERMS = {
    'proxima prova',
    'proximas provas',
    'próximas provas',
    'proxima avaliacao',
    'proxima avaliação',
    'avaliacoes futuras',
    'avaliações futuras',
    'proximas avaliacoes',
    'próximas avaliações',
}
ATTENDANCE_TIMELINE_TERMS = {
    'data das faltas',
    'datas das faltas',
    'quando foram as faltas',
    'qual data foram as faltas',
    'faltas com data',
    'datas da frequencia',
    'datas da frequência',
}
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
FINANCE_OVERDUE_TERMS = {
    'vencido',
    'vencidos',
    'vencida',
    'vencidas',
    'atrasado',
    'atrasados',
    'atrasada',
    'atrasadas',
    'inadimplencia',
}
FINANCE_PAID_TERMS = {
    'pago',
    'pagos',
    'paga',
    'pagas',
    'quitado',
    'quitados',
    'quitada',
    'quitadas',
}
FINANCE_NEXT_DUE_TERMS = {
    'proximo pagamento',
    'próximo pagamento',
    'proxima data de pagamento',
    'próxima data de pagamento',
    'proxima data do pagamento',
    'próxima data do pagamento',
    'proxima mensalidade',
    'próxima mensalidade',
    'proximo vencimento',
    'próximo vencimento',
    'quando vence',
    'qual vence primeiro',
}
FINANCE_SECOND_COPY_TERMS = {
    'segunda via',
    '2a via',
    'segunda via do boleto',
    'reemitir boleto',
    'emitir boleto novamente',
}
PERSONAL_ADMIN_STATUS_TERMS = {
    'documentacao atualizada',
    'documentação atualizada',
    'documentacao completa',
    'documentação completa',
    'cadastro atualizado',
    'cadastro completo',
    'meu cadastro',
    'meus dados cadastrais',
    'dados cadastrais',
    'documentacao',
    'documentação',
}
PERSONAL_PROFILE_UPDATE_TERMS = {
    'alterar email',
    'atualizar email',
    'mudar email',
    'corrigir email',
    'endereco de email',
    'endereço de email',
    'alterar telefone',
    'atualizar telefone',
    'mudar telefone',
}
ACADEMIC_IDENTITY_TERMS = {
    'matricula',
    'matrícula',
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
FINANCE_IDENTIFIER_TERMS = {
    'numero do boleto',
    'número do boleto',
    'codigo do boleto',
    'código do boleto',
    'identificador do boleto',
    'id do boleto',
    'numero da fatura',
    'número da fatura',
    'codigo da fatura',
    'código da fatura',
    'identificador da fatura',
    'id da fatura',
}
FINANCE_CONTRACT_TERMS = {
    'codigo do contrato',
    'código do contrato',
    'numero do contrato',
    'número do contrato',
    'identificador do contrato',
    'contrato financeiro',
}
ADMIN_STATUS_LABELS = {
    'complete': 'regular',
    'review': 'em revisao',
    'pending': 'com pendencias',
}
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
    'fax',
    'fone',
    'ligar',
    'ligo',
    'contato',
    'fale com',
    'canal oficial',
    'canais oficiais de contato',
    'canais de contato',
    'como entrar em contato',
    'fale conosco',
}
PUBLIC_WEB_TERMS = {
    'site',
    'site oficial',
    'website',
    'pagina oficial',
    'página oficial',
    'portal institucional',
    'link do site',
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
PUBLIC_CURRICULUM_TERMS = {
    'base curricular',
    'curriculo',
    'currículo',
    'componentes curriculares',
    'componente curricular',
    'materias do ensino medio',
    'matérias do ensino médio',
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
}
PUBLIC_UTILITY_DATE_TERMS = {
    'que dia e hoje',
    'que dia é hoje',
    'qual a data de hoje',
    'hoje e que dia',
    'hoje é que dia',
}
PUBLIC_DOCUMENT_SUBMISSION_TERMS = {
    'documentos online',
    'documento online',
    'envio de documentos',
    'enviar documentos',
    'mandar documentos',
    'envio digital',
    'documentos digitalmente',
    'aceita documentos online',
    'aceita envio online',
    'aceita envio digital',
    'por onde envio meus documentos',
    'como envio meus documentos',
    'canal de documentos',
    'enviar por fax',
    'mandar por fax',
    'posso enviar por fax',
    'posso enviar documentos por fax',
    'posso mandar documentos por fax',
    'enviar por telegrama',
    'mandar por telegrama',
    'posso enviar por telegrama',
    'posso mandar por telegrama',
    'enviar por caixa postal',
    'mandar por caixa postal',
    'caixa postal',
    'telegrama',
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
    'especial',
    'especiais',
    'ponto forte',
    'pontos fortes',
    'unica',
    'única',
}
PUBLIC_PEDAGOGICAL_TERMS = {
    'proposta pedagogica',
    'proposta pedagógica',
    'projeto pedagogico',
    'projeto pedagógico',
    'aprendizagem por projetos',
    'acolhimento',
    'convivencia',
    'convivência',
    'aprendizagem',
    'socioemocional',
}
PUBLIC_VISIT_TERMS = {
    'visita',
    'visitas',
    'visita guiada',
    'tour',
    'conhecer a escola',
    'agendar visita',
}
VISIT_RESCHEDULE_TERMS = {
    'remarcar visita',
    'remarcar a visita',
    'reagendar visita',
    'reagendar a visita',
    'mudar a visita',
    'mudar horario da visita',
    'mudar horario da minha visita',
    'trocar horario da visita',
}
VISIT_CANCEL_TERMS = {
    'cancelar visita',
    'cancelar a visita',
    'desmarcar visita',
    'desmarcar a visita',
    'cancelar minha visita',
}
INSTITUTIONAL_REQUEST_UPDATE_TERMS = {
    'complementar pedido',
    'complementar meu pedido',
    'complementar protocolo',
    'complementar minha solicitacao',
    'complementar minha solicitação',
    'acrescentar ao protocolo',
    'adicionar ao protocolo',
    'incluir no protocolo',
    'complemente meu pedido',
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
    'legal',
    'show',
    'massa',
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
WORKFLOW_VISIT_TERMS = {'visita', 'tour', 'conhecer a escola'}
WORKFLOW_REQUEST_TERMS = {'solicitacao', 'solicitação', 'pedido', 'protocolo', 'requerimento', 'direcao', 'direção', 'ouvidoria'}
WORKFLOW_HANDOFF_TERMS = {'atendimento', 'atendente', 'humano', 'chamado'}
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
    'me passa o protocolo',
    'meu protocolo',
    'resume meu pedido',
    'resuma meu pedido',
    'o que eu pedi',
    'qual foi meu pedido',
}
PROTOCOL_CODE_PATTERN = re.compile(
    r'\b(?:VIS|REQ)-\d{8}-[A-Z0-9]{6}\b|\bATD-\d{8}-[A-Z0-9]{8}\b',
    re.IGNORECASE,
)
WORKFLOW_STATUS_LABELS = {
    'queued': 'em fila',
    'requested': 'registrado',
    'in_progress': 'em atendimento',
    'resolved': 'concluido',
    'cancelled': 'cancelado',
}
WORKFLOW_QUEUE_LABELS = {
    'admissoes': 'admissions',
    'direcao': 'direcao',
    'coordenacao': 'coordenacao',
    'financeiro': 'financeiro',
    'secretaria': 'secretaria',
    'atendimento': 'atendimento',
}
PUBLIC_SEGMENT_TERMS = {
    'segmento',
    'segmentos',
    'quais segmentos',
    'segmentos atendidos',
    'segmentos a escola atende',
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
PUBLIC_ENRICHMENT_TERMS = {
    'aulas complementares',
    'atividades complementares',
    'complementares',
    'contraturno',
    'monitorias',
    'monitoria',
    'plantoes',
    'plantoes',
    'plantões',
    'estudo orientado',
    'trilhas academicas',
    'trilhas acadêmicas',
}
PUBLIC_SCHOLARSHIP_TERMS = {
    'bolsa',
    'bolsas',
    'desconto',
    'descontos',
    'politica comercial',
    'política comercial',
    'irmaos',
    'irmãos',
    'pagamento pontual',
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
PUBLIC_ACTIVE_TASK_BY_ACT = {
    'assistant_identity': 'public:assistant_identity',
    'capabilities': 'public:capabilities',
    'access_scope': 'public:access_scope',
    'service_routing': 'public:service_routing',
    'auth_guidance': 'public:auth_guidance',
    'document_submission': 'public:document_submission',
    'careers': 'public:careers',
    'teacher_directory': 'public:teacher_directory',
    'leadership': 'public:leadership',
    'contacts': 'public:contacts',
    'web_presence': 'public:web_presence',
    'social_presence': 'public:social_presence',
    'comparative': 'public:comparative',
    'pricing': 'public:pricing',
    'schedule': 'public:schedule',
    'operating_hours': 'public:operating_hours',
    'curriculum': 'public:curriculum',
    'features': 'public:features',
    'highlight': 'public:highlight',
    'visit': 'public:visit',
    'location': 'public:location',
    'confessional': 'public:confessional',
    'kpi': 'public:kpi',
    'segments': 'public:segments',
    'school_name': 'public:school_name',
    'timeline': 'public:timeline',
    'calendar_events': 'public:calendar_events',
    'utility_date': 'public:utility_date',
    'canonical_fact': 'public:canonical_fact',
}
PUBLIC_ACTIVE_ENTITY_BY_ACT = {
    'assistant_identity': 'eduassist',
    'capabilities': 'escola',
    'access_scope': 'conta vinculada',
    'service_routing': 'setores da escola',
    'auth_guidance': 'conta',
    'document_submission': 'documentos',
    'careers': 'carreiras',
    'teacher_directory': 'professores',
    'leadership': 'direcao',
    'contacts': 'escola',
    'web_presence': 'escola',
    'social_presence': 'redes sociais da escola',
    'comparative': 'diferenciais da escola',
    'pricing': 'mensalidade',
    'schedule': 'horario escolar',
    'operating_hours': 'escola',
    'curriculum': 'curriculo',
    'features': 'estrutura da escola',
    'highlight': 'diferenciais da escola',
    'visit': 'visita institucional',
    'location': 'escola',
    'confessional': 'identidade institucional',
    'kpi': 'indicadores institucionais',
    'segments': 'segmentos',
    'school_name': 'escola',
    'timeline': 'calendario institucional',
    'calendar_events': 'eventos publicos',
    'utility_date': 'data atual',
    'canonical_fact': 'escola',
}
FOCUS_TTL_SECONDS_BY_KIND = {
    'visit': 24 * 60 * 60,
    'request': 24 * 60 * 60,
    'finance': 45 * 60,
    'academic': 45 * 60,
    'secretaria': 30 * 60,
    'admissions': 20 * 60,
    'public': 20 * 60,
}
NON_STICKY_PUBLIC_TASKS = {
    'public:greeting',
    'public:assistant_identity',
    'public:capabilities',
    'public:access_scope',
}
PUBLIC_SEMANTIC_RESCUE_ACTS = {
    'assistant_identity',
    'capabilities',
    'access_scope',
    'service_routing',
    'auth_guidance',
    'document_submission',
    'careers',
    'teacher_directory',
    'leadership',
    'contacts',
    'web_presence',
    'social_presence',
    'comparative',
    'operating_hours',
    'timeline',
    'location',
    'curriculum',
    'features',
    'highlight',
    'visit',
    'pricing',
    'schedule',
    'segments',
    'school_name',
    'calendar_events',
}
WORKFLOW_ACTIVE_TASK_BY_KIND = {
    'visit': 'workflow:visit_booking',
    'request': 'workflow:institutional_request',
    'finance': 'workflow:finance_support',
    'secretaria': 'workflow:secretaria_support',
    'admissions': 'workflow:admissions_support',
    'support': 'workflow:human_handoff',
}
WORKFLOW_ACTIVE_ENTITY_BY_KIND = {
    'visit': 'visita institucional',
    'request': 'solicitacao institucional',
    'finance': 'financeiro',
    'secretaria': 'secretaria',
    'admissions': 'matricula',
    'support': 'atendimento humano',
}
ACADEMIC_ACTIVE_TASK_BY_FOCUS = {
    'grades': 'academic:grades',
    'attendance': 'academic:attendance',
    'attendance_timeline': 'academic:attendance_timeline',
    'upcoming': 'academic:upcoming',
    'registry': 'academic:registry',
}
FOLLOW_UP_CONTEXT_BY_TASK = {
    'public:contacts': 'contato de {entity}',
    'public:web_presence': 'site de {entity}',
    'public:location': 'endereco de {entity}',
    'public:operating_hours': 'horario de funcionamento de {entity}',
    'public:curriculum': 'curriculo de {entity}',
    'public:timeline': 'calendario institucional de {entity}',
    'public:features': 'estrutura e atividades de {entity}',
    'public:leadership': 'direcao de {entity}',
    'academic:grades': 'notas de {entity}',
    'academic:attendance': 'frequencia de {entity}',
    'academic:attendance_timeline': 'faltas de {entity}',
    'academic:upcoming': 'provas e atividades de {entity}',
    'academic:registry': 'dados academicos de {entity}',
    'finance:billing': 'financeiro de {entity}',
    'finance:invoice_id': 'fatura de {entity}',
    'finance:contract_code': 'contrato de {entity}',
    'finance:next_due': 'proximo pagamento de {entity}',
    'finance:second_copy': 'segunda via do boleto de {entity}',
    'admin:administrative_status': 'dados cadastrais de {entity}',
    'admin:student_administrative_status': 'documentacao de {entity}',
    'admin:profile_update': 'atualizacao cadastral de {entity}',
    'workflow:visit_booking': 'visita institucional',
    'workflow:institutional_request': 'solicitacao institucional',
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
    'depois disso',
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
GREETING_ONLY_TERMS = {
    'oi',
    'ola',
    'olá',
    'bom dia',
    'boa tarde',
    'boa noite',
    'opa',
    'e ai',
    'e aí',
}
ASSISTANT_IDENTITY_TERMS = {
    'com quem eu falo',
    'pra quem eu falo',
    'para quem eu falo',
    'quem e voce',
    'quem é você',
    'voce e quem',
    'você é quem',
    'quem esta ai',
    'quem está aí',
}
ASSISTANT_CAPABILITY_TERMS = {
    'o que voce faz',
    'o que você faz',
    'o que esta fazendo',
    'o que está fazendo',
    'o que ta fazendo',
    'o que tá fazendo',
    'como voce pode me ajudar',
    'como você pode me ajudar',
    'no que voce pode ajudar',
    'no que você pode ajudar',
    'quais assuntos',
    'que assuntos',
    'opcoes de assuntos',
    'opções de assuntos',
    'o que posso resolver aqui',
    'o que eu posso pedir aqui',
    'que opcoes eu tenho',
    'que opções eu tenho',
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
    'eu consigo ver o que exatamente',
    'o que exatamente eu consigo ver',
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
SERVICE_ROUTING_TERMS = {
    'com quem eu falo sobre',
    'pra quem eu falo sobre',
    'para quem eu falo sobre',
    'com quem eu falo',
    'com qual contato eu devo falar',
    'qual contato eu devo usar',
    'qual contato devo usar',
    'por qual canal',
    'como falo com',
    'como falar com',
    'como reporto',
    'como denunciar',
    'pra quem eu falo',
    'para quem eu falo',
    'quem cuida',
    'quem resolve',
    'qual setor',
    'qual area',
    'qual área',
    'qual equipe',
}
SERVICE_FOLLOW_UP_CONTEXT_TERMS = {
    'matricula',
    'bolsa',
    'desconto',
    'visita',
    'tour',
    'documento',
    'documentos',
    'historico',
    'declaracao',
    'transferencia',
    'uniforme',
    'rotina',
    'aprendizagem',
    'adaptacao',
    'professor',
    'faltas',
    'nota',
    'notas',
    'disciplina',
    'emocional',
    'convivencia',
    'orientacao',
    'socioemocional',
    'mensalidade',
    'boleto',
    'boletos',
    'financeiro',
    'fatura',
    'pagamento',
    'contrato',
    'direcao',
    'diretora',
    'ouvidoria',
    'elogio',
    'reclamacao',
    'sugestao',
    'portal',
    'senha',
    'acesso',
    'telegram',
    'bot',
    'sistema',
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
    recent_tool_calls: list[dict[str, Any]]
    message_count: int


@dataclass(frozen=True)
class StructuredAnswerFrame:
    lead: str
    facts: tuple[str, ...] = ()
    next_step: str | None = None
    offer: str | None = None


@dataclass(frozen=True)
class PublicInstitutionPlan:
    conversation_act: str
    required_tools: tuple[str, ...]
    fetch_profile: bool
    secondary_acts: tuple[str, ...] = ()
    requested_attribute: str | None = None
    requested_channel: str | None = None
    focus_hint: str | None = None
    semantic_source: str = 'rules'
    use_conversation_context: bool = False


@dataclass(frozen=True)
class PublicActRule:
    name: str
    matcher: Callable[[str], bool]
    required_tools: tuple[str, ...] = ()
    fetch_profile: bool = True


@dataclass(frozen=True)
class PublicProfileContext:
    profile: dict[str, Any]
    actor: dict[str, Any] | None
    message: str
    source_message: str
    normalized: str
    analysis_normalized: str
    school_name: str
    school_reference: str
    school_reference_capitalized: str
    city: str
    state: str
    district: str
    address_line: str
    postal_code: str
    website_url: str
    fax_number: str
    curriculum_basis: str
    curriculum_components: tuple[str, ...]
    confessional_status: str
    segment: str | None
    schedule_context_normalized: str
    shift_offers: tuple[dict[str, Any], ...]
    tuition_reference: tuple[dict[str, Any], ...]
    semantic_act: str | None
    contact_reference_message: str
    preferred_contact_labels: tuple[str, ...]
    requested_channel: str | None
    requested_attribute_override: str | None
    slot_memory: ConversationSlotMemory
    conversation_context: dict[str, Any] | None
    semantic_plan: PublicInstitutionPlan | None


@dataclass(frozen=True)
class ConversationSlotMemory:
    focus_kind: str | None = None
    protocol_code: str | None = None
    contact_subject: str | None = None
    feature_key: str | None = None
    active_task: str | None = None
    active_entity: str | None = None
    pending_question_type: str | None = None
    pending_disambiguation: str | None = None
    public_entity: str | None = None
    public_attribute: str | None = None
    requested_channel: str | None = None
    time_reference: str | None = None
    academic_student_name: str | None = None
    academic_focus_kind: str | None = None
    academic_attribute: str | None = None
    admin_attribute: str | None = None
    finance_student_name: str | None = None
    finance_status_filter: str | None = None
    finance_attribute: str | None = None
    finance_action: str | None = None


@dataclass(frozen=True)
class ProtectedAttributeRequest:
    domain: str
    attribute: str


@dataclass(frozen=True)
class AnswerVerificationResult:
    valid: bool
    reason: str | None = None


@dataclass(frozen=True)
class InternalSpecialistPlan:
    name: str
    purpose: str
    tool_names: tuple[str, ...]


@dataclass(frozen=True)
class ClarifyRepairPlan:
    kind: str
    student_name: str | None = None


def _normalize_text(text: str) -> str:
    normalized = unicodedata.normalize('NFKD', text)
    without_accents = ''.join(char for char in normalized if not unicodedata.combining(char))
    return without_accents.replace('º', 'o').replace('ª', 'a').lower()


def _is_greeting_only(text: str) -> bool:
    normalized = _normalize_text(text).strip()
    normalized = re.sub(r'[!?.,;:]+', '', normalized)
    normalized = ' '.join(normalized.split())
    return normalized in GREETING_ONLY_TERMS


def _recent_message_lines(conversation_context: dict[str, Any] | None) -> list[tuple[str, str]]:
    lines: list[tuple[str, str]] = []
    if not isinstance(conversation_context, dict):
        return lines
    for item in conversation_context.get('recent_messages', [])[-8:]:
        if not isinstance(item, dict):
            continue
        sender_type = str(item.get('sender_type', '')).strip().lower()
        content = str(item.get('content', '')).strip()
        if sender_type and content:
            lines.append((sender_type, content))
    return lines


def _recent_tool_call_entries(conversation_context: dict[str, Any] | None) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    if not isinstance(conversation_context, dict):
        return entries
    for item in conversation_context.get('recent_tool_calls', [])[-8:]:
        if isinstance(item, dict):
            entries.append(item)
    return entries


def _parse_recent_timestamp(value: Any) -> datetime | None:
    if isinstance(value, datetime):
        return value
    text = str(value or '').strip()
    if not text:
        return None
    normalized = text.replace('Z', '+00:00')
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=datetime.now().astimezone().tzinfo)
    return parsed


def _latest_recent_activity_at(conversation_context: dict[str, Any] | None) -> datetime | None:
    timestamps: list[datetime] = []
    if not isinstance(conversation_context, dict):
        return None
    for item in conversation_context.get('recent_messages', []):
        if not isinstance(item, dict):
            continue
        parsed = _parse_recent_timestamp(item.get('created_at'))
        if parsed is not None:
            timestamps.append(parsed)
    for item in conversation_context.get('recent_tool_calls', []):
        if not isinstance(item, dict):
            continue
        parsed = _parse_recent_timestamp(item.get('created_at'))
        if parsed is not None:
            timestamps.append(parsed)
    if not timestamps:
        return None
    return max(timestamps)


def _focus_ttl_seconds(*, focus_kind: str | None, active_task: str | None) -> int:
    normalized_focus_kind = str(focus_kind or '').strip()
    normalized_active_task = str(active_task or '').strip()
    if normalized_focus_kind in FOCUS_TTL_SECONDS_BY_KIND:
        return FOCUS_TTL_SECONDS_BY_KIND[normalized_focus_kind]
    if normalized_active_task.startswith('workflow:'):
        return FOCUS_TTL_SECONDS_BY_KIND['visit']
    if normalized_active_task.startswith(('finance:', 'academic:')):
        return FOCUS_TTL_SECONDS_BY_KIND['finance']
    if normalized_active_task.startswith('admin:'):
        return FOCUS_TTL_SECONDS_BY_KIND['secretaria']
    if normalized_active_task.startswith('public:'):
        return FOCUS_TTL_SECONDS_BY_KIND['public']
    return FOCUS_TTL_SECONDS_BY_KIND['public']


def _recent_focus_is_fresh(
    conversation_context: dict[str, Any] | None,
    *,
    focus_kind: str | None,
    active_task: str | None = None,
) -> bool:
    latest_activity = _latest_recent_activity_at(conversation_context)
    if latest_activity is None:
        return False
    now = datetime.now(latest_activity.tzinfo) if latest_activity.tzinfo is not None else datetime.utcnow()
    age_seconds = (now - latest_activity).total_seconds()
    return age_seconds <= _focus_ttl_seconds(focus_kind=focus_kind, active_task=active_task)


def _recent_orchestration_trace_payloads(conversation_context: dict[str, Any] | None) -> list[dict[str, Any]]:
    payloads: list[dict[str, Any]] = []
    for item in reversed(_recent_tool_call_entries(conversation_context)):
        if str(item.get('tool_name', '')).strip() != 'orchestration.trace':
            continue
        request_payload = item.get('request_payload')
        if isinstance(request_payload, dict):
            payloads.append(request_payload)
    return payloads


def _recent_trace_used_tool(conversation_context: dict[str, Any] | None, tool_name: str) -> bool:
    for payload in _recent_orchestration_trace_payloads(conversation_context):
        selected_tools = payload.get('selected_tools')
        if not isinstance(selected_tools, list):
            continue
        if any(str(value).strip() == tool_name for value in selected_tools if isinstance(value, str)):
            return True
    return False


def _recent_trace_slot_memory(conversation_context: dict[str, Any] | None) -> dict[str, Any] | None:
    for payload in _recent_orchestration_trace_payloads(conversation_context):
        slot_memory = payload.get('slot_memory')
        if isinstance(slot_memory, dict) and slot_memory:
            return slot_memory
    return None


def _recent_slot_value(conversation_context: dict[str, Any] | None, key: str) -> str | None:
    slot_memory = _recent_trace_slot_memory(conversation_context)
    if not isinstance(slot_memory, dict):
        return None
    value = slot_memory.get(key)
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _recent_trace_focus(conversation_context: dict[str, Any] | None) -> dict[str, str] | None:
    slot_memory = _recent_trace_slot_memory(conversation_context)
    if isinstance(slot_memory, dict):
        focus_kind = str(slot_memory.get('focus_kind', '') or '').strip()
        protocol_code = str(slot_memory.get('protocol_code', '') or '').strip()
        active_task = str(slot_memory.get('active_task', '') or '').strip()
        active_entity = str(slot_memory.get('active_entity', '') or '').strip()
        pending_question_type = str(slot_memory.get('pending_question_type', '') or '').strip()
        if focus_kind or active_task or active_entity:
            inferred_focus_kind = focus_kind
            if active_task.startswith('public:'):
                inferred_focus_kind = 'public'
            elif not inferred_focus_kind:
                if active_task == 'workflow:visit_booking':
                    inferred_focus_kind = 'visit'
                elif active_task == 'workflow:institutional_request':
                    inferred_focus_kind = 'request'
                elif active_task == 'workflow:human_handoff':
                    inferred_focus_kind = 'support'
                elif active_task.startswith('finance:'):
                    inferred_focus_kind = 'finance'
                elif active_task.startswith('academic:'):
                    inferred_focus_kind = 'academic'
                elif active_task.startswith('admin:'):
                    inferred_focus_kind = 'secretaria'
            if active_task in NON_STICKY_PUBLIC_TASKS:
                return None
            if not _recent_focus_is_fresh(
                conversation_context,
                focus_kind=inferred_focus_kind,
                active_task=active_task,
            ):
                return None
            return {
                key: str(value).strip()
                for key, value in {
                    'kind': inferred_focus_kind,
                    'protocol_code': protocol_code,
                    'active_task': active_task,
                    'active_entity': active_entity,
                    'pending_question_type': pending_question_type,
                    'pending_disambiguation': slot_memory.get('pending_disambiguation'),
                    'public_entity': slot_memory.get('public_entity'),
                    'public_attribute': slot_memory.get('public_attribute'),
                    'requested_channel': slot_memory.get('requested_channel'),
                    'time_reference': slot_memory.get('time_reference'),
                    'academic_focus_kind': slot_memory.get('academic_focus_kind'),
                    'academic_attribute': slot_memory.get('academic_attribute'),
                    'admin_attribute': slot_memory.get('admin_attribute'),
                    'finance_status_filter': slot_memory.get('finance_status_filter'),
                    'finance_attribute': slot_memory.get('finance_attribute'),
                    'finance_action': slot_memory.get('finance_action'),
                }.items()
                if str(value or '').strip()
            }
    for payload in _recent_orchestration_trace_payloads(conversation_context):
        selected_tools = payload.get('selected_tools')
        if isinstance(selected_tools, list):
            selected_tool_names = {str(tool_name).strip() for tool_name in selected_tools if isinstance(tool_name, str)}
            if {'schedule_school_visit', 'update_visit_booking', 'get_workflow_status'} & selected_tool_names:
                return {'kind': 'visit', 'protocol_code': ''}
            if {'create_institutional_request', 'update_institutional_request'} & selected_tool_names:
                return {'kind': 'request', 'protocol_code': ''}
            if 'get_financial_summary' in selected_tool_names:
                return {'kind': 'finance', 'protocol_code': ''}
            if 'get_administrative_status' in selected_tool_names:
                return {'kind': 'secretaria', 'protocol_code': ''}
    return None


def _recent_visit_slot(conversation_context: dict[str, Any] | None) -> tuple[date | None, str | None]:
    if not isinstance(conversation_context, dict):
        return None, None
    recent_tool_calls = conversation_context.get('recent_tool_calls', [])
    if not isinstance(recent_tool_calls, list):
        return None, None
    for item in recent_tool_calls:
        if not isinstance(item, dict):
            continue
        tool_name = str(item.get('tool_name', '') or '').strip()
        if tool_name not in {'update_visit_booking', 'schedule_school_visit'}:
            continue
        response_payload = item.get('response_payload')
        if not isinstance(response_payload, dict):
            continue
        booking = response_payload.get('item')
        if not isinstance(booking, dict):
            continue
        preferred_date_raw = str(booking.get('preferred_date', '') or '').strip()
        preferred_window = str(booking.get('preferred_window', '') or '').strip() or None
        preferred_date: date | None = None
        if preferred_date_raw:
            try:
                preferred_date = date.fromisoformat(preferred_date_raw)
            except ValueError:
                preferred_date = None
        if preferred_date is not None or preferred_window is not None:
            return preferred_date, preferred_window
    for sender_type, content in reversed(_recent_message_lines(conversation_context)):
        if sender_type != 'assistant':
            continue
        normalized = _normalize_text(content)
        if 'preferencia informada:' not in normalized and 'nova preferencia:' not in normalized:
            continue
        slot_match = re.search(
            r'(?:nova preferencia|preferencia informada):\s*(\d{2}/\d{2}/\d{4})?(?:\s*-\s*)?([a-z0-9:]+)?',
            normalized,
        )
        if not slot_match:
            continue
        preferred_date: date | None = None
        preferred_window: str | None = None
        raw_date = (slot_match.group(1) or '').strip()
        raw_window = (slot_match.group(2) or '').strip()
        if raw_date:
            try:
                preferred_date = datetime.strptime(raw_date, '%d/%m/%Y').date()
            except ValueError:
                preferred_date = None
        if raw_window:
            preferred_window = raw_window
        if preferred_date is not None or preferred_window is not None:
            return preferred_date, preferred_window
    return None, None


def _assistant_already_introduced(conversation_context: dict[str, Any] | None) -> bool:
    for sender_type, content in _recent_message_lines(conversation_context):
        normalized = _normalize_text(content)
        if sender_type == 'assistant' and 'eduassist' in normalized and 'colegio horizonte' in normalized:
            return True
    return False


def _assistant_message_is_capability_overview(normalized_message: str) -> bool:
    return (
        'voce esta falando com o eduassist' in normalized_message
        or 'você está falando com o eduassist' in normalized_message
        or 'posso te ajudar com' in normalized_message
        or 'posso ajudar com informacoes publicas da escola' in normalized_message
    )


def _recent_conversation_focus(conversation_context: dict[str, Any] | None) -> dict[str, str] | None:
    trace_focus = _recent_trace_focus(conversation_context)
    if trace_focus:
        return trace_focus
    if not _recent_focus_is_fresh(conversation_context, focus_kind='public'):
        return None
    last_user_message: str | None = None
    for sender_type, content in reversed(_recent_message_lines(conversation_context)):
        normalized = _normalize_text(content)
        protocol_code = _extract_protocol_code_from_text(content)
        if sender_type == 'assistant':
            if _assistant_message_is_capability_overview(normalized):
                continue
            if 'pedido de visita registrado' in normalized or 'pedido de visita segue' in normalized or 'visita cancelada' in normalized:
                return {'kind': 'visit', 'protocol_code': protocol_code or ''}
            if 'solicitacao institucional registrada' in normalized or 'sua solicitacao institucional' in normalized:
                return {'kind': 'request', 'protocol_code': protocol_code or ''}
            if 'financeiro' in normalized and any(token in normalized for token in {'boleto', 'fatura', 'contrato'}):
                return {'kind': 'finance', 'protocol_code': protocol_code or ''}
            if 'secretaria' in normalized:
                return {'kind': 'secretaria', 'protocol_code': protocol_code or ''}
            if 'matricula' in normalized:
                return {'kind': 'admissions', 'protocol_code': protocol_code or ''}
        elif sender_type == 'user' and last_user_message is None:
            last_user_message = content

    if not last_user_message:
        return None

    normalized_user = _normalize_text(last_user_message)
    if any(_message_matches_term(normalized_user, term) for term in {'visita', 'tour', 'conhecer a escola'}):
        return {'kind': 'visit', 'protocol_code': ''}
    if any(_message_matches_term(normalized_user, term) for term in {'direcao', 'direção', 'protocolo', 'solicitacao'}):
        return {'kind': 'request', 'protocol_code': ''}
    if any(_message_matches_term(normalized_user, term) for term in {'boleto', 'fatura', 'mensalidade', 'financeiro'}):
        return {'kind': 'finance', 'protocol_code': ''}
    if any(_message_matches_term(normalized_user, term) for term in {'documento', 'historico', 'secretaria'}):
        return {'kind': 'secretaria', 'protocol_code': ''}
    if any(_message_matches_term(normalized_user, term) for term in {'matricula', 'bolsa', 'desconto'}):
        return {'kind': 'admissions', 'protocol_code': ''}
    return None


def _recent_focus_follow_up_line(conversation_context: dict[str, Any] | None) -> str | None:
    focus = _recent_conversation_focus(conversation_context)
    if not focus:
        return None
    protocol_code = focus.get('protocol_code', '').strip()
    suffix = f' com protocolo {protocol_code}' if protocol_code else ''
    kind = focus.get('kind')
    if kind == 'visit':
        return f'Se quiser, eu retomo sua visita{suffix} e sigo daqui.'
    if kind == 'request':
        return f'Se quiser, eu retomo sua solicitacao institucional{suffix} e te digo status, prazo ou proximo passo.'
    return None


def _is_private_admin_follow_up(
    message: str,
    conversation_context: dict[str, Any] | None,
) -> bool:
    normalized = _normalize_text(message)
    if not any(
        _message_matches_term(normalized, term)
        for term in {'documentacao', 'documentação', 'documentos', 'cadastro', 'email', 'telefone', 'dados cadastrais'}
    ):
        return False
    focus = _recent_conversation_focus(conversation_context)
    if not isinstance(focus, dict):
        return False
    if focus.get('kind') == 'finance':
        return True
    active_task = str(focus.get('active_task', '') or '').strip()
    return active_task.startswith('finance:') or active_task.startswith('admin:')


def _is_assistant_identity_query(message: str) -> bool:
    normalized = _normalize_text(message)
    normalized_simple = normalized.strip(' ?.!')
    if normalized_simple in {'com quem eu falo', 'pra quem eu falo', 'para quem eu falo'}:
        return True
    if any(_message_matches_term(normalized, term) for term in SERVICE_ROUTING_TERMS):
        return False
    return any(_message_matches_term(normalized, term) for term in ASSISTANT_IDENTITY_TERMS)


def _is_capability_query(message: str) -> bool:
    normalized = _normalize_text(message)
    return any(_message_matches_term(normalized, term) for term in ASSISTANT_CAPABILITY_TERMS)


def _is_access_scope_query(message: str) -> bool:
    normalized = _normalize_text(message)
    if 'consigo ver' in normalized and 'exatamente' in normalized:
        return True
    return any(_message_matches_term(normalized, term) for term in ACCESS_SCOPE_TERMS)


def _is_actor_identity_query(message: str) -> bool:
    normalized = _normalize_text(message)
    return any(_message_matches_term(normalized, term) for term in ACTOR_IDENTITY_TERMS)


def _is_auth_guidance_query(message: str) -> bool:
    normalized = _normalize_text(message)
    return any(_message_matches_term(normalized, term) for term in AUTH_GUIDANCE_TERMS)


def _is_public_pricing_navigation_query(message: str) -> bool:
    normalized = _normalize_text(message)
    if not any(_message_matches_term(normalized, term) for term in PUBLIC_PRICING_TERMS):
        return False
    return not any(_message_matches_term(normalized, term) for term in {'meu', 'minha', 'meus', 'minhas', 'do meu filho', 'da minha filha'})


def _is_service_routing_query(message: str) -> bool:
    normalized = _normalize_text(message)
    normalized_simple = normalized.strip(' ?.!')
    if normalized_simple in {'com quem eu falo', 'pra quem eu falo', 'para quem eu falo'}:
        return False
    return any(_message_matches_term(normalized, term) for term in SERVICE_ROUTING_TERMS)


def _map_request(request: MessageResponseRequest, user_context: UserContext) -> OrchestrationRequest:
    return OrchestrationRequest(
        message=request.message,
        conversation_id=request.conversation_id,
        user=user_context,
        allow_graph_rag=request.allow_graph_rag,
        allow_handoff=request.allow_handoff,
    )


def _parse_csv_slices(value: str | None) -> list[str]:
    return [item.strip() for item in str(value or '').split(',') if item.strip()]


def _build_preview_state_input(
    *,
    request: MessageResponseRequest,
    user_context: UserContext,
    settings: Any,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        'request': _map_request(request, user_context),
    }
    if bool(getattr(settings, 'langgraph_hitl_user_traffic_enabled', False)):
        payload['hitl_enabled'] = True
        payload['hitl_target_slices'] = _parse_csv_slices(getattr(settings, 'langgraph_hitl_user_traffic_slices', 'support'))
    return payload


def _build_langgraph_pending_review_message(*, preview: Any) -> str:
    if preview.classification.domain is QueryDomain.support:
        return (
            'Seu pedido entrou em revisao humana antes da proxima etapa para manter o atendimento seguro e rastreavel. '
            'Assim que a equipe validar esse ponto, eu sigo desta mesma conversa.'
        )
    if preview.classification.access_tier is not AccessTier.public:
        return (
            'Essa consulta ficou pendente de revisao antes da liberacao final, para proteger os dados da conta e manter a trilha auditavel. '
            'Assim que esse ponto for validado, eu continuo daqui.'
        )
    return (
        'Esse pedido ficou pendente de revisao antes da resposta final. '
        'Assim que a validacao for concluida, eu continuo desta mesma conversa.'
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


def _primary_public_entity_hint(message: str, conversation_context: dict[str, Any] | None = None) -> str | None:
    hints = sorted(_extract_public_entity_hints(message))
    if hints:
        return hints[0]
    return _recent_slot_value(conversation_context, 'public_entity')


def _should_reuse_public_context(
    *,
    message: str,
    public_plan: PublicInstitutionPlan | None,
) -> bool:
    if _is_follow_up_query(message):
        return True
    return bool(public_plan and public_plan.use_conversation_context)


def _should_track_contact_subject(
    *,
    message: str,
    public_plan: PublicInstitutionPlan | None,
    recent_focus: dict[str, Any],
) -> bool:
    if _requested_contact_channel(message) is not None or _contact_is_general_school_query(message):
        return True
    if public_plan is not None and public_plan.conversation_act in {
        'contacts',
        'service_routing',
        'document_submission',
        'careers',
        'teacher_directory',
        'leadership',
    }:
        return True
    return str(recent_focus.get('active_task', '') or '').strip() in {'public:contacts', 'public:service_routing'}


def _should_track_feature_key(
    *,
    message: str,
    public_plan: PublicInstitutionPlan | None,
    recent_focus: dict[str, Any],
) -> bool:
    if public_plan is not None and public_plan.conversation_act == 'features':
        return True
    if not _is_follow_up_query(message):
        return False
    return str(recent_focus.get('active_task', '') or '').strip() == 'public:features'


def _requested_operating_hours_attribute(
    message: str,
    conversation_context: dict[str, Any] | None = None,
) -> str | None:
    normalized = _normalize_text(message)
    if any(_message_matches_term(normalized, term) for term in {'fecha', 'fechar', 'fechamento', 'encerra', 'encerramento'}):
        return 'close_time'
    if any(_message_matches_term(normalized, term) for term in {'abre', 'abertura', 'abre as', 'abre às'}):
        return 'open_time'
    recent_attribute = _recent_slot_value(conversation_context, 'public_attribute')
    if recent_attribute in {'open_time', 'close_time'} and _is_follow_up_query(message):
        return recent_attribute
    return None


def _detect_admin_attribute_request(
    message: str,
    conversation_context: dict[str, Any] | None = None,
) -> str | None:
    normalized = _normalize_text(message)
    if any(_message_matches_term(normalized, term) for term in {'proximo passo', 'próximo passo', 'o que falta', 'qual o proximo passo'}):
        return 'next_step'
    if any(_message_matches_term(normalized, term) for term in {'status', 'situacao', 'situação', 'como esta'}):
        return 'status'
    if any(_message_matches_term(normalized, term) for term in {'documentos', 'documentacao', 'documentação', 'comprovante', 'comprovantes'}):
        return 'documents'
    if any(_message_matches_term(normalized, term) for term in {'telefone', 'celular', 'fone'}):
        return 'phone'
    if any(_message_matches_term(normalized, term) for term in {'email', 'e-mail', 'mail'}):
        return 'email'
    recent_attribute = _recent_slot_value(conversation_context, 'admin_attribute')
    if recent_attribute and _is_follow_up_query(message):
        return recent_attribute
    return None


def _derive_public_active_task(public_plan: PublicInstitutionPlan | None) -> str | None:
    if public_plan is None:
        return None
    return PUBLIC_ACTIVE_TASK_BY_ACT.get(public_plan.conversation_act, f'public:{public_plan.conversation_act}')


def _derive_public_active_entity(
    *,
    public_plan: PublicInstitutionPlan | None,
    public_entity: str | None,
    contact_subject: str | None,
    feature_key: str | None,
    current_message: str,
    time_reference: str | None,
) -> str | None:
    if public_plan is None:
        return None
    if public_plan.conversation_act == 'features':
        requested_features = _requested_public_features(current_message)
        if feature_key:
            return feature_key.replace('_', ' ')
        if len(requested_features) > 1:
            return 'escola'
    if public_entity:
        return public_entity
    if public_plan.conversation_act == 'contacts' and contact_subject:
        return contact_subject.lower()
    if public_plan.conversation_act == 'operating_hours' and _message_matches_term(_normalize_text(current_message), 'biblioteca'):
        return 'biblioteca'
    if public_plan.conversation_act == 'timeline' and time_reference:
        return time_reference
    return PUBLIC_ACTIVE_ENTITY_BY_ACT.get(public_plan.conversation_act)


def _derive_active_task(
    *,
    current_message: str,
    public_plan: PublicInstitutionPlan | None,
    focus_kind: str | None,
    academic_focus_kind: str | None,
    academic_student_name: str | None,
    finance_student_name: str | None,
    finance_attribute: str | None,
    finance_action: str | None,
    preview: Any | None,
) -> str | None:
    public_task = _derive_public_active_task(public_plan)
    if public_task:
        return public_task
    if preview is not None and getattr(preview, 'classification', None) is not None:
        domain = getattr(preview.classification, 'domain', None)
        selected_tool_names = {
            str(tool_name).strip()
            for tool_name in getattr(preview, 'selected_tools', [])
            if isinstance(tool_name, str)
        }
        if domain is QueryDomain.institution and 'get_administrative_status' in selected_tool_names:
            if 'get_student_administrative_status' in selected_tool_names and (
                academic_student_name or finance_student_name
            ):
                return 'admin:student_administrative_status'
            if _wants_profile_update_guidance(current_message):
                return 'admin:profile_update'
            return 'admin:administrative_status'
        if domain is QueryDomain.institution and 'get_actor_identity_context' in selected_tool_names:
            normalized_current = _normalize_text(current_message)
            if _is_access_scope_query(current_message):
                return 'admin:access_scope'
            if any(
                _message_matches_term(normalized_current, term)
                for term in {
                    'quais meus filhos',
                    'quais sao meus filhos',
                    'quais são meus filhos',
                    'quem sao meus filhos',
                    'quem são meus filhos',
                    'quais filhos tenho',
                    'filhos matriculados',
                    'filhos vinculados',
                    'alunos vinculados',
                }
            ):
                return 'admin:linked_students'
            return 'admin:actor_identity'
        if domain is QueryDomain.academic:
            return ACADEMIC_ACTIVE_TASK_BY_FOCUS.get(academic_focus_kind or '', 'academic:student_summary')
        if domain is QueryDomain.finance:
            if finance_action == 'second_copy':
                return 'finance:second_copy'
            if finance_attribute:
                return f'finance:{finance_attribute}'
            return 'finance:billing'
    if focus_kind:
        return WORKFLOW_ACTIVE_TASK_BY_KIND.get(focus_kind)
    return None


def _derive_active_entity(
    *,
    active_task: str | None,
    focus_kind: str | None,
    public_plan: PublicInstitutionPlan | None,
    public_entity: str | None,
    contact_subject: str | None,
    feature_key: str | None,
    current_message: str,
    time_reference: str | None,
    academic_student_name: str | None,
    finance_student_name: str | None,
) -> str | None:
    if active_task == 'admin:actor_identity':
        return 'sua conta'
    if active_task == 'admin:access_scope':
        return 'sua conta'
    if active_task == 'admin:linked_students':
        return 'seus alunos vinculados'
    if active_task and active_task.startswith('admin:'):
        if active_task == 'admin:student_administrative_status':
            return academic_student_name or finance_student_name or 'aluno'
        return 'seu cadastro'
    if active_task and active_task.startswith('academic:'):
        return academic_student_name or 'aluno'
    if active_task and active_task.startswith('finance:'):
        return finance_student_name or 'responsavel financeiro'
    public_entity_value = _derive_public_active_entity(
        public_plan=public_plan,
        public_entity=public_entity,
        contact_subject=contact_subject,
        feature_key=feature_key,
        current_message=current_message,
        time_reference=time_reference,
    )
    if public_entity_value:
        return public_entity_value
    if focus_kind:
        return WORKFLOW_ACTIVE_ENTITY_BY_KIND.get(focus_kind)
    return None


def _derive_pending_question_type(
    *,
    message: str,
    public_plan: PublicInstitutionPlan | None,
    public_attribute: str | None,
    requested_channel: str | None,
    academic_attribute: str | None,
    admin_attribute: str | None,
    finance_attribute: str | None,
    finance_action: str | None,
    time_reference: str | None,
    focus_kind: str | None,
) -> str | None:
    if public_plan is not None and public_plan.secondary_acts:
        return 'multi_intent'
    if _is_follow_up_query(message):
        return 'follow_up'
    if any(
        value
        for value in (
            public_attribute,
            requested_channel,
            academic_attribute,
            admin_attribute,
            finance_attribute,
            finance_action,
        )
    ):
        return 'attribute_query'
    if time_reference:
        return 'time_query'
    if focus_kind in {'visit', 'request'}:
        return 'workflow_query'
    return None


def _follow_up_context_phrase(active_task: str | None, active_entity: str | None) -> str | None:
    if not active_task:
        return None
    template = FOLLOW_UP_CONTEXT_BY_TASK.get(active_task)
    if not template:
        return None
    entity = (active_entity or 'esse assunto').strip()
    return template.format(entity=entity)


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


def _is_positive_requirement_query(message: str) -> bool:
    normalized = _normalize_text(message)
    if _is_negative_requirement_query(message):
        return False
    has_requirement = any(_message_matches_term(normalized, term) for term in REQUIREMENT_QUERY_TERMS)
    has_positive = any(
        _message_matches_term(normalized, term)
        for term in {'exigido', 'exigidos', 'exigida', 'exigidas', 'necessario', 'necessarios', 'preciso', 'levar'}
    )
    return has_requirement and has_positive


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


def _detect_time_reference(message: str) -> str | None:
    explicit_date = _extract_requested_date(message)
    if explicit_date is not None:
        return explicit_date.isoformat()
    normalized = _normalize_text(message)
    if _message_matches_term(normalized, 'amanha') or _message_matches_term(normalized, 'amanhã'):
        return 'tomorrow'
    if _message_matches_term(normalized, 'hoje'):
        return 'today'
    return None


def _detect_academic_attribute_request(message: str) -> ProtectedAttributeRequest | None:
    normalized = _normalize_text(message)
    if any(_message_matches_term(normalized, term) for term in ACADEMIC_IDENTITY_TERMS):
        return ProtectedAttributeRequest(domain='academic', attribute='enrollment_code')
    if any(_message_matches_term(normalized, term) for term in ATTENDANCE_TIMELINE_TERMS):
        return None
    if any(_message_matches_term(normalized, term) for term in UPCOMING_ASSESSMENT_TERMS):
        return None
    if _contains_any(message, ATTENDANCE_TERMS) and not _contains_any(message, GRADE_TERMS):
        return ProtectedAttributeRequest(domain='academic', attribute='attendance')
    if _contains_any(message, GRADE_TERMS):
        return ProtectedAttributeRequest(domain='academic', attribute='grades')
    return None


def _detect_finance_attribute_request(message: str) -> ProtectedAttributeRequest | None:
    normalized = _normalize_text(message)
    wants_open_amount = any(
        _message_matches_term(normalized, term)
        for term in {
            'quanto esta em aberto',
            'quanto está em aberto',
            'valor em aberto',
            'saldo em aberto',
            'quanto devo',
            'quanto estou devendo',
            'valor pendente',
        }
    ) or (
        any(_message_matches_term(normalized, term) for term in FINANCE_OPEN_TERMS)
        and any(
            _message_matches_term(normalized, term)
            for term in {'quanto', 'valor', 'saldo', 'devo', 'devendo'}
        )
    )
    if wants_open_amount:
        return ProtectedAttributeRequest(domain='finance', attribute='open_amount')
    if any(_message_matches_term(normalized, term) for term in FINANCE_NEXT_DUE_TERMS):
        return ProtectedAttributeRequest(domain='finance', attribute='next_due')
    if any(_message_matches_term(normalized, term) for term in FINANCE_IDENTIFIER_TERMS):
        return ProtectedAttributeRequest(domain='finance', attribute='invoice_id')
    if any(_message_matches_term(normalized, term) for term in FINANCE_CONTRACT_TERMS):
        return ProtectedAttributeRequest(domain='finance', attribute='contract_code')
    return None


def _wants_finance_second_copy(
    message: str,
    *,
    conversation_context: dict[str, Any] | None = None,
) -> bool:
    normalized = _normalize_text(message)
    if any(_message_matches_term(normalized, term) for term in FINANCE_SECOND_COPY_TERMS):
        return True
    recent_second_copy = _recent_slot_value(conversation_context, 'finance_action') == 'second_copy'
    if not recent_second_copy:
        return False
    if _is_follow_up_query(message):
        return True
    if any(_message_matches_term(normalized, term) for term in FINANCE_IDENTIFIER_TERMS | {'boleto', 'fatura'}):
        return True
    return False


def _effective_finance_status_filter(
    message: str,
    *,
    conversation_context: dict[str, Any] | None = None,
) -> set[str] | None:
    explicit = _detect_finance_status_filter(message)
    if explicit is not None:
        return explicit
    if not _is_follow_up_query(message):
        return None
    raw = _recent_slot_value(conversation_context, 'finance_status_filter')
    if not raw:
        return None
    values = {part.strip() for part in raw.split(',') if part.strip()}
    return values or None


def _effective_finance_attribute_request(
    message: str,
    *,
    conversation_context: dict[str, Any] | None = None,
) -> ProtectedAttributeRequest | None:
    explicit = _detect_finance_attribute_request(message)
    if explicit is not None:
        return explicit
    if not _is_follow_up_query(message):
        return None
    raw = _recent_slot_value(conversation_context, 'finance_attribute')
    if raw:
        return ProtectedAttributeRequest(domain='finance', attribute=raw)
    return None


def _effective_academic_attribute_request(
    message: str,
    *,
    conversation_context: dict[str, Any] | None = None,
) -> ProtectedAttributeRequest | None:
    explicit = _detect_academic_attribute_request(message)
    if explicit is not None:
        return explicit
    if not _is_follow_up_query(message):
        return None
    raw = _recent_slot_value(conversation_context, 'academic_attribute')
    if raw:
        return ProtectedAttributeRequest(domain='academic', attribute=raw)
    return None


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
    if any(
        _message_matches_term(normalized, term)
        for term in {
            'fundamental i',
            'anos iniciais',
            '1o ano do fundamental',
            '2o ano do fundamental',
            '3o ano do fundamental',
            '4o ano do fundamental',
            '5o ano do fundamental',
            'primeiro ano do fundamental',
            'segundo ano do fundamental',
            'terceiro ano do fundamental',
            'quarto ano do fundamental',
            'quinto ano do fundamental',
        }
    ):
        return 'Ensino Fundamental I'
    if any(_message_matches_term(normalized, term) for term in {'fundamental', 'fundamental ii', '6o ano', '7o ano', '8o ano', '9o ano'}):
        return 'Ensino Fundamental II'
    if any(_message_matches_term(normalized, term) for term in {'ensino medio', 'ensino médio', 'medio', 'médio', '1o ano', '2o ano', '3o ano'}):
        return 'Ensino Medio'
    return None


def _segment_semantic_key(value: str | None) -> str | None:
    normalized = _normalize_text(str(value or '').strip())
    if not normalized:
        return None
    if any(
        _message_matches_term(normalized, term)
        for term in {
            'fundamental i',
            'anos iniciais',
            '1o ano do fundamental',
            '2o ano do fundamental',
            '3o ano do fundamental',
            '4o ano do fundamental',
            '5o ano do fundamental',
            'primeiro ano do fundamental',
            'segundo ano do fundamental',
            'terceiro ano do fundamental',
            'quarto ano do fundamental',
            'quinto ano do fundamental',
        }
    ):
        return 'fundamental_i'
    if any(
        _message_matches_term(normalized, term)
        for term in {'fundamental ii', '6o ano', '7o ano', '8o ano', '9o ano'}
    ):
        return 'fundamental_ii'
    if 'fundamental' in normalized:
        return 'fundamental_ii'
    if any(
        _message_matches_term(normalized, term)
        for term in {
            'ensino medio',
            'ensino médio',
            'medio',
            'médio',
            '1a a 3a serie',
            '1a a 3a série',
            '1o ano',
            '2o ano',
            '3o ano',
        }
    ):
        return 'ensino_medio'
    return normalized


def _public_segment_matches(row_segment: str | None, requested_segment: str | None) -> bool:
    if requested_segment is None:
        return True
    return _segment_semantic_key(row_segment) == _segment_semantic_key(requested_segment)


def _extract_grade_reference(message: str) -> str | None:
    normalized = _normalize_text(message)
    match = re.search(r'\b(6o ano|7o ano|8o ano|9o ano|1o ano|2o ano|3o ano)\b', normalized)
    if not match:
        return None
    return match.group(1)


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


def _recent_public_feature_key(conversation_context: dict[str, Any] | None) -> str | None:
    for _sender_type, content in reversed(_recent_message_lines(conversation_context)):
        features = _requested_public_features(content)
        if len(features) == 1:
            return features[0]
        normalized = _normalize_text(content)
        for feature_key in (
            'biblioteca',
            'cantina',
            'laboratorio',
            'maker',
            'quadra',
            'piscina',
            'futebol',
            'volei',
            'teatro',
            'danca',
        ):
            if _message_matches_term(normalized, feature_key):
                return feature_key
    return None


def _recent_public_contact_subject(
    profile: dict[str, Any],
    conversation_context: dict[str, Any] | None,
) -> str | None:
    recent_service = _recent_service_match(profile, conversation_context)
    if recent_service is not None:
        title = str(recent_service.get('title', '')).strip()
        if title:
            return title
    for _sender_type, content in reversed(_recent_message_lines(conversation_context)):
        normalized = _normalize_text(content)
        if any(_message_matches_term(normalized, term) for term in {'orientacao educacional', 'orientação educacional', 'bullying', 'socioemocional'}):
            return 'Orientacao educacional'
        if any(_message_matches_term(normalized, term) for term in {'financeiro', 'boleto', 'boletos'}):
            return 'Financeiro'
        if any(_message_matches_term(normalized, term) for term in {'diretora', 'diretor', 'direcao', 'direção', 'diretoria'}):
            return 'Direcao'
        if any(_message_matches_term(normalized, term) for term in {'coordenacao', 'coordenação'}):
            return 'Coordenacao'
        if any(_message_matches_term(normalized, term) for term in {'admissoes', 'admissões', 'matricula', 'matrícula', 'visita', 'tour'}):
            return 'Admissoes'
        if any(_message_matches_term(normalized, term) for term in {'secretaria'}):
            return 'Secretaria'
    return None


def _public_contact_reference_message(
    *,
    profile: dict[str, Any],
    source_message: str,
    analysis_message: str,
    conversation_context: dict[str, Any] | None,
) -> str:
    if not _is_follow_up_query(source_message):
        return source_message
    subject = _recent_public_contact_subject(profile, conversation_context)
    if subject:
        return f'{source_message} sobre {subject}'
    return analysis_message


def _preferred_contact_labels_from_context(
    profile: dict[str, Any],
    source_message: str,
    conversation_context: dict[str, Any] | None,
) -> list[str]:
    normalized = _normalize_text(source_message)
    preferred: list[str] = []

    def add(label: str) -> None:
        cleaned = label.strip()
        if cleaned and cleaned not in preferred:
            preferred.append(cleaned)

    explicit_terms = (
        ('Direcao', {'direcao', 'direção', 'diretoria', 'diretora', 'diretor'}),
        ('Coordenacao', {'coordenacao', 'coordenação', 'coordenador', 'coordenadora'}),
        ('Secretaria', {'secretaria'}),
        ('Financeiro', {'financeiro', 'boleto', 'boletos', 'mensalidade', 'fatura', 'faturas', 'contrato'}),
        ('Admissoes', {'admissoes', 'admissões', 'matricula', 'matrícula', 'visita', 'tour'}),
        ('Orientacao educacional', {'orientacao educacional', 'orientação educacional', 'bullying', 'socioemocional'}),
    )
    for label, terms in explicit_terms:
        if any(_message_matches_term(normalized, term) for term in terms):
            add(label)

    recent_service = _recent_service_match(profile, conversation_context)
    if isinstance(recent_service, dict):
        service_key = str(recent_service.get('service_key', '')).strip().lower()
        service_preferences = {
            'orientacao_educacional': 'Orientacao educacional',
            'financeiro_escolar': 'Financeiro',
            'visita_institucional': 'Admissoes',
            'solicitacao_direcao': 'Direcao',
            'secretaria_escolar': 'Secretaria',
        }
        preferred_label = service_preferences.get(service_key)
        if preferred_label:
            add(preferred_label)

    for _sender_type, content in reversed(_recent_message_lines(conversation_context)):
        content_normalized = _normalize_text(content)
        if any(_message_matches_term(content_normalized, term) for term in {'orientacao educacional', 'orientação educacional', 'bullying', 'socioemocional'}):
            add('Orientacao educacional')
            break
        if any(_message_matches_term(content_normalized, term) for term in {'financeiro', 'boleto', 'boletos'}):
            add('Financeiro')
            break
        if any(_message_matches_term(content_normalized, term) for term in {'diretora', 'diretor', 'direcao', 'direção', 'diretoria'}):
            add('Direcao')
            break
        if any(_message_matches_term(content_normalized, term) for term in {'coordenacao', 'coordenação'}):
            add('Coordenacao')
            break
        if any(_message_matches_term(content_normalized, term) for term in {'admissoes', 'admissões', 'matricula', 'matrícula', 'visita', 'tour'}):
            add('Admissoes')
            break
        if any(_message_matches_term(content_normalized, term) for term in {'secretaria'}):
            add('Secretaria')
            break
    return preferred


def _build_conversation_slot_memory(
    *,
    actor: dict[str, Any] | None,
    profile: dict[str, Any] | None,
    conversation_context: dict[str, Any] | None,
    request_message: str | None = None,
    public_plan: PublicInstitutionPlan | None = None,
    preview: Any | None = None,
) -> ConversationSlotMemory:
    focus = _recent_conversation_focus(conversation_context) or {}
    protocol_code = str(focus.get('protocol_code', '') or '').strip() or None
    focus_kind = str(focus.get('kind', '') or '').strip() or None
    safe_profile = profile if isinstance(profile, dict) else {}
    current_message = request_message or ''
    allow_public_context = _should_reuse_public_context(
        message=current_message,
        public_plan=public_plan,
    )
    public_entity = (
        (public_plan.focus_hint if public_plan and public_plan.focus_hint else None)
        or _primary_public_entity_hint(
            current_message,
            conversation_context if allow_public_context else None,
        )
    )
    public_attribute = (
        (public_plan.requested_attribute if public_plan and public_plan.requested_attribute else None)
        or (_recent_slot_value(conversation_context, 'public_attribute') if allow_public_context else None)
    )
    requested_channel = (
        (public_plan.requested_channel if public_plan and public_plan.requested_channel else None)
        or (_recent_slot_value(conversation_context, 'requested_channel') if allow_public_context else None)
    )
    time_reference = _detect_time_reference(current_message) or (
        _recent_slot_value(conversation_context, 'time_reference') if allow_public_context else None
    )
    academic_student = _recent_student_from_context(
        actor,
        capability='academic',
        conversation_context=conversation_context,
    )
    finance_student = _recent_student_from_context(
        actor,
        capability='finance',
        conversation_context=conversation_context,
    )
    mentioned_student = _student_focus_candidate(actor, current_message)
    if academic_student is None and isinstance(mentioned_student, dict) and bool(mentioned_student.get('can_view_academic', False)):
        academic_student = mentioned_student
    if finance_student is None and isinstance(mentioned_student, dict) and bool(mentioned_student.get('can_view_finance', False)):
        finance_student = mentioned_student
    preview_domain = getattr(getattr(preview, 'classification', None), 'domain', None)
    if (
        preview_domain not in {QueryDomain.academic, QueryDomain.finance}
        and mentioned_student is None
        and not _is_student_focus_activation_query(current_message, actor)
        and not _is_children_overview_query(current_message, actor)
    ):
        academic_student = None
        finance_student = None
    academic_focus_kind = None
    academic_attribute = None
    admin_attribute = None
    finance_status_filter = None
    finance_attribute = None
    finance_action = None
    if public_plan is not None and public_plan.conversation_act == 'operating_hours':
        public_attribute = _requested_operating_hours_attribute(
            current_message,
            conversation_context=conversation_context,
        ) or public_attribute
    if preview is not None and getattr(preview, 'classification', None) is not None:
        domain = getattr(preview.classification, 'domain', None)
        if domain is QueryDomain.support and not focus_kind:
            selected_tool_names = {
                str(tool_name).strip()
                for tool_name in getattr(preview, 'selected_tools', [])
                if isinstance(tool_name, str)
            }
            if {'schedule_school_visit', 'update_visit_booking'} & selected_tool_names:
                focus_kind = 'visit'
            elif {'create_institutional_request', 'update_institutional_request'} & selected_tool_names:
                focus_kind = 'request'
            elif 'create_support_ticket' in selected_tool_names and any(
                _message_matches_term(_normalize_text(current_message), term) for term in SUPPORT_FINANCE_TERMS
            ):
                focus_kind = 'finance'
            elif {'create_support_ticket', 'handoff_to_human'} & selected_tool_names:
                focus_kind = 'support'
        if domain is QueryDomain.academic:
            academic_focus_kind = _detect_academic_focus_kind(current_message) or _recent_slot_value(
                conversation_context,
                'academic_focus_kind',
            )
            academic_attribute_request = _effective_academic_attribute_request(
                current_message,
                conversation_context=conversation_context,
            )
            academic_attribute = (
                academic_attribute_request.attribute if academic_attribute_request is not None else None
            ) or _recent_slot_value(conversation_context, 'academic_attribute')
        elif domain is QueryDomain.finance:
            effective_status = _effective_finance_status_filter(
                current_message,
                conversation_context=conversation_context,
            )
            finance_status_filter = ','.join(sorted(effective_status)) if effective_status else _recent_slot_value(
                conversation_context,
                'finance_status_filter',
            )
            finance_attribute_request = _effective_finance_attribute_request(
                current_message,
                conversation_context=conversation_context,
            )
            finance_attribute = (
                finance_attribute_request.attribute if finance_attribute_request is not None else None
            ) or _recent_slot_value(conversation_context, 'finance_attribute')
            if _wants_finance_second_copy(current_message, conversation_context=conversation_context):
                finance_action = 'second_copy'
            else:
                finance_action = _recent_slot_value(conversation_context, 'finance_action')
        elif domain is QueryDomain.institution:
            selected_tool_names = {
                str(tool_name).strip()
                for tool_name in getattr(preview, 'selected_tools', [])
                if isinstance(tool_name, str)
            }
            if {'get_administrative_status', 'get_student_administrative_status'} & selected_tool_names:
                admin_attribute = _detect_admin_attribute_request(
                    current_message,
                    conversation_context=conversation_context,
                ) or _recent_slot_value(conversation_context, 'admin_attribute')
    if public_plan is not None:
        focus_kind = 'public'
    contact_subject = (
        _recent_public_contact_subject(safe_profile, conversation_context)
        if _should_track_contact_subject(
            message=current_message,
            public_plan=public_plan,
            recent_focus=focus,
        )
        else None
    )
    feature_key = (
        _recent_public_feature_key(conversation_context)
        if _should_track_feature_key(
            message=current_message,
            public_plan=public_plan,
            recent_focus=focus,
        )
        else None
    )
    academic_student_name = (
        str(academic_student.get('full_name', '')).strip() if isinstance(academic_student, dict) else None
    ) or None
    finance_student_name = (
        str(finance_student.get('full_name', '')).strip() if isinstance(finance_student, dict) else None
    ) or None
    active_task = _derive_active_task(
        current_message=current_message,
        public_plan=public_plan,
        focus_kind=focus_kind,
        academic_focus_kind=academic_focus_kind,
        academic_student_name=academic_student_name,
        finance_student_name=finance_student_name,
        finance_attribute=finance_attribute,
        finance_action=finance_action,
        preview=preview,
    )
    active_entity = _derive_active_entity(
        active_task=active_task,
        focus_kind=focus_kind,
        public_plan=public_plan,
        public_entity=public_entity,
        contact_subject=contact_subject,
        feature_key=feature_key,
        current_message=current_message,
        time_reference=time_reference,
        academic_student_name=academic_student_name,
        finance_student_name=finance_student_name,
    )
    pending_question_type = _derive_pending_question_type(
        message=current_message,
        public_plan=public_plan,
        public_attribute=public_attribute,
        requested_channel=requested_channel,
        academic_attribute=academic_attribute,
        admin_attribute=admin_attribute,
        finance_attribute=finance_attribute,
        finance_action=finance_action,
        time_reference=time_reference,
        focus_kind=focus_kind,
    )
    pending_disambiguation = _derive_pending_disambiguation(
        actor=actor,
        message=current_message,
        preview=preview,
        conversation_context=conversation_context,
    )
    return ConversationSlotMemory(
        focus_kind=focus_kind,
        protocol_code=protocol_code,
        contact_subject=contact_subject,
        feature_key=feature_key,
        active_task=active_task,
        active_entity=active_entity,
        pending_question_type=pending_question_type,
        pending_disambiguation=pending_disambiguation,
        public_entity=public_entity,
        public_attribute=public_attribute,
        requested_channel=requested_channel,
        time_reference=time_reference,
        academic_student_name=academic_student_name,
        academic_focus_kind=academic_focus_kind,
        academic_attribute=academic_attribute,
        admin_attribute=admin_attribute,
        finance_student_name=finance_student_name,
        finance_status_filter=finance_status_filter,
        finance_attribute=finance_attribute,
        finance_action=finance_action,
    )


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


def _is_public_feature_query(message: str) -> bool:
    normalized = _normalize_text(message)
    if _requested_public_features(message):
        return True
    return any(
        _message_matches_term(normalized, term)
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
            *PUBLIC_ENRICHMENT_TERMS,
        }
    )


def _asks_why_feature_is_missing(message: str) -> bool:
    normalized = _normalize_text(message)
    return any(
        _message_matches_term(normalized, term)
        for term in {
            'por que nao tem',
            'por que não tem',
            'por que nao possui',
            'por que não possui',
            'por que nao oferece',
            'por que não oferece',
            'por que nao existe',
            'por que não existe',
        }
    )


def _extract_feature_gap_focus(message: str) -> str | None:
    normalized = _normalize_text(message)
    cleaned = re.sub(
        r'^(?:e\s+)?(?:essa escola|o colegio|o col[eé]gio|a escola)?\s*(?:tem|possui|oferece|tem aula de|aula de|oficina de|curso de|atividade de|por que nao tem|por que nao possui|por que nao oferece|por que nao existe)\s+',
        '',
        normalized,
    ).strip(' ?.')
    if cleaned.startswith('e '):
        cleaned = cleaned[2:].strip()
    if cleaned:
        return cleaned
    salient = sorted(_extract_salient_terms(message))
    if salient:
        return ' '.join(salient[:4])
    return None


def _feature_suggestion_replies(feature_keys: list[str]) -> list[str]:
    if 'biblioteca' in feature_keys:
        return ['Qual o horario da biblioteca?', 'Qual o endereco da escola?', 'Quero agendar uma visita', 'Quais atividades a escola oferece?']
    if any(key in feature_keys for key in {'maker', 'danca', 'futebol', 'volei', 'teatro', 'laboratorio'}):
        return ['Quais atividades no contraturno a escola oferece?', 'Tem horarios dessas atividades?', 'Quero agendar uma visita', 'Qual o horario do 9o ano?']
    return ['Quais atividades a escola oferece?', 'Quero agendar uma visita', 'Qual o horario do 9o ano?', 'Como vinculo minha conta?']


def _compose_public_feature_answer(
    *,
    profile: dict[str, Any],
    original_message: str,
    analysis_message: str,
    conversation_context: dict[str, Any] | None = None,
) -> str | None:
    feature_map = _feature_inventory_map(profile)
    school_name = str(profile.get('school_name', 'Colegio Horizonte'))
    requested_features = _requested_public_features(original_message)
    requested_attributes = set(_requested_public_attributes(original_message))
    recent_focus = _recent_trace_focus(conversation_context)
    feature_followup_context = (
        isinstance(recent_focus, dict)
        and str(recent_focus.get('active_task', '')).strip() == 'public:features'
    )
    if not requested_features and 'name' in requested_attributes and _is_follow_up_query(original_message):
        recent_feature = _recent_public_feature_key(conversation_context)
        if recent_feature:
            requested_features = [recent_feature]
    if (
        not requested_features
        and _is_follow_up_query(original_message)
        and not _is_public_feature_query(original_message)
    ):
        focus = _extract_feature_gap_focus(original_message)
        if (
            feature_followup_context
            and focus
            and focus not in {'atividade', 'atividades', 'contraturno'}
        ):
            return (
                f'Nao vi uma referencia oficial sobre {focus} no perfil publico do {school_name}. '
                'Se quiser, eu posso te mostrar o que esta documentado sobre estrutura e atividades.'
            )
        requested_features = _requested_public_features(analysis_message)
    if not requested_features and _is_follow_up_query(original_message):
        recent_feature = _recent_public_feature_key(conversation_context)
        if recent_feature:
            requested_features = [recent_feature]
    asks_why_absent = _asks_why_feature_is_missing(original_message)
    if not requested_features and _is_public_feature_query(original_message):
        generic_activity_query = any(
            _message_matches_term(_normalize_text(original_message), term)
            for term in {'atividade', 'atividades', 'contraturno'}
        ) and not any(
            _message_matches_term(_normalize_text(original_message), term)
            for term in {'aula de', 'oficina de', 'curso de', 'clube de', 'atividade de'}
        )
        generic_structure_query = any(
            _message_matches_term(_normalize_text(original_message), term)
            for term in {'estrutura', 'infraestrutura', 'espaco', 'espaço', 'espacos', 'espaços', 'campus'}
        )
        focus = _extract_feature_gap_focus(original_message)
        if (
            focus
            and not generic_activity_query
            and not generic_structure_query
            and focus not in {'atividade', 'atividades', 'contraturno'}
        ):
            return (
                f'Nao vi uma referencia oficial sobre {focus} no perfil publico do {school_name}. '
                'Se voce quiser, eu posso te dizer quais atividades e espacos aparecem oficialmente.'
            )
        available_items: list[str] = []
        for feature_key in (
            'biblioteca',
            'maker',
            'quadra',
            'futebol',
            'volei',
            'danca',
            'teatro',
            'cantina',
            'orientacao educacional',
        ):
            item = feature_map.get(feature_key)
            if not item or not bool(item.get('available')):
                continue
            label = str(item.get('label', feature_key)).strip().lower()
            if label and label not in available_items:
                available_items.append(label)
        if available_items:
            preview = ', '.join(available_items[:5])
            return (
                f'Hoje, a estrutura do {school_name} inclui atividades e espacos como {preview}. '
                'Se quiser, eu posso te detalhar qualquer um deles.'
            )
        return (
            f'Hoje o perfil publico do {school_name} nao traz esse detalhe de estrutura ou atividade. '
            'Se quiser, eu posso te mostrar o que esta oficialmente documentado.'
        )
    if not requested_features:
        return None
    if len(requested_features) == 1:
        feature_key = requested_features[0]
        item = feature_map.get(feature_key)
        if item is None:
            return (
                f'Nao vi uma referencia oficial sobre {feature_key} no perfil publico do {school_name}. '
                'Se quiser, eu posso te mostrar o que esta documentado sobre estrutura e atividades.'
            )
        label = str(item.get('label', feature_key)).strip()
        notes = str(item.get('notes', '')).strip()
        available = bool(item.get('available'))
        if available and 'name' in requested_attributes:
            return f'O nome desse espaco e {label}.'
        if available:
            if asks_why_absent:
                return f'Na verdade, o {school_name} tem sim {label}. {notes}'.strip()
            if feature_key == 'biblioteca':
                return f'Sim. O {school_name} tem a {label}. {notes}'.strip()
            return f'Sim. O {school_name} oferece {label}. {notes}'.strip()
        if asks_why_absent:
            return f'Hoje o {school_name} nao oferece {label}. {notes}'.strip()
        return f'Nao. O {school_name} nao oferece {label}. {notes}'.strip()

    lines = [f'Sobre estrutura e atividades do {school_name}:']
    for feature_key in requested_features:
        item = feature_map.get(feature_key)
        if item is None:
            lines.append(f'- Ainda nao encontrei uma informacao oficial sobre {feature_key}.')
            continue
        label = str(item.get('label', feature_key)).strip()
        notes = str(item.get('notes', '')).strip()
        available = bool(item.get('available'))
        if available:
            lines.append(f'- Sim: {label}. {notes}'.rstrip())
        else:
            lines.append(f'- Nao: {label}. {notes}'.rstrip())
    return '\n'.join(lines)


def _compose_public_feature_schedule_follow_up(
    *,
    profile: dict[str, Any],
    original_message: str,
    analysis_message: str,
    conversation_context: dict[str, Any] | None,
) -> str | None:
    if not any(
        _message_matches_term(_normalize_text(original_message), term)
        for term in PUBLIC_SCHEDULE_TERMS | {'funciona quando', 'isso funciona quando'}
    ):
        return None
    requested_features = _requested_public_features(original_message)
    if (
        not requested_features
        and _is_follow_up_query(original_message)
        and not _is_public_feature_query(original_message)
    ):
        requested_features = _requested_public_features(analysis_message)
    if not requested_features and _is_follow_up_query(original_message):
        recent_feature = _recent_public_feature_key(conversation_context)
        if recent_feature:
            requested_features = [recent_feature]
    if len(requested_features) != 1:
        return None
    item = _feature_inventory_map(profile).get(requested_features[0])
    if item is None or not bool(item.get('available')):
        return None
    label = str(item.get('label', requested_features[0])).strip()
    notes = str(item.get('notes', '')).strip()
    if not notes:
        return None
    normalized_notes = _normalize_text(notes)
    if not any(
        marker in normalized_notes
        for marker in ('segunda', 'terca', 'terça', 'quarta', 'quinta', 'sexta', 'sabado', 'sábado', 'domingo', 'contraturno', '7h', '8h', '9h', '10h', '11h', '12h', '13h', '14h', '15h', '16h', '17h', '18h')
    ):
        return None
    return f'O horario de {label} hoje funciona assim: {notes}'


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


def _school_subject_reference(reference: str) -> str:
    cleaned = reference.strip()
    if cleaned.startswith(('a ', 'o ')):
        return cleaned
    return f'o {cleaned}'


def _school_object_reference(reference: str) -> str:
    cleaned = reference.strip()
    if cleaned == 'a escola':
        return 'da escola'
    if cleaned.startswith(('a ', 'o ')):
        return f'd{cleaned}'
    return f'de {cleaned}'


def _published_public_segments(profile: dict[str, Any]) -> set[str]:
    return {
        str(item).strip()
        for item in profile.get('segments', [])
        if isinstance(item, str) and str(item).strip()
    }


def _requested_unpublished_public_segment(context: PublicProfileContext) -> str | None:
    requested_segment = _select_public_segment(context.source_message)
    if not requested_segment:
        return None
    requested_key = _segment_semantic_key(requested_segment)
    if any(
        _segment_semantic_key(published_segment) == requested_key
        for published_segment in _published_public_segments(context.profile)
    ):
        return None
    return requested_segment


def _compose_public_segment_scope_gap(
    context: PublicProfileContext,
    *,
    requested_segment: str,
    topic: str,
) -> str:
    published_segments = sorted(_published_public_segments(context.profile))
    published_text = ', '.join(published_segments) if published_segments else 'os segmentos hoje publicados'
    return (
        f'Hoje eu nao tenho um detalhamento publico de {topic} para {requested_segment.lower()} em {context.school_reference}. '
        f'Pelo que a escola publica aqui, o recorte institucional coberto hoje e {published_text}.'
    )


def _contact_entries(profile: dict[str, Any], channel: str) -> list[dict[str, str]]:
    contacts = profile.get('contact_channels')
    if not isinstance(contacts, list):
        return []
    entries: list[dict[str, str]] = []
    for item in contacts:
        if not isinstance(item, dict):
            continue
        if str(item.get('channel', '')).lower() != channel:
            continue
        label = str(item.get('label', '')).strip()
        value = str(item.get('value', '')).strip()
        if not value:
            continue
        entries.append({'label': label, 'value': value})
    return entries


def _requested_contact_channel(message: str) -> str | None:
    normalized = _normalize_text(message)
    if any(_message_matches_term(normalized, term) for term in {'whatsapp', 'whats', 'zap'}):
        return 'whatsapp'
    if any(_message_matches_term(normalized, term) for term in {'email', 'e-mail', 'mail'}):
        return 'email'
    if any(_message_matches_term(normalized, term) for term in {'telefone', 'fone', 'ligacao', 'ligação', 'ligar', 'ligo', 'fax'}):
        return 'telefone'
    return None


def _is_public_social_query(message: str) -> bool:
    normalized = _normalize_text(message)
    return any(_message_matches_term(normalized, term) for term in PUBLIC_SOCIAL_TERMS)


def _is_public_careers_query(message: str) -> bool:
    normalized = _normalize_text(message)
    return any(_message_matches_term(normalized, term) for term in PUBLIC_CAREERS_TERMS)


def _is_public_web_query(message: str) -> bool:
    normalized = _normalize_text(message)
    return any(_message_matches_term(normalized, term) for term in PUBLIC_WEB_TERMS)


def _is_public_curriculum_query(message: str) -> bool:
    normalized = _normalize_text(message)
    if any(_message_matches_term(normalized, term) for term in PUBLIC_CURRICULUM_TERMS):
        return True
    if any(_message_matches_term(normalized, term) for term in PUBLIC_PEDAGOGICAL_TERMS):
        return True
    if _message_matches_term(normalized, 'acolhimento') and any(
        _message_matches_term(normalized, term)
        for term in {'disciplina', 'disciplinas', 'convivencia', 'convivência', 'aprendizagem', 'rotina'}
    ):
        return True
    return any(_message_matches_term(normalized, term) for term in {'materia', 'materias', 'disciplina', 'disciplinas'}) and any(
        _message_matches_term(normalized, term)
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


def _is_public_operating_hours_query(message: str) -> bool:
    normalized = _normalize_text(message)
    if any(_message_matches_term(normalized, term) for term in PUBLIC_OPERATING_HOURS_TERMS):
        return True
    return _contains_any(normalized, {'abre', 'abertura', 'funciona', 'fecha', 'fechamento'}) and _contains_any(
        normalized,
        {'amanha', 'amanhã', 'cedo', 'horas', 'hora', 'horario', 'horário'},
    )


def _is_public_timeline_query(message: str) -> bool:
    normalized = _normalize_text(message)
    asks_timing = any(
        _message_matches_term(normalized, term)
        for term in {
            'quando',
            'qual data',
            'que dia',
            'quando comeca',
            'quando começa',
            'quando fecha',
            'inicio',
            'início',
            'abertura',
            'comecam as aulas',
            'começam as aulas',
        }
    )
    if not asks_timing:
        return False
    return any(
        _message_matches_term(normalized, term)
        for term in {
            'matricula',
            'matrícula',
            'formatura',
            'inicio das aulas',
            'início das aulas',
            'comecam as aulas',
            'começam as aulas',
            'ano letivo',
        }
    )


def _is_public_calendar_event_query(message: str) -> bool:
    normalized = _normalize_text(message)
    if any(
        _message_matches_term(normalized, term)
        for term in {
            'proximo evento',
            'próximo evento',
            'proxima reuniao',
            'próxima reunião',
            'reuniao de pais',
            'reunião de pais',
            'reuniao geral',
            'reunião geral',
            'mostra de ciencias',
            'mostra de ciências',
            'plantao pedagogico',
            'plantão pedagógico',
            'visita guiada',
        }
    ):
        return True
    asks_timing = any(
        _message_matches_term(normalized, term)
        for term in {'quando', 'qual data', 'que dia', 'quando vai ser', 'quando acontece'}
    )
    if not asks_timing:
        return False
    return any(
        _message_matches_term(normalized, term)
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


def _is_public_date_query(message: str) -> bool:
    normalized = _normalize_text(message)
    return any(_message_matches_term(normalized, term) for term in PUBLIC_UTILITY_DATE_TERMS)


def _format_brazilian_date(value: date) -> str:
    month_names = {
        1: 'janeiro',
        2: 'fevereiro',
        3: 'marco',
        4: 'abril',
        5: 'maio',
        6: 'junho',
        7: 'julho',
        8: 'agosto',
        9: 'setembro',
        10: 'outubro',
        11: 'novembro',
        12: 'dezembro',
    }
    return f'{value.day} de {month_names.get(value.month, str(value.month))} de {value.year}'


def _parse_iso_date_value(value: Any) -> date | None:
    if isinstance(value, date):
        return value
    text = str(value or '').strip()
    if not text:
        return None
    try:
        return date.fromisoformat(text[:10])
    except ValueError:
        return None


def _format_public_date_text(value: Any) -> str:
    parsed = _parse_iso_date_value(value)
    if parsed is not None:
        return _format_brazilian_date(parsed)
    return str(value or 'data nao informada').strip() or 'data nao informada'


def _format_contact_origin(label: str | None, channel: str) -> str:
    cleaned = (label or '').strip().lower()
    if not cleaned:
        return ''
    if channel == 'telefone':
        return f'na {cleaned}'
    return f'pela {cleaned}'


def _wants_contact_list(message: str) -> bool:
    normalized = _normalize_text(message)
    return any(
        _message_matches_term(normalized, term)
        for term in {'quais', 'lista', 'todos', 'todas', 'contatos', 'canais', 'telefones', 'emails', 'e-mails'}
    )


def _contact_is_general_school_query(message: str) -> bool:
    normalized = _normalize_text(message)
    return any(
        _message_matches_term(normalized, term)
        for term in {'da escola', 'pra escola', 'para a escola', 'do colegio', 'do colégio', 'geral', 'institucional', 'principal'}
    )


def _select_primary_contact_entry(
    profile: dict[str, Any],
    channel: str,
    message: str,
    *,
    preferred_labels: list[str] | None = None,
) -> dict[str, str] | None:
    entries = _contact_entries(profile, channel)
    if not entries:
        return None

    normalized = _normalize_text(message)
    normalized_preferred = [_normalize_text(label) for label in preferred_labels or [] if label]
    for entry in entries:
        label = _normalize_text(entry.get('label', ''))
        if label and label in normalized:
            return entry

    for preferred_label in normalized_preferred:
        for entry in entries:
            label = _normalize_text(entry.get('label', ''))
            if label == preferred_label:
                return entry

    label_aliases = {
        'direcao': {'direcao', 'direção', 'diretoria', 'diretora', 'diretor'},
        'secretaria': {'secretaria', 'secretaria escolar', 'secretaria digital'},
        'orientacao educacional': {'orientacao educacional', 'orientação educacional', 'bullying', 'socioemocional'},
        'financeiro': {'financeiro', 'boleto', 'boletos', 'mensalidade', 'fatura', 'faturas', 'contrato'},
        'admissoes': {'admissoes', 'admissões', 'matricula', 'matrícula', 'visita', 'tour'},
    }
    for entry in entries:
        label = _normalize_text(entry.get('label', ''))
        aliases = label_aliases.get(label, set())
        if aliases and any(_message_matches_term(normalized, alias) for alias in aliases):
            return entry

    if _contact_is_general_school_query(message):
        priorities_by_channel = {
            'telefone': ['secretaria'],
            'email': ['secretaria'],
            'whatsapp': ['secretaria digital', 'atendimento comercial'],
        }
        for preferred_label in priorities_by_channel.get(channel, []):
            for entry in entries:
                if _normalize_text(entry.get('label', '')) == preferred_label:
                    return entry

    return entries[0]


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


def _public_feature_inventory(profile: dict[str, Any]) -> list[dict[str, Any]]:
    entries = profile.get('feature_inventory')
    return [item for item in entries if isinstance(item, dict)] if isinstance(entries, list) else []


def _capability_summary_lines(profile: dict[str, Any]) -> list[str]:
    capability_model = profile.get('assistant_capabilities')
    school_name = str(
        (capability_model.get('school_name') if isinstance(capability_model, dict) else None)
        or profile.get('school_name', 'Colegio Horizonte')
    )
    segments_source = (
        capability_model.get('segments')
        if isinstance(capability_model, dict)
        else profile.get('segments', [])
    )
    segments = [str(item) for item in segments_source if isinstance(item, str)]
    segment_summary = ', '.join(segments[:2]).lower() if segments else 'os segmentos atendidos'
    public_topics = [
        str(item) for item in (
            capability_model.get('public_topics', []) if isinstance(capability_model, dict) else []
        ) if isinstance(item, str)
    ]
    protected_topics = [
        str(item) for item in (
            capability_model.get('protected_topics', []) if isinstance(capability_model, dict) else []
        ) if isinstance(item, str)
    ]
    workflow_topics = [
        str(item) for item in (
            capability_model.get('workflow_topics', []) if isinstance(capability_model, dict) else []
        ) if isinstance(item, str)
    ]
    lines = [
        f'Posso te ajudar com a rotina institucional do {school_name} em {segment_summary}.',
        'No lado publico, eu cubro: ' + '; '.join(public_topics or [
            'matricula, bolsas, visitas, horarios, calendario, biblioteca, uniforme, transporte e vida escolar'
        ]) + '.',
        'Se sua conta estiver vinculada, eu tambem consigo cuidar de: ' + '; '.join(protected_topics or [
            'notas, faltas, boletos e vida financeira'
        ]) + '.',
        'Quando o assunto pedir acao, eu posso seguir com: ' + '; '.join(workflow_topics or [
            'solicitacoes para secretaria, coordenacao, orientacao educacional, financeiro ou direcao'
        ]) + '.',
        'Se quiser, me diga o tema do jeito que for mais natural e eu sigo com voce.',
    ]
    return lines


def _concierge_topic_examples(profile: dict[str, Any], limit: int = 5) -> list[str]:
    examples: list[str] = []
    capability_model = profile.get('assistant_capabilities')
    capability_topics = (
        capability_model.get('public_topics', [])
        if isinstance(capability_model, dict)
        else []
    )
    for item in capability_topics:
        if not isinstance(item, str):
            continue
        label = item.strip().lower()
        if label and label not in examples:
            examples.append(label)
        if len(examples) >= limit:
            return examples

    for service in _public_service_catalog(profile):
        title = str(service.get('title', '')).strip().lower()
        if not title:
            continue
        if 'admis' in title:
            label = 'matricula e visita'
        elif 'finance' in title:
            label = 'financeiro e boletos'
        elif 'secretaria' in title:
            label = 'secretaria e documentos'
        elif 'coorden' in title:
            label = 'coordenacao'
        elif 'orienta' in title:
            label = 'orientacao educacional'
        elif 'dire' in title or 'ouvidoria' in title:
            label = 'direcao e ouvidoria'
        else:
            label = title
        if label not in examples:
            examples.append(label)
        if len(examples) >= limit:
            return examples

    return examples or ['matricula', 'horarios', 'financeiro', 'secretaria', 'visitas']


def _compose_concierge_topic_examples(profile: dict[str, Any], limit: int = 5) -> str:
    examples = _concierge_topic_examples(profile, limit=limit)
    if not examples:
        return 'matricula, horarios, financeiro, secretaria e visitas'
    if len(examples) == 1:
        return examples[0]
    if len(examples) == 2:
        return f'{examples[0]} e {examples[1]}'
    return ', '.join(examples[:-1]) + f' e {examples[-1]}'


def _service_catalog_index(profile: dict[str, Any]) -> dict[str, dict[str, Any]]:
    entries = _public_service_catalog(profile)
    result: dict[str, dict[str, Any]] = {}
    for item in entries:
        key = str(item.get('service_key', '')).strip()
        if key:
            result[key] = item
    return result


def _requested_public_attribute(message: str) -> str | None:
    attributes = _requested_public_attributes(message)
    return attributes[0] if attributes else None


def _requested_public_attributes(message: str) -> tuple[str, ...]:
    normalized = _normalize_text(message)
    ordered_matches: list[str] = []

    def add_if_present(value: str, terms: set[str]) -> None:
        if value in ordered_matches:
            return
        if any(_message_matches_term(normalized, term) for term in terms):
            ordered_matches.append(value)

    add_if_present('close_time', {'fecha', 'fechar', 'fechamento', 'encerra', 'encerramento'})
    add_if_present('open_time', {'abre', 'abertura'})
    add_if_present('whatsapp', {'whatsapp', 'whats', 'zap'})
    add_if_present('email', {'email', 'e-mail', 'mail'})
    add_if_present('phone', {'telefone', 'fone', 'ligacao', 'ligação'})
    add_if_present('age', {'idade', 'quantos anos'})
    add_if_present('name', {'nome', 'quem e', 'quem é'})
    add_if_present('contact', {'contato', 'canal', 'como falo', 'como falar', 'falar com'})
    return tuple(ordered_matches)


def _is_public_teacher_identity_query(message: str) -> bool:
    normalized = _normalize_text(message)
    if not any(
        _message_matches_term(normalized, term)
        for term in {'prof', 'professor', 'professora', 'docente'}
    ):
        return False
    return _requested_public_attribute(message) in {'name', 'whatsapp', 'email', 'phone', 'contact'}


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
        subject = match.group(1).strip(' ?.')
        if subject:
            return subject
    return None


def _recent_service_match(
    profile: dict[str, Any],
    conversation_context: dict[str, Any] | None,
) -> dict[str, Any] | None:
    for sender_type, content in reversed(_recent_message_lines(conversation_context)):
        if sender_type not in {'user', 'assistant'}:
            continue
        matches = _service_matches_from_message(profile, content)
        if len(matches) == 1:
            return matches[0]
    return None


def _is_generic_service_contact_follow_up(message: str) -> bool:
    normalized = _normalize_text(message)
    return any(
        _message_matches_term(normalized, term)
        for term in {
            'com qual contato eu devo falar',
            'qual contato eu devo usar',
            'qual contato devo usar',
            'qual contato',
            'por qual canal',
            'como falo com',
            'como falar com',
            'quem devo procurar',
            'como entro em contato',
        }
    )


def _service_matches_from_message(profile: dict[str, Any], message: str) -> list[dict[str, Any]]:
    normalized = _normalize_text(message)
    catalog = _service_catalog_index(profile)
    service_keys: list[str] = []
    if any(_message_matches_term(normalized, term) for term in {'matricula', 'bolsa', 'desconto', 'admissao', 'admissoes', 'visita', 'tour'}):
        service_keys.extend(['atendimento_admissoes', 'visita_institucional'])
    if any(_message_matches_term(normalized, term) for term in {'secretaria', 'secretaria escolar'}):
        service_keys.append('secretaria_escolar')
    if any(_message_matches_term(normalized, term) for term in {'documento', 'documentos', 'historico', 'declaração', 'declaracao', 'transferencia', 'uniforme'}):
        service_keys.append('secretaria_escolar')
    if any(_message_matches_term(normalized, term) for term in {'rotina', 'aprendizagem', 'adaptacao', 'adaptação', 'professor', 'faltas', 'nota', 'notas', 'disciplina'}):
        service_keys.append('reuniao_coordenacao')
    if any(_message_matches_term(normalized, term) for term in {'emocional', 'convivencia', 'convivência', 'bullying', 'orientacao', 'orientação', 'socioemocional'}):
        service_keys.append('orientacao_educacional')
    if any(
        _message_matches_term(normalized, term)
        for term in {'mensalidade', 'boleto', 'boletos', 'financeiro', 'fatura', 'faturas', 'pagamento', 'contrato'}
    ):
        service_keys.append('financeiro_escolar')
    if any(_message_matches_term(normalized, term) for term in {'direcao', 'direção', 'diretora', 'ouvidoria', 'elogio', 'reclamacao', 'reclamação', 'sugestao', 'sugestão'}):
        service_keys.append('solicitacao_direcao')
    if any(_message_matches_term(normalized, term) for term in {'portal', 'senha', 'acesso', 'telegram', 'bot', 'sistema'}):
        service_keys.append('suporte_digital')
    if any(
        _message_matches_term(normalized, term)
        for term in {'trabalhar', 'vaga', 'curriculo', 'currículo', 'dar aula', 'professor', 'professora', 'processo seletivo'}
    ):
        service_keys.append('carreiras_docentes')
    unique_keys: list[str] = []
    for key in service_keys:
        if key in catalog and key not in unique_keys:
            unique_keys.append(key)
    return [catalog[key] for key in unique_keys]


def _humanize_service_eta(eta: str) -> str:
    cleaned = eta.strip()
    if not cleaned:
        return 'prazo nao informado'
    normalized = _normalize_text(cleaned)
    if normalized.startswith('retorno em '):
        return cleaned
    if normalized.startswith('protocolo imediato'):
        return cleaned
    return f'retorno em {cleaned}'


def _compose_assistant_identity_answer(
    profile: dict[str, Any],
    *,
    conversation_context: dict[str, Any] | None = None,
) -> str:
    school_name = str(profile.get('school_name', 'Colegio Horizonte'))
    base = (
        f'Voce esta falando com o EduAssist, o assistente institucional do {school_name}. '
        'Eu consigo te orientar por aqui, consultar informacoes da escola e abrir solicitacoes com protocolo. '
        'Se precisar, eu tambem te encaminho para secretaria, admissions, coordenacao, orientacao educacional, financeiro ou direcao.'
    )
    return base


def _is_public_document_submission_query(message: str) -> bool:
    normalized = _normalize_text(message)
    if any(_message_matches_term(normalized, term) for term in PUBLIC_DOCUMENT_SUBMISSION_TERMS):
        return True
    document_terms = {'documento', 'documentos', 'matricula', 'matrícula', 'cadastro'}
    digital_terms = {'online', 'digital', 'portal', 'email', 'e-mail', 'enviar', 'envio', 'mandar', 'mando'}
    special_channel_terms = {'fax', 'telegrama', 'caixa postal'}
    if any(_message_matches_term(normalized, term) for term in document_terms) and any(
        _message_matches_term(normalized, term) for term in special_channel_terms
    ):
        return True
    return any(_message_matches_term(normalized, term) for term in document_terms) and any(
        _message_matches_term(normalized, term) for term in digital_terms
    )


def _compose_public_document_submission_answer(
    profile: dict[str, Any],
    *,
    message: str | None = None,
) -> str:
    policy = profile.get('document_submission_policy')
    normalized_message = _normalize_text(message or '')
    if not isinstance(policy, dict):
        return (
            'Hoje a escola orienta tratar documentos e cadastro pela secretaria ou pelo portal institucional. '
            'Se quiser, eu posso te dizer o canal mais direto da secretaria.'
        )

    accepts_digital_submission = bool(policy.get('accepts_digital_submission'))
    accepted_channels = [
        str(item).strip()
        for item in policy.get('accepted_channels', [])
        if isinstance(item, str) and str(item).strip()
    ]
    warning = str(policy.get('warning', '')).strip()
    notes = str(policy.get('notes', '')).strip()
    secretaria_email_entry = _select_primary_contact_entry(
        profile,
        'email',
        'email da secretaria',
        preferred_labels=['Secretaria'],
    )
    secretaria_email = str(secretaria_email_entry.get('value', '')).strip() if secretaria_email_entry else ''

    accepted_channels_normalized = {_normalize_text(channel) for channel in accepted_channels}
    fallback_channels = []
    if any('portal' in channel for channel in accepted_channels_normalized):
        fallback_channels.append('portal institucional')
    if secretaria_email or any('email' in channel for channel in accepted_channels_normalized):
        fallback_channels.append('email da secretaria')
    if any('secretaria' in channel for channel in accepted_channels_normalized):
        fallback_channels.append('secretaria presencial')
    fallback_preview = ', '.join(fallback_channels) if fallback_channels else 'portal institucional, email da secretaria ou secretaria presencial'
    if any(
        _message_matches_term(normalized_message, term)
        for term in {'antes voce respondeu', 'você respondeu', 'voce respondeu', 'corrigindo'}
    ):
        return (
            f'Voce esta certo em cobrar essa correcao. Corrigindo: hoje a escola nao utiliza fax para envio de documentos. '
            f'Para isso, use {fallback_preview}.'
        )

    if _message_matches_term(normalized_message, 'fax'):
        return (
            f'Hoje a escola nao utiliza fax para envio de documentos. '
            f'Para isso, use {fallback_preview}.'
        )
    if _message_matches_term(normalized_message, 'telegrama'):
        return (
            f'Hoje a escola nao publica telegrama como canal valido para documentos. '
            f'Para isso, use {fallback_preview}.'
        )
    if _message_matches_term(normalized_message, 'caixa postal'):
        return (
            f'Hoje a escola nao trabalha com caixa postal para esse tipo de envio. '
            f'Para documentos, use {fallback_preview}.'
        )

    if not accepts_digital_submission:
        lines = [
            'Hoje a escola nao publica envio digital como canal principal para essa etapa.',
            'O caminho mais seguro continua sendo a secretaria ou o portal institucional.',
        ]
        if warning:
            lines.append(warning)
        return ' '.join(lines)

    lines = ['Sim. O envio inicial de documentos pode ser feito por canal digital.']
    if accepted_channels:
        canonical_channels = ['portal institucional', 'email da secretaria', 'secretaria presencial']
        lines.append('Hoje os canais mais diretos publicados para isso sao:')
        lines.extend(f'- {channel}' for channel in canonical_channels)
    elif secretaria_email:
        lines.append(f'O canal mais direto hoje e o email da secretaria: {secretaria_email}.')
    if secretaria_email and all('email da secretaria' not in channel.lower() for channel in accepted_channels):
        lines.append(f'Email da secretaria: {secretaria_email}.')
    if notes:
        lines.append(notes)
    if warning:
        lines.append(warning)
    return '\n'.join(lines)


def _try_public_channel_fast_answer(
    *,
    message: str,
    profile: dict[str, Any] | None,
) -> str | None:
    if not isinstance(profile, dict):
        return None
    normalized = _normalize_text(message)
    if _is_positive_requirement_query(message) or (
        any(_message_matches_term(normalized, term) for term in {'documento', 'documentos'})
        and any(_message_matches_term(normalized, term) for term in {'matricula', 'matrícula', 'exigido', 'exigidos'})
    ):
        return _compose_required_documents_answer(profile)
    if any(
        _message_matches_term(normalized, term)
        for term in {'proposta pedagogica', 'proposta pedagógica', 'projeto pedagogico', 'projeto pedagógico'}
    ) or (
        _message_matches_term(normalized, 'acolhimento')
        and any(_message_matches_term(normalized, term) for term in {'disciplina', 'disciplinas', 'convivencia', 'convivência'})
    ) or _is_public_curriculum_query(message):
        pedagogical_answer = _compose_public_pedagogical_answer(profile, message)
        if pedagogical_answer:
            return pedagogical_answer
    if any(
        _message_matches_term(normalized, term)
        for term in {'o que isso muda na pratica', 'o que isso muda na prática', 'na pratica no dia a dia', 'na prática no dia a dia'}
    ):
        practical_answer = _compose_public_comparative_practical_answer(profile)
        if practical_answer:
            return practical_answer
    if _is_comparative_query(message) or (
        _message_matches_term(normalized, 'publica')
        and any(_message_matches_term(normalized, term) for term in {'pagar', 'pagando', 'estudar'})
    ):
        comparative_answer = _compose_public_comparative_answer(profile)
        if comparative_answer:
            return comparative_answer
    if _is_public_document_submission_query(message) or (
        any(_message_matches_term(normalized, term) for term in {'documentacao', 'documentação', 'documentos'})
        and any(_message_matches_term(normalized, term) for term in {'mandar', 'enviar', 'envio', 'caminho'})
    ):
        return _compose_public_document_submission_answer(profile, message=message)
    if _message_matches_term(normalized, 'caixa postal'):
        primary_phone = _select_primary_contact_entry(
            profile,
            'telefone',
            'telefone principal',
        )
        if primary_phone:
            return (
                'Hoje a escola nao trabalha com caixa postal para esse tipo de envio. '
                f"Para documentos, use portal institucional, email da secretaria, secretaria presencial. "
                f"Se precisar falar com a escola, o telefone principal e {primary_phone.get('value')}."
            )
        return (
            'Hoje a escola nao trabalha com caixa postal para esse tipo de envio. '
            'Para documentos, use portal institucional, email da secretaria, secretaria presencial.'
        )
    if _requested_contact_channel(message) == 'telefone' and _message_matches_term(normalized, 'fax'):
        primary_phone = _select_primary_contact_entry(
            profile,
            'telefone',
            'telefone principal',
        )
        if primary_phone:
            return (
                'Hoje a escola nao utiliza fax. '
                f"Para entrar em contato por telefone, o numero da secretaria e {primary_phone.get('value')}."
            )
        return 'Hoje a escola nao utiliza fax.'
    return None


def _compose_public_pedagogical_answer(profile: dict[str, Any], message: str) -> str | None:
    normalized = _normalize_text(message)
    education_model = str(profile.get('education_model', '')).strip()
    curriculum_basis = str(profile.get('curriculum_basis', '')).strip()
    highlights = _public_highlights(profile)
    highlight_titles = [str(item.get('title', '')).strip() for item in highlights if str(item.get('title', '')).strip()]
    overview = str(profile.get('short_headline', '')).strip()
    if any(
        _message_matches_term(normalized, phrase)
        for phrase in {'proposta pedagogica', 'proposta pedagógica', 'projeto pedagogico', 'projeto pedagógico'}
    ):
        parts: list[str] = []
        if education_model:
            parts.append(f'A proposta pedagogica publicada hoje combina {education_model}.')
        if curriculum_basis:
            parts.append(f'No Ensino Medio, isso aparece junto de {curriculum_basis}.')
        if highlight_titles:
            parts.append(
                'Na pratica, isso aparece em frentes como {items}.'.format(
                    items=', '.join(highlight_titles[:3])
                )
            )
        parts.append(
            'Isso se traduz em acompanhamento mais proximo da aprendizagem e em uma proposta pedagogica explicita no dia a dia.'
        )
        return ' '.join(part for part in parts if part).strip() or None
    if _message_matches_term(normalized, 'acolhimento') and any(
        _message_matches_term(normalized, term)
        for term in {'disciplina', 'disciplinas', 'convivencia', 'convivência', 'aprendizagem', 'rotina'}
    ):
        parts = [
            'Pelo que a escola publica hoje, esse equilibrio aparece em uma rotina com acompanhamento proximo e acolhimento estruturado.'
        ]
        if overview:
            parts.append(overview)
        parts.append(
            'Na pratica, isso aparece em orientacao educacional, coordenacao, tutoria academica e projeto de vida, junto de uma jornada de acolhimento para familias e estudantes antes e depois da matricula.'
        )
        return ' '.join(part for part in parts if part).strip()
    if any(_message_matches_term(normalized, term) for term in PUBLIC_PEDAGOGICAL_TERMS):
        parts = []
        if education_model:
            parts.append(f'A proposta pedagogica publicada hoje combina {education_model}.')
        if highlight_titles:
            parts.append(
                'Os diferenciais pedagogicos mais claros aqui passam por {items}.'.format(
                    items=', '.join(highlight_titles[:3])
                )
            )
        return ' '.join(part for part in parts if part).strip() or None
    return None


def _compose_public_comparative_answer(profile: dict[str, Any]) -> str:
    highlights = _public_highlights(profile)
    highlight_titles = [str(item.get('title', '')).strip() for item in highlights if str(item.get('title', '')).strip()]
    education_model = str(profile.get('education_model', '')).strip()
    headline = str(profile.get('short_headline', '')).strip()
    labels_preview = ', '.join(highlight_titles[:3]) if highlight_titles else 'os diferenciais publicados da escola'
    parts = [
        'Estudar em uma escola publica pode ser uma boa escolha para muitas familias, e eu nao vou te vender uma comparacao vazia.',
        f'No que esta publicado aqui, os diferenciais desta escola passam por {labels_preview}.',
    ]
    if education_model:
        parts.append(f'A proposta pedagogica publicada hoje combina {education_model}.')
    parts.append(
        'Na pratica, isso aparece em acompanhamento mais proximo da aprendizagem, projeto de vida e combinados pedagogicos mais claros.'
    )
    if headline:
        parts.append(headline)
    parts.append(
        'Se quiser, eu posso te mostrar isso de forma mais pratica na rotina, na proposta pedagogica ou no contraturno.'
    )
    return ' '.join(part for part in parts if part).strip()


def _compose_public_comparative_practical_answer(profile: dict[str, Any]) -> str:
    education_model = str(profile.get('education_model', '')).strip()
    highlights = _public_highlights(profile)
    highlight_titles = [str(item.get('title', '')).strip() for item in highlights if str(item.get('title', '')).strip()]
    items = ', '.join(highlight_titles[:3]) if highlight_titles else 'tutoria academica, projeto de vida e acompanhamento proximo'
    parts = [
        'Na pratica, isso muda em uma rotina com aprendizagem por projetos, acompanhamento mais proximo e referencias claras de tutoria academica.',
        f'Os pontos que aparecem hoje de forma mais concreta sao {items}.',
        'Isso aparece no dia a dia em projeto de vida, acompanhamento mais proximo e referencias mais visiveis para familias e estudantes.',
    ]
    if education_model:
        parts.append(f'Isso conversa com uma proposta pedagogica que combina {education_model}.')
    return ' '.join(part for part in parts if part).strip()


def _compose_concierge_greeting(
    profile: dict[str, Any],
    message: str,
    conversation_context: dict[str, Any] | None,
) -> str:
    school_name = str(profile.get('school_name', 'Colegio Horizonte'))
    opening = 'Oi.'
    normalized = _normalize_text(message)
    if 'bom dia' in normalized:
        opening = 'Bom dia.'
    elif 'boa tarde' in normalized:
        opening = 'Boa tarde.'
    elif 'boa noite' in normalized:
        opening = 'Boa noite.'

    active_follow_up = _recent_focus_follow_up_line(conversation_context)
    if active_follow_up:
        if _assistant_already_introduced(conversation_context):
            return f'{opening} {active_follow_up}'
        return (
            f'{opening} Voce esta falando com o EduAssist do {school_name}. '
            f'{active_follow_up}'
        )

    if _assistant_already_introduced(conversation_context):
        return (
            f'{opening} Sou o EduAssist. Pode seguir do jeito que ficar mais facil. '
            'Se quiser, eu continuo por aqui com o mesmo assunto ou com um tema novo.'
        )

    examples = _compose_concierge_topic_examples(profile, limit=4)
    return (
        f'{opening} Voce esta falando com o EduAssist do {school_name}. '
        f'Posso te ajudar com {examples}. '
        'Se sua conta estiver vinculada, eu tambem consigo consultar notas, faltas e financeiro.'
    )


def _is_acknowledgement_query(message: str) -> bool:
    normalized = _normalize_text(message).strip()
    return any(_message_matches_term(normalized, term) for term in ACKNOWLEDGEMENT_TERMS)


def _compose_concierge_acknowledgement(
    *,
    conversation_context: dict[str, Any] | None,
) -> str:
    recent_assistant = _extract_recent_assistant_message(
        conversation_context.get('recent_messages', []) if isinstance(conversation_context, dict) else []
    )
    recent_normalized = _normalize_text(recent_assistant or '')
    if 'protocolo' in recent_normalized or 'ticket operacional' in recent_normalized:
        return 'Perfeito. Se quiser, eu acompanho o andamento desse atendimento por aqui.'
    if 'autenticacao' in recent_normalized or 'vinculo' in recent_normalized or 'link_' in recent_normalized:
        return 'Combinado. Quando quiser, eu continuo por aqui assim que sua conta estiver vinculada.'
    if 'financeiro' in recent_normalized:
        return 'Combinado. Se quiser, eu sigo com o proximo passo do financeiro ou te direciono para o setor certo.'
    if 'matricula' in recent_normalized or 'visita' in recent_normalized:
        return 'Perfeito. Se quiser, eu continuo daqui e te ajudo com o proximo passo.'
    return 'Por nada. Se quiser, pode seguir com a proxima duvida que eu continuo com voce por aqui.'


def _compose_capability_answer(
    profile: dict[str, Any],
    *,
    conversation_context: dict[str, Any] | None = None,
) -> str:
    public_examples = _compose_concierge_topic_examples(profile, limit=3)
    introduced = _assistant_already_introduced(conversation_context)
    if introduced:
        return (
            f'Por aqui eu consigo te ajudar com {public_examples}. '
            'Tambem consigo seguir com secretaria e documentos quando isso entrar no caminho. '
            'Se sua conta estiver vinculada, eu tambem consulto notas, faltas e financeiro escolar. '
            'Se precisar de uma acao, eu posso abrir visita, protocolo ou te encaminhar para o setor certo.'
        )
    return (
        f'Eu consigo te ajudar com {public_examples}. '
        'Tambem consigo seguir com secretaria e documentos quando isso entrar no caminho. '
        'Se sua conta estiver vinculada, eu tambem posso consultar notas, faltas e o financeiro escolar. '
        'Se fizer sentido, eu ainda abro visita, protocolo ou te direciono para o setor certo.'
    )


def _routing_follow_up_context_message(
    message: str,
    conversation_context: dict[str, Any] | None,
) -> str:
    if not isinstance(conversation_context, dict):
        return message
    recent_messages = conversation_context.get('recent_messages', [])
    if not isinstance(recent_messages, list):
        return message
    last_user_message = _extract_recent_user_message(recent_messages)
    last_assistant_message = _extract_recent_assistant_message(recent_messages)
    if not last_user_message:
        return message
    if _normalize_text(last_user_message) == _normalize_text(message):
        return message
    if (
        _is_greeting_only(last_user_message)
        or _is_service_routing_query(last_user_message)
        or _is_capability_query(last_user_message)
        or _is_assistant_identity_query(last_user_message)
    ):
        return message
    normalized_last_user = _normalize_text(last_user_message)
    if not any(_message_matches_term(normalized_last_user, term) for term in SERVICE_FOLLOW_UP_CONTEXT_TERMS):
        return message
    normalized_last_assistant = _normalize_text(last_assistant_message or '')
    if normalized_last_assistant and not any(
        marker in normalized_last_assistant
        for marker in (
            'autenticacao',
            'vinculo',
            'protocolo',
            'ticket operacional',
            'fila',
            'prazo',
            'setor',
            'canal recomendado',
        )
    ):
        return message
    return f'{message} sobre {last_user_message}'


def _compose_service_routing_menu(profile: dict[str, Any]) -> str:
    examples = _concierge_topic_examples(profile, limit=6)
    if not examples:
        return (
            'Hoje eu consigo te encaminhar para matricula, secretaria, coordenacao, orientacao, financeiro ou direcao.'
        )
    if len(examples) <= 3:
        return 'Hoje eu consigo te encaminhar para ' + ', '.join(examples) + '.'
    return (
        'Hoje eu consigo te encaminhar por aqui para '
        + ', '.join(examples[:-1])
        + f' e {examples[-1]}.'
    )


def _compose_service_routing_answer(
    profile: dict[str, Any],
    message: str,
    *,
    conversation_context: dict[str, Any] | None = None,
) -> str:
    message_for_matching = _routing_follow_up_context_message(message, conversation_context)
    matches = _service_matches_from_message(profile, message_for_matching)
    recent_match = None
    if not matches and _is_generic_service_contact_follow_up(message):
        recent_match = _recent_service_match(profile, conversation_context)
    if recent_match is not None:
        matches = [recent_match]
    if not matches:
        if _is_assistant_identity_query(message):
            return _compose_assistant_identity_answer(
                profile,
                conversation_context=conversation_context,
            )
        return (
            'Voce fala comigo, o EduAssist. Eu consigo te orientar e te encaminhar para secretaria, admissions, '
            f'coordenacao, orientacao educacional, financeiro ou direcao. {_compose_service_routing_menu(profile)} '
            'Se quiser, me diga o assunto em uma frase curta e eu te indico o melhor caminho sem voce precisar adivinhar o setor.'
        )
    if len(matches) == 1:
        item = matches[0]
        eta = _humanize_service_eta(str(item.get('typical_eta', 'prazo nao informado')))
        if _is_generic_service_contact_follow_up(message):
            response = (
                f'Voce pode falar com {item.get("title", "o setor institucional")} '
                f'por {item.get("request_channel", "canal institucional")}.'
            )
            if eta and eta != 'prazo nao informado':
                response += f' O prazo tipico e {eta}.'
            notes = str(item.get('notes', '')).strip()
            if notes:
                response += f' {notes}'
            response += ' Se quiser, eu sigo por aqui com a solicitacao certa.'
            return response
        return (
            f'Para tratar esse assunto, o caminho mais direto e {item.get("title", "o setor institucional")}. '
            f'Voce pode acionar por {item.get("request_channel", "canal institucional")}, e o prazo tipico e {eta}. '
            f'{str(item.get("notes", "")).strip()} '
            'Se preferir, eu mesmo ja posso seguir por aqui com a solicitacao certa.'
        )
    lines = ['Para esse tema, estes caminhos costumam funcionar melhor:']
    for item in matches[:3]:
        lines.append(
            '- {title}: {request_channel}. Prazo tipico: {typical_eta}.'.format(
                title=item.get('title', 'Setor institucional'),
                request_channel=item.get('request_channel', 'canal institucional'),
                typical_eta=item.get('typical_eta', 'nao informado'),
            )
        )
    lines.append('Se quiser, eu tambem posso seguir por aqui e abrir a solicitacao certa.')
    return '\n'.join(lines)


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


def _is_leadership_specific_query(message: str) -> bool:
    normalized = _normalize_text(message)
    if not any(_message_matches_term(normalized, term) for term in PUBLIC_LEADERSHIP_TERMS):
        return False
    return _requested_public_attribute(message) is not None


def _compose_public_teacher_directory_answer(
    profile: dict[str, Any],
    message: str,
) -> str:
    school_name = str(profile.get('school_name', 'Colegio Horizonte'))
    subject = _extract_teacher_subject(message)
    if subject:
        return (
            f'O {school_name} nao divulga nomes nem contatos diretos de professores por disciplina, como {subject}. '
            'Se quiser, eu posso te indicar a coordenacao pedagogica ou o setor certo para seguir com isso.'
        )
    return (
        f'O {school_name} nao divulga nomes nem contatos diretos de professores individualmente. '
        'Se quiser, eu posso te indicar a coordenacao pedagogica ou o setor certo.'
    )


def _compose_public_leadership_answer(
    profile: dict[str, Any],
    message: str,
    *,
    requested_attribute_override: str | None = None,
) -> str:
    school_name = str(profile.get('school_name', 'Colegio Horizonte'))
    member = _select_leadership_member(profile, message)
    if member is None:
        return f'Hoje o perfil publico do {school_name} nao traz a lideranca institucional detalhada.'

    requested_attribute = requested_attribute_override or _requested_public_attribute(message)
    title = str(member.get('title', 'Lideranca institucional')).strip()
    name = str(member.get('name', school_name)).strip()
    focus = str(member.get('focus', '')).strip()
    contact_channel = str(member.get('contact_channel', '')).strip()
    notes = str(member.get('notes', '')).strip()
    role_reference = f'a {title.lower()}'
    if 'diretor' in _normalize_text(message) or 'diretora' in _normalize_text(message) or 'direcao' in _normalize_text(message):
        role_reference = 'a direcao geral'

    if requested_attribute == 'name':
        return f'{title}: {name}.'
    if requested_attribute == 'age':
        response = (
            f'{role_reference.capitalize()} da escola hoje e {name}, '
            'mas a escola nao publica a idade dela.'
        )
        if contact_channel:
            response += f' Se voce precisar falar com esse setor, o canal institucional e {contact_channel}.'
        return response
    if requested_attribute == 'whatsapp':
        if contact_channel and '@' not in contact_channel:
            return f'O canal publicado para {role_reference} e {contact_channel}.'
        response = f'A escola nao publica um WhatsApp direto para {role_reference}.'
        if contact_channel:
            response += f' O contato institucional divulgado para esse atendimento e {contact_channel}.'
        return response
    if requested_attribute == 'phone':
        response = f'A escola nao publica um telefone direto para {role_reference}.'
        if contact_channel:
            response += f' O contato institucional divulgado para esse atendimento e {contact_channel}.'
        return response
    if requested_attribute in {'email', 'contact'}:
        if contact_channel:
            response = f'Voce pode falar com {role_reference} pelo canal institucional {contact_channel}.'
            if notes:
                response += f' {notes}'
            return response
        return f'O perfil publico da escola nao traz um canal direto publicado para {role_reference}.'

    lines = [f'{title}: {name}.']
    if focus:
        lines.append(focus)
    if contact_channel:
        lines.append(f'Canal institucional: {contact_channel}.')
    if notes:
        lines.append(notes)
    return ' '.join(line for line in lines if line)


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


def _compose_public_profile_answer_legacy(
    profile: dict[str, Any],
    message: str,
    *,
    original_message: str | None = None,
    conversation_context: dict[str, Any] | None = None,
    semantic_plan: PublicInstitutionPlan | None = None,
) -> str:
    source_message = original_message or message
    normalized = _normalize_text(source_message)
    analysis_normalized = _normalize_text(message)
    school_name = str(profile.get('school_name', 'Colegio Horizonte'))
    school_reference = 'a escola' if _assistant_already_introduced(conversation_context) else school_name
    school_reference_capitalized = 'A escola' if school_reference == 'a escola' else school_reference
    city = str(profile.get('city', ''))
    state = str(profile.get('state', ''))
    district = str(profile.get('district', ''))
    address_line = str(profile.get('address_line', ''))
    postal_code_raw = profile.get('postal_code')
    website_url_raw = profile.get('website_url')
    fax_number_raw = profile.get('fax_number')
    curriculum_basis_raw = profile.get('curriculum_basis')
    postal_code = postal_code_raw.strip() if isinstance(postal_code_raw, str) else ''
    website_url = website_url_raw.strip() if isinstance(website_url_raw, str) else ''
    fax_number = fax_number_raw.strip() if isinstance(fax_number_raw, str) else ''
    curriculum_basis = curriculum_basis_raw.strip() if isinstance(curriculum_basis_raw, str) else ''
    curriculum_components = [
        str(item).strip()
        for item in profile.get('curriculum_components', [])
        if isinstance(item, str) and str(item).strip()
    ]
    confessional_status = str(profile.get('confessional_status', '')).strip().lower()
    segment = _select_public_segment(message)
    if segment is None:
        segment = _select_public_segment(source_message)
    schedule_context_normalized = normalized
    if _is_follow_up_query(source_message) and any(
        _message_matches_term(analysis_normalized, term) for term in PUBLIC_SCHEDULE_TERMS
    ):
        schedule_context_normalized = analysis_normalized
    shift_offers = profile.get('shift_offers') if isinstance(profile.get('shift_offers'), list) else []
    tuition_reference = profile.get('tuition_reference') if isinstance(profile.get('tuition_reference'), list) else []
    feature_map = _feature_inventory_map(profile)
    semantic_act = semantic_plan.conversation_act if semantic_plan else None
    contact_reference_message = _public_contact_reference_message(
        profile=profile,
        source_message=source_message,
        analysis_message=message,
        conversation_context=conversation_context,
    )
    preferred_contact_labels = _preferred_contact_labels_from_context(
        profile,
        source_message,
        conversation_context,
    )
    requested_channel = (
        semantic_plan.requested_channel
        if semantic_plan and semantic_plan.requested_channel
        else _requested_contact_channel(contact_reference_message)
    )
    requested_attribute_override = (
        semantic_plan.requested_attribute
        if semantic_plan and semantic_plan.requested_attribute
        else None
    )

    if _is_acknowledgement_query(source_message):
        return _compose_concierge_acknowledgement(conversation_context=conversation_context)

    if semantic_act == 'greeting' or _is_greeting_only(source_message):
        return _compose_concierge_greeting(profile, source_message, conversation_context)

    if semantic_act == 'utility_date' or _is_public_date_query(source_message):
        return f'Hoje e {_format_brazilian_date(date.today())}.'

    if _is_auth_guidance_query(source_message):
        return (
            'Para consultas protegidas, como notas, faltas e financeiro, voce precisa vincular sua conta do Telegram ao portal da escola. '
            'No portal autenticado, gere o codigo de vinculacao e depois envie aqui o comando `/start link_<codigo>`. '
            'Depois disso, eu passo a consultar seus dados autorizados por este canal.'
        )

    if semantic_act == 'assistant_identity' or _is_assistant_identity_query(source_message):
        return _compose_assistant_identity_answer(
            profile,
            conversation_context=conversation_context,
        )

    if semantic_act == 'service_routing' or _is_service_routing_query(source_message):
        return _compose_service_routing_answer(
            profile,
            source_message,
            conversation_context=conversation_context,
        )

    if semantic_act == 'capabilities' or _is_capability_query(source_message):
        return _compose_capability_answer(
            profile,
            conversation_context=conversation_context,
        )

    if _is_public_document_submission_query(source_message):
        return _compose_public_document_submission_answer(profile, message=source_message)

    if _is_public_teacher_identity_query(source_message):
        return _compose_public_teacher_directory_answer(profile, source_message)

    if semantic_act == 'leadership' or _is_leadership_specific_query(source_message):
        return _compose_public_leadership_answer(
            profile,
            source_message,
            requested_attribute_override=requested_attribute_override,
        )

    if semantic_act == 'web_presence' or _is_public_web_query(source_message):
        if website_url:
            return f'O site oficial de {school_reference} hoje e {website_url}.'
        return (
            f'Hoje eu nao tenho um site oficial publicado no perfil canonico de {school_reference}. '
            'Se quiser, eu posso te passar o telefone ou o email da secretaria.'
        )

    if semantic_act == 'contacts' or any(_message_matches_term(normalized, term) for term in PUBLIC_CONTACT_TERMS):
        phone_lines = _contact_value(profile, 'telefone')
        whatsapp_lines = _contact_value(profile, 'whatsapp')
        email_lines = _contact_value(profile, 'email')
        fax_only_query = _message_matches_term(normalized, 'fax') and not any(
            _message_matches_term(normalized, term)
            for term in {'telefone', 'fone', 'ligar', 'ligo', 'whatsapp', 'email'}
        )
        if fax_only_query:
            if fax_number:
                return f'O fax institucional publicado de {school_reference} hoje e {fax_number}.'
            primary_phone = _select_primary_contact_entry(
                profile,
                'telefone',
                contact_reference_message,
                preferred_labels=preferred_contact_labels,
            )
            if primary_phone:
                return (
                    f'Hoje {school_reference} nao publica numero de fax. '
                    f"Se quiser ligar, o telefone principal e {primary_phone.get('value')}."
                )
            return f'Hoje {school_reference} nao publica numero de fax.'
        if requested_channel == 'telefone':
            primary_phone = _select_primary_contact_entry(
                profile,
                'telefone',
                contact_reference_message,
                preferred_labels=preferred_contact_labels,
            )
            if primary_phone and (_contact_is_general_school_query(contact_reference_message) or not _wants_contact_list(contact_reference_message)):
                label = primary_phone.get('label')
                value = primary_phone.get('value')
                if label:
                    response = f'O telefone principal {_school_object_reference(school_reference)} hoje e {value}, {_format_contact_origin(label, "telefone")}.'
                else:
                    response = f'O telefone principal {_school_object_reference(school_reference)} hoje e {value}.'
                if _message_matches_term(normalized, 'fax'):
                    if fax_number:
                        response += f' O fax publicado e {fax_number}.'
                    else:
                        response += ' Hoje a escola nao publica numero de fax.'
                return response
            if len(phone_lines) == 1:
                response = f'O telefone oficial de {school_reference} e {phone_lines[0]}.'
                if _message_matches_term(normalized, 'fax'):
                    response += ' Hoje a escola nao publica numero de fax.'
                return response
            lines = [f'Os telefones oficiais de {school_reference} hoje sao:']
            lines.extend(f'- {item}' for item in phone_lines)
            if _message_matches_term(normalized, 'fax'):
                lines.append('- Fax: nao publicado')
            return _render_structured_answer_lines(lines)
        if requested_channel == 'whatsapp':
            primary_whatsapp = _select_primary_contact_entry(
                profile,
                'whatsapp',
                contact_reference_message,
                preferred_labels=preferred_contact_labels,
            )
            if primary_whatsapp and (_contact_is_general_school_query(contact_reference_message) or not _wants_contact_list(contact_reference_message)):
                label = primary_whatsapp.get('label')
                value = primary_whatsapp.get('value')
                if label:
                    return f'O WhatsApp mais direto {_school_object_reference(school_reference)} hoje e {value}, {_format_contact_origin(label, "whatsapp")}.'
                return f'O WhatsApp oficial {_school_object_reference(school_reference)} hoje e {value}.'
            if len(whatsapp_lines) == 1:
                return f'O WhatsApp oficial de {school_reference} hoje e {whatsapp_lines[0]}.'
            lines = [f'Os canais de WhatsApp publicados por {school_reference} hoje sao:']
            lines.extend(f'- {item}' for item in whatsapp_lines)
            return _render_structured_answer_lines(lines)
        if requested_channel == 'email':
            primary_email = _select_primary_contact_entry(
                profile,
                'email',
                contact_reference_message,
                preferred_labels=preferred_contact_labels,
            )
            if primary_email and (_contact_is_general_school_query(contact_reference_message) or not _wants_contact_list(contact_reference_message)):
                label = primary_email.get('label')
                value = primary_email.get('value')
                if label:
                    return f'O email mais direto {_school_object_reference(school_reference)} hoje e {value}, {_format_contact_origin(label, "email")}.'
                return f'O email institucional publicado de {school_reference} e {value}.'
            if len(email_lines) == 1:
                return f'O email institucional publicado de {school_reference} e {email_lines[0]}.'
            lines = [f'Os emails institucionais publicados de {school_reference} hoje sao:']
            lines.extend(f'- {item}' for item in email_lines)
            return _render_structured_answer_lines(lines)
        lines = [f'Voce pode falar com {school_reference} por estes canais oficiais:']
        lines.extend(f'- {item}' for item in [*phone_lines, *whatsapp_lines, *email_lines])
        if _message_matches_term(normalized, 'fax'):
            lines.append('- Fax: nao publicado')
        return '\n'.join(lines)

    if semantic_act == 'operating_hours' or _is_public_operating_hours_query(source_message):
        return (
            f'O atendimento presencial {_school_object_reference(school_reference)} abre as 7h00 e segue ate as 17h30, de segunda a sexta-feira. '
            'Se voce estiver falando da biblioteca, ela funciona das 7h30 as 18h00.'
        )

    if semantic_act == 'location' or any(_message_matches_term(normalized, term) for term in PUBLIC_LOCATION_TERMS):
        location = ', '.join(part for part in [address_line, district, city, state] if part)
        if postal_code:
            location = f'{location}, CEP {postal_code}'
        return f'{school_reference_capitalized} fica em {location}.'

    if semantic_act == 'confessional' or any(_message_matches_term(normalized, term) for term in PUBLIC_CONFESSIONAL_TERMS):
        if confessional_status == 'laica':
            return (
                f'{school_reference_capitalized} e uma escola laica. '
                'A proposta institucional e plural e nao confessional.'
            )
        return f'Hoje o perfil publico classifica {school_reference} como {confessional_status}.'

    if any(_message_matches_term(normalized, term) for term in PUBLIC_LEADERSHIP_TERMS):
        return _compose_public_leadership_answer(
            profile,
            source_message,
            requested_attribute_override=requested_attribute_override,
        )

    if semantic_act == 'curriculum' or _is_public_curriculum_query(source_message):
        if curriculum_basis and curriculum_components:
            components = ', '.join(curriculum_components[:8])
            extra = ''
            if len(curriculum_components) > 8:
                extra = ', alem de projeto de vida, monitorias e trilhas eletivas'
            return (
                f'No Ensino Medio, {school_reference} segue a BNCC e um curriculo proprio de aprofundamento academico. '
                f'Os componentes que aparecem hoje na base publica incluem {components}{extra}.'
            )
        if curriculum_basis:
            return f'Hoje a base curricular publica de {school_reference} e esta: {curriculum_basis}'
        return (
            f'Hoje eu nao encontrei um detalhamento curricular estruturado de {school_reference}. '
            'Se quiser, eu posso resumir a proposta pedagogica publicada.'
        )

    if semantic_act == 'kpi' or any(_message_matches_term(normalized, term) for term in PUBLIC_KPI_TERMS):
        entries = _select_public_kpis(profile, message)
        if not entries:
            return f'Hoje o perfil publico de {school_reference} nao traz indicadores institucionais publicados.'
        if len(entries) == 1:
            item = entries[0]
            notes = str(item.get('notes', '')).strip()
            return (
                f"Hoje, {item.get('label', 'o indicador institucional')} esta em {item.get('value', '--')}{item.get('unit', '')} "
                f"({item.get('reference_period', 'periodo nao informado')}). {notes}".strip()
            )
        lines = [f'Os indicadores publicos mais recentes de {school_reference} sao:']
        for item in entries:
            lines.append(
                f"- {item.get('label', 'Indicador')}: {item.get('value', '--')}{item.get('unit', '')} "
                f"({item.get('reference_period', 'periodo nao informado')})"
            )
        return '\n'.join(lines)

    if semantic_act == 'highlight' or any(_message_matches_term(normalized, term) for term in PUBLIC_HIGHLIGHT_TERMS):
        item = _select_public_highlight(profile, message)
        if item is None:
            return f'Hoje o perfil publico de {school_reference} nao traz diferenciais institucionais consolidados.'
        evidence_line = str(item.get('evidence_line', '')).strip()
        intro = 'Um dos diferenciais documentados desta escola'
        if any(
            _message_matches_term(normalized, term)
            for term in {'curiosidade', 'curiosidades', 'unica', 'única'}
        ):
            intro = 'Uma curiosidade documentada desta escola'
        title = str(item.get('title', 'Diferencial institucional')).strip()
        description = str(item.get('description', '')).strip()
        lines = [f'{intro} e {title}. {description}'.strip()]
        if evidence_line:
            lines.append(f'Isso aparece de forma bem clara na proposta institucional: {evidence_line}')
        return ' '.join(line for line in lines if line)

    if semantic_act == 'visit' or any(_message_matches_term(normalized, term) for term in PUBLIC_VISIT_TERMS):
        offers = _public_visit_offers(profile)
        services = _public_service_catalog(profile)
        if not offers:
            return f'Hoje o perfil publico de {school_reference} nao traz janelas de visita institucional.'
        lines = [f'Hoje {_school_subject_reference(school_reference)} publica estas janelas de visita:']
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

    if semantic_act == 'pricing' or any(_message_matches_term(normalized, term) for term in PUBLIC_PRICING_TERMS):
        relevant_rows = [
            row for row in tuition_reference
            if isinstance(row, dict) and (segment is None or str(row.get('segment')) == segment)
        ]
        if not relevant_rows:
            relevant_rows = [row for row in tuition_reference if isinstance(row, dict)]
        if len(relevant_rows) == 1:
            row = relevant_rows[0]
            return (
                f"Para {row.get('segment', 'esse segmento')} no turno {row.get('shift_label', 'regular')}, "
                f"a mensalidade publica de referencia em 2026 e {row.get('monthly_amount', '0.00')} "
                f"e a taxa de matricula e {row.get('enrollment_fee', '0.00')}. "
                f"{str(row.get('notes', '')).strip()} "
                'Se quiser, eu tambem posso resumir bolsas, descontos comerciais e canais de matricula.'
            ).strip()
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

    feature_schedule_follow_up = _compose_public_feature_schedule_follow_up(
        profile=profile,
        original_message=source_message,
        analysis_message=message,
        conversation_context=conversation_context,
    )
    if feature_schedule_follow_up:
        return feature_schedule_follow_up

    feature_answer = _compose_public_feature_answer(
        profile=profile,
        original_message=source_message,
        analysis_message=message,
        conversation_context=conversation_context,
    )
    if semantic_act == 'features' and feature_answer:
        return feature_answer
    if feature_answer:
        return feature_answer

    if semantic_act == 'schedule' or any(_message_matches_term(schedule_context_normalized, term) for term in PUBLIC_SCHEDULE_TERMS):
        relevant_rows = [
            row for row in shift_offers
            if isinstance(row, dict) and (segment is None or str(row.get('segment')) == segment)
        ]
        if not relevant_rows:
            relevant_rows = [row for row in shift_offers if isinstance(row, dict)]
        if len(relevant_rows) == 1:
            row = relevant_rows[0]
            grade_reference = _extract_grade_reference(source_message)
            if grade_reference:
                return (
                    f'O {grade_reference} fica em {row.get("segment", "esse segmento")}. '
                    f'As atividades do turno {row.get("shift_label", "regular").lower()} vao de {row.get("starts_at", "--:--")} a {row.get("ends_at", "--:--")}. '
                    f'{str(row.get("notes", "")).strip()}'
                ).strip()
            return (
                f"Para {row.get('segment', 'esse segmento')}, as atividades no turno {row.get('shift_label', 'regular').lower()} "
                f"vao de {row.get('starts_at', '--:--')} a {row.get('ends_at', '--:--')}. "
                f"{str(row.get('notes', '')).strip()}"
            ).strip()
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
            return f'Hoje o perfil publico de {school_reference} nao traz os segmentos atendidos.'
        lines = [f'Hoje {school_reference} atende estes segmentos:']
        lines.extend(f'- {item}' for item in segments if isinstance(item, str))
        return '\n'.join(lines)

    if _is_public_school_name_query(message):
        return f'O nome oficial da escola e {school_name}.'

    headline = str(profile.get('short_headline', '')).strip()
    if headline:
        return f'{school_name}: {headline}'
    return f'O nome oficial da escola e {school_name}.'


def _build_public_profile_context(
    profile: dict[str, Any],
    message: str,
    *,
    actor: dict[str, Any] | None = None,
    original_message: str | None = None,
    conversation_context: dict[str, Any] | None = None,
    semantic_plan: PublicInstitutionPlan | None = None,
) -> PublicProfileContext:
    source_message = original_message or message
    normalized = _normalize_text(source_message)
    analysis_normalized = _normalize_text(message)
    slot_memory = _build_conversation_slot_memory(
        actor=None,
        profile=profile,
        conversation_context=conversation_context,
        request_message=source_message,
        public_plan=semantic_plan,
    )
    school_name = str(profile.get('school_name', 'Colegio Horizonte'))
    school_reference = 'a escola' if _assistant_already_introduced(conversation_context) else school_name
    school_reference_capitalized = 'A escola' if school_reference == 'a escola' else school_reference
    postal_code_raw = profile.get('postal_code')
    website_url_raw = profile.get('website_url')
    fax_number_raw = profile.get('fax_number')
    curriculum_basis_raw = profile.get('curriculum_basis')
    segment = _select_public_segment(message) or _select_public_segment(source_message)
    schedule_context_normalized = normalized
    if _is_follow_up_query(source_message) and any(
        _message_matches_term(analysis_normalized, term) for term in PUBLIC_SCHEDULE_TERMS
    ):
        schedule_context_normalized = analysis_normalized
    contact_reference_message = _public_contact_reference_message(
        profile=profile,
        source_message=source_message,
        analysis_message=message,
        conversation_context=conversation_context,
    )
    preferred_contact_labels = tuple(
        _preferred_contact_labels_from_context(
            profile,
            source_message,
            conversation_context,
        )
    )
    if _contact_is_general_school_query(contact_reference_message):
        preferred_contact_labels = ()
    return PublicProfileContext(
        profile=profile,
        actor=actor,
        message=message,
        source_message=source_message,
        normalized=normalized,
        analysis_normalized=analysis_normalized,
        school_name=school_name,
        school_reference=school_reference,
        school_reference_capitalized=school_reference_capitalized,
        city=str(profile.get('city', '')),
        state=str(profile.get('state', '')),
        district=str(profile.get('district', '')),
        address_line=str(profile.get('address_line', '')),
        postal_code=postal_code_raw.strip() if isinstance(postal_code_raw, str) else '',
        website_url=website_url_raw.strip() if isinstance(website_url_raw, str) else '',
        fax_number=fax_number_raw.strip() if isinstance(fax_number_raw, str) else '',
        curriculum_basis=curriculum_basis_raw.strip() if isinstance(curriculum_basis_raw, str) else '',
        curriculum_components=tuple(
            str(item).strip()
            for item in profile.get('curriculum_components', [])
            if isinstance(item, str) and str(item).strip()
        ),
        confessional_status=str(profile.get('confessional_status', '')).strip().lower(),
        segment=segment,
        schedule_context_normalized=schedule_context_normalized,
        shift_offers=tuple(
            row for row in profile.get('shift_offers', []) if isinstance(row, dict)
        ),
        tuition_reference=tuple(
            row for row in profile.get('tuition_reference', []) if isinstance(row, dict)
        ),
        semantic_act=semantic_plan.conversation_act if semantic_plan else None,
        contact_reference_message=contact_reference_message,
        preferred_contact_labels=preferred_contact_labels,
        requested_channel=(
            semantic_plan.requested_channel
            if semantic_plan and semantic_plan.requested_channel
            else _requested_contact_channel(contact_reference_message)
        ),
        requested_attribute_override=(
            semantic_plan.requested_attribute
            if semantic_plan and semantic_plan.requested_attribute
            else None
        ),
        slot_memory=slot_memory,
        conversation_context=conversation_context,
        semantic_plan=semantic_plan,
    )


def _resolve_public_profile_act(context: PublicProfileContext) -> str:
    if _is_acknowledgement_query(context.source_message):
        return 'acknowledgement'
    if context.semantic_act and context.semantic_act != 'canonical_fact':
        return context.semantic_act
    matched_rule = _match_public_act_rule(context.source_message)
    if matched_rule is not None:
        return matched_rule.name
    return 'canonical_fact'


def _handle_public_acknowledgement(context: PublicProfileContext) -> str:
    return _compose_concierge_acknowledgement(conversation_context=context.conversation_context)


def _handle_public_greeting(context: PublicProfileContext) -> str:
    return _compose_concierge_greeting(context.profile, context.source_message, context.conversation_context)


def _handle_public_utility_date(_: PublicProfileContext) -> str:
    return f'Hoje e {_format_brazilian_date(date.today())}.'


def _handle_public_auth_guidance(_: PublicProfileContext) -> str:
    return (
        'Para consultas protegidas, como notas, faltas e financeiro, voce precisa vincular sua conta do Telegram ao portal da escola. '
        'No portal autenticado, gere o codigo de vinculacao e depois envie aqui o comando `/start link_<codigo>`. '
        'Depois disso, eu passo a consultar seus dados autorizados por este canal.'
    )


def _handle_public_access_scope(context: PublicProfileContext) -> str:
    return _compose_public_access_scope_answer(
        context.actor,
        school_name=context.school_name,
    )


def _handle_public_assistant_identity(context: PublicProfileContext) -> str:
    return _compose_assistant_identity_answer(
        context.profile,
        conversation_context=context.conversation_context,
    )


def _handle_public_service_routing(context: PublicProfileContext) -> str:
    return _compose_service_routing_answer(
        context.profile,
        context.source_message,
        conversation_context=context.conversation_context,
    )


def _handle_public_capabilities(context: PublicProfileContext) -> str:
    return _compose_capability_answer(
        context.profile,
        conversation_context=context.conversation_context,
    )


def _handle_public_document_submission(context: PublicProfileContext) -> str:
    return _compose_public_document_submission_answer(context.profile, message=context.source_message)


def _handle_public_teacher_directory(context: PublicProfileContext) -> str:
    return _compose_public_teacher_directory_answer(context.profile, context.source_message)


def _handle_public_leadership(context: PublicProfileContext) -> str:
    return _compose_public_leadership_answer(
        context.profile,
        context.source_message,
        requested_attribute_override=context.requested_attribute_override,
    )


def _handle_public_web_presence(context: PublicProfileContext) -> str:
    if context.website_url:
        return f'O site oficial {_school_object_reference(context.school_reference)} hoje e {context.website_url}.'
    return (
        f'Hoje eu nao tenho um site oficial publicado no perfil canonico de {context.school_reference}. '
        'Se quiser, eu posso te passar o telefone ou o email da secretaria.'
    )


def _handle_public_social_presence(context: PublicProfileContext) -> str:
    instagram_entries = _contact_entries(context.profile, 'instagram')
    if instagram_entries:
        primary_entry = instagram_entries[0]
        value = str(primary_entry.get('value', '')).strip()
        label = str(primary_entry.get('label', '')).strip()
        if value:
            prefix = f'O {label.lower()} ' if label else 'O Instagram institucional '
            return (
                f'{prefix}{_school_object_reference(context.school_reference)} hoje e {value}. '
                'Se quiser, eu tambem posso te passar o site oficial ou os canais de atendimento.'
            )
    return (
        f'Hoje eu nao tenho um Instagram oficial publicado no perfil canonico de {context.school_reference}. '
        'Se quiser, eu posso te passar o site oficial ou os canais institucionais de contato.'
    )


def _handle_public_comparative(context: PublicProfileContext) -> str:
    return _compose_public_comparative_answer(context.profile)


def _handle_public_contacts(context: PublicProfileContext) -> str:
    phone_lines = _contact_value(context.profile, 'telefone')
    whatsapp_lines = _contact_value(context.profile, 'whatsapp')
    email_lines = _contact_value(context.profile, 'email')
    if _message_matches_term(context.normalized, 'caixa postal'):
        primary_phone = _select_primary_contact_entry(
            context.profile,
            'telefone',
            context.contact_reference_message,
            preferred_labels=context.preferred_contact_labels,
        )
        if primary_phone:
            return (
                f'Hoje {context.school_reference} nao trabalha com caixa postal como canal institucional. '
                f"Se precisar de contato, o telefone principal e {primary_phone.get('value')}."
            )
        return f'Hoje {context.school_reference} nao trabalha com caixa postal como canal institucional.'
    fax_only_query = _message_matches_term(context.normalized, 'fax') and not any(
        _message_matches_term(context.normalized, term)
        for term in {'telefone', 'fone', 'ligar', 'ligo', 'whatsapp', 'email'}
    )
    if fax_only_query:
        if context.fax_number:
            return f'O fax institucional publicado de {context.school_reference} hoje e {context.fax_number}.'
        primary_phone = _select_primary_contact_entry(
            context.profile,
            'telefone',
            context.contact_reference_message,
            preferred_labels=context.preferred_contact_labels,
        )
        if primary_phone:
            return (
                f'Hoje {context.school_reference} nao publica numero de fax. '
                f"Se quiser ligar, o telefone principal e {primary_phone.get('value')}."
            )
        return f'Hoje {context.school_reference} nao publica numero de fax.'
    if context.requested_channel == 'telefone':
        primary_phone = _select_primary_contact_entry(
            context.profile,
            'telefone',
            context.contact_reference_message,
            preferred_labels=context.preferred_contact_labels,
        )
        if primary_phone and (
            _contact_is_general_school_query(context.contact_reference_message)
            or not _wants_contact_list(context.contact_reference_message)
        ):
            label = primary_phone.get('label')
            value = primary_phone.get('value')
            if label:
                response = (
                    f'O telefone principal {_school_object_reference(context.school_reference)} hoje e {value}, '
                    f'{_format_contact_origin(label, "telefone")}.'
                )
            else:
                response = f'O telefone principal {_school_object_reference(context.school_reference)} hoje e {value}.'
            if _message_matches_term(context.normalized, 'fax'):
                response += (
                    f' O fax publicado e {context.fax_number}.'
                    if context.fax_number
                    else ' Hoje a escola nao publica numero de fax.'
                )
            return response
        if len(phone_lines) == 1:
            response = f'O telefone oficial de {context.school_reference} e {phone_lines[0]}.'
            if _message_matches_term(context.normalized, 'fax'):
                response += ' Hoje a escola nao publica numero de fax.'
            return response
        lines = [f'Os telefones oficiais de {context.school_reference} hoje sao:']
        lines.extend(f'- {item}' for item in phone_lines)
        if _message_matches_term(context.normalized, 'fax'):
            lines.append('- Fax: nao publicado')
        return '\n'.join(lines)
    if context.requested_channel == 'whatsapp':
        primary_whatsapp = _select_primary_contact_entry(
            context.profile,
            'whatsapp',
            context.contact_reference_message,
            preferred_labels=context.preferred_contact_labels,
        )
        if primary_whatsapp and (
            _contact_is_general_school_query(context.contact_reference_message)
            or not _wants_contact_list(context.contact_reference_message)
        ):
            label = primary_whatsapp.get('label')
            value = primary_whatsapp.get('value')
            if label:
                return (
                    f'O WhatsApp mais direto {_school_object_reference(context.school_reference)} hoje e {value}, '
                    f'{_format_contact_origin(label, "whatsapp")}.'
                )
            return f'O WhatsApp oficial {_school_object_reference(context.school_reference)} hoje e {value}.'
        if len(whatsapp_lines) == 1:
            return f'O WhatsApp oficial de {context.school_reference} hoje e {whatsapp_lines[0]}.'
        lines = [f'Os canais de WhatsApp publicados por {context.school_reference} hoje sao:']
        lines.extend(f'- {item}' for item in whatsapp_lines)
        return '\n'.join(lines)
    if context.requested_channel == 'email':
        primary_email = _select_primary_contact_entry(
            context.profile,
            'email',
            context.contact_reference_message,
            preferred_labels=context.preferred_contact_labels,
        )
        if primary_email and (
            _contact_is_general_school_query(context.contact_reference_message)
            or not _wants_contact_list(context.contact_reference_message)
        ):
            label = primary_email.get('label')
            value = primary_email.get('value')
            if label:
                return (
                    f'O email mais direto {_school_object_reference(context.school_reference)} hoje e {value}, '
                    f'{_format_contact_origin(label, "email")}.'
                )
            return f'O email institucional publicado de {context.school_reference} e {value}.'
        if len(email_lines) == 1:
            return f'O email institucional publicado de {context.school_reference} e {email_lines[0]}.'
        lines = [f'Os emails institucionais publicados de {context.school_reference} hoje sao:']
        lines.extend(f'- {item}' for item in email_lines)
        return '\n'.join(lines)
    lines = [f'Voce pode falar com {context.school_reference} por estes canais oficiais:']
    lines.extend(f'- {item}' for item in [*phone_lines, *whatsapp_lines, *email_lines])
    if _message_matches_term(context.normalized, 'fax'):
        lines.append('- Fax: nao publicado')
    return '\n'.join(lines)


def _handle_public_careers(context: PublicProfileContext) -> str:
    catalog = _service_catalog_index(context.profile)
    careers_entry = catalog.get('carreiras_docentes')
    if careers_entry is None:
        return (
            f'Hoje eu nao tenho um fluxo publico de recrutamento docente estruturado no perfil canonico de {context.school_reference}. '
            'Se quiser, eu posso te passar os canais institucionais da escola.'
        )
    request_channel = str(careers_entry.get('request_channel', 'canal institucional')).strip()
    typical_eta = _humanize_service_eta(str(careers_entry.get('typical_eta', 'prazo nao informado')))
    notes = str(careers_entry.get('notes', '')).strip()
    response = (
        f'Se voce quer se candidatar para dar aula em {context.school_reference}, o caminho mais direto hoje e {request_channel}. '
        f'O prazo tipico e {typical_eta}.'
    )
    if notes:
        response += f' {notes}'
    return response


def _target_public_feature_for_operating_hours(context: PublicProfileContext) -> dict[str, Any] | None:
    feature_map = _feature_inventory_map(context.profile)
    requested_features = _requested_public_features(context.source_message)
    if not requested_features and _is_follow_up_query(context.source_message):
        recent_feature = _recent_public_feature_key(context.conversation_context)
        if recent_feature:
            requested_features = [recent_feature]
    if not requested_features and context.semantic_plan and context.semantic_plan.focus_hint:
        requested_features = _requested_public_features(context.semantic_plan.focus_hint)
    if len(requested_features) != 1:
        return None
    feature_entry = feature_map.get(requested_features[0])
    return feature_entry if isinstance(feature_entry, dict) and bool(feature_entry.get('available')) else None


def _handle_public_operating_hours(context: PublicProfileContext) -> str:
    requested_attribute = context.requested_attribute_override or _requested_operating_hours_attribute(
        context.source_message,
        context.conversation_context,
    )
    requested_attributes = set(_requested_public_attributes(context.source_message))
    feature_entry = _target_public_feature_for_operating_hours(context)
    if feature_entry is not None:
        label = str(feature_entry.get('label', 'esse espaco')).strip() or 'esse espaco'
        notes = str(feature_entry.get('notes', '')).strip()
        feature_key = str(feature_entry.get('feature_key', '')).strip().lower()
        feature_reference = 'A biblioteca' if feature_key == 'biblioteca' else f'O espaco {label}'
        if notes:
            normalized_notes = _normalize_text(notes)
            hours_match = re.search(r'das\s+[0-9h:]+\s+as\s+[0-9h:]+', normalized_notes)
            hours_text = hours_match.group(0) if hours_match else None
            if 'name' in requested_attributes:
                if feature_key == 'biblioteca' and hours_text:
                    return f'A Biblioteca {label} funciona das 7h30 as 18h00.'
                return f'{feature_reference} se chama {label}. Pelo perfil publico, {notes}'
            if feature_key == 'biblioteca' and hours_text:
                return f'A Biblioteca {label} funciona das 7h30 as 18h00.'
            return f'Pelo perfil publico, {label} funciona assim hoje: {notes}'
    if requested_attribute == 'open_time':
        return (
            f'O atendimento presencial {_school_object_reference(context.school_reference)} abre as 7h00, de segunda a sexta-feira. '
            'Se voce estiver falando da biblioteca, ela abre as 7h30.'
        )
    if requested_attribute == 'close_time':
        return (
            f'O atendimento presencial {_school_object_reference(context.school_reference)} fecha as 17h30, de segunda a sexta-feira. '
            'Se voce estiver falando da biblioteca, ela fecha as 18h00.'
        )
    return (
        f'O atendimento presencial {_school_object_reference(context.school_reference)} abre as 7h00 e segue ate as 17h30, de segunda a sexta-feira. '
        'Se voce estiver falando da biblioteca, ela funciona das 7h30 as 18h00.'
    )


def _handle_public_timeline(context: PublicProfileContext) -> str:
    entries = context.profile.get('public_timeline')
    if not isinstance(entries, list) or not entries:
        return f'Hoje a base publica de {context.school_reference} nao traz um marco institucional estruturado para essa data.'

    normalized = context.normalized

    def _pick(topic_fragment: str) -> dict[str, Any] | None:
        for item in entries:
            if not isinstance(item, dict):
                continue
            if topic_fragment in str(item.get('topic_key', '')):
                return item
        return None

    chosen: dict[str, Any] | None = None
    recent_focus = _recent_conversation_focus(context.conversation_context) or {}
    if (
        _is_follow_up_query(context.source_message)
        and str(recent_focus.get('kind', '') or '').strip() == 'admissions'
        and any(
            _message_matches_term(normalized, term)
            for term in {'inicio das aulas', 'início das aulas', 'comecam as aulas', 'começam as aulas', 'aulas'}
        )
    ):
        chosen = _pick('school_year_start')
    elif _message_matches_term(normalized, 'matricula') or _message_matches_term(normalized, 'matrícula'):
        chosen = _pick('admissions_opening')
    elif _message_matches_term(normalized, 'formatura'):
        chosen = _pick('graduation')
    elif any(
        _message_matches_term(normalized, term)
        for term in {'inicio das aulas', 'início das aulas', 'comecam as aulas', 'começam as aulas', 'ano letivo'}
    ):
        chosen = _pick('school_year_start')

    if chosen is None:
        chosen = next((item for item in entries if isinstance(item, dict)), None)
    if chosen is None:
        return f'Hoje a base publica de {context.school_reference} nao traz um marco institucional estruturado para essa data.'

    summary = str(chosen.get('summary', '')).strip()
    notes = str(chosen.get('notes', '')).strip()
    if notes:
        return f'{summary} {notes}'.strip()
    return summary


def _recent_user_message_mentions(
    conversation_context: dict[str, Any] | None,
    terms: set[str],
) -> bool:
    if not isinstance(conversation_context, dict):
        return False
    seen_current_user = False
    for sender_type, content in reversed(_recent_message_lines(conversation_context)):
        if sender_type != 'user':
            continue
        if not seen_current_user:
            seen_current_user = True
            continue
        normalized = _normalize_text(content)
        if any(_message_matches_term(normalized, term) for term in terms):
            return True
    return False


def _compose_public_school_year_start_answer(profile: dict[str, Any], school_reference: str) -> str | None:
    entries = profile.get('public_timeline')
    if not isinstance(entries, list):
        return None
    for item in entries:
        if not isinstance(item, dict):
            continue
        if 'school_year_start' not in str(item.get('topic_key', '')):
            continue
        summary = str(item.get('summary', '')).strip()
        notes = str(item.get('notes', '')).strip()
        if summary and notes:
            return f'{summary} {notes}'.strip()
        if summary:
            return summary
    return None


def _event_query_tokens(message: str, focus_hint: str | None = None) -> set[str]:
    source = _normalize_text(' '.join(part for part in [focus_hint or '', message] if part).strip())
    tokens = {
        token
        for token in re.findall(r'[a-z0-9]{3,}', source)
        if token not in {
            'quando',
            'qual',
            'quais',
            'que',
            'dia',
            'data',
            'proximo',
            'proxima',
            'proximoa',
            'evento',
            'eventos',
            'publico',
            'publicos',
            'amanha',
            'hoje',
            'escola',
            'colegio',
        }
    }
    return tokens


def _format_event_datetime_br(value: str | None) -> str | None:
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace('Z', '+00:00'))
    except Exception:
        return None
    return parsed.astimezone(ZoneInfo('America/Sao_Paulo')).strftime('%d/%m/%Y às %Hh%M')


def _select_public_calendar_events(
    *,
    events: list[dict[str, Any]],
    message: str,
    focus_hint: str | None,
) -> list[dict[str, Any]]:
    normalized = _normalize_text(message)
    tokens = _event_query_tokens(message, focus_hint)
    scored: list[tuple[int, dict[str, Any]]] = []
    for event in events:
        haystack = _normalize_text(
            ' '.join(
                str(event.get(key, '')).strip()
                for key in ('title', 'description', 'category', 'audience')
            )
        )
        score = 0
        for token in tokens:
            if token in haystack:
                score += 2
        if any(_message_matches_term(normalized, term) for term in {'reuniao', 'reunião', 'pais', 'responsaveis', 'responsáveis'}) and (
            'meeting' in haystack or 'reuniao' in haystack or 'responsaveis' in haystack
        ):
            score += 3
        if any(_message_matches_term(normalized, term) for term in {'mostra', 'ciencias', 'ciências'}) and (
            'mostra' in haystack or 'ciencias' in haystack
        ):
            score += 3
        if any(_message_matches_term(normalized, term) for term in {'visita', 'tour', 'guiada'}) and (
            'visita' in haystack or 'open_house' in haystack
        ):
            score += 3
        if score > 0:
            scored.append((score, event))
    if scored:
        scored.sort(
            key=lambda item: (
                -item[0],
                str(item[1].get('starts_at', '')),
                str(item[1].get('title', '')),
            )
        )
        return [item for _score, item in scored[:2]]
    sorted_events = sorted(
        events,
        key=lambda event: (
            str(event.get('starts_at', '')),
            str(event.get('title', '')),
        ),
    )
    return sorted_events[:2]


def _handle_public_calendar_events(context: PublicProfileContext) -> str:
    events = context.profile.get('public_calendar_events')
    if not isinstance(events, list) or not events:
        return f'Hoje a base publica de eventos de {context.school_reference} nao trouxe agenda estruturada para esse pedido.'

    selected = _select_public_calendar_events(
        events=[item for item in events if isinstance(item, dict)],
        message=context.source_message,
        focus_hint=context.semantic_plan.focus_hint if context.semantic_plan else None,
    )
    if not selected:
        return f'Hoje eu nao encontrei um evento publico especifico para esse pedido em {context.school_reference}.'

    if len(selected) == 1:
        item = selected[0]
        title = str(item.get('title', 'Evento publico')).strip()
        description = str(item.get('description', '')).strip()
        starts_at = _format_event_datetime_br(item.get('starts_at'))
        ends_at = _format_event_datetime_br(item.get('ends_at'))
        time_part = f'{starts_at}' if starts_at else 'data ainda nao informada'
        if starts_at and ends_at:
            time_part = f'{starts_at} até {ends_at.split(" às ")[-1]}'
        response = f'{title}: {time_part}.'
        if description:
            response += f' {description}'
        return response

    lines = ['Encontrei estes proximos eventos publicos relacionados a esse assunto:']
    for item in selected:
        title = str(item.get('title', 'Evento publico')).strip()
        starts_at = _format_event_datetime_br(item.get('starts_at')) or 'data ainda nao informada'
        lines.append(f'- {title}: {starts_at}.')
    return '\n'.join(lines)


def _handle_public_location(context: PublicProfileContext) -> str:
    location = ', '.join(part for part in [context.address_line, context.district, context.city, context.state] if part)
    if context.postal_code:
        location = f'{location}, CEP {context.postal_code}'
    return f'{context.school_reference_capitalized} fica em {location}.'


def _handle_public_confessional(context: PublicProfileContext) -> str:
    if context.confessional_status == 'laica':
        return (
            f'{context.school_reference_capitalized} e uma escola laica. '
            'A proposta institucional e plural e nao confessional.'
        )
    return f'Hoje o perfil publico classifica {context.school_reference} como {context.confessional_status}.'


def _handle_public_curriculum(context: PublicProfileContext) -> str:
    pedagogical_answer = _compose_public_pedagogical_answer(context.profile, context.source_message)
    if pedagogical_answer:
        return pedagogical_answer
    requested_unpublished_segment = _requested_unpublished_public_segment(context)
    if requested_unpublished_segment:
        return _compose_public_segment_scope_gap(
            context,
            requested_segment=requested_unpublished_segment,
            topic='grade curricular',
        )
    if context.curriculum_basis and context.curriculum_components:
        components = ', '.join(context.curriculum_components[:8])
        extra = ', alem de projeto de vida, monitorias e trilhas eletivas' if len(context.curriculum_components) > 8 else ''
        return (
            f'No Ensino Medio, {context.school_reference} segue a BNCC e um curriculo proprio de aprofundamento academico. '
            f'Os componentes que aparecem hoje na base publica incluem {components}{extra}.'
        )
    if context.curriculum_basis:
        return f'Hoje a base curricular publica de {context.school_reference} e esta: {context.curriculum_basis}'
    return (
        f'Hoje eu nao encontrei um detalhamento curricular estruturado de {context.school_reference}. '
        'Se quiser, eu posso resumir a proposta pedagogica publicada.'
    )


def _handle_public_kpi(context: PublicProfileContext) -> str:
    entries = _select_public_kpis(context.profile, context.source_message)
    if not entries:
        return f'Hoje o perfil publico de {context.school_reference} nao traz indicadores institucionais publicados.'
    if len(entries) == 1:
        item = entries[0]
        notes = str(item.get('notes', '')).strip()
        return (
            f"Hoje, {item.get('label', 'o indicador institucional')} esta em {item.get('value', '--')}{item.get('unit', '')} "
            f"({item.get('reference_period', 'periodo nao informado')}). {notes}".strip()
        )
    lines = [f'Os indicadores publicos mais recentes de {context.school_reference} sao:']
    for item in entries:
        lines.append(
            f"- {item.get('label', 'Indicador')}: {item.get('value', '--')}{item.get('unit', '')} "
            f"({item.get('reference_period', 'periodo nao informado')})"
        )
    return '\n'.join(lines)


def _handle_public_highlight(context: PublicProfileContext) -> str:
    item = _select_public_highlight(context.profile, context.source_message)
    if item is None:
        return f'Hoje o perfil publico de {context.school_reference} nao traz diferenciais institucionais consolidados.'
    evidence_line = str(item.get('evidence_line', '')).strip()
    intro = 'Um dos diferenciais documentados desta escola'
    if any(
        _message_matches_term(context.normalized, term)
        for term in {'curiosidade', 'curiosidades', 'unica', 'única'}
    ):
        intro = 'Uma curiosidade documentada desta escola'
    title = str(item.get('title', 'Diferencial institucional')).strip()
    description = str(item.get('description', '')).strip()
    lines = [f'{intro} e {title}. {description}'.strip()]
    if evidence_line:
        lines.append(f'Isso aparece de forma bem clara na proposta institucional: {evidence_line}')
    return ' '.join(line for line in lines if line)


def _handle_public_visit(context: PublicProfileContext) -> str:
    offers = _public_visit_offers(context.profile)
    services = _public_service_catalog(context.profile)
    if not offers:
        return f'Hoje o perfil publico de {context.school_reference} nao traz janelas de visita institucional.'
    lines = [f'Hoje {_school_subject_reference(context.school_reference)} publica estas janelas de visita:']
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


def _is_public_scholarship_query(message: str) -> bool:
    normalized = _normalize_text(message)
    return any(_message_matches_term(normalized, term) for term in PUBLIC_SCHOLARSHIP_TERMS)


def _is_public_enrichment_query(message: str) -> bool:
    normalized = _normalize_text(message)
    return any(_message_matches_term(normalized, term) for term in PUBLIC_ENRICHMENT_TERMS)


def _compose_public_scholarship_answer(context: PublicProfileContext) -> str:
    requested_unpublished_segment = _requested_unpublished_public_segment(context)
    if requested_unpublished_segment:
        return _compose_public_segment_scope_gap(
            context,
            requested_segment=requested_unpublished_segment,
            topic='bolsas e descontos',
        )
    service = next(
        (
            item
            for item in _public_service_catalog(context.profile)
            if str(item.get('service_key', '')).strip() == 'atendimento_admissoes'
        ),
        None,
    )
    relevant_rows = [
        row for row in context.tuition_reference
        if isinstance(row, dict) and (context.segment is None or str(row.get('segment')) == context.segment)
    ]
    if not relevant_rows:
        relevant_rows = [row for row in context.tuition_reference if isinstance(row, dict)]

    policy_notes: list[str] = []
    for row in relevant_rows:
        notes = str(row.get('notes', '')).strip()
        normalized_notes = _normalize_text(notes)
        if notes and any(
            _message_matches_term(normalized_notes, term)
            for term in {'irmaos', 'irmãos', 'pagamento pontual', 'politica comercial', 'política comercial'}
        ):
            policy_notes.append(notes)
    lines = [
        f'Hoje, pelo que {context.school_reference} publica, bolsas e descontos entram no atendimento comercial de matricula.',
    ]
    if policy_notes:
        lines.append(f'A referencia comercial atual tambem menciona {policy_notes[0].lower()}')
    else:
        lines.append(
            'A base publica confirma que esse tema passa pelo canal comercial, junto com simulacao financeira e processo de ingresso.'
        )
    if isinstance(service, dict):
        request_channel = str(service.get('request_channel', 'canal institucional')).strip()
        eta = _humanize_service_eta(str(service.get('typical_eta', 'retorno em ate 1 dia util')))
        notes = str(service.get('notes', '')).strip()
        lines.append(
            f'O caminho mais direto hoje e {service.get("title", "matricula e atendimento comercial")} por {request_channel}, com {eta}.'
        )
        if notes:
            lines.append(notes)
    return ' '.join(line.strip() for line in lines if line and line.strip())


def _compose_public_enrichment_answer(context: PublicProfileContext) -> str:
    requested_unpublished_segment = _requested_unpublished_public_segment(context)
    if requested_unpublished_segment:
        return _compose_public_segment_scope_gap(
            context,
            requested_segment=requested_unpublished_segment,
            topic='atividades complementares',
        )
    relevant_rows = [
        row for row in context.shift_offers
        if isinstance(row, dict) and _public_segment_matches(str(row.get('segment')), context.segment)
    ]
    if not relevant_rows:
        relevant_rows = [row for row in context.shift_offers if isinstance(row, dict)]

    available_features = _public_feature_inventory(context.profile)
    enrichment_labels: list[str] = []
    for key in ('biblioteca', 'danca', 'teatro', 'futebol', 'volei', 'maker', 'laboratorio'):
        item = next(
            (
                feature
                for feature in available_features
                if str(feature.get('feature_key', '')).strip() == key and bool(feature.get('available'))
            ),
            None,
        )
        if not isinstance(item, dict):
            continue
        label = str(item.get('label', '')).strip()
        if label and label not in enrichment_labels:
            enrichment_labels.append(label)

    if len(relevant_rows) == 1:
        row = relevant_rows[0]
        lines = [
            f'Hoje {_school_subject_reference(context.school_reference)} divulga atividades complementares no {str(row.get("segment", "segmento")).lower()}.',
            str(row.get('notes', '')).strip(),
        ]
    else:
        lines = [f'Hoje {_school_subject_reference(context.school_reference)} divulga atividades complementares no contraturno de forma assim:']
        for row in relevant_rows[:3]:
            segment = str(row.get('segment', 'Segmento')).strip()
            notes = str(row.get('notes', '')).strip()
            if notes:
                lines.append(f'- {segment}: {notes}')
    if enrichment_labels:
        labels_preview = ', '.join(enrichment_labels[:6])
        lines.append(f'Entre as ofertas que aparecem com mais clareza hoje estao {labels_preview}.')
    return ' '.join(line.strip() for line in lines if line and line.strip())


def _handle_public_pricing(context: PublicProfileContext) -> str:
    if _is_public_scholarship_query(context.source_message):
        return _compose_public_scholarship_answer(context)
    requested_unpublished_segment = _requested_unpublished_public_segment(context)
    if requested_unpublished_segment:
        return _compose_public_segment_scope_gap(
            context,
            requested_segment=requested_unpublished_segment,
            topic='mensalidades publicas',
        )
    relevant_rows = [
        row for row in context.tuition_reference
        if isinstance(row, dict) and _public_segment_matches(str(row.get('segment')), context.segment)
    ]
    if not relevant_rows:
        relevant_rows = [row for row in context.tuition_reference if isinstance(row, dict)]
    if len(relevant_rows) == 1:
        row = relevant_rows[0]
        return (
            f"Para {row.get('segment', 'esse segmento')} no turno {row.get('shift_label', 'regular')}, "
            f"a mensalidade publica de referencia em 2026 e {row.get('monthly_amount', '0.00')} "
            f"e a taxa de matricula e {row.get('enrollment_fee', '0.00')}. "
            f"{str(row.get('notes', '')).strip()} "
            'Se quiser, eu tambem posso resumir bolsas, descontos comerciais e canais de matricula.'
        ).strip()
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


def _handle_public_schedule(context: PublicProfileContext) -> str:
    requested_unpublished_segment = _requested_unpublished_public_segment(context)
    if requested_unpublished_segment:
        return _compose_public_segment_scope_gap(
            context,
            requested_segment=requested_unpublished_segment,
            topic='horarios',
        )
    relevant_rows = [
        row for row in context.shift_offers
        if isinstance(row, dict) and _public_segment_matches(str(row.get('segment')), context.segment)
    ]
    if not relevant_rows:
        relevant_rows = [row for row in context.shift_offers if isinstance(row, dict)]
    if len(relevant_rows) == 1:
        row = relevant_rows[0]
        grade_reference = _extract_grade_reference(context.source_message)
        if grade_reference:
            return (
                f'O {grade_reference} fica em {row.get("segment", "esse segmento")}. '
                f'As atividades do turno {row.get("shift_label", "regular").lower()} vao de {row.get("starts_at", "--:--")} a {row.get("ends_at", "--:--")}. '
                f'{str(row.get("notes", "")).strip()}'
            ).strip()
        return (
            f"Para {row.get('segment', 'esse segmento')}, as atividades no turno {row.get('shift_label', 'regular').lower()} "
            f"vao de {row.get('starts_at', '--:--')} a {row.get('ends_at', '--:--')}. "
            f"{str(row.get('notes', '')).strip()}"
        ).strip()
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


def _handle_public_features(context: PublicProfileContext) -> str:
    if _is_public_enrichment_query(context.source_message):
        return _compose_public_enrichment_answer(context)
    feature_schedule_follow_up = _compose_public_feature_schedule_follow_up(
        profile=context.profile,
        original_message=context.source_message,
        analysis_message=context.message,
        conversation_context=context.conversation_context,
    )
    if feature_schedule_follow_up:
        return feature_schedule_follow_up
    feature_answer = _compose_public_feature_answer(
        profile=context.profile,
        original_message=context.source_message,
        analysis_message=context.message,
        conversation_context=context.conversation_context,
    )
    if feature_answer:
        return feature_answer
    return (
        f'Hoje o perfil publico de {context.school_reference} nao traz esse detalhe de estrutura ou atividade. '
        'Se quiser, eu posso te mostrar o que esta oficialmente documentado.'
    )


def _handle_public_segments(context: PublicProfileContext) -> str:
    segments = context.profile.get('segments')
    if not isinstance(segments, list) or not segments:
        return f'Hoje o perfil publico de {context.school_reference} nao traz os segmentos atendidos.'
    lines = [f'Hoje {context.school_reference} atende estes segmentos:']
    lines.extend(f'- {item}' for item in segments if isinstance(item, str))
    return '\n'.join(lines)


def _handle_public_school_name(context: PublicProfileContext) -> str:
    return f'O nome oficial da escola e {context.school_name}.'


def _public_profile_handler_registry() -> dict[str, Callable[[PublicProfileContext], str]]:
    return {
        'acknowledgement': _handle_public_acknowledgement,
        'greeting': _handle_public_greeting,
        'utility_date': _handle_public_utility_date,
        'auth_guidance': _handle_public_auth_guidance,
        'access_scope': _handle_public_access_scope,
        'assistant_identity': _handle_public_assistant_identity,
        'service_routing': _handle_public_service_routing,
        'capabilities': _handle_public_capabilities,
        'document_submission': _handle_public_document_submission,
        'careers': _handle_public_careers,
        'teacher_directory': _handle_public_teacher_directory,
        'leadership': _handle_public_leadership,
        'web_presence': _handle_public_web_presence,
        'social_presence': _handle_public_social_presence,
        'comparative': _handle_public_comparative,
        'contacts': _handle_public_contacts,
        'operating_hours': _handle_public_operating_hours,
        'timeline': _handle_public_timeline,
        'calendar_events': _handle_public_calendar_events,
        'location': _handle_public_location,
        'confessional': _handle_public_confessional,
        'curriculum': _handle_public_curriculum,
        'kpi': _handle_public_kpi,
        'highlight': _handle_public_highlight,
        'visit': _handle_public_visit,
        'pricing': _handle_public_pricing,
        'schedule': _handle_public_schedule,
        'features': _handle_public_features,
        'segments': _handle_public_segments,
        'school_name': _handle_public_school_name,
    }


AGENTIC_PUBLIC_COMPOSITION_ACTS = {
    'canonical_fact',
    'school_name',
    'segments',
    'leadership',
    'contacts',
    'web_presence',
    'social_presence',
    'comparative',
    'pricing',
    'schedule',
    'operating_hours',
    'curriculum',
    'features',
    'highlight',
    'visit',
    'location',
    'confessional',
    'careers',
    'timeline',
    'calendar_events',
}


async def _compose_public_profile_answer_agentic(
    *,
    settings: Any,
    profile: dict[str, Any],
    actor: dict[str, Any] | None = None,
    message: str,
    original_message: str | None = None,
    conversation_context: dict[str, Any] | None = None,
    semantic_plan: PublicInstitutionPlan | None = None,
    deterministic_text_sink: dict[str, Any] | None = None,
) -> str:
    deterministic_text = _compose_public_profile_answer(
        profile,
        message,
        actor=actor,
        original_message=original_message,
        conversation_context=conversation_context,
        semantic_plan=semantic_plan,
    )
    if deterministic_text_sink is not None:
        deterministic_text_sink['deterministic_text'] = deterministic_text
    context = _build_public_profile_context(
        profile,
        message,
        actor=actor,
        original_message=original_message,
        conversation_context=conversation_context,
        semantic_plan=semantic_plan,
    )
    resolved_act = _resolve_public_profile_act(context)
    if resolved_act not in AGENTIC_PUBLIC_COMPOSITION_ACTS:
        return deterministic_text

    evidence_bundle = build_public_evidence_bundle(
        profile,
        primary_act=resolved_act,
        secondary_acts=semantic_plan.secondary_acts if semantic_plan is not None else (),
        request_message=original_message or message,
        focus_hint=semantic_plan.focus_hint if semantic_plan is not None else None,
    )
    if evidence_bundle is None:
        return deterministic_text

    plan_payload = {
        'conversation_act': resolved_act,
        'secondary_acts': list(evidence_bundle.secondary_acts),
        'requested_attribute': semantic_plan.requested_attribute if semantic_plan else None,
        'requested_channel': semantic_plan.requested_channel if semantic_plan else None,
        'semantic_source': semantic_plan.semantic_source if semantic_plan else 'rules',
    }
    llm_text = await compose_public_grounded_with_provider(
        settings=settings,
        request_message=original_message or message,
        draft_text=deterministic_text,
        public_plan=plan_payload,
        evidence_lines=[fact.text for fact in evidence_bundle.facts],
        conversation_context=conversation_context,
        school_profile=profile,
    )
    return llm_text or deterministic_text


def _compose_public_profile_answer(
    profile: dict[str, Any],
    message: str,
    *,
    actor: dict[str, Any] | None = None,
    original_message: str | None = None,
    conversation_context: dict[str, Any] | None = None,
    semantic_plan: PublicInstitutionPlan | None = None,
) -> str:
    context = _build_public_profile_context(
        profile,
        message,
        actor=actor,
        original_message=original_message,
        conversation_context=conversation_context,
        semantic_plan=semantic_plan,
    )
    normalized_source_message = _normalize_text(context.source_message)
    if (
        (
            _is_follow_up_query(context.source_message)
            or normalized_source_message.startswith('depois disso')
        )
        and any(
            _message_matches_term(normalized_source_message, term)
            for term in {'inicio das aulas', 'início das aulas', 'comecam as aulas', 'começam as aulas', 'aulas'}
        )
        and (
            normalized_source_message.startswith('depois disso')
            or _recent_user_message_mentions(
                context.conversation_context,
                {'matricula', 'matrícula', 'proximo ciclo', 'próximo ciclo', 'inscricoes', 'inscrições'},
            )
        )
    ):
        school_year_start_answer = _compose_public_school_year_start_answer(profile, context.school_reference)
        if school_year_start_answer:
            return school_year_start_answer
    registry = _public_profile_handler_registry()
    resolved_act = _resolve_public_profile_act(context)
    handler = registry.get(resolved_act)
    if handler is not None:
        primary_text = handler(context)
        extra_texts: list[str] = []
        if semantic_plan is not None:
            secondary_acts = semantic_plan.secondary_acts[:2]
            if semantic_plan.conversation_act == 'timeline' and not _has_public_multi_intent_signal(context.source_message):
                secondary_acts = ()
            for act in secondary_acts:
                if act == resolved_act:
                    continue
                if (
                    resolved_act == 'operating_hours'
                    and act == 'features'
                    and _target_public_feature_for_operating_hours(context) is not None
                ):
                    continue
                extra_handler = registry.get(act)
                if extra_handler is None:
                    continue
                candidate = extra_handler(context).strip()
                if not candidate:
                    continue
                normalized_candidate = _normalize_text(candidate)
                if normalized_candidate in _normalize_text(primary_text):
                    continue
                if any(normalized_candidate in _normalize_text(text) for text in extra_texts):
                    continue
                extra_texts.append(candidate)
        if extra_texts:
            return '\n\n'.join([primary_text, *extra_texts])
        return primary_text
    return _compose_public_profile_answer_legacy(
        profile,
        message,
        original_message=original_message,
        conversation_context=conversation_context,
        semantic_plan=semantic_plan,
    )


def _compose_negative_requirement_answer() -> str:
    lines = [
        'A base atual informa os documentos exigidos para a matricula, mas nao lista explicitamente quais documentos sao dispensaveis.',
        'Por isso, nao e seguro afirmar o que voce "nao precisa" levar.',
        'O que esta explicitamente exigido hoje e:',
    ]
    lines.extend(f'- {item}' for item in KNOWN_ADMISSIONS_REQUIREMENTS)
    lines.append('Se quiser, eu posso resumir apenas os documentos exigidos ou explicar as etapas da matricula.')
    return '\n'.join(lines)


def _compose_required_documents_answer(profile: dict[str, Any] | None = None) -> str:
    requirements: list[str] = []
    if isinstance(profile, dict):
        requirements = [
            str(item).strip()
            for item in (profile.get('admissions_required_documents') or [])
            if isinstance(item, str) and str(item).strip()
        ]
    requirements = requirements or list(KNOWN_ADMISSIONS_REQUIREMENTS)
    lines = ['Hoje os documentos exigidos para a matricula publicados pela escola sao:']
    lines.extend(f'- {item}' for item in requirements)
    lines.append('Se quiser, eu tambem posso explicar as etapas da matricula ou como funciona o envio inicial desses documentos.')
    return '\n'.join(lines)


def _compose_comparative_gap_answer(profile: dict[str, Any] | None = None) -> str:
    return _compose_public_comparative_answer(profile or {})


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


def _extract_protocol_code_from_text(text: str | None) -> str | None:
    if not text:
        return None
    match = PROTOCOL_CODE_PATTERN.search(text)
    if match is None:
        return None
    return match.group(0).upper()


def _extract_protocol_code_hint(
    message: str,
    conversation_context: dict[str, Any] | None,
) -> str | None:
    direct_match = _extract_protocol_code_from_text(message)
    if direct_match:
        return direct_match
    for payload in _recent_orchestration_trace_payloads(conversation_context):
        slot_memory = payload.get('slot_memory')
        if not isinstance(slot_memory, dict):
            continue
        protocol_code = str(slot_memory.get('protocol_code', '') or '').strip()
        if protocol_code:
            return protocol_code
    for _sender_type, content in reversed(_recent_message_lines(conversation_context)):
        code = _extract_protocol_code_from_text(content)
        if code:
            return code
    return None


def _detect_workflow_kind_hint(
    message: str,
    conversation_context: dict[str, Any] | None,
) -> str | None:
    normalized = _normalize_text(message)
    if any(_message_matches_term(normalized, term) for term in WORKFLOW_VISIT_TERMS):
        return 'visit_booking'
    if any(_message_matches_term(normalized, term) for term in WORKFLOW_REQUEST_TERMS):
        return 'institutional_request'
    if any(_message_matches_term(normalized, term) for term in WORKFLOW_HANDOFF_TERMS):
        return 'support_handoff'

    focus = _recent_trace_focus(conversation_context)
    if isinstance(focus, dict):
        focus_kind = str(focus.get('kind', '')).strip()
        if focus_kind == 'visit':
            return 'visit_booking'
        if focus_kind == 'request':
            return 'institutional_request'
        if focus_kind == 'support':
            return 'support_handoff'

    for _sender_type, content in reversed(_recent_message_lines(conversation_context)):
        content_normalized = _normalize_text(content)
        if 'pedido de visita registrado' in content_normalized or 'vis-' in content_normalized:
            return 'visit_booking'
        if 'solicitacao institucional registrada' in content_normalized or 'req-' in content_normalized:
            return 'institutional_request'
        if 'encaminhei sua solicitacao para a fila' in content_normalized or 'atd-' in content_normalized:
            return 'support_handoff'
    return None


def _conversation_context_payload(conversation_context: ConversationContextBundle | None) -> dict[str, Any] | None:
    if conversation_context is None:
        return None
    return {
        'conversation_external_id': conversation_context.conversation_external_id,
        'message_count': conversation_context.message_count,
        'recent_messages': conversation_context.recent_messages,
        'recent_tool_calls': conversation_context.recent_tool_calls,
    }


def _looks_like_visit_update_follow_up(message: str) -> bool:
    normalized = _normalize_text(message)
    if _extract_requested_date(message) or _extract_requested_window(message):
        return True
    return any(
        _message_matches_term(normalized, term)
        for term in {
            'pode ser',
            'nesse dia',
            'neste dia',
            'naquele dia',
            'esse dia',
            'aquele dia',
            'nessa data',
            'nesta data',
        }
    )


def _build_analysis_message(message: str, conversation_context: ConversationContextBundle | None) -> str:
    if conversation_context is None:
        return message

    context_payload = _conversation_context_payload(conversation_context)
    if _is_discourse_repair_reset_query(message, context_payload):
        return message
    recent_focus = _recent_conversation_focus(context_payload)
    if (
        _recent_trace_used_tool(context_payload, 'get_administrative_status')
        and _detect_admin_attribute_request(message, context_payload) is not None
    ):
        return f'{message} sobre dados cadastrais do seu cadastro'
    if recent_focus and recent_focus.get('kind') == 'visit' and _looks_like_visit_update_follow_up(message):
        return f'remarcar visita: {message}'
    if not conversation_context.recent_messages:
        return message
    if not _is_follow_up_query(message):
        return message

    last_user_message = _extract_recent_user_message(conversation_context.recent_messages)
    last_assistant_message = _extract_recent_assistant_message(conversation_context.recent_messages)
    if not last_user_message and not last_assistant_message:
        return message

    if recent_focus:
        active_task = str(recent_focus.get('active_task', '') or '').strip()
        if active_task == 'public:document_submission':
            return f'{message} sobre envio de documentos pela secretaria ou portal institucional'
        if active_task == 'workflow:human_handoff' and any(
            _message_matches_term(_normalize_text(message), term)
            for term in {'abre pra', 'abre para', 'encaminha pra', 'encaminha para'}
        ):
            return f'abrir atendimento humano para {message}'
        if active_task.startswith(('admin:', 'finance:', 'academic:', 'workflow:')):
            context_phrase = _follow_up_context_phrase(
                active_task,
                recent_focus.get('active_entity'),
            )
            if context_phrase:
                return f'{message} sobre {context_phrase}'

    entity_hints = {
        *_extract_public_entity_hints(last_user_message or ''),
        *_extract_public_entity_hints(last_assistant_message or ''),
    }
    if entity_hints:
        referents = ', '.join(sorted(entity_hints))
        return f'{message} sobre {referents}'
    if recent_focus:
        context_phrase = _follow_up_context_phrase(
            recent_focus.get('active_task'),
            recent_focus.get('active_entity'),
        )
        if context_phrase:
            return f'{message} sobre {context_phrase}'
        active_entity = recent_focus.get('active_entity')
        if active_entity:
            return f'{message} sobre {active_entity}'
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
    normalized_message = _normalize_text(message or '')
    if message and _is_public_document_submission_query(message):
        if _message_matches_term(normalized_message, 'fax'):
            return (
                'Hoje a escola nao utiliza fax para envio de documentos. '
                'Para isso, use portal institucional, email da secretaria, secretaria presencial.'
            )
        if _message_matches_term(normalized_message, 'telegrama'):
            return (
                'Hoje a escola nao publica telegrama como canal valido para documentos. '
                'Para isso, use portal institucional, email da secretaria, secretaria presencial.'
            )
        if _message_matches_term(normalized_message, 'caixa postal'):
            return (
                'Hoje a escola nao trabalha com caixa postal para esse tipo de envio. '
                'Para documentos, use portal institucional, email da secretaria, secretaria presencial.'
            )
        return (
            'Para enviar documentos hoje, use portal institucional, email da secretaria ou secretaria presencial.'
        )
    if any(
        _message_matches_term(normalized_message, term)
        for term in {'abre pra', 'abre para', 'encaminha pra', 'encaminha para'}
    ):
        queue_label = None
        if any(_message_matches_term(normalized_message, term) for term in {'secretaria'}):
            queue_label = 'secretaria'
        elif any(_message_matches_term(normalized_message, term) for term in {'financeiro'}):
            queue_label = 'financeiro'
        elif any(_message_matches_term(normalized_message, term) for term in {'direcao', 'direção'}):
            queue_label = 'direcao'
        elif any(_message_matches_term(normalized_message, term) for term in {'coordenacao', 'coordenação'}):
            queue_label = 'coordenacao'
        if queue_label:
            return (
                f'Sem problema, sigo daqui com atendimento humano para {queue_label}. '
                'Se quiser, eu tambem posso resumir o assunto em uma frase para deixar esse encaminhamento mais claro.'
            )
    focus = _extract_public_gap_focus(message or '')
    if focus:
        return (
            f'Hoje eu nao encontrei uma informacao publica oficial sobre {focus}. '
            'Se isso for decisivo para voce, a escola precisa publicar esse ponto de forma oficial ou ampliar a base documental.'
        )
    if query_hints:
        return (
            'Ainda nao encontrei evidencia publica suficiente para responder isso com seguranca do jeito que a pergunta foi feita. '
            'Se quiser, eu posso tentar por outro caminho, como o setor responsavel, o canal oficial ou a politica institucional relacionada.'
        )
    return (
        'Ainda nao encontrei uma resposta suficientemente suportada na base publica. '
        'Tente reformular a pergunta com termos como matricula, calendario, secretaria ou atendimento.'
    )


def _extract_school_reference_candidate(message: str) -> str | None:
    normalized = _normalize_text(message)
    stop_tokens = {
        'setor',
        'departamento',
        'area',
        'área',
        'fila',
        'na',
        'no',
        'em',
        'quinta',
        'sexta',
        'segunda',
        'terca',
        'terça',
        'quarta',
        'sabado',
        'sábado',
        'domingo',
        'manha',
        'manhã',
        'tarde',
        'noite',
        'diretor',
        'diretora',
        'secretaria',
        'secretariao',
        'humano',
        'atendimento',
        'financeiro',
        'matricula',
        'matrícula',
        'coordenacao',
        'coordenação',
        'orientacao',
        'orientação',
        'professor',
        'professora',
        'oferece',
        'tem',
        'fica',
        'abre',
        'fecha',
        'aceita',
        'publica',
        'publico',
        'funciona',
        'site',
        'instagram',
        'telefone',
        'whatsapp',
        'email',
    }
    patterns = (
        r'\b(?:colegio|colégio|escola)\s+([a-z0-9]+(?:\s+[a-z0-9]+){0,3})\b',
        r'\b(?:e|é)\s+do\s+([a-z0-9]+(?:\s+[a-z0-9]+){0,3})\b',
        r'\b(?:nao|não)\s+e\s+do\s+([a-z0-9]+(?:\s+[a-z0-9]+){0,3})\b',
        r'\bfalar com\s+(?:o|a)\s+([a-z0-9]+(?:\s+[a-z0-9]+){0,3})\b',
    )
    for pattern in patterns:
        match = re.search(pattern, normalized)
        if not match:
            continue
        candidate = match.group(1).strip()
        candidate_tokens = [token for token in candidate.split() if token not in {'o', 'a', 'do', 'da', 'de'}]
        if not candidate_tokens:
            continue
        if candidate_tokens[0] in stop_tokens:
            continue
        if len(candidate_tokens) == 1 and candidate_tokens[0] in stop_tokens:
            continue
        return ' '.join(candidate_tokens)
    return None


def _school_identity_tokens(profile: dict[str, Any] | None) -> set[str]:
    school_name = _normalize_text(str((profile or {}).get('school_name', '') or ''))
    return {
        token
        for token in school_name.split()
        if token and token not in {'colegio', 'colégio', 'escola', 'do', 'da', 'de'}
    }


def _foreign_school_reference(
    *,
    message: str,
    school_profile: dict[str, Any] | None,
    conversation_context: dict[str, Any] | None,
) -> str | None:
    if _is_comparative_query(message):
        return None
    normalized = _normalize_text(message)
    recent_focus = _recent_trace_focus(conversation_context) or {}
    recent_active_task = str(recent_focus.get('active_task', '') or '').strip()
    recent_student_name = str(
        recent_focus.get('academic_student_name')
        or recent_focus.get('finance_student_name')
        or recent_focus.get('student_name')
        or ''
    ).strip()
    school_tokens = _school_identity_tokens(school_profile)
    direct_reference = _extract_school_reference_candidate(message)
    if direct_reference:
        direct_reference_tokens = set(direct_reference.split())
        support_like_tokens = {
            'setor',
            'financeiro',
            'secretaria',
            'direcao',
            'direção',
            'diretoria',
            'coordenacao',
            'coordenação',
            'matricula',
            'matrícula',
            'atendimento',
            'humano',
            'fila',
        }
        if direct_reference_tokens & support_like_tokens:
            return None
        if (
            normalized.startswith('e do ')
            or normalized.startswith('e da ')
            or normalized.startswith('do ')
            or normalized.startswith('da ')
        ) and (
            recent_active_task.startswith(('academic:', 'finance:', 'admin:'))
            or bool(recent_student_name)
        ):
            return None
        reference_tokens = set(direct_reference.split())
        if not (reference_tokens & school_tokens):
            return direct_reference
    if not any(
        _message_matches_term(normalized, term)
        for term in {'falar com', 'me passa', 'passa pro', 'passa para', 'diretor', 'diretora', 'contato'}
    ):
        return None
    for sender_type, content in reversed(_recent_message_lines(conversation_context)):
        if sender_type != 'user':
            continue
        historical_reference = _extract_school_reference_candidate(content)
        if not historical_reference:
            continue
        reference_tokens = set(historical_reference.split())
        if reference_tokens & school_tokens:
            continue
        return historical_reference
    return None


def _compose_foreign_school_redirect(
    *,
    school_profile: dict[str, Any] | None,
    foreign_school_reference: str,
) -> str:
    school_name = str((school_profile or {}).get('school_name', '') or 'Colégio Horizonte').strip()
    foreign_school_name = foreign_school_reference.title()
    return (
        f'Aqui e o {school_name}. Se voce esta procurando o {foreign_school_name}, '
        'eu nao tenho acesso ao atendimento dessa outra instituicao. '
        f'Se quiser, sigo te ajudando com o {school_name} por aqui.'
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
        recent_tool_calls=[item for item in payload.get('recent_tool_calls', []) if isinstance(item, dict)],
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


def _serialize_slot_memory(slot_memory: ConversationSlotMemory) -> dict[str, Any]:
    return {
        key: value
        for key, value in {
            'focus_kind': slot_memory.focus_kind,
            'protocol_code': slot_memory.protocol_code,
            'contact_subject': slot_memory.contact_subject,
            'feature_key': slot_memory.feature_key,
            'active_task': slot_memory.active_task,
            'active_entity': slot_memory.active_entity,
            'pending_question_type': slot_memory.pending_question_type,
            'pending_disambiguation': slot_memory.pending_disambiguation,
            'public_entity': slot_memory.public_entity,
            'public_attribute': slot_memory.public_attribute,
            'requested_channel': slot_memory.requested_channel,
            'time_reference': slot_memory.time_reference,
            'academic_student_name': slot_memory.academic_student_name,
            'academic_focus_kind': slot_memory.academic_focus_kind,
            'academic_attribute': slot_memory.academic_attribute,
            'admin_attribute': slot_memory.admin_attribute,
            'finance_student_name': slot_memory.finance_student_name,
            'finance_status_filter': slot_memory.finance_status_filter,
            'finance_attribute': slot_memory.finance_attribute,
            'finance_action': slot_memory.finance_action,
        }.items()
        if value
    }


async def _persist_operational_trace(
    *,
    settings: Any,
    conversation_external_id: str | None,
    channel: str,
    engine_name: str,
    engine_mode: str,
    actor: dict[str, Any] | None,
    preview: Any,
    school_profile: dict[str, Any] | None,
    conversation_context: dict[str, Any] | None,
    public_plan: PublicInstitutionPlan | None,
    request_message: str,
    message_text: str,
    citations_count: int,
    suggested_reply_count: int,
    visual_asset_count: int,
    answer_verifier_valid: bool,
    answer_verifier_reason: str | None,
    answer_verifier_fallback_used: bool,
    deterministic_fallback_available: bool,
    answer_verifier_judge_used: bool,
    langgraph_trace_metadata: dict[str, Any] | None = None,
    engine_trace_metadata: dict[str, Any] | None = None,
) -> None:
    if not conversation_external_id:
        return

    actor_user_id = actor.get('user_id') if isinstance(actor, dict) else None
    slot_memory = _build_conversation_slot_memory(
        actor=actor,
        profile=school_profile,
        conversation_context=conversation_context,
        request_message=request_message,
        public_plan=public_plan,
        preview=preview,
    )
    trace_request_payload: dict[str, Any] = {
        'engine_name': engine_name,
        'engine_mode': engine_mode,
        'mode': preview.mode.value,
        'domain': preview.classification.domain.value,
        'access_tier': preview.classification.access_tier.value,
        'selected_tools': list(preview.selected_tools),
        'graph_path': list(preview.graph_path),
        'reason': preview.reason,
        'slot_memory': _serialize_slot_memory(slot_memory),
    }
    if public_plan is not None:
        trace_request_payload['public_plan'] = {
            'conversation_act': public_plan.conversation_act,
            'secondary_acts': list(public_plan.secondary_acts),
            'semantic_source': public_plan.semantic_source,
            'use_conversation_context': public_plan.use_conversation_context,
            'fetch_profile': public_plan.fetch_profile,
            'focus_hint': public_plan.focus_hint,
            'requested_attribute': public_plan.requested_attribute,
            'requested_channel': public_plan.requested_channel,
            'required_tools': list(public_plan.required_tools),
        }
    if isinstance(langgraph_trace_metadata, dict) and langgraph_trace_metadata:
        langgraph_trace_sections = build_langgraph_trace_sections(
            langgraph_trace_metadata,
            graph_path=list(getattr(preview, 'graph_path', []) or []),
        )
        if langgraph_trace_sections.get('request'):
            trace_request_payload['langgraph'] = langgraph_trace_sections['request']
    if engine_name == 'crewai':
        crewai_trace_sections = build_crewai_trace_sections(engine_trace_metadata)
        if crewai_trace_sections.get('request'):
            trace_request_payload['crewai'] = crewai_trace_sections['request']

    trace_response_payload = {
        'message_length': len(message_text),
        'citations_count': citations_count,
        'suggested_reply_count': suggested_reply_count,
        'visual_asset_count': visual_asset_count,
        'answer_verifier_valid': answer_verifier_valid,
        'answer_verifier_reason': answer_verifier_reason or '',
        'answer_verifier_fallback_used': answer_verifier_fallback_used,
        'deterministic_fallback_available': deterministic_fallback_available,
        'answer_verifier_judge_used': answer_verifier_judge_used,
    }
    if isinstance(langgraph_trace_metadata, dict) and langgraph_trace_metadata:
        langgraph_trace_sections = build_langgraph_trace_sections(
            langgraph_trace_metadata,
            graph_path=list(getattr(preview, 'graph_path', []) or []),
        )
        if langgraph_trace_sections.get('response'):
            trace_response_payload['langgraph'] = langgraph_trace_sections['response']
    if engine_name == 'crewai':
        crewai_trace_sections = build_crewai_trace_sections(engine_trace_metadata)
        if crewai_trace_sections.get('response'):
            trace_response_payload['crewai'] = crewai_trace_sections['response']
    await _api_core_post(
        settings=settings,
        path='/v1/internal/conversations/tool-calls',
        payload={
            'channel': channel,
            'conversation_external_id': conversation_external_id,
            'actor_user_id': actor_user_id,
            'tool_calls': [
                {
                    'tool_name': 'orchestration.trace',
                    'status': 'ok',
                    'request_payload': trace_request_payload,
                    'response_payload': trace_response_payload,
                }
            ],
        },
    )


def _extract_langgraph_snapshot_metadata(snapshot: Any) -> dict[str, Any]:
    values = dict(getattr(snapshot, 'values', {}) or {})
    config = getattr(snapshot, 'config', None)
    parent_config = getattr(snapshot, 'parent_config', None)
    metadata = getattr(snapshot, 'metadata', None)
    configurable = config.get('configurable', {}) if isinstance(config, dict) else {}
    parent_configurable = parent_config.get('configurable', {}) if isinstance(parent_config, dict) else {}
    next_nodes = [str(item) for item in (getattr(snapshot, 'next', None) or ())]
    task_names = [str(getattr(task, 'name', '')) for task in (getattr(snapshot, 'tasks', None) or ()) if str(getattr(task, 'name', '')).strip()]
    top_level_interrupts = list(getattr(snapshot, 'interrupts', None) or ())
    task_interrupt_count = sum(len(getattr(task, 'interrupts', None) or ()) for task in (getattr(snapshot, 'tasks', None) or ()))
    payload: dict[str, Any] = {
        'state_available': True,
        'created_at': str(getattr(snapshot, 'created_at', '') or ''),
        'next_nodes': next_nodes,
        'task_names': task_names,
        'top_level_interrupt_count': len(top_level_interrupts),
        'task_interrupt_count': task_interrupt_count,
        'has_pending_interrupt': bool(top_level_interrupts or task_interrupt_count),
        'state_route': values.get('route'),
        'state_slice_name': values.get('slice_name'),
        'hitl_status': values.get('hitl_status'),
    }
    checkpoint_id = configurable.get('checkpoint_id') or parent_configurable.get('checkpoint_id')
    checkpoint_ns = configurable.get('checkpoint_ns') or parent_configurable.get('checkpoint_ns')
    if checkpoint_id:
        payload['checkpoint_id'] = str(checkpoint_id)
    if checkpoint_ns:
        payload['checkpoint_ns'] = str(checkpoint_ns)
    if isinstance(metadata, dict) and metadata:
        payload['snapshot_metadata'] = {
            str(key): value
            for key, value in metadata.items()
            if isinstance(value, (str, int, float, bool)) or value is None
        }
    return payload


def _capture_langgraph_trace_metadata(
    *,
    graph: Any,
    thread_id: str | None,
    langgraph_artifacts: Any,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        'thread_id': thread_id or '',
        'checkpointer_enabled': bool(getattr(langgraph_artifacts, 'checkpointer_enabled', False)),
        'checkpointer_backend': str(getattr(langgraph_artifacts, 'checkpointer_backend', '') or ''),
        'state_available': False,
    }
    if not thread_id or not getattr(langgraph_artifacts, 'checkpointer_enabled', False):
        return payload
    try:
        snapshot = get_orchestration_state_snapshot(graph=graph, thread_id=thread_id, subgraphs=True)
    except Exception as exc:
        payload['state_fetch_error'] = exc.__class__.__name__
        payload['state_fetch_error_message'] = str(exc)
        return payload
    payload.update(_extract_langgraph_snapshot_metadata(snapshot))
    return payload


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


async def _fetch_public_assistant_capabilities(*, settings: Any) -> dict[str, Any] | None:
    payload, status_code = await _api_core_get(
        settings=settings,
        path='/v1/public/assistant-capabilities',
    )
    if status_code != 200 or payload is None:
        return None
    capabilities = payload.get('capabilities')
    return capabilities if isinstance(capabilities, dict) else None


async def _fetch_public_org_directory(*, settings: Any) -> dict[str, Any] | None:
    payload, status_code = await _api_core_get(
        settings=settings,
        path='/v1/public/org-directory',
    )
    if status_code != 200 or payload is None:
        return None
    directory = payload.get('directory')
    return directory if isinstance(directory, dict) else None


async def _fetch_public_service_directory(*, settings: Any) -> dict[str, Any] | None:
    payload, status_code = await _api_core_get(
        settings=settings,
        path='/v1/public/service-directory',
    )
    if status_code != 200 or payload is None:
        return None
    directory = payload.get('directory')
    return directory if isinstance(directory, dict) else None


async def _fetch_public_timeline(*, settings: Any) -> dict[str, Any] | None:
    payload, status_code = await _api_core_get(
        settings=settings,
        path='/v1/public/timeline',
    )
    if status_code != 200 or payload is None:
        return None
    timeline = payload.get('timeline')
    return timeline if isinstance(timeline, dict) else None


async def _fetch_public_calendar_events(*, settings: Any) -> list[dict[str, Any]]:
    today = date.today()
    payload, status_code = await _api_core_get(
        settings=settings,
        path='/v1/calendar/public',
        params={
            'date_from': today.isoformat(),
            'date_to': (today + timedelta(days=180)).isoformat(),
            'limit': 12,
        },
    )
    if status_code != 200 or payload is None:
        return []
    events = payload.get('events')
    if not isinstance(events, list):
        return []
    return [item for item in events if isinstance(item, dict)]


async def _fetch_internal_workflow_status(
    *,
    settings: Any,
    conversation_external_id: str,
    protocol_code: str | None = None,
    workflow_kind: str | None = None,
) -> dict[str, Any] | None:
    params: dict[str, object] = {
        'conversation_external_id': conversation_external_id,
        'channel': 'telegram',
    }
    if protocol_code:
        params['protocol_code'] = protocol_code
    if workflow_kind:
        params['workflow_kind'] = workflow_kind

    payload, status_code = await _api_core_get(
        settings=settings,
        path='/v1/internal/workflows/status',
        params=params,
    )
    if status_code != 200 or payload is None:
        return None
    return payload if isinstance(payload, dict) else None


def _matches_public_contact_rule(message: str) -> bool:
    normalized = _normalize_text(message)
    return any(_message_matches_term(normalized, term) for term in PUBLIC_CONTACT_TERMS)


def _matches_public_location_rule(message: str) -> bool:
    normalized = _normalize_text(message)
    return any(_message_matches_term(normalized, term) for term in PUBLIC_LOCATION_TERMS)


def _matches_public_confessional_rule(message: str) -> bool:
    normalized = _normalize_text(message)
    return any(_message_matches_term(normalized, term) for term in PUBLIC_CONFESSIONAL_TERMS)


def _matches_public_kpi_rule(message: str) -> bool:
    normalized = _normalize_text(message)
    return any(_message_matches_term(normalized, term) for term in PUBLIC_KPI_TERMS)


def _matches_public_highlight_rule(message: str) -> bool:
    normalized = _normalize_text(message)
    return any(_message_matches_term(normalized, term) for term in PUBLIC_HIGHLIGHT_TERMS)


def _matches_public_visit_rule(message: str) -> bool:
    normalized = _normalize_text(message)
    return any(_message_matches_term(normalized, term) for term in PUBLIC_VISIT_TERMS)


def _matches_public_pricing_rule(message: str) -> bool:
    normalized = _normalize_text(message)
    return any(_message_matches_term(normalized, term) for term in PUBLIC_PRICING_TERMS)


def _matches_public_schedule_rule(message: str) -> bool:
    normalized = _normalize_text(message)
    return any(_message_matches_term(normalized, term) for term in PUBLIC_SCHEDULE_TERMS)


def _matches_public_feature_rule(message: str) -> bool:
    return _is_public_feature_query(message)


def _matches_public_segment_rule(message: str) -> bool:
    normalized = _normalize_text(message)
    return any(_message_matches_term(normalized, term) for term in PUBLIC_SEGMENT_TERMS)


PUBLIC_ACT_RULES: tuple[PublicActRule, ...] = (
    PublicActRule('greeting', _is_greeting_only, ('list_assistant_capabilities',), False),
    PublicActRule('utility_date', _is_public_date_query, (), False),
    PublicActRule('auth_guidance', _is_auth_guidance_query, (), False),
    PublicActRule('access_scope', _is_access_scope_query, ('list_assistant_capabilities',), False),
    PublicActRule('service_routing', _is_service_routing_query, ('get_service_directory',), False),
    PublicActRule('assistant_identity', _is_assistant_identity_query, ('get_org_directory',), False),
    PublicActRule('capabilities', _is_capability_query, ('list_assistant_capabilities',), False),
    PublicActRule('document_submission', _is_public_document_submission_query),
    PublicActRule('careers', _is_public_careers_query, ('get_service_directory',)),
    PublicActRule('teacher_directory', _is_public_teacher_identity_query),
    PublicActRule('leadership', _is_leadership_specific_query, ('get_org_directory',), False),
    PublicActRule('web_presence', _is_public_web_query),
    PublicActRule('social_presence', _is_public_social_query),
    PublicActRule('contacts', _matches_public_contact_rule, ('get_org_directory',)),
    PublicActRule('comparative', _is_comparative_query),
    PublicActRule('operating_hours', _is_public_operating_hours_query),
    PublicActRule('timeline', _is_public_timeline_query, ('get_public_timeline',), False),
    PublicActRule('calendar_events', _is_public_calendar_event_query, ('get_public_calendar_events',), False),
    PublicActRule('location', _matches_public_location_rule),
    PublicActRule('confessional', _matches_public_confessional_rule),
    PublicActRule('curriculum', _is_public_curriculum_query),
    PublicActRule('kpi', _matches_public_kpi_rule),
    PublicActRule('highlight', _matches_public_highlight_rule),
    PublicActRule('visit', _matches_public_visit_rule),
    PublicActRule('pricing', _matches_public_pricing_rule),
    PublicActRule('schedule', _matches_public_schedule_rule),
    PublicActRule('features', _matches_public_feature_rule),
    PublicActRule('segments', _matches_public_segment_rule),
    PublicActRule('school_name', _is_public_school_name_query),
)


def _match_public_act_rule(message: str) -> PublicActRule | None:
    for rule in PUBLIC_ACT_RULES:
        try:
            if rule.matcher(message):
                return rule
        except Exception:
            continue
    return None


def _matched_public_act_rules(
    message: str,
    *,
    conversation_context: dict[str, Any] | None = None,
) -> tuple[PublicActRule, ...]:
    matched: list[PublicActRule] = []
    for rule in PUBLIC_ACT_RULES:
        try:
            if rule.matcher(message):
                matched.append(rule)
        except Exception:
            continue
    normalized = _normalize_text(message)
    recent_feature_key = _recent_public_feature_key(conversation_context)
    if (
        recent_feature_key
        and _is_follow_up_query(message)
        and (
            any(_message_matches_term(normalized, term) for term in PUBLIC_SCHEDULE_TERMS)
            or bool(_requested_contact_channel(message))
            or _message_matches_term(normalized, 'nome')
        )
    ):
        feature_rule = next((rule for rule in PUBLIC_ACT_RULES if rule.name == 'features'), None)
        if feature_rule is not None and all(rule.name != 'features' for rule in matched):
            matched.append(feature_rule)
    recent_focus = _recent_trace_focus(conversation_context)
    if (
        isinstance(recent_focus, dict)
        and str(recent_focus.get('active_task', '')).strip() == 'public:features'
        and _is_follow_up_query(message)
    ):
        feature_rule = next((rule for rule in PUBLIC_ACT_RULES if rule.name == 'features'), None)
        if feature_rule is not None and all(rule.name != 'features' for rule in matched):
            matched.append(feature_rule)
    return tuple(matched)


def _has_public_multi_intent_signal(message: str) -> bool:
    normalized = _normalize_text(message)
    collapsed = re.sub(r'\s+', ' ', normalized).strip()
    collapsed_without_leading_connector = re.sub(r'^(e|tambem|tambem,|alem disso)\s+', '', collapsed).strip()
    if re.match(r'^(quando|qual|quais|quem|onde|como|o que|que|por que)\s+e\b', collapsed):
        return False
    if re.match(r'^(quando|qual|quais|quem|onde|como|o que|que|por que)\s+e\b', collapsed_without_leading_connector):
        return False
    if collapsed.startswith('e ') and ' e ' not in collapsed_without_leading_connector:
        return False
    return any(
        marker in collapsed_without_leading_connector
        for marker in (
            ' e ',
            ', e ',
            ' alem de ',
            ' além de ',
            ' tambem ',
            ' também ',
        )
    )


def _prioritize_public_act_rules(
    message: str,
    matched_rules: tuple[PublicActRule, ...],
) -> tuple[PublicActRule, ...]:
    if len(matched_rules) < 2:
        return matched_rules

    feature_requested = bool(_requested_public_features(message))
    channel_requested = _requested_contact_channel(message) is not None
    base_priority = {
        'greeting': 100,
        'utility_date': 100,
        'auth_guidance': 95,
        'access_scope': 94,
        'assistant_identity': 95,
        'service_routing': 95,
        'capabilities': 90,
        'comparative': 89,
        'document_submission': 88,
        'careers': 88,
        'teacher_directory': 88,
        'leadership': 86,
        'contacts': 84,
        'social_presence': 83,
        'web_presence': 82,
        'location': 82,
        'curriculum': 82,
        'calendar_events': 82,
        'timeline': 81,
        'features': 80,
        'operating_hours': 70,
        'schedule': 65,
        'pricing': 64,
        'visit': 64,
        'kpi': 62,
        'highlight': 62,
        'segments': 58,
        'school_name': 56,
        'confessional': 54,
    }

    ranked: list[tuple[int, int, PublicActRule]] = []
    for index, rule in enumerate(matched_rules):
        score = base_priority.get(rule.name, 40)
        if rule.name == 'features' and feature_requested:
            score += 18
        if rule.name == 'schedule' and feature_requested:
            score -= 18
        if rule.name == 'contacts' and channel_requested:
            score += 8
        ranked.append((-score, index, rule))

    ranked.sort()
    return tuple(rule for _score, _index, rule in ranked)


PUBLIC_SEMANTIC_ACTS = {
    'greeting',
    'auth_guidance',
    'access_scope',
    'assistant_identity',
    'capabilities',
    'service_routing',
    'document_submission',
    'careers',
    'teacher_directory',
    'leadership',
    'contacts',
    'web_presence',
    'social_presence',
    'comparative',
    'pricing',
    'schedule',
    'operating_hours',
    'curriculum',
    'features',
    'highlight',
    'visit',
    'location',
    'confessional',
    'kpi',
    'segments',
    'school_name',
    'timeline',
    'calendar_events',
    'utility_date',
    'canonical_fact',
}
PUBLIC_SEMANTIC_TOOLS = {
    'get_public_school_profile',
    'list_assistant_capabilities',
    'get_org_directory',
    'get_service_directory',
    'get_public_timeline',
    'get_public_calendar_events',
}


def _should_run_public_semantic_resolver(
    *,
    message: str,
    preview: Any,
    conversation_context: dict[str, Any] | None,
) -> bool:
    if preview.classification.domain not in {QueryDomain.institution, QueryDomain.calendar}:
        return False
    if preview.classification.access_tier is not AccessTier.public:
        return False
    if preview.mode not in {
        OrchestrationMode.structured_tool,
        OrchestrationMode.hybrid_retrieval,
        OrchestrationMode.clarify,
    }:
        return False
    return True


def _is_public_semantic_rescue_candidate(preview: Any) -> bool:
    if preview.classification.domain not in {QueryDomain.institution, QueryDomain.calendar}:
        return False
    if preview.classification.access_tier is not AccessTier.public:
        return False
    return preview.mode in {OrchestrationMode.hybrid_retrieval, OrchestrationMode.clarify}


def _should_apply_public_semantic_rescue(
    *,
    preview: Any,
    plan: PublicInstitutionPlan | None,
) -> bool:
    if plan is None:
        return False
    if plan.semantic_source != 'llm':
        return False
    if plan.conversation_act not in PUBLIC_SEMANTIC_RESCUE_ACTS:
        return False
    if preview.mode is OrchestrationMode.clarify:
        return True
    if preview.mode is OrchestrationMode.hybrid_retrieval:
        return True
    return False


def _recent_student_disambiguation_domain(
    conversation_context: dict[str, Any] | None,
) -> QueryDomain | None:
    if not isinstance(conversation_context, dict):
        return None
    recent_assistant = _extract_recent_assistant_message(conversation_context.get('recent_messages', []))
    if 'mais de um aluno vinculado' not in _normalize_text(recent_assistant or ''):
        return None
    recent_focus = _recent_trace_focus(conversation_context)
    if not isinstance(recent_focus, dict):
        return None
    active_task = str(recent_focus.get('active_task', '') or '').strip()
    if active_task.startswith('academic:'):
        return QueryDomain.academic
    if active_task.startswith('finance:'):
        return QueryDomain.finance
    return None


def _apply_student_disambiguation_rescue(
    *,
    preview: Any,
    actor: dict[str, Any] | None,
    message: str,
    conversation_context: dict[str, Any] | None,
) -> bool:
    if preview.mode is not OrchestrationMode.clarify:
        return False
    if not isinstance(actor, dict):
        return False
    rescued_domain = _recent_student_disambiguation_domain(conversation_context)
    if rescued_domain is None:
        return False
    capability = 'finance' if rescued_domain is QueryDomain.finance else 'academic'
    matched_students = _matching_students_in_text(
        _eligible_students(actor, capability=capability),
        message,
    )
    if len(matched_students) != 1:
        return False

    preview.mode = OrchestrationMode.structured_tool
    preview.classification = IntentClassification(
        domain=rescued_domain,
        access_tier=AccessTier.sensitive if rescued_domain is QueryDomain.finance else AccessTier.authenticated,
        confidence=0.87,
        reason='follow-up curto resolveu a desambiguacao do aluno com base no contexto recente',
    )
    if rescued_domain is QueryDomain.academic:
        preview.selected_tools = [
            'get_student_academic_summary',
            'get_student_attendance',
            'get_student_grades',
            'get_student_upcoming_assessments',
            'get_student_attendance_timeline',
        ]
        preview.output_contract = 'dados academicos autorizados, auditaveis e minimizados'
    else:
        preview.selected_tools = ['get_financial_summary']
        preview.output_contract = 'dados financeiros autorizados, auditaveis e com trilha reforcada'
    preview.retrieval_backend = RetrievalBackend.none
    preview.citations_required = False
    preview.needs_authentication = False
    preview.reason = 'o usuario respondeu a desambiguacao do aluno e o fluxo protegido pode continuar'
    preview.graph_path = [*preview.graph_path, 'student_disambiguation_rescue']
    if rescued_domain is QueryDomain.finance and 'sensitive_data_path' not in preview.risk_flags:
        preview.risk_flags = [*preview.risk_flags, 'sensitive_data_path']
    return True


def _normalize_public_semantic_plan(payload: dict[str, Any] | None) -> PublicInstitutionPlan | None:
    if not isinstance(payload, dict):
        return None
    conversation_act = str(payload.get('conversation_act', '')).strip()
    if conversation_act not in PUBLIC_SEMANTIC_ACTS:
        return None
    required_tools_raw = payload.get('required_tools', [])
    required_tools = tuple(
        tool_name
        for tool_name in required_tools_raw
        if isinstance(tool_name, str) and tool_name in PUBLIC_SEMANTIC_TOOLS
    ) if isinstance(required_tools_raw, list) else ()
    secondary_acts_raw = payload.get('secondary_acts', [])
    secondary_acts = tuple(
        act
        for act in secondary_acts_raw
        if isinstance(act, str) and act in PUBLIC_SEMANTIC_ACTS and act != conversation_act
    ) if isinstance(secondary_acts_raw, list) else ()
    requested_attribute = str(payload.get('requested_attribute', '')).strip() or None
    if requested_attribute == 'none':
        requested_attribute = None
    requested_channel = str(payload.get('requested_channel', '')).strip() or None
    if requested_channel == 'none':
        requested_channel = None
    focus_hint = str(payload.get('focus_hint', '')).strip() or None
    fetch_profile = 'get_public_school_profile' in required_tools or conversation_act in {
        'web_presence',
        'social_presence',
        'comparative',
        'pricing',
        'schedule',
        'operating_hours',
        'curriculum',
        'features',
        'highlight',
        'visit',
        'location',
        'confessional',
        'kpi',
        'document_submission',
        'careers',
        'teacher_directory',
        'segments',
        'school_name',
        'calendar_events',
        'canonical_fact',
    }
    use_conversation_context = bool(payload.get('use_conversation_context'))
    return PublicInstitutionPlan(
        conversation_act=conversation_act,
        required_tools=required_tools,
        fetch_profile=fetch_profile,
        secondary_acts=secondary_acts,
        requested_attribute=requested_attribute,
        requested_channel=requested_channel,
        focus_hint=focus_hint,
        semantic_source='llm',
        use_conversation_context=use_conversation_context,
    )


def _apply_public_semantic_plan_overrides(
    message: str,
    semantic_plan: PublicInstitutionPlan | None,
) -> PublicInstitutionPlan | None:
    if semantic_plan is None:
        return None
    if _is_public_timeline_query(message) and semantic_plan.conversation_act != 'timeline':
        return replace(semantic_plan, conversation_act='timeline')
    if _is_access_scope_query(message) and semantic_plan.conversation_act != 'access_scope':
        return replace(semantic_plan, conversation_act='access_scope')
    if _is_assistant_identity_query(message) and semantic_plan.conversation_act != 'assistant_identity':
        return replace(semantic_plan, conversation_act='assistant_identity')
    if _is_public_enrichment_query(message) and semantic_plan.conversation_act != 'features':
        return replace(semantic_plan, conversation_act='features')
    if _is_public_scholarship_query(message) and semantic_plan.conversation_act != 'pricing':
        return replace(semantic_plan, conversation_act='pricing')
    requested_attributes = set(_requested_public_attributes(message))
    primary_entity = _primary_public_entity_hint(message)
    if (
        semantic_plan.conversation_act == 'operating_hours'
        and 'name' in requested_attributes
        and primary_entity not in {None, 'escola'}
        and 'features' not in semantic_plan.secondary_acts
    ):
        return replace(semantic_plan, secondary_acts=(*semantic_plan.secondary_acts[:1], 'features'))
    return semantic_plan


def _normalize_public_plan_for_message(
    *,
    message: str,
    conversation_context: dict[str, Any] | None,
    conversation_act: str,
    secondary_acts: tuple[str, ...],
    required_tools: list[str],
    fetch_profile: bool,
) -> tuple[str, tuple[str, ...], list[str], bool]:
    requested_attributes = set(_requested_public_attributes(message))
    primary_entity = _primary_public_entity_hint(message, conversation_context)
    normalized_act = conversation_act
    normalized_secondary = [
        act
        for act in secondary_acts
        if isinstance(act, str) and act and act != conversation_act
    ]
    normalized_tools = [tool_name for tool_name in required_tools if isinstance(tool_name, str) and tool_name]
    normalized_fetch_profile = fetch_profile

    def ensure_tool(tool_name: str) -> None:
        if tool_name not in normalized_tools:
            normalized_tools.append(tool_name)

    if _is_public_document_submission_query(message):
        normalized_act = 'document_submission'
        ensure_tool('get_public_school_profile')
        normalized_fetch_profile = True
    elif (
        _is_follow_up_query(message)
        and isinstance(_recent_trace_focus(conversation_context), dict)
        and str((_recent_trace_focus(conversation_context) or {}).get('active_task', '')).strip() == 'public:document_submission'
    ):
        normalized_act = 'document_submission'
        ensure_tool('get_public_school_profile')
        normalized_fetch_profile = True
    elif _matches_public_contact_rule(message) or _requested_contact_channel(message) is not None:
        normalized_act = 'contacts'
        ensure_tool('get_public_school_profile')
        normalized_fetch_profile = True
    elif _is_public_timeline_query(message):
        normalized_act = 'timeline'
        normalized_secondary = [act for act in normalized_secondary if act != 'calendar_events']
        normalized_tools = [tool_name for tool_name in normalized_tools if tool_name != 'get_public_calendar_events']
        ensure_tool('get_public_timeline')
        normalized_fetch_profile = True
    elif _is_public_calendar_event_query(message):
        normalized_act = 'calendar_events'
        normalized_tools = [tool_name for tool_name in normalized_tools if tool_name != 'get_public_timeline']
        ensure_tool('get_public_calendar_events')
        normalized_fetch_profile = True

    if (
        _is_follow_up_query(message)
        and requested_attributes == {'name'}
        and primary_entity not in {None, 'escola'}
        and normalized_act not in {'contacts', 'leadership', 'teacher_directory'}
    ):
        normalized_act = 'features'
        ensure_tool('get_public_school_profile')
        normalized_fetch_profile = True
    elif (
        normalized_act == 'operating_hours'
        and 'name' in requested_attributes
        and primary_entity not in {None, 'escola'}
        and 'features' not in normalized_secondary
    ):
        normalized_secondary = ['features', *normalized_secondary]

    normalized_secondary = [act for act in normalized_secondary if act != normalized_act][:2]
    return normalized_act, tuple(normalized_secondary), normalized_tools, normalized_fetch_profile


async def _resolve_public_institution_plan(
    *,
    settings: Any,
    message: str,
    preview: Any,
    conversation_context: dict[str, Any] | None,
    school_profile: dict[str, Any] | None,
) -> PublicInstitutionPlan:
    semantic_plan: PublicInstitutionPlan | None = None
    if _should_run_public_semantic_resolver(
        message=message,
        preview=preview,
        conversation_context=conversation_context,
    ):
        payload: dict[str, Any] | None = None
        try:
            payload = await resolve_public_semantic_with_provider(
                settings=settings,
                request_message=message,
                conversation_context=conversation_context,
                school_profile=school_profile,
                selected_tools=list(preview.selected_tools),
            )
        except Exception:
            payload = None
        semantic_plan = _normalize_public_semantic_plan(payload)
        semantic_plan = _apply_public_semantic_plan_overrides(message, semantic_plan)
    return _build_public_institution_plan(
        message,
        list(preview.selected_tools),
        semantic_plan=semantic_plan,
        conversation_context=conversation_context,
        school_profile=school_profile,
    )


def _build_public_institution_plan(
    message: str,
    selected_tools: list[str],
    semantic_plan: PublicInstitutionPlan | None = None,
    *,
    conversation_context: dict[str, Any] | None = None,
    school_profile: dict[str, Any] | None = None,
) -> PublicInstitutionPlan:
    required_tools: list[str] = []
    secondary_acts: tuple[str, ...] = semantic_plan.secondary_acts if semantic_plan else ()

    def add(tool_name: str) -> None:
        if tool_name not in required_tools:
            required_tools.append(tool_name)

    conversation_act = semantic_plan.conversation_act if semantic_plan else 'canonical_fact'
    fetch_profile = semantic_plan.fetch_profile if semantic_plan else True
    if (
        _is_leadership_specific_query(message)
        and conversation_act == 'contacts'
        and (
            (semantic_plan and semantic_plan.requested_attribute in {'name', 'age', 'whatsapp', 'phone', 'email', 'contact'})
            or _requested_public_attribute(message) in {'name', 'age', 'whatsapp', 'phone', 'email', 'contact'}
        )
    ):
        conversation_act = 'leadership'

    if semantic_plan is not None:
        for tool_name in semantic_plan.required_tools:
            add(tool_name)
        if not secondary_acts and _has_public_multi_intent_signal(message):
            matched_rules = _prioritize_public_act_rules(
                message,
                _matched_public_act_rules(message, conversation_context=conversation_context),
            )
            secondary_acts = tuple(
                rule.name
                for rule in matched_rules[:3]
                if rule.name != conversation_act
            )
    else:
        matched_rules = _prioritize_public_act_rules(
            message,
            _matched_public_act_rules(message, conversation_context=conversation_context),
        )
        if matched_rules:
            primary_rule = matched_rules[0]
            conversation_act = primary_rule.name
            fetch_profile = primary_rule.fetch_profile
            if _has_public_multi_intent_signal(message):
                secondary_acts = tuple(
                    rule.name for rule in matched_rules[1:3] if rule.name != conversation_act
                )
            for rule in matched_rules[:3]:
                for tool_name in rule.required_tools:
                    add(tool_name)
        else:
            matched_rule = _match_public_act_rule(message)
            if matched_rule is not None:
                conversation_act = matched_rule.name
                fetch_profile = matched_rule.fetch_profile
                for tool_name in matched_rule.required_tools:
                    add(tool_name)

    for tool_name in selected_tools:
        if tool_name == 'get_public_school_profile':
            continue
        add(tool_name)

    conversation_act, secondary_acts, required_tools, fetch_profile = _normalize_public_plan_for_message(
        message=message,
        conversation_context=conversation_context,
        conversation_act=conversation_act,
        secondary_acts=secondary_acts,
        required_tools=required_tools,
        fetch_profile=fetch_profile,
    )

    if conversation_act == 'assistant_identity':
        add('get_service_directory')

    if isinstance(school_profile, dict) and _requested_contact_channel(message):
        preferred_labels = _preferred_contact_labels_from_context(
            school_profile,
            message,
            conversation_context,
        )
        if _contact_is_general_school_query(message):
            preferred_labels = []
        if any(label in {'Orientacao educacional', 'Financeiro', 'Admissoes'} for label in preferred_labels):
            add('get_service_directory')
        if any(label in {'Direcao', 'Coordenacao'} for label in preferred_labels):
            add('get_org_directory')

    if fetch_profile or (not required_tools and conversation_act != 'utility_date'):
        add('get_public_school_profile')
    if conversation_act == 'timeline' and not _has_public_multi_intent_signal(message):
        secondary_acts = ()

    return PublicInstitutionPlan(
        conversation_act=conversation_act,
        required_tools=tuple(required_tools),
        fetch_profile=fetch_profile,
        secondary_acts=secondary_acts,
        requested_attribute=semantic_plan.requested_attribute if semantic_plan else None,
        requested_channel=semantic_plan.requested_channel if semantic_plan else None,
        focus_hint=semantic_plan.focus_hint if semantic_plan else None,
        semantic_source=semantic_plan.semantic_source if semantic_plan else 'rules',
        use_conversation_context=semantic_plan.use_conversation_context if semantic_plan else False,
    )


def _build_public_institution_specialists(plan: PublicInstitutionPlan) -> tuple[InternalSpecialistPlan, ...]:
    specialists: list[InternalSpecialistPlan] = []

    concierge_tools = tuple(
        tool_name
        for tool_name in plan.required_tools
        if tool_name in {'list_assistant_capabilities', 'get_service_directory'}
    )
    if plan.conversation_act in {'greeting', 'capabilities', 'assistant_identity', 'service_routing'} or concierge_tools:
        specialists.append(
            InternalSpecialistPlan(
                name='concierge',
                purpose='navegacao institucional, descoberta de capacidades e orientacao por setor',
                tool_names=concierge_tools,
            )
        )

    knowledge_tools = tuple(
        tool_name
        for tool_name in plan.required_tools
        if tool_name in {'get_public_school_profile', 'get_org_directory', 'get_public_timeline', 'get_public_calendar_events'}
    )
    if knowledge_tools or not specialists:
        specialists.append(
            InternalSpecialistPlan(
                name='public_knowledge',
                purpose='fatos canonicos, lideranca, contatos e perfil publico da instituicao',
                tool_names=knowledge_tools,
            )
        )

    return tuple(specialists)


async def _execute_public_institution_plan(
    *,
    settings: Any,
    plan: PublicInstitutionPlan,
    school_profile: dict[str, Any] | None,
) -> tuple[dict[str, Any], list[str], list[str]]:
    profile = dict(school_profile or {}) if plan.fetch_profile else {}
    executed_tools: list[str] = []
    executed_specialists: list[str] = []

    for specialist in _build_public_institution_specialists(plan):
        executed_specialists.append(specialist.name)
        for tool_name in specialist.tool_names:
            if tool_name == 'get_public_school_profile':
                if not profile:
                    fetched_profile = await _fetch_public_school_profile(settings=settings)
                    if isinstance(fetched_profile, dict):
                        profile = dict(fetched_profile)
                executed_tools.append(tool_name)
                continue

            if tool_name == 'list_assistant_capabilities':
                capabilities = await _fetch_public_assistant_capabilities(settings=settings)
                if isinstance(capabilities, dict):
                    profile['assistant_capabilities'] = capabilities
                    profile.setdefault('school_name', capabilities.get('school_name'))
                    profile.setdefault('segments', capabilities.get('segments', []))
                executed_tools.append(tool_name)
                continue

            if tool_name == 'get_org_directory':
                directory = await _fetch_public_org_directory(settings=settings)
                if isinstance(directory, dict):
                    profile.setdefault('school_name', directory.get('school_name'))
                    profile['leadership_team'] = directory.get('leadership_team', [])
                    profile['contact_channels'] = directory.get('contact_channels', [])
                executed_tools.append(tool_name)
                continue

            if tool_name == 'get_service_directory':
                directory = await _fetch_public_service_directory(settings=settings)
                if isinstance(directory, dict):
                    profile.setdefault('school_name', directory.get('school_name'))
                    profile['service_catalog'] = directory.get('services', [])
                executed_tools.append(tool_name)
                continue

            if tool_name == 'get_public_timeline':
                timeline = await _fetch_public_timeline(settings=settings)
                if isinstance(timeline, dict):
                    profile.setdefault('school_name', timeline.get('school_name'))
                    profile['public_timeline'] = timeline.get('entries', [])
                executed_tools.append(tool_name)
                continue

            if tool_name == 'get_public_calendar_events':
                events = await _fetch_public_calendar_events(settings=settings)
                if events:
                    profile['public_calendar_events'] = events
                executed_tools.append(tool_name)
                continue

    return profile, executed_tools, executed_specialists


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


def _detect_visit_booking_action(message: str) -> str | None:
    normalized = _normalize_text(message)
    if any(_message_matches_term(normalized, term) for term in VISIT_CANCEL_TERMS):
        return 'cancel'
    if any(_message_matches_term(normalized, term) for term in VISIT_RESCHEDULE_TERMS):
        return 'reschedule'
    if any(_message_matches_term(normalized, phrase) for phrase in {'se eu precisar remarcar', 'e se eu precisar remarcar'}):
        return 'reschedule'
    visit_targets = {'visita', 'visita guiada', 'tour'}
    if _contains_any(normalized, {'cancelar', 'desmarcar'}) and _contains_any(normalized, visit_targets):
        return 'cancel'
    if _contains_any(normalized, {'remarcar', 'reagendar', 'mudar', 'trocar'}) and _contains_any(
        normalized,
        visit_targets,
    ):
        return 'reschedule'
    return None


def _detect_institutional_request_action(message: str) -> str | None:
    normalized = _normalize_text(message)
    if any(_message_matches_term(normalized, term) for term in INSTITUTIONAL_REQUEST_UPDATE_TERMS):
        return 'append_note'
    if any(_message_matches_term(normalized, phrase) for phrase in {'complementa dizendo que', 'complementar dizendo que', 'adiciona dizendo que', 'acrescenta dizendo que'}):
        return 'append_note'
    if _contains_any(normalized, {'complementar', 'completar', 'acrescentar', 'adicionar', 'incluir'}) and _contains_any(
        normalized,
        {'pedido', 'solicitacao', 'solicitação', 'protocolo', 'requerimento'},
    ):
        return 'append_note'
    return None


def _extract_institutional_request_update_details(message: str) -> str:
    compact = ' '.join(message.split()).strip()
    patterns = (
        r'^(?:quero\s+)?(?:complementar|completar|acrescentar|adicionar|incluir)\s+(?:ao?\s+)?(?:meu\s+)?(?:pedido|protocolo|requerimento|solicitacao|solicitação)\s*(?:dizendo\s+que|informando\s+que|com|sobre)?\s*',
        r'^(?:complemente|acrescente|adicione)\s+(?:ao?\s+)?(?:meu\s+)?(?:pedido|protocolo|requerimento|solicitacao|solicitação)\s*(?:com|sobre)?\s*',
        r'^(?:complementa|complementar|adiciona|acrescenta)\s+dizendo\s+que\s*',
    )
    details = compact
    for pattern in patterns:
        details = re.sub(pattern, '', details, flags=re.IGNORECASE).strip(' .:-')
    return details or compact


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


async def _update_visit_booking(
    *,
    settings: Any,
    request: MessageResponseRequest,
    conversation_context: dict[str, Any] | None,
) -> dict[str, Any] | None:
    conversation_external_id = request.conversation_id or _effective_conversation_id(request)
    if not conversation_external_id:
        return None
    action = _detect_visit_booking_action(request.message)
    if action is None:
        recent_focus = _recent_trace_focus(conversation_context)
        if recent_focus and recent_focus.get('kind') == 'visit' and _looks_like_visit_update_follow_up(request.message):
            action = 'reschedule'
    if action is None:
        return None
    preferred_date = _extract_requested_date(request.message)
    preferred_window = _extract_requested_window(request.message)
    protocol_code = _extract_protocol_code_hint(request.message, conversation_context)
    if not protocol_code:
        recent_snapshot = _workflow_snapshot_from_context(
            conversation_context,
            workflow_kind_hint='visit_booking',
            protocol_code_hint=None,
        )
        if isinstance(recent_snapshot, dict):
            item = recent_snapshot.get('item')
            if isinstance(item, dict):
                protocol_code = str(item.get('protocol_code', '') or '').strip() or None
    payload = {
        'conversation_external_id': conversation_external_id,
        'channel': request.channel.value,
        'telegram_chat_id': request.telegram_chat_id,
        'protocol_code': protocol_code,
        'action': action,
        'preferred_date': preferred_date.isoformat() if preferred_date else None,
        'preferred_window': preferred_window,
        'notes': request.message,
    }
    response_payload, status_code = await _api_core_post(
        settings=settings,
        path='/v1/internal/workflows/visit-bookings/actions',
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


async def _update_institutional_request(
    *,
    settings: Any,
    request: MessageResponseRequest,
    conversation_context: dict[str, Any] | None,
) -> dict[str, Any] | None:
    conversation_external_id = request.conversation_id or _effective_conversation_id(request)
    if not conversation_external_id:
        return None
    action = _detect_institutional_request_action(request.message)
    if action is None:
        return None
    protocol_code = _extract_protocol_code_hint(request.message, conversation_context)
    if not protocol_code:
        recent_snapshot = _workflow_snapshot_from_context(
            conversation_context,
            workflow_kind_hint='institutional_request',
            protocol_code_hint=None,
        )
        if isinstance(recent_snapshot, dict):
            item = recent_snapshot.get('item')
            if isinstance(item, dict):
                protocol_code = str(item.get('protocol_code', '') or '').strip() or None
    payload = {
        'conversation_external_id': conversation_external_id,
        'channel': request.channel.value,
        'telegram_chat_id': request.telegram_chat_id,
        'protocol_code': protocol_code,
        'action': action,
        'details': _extract_institutional_request_update_details(request.message),
    }
    response_payload, status_code = await _api_core_post(
        settings=settings,
        path='/v1/internal/workflows/institutional-requests/actions',
        payload=payload,
    )
    if status_code != 200 or response_payload is None:
        return None
    return response_payload


def _compose_visit_booking_answer(response_payload: dict[str, Any] | None, school_profile: dict[str, Any] | None) -> str:
    school_name = str((school_profile or {}).get('school_name', 'Colegio Horizonte'))
    if not response_payload:
        return _render_structured_answer_frame(
            StructuredAnswerFrame(
                lead=f'Posso orientar sobre visitas ao {school_name}, mas nao consegui registrar o pedido agora',
                offer='Tente novamente em instantes ou use o canal de admissions',
            )
        )
    item = response_payload.get('item')
    if not isinstance(item, dict):
        return _render_structured_answer_frame(
            StructuredAnswerFrame(
                lead=f'Registrei a intencao de visita ao {school_name}, mas nao consegui recuperar o protocolo agora',
                offer='Use admissions para confirmar o agendamento',
            )
        )
    preferred_date = item.get('preferred_date')
    preferred_window = item.get('preferred_window')
    slot_parts = []
    if preferred_date:
        slot_parts.append(str(preferred_date))
    if preferred_window:
        slot_parts.append(str(preferred_window))
    slot = ' - '.join(slot_parts) if slot_parts else 'janela a confirmar'
    return _render_structured_answer_frame(
        StructuredAnswerFrame(
            lead=f'Pedido de visita registrado para o {school_name}',
            facts=(
                f"Protocolo: {item.get('protocol_code', 'indisponivel')}",
                f'Preferencia informada: {slot}',
                f"Fila responsavel: {item.get('queue_name', 'admissoes')}",
                f"Ticket operacional: {item.get('linked_ticket_code', 'a confirmar')}",
            ),
            next_step='A equipe comercial valida a janela e retorna com a confirmacao',
        )
    )


def _compose_visit_booking_action_answer(response_payload: dict[str, Any] | None, *, request_message: str) -> str:
    action = _detect_visit_booking_action(request_message)
    preferred_date = _extract_requested_date(request_message)
    preferred_window = _extract_requested_window(request_message)

    if action == 'reschedule' and preferred_date is None and not preferred_window:
        facts: list[str] = []
        if isinstance(response_payload, dict):
            item = response_payload.get('item')
            if isinstance(item, dict):
                protocol_code = str(item.get('protocol_code', '') or '').strip()
                linked_ticket_code = str(item.get('linked_ticket_code', '') or '').strip()
                if protocol_code:
                    facts.append(f'Protocolo: {protocol_code}')
                if linked_ticket_code:
                    facts.append(f'Ticket operacional: {linked_ticket_code}')
        return _render_structured_answer_frame(
            StructuredAnswerFrame(
                lead='Consigo remarcar a visita por aqui',
                facts=tuple(facts),
                offer='Me diga pelo menos o novo dia ou a janela desejada, por exemplo: "remarque para sexta de manha" ou "troque para 28/03 as 10h"',
            )
        )

    if not response_payload or not isinstance(response_payload, dict):
        return _render_structured_answer_frame(
            StructuredAnswerFrame(
                lead='Nao consegui atualizar a visita agora',
                offer='Se quiser, me passe novamente o protocolo da visita ou o novo horario desejado',
            )
        )

    item = response_payload.get('item')
    if not isinstance(item, dict):
        return 'Localizei a visita, mas nao consegui montar a atualizacao agora.'

    protocol_code = str(item.get('protocol_code', 'indisponivel'))
    queue_name = _humanize_workflow_queue(item.get('queue_name'))
    linked_ticket_code = str(item.get('linked_ticket_code', '') or '').strip()
    slot_label = str(item.get('slot_label', '') or '').strip()

    if action == 'cancel':
        facts = [f'Protocolo: {protocol_code}']
        if linked_ticket_code:
            facts.append(f'Ticket operacional: {linked_ticket_code}')
        return _render_structured_answer_frame(
            StructuredAnswerFrame(
                lead=f'Visita cancelada no fluxo de {queue_name}',
                facts=tuple(facts),
                offer='Se quiser, eu tambem posso registrar um novo pedido de visita quando voce preferir',
            )
        )

    facts = [f'Protocolo: {protocol_code}']
    if linked_ticket_code:
        facts.append(f'Ticket operacional: {linked_ticket_code}')
    if slot_label:
        facts.append(f'Nova preferencia: {slot_label}')
    return _render_structured_answer_frame(
        StructuredAnswerFrame(
            lead=f'Pedido de visita atualizado com a fila de {queue_name}',
            facts=tuple(facts),
            next_step='Admissions valida a nova janela e retorna com a confirmacao',
        )
    )


def _compose_institutional_request_answer(response_payload: dict[str, Any] | None) -> str:
    if not response_payload:
        return _render_structured_answer_frame(
            StructuredAnswerFrame(
                lead='Posso orientar sobre protocolos institucionais, mas nao consegui registrar a solicitacao agora',
                offer='Tente novamente em instantes ou use a secretaria',
            )
        )
    item = response_payload.get('item')
    if not isinstance(item, dict):
        return _render_structured_answer_frame(
            StructuredAnswerFrame(
                lead='Registrei a manifestacao institucional, mas nao consegui recuperar o protocolo neste momento',
                offer='Use a secretaria ou a ouvidoria para confirmar',
            )
        )
    return _render_structured_answer_frame(
        StructuredAnswerFrame(
            lead=f"Solicitacao institucional registrada para {item.get('target_area', 'o setor responsavel')}",
            facts=(
                f"Protocolo: {item.get('protocol_code', 'indisponivel')}",
                f"Assunto: {item.get('subject', 'solicitacao institucional')}",
                f"Fila responsavel: {item.get('queue_name', 'atendimento')}",
                f"Ticket operacional: {item.get('linked_ticket_code', 'a confirmar')}",
            ),
            next_step='A equipe faz a triagem inicial e segue o retorno pelo fluxo institucional',
        )
    )


def _compose_institutional_request_action_answer(
    response_payload: dict[str, Any] | None,
    *,
    request_message: str,
) -> str:
    detail_text = _extract_institutional_request_update_details(request_message)
    if not detail_text:
        return _render_structured_answer_frame(
            StructuredAnswerFrame(
                lead='Consigo complementar essa solicitacao por aqui',
                offer='Me diga o que precisa ser acrescentado ao protocolo e eu atualizo o pedido',
            )
        )

    if not response_payload or not isinstance(response_payload, dict):
        return _render_structured_answer_frame(
            StructuredAnswerFrame(
                lead='Nao consegui complementar a solicitacao agora',
                offer='Se quiser, me passe novamente o protocolo ou reescreva o complemento em uma frase curta',
            )
        )

    item = response_payload.get('item')
    if not isinstance(item, dict):
        return 'Localizei a solicitacao, mas nao consegui registrar o complemento agora.'

    protocol_code = str(item.get('protocol_code', 'indisponivel'))
    queue_name = _humanize_workflow_queue(item.get('queue_name'))
    linked_ticket_code = str(item.get('linked_ticket_code', '') or '').strip()
    facts = [f'Protocolo: {protocol_code}']
    if linked_ticket_code:
        facts.append(f'Ticket operacional: {linked_ticket_code}')
    facts.append(f'Novo complemento: {detail_text}')
    return _render_structured_answer_frame(
        StructuredAnswerFrame(
            lead=f'Complemento registrado na fila de {queue_name}',
            facts=tuple(facts),
            next_step='A equipe responsavel recebe essa atualizacao no mesmo fluxo do pedido',
        )
    )


def _humanize_workflow_status(status: str) -> str:
    normalized = str(status or '').strip().lower()
    return WORKFLOW_STATUS_LABELS.get(normalized, normalized or 'em analise')


def _humanize_workflow_queue(queue_name: str | None) -> str:
    normalized = str(queue_name or '').strip().lower()
    return WORKFLOW_QUEUE_LABELS.get(normalized, normalized or 'atendimento')


def _format_workflow_timestamp(value: Any) -> str | None:
    if isinstance(value, str):
        raw = value.strip()
        if not raw:
            return None
        try:
            value = datetime.fromisoformat(raw.replace('Z', '+00:00'))
        except ValueError:
            return None
    if not isinstance(value, datetime):
        return None
    reference = datetime.now(tz=value.tzinfo) if value.tzinfo else datetime.now()
    current_date = reference.date()
    target_date = value.date()
    time_label = value.strftime('%H:%M')
    if target_date == current_date:
        return f'hoje as {time_label}'
    if target_date == current_date - timedelta(days=1):
        return f'ontem as {time_label}'
    return value.strftime('%d/%m/%Y as %H:%M')


def _frame_sentence(text: str | None) -> str | None:
    normalized = str(text or '').strip()
    if not normalized:
        return None
    if normalized[-1] not in '.!?':
        normalized = f'{normalized}.'
    return normalized


def _render_structured_answer_frame(frame: StructuredAnswerFrame) -> str:
    parts: list[str] = []
    lead = _frame_sentence(frame.lead)
    if lead:
        parts.append(lead)
    for fact in frame.facts:
        sentence = _frame_sentence(fact)
        if sentence:
            parts.append(sentence)
    next_step = _frame_sentence(frame.next_step)
    if next_step:
        parts.append(next_step)
    offer = _frame_sentence(frame.offer)
    if offer:
        parts.append(offer)
    return ' '.join(parts).strip()


def _render_structured_answer_lines(lines: list[str]) -> str:
    if not lines:
        return ''
    lead = str(lines[0] or '').strip()
    if lead.startswith('- '):
        lead = lead[2:].strip()
    facts: list[str] = []
    next_step: str | None = None
    offer: str | None = None
    for raw in lines[1:]:
        text = str(raw or '').strip()
        if not text:
            continue
        if text.startswith('- '):
            text = text[2:].strip()
        normalized = _normalize_text(text)
        if normalized.startswith('proximo passo:'):
            next_step = text
        elif normalized.startswith('se quiser'):
            offer = text if offer is None else f'{offer} {text}'
        else:
            facts.append(text)
    return _render_structured_answer_frame(
        StructuredAnswerFrame(
            lead=lead,
            facts=tuple(facts),
            next_step=next_step,
            offer=offer,
        )
    )


def _compose_orphan_workflow_follow_up_answer(
    message: str,
    conversation_context: dict[str, Any] | None,
) -> str | None:
    if _recent_conversation_focus(conversation_context):
        return None
    normalized = _normalize_text(message)
    asks_summary = any(
        _message_matches_term(normalized, term)
        for term in {'resume pra mim', 'resuma pra mim', 'faz um resumo', 'me da um resumo', 'me dê um resumo'}
    )
    asks_status = any(
        _message_matches_term(normalized, term)
        for term in {
            'esse atendimento',
            'esse pedido',
            'essa fila',
            'esse protocolo',
            'como esta esse atendimento',
            'como está esse atendimento',
            'status',
            'fila',
            'protocolo',
        }
    )
    if asks_summary:
        return (
            'Se voce quer um resumo do atendimento, me passe o protocolo ou relembre se o assunto era visita, direcao, financeiro ou secretaria. '
            'Com isso, eu te devolvo o resumo e o protocolo corretos.'
        )
    if asks_status:
        return (
            'Se voce quer consultar status ou fila de um atendimento, me passe o codigo que comeca com VIS, REQ ou ATD, '
            'ou me relembre qual era o assunto para eu localizar o protocolo correto.'
        )
    return None


def _workflow_snapshot_from_context(
    conversation_context: dict[str, Any] | None,
    *,
    workflow_kind_hint: str | None,
    protocol_code_hint: str | None,
) -> dict[str, Any] | None:
    focus = _recent_trace_focus(conversation_context)
    if not isinstance(focus, dict):
        return None
    focus_kind = str(focus.get('kind', '') or '').strip()
    active_task = str(focus.get('active_task', '') or '').strip()
    if not _recent_focus_is_fresh(conversation_context, focus_kind=focus_kind, active_task=active_task):
        return None

    expected_workflow_types: set[str] = set()
    if workflow_kind_hint:
        expected_workflow_types.add(str(workflow_kind_hint).strip())
    elif focus_kind == 'visit':
        expected_workflow_types.add('visit_booking')
    elif focus_kind == 'request':
        expected_workflow_types.add('institutional_request')
    elif focus_kind == 'support':
        expected_workflow_types.add('support_handoff')

    for item in reversed(_recent_tool_call_entries(conversation_context)):
        tool_name = str(item.get('tool_name', '') or '').strip()
        if tool_name not in {
            'get_workflow_status',
            'schedule_school_visit',
            'update_visit_booking',
            'create_institutional_request',
            'update_institutional_request',
            'create_support_ticket',
            'handoff_to_human',
        }:
            continue
        response_payload = item.get('response_payload')
        if not isinstance(response_payload, dict):
            continue
        snapshot = response_payload.get('item')
        if not isinstance(snapshot, dict):
            continue
        normalized_snapshot = dict(snapshot)
        if tool_name in {'schedule_school_visit', 'update_visit_booking'}:
            normalized_snapshot.setdefault('workflow_type', 'visit_booking')
        elif tool_name in {'create_institutional_request', 'update_institutional_request'}:
            normalized_snapshot.setdefault('workflow_type', 'institutional_request')
        elif tool_name in {'create_support_ticket', 'handoff_to_human'}:
            normalized_snapshot.setdefault('workflow_type', 'support_handoff')
            if not normalized_snapshot.get('protocol_code') and normalized_snapshot.get('ticket_code'):
                normalized_snapshot['protocol_code'] = normalized_snapshot.get('ticket_code')
            if not normalized_snapshot.get('linked_ticket_code') and normalized_snapshot.get('ticket_code'):
                normalized_snapshot['linked_ticket_code'] = normalized_snapshot.get('ticket_code')
        workflow_type = str(normalized_snapshot.get('workflow_type', '') or '').strip()
        if expected_workflow_types and workflow_type not in expected_workflow_types:
            continue
        snapshot_protocol = str(normalized_snapshot.get('protocol_code', '') or '').strip()
        if protocol_code_hint and snapshot_protocol and snapshot_protocol.upper() != str(protocol_code_hint).strip().upper():
            continue
        return {'found': True, 'item': normalized_snapshot}
    return None


def _compose_workflow_status_answer(
    response_payload: dict[str, Any] | None,
    *,
    protocol_code_hint: str | None,
    request_message: str,
) -> str:
    normalized_request = _normalize_text(request_message)
    asks_status_explicitly = any(
        _message_matches_term(normalized_request, term)
        for term in {
            'qual o status',
            'status',
            'andamento',
            'situacao',
            'fila',
            'como esta esse atendimento',
            'como está esse atendimento',
            'qual o prazo',
            'quando me respondem',
            'quem vai me responder',
        }
    )
    asks_update_explicitly = any(
        _message_matches_term(normalized_request, term)
        for term in {
            'tem alguma atualizacao',
            'tem alguma atualização',
            'alguma atualizacao',
            'alguma atualização',
            'ultima atualizacao',
            'ultima atualização',
            'teve atualizacao',
            'teve atualização',
        }
    )
    asks_next_step = any(
        _message_matches_term(normalized_request, term)
        for term in {
            'qual o proximo passo',
            'qual o próximo passo',
            'proximo passo',
            'próximo passo',
            'e agora',
            'o que acontece agora',
        }
    )
    asks_protocol_only = not asks_status_explicitly and any(
        _message_matches_term(normalized_request, term)
        for term in {'qual o protocolo', 'me passa o protocolo', 'meu protocolo', 'numero do protocolo', 'protocolo'}
    )
    asks_summary = any(
        _message_matches_term(normalized_request, term)
        for term in {
            'resume meu pedido',
            'resuma meu pedido',
            'faz um resumo do meu pedido',
            'faz um resumo',
            'o que eu pedi',
            'qual foi meu pedido',
            'resume pra mim',
            'resuma pra mim',
        }
    )

    if not isinstance(response_payload, dict) or not response_payload.get('found'):
        if protocol_code_hint:
            return (
                f'Ainda nao localizei um protocolo ativo com o codigo {protocol_code_hint}. '
                'Se quiser, me encaminhe novamente o codigo completo ou me diga se o assunto era visita, direcao, financeiro ou secretaria.'
            )
        if asks_summary:
            return (
                'Ainda nao encontrei um protocolo recente nesta conversa para montar o resumo do pedido. '
                'Se quiser, me diga o codigo que comeca com VIS, REQ ou ATD, ou me lembre se o assunto era visita, direcao, financeiro ou secretaria.'
            )
        if asks_status_explicitly or asks_update_explicitly or asks_next_step:
            return (
                'Ainda nao encontrei um protocolo recente nesta conversa para consultar o status da fila. '
                'Se quiser, me diga o codigo que comeca com VIS, REQ ou ATD, ou me lembre se o assunto era visita, direcao, financeiro ou secretaria.'
            )
        return (
            'Ainda nao encontrei um protocolo recente nesta conversa. '
            'Se quiser, me diga o codigo que comeca com VIS, REQ ou ATD, ou me lembre se o assunto era visita, direcao, financeiro ou secretaria.'
        )

    item = response_payload.get('item')
    if not isinstance(item, dict):
        return 'Localizei um protocolo desta conversa, mas nao consegui interpretar o status agora.'

    workflow_type = str(item.get('workflow_type', 'support_handoff'))
    status_label = _humanize_workflow_status(str(item.get('status', '')))
    queue_label = _humanize_workflow_queue(item.get('queue_name'))
    protocol_code = str(item.get('protocol_code', protocol_code_hint or 'indisponivel'))
    linked_ticket_code = str(item.get('linked_ticket_code', '') or '').strip()
    subject = str(item.get('subject', '') or '').strip()
    summary_text = str(item.get('summary', '') or '').strip()
    target_area = str(item.get('target_area', '') or '').strip()
    preferred_date = str(item.get('preferred_date', '') or '').strip()
    preferred_window = str(item.get('preferred_window', '') or '').strip()
    slot_label = str(item.get('slot_label', '') or '').strip()
    updated_at_label = _format_workflow_timestamp(item.get('updated_at'))
    if workflow_type == 'visit_booking':
        if asks_protocol_only:
            lines = [f'O protocolo da sua visita e {protocol_code}.']
            if linked_ticket_code:
                lines.append(f'- Ticket operacional: {linked_ticket_code}')
            if slot_label:
                lines.append(f'- Preferencia registrada: {slot_label}')
            lines.append('Se quiser, eu tambem posso te dizer o status, remarcar ou cancelar a visita.')
            return _render_structured_answer_lines(lines)
        if asks_summary:
            lines = ['Resumo do seu pedido de visita:']
            if slot_label:
                lines.append(f'- Preferencia registrada: {slot_label}')
            elif preferred_date or preferred_window:
                preference = ' - '.join(part for part in [preferred_date, preferred_window] if part)
                lines.append(f'- Preferencia registrada: {preference}')
            lines.append(f'- Protocolo: {protocol_code}')
            if linked_ticket_code:
                lines.append(f'- Ticket operacional: {linked_ticket_code}')
            lines.append(f'- Status atual: {status_label}')
            lines.append('Se quiser, eu posso remarcar, cancelar ou acompanhar esse pedido com voce.')
            return '\n'.join(lines)
        if asks_update_explicitly:
            lines = [f'A ultima atualizacao da sua visita mostra que ela segue {status_label}.', f'- Protocolo: {protocol_code}']
            if updated_at_label:
                lines.append(f'- Ultima movimentacao registrada: {updated_at_label}')
            if linked_ticket_code:
                lines.append(f'- Ticket operacional: {linked_ticket_code}')
            if slot_label:
                lines.append(f'- Preferencia registrada: {slot_label}')
            lines.append('No momento, a equipe comercial ainda precisa validar a janela antes da confirmacao.')
            return '\n'.join(lines)
        if asks_next_step:
            lines = [f'Proximo passo da sua visita: admissions valida a janela antes de confirmar o horario.', f'- Protocolo: {protocol_code}']
            if updated_at_label:
                lines.append(f'- Ultima movimentacao registrada: {updated_at_label}')
            if slot_label:
                lines.append(f'- Preferencia registrada: {slot_label}')
            lines.append('Se quiser, eu posso remarcar ou cancelar esse pedido por aqui.')
            return '\n'.join(lines)
        lines = [
            f'Seu pedido de visita segue {status_label} com a fila de {queue_label}.',
            f'- Protocolo: {protocol_code}',
        ]
        if linked_ticket_code:
            lines.append(f'- Ticket operacional: {linked_ticket_code}')
        if updated_at_label:
            lines.append(f'- Ultima movimentacao registrada: {updated_at_label}')
        if slot_label:
            lines.append(f'- Preferencia registrada: {slot_label}')
        elif preferred_date or preferred_window:
            preference = ' - '.join(part for part in [preferred_date, preferred_window] if part)
            lines.append(f'- Preferencia registrada: {preference}')
        if any(_message_matches_term(normalized_request, term) for term in {'qual o prazo', 'quanto tempo demora', 'quando me respondem', 'quando vao me responder', 'quando vão me responder'}):
            lines.append('Prazo esperado: admissions costuma validar a janela e retornar em ate 1 dia util.')
        elif any(_message_matches_term(normalized_request, term) for term in {'quem vai me responder', 'quem vai retornar', 'quem fica com isso'}):
            lines.append('Quem responde: a equipe comercial de admissions devolve a confirmacao por este fluxo.')
        else:
            lines.append('Proximo passo: a equipe comercial valida a janela e retorna com a confirmacao.')
        return _render_structured_answer_lines(lines)

    if workflow_type == 'institutional_request':
        if asks_protocol_only:
            lines = [f'O protocolo da sua solicitacao e {protocol_code}.']
            if linked_ticket_code:
                lines.append(f'- Ticket operacional: {linked_ticket_code}')
            if target_area:
                lines.append(f'- Area responsavel: {target_area}')
            lines.append('Se quiser, eu tambem posso resumir o pedido ou verificar o status atual.')
            return _render_structured_answer_lines(lines)
        if asks_summary:
            lines = ['Resumo da sua solicitacao institucional:']
            if subject:
                lines.append(f'- Assunto: {subject}')
            if target_area:
                lines.append(f'- Area responsavel: {target_area}')
            if summary_text:
                lines.append(f'- Detalhes registrados: {summary_text}')
            lines.append(f'- Protocolo: {protocol_code}')
            if linked_ticket_code:
                lines.append(f'- Ticket operacional: {linked_ticket_code}')
            lines.append(f'- Status atual: {status_label}')
            lines.append('Se quiser, eu tambem posso te dizer o prazo estimado ou quem responde por essa fila.')
            return _render_structured_answer_lines(lines)
        if asks_update_explicitly:
            lines = [
                f'A ultima atualizacao do seu protocolo mostra que ele segue {status_label}.',
                f'- Protocolo: {protocol_code}',
            ]
            if updated_at_label:
                lines.append(f'- Ultima movimentacao registrada: {updated_at_label}')
            if target_area:
                lines.append(f'- Area responsavel: {target_area}')
            if linked_ticket_code:
                lines.append(f'- Ticket operacional: {linked_ticket_code}')
            lines.append(f'No momento, a fila de {queue_label} ainda precisa analisar o contexto antes do retorno.')
            return _render_structured_answer_lines(lines)
        if asks_next_step:
            lines = [
                f'Proximo passo do seu protocolo: a fila de {queue_label} analisa o contexto e prepara o retorno.',
                f'- Protocolo: {protocol_code}',
            ]
            if updated_at_label:
                lines.append(f'- Ultima movimentacao registrada: {updated_at_label}')
            if target_area:
                lines.append(f'- Area responsavel: {target_area}')
            lines.append('Se quiser, eu tambem posso resumir o pedido ou registrar um complemento.')
            return _render_structured_answer_lines(lines)
        lines = [
            f'Sua solicitacao institucional segue {status_label} na fila de {queue_label}.',
            f'- Protocolo: {protocol_code}',
        ]
        if subject:
            lines.append(f'- Assunto: {subject}')
        if target_area:
            lines.append(f'- Area responsavel: {target_area}')
        if linked_ticket_code:
            lines.append(f'- Ticket operacional: {linked_ticket_code}')
        if updated_at_label:
            lines.append(f'- Ultima movimentacao registrada: {updated_at_label}')
        if any(_message_matches_term(normalized_request, term) for term in {'qual o prazo', 'quanto tempo demora', 'quando me respondem', 'quando vao me responder', 'quando vão me responder'}):
            lines.append('Prazo esperado: a triagem inicial costuma acontecer em ate 2 dias uteis, conforme a fila responsavel.')
        elif any(_message_matches_term(normalized_request, term) for term in {'quem vai me responder', 'quem vai retornar', 'quem fica com isso'}):
            lines.append(f'Quem responde: a equipe da fila de {queue_label} devolve o retorno pelo fluxo institucional.')
        else:
            lines.append('Proximo passo: a equipe responsavel analisa o contexto e devolve o retorno pelo fluxo institucional.')
        return _render_structured_answer_lines(lines)

    if asks_protocol_only:
        lines = [f'O protocolo atual do seu atendimento e {protocol_code}.']
        if linked_ticket_code and linked_ticket_code != protocol_code:
            lines.append(f'- Ticket operacional: {linked_ticket_code}')
        lines.append('Se quiser, eu posso te dizer o status atual ou resumir o que ja foi registrado.')
        return _render_structured_answer_lines(lines)

    if asks_summary:
        lines = ['Resumo do seu atendimento institucional:']
        if subject:
            lines.append(f'- Assunto: {subject}')
        lines.append(f'- Protocolo: {protocol_code}')
        if linked_ticket_code and linked_ticket_code != protocol_code:
            lines.append(f'- Ticket operacional: {linked_ticket_code}')
        lines.append(f'- Status atual: {status_label}')
        lines.append('Se quiser, eu tambem posso te orientar sobre o proximo passo.')
        return _render_structured_answer_lines(lines)

    lines = [
        f'Seu atendimento segue {status_label} na fila de {queue_label}.',
        f'- Protocolo: {protocol_code}',
    ]
    if subject:
        lines.append(f'- Resumo: {subject}')
    if linked_ticket_code and linked_ticket_code != protocol_code:
        lines.append(f'- Ticket operacional: {linked_ticket_code}')
    if any(_message_matches_term(normalized_request, term) for term in {'quem vai me responder', 'quem vai retornar', 'quem fica com isso'}):
        lines.append(f'Quem responde: a equipe da fila de {queue_label} continua esse atendimento.')
    elif any(_message_matches_term(normalized_request, term) for term in {'qual o prazo', 'quanto tempo demora'}):
        lines.append('Prazo esperado: o retorno depende da fila atual, e eu posso te ajudar a identificar o proximo setor.')
    else:
        lines.append('Se quiser, eu tambem posso te orientar sobre o proximo setor ou resumir o que ja foi registrado.')
    return _render_structured_answer_lines(lines)


def _dedupe_suggested_replies(texts: list[str], *, limit: int = 4) -> list[MessageResponseSuggestedReply]:
    seen: set[str] = set()
    items: list[MessageResponseSuggestedReply] = []
    for text in texts:
        label = str(text or '').strip()
        if not label:
            continue
        normalized = _normalize_text(label)
        if normalized in seen:
            continue
        seen.add(normalized)
        items.append(MessageResponseSuggestedReply(text=label[:80]))
        if len(items) >= limit:
            break
    return items


def _default_public_suggested_replies() -> list[str]:
    return [
        'Mensalidade do ensino medio',
        'Horario do 9o ano',
        'Agendar visita',
        'Como vinculo minha conta?',
    ]


def _institution_suggested_replies(
    *,
    request: MessageResponseRequest,
    preview: Any,
    school_profile: dict[str, Any] | None,
    conversation_context: dict[str, Any] | None,
) -> list[str]:
    normalized = _normalize_text(request.message)
    profile = school_profile or {}
    recent_focus = _recent_conversation_focus(conversation_context)
    if preview.mode is OrchestrationMode.structured_tool and 'get_administrative_status' in preview.selected_tools:
        return [
            'Falar com a secretaria',
            'Por onde envio meus documentos?',
            'Como altero meu email cadastral?',
            'Tem boleto em aberto?',
        ]
    if _is_greeting_only(request.message) or _is_capability_query(request.message) or _is_auth_guidance_query(request.message):
        if recent_focus:
            kind = recent_focus.get('kind')
            if kind == 'visit':
                return [
                    'Qual o status da visita?',
                    'Quero remarcar a visita',
                    'Quero cancelar a visita',
                    'Qual o protocolo da visita?',
                ]
            if kind == 'request':
                return [
                    'Qual o status do meu protocolo?',
                    'Qual o prazo?',
                    'Quem vai me responder?',
                    'Resume meu pedido',
                ]
            if kind == 'finance':
                return [
                    'Como vinculo minha conta?',
                    'Mensalidade do ensino medio',
                    'Quero falar sobre contrato',
                    'Falar com o financeiro',
                ]
        return _default_public_suggested_replies()
    if _is_assistant_identity_query(request.message):
        if recent_focus and recent_focus.get('kind') == 'visit':
            return [
                'Qual o status da visita?',
                'Quero remarcar a visita',
                'Quero cancelar a visita',
                'Qual o protocolo da visita?',
            ]
        if recent_focus and recent_focus.get('kind') == 'request':
            return [
                'Qual o status do meu protocolo?',
                'Qual o prazo?',
                'Quem vai me responder?',
                'Resume meu pedido',
            ]
        return [
            'Quais opcoes de assuntos eu tenho aqui?',
            'Falar com a secretaria',
            'Agendar visita',
            'Como vinculo minha conta?',
        ]
    if _is_service_routing_query(request.message):
        message_for_matching = _routing_follow_up_context_message(request.message, conversation_context)
        matches = _service_matches_from_message(profile, message_for_matching)
        if matches:
            service_key = str(matches[0].get('service_key', '')).strip().lower()
            if service_key == 'financeiro_escolar':
                return [
                    'Como vinculo minha conta?',
                    'Mensalidade do ensino medio',
                    'Quero falar sobre contrato',
                    'Agendar visita',
                ]
            if service_key == 'secretaria_escolar':
                return [
                    'Quais documentos preciso para matricula?',
                    'Preciso de historico escolar',
                    'Quero falar com a secretaria',
                    'Agendar visita',
                ]
            if service_key == 'visita_institucional':
                return [
                    'Quero agendar uma visita',
                    'Qual o horario do 9o ano?',
                    'Mensalidade do ensino medio',
                    'Como vinculo minha conta?',
                ]
            if service_key == 'orientacao_educacional':
                return [
                    'Quero registrar esse caso',
                    'Como falo com a direcao?',
                    'Qual o prazo de retorno?',
                    'Quais opcoes de assuntos eu tenho aqui?',
                ]
            if service_key == 'solicitacao_direcao':
                return [
                    'Quero protocolar uma solicitacao',
                    'Qual o nome da diretora?',
                    'Qual o status do meu protocolo?',
                    'Agendar visita',
                ]
        return [
            'Falar com a secretaria',
            'Falar com o financeiro',
            'Agendar visita',
            'Como vinculo minha conta?',
        ]
    if any(_message_matches_term(normalized, term) for term in PUBLIC_LEADERSHIP_TERMS):
        return [
            'Qual o email da direcao?',
            'Quero protocolar uma solicitacao',
            'Quais opcoes de assuntos eu tenho aqui?',
            'Agendar visita',
        ]
    if any(_message_matches_term(normalized, term) for term in PUBLIC_CONTACT_TERMS):
        return [
            'Falar com a secretaria',
            'Agendar visita',
            'Mensalidade do ensino medio',
            'Como vinculo minha conta?',
        ]
    if any(_message_matches_term(normalized, term) for term in PUBLIC_KPI_TERMS):
        return [
            'Mostre um grafico da media de aprovacao',
            'Fale uma curiosidade da escola',
            'Qual o nome da diretora?',
            'Agendar visita',
        ]
    if any(_message_matches_term(normalized, term) for term in PUBLIC_HIGHLIGHT_TERMS):
        return [
            'Qual a media de aprovacao?',
            'A escola e laica ou confessional?',
            'Qual o horario do 9o ano?',
            'Agendar visita',
        ]
    if any(_message_matches_term(normalized, term) for term in PUBLIC_VISIT_TERMS):
        return [
            'Quero agendar uma visita',
            'Qual o status da visita?',
            'Qual o prazo?',
            'Quem vai me responder?',
        ]
    if _is_public_pricing_navigation_query(request.message):
        return [
            'Como vinculo minha conta?',
            'Quais bolsas a escola oferece?',
            'Agendar visita',
            'Qual o horario do 9o ano?',
        ]
    feature_keys = _requested_public_features(request.message)
    if (
        not feature_keys
        and _is_follow_up_query(request.message)
        and not _is_public_feature_query(request.message)
    ):
        feature_keys = _requested_public_features(
            _routing_follow_up_context_message(request.message, conversation_context)
        )
    if feature_keys or _is_public_feature_query(request.message):
        return _feature_suggestion_replies(feature_keys)
    if preview.mode is OrchestrationMode.hybrid_retrieval:
        if 'matricula' in normalized:
            return [
                'Qual a mensalidade do ensino medio?',
                'Quero agendar uma visita',
                'Qual o horario do 9o ano?',
                'Como vinculo minha conta?',
            ]
        return _default_public_suggested_replies()
    return _default_public_suggested_replies()
def _workflow_contextual_suggested_replies(
    *,
    preview: Any,
    conversation_context: dict[str, Any] | None,
) -> list[str] | None:
    recent_focus = _recent_conversation_focus(conversation_context)
    if not recent_focus:
        return None
    kind = recent_focus.get('kind')
    if 'get_workflow_status' in preview.selected_tools:
        if kind == 'visit':
            return ['Tem alguma atualizacao da visita?', 'Qual o proximo passo da visita?', 'Quero remarcar a visita', 'Quero cancelar a visita']
        if kind == 'request':
            return ['Tem alguma atualizacao?', 'Qual o proximo passo?', 'Complementar meu pedido', 'Resume meu pedido']
    if 'update_visit_booking' in preview.selected_tools or kind == 'visit':
        return ['Tem alguma atualizacao da visita?', 'Qual o proximo passo da visita?', 'Quero cancelar a visita', 'Quero remarcar a visita']
    if 'update_institutional_request' in preview.selected_tools or kind == 'request':
        return ['Tem alguma atualizacao?', 'Qual o proximo passo?', 'Complementar meu pedido', 'Resume meu pedido']
    return None


def _recent_protected_student_name(
    actor: dict[str, Any] | None,
    *,
    capability: str,
    message: str | None = None,
    conversation_context: dict[str, Any] | None,
) -> str | None:
    student: dict[str, Any] | None = None
    if message:
        student, _clarification = _select_linked_student(
            actor,
            message,
            capability=capability,
            conversation_context=conversation_context,
        )
    if student is None:
        student = _recent_student_from_context(
            actor,
            capability=capability,
            conversation_context=conversation_context,
        )
    if student is None:
        return None
    full_name = str(student.get('full_name', '')).strip()
    if not full_name:
        return None
    return full_name.split()[0]


def _protected_suggested_replies(
    *,
    request: MessageResponseRequest,
    preview: Any,
    actor: dict[str, Any] | None,
    conversation_context: dict[str, Any] | None,
) -> list[str]:
    role_code = str((actor or {}).get('role_code', 'anonymous'))
    if preview.classification.domain is QueryDomain.finance:
        student_name = _recent_protected_student_name(
            actor,
            capability='finance',
            message=request.message,
            conversation_context=conversation_context,
        )
        if student_name:
            return [
                f'Quais boletos do {student_name} estao em aberto?',
                f'Tem alguma fatura vencida do {student_name}?',
                f'Preciso da segunda via do {student_name}',
                f'E as notas do {student_name}?',
            ]
        return ['Quais boletos estao em aberto?', 'Tem alguma fatura vencida?', 'Preciso da segunda via', 'Qual a mensalidade?']
    if role_code == 'teacher':
        return ['Quais turmas eu tenho?', 'Mostre minha agenda', 'Qual o horario de hoje?', 'Tem aula substituta?']
    student_name = _recent_protected_student_name(
        actor,
        capability='academic',
        message=request.message,
        conversation_context=conversation_context,
    )
    if student_name:
        return [
            f'E a frequencia do {student_name}?',
            f'E o financeiro do {student_name}?',
            f'Mostre um grafico das notas do {student_name}',
            f'Qual o calendario da turma do {student_name}?',
        ]
    return ['Mostre as notas', 'Quais sao as faltas?', 'Tem prova marcada?', 'Qual o calendario da turma?']


def _support_suggested_replies(*, preview: Any, conversation_context: dict[str, Any] | None) -> list[str]:
    contextual = _workflow_contextual_suggested_replies(
        preview=preview,
        conversation_context=conversation_context,
    )
    if contextual:
        return contextual
    if 'get_workflow_status' in preview.selected_tools:
        return ['Qual o prazo?', 'Quem vai me responder?', 'Qual o protocolo?', 'Complementar meu pedido']
    if 'update_visit_booking' in preview.selected_tools:
        return ['Qual o status da visita?', 'Qual o protocolo da visita?', 'Quero cancelar a visita', 'Quero remarcar a visita']
    if 'update_institutional_request' in preview.selected_tools:
        return ['Qual o status do meu protocolo?', 'Qual o prazo?', 'Quem vai me responder?', 'Resume meu pedido']
    if 'schedule_school_visit' in preview.selected_tools:
        return ['Qual o status da visita?', 'Qual o prazo?', 'Quem vai me responder?', 'Mudar horario da visita']
    return ['Qual o status do meu protocolo?', 'Qual o prazo?', 'Quem vai me responder?', 'E agora?']


def _deny_suggested_replies() -> list[str]:
    return ['Como vinculo minha conta?', 'Mensalidade do ensino medio', 'Agendar visita', 'Quais opcoes de assuntos eu tenho aqui?']


def _build_suggested_replies(
    *,
    request: MessageResponseRequest,
    preview: Any,
    actor: dict[str, Any] | None,
    school_profile: dict[str, Any] | None,
    conversation_context: dict[str, Any] | None,
) -> list[MessageResponseSuggestedReply]:
    candidate_texts: list[str]
    if preview.mode is OrchestrationMode.deny:
        candidate_texts = _deny_suggested_replies()
    elif preview.classification.domain is QueryDomain.support and preview.mode is OrchestrationMode.structured_tool:
        candidate_texts = _support_suggested_replies(preview=preview, conversation_context=conversation_context)
    elif preview.classification.domain in {QueryDomain.academic, QueryDomain.finance} and preview.mode is OrchestrationMode.structured_tool:
        candidate_texts = _protected_suggested_replies(
            request=request,
            preview=preview,
            actor=actor,
            conversation_context=conversation_context,
        )
    elif preview.classification.domain is QueryDomain.institution:
        candidate_texts = _institution_suggested_replies(
            request=request,
            preview=preview,
            school_profile=school_profile,
            conversation_context=conversation_context,
        )
    elif preview.classification.domain is QueryDomain.calendar:
        candidate_texts = [
            'Quando e a proxima reuniao de pais?',
            'Quando comecam as aulas?',
            'Qual o horario do 9o ano?',
            'Agendar visita',
        ]
    else:
        candidate_texts = _default_public_suggested_replies()
    return _dedupe_suggested_replies(candidate_texts)


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


def _normalize_response_wording(message_text: str) -> str:
    normalized = str(message_text or '')
    replacements = {
        'enviar por e-mail para a secretaria': 'usar o email da secretaria',
        'o e-mail da secretaria': 'o email da secretaria',
        'E-mail da secretaria': 'Email da secretaria',
    }
    for source, target in replacements.items():
        normalized = normalized.replace(source, target)
    return normalized


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
    conversation_context: dict[str, Any] | None = None,
) -> list[MessageResponseVisualAsset]:
    specialists = _build_visual_specialists(preview=preview, message=request.message)
    if not specialists:
        return []

    set_span_attributes(
        **{
            'eduassist.visual_manager.executed_specialists': ','.join(
                specialist.name for specialist in specialists
            ),
            'eduassist.visual_manager.executed_tools': ','.join(
                tool_name for specialist in specialists for tool_name in specialist.tool_names
            ),
        }
    )

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

    student, clarification = _select_linked_student(
        actor,
        request.message,
        capability='finance' if preview.classification.domain is QueryDomain.finance else 'academic',
        conversation_context=conversation_context,
    )
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
        return _render_structured_answer_frame(
            StructuredAnswerFrame(
                lead='Posso seguir com orientacoes publicas por aqui, mas nao consegui registrar o encaminhamento humano agora',
                offer='Tente novamente em instantes ou use a secretaria',
            )
        )

    item = handoff_payload.get('item')
    if not isinstance(item, dict):
        return _render_structured_answer_frame(
            StructuredAnswerFrame(
                lead='Registrei a necessidade de atendimento humano, mas nao consegui recuperar o protocolo',
                offer='Use a secretaria para confirmar a fila',
            )
        )

    queue_name = str(item.get('queue_name', 'atendimento'))
    ticket_code = str(item.get('ticket_code', 'protocolo indisponivel'))
    status = str(item.get('status', 'queued'))
    created = bool(handoff_payload.get('created', False))

    if created:
        return _render_structured_answer_frame(
            StructuredAnswerFrame(
                lead=f'Encaminhei sua solicitacao para a fila de {queue_name}',
                facts=(
                    f'Protocolo: {ticket_code}',
                    f'Status atual: {status}',
                ),
                next_step='A equipe humana pode continuar esse atendimento no portal operacional',
            )
        )

    return _render_structured_answer_frame(
        StructuredAnswerFrame(
            lead=f'Sua solicitacao ja estava registrada na fila de {queue_name}',
            facts=(
                f'Protocolo: {ticket_code}',
                f'Status atual: {status}',
            ),
        )
    )


def _linked_students(actor: dict[str, Any] | None) -> list[dict[str, Any]]:
    if not actor:
        return []
    linked_students = actor.get('linked_students')
    if not isinstance(linked_students, list):
        return []
    return [student for student in linked_students if isinstance(student, dict)]


def _student_focus_candidate(actor: dict[str, Any] | None, message: str) -> dict[str, Any] | None:
    matched_students = _matching_students_in_text(_linked_students(actor), message)
    if len(matched_students) != 1:
        return None
    return matched_students[0]


def _student_capability_topics(student: dict[str, Any]) -> list[str]:
    topics: list[str] = []
    if bool(student.get('can_view_academic', False)):
        topics.extend(['notas', 'faltas', 'proximas provas', 'matricula'])
    if bool(student.get('can_view_finance', False)):
        topics.extend(['financeiro', 'boletos'])
    deduped: list[str] = []
    for topic in topics:
        if topic not in deduped:
            deduped.append(topic)
    return deduped


def _is_children_overview_query(message: str, actor: dict[str, Any] | None) -> bool:
    if not _linked_students(actor):
        return False
    normalized = _normalize_text(message)
    if any(
        _message_matches_term(normalized, term)
        for term in {
            'quais meus filhos',
            'quais sao meus filhos',
            'quais são meus filhos',
            'quem sao meus filhos',
            'quem são meus filhos',
            'quem estao vinculados',
            'quem está vinculado',
        }
    ):
        return True
    if not any(
        _message_matches_term(normalized, term)
        for term in {
            'meus filhos',
            'meu filho',
            'quais filhos tenho',
            'filhos matriculados',
            'filhos vinculados',
            'alunos vinculados',
        }
    ):
        return False
    return any(
        _message_matches_term(normalized, term)
        for term in {
            'informacao',
            'informacoes',
            'dados',
            'fornecer',
            'consigo obter',
            'posso obter',
            'matriculados',
            'vinculados',
        }
    )


def _is_student_focus_activation_query(message: str, actor: dict[str, Any] | None) -> bool:
    student = _student_focus_candidate(actor, message)
    if student is None:
        return False
    normalized = _normalize_text(message)
    if any(
        value is not None
        for value in (
            _detect_academic_focus_kind(message),
            _detect_academic_attribute_request(message),
            _detect_finance_attribute_request(message),
        )
    ):
        return False
    if _effective_finance_status_filter(message) or _detect_admin_attribute_request(message) is not None:
        return False
    if any(
        _message_matches_term(normalized, term)
        for term in {
            'quero falar do',
            'quero falar sobre',
            'falar do',
            'falar sobre',
            'sobre o',
            'sobre a',
            'eu falei',
        }
    ):
        return True
    token_count = len(re.findall(r'[a-z0-9]+', normalized))
    return token_count <= 6


def _is_discourse_repair_reset_query(
    message: str,
    conversation_context: dict[str, Any] | None,
) -> bool:
    normalized = _normalize_text(message)
    if not any(
        _message_matches_term(normalized, term)
        for term in {
            'cheguei agora',
            'acabei de chegar',
            'acabei de entrar',
            'eu cheguei agora',
            'mas eu cheguei agora',
            'acabei de chegar agora',
        }
    ):
        return False
    recent_focus = _recent_trace_focus(conversation_context)
    if not isinstance(recent_focus, dict):
        return False
    active_task = str(recent_focus.get('active_task', '') or '').strip()
    return active_task.startswith('workflow:')


def _derive_pending_disambiguation(
    *,
    actor: dict[str, Any] | None,
    message: str,
    preview: Any | None,
    conversation_context: dict[str, Any] | None,
) -> str | None:
    if _is_discourse_repair_reset_query(message, conversation_context):
        return 'workflow_reset'
    if _is_access_scope_query(message) or _is_access_scope_repair_query(message, actor, conversation_context):
        return 'access_scope'
    if _is_linked_student_repair_query(message, conversation_context):
        return 'linked_student_repair'
    if _is_children_overview_query(message, actor):
        return 'linked_students_overview'
    linked_students = _linked_students(actor)
    if linked_students and not _matching_students_in_text(linked_students, message) and _explicit_unmatched_student_reference(
        linked_students,
        message,
        conversation_context=conversation_context,
    ):
        return 'student_reference_unmatched'
    if _is_student_focus_activation_query(message, actor):
        return 'student_focus'
    if preview is not None and getattr(preview, 'mode', None) is OrchestrationMode.clarify:
        rescued_domain = _recent_student_disambiguation_domain(conversation_context)
        if rescued_domain is not None:
            return 'student_selection'
    return None


def _compose_linked_students_overview_answer(actor: dict[str, Any] | None) -> str | None:
    students = _linked_students(actor)
    if not students:
        return None
    names = [str(student.get('full_name', 'Aluno')).strip() for student in students]
    names = [name for name in names if name]
    if not names:
        return None
    preview_names = ', '.join(names[:-1]) + f' e {names[-1]}' if len(names) > 1 else names[0]
    capability_topics = _student_capability_topics(students[0])
    capability_text = ', '.join(capability_topics[:6]) if capability_topics else 'informacoes escolares autorizadas'
    return (
        f'Os alunos vinculados a esta conta hoje sao {preview_names}. '
        f'Eu posso consultar {capability_text}, dentro do que sua vinculacao permitir. '
        'Se quiser, me diga direto algo como "notas do Lucas" ou "financeiro da Ana".'
    )


def _compose_authenticated_access_scope_answer(
    actor: dict[str, Any] | None,
    *,
    school_name: str = 'Colegio Horizonte',
) -> str:
    students = _linked_students(actor)
    if not students:
        return (
            'Para consultas protegidas, como notas, faltas, provas e financeiro, voce precisa vincular sua conta do Telegram '
            f'ao portal do {school_name}. No portal autenticado, gere o codigo de vinculacao e depois envie aqui o comando '
            '`/start link_<codigo>`. Depois disso, eu passo a consultar seus dados autorizados por este canal.'
        )

    names = [str(student.get('full_name', 'Aluno')).strip() for student in students]
    names = [name for name in names if name]
    preview_names = ', '.join(names[:-1]) + f' e {names[-1]}' if len(names) > 1 else (names[0] if names else 'aluno vinculado')
    topics: list[str] = []
    for student in students:
        for topic in _student_capability_topics(student):
            if topic not in topics:
                topics.append(topic)
    topics_text = ', '.join(topics[:6]) if topics else 'informacoes escolares autorizadas'
    return (
        f'Voce ja esta autenticado por aqui e sua conta esta vinculada a {preview_names}. '
        f'Por este canal eu consigo consultar {topics_text}, dentro das permissoes dessa vinculacao. '
        'Se quiser, me diga algo como "notas do Lucas", "faltas da Ana" ou "financeiro do Lucas".'
    )


def _compose_public_access_scope_answer(
    actor: dict[str, Any] | None,
    *,
    school_name: str = 'Colegio Horizonte',
) -> str:
    return _compose_authenticated_access_scope_answer(actor, school_name=school_name)


def _humanize_actor_role(role_code: str | None) -> str:
    normalized = str(role_code or '').strip().lower()
    return {
        'guardian': 'responsavel',
        'student': 'aluno',
        'teacher': 'professor',
        'finance': 'financeiro',
        'coordinator': 'coordenacao',
        'admin': 'administracao',
    }.get(normalized, normalized or 'usuario autenticado')


def _compose_actor_identity_answer(actor: dict[str, Any] | None) -> str:
    if not actor:
        return (
            'Eu ainda nao consegui confirmar a identidade desta conta no Telegram. '
            'Se quiser, tente novamente em instantes ou refaca a vinculacao pelo portal.'
        )
    actor_name = str(actor.get('full_name', 'Usuario')).strip() or 'Usuario'
    role_label = _humanize_actor_role(actor.get('role_code'))
    students = _linked_students(actor)
    if not students:
        return (
            f'Voce esta falando aqui como {actor_name}, no perfil de {role_label}. '
            'No momento eu nao encontrei alunos vinculados a esta conta para consulta protegida.'
        )
    names = [str(student.get('full_name', 'Aluno')).strip() for student in students]
    names = [name for name in names if name]
    preview_names = ', '.join(names[:-1]) + f' e {names[-1]}' if len(names) > 1 else names[0]
    topics: list[str] = []
    for student in students:
        for topic in _student_capability_topics(student):
            if topic not in topics:
                topics.append(topic)
    topics_text = ', '.join(topics[:6]) if topics else 'informacoes escolares autorizadas'
    return (
        f'Voce esta falando aqui como {actor_name}, no perfil de {role_label}. '
        f'Sua conta esta vinculada a {preview_names}. '
        f'Por aqui eu consigo consultar {topics_text}, dentro das permissoes dessa vinculacao.'
    )


def _compose_account_context_answer(
    actor: dict[str, Any] | None,
    *,
    request_message: str,
    conversation_context: dict[str, Any] | None = None,
) -> str:
    if _is_children_overview_query(request_message, actor):
        overview = _compose_linked_students_overview_answer(actor)
        if overview:
            return overview
    if _is_access_scope_query(request_message) or _is_access_scope_repair_query(
        request_message,
        actor,
        conversation_context,
    ):
        return _compose_authenticated_access_scope_answer(actor)
    return _compose_actor_identity_answer(actor)


def _compose_student_focus_activation_answer(
    actor: dict[str, Any] | None,
    *,
    student_name: str | None,
) -> str | None:
    if not student_name:
        return None
    student = _student_focus_candidate(actor, student_name) or next(
        (
            item
            for item in _linked_students(actor)
            if _normalize_text(str(item.get('full_name', ''))) == _normalize_text(student_name)
        ),
        None,
    )
    topics = _student_capability_topics(student or {})
    if topics:
        topics_text = ', '.join(topics[:6])
        return (
            f'Perfeito, seguimos com {student_name}. '
            f'Posso te ajudar com {topics_text}. '
            'Se quiser, ja me diga o que voce quer ver primeiro.'
        )
    return (
        f'Perfeito, seguimos com {student_name}. '
        'Se quiser, me diga agora qual assunto voce quer ver sobre esse aluno.'
    )


def _compose_workflow_reset_answer() -> str:
    return (
        'Sem problema, vamos comecar do zero entao. '
        'Se voce quiser atendimento humano por aqui, me diga em uma frase curta qual e o assunto '
        'como financeiro, secretaria, matricula ou direcao, e eu sigo desse ponto.'
    )


def _compose_linked_student_repair_answer(actor: dict[str, Any] | None) -> str | None:
    students = _linked_students(actor)
    if not students:
        return None
    options = _format_student_options(students)
    return (
        'Entendi. Pelo que aparece nesta vinculacao do Telegram, eu so encontrei estes alunos liberados para consulta: '
        f'{options}. '
        'Se o aluno que voce esperava nao apareceu aqui, vale revisar a vinculacao no portal ou com a secretaria. '
        'Se quiser, eu posso continuar agora com qualquer um desses alunos.'
    )


def _should_use_student_administrative_status(
    actor: dict[str, Any] | None,
    message: str,
    *,
    conversation_context: dict[str, Any] | None,
) -> bool:
    students = _linked_students(actor)
    if not students:
        return False
    if _matching_students_in_text(students, message):
        return True
    if _explicit_unmatched_student_reference(
        students,
        message,
        conversation_context=conversation_context,
    ):
        return True
    normalized = _normalize_text(message)
    if any(_message_matches_term(normalized, term) for term in {'meu filho', 'minha filha', 'aluno', 'aluna'}):
        return True
    if not _is_follow_up_query(message):
        return False
    recent_focus = _recent_trace_focus(conversation_context) or {}
    if str(recent_focus.get('active_task', '') or '').strip() == 'admin:student_administrative_status':
        return True
    if _recent_slot_value(conversation_context, 'admin_attribute'):
        return True
    return any(
        _recent_slot_value(conversation_context, key)
        for key in ('academic_student_name', 'finance_student_name')
    )


def _recent_assistant_auth_context(conversation_context: dict[str, Any] | None) -> bool:
    for sender_type, content in reversed(_recent_message_lines(conversation_context)):
        if sender_type != 'assistant':
            continue
        normalized = _normalize_text(content)
        if any(
            _message_matches_term(normalized, term)
            for term in {
                'portal do aluno',
                'portal do responsavel',
                'portal do aluno ou responsavel',
                'portal autenticado',
                'vincular sua conta',
                'acessar o portal',
                'acesse o portal',
            }
        ):
            return True
    return False


def _recent_assistant_unmatched_student_context(
    conversation_context: dict[str, Any] | None,
) -> bool:
    for sender_type, content in reversed(_recent_message_lines(conversation_context)):
        if sender_type != 'assistant':
            continue
        normalized = _normalize_text(content)
        if (
            _message_matches_term(normalized, 'nao encontrei')
            and _message_matches_term(normalized, 'alunos vinculados')
        ):
            return True
    return False


def _is_access_scope_repair_query(
    message: str,
    actor: dict[str, Any] | None,
    conversation_context: dict[str, Any] | None,
) -> bool:
    if not _linked_students(actor):
        return False
    if not _recent_assistant_auth_context(conversation_context):
        return False
    normalized = _normalize_text(message)
    return any(
        _message_matches_term(normalized, term)
        for term in {
            'ja me autentiquei',
            'já me autentiquei',
            'ja estou autenticado',
            'já estou autenticado',
            'mas e meu filho',
            'mas é meu filho',
            'esta matriculado como meu filho',
            'está matriculado como meu filho',
        }
    )


def _is_linked_student_repair_query(
    message: str,
    conversation_context: dict[str, Any] | None,
) -> bool:
    if not _recent_assistant_unmatched_student_context(conversation_context):
        return False
    normalized = _normalize_text(message)
    return any(
        _message_matches_term(normalized, term)
        for term in {
            'mas e meu filho',
            'mas é meu filho',
            'esta matriculado como meu filho',
            'está matriculado como meu filho',
            'mas ele e meu filho',
            'mas ele é meu filho',
        }
    )


def _compose_contextual_clarify_answer(
    *,
    request_message: str,
    actor: dict[str, Any] | None,
    conversation_context: dict[str, Any] | None,
    slot_memory: ConversationSlotMemory,
) -> str | None:
    if slot_memory.pending_disambiguation == 'workflow_reset':
        return _compose_workflow_reset_answer()
    if slot_memory.pending_disambiguation == 'access_scope':
        return _compose_public_access_scope_answer(actor)
    if slot_memory.pending_disambiguation == 'linked_student_repair':
        return _compose_linked_student_repair_answer(actor)
    if slot_memory.pending_disambiguation == 'linked_students_overview':
        return _compose_linked_students_overview_answer(actor)
    if slot_memory.pending_disambiguation == 'student_reference_unmatched':
        students = _linked_students(actor)
        requested_name = _explicit_unmatched_student_reference(
            students,
            request_message,
            conversation_context=conversation_context,
        )
        if students and requested_name:
            return _compose_unmatched_student_reference_answer(
                requested_name=requested_name,
                students=students,
            )
    if slot_memory.pending_disambiguation == 'student_focus':
        student_name = slot_memory.academic_student_name or slot_memory.finance_student_name
        return _compose_student_focus_activation_answer(actor, student_name=student_name)
    if slot_memory.pending_disambiguation == 'student_selection':
        rescued_domain = _recent_student_disambiguation_domain(conversation_context)
        if rescued_domain is QueryDomain.finance:
            return 'Perfeito. Me diga qual aluno voce quer consultar no financeiro e eu sigo por esse caminho.'
        if rescued_domain is QueryDomain.academic:
            return 'Perfeito. Me diga qual aluno voce quer consultar e eu sigo por notas, faltas ou provas dele.'
    return None


def _eligible_students(actor: dict[str, Any] | None, *, capability: str) -> list[dict[str, Any]]:
    students = _linked_students(actor)
    if capability == 'academic':
        return [student for student in students if bool(student.get('can_view_academic', False))]
    if capability == 'finance':
        return [student for student in students if bool(student.get('can_view_finance', False))]
    return students


def _student_matches_text(student: dict[str, Any], text: str) -> bool:
    normalized_text = _normalize_text(text)
    full_name = str(student.get('full_name', ''))
    enrollment_code = str(student.get('enrollment_code', ''))
    normalized_name = _normalize_text(full_name)
    if normalized_name and normalized_name in normalized_text:
        return True
    if enrollment_code and enrollment_code.lower() in normalized_text:
        return True
    return False


def _student_name_tokens(student: dict[str, Any]) -> list[str]:
    full_name = _normalize_text(str(student.get('full_name', '')))
    return [token for token in re.findall(r'[a-z0-9]+', full_name) if len(token) >= 3]


def _is_student_reference_context_message(message: str) -> bool:
    normalized = _normalize_text(message)
    return any(
        _message_matches_term(normalized, term)
        for term in {
            'meu filho',
            'minha filha',
            'aluno',
            'aluna',
            'nota',
            'notas',
            'falta',
            'faltas',
            'prova',
            'provas',
            'boletim',
            'frequencia',
            'frequência',
            'matricula',
            'matrícula',
            'financeiro',
            'boleto',
            'boletos',
            'fatura',
            'faturas',
            'mensalidade',
            'pagamento',
            'vencimento',
            'contrato',
        }
    )


def _extract_explicit_student_reference_candidates(message: str) -> list[str]:
    normalized = _normalize_text(message)
    patterns = [
        (r'e\s+se\s+eu\s+perguntar\s+do\s+([a-z]{3,}(?:\s+[a-z]{3,}){0,2})', True),
        (r'(?:sobre o|sobre a|do|da)\s+([a-z]{3,}(?:\s+[a-z]{3,}){0,2})', True),
        (r'(?:meu filho|minha filha|aluno|aluna)\s+([a-z]{3,}(?:\s+[a-z]{3,}){0,2})', False),
        (r'(?:e o|e a)\s+([a-z]{3,}(?:\s+[a-z]{3,}){0,2})', True),
    ]
    candidates: list[str] = []
    stopwords = {
        'a',
        'agora',
        'ai',
        'aí',
        'autenticado',
        'autenticada',
        'autentiquei',
        'com',
        'da',
        'de',
        'do',
        'e',
        'eu',
        'falei',
        'falar',
        'ja',
        'já',
        'mas',
        'me',
        'meu',
        'meus',
        'minha',
        'minhas',
        'filho',
        'filha',
        'notas',
        'faltas',
        'financeiro',
        'boletos',
        'dados',
        'informacoes',
        'informações',
        'matricula',
        'matrícula',
        'documentacao',
        'documentação',
        'documentos',
        'pagamento',
        'pagamentos',
        'data',
        'datas',
        'proximo',
        'proxima',
        'próximo',
        'próxima',
        'vencimento',
        'vencimentos',
        'boleto',
        'contrato',
        'telefone',
        'email',
        'horario',
        'horário',
        'quero',
        'saber',
        'se',
        'perguntar',
        'pergunto',
        'sobre',
        'ta',
        'tá',
        'ver',
        'vinculado',
        'vinculada',
    }
    has_student_context = _is_student_reference_context_message(normalized)
    for pattern, requires_student_context in patterns:
        if requires_student_context and not has_student_context:
            continue
        for match in re.finditer(pattern, normalized):
            raw = match.group(1).strip(' ?!.,;:')
            tokens = [token for token in raw.split() if token not in stopwords]
            if not tokens:
                continue
            if len(tokens) == 1 and tokens[0] in stopwords:
                continue
            candidate = ' '.join(tokens[:3]).strip()
            if candidate and candidate not in candidates:
                candidates.append(candidate)
    return candidates


def _student_matches_candidate(student: dict[str, Any], candidate: str) -> bool:
    normalized_candidate = _normalize_text(candidate).strip()
    if not normalized_candidate:
        return False
    full_name = _normalize_text(str(student.get('full_name', '')))
    if not full_name:
        return False
    if normalized_candidate == full_name or normalized_candidate in full_name:
        return True
    return normalized_candidate in _student_name_tokens(student)


def _explicit_unmatched_student_reference(
    students: list[dict[str, Any]],
    message: str,
    *,
    conversation_context: dict[str, Any] | None = None,
) -> str | None:
    candidates = _extract_explicit_student_reference_candidates(message)
    if not candidates and isinstance(conversation_context, dict):
        recent_focus = _recent_trace_focus(conversation_context) or {}
        recent_active_task = str(recent_focus.get('active_task', '') or '').strip()
        recent_student_name = str(
            recent_focus.get('academic_student_name')
            or recent_focus.get('finance_student_name')
            or recent_focus.get('student_name')
            or ''
        ).strip()
        normalized = _normalize_text(message)
        followup_match = re.fullmatch(r'(?:e\s+d[oa]|e\s+se\s+eu\s+perguntar\s+d[oa])\s+([a-z]{3,}(?:\s+[a-z]{3,}){0,2})\??', normalized)
        if followup_match and (
            recent_active_task.startswith(('academic:', 'finance:', 'admin:'))
            or bool(recent_student_name)
        ):
            followup_candidate = followup_match.group(1).strip()
            if followup_candidate:
                candidates.append(followup_candidate)
    for candidate in candidates:
        if any(_student_matches_candidate(student, candidate) for student in students):
            continue
        return candidate
    return None


def _format_student_options(students: list[dict[str, Any]]) -> str:
    return ', '.join(
        f"{student.get('full_name', 'Aluno')} ({student.get('enrollment_code', 'sem codigo')})"
        for student in students
    )


def _compose_unmatched_student_reference_answer(
    *,
    requested_name: str,
    students: list[dict[str, Any]],
) -> str:
    options = _format_student_options(students)
    return (
        f'Hoje eu nao encontrei {requested_name.title()} entre os alunos vinculados a esta conta. '
        f'No momento, os alunos que aparecem aqui sao: {options}. '
        'Se quiser, me diga qual deles voce quer consultar.'
    )


def _matching_students_in_text(students: list[dict[str, Any]], text: str) -> list[dict[str, Any]]:
    matches = {
        str(student.get('student_id')): student
        for student in students
        if _student_matches_text(student, text)
    }
    if matches:
        return list(matches.values())

    normalized_text = _normalize_text(text)
    token_index: dict[str, list[dict[str, Any]]] = {}
    for student in students:
        for token in _student_name_tokens(student):
            token_index.setdefault(token, []).append(student)
    for token, owners in token_index.items():
        if len(owners) == 1 and _message_matches_term(normalized_text, token):
            owner = owners[0]
            matches[str(owner.get('student_id'))] = owner
    return list(matches.values())


def _recent_student_from_context(
    actor: dict[str, Any] | None,
    *,
    capability: str,
    conversation_context: dict[str, Any] | None,
) -> dict[str, Any] | None:
    students = _eligible_students(actor, capability=capability)
    if not students or not isinstance(conversation_context, dict):
        return None
    recent_focus = _recent_trace_focus(conversation_context) or {}
    recent_active_task = str(recent_focus.get('active_task', '') or '').strip()
    candidate_names: list[str] = []
    for key in ('finance_student_name', 'academic_student_name'):
        candidate_name = _recent_slot_value(conversation_context, key)
        if candidate_name and candidate_name not in candidate_names:
            candidate_names.append(candidate_name)
    if recent_active_task == 'admin:student_administrative_status':
        active_entity = str(recent_focus.get('active_entity', '') or '').strip()
        if active_entity and active_entity not in candidate_names and active_entity != 'aluno':
            candidate_names.append(active_entity)
    for candidate_name in candidate_names:
        matched_students = _matching_students_in_text(students, candidate_name)
        if len(matched_students) == 1:
            return matched_students[0]
    for _sender_type, content in reversed(_recent_message_lines(conversation_context)):
        matched_students = _matching_students_in_text(students, content)
        if len(matched_students) == 1:
            return matched_students[0]
    return None


def _select_linked_student(
    actor: dict[str, Any] | None,
    message: str,
    *,
    capability: str = 'academic',
    conversation_context: dict[str, Any] | None = None,
) -> tuple[dict[str, Any] | None, str | None]:
    students = _eligible_students(actor, capability=capability)
    if not students:
        return None, 'Nao encontrei um aluno vinculado a esta conta para essa consulta.'

    matched_students = _matching_students_in_text(students, message)
    if len(matched_students) == 1:
        return matched_students[0], None

    recent_student = _recent_student_from_context(
        actor,
        capability=capability,
        conversation_context=conversation_context,
    )

    unmatched_student_reference = _explicit_unmatched_student_reference(
        students,
        message,
        conversation_context=conversation_context,
    )
    if unmatched_student_reference:
        return None, _compose_unmatched_student_reference_answer(
            requested_name=unmatched_student_reference,
            students=students,
        )

    if len(students) == 1:
        return students[0], None

    if recent_student is not None and _is_follow_up_query(message):
        return recent_student, None

    options = _format_student_options(students)
    return None, f'Sua conta tem mais de um aluno vinculado. Diga qual aluno deseja consultar: {options}.'


def _available_subjects(summary: dict[str, Any]) -> dict[str, dict[str, str]]:
    available_subjects: dict[str, str] = {}
    available_codes: dict[str, str] = {}

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
            subject_code = row.get('subject_code')
            if isinstance(subject_code, str) and subject_code.strip():
                available_codes[normalized_subject] = subject_code.strip()
    return {
        normalized_subject: {
            'subject_name': subject_name,
            'subject_code': available_codes.get(normalized_subject, ''),
        }
        for normalized_subject, subject_name in available_subjects.items()
    }


def _subject_filter_from_text(text: str, summary: dict[str, Any]) -> str | None:
    lowered = _normalize_text(text)
    available_subjects = _available_subjects(summary)

    for normalized_subject in available_subjects:
        if normalized_subject in lowered:
            return normalized_subject
        for hint in SUBJECT_HINTS.get(normalized_subject, set()):
            if hint in lowered:
                return normalized_subject

    return None


def _detect_academic_focus_kind(message: str) -> str | None:
    if _contains_any(message, UPCOMING_ASSESSMENT_TERMS):
        return 'upcoming'
    if _contains_any(message, ATTENDANCE_TIMELINE_TERMS):
        return 'attendance_timeline'
    if _contains_any(message, ATTENDANCE_TERMS) and not _contains_any(message, GRADE_TERMS):
        return 'attendance'
    if _contains_any(message, GRADE_TERMS):
        return 'grades'
    return None


def _recent_subject_filter_from_context(
    message: str,
    summary: dict[str, Any],
    *,
    conversation_context: dict[str, Any] | None,
    focus_kind: str | None,
) -> str | None:
    if not isinstance(conversation_context, dict):
        return None

    for sender_type, content in reversed(_recent_message_lines(conversation_context)):
        if sender_type != 'user':
            continue
        if content.strip() == message.strip():
            continue
        if focus_kind == 'grades' and not _contains_any(content, GRADE_TERMS):
            continue
        if focus_kind in {'attendance', 'attendance_timeline'} and not (
            _contains_any(content, ATTENDANCE_TERMS) or _contains_any(content, ATTENDANCE_TIMELINE_TERMS)
        ):
            continue
        if focus_kind == 'upcoming' and not (
            _contains_any(content, UPCOMING_ASSESSMENT_TERMS) or _contains_any(content, GRADE_TERMS)
        ):
            continue
        subject_filter = _subject_filter_from_text(content, summary)
        if subject_filter:
            return subject_filter
    return None


def _detect_subject_filter(
    message: str,
    summary: dict[str, Any],
    *,
    conversation_context: dict[str, Any] | None = None,
    focus_kind: str | None = None,
) -> str | None:
    direct_filter = _subject_filter_from_text(message, summary)
    if direct_filter:
        return direct_filter
    return _recent_subject_filter_from_context(
        message,
        summary,
        conversation_context=conversation_context,
        focus_kind=focus_kind,
    )


def _subject_code_for_filter(summary: dict[str, Any], subject_filter: str | None) -> str | None:
    if not subject_filter:
        return None
    available_subjects = _available_subjects(summary)
    subject = available_subjects.get(subject_filter)
    if not isinstance(subject, dict):
        return None
    subject_code = str(subject.get('subject_code', '')).strip()
    return subject_code or None


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
    subject_rows: dict[str, dict[str, Any]] = {}
    for grade in grades:
        if not isinstance(grade, dict):
            continue
        subject_name = str(grade.get('subject_name', '') or '').strip()
        if not subject_name:
            continue
        subject_key = _normalize_text(subject_name)
        current = subject_rows.get(subject_key)
        if current is None:
            subject_rows[subject_key] = grade
            continue
        current_due = str(current.get('due_date', '') or '')
        candidate_due = str(grade.get('due_date', '') or '')
        if candidate_due and candidate_due > current_due:
            subject_rows[subject_key] = grade

    chosen = sorted(
        subject_rows.values(),
        key=lambda item: _normalize_text(str(item.get('subject_name', ''))),
    )[:8]
    if not chosen:
        chosen = [grade for grade in grades[:8] if isinstance(grade, dict)]

    lines = []
    for grade in chosen:
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


def _format_attendance_overview(summary: dict[str, Any]) -> list[str]:
    attendance = summary.get('attendance')
    if not isinstance(attendance, list) or not attendance:
        return ['- Ainda nao ha registros consolidados de frequencia neste recorte.']
    present = 0
    late = 0
    absent = 0
    minutes = 0
    for row in attendance:
        if not isinstance(row, dict):
            continue
        present += int(row.get('present_count', 0) or 0)
        late += int(row.get('late_count', 0) or 0)
        absent += int(row.get('absent_count', 0) or 0)
        minutes += int(row.get('absent_minutes', 0) or 0)
    return [
        f'- Presencas registradas: {present}',
        f'- Faltas registradas: {absent}',
        f'- Atrasos registrados: {late}',
        f'- Minutos somados de ausencia: {minutes}',
    ]


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
    if any(_message_matches_term(lowered, term) for term in FINANCE_NEXT_DUE_TERMS):
        return None
    if any(term in lowered for term in FINANCE_OVERDUE_TERMS):
        return {'overdue'}
    if any(term in lowered for term in FINANCE_PAID_TERMS):
        return {'paid'}
    if any(term in lowered for term in FINANCE_OPEN_TERMS):
        return {'open', 'overdue'}
    return None


def _wants_finance_count_summary(message: str) -> bool:
    normalized = _normalize_text(message)
    return any(
        _message_matches_term(normalized, term)
        for term in {'quantas', 'quantos', 'qtd', 'quantidade', 'tenho quantas', 'tenho quantos'}
    )


def _wants_upcoming_assessments(message: str) -> bool:
    return _contains_any(message, UPCOMING_ASSESSMENT_TERMS)


def _wants_attendance_timeline(message: str) -> bool:
    return _contains_any(message, ATTENDANCE_TIMELINE_TERMS)


def _mentions_personal_admin_status(message: str) -> bool:
    normalized = _normalize_text(message)
    has_personal_anchor = any(
        _message_matches_term(normalized, term)
        for term in {
            'meu',
            'minha',
            'meus',
            'minhas',
            'estou',
            'cadastro',
            'documentacao',
            'documentação',
            'dados cadastrais',
            'atualizada',
            'atualizado',
            'completa',
            'completo',
        }
    )
    return has_personal_anchor and any(
        _message_matches_term(normalized, term) for term in PERSONAL_ADMIN_STATUS_TERMS
    )


def _wants_profile_update_guidance(message: str) -> bool:
    return _contains_any(message, PERSONAL_PROFILE_UPDATE_TERMS)


def _humanize_invoice_status(status: str | None) -> str:
    normalized = _normalize_text(status or '')
    mapping = {
        'paid': 'paga',
        'open': 'em aberto',
        'overdue': 'vencida',
        'cancelled': 'cancelada',
    }
    return mapping.get(normalized, status or 'desconhecido')


def _finance_empty_lines(status_filter: set[str] | None = None) -> list[str]:
    if status_filter == {'paid'}:
        return ['- Nao encontrei faturas pagas neste recorte.']
    if status_filter == {'overdue'}:
        return ['- Hoje nao ha faturas vencidas neste recorte.']
    if status_filter == {'open', 'overdue'}:
        return ['- Hoje nao ha faturas em aberto ou vencidas neste recorte.']
    return ['- Nao encontrei faturas registradas neste recorte.']


def _format_invoice_lines(
    invoices: list[dict[str, Any]],
    *,
    status_filter: set[str] | None = None,
) -> list[str]:
    if not invoices:
        return _finance_empty_lines(status_filter)
    lines = []
    for invoice in invoices[:6]:
        lines.append(
            '- {reference_month}: vencimento {due_date}, status {status}, valor {amount_due}'.format(
                reference_month=invoice.get('reference_month', '---'),
                due_date=invoice.get('due_date', '---'),
                status=_humanize_invoice_status(str(invoice.get('status', 'desconhecido'))),
                amount_due=invoice.get('amount_due', '0.00'),
            )
        )
    return lines


def _parse_invoice_amount(value: Any) -> float:
    raw = str(value or '').strip()
    if not raw:
        return 0.0
    raw = raw.replace('R$', '').replace(' ', '')
    if ',' in raw and '.' in raw:
        raw = raw.replace('.', '').replace(',', '.')
    elif ',' in raw:
        raw = raw.replace(',', '.')
    try:
        return float(raw)
    except ValueError:
        return 0.0


def _format_upcoming_assessments(summary: dict[str, Any]) -> list[str]:
    assessments = summary.get('assessments')
    if not isinstance(assessments, list) or not assessments:
        return ['- Nao encontrei proximas avaliacoes registradas neste recorte.']
    lines = []
    for assessment in assessments[:6]:
        if not isinstance(assessment, dict):
            continue
        lines.append(
            '- {subject_name} - {item_title}: {due_date}'.format(
                subject_name=assessment.get('subject_name', 'Disciplina'),
                item_title=assessment.get('item_title', 'Avaliacao'),
                due_date=assessment.get('due_date', 'data nao informada'),
            )
        )
    return lines or ['- Nao encontrei proximas avaliacoes registradas neste recorte.']


def _format_attendance_timeline(summary: dict[str, Any]) -> list[str]:
    records = summary.get('records')
    if not isinstance(records, list) or not records:
        return ['- Nao encontrei faltas ou registros recentes com data neste recorte.']
    lines = []
    for record in records[:8]:
        if not isinstance(record, dict):
            continue
        status = str(record.get('status', 'nao informado')).lower()
        status_label = {
            'present': 'presenca',
            'late': 'atraso',
            'absent': 'falta',
        }.get(status, status)
        suffix = ''
        minutes_absent = int(record.get('minutes_absent', 0) or 0)
        if minutes_absent > 0:
            suffix = f' ({minutes_absent} min)'
        lines.append(
            '- {record_date} - {subject_name}: {status_label}{suffix}'.format(
                record_date=record.get('record_date', 'data nao informada'),
                subject_name=record.get('subject_name', 'Disciplina'),
                status_label=status_label,
                suffix=suffix,
            )
        )
    return lines or ['- Nao encontrei faltas ou registros recentes com data neste recorte.']


def _administrative_checklist_lines(summary: dict[str, Any]) -> list[str]:
    checklist = summary.get('checklist')
    if not isinstance(checklist, list) or not checklist:
        return ['- Nao encontrei itens administrativos detalhados para este cadastro.']
    lines: list[str] = []
    for item in checklist:
        if not isinstance(item, dict):
            continue
        label = str(item.get('label', 'Item'))
        status = ADMIN_STATUS_LABELS.get(str(item.get('status', '')).lower(), str(item.get('status', 'nao informado')))
        notes = str(item.get('notes', '')).strip()
        line = f'- {label}: {status}'
        if notes:
            line += f'. {notes}'
        lines.append(line)
    return lines or ['- Nao encontrei itens administrativos detalhados para este cadastro.']


def _format_administrative_status(
    summary: dict[str, Any],
    *,
    profile_update: bool,
    requested_attribute: str | None = None,
) -> list[str]:
    if requested_attribute == 'next_step':
        next_step = str(summary.get('next_step') or '').strip()
        if next_step:
            return [f'Hoje, o proximo passo do seu cadastro e este: {next_step}']
        return ['Hoje eu nao encontrei um proximo passo pendente no seu cadastro.']
    if requested_attribute == 'status':
        overall_status = ADMIN_STATUS_LABELS.get(str(summary.get('overall_status', '')).lower(), 'em analise')
        return [f'Situacao administrativa do seu cadastro hoje: {overall_status}.']
    if requested_attribute == 'email':
        email = str(summary.get('profile_email') or 'nao informado')
        return [
            f'Hoje o email cadastral registrado e {email}.',
            'Se precisar atualizar esse dado, o caminho mais seguro continua sendo a secretaria escolar, com confirmacao do titular.',
        ]
    if requested_attribute == 'phone':
        phone = str(summary.get('profile_phone') or 'nao informado')
        return [
            f'O telefone cadastral atual e {phone}.',
            'Se precisar atualizar esse dado, o caminho mais seguro continua sendo a secretaria escolar, com confirmacao do titular.',
        ]
    if requested_attribute == 'documents':
        overall_status = ADMIN_STATUS_LABELS.get(str(summary.get('overall_status', '')).lower(), 'em analise')
        lines = [
            f'Situacao administrativa do seu cadastro hoje: {overall_status}.',
            'Situacao documental do seu cadastro hoje:',
        ]
        lines.extend(_administrative_checklist_lines(summary))
        next_step = str(summary.get('next_step') or '').strip()
        if next_step:
            lines.append(f'Proximo passo: {next_step}')
        return lines
    if profile_update:
        email = str(summary.get('profile_email') or 'nao informado')
        phone = str(summary.get('profile_phone') or 'nao informado')
        lines = [
            f'Hoje o email cadastral registrado e {email}.',
            f'O telefone cadastral atual e {phone}.',
            'Para alterar email ou telefone, o caminho mais seguro e secretaria escolar, porque essa atualizacao ainda exige confirmacao do titular.',
            'Se quiser, eu tambem posso te dizer qual canal da secretaria faz essa tratativa mais rapido.',
        ]
        return lines

    overall_status = ADMIN_STATUS_LABELS.get(str(summary.get('overall_status', '')).lower(), 'em analise')
    lines = [f'Situacao administrativa do seu cadastro hoje: {overall_status}.']
    lines.extend(_administrative_checklist_lines(summary))
    next_step = str(summary.get('next_step') or '').strip()
    if next_step:
        lines.append(f'Proximo passo: {next_step}')
    return lines


def _format_student_administrative_status(
    summary: dict[str, Any],
    *,
    requested_attribute: str | None = None,
) -> list[str]:
    student_name = str(summary.get('student_name') or 'o aluno').strip() or 'o aluno'
    overall_status = ADMIN_STATUS_LABELS.get(str(summary.get('overall_status', '')).lower(), 'em analise')
    enrollment_code = str(summary.get('enrollment_code') or '').strip()
    guardian_name = str(summary.get('guardian_name') or '').strip()

    if requested_attribute == 'next_step':
        next_step = str(summary.get('next_step') or '').strip()
        if next_step:
            return [f'Hoje, o proximo passo da documentacao de {student_name} e este: {next_step}']
        return [f'Hoje eu nao encontrei um proximo passo pendente na documentacao de {student_name}.']
    if requested_attribute == 'status':
        return [f'Situacao documental de {student_name} hoje: {overall_status}.']
    if requested_attribute == 'documents':
        lines = [f'Situacao documental de {student_name} hoje: {overall_status}.']
        lines.extend(_administrative_checklist_lines(summary))
        next_step = str(summary.get('next_step') or '').strip()
        if next_step:
            lines.append(f'Proximo passo: {next_step}')
        return lines

    lines = [f'Situacao documental de {student_name} hoje: {overall_status}.']
    if enrollment_code:
        lines.append(f'- Matricula: {enrollment_code}')
    if guardian_name:
        lines.append(f'- Responsavel vinculado: {guardian_name}')
    lines.extend(_administrative_checklist_lines(summary))
    next_step = str(summary.get('next_step') or '').strip()
    if next_step:
        lines.append(f'Proximo passo: {next_step}')
    return lines


def _select_relevant_invoice(
    summary: dict[str, Any],
    *,
    status_filter: set[str] | None,
    prefer_open: bool,
) -> dict[str, Any] | None:
    invoices = _filter_invoice_rows(summary, status_filter=status_filter)
    if not invoices:
        invoices = _filter_invoice_rows(summary, status_filter=None)
    if not invoices:
        return None
    if prefer_open:
        for invoice in invoices:
            if not isinstance(invoice, dict):
                continue
            if str(invoice.get('status', '')).lower() in {'open', 'overdue'}:
                return invoice
    for invoice in invoices:
        if isinstance(invoice, dict):
            return invoice
    return None


def _select_next_due_invoice(
    summary: dict[str, Any],
    *,
    status_filter: set[str] | None,
) -> dict[str, Any] | None:
    open_invoices = _filter_invoice_rows(summary, status_filter={'open'})
    overdue_invoices = _filter_invoice_rows(summary, status_filter={'overdue'})
    candidate_pool = open_invoices or overdue_invoices
    if not candidate_pool:
        return None

    def _invoice_sort_key(invoice: dict[str, Any]) -> tuple[bool, date, str]:
        due_date = _parse_iso_date_value(invoice.get('due_date'))
        return (
            due_date is None,
            due_date or date.max,
            str(invoice.get('reference_month', '')),
        )

    for invoice in sorted(
        (invoice for invoice in candidate_pool if isinstance(invoice, dict)),
        key=_invoice_sort_key,
    ):
        return invoice
    return None


def _compose_academic_attribute_answer(
    summary: dict[str, Any],
    *,
    attribute_request: ProtectedAttributeRequest,
    student_name: str,
    message: str | None = None,
) -> str:
    if attribute_request.attribute == 'enrollment_code':
        enrollment_code = str(summary.get('enrollment_code', '') or '').strip()
        class_name = str(summary.get('class_name', '') or 'turma nao informada').strip()
        if enrollment_code:
            return (
                f'A matricula de {student_name} e {enrollment_code}. '
                f'Turma atual: {class_name}.'
            )
        return (
            f'Nao encontrei o codigo de matricula de {student_name} '
            'neste recorte autorizado.'
        )
    if attribute_request.attribute == 'attendance':
        normalized_message = _normalize_text(message or '')
        if _message_matches_term(normalized_message, 'frequencia') and not _contains_any(normalized_message, {'falta', 'faltas'}):
            lines = [f'Panorama de frequencia de {student_name}:']
            lines.append('Resumo geral:')
            lines.extend(_format_attendance_overview(summary))
            return '\n'.join(lines)
        attendance = summary.get('attendance')
        absent = 0
        late = 0
        if isinstance(attendance, list):
            for row in attendance:
                if not isinstance(row, dict):
                    continue
                absent += int(row.get('absent_count', 0) or 0)
                late += int(row.get('late_count', 0) or 0)
        return (
            f'No recorte de faltas de {student_name}, eu encontrei {absent} falta(s) '
            f'e {late} atraso(s).'
        )
    if attribute_request.attribute == 'grades':
        lines = [f'Notas de {student_name}:']
        lines.extend(_format_grades(summary))
        return '\n'.join(lines)
    return f'Nao encontrei um atributo academico suportado para {student_name} neste recorte.'


def _compose_finance_attribute_answer(
    summary: dict[str, Any],
    *,
    attribute_request: ProtectedAttributeRequest,
    status_filter: set[str] | None,
    wants_second_copy: bool,
) -> str:
    student_name = str(summary.get('student_name', 'Aluno')).strip() or 'Aluno'
    if attribute_request.attribute == 'contract_code':
        contract_code = str(summary.get('contract_code', '') or '').strip()
        if contract_code:
            return f'O codigo do contrato financeiro de {student_name} e {contract_code}.'
        return f'Nao encontrei o codigo de contrato de {student_name} neste recorte.'

    if attribute_request.attribute == 'next_due':
        invoice = _select_next_due_invoice(summary, status_filter=status_filter)
        if not isinstance(invoice, dict):
            fallback_invoices = [
                item for item in (summary.get('invoices') or [])
                if isinstance(item, dict)
            ]
            if fallback_invoices:
                fallback_invoices.sort(
                    key=lambda item: (
                        str(item.get('status', '')).lower() not in {'open', 'overdue'},
                        str(item.get('due_date', '')),
                    )
                )
                invoice = fallback_invoices[0]
        if not isinstance(invoice, dict):
            return f'Hoje nao encontrei um proximo pagamento pendente de {student_name}.'
        reference_month = str(invoice.get('reference_month', '') or '---').strip()
        due_date = _format_public_date_text(invoice.get('due_date'))
        amount_due = str(invoice.get('amount_due', '0.00')).strip() or '0.00'
        status = str(invoice.get('status', '')).lower()
        status_label = _humanize_invoice_status(status or 'desconhecido')
        if status == 'open':
            return (
                f'O proximo pagamento de {student_name} hoje e a referencia {reference_month}, '
                f'com vencimento em {due_date} e valor {amount_due}. '
                f'Status atual: {status_label}.'
            )
        return (
            f'Hoje a cobranca pendente mais imediata de {student_name} e a referencia {reference_month}, '
            f'com vencimento em {due_date} e valor {amount_due}. '
            f'Status atual: {status_label}.'
        )

    if attribute_request.attribute == 'open_amount':
        invoices = _filter_invoice_rows(summary, status_filter=status_filter or {'open', 'overdue'})
        outstanding_invoices = [
            invoice
            for invoice in invoices
            if str(invoice.get('status', '')).lower() in {'open', 'overdue'}
        ]
        total_outstanding = sum(_parse_invoice_amount(invoice.get('amount_due')) for invoice in outstanding_invoices)
        if total_outstanding <= 0:
            return f'Hoje nao encontrei valor em aberto para {student_name} neste recorte.'
        return (
            f'Hoje o valor total em aberto de {student_name} neste recorte e R$ {total_outstanding:.2f}, '
            f'distribuido em {len(outstanding_invoices)} fatura(s).'
        )

    if attribute_request.attribute == 'invoice_id':
        invoice = _select_relevant_invoice(
            summary,
            status_filter=status_filter,
            prefer_open=wants_second_copy or status_filter in ({'open', 'overdue'}, {'overdue'}),
        )
        if not isinstance(invoice, dict):
            return (
                f'Hoje nao encontrei uma fatura compativel de {student_name} '
                'para informar o identificador.'
            )
        invoice_id = str(invoice.get('invoice_id', '') or '').strip()
        reference_month = str(invoice.get('reference_month', '') or '---').strip()
        due_date = str(invoice.get('due_date', '') or '---').strip()
        status_label = _humanize_invoice_status(str(invoice.get('status', 'desconhecido')))
        lines = [
            f'O identificador da fatura mais relevante de {student_name} hoje e {invoice_id}.',
            f'- Referencia: {reference_month}',
            f'- Vencimento: {due_date}',
            f'- Status: {status_label}',
        ]
        if wants_second_copy:
            lines.append(
                'Se quiser a segunda via, eu sigo usando esse identificador como referencia da fatura.'
            )
        return '\n'.join(lines)

    return f'Nao encontrei um atributo financeiro suportado para {student_name} neste recorte.'


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


def _build_protected_record_specialists(*, preview: Any, role_code: str) -> tuple[InternalSpecialistPlan, ...]:
    if preview.classification.domain is QueryDomain.institution and {
        'get_administrative_status',
        'get_student_administrative_status',
        'get_actor_identity_context',
    } & set(preview.selected_tools):
        return (
            InternalSpecialistPlan(
                name='protected_records',
                purpose='consultas protegidas de identidade da conta, cadastro e documentacao por aluno vinculado',
                tool_names=tuple(
                    tool_name
                    for tool_name in (
                        'get_actor_identity_context',
                        'get_administrative_status',
                        'get_student_administrative_status',
                    )
                    if tool_name in set(preview.selected_tools)
                ),
            ),
        )

    if preview.classification.domain is QueryDomain.academic and role_code == 'teacher':
        return (
            InternalSpecialistPlan(
                name='protected_records',
                purpose='consultas protegidas de agenda, turmas e disciplinas docentes',
                tool_names=('get_teacher_schedule',),
            ),
        )

    if preview.classification.domain is QueryDomain.academic:
        return (
            InternalSpecialistPlan(
                name='protected_records',
                purpose='consultas protegidas de notas, frequencia e vida academica por aluno vinculado',
                tool_names=(
                    'get_student_academic_summary',
                    'get_student_upcoming_assessments',
                    'get_student_attendance_timeline',
                ),
            ),
        )

    if preview.classification.domain is QueryDomain.finance:
        return (
            InternalSpecialistPlan(
                name='protected_records',
                purpose='consultas protegidas de faturas, contrato e situacao financeira por aluno vinculado',
                tool_names=(
                    'get_student_financial_summary',
                    'get_administrative_status',
                ),
            ),
        )

    return ()


async def _execute_teacher_protected_specialist(
    *,
    settings: Any,
    request: MessageResponseRequest,
    actor: dict[str, Any],
) -> str:
    if request.telegram_chat_id is None:
        return _compose_structured_deny(actor)

    message = request.message
    normalized_message = _normalize_text(message)
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


async def _execute_protected_records_specialist(
    *,
    settings: Any,
    request: MessageResponseRequest,
    preview: Any,
    actor: dict[str, Any],
    conversation_context: dict[str, Any] | None = None,
) -> str:
    if request.telegram_chat_id is None:
        return _compose_structured_deny(actor)

    message = request.message
    normalized_message = _normalize_text(message)
    wants_admin_status = _mentions_personal_admin_status(message)
    wants_profile_update = _wants_profile_update_guidance(message)
    requested_admin_attribute = _detect_admin_attribute_request(
        message,
        conversation_context=conversation_context,
    )
    if _is_access_scope_query(message) or _is_access_scope_repair_query(
        message,
        actor,
        conversation_context,
    ):
        return _compose_authenticated_access_scope_answer(actor)
    if _is_actor_identity_query(message):
        return _compose_actor_identity_answer(actor)
    if _is_public_document_submission_query(message):
        if _message_matches_term(normalized_message, 'fax'):
            return (
                'Hoje a escola nao utiliza fax para envio de documentos. '
                'Para isso, use portal institucional, email da secretaria, secretaria presencial.'
            )
        if _message_matches_term(normalized_message, 'telegrama'):
            return (
                'Hoje a escola nao publica telegrama como canal valido para documentos. '
                'Para isso, use portal institucional, email da secretaria, secretaria presencial.'
            )
        if _message_matches_term(normalized_message, 'caixa postal'):
            return (
                'Hoje a escola nao trabalha com caixa postal para esse tipo de envio. '
                'Para documentos, use portal institucional, email da secretaria, secretaria presencial.'
            )
        return (
            'Para enviar documentos hoje, use portal institucional, email da secretaria ou secretaria presencial.'
        )
    should_force_student_admin_path = (
        requested_admin_attribute is not None
        and _effective_finance_attribute_request(
            message,
            conversation_context=conversation_context,
        )
        is None
        and _should_use_student_administrative_status(
            actor,
            message,
            conversation_context=conversation_context,
        )
    )
    linked_students = _linked_students(actor)
    unmatched_student_name = _explicit_unmatched_student_reference(
        linked_students,
        message,
        conversation_context=conversation_context,
    )
    if linked_students and unmatched_student_name:
        return _compose_unmatched_student_reference_answer(
            requested_name=unmatched_student_name,
            students=linked_students,
        )

    if preview.classification.domain is QueryDomain.institution and 'get_actor_identity_context' in preview.selected_tools:
        return _compose_account_context_answer(
            actor,
            request_message=message,
            conversation_context=conversation_context,
        )

    if should_force_student_admin_path:
        preview.classification = IntentClassification(
            domain=QueryDomain.institution,
            access_tier=AccessTier.authenticated,
            confidence=0.9,
            reason='follow-up administrativo de aluno exige service deterministico e estado tipado',
        )
        preview.selected_tools = ['get_administrative_status', 'get_student_administrative_status']
        return await _compose_student_administrative_status_answer(
            settings=settings,
            request=request,
            actor=actor,
            message=message,
            conversation_context=conversation_context,
            requested_attribute=requested_admin_attribute,
        )

    if preview.classification.domain is QueryDomain.institution and (
        'get_administrative_status' in preview.selected_tools
        or 'get_student_administrative_status' in preview.selected_tools
    ):
        if (
            'get_student_administrative_status' in preview.selected_tools
            and _should_use_student_administrative_status(
                actor,
                message,
                conversation_context=conversation_context,
            )
        ):
            return await _compose_student_administrative_status_answer(
                settings=settings,
                request=request,
                actor=actor,
                message=message,
                conversation_context=conversation_context,
                requested_attribute=requested_admin_attribute,
            )

        payload, status_code = await _api_core_get(
            settings=settings,
            path='/v1/actors/me/administrative-status',
            params={'telegram_chat_id': request.telegram_chat_id},
        )
        if status_code == 403:
            return 'Seu perfil nao tem permissao para consultar esse status administrativo.'
        if status_code != 200 or payload is None:
            return 'Nao consegui consultar seu cadastro administrativo agora. Tente novamente em instantes.'

        summary = payload.get('summary', {})
        if not isinstance(summary, dict):
            return 'Nao consegui interpretar o retorno administrativo desta consulta.'
        return '\n'.join(
            _format_administrative_status(
                summary,
                profile_update=wants_profile_update,
                requested_attribute=requested_admin_attribute,
            )
        )

    if preview.classification.domain is QueryDomain.finance:
        requested_status = _effective_finance_status_filter(
            message,
            conversation_context=conversation_context,
        )
        finance_attribute_request = _effective_finance_attribute_request(
            message,
            conversation_context=conversation_context,
        )
        wants_second_copy = _wants_finance_second_copy(
            message,
            conversation_context=conversation_context,
        )
        include_admin_section = 'get_administrative_status' in preview.selected_tools and (
            wants_admin_status or wants_profile_update
        )
        finance_students = _eligible_students(actor, capability='finance')
        if len(finance_students) > 1:
            student, clarification = _select_linked_student(
                actor,
                message,
                capability='finance',
                conversation_context=conversation_context,
            )
            if student is None and clarification is not None:
                if finance_attribute_request is not None:
                    return clarification
                summaries: list[dict[str, Any]] = []
                for candidate in finance_students:
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
                    for student in finance_students
                ):
                    lines = ['Resumo financeiro das contas vinculadas:']
                    total_open = 0
                    total_overdue = 0
                    filtered_any = False
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
                        if filtered_invoices:
                            filtered_any = True
                            for invoice_line in _format_invoice_lines(filtered_invoices, status_filter=requested_status)[:2]:
                                lines.append(f'  {invoice_line[2:]}' if invoice_line.startswith('- ') else invoice_line)
                    lines.insert(1, f'- Total de faturas em aberto: {total_open}')
                    lines.insert(2, f'- Total de faturas vencidas: {total_overdue}')
                    if not filtered_any:
                        lines.extend(_finance_empty_lines(requested_status))
                    if wants_second_copy:
                        lines.append(
                            'A emissao automatica de segunda via ainda entra na proxima etapa; '
                            'por enquanto eu consigo informar a situacao das faturas.'
                        )
                    if include_admin_section:
                        admin_payload, admin_status_code = await _api_core_get(
                            settings=settings,
                            path='/v1/actors/me/administrative-status',
                            params={'telegram_chat_id': request.telegram_chat_id},
                        )
                        admin_summary = admin_payload.get('summary') if isinstance(admin_payload, dict) else None
                        if admin_status_code == 200 and isinstance(admin_summary, dict):
                            lines.append('')
                            lines.append('Cadastro e documentacao:')
                            lines.extend(
                                _format_administrative_status(
                                    admin_summary,
                                    profile_update=wants_profile_update,
                                    requested_attribute=requested_admin_attribute,
                                )
                            )
                    return '\n'.join(lines)

    requested_capability = 'finance' if preview.classification.domain is QueryDomain.finance else 'academic'
    student, clarification = _select_linked_student(
        actor,
        message,
        capability=requested_capability,
        conversation_context=conversation_context,
    )
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

        academic_attribute_request = _effective_academic_attribute_request(
            message,
            conversation_context=conversation_context,
        )
        if academic_attribute_request is not None:
            return _compose_academic_attribute_answer(
                summary,
                attribute_request=academic_attribute_request,
                student_name=student_name,
                message=message,
            )

        focus_kind = _detect_academic_focus_kind(message)
        term_filter = _extract_term_filter(message)
        context_focus = focus_kind
        if focus_kind == 'upcoming' and not _is_follow_up_query(message):
            context_focus = None
        subject_filter = _detect_subject_filter(
            message,
            summary,
            conversation_context=conversation_context,
            focus_kind=context_focus,
        )
        subject_code = _subject_code_for_filter(summary, subject_filter)

        if _wants_upcoming_assessments(message):
            upcoming_payload, upcoming_status_code = await _api_core_get(
                settings=settings,
                path=f'/v1/students/{student_id}/upcoming-assessments',
                params={
                    'telegram_chat_id': request.telegram_chat_id,
                    **({'subject_code': subject_code} if subject_code else {}),
                },
            )
            if upcoming_status_code == 403:
                return 'Seu perfil nao tem permissao para consultar as proximas avaliacoes deste aluno.'
            if upcoming_status_code != 200 or upcoming_payload is None:
                return 'Nao consegui consultar as proximas avaliacoes agora. Tente novamente em instantes.'
            upcoming_summary = upcoming_payload.get('summary', {})
            if not isinstance(upcoming_summary, dict):
                return 'Nao consegui interpretar o retorno das proximas avaliacoes.'
            lines = [
                f"Proximas avaliacoes de {student_name}:",
                f"- Turma: {summary.get('class_name', 'nao informada')}",
            ]
            if subject_filter:
                lines.append(f"- Disciplina filtrada: {subject_filter.title()}")
            lines.extend(_format_upcoming_assessments(upcoming_summary))
            return '\n'.join(lines)

        if _wants_attendance_timeline(message):
            timeline_payload, timeline_status_code = await _api_core_get(
                settings=settings,
                path=f'/v1/students/{student_id}/attendance-timeline',
                params={
                    'telegram_chat_id': request.telegram_chat_id,
                    **({'subject_code': subject_code} if subject_code else {}),
                },
            )
            if timeline_status_code == 403:
                return 'Seu perfil nao tem permissao para consultar as faltas detalhadas deste aluno.'
            if timeline_status_code != 200 or timeline_payload is None:
                return 'Nao consegui consultar as faltas com data agora. Tente novamente em instantes.'
            timeline_summary = timeline_payload.get('summary', {})
            if not isinstance(timeline_summary, dict):
                return 'Nao consegui interpretar o retorno detalhado de frequencia.'
            lines = [
                f'Registros de frequencia de {student_name}:',
                f"- Turma: {summary.get('class_name', 'nao informada')}",
            ]
            if subject_filter:
                lines.append(f"- Disciplina filtrada: {subject_filter.title()}")
            lines.extend(_format_attendance_timeline(timeline_summary))
            return '\n'.join(lines)

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
            if _message_matches_term(_normalize_text(message), 'frequencia') and not _contains_any(message, {'falta', 'faltas'}):
                lines[0] = f'Panorama de frequencia de {student_name}:'
                lines.append('Resumo geral:')
                lines.extend(_format_attendance_overview(filtered_summary))
            else:
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

    requested_status = _effective_finance_status_filter(
        message,
        conversation_context=conversation_context,
    )
    wants_second_copy = _wants_finance_second_copy(
        message,
        conversation_context=conversation_context,
    )
    finance_attribute_request = _effective_finance_attribute_request(
        message,
        conversation_context=conversation_context,
    )
    if finance_attribute_request is not None:
        return _compose_finance_attribute_answer(
            summary,
            attribute_request=finance_attribute_request,
            status_filter=requested_status,
            wants_second_copy=wants_second_copy,
        )
    filtered_invoices = _filter_invoice_rows(summary, status_filter=requested_status)
    if _wants_finance_count_summary(message) and requested_status == {'overdue'}:
        overdue_count = len(filtered_invoices)
        if overdue_count == 0:
            return f'Hoje {student_name} nao tem mensalidades vencidas.'
        plural = 'mensalidade vencida' if overdue_count == 1 else 'mensalidades vencidas'
        return f'Hoje {student_name} tem {overdue_count} {plural}.'
    include_admin_section = 'get_administrative_status' in preview.selected_tools and (
        wants_admin_status or wants_profile_update
    )
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
    lines.extend(_format_invoice_lines(filtered_invoices, status_filter=requested_status))
    if wants_second_copy:
        lines.append(
            'A emissao automatica de segunda via ainda entra na proxima etapa; '
            'por enquanto eu consigo informar a situacao e os vencimentos.'
        )
    if include_admin_section:
        admin_payload, admin_status_code = await _api_core_get(
            settings=settings,
            path='/v1/actors/me/administrative-status',
            params={'telegram_chat_id': request.telegram_chat_id},
        )
        admin_summary = admin_payload.get('summary') if isinstance(admin_payload, dict) else None
        if admin_status_code == 200 and isinstance(admin_summary, dict):
            lines.append('')
            lines.append('Cadastro e documentacao:')
            lines.extend(
                _format_administrative_status(
                    admin_summary,
                    profile_update=wants_profile_update,
                    requested_attribute=requested_admin_attribute,
                )
            )
    return '\n'.join(lines)


def _build_visual_specialists(*, preview: Any, message: str) -> tuple[InternalSpecialistPlan, ...]:
    if not _wants_visual_response(message):
        return ()

    if preview.classification.domain is QueryDomain.institution:
        return (
            InternalSpecialistPlan(
                name='visual',
                purpose='graficos publicos institucionais e indicadores visuais',
                tool_names=('build_public_kpi_visual',),
            ),
        )

    if preview.classification.domain is QueryDomain.academic:
        return (
            InternalSpecialistPlan(
                name='visual',
                purpose='graficos academicos sintetizados a partir do resumo do aluno',
                tool_names=('build_academic_visual',),
            ),
        )

    if preview.classification.domain is QueryDomain.finance:
        return (
            InternalSpecialistPlan(
                name='visual',
                purpose='graficos financeiros sintetizados a partir do resumo do aluno',
                tool_names=('build_finance_visual',),
            ),
        )

    return ()


def _compose_structured_deny(actor: dict[str, Any] | None) -> str:
    if actor is None:
        return (
            'Essa consulta depende de autenticacao e vinculo da sua conta no Telegram. '
            'Use o portal da escola para gerar o codigo de vinculacao e depois envie o comando '
            '`/start link_<codigo>` ao bot.'
        )
    return 'Nao consegui autorizar essa consulta neste contexto. Se precisar, use o portal autenticado da escola.'


async def _compose_student_administrative_status_answer(
    *,
    settings: Any,
    request: MessageResponseRequest,
    actor: dict[str, Any],
    message: str,
    conversation_context: dict[str, Any] | None,
    requested_attribute: str | None,
) -> str:
    student, clarification = _select_linked_student(
        actor,
        message,
        capability='linked',
        conversation_context=conversation_context,
    )
    if clarification is not None:
        return clarification
    if student is None:
        return 'Nao consegui identificar o aluno desta consulta administrativa no Telegram.'
    student_id = student.get('student_id')
    if not isinstance(student_id, str):
        return 'Nao consegui identificar o aluno desta consulta administrativa no Telegram.'
    payload, status_code = await _api_core_get(
        settings=settings,
        path=f'/v1/students/{student_id}/administrative-status',
        params={'telegram_chat_id': request.telegram_chat_id},
    )
    if status_code == 403:
        return 'Seu perfil nao tem permissao para consultar a documentacao desse aluno.'
    if status_code != 200 or payload is None:
        return 'Nao consegui consultar a documentacao desse aluno agora. Tente novamente em instantes.'

    summary = payload.get('summary', {})
    if not isinstance(summary, dict):
        return 'Nao consegui interpretar o retorno administrativo desse aluno.'
    return '\n'.join(
        _format_student_administrative_status(
            summary,
            requested_attribute=requested_attribute,
        )
    )


async def _compose_structured_tool_answer(
    *,
    settings: Any,
    request: MessageResponseRequest,
    analysis_message: str,
    preview: Any,
    actor: dict[str, Any] | None,
    school_profile: dict[str, Any] | None,
    conversation_context: dict[str, Any] | None = None,
    public_plan_sink: dict[str, Any] | None = None,
    resolved_public_plan: PublicInstitutionPlan | None = None,
) -> str:
    message = request.message
    if request.telegram_chat_id is not None and actor is None:
        actor = await _fetch_actor_context(settings=settings, telegram_chat_id=request.telegram_chat_id)
    if school_profile is not None:
        fast_public_channel_answer = _try_public_channel_fast_answer(
            message=request.message,
            profile=school_profile,
        )
        if fast_public_channel_answer:
            if public_plan_sink is not None:
                public_plan_sink['deterministic_text'] = fast_public_channel_answer
            return fast_public_channel_answer
    if actor is not None and _is_student_focus_activation_query(message, actor):
        student = _student_focus_candidate(actor, message)
        student_name = str((student or {}).get('full_name', '')).strip() or None
        activated_answer = _compose_student_focus_activation_answer(
            actor,
            student_name=student_name,
        )
        if activated_answer:
            return activated_answer

    if preview.classification.domain in {QueryDomain.institution, QueryDomain.calendar}:
        orphan_workflow_follow_up = _compose_orphan_workflow_follow_up_answer(
            request.message,
            conversation_context,
        )
        if orphan_workflow_follow_up:
            return orphan_workflow_follow_up
        use_admin_path = (
            {'get_administrative_status', 'get_student_administrative_status', 'get_actor_identity_context'}
            & set(preview.selected_tools)
        ) or (
            request.telegram_chat_id is not None and _is_private_admin_follow_up(request.message, conversation_context)
        )
        if preview.classification.domain is QueryDomain.institution and use_admin_path:
            if not {'get_administrative_status', 'get_student_administrative_status', 'get_actor_identity_context'} & set(preview.selected_tools):
                preview.selected_tools = [*preview.selected_tools, 'get_administrative_status', 'get_student_administrative_status']
            if request.telegram_chat_id is None:
                return _compose_structured_deny(actor)
            actor = actor or await _fetch_actor_context(settings=settings, telegram_chat_id=request.telegram_chat_id)
            if actor is None:
                return _compose_structured_deny(actor)
            specialists = _build_protected_record_specialists(
                preview=preview,
                role_code=str(actor.get('role_code', 'anonymous')),
            )
            set_span_attributes(
                **{
                    'eduassist.protected_manager.executed_specialists': ','.join(
                        specialist.name for specialist in specialists
                    ),
                    'eduassist.protected_manager.executed_tools': ','.join(
                        tool_name for specialist in specialists for tool_name in specialist.tool_names
                    ),
                }
            )
            return await _execute_protected_records_specialist(
                settings=settings,
                request=request,
                preview=preview,
                actor=actor,
                conversation_context=conversation_context,
            )
        fast_public_channel_answer = _try_public_channel_fast_answer(
            message=request.message,
            profile=school_profile,
        )
        if fast_public_channel_answer:
            if public_plan_sink is not None:
                public_plan_sink['deterministic_text'] = fast_public_channel_answer
            return fast_public_channel_answer
        plan = resolved_public_plan or await _resolve_public_institution_plan(
            settings=settings,
            message=request.message,
            preview=preview,
            conversation_context=conversation_context,
            school_profile=school_profile,
        )
        if public_plan_sink is not None:
            public_plan_sink['plan'] = plan
        preview.selected_tools = list(plan.required_tools)
        profile, executed_tools, executed_specialists = await _execute_public_institution_plan(
            settings=settings,
            plan=plan,
            school_profile=school_profile,
        )
        should_prefer_deterministic_public_answer = (
            _is_positive_requirement_query(request.message)
            or _is_public_document_submission_query(request.message)
            or _is_comparative_query(request.message)
            or (
                (
                    _is_follow_up_query(request.message)
                    or _normalize_text(request.message).startswith('depois disso')
                )
                and any(
                    _message_matches_term(_normalize_text(request.message), term)
                    for term in {'inicio das aulas', 'início das aulas', 'comecam as aulas', 'começam as aulas', 'aulas'}
                )
                and (
                    _normalize_text(request.message).startswith('depois disso')
                    or _recent_user_message_mentions(
                        conversation_context,
                        {'matricula', 'matrícula', 'proximo ciclo', 'próximo ciclo', 'inscricoes', 'inscrições'},
                    )
                )
            )
            or any(
                _message_matches_term(_normalize_text(request.message), term)
                for term in {'o que isso muda na pratica', 'o que isso muda na prática', 'na pratica no dia a dia', 'na prática no dia a dia'}
            )
            or plan.conversation_act in {'curriculum', 'comparative'}
        )
        if should_prefer_deterministic_public_answer and profile:
            deterministic_public_answer = _compose_public_profile_answer(
                profile,
                analysis_message,
                actor=actor,
                original_message=request.message,
                conversation_context=conversation_context,
                semantic_plan=plan,
            )
            if deterministic_public_answer:
                if public_plan_sink is not None:
                    public_plan_sink['deterministic_text'] = deterministic_public_answer
                return deterministic_public_answer
        fast_public_channel_answer = _try_public_channel_fast_answer(
            message=request.message,
            profile=profile,
        )
        if fast_public_channel_answer:
            if public_plan_sink is not None:
                public_plan_sink['deterministic_text'] = fast_public_channel_answer
            return fast_public_channel_answer
        slot_memory = _build_conversation_slot_memory(
            actor=actor,
            profile=profile,
            conversation_context=conversation_context,
            request_message=request.message,
            public_plan=plan,
            preview=preview,
        )
        set_span_attributes(
            **{
                'eduassist.public_manager.act': plan.conversation_act,
                'eduassist.public_manager.secondary_acts': ','.join(plan.secondary_acts),
                'eduassist.public_manager.fetch_profile': plan.fetch_profile,
                'eduassist.public_manager.semantic_source': plan.semantic_source,
                'eduassist.public_manager.focus_hint': plan.focus_hint or '',
                'eduassist.public_manager.requested_attribute': plan.requested_attribute or '',
                'eduassist.public_manager.requested_channel': plan.requested_channel or '',
                'eduassist.public_manager.slot_focus_kind': slot_memory.focus_kind or '',
                'eduassist.public_manager.slot_contact_subject': slot_memory.contact_subject or '',
                'eduassist.public_manager.slot_feature_key': slot_memory.feature_key or '',
                'eduassist.public_manager.executed_tools': ','.join(executed_tools),
                'eduassist.public_manager.executed_specialists': ','.join(executed_specialists),
            }
        )
        if not profile and plan.conversation_act != 'utility_date':
            return _compose_public_gap_answer(set())
        return await _compose_public_profile_answer_agentic(
            settings=settings,
            profile=profile,
            actor=actor,
            message=analysis_message,
            original_message=request.message,
            conversation_context=conversation_context,
            semantic_plan=plan,
            deterministic_text_sink=public_plan_sink,
        )

    if preview.classification.domain is QueryDomain.support:
        if 'get_workflow_status' in preview.selected_tools:
            workflow_specialist = 'workflow_status'
        elif 'update_visit_booking' in preview.selected_tools:
            workflow_specialist = 'workflow_visit_update'
        elif 'update_institutional_request' in preview.selected_tools:
            workflow_specialist = 'workflow_request_update'
        else:
            workflow_specialist = 'workflow'
        set_span_attributes(
            **{
                'eduassist.workflow_manager.executed_specialists': workflow_specialist,
            }
        )
        if 'get_workflow_status' in preview.selected_tools:
            conversation_external_id = request.conversation_id or _effective_conversation_id(request)
            if not conversation_external_id:
                return (
                    'Consigo acompanhar protocolos por aqui, mas preciso que a conversa esteja vinculada '
                    'ao atendimento atual. Se quiser, me envie o codigo que comeca com VIS, REQ ou ATD.'
                )
            protocol_code_hint = _extract_protocol_code_hint(request.message, conversation_context)
            workflow_kind_hint = _detect_workflow_kind_hint(request.message, conversation_context)
            set_span_attributes(
                **{
                    'eduassist.workflow_manager.protocol_hint_present': bool(protocol_code_hint),
                    'eduassist.workflow_manager.workflow_kind_hint': workflow_kind_hint,
                }
            )
            cached_workflow_payload = _workflow_snapshot_from_context(
                conversation_context,
                workflow_kind_hint=workflow_kind_hint,
                protocol_code_hint=protocol_code_hint,
            )
            if isinstance(cached_workflow_payload, dict):
                set_span_attributes(
                    **{
                        'eduassist.workflow_manager.cache_hit': True,
                    }
                )
                return _compose_workflow_status_answer(
                    cached_workflow_payload,
                    protocol_code_hint=protocol_code_hint,
                    request_message=request.message,
                )
            set_span_attributes(
                **{
                    'eduassist.workflow_manager.cache_hit': False,
                }
            )
            workflow_payload = await _fetch_internal_workflow_status(
                settings=settings,
                conversation_external_id=conversation_external_id,
                protocol_code=protocol_code_hint,
                workflow_kind=workflow_kind_hint,
            )
            return _compose_workflow_status_answer(
                workflow_payload,
                protocol_code_hint=protocol_code_hint,
                request_message=request.message,
            )
        if 'update_visit_booking' in preview.selected_tools:
            if (
                _detect_visit_booking_action(request.message) == 'reschedule'
                and _extract_requested_date(request.message) is None
                and not _extract_requested_window(request.message)
            ):
                cached_workflow_payload = _workflow_snapshot_from_context(
                    conversation_context,
                    workflow_kind_hint='visit_booking',
                    protocol_code_hint=_extract_protocol_code_hint(request.message, conversation_context),
                )
                if isinstance(cached_workflow_payload, dict):
                    return _compose_visit_booking_action_answer(
                        cached_workflow_payload,
                        request_message=request.message,
                    )
                conversation_external_id = request.conversation_id or _effective_conversation_id(request)
                if conversation_external_id:
                    live_workflow_payload = await _fetch_internal_workflow_status(
                        settings=settings,
                        conversation_external_id=conversation_external_id,
                        protocol_code=_extract_protocol_code_hint(request.message, conversation_context),
                        workflow_kind='visit_booking',
                    )
                    if isinstance(live_workflow_payload, dict):
                        return _compose_visit_booking_action_answer(
                            live_workflow_payload,
                            request_message=request.message,
                        )
            workflow_payload = await _update_visit_booking(
                settings=settings,
                request=request,
                conversation_context=conversation_context,
            )
            return _compose_visit_booking_action_answer(
                workflow_payload,
                request_message=request.message,
            )
        if 'update_institutional_request' in preview.selected_tools:
            workflow_payload = await _update_institutional_request(
                settings=settings,
                request=request,
                conversation_context=conversation_context,
            )
            return _compose_institutional_request_action_answer(
                workflow_payload,
                request_message=request.message,
            )
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

    if preview.classification.domain is QueryDomain.academic and role_code == 'teacher':
        specialists = _build_protected_record_specialists(preview=preview, role_code=role_code)
        set_span_attributes(
            **{
                'eduassist.protected_manager.executed_specialists': ','.join(
                    specialist.name for specialist in specialists
                ),
                'eduassist.protected_manager.executed_tools': ','.join(
                    tool_name for specialist in specialists for tool_name in specialist.tool_names
                ),
            }
        )
        return await _execute_teacher_protected_specialist(
            settings=settings,
            request=request,
            actor=actor,
        )

    if preview.classification.domain in {QueryDomain.academic, QueryDomain.finance}:
        if _is_student_focus_activation_query(message, actor):
            student = _student_focus_candidate(actor, message)
            student_name = str((student or {}).get('full_name', '')).strip() or None
            activated_answer = _compose_student_focus_activation_answer(
                actor,
                student_name=student_name,
            )
            if activated_answer:
                return activated_answer
        specialists = _build_protected_record_specialists(preview=preview, role_code=role_code)
        set_span_attributes(
            **{
                'eduassist.protected_manager.executed_specialists': ','.join(
                    specialist.name for specialist in specialists
                ),
                'eduassist.protected_manager.executed_tools': ','.join(
                    tool_name for specialist in specialists for tool_name in specialist.tool_names
                ),
            }
        )
        return await _execute_protected_records_specialist(
            settings=settings,
            request=request,
            preview=preview,
            actor=actor,
            conversation_context=conversation_context,
        )

    return (
        'Esse fluxo protegido ainda nao foi concluido para este perfil no Telegram. '
        'Por enquanto, use o portal autenticado da escola.'
    )


def _compose_deterministic_answer(
    *,
    request_message: str,
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
    timeline_query = preview.classification.domain is QueryDomain.calendar and _is_public_timeline_query(request_message)

    if preview.classification.domain is QueryDomain.calendar and calendar_events and not timeline_query:
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


def _should_run_response_critic(*, preview: Any, request: MessageResponseRequest) -> bool:
    if preview.needs_authentication:
        return False
    if preview.mode is OrchestrationMode.deny:
        return False
    if preview.classification.domain in {QueryDomain.academic, QueryDomain.finance}:
        return False
    if preview.mode in {OrchestrationMode.structured_tool, OrchestrationMode.hybrid_retrieval, OrchestrationMode.clarify}:
        return request.channel.value in {'telegram', 'web'}
    return False


def _should_polish_structured_answer(*, preview: Any, request: MessageResponseRequest) -> bool:
    if preview.mode is not OrchestrationMode.structured_tool:
        return False
    if preview.needs_authentication:
        return False
    if request.channel.value not in {'telegram', 'web'}:
        return False
    if preview.classification.domain is QueryDomain.support:
        return False
    if (
        preview.classification.access_tier is AccessTier.public
        and preview.classification.domain in {QueryDomain.institution, QueryDomain.calendar}
    ):
        return True
    return False


def _preserve_capability_anchor_terms(
    *,
    original_text: str,
    polished_text: str | None,
    request_message: str,
) -> str | None:
    if not polished_text:
        return polished_text

    original_trimmed = original_text.strip()
    polished_trimmed = polished_text.strip()
    if original_trimmed:
        if len(original_trimmed) >= 80 and len(polished_trimmed) < max(48, int(len(original_trimmed) * 0.7)):
            return original_text
        if original_trimmed[-1] in '.!?' and polished_trimmed and polished_trimmed[-1] not in '.!?':
            return original_text

    original_codes = {
        match.group(0).upper()
        for match in PROTOCOL_CODE_PATTERN.finditer(original_text)
    }
    polished_normalized = _normalize_text(polished_text)
    if original_codes:
        if not all(code.lower() in polished_text.lower() for code in original_codes):
            return original_text
        if 'ticket operacional' in _normalize_text(original_text) and 'ticket operacional' not in polished_normalized:
            return original_text
        if 'fila' in _normalize_text(original_text) and 'fila' not in polished_normalized:
            return original_text

    normalized_message = _normalize_text(request_message)
    capability_like_query = any(
        _message_matches_term(normalized_message, term)
        for term in {'quais opcoes de assuntos', 'opcoes de assuntos', 'opções de assuntos', 'o que voce faz', 'como voce pode me ajudar'}
    ) or any(
        _message_matches_term(normalized_message, term)
        for term in {
            'oi',
            'ola',
            'olá',
            'bom dia',
            'boa tarde',
            'boa noite',
            'com quem eu falo',
            'pra quem eu falo',
            'para quem eu falo',
            'quem e voce',
            'quem é você',
            'voce e quem',
            'você é quem',
        }
    )
    if capability_like_query:
        for required_phrase in ('eduassist', 'colegio horizonte'):
            if required_phrase in _normalize_text(original_text) and required_phrase not in polished_normalized:
                return original_text
        original_terms = [
            term
            for term in ('matricula', 'financeiro', 'secretaria', 'visita', 'notas', 'faltas')
            if term in _normalize_text(original_text)
        ]
        if original_terms:
            preserved_count = sum(term in polished_normalized for term in original_terms)
            if preserved_count < min(3, len(original_terms)):
                return original_text

    if any(
        _message_matches_term(normalized_message, term)
        for term in PUBLIC_LEADERSHIP_TERMS | PUBLIC_CONTACT_TERMS | ASSISTANT_IDENTITY_TERMS
    ):
        email_pattern = re.compile(r'[\w.\-+]+@[\w.\-]+\.\w+')
        original_emails = {match.group(0).lower() for match in email_pattern.finditer(original_text)}
        if original_emails and not all(email in polished_text.lower() for email in original_emails):
            return original_text

        proper_name_pattern = re.compile(
            r'\b[A-ZÁÉÍÓÚÂÊÔÃÕÇ][A-Za-zÁÉÍÓÚÂÊÔÃÕÇáéíóúâêôãõç]+(?:\s+[A-ZÁÉÍÓÚÂÊÔÃÕÇ][A-Za-zÁÉÍÓÚÂÊÔÃÕÇáéíóúâêôãõç]+)+\b'
        )
        ignored_names = {
            'colegio horizonte',
            'eduassist',
            'canal institucional',
            'lideranca institucional',
            'diretora geral',
            'diretor geral',
        }
        original_names = {
            _normalize_text(match.group(0))
            for match in proper_name_pattern.finditer(original_text)
            if _normalize_text(match.group(0)) not in ignored_names
        }
        if original_names and not all(name in polished_normalized for name in original_names):
            return original_text
    return polished_text


UUID_PATTERN = re.compile(r'\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b', re.IGNORECASE)
ENROLLMENT_CODE_PATTERN = re.compile(r'\bMAT-\d{4}-\d{3,}\b', re.IGNORECASE)
CONTRACT_CODE_PATTERN = re.compile(r'\bCTR-\d{4}-\d{3,}\b', re.IGNORECASE)
EMAIL_PATTERN = re.compile(r'\b[\w.\-+]+@[\w.\-]+\.\w+\b', re.IGNORECASE)
PHONE_PATTERN = re.compile(r'\(\d{2}\)\s*\d{4,5}-\d{4}')
URL_PATTERN = re.compile(r'https?://\S+', re.IGNORECASE)
DATE_PATTERN = re.compile(r'\b\d{2}/\d{2}/\d{4}\b|\b\d{4}-\d{2}-\d{2}\b')
TEXTUAL_DATE_PATTERN = re.compile(
    r'\b\d{1,2}\s+de\s+[a-zç]+(?:\s+de)?\s+\d{4}\b',
    re.IGNORECASE,
)
TIME_PATTERN = re.compile(r'\b\d{1,2}h\d{2}\b|\b\d{2}:\d{2}\b', re.IGNORECASE)
PROPER_NAME_PATTERN = re.compile(
    r'\b[A-ZÁÉÍÓÚÂÊÔÃÕÇ][A-Za-zÁÉÍÓÚÂÊÔÃÕÇáéíóúâêôãõç]+(?:\s+[A-ZÁÉÍÓÚÂÊÔÃÕÇ][A-Za-zÁÉÍÓÚÂÊÔÃÕÇáéíóúâêôãõç]+)+\b'
)
IGNORED_VERIFIER_NAMES = {
    'colegio horizonte',
    'ensino medio',
    'ensino fundamental ii',
    'ensino fundamental i',
    'diretora geral',
    'diretor geral',
    'orientacao educacional',
    'atendimento comercial',
    'secretaria digital',
}


def _extract_verification_anchors(text: str) -> set[str]:
    anchors: set[str] = set()
    normalized_text = _normalize_text(text)
    for pattern in (
        URL_PATTERN,
        EMAIL_PATTERN,
        PHONE_PATTERN,
        PROTOCOL_CODE_PATTERN,
        UUID_PATTERN,
        ENROLLMENT_CODE_PATTERN,
        CONTRACT_CODE_PATTERN,
        DATE_PATTERN,
        TEXTUAL_DATE_PATTERN,
        TIME_PATTERN,
    ):
        for match in pattern.finditer(text):
            anchors.add(_normalize_text(match.group(0)))
    if 'cep ' in normalized_text:
        cep_match = re.search(r'cep\s+\d{5}-\d{3}', normalized_text)
        if cep_match:
            anchors.add(cep_match.group(0))
    return anchors


def _extract_fallback_named_entities(text: str) -> set[str]:
    entities: set[str] = set()
    for match in PROPER_NAME_PATTERN.finditer(text):
        normalized = _normalize_text(match.group(0))
        if normalized in IGNORED_VERIFIER_NAMES:
            continue
        entities.add(normalized)
    return entities


def _unexpected_protected_entities(
    *,
    preview: Any,
    candidate_text: str,
    fallback_text: str,
) -> set[str]:
    if preview.classification.access_tier is AccessTier.public:
        return set()
    if preview.mode is not OrchestrationMode.structured_tool:
        return set()
    if preview.classification.domain not in {
        QueryDomain.institution,
        QueryDomain.academic,
        QueryDomain.finance,
    }:
        return set()

    fallback_entities = _extract_fallback_named_entities(fallback_text)
    if not fallback_entities:
        return set()
    candidate_entities = _extract_fallback_named_entities(candidate_text)
    if not candidate_entities:
        return set()
    return {
        entity for entity in candidate_entities - fallback_entities
        if entity not in IGNORED_VERIFIER_NAMES
    }


def _required_verifier_terms(
    *,
    preview: Any,
    public_plan: PublicInstitutionPlan | None,
    slot_memory: ConversationSlotMemory,
    request_message: str,
    fallback_text: str,
) -> set[str]:
    required_terms: set[str] = set()
    normalized_message = _normalize_text(request_message)
    fallback_normalized = _normalize_text(fallback_text)
    selected_tool_names = set(getattr(preview, 'selected_tools', []) or [])

    requested_attribute = (
        public_plan.requested_attribute
        if public_plan and public_plan.requested_attribute
        else slot_memory.public_attribute
    )
    requested_channel = (
        public_plan.requested_channel
        if public_plan and public_plan.requested_channel
        else slot_memory.requested_channel
    )

    if requested_attribute == 'age':
        required_terms.add('idade')
    elif requested_attribute == 'whatsapp':
        required_terms.add('whatsapp')
    elif requested_attribute == 'phone':
        required_terms.add('telefone')
    elif requested_attribute == 'email':
        required_terms.add('email')

    if requested_channel == 'telefone':
        required_terms.add('telefone')
    elif requested_channel == 'whatsapp':
        required_terms.add('whatsapp')
    elif requested_channel == 'email':
        required_terms.add('email')

    if slot_memory.academic_attribute == 'enrollment_code':
        required_terms.add('matricula')

    if slot_memory.finance_attribute == 'contract_code':
        required_terms.add('contrato')
    elif slot_memory.finance_attribute == 'invoice_id':
        required_terms.add('fatura')

    if slot_memory.finance_action == 'second_copy' or any(
        _message_matches_term(normalized_message, term) for term in FINANCE_SECOND_COPY_TERMS
    ):
        if 'segunda via' in fallback_normalized:
            required_terms.add('segunda via')

    if preview.classification.access_tier is not AccessTier.public and selected_tool_names & {
        'get_actor_identity_context',
        'get_student_academic_summary',
        'get_student_attendance',
        'get_student_grades',
        'get_student_upcoming_assessments',
        'get_student_attendance_timeline',
        'get_financial_summary',
        'get_student_administrative_status',
    }:
        required_terms.update(_extract_fallback_named_entities(fallback_text))

    if 'get_student_administrative_status' in selected_tool_names:
        required_terms.add('documentacao')
    elif 'get_actor_identity_context' in selected_tool_names:
        required_terms.add('perfil')

    if public_plan and public_plan.conversation_act == 'assistant_identity':
        required_terms.add('eduassist')
    if requested_attribute == 'name' or any(
        _message_matches_term(normalized_message, term)
        for term in {'qual o nome', 'nome da', 'nome do', 'como se chama'}
    ):
        required_terms.update(_extract_fallback_named_entities(fallback_text))

    return {term for term in required_terms if term}


def _extract_time_anchors(text: str) -> list[str]:
    return [_normalize_text(match.group(0)) for match in TIME_PATTERN.finditer(text)]


def _critical_verification_anchors(
    *,
    fallback_text: str,
    public_plan: PublicInstitutionPlan | None,
    slot_memory: ConversationSlotMemory,
) -> set[str]:
    anchors = _extract_verification_anchors(fallback_text)
    if not anchors:
        return anchors

    conversation_act = public_plan.conversation_act if public_plan is not None else None
    requested_attribute = (
        public_plan.requested_attribute
        if public_plan and public_plan.requested_attribute
        else slot_memory.public_attribute
    )

    if conversation_act == 'operating_hours':
        time_anchors = _extract_time_anchors(fallback_text)
        non_time_anchors = {anchor for anchor in anchors if anchor not in time_anchors}
        if requested_attribute == 'open_time' and time_anchors:
            return {*non_time_anchors, time_anchors[0]}
        if requested_attribute == 'close_time' and time_anchors:
            return {*non_time_anchors, time_anchors[-1]}
        if time_anchors:
            return {*non_time_anchors, time_anchors[0], time_anchors[-1]}
    return anchors


def _verify_answer_against_contract(
    *,
    request_message: str,
    preview: Any,
    candidate_text: str,
    deterministic_fallback_text: str | None,
    public_plan: PublicInstitutionPlan | None,
    slot_memory: ConversationSlotMemory,
) -> AnswerVerificationResult:
    if not deterministic_fallback_text:
        return AnswerVerificationResult(valid=True)

    candidate_normalized = _normalize_text(candidate_text)
    fallback_normalized = _normalize_text(deterministic_fallback_text)
    if candidate_normalized == fallback_normalized:
        return AnswerVerificationResult(valid=True)

    fallback_anchors = _critical_verification_anchors(
        fallback_text=deterministic_fallback_text,
        public_plan=public_plan,
        slot_memory=slot_memory,
    )
    missing_anchors = sorted(anchor for anchor in fallback_anchors if anchor not in candidate_normalized)
    if missing_anchors:
        return AnswerVerificationResult(valid=False, reason=f'missing_anchor:{missing_anchors[0]}')

    required_terms = _required_verifier_terms(
        preview=preview,
        public_plan=public_plan,
        slot_memory=slot_memory,
        request_message=request_message,
        fallback_text=deterministic_fallback_text,
    )
    missing_terms = sorted(term for term in required_terms if term not in candidate_normalized)
    if missing_terms:
        return AnswerVerificationResult(valid=False, reason=f'missing_term:{missing_terms[0]}')

    unexpected_entities = sorted(
        _unexpected_protected_entities(
            preview=preview,
            candidate_text=candidate_text,
            fallback_text=deterministic_fallback_text,
        )
    )
    if unexpected_entities:
        return AnswerVerificationResult(valid=False, reason=f'unexpected_entity:{unexpected_entities[0]}')

    return AnswerVerificationResult(valid=True)


def _should_run_semantic_answer_judge(
    *,
    preview: Any,
    deterministic_fallback_text: str | None,
    candidate_text: str,
    public_plan: PublicInstitutionPlan | None,
) -> bool:
    if not deterministic_fallback_text:
        return False
    if _normalize_text(candidate_text) == _normalize_text(deterministic_fallback_text):
        return False
    if preview.classification.access_tier is AccessTier.public:
        if preview.classification.domain not in {QueryDomain.institution, QueryDomain.calendar}:
            return False
        if preview.mode not in {
            OrchestrationMode.structured_tool,
            OrchestrationMode.hybrid_retrieval,
            OrchestrationMode.clarify,
        }:
            return False
        if public_plan is not None and public_plan.conversation_act in {'greeting', 'capabilities'}:
            return False
        return True

    if preview.mode is not OrchestrationMode.structured_tool:
        return False
    return preview.classification.domain in {
        QueryDomain.institution,
        QueryDomain.academic,
        QueryDomain.finance,
    }


async def _verify_answer_against_contract_async(
    *,
    settings: Any,
    request_message: str,
    preview: Any,
    candidate_text: str,
    deterministic_fallback_text: str | None,
    public_plan: PublicInstitutionPlan | None,
    slot_memory: ConversationSlotMemory,
) -> tuple[AnswerVerificationResult, bool]:
    deterministic_result = _verify_answer_against_contract(
        request_message=request_message,
        preview=preview,
        candidate_text=candidate_text,
        deterministic_fallback_text=deterministic_fallback_text,
        public_plan=public_plan,
        slot_memory=slot_memory,
    )
    should_run_judge = _should_run_semantic_answer_judge(
        preview=preview,
        deterministic_fallback_text=deterministic_fallback_text,
        candidate_text=candidate_text,
        public_plan=public_plan,
    )
    if not deterministic_result.valid and (
        deterministic_result.reason is None
        or not deterministic_result.reason.startswith(('missing_anchor:', 'missing_term:'))
    ):
        return deterministic_result, False
    if not should_run_judge:
        return deterministic_result, False

    public_plan_payload = None
    if public_plan is not None:
        public_plan_payload = {
            'conversation_act': public_plan.conversation_act,
            'secondary_acts': list(public_plan.secondary_acts),
            'requested_attribute': public_plan.requested_attribute,
            'requested_channel': public_plan.requested_channel,
            'focus_hint': public_plan.focus_hint,
            'semantic_source': public_plan.semantic_source,
            'use_conversation_context': public_plan.use_conversation_context,
        }
    judge_payload = await judge_answer_relevance_with_provider(
        settings=settings,
        request_message=request_message,
        preview=preview,
        candidate_text=candidate_text,
        fallback_text=deterministic_fallback_text or '',
        public_plan=public_plan_payload,
        slot_memory=_serialize_slot_memory(slot_memory),
    )
    if not isinstance(judge_payload, dict):
        return deterministic_result, False
    judge_valid = judge_payload.get('valid')
    judge_reason = str(judge_payload.get('reason', '')).strip()
    if judge_valid is False:
        if deterministic_result.valid:
            return AnswerVerificationResult(valid=False, reason=f'semantic_judge:{judge_reason or "mismatch"}'), True
        return deterministic_result, True
    if judge_valid is True and not deterministic_result.valid:
        return AnswerVerificationResult(valid=True), True
    return deterministic_result, True


async def generate_message_response(
    *,
    request: MessageResponseRequest,
    settings: Any,
    engine_name: str = 'langgraph',
    engine_mode: str = 'langgraph',
) -> MessageResponse:
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
            'eduassist.orchestration.engine_name': engine_name,
            'eduassist.orchestration.engine_mode': engine_mode,
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
        context_payload = _conversation_context_payload(conversation_context)
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

        langgraph_artifacts = get_langgraph_artifacts(settings)
        graph = langgraph_artifacts.graph
        langgraph_thread_id = resolve_langgraph_thread_id(
            conversation_external_id=effective_conversation_id,
            channel=request.channel.value,
            telegram_chat_id=request.telegram_chat_id,
        )
        with start_span('eduassist.orchestration.graph_preview', tracer_name='eduassist.ai_orchestrator.runtime'):
            preview_request = request.model_copy(update={'message': analysis_message})
            state = invoke_orchestration_graph(
                graph=graph,
                state_input=_build_preview_state_input(
                    request=preview_request,
                    user_context=effective_user,
                    settings=settings,
                ),
                thread_id=langgraph_thread_id,
            )
            if isinstance(state, dict) and state.get('__interrupt__'):
                snapshot = get_orchestration_state_snapshot(
                    graph=graph,
                    thread_id=langgraph_thread_id,
                    subgraphs=True,
                ) if langgraph_thread_id else None
                snapshot_values = dict(getattr(snapshot, 'values', {}) or {}) if snapshot is not None else {}
                if snapshot_values:
                    preview = to_preview(snapshot_values)
                else:
                    preview = OrchestrationPreview(
                        mode=OrchestrationMode.structured_tool,
                        classification=IntentClassification(
                            domain=QueryDomain.support,
                            access_tier=AccessTier.authenticated,
                            confidence=0.9,
                            reason='langgraph_hitl_pending_review',
                        ),
                        reason='langgraph_hitl_pending_review',
                )
                preview.reason = 'langgraph_hitl_pending_review'
                preview.risk_flags = list(dict.fromkeys([*preview.risk_flags, 'pending_human_review']))
                langgraph_trace_metadata = _capture_langgraph_trace_metadata(
                    graph=graph,
                    thread_id=langgraph_thread_id,
                    langgraph_artifacts=langgraph_artifacts,
                )
                message_text = _build_langgraph_pending_review_message(preview=preview)
                message_text = _normalize_response_wording(message_text)
                suggested_replies = _build_suggested_replies(
                    request=request,
                    preview=preview,
                    actor=actor,
                    school_profile=school_profile,
                    conversation_context=context_payload,
                )
                await _persist_operational_trace(
                    settings=settings,
                    conversation_external_id=effective_conversation_id,
                    channel=request.channel.value,
                    engine_name=engine_name,
                    engine_mode=engine_mode,
                    actor=actor,
                    preview=preview,
                    school_profile=school_profile,
                    conversation_context=context_payload,
                    public_plan=None,
                    request_message=request.message,
                    message_text=message_text,
                    citations_count=0,
                    suggested_reply_count=len(suggested_replies),
                    visual_asset_count=0,
                    answer_verifier_valid=True,
                    answer_verifier_reason='langgraph_hitl_pending_review',
                    answer_verifier_fallback_used=False,
                    deterministic_fallback_available=False,
                    answer_verifier_judge_used=False,
                    langgraph_trace_metadata=langgraph_trace_metadata,
                )
                await _persist_conversation_turn(
                    settings=settings,
                    conversation_external_id=effective_conversation_id,
                    channel=request.channel.value,
                    actor=actor,
                    user_message=request.message,
                    assistant_message=message_text,
                )
                return MessageResponse(
                    message_text=message_text,
                    mode=preview.mode,
                    classification=preview.classification,
                    reason=preview.reason,
                    selected_tools=preview.selected_tools,
                    graph_path=preview.graph_path,
                    retrieval_backend=preview.retrieval_backend,
                    needs_authentication=preview.needs_authentication,
                    citations=[],
                    calendar_events=[],
                    visual_assets=[],
                    risk_flags=preview.risk_flags,
                    suggested_replies=suggested_replies,
                )
            preview = to_preview(state)
        langgraph_trace_metadata = _capture_langgraph_trace_metadata(
            graph=graph,
            thread_id=langgraph_thread_id,
            langgraph_artifacts=langgraph_artifacts,
        )
        set_span_attributes(
            **{
                'eduassist.orchestration.mode': preview.mode.value,
                'eduassist.orchestration.domain': preview.classification.domain.value,
                'eduassist.orchestration.access_tier': preview.classification.access_tier.value,
                'eduassist.orchestration.needs_authentication': preview.needs_authentication,
                'eduassist.orchestration.selected_tools': preview.selected_tools,
                'eduassist.orchestration.graph_path': preview.graph_path,
                'eduassist.orchestration.retrieval_backend': preview.retrieval_backend.value,
                'eduassist.orchestration.langgraph_thread_id': langgraph_thread_id or '',
                'eduassist.orchestration.langgraph_checkpointer_enabled': langgraph_artifacts.checkpointer_enabled,
                'eduassist.orchestration.langgraph_checkpointer_backend': langgraph_artifacts.checkpointer_backend or '',
                'eduassist.orchestration.langgraph_state_available': bool(langgraph_trace_metadata.get('state_available')),
                'eduassist.orchestration.langgraph_state_fetch_error': str(langgraph_trace_metadata.get('state_fetch_error', '') or ''),
                'eduassist.orchestration.langgraph_checkpoint_id': str(langgraph_trace_metadata.get('checkpoint_id', '') or ''),
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
        public_plan: PublicInstitutionPlan | None = None
        deterministic_fallback_text: str | None = None
        rescued_public_plan: PublicInstitutionPlan | None = None

        if _is_public_semantic_rescue_candidate(preview):
            rescued_public_plan = await _resolve_public_institution_plan(
                settings=settings,
                message=request.message,
                preview=preview,
                conversation_context=context_payload,
                school_profile=school_profile,
            )
            if _should_apply_public_semantic_rescue(preview=preview, plan=rescued_public_plan):
                preview.mode = OrchestrationMode.structured_tool
                preview.reason = 'planejamento semantico publico encontrou um ato estruturado mais adequado ao turno'
                preview.selected_tools = list(rescued_public_plan.required_tools)
                set_span_attributes(
                    **{
                        'eduassist.orchestration.semantic_rescue_applied': True,
                        'eduassist.orchestration.semantic_rescue_act': rescued_public_plan.conversation_act,
                        'eduassist.orchestration.semantic_rescue_source': rescued_public_plan.semantic_source,
                    }
                )
            else:
                set_span_attributes(
                    **{
                        'eduassist.orchestration.semantic_rescue_applied': False,
                    }
                )

        if _apply_student_disambiguation_rescue(
            preview=preview,
            actor=actor,
            message=request.message,
            conversation_context=context_payload,
        ):
            set_span_attributes(
                **{
                    'eduassist.orchestration.student_disambiguation_rescue_applied': True,
                    'eduassist.orchestration.student_disambiguation_rescue_domain': preview.classification.domain.value,
                }
            )

        linked_students = _linked_students(actor)
        unmatched_student_reference = _explicit_unmatched_student_reference(
            linked_students,
            request.message,
            conversation_context=context_payload,
        ) if linked_students else None
        foreign_school_reference = None if unmatched_student_reference else _foreign_school_reference(
            message=request.message,
            school_profile=school_profile,
            conversation_context=context_payload,
        )
        if foreign_school_reference:
            set_span_attributes(
                **{
                    'eduassist.orchestration.used_llm': False,
                    'eduassist.orchestration.answer_guardrail': 'foreign_school_redirect',
                }
            )
            message_text = _compose_foreign_school_redirect(
                school_profile=school_profile,
                foreign_school_reference=foreign_school_reference,
            )
            deterministic_fallback_text = message_text
            verification, semantic_judge_used = await _verify_answer_against_contract_async(
                settings=settings,
                request_message=request.message,
                preview=preview,
                candidate_text=message_text,
                deterministic_fallback_text=deterministic_fallback_text,
                public_plan=public_plan,
                slot_memory=_build_conversation_slot_memory(
                    actor=actor,
                    profile=school_profile,
                    conversation_context=context_payload,
                    request_message=request.message,
                    public_plan=public_plan,
                    preview=preview,
                ),
            )
            set_span_attributes(
                **{
                    'eduassist.orchestration.answer_verifier_valid': verification.valid,
                    'eduassist.orchestration.answer_verifier_reason': verification.reason or '',
                    'eduassist.orchestration.answer_verifier_judge_used': semantic_judge_used,
                }
            )
            message_text = _normalize_response_wording(message_text)
            suggested_replies = _build_suggested_replies(
                request=request,
                preview=preview,
                actor=actor,
                school_profile=school_profile,
                conversation_context=context_payload,
            )
            await _persist_operational_trace(
                settings=settings,
                conversation_external_id=effective_conversation_id,
                channel=request.channel.value,
                engine_name=engine_name,
                engine_mode=engine_mode,
                actor=actor,
                preview=preview,
                school_profile=school_profile,
                conversation_context=context_payload,
                public_plan=public_plan,
                request_message=request.message,
                message_text=message_text,
                citations_count=0,
                suggested_reply_count=len(suggested_replies),
                visual_asset_count=0,
                answer_verifier_valid=verification.valid,
                answer_verifier_reason=verification.reason,
                answer_verifier_fallback_used=False,
                deterministic_fallback_available=True,
                answer_verifier_judge_used=semantic_judge_used,
                langgraph_trace_metadata=langgraph_trace_metadata,
            )
            await _persist_conversation_turn(
                settings=settings,
                conversation_external_id=effective_conversation_id,
                channel=request.channel.value,
                actor=actor,
                user_message=request.message,
                assistant_message=message_text,
            )
            return MessageResponse(
                message_text=message_text,
                mode=preview.mode,
                classification=preview.classification,
                reason=preview.reason,
                selected_tools=preview.selected_tools,
                graph_path=preview.graph_path,
                retrieval_backend=preview.retrieval_backend,
                needs_authentication=preview.needs_authentication,
                citations=[],
                calendar_events=[],
                visual_assets=[],
                risk_flags=preview.risk_flags,
                suggested_replies=suggested_replies,
            )

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
                public_plan_sink: dict[str, Any] = {}
                message_text = await _compose_structured_tool_answer(
                    settings=settings,
                    request=request,
                    analysis_message=analysis_message,
                    preview=preview,
                    actor=actor,
                    school_profile=school_profile,
                    conversation_context=context_payload,
                    public_plan_sink=public_plan_sink,
                    resolved_public_plan=rescued_public_plan,
                )
                public_plan = public_plan_sink.get('plan')
                deterministic_fallback_text = str(public_plan_sink.get('deterministic_text') or message_text)
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
                deterministic_fallback_text = message_text
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
                request_message=request.message,
                preview=preview,
                retrieval_hits=retrieval_hits,
                citations=[],
                calendar_events=calendar_events,
                query_hints=query_hints,
            )
            deterministic_fallback_text = message_text
        else:
            with start_span('eduassist.orchestration.answer_composition', tracer_name='eduassist.ai_orchestrator.runtime'):
                deterministic_answer_candidate: str | None = None
                if _is_greeting_only(request.message):
                    set_span_attributes(
                        **{
                            'eduassist.orchestration.used_llm': False,
                            'eduassist.orchestration.answer_guardrail': 'institutional_greeting',
                        }
                    )
                    citations = []
                    message_text = INSTITUTIONAL_GREETING
                    deterministic_answer_candidate = message_text
                elif preview.mode is OrchestrationMode.hybrid_retrieval and not retrieval_supported:
                    set_span_attributes(**{'eduassist.orchestration.used_llm': False})
                    citations = []
                    message_text = _compose_public_gap_answer(query_hints, request.message)
                    deterministic_answer_candidate = message_text
                elif preview.mode is OrchestrationMode.hybrid_retrieval and _is_negative_requirement_query(request.message):
                    set_span_attributes(
                        **{
                            'eduassist.orchestration.used_llm': False,
                            'eduassist.orchestration.answer_guardrail': 'negative_requirement_abstention',
                        }
                    )
                    message_text = _compose_negative_requirement_answer()
                    deterministic_answer_candidate = message_text
                elif preview.mode is OrchestrationMode.hybrid_retrieval and _is_comparative_query(request.message):
                    set_span_attributes(
                        **{
                            'eduassist.orchestration.used_llm': False,
                            'eduassist.orchestration.answer_guardrail': 'comparative_abstention',
                        }
                    )
                    citations = []
                    message_text = _compose_comparative_gap_answer(school_profile)
                    deterministic_answer_candidate = message_text
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
                    deterministic_answer_candidate = message_text
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
                    deterministic_answer_candidate = message_text
                elif preview.mode is OrchestrationMode.clarify:
                    fast_public_channel_answer = _try_public_channel_fast_answer(
                        message=request.message,
                        profile=school_profile,
                    )
                    if fast_public_channel_answer:
                        set_span_attributes(
                            **{
                                'eduassist.orchestration.used_llm': False,
                                'eduassist.orchestration.answer_guardrail': 'public_fast_path_clarify',
                            }
                        )
                        message_text = fast_public_channel_answer
                        deterministic_answer_candidate = fast_public_channel_answer
                    else:
                        clarify_slot_memory = _build_conversation_slot_memory(
                            actor=actor,
                            profile=school_profile,
                            conversation_context=context_payload,
                            request_message=request.message,
                            public_plan=public_plan,
                            preview=preview,
                        )
                        contextual_clarify = _compose_contextual_clarify_answer(
                            request_message=request.message,
                            actor=actor,
                            conversation_context=context_payload,
                            slot_memory=clarify_slot_memory,
                        )
                        if contextual_clarify:
                            set_span_attributes(
                                **{
                                    'eduassist.orchestration.used_llm': False,
                                    'eduassist.orchestration.answer_guardrail': 'contextual_clarify',
                                }
                            )
                            message_text = contextual_clarify
                            deterministic_answer_candidate = contextual_clarify
                        else:
                            deterministic_answer_candidate = _compose_deterministic_answer(
                                request_message=request.message,
                                preview=preview,
                                retrieval_hits=retrieval_hits,
                                citations=citations,
                                calendar_events=calendar_events,
                                query_hints=query_hints,
                            )
                            llm_text = await compose_with_provider(
                                settings=settings,
                                request_message=request.message,
                                analysis_message=analysis_message,
                                preview=preview,
                            citations=citations,
                            calendar_events=calendar_events,
                            conversation_context=context_payload,
                            school_profile=school_profile,
                        )
                        set_span_attributes(
                            **{
                                'eduassist.orchestration.used_llm': bool(llm_text),
                                'eduassist.orchestration.llm_provider': settings.llm_provider,
                            }
                        )
                        message_text = llm_text or deterministic_answer_candidate
                else:
                    deterministic_answer_candidate = _compose_deterministic_answer(
                        request_message=request.message,
                        preview=preview,
                        retrieval_hits=retrieval_hits,
                        citations=citations,
                        calendar_events=calendar_events,
                        query_hints=query_hints,
                    )
                    llm_text = await compose_with_provider(
                        settings=settings,
                        request_message=request.message,
                        analysis_message=analysis_message,
                        preview=preview,
                        citations=citations,
                        calendar_events=calendar_events,
                        conversation_context=context_payload,
                        school_profile=school_profile,
                    )
                    set_span_attributes(
                        **{
                            'eduassist.orchestration.used_llm': bool(llm_text),
                            'eduassist.orchestration.llm_provider': settings.llm_provider,
                        }
                    )
                    message_text = llm_text or deterministic_answer_candidate
                deterministic_fallback_text = deterministic_answer_candidate

        if _should_polish_structured_answer(preview=preview, request=request):
            original_structured_text = message_text
            polished_text = await polish_structured_with_provider(
                settings=settings,
                request_message=request.message,
                preview=preview,
                draft_text=message_text,
                conversation_context=context_payload,
                school_profile=school_profile,
            )
            set_span_attributes(
                **{
                    'eduassist.orchestration.structured_polish_used': bool(polished_text),
                }
            )
            polished_text = _preserve_capability_anchor_terms(
                original_text=original_structured_text,
                polished_text=polished_text,
                request_message=request.message,
            )
            if polished_text:
                message_text = polished_text

        if settings.llm_provider == 'openai' and _should_run_response_critic(preview=preview, request=request):
            revised_text = await revise_with_provider(
                settings=settings,
                request_message=request.message,
                preview=preview,
                draft_text=message_text,
                conversation_context=context_payload,
                school_profile=school_profile,
            )
            set_span_attributes(
                **{
                    'eduassist.orchestration.response_critic_used': bool(revised_text),
                }
            )
            if revised_text:
                message_text = revised_text

        verifier_slot_memory = _build_conversation_slot_memory(
            actor=actor,
            profile=school_profile,
            conversation_context=context_payload,
            request_message=request.message,
            public_plan=public_plan,
            preview=preview,
        )
        verification, semantic_judge_used = await _verify_answer_against_contract_async(
            settings=settings,
            request_message=request.message,
            preview=preview,
            candidate_text=message_text,
            deterministic_fallback_text=deterministic_fallback_text,
            public_plan=public_plan,
            slot_memory=verifier_slot_memory,
        )
        set_span_attributes(
            **{
                'eduassist.orchestration.answer_verifier_valid': verification.valid,
                'eduassist.orchestration.answer_verifier_reason': verification.reason or '',
                'eduassist.orchestration.answer_verifier_judge_used': semantic_judge_used,
            }
        )
        answer_verifier_fallback_used = False
        if not verification.valid and deterministic_fallback_text:
            message_text = deterministic_fallback_text
            answer_verifier_fallback_used = True

        if citations:
            sources = _render_source_lines(citations)
            if sources and sources not in message_text:
                message_text = f'{message_text}\n\n{sources}'
        message_text = _normalize_response_wording(message_text)

        visual_assets = await _maybe_build_visual_assets(
            settings=settings,
            request=request,
            preview=preview,
            actor=actor,
            school_profile=school_profile,
            conversation_context=context_payload,
        )
        suggested_replies = _build_suggested_replies(
            request=request,
            preview=preview,
            actor=actor,
            school_profile=school_profile,
            conversation_context=context_payload,
        )

        await _persist_conversation_turn(
            settings=settings,
            conversation_external_id=effective_conversation_id,
            channel=request.channel.value,
            actor=actor,
            user_message=request.message,
            assistant_message=message_text,
        )
        await _persist_operational_trace(
            settings=settings,
            conversation_external_id=effective_conversation_id,
            channel=request.channel.value,
            engine_name=engine_name,
            engine_mode=engine_mode,
            actor=actor,
            preview=preview,
            school_profile=school_profile,
            conversation_context=context_payload,
            public_plan=public_plan,
            request_message=request.message,
            message_text=message_text,
            citations_count=len(citations),
            suggested_reply_count=len(suggested_replies),
            visual_asset_count=len(visual_assets),
            answer_verifier_valid=verification.valid,
            answer_verifier_reason=verification.reason,
            answer_verifier_fallback_used=answer_verifier_fallback_used,
            deterministic_fallback_available=bool(deterministic_fallback_text),
            answer_verifier_judge_used=semantic_judge_used,
            langgraph_trace_metadata=langgraph_trace_metadata,
        )

        set_span_attributes(
            **{
                'eduassist.response.length': len(message_text),
                'eduassist.response.visual_asset_count': len(visual_assets),
                'eduassist.response.suggested_reply_count': len(suggested_replies),
            }
        )
        metric_attributes = {
            'engine_name': engine_name,
            'engine_mode': engine_mode,
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
        selected_tools = list(preview.selected_tools)
        if (
            preview.mode is OrchestrationMode.structured_tool
            and preview.classification.domain is QueryDomain.institution
            and preview.classification.access_tier is AccessTier.public
            and 'get_administrative_status' not in preview.selected_tools
            and 'get_student_administrative_status' not in preview.selected_tools
            and 'get_actor_identity_context' not in preview.selected_tools
        ):
            if public_plan is not None:
                selected_tools = list(public_plan.required_tools)
            else:
                selected_tools = _build_public_institution_plan(
                    request.message,
                    list(preview.selected_tools),
                ).required_tools
            if 'get_public_school_profile' not in selected_tools:
                selected_tools = [*selected_tools, 'get_public_school_profile']
        return MessageResponse(
            message_text=message_text,
            mode=preview.mode,
            classification=preview.classification,
            retrieval_backend=preview.retrieval_backend,
            selected_tools=selected_tools,
            citations=citations,
            visual_assets=visual_assets,
            suggested_replies=suggested_replies,
            calendar_events=calendar_events,
            needs_authentication=preview.needs_authentication,
            graph_path=preview.graph_path,
            risk_flags=preview.risk_flags,
            reason=preview.reason,
        )
