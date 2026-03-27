#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib.error import URLError
from urllib.request import Request, urlopen

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.evals.apply_framework_rollout_promotion import (
    _apply_overrides,
    _build_preflight_payload,
    _build_settings,
    _env_updates_from_args,
    _render_env_lines,
)

DEFAULT_ENV_FILE = REPO_ROOT / '.env'
DEFAULT_COMPOSE_FILE = REPO_ROOT / 'infra/compose/compose.yaml'
DEFAULT_REPORT = REPO_ROOT / 'docs/architecture/framework-rollout-execution-report.md'
DEFAULT_JSON = REPO_ROOT / 'docs/architecture/framework-rollout-execution-report.json'
DEFAULT_ARTIFACT_JSON = REPO_ROOT / 'artifacts/framework-rollout-execution-report.json'
DEFAULT_STATUS_URL = 'http://127.0.0.1:8002/v1/status'
DEFAULT_BACKUP_DIR = REPO_ROOT / 'artifacts/env-snapshots'
LOCAL_SCORECARD_PATH = REPO_ROOT / 'artifacts/framework-native-scorecard.json'
LOCAL_SCORECARD_DOC_PATH = REPO_ROOT / 'docs/architecture/framework-native-scorecard.json'
SERVICE_CONTAINER_NAMES = {
    'ai-orchestrator': 'eduassist-ai-orchestrator',
}


def _http_json(url: str) -> dict[str, Any]:
    request = Request(url)
    with urlopen(request, timeout=15) as response:
        payload = json.load(response)
    if not isinstance(payload, dict):
        raise RuntimeError('status endpoint did not return a JSON object')
    return payload


def _wait_for_status(url: str, timeout_seconds: int) -> dict[str, Any]:
    deadline = time.monotonic() + timeout_seconds
    last_error: str | None = None
    while time.monotonic() < deadline:
        try:
            payload = _http_json(url)
            if bool(payload.get('ready')):
                return payload
            last_error = 'status returned ready=false'
        except URLError as exc:
            last_error = str(exc)
        except Exception as exc:  # pragma: no cover - defensive
            last_error = str(exc)
        time.sleep(1)
    raise RuntimeError(f'timed out waiting for healthy status from {url}: {last_error or "unknown error"}')


def _sync_runtime_artifacts(*, services: list[str]) -> list[str]:
    synced: list[str] = []
    scorecard_source = LOCAL_SCORECARD_PATH if LOCAL_SCORECARD_PATH.exists() else LOCAL_SCORECARD_DOC_PATH
    if 'ai-orchestrator' in services and scorecard_source.exists():
        container_name = SERVICE_CONTAINER_NAMES.get('ai-orchestrator')
        if container_name:
            subprocess.run(
                [
                    'docker',
                    'exec',
                    container_name,
                    'mkdir',
                    '-p',
                    '/workspace/artifacts',
                ],
                cwd=REPO_ROOT,
                check=True,
            )
            subprocess.run(
                [
                    'docker',
                    'cp',
                    str(scorecard_source),
                    f'{container_name}:/workspace/artifacts/framework-native-scorecard.json',
                ],
                cwd=REPO_ROOT,
                check=True,
            )
            synced.append('framework-native-scorecard.json')
    return synced


def _wait_for_validated_status(*, url: str, timeout_seconds: int, proposed_settings: Any) -> tuple[dict[str, Any], list[str]]:
    deadline = time.monotonic() + timeout_seconds
    last_payload: dict[str, Any] | None = None
    last_errors: list[str] = ['status validation did not run']
    while time.monotonic() < deadline:
        try:
            payload = _http_json(url)
            last_payload = payload
            if not bool(payload.get('ready')):
                last_errors = ['status returned ready=false']
            else:
                last_errors = _validate_status(payload=payload, proposed_settings=proposed_settings)
                if not last_errors:
                    return payload, []
        except URLError as exc:
            last_errors = [str(exc)]
        except Exception as exc:  # pragma: no cover - defensive
            last_errors = [str(exc)]
        time.sleep(1)
    return last_payload or {}, last_errors


def _restart_services(*, env_file: Path, compose_file: Path, services: list[str]) -> None:
    cmd = [
        'docker',
        'compose',
        '--env-file',
        str(env_file),
        '-f',
        str(compose_file),
        'up',
        '-d',
        '--no-deps',
        *services,
    ]
    subprocess.run(cmd, cwd=REPO_ROOT, check=True)


