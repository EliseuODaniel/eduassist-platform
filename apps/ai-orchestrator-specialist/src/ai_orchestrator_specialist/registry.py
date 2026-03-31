from __future__ import annotations

import json
import os
from functools import lru_cache
from pathlib import Path

from .models import SpecialistSpec


def _default_registry_path() -> Path:
    return Path(__file__).with_name("specialist_registry.json")


def _registry_path() -> Path:
    configured = str(os.getenv("SPECIALIST_SUPERVISOR_REGISTRY_PATH", "") or "").strip()
    if configured:
        return Path(configured)
    return _default_registry_path()


@lru_cache(maxsize=1)
def _load_registry_specs() -> tuple[SpecialistSpec, ...]:
    path = _registry_path()
    payload = json.loads(path.read_text(encoding="utf-8"))
    return tuple(SpecialistSpec.model_validate(item) for item in payload if isinstance(item, dict))


def get_specialist_registry() -> dict[str, SpecialistSpec]:
    return {spec.id: spec for spec in _load_registry_specs() if spec.activation_flag}

