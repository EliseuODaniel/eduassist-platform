from __future__ import annotations

from typing import Any

from eduassist_semantic_ingress import (
    IngressSemanticPlan,
    is_terminal_ingress_act,
    looks_like_school_scope_message,
    resolve_semantic_ingress_with_provider,
    should_run_semantic_ingress_classifier,
)

from .models import AccessTier, IntentClassification, OrchestrationMode, OrchestrationPreview, QueryDomain, RetrievalBackend


_SEMANTIC_INGRESS_TOOL_MAP: dict[str, tuple[str, ...]] = {
    "greeting": ("get_public_school_profile", "list_assistant_capabilities"),
    "assistant_identity": ("get_public_school_profile", "get_org_directory"),
    "auth_guidance": ("get_public_school_profile",),
    "capabilities": ("get_public_school_profile", "list_assistant_capabilities"),
    "input_clarification": ("get_public_school_profile",),
    "language_preference": ("get_public_school_profile",),
    "scope_boundary": ("get_public_school_profile", "list_assistant_capabilities"),
}


def _preview_payload(preview: OrchestrationPreview) -> dict[str, Any]:
    return {
        "mode": preview.mode.value,
        "domain": preview.classification.domain.value,
        "access_tier": preview.classification.access_tier.value,
        "reason": preview.reason,
        "selected_tools": list(preview.selected_tools),
    }


async def maybe_resolve_semantic_ingress_plan(
    *,
    settings: Any,
    request_message: str,
    conversation_context: dict[str, Any] | None,
    preview: OrchestrationPreview,
    stack_label: str,
) -> IngressSemanticPlan | None:
    if not should_run_semantic_ingress_classifier(
        message=request_message,
        current_domain=preview.classification.domain.value,
        current_access_tier=preview.classification.access_tier.value,
        current_mode=preview.mode.value,
    ):
        return None
    plan = await resolve_semantic_ingress_with_provider(
        settings=settings,
        stack_label=stack_label,
        request_message=request_message,
        conversation_context=conversation_context,
        preview=_preview_payload(preview),
    )
    if plan is None or plan.conversation_act == "none":
        return None
    if plan.conversation_act == "scope_boundary" and looks_like_school_scope_message(request_message):
        return None
    return plan


def apply_semantic_ingress_preview(
    *,
    preview: OrchestrationPreview,
    plan: IngressSemanticPlan,
    stack_name: str,
) -> OrchestrationPreview:
    ingress_tools = list(_SEMANTIC_INGRESS_TOOL_MAP.get(plan.conversation_act, ()))
    if is_terminal_ingress_act(plan.conversation_act):
        selected_tools = ingress_tools
    else:
        selected_tools = list(dict.fromkeys([*ingress_tools, *preview.selected_tools]))
    return preview.model_copy(
        update={
            "mode": OrchestrationMode.structured_tool,
            "classification": IntentClassification(
                domain=QueryDomain.institution,
                access_tier=AccessTier.public,
                confidence=0.97,
                reason=f"{stack_name}_semantic_ingress:{plan.conversation_act}",
            ),
            "retrieval_backend": RetrievalBackend.none,
            "selected_tools": selected_tools,
            "citations_required": False,
            "needs_authentication": False,
            "graph_path": [*list(preview.graph_path), f"semantic_ingress:{plan.conversation_act}"],
            "reason": f"{stack_name}_semantic_ingress:{plan.conversation_act}",
            "output_contract": "ato de entrada classificado por LLM e resolvido pela stack",
        }
    )


def build_semantic_ingress_public_plan(plan: IngressSemanticPlan) -> Any:
    from . import runtime as rt

    required_tools = _SEMANTIC_INGRESS_TOOL_MAP.get(plan.conversation_act, ())
    return rt.PublicInstitutionPlan(
        conversation_act=plan.conversation_act,
        required_tools=required_tools,
        fetch_profile=True,
        semantic_source="semantic_ingress_llm",
        use_conversation_context=bool(plan.use_conversation_context),
    )


def is_terminal_semantic_ingress_plan(plan: IngressSemanticPlan | None) -> bool:
    if plan is None:
        return False
    return is_terminal_ingress_act(plan.conversation_act)
