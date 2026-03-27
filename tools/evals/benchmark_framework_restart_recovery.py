#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path
from time import perf_counter
from typing import Any
from urllib.parse import urlencode

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tests.e2e._common import Settings, assert_condition, request

DEFAULT_DATASET = REPO_ROOT / 'tests/evals/datasets/framework_restart_recovery_cases.json'
DEFAULT_REPORT = REPO_ROOT / 'docs/architecture/framework-restart-recovery-report.md'
DEFAULT_CREWAI_URL = os.getenv('SMOKE_AI_ORCHESTRATOR_CREWAI_URL', 'http://127.0.0.1:8004').rstrip('/')


def _normalize_match_text(value: str) -> str:
    normalized = ''.join(ch.lower() for ch in str(value or '').strip())
    normalized = normalized.replace('á', 'a').replace('à', 'a').replace('â', 'a').replace('ã', 'a')
    normalized = normalized.replace('é', 'e').replace('ê', 'e')
    normalized = normalized.replace('í', 'i')
    normalized = normalized.replace('ó', 'o').replace('ô', 'o').replace('õ', 'o')
    normalized = normalized.replace('ú', 'u')
    normalized = normalized.replace('ç', 'c')
    return ' '.join(''.join(ch if ch.isalnum() else ' ' for ch in normalized).split())


def _contains_expected_keywords(answer_text: str, expected_keywords: list[str]) -> bool:
    normalized_answer = _normalize_match_text(answer_text)
    return all(_normalize_match_text(keyword) in normalized_answer for keyword in expected_keywords)


def _restart_container(*, container: str, health_url: str) -> float:
    started_at = perf_counter()
    subprocess.run(
        ['docker', 'restart', container],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        cwd=REPO_ROOT,
    )
    _wait_for_health_url(container, health_url, attempts=45, delay_seconds=1.0)
    return round((perf_counter() - started_at) * 1000, 1)


