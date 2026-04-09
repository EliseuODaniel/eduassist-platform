from __future__ import annotations

import asyncio

import pytest

from ai_orchestrator.service_settings import Settings
from ai_orchestrator.stack_postprocessing import postprocess_stack_response
from ai_orchestrator.stack_runtime_profiles import build_stack_local_settings
from ai_orchestrator.models import (
    AccessTier,
    ConversationChannel,
    IntentClassification,
    MessageResponse,
    MessageResponseRequest,
    OrchestrationMode,
    QueryDomain,
    RetrievalBackend,
    UserContext,
)


def _settings() -> Settings:
    return Settings.model_construct(
        app_env='development',
        internal_api_token='dev-internal-token',
        openai_model='gpt-5.4',
        google_model='gemini-2.5-flash-lite',
        feature_flag_answer_experience_enabled=True,
        feature_flag_context_repair_enabled=True,
        feature_flag_final_polish_enabled=True,
        feature_flag_final_polish_public_enabled=True,
        feature_flag_final_polish_protected_enabled=True,
        candidate_chooser_enabled=True,
        public_response_cache_enabled=True,
        strict_framework_isolation_enabled=False,
    )


def _request() -> MessageResponseRequest:
    return MessageResponseRequest(
        message='teste',
        channel=ConversationChannel.telegram,
        user=UserContext(role='anonymous', authenticated=False),
    )


def _response() -> MessageResponse:
    return MessageResponse(
        message_text='resposta',
        mode=OrchestrationMode.structured_tool,
        classification=IntentClassification(
            domain=QueryDomain.institution,
            access_tier=AccessTier.public,
            confidence=1.0,
            reason='test',
        ),
        retrieval_backend=RetrievalBackend.none,
        reason='test',
    )


def test_stack_local_settings_keep_quality_stabilizers_under_framework_isolation() -> None:
    base = _settings()
    isolated = build_stack_local_settings(base_settings=base, stack_name='langgraph')

    assert isolated.feature_flag_answer_experience_enabled is True
    assert isolated.feature_flag_context_repair_enabled is True
    assert isolated.feature_flag_final_polish_enabled is True
    assert isolated.candidate_chooser_enabled is True
    assert isolated.public_response_cache_enabled is True
    assert isolated.strict_framework_isolation_enabled is True


def test_stack_local_postprocess_delegates_to_grounded_answer_experience(monkeypatch: pytest.MonkeyPatch) -> None:
    response = _response()

    async def fake_apply_grounded_answer_experience(*, request, response, settings, stack_name):
        assert request == _request()
        assert settings.internal_api_token == 'dev-internal-token'
        assert stack_name == 'python_functions'
        return response.model_copy(update={'answer_experience_eligible': True, 'message_text': 'resposta melhor'})

    monkeypatch.setattr(
        'ai_orchestrator.stack_postprocessing.apply_grounded_answer_experience',
        fake_apply_grounded_answer_experience,
    )

    updated = asyncio.run(
        postprocess_stack_response(
            stack_name='python_functions',
            request=_request(),
            response=response,
            settings=_settings(),
        )
    )
    assert updated.message_text == 'resposta melhor'
    assert updated.answer_experience_eligible is True
