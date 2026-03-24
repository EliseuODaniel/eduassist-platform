from __future__ import annotations

import base64
from functools import lru_cache
import secrets

import httpx
from fastapi import FastAPI, Header, HTTPException, Request
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict
from eduassist_observability import configure_observability


class Settings(BaseSettings):
    model_config = SettingsConfigDict(case_sensitive=False)

    app_env: str = 'development'
    log_level: str = 'INFO'
    port: int = 8000
    telegram_bot_token: str | None = None
    telegram_bot_username: str | None = None
    telegram_webhook_secret: str = 'change-me'
    api_core_url: str = 'http://api-core:8000'
    ai_orchestrator_url: str = 'http://ai-orchestrator:8000'
    internal_api_token: str = 'dev-internal-token'
    telegram_api_base_url: str = 'https://api.telegram.org'


@lru_cache
def get_settings() -> Settings:
    return Settings()


class HealthResponse(BaseModel):
    status: str
    service: str
    ready: bool


app = FastAPI(
    title='EduAssist Telegram Gateway',
    version='0.2.0',
    summary='Telegram ingress bootstrap for EduAssist Platform.',
)

configure_observability(
    service_name='telegram-gateway',
    service_version=app.version,
    environment=get_settings().app_env,
    app=app,
    excluded_urls='/healthz,/meta',
)


def _require_internal_api_token(x_internal_api_token: str | None) -> None:
    settings = get_settings()
    if not x_internal_api_token or not secrets.compare_digest(x_internal_api_token, settings.internal_api_token):
        raise HTTPException(status_code=401, detail='invalid_internal_api_token')


def _extract_message(payload: dict[str, object]) -> dict[str, object] | None:
    for key in ('message', 'edited_message'):
        value = payload.get(key)
        if isinstance(value, dict):
            return value
    return None


def _extract_link_code(text: str) -> str | None:
    if text.startswith('/start '):
        payload = text.split(' ', 1)[1].strip()
        if payload.startswith('link_'):
            return payload[len('link_') :]
    if text.startswith('/link '):
        return text.split(' ', 1)[1].strip()
    return None


async def _send_telegram_message(chat_id: int, text: str) -> None:
    settings = get_settings()
    if not settings.telegram_bot_token:
        return

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            await client.post(
                f'{settings.telegram_api_base_url}/bot{settings.telegram_bot_token}/sendMessage',
                json={'chat_id': chat_id, 'text': text},
            )
    except Exception:
        return


async def _send_telegram_photo(chat_id: int, image_bytes: bytes, *, caption: str | None = None) -> None:
    settings = get_settings()
    if not settings.telegram_bot_token:
        return

    data = {'chat_id': str(chat_id)}
    if caption:
        data['caption'] = caption[:1024]

    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            await client.post(
                f'{settings.telegram_api_base_url}/bot{settings.telegram_bot_token}/sendPhoto',
                data=data,
                files={'photo': ('eduassist-visual.png', image_bytes, 'image/png')},
            )
    except Exception:
        return


async def _consume_link_code(message: dict[str, object], challenge_code: str) -> dict[str, object]:
    settings = get_settings()

    chat = message.get('chat') if isinstance(message.get('chat'), dict) else {}
    sender = message.get('from') if isinstance(message.get('from'), dict) else {}
    chat_id = int(chat['id'])

    payload = {
        'challenge_code': challenge_code,
        'telegram_user_id': int(sender['id']) if sender.get('id') is not None else None,
        'telegram_chat_id': chat_id,
        'username': sender.get('username'),
        'first_name': sender.get('first_name'),
        'last_name': sender.get('last_name'),
    }

    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.post(
            f'{settings.api_core_url}/v1/internal/telegram/link/consume',
            headers={'X-Internal-Api-Token': settings.internal_api_token},
            json=payload,
        )
    response.raise_for_status()
    data = response.json()

    actor_name = data.get('actor', {}).get('full_name', 'usuario')
    await _send_telegram_message(
        chat_id,
        f'Conta vinculada com sucesso a {actor_name}. Agora voce pode usar os fluxos autenticados do bot.',
    )
    return data


@app.get('/healthz', response_model=HealthResponse)
async def healthz() -> HealthResponse:
    return HealthResponse(
        status='ok',
        service='telegram-gateway',
        ready=True,
    )


@app.get('/meta')
async def meta(
    x_internal_api_token: str | None = Header(default=None, alias='X-Internal-Api-Token'),
) -> dict[str, str | None]:
    _require_internal_api_token(x_internal_api_token)
    settings = get_settings()
    return {
        'service': 'telegram-gateway',
        'environment': settings.app_env,
        'botUsername': settings.telegram_bot_username,
        'telegramConfigured': 'yes' if settings.telegram_bot_token else 'no',
    }


@app.get('/webhooks/telegram')
async def webhook_info() -> dict[str, object]:
    return {
        'service': 'telegram-gateway',
        'ready': True,
        'message': 'Use POST on this endpoint for Telegram updates.',
    }


def _map_role(role_code: str | None) -> str:
    allowed = {
        'guardian',
        'student',
        'teacher',
        'staff',
        'finance',
        'coordinator',
        'admin',
    }
    if role_code in allowed:
        return role_code
    return 'anonymous'


async def _resolve_actor_context(chat_id: int) -> dict[str, object] | None:
    settings = get_settings()
    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            response = await client.get(
                f'{settings.api_core_url}/v1/internal/identity/context',
                headers={'X-Internal-Api-Token': settings.internal_api_token},
                params={'telegram_chat_id': chat_id},
            )
        response.raise_for_status()
    except Exception:
        return None

    payload = response.json()
    actor = payload.get('actor')
    return actor if isinstance(actor, dict) else None


