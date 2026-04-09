from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any
from uuid import uuid4

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'e2e'))

from _common import Settings, assert_condition, request, wait_for_health


ROOT_DIR = Path(__file__).resolve().parents[2]
DEFAULT_DATASET_PATH = ROOT_DIR / 'tests' / 'evals' / 'datasets' / 'dedicated_runtime_cases.json'
DEFAULT_OUTPUT_PATH = ROOT_DIR / 'artifacts' / 'dedicated-runtime-quality-report.json'
RUN_ID = uuid4().hex[:8]


def _normalize(value: str) -> str:
    return str(value or '').lower()


def _load_cases(path: Path) -> list[dict[str, Any]]:
    payload = json.loads(path.read_text(encoding='utf-8'))
    assert_condition(isinstance(payload, list) and payload, 'dedicated_eval_dataset_invalid')
    return [item for item in payload if isinstance(item, dict)]


def _post_message_response(settings: Settings, *, base_url: str, case: dict[str, Any]) -> tuple[int, Any]:
    channel = str(case.get('channel') or 'api')
    payload: dict[str, Any] = {
        'message': str(case['message']),
        'conversation_id': f"dedicated-eval:{case['case_id']}:{RUN_ID}",
        'channel': channel,
        'user': case.get('user') or {'authenticated': False, 'role': 'anonymous'},
    }
    if channel == 'telegram':
        payload['telegram_chat_id'] = int(case.get('telegram_chat_id') or 1649845499)
    status, _, body = request(
        'POST',
        f'{base_url}/v1/messages/respond',
        headers={'X-Internal-Api-Token': settings.internal_api_token},
        json_body=payload,
        timeout=60.0,
    )
    return status, body


def _assert_case(case: dict[str, Any], payload: dict[str, Any]) -> None:
    case_id = str(case['case_id'])
    message_text = str(payload.get('message_text', ''))
    lowered = _normalize(message_text)
    assert_condition(message_text.strip(), f'{case_id}:empty_message')

    for snippet in case.get('message_contains', []):
        assert_condition(_normalize(str(snippet)) in lowered, f'{case_id}:message_missing:{snippet}')

    any_contains = tuple(str(item) for item in case.get('message_any_contains', []))
    if any_contains:
        assert_condition(
            any(_normalize(option) in lowered for option in any_contains),
            f'{case_id}:message_missing_any:{",".join(any_contains)}',
        )

    for snippet in case.get('message_excludes', []):
        assert_condition(_normalize(str(snippet)) not in lowered, f'{case_id}:message_leaked:{snippet}')


def _write_report(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def main() -> int:
    parser = argparse.ArgumentParser(description='Dedicated-first eval suite for a single stack runtime.')
    parser.add_argument('--base-url', default='http://127.0.0.1:8007')
    parser.add_argument('--dataset', type=Path, default=DEFAULT_DATASET_PATH)
    parser.add_argument('--output', type=Path, default=DEFAULT_OUTPUT_PATH)
    args = parser.parse_args()

    settings = Settings()
    print('Dedicated runtime eval suite starting...')

    for name, url in [
        ('api-core', f'{settings.api_core_url}/healthz'),
        ('runtime', f'{args.base_url}/healthz'),
    ]:
        wait_for_health(name, url)
        print(f'[ok] health {name}')

    cases = _load_cases(args.dataset)
    failures: list[str] = []
    results: list[dict[str, Any]] = []
    for case in cases:
        case_id = str(case['case_id'])
        try:
            status, body = _post_message_response(settings, base_url=args.base_url, case=case)
            assert_condition(status == 200 and isinstance(body, dict), f'{case_id}:request_failed')
            _assert_case(case, body)
            results.append(
                {
                    'case_id': case_id,
                    'passed': True,
                    'mode': body.get('mode'),
                    'reason': body.get('reason'),
                    'message_preview': str(body.get('message_text', ''))[:220],
                }
            )
            print(f"[ok] {case_id} mode={body.get('mode')}")
        except AssertionError as exc:
            failures.append(str(exc))
            results.append({'case_id': case_id, 'passed': False, 'error': str(exc)})
            print(f'[fail] {exc}', file=sys.stderr)

    report = {
        'run_id': RUN_ID,
        'base_url': args.base_url,
        'dataset': str(args.dataset),
        'passed': len(failures) == 0,
        'summary': {
            'passed': len(cases) - len(failures),
            'total': len(cases),
        },
        'results': results,
    }
    _write_report(args.output, report)

    if failures:
        print(f'Dedicated runtime eval suite failed with {len(failures)} case(s). Report: {args.output}', file=sys.stderr)
        return 1

    print(f'Dedicated runtime eval suite finished successfully. Report: {args.output}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