def _normalize_slice_rollouts(value: str | None) -> str:
    items: list[tuple[str, int]] = []
    for part in str(value or '').split(','):
        normalized = part.strip()
        if not normalized:
            continue
        separator = '=' if '=' in normalized else ':'
        if separator not in normalized:
            continue
        name, raw = normalized.split(separator, 1)
        try:
            items.append((name.strip(), int(raw.strip())))
        except ValueError:
            continue
    items.sort(key=lambda item: item[0])
    return ','.join(f'{name}:{percent}' for name, percent in items)


def _validate_status(*, payload: dict[str, Any], proposed_settings: Any) -> list[str]:
    errors: list[str] = []
    if str(payload.get('experimentPrimaryEngine', '') or '') != str(proposed_settings.orchestrator_experiment_primary_engine or ''):
        errors.append('experimentPrimaryEngine does not match proposed settings')
    if str(payload.get('experimentSlices', '') or '') != str(proposed_settings.orchestrator_experiment_slices or ''):
        errors.append('experimentSlices does not match proposed settings')
    if _normalize_slice_rollouts(payload.get('experimentSliceRollouts')) != _normalize_slice_rollouts(
        proposed_settings.orchestrator_experiment_slice_rollouts
    ):
        errors.append('experimentSliceRollouts does not match proposed settings')
    if str(payload.get('experimentAllowlistSlices', '') or '') != str(proposed_settings.orchestrator_experiment_allowlist_slices or ''):
        errors.append('experimentAllowlistSlices does not match proposed settings')
    live_summary = payload.get('experimentLivePromotionSummary')
    if not isinstance(live_summary, dict):
        errors.append('experimentLivePromotionSummary missing from live status')
    else:
        if str(live_summary.get('candidate_engine', '') or '') != str(proposed_settings.orchestrator_experiment_primary_engine or ''):
            errors.append('live promotion summary candidate engine does not match proposed settings')
        advisory = live_summary.get('advisory_by_slice') if isinstance(live_summary.get('advisory_by_slice'), dict) else {}
        pilot_status = live_summary.get('pilot_status') if isinstance(live_summary.get('pilot_status'), dict) else {}
        configured_slices = {item.strip() for item in str(getattr(proposed_settings, 'orchestrator_experiment_slices', '') or '').split(',') if item.strip()}
        if 'protected' in configured_slices:
            protected_advisory = advisory.get('protected') if isinstance(advisory.get('protected'), dict) else {}
            if not bool(protected_advisory.get('pilot_live_gate_ok', False)):
                errors.append('protected pilot live gate is not open after restart')
            if bool(getattr(proposed_settings, 'crewai_hitl_user_traffic_enabled', False)) != bool(pilot_status.get('crewaiHitlUserTrafficEnabled', False)):
                errors.append('CrewAI pilot user-traffic HITL flag does not match proposed settings')
            expected_hitl_slices = str(getattr(proposed_settings, 'crewai_hitl_user_traffic_slices', '') or '')
            if expected_hitl_slices and str(pilot_status.get('crewaiHitlUserTrafficSlices', '') or '') != expected_hitl_slices:
                errors.append('CrewAI pilot user-traffic HITL slices do not match proposed settings')
            if int(payload.get('experimentTelegramChatAllowlistCount', 0) or 0) <= 0 and int(payload.get('experimentConversationAllowlistCount', 0) or 0) <= 0:
                errors.append('protected canary requires at least one allowlist identifier in live status')
    return errors


