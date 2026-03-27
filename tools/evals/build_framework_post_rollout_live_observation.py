#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from urllib.request import urlopen

REPO_ROOT = Path(__file__).resolve().parents[2]

DEFAULT_STATUS_URL = 'http://127.0.0.1:8002/v1/status'
DEFAULT_REPORT_MD = REPO_ROOT / 'docs/architecture/framework-post-rollout-live-observation-report.md'
DEFAULT_REPORT_JSON = REPO_ROOT / 'docs/architecture/framework-post-rollout-live-observation-report.json'
DEFAULT_ARTIFACT_JSON = REPO_ROOT / 'artifacts/framework-post-rollout-live-observation-report.json'
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


def _service_health(container_name: str) -> dict:
    try:
        payload = _run(['docker', 'inspect', '-f', '{{json .State}}', container_name])
        state = json.loads(payload)
    except Exception as exc:  # pragma: no cover - operational fallback
        return {'exists': False, 'error': str(exc)}
    health = state.get('Health') if isinstance(state, dict) else None
    return {
        'exists': True,
        'running': bool(isinstance(state, dict) and state.get('Running')),
        'status': str(state.get('Status', '') if isinstance(state, dict) else ''),
        'health_status': str(health.get('Status', '') if isinstance(health, dict) else ''),
        'started_at': str(state.get('StartedAt', '') if isinstance(state, dict) else ''),
    }


def _status_payload(url: str) -> dict:
    with urlopen(url, timeout=15) as response:
        payload = json.load(response)
    if not isinstance(payload, dict):
        raise RuntimeError('status endpoint did not return a JSON object')
    return payload


def _load_json(path: Path):
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except Exception:
        return None


def _latest_entry() -> dict | None:
    payload = _load_json(CHANGELOG_JSON)
    if not isinstance(payload, list):
        return None
    rows = [item for item in payload if isinstance(item, dict)]
    return rows[-1] if rows else None


def _write_report(*, report_md: Path, report_json: Path, artifact_json: Path, payload: dict) -> None:
    lines = [
        '# Framework Post-Rollout Live Observation Report',
        '',
        f"Date: {payload['generated_at']}",
        '',
        '## Summary',
        '',
        f"- classification: `{payload['classification']}`",
        f"- observation healthy: `{payload['observation_healthy']}`",
        f"- resolved primary stack: `{payload['status'].get('resolvedPrimaryStack', '')}`",
        f"- experiment primary engine: `{payload['status'].get('experimentPrimaryEngine', '')}`",
        f"- experiment slice rollouts: `{payload['status'].get('experimentSliceRollouts', '')}`",
        f"- telegram chat allowlist count: `{payload['status'].get('experimentTelegramChatAllowlistCount', 0)}`",
        f"- conversation allowlist count: `{payload['status'].get('experimentConversationAllowlistCount', 0)}`",
        '',
        '## Live Advisory',
        '',
        f"- promotable now: `{', '.join(payload['advisory'].get('promotable_now') or []) or '(none)'}`",
        f"- maintain now: `{', '.join(payload['advisory'].get('maintain_now') or []) or '(none)'}`",
    ]
    blocked_now = payload['advisory'].get('blocked_now') or {}
    if blocked_now:
        lines.extend(['', '## Blocked Slices', ''])
        for slice_name, reason in blocked_now.items():
            lines.append(f"- `{slice_name}`: {reason}")

    pilot_status = payload['advisory'].get('pilot_status') if isinstance(payload.get('advisory'), dict) else {}
    if isinstance(pilot_status, dict):
        lines.extend(
            [
                '',
                '## CrewAI Pilot Review Gate',
                '',
                f"- user-traffic HITL enabled: `{pilot_status.get('crewaiHitlUserTrafficEnabled')}`",
                f"- user-traffic HITL slices: `{pilot_status.get('crewaiHitlUserTrafficSlices', '')}`",
            ]
        )

    lines.extend(['', '## Service Health', '', '| Service | Running | Health | Started At |', '| --- | --- | --- | --- |'])
    for name, item in payload['services'].items():
        lines.append(
            f"| `{name}` | `{'yes' if item.get('running') else 'no'}` | "
            f"`{item.get('health_status') or item.get('status') or 'unknown'}` | "
            f"`{item.get('started_at', '')}` |"
        )

    latest = payload.get('latest_rollout_entry')
    if isinstance(latest, dict):
        lines.extend(
            [
                '',
                '## Latest Rollout Entry',
                '',
                f"- timestamp: `{latest.get('timestamp', '')}`",
                f"- intent: `{latest.get('intent', 'promotion')}`",
                f"- slice: `{latest.get('slice', '')}`",
                f"- before: `{latest.get('before_rollout_percent', '')}%`",
                f"- after: `{latest.get('after_rollout_percent', '')}%`",
                f"- result: `{latest.get('result', '')}`",
                f"- reason: `{latest.get('reason', '')}`",
            ]
        )

    if payload.get('observation_errors'):
        lines.extend(['', '## Observation Errors', ''])
        for item in payload['observation_errors']:
            lines.append(f'- {item}')

    report_md.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    json_text = json.dumps(payload, ensure_ascii=False, indent=2) + '\n'
    report_json.write_text(json_text, encoding='utf-8')
    artifact_json.parent.mkdir(parents=True, exist_ok=True)
    artifact_json.write_text(json_text, encoding='utf-8')


def main() -> int:
    status = _status_payload(DEFAULT_STATUS_URL)
    services = {name: _service_health(container) for name, container in SERVICE_CONTAINERS.items()}
    advisory = status.get('experimentLivePromotionSummary') if isinstance(status, dict) else {}
    if not isinstance(advisory, dict):
        advisory = {}

    errors: list[str] = []
    if not bool(status.get('ready')):
        errors.append('status.ready=false')
    if not isinstance(status.get('experimentLivePromotionSummary'), dict):
        errors.append('experimentLivePromotionSummary missing from live status')
    for name, item in services.items():
        if not item.get('exists'):
            errors.append(f'{name} container missing')
            continue
        if not item.get('running'):
            errors.append(f'{name} container not running')
        if item.get('health_status') not in {'', 'healthy'}:
            errors.append(f"{name} health={item.get('health_status')}")

    protected = (advisory.get('advisory_by_slice') or {}).get('protected') if isinstance(advisory, dict) else {}
    if isinstance(protected, dict) and protected.get('live'):
        if not protected.get('allowlist_only'):
            errors.append('protected live slice is not restricted to allowlist')
        if not protected.get('pilot_live_gate_ok'):
            errors.append('protected live slice does not have CrewAI pilot live gate open')
        if int(status.get('experimentTelegramChatAllowlistCount', 0) or 0) <= 0 and int(status.get('experimentConversationAllowlistCount', 0) or 0) <= 0:
            errors.append('protected live slice has no allowlist identifiers configured')

    payload = {
        'generated_at': datetime.now(UTC).isoformat(),
        'classification': 'healthy' if not errors else 'degraded',
        'observation_healthy': not errors,
        'observation_errors': errors,
        'status': status,
        'services': services,
        'advisory': advisory,
        'latest_rollout_entry': _latest_entry(),
    }
    _write_report(report_md=DEFAULT_REPORT_MD, report_json=DEFAULT_REPORT_JSON, artifact_json=DEFAULT_ARTIFACT_JSON, payload=payload)
    print(DEFAULT_REPORT_MD)
    print(DEFAULT_REPORT_JSON)
    print(DEFAULT_ARTIFACT_JSON)
    return 0 if not errors else 1


if __name__ == '__main__':
    raise SystemExit(main())
