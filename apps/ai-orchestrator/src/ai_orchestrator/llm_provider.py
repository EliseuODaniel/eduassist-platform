from __future__ import annotations

from typing import Any

import httpx
from openai import AsyncOpenAI

from .models import CalendarEventCard, MessageResponseCitation


PROJECT_CONTEXT = (
    'Contexto do projeto EduAssist: voce atua como assistente institucional de uma escola de ensino medio. '
    'O sistema tem foco em atendimento escolar seguro, auditavel e baseado em fontes. '
    'Dados academicos e financeiros so podem ser respondidos quando o fluxo autenticado e autorizado liberar. '
    'Perguntas publicas devem priorizar fatos canonicos, documentos institucionais e calendario oficial. '
    'Perguntas comparativas, competitivas ou de recomendacao exigem cuidado extra: '
    'nao afirme superioridade sobre concorrentes sem base explicita; em vez disso, resuma os diferenciais documentados desta escola '
    'e ofereca uma comparacao limitada apenas se houver base ou se o usuario informar a instituicao especifica.'
)


def _build_context_sections(
    *,
    request_message: str,
    analysis_message: str,
    preview: Any,
    citations: list[MessageResponseCitation],
    calendar_events: list[CalendarEventCard],
    conversation_context: dict[str, Any] | None,
    school_profile: dict[str, Any] | None,
) -> tuple[str, str]:
    def school_profile_summary(profile: dict[str, Any]) -> str:
        name = profile.get('school_name')
        city = profile.get('city')
        state = profile.get('state')
        unit = profile.get('school_unit_code')
        segments = ', '.join(str(item) for item in profile.get('segments', [])[:4] if isinstance(item, str)) or 'nao informado'
        leadership = '; '.join(
            f"{item.get('title', 'lideranca')}: {item.get('name', 'nao informado')}"
            for item in profile.get('leadership_team', [])[:4]
            if isinstance(item, dict)
        ) or 'nao informado'
        services = '; '.join(
            f"{item.get('title', 'servico')} ({item.get('request_channel', 'canal institucional')})"
            for item in profile.get('service_catalog', [])[:6]
            if isinstance(item, dict)
        ) or 'nao informado'
        highlights = '; '.join(
            str(item.get('title', 'diferencial'))
            for item in profile.get('highlights', [])[:4]
            if isinstance(item, dict)
        ) or 'nao informado'
        return (
            f'nome={name or "nao informado"}, cidade={city or "nao informado"}, '
            f'estado={state or "nao informado"}, unidade={unit or "nao informado"}, '
            f'segmentos={segments}, lideranca={leadership}, servicos={services}, destaques={highlights}'
        )

    snippets = '\n\n'.join(
        f'Fonte {index}: {citation.document_title} ({citation.version_label})\nTrecho: {citation.excerpt}'
        for index, citation in enumerate(citations, start=1)
    )
    calendar_context = '\n'.join(
        f'- {event.title}: {event.description or "sem descricao"} '
        f'({event.starts_at.isoformat()} -> {event.ends_at.isoformat()})'
        for event in calendar_events[:4]
    )
    recent_messages = []
    if isinstance(conversation_context, dict):
        for item in conversation_context.get('recent_messages', [])[-6:]:
            if not isinstance(item, dict):
                continue
            sender_type = str(item.get('sender_type', 'desconhecido'))
            content = str(item.get('content', '')).strip()
            if content:
                recent_messages.append(f'- {sender_type}: {content}')
    memory_block = '\n'.join(recent_messages) or 'nenhum'
    school_profile_block = 'nenhum'
    if isinstance(school_profile, dict):
        school_profile_block = school_profile_summary(school_profile)
    instructions = (
        'Voce e o assistente EduAssist de uma escola de ensino medio. '
        'Responda em portugues do Brasil, com tom humano, profissional e natural, como uma recepcao escolar experiente. '
        f'{PROJECT_CONTEXT} '
        'Use apenas o contexto fornecido. Nao invente regras, datas, documentos ou horarios. '
        'Nao transforme listas de requisitos em afirmacoes sobre itens dispensaveis ou desnecessarios. '
        'Quando a pergunta for negativa, de exclusao, excecao ou complemento, so responda esse ponto '
        'se o contexto disser isso explicitamente. '
        'Quando a pergunta for comparativa, reconheca o limite da base e ofereca resumir os diferenciais documentados desta escola. '
        'Quando a pergunta parecer continuidade de uma conversa, use o historico recente apenas para resolver referencias como "isso", "ela", "esse horario", '
        'sem mudar o que realmente esta sustentado pelas fontes. '
        'Quando o usuario fizer uma pergunta de navegacao, como "com quem eu falo", "o que voce faz" ou "quais assuntos posso tratar aqui", '
        'aja como concierge institucional: explique o que o bot resolve, qual setor cuida do assunto e qual proximo passo o usuario pode seguir. '
        'Evite reapresentar o assistente por completo se o historico recente mostrar que ele ja se apresentou. '
        'Evite respostas roboticas, redundantes ou que so repitam menu; priorize uma resposta curta, util e orientada para acao. '
        'Se a pergunta exigir autenticacao, diga isso com clareza. '
        'Se houver calendario estruturado, priorize-o. '
        'Se o contexto nao responder a pergunta, diga explicitamente que a base atual nao tem evidencia suficiente. '
        'Nao cite fontes inline; elas serao anexadas depois.'
    )
    prompt = (
        f'Pergunta do usuario:\n{request_message}\n\n'
        f'Mensagem expandida para analise:\n{analysis_message}\n\n'
        f'Roteamento:\n- modo: {preview.mode.value}\n'
        f'- dominio: {preview.classification.domain.value}\n'
        f'- autenticacao necessaria: {preview.needs_authentication}\n\n'
        f'Perfil canonico da escola:\n{school_profile_block}\n\n'
        f'Historico recente da conversa:\n{memory_block}\n\n'
        f'Eventos estruturados:\n{calendar_context or "nenhum"}\n\n'
        f'Trechos citaveis:\n{snippets or "nenhum"}'
    )
    return instructions, prompt


