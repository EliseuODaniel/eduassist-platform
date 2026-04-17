#!/usr/bin/env python3
from __future__ import annotations

import argparse
import asyncio
import json
import math
import os
import statistics
import sys
from datetime import UTC, datetime
from pathlib import Path
from time import perf_counter
from typing import Any
from uuid import uuid4

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

from ai_orchestrator.models import ConversationChannel, MessageResponseRequest, UserContext  # noqa: E402
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

DEFAULT_DATASET = REPO_ROOT / 'tests/evals/datasets/specialist_model_ab_cases.20260417.json'
DEFAULT_OUTPUT_DIR = REPO_ROOT / 'artifacts/model-ab'
DEFAULT_BASE_URL = os.getenv('AI_ORCHESTRATOR_SPECIALIST_BENCH_URL', 'http://127.0.0.1:8005')
INTERNAL_API_TOKEN = os.getenv('INTERNAL_API_TOKEN', 'dev-internal-token')
RUN_ID = uuid4().hex[:8]


def _load_dataset(path: Path) -> list[dict[str, Any]]:
    payload = json.loads(path.read_text(encoding='utf-8'))
    if isinstance(payload, dict) and isinstance(payload.get('threads'), list):
        return _expand_entries(payload['threads'])
    return _expand_entries(_normalize_prompt_entries(payload))


def _user(entry: dict[str, Any]) -> UserContext:
    explicit_user = entry.get('user')
    if isinstance(explicit_user, dict) and explicit_user:
        return UserContext.model_validate(explicit_user)
    return UserContext(role='anonymous', authenticated=False)


async def _fetch_status(*, base_url: str) -> dict[str, Any]:
    async with httpx.AsyncClient(timeout=httpx.Timeout(10.0, connect=3.0)) as client:
        response = await client.get(
            f'{base_url.rstrip("/")}/v1/status',
            headers={'X-Internal-Api-Token': INTERNAL_API_TOKEN},
        )
        response.raise_for_status()
        payload = response.json()
    return payload if isinstance(payload, dict) else {}


async def _wait_for_health(*, base_url: str, timeout_seconds: float = 180.0) -> None:
    deadline = perf_counter() + timeout_seconds
    last_error = 'uninitialized'
    while perf_counter() < deadline:
        try:
            async with httpx.AsyncClient(timeout=httpx.Timeout(5.0, connect=2.0)) as client:
                response = await client.get(f'{base_url.rstrip("/")}/healthz')
            if response.status_code == 200:
                return
            last_error = f'http_{response.status_code}'
        except Exception as exc:
            last_error = f'{type(exc).__name__}: {exc}'
        await asyncio.sleep(2.0)
    raise SystemExit(f'specialist_runtime_not_ready: {last_error}')


