#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATABASE_URL = "postgresql://eduassist:eduassist@127.0.0.1:5432/eduassist"
DEFAULT_REPORT = REPO_ROOT / "docs/architecture/retrieval-trace-calibration-report.md"
DEFAULT_JSON_REPORT = REPO_ROOT / "docs/architecture/retrieval-trace-calibration-report.json"
STACKS = ("langgraph", "python_functions", "llamaindex", "specialist_supervisor")


@dataclass(slots=True)
class RetrievalTraceRow:
    created_at: datetime
    conversation_id: str
    stack: str
    thread_id: str
    turn_index: int
    request_payload: dict[str, Any]
    response_payload: dict[str, Any]


def _safe_div(numerator: float, denominator: float) -> float:
    if denominator == 0:
        return 0.0
    return numerator / denominator


def _percent(value: float) -> float:
    return round(value * 100.0, 1)


def _stack_key(stack: str) -> str:
    return stack if stack != "specialist_supervisor" else "specialist_supervisor"


def _extract_trace_key(*, external_thread_id: str, run_prefix: str) -> tuple[str, str] | None:
    prefix = f"{run_prefix}:"
    if not external_thread_id.startswith(prefix):
        return None
    suffix_stack = next(
        (stack for stack in STACKS if external_thread_id.endswith(f":{stack}")),
        None,
    )
    if suffix_stack is None:
        return None
    inner = external_thread_id[len(prefix) : -len(f":{suffix_stack}")]
    return suffix_stack, inner


def _fetch_rows(
    *,
    run_prefix: str,
    postgres_container: str,
    postgres_user: str,
    postgres_db: str,
) -> list[RetrievalTraceRow]:
    run_prefix_like = f"{run_prefix}:%".replace("'", "''")
    query = f"""
    select json_build_object(
      'created_at', to_char(tc.created_at at time zone 'UTC', 'YYYY-MM-DD"T"HH24:MI:SS.MS"Z"'),
      'external_thread_id', c.external_thread_id,
      'request_payload', tc.request_payload,
      'response_payload', tc.response_payload
    )::text
    from conversation.tool_calls tc
    join conversation.conversations c on c.id = tc.conversation_id
    where tc.tool_name = 'orchestration.trace'
      and c.external_thread_id like '{run_prefix_like}'
    order by c.external_thread_id asc, tc.created_at asc, tc.id asc
    """
    command = [
        "docker",
        "exec",
        postgres_container,
        "psql",
        "-U",
        postgres_user,
        "-d",
        postgres_db,
        "-At",
        "-c",
        query,
    ]
    completed = subprocess.run(
        command,
        check=True,
        capture_output=True,
        text=True,
    )
    raw_rows = [json.loads(line) for line in completed.stdout.splitlines() if line.strip()]
    turn_counters: dict[str, int] = defaultdict(int)
    result: list[RetrievalTraceRow] = []
    for row in raw_rows:
        conversation_id = str(row["external_thread_id"])
        trace_key = _extract_trace_key(external_thread_id=conversation_id, run_prefix=run_prefix)
        if trace_key is None:
            continue
        stack, thread_id = trace_key
        turn_counters[conversation_id] += 1
        request_payload = row["request_payload"] if isinstance(row["request_payload"], dict) else {}
        response_payload = row["response_payload"] if isinstance(row["response_payload"], dict) else {}
        result.append(
            RetrievalTraceRow(
                created_at=datetime.fromisoformat(str(row["created_at"]).replace("Z", "+00:00")),
                conversation_id=conversation_id,
                stack=stack,
                thread_id=thread_id,
                turn_index=turn_counters[conversation_id],
                request_payload=request_payload,
                response_payload=response_payload,
            )
        )
    return result


