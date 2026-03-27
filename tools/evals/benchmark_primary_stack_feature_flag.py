#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path
from textwrap import dedent
from typing import Any
from urllib.request import Request, urlopen

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tests.e2e._common import Settings, assert_condition

DEFAULT_DATASET = REPO_ROOT / 'tests/evals/datasets/framework_primary_stack_flag_cases.json'
DEFAULT_REPORT = REPO_ROOT / 'docs/architecture/framework-primary-stack-flag-report.md'
ORCHESTRATOR_CONTAINER = 'eduassist-ai-orchestrator'


def _headers(settings: Settings, *, json_content: bool = False) -> dict[str, str]:
    headers = {'X-Internal-Api-Token': settings.internal_api_token}
    if json_content:
        headers['Content-Type'] = 'application/json'
    return headers


def _read_json_via_http(url: str, headers: dict[str, str]) -> Any:
    request = Request(url, headers=headers)
    with urlopen(request, timeout=30) as response:
        return json.load(response)


def _docker_exec_python(script_text: str) -> dict[str, Any]:
    local_script = REPO_ROOT / 'artifacts' / 'tmp_primary_stack_flag_eval.py'
    local_script.parent.mkdir(parents=True, exist_ok=True)
    local_script.write_text(script_text, encoding='utf-8')
    subprocess.run(
        ['docker', 'cp', str(local_script), f'{ORCHESTRATOR_CONTAINER}:/tmp/primary_stack_flag_eval.py'],
        cwd=REPO_ROOT,
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    completed = subprocess.run(
        [
            'docker',
            'exec',
            ORCHESTRATOR_CONTAINER,
            'sh',
            '-lc',
            'PYTHONPATH=/workspace/apps/ai-orchestrator/src /workspace/apps/ai-orchestrator/.venv/bin/python /tmp/primary_stack_flag_eval.py',
        ],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(completed.stdout)


def _run_case(case: dict[str, Any], settings: Settings) -> dict[str, Any]:
    primary_stack = str(case.get('primary_stack') or 'crewai').strip().lower()
    base_conversation_id = str(case['conversation_id']).strip()
    conversation_id = f'{base_conversation_id}-{primary_stack}-primary'
    script_text = dedent(
        f"""
        import asyncio, json
        from ai_orchestrator.main import Settings
        from ai_orchestrator.engine_selector import build_engine_bundle
        from ai_orchestrator.models import MessageResponseRequest

        async def main():
            settings = Settings(
                orchestrator_engine='crewai' if {json.dumps(primary_stack)} == 'langgraph' else 'langgraph',
                feature_flag_primary_orchestration_stack={json.dumps(primary_stack)},
                crewai_pilot_url='http://ai-orchestrator-crewai:8000',
                internal_api_token={json.dumps(settings.internal_api_token)},
                orchestrator_experiment_enabled=False,
            )
            request = MessageResponseRequest(
                message={json.dumps(case['message'])},
                conversation_id={json.dumps(conversation_id)},
                telegram_chat_id={json.dumps(case['telegram_chat_id'])},
                channel='telegram',
            )
            bundle = build_engine_bundle(settings, request=request)
            response = await bundle.primary.respond(request=request, settings=settings, engine_mode=bundle.mode)
            print(json.dumps({{
                'mode': bundle.mode,
                'engine': bundle.primary.name,
                'message_text': response.message_text,
                'response_mode': response.mode.value,
                'graph_path': response.graph_path,
                'selected_tools': response.selected_tools,
                'classification': {{
                    'domain': response.classification.domain.value,
                    'access_tier': response.classification.access_tier.value,
                }},
                'suggested_replies': [item.text for item in response.suggested_replies],
            }}, ensure_ascii=False))

        asyncio.run(main())
        """
    ).strip()
    runtime_result = _docker_exec_python(script_text)

    trace_context = _read_json_via_http(
        f'{settings.api_core_url}/v1/internal/conversations/context?conversation_external_id={conversation_id}&channel=telegram&limit=10',
        _headers(settings),
    )
    trace = None
    for tool_call in reversed(trace_context.get('recent_tool_calls', [])):
        if tool_call.get('tool_name') == 'orchestration.trace':
            trace = tool_call
            break

    assert_condition(runtime_result['classification']['domain'] == case['expected_domain'], f'{case["id"]}:wrong_domain')
    assert_condition(runtime_result['classification']['access_tier'] == case['expected_access_tier'], f'{case["id"]}:wrong_access_tier')
    for tool_name in case.get('expected_selected_tools') or []:
        assert_condition(tool_name in runtime_result['selected_tools'], f'{case["id"]}:missing_tool:{tool_name}')
    for node_name in case.get('expected_graph_path_nodes') or []:
        assert_condition(node_name in runtime_result['graph_path'], f'{case["id"]}:missing_graph_path:{node_name}')

    assert_condition(isinstance(trace, dict), f'{case["id"]}:missing_trace')
    request_payload = trace.get('request_payload') or {}
    response_payload = trace.get('response_payload') or {}
    assert_condition(runtime_result['engine'] == primary_stack, f'{case["id"]}:wrong_primary_engine')
    assert_condition(runtime_result['mode'] == primary_stack, f'{case["id"]}:wrong_bundle_mode')
    assert_condition(request_payload.get('engine_name') == primary_stack, f'{case["id"]}:trace_wrong_engine')
    assert_condition(request_payload.get('engine_mode') == primary_stack, f'{case["id"]}:trace_wrong_mode')

    trace_section = response_payload.get(primary_stack) or {}
    if primary_stack == 'crewai':
        assert_condition('langgraph' not in request_payload, f'{case["id"]}:langgraph_leaked_into_trace')
        assert_condition('crewai' in request_payload, f'{case["id"]}:missing_crewai_trace_request')
    else:
        assert_condition('crewai' not in request_payload, f'{case["id"]}:crewai_leaked_into_trace')
        assert_condition('langgraph' in request_payload, f'{case["id"]}:missing_langgraph_trace_request')
    assert_condition(
        (trace_section.get('timeline_kind') == case['expected_trace_timeline_kind']),
        f'{case["id"]}:wrong_trace_timeline_kind',
    )

    return {
        'id': case['id'],
        'primary_stack': primary_stack,
        'slice': case['slice'],
        'conversation_id': conversation_id,
        'passed': True,
        'engine': runtime_result['engine'],
        'mode': runtime_result['mode'],
        'graph_path': runtime_result['graph_path'],
        'selected_tools': runtime_result['selected_tools'],
        'suggested_replies': runtime_result['suggested_replies'],
        'trace_timeline_kind': trace_section.get('timeline_kind'),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--dataset', type=Path, default=DEFAULT_DATASET)
    parser.add_argument('--report', type=Path, default=DEFAULT_REPORT)
    args = parser.parse_args()

    settings = Settings()
    cases = json.loads(args.dataset.read_text(encoding='utf-8'))
    results = [_run_case(case, settings) for case in cases]

    lines = [
        '# Framework Primary Stack Feature Flag Report',
        '',
        f'Date: {datetime.now(UTC).isoformat()}',
        '',
        '## Goal',
        '',
        'Validate that `FEATURE_FLAG_PRIMARY_ORCHESTRATION_STACK` can switch the primary path to either framework natively, without leaking the alternate runtime metadata into the canonical trace.',
        '',
        '## Results',
        '',
        '| Case | Primary | Slice | Result | Notes |',
        '| --- | --- | --- | --- | --- |',
    ]
    for result in results:
        lines.append(
            f"| `{result['id']}` | `{result['primary_stack']}` | `{result['slice']}` | passed | engine `{result['engine']}`, mode `{result['mode']}`, timeline `{result['trace_timeline_kind']}` |"
        )

    stacks = {}
    for result in results:
        stacks.setdefault(result['primary_stack'], []).append(result)

    lines.extend(
        [
            '',
            '## Summary',
            '',
            f"- passed `{sum(1 for item in results if item['passed'])}/{len(results)}` cases",
            f"- `crewai` passed `{sum(1 for item in stacks.get('crewai', []) if item['passed'])}/{len(stacks.get('crewai', []))}` native-path cases",
            f"- `langgraph` passed `{sum(1 for item in stacks.get('langgraph', []) if item['passed'])}/{len(stacks.get('langgraph', []))}` native-path cases",
            '- canonical traces stayed on the selected framework metadata only for these primary-path runs',
            '- `graph_path` and response shaping stayed native to the selected framework under the feature flag',
            '',
        ]
    )
    args.report.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(args.report)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
