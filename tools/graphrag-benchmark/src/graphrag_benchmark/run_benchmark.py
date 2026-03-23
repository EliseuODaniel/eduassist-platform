from __future__ import annotations

import argparse
import json
import os
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from time import monotonic
from typing import Any
from urllib.request import Request, urlopen

from graphrag_benchmark.preflight import get_workspace_provider_status


ROOT_DIR = Path(__file__).resolve().parents[4]
PROJECT_DIR = ROOT_DIR / 'tools' / 'graphrag-benchmark'
DEFAULT_WORKSPACE = ROOT_DIR / 'artifacts' / 'graphrag' / 'eduassist-public-benchmark'
DEFAULT_DATASET = ROOT_DIR / 'tools' / 'graphrag-benchmark' / 'datasets' / 'public_corpus_queries.json'
DEFAULT_OUTPUT_DIR = ROOT_DIR / 'artifacts' / 'graphrag' / 'benchmark-runs'


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Compare baseline hybrid retrieval with GraphRAG queries.')
    parser.add_argument('--workspace', type=Path, default=DEFAULT_WORKSPACE)
    parser.add_argument('--dataset', type=Path, default=DEFAULT_DATASET)
    parser.add_argument('--output-dir', type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument('--baseline-url', default=os.getenv('SMOKE_AI_ORCHESTRATOR_URL', 'http://localhost:8002'))
    parser.add_argument('--internal-api-token', default=os.getenv('SMOKE_INTERNAL_API_TOKEN', 'dev-internal-token'))
    parser.add_argument('--public-chat-id', type=int, default=777001)
    parser.add_argument('--response-type', default='List of 3-7 bullet points')
    parser.add_argument('--skip-graphrag', action='store_true')
    return parser.parse_args()


def _normalize_text(value: str) -> str:
    return ''.join(char.lower() for char in value if char.isalnum() or char.isspace())


def _request_json(*, url: str, payload: dict[str, Any], headers: dict[str, str]) -> dict[str, Any]:
    request = Request(
        url,
        data=json.dumps(payload).encode('utf-8'),
        headers={'Content-Type': 'application/json', **headers},
        method='POST',
    )
    with urlopen(request, timeout=30.0) as response:
        return json.loads(response.read().decode('utf-8'))


def _run_baseline(*, baseline_url: str, token: str, chat_id: int, query: str) -> dict[str, Any]:
    started_at = monotonic()
    payload = _request_json(
        url=f'{baseline_url}/v1/messages/respond',
        payload={'message': query, 'telegram_chat_id': chat_id},
        headers={'X-Internal-Api-Token': token},
    )
    duration_ms = round((monotonic() - started_at) * 1000, 2)
    return {
        'duration_ms': duration_ms,
        'mode': payload.get('mode'),
        'retrieval_backend': payload.get('retrieval_backend'),
        'citations': len(payload.get('citations', [])),
        'graph_path': payload.get('graph_path', []),
        'message_text': payload.get('message_text', ''),
    }


def _graphrag_ready(workspace: Path) -> tuple[bool, str, dict[str, Any]]:
    if not (workspace / 'settings.yaml').exists():
        return False, 'workspace_not_bootstrapped', {}
    if not (workspace / 'output').exists():
        return False, 'index_output_missing', {}
    provider_status = get_workspace_provider_status(workspace)
    return (
        bool(provider_status.get('provider_ready')),
        str(provider_status.get('provider_reason', 'provider_not_ready')),
        provider_status,
    )


def _run_graphrag_query(
    *,
    workspace: Path,
    method: str,
    query: str,
    response_type: str,
) -> dict[str, Any]:
    started_at = monotonic()
    result = subprocess.run(
        [
            'uv',
            'run',
            '--project',
            str(PROJECT_DIR),
            'graphrag',
            'query',
            '-r',
            str(workspace),
            '-m',
            method,
            '--response-type',
            response_type,
            query,
        ],
        text=True,
        capture_output=True,
        cwd=str(ROOT_DIR),
    )
    duration_ms = round((monotonic() - started_at) * 1000, 2)
    return {
        'status': 'completed' if result.returncode == 0 else 'failed',
        'return_code': result.returncode,
        'duration_ms': duration_ms,
        'stdout': result.stdout.strip(),
        'stderr': result.stderr.strip(),
    }


def _review_score(*, text: str, review_focus: list[str]) -> dict[str, Any]:
    normalized_text = _normalize_text(text)
    matched = [term for term in review_focus if _normalize_text(term) in normalized_text]
    return {
        'matched_terms': matched,
        'matched_count': len(matched),
        'expected_count': len(review_focus),
    }


def _write_markdown_report(target: Path, report: dict[str, Any]) -> None:
    lines = [
        '# GraphRAG Benchmark Report',
        '',
        f"- generated_at: `{report['generated_at']}`",
        f"- workspace: `{report['workspace']}`",
        f"- dataset: `{report['dataset']}`",
        '',
        '| case | baseline | citations | basic | local | global | drift |',
        '| --- | --- | ---: | --- | --- | --- | --- |',
    ]
    for item in report['cases']:
        methods = item.get('graphrag', {})
        lines.append(
            '| {case} | {mode} | {citations} | {basic} | {local} | {global_status} | {drift} |'.format(
                case=item['case_id'],
                mode=item['baseline']['mode'],
                citations=item['baseline']['citations'],
                basic=methods.get('basic', {}).get('status', 'skipped'),
                local=methods.get('local', {}).get('status', 'skipped'),
                global_status=methods.get('global', {}).get('status', 'skipped'),
                drift=methods.get('drift', {}).get('status', 'skipped'),
            )
        )
    target.write_text('\n'.join(lines) + '\n', encoding='utf-8')


def main() -> int:
    args = parse_args()
    workspace = args.workspace.resolve()
    dataset_path = args.dataset.resolve()
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    cases = json.loads(dataset_path.read_text(encoding='utf-8'))
    ready, readiness_reason, provider_status = _graphrag_ready(workspace)

    report: dict[str, Any] = {
        'generated_at': datetime.now(UTC).isoformat(),
        'workspace': workspace.as_posix(),
        'dataset': dataset_path.as_posix(),
        'baseline_url': args.baseline_url,
        'graphrag_ready': ready,
        'graphrag_readiness_reason': readiness_reason,
        'provider_status': provider_status,
        'cases': [],
    }

    for case in cases:
        query = str(case['query'])
        review_focus = list(case.get('review_focus', []))
        baseline = _run_baseline(
            baseline_url=args.baseline_url,
            token=args.internal_api_token,
            chat_id=args.public_chat_id,
            query=query,
        )
        case_result: dict[str, Any] = {
            'case_id': case['case_id'],
            'query': query,
            'review_focus': review_focus,
            'baseline': baseline,
            'graphrag': {},
        }

        if args.skip_graphrag or not ready:
            for method in case.get('methods', []):
                case_result['graphrag'][method] = {
                    'status': 'skipped',
                    'reason': 'skip_requested' if args.skip_graphrag else readiness_reason,
                }
        else:
            for method in case.get('methods', []):
                result = _run_graphrag_query(
                    workspace=workspace,
                    method=method,
                    query=query,
                    response_type=args.response_type,
                )
                result['review_score'] = _review_score(
                    text=result.get('stdout', ''),
                    review_focus=review_focus,
                )
                case_result['graphrag'][method] = result

        report['cases'].append(case_result)

    stamp = datetime.now(UTC).strftime('%Y%m%dT%H%M%SZ')
    json_target = output_dir / f'graphrag-benchmark-{stamp}.json'
    markdown_target = output_dir / f'graphrag-benchmark-{stamp}.md'
    json_target.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    _write_markdown_report(markdown_target, report)

    print(
        json.dumps(
            {
                'json_report': json_target.as_posix(),
                'markdown_report': markdown_target.as_posix(),
                'graphrag_ready': ready,
                'graphrag_readiness_reason': readiness_reason,
                'provider_profile': provider_status.get('provider_profile'),
                'cases': len(report['cases']),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
