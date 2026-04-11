from __future__ import annotations

import re
from dataclasses import dataclass
from decimal import Decimal
from typing import Any, Awaitable, Callable

from .answer_payloads import (
    access_tier_for_domain as _access_tier_for_domain,
)
from .answer_payloads import (
    default_suggested_replies as _default_suggested_replies,
)
from .models import (
    MessageEvidencePack,
    MessageEvidenceSupport,
    MessageIntentClassification,
    MessageResponseSuggestedReply,
    OperationalMemory,
    ResolvedTurnIntent,
    SupervisorAnswerPayload,
)
from .public_profile_answers import (
    _compose_interval_schedule_answer,
    _compose_shift_offers_answer,
)
from .public_query_patterns import _looks_like_public_doc_bundle_request

PASSING_GRADE_TARGET = Decimal("7.0")


def _looks_like_public_pricing_navigation_query(message: str, *, deps: ResolvedIntentDeps) -> bool:
    normalized = deps.normalize_text(message)
    pricing_terms = {"mensalidade", "mensalidades", "matricula", "matrícula", "taxa de matricula", "taxa de matrícula"}
    if not any(term in normalized for term in pricing_terms):
        return False
    private_finance_terms = {
        "fatura",
        "faturas",
        "boleto",
        "boletos",
        "em aberto",
        "vencimento",
        "vencida",
        "vencidas",
        "do lucas",
        "da ana",
        "meu filho",
        "minha filha",
    }
    return not any(term in normalized for term in private_finance_terms)


def _looks_like_public_pricing_context_follow_up(ctx: Any, *, deps: ResolvedIntentDeps) -> bool:
    normalized = deps.normalize_text(ctx.request.message).strip()
    if _looks_like_public_pricing_navigation_query(ctx.request.message, deps=deps):
        return False
    recent_messages = (
        ctx.conversation_context.get("recent_messages", [])
        if isinstance(ctx.conversation_context, dict)
        else []
    )
    recent_user_messages = [
        deps.normalize_text(item.get("content"))
        for item in recent_messages[-6:]
        if isinstance(item, dict) and str(item.get("sender_type", "")).lower() == "user"
    ]
    pricing_context_active = any(
        any(term in message for term in {"mensalidade", "matricula", "matrícula"})
        and any(term in message for term in {"ensino medio", "ensino médio", "fundamental", "filhos", "alunos"})
        for message in recent_user_messages
    )
    if not pricing_context_active:
        return False
    if normalized in {"1o", "2o", "3o", "6o", "7o", "8o", "9o"}:
        return True
    if re.fullmatch(r"(1o|2o|3o|6o|7o|8o|9o)\s+ano", normalized):
        return True
    return normalized.startswith("e para") or "filhos" in normalized or "alunos" in normalized


def _recent_messages_blob(conversation_context: dict[str, Any] | None, *, deps: "ResolvedIntentDeps") -> str:
    if not isinstance(conversation_context, dict):
        return ""
    recent_messages = conversation_context.get("recent_messages")
    if not isinstance(recent_messages, list):
        return ""
    return " ".join(
        deps.normalize_text(item.get("content"))
        for item in recent_messages
        if isinstance(item, dict) and str(item.get("content") or "").strip()
    )


def _looks_like_family_academic_reason_followup(message: str, *, deps: "ResolvedIntentDeps") -> bool:
    normalized = deps.normalize_text(message)
    return any(
        term in normalized
        for term in {
            "qual e o principal motivo desse alerta",
            "qual é o principal motivo desse alerta",
            "principal motivo desse alerta",
            "motivo desse alerta",
            "principal motivo",
            "por que ele aparece primeiro",
            "por que ela aparece primeiro",
            "por que ele esta primeiro",
            "por que ela esta primeiro",
            "por que ele ficou na frente",
            "por que ela ficou na frente",
            "o que puxou isso",
            "o que puxou esse alerta",
            "qual materia puxou isso",
            "qual disciplina puxou isso",
            "me explique esse alerta",
        }
    )


def _looks_like_family_academic_next_in_line_followup(message: str, *, deps: "ResolvedIntentDeps") -> bool:
    normalized = deps.normalize_text(message)
    return any(
        term in normalized
        for term in {
            "logo depois dele",
            "logo depois dela",
            "quem vem na fila",
            "quem vem depois",
            "depois dele",
            "depois dela",
            "e logo depois",
            "quem aparece depois",
        }
    )


def _recent_family_academic_context(ctx: Any, *, deps: "ResolvedIntentDeps") -> bool:
    normalized = _recent_messages_blob(getattr(ctx, "conversation_context", None), deps=deps)
    return any(
        term in normalized
        for term in {
            "panorama academico das contas vinculadas",
            "quem hoje exige maior atencao academica",
            "mais perto da media minima",
            "mais perto da media mínima",
        }
    )


def _recent_family_attendance_context(ctx: Any, *, deps: "ResolvedIntentDeps") -> bool:
    normalized = _recent_messages_blob(getattr(ctx, "conversation_context", None), deps=deps)
    return any(
        term in normalized
        for term in {
            "panorama de faltas e frequencia das contas vinculadas",
            "panorama de faltas e frequência das contas vinculadas",
            "panorama de frequencia das contas vinculadas",
            "panorama de frequência das contas vinculadas",
            "frequencia dos meus filhos",
            "frequência dos meus filhos",
            "frequencia dos meus dois filhos",
            "frequência dos meus dois filhos",
            "quem exige maior atencao agora",
            "quem exige maior atenção agora",
            "principal alerta de frequencia",
            "principal alerta de frequência",
            "o que eu deveria acompanhar primeiro",
        }
    )


def _recent_linked_student_name(ctx: Any, *, deps: "ResolvedIntentDeps") -> str | None:
    recent_blob = _recent_messages_blob(getattr(ctx, "conversation_context", None), deps=deps)
    if not recent_blob:
        return None
    for student in deps.linked_students(getattr(ctx, "actor", None), capability="academic"):
        if not isinstance(student, dict):
            continue
        full_name = str(student.get("full_name") or "").strip()
        if not full_name:
            continue
        normalized_full_name = deps.normalize_text(full_name)
        first_name = normalized_full_name.split(" ")[0] if normalized_full_name else ""
        if normalized_full_name and normalized_full_name in recent_blob:
            return full_name
        if first_name and re.search(rf"\b{re.escape(first_name)}\b", recent_blob):
            return full_name
    return None


def _family_academic_ranking(summaries: list[dict[str, Any]], *, deps: "ResolvedIntentDeps") -> list[dict[str, Any]]:
    ranking: list[dict[str, Any]] = []
    for summary in summaries:
        grades = summary.get("grades")
        if not isinstance(grades, list):
            continue
        candidate_rows: list[tuple[Decimal, str]] = []
        for row in grades:
            if not isinstance(row, dict):
                continue
            score = row.get("score")
            if score is None:
                continue
            try:
                score_decimal = Decimal(str(score))
            except Exception:
                continue
            subject_name = str(row.get("subject_name") or "Disciplina").strip() or "Disciplina"
            candidate_rows.append((score_decimal, subject_name))
        if not candidate_rows:
            continue
        candidate_rows.sort(key=lambda item: (item[0], deps.normalize_text(item[1])))
        weakest_score, weakest_subject = candidate_rows[0]
        ranking.append(
            {
                "student_name": str(summary.get("student_name") or "Aluno").strip() or "Aluno",
                "subject_name": weakest_subject,
                "score": weakest_score,
            }
        )
    ranking.sort(key=lambda item: (item["score"], deps.normalize_text(item["student_name"])))
    return ranking


