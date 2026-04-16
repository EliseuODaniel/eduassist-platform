from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any, Literal

import httpx
from eduassist_observability import set_span_attributes
from openai import AsyncOpenAI
from pydantic import BaseModel, Field

from .context_budget import (
    ContextBudgetSnapshot,
    build_context_section_budget,
    estimate_text_tokens,
    pack_context_items,
    pack_context_json_items,
    record_context_budget,
)
from .runtime import (
    _extract_json_object,
    _preview_compact,
    _recent_messages,
    _validated_conversation_act,
    _llm_model_profile,
    _normalize_google_model,
    _contains_term,
    looks_like_high_confidence_public_school_faq,
    looks_like_opaque_short_input,
    looks_like_scope_boundary_candidate,
    looks_like_school_scope_message,
    normalize_ingress_text,
)
from eduassist_observability import (
    extract_google_usage,
    extract_openai_usage,
    normalize_gen_ai_provider_name,
    start_gen_ai_client_operation,
)


TurnScope = Literal["public", "protected", "meta", "unknown"]
TurnRouterConfidenceBucket = Literal["low", "medium", "high"]

_EXPLICIT_UNAUTHENTICATED_TERMS = {
    "nao estou autenticado",
    "não estou autenticado",
    "nao estou logado",
    "não estou logado",
    "sem autenticacao",
    "sem autenticação",
    "sem login",
    "nao tenho acesso",
    "não tenho acesso",
    "nao vinculei",
    "não vinculei",
    "ainda nao vinculei",
    "ainda não vinculei",
    "nao estou vinculado",
    "não estou vinculado",
    "sem vinculo",
    "sem vínculo",
}

_AUTH_GUIDANCE_TERMS = {
    "como vinculo minha conta",
    "como eu vinculo minha conta",
    "como vinculo meu telegram",
    "como eu vinculo meu telegram",
    "como faco o vinculo",
    "como faço o vinculo",
    "codigo de vinculacao",
    "código de vinculação",
    "link_",
}


def _looks_like_explicit_unauthenticated_request(message: str) -> bool:
    normalized = normalize_ingress_text(message)
    if not normalized:
        return False
    return any(term in normalized for term in _EXPLICIT_UNAUTHENTICATED_TERMS | _AUTH_GUIDANCE_TERMS)


def effective_turn_frame_authenticated(
    *,
    authenticated: bool,
    actor_present: bool,
    message: str,
) -> bool:
    if authenticated:
        return True
    if _looks_like_explicit_unauthenticated_request(message):
        return False
    return actor_present


@dataclass(frozen=True)
class CapabilitySpec:
    capability_id: str
    domain: str
    access_tier: str
    scope: TurnScope
    description: str
    aliases: tuple[str, ...]
    follow_up_aliases: tuple[str, ...] = ()
    public_conversation_act: str | None = None
    public_focus_hint: str | None = None
    requested_attribute: str | None = None
    priority: int = 100


class FocusFrame(BaseModel):
    capability_id: str | None = None
    domain: str | None = None
    access_tier: str | None = None
    scope: TurnScope = "unknown"
    active_entity: str | None = None
    active_attribute: str | None = None
    active_actor: str | None = None
    active_targets: list[str] = Field(default_factory=list)
    pending_question_type: str | None = None
    requested_channel: str | None = None
    time_reference: str | None = None
    source: str = "none"
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    recent_user_message: str | None = None
    recent_assistant_message: str | None = None


class CapabilityCandidate(BaseModel):
    capability_id: str
    domain: str
    access_tier: str
    scope: TurnScope
    score: float = Field(default=0.0, ge=0.0)
    reason: str
    public_conversation_act: str | None = None
    public_focus_hint: str | None = None
    requested_attribute: str | None = None


class TurnFrame(BaseModel):
    conversation_act: str = "none"
    capability_id: str | None = None
    domain: str = "unknown"
    access_tier: str = "public"
    scope: TurnScope = "unknown"
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    confidence_bucket: TurnRouterConfidenceBucket = "medium"
    reason: str = ""
    source: str = "heuristic"
    needs_clarification: bool = False
    follow_up_of: str | None = None
    public_conversation_act: str | None = None
    public_focus_hint: str | None = None
    requested_attribute: str | None = None
    candidate_capability_ids: list[str] = Field(default_factory=list)


_GENERIC_FOLLOW_UP_TERMS = {
    "e",
    "e ai",
    "e aí",
    "e quanto",
    "e que horas",
    "e o",
    "e a",
    "e os",
    "e as",
    "e qual",
    "e quais",
    "e quando",
    "qual o proximo vencimento",
    "qual o próximo vencimento",
    "que horas fecha",
    "que horas termina",
    "que horas começa",
    "que horas comeca",
}

_PROTECTED_FINANCE_PERSONAL_TERMS = {
    "meu financeiro",
    "minha situacao financeira",
    "minha situação financeira",
    "meu vencimento",
    "minha fatura",
    "minhas faturas",
    "meu boleto",
    "meus boletos",
    "proximo vencimento",
    "próximo vencimento",
    "em aberto",
    "contas vinculadas",
}

_PROTECTED_ACADEMIC_PERSONAL_TERMS = {
    "minhas notas",
    "meu boletim",
    "minha frequencia",
    "minha frequência",
    "minhas faltas",
    "faltas do",
    "notas do",
    "boletim do",
    "frequencia do",
    "frequência do",
}

_PROTECTED_ADMIN_PERSONAL_TERMS = {
    "documentacao da ana",
    "documentação da ana",
    "documentos da ana",
    "pendencias da ana",
    "pendências da ana",
    "pendencias documentais",
    "pendências documentais",
    "situacao documental",
    "situação documental",
    "pendencia documental",
    "pendência documental",
    "pendencia administrativa",
    "pendência administrativa",
    "status administrativo",
    "status documental",
    "cadastro da ana",
}

_PROTECTED_ACCESS_SCOPE_TERMS = {
    "o que eu consigo consultar",
    "o que eu consigo ver",
    "o que consigo ver",
    "o que eu posso ver",
    "o que posso ver",
    "quero meu escopo",
    "meu escopo",
    "escopo exato",
    "escopo entre academico e financeiro",
    "escopo entre acadêmico e financeiro",
    "quais alunos estao vinculados",
    "quais alunos estão vinculados",
    "quem esta vinculado",
    "quem está vinculado",
}

_TEACHER_SCHEDULE_TERMS = {
    "sou professor",
    "sou professora",
    "meu horario",
    "meu horário",
    "minhas turmas",
    "minhas disciplinas",
    "grade docente",
    "rotina docente",
    "deste ano",
}

_TEACHER_SEGMENT_FOLLOWUP_TERMS = {
    "ensino medio",
    "ensino médio",
    "medio",
    "médio",
    "fundamental",
    "so a parte",
    "só a parte",
    "apenas a parte",
}

_ADMIN_FINANCE_COMBO_ADMIN_TERMS = {
    "documentacao",
    "documentação",
    "documental",
    "cadastro",
    "administrativ",
    "pendenc",
    "regularidade",
}

_ADMIN_FINANCE_COMBO_FINANCE_TERMS = {
    "financeir",
    "mensalidade",
    "fatura",
    "boleto",
    "vencimento",
    "pagamento",
    "cobranca",
    "cobrança",
}

_ADMIN_FINANCE_COMBO_LINK_TERMS = {
    "junto",
    "ao mesmo tempo",
    "ao mesmo passo",
    "impedimento de atendimento",
    "impedimento do atendimento",
    "bloqueio de atendimento",
    "ha impedimento",
    "há impedimento",
}

_ACADEMIC_UPCOMING_TERMS = {
    "proximas provas",
    "próximas provas",
    "proximas avaliacoes",
    "próximas avaliações",
    "avaliacoes previstas",
    "avaliações previstas",
    "cronograma avaliativo",
    "provas e avaliacoes",
    "provas e avaliações",
    "entregas previstas",
}

_ACADEMIC_COMPARISON_TERMS = {
    "compare",
    "compar",
    "comparar",
    "contra",
    "entre ",
    "veredito academico",
    "veredito acadêmico",
}

_ACADEMIC_COMPARISON_ANCHORS = {
    "reprovar",
    "reprov",
    "academ",
    "media minima",
    "média mínima",
    "media parcial",
    "média parcial",
    "componente",
    "disciplina",
}

