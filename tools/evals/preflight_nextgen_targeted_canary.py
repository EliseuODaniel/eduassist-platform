#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.evals.preflight_nextgen_stack_runtime import (  # noqa: E402
    _clear_runtime_primary_stack,
    _get_runtime_primary_stack,
    _http_json,
    _restore_previous_override,
)

DEFAULT_DATASET = REPO_ROOT / 'tests/evals/datasets/nextgen_targeted_canary_cases.json'
DEFAULT_REPORT = REPO_ROOT / 'docs/architecture/nextgen-targeted-canary-preflight-report.md'
DEFAULT_JSON = REPO_ROOT / 'docs/architecture/nextgen-targeted-canary-preflight-report.json'
DEFAULT_ARTIFACT_JSON = REPO_ROOT / 'artifacts/nextgen-targeted-canary-preflight-report.json'
SUPPORTED_STACKS = ('python_functions', 'llamaindex')


def _contains_expected_keywords(answer_text: str, expected_keywords: list[str]) -> bool:
    haystack = str(answer_text or '').lower()
    return all(str(keyword).strip().lower() in haystack for keyword in expected_keywords if str(keyword).strip())


def _get_runtime_targeted_stack(*, base_url: str, internal_api_token: str) -> dict[str, Any]:
    _, payload = _http_json(
        method='GET',
        url=f'{base_url}/v1/internal/runtime/targeted-stack',
        headers={'X-Internal-Api-Token': internal_api_token},
        timeout=20.0,
    )
    return payload


def _set_runtime_targeted_stack(
    *,
    base_url: str,
    internal_api_token: str,
    stack: str,
    operator: str,
    reason: str,
    slices: list[str],
    telegram_chat_allowlist: list[str],
    conversation_allowlist: list[str],
) -> dict[str, Any]:
    _, payload = _http_json(
        method='POST',
        url=f'{base_url}/v1/internal/runtime/targeted-stack',
        payload={
            'stack': stack,
            'operator': operator,
            'reason': reason,
            'slices': slices,
            'telegram_chat_allowlist': telegram_chat_allowlist,
            'conversation_allowlist': conversation_allowlist,
        },
        headers={'X-Internal-Api-Token': internal_api_token},
        timeout=20.0,
    )
    return payload


def _clear_runtime_targeted_stack(
    *,
    base_url: str,
    internal_api_token: str,
    operator: str,
    reason: str,
) -> dict[str, Any]:
    _, payload = _http_json(
        method='POST',
        url=f'{base_url}/v1/internal/runtime/targeted-stack',
        payload={'clear_override': True, 'operator': operator, 'reason': reason},
        headers={'X-Internal-Api-Token': internal_api_token},
        timeout=20.0,
    )
    return payload


def _restore_previous_targeted_override(
    *,
    base_url: str,
    internal_api_token: str,
    operator: str,
    previous_state: dict[str, Any],
) -> dict[str, Any]:
    previous_override = previous_state.get('targetedOverride')
    if isinstance(previous_override, dict) and str(previous_override.get('value') or '').strip():
        return _set_runtime_targeted_stack(
            base_url=base_url,
            internal_api_token=internal_api_token,
            stack=str(previous_override.get('value')),
            operator=operator,
            reason='restore_previous_targeted_runtime_override',
            slices=[str(item) for item in (previous_override.get('slices') or []) if str(item).strip()],
            telegram_chat_allowlist=[
                str(item) for item in (previous_override.get('telegram_chat_allowlist') or []) if str(item).strip()
            ],
            conversation_allowlist=[
                str(item) for item in (previous_override.get('conversation_allowlist') or []) if str(item).strip()
            ],
        )
    return _clear_runtime_targeted_stack(
        base_url=base_url,
        internal_api_token=internal_api_token,
        operator=operator,
        reason='restore_default_targeted_runtime_stack',
    )


def _load_cases(path: Path) -> list[dict[str, Any]]:
    payload = json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(payload, list):
        raise ValueError(f'Expected a list of cases in {path}')
    return [item for item in payload if isinstance(item, dict)]


