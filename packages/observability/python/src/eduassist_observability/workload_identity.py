from __future__ import annotations

import secrets
from dataclasses import dataclass
from typing import Iterable


_SPIFFE_FORWARD_HEADER = 'x-forwarded-spiffe-id'
_INTERNAL_TOKEN_HEADER = 'x-internal-api-token'


@dataclass(frozen=True)
class WorkloadIdentityDecision:
    authenticated: bool
    mechanism: str | None
    mode: str
    spiffe_id: str | None = None


def normalize_workload_identity_mode(value: str | None) -> str:
    normalized = str(value or '').strip().lower()
    if normalized in {'spiffe', 'spiffe_required', 'spiffe-only'}:
        return 'spiffe_required'
    if normalized in {'token_or_spiffe', 'spiffe_optional', 'hybrid'}:
        return 'token_or_spiffe'
    return 'token'


def parse_allowed_spiffe_ids(value: str | Iterable[str] | None) -> tuple[str, ...]:
    if value is None:
        return ()
    if isinstance(value, str):
        raw_items = value.split(',')
    else:
        raw_items = list(value)
    normalized = []
    for item in raw_items:
        candidate = str(item or '').strip()
        if candidate and candidate not in normalized:
            normalized.append(candidate)
    return tuple(normalized)


def evaluate_internal_workload_identity(
    *,
    provided_token: str | None,
    expected_token: str,
    forwarded_spiffe_id: str | None,
    mode: str | None,
    allowed_spiffe_ids: str | Iterable[str] | None,
) -> WorkloadIdentityDecision:
    normalized_mode = normalize_workload_identity_mode(mode)
    token = str(provided_token or '').strip()
    if normalized_mode != 'spiffe_required' and token and secrets.compare_digest(token, expected_token):
        return WorkloadIdentityDecision(
            authenticated=True,
            mechanism='internal_api_token',
            mode=normalized_mode,
        )

    spiffe_id = str(forwarded_spiffe_id or '').strip()
    if spiffe_id and spiffe_id in parse_allowed_spiffe_ids(allowed_spiffe_ids):
        return WorkloadIdentityDecision(
            authenticated=True,
            mechanism='spiffe_id',
            mode=normalized_mode,
            spiffe_id=spiffe_id,
        )

    return WorkloadIdentityDecision(
        authenticated=False,
        mechanism=None,
        mode=normalized_mode,
        spiffe_id=spiffe_id or None,
    )


def scope_header_value(scope: dict[str, object], header_name: str) -> str | None:
    target = header_name.strip().lower().encode('latin-1')
    for raw_name, raw_value in scope.get('headers', []) or []:
        if raw_name.lower() == target:
            return raw_value.decode('latin-1')
    return None


def bridge_spiffe_identity_to_internal_token(
    scope: dict[str, object],
    *,
    expected_token: str,
    mode: str | None,
    allowed_spiffe_ids: str | Iterable[str] | None,
) -> WorkloadIdentityDecision:
    provided_token = scope_header_value(scope, _INTERNAL_TOKEN_HEADER)
    forwarded_spiffe_id = scope_header_value(scope, _SPIFFE_FORWARD_HEADER)
    decision = evaluate_internal_workload_identity(
        provided_token=provided_token,
        expected_token=expected_token,
        forwarded_spiffe_id=forwarded_spiffe_id,
        mode=mode,
        allowed_spiffe_ids=allowed_spiffe_ids,
    )
    if decision.authenticated and decision.mechanism == 'spiffe_id' and not provided_token:
        headers = list(scope.get('headers', []) or [])
        headers.append((_INTERNAL_TOKEN_HEADER.encode('latin-1'), expected_token.encode('latin-1')))
        scope['headers'] = headers
    return decision