_EXTERNAL_PUBLIC_FACILITY_TERMS = {
    "da cidade",
    "municipal",
    "prefeitura",
    "publica da cidade",
    "pública da cidade",
    "biblioteca publica",
    "biblioteca pública",
    "publica municipal",
    "pública municipal",
}

_EXTERNAL_PUBLIC_FACILITY_BOUNDARY_TERMS = {
    "fora do colegio",
    "fora do colégio",
    "fora da escola",
    "nao e a biblioteca da escola",
    "não é a biblioteca da escola",
    "nao e biblioteca da escola",
    "não é biblioteca da escola",
    "nao e da escola",
    "não é da escola",
    "nao e do colegio",
    "não é do colégio",
    "fora do colegio horizonte",
    "fora do colégio horizonte",
    "na cidade",
    "da cidade",
    "externa",
    "fora daqui",
}

_RESTRICTED_DOC_ANCHOR_TERMS = {
    "manual interno",
    "protocolo interno",
    "playbook interno",
    "documento interno",
    "documentos internos",
    "material interno",
    "orientacao interna",
    "orientação interna",
    "procedimento interno",
    "fluxo interno",
    "rotina interna",
    "rotinas internas",
    "validacao interna",
    "validação interna",
    "validacoes internas",
    "validações internas",
}

_RESTRICTED_DOC_NOUN_TERMS = {
    "manual",
    "protocolo",
    "playbook",
    "documento",
    "documentos",
    "material",
    "orientacao",
    "orientação",
    "procedimento",
    "fluxo",
    "rotina",
    "validacao",
    "validação",
    "validacoes",
    "validações",
}

_RESTRICTED_DOC_SIGNAL_TERMS = {
    "escopo",
    "telegram",
    "parcial",
    "professor",
    "docente",
    "avaliac",
    "comunic",
    "pedagog",
    "negoci",
    "financeir",
    "quitacao",
    "quitação",
    "promessa de quitacao",
    "promessa de quitação",
    "pagamento",
    "transferenc",
    "secretaria",
    "internacional",
    "hospedagem",
    "viagem",
    "excursao",
    "excursão",
}

_OPEN_TIME_TERMS = {"abre", "abertura"}
_CLOSE_TIME_TERMS = {"fecha", "fechar", "fechamento", "encerra", "encerramento"}

