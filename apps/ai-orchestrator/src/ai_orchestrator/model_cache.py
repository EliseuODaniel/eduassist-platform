from __future__ import annotations

import os
from pathlib import Path
import shutil


def _cache_root() -> Path:
    raw = str(os.getenv("XDG_CACHE_HOME", "") or "").strip()
    if raw:
        return Path(raw)
    return Path("/tmp/eduassist-cache")


def _ensure_writable_cache_dir(preferred: Path, *, fallback: Path) -> Path:
    try:
        preferred.mkdir(parents=True, exist_ok=True)
        probe = preferred / ".write-test"
        probe.write_text("ok", encoding="utf-8")
        probe.unlink(missing_ok=True)
        return preferred
    except OSError:
        fallback.mkdir(parents=True, exist_ok=True)
        return fallback


def configure_model_cache_env() -> None:
    preferred_root = _cache_root()
    cache_root = _ensure_writable_cache_dir(
        preferred_root,
        fallback=Path("/tmp/eduassist-cache"),
    )
    huggingface_home = cache_root / "huggingface"
    hub_cache = huggingface_home / "hub"
    fastembed_cache = cache_root / "fastembed"
    os.environ["XDG_CACHE_HOME"] = str(cache_root)
    os.environ["HF_HOME"] = str(huggingface_home)
    os.environ["HF_HUB_CACHE"] = str(hub_cache)
    os.environ["HUGGINGFACE_HUB_CACHE"] = os.environ["HF_HUB_CACHE"]
    os.environ["FASTEMBED_CACHE_PATH"] = str(fastembed_cache)
    hub_cache.mkdir(parents=True, exist_ok=True)
    fastembed_cache.mkdir(parents=True, exist_ok=True)


def fastembed_cache_path() -> Path:
    configure_model_cache_env()
    return Path(os.environ["FASTEMBED_CACHE_PATH"])


def clear_fastembed_cache() -> None:
    shutil.rmtree(fastembed_cache_path(), ignore_errors=True)


configure_model_cache_env()
