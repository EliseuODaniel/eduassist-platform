#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import sys
from copy import deepcopy
from datetime import UTC, datetime
from pathlib import Path
from types import SimpleNamespace
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
APP_SRC = REPO_ROOT / 'apps/ai-orchestrator/src'
if str(APP_SRC) not in sys.path:
    sys.path.insert(0, str(APP_SRC))

from ai_orchestrator.engine_selector import get_experiment_live_promotion_summary

DEFAULT_REPORT = REPO_ROOT / 'docs/architecture/framework-rollout-preflight-report.md'
DEFAULT_JSON = REPO_ROOT / 'docs/architecture/framework-rollout-preflight-report.json'
DEFAULT_ARTIFACT_JSON = REPO_ROOT / 'artifacts/framework-rollout-preflight-report.json'
LOCAL_SCORECARD_PATH = REPO_ROOT / 'artifacts/framework-native-scorecard.json'
LOCAL_SCORECARD_DOC_PATH = REPO_ROOT / 'docs/architecture/framework-native-scorecard.json'


def _load_env_file(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    result: dict[str, str] = {}
    for raw_line in path.read_text(encoding='utf-8').splitlines():
        line = raw_line.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue
        key, value = line.split('=', 1)
        result[key.strip()] = value.strip().strip('"').strip("'")
    return result


def _env_value(name: str, default: str, *, env_file_values: dict[str, str]) -> str:
    if name in os.environ:
        return str(os.environ[name])
    if name in env_file_values:
        return str(env_file_values[name])
    return default


def _bool_env(name: str, default: bool, *, env_file_values: dict[str, str]) -> bool:
    raw = str(_env_value(name, str(default), env_file_values=env_file_values)).strip().lower()
    return raw in {'1', 'true', 'yes', 'on'}


def _normalize_scorecard_path(value: str) -> str:
    normalized = str(value or '').strip()
    if not normalized:
        return str(LOCAL_SCORECARD_PATH if LOCAL_SCORECARD_PATH.exists() else LOCAL_SCORECARD_DOC_PATH)
    if normalized.startswith('/workspace/artifacts/') and LOCAL_SCORECARD_PATH.exists():
        return str(LOCAL_SCORECARD_PATH)
    if normalized.startswith('/workspace/docs/architecture/') and LOCAL_SCORECARD_DOC_PATH.exists():
        return str(LOCAL_SCORECARD_DOC_PATH)
    return normalized


def _normalize_pilot_url(value: str) -> str:
    normalized = str(value or '').strip()
    if not normalized:
        return ''
    replacements = {
        'http://ai-orchestrator-crewai:8000': 'http://127.0.0.1:8004',
        'http://localhost:8000': 'http://127.0.0.1:8004',
    }
    return replacements.get(normalized, normalized)


def _build_settings(env_file: Path) -> SimpleNamespace:
    env_file_values = _load_env_file(env_file)
    default_scorecard_path = str(LOCAL_SCORECARD_PATH if LOCAL_SCORECARD_PATH.exists() else LOCAL_SCORECARD_DOC_PATH)
    return SimpleNamespace(
        orchestrator_engine=_env_value('ORCHESTRATOR_ENGINE', 'langgraph', env_file_values=env_file_values),
        feature_flag_primary_orchestration_stack=_env_value('FEATURE_FLAG_PRIMARY_ORCHESTRATION_STACK', '', env_file_values=env_file_values),
        orchestrator_experiment_enabled=_bool_env('ORCHESTRATOR_EXPERIMENT_ENABLED', False, env_file_values=env_file_values),
        orchestrator_experiment_primary_engine=_env_value('ORCHESTRATOR_EXPERIMENT_PRIMARY_ENGINE', 'crewai', env_file_values=env_file_values),
        orchestrator_experiment_slices=_env_value('ORCHESTRATOR_EXPERIMENT_SLICES', '', env_file_values=env_file_values),
        orchestrator_experiment_rollout_percent=int(_env_value('ORCHESTRATOR_EXPERIMENT_ROLLOUT_PERCENT', '0', env_file_values=env_file_values) or 0),
        orchestrator_experiment_slice_rollouts=_env_value('ORCHESTRATOR_EXPERIMENT_SLICE_ROLLOUTS', '', env_file_values=env_file_values),
        orchestrator_experiment_telegram_chat_allowlist=_env_value('ORCHESTRATOR_EXPERIMENT_TELEGRAM_CHAT_ALLOWLIST', '', env_file_values=env_file_values),
        orchestrator_experiment_conversation_allowlist=_env_value('ORCHESTRATOR_EXPERIMENT_CONVERSATION_ALLOWLIST', '', env_file_values=env_file_values),
        orchestrator_experiment_allowlist_slices=_env_value('ORCHESTRATOR_EXPERIMENT_ALLOWLIST_SLICES', '', env_file_values=env_file_values),
        orchestrator_experiment_require_scorecard=_bool_env('ORCHESTRATOR_EXPERIMENT_REQUIRE_SCORECARD', False, env_file_values=env_file_values),
        orchestrator_experiment_scorecard_path=_normalize_scorecard_path(
            _env_value('ORCHESTRATOR_EXPERIMENT_SCORECARD_PATH', default_scorecard_path, env_file_values=env_file_values)
        ),
        orchestrator_experiment_min_primary_engine_score=int(
            _env_value('ORCHESTRATOR_EXPERIMENT_MIN_PRIMARY_ENGINE_SCORE', '20', env_file_values=env_file_values) or 20
        ),
        orchestrator_experiment_require_healthy_pilot=_bool_env('ORCHESTRATOR_EXPERIMENT_REQUIRE_HEALTHY_PILOT', False, env_file_values=env_file_values),
        orchestrator_experiment_health_ttl_seconds=int(_env_value('ORCHESTRATOR_EXPERIMENT_HEALTH_TTL_SECONDS', '15', env_file_values=env_file_values) or 15),
        crewai_hitl_user_traffic_enabled=_bool_env('CREWAI_HITL_USER_TRAFFIC_ENABLED', False, env_file_values=env_file_values),
        crewai_hitl_user_traffic_slices=_env_value('CREWAI_HITL_USER_TRAFFIC_SLICES', '', env_file_values=env_file_values),
        crewai_pilot_url=_normalize_pilot_url(_env_value('CREWAI_PILOT_URL', '', env_file_values=env_file_values)),
        internal_api_token=_env_value('INTERNAL_API_TOKEN', 'dev-internal-token', env_file_values=env_file_values),
    )


def _parse_slice_rollouts(value: str | None) -> dict[str, int]:
    result: dict[str, int] = {}
    for item in str(value or '').split(','):
        normalized = item.strip()
        if not normalized:
            continue
        separator = '=' if '=' in normalized else ':'
        if separator not in normalized:
            continue
        slice_name, raw_percent = normalized.split(separator, 1)
        try:
            result[slice_name.strip()] = max(0, min(100, int(raw_percent.strip())))
        except ValueError:
            continue
    return result


def _configured_slice_set(value: str | None) -> set[str]:
    return {item.strip() for item in str(value or '').split(',') if item.strip()}


def _slice_diff(current_settings: Any, proposed_settings: Any) -> list[dict[str, Any]]:
    known = {'public', 'protected', 'support', 'workflow'}
    current_rollouts = _parse_slice_rollouts(getattr(current_settings, 'orchestrator_experiment_slice_rollouts', ''))
    proposed_rollouts = _parse_slice_rollouts(getattr(proposed_settings, 'orchestrator_experiment_slice_rollouts', ''))
    current_slices = _configured_slice_set(getattr(current_settings, 'orchestrator_experiment_slices', ''))
    proposed_slices = _configured_slice_set(getattr(proposed_settings, 'orchestrator_experiment_slices', ''))
    known.update(current_rollouts.keys())
    known.update(proposed_rollouts.keys())
    known.update(current_slices)
    known.update(proposed_slices)

    result: list[dict[str, Any]] = []
    for slice_name in sorted(known):
        before_rollout = current_rollouts.get(slice_name, int(getattr(current_settings, 'orchestrator_experiment_rollout_percent', 0) or 0))
        after_rollout = proposed_rollouts.get(slice_name, int(getattr(proposed_settings, 'orchestrator_experiment_rollout_percent', 0) or 0))
        before_configured = slice_name in current_slices
        after_configured = slice_name in proposed_slices
        if before_rollout == after_rollout and before_configured == after_configured:
            continue
        result.append(
            {
                'slice': slice_name,
                'configured_before': before_configured,
                'configured_after': after_configured,
                'rollout_before': before_rollout,
                'rollout_after': after_rollout,
            }
        )
    return result


def _apply_overrides(base: Any, args: argparse.Namespace) -> Any:
    settings = deepcopy(base)
    if args.candidate_engine is not None:
        settings.orchestrator_experiment_primary_engine = args.candidate_engine
    if args.slices is not None:
        settings.orchestrator_experiment_slices = args.slices
    if args.slice_rollouts is not None:
        settings.orchestrator_experiment_slice_rollouts = args.slice_rollouts
    if args.allowlist_slices is not None:
        settings.orchestrator_experiment_allowlist_slices = args.allowlist_slices
    if args.telegram_chat_allowlist is not None:
        settings.orchestrator_experiment_telegram_chat_allowlist = args.telegram_chat_allowlist
    if args.conversation_allowlist is not None:
        settings.orchestrator_experiment_conversation_allowlist = args.conversation_allowlist
    if args.experiment_enabled is not None:
        settings.orchestrator_experiment_enabled = args.experiment_enabled
    if args.require_scorecard is not None:
        settings.orchestrator_experiment_require_scorecard = args.require_scorecard
    if args.require_healthy_pilot is not None:
        settings.orchestrator_experiment_require_healthy_pilot = args.require_healthy_pilot
    if args.min_primary_engine_score is not None:
        settings.orchestrator_experiment_min_primary_engine_score = args.min_primary_engine_score
    if args.crewai_hitl_user_traffic_enabled is not None:
        settings.crewai_hitl_user_traffic_enabled = args.crewai_hitl_user_traffic_enabled
    if args.crewai_hitl_user_traffic_slices is not None:
        settings.crewai_hitl_user_traffic_slices = args.crewai_hitl_user_traffic_slices
    return settings


def _decision(entry: dict[str, Any]) -> str:
    action = str(entry.get('action', 'blocked'))
    if action in {'expand_gradually', 'activate_configured_slice', 'start_controlled_canary', 'start_tiny_rollout'}:
        return 'approve'
    if action in {'maintain_controlled', 'maintain_live'}:
        return 'maintain'
    return 'reject'


def main() -> int:
    parser = argparse.ArgumentParser(description='Preflight a proposed framework rollout change before applying any env update.')
    parser.add_argument('--candidate-engine', default=None)
    parser.add_argument('--slices', default=None, help='Override ORCHESTRATOR_EXPERIMENT_SLICES')
    parser.add_argument('--slice-rollouts', default=None, help='Override ORCHESTRATOR_EXPERIMENT_SLICE_ROLLOUTS')
    parser.add_argument('--allowlist-slices', default=None, help='Override ORCHESTRATOR_EXPERIMENT_ALLOWLIST_SLICES')
    parser.add_argument('--telegram-chat-allowlist', default=None, help='Override ORCHESTRATOR_EXPERIMENT_TELEGRAM_CHAT_ALLOWLIST')
    parser.add_argument('--conversation-allowlist', default=None, help='Override ORCHESTRATOR_EXPERIMENT_CONVERSATION_ALLOWLIST')
    parser.add_argument('--crewai-hitl-user-traffic-enabled', dest='crewai_hitl_user_traffic_enabled', action='store_true')
    parser.add_argument('--no-crewai-hitl-user-traffic-enabled', dest='crewai_hitl_user_traffic_enabled', action='store_false')
    parser.add_argument('--crewai-hitl-user-traffic-slices', default=None, help='Override CREWAI_HITL_USER_TRAFFIC_SLICES')
    parser.add_argument('--experiment-enabled', dest='experiment_enabled', action='store_true')
    parser.add_argument('--no-experiment-enabled', dest='experiment_enabled', action='store_false')
    parser.add_argument('--require-scorecard', dest='require_scorecard', action='store_true')
    parser.add_argument('--no-require-scorecard', dest='require_scorecard', action='store_false')
    parser.add_argument('--require-healthy-pilot', dest='require_healthy_pilot', action='store_true')
    parser.add_argument('--no-require-healthy-pilot', dest='require_healthy_pilot', action='store_false')
    parser.add_argument('--min-primary-engine-score', type=int, default=None)
    parser.add_argument('--env-file', type=Path, default=REPO_ROOT / '.env')
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
    current_summary = get_experiment_live_promotion_summary(settings=current_settings)
    proposed_summary = get_experiment_live_promotion_summary(settings=proposed_settings)
    slice_changes = _slice_diff(current_settings, proposed_settings)

    advisory_by_slice = proposed_summary.get('advisory_by_slice') or {}
    requested_live_slices = [
        str(item.get('slice'))
        for item in slice_changes
        if item.get('configured_after') and int(item.get('rollout_after') or 0) > 0
    ]
    if not requested_live_slices:
        requested_live_slices = [
            slice_name
            for slice_name, entry in advisory_by_slice.items()
            if isinstance(entry, dict) and entry.get('live')
        ]

    proposed_allowlist_slices = _configured_slice_set(getattr(proposed_settings, 'orchestrator_experiment_allowlist_slices', ''))
    proposed_chat_allowlist = _configured_slice_set(getattr(proposed_settings, 'orchestrator_experiment_telegram_chat_allowlist', ''))
    proposed_conversation_allowlist = _configured_slice_set(getattr(proposed_settings, 'orchestrator_experiment_conversation_allowlist', ''))

    blocking_issues: list[str] = []
    per_slice_verdicts: dict[str, Any] = {}
    for slice_name in ('public', 'protected', 'support', 'workflow'):
        entry = advisory_by_slice.get(slice_name) or {}
        decision = _decision(entry)
        blocked_reasons = list(entry.get('blocked_reasons') or [])
        if slice_name in requested_live_slices and decision == 'reject':
            blocking_issues.extend(f'{slice_name}: {reason}' for reason in blocked_reasons or ['blocked by preflight'])
        per_slice_verdicts[slice_name] = {
            'decision': decision,
            'action': entry.get('action', 'blocked'),
            'blocked_reasons': blocked_reasons,
        }

    if 'protected' in requested_live_slices:
        if 'protected' not in proposed_allowlist_slices:
            blocking_issues.append('protected: protected canary must keep `protected` inside ORCHESTRATOR_EXPERIMENT_ALLOWLIST_SLICES.')
        if not proposed_chat_allowlist and not proposed_conversation_allowlist:
            blocking_issues.append('protected: protected canary requires at least one telegram chat or conversation allowlist identifier.')
        if not bool(getattr(proposed_settings, 'crewai_hitl_user_traffic_enabled', False)):
            blocking_issues.append('protected: protected canary requires CREWAI_HITL_USER_TRAFFIC_ENABLED=true.')
        proposed_hitl_slices = _configured_slice_set(getattr(proposed_settings, 'crewai_hitl_user_traffic_slices', ''))
        if proposed_hitl_slices and 'protected' not in proposed_hitl_slices:
            blocking_issues.append('protected: protected canary requires protected inside CREWAI_HITL_USER_TRAFFIC_SLICES.')

    safe_to_apply = not blocking_issues
    overall_verdict = 'approve' if safe_to_apply else 'reject'
    proposed_allowlist_identifiers = {
        'telegram_chat_ids': sorted(proposed_chat_allowlist),
        'conversation_ids': sorted(proposed_conversation_allowlist),
    }
    proposed_crewai_hitl = {
        'user_traffic_enabled': bool(getattr(proposed_settings, 'crewai_hitl_user_traffic_enabled', False)),
        'user_traffic_slices': str(getattr(proposed_settings, 'crewai_hitl_user_traffic_slices', '') or ''),
    }

    lines = [
        '# Framework Rollout Preflight Report',
        '',
        f'Date: {datetime.now(UTC).isoformat()}',
        '',
        '## Goal',
        '',
        'Validate a proposed canary rollout change before applying environment or rollout updates.',
        '',
        '## Verdict',
        '',
        f"- overall verdict: `{overall_verdict}`",
        f"- safe to apply: `{safe_to_apply}`",
        f"- requested live slices: `{', '.join(requested_live_slices) or '(none)'}`",
        f"- candidate engine: `{proposed_summary['candidate_engine']}`",
        f"- proposed telegram chat allowlist count: `{len(proposed_allowlist_identifiers['telegram_chat_ids'])}`",
        f"- proposed conversation allowlist count: `{len(proposed_allowlist_identifiers['conversation_ids'])}`",
        f"- proposed CrewAI protected user-traffic HITL: `{proposed_crewai_hitl['user_traffic_enabled']}`",
        f"- proposed CrewAI HITL slices: `{proposed_crewai_hitl['user_traffic_slices']}`",
        '',
        '## Proposed Changes',
        '',
        '| Slice | Configured Before | Configured After | Rollout Before | Rollout After |',
        '| --- | --- | --- | ---: | ---: |',
    ]
    for item in slice_changes:
        lines.append(
            f"| `{item['slice']}` | `{'yes' if item['configured_before'] else 'no'}` | "
            f"`{'yes' if item['configured_after'] else 'no'}` | "
            f"`{item['rollout_before']}%` | `{item['rollout_after']}%` |"
        )
    if not slice_changes:
        lines.append('| `(none)` | `-` | `-` | `-` | `-` |')

    lines.extend(
        [
            '',
            '## Proposed Slice Decisions',
            '',
            '| Slice | Decision | Action | Blocked Reasons |',
            '| --- | --- | --- | --- |',
        ]
    )
    for slice_name in ('public', 'protected', 'support', 'workflow'):
        verdict = per_slice_verdicts.get(slice_name) or {}
        lines.append(
            f"| `{slice_name}` | `{verdict.get('decision', 'reject')}` | "
            f"`{verdict.get('action', 'blocked')}` | "
            f"{'; '.join(verdict.get('blocked_reasons') or [])} |"
        )

    lines.extend(
        [
            '',
            '## Current Live Summary',
            '',
            f"- promotable now: `{', '.join(current_summary.get('promotable_now') or []) or '(none)'}`",
            f"- maintain now: `{', '.join(current_summary.get('maintain_now') or []) or '(none)'}`",
            '',
            '## Proposed Live Summary',
            '',
            f"- promotable now: `{', '.join(proposed_summary.get('promotable_now') or []) or '(none)'}`",
            f"- maintain now: `{', '.join(proposed_summary.get('maintain_now') or []) or '(none)'}`",
            '',
        ]
    )
    if blocking_issues:
        lines.extend(['## Blocking Issues', ''])
        for item in blocking_issues:
            lines.append(f'- {item}')
        lines.append('')

    payload = {
        'generated_at': datetime.now(UTC).isoformat(),
        'overall_verdict': overall_verdict,
        'safe_to_apply': safe_to_apply,
        'requested_live_slices': requested_live_slices,
        'slice_changes': slice_changes,
        'blocking_issues': blocking_issues,
        'current_summary': current_summary,
        'proposed_summary': proposed_summary,
        'per_slice_verdicts': per_slice_verdicts,
        'proposed_allowlist_identifiers': proposed_allowlist_identifiers,
        'proposed_crewai_hitl': proposed_crewai_hitl,
    }
    args.report.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    json_text = json.dumps(payload, ensure_ascii=False, indent=2) + '\n'
    args.json.write_text(json_text, encoding='utf-8')
    args.artifact_json.parent.mkdir(parents=True, exist_ok=True)
    args.artifact_json.write_text(json_text, encoding='utf-8')
    print(args.report)
    print(args.json)
    print(args.artifact_json)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
