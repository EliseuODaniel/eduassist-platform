from __future__ import annotations

import os
from typing import Any

from fastapi import FastAPI
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from sqlalchemy.engine import Engine

_CONFIGURED_SERVICES: set[str] = set()


def _env_flag(name: str, default: bool = False) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def _normalize_traces_endpoint() -> str | None:
    direct = os.getenv("OTEL_EXPORTER_OTLP_TRACES_ENDPOINT")
    if direct:
        return direct

    base = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT")
    if not base:
        return None

    if base.endswith("/v1/traces"):
        return base
    return f"{base.rstrip('/')}/v1/traces"


def _parse_headers(raw: str | None) -> dict[str, str] | None:
    if not raw:
        return None

    headers: dict[str, str] = {}
    for item in raw.split(","):
        if "=" not in item:
            continue
        key, value = item.split("=", 1)
        key = key.strip()
        value = value.strip()
        if key and value:
            headers[key] = value
    return headers or None


def configure_observability(
    *,
    service_name: str,
    service_version: str,
    environment: str,
    app: FastAPI | None = None,
    sqlalchemy_engine: Engine | None = None,
    instrument_httpx: bool = True,
    excluded_urls: str = "",
) -> None:
    if service_name in _CONFIGURED_SERVICES:
        return

    if not _env_flag("OTEL_ENABLED", default=False):
        _CONFIGURED_SERVICES.add(service_name)
        return

    traces_endpoint = _normalize_traces_endpoint()
    if not traces_endpoint:
        _CONFIGURED_SERVICES.add(service_name)
        return

    resource_attributes: dict[str, Any] = {
        "service.name": service_name,
        "service.version": service_version,
        "deployment.environment": environment,
    }
    namespace = os.getenv("OTEL_SERVICE_NAMESPACE")
    if namespace:
        resource_attributes["service.namespace"] = namespace

    provider = TracerProvider(resource=Resource.create(resource_attributes))
    provider.add_span_processor(
        BatchSpanProcessor(
            OTLPSpanExporter(
                endpoint=traces_endpoint,
                headers=_parse_headers(os.getenv("OTEL_EXPORTER_OTLP_HEADERS")),
            )
        )
    )
    trace.set_tracer_provider(provider)

    if app is not None:
        @app.middleware("http")
        async def add_trace_response_headers(request, call_next):
            response = await call_next(request)
            current_span = trace.get_current_span()
            span_context = current_span.get_span_context()
            if span_context.is_valid:
                response.headers["X-Trace-Id"] = f"{span_context.trace_id:032x}"
                response.headers["X-Span-Id"] = f"{span_context.span_id:016x}"
            return response

        FastAPIInstrumentor.instrument_app(app, excluded_urls=excluded_urls)

    if instrument_httpx:
        HTTPXClientInstrumentor().instrument()

    if sqlalchemy_engine is not None:
        SQLAlchemyInstrumentor().instrument(engine=sqlalchemy_engine)

    _CONFIGURED_SERVICES.add(service_name)
