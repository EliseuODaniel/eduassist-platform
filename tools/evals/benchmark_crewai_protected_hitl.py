#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from datetime import UTC, datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tests.e2e._common import Settings, assert_condition, request

OUTPUT_PATH = REPO_ROOT / 'docs/architecture/framework-crewai-protected-hitl-report.md'
OUTPUT_JSON_PATH = REPO_ROOT / 'docs/architecture/framework-crewai-protected-hitl-report.json'


def _headers(settings: Settings) -> dict[str, str]:
    return {
        'X-Internal-Api-Token': settings.internal_api_token,
        'Content-Type': 'application/json',
    }


def _start_review(settings: Settings, *, conversation_id: str, message: str) -> dict[str, object]:
    status, _, payload = request(
        'POST',
        'http://127.0.0.1:8004/v1/internal/hitl/review/protected',
        headers=_headers(settings),
        json_body={
            'message': message,
            'conversation_id': conversation_id,
            'telegram_chat_id': 1649845499,
            'channel': 'telegram',
        },
        timeout=30.0,
    )
    assert_condition(status == 200 and isinstance(payload, dict), f'crewai_hitl_start_failed:{conversation_id}')
    return payload


def _get_state(settings: Settings, *, conversation_id: str) -> dict[str, object]:
    status, _, payload = request(
        'GET',
        f'http://127.0.0.1:8004/v1/internal/hitl/state/protected?conversation_id={conversation_id}&channel=telegram',
        headers={'X-Internal-Api-Token': settings.internal_api_token},
        timeout=30.0,
    )
    assert_condition(status == 200 and isinstance(payload, dict), f'crewai_hitl_state_failed:{conversation_id}')
    return payload


def _resume(settings: Settings, *, conversation_id: str, feedback: str) -> dict[str, object]:
    status, _, payload = request(
        'POST',
        'http://127.0.0.1:8004/v1/internal/hitl/resume/protected',
        headers=_headers(settings),
        json_body={
            'conversation_id': conversation_id,
            'telegram_chat_id': 1649845499,
            'channel': 'telegram',
            'feedback': feedback,
        },
        timeout=30.0,
    )
    assert_condition(status == 200 and isinstance(payload, dict), f'crewai_hitl_resume_failed:{conversation_id}')
    return payload


def _run_case(settings: Settings, *, case_id: str, message: str, feedback: str, expected_reason: str, expected_contains: str) -> dict[str, object]:
    started = _start_review(settings, conversation_id=case_id, message=message)
    state_before = _get_state(settings, conversation_id=case_id)
    resumed = _resume(settings, conversation_id=case_id, feedback=feedback)
    state_after = _get_state(settings, conversation_id=case_id)

    started_status = str(started.get('status', ''))
    started_result = started.get('result') if isinstance(started.get('result'), dict) else {}
    resumed_result = resumed.get('result') if isinstance(resumed.get('result'), dict) else {}
    resumed_metadata = resumed_result.get('metadata') if isinstance(resumed_result.get('metadata'), dict) else {}
    resumed_answer = resumed_metadata.get('answer') if isinstance(resumed_metadata.get('answer'), dict) else {}
    resumed_text = str(resumed_answer.get('answer_text', '') or '')
    resumed_reason = str(resumed_result.get('reason', '') or '')

    passed = (
        started_status == 'pending'
        and bool(state_before.get('pending'))
        and resumed.get('status') == 'completed'
        and not bool(state_after.get('pending'))
        and resumed_reason == expected_reason
        and expected_contains.lower() in resumed_text.lower()
    )
    return {
        'case_id': case_id,
        'message': message,
        'feedback': feedback,
        'passed': passed,
        'started_status': started_status,
        'pending_before_resume': bool(state_before.get('pending')),
        'pending_after_resume': bool(state_after.get('pending')),
        'resumed_reason': resumed_reason,
        'resumed_text': resumed_text,
    }


def main() -> int:
    settings = Settings()
    cases = [
        _run_case(
            settings,
            case_id='crewai-protected-hitl-approved-1',
            message='qual meu acesso? a que dados',
            feedback='approved',
            expected_reason='crewai_protected_review_approved',
            expected_contains='vinculada',
        ),
        _run_case(
            settings,
            case_id='crewai-protected-hitl-rejected-1',
            message='qual situacao de documentacao do Lucas?',
            feedback='rejected',
            expected_reason='crewai_protected_review_rejected',
            expected_contains='nao foi liberada',
        ),
    ]
    payload = {
        'generated_at': datetime.now(UTC).isoformat(),
        'summary': {
            'passed': sum(1 for case in cases if case['passed']),
            'total': len(cases),
            'all_passed': all(case['passed'] for case in cases),
        },
        'cases': cases,
    }
    lines = [
        '# CrewAI Protected HITL Report',
        '',
        f"Date: {payload['generated_at']}",
        '',
        '## Goal',
        '',
        'Validate that the CrewAI protected slice can pause for operator review, expose pending state, and resume with approve/reject outcomes on the same persisted flow id.',
        '',
        '## Summary',
        '',
        f"- Passed: `{payload['summary']['passed']}/{payload['summary']['total']}`",
        f"- All passed: `{'yes' if payload['summary']['all_passed'] else 'no'}`",
        '',
        '## Cases',
        '',
        '| Case | Result | Evidence |',
        '| --- | --- | --- |',
    ]
    for case in cases:
        evidence = (
            f"started=`{case['started_status']}`, pending_before=`{case['pending_before_resume']}`, "
            f"pending_after=`{case['pending_after_resume']}`, reason=`{case['resumed_reason']}`"
        )
        lines.append(f"| `{case['case_id']}` | `{'passed' if case['passed'] else 'failed'}` | {evidence} |")
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
    print(OUTPUT_PATH)
    print(OUTPUT_JSON_PATH)
    return 0 if payload['summary']['all_passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
