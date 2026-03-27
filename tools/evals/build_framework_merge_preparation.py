#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
from datetime import UTC, datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

DEFAULT_TARGET_BRANCH = 'origin/main'
DEFAULT_REPORT_MD = REPO_ROOT / 'docs/architecture/framework-merge-preparation-report.md'
DEFAULT_REPORT_JSON = REPO_ROOT / 'docs/architecture/framework-merge-preparation-report.json'
DEFAULT_ARTIFACT_JSON = REPO_ROOT / 'artifacts/framework-merge-preparation-report.json'
RELEASE_SNAPSHOT_JSON = REPO_ROOT / 'docs/architecture/framework-release-snapshot-report.json'
CHECKLIST_JSON = REPO_ROOT / 'docs/architecture/framework-merge-release-checklist-report.json'


def _run(cmd: list[str]) -> str:
    completed = subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True, check=True)
    return completed.stdout.strip()


def _load_json(path: Path):
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except Exception:
        return None


def _target_branch(default_target: str) -> str:
    try:
        remote_head = _run(['git', 'symbolic-ref', 'refs/remotes/origin/HEAD'])
    except Exception:
        return default_target
    if remote_head.startswith('refs/remotes/'):
        return remote_head.removeprefix('refs/remotes/')
    return default_target


def _write_report(*, report_md: Path, report_json: Path, artifact_json: Path, payload: dict) -> None:
    lines = [
        '# Framework Merge Preparation Report',
        '',
        f"Date: {payload['generated_at']}",
        '',
        '## Summary',
        '',
        f"- classification: `{payload['classification']}`",
        f"- merge-ready: `{payload['merge_ready']}`",
        f"- source branch: `{payload['source_branch']}`",
        f"- target branch: `{payload['target_branch']}`",
        f"- ahead of target: `{payload['ahead_count']}` commits",
        f"- behind target: `{payload['behind_count']}` commits",
        '',
        '## Preconditions',
        '',
        f"- release snapshot ready: `{payload['release_snapshot_ready']}`",
        f"- merge checklist ready: `{payload['merge_checklist_ready']}`",
        f"- working tree clean: `{payload['working_tree_clean']}`",
        '',
        '## Diff Summary',
        '',
        '```text',
        payload['diff_stat'],
        '```',
        '',
        '## Recommended Next Actions',
        '',
    ]
    for item in payload['recommended_actions']:
        lines.append(f'- {item}')
    if payload.get('blocking_items'):
        lines.extend(['', '## Blocking Items', ''])
        for item in payload['blocking_items']:
            lines.append(f'- {item}')

    report_md.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    json_text = json.dumps(payload, ensure_ascii=False, indent=2) + '\n'
    report_json.write_text(json_text, encoding='utf-8')
    artifact_json.parent.mkdir(parents=True, exist_ok=True)
    artifact_json.write_text(json_text, encoding='utf-8')


def main() -> int:
    parser = argparse.ArgumentParser(description='Build a merge-preparation report for the dual-stack rollout branch.')
    parser.add_argument('--target-branch', default=DEFAULT_TARGET_BRANCH)
    args = parser.parse_args()

    source_branch = _run(['git', 'rev-parse', '--abbrev-ref', 'HEAD'])
    target_branch = _target_branch(args.target_branch)
    release_snapshot = _load_json(RELEASE_SNAPSHOT_JSON)
    merge_checklist = _load_json(CHECKLIST_JSON)
    git_status = _run(['git', 'status', '--short'])
    ahead_count = int(_run(['git', 'rev-list', '--count', f'{target_branch}..HEAD']) or '0')
    behind_count = int(_run(['git', 'rev-list', '--count', f'HEAD..{target_branch}']) or '0')
    diff_stat = _run(['git', 'diff', '--stat', f'{target_branch}...HEAD']) or '(no diff)'

    release_snapshot_ready = bool(isinstance(release_snapshot, dict) and release_snapshot.get('posture', {}).get('ready_for_guarded_release'))
    merge_checklist_ready = bool(isinstance(merge_checklist, dict) and merge_checklist.get('ready_to_merge_or_release'))
    working_tree_clean = not bool(git_status.strip())

    blocking_items: list[str] = []
    if not release_snapshot_ready:
        blocking_items.append('release snapshot is not ready')
    if not merge_checklist_ready:
        blocking_items.append('merge/release checklist is not ready')
    if not working_tree_clean:
        blocking_items.append('working tree is not clean')
    if behind_count > 0:
        blocking_items.append(f'branch is behind {target_branch} by {behind_count} commits')

    recommended_actions: list[str] = []
    if behind_count > 0:
        recommended_actions.append(f'rebase or merge {target_branch} before opening a final merge.')
    if blocking_items:
        recommended_actions.append('keep using the guarded rollout path until the blocking items are cleared.')
    else:
        recommended_actions.append(f'open or finalize the merge from `{source_branch}` into `{target_branch}`.')
        recommended_actions.append('keep protected blocked unless a separate protected promotion decision is made later.')

    payload = {
        'generated_at': datetime.now(UTC).isoformat(),
        'classification': 'ready' if not blocking_items else 'blocked',
        'merge_ready': not blocking_items,
        'source_branch': source_branch,
        'target_branch': target_branch,
        'ahead_count': ahead_count,
        'behind_count': behind_count,
        'release_snapshot_ready': release_snapshot_ready,
        'merge_checklist_ready': merge_checklist_ready,
        'working_tree_clean': working_tree_clean,
        'diff_stat': diff_stat,
        'recommended_actions': recommended_actions,
        'blocking_items': blocking_items,
    }
    _write_report(report_md=DEFAULT_REPORT_MD, report_json=DEFAULT_REPORT_JSON, artifact_json=DEFAULT_ARTIFACT_JSON, payload=payload)
    print(DEFAULT_REPORT_MD)
    print(DEFAULT_REPORT_JSON)
    print(DEFAULT_ARTIFACT_JSON)
    return 0 if not blocking_items else 1


if __name__ == '__main__':
    raise SystemExit(main())
