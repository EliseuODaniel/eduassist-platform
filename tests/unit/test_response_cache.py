from __future__ import annotations

from ai_orchestrator.response_cache import (
    _PUBLIC_RESPONSE_CACHE,
    get_cached_public_response,
    store_cached_public_response,
)


def setup_function() -> None:
    _PUBLIC_RESPONSE_CACHE.clear()


def test_response_cache_returns_exact_hit() -> None:
    store_cached_public_response(
        message='Como funciona a trilha entre secretaria, coordenacao e direcao?',
        text='Secretaria faz a triagem inicial, coordenacao acompanha e a direcao recebe escalonamentos formais.',
        canonical_lane='public_bundle.governance_protocol',
        topic='governance_channels',
        evidence_fingerprint='governance-v1',
        candidate_kind='deterministic',
        reason='deterministic_candidate_selected',
        ttl_seconds=60.0,
    )
    cached = get_cached_public_response(
        message='Como funciona a trilha entre secretaria, coordenacao e direcao?',
        canonical_lane='public_bundle.governance_protocol',
        topic='governance_channels',
        evidence_fingerprint='governance-v1',
    )
    assert cached is not None
    assert cached.cache_kind == 'exact'
    assert cached.candidate_kind == 'deterministic'


def test_response_cache_returns_semantic_hit_for_near_duplicate() -> None:
    store_cached_public_response(
        message='Como funciona a trilha entre secretaria, coordenacao e direcao?',
        text='Secretaria faz a triagem inicial, coordenacao acompanha e a direcao recebe escalonamentos formais.',
        canonical_lane='public_bundle.governance_protocol',
        topic='governance_channels',
        evidence_fingerprint='governance-v1',
        candidate_kind='deterministic',
        reason='deterministic_candidate_selected',
        ttl_seconds=60.0,
    )
    cached = get_cached_public_response(
        message='Qual e o caminho institucional entre secretaria, coordenacao e direcao?',
        canonical_lane='public_bundle.governance_protocol',
        topic='governance_channels',
        evidence_fingerprint='governance-v1',
        semantic_threshold=0.3,
    )
    assert cached is not None
    assert cached.cache_kind == 'semantic'


def test_response_cache_requires_matching_evidence_fingerprint() -> None:
    store_cached_public_response(
        message='Como funciona a trilha entre secretaria, coordenacao e direcao?',
        text='Secretaria faz a triagem inicial, coordenacao acompanha e a direcao recebe escalonamentos formais.',
        canonical_lane='public_bundle.governance_protocol',
        topic='governance_channels',
        evidence_fingerprint='governance-v1',
        candidate_kind='deterministic',
        reason='deterministic_candidate_selected',
        ttl_seconds=60.0,
    )
    cached = get_cached_public_response(
        message='Como funciona a trilha entre secretaria, coordenacao e direcao?',
        canonical_lane='public_bundle.governance_protocol',
        topic='governance_channels',
        evidence_fingerprint='governance-v2',
    )
    assert cached is None
