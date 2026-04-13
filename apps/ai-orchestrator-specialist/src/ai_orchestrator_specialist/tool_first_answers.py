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
from .public_profile_answers import (
    _compose_attendance_policy_answer,
    _compose_passing_policy_answer,
    _compose_project_of_life_answer,
    _compose_timeline_bundle_answer,
)
from .public_query_patterns import (
    _looks_like_attendance_policy_query,
    _looks_like_passing_policy_query,
    _looks_like_project_of_life_query,
    _looks_like_public_doc_bundle_request,
)
from .support_workflow_helpers import (
    _build_support_handoff_summary,
    _compose_support_handoff_answer,
    _detect_support_handoff_queue,
    _looks_like_human_handoff_request,
)
from .tool_first_public_answers import (
    ToolFirstPublicDeps,
    maybe_tool_first_public_answer,
)
from .tool_first_protected_answers import (
    ToolFirstProtectedDeps,
    maybe_tool_first_protected_answer,
)
from .tool_first_workflows import (
    ToolFirstWorkflowDeps,
    maybe_tool_first_workflow_answer,
)


@dataclass(frozen=True)
class ToolFirstStructuredDeps:
    normalize_text: Callable[[str | None], str]
    effective_multi_intent_domains: Callable[[Any, str], list[str]]
    create_support_handoff_payload: Callable[..., Awaitable[dict[str, Any]]]
    maybe_restricted_document_tool_first_answer: Callable[..., Awaitable[SupervisorAnswerPayload | None]]
    public_deps: ToolFirstPublicDeps
    workflow_deps: ToolFirstWorkflowDeps
    protected_deps: ToolFirstProtectedDeps
    student_hint_from_message: Callable[..., str | None]
    is_student_name_only_followup: Callable[..., str | None]
    fetch_academic_summary_payload: Callable[..., Awaitable[dict[str, Any] | None]]
    fetch_financial_summary_payload: Callable[..., Awaitable[dict[str, Any] | None]]
    build_academic_finance_combo_payload: Callable[..., SupervisorAnswerPayload]
    safe_excerpt: Callable[..., str | None]
    fetch_public_payload: Callable[..., Awaitable[dict[str, Any] | None]]
    format_brl: Callable[[Any], str]


def _should_prioritize_protected_before_public(
    ctx: Any,
    *,
    preview: dict[str, Any],
    deps: ToolFirstStructuredDeps,
) -> bool:
    if not bool(getattr(ctx.request.user, "authenticated", False)):
        return False
    turn_frame = preview.get("turn_frame") if isinstance(preview.get("turn_frame"), dict) else {}
    capability_id = str(turn_frame.get("capability_id") or "").strip()
    if capability_id.startswith("protected."):
        return True
    message = ctx.request.message
    protected_deps = deps.protected_deps
    return any(
        (
            protected_deps.looks_like_admin_finance_combo_query(message),
            protected_deps.looks_like_family_finance_aggregate_query(message),
            protected_deps.looks_like_family_academic_aggregate_query(message),
            protected_deps.looks_like_family_attendance_aggregate_query(message),
        )
    )


def _build_tool_first_payload(
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
        graph_path=["specialist_supervisor", "tool_first", graph_leaf],
        reason=reason,
    )


