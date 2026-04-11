#!/usr/bin/env python3
from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from time import perf_counter
from typing import Any

import httpx

REPO_ROOT = Path(__file__).resolve().parents[2]


def _load_local_env(path: Path) -> None:
    if not path.exists():
        return
    for raw_line in path.read_text(encoding='utf-8').splitlines():
        line = raw_line.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue
        key, value = line.split('=', 1)
        os.environ.setdefault(key.strip(), value.strip())


_load_local_env(REPO_ROOT / '.env')
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
AI_ORCHESTRATOR_SRC = REPO_ROOT / 'apps/ai-orchestrator/src'
if str(AI_ORCHESTRATOR_SRC) not in sys.path:
    sys.path.insert(0, str(AI_ORCHESTRATOR_SRC))

from ai_orchestrator.models import MessageResponseRequest, UserContext

DEFAULT_DATASET = REPO_ROOT / 'tests/evals/datasets/four_path_chatbot_smoke_cases.json'
DEFAULT_REPORT = REPO_ROOT / 'docs/architecture/four-path-chatbot-smoke-report.md'
DEFAULT_JSON_REPORT = REPO_ROOT / 'docs/architecture/four-path-chatbot-smoke-report.json'
STACKS = ('langgraph', 'python_functions', 'llamaindex', 'specialist_supervisor')
STACK_URLS = {
    'langgraph': os.getenv('AI_ORCHESTRATOR_LANGGRAPH_BENCH_URL', 'http://127.0.0.1:8006'),
    'python_functions': os.getenv('AI_ORCHESTRATOR_PYTHON_FUNCTIONS_BENCH_URL', 'http://127.0.0.1:8007'),
    'llamaindex': os.getenv('AI_ORCHESTRATOR_LLAMAINDEX_BENCH_URL', 'http://127.0.0.1:8008'),
    'specialist_supervisor': os.getenv('AI_ORCHESTRATOR_SPECIALIST_BENCH_URL', 'http://127.0.0.1:8015'),
}
INTERNAL_API_TOKEN = os.getenv('INTERNAL_API_TOKEN', 'dev-internal-token')


@dataclass
class CaseResult:
    case_id: str
    stack: str
    passed: bool
    latency_ms: float
    mode: str
    access_tier: str
    reason: str
    graph_path: list[str]
    message_preview: str
    error: str | None = None


def _build_request(case: dict[str, Any], *, stack: str) -> MessageResponseRequest:
    return MessageResponseRequest(
        message=str(case['message']),
        conversation_id=f"{case['conversation_id']}-{stack}",
        telegram_chat_id=int(case['telegram_chat_id']),
        channel='telegram',
        user=UserContext.model_validate(case.get('user') or {}),
        allow_graph_rag=True,
        allow_handoff=True,
    )


async def _run_case(case: dict[str, Any], *, stack: str) -> CaseResult:
    request = _build_request(case, stack=stack)
    target_url = str(STACK_URLS[stack]).rstrip('/')
    started = perf_counter()
    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(10.0, connect=3.0)) as client:
            http_response = await asyncio.wait_for(
                client.post(
                    f'{target_url}/v1/messages/respond',
                    headers={'X-Internal-Api-Token': INTERNAL_API_TOKEN},
                    json=request.model_dump(mode='json'),
                ),
                timeout=11.0,
            )
        http_response.raise_for_status()
        response = http_response.json()
        latency_ms = (perf_counter() - started) * 1000
        expected_access_tier = str(case.get('expected_access_tier') or '').strip()
        access_tier = str(response.get('classification', {}).get('access_tier') or 'unknown')
        message_text = str(response.get('message_text') or '')
        passed = bool(message_text.strip()) and (not expected_access_tier or access_tier == expected_access_tier)
        return CaseResult(
            case_id=str(case['id']),
            stack=stack,
            passed=passed,
            latency_ms=latency_ms,
            mode=str(response.get('mode') or 'unknown'),
            access_tier=access_tier,
            reason=str(response.get('reason') or ''),
            graph_path=list(response.get('graph_path') or []),
            message_preview=message_text[:180],
            error=None,
        )
    except Exception as exc:
        latency_ms = (perf_counter() - started) * 1000
        return CaseResult(
            case_id=str(case['id']),
            stack=stack,
            passed=False,
            latency_ms=latency_ms,
            mode='error',
            access_tier='unknown',
            reason='exception',
            graph_path=[],
            message_preview='',
            error=f'{type(exc).__name__}: {exc}',
        )


