from __future__ import annotations

import re
from typing import Any

from .workflow_pilot import _internal_get, _internal_post, _normalize_text


SUPPORT_TICKET_PATTERN = re.compile(r'\bATD-\d{8}-[A-Z0-9]{8}\b', re.IGNORECASE)


def _extract_ticket_code(message: str) -> str | None:
    match = SUPPORT_TICKET_PATTERN.search(str(message or '').upper())
    return match.group(0) if match else None


def _detect_queue(message: str) -> str:
    normalized = _normalize_text(message)
    if 'financeir' in normalized or 'mensalidad' in normalized or 'boleto' in normalized:
        return 'financeiro'
    if 'secretari' in normalized:
        return 'secretaria'
    if 'direc' in normalized:
        return 'direcao'
    if 'orienta' in normalized or 'bullying' in normalized or 'emocional' in normalized:
        return 'orientacao'
    if 'matricul' in normalized or 'visita' in normalized or 'admiss' in normalized:
        return 'admissoes'
    return 'atendimento'


def _wants_human_handoff(message: str) -> bool:
    normalized = _normalize_text(message)
    markers = (
        'atendente humano',
        'atendimento humano',
        'quero falar com um humano',
        'preciso falar com um humano',
        'quero falar com o setor',
        'quero falar com a secretaria',
        'quero falar com o financeiro',
        'nao resolveu',
        'não resolveu',
        'atendente',
        'humano',
        'suporte',
    )
    return any(marker in normalized for marker in markers)


def _is_status_request(message: str) -> bool:
    normalized = _normalize_text(message)
    return any(
        marker in normalized
        for marker in (
            'qual o status',
            'como esta',
            'como está',
            'segue na fila',
            'fila',
            'status atual',
        )
    )


def _is_protocol_request(message: str) -> bool:
    normalized = _normalize_text(message)
    return 'protocolo' in normalized


def _is_summary_request(message: str) -> bool:
    normalized = _normalize_text(message)
    return any(marker in normalized for marker in ('resuma', 'resume', 'resumir', 'resumo'))


def _is_repair_turn(message: str) -> bool:
    normalized = _normalize_text(message)
    return any(marker in normalized for marker in ('cheguei agora', 'agora que cheguei', 'vim agora'))


async def _get_support_status(
    settings: Any,
    *,
    conversation_id: str,
    channel: str,
    protocol_code: str | None = None,
) -> dict[str, Any]:
    params: dict[str, Any] = {
        'conversation_external_id': conversation_id,
        'channel': channel,
        'workflow_kind': 'support_handoff',
    }
    if protocol_code:
        params['protocol_code'] = protocol_code
    return await _internal_get(settings, '/v1/internal/workflows/status', params=params)


def _handoff_create_response(item: dict[str, Any], *, created: bool) -> str:
    queue_name = str(item.get('queue_name') or 'atendimento')
    ticket_code = str(item.get('ticket_code') or item.get('linked_ticket_code') or '')
    status = str(item.get('status') or 'queued')
    if created:
        return (
            f"Encaminhei sua solicitacao para a fila de {queue_name}. "
            f"Protocolo: {ticket_code}. "
            f"Status atual: {status}. "
            'A equipe humana podera continuar esse atendimento no portal operacional.'
        )
    return (
        f"Sua solicitacao ja estava registrada na fila de {queue_name}. "
        f"Protocolo: {ticket_code}. "
        f"Status atual: {status}."
    )


def _handoff_protocol_response(item: dict[str, Any]) -> str:
    ticket_code = str(item.get('protocol_code') or item.get('linked_ticket_code') or '')
    return (
        f"O protocolo do seu atendimento e {ticket_code}. "
        'Se quiser, posso verificar o status atual ou te dar um resumo do que ja foi registrado.'
    )


