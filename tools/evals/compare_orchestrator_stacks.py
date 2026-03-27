#!/usr/bin/env python3
from __future__ import annotations

import argparse
import difflib
import json
from pathlib import Path
from time import perf_counter
from datetime import datetime, UTC
import re
from typing import Any
import unicodedata
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
ERROR_WEIGHTS = {
    'request_failed': 60,
    'forbidden_entity_or_value': 45,
    'repair_miss': 18,
    'followup_context_drop': 25,
    'missing_expected_keyword': 20,
    'unnecessary_clarification': 12,
    'repetitive_reply': 10,
    'canned_tone': 8,
}

QUALITY_SIGNAL_NAMES = (
    'repair_ack',
    'followup_adaptation',
    'personalization',
)


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
    support_terms = (
        'atendente humano',
        'atendimento humano',
        'quero falar com um humano',
        'preciso falar com um humano',
        'como falo com um atendente',
        'quero falar com o setor',
        'suporte humano',
        'atendente',
        'humano',
        'ticket operacional',
        'atd-',
    )
    if any(term in lowered for term in support_terms):
        return 'support'
    workflow_terms = (
        'visita',
        'tour',
        'protocolar',
        'protocolo',
        'solicitacao',
        'solicitação',
        'remarcar',
        'reagendar',
        'cancelar a visita',
        'resume meu pedido',
        'status da visita',
        'status do protocolo',
    )
    if any(term in lowered for term in workflow_terms):
        return 'workflow'
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
        if isinstance(item, dict) and isinstance(item.get('turns'), list):
            entries.append(item)
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


