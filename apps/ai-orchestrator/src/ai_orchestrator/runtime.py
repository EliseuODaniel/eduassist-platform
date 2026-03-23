from __future__ import annotations

from datetime import date, timedelta
from typing import Any

import httpx
from openai import AsyncOpenAI

from .graph import build_orchestration_graph, to_preview
from .models import (
    CalendarEventCard,
    MessageResponse,
    MessageResponseCitation,
    MessageResponseRequest,
    OrchestrationMode,
    OrchestrationRequest,
    QueryDomain,
    RetrievalBackend,
)
from .retrieval import get_retrieval_service


DEFAULT_PUBLIC_HELP = (
    'Posso ajudar com informacoes publicas da escola, como calendario, matricula, '
    'documentos exigidos e regras de atendimento digital.'
)


def _map_request(request: MessageResponseRequest) -> OrchestrationRequest:
    return OrchestrationRequest(
        message=request.message,
        conversation_id=request.conversation_id,
        user=request.user,
        allow_graph_rag=request.allow_graph_rag,
        allow_handoff=request.allow_handoff,
    )


def _category_for_domain(domain: QueryDomain) -> str | None:
    if domain is QueryDomain.calendar:
        return 'calendar'
    return None


def _collect_citations(hits: list[Any], limit: int = 3) -> list[MessageResponseCitation]:
    citations: list[MessageResponseCitation] = []
    seen: set[tuple[str, str]] = set()
    for hit in hits:
        document_key = (hit.citation.document_title, hit.citation.version_label)
        if document_key in seen:
            continue
        citations.append(
            MessageResponseCitation(
                document_title=hit.citation.document_title,
                version_label=hit.citation.version_label,
                storage_path=hit.citation.storage_path,
                chunk_id=hit.citation.chunk_id,
                excerpt=hit.text_excerpt,
            )
        )
        seen.add(document_key)
        if len(citations) >= limit:
            break
    return citations


def _render_source_lines(citations: list[MessageResponseCitation]) -> str:
    if not citations:
        return ''
    lines = ['Fontes:']
    for citation in citations:
        lines.append(f'- {citation.document_title} ({citation.version_label})')
    return '\n'.join(lines)


def _format_event_line(event: CalendarEventCard) -> str:
    start = event.starts_at.astimezone().strftime('%d/%m/%Y %H:%M')
    end = event.ends_at.astimezone().strftime('%d/%m/%Y %H:%M')
    if event.description:
        return f'- {start} a {end}: {event.title}. {event.description}'
    return f'- {start} a {end}: {event.title}'


def _compose_deterministic_answer(
    *,
    request: MessageResponseRequest,
    preview: Any,
    retrieval_hits: list[Any],
    citations: list[MessageResponseCitation],
    calendar_events: list[CalendarEventCard],
) -> str:
    if preview.mode is OrchestrationMode.deny:
        return (
            'Essa consulta depende de autenticacao e vinculo da sua conta no Telegram. '
            'Use o portal da escola para gerar o codigo de vinculacao e depois envie o comando '
            '`/start link_<codigo>` ao bot.'
        )

    if preview.mode is OrchestrationMode.clarify:
        return (
            f'{DEFAULT_PUBLIC_HELP} Se quiser, pergunte por exemplo: '
            '"quais documentos preciso para a matricula?" ou '
            '"quando acontece a reuniao de pais?".'
        )

    if preview.mode is OrchestrationMode.handoff:
        return (
            'Posso seguir com orientacoes publicas por aqui, mas o handoff humano ainda sera '
            'conectado na proxima etapa. Por enquanto, use a secretaria ou o portal institucional.'
        )

    if preview.mode is OrchestrationMode.structured_tool:
        return (
            'Seu vinculo foi reconhecido, mas as consultas protegidas diretamente pelo Telegram '
            'entram na proxima entrega. Por enquanto, esses dados continuam disponiveis no portal '
            'autenticado da escola.'
        )

    sections: list[str] = []

    if preview.classification.domain is QueryDomain.calendar and calendar_events:
        sections.append('Encontrei estes proximos eventos publicos no calendario escolar:')
        sections.extend(_format_event_line(event) for event in calendar_events[:3])

    if retrieval_hits:
        intro = 'Segundo a base institucional atual:'
        if preview.classification.domain is QueryDomain.calendar and sections:
            intro = 'Tambem localizei estas referencias na base documental:'
        sections.append(intro)
        sections.extend(f'- {hit.text_excerpt}' for hit in retrieval_hits[:2])

    if not sections:
        return (
            'Ainda nao encontrei uma resposta suficientemente suportada na base publica. '
            'Tente reformular a pergunta com termos como matricula, calendario, secretaria ou atendimento.'
        )

    source_lines = _render_source_lines(citations)
    if source_lines:
        sections.append(source_lines)
    return '\n'.join(sections)


