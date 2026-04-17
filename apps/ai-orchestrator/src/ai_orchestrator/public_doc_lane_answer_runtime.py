from __future__ import annotations

import inspect
from functools import lru_cache
from typing import Any, Callable

from . import public_doc_knowledge as _native
from .public_doc_lane_registry import PUBLIC_CANONICAL_LANE_COMPOSERS

@lru_cache(maxsize=1)
def _public_lane_composer_lookup() -> dict[str, Callable[..., str | None]]:
    lookup: dict[str, Callable[..., str | None]] = {}
    for lane, composer_name in PUBLIC_CANONICAL_LANE_COMPOSERS.items():
        composer = getattr(_native, composer_name, None)
        if callable(composer):
            lookup[lane] = composer
    return lookup


def _invoke_lane_composer(
    composer: Callable[..., str | None],
    *,
    profile: dict[str, Any] | None = None,
) -> str | None:
    signature = inspect.signature(composer)
    if not signature.parameters:
        return composer()
    return composer(profile)


def compose_public_canonical_lane_answer(
    lane: str,
    *,
    profile: dict[str, Any] | None = None,
) -> str | None:
    composer = _public_lane_composer_lookup().get(lane)
    if composer is None:
        return None
    return _invoke_lane_composer(composer, profile=profile)