def _load_eval_results(path: Path | None) -> dict[tuple[str, str, int], dict[str, Any]]:
    if path is None or not path.exists():
        return {}
    payload = json.loads(path.read_text(encoding="utf-8"))
    rows = payload.get("results") if isinstance(payload, dict) else None
    if not isinstance(rows, list):
        return {}
    mapping: dict[tuple[str, str, int], dict[str, Any]] = {}
    for row in rows:
        if not isinstance(row, dict):
            continue
        if isinstance(row.get("stack"), str):
            stack = str(row.get("stack") or "").strip()
            thread_id = str(row.get("thread_id") or "").strip()
            turn_index = int(row.get("turn_index") or 1)
            if not stack or not thread_id:
                continue
            mapping[(stack, thread_id, turn_index)] = row
            continue

        thread_id = str(row.get("thread_id") or "").strip()
        turn_index = int(row.get("turn_index") or 1)
        if not thread_id:
            continue
        for stack in STACKS:
            stack_payload = row.get(stack)
            if not isinstance(stack_payload, dict):
                continue
            mapping[(stack, thread_id, turn_index)] = {
                "stack": stack,
                "thread_id": thread_id,
                "turn_index": turn_index,
                "quality_score": stack_payload.get("quality_score"),
                "keyword_pass": stack_payload.get("keyword_pass"),
                "latency_ms": stack_payload.get("latency_ms"),
                "retrieval_type": row.get("category") or row.get("slice") or "",
                "prompt": row.get("prompt") or "",
                "reason": stack_payload.get("reason") or "",
                "error_types": list(stack_payload.get("error_types") or []),
            }
    return mapping


def _extract_retrieval_sections(
    *,
    row: RetrievalTraceRow,
) -> tuple[dict[str, Any], dict[str, Any]]:
    stack_key = _stack_key(row.stack)
    request_section = row.request_payload.get(stack_key)
    response_section = row.response_payload.get(stack_key)
    return (
        request_section if isinstance(request_section, dict) else {},
        response_section if isinstance(response_section, dict) else {},
    )


def _trace_item(
    *,
    row: RetrievalTraceRow,
    eval_row: dict[str, Any] | None,
) -> dict[str, Any]:
    request_section, response_section = _extract_retrieval_sections(row=row)
    retrieval_policy = request_section.get("retrieval_policy")
    retrieval_result = response_section.get("retrieval_result")
    if not isinstance(retrieval_policy, dict):
        retrieval_policy = {}
    if not isinstance(retrieval_result, dict):
        retrieval_result = {}

    public_plan = row.request_payload.get("public_plan")
    top_level_reason = str(row.request_payload.get("reason") or "").strip()
    capability_id = str(retrieval_policy.get("capability_id") or "").strip()
    if not capability_id and isinstance(public_plan, dict):
        capability_id = str(public_plan.get("conversation_act") or "").strip() or "unknown"
    if not capability_id and ":public_bundle." in top_level_reason:
        capability_id = top_level_reason.split(":", 1)[-1]
    elif not capability_id and top_level_reason:
        capability_id = top_level_reason

    has_retrieval_metadata = bool(retrieval_policy) or bool(retrieval_result)

    return {
        "created_at": row.created_at.isoformat(),
        "stack": row.stack,
        "thread_id": row.thread_id,
        "turn_index": row.turn_index,
        "conversation_id": row.conversation_id,
        "capability_id": capability_id or "unknown",
        "policy_reason": str(retrieval_policy.get("reason") or "").strip() or "unknown",
        "profile": str(retrieval_policy.get("profile") or "").strip() or "unknown",
        "top_k": int(retrieval_policy.get("top_k") or 0),
        "category": str(retrieval_policy.get("category") or "").strip() or "all",
        "has_retrieval_metadata": has_retrieval_metadata,
        "total_hits": int(retrieval_result.get("total_hits") or 0),
        "selected_hit_count": int(retrieval_result.get("selected_hit_count") or 0),
        "document_group_count": int(retrieval_result.get("document_group_count") or 0),
        "citations_count": int(retrieval_result.get("citations_count") or 0),
        "answerable": bool(retrieval_result.get("answerable")) if "answerable" in retrieval_result else None,
        "coverage_ratio": float(retrieval_result.get("coverage_ratio") or 0.0),
        "answerability_coverage_ratio": float(
            retrieval_result.get("answerability_coverage_ratio") or 0.0
        ),
        "reranker_applied": bool(retrieval_result.get("reranker_applied", False)),
        "corrective_retry_applied": bool(
            retrieval_result.get("corrective_retry_applied", False)
        ),
        "citation_first_recommended": bool(
            retrieval_result.get("citation_first_recommended", False)
        ),
        "query_plan_profile": str(retrieval_result.get("query_plan_profile") or "").strip()
        or "unknown",
        "query_plan_intent": str(retrieval_result.get("query_plan_intent") or "").strip()
        or "unknown",
        "canonical_lane": str(retrieval_result.get("canonical_lane") or "").strip() or "",
        "quality_score": int(eval_row.get("quality_score") or 0) if isinstance(eval_row, dict) else None,
        "keyword_pass": bool(eval_row.get("keyword_pass")) if isinstance(eval_row, dict) else None,
        "latency_ms": float(eval_row.get("latency_ms") or 0.0) if isinstance(eval_row, dict) else None,
        "retrieval_type": str(eval_row.get("retrieval_type") or "").strip()
        if isinstance(eval_row, dict)
        else "",
        "prompt": str(eval_row.get("prompt") or "").strip() if isinstance(eval_row, dict) else "",
        "reason": str(eval_row.get("reason") or "").strip() if isinstance(eval_row, dict) else "",
        "error_types": list(eval_row.get("error_types") or []) if isinstance(eval_row, dict) else [],
    }


