#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib import error, request

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATASET = REPO_ROOT / 'tests/evals/datasets/four_path_chatbot_smoke_cases.json'
DEFAULT_REPORT = REPO_ROOT / 'docs/architecture/nextgen-stack-runtime-preflight-report.md'
DEFAULT_JSON = REPO_ROOT / 'docs/architecture/nextgen-stack-runtime-preflight-report.json'
DEFAULT_ARTIFACT_JSON = REPO_ROOT / 'artifacts/nextgen-stack-runtime-preflight-report.json'
SUPPORTED_STACKS = ('python_functions', 'llamaindex')


def _http_json(
    *,
    method: str,
    url: str,
    payload: dict[str, Any] | None = None,
    headers: dict[str, str] | None = None,
    timeout: float = 30.0,
) -> tuple[int, dict[str, Any]]:
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


def _set_runtime_primary_stack(
    *,
    base_url: str,
    internal_api_token: str,
    stack: str,
    operator: str,
    reason: str,
) -> dict[str, Any]:
    _, payload = _http_json(
        method='POST',
        url=f'{base_url}/v1/internal/runtime/primary-stack',
        payload={'stack': stack, 'operator': operator, 'reason': reason},
        headers={'X-Internal-Api-Token': internal_api_token},
        timeout=20.0,
    )
    return payload


def _clear_runtime_primary_stack(
    *,
    base_url: str,
    internal_api_token: str,
    operator: str,
    reason: str,
) -> dict[str, Any]:
    _, payload = _http_json(
        method='POST',
        url=f'{base_url}/v1/internal/runtime/primary-stack',
        payload={'clear_override': True, 'operator': operator, 'reason': reason},
        headers={'X-Internal-Api-Token': internal_api_token},
        timeout=20.0,
    )
    return payload


def _restore_previous_override(
    *,
    base_url: str,
    internal_api_token: str,
    operator: str,
    previous_state: dict[str, Any],
) -> dict[str, Any]:
    previous_override = str(previous_state.get('runtimePrimaryStackOverride') or '').strip()
    if previous_override:
        return _set_runtime_primary_stack(
            base_url=base_url,
            internal_api_token=internal_api_token,
            stack=previous_override,
            operator=operator,
            reason='restore_previous_runtime_override',
        )
    return _clear_runtime_primary_stack(
        base_url=base_url,
        internal_api_token=internal_api_token,
        operator=operator,
        reason='restore_default_runtime_stack',
    )


def _load_cases(path: Path) -> list[dict[str, Any]]:
    payload = json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(payload, list):
        raise ValueError(f'Expected a list of cases in {path}')
    return [item for item in payload if isinstance(item, dict)]


def _run_case(
    *,
    base_url: str,
    internal_api_token: str,
    stack: str,
    case: dict[str, Any],
) -> dict[str, Any]:
    payload = {
        'message': str(case['message']),
        'conversation_id': f"{case['conversation_id']}-{stack}-runtime-preflight",
        'telegram_chat_id': int(case['telegram_chat_id']),
        'channel': 'telegram',
        'user': case.get('user') or {},
        'allow_graph_rag': True,
        'allow_handoff': True,
    }
    status_code, body = _http_json(
        method='POST',
        url=f'{base_url}/v1/messages/respond',
        payload=payload,
        headers={'X-Internal-Api-Token': internal_api_token},
        timeout=40.0,
    )
    graph_path = [str(item) for item in (body.get('graph_path') or []) if str(item).strip()]
    access_tier = str((body.get('classification') or {}).get('access_tier') or '')
    message_text = str(body.get('message_text') or '')
    expected_access_tier = str(case.get('expected_access_tier') or '').strip()
    passed = bool(
        status_code == 200
        and message_text.strip()
        and (not expected_access_tier or access_tier == expected_access_tier)
        and f'kernel:{stack}' in graph_path
    )
    return {
        'case_id': str(case['id']),
        'stack': stack,
        'status': status_code,
        'passed': passed,
        'expected_access_tier': expected_access_tier,
        'access_tier': access_tier,
        'reason': str(body.get('reason') or ''),
        'mode': str(body.get('mode') or ''),
        'graph_path': graph_path,
        'message_preview': message_text[:220],
    }


def _summary_for_stack(results: list[dict[str, Any]], *, stack: str) -> dict[str, Any]:
    subset = [item for item in results if item['stack'] == stack]
    return {
        'passed': sum(1 for item in subset if item['passed']),
        'total': len(subset),
        'ready_for_controlled_runtime': bool(subset) and all(item['passed'] for item in subset),
    }


