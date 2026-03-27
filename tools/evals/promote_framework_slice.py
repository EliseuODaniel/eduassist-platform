#!/usr/bin/env python3
from __future__ import annotations

import argparse
import getpass
import json
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.evals.apply_framework_rollout_promotion import _build_settings, _parse_slice_rollouts

DEFAULT_ENV_FILE = REPO_ROOT / '.env'
DEFAULT_CHANGELOG_MD = REPO_ROOT / 'docs/architecture/framework-rollout-changelog.md'
DEFAULT_CHANGELOG_JSON = REPO_ROOT / 'docs/architecture/framework-rollout-changelog.json'
DEFAULT_REPORT_MD = REPO_ROOT / 'docs/architecture/framework-slice-promotion-report.md'
DEFAULT_REPORT_JSON = REPO_ROOT / 'docs/architecture/framework-slice-promotion-report.json'
DEFAULT_ARTIFACT_JSON = REPO_ROOT / 'artifacts/framework-slice-promotion-report.json'


def _configured_slice_set(value: str | None) -> set[str]:
    return {item.strip() for item in str(value or '').split(',') if item.strip()}


def _normalize_rollouts(mapping: dict[str, int]) -> str:
    items = sorted((name, percent) for name, percent in mapping.items() if percent > 0)
    return ','.join(f'{name}:{percent}' for name, percent in items)


def _normalize_csv(values: set[str]) -> str:
    return ','.join(sorted(item for item in values if item))


def _load_json_array(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    try:
        payload = json.loads(path.read_text(encoding='utf-8'))
    except Exception:
        return []
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]
    return []


