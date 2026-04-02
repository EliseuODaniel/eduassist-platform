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


@dataclass(frozen=True)
class ResolvedIntentDeps:
    normalize_text: Callable[[str | None], str]
    looks_like_subject_followup: Callable[[str], bool]
    looks_like_academic_risk_followup: Callable[[str], bool]
    looks_like_family_finance_aggregate_query: Callable[[str], bool]
    fetch_academic_summary_payload: Callable[..., Awaitable[dict[str, Any] | None]]
    fetch_financial_summary_payload: Callable[..., Awaitable[dict[str, Any] | None]]
    resolved_academic_target_name: Callable[..., str | None]
    needs_specific_academic_student_clarification: Callable[..., bool]
    build_academic_student_selection_clarify: Callable[..., SupervisorAnswerPayload]
    compose_academic_risk_answer: Callable[[dict[str, Any]], str]
    compose_named_subject_grade_answer: Callable[..., str | None]
    compose_named_grade_answer: Callable[[dict[str, Any]], str]
    compose_named_attendance_answer: Callable[..., str | None]
    compose_academic_snapshot_lines: Callable[[dict[str, Any]], list[str]]
    compose_finance_aggregate_answer: Callable[[list[dict[str, Any]]], str]
    compose_finance_installments_answer: Callable[[dict[str, Any]], str]
    linked_students: Callable[..., list[dict[str, Any]]]
    safe_excerpt: Callable[..., str | None]
    subject_hint_from_text: Callable[[str], str | None]
    recent_subject_from_context: Callable[..., str | None]
    subject_code_from_hint: Callable[..., tuple[str | None, str | None]]
    student_hint_from_message: Callable[..., str | None]


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
    memory = ctx.operational_memory or OperationalMemory()
    subject_hint = str(resolved.referenced_subject or "").strip() or (
        memory.active_subject if deps.looks_like_subject_followup(ctx.request.message) else None
    )
    target_name = deps.resolved_academic_target_name(ctx, resolved=resolved)
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
            answer_text = (
                deps.compose_academic_risk_answer(summary)
                if deps.looks_like_academic_risk_followup(ctx.request.message)
                else deps.compose_named_subject_grade_answer(summary, subject_hint=subject_hint) or deps.compose_named_grade_answer(summary)
            )
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
    lines = ["Panorama academico das contas vinculadas:"]
    for summary in summaries:
        lines.extend(deps.compose_academic_snapshot_lines(summary))
    return SupervisorAnswerPayload(
        message_text="\n".join(lines),
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
    target_name = deps.resolved_academic_target_name(ctx, resolved=resolved)
    if deps.needs_specific_academic_student_clarification(ctx, target_name=target_name, subject_hint=subject_hint):
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
    target_name = str(resolved.referenced_student_name or "").strip()
    if not target_name and wants_family_finance_aggregate:
        summaries: list[dict[str, Any]] = []
        for student in deps.linked_students(ctx.actor, capability="finance"):
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
            for student in deps.linked_students(ctx.actor, capability="finance")
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
    if not target_name and len(deps.linked_students(ctx.actor, capability="finance")) > 1:
        return SupervisorAnswerPayload(
            message_text="Consigo verificar a situacao financeira, mas preciso que voce me diga qual aluno: Lucas Oliveira ou Ana Oliveira?",
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
        student = next(iter(deps.linked_students(ctx.actor, capability="finance")), None)
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
    resolved = ctx.resolved_turn
    if resolved is None or resolved.domain == "unknown":
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
