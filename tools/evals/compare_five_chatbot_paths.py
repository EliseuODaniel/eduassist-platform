#!/usr/bin/env python3
from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
from datetime import UTC, datetime
from pathlib import Path
from time import perf_counter
from typing import Any
from urllib.parse import urlparse, urlunparse

from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(REPO_ROOT / '.env', override=False)
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
AI_ORCHESTRATOR_SRC = REPO_ROOT / 'apps/ai-orchestrator/src'
if str(AI_ORCHESTRATOR_SRC) not in sys.path:
    sys.path.insert(0, str(AI_ORCHESTRATOR_SRC))
OBSERVABILITY_SRC = REPO_ROOT / 'packages/observability/python/src'
if str(OBSERVABILITY_SRC) not in sys.path:
    sys.path.insert(0, str(OBSERVABILITY_SRC))
SPECIALIST_SUPERVISOR_SRC = REPO_ROOT / 'apps/ai-orchestrator-specialist/src'
if str(SPECIALIST_SUPERVISOR_SRC) not in sys.path:
    sys.path.insert(0, str(SPECIALIST_SUPERVISOR_SRC))
SPECIALIST_SOURCE_SERVER = REPO_ROOT / 'tools/evals/run_specialist_supervisor_source_server.py'

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

from ai_orchestrator.engine_selector import build_engine_bundle  # noqa: E402
from ai_orchestrator.main import Settings  # noqa: E402
from ai_orchestrator.models import (  # noqa: E402
    ConversationChannel,
    MessageResponseRequest,
    UserContext,
    UserRole,
)

DEFAULT_PROMPTS = REPO_ROOT / 'tests/evals/datasets/five_path_random_probe_cases.json'
DEFAULT_REPORT = REPO_ROOT / 'docs/architecture/five-path-chatbot-comparison-report.md'
DEFAULT_JSON_REPORT = REPO_ROOT / 'docs/architecture/five-path-chatbot-comparison-report.json'
STACKS = ('langgraph', 'python_functions', 'llamaindex', 'specialist_supervisor')


class _SpecialistSourceClient:
    def __init__(self) -> None:
        self._process: asyncio.subprocess.Process | None = None
        self._lock = asyncio.Lock()

    async def _start(self) -> None:
        if self._process is not None and self._process.returncode is None:
            return
        self._process = await asyncio.create_subprocess_exec(
            'uv',
            'run',
            '--project',
            str(REPO_ROOT / 'apps/ai-orchestrator-specialist'),
            'python',
            str(SPECIALIST_SOURCE_SERVER),
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
        )

    async def request(self, payload: dict[str, Any], *, timeout_seconds: float) -> dict[str, Any]:
        async with self._lock:
            await self._start()
            assert self._process is not None
            assert self._process.stdin is not None
            assert self._process.stdout is not None
            self._process.stdin.write((json.dumps(payload, ensure_ascii=False) + '\n').encode('utf-8'))
            await self._process.stdin.drain()
            raw = await asyncio.wait_for(self._process.stdout.readline(), timeout=timeout_seconds)
            if not raw:
                raise RuntimeError('specialist_source_runner_terminated')
            response = json.loads(raw.decode('utf-8'))
            if not bool(response.get('ok', False)):
                raise RuntimeError(str(response.get('error') or 'specialist_source_runner_error'))
            result = response.get('response')
            return result if isinstance(result, dict) else {}

    async def close(self) -> None:
        if self._process is None:
            return
        if self._process.stdin is not None and not self._process.stdin.is_closing():
            self._process.stdin.close()
        try:
            await asyncio.wait_for(self._process.wait(), timeout=2.0)
        except Exception:
            self._process.kill()
            await self._process.wait()
        finally:
            self._process = None


def _normalize_local_service_url(value: str, *, kind: str) -> str:
    normalized = str(value or '').strip()
    if not normalized:
        defaults = {
            'api_core': 'http://127.0.0.1:8001',
            'ai_orchestrator': 'http://127.0.0.1:8002',
            'specialist_pilot': 'http://127.0.0.1:8015',
        }
        return defaults[kind]
    replacements = {
        'http://api-core:8000': 'http://127.0.0.1:8001',
        'http://ai-orchestrator:8000': 'http://127.0.0.1:8002',
        'http://ai-orchestrator-specialist:8000': 'http://127.0.0.1:8015',
        'http://localhost:8000': {
            'specialist_pilot': 'http://127.0.0.1:8015',
        }.get(kind, normalized),
    }
    return replacements.get(normalized, normalized)