def _compose_family_academic_alert_reason(
    summaries: list[dict[str, Any]],
    *,
    deps: "ResolvedIntentDeps",
) -> str | None:
    ranking = _family_academic_ranking(summaries, deps=deps)
    if not ranking:
        return None
    top = ranking[0]
    top_score = str(top["score"]).replace(".", ",")
    return (
        f"{top['student_name']} aparece primeiro porque o ponto academico mais sensivel dele hoje e "
        f"{top['subject_name']}, com media parcial {top_score}. "
        "Esse componente puxa o alerta por ficar mais perto da media minima neste recorte."
    )


def _compose_family_academic_next_in_line(
    summaries: list[dict[str, Any]],
    *,
    deps: "ResolvedIntentDeps",
) -> str | None:
    ranking = _family_academic_ranking(summaries, deps=deps)
    if len(ranking) < 2:
        return None
    first = ranking[0]
    second = ranking[1]
    second_score = str(second["score"]).replace(".", ",")
    return (
        f"Logo depois de {first['student_name']}, quem vem na fila e {second['student_name']}, "
        f"puxado(a) por {second['subject_name']} com media parcial {second_score}."
    )


async def _maybe_recent_context_followup_answer(
    ctx: Any,
    *,
    deps: "ResolvedIntentDeps",
) -> SupervisorAnswerPayload | None:
    if not getattr(getattr(ctx, "request", None), "user", None) or not ctx.request.user.authenticated:
        return None
    if _recent_family_academic_context(ctx, deps=deps) and (
        _looks_like_family_academic_reason_followup(ctx.request.message, deps=deps)
        or _looks_like_family_academic_next_in_line_followup(ctx.request.message, deps=deps)
    ):
        summaries: list[dict[str, Any]] = []
        for student in deps.linked_students(ctx.actor, capability="academic"):
            student_name = str((student or {}).get("full_name") or "").strip()
            if not student_name:
                continue
            payload = await deps.fetch_academic_summary_payload(ctx, student_name_hint=student_name)
            summary = payload.get("summary") if isinstance(payload, dict) else None
            if isinstance(summary, dict):
                summaries.append(summary)
        if summaries:
            if _looks_like_family_academic_reason_followup(ctx.request.message, deps=deps):
                answer_text = _compose_family_academic_alert_reason(summaries, deps=deps)
                if answer_text:
                    return SupervisorAnswerPayload(
                        message_text=answer_text,
                        mode="structured_tool",
                        classification=MessageIntentClassification(
                            domain="academic",
                            access_tier=_access_tier_for_domain("academic", True),
                            confidence=0.97,
                            reason="specialist_supervisor_recent_context:family_academic_reason_followup",
                        ),
                        evidence_pack=MessageEvidencePack(
                            strategy="structured_tools",
                            summary="Follow-up curto recuperado a partir do panorama academico recente das contas vinculadas.",
                            source_count=len(summaries),
                            support_count=min(len(summaries), 2),
                            supports=[
                                MessageEvidenceSupport(
                                    kind="academic_summary",
                                    label=str(summary.get("student_name") or "Aluno"),
                                    detail=deps.safe_excerpt(answer_text, limit=180),
                                )
                                for summary in summaries[:2]
                            ],
                        ),
                        suggested_replies=_default_suggested_replies("academic"),
                        graph_path=["specialist_supervisor", "recent_context", "family_academic_reason_followup"],
                        reason="specialist_supervisor_recent_context:family_academic_reason_followup",
                    )
            if _looks_like_family_academic_next_in_line_followup(ctx.request.message, deps=deps):
                answer_text = _compose_family_academic_next_in_line(summaries, deps=deps)
                if answer_text:
                    return SupervisorAnswerPayload(
                        message_text=answer_text,
                        mode="structured_tool",
                        classification=MessageIntentClassification(
                            domain="academic",
                            access_tier=_access_tier_for_domain("academic", True),
                            confidence=0.97,
                            reason="specialist_supervisor_recent_context:family_academic_next_in_line_followup",
                        ),
                        evidence_pack=MessageEvidencePack(
                            strategy="structured_tools",
                            summary="Follow-up curto recuperado a partir do ranking academico recente da familia.",
                            source_count=len(summaries),
                            support_count=min(len(summaries), 2),
                            supports=[
                                MessageEvidenceSupport(
                                    kind="academic_summary",
                                    label=str(summary.get("student_name") or "Aluno"),
                                    detail=deps.safe_excerpt(answer_text, limit=180),
                                )
                                for summary in summaries[:2]
                            ],
                        ),
                        suggested_replies=_default_suggested_replies("academic"),
                        graph_path=["specialist_supervisor", "recent_context", "family_academic_next_in_line_followup"],
                        reason="specialist_supervisor_recent_context:family_academic_next_in_line_followup",
                    )
    normalized = deps.normalize_text(ctx.request.message)
    if not _recent_family_attendance_context(ctx, deps=deps):
        return None
    if not any(
        term in normalized
        for term in {
            "principal alerta",
            "maior atencao",
            "maior atenção",
            "mais atencao",
            "mais atenção",
            "quem exige mais atencao",
            "quem exige mais atenção",
            "inspira mais atencao",
            "inspira mais atenção",
            "olhando as faltas",
            "por que a frequencia",
            "por que a frequência",
            "frequencia dele preocupa",
            "frequência dele preocupa",
            "preocupa mais",
            "preocupa menos",
            "o que eu deveria acompanhar primeiro",
            "o que deveria acompanhar primeiro",
            "o que acompanhar primeiro",
            "sem repetir os numeros todos",
            "sem repetir os numeros",
            "proximo passo",
            "próximo passo",
        }
    ):
        return None
    target_name = (
        deps.student_hint_from_message(ctx.actor, ctx.request.message)
        or str(getattr(ctx.operational_memory, "active_student_name", "") or "").strip()
        or _recent_linked_student_name(ctx, deps=deps)
    )
    synthetic_resolved = ResolvedTurnIntent(
        key="academic.attendance_summary",
        domain="academic",
        subintent="attendance_summary",
        capability="academic.attendance_summary",
        access_tier="authenticated",
        confidence=0.97,
        referenced_student_name=target_name or None,
    )
    return await _resolved_academic_attendance_summary_answer(ctx, synthetic_resolved, deps=deps)


