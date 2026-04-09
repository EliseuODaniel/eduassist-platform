from __future__ import annotations

from tools.ops import telegram_webhook


def test_normalize_base_url_strips_trailing_slash() -> None:
    assert telegram_webhook._normalize_base_url("https://eduassist.example.com/") == "https://eduassist.example.com"


def test_resolve_public_base_url_prefers_explicit_env_url() -> None:
    env = {"TELEGRAM_PUBLIC_BASE_URL": "https://eduassist.example.com/"}
    assert telegram_webhook.resolve_public_base_url(env) == "https://eduassist.example.com"


def test_resolve_public_base_url_rejects_named_tunnel_without_explicit_url() -> None:
    env = {"CLOUDFLARED_TUNNEL_TOKEN": "secret-token", "CLOUDFLARED_ALLOW_QUICK_TUNNEL": "false"}
    try:
        telegram_webhook.resolve_public_base_url(env)
    except RuntimeError as exc:
        assert "TELEGRAM_PUBLIC_BASE_URL" in str(exc)
    else:  # pragma: no cover - defensive
        raise AssertionError("expected RuntimeError for named tunnel without explicit URL")


def test_resolve_public_base_url_uses_quick_tunnel_logs_when_allowed(monkeypatch) -> None:
    monkeypatch.setattr(
        telegram_webhook,
        "get_cloudflared_url",
        lambda timeout_seconds=60: "https://quick-tunnel.trycloudflare.com",
    )
    env = {"CLOUDFLARED_ALLOW_QUICK_TUNNEL": "true"}
    assert telegram_webhook.resolve_public_base_url(env) == "https://quick-tunnel.trycloudflare.com"

