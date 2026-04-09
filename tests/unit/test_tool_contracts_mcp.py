from __future__ import annotations

import importlib

from fastapi.testclient import TestClient

from ai_orchestrator.tools import get_mcp_tool_descriptors


def _load_runtime_main(monkeypatch):
    monkeypatch.setenv('INTERNAL_API_TOKEN', 'real-token')
    monkeypatch.setenv('ALLOW_INSECURE_INTERNAL_API_TOKEN', 'false')
    import ai_orchestrator.main as runtime_main

    return importlib.reload(runtime_main)


def test_mcp_tool_descriptors_expose_expected_shape() -> None:
    descriptors = get_mcp_tool_descriptors()
    assert descriptors
    first = descriptors[0]
    assert isinstance(first.get('name'), str) and first['name']
    assert isinstance(first.get('description'), str) and first['description']
    assert isinstance(first.get('inputSchema'), dict)
    annotations = first.get('annotations')
    assert isinstance(annotations, dict)
    assert 'readOnlyHint' in annotations
    eduassist_meta = first.get('eduassistMeta')
    assert isinstance(eduassist_meta, dict)
    assert 'accessTier' in eduassist_meta


def test_mcp_tools_endpoint_returns_catalog(monkeypatch) -> None:
    runtime_main = _load_runtime_main(monkeypatch)
    monkeypatch.setattr(runtime_main, '_warm_retrieval_service', lambda _settings: None)
    monkeypatch.setattr(runtime_main, '_warm_langgraph_service', lambda _settings: None)
    monkeypatch.setattr(runtime_main, 'close_langgraph_runtime', lambda: None)

    with TestClient(runtime_main.app) as client:
        response = client.get('/v1/mcp/tools')
    assert response.status_code == 200
    body = response.json()
    assert body['service'] == 'ai-orchestrator'
    assert body['count'] >= 1
    assert isinstance(body['tools'], list) and body['tools']