_CAPABILITY_SPECS: tuple[CapabilitySpec, ...] = (
    CapabilitySpec(
        capability_id="public.facilities.library.exists",
        domain="institution",
        access_tier="public",
        scope="public",
        description="confirmar se a escola possui biblioteca",
        aliases=(
            "tem biblioteca",
            "ha biblioteca",
            "há biblioteca",
            "possui biblioteca",
            "existe biblioteca",
        ),
        public_conversation_act="features",
        public_focus_hint="library",
        priority=10,
    ),
    CapabilitySpec(
        capability_id="public.facilities.library.hours",
        domain="institution",
        access_tier="public",
        scope="public",
        description="informar horario de funcionamento da biblioteca",
        aliases=(
            "horario da biblioteca",
            "horário da biblioteca",
            "horario de fechamento da biblioteca",
            "horário de fechamento da biblioteca",
            "horario de abertura da biblioteca",
            "horário de abertura da biblioteca",
            "fechamento da biblioteca",
            "abertura da biblioteca",
            "que horas fecha a biblioteca",
            "que horas abre a biblioteca",
            "ate que horas funciona a biblioteca",
            "até que horas funciona a biblioteca",
            "biblioteca funciona",
        ),
        follow_up_aliases=("que horas fecha", "ate que horas funciona", "até que horas funciona"),
        public_conversation_act="operating_hours",
        public_focus_hint="library",
        priority=9,
    ),
    CapabilitySpec(
        capability_id="public.contacts.leadership",
        domain="institution",
        access_tier="public",
        scope="public",
        description="informar contato da direção ou coordenação",
        aliases=(
            "contato do diretor",
            "contato da diretora",
            "email do diretor",
            "e-mail do diretor",
            "telefone da diretoria",
            "contato da direcao",
            "contato da direção",
            "falar com a direcao",
            "falar com a direção",
        ),
        public_conversation_act="leadership",
        public_focus_hint="leadership",
        requested_attribute="contact",
        priority=8,
    ),
    CapabilitySpec(
        capability_id="public.enrollment.required_documents",
        domain="institution",
        access_tier="public",
        scope="public",
        description="listar documentos exigidos para matrícula",
        aliases=(
            "quais documentos preciso para matricula",
            "quais documentos preciso para matrícula",
            "documentos para matricula",
            "documentos para matrícula",
            "documentos exigidos para matricula",
            "documentos exigidos para matrícula",
            "documentos necessarios para matricula",
            "documentos necessários para matrícula",
        ),
        public_conversation_act="document_submission",
        public_focus_hint="enrollment",
        priority=7,
    ),
    CapabilitySpec(
        capability_id="public.enrollment.pricing",
        domain="institution",
        access_tier="public",
        scope="public",
        description="informar valores públicos de matrícula ou mensalidade",
        aliases=(
            "valor da matricula",
            "valor da matrícula",
            "quanto custa a matricula",
            "quanto custa a matrícula",
            "mensalidade da escola",
            "preco da matricula",
            "preço da matrícula",
            "taxa de matricula",
            "taxa de matrícula",
        ),
        follow_up_aliases=("e a mensalidade", "e o valor", "e a taxa"),
        public_conversation_act="pricing",
        public_focus_hint="pricing",
        priority=6,
    ),
    CapabilitySpec(
        capability_id="public.schedule.shift_offers",
        domain="institution",
        access_tier="public",
        scope="public",
        description="informar turnos e turmas atendidos pela escola",
        aliases=(
            "quais turmas a escola atende",
            "quais turmas",
            "quais turnos",
            "turnos da escola",
            "turno da manhã",
            "turno da manha",
            "manha",
            "manhã",
            "matutino",
            "matutina",
            "vespertino",
            "vespertina",
            "noturno",
            "noturna",
            "integral",
            "tem aula de madrugada",
            "aula de madrugada",
            "madrugada",
        ),
        public_conversation_act="schedule",
        public_focus_hint="shift_offers",
        priority=5,
    ),
    CapabilitySpec(
        capability_id="public.schedule.class_start_time",
        domain="institution",
        access_tier="public",
        scope="public",
        description="informar que horas a aula começa em um turno",
        aliases=(
            "que horas começa a aula",
            "que horas comeca a aula",
            "horario da aula",
            "horário da aula",
            "inicio da aula",
            "início da aula",
            "aula de manhã",
            "aula de manha",
            "aula da manhã",
            "aula da manha",
        ),
        follow_up_aliases=("que horas começa", "que horas comeca", "e que horas começa", "e que horas comeca"),
        public_conversation_act="schedule",
        public_focus_hint="shift_offers",
        requested_attribute="start_time",
        priority=4,
    ),
    CapabilitySpec(
        capability_id="public.schedule.class_end_time",
        domain="institution",
        access_tier="public",
        scope="public",
        description="informar que horas a aula termina em um turno",
        aliases=(
            "que horas termina a aula",
            "que horas acaba a aula",
            "que horas fecha a aula",
            "ate que horas vai a aula",
            "até que horas vai a aula",
            "qual horario da ultima aula",
            "qual horário da última aula",
            "ultima aula",
            "última aula",
        ),
        follow_up_aliases=("que horas termina", "que horas acaba", "e que horas termina", "e que horas acaba"),
        public_conversation_act="schedule",
        public_focus_hint="shift_offers",
        requested_attribute="end_time",
        priority=4,
    ),
    CapabilitySpec(
        capability_id="public.curriculum.overview",
        domain="institution",
        access_tier="public",
        scope="public",
        description="informar base curricular publica, BNCC e componentes ensinados",
        aliases=(
            "o que e bncc",
            "o que é bncc",
            "bncc",
            "curriculo",
            "currículo",
            "conteudo ensinado",
            "conteúdo ensinado",
            "conteudo ensinado em",
            "conteúdo ensinado em",
            "qual o conteudo ensinado em",
            "qual o conteúdo ensinado em",
        ),
        public_conversation_act="curriculum",
        public_focus_hint="curriculum",
        priority=3,
    ),
    CapabilitySpec(
        capability_id="public.identity.confessional",
        domain="institution",
        access_tier="public",
        scope="public",
        description="informar se a escola e confessional ou laica",
        aliases=(
            "colegio confessional",
            "colégio confessional",
            "escola confessional",
            "e um colegio confessional",
            "é um colégio confessional",
            "escola laica",
            "laica",
            "religiosa",
        ),
        public_conversation_act="confessional",
        public_focus_hint="confessional",
        priority=3,
    ),
    CapabilitySpec(
        capability_id="public.web.news",
        domain="institution",
        access_tier="public",
        scope="public",
        description="responder de forma segura sobre noticias recentes e canais oficiais",
        aliases=(
            "ultima noticia sobre o colegio",
            "última notícia sobre o colégio",
            "ultima noticia sobre a escola",
            "última notícia sobre a escola",
            "noticias da escola",
            "notícias da escola",
        ),
        public_conversation_act="web_presence",
        public_focus_hint="news",
        requested_attribute="news",
        priority=3,
    ),
    CapabilitySpec(
        capability_id="public.calendar.year_start",
        domain="calendar",
        access_tier="public",
        scope="public",
        description="informar quando o ano letivo ou as aulas começam",
        aliases=(
            "quando iniciam as aulas",
            "quando começam as aulas",
            "quando comecam as aulas",
            "inicio das aulas",
            "início das aulas",
            "quando inicia o ano letivo",
            "ano letivo",
        ),
        public_conversation_act="timeline",
        public_focus_hint="school_year_start",
        priority=3,
    ),
    CapabilitySpec(
        capability_id="protected.account.access_scope",
        domain="institution",
        access_tier="authenticated",
        scope="protected",
        description="explicar o escopo autenticado da conta entre acadêmico e financeiro",
        aliases=(
            "o que eu consigo consultar",
            "o que eu consigo ver",
            "o que eu posso ver",
            "quero meu escopo",
            "meu escopo exato",
            "escopo entre academico e financeiro",
            "escopo entre acadêmico e financeiro",
            "quais alunos estao vinculados",
            "quais alunos estão vinculados",
        ),
        follow_up_aliases=("e sobre cada um", "e por aluno", "e no telegram"),
        priority=18,
    ),
    CapabilitySpec(
        capability_id="protected.documents.restricted_lookup",
        domain="support",
        access_tier="sensitive",
        scope="protected",
        description="consultar manual, protocolo, playbook ou procedimento interno restrito",
        aliases=(
            "manual interno",
            "protocolo interno",
            "playbook interno",
            "documento interno",
            "material interno",
            "procedimento interno",
            "fluxo interno",
        ),
        priority=18,
    ),
    CapabilitySpec(
        capability_id="protected.institution.admin_finance_status",
        domain="institution",
        access_tier="sensitive",
        scope="protected",
        description="combinar regularidade administrativa e financeiro para apontar impedimentos",
        aliases=(
            "documentacao e financeiro",
            "documentação e financeiro",
            "administrativo e financeiro",
            "administrativa e financeiro",
            "impedimento de atendimento",
            "bloqueio de atendimento",
        ),
        follow_up_aliases=("e isso bloqueia atendimento", "e ha impedimento", "e há impedimento"),
        priority=21,
    ),
    CapabilitySpec(
        capability_id="protected.finance.summary",
        domain="finance",
        access_tier="sensitive",
        scope="protected",
        description="resumo financeiro protegido da família",
        aliases=(
            "meu financeiro",
            "minha situacao financeira",
            "minha situação financeira",
            "resumo financeiro",
            "financeiro da familia",
            "financeiro da família",
        ),
        follow_up_aliases=("e o financeiro", "e meu financeiro"),
        priority=20,
    ),
    CapabilitySpec(
        capability_id="protected.finance.next_due",
        domain="finance",
        access_tier="sensitive",
        scope="protected",
        description="próximo vencimento financeiro protegido",
        aliases=(
            "qual o proximo vencimento",
            "qual o próximo vencimento",
            "proximo vencimento",
            "próximo vencimento",
            "quando vence a proxima fatura",
            "quando vence a próxima fatura",
        ),
        follow_up_aliases=("e o proximo vencimento", "e o próximo vencimento"),
        priority=19,
    ),
    CapabilitySpec(
        capability_id="protected.teacher.schedule",
        domain="academic",
        access_tier="authenticated",
        scope="protected",
        description="consultar grade docente, turmas e disciplinas do professor autenticado",
        aliases=(
            "sou professor",
            "sou professora",
            "meu horario",
            "meu horário",
            "minhas turmas",
            "minhas disciplinas",
            "grade docente",
            "rotina docente",
        ),
        follow_up_aliases=("ensino medio", "ensino médio", "só a parte", "so a parte"),
        priority=28,
    ),
    CapabilitySpec(
        capability_id="protected.academic.upcoming_assessments",
        domain="academic",
        access_tier="authenticated",
        scope="protected",
        description="consultar próximas avaliações por aluno ou agregado familiar",
        aliases=(
            "proximas provas",
            "próximas provas",
            "proximas avaliacoes",
            "próximas avaliações",
            "avaliacoes previstas",
            "avaliações previstas",
            "provas e avaliacoes",
            "provas e avaliações",
        ),
        follow_up_aliases=("e as proximas provas", "e as próximas provas"),
        priority=29,
    ),
    CapabilitySpec(
        capability_id="protected.academic.family_comparison",
        domain="academic",
        access_tier="authenticated",
        scope="protected",
        description="comparar academicamente dois alunos vinculados e apontar o maior risco",
        aliases=(
            "veredito academico",
            "veredito acadêmico",
            "quem esta mais perto de reprovar",
            "quem está mais perto de reprovar",
            "entre ana e lucas",
            "entre lucas e ana",
        ),
        follow_up_aliases=(
            "tira o",
            "mostra so",
            "mostra só",
            "só a ana",
            "so a ana",
            "agora quero apenas",
            "agora quero só",
            "agora quero so",
            "fique apenas com",
            "foque só",
            "foque so",
            "recorte só",
            "recorte so",
            "em quais materias",
            "em quais matérias",
            "em quais disciplinas",
            "mais exposta",
            "mais exposto",
            "mais vulneravel",
            "mais vulnerável",
            "mais fragilizada",
            "mais fragilizado",
        ),
        priority=30,
    ),
    CapabilitySpec(
        capability_id="protected.academic.grades",
        domain="academic",
        access_tier="authenticated",
        scope="protected",
        description="notas e boletim protegidos",
        aliases=(
            "notas do",
            "boletim do",
            "minhas notas",
            "meu boletim",
        ),
        priority=30,
    ),
    CapabilitySpec(
        capability_id="protected.academic.attendance",
        domain="academic",
        access_tier="authenticated",
        scope="protected",
        description="frequência e faltas protegidas",
        aliases=(
            "faltas do",
            "frequencia do",
            "frequência do",
            "minhas faltas",
            "minha frequencia",
            "minha frequência",
        ),
        priority=31,
    ),
    CapabilitySpec(
        capability_id="protected.administrative.status",
        domain="institution",
        access_tier="authenticated",
        scope="protected",
        description="status documental e administrativo protegido",
        aliases=(
            "pendencias documentais",
            "pendências documentais",
            "pendencia documental",
            "pendência documental",
            "pendencias administrativas",
            "pendências administrativas",
            "pendencia administrativa",
            "pendência administrativa",
            "status administrativo",
            "status documental",
            "documentacao da ana",
            "documentação da ana",
            "documentos da ana",
            "cadastro da ana",
        ),
        follow_up_aliases=("e a documentacao", "e a documentação", "e o cadastro"),
        priority=29,
    ),
)

_SPEC_BY_ID = {spec.capability_id: spec for spec in _CAPABILITY_SPECS}


def capability_specs() -> tuple[CapabilitySpec, ...]:
    return _CAPABILITY_SPECS


def capability_spec(capability_id: str | None) -> CapabilitySpec | None:
    return _SPEC_BY_ID.get(str(capability_id or "").strip())


