#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib.request import urlopen

REPO_ROOT = Path(__file__).resolve().parents[2]

DEFAULT_STATUS_URL = 'http://127.0.0.1:8002/v1/status'
DEFAULT_REPORT = REPO_ROOT / 'docs/architecture/framework-release-snapshot-report.md'
DEFAULT_JSON = REPO_ROOT / 'docs/architecture/framework-release-snapshot-report.json'
DEFAULT_ARTIFACT_JSON = REPO_ROOT / 'artifacts/framework-release-snapshot-report.json'
CHANGELOG_JSON = REPO_ROOT / 'docs/architecture/framework-rollout-changelog.json'

SERVICE_CONTAINERS = {
    'ai-orchestrator': 'eduassist-ai-orchestrator',
    'ai-orchestrator-crewai': 'eduassist-ai-orchestrator-crewai',
    'api-core': 'eduassist-api-core',
    'telegram-gateway': 'eduassist-telegram-gateway',
}


def _run(cmd: list[str]) -> str:
    completed = subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True, check=True)
    return completed.stdout.strip()


def _git_snapshot() -> dict[str, Any]:
    branch = _run(['git', 'rev-parse', '--abbrev-ref', 'HEAD'])
    commit = _run(['git', 'rev-parse', 'HEAD'])
    status = _run(['git', 'status', '--short'])
    return {
        'branch': branch,
        'commit': commit,
        'working_tree_clean': not bool(status.strip()),
        'status_short': status,
    }


def _service_health(container_name: str) -> dict[str, Any]:
    try:
        payload = _run(
            [
                'docker',
                'inspect',
                '-f',
                '{{json .State}}',
                container_name,
            ]
        )
        state = json.loads(payload)
    except Exception as exc:  # pragma: no cover - operational fallback
        return {'exists': False, 'error': str(exc)}

    health = state.get('Health') if isinstance(state, dict) else None
    return {
        'exists': True,
        'running': bool(isinstance(state, dict) and state.get('Running')),
        'status': str(state.get('Status', '') if isinstance(state, dict) else ''),
        'health_status': str(health.get('Status', '') if isinstance(health, dict) else ''),
    }


def _status_payload(url: str) -> dict[str, Any]:
    with urlopen(url, timeout=15) as response:
        payload = json.load(response)
    if not isinstance(payload, dict):
        raise RuntimeError('status endpoint did not return a JSON object')
    return payload


def _load_json(path: Path) -> Any:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except Exception:
        return None


def _latest_changelog_entries(limit: int = 5) -> list[dict[str, Any]]:
    payload = _load_json(CHANGELOG_JSON)
    if not isinstance(payload, list):
        return []
    rows = [item for item in payload if isinstance(item, dict)]
    return list(reversed(rows[-limit:]))


def _release_posture(*, git_snapshot: dict[str, Any], status_payload: dict[str, Any], services: dict[str, Any]) -> dict[str, Any]:
    live_summary = status_payload.get('experimentLivePromotionSummary')
    readiness = status_payload.get('experimentRolloutReadiness')
    errors: list[str] = []

    if not git_snapshot.get('working_tree_clean'):
        errors.append('working tree is not clean')
    if not bool(status_payload.get('ready')):
        errors.append('ai-orchestrator status is not ready')
    for name, health in services.items():
        if not bool(health.get('exists')):
            errors.append(f'{name} container is missing')
            continue
        if not bool(health.get('running')):
            errors.append(f'{name} container is not running')
        if health.get('health_status') not in {'', 'healthy'}:
            errors.append(f'{name} health is {health.get("health_status")}')

    configured_live_slices: list[str] = []
    if isinstance(readiness, dict):
        per_slice = readiness.get('per_slice')
        if isinstance(per_slice, dict):
            for slice_name, entry in per_slice.items():
                if isinstance(entry, dict) and entry.get('live'):
                    configured_live_slices.append(str(slice_name))

    if isinstance(live_summary, dict):
        advisory = live_summary.get('advisory_by_slice')
        if isinstance(advisory, dict):
            for slice_name in configured_live_slices:
                entry = advisory.get(slice_name)
                action = str(entry.get('action', '') if isinstance(entry, dict) else '')
                if action not in {'maintain_controlled', 'maintain_live', 'expand_gradually'}:
                    errors.append(f'configured live slice {slice_name} is not in a promotable/maintainable action state')
    else:
        errors.append('experimentLivePromotionSummary missing from status')

    return {
        'ready_for_guarded_release': not errors,
        'classification': 'ready' if not errors else 'blocked',
        'errors': errors,
    }