def _specialist_benchmark_mode() -> str:
    return str(os.getenv('SPECIALIST_SUPERVISOR_BENCHMARK_MODE', 'pilot') or 'pilot').strip().lower()


def _replace_url_host(value: str, *, replacements: dict[str, str]) -> str:
    normalized = str(value or '').strip()
    if not normalized:
        return normalized
    parsed = urlparse(normalized)
    host = (parsed.hostname or '').strip().lower()
    replacement_host = replacements.get(host)
    if replacement_host is None:
        return normalized
    netloc = replacement_host
    if parsed.port is not None:
        netloc = f'{replacement_host}:{parsed.port}'
    if parsed.username:
        auth = parsed.username
        if parsed.password:
            auth = f'{auth}:{parsed.password}'
        netloc = f'{auth}@{netloc}'
    return urlunparse(parsed._replace(netloc=netloc))


def _normalize_local_database_url(value: str) -> str:
    normalized = str(value or '').strip()
    if not normalized:
        return 'postgresql://eduassist:eduassist@127.0.0.1:5432/eduassist'
    return _replace_url_host(
        normalized,
        replacements={
            'postgres': '127.0.0.1',
            'localhost': '127.0.0.1',
        },
    )


def _normalize_local_qdrant_url(value: str) -> str:
    normalized = str(value or '').strip()
    if not normalized:
        return 'http://127.0.0.1:6333'
    return _replace_url_host(
        normalized,
        replacements={
            'qdrant': '127.0.0.1',
            'localhost': '127.0.0.1',
        },
    )


def _exception_reason(*, stack: str, exc: Exception) -> str:
    details = f'{type(exc).__name__}: {exc}'.lower()
    if 'connecttimeout' in details or 'connecterror' in details or 'allconnectionattemptsfailed' in details:
        if stack == 'specialist_supervisor':
            return f'{stack}_pilot_unavailable'
        return 'dependency_unavailable'
    if 'llm_unconfigured' in details:
        return 'runtime_unconfigured'
    return 'exception'


def _benchmark_context() -> dict[str, Any]:
    return {
        'specialist_supervisor_benchmark_mode': _specialist_benchmark_mode(),
        'api_core_url': _normalize_local_service_url(os.getenv('API_CORE_URL', ''), kind='api_core'),
        'ai_orchestrator_url': _normalize_local_service_url(os.getenv('AI_ORCHESTRATOR_URL', ''), kind='ai_orchestrator'),
        'specialist_supervisor_pilot_url': _normalize_local_service_url(
            os.getenv('SPECIALIST_SUPERVISOR_PILOT_URL', ''),
            kind='specialist_pilot',
        ),
        'database_url': _normalize_local_database_url(
            os.getenv('BENCHMARK_DATABASE_URL')
            or os.getenv('DATABASE_URL_LOCAL')
            or os.getenv('DATABASE_URL')
            or ''
        ),
        'qdrant_url': _normalize_local_qdrant_url(os.getenv('BENCHMARK_QDRANT_URL') or os.getenv('QDRANT_URL') or ''),
        'env_loaded': True,
    }


def _load_prompts(path: str) -> list[dict[str, Any]]:
    payload = json.loads(Path(path).read_text(encoding='utf-8'))
    if isinstance(payload, dict) and isinstance(payload.get('threads'), list):
        return _expand_entries(payload['threads'])
    return _expand_entries(_normalize_prompt_entries(payload))


def _build_settings(*, stack: str) -> Settings:
    fallback = 'langgraph' if stack != 'langgraph' else 'python_functions'
    return Settings(
        orchestrator_engine=fallback,
        feature_flag_primary_orchestration_stack=stack,
        strict_framework_isolation_enabled=True,
        orchestrator_experiment_enabled=False,
        langgraph_checkpointer_enabled=False,
        api_core_url=_normalize_local_service_url(os.getenv('API_CORE_URL', ''), kind='api_core'),
        qdrant_url=_normalize_local_qdrant_url(os.getenv('BENCHMARK_QDRANT_URL') or os.getenv('QDRANT_URL') or ''),
        database_url=_normalize_local_database_url(
            os.getenv('BENCHMARK_DATABASE_URL')
            or os.getenv('DATABASE_URL_LOCAL')
            or os.getenv('DATABASE_URL')
            or ''
        ),
        specialist_supervisor_pilot_url=_normalize_local_service_url(
            os.getenv('SPECIALIST_SUPERVISOR_PILOT_URL', ''),
            kind='specialist_pilot',
        ),
    )