def _merge_focus_with_candidate(
    focus: FocusFrame,
    *,
    candidate: CapabilityCandidate,
    recent_user_message: str | None,
    recent_assistant_message: str | None,
) -> FocusFrame:
    merged_domain = focus.domain if focus.domain and focus.domain != "unknown" else candidate.domain
    merged_scope = focus.scope if focus.scope != "unknown" else candidate.scope
    merged_access_tier = (
        focus.access_tier
        if focus.access_tier and focus.access_tier not in {"public", "unknown"}
        else candidate.access_tier
    )
    merged_attribute = focus.active_attribute or candidate.requested_attribute
    merged_entity = focus.active_entity or candidate.public_focus_hint
    merged_confidence = max(focus.confidence, min(0.92, 0.42 + candidate.score / 10.0))
    return focus.model_copy(
        update={
            "capability_id": candidate.capability_id,
            "domain": merged_domain,
            "scope": merged_scope,
            "access_tier": merged_access_tier,
            "active_attribute": merged_attribute,
            "active_entity": merged_entity,
            "confidence": merged_confidence,
            "recent_user_message": recent_user_message,
            "recent_assistant_message": recent_assistant_message,
        }
    )


def _normalize_lines(conversation_context: dict[str, Any] | None) -> list[tuple[str, str]]:
    if not isinstance(conversation_context, dict):
        return []
    lines: list[tuple[str, str]] = []
    raw_messages = conversation_context.get("recent_messages")
    if not isinstance(raw_messages, list):
        raw_messages = conversation_context.get("messages")
    for item in (raw_messages or [])[-8:]:
        if not isinstance(item, dict):
            continue
        sender = str(item.get("sender_type") or item.get("role") or "").strip().lower()
        content = str(item.get("content") or "").strip()
        if sender and content:
            lines.append((sender, content))
    return lines


def _recent_trace_slot_memory(conversation_context: dict[str, Any] | None) -> dict[str, Any] | None:
    if not isinstance(conversation_context, dict):
        return None
    recent_tool_calls = conversation_context.get("recent_tool_calls")
    if not isinstance(recent_tool_calls, list):
        return None
    for item in reversed(recent_tool_calls[-8:]):
        if not isinstance(item, dict):
            continue
        if str(item.get("tool_name") or "").strip() != "orchestration.trace":
            continue
        request_payload = item.get("request_payload")
        if not isinstance(request_payload, dict):
            continue
        slot_memory = request_payload.get("slot_memory")
        if isinstance(slot_memory, dict) and slot_memory:
            return slot_memory
    return None


def _recent_trace_used_tool(conversation_context: dict[str, Any] | None, tool_name: str) -> bool:
    if not isinstance(conversation_context, dict):
        return False
    recent_tool_calls = conversation_context.get("recent_tool_calls")
    if not isinstance(recent_tool_calls, list):
        return False
    for item in reversed(recent_tool_calls[-8:]):
        if not isinstance(item, dict):
            continue
        if str(item.get("tool_name") or "").strip() != "orchestration.trace":
            continue
        request_payload = item.get("request_payload")
        if not isinstance(request_payload, dict):
            continue
        selected_tools = request_payload.get("selected_tools")
        if not isinstance(selected_tools, list):
            continue
        if any(str(value).strip() == tool_name for value in selected_tools):
            return True
    return False


def _focus_frame_from_trace(conversation_context: dict[str, Any] | None) -> FocusFrame | None:
    slot_memory = _recent_trace_slot_memory(conversation_context)
    if not isinstance(slot_memory, dict):
        if _recent_trace_used_tool(conversation_context, "get_teacher_schedule"):
            return FocusFrame(
                capability_id="protected.teacher.schedule",
                domain="academic",
                access_tier="authenticated",
                scope="protected",
                source="recent_trace",
                confidence=0.76,
            )
        return None
    active_task = str(slot_memory.get("active_task") or "").strip().lower()
    public_entity = str(
        slot_memory.get("public_entity")
        or slot_memory.get("active_entity")
        or ""
    ).strip() or None
    active_attribute = str(
        slot_memory.get("public_attribute")
        or slot_memory.get("finance_attribute")
        or slot_memory.get("academic_attribute")
        or slot_memory.get("admin_attribute")
        or ""
    ).strip() or None
    active_actor = str(
        slot_memory.get("student_name")
        or slot_memory.get("finance_student_name")
        or slot_memory.get("academic_student_name")
        or ""
    ).strip() or None
    active_targets = [
        value
        for value in (
            str(slot_memory.get("academic_student_name") or "").strip() or None,
            str(slot_memory.get("finance_student_name") or "").strip() or None,
        )
        if value
    ]
    pending_question_type = str(slot_memory.get("pending_question_type") or "").strip() or None
    requested_channel = str(slot_memory.get("requested_channel") or "").strip() or None
    time_reference = str(slot_memory.get("time_reference") or "").strip() or None
    capability_id = None
    if public_entity == "library" or active_task == "public:operating_hours":
        capability_id = "public.facilities.library.hours"
    elif active_task == "public:pricing":
        capability_id = "public.enrollment.pricing"
    elif active_task == "public:leadership":
        capability_id = "public.contacts.leadership"
    elif active_task == "finance:summary":
        capability_id = "protected.finance.summary"
    elif active_task == "finance:next_due" or active_attribute == "next_due":
        capability_id = "protected.finance.next_due"
    elif active_task == "academic:grades":
        capability_id = "protected.academic.grades"
    elif active_task == "academic:upcoming" or active_attribute == "upcoming_assessments":
        capability_id = "protected.academic.upcoming_assessments"
    elif active_task == "academic:attendance":
        capability_id = "protected.academic.attendance"
    elif active_task == "admin:access_scope":
        capability_id = "protected.account.access_scope"
    elif active_task in {"admin:administrative_status", "admin:student_administrative_status"}:
        capability_id = "protected.administrative.status"
    elif _recent_trace_used_tool(conversation_context, "get_teacher_schedule"):
        capability_id = "protected.teacher.schedule"
    if active_task.startswith("finance:"):
        return FocusFrame(
            capability_id=capability_id,
            domain="finance",
            access_tier="sensitive",
            scope="protected",
            active_entity=public_entity,
            active_attribute=active_attribute,
            active_actor=active_actor,
            active_targets=active_targets,
            pending_question_type=pending_question_type,
            requested_channel=requested_channel,
            time_reference=time_reference,
            source="recent_trace",
            confidence=0.84,
        )
    if active_task.startswith("academic:"):
        return FocusFrame(
            capability_id=capability_id,
            domain="academic",
            access_tier="authenticated",
            scope="protected",
            active_entity=public_entity,
            active_attribute=active_attribute,
            active_actor=active_actor,
            active_targets=active_targets,
            pending_question_type=pending_question_type,
            requested_channel=requested_channel,
            time_reference=time_reference,
            source="recent_trace",
            confidence=0.84,
        )
    if active_task.startswith("admin:"):
        return FocusFrame(
            capability_id=capability_id,
            domain="institution",
            access_tier="authenticated",
            scope="protected",
            active_entity=public_entity,
            active_attribute=active_attribute,
            active_actor=active_actor,
            active_targets=active_targets,
            pending_question_type=pending_question_type,
            requested_channel=requested_channel,
            time_reference=time_reference,
            source="recent_trace",
            confidence=0.84,
        )
    if active_task.startswith("public:") or public_entity or active_attribute:
        return FocusFrame(
            capability_id=capability_id,
            domain="institution",
            access_tier="public",
            scope="public",
            active_entity=public_entity,
            active_attribute=active_attribute,
            active_actor=active_actor,
            active_targets=active_targets,
            pending_question_type=pending_question_type,
            requested_channel=requested_channel,
            time_reference=time_reference,
            source="recent_trace",
            confidence=0.78,
        )
    if capability_id == "protected.teacher.schedule":
        return FocusFrame(
            capability_id=capability_id,
            domain="academic",
            access_tier="authenticated",
            scope="protected",
            active_entity="teacher_schedule",
            active_attribute=active_attribute,
            active_actor=active_actor,
            active_targets=active_targets,
            pending_question_type=pending_question_type,
            requested_channel=requested_channel,
            time_reference=time_reference,
            source="recent_trace",
            confidence=0.78,
        )
    return None


