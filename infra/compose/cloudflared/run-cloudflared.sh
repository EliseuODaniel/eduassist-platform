#!/bin/sh
set -eu

if [ -n "${CLOUDFLARED_TUNNEL_TOKEN:-}" ]; then
  echo "cloudflared: starting named tunnel via token" >&2
  exec cloudflared tunnel --no-autoupdate run --token "${CLOUDFLARED_TUNNEL_TOKEN}"
fi

if [ "${CLOUDFLARED_ALLOW_QUICK_TUNNEL:-true}" != "true" ]; then
  echo "cloudflared: CLOUDFLARED_TUNNEL_TOKEN is not set and quick tunnels are disabled; configure a named tunnel token." >&2
  exit 1
fi

echo "cloudflared: starting quick tunnel fallback; prefer CLOUDFLARED_TUNNEL_TOKEN for a stable named tunnel" >&2
exec cloudflared tunnel --no-autoupdate --url "${CLOUDFLARED_TARGET_URL:-http://telegram-gateway:8000}"