def main() -> int:
    status_payload = _status_payload(DEFAULT_STATUS_URL)
    git_snapshot = _git_snapshot()
    services = {name: _service_health(container) for name, container in SERVICE_CONTAINERS.items()}
    posture = _release_posture(git_snapshot=git_snapshot, status_payload=status_payload, services=services)
    latest_entries = _latest_changelog_entries()

    live_summary = status_payload.get('experimentLivePromotionSummary') or {}
    next_actions = []
    if isinstance(live_summary, dict):
        for slice_name in live_summary.get('promotable_now') or []:
            next_actions.append(f'consider gradual promotion for {slice_name}')
        for slice_name in live_summary.get('maintain_now') or []:
            next_actions.append(f'maintain current controlled posture for {slice_name}')
        for slice_name, reason in (live_summary.get('blocked_now') or {}).items():
            next_actions.append(f'keep {slice_name} blocked: {reason}')

    lines = [
        '# Framework Release Snapshot Report',
        '',
        f'Date: {datetime.now(UTC).isoformat()}',
        '',
        '## Goal',
        '',
        'Capture a single operational snapshot before merge or rollout promotion, using live runtime state plus framework rollout artifacts.',
        '',
        '## Release Posture',
        '',
        f"- classification: `{posture['classification']}`",
        f"- ready for guarded release: `{posture['ready_for_guarded_release']}`",
        f"- branch: `{git_snapshot['branch']}`",
        f"- commit: `{git_snapshot['commit']}`",
        f"- working tree clean: `{git_snapshot['working_tree_clean']}`",
        '',
        '## Runtime Snapshot',
        '',
        f"- resolved primary stack: `{status_payload.get('resolvedPrimaryStack', '')}`",
        f"- experiment primary engine: `{status_payload.get('experimentPrimaryEngine', '')}`",
        f"- experiment slices: `{status_payload.get('experimentSlices', '')}`",
        f"- experiment slice rollouts: `{status_payload.get('experimentSliceRollouts', '')}`",
        f"- experiment allowlist slices: `{status_payload.get('experimentAllowlistSlices', '')}`",
        '',
        '## Service Health',
        '',
        '| Service | Running | Health |',
        '| --- | --- | --- |',
    ]
    for name, health in services.items():
        lines.append(
            f"| `{name}` | `{'yes' if health.get('running') else 'no'}` | "
            f"`{health.get('health_status') or health.get('status') or 'unknown'}` |"
        )

    lines.extend(['', '## Next Operator Actions', ''])
    if next_actions:
        for item in next_actions:
            lines.append(f'- {item}')
    else:
        lines.append('- `(none)`')

    if latest_entries:
        lines.extend(['', '## Latest Rollout Changelog Entries', '', '| Date | Intent | Slice | Before | After | Result | Operator | Reason |', '| --- | --- | --- | ---: | ---: | --- | --- | --- |'])
        for item in latest_entries:
            lines.append(
                f"| `{item.get('timestamp', '')}` | `{item.get('intent', 'promotion')}` | `{item.get('slice', '')}` | "
                f"`{item.get('before_rollout_percent', '')}%` | `{item.get('after_rollout_percent', '')}%` | "
                f"`{item.get('result', '')}` | `{item.get('operator', '')}` | {item.get('reason', '')} |"
            )

    if posture['errors']:
        lines.extend(['', '## Blocking Errors', ''])
        for item in posture['errors']:
            lines.append(f'- {item}')

    payload = {
        'generated_at': datetime.now(UTC).isoformat(),
        'git': git_snapshot,
        'services': services,
        'status': status_payload,
        'posture': posture,
        'latest_rollout_entries': latest_entries,
        'next_actions': next_actions,
    }
    DEFAULT_REPORT.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    json_text = json.dumps(payload, ensure_ascii=False, indent=2) + '\n'
    DEFAULT_JSON.write_text(json_text, encoding='utf-8')
    DEFAULT_ARTIFACT_JSON.parent.mkdir(parents=True, exist_ok=True)
    DEFAULT_ARTIFACT_JSON.write_text(json_text, encoding='utf-8')
    print(DEFAULT_REPORT)
    print(DEFAULT_JSON)
    print(DEFAULT_ARTIFACT_JSON)
    return 0 if posture['ready_for_guarded_release'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
