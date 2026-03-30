#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_REPORT = REPO_ROOT / 'docs/architecture/nextgen-targeted-canary-activation-report.md'
DEFAULT_JSON = REPO_ROOT / 'docs/architecture/nextgen-targeted-canary-activation-report.json'
DEFAULT_ARTIFACT_JSON = REPO_ROOT / 'artifacts/nextgen-targeted-canary-activation-report.json'
SUPPORTED_STACKS = ('python_functions', 'llamaindex')


def _http_json(
    *,
    method: str,
    url: str,
    payload: dict[str, Any] | None = None,
    headers: dict[str, str] | None = None,
    timeout: float = 30.0,
) -> tuple[int, dict[str, Any]]:
    from urllib import error, request

    body = json.dumps(payload).encode('utf-8') if payload is not None else None
    request_headers = {'Accept': 'application/json', **(headers or {})}
    if body is not None:
        request_headers.setdefault('Content-Type', 'application/json')
    req = request.Request(url, data=body, headers=request_headers, method=method.upper())
    try:
        with request.urlopen(req, timeout=timeout) as response:
            raw = response.read().decode('utf-8')
            parsed = json.loads(raw) if raw else {}
            return int(response.status), parsed if isinstance(parsed, dict) else {'value': parsed}
    except error.HTTPError as exc:
        raw = exc.read().decode('utf-8')
        try:
            parsed = json.loads(raw) if raw else {}
        except Exception:
            parsed = {'raw': raw}
        return int(exc.code), parsed if isinstance(parsed, dict) else {'value': parsed}


def _get_runtime_primary_stack(*, base_url: str, internal_api_token: str) -> dict[str, Any]:
    _, payload = _http_json(
        method='GET',
        url=f'{base_url}/v1/internal/runtime/primary-stack',
        headers={'X-Internal-Api-Token': internal_api_token},
        timeout=20.0,
    )
    return payload


def _get_runtime_targeted_stack(*, base_url: str, internal_api_token: str) -> dict[str, Any]:
    _, payload = _http_json(
        method='GET',
        url=f'{base_url}/v1/internal/runtime/targeted-stack',
        headers={'X-Internal-Api-Token': internal_api_token},
        timeout=20.0,
    )
    return payload


def _set_runtime_targeted_stack(
    *,
    base_url: str,
    internal_api_token: str,
    stack: str,
    operator: str,
    reason: str,
    ttl_seconds: int,
    slices: list[str],
    telegram_chat_allowlist: list[str],
    conversation_allowlist: list[str],
) -> tuple[int, dict[str, Any]]:
    return _http_json(
        method='POST',
        url=f'{base_url}/v1/internal/runtime/targeted-stack',
        payload={
            'stack': stack,
            'operator': operator,
            'reason': reason,
            'ttl_seconds': ttl_seconds,
            'slices': slices,
            'telegram_chat_allowlist': telegram_chat_allowlist,
            'conversation_allowlist': conversation_allowlist,
        },
        headers={'X-Internal-Api-Token': internal_api_token},
        timeout=20.0,
    )


def _clear_runtime_targeted_stack(
    *,
    base_url: str,
    internal_api_token: str,
    operator: str,
    reason: str,
) -> tuple[int, dict[str, Any]]:
    return _http_json(
        method='POST',
        url=f'{base_url}/v1/internal/runtime/targeted-stack',
        payload={'clear_override': True, 'operator': operator, 'reason': reason},
        headers={'X-Internal-Api-Token': internal_api_token},
        timeout=20.0,
    )


def _write_report(*, report_md: Path, report_json: Path, artifact_json: Path, payload: dict[str, Any]) -> None:
    json_text = json.dumps(payload, ensure_ascii=False, indent=2) + '\n'
    report_json.write_text(json_text, encoding='utf-8')
    artifact_json.write_text(json_text, encoding='utf-8')

    lines = [
        '# Next-Gen Targeted Canary Activation Report',
        '',
        f"Date: {payload['generated_at']}",
        '',
        f"Base URL: `{payload['base_url']}`",
        '',
        f"Action: `{payload['action']}`",
        '',
        '## Runtime State',
        '',
        f"- Before primary: `resolved={payload['runtime_before'].get('resolvedPrimaryStack')}` from `{payload['runtime_before'].get('resolvedPrimaryStackSource')}`",
        f"- Before targeted: `{(payload['targeted_before'].get('targetedOverride') or {}).get('value')}`",
        f"- After primary: `resolved={payload['runtime_after'].get('resolvedPrimaryStack')}` from `{payload['runtime_after'].get('resolvedPrimaryStackSource')}`",
        f"- After targeted: `{(payload['targeted_after'].get('targetedOverride') or {}).get('value')}`",
        '',
    ]
    if payload['action'] == 'activated':
        lines.extend(
            [
                '## Activated Window',
                '',
                f"- Stack: `{payload['stack']}`",
                f"- TTL seconds: `{payload['ttl_seconds']}`",
                f"- Expires at: `{payload['targeted_after'].get('runtimeTargetedStackOverrideExpiresAt')}`",
                f"- Slices: `{', '.join(payload['slices'])}`",
                f"- Telegram chat allowlist: `{', '.join(payload['telegram_chat_allowlist']) or 'none'}`",
                f"- Conversation allowlist: `{', '.join(payload['conversation_allowlist']) or 'none'}`",
                '',
                '## Practical Meaning',
                '',
                '- So as conversas allowlisted entram na stack nova durante essa janela.',
                '- O resto do trafego continua no baseline atual.',
                '- Ao expirar o TTL, o override direcionado deixa de valer automaticamente.',
                '',
            ]
        )
    else:
        lines.extend(
            [
                '## Clear Result',
                '',
                '- O override direcionado foi removido.',
                '- Novas conversas voltam a obedecer o baseline normal do runtime.',
                '',
            ]
        )
    report_md.write_text('\n'.join(lines), encoding='utf-8')


