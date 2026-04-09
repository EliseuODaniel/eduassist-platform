from __future__ import annotations

from fastapi.testclient import TestClient

from ai_orchestrator.dedicated_stack_app import create_dedicated_stack_app
from ai_orchestrator.service_settings import Settings


def test_dedicated_stack_status_exposes_runtime_diagnostics(monkeypatch) -> None:
    settings = Settings(
        internal_api_token="real-token",
        app_env="test",
    )
    monkeypatch.setattr("ai_orchestrator.dedicated_stack_app.get_settings", lambda: settings)
    monkeypatch.setattr(
        "ai_orchestrator.dedicated_stack_app.build_stack_local_settings",
        lambda *, base_settings, stack_name: base_settings,
    )
    monkeypatch.setattr(
        "ai_orchestrator.dedicated_stack_app._engine_for_stack",
        lambda stack_name: type("ReadyEngine", (), {"ready": True})(),
    )
    monkeypatch.setattr(
        "ai_orchestrator.dedicated_stack_app._dedicated_runtime_diagnostics",
        lambda *, stack_name, settings: {
            "runtimeMode": "source",
            "operationalReadiness": True,
            "sourceContainerDriftRisk": False,
            "checks": [{"name": "api_core", "status": "ok"}],
            "stack": stack_name,
        },
    )

    app = create_dedicated_stack_app(
        stack_name="python_functions",
        service_name="ai-orchestrator-python-functions",
    )
    with TestClient(app) as client:
        response = client.get("/v1/status")

    assert response.status_code == 200
    body = response.json()
    assert body["serviceRole"] == "dedicated-stack-runtime"
    assert body["primaryServingRecommended"] is True
    assert body["runtimeDiagnostics"]["runtimeMode"] == "source"
    assert body["runtimeDiagnostics"]["sourceContainerDriftRisk"] is False
