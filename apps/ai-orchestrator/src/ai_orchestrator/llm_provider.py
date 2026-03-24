from __future__ import annotations

from typing import Any

import httpx
from openai import AsyncOpenAI

from .models import CalendarEventCard, MessageResponseCitation


def _build_context_sections(
    *,
    request_message: str,
    preview: Any,
    citations: list[MessageResponseCitation],
    calendar_events: list[CalendarEventCard],
) -> tuple[str, str]:
    snippets = '\n\n'.join(
        f'Fonte {index}: {citation.document_title} ({citation.version_label})\nTrecho: {citation.excerpt}'
        for index, citation in enumerate(citations, start=1)
    )
    calendar_context = '\n'.join(
        f'- {event.title}: {event.description or "sem descricao"} '
        f'({event.starts_at.isoformat()} -> {event.ends_at.isoformat()})'
        for event in calendar_events[:4]
    )
    instructions = (
        'Voce e o assistente EduAssist de uma escola de ensino medio. '
        'Responda em portugues do Brasil, de forma objetiva e educada. '
        'Use apenas o contexto fornecido. Nao invente regras, datas, documentos ou horarios. '
        'Nao transforme listas de requisitos em afirmacoes sobre itens dispensaveis ou desnecessarios. '
        'Quando a pergunta for negativa, de exclusao, excecao ou complemento, so responda esse ponto '
        'se o contexto disser isso explicitamente. '
        'Se a pergunta exigir autenticacao, diga isso com clareza. '
        'Se houver calendario estruturado, priorize-o. '
        'Se o contexto nao responder a pergunta, diga explicitamente que a base atual nao tem evidencia suficiente. '
        'Nao cite fontes inline; elas serao anexadas depois.'
    )
    prompt = (
        f'Pergunta do usuario:\n{request_message}\n\n'
        f'Roteamento:\n- modo: {preview.mode.value}\n'
        f'- dominio: {preview.classification.domain.value}\n'
        f'- autenticacao necessaria: {preview.needs_authentication}\n\n'
        f'Eventos estruturados:\n{calendar_context or "nenhum"}\n\n'
        f'Trechos citaveis:\n{snippets or "nenhum"}'
    )
    return instructions, prompt


async def compose_with_openai(
    *,
    settings: Any,
    request_message: str,
    preview: Any,
    citations: list[MessageResponseCitation],
    calendar_events: list[CalendarEventCard],
) -> str | None:
    if settings.llm_provider != 'openai' or not settings.openai_api_key:
        return None

    instructions, prompt = _build_context_sections(
        request_message=request_message,
        preview=preview,
        citations=citations,
        calendar_events=calendar_events,
    )

    try:
        client = AsyncOpenAI(api_key=settings.openai_api_key, base_url=settings.openai_base_url)
        response = await client.responses.create(
            model=settings.openai_model,
            instructions=instructions,
            input=prompt,
        )
        text = (response.output_text or '').strip()
        return text or None
    except Exception:
        return None


async def compose_with_google(
    *,
    settings: Any,
    request_message: str,
    preview: Any,
    citations: list[MessageResponseCitation],
    calendar_events: list[CalendarEventCard],
) -> str | None:
    if settings.llm_provider not in {'google', 'gemini'} or not settings.google_api_key:
        return None

    instructions, prompt = _build_context_sections(
        request_message=request_message,
        preview=preview,
        citations=citations,
        calendar_events=calendar_events,
    )
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
        'generationConfig': {
            'temperature': 0.2,
            'maxOutputTokens': 700,
        },
    }
    endpoint = f"{settings.google_api_base_url.rstrip('/')}/models/{settings.google_model}:generateContent"
    headers = {
        'Content-Type': 'application/json',
        'x-goog-api-key': settings.google_api_key,
    }

    try:
        async with httpx.AsyncClient(timeout=25.0) as client:
            response = await client.post(endpoint, headers=headers, json=payload)
        response.raise_for_status()
        body = response.json()
    except Exception:
        return None

    candidates = body.get('candidates')
    if not isinstance(candidates, list) or not candidates:
        return None
    content = candidates[0].get('content')
    if not isinstance(content, dict):
        return None
    parts = content.get('parts')
    if not isinstance(parts, list):
        return None
    texts = [part.get('text', '').strip() for part in parts if isinstance(part, dict)]
    merged = '\n'.join(text for text in texts if text)
    return merged or None


async def compose_with_provider(
    *,
    settings: Any,
    request_message: str,
    preview: Any,
    citations: list[MessageResponseCitation],
    calendar_events: list[CalendarEventCard],
) -> str | None:
    if settings.llm_provider == 'openai':
        return await compose_with_openai(
            settings=settings,
            request_message=request_message,
            preview=preview,
            citations=citations,
            calendar_events=calendar_events,
        )
    if settings.llm_provider in {'google', 'gemini'}:
        return await compose_with_google(
            settings=settings,
            request_message=request_message,
            preview=preview,
            citations=citations,
            calendar_events=calendar_events,
        )
    return None
