from __future__ import annotations

import re
from typing import Any

from .public_profile_answers import _compose_human_handoff_answer, _select_contact_channel


def _normalize_text(value: str | None) -> str:
    return re.sub(r"\s+", " ", str(value or "").strip().lower())


def _looks_like_human_handoff_request(message: str) -> bool:
    normalized = _normalize_text(message)
    if any(
        marker in normalized
        for marker in (
            "qual a diferenca entre",
            "qual a diferença entre",
            "explique a diferenca entre",
            "explique a diferença entre",
            "compare",
            "como se complementam",
            "o que muda entre",
            "quem faz o que",
        )
    ):
        return False
    if any(
        marker in normalized
        for marker in (
            "bloqueando atendimento",
            "bloqueia atendimento",
            "bloqueio de atendimento",
            "ha bloqueio de atendimento",
            "há bloqueio de atendimento",
            "se ha bloqueio de atendimento",
            "se há bloqueio de atendimento",
        )
    ):
        return False
    if any(term in normalized for term in ("playbook interno", "manual interno", "protocolo interno", "documento interno", "material interno")):
        return False
    queue_signals = (
        "financeir",
        "secretari",
        "direc",
        "coordena",
        "orienta",
        "matricul",
        "admiss",
        "document",
    )
    direct_markers = (
        "atendente humano",
        "atendimento humano",
        "quero falar com humano",
        "quero falar com um humano",
        "preciso falar com um humano",
        "preciso falar com humano",
        "quero falar com o financeiro",
        "quero falar com a secretaria",
        "quero falar com a direção",
        "quero falar com a direcao",
        "quero falar com a coordenação",
        "quero falar com a coordenacao",
        "quero falar com a orientação",
        "quero falar com a orientacao",
        "quero falar com admissions",
        "quero falar com atendimento",
        "quero um atendente",
        "quero secretaria",
        "quero financeiro",
        "quero direcao",
        "quero direção",
        "preciso de secretaria",
        "preciso de financeiro",
        "abre um atendimento",
        "abre um chamado",
        "abre um protocolo",
        "me encaminha",
        "me encaminhe",
        "encaminha pra",
        "encaminha para",
        "encaminhe pra",
        "encaminhe para",
    )
    if any(marker in normalized for marker in direct_markers):
        return True
    if any(signal in normalized for signal in queue_signals) and any(
        marker in normalized
        for marker in (
            "falar",
            "encaminha",
            "encaminhe",
            "atendimento",
            "atendente",
            "chamado",
            "abrir",
            "abre",
        )
    ):
        return True
    return False


def _detect_support_handoff_queue(ctx: Any) -> str:
    normalized = _normalize_text(ctx.request.message)
    registry = ctx.specialist_registry or {}

    def _queue_from_specialist(specialist_id: str) -> str | None:
        spec = registry.get(specialist_id)
        if spec is None or not getattr(spec, "handoff_enabled", False):
            return None
        queue_name = str(getattr(spec, "handoff_queue", "") or "").strip()
        return queue_name or None

    if any(term in normalized for term in {"financeir", "mensalidad", "boleto", "fatura", "segunda via"}):
        return "financeiro"
    if any(term in normalized for term in {"coordena", "nota", "falt", "boletim", "professor", "disciplina"}):
        return "coordenacao"
    if any(term in normalized for term in {"orienta", "bullying", "emocional", "convivencia", "comportamento"}):
        return "orientacao"
    if any(term in normalized for term in {"direc", "direção", "ouvidoria"}):
        return "direcao"
    if any(term in normalized for term in {"matricul", "visita", "admiss", "vaga"}):
        return "admissoes"
    if any(
        term in normalized
        for term in {"secretari", "document", "declaracao", "declaração", "historico", "histórico"}
    ):
        return "secretaria"
    if ctx.operational_memory is not None:
        if "finance" in ctx.operational_memory.active_domains or ctx.operational_memory.active_domain == "finance":
            return _queue_from_specialist("finance_specialist") or "financeiro"
        if "academic" in ctx.operational_memory.active_domains or ctx.operational_memory.active_domain == "academic":
            return _queue_from_specialist("academic_specialist") or "coordenacao"
        if "support" in ctx.operational_memory.active_domains or ctx.operational_memory.active_domain == "support":
            return _queue_from_specialist("workflow_specialist") or "atendimento"
    return _queue_from_specialist("workflow_specialist") or "atendimento"


