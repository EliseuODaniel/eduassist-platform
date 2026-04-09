from __future__ import annotations

import asyncio
from types import SimpleNamespace

import httpx

from ai_orchestrator_specialist import runtime_io


class _FakeClient:
    def __init__(self, payload: dict | None = None, *, error: Exception | None = None) -> None:
        self._payload = payload
        self._error = error

    async def get(self, *_args, **_kwargs):
        if self._error is not None:
            raise self._error
        return _FakeResponse(self._payload)


class _FakeResponse:
    def __init__(self, payload: dict | None) -> None:
        self._payload = payload

    def raise_for_status(self) -> None:
        return None

    def json(self) -> dict | None:
        return self._payload


def _ctx(*, client: object) -> SimpleNamespace:
    return SimpleNamespace(
        http_client=client,
        settings=SimpleNamespace(
            api_core_url="http://api-core:8000",
            internal_api_token="dev-internal-token",
            public_resource_cache_ttl_seconds=120.0,
            public_resource_timeout_seconds=0.2,
        ),
    )


def test_fetch_public_payload_returns_stale_cache_when_api_core_times_out() -> None:
    runtime_io._PUBLIC_RESOURCE_CACHE.clear()
    try:
        warm_ctx = _ctx(client=_FakeClient({"profile": {"school_name": "Colegio Horizonte"}}))
        warm_value = asyncio.run(
            runtime_io.fetch_public_payload(warm_ctx, "/v1/public/school-profile", "profile")
        )
        assert warm_value == {"school_name": "Colegio Horizonte"}

        timeout_exc = httpx.ReadTimeout(
            "boom",
            request=httpx.Request("GET", "http://api-core:8000/v1/public/school-profile"),
        )
        stale_ctx = _ctx(client=_FakeClient(error=timeout_exc))
        stale_value = asyncio.run(
            runtime_io.fetch_public_payload(stale_ctx, "/v1/public/school-profile", "profile")
        )
        assert stale_value == {"school_name": "Colegio Horizonte"}
    finally:
        runtime_io._PUBLIC_RESOURCE_CACHE.clear()


def test_fetch_public_school_profile_degrades_to_none_when_api_core_is_unavailable() -> None:
    runtime_io._PUBLIC_RESOURCE_CACHE.clear()
    try:
        timeout_exc = httpx.ReadTimeout(
            "boom",
            request=httpx.Request("GET", "http://api-core:8000/v1/public/school-profile"),
        )
        ctx = _ctx(client=_FakeClient(error=timeout_exc))
        profile = asyncio.run(runtime_io.fetch_public_school_profile(ctx))
        assert profile is None
    finally:
        runtime_io._PUBLIC_RESOURCE_CACHE.clear()
