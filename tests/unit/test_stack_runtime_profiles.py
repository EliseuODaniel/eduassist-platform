from __future__ import annotations

import asyncio
from types import SimpleNamespace

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


def test_stack_postprocess_applies_answer_surface_refiner_after_grounded_answer_experience(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    response = _response()

    async def fake_apply_grounded_answer_experience(*, request, response, settings, stack_name):
        return response.model_copy(
            update={
                'message_text': 'A biblioteca funciona de segunda a sexta, das 7h30 às 18h00.',
                'answer_experience_eligible': True,
                'answer_experience_reason': 'python_functions_native_contextual_public_answer',
            }
        )

    async def fake_refine_answer_surface_with_provider(**kwargs):
        assert kwargs['stack_label'] == 'python_functions'
        assert kwargs['request_message'] == 'teste'
        return SimpleNamespace(
            answer_text='A biblioteca fecha às 18h00.',
            used_llm=True,
            changed=True,
            preserved_fallback=False,
            reason='answer_surface_refiner',
        )

    monkeypatch.setattr(
        'ai_orchestrator.stack_postprocessing.apply_grounded_answer_experience',
        fake_apply_grounded_answer_experience,
    )
    monkeypatch.setattr(
        'ai_orchestrator.stack_answer_surface_refiner.refine_answer_surface_with_provider',
        fake_refine_answer_surface_with_provider,
    )

    updated = asyncio.run(
        postprocess_stack_response(
            stack_name='python_functions',
            request=_request(),
            response=response,
            settings=_settings(),
        )
    )

    assert updated.message_text == 'A biblioteca fecha às 18h00.'
    assert updated.used_llm is True
    assert 'answer_surface_refiner' in updated.llm_stages
    assert updated.answer_experience_reason.endswith('answer_surface_refiner')


def test_stack_postprocess_preserves_original_text_when_surface_refiner_is_disabled(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    response = _response()
    settings = _settings().model_copy(
        update={'feature_flag_answer_surface_refiner_enabled': False}
    )

    async def fake_apply_grounded_answer_experience(*, request, response, settings, stack_name):
        return response.model_copy(
            update={
                'message_text': 'Seu protocolo é ATD-20260417-ABCD1234.',
                'answer_experience_eligible': True,
                'answer_experience_reason': 'public_service_ticket',
            }
        )

    async def fake_refine_answer_surface_with_provider(**kwargs):
        raise AssertionError('surface refiner should not run when disabled')

    monkeypatch.setattr(
        'ai_orchestrator.stack_postprocessing.apply_grounded_answer_experience',
        fake_apply_grounded_answer_experience,
    )
    monkeypatch.setattr(
        'ai_orchestrator.stack_answer_surface_refiner.refine_answer_surface_with_provider',
        fake_refine_answer_surface_with_provider,
    )

    updated = asyncio.run(
        postprocess_stack_response(
            stack_name='python_functions',
            request=_request(),
            response=response,
            settings=settings,
        )
    )

    assert updated.message_text == 'Seu protocolo é ATD-20260417-ABCD1234.'
    assert updated.llm_stages == []


def test_stack_postprocess_records_surface_refiner_stage_when_candidate_is_rejected(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    response = _response()
    protocol_text = 'Seu protocolo é ATD-20260417-ABCD1234.'

    async def fake_apply_grounded_answer_experience(*, request, response, settings, stack_name):
        return response.model_copy(
            update={
                'message_text': protocol_text,
                'answer_experience_eligible': True,
                'answer_experience_reason': 'public_service_ticket',
            }
        )

    async def fake_refine_answer_surface_with_provider(**kwargs):
        return SimpleNamespace(
            answer_text=protocol_text,
            used_llm=True,
            changed=False,
            preserved_fallback=True,
            reason='validation_rejected',
        )

    monkeypatch.setattr(
        'ai_orchestrator.stack_postprocessing.apply_grounded_answer_experience',
        fake_apply_grounded_answer_experience,
    )
    monkeypatch.setattr(
        'ai_orchestrator.stack_answer_surface_refiner.refine_answer_surface_with_provider',
        fake_refine_answer_surface_with_provider,
    )

    updated = asyncio.run(
        postprocess_stack_response(
            stack_name='python_functions',
            request=_request(),
            response=response,
            settings=_settings(),
        )
    )

    assert updated.message_text == protocol_text
    assert updated.used_llm is True
    assert 'answer_surface_refiner' in updated.llm_stages
    assert updated.answer_experience_reason.endswith('validation_rejected')