def _aggregate_trace_items(items: list[dict[str, Any]]) -> dict[str, Any]:
    def _metrics(subset: list[dict[str, Any]]) -> dict[str, Any]:
        retrieval_subset = [
            item
            for item in subset
            if bool(
                item.get("has_retrieval_metadata")
                or item.get("top_k")
                or item.get("total_hits")
                or item.get("answerable") is not None
            )
        ]
        answerable_subset = [item for item in subset if item["answerable"] is not None]
        quality_subset = [item for item in subset if item["quality_score"] is not None]
        return {
            "count": len(subset),
            "retrieval_trace_count": len(retrieval_subset),
            "retrieval_trace_rate": round(
                _safe_div(len(retrieval_subset), max(1, len(subset))),
                3,
            ),
            "avg_top_k": round(
                sum(float(item["top_k"]) for item in retrieval_subset)
                / max(1, len(retrieval_subset)),
                2,
            ),
            "avg_total_hits": round(
                sum(float(item["total_hits"]) for item in retrieval_subset)
                / max(1, len(retrieval_subset)),
                2,
            ),
            "avg_selected_hit_count": round(
                sum(float(item["selected_hit_count"]) for item in retrieval_subset)
                / max(1, len(retrieval_subset)),
                2,
            ),
            "avg_coverage_ratio": round(
                sum(float(item["coverage_ratio"]) for item in retrieval_subset)
                / max(1, len(retrieval_subset)),
                3,
            ),
            "avg_answerability_coverage_ratio": round(
                sum(float(item["answerability_coverage_ratio"]) for item in retrieval_subset)
                / max(1, len(retrieval_subset)),
                3,
            ),
            "answerable_rate": round(
                _safe_div(
                    sum(1 for item in answerable_subset if item["answerable"]),
                    max(1, len(answerable_subset)),
                ),
                3,
            ),
            "keyword_pass_rate": round(
                _safe_div(
                    sum(1 for item in quality_subset if item["keyword_pass"]),
                    max(1, len(quality_subset)),
                ),
                3,
            ),
            "quality_avg": round(
                sum(float(item["quality_score"] or 0) for item in quality_subset)
                / max(1, len(quality_subset)),
                1,
            ),
            "latency_avg_ms": round(
                sum(float(item["latency_ms"] or 0.0) for item in quality_subset)
                / max(1, len(quality_subset)),
                1,
            ),
            "reranker_rate": round(
                _safe_div(
                    sum(1 for item in retrieval_subset if item["reranker_applied"]),
                    max(1, len(retrieval_subset)),
                ),
                3,
            ),
            "corrective_retry_rate": round(
                _safe_div(
                    sum(1 for item in retrieval_subset if item["corrective_retry_applied"]),
                    max(1, len(retrieval_subset)),
                ),
                3,
            ),
            "citation_first_rate": round(
                _safe_div(
                    sum(1 for item in retrieval_subset if item["citation_first_recommended"]),
                    max(1, len(retrieval_subset)),
                ),
                3,
            ),
            "profile_counts": dict(Counter(item["profile"] for item in retrieval_subset)),
            "policy_reason_counts": dict(Counter(item["policy_reason"] for item in retrieval_subset)),
        }

    by_stack: dict[str, Any] = {}
    by_capability: dict[str, Any] = {}
    by_stack_capability: dict[str, Any] = {stack: {} for stack in STACKS}
    recommendations: list[str] = []

    for stack in STACKS:
        stack_items = [item for item in items if item["stack"] == stack]
        by_stack[stack] = _metrics(stack_items)
        capability_ids = sorted({item["capability_id"] for item in stack_items})
        for capability_id in capability_ids:
            subset = [item for item in stack_items if item["capability_id"] == capability_id]
            by_stack_capability[stack][capability_id] = _metrics(subset)

    for capability_id in sorted({item["capability_id"] for item in items}):
        subset = [item for item in items if item["capability_id"] == capability_id]
        bucket = _metrics(subset)
        bucket["stacks"] = sorted({item["stack"] for item in subset})
        by_capability[capability_id] = bucket

        if bucket["retrieval_trace_count"] >= 4 and bucket["answerable_rate"] < 0.75:
            if bucket["avg_total_hits"] >= bucket["avg_top_k"] - 0.25:
                recommendations.append(
                    f"`{capability_id}` está com `answerable_rate={_percent(bucket['answerable_rate'])}%` e saturando `top_k`; vale testar `top_k` maior ou profile mais profundo."
                )
            else:
                recommendations.append(
                    f"`{capability_id}` está com `answerable_rate={_percent(bucket['answerable_rate'])}%` sem saturar `top_k`; vale revisar query variants, metadata e chunking."
                )
        elif bucket["retrieval_trace_count"] >= 4 and bucket["quality_avg"] < 85 and bucket["answerable_rate"] >= 0.75:
            recommendations.append(
                f"`{capability_id}` tem suporte suficiente, mas `quality_avg={bucket['quality_avg']}`; vale revisar composição grounded e resposta final, não só retrieval."
            )

    return {
        "by_stack": by_stack,
        "by_capability": by_capability,
        "by_stack_capability": by_stack_capability,
        "recommendations": recommendations,
    }


