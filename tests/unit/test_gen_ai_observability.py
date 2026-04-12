from __future__ import annotations

from types import SimpleNamespace

from eduassist_observability import (
    estimate_gen_ai_cost_usd,
    extract_google_usage,
    extract_openai_usage,
    normalize_gen_ai_provider_name,
)


def test_normalize_gen_ai_provider_name_maps_google_and_self_hosted() -> None:
    assert (
        normalize_gen_ai_provider_name(
            'google', base_url='https://generativelanguage.googleapis.com/v1beta'
        )
        == 'gcp.gen_ai'
    )
    assert (
        normalize_gen_ai_provider_name('openai', base_url='http://local-llm-gemma4e4b:8080/v1')
        == 'self_hosted'
    )
    assert (
        normalize_gen_ai_provider_name('openai', base_url='https://api.openai.com/v1') == 'openai'
    )


def test_estimate_gen_ai_cost_usd_uses_current_gemini_flash_lite_baseline() -> None:
    estimated = estimate_gen_ai_cost_usd(
        provider_name='gcp.gen_ai',
        request_model='gemini-2.5-flash-lite',
        input_tokens=2000,
        output_tokens=500,
    )
    assert estimated is not None
    assert round(estimated, 8) == 0.0002


def test_extract_google_usage_reads_usage_metadata_and_cost() -> None:
    usage = extract_google_usage(
        {
            'modelVersion': 'gemini-2.5-flash-lite',
            'usageMetadata': {
                'promptTokenCount': 120,
                'candidatesTokenCount': 30,
                'totalTokenCount': 150,
            },
            'candidates': [
                {'finishReason': 'STOP'},
            ],
        },
        request_model='gemini-2.5-flash-lite',
    )

    assert usage.input_tokens == 120
    assert usage.output_tokens == 30
    assert usage.total_tokens == 150
    assert usage.response_model == 'gemini-2.5-flash-lite'
    assert usage.finish_reasons == ('stop',)
    assert usage.estimated_cost_usd is not None


def test_extract_openai_usage_reads_chat_completion_shape() -> None:
    response = SimpleNamespace(
        model='ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M',
        id='resp_local_1',
        usage=SimpleNamespace(prompt_tokens=90, completion_tokens=25, total_tokens=115),
        choices=[SimpleNamespace(finish_reason='stop')],
    )

    usage = extract_openai_usage(
        response,
        request_model='ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M',
        provider_name='self_hosted',
    )

    assert usage.input_tokens == 90
    assert usage.output_tokens == 25
    assert usage.total_tokens == 115
    assert usage.response_model == 'ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M'
    assert usage.response_id == 'resp_local_1'
    assert usage.finish_reasons == ('stop',)
    assert usage.estimated_cost_usd == 0.0
