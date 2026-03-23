from __future__ import annotations

import json
import os
import sys
import time
from base64 import b64encode
from dataclasses import dataclass
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen


def _env(name: str, default: str) -> str:
    return os.getenv(name, default)


@dataclass(frozen=True)
class Settings:
    api_core_url: str = _env("SMOKE_API_CORE_URL", "http://localhost:8001")
    ai_orchestrator_url: str = _env("SMOKE_AI_ORCHESTRATOR_URL", "http://localhost:8002")
    telegram_gateway_url: str = _env("SMOKE_TELEGRAM_GATEWAY_URL", "http://localhost:8003")
    keycloak_url: str = _env("SMOKE_KEYCLOAK_URL", "http://localhost:8080")
    grafana_url: str = _env("SMOKE_GRAFANA_URL", "http://localhost:3004")
    tempo_url: str = _env("SMOKE_TEMPO_URL", "http://localhost:3200")
    loki_url: str = _env("SMOKE_LOKI_URL", "http://localhost:3100")
    keycloak_realm: str = _env("SMOKE_KEYCLOAK_REALM", "eduassist")
    username: str = _env("SMOKE_USERNAME", "maria.oliveira")
    password: str = _env("SMOKE_PASSWORD", "Eduassist123!")
    client_id: str = _env("SMOKE_CLIENT_ID", "eduassist-cli")
    telegram_secret: str = _env("SMOKE_TELEGRAM_SECRET", "change-me")
    grafana_user: str = _env("SMOKE_GRAFANA_USER", "admin")
    grafana_password: str = _env("SMOKE_GRAFANA_PASSWORD", "admin123")


