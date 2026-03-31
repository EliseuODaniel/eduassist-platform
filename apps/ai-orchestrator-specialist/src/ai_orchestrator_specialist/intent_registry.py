from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

from .models import IntentRouteSpec


def _default_registry_path() -> Path:
    return Path(__file__).with_name("intent_registry.json")


@lru_cache(maxsize=1)
def _load_intent_specs() -> tuple[IntentRouteSpec, ...]:
    payload = json.loads(_default_registry_path().read_text(encoding="utf-8"))
    return tuple(IntentRouteSpec.model_validate(item) for item in payload if isinstance(item, dict))


def get_intent_registry() -> tuple[IntentRouteSpec, ...]:
    return _load_intent_specs()


def has_registered_school_signal(normalized_message: str) -> bool:
    message = str(normalized_message or "").strip()
    if not message:
        return False
    for spec in get_intent_registry():
        if any(term and term in message for term in spec.any_terms):
            return True
        if spec.all_terms and all(term and term in message for term in spec.all_terms):
            return True
    return False
