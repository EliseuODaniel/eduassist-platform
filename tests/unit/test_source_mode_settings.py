from __future__ import annotations

import pytest

from api_core.config import Settings as ApiCoreSettings
from ai_orchestrator.service_settings import Settings as OrchestratorSettings
from ai_orchestrator_specialist.main import Settings as SpecialistSettings
from telegram_gateway.main import Settings as TelegramGatewaySettings


def test_orchestrator_settings_normalize_compose_hosts_in_source_mode(monkeypatch) -> None:
    monkeypatch.setattr("ai_orchestrator.service_settings.detect_runtime_mode", lambda: "source")
    settings = OrchestratorSettings(
        api_core_url="http://api-core:8000",
        database_url="postgresql://eduassist:eduassist@postgres:5432/eduassist",
        qdrant_url="http://qdrant:6333",
        langgraph_orchestrator_url="http://ai-orchestrator-langgraph:8000",
        python_functions_orchestrator_url="http://ai-orchestrator-python-functions:8000",
        llamaindex_orchestrator_url="http://ai-orchestrator-llamaindex:8000",
    )

    assert settings.api_core_url == "http://127.0.0.1:8001"
    assert settings.database_url == "postgresql://eduassist:eduassist@127.0.0.1:5432/eduassist"
    assert settings.qdrant_url == "http://127.0.0.1:6333"
    assert settings.langgraph_orchestrator_url == "http://127.0.0.1:8006"
    assert settings.python_functions_orchestrator_url == "http://127.0.0.1:8007"
    assert settings.llamaindex_orchestrator_url == "http://127.0.0.1:8008"


def test_orchestrator_settings_respect_local_env_overrides(monkeypatch) -> None:
    monkeypatch.setattr("ai_orchestrator.service_settings.detect_runtime_mode", lambda: "source")
    monkeypatch.setenv("API_CORE_URL_LOCAL", "http://127.0.0.1:9001")
    monkeypatch.setenv("DATABASE_URL_LOCAL", "postgresql://eduassist:eduassist@127.0.0.1:9543/eduassist")
    monkeypatch.setenv("QDRANT_URL_LOCAL", "http://127.0.0.1:9633")

    settings = OrchestratorSettings(
        api_core_url="http://api-core:8000",
        database_url="postgresql://eduassist:eduassist@postgres:5432/eduassist",
        qdrant_url="http://qdrant:6333",
    )

    assert settings.api_core_url == "http://127.0.0.1:9001"
    assert settings.database_url == "postgresql://eduassist:eduassist@127.0.0.1:9543/eduassist"
    assert settings.qdrant_url == "http://127.0.0.1:9633"


def test_specialist_settings_normalize_compose_hosts_and_workspace_memory_in_source_mode(monkeypatch) -> None:
    monkeypatch.setattr("ai_orchestrator_specialist.main.detect_runtime_mode", lambda: "source")

    settings = SpecialistSettings(
        api_core_url="http://api-core:8000",
        orchestrator_url="http://ai-orchestrator:8000",
        database_url="postgresql://eduassist:eduassist@postgres:5432/eduassist",
        agent_memory_url="sqlite+aiosqlite:////workspace/.runtime/specialist_supervisor_memory.db",
        qdrant_url="http://qdrant:6333",
    )

    assert settings.api_core_url == "http://127.0.0.1:8001"
    assert settings.orchestrator_url == "http://127.0.0.1:8002"
    assert settings.database_url == "postgresql://eduassist:eduassist@127.0.0.1:5432/eduassist"
    assert settings.qdrant_url == "http://127.0.0.1:6333"
    assert settings.agent_memory_url.startswith("sqlite+aiosqlite:///")
    assert "/workspace/" not in settings.agent_memory_url


def test_specialist_settings_accept_explicit_control_plane_url(monkeypatch) -> None:
    monkeypatch.setattr("ai_orchestrator_specialist.main.detect_runtime_mode", lambda: "source")

    settings = SpecialistSettings(
        api_core_url="http://api-core:8000",
        orchestrator_url="http://should-not-win:8000",
        control_plane_orchestrator_url="http://ai-orchestrator:8000",
        database_url="postgresql://eduassist:eduassist@postgres:5432/eduassist",
        agent_memory_url="sqlite+aiosqlite:////workspace/.runtime/specialist_supervisor_memory.db",
        qdrant_url="http://qdrant:6333",
    )

    assert settings.orchestrator_url == "http://127.0.0.1:8002"
    assert settings.control_plane_orchestrator_url == "http://127.0.0.1:8002"


def test_internal_token_placeholder_is_rejected_by_default() -> None:
    with pytest.raises(ValueError, match="internal_api_token must be set"):
        OrchestratorSettings(internal_api_token="dev-internal-token", app_env="development")
    with pytest.raises(ValueError, match="internal_api_token must be set"):
        ApiCoreSettings(internal_api_token="change-me-internal-token", app_env="development")
    with pytest.raises(ValueError, match="internal_api_token must be set"):
        SpecialistSettings(internal_api_token="dev-internal-token", app_env="development")
    with pytest.raises(ValueError, match="internal_api_token must be set"):
        TelegramGatewaySettings(internal_api_token="dev-internal-token", app_env="development")
    with pytest.raises(ValueError, match="telegram_webhook_secret must be set"):
        TelegramGatewaySettings(
            internal_api_token="real-token",
            telegram_webhook_secret="change-me",
            app_env="development",
        )


def test_internal_token_placeholder_can_be_explicitly_allowed_for_isolated_tests() -> None:
    orchestrator = OrchestratorSettings(
        internal_api_token="dev-internal-token",
        allow_insecure_internal_api_token=True,
        app_env="development",
    )
    api_core = ApiCoreSettings(
        internal_api_token="change-me-internal-token",
        allow_insecure_internal_api_token=True,
        app_env="development",
    )
    specialist = SpecialistSettings(
        internal_api_token="dev-internal-token",
        allow_insecure_internal_api_token=True,
        app_env="development",
    )
    gateway = TelegramGatewaySettings(
        internal_api_token="dev-internal-token",
        allow_insecure_internal_api_token=True,
        telegram_webhook_secret="real-webhook-secret",
        app_env="development",
    )

    assert orchestrator.internal_api_token == "dev-internal-token"
    assert api_core.internal_api_token == "change-me-internal-token"
    assert specialist.internal_api_token == "dev-internal-token"
    assert gateway.internal_api_token == "dev-internal-token"


def test_control_plane_direct_serving_is_disabled_by_default_and_can_be_enabled() -> None:
    default_settings = OrchestratorSettings(
        internal_api_token="real-token",
        app_env="development",
    )
    enabled_settings = OrchestratorSettings(
        internal_api_token="real-token",
        control_plane_allow_direct_serving=True,
        app_env="development",
    )

    assert default_settings.control_plane_allow_direct_serving is False
    assert enabled_settings.control_plane_allow_direct_serving is True


def test_telegram_webhook_secret_placeholder_is_allowed_in_test_env() -> None:
    gateway = TelegramGatewaySettings(
        internal_api_token="dev-internal-token",
        allow_insecure_internal_api_token=True,
        telegram_webhook_secret="change-me",
        app_env="test",
    )
    assert gateway.telegram_webhook_secret == "change-me"
