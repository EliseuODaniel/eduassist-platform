#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import sys
from datetime import UTC, datetime
from pathlib import Path
from types import SimpleNamespace

REPO_ROOT = Path(__file__).resolve().parents[2]
APP_SRC = REPO_ROOT / 'apps/ai-orchestrator/src'
if str(APP_SRC) not in sys.path:
    sys.path.insert(0, str(APP_SRC))

from ai_orchestrator.engine_selector import get_experiment_rollout_readiness, get_scorecard_gate_status

OUTPUT_MD = REPO_ROOT / 'docs/architecture/framework-rollout-readiness-report.md'
OUTPUT_JSON = REPO_ROOT / 'docs/architecture/framework-rollout-readiness-report.json'
ARTIFACT_JSON = REPO_ROOT / 'artifacts/framework-rollout-readiness-report.json'
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


def _bool_env(name: str, default: bool) -> bool:
    raw = str(_env_value(name, str(default))).strip().lower()
    return raw in {'1', 'true', 'yes', 'on'}


_ENV_FILE_VALUES = _load_env_file(REPO_ROOT / '.env')


def _env_value(name: str, default: str) -> str:
    if name in os.environ:
        return str(os.environ[name])
    if name in _ENV_FILE_VALUES:
        return str(_ENV_FILE_VALUES[name])
    return default


def _normalize_scorecard_path(value: str) -> str:
    normalized = str(value or '').strip()
    if not normalized:
        return str(LOCAL_SCORECARD_PATH if LOCAL_SCORECARD_PATH.exists() else LOCAL_SCORECARD_DOC_PATH)
    if normalized.startswith('/workspace/artifacts/') and LOCAL_SCORECARD_PATH.exists():
        return str(LOCAL_SCORECARD_PATH)
    if normalized.startswith('/workspace/docs/architecture/') and LOCAL_SCORECARD_DOC_PATH.exists():
        return str(LOCAL_SCORECARD_DOC_PATH)
    return normalized


def _build_settings() -> SimpleNamespace:
    default_scorecard_path = str(LOCAL_SCORECARD_PATH if LOCAL_SCORECARD_PATH.exists() else LOCAL_SCORECARD_DOC_PATH)
    return SimpleNamespace(
        orchestrator_engine=_env_value('ORCHESTRATOR_ENGINE', 'langgraph'),
        feature_flag_primary_orchestration_stack=_env_value('FEATURE_FLAG_PRIMARY_ORCHESTRATION_STACK', ''),
        orchestrator_experiment_enabled=_bool_env('ORCHESTRATOR_EXPERIMENT_ENABLED', False),
        orchestrator_experiment_primary_engine=_env_value('ORCHESTRATOR_EXPERIMENT_PRIMARY_ENGINE', 'crewai'),
        orchestrator_experiment_slices=_env_value('ORCHESTRATOR_EXPERIMENT_SLICES', ''),
        orchestrator_experiment_rollout_percent=int(_env_value('ORCHESTRATOR_EXPERIMENT_ROLLOUT_PERCENT', '0') or 0),
        orchestrator_experiment_slice_rollouts=_env_value('ORCHESTRATOR_EXPERIMENT_SLICE_ROLLOUTS', ''),
        orchestrator_experiment_allowlist_slices=_env_value('ORCHESTRATOR_EXPERIMENT_ALLOWLIST_SLICES', ''),
        orchestrator_experiment_require_scorecard=_bool_env('ORCHESTRATOR_EXPERIMENT_REQUIRE_SCORECARD', False),
        orchestrator_experiment_scorecard_path=_normalize_scorecard_path(
            _env_value('ORCHESTRATOR_EXPERIMENT_SCORECARD_PATH', default_scorecard_path)
        ),
        orchestrator_experiment_min_primary_engine_score=int(
            _env_value('ORCHESTRATOR_EXPERIMENT_MIN_PRIMARY_ENGINE_SCORE', '20') or 20
        ),
        orchestrator_experiment_require_healthy_pilot=_bool_env('ORCHESTRATOR_EXPERIMENT_REQUIRE_HEALTHY_PILOT', False),
        crewai_pilot_url=_env_value('CREWAI_PILOT_URL', ''),
    )


def main() -> int:
    settings = _build_settings()
    gate = get_scorecard_gate_status(settings=settings, primary_engine=settings.orchestrator_experiment_primary_engine)
    readiness = get_experiment_rollout_readiness(settings=settings)

    lines = [
        '# Framework Rollout Readiness Report',
        '',
        f'Date: {datetime.now(UTC).isoformat()}',
        '',
        '## Goal',
        '',
        'Summarize what can be promoted now, by slice, before any canary or feature-flag rollout change.',
        '',
        '## Candidate Engine',
        '',
        f"- candidate engine: `{readiness['candidate_engine']}`",
        f"- scorecard loaded: `{readiness['scorecard_loaded']}`",
        f"- scorecard enforced: `{readiness['scorecard_enforced']}`",
        f"- pilot health enforced: `{readiness['pilot_health_enforced']}`",
        f"- gate eligible: `{readiness['gate_eligible']}`",
        f"- primary-stack native path passed: `{readiness['primary_stack_native_path_passed']}`",
        f"- configured slices: `{', '.join(readiness['configured_slices']) or '(none)'}`",
        f"- promotable now: `{', '.join(readiness['promotable_now']) or '(none)'}`",
        f"- recommended next promotions: `{', '.join(readiness['recommended_next_promotions']) or '(none)'}`",
        '',
        '## Per Slice',
        '',
        '| Slice | Eligible | Configured | Live | Rollout | Allowlist Only | Reason |',
        '| --- | --- | --- | --- | ---: | --- | --- |',
    ]

    per_slice = readiness.get('per_slice') or {}
    for slice_name in ('public', 'protected', 'support', 'workflow'):
        entry = per_slice.get(slice_name) or {}
        lines.append(
            f"| `{slice_name}` | `{'yes' if entry.get('eligible') else 'no'}` | "
            f"`{'yes' if entry.get('configured') else 'no'}` | "
            f"`{'yes' if entry.get('live') else 'no'}` | "
            f"`{int(entry.get('configured_rollout_percent') or 0)}%` | "
            f"`{'yes' if entry.get('allowlist_only') else 'no'}` | "
            f"{entry.get('reason') or ''} |"
        )

    lines.extend(
        [
            '',
            '## Gate Snapshot',
            '',
            '```json',
            json.dumps(gate, ensure_ascii=False, indent=2),
            '```',
            '',
        ]
    )

    payload = {
        'generated_at': datetime.now(UTC).isoformat(),
        'gate': gate,
        'readiness': readiness,
    }
    OUTPUT_MD.write_text('\n'.join(lines), encoding='utf-8')
    json_text = json.dumps(payload, ensure_ascii=False, indent=2) + '\n'
    OUTPUT_JSON.write_text(json_text, encoding='utf-8')
    ARTIFACT_JSON.parent.mkdir(parents=True, exist_ok=True)
    ARTIFACT_JSON.write_text(json_text, encoding='utf-8')
    print(OUTPUT_MD)
    print(OUTPUT_JSON)
    print(ARTIFACT_JSON)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
