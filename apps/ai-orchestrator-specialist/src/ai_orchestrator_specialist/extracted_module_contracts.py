from __future__ import annotations

from typing import Any


def refresh_extracted_module_contract(
    *,
    native_module: Any,
    namespace: dict[str, Any],
    contract_names: tuple[str, ...],
    local_extracted_names: set[str] | frozenset[str],
    contract_label: str,
) -> None:
    missing: list[str] = []
    for name in contract_names:
        if name in local_extracted_names:
            continue
        if not hasattr(native_module, name):
            missing.append(name)
            continue
        namespace[name] = getattr(native_module, name)
    if missing:
        missing_list = ", ".join(sorted(missing))
        raise RuntimeError(f"{contract_label} missing native contract symbols: {missing_list}")
