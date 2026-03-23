from __future__ import annotations

import json
import os
from collections.abc import Mapping, Sequence
from contextlib import contextmanager
from datetime import date, datetime
from enum import Enum
from typing import Any
from uuid import UUID

from fastapi import FastAPI
from opentelemetry import metrics, trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace import Span, Status, StatusCode
from sqlalchemy.engine import Engine
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter

_CONFIGURED_SERVICES: set[str] = set()
_COUNTERS: dict[tuple[str, str, str | None, str | None], Any] = {}
_HISTOGRAMS: dict[tuple[str, str, str | None, str | None], Any] = {}


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


def _normalize_metrics_endpoint() -> str | None:
    direct = os.getenv("OTEL_EXPORTER_OTLP_METRICS_ENDPOINT")
    if direct:
        return direct

    base = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT")
    if not base:
        return None

    if base.endswith("/v1/metrics"):
        return base
    return f"{base.rstrip('/')}/v1/metrics"


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


def _normalize_sequence(items: Sequence[Any]) -> tuple[Any, ...] | None:
    normalized = [_normalize_attribute_value(item) for item in items]
    normalized = [item for item in normalized if item is not None]
    if not normalized:
        return None

    if all(isinstance(item, bool) for item in normalized):
        return tuple(normalized)
    if all(isinstance(item, int) and not isinstance(item, bool) for item in normalized):
        return tuple(normalized)
    if all(isinstance(item, float) for item in normalized):
        return tuple(normalized)
    return tuple(str(item) for item in normalized)


def _normalize_attribute_value(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, (str, bool, float)):
        return value
    if isinstance(value, int) and not isinstance(value, bool):
        return value
    if isinstance(value, Enum):
        return str(value.value)
    if isinstance(value, (UUID, date, datetime)):
        return str(value)
    if isinstance(value, Mapping):
        return json.dumps(value, sort_keys=True, default=str)
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return _normalize_sequence(value)
    return str(value)


def get_tracer(name: str = "eduassist") -> trace.Tracer:
    return trace.get_tracer(name)


def get_meter(name: str = "eduassist"):
    return metrics.get_meter(name)


def set_span_attributes(span: Span | None = None, /, **attributes: Any) -> None:
    target_span = span or trace.get_current_span()
    if target_span is None:
        return
    for key, value in attributes.items():
        normalized = _normalize_attribute_value(value)
        if normalized is None:
            continue
        target_span.set_attribute(key, normalized)


def _normalize_metric_value(value: Any) -> str | bool | int | float | None:
    if value is None:
        return None
    if isinstance(value, (str, bool, float)):
        return value
    if isinstance(value, int) and not isinstance(value, bool):
        return value
    if isinstance(value, Enum):
        return str(value.value)
    if isinstance(value, (UUID, date, datetime)):
        return str(value)
    return str(value)


def _normalize_metric_attributes(attributes: Mapping[str, Any] | None = None) -> dict[str, str | bool | int | float]:
    if not attributes:
        return {}

    normalized: dict[str, str | bool | int | float] = {}
    for key, value in attributes.items():
        metric_value = _normalize_metric_value(value)
        if metric_value is None:
            continue
        normalized[key] = metric_value
    return normalized


def _get_counter(
    *,
    meter_name: str,
    name: str,
    description: str | None,
    unit: str | None,
):
    cache_key = (meter_name, name, description, unit)
    counter = _COUNTERS.get(cache_key)
    if counter is not None:
        return counter

    counter = get_meter(meter_name).create_counter(
        name,
        description=description or "",
        unit=unit or "",
    )
    _COUNTERS[cache_key] = counter
    return counter


def _get_histogram(
    *,
    meter_name: str,
    name: str,
    description: str | None,
    unit: str | None,
):
    cache_key = (meter_name, name, description, unit)
    histogram = _HISTOGRAMS.get(cache_key)
    if histogram is not None:
        return histogram

    histogram = get_meter(meter_name).create_histogram(
        name,
        description=description or "",
        unit=unit or "",
    )
    _HISTOGRAMS[cache_key] = histogram
    return histogram


def record_counter(
    name: str,
    value: int | float = 1,
    *,
    meter_name: str = "eduassist",
    attributes: Mapping[str, Any] | None = None,
    description: str | None = None,
    unit: str | None = None,
) -> None:
    counter = _get_counter(
        meter_name=meter_name,
        name=name,
        description=description,
        unit=unit,
    )
    counter.add(value, attributes=_normalize_metric_attributes(attributes))


def record_histogram(
    name: str,
    value: int | float,
    *,
    meter_name: str = "eduassist",
    attributes: Mapping[str, Any] | None = None,
    description: str | None = None,
    unit: str | None = None,
) -> None:
    histogram = _get_histogram(
        meter_name=meter_name,
        name=name,
        description=description,
        unit=unit,
    )
    histogram.record(value, attributes=_normalize_metric_attributes(attributes))


@contextmanager
def start_span(
    name: str,
    *,
    tracer_name: str = "eduassist",
    **attributes: Any,
):
    tracer = get_tracer(tracer_name)
    with tracer.start_as_current_span(name) as span:
        set_span_attributes(span, **attributes)
        try:
            yield span
        except Exception as exc:
            span.record_exception(exc)
            span.set_status(Status(StatusCode.ERROR, exc.__class__.__name__))
            raise


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
    metrics_endpoint = _normalize_metrics_endpoint()
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

    resource = Resource.create(resource_attributes)

    tracer_provider = TracerProvider(resource=resource)
    tracer_provider.add_span_processor(
        BatchSpanProcessor(
            OTLPSpanExporter(
                endpoint=traces_endpoint,
                headers=_parse_headers(os.getenv("OTEL_EXPORTER_OTLP_HEADERS")),
            )
        )
    )
    trace.set_tracer_provider(tracer_provider)

    meter_provider: MeterProvider | None = None
    if metrics_endpoint:
        metric_reader = PeriodicExportingMetricReader(
            OTLPMetricExporter(
                endpoint=metrics_endpoint,
                headers=_parse_headers(os.getenv("OTEL_EXPORTER_OTLP_HEADERS")),
            ),
            export_interval_millis=int(os.getenv("OTEL_METRIC_EXPORT_INTERVAL_MILLIS", "5000")),
            export_timeout_millis=int(os.getenv("OTEL_METRIC_EXPORT_TIMEOUT_MILLIS", "10000")),
        )
        meter_provider = MeterProvider(resource=resource, metric_readers=[metric_reader])
        metrics.set_meter_provider(meter_provider)

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

        FastAPIInstrumentor.instrument_app(
            app,
            tracer_provider=tracer_provider,
            meter_provider=meter_provider,
            excluded_urls=excluded_urls,
        )

    if instrument_httpx:
        HTTPXClientInstrumentor().instrument()

    if sqlalchemy_engine is not None:
        SQLAlchemyInstrumentor().instrument(engine=sqlalchemy_engine)

    _CONFIGURED_SERVICES.add(service_name)
