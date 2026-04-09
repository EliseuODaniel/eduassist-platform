from __future__ import annotations

import asyncio
from dataclasses import dataclass
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
    OperationalMemory,
    SupervisorAnswerPayload,
)


@dataclass(frozen=True)
class OperationalMemoryDeps:
    normalize_text: Callable[[str | None], str]
    looks_like_public_doc_bundle_request: Callable[[str], bool]
    is_student_name_only_followup: Callable[..., str | None]
    effective_multi_intent_domains: Callable[[Any, str], list[str]]
    subject_hint_from_text: Callable[[str], str | None]
    looks_like_subject_followup: Callable[[str], bool]
    looks_like_student_pronoun_followup: Callable[[str], bool]
    student_hint_from_message: Callable[..., str | None]
    fetch_academic_summary_payload: Callable[..., Awaitable[dict[str, Any] | None]]
    fetch_financial_summary_payload: Callable[..., Awaitable[dict[str, Any] | None]]
    fetch_upcoming_assessments_payload: Callable[..., Awaitable[dict[str, Any] | None]]
    build_academic_finance_combo_payload: Callable[..., SupervisorAnswerPayload]
    build_grade_requirement_answer: Callable[..., SupervisorAnswerPayload]
    compose_academic_risk_answer: Callable[[dict[str, Any]], str]
    compose_named_subject_grade_answer: Callable[..., str | None]
    compose_upcoming_assessments_lines: Callable[[dict[str, Any]], list[str]]
    safe_excerpt: Callable[..., str | None]
    looks_like_academic_risk_followup: Callable[[str], bool]
    looks_like_other_student_followup: Callable[[str], bool]
    other_linked_student: Callable[..., dict[str, Any] | None]
    compose_admin_status_answer: Callable[[dict[str, Any]], str]
    compose_named_grade_answer: Callable[[dict[str, Any]], str]
    compose_finance_installments_answer: Callable[[dict[str, Any]], str]


def _looks_like_meta_repair_question(message: str, *, deps: OperationalMemoryDeps) -> bool:
    normalized = deps.normalize_text(message)
    return any(
        term in normalized
        for term in {
            "essa resposta",
            "resposta aqui",
            "era sobre o que",
            "mas voce falou",
            "mas você falou",
        }
    )


def _compose_meta_repair_answer(memory: OperationalMemory) -> str | None:
    active_domain = str(memory.active_domain or "").strip()
    active_student_name = str(memory.active_student_name or "").strip()
    active_subject = str(memory.active_subject or "").strip()
    active_topic = str(memory.active_topic or "").strip()
    if active_domain == "academic":
        scope = f" sobre {active_student_name}" if active_student_name else ""
        if active_subject:
            return f"A resposta anterior estava falando das proximas provas{scope}, com foco em {active_subject}."
        if active_topic == "upcoming_assessments":
            return f"A resposta anterior estava falando das proximas avaliacoes{scope}."
        if active_topic == "attendance":
            return f"A resposta anterior estava falando da frequencia{scope}."
        return f"A resposta anterior estava falando do panorama academico{scope}."
    if active_domain == "finance":
        scope = f" de {active_student_name}" if active_student_name else ""
        return f"A resposta anterior estava falando do financeiro{scope}."
    if active_domain == "institution":
        return "A resposta anterior estava falando do status administrativo ou documental desta conta."
    return None


def _filtered_upcoming_summary(
    summary: dict[str, Any],
    *,
    subject_hint: str | None,
    deps: OperationalMemoryDeps,
) -> dict[str, Any]:
    if not subject_hint:
        return summary
    assessments = summary.get("assessments")
    if not isinstance(assessments, list):
        return summary
    filtered = [
        item
        for item in assessments
        if isinstance(item, dict)
        and deps.normalize_text(item.get("subject_name")) == deps.normalize_text(subject_hint)
    ]
    updated = dict(summary)
    updated["assessments"] = filtered
    return updated


