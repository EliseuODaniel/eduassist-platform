#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT_MD = REPO_ROOT / 'docs/architecture/specialist-gemma-vs-qwen-ab-report-20260417.md'
DEFAULT_OUTPUT_JSON = REPO_ROOT / 'docs/architecture/specialist-gemma-vs-qwen-ab-report-20260417.json'


def _load(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(payload, dict):
        raise SystemExit(f'invalid report: {path}')
    return payload


def _index_by_id(payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
    rows = payload.get('results')
    if not isinstance(rows, list):
        raise SystemExit('invalid report results')
    indexed: dict[str, dict[str, Any]] = {}
    for row in rows:
        if isinstance(row, dict):
            indexed[str(row.get('id') or '')] = row
    return indexed


def _winner(a: float, b: float, *, lower_is_better: bool = False) -> str:
    if a == b:
        return 'tie'
    if lower_is_better:
        return 'a' if a < b else 'b'
    return 'a' if a > b else 'b'


def _render_markdown(payload: dict[str, Any]) -> str:
    lines = ['# Specialist Model A/B Report', '']
    lines.append(f"Date: {payload['generated_at']}")
    lines.append('')
    lines.append(f"Arm A: `{payload['arm_a']['model_label']}`")
    lines.append(f"Arm B: `{payload['arm_b']['model_label']}`")
    lines.append('')
    lines.append('## Automated Summary')
    lines.append('')
    lines.append('| Arm | OK | Keyword pass | Quality | Avg latency | P95 latency |')
    lines.append('| --- | --- | --- | --- | --- | --- |')
    for arm_key in ('arm_a', 'arm_b'):
        arm = payload[arm_key]
        summary = arm['summary']['overall']
        lines.append(
            f"| `{arm['model_label']}` | `{summary['ok']}/{summary['count']}` | `{summary['keyword_pass']}/{summary['count']}` | `{summary['quality_avg']}` | `{summary['avg_latency_ms']} ms` | `{summary['p95_latency_ms']} ms` |"
        )
    lines.append('')
    lines.append('## Win Count')
    lines.append('')
    win_count = payload['comparison']['win_count']
    lines.append(f"- quality winner count: `{payload['arm_a']['model_label']}` `{win_count['quality']['a']}`, `{payload['arm_b']['model_label']}` `{win_count['quality']['b']}`, tie `{win_count['quality']['tie']}`")
    lines.append(f"- latency winner count: `{payload['arm_a']['model_label']}` `{win_count['latency']['a']}`, `{payload['arm_b']['model_label']}` `{win_count['latency']['b']}`, tie `{win_count['latency']['tie']}`")
    lines.append('')
    lines.append('## Case-by-Case Comparison')
    lines.append('')
    for row in payload['comparison']['cases']:
        lines.append(f"### {row['id']} `{row['slice']}` `{row['category']}`")
        lines.append('')
        lines.append(f"- prompt: `{row['prompt']}`")
        lines.append(f"- quality winner: `{row['quality_winner']}`")
        lines.append(f"- latency winner: `{row['latency_winner']}`")
        lines.append(f"- `{payload['arm_a']['model_label']}` quality `{row['arm_a']['quality_score']}`, latency `{row['arm_a']['latency_ms']} ms`")
        lines.append(f"- `{payload['arm_b']['model_label']}` quality `{row['arm_b']['quality_score']}`, latency `{row['arm_b']['latency_ms']} ms`")
        lines.append(f"- `{payload['arm_a']['model_label']}` answer: {row['arm_a']['message_text']}")
        lines.append(f"- `{payload['arm_b']['model_label']}` answer: {row['arm_b']['message_text']}")
        lines.append('')
    return '\n'.join(lines) + '\n'


def main() -> int:
    parser = argparse.ArgumentParser(description='Compare two specialist model profile evaluation reports.')
    parser.add_argument('--arm-a', type=Path, required=True)
    parser.add_argument('--arm-b', type=Path, required=True)
    parser.add_argument('--output-md', type=Path, default=DEFAULT_OUTPUT_MD)
    parser.add_argument('--output-json', type=Path, default=DEFAULT_OUTPUT_JSON)
    args = parser.parse_args()

    arm_a = _load(args.arm_a)
    arm_b = _load(args.arm_b)
    by_id_a = _index_by_id(arm_a)
    by_id_b = _index_by_id(arm_b)
    case_ids = sorted(set(by_id_a) & set(by_id_b))
    comparison_cases: list[dict[str, Any]] = []
    quality_wins = {'a': 0, 'b': 0, 'tie': 0}
    latency_wins = {'a': 0, 'b': 0, 'tie': 0}
    for case_id in case_ids:
        row_a = by_id_a[case_id]
        row_b = by_id_b[case_id]
        quality_winner = _winner(float(row_a['quality_score']), float(row_b['quality_score']))
        latency_winner = _winner(float(row_a['latency_ms']), float(row_b['latency_ms']), lower_is_better=True)
        quality_wins[quality_winner] += 1
        latency_wins[latency_winner] += 1
        comparison_cases.append(
            {
                'id': case_id,
                'slice': row_a['slice'],
                'category': row_a['category'],
                'prompt': row_a['prompt'],
                'quality_winner': quality_winner,
                'latency_winner': latency_winner,
                'arm_a': {
                    'quality_score': row_a['quality_score'],
                    'keyword_pass': row_a['keyword_pass'],
                    'latency_ms': row_a['latency_ms'],
                    'message_text': row_a['message_text'],
                },
                'arm_b': {
                    'quality_score': row_b['quality_score'],
                    'keyword_pass': row_b['keyword_pass'],
                    'latency_ms': row_b['latency_ms'],
                    'message_text': row_b['message_text'],
                },
            }
        )

    payload = {
        'generated_at': datetime.now(UTC).isoformat(),
        'arm_a': arm_a,
        'arm_b': arm_b,
        'comparison': {
            'count': len(comparison_cases),
            'win_count': {
                'quality': quality_wins,
                'latency': latency_wins,
            },
            'cases': comparison_cases,
        },
    }
    args.output_md.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    args.output_md.write_text(_render_markdown(payload), encoding='utf-8')
    print(args.output_json)
    print(args.output_md)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
