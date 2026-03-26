from __future__ import annotations

import json
import os
import time
from base64 import b64encode
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen


_DOTENV_CACHE: dict[str, str] | None = None


def _load_dotenv() -> dict[str, str]:
    global _DOTENV_CACHE
    if _DOTENV_CACHE is not None:
        return _DOTENV_CACHE

    repo_root = Path(__file__).resolve().parents[2]
    env_path = repo_root / ".env"
    values: dict[str, str] = {}
    if env_path.exists():
        for raw_line in env_path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            values[key.strip()] = value.strip()
    _DOTENV_CACHE = values
    return values


def _env(name: str, default: str) -> str:
    return os.getenv(name) or _load_dotenv().get(name, default)


@dataclass(frozen=True)
class Settings:
    api_core_url: str = _env("SMOKE_API_CORE_URL", "http://127.0.0.1:8001")
    ai_orchestrator_url: str = _env("SMOKE_AI_ORCHESTRATOR_URL", "http://127.0.0.1:8002")
    telegram_gateway_url: str = _env("SMOKE_TELEGRAM_GATEWAY_URL", "http://127.0.0.1:8003")
    keycloak_url: str = _env("SMOKE_KEYCLOAK_URL", "http://127.0.0.1:8080")
    grafana_url: str = _env("SMOKE_GRAFANA_URL", "http://127.0.0.1:3004")
    prometheus_url: str = _env("SMOKE_PROMETHEUS_URL", "http://127.0.0.1:9090")
    tempo_url: str = _env("SMOKE_TEMPO_URL", "http://127.0.0.1:3200")
    loki_url: str = _env("SMOKE_LOKI_URL", "http://127.0.0.1:3100")
    keycloak_realm: str = _env("SMOKE_KEYCLOAK_REALM", "eduassist")
    username: str = _env("SMOKE_USERNAME", "maria.oliveira")
    password: str = _env("SMOKE_PASSWORD", "Eduassist123!")
    client_id: str = _env("SMOKE_CLIENT_ID", "eduassist-cli")
    internal_api_token: str = _env("SMOKE_INTERNAL_API_TOKEN", "dev-internal-token")
    telegram_secret: str = _env("SMOKE_TELEGRAM_SECRET", _env("TELEGRAM_WEBHOOK_SECRET", "change-me"))
    grafana_user: str = _env("SMOKE_GRAFANA_USER", "admin")
    grafana_password: str = _env("SMOKE_GRAFANA_PASSWORD", "admin123")


def request(
    method: str,
    url: str,
    *,
    headers: dict[str, str] | None = None,
    json_body: Any | None = None,
    form_body: dict[str, str] | None = None,
    timeout: float = 20.0,
) -> tuple[int, dict[str, str], Any]:
    payload: bytes | None = None
    request_headers = dict(headers or {})
    if json_body is not None:
        payload = json.dumps(json_body).encode("utf-8")
        request_headers.setdefault("Content-Type", "application/json")
    elif form_body is not None:
        payload = urlencode(form_body).encode("utf-8")
        request_headers.setdefault("Content-Type", "application/x-www-form-urlencoded")

    request_obj = Request(url, data=payload, headers=request_headers, method=method)
    try:
        with urlopen(request_obj, timeout=timeout) as response:
            body = response.read().decode("utf-8")
            content_type = response.headers.get("Content-Type", "")
            parsed: Any = body
            if "application/json" in content_type:
                parsed = json.loads(body)
            return response.status, dict(response.headers.items()), parsed
    except HTTPError as exc:
        body = exc.read().decode("utf-8")
        parsed = body
        if "application/json" in (exc.headers.get("Content-Type", "")):
            try:
                parsed = json.loads(body)
            except json.JSONDecodeError:
                pass
        return exc.code, dict(exc.headers.items()), parsed
    except URLError as exc:
        raise RuntimeError(f"request_failed:{method}:{url}:{exc.reason}") from exc


