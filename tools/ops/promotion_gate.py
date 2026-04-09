from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


ROOT_DIR = Path(__file__).resolve().parents[2]
AI_ORCHESTRATOR_SRC = ROOT_DIR / 'apps' / 'ai-orchestrator' / 'src'
OBSERVABILITY_SRC = ROOT_DIR / 'packages' / 'observability' / 'python' / 'src'
if AI_ORCHESTRATOR_SRC.as_posix() not in sys.path:
    sys.path.insert(0, AI_ORCHESTRATOR_SRC.as_posix())
if OBSERVABILITY_SRC.as_posix() not in sys.path:
    sys.path.insert(0, OBSERVABILITY_SRC.as_posix())

from ai_orchestrator.engine_selector import (  # noqa: E402
    get_experiment_live_promotion_summary,
    get_experiment_rollout_readiness,
    get_scorecard_gate_status,
)
from ai_orchestrator.service_settings import Settings  # noqa: E402


DEFAULT_OUTPUT_DIR = ROOT_DIR / 'artifacts' / 'promotion-gate'


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Run dedicated-first promotion gates and emit a promotion summary.')
    parser.add_argument('--output-dir', type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument('--require-stable-edge', action='store_true')
    parser.add_argument('--skip-telegram-smoke', action='store_true')
    parser.add_argument('--skip-eval', action='store_true')
    return parser.parse_args()


def _run_command(name: str, command: list[str]) -> dict[str, Any]:
    started_at = datetime.now(UTC)
    result = subprocess.run(
        command,
        cwd=str(ROOT_DIR),
        text=True,
        capture_output=True,
    )
    duration_ms = round((datetime.now(UTC) - started_at).total_seconds() * 1000, 2)
    stdout = (result.stdout or '').strip()
    stderr = (result.stderr or '').strip()
    return {
        'name': name,
        'command': command,
        'ok': result.returncode == 0,
        'return_code': result.returncode,
        'duration_ms': duration_ms,
        'stdout_excerpt': stdout[:2500],
        'stderr_excerpt': stderr[:2500],
    }


def _parse_json_excerpt(check: dict[str, Any]) -> dict[str, Any] | None:
    excerpt = str(check.get('stdout_excerpt') or '').strip()
    if not excerpt:
        return None
    candidates = [excerpt]
    lines = [line.strip() for line in excerpt.splitlines() if line.strip()]
    candidates.extend(reversed(lines))
    first_brace = excerpt.find('{')
    last_brace = excerpt.rfind('}')
    if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
        candidates.append(excerpt[first_brace : last_brace + 1])
    seen: set[str] = set()
    for candidate in candidates:
        if candidate in seen:
            continue
        seen.add(candidate)
        try:
            loaded = json.loads(candidate)
        except json.JSONDecodeError:
            continue
        if isinstance(loaded, dict):
            return loaded
    return None


def _write_markdown(path: Path, payload: dict[str, Any]) -> None:
    lines = [
        '# Dedicated-First Promotion Gate',
        '',
        f"- generated_at: `{payload['generated_at']}`",
        f"- overall_ok: `{payload['ok']}`",
        f"- require_stable_edge: `{payload['require_stable_edge']}`",
        '',
        '## Command Gates',
        '',
        '| gate | ok | duration_ms |',
        '| --- | --- | ---: |',
    ]
    for check in payload['checks']:
        lines.append(f"| {check['name']} | {check['ok']} | {check['duration_ms']} |")

    edge = payload.get('edge')
    if isinstance(edge, dict):
        lines.extend(
            [
                '',
                '## Edge',
                '',
                f"- edge_mode: `{edge.get('edge_mode')}`",
                f"- public_base_url: `{edge.get('public_base_url')}`",
                f"- ready_for_stable_edge: `{edge.get('ready_for_stable_edge')}`",
                f"- next_step: {edge.get('next_step')}",
            ]
        )
        risks = edge.get('risks')
        if isinstance(risks, list) and risks:
            lines.append('- risks:')
            for item in risks:
                lines.append(f"  - {item}")

    gate_status = payload.get('scorecard_gate_status')
    if isinstance(gate_status, dict):
        lines.extend(
            [
                '',
                '## Scorecard Gate',
                '',
                f"- selected_engine: `{gate_status.get('selected_engine')}`",
                f"- eligible: `{gate_status.get('eligible')}`",
                f"- total_score: `{gate_status.get('total_score')}`",
                f"- native_path_passed: `{gate_status.get('primary_stack_native_path_passed')}`",
            ]
        )

    promotion = payload.get('promotion_summary')
    if isinstance(promotion, dict):
        lines.extend(
            [
                '',
                '## Promotion Summary',
                '',
                f"- candidate_engine: `{promotion.get('candidate_engine')}`",
                f"- experiment_enabled: `{promotion.get('experiment_enabled')}`",
                f"- promotable_now: `{', '.join(promotion.get('promotable_now') or []) or 'none'}`",
                f"- maintain_now: `{', '.join(promotion.get('maintain_now') or []) or 'none'}`",
            ]
        )
        blocked = promotion.get('blocked_now')
        if isinstance(blocked, dict) and blocked:
            lines.append('- blocked_now:')
            for slice_name, reason in blocked.items():
                lines.append(f"  - `{slice_name}`: {reason}")

    lines.extend(
        [
            '',
            '## Summary',
            '',
            payload['summary'],
            '',
        ]
    )
    path.write_text('\n'.join(lines), encoding='utf-8')


def main() -> int:
    args = parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    checks = [
        _run_command('telegram-edge-readiness', ['make', 'telegram-edge-readiness']),
        _run_command('smoke-dedicated', ['make', 'smoke-dedicated']),
        _run_command('smoke-dedicated-multiturn', ['make', 'smoke-dedicated-multiturn']),
        _run_command('smoke-dedicated-long-memory', ['make', 'smoke-dedicated-long-memory']),
        _run_command('runtime-parity-check', ['make', 'runtime-parity-check']),
    ]
    if not args.skip_telegram_smoke:
        checks.append(_run_command('smoke-telegram-dedicated', ['make', 'smoke-telegram-dedicated']))
    if not args.skip_eval:
        checks.append(_run_command('eval-dedicated', ['make', 'eval-dedicated']))

    edge = _parse_json_excerpt(next(check for check in checks if check['name'] == 'telegram-edge-readiness'))
    settings = Settings()
    scorecard_gate_status = get_scorecard_gate_status(settings=settings)
    rollout_readiness = get_experiment_rollout_readiness(settings=settings)
    promotion_summary = get_experiment_live_promotion_summary(settings=settings)

    mandatory_ok = all(check['ok'] for check in checks if check['name'] != 'telegram-edge-readiness')
    edge_ok = bool(isinstance(edge, dict) and edge.get('ok', False))
    stable_edge_ok = bool(isinstance(edge, dict) and edge.get('ready_for_stable_edge', False))
    overall_ok = mandatory_ok and edge_ok and (stable_edge_ok if args.require_stable_edge else True)

    if overall_ok and args.require_stable_edge:
        summary = (
            'Todos os gates dedicated-first passaram, incluindo borda publica estavel pronta para named tunnel.'
        )
    elif overall_ok:
        summary = (
            'Todos os gates dedicated-first passaram. A arquitetura esta pronta para promote local/controlado; '
            'a borda publica estavel continua recomendada, mas nao foi exigida nesta execucao.'
        )
    else:
        summary = (
            'Um ou mais gates dedicated-first falharam. Revise smokes, memoria longa, parity, '
            'Telegram e scorecard antes de promover qualquer mudanca.'
        )

    payload = {
        'generated_at': datetime.now(UTC).isoformat(),
        'ok': overall_ok,
        'require_stable_edge': args.require_stable_edge,
        'checks': checks,
        'edge': edge,
        'scorecard_gate_status': scorecard_gate_status,
        'rollout_readiness': rollout_readiness,
        'promotion_summary': promotion_summary,
        'summary': summary,
    }

    mode = 'stable-edge' if args.require_stable_edge else 'standard'
    stamp = datetime.now(UTC).strftime('%Y%m%dT%H%M%S%fZ')
    json_target = args.output_dir / f'promotion-gate-{mode}-{stamp}.json'
    markdown_target = args.output_dir / f'promotion-gate-{mode}-{stamp}.md'
    json_target.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')
    _write_markdown(markdown_target, payload)
    print(
        json.dumps(
            {
                'ok': overall_ok,
                'json_report': json_target.as_posix(),
                'markdown_report': markdown_target.as_posix(),
                'summary': summary,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0 if overall_ok else 1


if __name__ == '__main__':
    raise SystemExit(main())