def main() -> int:
    parser = argparse.ArgumentParser(description='Activate or clear a targeted next-gen canary window for Telegram traffic.')
    parser.add_argument('--base-url', default='http://127.0.0.1:8002')
    parser.add_argument('--internal-api-token', default=os.environ.get('INTERNAL_API_TOKEN', 'dev-internal-token'))
    parser.add_argument('--operator', default='codex')
    parser.add_argument('--stack', choices=SUPPORTED_STACKS)
    parser.add_argument('--slice', action='append', dest='slices', default=[])
    parser.add_argument('--telegram-chat-id', action='append', dest='telegram_chat_ids', default=[])
    parser.add_argument('--conversation-id', action='append', dest='conversation_ids', default=[])
    parser.add_argument('--ttl-minutes', type=int, default=15)
    parser.add_argument('--reason')
    parser.add_argument('--clear', action='store_true')
    parser.add_argument('--report', type=Path, default=DEFAULT_REPORT)
    parser.add_argument('--json', type=Path, default=DEFAULT_JSON)
    parser.add_argument('--artifact-json', type=Path, default=DEFAULT_ARTIFACT_JSON)
    args = parser.parse_args()

    runtime_before = _get_runtime_primary_stack(base_url=args.base_url, internal_api_token=args.internal_api_token)
    targeted_before = _get_runtime_targeted_stack(base_url=args.base_url, internal_api_token=args.internal_api_token)

    if args.clear:
        status_code, payload = _clear_runtime_targeted_stack(
            base_url=args.base_url,
            internal_api_token=args.internal_api_token,
            operator=args.operator,
            reason=str(args.reason or 'manual_targeted_canary_clear').strip(),
        )
        if status_code != 200:
            raise SystemExit(f'failed_to_clear_targeted_canary:{status_code}:{payload}')
        runtime_after = _get_runtime_primary_stack(base_url=args.base_url, internal_api_token=args.internal_api_token)
        targeted_after = _get_runtime_targeted_stack(base_url=args.base_url, internal_api_token=args.internal_api_token)
        result = {
            'generated_at': datetime.now(UTC).isoformat(),
            'action': 'cleared',
            'base_url': args.base_url,
            'runtime_before': runtime_before,
            'targeted_before': targeted_before,
            'runtime_after': runtime_after,
            'targeted_after': targeted_after,
            'response': payload,
        }
        _write_report(report_md=args.report, report_json=args.json, artifact_json=args.artifact_json, payload=result)
        return 0

    if not args.stack:
        raise SystemExit('--stack is required unless --clear is used')
    if str(runtime_before.get('runtimePrimaryStackOverride') or '').strip():
        raise SystemExit('targeted_canary_requires_no_primary_override')
    if str((targeted_before.get('targetedOverride') or {}).get('value') or '').strip():
        raise SystemExit('targeted_canary_requires_no_existing_targeted_override')
    if not args.slices:
        raise SystemExit('at least one --slice is required')
    if not args.telegram_chat_ids and not args.conversation_ids:
        raise SystemExit('at least one --telegram-chat-id or --conversation-id is required')

    ttl_seconds = max(60, int(args.ttl_minutes) * 60)
    status_code, payload = _set_runtime_targeted_stack(
        base_url=args.base_url,
        internal_api_token=args.internal_api_token,
        stack=args.stack,
        operator=args.operator,
        reason=str(args.reason or f'nextgen_targeted_canary_{args.stack}').strip(),
        ttl_seconds=ttl_seconds,
        slices=[str(item).strip() for item in args.slices if str(item).strip()],
        telegram_chat_allowlist=[str(item).strip() for item in args.telegram_chat_ids if str(item).strip()],
        conversation_allowlist=[str(item).strip() for item in args.conversation_ids if str(item).strip()],
    )
    if status_code != 200:
        raise SystemExit(f'failed_to_activate_targeted_canary:{status_code}:{payload}')

    runtime_after = _get_runtime_primary_stack(base_url=args.base_url, internal_api_token=args.internal_api_token)
    targeted_after = _get_runtime_targeted_stack(base_url=args.base_url, internal_api_token=args.internal_api_token)
    result = {
        'generated_at': datetime.now(UTC).isoformat(),
        'action': 'activated',
        'base_url': args.base_url,
        'stack': args.stack,
        'ttl_seconds': ttl_seconds,
        'slices': [str(item).strip() for item in args.slices if str(item).strip()],
        'telegram_chat_allowlist': [str(item).strip() for item in args.telegram_chat_ids if str(item).strip()],
        'conversation_allowlist': [str(item).strip() for item in args.conversation_ids if str(item).strip()],
        'runtime_before': runtime_before,
        'targeted_before': targeted_before,
        'runtime_after': runtime_after,
        'targeted_after': targeted_after,
        'response': payload,
    }
    _write_report(report_md=args.report, report_json=args.json, artifact_json=args.artifact_json, payload=result)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