def _user_for_slice(entry: dict[str, Any]) -> UserContext:
    explicit_user = entry.get('user')
    if isinstance(explicit_user, dict) and explicit_user:
        return UserContext.model_validate(explicit_user)
    slice_name = str(entry.get('slice') or 'public')
    chat_id = entry.get('telegram_chat_id')
    if slice_name in {'protected', 'support', 'workflow'} or str(chat_id) == '1649845499':
        return UserContext(
            role=UserRole.guardian,
            authenticated=True,
            linked_student_ids=['stu-lucas', 'stu-ana'],
            scopes=['students:read', 'administrative:read', 'financial:read', 'academic:read'],
        )
    return UserContext(role=UserRole.anonymous, authenticated=False)


async def _run_turn(
    *,
    stack: str,
    entry: dict[str, Any],
    timeout_seconds: float,
    specialist_source_client: _SpecialistSourceClient | None = None,
) -> dict[str, Any]:
    if stack == 'specialist_supervisor' and _specialist_benchmark_mode() == 'source':
        started = perf_counter()
        try:
            client = specialist_source_client or _SpecialistSourceClient()
            payload = await client.request(
                {
                    'request': {
                        'message': str(entry['prompt']),
                        'conversation_id': f"{entry.get('run_prefix') or 'debug:five-path'}:{entry.get('thread_id') or 'single'}:{stack}",
                        'telegram_chat_id': entry.get('telegram_chat_id'),
                        'channel': 'telegram',
                        'user': _user_for_slice(entry).model_dump(mode='json'),
                        'allow_graph_rag': True,
                        'allow_handoff': True,
                    },
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
                'reason': _exception_reason(stack=stack, exc=exc),
                'graph_path': [],
            }

    settings = _build_settings(stack=stack)
    run_prefix = str(entry.get('run_prefix') or 'debug:five-path')
    conversation_id = f"{run_prefix}:{entry.get('thread_id') or 'single'}:{stack}"
    request = MessageResponseRequest(
        message=str(entry['prompt']),
        conversation_id=conversation_id,
        telegram_chat_id=entry.get('telegram_chat_id'),
        channel=ConversationChannel.telegram,
        user=_user_for_slice(entry),
        allow_graph_rag=True,
        allow_handoff=True,
    )
    bundle = build_engine_bundle(settings, request=request)
    started = perf_counter()
    try:
        response = await asyncio.wait_for(
            bundle.primary.respond(request=request, settings=settings, engine_mode=bundle.mode),
            timeout=timeout_seconds,
        )
        latency_ms = round((perf_counter() - started) * 1000, 1)
        body = response.model_dump(mode='json')
        return {
            'status': 200,
            'body': body,
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
            'reason': _exception_reason(stack=stack, exc=exc),
            'graph_path': [],
        }


def _render_markdown(payload: dict[str, Any], *, stacks: tuple[str, ...]) -> str:
    lines = ['# Five-Path Chatbot Comparison Report', '']
    lines.append(f"Date: {payload['generated_at']}")
    lines.append('')
    lines.append(f"Dataset: `{payload['dataset']}`")
    lines.append('')
    lines.append(f"Run prefix: `{payload.get('run_prefix', '')}`")
    lines.append('')
    lines.append(f"Stack execution mode: `{payload.get('stack_execution_mode', 'sequential')}`")
    lines.append('')
    benchmark_context = payload.get('benchmark_context') if isinstance(payload.get('benchmark_context'), dict) else {}
    if benchmark_context:
        lines.append('## Benchmark Context')
        lines.append('')
        lines.append(f"- specialist benchmark mode: `{benchmark_context.get('specialist_supervisor_benchmark_mode', 'unknown')}`")
        lines.append(f"- api-core: `{benchmark_context.get('api_core_url', '')}`")
        lines.append(f"- ai-orchestrator: `{benchmark_context.get('ai_orchestrator_url', '')}`")
        lines.append(f"- specialist pilot: `{benchmark_context.get('specialist_supervisor_pilot_url', '')}`")
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
    lines.append('## By Slice')
    lines.append('')
    for slice_name, bucket in payload['summary']['by_slice'].items():
        lines.append(f"- `{slice_name}`")
        for stack in stacks:
            stack_bucket = bucket.get(stack) or {}
            lines.append(
                f"  - `{stack}`: ok {stack_bucket.get('ok', 0)}/{bucket['count']}, "
                f"keyword pass {stack_bucket.get('keyword_pass', 0)}/{bucket['count']}, "
                f"quality {stack_bucket.get('quality_avg', 0)}, latency {stack_bucket.get('avg_latency_ms', 0)}ms"
            )
    lines.append('')
    lines.append('## Error Types')
    lines.append('')
    for stack in stacks:
        bucket = payload['summary']['error_types'][stack]
        items = ', '.join(f'{name}={count}' for name, count in sorted(bucket.items()))
        lines.append(f"- `{stack}`: {items or 'nenhum'}")
    lines.append('')
    lines.append('## Prompt Results')
    lines.append('')
    for result in payload['results']:
        lines.append(f"### {result['prompt']}")
        lines.append('')
        lines.append(f"- Slice: `{result['slice']}`")
        if result.get('thread_id'):
            lines.append(f"- Thread: `{result['thread_id']}` turn `{result['turn_index']}`")
        for stack in stacks:
            item = result[stack]
            lines.append(
                f"- `{stack}`: status {item['status']}, latency {item['latency_ms']}ms, keyword pass `{item['keyword_pass']}`, quality `{item['quality_score']}`, reason `{item['reason']}`"
            )
            if item.get('error_types'):
                lines.append(f"  errors: {', '.join(item['error_types'])}")
            lines.append(f"  answer: {item['answer_text']}")
        lines.append('')
    return '\n'.join(lines).replace('\n  - ', '\n  - ')


async def _run_all(
    entries: list[dict[str, Any]],
    *,
    timeout_seconds: float,
    stacks: tuple[str, ...],
    parallel_stacks: bool,
) -> dict[str, Any]:
    run_prefix = f"debug:five-path:{datetime.now(UTC).strftime('%Y%m%dT%H%M%SZ')}"
    previous_answers: dict[str, dict[str, str]] = {stack: {} for stack in stacks}
    results: list[dict[str, Any]] = []
    specialist_source_client = (
        _SpecialistSourceClient()
        if 'specialist_supervisor' in stacks and _specialist_benchmark_mode() == 'source'
        else None
    )

    try:
        for entry in entries:
            entry_with_run_prefix = {**entry, 'run_prefix': run_prefix}
            row: dict[str, Any] = {
                'prompt': entry['prompt'],
                'slice': entry['slice'],
                'category': entry.get('category') or 'uncategorized',
                'thread_id': entry.get('thread_id') or '',
                'turn_index': entry.get('turn_index') or 1,
                'note': entry.get('note') or '',
                'run_prefix': run_prefix,
            }
            if parallel_stacks:
                raw_by_stack = {
                    stack: result
                    for stack, result in zip(
                        stacks,
                        await asyncio.gather(
                            *[
                                _run_turn(
                                    stack=stack,
                                    entry=entry_with_run_prefix,
                                    timeout_seconds=timeout_seconds,
                                    specialist_source_client=specialist_source_client,
                                )
                                for stack in stacks
                            ]
                        ),
                        strict=True,
                    )
                }
            else:
                raw_by_stack = {}
                for stack in stacks:
                    raw_by_stack[stack] = await _run_turn(
                        stack=stack,
                        entry=entry_with_run_prefix,
                        timeout_seconds=timeout_seconds,
                        specialist_source_client=specialist_source_client,
                    )
            for stack in stacks:
                raw = raw_by_stack[stack]
                answer_text = _extract_answer_text(raw['body'])
                thread_key = str(entry.get('thread_id') or '')
                previous_answer = previous_answers[stack].get(thread_key, '') if thread_key else ''
                expected_keywords = list(entry.get('expected_keywords') or [])
                forbidden_keywords = list(entry.get('forbidden_keywords') or [])
                error_types = _detect_error_types(
                    answer_text=answer_text,
                    expected_keywords=expected_keywords,
                    forbidden_keywords=forbidden_keywords,
                    prompt=str(entry['prompt']),
                    previous_answer=previous_answer,
                    status=int(raw['status']),
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
                quality_score = _quality_score(status=int(raw['status']), error_types=error_types)
                keyword_pass = _contains_expected_keywords(answer_text, expected_keywords) and not _contains_forbidden_keywords(
                    answer_text,
                    forbidden_keywords,
                )
                row[stack] = {
                    'status': int(raw['status']),
                    'latency_ms': float(raw['latency_ms']),
                    'mode': raw['mode'],
                    'reason': raw['reason'],
                    'graph_path': raw['graph_path'],
                    'answer_text': answer_text,
                    'keyword_pass': keyword_pass,
                    'quality_score': quality_score,
                    'error_types': error_types,
                    'quality_signals': quality_signals,
                }
                if thread_key:
                    previous_answers[stack][thread_key] = answer_text
            results.append(row)
    finally:
        if specialist_source_client is not None:
            await specialist_source_client.close()

    summary_by_stack: dict[str, Any] = {}
    summary_by_slice: dict[str, Any] = {}
    summary_error_types: dict[str, dict[str, int]] = {stack: {} for stack in stacks}
    for stack in stacks:
        subset = [row[stack] for row in results]
        summary_by_stack[stack] = {
            'count': len(subset),
            'ok': sum(1 for item in subset if item['status'] == 200),
            'keyword_pass': sum(1 for item in subset if item['keyword_pass']),
            'quality_avg': round(sum(item['quality_score'] for item in subset) / max(1, len(subset)), 1),
            'avg_latency_ms': round(sum(item['latency_ms'] for item in subset) / max(1, len(subset)), 1),
        }
        for item in subset:
            for error in item['error_types']:
                summary_error_types[stack][error] = summary_error_types[stack].get(error, 0) + 1
    slices = sorted({str(row['slice']) for row in results})
    for slice_name in slices:
        rows = [row for row in results if row['slice'] == slice_name]
        summary_by_slice[slice_name] = {'count': len(rows)}
        for stack in stacks:
            subset = [row[stack] for row in rows]
            summary_by_slice[slice_name][stack] = {
                'ok': sum(1 for item in subset if item['status'] == 200),
                'keyword_pass': sum(1 for item in subset if item['keyword_pass']),
                'quality_avg': round(sum(item['quality_score'] for item in subset) / max(1, len(subset)), 1),
                'avg_latency_ms': round(sum(item['latency_ms'] for item in subset) / max(1, len(subset)), 1),
            }

    return {
        'generated_at': datetime.now(UTC).isoformat(),
        'dataset': str(DEFAULT_PROMPTS),
        'run_prefix': run_prefix,
        'benchmark_context': _benchmark_context(),
        'stack_execution_mode': 'parallel' if parallel_stacks else 'sequential',
        'summary': {
            'by_stack': summary_by_stack,
            'by_slice': summary_by_slice,
            'error_types': summary_error_types,
        },
        'results': results,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--dataset', type=Path, default=DEFAULT_PROMPTS)
    parser.add_argument('--report', type=Path, default=DEFAULT_REPORT)
    parser.add_argument('--json-report', type=Path, default=DEFAULT_JSON_REPORT)
    parser.add_argument('--timeout-seconds', type=float, default=45.0)
    parser.add_argument(
        '--parallel-stacks',
        action='store_true',
        help='Executa todos os caminhos em paralelo por prompt. O padrao sequencial evita contencao e produz benchmark mais justo.',
    )
    parser.add_argument(
        '--stacks',
        nargs='+',
        choices=STACKS,
        default=list(STACKS),
        help='Subconjunto de stacks a comparar.',
    )
    args = parser.parse_args()

    entries = _load_prompts(str(args.dataset))
    selected_stacks = tuple(dict.fromkeys(args.stacks))
    payload = asyncio.run(
        _run_all(
            entries,
            timeout_seconds=max(1.0, float(args.timeout_seconds)),
            stacks=selected_stacks,
            parallel_stacks=bool(args.parallel_stacks),
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
