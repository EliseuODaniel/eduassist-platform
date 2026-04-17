from __future__ import annotations

import asyncio
from types import SimpleNamespace

from ai_orchestrator import llm_provider


def _settings(**overrides) -> SimpleNamespace:
    base = dict(
        openai_api_key='local-llm',
        openai_base_url='http://local-llm-gemma4e4b:8080/v1',
        openai_model='ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M',
        openai_api_mode='chat_completions',
        llm_provider='openai',
    )
    base.update(overrides)
    return SimpleNamespace(**base)


def test_openai_api_mode_uses_chat_completions_for_local_openai_compatible_auto() -> None:
    settings = _settings(openai_api_mode='auto')
    assert llm_provider._openai_api_mode(settings) == 'chat_completions'


def test_openai_text_call_uses_chat_completions_for_local_mode(monkeypatch) -> None:
    calls: list[dict[str, object]] = []

    class _FakeChatCompletions:
        async def create(self, **kwargs):
            calls.append(kwargs)
            return SimpleNamespace(
                choices=[
                    SimpleNamespace(message=SimpleNamespace(content='Resposta local do Gemma'))
                ]
            )

    class _FakeClient:
        def __init__(self, *args, **kwargs):
            self.chat = SimpleNamespace(completions=_FakeChatCompletions())

    monkeypatch.setattr(llm_provider, 'AsyncOpenAI', _FakeClient)

    text = asyncio.run(
        llm_provider._openai_text_call(
            settings=_settings(),
            instructions='Responda em portugues.',
            prompt='Diga oi',
            temperature=0.2,
            max_output_tokens=64,
            top_p=0.9,
            timeout=5.0,
        )
    )

    assert text == 'Resposta local do Gemma'
    assert calls
    call = calls[0]
    assert call['model'] == 'ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M'
    assert call['messages'][0]['role'] == 'system'
    assert call['messages'][1]['role'] == 'user'
    assert call['max_tokens'] == 64


def test_compose_with_openai_works_in_local_chat_completions_mode(monkeypatch) -> None:
    calls: list[dict[str, object]] = []

    class _FakeChatCompletions:
        async def create(self, **kwargs):
            calls.append(kwargs)
            return SimpleNamespace(
                choices=[
                    SimpleNamespace(message=SimpleNamespace(content='Resposta grounded local'))
                ]
            )

    class _FakeClient:
        def __init__(self, *args, **kwargs):
            self.chat = SimpleNamespace(completions=_FakeChatCompletions())

    monkeypatch.setattr(llm_provider, 'AsyncOpenAI', _FakeClient)

    preview = SimpleNamespace(
        mode=SimpleNamespace(value='structured_tool'),
        classification=SimpleNamespace(domain=SimpleNamespace(value='institution')),
        needs_authentication=False,
    )
    text = asyncio.run(
        llm_provider.compose_with_openai(
            settings=_settings(),
            request_message='Qual o endereco da escola?',
            analysis_message='Qual o endereco da escola?',
            preview=preview,
            citations=[],
            calendar_events=[],
            conversation_context=None,
            school_profile={'school_name': 'Colegio Horizonte'},
            context_pack='Endereco oficial em Sao Paulo.',
        )
    )

    assert text == 'Resposta grounded local'
    assert calls


def test_openai_text_call_uses_chat_completions_for_local_qwen_mode(monkeypatch) -> None:
    calls: list[dict[str, object]] = []

    class _FakeChatCompletions:
        async def create(self, **kwargs):
            calls.append(kwargs)
            return SimpleNamespace(
                choices=[
                    SimpleNamespace(message=SimpleNamespace(content='Resposta local do Qwen'))
                ]
            )

    class _FakeClient:
        def __init__(self, *args, **kwargs):
            self.chat = SimpleNamespace(completions=_FakeChatCompletions())

    monkeypatch.setattr(llm_provider, 'AsyncOpenAI', _FakeClient)

    text = asyncio.run(
        llm_provider._openai_text_call(
            settings=_settings(
                openai_base_url='http://local-llm-qwen3-4b:8080/v1',
                openai_model='Qwen_Qwen3-4B-Instruct-2507-Q5_K_M.gguf',
            ),
            instructions='Responda em portugues.',
            prompt='Diga oi',
            temperature=0.2,
            max_output_tokens=64,
            top_p=0.9,
            timeout=5.0,
        )
    )

    assert text == 'Resposta local do Qwen'
    assert calls
    call = calls[0]
    assert call['model'] == 'Qwen_Qwen3-4B-Instruct-2507-Q5_K_M.gguf'
    assert call['messages'][0]['role'] == 'system'
    assert call['messages'][1]['role'] == 'user'
