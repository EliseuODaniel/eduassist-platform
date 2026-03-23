from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import yaml


REMOTE_OPENAI_PROFILE = 'openai-remote'
LOCAL_OPENAI_COMPATIBLE_PROFILE = 'local-openai-compatible'
PLACEHOLDER_TOKENS = {'<API_KEY>', '<LOCAL_CHAT_MODEL>', '<LOCAL_EMBEDDING_MODEL>'}


def load_env_file(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.exists():
        return values
    for raw_line in path.read_text(encoding='utf-8').splitlines():
        line = raw_line.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue
        key, value = line.split('=', 1)
        values[key.strip()] = value.strip()
    return values


def load_settings(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return yaml.safe_load(path.read_text(encoding='utf-8')) or {}


def detect_profile(*, settings: dict[str, Any], env_values: dict[str, str]) -> str:
    explicit = env_values.get('GRAPHRAG_PROVIDER_PROFILE', '').strip()
    if explicit:
        return explicit

    completion_models = settings.get('completion_models', {})
    default_model = completion_models.get('default_completion_model', {})
    api_base = str(default_model.get('api_base', '') or '')
    if '${GRAPHRAG_LOCAL_API_BASE}' in api_base:
        return LOCAL_OPENAI_COMPATIBLE_PROFILE
    return REMOTE_OPENAI_PROFILE


def _is_configured(value: str | None) -> bool:
    if value is None:
        return False
    candidate = value.strip()
    return bool(candidate) and candidate not in PLACEHOLDER_TOKENS


def _normalize_base_url(value: str) -> str:
    return value.rstrip('/')


def _request_json(*, url: str, headers: dict[str, str]) -> dict[str, Any]:
    request = Request(url, headers=headers, method='GET')
    with urlopen(request, timeout=10.0) as response:
        return json.loads(response.read().decode('utf-8'))


def _resolve_local_provider_value(
    env_values: dict[str, str],
    *,
    specific_key: str,
    shared_key: str,
    default: str | None = None,
) -> str | None:
    specific_value = env_values.get(specific_key)
    if specific_value is not None and specific_value.strip():
        return specific_value.strip()

    shared_value = env_values.get(shared_key)
    if shared_value is not None and shared_value.strip():
        return shared_value.strip()

    return default


def _model_present(*, expected_model: str, available_models: list[str]) -> bool:
    normalized_expected = expected_model.strip()
    variants = {
        normalized_expected,
        f'{normalized_expected}:latest',
    }
    if normalized_expected.endswith(':latest'):
        variants.add(normalized_expected.rsplit(':', 1)[0])
    return any(candidate in available_models for candidate in variants)


def _check_openai_compatible_endpoint(*, api_base: str, api_key: str, models: list[str]) -> dict[str, Any]:
    base_url = _normalize_base_url(api_base)
    headers = {'Authorization': f'Bearer {api_key}'}
    try:
        payload = _request_json(url=f'{base_url}/models', headers=headers)
    except HTTPError as exc:
        return {
            'endpoint_reachable': False,
            'provider_ready': False,
            'provider_reason': f'local_endpoint_http_error_{exc.code}',
            'available_models': [],
        }
    except URLError:
        return {
            'endpoint_reachable': False,
            'provider_ready': False,
            'provider_reason': 'local_endpoint_unreachable',
            'available_models': [],
        }

    data = payload.get('data') or []
    available_models = sorted(
        item.get('id', '')
        for item in data
        if isinstance(item, dict) and item.get('id')
    )
    missing_models = [
        model
        for model in models
        if not _model_present(expected_model=model, available_models=available_models)
    ]
    return {
        'endpoint_reachable': True,
        'provider_ready': not missing_models,
        'provider_reason': 'ready' if not missing_models else 'local_models_missing',
        'available_models': available_models,
        'missing_models': missing_models,
    }


def get_workspace_provider_status(workspace: Path) -> dict[str, Any]:
    settings_path = workspace / 'settings.yaml'
    env_path = workspace / '.env'
    settings = load_settings(settings_path)
    env_values = load_env_file(env_path)
    profile = detect_profile(settings=settings, env_values=env_values)

    status: dict[str, Any] = {
        'provider_profile': profile,
        'provider_configured': False,
        'provider_ready': False,
        'provider_reason': 'missing_provider_configuration',
        'endpoint_reachable': None,
        'available_models': [],
        'missing_models': [],
    }

    if profile == REMOTE_OPENAI_PROFILE:
        api_key = env_values.get('GRAPHRAG_API_KEY')
        configured = _is_configured(api_key)
        status.update(
            {
                'provider_configured': configured,
                'provider_ready': configured,
                'provider_reason': 'ready' if configured else 'missing_api_key',
            }
        )
        return status

    if profile == LOCAL_OPENAI_COMPATIBLE_PROFILE:
        chat_api_base = _resolve_local_provider_value(
            env_values,
            specific_key='GRAPHRAG_LOCAL_CHAT_API_BASE',
            shared_key='GRAPHRAG_LOCAL_API_BASE',
        )
        embedding_api_base = _resolve_local_provider_value(
            env_values,
            specific_key='GRAPHRAG_LOCAL_EMBEDDING_API_BASE',
            shared_key='GRAPHRAG_LOCAL_API_BASE',
        )
        chat_model = env_values.get('GRAPHRAG_LOCAL_CHAT_MODEL')
        embedding_model = env_values.get('GRAPHRAG_LOCAL_EMBEDDING_MODEL')
        chat_api_key = _resolve_local_provider_value(
            env_values,
            specific_key='GRAPHRAG_LOCAL_CHAT_API_KEY',
            shared_key='GRAPHRAG_LOCAL_API_KEY',
            default='ollama',
        )
        embedding_api_key = _resolve_local_provider_value(
            env_values,
            specific_key='GRAPHRAG_LOCAL_EMBEDDING_API_KEY',
            shared_key='GRAPHRAG_LOCAL_API_KEY',
            default='ollama',
        )

        configured = all(
            _is_configured(value)
            for value in [chat_api_base, embedding_api_base, chat_model, embedding_model]
        )
        status['provider_configured'] = configured
        if not configured:
            status['provider_reason'] = 'missing_local_provider_values'
            return status

        chat_endpoint_status = _check_openai_compatible_endpoint(
            api_base=str(chat_api_base),
            api_key=str(chat_api_key or 'ollama'),
            models=[str(chat_model)],
        )
        embedding_endpoint_status = _check_openai_compatible_endpoint(
            api_base=str(embedding_api_base),
            api_key=str(embedding_api_key or 'ollama'),
            models=[str(embedding_model)],
        )
        available_models = sorted(
            {
                *chat_endpoint_status.get('available_models', []),
                *embedding_endpoint_status.get('available_models', []),
            }
        )
        missing_models = [
            *chat_endpoint_status.get('missing_models', []),
            *embedding_endpoint_status.get('missing_models', []),
        ]
        provider_ready = bool(chat_endpoint_status.get('provider_ready')) and bool(
            embedding_endpoint_status.get('provider_ready')
        )

        if provider_ready:
            provider_reason = 'ready'
        elif not chat_endpoint_status.get('endpoint_reachable'):
            provider_reason = 'local_chat_endpoint_unreachable'
        elif not embedding_endpoint_status.get('endpoint_reachable'):
            provider_reason = 'local_embedding_endpoint_unreachable'
        elif chat_endpoint_status.get('missing_models'):
            provider_reason = 'local_chat_models_missing'
        elif embedding_endpoint_status.get('missing_models'):
            provider_reason = 'local_embedding_models_missing'
        else:
            provider_reason = 'local_provider_not_ready'

        status.update(
            {
                'provider_ready': provider_ready,
                'provider_reason': provider_reason,
                'endpoint_reachable': bool(chat_endpoint_status.get('endpoint_reachable'))
                and bool(embedding_endpoint_status.get('endpoint_reachable')),
                'chat_endpoint_reachable': chat_endpoint_status.get('endpoint_reachable'),
                'embedding_endpoint_reachable': embedding_endpoint_status.get('endpoint_reachable'),
                'chat_api_base': chat_api_base,
                'embedding_api_base': embedding_api_base,
                'chat_available_models': chat_endpoint_status.get('available_models', []),
                'embedding_available_models': embedding_endpoint_status.get('available_models', []),
                'available_models': available_models,
                'missing_models': missing_models,
            }
        )
        return status

    status['provider_reason'] = 'unsupported_provider_profile'
    return status
