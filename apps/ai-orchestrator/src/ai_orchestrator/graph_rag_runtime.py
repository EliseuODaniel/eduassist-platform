from __future__ import annotations

import asyncio
import os
import re
import subprocess
from pathlib import Path
from typing import Any


GRAPH_RAG_GLOBAL_HINTS = {'tendencias', 'visao geral', 'panorama geral', 'corpus inteiro'}
GRAPH_RAG_DRIFT_HINTS = {'explore', 'explorar', 'investigue', 'investigar', 'aprofunde'}
GRAPH_RAG_COMPARATIVE_HINTS = {
    'compare',
    'comparacao',
    'comparativo',
    'relacione',
    'sintetize',
    'cruze',
    'mapeie',
    'explique como',
    'temas atravessam',
    'o que uma familia precisa entender',
    'uma unica explicacao coerente',
    'quando cruzamos',
    'guia de sobrevivencia do primeiro mes',
    'primeiro mes',
    'primeiro mês',
    'regras e prazos',
    'muito esquecido',
    'de ponta a ponta',
    'do ponto de vista financeiro e administrativo',
}


def _normalize_graph_rag_message(message: str) -> str:
    return re.sub(r'\s+', ' ', str(message or '').lower()).strip()


def select_graph_rag_method(message: str) -> str:
    lowered = _normalize_graph_rag_message(message)
    if any(term in lowered for term in GRAPH_RAG_DRIFT_HINTS):
        return 'drift'
    if any(term in lowered for term in GRAPH_RAG_COMPARATIVE_HINTS):
        return 'global'
    if any(term in lowered for term in GRAPH_RAG_GLOBAL_HINTS):
        return 'global'
    return 'local'


def _graph_rag_method_timeouts() -> dict[str, int]:
    return {
        'local': 50,
        'global': 90,
        'drift': 150,
    }


def _graph_rag_method_attempts(primary_method: str) -> tuple[str, ...]:
    if primary_method == 'drift':
        return ('drift', 'global', 'local')
    if primary_method == 'global':
        return ('global', 'drift', 'local')
    return ('local', 'global')


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

    primary_method = select_graph_rag_method(query)
    env = {
        **os.environ,
        'GRAPHRAG_LOCAL_CHAT_API_BASE': settings.graph_rag_local_chat_api_base,
        'GRAPHRAG_LOCAL_EMBEDDING_API_BASE': settings.graph_rag_local_embedding_api_base,
        'GRAPHRAG_LOCAL_CHAT_API_KEY': settings.graph_rag_local_chat_api_key,
        'GRAPHRAG_LOCAL_EMBEDDING_API_KEY': settings.graph_rag_local_embedding_api_key,
    }

    attempted_methods: list[str] = []
    timeouts = _graph_rag_method_timeouts()
    for method in _graph_rag_method_attempts(primary_method):
        attempted_methods.append(method)
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
        try:
            result = await asyncio.to_thread(
                subprocess.run,
                command,
                cwd='/workspace',
                env=env,
                text=True,
                capture_output=True,
                timeout=timeouts.get(method, 60),
                check=False,
            )
        except Exception:
            continue

        text = result.stdout.strip()
        if result.returncode != 0 or not text:
            continue
        return {
            'method': method,
            'requested_method': primary_method,
            'attempted_methods': attempted_methods,
            'fallback_used': method != primary_method,
            'text': _sanitize_graph_rag_text(text),
        }
    return None