def _build_support_handoff_summary(ctx: Any, *, queue_name: str) -> str:
    requester = "Visitante do bot"
    if isinstance(ctx.actor, dict) and str(ctx.actor.get("full_name") or "").strip():
        requester = str(ctx.actor.get("full_name")).strip()
    excerpt = " ".join(str(ctx.request.message or "").split())
    if len(excerpt) > 220:
        excerpt = f"{excerpt[:219].rstrip()}..."
    return (
        f"{requester} solicitou atendimento humano para a fila "
        f"{queue_name} pelo canal {ctx.request.channel.value}: {excerpt}"
    )


def _compose_support_handoff_answer(
    payload: dict[str, Any] | None,
    *,
    profile: dict[str, Any] | None,
    queue_name: str,
) -> str:
    if not isinstance(payload, dict):
        return _compose_human_handoff_answer(profile)
    item = payload.get("item")
    if not isinstance(item, dict):
        return _compose_human_handoff_answer(profile)
    ticket_code = str(
        item.get("ticket_code")
        or item.get("protocol_code")
        or item.get("linked_ticket_code")
        or "indisponivel"
    ).strip()
    status = str(item.get("status") or "queued").strip()
    created = bool(payload.get("created", False))
    queue_label = str(item.get("queue_name") or queue_name or "atendimento").strip()
    base = (
        f"Encaminhei sua solicitacao para a fila de {queue_label}. "
        if created
        else f"Sua solicitacao humana ja estava registrada na fila de {queue_label}. "
    )
    answer = f"{base}Protocolo: {ticket_code}. Status atual: {status}."
    whatsapp = _select_contact_channel(
        profile,
        label_contains=("secretaria", "atendimento comercial"),
        channel_equals=("whatsapp",),
    )
    if isinstance(whatsapp, dict) and str(whatsapp.get("value") or "").strip():
        answer += (
            " Se preferir, voce tambem pode seguir pelo WhatsApp oficial "
            f"{str(whatsapp.get('value')).strip()}."
        )
    return answer


def _compose_visit_status_answer(item: dict[str, Any], *, guidance_only: bool = False) -> str:
    protocol_code = str(item.get("protocol_code") or "indisponivel").strip()
    ticket_code = str(item.get("linked_ticket_code") or "").strip()
    slot_label = str(item.get("slot_label") or item.get("preferred_window") or "").strip()
    status = str(item.get("status") or "queued").strip()
    if guidance_only:
        parts = [f"Para remarcar a visita, eu sigo pelo protocolo {protocol_code}."]
        if slot_label:
            parts.append(f"A preferencia atual registrada e {slot_label}.")
        parts.append("Me diga o novo dia ou janela desejada e eu atualizo o pedido.")
        if ticket_code:
            parts.append(f"Ticket operacional: {ticket_code}.")
        return " ".join(parts)
    parts = [f"Seu pedido de visita segue {status}."]
    parts.append(f"Protocolo: {protocol_code}.")
    if slot_label:
        parts.append(f"Preferencia registrada: {slot_label}.")
    if ticket_code:
        parts.append(f"Ticket operacional: {ticket_code}.")
    return " ".join(parts)


def _compose_support_status_answer(item: dict[str, Any]) -> str:
    protocol_code = str(item.get("protocol_code") or "indisponivel").strip()
    queue_name = str(item.get("queue_name") or "atendimento").strip()
    status = str(item.get("status") or "queued").strip()
    ticket_code = str(item.get("linked_ticket_code") or "").strip()
    subject = str(item.get("subject") or "atendimento").strip()
    parts = [
        f"O atendimento sobre {subject} esta com status {status}.",
        f"Protocolo: {protocol_code}.",
        f"Fila: {queue_name}.",
    ]
    if ticket_code:
        parts.append(f"Ticket operacional: {ticket_code}.")
    return " ".join(parts)
