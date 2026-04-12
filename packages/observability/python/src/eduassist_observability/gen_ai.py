from __future__ import annotations

from collections.abc import Iterable, Mapping
from contextlib import contextmanager
from dataclasses import dataclass
from time import monotonic
from typing import Any
from urllib.parse import urlparse

from opentelemetry.trace import Span, SpanKind

from .runtime import record_histogram, set_span_attributes, start_span


@dataclass(frozen=True)
class GenAIUsage:
    input_tokens: int | None = None
    output_tokens: int | None = None
    total_tokens: int | None = None
    response_model: str | None = None
    response_id: str | None = None
    finish_reasons: tuple[str, ...] = ()
    estimated_cost_usd: float | None = None


@dataclass(frozen=True)
class GenAIServerEndpoint:
    address: str | None = None
    port: int | None = None


def normalize_gen_ai_provider_name(provider: str | None, *, base_url: str | None = None) -> str:
    normalized = str(provider or '').strip().lower()
    base = str(base_url or '').strip().lower()
    if normalized in {'google', 'gemini', 'litellm'}:
        return 'gcp.gen_ai'
    if normalized == 'openai':
        if base and 'api.openai.com' not in base:
            return 'self_hosted'
        return 'openai'
    if not normalized and base and 'api.openai.com' not in base:
        return 'self_hosted'
    return normalized or 'unknown'


def parse_server_endpoint(base_url: str | None) -> GenAIServerEndpoint:
    parsed = urlparse(str(base_url or '').strip())
    address = str(parsed.hostname or '').strip() or None
    return GenAIServerEndpoint(address=address, port=parsed.port)


def _coerce_int(value: Any) -> int | None:
    if value is None:
        return None
    try:
        return int(value)
    except Exception:
        return None


def _coerce_finish_reasons(values: Iterable[Any]) -> tuple[str, ...]:
    normalized: list[str] = []
    for value in values:
        cleaned = str(value or '').strip().lower()
        if cleaned:
            normalized.append(cleaned)
    return tuple(normalized)


def _estimate_google_gemini_cost_usd(
    *,
    request_model: str | None,
    input_tokens: int | None,
    output_tokens: int | None,
) -> float | None:
    normalized = str(request_model or '').strip().lower().removeprefix('models/')
    if not normalized:
        return None

    per_million: tuple[float, float] | None = None
    if 'gemini-2.5-flash-lite' in normalized:
        per_million = (0.05, 0.20)
    elif 'gemini-2.5-flash' in normalized:
        per_million = (0.15, 1.25)

    if per_million is None:
        return None

    input_cost = (float(input_tokens or 0) / 1_000_000.0) * per_million[0]
    output_cost = (float(output_tokens or 0) / 1_000_000.0) * per_million[1]
    return round(input_cost + output_cost, 8)


def estimate_gen_ai_cost_usd(
    *,
    provider_name: str,
    request_model: str | None,
    input_tokens: int | None,
    output_tokens: int | None,
) -> float | None:
    normalized_provider = str(provider_name or '').strip().lower()
    if normalized_provider == 'self_hosted':
        return 0.0
    if normalized_provider == 'gcp.gen_ai':
        return _estimate_google_gemini_cost_usd(
            request_model=request_model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
        )
    return None


def extract_openai_usage(
    response: Any, *, request_model: str | None = None, provider_name: str = 'openai'
) -> GenAIUsage:
    usage = getattr(response, 'usage', None)
    input_tokens = None
    output_tokens = None
    total_tokens = None
    if usage is not None:
        input_tokens = _coerce_int(
            getattr(usage, 'prompt_tokens', None) or getattr(usage, 'input_tokens', None)
        )
        output_tokens = _coerce_int(
            getattr(usage, 'completion_tokens', None) or getattr(usage, 'output_tokens', None)
        )
        total_tokens = _coerce_int(getattr(usage, 'total_tokens', None))

    response_model = str(getattr(response, 'model', '') or '').strip() or None
    response_id = str(getattr(response, 'id', '') or '').strip() or None

    finish_reasons: list[str] = []
    choices = getattr(response, 'choices', None) or []
    if isinstance(choices, list):
        finish_reasons.extend(
            str(getattr(choice, 'finish_reason', '') or '').strip() for choice in choices
        )

    if total_tokens is None and (input_tokens is not None or output_tokens is not None):
        total_tokens = int(input_tokens or 0) + int(output_tokens or 0)

    estimated_cost_usd = estimate_gen_ai_cost_usd(
        provider_name=provider_name,
        request_model=request_model or response_model,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
    )
    return GenAIUsage(
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        total_tokens=total_tokens,
        response_model=response_model,
        response_id=response_id,
        finish_reasons=_coerce_finish_reasons(finish_reasons),
        estimated_cost_usd=estimated_cost_usd,
    )


def extract_google_usage(
    body: Mapping[str, Any], *, request_model: str | None = None
) -> GenAIUsage:
    usage = body.get('usageMetadata') if isinstance(body, Mapping) else None
    input_tokens = (
        _coerce_int(usage.get('promptTokenCount')) if isinstance(usage, Mapping) else None
    )
    output_tokens = (
        _coerce_int(usage.get('candidatesTokenCount')) if isinstance(usage, Mapping) else None
    )
    total_tokens = _coerce_int(usage.get('totalTokenCount')) if isinstance(usage, Mapping) else None

    response_model = str(body.get('modelVersion') or '').strip() or None
    finish_reasons: list[str] = []
    candidates = body.get('candidates') if isinstance(body, Mapping) else None
    if isinstance(candidates, list):
        for candidate in candidates:
            if isinstance(candidate, Mapping):
                finish_reasons.append(str(candidate.get('finishReason') or '').strip())

    if total_tokens is None and (input_tokens is not None or output_tokens is not None):
        total_tokens = int(input_tokens or 0) + int(output_tokens or 0)

    estimated_cost_usd = estimate_gen_ai_cost_usd(
        provider_name='gcp.gen_ai',
        request_model=request_model or response_model,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
    )
    return GenAIUsage(
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        total_tokens=total_tokens,
        response_model=response_model,
        finish_reasons=_coerce_finish_reasons(finish_reasons),
        estimated_cost_usd=estimated_cost_usd,
    )


