from __future__ import annotations

import asyncio
import base64
import io
import re
import unicodedata
from collections.abc import Callable
from dataclasses import replace
from datetime import date, datetime, timedelta
from decimal import Decimal, InvalidOperation
from time import monotonic
from types import SimpleNamespace
from typing import Any
from zoneinfo import ZoneInfo

import httpx
from PIL import Image, ImageDraw, ImageFont

from eduassist_observability import (
    canonicalize_evidence_strategy,
    canonicalize_risk_flags,
    record_counter,
    record_histogram,
    set_span_attributes,
    start_span,
)
from eduassist_semantic_ingress import (
    looks_like_language_preference_feedback,
    looks_like_school_scope_message,
    looks_like_scope_boundary_candidate,
)

from .candidate_builder import build_response_candidate
from .candidate_chooser import choose_best_candidate
from .entity_resolution import resolve_entity_hints
from .evidence_pack import (
    build_direct_answer_evidence_pack,
    build_known_unknown_evidence_pack,
    build_retrieval_evidence_pack,
    build_structured_tool_evidence_pack,
)
from .final_polish_policy import build_final_polish_decision
from .graph import to_preview
from .graph_rag_runtime import graph_rag_workspace_ready, run_graph_rag_query
from .langgraph_local_llm import (
    compose_langgraph_public_grounded_with_provider,
    compose_langgraph_with_provider,
    polish_langgraph_with_provider,
    resolve_langgraph_public_semantic_with_provider,
    revise_langgraph_with_provider,
    verify_langgraph_answer_against_contract,
)
from .langgraph_runtime import (
    get_langgraph_artifacts,
    get_orchestration_state_snapshot,
    invoke_orchestration_graph,
    resolve_langgraph_thread_id,
)
from .langgraph_trace import build_langgraph_trace_sections
from .llm_provider import judge_answer_relevance_with_provider
from .models import (
    AccessTier,
    AnswerVerificationResult,
    CalendarEventCard,
    ConversationContextBundle,
    ConversationSlotMemory,
    IntentClassification,
    InternalSpecialistPlan,
    MessageEvidencePack,
    MessageEvidenceSupport,
    MessageResponse,
    MessageResponseCitation,
    MessageResponseRequest,
    MessageResponseSuggestedReply,
    MessageResponseVisualAsset,
    OrchestrationMode,
    OrchestrationPreview,
    OrchestrationRequest,
    ProtectedAttributeRequest,
    PublicActRule,
    PublicAnswerabilityAssessment,
    PublicInstitutionPlan,
    PublicProfileContext,
    QueryDomain,
    RetrievalBackend,
    RetrievalProfile,
    StructuredAnswerFrame,
    UserContext,
    UserRole,
)
from .public_agentic_engine import build_public_evidence_bundle
from .public_doc_knowledge import (
    compose_public_bolsas_and_processes,
    compose_public_calendar_visibility,
    compose_public_canonical_lane_answer,
    compose_public_conduct_policy_contextual_answer,
    compose_public_family_new_calendar_assessment_enrollment,
    compose_public_first_month_risks,
    compose_public_health_authorizations_bridge,
    compose_public_health_second_call,
    compose_public_outings_authorizations,
    compose_public_permanence_and_family_support,
    compose_public_process_compare,
    compose_public_transport_uniform_bundle,
    match_public_canonical_lane,
)
from .public_known_unknowns import (
    compose_public_known_unknown_answer,
    detect_public_known_unknown_key,
)
from .request_intent_guardrails import (
    looks_like_explicit_admin_status_query,
    looks_like_school_domain_request,
)
from .response_cache import get_cached_public_response, store_cached_public_response
from .retrieval import (
    can_read_restricted_documents,
    compose_restricted_document_grounded_answer_for_query,
    compose_restricted_document_no_match_answer,
    get_retrieval_service,
    looks_like_restricted_document_query,
    select_relevant_restricted_hits,
)
from .retrieval_aware_router import build_public_evidence_probe, build_routing_decision
from .serving_policy import LoadSnapshot, build_public_serving_policy
from .serving_telemetry import get_stack_telemetry_snapshot, record_stack_outcome
from .specialist_trace import build_specialist_trace_sections

