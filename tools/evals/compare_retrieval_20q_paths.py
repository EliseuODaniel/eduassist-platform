#!/usr/bin/env python3
from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from time import perf_counter
from typing import Any

from dotenv import load_dotenv


REPO_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(REPO_ROOT / '.env', override=False)
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
AI_ORCHESTRATOR_SRC = REPO_ROOT / 'apps/ai-orchestrator/src'
if str(AI_ORCHESTRATOR_SRC) not in sys.path:
    sys.path.insert(0, str(AI_ORCHESTRATOR_SRC))

from ai_orchestrator.engine_selector import build_engine_bundle
from ai_orchestrator.models import ConversationChannel, MessageResponseRequest, UserContext
from tools.evals.compare_five_chatbot_paths import (
    STACKS,
    _SpecialistSourceClient,
    _build_settings,
    _normalize_local_service_url,
    _specialist_benchmark_mode,
)
from tools.evals.compare_orchestrator_stacks import (
    _contains_expected_keywords,
    _contains_forbidden_keywords,
    _detect_error_types,
    _detect_quality_signals,
    _extract_answer_text,
    _quality_score,
)


DEFAULT_DATASET = REPO_ROOT / 'tests/evals/datasets/retrieval_20q_probe_cases.json'
DEFAULT_REPORT = REPO_ROOT / 'docs/architecture/retrieval-20q-cross-path-report.md'
DEFAULT_JSON_REPORT = REPO_ROOT / 'docs/architecture/retrieval-20q-cross-path-report.json'


def _load_cases(path: Path) -> list[dict[str, Any]]:
    payload = json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(payload, list):
        raise SystemExit('retrieval_20q_dataset_must_be_a_list')
    normalized: list[dict[str, Any]] = []
    for index, item in enumerate(payload, start=1):
        if not isinstance(item, dict) or not isinstance(item.get('prompt'), str):
            raise SystemExit('each retrieval_20q case must be an object with prompt')
        normalized.append(
            {
                'id': str(item.get('id') or f'Q{200 + index}'),
                'prompt': str(item['prompt']),
                'slice': str(item.get('slice') or 'public'),
                'category': str(item.get('category') or 'uncategorized'),
                'retrieval_type': str(item.get('retrieval_type') or item.get('category') or 'uncategorized'),
                'expected_keywords': [str(keyword) for keyword in (item.get('expected_keywords') or []) if str(keyword).strip()],
                'forbidden_keywords': [str(keyword) for keyword in (item.get('forbidden_keywords') or []) if str(keyword).strip()],
                'thread_id': str(item.get('thread_id') or ''),
                'turn_index': int(item.get('turn_index') or 1),
                'note': str(item.get('note') or ''),
                'telegram_chat_id': item.get('telegram_chat_id'),
                'user': dict(item.get('user') or {}),
            }
        )
    return normalized


def _user_for_case(entry: dict[str, Any]) -> UserContext:
    explicit_user = entry.get('user')
    if isinstance(explicit_user, dict) and explicit_user:
        return UserContext.model_validate(explicit_user)
    return UserContext()


