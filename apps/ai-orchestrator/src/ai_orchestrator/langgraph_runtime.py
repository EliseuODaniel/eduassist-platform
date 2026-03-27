from __future__ import annotations

from dataclasses import dataclass
import logging
import threading
from typing import Any
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from langgraph.types import Command

from .graph import build_orchestration_graph
from .models import (
    AccessTier,
    IntentClassification,
    OrchestrationMode,
    OrchestrationRequest,
    QueryDomain,
    RetrievalBackend,
    UserContext,
    UserRole,
)

logger = logging.getLogger(__name__)


@dataclass
class LangGraphArtifacts:
    graph: Any
    thread_id_enabled: bool
    checkpointer_enabled: bool
    checkpointer_backend: str | None
    checkpointer_context: Any | None = None


_ARTIFACTS_CACHE: dict[tuple[bool, bool, str], LangGraphArtifacts] = {}
_ARTIFACTS_LOCK = threading.Lock()
_CHECKPOINT_MSGPACK_ALLOWLIST: tuple[type[Any], ...] = (
    UserRole,
    QueryDomain,
    AccessTier,
    OrchestrationMode,
    RetrievalBackend,
    UserContext,
    OrchestrationRequest,
    IntentClassification,
)


def _normalize_postgres_conn_string(conn_string: str | None) -> str | None:
    value = str(conn_string or '').strip()
    if not value:
        return None
    if value.startswith('postgresql+'):
        scheme, remainder = value.split('://', 1)
        normalized_scheme = scheme.split('+', 1)[0]
        return f'{normalized_scheme}://{remainder}'
    return value


def _base_checkpoint_conn_string(settings: Any) -> str | None:
    explicit_value = _normalize_postgres_conn_string(getattr(settings, 'langgraph_checkpointer_url', None))
    if explicit_value:
        return explicit_value
    return _normalize_postgres_conn_string(getattr(settings, 'database_url', None))


def _checkpoint_schema(settings: Any) -> str | None:
    value = str(getattr(settings, 'langgraph_checkpointer_schema', 'langgraph_checkpoint') or '').strip()
    return value or None


def _checkpoint_conn_string(settings: Any) -> str | None:
    base_conn_string = _base_checkpoint_conn_string(settings)
    schema = _checkpoint_schema(settings)
    if not base_conn_string or not schema:
        return base_conn_string
    split = urlsplit(base_conn_string)
    query_params = parse_qsl(split.query, keep_blank_values=True)
    query_params = [(key, value) for key, value in query_params if key != 'options']
    query_params.append(('options', f'-csearch_path={schema}'))
    return urlunsplit((split.scheme, split.netloc, split.path, urlencode(query_params), split.fragment))


def _checkpoint_requested(settings: Any) -> bool:
    return bool(getattr(settings, 'langgraph_checkpointer_enabled', True))


def _graph_cache_key(settings: Any) -> tuple[bool, bool, str]:
    checkpoint_conn_string = _checkpoint_conn_string(settings) or ''
    return (
        bool(getattr(settings, 'graph_rag_enabled', False)),
        _checkpoint_requested(settings) and bool(checkpoint_conn_string),
        checkpoint_conn_string,
    )


def _apply_checkpoint_serde_allowlist(checkpointer: Any) -> None:
    serde = getattr(checkpointer, 'serde', None)
    if serde is None:
        return
    try:
        from langgraph.checkpoint.serde.jsonplus import JsonPlusSerializer

        current_unpack_ext_hook = getattr(serde, '_unpack_ext_hook', None)
        custom_unpack_ext_hook = (
            current_unpack_ext_hook
            if getattr(serde, '_custom_unpack_ext_hook', False) and callable(current_unpack_ext_hook)
            else None
        )
        checkpointer.serde = JsonPlusSerializer(
            pickle_fallback=bool(getattr(serde, 'pickle_fallback', False)),
            allowed_json_modules=getattr(serde, '_allowed_json_modules', None),
            allowed_msgpack_modules=_CHECKPOINT_MSGPACK_ALLOWLIST,
            __unpack_ext_hook__=custom_unpack_ext_hook,
        )
    except Exception:
        logger.warning('langgraph_checkpointer_serde_allowlist_failed', exc_info=True)


