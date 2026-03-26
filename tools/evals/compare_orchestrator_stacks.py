#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from time import perf_counter
from typing import Any
from urllib.error import HTTPError
from urllib.request import Request, urlopen


DEFAULT_PROMPTS = [
    {'prompt': 'qual o horario da biblioteca?', 'slice': 'public'},
    {'prompt': 'quando comeca a matricula?', 'slice': 'public'},
    {'prompt': 'qual o telefone e o fax?', 'slice': 'public'},
    {'prompt': 'qual instagram do colegio?', 'slice': 'public'},
    {'prompt': 'quais meus filhos?', 'slice': 'protected'},
    {'prompt': 'estou logado como?', 'slice': 'protected'},
    {'prompt': 'qual situacao de documentacao do Lucas?', 'slice': 'protected'},
    {'prompt': 'qual proximo pagamento do Lucas?', 'slice': 'protected'},
]

DEFAULT_PROMPT_FILE = 'tests/evals/datasets/two_stack_shadow_cases.json'


def _post_json(url: str, headers: dict[str, str], payload: dict[str, Any]) -> tuple[int, dict[str, Any] | str, float]:
    encoded = json.dumps(payload).encode('utf-8')
    request = Request(url, data=encoded, headers=headers, method='POST')
    started = perf_counter()
    try:
        with urlopen(request, timeout=90) as response:
            body = response.read().decode('utf-8')
            latency_ms = (perf_counter() - started) * 1000
            return response.status, json.loads(body), latency_ms
    except HTTPError as exc:
        body = exc.read().decode('utf-8')
        latency_ms = (perf_counter() - started) * 1000
        try:
            return exc.code, json.loads(body), latency_ms
        except json.JSONDecodeError:
            return exc.code, body, latency_ms


def _infer_slice(prompt: str) -> str:
    lowered = prompt.lower()
    protected_terms = (
        'nota', 'notas', 'falta', 'faltas', 'frequencia', 'prova', 'provas',
        'avaliacao', 'avaliacoes', 'financeiro', 'boleto', 'pagamento',
        'mensalidade', 'documentacao', 'documentos', 'meus filhos',
        'meu filho', 'minha filha', 'estou logado', 'meu acesso', 'lucas', 'ana',
    )
    return 'protected' if any(term in lowered for term in protected_terms) else 'public'


def _normalize_prompt_entries(payload: Any) -> list[dict[str, Any]]:
    if not isinstance(payload, list):
        raise SystemExit('Prompt file must be a JSON list.')
    entries: list[dict[str, Any]] = []
    for item in payload:
        if isinstance(item, str):
            entries.append({'prompt': item, 'slice': _infer_slice(item), 'category': 'uncategorized', 'expected_keywords': []})
            continue
        if isinstance(item, dict) and isinstance(item.get('prompt'), str):
            prompt = item['prompt']
            slice_name = str(item.get('slice') or _infer_slice(prompt))
            category = str(item.get('category') or 'uncategorized')
            expected_keywords = [str(keyword) for keyword in (item.get('expected_keywords') or []) if str(keyword).strip()]
            entries.append({'prompt': prompt, 'slice': slice_name, 'category': category, 'expected_keywords': expected_keywords})
            continue
        raise SystemExit('Each prompt entry must be a string or an object with a prompt field.')
    return entries


def _load_prompts(path: str | None) -> list[dict[str, Any]]:
    if not path:
        default_path = Path(DEFAULT_PROMPT_FILE)
        if default_path.exists():
            payload = json.loads(default_path.read_text())
            return _normalize_prompt_entries(payload)
        return _normalize_prompt_entries(DEFAULT_PROMPTS)
    payload = json.loads(Path(path).read_text())
    return _normalize_prompt_entries(payload)


def _extract_answer_text(body: dict[str, Any] | str) -> str:
    if isinstance(body, str):
        return body
    if not isinstance(body, dict):
        return ''
    if isinstance(body.get('message_text'), str):
        return str(body['message_text'])
    metadata = body.get('metadata')
    if isinstance(metadata, dict):
        answer = metadata.get('answer')
        if isinstance(answer, dict) and isinstance(answer.get('answer_text'), str):
            return str(answer['answer_text'])
    return ''


