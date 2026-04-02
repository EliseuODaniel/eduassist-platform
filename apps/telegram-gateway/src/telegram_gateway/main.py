from __future__ import annotations

import base64
from collections import OrderedDict
from functools import lru_cache
import logging
from pathlib import Path
import secrets
from threading import Lock
from time import monotonic

import httpx
from fastapi import BackgroundTasks, FastAPI, Header, HTTPException, Request
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict
from eduassist_observability import build_runtime_diagnostics, configure_observability


_ROOT_ENV_FILE = Path(__file__).resolve().parents[4] / '.env'
_RECENT_TELEGRAM_UPDATE_IDS: OrderedDict[int, float] = OrderedDict()
_TELEGRAM_UPDATE_DEDUPE_LOCK = Lock()
_TELEGRAM_UPDATE_DEDUPE_TTL_SECONDS = 60.0 * 15.0
_TELEGRAM_UPDATE_DEDUPE_LIMIT = 4096


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        case_sensitive=False,
        env_file=('/workspace/.env', str(_ROOT_ENV_FILE), '.env'),
        env_ignore_empty=True,
        extra='ignore',
    )

    app_env: str = 'development'
    log_level: str = 'INFO'
    port: int = 8000
    telegram_bot_token: str | None = None
    telegram_bot_username: str | None = None
    telegram_webhook_secret: str = 'change-me'
    api_core_url: str = 'http://api-core:8000'
    ai_orchestrator_url: str = 'http://ai-orchestrator:8000'
    ai_orchestrator_timeout_seconds: float = 45.0
    graph_rag_async_timeout_seconds: float = 480.0
    graph_rag_async_max_seconds: int = 420
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

logger = logging.getLogger(__name__)


def _require_internal_api_token(x_internal_api_token: str | None) -> None:
    settings = get_settings()
    if not x_internal_api_token or not secrets.compare_digest(x_internal_api_token, settings.internal_api_token):
        raise HTTPException(status_code=401, detail='invalid_internal_api_token')


def _telegram_runtime_diagnostics(settings: Settings) -> dict[str, object]:
    return build_runtime_diagnostics(
        service_name='telegram-gateway',
        env_file_candidates=('/workspace/.env', str(_ROOT_ENV_FILE), '.env'),
        service_checks=[
            {'name': 'api_core', 'endpoint': settings.api_core_url, 'required': True},
            {'name': 'ai_orchestrator', 'endpoint': settings.ai_orchestrator_url, 'required': True},
            {
                'name': 'telegram_api',
                'endpoint': settings.telegram_api_base_url,
                'required': True,
                'allow_localhost_in_container': False,
                'allow_service_dns_in_source': True,
            },
        ],
        secret_checks=[
            {
                'name': 'telegram_bot_token',
                'value': settings.telegram_bot_token,
                'required': True,
            },
            {
                'name': 'telegram_webhook_secret',
                'value': settings.telegram_webhook_secret,
                'required': True,
                'placeholder_values': ('change-me',),
            },
            {
                'name': 'internal_api_token',
                'value': settings.internal_api_token,
                'required': True,
                'placeholder_values': ('dev-internal-token',),
            },
        ],
    )


def _log_runtime_diagnostics(diagnostics: dict[str, object]) -> None:
    warnings = diagnostics.get('warnings') if isinstance(diagnostics.get('warnings'), list) else []
    blockers = diagnostics.get('blockers') if isinstance(diagnostics.get('blockers'), list) else []
    logger.info(
        'telegram_gateway_runtime_diagnostics',
        extra={
            'operational_readiness': bool(diagnostics.get('operationalReadiness')),
            'runtime_mode': diagnostics.get('runtimeMode'),
            'source_container_drift_risk': diagnostics.get('sourceContainerDriftRisk'),
            'warning_count': len(warnings),
            'blocker_count': len(blockers),
        },
    )
    for item in warnings:
        if isinstance(item, dict):
            logger.warning('telegram_gateway_runtime_warning %s', str(item.get('message') or item.get('code') or 'warning'))
    for item in blockers:
        if isinstance(item, dict):
            logger.error('telegram_gateway_runtime_blocker %s', str(item.get('message') or item.get('code') or 'blocker'))


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


