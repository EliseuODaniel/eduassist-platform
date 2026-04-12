## Cloudflared mode

The current `main` branch uses a dedicated-first architecture and should prefer a stable named tunnel for Telegram-facing tests.

Recommended:
- set `CLOUDFLARED_TUNNEL_TOKEN` to a named tunnel token
- keep `CLOUDFLARED_ALLOW_QUICK_TUNNEL=false`

Development fallback:
- if no named tunnel token is available, set `CLOUDFLARED_ALLOW_QUICK_TUNNEL=true`
- the runner will fall back to a temporary quick tunnel

Operational note:
- `TryCloudflare` is still acceptable for local development and short demos;
- for longer Telegram sessions, the recommended path is a named tunnel with:
  - `CLOUDFLARED_TUNNEL_TOKEN`
  - `TELEGRAM_PUBLIC_BASE_URL`

Relevant env vars:
- `CLOUDFLARED_TARGET_URL`
- `CLOUDFLARED_TUNNEL_TOKEN`
- `CLOUDFLARED_ALLOW_QUICK_TUNNEL`

References:
- https://developers.cloudflare.com/cloudflare-one/networks/connectors/cloudflare-tunnel/do-more-with-tunnels/trycloudflare/
- https://developers.cloudflare.com/cloudflare-one/networks/connectors/cloudflare-tunnel/configure-tunnels/run-parameters/
