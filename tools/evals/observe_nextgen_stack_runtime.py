#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import UTC, datetime
from pathlib import Path
from time import perf_counter
from typing import Any
from urllib import error, request

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
OBSERVABILITY_SRC = REPO_ROOT / 'packages/observability/python/src'
if str(OBSERVABILITY_SRC) not in sys.path:
    sys.path.insert(0, str(OBSERVABILITY_SRC))

from tools.evals.eval_quality_utils import (  # noqa: E402
    _contains_expected_keywords,
    _contains_forbidden_keywords,
    _detect_error_types,
    _detect_quality_signals,
    _expand_entries,
    _extract_answer_text,
    _normalize_prompt_entries,
    _quality_score,
)
from tools.evals.preflight_nextgen_stack_runtime import (  # noqa: E402
    SUPPORTED_STACKS,
    _get_runtime_primary_stack,
    _restore_previous_override,
    _set_runtime_primary_stack,
)

DEFAULT_DATASET = REPO_ROOT / 'tests/evals/datasets/nextgen_runtime_observation_cases.json'
DEFAULT_REPORT = REPO_ROOT / 'docs/architecture/nextgen-stack-runtime-observation-report.md'
DEFAULT_JSON = REPO_ROOT / 'docs/architecture/nextgen-stack-runtime-observation-report.json'
DEFAULT_ARTIFACT_JSON = REPO_ROOT / 'artifacts/nextgen-stack-runtime-observation-report.json'


