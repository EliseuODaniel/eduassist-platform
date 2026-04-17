from __future__ import annotations

from eduassist_observability.workload_identity import (
    bridge_spiffe_identity_to_internal_token,
    evaluate_internal_workload_identity,
)


def test_token_mode_accepts_expected_internal_token() -> None:
    decision = evaluate_internal_workload_identity(
        provided_token='expected-token',
        expected_token='expected-token',
        forwarded_spiffe_id=None,
        mode='token',
        allowed_spiffe_ids=(),
    )

    assert decision.authenticated is True
    assert decision.mechanism == 'internal_api_token'


def test_hybrid_mode_accepts_allowed_spiffe_id() -> None:
    decision = evaluate_internal_workload_identity(
        provided_token=None,
        expected_token='expected-token',
        forwarded_spiffe_id='spiffe://eduassist/internal/telegram-gateway',
        mode='token_or_spiffe',
        allowed_spiffe_ids=('spiffe://eduassist/internal/telegram-gateway',),
    )

    assert decision.authenticated is True
    assert decision.mechanism == 'spiffe_id'
    assert decision.spiffe_id == 'spiffe://eduassist/internal/telegram-gateway'


def test_spiffe_required_rejects_token_only_requests() -> None:
    decision = evaluate_internal_workload_identity(
        provided_token='expected-token',
        expected_token='expected-token',
        forwarded_spiffe_id=None,
        mode='spiffe_required',
        allowed_spiffe_ids=('spiffe://eduassist/internal/telegram-gateway',),
    )

    assert decision.authenticated is False
    assert decision.mechanism is None


def test_bridge_injects_internal_token_for_allowed_spiffe_identity() -> None:
    scope = {
        'headers': [
            (b'x-forwarded-spiffe-id', b'spiffe://eduassist/internal/api-core'),
        ]
    }

    decision = bridge_spiffe_identity_to_internal_token(
        scope,
        expected_token='expected-token',
        mode='token_or_spiffe',
        allowed_spiffe_ids=('spiffe://eduassist/internal/api-core',),
    )

    assert decision.authenticated is True
    assert decision.mechanism == 'spiffe_id'
    assert (b'x-internal-api-token', b'expected-token') in scope['headers']