async def maybe_tool_first_structured_answer(
    ctx: Any,
    *,
    deps: ToolFirstStructuredDeps,
) -> SupervisorAnswerPayload | None:
    normalized = deps.normalize_text(ctx.request.message)
    profile = ctx.school_profile if isinstance(ctx.school_profile, dict) else {}
    preview = ctx.preview_hint if isinstance(ctx.preview_hint, dict) else {}
    preview_mode = str(preview.get("mode") or "").strip()
    memory = ctx.operational_memory or OperationalMemory()
    multi_domains = deps.effective_multi_intent_domains(memory, ctx.request.message)

    restricted_doc_answer = await deps.maybe_restricted_document_tool_first_answer(ctx, profile=profile)
    if restricted_doc_answer is not None:
        return restricted_doc_answer

    if ctx.request.allow_handoff and _looks_like_human_handoff_request(ctx.request.message):
        queue_name = _detect_support_handoff_queue(ctx)
        payload = await deps.create_support_handoff_payload(
            ctx,
            queue_name=queue_name,
            summary=_build_support_handoff_summary(ctx, queue_name=queue_name),
        )
        item = payload.get("item") if isinstance(payload, dict) else None
        if isinstance(item, dict):
            protocol = str(item.get("ticket_code") or item.get("protocol_code") or item.get("linked_ticket_code") or "indisponivel").strip()
            status = str(item.get("status") or "queued").strip()
            queue_label = str(item.get("queue_name") or queue_name or "atendimento").strip()
            return SupervisorAnswerPayload(
                message_text=_compose_support_handoff_answer(payload, profile=profile, queue_name=queue_label),
                mode="handoff",
                classification=MessageIntentClassification(
                    domain="support",
                    access_tier=_access_tier_for_domain("support", ctx.request.user.authenticated),
                    confidence=0.99,
                    reason="specialist_supervisor_tool_first:human_handoff",
                ),
                evidence_pack=MessageEvidencePack(
                    strategy="workflow_status",
                    summary="Encaminhamento humano real com protocolo e fila operacional.",
                    source_count=1,
                    support_count=2,
                    supports=[
                        MessageEvidenceSupport(kind="workflow", label="Fila humana", detail=f"{queue_label} · {status}"),
                        MessageEvidenceSupport(kind="workflow", label="Protocolo", detail=protocol),
                    ],
                ),
                suggested_replies=_default_suggested_replies("support"),
                graph_path=["specialist_supervisor", "tool_first", "human_handoff"],
                reason="specialist_supervisor_tool_first:human_handoff",
            )

    if _should_prioritize_protected_before_public(ctx, preview=preview, deps=deps):
        protected_tool_answer = await maybe_tool_first_protected_answer(
            ctx,
            normalized=normalized,
            preview=preview,
            memory=memory,
            deps=deps.protected_deps,
        )
        if protected_tool_answer is not None:
            return protected_tool_answer

    public_tool_answer = await maybe_tool_first_public_answer(
        ctx,
        normalized=normalized,
        profile=profile,
        deps=deps.public_deps,
    )
    if public_tool_answer is not None:
        return public_tool_answer

    if (
        ctx.request.user.authenticated
        and not _looks_like_public_doc_bundle_request(ctx.request.message)
        and len(multi_domains) >= 2
        and "academic" in multi_domains
        and "finance" in multi_domains
    ):
        target_name = (
            deps.student_hint_from_message(ctx.actor, ctx.request.message)
            or deps.is_student_name_only_followup(ctx.actor, ctx.request.message)
            or memory.active_student_name
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
                    reason="specialist_supervisor_tool_first:academic_finance_combo",
                    graph_path=["specialist_supervisor", "tool_first", "academic_finance_combo"],
                )

    if profile and _looks_like_project_of_life_query(ctx.request.message):
        answer_text = _compose_project_of_life_answer(profile)
        if answer_text:
            return _build_tool_first_payload(
                message_text=answer_text,
                domain="institution",
                access_tier=_access_tier_for_domain("institution", ctx.request.user.authenticated),
                confidence=0.99,
                reason="specialist_supervisor_tool_first:project_of_life_policy",
                summary="Resposta deterministica baseada na politica academica publica da escola.",
                supports=[
                    MessageEvidenceSupport(kind="policy", label="Projeto de vida", detail=deps.safe_excerpt(answer_text, limit=180)),
                ],
                graph_leaf="project_of_life_policy",
                suggested_domain="institution",
            )

    if profile and _looks_like_attendance_policy_query(ctx.request.message):
        answer_text = _compose_attendance_policy_answer(profile, message=ctx.request.message)
        if answer_text:
            return _build_tool_first_payload(
                message_text=answer_text,
                domain="academic",
                access_tier=_access_tier_for_domain("academic", ctx.request.user.authenticated),
                confidence=0.99,
                reason="specialist_supervisor_tool_first:attendance_policy",
                summary="Resposta deterministica baseada na politica publica de frequencia.",
                supports=[
                    MessageEvidenceSupport(kind="policy", label="Politica de frequencia", detail=deps.safe_excerpt(answer_text, limit=180)),
                ],
                graph_leaf="attendance_policy",
                suggested_domain="academic",
            )

    if profile and _looks_like_passing_policy_query(ctx.request.message):
        answer_text = _compose_passing_policy_answer(profile, authenticated=ctx.request.user.authenticated)
        if answer_text:
            return _build_tool_first_payload(
                message_text=answer_text,
                domain="academic",
                access_tier=_access_tier_for_domain("academic", ctx.request.user.authenticated),
                confidence=0.99,
                reason="specialist_supervisor_tool_first:passing_policy",
                summary="Resposta deterministica baseada na politica publica de aprovacao.",
                supports=[
                    MessageEvidenceSupport(kind="policy", label="Meta de aprovacao", detail="media publica 7,0/10"),
                ],
                graph_leaf="passing_policy",
                suggested_domain="academic",
            )

    if profile and (
        "mandar documentos" in normalized
        or "enviar documentos" in normalized
        or ("canais" in normalized and "documentos" in normalized)
        or ("prazos" in normalized and "secretaria" in normalized and ("documentos" in normalized or "declaracoes" in normalized or "atualizacoes cadastrais" in normalized))
    ):
        policy = profile.get("document_submission_policy")
        if isinstance(policy, dict):
            channels = policy.get("accepted_channels") if isinstance(policy.get("accepted_channels"), list) else []
            rendered_channels = ", ".join(str(item).strip() for item in channels if str(item).strip())
            warning = str(policy.get("warning") or "").strip()
            notes = str(policy.get("notes") or "").strip()
            service_catalog = profile.get("service_catalog")
            secretaria_eta = ""
            if isinstance(service_catalog, list):
                secretaria_entry = next(
                    (
                        item
                        for item in service_catalog
                        if isinstance(item, dict) and str(item.get("service_key") or "").strip() == "secretaria_escolar"
                    ),
                    None,
                )
                if isinstance(secretaria_entry, dict):
                    secretaria_eta = str(secretaria_entry.get("typical_eta") or "").strip()
            return _build_tool_first_payload(
                message_text=(
                    "Voce pode mandar documentos pelo portal institucional, pelo email da secretaria "
                    "ou levar na secretaria presencial para conferencia final. "
                    + (f"Prazo esperado da secretaria: {secretaria_eta}. " if secretaria_eta else "")
                    + f"{notes} {warning}"
                ).strip(),
                domain="institution",
                access_tier="public",
                confidence=0.99,
                reason="specialist_supervisor_tool_first:document_submission_policy",
                summary="Resposta deterministica baseada na politica publica de envio documental.",
                supports=[
                    MessageEvidenceSupport(kind="policy", label="Canais aceitos", detail=rendered_channels),
                    MessageEvidenceSupport(kind="policy", label="Observacao", detail=deps.safe_excerpt(warning or notes)),
                ],
                graph_leaf="document_submission_policy",
                suggested_domain="institution",
            )

    timeline_query = (
        any(term in normalized for term in {"matricula de 2026", "matrícula de 2026", "abre a matricula", "abre a matrícula"})
        or any(
            term in normalized
            for term in {
                "quando comecam as aulas",
                "quando começam as aulas",
                "comeco das aulas",
                "começo das aulas",
                "inicio das aulas",
                "início das aulas",
                "quando comeca o ano letivo",
                "quando começa o ano letivo",
                "inicio do ano letivo",
                "início do ano letivo",
            }
        )
        or (
            any(term in normalized for term in {"ordene", "ordem", "sequencia", "sequência"})
            and "matricula" in normalized
            and any(term in normalized for term in {"aulas", "ano letivo"})
        )
    )
    if timeline_query:
        timeline_payload = await deps.fetch_public_payload(ctx, "/v1/public/timeline", "timeline")
        entries = timeline_payload.get("entries") if isinstance(timeline_payload, dict) else None
        if isinstance(entries, list):
            combined_answer = _compose_timeline_bundle_answer({"public_timeline": entries}, ctx.request.message)
            if combined_answer:
                return _build_tool_first_payload(
                    message_text=combined_answer,
                    domain="calendar",
                    access_tier="public",
                    confidence=0.99,
                    reason="specialist_supervisor_tool_first:public_timeline_bundle",
                    summary="Resposta deterministica combinando matricula e inicio das aulas.",
                    supports=[
                        MessageEvidenceSupport(kind="timeline", label="Linha do tempo publica", detail=deps.safe_excerpt(combined_answer)),
                    ],
                    graph_leaf="public_timeline_bundle",
                    suggested_domain="institution",
                )
            topic_fragment = "admissions_opening" if any(term in normalized for term in {"matricula", "matrícula"}) else "school_year_start"
            item = deps.public_deps.timeline_entry(entries, topic_fragment=topic_fragment)
            if isinstance(item, dict):
                summary = str(item.get("summary") or "").strip()
                notes = str(item.get("notes") or "").strip()
                answer_text = f"{summary} {notes}".strip()
                return _build_tool_first_payload(
                    message_text=answer_text,
                    domain="calendar",
                    access_tier="public",
                    confidence=0.99,
                    reason="specialist_supervisor_tool_first:public_timeline",
                    summary="Resposta deterministica baseada na timeline publica institucional.",
                    supports=[
                        MessageEvidenceSupport(kind="timeline", label=str(item.get("title") or "Timeline"), detail=deps.safe_excerpt(answer_text)),
                    ],
                    graph_leaf="public_timeline",
                    suggested_domain="institution",
                )

    if profile and "mensalidade" in normalized and "ensino medio" in normalized:
        rows = profile.get("tuition_reference")
        if isinstance(rows, list):
            chosen = next(
                (row for row in rows if isinstance(row, dict) and "ensino medio" in deps.normalize_text(row.get("segment"))),
                None,
            )
            if isinstance(chosen, dict):
                monthly = deps.format_brl(chosen.get("monthly_amount"))
                enrollment = deps.format_brl(chosen.get("enrollment_fee"))
                notes = str(chosen.get("notes") or "").strip()
                return _build_tool_first_payload(
                    message_text=(
                        f"Para Ensino Medio no turno {chosen.get('shift_label', 'Manha')}, a mensalidade publica de referencia em 2026 "
                        f"e {monthly} e a taxa de matricula e {enrollment}. {notes}"
                    ).strip(),
                    domain="finance",
                    access_tier="public",
                    confidence=0.99,
                    reason="specialist_supervisor_tool_first:public_pricing_reference",
                    summary="Resposta deterministica baseada na tabela publica de valores.",
                    supports=[
                        MessageEvidenceSupport(
                            kind="pricing_reference",
                            label=str(chosen.get("segment") or "Tabela publica"),
                            detail=f"mensalidade {monthly} · matricula {enrollment}",
                        ),
                    ],
                    graph_leaf="public_pricing_reference",
                    suggested_domain="finance",
                )

    workflow_answer = await maybe_tool_first_workflow_answer(
        ctx,
        normalized=normalized,
        profile=profile,
        preview_mode=preview_mode,
        memory=memory,
        deps=deps.workflow_deps,
    )
    if workflow_answer is not None:
        return workflow_answer

    protected_tool_answer = await maybe_tool_first_protected_answer(
        ctx,
        normalized=normalized,
        preview=preview,
        memory=memory,
        deps=deps.protected_deps,
    )
    if protected_tool_answer is not None:
        return protected_tool_answer

    return None
