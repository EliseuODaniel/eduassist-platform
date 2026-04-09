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
from .public_profile_answers import (
    _extract_requested_visit_date_iso,
    _extract_requested_visit_window,
    _weekday_label_from_iso,
)
from .support_workflow_helpers import (
    _compose_support_status_answer,
    _compose_visit_status_answer,
)


@dataclass(frozen=True)
class ToolFirstWorkflowDeps:
    http_post: Callable[..., Awaitable[dict[str, Any] | None]]
    strip_none: Callable[[dict[str, Any]], dict[str, Any]]
    effective_conversation_id: Callable[[Any], str]
    create_institutional_request_payload: Callable[..., Awaitable[dict[str, Any]]]
    create_visit_booking_payload: Callable[..., Awaitable[dict[str, Any]]]
    workflow_status_payload: Callable[..., Awaitable[dict[str, Any]]]


def _build_workflow_payload(
    *,
    message_text: str,
    domain: str,
    access_tier: str,
    confidence: float,
    reason: str,
    summary: str,
    supports: list[MessageEvidenceSupport],
    graph_leaf: str,
    mode: str = "structured_tool",
) -> SupervisorAnswerPayload:
    strategy = "workflow_status"
    return SupervisorAnswerPayload(
        message_text=message_text,
        mode=mode,
        classification=MessageIntentClassification(
            domain=domain,
            access_tier=access_tier,
            confidence=confidence,
            reason=reason,
        ),
        evidence_pack=MessageEvidencePack(
            strategy=strategy,
            summary=summary,
            source_count=max(len(supports), 1),
            support_count=len(supports),
            supports=supports,
        ),
        suggested_replies=_default_suggested_replies("support"),
        graph_path=["specialist_supervisor", "tool_first", graph_leaf],
        reason=reason,
    )