def _append_changelog(*, entry: dict[str, Any], md_path: Path, json_path: Path) -> None:
    rows = _load_json_array(json_path)
    rows.append(entry)
    json_path.write_text(json.dumps(rows, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

    lines = [
        '# Framework Rollout Changelog',
        '',
        '| Date | Slice | Before | After | Mode | Result | Operator | Reason | Env File |',
        '| --- | --- | ---: | ---: | --- | --- | --- | --- | --- |',
    ]
    for item in reversed(rows[-50:]):
        lines.append(
            f"| `{item.get('timestamp', '')}` | `{item.get('slice', '')}` | "
            f"`{item.get('before_rollout_percent', '')}%` | `{item.get('after_rollout_percent', '')}%` | "
            f"`{item.get('mode', '')}` | `{item.get('result', '')}` | "
            f"`{item.get('operator', '')}` | {item.get('reason', '')} | `{item.get('env_file', '')}` |"
        )
    md_path.write_text('\n'.join(lines) + '\n', encoding='utf-8')


def _write_report(*, report_md: Path, report_json: Path, artifact_json: Path, payload: dict[str, Any]) -> None:
    lines = [
        '# Framework Slice Promotion Report',
        '',
        f"Date: {payload['timestamp']}",
        '',
        '## Summary',
        '',
        f"- slice: `{payload['slice']}`",
        f"- before rollout: `{payload['before_rollout_percent']}%`",
        f"- after rollout: `{payload['after_rollout_percent']}%`",
        f"- mode: `{payload['mode']}`",
        f"- apply requested: `{payload['apply']}`",
        f"- result: `{payload['result']}`",
        f"- operator: `{payload['operator']}`",
        f"- reason: `{payload['reason']}`",
        f"- env file: `{payload['env_file']}`",
        f"- proposed slices: `{payload['proposed_slices']}`",
        f"- proposed slice rollouts: `{payload['proposed_slice_rollouts']}`",
        f"- proposed allowlist slices: `{payload['proposed_allowlist_slices']}`",
        f"- nested report: `{payload['nested_report']}`",
    ]
    if payload.get('stderr'):
        lines.extend(['', '## STDERR', '', '```text', str(payload['stderr']), '```'])
    report_md.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    json_text = json.dumps(payload, ensure_ascii=False, indent=2) + '\n'
    report_json.write_text(json_text, encoding='utf-8')
    artifact_json.parent.mkdir(parents=True, exist_ok=True)
    artifact_json.write_text(json_text, encoding='utf-8')


def main() -> int:
    parser = argparse.ArgumentParser(description='Promote a rollout slice through a single command with changelog output.')
    parser.add_argument('--slice', required=True, choices=['public', 'protected', 'support', 'workflow'])
    parser.add_argument('--to-rollout-percent', required=True, type=int)
    parser.add_argument('--reason', required=True)
    parser.add_argument('--operator', default='')
    parser.add_argument('--env-file', type=Path, default=DEFAULT_ENV_FILE)
    parser.add_argument('--candidate-engine', default=None)
    parser.add_argument('--services', default='ai-orchestrator')
    parser.add_argument('--status-url', default='http://127.0.0.1:8002/v1/status')
    parser.add_argument('--allowlist-mode', choices=['auto', 'keep', 'add', 'remove'], default='auto')
    parser.add_argument('--apply', action='store_true')
    parser.add_argument('--changelog-md', type=Path, default=DEFAULT_CHANGELOG_MD)
    parser.add_argument('--changelog-json', type=Path, default=DEFAULT_CHANGELOG_JSON)
    parser.add_argument('--report', type=Path, default=DEFAULT_REPORT_MD)
    parser.add_argument('--json', type=Path, default=DEFAULT_REPORT_JSON)
    parser.add_argument('--artifact-json', type=Path, default=DEFAULT_ARTIFACT_JSON)
    args = parser.parse_args()

    settings = _build_settings(args.env_file)
    slice_rollouts = _parse_slice_rollouts(getattr(settings, 'orchestrator_experiment_slice_rollouts', ''))
    configured_slices = _configured_slice_set(getattr(settings, 'orchestrator_experiment_slices', ''))
    allowlist_slices = _configured_slice_set(getattr(settings, 'orchestrator_experiment_allowlist_slices', ''))

    before_rollout_percent = int(slice_rollouts.get(args.slice, getattr(settings, 'orchestrator_experiment_rollout_percent', 0) or 0))
    target_percent = max(0, min(100, int(args.to_rollout_percent)))

    if target_percent > 0:
        configured_slices.add(args.slice)
        slice_rollouts[args.slice] = target_percent
    else:
        configured_slices.discard(args.slice)
        slice_rollouts.pop(args.slice, None)

    if args.allowlist_mode == 'add':
        allowlist_slices.add(args.slice)
    elif args.allowlist_mode == 'remove':
        allowlist_slices.discard(args.slice)
    elif args.allowlist_mode == 'auto':
        if args.slice in {'support', 'workflow'} and target_percent > 0:
            allowlist_slices.add(args.slice)
        if args.slice == 'public':
            allowlist_slices.discard(args.slice)

    proposed_slices = _normalize_csv(configured_slices)
    proposed_slice_rollouts = _normalize_rollouts(slice_rollouts)
    proposed_allowlist_slices = _normalize_csv(allowlist_slices)

    command = [
        'python3',
        str(REPO_ROOT / ('tools/evals/execute_framework_rollout_promotion.py' if args.apply else 'tools/evals/preflight_framework_rollout_promotion.py')),
        '--env-file',
        str(args.env_file),
        '--slices',
        proposed_slices,
        '--slice-rollouts',
        proposed_slice_rollouts,
        '--allowlist-slices',
        proposed_allowlist_slices,
    ]
    if args.candidate_engine:
        command.extend(['--candidate-engine', args.candidate_engine])
    if args.apply:
        command.extend(['--services', args.services, '--status-url', args.status_url, '--apply'])

    completed = subprocess.run(
        command,
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )

    nested_paths = [line.strip() for line in completed.stdout.splitlines() if line.strip()]
    nested_report = nested_paths[0] if nested_paths else ''
    result = 'passed' if completed.returncode == 0 else 'failed'
    operator = str(args.operator or '').strip() or getpass.getuser()
    payload = {
        'timestamp': datetime.now(UTC).isoformat(),
        'slice': args.slice,
        'before_rollout_percent': before_rollout_percent,
        'after_rollout_percent': target_percent,
        'mode': 'execute' if args.apply else 'preflight',
        'apply': args.apply,
        'result': result,
        'operator': operator,
        'reason': str(args.reason).strip(),
        'returncode': completed.returncode,
        'env_file': str(args.env_file),
        'proposed_slices': proposed_slices,
        'proposed_slice_rollouts': proposed_slice_rollouts,
        'proposed_allowlist_slices': proposed_allowlist_slices,
        'nested_report': nested_report,
        'stdout': completed.stdout,
        'stderr': completed.stderr,
    }

    _append_changelog(entry=payload, md_path=args.changelog_md, json_path=args.changelog_json)
    _write_report(report_md=args.report, report_json=args.json, artifact_json=args.artifact_json, payload=payload)

    print(args.report)
    print(args.json)
    print(args.changelog_md)
    print(args.changelog_json)
    return completed.returncode


if __name__ == '__main__':
    raise SystemExit(main())
