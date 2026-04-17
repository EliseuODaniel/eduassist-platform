from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from .intent_registry import get_intent_registry, has_registered_school_signal
from .models import IntentRouteSpec, OperationalMemory, ResolvedTurnIntent, SupervisorAnswerPayload


@dataclass(frozen=True)
class IntentResolutionDeps:
    normalize_text: Callable[[str | None], str]
    contains_any: Callable[[str, set[str] | tuple[str, ...]], bool]
    preview_domain: Callable[[dict[str, Any] | None], str]
    linked_students: Callable[..., list[dict[str, Any]]]
    resolve_student: Callable[..., dict[str, Any] | None]
    subject_hint_from_text: Callable[[str | None], str | None]
    pending_kind_from_answer: Callable[[SupervisorAnswerPayload], str | None]
    topic_from_reason: Callable[[str | None], str | None]
    effective_multi_intent_domains: Callable[[Any, str], list[str]]
    student_hint_from_message: Callable[..., str | None]
    unknown_explicit_student_reference: Callable[..., str | None]
    is_student_name_only_followup: Callable[..., str | None]
    find_student_by_hint: Callable[..., dict[str, Any] | None]
    looks_like_other_student_followup: Callable[[str], bool]
    student_from_memory: Callable[..., dict[str, Any] | None]
    other_linked_student: Callable[..., dict[str, Any] | None]
    looks_like_student_pronoun_followup: Callable[[str], bool]
    looks_like_subject_followup: Callable[[str], bool]


def school_domain_terms() -> set[str]:
    return {
        "escola",
        "colegio",
        "colégio",
        "eduassist",
        "matricula",
        "matrícula",
        "mensalidade",
        "biblioteca",
        "bncc",
        "visita",
        "secretaria",
        "financeiro",
        "fatura",
        "boleto",
        "boletim",
        "nota",
        "notas",
        "media",
        "média",
        "frequencia",
        "frequência",
        "falta",
        "faltas",
        "lucas",
        "ana",
        "recepcao",
        "recepção",
        "admissions",
        "documentacao",
        "documentação",
        "aluno",
        "aluna",
        "estudante",
        "protocolo",
        "atendimento",
        "aulas",
        "ano letivo",
        "professor",
        "professora",
        "9o ano",
        "ensino medio",
        "ensino médio",
        "agenda",
        "calendario",
        "calendário",
        "feriado",
        "feriados",
        "recesso",
        "materia",
        "matéria",
        "materias",
        "matérias",
        "turno",
        "turnos",
        "turma",
        "turmas",
        "manha",
        "manhã",
        "matutivo",
        "matutino",
        "matutina",
        "vespertino",
        "vespertina",
        "noturno",
        "noturna",
        "horario de aula",
        "horário de aula",
        "horario da aula",
        "horário da aula",
        "intervalo",
        "intervalos",
        "recreio",
        "recreios",
        "disciplina",
        "disciplinas",
        "matematica",
        "matemática",
        "frequencia",
        "frequência",
        "presenca",
        "presença",
        "projeto de vida",
        "aprovacao",
        "aprovação",
        "recuperacao",
        "recuperação",
    }


def looks_like_general_knowledge_query(
    message: str,
    *,
    deps: IntentResolutionDeps,
) -> bool:
    normalized = deps.normalize_text(message)
    explicit_out_of_scope_markers = (
        "fora do tema escolar",
        "fora do escopo da escola",
        "fora da escola",
        "sem relacao com escola",
        "sem relação com escola",
        "sem relacao com a escola",
        "sem relação com a escola",
        "mudando de assunto",
        "saindo do assunto da escola",
    )
    open_world_topic_terms = {
        "filme",
        "filmes",
        "serie",
        "série",
        "series",
        "séries",
        "jogo",
        "jogos",
        "receita",
        "receitas",
        "netflix",
        "cinema",
        "livro",
        "livros",
        "politica",
        "política",
    }
    open_world_starters = (
        "me ajuda a escolher ",
        "me ajuda a decidir ",
        "me indica ",
        "me recomenda ",
        "recomenda ",
        "indique ",
        "quero uma recomendacao ",
        "quero uma recomendação ",
        "me fala ",
        "me diga ",
    )
    if not normalized:
        return False
    if any(marker in normalized for marker in explicit_out_of_scope_markers) and (
        normalized.endswith("?")
        or any(term in normalized for term in open_world_topic_terms)
    ):
        return True
    if any(term in normalized for term in open_world_topic_terms) and any(
        normalized.startswith(starter) or starter in normalized for starter in open_world_starters
    ):
        return True
    if any(term in normalized for term in {"feriado", "feriados", "calendario", "calendário", "recesso"}) and any(
        term in normalized for term in {"ano", "ano letivo", "escola", "colegio", "colégio", "publico", "público"}
    ):
        return False
    if deps.contains_any(normalized, school_domain_terms()) or has_registered_school_signal(normalized):
        return False
    if len(normalized) > 180:
        return False
    if any(token in normalized for token in {"token", "prompt", "senha", "credencial", "api key"}):
        return False
    starters = (
        "qual ",
        "quais ",
        "quantos ",
        "quantas ",
        "quem ",
        "o que ",
        "onde ",
        "quando ",
        "como ",
        "por que ",
        "porque ",
    )
    return (
        normalized.endswith("?")
        or normalized.startswith(starters)
        or normalized.startswith(open_world_starters)
    )