def _expand_entries(entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    expanded: list[dict[str, Any]] = []
    for index, entry in enumerate(entries, start=1):
        if isinstance(entry.get('turns'), list):
            thread_id = str(entry.get('thread_id') or f'thread_{index}')
            default_slice = str(entry.get('slice') or 'public')
            default_category = str(entry.get('category') or 'threaded')
            for turn_index, turn in enumerate(entry['turns'], start=1):
                if not isinstance(turn, dict) or not isinstance(turn.get('prompt'), str):
                    raise SystemExit('Each threaded turn must be an object with a prompt field.')
                prompt = str(turn['prompt'])
                expanded.append(
                    {
                        'prompt': prompt,
                        'slice': str(turn.get('slice') or default_slice or _infer_slice(prompt)),
                        'category': str(turn.get('category') or default_category),
                        'expected_keywords': [str(keyword) for keyword in (turn.get('expected_keywords') or []) if str(keyword).strip()],
                        'forbidden_keywords': [str(keyword) for keyword in (turn.get('forbidden_keywords') or []) if str(keyword).strip()],
                        'thread_id': thread_id,
                        'turn_index': turn_index,
                        'note': str(turn.get('note') or ''),
                        'telegram_chat_id': turn.get('telegram_chat_id', entry.get('telegram_chat_id')),
                    }
                )
            continue
        expanded.append(
            {
                'prompt': str(entry['prompt']),
                'slice': str(entry.get('slice') or _infer_slice(str(entry['prompt']))),
                'category': str(entry.get('category') or 'uncategorized'),
                'expected_keywords': [str(keyword) for keyword in (entry.get('expected_keywords') or []) if str(keyword).strip()],
                'forbidden_keywords': [str(keyword) for keyword in (entry.get('forbidden_keywords') or []) if str(keyword).strip()],
                'thread_id': str(entry.get('thread_id') or ''),
                'turn_index': int(entry.get('turn_index') or 1),
                'note': str(entry.get('note') or ''),
                'telegram_chat_id': entry.get('telegram_chat_id'),
            }
        )
    return expanded


def _load_prompts(path: str | None) -> list[dict[str, Any]]:
    if not path:
        default_path = Path(DEFAULT_PROMPT_FILE)
        if default_path.exists():
            payload = json.loads(default_path.read_text())
            return _expand_entries(_normalize_prompt_entries(payload))
        return _expand_entries(_normalize_prompt_entries(DEFAULT_PROMPTS))
    payload = json.loads(Path(path).read_text())
    return _expand_entries(_normalize_prompt_entries(payload))


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


def _normalize_match_text(value: str) -> str:
    text = unicodedata.normalize('NFKD', str(value or ''))
    text = ''.join(ch for ch in text if not unicodedata.combining(ch))
    text = text.casefold()
    text = re.sub(r'[-_/]+', '', text)
    text = re.sub(r'[^0-9a-z]+', ' ', text)
    text = re.sub(r'(?<=\d)\s+(?=\d)', '', text)
    return ' '.join(text.split())


def _contains_expected_keywords(answer_text: str, expected_keywords: list[str]) -> bool:
    if not expected_keywords:
        return True
    normalized_answer = _normalize_match_text(answer_text)
    return all(_normalize_match_text(keyword) in normalized_answer for keyword in expected_keywords)


def _contains_forbidden_keywords(answer_text: str, forbidden_keywords: list[str]) -> bool:
    if not forbidden_keywords:
        return False
    normalized_answer = _normalize_match_text(answer_text)
    return any(_normalize_match_text(keyword) in normalized_answer for keyword in forbidden_keywords)


def _detect_error_types(
    *,
    answer_text: str,
    expected_keywords: list[str],
    forbidden_keywords: list[str],
    prompt: str,
    previous_answer: str,
    status: int,
    turn_index: int,
    note: str,
) -> list[str]:
    if status != 200:
        return ['request_failed']
    normalized_answer = answer_text.casefold().strip()
    normalized_note = note.casefold().strip()
    errors: list[str] = []
    if expected_keywords and not _contains_expected_keywords(answer_text, expected_keywords):
        errors.append('missing_expected_keyword')
    if _contains_forbidden_keywords(answer_text, forbidden_keywords):
        errors.append('forbidden_entity_or_value')
    if expected_keywords and '?' in answer_text:
        errors.append('unnecessary_clarification')
    if turn_index > 1 and previous_answer:
        similarity = difflib.SequenceMatcher(a=previous_answer.casefold().strip(), b=normalized_answer).ratio()
        repeated_auth_guidance = (
            'essa consulta depende de autenticacao e vinculo da sua conta no telegram' in normalized_answer
            and 'current state drift' in normalized_note
        )
        if similarity >= 0.92 and not repeated_auth_guidance:
            errors.append('repetitive_reply')
        if prompt.casefold().strip().startswith('e ') and expected_keywords and not _contains_expected_keywords(answer_text, expected_keywords):
            errors.append('followup_context_drop')
    if 'repair' in normalized_note:
        repair_markers = (
            'desculp',
            'corrig',
            'voce esta certo',
            'você está certo',
            'houve um erro',
            'confus',
            'sem problema',
            'comecar do zero',
            'começar do zero',
        )
        if not any(marker in normalized_answer for marker in repair_markers):
            errors.append('repair_miss')
    canned_markers = (
        'por aqui eu consigo te ajudar',
        'se quiser, pode me dizer direto',
        'se precisar de mais alguma informacao',
        'e so me avisar',
    )
    if any(marker in normalized_answer for marker in canned_markers) and expected_keywords:
        errors.append('canned_tone')
    return sorted(set(errors))


def _needs_personalization(prompt: str, expected_keywords: list[str]) -> bool:
    normalized_prompt = _normalize_match_text(prompt)
    if any(term in normalized_prompt.split() for term in ('meu', 'minha', 'meus', 'minhas', 'dele', 'dela')):
        return True
    if any(term in normalized_prompt for term in ('lucas', 'ana', 'joao', 'joão', 'maria', 'sofia')):
        return True
    return any(' ' in str(keyword).strip() for keyword in expected_keywords)


def _detect_quality_signals(
    *,
    answer_text: str,
    expected_keywords: list[str],
    prompt: str,
    previous_answer: str,
    turn_index: int,
    note: str,
) -> dict[str, bool | None]:
    normalized_answer = answer_text.casefold().strip()
    normalized_note = note.casefold().strip()
    followup_prompt = prompt.casefold().strip().startswith(('e ', 'mas '))
    repair_eligible = 'repair' in normalized_note
    personalization_eligible = _needs_personalization(prompt, expected_keywords)
    repair_markers = (
        'desculp',
        'corrig',
        'voce esta certo',
        'você está certo',
        'houve um erro',
        'confus',
        'sem problema',
        'comecar do zero',
        'começar do zero',
    )
    return {
        'repair_ack': (
            any(marker in normalized_answer for marker in repair_markers)
            if repair_eligible
            else None
        ),
        'followup_adaptation': (
            (
                not previous_answer
                or difflib.SequenceMatcher(a=previous_answer.casefold().strip(), b=normalized_answer).ratio() < 0.92
            )
            if turn_index > 1 and followup_prompt
            else None
        ),
        'personalization': (
            (not expected_keywords or _contains_expected_keywords(answer_text, expected_keywords))
            if personalization_eligible
            else None
        ),
    }


def _quality_score(*, status: int, error_types: list[str]) -> int:
    if status != 200:
        return 0
    penalty = sum(ERROR_WEIGHTS.get(error_type, 5) for error_type in error_types)
    return max(0, 100 - penalty)


def _summarize(results: list[dict[str, Any]]) -> dict[str, Any]:
    summary: dict[str, Any] = {
        'total_prompts': len(results),
        'by_slice': {},
        'by_category': {},
        'by_thread': {},
        'error_types': {'baseline': {}, 'crewai': {}},
        'quality_signals': {
            'baseline': {name: {'hits': 0, 'eligible': 0} for name in QUALITY_SIGNAL_NAMES},
            'crewai': {name: {'hits': 0, 'eligible': 0} for name in QUALITY_SIGNAL_NAMES},
        },
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
                'baseline_quality_avg': 0.0,
                'crewai_quality_avg': 0.0,
            },
        )
        bucket['count'] += 1
        bucket['baseline_avg_latency_ms'] += float(result['baseline']['latency_ms'])
        bucket['crewai_avg_latency_ms'] += float(result['crewai']['latency_ms'])
        bucket['baseline_ok'] += 1 if int(result['baseline']['status']) == 200 else 0
        bucket['crewai_ok'] += 1 if int(result['crewai']['status']) == 200 else 0
        bucket['baseline_keyword_pass'] += 1 if bool(result['baseline']['keyword_pass']) else 0
        bucket['crewai_keyword_pass'] += 1 if bool(result['crewai']['keyword_pass']) else 0
        bucket['baseline_quality_avg'] += float(result['baseline']['quality_score'])
        bucket['crewai_quality_avg'] += float(result['crewai']['quality_score'])
        category = result['category']
        category_bucket = summary['by_category'].setdefault(
            category,
            {
                'count': 0,
                'baseline_ok': 0,
                'crewai_ok': 0,
                'baseline_keyword_pass': 0,
                'crewai_keyword_pass': 0,
                'baseline_quality_avg': 0.0,
                'crewai_quality_avg': 0.0,
            },
        )
        category_bucket['count'] += 1
        category_bucket['baseline_ok'] += 1 if int(result['baseline']['status']) == 200 else 0
        category_bucket['crewai_ok'] += 1 if int(result['crewai']['status']) == 200 else 0
        category_bucket['baseline_keyword_pass'] += 1 if bool(result['baseline']['keyword_pass']) else 0
        category_bucket['crewai_keyword_pass'] += 1 if bool(result['crewai']['keyword_pass']) else 0
        category_bucket['baseline_quality_avg'] += float(result['baseline']['quality_score'])
        category_bucket['crewai_quality_avg'] += float(result['crewai']['quality_score'])
        thread_id = str(result.get('thread_id') or '')
        if thread_id:
            thread_bucket = summary['by_thread'].setdefault(
                thread_id,
                {
                    'count': 0,
                    'slice': result['slice'],
                    'category': result['category'],
                    'baseline_keyword_pass': 0,
                    'crewai_keyword_pass': 0,
                    'baseline_quality_avg': 0.0,
                    'crewai_quality_avg': 0.0,
                },
            )
            thread_bucket['count'] += 1
            thread_bucket['baseline_keyword_pass'] += 1 if bool(result['baseline']['keyword_pass']) else 0
            thread_bucket['crewai_keyword_pass'] += 1 if bool(result['crewai']['keyword_pass']) else 0
            thread_bucket['baseline_quality_avg'] += float(result['baseline']['quality_score'])
            thread_bucket['crewai_quality_avg'] += float(result['crewai']['quality_score'])
        for error in result['baseline'].get('error_types', []):
            summary['error_types']['baseline'][error] = summary['error_types']['baseline'].get(error, 0) + 1
        for error in result['crewai'].get('error_types', []):
            summary['error_types']['crewai'][error] = summary['error_types']['crewai'].get(error, 0) + 1
        for engine_name in ('baseline', 'crewai'):
            for signal_name, signal_value in (result[engine_name].get('quality_signals') or {}).items():
                if signal_name not in QUALITY_SIGNAL_NAMES:
                    continue
                if signal_value is None:
                    continue
                signal_bucket = summary['quality_signals'][engine_name][signal_name]
                signal_bucket['eligible'] += 1
                signal_bucket['hits'] += 1 if signal_value else 0
    for bucket in summary['by_slice'].values():
        count = max(1, int(bucket['count']))
        bucket['baseline_avg_latency_ms'] = round(bucket['baseline_avg_latency_ms'] / count, 1)
        bucket['crewai_avg_latency_ms'] = round(bucket['crewai_avg_latency_ms'] / count, 1)
        bucket['baseline_quality_avg'] = round(bucket['baseline_quality_avg'] / count, 1)
        bucket['crewai_quality_avg'] = round(bucket['crewai_quality_avg'] / count, 1)
    for bucket in summary['by_category'].values():
        count = max(1, int(bucket['count']))
        bucket['baseline_quality_avg'] = round(bucket['baseline_quality_avg'] / count, 1)
        bucket['crewai_quality_avg'] = round(bucket['crewai_quality_avg'] / count, 1)
    for bucket in summary['by_thread'].values():
        count = max(1, int(bucket['count']))
        bucket['baseline_quality_avg'] = round(bucket['baseline_quality_avg'] / count, 1)
        bucket['crewai_quality_avg'] = round(bucket['crewai_quality_avg'] / count, 1)
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
            f"quality {bucket.get('baseline_quality_avg')} vs {bucket.get('crewai_quality_avg')}, "
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
            f"CrewAI keyword pass {bucket.get('crewai_keyword_pass')}/{bucket.get('count')}, "
            f"quality {bucket.get('baseline_quality_avg')} vs {bucket.get('crewai_quality_avg')}"
        )
    lines.append('')
    lines.append('## Error Types')
    lines.append('')
    for engine_name, bucket in (summary.get('error_types') or {}).items():
        items = ', '.join(f'{name}={count}' for name, count in sorted(bucket.items()))
        lines.append(f"- `{engine_name}`: {items or 'nenhum'}")
    lines.append('')
    lines.append('## Quality Signals')
    lines.append('')
    for engine_name, bucket in (summary.get('quality_signals') or {}).items():
        parts = []
        for signal_name, signal_values in bucket.items():
            parts.append(f"{signal_name} {signal_values.get('hits')}/{signal_values.get('eligible')}")
        lines.append(f"- `{engine_name}`: {', '.join(parts)}")
    lines.append('')
    lines.append('## By Thread')
    lines.append('')
    for thread_id, bucket in (summary.get('by_thread') or {}).items():
        lines.append(
            f"- `{thread_id}` ({bucket.get('slice')}/{bucket.get('category')}): "
            f"baseline keyword pass {bucket.get('baseline_keyword_pass')}/{bucket.get('count')}, "
            f"CrewAI keyword pass {bucket.get('crewai_keyword_pass')}/{bucket.get('count')}, "
            f"quality {bucket.get('baseline_quality_avg')} vs {bucket.get('crewai_quality_avg')}"
        )
    lines.append('')
    lines.append('## Prompt Results')
    lines.append('')
    for result in payload.get('results') or []:
        lines.append(f"### {result['prompt']}")
        lines.append('')
        lines.append(f"- Slice: `{result['slice']}`")
        lines.append(f"- Category: `{result['category']}`")
        if result.get('thread_id'):
            lines.append(f"- Thread: `{result['thread_id']}` turn `{result['turn_index']}`")
        if result.get('note'):
            lines.append(f"- Note: {result['note']}")
        lines.append(f"- Baseline: status {result['baseline']['status']}, latency {result['baseline']['latency_ms']}ms, keyword pass `{result['baseline']['keyword_pass']}`, quality `{result['baseline']['quality_score']}`")
        lines.append(f"- CrewAI: status {result['crewai']['status']}, latency {result['crewai']['latency_ms']}ms, keyword pass `{result['crewai']['keyword_pass']}`, quality `{result['crewai']['quality_score']}`")
        if result['baseline'].get('error_types'):
            lines.append(f"- Baseline errors: {', '.join(result['baseline']['error_types'])}")
        if result['crewai'].get('error_types'):
            lines.append(f"- CrewAI errors: {', '.join(result['crewai']['error_types'])}")
        baseline_signals = ', '.join(f'{k}={v}' for k, v in (result['baseline'].get('quality_signals') or {}).items())
        crewai_signals = ', '.join(f'{k}={v}' for k, v in (result['crewai'].get('quality_signals') or {}).items())
        if baseline_signals:
            lines.append(f"- Baseline quality signals: {baseline_signals}")
        if crewai_signals:
            lines.append(f"- CrewAI quality signals: {crewai_signals}")
        lines.append(f"- Baseline answer: {result['baseline']['answer_text']}")
        lines.append(f"- CrewAI answer: {result['crewai']['answer_text']}")
        lines.append('')
    return '\n'.join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description='Compare LangGraph baseline with CrewAI public pilot.')
    parser.add_argument('--prompt-file', help='JSON file with a list of prompt strings.')
    parser.add_argument('--output', help='Optional JSON output path.')
    parser.add_argument('--markdown-output', help='Optional Markdown report path.')
    parser.add_argument('--conversation-prefix')
    parser.add_argument('--telegram-chat-id', type=int, default=1649845499)
    parser.add_argument('--ai-url', default='http://localhost:8002/v1/messages/respond')
    parser.add_argument('--crewai-public-url', default='http://localhost:8004/v1/shadow/public')
    parser.add_argument('--crewai-protected-url', default='http://localhost:8004/v1/shadow/protected')
    parser.add_argument('--crewai-workflow-url', default='http://localhost:8004/v1/shadow/workflow')
    parser.add_argument('--crewai-support-url', default='http://localhost:8004/v1/shadow/support')
    parser.add_argument('--internal-token', default='dev-internal-token')
    args = parser.parse_args()
    conversation_prefix = args.conversation_prefix or f"debug:stack-compare:{datetime.now(UTC).strftime('%Y%m%dT%H%M%SZ')}"

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
    previous_answers: dict[str, dict[str, str]] = {}
    for index, entry in enumerate(prompts, start=1):
        prompt = entry['prompt']
        slice_name = entry['slice']
        category = entry.get('category', 'uncategorized')
        expected_keywords = [str(keyword) for keyword in (entry.get('expected_keywords') or [])]
        forbidden_keywords = [str(keyword) for keyword in (entry.get('forbidden_keywords') or [])]
        thread_id = str(entry.get('thread_id') or '')
        turn_index = int(entry.get('turn_index') or 1)
        note = str(entry.get('note') or '')
        telegram_chat_id = entry.get('telegram_chat_id')
        conversation_id = f'{conversation_prefix}:thread:{thread_id}' if thread_id else f'{conversation_prefix}:{index}'
        baseline_status, baseline_body, baseline_latency = _post_json(
            args.ai_url,
            baseline_headers,
            {
                'message': prompt,
                'telegram_chat_id': telegram_chat_id if telegram_chat_id is not None else args.telegram_chat_id,
                'conversation_id': conversation_id,
            },
        )
        pilot_url = args.crewai_public_url
        if slice_name == 'protected':
            pilot_url = args.crewai_protected_url
        elif slice_name == 'workflow':
            pilot_url = args.crewai_workflow_url
        elif slice_name == 'support':
            pilot_url = args.crewai_support_url
        pilot_status, pilot_body, pilot_latency = _post_json(
            pilot_url,
            pilot_headers,
            {
                'message': prompt,
                'telegram_chat_id': telegram_chat_id if telegram_chat_id is not None else args.telegram_chat_id,
                'conversation_id': conversation_id,
                'channel': 'telegram',
            },
        )
        baseline_answer = _extract_answer_text(baseline_body)
        crewai_answer = _extract_answer_text(pilot_body)
        state = previous_answers.setdefault(conversation_id, {'baseline': '', 'crewai': ''})
        previous_baseline_answer = state['baseline']
        previous_crewai_answer = state['crewai']
        baseline_error_types = _detect_error_types(
            answer_text=baseline_answer,
            expected_keywords=expected_keywords,
            forbidden_keywords=forbidden_keywords,
            prompt=prompt,
            previous_answer=previous_baseline_answer,
            status=baseline_status,
            turn_index=turn_index,
            note=note,
        )
        crewai_error_types = _detect_error_types(
            answer_text=crewai_answer,
            expected_keywords=expected_keywords,
            forbidden_keywords=forbidden_keywords,
            prompt=prompt,
            previous_answer=previous_crewai_answer,
            status=pilot_status,
            turn_index=turn_index,
            note=note,
        )
        result = {
            'prompt': prompt,
            'slice': slice_name,
            'category': category,
            'expected_keywords': expected_keywords,
            'forbidden_keywords': forbidden_keywords,
            'conversation_id': conversation_id,
            'thread_id': thread_id,
            'turn_index': turn_index,
            'note': note,
            'telegram_chat_id': telegram_chat_id if telegram_chat_id is not None else args.telegram_chat_id,
            'run_prefix': conversation_prefix,
            'baseline': {
                'status': baseline_status,
                'latency_ms': round(baseline_latency, 1),
                'answer_text': baseline_answer,
                'keyword_pass': _contains_expected_keywords(baseline_answer, expected_keywords),
                'error_types': baseline_error_types,
                'quality_signals': _detect_quality_signals(
                    answer_text=baseline_answer,
                    expected_keywords=expected_keywords,
                    prompt=prompt,
                    previous_answer=previous_baseline_answer,
                    turn_index=turn_index,
                    note=note,
                ),
                'quality_score': _quality_score(status=baseline_status, error_types=baseline_error_types),
                'body': baseline_body,
            },
            'crewai': {
                'status': pilot_status,
                'latency_ms': round(pilot_latency, 1),
                'answer_text': crewai_answer,
                'keyword_pass': _contains_expected_keywords(crewai_answer, expected_keywords),
                'error_types': crewai_error_types,
                'quality_signals': _detect_quality_signals(
                    answer_text=crewai_answer,
                    expected_keywords=expected_keywords,
                    prompt=prompt,
                    previous_answer=previous_crewai_answer,
                    turn_index=turn_index,
                    note=note,
                ),
                'quality_score': _quality_score(status=pilot_status, error_types=crewai_error_types),
                'body': pilot_body,
            },
        }
        results.append(result)
        state['baseline'] = baseline_answer
        state['crewai'] = crewai_answer

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
