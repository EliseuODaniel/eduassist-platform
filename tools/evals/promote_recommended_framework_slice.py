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
APP_SRC = REPO_ROOT / 'apps/ai-orchestrator/src'
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
if str(APP_SRC) not in sys.path:
    sys.path.insert(0, str(APP_SRC))

from ai_orchestrator.engine_selector import get_experiment_live_promotion_summary  # noqa: E402
from tools.evals.apply_framework_rollout_promotion import _build_settings  # noqa: E402
from tools.evals.promote_framework_slice import DEFAULT_CHANGELOG_JSON, DEFAULT_CHANGELOG_MD  # noqa: E402

DEFAULT_ENV_FILE = REPO_ROOT / '.env'
DEFAULT_REPORT_MD = REPO_ROOT / 'docs/architecture/framework-recommended-slice-promotion-report.md'
DEFAULT_REPORT_JSON = REPO_ROOT / 'docs/architecture/framework-recommended-slice-promotion-report.json'
DEFAULT_ARTIFACT_JSON = REPO_ROOT / 'artifacts/framework-recommended-slice-promotion-report.json'
PROMOTION_LADDER = [1, 2, 5, 10, 25, 50, 100]
PROMOTABLE_ACTIONS = {'expand_gradually', 'start_tiny_rollout', 'start_controlled_canary', 'activate_configured_slice'}
SLICE_PRIORITY = ['public', 'support', 'workflow', 'protected']


def _recommended_target(*, slice_name: str, action: str, current_percent: int) -> int:
    current = max(0, min(100, int(current_percent)))
    if action == 'expand_gradually':
        for candidate in PROMOTION_LADDER:
            if candidate > current:
                return candidate
        return 100
    if action == 'start_tiny_rollout':
        return 1
    if action == 'start_controlled_canary':
        return 100
    if action == 'activate_configured_slice':
        if current > 0:
            return current
        return 100 if slice_name in {'support', 'workflow'} else 1
    raise RuntimeError(f'No promotion target is defined for action {action!r}.')


