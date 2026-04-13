from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any, Literal

import httpx
from openai import AsyncOpenAI
from pydantic import BaseModel, Field

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
)

_SPEC_BY_ID = {spec.capability_id: spec for spec in _CAPABILITY_SPECS}


def capability_specs() -> tuple[CapabilitySpec, ...]:
    return _CAPABILITY_SPECS


def capability_spec(capability_id: str | None) -> CapabilitySpec | None:
    return _SPEC_BY_ID.get(str(capability_id or "").strip())


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


def _looks_like_follow_up(normalized_message: str) -> bool:
    if not normalized_message:
        return False
    if len(normalized_message.split()) <= 6 and any(
        _contains_term(normalized_message, term) for term in _GENERIC_FOLLOW_UP_TERMS
    ):
        return True
    return normalized_message.startswith(("e ", "mas ", "agora ", "entao ", "então "))


def derive_focus_frame(
    *,
    conversation_context: dict[str, Any] | None,
    authenticated: bool,
) -> FocusFrame:
    recent_lines = _normalize_lines(conversation_context)
    recent_user_message = next((content for sender, content in reversed(recent_lines) if sender == "user"), None)
    recent_assistant_message = next((content for sender, content in reversed(recent_lines) if sender == "assistant"), None)
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
        return FocusFrame(
            capability_id=top.capability_id,
            domain=top.domain,
            access_tier=top.access_tier,
            scope=top.scope,
            source=source_name,
            confidence=min(0.95, 0.45 + top.score / 10.0),
            recent_user_message=recent_user_message,
            recent_assistant_message=recent_assistant_message,
        )
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
    focus = derive_focus_frame(conversation_context=conversation_context, authenticated=authenticated)
    follow_up = _looks_like_follow_up(normalized)
    high_confidence_public = looks_like_high_confidence_public_school_faq(message)
    candidates: list[CapabilityCandidate] = []
    for spec in capability_specs():
        if spec.scope == "protected" and not authenticated:
            continue
        score = 0.0
        reasons: list[str] = []
        for alias in spec.aliases:
            if _contains_term(normalized, alias):
                score += 3.0
                reasons.append(f"alias:{normalize_ingress_text(alias)}")
        for alias in spec.follow_up_aliases:
            if _contains_term(normalized, alias):
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
            )
        ):
            score += 1.6
            reasons.append("protected_personal_anchor")
        if focus.capability_id == spec.capability_id and follow_up:
            score += 2.2
            reasons.append("follow_up_same_capability")
        elif focus.domain == spec.domain and focus.scope == spec.scope and follow_up:
            score += 1.2
            reasons.append("follow_up_same_domain")
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
                requested_attribute=spec.requested_attribute,
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
    candidates = build_capability_candidates(
        message=message,
        conversation_context=conversation_context,
        authenticated=authenticated,
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
    return TurnFrame(
        conversation_act=_validated_conversation_act(request_message=message, act="none"),
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
        follow_up_of=derive_focus_frame(
            conversation_context=conversation_context,
            authenticated=authenticated,
        ).capability_id
        if _looks_like_follow_up(normalized)
        else None,
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


def _router_prompt(
    *,
    request_message: str,
    conversation_context: dict[str, Any] | None,
    preview: dict[str, Any] | None,
    candidates: list[CapabilityCandidate],
    focus: FocusFrame,
) -> str:
    candidates_payload = [
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
    return (
        "Escolha a capability mais adequada para o turno atual.\n\n"
        f"Preview atual:\n{_preview_compact(preview)}\n\n"
        f"Historico recente:\n{_recent_messages(conversation_context)}\n\n"
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
    prompt = _router_prompt(
        request_message=request_message,
        conversation_context=conversation_context,
        preview=preview,
        candidates=candidates,
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
        requested_attribute=spec.requested_attribute,
        candidate_capability_ids=[candidate.capability_id for candidate in candidates],
    )
