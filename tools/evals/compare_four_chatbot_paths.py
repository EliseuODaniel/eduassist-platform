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

from ai_orchestrator.models import (  # noqa: E402
    ConversationChannel,
    MessageResponseRequest,
    UserContext,
    UserRole,
)

DEFAULT_PROMPTS = REPO_ROOT / 'artifacts/two_stack_random_strict_llm_live_20260327_v1_dataset.json'
DEFAULT_REPORT = REPO_ROOT / 'docs/architecture/four-path-chatbot-comparison-report.md'
DEFAULT_JSON_REPORT = REPO_ROOT / 'docs/architecture/four-path-chatbot-comparison-report.json'
STACKS = ('langgraph', 'python_functions', 'llamaindex', 'specialist_supervisor')
STACK_URLS = {
    'langgraph': os.getenv('AI_ORCHESTRATOR_LANGGRAPH_BENCH_URL', 'http://127.0.0.1:8006'),
    'python_functions': os.getenv('AI_ORCHESTRATOR_PYTHON_FUNCTIONS_BENCH_URL', 'http://127.0.0.1:8007'),
    'llamaindex': os.getenv('AI_ORCHESTRATOR_LLAMAINDEX_BENCH_URL', 'http://127.0.0.1:8008'),
    'specialist_supervisor': os.getenv('AI_ORCHESTRATOR_SPECIALIST_BENCH_URL', 'http://127.0.0.1:8005'),
}
INTERNAL_API_TOKEN = os.getenv('INTERNAL_API_TOKEN', 'dev-internal-token')


def _load_four_path_prompts(path: str) -> list[dict[str, Any]]:
    payload = json.loads(Path(path).read_text(encoding='utf-8'))
    if isinstance(payload, dict) and isinstance(payload.get('threads'), list):
        return _expand_entries(payload['threads'])
    return _expand_entries(_normalize_prompt_entries(payload))


def _user_for_slice(entry: dict[str, Any]) -> UserContext:
    explicit_user = entry.get('user')
    if isinstance(explicit_user, dict) and explicit_user:
        return UserContext.model_validate(explicit_user)
    slice_name = str(entry.get('slice') or 'public')
    category = str(entry.get('category') or '').strip()
    chat_id = entry.get('telegram_chat_id')
    if category in {'restricted_doc_positive', 'restricted_doc_negative'}:
        return UserContext(
            role=UserRole.staff,
            authenticated=True,
            scopes=['documents:restricted:read', 'documents:private:read'],
        )
    if category == 'restricted_doc_denied':
        return UserContext(
            role=UserRole.guardian,
            authenticated=True,
            linked_student_ids=['stu-lucas', 'stu-ana'],
            scopes=['students:read', 'administrative:read', 'financial:read', 'academic:read'],
        )
    if slice_name == 'protected' or str(chat_id) == '1649845499':
        return UserContext(
            role=UserRole.guardian,
            authenticated=True,
            linked_student_ids=['stu-lucas', 'stu-ana'],
            scopes=['students:read', 'administrative:read', 'financial:read', 'academic:read'],
        )
    return UserContext(role=UserRole.anonymous, authenticated=False)


async def _run_turn(*, stack: str, entry: dict[str, Any], llm_forced: bool = False) -> dict[str, Any]:
    run_prefix = str(entry.get('run_prefix') or 'debug:four-path')
    conversation_id = f"{run_prefix}:{entry.get('thread_id') or 'single'}:{stack}"
    request = MessageResponseRequest(
        message=str(entry['prompt']),
        conversation_id=conversation_id,
        telegram_chat_id=entry.get('telegram_chat_id'),
        channel=ConversationChannel.telegram,
        user=_user_for_slice(entry),
        allow_graph_rag=True,
        allow_handoff=True,
        debug_options={'llm_forced_mode': llm_forced},
    )
    target_url = str(STACK_URLS[stack]).rstrip('/')
    started = perf_counter()
    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(25.0, connect=5.0)) as client:
            http_response = await asyncio.wait_for(
                client.post(
                    f'{target_url}/v1/messages/respond',
                    headers={'X-Internal-Api-Token': INTERNAL_API_TOKEN},
                    json=request.model_dump(mode='json'),
                ),
                timeout=26.0,
            )
        http_response.raise_for_status()
        latency_ms = round((perf_counter() - started) * 1000, 1)
        body = http_response.json()
        mode = body.get('mode') or 'error'
        reason = body.get('reason') or ''
        graph_path = list(body.get('graph_path') or [])
        return {
            'status': 200,
            'body': body,
            'latency_ms': latency_ms,
            'mode': mode,
            'reason': reason,
            'graph_path': graph_path,
            'used_llm': bool(body.get('used_llm', False)),
            'llm_stages': list(body.get('llm_stages') or []),
            'final_polish_applied': bool(body.get('final_polish_applied', False)),
            'final_polish_mode': body.get('final_polish_mode'),
            'final_polish_reason': body.get('final_polish_reason'),
            'answer_experience_applied': bool(body.get('answer_experience_applied', False)),
            'answer_experience_reason': body.get('answer_experience_reason'),
            'answer_experience_provider': body.get('answer_experience_provider'),
            'answer_experience_model': body.get('answer_experience_model'),
            'candidate_chosen': body.get('candidate_chosen'),
            'candidate_reason': body.get('candidate_reason'),
            'retrieval_probe_topic': body.get('retrieval_probe_topic'),
            'response_cache_hit': bool(body.get('response_cache_hit', False)),
            'response_cache_kind': body.get('response_cache_kind'),
        }
    except Exception as exc:
        latency_ms = round((perf_counter() - started) * 1000, 1)
        return {
            'status': 599,
            'body': {'error': f'{type(exc).__name__}: {exc}'},
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
            'candidate_chosen': None,
            'candidate_reason': None,
            'retrieval_probe_topic': None,
            'response_cache_hit': False,
            'response_cache_kind': None,
        }


