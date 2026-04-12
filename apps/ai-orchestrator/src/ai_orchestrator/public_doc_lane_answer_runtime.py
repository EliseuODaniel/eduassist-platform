from __future__ import annotations

import inspect
from typing import Any, Callable

LOCAL_EXTRACTED_NAMES = {"compose_public_canonical_lane_answer"}

from . import public_doc_knowledge as _native
from .public_doc_lane_registry import PUBLIC_CANONICAL_LANE_COMPOSERS


def _refresh_native_namespace() -> None:
    for name, value in vars(_native).items():
        if name.startswith("__") or name in LOCAL_EXTRACTED_NAMES:
            continue
        globals()[name] = value


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
    _refresh_native_namespace()
    composer_name = PUBLIC_CANONICAL_LANE_COMPOSERS.get(lane)
    composer = globals().get(str(composer_name or "")) if composer_name else None
    if not callable(composer):
        return None
    return _invoke_lane_composer(composer, profile=profile)