def _select_slice(*, requested_slice: str, advisory_by_slice: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    if requested_slice != 'auto':
        payload = advisory_by_slice.get(requested_slice)
        if not isinstance(payload, dict):
            raise RuntimeError(f'Slice {requested_slice!r} is not present in the live promotion summary.')
        return requested_slice, payload

    for slice_name in SLICE_PRIORITY:
        payload = advisory_by_slice.get(slice_name)
        if not isinstance(payload, dict):
            continue
        if str(payload.get('action', '') or '') in PROMOTABLE_ACTIONS:
            return slice_name, payload
    raise RuntimeError('No promotable slice is currently recommended by the live promotion summary.')


def _write_report(*, report_md: Path, report_json: Path, artifact_json: Path, payload: dict[str, Any]) -> None:
    lines = [
        '# Framework Recommended Slice Promotion Report',
        '',
        f"Date: {payload['timestamp']}",
        '',
        '## Summary',
        '',
        f"- candidate engine: `{payload['candidate_engine']}`",
        f"- selected slice: `{payload['selected_slice']}`",
        f"- advisory action: `{payload['advisory_action']}`",
        f"- current rollout: `{payload['current_rollout_percent']}%`",
        f"- recommended rollout: `{payload['recommended_rollout_percent']}%`",
        f"- apply requested: `{payload['apply']}`",
        f"- operator: `{payload['operator']}`",
        f"- reason: `{payload['reason']}`",
        f"- nested report: `{payload['nested_report']}`",
    ]
    if payload.get('blocked_reasons'):
        lines.extend(['', '## Advisory Blocked Reasons', ''])
        for item in payload['blocked_reasons']:
            lines.append(f'- {item}')
    if payload.get('stderr'):
        lines.extend(['', '## STDERR', '', '```text', str(payload['stderr']), '```'])
    report_md.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    json_text = json.dumps(payload, ensure_ascii=False, indent=2) + '\n'
    report_json.write_text(json_text, encoding='utf-8')
    artifact_json.parent.mkdir(parents=True, exist_ok=True)
    artifact_json.write_text(json_text, encoding='utf-8')


def main() -> int:
    parser = argparse.ArgumentParser(description='Promote the slice currently recommended by the live experiment summary.')
    parser.add_argument('--slice', default='auto', choices=['auto', 'public', 'protected', 'support', 'workflow'])
    parser.add_argument('--reason', required=True)
    parser.add_argument('--operator', default='')
    parser.add_argument('--env-file', type=Path, default=DEFAULT_ENV_FILE)
    parser.add_argument('--candidate-engine', default=None)
    parser.add_argument('--allowlist-mode', choices=['auto', 'keep', 'add', 'remove'], default='auto')
    parser.add_argument('--services', default='ai-orchestrator')
    parser.add_argument('--status-url', default='http://127.0.0.1:8002/v1/status')
    parser.add_argument('--apply', action='store_true')
    parser.add_argument('--changelog-md', type=Path, default=DEFAULT_CHANGELOG_MD)
    parser.add_argument('--changelog-json', type=Path, default=DEFAULT_CHANGELOG_JSON)
    parser.add_argument('--report', type=Path, default=DEFAULT_REPORT_MD)
    parser.add_argument('--json', type=Path, default=DEFAULT_REPORT_JSON)
    parser.add_argument('--artifact-json', type=Path, default=DEFAULT_ARTIFACT_JSON)
    args = parser.parse_args()

    settings = _build_settings(args.env_file)
    if args.candidate_engine:
        settings.orchestrator_experiment_primary_engine = str(args.candidate_engine).strip()

    summary = get_experiment_live_promotion_summary(settings=settings)
    advisory_by_slice = summary.get('advisory_by_slice')
    if not isinstance(advisory_by_slice, dict):
        raise RuntimeError('Live promotion summary does not include advisory_by_slice.')

    selected_slice, advisory = _select_slice(requested_slice=args.slice, advisory_by_slice=advisory_by_slice)
    advisory_action = str(advisory.get('action', '') or '')
    if advisory_action not in PROMOTABLE_ACTIONS:
        raise RuntimeError(f'Slice {selected_slice!r} is currently {advisory_action!r}, not promotable.')

    current_rollout_percent = int(advisory.get('configured_rollout_percent', 0) or 0)
    recommended_rollout_percent = _recommended_target(
        slice_name=selected_slice,
        action=advisory_action,
        current_percent=current_rollout_percent,
    )

    command = [
        'python3',
        str(REPO_ROOT / 'tools/evals/promote_framework_slice.py'),
        '--slice',
        selected_slice,
        '--to-rollout-percent',
        str(recommended_rollout_percent),
        '--reason',
        args.reason,
        '--operator',
        str(args.operator or ''),
        '--env-file',
        str(args.env_file),
        '--allowlist-mode',
        args.allowlist_mode,
        '--changelog-md',
        str(args.changelog_md),
        '--changelog-json',
        str(args.changelog_json),
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
        'candidate_engine': summary.get('candidate_engine'),
        'selected_slice': selected_slice,
        'advisory_action': advisory_action,
        'current_rollout_percent': current_rollout_percent,
        'recommended_rollout_percent': recommended_rollout_percent,
        'apply': args.apply,
        'operator': str(args.operator or '').strip(),
        'reason': str(args.reason).strip(),
        'blocked_reasons': advisory.get('blocked_reasons', []),
        'nested_report': nested_report,
        'stdout': completed.stdout,
        'stderr': completed.stderr,
        'returncode': completed.returncode,
        'live_summary_excerpt': {
            'promotable_now': summary.get('promotable_now'),
            'maintain_now': summary.get('maintain_now'),
            'blocked_now': summary.get('blocked_now'),
        },
    }
    _write_report(report_md=args.report, report_json=args.json, artifact_json=args.artifact_json, payload=payload)
    print(args.report)
    print(args.json)
    print(args.artifact_json)
    return completed.returncode


if __name__ == '__main__':
    raise SystemExit(main())
