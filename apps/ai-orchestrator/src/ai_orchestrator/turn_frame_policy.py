from __future__ import annotations

from typing import Any

from .models import AccessTier, QueryDomain


def turn_frame_capability_id(turn_frame: Any) -> str | None:
    capability_id = str(getattr(turn_frame, "capability_id", "") or "").strip()
    return capability_id or None


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
