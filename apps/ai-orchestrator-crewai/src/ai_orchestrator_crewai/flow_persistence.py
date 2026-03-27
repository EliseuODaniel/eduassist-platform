from __future__ import annotations

from functools import lru_cache
import os
from pathlib import Path

try:
    from crewai.flow.persistence import SQLiteFlowPersistence
except Exception:  # pragma: no cover - defensive import
    SQLiteFlowPersistence = None  # type: ignore[assignment]


DEFAULT_FLOW_STATE_DIR = '/workspace/artifacts/crewai-flow-state'


def _flow_state_root() -> Path:
    configured = str(os.getenv('CREWAI_FLOW_STATE_DIR') or DEFAULT_FLOW_STATE_DIR).strip()
    path = Path(configured)
    path.mkdir(parents=True, exist_ok=True)
    return path


@lru_cache(maxsize=8)
def get_sqlite_flow_persistence(slice_name: str):
    if SQLiteFlowPersistence is None:
        return None
    db_path = _flow_state_root() / f'{slice_name}.sqlite3'
    return SQLiteFlowPersistence(db_path=str(db_path))


def build_flow_state_id(
    *,
    slice_name: str,
    conversation_id: str | None,
    telegram_chat_id: int | None,
    channel: str,
) -> str | None:
    normalized_channel = str(channel or 'telegram').strip() or 'telegram'
    if conversation_id:
        return f'{slice_name}:{normalized_channel}:conversation:{conversation_id}'
    if telegram_chat_id is not None:
        return f'{slice_name}:{normalized_channel}:telegram_chat:{telegram_chat_id}'
    return None