def assert_condition(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def fetch_token(settings: Settings, *, username: str | None = None, password: str | None = None) -> str:
    status, _, payload = request(
        "POST",
        f"{settings.keycloak_url}/realms/{settings.keycloak_realm}/protocol/openid-connect/token",
        form_body={
            "client_id": settings.client_id,
            "grant_type": "password",
            "username": username or settings.username,
            "password": password or settings.password,
        },
    )
    assert_condition(status == 200 and isinstance(payload, dict), "token_request_failed")
    token = payload.get("access_token")
    assert_condition(isinstance(token, str) and len(token) > 20, "invalid_access_token")
    return token


def wait_for_health(name: str, url: str, *, attempts: int = 8, delay_seconds: float = 3.0) -> None:
    last_status = None
    for _ in range(attempts):
        status, _, _ = request("GET", url, timeout=10.0)
        last_status = status
        if status == 200:
            return
        time.sleep(delay_seconds)
    raise AssertionError(f"health_failed:{name}:{last_status}")


def extract_trace_id(headers: dict[str, str]) -> str:
    trace_id = headers.get("X-Trace-Id") or headers.get("x-trace-id")
    assert_condition(isinstance(trace_id, str) and len(trace_id) == 32, "missing_trace_id")
    return trace_id


def wait_for_tempo_trace(settings: Settings, trace_id: str) -> dict[str, Any]:
    for _ in range(6):
        status, _, payload = request("GET", f"{settings.tempo_url}/api/traces/{trace_id}", timeout=10.0)
        if status == 200 and isinstance(payload, dict):
            return payload
        time.sleep(2)
    raise AssertionError(f"tempo_trace_not_found:{trace_id}")


def wait_for_loki_logs(settings: Settings, query: str) -> dict[str, Any]:
    for _ in range(6):
        payload = loki_query_range(settings, query)
        if loki_has_results(payload):
            return payload
        time.sleep(2)
    raise AssertionError(f"loki_query_empty:{query}")


def loki_query_range(
    settings: Settings,
    query: str,
    *,
    limit: int = 20,
    lookback_minutes: int = 30,
) -> dict[str, Any]:
    encoded = quote(query, safe="")
    end_ns = int(time.time() * 1_000_000_000)
    start_ns = end_ns - (lookback_minutes * 60 * 1_000_000_000)
    status, _, payload = request(
        "GET",
        (
            f"{settings.loki_url}/loki/api/v1/query_range"
            f"?query={encoded}&limit={limit}&start={start_ns}&end={end_ns}"
        ),
        timeout=10.0,
    )
    assert_condition(status == 200 and isinstance(payload, dict), f"loki_query_failed:{query}")
    return payload


def loki_has_results(payload: dict[str, Any]) -> bool:
    data = payload.get("data", {})
    result = data.get("result", [])
    return isinstance(result, list) and bool(result)


def prometheus_query(settings: Settings, query: str) -> dict[str, Any]:
    encoded = quote(query, safe="")
    status, _, payload = request(
        "GET",
        f"{settings.prometheus_url}/api/v1/query?query={encoded}",
        timeout=10.0,
    )
    assert_condition(status == 200 and isinstance(payload, dict), f"prometheus_query_failed:{query}")
    return payload


def wait_for_prometheus_result(
    settings: Settings,
    query: str,
    *,
    attempts: int = 8,
    delay_seconds: float = 2.0,
) -> list[dict[str, Any]]:
    for _ in range(attempts):
        payload = prometheus_query(settings, query)
        data = payload.get("data", {})
        result = data.get("result", [])
        if isinstance(result, list) and result:
            return result
        time.sleep(delay_seconds)
    raise AssertionError(f"prometheus_query_empty:{query}")


def trace_span_names(payload: dict[str, Any]) -> set[str]:
    names: set[str] = set()
    for batch in payload.get("batches", []):
        for scope in batch.get("scopeSpans", []):
            for span in scope.get("spans", []):
                name = span.get("name")
                if isinstance(name, str):
                    names.add(name)
    return names


def wait_for_trace_span(settings: Settings, trace_id: str, span_name: str) -> dict[str, Any]:
    last_payload: dict[str, Any] | None = None
    for _ in range(6):
        payload = wait_for_tempo_trace(settings, trace_id)
        last_payload = payload
        if span_name in trace_span_names(payload):
            return payload
        time.sleep(2)
    raise AssertionError(f"missing_trace_span:{span_name}:{trace_id}:{sorted(trace_span_names(last_payload or {}))}")


def grafana_basic_auth_header(settings: Settings) -> dict[str, str]:
    token = b64encode(f"{settings.grafana_user}:{settings.grafana_password}".encode("utf-8")).decode("ascii")
    return {"Authorization": f"Basic {token}"}


def telegram_webhook_request(
    settings: Settings,
    *,
    update_id: int,
    message_id: int,
    text: str,
    chat_id: int,
    username: str,
    first_name: str,
    secret: str | None = None,
) -> tuple[int, dict[str, str], Any]:
    return request(
        "POST",
        f"{settings.telegram_gateway_url}/webhooks/telegram",
        headers={"x-telegram-bot-api-secret-token": secret or settings.telegram_secret},
        json_body={
            "update_id": update_id,
            "message": {
                "message_id": message_id,
                "date": 1774271000 + message_id,
                "text": text,
                "chat": {"id": chat_id, "type": "private"},
                "from": {"id": chat_id, "is_bot": False, "first_name": first_name, "username": username},
            },
        },
    )