def _looks_like_access_scope_request(normalized_message: str) -> bool:
    if not normalized_message:
        return False
    if any(_contains_term(normalized_message, term) for term in _PROTECTED_ACCESS_SCOPE_TERMS):
        return True
    return "escopo" in normalized_message and any(
        _contains_term(normalized_message, term)
        for term in ("academico", "acadêmico", "financeiro", "telegram")
    )


def _looks_like_teacher_schedule_request(normalized_message: str, focus: FocusFrame) -> bool:
    if not normalized_message:
        return False
    if any(_contains_term(normalized_message, term) for term in _TEACHER_SCHEDULE_TERMS):
        return True
    if focus.capability_id == "protected.teacher.schedule" and _looks_like_contextual_follow_up(
        normalized_message,
        focus=focus,
    ):
        if any(_contains_term(normalized_message, term) for term in _TEACHER_SEGMENT_FOLLOWUP_TERMS):
            return True
        return any(
            _contains_term(normalized_message, term)
            for term in ("turmas", "disciplinas", "grade", "agenda", "horario", "horário")
        )
    return False


def _looks_like_admin_finance_combo_request(normalized_message: str) -> bool:
    if not normalized_message:
        return False
    has_admin = any(term in normalized_message for term in _ADMIN_FINANCE_COMBO_ADMIN_TERMS)
    has_finance = any(term in normalized_message for term in _ADMIN_FINANCE_COMBO_FINANCE_TERMS)
    if not (has_admin and has_finance):
        return False
    return True


def _looks_like_upcoming_assessments_request(normalized_message: str) -> bool:
    return bool(normalized_message) and any(
        _contains_term(normalized_message, term) for term in _ACADEMIC_UPCOMING_TERMS
    )


def _looks_like_academic_comparison_request(normalized_message: str) -> bool:
    if not normalized_message:
        return False
    has_compare = any(term in normalized_message for term in _ACADEMIC_COMPARISON_TERMS)
    has_academic_anchor = any(term in normalized_message for term in _ACADEMIC_COMPARISON_ANCHORS)
    if has_compare and has_academic_anchor:
        return True
    if any(
        _contains_term(normalized_message, term)
        for term in (
            "panorama academico das contas vinculadas",
            "quem hoje exige maior atencao academica",
            "quem hoje exige maior atenção acadêmica",
        )
    ):
        return True
    has_family_anchor = any(
        _contains_term(normalized_message, term)
        for term in (
            "meus filhos",
            "meus dois filhos",
            "contas vinculadas",
            "ana",
            "lucas",
        )
    )
    has_risk_anchor = any(
        _contains_term(normalized_message, term)
        for term in (
            "mais vulneravel",
            "mais vulnerável",
            "mais exposta",
            "mais exposto",
            "mais fragil",
            "mais frágil",
            "limite de aprovacao",
            "limite de aprovação",
            "media minima",
            "média mínima",
            "mais perto da media minima",
            "mais perto da média mínima",
            "mais perto do limite de aprovacao",
            "mais perto do limite de aprovação",
            "maior atencao academica",
            "maior atenção acadêmica",
            "disciplina",
            "disciplinas",
            "componente",
            "componentes",
            "materias",
            "matérias",
        )
    )
    return has_family_anchor and has_risk_anchor


def _looks_like_follow_up(normalized_message: str) -> bool:
    if not normalized_message:
        return False
    if len(normalized_message.split()) <= 6 and any(
        _contains_term(normalized_message, term) for term in _GENERIC_FOLLOW_UP_TERMS
    ):
        return True
    return normalized_message.startswith(("e ", "mas ", "agora ", "entao ", "então "))


def _looks_like_contextual_follow_up(
    normalized_message: str,
    *,
    focus: FocusFrame,
    top_candidate: CapabilityCandidate | None = None,
) -> bool:
    if _looks_like_follow_up(normalized_message):
        return True
    if not normalized_message:
        return False
    focus_has_context = bool(
        focus.capability_id
        or (
            focus.domain
            and focus.domain != "unknown"
            and focus.scope != "unknown"
        )
    )
    if not focus_has_context or not focus.pending_question_type:
        return False
    if (
        top_candidate is not None
        and focus.capability_id
        and top_candidate.capability_id != focus.capability_id
    ):
        return False
    continuity_terms = (
        "mantendo o contexto anterior",
        "sem repetir tudo",
        "so a parte",
        "só a parte",
        "apenas a parte",
        "agora so",
        "agora só",
        "isole apenas",
        "agora quero apenas",
        "agora quero só",
        "agora quero so",
        "quero apenas",
        "fique apenas com",
        "seguindo o panorama",
        "depois do panorama",
        "mantendo a comparacao",
        "mantendo a comparação",
    )
    if any(_contains_term(normalized_message, term) for term in continuity_terms):
        return True
    if focus.capability_id == "protected.teacher.schedule" and any(
        _contains_term(normalized_message, term) for term in _TEACHER_SEGMENT_FOLLOWUP_TERMS
    ):
        if _looks_like_follow_up(normalized_message):
            return True
        if len(normalized_message.split()) <= 3 and focus.pending_question_type in {"follow_up", "attribute_query"}:
            return True
        if any(
            _contains_term(normalized_message, term)
            for term in (
                "mantendo o contexto",
                "contexto anterior",
                "apenas a parte",
                "so a parte",
                "só a parte",
                "parte do",
                "recorte",
            )
        ):
            return True
    if (
        focus.capability_id == "protected.academic.attendance"
        and (
            focus.active_targets
            or focus.active_actor
            or focus.pending_question_type in {"follow_up", "attribute_query"}
        )
    ):
        has_target_focus = _mentions_focus_target(normalized_message, focus)
        has_attendance_focus = any(
            _contains_term(normalized_message, term)
            for term in (
                "frequencia",
                "frequência",
                "falta",
                "faltas",
                "ausencias",
                "ausências",
                "atrasos",
                "presenca",
                "presença",
                "alerta",
                "risco",
                "sensivel",
                "sensível",
                "concreto",
                "principal",
            )
        )
        if has_target_focus and has_attendance_focus:
            return True
    if (
        focus.capability_id == "protected.academic.family_comparison"
        and (
            focus.active_targets
            or focus.active_actor
            or focus.pending_question_type in {"follow_up", "attribute_query"}
        )
    ):
        has_target_focus = _mentions_focus_target(normalized_message, focus)
        has_academic_focus = any(
            _contains_term(normalized_message, term)
            for term in (
                "materias",
                "matérias",
                "disciplinas",
                "componente",
                "componentes",
                "vulneravel",
                "vulnerável",
                "fragil",
                "frágil",
                "fragilizada",
                "fragilizado",
                "exposta",
                "exposto",
                "risco",
                "alerta",
                "mais exposta",
                "mais exposto",
                "mais vulneravel",
                "mais vulnerável",
                "ponto mais fraco",
            )
        )
        if has_target_focus and has_academic_focus:
            return True
    return False


def _mentions_focus_target(normalized_message: str, focus: FocusFrame) -> bool:
    targets = [target for target in [*focus.active_targets, focus.active_actor] if target]
    if not normalized_message or not targets:
        return False
    for target in targets:
        normalized_target = normalize_ingress_text(target)
        if normalized_target and _contains_term(normalized_message, normalized_target):
            return True
        first_name = normalized_target.split()[0] if normalized_target else ""
        if len(first_name) >= 3 and _contains_term(normalized_message, first_name):
            return True
    return False


def _looks_like_attendance_target_follow_up(normalized_message: str, focus: FocusFrame) -> bool:
    if focus.capability_id != "protected.academic.attendance" or focus.scope != "protected":
        return False
    if not normalized_message:
        return False
    if not _mentions_focus_target(normalized_message, focus):
        return False
    has_attendance_focus = any(
        _contains_term(normalized_message, term)
        for term in (
            "frequencia",
            "frequência",
            "falta",
            "faltas",
            "ausencias",
            "ausências",
            "atrasos",
            "presenca",
            "presença",
            "alerta",
            "risco",
            "concreto",
            "principal",
            "mais concreto",
            "mais sensivel",
            "mais sensível",
        )
    )
    if not has_attendance_focus:
        return False
    return _looks_like_contextual_follow_up(normalized_message, focus=focus) or any(
        _contains_term(normalized_message, term)
        for term in (
            "mantendo o contexto",
            "continuando a analise",
            "continuando a análise",
            "corta para",
            "recorte so",
            "recorte só",
            "isole",
            "resuma",
            "resume",
            "agora",
        )
    )