def _can_carry_active_subject(
    *,
    message: str,
    memory: OperationalMemory,
    student_name_only_followup: str | None,
    student_pronoun_followup: bool,
    other_student_followup: bool,
    explicit_subject_hint: str | None,
    deps: OperationalMemoryDeps,
) -> bool:
    if _looks_like_meta_repair_question(message, deps=deps):
        return False
    if explicit_subject_hint:
        return True
    if not memory.active_subject or memory.active_domain != "academic":
        return False
    if deps.looks_like_subject_followup(message):
        return True
    if memory.pending_kind == "academic_subject" and (
        student_name_only_followup or student_pronoun_followup or other_student_followup
    ):
        return True
    if memory.active_topic == "grade_requirement" and (
        student_name_only_followup or student_pronoun_followup or other_student_followup
    ):
        return True
    return False


def _build_memory_payload(
    *,
    message_text: str,
    domain: str,
    access_tier: str,
    confidence: float,
    reason: str,
    summary: str,
    supports: list[MessageEvidenceSupport],
    graph_leaf: str,
    suggested_domain: str | None = None,
) -> SupervisorAnswerPayload:
    return SupervisorAnswerPayload(
        message_text=message_text,
        mode="structured_tool",
        classification=MessageIntentClassification(
            domain=domain,
            access_tier=access_tier,
            confidence=confidence,
            reason=reason,
        ),
        evidence_pack=MessageEvidencePack(
            strategy="structured_tools",
            summary=summary,
            source_count=max(len(supports), 1 if supports else 0),
            support_count=len(supports),
            supports=supports,
        ),
        suggested_replies=_default_suggested_replies(suggested_domain or domain),
        graph_path=["specialist_supervisor", "operational_memory", graph_leaf],
        reason=reason,
    )


