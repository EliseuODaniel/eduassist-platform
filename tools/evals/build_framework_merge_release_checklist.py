#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from urllib.request import urlopen

REPO_ROOT = Path(__file__).resolve().parents[2]

DEFAULT_STATUS_URL = 'http://127.0.0.1:8002/v1/status'
DEFAULT_REPORT_MD = REPO_ROOT / 'docs/architecture/framework-merge-release-checklist-report.md'
DEFAULT_REPORT_JSON = REPO_ROOT / 'docs/architecture/framework-merge-release-checklist-report.json'
DEFAULT_ARTIFACT_JSON = REPO_ROOT / 'artifacts/framework-merge-release-checklist-report.json'
RELEASE_SNAPSHOT_JSON = REPO_ROOT / 'docs/architecture/framework-release-snapshot-report.json'
CHANGELOG_JSON = REPO_ROOT / 'docs/architecture/framework-rollout-changelog.json'
READINESS_JSON = REPO_ROOT / 'docs/architecture/framework-rollout-readiness-report.json'
LIVE_SUMMARY_JSON = REPO_ROOT / 'docs/architecture/framework-live-promotion-summary-report.json'
SCORECARD_JSON = REPO_ROOT / 'docs/architecture/framework-native-scorecard.json'
GOVERNANCE_ONLY_DIFF_PATHS = {
    'docs/architecture/framework-release-snapshot-report.md',
    'docs/architecture/framework-release-snapshot-report.json',
    'docs/architecture/framework-merge-release-checklist-report.md',
    'docs/architecture/framework-merge-release-checklist-report.json',
}


def _run(cmd: list[str]) -> str:
    completed = subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True, check=True)
    return completed.stdout.strip()


def _load_json(path: Path) -> dict | list | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except Exception:
        return None


def _status_payload(url: str) -> dict:
    with urlopen(url, timeout=15) as response:
        payload = json.load(response)
    if not isinstance(payload, dict):
        raise RuntimeError('status endpoint did not return a JSON object')
    return payload


def _all_services_healthy(snapshot: dict) -> tuple[bool, str]:
    services = snapshot.get('services')
    if not isinstance(services, dict) or not services:
        return False, 'release snapshot does not contain service health.'
    unhealthy: list[str] = []
    for name, item in services.items():
        if not isinstance(item, dict):
            unhealthy.append(f'{name}:unknown')
            continue
        if not item.get('exists'):
            unhealthy.append(f'{name}:missing')
            continue
        if not item.get('running'):
            unhealthy.append(f'{name}:not-running')
            continue
        if str(item.get('health_status', '') or '') not in {'', 'healthy'}:
            unhealthy.append(f"{name}:{item.get('health_status')}")
    if unhealthy:
        return False, ', '.join(unhealthy)
    return True, 'all tracked services are healthy.'


def _changelog_normalized(rows: list[dict]) -> tuple[bool, str]:
    gaps: list[str] = []
    for item in rows:
        timestamp = str(item.get('timestamp', '') or '')
        for field in ('intent', 'operator', 'reason'):
            if not str(item.get(field, '') or '').strip():
                gaps.append(f'{timestamp}:{field}')
    if gaps:
        return False, '; '.join(gaps[:10])
    return True, 'all changelog entries contain intent, operator, and reason.'


def _snapshot_matches_head(*, release_git: dict | None, head_branch: str, head_commit: str) -> tuple[bool, str]:
    if not isinstance(release_git, dict):
        return False, 'release snapshot git block missing.'
    snapshot_branch = str(release_git.get('branch', '') or '')
    snapshot_commit = str(release_git.get('commit', '') or '')
    if snapshot_branch != head_branch:
        return False, f'snapshot branch={snapshot_branch} head branch={head_branch}'
    if snapshot_commit == head_commit:
        return True, 'snapshot commit matches HEAD exactly.'
    try:
        diff_output = _run(['git', 'diff', '--name-only', f'{snapshot_commit}..{head_commit}'])
    except Exception as exc:
        return False, f'could not diff snapshot commit to HEAD: {exc}'
    changed_paths = [line.strip() for line in diff_output.splitlines() if line.strip()]
    if changed_paths and all(path in GOVERNANCE_ONLY_DIFF_PATHS for path in changed_paths):
        return True, 'snapshot trails HEAD only by governance report files.'
    return False, 'snapshot differs from HEAD beyond governance-only report files.'