def _request(
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

    request = Request(url, data=payload, headers=request_headers, method=method)
    try:
        with urlopen(request, timeout=timeout) as response:
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


def _assert(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def _fetch_token(settings: Settings) -> str:
    status, _, payload = _request(
        "POST",
        f"{settings.keycloak_url}/realms/{settings.keycloak_realm}/protocol/openid-connect/token",
        form_body={
            "client_id": settings.client_id,
            "grant_type": "password",
            "username": settings.username,
            "password": settings.password,
        },
    )
    _assert(status == 200 and isinstance(payload, dict), "token_request_failed")
    token = payload.get("access_token")
    _assert(isinstance(token, str) and len(token) > 20, "invalid_access_token")
    return token


def _wait_for_health(name: str, url: str, *, attempts: int = 8, delay_seconds: float = 3.0) -> None:
    last_status = None
    for _ in range(attempts):
        status, _, _ = _request("GET", url, timeout=10.0)
        last_status = status
        if status == 200:
            return
        time.sleep(delay_seconds)
    raise AssertionError(f"health_failed:{name}:{last_status}")


def _extract_trace_id(headers: dict[str, str]) -> str:
    trace_id = headers.get("X-Trace-Id") or headers.get("x-trace-id")
    _assert(isinstance(trace_id, str) and len(trace_id) == 32, "missing_trace_id")
    return trace_id


def _wait_for_tempo_trace(settings: Settings, trace_id: str) -> dict[str, Any]:
    for _ in range(6):
        status, _, payload = _request("GET", f"{settings.tempo_url}/api/traces/{trace_id}", timeout=10.0)
        if status == 200 and isinstance(payload, dict):
            return payload
        time.sleep(2)
    raise AssertionError(f"tempo_trace_not_found:{trace_id}")


def _wait_for_loki_logs(settings: Settings, query: str) -> dict[str, Any]:
    encoded = quote(query, safe="")
    end_ns = int(time.time() * 1_000_000_000)
    start_ns = end_ns - (30 * 60 * 1_000_000_000)
    for _ in range(6):
        status, _, payload = _request(
            "GET",
            (
                f"{settings.loki_url}/loki/api/v1/query_range"
                f"?query={encoded}&limit=20&start={start_ns}&end={end_ns}"
            ),
            timeout=10.0,
        )
        if status == 200 and isinstance(payload, dict):
            data = payload.get("data", {})
            result = data.get("result", [])
            if isinstance(result, list) and result:
                return payload
        time.sleep(2)
    raise AssertionError(f"loki_query_empty:{query}")


def _trace_span_names(payload: dict[str, Any]) -> set[str]:
    names: set[str] = set()
    for batch in payload.get("batches", []):
        for scope in batch.get("scopeSpans", []):
            for span in scope.get("spans", []):
                name = span.get("name")
                if isinstance(name, str):
                    names.add(name)
    return names


def _wait_for_trace_span(settings: Settings, trace_id: str, span_name: str) -> dict[str, Any]:
    last_payload: dict[str, Any] | None = None
    for _ in range(6):
        payload = _wait_for_tempo_trace(settings, trace_id)
        last_payload = payload
        if span_name in _trace_span_names(payload):
            return payload
        time.sleep(2)
    raise AssertionError(f"missing_trace_span:{span_name}:{trace_id}:{sorted(_trace_span_names(last_payload or {}))}")


def main() -> int:
    settings = Settings()
    print("Smoke suite starting...")

    for name, url in [
        ("api-core", f"{settings.api_core_url}/healthz"),
        ("ai-orchestrator", f"{settings.ai_orchestrator_url}/healthz"),
        ("telegram-gateway", f"{settings.telegram_gateway_url}/healthz"),
        ("tempo", f"{settings.tempo_url}/ready"),
        ("loki", f"{settings.loki_url}/ready"),
    ]:
        _wait_for_health(name, url)
        print(f"[ok] health {name}")

    token = _fetch_token(settings)
    print("[ok] keycloak token")

    status, _, payload = _request(
        "GET",
        f"{settings.api_core_url}/v1/operations/overview",
        headers={"Authorization": f"Bearer {token}"},
    )
    _assert(status == 200 and isinstance(payload, dict), "operations_overview_failed")
    print("[ok] operations overview")

    public_status, public_headers, public_payload = _request(
        "POST",
        f"{settings.telegram_gateway_url}/webhooks/telegram",
        headers={"x-telegram-bot-api-secret-token": settings.telegram_secret},
        json_body={
            "update_id": 9901,
            "message": {
                "message_id": 1,
                "date": 1774271000,
                "text": "quais documentos sao exigidos para matricula?",
                "chat": {"id": 777001, "type": "private"},
                "from": {"id": 777001, "is_bot": False, "first_name": "Visitante", "username": "visitante.publico"},
            },
        },
    )
    _assert(public_status == 200 and isinstance(public_payload, dict), "public_webhook_failed")
    _assert("reply" in public_payload and "document" in str(public_payload["reply"]).lower(), "public_reply_unexpected")
    public_trace_id = _extract_trace_id(public_headers)
    print("[ok] public faq")

    protected_status, protected_headers, protected_payload = _request(
        "POST",
        f"{settings.telegram_gateway_url}/webhooks/telegram",
        headers={"x-telegram-bot-api-secret-token": settings.telegram_secret},
        json_body={
            "update_id": 9902,
            "message": {
                "message_id": 2,
                "date": 1774271001,
                "text": "quero ver as notas do Lucas Oliveira",
                "chat": {"id": 555001, "type": "private"},
                "from": {"id": 555001, "is_bot": False, "first_name": "Maria", "username": "maria.oliveira"},
            },
        },
    )
    _assert(protected_status == 200 and isinstance(protected_payload, dict), "protected_webhook_failed")
    _assert("Resumo academico de Lucas Oliveira" in str(protected_payload.get("reply", "")), "protected_reply_unexpected")
    protected_trace_id = _extract_trace_id(protected_headers)
    print("[ok] protected academic")

    handoff_status, handoff_headers, handoff_payload = _request(
        "POST",
        f"{settings.telegram_gateway_url}/webhooks/telegram",
        headers={"x-telegram-bot-api-secret-token": settings.telegram_secret},
        json_body={
            "update_id": 9903,
            "message": {
                "message_id": 3,
                "date": 1774271002,
                "text": "quero falar com um humano sobre o financeiro",
                "chat": {"id": 555001, "type": "private"},
                "from": {"id": 555001, "is_bot": False, "first_name": "Maria", "username": "maria.oliveira"},
            },
        },
    )
    _assert(handoff_status == 200 and isinstance(handoff_payload, dict), "handoff_webhook_failed")
    _assert("Protocolo:" in str(handoff_payload.get("reply", "")), "handoff_reply_unexpected")
    handoff_trace_id = _extract_trace_id(handoff_headers)
    print("[ok] human handoff")

    dashboard_status, _, dashboard_payload = _request(
        "GET",
        f"{settings.grafana_url}/api/search?query={quote('EduAssist Tracing Overview', safe='')}",
        headers={
            "Authorization": "Basic "
            + b64encode(f"{settings.grafana_user}:{settings.grafana_password}".encode("utf-8")).decode("ascii")
        },
    )
    _assert(dashboard_status == 200 and isinstance(dashboard_payload, list) and dashboard_payload, "grafana_dashboard_missing")
    print("[ok] grafana dashboard")

    public_trace = _wait_for_trace_span(settings, public_trace_id, "eduassist.retrieval.hybrid_search")
    public_spans = _trace_span_names(public_trace)
    _assert("eduassist.retrieval.hybrid_search" in public_spans, "missing_public_retrieval_span")
    print("[ok] tempo retrieval span")

    protected_trace = _wait_for_trace_span(settings, protected_trace_id, "eduassist.policy.decide")
    protected_spans = _trace_span_names(protected_trace)
    _assert("eduassist.policy.decide" in protected_spans, "missing_policy_span")
    print("[ok] tempo policy span")

    handoff_trace = _wait_for_trace_span(settings, handoff_trace_id, "eduassist.support.create_handoff")
    handoff_spans = _trace_span_names(handoff_trace)
    _assert("eduassist.support.create_handoff" in handoff_spans, "missing_handoff_span")
    print("[ok] tempo handoff span")

    loki_payload = _wait_for_loki_logs(settings, '{compose_service="telegram-gateway"}')
    loki_results = loki_payload.get("data", {}).get("result", [])
    _assert(isinstance(loki_results, list) and loki_results, "loki_no_gateway_logs")
    print("[ok] loki gateway logs")

    print("Smoke suite finished successfully.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as exc:
        print(f"[fail] {exc}", file=sys.stderr)
        raise SystemExit(1)
