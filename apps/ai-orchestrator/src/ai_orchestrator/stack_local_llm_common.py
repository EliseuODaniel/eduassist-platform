from __future__ import annotations

from typing import Any

from .llm_provider import (
    _extract_json_object,
    _google_extract_text,
    _google_generate_content_body,
    _google_generation_config,
    _openai_text_call,
)


async def stack_local_text_call(
    *,
    settings: Any,
    instructions: str,
    prompt: str,
    temperature: float,
    max_output_tokens: int,
    top_p: float | None = None,
) -> str | None:
    provider = str(getattr(settings, 'llm_provider', 'openai') or 'openai').strip().lower()
    if provider == 'openai' and getattr(settings, 'openai_api_key', None):
        return await _openai_text_call(
            settings=settings,
            instructions=instructions,
            prompt=prompt,
            temperature=temperature,
            max_output_tokens=max_output_tokens,
            top_p=top_p,
            timeout=20.0,
        )

    if provider in {'google', 'gemini'} and getattr(settings, 'google_api_key', None):
        payload = {
            'system_instruction': {
                'parts': [{'text': instructions}],
            },
            'contents': [
                {
                    'role': 'user',
                    'parts': [{'text': prompt}],
                }
            ],
            'generationConfig': _google_generation_config(
                settings,
                temperature=temperature,
                max_output_tokens=max_output_tokens,
                top_p=top_p,
            ),
        }
        body = await _google_generate_content_body(
            settings=settings,
            payload=payload,
            timeout=20.0,
        )
        if not isinstance(body, dict):
            return None
        merged = _google_extract_text(body)
        return merged or None
    return None


async def stack_local_json_call(
    *,
    settings: Any,
    instructions: str,
    prompt: str,
    temperature: float,
    max_output_tokens: int,
    top_p: float | None = None,
) -> dict[str, Any] | None:
    text = await stack_local_text_call(
        settings=settings,
        instructions=instructions,
        prompt=prompt,
        temperature=temperature,
        max_output_tokens=max_output_tokens,
        top_p=top_p,
    )
    if not text:
        return None
    return _extract_json_object(text)
