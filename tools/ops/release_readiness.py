from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


ROOT_DIR = Path(__file__).resolve().parents[2]
GRAPH_RAG_SRC_DIR = ROOT_DIR / 'tools' / 'graphrag-benchmark' / 'src'
if GRAPH_RAG_SRC_DIR.as_posix() not in sys.path:
    sys.path.insert(0, GRAPH_RAG_SRC_DIR.as_posix())

from graphrag_benchmark.preflight import get_workspace_provider_status  # noqa: E402


DEFAULT_OUTPUT_DIR = ROOT_DIR / 'artifacts' / 'readiness'
DEFAULT_GRAPH_RAG_WORKSPACE = ROOT_DIR / 'artifacts' / 'graphrag' / 'eduassist-public-benchmark'
DEFAULT_GRAPH_RAG_REPORTS = ROOT_DIR / 'artifacts' / 'graphrag' / 'benchmark-runs'


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Run minimum release gates and emit a readiness report.')
    parser.add_argument('--strict-graphrag', action='store_true')
    parser.add_argument('--output-dir', type=Path, default=DEFAULT_OUTPUT_DIR)
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
    return {
        'name': name,
        'command': command,
        'ok': result.returncode == 0,
        'return_code': result.returncode,
        'duration_ms': duration_ms,
        'stdout_excerpt': result.stdout.strip()[:2000],
        'stderr_excerpt': result.stderr.strip()[:2000],
    }


def _report_has_completed_graphrag(payload: dict[str, Any]) -> bool:
    for case in payload.get('cases', []):
        methods = case.get('graphrag', {})
        for result in methods.values():
            if isinstance(result, dict) and result.get('status') == 'completed':
                return True
    return False


def _load_latest_graphrag_report(
    report_dir: Path,
    *,
    require_completed: bool = False,
) -> dict[str, Any] | None:
    if not report_dir.exists():
        return None
    candidates = sorted(report_dir.glob('graphrag-benchmark-*.json'))
    if not candidates:
        return None

    for candidate in reversed(candidates):
        payload = json.loads(candidate.read_text(encoding='utf-8'))
        if require_completed and not _report_has_completed_graphrag(payload):
            continue
        payload['_report_path'] = candidate.as_posix()
        return payload
    return None


def _graphrag_status(*, workspace: Path, report_dir: Path) -> dict[str, Any]:
    latest_report = _load_latest_graphrag_report(report_dir)
    latest_completed_report = _load_latest_graphrag_report(report_dir, require_completed=True)
    full_benchmark_completed = latest_completed_report is not None

    provider_status = get_workspace_provider_status(workspace)

    return {
        'workspace_exists': workspace.exists(),
        'settings_exists': (workspace / 'settings.yaml').exists(),
        'input_exists': (workspace / 'input').exists(),
        'output_exists': (workspace / 'output').exists(),
        'provider_profile': provider_status.get('provider_profile'),
        'provider_configured': provider_status.get('provider_configured'),
        'provider_ready': provider_status.get('provider_ready'),
        'provider_reason': provider_status.get('provider_reason'),
        'endpoint_reachable': provider_status.get('endpoint_reachable'),
        'available_models': provider_status.get('available_models'),
        'missing_models': provider_status.get('missing_models'),
        'latest_report': latest_report,
        'latest_completed_report': latest_completed_report,
        'full_benchmark_completed': full_benchmark_completed,
    }