def _build_user_context(actor: dict[str, object] | None) -> dict[str, object]:
    if actor is None:
        return {
            'role': 'anonymous',
            'authenticated': False,
            'linked_student_ids': [],
            'scopes': [],
        }

    linked_student_ids = actor.get('linked_student_ids')
    return {
        'role': _map_role(actor.get('role_code') if isinstance(actor.get('role_code'), str) else None),
        'authenticated': True,
        'linked_student_ids': linked_student_ids if isinstance(linked_student_ids, list) else [],
        'scopes': [],
    }


def _default_help_message() -> str:
    return (
        'EduAssist esta pronto para orientar sobre informacoes publicas da escola. '
        'Voce pode perguntar sobre calendario, matricula, secretaria e atendimento digital. '
        'Para consultas protegidas, vincule sua conta pelo portal e envie o codigo ao bot.'
    )


async def _orchestrate_message(
    *,
    chat_id: int,
    text: str,
    update_id: int | None,
) -> dict[str, object]:
    settings = get_settings()
    actor = await _resolve_actor_context(chat_id)
    user_context = _build_user_context(actor)

    payload = {
        'message': text,
        'conversation_id': f'telegram:{chat_id}',
        'telegram_chat_id': chat_id,
        'channel': 'telegram',
        'user': user_context,
    }

    async with httpx.AsyncClient(timeout=20.0) as client:
        response = await client.post(
            f'{settings.ai_orchestrator_url}/v1/messages/respond',
            headers={'X-Internal-Api-Token': settings.internal_api_token},
            json=payload,
        )
    response.raise_for_status()
    return response.json()


@app.post('/webhooks/telegram')
async def telegram_webhook(
    request: Request,
    x_telegram_bot_api_secret_token: str | None = Header(default=None),
) -> dict[str, object]:
    settings = get_settings()
    if x_telegram_bot_api_secret_token != settings.telegram_webhook_secret:
        raise HTTPException(status_code=401, detail='Invalid Telegram webhook secret.')

    payload = await request.json()
    update_id = payload.get('update_id') if isinstance(payload, dict) else None
    message = _extract_message(payload if isinstance(payload, dict) else {})
    if message is None:
        return {
            'accepted': True,
            'service': 'telegram-gateway',
            'processed': 'noop',
            'payloadKeys': sorted(payload.keys()) if isinstance(payload, dict) else [],
        }

    text = message.get('text')
    if not isinstance(text, str):
        return {
            'accepted': True,
            'service': 'telegram-gateway',
            'processed': 'non_text_message',
            'payloadKeys': sorted(payload.keys()),
        }

    challenge_code = _extract_link_code(text)
    if challenge_code is None:
        chat = message.get('chat') if isinstance(message.get('chat'), dict) else {}
        chat_id = int(chat['id']) if chat.get('id') is not None else None
        if chat_id is None:
            return {
                'accepted': True,
                'service': 'telegram-gateway',
                'processed': 'missing_chat',
            }

        if text.strip() in {'/start', '/help'}:
            help_text = _default_help_message()
            await _send_telegram_message(chat_id, help_text)
            return {
                'accepted': True,
                'service': 'telegram-gateway',
                'processed': 'help_message',
                'reply': help_text,
            }

        try:
            orchestration = await _orchestrate_message(
                chat_id=chat_id,
                text=text,
                update_id=update_id if isinstance(update_id, int) else None,
            )
            reply_text = str(orchestration.get('message_text', _default_help_message()))
            await _send_telegram_message(chat_id, reply_text)
            visual_assets = orchestration.get('visual_assets', [])
            if isinstance(visual_assets, list):
                for asset in visual_assets:
                    if not isinstance(asset, dict):
                        continue
                    if str(asset.get('mime_type', '')).lower() != 'image/png':
                        continue
                    encoded = asset.get('base64_data')
                    if not isinstance(encoded, str) or not encoded:
                        continue
                    try:
                        image_bytes = base64.b64decode(encoded)
                    except Exception:
                        continue
                    await _send_telegram_photo(
                        chat_id,
                        image_bytes,
                        caption=str(asset.get('caption') or asset.get('title') or 'Visual institucional'),
                    )
            return {
                'accepted': True,
                'service': 'telegram-gateway',
                'processed': 'orchestrated_message',
                'reply': reply_text,
                'orchestration': orchestration,
            }
        except httpx.HTTPError as exc:
            fallback_text = (
                'Nao consegui consultar a base da escola agora. '
                'Tente novamente em instantes ou use o portal institucional.'
            )
            await _send_telegram_message(chat_id, fallback_text)
            return {
                'accepted': True,
                'service': 'telegram-gateway',
                'processed': 'orchestration_error',
                'reply': fallback_text,
                'detail': str(exc),
            }

    try:
        link_response = await _consume_link_code(message, challenge_code)
        return {
            'accepted': True,
            'service': 'telegram-gateway',
            'processed': 'telegram_link',
            'linkResponse': link_response,
        }
    except httpx.HTTPStatusError as exc:
        detail = exc.response.text
        chat = message.get('chat') if isinstance(message.get('chat'), dict) else {}
        if chat.get('id') is not None:
            await _send_telegram_message(
                int(chat['id']),
                'Nao foi possivel concluir o vinculo agora. Gere um novo codigo no portal e tente novamente.',
            )
        return {
            'accepted': True,
            'service': 'telegram-gateway',
            'processed': 'telegram_link_error',
            'statusCode': exc.response.status_code,
            'detail': detail,
        }
