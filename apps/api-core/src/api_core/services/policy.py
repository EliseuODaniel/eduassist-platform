from __future__ import annotations

from typing import Any

import httpx

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

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.post(f'{settings.opa_url}/v1/data/eduassist/authz', json=payload)
            response.raise_for_status()
            result = response.json().get('result', {})
            return PolicyDecision(
                allow=bool(result.get('allow', False)),
                reason=str(result.get('reason', 'no_reason_from_opa')),
                source='opa',
            )
    except Exception as exc:  # pragma: no cover - network fallback path
        return PolicyDecision(
            allow=False,
            reason=f'opa_unavailable:{exc.__class__.__name__}',
            source='fallback',
        )