async def _run_all(cases: list[dict[str, Any]]) -> list[CaseResult]:
    results: list[CaseResult] = []
    for stack in STACKS:
        for case in cases:
            results.append(await _run_case(case, stack=stack))
    return results


def _summary_for_stack(results: list[CaseResult], *, stack: str) -> dict[str, Any]:
    subset = [item for item in results if item.stack == stack]
    if not subset:
        return {'passed': 0, 'total': 0, 'avg_latency_ms': None}
    passed = sum(1 for item in subset if item.passed)
    avg_latency_ms = sum(item.latency_ms for item in subset) / len(subset)
    return {'passed': passed, 'total': len(subset), 'avg_latency_ms': round(avg_latency_ms, 1)}


def _write_reports(*, results: list[CaseResult], markdown_path: Path, json_path: Path) -> None:
    generated_at = datetime.now(UTC).isoformat()
    payload = {
        'generated_at': generated_at,
        'stacks': {stack: _summary_for_stack(results, stack=stack) for stack in STACKS},
        'results': [item.__dict__ for item in results],
    }
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

    lines = [
        '# Four-Path Chatbot Smoke Report',
        '',
        f'Date: {generated_at}',
        '',
        '## Goal',
        '',
        'Validate the first four chatbot paths side by side under strict framework isolation:',
        '',
        '- `langgraph`',
        '- `python_functions`',
        '- `llamaindex`',
        '- `specialist_supervisor`',
        '',
        '## Stack Summary',
        '',
        '| Stack | Passed | Avg latency |',
        '| --- | --- | --- |',
    ]
    for stack in STACKS:
        summary = _summary_for_stack(results, stack=stack)
        lines.append(f"| `{stack}` | `{summary['passed']}/{summary['total']}` | `{summary['avg_latency_ms']} ms` |")

    lines.extend(
        [
            '',
            '## Case Details',
            '',
            '| Case | Stack | Result | Mode | Access tier | Latency | Notes |',
            '| --- | --- | --- | --- | --- | --- | --- |',
        ]
    )
    for item in results:
        notes = item.error or item.reason
        lines.append(
            f"| `{item.case_id}` | `{item.stack}` | {'passed' if item.passed else 'failed'} | `{item.mode}` | `{item.access_tier}` | `{item.latency_ms:.1f} ms` | {notes} |"
        )

    lines.extend(
        [
            '',
            '## Interpretation',
            '',
            '- `python_functions` is the lean baseline: shared planner and executor, no heavy orchestration framework around the control loop.',
            '- `llamaindex` uses the same planner/executor kernel but runs it inside a native LlamaIndex Workflow with explicit `plan -> execute -> reflect` steps.',
            '- `langgraph` remains the graph-native reference path for stateful orchestration.',
            '',
        ]
    )
    markdown_path.write_text('\n'.join(lines) + '\n', encoding='utf-8')


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--dataset', type=Path, default=DEFAULT_DATASET)
    parser.add_argument('--report', type=Path, default=DEFAULT_REPORT)
    parser.add_argument('--json-report', type=Path, default=DEFAULT_JSON_REPORT)
    args = parser.parse_args()

    cases = json.loads(args.dataset.read_text(encoding='utf-8'))
    results = asyncio.run(_run_all(cases))
    _write_reports(results=results, markdown_path=args.report, json_path=args.json_report)
    print(args.report)
    print(args.json_report)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