async def _run_turn(
    *,
    stack: str,
    entry: dict[str, Any],
    timeout_seconds: float,
    run_prefix: str,
    specialist_source_client: _SpecialistSourceClient | None = None,
) -> dict[str, Any]:
    if stack == 'specialist_supervisor' and _specialist_benchmark_mode() == 'source':
        started = perf_counter()
        try:
            client = specialist_source_client or _SpecialistSourceClient()
            request = MessageResponseRequest(
                message=str(entry['prompt']),
                conversation_id=f"{run_prefix}:{entry.get('thread_id') or 'single'}:{stack}",
                telegram_chat_id=entry.get('telegram_chat_id'),
                channel=ConversationChannel.telegram,
                user=_user_for_case(entry),
                allow_graph_rag=False,
                allow_handoff=False,
            )
            payload = await client.request(
                {
                    'request': request.model_dump(mode='json'),
                    'api_core_url': _normalize_local_service_url(os.getenv('API_CORE_URL', ''), kind='api_core'),
                    'orchestrator_url': _normalize_local_service_url(os.getenv('AI_ORCHESTRATOR_URL', ''), kind='ai_orchestrator'),
                    'internal_api_token': os.getenv('INTERNAL_API_TOKEN', 'dev-internal-token'),
                    'openai_api_key': os.getenv('OPENAI_API_KEY'),
                    'google_api_key': os.getenv('GOOGLE_API_KEY'),
                },
                timeout_seconds=timeout_seconds,
            )
            answer = payload.get('answer') if isinstance(payload, dict) and isinstance(payload.get('answer'), dict) else {}
            latency_ms = round((perf_counter() - started) * 1000, 1)
            return {
                'status': 200,
                'body': answer,
                'latency_ms': latency_ms,
                'mode': answer.get('mode') or 'unknown',
                'reason': answer.get('reason') or str((payload or {}).get('reason') or ''),
                'graph_path': list(answer.get('graph_path') or []),
            }
        except Exception as exc:
            latency_ms = round((perf_counter() - started) * 1000, 1)
            return {
                'status': 599,
                'body': {'error': f'{type(exc).__name__}: {exc}'},
                'latency_ms': latency_ms,
                'mode': 'error',
                'reason': f'{type(exc).__name__}: {exc}',
                'graph_path': [],
            }

    settings = _build_settings(stack=stack)
    request = MessageResponseRequest(
        message=str(entry['prompt']),
        conversation_id=f"{run_prefix}:{entry.get('thread_id') or 'single'}:{stack}",
        telegram_chat_id=entry.get('telegram_chat_id'),
        channel=ConversationChannel.telegram,
        user=_user_for_case(entry),
        allow_graph_rag=False,
        allow_handoff=False,
    )
    bundle = build_engine_bundle(settings, request=request)
    started = perf_counter()
    try:
        response = await asyncio.wait_for(
            bundle.primary.respond(request=request, settings=settings, engine_mode=bundle.mode),
            timeout=timeout_seconds,
        )
        latency_ms = round((perf_counter() - started) * 1000, 1)
        return {
            'status': 200,
            'body': response.model_dump(mode='json'),
            'latency_ms': latency_ms,
            'mode': response.mode.value,
            'reason': response.reason,
            'graph_path': list(response.graph_path),
        }
    except Exception as exc:
        latency_ms = round((perf_counter() - started) * 1000, 1)
        return {
            'status': 599,
            'body': {'error': f'{type(exc).__name__}: {exc}'},
            'latency_ms': latency_ms,
            'mode': 'error',
            'reason': f'{type(exc).__name__}: {exc}',
            'graph_path': [],
        }


def _summarize(results: list[dict[str, Any]], *, stacks: tuple[str, ...]) -> dict[str, Any]:
    summary: dict[str, Any] = {
        'by_stack': {},
        'by_slice': {},
        'by_category': {},
        'by_retrieval_type': {},
        'failures': [],
    }
    for stack in stacks:
        subset = [item for item in results if item['stack'] == stack]
        summary['by_stack'][stack] = {
            'count': len(subset),
            'ok': sum(1 for item in subset if item['status'] == 200),
            'keyword_pass': sum(1 for item in subset if item['keyword_pass']),
            'quality_avg': round(sum(item['quality_score'] for item in subset) / max(1, len(subset)), 1),
            'avg_latency_ms': round(sum(item['latency_ms'] for item in subset) / max(1, len(subset)), 1),
            'mode_counts': dict(Counter(item['mode'] for item in subset)),
            'retrieval_backend_counts': dict(Counter(item['retrieval_backend'] or 'none' for item in subset)),
            'evidence_strategy_counts': dict(Counter(item['evidence_strategy'] or 'none' for item in subset)),
            'error_type_counts': dict(Counter(error for item in subset for error in item['error_types'])),
        }
    for field in ('slice', 'category', 'retrieval_type'):
        target_key = f'by_{field}'
        values = sorted({str(item[field]) for item in results})
        for value in values:
            bucket: dict[str, Any] = {'count': 0}
            scoped_rows = [item for item in results if item[field] == value]
            bucket['count'] = len(scoped_rows)
            for stack in stacks:
                subset = [item for item in scoped_rows if item['stack'] == stack]
                bucket[stack] = {
                    'count': len(subset),
                    'keyword_pass': sum(1 for item in subset if item['keyword_pass']),
                    'quality_avg': round(sum(item['quality_score'] for item in subset) / max(1, len(subset)), 1),
                    'avg_latency_ms': round(sum(item['latency_ms'] for item in subset) / max(1, len(subset)), 1),
                }
            summary[target_key][value] = bucket
    summary['failures'] = [
        {
            'id': item['id'],
            'stack': item['stack'],
            'slice': item['slice'],
            'category': item['category'],
            'retrieval_type': item['retrieval_type'],
            'quality_score': item['quality_score'],
            'error_types': item['error_types'],
            'reason': item['reason'],
            'mode': item['mode'],
            'retrieval_backend': item['retrieval_backend'],
        }
        for item in results
        if item['status'] != 200 or item['quality_score'] < 100
    ]
    return summary