def _render_markdown(payload: dict[str, Any]) -> str:
    lines = ["# Retrieval Trace Calibration Report", ""]
    lines.append(f"Generated at: {payload['generated_at']}")
    lines.append("")
    lines.append(f"Run prefix: `{payload['run_prefix']}`")
    lines.append("")
    if payload.get("eval_json_path"):
        lines.append(f"Eval JSON: `{payload['eval_json_path']}`")
        lines.append("")

    lines.append("## Stack Summary")
    lines.append("")
    lines.append(
        "| Stack | Count | Retrieval traces | Answerable | Quality | Avg top_k | Avg hits | Avg selected | Coverage | Latency |"
    )
    lines.append("| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |")
    for stack in STACKS:
        bucket = payload["summary"]["by_stack"].get(stack) or {}
        lines.append(
            f"| `{stack}` | `{bucket.get('count', 0)}` | `{bucket.get('retrieval_trace_count', 0)}` | `{_percent(bucket.get('answerable_rate', 0.0))}%` | "
            f"`{bucket.get('quality_avg', 0.0)}` | `{bucket.get('avg_top_k', 0.0)}` | "
            f"`{bucket.get('avg_total_hits', 0.0)}` | `{bucket.get('avg_selected_hit_count', 0.0)}` | "
            f"`{bucket.get('avg_coverage_ratio', 0.0)}` | `{bucket.get('latency_avg_ms', 0.0)} ms` |"
        )
    lines.append("")

    lines.append("## Capability Highlights")
    lines.append("")
    lines.append("| Capability | Count | Retrieval traces | Answerable | Quality | Avg top_k | Avg hits | Coverage | Stacks |")
    lines.append("| --- | --- | --- | --- | --- | --- | --- | --- | --- |")
    ranked_capabilities = sorted(
        payload["summary"]["by_capability"].items(),
        key=lambda item: (
            item[1].get("answerable_rate", 0.0),
            item[1].get("quality_avg", 0.0),
            -item[1].get("count", 0),
        ),
    )
    for capability_id, bucket in ranked_capabilities[:15]:
        lines.append(
            f"| `{capability_id}` | `{bucket['count']}` | `{bucket['retrieval_trace_count']}` | `{_percent(bucket['answerable_rate'])}%` | "
            f"`{bucket['quality_avg']}` | `{bucket['avg_top_k']}` | `{bucket['avg_total_hits']}` | "
            f"`{bucket['avg_coverage_ratio']}` | `{', '.join(bucket.get('stacks', []))}` |"
        )
    lines.append("")

    lines.append("## Recommendations")
    lines.append("")
    for item in payload["summary"]["recommendations"]:
        lines.append(f"- {item}")
    if not payload["summary"]["recommendations"]:
        lines.append("- Nenhum ajuste forte recomendado nesta janela.")
    lines.append("")

    lines.append("## Trace Samples")
    lines.append("")
    for item in payload["trace_samples"]:
        lines.append(f"### `{item['stack']}` `{item['capability_id']}` `{item['thread_id']}`")
        lines.append("")
        lines.append(f"- Turn: `{item['turn_index']}`")
        lines.append(f"- Prompt: {item['prompt'] or 'n/a'}")
        lines.append(f"- Policy: `{item['profile']}` / `top_k={item['top_k']}` / `{item['policy_reason']}`")
        lines.append(
            f"- Retrieval: hits `{item['selected_hit_count']}/{item['total_hits']}`, coverage `{item['coverage_ratio']}`, answerable `{item['answerable']}`"
        )
        if item["quality_score"] is not None:
            lines.append(
                f"- Eval: quality `{item['quality_score']}`, keyword pass `{item['keyword_pass']}`, latency `{item['latency_ms']} ms`"
            )
        if item["reason"]:
            lines.append(f"- Reason: `{item['reason']}`")
        if item["error_types"]:
            lines.append(f"- Errors: `{', '.join(item['error_types'])}`")
        lines.append("")
    return "\n".join(lines)


