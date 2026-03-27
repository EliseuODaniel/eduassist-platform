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
LEGACY_OPERATOR = 'legacy-unknown'
LEGACY_REASON = 'Legacy changelog entry normalized after operator/reason became required audit fields.'


def _configured_slice_set(value: str | None) -> set[str]:
    return {item.strip() for item in str(value or '').split(',') if item.strip()}


def _normalize_rollouts(mapping: dict[str, int]) -> str:
    items = sorted((name, percent) for name, percent in mapping.items() if percent > 0)
    return ','.join(f'{name}:{percent}' for name, percent in items)


def _normalize_csv(values: set[str]) -> str:
    return ','.join(sorted(item for item in values if item))


def _resolved_candidate_engine(*, requested_candidate_engine: str | None, settings: Any) -> str:
    requested = str(requested_candidate_engine or '').strip().lower()
    if requested:
        return requested
    return str(getattr(settings, 'orchestrator_experiment_primary_engine', 'crewai') or 'crewai').strip().lower()


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


def _infer_intent(entry: dict[str, Any]) -> str:
    raw_intent = str(entry.get('intent', '') or '').strip().lower()
    if raw_intent in {'promotion', 'rollback'}:
        return raw_intent
    try:
        before_percent = int(entry.get('before_rollout_percent', 0) or 0)
        after_percent = int(entry.get('after_rollout_percent', 0) or 0)
    except Exception:
        return 'promotion'
    return 'rollback' if after_percent < before_percent else 'promotion'


def _normalize_changelog_entry(entry: dict[str, Any], *, normalized_at: str | None = None) -> tuple[dict[str, Any], bool]:
    row = dict(entry)
    changed = False
    normalized_fields = set(str(item).strip() for item in row.get('normalized_legacy_fields', []) if str(item).strip())

    if not str(row.get('intent', '') or '').strip():
        row['intent'] = _infer_intent(row)
        normalized_fields.add('intent')
        changed = True

    if not str(row.get('operator', '') or '').strip():
        row['operator'] = LEGACY_OPERATOR
        normalized_fields.add('operator')
        changed = True

    if not str(row.get('reason', '') or '').strip():
        row['reason'] = LEGACY_REASON
        normalized_fields.add('reason')
        changed = True

    if changed:
        row['normalized_legacy_fields'] = sorted(normalized_fields)
        row['normalized_legacy_at'] = str(normalized_at or row.get('normalized_legacy_at') or datetime.now(UTC).isoformat())

    return row, changed


def _normalize_changelog_rows(rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], int]:
    normalized_at = datetime.now(UTC).isoformat()
    normalized_rows: list[dict[str, Any]] = []
    changed_count = 0
    for row in rows:
        normalized_row, changed = _normalize_changelog_entry(row, normalized_at=normalized_at)
        normalized_rows.append(normalized_row)
        if changed:
            changed_count += 1
    return normalized_rows, changed_count


