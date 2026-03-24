#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ENV_PATH = ROOT / ".env"
COMPOSE_FILE = ROOT / "infra" / "compose" / "compose.yaml"
CLOUDFLARED_CONTAINER = "eduassist-cloudflared"
CLOUDFLARED_URL_PATTERN = re.compile(
    r"https://[a-z0-9-]+\.trycloudflare\.com", re.IGNORECASE
)


def load_env_file(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in raw_line:
            continue
        key, value = raw_line.split("=", 1)
        values[key.strip()] = value.strip()
    return values


def telegram_api_call(token: str, method: str, payload: dict[str, str] | None = None) -> dict:
    encoded = None
    if payload is not None:
        encoded = urllib.parse.urlencode(payload).encode("utf-8")
    request = urllib.request.Request(
        f"https://api.telegram.org/bot{token}/{method}",
        data=encoded,
        method="POST" if payload is not None else "GET",
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)


def get_cloudflared_url(timeout_seconds: int = 60) -> str:
    deadline = time.time() + timeout_seconds
    latest_logs = ""
    while time.time() < deadline:
        result = subprocess.run(
            ["docker", "logs", CLOUDFLARED_CONTAINER],
            capture_output=True,
            text=True,
            check=False,
        )
        latest_logs = (result.stdout or "") + (result.stderr or "")
        matches = CLOUDFLARED_URL_PATTERN.findall(latest_logs)
        if matches:
            return matches[-1]
        time.sleep(2)
    raise RuntimeError(
        "Nao encontrei URL do trycloudflare nos logs do container "
        f"{CLOUDFLARED_CONTAINER}.\nTrecho final dos logs:\n{latest_logs[-1200:]}"
    )


def wait_for_public_healthcheck(base_url: str, timeout_seconds: int = 60) -> None:
    deadline = time.time() + timeout_seconds
    last_error = None
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(f"{base_url}/healthz", timeout=20) as response:
                if response.status == 200:
                    return
        except Exception as exc:  # pragma: no cover - operational path
            last_error = exc
        time.sleep(3)
    raise RuntimeError(
        f"Tunel publico nao ficou saudavel em {base_url}/healthz: {last_error}"
    )


def register_webhook() -> int:
    env = load_env_file(ENV_PATH)
    token = env.get("TELEGRAM_BOT_TOKEN", "").strip()
    secret = env.get("TELEGRAM_WEBHOOK_SECRET", "").strip()
    if not token:
        print(json.dumps({"ok": False, "error": "TELEGRAM_BOT_TOKEN ausente no .env"}))
        return 1
    if not secret:
        print(json.dumps({"ok": False, "error": "TELEGRAM_WEBHOOK_SECRET ausente no .env"}))
        return 1

    public_base_url = get_cloudflared_url()
    wait_for_public_healthcheck(public_base_url)
    webhook_url = f"{public_base_url}/webhooks/telegram"

    set_result = telegram_api_call(
        token,
        "setWebhook",
        {
            "url": webhook_url,
            "secret_token": secret,
            "drop_pending_updates": "true",
        },
    )
    info_result = telegram_api_call(token, "getWebhookInfo")
    print(
        json.dumps(
            {
                "public_base_url": public_base_url,
                "webhook_url": webhook_url,
                "set_webhook": set_result,
                "webhook_info": info_result,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


def webhook_info() -> int:
    env = load_env_file(ENV_PATH)
    token = env.get("TELEGRAM_BOT_TOKEN", "").strip()
    if not token:
        print(json.dumps({"ok": False, "error": "TELEGRAM_BOT_TOKEN ausente no .env"}))
        return 1
    result = telegram_api_call(token, "getWebhookInfo")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Gerencia webhook do Telegram para o stack local.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("register", help="Descobre a URL do cloudflared e registra o webhook.")
    subparsers.add_parser("info", help="Mostra o estado atual do webhook no Telegram.")
    args = parser.parse_args()

    try:
        if args.command == "register":
            return register_webhook()
        if args.command == "info":
            return webhook_info()
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", "replace")
        print(json.dumps({"ok": False, "http_error": exc.code, "body": body}, ensure_ascii=False))
        return 1
    except Exception as exc:  # pragma: no cover - operational path
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False))
        return 1
    return 1


if __name__ == "__main__":
    sys.exit(main())