class GenAIClientOperation:
    def __init__(
        self,
        *,
        span: Span,
        metric_attributes: dict[str, Any],
        request_model: str | None,
        provider_name: str,
        start_time: float,
    ) -> None:
        self._span = span
        self._metric_attributes = metric_attributes
        self._request_model = request_model
        self._provider_name = provider_name
        self._start_time = start_time
        self._finished = False

    def finish(
        self,
        *,
        usage: GenAIUsage | None = None,
        error_type: str | None = None,
        extra_attributes: Mapping[str, Any] | None = None,
    ) -> None:
        if self._finished:
            return
        self._finished = True
        duration_seconds = max(monotonic() - self._start_time, 0.0)
        record_histogram(
            'gen_ai.client.operation.duration',
            duration_seconds,
            meter_name='eduassist.gen_ai',
            unit='s',
            description='Client-side GenAI operation latency.',
            attributes=self._metric_attributes,
        )
        span_attributes: dict[str, Any] = dict(self._metric_attributes)
        if error_type:
            span_attributes['error.type'] = error_type
        if usage is not None:
            if usage.response_model:
                span_attributes['gen_ai.response.model'] = usage.response_model
            if usage.response_id:
                span_attributes['gen_ai.response.id'] = usage.response_id
            if usage.finish_reasons:
                span_attributes['gen_ai.response.finish_reasons'] = usage.finish_reasons
            if usage.input_tokens is not None:
                span_attributes['gen_ai.usage.input_tokens'] = usage.input_tokens
                record_histogram(
                    'gen_ai.client.token.usage',
                    usage.input_tokens,
                    meter_name='eduassist.gen_ai',
                    unit='{token}',
                    description='Number of GenAI client input and output tokens used.',
                    attributes={**self._metric_attributes, 'gen_ai.token.type': 'input'},
                )
            if usage.output_tokens is not None:
                span_attributes['gen_ai.usage.output_tokens'] = usage.output_tokens
                record_histogram(
                    'gen_ai.client.token.usage',
                    usage.output_tokens,
                    meter_name='eduassist.gen_ai',
                    unit='{token}',
                    description='Number of GenAI client input and output tokens used.',
                    attributes={**self._metric_attributes, 'gen_ai.token.type': 'output'},
                )
            if usage.total_tokens is not None:
                span_attributes['eduassist.gen_ai.usage.total_tokens'] = usage.total_tokens
            if usage.estimated_cost_usd is not None:
                span_attributes['eduassist.gen_ai.cost.estimated_usd'] = usage.estimated_cost_usd
                record_histogram(
                    'eduassist_gen_ai_estimated_cost_usd',
                    usage.estimated_cost_usd,
                    meter_name='eduassist.gen_ai',
                    unit='USD',
                    description='Estimated GenAI provider cost per request.',
                    attributes=self._metric_attributes,
                )
        if extra_attributes:
            span_attributes.update(extra_attributes)
        set_span_attributes(self._span, **span_attributes)


@contextmanager
def start_gen_ai_client_operation(
    *,
    provider_name: str,
    operation_name: str,
    request_model: str | None,
    base_url: str | None = None,
    request_temperature: float | None = None,
    request_max_tokens: int | None = None,
    request_top_p: float | None = None,
    llm_model_profile: str | None = None,
):
    endpoint = parse_server_endpoint(base_url)
    metric_attributes: dict[str, Any] = {
        'gen_ai.provider.name': provider_name,
        'gen_ai.operation.name': operation_name,
    }
    span_attributes: dict[str, Any] = dict(metric_attributes)
    if request_model:
        metric_attributes['gen_ai.request.model'] = request_model
        span_attributes['gen_ai.request.model'] = request_model
    if endpoint.address:
        metric_attributes['server.address'] = endpoint.address
        span_attributes['server.address'] = endpoint.address
    if endpoint.port is not None:
        metric_attributes['server.port'] = endpoint.port
        span_attributes['server.port'] = endpoint.port
    if request_temperature is not None:
        span_attributes['gen_ai.request.temperature'] = request_temperature
    if request_max_tokens is not None:
        span_attributes['gen_ai.request.max_tokens'] = request_max_tokens
    if request_top_p is not None:
        span_attributes['gen_ai.request.top_p'] = request_top_p
    if llm_model_profile:
        metric_attributes['eduassist.llm_model_profile'] = llm_model_profile
        span_attributes['eduassist.llm_model_profile'] = llm_model_profile

    span_name = f'gen_ai.{provider_name}.{operation_name}'
    with start_span(
        span_name, tracer_name='eduassist.gen_ai', kind=SpanKind.CLIENT, **span_attributes
    ) as span:
        operation = GenAIClientOperation(
            span=span,
            metric_attributes=metric_attributes,
            request_model=request_model,
            provider_name=provider_name,
            start_time=monotonic(),
        )
        try:
            yield operation
        except Exception as exc:
            operation.finish(error_type=exc.__class__.__name__)
            raise
        else:
            operation.finish()
