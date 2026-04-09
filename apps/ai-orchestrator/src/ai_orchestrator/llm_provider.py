from __future__ import annotations

import json
import re
from typing import Any

import httpx
from openai import AsyncOpenAI

from .models import CalendarEventCard, MessageResponseCitation

PROJECT_CONTEXT = (
    'Contexto do projeto EduAssist: voce atua como assistente institucional de uma escola de ensino fundamental II e ensino medio. '
    'O sistema tem foco em atendimento escolar seguro, auditavel e baseado em fontes. '
    'Dados academicos e financeiros so podem ser respondidos quando o fluxo autenticado e autorizado liberar. '
    'Perguntas publicas devem priorizar fatos canonicos, documentos institucionais e calendario oficial. '
    'Perguntas comparativas, competitivas ou de recomendacao exigem cuidado extra: '
    'nao afirme superioridade sobre concorrentes sem base explicita; em vez disso, resuma os diferenciais documentados desta escola '
    'e ofereca uma comparacao limitada apenas se houver base ou se o usuario informar a instituicao especifica.'
)


def _extract_json_object(text: str) -> dict[str, Any] | None:
    cleaned = text.strip()
    if not cleaned:
        return None
    fenced = re.search(r'```(?:json)?\s*(\{.*\})\s*```', cleaned, flags=re.DOTALL)
    candidate = fenced.group(1) if fenced else cleaned
    if not candidate.startswith('{'):
        start = candidate.find('{')
        end = candidate.rfind('}')
        if start >= 0 and end > start:
            candidate = candidate[start : end + 1]
    try:
        payload = json.loads(candidate)
    except Exception:
        return None
    return payload if isinstance(payload, dict) else None


def _google_model_candidates(configured_model: str) -> tuple[str, ...]:
    base = str(configured_model or '').strip()
    if base.startswith('models/'):
        base = base.split('/', 1)[1]

    seen: set[str] = set()
    candidates: list[str] = []

    def add(name: str | None) -> None:
        cleaned = str(name or '').strip()
        if not cleaned:
            return
        if cleaned.startswith('models/'):
            cleaned = cleaned.split('/', 1)[1]
        if cleaned in seen:
            return
        seen.add(cleaned)
        candidates.append(cleaned)

    add(base)
    if '-preview' in base:
        add(re.sub(r'-preview(?:-[a-z0-9-]+)?', '', base))
    if base.startswith('gemini-2.5-'):
        add('gemini-2.5-flash')
        add('gemini-2.5-pro')
    add('gemini-2.5-flash')
    add('gemini-2.0-flash')
    return tuple(candidates)


def _google_response_requires_model_fallback(response: httpx.Response) -> bool:
    if response.status_code not in {400, 404}:
        return False
    normalized = response.text.lower()
    return 'not found' in normalized or 'not supported for generatecontent' in normalized


async def _google_generate_content_body(
    *,
    settings: Any,
    payload: dict[str, Any],
    timeout: float,
) -> dict[str, Any] | None:
    headers = {
        'Content-Type': 'application/json',
        'x-goog-api-key': settings.google_api_key,
    }
    async with httpx.AsyncClient(timeout=timeout) as client:
        for model_name in _google_model_candidates(settings.google_model):
            endpoint = f"{settings.google_api_base_url.rstrip('/')}/models/{model_name}:generateContent"
            try:
                response = await client.post(endpoint, headers=headers, json=payload)
            except Exception:
                return None
            if _google_response_requires_model_fallback(response):
                continue
            try:
                response.raise_for_status()
                body = response.json()
            except Exception:
                return None
            return body if isinstance(body, dict) else None
    return None


def _google_extract_text(body: dict[str, Any]) -> str | None:
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
    merged = '\n'.join(text for text in texts if text).strip()
    return merged or None


def _google_generation_config(
    settings: Any,
    *,
    temperature: float,
    max_output_tokens: int,
    top_p: float | None = None,
) -> dict[str, Any]:
    config: dict[str, Any] = {
        'temperature': temperature,
        'maxOutputTokens': max_output_tokens,
    }
    if top_p is not None:
        config['topP'] = top_p
    if '2.5' in str(settings.google_model):
        config['thinkingConfig'] = {'thinkingBudget': 0}
    return config


def _build_context_sections(
    *,
    request_message: str,
    analysis_message: str,
    preview: Any,
    citations: list[MessageResponseCitation],
    calendar_events: list[CalendarEventCard],
    context_pack: str | None,
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
        'Se o usuario estiver corrigindo o rumo da conversa ou mostrando que a resposta anterior nao serviu, trate isso como reparo de conversa: '
        'reconheca brevemente, corrija o rumo e evite repetir blocos inteiros do turno anterior. '
        'Quando a pergunta tiver duas partes, cubra as duas com clareza; se so houver suporte para uma delas, diga isso explicitamente. '
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
        f'Contexto agregado por documento:\n{context_pack or "nenhum"}\n\n'
        f'Trechos citaveis:\n{snippets or "nenhum"}'
    )
    return instructions, prompt


