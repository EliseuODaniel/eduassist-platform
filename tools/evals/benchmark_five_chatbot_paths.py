#!/usr/bin/env python3
from __future__ import annotations

import argparse
import asyncio
import json
import sys
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from time import perf_counter
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
AI_ORCHESTRATOR_SRC = REPO_ROOT / 'apps/ai-orchestrator/src'
if str(AI_ORCHESTRATOR_SRC) not in sys.path:
    sys.path.insert(0, str(AI_ORCHESTRATOR_SRC))
SEMANTIC_INGRESS_SRC = REPO_ROOT / 'packages/semantic-ingress/python/src'
if str(SEMANTIC_INGRESS_SRC) not in sys.path:
    sys.path.insert(0, str(SEMANTIC_INGRESS_SRC))

from ai_orchestrator.engine_selector import build_engine_bundle
from ai_orchestrator.main import Settings
from ai_orchestrator.models import MessageResponseRequest, UserContext

DEFAULT_DATASET = REPO_ROOT / 'tests/evals/datasets/four_path_chatbot_smoke_cases.json'
DEFAULT_REPORT = REPO_ROOT / 'docs/architecture/five-path-chatbot-smoke-report.md'
DEFAULT_JSON_REPORT = REPO_ROOT / 'docs/architecture/five-path-chatbot-smoke-report.json'
STACKS = ('langgraph', 'python_functions', 'llamaindex', 'specialist_supervisor')


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


def _make_settings(*, stack: str) -> Settings:
    fallback = 'langgraph' if stack != 'langgraph' else 'python_functions'
    return Settings(
        orchestrator_engine=fallback,
        feature_flag_primary_orchestration_stack=stack,
        strict_framework_isolation_enabled=True,
        orchestrator_experiment_enabled=False,
        langgraph_checkpointer_enabled=False,
        api_core_url='http://127.0.0.1:8001',
        qdrant_url='http://127.0.0.1:6333',
        database_url='postgresql://eduassist:eduassist@127.0.0.1:5432/eduassist',
        specialist_supervisor_pilot_url='http://127.0.0.1:8015',
    )


def _build_request(case: dict[str, Any], *, stack: str, run_prefix: str) -> MessageResponseRequest:
    return MessageResponseRequest(
        message=str(case['message']),
        conversation_id=f"{run_prefix}:{case['conversation_id']}-{stack}",
        telegram_chat_id=int(case['telegram_chat_id']),
        channel='telegram',
        user=UserContext.model_validate(case.get('user') or {}),
        allow_graph_rag=True,
        allow_handoff=True,
    )


async def _run_case(case: dict[str, Any], *, stack: str, run_prefix: str) -> CaseResult:
    settings = _make_settings(stack=stack)
    request = _build_request(case, stack=stack, run_prefix=run_prefix)
    bundle = build_engine_bundle(settings, request=request)
    started = perf_counter()
    try:
        response = await asyncio.wait_for(
            bundle.primary.respond(request=request, settings=settings, engine_mode=bundle.mode),
            timeout=45.0,
        )
        latency_ms = (perf_counter() - started) * 1000
        expected_access_tier = str(case.get('expected_access_tier') or '').strip()
        access_tier = response.classification.access_tier.value
        passed = bool(response.message_text.strip()) and (not expected_access_tier or access_tier == expected_access_tier)
        return CaseResult(
            case_id=str(case['id']),
            stack=stack,
            passed=passed,
            latency_ms=latency_ms,
            mode=response.mode.value,
            access_tier=access_tier,
            reason=response.reason,
            graph_path=list(response.graph_path),
            message_preview=response.message_text[:180],
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


async def _run_all(cases: list[dict[str, Any]]) -> tuple[str, list[CaseResult]]:
    run_prefix = f"debug:five-path-smoke:{datetime.now(UTC).strftime('%Y%m%dT%H%M%SZ')}"
    results: list[CaseResult] = []
    for stack in STACKS:
        for case in cases:
            results.append(await _run_case(case, stack=stack, run_prefix=run_prefix))
    return run_prefix, results


def _summary_for_stack(results: list[CaseResult], *, stack: str) -> dict[str, Any]:
    subset = [item for item in results if item.stack == stack]
    if not subset:
        return {'passed': 0, 'total': 0, 'avg_latency_ms': None}
    passed = sum(1 for item in subset if item.passed)
    avg_latency_ms = sum(item.latency_ms for item in subset) / len(subset)
    return {'passed': passed, 'total': len(subset), 'avg_latency_ms': round(avg_latency_ms, 1)}


def _write_reports(*, dataset: Path, run_prefix: str, results: list[CaseResult], markdown_path: Path, json_path: Path) -> None:
    generated_at = datetime.now(UTC).isoformat()
    payload = {
        'generated_at': generated_at,
        'dataset': str(dataset),
        'run_prefix': run_prefix,
        'stacks': {stack: _summary_for_stack(results, stack=stack) for stack in STACKS},
        'results': [item.__dict__ for item in results],
    }
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

    lines = [
        '# Active-Path Chatbot Smoke Report',
        '',
        f'Date: {generated_at}',
        '',
        f'Dataset: `{dataset}`',
        '',
        f'Run prefix: `{run_prefix}`',
        '',
        '## Goal',
        '',
        'Validate the active chatbot paths side by side under strict framework isolation:',
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
            '- `python_functions` is the lean code-first baseline with a planner/executor/reflection loop.',
            '- `llamaindex` pushes native workflow, retrieval, citation, and document lifecycle capabilities further.',
            '- `specialist_supervisor` is the quality-first path with manager pattern and specialists-as-tools on top of the shared truth sources.',
            '- `langgraph` is the graph-native reference path for more stateful orchestration.',
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
    run_prefix, results = asyncio.run(_run_all(cases))
    _write_reports(
        dataset=args.dataset,
        run_prefix=run_prefix,
        results=results,
        markdown_path=args.report,
        json_path=args.json_report,
    )
    print(args.report)
    print(args.json_report)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
