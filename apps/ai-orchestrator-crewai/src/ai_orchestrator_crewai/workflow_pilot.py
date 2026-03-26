from __future__ import annotations

from datetime import UTC, date, datetime, timedelta
import re
from typing import Any

import httpx


def _normalize_text(value: str) -> str:
    return ' '.join(str(value or '').strip().lower().split())


def _contains_any(text: str, terms: set[str]) -> bool:
    normalized = _normalize_text(text)
    return any(term in normalized for term in terms)


def _extract_protocol_code(message: str) -> str | None:
    match = re.search(r'\b(?:VIS|REQ)-\d{8}-[A-Z0-9]{6}\b', str(message or '').upper())
    return match.group(0) if match else None


def _extract_preferred_window(message: str) -> str | None:
    normalized = _normalize_text(message)
    if 'manha' in normalized or 'manhã' in normalized:
        return 'manha'
    if 'tarde' in normalized:
        return 'tarde'
    if 'noite' in normalized:
        return 'noite'
    return None


def _extract_preferred_date(message: str) -> date | None:
    normalized = _normalize_text(message)
    weekdays = {
        'segunda': 0,
        'terca': 1,
        'terça': 1,
        'quarta': 2,
        'quinta': 3,
        'sexta': 4,
        'sabado': 5,
        'sábado': 5,
        'domingo': 6,
    }
    today = datetime.now(UTC).date()
    for label, weekday in weekdays.items():
        if label in normalized:
            delta = (weekday - today.weekday()) % 7
            return today + timedelta(days=delta)
    return None


def _render_date(value: str | None) -> str | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value).date().strftime('%d/%m/%Y')
    except ValueError:
        return value


async def _internal_get(settings: Any, path: str, *, params: dict[str, Any]) -> dict[str, Any]:
    base_url = str(getattr(settings, 'api_core_url', 'http://api-core:8000')).rstrip('/')
    async with httpx.AsyncClient(timeout=20.0) as client:
        response = await client.get(
            f'{base_url}{path}',
            params=params,
            headers={'X-Internal-Api-Token': getattr(settings, 'internal_api_token', 'dev-internal-token')},
        )
    response.raise_for_status()
    return response.json()


async def _internal_post(settings: Any, path: str, *, payload: dict[str, Any]) -> dict[str, Any]:
    base_url = str(getattr(settings, 'api_core_url', 'http://api-core:8000')).rstrip('/')
    async with httpx.AsyncClient(timeout=20.0) as client:
        response = await client.post(
            f'{base_url}{path}',
            json=payload,
            headers={
                'Content-Type': 'application/json',
                'X-Internal-Api-Token': getattr(settings, 'internal_api_token', 'dev-internal-token'),
            },
        )
    response.raise_for_status()
    return response.json()


async def _get_workflow_status(
    settings: Any,
    *,
    conversation_id: str,
    channel: str,
    protocol_code: str | None = None,
    workflow_kind: str | None = None,
) -> dict[str, Any]:
    params: dict[str, Any] = {
        'conversation_external_id': conversation_id,
        'channel': channel,
    }
    if protocol_code:
        params['protocol_code'] = protocol_code
    if workflow_kind:
        params['workflow_kind'] = workflow_kind
    return await _internal_get(settings, '/v1/internal/workflows/status', params=params)


def _visit_create_response(item: dict[str, Any]) -> str:
    preferred_date = _render_date(item.get('preferred_date'))
    preferred_window = str(item.get('preferred_window') or '').strip()
    preference = ' - '.join(part for part in [preferred_date, preferred_window] if part) or 'janela a confirmar'
    return (
        'Pedido de visita registrado para o Colegio Horizonte. '
        f"Protocolo: {item.get('protocol_code')}. "
        f"Preferencia informada: {preference}. "
        f"Fila responsavel: {item.get('queue_name')}. "
        f"Ticket operacional: {item.get('linked_ticket_code')}. "
        'A equipe comercial valida a janela e retorna com a confirmacao.'
    )