def _extract_explicit_graphrag_request(text: str) -> tuple[str | None, str | None]:
    stripped = text.strip()
    command_prefixes = (
        ('/graphrag_global', 'global'),
        ('/graphrag_local', 'local'),
        ('/graphrag_drift', 'drift'),
        ('/graphrag', None),
    )
    for prefix, method in command_prefixes:
        if stripped == prefix:
            return '', method
        if stripped.startswith(f'{prefix} '):
            return stripped[len(prefix):].strip(), method
    return None, None


def _consume_telegram_update_id(update_id: int | None) -> bool:
    if update_id is None:
        return True
    now = monotonic()
    with _TELEGRAM_UPDATE_DEDUPE_LOCK:
        expired = [
            item
            for item, seen_at in _RECENT_TELEGRAM_UPDATE_IDS.items()
            if now - seen_at > _TELEGRAM_UPDATE_DEDUPE_TTL_SECONDS
        ]
        for item in expired:
            _RECENT_TELEGRAM_UPDATE_IDS.pop(item, None)
        if update_id in _RECENT_TELEGRAM_UPDATE_IDS:
            return False
        _RECENT_TELEGRAM_UPDATE_IDS[update_id] = now
        while len(_RECENT_TELEGRAM_UPDATE_IDS) > _TELEGRAM_UPDATE_DEDUPE_LIMIT:
            _RECENT_TELEGRAM_UPDATE_IDS.popitem(last=False)
    return True


def _build_reply_markup(suggested_replies: list[dict[str, object]] | None) -> dict[str, object] | None:
    if not isinstance(suggested_replies, list):
        return None
    labels: list[str] = []
    for item in suggested_replies:
        if not isinstance(item, dict):
            continue
        text = str(item.get('text', '')).strip()
        if not text or text in labels:
            continue
        labels.append(text[:80])
        if len(labels) >= 4:
            break
    if not labels:
        return None
    keyboard = [labels[index:index + 2] for index in range(0, len(labels), 2)]
    return {
        'keyboard': keyboard,
        'resize_keyboard': True,
        'one_time_keyboard': True,
        'input_field_placeholder': 'Escolha um proximo passo ou digite sua mensagem',
    }


async def _send_telegram_message(
    chat_id: int,
    text: str,
    *,
    reply_markup: dict[str, object] | None = None,
) -> bool:
    settings = get_settings()
    if not settings.telegram_bot_token:
        return False

    payload: dict[str, object] = {'chat_id': chat_id, 'text': text}
    if reply_markup:
        payload['reply_markup'] = reply_markup

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.post(
                f'{settings.telegram_api_base_url}/bot{settings.telegram_bot_token}/sendMessage',
                json=payload,
            )
        response.raise_for_status()
        body = response.json()
        if not body.get('ok', False):
            logger.warning(
                'telegram_send_message_not_ok chat_id=%s body=%s',
                chat_id,
                body,
            )
            return False
        return True
    except Exception as exc:
        logger.exception(
            'telegram_send_message_failed chat_id=%s has_reply_markup=%s error=%s',
            chat_id,
            reply_markup is not None,
            exc,
        )
        return False


async def _send_telegram_photo(chat_id: int, image_bytes: bytes, *, caption: str | None = None) -> None:
    settings = get_settings()
    if not settings.telegram_bot_token:
        return

    data = {'chat_id': str(chat_id)}
    if caption:
        data['caption'] = caption[:1024]

    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            response = await client.post(
                f'{settings.telegram_api_base_url}/bot{settings.telegram_bot_token}/sendPhoto',
                data=data,
                files={'photo': ('eduassist-visual.png', image_bytes, 'image/png')},
            )
        response.raise_for_status()
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


@app.on_event('startup')
async def log_startup_diagnostics() -> None:
    _log_runtime_diagnostics(_telegram_runtime_diagnostics(get_settings()))


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
        'runtimeDiagnostics': _telegram_runtime_diagnostics(settings),
    }