def _build_request_payload(*, case: dict[str, Any], conversation_id: str, telegram_chat_id: int) -> dict[str, Any]:
    return {
        'message': str(case['message']),
        'conversation_id': conversation_id,
        'telegram_chat_id': int(telegram_chat_id),
        'channel': 'telegram',
        'user': case.get('user') or {},
        'allow_graph_rag': True,
        'allow_handoff': True,
    }


def _run_single_probe(
    *,
    base_url: str,
    internal_api_token: str,
    payload: dict[str, Any],
) -> tuple[int, dict[str, Any]]:
    return _http_json(
        method='POST',
        url=f'{base_url}/v1/messages/respond',
        payload=payload,
        headers={'X-Internal-Api-Token': internal_api_token},
        timeout=45.0,
    )


def _evaluate_result(
    *,
    stack: str,
    case: dict[str, Any],
    lane: str,
    status_code: int,
    body: dict[str, Any],
) -> dict[str, Any]:
    graph_path = [str(item) for item in (body.get('graph_path') or []) if str(item).strip()]
    mode = str(body.get('mode') or '')
    answer_text = str(body.get('message_text') or '')
    access_tier = str((body.get('classification') or {}).get('access_tier') or '')
    expected_access_tier = str(case.get('expected_access_tier') or '').strip()
    expected_keywords = [str(item) for item in (case.get('expected_keywords') or []) if str(item).strip()]
    targeted_hit = f'kernel:{stack}' in graph_path
    keyword_pass = _contains_expected_keywords(answer_text, expected_keywords)

    if lane == 'allowlisted':
        passed = bool(
            status_code == 200
            and targeted_hit
            and keyword_pass
            and (not expected_access_tier or access_tier == expected_access_tier)
        )
    else:
        passed = bool(
            status_code == 200
            and not targeted_hit
            and not mode.startswith('targeted:')
            and keyword_pass
            and (not expected_access_tier or access_tier == expected_access_tier)
        )

    return {
        'case_id': str(case['id']),
        'stack': stack,
        'lane': lane,
        'status': status_code,
        'passed': passed,
        'mode': mode,
        'reason': str(body.get('reason') or ''),
        'graph_path': graph_path,
        'access_tier': access_tier,
        'keyword_pass': keyword_pass,
        'targeted_hit': targeted_hit,
        'message_preview': answer_text[:220],
    }


def _summary_for_stack(results: list[dict[str, Any]], *, stack: str) -> dict[str, Any]:
    subset = [item for item in results if item['stack'] == stack]
    allowlisted = [item for item in subset if item['lane'] == 'allowlisted']
    control = [item for item in subset if item['lane'] == 'control']
    return {
        'allowlisted_passed': sum(1 for item in allowlisted if item['passed']),
        'allowlisted_total': len(allowlisted),
        'control_passed': sum(1 for item in control if item['passed']),
        'control_total': len(control),
        'ready_for_targeted_canary': bool(subset) and all(item['passed'] for item in subset),
    }