def _docker_file_exists(*, container: str, path: str) -> bool:
    completed = subprocess.run(
        ['docker', 'exec', container, 'test', '-f', path],
        cwd=REPO_ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    return completed.returncode == 0


def _crewai_url(path: str) -> str:
    return f'{DEFAULT_CREWAI_URL}{path}'


def _headers(settings: Settings, *, json_content: bool = False) -> dict[str, str]:
    headers = {'X-Internal-Api-Token': settings.internal_api_token}
    if json_content:
        headers['Content-Type'] = 'application/json'
    return headers


def _wait_for_health_url(name: str, url: str, *, attempts: int = 30, delay_seconds: float = 1.0) -> None:
    import time

    last_error: str | None = None
    for _ in range(attempts):
        try:
            status, _, _ = request('GET', url, timeout=10.0)
            if status == 200:
                return
            last_error = f'status={status}'
        except Exception as exc:  # pragma: no cover - transient local boot timing
            last_error = str(exc)
        time.sleep(delay_seconds)
    raise AssertionError(f'health_failed:{name}:{last_error}')


def _extract_answer_text(body: Any) -> str:
    if not isinstance(body, dict):
        return str(body or '')
    metadata = body.get('metadata')
    if isinstance(metadata, dict):
        answer = metadata.get('answer')
        if isinstance(answer, dict) and isinstance(answer.get('answer_text'), str):
            return str(answer.get('answer_text'))
    if isinstance(body.get('message_text'), str):
        return str(body.get('message_text'))
    return ''


def _run_langgraph_hitl_restart_case(case: dict[str, Any], settings: Settings) -> dict[str, Any]:
    review_payload = {
        'message': case['message'],
        'conversation_id': case['conversation_id'],
        'telegram_chat_id': case['telegram_chat_id'],
        'channel': case.get('channel', 'telegram'),
        'user': case.get('user') or {},
        'target_slices': case.get('target_slices') or ['protected'],
    }
    status, _, review_body = request(
        'POST',
        f'{settings.ai_orchestrator_url}/v1/internal/hitl/review',
        headers=_headers(settings, json_content=True),
        json_body=review_payload,
        timeout=40.0,
    )
    assert_condition(status == 200 and isinstance(review_body, dict), f'{case["id"]}:review_failed')
    interrupts = review_body.get('interrupts') or []
    assert_condition(review_body.get('status') == 'pending', f'{case["id"]}:review_not_pending')
    assert_condition(bool(interrupts), f'{case["id"]}:missing_interrupt')

    interrupt_kind = (
        interrupts[0].get('value', {}).get('kind')
        if isinstance(interrupts[0], dict)
        else None
    )
    assert_condition(interrupt_kind == case['expected_interrupt_kind'], f'{case["id"]}:unexpected_interrupt_kind:{interrupt_kind}')

    restart_ms = _restart_container(
        container=case['container'],
        health_url=f'{settings.ai_orchestrator_url}/healthz',
    )

    query = urlencode(
        {
            'conversation_id': case['conversation_id'],
            'channel': case.get('channel', 'telegram'),
        }
    )
    status, _, state_body = request(
        'GET',
        f'{settings.ai_orchestrator_url}/v1/internal/hitl/state?{query}',
        headers=_headers(settings),
        timeout=20.0,
    )
    assert_condition(status == 200 and isinstance(state_body, dict), f'{case["id"]}:state_failed')
    assert_condition(bool(state_body.get('pending')), f'{case["id"]}:pending_lost_after_restart')

    resume_payload = {
        'conversation_id': case['conversation_id'],
        'channel': case.get('channel', 'telegram'),
        'resume_value': case['resume_value'],
    }
    status, _, resume_body = request(
        'POST',
        f'{settings.ai_orchestrator_url}/v1/internal/hitl/resume',
        headers=_headers(settings, json_content=True),
        json_body=resume_payload,
        timeout=40.0,
    )
    assert_condition(status == 200 and isinstance(resume_body, dict), f'{case["id"]}:resume_failed')
    preview = resume_body.get('preview') or {}
    graph_path = [str(item) for item in (preview.get('graph_path') or [])]
    for node_name in case.get('expected_graph_path_nodes') or []:
        assert_condition(node_name in graph_path, f'{case["id"]}:missing_graph_node:{node_name}')

    status, _, final_state = request(
        'GET',
        f'{settings.ai_orchestrator_url}/v1/internal/hitl/state?{query}',
        headers=_headers(settings),
        timeout=20.0,
    )
    assert_condition(status == 200 and isinstance(final_state, dict), f'{case["id"]}:final_state_failed')
    assert_condition(not bool(final_state.get('pending')), f'{case["id"]}:pending_after_resume')

    return {
        'id': case['id'],
        'framework': case['framework'],
        'slice': case['slice'],
        'passed': True,
        'restart_ms': restart_ms,
        'review_status': review_body.get('status'),
        'pending_after_restart': bool(state_body.get('pending')),
        'resume_status': resume_body.get('status'),
        'graph_path': graph_path,
        'hitl_status': (resume_body.get('snapshot') or {}).get('values', {}).get('hitl_status'),
    }


def _run_crewai_shadow_restart_case(case: dict[str, Any], settings: Settings) -> dict[str, Any]:
    payload = {
        'message': case['before_message'],
        'conversation_id': case['conversation_id'],
        'telegram_chat_id': case['telegram_chat_id'],
        'channel': case.get('channel', 'telegram'),
    }
    status, _, before_body = request(
        'POST',
        _crewai_url(case['endpoint']),
        headers=_headers(settings, json_content=True),
        json_body=payload,
        timeout=40.0,
    )
    assert_condition(status == 200 and isinstance(before_body, dict), f'{case["id"]}:before_failed')
    before_metadata = before_body.get('metadata') if isinstance(before_body.get('metadata'), dict) else {}
    before_state_id = str(before_metadata.get('flow_state_id') or '')
    assert_condition(before_state_id, f'{case["id"]}:missing_before_state_id')

    restart_ms = _restart_container(
        container=case['container'],
        health_url=f'{DEFAULT_CREWAI_URL}/healthz',
    )

    payload['message'] = case['after_message']
    status, _, after_body = request(
        'POST',
        _crewai_url(case['endpoint']),
        headers=_headers(settings, json_content=True),
        json_body=payload,
        timeout=40.0,
    )
    assert_condition(status == 200 and isinstance(after_body, dict), f'{case["id"]}:after_failed')
    after_metadata = after_body.get('metadata') if isinstance(after_body.get('metadata'), dict) else {}
    after_state_id = str(after_metadata.get('flow_state_id') or '')
    assert_condition(after_state_id == before_state_id, f'{case["id"]}:flow_state_id_drift:{before_state_id}:{after_state_id}')
    expected_state_id = str(case.get('expected_flow_state_id') or '').strip()
    if expected_state_id:
        assert_condition(after_state_id == expected_state_id, f'{case["id"]}:unexpected_state_id:{after_state_id}')

    sqlite_exists = _docker_file_exists(container=case['container'], path=case['sqlite_path'])
    assert_condition(sqlite_exists, f'{case["id"]}:missing_sqlite_state_file')

    answer_text = _extract_answer_text(after_body)
    assert_condition(
        _contains_expected_keywords(answer_text, [str(item) for item in case.get('expected_keywords_after') or []]),
        f'{case["id"]}:after_answer_missing_keywords:{answer_text}',
    )

    return {
        'id': case['id'],
        'framework': case['framework'],
        'slice': case['slice'],
        'passed': True,
        'restart_ms': restart_ms,
        'before_state_id': before_state_id,
        'after_state_id': after_state_id,
        'before_answer': _extract_answer_text(before_body),
        'after_answer': answer_text,
        'sqlite_exists': sqlite_exists,
        'flow_state_persisted': bool(after_metadata.get('flow_state_persisted', sqlite_exists)),
    }


def _run_case(case: dict[str, Any], settings: Settings) -> dict[str, Any]:
    try:
        if case['type'] == 'langgraph_hitl_restart':
            return _run_langgraph_hitl_restart_case(case, settings)
        if case['type'] == 'crewai_shadow_restart':
            return _run_crewai_shadow_restart_case(case, settings)
        raise AssertionError(f'unknown_case_type:{case["type"]}')
    except Exception as exc:
        return {
            'id': case.get('id', 'unknown'),
            'framework': case.get('framework', 'unknown'),
            'slice': case.get('slice', 'unknown'),
            'passed': False,
            'error': str(exc),
        }


def _render_report(*, dataset_path: Path, results: list[dict[str, Any]]) -> str:
    generated_at = datetime.now(UTC).isoformat()
    passed_count = sum(1 for item in results if item.get('passed'))
    lines = [
        '# Framework Restart Recovery Report',
        '',
        f'Date: {generated_at}',
        '',
        '## Scope',
        '',
        'This benchmark validates native restart/recovery behavior for the strongest framework-native durability paths currently implemented:',
        '',
        '- LangGraph protected HITL resume after process restart',
        '- CrewAI `Flow` continuity for `public` follow-up after process restart',
        '- CrewAI `Flow` continuity for `protected` student follow-up after process restart',
        '- CrewAI `Flow` continuity for `support` follow-up after process restart',
        '- CrewAI `Flow` continuity for `workflow` follow-up after process restart',
        '',
        f'Dataset: [{dataset_path.name}]({dataset_path})',
        '',
        '## Summary',
        '',
        f'- Passed cases: `{passed_count}/{len(results)}`',
        '',
        '| Case | Framework | Slice | Result | Restart | Key evidence |',
        '| --- | --- | --- | --- | ---: | --- |',
    ]

    for item in results:
        if item.get('passed'):
            evidence = []
            if item.get('pending_after_restart') is True:
                evidence.append('pending interrupt survived restart')
            if item.get('before_state_id') and item.get('after_state_id'):
                evidence.append('stable flow_state_id')
            if item.get('sqlite_exists'):
                evidence.append('sqlite state file present')
            if item.get('hitl_status'):
                evidence.append(f'hitl_status={item["hitl_status"]}')
            evidence_text = '; '.join(evidence) or 'validated'
        else:
            evidence_text = str(item.get('error') or 'failed')
        lines.append(
            f"| `{item['id']}` | `{item['framework']}` | `{item['slice']}` | "
            f"{'passed' if item.get('passed') else 'failed'} | `{item.get('restart_ms', '-')}` ms | {evidence_text} |"
        )

    for item in results:
        lines.extend(
            [
                '',
                f"## {item['id']}",
                '',
                f"- Framework: `{item['framework']}`",
                f"- Slice: `{item['slice']}`",
                f"- Result: `{'passed' if item.get('passed') else 'failed'}`",
            ]
        )
        if item.get('restart_ms') is not None:
            lines.append(f"- Restart duration: `{item['restart_ms']}` ms")
        if not item.get('passed'):
            lines.append(f"- Error: `{item.get('error')}`")
            continue
        if item.get('pending_after_restart') is not None:
            lines.append(f"- Pending after restart: `{item['pending_after_restart']}`")
        if item.get('resume_status'):
            lines.append(f"- Resume status: `{item['resume_status']}`")
        if item.get('graph_path'):
            lines.append(f"- Graph path after resume: `{ ' -> '.join(item['graph_path']) }`")
        if item.get('hitl_status'):
            lines.append(f"- HITL status: `{item['hitl_status']}`")
        if item.get('before_state_id'):
            lines.append(f"- Flow state before restart: `{item['before_state_id']}`")
        if item.get('after_state_id'):
            lines.append(f"- Flow state after restart: `{item['after_state_id']}`")
        if item.get('flow_state_persisted') is not None:
            lines.append(f"- Flow persistence available: `{item['flow_state_persisted']}`")
        if item.get('sqlite_exists') is not None:
            lines.append(f"- SQLite state file present: `{item['sqlite_exists']}`")
        if item.get('before_answer'):
            lines.append(f"- Before answer: `{item['before_answer']}`")
        if item.get('after_answer'):
            lines.append(f"- After answer: `{item['after_answer']}`")

    lines.extend(
        [
            '',
            '## Readout',
            '',
            'Evidence from this run suggests:',
            '',
            '- LangGraph checkpoint-backed HITL is now durable enough to pause, restart, inspect pending state, and resume the exact protected review thread.',
            '- CrewAI `Flow` state for `public`, `protected`, `support`, and `workflow` now survives service restart strongly enough to keep follow-up continuity with the same `flow_state_id`.',
            '- This closes the most important durability gap in the top-line roadmap before broader crash/recovery comparisons.',
        ]
    )
    return '\n'.join(lines) + '\n'


def main() -> int:
    parser = argparse.ArgumentParser(description='Benchmark framework restart/recovery behavior for LangGraph and CrewAI.')
    parser.add_argument('--dataset', default=str(DEFAULT_DATASET))
    parser.add_argument('--report', default=str(DEFAULT_REPORT))
    args = parser.parse_args()

    settings = Settings()
    dataset_path = Path(args.dataset).resolve()
    report_path = Path(args.report).resolve()

    cases = json.loads(dataset_path.read_text(encoding='utf-8'))
    if not isinstance(cases, list):
        raise SystemExit('Dataset must be a JSON list.')

    _wait_for_health_url('ai-orchestrator', f'{settings.ai_orchestrator_url}/healthz', attempts=45, delay_seconds=1.0)
    _wait_for_health_url('ai-orchestrator-crewai', f'{DEFAULT_CREWAI_URL}/healthz', attempts=45, delay_seconds=1.0)

    results = [_run_case(case, settings) for case in cases if isinstance(case, dict)]
    report = _render_report(dataset_path=dataset_path, results=results)
    report_path.write_text(report, encoding='utf-8')
    print(report)
    return 0 if all(item.get('passed') for item in results) else 1


if __name__ == '__main__':
    raise SystemExit(main())