@dataclass(frozen=True)
class ResolvedIntentDeps:
    normalize_text: Callable[[str | None], str]
    looks_like_subject_followup: Callable[[str], bool]
    looks_like_academic_risk_followup: Callable[[str], bool]
    looks_like_family_finance_aggregate_query: Callable[[str], bool]
    looks_like_family_attendance_aggregate_query: Callable[[str], bool]
    fetch_academic_summary_payload: Callable[..., Awaitable[dict[str, Any] | None]]
    fetch_financial_summary_payload: Callable[..., Awaitable[dict[str, Any] | None]]
    fetch_upcoming_assessments_payload: Callable[..., Awaitable[dict[str, Any] | None]]
    resolved_academic_target_name: Callable[..., str | None]
    needs_specific_academic_student_clarification: Callable[..., bool]
    build_academic_student_selection_clarify: Callable[..., SupervisorAnswerPayload]
    compose_academic_risk_answer: Callable[[dict[str, Any]], str]
    compose_named_subject_grade_answer: Callable[..., str | None]
    compose_named_grade_answer: Callable[[dict[str, Any]], str]
    compose_named_attendance_answer: Callable[..., str | None]
    compose_academic_snapshot_lines: Callable[[dict[str, Any]], list[str]]
    compose_academic_aggregate_answer: Callable[[list[dict[str, Any]]], str]
    compose_finance_aggregate_answer: Callable[[list[dict[str, Any]]], str]
    compose_finance_installments_answer: Callable[[dict[str, Any]], str]
    linked_students: Callable[..., list[dict[str, Any]]]
    safe_excerpt: Callable[..., str | None]
    subject_hint_from_text: Callable[[str], str | None]
    recent_subject_from_context: Callable[..., str | None]
    subject_code_from_hint: Callable[..., tuple[str | None, str | None]]
    student_hint_from_message: Callable[..., str | None]
    is_student_name_only_followup: Callable[..., str | None]
    compose_upcoming_assessments_lines: Callable[[dict[str, Any]], list[str]]


def _academic_grade_requirement(
    summary: dict[str, Any],
    *,
    subject_hint: str | None,
    deps: ResolvedIntentDeps,
) -> dict[str, Any]:
    subject_code, subject_name = deps.subject_code_from_hint(summary, subject_hint)
    if not subject_code and not subject_name:
        return {"error": "subject_not_found", "subject_hint": subject_hint}
    grades = summary.get("grades")
    if not isinstance(grades, list):
        return {"error": "grades_unavailable"}
    relevant_scores: list[Decimal] = []
    for item in grades:
        if not isinstance(item, dict):
            continue
        if subject_code and str(item.get("subject_code", "")).strip() != subject_code:
            continue
        score = item.get("score")
        if score is None:
            continue
        try:
            relevant_scores.append(Decimal(str(score)))
        except Exception:
            continue
    if not relevant_scores:
        return {"error": "subject_not_found", "subject_hint": subject_hint}
    average = sum(relevant_scores) / Decimal(len(relevant_scores))
    needed = PASSING_GRADE_TARGET - average
    if needed < Decimal("0"):
        needed = Decimal("0")
    return {
        "subject_name": subject_name or subject_hint,
        "current_average": str(average.quantize(Decimal("0.1"))),
        "passing_target": str(PASSING_GRADE_TARGET),
        "points_needed": str(needed.quantize(Decimal("0.1"))),
        "evidence_count": len(relevant_scores),
    }


def build_grade_requirement_answer(
    *,
    student: dict[str, Any],
    summary: dict[str, Any],
    subject_hint: str | None,
    deps: ResolvedIntentDeps | None = None,
) -> SupervisorAnswerPayload:
    if deps is None:
        raise RuntimeError("ResolvedIntentDeps is required to build grade requirement answers")
    requirement = _academic_grade_requirement(summary, subject_hint=subject_hint, deps=deps)
    student_name = str(student.get("full_name") or "o aluno").strip()
    if requirement.get("error") == "subject_not_found":
        if str(subject_hint or "").strip():
            subject_label = str(subject_hint or "a disciplina").strip()
            return SupervisorAnswerPayload(
                message_text=(
                    f"Hoje eu nao encontrei notas de {student_name} em {subject_label} "
                    "no recorte academico desta conta."
                ),
                mode="structured_tool",
                classification=MessageIntentClassification(
                    domain="academic",
                    access_tier="authenticated",
                    confidence=0.98,
                    reason="specialist_supervisor_fast_path:academic_subject_not_found",
                ),
                evidence_pack=MessageEvidencePack(
                    strategy="structured_tools",
                    summary="Disciplina explicitamente pedida nao foi encontrada no resumo academico do aluno.",
                    source_count=1,
                    support_count=1,
                    supports=[
                        MessageEvidenceSupport(
                            kind="student_context",
                            label=student_name,
                            detail=f"Disciplina nao encontrada: {subject_label}",
                        )
                    ],
                ),
                suggested_replies=_default_suggested_replies("academic"),
                graph_path=["specialist_supervisor", "fast_path", "academic_subject_not_found"],
                reason="specialist_supervisor_fast_path:academic_subject_not_found",
            )
        return SupervisorAnswerPayload(
            message_text=f"Consigo calcular isso para {student_name}, mas preciso que voce confirme a disciplina exata.",
            mode="clarify",
            classification=MessageIntentClassification(
                domain="academic",
                access_tier="authenticated",
                confidence=0.96,
                reason="specialist_supervisor_fast_path:academic_subject_clarify",
            ),
            evidence_pack=MessageEvidencePack(
                strategy="structured_tools",
                summary="Clarificacao necessaria antes do calculo academico.",
                source_count=1,
                support_count=1,
                supports=[
                    MessageEvidenceSupport(
                        kind="student_context",
                        label=student_name,
                        detail="A disciplina nao foi identificada com seguranca.",
                    )
                ],
            ),
            suggested_replies=[
                MessageResponseSuggestedReply(text="Física"),
                MessageResponseSuggestedReply(text="Educação Física"),
                MessageResponseSuggestedReply(text="Matemática"),
                MessageResponseSuggestedReply(text="Português"),
            ],
            graph_path=["specialist_supervisor", "fast_path", "academic_grade_requirement"],
            reason="specialist_supervisor_fast_path:academic_subject_clarify",
        )
    if requirement.get("error"):
        return SupervisorAnswerPayload(
            message_text=f"Ainda nao consegui calcular isso com seguranca para {student_name}.",
            mode="clarify",
            classification=MessageIntentClassification(
                domain="academic",
                access_tier="authenticated",
                confidence=0.6,
                reason="specialist_supervisor_fast_path:academic_grade_requirement_unavailable",
            ),
            suggested_replies=_default_suggested_replies("academic"),
            graph_path=["specialist_supervisor", "fast_path", "academic_grade_requirement"],
            reason="specialist_supervisor_fast_path:academic_grade_requirement_unavailable",
        )
    subject_name = str(requirement.get("subject_name") or "a disciplina").strip()
    current_average = str(requirement.get("current_average") or "0.0").replace(".", ",")
    needed = str(requirement.get("points_needed") or "0.0").replace(".", ",")
    return SupervisorAnswerPayload(
        message_text=(
            f"Hoje {student_name} esta com media parcial {current_average} em {subject_name}. "
            f"Para chegar a 7,0, faltam {needed} ponto(s)."
        ),
        mode="structured_tool",
        classification=MessageIntentClassification(
            domain="academic",
            access_tier="authenticated",
            confidence=0.99,
            reason="specialist_supervisor_fast_path:academic_grade_requirement",
        ),
        evidence_pack=MessageEvidencePack(
            strategy="structured_tools",
            summary="Calculo academico deterministico com base no resumo do aluno.",
            source_count=1,
            support_count=2,
            supports=[
                MessageEvidenceSupport(kind="student_context", label=student_name, detail=subject_name),
                MessageEvidenceSupport(
                    kind="grade_requirement",
                    label="Meta de aprovacao",
                    detail=f"media atual {current_average} · faltam {needed}",
                ),
            ],
        ),
        suggested_replies=_default_suggested_replies("academic"),
        graph_path=["specialist_supervisor", "fast_path", "academic_grade_requirement"],
        reason="specialist_supervisor_fast_path:academic_grade_requirement",
    )


