from __future__ import annotations

from typing import Any

from eduassist_semantic_ingress import (
    IngressSemanticPlan,
    TurnFrame,
    effective_turn_frame_authenticated as _effective_turn_frame_authenticated,
    is_terminal_ingress_act,
    looks_like_school_scope_message,
    resolve_semantic_ingress_with_provider,
    resolve_turn_frame_with_provider,
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

_TURN_FRAME_PUBLIC_TOOL_MAP: dict[str, tuple[str, ...]] = {
    "pricing": ("get_public_school_profile", "project_public_pricing"),
    "leadership": ("get_public_school_profile", "get_org_directory"),
    "document_submission": ("get_public_school_profile",),
    "schedule": ("get_public_school_profile",),
    "timeline": ("get_public_school_profile",),
    "features": ("get_public_school_profile",),
    "operating_hours": ("get_public_school_profile",),
}

_TURN_FRAME_PROTECTED_TOOL_MAP: dict[str, tuple[str, ...]] = {
    "protected.account.access_scope": ("get_actor_identity_context",),
    "protected.documents.restricted_lookup": ("retrieve_restricted_documents",),
    "protected.institution.admin_finance_status": (
        "get_administrative_status",
        "get_financial_summary",
    ),
    "protected.finance.summary": ("get_financial_summary",),
    "protected.finance.next_due": ("get_financial_summary",),
    "protected.teacher.schedule": ("get_teacher_schedule",),
    "protected.academic.upcoming_assessments": (
        "get_student_academic_summary",
        "get_student_upcoming_assessments",
    ),
    "protected.academic.family_comparison": ("get_student_academic_summary",),
    "protected.academic.grades": (
        "get_student_academic_summary",
        "get_student_grades",
        "get_student_upcoming_assessments",
    ),
    "protected.academic.attendance": (
        "get_student_attendance",
        "get_student_attendance_timeline",
    ),
    "protected.administrative.status": (
        "get_student_administrative_status",
        "get_administrative_status",
    ),
}


def _preview_payload(preview: OrchestrationPreview) -> dict[str, Any]:
    payload = {
        "mode": preview.mode.value,
        "domain": preview.classification.domain.value,
        "access_tier": preview.classification.access_tier.value,
        "reason": preview.reason,
        "selected_tools": list(preview.selected_tools),
    }
    turn_frame = getattr(preview, "turn_frame", None)
    if isinstance(turn_frame, dict):
        payload["turn_frame"] = turn_frame
    return payload


def resolve_turn_frame_authenticated_flag(
    *,
    request_message: str,
    authenticated: bool,
    actor: dict[str, Any] | None = None,
) -> bool:
    return _effective_turn_frame_authenticated(
        authenticated=authenticated,
        actor_present=isinstance(actor, dict) and bool(actor),
        message=request_message,
    )


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


async def maybe_resolve_turn_frame(
    *,
    settings: Any,
    request_message: str,
    conversation_context: dict[str, Any] | None,
    preview: OrchestrationPreview,
    stack_label: str,
    authenticated: bool,
) -> TurnFrame | None:
    return await resolve_turn_frame_with_provider(
        settings=settings,
        stack_label=stack_label,
        request_message=request_message,
        conversation_context=conversation_context,
        preview=_preview_payload(preview),
        authenticated=authenticated,
    )


def apply_turn_frame_preview(
    *,
    preview: OrchestrationPreview,
    turn_frame: TurnFrame,
    stack_name: str,
) -> OrchestrationPreview:
    if turn_frame.capability_id is None and turn_frame.conversation_act == "none":
        return preview
    selected_tools = list(preview.selected_tools)
    if turn_frame.scope == "public":
        selected_tools = list(
            dict.fromkeys(
                _TURN_FRAME_PUBLIC_TOOL_MAP.get(
                    str(turn_frame.public_conversation_act or "").strip(),
                    ("get_public_school_profile",),
                )
            )
        )
    elif turn_frame.scope == "protected":
        selected_tools = list(
            dict.fromkeys(
                _TURN_FRAME_PROTECTED_TOOL_MAP.get(
                    str(turn_frame.capability_id or "").strip(),
                    tuple(preview.selected_tools),
                )
            )
        )
    access_tier = (
        AccessTier.public
        if turn_frame.access_tier == "public"
        else AccessTier.authenticated
        if turn_frame.access_tier == "authenticated"
        else AccessTier.sensitive
    )
    domain = (
        QueryDomain.institution
        if turn_frame.domain == "institution"
        else QueryDomain.calendar
        if turn_frame.domain == "calendar"
        else QueryDomain.academic
        if turn_frame.domain == "academic"
        else QueryDomain.finance
        if turn_frame.domain == "finance"
        else QueryDomain.support
        if turn_frame.domain == "support"
        else QueryDomain.unknown
    )
    mode = (
        OrchestrationMode.clarify
        if turn_frame.needs_clarification
        else OrchestrationMode.structured_tool
    )
    graph_path = [
        *list(preview.graph_path),
        f"turn_frame:{turn_frame.capability_id or turn_frame.conversation_act}",
    ]
    return preview.model_copy(
        update={
            "mode": mode,
            "classification": IntentClassification(
                domain=domain,
                access_tier=access_tier,
                confidence=turn_frame.confidence,
                reason=f"{stack_name}_turn_frame:{turn_frame.capability_id or turn_frame.conversation_act}",
            ),
            "retrieval_backend": RetrievalBackend.none
            if mode is OrchestrationMode.structured_tool
            else preview.retrieval_backend,
            "selected_tools": selected_tools,
            "needs_authentication": access_tier is not AccessTier.public
            and mode is not OrchestrationMode.clarify,
            "graph_path": graph_path,
            "reason": f"{stack_name}_turn_frame:{turn_frame.capability_id or turn_frame.conversation_act}",
            "output_contract": "turno estruturado pelo semantic router e resolvido pela stack",
        }
    )


def build_turn_frame_public_plan(turn_frame: TurnFrame | None) -> Any:
    if turn_frame is None or turn_frame.scope != "public":
        return None
    act = str(turn_frame.public_conversation_act or "").strip()
    if not act:
        return None
    from . import runtime as rt

    return rt.PublicInstitutionPlan(
        conversation_act=act,
        required_tools=_TURN_FRAME_PUBLIC_TOOL_MAP.get(act, ("get_public_school_profile",)),
        fetch_profile=True,
        requested_attribute=turn_frame.requested_attribute,
        focus_hint=turn_frame.public_focus_hint,
        semantic_source="turn_frame",
        use_conversation_context=bool(turn_frame.follow_up_of),
    )


def is_terminal_semantic_ingress_plan(plan: IngressSemanticPlan | None) -> bool:
    if plan is None:
        return False
    return is_terminal_ingress_act(plan.conversation_act)