def _render_markdown(payload: dict[str, Any], *, stacks: tuple[str, ...]) -> str:
    lines = ['# Retrieval 20Q Cross-Path Report', '']
    lines.append(f"Date: {payload['generated_at']}")
    lines.append('')
    lines.append(f"Dataset: `{payload['dataset']}`")
    lines.append('')
    lines.append(f"Run prefix: `{payload['run_prefix']}`")
    lines.append('')
    lines.append('## Stack Summary')
    lines.append('')
    lines.append('| Stack | OK | Keyword pass | Quality | Avg latency |')
    lines.append('| --- | --- | --- | --- | --- |')
    for stack in stacks:
        bucket = payload['summary']['by_stack'][stack]
        lines.append(
            f"| `{stack}` | `{bucket['ok']}/{bucket['count']}` | `{bucket['keyword_pass']}/{bucket['count']}` | `{bucket['quality_avg']}` | `{bucket['avg_latency_ms']} ms` |"
        )
    lines.append('')
    lines.append('## By Retrieval Type')
    lines.append('')
    for retrieval_type, bucket in payload['summary']['by_retrieval_type'].items():
        lines.append(f"- `{retrieval_type}`")
        for stack in stacks:
            item = bucket.get(stack) or {}
            lines.append(
                f"  - `{stack}`: keyword pass {item.get('keyword_pass', 0)}/{item.get('count', 0)}, "
                f"quality {item.get('quality_avg', 0)}, latency {item.get('avg_latency_ms', 0)}ms"
            )
    lines.append('')
    lines.append('## Failures')
    lines.append('')
    for item in payload['summary']['failures']:
        lines.append(
            f"- `{item['id']}` `{item['stack']}` `{item['retrieval_type']}` quality `{item['quality_score']}` "
            f"mode `{item['mode']}` reason `{item['reason']}` errors `{', '.join(item['error_types']) or 'none'}`"
        )
    lines.append('')
    lines.append('## Prompt Results')
    lines.append('')
    grouped: dict[str, list[dict[str, Any]]] = {}
    for row in payload['results']:
        grouped.setdefault(str(row['id']), []).append(row)
    for case_id in sorted(grouped):
        rows = grouped[case_id]
        prompt = rows[0]['prompt']
        retrieval_type = rows[0]['retrieval_type']
        lines.append(f"### `{case_id}` {prompt}")
        lines.append('')
        lines.append(f"- Retrieval type: `{retrieval_type}`")
        lines.append(f"- Slice: `{rows[0]['slice']}`")
        for row in rows:
            lines.append(
                f"- `{row['stack']}`: status {row['status']}, latency {row['latency_ms']}ms, "
                f"quality `{row['quality_score']}`, reason `{row['reason']}`, "
                f"backend `{row['retrieval_backend']}`, strategy `{row['evidence_strategy']}`"
            )
            if row['error_types']:
                lines.append(f"  errors: {', '.join(row['error_types'])}")
            lines.append(f"  answer: {row['answer_text']}")
        lines.append('')
    return '\n'.join(lines)