def _write_markdown(target: Path, payload: dict[str, Any]) -> None:
    lines = [
        '# Release Readiness Report',
        '',
        f"- generated_at: `{payload['generated_at']}`",
        f"- overall_ok: `{payload['ok']}`",
        f"- strict_graphrag: `{payload['strict_graphrag']}`",
        '',
        '## Command Gates',
        '',
        '| gate | ok | duration_ms |',
        '| --- | --- | ---: |',
    ]
    for check in payload['checks']:
        lines.append(f"| {check['name']} | {check['ok']} | {check['duration_ms']} |")

    graphrag = payload['graphrag']
    lines.extend(
        [
            '',
            '## GraphRAG Status',
            '',
            f"- workspace_exists: `{graphrag['workspace_exists']}`",
            f"- settings_exists: `{graphrag['settings_exists']}`",
            f"- input_exists: `{graphrag['input_exists']}`",
            f"- output_exists: `{graphrag['output_exists']}`",
            f"- provider_profile: `{graphrag['provider_profile']}`",
            f"- provider_configured: `{graphrag['provider_configured']}`",
            f"- provider_ready: `{graphrag['provider_ready']}`",
            f"- provider_reason: `{graphrag['provider_reason']}`",
            f"- endpoint_reachable: `{graphrag['endpoint_reachable']}`",
            f"- full_benchmark_completed: `{graphrag['full_benchmark_completed']}`",
        ]
    )
    missing_models = graphrag.get('missing_models') or []
    if missing_models:
        lines.append(f"- missing_models: `{', '.join(missing_models)}`")
    latest_report = graphrag.get('latest_report')
    if isinstance(latest_report, dict):
        lines.append(f"- latest_report: `{latest_report.get('_report_path')}`")
        lines.append(f"- latest_report_ready: `{latest_report.get('graphrag_ready')}`")
        lines.append(f"- latest_report_reason: `{latest_report.get('graphrag_readiness_reason')}`")

    lines.extend(
        [
            '',
            '## Summary',
            '',
            payload['summary'],
            '',
        ]
    )
    target.write_text('\n'.join(lines), encoding='utf-8')


def main() -> int:
    args = parse_args()
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    checks = [
        _run_command('db-check-runtime-role', ['make', 'db-check-runtime-role']),
        _run_command('db-check-rls', ['make', 'db-check-rls']),
        _run_command('eval-orchestrator', ['make', 'eval-orchestrator']),
        _run_command('smoke-all', ['make', 'smoke-all']),
        _run_command('graphrag-benchmark-baseline', ['make', 'graphrag-benchmark-baseline']),
    ]

    graphrag = _graphrag_status(
        workspace=DEFAULT_GRAPH_RAG_WORKSPACE,
        report_dir=DEFAULT_GRAPH_RAG_REPORTS,
    )

    mandatory_ok = all(check['ok'] for check in checks)
    graphrag_ok = graphrag['full_benchmark_completed']
    overall_ok = mandatory_ok and (graphrag_ok if args.strict_graphrag else True)

    if overall_ok and args.strict_graphrag:
        summary = 'Todos os gates passaram, incluindo benchmark completo de GraphRAG.'
    elif overall_ok:
        summary = (
            'Todos os gates obrigatorios passaram. O sistema esta pronto para demo/operacao local; '
            'o benchmark completo de GraphRAG continua opcional e depende de provider configurado.'
        )
    elif mandatory_ok:
        summary = (
            'Os gates obrigatorios passaram, mas o modo estrito falhou porque o benchmark completo '
            'de GraphRAG ainda nao foi executado.'
        )
    else:
        summary = 'Um ou mais gates obrigatorios falharam. Revise os checks antes de considerar release.'

    payload = {
        'generated_at': datetime.now(UTC).isoformat(),
        'ok': overall_ok,
        'strict_graphrag': args.strict_graphrag,
        'checks': checks,
        'graphrag': graphrag,
        'summary': summary,
    }

    mode = 'strict' if args.strict_graphrag else 'standard'
    stamp = datetime.now(UTC).strftime('%Y%m%dT%H%M%S%fZ')
    json_target = output_dir / f'release-readiness-{mode}-{stamp}.json'
    markdown_target = output_dir / f'release-readiness-{mode}-{stamp}.md'
    json_target.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')
    _write_markdown(markdown_target, payload)
    print(
        json.dumps(
            {
                'ok': overall_ok,
                'strict_graphrag': args.strict_graphrag,
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