def _detected_subject_hint(
    summary: dict[str, Any],
    message: str,
    *,
    conversation_context: dict[str, Any] | None = None,
    operational_memory: OperationalMemory | None = None,
    deps: ResolvedIntentDeps,
) -> str | None:
    normalized_message = deps.normalize_text(message)
    direct_hint = deps.subject_hint_from_text(message)
    if direct_hint:
        return direct_hint
    grades = summary.get("grades")
    if not isinstance(grades, list):
        return None
    for item in grades:
        if not isinstance(item, dict):
            continue
        subject_name = str(item.get("subject_name", "") or "").strip()
        normalized_name = deps.normalize_text(subject_name)
        if normalized_name and normalized_name in normalized_message:
            return subject_name
    match = re.search(r"\bem\s+([a-zA-ZÀ-ÿ ]+?)(?:\?|$)", message, flags=re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return deps.recent_subject_from_context(
        summary,
        conversation_context,
        operational_memory=operational_memory,
    )


async def maybe_academic_grade_fast_path_answer(
    ctx: Any,
    *,
    deps: ResolvedIntentDeps,
) -> SupervisorAnswerPayload | None:
    normalized = deps.normalize_text(ctx.request.message)
    if not ctx.request.user.authenticated:
        return None
    resolved_turn = getattr(ctx, "resolved_turn", None)
    student_hint = deps.student_hint_from_message(
        getattr(ctx, "actor", None),
        ctx.request.message,
    ) or deps.resolved_academic_target_name(ctx, resolved=resolved_turn)
    recent_messages = (
        ctx.conversation_context.get("recent_messages", [])
        if isinstance(ctx.conversation_context, dict)
        else []
    )
    recent_user_messages = [
        deps.normalize_text(item.get("content"))
        for item in recent_messages[-6:]
        if isinstance(item, dict) and str(item.get("sender_type", "")).lower() == "user"
    ]
    recent_upcoming_context = any(
        any(
            term in message
            for term in {
                "proxima prova",
                "próxima prova",
                "proxima avaliacao",
                "próxima avaliação",
                "proximas avaliacoes",
                "próximas avaliações",
                "proximas provas",
                "próximas provas",
                "provas e entregas",
            }
        )
        for message in recent_user_messages
    )
    short_student_switch_followup = len(re.findall(r"[a-z0-9]+", normalized)) <= 6 and not any(
        term in normalized
        for term in {
            "nota",
            "notas",
            "falta",
            "faltas",
            "financeiro",
            "boleto",
            "matricula",
            "matrícula",
        }
    )
    if recent_upcoming_context and student_hint and short_student_switch_followup:
        subject_hint = deps.subject_hint_from_text(ctx.request.message)
        upcoming_payload = await deps.fetch_upcoming_assessments_payload(ctx, student_name_hint=student_hint)
        if isinstance(upcoming_payload, dict) and not upcoming_payload.get("error"):
            student = upcoming_payload.get("student") if isinstance(upcoming_payload.get("student"), dict) else None
            summary = upcoming_payload.get("summary") if isinstance(upcoming_payload.get("summary"), dict) else None
            if student and summary:
                if subject_hint:
                    assessments = summary.get("assessments")
                    if isinstance(assessments, list):
                        filtered = [
                            item
                            for item in assessments
                            if isinstance(item, dict)
                            and deps.normalize_text(item.get("subject_name")) == deps.normalize_text(subject_hint)
                        ]
                        summary = dict(summary)
                        summary["assessments"] = filtered
                student_name = str(student.get("full_name") or student_hint or "Aluno").strip()
                if subject_hint and not summary.get("assessments"):
                    answer_text = (
                        f"Hoje eu nao encontrei proximas avaliacoes de {student_name} em {subject_hint} "
                        "no recorte academico desta conta."
                    )
                    return SupervisorAnswerPayload(
                        message_text=answer_text,
                        mode="structured_tool",
                        classification=MessageIntentClassification(
                            domain="academic",
                            access_tier=_access_tier_for_domain("academic", True),
                            confidence=0.99,
                            reason="specialist_supervisor_fast_path:upcoming_followup_subject_not_found",
                        ),
                        evidence_pack=MessageEvidencePack(
                            strategy="structured_tools",
                            summary="Follow-up curto de proximas avaliacoes com disciplina explicitamente filtrada.",
                            source_count=1,
                            support_count=1,
                            supports=[
                                MessageEvidenceSupport(
                                    kind="academic_summary",
                                    label=student_name,
                                    detail=deps.safe_excerpt(answer_text, limit=180),
                                ),
                            ],
                        ),
                        suggested_replies=_default_suggested_replies("academic"),
                        graph_path=["specialist_supervisor", "fast_path", "upcoming_followup_subject_not_found"],
                        reason="specialist_supervisor_fast_path:upcoming_followup_subject_not_found",
                    )
                lines = [f"Proximas avaliacoes de {student_name}:"]
                class_name = str(student.get("class_name") or "").strip()
                if class_name:
                    lines.append(f"- Turma: {class_name}")
                if subject_hint:
                    lines.append(f"- Disciplina filtrada: {subject_hint}")
                lines.extend(deps.compose_upcoming_assessments_lines(summary))
                answer_text = "\n".join(lines)
                return SupervisorAnswerPayload(
                    message_text=answer_text,
                    mode="structured_tool",
                    classification=MessageIntentClassification(
                        domain="academic",
                        access_tier=_access_tier_for_domain("academic", True),
                        confidence=0.99,
                        reason="specialist_supervisor_fast_path:upcoming_followup_student_switch",
                    ),
                    evidence_pack=MessageEvidencePack(
                        strategy="structured_tools",
                        summary="Follow-up curto de troca de aluno reaproveitando o foco recente de proximas avaliacoes.",
                        source_count=1,
                        support_count=1,
                        supports=[
                            MessageEvidenceSupport(
                                kind="academic_summary",
                                label=student_name,
                                detail=deps.safe_excerpt(answer_text, limit=180),
                            ),
                        ],
                    ),
                    suggested_replies=_default_suggested_replies("academic"),
                    graph_path=["specialist_supervisor", "fast_path", "upcoming_followup_student_switch"],
                    reason="specialist_supervisor_fast_path:upcoming_followup_student_switch",
                )
    if deps.looks_like_academic_risk_followup(ctx.request.message):
        payload = await deps.fetch_academic_summary_payload(ctx, student_name_hint=student_hint)
        if not isinstance(payload, dict) or payload.get("error"):
            return None
        summary = payload.get("summary") if isinstance(payload.get("summary"), dict) else None
        if not summary:
            return None
        answer_text = deps.compose_academic_risk_answer(summary)
        if not answer_text:
            return None
        return SupervisorAnswerPayload(
            message_text=answer_text,
            mode="structured_tool",
            classification=MessageIntentClassification(
                domain="academic",
                access_tier=_access_tier_for_domain("academic", True),
                confidence=0.99,
                reason="specialist_supervisor_fast_path:academic_risk",
            ),
            evidence_pack=MessageEvidencePack(
                strategy="structured_tools",
                summary="Recorte deterministico dos componentes com maior risco academico do aluno solicitado.",
                source_count=1,
                support_count=1,
                supports=[
                    MessageEvidenceSupport(
                        kind="academic_summary",
                        label=str(summary.get("student_name") or "Aluno"),
                        detail=deps.safe_excerpt(answer_text, limit=180),
                    ),
                ],
            ),
            suggested_replies=_default_suggested_replies("academic"),
            graph_path=["specialist_supervisor", "fast_path", "academic_risk"],
            reason="specialist_supervisor_fast_path:academic_risk",
        )
    if "quanto falta" not in normalized:
        return None
    if not any(term in normalized for term in {"aprova", "passar", "tirar de nota"}):
        return None
    student_hint = deps.student_hint_from_message(ctx.actor, ctx.request.message)
    payload = await deps.fetch_academic_summary_payload(ctx, student_name_hint=student_hint)
    if not isinstance(payload, dict) or payload.get("error"):
        return None
    student = payload.get("student") if isinstance(payload.get("student"), dict) else None
    summary = payload.get("summary") if isinstance(payload.get("summary"), dict) else None
    if not student or not summary:
        return None
    subject_hint = _detected_subject_hint(
        summary,
        ctx.request.message,
        conversation_context=ctx.conversation_context,
        operational_memory=ctx.operational_memory,
        deps=deps,
    )
    return build_grade_requirement_answer(student=student, summary=summary, subject_hint=subject_hint, deps=deps)


async def _resolved_shift_offers_answer(
    ctx: Any,
    resolved: ResolvedTurnIntent,
    *,
    deps: ResolvedIntentDeps,
) -> SupervisorAnswerPayload | None:
    answer_text = _compose_shift_offers_answer(ctx.school_profile, message=ctx.request.message)
    if not answer_text:
        return None
    return SupervisorAnswerPayload(
        message_text=answer_text,
        mode="structured_tool",
        classification=MessageIntentClassification(
            domain="institution",
            access_tier="public",
            confidence=resolved.confidence,
            reason="specialist_supervisor_resolved_intent:shift_offers",
        ),
        evidence_pack=MessageEvidencePack(
            strategy="structured_tools",
            summary="Resposta deterministica baseada nos turnos publicos da escola.",
            source_count=1,
            support_count=1,
            supports=[
                MessageEvidenceSupport(kind="public_schedule", label="Turnos publicos", detail=deps.safe_excerpt(answer_text, limit=180)),
            ],
        ),
        suggested_replies=_default_suggested_replies("institution"),
        graph_path=["specialist_supervisor", "resolved_intent", "shift_offers"],
        reason="specialist_supervisor_resolved_intent:shift_offers",
    )


async def _resolved_interval_schedule_answer(
    ctx: Any,
    resolved: ResolvedTurnIntent,
    *,
    deps: ResolvedIntentDeps,
) -> SupervisorAnswerPayload | None:
    answer_text = _compose_interval_schedule_answer(ctx.school_profile, message=ctx.request.message)
    if not answer_text:
        return None
    return SupervisorAnswerPayload(
        message_text=answer_text,
        mode="structured_tool",
        classification=MessageIntentClassification(
            domain="institution",
            access_tier="public",
            confidence=resolved.confidence,
            reason="specialist_supervisor_resolved_intent:interval_schedule",
        ),
        evidence_pack=MessageEvidencePack(
            strategy="structured_tools",
            summary="Resposta deterministica baseada no quadro publico de intervalos.",
            source_count=1,
            support_count=1,
            supports=[
                MessageEvidenceSupport(kind="public_schedule", label="Intervalos publicos", detail=deps.safe_excerpt(answer_text, limit=180)),
            ],
        ),
        suggested_replies=_default_suggested_replies("institution"),
        graph_path=["specialist_supervisor", "resolved_intent", "interval_schedule"],
        reason="specialist_supervisor_resolved_intent:interval_schedule",
    )


async def _resolved_academic_student_grades_answer(
    ctx: Any,
    resolved: ResolvedTurnIntent,
    *,
    deps: ResolvedIntentDeps,
) -> SupervisorAnswerPayload | None:
    if not ctx.request.user.authenticated:
        return None
    if _looks_like_public_doc_bundle_request(ctx.request.message):
        return None
    if deps.looks_like_family_attendance_aggregate_query(ctx.request.message):
        return None
    memory = ctx.operational_memory or OperationalMemory()
    subject_hint = str(resolved.referenced_subject or "").strip() or (
        memory.active_subject if deps.looks_like_subject_followup(ctx.request.message) else None
    )
    target_name = deps.student_hint_from_message(
        ctx.actor,
        ctx.request.message,
    ) or deps.resolved_academic_target_name(ctx, resolved=resolved)
    if deps.needs_specific_academic_student_clarification(ctx, target_name=target_name, subject_hint=subject_hint):
        return deps.build_academic_student_selection_clarify(
            ctx,
            reason="specialist_supervisor_resolved_intent:student_grades_clarify",
            graph_path=["specialist_supervisor", "resolved_intent", "student_grades_clarify"],
            confidence=resolved.confidence,
        )
    if target_name:
        payload = await deps.fetch_academic_summary_payload(ctx, student_name_hint=target_name)
        summary = payload.get("summary") if isinstance(payload, dict) else None
        if isinstance(summary, dict):
            if deps.looks_like_academic_risk_followup(ctx.request.message):
                answer_text = deps.compose_academic_risk_answer(summary)
            else:
                answer_text = deps.compose_named_subject_grade_answer(summary, subject_hint=subject_hint)
                if not answer_text and subject_hint:
                    student_name = str(summary.get("student_name") or target_name or "Aluno").strip() or "Aluno"
                    answer_text = (
                        f"Hoje eu nao encontrei notas de {student_name} em {subject_hint} "
                        "no recorte academico desta conta."
                    )
                if not answer_text:
                    answer_text = deps.compose_named_grade_answer(summary)
            support_label = str(summary.get("student_name") or "Aluno")
            return SupervisorAnswerPayload(
                message_text=answer_text,
                mode="structured_tool",
                classification=MessageIntentClassification(
                    domain="academic",
                    access_tier=_access_tier_for_domain("academic", True),
                    confidence=resolved.confidence,
                    reason="specialist_supervisor_resolved_intent:student_grades",
                ),
                evidence_pack=MessageEvidencePack(
                    strategy="structured_tools",
                    summary="Notas deterministicas do aluno resolvido pela memoria discursiva.",
                    source_count=1,
                    support_count=1,
                    supports=[
                        MessageEvidenceSupport(kind="academic_summary", label=support_label, detail=deps.safe_excerpt(answer_text, limit=180)),
                    ],
                ),
                suggested_replies=_default_suggested_replies("academic"),
                graph_path=["specialist_supervisor", "resolved_intent", "student_grades"],
                reason="specialist_supervisor_resolved_intent:student_grades",
            )
    summaries: list[dict[str, Any]] = []
    for student in deps.linked_students(ctx.actor, capability="academic"):
        payload = await deps.fetch_academic_summary_payload(ctx, student_name_hint=str(student.get("full_name") or ""))
        summary = payload.get("summary") if isinstance(payload, dict) else None
        if isinstance(summary, dict):
            summaries.append(summary)
    if not summaries:
        return None
    return SupervisorAnswerPayload(
        message_text=deps.compose_academic_aggregate_answer(summaries),
        mode="structured_tool",
        classification=MessageIntentClassification(
            domain="academic",
            access_tier=_access_tier_for_domain("academic", True),
            confidence=resolved.confidence,
            reason="specialist_supervisor_resolved_intent:academic_summary_aggregate",
        ),
        evidence_pack=MessageEvidencePack(
            strategy="structured_tools",
            summary="Panorama academico quando a pergunta pede notas sem delimitar um unico aluno.",
            source_count=len(summaries),
            support_count=len(summaries),
            supports=[
                MessageEvidenceSupport(
                    kind="academic_summary",
                    label=str(summary.get("student_name") or "Aluno"),
                    detail=deps.safe_excerpt(deps.compose_academic_snapshot_lines(summary)[0], limit=180),
                )
                for summary in summaries[:4]
            ],
        ),
        suggested_replies=_default_suggested_replies("academic"),
        graph_path=["specialist_supervisor", "resolved_intent", "academic_summary_aggregate"],
        reason="specialist_supervisor_resolved_intent:academic_summary_aggregate",
    )


async def _resolved_academic_attendance_summary_answer(
    ctx: Any,
    resolved: ResolvedTurnIntent,
    *,
    deps: ResolvedIntentDeps,
) -> SupervisorAnswerPayload | None:
    if not ctx.request.user.authenticated:
        return None
    memory = ctx.operational_memory or OperationalMemory()
    subject_hint = str(resolved.referenced_subject or "").strip() or (
        memory.active_subject if deps.looks_like_subject_followup(ctx.request.message) else None
    )
    target_name = deps.student_hint_from_message(
        ctx.actor,
        ctx.request.message,
    ) or deps.resolved_academic_target_name(ctx, resolved=resolved)
    if not target_name:
        target_name = str(memory.active_student_name or "").strip() or _recent_linked_student_name(ctx, deps=deps)
    if deps.needs_specific_academic_student_clarification(ctx, target_name=target_name, subject_hint=subject_hint):
        summaries: list[dict[str, Any]] = []
        for student in deps.linked_students(ctx.actor, capability="academic"):
            student_name = str(student.get("full_name") or "").strip()
            if not student_name:
                continue
            payload = await deps.fetch_academic_summary_payload(ctx, student_name_hint=student_name)
            summary = payload.get("summary") if isinstance(payload, dict) else None
            if isinstance(summary, dict):
                summaries.append(summary)
        if summaries:
            def _attendance_totals(summary: dict[str, Any]) -> tuple[int, int, int]:
                attendance = summary.get("attendance")
                absent_total = 0
                late_total = 0
                absent_minutes_total = 0
                if isinstance(attendance, list):
                    for row in attendance:
                        if not isinstance(row, dict):
                            continue
                        absent_total += int(row.get("absent_count") or 0)
                        late_total += int(row.get("late_count") or 0)
                        absent_minutes_total += int(row.get("absent_minutes") or 0)
                return absent_total, late_total, absent_minutes_total

            lines = ["Panorama de faltas e frequencia das contas vinculadas:"]
            strongest_name = None
            strongest_score = (-1, -1, -1)
            supports: list[MessageEvidenceSupport] = []
            for summary in summaries:
                answer_line = deps.compose_named_attendance_answer(summary, subject_hint=subject_hint)
                student_name = str(summary.get("student_name") or "Aluno").strip() or "Aluno"
                if answer_line:
                    lines.append(f"- {answer_line}")
                    supports.append(
                        MessageEvidenceSupport(
                            kind="academic_summary",
                            label=student_name,
                            detail=deps.safe_excerpt(answer_line, limit=180),
                        )
                    )
                score = _attendance_totals(summary)
                if score > strongest_score:
                    strongest_score = score
                    strongest_name = student_name
            if strongest_name and strongest_score > (0, 0, 0):
                lines.append(f"Quem exige maior atencao agora: {strongest_name}.")
            return SupervisorAnswerPayload(
                message_text="\n".join(lines),
                mode="structured_tool",
                classification=MessageIntentClassification(
                    domain="academic",
                    access_tier=_access_tier_for_domain("academic", True),
                    confidence=resolved.confidence,
                    reason="specialist_supervisor_resolved_intent:attendance_summary_aggregate",
                ),
                evidence_pack=MessageEvidencePack(
                    strategy="structured_tools",
                    summary="Panorama agregado de frequencia sem exigir escolha manual do aluno quando a pergunta pede os filhos.",
                    source_count=len(summaries),
                    support_count=len(supports),
                    supports=supports[:4],
                ),
                suggested_replies=_default_suggested_replies("academic"),
                graph_path=["specialist_supervisor", "resolved_intent", "attendance_summary_aggregate"],
                reason="specialist_supervisor_resolved_intent:attendance_summary_aggregate",
            )
        return deps.build_academic_student_selection_clarify(
            ctx,
            reason="specialist_supervisor_resolved_intent:attendance_clarify",
            graph_path=["specialist_supervisor", "resolved_intent", "attendance_clarify"],
            confidence=resolved.confidence,
        )
    if not target_name:
        return None
    payload = await deps.fetch_academic_summary_payload(ctx, student_name_hint=target_name)
    summary = payload.get("summary") if isinstance(payload, dict) else None
    if not isinstance(summary, dict):
        return None
    normalized_message = deps.normalize_text(ctx.request.message)
    if any(
        term in normalized_message
        for term in {
            "principal alerta",
            "maior atencao",
            "maior atenção",
            "mais atencao",
            "mais atenção",
            "quem exige mais atencao",
            "quem exige mais atenção",
            "inspira mais atencao",
            "inspira mais atenção",
            "chama mais atencao",
            "chama mais atenção",
            "chamam atencao",
            "chamam atenção",
            "olhando as faltas",
            "bate na frequencia",
            "bate na frequência",
            "por que a frequencia",
            "por que a frequência",
            "frequencia dele preocupa",
            "frequência dele preocupa",
            "preocupa mais",
            "preocupa menos",
        }
    ):
        attendance = summary.get("attendance")
        if isinstance(attendance, list):
            priority_rows = [row for row in attendance if isinstance(row, dict)]
            priority_rows.sort(
                key=lambda row: (
                    -(int(row.get("absent_count", 0) or 0)),
                    -(int(row.get("late_count", 0) or 0)),
                    -(int(row.get("present_count", 0) or 0)),
                    deps.normalize_text(str(row.get("subject_name") or "")),
                )
            )
            if priority_rows:
                top_row = priority_rows[0]
                subject_name = str(top_row.get("subject_name") or "Disciplina").strip() or "Disciplina"
                absent = int(top_row.get("absent_count", 0) or 0)
                late = int(top_row.get("late_count", 0) or 0)
                present = int(top_row.get("present_count", 0) or 0)
                student_name = str(summary.get("student_name") or target_name or "Aluno").strip() or "Aluno"
                answer_text = (
                    f"O principal alerta de frequencia de {student_name} hoje aparece em {subject_name}: "
                    f"{absent} falta(s), {late} atraso(s) e {present} presenca(s) neste recorte. "
                    "Esse e o foco principal porque concentra a maior combinacao de faltas e atrasos do aluno neste momento. "
                    f"Proximo passo: acompanhar {subject_name} nas proximas aulas para verificar se novas faltas ou atrasos continuam pressionando a frequencia."
                )
                return SupervisorAnswerPayload(
                    message_text=answer_text,
                    mode="structured_tool",
                    classification=MessageIntentClassification(
                        domain="academic",
                        access_tier=_access_tier_for_domain("academic", True),
                        confidence=resolved.confidence,
                        reason="specialist_supervisor_resolved_intent:attendance_primary_alert",
                    ),
                    evidence_pack=MessageEvidencePack(
                        strategy="structured_tools",
                        summary="Principal alerta de frequencia do aluno resolvido deterministicamente.",
                        source_count=1,
                        support_count=1,
                        supports=[
                            MessageEvidenceSupport(
                                kind="academic_summary",
                                label=student_name,
                                detail=deps.safe_excerpt(answer_text, limit=180),
                            ),
                        ],
                    ),
                    suggested_replies=_default_suggested_replies("academic"),
                    graph_path=["specialist_supervisor", "resolved_intent", "attendance_primary_alert"],
                    reason="specialist_supervisor_resolved_intent:attendance_primary_alert",
                )
    if any(
        term in normalized_message
        for term in {
            "o que eu deveria acompanhar primeiro",
            "o que deveria acompanhar primeiro",
            "o que acompanhar primeiro",
            "sem repetir os numeros todos",
            "sem repetir os numeros",
            "proximo passo",
            "próximo passo",
        }
    ):
        attendance = summary.get("attendance")
        if isinstance(attendance, list):
            priority_rows = [row for row in attendance if isinstance(row, dict)]
            priority_rows.sort(
                key=lambda row: (
                    -(int(row.get("absent_count", 0) or 0)),
                    -(int(row.get("late_count", 0) or 0)),
                    -(int(row.get("absent_minutes", 0) or 0)),
                    deps.normalize_text(str(row.get("subject_name") or "")),
                )
            )
            if priority_rows:
                top_row = priority_rows[0]
                subject_name = str(top_row.get("subject_name") or "Disciplina").strip() or "Disciplina"
                absent = int(top_row.get("absent_count", 0) or 0)
                late = int(top_row.get("late_count", 0) or 0)
                student_name = str(summary.get("student_name") or target_name or "Aluno").strip() or "Aluno"
                answer_text = (
                    f"O proximo passo para {student_name} e acompanhar primeiro {subject_name}, "
                    f"porque esse componente concentra {absent} falta(s) e {late} atraso(s) neste recorte. "
                    "Na pratica, vale monitorar novas ausencias e alinhar a rotina antes que esse ponto siga acumulando risco."
                )
                return SupervisorAnswerPayload(
                    message_text=answer_text,
                    mode="structured_tool",
                    classification=MessageIntentClassification(
                        domain="academic",
                        access_tier=_access_tier_for_domain("academic", True),
                        confidence=resolved.confidence,
                        reason="specialist_supervisor_resolved_intent:attendance_next_step",
                    ),
                    evidence_pack=MessageEvidencePack(
                        strategy="structured_tools",
                        summary="Proximo passo de frequencia do aluno resolvido deterministicamente.",
                        source_count=1,
                        support_count=1,
                        supports=[
                            MessageEvidenceSupport(
                                kind="academic_summary",
                                label=student_name,
                                detail=deps.safe_excerpt(answer_text, limit=180),
                            ),
                        ],
                    ),
                    suggested_replies=_default_suggested_replies("academic"),
                    graph_path=["specialist_supervisor", "resolved_intent", "attendance_next_step"],
                    reason="specialist_supervisor_resolved_intent:attendance_next_step",
                )
    answer_text = deps.compose_named_attendance_answer(summary, subject_hint=subject_hint)
    if not answer_text:
        return None
    return SupervisorAnswerPayload(
        message_text=answer_text,
        mode="structured_tool",
        classification=MessageIntentClassification(
            domain="academic",
            access_tier=_access_tier_for_domain("academic", True),
            confidence=resolved.confidence,
            reason="specialist_supervisor_resolved_intent:attendance_summary",
        ),
        evidence_pack=MessageEvidencePack(
            strategy="structured_tools",
            summary="Frequencia deterministica do aluno resolvido pela memoria discursiva.",
            source_count=1,
            support_count=1,
            supports=[
                MessageEvidenceSupport(kind="academic_summary", label=str(summary.get("student_name") or "Aluno"), detail=deps.safe_excerpt(answer_text, limit=180)),
            ],
        ),
        suggested_replies=_default_suggested_replies("academic"),
        graph_path=["specialist_supervisor", "resolved_intent", "attendance_summary"],
        reason="specialist_supervisor_resolved_intent:attendance_summary",
    )


async def _resolved_finance_student_summary_answer(
    ctx: Any,
    resolved: ResolvedTurnIntent,
    *,
    deps: ResolvedIntentDeps,
) -> SupervisorAnswerPayload | None:
    if not ctx.request.user.authenticated:
        return None
    wants_family_finance_aggregate = deps.looks_like_family_finance_aggregate_query(ctx.request.message)
    finance_students = deps.linked_students(ctx.actor, capability="finance")
    target_name = str(resolved.referenced_student_name or "").strip()
    normalized_target = deps.normalize_text(target_name)
    if target_name and finance_students:
        linked_names = {
            deps.normalize_text(str(student.get("full_name") or ""))
            for student in finance_students
            if str(student.get("full_name") or "").strip()
        }
        if normalized_target and normalized_target not in linked_names:
            linked_preview = ", ".join(
                str(student.get("full_name") or "").strip()
                for student in finance_students
                if str(student.get("full_name") or "").strip()
            )
            return SupervisorAnswerPayload(
                message_text=(
                    f"Nao posso expor o financeiro de {target_name} porque esse aluno nao aparece entre os vinculados desta conta. "
                    + (
                        f"No recorte atual, eu consigo consultar apenas: {linked_preview}."
                        if linked_preview
                        else "No recorte atual, eu consigo consultar apenas os alunos vinculados desta sessao."
                    )
                ),
                mode="deny",
                classification=MessageIntentClassification(
                    domain="finance",
                    access_tier=_access_tier_for_domain("finance", True),
                    confidence=0.99,
                    reason="specialist_supervisor_resolved_intent:finance_third_party_denied",
                ),
                evidence_pack=MessageEvidencePack(
                    strategy="deny",
                    summary="Pedido de financeiro para aluno nao vinculado negado por privacidade.",
                    source_count=1,
                    support_count=1,
                    supports=[
                        MessageEvidenceSupport(
                            kind="privacy_guardrail",
                            label="Aluno nao vinculado",
                            detail=target_name,
                        )
                    ],
                ),
                suggested_replies=_default_suggested_replies("finance"),
                graph_path=["specialist_supervisor", "resolved_intent", "finance_third_party_denied"],
                risk_flags=["privacy_guardrail"],
                reason="specialist_supervisor_resolved_intent:finance_third_party_denied",
            )
    if not target_name and wants_family_finance_aggregate:
        summaries: list[dict[str, Any]] = []
        for student in finance_students:
            payload = await deps.fetch_financial_summary_payload(ctx, student_name_hint=str(student.get("full_name") or ""))
            summary = payload.get("summary") if isinstance(payload, dict) else None
            if isinstance(summary, dict):
                summaries.append(summary)
        if summaries:
            return SupervisorAnswerPayload(
                message_text=deps.compose_finance_aggregate_answer(summaries),
                mode="structured_tool",
                classification=MessageIntentClassification(
                    domain="finance",
                    access_tier=_access_tier_for_domain("finance", True),
                    confidence=resolved.confidence,
                    reason="specialist_supervisor_resolved_intent:financial_summary_aggregate",
                ),
                evidence_pack=MessageEvidencePack(
                    strategy="structured_tools",
                    summary="Resumo financeiro agregado resolvido pela memoria discursiva e pelos alunos vinculados.",
                    source_count=len(summaries),
                    support_count=len(summaries),
                    supports=[
                        MessageEvidenceSupport(
                            kind="finance_summary",
                            label=str(summary.get("student_name") or "Aluno"),
                            detail=f"em aberto {summary.get('open_invoice_count', 0)} · vencidas {summary.get('overdue_invoice_count', 0)}",
                        )
                        for summary in summaries[:4]
                    ],
                ),
                suggested_replies=_default_suggested_replies("finance"),
                graph_path=["specialist_supervisor", "resolved_intent", "financial_summary_aggregate"],
                reason="specialist_supervisor_resolved_intent:financial_summary_aggregate",
            )
        finance_names = [
            str(student.get("full_name") or "").strip()
            for student in finance_students
            if str(student.get("full_name") or "").strip()
        ]
        if finance_names:
            return SupervisorAnswerPayload(
                message_text=(
                    "Resumo financeiro da familia hoje: "
                    f"{', '.join(finance_names)}. "
                    "Nao consegui carregar agora os vencimentos e proximos passos detalhados."
                ),
                mode="structured_tool",
                classification=MessageIntentClassification(
                    domain="finance",
                    access_tier=_access_tier_for_domain("finance", True),
                    confidence=resolved.confidence,
                    reason="specialist_supervisor_resolved_intent:financial_summary_aggregate_fallback",
                ),
                evidence_pack=MessageEvidencePack(
                    strategy="structured_tools",
                    summary="Fallback seguro para resumo financeiro agregado resolvido pela memoria discursiva.",
                    source_count=0,
                    support_count=0,
                ),
                suggested_replies=_default_suggested_replies("finance"),
                graph_path=["specialist_supervisor", "resolved_intent", "financial_summary_aggregate_fallback"],
                reason="specialist_supervisor_resolved_intent:financial_summary_aggregate_fallback",
            )
    if not target_name and len(finance_students) > 1:
        return SupervisorAnswerPayload(
            message_text=(
                "Consigo verificar o financeiro por aluno, mas aqui ainda faltou dizer qual recorte voce quer. "
                "Se a ideia for um panorama da familia, eu separo mensalidade, taxa, atraso e desconto no conjunto. "
                "Se voce quiser um aluno especifico, me diga qual deles."
            ),
            mode="clarify",
            classification=MessageIntentClassification(
                domain="finance",
                access_tier=_access_tier_for_domain("finance", True),
                confidence=resolved.confidence,
                reason="specialist_supervisor_resolved_intent:finance_student_clarify",
            ),
            suggested_replies=[
                MessageResponseSuggestedReply(text="Lucas Oliveira"),
                MessageResponseSuggestedReply(text="Ana Oliveira"),
            ],
            graph_path=["specialist_supervisor", "resolved_intent", "finance_student_clarify"],
            reason="specialist_supervisor_resolved_intent:finance_student_clarify",
        )
    if not target_name:
        student = next(iter(finance_students), None)
        target_name = str(student.get("full_name") or "").strip() if isinstance(student, dict) else ""
    if not target_name:
        return None
    payload = await deps.fetch_financial_summary_payload(ctx, student_name_hint=target_name)
    summary = payload.get("summary") if isinstance(payload, dict) else None
    if not isinstance(summary, dict):
        return None
    answer_text = (
        deps.compose_finance_installments_answer(summary)
        if "parcela" in deps.normalize_text(ctx.request.message)
        else deps.compose_finance_aggregate_answer([summary])
    )
    return SupervisorAnswerPayload(
        message_text=answer_text,
        mode="structured_tool",
        classification=MessageIntentClassification(
            domain="finance",
            access_tier=_access_tier_for_domain("finance", True),
            confidence=resolved.confidence,
            reason="specialist_supervisor_resolved_intent:finance_student_summary",
        ),
        evidence_pack=MessageEvidencePack(
            strategy="structured_tools",
            summary="Resumo financeiro deterministico do aluno resolvido pela memoria discursiva.",
            source_count=1,
            support_count=1,
            supports=[
                MessageEvidenceSupport(kind="finance_summary", label=str(summary.get("student_name") or "Aluno"), detail=f"em aberto {summary.get('open_invoice_count', 0)} · vencidas {summary.get('overdue_invoice_count', 0)}"),
            ],
        ),
        suggested_replies=_default_suggested_replies("finance"),
        graph_path=["specialist_supervisor", "resolved_intent", "finance_student_summary"],
        reason="specialist_supervisor_resolved_intent:finance_student_summary",
    )


async def maybe_resolved_intent_answer(
    ctx: Any,
    *,
    deps: ResolvedIntentDeps,
) -> SupervisorAnswerPayload | None:
    recent_context_answer = await _maybe_recent_context_followup_answer(ctx, deps=deps)
    if recent_context_answer is not None:
        return recent_context_answer
    resolved = ctx.resolved_turn
    if resolved is None or resolved.domain == "unknown":
        return None
    if _looks_like_public_pricing_navigation_query(
        ctx.request.message,
        deps=deps,
    ) or _looks_like_public_pricing_context_follow_up(ctx, deps=deps):
        return None
    normalized_message = deps.normalize_text(ctx.request.message)
    if ctx.request.user.authenticated and "documentacao" in normalized_message and any(
        term in normalized_message for term in {"financeiro", "bloque", "boleto", "mensalidade", "fatura"}
    ):
        return None
    handlers: dict[str, Any] = {
        "institution.shift_offers": _resolved_shift_offers_answer,
        "institution.interval_schedule": _resolved_interval_schedule_answer,
        "academic.student_grades": _resolved_academic_student_grades_answer,
        "academic.attendance_summary": _resolved_academic_attendance_summary_answer,
        "finance.student_summary": _resolved_finance_student_summary_answer,
    }
    handler = handlers.get(resolved.capability)
    if handler is None:
        return None
    return await handler(ctx, resolved, deps=deps)
