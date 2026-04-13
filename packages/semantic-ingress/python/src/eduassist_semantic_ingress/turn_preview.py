from __future__ import annotations

from typing import Any

from .turn_router import TurnFrame


def turn_frame_preview_metadata(turn_frame: TurnFrame | None) -> dict[str, Any] | None:
    if turn_frame is None:
        return None
    if turn_frame.capability_id is None and turn_frame.conversation_act == "none":
        return None
    return {
        "conversation_act": turn_frame.conversation_act,
        "capability_id": turn_frame.capability_id,
        "domain": turn_frame.domain,
        "access_tier": turn_frame.access_tier,
        "scope": turn_frame.scope,
        "confidence": turn_frame.confidence,
        "confidence_bucket": turn_frame.confidence_bucket,
        "reason": turn_frame.reason,
        "source": turn_frame.source,
        "needs_clarification": turn_frame.needs_clarification,
        "follow_up_of": turn_frame.follow_up_of,
        "public_conversation_act": turn_frame.public_conversation_act,
        "public_focus_hint": turn_frame.public_focus_hint,
        "requested_attribute": turn_frame.requested_attribute,
        "candidate_capability_ids": list(turn_frame.candidate_capability_ids),
    }