def _build_revision_sections(
    *,
    request_message: str,
    preview: Any,
    draft_text: str,
    conversation_context: dict[str, Any] | None,
    school_profile: dict[str, Any] | None,
) -> tuple[str, str]:
    recent_messages = []
    if isinstance(conversation_context, dict):
        for item in conversation_context.get('recent_messages', [])[-4:]:
            if not isinstance(item, dict):
                continue
            sender_type = str(item.get('sender_type', 'desconhecido'))
            content = str(item.get('content', '')).strip()
            if content:
                recent_messages.append(f'- {sender_type}: {content}')
    memory_block = '\n'.join(recent_messages) or 'nenhum'
    school_name = str((school_profile or {}).get('school_name') or 'Colegio Horizonte')
    instructions = (
        'Voce e o revisor final de respostas do EduAssist. '
        f'{PROJECT_CONTEXT} '
        'Sua tarefa e revisar uma resposta ja redigida e melhorar apenas o tom, a naturalidade, a clareza e o proximo passo util. '
        'Nao adicione fatos novos. Nao altere regras de acesso. Nao remova alertas de autenticacao. '
        'Nao transforme a resposta em menu robotico. '
        'Se a resposta ja estiver boa, devolva exatamente KEEP. '
        'Se revisar, devolva somente a nova resposta final em portugues do Brasil, com tom humano, profissional e institucional. '
        'Se houver historico recente, evite reapresentar o assistente de forma repetitiva. '
        'Prefira respostas curtas a moderadas, orientadas para resolver o problema do usuario.'
    )
    prompt = (
        f'Escola: {school_name}\n'
        f'Pergunta do usuario:\n{request_message}\n\n'
        f'Roteamento:\n- modo: {preview.mode.value}\n- dominio: {preview.classification.domain.value}\n'
        f'- autenticacao necessaria: {preview.needs_authentication}\n\n'
        f'Historico recente:\n{memory_block}\n\n'
        f'Rascunho atual:\n{draft_text}'
    )
    return instructions, prompt


def _build_structured_polish_sections(
    *,
    request_message: str,
    preview: Any,
    draft_text: str,
    conversation_context: dict[str, Any] | None,
    school_profile: dict[str, Any] | None,
) -> tuple[str, str]:
    recent_messages = []
    if isinstance(conversation_context, dict):
        for item in conversation_context.get('recent_messages', [])[-4:]:
            if not isinstance(item, dict):
                continue
            sender_type = str(item.get('sender_type', 'desconhecido'))
            content = str(item.get('content', '')).strip()
            if content:
                recent_messages.append(f'- {sender_type}: {content}')
    memory_block = '\n'.join(recent_messages) or 'nenhum'
    school_name = str((school_profile or {}).get('school_name') or 'Colegio Horizonte')
    instructions = (
        'Voce e um polidor de respostas estruturadas do EduAssist. '
        f'{PROJECT_CONTEXT} '
        'Receba uma resposta correta e deixe-a mais humana, natural, acolhedora e objetiva, como uma atendente escolar experiente. '
        'Nao adicione fatos novos. Nao remova protocolos, filas, codigos, horarios, valores ou avisos de autenticacao. '
        'Nao transforme a resposta em menu, template rigido ou slogan. '
        'Evite reapresentar o assistente se ele ja estiver contextualizado na conversa. '
        'Prefira 2 a 4 frases curtas, com boa fluidez conversacional. '
        'Se a pergunta for de saudacao, identidade, capacidades ou direcionamento de setor, responda como concierge institucional humano e direto. '
        'Se a resposta ja estiver boa, devolva exatamente KEEP. '
        'Se revisar, devolva apenas a nova resposta final em portugues do Brasil.'
    )
    prompt = (
        f'Escola: {school_name}\n'
        f'Pergunta do usuario:\n{request_message}\n\n'
        f'Roteamento:\n- modo: {preview.mode.value}\n- dominio: {preview.classification.domain.value}\n'
        f'- autenticacao necessaria: {preview.needs_authentication}\n\n'
        f'Historico recente:\n{memory_block}\n\n'
        f'Resposta estruturada atual:\n{draft_text}'
    )
    return instructions, prompt


def _build_public_semantic_resolution_sections(
    *,
    request_message: str,
    conversation_context: dict[str, Any] | None,
    school_profile: dict[str, Any] | None,
    selected_tools: list[str],
) -> tuple[str, str]:
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
    school_name = str((school_profile or {}).get('school_name') or 'Colegio Horizonte')
    segments = ', '.join(
        str(item) for item in (school_profile or {}).get('segments', [])[:4] if isinstance(item, str)
    ) or 'nao informado'
    available_tools = [
        'get_public_school_profile',
        'list_assistant_capabilities',
        'get_org_directory',
        'get_service_directory',
        'get_public_timeline',
        'get_public_calendar_events',
    ]
    instructions = (
        'Voce e o resolvedor semantico publico do EduAssist. '
        f'{PROJECT_CONTEXT} '
        'Sua tarefa nao e responder ao usuario. Sua tarefa e decidir qual e o ato conversacional principal, '
        'qual foco da pergunta e quais tools publicas tipadas devem ser usadas. '
        'Seja conservador com contexto: use o historico recente apenas quando ele realmente resolver uma referencia curta como '
        '"isso", "ela", "esse horario", "e o telefone?" ou "e qual o proximo passo?". '
        'Nao invente tools. Nao crie fatos. '
        'Devolva apenas JSON valido com estas chaves: '
        'conversation_act, secondary_acts, required_tools, requested_attribute, requested_channel, focus_hint, use_conversation_context. '
        'conversation_act deve ser um entre: greeting, auth_guidance, access_scope, assistant_identity, capabilities, service_routing, document_submission, careers, teacher_directory, leadership, contacts, '
        'web_presence, social_presence, comparative, pricing, schedule, operating_hours, curriculum, features, highlight, visit, location, confessional, kpi, segments, school_name, timeline, calendar_events, utility_date, canonical_fact. '
        'secondary_acts deve ser uma lista opcional com no maximo 2 atos extras quando a pergunta pedir mais de uma informacao publica ao mesmo tempo, '
        'como site + endereco ou telefone + fax. Se nao houver multi-intencao publica, devolva lista vazia. '
        'Use timeline para marcos institucionais como inicio de matricula, inicio das aulas, formatura e outras datas-chave. '
        'Nao use calendar_events para inicio de matricula, inicio das aulas ou formatura; nesses casos o ato correto e timeline. '
        'Use access_scope quando o usuario perguntar o que consegue ver, quais dados pode consultar ou qual acesso ja tem neste Telegram vinculado. '
        'Use calendar_events para agendas e eventos publicos concretos, como reuniao de pais, feira, mostra ou eventos desta semana. '
        'Se a pergunta pedir horario e nome do mesmo espaco, como a biblioteca, prefira operating_hours como ato principal e use features como secondary_act. '
        'required_tools deve usar apenas: '
        + ', '.join(available_tools)
        + '. '
        'requested_attribute deve ser um entre: name, age, whatsapp, phone, email, contact, open_time, close_time, none. '
        'requested_channel deve ser um entre: telefone, whatsapp, email, none. '
        'focus_hint deve ser curto e opcional. '
        'use_conversation_context deve ser true apenas quando a pergunta atual realmente depender do turno anterior, '
        'como follow-up eliptico curto; use false quando o usuario claramente mudou de assunto.'
    )
    prompt = (
        f'Escola: {school_name}\n'
        f'Segmentos: {segments}\n'
        f'Tools ja sugeridas pelo roteador: {selected_tools}\n\n'
        f'Historico recente:\n{memory_block}\n\n'
        f'Pergunta do usuario:\n{request_message}\n\n'
        'Responda somente com JSON.'
    )
    return instructions, prompt