async def _fetch_public_calendar(*, api_core_url: str) -> list[CalendarEventCard]:
    today = date.today()
    params = {
        'date_from': today.isoformat(),
        'date_to': (today + timedelta(days=120)).isoformat(),
        'limit': 6,
    }
    async with httpx.AsyncClient(timeout=8.0) as client:
        response = await client.get(f'{api_core_url}/v1/calendar/public', params=params)
        response.raise_for_status()
    payload = response.json()
    events = payload.get('events', [])
    return [CalendarEventCard.model_validate(event) for event in events]


async def _compose_with_openai(
    *,
    settings: Any,
    request: MessageResponseRequest,
    preview: Any,
    citations: list[MessageResponseCitation],
    calendar_events: list[CalendarEventCard],
) -> str | None:
    if settings.llm_provider != 'openai' or not settings.openai_api_key:
        return None

    snippets = '\n\n'.join(
        f'Fonte {index}: {citation.document_title} ({citation.version_label})\nTrecho: {citation.excerpt}'
        for index, citation in enumerate(citations, start=1)
    )
    calendar_context = '\n'.join(_format_event_line(event) for event in calendar_events[:4])

    instructions = (
        'Voce e o assistente EduAssist de uma escola de ensino medio. '
        'Responda em portugues do Brasil, de forma objetiva e educada. '
        'Use apenas o contexto fornecido. Nao invente regras, datas ou documentos. '
        'Se a pergunta exigir autenticacao, diga isso com clareza. '
        'Se houver calendario estruturado, priorize-o. Nao cite fontes inline; elas serao anexadas depois.'
    )
    prompt = (
        f'Pergunta do usuario:\n{request.message}\n\n'
        f'Roteamento:\n- modo: {preview.mode.value}\n'
        f'- dominio: {preview.classification.domain.value}\n'
        f'- autenticacao necessaria: {preview.needs_authentication}\n\n'
        f'Eventos estruturados:\n{calendar_context or "nenhum"}\n\n'
        f'Trechos citaveis:\n{snippets or "nenhum"}'
    )

    try:
        client = AsyncOpenAI(api_key=settings.openai_api_key, base_url=settings.openai_base_url)
        response = await client.responses.create(
            model=settings.openai_model,
            instructions=instructions,
            input=prompt,
        )
        text = (response.output_text or '').strip()
        if not text:
            return None
        return text
    except Exception:
        return None


async def generate_message_response(*, request: MessageResponseRequest, settings: Any) -> MessageResponse:
    graph = build_orchestration_graph(settings.graph_rag_enabled)
    state = graph.invoke({'request': _map_request(request)})
    preview = to_preview(state)

    retrieval_hits: list[Any] = []
    citations: list[MessageResponseCitation] = []
    calendar_events: list[CalendarEventCard] = []

    if preview.mode is OrchestrationMode.hybrid_retrieval:
        retrieval_service = get_retrieval_service(
            database_url=settings.database_url,
            qdrant_url=settings.qdrant_url,
            collection_name=settings.qdrant_documents_collection,
            embedding_model=settings.document_embedding_model,
        )
        search = retrieval_service.hybrid_search(
            query=request.message,
            top_k=4,
            visibility='public',
            category=_category_for_domain(preview.classification.domain),
        )
        retrieval_hits = search.hits
        citations = _collect_citations(search.hits)

        if preview.classification.domain is QueryDomain.calendar:
            calendar_events = await _fetch_public_calendar(api_core_url=settings.api_core_url)

    llm_text = await _compose_with_openai(
        settings=settings,
        request=request,
        preview=preview,
        citations=citations,
        calendar_events=calendar_events,
    )
    message_text = llm_text or _compose_deterministic_answer(
        request=request,
        preview=preview,
        retrieval_hits=retrieval_hits,
        citations=citations,
        calendar_events=calendar_events,
    )

    if citations:
        sources = _render_source_lines(citations)
        if sources and sources not in message_text:
            message_text = f'{message_text}\n\n{sources}'

    return MessageResponse(
        message_text=message_text,
        mode=preview.mode,
        classification=preview.classification,
        retrieval_backend=preview.retrieval_backend,
        selected_tools=preview.selected_tools,
        citations=citations,
        calendar_events=calendar_events,
        needs_authentication=preview.needs_authentication,
        graph_path=preview.graph_path,
        risk_flags=preview.risk_flags,
        reason=preview.reason,
    )