def _write_report(*, report_md: Path, report_json: Path, artifact_json: Path, payload: dict[str, Any]) -> None:
    json_text = json.dumps(payload, ensure_ascii=False, indent=2) + '\n'
    report_json.write_text(json_text, encoding='utf-8')
    artifact_json.write_text(json_text, encoding='utf-8')

    lines = [
        '# Next-Gen Targeted Canary Preflight Report',
        '',
        f"Date: {payload['generated_at']}",
        '',
        f"Base URL: `{payload['base_url']}`",
        '',
        f"Dataset: `{payload['dataset']}`",
        '',
        '## Summary',
        '',
        '| Stack | Allowlisted lane | Control lane | Ready for targeted canary |',
        '| --- | --- | --- | --- |',
    ]
    for stack in payload['stacks']:
        bucket = payload['summary']['by_stack'][stack]
        lines.append(
            f"| `{stack}` | `{bucket['allowlisted_passed']}/{bucket['allowlisted_total']}` | `{bucket['control_passed']}/{bucket['control_total']}` | `{bucket['ready_for_targeted_canary']}` |"
        )
    lines.extend(
        [
            '',
            '## Runtime State',
            '',
            f"- Before: `resolved={payload['runtime_before'].get('resolvedPrimaryStack')}` from `{payload['runtime_before'].get('resolvedPrimaryStackSource')}`",
            f"- Baseline during preflight: `resolved={payload['baseline_runtime'].get('resolvedPrimaryStack')}` from `{payload['baseline_runtime'].get('resolvedPrimaryStackSource')}`",
            f"- Targeted before: `{payload['targeted_before'].get('targetedOverride', {}).get('value')}`",
            f"- After restore: `resolved={payload['runtime_after_restore'].get('resolvedPrimaryStack')}` from `{payload['runtime_after_restore'].get('resolvedPrimaryStackSource')}`",
            f"- Targeted after restore: `{payload['targeted_after_restore'].get('targetedOverride', {}).get('value')}`",
            '',
            '## Why this drill uses `protected`',
            '',
            '- O objetivo aqui e provar que so a conversa allowlisted entra na stack nova.',
            '- O slice `protected` foi escolhido porque o baseline atual fica em `LangGraph`, sem ruido do experimento vivo que ainda existe em outros slices.',
            '- O drill usa o mesmo chat autenticado nos dois lados e muda apenas o `conversation_id`, para isolar a regra de canario sem perder o contexto real de autenticacao.',
            '',
            '## Probe Results',
            '',
            '| Case | Stack | Lane | Result | Mode | Targeted hit | Access tier | Reason |',
            '| --- | --- | --- | --- | --- | --- | --- | --- |',
        ]
    )
    for item in payload['results']:
        lines.append(
            f"| `{item['case_id']}` | `{item['stack']}` | `{item['lane']}` | {'passed' if item['passed'] else 'failed'} | `{item['mode']}` | `{item['targeted_hit']}` | `{item['access_tier']}` | `{item['reason']}` |"
        )
    report_md.write_text('\n'.join(lines) + '\n', encoding='utf-8')