def _contains_expected_keywords(answer_text: str, expected_keywords: list[str]) -> bool:
    if not expected_keywords:
        return True
    normalized_answer = answer_text.casefold()
    return all(keyword.casefold() in normalized_answer for keyword in expected_keywords)


def _summarize(results: list[dict[str, Any]]) -> dict[str, Any]:
    summary: dict[str, Any] = {
        'total_prompts': len(results),
        'by_slice': {},
        'by_category': {},
    }
    for result in results:
        slice_name = result['slice']
        bucket = summary['by_slice'].setdefault(
            slice_name,
            {
                'count': 0,
                'baseline_avg_latency_ms': 0.0,
                'crewai_avg_latency_ms': 0.0,
                'baseline_ok': 0,
                'crewai_ok': 0,
                'baseline_keyword_pass': 0,
                'crewai_keyword_pass': 0,
            },
        )
        bucket['count'] += 1
        bucket['baseline_avg_latency_ms'] += float(result['baseline']['latency_ms'])
        bucket['crewai_avg_latency_ms'] += float(result['crewai']['latency_ms'])
        bucket['baseline_ok'] += 1 if int(result['baseline']['status']) == 200 else 0
        bucket['crewai_ok'] += 1 if int(result['crewai']['status']) == 200 else 0
        bucket['baseline_keyword_pass'] += 1 if bool(result['baseline']['keyword_pass']) else 0
        bucket['crewai_keyword_pass'] += 1 if bool(result['crewai']['keyword_pass']) else 0
        category = result['category']
        category_bucket = summary['by_category'].setdefault(
            category,
            {
                'count': 0,
                'baseline_ok': 0,
                'crewai_ok': 0,
                'baseline_keyword_pass': 0,
                'crewai_keyword_pass': 0,
            },
        )
        category_bucket['count'] += 1
        category_bucket['baseline_ok'] += 1 if int(result['baseline']['status']) == 200 else 0
        category_bucket['crewai_ok'] += 1 if int(result['crewai']['status']) == 200 else 0
        category_bucket['baseline_keyword_pass'] += 1 if bool(result['baseline']['keyword_pass']) else 0
        category_bucket['crewai_keyword_pass'] += 1 if bool(result['crewai']['keyword_pass']) else 0
    for bucket in summary['by_slice'].values():
        count = max(1, int(bucket['count']))
        bucket['baseline_avg_latency_ms'] = round(bucket['baseline_avg_latency_ms'] / count, 1)
        bucket['crewai_avg_latency_ms'] = round(bucket['crewai_avg_latency_ms'] / count, 1)
    return summary


