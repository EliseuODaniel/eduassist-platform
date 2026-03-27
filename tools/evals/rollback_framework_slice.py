#!/usr/bin/env python3
from __future__ import annotations

import argparse
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
DEFAULT_CHANGELOG_JSON = REPO_ROOT / 'docs/architecture/framework-rollout-changelog.json'
DEFAULT_REPORT_MD = REPO_ROOT / 'docs/architecture/framework-slice-rollback-report.md'
DEFAULT_REPORT_JSON = REPO_ROOT / 'docs/architecture/framework-slice-rollback-report.json'
DEFAULT_ARTIFACT_JSON = REPO_ROOT / 'artifacts/framework-slice-rollback-report.json'


def _load_changelog(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    try:
        payload = json.loads(path.read_text(encoding='utf-8'))
    except Exception:
        return []
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]
    return []


def _resolve_target_percent(
    *,
    slice_name: str,
    current_percent: int,
    changelog_path: Path,
    explicit_target: int | None,
    allow_preflight_fallback: bool,
) -> tuple[int, dict[str, Any] | None]:
    if explicit_target is not None:
        return max(0, min(100, int(explicit_target))), None

    rows = _load_changelog(changelog_path)
    for entry in reversed(rows):
        if str(entry.get('slice', '') or '') != slice_name:
            continue
        if str(entry.get('result', '') or '') != 'passed':
            continue
        if str(entry.get('intent', 'promotion') or 'promotion') == 'rollback':
            continue
        if bool(entry.get('apply')) or allow_preflight_fallback:
            before_percent = int(entry.get('before_rollout_percent', current_percent) or current_percent)
            return max(0, min(100, before_percent)), entry
    raise RuntimeError(
        f'No suitable changelog entry found for slice {slice_name!r}. '
        'Pass --to-rollout-percent explicitly or allow fallback to preflight history.'
    )


def _write_report(*, report_md: Path, report_json: Path, artifact_json: Path, payload: dict[str, Any]) -> None:
    lines = [
        '# Framework Slice Rollback Report',
        '',
        f"Date: {payload['timestamp']}",
        '',
        '## Summary',
        '',
        f"- slice: `{payload['slice']}`",
        f"- current rollout: `{payload['current_rollout_percent']}%`",
        f"- rollback target: `{payload['target_rollout_percent']}%`",
        f"- apply requested: `{payload['apply']}`",
        f"- result: `{payload['result']}`",
        f"- operator: `{payload['operator']}`",
        f"- reason: `{payload['reason']}`",
        f"- source: `{payload['target_source']}`",
        f"- env file: `{payload['env_file']}`",
        f"- nested promotion report: `{payload['nested_report']}`",
    ]
    if payload.get('history_reference'):
        lines.extend(
            [
                '',
                '## History Reference',
                '',
                '```json',
                json.dumps(payload['history_reference'], ensure_ascii=False, indent=2),
                '```',
            ]
        )
    if payload.get('stderr'):
        lines.extend(['', '## STDERR', '', '```text', str(payload['stderr']), '```'])
    report_md.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    json_text = json.dumps(payload, ensure_ascii=False, indent=2) + '\n'
    report_json.write_text(json_text, encoding='utf-8')
    artifact_json.parent.mkdir(parents=True, exist_ok=True)
    artifact_json.write_text(json_text, encoding='utf-8')


def main() -> int:
    parser = argparse.ArgumentParser(description='Rollback a rollout slice through the same audited promotion path.')
    parser.add_argument('--slice', required=True, choices=['public', 'protected', 'support', 'workflow'])
    parser.add_argument('--reason', required=True)
    parser.add_argument('--operator', default='')
    parser.add_argument('--env-file', type=Path, default=DEFAULT_ENV_FILE)
    parser.add_argument('--candidate-engine', default=None)
    parser.add_argument('--services', default='ai-orchestrator')
    parser.add_argument('--status-url', default='http://127.0.0.1:8002/v1/status')
    parser.add_argument('--allowlist-mode', choices=['auto', 'keep', 'add', 'remove'], default='auto')
    parser.add_argument('--to-rollout-percent', type=int, default=None)
    parser.add_argument('--allow-preflight-fallback', action='store_true')
    parser.add_argument('--apply', action='store_true')
    parser.add_argument('--changelog-json', type=Path, default=DEFAULT_CHANGELOG_JSON)
    parser.add_argument('--report', type=Path, default=DEFAULT_REPORT_MD)
    parser.add_argument('--json', type=Path, default=DEFAULT_REPORT_JSON)
    parser.add_argument('--artifact-json', type=Path, default=DEFAULT_ARTIFACT_JSON)
    args = parser.parse_args()

    settings = _build_settings(args.env_file)
    slice_rollouts = _parse_slice_rollouts(getattr(settings, 'orchestrator_experiment_slice_rollouts', ''))
    current_percent = int(slice_rollouts.get(args.slice, getattr(settings, 'orchestrator_experiment_rollout_percent', 0) or 0))
    target_percent, history_reference = _resolve_target_percent(
        slice_name=args.slice,
        current_percent=current_percent,
        changelog_path=args.changelog_json,
        explicit_target=args.to_rollout_percent,
        allow_preflight_fallback=args.allow_preflight_fallback,
    )

    command = [
        'python3',
        str(REPO_ROOT / 'tools/evals/promote_framework_slice.py'),
        '--intent',
        'rollback',
        '--slice',
        args.slice,
        '--to-rollout-percent',
        str(target_percent),
        '--reason',
        args.reason,
        '--operator',
        args.operator,
        '--env-file',
        str(args.env_file),
        '--allowlist-mode',
        args.allowlist_mode,
    ]
    if args.candidate_engine:
        command.extend(['--candidate-engine', args.candidate_engine])
    if args.apply:
        command.extend(['--services', args.services, '--status-url', args.status_url, '--apply'])

    completed = subprocess.run(command, cwd=REPO_ROOT, capture_output=True, text=True)
    nested_paths = [line.strip() for line in completed.stdout.splitlines() if line.strip()]
    nested_report = nested_paths[0] if nested_paths else ''
    payload = {
        'timestamp': datetime.now(UTC).isoformat(),
        'slice': args.slice,
        'current_rollout_percent': current_percent,
        'target_rollout_percent': target_percent,
        'apply': args.apply,
        'result': 'passed' if completed.returncode == 0 else 'failed',
        'operator': args.operator or '',
        'reason': str(args.reason).strip(),
        'target_source': 'explicit' if args.to_rollout_percent is not None else 'history',
        'history_reference': history_reference,
        'env_file': str(args.env_file),
        'nested_report': nested_report,
        'stdout': completed.stdout,
        'stderr': completed.stderr,
        'returncode': completed.returncode,
    }
    _write_report(report_md=args.report, report_json=args.json, artifact_json=args.artifact_json, payload=payload)
    print(args.report)
    print(args.json)
    return completed.returncode


if __name__ == '__main__':
    raise SystemExit(main())
