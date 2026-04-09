from __future__ import annotations

from pathlib import Path

import ai_orchestrator.model_cache as model_cache


def test_ensure_writable_cache_dir_falls_back_when_preferred_cannot_be_created(tmp_path: Path) -> None:
    fallback = tmp_path / "fallback"
    chosen = model_cache._ensure_writable_cache_dir(
        Path("/proc/eduassist-unwritable-cache"),
        fallback=fallback,
    )
    assert chosen == fallback
    assert fallback.exists()


def test_configure_model_cache_env_rewrites_workspace_cache_to_local_fallback(
    monkeypatch,
    tmp_path: Path,
) -> None:
    monkeypatch.setenv("XDG_CACHE_HOME", "/workspace/.cache")
    monkeypatch.setenv("HF_HOME", "/workspace/.cache/huggingface")
    monkeypatch.setenv("HF_HUB_CACHE", "/workspace/.cache/huggingface/hub")
    monkeypatch.setenv("HUGGINGFACE_HUB_CACHE", "/workspace/.cache/huggingface/hub")
    monkeypatch.setenv("FASTEMBED_CACHE_PATH", "/workspace/.cache/fastembed")
    monkeypatch.setattr(model_cache, "_cache_root", lambda: tmp_path / "runtime-cache")
    model_cache.configure_model_cache_env()

    assert Path(model_cache.os.environ["XDG_CACHE_HOME"]).is_dir()
    assert str(model_cache.os.environ["XDG_CACHE_HOME"]).startswith(str(tmp_path / "runtime-cache"))
    assert Path(model_cache.os.environ["HF_HUB_CACHE"]).is_dir()
    assert Path(model_cache.os.environ["FASTEMBED_CACHE_PATH"]).is_dir()