def _http_json(
    *,
    method: str,
    url: str,
    payload: dict[str, Any] | None = None,
    headers: dict[str, str] | None = None,
    timeout: float = 40.0,
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


def _load_entries(path: Path) -> list[dict[str, Any]]:
    payload = json.loads(path.read_text(encoding='utf-8'))
    if isinstance(payload, dict) and isinstance(payload.get('threads'), list):
        return _expand_entries(payload['threads'])
    return _expand_entries(_normalize_prompt_entries(payload))


def _run_case(
    *,
    base_url: str,
    internal_api_token: str,
    stack: str,
    entry: dict[str, Any],
    previous_answer: str,
) -> dict[str, Any]:
    payload = {
        'message': str(entry['prompt']),
        'conversation_id': f"{entry.get('thread_id') or 'single'}:{stack}:runtime-observation",
        'telegram_chat_id': entry.get('telegram_chat_id'),
        'channel': 'telegram',
        'user': (
            {
                'role': 'guardian',
                'authenticated': True,
                'linked_student_ids': ['stu-lucas', 'stu-ana'],
                'scopes': ['students:read', 'administrative:read', 'financial:read', 'academic:read'],
            }
            if str(entry.get('slice') or '') == 'protected' or str(entry.get('telegram_chat_id') or '') == '1649845499'
            else {
                'role': 'anonymous',
                'authenticated': False,
                'linked_student_ids': [],
                'scopes': [],
            }
        ),
        'allow_graph_rag': True,
        'allow_handoff': True,
    }
    started = perf_counter()
    status, body = _http_json(
        method='POST',
        url=f'{base_url}/v1/messages/respond',
        payload=payload,
        headers={'X-Internal-Api-Token': internal_api_token},
        timeout=50.0,
    )
    latency_ms = round((perf_counter() - started) * 1000, 1)
    answer_text = _extract_answer_text(body)
    expected_keywords = [str(keyword) for keyword in (entry.get('expected_keywords') or []) if str(keyword).strip()]
    forbidden_keywords = [str(keyword) for keyword in (entry.get('forbidden_keywords') or []) if str(keyword).strip()]
    error_types = _detect_error_types(
        answer_text=answer_text,
        expected_keywords=expected_keywords,
        forbidden_keywords=forbidden_keywords,
        prompt=str(entry['prompt']),
        previous_answer=previous_answer,
        status=status,
        turn_index=int(entry.get('turn_index') or 1),
        note=str(entry.get('note') or ''),
    )
    quality_signals = _detect_quality_signals(
        answer_text=answer_text,
        expected_keywords=expected_keywords,
        prompt=str(entry['prompt']),
        previous_answer=previous_answer,
        turn_index=int(entry.get('turn_index') or 1),
        note=str(entry.get('note') or ''),
    )
    graph_path = [str(item) for item in (body.get('graph_path') or []) if str(item).strip()]
    expected_kernel = f'kernel:{stack}'
    observed_kernel = next((item for item in graph_path if item.startswith('kernel:')), '')
    foreign_kernel = bool(observed_kernel and observed_kernel != expected_kernel)
    keyword_pass = _contains_expected_keywords(answer_text, expected_keywords) and not _contains_forbidden_keywords(
        answer_text,
        forbidden_keywords,
    )
    return {
        'stack': stack,
        'prompt': str(entry['prompt']),
        'slice': str(entry.get('slice') or 'public'),
        'category': str(entry.get('category') or 'runtime_observation'),
        'thread_id': str(entry.get('thread_id') or ''),
        'turn_index': int(entry.get('turn_index') or 1),
        'note': str(entry.get('note') or ''),
        'status': status,
        'latency_ms': latency_ms,
        'mode': str(body.get('mode') or ''),
        'reason': str(body.get('reason') or ''),
        'access_tier': str((body.get('classification') or {}).get('access_tier') or ''),
        'graph_path': graph_path,
        'expected_kernel': expected_kernel,
        'observed_kernel': observed_kernel,
        'foreign_kernel': foreign_kernel,
        'answer_text': answer_text,
        'keyword_pass': keyword_pass,
        'quality_score': _quality_score(status=status, error_types=error_types),
        'error_types': error_types,
        'quality_signals': quality_signals,
        'expected_keywords': expected_keywords,
        'forbidden_keywords': forbidden_keywords,
    }


def _summarize(results: list[dict[str, Any]], *, stacks: list[str]) -> dict[str, Any]:
    by_stack: dict[str, dict[str, Any]] = {}
    by_slice: dict[str, dict[str, Any]] = {}
    by_thread: dict[str, dict[str, Any]] = {}
    error_types: dict[str, dict[str, int]] = {stack: {} for stack in stacks}

    for stack in stacks:
        subset = [row for row in results if row['stack'] == stack]
        by_stack[stack] = {
            'count': len(subset),
            'ok': sum(1 for row in subset if int(row['status']) == 200),
            'keyword_pass': sum(1 for row in subset if bool(row['keyword_pass'])),
            'quality_avg': round(sum(float(row['quality_score']) for row in subset) / max(1, len(subset)), 1),
            'avg_latency_ms': round(sum(float(row['latency_ms']) for row in subset) / max(1, len(subset)), 1),
            'max_latency_ms': round(max((float(row['latency_ms']) for row in subset), default=0.0), 1),
            'kernel_consistency_pass': bool(subset) and all(not row['foreign_kernel'] and row['expected_kernel'] in row['graph_path'] for row in subset),
        }
        by_stack[stack]['latency_watch'] = bool(
            by_stack[stack]['avg_latency_ms'] >= 1000.0 or by_stack[stack]['max_latency_ms'] >= 5000.0
        )
        by_stack[stack]['stable_for_controlled_runtime_window'] = bool(
            by_stack[stack]['count'] > 0
            and by_stack[stack]['ok'] == by_stack[stack]['count']
            and by_stack[stack]['keyword_pass'] == by_stack[stack]['count']
            and by_stack[stack]['kernel_consistency_pass']
            and by_stack[stack]['quality_avg'] >= 99.0
        )
        for row in subset:
            for error_name in row.get('error_types') or []:
                error_types[stack][error_name] = error_types[stack].get(error_name, 0) + 1

    slice_names = sorted({str(row['slice']) for row in results})
    for slice_name in slice_names:
        rows = [row for row in results if row['slice'] == slice_name]
        turn_count = len({(str(row.get('thread_id') or ''), int(row.get('turn_index') or 1), str(row.get('prompt') or '')) for row in rows})
        by_slice[slice_name] = {'count': len(rows), 'turn_count': turn_count}
        for stack in stacks:
            subset = [row for row in rows if row['stack'] == stack]
            by_slice[slice_name][stack] = {
                'count': len(subset),
                'ok': sum(1 for row in subset if int(row['status']) == 200),
                'keyword_pass': sum(1 for row in subset if bool(row['keyword_pass'])),
                'quality_avg': round(sum(float(row['quality_score']) for row in subset) / max(1, len(subset)), 1),
                'avg_latency_ms': round(sum(float(row['latency_ms']) for row in subset) / max(1, len(subset)), 1),
            }

    thread_keys = sorted({str(row['thread_id']) for row in results if str(row.get('thread_id') or '').strip()})
    for thread_id in thread_keys:
        rows = [row for row in results if row['thread_id'] == thread_id]
        bucket = {
            'count': len(rows),
            'turn_count': len({(int(row.get('turn_index') or 1), str(row.get('prompt') or '')) for row in rows}),
            'slice': rows[0]['slice'] if rows else '',
        }
        for stack in stacks:
            subset = [row for row in rows if row['stack'] == stack]
            bucket[stack] = {
                'count': len(subset),
                'ok': sum(1 for row in subset if int(row['status']) == 200),
                'keyword_pass': sum(1 for row in subset if bool(row['keyword_pass'])),
                'quality_avg': round(sum(float(row['quality_score']) for row in subset) / max(1, len(subset)), 1),
                'avg_latency_ms': round(sum(float(row['latency_ms']) for row in subset) / max(1, len(subset)), 1),
            }
        by_thread[thread_id] = bucket

    return {
        'by_stack': by_stack,
        'by_slice': by_slice,
        'by_thread': by_thread,
        'error_types': error_types,
    }


def _render_markdown(payload: dict[str, Any]) -> str:
    lines = ['# Next-Gen Stack Runtime Observation Report', '']
    lines.append(f"Date: {payload['generated_at']}")
    lines.append('')
    lines.append(f"Base URL: `{payload['base_url']}`")
    lines.append('')
    lines.append(f"Dataset: `{payload['dataset']}`")
    lines.append('')
    lines.append('## Summary')
    lines.append('')
    lines.append('| Stack | OK | Keyword pass | Quality | Avg latency | Stable window | Latency watch |')
    lines.append('| --- | --- | --- | --- | --- | --- | --- |')
    for stack in payload['stacks']:
        bucket = payload['summary']['by_stack'][stack]
        lines.append(
            f"| `{stack}` | `{bucket['ok']}/{bucket['count']}` | `{bucket['keyword_pass']}/{bucket['count']}` | `{bucket['quality_avg']}` | `{bucket['avg_latency_ms']} ms` | `{bucket['stable_for_controlled_runtime_window']}` | `{bucket['latency_watch']}` |"
        )
    lines.extend(
        [
            '',
            '## Runtime State',
            '',
            f"- Before: `resolved={payload['runtime_before'].get('resolvedPrimaryStack')}` from `{payload['runtime_before'].get('resolvedPrimaryStackSource')}`",
            f"- After restore: `resolved={payload['runtime_after_restore'].get('resolvedPrimaryStack')}` from `{payload['runtime_after_restore'].get('resolvedPrimaryStackSource')}`",
            '',
            '## By Slice',
            '',
        ]
    )
    for slice_name, bucket in payload['summary']['by_slice'].items():
        lines.append(f"- `{slice_name}` ({bucket.get('turn_count', 0)} turns)")
        for stack in payload['stacks']:
            stack_bucket = bucket.get(stack) or {}
            lines.append(
                f"  - `{stack}`: ok {stack_bucket.get('ok', 0)}/{stack_bucket.get('count', 0)}, keyword pass {stack_bucket.get('keyword_pass', 0)}/{stack_bucket.get('count', 0)}, quality {stack_bucket.get('quality_avg', 0)}, latency {stack_bucket.get('avg_latency_ms', 0)}ms"
            )
    lines.extend(['', '## By Thread', ''])
    for thread_id, bucket in payload['summary']['by_thread'].items():
        lines.append(f"- `{thread_id}` ({bucket.get('slice')}, {bucket.get('turn_count', 0)} turns)")
        for stack in payload['stacks']:
            stack_bucket = bucket.get(stack) or {}
            lines.append(
                f"  - `{stack}`: ok {stack_bucket.get('ok', 0)}/{stack_bucket.get('count', 0)}, keyword pass {stack_bucket.get('keyword_pass', 0)}/{stack_bucket.get('count', 0)}, quality {stack_bucket.get('quality_avg', 0)}, latency {stack_bucket.get('avg_latency_ms', 0)}ms"
            )
    lines.extend(['', '## Error Types', ''])
    for stack, bucket in payload['summary']['error_types'].items():
        items = ', '.join(f'{name}={count}' for name, count in sorted(bucket.items()))
        lines.append(f"- `{stack}`: {items or 'nenhum'}")
    lines.extend(['', '## Operational Notes', ''])
    for stack in payload['stacks']:
        bucket = payload['summary']['by_stack'][stack]
        if bucket.get('latency_watch'):
            lines.append(
                f"- `{stack}` entrou em observacao estavel, mas ainda merece atencao de latencia: media `{bucket['avg_latency_ms']} ms`, pico `{bucket['max_latency_ms']} ms`."
            )
        else:
            lines.append(f"- `{stack}` ficou estavel e sem alerta de latencia relevante nesta janela curta.")
    lines.extend(['', '## Prompt Results', ''])
    for row in payload['results']:
        lines.append(f"### {row['prompt']}")
        lines.append('')
        lines.append(f"- Stack: `{row['stack']}`")
        lines.append(f"- Slice: `{row['slice']}`")
        if row.get('thread_id'):
            lines.append(f"- Thread: `{row['thread_id']}` turn `{row['turn_index']}`")
        lines.append(f"- Status: `{row['status']}`")
        lines.append(f"- Latency: `{row['latency_ms']} ms`")
        lines.append(f"- Mode: `{row['mode']}`")
        lines.append(f"- Reason: `{row['reason']}`")
        lines.append(f"- Access tier: `{row['access_tier']}`")
        lines.append(f"- Expected kernel: `{row['expected_kernel']}`")
        lines.append(f"- Observed kernel: `{row['observed_kernel']}`")
        lines.append(f"- Kernel consistency: `{not row['foreign_kernel'] and row['expected_kernel'] in row['graph_path']}`")
        lines.append(f"- Keyword pass: `{row['keyword_pass']}`")
        lines.append(f"- Quality score: `{row['quality_score']}`")
        if row.get('error_types'):
            lines.append(f"- Errors: {', '.join(row['error_types'])}")
        lines.append(f"- Answer: {row['answer_text']}")
        lines.append('')
    return '\n'.join(lines)


def _write_outputs(*, report_md: Path, report_json: Path, artifact_json: Path, payload: dict[str, Any]) -> None:
    json_text = json.dumps(payload, ensure_ascii=False, indent=2) + '\n'
    report_json.write_text(json_text, encoding='utf-8')
    artifact_json.write_text(json_text, encoding='utf-8')
    report_md.write_text(_render_markdown(payload) + '\n', encoding='utf-8')


def main() -> int:
    parser = argparse.ArgumentParser(description='Observe python_functions and llamaindex in the live runtime using runtime override.')
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
    entries = _load_entries(args.dataset)
    runtime_before = _get_runtime_primary_stack(base_url=args.base_url, internal_api_token=args.internal_api_token)
    override_actions: list[dict[str, Any]] = []
    results: list[dict[str, Any]] = []
    previous_answers: dict[tuple[str, str], str] = {}

    try:
        for stack in stacks:
            override_payload = _set_runtime_primary_stack(
                base_url=args.base_url,
                internal_api_token=args.internal_api_token,
                stack=stack,
                operator=args.operator,
                reason=f'nextgen_runtime_observation_{stack}',
            )
            override_actions.append({'stack': stack, 'payload': override_payload})
            for entry in entries:
                thread_id = str(entry.get('thread_id') or '')
                previous_answer = previous_answers.get((stack, thread_id), '') if thread_id else ''
                row = _run_case(
                    base_url=args.base_url,
                    internal_api_token=args.internal_api_token,
                    stack=stack,
                    entry=entry,
                    previous_answer=previous_answer,
                )
                results.append(row)
                if thread_id:
                    previous_answers[(stack, thread_id)] = row['answer_text']
    finally:
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
        'summary': _summarize(results, stacks=stacks),
        'results': results,
    }
    _write_outputs(report_md=args.report, report_json=args.json, artifact_json=args.artifact_json, payload=payload)
    print(args.report)
    print(args.json)
    return 0 if all(
        payload['summary']['by_stack'][stack]['stable_for_controlled_runtime_window']
        for stack in stacks
    ) else 1


if __name__ == '__main__':
    raise SystemExit(main())
