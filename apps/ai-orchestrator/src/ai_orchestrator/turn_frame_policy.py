from __future__ import annotations

from typing import Any

from .models import AccessTier, QueryDomain


_DIRECT_PROTECTED_SPECIALIST_CAPABILITIES = {
    "protected.account.access_scope",
    "protected.institution.admin_finance_status",
    "protected.teacher.schedule",
    "protected.academic.upcoming_assessments",
    "protected.academic.family_comparison",
}


def turn_frame_capability_id(turn_frame: Any) -> str | None:
    capability_id = str(getattr(turn_frame, "capability_id", "") or "").strip()
    return capability_id or None


def is_scope_boundary_turn_frame(turn_frame: Any) -> bool:
    return str(getattr(turn_frame, "conversation_act", "") or "").strip() == "scope_boundary"


def is_restricted_document_turn_frame(turn_frame: Any) -> bool:
    return turn_frame_capability_id(turn_frame) == "protected.documents.restricted_lookup"


def is_teacher_schedule_turn_frame(turn_frame: Any) -> bool:
    return turn_frame_capability_id(turn_frame) == "protected.teacher.schedule"


def is_direct_protected_specialist_turn_frame(turn_frame: Any) -> bool:
    capability_id = turn_frame_capability_id(turn_frame)
    if capability_id is None:
        return False
    return capability_id in _DIRECT_PROTECTED_SPECIALIST_CAPABILITIES


def turn_frame_reason(turn_frame: Any) -> str:
    return str(getattr(turn_frame, "reason", "") or "").strip()


def is_external_public_facility_turn_frame(turn_frame: Any) -> bool:
    if not is_scope_boundary_turn_frame(turn_frame):
        return False
    return "external_public_facility" in turn_frame_reason(turn_frame)


def turn_frame_query_domain(turn_frame: Any) -> QueryDomain | None:
    domain = str(getattr(turn_frame, "domain", "") or "").strip().lower()
    mapping = {
        "institution": QueryDomain.institution,
        "calendar": QueryDomain.calendar,
        "academic": QueryDomain.academic,
        "finance": QueryDomain.finance,
        "support": QueryDomain.support,
        "unknown": QueryDomain.unknown,
    }
    return mapping.get(domain)


def turn_frame_access_tier(turn_frame: Any) -> AccessTier | None:
    access_tier = str(getattr(turn_frame, "access_tier", "") or "").strip().lower()
    mapping = {
        "public": AccessTier.public,
        "authenticated": AccessTier.authenticated,
        "sensitive": AccessTier.sensitive,
    }
    return mapping.get(access_tier)


def turn_frame_canonical_lane(turn_frame: Any) -> str | None:
    act = str(getattr(turn_frame, "public_conversation_act", "") or "").strip().lower()
    if act == "pricing":
        return "public_bundle.bolsas_and_processes"
    if act == "timeline":
        return "public_bundle.timeline_lifecycle"
    return None


def turn_frame_public_selected_tools(turn_frame: Any) -> list[str]:
    tools = ["get_public_school_profile"]
    if str(getattr(turn_frame, "public_conversation_act", "") or "").strip().lower() == "pricing":
        tools.append("project_public_pricing")
    return list(dict.fromkeys(tools))


def append_turn_frame_reason(reason: str, turn_frame: Any) -> str:
    capability_id = turn_frame_capability_id(turn_frame)
    if not capability_id:
        return reason
    return f"{reason};turn_frame={capability_id}"


def append_turn_frame_graph_path(graph_path: list[str], turn_frame: Any) -> list[str]:
    capability_id = turn_frame_capability_id(turn_frame)
    if not capability_id:
        return list(graph_path)
    return [*list(graph_path), f"turn_frame:{capability_id}"]


def preview_targets_restricted_document_surface(preview: Any) -> bool:
    reason = str(getattr(preview, "reason", "") or "").strip().lower()
    if any(
        marker in reason
        for marker in ("restricted_document", "restricted_doc", "protected.documents.restricted_lookup")
    ):
        return True
    graph_path = [
        str(node).strip().lower()
        for node in (getattr(preview, "graph_path", None) or [])
        if str(node).strip()
    ]
    if any("turn_frame:protected.documents.restricted_lookup" in node for node in graph_path):
        return True
    selected_tools = {
        str(tool).strip().lower()
        for tool in (getattr(preview, "selected_tools", None) or [])
        if str(tool).strip()
    }
    return "retrieve_restricted_documents" in selected_tools or (
        "search_documents" in selected_tools and "restricted" in reason
    )
