#!/usr/bin/env python3
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_WAVES = {
    "public_grounding": REPO_ROOT / "docs/architecture/system_question_bank_wave_public_grounding-report-final-v4.json",
    "public_graphrag": REPO_ROOT / "docs/architecture/system_question_bank_wave_public_graphrag-report-final-v4.json",
    "protected_ops": REPO_ROOT / "docs/architecture/system_question_bank_wave_protected_ops-report-final-v4.json",
    "sensitive_external": REPO_ROOT / "docs/architecture/system_question_bank_wave_sensitive_external-report-final-v4.json",
    "teacher_workflow": REPO_ROOT / "docs/architecture/system_question_bank_wave_teacher_workflow-report-final-v4.json",
}
OUTPUT_MD = REPO_ROOT / "docs/architecture/five-path-system-question-bank-v4-scorecard.md"
OUTPUT_JSON = REPO_ROOT / "docs/architecture/five-path-system-question-bank-v4-scorecard.json"


@dataclass
class WaveResult:
    wave: str
    count: int
    ok: int
    quality_avg: float
    avg_latency_ms: float
    error_types: dict[str, int]


def _load_report(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _stack_results_by_wave() -> dict[str, dict[str, WaveResult]]:
    matrix: dict[str, dict[str, WaveResult]] = {}
    for wave_name, path in DEFAULT_WAVES.items():
        payload = _load_report(path)
        by_stack = payload["summary"]["by_stack"]
        error_types = payload["summary"]["error_types"]
        for stack, item in by_stack.items():
            matrix.setdefault(stack, {})[wave_name] = WaveResult(
                wave=wave_name,
                count=int(item["count"]),
                ok=int(item["ok"]),
                quality_avg=float(item["quality_avg"]),
                avg_latency_ms=float(item["avg_latency_ms"]),
                error_types={str(k): int(v) for k, v in (error_types.get(stack) or {}).items()},
            )
    return matrix


def _weighted_average(results: list[WaveResult], field: str) -> float:
    numerator = sum(getattr(item, field) * item.count for item in results)
    denominator = sum(item.count for item in results) or 1
    return round(numerator / denominator, 1)


def _totals(results: list[WaveResult]) -> tuple[int, int]:
    ok = sum(item.ok for item in results)
    count = sum(item.count for item in results)
    return ok, count


def _aggregate_error_types(results: list[WaveResult]) -> dict[str, int]:
    aggregated: dict[str, int] = {}
    for item in results:
        for name, value in item.error_types.items():
            aggregated[name] = aggregated.get(name, 0) + value
    return dict(sorted(aggregated.items()))


def _latency_rank(matrix: dict[str, dict[str, WaveResult]]) -> list[str]:
    return sorted(matrix, key=lambda stack: _weighted_average(list(matrix[stack].values()), "avg_latency_ms"))


def _quality_rank(matrix: dict[str, dict[str, WaveResult]]) -> list[str]:
    return sorted(
        matrix,
        key=lambda stack: (
            -_weighted_average(list(matrix[stack].values()), "quality_avg"),
            _weighted_average(list(matrix[stack].values()), "avg_latency_ms"),
        ),
    )


def _build_payload() -> dict[str, Any]:
    matrix = _stack_results_by_wave()
    stacks: dict[str, Any] = {}
    for stack, waves in matrix.items():
        ordered = [waves[name] for name in DEFAULT_WAVES]
        ok, count = _totals(ordered)
        stacks[stack] = {
            "overall": {
                "ok": ok,
                "count": count,
                "quality_avg": _weighted_average(ordered, "quality_avg"),
                "avg_latency_ms": _weighted_average(ordered, "avg_latency_ms"),
                "error_types": _aggregate_error_types(ordered),
            },
            "waves": {
                item.wave: {
                    "ok": item.ok,
                    "count": item.count,
                    "quality_avg": item.quality_avg,
                    "avg_latency_ms": item.avg_latency_ms,
                    "error_types": item.error_types,
                }
                for item in ordered
            },
        }
    return {
        "wave_order": list(DEFAULT_WAVES.keys()),
        "quality_ranking": _quality_rank(matrix),
        "latency_ranking": _latency_rank(matrix),
        "stacks": stacks,
        "notes": [
            "CrewAI permanece no scorecard como baseline comparativa funcional, sem novos investimentos de arquitetura.",
            "Os caminhos ativos em evolucao sao langgraph, python_functions, llamaindex e specialist_supervisor.",
            "Se um stack tiver request_failed ou *_pilot_unavailable, trate isso como sinal operacional separado de qualidade semantica.",
            "No protected_ops v4, a anomalia residual do specialist_supervisor vem do artifacto anterior ao carregamento automatico do .env no harness source-mode.",
            "Os casos Q039 e Q063 do specialist_supervisor foram retestados depois da correcao do harness e passaram com status 200.",
        ],
    }


def _render_markdown(payload: dict[str, Any]) -> str:
    lines = ["# Five-Path System Question Bank v4 Scorecard", ""]
    lines.append("## Overall")
    lines.append("")
    lines.append("| Stack | OK | Quality | Avg latency | Error types |")
    lines.append("| --- | --- | --- | --- | --- |")
    for stack, info in payload["stacks"].items():
        overall = info["overall"]
        errors = ", ".join(f"{k}={v}" for k, v in overall["error_types"].items()) or "nenhum"
        lines.append(
            f"| `{stack}` | `{overall['ok']}/{overall['count']}` | `{overall['quality_avg']}` | `{overall['avg_latency_ms']} ms` | `{errors}` |"
        )
    lines.append("")
    lines.append("## Rankings")
    lines.append("")
    lines.append(f"- qualidade: {', '.join(f'`{item}`' for item in payload['quality_ranking'])}")
    lines.append(f"- latencia: {', '.join(f'`{item}`' for item in payload['latency_ranking'])}")
    lines.append("")
    lines.append("## By Wave")
    lines.append("")
    for wave_name in payload["wave_order"]:
        lines.append(f"### {wave_name}")
        lines.append("")
        lines.append("| Stack | OK | Quality | Avg latency |")
        lines.append("| --- | --- | --- | --- |")
        for stack, info in payload["stacks"].items():
            wave = info["waves"][wave_name]
            lines.append(
                f"| `{stack}` | `{wave['ok']}/{wave['count']}` | `{wave['quality_avg']}` | `{wave['avg_latency_ms']} ms` |"
            )
        lines.append("")
    lines.append("## Notes")
    lines.append("")
    for note in payload["notes"]:
        lines.append(f"- {note}")
    return "\n".join(lines)


def main() -> int:
    payload = _build_payload()
    OUTPUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    OUTPUT_MD.write_text(_render_markdown(payload) + "\n", encoding="utf-8")
    print(OUTPUT_MD)
    print(OUTPUT_JSON)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
