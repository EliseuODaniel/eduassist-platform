from __future__ import annotations

from typing import Any

from eduassist_semantic_ingress import (
    IngressSemanticPlan,
    looks_like_school_scope_message,
    resolve_semantic_ingress_with_provider,
    should_run_semantic_ingress_classifier,
)


def _preview_payload(preview_hint: dict[str, Any] | None) -> dict[str, Any]:
    preview = preview_hint if isinstance(preview_hint, dict) else {}
    classification = preview.get("classification") if isinstance(preview.get("classification"), dict) else {}
    return {
        "mode": str(preview.get("mode") or "").strip(),
        "domain": str(classification.get("domain") or "").strip(),
        "access_tier": str(classification.get("access_tier") or "").strip(),
        "reason": str(preview.get("reason") or "").strip(),
        "selected_tools": list(preview.get("selected_tools") or []),
    }


async def maybe_resolve_semantic_ingress_plan(
    *,
    settings: Any,
    request_message: str,
    conversation_context: dict[str, Any] | None,
    preview_hint: dict[str, Any] | None,
) -> IngressSemanticPlan | None:
    preview_payload = _preview_payload(preview_hint)
    if not should_run_semantic_ingress_classifier(
        message=request_message,
        current_domain=str(preview_payload.get("domain") or ""),
        current_access_tier=str(preview_payload.get("access_tier") or ""),
        current_mode=str(preview_payload.get("mode") or ""),
    ):
        return None
    plan = await resolve_semantic_ingress_with_provider(
        settings=settings,
        stack_label="specialist_supervisor",
        request_message=request_message,
        conversation_context=conversation_context,
        preview=preview_payload,
    )
    if plan is None or plan.conversation_act == "none":
        return None
    if plan.conversation_act == "scope_boundary" and looks_like_school_scope_message(request_message):
        return None
    return plan


def apply_semantic_ingress_preview_hint(
    *,
    preview_hint: dict[str, Any] | None,
    plan: IngressSemanticPlan,
) -> dict[str, Any]:
    preview = dict(preview_hint or {})
    preview["mode"] = "structured_tool"
    preview["classification"] = {
        "domain": "institution",
        "access_tier": "public",
        "confidence": 0.97,
        "reason": f"specialist_semantic_ingress:{plan.conversation_act}",
    }
    preview["retrieval_backend"] = "none"
    preview["graph_path"] = [
        *list(preview.get("graph_path") or ["specialist_supervisor", "local_preview_hint"]),
        f"semantic_ingress:{plan.conversation_act}",
    ]
    preview["reason"] = f"specialist_semantic_ingress:{plan.conversation_act}"
    preview["semantic_ingress"] = plan.model_dump(mode="json")
    return preview


def semantic_ingress_act(preview_hint: dict[str, Any] | None) -> str | None:
    preview = preview_hint if isinstance(preview_hint, dict) else {}
    payload = preview.get("semantic_ingress")
    if not isinstance(payload, dict):
        return None
    act = str(payload.get("conversation_act") or "").strip()
    return act or None
