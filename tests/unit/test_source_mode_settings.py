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


def test_orchestrator_llm_profile_switches_to_gemini_flash_lite() -> None:
    settings = OrchestratorSettings(
        internal_api_token="real-token",
        llm_model_profile="gemini_flash_lite",
        app_env="test",
    )

    assert settings.llm_provider == "google"
    assert settings.google_model == "gemini-2.5-flash-lite"
    assert settings.answer_experience_provider == "google"
    assert settings.answer_experience_google_model == "gemini-2.5-flash-lite"


def test_orchestrator_llm_profile_switches_to_local_gemma() -> None:
    settings = OrchestratorSettings(
        internal_api_token="real-token",
        llm_model_profile="gemma4e4b_local",
        app_env="test",
    )

    assert settings.llm_provider == "openai"
    assert settings.openai_api_mode == "chat_completions"
    assert settings.openai_api_key == "local-llm"
    assert settings.openai_base_url == "http://local-llm-gemma4e4b:8080/v1"
    assert settings.openai_model == "ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M"
    assert settings.answer_experience_provider == "openai"
    assert settings.answer_experience_openai_api_mode == "chat_completions"


def test_orchestrator_llm_profile_switches_to_local_qwen() -> None:
    settings = OrchestratorSettings(
        internal_api_token="real-token",
        llm_model_profile="qwen3_4b_instruct_local",
        app_env="test",
    )

    assert settings.llm_provider == "openai"
    assert settings.openai_api_mode == "chat_completions"
    assert settings.openai_api_key == "local-llm"
    assert settings.openai_base_url == "http://local-llm-qwen3-4b:8080/v1"
    assert settings.openai_model == "Qwen_Qwen3-4B-Instruct-2507-Q5_K_M.gguf"
    assert settings.answer_experience_provider == "openai"
    assert settings.answer_experience_openai_api_mode == "chat_completions"


def test_specialist_llm_profile_switches_to_local_gemma() -> None:
    settings = SpecialistSettings(
        internal_api_token="real-token",
        llm_model_profile="gemma4e4b_local",
        app_env="test",
    )

    assert settings.llm_provider == "openai"
    assert settings.openai_api_mode == "chat_completions"
    assert settings.openai_api_key == "local-llm"
    assert settings.openai_base_url == "http://local-llm-gemma4e4b:8080/v1"
    assert settings.openai_model == "ggml-org_gemma-4-E4B-it-GGUF_gemma-4-e4b-it-Q4_K_M.gguf"
    assert settings.openai_fast_model == settings.openai_model
    assert settings.openai_reasoning_model == settings.openai_model


def test_specialist_llm_profile_switches_to_local_qwen() -> None:
    settings = SpecialistSettings(
        internal_api_token="real-token",
        llm_model_profile="qwen3_4b_instruct_local",
        app_env="test",
    )

    assert settings.llm_provider == "openai"
    assert settings.openai_api_mode == "chat_completions"
    assert settings.openai_api_key == "local-llm"
    assert settings.openai_base_url == "http://local-llm-qwen3-4b:8080/v1"
    assert settings.openai_model == "Qwen_Qwen3-4B-Instruct-2507-Q5_K_M.gguf"
    assert settings.openai_fast_model == settings.openai_model
    assert settings.openai_reasoning_model == settings.openai_model


def test_specialist_local_gemma_disables_strict_tool_json_outputs() -> None:
    pytest.importorskip("agents")
    from ai_orchestrator_specialist.agent_builders import SpecialistAgentDeps, supports_tool_json_outputs

    settings = SpecialistSettings(
        internal_api_token="real-token",
        llm_model_profile="gemma4e4b_local",
        app_env="test",
    )
    deps = SpecialistAgentDeps(
        resolve_llm_provider=lambda cfg: "openai",
        get_public_profile_bundle=None,
        fetch_academic_policy=None,
        search_public_documents=None,
        search_private_documents=None,
        run_graph_rag_query=None,
        project_public_pricing=None,
        fetch_actor_identity=None,
        fetch_academic_summary=None,
        fetch_upcoming_assessments=None,
        fetch_attendance_timeline=None,
        calculate_grade_requirement=None,
        fetch_financial_summary=None,
        fetch_workflow_status=None,
        create_support_handoff=None,
        create_visit_booking=None,
        update_visit_booking=None,
        create_institutional_request=None,
        update_institutional_request=None,
    )

    assert supports_tool_json_outputs(settings, deps=deps) is False


def test_telegram_webhook_secret_placeholder_is_allowed_in_test_env() -> None:
    gateway = TelegramGatewaySettings(
        internal_api_token="dev-internal-token",
        allow_insecure_internal_api_token=True,
        telegram_webhook_secret="change-me",
        app_env="test",
    )
    assert gateway.telegram_webhook_secret == "change-me"
