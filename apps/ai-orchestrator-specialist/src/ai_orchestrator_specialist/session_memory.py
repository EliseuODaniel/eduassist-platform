from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from agents.extensions.memory.sqlalchemy_session import SQLAlchemySession


def sqlalchemy_url(database_url: str) -> str:
    normalized = str(database_url or "").strip()
    if normalized.startswith("sqlite+aiosqlite:///"):
        return normalized
    if normalized.startswith("sqlite:///"):
        return normalized.replace("sqlite:///", "sqlite+aiosqlite:///", 1)
    if normalized.startswith("postgresql+asyncpg://"):
        return normalized
    if normalized.startswith("postgresql://"):
        return normalized.replace("postgresql://", "postgresql+asyncpg://", 1)
    return normalized


def sqlite_database_path(database_url: str) -> str | None:
    normalized = sqlalchemy_url(database_url)
    if normalized.startswith("sqlite+aiosqlite:///"):
        return normalized.split("sqlite+aiosqlite:///", 1)[1]
    if normalized.startswith("sqlite:///"):
        return normalized.split("sqlite:///", 1)[1]
    return None


def prepare_agent_memory(database_url: str) -> tuple[str, bool]:
    normalized = sqlalchemy_url(database_url)
    sqlite_path = sqlite_database_path(normalized)
    if sqlite_path:
        parent = os.path.dirname(sqlite_path)
        if parent:
            os.makedirs(parent, exist_ok=True)
        return normalized, True
    return normalized, False


def _default_runtime_dir() -> Path:
    return Path(__file__).resolve().parents[4] / ".runtime"


def _sqlite_url_from_path(path: Path) -> str:
    return f"sqlite+aiosqlite:///{path}"


def _resolved_sqlite_path(sqlite_path: str, *, preferred_dir: str | None = None) -> Path:
    candidate = Path(sqlite_path)
    target_dir = Path(preferred_dir).expanduser() if preferred_dir else None
    if target_dir is not None:
        target_dir.mkdir(parents=True, exist_ok=True)
        return target_dir / candidate.name
    parent = candidate.parent
    try:
        parent.mkdir(parents=True, exist_ok=True)
        test_file = parent / ".write_check"
        test_file.write_text("ok", encoding="utf-8")
        test_file.unlink(missing_ok=True)
        return candidate
    except Exception:
        fallback_dir = _default_runtime_dir()
        fallback_dir.mkdir(parents=True, exist_ok=True)
        return fallback_dir / candidate.name


def resolved_agent_memory_url(database_url: str, *, preferred_dir: str | None = None) -> tuple[str, bool]:
    normalized = sqlalchemy_url(database_url)
    sqlite_path = sqlite_database_path(normalized)
    if not sqlite_path:
        return normalized, False
    resolved_path = _resolved_sqlite_path(sqlite_path, preferred_dir=preferred_dir)
    resolved_path.parent.mkdir(parents=True, exist_ok=True)
    return _sqlite_url_from_path(resolved_path), True


def build_supervisor_session(
    *,
    conversation_id: str,
    agent_memory_url: str,
    preferred_dir: str | None = None,
) -> SQLAlchemySession:
    memory_url, create_memory_tables = resolved_agent_memory_url(agent_memory_url, preferred_dir=preferred_dir)
    return SQLAlchemySession.from_url(
        conversation_id,
        url=memory_url,
        create_tables=create_memory_tables,
    )