def build_operational_memory(
    ctx: Any,
    *,
    answer: SupervisorAnswerPayload,
    route: str,
    deps: IntentResolutionDeps,
) -> OperationalMemory:
    previous = ctx.operational_memory.model_copy(deep=True) if ctx.operational_memory is not None else OperationalMemory()
    active_domain = str(answer.classification.domain or previous.active_domain or "").strip() or None
    active_topic = deps.topic_from_reason(answer.reason) or previous.active_topic
    multi_domains = deps.effective_multi_intent_domains(previous, ctx.request.message)
    active_domains = list(
        dict.fromkeys(multi_domains or previous.multi_intent_domains or ([active_domain] if active_domain else []))
    )
    explicit_subject_hint = deps.subject_hint_from_text(ctx.request.message)
    carry_subject_from_previous = (
        previous.active_domain == "academic"
        and previous.active_subject is not None
        and (
            deps.looks_like_subject_followup(ctx.request.message)
            or previous.pending_kind in {"academic_subject", "academic_student_selection"}
        )
    )
    subject_hint = explicit_subject_hint or (previous.active_subject if carry_subject_from_previous else None)
    capability = "finance" if active_domain == "finance" else "academic"
    student_hint = deps.student_hint_from_message(ctx.actor, ctx.request.message) or deps.is_student_name_only_followup(
        ctx.actor,
        ctx.request.message,
    )
    student = deps.resolve_student(
        ctx.actor,
        capability=capability,
        student_name_hint=student_hint,
        conversation_context=ctx.conversation_context,
        operational_memory=previous,
        current_message=ctx.request.message,
    )
    alternate_student = deps.other_linked_student(
        ctx.actor,
        capability=capability,
        current_student_id=str(student.get("student_id") or "") if isinstance(student, dict) else previous.active_student_id,
    )
    return previous.model_copy(
        update={
            "active_domain": active_domain or previous.active_domain,
            "active_domains": active_domains or previous.active_domains,
            "active_student_id": str(student.get("student_id") or "").strip() or previous.active_student_id
            if isinstance(student, dict)
            else previous.active_student_id,
            "active_student_name": str(student.get("full_name") or "").strip() or previous.active_student_name
            if isinstance(student, dict)
            else previous.active_student_name,
            "alternate_student_id": str(alternate_student.get("student_id") or "").strip() or previous.alternate_student_id
            if isinstance(alternate_student, dict)
            else previous.alternate_student_id,
            "alternate_student_name": str(alternate_student.get("full_name") or "").strip() or previous.alternate_student_name
            if isinstance(alternate_student, dict)
            else previous.alternate_student_name,
            "active_subject": subject_hint,
            "active_topic": active_topic,
            "pending_kind": deps.pending_kind_from_answer(answer),
            "pending_prompt": answer.message_text if answer.mode == "clarify" else None,
            "multi_intent_domains": multi_domains or previous.multi_intent_domains,
            "last_specialists": [item for item in answer.graph_path if item.endswith("_specialist")] or previous.last_specialists,
            "last_route": route,
            "last_reason": answer.reason,
        }
    )