def _worktree_is_governance_only(status_short: str) -> tuple[bool, str]:
    lines = [line.rstrip() for line in str(status_short or '').splitlines() if line.strip()]
    if not lines:
        return True, 'working tree is clean.'
    paths: list[str] = []
    for line in lines:
        candidate = line[3:].strip() if len(line) >= 4 else line.strip()
        if '->' in candidate:
            candidate = candidate.split('->', 1)[1].strip()
        paths.append(candidate)
    if paths and all(path in GOVERNANCE_ONLY_DIFF_PATHS for path in paths):
        return True, 'working tree differs only by governance report files.'
    return False, status_short


def _check_items(*, status_payload: dict, snapshot: dict, changelog_rows: list[dict]) -> list[dict]:
    head_branch = _run(['git', 'rev-parse', '--abbrev-ref', 'HEAD'])
    head_commit = _run(['git', 'rev-parse', 'HEAD'])
    git_status_short = _run(['git', 'status', '--short'])
    worktree_clean_enough, worktree_detail = _worktree_is_governance_only(git_status_short)

    release_git = snapshot.get('git') if isinstance(snapshot, dict) else None
    release_posture = snapshot.get('posture') if isinstance(snapshot, dict) else None
    snapshot_matches_head, snapshot_match_detail = _snapshot_matches_head(
        release_git=release_git,
        head_branch=head_branch,
        head_commit=head_commit,
    )

    services_ok, services_detail = _all_services_healthy(snapshot if isinstance(snapshot, dict) else {})
    changelog_ok, changelog_detail = _changelog_normalized(changelog_rows)
    scorecard_gate = status_payload.get('experimentScorecardGate') if isinstance(status_payload, dict) else None
    live_summary = status_payload.get('experimentLivePromotionSummary') if isinstance(status_payload, dict) else None
    blocked_now = live_summary.get('blocked_now') if isinstance(live_summary, dict) else {}
    candidate_engine = status_payload.get('experimentPrimaryEngine', '')

    items = [
        {
            'id': 'git_clean',
            'status': 'pass' if worktree_clean_enough else 'fail',
            'detail': worktree_detail,
        },
        {
            'id': 'release_snapshot_exists',
            'status': 'pass' if isinstance(snapshot, dict) else 'fail',
            'detail': 'release snapshot JSON is present.' if isinstance(snapshot, dict) else 'release snapshot JSON missing or unreadable.',
        },
        {
            'id': 'release_snapshot_matches_head',
            'status': 'pass' if snapshot_matches_head else 'fail',
            'detail': snapshot_match_detail,
        },
        {
            'id': 'release_snapshot_ready',
            'status': 'pass' if isinstance(release_posture, dict) and release_posture.get('ready_for_guarded_release') else 'fail',
            'detail': json.dumps(release_posture or {}, ensure_ascii=False),
        },
        {
            'id': 'runtime_status_ready',
            'status': 'pass' if bool(status_payload.get('ready')) else 'fail',
            'detail': f"status.ready={status_payload.get('ready')}",
        },
        {
            'id': 'services_healthy',
            'status': 'pass' if services_ok else 'fail',
            'detail': services_detail,
        },
        {
            'id': 'scorecard_gate_loaded',
            'status': 'pass' if isinstance(scorecard_gate, dict) and scorecard_gate.get('loaded') else 'fail',
            'detail': json.dumps(scorecard_gate or {}, ensure_ascii=False),
        },
        {
            'id': 'primary_stack_native_path_passed',
            'status': 'pass' if isinstance(scorecard_gate, dict) and scorecard_gate.get('primary_stack_native_path_passed') else 'fail',
            'detail': f"primary_stack_native_path_passed={bool(isinstance(scorecard_gate, dict) and scorecard_gate.get('primary_stack_native_path_passed'))}",
        },
        {
            'id': 'live_promotion_summary_present',
            'status': 'pass' if isinstance(live_summary, dict) else 'fail',
            'detail': 'experimentLivePromotionSummary available.' if isinstance(live_summary, dict) else 'missing from /v1/status.',
        },
        {
            'id': 'changelog_normalized',
            'status': 'pass' if changelog_ok else 'fail',
            'detail': changelog_detail,
        },
        {
            'id': 'protected_blocked_for_crewai_candidate',
            'status': 'pass'
            if str(candidate_engine).strip().lower() != 'crewai'
            or (isinstance(blocked_now, dict) and 'protected' in blocked_now)
            else 'fail',
            'detail': 'protected remains blocked for crewai candidate engine.'
            if str(candidate_engine).strip().lower() == 'crewai'
            else 'not applicable to current candidate engine.',
        },
        {
            'id': 'core_artifacts_present',
            'status': 'pass'
            if all(path.exists() for path in (READINESS_JSON, LIVE_SUMMARY_JSON, SCORECARD_JSON, RELEASE_SNAPSHOT_JSON))
            else 'fail',
            'detail': ', '.join(
                f'{path.name}={"yes" if path.exists() else "no"}'
                for path in (READINESS_JSON, LIVE_SUMMARY_JSON, SCORECARD_JSON, RELEASE_SNAPSHOT_JSON)
            ),
        },
    ]
    return items