async def compose_with_openai(
    *,
    settings: Any,
    request_message: str,
    analysis_message: str,
    preview: Any,
    citations: list[MessageResponseCitation],
    calendar_events: list[CalendarEventCard],
    conversation_context: dict[str, Any] | None,
    school_profile: dict[str, Any] | None,
) -> str | None:
    if settings.llm_provider != 'openai' or not settings.openai_api_key:
        return None

    instructions, prompt = _build_context_sections(
        request_message=request_message,
        analysis_message=analysis_message,
        preview=preview,
        citations=citations,
        calendar_events=calendar_events,
        conversation_context=conversation_context,
        school_profile=school_profile,
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
    analysis_message: str,
    preview: Any,
    citations: list[MessageResponseCitation],
    calendar_events: list[CalendarEventCard],
    conversation_context: dict[str, Any] | None,
    school_profile: dict[str, Any] | None,
) -> str | None:
    if settings.llm_provider not in {'google', 'gemini'} or not settings.google_api_key:
        return None

    instructions, prompt = _build_context_sections(
        request_message=request_message,
        analysis_message=analysis_message,
        preview=preview,
        citations=citations,
        calendar_events=calendar_events,
        conversation_context=conversation_context,
        school_profile=school_profile,
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
    analysis_message: str,
    preview: Any,
    citations: list[MessageResponseCitation],
    calendar_events: list[CalendarEventCard],
    conversation_context: dict[str, Any] | None,
    school_profile: dict[str, Any] | None,
) -> str | None:
    if settings.llm_provider == 'openai':
        return await compose_with_openai(
            settings=settings,
            request_message=request_message,
            analysis_message=analysis_message,
            preview=preview,
            citations=citations,
            calendar_events=calendar_events,
            conversation_context=conversation_context,
            school_profile=school_profile,
        )
    if settings.llm_provider in {'google', 'gemini'}:
        return await compose_with_google(
            settings=settings,
            request_message=request_message,
            analysis_message=analysis_message,
            preview=preview,
            citations=citations,
            calendar_events=calendar_events,
            conversation_context=conversation_context,
            school_profile=school_profile,
        )
    return None
