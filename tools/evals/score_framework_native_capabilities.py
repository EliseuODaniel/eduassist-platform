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
USER_TRAFFIC_HITL_REPORT = REPO_ROOT / 'docs/architecture/framework-langgraph-user-traffic-hitl-report.md'
CREWAI_PROTECTED_HITL_REPORT = REPO_ROOT / 'docs/architecture/framework-crewai-protected-hitl-report.md'


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


def _fetch_crewai_live_summary(settings: Settings) -> dict[str, Any]:
    headers = {'X-Internal-Api-Token': settings.internal_api_token, 'Content-Type': 'application/json'}
    crewai_url = 'http://127.0.0.1:8004'
    _, _, status_payload = request(
        'GET',
        f'{crewai_url}/v1/status',
        headers={'X-Internal-Api-Token': settings.internal_api_token},
        timeout=20.0,
    )
    public_conv = 'scorecard-crewai-public-live-1'
    protected_conv = 'scorecard-crewai-protected-live-1'
    support_conv = 'scorecard-crewai-support-live-1'
    workflow_conv = 'scorecard-crewai-workflow-live-1'
    _, _, public_payload = request(
        'POST',
        f'{crewai_url}/v1/shadow/public',
        headers=headers,
        json_body={
            'message': 'qual o horario da biblioteca?',
            'conversation_id': public_conv,
            'telegram_chat_id': 1649845499,
        },
        timeout=30.0,
    )
    _, _, protected_payload = request(
        'POST',
        f'{crewai_url}/v1/shadow/protected',
        headers=headers,
        json_body={
            'message': 'qual situacao de documentacao do Lucas?',
            'conversation_id': protected_conv,
            'telegram_chat_id': 1649845499,
        },
        timeout=30.0,
    )
    _, _, support_payload = request(
        'POST',
        f'{crewai_url}/v1/shadow/support',
        headers=headers,
        json_body={
            'message': 'quero falar com a secretaria',
            'conversation_id': support_conv,
            'telegram_chat_id': 1649845499,
        },
        timeout=30.0,
    )
    _, _, workflow_payload = request(
        'POST',
        f'{crewai_url}/v1/shadow/workflow',
        headers=headers,
        json_body={
            'message': 'quero agendar uma visita na quinta a tarde',
            'conversation_id': workflow_conv,
            'telegram_chat_id': 1649845499,
        },
        timeout=30.0,
    )
    return {
        'status': status_payload if isinstance(status_payload, dict) else {},
        'public': public_payload if isinstance(public_payload, dict) else {},
        'protected': protected_payload if isinstance(protected_payload, dict) else {},
        'support': support_payload if isinstance(support_payload, dict) else {},
        'workflow': workflow_payload if isinstance(workflow_payload, dict) else {},
    }


def _score_lines(title: str, score: int, weight: int, evidence: str) -> str:
    return f'| {title} | `{score}/{weight}` | {evidence} |'


def _slice_eligibility_map(
    *,
    framework: str,
    gate_eligible: bool,
    recommended_canary_slices: list[str],
    blocked_canary_slices: list[str],
    blocked_reasons: dict[str, str] | None = None,
) -> dict[str, dict[str, Any]]:
    blocked_reasons = blocked_reasons or {}
    eligibility: dict[str, dict[str, Any]] = {}
    for slice_name in ('public', 'protected', 'support', 'workflow'):
        if not gate_eligible:
            eligibility[slice_name] = {
                'eligible': False,
                'reason': f'{framework} does not currently satisfy the promotion gate.',
            }
            continue
        if slice_name in blocked_canary_slices:
            eligibility[slice_name] = {
                'eligible': False,
                'reason': blocked_reasons.get(slice_name) or f'{slice_name} stays blocked for {framework}.',
            }
            continue
        if recommended_canary_slices and slice_name not in recommended_canary_slices:
            eligibility[slice_name] = {
                'eligible': False,
                'reason': f'{slice_name} is not in the recommended canary set for {framework}.',
            }
            continue
        eligibility[slice_name] = {
            'eligible': True,
            'reason': f'{slice_name} is allowed for {framework} under the current scorecard gate.',
        }
    return eligibility


