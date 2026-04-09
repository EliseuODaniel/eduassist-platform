from __future__ import annotations

import importlib

from fastapi.testclient import TestClient

from ai_orchestrator.models import MessageResponse


def _load_runtime_main(monkeypatch):
    monkeypatch.setenv('INTERNAL_API_TOKEN', 'real-token')
    monkeypatch.setenv('ALLOW_INSECURE_INTERNAL_API_TOKEN', 'false')
    import ai_orchestrator.main as runtime_main

    return importlib.reload(runtime_main)


def _build_request() -> dict[str, object]:
    return {
        'message': 'oi',
        'telegram_chat_id': 1649845499,
    }


def test_control_plane_blocks_direct_serving_when_disabled(monkeypatch) -> None:
    runtime_main = _load_runtime_main(monkeypatch)
    settings = runtime_main.Settings(
        internal_api_token='real-token',
        control_plane_allow_direct_serving=False,
        app_env='test',
    )
    monkeypatch.setattr(runtime_main, 'get_settings', lambda: settings)
    monkeypatch.setattr(runtime_main, '_warm_retrieval_service', lambda _settings: None)
    monkeypatch.setattr(runtime_main, '_warm_langgraph_service', lambda _settings: None)
    monkeypatch.setattr(runtime_main, 'close_langgraph_runtime', lambda: None)

    with TestClient(runtime_main.app) as client:
        response = client.post(
            '/v1/messages/respond',
            headers={'X-Internal-Api-Token': 'real-token'},
            json=_build_request(),
        )

    assert response.status_code == 503
    body = response.json()
    assert body['detail']['code'] == 'control_plane_direct_serving_disabled'
    assert 'dedicated stack runtime' in body['detail']['message'].lower()
    assert body['detail']['recommendedTargets']['python_functions'] in {
        'http://ai-orchestrator-python-functions:8000',
        'http://127.0.0.1:8007',
    }


def test_control_plane_can_proxy_direct_serving_when_explicitly_enabled(monkeypatch) -> None:
    runtime_main = _load_runtime_main(monkeypatch)
    settings = runtime_main.Settings(
        internal_api_token='real-token',
        control_plane_allow_direct_serving=True,
        app_env='test',
    )
    monkeypatch.setattr(runtime_main, 'get_settings', lambda: settings)
    monkeypatch.setattr(runtime_main, '_warm_retrieval_service', lambda _settings: None)
    monkeypatch.setattr(runtime_main, '_warm_langgraph_service', lambda _settings: None)
    monkeypatch.setattr(runtime_main, 'close_langgraph_runtime', lambda: None)

    async def _fake_proxy_stack_message_response(*, settings, request) -> MessageResponse:
        return MessageResponse.model_validate(
            {
                'message_text': 'Resposta dedicada ok',
                'mode': 'structured_tool',
                'classification': {
                    'domain': 'institution',
                    'access_tier': 'public',
                    'confidence': 1.0,
                    'reason': 'test',
                },
                'retrieval_backend': 'none',
                'reason': 'test',
            }
        )

    monkeypatch.setattr(runtime_main, '_proxy_stack_message_response', _fake_proxy_stack_message_response)

    with TestClient(runtime_main.app) as client:
        response = client.post(
            '/v1/messages/respond',
            headers={'X-Internal-Api-Token': 'real-token'},
            json=_build_request(),
        )

    assert response.status_code == 200
    body = response.json()
    assert body['message_text'] == 'Resposta dedicada ok'


def test_control_plane_status_exposes_primary_and_compatibility_interfaces(monkeypatch) -> None:
    runtime_main = _load_runtime_main(monkeypatch)
    settings = runtime_main.Settings(
        internal_api_token='real-token',
        control_plane_allow_direct_serving=False,
        app_env='test',
    )
    monkeypatch.setattr(runtime_main, 'get_settings', lambda: settings)
    monkeypatch.setattr(runtime_main, '_warm_retrieval_service', lambda _settings: None)
    monkeypatch.setattr(runtime_main, '_warm_langgraph_service', lambda _settings: None)
    monkeypatch.setattr(runtime_main, 'close_langgraph_runtime', lambda: None)
    monkeypatch.setattr(runtime_main, 'get_langgraph_runtime_status', lambda _settings: {
        'checkpointerConfigured': False,
        'checkpointerInitialized': False,
        'checkpointerBackend': 'none',
        'threadIdEnabled': True,
    })
    monkeypatch.setattr(runtime_main, 'get_scorecard_gate_status', lambda settings: {})
    monkeypatch.setattr(runtime_main, 'get_experiment_rollout_readiness', lambda settings: {})
    monkeypatch.setattr(runtime_main, 'get_experiment_live_promotion_summary', lambda settings: {})
    monkeypatch.setattr(runtime_main, '_experimental_stack_readiness', lambda settings: {})
    monkeypatch.setattr(runtime_main, '_orchestrator_runtime_diagnostics', lambda settings: {})
    monkeypatch.setattr(runtime_main, '_public_runtime_diagnostics_summary', lambda diagnostics: {})

    with TestClient(runtime_main.app) as client:
        response = client.get('/v1/status')

    assert response.status_code == 200
    body = response.json()
    assert body['serviceRole'] == 'control-plane-router'
    assert body['primaryServingRecommended'] is False
    assert '/v1/messages/respond' in body['controlPlaneCompatibilityInterfaces']
    assert '/v1/internal/runtime/*' in body['controlPlanePrimaryInterfaces']