def _build_public_grounded_composition_sections(
    *,
    request_message: str,
    draft_text: str,
    public_plan: dict[str, Any],
    evidence_lines: list[str],
    conversation_context: dict[str, Any] | None,
    school_profile: dict[str, Any] | None,
) -> tuple[str, str]:
    recent_messages = []
    if isinstance(conversation_context, dict):
        for item in conversation_context.get('recent_messages', [])[-4:]:
            if not isinstance(item, dict):
                continue
            sender_type = str(item.get('sender_type', 'desconhecido'))
            content = str(item.get('content', '')).strip()
            if content:
                recent_messages.append(f'- {sender_type}: {content}')
    memory_block = '\n'.join(recent_messages) or 'nenhum'
    school_name = str((school_profile or {}).get('school_name') or 'Colegio Horizonte')
    evidence_block = '\n'.join(f'- {line}' for line in evidence_lines) or '- nenhum'
    instructions = (
        'Voce e o compositor grounded de respostas publicas do EduAssist. '
        f'{PROJECT_CONTEXT} '
        'Receba uma pergunta, um plano semantico publico e um pacote de evidencias estruturadas. '
        'Sua tarefa e responder exatamente a pergunta do usuario com tom humano, natural, direto e contextualizado. '
        'Nao adicione fatos fora das evidencias. '
        'Nao use tom de menu, FAQ engessada, slogan ou call center robotico. '
        'Se o usuario estiver corrigindo algo que acabou de ser entendido errado, reconheca isso brevemente e corrija o rumo sem se defender. '
        'Se o usuario mencionar outra escola, deixe claro que voce representa apenas o ' + school_name + ' e nao invente informacoes sobre a outra instituicao. '
        'Se a pergunta pedir algo fora do escopo publicado, admita esse limite com clareza e aproveite apenas a parte realmente suportada pela evidencia. '
        'Se a pergunta pedir comparacao, mantenha a comparacao restrita ao que as evidencias documentam desta escola. '
        'Se houver secondary_acts ou mais de um fato pedido no mesmo turno, cubra cada parte explicitamente; nao deixe cair nenhum item importante. '
        'Nao elimine nomes proprios, datas, horarios, telefones, e-mails ou URLs que ja estao no rascunho grounded quando eles respondem parte da pergunta. '
        'Se a pergunta envolver um espaco nomeado, como biblioteca, preserve o nome proprio desse espaco na resposta final. '
        'Responda em 2 a 5 frases. Prefira paragrafo curto. '
        'Se o rascunho deterministicamente grounded ja estiver bom, voce pode reescreve-lo de forma mais humana, mas sem perder a mesma substancia. '
        'Devolva apenas a resposta final em portugues do Brasil.'
    )
    prompt = (
        f'Escola:\n{school_name}\n\n'
        f'Pergunta do usuario:\n{request_message}\n\n'
        f'Plano semantico publico:\n{json.dumps(public_plan, ensure_ascii=False)}\n\n'
        f'Historico recente:\n{memory_block}\n\n'
        f'Evidencias estruturadas:\n{evidence_block}\n\n'
        f'Rascunho grounded atual:\n{draft_text}'
    )
    return instructions, prompt