def _render_markdown_report(payload: dict[str, Any]) -> str:
    lines = ['# Two-Stack Shadow Comparison Report', '']
    summary = payload.get('summary') or {}
    lines.append('## Summary')
    lines.append('')
    lines.append(f"- Total prompts: {summary.get('total_prompts', 0)}")
    for slice_name, bucket in (summary.get('by_slice') or {}).items():
        lines.append(
            f"- `{slice_name}`: baseline ok {bucket.get('baseline_ok')}/{bucket.get('count')}, "
            f"CrewAI ok {bucket.get('crewai_ok')}/{bucket.get('count')}, "
            f"baseline keyword pass {bucket.get('baseline_keyword_pass')}/{bucket.get('count')}, "
            f"CrewAI keyword pass {bucket.get('crewai_keyword_pass')}/{bucket.get('count')}, "
            f"latency {bucket.get('baseline_avg_latency_ms')}ms vs {bucket.get('crewai_avg_latency_ms')}ms"
        )
    lines.append('')
    lines.append('## By Category')
    lines.append('')
    for category, bucket in (summary.get('by_category') or {}).items():
        lines.append(
            f"- `{category}`: baseline ok {bucket.get('baseline_ok')}/{bucket.get('count')}, "
            f"CrewAI ok {bucket.get('crewai_ok')}/{bucket.get('count')}, "
            f"baseline keyword pass {bucket.get('baseline_keyword_pass')}/{bucket.get('count')}, "
            f"CrewAI keyword pass {bucket.get('crewai_keyword_pass')}/{bucket.get('count')}"
        )
    lines.append('')
    lines.append('## Prompt Results')
    lines.append('')
    for result in payload.get('results') or []:
        lines.append(f"### {result['prompt']}")
        lines.append('')
        lines.append(f"- Slice: `{result['slice']}`")
        lines.append(f"- Category: `{result['category']}`")
        lines.append(f"- Baseline: status {result['baseline']['status']}, latency {result['baseline']['latency_ms']}ms, keyword pass `{result['baseline']['keyword_pass']}`")
        lines.append(f"- CrewAI: status {result['crewai']['status']}, latency {result['crewai']['latency_ms']}ms, keyword pass `{result['crewai']['keyword_pass']}`")
        lines.append(f"- Baseline answer: {result['baseline']['answer_text']}")
        lines.append(f"- CrewAI answer: {result['crewai']['answer_text']}")
        lines.append('')
    return '\n'.join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description='Compare LangGraph baseline with CrewAI public pilot.')
    parser.add_argument('--prompt-file', help='JSON file with a list of prompt strings.')
    parser.add_argument('--output', help='Optional JSON output path.')
    parser.add_argument('--markdown-output', help='Optional Markdown report path.')
    parser.add_argument('--conversation-prefix', default='debug:stack-compare')
    parser.add_argument('--telegram-chat-id', type=int, default=1649845499)
    parser.add_argument('--ai-url', default='http://localhost:8002/v1/messages/respond')
    parser.add_argument('--crewai-public-url', default='http://localhost:8004/v1/shadow/public')
    parser.add_argument('--crewai-protected-url', default='http://localhost:8004/v1/shadow/protected')
    parser.add_argument('--internal-token', default='dev-internal-token')
    args = parser.parse_args()

    prompts = _load_prompts(args.prompt_file)
    baseline_headers = {
        'Content-Type': 'application/json',
        'X-Internal-Api-Token': args.internal_token,
    }
    pilot_headers = {
        'Content-Type': 'application/json',
        'X-Internal-Api-Token': args.internal_token,
    }

    results: list[dict[str, Any]] = []
    for index, entry in enumerate(prompts, start=1):
        prompt = entry['prompt']
        slice_name = entry['slice']
        category = entry.get('category', 'uncategorized')
        expected_keywords = [str(keyword) for keyword in (entry.get('expected_keywords') or [])]
        conversation_id = f'{args.conversation_prefix}:{index}'
        baseline_status, baseline_body, baseline_latency = _post_json(
            args.ai_url,
            baseline_headers,
            {
                'message': prompt,
                'telegram_chat_id': args.telegram_chat_id,
                'conversation_id': conversation_id,
            },
        )
        pilot_status, pilot_body, pilot_latency = _post_json(
            args.crewai_protected_url if slice_name == 'protected' else args.crewai_public_url,
            pilot_headers,
            {
                'message': prompt,
                'telegram_chat_id': args.telegram_chat_id,
                'conversation_id': conversation_id,
                'channel': 'telegram',
            },
        )
        baseline_answer = _extract_answer_text(baseline_body)
        crewai_answer = _extract_answer_text(pilot_body)
        result = {
            'prompt': prompt,
            'slice': slice_name,
            'category': category,
            'expected_keywords': expected_keywords,
            'conversation_id': conversation_id,
            'baseline': {
                'status': baseline_status,
                'latency_ms': round(baseline_latency, 1),
                'answer_text': baseline_answer,
                'keyword_pass': _contains_expected_keywords(baseline_answer, expected_keywords),
                'body': baseline_body,
            },
            'crewai': {
                'status': pilot_status,
                'latency_ms': round(pilot_latency, 1),
                'answer_text': crewai_answer,
                'keyword_pass': _contains_expected_keywords(crewai_answer, expected_keywords),
                'body': pilot_body,
            },
        }
        results.append(result)

    payload = {'summary': _summarize(results), 'results': results}
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2))
    if args.markdown_output:
        output_path = Path(args.markdown_output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(_render_markdown_report(payload))
    else:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