@app.get('/v1/status')
async def status(
    x_internal_api_token: str | None = Header(default=None, alias='X-Internal-Api-Token'),
) -> dict[str, object]:
    _require_internal_api_token(x_internal_api_token)
    settings = get_settings()
    return {
        'service': 'telegram-gateway',
        'ready': True,
        'environment': settings.app_env,
        'botUsername': settings.telegram_bot_username,
        'telegramConfigured': bool(settings.telegram_bot_token),
        'aiOrchestratorTimeoutSeconds': settings.ai_orchestrator_timeout_seconds,
        'runtimeDiagnostics': _telegram_runtime_diagnostics(settings),
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
        'Oi. Sou o EduAssist do Colegio Horizonte. '
        'Pode me dizer o assunto do jeito que for mais natural, como matricula, visita, financeiro, notas, secretaria ou direcao. '
        'Se quiser uma sintese GraphRAG real dos documentos publicos, use /graphrag seguido da pergunta.'
    )


def _graph_rag_ack_message(*, preferred_method: str | None, max_seconds: int) -> str:
    method_label = preferred_method or 'auto'
    return (
        'Iniciei uma consulta GraphRAG real nos documentos publicos. '
        f'Metodo: {method_label}. '
        f'Isso pode levar ate {max_seconds}s; quando terminar eu te respondo aqui.'
    )


def _graph_rag_usage_message() -> str:
    return (
        'Use um destes formatos:\n'
        '- /graphrag <pergunta>\n'
        '- /graphrag_global <pergunta ampla>\n'
        '- /graphrag_local <pergunta focada em entidades/trechos>\n'
        '- /graphrag_drift <pergunta investigativa>'
    )


def _format_explicit_graphrag_result(payload: dict[str, object], *, preferred_method: str | None) -> str | None:
    result = payload.get('result')
    if not isinstance(result, dict):
        return None
    text = str(result.get('text') or '').strip()
    if not text:
        return None
    method = str(result.get('method') or preferred_method or 'auto').strip()
    requested_method = str(result.get('requested_method') or preferred_method or '').strip()
    footer_lines = ['[GraphRAG real]', f'metodo: {method}']
    if requested_method and requested_method != method:
        footer_lines.append(f'pedido: {requested_method}')
    return f'{text}\n\n' + '\n'.join(footer_lines)


async def _run_explicit_graphrag_query(
    *,
    query: str,
    preferred_method: str | None,
) -> dict[str, object]:
    settings = get_settings()
    payload: dict[str, object] = {
        'query': query,
        'max_seconds': settings.graph_rag_async_max_seconds,
        'fallback_enabled': True,
        'timeout_profile': 'async',
    }
    if preferred_method in {'local', 'global', 'drift'}:
        payload['preferred_method'] = preferred_method
    logger.info(
        'telegram_graphrag_started preferred_method=%s max_seconds=%s query_len=%s',
        preferred_method or 'auto',
        settings.graph_rag_async_max_seconds,
        len(query),
    )
    async with httpx.AsyncClient(timeout=settings.graph_rag_async_timeout_seconds) as client:
        response = await client.post(
            f'{settings.ai_orchestrator_url}/v1/internal/graphrag/query',
            headers={'X-Internal-Api-Token': settings.internal_api_token},
            json=payload,
        )
    response.raise_for_status()
    body = response.json()
    logger.info(
        'telegram_graphrag_completed preferred_method=%s status_code=%s',
        preferred_method or 'auto',
        response.status_code,
    )
    return body if isinstance(body, dict) else {}


