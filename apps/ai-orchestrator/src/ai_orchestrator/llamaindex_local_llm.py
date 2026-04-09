from __future__ import annotations

import json
from typing import Any

from .models import CalendarEventCard, MessageResponseCitation
from .stack_local_llm_common import stack_local_json_call, stack_local_text_call

_STACK_LABEL = 'LlamaIndex'


def _school_name(school_profile: dict[str, Any] | None) -> str:
    return str((school_profile or {}).get('school_name') or 'Colegio Horizonte')


def _recent_messages(conversation_context: dict[str, Any] | None, *, limit: int = 6) -> str:
    lines: list[str] = []
    if isinstance(conversation_context, dict):
        for item in (conversation_context.get('recent_messages') or [])[-limit:]:
            if not isinstance(item, dict):
                continue
            sender = str(item.get('sender_type', 'desconhecido')).strip()
            content = str(item.get('content', '')).strip()
            if content:
                lines.append(f'- {sender}: {content}')
    return '\n'.join(lines) or '- nenhum'


def _citations_block(citations: list[MessageResponseCitation], context_pack: str | None) -> str:
    lines = [
        f'- {citation.document_title}: {citation.excerpt}'
        for citation in citations[:8]
        if str(citation.excerpt).strip()
    ]
    if context_pack:
        lines.append(f'- Contexto documental consolidado: {context_pack}')
    return '\n'.join(lines) or '- nenhuma evidencia documental'


def _calendar_block(calendar_events: list[CalendarEventCard]) -> str:
    lines = [
        f'- {event.title}: {event.description or "sem descricao"}'
        for event in calendar_events[:4]
    ]
    return '\n'.join(lines) or '- nenhum evento estruturado'


def _compose_sections(
    *,
    request_message: str,
    analysis_message: str,
    preview: Any,
    citations: list[MessageResponseCitation],
    calendar_events: list[CalendarEventCard],
    conversation_context: dict[str, Any] | None,
    school_profile: dict[str, Any] | None,
    context_pack: str | None,
) -> tuple[str, str]:
    instructions = (
        f'Voce e o compositor auxiliar do caminho {_STACK_LABEL} no EduAssist. '
        'Este caminho prioriza sintese documental, combinacao de evidencias e resposta grounded. '
        'Use apenas as evidencias fornecidas. Preserve a pergunta original, o foco do turno e a cobertura dos pontos pedidos. '
        'Nao invente fatos, nao troque entidades, nao esconda limites de evidencia. '
        'Devolva apenas a resposta final.'
    )
    prompt = (
        f'Escola: {_school_name(school_profile)}\n'
        f'Pergunta do usuario:\n{request_message}\n\n'
        f'Mensagem expandida para analise:\n{analysis_message}\n\n'
        f'Modo: {preview.mode.value}\n'
        f'Dominio: {preview.classification.domain.value}\n'
        f'Acesso: {preview.classification.access_tier.value}\n\n'
        f'Historico recente:\n{_recent_messages(conversation_context)}\n\n'
        f'Eventos estruturados:\n{_calendar_block(calendar_events)}\n\n'
        f'Evidencias:\n{_citations_block(citations, context_pack)}'
    )
    return instructions, prompt


def _revision_sections(
    *,
    request_message: str,
    preview: Any,
    draft_text: str,
    conversation_context: dict[str, Any] | None,
    school_profile: dict[str, Any] | None,
    purpose: str,
) -> tuple[str, str]:
    instructions = (
        f'Voce esta refinando uma resposta do caminho {_STACK_LABEL}. '
        'Melhore naturalidade, concisao e cobertura do pedido sem acrescentar fatos. '
        'Se a resposta ja estiver boa, devolva exatamente KEEP. '
        'Devolva somente o texto final.'
    )
    prompt = (
        f'Objetivo: {purpose}\n'
        f'Escola: {_school_name(school_profile)}\n'
        f'Pergunta do usuario:\n{request_message}\n\n'
        f'Modo: {preview.mode.value}\n'
        f'Dominio: {preview.classification.domain.value}\n\n'
        f'Historico recente:\n{_recent_messages(conversation_context, limit=4)}\n\n'
        f'Rascunho atual:\n{draft_text}'
    )
    return instructions, prompt


def _judge_sections(
    *,
    request_message: str,
    preview: Any,
    candidate_text: str,
    fallback_text: str,
    public_plan: dict[str, Any] | None,
    slot_memory: dict[str, Any] | None,
) -> tuple[str, str]:
    instructions = (
        f'Voce e o juiz semantico do caminho {_STACK_LABEL}. '
        'Compare a resposta candidata com a resposta grounded de referencia. '
        'Marque invalid quando a candidata perder cobertura importante, trocar o foco da pergunta ou contradizer a referencia grounded. '
        'Responda somente com JSON valido contendo valid e reason.'
    )
    prompt = (
        f'Pergunta do usuario:\n{request_message}\n\n'
        f'Modo: {preview.mode.value}\n'
        f'Dominio: {preview.classification.domain.value}\n'
        f'Plano publico: {json.dumps(public_plan or {}, ensure_ascii=False)}\n'
        f'Slots: {json.dumps(slot_memory or {}, ensure_ascii=False)}\n\n'
        f'Resposta grounded de referencia:\n{fallback_text}\n\n'
        f'Resposta candidata:\n{candidate_text}'
    )
    return instructions, prompt