def _visit_status_response(item: dict[str, Any]) -> str:
    preferred_date = _render_date(item.get('preferred_date'))
    preferred_window = str(item.get('preferred_window') or '').strip()
    preference = ' - '.join(part for part in [preferred_date, preferred_window] if part) or 'janela a confirmar'
    return (
        f"Seu pedido de visita segue em fila com a fila de {item.get('queue_name')}. "
        f"- Protocolo: {item.get('protocol_code')} "
        f"- Ticket operacional: {item.get('linked_ticket_code')} "
        f"- Preferencia registrada: {preference} "
        'Proximo passo: a equipe comercial valida a janela e retorna com a confirmacao.'
    )


def _visit_protocol_response(item: dict[str, Any]) -> str:
    preferred_date = _render_date(item.get('preferred_date'))
    preferred_window = str(item.get('preferred_window') or '').strip()
    preference = ' - '.join(part for part in [preferred_date, preferred_window] if part) or 'janela a confirmar'
    return (
        f"O protocolo da sua visita e {item.get('protocol_code')}. "
        f"- Ticket operacional: {item.get('linked_ticket_code')} "
        f"- Preferencia registrada: {preference} "
        'Se quiser, eu tambem posso te dizer o status, remarcar ou cancelar a visita.'
    )


def _visit_action_response(item: dict[str, Any], *, action: str) -> str:
    if action == 'cancel':
        return (
            f"Visita cancelada no fluxo de {item.get('queue_name')}. "
            f"- Protocolo: {item.get('protocol_code')} "
            f"- Ticket operacional: {item.get('linked_ticket_code')} "
            'Se quiser, eu tambem posso registrar um novo pedido de visita quando voce preferir.'
        )
    preferred_date = _render_date(item.get('preferred_date'))
    preferred_window = str(item.get('preferred_window') or '').strip()
    preference = ' - '.join(part for part in [preferred_date, preferred_window] if part) or 'janela a confirmar'
    return (
        f"Pedido de visita atualizado com a fila de {item.get('queue_name')}. "
        f"- Protocolo: {item.get('protocol_code')} "
        f"- Ticket operacional: {item.get('linked_ticket_code')} "
        f"- Nova preferencia: {preference} "
        'Proximo passo: admissions valida a nova janela e retorna com a confirmacao.'
    )


def _request_create_response(item: dict[str, Any], *, subject: str) -> str:
    return (
        f"Solicitacao institucional registrada para {item.get('target_area')}. "
        f"Protocolo: {item.get('protocol_code')}. "
        f"Assunto: {subject}. "
        f"Fila responsavel: {item.get('queue_name')}. "
        f"Ticket operacional: {item.get('linked_ticket_code')}. "
        'A equipe faz a triagem inicial e segue o retorno pelo fluxo institucional.'
    )


def _request_protocol_response(item: dict[str, Any]) -> str:
    return (
        f"O protocolo da sua solicitacao e {item.get('protocol_code')}. "
        f"- Ticket operacional: {item.get('linked_ticket_code')} "
        f"- Area responsavel: {item.get('target_area')} "
        'Se quiser, eu tambem posso resumir o pedido ou verificar o status atual.'
    )


def _request_summary_response(item: dict[str, Any]) -> str:
    subject = str(item.get('subject') or '').strip()
    return (
        'Resumo da sua solicitacao institucional: '
        f"- Assunto: {subject} "
        f"- Area responsavel: {item.get('target_area')} "
        f"- Protocolo: {item.get('protocol_code')} "
        f"- Ticket operacional: {item.get('linked_ticket_code')} "
        f"- Status atual: {item.get('status')} "
        'Se quiser, eu tambem posso te dizer o prazo estimado ou quem responde por essa fila.'
    )


