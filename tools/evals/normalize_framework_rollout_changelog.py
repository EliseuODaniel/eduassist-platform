#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.evals.promote_framework_slice import (  # noqa: E402
    DEFAULT_CHANGELOG_JSON,
    DEFAULT_CHANGELOG_MD,
    _load_json_array,
    _normalize_changelog_rows,
    _write_changelog,
)

DEFAULT_REPORT_MD = REPO_ROOT / 'docs/architecture/framework-rollout-changelog-normalization-report.md'
DEFAULT_REPORT_JSON = REPO_ROOT / 'docs/architecture/framework-rollout-changelog-normalization-report.json'
DEFAULT_ARTIFACT_JSON = REPO_ROOT / 'artifacts/framework-rollout-changelog-normalization-report.json'


def _write_report(*, report_md: Path, report_json: Path, artifact_json: Path, payload: dict) -> None:
    lines = [
        '# Framework Rollout Changelog Normalization Report',
        '',
        f"Date: {payload['generated_at']}",
        '',
        '## Summary',
        '',
        f"- total entries: `{payload['total_entries']}`",
        f"- normalized entries: `{payload['normalized_entries']}`",
        f"- legacy gaps remaining: `{payload['legacy_gaps_remaining']}`",
        f"- changelog json: `{payload['changelog_json']}`",
        f"- changelog md: `{payload['changelog_md']}`",
    ]
    if payload.get('normalized_examples'):
        lines.extend(['', '## Normalized Examples', ''])
        for item in payload['normalized_examples']:
            lines.append(
                f"- `{item.get('timestamp', '')}` `{item.get('slice', '')}` "
                f"fields={','.join(item.get('normalized_legacy_fields', []))}"
            )
    report_md.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    json_text = json.dumps(payload, ensure_ascii=False, indent=2) + '\n'
    report_json.write_text(json_text, encoding='utf-8')
    artifact_json.parent.mkdir(parents=True, exist_ok=True)
    artifact_json.write_text(json_text, encoding='utf-8')


def main() -> int:
    parser = argparse.ArgumentParser(description='Normalize legacy rollout changelog entries to current audit fields.')
    parser.add_argument('--changelog-json', type=Path, default=DEFAULT_CHANGELOG_JSON)
    parser.add_argument('--changelog-md', type=Path, default=DEFAULT_CHANGELOG_MD)
    parser.add_argument('--report', type=Path, default=DEFAULT_REPORT_MD)
    parser.add_argument('--json', type=Path, default=DEFAULT_REPORT_JSON)
    parser.add_argument('--artifact-json', type=Path, default=DEFAULT_ARTIFACT_JSON)
    args = parser.parse_args()

    rows = _load_json_array(args.changelog_json)
    normalized_rows, changed_count = _normalize_changelog_rows(rows)
    _write_changelog(rows=normalized_rows, md_path=args.changelog_md, json_path=args.changelog_json)

    legacy_gaps_remaining = 0
    for item in normalized_rows:
        if not str(item.get('intent', '') or '').strip():
            legacy_gaps_remaining += 1
        if not str(item.get('operator', '') or '').strip():
            legacy_gaps_remaining += 1
        if not str(item.get('reason', '') or '').strip():
            legacy_gaps_remaining += 1

    payload = {
        'generated_at': datetime.now(UTC).isoformat(),
        'total_entries': len(normalized_rows),
        'normalized_entries': changed_count,
        'legacy_gaps_remaining': legacy_gaps_remaining,
        'changelog_json': str(args.changelog_json),
        'changelog_md': str(args.changelog_md),
        'normalized_examples': [
            {
                'timestamp': item.get('timestamp'),
                'slice': item.get('slice'),
                'normalized_legacy_fields': item.get('normalized_legacy_fields', []),
            }
            for item in normalized_rows
            if item.get('normalized_legacy_fields')
        ][:10],
    }
    _write_report(report_md=args.report, report_json=args.json, artifact_json=args.artifact_json, payload=payload)
    print(args.report)
    print(args.json)
    print(args.artifact_json)
    return 0 if legacy_gaps_remaining == 0 else 1


if __name__ == '__main__':
    raise SystemExit(main())
