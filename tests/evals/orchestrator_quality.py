from __future__ import annotations

import json
import os
import sys
import unicodedata
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'e2e'))

from _common import Settings, assert_condition, request, wait_for_health


ROOT_DIR = Path(__file__).resolve().parents[2]
DEFAULT_DATASET_PATH = ROOT_DIR / 'tests' / 'evals' / 'datasets' / 'orchestrator_cases.json'


def _normalize_text(value: str) -> str:
    normalized = unicodedata.normalize('NFKD', value)
    without_accents = ''.join(char for char in normalized if not unicodedata.combining(char))
    return without_accents.lower()


def _load_cases() -> list[dict[str, Any]]:
    dataset_path = Path(os.getenv('ORCHESTRATOR_EVAL_DATASET', str(DEFAULT_DATASET_PATH)))
    payload = json.loads(dataset_path.read_text(encoding='utf-8'))
    assert_condition(isinstance(payload, list) and payload, 'eval_dataset_invalid')
    return payload


def _post_message_response(settings: Settings, payload: dict[str, Any]) -> tuple[int, Any]:
    status, _, body = request(
        'POST',
        f'{settings.ai_orchestrator_url}/v1/messages/respond',
        headers={'X-Internal-Api-Token': settings.internal_api_token},
        json_body=payload,
        timeout=25.0,
    )
    return status, body


def _post_retrieval_search(settings: Settings, payload: dict[str, Any]) -> tuple[int, Any]:
    status, _, body = request(
        'POST',
        f'{settings.ai_orchestrator_url}/v1/retrieval/search',
        json_body=payload,
        timeout=25.0,
    )
    return status, body


def _assert_common_text_rules(message_text: str, expected: dict[str, Any], case_id: str) -> None:
    normalized_message = _normalize_text(message_text)
    for snippet in expected.get('message_contains', []):
        assert_condition(
            _normalize_text(str(snippet)) in normalized_message,
            f'{case_id}:message_missing:{snippet}',
        )
    for snippet in expected.get('message_excludes', []):
        assert_condition(
            _normalize_text(str(snippet)) not in normalized_message,
            f'{case_id}:message_leaked:{snippet}',
        )


def _assert_message_response(case: dict[str, Any], payload: dict[str, Any]) -> None:
    case_id = str(case['case_id'])
    expected = case['expected']
    classification = payload.get('classification', {})
    citations = payload.get('citations', [])
    calendar_events = payload.get('calendar_events', [])
    selected_tools = payload.get('selected_tools', [])
    graph_path = payload.get('graph_path', [])
    risk_flags = payload.get('risk_flags', [])

    assert_condition(payload.get('mode') == expected.get('mode'), f'{case_id}:mode_mismatch')
    assert_condition(
        classification.get('domain') == expected.get('domain'),
        f'{case_id}:domain_mismatch',
    )
    assert_condition(
        classification.get('access_tier') == expected.get('access_tier'),
        f'{case_id}:access_tier_mismatch',
    )
    assert_condition(
        payload.get('retrieval_backend') == expected.get('retrieval_backend'),
        f'{case_id}:retrieval_backend_mismatch',
    )
    assert_condition(
        payload.get('needs_authentication') == expected.get('needs_authentication'),
        f'{case_id}:needs_authentication_mismatch',
    )

    for tool_name in expected.get('selected_tools_includes', []):
        assert_condition(tool_name in selected_tools, f'{case_id}:missing_tool:{tool_name}')

    for node_name in expected.get('graph_path_includes', []):
        assert_condition(node_name in graph_path, f'{case_id}:missing_graph_node:{node_name}')

    for risk_flag in expected.get('risk_flags_include', []):
        assert_condition(risk_flag in risk_flags, f'{case_id}:missing_risk_flag:{risk_flag}')

    min_citations = int(expected.get('min_citations', 0))
    assert_condition(len(citations) >= min_citations, f'{case_id}:citation_count_too_low')
    for citation in citations[:min_citations]:
        assert_condition(isinstance(citation, dict), f'{case_id}:citation_invalid')
        for field_name in ('document_title', 'version_label', 'storage_path', 'chunk_id', 'excerpt'):
            assert_condition(citation.get(field_name), f'{case_id}:citation_missing_{field_name}')

    min_calendar_events = int(expected.get('min_calendar_events', 0))
    assert_condition(
        len(calendar_events) >= min_calendar_events,
        f'{case_id}:calendar_event_count_too_low',
    )

    reason_contains = expected.get('reason_contains')
    if reason_contains:
        assert_condition(
            _normalize_text(str(reason_contains)) in _normalize_text(str(payload.get('reason', ''))),
            f'{case_id}:reason_unexpected',
        )

    _assert_common_text_rules(str(payload.get('message_text', '')), expected, case_id)