async def maybe_tool_first_workflow_answer(
    ctx: Any,
    *,
    normalized: str,
    profile: dict[str, Any],
    preview_mode: str,
    memory: Any,
    deps: ToolFirstWorkflowDeps,
) -> SupervisorAnswerPayload | None:
    support_access_tier = _access_tier_for_domain("support", ctx.request.user.authenticated)

    if any(term in normalized for term in {"falar com o financeiro", "quero falar com o financeiro", "setor financeiro"}):
        payload = await deps.create_institutional_request_payload(ctx, target_area="financeiro")
        item = payload.get("item") if isinstance(payload, dict) else None
        if isinstance(item, dict):
            protocol = str(item.get("protocol_code") or "indisponivel").strip()
            queue_name = str(item.get("queue_name") or "financeiro").strip()
            ticket = str(item.get("linked_ticket_code") or "").strip()
            return _build_workflow_payload(
                message_text=(
                    f"Acionei o financeiro para voce. Protocolo: {protocol}. "
                    f"Fila responsavel: {queue_name}. "
                    f"{f'Ticket operacional: {ticket}. ' if ticket else ''}"
                    "Se quiser, eu tambem posso acompanhar o status deste atendimento."
                ),
                domain="support",
                access_tier=support_access_tier,
                confidence=0.99,
                reason="specialist_supervisor_tool_first:support_handoff",
                summary="Handoff deterministico para fila de atendimento.",
                supports=[
                    MessageEvidenceSupport(kind="workflow", label="Atendimento financeiro", detail=f"protocolo {protocol} · fila {queue_name}"),
                ],
                graph_leaf="support_handoff",
                mode="handoff",
            )

    support_status_requested = any(
        term in normalized
        for term in {
            "esse atendimento",
            "status do atendimento",
            "como esta esse atendimento",
            "qual o status do protocolo",
            "qual o status",
            "status atual",
            "meu protocolo",
        }
    )
    support_context_active = (
        memory.active_domain == "support"
        or "support" in memory.active_domains
        or preview_mode == "handoff"
        or any(term in normalized for term in {"atendimento", "atendente", "fila", "humano", "secretaria", "financeiro"})
    )
    if support_status_requested and support_context_active:
        payload = await deps.workflow_status_payload(ctx, workflow_kind="support_handoff")
        item = payload.get("item") if isinstance(payload, dict) else None
        if isinstance(item, dict):
            return _build_workflow_payload(
                message_text=_compose_support_status_answer(item),
                domain="support",
                access_tier=support_access_tier,
                confidence=0.98,
                reason="specialist_supervisor_tool_first:support_status",
                summary="Status deterministico do atendimento institucional.",
                supports=[
                    MessageEvidenceSupport(
                        kind="workflow",
                        label=str(item.get("protocol_code") or "protocolo"),
                        detail=f"{item.get('status')} · {item.get('queue_name')}",
                    ),
                ],
                graph_leaf="support_status",
            )

    visit_reschedule_hint = any(
        term in normalized
        for term in {
            "remarcar",
            "remarco",
            "reagendar",
            "trocar horario",
            "trocar o horario",
            "mudar horario",
            "mudar o horario",
            "se eu precisar remarcar",
            "por onde remarco",
        }
    )
    visit_followup_hint = visit_reschedule_hint or any(
        term in normalized for term in {"pode ser", "quinta", "terça", "terca", "quarta", "sexta", "sabado", "sábado", "manha", "tarde", "noite"}
    )
    if visit_followup_hint:
        payload = await deps.workflow_status_payload(ctx, workflow_kind="visit_booking")
        item = payload.get("item") if isinstance(payload, dict) else None
        if isinstance(item, dict):
            preferred_date = _extract_requested_visit_date_iso(ctx.request.message)
            preferred_window = _extract_requested_visit_window(profile, ctx.request.message)
            if preferred_date or preferred_window:
                updated = await deps.http_post(
                    ctx.http_client,
                    base_url=ctx.settings.api_core_url,
                    path="/v1/internal/workflows/visit-bookings/actions",
                    token=ctx.settings.internal_api_token,
                    payload=deps.strip_none(
                        {
                            "conversation_external_id": deps.effective_conversation_id(ctx.request),
                            "channel": ctx.request.channel.value,
                            "telegram_chat_id": ctx.request.telegram_chat_id,
                            "protocol_code": str(item.get("protocol_code") or "").strip() or None,
                            "action": "reschedule",
                            "preferred_date": preferred_date,
                            "preferred_window": preferred_window,
                            "notes": ctx.request.message,
                        }
                    ),
                )
                updated_item = updated.get("item") if isinstance(updated, dict) else None
                if isinstance(updated_item, dict):
                    protocol = str(updated_item.get("protocol_code") or item.get("protocol_code") or "indisponivel").strip()
                    weekday_label = _weekday_label_from_iso(preferred_date) or "quinta-feira"
                    window_label = preferred_window or str(updated_item.get("preferred_window") or "14:30")
                    return _build_workflow_payload(
                        message_text=(
                            f"Pedido de visita atualizado. Protocolo: {protocol}. "
                            f"Nova preferencia: {weekday_label}, {window_label}. "
                            "Admissions valida a nova janela e retorna com a confirmacao."
                        ),
                        domain="support",
                        access_tier=support_access_tier,
                        confidence=0.99,
                        reason="specialist_supervisor_tool_first:visit_reschedule",
                        summary="Atualizacao deterministica da visita a partir do contexto recente.",
                        supports=[
                            MessageEvidenceSupport(kind="workflow", label="Visita atualizada", detail=f"protocolo {protocol} · {weekday_label}, {window_label}"),
                        ],
                        graph_leaf="visit_reschedule",
                    )

    if any(term in normalized for term in {"cancela", "cancelar", "cancelamento"}):
        payload = await deps.workflow_status_payload(ctx, workflow_kind="visit_booking")
        item = payload.get("item") if isinstance(payload, dict) else None
        if isinstance(item, dict):
            cancelled = await deps.http_post(
                ctx.http_client,
                base_url=ctx.settings.api_core_url,
                path="/v1/internal/workflows/visit-bookings/actions",
                token=ctx.settings.internal_api_token,
                payload=deps.strip_none(
                    {
                        "conversation_external_id": deps.effective_conversation_id(ctx.request),
                        "channel": ctx.request.channel.value,
                        "telegram_chat_id": ctx.request.telegram_chat_id,
                        "protocol_code": str(item.get("protocol_code") or "").strip() or None,
                        "action": "cancel",
                        "notes": ctx.request.message,
                    }
                ),
            )
            cancelled_item = cancelled.get("item") if isinstance(cancelled, dict) else None
            if isinstance(cancelled_item, dict):
                protocol = str(cancelled_item.get("protocol_code") or item.get("protocol_code") or "indisponivel").strip()
                return _build_workflow_payload(
                    message_text=(
                        f"Pedido de visita cancelado. Protocolo: {protocol}. "
                        "Se quiser, eu posso abrir um novo agendamento com outra data."
                    ),
                    domain="support",
                    access_tier=support_access_tier,
                    confidence=0.99,
                    reason="specialist_supervisor_tool_first:visit_cancel",
                    summary="Cancelamento deterministico do pedido de visita a partir do contexto recente.",
                    supports=[MessageEvidenceSupport(kind="workflow", label=protocol or "protocolo", detail="visita cancelada")],
                    graph_leaf="visit_cancel",
                )

    if "visita" in normalized and any(term in normalized for term in {"protocolo", "status", "andamento"}):
        payload = await deps.workflow_status_payload(ctx, workflow_kind="visit_booking")
        item = payload.get("item") if isinstance(payload, dict) else None
        if isinstance(item, dict):
            protocol = str(item.get("protocol_code") or "indisponivel").strip()
            slot = str(item.get("slot_label") or item.get("preferred_window") or "janela a confirmar").strip()
            return _build_workflow_payload(
                message_text=_compose_visit_status_answer(item),
                domain="support",
                access_tier=support_access_tier,
                confidence=0.99,
                reason="specialist_supervisor_tool_first:visit_status",
                summary="Consulta deterministica ao status do fluxo de visita.",
                supports=[MessageEvidenceSupport(kind="workflow", label=protocol or "protocolo", detail=slot)],
                graph_leaf="visit_status",
            )

    if any(term in normalized for term in {"visita", "visitar", "tour"}) and any(term in normalized for term in {"agendar", "marcar", "visitar", "conhecer"}):
        payload = await deps.create_visit_booking_payload(ctx)
        item = payload.get("item") if isinstance(payload, dict) else None
        if isinstance(item, dict):
            protocol = str(item.get("protocol_code") or "indisponivel").strip()
            ticket = str(item.get("linked_ticket_code") or "").strip()
            slot = str(item.get("slot_label") or item.get("preferred_window") or "janela a confirmar").strip()
            return _build_workflow_payload(
                message_text=(
                    f"Pedido de visita registrado. Protocolo: {protocol}. "
                    f"Preferencia registrada: {slot}. "
                    f"{f'Ticket operacional: {ticket}. ' if ticket else ''}"
                    "Se quiser, eu tambem posso acompanhar o status ou remarcar a visita."
                ),
                domain="support",
                access_tier=support_access_tier,
                confidence=0.99,
                reason="specialist_supervisor_tool_first:visit_booking",
                summary="Registro deterministico do pedido de visita.",
                supports=[MessageEvidenceSupport(kind="workflow", label="Pedido de visita", detail=f"protocolo {protocol} · {slot}")],
                graph_leaf="visit_booking",
            )

    if visit_reschedule_hint:
        payload = await deps.workflow_status_payload(ctx, workflow_kind="visit_booking")
        item = payload.get("item") if isinstance(payload, dict) else None
        if isinstance(item, dict):
            return _build_workflow_payload(
                message_text=_compose_visit_status_answer(item, guidance_only=True),
                domain="support",
                access_tier=support_access_tier,
                confidence=0.98,
                reason="specialist_supervisor_tool_first:visit_reschedule_guidance",
                summary="Orientacao deterministica para remarcacao da visita.",
                supports=[
                    MessageEvidenceSupport(
                        kind="workflow",
                        label=str(item.get("protocol_code") or "protocolo"),
                        detail=str(item.get("slot_label") or item.get("preferred_window") or ""),
                    ),
                ],
                graph_leaf="visit_reschedule_guidance",
            )

    return None