async def _run_turn(
    *,
    base_url: str,
    entry: dict[str, Any],
    model_label: str,
    timeout_seconds: float,
    previous_answer: str,
) -> dict[str, Any]:
    conversation_id = f"model-ab:{model_label}:{entry.get('thread_id') or entry.get('id') or 'single'}:{RUN_ID}"
    request = MessageResponseRequest(
        message=str(entry['prompt']),
        conversation_id=conversation_id,
        channel=ConversationChannel.telegram,
        telegram_chat_id=entry.get('telegram_chat_id'),
        user=_user(entry),
        allow_graph_rag=True,
        allow_handoff=True,
    )
    started = perf_counter()
    try:
        connect_timeout = min(5.0, max(1.0, timeout_seconds / 5.0))
        async with httpx.AsyncClient(timeout=httpx.Timeout(timeout_seconds, connect=connect_timeout)) as client:
            response = await client.post(
                f'{base_url.rstrip("/")}/v1/messages/respond',
                headers={'X-Internal-Api-Token': INTERNAL_API_TOKEN},
                json=request.model_dump(mode='json'),
            )
        response.raise_for_status()
        latency_ms = round((perf_counter() - started) * 1000, 1)
        body = response.json()
        answer_text = _extract_answer_text(body)
        expected_keywords = [str(item) for item in (entry.get('expected_keywords') or [])]
        forbidden_keywords = [str(item) for item in (entry.get('forbidden_keywords') or [])]
        keyword_pass = _contains_expected_keywords(answer_text, expected_keywords) and not _contains_forbidden_keywords(
            answer_text,
            forbidden_keywords,
        )
        error_types = _detect_error_types(
            answer_text=answer_text,
            expected_keywords=expected_keywords,
            forbidden_keywords=forbidden_keywords,
            expected_sections=[str(item) for item in (entry.get('expected_sections') or [])],
            rubric_tags=[str(item) for item in (entry.get('rubric_tags') or [])],
            prompt=str(entry['prompt']),
            previous_answer=previous_answer,
            status=200,
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
        quality_score = min(
            100,
            _quality_score(status=200, error_types=error_types)
            + (5 * sum(1 for value in quality_signals.values() if value is True)),
        )
        return {
            'id': str(entry.get('id') or ''),
            'thread_id': str(entry.get('thread_id') or ''),
            'turn_index': int(entry.get('turn_index') or 1),
            'slice': str(entry.get('slice') or 'public'),
            'category': str(entry.get('category') or 'uncategorized'),
            'note': str(entry.get('note') or ''),
            'prompt': str(entry['prompt']),
            'status': 200,
            'latency_ms': latency_ms,
            'mode': str(body.get('mode') or 'unknown'),
            'reason': str(body.get('reason') or ''),
            'graph_path': list(body.get('graph_path') or []),
            'used_llm': bool(body.get('used_llm', False)),
            'llm_stages': list(body.get('llm_stages') or []),
            'final_polish_applied': bool(body.get('final_polish_applied', False)),
            'final_polish_mode': body.get('final_polish_mode'),
            'final_polish_reason': body.get('final_polish_reason'),
            'answer_experience_applied': bool(body.get('answer_experience_applied', False)),
            'answer_experience_reason': body.get('answer_experience_reason'),
            'answer_experience_provider': body.get('answer_experience_provider'),
            'answer_experience_model': body.get('answer_experience_model'),
            'message_text': answer_text,
            'expected_keywords': expected_keywords,
            'forbidden_keywords': forbidden_keywords,
            'keyword_pass': bool(keyword_pass),
            'error_types': error_types,
            'quality_signals': quality_signals,
            'quality_score': int(quality_score),
        }
    except Exception as exc:
        latency_ms = round((perf_counter() - started) * 1000, 1)
        return {
            'id': str(entry.get('id') or ''),
            'thread_id': str(entry.get('thread_id') or ''),
            'turn_index': int(entry.get('turn_index') or 1),
            'slice': str(entry.get('slice') or 'public'),
            'category': str(entry.get('category') or 'uncategorized'),
            'note': str(entry.get('note') or ''),
            'prompt': str(entry['prompt']),
            'status': 599,
            'latency_ms': latency_ms,
            'mode': 'error',
            'reason': 'exception',
            'graph_path': [],
            'used_llm': False,
            'llm_stages': [],
            'final_polish_applied': False,
            'final_polish_mode': None,
            'final_polish_reason': None,
            'answer_experience_applied': False,
            'answer_experience_reason': None,
            'answer_experience_provider': None,
            'answer_experience_model': None,
            'message_text': '',
            'expected_keywords': [str(item) for item in (entry.get('expected_keywords') or [])],
            'forbidden_keywords': [str(item) for item in (entry.get('forbidden_keywords') or [])],
            'keyword_pass': False,
            'error_types': ['request_failed'],
            'quality_signals': {},
            'quality_score': 40,
            'error': f'{type(exc).__name__}: {exc}',
        }


def _percentile(values: list[float], p: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    if len(ordered) == 1:
        return float(ordered[0])
    rank = (len(ordered) - 1) * p
    lower = math.floor(rank)
    upper = math.ceil(rank)
    if lower == upper:
        return float(ordered[lower])
    return float(ordered[lower] + (ordered[upper] - ordered[lower]) * (rank - lower))


def _bucket(rows: list[dict[str, Any]]) -> dict[str, Any]:
    latencies = [float(item['latency_ms']) for item in rows]
    return {
        'count': len(rows),
        'ok': sum(1 for item in rows if int(item['status']) == 200),
        'keyword_pass': sum(1 for item in rows if bool(item['keyword_pass'])),
        'quality_avg': round(sum(float(item['quality_score']) for item in rows) / max(1, len(rows)), 1),
        'avg_latency_ms': round(sum(latencies) / max(1, len(latencies)), 1),
        'median_latency_ms': round(statistics.median(latencies), 1) if latencies else 0.0,
        'p95_latency_ms': round(_percentile(latencies, 0.95), 1),
        'final_polish_applied': sum(1 for item in rows if bool(item['final_polish_applied'])),
    }


def _render_markdown(payload: dict[str, Any]) -> str:
    lines = ['# Specialist Model Profile Evaluation', '']
    lines.append(f"Date: {payload['generated_at']}")
    lines.append('')
    lines.append(f"Model label: `{payload['model_label']}`")
    lines.append(f"Runtime URL: `{payload['base_url']}`")
    lines.append(f"Dataset: `{payload['dataset']}`")
    lines.append('')
    status = payload.get('runtime_status') or {}
    if status:
        lines.append('## Runtime Status')
        lines.append('')
        lines.append(f"- llmModelProfile: `{status.get('llmModelProfile', 'unknown')}`")
        lines.append(f"- llmProvider: `{status.get('llmProvider', 'unknown')}`")
        lines.append(f"- openaiApiMode: `{status.get('openaiApiMode', 'unknown')}`")
        lines.append(f"- openaiModel: `{status.get('openaiModel', 'unknown')}`")
        lines.append('')
    summary = payload['summary']
    lines.append('## Overall Summary')
    lines.append('')
    lines.append(f"- ok: `{summary['overall']['ok']}/{summary['overall']['count']}`")
    lines.append(f"- keyword pass: `{summary['overall']['keyword_pass']}/{summary['overall']['count']}`")
    lines.append(f"- quality avg: `{summary['overall']['quality_avg']}`")
    lines.append(f"- avg latency: `{summary['overall']['avg_latency_ms']} ms`")
    lines.append(f"- p95 latency: `{summary['overall']['p95_latency_ms']} ms`")
    lines.append('')
    lines.append('## By Slice')
    lines.append('')
    lines.append('| Slice | OK | Keyword pass | Quality | Avg latency |')
    lines.append('| --- | --- | --- | --- | --- |')
    for slice_name, bucket in summary['by_slice'].items():
        lines.append(
            f"| `{slice_name}` | `{bucket['ok']}/{bucket['count']}` | `{bucket['keyword_pass']}/{bucket['count']}` | `{bucket['quality_avg']}` | `{bucket['avg_latency_ms']} ms` |"
        )
    lines.append('')
    failing = [item for item in payload['results'] if int(item['status']) != 200 or int(item['quality_score']) < 100]
    if failing:
        lines.append('## Non-Perfect Cases')
        lines.append('')
        for item in failing:
            lines.append(f"### {item['id']} `{item['slice']}` `{item['category']}`")
            lines.append('')
            lines.append(f"- prompt: `{item['prompt']}`")
            lines.append(f"- status: `{item['status']}`")
            lines.append(f"- quality: `{item['quality_score']}`")
            lines.append(f"- keyword pass: `{item['keyword_pass']}`")
            lines.append(f"- latency: `{item['latency_ms']} ms`")
            lines.append(f"- reason: `{item['reason']}`")
            lines.append(f"- errors: `{', '.join(item['error_types']) or 'none'}`")
            lines.append(f"- answer: {item['message_text'] or item.get('error', '')}")
            lines.append('')
    lines.append('## Case Log')
    lines.append('')
    for item in payload['results']:
        lines.append(f"### {item['id']} `{item['slice']}` `{item['category']}`")
        lines.append('')
        lines.append(f"- prompt: `{item['prompt']}`")
        lines.append(f"- status: `{item['status']}`")
        lines.append(f"- quality: `{item['quality_score']}`")
        lines.append(f"- keyword pass: `{item['keyword_pass']}`")
        lines.append(f"- latency: `{item['latency_ms']} ms`")
        lines.append(f"- mode: `{item['mode']}`")
        lines.append(f"- reason: `{item['reason']}`")
        lines.append(f"- llm stages: `{', '.join(item['llm_stages']) or 'none'}`")
        lines.append(f"- final polish: `{item['final_polish_applied']}` ({item['final_polish_reason'] or 'none'})")
        lines.append(f"- answer experience model: `{item['answer_experience_model'] or 'none'}`")
        lines.append(f"- answer: {item['message_text'] or item.get('error', '')}")
        lines.append('')
    return '\n'.join(lines) + '\n'


async def _run_all(
    *,
    base_url: str,
    dataset: list[dict[str, Any]],
    dataset_path: Path,
    model_label: str,
    timeout_seconds: float,
) -> dict[str, Any]:
    status = await _fetch_status(base_url=base_url)
    results: list[dict[str, Any]] = []
    previous_answer_by_thread: dict[str, str] = {}
    total = len(dataset)
    for index, entry in enumerate(dataset, start=1):
        thread_id = str(entry.get('thread_id') or entry.get('id') or 'single')
        row = await _run_turn(
            base_url=base_url,
            entry=entry,
            model_label=model_label,
            timeout_seconds=timeout_seconds,
            previous_answer=previous_answer_by_thread.get(thread_id, ''),
        )
        results.append(row)
        print(
            f"[{index}/{total}] {row['id']} status={row['status']} quality={row['quality_score']} "
            f"latency_ms={row['latency_ms']} reason={row['reason']}",
            flush=True,
        )
        if int(row.get('status') or 0) == 200 and str(row.get('message_text') or '').strip():
            previous_answer_by_thread[thread_id] = str(row.get('message_text') or '')
    by_slice: dict[str, list[dict[str, Any]]] = {}
    for item in results:
        by_slice.setdefault(str(item['slice']), []).append(item)
    payload = {
        'generated_at': datetime.now(UTC).isoformat(),
        'model_label': model_label,
        'base_url': base_url,
        'dataset': str(dataset_path),
        'timeout_seconds': timeout_seconds,
        'runtime_status': status,
        'summary': {
            'overall': _bucket(results),
            'by_slice': {slice_name: _bucket(rows) for slice_name, rows in by_slice.items()},
        },
        'results': results,
    }
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description='Evaluate one specialist runtime/model profile over a fixed A/B dataset.')
    parser.add_argument('--base-url', default=DEFAULT_BASE_URL)
    parser.add_argument('--dataset', type=Path, default=DEFAULT_DATASET)
    parser.add_argument('--output-dir', type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument('--model-label', required=True)
    parser.add_argument('--timeout-seconds', type=float, default=30.0)
    args = parser.parse_args()

    dataset = _load_dataset(args.dataset)
    asyncio.run(_wait_for_health(base_url=args.base_url))
    payload = asyncio.run(
        _run_all(
            base_url=args.base_url,
            dataset=dataset,
            dataset_path=args.dataset,
            model_label=args.model_label,
            timeout_seconds=args.timeout_seconds,
        )
    )
    args.output_dir.mkdir(parents=True, exist_ok=True)
    slug = str(args.model_label).strip().lower().replace(' ', '-')
    json_path = args.output_dir / f'specialist-model-ab-{slug}.json'
    md_path = args.output_dir / f'specialist-model-ab-{slug}.md'
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    md_path.write_text(_render_markdown(payload), encoding='utf-8')
    print(json_path)
    print(md_path)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