def _looks_like_external_public_facility_query(normalized_message: str) -> bool:
    if not normalized_message:
        return False
    if not any(_contains_term(normalized_message, term) for term in ("biblioteca", "library")):
        return False
    mentions_school = any(
        _contains_term(normalized_message, term)
        for term in ("escola", "colegio", "colégio", "horizonte")
    )
    explicit_external_boundary = any(
        _contains_term(normalized_message, term)
        for term in _EXTERNAL_PUBLIC_FACILITY_BOUNDARY_TERMS
    )
    if mentions_school and not explicit_external_boundary:
        return False
    return any(_contains_term(normalized_message, term) for term in _EXTERNAL_PUBLIC_FACILITY_TERMS)


def _requested_attribute_for_spec(*, spec: CapabilitySpec, normalized_message: str) -> str | None:
    if spec.capability_id == "public.facilities.library.hours":
        if any(_contains_term(normalized_message, term) for term in _CLOSE_TIME_TERMS):
            return "close_time"
        if any(_contains_term(normalized_message, term) for term in _OPEN_TIME_TERMS):
            return "open_time"
    return spec.requested_attribute


def _looks_like_restricted_document_query(normalized_message: str) -> bool:
    if not normalized_message:
        return False
    if any(_contains_term(normalized_message, term) for term in _RESTRICTED_DOC_ANCHOR_TERMS):
        return True
    noun_hits = sum(
        1 for term in _RESTRICTED_DOC_NOUN_TERMS if _contains_term(normalized_message, term)
    )
    if noun_hits == 0:
        return False
    signal_hits = sum(
        1 for term in _RESTRICTED_DOC_SIGNAL_TERMS if _contains_term(normalized_message, term)
    )
    return signal_hits >= 1


def derive_focus_frame(
    *,
    conversation_context: dict[str, Any] | None,
    authenticated: bool,
) -> FocusFrame:
    recent_lines = _normalize_lines(conversation_context)
    recent_user_message = next((content for sender, content in reversed(recent_lines) if sender == "user"), None)
    recent_assistant_message = next((content for sender, content in reversed(recent_lines) if sender == "assistant"), None)
    traced_focus = _focus_frame_from_trace(conversation_context)
    traced_focus_with_history = (
        traced_focus.model_copy(
            update={
                "recent_user_message": recent_user_message,
                "recent_assistant_message": recent_assistant_message,
            }
        )
        if traced_focus is not None
        else None
    )
    if traced_focus_with_history is not None and traced_focus_with_history.capability_id:
        return traced_focus_with_history
    for source_name, message in (
        ("recent_user", recent_user_message),
        ("recent_assistant", recent_assistant_message),
    ):
        if not message:
            continue
        candidates = build_capability_candidates(
            message=message,
            conversation_context=None,
            authenticated=authenticated,
        )
        if not candidates:
            continue
        top = candidates[0]
        if top.score < 4.0:
            continue
        if traced_focus_with_history is not None:
            same_scope = top.scope == traced_focus_with_history.scope
            same_domain = (
                traced_focus_with_history.domain in {None, "", "unknown"}
                or top.domain == traced_focus_with_history.domain
            )
            if same_scope and same_domain:
                return _merge_focus_with_candidate(
                    traced_focus_with_history,
                    candidate=top,
                    recent_user_message=recent_user_message,
                    recent_assistant_message=recent_assistant_message,
                )
        return FocusFrame(
            capability_id=top.capability_id,
            domain=top.domain,
            access_tier=top.access_tier,
            scope=top.scope,
            active_attribute=top.requested_attribute,
            active_entity=top.public_focus_hint,
            source=source_name,
            confidence=min(0.95, 0.45 + top.score / 10.0),
            recent_user_message=recent_user_message,
            recent_assistant_message=recent_assistant_message,
        )
    if traced_focus_with_history is not None:
        return traced_focus_with_history
    return FocusFrame(
        recent_user_message=recent_user_message,
        recent_assistant_message=recent_assistant_message,
    )


def build_capability_candidates(
    *,
    message: str,
    conversation_context: dict[str, Any] | None,
    authenticated: bool,
) -> list[CapabilityCandidate]:
    normalized = normalize_ingress_text(message)
    if not normalized:
        return []
    if _looks_like_external_public_facility_query(normalized):
        return []
    focus = derive_focus_frame(conversation_context=conversation_context, authenticated=authenticated)
    follow_up = _looks_like_follow_up(normalized)
    contextual_follow_up = _looks_like_contextual_follow_up(normalized, focus=focus)
    high_confidence_public = looks_like_high_confidence_public_school_faq(message)
    candidates: list[CapabilityCandidate] = []
    for spec in capability_specs():
        if spec.scope == "protected" and not authenticated:
            continue
        score = 0.0
        reasons: list[str] = []
        if (
            spec.capability_id == "protected.documents.restricted_lookup"
            and _looks_like_restricted_document_query(normalized)
        ):
            score += 4.2
            reasons.append("restricted_document_anchor")
        if spec.capability_id == "protected.account.access_scope" and _looks_like_access_scope_request(normalized):
            score += 4.6
            reasons.append("access_scope_anchor")
        if spec.capability_id == "protected.teacher.schedule" and _looks_like_teacher_schedule_request(normalized, focus):
            score += 4.4
            reasons.append("teacher_schedule_anchor")
        if spec.capability_id == "protected.institution.admin_finance_status" and _looks_like_admin_finance_combo_request(normalized):
            score += 4.8
            reasons.append("admin_finance_combo_anchor")
        if spec.capability_id == "protected.academic.upcoming_assessments" and _looks_like_upcoming_assessments_request(normalized):
            score += 4.0
            reasons.append("upcoming_assessments_anchor")
        if spec.capability_id == "protected.academic.family_comparison" and _looks_like_academic_comparison_request(normalized):
            score += 4.2
            reasons.append("academic_comparison_anchor")
        if spec.capability_id == "protected.academic.attendance" and _looks_like_attendance_target_follow_up(
            normalized,
            focus,
        ):
            score += 4.6
            reasons.append("attendance_target_follow_up_anchor")
        for alias in spec.aliases:
            if _contains_term(normalized, alias):
                score += 3.0
                reasons.append(f"alias:{normalize_ingress_text(alias)}")
        follow_up_alias_enabled = contextual_follow_up and (
            focus.capability_id == spec.capability_id
            or (focus.domain == spec.domain and focus.scope == spec.scope)
        )
        for alias in spec.follow_up_aliases:
            if follow_up_alias_enabled and _contains_term(normalized, alias):
                score += 2.5
                reasons.append(f"followup_alias:{normalize_ingress_text(alias)}")
        if spec.scope == "public" and high_confidence_public:
            score += 0.8
            reasons.append("public_school_faq")
        if spec.scope == "protected" and any(
            _contains_term(normalized, term)
            for term in (
                _PROTECTED_FINANCE_PERSONAL_TERMS
                if spec.domain == "finance"
                else _PROTECTED_ACADEMIC_PERSONAL_TERMS
                if spec.domain == "academic"
                else _PROTECTED_ADMIN_PERSONAL_TERMS
            )
        ):
            score += 1.6
            reasons.append("protected_personal_anchor")
        if focus.capability_id == spec.capability_id and contextual_follow_up:
            score += 2.2
            reasons.append("follow_up_same_capability")
        elif focus.domain == spec.domain and focus.scope == spec.scope and contextual_follow_up:
            score += 1.2
            reasons.append("follow_up_same_domain")
        if follow_up and focus.active_entity:
            entity_normalized = normalize_ingress_text(focus.active_entity)
            if entity_normalized and _contains_term(normalized, entity_normalized):
                score += 1.4
                reasons.append("follow_up_same_entity")
        requested_attribute = _requested_attribute_for_spec(
            spec=spec,
            normalized_message=normalized,
        )
        if follow_up and focus.active_attribute and requested_attribute == focus.active_attribute:
            score += 0.9
            reasons.append("follow_up_same_attribute")
        if (
            follow_up
            and focus.scope == "protected"
            and focus.active_actor
            and spec.scope == "protected"
        ):
            score += 0.6
            reasons.append("follow_up_same_actor")
        if spec.scope == "public" and any(
            _contains_term(normalized, alias) for alias in ("escola", "colegio", "colégio")
        ):
            score += 0.4
        if score <= 0.0:
            continue
        candidates.append(
            CapabilityCandidate(
                capability_id=spec.capability_id,
                domain=spec.domain,
                access_tier=spec.access_tier,
                scope=spec.scope,
                score=score,
                reason=";".join(reasons) or "alias_match",
                public_conversation_act=spec.public_conversation_act,
                public_focus_hint=spec.public_focus_hint,
                requested_attribute=requested_attribute,
            )
        )
    candidates.sort(key=lambda item: (-item.score, item.capability_id))
    return candidates[:5]


