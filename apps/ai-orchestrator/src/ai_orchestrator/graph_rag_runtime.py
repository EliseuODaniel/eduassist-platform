from __future__ import annotations

import asyncio
import os
import re
import subprocess
from pathlib import Path
from typing import Any


GRAPH_RAG_GLOBAL_HINTS = {'tendencias', 'visao geral', 'panorama geral', 'corpus inteiro'}
GRAPH_RAG_DRIFT_HINTS = {'explore', 'explorar', 'investigue', 'investigar', 'aprofunde'}


def select_graph_rag_method(message: str) -> str:
    lowered = message.lower()
    if any(term in lowered for term in GRAPH_RAG_DRIFT_HINTS):
        return 'drift'
    if any(term in lowered for term in GRAPH_RAG_GLOBAL_HINTS):
        return 'global'
    return 'local'


def graph_rag_workspace_ready(workspace: str) -> bool:
    root = Path(workspace)
    return (root / 'settings.yaml').exists() and (root / 'output').exists()


def _sanitize_graph_rag_text(text: str) -> str:
    cleaned = re.sub(r'```[\s\S]*?```', '', text).strip()
    cleaned = re.sub(r'\n{3,}', '\n\n', cleaned).strip()
    return cleaned or text.strip()


async def run_graph_rag_query(
    *,
    settings: Any,
    query: str,
) -> dict[str, str] | None:
    workspace = Path(settings.graph_rag_workspace)
    if not graph_rag_workspace_ready(settings.graph_rag_workspace):
        return None

    method = select_graph_rag_method(query)
    command = [
        'uv',
        'run',
        '--project',
        '/workspace/apps/ai-orchestrator',
        'graphrag',
        'query',
        '-r',
        str(workspace),
        '-m',
        method,
        '--response-type',
        settings.graph_rag_response_type,
        query,
    ]
    env = {
        **os.environ,
        'GRAPHRAG_LOCAL_CHAT_API_BASE': settings.graph_rag_local_chat_api_base,
        'GRAPHRAG_LOCAL_EMBEDDING_API_BASE': settings.graph_rag_local_embedding_api_base,
        'GRAPHRAG_LOCAL_CHAT_API_KEY': settings.graph_rag_local_chat_api_key,
        'GRAPHRAG_LOCAL_EMBEDDING_API_KEY': settings.graph_rag_local_embedding_api_key,
    }

    try:
        result = await asyncio.to_thread(
            subprocess.run,
            command,
            cwd='/workspace',
            env=env,
            text=True,
            capture_output=True,
            timeout=45,
            check=False,
        )
    except Exception:
        return None

    text = result.stdout.strip()
    if result.returncode != 0 or not text:
        return None
    return {
        'method': method,
        'text': _sanitize_graph_rag_text(text),
    }