def _build_grounded_answer_experience_sections(
    *,
    request_message: str,
    draft_text: str,
    mode: str,
    domain: str,
    access_tier: str,
    selected_tools: list[str],
    evidence_lines: list[str],
    recent_messages: list[str],
    school_profile: dict[str, Any] | None,
    reason: str,
    focus_summary: str | None = None,
) -> tuple[str, str]:
    school_name = str((school_profile or {}).get('school_name') or 'Colegio Horizonte')
    evidence_block = '\n'.join(f'- {line}' for line in evidence_lines[:10]) or '- nenhuma evidencia adicional'
    memory_block = '\n'.join(f'- {line}' for line in recent_messages[-6:]) or '- nenhum'
    tools_block = ', '.join(selected_tools) if selected_tools else 'nenhuma'
    instructions = (
        'Voce e a camada final de experiencia conversacional grounded do EduAssist. '
        f'{PROJECT_CONTEXT} '
        'Sua tarefa e transformar uma resposta correta ou parcialmente correta em uma resposta final realmente adaptada ao que o usuario perguntou, '
        'como o ChatGPT faria ao responder sobre um documento carregado: natural, inteligente, focada e contextualizada. '
        'Mas faca isso sem inventar fatos. Use apenas o rascunho e as evidencias fornecidas. '
        'Se o rascunho estiver amplo demais, recorte apenas a parte pedida pelo usuario. '
        'Se o rascunho estiver no dominio errado ou nao responder exatamente, nao repita a parte errada; diga com clareza que a resposta atual nao trouxe evidencia suficiente '
        'para confirmar exatamente aquele ponto. '
        'Preserve nomes proprios, valores, datas, numeros de media, frequencia, horarios, codigos, canais oficiais e limites de autenticacao quando eles realmente ajudarem a responder. '
        'Nao fale em "segundo o sistema" nem em "conforme o banco". Fale como um atendente escolar muito competente. '
        'Nao use tom de menu, FAQ dura, template mecanico ou autopromocao. '
        'Se o usuario estiver corrigindo um erro anterior, reconheca isso brevemente e corrija o rumo. '
        'Se a pergunta pedir um item especifico, como uma materia, um aluno, uma fatura ou uma avaliacao, responda so aquele recorte. '
        'Nao carregue assuntos anteriores que nao facam parte do foco atual. '
        'Nao mencione notas, medias, disciplinas ou financeiro se isso nao foi pedido agora. '
        'Use texto simples. Nao use Markdown, asteriscos, negrito, tabelas ou listas inline confusas. '
        'Se precisar listar itens, coloque um item por linha, com prefixo "- ". '
        'Se houver base para responder, responda de forma direta e satisfatoria. '
        'Se nao houver base suficiente no rascunho/evidencias, seja honesto sobre o limite. '
        'Devolva apenas a resposta final em portugues do Brasil.'
    )
    prompt = (
        f'Escola: {school_name}\n'
        f'Modo atual: {mode}\n'
        f'Dominio atual: {domain}\n'
        f'Nível de acesso: {access_tier}\n'
        f'Reason do runtime: {reason}\n'
        f'Tools envolvidos: {tools_block}\n\n'
        f'Pergunta do usuario:\n{request_message}\n\n'
        f'Foco resolvido deste turno:\n{focus_summary or "sem foco explicito"}\n\n'
        f'Historico recente:\n{memory_block}\n\n'
        f'Evidencias disponiveis:\n{evidence_block}\n\n'
        f'Rascunho atual:\n{draft_text}'
    )
    return instructions, prompt


def _build_context_repair_sections(
    *,
    request_message: str,
    draft_text: str,
    mode: str,
    domain: str,
    access_tier: str,
    selected_tools: list[str],
    evidence_lines: list[str],
    recent_messages: list[str],
    school_profile: dict[str, Any] | None,
    reason: str,
    focus_summary: str | None = None,
    actor_summary: str | None = None,
) -> tuple[str, str]:
    school_name = str((school_profile or {}).get('school_name') or 'Colegio Horizonte')
    evidence_block = '\n'.join(f'- {line}' for line in evidence_lines[:10]) or '- nenhuma evidencia adicional'
    memory_block = '\n'.join(f'- {line}' for line in recent_messages[-6:]) or '- nenhum'
    tools_block = ', '.join(selected_tools) if selected_tools else 'nenhuma'
    instructions = (
        'Voce e o planejador de reparo de contexto e grounding do EduAssist. '
        f'{PROJECT_CONTEXT} '
        'Sua tarefa e decidir o proximo melhor passo quando a resposta atual parece insuficiente, ambigua ou pouco satisfatoria. '
        'Escolha entre quatro acoes: keep, clarify, retry_retrieval ou unavailable. '
        'Preferir retry_retrieval quando a pergunta do usuario ja estiver compreensivel com a mensagem atual, o foco resolvido e o historico recente, '
        'mas a recuperacao atual parece fraca, generica ou insuficiente. '
        'Escolha clarify apenas quando faltar uma informacao essencial que precisa vir do usuario, como qual aluno, qual disciplina, qual periodo ou qual documento. '
        'Escolha unavailable apenas quando a pergunta estiver clara e voce tiver alta confianca de que a informacao nao esta disponivel no material/servicos atuais, mesmo apos uma nova busca enriquecida. '
        'Evite unavailable cedo demais. Se houver chance razoavel de uma nova busca com mais contexto resolver, prefira retry_retrieval. '
        'Quando gerar retry_query, torne a consulta autocontida e mais especifica, incorporando entidades e restricoes do foco atual sem inventar fatos. '
        'Quando gerar clarify, escreva apenas uma pergunta curta, natural e objetiva em portugues do Brasil. '
        'Quando gerar unavailable, escreva uma resposta honesta e curta, sem dizer que e impossivel; diga apenas que nao encontrei base suficiente no momento. '
        'Devolva apenas JSON valido com as chaves: action, message, retry_query, confidence, reason.'
    )
    prompt = (
        f'Escola: {school_name}\n'
        f'Modo atual: {mode}\n'
        f'Dominio atual: {domain}\n'
        f'Nível de acesso: {access_tier}\n'
        f'Reason do runtime: {reason}\n'
        f'Tools envolvidos: {tools_block}\n\n'
        f'Pergunta do usuario:\n{request_message}\n\n'
        f'Foco resolvido deste turno:\n{focus_summary or "sem foco explicito"}\n\n'
        f'Resumo do ator:\n{actor_summary or "sem resumo do ator"}\n\n'
        f'Historico recente:\n{memory_block}\n\n'
        f'Evidencias disponiveis:\n{evidence_block}\n\n'
        f'Resposta/rascunho atual:\n{draft_text}\n\n'
        'Responda somente com JSON.'
    )
    return instructions, prompt