def get_langgraph_artifacts(settings: Any) -> LangGraphArtifacts:
    cache_key = _graph_cache_key(settings)
    with _ARTIFACTS_LOCK:
        cached = _ARTIFACTS_CACHE.get(cache_key)
        if cached is not None:
            return cached

        checkpoint_conn_string = _checkpoint_conn_string(settings)
        checkpointer = None
        checkpointer_context = None
        checkpointer_enabled = False
        checkpointer_backend: str | None = None

        if _checkpoint_requested(settings) and checkpoint_conn_string:
            try:
                from langgraph.checkpoint.postgres import PostgresSaver
                import psycopg
                from psycopg import sql

                schema = _checkpoint_schema(settings)
                base_conn_string = _base_checkpoint_conn_string(settings)
                if schema and base_conn_string:
                    try:
                        with psycopg.connect(base_conn_string, autocommit=True) as connection:
                            with connection.cursor() as cursor:
                                cursor.execute(
                                    sql.SQL('CREATE SCHEMA IF NOT EXISTS {}').format(sql.Identifier(schema))
                                )
                    except Exception:
                        logger.warning('langgraph_checkpointer_schema_create_skipped', exc_info=True)
                checkpointer_context = PostgresSaver.from_conn_string(checkpoint_conn_string)
                checkpointer = checkpointer_context.__enter__()
                if schema:
                    with checkpointer.conn.cursor() as cursor:
                        cursor.execute(
                            sql.SQL('SET search_path TO {}, public').format(sql.Identifier(schema))
                        )
                    checkpointer.conn.commit()
                _apply_checkpoint_serde_allowlist(checkpointer)
                checkpointer.setup()
                checkpointer_enabled = True
                checkpointer_backend = 'postgres'
                logger.info('langgraph_checkpointer_ready', extra={'backend': checkpointer_backend})
            except Exception:
                logger.exception('langgraph_checkpointer_initialization_failed')
                checkpointer = None
                checkpointer_context = None
                checkpointer_enabled = False
                checkpointer_backend = None

        graph = build_orchestration_graph(
            bool(getattr(settings, 'graph_rag_enabled', False)),
            checkpointer=checkpointer,
        )
        artifacts = LangGraphArtifacts(
            graph=graph,
            thread_id_enabled=True,
            checkpointer_enabled=checkpointer_enabled,
            checkpointer_backend=checkpointer_backend,
            checkpointer_context=checkpointer_context,
        )
        _ARTIFACTS_CACHE[cache_key] = artifacts
        return artifacts


def warm_langgraph_runtime(settings: Any) -> LangGraphArtifacts:
    return get_langgraph_artifacts(settings)


def close_langgraph_runtime() -> None:
    with _ARTIFACTS_LOCK:
        artifacts = list(_ARTIFACTS_CACHE.values())
        _ARTIFACTS_CACHE.clear()
    for artifact in artifacts:
        if artifact.checkpointer_context is None:
            continue
        try:
            artifact.checkpointer_context.__exit__(None, None, None)
        except Exception:
            logger.exception('langgraph_checkpointer_close_failed')


def get_langgraph_runtime_status(settings: Any) -> dict[str, Any]:
    cache_key = _graph_cache_key(settings)
    with _ARTIFACTS_LOCK:
        cached = _ARTIFACTS_CACHE.get(cache_key)
    checkpoint_conn_string = _checkpoint_conn_string(settings)
    return {
        'threadIdEnabled': True,
        'checkpointerConfigured': _checkpoint_requested(settings) and bool(checkpoint_conn_string),
        'checkpointerInitialized': cached.checkpointer_enabled if cached is not None else False,
        'checkpointerBackend': cached.checkpointer_backend if cached is not None else None,
    }


def resolve_langgraph_thread_id(
    *,
    conversation_external_id: str | None = None,
    channel: str | None = None,
    telegram_chat_id: int | None = None,
) -> str | None:
    if conversation_external_id:
        return f'conversation:{conversation_external_id}'
    normalized_channel = str(channel or 'telegram').strip() or 'telegram'
    if telegram_chat_id is not None:
        return f'{normalized_channel}:chat:{telegram_chat_id}'
    return None


def _thread_config(thread_id: str | None) -> dict[str, Any] | None:
    if not thread_id:
        return None
    return {'configurable': {'thread_id': thread_id}}


def invoke_orchestration_graph(
    *,
    graph: Any,
    state_input: dict[str, Any] | Command | None,
    thread_id: str | None,
    version: str = 'v1',
) -> Any:
    config = _thread_config(thread_id)
    if config is not None:
        return graph.invoke(state_input, config=config, version=version)
    return graph.invoke(state_input, version=version)


def resume_orchestration_graph(
    *,
    graph: Any,
    thread_id: str,
    resume_value: Any,
    version: str = 'v1',
) -> Any:
    return graph.invoke(Command(resume=resume_value), config=_thread_config(thread_id), version=version)


def get_orchestration_state_snapshot(
    *,
    graph: Any,
    thread_id: str,
    subgraphs: bool = False,
) -> Any:
    return graph.get_state(_thread_config(thread_id), subgraphs=subgraphs)