def build_turn_frame_hint(
    *,
    message: str,
    conversation_context: dict[str, Any] | None,
    preview: dict[str, Any] | None,
    authenticated: bool,
) -> TurnFrame | None:
    normalized = normalize_ingress_text(message)
    if not normalized:
        return None
    if _looks_like_external_public_facility_query(normalized):
        return TurnFrame(
            conversation_act="scope_boundary",
            confidence=0.82,
            confidence_bucket="high",
            reason="external_public_facility_turn_hint",
            source="heuristic",
        )
    candidates = build_capability_candidates(
        message=message,
        conversation_context=conversation_context,
        authenticated=authenticated,
    )
    if not authenticated:
        auth_candidates = [
            candidate
            for candidate in build_capability_candidates(
                message=message,
                conversation_context=conversation_context,
                authenticated=True,
            )
            if candidate.capability_id != "protected.documents.restricted_lookup"
            and (spec := capability_spec(candidate.capability_id)) is not None
            and spec.scope == "protected"
        ]
        if auth_candidates:
            top = auth_candidates[0]
            second = auth_candidates[1] if len(auth_candidates) > 1 else None
            margin = top.score - (second.score if second is not None else 0.0)
            confidence = min(0.96, 0.48 + top.score / 12.0 + max(0.0, margin) / 24.0)
            return TurnFrame(
                conversation_act="auth_guidance",
                domain="institution",
                access_tier="public",
                scope="public",
                confidence=confidence,
                confidence_bucket="high" if confidence >= 0.82 else "medium",
                reason=f"protected_requires_auth:{top.capability_id}",
                source="heuristic",
                public_conversation_act="auth_guidance",
                requested_attribute=top.requested_attribute,
                candidate_capability_ids=[candidate.capability_id for candidate in auth_candidates[:5]],
            )
    if not candidates:
        if looks_like_opaque_short_input(message):
            return TurnFrame(
                conversation_act="input_clarification",
                confidence=0.72,
                confidence_bucket="medium",
                reason="opaque_short_input_turn_hint",
                source="heuristic",
                needs_clarification=True,
            )
        if looks_like_scope_boundary_candidate(message) and not looks_like_school_scope_message(message):
            return TurnFrame(
                conversation_act="scope_boundary",
                confidence=0.74,
                confidence_bucket="medium",
                reason="scope_boundary_turn_hint",
                source="heuristic",
            )
        return None
    top = candidates[0]
    second = candidates[1] if len(candidates) > 1 else None
    margin = top.score - (second.score if second is not None else 0.0)
    confidence = min(0.98, 0.40 + top.score / 10.0 + max(0.0, margin) / 20.0)
    if top.score < 3.0:
        return None
    if second is not None and margin < 0.75 and top.score < 5.5:
        return TurnFrame(
            conversation_act="none",
            confidence=max(0.35, confidence - 0.15),
            confidence_bucket="low",
            reason=f"ambiguous_candidates:{top.capability_id}:{second.capability_id}",
            source="heuristic",
            needs_clarification=True,
            candidate_capability_ids=[candidate.capability_id for candidate in candidates],
        )
    focus = derive_focus_frame(
        conversation_context=conversation_context,
        authenticated=authenticated,
    )
    contextual_follow_up = _looks_like_contextual_follow_up(normalized, focus=focus, top_candidate=top)
    follow_up_of = None
    if contextual_follow_up:
        if focus.capability_id:
            follow_up_of = focus.capability_id
        elif focus.scope == top.scope and focus.domain == top.domain:
            follow_up_of = top.capability_id
    return TurnFrame(
        # Strong capability matches should stay capability-led. Let scope
        # boundary heuristics win only in the explicit no-capability branches
        # above, otherwise protected/public intents can be incorrectly
        # downgraded to generic boundaries.
        conversation_act="none",
        capability_id=top.capability_id,
        domain=top.domain,
        access_tier=top.access_tier,
        scope=top.scope,
        confidence=confidence,
        confidence_bucket="high" if confidence >= 0.82 else "medium",
        reason=f"deterministic_candidate:{top.reason}",
        source="heuristic",
        public_conversation_act=top.public_conversation_act,
        public_focus_hint=top.public_focus_hint,
        requested_attribute=top.requested_attribute,
        candidate_capability_ids=[candidate.capability_id for candidate in candidates],
        follow_up_of=follow_up_of,
    )


def _router_instructions(stack_label: str) -> str:
    return (
        f"Voce e o roteador semantico estruturado do caminho {stack_label}. "
        "Voce nao responde ao usuario. Sua funcao e escolher uma capability canonica entre as candidatas fornecidas. "
        "Devolva somente JSON com as chaves: capability_id, confidence_bucket, needs_clarification, follow_up_of, reason. "
        "Use capability_id=none quando nenhuma capability estiver forte o bastante. "
        "Se a pergunta atual for publica e institucional, prefira a capability publica correta mesmo quando o usuario estiver autenticado. "
        "So use needs_clarification=true quando a pergunta estiver realmente ambigua entre candidatas plausiveis. "
        "Nao force capability protegida quando a pergunta atual for claramente FAQ publica da escola."
    )


def _semantic_router_history_budget_tokens(settings: Any) -> int:
    return max(64, int(getattr(settings, "semantic_router_history_budget_tokens", 180) or 180))


def _semantic_router_candidate_budget_tokens(settings: Any) -> int:
    return max(96, int(getattr(settings, "semantic_router_candidate_budget_tokens", 220) or 220))


def _recent_history_lines(conversation_context: dict[str, Any] | None) -> list[str]:
    history_block = _recent_messages(conversation_context, limit=32)
    if not history_block or history_block.strip() == "- nenhum":
        return []
    return [line for line in history_block.splitlines() if line.strip()]


def _router_prompt(
    *,
    request_message: str,
    preview: dict[str, Any] | None,
    history_block: str,
    candidates_payload: list[dict[str, Any]],
    focus: FocusFrame,
) -> str:
    return (
        "Escolha a capability mais adequada para o turno atual.\n\n"
        f"Preview atual:\n{_preview_compact(preview)}\n\n"
        f"Historico recente:\n{history_block}\n\n"
        f"Focus frame:\n{json.dumps(focus.model_dump(mode='json'), ensure_ascii=False, sort_keys=True)}\n\n"
        f"Candidatas:\n{json.dumps(candidates_payload, ensure_ascii=False, sort_keys=True)}\n\n"
        f"Mensagem atual:\n{request_message}\n\n"
        "Regras:\n"
        "- preserve a pergunta atual acima do contexto herdado.\n"
        "- follow_up_of so deve ser preenchido se a pergunta atual for claramente eliptica.\n"
        "- perguntas publicas sobre biblioteca, matricula, horarios, direcao, calendario e turnos devem ficar no escopo publico.\n"
        "- perguntas como 'qual o proximo vencimento' so vao para protegido se houver contexto financeiro recente ou ancoras pessoais.\n"
        "- se a escolha mais segura for pedir esclarecimento, use capability_id=none e needs_clarification=true."
    )