def _assert_retrieval_search(case: dict[str, Any], payload: dict[str, Any]) -> None:
    case_id = str(case['case_id'])
    expected = case['expected']
    hits = payload.get('hits', [])

    assert_condition(
        payload.get('retrieval_backend') == expected.get('retrieval_backend'),
        f'{case_id}:retrieval_backend_mismatch',
    )
    assert_condition(
        int(payload.get('total_hits', 0)) >= int(expected.get('min_total_hits', 0)),
        f'{case_id}:total_hits_too_low',
    )
    assert_condition(isinstance(hits, list) and hits, f'{case_id}:hits_missing')

    titles = [str(hit.get('document_title', '')) for hit in hits if isinstance(hit, dict)]
    for title in expected.get('required_document_titles', []):
        assert_condition(title in titles, f'{case_id}:missing_document_title:{title}')

    first_hit = hits[0]
    assert_condition(isinstance(first_hit, dict), f'{case_id}:first_hit_invalid')
    expected_visibility = expected.get('first_hit_visibility')
    if expected_visibility is not None:
        assert_condition(
            first_hit.get('visibility') == expected_visibility,
            f'{case_id}:first_hit_visibility_mismatch',
        )
    citation = first_hit.get('citation', {})
    assert_condition(isinstance(citation, dict), f'{case_id}:first_hit_citation_missing')
    assert_condition(citation.get('storage_path'), f'{case_id}:first_hit_storage_path_missing')


def main() -> int:
    settings = Settings()
    print('Orchestrator eval suite starting...')

    for name, url in [
        ('api-core', f'{settings.api_core_url}/healthz'),
        ('ai-orchestrator', f'{settings.ai_orchestrator_url}/healthz'),
    ]:
        wait_for_health(name, url)
        print(f'[ok] health {name}')

    cases = _load_cases()
    failures: list[str] = []

    for case in cases:
        case_id = str(case['case_id'])
        case_type = str(case['type'])
        try:
            if case_type == 'message_response':
                status, body = _post_message_response(settings, case['request'])
                assert_condition(status == 200 and isinstance(body, dict), f'{case_id}:request_failed')
                _assert_message_response(case, body)
                print(
                    f"[ok] {case_id} mode={body.get('mode')} "
                    f"domain={body.get('classification', {}).get('domain')}"
                )
                continue

            if case_type == 'retrieval_search':
                status, body = _post_retrieval_search(settings, case['request'])
                assert_condition(status == 200 and isinstance(body, dict), f'{case_id}:request_failed')
                _assert_retrieval_search(case, body)
                print(
                    f"[ok] {case_id} backend={body.get('retrieval_backend')} "
                    f"hits={body.get('total_hits')}"
                )
                continue

            raise AssertionError(f'{case_id}:unsupported_case_type:{case_type}')
        except AssertionError as exc:
            print(f'[fail] {exc}', file=sys.stderr)
            failures.append(str(exc))

    if failures:
        print(
            f'Orchestrator eval suite failed with {len(failures)} case(s).',
            file=sys.stderr,
        )
        return 1

    print(f'Orchestrator eval suite finished successfully. {len(cases)} cases passed.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
