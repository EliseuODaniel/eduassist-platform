#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import random
from pathlib import Path
from typing import Any


def _render_markdown(packet: dict[str, Any]) -> str:
    lines = ['# Blind Review Packet', '']
    lines.append(f"Source report: `{packet['source_report']}`")
    lines.append(f"Seed: `{packet['seed']}`")
    lines.append('')
    lines.append('Critérios sugeridos para avaliação humana:')
    lines.append('- precisão factual')
    lines.append('- completude')
    lines.append('- utilidade prática')
    lines.append('- clareza')
    lines.append('- aderência ao escopo pedido')
    lines.append('- concisão')
    lines.append('- naturalidade do tom')
    lines.append('')
    for case in packet['cases']:
        lines.append(f"## {case['id']}")
        lines.append('')
        lines.append(f"Prompt: {case['prompt']}")
        lines.append('')
        lines.append(f"Slice: `{case['slice']}` | Categoria: `{case['category']}`")
        lines.append('')
        for answer in case['answers']:
            lines.append(f"### Resposta {answer['blind_label']}")
            lines.append('')
            lines.append(answer['answer_text'] or '[resposta vazia]')
            lines.append('')
    return '\n'.join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--report-json', required=True)
    parser.add_argument('--output-md', required=True)
    parser.add_argument('--output-key-json', required=True)
    parser.add_argument('--seed', type=int, default=42)
    args = parser.parse_args()

    report_path = Path(args.report_json).resolve()
    payload = json.loads(report_path.read_text(encoding='utf-8'))
    rng = random.Random(args.seed)

    packet: dict[str, Any] = {
        'source_report': str(report_path),
        'seed': args.seed,
        'cases': [],
    }
    answer_key: dict[str, Any] = {
        'source_report': str(report_path),
        'seed': args.seed,
        'cases': [],
    }

    for index, row in enumerate(payload.get('results', []), start=1):
        blind_answers: list[dict[str, Any]] = []
        stack_entries: list[tuple[str, dict[str, Any]]] = [
            (stack_name, row[stack_name])
            for stack_name in ('langgraph', 'python_functions', 'llamaindex', 'specialist_supervisor')
        ]
        rng.shuffle(stack_entries)
        labels = ['A', 'B', 'C', 'D']
        key_rows: list[dict[str, Any]] = []
        for blind_label, (stack_name, answer_payload) in zip(labels, stack_entries, strict=True):
            blind_answers.append(
                {
                    'blind_label': blind_label,
                    'answer_text': str(answer_payload.get('answer_text') or ''),
                }
            )
            key_rows.append(
                {
                    'blind_label': blind_label,
                    'stack': stack_name,
                    'quality_score': answer_payload.get('quality_score'),
                    'keyword_pass': answer_payload.get('keyword_pass'),
                    'latency_ms': answer_payload.get('latency_ms'),
                }
            )
        case_id = row.get('id') or f'case_{index:03d}'
        packet['cases'].append(
            {
                'id': case_id,
                'prompt': row['prompt'],
                'slice': row['slice'],
                'category': row.get('category') or 'uncategorized',
                'answers': blind_answers,
            }
        )
        answer_key['cases'].append(
            {
                'id': case_id,
                'prompt': row['prompt'],
                'mapping': key_rows,
            }
        )

    output_md = Path(args.output_md)
    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_md.write_text(_render_markdown(packet), encoding='utf-8')

    output_key = Path(args.output_key_json)
    output_key.parent.mkdir(parents=True, exist_ok=True)
    output_key.write_text(json.dumps(answer_key, ensure_ascii=False, indent=2), encoding='utf-8')

    print(str(output_md))
    print(str(output_key))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
