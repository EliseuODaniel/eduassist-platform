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
    'qual o horario da biblioteca?',
    'quando comeca a matricula?',
    'qual o telefone e o fax?',
    'qual instagram do colegio?',
    'qual a estrutura da escola?',
]


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


def _load_prompts(path: str | None) -> list[str]:
    if not path:
        return DEFAULT_PROMPTS
    payload = json.loads(Path(path).read_text())
    if isinstance(payload, list):
        return [str(item) for item in payload]
    raise SystemExit('Prompt file must be a JSON list of strings.')


def main() -> int:
    parser = argparse.ArgumentParser(description='Compare LangGraph baseline with CrewAI public pilot.')
    parser.add_argument('--prompt-file', help='JSON file with a list of prompt strings.')
    parser.add_argument('--output', help='Optional JSON output path.')
    parser.add_argument('--conversation-prefix', default='debug:stack-compare')
    parser.add_argument('--telegram-chat-id', type=int, default=1649845499)
    parser.add_argument('--ai-url', default='http://localhost:8002/v1/messages/respond')
    parser.add_argument('--crewai-url', default='http://localhost:8004/v1/shadow/public')
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
    for index, prompt in enumerate(prompts, start=1):
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
            args.crewai_url,
            pilot_headers,
            {
                'message': prompt,
                'telegram_chat_id': args.telegram_chat_id,
                'conversation_id': conversation_id,
                'channel': 'telegram',
            },
        )
        result = {
            'prompt': prompt,
            'conversation_id': conversation_id,
            'baseline': {
                'status': baseline_status,
                'latency_ms': round(baseline_latency, 1),
                'body': baseline_body,
            },
            'crewai': {
                'status': pilot_status,
                'latency_ms': round(pilot_latency, 1),
                'body': pilot_body,
            },
        }
        results.append(result)

    payload = {'results': results}
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
