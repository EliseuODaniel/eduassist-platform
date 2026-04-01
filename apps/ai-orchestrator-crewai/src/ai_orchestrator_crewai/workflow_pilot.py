from __future__ import annotations

from datetime import UTC, date, datetime, timedelta
import re
from typing import Any

import httpx

from .flow_persistence import build_flow_state_id
from .listeners import suppress_crewai_tracing_messages


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


def _weekday_label_for_iso_date(value: str | None) -> str | None:
    if not value:
        return None
    try:
        weekday = datetime.fromisoformat(value).date().weekday()
    except ValueError:
        return None
    labels = {
        0: 'segunda-feira',
        1: 'terca-feira',
        2: 'quarta-feira',
        3: 'quinta-feira',
        4: 'sexta-feira',
        5: 'sabado',
        6: 'domingo',
    }
    return labels.get(weekday)


def _render_visit_preference(
    item: dict[str, Any],
    *,
    preferred_date_override: str | None = None,
    preferred_window_override: str | None = None,
) -> str:
    preferred_date_value = str(preferred_date_override or item.get('preferred_date') or '').strip() or None
    preferred_date = _render_date(preferred_date_value)
    preferred_window = str(preferred_window_override or '').strip()
    slot_label = str(item.get('slot_label') or '').strip()
    canonical_window = str(item.get('preferred_window') or '').strip()
    if not preferred_window:
        preferred_window = canonical_window

    weekday_label = _weekday_label_for_iso_date(preferred_date_value)
    display_label = slot_label
    if weekday_label and preferred_window:
        display_label = f'{weekday_label} - {preferred_window}'
        if slot_label:
            display_label += f' ({slot_label})'
    elif weekday_label:
        display_label = weekday_label if not slot_label else f'{weekday_label} ({slot_label})'
    elif preferred_date and preferred_window and preferred_window != canonical_window:
        display_label = f'{preferred_date} - {preferred_window}'
        if slot_label:
            display_label += f' ({slot_label})'
    elif preferred_date and preferred_window:
        display_label = ' - '.join(part for part in [preferred_date, preferred_window] if part)
    elif preferred_date and slot_label:
        display_label = f'{preferred_date} ({slot_label})'
    elif preferred_date:
        display_label = preferred_date
    elif preferred_window and slot_label and preferred_window != canonical_window:
        display_label = f'{preferred_window} ({slot_label})'
    elif preferred_window:
        display_label = preferred_window

    return display_label or 'janela a confirmar'


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


def _visit_create_response(
    item: dict[str, Any],
    *,
    preferred_date_override: str | None = None,
    preferred_window_override: str | None = None,
) -> str:
    preference = _render_visit_preference(
        item,
        preferred_date_override=preferred_date_override,
        preferred_window_override=preferred_window_override,
    )
    return (
        'Pedido de visita registrado para o Colegio Horizonte. '
        f"Protocolo: {item.get('protocol_code')}. "
        f"Preferencia informada: {preference}. "
        f"Fila responsavel: {item.get('queue_name')}. "
        f"Ticket operacional: {item.get('linked_ticket_code')}. "
        'A equipe comercial valida a janela e retorna com a confirmacao.'
    )


def _visit_status_response(
    item: dict[str, Any],
    *,
    preferred_date_override: str | None = None,
    preferred_window_override: str | None = None,
) -> str:
    preference = _render_visit_preference(
        item,
        preferred_date_override=preferred_date_override,
        preferred_window_override=preferred_window_override,
    )
    return (
        f"Seu pedido de visita segue em fila com a fila de {item.get('queue_name')}. "
        f"- Protocolo: {item.get('protocol_code')} "
        f"- Ticket operacional: {item.get('linked_ticket_code')} "
        f"- Preferencia registrada: {preference} "
        'Proximo passo: a equipe comercial valida a janela e retorna com a confirmacao.'
    )


def _visit_protocol_response(
    item: dict[str, Any],
    *,
    preferred_date_override: str | None = None,
    preferred_window_override: str | None = None,
) -> str:
    preference = _render_visit_preference(
        item,
        preferred_date_override=preferred_date_override,
        preferred_window_override=preferred_window_override,
    )
    return (
        f"O protocolo da sua visita e {item.get('protocol_code')}. "
        f"- Ticket operacional: {item.get('linked_ticket_code')} "
        f"- Preferencia registrada: {preference} "
        'Se quiser, eu tambem posso te dizer o status, remarcar ou cancelar a visita.'
    )


def _visit_action_response(
    item: dict[str, Any],
    *,
    action: str,
    preferred_date_override: str | None = None,
    preferred_window_override: str | None = None,
) -> str:
    if action == 'cancel':
        return (
            f"Visita cancelada no fluxo de {item.get('queue_name')}. "
            f"- Protocolo: {item.get('protocol_code')} "
            f"- Ticket operacional: {item.get('linked_ticket_code')} "
            'Se quiser, eu tambem posso registrar um novo pedido de visita quando voce preferir.'
        )
    preference = _render_visit_preference(
        item,
        preferred_date_override=preferred_date_override,
        preferred_window_override=preferred_window_override,
    )
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
    user_context: dict[str, Any] | None,
    settings: Any,
) -> dict[str, Any]:
    from .workflow_flow import WorkflowShadowFlow

    flow = WorkflowShadowFlow(settings=settings)
    with suppress_crewai_tracing_messages():
        result = await flow.kickoff_async(
            inputs={
                'id': build_flow_state_id(
                    slice_name='workflow',
                    conversation_id=conversation_id or (
                        f'telegram:{telegram_chat_id}' if channel == 'telegram' and telegram_chat_id is not None else None
                    ),
                    telegram_chat_id=telegram_chat_id,
                    channel=channel,
                ),
                'message': message,
                'conversation_id': conversation_id or (
                    f'telegram:{telegram_chat_id}' if channel == 'telegram' and telegram_chat_id is not None else None
                ),
                'telegram_chat_id': telegram_chat_id,
                'channel': channel,
                'user_context': user_context,
            }
        )
    if isinstance(result, dict):
        return result
    return {
        'engine_name': 'crewai',
        'executed': False,
        'reason': 'crewai_workflow_flow_unexpected_output',
        'metadata': {
            'slice_name': 'workflow',
            'conversation_id': conversation_id,
        },
    }
