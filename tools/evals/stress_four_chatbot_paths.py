#!/usr/bin/env python3
from __future__ import annotations

import argparse
import asyncio
import json
import sys
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from statistics import median
from time import perf_counter
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.evals.compare_four_chatbot_paths import STACKS, _run_turn
from tools.evals.eval_quality_utils import (
    _contains_expected_keywords,
    _contains_forbidden_keywords,
    _detect_error_types,
    _extract_answer_text,
    _quality_score,
)
DEFAULT_DATASET = REPO_ROOT / "tests/evals/datasets/retrieval_50q_stress_iter1.generated.20260409.json"
DEFAULT_REPORT = REPO_ROOT / "docs/architecture/four-path-chatbot-stress-report.md"
DEFAULT_JSON_REPORT = REPO_ROOT / "docs/architecture/four-path-chatbot-stress-report.json"


def _percentile(values: list[float], q: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    index = (len(ordered) - 1) * q
    lower = int(index)
    upper = min(lower + 1, len(ordered) - 1)
    if lower == upper:
        return float(ordered[lower])
    weight = index - lower
    return float(ordered[lower] * (1 - weight) + ordered[upper] * weight)


async def _run_case(
    *,
    stack: str,
    entry: dict[str, Any],
    guardian_chat_id: str | None,
    timeout_seconds: float,
    concurrency: int,
    round_index: int,
    sequence_index: int,
    run_prefix_base: str,
) -> dict[str, Any]:
    unique_entry = dict(entry)
    unique_entry["run_prefix"] = f"{run_prefix_base}:c{concurrency}:r{round_index}:n{sequence_index}"
    raw = await _run_turn(
        stack=stack,
        entry=unique_entry,
        guardian_chat_id=guardian_chat_id,
        timeout_seconds=timeout_seconds,
    )
    answer_text = _extract_answer_text(raw["body"])
    expected_keywords = list(entry.get("expected_keywords") or [])
    forbidden_keywords = list(entry.get("forbidden_keywords") or [])
    expected_sections = list(entry.get("expected_sections") or [])
    rubric_tags = list(entry.get("rubric_tags") or [])
    error_types = _detect_error_types(
        answer_text=answer_text,
        expected_keywords=expected_keywords,
        forbidden_keywords=forbidden_keywords,
        expected_sections=expected_sections,
        rubric_tags=rubric_tags,
        prompt=str(entry["prompt"]),
        previous_answer="",
        status=int(raw["status"]),
        turn_index=1,
        note=str(entry.get("note") or ""),
    )
    quality_score = _quality_score(status=int(raw["status"]), error_types=error_types)
    keyword_pass = _contains_expected_keywords(answer_text, expected_keywords) and not _contains_forbidden_keywords(
        answer_text,
        forbidden_keywords,
    )
    return {
        "id": str(entry.get("id") or ""),
        "slice": str(entry.get("slice") or ""),
        "category": str(entry.get("category") or ""),
        "status": int(raw["status"]),
        "latency_ms": float(raw["latency_ms"]),
        "reason": str(raw.get("reason") or ""),
        "mode": str(raw.get("mode") or ""),
        "quality_score": int(quality_score),
        "keyword_pass": bool(keyword_pass),
        "error_types": list(error_types),
    }


async def _run_stack_level(
    *,
    stack: str,
    entries: list[dict[str, Any]],
    concurrency: int,
    rounds: int,
    guardian_chat_id: str | None,
    timeout_seconds: float,
    run_prefix_base: str,
) -> dict[str, Any]:
    semaphore = asyncio.Semaphore(max(1, concurrency))
    started = perf_counter()
    tasks: list[asyncio.Task[dict[str, Any]]] = []
    sequence_index = 0

    async def _bounded(entry: dict[str, Any], *, round_index: int, item_index: int) -> dict[str, Any]:
        async with semaphore:
            return await _run_case(
                stack=stack,
                entry=entry,
                guardian_chat_id=guardian_chat_id,
                timeout_seconds=timeout_seconds,
                concurrency=concurrency,
                round_index=round_index,
                sequence_index=item_index,
                run_prefix_base=run_prefix_base,
            )

    for round_index in range(1, rounds + 1):
        for entry in entries:
            sequence_index += 1
            tasks.append(asyncio.create_task(_bounded(entry, round_index=round_index, item_index=sequence_index)))

    results = await asyncio.gather(*tasks)
    wall_time_ms = (perf_counter() - started) * 1000
    latencies = [float(item["latency_ms"]) for item in results]
    quality_scores = [int(item["quality_score"]) for item in results]
    keyword_passes = sum(1 for item in results if item["keyword_pass"])
    ok_count = sum(1 for item in results if int(item["status"]) == 200)
    error_counter: Counter[str] = Counter()
    reason_counter: Counter[str] = Counter()
    for item in results:
        error_counter.update(item.get("error_types") or [])
        reason = str(item.get("reason") or "").strip()
        if reason:
            reason_counter[reason] += 1

    wall_time_seconds = max(wall_time_ms / 1000.0, 0.001)
    throughput_rps = len(results) / wall_time_seconds
    return {
        "stack": stack,
        "concurrency": concurrency,
        "rounds": rounds,
        "count": len(results),
        "ok": ok_count,
        "keyword_pass": keyword_passes,
        "quality_avg": round(sum(quality_scores) / max(1, len(quality_scores)), 1),
        "avg_latency_ms": round(sum(latencies) / max(1, len(latencies)), 1),
        "median_latency_ms": round(float(median(latencies)) if latencies else 0.0, 1),
        "p95_latency_ms": round(_percentile(latencies, 0.95), 1),
        "max_latency_ms": round(max(latencies) if latencies else 0.0, 1),
        "throughput_rps": round(throughput_rps, 2),
        "error_types": dict(error_counter.most_common()),
        "top_reasons": [{"reason": key, "count": value} for key, value in reason_counter.most_common(5)],
        "results": results,
    }


def _recommendations(payload: dict[str, Any]) -> list[str]:
    items: list[str] = []
    for stack, bucket in payload["summary"]["by_stack"].items():
        worst = max(bucket["by_concurrency"], key=lambda item: float(item["p95_latency_ms"]))
        if float(worst["p95_latency_ms"]) > 15000:
            items.append(
                f"`{stack}` reached p95 `{worst['p95_latency_ms']} ms` at concurrency `{worst['concurrency']}`; inspect slowest routes and queueing."
            )
        if int(worst["ok"]) < int(worst["count"]):
            items.append(
                f"`{stack}` dropped successful responses under concurrency `{worst['concurrency']}` (`{worst['ok']}/{worst['count']}`); inspect timeouts and retries."
            )
        if int(worst["keyword_pass"]) < int(worst["count"]):
            items.append(
                f"`{stack}` lost grounding quality under concurrency `{worst['concurrency']}` (`keyword_pass {worst['keyword_pass']}/{worst['count']}`)."
            )
    return items


def _render_markdown(payload: dict[str, Any]) -> str:
    lines = ["# Four-Path Chatbot Stress Report", ""]
    lines.append(f"Date: {payload['generated_at']}")
    lines.append("")
    lines.append(f"Dataset: `{payload['dataset']}`")
    lines.append(f"Guardian chat id: `{payload.get('guardian_chat_id') or 'none'}`")
    lines.append(f"Timeout: `{payload['timeout_seconds']}s`")
    lines.append(f"Rounds: `{payload['rounds']}`")
    lines.append(f"Concurrency levels: `{', '.join(str(item) for item in payload['concurrency_levels'])}`")
    lines.append("")
    lines.append("## Stack Summary")
    lines.append("")
    lines.append("| Stack | Concurrency | OK | Keyword pass | Quality | Avg latency | P95 | Max | Throughput |")
    lines.append("| --- | --- | --- | --- | --- | --- | --- | --- | --- |")
    for stack in STACKS:
        for bucket in payload["summary"]["by_stack"][stack]["by_concurrency"]:
            lines.append(
                f"| `{stack}` | `{bucket['concurrency']}` | `{bucket['ok']}/{bucket['count']}` | "
                f"`{bucket['keyword_pass']}/{bucket['count']}` | `{bucket['quality_avg']}` | `{bucket['avg_latency_ms']} ms` | "
                f"`{bucket['p95_latency_ms']} ms` | `{bucket['max_latency_ms']} ms` | `{bucket['throughput_rps']} rps` |"
            )
    lines.append("")
    lines.append("## Recommendations")
    lines.append("")
    for item in payload["recommendations"]:
        lines.append(f"- {item}")
    if not payload["recommendations"]:
        lines.append("- Nenhum gargalo crítico apareceu nesta rodada de stress.")
    lines.append("")
    lines.append("## Dominant Error Types")
    lines.append("")
    for stack in STACKS:
        for bucket in payload["summary"]["by_stack"][stack]["by_concurrency"]:
            errors = ", ".join(f"`{k}` x{v}" for k, v in bucket["error_types"].items()) or "`none`"
            lines.append(f"- `{stack}` @ `{bucket['concurrency']}`: {errors}")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run concurrency stress across the four chatbot paths with the standard rubric.")
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--json-report", type=Path, default=DEFAULT_JSON_REPORT)
    parser.add_argument("--guardian-chat-id", default="1649845499")
    parser.add_argument("--timeout-seconds", type=float, default=45.0)
    parser.add_argument("--concurrency-levels", default="1,2,4")
    parser.add_argument("--rounds", type=int, default=1)
    args = parser.parse_args()

    entries = json.loads(args.dataset.read_text(encoding="utf-8"))
    if not isinstance(entries, list):
        raise SystemExit(f"invalid_dataset:{args.dataset}")

    concurrency_levels = [max(1, int(item.strip())) for item in str(args.concurrency_levels).split(",") if item.strip()]
    generated_at = datetime.now(UTC).isoformat()
    run_prefix_base = f"debug:four-path-stress:{datetime.now(UTC).strftime('%Y%m%dT%H%M%SZ')}"

    by_stack: dict[str, dict[str, Any]] = {}
    raw_runs: list[dict[str, Any]] = []
    for stack in STACKS:
        buckets: list[dict[str, Any]] = []
        for concurrency in concurrency_levels:
            result = asyncio.run(
                _run_stack_level(
                    stack=stack,
                    entries=entries,
                    concurrency=concurrency,
                    rounds=max(1, int(args.rounds)),
                    guardian_chat_id=str(args.guardian_chat_id),
                    timeout_seconds=float(args.timeout_seconds),
                    run_prefix_base=run_prefix_base,
                )
            )
            raw_runs.append(result)
            summary_bucket = {key: value for key, value in result.items() if key != "results"}
            buckets.append(summary_bucket)
        by_stack[stack] = {"by_concurrency": buckets}

    payload = {
        "generated_at": generated_at,
        "dataset": str(args.dataset),
        "guardian_chat_id": str(args.guardian_chat_id),
        "timeout_seconds": float(args.timeout_seconds),
        "rounds": max(1, int(args.rounds)),
        "concurrency_levels": concurrency_levels,
        "summary": {"by_stack": by_stack},
        "recommendations": [],
        "raw_runs": raw_runs,
    }
    payload["recommendations"] = _recommendations(payload)

    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.json_report.parent.mkdir(parents=True, exist_ok=True)
    args.json_report.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    args.report.write_text(_render_markdown(payload) + "\n", encoding="utf-8")
    print(args.report)
    print(args.json_report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
