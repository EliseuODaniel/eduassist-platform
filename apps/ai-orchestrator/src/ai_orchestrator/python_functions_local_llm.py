from __future__ import annotations

import json
from typing import Any

from .models import CalendarEventCard, MessageResponseCitation
from .prompt_packing_runtime import (
    pack_calendar_lines,
    pack_evidence_lines,
    pack_recent_history,
)
from .stack_local_llm_common import stack_local_json_call, stack_local_text_call

_STACK_LABEL = 'Python Functions'


def _school_name(school_profile: dict[str, Any] | None) -> str:
    return str((school_profile or {}).get('school_name') or 'Colegio Horizonte')


def _citation_lines(citations: list[MessageResponseCitation], context_pack: str | None) -> list[str]:
    lines = [
        f'- {citation.document_title}: {citation.excerpt}'
        for citation in citations[:6]
        if str(citation.excerpt).strip()
    ]
    if context_pack:
        lines.append(f'Contexto documental consolidado: {context_pack}')
    return lines


def _calendar_lines(calendar_events: list[CalendarEventCard]) -> list[str]:
    return [
        f'- {event.title}: {event.description or "sem descricao"}'
        for event in calendar_events[:4]
    ]


def _compose_sections(
    *,
    settings: Any,
    request_message: str,
    analysis_message: str,
    preview: Any,
    citations: list[MessageResponseCitation],
    calendar_events: list[CalendarEventCard],
    conversation_context: dict[str, Any] | None,
    school_profile: dict[str, Any] | None,
    context_pack: str | None,
) -> tuple[str, str]:
    history_block = pack_recent_history(
        settings=settings,
        conversation_context=conversation_context,
    )
    evidence_block = pack_evidence_lines(
        settings=settings,
        evidence_lines=_citation_lines(citations, context_pack),
        empty_text='- nenhuma evidencia documental',
    )
    calendar_block = pack_calendar_lines(
        settings=settings,
        calendar_lines=_calendar_lines(calendar_events),
        empty_text='- nenhum evento estruturado',
    )
    instructions = (
        f'Voce e o compositor final do caminho {_STACK_LABEL} no EduAssist. '
        'Este caminho prioriza roteamento deterministico e respostas enxutas. '
        'Use apenas as evidencias fornecidas e cubra exatamente o que o usuario pediu. '
        'Se a pergunta tiver mais de um item, responda cada item explicitamente. '
        'Nao troque o dominio da pergunta, nao misture alunos ou disciplinas, nao invente fatos. '
        'Mantenha a resposta clara, objetiva e natural. '
        'Devolva apenas a resposta final.'
    )
    prompt = (
        f'Escola: {_school_name(school_profile)}\n'
        f'Pergunta do usuario:\n{request_message}\n\n'
        f'Mensagem expandida para analise:\n{analysis_message}\n\n'
        f'Modo: {preview.mode.value}\n'
        f'Dominio: {preview.classification.domain.value}\n'
        f'Acesso: {preview.classification.access_tier.value}\n\n'
        f'Historico recente:\n{history_block}\n\n'
        f'Eventos estruturados:\n{calendar_block}\n\n'
        f'Evidencias:\n{evidence_block}'
    )
    return instructions, prompt


def _revision_sections(
    *,
    settings: Any,
    request_message: str,
    preview: Any,
    draft_text: str,
    conversation_context: dict[str, Any] | None,
    school_profile: dict[str, Any] | None,
    purpose: str,
) -> tuple[str, str]:
    history_block = pack_recent_history(
        settings=settings,
        conversation_context=conversation_context,
    )
    instructions = (
        f'Voce esta refinando uma resposta do caminho {_STACK_LABEL}. '
        'Melhore apenas clareza, completude e aderencia ao pedido. '
        'Nao adicione fatos novos nem mude o foco do texto. '
        'Se a resposta ja estiver boa, devolva exatamente KEEP. '
        'Devolva somente o texto final.'
    )
    prompt = (
        f'Objetivo: {purpose}\n'
        f'Escola: {_school_name(school_profile)}\n'
        f'Pergunta do usuario:\n{request_message}\n\n'
        f'Modo: {preview.mode.value}\n'
        f'Dominio: {preview.classification.domain.value}\n\n'
        f'Historico recente:\n{history_block}\n\n'
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
        'Decida se a resposta candidata preserva a mesma intencao e o mesmo foco da resposta grounded de referencia. '
        'Marque invalid quando a candidata trocar o assunto, perder o atributo pedido ou responder apenas uma parte importante da pergunta. '
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


async def compose_python_functions_with_provider(
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
        settings=settings,
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
        max_output_tokens=280,
        top_p=0.9,
    )


async def polish_python_functions_with_provider(
    *,
    settings: Any,
    request_message: str,
    preview: Any,
    draft_text: str,
    conversation_context: dict[str, Any] | None,
    school_profile: dict[str, Any] | None,
) -> str | None:
    instructions, prompt = _revision_sections(
        settings=settings,
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
        max_output_tokens=200,
        top_p=0.9,
    )
    if not text or text == 'KEEP':
        return None
    return text


async def revise_python_functions_with_provider(
    *,
    settings: Any,
    request_message: str,
    preview: Any,
    draft_text: str,
    conversation_context: dict[str, Any] | None,
    school_profile: dict[str, Any] | None,
) -> str | None:
    instructions, prompt = _revision_sections(
        settings=settings,
        request_message=request_message,
        preview=preview,
        draft_text=draft_text,
        conversation_context=conversation_context,
        school_profile=school_profile,
        purpose='revisar a resposta final e garantir que todos os itens pedidos foram cobertos',
    )
    text = await stack_local_text_call(
        settings=settings,
        instructions=instructions,
        prompt=prompt,
        temperature=0.03,
        max_output_tokens=200,
        top_p=0.9,
    )
    if not text or text == 'KEEP':
        return None
    return text


async def judge_python_functions_answer_relevance_with_provider(
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


async def verify_python_functions_answer_against_contract(
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
    judge_payload = await judge_python_functions_answer_relevance_with_provider(
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