def _score_intent_spec(
    spec: IntentRouteSpec,
    *,
    normalized_message: str,
    preview_domain: str,
    operational_memory: OperationalMemory,
    has_student_pronoun: bool,
    subject_hint: str | None,
    subject_followup: bool,
    authenticated: bool,
) -> int:
    if spec.requires_auth and not authenticated:
        return -1
    if spec.none_terms and any(term in normalized_message for term in spec.none_terms):
        return -1
    if spec.all_terms and not all(term in normalized_message for term in spec.all_terms):
        return -1
    any_hits = sum(1 for term in spec.any_terms if term and term in normalized_message)
    active_domains = set(operational_memory.active_domains)
    if operational_memory.active_domain:
        active_domains.add(str(operational_memory.active_domain))
    if spec.any_terms and any_hits == 0:
        allow_subject_followup = (
            subject_followup
            and spec.domain == "academic"
            and spec.carry_active_student
            and any(domain in active_domains for domain in spec.memory_domains)
        )
        if not allow_subject_followup:
            return -1
        any_hits = 1
    score = any_hits * 10
    if preview_domain and preview_domain in spec.preview_domains:
        score += 6
    if any(domain in active_domains for domain in spec.memory_domains):
        score += 5
    if has_student_pronoun and spec.carry_active_student:
        score += 5
    if subject_hint and spec.carry_active_subject:
        score += 3
    return score


def _resolve_student_reference_for_spec(
    ctx: Any,
    *,
    spec: IntentRouteSpec,
    deps: IntentResolutionDeps,
) -> tuple[dict[str, Any] | None, bool]:
    capability = "finance" if spec.domain == "finance" else "academic"
    alternate_name = str(getattr(ctx.resolved_turn, "alternate_student_name", "") or "").strip()
    if not alternate_name:
        alternate_name = str(getattr(ctx.operational_memory, "alternate_student_name", "") or "").strip()
    if alternate_name:
        normalized_message = deps.normalize_text(ctx.request.message)
        alternate_tokens = [deps.normalize_text(token) for token in alternate_name.split() if token.strip()]
        if any(token and token in normalized_message for token in alternate_tokens):
            student = deps.find_student_by_hint(ctx.actor, capability=capability, hint=alternate_name)
            if student is not None:
                return student, False
    if deps.unknown_explicit_student_reference(ctx.actor, ctx.request.message):
        return None, False
    explicit_hint = deps.student_hint_from_message(ctx.actor, ctx.request.message) or deps.is_student_name_only_followup(
        ctx.actor,
        ctx.request.message,
    )
    if explicit_hint:
        return deps.find_student_by_hint(ctx.actor, capability=capability, hint=explicit_hint), False
    if deps.looks_like_other_student_followup(ctx.request.message):
        current = deps.student_from_memory(ctx.actor, ctx.operational_memory, capability=capability)
        other = deps.other_linked_student(
            ctx.actor,
            capability=capability,
            current_student_id=str(current.get("student_id") or "") if isinstance(current, dict) else None,
        )
        return other, other is not None
    if spec.carry_active_student and deps.looks_like_student_pronoun_followup(ctx.request.message):
        remembered = deps.student_from_memory(ctx.actor, ctx.operational_memory, capability=capability)
        if isinstance(remembered, dict):
            return remembered, True
    if spec.carry_active_student:
        remembered = deps.student_from_memory(ctx.actor, ctx.operational_memory, capability=capability)
        if isinstance(remembered, dict):
            return remembered, True
    students = deps.linked_students(ctx.actor, capability=capability)
    if len(students) == 1:
        return students[0], False
    return None, False


