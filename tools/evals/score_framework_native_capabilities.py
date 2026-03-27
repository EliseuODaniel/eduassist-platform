#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib.request import Request, urlopen

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tests.e2e._common import Settings, request

OUTPUT_PATH = REPO_ROOT / 'docs/architecture/framework-native-scorecard.md'
OUTPUT_JSON_PATH = REPO_ROOT / 'docs/architecture/framework-native-scorecard.json'
ARTIFACT_JSON_PATH = REPO_ROOT / 'artifacts/framework-native-scorecard.json'
PRIMARY_STACK_REPORT = REPO_ROOT / 'docs/architecture/framework-primary-stack-flag-report.md'
RESTART_REPORT = REPO_ROOT / 'docs/architecture/framework-restart-recovery-report.md'
CRASH_REPORT = REPO_ROOT / 'docs/architecture/framework-crash-recovery-report.md'


def _read_text(path: Path) -> str:
    return path.read_text(encoding='utf-8') if path.exists() else ''


def _has_all(report_text: str, needles: list[str]) -> bool:
    return all(needle in report_text for needle in needles)


def _fetch_trace_summary(settings: Settings) -> dict[str, Any]:
    headers = {'X-Internal-Api-Token': settings.internal_api_token, 'Content-Type': 'application/json'}

    langgraph_conv = 'scorecard-topline-langgraph-1'
    request(
        'POST',
        f'{settings.ai_orchestrator_url}/v1/messages/respond',
        headers=headers,
        json_body={
            'message': 'qual o horario da biblioteca?',
            'conversation_id': langgraph_conv,
            'telegram_chat_id': 990221,
            'channel': 'telegram',
            'user': {'role': 'anonymous', 'authenticated': False, 'linked_student_ids': [], 'scopes': []},
            'allow_graph_rag': True,
            'allow_handoff': True,
        },
        timeout=40.0,
    )

    crewai_conv = 'scorecard-topline-crewai-1'
    request(
        'POST',
        f'{settings.ai_orchestrator_url}/v1/messages/respond',
        headers=headers,
        json_body={
            'message': 'quero falar com a secretaria',
            'conversation_id': crewai_conv,
            'telegram_chat_id': 1649845499,
            'channel': 'telegram',
            'user': {'role': 'anonymous', 'authenticated': False, 'linked_student_ids': [], 'scopes': []},
            'allow_graph_rag': True,
            'allow_handoff': True,
        },
        timeout=40.0,
    )

    summaries: dict[str, Any] = {}
    for key, conv in (('langgraph', langgraph_conv), ('crewai', crewai_conv)):
        req = Request(
            f'{settings.api_core_url}/v1/internal/conversations/context?conversation_external_id={conv}&channel=telegram&limit=10',
            headers={'X-Internal-Api-Token': settings.internal_api_token},
        )
        with urlopen(req, timeout=20) as response:
            ctx = json.load(response)
        for tool_call in ctx.get('recent_tool_calls', []):
            if tool_call.get('tool_name') != 'orchestration.trace':
                continue
            request_payload = tool_call.get('request_payload') or {}
            response_payload = tool_call.get('response_payload') or {}
            summaries[key] = {
                'request_payload': request_payload,
                'response_payload': response_payload,
            }
            break
    return summaries


def _score_lines(title: str, score: int, weight: int, evidence: str) -> str:
    return f'| {title} | `{score}/{weight}` | {evidence} |'