def _handoff_status_response(item: dict[str, Any]) -> str:
    ticket_code = str(item.get('protocol_code') or item.get('linked_ticket_code') or '')
    status = str(item.get('status') or 'queued')
    queue_name = str(item.get('queue_name') or 'atendimento')
    return (
        f"O protocolo do seu atendimento e {ticket_code}. "
        f'O status atual e "{status}", o que significa que sua solicitacao esta na fila para ser atendida pela equipe de {queue_name}.'
    )


def _handoff_summary_response(item: dict[str, Any]) -> str:
    ticket_code = str(item.get('protocol_code') or item.get('linked_ticket_code') or '')
    status = str(item.get('status') or 'queued')
    queue_name = str(item.get('queue_name') or 'atendimento')
    summary = str(item.get('summary') or 'Atendimento institucional').strip()
    return (
        'Resumo do seu atendimento humano: '
        f"- Fila responsavel: {queue_name} "
        f"- Protocolo: {ticket_code} "
        f"- Status atual: {status} "
        f"- Resumo registrado: {summary}"
    )


def _repair_response() -> str:
    return (
        'Sem problema, vamos comecar do zero entao. '
        'Se voce quiser atendimento humano por aqui, me diga em uma frase curta qual e o assunto como financeiro, secretaria, matricula ou direcao, e eu sigo desse ponto.'
    )


async def run_support_crewai_pilot(
    *,
    message: str,
    conversation_id: str | None,
    telegram_chat_id: int | None,
    channel: str,
    settings: Any,
) -> dict[str, Any]:
    conversation_external_id = str(conversation_id or '').strip()
    if not conversation_external_id:
        return {
            'engine_name': 'crewai',
            'executed': False,
            'reason': 'missing_conversation_id_for_support',
            'metadata': {'slice_name': 'support'},
        }

    normalized = _normalize_text(message)
    ticket_code = _extract_ticket_code(message)
    support_status = await _get_support_status(
        settings,
        conversation_id=conversation_external_id,
        channel=channel,
        protocol_code=ticket_code,
    )
    current_item = support_status.get('item') if isinstance(support_status, dict) else None

    if _is_repair_turn(normalized):
        return {
            'engine_name': 'crewai',
            'executed': True,
            'reason': 'support_repair',
            'metadata': {
                'slice_name': 'support',
                'answer': {'answer_text': _repair_response()},
            },
        }

    if _wants_human_handoff(message):
        queue_name = _detect_queue(message)
        payload = await _internal_post(
            settings,
            '/v1/internal/support/handoffs',
            payload={
                'conversation_external_id': conversation_external_id,
                'channel': channel,
                'queue_name': queue_name,
                'summary': f'Atendimento humano solicitado para {queue_name}',
                'telegram_chat_id': telegram_chat_id,
                'user_message': message,
            },
        )
        item = payload.get('item') if isinstance(payload, dict) else {}
        created = bool(payload.get('created'))
        return {
            'engine_name': 'crewai',
            'executed': True,
            'reason': 'support_handoff_created' if created else 'support_handoff_reused',
            'metadata': {
                'slice_name': 'support',
                'queue_name': queue_name,
                'created': created,
                'answer': {'answer_text': _handoff_create_response(item, created=created)},
            },
        }

    if isinstance(current_item, dict) and (_is_protocol_request(message) or _is_status_request(message) or _is_summary_request(message)):
        if _is_protocol_request(message) and not _is_status_request(message):
            answer_text = _handoff_protocol_response(current_item)
            reason = 'support_protocol'
        elif _is_summary_request(message):
            answer_text = _handoff_summary_response(current_item)
            reason = 'support_summary'
        else:
            answer_text = _handoff_status_response(current_item)
            reason = 'support_status'
        return {
            'engine_name': 'crewai',
            'executed': True,
            'reason': reason,
            'metadata': {
                'slice_name': 'support',
                'ticket_code': current_item.get('protocol_code'),
                'answer': {'answer_text': answer_text},
            },
        }

    return {
        'engine_name': 'crewai',
        'executed': False,
        'reason': 'support_not_supported',
        'metadata': {'slice_name': 'support'},
    }