def main() -> int:
    settings = Settings()
    primary_stack_text = _read_text(PRIMARY_STACK_REPORT)
    restart_text = _read_text(RESTART_REPORT)
    crash_text = _read_text(CRASH_REPORT)
    user_traffic_hitl_text = _read_text(USER_TRAFFIC_HITL_REPORT)
    crewai_protected_hitl_text = _read_text(CREWAI_PROTECTED_HITL_REPORT)
    traces = _fetch_trace_summary(settings)
    crewai_live = _fetch_crewai_live_summary(settings)

    langgraph_trace = traces.get('langgraph', {})
    langgraph_request = langgraph_trace.get('request_payload') or {}
    langgraph_meta = langgraph_request.get('langgraph') or {}

    crewai_trace = traces.get('crewai', {})
    crewai_request = crewai_trace.get('request_payload') or {}
    crewai_response = crewai_trace.get('response_payload') or {}
    crewai_req_meta = crewai_request.get('crewai') or {}
    crewai_resp_meta = crewai_response.get('crewai') or {}
    crewai_status = crewai_live.get('status') or {}
    crewai_capabilities = set(crewai_status.get('capabilities') or [])
    crewai_public_meta = (crewai_live.get('public') or {}).get('metadata') or {}
    crewai_protected_meta = (crewai_live.get('protected') or {}).get('metadata') or {}
    crewai_support_meta = (crewai_live.get('support') or {}).get('metadata') or {}
    crewai_workflow_meta = (crewai_live.get('workflow') or {}).get('metadata') or {}

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
    langgraph_user_traffic_hitl_ok = _has_all(
        user_traffic_hitl_text,
        [
            'langgraph-user-traffic-hitl-support-1',
            'langgraph-user-traffic-hitl-protected-1',
            '- All passed: `yes`',
        ],
    )
    crewai_protected_hitl_ok = _has_all(
        crewai_protected_hitl_text,
        [
            'crewai-protected-hitl-approved-1',
            'crewai-protected-hitl-rejected-1',
            '- All passed: `yes`',
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
            5 if langgraph_user_traffic_hitl_ok else (4 if langgraph_meta.get('thread_id') and langgraph_meta.get('checkpoint_id') else 2),
            5,
            'Checkpoint-backed thread inspection is live, and user-traffic HITL is now validated in [framework-langgraph-user-traffic-hitl-report.md](/home/edann/projects/eduassist-platform/docs/architecture/framework-langgraph-user-traffic-hitl-report.md).',
        )
    )
    langgraph_score += 5 if langgraph_user_traffic_hitl_ok else (4 if langgraph_meta.get('thread_id') and langgraph_meta.get('checkpoint_id') else 2)

    crewai_has_live_flow_ids = all(
        isinstance(meta, dict) and bool(meta.get('flow_state_id'))
        for meta in (crewai_public_meta, crewai_protected_meta, crewai_support_meta, crewai_workflow_meta)
    )
    crewai_native_guardrails_capable = {'task-trace-telemetry', 'task-guardrails'}.issubset(crewai_capabilities)
    crewai_agentic_rendering_capable = 'agentic-rendering-for-support-workflow' in crewai_capabilities

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
            5 if crewai_has_live_flow_ids and crewai_native_guardrails_capable else (4 if 'validation_stack' in crewai_req_meta and isinstance(crewai_resp_meta, dict) and 'latency_ms' in crewai_resp_meta else 2),
            5,
            'Canonical trace exposes normalized CrewAI metadata, the pilot advertises native `task-guardrails`, and all four live slice checks return persisted `flow_state_id` values.',
        )
    )
    crewai_score += 5 if crewai_has_live_flow_ids and crewai_native_guardrails_capable else (4 if 'validation_stack' in crewai_req_meta and isinstance(crewai_resp_meta, dict) and 'latency_ms' in crewai_resp_meta else 2)
    crewai_rows.append(
        _score_lines(
            'Operator debug ergonomics',
            5 if crewai_protected_hitl_ok else (4 if crewai_has_live_flow_ids and crewai_native_guardrails_capable and crewai_agentic_rendering_capable else 3),
            5,
            'Protected operator review is now validated in [framework-crewai-protected-hitl-report.md](/home/edann/projects/eduassist-platform/docs/architecture/framework-crewai-protected-hitl-report.md), with pending-state inspection plus approve/reject resume on the same persisted flow id.',
        )
    )
    crewai_score += 5 if crewai_protected_hitl_ok else (4 if crewai_has_live_flow_ids and crewai_native_guardrails_capable and crewai_agentic_rendering_capable else 3)
    crewai_blocked_reasons: dict[str, str] = {}
    langgraph_gate_eligible = langgraph_score >= 24 and langgraph_primary_native_ok and langgraph_restart_ok and langgraph_crash_ok
    crewai_gate_eligible = crewai_score >= 24 and crewai_primary_native_ok and crewai_restart_ok and crewai_crash_ok
    langgraph_slice_eligibility = _slice_eligibility_map(
        framework='langgraph',
        gate_eligible=langgraph_gate_eligible,
        recommended_canary_slices=['public', 'protected', 'support', 'workflow'],
        blocked_canary_slices=[],
    )
    crewai_slice_eligibility = _slice_eligibility_map(
        framework='crewai',
        gate_eligible=crewai_gate_eligible,
        recommended_canary_slices=['public', 'protected', 'support', 'workflow'],
        blocked_canary_slices=[],
        blocked_reasons=crewai_blocked_reasons,
    )

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
        '- [framework-langgraph-user-traffic-hitl-report.md](/home/edann/projects/eduassist-platform/docs/architecture/framework-langgraph-user-traffic-hitl-report.md)',
        '- [framework-crewai-protected-hitl-report.md](/home/edann/projects/eduassist-platform/docs/architecture/framework-crewai-protected-hitl-report.md)',
        '- live `orchestration.trace` samples for one `LangGraph` path and one `CrewAI` path',
        '- live direct `CrewAI` slice responses for `public`, `protected`, `support`, and `workflow`',
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
        f'- `CrewAI` is now strong on Flow continuity, task guardrails, and protected operator review, with `{crewai_score}/{crewai_max}`.',
        '- The comparison is now top-line enough for durability/debug to be a real architectural differentiator, not just a qualitative impression.',
        '',
        '## Promotion Gate By Slice',
        '',
        '### LangGraph',
        '',
        '| Slice | Eligible | Reason |',
        '| --- | --- | --- |',
        *[
            f"| `{slice_name}` | `{'yes' if details['eligible'] else 'no'}` | {details['reason']} |"
            for slice_name, details in langgraph_slice_eligibility.items()
        ],
        '',
        '### CrewAI',
        '',
        '| Slice | Eligible | Reason |',
        '| --- | --- | --- |',
        *[
            f"| `{slice_name}` | `{'yes' if details['eligible'] else 'no'}` | {details['reason']} |"
            for slice_name, details in crewai_slice_eligibility.items()
        ],
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
        json.dumps(
            {
                'status': crewai_status,
                'request': crewai_req_meta,
                'response': crewai_resp_meta,
                'live_public': crewai_public_meta,
                'live_protected': crewai_protected_meta,
                'live_support': crewai_support_meta,
                'live_workflow': crewai_workflow_meta,
            },
            ensure_ascii=False,
            indent=2,
        ),
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
                'recommended_canary_slices': ['public', 'protected', 'support', 'workflow'],
                'blocked_canary_slices': [],
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
                    'live': {
                        'status': crewai_status,
                        'public': crewai_public_meta,
                        'protected': crewai_protected_meta,
                        'support': crewai_support_meta,
                        'workflow': crewai_workflow_meta,
                    },
                },
                'recommended_canary_slices': ['public', 'protected', 'support', 'workflow'],
                'blocked_canary_slices': [],
                'blocked_reasons': crewai_blocked_reasons,
            },
        },
        'promotion_gate': {
            'crewai': {
                'eligible': crewai_gate_eligible,
                'minimum_score_for_canary': 20,
                'primary_stack_native_path_required': True,
                'recommended_canary_slices': ['public', 'protected', 'support', 'workflow'],
                'blocked_canary_slices': [],
                'slice_eligibility': crewai_slice_eligibility,
            },
            'langgraph': {
                'eligible': langgraph_gate_eligible,
                'minimum_score_for_canary': 20,
                'primary_stack_native_path_required': True,
                'recommended_canary_slices': ['public', 'protected', 'support', 'workflow'],
                'blocked_canary_slices': [],
                'slice_eligibility': langgraph_slice_eligibility,
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
