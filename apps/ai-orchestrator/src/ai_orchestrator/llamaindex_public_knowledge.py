from __future__ import annotations

from typing import Any

from .public_doc_knowledge import (
    compose_public_canonical_lane_answer as _shared_compose_public_canonical_lane_answer,
    compose_public_conduct_policy_contextual_answer as _shared_compose_public_conduct_policy_contextual_answer,
    match_public_canonical_lane as _shared_match_public_canonical_lane,
)


def match_public_canonical_lane(message: str) -> str | None:
    return _shared_match_public_canonical_lane(message)


def compose_public_canonical_lane_answer(
    lane: str,
    *,
    profile: dict[str, Any] | None = None,
) -> str | None:
    return _shared_compose_public_canonical_lane_answer(lane, profile=profile)


def compose_public_conduct_policy_contextual_answer(
    message: str,
    *,
    profile: dict[str, Any] | None = None,
) -> str | None:
    return _shared_compose_public_conduct_policy_contextual_answer(message, profile=profile)