def _render_markdown(payload: dict[str, Any]) -> str:
    lines = ['# Four-Path Chatbot Comparison Report', '']
    lines.append(f"Date: {payload['generated_at']}")
    lines.append('')
    lines.append(f"Dataset: `{payload['dataset']}`")
    lines.append('')
    lines.append(f"LLM forced: `{payload.get('llm_forced', False)}`")
    lines.append('')
    lines.append(f"Run prefix: `{payload.get('run_prefix', '')}`")
    lines.append('')
    lines.append('## Stack Summary')
    lines.append('')
    lines.append('| Stack | OK | Keyword pass | Quality | Avg latency | Final polish |')
    lines.append('| --- | --- | --- | --- | --- | --- |')
    for stack, bucket in payload['summary']['by_stack'].items():
        lines.append(
            f"| `{stack}` | `{bucket['ok']}/{bucket['count']}` | `{bucket['keyword_pass']}/{bucket['count']}` | `{bucket['quality_avg']}` | `{bucket['avg_latency_ms']} ms` | `{bucket['final_polish_applied']}/{bucket['count']}` |"
        )
    lines.append('')
    lines.append('## By Slice')
    lines.append('')
    for slice_name, bucket in payload['summary']['by_slice'].items():
        lines.append(f"- `{slice_name}`")
        for stack in STACKS:
            stack_bucket = bucket.get(stack) or {}
            lines.append(
                f"  - `{stack}`: ok {stack_bucket.get('ok', 0)}/{bucket['count']}, "
                f"keyword pass {stack_bucket.get('keyword_pass', 0)}/{bucket['count']}, "
                f"quality {stack_bucket.get('quality_avg', 0)}, latency {stack_bucket.get('avg_latency_ms', 0)}ms, "
                f"final polish {stack_bucket.get('final_polish_applied', 0)}/{bucket['count']}"
            )
    lines.append('')
    lines.append('## Error Types')
    lines.append('')
    for stack, bucket in payload['summary']['error_types'].items():
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
        for stack in STACKS:
            item = result[stack]
            lines.append(
                f"- `{stack}`: status {item['status']}, latency {item['latency_ms']}ms, keyword pass `{item['keyword_pass']}`, quality `{item['quality_score']}`, used_llm `{item['used_llm']}`, llm_stages `{', '.join(item['llm_stages']) or 'none'}`, final_polish_applied `{item['final_polish_applied']}`, final_polish_mode `{item['final_polish_mode'] or 'none'}`, final_polish_reason `{item['final_polish_reason'] or 'none'}`, answer_experience_applied `{item.get('answer_experience_applied', False)}`, answer_experience_reason `{item.get('answer_experience_reason') or 'none'}`, answer_experience_provider `{item.get('answer_experience_provider') or 'none'}`, answer_experience_model `{item.get('answer_experience_model') or 'none'}`, candidate `{item.get('candidate_chosen') or 'none'}`, candidate_reason `{item.get('candidate_reason') or 'none'}`, probe_topic `{item.get('retrieval_probe_topic') or 'none'}`, cache_hit `{item.get('response_cache_hit', False)}`, cache_kind `{item.get('response_cache_kind') or 'none'}`, reason `{item['reason']}`"
            )
            if item.get('error_types'):
                lines.append(f"  errors: {', '.join(item['error_types'])}")
            lines.append(f"  answer: {item['answer_text']}")
        lines.append('')
    return '\n'.join(lines).replace('\n  - ', '\n  - ')


