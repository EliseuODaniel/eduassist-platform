from __future__ import annotations

from time import monotonic
from typing import Any

import httpx
from eduassist_observability import record_counter, record_histogram, set_span_attributes, start_span

from api_core.contracts import ActorContext, PolicyDecision
from api_core.config import get_settings


async def decide_policy(
    *,
    action: str,
    actor: ActorContext,
    resource: dict[str, Any] | None = None,
) -> PolicyDecision:
    settings = get_settings()
    started_at = monotonic()
    payload = {
        'input': {
            'action': action,
            'subject': actor.to_policy_subject(),
            'resource': resource or {},
        }
    }

    with start_span(
        'eduassist.policy.decide',
        tracer_name='eduassist.api_core.policy',
        **{
            'eduassist.policy.action': action,
            'eduassist.actor.role': actor.role_code,
            'eduassist.actor.authenticated': actor.authenticated,
            'eduassist.resource.type': (resource or {}).get('resource_type'),
        },
    ):
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.post(f'{settings.opa_url}/v1/data/eduassist/authz', json=payload)
                response.raise_for_status()
                result = response.json().get('result', {})
                decision = PolicyDecision(
                    allow=bool(result.get('allow', False)),
                    reason=str(result.get('reason', 'no_reason_from_opa')),
                    source='opa',
                )
                set_span_attributes(
                    **{
                        'http.status_code': response.status_code,
                        'eduassist.policy.allow': decision.allow,
                        'eduassist.policy.reason': decision.reason,
                        'eduassist.policy.source': decision.source,
                    },
                )
                _record_policy_metrics(
                    action=action,
                    actor=actor,
                    decision=decision,
                    resource=resource,
                    latency_ms=(monotonic() - started_at) * 1000,
                )
                return decision
        except Exception as exc:  # pragma: no cover - network fallback path
            decision = PolicyDecision(
                allow=False,
                reason=f'opa_unavailable:{exc.__class__.__name__}',
                source='fallback',
            )
            set_span_attributes(
                **{
                    'eduassist.policy.allow': decision.allow,
                    'eduassist.policy.reason': decision.reason,
                    'eduassist.policy.source': decision.source,
                }
            )
            _record_policy_metrics(
                action=action,
                actor=actor,
                decision=decision,
                resource=resource,
                latency_ms=(monotonic() - started_at) * 1000,
            )
            return decision


def _record_policy_metrics(
    *,
    action: str,
    actor: ActorContext,
    decision: PolicyDecision,
    resource: dict[str, Any] | None,
    latency_ms: float,
) -> None:
    metric_attributes = {
        'action': action,
        'allow': decision.allow,
        'source': decision.source,
        'role': actor.role_code,
        'authenticated': actor.authenticated,
        'resource_type': (resource or {}).get('resource_type', 'unknown'),
    }
    record_counter(
        'eduassist_policy_decisions',
        attributes=metric_attributes,
        description='Policy decisions emitted by api-core.',
    )
    record_histogram(
        'eduassist_policy_decision_latency_ms',
        latency_ms,
        attributes={
            'action': action,
            'source': decision.source,
            'allow': decision.allow,
        },
        description='Latency of policy evaluation in milliseconds.',
    )