def _write_changelog(*, rows: list[dict[str, Any]], md_path: Path, json_path: Path) -> None:
    json_path.write_text(json.dumps(rows, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

    lines = [
        '# Framework Rollout Changelog',
        '',
        '| Date | Intent | Slice | Before | After | Mode | Result | Operator | Reason | Env File |',
        '| --- | --- | --- | ---: | ---: | --- | --- | --- | --- | --- |',
    ]
    for item in reversed(rows[-50:]):
        lines.append(
            f"| `{item.get('timestamp', '')}` | `{item.get('intent', 'promotion')}` | `{item.get('slice', '')}` | "
            f"`{item.get('before_rollout_percent', '')}%` | `{item.get('after_rollout_percent', '')}%` | "
            f"`{item.get('mode', '')}` | `{item.get('result', '')}` | "
            f"`{item.get('operator', '')}` | {item.get('reason', '')} | `{item.get('env_file', '')}` |"
        )
    md_path.write_text('\n'.join(lines) + '\n', encoding='utf-8')


def _append_changelog(*, entry: dict[str, Any], md_path: Path, json_path: Path) -> None:
    rows = _load_json_array(json_path)
    rows, _ = _normalize_changelog_rows(rows)
    normalized_entry, _ = _normalize_changelog_entry(entry)
    rows.append(normalized_entry)
    _write_changelog(rows=rows, md_path=md_path, json_path=json_path)


def _write_report(*, report_md: Path, report_json: Path, artifact_json: Path, payload: dict[str, Any]) -> None:
    lines = [
        '# Framework Slice Promotion Report',
        '',
        f"Date: {payload['timestamp']}",
        '',
        '## Summary',
        '',
        f"- intent: `{payload['intent']}`",
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
        f"- proposed telegram chat allowlist: `{payload.get('proposed_telegram_chat_allowlist', '')}`",
        f"- proposed conversation allowlist: `{payload.get('proposed_conversation_allowlist', '')}`",
        f"- proposed CrewAI protected user-traffic HITL: `{payload.get('proposed_crewai_hitl_user_traffic_enabled')}`",
        f"- proposed CrewAI HITL slices: `{payload.get('proposed_crewai_hitl_user_traffic_slices', '')}`",
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
    parser.add_argument('--intent', choices=['promotion', 'rollback'], default='promotion')
    parser.add_argument('--slice', required=True, choices=['public', 'protected', 'support', 'workflow'])
    parser.add_argument('--to-rollout-percent', required=True, type=int)
    parser.add_argument('--reason', required=True)
    parser.add_argument('--operator', default='')
    parser.add_argument('--env-file', type=Path, default=DEFAULT_ENV_FILE)
    parser.add_argument('--candidate-engine', default=None)
    parser.add_argument('--services', default='ai-orchestrator')
    parser.add_argument('--status-url', default='http://127.0.0.1:8002/v1/status')
    parser.add_argument('--allowlist-mode', choices=['auto', 'keep', 'add', 'remove'], default='auto')
    parser.add_argument('--protected-hitl-mode', choices=['auto', 'keep', 'enable', 'disable'], default='auto')
    parser.add_argument('--telegram-chat-allowlist', default=None)
    parser.add_argument('--conversation-allowlist', default=None)
    parser.add_argument('--apply', action='store_true')
    parser.add_argument('--changelog-md', type=Path, default=DEFAULT_CHANGELOG_MD)
    parser.add_argument('--changelog-json', type=Path, default=DEFAULT_CHANGELOG_JSON)
    parser.add_argument('--report', type=Path, default=DEFAULT_REPORT_MD)
    parser.add_argument('--json', type=Path, default=DEFAULT_REPORT_JSON)
    parser.add_argument('--artifact-json', type=Path, default=DEFAULT_ARTIFACT_JSON)
    args = parser.parse_args()

    settings = _build_settings(args.env_file)
    candidate_engine = _resolved_candidate_engine(requested_candidate_engine=args.candidate_engine, settings=settings)
    slice_rollouts = _parse_slice_rollouts(getattr(settings, 'orchestrator_experiment_slice_rollouts', ''))
    configured_slices = _configured_slice_set(getattr(settings, 'orchestrator_experiment_slices', ''))
    allowlist_slices = _configured_slice_set(getattr(settings, 'orchestrator_experiment_allowlist_slices', ''))
    telegram_chat_allowlist = _configured_slice_set(getattr(settings, 'orchestrator_experiment_telegram_chat_allowlist', ''))
    conversation_allowlist = _configured_slice_set(getattr(settings, 'orchestrator_experiment_conversation_allowlist', ''))
    crewai_hitl_user_traffic_slices = _configured_slice_set(getattr(settings, 'crewai_hitl_user_traffic_slices', ''))
    crewai_hitl_user_traffic_enabled = bool(getattr(settings, 'crewai_hitl_user_traffic_enabled', False))

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
        if args.slice == 'protected':
            if target_percent > 0:
                allowlist_slices.add('protected')
            else:
                allowlist_slices.discard('protected')

    if args.telegram_chat_allowlist is not None:
        telegram_chat_allowlist = _configured_slice_set(args.telegram_chat_allowlist)
    if args.conversation_allowlist is not None:
        conversation_allowlist = _configured_slice_set(args.conversation_allowlist)

    if args.slice == 'protected' and candidate_engine == 'crewai':
        protected_hitl_mode = args.protected_hitl_mode
        if protected_hitl_mode in {'auto', 'enable'} and target_percent > 0:
            crewai_hitl_user_traffic_enabled = True
            crewai_hitl_user_traffic_slices.add('protected')
        elif protected_hitl_mode in {'auto', 'disable'} and target_percent <= 0:
            crewai_hitl_user_traffic_slices.discard('protected')
            crewai_hitl_user_traffic_enabled = bool(crewai_hitl_user_traffic_slices)

    proposed_slices = _normalize_csv(configured_slices)
    proposed_slice_rollouts = _normalize_rollouts(slice_rollouts)
    proposed_allowlist_slices = _normalize_csv(allowlist_slices)
    proposed_telegram_chat_allowlist = _normalize_csv(telegram_chat_allowlist)
    proposed_conversation_allowlist = _normalize_csv(conversation_allowlist)
    proposed_crewai_hitl_user_traffic_slices = _normalize_csv(crewai_hitl_user_traffic_slices)

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
        '--telegram-chat-allowlist',
        proposed_telegram_chat_allowlist,
        '--conversation-allowlist',
        proposed_conversation_allowlist,
        '--crewai-hitl-user-traffic-slices',
        proposed_crewai_hitl_user_traffic_slices,
    ]
    command.append('--crewai-hitl-user-traffic-enabled' if crewai_hitl_user_traffic_enabled else '--no-crewai-hitl-user-traffic-enabled')
    if args.candidate_engine:
        command.extend(['--candidate-engine', args.candidate_engine])
    if args.apply:
        services = [item.strip() for item in str(args.services).split(',') if item.strip()]
        if args.slice == 'protected' and candidate_engine == 'crewai' and 'ai-orchestrator-crewai' not in services:
            services.append('ai-orchestrator-crewai')
        command.extend(['--services', ','.join(services), '--status-url', args.status_url, '--apply'])

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
        'intent': args.intent,
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
        'proposed_telegram_chat_allowlist': proposed_telegram_chat_allowlist,
        'proposed_conversation_allowlist': proposed_conversation_allowlist,
        'proposed_crewai_hitl_user_traffic_enabled': crewai_hitl_user_traffic_enabled,
        'proposed_crewai_hitl_user_traffic_slices': proposed_crewai_hitl_user_traffic_slices,
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