DEFAULT_PUBLIC_HELP = (
    'Posso ajudar com informacoes publicas da escola, como calendario, matricula, '
    'documentos exigidos e regras de atendimento digital.'
)
_PUBLIC_RESOURCE_CACHE_TTL_SECONDS = 120.0
_PUBLIC_RESOURCE_CACHE: dict[str, dict[str, Any]] = {}


def _llm_forced_mode_enabled(
    *, settings: Any, request: MessageResponseRequest | Any | None = None
) -> bool:
    if bool(getattr(settings, 'feature_flag_final_polish_force_llm', False)):
        return True
    debug_options = getattr(request, 'debug_options', None)
    if isinstance(debug_options, dict):
        return bool(debug_options.get('llm_forced_mode'))
    return False


ATTENDANCE_TERMS = {'frequencia', 'falta', 'faltas', 'presenca', 'presencas'}
GRADE_TERMS = {'nota', 'notas', 'boletim', 'avaliacao', 'avaliacoes', 'prova', 'provas'}
GRADE_REQUIREMENT_TERMS = {
    'quanto precisa tirar',
    'quanto precisa de nota',
    'quanto precisa tirar de nota',
    'precisa tirar',
    'precisa tirar de nota',
    'precisa de nota',
    'nota precisa',
    'nota para passar',
    'nota pra passar',
    'nota para aprovar',
    'nota pra aprovar',
}
GRADE_APPROVAL_TERMS = {
    'passar',
    'aprovar',
    'aprovado',
    'aprovada',
    'ser aprovado',
    'ser aprovada',
    'media de aprovacao',
    'média de aprovação',
    'media para passar',
    'média para passar',
}
PASSING_GRADE_TARGET = 7.0
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
FINANCE_OPEN_TERMS = {
    'aberto',
    'abertos',
    'em aberto',
    'pendencia',
    'pendencias',
    'boleto',
    'boletos',
}
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
    'parte administrativa',
    'situacao administrativa',
    'situação administrativa',
    'administrativo',
    'administrativa',
    'pendencia administrativa',
    'pendência administrativa',
    'pendencias administrativas',
    'pendências administrativas',
    'documentacao atualizada',
    'documentação atualizada',
    'documentacao completa',
    'documentação completa',
    'pendencia documental',
    'pendência documental',
    'pendencias documentais',
    'pendências documentais',
    'quadro documental',
    'cadastro atualizado',
    'cadastro completo',
    'meu cadastro',
    'meus dados cadastrais',
    'dados cadastrais',
    'documentacao',
    'documentação',
    'documental',
    'documentais',
    'exige acao',
    'exigem acao',
    'proximo passo',
    'próximo passo',
}
FAMILY_FINANCE_AGGREGATE_TERMS = {
    'como esta o financeiro da familia',
    'como está o financeiro da família',
    'como estao meus pagamentos',
    'como estão meus pagamentos',
    'meus pagamentos',
    'meus boletos',
    'situacao financeira da familia',
    'situação financeira da família',
    'situacao financeira atual da familia',
    'situação financeira atual da família',
    'resuma a situacao financeira',
    'resuma a situação financeira',
    'resumo financeiro da familia',
    'resumo financeiro da família',
    'financeiro da familia',
    'financeiro da familia hoje',
    'quadro financeiro da familia',
    'financeiro da família',
    'financeiro da família hoje',
    'quadro financeiro da família',
    'vencimentos e proximos passos',
    'vencimentos e próximos passos',
    'contas vinculadas',
}
FAMILY_ACADEMIC_AGGREGATE_TERMS = {
    'panorama academico',
    'panorama acadêmico',
    'quadro academico',
    'quadro acadêmico',
    'situacao academica',
    'situação acadêmica',
    'situacao academica dos meus dois filhos',
    'situação acadêmica dos meus dois filhos',
    'meus dois filhos',
    'meus filhos',
    'dos meus filhos',
    'da minha familia',
    'da minha família',
    'quem esta mais perto do limite',
    'quem está mais perto do limite',
    'quem esta mais proximo do limite',
    'quem está mais próximo do limite',
    'quem esta mais perto da aprovacao',
    'quem está mais perto da aprovação',
    'mais proximo do limite de aprovacao',
    'mais próximo do limite de aprovação',
    'academicamente pior',
    'mais critico academicamente',
    'mais crítico academicamente',
    'qual dos meus filhos esta academicamente pior',
    'qual dos meus filhos está academicamente pior',
    'qual dos meus filhos esta pior',
    'qual dos meus filhos está pior',
}
FAMILY_REFERENCE_TERMS = {
    'familia',
    'família',
    'filhos',
    'meus filhos',
    'meus dois filhos',
    'contas vinculadas',
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
SUBJECT_REQUEST_LABELS = {
    'matematica': 'Matematica',
    'matemática': 'Matematica',
    'portugues': 'Lingua Portuguesa',
    'português': 'Lingua Portuguesa',
    'redacao': 'Redacao',
    'redação': 'Redacao',
    'biologia': 'Biologia',
    'historia': 'Historia',
    'história': 'Historia',
    'fisica': 'Fisica',
    'física': 'Fisica',
    'quimica': 'Quimica',
    'química': 'Quimica',
    'geografia': 'Geografia',
    'ingles': 'Lingua Inglesa',
    'inglês': 'Lingua Inglesa',
    'lingua inglesa': 'Lingua Inglesa',
    'língua inglesa': 'Lingua Inglesa',
    'english': 'Lingua Inglesa',
    'educacao fisica': 'Educacao Fisica',
    'educação física': 'Educacao Fisica',
    'projeto de vida': 'Projeto de vida',
    'danca': 'Danca',
    'dança': 'Danca',
}
UNKNOWN_SUBJECT_CONTEXT_TERMS = {
    'nota',
    'notas',
    'media',
    'média',
    'medias',
    'médias',
    'boletim',
    'prova',
    'provas',
    'avaliacao',
    'avaliação',
    'avaliacoes',
    'avaliações',
    'entrega',
    'entregas',
    'disciplina',
    'disciplinas',
    'materia',
    'matéria',
    'materias',
    'matérias',
    'aulas de',
}
UNKNOWN_SUBJECT_STOPWORDS = {
    'ele',
    'ela',
    'dele',
    'dela',
    'deles',
    'delas',
    'isso',
    'essa',
    'esse',
    'essas',
    'esses',
    'aquilo',
    'todas',
    'todos',
    'toda',
    'todo',
    'aula',
    'aulas',
    'disciplina',
    'disciplinas',
    'materia',
    'matéria',
    'materias',
    'matérias',
    'nota',
    'notas',
    'media',
    'média',
    'medias',
    'médias',
    'prova',
    'provas',
    'avaliacao',
    'avaliação',
    'avaliacoes',
    'avaliações',
    'entrega',
    'entregas',
}
ACADEMIC_DIFFICULTY_TERMS = {
    'mais dificil',
    'mais difícil',
    'mais puxada',
    'mais pesada',
    'mais complicada',
}
ACADEMIC_DIFFICULTY_ANCHORS = {
    'disciplina',
    'disciplinas',
    'materia',
    'matéria',
    'materias',
    'matérias',
    'nota',
    'notas',
    'media',
    'média',
    'medias',
    'médias',
    'boletim',
    'dele',
    'dela',
    'do aluno',
    'da aluna',
}
PUBLIC_CURRICULUM_SCOPE_TERMS = {
    'no colegio',
    'no colégio',
    'na escola',
    'do colegio',
    'do colégio',
    'da escola',
    'o colegio',
    'o colégio',
    'essa escola',
}
PUBLIC_PRICING_TERMS = {
    'mensalidade',
    'mensalidades',
    'valor',
    'valores',
    'preco',
    'preços',
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
    'contatos',
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
PUBLIC_CAPACITY_STUDENT_TERMS = {
    'vaga de aluno',
    'vagas de aluno',
    'vaga de alunos',
    'vagas de alunos',
    'vaga para aluno',
    'vagas para alunos',
    'vagas na escola',
    'vaga na escola',
    'quantas vagas tem na escola',
    'quantidade de vagas na escola',
    'capacidade da escola',
    'capacidade de alunos',
    'vagas de matricula',
    'vagas de matrícula',
    'disponibilidade de matricula',
    'disponibilidade de matrícula',
}
PUBLIC_CAPACITY_PARKING_TERMS = {
    'estacionamento',
    'vaga no estacionamento',
    'vagas no estacionamento',
    'vagas do estacionamento',
    'vaga de estacionamento',
    'vagas de estacionamento',
}
PUBLIC_CAPACITY_DISAMBIGUATION_TERMS = {
    'aluno',
    'alunos',
    'escola',
    'matricula',
    'matrícula',
    'turma',
    'turmas',
    'segmento',
    'segmentos',
    'estacionamento',
    'capacidade',
    'lotacao',
    'lotação',
}
PUBLIC_NOTIFICATION_TERMS = {
    'me avisa',
    'me avise',
    'me lembrar',
    'me lembre',
    'vao me avisar',
    'vão me avisar',
    'vai me avisar',
    'quando chegar perto',
}
TEACHER_INTERNAL_SCOPE_TERMS = {
    'ja sou professor',
    'já sou professor',
    'ja sou professora',
    'já sou professora',
    'sou professor do colegio',
    'sou professor do colégio',
    'sou professora do colegio',
    'sou professora do colégio',
    'meus alunos',
    'meus estudantes',
    'minhas turmas',
    'minhas disciplinas',
    'meu horario docente',
    'meu horário docente',
    'meu horario de aula',
    'meu horário de aula',
    'meus horarios de aula',
    'meus horários de aula',
    'minha grade docente',
    'minha grade',
    'grade docente completa',
    'quais turmas eu tenho',
    'quais turmas eu atendo',
    'quais disciplinas eu tenho',
    'quais disciplinas eu atendo',
    'quais classes eu tenho',
    'quais classes eu atendo',
    'rotina docente',
    'minha rotina docente',
    'portal docente',
    'portal do professor',
}
TEACHER_SCOPE_GUIDANCE_TERMS = {
    *TEACHER_INTERNAL_SCOPE_TERMS,
    'situacao dos meus alunos',
    'situação dos meus alunos',
    'como verifico a situacao dos meus alunos',
    'como verifico a situação dos meus alunos',
    'como verifico meus alunos',
}
TEACHER_RECRUITMENT_TERMS = {
    'trabalhar',
    'trabalhe conosco',
    'dar aula',
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
    'bncc',
    'segue a bncc',
    'seguir a bncc',
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
    'prazos e canais da secretaria',
    'prazo da secretaria para documentos',
    'prazos para secretaria receber documentos',
    'canais da secretaria para documentos',
    'declaracoes e atualizacoes cadastrais',
    'declarações e atualizações cadastrais',
    'atualizacoes cadastrais',
    'atualizações cadastrais',
}
PUBLIC_LOCATION_TERMS = {
    'endereco',
    'endereço',
    'cidade',
    'estado',
    'bairro',
    'qual bairro',
    'em qual bairro',
    'onde fica',
    'localizacao',
    'localização',
}
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
    '30 segundos',
    '30s',
    'familia nova',
    'família nova',
    'por que escolher',
    'por que deveria',
    'por que colocaria',
}
PUBLIC_CROSS_DOCUMENT_TERMS = {
    'compare',
    'comparar',
    'comparacao',
    'comparação',
    'comparativo',
    'sintetize',
    'sintetizar',
    'relacione',
    'pilares',
    'ponto de vista',
    'guia de sobrevivencia',
    'guia de sobrevivência',
    'de ponta a ponta',
    'quando cruzamos',
    'o que muda',
    'destacando',
}
PUBLIC_CROSS_DOCUMENT_DOC_TERMS = {
    'calendario',
    'calendário',
    'agenda',
    'manual',
    'regulamentos',
    'politica',
    'política',
    'proposta pedagogica',
    'proposta pedagógica',
    'secretaria',
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
    'quero conhecer a escola',
    'visitar a escola',
    'visitar o colegio',
    'visitar o colégio',
    'quero visitar',
    'agendar visita',
}
VISIT_RESCHEDULE_TERMS = {
    'remarcar visita',
    'remarcar a visita',
    'remarca visita',
    'remarca a visita',
    'reagendar visita',
    'reagendar a visita',
    'reagenda visita',
    'reagenda a visita',
    'mudar a visita',
    'muda a visita',
    'mudar horario da visita',
    'mudar o horario da visita',
    'muda o horario da visita',
    'mudar horario da minha visita',
    'trocar horario da visita',
    'trocar o horario da visita',
    'troca o horario da visita',
    'trocar o horario',
    'mudar o horario',
    'remarco',
}
VISIT_CANCEL_TERMS = {
    'cancelar visita',
    'cancelar a visita',
    'cancela visita',
    'cancela a visita',
    'desmarcar visita',
    'desmarcar a visita',
    'desmarca visita',
    'desmarca a visita',
    'cancelar minha visita',
    'cancela minha visita',
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
WORKFLOW_REQUEST_TERMS = {
    'solicitacao',
    'solicitação',
    'pedido',
    'protocolo',
    'requerimento',
    'direcao',
    'direção',
    'ouvidoria',
}
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
FINANCE_TERMS = SUPPORT_FINANCE_TERMS | {'vencimento', 'vencimentos', 'atraso', 'atrasos'}
SUPPORT_COORDINATION_TERMS = {'coordenacao', 'pedagogico', 'ocorrencia', 'professor', 'disciplina'}
SUPPORT_SECRETARIAT_TERMS = {
    'secretaria',
    'matricula',
    'documento',
    'declaracao',
    'historico',
    'transferencia',
}
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
    'orientacao educacional': 'orientacao educacional',
    'orientação educacional': 'orientacao educacional',
}
PUBLIC_ACTIVE_TASK_BY_ACT = {
    'assistant_identity': 'public:assistant_identity',
    'capabilities': 'public:capabilities',
    'access_scope': 'public:access_scope',
    'language_preference': 'public:language_preference',
    'scope_boundary': 'public:scope_boundary',
    'service_routing': 'public:service_routing',
    'auth_guidance': 'public:auth_guidance',
    'document_submission': 'public:document_submission',
    'capacity': 'public:capacity',
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
    'language_preference': 'idioma da conversa',
    'scope_boundary': 'limite de escopo',
    'service_routing': 'setores da escola',
    'auth_guidance': 'conta',
    'document_submission': 'documentos',
    'capacity': 'vagas e capacidade da escola',
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
    'public:language_preference',
    'public:scope_boundary',
}
PUBLIC_SEMANTIC_RESCUE_ACTS = {
    'assistant_identity',
    'capabilities',
    'access_scope',
    'language_preference',
    'scope_boundary',
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
    'public:capacity': 'vagas e capacidade de {entity}',
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
    'privada',
}
FOLLOW_UP_OPENERS = {
    'depois disso',
    'mantendo o contexto anterior',
    'continuando o panorama',
    'seguindo o panorama',
    'agora foque',
    'agora quero apenas',
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
    'mas e ',
    'mas e se',
    'mas e qual',
    'mas e quais',
    'mas e quanto',
    'mas e quando',
    'mas e como',
    'mas e onde',
    'mas e por que',
    'mas e pq',
}
FOLLOW_UP_REFERENTS = {
    'isso',
    'essa',
    'esse',
    'essas',
    'esses',
    'dela',
    'dele',
    'ela',
    'ele',
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
    'qual e o meu escopo',
    'qual é o meu escopo',
    'meu escopo',
    'escopo da minha conta',
    'qual meu acesso',
    'a que dados',
    'que dados eu posso ver',
    'que dados posso ver',
    'o que eu consigo ver',
    'o que consigo ver',
    'o que eu consigo acessar',
    'o que consigo acessar',
    'quais dados eu consigo acessar',
    'quais dados consigo acessar',
    'quais dados dos meus alunos eu consigo acessar',
    'quais dados dos meus dois alunos eu consigo acessar',
    'o que posso consultar aqui',
    'que informacoes consigo obter',
    'que informações consigo obter',
    'qual acesso eu tenho',
    'eu consigo ver o que exatamente',
    'o que exatamente eu consigo ver',
    'academico, financeiro ou os dois',
    'acadêmico, financeiro ou os dois',
    'academico e financeiro',
    'acadêmico e financeiro',
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
    'quem responde por',
    'pra quem eu falo sobre',
    'para quem eu falo sobre',
    'com quem eu falo',
    'com qual contato eu devo falar',
    'qual contato eu devo usar',
    'qual contato devo usar',
    'por qual canal',
    'como falo com',
    'como falar com',
    'como entro em contato',
    'como entrar em contato',
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
    'qual a diferenca entre falar com',
    'qual a diferença entre falar com',
    'diferenca entre secretaria',
    'diferença entre secretaria',
    'secretaria coordenacao orientacao',
    'secretaria coordenação orientação',
    'atendimento comercial',
    'me diga so os canais',
    'me diga só os canais',
    'canais de',
    'uma linha por setor',
    'qual desses setores entra primeiro',
    'nao me manda menu geral',
    'não me manda menu geral',
    'caminho mais curto',
    'nao a lista completa',
    'não a lista completa',
}
PUBLIC_POLICY_TERMS = {
    'politica de avaliacao',
    'política de avaliação',
    'avaliacao, recuperacao e promocao',
    'avaliação, recuperação e promoção',
    'avaliacao recuperacao promocao',
    'avaliação recuperação promoção',
    'recuperacao e promocao',
    'recuperação e promoção',
    'media de aprovacao',
    'média de aprovação',
    'nota de aprovacao',
    'nota de aprovação',
    'projeto de vida',
    'frequencia minima',
    'frequência mínima',
    '75%',
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
    'a',
    'o',
    'as',
    'os',
    'de',
    'da',
    'do',
    'das',
    'dos',
    'e',
    'ou',
    'para',
    'por',
    'com',
    'sem',
    'no',
    'na',
    'nos',
    'nas',
    'um',
    'uma',
    'uns',
    'umas',
    'que',
    'qual',
    'quais',
    'como',
    'quando',
    'onde',
    'porque',
    'por que',
    'se',
    'eu',
    'voce',
    'vocês',
    'me',
    'minha',
    'meu',
    'minhas',
    'meus',
    'ainda',
    'mais',
    'menos',
    'sobre',
    'preciso',
    'precisa',
    'algum',
    'alguma',
    'alguns',
    'algumas',
    'existe',
    'ha',
    'haver',
    'escola',
    'colegio',
    'colégio',
    'bot',
    'telegram',
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
    'pergunta',
    'anterior',
    'usuario',
    'assistente',
    'resposta',
    'ultima',
    'última',
    'fonte',
    'fontes',
}
HIGH_RISK_REASONING_TERMS = {
    'exceto',
    'excecao',
    'exceções',
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
VISUAL_TERMS = {
    'grafico',
    'gráfico',
    'visual',
    'grafica',
    'barra',
    'comparativo',
    'evolucao',
    'evolução',
}


UUID_PATTERN = re.compile(
    r'\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b', re.IGNORECASE
)
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


# Extracted bridge modules. Imported at the end so the shared runtime helper
# namespace is fully defined before the bridge modules reuse it.


def _export_module_namespace(module: object) -> None:
    for name, value in vars(module).items():
        if name.startswith('__'):
            continue
        globals()[name] = value


from . import runtime_api as _runtime_api  # noqa: E402

_export_module_namespace(_runtime_api)

from . import public_profile_runtime as _public_profile_runtime  # noqa: E402

_export_module_namespace(_public_profile_runtime)

from . import workflow_runtime as _workflow_runtime  # noqa: E402

_export_module_namespace(_workflow_runtime)

from . import conversation_focus_runtime as _conversation_focus_runtime  # noqa: E402

_export_module_namespace(_conversation_focus_runtime)

from . import analysis_context_runtime as _analysis_context_runtime  # noqa: E402

_export_module_namespace(_analysis_context_runtime)

from . import intent_analysis_runtime as _intent_analysis_runtime  # noqa: E402

_export_module_namespace(_intent_analysis_runtime)

from . import public_act_rules_runtime as _public_act_rules_runtime  # noqa: E402

_export_module_namespace(_public_act_rules_runtime)

from . import public_orchestration_runtime as _public_orchestration_runtime  # noqa: E402

_export_module_namespace(_public_orchestration_runtime)

from . import reply_experience_runtime as _reply_experience_runtime  # noqa: E402

_export_module_namespace(_reply_experience_runtime)

from . import student_scope_runtime as _student_scope_runtime  # noqa: E402

_export_module_namespace(_student_scope_runtime)

from . import protected_domain_runtime as _protected_domain_runtime  # noqa: E402

_export_module_namespace(_protected_domain_runtime)

from . import protected_summary_runtime as _protected_summary_runtime  # noqa: E402

_export_module_namespace(_protected_summary_runtime)

from . import answer_verification_runtime as _answer_verification_runtime  # noqa: E402

_export_module_namespace(_answer_verification_runtime)

from . import protected_records_runtime as _protected_records_runtime  # noqa: E402

_export_module_namespace(_protected_records_runtime)

from . import structured_tool_runtime as _structured_tool_runtime  # noqa: E402

_export_module_namespace(_structured_tool_runtime)

from . import message_response_runtime as _message_response_runtime  # noqa: E402

_export_module_namespace(_message_response_runtime)
