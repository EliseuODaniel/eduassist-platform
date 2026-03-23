from __future__ import annotations

from typing import Any

import httpx
from eduassist_observability import set_span_attributes, start_span

from api_core.contracts import ActorContext, PolicyDecision
from api_core.config import get_settings


async def decide_policy(
    *,
    action: str,
    actor: ActorContext,
    resource: dict[str, Any] | None = None,
) -> PolicyDecision:
    settings = get_settings()
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
            return decision