def _write_report(*, report_md: Path, report_json: Path, artifact_json: Path, payload: dict) -> None:
    lines = [
        '# Framework Merge Release Checklist Report',
        '',
        f"Date: {payload['generated_at']}",
        '',
        '## Summary',
        '',
        f"- classification: `{payload['classification']}`",
        f"- ready to merge/release: `{payload['ready_to_merge_or_release']}`",
        f"- passed checks: `{payload['passed_checks']}`",
        f"- failed checks: `{payload['failed_checks']}`",
        '',
        '## Checklist',
        '',
        '| Item | Status | Detail |',
        '| --- | --- | --- |',
    ]
    for item in payload['checks']:
        lines.append(f"| `{item['id']}` | `{item['status']}` | {item['detail']} |")
    if payload.get('blocking_items'):
        lines.extend(['', '## Blocking Items', ''])
        for item in payload['blocking_items']:
            lines.append(f"- `{item['id']}`: {item['detail']}")

    report_md.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    json_text = json.dumps(payload, ensure_ascii=False, indent=2) + '\n'
    report_json.write_text(json_text, encoding='utf-8')
    artifact_json.parent.mkdir(parents=True, exist_ok=True)
    artifact_json.write_text(json_text, encoding='utf-8')


def main() -> int:
    status_payload = _status_payload(DEFAULT_STATUS_URL)
    snapshot = _load_json(RELEASE_SNAPSHOT_JSON)
    changelog_rows = _load_json(CHANGELOG_JSON)
    if not isinstance(changelog_rows, list):
        changelog_rows = []
    changelog_rows = [item for item in changelog_rows if isinstance(item, dict)]

    checks = _check_items(status_payload=status_payload, snapshot=snapshot if isinstance(snapshot, dict) else {}, changelog_rows=changelog_rows)
    failed = [item for item in checks if item['status'] != 'pass']
    payload = {
        'generated_at': datetime.now(UTC).isoformat(),
        'classification': 'ready' if not failed else 'blocked',
        'ready_to_merge_or_release': not failed,
        'passed_checks': len(checks) - len(failed),
        'failed_checks': len(failed),
        'checks': checks,
        'blocking_items': failed,
    }
    _write_report(report_md=DEFAULT_REPORT_MD, report_json=DEFAULT_REPORT_JSON, artifact_json=DEFAULT_ARTIFACT_JSON, payload=payload)
    print(DEFAULT_REPORT_MD)
    print(DEFAULT_REPORT_JSON)
    print(DEFAULT_ARTIFACT_JSON)
    return 0 if not failed else 1


if __name__ == '__main__':
    raise SystemExit(main())