async def maybe_operational_memory_follow_up_answer(
    ctx: Any,
    *,
    deps: OperationalMemoryDeps,
) -> SupervisorAnswerPayload | None:
    memory = ctx.operational_memory or OperationalMemory()
    if not ctx.request.user.authenticated:
        return None
    if deps.looks_like_public_doc_bundle_request(ctx.request.message):
        return None
    student_name_only_followup = deps.is_student_name_only_followup(ctx.actor, ctx.request.message)
    student_pronoun_followup = deps.looks_like_student_pronoun_followup(ctx.request.message)
    other_student_followup = deps.looks_like_other_student_followup(ctx.request.message)
    explicit_student_hint = deps.student_hint_from_message(ctx.actor, ctx.request.message)
    if _looks_like_meta_repair_question(ctx.request.message, deps=deps):
        answer_text = _compose_meta_repair_answer(memory)
        if answer_text:
            return _build_memory_payload(
                message_text=answer_text,
                domain=memory.active_domain or "institution",
                access_tier=_access_tier_for_domain(memory.active_domain or "institution", True),
                confidence=0.97,
                reason="specialist_supervisor_memory:meta_repair",
                summary="Reparo meta curto explicando o assunto da resposta anterior.",
                supports=[],
                graph_leaf="meta_repair",
                suggested_domain=memory.active_domain or "institution",
            )
        return None
    multi_domains = deps.effective_multi_intent_domains(memory, ctx.request.message)
    explicit_subject_hint = deps.subject_hint_from_text(ctx.request.message)
    carry_active_subject = _can_carry_active_subject(
        message=ctx.request.message,
        memory=memory,
        student_name_only_followup=student_name_only_followup,
        student_pronoun_followup=student_pronoun_followup,
        other_student_followup=other_student_followup,
        explicit_subject_hint=explicit_subject_hint,
        deps=deps,
    )
    subject_hint = explicit_subject_hint or (memory.active_subject if carry_active_subject else None)

    if len(multi_domains) >= 2 and "academic" in multi_domains and "finance" in multi_domains:
        target_name = explicit_student_hint or student_name_only_followup or (
            memory.active_student_name if (student_pronoun_followup or other_student_followup) else None
        )
        if target_name:
            academic_payload, finance_payload = await asyncio.gather(
                deps.fetch_academic_summary_payload(ctx, student_name_hint=target_name),
                deps.fetch_financial_summary_payload(ctx, student_name_hint=target_name),
            )
            academic_summary = academic_payload.get("summary") if isinstance(academic_payload, dict) else None
            finance_summary = finance_payload.get("summary") if isinstance(finance_payload, dict) else None
            if isinstance(academic_summary, dict) and isinstance(finance_summary, dict):
                return deps.build_academic_finance_combo_payload(
                    academic_summary=academic_summary,
                    finance_summary=finance_summary,
                    reason="specialist_supervisor_memory:academic_finance_combo",
                    graph_path=["specialist_supervisor", "operational_memory", "academic_finance_combo"],
                )

    if ctx.operational_memory is None:
        return None

    if student_name_only_followup and memory.pending_kind == "upcoming_assessments_student_selection":
        payload = await deps.fetch_upcoming_assessments_payload(ctx, student_name_hint=student_name_only_followup)
        student = payload.get("student") if isinstance(payload, dict) else None
        summary = payload.get("summary") if isinstance(payload, dict) else None
        if isinstance(student, dict) and isinstance(summary, dict):
            filtered_summary = _filtered_upcoming_summary(summary, subject_hint=memory.active_subject, deps=deps)
            student_name = str(student.get("full_name") or student_name_only_followup or "Aluno").strip() or "Aluno"
            lines = [f"Proximas avaliacoes de {student_name}:"]
            lines.extend(deps.compose_upcoming_assessments_lines(filtered_summary))
            return _build_memory_payload(
                message_text="\n".join(lines),
                domain="academic",
                access_tier=_access_tier_for_domain("academic", True),
                confidence=0.98,
                reason="specialist_supervisor_memory:upcoming_assessments_student_selection",
                summary="Selecao de aluno resolvida pela memoria operacional para proximas avaliacoes.",
                supports=[
                    MessageEvidenceSupport(
                        kind="upcoming_assessments",
                        label=student_name,
                        detail=deps.safe_excerpt("\n".join(lines), limit=180),
                    )
                ],
                graph_leaf="upcoming_assessments_student_selection",
                suggested_domain="academic",
            )

    if (
        memory.active_student_name
        and memory.active_domain in {"academic", "finance"}
        and carry_active_subject
    ):
        payload = await deps.fetch_academic_summary_payload(ctx, student_name_hint=memory.active_student_name)
        student = payload.get("student") if isinstance(payload, dict) else None
        summary = payload.get("summary") if isinstance(payload, dict) else None
        if isinstance(student, dict) and isinstance(summary, dict):
            if memory.active_topic == "grade_requirement":
                return deps.build_grade_requirement_answer(student=student, summary=summary, subject_hint=subject_hint)
            answer_text = deps.compose_named_subject_grade_answer(summary, subject_hint=subject_hint)
            if not answer_text and subject_hint:
                student_name = str(student.get("full_name") or memory.active_student_name or "Aluno").strip() or "Aluno"
                if "existe na base" in deps.normalize_text(ctx.request.message):
                    answer_text = (
                        f"No recorte academico atual, nao encontrei disciplina ou registros de {student_name} em {subject_hint}."
                    )
                else:
                    answer_text = (
                        f"No recorte academico atual, nao encontrei notas de {student_name} em {subject_hint}."
                    )
            if answer_text:
                return _build_memory_payload(
                    message_text=answer_text,
                    domain="academic",
                    access_tier=_access_tier_for_domain("academic", True),
                    confidence=0.98,
                    reason="specialist_supervisor_memory:subject_followup",
                    summary="Follow-up academico deterministico preservando aluno e disciplina ativos.",
                    supports=[
                        MessageEvidenceSupport(
                            kind="academic_summary",
                            label=str(summary.get("student_name") or "Aluno"),
                            detail=deps.safe_excerpt(answer_text, limit=180),
                        ),
                    ],
                    graph_leaf="subject_followup",
                    suggested_domain="academic",
                )

    target_risk_student = (
        explicit_student_hint
        or student_name_only_followup
        or memory.active_student_name
    )
    if (
        target_risk_student
        and memory.active_domain == "academic"
        and deps.looks_like_academic_risk_followup(ctx.request.message)
    ):
        payload = await deps.fetch_academic_summary_payload(ctx, student_name_hint=target_risk_student)
        summary = payload.get("summary") if isinstance(payload, dict) else None
        if isinstance(summary, dict):
            answer_text = deps.compose_academic_risk_answer(summary)
            if answer_text:
                return _build_memory_payload(
                    message_text=answer_text,
                    domain="academic",
                    access_tier=_access_tier_for_domain("academic", True),
                    confidence=0.98,
                    reason="specialist_supervisor_memory:academic_risk_followup",
                    summary="Follow-up academico deterministico destacando os componentes com maior risco.",
                    supports=[
                        MessageEvidenceSupport(
                            kind="academic_summary",
                            label=str(summary.get("student_name") or "Aluno"),
                            detail=deps.safe_excerpt(answer_text, limit=180),
                        ),
                    ],
                    graph_leaf="academic_risk_followup",
                    suggested_domain="academic",
                )

    if other_student_followup:
        if memory.active_domain == "academic" and memory.active_student_id:
            other = deps.other_linked_student(ctx.actor, capability="academic", current_student_id=memory.active_student_id)
            if isinstance(other, dict):
                payload = await deps.fetch_academic_summary_payload(ctx, student_name_hint=str(other.get("full_name") or ""))
                summary = payload.get("summary") if isinstance(payload, dict) else None
                if isinstance(summary, dict):
                    if memory.active_topic == "grade_requirement":
                        return deps.build_grade_requirement_answer(
                            student=other,
                            summary=summary,
                            subject_hint=memory.active_subject,
                        )
                    if memory.active_topic == "administrative_status":
                        return _build_memory_payload(
                            message_text=deps.compose_admin_status_answer(summary),
                            domain="academic",
                            access_tier=_access_tier_for_domain("academic", True),
                            confidence=0.98,
                            reason="specialist_supervisor_memory:other_student_administrative_status",
                            summary="Follow-up deterministico usando o outro aluno vinculado.",
                            supports=[
                                MessageEvidenceSupport(
                                    kind="administrative_status",
                                    label=str(summary.get("student_name") or "Aluno"),
                                    detail=str(summary.get("overall_status") or ""),
                                ),
                            ],
                            graph_leaf="other_student_administrative_status",
                            suggested_domain="academic",
                        )
                    answer_text = deps.compose_named_grade_answer(summary)
                    return _build_memory_payload(
                        message_text=answer_text,
                        domain="academic",
                        access_tier=_access_tier_for_domain("academic", True),
                        confidence=0.98,
                        reason="specialist_supervisor_memory:other_student_academic",
                        summary="Follow-up deterministico usando o outro aluno vinculado.",
                        supports=[
                            MessageEvidenceSupport(
                                kind="academic_summary",
                                label=str(summary.get("student_name") or "Aluno"),
                                detail=deps.safe_excerpt(answer_text, limit=180),
                            ),
                        ],
                        graph_leaf="other_student_academic",
                        suggested_domain="academic",
                    )
        if memory.active_domain == "finance" and memory.active_student_id:
            other = deps.other_linked_student(ctx.actor, capability="finance", current_student_id=memory.active_student_id)
            if isinstance(other, dict):
                payload = await deps.fetch_financial_summary_payload(ctx, student_name_hint=str(other.get("full_name") or ""))
                summary = payload.get("summary") if isinstance(payload, dict) else None
                if isinstance(summary, dict):
                    return _build_memory_payload(
                        message_text=deps.compose_finance_installments_answer(summary),
                        domain="finance",
                        access_tier=_access_tier_for_domain("finance", True),
                        confidence=0.98,
                        reason="specialist_supervisor_memory:other_student_finance",
                        summary="Follow-up financeiro deterministico usando o outro aluno vinculado.",
                        supports=[
                            MessageEvidenceSupport(
                                kind="finance_summary",
                                label=str(summary.get("student_name") or "Aluno"),
                                detail=f"em aberto {summary.get('open_invoice_count', 0)} · vencidas {summary.get('overdue_invoice_count', 0)}",
                            ),
                        ],
                        graph_leaf="other_student_finance",
                        suggested_domain="finance",
                    )

    if student_name_only_followup and memory.pending_kind in {"student_selection", "academic_subject"}:
        if memory.active_domain == "academic":
            payload = await deps.fetch_academic_summary_payload(ctx, student_name_hint=student_name_only_followup)
            student = payload.get("student") if isinstance(payload, dict) else None
            summary = payload.get("summary") if isinstance(payload, dict) else None
            if isinstance(student, dict) and isinstance(summary, dict):
                if memory.active_topic == "grade_requirement" or memory.pending_kind == "academic_subject":
                    return deps.build_grade_requirement_answer(student=student, summary=summary, subject_hint=memory.active_subject)
                if memory.active_topic == "administrative_status":
                    return _build_memory_payload(
                        message_text=deps.compose_admin_status_answer(summary),
                        domain="academic",
                        access_tier=_access_tier_for_domain("academic", True),
                        confidence=0.98,
                        reason="specialist_supervisor_memory:student_selection_administrative_status",
                        summary="Selecao de aluno resolvida pela memoria operacional.",
                        supports=[
                            MessageEvidenceSupport(
                                kind="administrative_status",
                                label=str(summary.get("student_name") or "Aluno"),
                                detail=str(summary.get("overall_status") or ""),
                            ),
                        ],
                        graph_leaf="student_selection_administrative_status",
                        suggested_domain="academic",
                    )
                answer_text = deps.compose_named_grade_answer(summary)
                return _build_memory_payload(
                    message_text=answer_text,
                    domain="academic",
                    access_tier=_access_tier_for_domain("academic", True),
                    confidence=0.98,
                    reason="specialist_supervisor_memory:student_selection_academic",
                    summary="Selecao de aluno resolvida pela memoria operacional.",
                    supports=[
                        MessageEvidenceSupport(
                            kind="academic_summary",
                            label=str(summary.get("student_name") or "Aluno"),
                            detail=deps.safe_excerpt(answer_text, limit=180),
                        ),
                    ],
                    graph_leaf="student_selection_academic",
                    suggested_domain="academic",
                )
        if memory.active_domain == "finance":
            payload = await deps.fetch_financial_summary_payload(ctx, student_name_hint=student_name_only_followup)
            summary = payload.get("summary") if isinstance(payload, dict) else None
            if isinstance(summary, dict):
                return _build_memory_payload(
                    message_text=deps.compose_finance_installments_answer(summary),
                    domain="finance",
                    access_tier=_access_tier_for_domain("finance", True),
                    confidence=0.98,
                    reason="specialist_supervisor_memory:student_selection_finance",
                    summary="Selecao de aluno financeiro resolvida pela memoria operacional.",
                    supports=[
                        MessageEvidenceSupport(
                            kind="finance_summary",
                            label=str(summary.get("student_name") or "Aluno"),
                            detail=f"em aberto {summary.get('open_invoice_count', 0)} · vencidas {summary.get('overdue_invoice_count', 0)}",
                        ),
                    ],
                    graph_leaf="student_selection_finance",
                    suggested_domain="finance",
                )

    return None