def _write_report(
    *,
    report_path: Path,
    json_path: Path,
    artifact_json_path: Path,
    preflight: dict[str, Any],
    env_file: Path,
    compose_file: Path,
    services: list[str],
    status_url: str,
    backup_path: Path | None,
    restart_attempted: bool,
    synced_artifacts: list[str],
    live_status: dict[str, Any] | None,
    live_validation_errors: list[str],
) -> None:
    lines = [
        '# Framework Rollout Execution Report',
        '',
        f'Date: {datetime.now(UTC).isoformat()}',
        '',
        '## Goal',
        '',
        'Record a full rollout operation: preflight, apply to env, service restart, and live status validation.',
        '',
        '## Execution Summary',
        '',
        f"- preflight verdict: `{preflight['overall_verdict']}`",
        f"- preflight safe_to_apply: `{preflight['safe_to_apply']}`",
        f"- restart attempted: `{restart_attempted}`",
        f"- services restarted: `{', '.join(services) or '(none)'}`",
        f"- env file: `{env_file}`",
        f"- backup path: `{backup_path if backup_path else '(none)'}`",
        f"- compose file: `{compose_file}`",
        f"- status url: `{status_url}`",
        f"- synced runtime artifacts: `{', '.join(synced_artifacts) or '(none)'}`",
        f"- live validation passed: `{not live_validation_errors}`",
        '',
        '## Requested Live Slices',
        '',
        f"- `{', '.join(preflight.get('requested_live_slices') or []) or '(none)'}`",
        '',
        '## Live Validation Errors',
        '',
    ]
    if live_validation_errors:
        for item in live_validation_errors:
            lines.append(f'- {item}')
    else:
        lines.append('- `(none)`')

    lines.extend(['', '## Slice Changes', '', '| Slice | Configured Before | Configured After | Rollout Before | Rollout After |', '| --- | --- | --- | ---: | ---: |'])
    for item in preflight.get('slice_changes') or []:
        lines.append(
            f"| `{item['slice']}` | `{'yes' if item['configured_before'] else 'no'}` | "
            f"`{'yes' if item['configured_after'] else 'no'}` | "
            f"`{item['rollout_before']}%` | `{item['rollout_after']}%` |"
        )
    if not (preflight.get('slice_changes') or []):
        lines.append('| `(none)` | `-` | `-` | `-` | `-` |')

    if isinstance(live_status, dict):
        lines.extend(
            [
                '',
                '## Live Status Snapshot',
                '',
                '```json',
                json.dumps(
                    {
                        'resolvedPrimaryStack': live_status.get('resolvedPrimaryStack'),
                        'experimentPrimaryEngine': live_status.get('experimentPrimaryEngine'),
                        'experimentSlices': live_status.get('experimentSlices'),
                        'experimentSliceRollouts': live_status.get('experimentSliceRollouts'),
                        'experimentAllowlistSlices': live_status.get('experimentAllowlistSlices'),
                        'experimentLivePromotionSummary': live_status.get('experimentLivePromotionSummary'),
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                '```',
                '',
            ]
        )

    report_path.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    body = {
        'generated_at': datetime.now(UTC).isoformat(),
        'preflight': preflight,
        'env_file': str(env_file),
        'compose_file': str(compose_file),
        'services': services,
        'status_url': status_url,
        'backup_path': str(backup_path) if backup_path else None,
        'restart_attempted': restart_attempted,
        'synced_artifacts': synced_artifacts,
        'live_validation_passed': not live_validation_errors,
        'live_validation_errors': live_validation_errors,
        'live_status': live_status,
    }
    json_text = json.dumps(body, ensure_ascii=False, indent=2) + '\n'
    json_path.write_text(json_text, encoding='utf-8')
    artifact_json_path.parent.mkdir(parents=True, exist_ok=True)
    artifact_json_path.write_text(json_text, encoding='utf-8')


def main() -> int:
    parser = argparse.ArgumentParser(description='Execute a rollout promotion with preflight, restart, and live validation.')
    parser.add_argument('--candidate-engine', default=None)
    parser.add_argument('--slices', default=None)
    parser.add_argument('--slice-rollouts', default=None)
    parser.add_argument('--allowlist-slices', default=None)
    parser.add_argument('--telegram-chat-allowlist', default=None)
    parser.add_argument('--conversation-allowlist', default=None)
    parser.add_argument('--rollout-percent', type=int, default=None)
    parser.add_argument('--crewai-hitl-user-traffic-enabled', dest='crewai_hitl_user_traffic_enabled', action='store_true')
    parser.add_argument('--no-crewai-hitl-user-traffic-enabled', dest='crewai_hitl_user_traffic_enabled', action='store_false')
    parser.add_argument('--crewai-hitl-user-traffic-slices', default=None)
    parser.add_argument('--experiment-enabled', dest='experiment_enabled', action='store_true')
    parser.add_argument('--no-experiment-enabled', dest='experiment_enabled', action='store_false')
    parser.add_argument('--require-scorecard', dest='require_scorecard', action='store_true')
    parser.add_argument('--no-require-scorecard', dest='require_scorecard', action='store_false')
    parser.add_argument('--require-healthy-pilot', dest='require_healthy_pilot', action='store_true')
    parser.add_argument('--no-require-healthy-pilot', dest='require_healthy_pilot', action='store_false')
    parser.add_argument('--min-primary-engine-score', type=int, default=None)
    parser.add_argument('--env-file', type=Path, default=DEFAULT_ENV_FILE)
    parser.add_argument('--compose-file', type=Path, default=DEFAULT_COMPOSE_FILE)
    parser.add_argument('--services', default='ai-orchestrator')
    parser.add_argument('--status-url', default=DEFAULT_STATUS_URL)
    parser.add_argument('--status-timeout-seconds', type=int, default=60)
    parser.add_argument('--backup-dir', type=Path, default=DEFAULT_BACKUP_DIR)
    parser.add_argument('--apply', action='store_true')
    parser.add_argument('--report', type=Path, default=DEFAULT_REPORT)
    parser.add_argument('--json', type=Path, default=DEFAULT_JSON)
    parser.add_argument('--artifact-json', type=Path, default=DEFAULT_ARTIFACT_JSON)
    parser.set_defaults(
        crewai_hitl_user_traffic_enabled=None,
        experiment_enabled=None,
        require_scorecard=None,
        require_healthy_pilot=None,
    )
    args = parser.parse_args()

    current_settings = _build_settings(args.env_file)
    proposed_settings = _apply_overrides(current_settings, args)
    preflight = _build_preflight_payload(current_settings, proposed_settings)
    if not preflight['safe_to_apply']:
        _write_report(
            report_path=args.report,
            json_path=args.json,
            artifact_json_path=args.artifact_json,
            preflight=preflight,
            env_file=args.env_file,
            compose_file=args.compose_file,
            services=[item.strip() for item in args.services.split(',') if item.strip()],
            status_url=args.status_url,
            backup_path=None,
            restart_attempted=False,
            synced_artifacts=[],
            live_status=None,
            live_validation_errors=list(preflight.get('blocking_issues') or ['preflight rejected the proposal']),
        )
        print(args.report)
        print(args.json)
        print(args.artifact_json)
        return 2

    if not args.apply:
        _write_report(
            report_path=args.report,
            json_path=args.json,
            artifact_json_path=args.artifact_json,
            preflight=preflight,
            env_file=args.env_file,
            compose_file=args.compose_file,
            services=[item.strip() for item in args.services.split(',') if item.strip()],
            status_url=args.status_url,
            backup_path=None,
            restart_attempted=False,
            synced_artifacts=[],
            live_status=None,
            live_validation_errors=['execution requires --apply'],
        )
        print(args.report)
        print(args.json)
        print(args.artifact_json)
        return 1

    original_text = args.env_file.read_text(encoding='utf-8') if args.env_file.exists() else ''
    updates = _env_updates_from_args(args)
    args.backup_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(UTC).strftime('%Y%m%dT%H%M%SZ')
    backup_path = args.backup_dir / f'{args.env_file.stem}-execute-{timestamp}.bak'
    if args.env_file.exists():
        shutil.copy2(args.env_file, backup_path)
    else:
        backup_path.write_text('', encoding='utf-8')
    args.env_file.write_text(_render_env_lines(original_text, updates), encoding='utf-8')

    services = [item.strip() for item in args.services.split(',') if item.strip()]
    if any(key.startswith('CREWAI_HITL_') for key in updates) and 'ai-orchestrator-crewai' not in services:
        services.append('ai-orchestrator-crewai')
    live_status: dict[str, Any] | None = None
    live_validation_errors: list[str] = []
    synced_artifacts: list[str] = []
    try:
        _restart_services(env_file=args.env_file, compose_file=args.compose_file, services=services)
        live_status = _wait_for_status(args.status_url, args.status_timeout_seconds)
        synced_artifacts = _sync_runtime_artifacts(services=services)
        live_status, live_validation_errors = _wait_for_validated_status(
            url=args.status_url,
            timeout_seconds=args.status_timeout_seconds,
            proposed_settings=proposed_settings,
        )
    except Exception as exc:
        live_validation_errors = [f'rollout execution failed: {exc}']

    _write_report(
        report_path=args.report,
        json_path=args.json,
        artifact_json_path=args.artifact_json,
        preflight=preflight,
        env_file=args.env_file,
        compose_file=args.compose_file,
        services=services,
        status_url=args.status_url,
        backup_path=backup_path,
        restart_attempted=True,
        synced_artifacts=synced_artifacts,
        live_status=live_status,
        live_validation_errors=live_validation_errors,
    )
    print(args.report)
    print(args.json)
    print(args.artifact_json)
    return 0 if not live_validation_errors else 1


if __name__ == '__main__':
    raise SystemExit(main())