def _build_answer_verification_sections(
    *,
    request_message: str,
    preview: Any,
    candidate_text: str,
    fallback_text: str,
    public_plan: dict[str, Any] | None,
    slot_memory: dict[str, Any] | None,
) -> tuple[str, str]:
    protected_query = (
        preview.mode.value == 'structured_tool'
        and preview.classification.access_tier.value != 'public'
        and preview.classification.domain.value in {'institution', 'academic', 'finance'}
    )
    protected_rules = (
        'Como esta consulta e protegida, identidade e escopo sao criticos. '
        'Marque invalid se a candidata trocar o responsavel autenticado, trocar o aluno em foco, '
        'misturar Lucas com Fernando, responder sobre outro filho, trocar boleto/contrato/matricula por outro registro '
        'ou transformar uma pergunta sobre acesso da conta em uma resposta sobre um aluno. '
        'Tambem marque invalid se a grounded responder o atributo certo e a candidata escorregar para um resumo generico.'
        if protected_query
        else ''
    )
    instructions = (
        'Voce e o verificador semantico final do EduAssist. '
        f'{PROJECT_CONTEXT} '
        'Sua tarefa e julgar se uma resposta candidata ainda responde a mesma pergunta do usuario '
        'que a resposta deterministica grounded. '
        'Priorize relevancia semantica e cobertura da pergunta, nao estilo. '
        'Marque invalid quando a resposta candidata muda de assunto, troca a entidade principal, '
        'omite o atributo pedido, responde so parte de uma pergunta composta ou contradiz a resposta grounded. '
        'Tambem marque invalid quando a resposta grounded tinha um nome, data, horario, telefone, e-mail ou URL necessario para responder a pergunta '
        'e a candidata deixou esse dado cair. '
        f'{protected_rules} '
        'Se a candidata preservar o mesmo sentido central da grounded, pode marcar valid mesmo com redacao diferente. '
        'Devolva apenas JSON valido com as chaves: valid, reason.'
    )
    prompt = (
        f'Pergunta do usuario:\n{request_message}\n\n'
        f'Roteamento:\n- modo: {preview.mode.value}\n- dominio: {preview.classification.domain.value}\n'
        f'- autenticacao necessaria: {preview.needs_authentication}\n\n'
        f'Plano publico:\n{json.dumps(public_plan or {}, ensure_ascii=False)}\n\n'
        f'Memoria de slots:\n{json.dumps(slot_memory or {}, ensure_ascii=False)}\n\n'
        f'Resposta grounded de referencia:\n{fallback_text}\n\n'
        f'Resposta candidata:\n{candidate_text}\n\n'
        'Responda somente com JSON.'
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
    context_pack: str | None = None,
) -> str | None:
    if settings.llm_provider != 'openai' or not settings.openai_api_key:
        return None

    instructions, prompt = _build_context_sections(
        request_message=request_message,
        analysis_message=analysis_message,
        preview=preview,
        citations=citations,
        calendar_events=calendar_events,
        context_pack=context_pack,
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


async def revise_with_openai(
    *,
    settings: Any,
    request_message: str,
    preview: Any,
    draft_text: str,
    conversation_context: dict[str, Any] | None,
    school_profile: dict[str, Any] | None,
) -> str | None:
    if settings.llm_provider != 'openai' or not settings.openai_api_key:
        return None

    instructions, prompt = _build_revision_sections(
        request_message=request_message,
        preview=preview,
        draft_text=draft_text,
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
        if not text or text == 'KEEP':
            return None
        return text
    except Exception:
        return None


async def polish_structured_with_openai(
    *,
    settings: Any,
    request_message: str,
    preview: Any,
    draft_text: str,
    conversation_context: dict[str, Any] | None,
    school_profile: dict[str, Any] | None,
) -> str | None:
    if settings.llm_provider != 'openai' or not settings.openai_api_key:
        return None

    instructions, prompt = _build_structured_polish_sections(
        request_message=request_message,
        preview=preview,
        draft_text=draft_text,
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
        if not text or text == 'KEEP':
            return None
        return text
    except Exception:
        return None


async def resolve_public_semantic_with_openai(
    *,
    settings: Any,
    request_message: str,
    conversation_context: dict[str, Any] | None,
    school_profile: dict[str, Any] | None,
    selected_tools: list[str],
) -> dict[str, Any] | None:
    if settings.llm_provider != 'openai' or not settings.openai_api_key:
        return None

    instructions, prompt = _build_public_semantic_resolution_sections(
        request_message=request_message,
        conversation_context=conversation_context,
        school_profile=school_profile,
        selected_tools=selected_tools,
    )
    try:
        client = AsyncOpenAI(api_key=settings.openai_api_key, base_url=settings.openai_base_url)
        response = await client.responses.create(
            model=settings.openai_model,
            instructions=instructions,
            input=prompt,
        )
        text = (response.output_text or '').strip()
    except Exception:
        return None
    return _extract_json_object(text)


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
    context_pack: str | None = None,
) -> str | None:
    if settings.llm_provider not in {'google', 'gemini'} or not settings.google_api_key:
        return None

    instructions, prompt = _build_context_sections(
        request_message=request_message,
        analysis_message=analysis_message,
        preview=preview,
        citations=citations,
        calendar_events=calendar_events,
        context_pack=context_pack,
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
        'generationConfig': _google_generation_config(
            settings,
            temperature=0.2,
            max_output_tokens=700,
        ),
    }
    body = await _google_generate_content_body(
        settings=settings,
        payload=payload,
        timeout=25.0,
    )
    if not isinstance(body, dict):
        return None
    merged = _google_extract_text(body)
    return merged or None


async def revise_with_google(
    *,
    settings: Any,
    request_message: str,
    preview: Any,
    draft_text: str,
    conversation_context: dict[str, Any] | None,
    school_profile: dict[str, Any] | None,
) -> str | None:
    if settings.llm_provider not in {'google', 'gemini'} or not settings.google_api_key:
        return None

    instructions, prompt = _build_revision_sections(
        request_message=request_message,
        preview=preview,
        draft_text=draft_text,
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
        'generationConfig': _google_generation_config(
            settings,
            temperature=0.15,
            max_output_tokens=320,
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
    if not merged or merged == 'KEEP':
        return None
    return merged


async def polish_structured_with_google(
    *,
    settings: Any,
    request_message: str,
    preview: Any,
    draft_text: str,
    conversation_context: dict[str, Any] | None,
    school_profile: dict[str, Any] | None,
) -> str | None:
    if settings.llm_provider not in {'google', 'gemini'} or not settings.google_api_key:
        return None

    instructions, prompt = _build_structured_polish_sections(
        request_message=request_message,
        preview=preview,
        draft_text=draft_text,
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
        'generationConfig': _google_generation_config(
            settings,
            temperature=0.1,
            max_output_tokens=240,
        ),
    }
    body = await _google_generate_content_body(
        settings=settings,
        payload=payload,
        timeout=15.0,
    )
    if not isinstance(body, dict):
        return None
    merged = _google_extract_text(body)
    if not merged or merged == 'KEEP':
        return None
    return merged


async def resolve_public_semantic_with_google(
    *,
    settings: Any,
    request_message: str,
    conversation_context: dict[str, Any] | None,
    school_profile: dict[str, Any] | None,
    selected_tools: list[str],
) -> dict[str, Any] | None:
    if settings.llm_provider not in {'google', 'gemini'} or not settings.google_api_key:
        return None

    instructions, prompt = _build_public_semantic_resolution_sections(
        request_message=request_message,
        conversation_context=conversation_context,
        school_profile=school_profile,
        selected_tools=selected_tools,
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
        'generationConfig': _google_generation_config(
            settings,
            temperature=0.0,
            max_output_tokens=220,
        ),
    }
    body = await _google_generate_content_body(
        settings=settings,
        payload=payload,
        timeout=15.0,
    )
    if not isinstance(body, dict):
        return None
    merged = _google_extract_text(body)
    return _extract_json_object(merged)


async def judge_answer_relevance_with_openai(
    *,
    settings: Any,
    request_message: str,
    preview: Any,
    candidate_text: str,
    fallback_text: str,
    public_plan: dict[str, Any] | None,
    slot_memory: dict[str, Any] | None,
) -> dict[str, Any] | None:
    if settings.llm_provider != 'openai' or not settings.openai_api_key:
        return None

    instructions, prompt = _build_answer_verification_sections(
        request_message=request_message,
        preview=preview,
        candidate_text=candidate_text,
        fallback_text=fallback_text,
        public_plan=public_plan,
        slot_memory=slot_memory,
    )
    try:
        client = AsyncOpenAI(api_key=settings.openai_api_key, base_url=settings.openai_base_url)
        response = await client.responses.create(
            model=settings.openai_model,
            instructions=instructions,
            input=prompt,
        )
        text = (response.output_text or '').strip()
    except Exception:
        return None
    return _extract_json_object(text)


async def judge_answer_relevance_with_google(
    *,
    settings: Any,
    request_message: str,
    preview: Any,
    candidate_text: str,
    fallback_text: str,
    public_plan: dict[str, Any] | None,
    slot_memory: dict[str, Any] | None,
) -> dict[str, Any] | None:
    if settings.llm_provider not in {'google', 'gemini'} or not settings.google_api_key:
        return None

    instructions, prompt = _build_answer_verification_sections(
        request_message=request_message,
        preview=preview,
        candidate_text=candidate_text,
        fallback_text=fallback_text,
        public_plan=public_plan,
        slot_memory=slot_memory,
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
        'generationConfig': _google_generation_config(
            settings,
            temperature=0.0,
            max_output_tokens=160,
        ),
    }
    body = await _google_generate_content_body(
        settings=settings,
        payload=payload,
        timeout=15.0,
    )
    if not isinstance(body, dict):
        return None
    merged = _google_extract_text(body)
    return _extract_json_object(merged)


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
    context_pack: str | None = None,
) -> str | None:
    if settings.llm_provider == 'openai':
        return await compose_with_openai(
            settings=settings,
            request_message=request_message,
            analysis_message=analysis_message,
            preview=preview,
            citations=citations,
            calendar_events=calendar_events,
            context_pack=context_pack,
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
            context_pack=context_pack,
            conversation_context=conversation_context,
            school_profile=school_profile,
        )
    return None


async def revise_with_provider(
    *,
    settings: Any,
    request_message: str,
    preview: Any,
    draft_text: str,
    conversation_context: dict[str, Any] | None,
    school_profile: dict[str, Any] | None,
) -> str | None:
    if settings.llm_provider == 'openai':
        return await revise_with_openai(
            settings=settings,
            request_message=request_message,
            preview=preview,
            draft_text=draft_text,
            conversation_context=conversation_context,
            school_profile=school_profile,
        )
    if settings.llm_provider in {'google', 'gemini'}:
        return await revise_with_google(
            settings=settings,
            request_message=request_message,
            preview=preview,
            draft_text=draft_text,
            conversation_context=conversation_context,
            school_profile=school_profile,
        )
    return None


async def polish_structured_with_provider(
    *,
    settings: Any,
    request_message: str,
    preview: Any,
    draft_text: str,
    conversation_context: dict[str, Any] | None,
    school_profile: dict[str, Any] | None,
) -> str | None:
    if settings.llm_provider == 'openai':
        return await polish_structured_with_openai(
            settings=settings,
            request_message=request_message,
            preview=preview,
            draft_text=draft_text,
            conversation_context=conversation_context,
            school_profile=school_profile,
        )
    if settings.llm_provider in {'google', 'gemini'}:
        return await polish_structured_with_google(
            settings=settings,
            request_message=request_message,
            preview=preview,
            draft_text=draft_text,
            conversation_context=conversation_context,
            school_profile=school_profile,
        )
    return None


async def resolve_public_semantic_with_provider(
    *,
    settings: Any,
    request_message: str,
    conversation_context: dict[str, Any] | None,
    school_profile: dict[str, Any] | None,
    selected_tools: list[str],
) -> dict[str, Any] | None:
    if settings.llm_provider == 'openai':
        return await resolve_public_semantic_with_openai(
            settings=settings,
            request_message=request_message,
            conversation_context=conversation_context,
            school_profile=school_profile,
            selected_tools=selected_tools,
        )
    if settings.llm_provider in {'google', 'gemini'}:
        return await resolve_public_semantic_with_google(
            settings=settings,
            request_message=request_message,
            conversation_context=conversation_context,
            school_profile=school_profile,
            selected_tools=selected_tools,
        )
    return None


async def compose_public_grounded_with_openai(
    *,
    settings: Any,
    request_message: str,
    draft_text: str,
    public_plan: dict[str, Any],
    evidence_lines: list[str],
    conversation_context: dict[str, Any] | None,
    school_profile: dict[str, Any] | None,
) -> str | None:
    if settings.llm_provider != 'openai' or not settings.openai_api_key:
        return None
    instructions, prompt = _build_public_grounded_composition_sections(
        request_message=request_message,
        draft_text=draft_text,
        public_plan=public_plan,
        evidence_lines=evidence_lines,
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
    except Exception:
        return None
    return text or None


async def compose_public_grounded_with_google(
    *,
    settings: Any,
    request_message: str,
    draft_text: str,
    public_plan: dict[str, Any],
    evidence_lines: list[str],
    conversation_context: dict[str, Any] | None,
    school_profile: dict[str, Any] | None,
) -> str | None:
    if settings.llm_provider not in {'google', 'gemini'} or not settings.google_api_key:
        return None
    instructions, prompt = _build_public_grounded_composition_sections(
        request_message=request_message,
        draft_text=draft_text,
        public_plan=public_plan,
        evidence_lines=evidence_lines,
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
        'generationConfig': _google_generation_config(
            settings,
            temperature=0.15,
            top_p=0.9,
            max_output_tokens=320,
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


async def compose_public_grounded_with_provider(
    *,
    settings: Any,
    request_message: str,
    draft_text: str,
    public_plan: dict[str, Any],
    evidence_lines: list[str],
    conversation_context: dict[str, Any] | None,
    school_profile: dict[str, Any] | None,
) -> str | None:
    if settings.llm_provider == 'openai':
        return await compose_public_grounded_with_openai(
            settings=settings,
            request_message=request_message,
            draft_text=draft_text,
            public_plan=public_plan,
            evidence_lines=evidence_lines,
            conversation_context=conversation_context,
            school_profile=school_profile,
        )
    if settings.llm_provider in {'google', 'gemini'}:
        return await compose_public_grounded_with_google(
            settings=settings,
            request_message=request_message,
            draft_text=draft_text,
            public_plan=public_plan,
            evidence_lines=evidence_lines,
            conversation_context=conversation_context,
            school_profile=school_profile,
        )
    return None


async def compose_grounded_answer_experience_with_openai(
    *,
    settings: Any,
    request_message: str,
    draft_text: str,
    mode: str,
    domain: str,
    access_tier: str,
    selected_tools: list[str],
    evidence_lines: list[str],
    recent_messages: list[str],
    school_profile: dict[str, Any] | None,
    reason: str,
    focus_summary: str | None = None,
) -> str | None:
    if not settings.openai_api_key:
        return None
    instructions, prompt = _build_grounded_answer_experience_sections(
        request_message=request_message,
        draft_text=draft_text,
        mode=mode,
        domain=domain,
        access_tier=access_tier,
        selected_tools=selected_tools,
        evidence_lines=evidence_lines,
        recent_messages=recent_messages,
        school_profile=school_profile,
        reason=reason,
        focus_summary=focus_summary,
    )
    try:
        client = AsyncOpenAI(api_key=settings.openai_api_key, base_url=settings.openai_base_url)
        response = await client.responses.create(
            model=settings.openai_model,
            instructions=instructions,
            input=prompt,
        )
        text = (response.output_text or '').strip()
    except Exception:
        return None
    return text or None


async def compose_grounded_answer_experience_with_google(
    *,
    settings: Any,
    request_message: str,
    draft_text: str,
    mode: str,
    domain: str,
    access_tier: str,
    selected_tools: list[str],
    evidence_lines: list[str],
    recent_messages: list[str],
    school_profile: dict[str, Any] | None,
    reason: str,
    focus_summary: str | None = None,
) -> str | None:
    if not settings.google_api_key:
        return None
    instructions, prompt = _build_grounded_answer_experience_sections(
        request_message=request_message,
        draft_text=draft_text,
        mode=mode,
        domain=domain,
        access_tier=access_tier,
        selected_tools=selected_tools,
        evidence_lines=evidence_lines,
        recent_messages=recent_messages,
        school_profile=school_profile,
        reason=reason,
        focus_summary=focus_summary,
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
        'generationConfig': _google_generation_config(
            settings,
            temperature=0.12,
            top_p=0.9,
            max_output_tokens=320,
        ),
    }
    body = await _google_generate_content_body(
        settings=settings,
        payload=payload,
        timeout=18.0,
    )
    if not isinstance(body, dict):
        return None
    merged = _google_extract_text(body)
    return merged or None


async def compose_grounded_answer_experience_with_provider(
    *,
    settings: Any,
    request_message: str,
    draft_text: str,
    mode: str,
    domain: str,
    access_tier: str,
    selected_tools: list[str],
    evidence_lines: list[str],
    recent_messages: list[str],
    school_profile: dict[str, Any] | None,
    reason: str,
    focus_summary: str | None = None,
) -> str | None:
    if settings.llm_provider == 'openai':
        return await compose_grounded_answer_experience_with_openai(
            settings=settings,
            request_message=request_message,
            draft_text=draft_text,
            mode=mode,
            domain=domain,
            access_tier=access_tier,
            selected_tools=selected_tools,
            evidence_lines=evidence_lines,
            recent_messages=recent_messages,
            school_profile=school_profile,
            reason=reason,
            focus_summary=focus_summary,
        )
    if settings.llm_provider in {'google', 'gemini'}:
        return await compose_grounded_answer_experience_with_google(
            settings=settings,
            request_message=request_message,
            draft_text=draft_text,
            mode=mode,
            domain=domain,
            access_tier=access_tier,
            selected_tools=selected_tools,
            evidence_lines=evidence_lines,
            recent_messages=recent_messages,
            school_profile=school_profile,
            reason=reason,
            focus_summary=focus_summary,
        )
    return None


async def plan_context_repair_with_openai(
    *,
    settings: Any,
    request_message: str,
    draft_text: str,
    mode: str,
    domain: str,
    access_tier: str,
    selected_tools: list[str],
    evidence_lines: list[str],
    recent_messages: list[str],
    school_profile: dict[str, Any] | None,
    reason: str,
    focus_summary: str | None = None,
    actor_summary: str | None = None,
) -> dict[str, Any] | None:
    if not settings.openai_api_key:
        return None
    instructions, prompt = _build_context_repair_sections(
        request_message=request_message,
        draft_text=draft_text,
        mode=mode,
        domain=domain,
        access_tier=access_tier,
        selected_tools=selected_tools,
        evidence_lines=evidence_lines,
        recent_messages=recent_messages,
        school_profile=school_profile,
        reason=reason,
        focus_summary=focus_summary,
        actor_summary=actor_summary,
    )
    try:
        client = AsyncOpenAI(api_key=settings.openai_api_key, base_url=settings.openai_base_url)
        response = await client.responses.create(
            model=settings.openai_model,
            instructions=instructions,
            input=prompt,
        )
        text = (response.output_text or '').strip()
    except Exception:
        return None
    return _extract_json_object(text or '')


async def plan_context_repair_with_google(
    *,
    settings: Any,
    request_message: str,
    draft_text: str,
    mode: str,
    domain: str,
    access_tier: str,
    selected_tools: list[str],
    evidence_lines: list[str],
    recent_messages: list[str],
    school_profile: dict[str, Any] | None,
    reason: str,
    focus_summary: str | None = None,
    actor_summary: str | None = None,
) -> dict[str, Any] | None:
    if not settings.google_api_key:
        return None
    instructions, prompt = _build_context_repair_sections(
        request_message=request_message,
        draft_text=draft_text,
        mode=mode,
        domain=domain,
        access_tier=access_tier,
        selected_tools=selected_tools,
        evidence_lines=evidence_lines,
        recent_messages=recent_messages,
        school_profile=school_profile,
        reason=reason,
        focus_summary=focus_summary,
        actor_summary=actor_summary,
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
        'generationConfig': _google_generation_config(
            settings,
            temperature=0.05,
            top_p=0.9,
            max_output_tokens=220,
        ),
    }
    body = await _google_generate_content_body(
        settings=settings,
        payload=payload,
        timeout=18.0,
    )
    if not isinstance(body, dict):
        return None
    merged = _google_extract_text(body)
    return _extract_json_object(merged or '')


async def plan_context_repair_with_provider(
    *,
    settings: Any,
    request_message: str,
    draft_text: str,
    mode: str,
    domain: str,
    access_tier: str,
    selected_tools: list[str],
    evidence_lines: list[str],
    recent_messages: list[str],
    school_profile: dict[str, Any] | None,
    reason: str,
    focus_summary: str | None = None,
    actor_summary: str | None = None,
) -> dict[str, Any] | None:
    if settings.llm_provider == 'openai':
        return await plan_context_repair_with_openai(
            settings=settings,
            request_message=request_message,
            draft_text=draft_text,
            mode=mode,
            domain=domain,
            access_tier=access_tier,
            selected_tools=selected_tools,
            evidence_lines=evidence_lines,
            recent_messages=recent_messages,
            school_profile=school_profile,
            reason=reason,
            focus_summary=focus_summary,
            actor_summary=actor_summary,
        )
    if settings.llm_provider in {'google', 'gemini'}:
        return await plan_context_repair_with_google(
            settings=settings,
            request_message=request_message,
            draft_text=draft_text,
            mode=mode,
            domain=domain,
            access_tier=access_tier,
            selected_tools=selected_tools,
            evidence_lines=evidence_lines,
            recent_messages=recent_messages,
            school_profile=school_profile,
            reason=reason,
            focus_summary=focus_summary,
            actor_summary=actor_summary,
        )
    return None


async def judge_answer_relevance_with_provider(
    *,
    settings: Any,
    request_message: str,
    preview: Any,
    candidate_text: str,
    fallback_text: str,
    public_plan: dict[str, Any] | None,
    slot_memory: dict[str, Any] | None,
) -> dict[str, Any] | None:
    if settings.llm_provider == 'openai':
        return await judge_answer_relevance_with_openai(
            settings=settings,
            request_message=request_message,
            preview=preview,
            candidate_text=candidate_text,
            fallback_text=fallback_text,
            public_plan=public_plan,
            slot_memory=slot_memory,
        )
    if settings.llm_provider in {'google', 'gemini'}:
        return await judge_answer_relevance_with_google(
            settings=settings,
            request_message=request_message,
            preview=preview,
            candidate_text=candidate_text,
            fallback_text=fallback_text,
            public_plan=public_plan,
            slot_memory=slot_memory,
        )
    return None