def _request_status_response(item: dict[str, Any]) -> str:
    return (
        f"Sua solicitacao segue em fila com a area de {item.get('queue_name')}. "
        f"- Protocolo: {item.get('protocol_code')} "
        f"- Ticket operacional: {item.get('linked_ticket_code')} "
        f"- Status atual: {item.get('status')} "
        'Proximo passo: a equipe responsavel recebe essa atualizacao e segue o retorno pelo fluxo institucional.'
    )


def _request_action_response(item: dict[str, Any], *, detail: str) -> str:
    return (
        f"Complemento registrado na fila de {item.get('queue_name')}. "
        f"- Protocolo: {item.get('protocol_code')} "
        f"- Ticket operacional: {item.get('linked_ticket_code')} "
        f"- Novo complemento: {detail} "
        'Proximo passo: a equipe responsavel recebe essa atualizacao no mesmo fluxo do pedido.'
    )


async def run_workflow_crewai_pilot(
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
            'reason': 'missing_conversation_id_for_workflow',
            'metadata': {'slice_name': 'workflow'},
        }

    normalized = _normalize_text(message)
    protocol_code = _extract_protocol_code(message)
    workflow_status = await _get_workflow_status(
        settings,
        conversation_id=conversation_external_id,
        channel=channel,
        protocol_code=protocol_code,
    )
    current_item = workflow_status.get('item') if isinstance(workflow_status, dict) else None
    current_type = str(current_item.get('workflow_type') or '').strip() if isinstance(current_item, dict) else ''

    visit_terms = {'visita', 'tour', 'conhecer a escola'}
    request_terms = {'direcao', 'direção', 'protocolo', 'protocolar', 'solicitacao', 'solicitação', 'pedido'}

    if _contains_any(normalized, visit_terms) and _contains_any(normalized, {'cancelar', 'desmarcar'}):
        payload = await _internal_post(
            settings,
            '/v1/internal/workflows/visit-bookings/actions',
            payload={
                'conversation_external_id': conversation_external_id,
                'channel': channel,
                'telegram_chat_id': telegram_chat_id,
                'protocol_code': protocol_code or (current_item or {}).get('protocol_code'),
                'action': 'cancel',
                'notes': message,
            },
        )
        item = payload.get('item', {})
        return {'engine_name': 'crewai', 'executed': True, 'reason': 'workflow_visit_cancel', 'metadata': {'slice_name': 'workflow', 'answer': {'answer_text': _visit_action_response(item, action='cancel')}, 'workflow_type': 'visit'}}

    if _contains_any(normalized, visit_terms) and _contains_any(normalized, {'remarcar', 'reagendar', 'mudar'}):
        payload = await _internal_post(
            settings,
            '/v1/internal/workflows/visit-bookings/actions',
            payload={
                'conversation_external_id': conversation_external_id,
                'channel': channel,
                'telegram_chat_id': telegram_chat_id,
                'protocol_code': protocol_code or (current_item or {}).get('protocol_code'),
                'action': 'reschedule',
                'preferred_date': (_extract_preferred_date(message) or date.today()).isoformat(),
                'preferred_window': _extract_preferred_window(message),
                'notes': message,
            },
        )
        item = payload.get('item', {})
        return {'engine_name': 'crewai', 'executed': True, 'reason': 'workflow_visit_reschedule', 'metadata': {'slice_name': 'workflow', 'answer': {'answer_text': _visit_action_response(item, action='reschedule')}, 'workflow_type': 'visit'}}

    if _contains_any(normalized, visit_terms) and _contains_any(normalized, {'agendar', 'marcar', 'quero'}) and 'visita' in normalized:
        payload = await _internal_post(
            settings,
            '/v1/internal/workflows/visit-bookings',
            payload={
                'conversation_external_id': conversation_external_id,
                'channel': channel,
                'telegram_chat_id': telegram_chat_id,
                'preferred_date': _extract_preferred_date(message).isoformat() if _extract_preferred_date(message) else None,
                'preferred_window': _extract_preferred_window(message),
                'notes': message,
            },
        )
        item = payload.get('item', {})
        return {'engine_name': 'crewai', 'executed': True, 'reason': 'workflow_visit_create', 'metadata': {'slice_name': 'workflow', 'answer': {'answer_text': _visit_create_response(item)}, 'workflow_type': 'visit'}}

    if _contains_any(normalized, {'status', 'andamento'}) or 'qual o protocolo' in normalized or 'resume meu pedido' in normalized:
        if not isinstance(current_item, dict):
            return {'engine_name': 'crewai', 'executed': True, 'reason': 'workflow_not_found', 'metadata': {'slice_name': 'workflow', 'answer': {'answer_text': 'Nao encontrei um protocolo ativo nesta conversa para retomar agora.'}, 'workflow_type': 'unknown'}}
        if 'qual o protocolo' in normalized:
            if current_type == 'visit_booking':
                text = _visit_protocol_response(current_item)
            else:
                text = _request_protocol_response(current_item)
            return {'engine_name': 'crewai', 'executed': True, 'reason': 'workflow_protocol_lookup', 'metadata': {'slice_name': 'workflow', 'answer': {'answer_text': text}, 'workflow_type': current_type}}
        if 'resume meu pedido' in normalized:
            text = _request_summary_response(current_item) if current_type == 'institutional_request' else _visit_status_response(current_item)
            return {'engine_name': 'crewai', 'executed': True, 'reason': 'workflow_summary_lookup', 'metadata': {'slice_name': 'workflow', 'answer': {'answer_text': text}, 'workflow_type': current_type}}
        text = _visit_status_response(current_item) if current_type == 'visit_booking' else _request_status_response(current_item)
        return {'engine_name': 'crewai', 'executed': True, 'reason': 'workflow_status_lookup', 'metadata': {'slice_name': 'workflow', 'answer': {'answer_text': text}, 'workflow_type': current_type}}

    if _contains_any(normalized, request_terms) and _contains_any(normalized, {'protocolar', 'solicitacao', 'solicitação', 'pedido'}):
        payload = await _internal_post(
            settings,
            '/v1/internal/workflows/institutional-requests',
            payload={
                'conversation_external_id': conversation_external_id,
                'channel': channel,
                'telegram_chat_id': telegram_chat_id,
                'target_area': 'direcao' if _contains_any(normalized, {'direcao', 'direção'}) else 'atendimento',
                'category': 'solicitacao_institucional',
                'subject': message,
                'details': message,
            },
        )
        item = payload.get('item', {})
        return {'engine_name': 'crewai', 'executed': True, 'reason': 'workflow_request_create', 'metadata': {'slice_name': 'workflow', 'answer': {'answer_text': _request_create_response(item, subject=message)}, 'workflow_type': 'request'}}

    if _contains_any(normalized, {'complementar', 'acrescentar', 'adicionar', 'incluir'}) and current_type == 'institutional_request':
        payload = await _internal_post(
            settings,
            '/v1/internal/workflows/institutional-requests/actions',
            payload={
                'conversation_external_id': conversation_external_id,
                'channel': channel,
                'telegram_chat_id': telegram_chat_id,
                'protocol_code': protocol_code or (current_item or {}).get('protocol_code'),
                'action': 'add_details',
                'details': message,
            },
        )
        item = payload.get('item', {})
        detail = message.replace('quero complementar meu pedido dizendo que', '').strip() or message
        return {'engine_name': 'crewai', 'executed': True, 'reason': 'workflow_request_update', 'metadata': {'slice_name': 'workflow', 'answer': {'answer_text': _request_action_response(item, detail=detail)}, 'workflow_type': 'request'}}

    return {
        'engine_name': 'crewai',
        'executed': False,
        'reason': 'workflow_not_supported',
        'metadata': {'slice_name': 'workflow'},
    }
