from __future__ import annotations

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
    SupervisorAnswerPayload,
)
from .public_query_patterns import (
    _looks_like_actor_admin_status_query,
    _looks_like_passing_policy_query,
    _looks_like_public_doc_bundle_request,
)


@dataclass(frozen=True)
class ToolFirstProtectedDeps:
    contains_any: Callable[[str, set[str]], bool]
    looks_like_admin_finance_combo_query: Callable[[str], bool]
    looks_like_family_finance_aggregate_query: Callable[[str], bool]
    student_hint_from_message: Callable[..., str | None]
    looks_like_student_pronoun_followup: Callable[[str], bool]
    fetch_financial_summary_payload: Callable[..., Awaitable[dict[str, Any] | None]]
    linked_students: Callable[..., list[dict[str, Any]]]
    compose_finance_installments_answer: Callable[[dict[str, Any]], str]
    compose_finance_aggregate_answer: Callable[[list[dict[str, Any]]], str]
    looks_like_academic_risk_followup: Callable[[str], bool]
    looks_like_family_academic_aggregate_query: Callable[[str], bool]
    subject_hint_from_text: Callable[[str], str | None]
    looks_like_subject_followup: Callable[[str], bool]
    resolved_academic_target_name: Callable[..., str | None]
    needs_specific_academic_student_clarification: Callable[..., bool]
    build_academic_student_selection_clarify: Callable[..., SupervisorAnswerPayload]
    fetch_academic_summary_payload: Callable[..., Awaitable[dict[str, Any] | None]]
    compose_academic_risk_answer: Callable[[dict[str, Any]], str]
    compose_named_subject_grade_answer: Callable[..., str | None]
    compose_named_grade_answer: Callable[[dict[str, Any]], str]
    compose_academic_snapshot_lines: Callable[[dict[str, Any]], list[str]]
    safe_excerpt: Callable[..., str]
    http_get: Callable[..., Awaitable[dict[str, Any] | None]]
    compose_actor_admin_status_answer: Callable[[dict[str, Any]], str]
    recent_student_from_context_with_memory: Callable[..., dict[str, Any] | None]
    compose_admin_status_answer: Callable[[dict[str, Any]], str]
    find_student_by_hint: Callable[..., dict[str, Any] | None]


def _build_protected_tool_payload(
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
            source_count=max(len(supports), 0),
            support_count=len(supports),
            supports=supports,
        ),
        suggested_replies=_default_suggested_replies(suggested_domain or domain),
        graph_path=["specialist_supervisor", "tool_first", graph_leaf],
        reason=reason,
    )