def _record_turn_router_context_budget(
    *,
    stack_label: str,
    request_message: str,
    instructions: str,
    prompt: str,
    history_budget: Any,
    candidate_budget: Any,
    preview: dict[str, Any] | None,
    focus: FocusFrame,
) -> None:
    snapshot = ContextBudgetSnapshot(
        pipeline="turn_router",
        stack_label=stack_label,
        estimated_prompt_tokens=estimate_text_tokens(prompt),
        estimated_instruction_tokens=estimate_text_tokens(instructions),
        estimated_request_tokens=estimate_text_tokens(request_message),
        estimated_candidate_tokens=candidate_budget.estimated_tokens,
        candidate_count=candidate_budget.total_items,
        history=build_context_section_budget(
            rendered_text=history_budget.rendered_text,
            total_items=history_budget.total_items,
            used_items=history_budget.used_items,
        ),
    )
    record_context_budget(snapshot)
    preview_reason = str((preview or {}).get("reason") or "").strip()
    if preview_reason or focus.capability_id:
        extra_attrs: dict[str, Any] = {}
        if preview_reason:
            extra_attrs["eduassist.context.preview_reason"] = preview_reason
        if focus.capability_id:
            extra_attrs["eduassist.context.focus_capability_id"] = focus.capability_id
        set_span_attributes(**extra_attrs)


async def _turn_router_text_call(
    *,
    settings: Any,
    stack_label: str,
    request_message: str,
    conversation_context: dict[str, Any] | None,
    preview: dict[str, Any] | None,
    candidates: list[CapabilityCandidate],
    focus: FocusFrame,
) -> str | None:
    instructions = _router_instructions(stack_label)
    history_budget = pack_context_items(
        _recent_history_lines(conversation_context),
        token_budget=_semantic_router_history_budget_tokens(settings),
        empty_text="- nenhum",
        keep_last=True,
    )
    candidate_payloads = [
        {
            "capability_id": candidate.capability_id,
            "domain": candidate.domain,
            "access_tier": candidate.access_tier,
            "scope": candidate.scope,
            "reason": candidate.reason,
            "score": round(candidate.score, 2),
        }
        for candidate in candidates
    ]
    packed_candidates, candidate_budget = pack_context_json_items(
        candidate_payloads,
        token_budget=_semantic_router_candidate_budget_tokens(settings),
        empty_text="[]",
    )
    prompt = _router_prompt(
        request_message=request_message,
        preview=preview,
        history_block=history_budget.rendered_text,
        candidates_payload=packed_candidates,
        focus=focus,
    )
    _record_turn_router_context_budget(
        stack_label=stack_label,
        request_message=request_message,
        instructions=instructions,
        prompt=prompt,
        history_budget=history_budget,
        candidate_budget=candidate_budget,
        preview=preview,
        focus=focus,
    )
    provider = str(getattr(settings, "llm_provider", "openai") or "openai").strip().lower()
    if provider == "openai" and getattr(settings, "openai_api_key", None):
        openai_base_url = str(getattr(settings, "openai_base_url", "https://api.openai.com/v1"))
        openai_model = str(getattr(settings, "openai_model", "gpt-5.4"))
        provider_name = normalize_gen_ai_provider_name("openai", base_url=openai_base_url)
        with start_gen_ai_client_operation(
            provider_name=provider_name,
            operation_name="turn_frame_classification",
            request_model=openai_model,
            base_url=openai_base_url,
            llm_model_profile=_llm_model_profile(settings),
        ) as operation:
            try:
                client = AsyncOpenAI(api_key=settings.openai_api_key, base_url=openai_base_url)
                response = await client.responses.create(
                    model=openai_model,
                    instructions=instructions,
                    input=prompt,
                )
                text = (response.output_text or "").strip()
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
    if provider in {"google", "gemini", "litellm"} and getattr(settings, "google_api_key", None):
        model_name = _normalize_google_model(getattr(settings, "google_model", "gemini-2.5-flash"))
        endpoint = str(
            getattr(
                settings, "google_api_base_url", "https://generativelanguage.googleapis.com/v1beta"
            )
        ).rstrip("/")
        payload = {
            "system_instruction": {"parts": [{"text": instructions}]},
            "contents": [{"role": "user", "parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.0,
                "topP": 0.9,
                "maxOutputTokens": 220,
            },
        }
        url = f"{endpoint}/{model_name}:generateContent"
        provider_name = normalize_gen_ai_provider_name("google", base_url=endpoint)
        with start_gen_ai_client_operation(
            provider_name=provider_name,
            operation_name="turn_frame_classification",
            request_model=model_name,
            base_url=endpoint,
            request_temperature=0.0,
            request_max_tokens=220,
            request_top_p=0.9,
            llm_model_profile=_llm_model_profile(settings),
        ) as operation:
            try:
                async with httpx.AsyncClient(timeout=20.0) as client:
                    response = await client.post(
                        url,
                        params={"key": str(settings.google_api_key)},
                        json=payload,
                    )
                    response.raise_for_status()
                    body = response.json()
            except Exception as exc:
                operation.finish(error_type=exc.__class__.__name__)
                return None
            if not isinstance(body, dict):
                operation.finish(error_type="invalid_payload")
                return None
            operation.finish(usage=extract_google_usage(body, request_model=model_name))
        candidates_payload = body.get("candidates") if isinstance(body, dict) else None
        if not isinstance(candidates_payload, list):
            return None
        fragments: list[str] = []
        for candidate in candidates_payload:
            if not isinstance(candidate, dict):
                continue
            content = candidate.get("content")
            parts = content.get("parts") if isinstance(content, dict) else None
            if not isinstance(parts, list):
                continue
            for part in parts:
                if isinstance(part, dict):
                    text = str(part.get("text") or "").strip()
                    if text:
                        fragments.append(text)
        return "\n".join(fragments).strip() or None
    return None


async def resolve_turn_frame_with_provider(
    *,
    settings: Any,
    stack_label: str,
    request_message: str,
    conversation_context: dict[str, Any] | None,
    preview: dict[str, Any] | None,
    authenticated: bool,
) -> TurnFrame | None:
    deterministic = build_turn_frame_hint(
        message=request_message,
        conversation_context=conversation_context,
        preview=preview,
        authenticated=authenticated,
    )
    if deterministic is not None and (
        deterministic.capability_id is None
        or deterministic.needs_clarification
        or deterministic.confidence >= 0.9
        or len(deterministic.candidate_capability_ids) <= 1
    ):
        return deterministic
    candidates = build_capability_candidates(
        message=request_message,
        conversation_context=conversation_context,
        authenticated=authenticated,
    )
    if not candidates:
        return deterministic
    focus = derive_focus_frame(
        conversation_context=conversation_context,
        authenticated=authenticated,
    )
    text = await _turn_router_text_call(
        settings=settings,
        stack_label=stack_label,
        request_message=request_message,
        conversation_context=conversation_context,
        preview=preview,
        candidates=candidates,
        focus=focus,
    )
    if not text:
        return deterministic
    payload = _extract_json_object(text)
    if not isinstance(payload, dict):
        return deterministic
    capability_id = str(payload.get("capability_id") or "").strip()
    if capability_id in {"", "none"}:
        if bool(payload.get("needs_clarification")):
            return TurnFrame(
                conversation_act="input_clarification",
                confidence=0.62,
                confidence_bucket="low",
                reason=str(payload.get("reason") or "router_needs_clarification").strip() or "router_needs_clarification",
                source="llm",
                needs_clarification=True,
                candidate_capability_ids=[candidate.capability_id for candidate in candidates],
            )
        return deterministic
    spec = capability_spec(capability_id)
    if spec is None:
        return deterministic
    confidence_bucket = str(payload.get("confidence_bucket") or "medium").strip().lower()
    if confidence_bucket not in {"low", "medium", "high"}:
        confidence_bucket = "medium"
    confidence = {"low": 0.55, "medium": 0.76, "high": 0.9}[confidence_bucket]
    return TurnFrame(
        conversation_act="none",
        capability_id=spec.capability_id,
        domain=spec.domain,
        access_tier=spec.access_tier,
        scope=spec.scope,
        confidence=confidence,
        confidence_bucket=confidence_bucket,  # type: ignore[arg-type]
        reason=str(payload.get("reason") or "llm_turn_router").strip() or "llm_turn_router",
        source="llm",
        needs_clarification=bool(payload.get("needs_clarification")),
        follow_up_of=str(payload.get("follow_up_of") or "").strip() or deterministic.follow_up_of if deterministic else None,
        public_conversation_act=spec.public_conversation_act,
        public_focus_hint=spec.public_focus_hint,
        requested_attribute=_requested_attribute_for_spec(
            spec=spec,
            normalized_message=normalize_ingress_text(request_message),
        ),
        candidate_capability_ids=[candidate.capability_id for candidate in candidates],
    )