async def _process_explicit_graphrag_message(
    *,
    chat_id: int,
    query: str,
    preferred_method: str | None,
    update_id: int | None,
) -> None:
    try:
        payload = await _run_explicit_graphrag_query(query=query, preferred_method=preferred_method)
        result_text = _format_explicit_graphrag_result(payload, preferred_method=preferred_method)
        if result_text is None:
            result_text = (
                'O GraphRAG real nao concluiu uma sintese final neste modo. '
                'Tente uma pergunta mais curta ou especifique /graphrag_local ou /graphrag_global.'
            )
        sent = await _send_telegram_message(chat_id, result_text)
        if not sent:
            logger.error('telegram_graphrag_send_exhausted chat_id=%s update_id=%s', chat_id, update_id)
    except httpx.HTTPError as exc:
        logger.exception('telegram_graphrag_http_failed chat_id=%s update_id=%s error=%s', chat_id, update_id, exc)
        await _send_telegram_message(
            chat_id,
            'Nao consegui concluir o GraphRAG real agora. '
            'Tente novamente em instantes ou use uma pergunta mais curta com /graphrag_local.',
        )
    except Exception as exc:
        logger.exception(
            'telegram_graphrag_unexpected_failed chat_id=%s update_id=%s error=%s',
            chat_id,
            update_id,
            exc,
        )
        await _send_telegram_message(
            chat_id,
            'O modo assíncrono de GraphRAG falhou antes de concluir a execução. '
            'Tente novamente em instantes.',
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

    async with httpx.AsyncClient(timeout=settings.ai_orchestrator_timeout_seconds) as client:
        response = await client.post(
            f'{settings.ai_orchestrator_url}/v1/messages/respond',
            headers={'X-Internal-Api-Token': settings.internal_api_token},
            json=payload,
        )
    response.raise_for_status()
    return response.json()


async def _process_telegram_text_message(
    *,
    chat_id: int,
    text: str,
    update_id: int | None,
) -> None:
    try:
        orchestration = await _orchestrate_message(
            chat_id=chat_id,
            text=text,
            update_id=update_id,
        )
        reply_text = str(orchestration.get('message_text', _default_help_message()))
        reply_markup = _build_reply_markup(orchestration.get('suggested_replies'))
        sent = await _send_telegram_message(chat_id, reply_text, reply_markup=reply_markup)
        if not sent and reply_markup is not None:
            logger.warning(
                'telegram_send_retry_without_markup chat_id=%s',
                chat_id,
            )
            sent = await _send_telegram_message(chat_id, reply_text, reply_markup=None)
        if not sent:
            logger.error(
                'telegram_send_message_exhausted chat_id=%s update_id=%s',
                chat_id,
                update_id,
            )
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
    except httpx.HTTPError:
        fallback_text = (
            'Nao consegui consultar a base da escola agora. '
            'Tente novamente em instantes ou use o portal institucional.'
        )
        await _send_telegram_message(chat_id, fallback_text)


def _command_to_orchestrator_text(text: str) -> str | None:
    normalized = text.strip().lower()
    if normalized == '/start':
        return 'ola'
    if normalized == '/help':
        return 'quais opcoes de assuntos eu tenho aqui?'
    return None


@app.post('/webhooks/telegram')
async def telegram_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    x_telegram_bot_api_secret_token: str | None = Header(default=None),
) -> dict[str, object]:
    settings = get_settings()
    if x_telegram_bot_api_secret_token != settings.telegram_webhook_secret:
        raise HTTPException(status_code=401, detail='Invalid Telegram webhook secret.')

    payload = await request.json()
    update_id = payload.get('update_id') if isinstance(payload, dict) else None
    if isinstance(update_id, int) and not _consume_telegram_update_id(update_id):
        logger.info('telegram_duplicate_update_ignored update_id=%s', update_id)
        return {
            'accepted': True,
            'service': 'telegram-gateway',
            'processed': 'duplicate_update_ignored',
            'update_id': update_id,
        }
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

        graphrag_query, graphrag_method = _extract_explicit_graphrag_request(text)
        if graphrag_query is not None:
            if not graphrag_query.strip():
                await _send_telegram_message(chat_id, _graph_rag_usage_message())
                return {
                    'accepted': True,
                    'service': 'telegram-gateway',
                    'processed': 'graphrag_usage',
                    'update_id': update_id,
                }
            await _send_telegram_message(
                chat_id,
                _graph_rag_ack_message(
                    preferred_method=graphrag_method,
                    max_seconds=get_settings().graph_rag_async_max_seconds,
                ),
            )
            background_tasks.add_task(
                _process_explicit_graphrag_message,
                chat_id=chat_id,
                query=graphrag_query,
                preferred_method=graphrag_method,
                update_id=update_id if isinstance(update_id, int) else None,
            )
            return {
                'accepted': True,
                'service': 'telegram-gateway',
                'processed': 'graphrag_enqueued',
                'update_id': update_id,
                'preferred_method': graphrag_method or 'auto',
            }

        command_text = _command_to_orchestrator_text(text)
        if command_text is not None:
            text = command_text

        background_tasks.add_task(
            _process_telegram_text_message,
            chat_id=chat_id,
            text=text,
            update_id=update_id if isinstance(update_id, int) else None,
        )
        return {
            'accepted': True,
            'service': 'telegram-gateway',
            'processed': 'orchestrated_message_enqueued',
            'chat_id': chat_id,
            'update_id': update_id,
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