async def compose_llamaindex_with_provider(
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
    instructions, prompt = _compose_sections(
        request_message=request_message,
        analysis_message=analysis_message,
        preview=preview,
        citations=citations,
        calendar_events=calendar_events,
        conversation_context=conversation_context,
        school_profile=school_profile,
        context_pack=context_pack,
    )
    return await stack_local_text_call(
        settings=settings,
        instructions=instructions,
        prompt=prompt,
        temperature=0.08,
        max_output_tokens=320,
        top_p=0.9,
    )


async def polish_llamaindex_with_provider(
    *,
    settings: Any,
    request_message: str,
    preview: Any,
    draft_text: str,
    conversation_context: dict[str, Any] | None,
    school_profile: dict[str, Any] | None,
) -> str | None:
    instructions, prompt = _revision_sections(
        request_message=request_message,
        preview=preview,
        draft_text=draft_text,
        conversation_context=conversation_context,
        school_profile=school_profile,
        purpose='polir resposta estruturada sem alterar fatos',
    )
    text = await stack_local_text_call(
        settings=settings,
        instructions=instructions,
        prompt=prompt,
        temperature=0.05,
        max_output_tokens=220,
        top_p=0.9,
    )
    if not text or text == 'KEEP':
        return None
    return text


async def revise_llamaindex_with_provider(
    *,
    settings: Any,
    request_message: str,
    preview: Any,
    draft_text: str,
    conversation_context: dict[str, Any] | None,
    school_profile: dict[str, Any] | None,
) -> str | None:
    instructions, prompt = _revision_sections(
        request_message=request_message,
        preview=preview,
        draft_text=draft_text,
        conversation_context=conversation_context,
        school_profile=school_profile,
        purpose='revisar a resposta final e preservar a cobertura documental correta',
    )
    text = await stack_local_text_call(
        settings=settings,
        instructions=instructions,
        prompt=prompt,
        temperature=0.03,
        max_output_tokens=220,
        top_p=0.9,
    )
    if not text or text == 'KEEP':
        return None
    return text


async def judge_llamaindex_answer_relevance_with_provider(
    *,
    settings: Any,
    request_message: str,
    preview: Any,
    candidate_text: str,
    fallback_text: str,
    public_plan: dict[str, Any] | None,
    slot_memory: dict[str, Any] | None,
) -> dict[str, Any] | None:
    instructions, prompt = _judge_sections(
        request_message=request_message,
        preview=preview,
        candidate_text=candidate_text,
        fallback_text=fallback_text,
        public_plan=public_plan,
        slot_memory=slot_memory,
    )
    return await stack_local_json_call(
        settings=settings,
        instructions=instructions,
        prompt=prompt,
        temperature=0.0,
        max_output_tokens=120,
        top_p=0.9,
    )


async def verify_llamaindex_answer_against_contract(
    *,
    settings: Any,
    request_message: str,
    preview: Any,
    candidate_text: str,
    deterministic_fallback_text: str | None,
    public_plan: Any,
    slot_memory: Any,
) -> tuple[Any, bool]:
    from . import runtime as rt

    deterministic_result = rt._verify_answer_against_contract(
        request_message=request_message,
        preview=preview,
        candidate_text=candidate_text,
        deterministic_fallback_text=deterministic_fallback_text,
        public_plan=public_plan,
        slot_memory=slot_memory,
    )
    should_run_judge = rt._should_run_semantic_answer_judge(
        preview=preview,
        deterministic_fallback_text=deterministic_fallback_text,
        candidate_text=candidate_text,
        public_plan=public_plan,
    )
    if not deterministic_result.valid and (
        deterministic_result.reason is None
        or not str(deterministic_result.reason).startswith(('missing_anchor:', 'missing_term:'))
    ):
        return deterministic_result, False
    if not should_run_judge:
        return deterministic_result, False

    public_plan_payload = None
    if public_plan is not None:
        public_plan_payload = {
            'conversation_act': public_plan.conversation_act,
            'secondary_acts': list(public_plan.secondary_acts),
            'requested_attribute': public_plan.requested_attribute,
            'requested_channel': public_plan.requested_channel,
            'focus_hint': public_plan.focus_hint,
            'semantic_source': public_plan.semantic_source,
            'use_conversation_context': public_plan.use_conversation_context,
        }
    judge_payload = await judge_llamaindex_answer_relevance_with_provider(
        settings=settings,
        request_message=request_message,
        preview=preview,
        candidate_text=candidate_text,
        fallback_text=deterministic_fallback_text or '',
        public_plan=public_plan_payload,
        slot_memory=rt._serialize_slot_memory(slot_memory),
    )
    if not isinstance(judge_payload, dict):
        return deterministic_result, False
    judge_valid = judge_payload.get('valid')
    judge_reason = str(judge_payload.get('reason', '')).strip()
    if judge_valid is False:
        if deterministic_result.valid:
            return rt.AnswerVerificationResult(valid=False, reason=f'semantic_judge:{judge_reason or "mismatch"}'), True
        return deterministic_result, True
    if judge_valid is True and not deterministic_result.valid:
        return rt.AnswerVerificationResult(valid=True), True
    return deterministic_result, True
