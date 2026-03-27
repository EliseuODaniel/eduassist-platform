#!/usr/bin/env python3
from __future__ import annotations

import asyncio
import json
import os
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

REPO_ROOT = Path(os.getenv('BENCHMARK_REPO_ROOT') or Path(__file__).resolve().parents[2])
AI_ORCHESTRATOR_SRC = REPO_ROOT / 'apps/ai-orchestrator/src'
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
if str(AI_ORCHESTRATOR_SRC) not in sys.path:
    sys.path.insert(0, str(AI_ORCHESTRATOR_SRC))

from ai_orchestrator.graph import to_preview
from ai_orchestrator.langgraph_runtime import (
    get_langgraph_artifacts,
    get_orchestration_state_snapshot,
    resolve_langgraph_thread_id,
    resume_orchestration_graph,
)
from ai_orchestrator.main import Settings as AppSettings
from ai_orchestrator.models import ConversationChannel, MessageResponseRequest, UserContext, UserRole
from ai_orchestrator.runtime import generate_message_response

OUTPUT_PATH = REPO_ROOT / 'docs/architecture/framework-langgraph-user-traffic-hitl-report.md'
OUTPUT_JSON_PATH = REPO_ROOT / 'docs/architecture/framework-langgraph-user-traffic-hitl-report.json'


def _default_runtime_urls() -> dict[str, str]:
    in_container = Path('/.dockerenv').exists()
    if in_container:
        return {
            'api_core_url': 'http://api-core:8000',
            'database_url': 'postgresql://eduassist:eduassist@postgres:5432/eduassist',
            'qdrant_url': 'http://qdrant:6333',
        }
    return {
        'api_core_url': 'http://127.0.0.1:8001',
        'database_url': 'postgresql://eduassist:eduassist@127.0.0.1:5432/eduassist',
        'qdrant_url': 'http://127.0.0.1:6333',
    }


def _make_settings() -> AppSettings:
    defaults = _default_runtime_urls()
    api_core_url = os.getenv('BENCHMARK_API_CORE_URL', defaults['api_core_url'])
    database_url = os.getenv('BENCHMARK_DATABASE_URL', defaults['database_url'])
    qdrant_url = os.getenv('BENCHMARK_QDRANT_URL', defaults['qdrant_url'])
    return AppSettings(
        api_core_url=api_core_url,
        database_url=database_url,
        qdrant_url=qdrant_url,
        langgraph_checkpointer_enabled=True,
        langgraph_checkpointer_url=database_url,
        langgraph_hitl_enabled=True,
        langgraph_hitl_default_slices='support,protected',
        langgraph_hitl_user_traffic_enabled=True,
        langgraph_hitl_user_traffic_slices='support,protected',
        internal_api_token='dev-internal-token',
    )


def _pending_interrupt_count(snapshot: Any) -> int:
    interrupts = getattr(snapshot, 'interrupts', None) or ()
    return len(list(interrupts))