async def _run_all(entries: list[dict[str, Any]], *, llm_forced: bool = False) -> dict[str, Any]:
    run_kind = 'llm-forced' if llm_forced else 'normal'
    run_prefix = f"debug:four-path:{run_kind}:{datetime.now(UTC).strftime('%Y%m%dT%H%M%SZ')}"
    previous_answers: dict[str, dict[str, str]] = {stack: {} for stack in STACKS}
    results: list[dict[str, Any]] = []

    for entry in entries:
        entry_with_run_prefix = {**entry, 'run_prefix': run_prefix}
        row: dict[str, Any] = {
            'id': entry.get('id') or '',
            'prompt': entry['prompt'],
            'slice': entry['slice'],
            'category': entry.get('category') or 'uncategorized',
            'thread_id': entry.get('thread_id') or '',
            'turn_index': entry.get('turn_index') or 1,
            'note': entry.get('note') or '',
            'run_prefix': run_prefix,
        }
        for stack in STACKS:
            raw = await _run_turn(stack=stack, entry=entry_with_run_prefix, llm_forced=llm_forced)
            answer_text = _extract_answer_text(raw['body'])
            thread_key = str(entry.get('thread_id') or '')
            previous_answer = previous_answers[stack].get(thread_key, '') if thread_key else ''
            expected_keywords = list(entry.get('expected_keywords') or [])
            forbidden_keywords = list(entry.get('forbidden_keywords') or [])
            expected_sections = list(entry.get('expected_sections') or [])
            rubric_tags = list(entry.get('rubric_tags') or [])
            error_types = _detect_error_types(
                answer_text=answer_text,
                expected_keywords=expected_keywords,
                forbidden_keywords=forbidden_keywords,
                expected_sections=expected_sections,
                rubric_tags=rubric_tags,
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
                'used_llm': bool(raw.get('used_llm', False)),
                'llm_stages': [str(item).strip() for item in (raw.get('llm_stages') or []) if str(item).strip()],
                'final_polish_applied': bool(raw.get('final_polish_applied', False)),
                'final_polish_mode': str(raw.get('final_polish_mode') or ''),
                'final_polish_reason': str(raw.get('final_polish_reason') or ''),
                'answer_experience_applied': bool(raw.get('answer_experience_applied', False)),
                'answer_experience_reason': str(raw.get('answer_experience_reason') or ''),
                'answer_experience_provider': str(raw.get('answer_experience_provider') or ''),
                'answer_experience_model': str(raw.get('answer_experience_model') or ''),
                'candidate_chosen': str(raw.get('candidate_chosen') or ''),
                'candidate_reason': str(raw.get('candidate_reason') or ''),
                'retrieval_probe_topic': str(raw.get('retrieval_probe_topic') or ''),
                'response_cache_hit': bool(raw.get('response_cache_hit', False)),
                'response_cache_kind': str(raw.get('response_cache_kind') or ''),
                'answer_text': answer_text,
                'keyword_pass': keyword_pass,
                'quality_score': quality_score,
                'error_types': error_types,
                'quality_signals': quality_signals,
            }
            if thread_key:
                previous_answers[stack][thread_key] = answer_text
        results.append(row)

    summary_by_stack: dict[str, Any] = {}
    summary_by_slice: dict[str, Any] = {}
    summary_error_types: dict[str, dict[str, int]] = {stack: {} for stack in STACKS}
    for stack in STACKS:
        subset = [row[stack] for row in results]
        summary_by_stack[stack] = {
            'count': len(subset),
            'ok': sum(1 for item in subset if item['status'] == 200),
            'keyword_pass': sum(1 for item in subset if item['keyword_pass']),
            'quality_avg': round(sum(item['quality_score'] for item in subset) / max(1, len(subset)), 1),
            'avg_latency_ms': round(sum(item['latency_ms'] for item in subset) / max(1, len(subset)), 1),
            'final_polish_applied': sum(1 for item in subset if item.get('final_polish_applied')),
        }
        for item in subset:
            for error in item['error_types']:
                summary_error_types[stack][error] = summary_error_types[stack].get(error, 0) + 1
    slices = sorted({str(row['slice']) for row in results})
    for slice_name in slices:
        rows = [row for row in results if row['slice'] == slice_name]
        summary_by_slice[slice_name] = {'count': len(rows)}
        for stack in STACKS:
            subset = [row[stack] for row in rows]
            summary_by_slice[slice_name][stack] = {
                'ok': sum(1 for item in subset if item['status'] == 200),
                'keyword_pass': sum(1 for item in subset if item['keyword_pass']),
                'quality_avg': round(sum(item['quality_score'] for item in subset) / max(1, len(subset)), 1),
                'avg_latency_ms': round(sum(item['latency_ms'] for item in subset) / max(1, len(subset)), 1),
                'final_polish_applied': sum(1 for item in subset if item.get('final_polish_applied')),
            }
    return {
        'generated_at': datetime.now(UTC).isoformat(),
        'llm_forced': bool(llm_forced),
        'run_prefix': run_prefix,
        'summary': {
            'by_stack': summary_by_stack,
            'by_slice': summary_by_slice,
            'error_types': summary_error_types,
        },
        'results': results,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--prompt-file', default=str(DEFAULT_PROMPTS))
    parser.add_argument('--report', default=str(DEFAULT_REPORT))
    parser.add_argument('--json-report', default=str(DEFAULT_JSON_REPORT))
    parser.add_argument('--llm-forced', action='store_true')
    args = parser.parse_args()

    entries = _load_four_path_prompts(args.prompt_file)
    payload = asyncio.run(_run_all(entries, llm_forced=bool(args.llm_forced)))
    payload['dataset'] = str(Path(args.prompt_file).resolve())

    report_path = Path(args.report)
    json_report_path = Path(args.json_report)
    report_path.write_text(_render_markdown(payload) + '\n', encoding='utf-8')
    json_report_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(report_path)
    print(json_report_path)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