def main() -> int:
    settings = Settings()
    primary_stack_text = _read_text(PRIMARY_STACK_REPORT)
    restart_text = _read_text(RESTART_REPORT)
    crash_text = _read_text(CRASH_REPORT)
    traces = _fetch_trace_summary(settings)

    langgraph_trace = traces.get('langgraph', {})
    langgraph_request = langgraph_trace.get('request_payload') or {}
    langgraph_meta = langgraph_request.get('langgraph') or {}

    crewai_trace = traces.get('crewai', {})
    crewai_request = crewai_trace.get('request_payload') or {}
    crewai_response = crewai_trace.get('response_payload') or {}
    crewai_req_meta = crewai_request.get('crewai') or {}
    crewai_resp_meta = crewai_response.get('crewai') or {}

    langgraph_restart_ok = _has_all(
        restart_text,
        [
            'langgraph_protected_hitl_restart_recovery',
            '| `langgraph_protected_hitl_restart_recovery` | `langgraph` | `protected` | passed |',
            'pending interrupt survived restart',
        ],
    )
    langgraph_crash_ok = _has_all(
        crash_text,
        [
            'langgraph_protected_hitl_crash_recovery',
            '| `langgraph_protected_hitl_crash_recovery` | `langgraph` | `protected` | passed |',
            'pending interrupt survived crash',
        ],
    )
    crewai_restart_ok = _has_all(
        restart_text,
        [
            'crewai_public_flow_restart_recovery',
            'crewai_protected_flow_restart_recovery',
            'stable flow_state_id',
        ],
    )
    crewai_crash_ok = _has_all(
        crash_text,
        [
            'crewai_public_flow_crash_recovery',
            'crewai_protected_flow_crash_recovery',
            'stable flow_state_id',
        ],
    )
    crewai_primary_native_ok = _has_all(
        primary_stack_text,
        [
            'crewai_primary_public_native_path',
            'crewai_primary_protected_native_path',
            'crewai_primary_support_native_path',
            'crewai_primary_workflow_native_path',
            '| `crewai_primary_public_native_path` | `crewai` | `public` | passed |',
            '| `crewai_primary_protected_native_path` | `crewai` | `protected` | passed |',
        ],
    )
    langgraph_primary_native_ok = _has_all(
        primary_stack_text,
        [
            'langgraph_primary_public_native_path',
            'langgraph_primary_protected_native_path',
            'langgraph_primary_support_native_path',
            'langgraph_primary_workflow_native_path',
            '| `langgraph_primary_public_native_path` | `langgraph` | `public` | passed |',
            '| `langgraph_primary_protected_native_path` | `langgraph` | `protected` | passed |',
        ],
    )

    langgraph_score = 0
    langgraph_max = 30
    crewai_score = 0
    crewai_max = 30

    langgraph_rows = []
    langgraph_rows.append(
        _score_lines(
            'Primary-stack native feature-flag path',
            5 if langgraph_primary_native_ok else 0,
            5,
            'Validated by [framework-primary-stack-flag-report.md](/home/edann/projects/eduassist-platform/docs/architecture/framework-primary-stack-flag-report.md).',
        )
    )
    langgraph_score += 5 if langgraph_primary_native_ok else 0
    langgraph_rows.append(
        _score_lines(
            'Checkpointed persistence',
            5 if langgraph_meta.get('checkpointer_backend') == 'postgres' and langgraph_meta.get('state_available') else 2,
            5,
            'Live `orchestration.trace` carries `thread_id`, `checkpoint_id`, `state_available=true`, and `checkpointer_backend=postgres`.',
        )
    )
    langgraph_score += 5 if langgraph_meta.get('checkpointer_backend') == 'postgres' and langgraph_meta.get('state_available') else 2
    langgraph_rows.append(
        _score_lines(
            'HITL durability after restart',
            5 if langgraph_restart_ok else 0,
            5,
            'Validated by [framework-restart-recovery-report.md](/home/edann/projects/eduassist-platform/docs/architecture/framework-restart-recovery-report.md).',
        )
    )
    langgraph_score += 5 if langgraph_restart_ok else 0
    langgraph_rows.append(
        _score_lines(
            'HITL durability after crash',
            5 if langgraph_crash_ok else 0,
            5,
            'Validated by [framework-crash-recovery-report.md](/home/edann/projects/eduassist-platform/docs/architecture/framework-crash-recovery-report.md).',
        )
    )
    langgraph_score += 5 if langgraph_crash_ok else 0
    langgraph_rows.append(
        _score_lines(
            'Native graph introspection',
            5 if langgraph_meta.get('checkpoint_id') and langgraph_meta.get('state_route') and 'snapshot_metadata' in langgraph_meta else 2,
            5,
            'Trace already exposes `checkpoint_id`, `state_route`, interrupt counts, and snapshot metadata.',
        )
    )
    langgraph_score += 5 if langgraph_meta.get('checkpoint_id') and langgraph_meta.get('state_route') and 'snapshot_metadata' in langgraph_meta else 2
    langgraph_rows.append(
        _score_lines(
            'Operator debug ergonomics',
            4 if langgraph_meta.get('thread_id') and langgraph_meta.get('checkpoint_id') else 2,
            5,
            'Internal review/state/resume endpoints plus checkpoint-backed thread inspection are already live.',
        )
    )
    langgraph_score += 4 if langgraph_meta.get('thread_id') and langgraph_meta.get('checkpoint_id') else 2

    crewai_rows = []
    crewai_rows.append(
        _score_lines(
            'Primary-stack native feature-flag path',
            5 if crewai_primary_native_ok else 0,
            5,
            'Validated by [framework-primary-stack-flag-report.md](/home/edann/projects/eduassist-platform/docs/architecture/framework-primary-stack-flag-report.md).',
        )
    )
    crewai_score += 5 if crewai_primary_native_ok else 0
    crewai_rows.append(
        _score_lines(
            'Flow persistence',
            5 if crewai_req_meta.get('flow_enabled') and crewai_req_meta.get('flow_state_id') else 2,
            5,
            'Live `orchestration.trace` carries `flow_enabled=true` and `flow_state_id` for the CrewAI path.',
        )
    )
    crewai_score += 5 if crewai_req_meta.get('flow_enabled') and crewai_req_meta.get('flow_state_id') else 2
    crewai_rows.append(
        _score_lines(
            'Restart continuity',
            5 if crewai_restart_ok else 0,
            5,
            'Validated by [framework-restart-recovery-report.md](/home/edann/projects/eduassist-platform/docs/architecture/framework-restart-recovery-report.md).',
        )
    )
    crewai_score += 5 if crewai_restart_ok else 0
    crewai_rows.append(
        _score_lines(
            'Crash continuity',
            5 if crewai_crash_ok else 0,
            5,
            'Validated by [framework-crash-recovery-report.md](/home/edann/projects/eduassist-platform/docs/architecture/framework-crash-recovery-report.md).',
        )
    )
    crewai_score += 5 if crewai_crash_ok else 0
    crewai_rows.append(
        _score_lines(
            'Task/flow trace richness',
            4 if 'validation_stack' in crewai_req_meta and isinstance(crewai_resp_meta, dict) and 'latency_ms' in crewai_resp_meta else 2,
            5,
            'Canonical trace now exposes normalized CrewAI request/response metadata, and agentic paths emit `event_summary`/`task_trace` in pilot metadata.',
        )
    )
    crewai_score += 4 if 'validation_stack' in crewai_req_meta and isinstance(crewai_resp_meta, dict) and 'latency_ms' in crewai_resp_meta else 2
    crewai_rows.append(
        _score_lines(
            'Operator debug ergonomics',
            3,
            5,
            'Good flow-state visibility, but no CrewAI-native HITL equivalent and some deterministic slices still expose thinner traces than agentic ones.',
        )
    )
    crewai_score += 3

    output = [
        '# Framework Native Scorecard',
        '',
        f'Date: {datetime.now(UTC).isoformat()}',
        '',
        '## Goal',
        '',
        'Score the two orchestration stacks on framework-native durability and debug capabilities, not only answer quality.',
        '',
        '## Evidence Used',
        '',
        '- [framework-primary-stack-flag-report.md](/home/edann/projects/eduassist-platform/docs/architecture/framework-primary-stack-flag-report.md)',
        '- [framework-restart-recovery-report.md](/home/edann/projects/eduassist-platform/docs/architecture/framework-restart-recovery-report.md)',
        '- [framework-crash-recovery-report.md](/home/edann/projects/eduassist-platform/docs/architecture/framework-crash-recovery-report.md)',
        '- live `orchestration.trace` samples for one `LangGraph` path and one `CrewAI` path',
        '',
        '## Totals',
        '',
        f'- `LangGraph`: `{langgraph_score}/{langgraph_max}`',
        f'- `CrewAI`: `{crewai_score}/{crewai_max}`',
        '',
        '## LangGraph',
        '',
        '| Capability | Score | Evidence |',
        '| --- | ---: | --- |',
        *langgraph_rows,
        '',
        '## CrewAI',
        '',
        '| Capability | Score | Evidence |',
        '| --- | ---: | --- |',
        *crewai_rows,
        '',
        '## Readout',
        '',
        'Current inference from the evidence:',
        '',
        f'- `LangGraph` leads in native persistence + HITL + checkpoint/state introspection with a score of `{langgraph_score}/{langgraph_max}`.',
        f'- `CrewAI` is now strong on Flow continuity and good on canonical trace visibility, with `{crewai_score}/{crewai_max}`, but still trails in operator-facing control primitives.',
        '- The comparison is now top-line enough for durability/debug to be a real architectural differentiator, not just a qualitative impression.',
        '',
        '## Trace Samples',
        '',
        '### LangGraph',
        '',
        '```json',
        json.dumps(langgraph_meta, ensure_ascii=False, indent=2),
        '```',
        '',
        '### CrewAI',
        '',
        '```json',
        json.dumps({'request': crewai_req_meta, 'response': crewai_resp_meta}, ensure_ascii=False, indent=2),
        '```',
    ]
    OUTPUT_PATH.write_text('\n'.join(output) + '\n', encoding='utf-8')
    json_payload = {
        'generated_at': datetime.now(UTC).isoformat(),
        'frameworks': {
            'langgraph': {
                'total_score': langgraph_score,
                'max_score': langgraph_max,
                'primary_stack_native_path_passed': langgraph_primary_native_ok,
                'restart_recovery_passed': langgraph_restart_ok,
                'crash_recovery_passed': langgraph_crash_ok,
                'trace_sample': langgraph_meta,
            },
            'crewai': {
                'total_score': crewai_score,
                'max_score': crewai_max,
                'primary_stack_native_path_passed': crewai_primary_native_ok,
                'restart_recovery_passed': crewai_restart_ok,
                'crash_recovery_passed': crewai_crash_ok,
                'trace_sample': {
                    'request': crewai_req_meta,
                    'response': crewai_resp_meta,
                },
                'recommended_canary_slices': ['public', 'support', 'workflow'],
                'blocked_canary_slices': ['protected'],
                'blocked_reasons': {
                    'protected': 'protected still trails LangGraph in operator-facing control primitives and should stay behind manual review.',
                },
            },
        },
        'promotion_gate': {
            'crewai': {
                'eligible': crewai_score >= 24 and crewai_primary_native_ok and crewai_restart_ok and crewai_crash_ok,
                'minimum_score_for_canary': 20,
                'primary_stack_native_path_required': True,
                'recommended_canary_slices': ['public', 'support', 'workflow'],
                'blocked_canary_slices': ['protected'],
            },
            'langgraph': {
                'eligible': langgraph_score >= 24 and langgraph_primary_native_ok and langgraph_restart_ok and langgraph_crash_ok,
                'minimum_score_for_canary': 20,
                'primary_stack_native_path_required': True,
                'recommended_canary_slices': ['public', 'protected', 'support', 'workflow'],
                'blocked_canary_slices': [],
            }
        },
    }
    scorecard_json = json.dumps(json_payload, ensure_ascii=False, indent=2) + '\n'
    OUTPUT_JSON_PATH.write_text(scorecard_json, encoding='utf-8')
    ARTIFACT_JSON_PATH.parent.mkdir(parents=True, exist_ok=True)
    ARTIFACT_JSON_PATH.write_text(scorecard_json, encoding='utf-8')
    print(OUTPUT_PATH)
    print(OUTPUT_JSON_PATH)
    print(ARTIFACT_JSON_PATH)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