def _main() -> None:
    parser = argparse.ArgumentParser(
        description="Analyze retrieval traces recorded in api-core for a benchmark run."
    )
    parser.add_argument("--run-prefix", required=True)
    parser.add_argument("--database-url", default=DEFAULT_DATABASE_URL)
    parser.add_argument("--postgres-container", default="eduassist-postgres")
    parser.add_argument("--postgres-user", default="eduassist")
    parser.add_argument("--postgres-db", default="eduassist")
    parser.add_argument("--eval-json", default=None)
    parser.add_argument("--report", default=str(DEFAULT_REPORT))
    parser.add_argument("--json-report", default=str(DEFAULT_JSON_REPORT))
    args = parser.parse_args()

    eval_json_path = Path(args.eval_json) if args.eval_json else None
    eval_rows = _load_eval_results(eval_json_path)
    trace_rows = _fetch_rows(
        run_prefix=args.run_prefix,
        postgres_container=args.postgres_container,
        postgres_user=args.postgres_user,
        postgres_db=args.postgres_db,
    )
    items = [
        _trace_item(
            row=row,
            eval_row=eval_rows.get((row.stack, row.thread_id, row.turn_index)),
        )
        for row in trace_rows
    ]
    summary = _aggregate_trace_items(items)
    trace_samples = sorted(
        items,
        key=lambda item: (
            item["quality_score"] if item["quality_score"] is not None else 999,
            item["answerable"] is True,
            item["coverage_ratio"],
        ),
    )[:12]

    payload = {
        "generated_at": datetime.now(UTC).isoformat(),
        "run_prefix": args.run_prefix,
        "database_url": args.database_url,
        "eval_json_path": str(eval_json_path) if eval_json_path else None,
        "trace_count": len(items),
        "summary": summary,
        "trace_samples": trace_samples,
    }

    report_path = Path(args.report)
    json_path = Path(args.json_report)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(_render_markdown(payload) + "\n", encoding="utf-8")
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"trace_count": len(items), "run_prefix": args.run_prefix}, ensure_ascii=False))


if __name__ == "__main__":
    _main()
