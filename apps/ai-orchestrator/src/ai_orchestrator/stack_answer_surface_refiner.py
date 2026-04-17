from __future__ import annotations

from typing import Any

from eduassist_semantic_ingress import refine_answer_surface_with_provider

from .models import AccessTier, MessageResponse, MessageResponseRequest, OrchestrationMode


def _csv_values(raw: str | None) -> set[str]:
    return {item.strip().casefold() for item in str(raw or "").split(",") if item.strip()}


def _normalize_text(value: Any) -> str:
    return " ".join(str(value or "").strip().split())


def _refiner_enabled(
    *,
    request: MessageResponseRequest,
    response: MessageResponse,
    settings: Any,
    stack_name: str,
) -> bool:
    if not bool(getattr(settings, "feature_flag_answer_surface_refiner_enabled", True)):
        return False
    stack_allowlist = _csv_values(getattr(settings, "feature_flag_answer_surface_refiner_stacks", ""))
    if stack_allowlist and str(stack_name or "").strip().casefold() not in stack_allowlist:
        return False
    channel_allowlist = _csv_values(getattr(settings, "feature_flag_answer_surface_refiner_channels", "telegram,web"))
    if channel_allowlist and request.channel.value.casefold() not in channel_allowlist:
        return False
    if request.debug_options.get("disable_answer_experience"):
        return False
    if not str(response.message_text or "").strip():
        return False
    return True


def _refiner_mode(response: MessageResponse) -> str:
    reason = _normalize_text(
        getattr(response, "answer_experience_reason", None) or getattr(response, "reason", None)
    ).casefold()
    text = _normalize_text(getattr(response, "message_text", None)).casefold()
    if response.mode == OrchestrationMode.clarify:
        return "clarify"
    if response.mode == OrchestrationMode.deny or any(
        token in reason for token in ("third_party_denied", "privacy_guardrail", "input_guardrail_blocked", "denied", "blocked")
    ):
        return "deny"
    if "scope_boundary" in reason or "boundary" in reason:
        return "boundary"
    if "auth_guidance" in reason or "/start link_" in text or "portal autenticado" in text or "codigo" in text or "código" in text:
        return "auth_guidance"
    if response.classification.access_tier != AccessTier.public:
        return "protected"
    return "public"


def _build_evidence_lines(response: MessageResponse) -> list[str]:
    lines: list[str] = []
    if response.evidence_pack is not None:
        for support in response.evidence_pack.supports[:8]:
            label = _normalize_text(support.label or support.kind)
            detail = _normalize_text(support.detail)
            excerpt = _normalize_text(support.excerpt)
            fragments = [part for part in (label, detail, excerpt) if part]
            if fragments:
                lines.append(" | ".join(fragments))
        summary = _normalize_text(response.evidence_pack.summary)
        if summary:
            lines.append(summary)
    for citation in response.citations[:4]:
        excerpt = _normalize_text(citation.excerpt)
        if excerpt:
            lines.append(f"{citation.document_title}: {excerpt}")
    for event in response.calendar_events[:4]:
        detail = _normalize_text(event.description)
        fragments = [event.title, detail, event.starts_at.isoformat()]
        lines.append(" | ".join(part for part in fragments if part))
    deduped: list[str] = []
    seen: set[str] = set()
    for line in lines:
        key = line.casefold()
        if not key or key in seen:
            continue
        seen.add(key)
        deduped.append(line)
    return deduped[:10]


def _target_names(response: MessageResponse) -> list[str]:
    names: list[str] = []
    if response.evidence_pack is None:
        return names
    for support in response.evidence_pack.supports[:6]:
        cleaned = str(support.label or "").strip()
        if not cleaned or cleaned in names:
            continue
        names.append(cleaned)
    return names[:3]


async def maybe_refine_stack_response_surface(
    *,
    stack_name: str,
    request: MessageResponseRequest,
    response: MessageResponse,
    settings: Any,
) -> MessageResponse:
    if not _refiner_enabled(
        request=request,
        response=response,
        settings=settings,
        stack_name=stack_name,
    ):
        return response
    evidence_lines = _build_evidence_lines(response) or [str(response.message_text or "").strip()]
    refinement = await refine_answer_surface_with_provider(
        settings=settings,
        stack_label=stack_name,
        request_message=request.message,
        original_text=response.message_text,
        answer_mode=_refiner_mode(response),
        answer_reason=str(
            getattr(response, "answer_experience_reason", None) or getattr(response, "reason", "") or ""
        ),
        domain=response.classification.domain.value,
        access_tier=response.classification.access_tier.value,
        evidence_lines=evidence_lines,
        conversation_context=None,
        target_names=_target_names(response),
        active_subject=None,
    )
    if not refinement.used_llm:
        return response
    llm_stages = [str(item).strip() for item in (response.llm_stages or []) if str(item).strip()]
    if "answer_surface_refiner" not in llm_stages:
        llm_stages.append("answer_surface_refiner")
    base_reason = str(getattr(response, "answer_experience_reason", None) or getattr(response, "reason", "") or "")
    reason_suffix = str(refinement.reason or "answer_surface_refiner")
    combined_reason = f"{base_reason}:{reason_suffix}" if base_reason else reason_suffix
    return response.model_copy(
        update={
            "message_text": refinement.answer_text,
            "used_llm": bool(getattr(response, "used_llm", False) or refinement.used_llm),
            "llm_stages": llm_stages,
            "answer_experience_eligible": True,
            "answer_experience_applied": bool(getattr(response, "answer_experience_applied", False) or refinement.changed),
            "answer_experience_reason": combined_reason,
            "answer_experience_provider": settings.llm_provider,
            "answer_experience_model": settings.google_model if settings.llm_provider in {"google", "gemini"} else settings.openai_model,
        }
    )
