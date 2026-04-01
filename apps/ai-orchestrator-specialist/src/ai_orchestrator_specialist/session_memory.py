from __future__ import annotations

import os
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


def build_supervisor_session(
    *,
    conversation_id: str,
    agent_memory_url: str,
) -> SQLAlchemySession:
    memory_url, create_memory_tables = prepare_agent_memory(agent_memory_url)
    return SQLAlchemySession.from_url(
        conversation_id,
        url=memory_url,
        create_tables=create_memory_tables,
    )