def _resolved_turn_from_turn_frame(ctx: Any) -> ResolvedTurnIntent | None:
    preview_hint = ctx.preview_hint if isinstance(getattr(ctx, "preview_hint", None), dict) else {}
    turn_frame = preview_hint.get("turn_frame") if isinstance(preview_hint, dict) else None
    if not isinstance(turn_frame, dict):
        return None
    capability_id = str(turn_frame.get("capability_id") or "").strip()
    if not capability_id:
        return None
    mapping = {
        "public.schedule.shift_offers": ("institution.shift_offers", "institution", "shift_offers", "institution.shift_offers"),
        "public.schedule.class_start_time": ("institution.shift_offers", "institution", "shift_offers", "institution.shift_offers"),
        "public.schedule.class_end_time": ("institution.shift_offers", "institution", "shift_offers", "institution.shift_offers"),
        "public.calendar.year_start": ("institution.shift_offers", "institution", "shift_offers", "institution.shift_offers"),
        "public.curriculum.overview": ("institution.facilities", "institution", "facilities", "institution.facilities"),
        "public.identity.confessional": ("institution.facilities", "institution", "facilities", "institution.facilities"),
        "public.web.news": ("institution.facilities", "institution", "facilities", "institution.facilities"),
        "public.facilities.library.exists": ("institution.facilities", "institution", "facilities", "institution.facilities"),
        "public.facilities.library.hours": ("institution.facilities", "institution", "facilities", "institution.facilities"),
        "public.contacts.leadership": ("institution.facilities", "institution", "facilities", "institution.facilities"),
        "public.enrollment.required_documents": ("institution.facilities", "institution", "facilities", "institution.facilities"),
        "public.enrollment.pricing": ("institution.facilities", "institution", "facilities", "institution.facilities"),
        "protected.finance.summary": ("finance.student_summary", "finance", "student_summary", "finance.student_summary"),
        "protected.finance.next_due": ("finance.student_summary", "finance", "student_summary", "finance.student_summary"),
        "protected.academic.grades": ("academic.student_grades", "academic", "student_grades", "academic.student_grades"),
        "protected.academic.attendance": ("academic.attendance_summary", "academic", "attendance_summary", "academic.attendance_summary"),
    }
    resolved = mapping.get(capability_id)
    if resolved is None:
        return None
    key, domain, subintent, capability = resolved
    return ResolvedTurnIntent(
        key=key,
        domain=domain,
        subintent=subintent,
        capability=capability,
        access_tier=str(turn_frame.get("access_tier") or "public"),
        confidence=float(turn_frame.get("confidence") or 0.9),
        requires_grounding=domain in {"institution", "finance", "academic"},
        rationale=f"turn_frame:{capability_id}",
    )


def resolve_turn_intent(
    ctx: Any,
    *,
    deps: IntentResolutionDeps,
) -> ResolvedTurnIntent:
    turn_frame_resolved = _resolved_turn_from_turn_frame(ctx)
    if turn_frame_resolved is not None:
        return turn_frame_resolved
    normalized = deps.normalize_text(ctx.request.message)
    preview_domain = deps.preview_domain(ctx.preview_hint)
    memory = ctx.operational_memory or OperationalMemory()
    has_student_pronoun = deps.looks_like_student_pronoun_followup(ctx.request.message)
    subject_hint = deps.subject_hint_from_text(ctx.request.message)
    subject_followup = deps.looks_like_subject_followup(ctx.request.message)
    name_only_hint = deps.is_student_name_only_followup(ctx.actor, ctx.request.message)
    best_spec: IntentRouteSpec | None = None
    best_score = -1
    for spec in get_intent_registry():
        score = _score_intent_spec(
            spec,
            normalized_message=normalized,
            preview_domain=preview_domain,
            operational_memory=memory,
            has_student_pronoun=has_student_pronoun,
            subject_hint=subject_hint,
            subject_followup=subject_followup,
            authenticated=ctx.request.user.authenticated,
        )
        if score < 0:
            continue
        if score > best_score or (score == best_score and best_spec is not None and spec.priority < best_spec.priority):
            best_spec = spec
            best_score = score
    if best_spec is None and name_only_hint:
        registry_by_key = {spec.key: spec for spec in get_intent_registry()}
        memory_domain = str(memory.active_domain or "").strip().lower()
        if memory_domain == "finance":
            best_spec = registry_by_key.get("finance.student_summary")
            best_score = 8 if best_spec is not None else -1
        elif memory_domain == "academic":
            best_spec = registry_by_key.get("academic.student_grades")
            best_score = 8 if best_spec is not None else -1
    if best_spec is None:
        return ResolvedTurnIntent(rationale="no_intent_registry_match", confidence=0.0)
    student, used_memory = _resolve_student_reference_for_spec(ctx, spec=best_spec, deps=deps)
    resolved_subject = subject_hint or (memory.active_subject if best_spec.carry_active_subject else None)
    confidence = min(0.99, 0.45 + (best_score / 40))
    rationale_bits = [best_spec.key]
    if preview_domain:
        rationale_bits.append(f"preview={preview_domain}")
    if used_memory:
        rationale_bits.append("memory")
    return ResolvedTurnIntent(
        key=best_spec.key,
        domain=best_spec.domain,
        subintent=best_spec.subintent,
        capability=best_spec.capability,
        access_tier=best_spec.access_tier,
        confidence=confidence,
        requires_grounding=best_spec.requires_grounding,
        referenced_student_id=(str(student.get("student_id") or "").strip() or None) if isinstance(student, dict) else None,
        referenced_student_name=(str(student.get("full_name") or "").strip() or None) if isinstance(student, dict) else None,
        referenced_subject=resolved_subject,
        used_operational_memory=used_memory,
        rationale="; ".join(rationale_bits),
    )
