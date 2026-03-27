#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from urllib.request import Request, urlopen

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_STATUS_URL = 'http://127.0.0.1:8002/v1/status'
DEFAULT_REPORT_MD = REPO_ROOT / 'docs/architecture/framework-protected-canary-live-observation-report.md'
DEFAULT_REPORT_JSON = REPO_ROOT / 'docs/architecture/framework-protected-canary-live-observation-report.json'
DEFAULT_ARTIFACT_JSON = REPO_ROOT / 'artifacts/framework-protected-canary-live-observation-report.json'


def _status_payload(url: str) -> dict:
    request = Request(url, headers={'X-Internal-Api-Token': 'dev-internal-token'})
    with urlopen(request, timeout=15) as response:
        payload = json.load(response)
    if not isinstance(payload, dict):
        raise RuntimeError('status endpoint did not return a JSON object')
    return payload


def _write_report(*, report_md: Path, report_json: Path, artifact_json: Path, payload: dict) -> None:
    lines = [
        '# Framework Protected Canary Live Observation Report',
        '',
        f"Date: {payload['generated_at']}",
        '',
        '## Summary',
        '',
        f"- classification: `{payload['classification']}`",
        f"- protected configured: `{payload['protected'].get('configured')}`",
        f"- protected live: `{payload['protected'].get('live')}`",
        f"- protected allowlist only: `{payload['protected'].get('allowlist_only')}`",
        f"- protected pilot live gate ok: `{payload['protected'].get('pilot_live_gate_ok')}`",
        f"- pilot user-traffic HITL enabled: `{payload['pilot_status'].get('crewaiHitlUserTrafficEnabled')}`",
        f"- pilot user-traffic HITL slices: `{payload['pilot_status'].get('crewaiHitlUserTrafficSlices', '')}`",
        f"- telegram chat allowlist count: `{payload['allowlist_counts'].get('telegram_chat_count', 0)}`",
        f"- conversation allowlist count: `{payload['allowlist_counts'].get('conversation_count', 0)}`",
        '',
        '## Protected Advisory',
        '',
        '```json',
        json.dumps(payload['protected'], ensure_ascii=False, indent=2),
        '```',
        '',
        '## Pilot Status',
        '',
        '```json',
        json.dumps(payload['pilot_status'], ensure_ascii=False, indent=2),
        '```',
    ]
    if payload.get('errors'):
        lines.extend(['', '## Errors', ''])
        for item in payload['errors']:
            lines.append(f'- {item}')
    report_md.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    json_text = json.dumps(payload, ensure_ascii=False, indent=2) + '\n'
    report_json.write_text(json_text, encoding='utf-8')
    artifact_json.parent.mkdir(parents=True, exist_ok=True)
    artifact_json.write_text(json_text, encoding='utf-8')


def main() -> int:
    status = _status_payload(DEFAULT_STATUS_URL)
    live_summary = status.get('experimentLivePromotionSummary') if isinstance(status.get('experimentLivePromotionSummary'), dict) else {}
    protected = (live_summary.get('advisory_by_slice') or {}).get('protected') if isinstance(live_summary, dict) else {}
    if not isinstance(protected, dict):
        protected = {}
    pilot_status = live_summary.get('pilot_status') if isinstance(live_summary.get('pilot_status'), dict) else {}
    allowlist_counts = {
        'telegram_chat_count': int(status.get('experimentTelegramChatAllowlistCount', 0) or 0),
        'conversation_count': int(status.get('experimentConversationAllowlistCount', 0) or 0),
    }
    errors: list[str] = []
    if not bool(status.get('ready')):
        errors.append('status.ready=false')
    if not bool(protected.get('configured', False)):
        errors.append('protected slice is not configured')
    if not bool(protected.get('live', False)):
        errors.append('protected slice is not live')
    if not bool(protected.get('allowlist_only', False)):
        errors.append('protected slice is not restricted to allowlist')
    if not bool(protected.get('pilot_live_gate_ok', False)):
        errors.append('protected pilot live gate is not open')
    if not bool(pilot_status.get('crewaiHitlUserTrafficEnabled', False)):
        errors.append('CrewAI pilot user-traffic HITL is disabled')
    if 'protected' not in {item.strip() for item in str(pilot_status.get('crewaiHitlUserTrafficSlices', '') or '').split(',') if item.strip()}:
        errors.append('CrewAI pilot user-traffic HITL slices do not include protected')
    if allowlist_counts['telegram_chat_count'] <= 0 and allowlist_counts['conversation_count'] <= 0:
        errors.append('no allowlist identifiers are configured')

    payload = {
        'generated_at': datetime.now(UTC).isoformat(),
        'classification': 'ready' if not errors else 'blocked',
        'errors': errors,
        'protected': protected,
        'pilot_status': pilot_status,
        'allowlist_counts': allowlist_counts,
        'status': status,
    }
    _write_report(report_md=DEFAULT_REPORT_MD, report_json=DEFAULT_REPORT_JSON, artifact_json=DEFAULT_ARTIFACT_JSON, payload=payload)
    print(DEFAULT_REPORT_MD)
    print(DEFAULT_REPORT_JSON)
    print(DEFAULT_ARTIFACT_JSON)
    return 0 if not errors else 1


if __name__ == '__main__':
    raise SystemExit(main())
