#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATASET = REPO_ROOT / "tests/evals/datasets/retrieval_50q_probe_cases.generated.json"
DEFAULT_COMPARISON_REPORT = REPO_ROOT / "docs/architecture/retrieval-50q-cross-path-report.md"
DEFAULT_COMPARISON_JSON = REPO_ROOT / "docs/architecture/retrieval-50q-cross-path-report.json"
DEFAULT_TRACE_REPORT = REPO_ROOT / "docs/architecture/retrieval-50q-trace-calibration-report.md"
DEFAULT_TRACE_JSON = REPO_ROOT / "docs/architecture/retrieval-50q-trace-calibration-report.json"
DEFAULT_COMBINED_REPORT = REPO_ROOT / "docs/architecture/retrieval-50q-combined-evaluation-report.md"
DEFAULT_COMBINED_JSON = REPO_ROOT / "docs/architecture/retrieval-50q-combined-evaluation-report.json"


def _run(cmd: list[str]) -> None:
    subprocess.run(cmd, cwd=REPO_ROOT, check=True)


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise SystemExit(f"invalid_json_payload:{path}")
    return payload


def _render_markdown(payload: dict[str, Any]) -> str:
    comparison = payload["comparison"]
    trace = payload["trace"]
    case_count = 0
    try:
        case_count = max(int(bucket.get("count", 0)) for bucket in comparison["summary"]["by_stack"].values())
    except Exception:
        case_count = 0
    title_count = case_count or 50
    lines = [f"# Retrieval {title_count}Q Combined Evaluation Report", ""]
    lines.append(f"Generated at: {payload['generated_at']}")
    lines.append("")
    lines.append(f"Dataset: `{payload['dataset']}`")
    lines.append(f"Run prefix: `{comparison['run_prefix']}`")
    lines.append(f"Guardian chat id: `{comparison.get('guardian_chat_id') or 'none'}`")
    lines.append(f"Turn timeout: `{comparison.get('timeout_seconds') or 'unknown'}s`")
    lines.append("")
    lines.append("## Final Outcome")
    lines.append("")
    lines.append("| Stack | Keyword pass | Quality | Avg latency | Answerable | Avg coverage | Avg top_k |")
    lines.append("| --- | --- | --- | --- | --- | --- | --- |")
    for stack, compare_bucket in comparison["summary"]["by_stack"].items():
        trace_bucket = trace["summary"]["by_stack"].get(stack) or {}
        lines.append(
            f"| `{stack}` | `{compare_bucket['keyword_pass']}/{compare_bucket['count']}` | `{compare_bucket['quality_avg']}` | "
            f"`{compare_bucket['avg_latency_ms']} ms` | `{round(float(trace_bucket.get('answerable_rate', 0.0)) * 100.0, 1)}%` | "
            f"`{trace_bucket.get('avg_coverage_ratio', 0.0)}` | `{trace_bucket.get('avg_top_k', 0.0)}` |"
        )
    lines.append("")
    lines.append("## Automated Recommendations")
    lines.append("")
    for item in trace["summary"]["recommendations"]:
        lines.append(f"- {item}")
    if not trace["summary"]["recommendations"]:
        lines.append("- Nenhum ajuste forte recomendado nesta rodada.")
    lines.append("")
    lines.append("## Artifact Paths")
    lines.append("")
    for key, value in payload["artifacts"].items():
        lines.append(f"- `{key}`: `{value}`")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate a fresh retrieval dataset, run the cross-stack suite, analyze traces, and emit a combined report."
    )
    parser.add_argument("--count", type=int, default=50)
    parser.add_argument("--seed", type=int, default=260413)
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET)
    parser.add_argument("--comparison-report", type=Path, default=DEFAULT_COMPARISON_REPORT)
    parser.add_argument("--comparison-json", type=Path, default=DEFAULT_COMPARISON_JSON)
    parser.add_argument("--trace-report", type=Path, default=DEFAULT_TRACE_REPORT)
    parser.add_argument("--trace-json", type=Path, default=DEFAULT_TRACE_JSON)
    parser.add_argument("--combined-report", type=Path, default=DEFAULT_COMBINED_REPORT)
    parser.add_argument("--combined-json", type=Path, default=DEFAULT_COMBINED_JSON)
    parser.add_argument("--timeout-seconds", type=float, default=90.0)
    parser.add_argument("--guardian-chat-id", default=os.getenv("EVAL_GUARDIAN_CHAT_ID", "1649845499"))
    parser.add_argument("--database-url", default="postgresql://eduassist:eduassist@127.0.0.1:5432/eduassist")
    args = parser.parse_args()

    args.dataset.parent.mkdir(parents=True, exist_ok=True)
    for path in (
        args.comparison_report,
        args.comparison_json,
        args.trace_report,
        args.trace_json,
        args.combined_report,
        args.combined_json,
    ):
        path.parent.mkdir(parents=True, exist_ok=True)

    _run(
        [
            "uv",
            "run",
            "python",
            "tools/evals/generate_retrieval_20q_probe_cases.py",
            "--seed",
            str(args.seed),
            "--count",
            str(args.count),
            "--output",
            str(args.dataset),
        ]
    )
    compare_cmd = [
        "uv",
        "run",
        "python",
        "tools/evals/compare_four_chatbot_paths.py",
        "--prompt-file",
        str(args.dataset),
        "--report",
        str(args.comparison_report),
        "--json-report",
        str(args.comparison_json),
        "--guardian-chat-id",
        str(args.guardian_chat_id),
        "--timeout-seconds",
        str(args.timeout_seconds),
    ]
    _run(compare_cmd)

    comparison = _load_json(args.comparison_json)
    run_prefix = str(comparison.get("run_prefix") or "").strip()
    if not run_prefix:
        raise SystemExit("missing_run_prefix_in_comparison_report")

    _run(
        [
            "uv",
            "run",
            "python",
            "tools/evals/analyze_retrieval_run_traces.py",
            "--run-prefix",
            run_prefix,
            "--database-url",
            args.database_url,
            "--eval-json",
            str(args.comparison_json),
            "--report",
            str(args.trace_report),
            "--json-report",
            str(args.trace_json),
        ]
    )

    trace = _load_json(args.trace_json)
    payload = {
        "generated_at": datetime.now(UTC).isoformat(),
        "dataset": str(args.dataset),
        "comparison": comparison,
        "trace": trace,
        "artifacts": {
            "comparison_report": str(args.comparison_report),
            "comparison_json": str(args.comparison_json),
            "trace_report": str(args.trace_report),
            "trace_json": str(args.trace_json),
        },
    }
    args.combined_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    args.combined_report.write_text(_render_markdown(payload) + "\n", encoding="utf-8")
    print(args.combined_report)
    print(args.combined_json)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
