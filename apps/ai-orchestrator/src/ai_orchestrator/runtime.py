"""Compatibility facade for the shared runtime surface.

The heavy implementation now lives in ``runtime_core.py`` plus domain-specific
bridge modules. Keep this file intentionally small so new work is pushed into
cohesive modules instead of rebuilding a god module.
"""

from __future__ import annotations

from . import runtime_core as _runtime_core
from .conversation_focus_runtime import _normalize_text as _runtime_normalize_text
from .public_orchestration_runtime import (
    _apply_workflow_follow_up_rescue as _runtime_apply_workflow_follow_up_rescue,
)


def _export_runtime_core() -> None:
    for name, value in vars(_runtime_core).items():
        if name.startswith('__'):
            continue
        globals()[name] = value


_export_runtime_core()

_apply_workflow_follow_up_rescue = _runtime_apply_workflow_follow_up_rescue
_normalize_text = _runtime_normalize_text

__all__ = [name for name in globals() if not name.startswith('__')]