def _write_report(*, report_md: Path, report_json: Path, artifact_json: Path, payload: dict[str, Any]) -> None:
    json_text = json.dumps(payload, ensure_ascii=False, indent=2) + '\n'
    report_json.write_text(json_text, encoding='utf-8')
    artifact_json.write_text(json_text, encoding='utf-8')

    lines = [
        '# Next-Gen Stack Runtime Preflight Report',
        '',
        f"Date: {payload['generated_at']}",
        '',
        f"Base URL: `{payload['base_url']}`",
        '',
        f"Dataset: `{payload['dataset']}`",
        '',
        '## Summary',
        '',
        '| Stack | Passed | Ready for controlled runtime |',
        '| --- | --- | --- |',
    ]
    for stack in payload['stacks']:
        bucket = payload['summary']['by_stack'][stack]
        lines.append(
            f"| `{stack}` | `{bucket['passed']}/{bucket['total']}` | `{bucket['ready_for_controlled_runtime']}` |"
        )
    lines.extend(
        [
            '',
            '## Runtime State',
            '',
            f"- Before: `resolved={payload['runtime_before'].get('resolvedPrimaryStack')}` from `{payload['runtime_before'].get('resolvedPrimaryStackSource')}`",
            f"- After restore: `resolved={payload['runtime_after_restore'].get('resolvedPrimaryStack')}` from `{payload['runtime_after_restore'].get('resolvedPrimaryStackSource')}`",
            '',
            '## Case Results',
            '',
            '| Case | Stack | Result | Mode | Access tier | Reason |',
            '| --- | --- | --- | --- | --- | --- |',
        ]
    )
    for item in payload['results']:
        lines.append(
            f"| `{item['case_id']}` | `{item['stack']}` | {'passed' if item['passed'] else 'failed'} | `{item['mode']}` | `{item['access_tier']}` | `{item['reason']}` |"
        )
    report_md.write_text('\n'.join(lines) + '\n', encoding='utf-8')


def main() -> int:
    parser = argparse.ArgumentParser(description='Preflight python_functions and llamaindex stacks against the live runtime with runtime override.')
    parser.add_argument('--stack', choices=[*SUPPORTED_STACKS, 'all'], default='all')
    parser.add_argument('--base-url', default='http://127.0.0.1:8002')
    parser.add_argument('--internal-api-token', default=os.environ.get('INTERNAL_API_TOKEN', 'dev-internal-token'))
    parser.add_argument('--operator', default='codex')
    parser.add_argument('--dataset', type=Path, default=DEFAULT_DATASET)
    parser.add_argument('--report', type=Path, default=DEFAULT_REPORT)
    parser.add_argument('--json', type=Path, default=DEFAULT_JSON)
    parser.add_argument('--artifact-json', type=Path, default=DEFAULT_ARTIFACT_JSON)
    args = parser.parse_args()

    stacks = list(SUPPORTED_STACKS if args.stack == 'all' else [args.stack])
    cases = _load_cases(args.dataset)
    runtime_before = _get_runtime_primary_stack(base_url=args.base_url, internal_api_token=args.internal_api_token)
    results: list[dict[str, Any]] = []
    override_actions: list[dict[str, Any]] = []

    for stack in stacks:
        override_payload = _set_runtime_primary_stack(
            base_url=args.base_url,
            internal_api_token=args.internal_api_token,
            stack=stack,
            operator=args.operator,
            reason=f'nextgen_runtime_preflight_{stack}',
        )
        override_actions.append({'stack': stack, 'payload': override_payload})
        for case in cases:
            results.append(_run_case(base_url=args.base_url, internal_api_token=args.internal_api_token, stack=stack, case=case))

    runtime_after_restore = _restore_previous_override(
        base_url=args.base_url,
        internal_api_token=args.internal_api_token,
        operator=args.operator,
        previous_state=runtime_before,
    )

    payload = {
        'generated_at': datetime.now(UTC).isoformat(),
        'base_url': args.base_url,
        'dataset': str(args.dataset),
        'stacks': stacks,
        'runtime_before': runtime_before,
        'override_actions': override_actions,
        'runtime_after_restore': runtime_after_restore,
        'summary': {
            'by_stack': {stack: _summary_for_stack(results, stack=stack) for stack in stacks},
        },
        'results': results,
    }
    _write_report(report_md=args.report, report_json=args.json, artifact_json=args.artifact_json, payload=payload)
    print(args.report)
    print(args.json)
    return 0 if all(bucket['ready_for_controlled_runtime'] for bucket in payload['summary']['by_stack'].values()) else 1


if __name__ == '__main__':
    raise SystemExit(main())