async def _run_case(
    *,
    settings: AppSettings,
    case_id: str,
    message: str,
    telegram_chat_id: int,
    authenticated: bool,
    expected_slice: str,
    resume_value: dict[str, Any],
) -> dict[str, Any]:
    request = MessageResponseRequest(
        message=message,
        conversation_id=case_id,
        telegram_chat_id=telegram_chat_id,
        channel=ConversationChannel.telegram,
        user=UserContext(
            role=UserRole.guardian if authenticated else UserRole.anonymous,
            authenticated=authenticated,
            linked_student_ids=[],
            scopes=[],
        ),
        allow_graph_rag=True,
        allow_handoff=True,
    )
    response = await generate_message_response(
        request=request,
        settings=settings,
        engine_name='langgraph',
        engine_mode='langgraph',
    )
    thread_id = resolve_langgraph_thread_id(
        conversation_external_id=case_id,
        channel='telegram',
        telegram_chat_id=telegram_chat_id,
    )
    graph = get_langgraph_artifacts(settings).graph
    snapshot_before = get_orchestration_state_snapshot(
        graph=graph,
        thread_id=thread_id,
        subgraphs=True,
    )
    pending_before = _pending_interrupt_count(snapshot_before)
    resume_state = resume_orchestration_graph(
        graph=graph,
        thread_id=thread_id,
        resume_value=resume_value,
    )
    snapshot_after = get_orchestration_state_snapshot(
        graph=graph,
        thread_id=thread_id,
        subgraphs=True,
    )
    pending_after = _pending_interrupt_count(snapshot_after)
    resumed_preview = to_preview(resume_state if isinstance(resume_state, dict) else dict(getattr(snapshot_after, 'values', {}) or {}))

    passed = (
        response.reason == 'langgraph_hitl_pending_review'
        and 'pending_human_review' in response.risk_flags
        and pending_before > 0
        and pending_after == 0
        and bool(thread_id)
        and expected_slice in response.graph_path
    )
    return {
        'case_id': case_id,
        'slice': expected_slice,
        'message': message,
        'passed': passed,
        'thread_id': thread_id,
        'response_reason': response.reason,
        'response_mode': response.mode.value,
        'response_graph_path': response.graph_path,
        'response_risk_flags': response.risk_flags,
        'pending_before_resume': pending_before,
        'pending_after_resume': pending_after,
        'resumed_reason': resumed_preview.reason,
        'resumed_mode': resumed_preview.mode.value,
        'resumed_graph_path': resumed_preview.graph_path,
    }


async def _run() -> dict[str, Any]:
    settings = _make_settings()
    cases = [
        await _run_case(
            settings=settings,
            case_id='langgraph-user-traffic-hitl-support-1',
            message='quero falar com a secretaria',
            telegram_chat_id=1649845499,
            authenticated=False,
            expected_slice='support_slice',
            resume_value={'approved': True, 'operator': 'codex'},
        ),
        await _run_case(
            settings=settings,
            case_id='langgraph-user-traffic-hitl-protected-1',
            message='qual meu acesso? a que dados',
            telegram_chat_id=1649845499,
            authenticated=True,
            expected_slice='protected_slice',
            resume_value={'approved': False, 'operator': 'codex', 'reason': 'manual protected review denial test'},
        ),
    ]
    passed = sum(1 for item in cases if item['passed'])
    return {
        'generated_at': datetime.now(UTC).isoformat(),
        'summary': {
            'passed': passed,
            'total': len(cases),
            'all_passed': passed == len(cases),
        },
        'cases': cases,
    }


def _write_report(payload: dict[str, Any]) -> None:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_JSON_PATH.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        '# LangGraph User-Traffic HITL Report',
        '',
        f"Date: {payload['generated_at']}",
        '',
        '## Goal',
        '',
        'Validate that normal user traffic can enter native LangGraph `interrupt()` review paths, persist the pending state, and resume the same thread safely.',
        '',
        '## Summary',
        '',
        f"- Passed: `{payload['summary']['passed']}/{payload['summary']['total']}`",
        f"- All passed: `{'yes' if payload['summary']['all_passed'] else 'no'}`",
        '',
        '## Cases',
        '',
        '| Case | Slice | Result | Evidence |',
        '| --- | --- | --- | --- |',
    ]
    for case in payload['cases']:
        evidence = (
            f"reason=`{case['response_reason']}`, pending_before=`{case['pending_before_resume']}`, "
            f"pending_after=`{case['pending_after_resume']}`, graph_path=`{' -> '.join(case['response_graph_path'])}`"
        )
        lines.append(
            f"| `{case['case_id']}` | `{case['slice']}` | `{'passed' if case['passed'] else 'failed'}` | {evidence} |"
        )
    lines.extend(
        [
            '',
            '## Raw JSON',
            '',
            '```json',
            json.dumps(payload, ensure_ascii=False, indent=2),
            '```',
        ]
    )
    OUTPUT_PATH.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    OUTPUT_JSON_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def main() -> int:
    payload = asyncio.run(_run())
    _write_report(payload)
    print(OUTPUT_PATH)
    print(OUTPUT_JSON_PATH)
    return 0 if payload['summary']['all_passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