async def maybe_tool_first_protected_answer(
    ctx: Any,
    *,
    normalized: str,
    preview: dict[str, Any],
    memory: Any,
    deps: ToolFirstProtectedDeps,
) -> SupervisorAnswerPayload | None:
    finance_terms = {
        "pagamento",
        "pagamentos",
        "financeiro",
        "mensalidade",
        "fatura",
        "faturas",
        "boleto",
        "boletos",
        "segunda via",
        "vencimento",
        "vencida",
        "vencidas",
        "parcela",
        "parcelas",
    }
    if ctx.request.user.authenticated and not deps.looks_like_admin_finance_combo_query(ctx.request.message) and (
        deps.contains_any(normalized, finance_terms)
        or str(preview.get("classification", {}).get("domain") or "") == "finance"
    ) and not any(term in normalized for term in {"documentacao", "documentação", "documental", "documentais", "pendencia", "pendencias", "pendência", "pendências", "cadastro", "cadastral"}):
        wants_family_finance_aggregate = deps.looks_like_family_finance_aggregate_query(ctx.request.message)
        student_hint = (
            None
            if wants_family_finance_aggregate
            else (
                str((ctx.resolved_turn.referenced_student_name if ctx.resolved_turn is not None else "") or "").strip()
                or deps.student_hint_from_message(ctx.actor, ctx.request.message)
                or (memory.active_student_name if deps.looks_like_student_pronoun_followup(ctx.request.message) else None)
            )
        )
        if student_hint:
            payload = await deps.fetch_financial_summary_payload(ctx, student_name_hint=student_hint)
            summary = payload.get("summary") if isinstance(payload, dict) else None
            if isinstance(summary, dict):
                message_text = deps.compose_finance_installments_answer(summary) if "parcela" in normalized else deps.compose_finance_aggregate_answer([summary])
                return _build_protected_tool_payload(
                    message_text=message_text,
                    domain="finance",
                    access_tier=_access_tier_for_domain("finance", True),
                    confidence=0.99,
                    reason="specialist_supervisor_tool_first:financial_summary",
                    summary="Resumo financeiro deterministico por aluno.",
                    supports=[MessageEvidenceSupport(kind="finance_summary", label=str(summary.get("student_name") or "Aluno"), detail=f"em aberto {summary.get('open_invoice_count', 0)} · vencidas {summary.get('overdue_invoice_count', 0)}")],
                    graph_leaf="financial_summary",
                    suggested_domain="finance",
                )
            return _build_protected_tool_payload(
                message_text=f"Resumo financeiro de {student_hint}: nao consegui carregar agora os vencimentos e proximos passos detalhados.",
                domain="finance",
                access_tier=_access_tier_for_domain("finance", True),
                confidence=0.9,
                reason="specialist_supervisor_tool_first:financial_summary_scoped_fallback",
                summary="Fallback seguro para resumo financeiro por aluno vinculado.",
                supports=[],
                graph_leaf="financial_summary_scoped_fallback",
                suggested_domain="finance",
            )
        summaries: list[dict[str, Any]] = []
        for student in deps.linked_students(ctx.actor, capability="finance"):
            payload = await deps.fetch_financial_summary_payload(ctx, student_name_hint=str(student.get("full_name") or ""))
            summary = payload.get("summary") if isinstance(payload, dict) else None
            if isinstance(summary, dict):
                summaries.append(summary)
        if summaries:
            return _build_protected_tool_payload(
                message_text=deps.compose_finance_aggregate_answer(summaries),
                domain="finance",
                access_tier=_access_tier_for_domain("finance", True),
                confidence=0.99,
                reason="specialist_supervisor_tool_first:financial_summary_aggregate",
                summary="Resumo financeiro deterministico das contas vinculadas.",
                supports=[
                    MessageEvidenceSupport(
                        kind="finance_summary",
                        label=str(summary.get("student_name") or "Aluno"),
                        detail=f"em aberto {summary.get('open_invoice_count', 0)} · vencidas {summary.get('overdue_invoice_count', 0)}",
                    )
                    for summary in summaries[:4]
                ],
                graph_leaf="financial_summary_aggregate",
                suggested_domain="finance",
            )
        finance_names = [
            str(student.get("full_name") or "").strip()
            for student in deps.linked_students(ctx.actor, capability="finance")
            if str(student.get("full_name") or "").strip()
        ]
        if finance_names:
            return _build_protected_tool_payload(
                message_text=f"Resumo financeiro da familia hoje: {', '.join(finance_names)}. Nao consegui carregar agora os vencimentos e proximos passos detalhados.",
                domain="finance",
                access_tier=_access_tier_for_domain("finance", True),
                confidence=0.9,
                reason="specialist_supervisor_tool_first:financial_summary_aggregate_fallback",
                summary="Fallback seguro para resumo financeiro agregado.",
                supports=[],
                graph_leaf="financial_summary_aggregate_fallback",
                suggested_domain="finance",
            )

    if ctx.request.user.authenticated and (
        "nota" in normalized
        or "notas" in normalized
        or deps.looks_like_academic_risk_followup(ctx.request.message)
        or deps.looks_like_family_academic_aggregate_query(ctx.request.message)
        or str(preview.get("classification", {}).get("domain") or "") == "academic"
    ) and not _looks_like_passing_policy_query(ctx.request.message) and not _looks_like_public_doc_bundle_request(
        ctx.request.message
    ) and not _looks_like_actor_admin_status_query(ctx.request.message) and not any(
        term in normalized for term in {"administrativa", "administrativo", "administrativas", "administrativos", "regularidade"}
    ):
        subject_hint = deps.subject_hint_from_text(ctx.request.message) or (
            memory.active_subject if deps.looks_like_subject_followup(ctx.request.message) else None
        )
        student_hint = deps.resolved_academic_target_name(ctx, resolved=ctx.resolved_turn)
        if deps.needs_specific_academic_student_clarification(ctx, target_name=student_hint, subject_hint=subject_hint):
            return deps.build_academic_student_selection_clarify(
                ctx,
                reason="specialist_supervisor_tool_first:academic_student_clarify",
                graph_path=["specialist_supervisor", "tool_first", "academic_student_clarify"],
            )
        if student_hint:
            payload = await deps.fetch_academic_summary_payload(ctx, student_name_hint=student_hint)
            summary = payload.get("summary") if isinstance(payload, dict) else None
            if isinstance(summary, dict):
                answer_text = (
                    deps.compose_academic_risk_answer(summary)
                    if deps.looks_like_academic_risk_followup(ctx.request.message)
                    else deps.compose_named_subject_grade_answer(summary, subject_hint=subject_hint) or deps.compose_named_grade_answer(summary)
                )
                return _build_protected_tool_payload(
                    message_text=answer_text,
                    domain="academic",
                    access_tier=_access_tier_for_domain("academic", True),
                    confidence=0.99,
                    reason="specialist_supervisor_tool_first:academic_summary",
                    summary="Resumo academico deterministico por aluno.",
                    supports=[MessageEvidenceSupport(kind="academic_summary", label=str(summary.get("student_name") or "Aluno"), detail=deps.safe_excerpt(answer_text, limit=180))],
                    graph_leaf="academic_summary",
                    suggested_domain="academic",
                )
            return _build_protected_tool_payload(
                message_text=f"{student_hint} e o foco desta consulta academica. Nao consegui carregar agora o detalhamento solicitado por disciplina.",
                domain="academic",
                access_tier=_access_tier_for_domain("academic", True),
                confidence=0.9,
                reason="specialist_supervisor_tool_first:academic_summary_scoped_fallback",
                summary="Fallback seguro para resumo academico por aluno vinculado.",
                supports=[],
                graph_leaf="academic_summary_scoped_fallback",
                suggested_domain="academic",
            )
        summaries: list[dict[str, Any]] = []
        for student in deps.linked_students(ctx.actor, capability="academic"):
            payload = await deps.fetch_academic_summary_payload(ctx, student_name_hint=str(student.get("full_name") or ""))
            summary = payload.get("summary") if isinstance(payload, dict) else None
            if isinstance(summary, dict):
                summaries.append(summary)
        if summaries:
            lines = ["Panorama academico das contas vinculadas:"]
            for summary in summaries:
                lines.extend(deps.compose_academic_snapshot_lines(summary))
            return _build_protected_tool_payload(
                message_text="\n".join(lines),
                domain="academic",
                access_tier=_access_tier_for_domain("academic", True),
                confidence=0.98,
                reason="specialist_supervisor_tool_first:academic_summary_aggregate",
                summary="Panorama academico deterministico das contas vinculadas.",
                supports=[
                    MessageEvidenceSupport(kind="academic_summary", label=str(summary.get("student_name") or "Aluno"), detail=deps.safe_excerpt(deps.compose_academic_snapshot_lines(summary)[0], limit=180))
                    for summary in summaries[:4]
                ],
                graph_leaf="academic_summary_aggregate",
                suggested_domain="academic",
            )
        academic_names = [
            str(student.get("full_name") or "").strip()
            for student in deps.linked_students(ctx.actor, capability="academic")
            if str(student.get("full_name") or "").strip()
        ]
        if academic_names:
            return _build_protected_tool_payload(
                message_text=f"Panorama academico das contas vinculadas: {', '.join(academic_names)}. Nao consegui carregar agora o detalhamento objetivo por disciplina.",
                domain="academic",
                access_tier=_access_tier_for_domain("academic", True),
                confidence=0.9,
                reason="specialist_supervisor_tool_first:academic_summary_aggregate_fallback",
                summary="Fallback seguro para panorama academico agregado.",
                supports=[],
                graph_leaf="academic_summary_aggregate_fallback",
                suggested_domain="academic",
            )

    if ctx.request.user.authenticated and "documentacao" in normalized and any(
        term in normalized for term in {"financeiro", "bloque", "boleto", "mensalidade", "fatura"}
    ):
        admin_lines: list[str] = []
        actor_admin_payload = await deps.http_get(
            ctx.http_client,
            base_url=ctx.settings.api_core_url,
            path="/v1/actors/me/administrative-status",
            token=ctx.settings.internal_api_token,
            params={"telegram_chat_id": ctx.request.telegram_chat_id},
        )
        actor_admin_summary = actor_admin_payload.get("summary") if isinstance(actor_admin_payload, dict) else None
        if isinstance(actor_admin_summary, dict):
            admin_lines = [line for line in deps.compose_actor_admin_status_answer(actor_admin_summary).splitlines() if line.strip()]
        if not admin_lines:
            admin_student = deps.recent_student_from_context_with_memory(
                ctx.actor,
                ctx.conversation_context,
                operational_memory=ctx.operational_memory,
            )
            if isinstance(admin_student, dict):
                payload = await deps.http_get(
                    ctx.http_client,
                    base_url=ctx.settings.api_core_url,
                    path=f"/v1/students/{admin_student['student_id']}/administrative-status",
                    token=ctx.settings.internal_api_token,
                    params={"telegram_chat_id": ctx.request.telegram_chat_id},
                )
                summary = payload.get("summary") if isinstance(payload, dict) else None
                if isinstance(summary, dict):
                    admin_lines = [line for line in deps.compose_admin_status_answer(summary).splitlines() if line.strip()]
        finance_summaries: list[dict[str, Any]] = []
        for student in deps.linked_students(ctx.actor, capability="finance"):
            payload = await deps.http_get(
                ctx.http_client,
                base_url=ctx.settings.api_core_url,
                path=f"/v1/students/{student['student_id']}/financial-summary",
                token=ctx.settings.internal_api_token,
                params={"telegram_chat_id": ctx.request.telegram_chat_id},
            )
            summary = payload.get("summary") if isinstance(payload, dict) else None
            if isinstance(summary, dict):
                finance_summaries.append(summary)
        if admin_lines or finance_summaries:
            lines: list[str] = []
            if admin_lines:
                lines.extend(admin_lines)
            if finance_summaries:
                if lines:
                    lines.append("")
                lines.append("Financeiro:")
                for summary in finance_summaries:
                    student_name = str(summary.get("student_name") or "Aluno").strip()
                    open_count = int(summary.get("open_invoice_count", 0) or 0)
                    overdue_count = int(summary.get("overdue_invoice_count", 0) or 0)
                    lines.append(f"- {student_name}: {open_count} fatura(s) em aberto e {overdue_count} vencida(s).")
                if all(
                    int(summary.get("open_invoice_count", 0) or 0) == 0 and int(summary.get("overdue_invoice_count", 0) or 0) == 0
                    for summary in finance_summaries
                ):
                    lines.append("No momento, eu nao encontrei bloqueio financeiro de atendimento nas contas vinculadas.")
            return _build_protected_tool_payload(
                message_text="\n".join(lines),
                domain="finance",
                access_tier=_access_tier_for_domain("finance", True),
                confidence=0.98,
                reason="specialist_supervisor_tool_first:admin_finance_overview",
                summary="Panorama combinado de documentacao e financeiro das contas vinculadas.",
                supports=[
                    MessageEvidenceSupport(kind="administrative_status", label="Documentacao", detail="status administrativo consolidado"),
                    MessageEvidenceSupport(kind="finance_summary", label="Financeiro", detail="contas vinculadas agregadas"),
                ],
                graph_leaf="admin_finance_overview",
                suggested_domain="finance",
            )

    actor_admin_student_hint = deps.student_hint_from_message(ctx.actor, ctx.request.message)
    if ctx.request.user.authenticated and _looks_like_actor_admin_status_query(ctx.request.message) and not actor_admin_student_hint:
        try:
            actor_admin_payload = await deps.http_get(
                ctx.http_client,
                base_url=ctx.settings.api_core_url,
                path="/v1/actors/me/administrative-status",
                token=ctx.settings.internal_api_token,
                params={"telegram_chat_id": ctx.request.telegram_chat_id},
            )
        except Exception:
            actor_admin_payload = None
        actor_admin_summary = actor_admin_payload.get("summary") if isinstance(actor_admin_payload, dict) else None
        if isinstance(actor_admin_summary, dict):
            return _build_protected_tool_payload(
                message_text=deps.compose_actor_admin_status_answer(actor_admin_summary),
                domain="institution",
                access_tier=_access_tier_for_domain("institution", True),
                confidence=0.99,
                reason="specialist_supervisor_tool_first:actor_admin_status",
                summary="Status administrativo deterministico do cadastro autenticado.",
                supports=[
                    MessageEvidenceSupport(kind="administrative_status", label="Cadastro autenticado", detail=str(actor_admin_summary.get("overall_status") or "em analise")),
                ],
                graph_leaf="actor_admin_status",
                suggested_domain="institution",
            )

    if ctx.request.user.authenticated and any(
        term in normalized for term in {"documentacao", "documentação", "documental", "documentais", "cadastro", "cadastral", "administrativo", "administrativa", "parte administrativa"}
    ):
        student_hint = deps.student_hint_from_message(ctx.actor, ctx.request.message)
        student = deps.find_student_by_hint(ctx.actor, capability="academic", hint=student_hint) or deps.recent_student_from_context_with_memory(
            ctx.actor,
            ctx.conversation_context,
            operational_memory=ctx.operational_memory,
        )
        if isinstance(student, dict):
            payload = await deps.http_get(
                ctx.http_client,
                base_url=ctx.settings.api_core_url,
                path=f"/v1/students/{student['student_id']}/administrative-status",
                token=ctx.settings.internal_api_token,
                params={"telegram_chat_id": ctx.request.telegram_chat_id},
            )
            summary = payload.get("summary") if isinstance(payload, dict) else None
            if isinstance(summary, dict):
                return _build_protected_tool_payload(
                    message_text=deps.compose_admin_status_answer(summary),
                    domain="academic",
                    access_tier=_access_tier_for_domain("academic", True),
                    confidence=0.99,
                    reason="specialist_supervisor_tool_first:administrative_status",
                    summary="Status administrativo deterministico do aluno vinculado.",
                    supports=[
                        MessageEvidenceSupport(kind="administrative_status", label=str(summary.get("student_name") or "Aluno"), detail=str(summary.get("overall_status") or "")),
                    ],
                    graph_leaf="administrative_status",
                    suggested_domain="academic",
                )
            student_name = str(student.get("full_name") or "o aluno").strip() or "o aluno"
            return _build_protected_tool_payload(
                message_text=(
                    f"Hoje {student_name} ainda aparece com pendencias administrativas. "
                    "Nao consegui abrir o detalhamento completo agora, mas o proximo passo seguro continua sendo "
                    "seguir pelo portal autenticado ou pela secretaria escolar."
                ),
                domain="academic",
                access_tier=_access_tier_for_domain("academic", True),
                confidence=0.9,
                reason="specialist_supervisor_tool_first:administrative_status_scoped_fallback",
                summary="Fallback seguro para status administrativo por aluno vinculado.",
                supports=[],
                graph_leaf="administrative_status_scoped_fallback",
                suggested_domain="academic",
            )

    return None