async def _run_all(
    cases: list[dict[str, Any]],
    *,
    stacks: tuple[str, ...],
    timeout_seconds: float,
) -> dict[str, Any]:
    run_prefix = f"debug:retrieval20:{datetime.now(UTC).strftime('%Y%m%dT%H%M%SZ')}"
    results: list[dict[str, Any]] = []
    previous_answers: dict[str, dict[str, str]] = {stack: {} for stack in stacks}
    specialist_source_client = (
        _SpecialistSourceClient()
        if 'specialist_supervisor' in stacks and _specialist_benchmark_mode() == 'source'
        else None
    )
    try:
        for case in cases:
            for stack in stacks:
                raw = await _run_turn(
                    stack=stack,
                    entry=case,
                    timeout_seconds=timeout_seconds,
                    run_prefix=run_prefix,
                    specialist_source_client=specialist_source_client,
                )
                body = raw['body'] if isinstance(raw.get('body'), dict) else {}
                answer_text = _extract_answer_text(body)
                thread_key = str(case.get('thread_id') or '')
                previous_answer = previous_answers[stack].get(thread_key, '') if thread_key else ''
                expected_keywords = list(case.get('expected_keywords') or [])
                forbidden_keywords = list(case.get('forbidden_keywords') or [])
                error_types = _detect_error_types(
                    answer_text=answer_text,
                    expected_keywords=expected_keywords,
                    forbidden_keywords=forbidden_keywords,
                    prompt=str(case['prompt']),
                    previous_answer=previous_answer,
                    status=int(raw['status']),
                    turn_index=int(case.get('turn_index') or 1),
                    note=str(case.get('note') or ''),
                )
                quality_signals = _detect_quality_signals(
                    answer_text=answer_text,
                    expected_keywords=expected_keywords,
                    prompt=str(case['prompt']),
                    previous_answer=previous_answer,
                    turn_index=int(case.get('turn_index') or 1),
                    note=str(case.get('note') or ''),
                )
                quality_score = _quality_score(status=int(raw['status']), error_types=error_types)
                keyword_pass = _contains_expected_keywords(answer_text, expected_keywords) and not _contains_forbidden_keywords(
                    answer_text,
                    forbidden_keywords,
                )
                if thread_key and answer_text.strip():
                    previous_answers[stack][thread_key] = answer_text
                evidence_pack = body.get('evidence_pack') if isinstance(body, dict) else None
                results.append(
                    {
                        'id': str(case.get('id') or ''),
                        'stack': stack,
                        'slice': case['slice'],
                        'category': case['category'],
                        'retrieval_type': case['retrieval_type'],
                        'thread_id': thread_key,
                        'turn_index': int(case.get('turn_index') or 1),
                        'prompt': case['prompt'],
                        'status': int(raw['status']),
                        'latency_ms': float(raw['latency_ms']),
                        'mode': raw['mode'],
                        'reason': raw['reason'],
                        'graph_path': list(raw['graph_path']),
                        'retrieval_backend': body.get('retrieval_backend'),
                        'evidence_strategy': evidence_pack.get('strategy') if isinstance(evidence_pack, dict) else None,
                        'support_count': evidence_pack.get('support_count') if isinstance(evidence_pack, dict) else None,
                        'citation_count': len(body.get('citations') or []) if isinstance(body, dict) else 0,
                        'risk_flags': list(body.get('risk_flags') or []) if isinstance(body, dict) else [],
                        'keyword_pass': bool(keyword_pass),
                        'quality_score': int(quality_score),
                        'error_types': error_types,
                        'quality_signals': quality_signals,
                        'answer_text': answer_text,
                    }
                )
    finally:
        if specialist_source_client is not None:
            await specialist_source_client.close()

    return {
        'generated_at': datetime.now(UTC).isoformat(),
        'dataset': str(DEFAULT_DATASET),
        'run_prefix': run_prefix,
        'stacks': list(stacks),
        'summary': _summarize(results, stacks=stacks),
        'results': results,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description='Run the retrieval 20-question dataset across selected paths.')
    parser.add_argument('--dataset', type=Path, default=DEFAULT_DATASET)
    parser.add_argument('--report', type=Path, default=DEFAULT_REPORT)
    parser.add_argument('--json-report', type=Path, default=DEFAULT_JSON_REPORT)
    parser.add_argument('--timeout-seconds', type=float, default=90.0)
    parser.add_argument('--stacks', nargs='+', choices=STACKS, default=list(STACKS))
    args = parser.parse_args()

    cases = _load_cases(args.dataset)
    selected_stacks = tuple(dict.fromkeys(args.stacks))
    payload = asyncio.run(
        _run_all(
            cases,
            stacks=selected_stacks,
            timeout_seconds=max(1.0, float(args.timeout_seconds)),
        )
    )
    payload['dataset'] = str(args.dataset)
    payload['stacks'] = list(selected_stacks)
    args.json_report.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    args.report.write_text(_render_markdown(payload, stacks=selected_stacks) + '\n', encoding='utf-8')
    print(args.report)
    print(args.json_report)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