def main() -> int:
    parser = argparse.ArgumentParser(description='Preflight targeted allowlist canary routing for python_functions and llamaindex.')
    parser.add_argument('--stack', choices=[*SUPPORTED_STACKS, 'all'], default='all')
    parser.add_argument(
        '--base-url',
        default=os.getenv('CONTROL_PLANE_ORCHESTRATOR_URL', 'http://127.0.0.1:8002'),
    )
    parser.add_argument('--internal-api-token', default=os.environ.get('INTERNAL_API_TOKEN', 'dev-internal-token'))
    parser.add_argument('--operator', default='codex')
    parser.add_argument('--dataset', type=Path, default=DEFAULT_DATASET)
    parser.add_argument('--report', type=Path, default=DEFAULT_REPORT)
    parser.add_argument('--json', type=Path, default=DEFAULT_JSON)
    parser.add_argument('--artifact-json', type=Path, default=DEFAULT_ARTIFACT_JSON)
    args = parser.parse_args()

    stacks = list(SUPPORTED_STACKS if args.stack == 'all' else [args.stack])
    cases = _load_cases(args.dataset)
    runtime_before = _get_runtime_primary_stack(base_url=args.base_url, internal_api_token=args.internal_api_token)
    targeted_before = _get_runtime_targeted_stack(base_url=args.base_url, internal_api_token=args.internal_api_token)
    results: list[dict[str, Any]] = []
    targeted_actions: list[dict[str, Any]] = []

    baseline_runtime: dict[str, Any] | None = None
    runtime_after_restore: dict[str, Any] | None = None
    targeted_after_restore: dict[str, Any] | None = None

    try:
        if str(runtime_before.get('runtimePrimaryStackOverride') or '').strip():
            _clear_runtime_primary_stack(
                base_url=args.base_url,
                internal_api_token=args.internal_api_token,
                operator=args.operator,
                reason='nextgen_targeted_canary_preflight_clear_primary_override',
            )
        if str((targeted_before.get('targetedOverride') or {}).get('value') or '').strip():
            _clear_runtime_targeted_stack(
                base_url=args.base_url,
                internal_api_token=args.internal_api_token,
                operator=args.operator,
                reason='nextgen_targeted_canary_preflight_clear_previous_targeted_override',
            )

        baseline_runtime = _get_runtime_primary_stack(base_url=args.base_url, internal_api_token=args.internal_api_token)
        if str(baseline_runtime.get('resolvedPrimaryStack') or '') != 'langgraph':
            raise RuntimeError(
                f"targeted_canary_requires_langgraph_baseline:resolved={baseline_runtime.get('resolvedPrimaryStack')}"
            )

        for stack in stacks:
            slices = sorted({str(case.get('slice') or '').strip() for case in cases if str(case.get('slice') or '').strip()})
            conversation_allowlist = [
                f"{str(case['conversation_id']).strip()}:{stack}:allowlisted" for case in cases if str(case.get('conversation_id') or '').strip()
            ]
            targeted_payload = _set_runtime_targeted_stack(
                base_url=args.base_url,
                internal_api_token=args.internal_api_token,
                stack=stack,
                operator=args.operator,
                reason=f'nextgen_targeted_canary_preflight_{stack}',
                slices=slices,
                telegram_chat_allowlist=[],
                conversation_allowlist=conversation_allowlist,
            )
            targeted_actions.append({'stack': stack, 'payload': targeted_payload})

            for case in cases:
                allowlisted_payload = _build_request_payload(
                    case=case,
                    conversation_id=f"{case['conversation_id']}:{stack}:allowlisted",
                    telegram_chat_id=int(case['telegram_chat_id']),
                )
                control_payload = _build_request_payload(
                    case=case,
                    conversation_id=f"{case['conversation_id']}:{stack}:control",
                    telegram_chat_id=int(case['telegram_chat_id']),
                )

                allowed_status, allowed_body = _run_single_probe(
                    base_url=args.base_url,
                    internal_api_token=args.internal_api_token,
                    payload=allowlisted_payload,
                )
                control_status, control_body = _run_single_probe(
                    base_url=args.base_url,
                    internal_api_token=args.internal_api_token,
                    payload=control_payload,
                )
                results.append(
                    _evaluate_result(
                        stack=stack,
                        case=case,
                        lane='allowlisted',
                        status_code=allowed_status,
                        body=allowed_body,
                    )
                )
                results.append(
                    _evaluate_result(
                        stack=stack,
                        case=case,
                        lane='control',
                        status_code=control_status,
                        body=control_body,
                    )
                )

        runtime_after_restore = _restore_previous_override(
            base_url=args.base_url,
            internal_api_token=args.internal_api_token,
            operator=args.operator,
            previous_state=runtime_before,
        )
        targeted_after_restore = _restore_previous_targeted_override(
            base_url=args.base_url,
            internal_api_token=args.internal_api_token,
            operator=args.operator,
            previous_state=targeted_before,
        )
    finally:
        if runtime_after_restore is None:
            runtime_after_restore = _restore_previous_override(
                base_url=args.base_url,
                internal_api_token=args.internal_api_token,
                operator=args.operator,
                previous_state=runtime_before,
            )
        if targeted_after_restore is None:
            targeted_after_restore = _restore_previous_targeted_override(
                base_url=args.base_url,
                internal_api_token=args.internal_api_token,
                operator=args.operator,
                previous_state=targeted_before,
            )

    payload = {
        'generated_at': datetime.now(UTC).isoformat(),
        'base_url': args.base_url,
        'dataset': str(args.dataset),
        'stacks': stacks,
        'runtime_before': runtime_before,
        'baseline_runtime': baseline_runtime or {},
        'targeted_before': targeted_before,
        'targeted_actions': targeted_actions,
        'runtime_after_restore': runtime_after_restore,
        'targeted_after_restore': targeted_after_restore,
        'results': results,
        'summary': {'by_stack': {stack: _summary_for_stack(results, stack=stack) for stack in stacks}},
    }
    _write_report(report_md=args.report, report_json=args.json, artifact_json=args.artifact_json, payload=payload)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
