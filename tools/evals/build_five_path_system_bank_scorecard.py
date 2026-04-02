#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_WAVE_NAMES = (
    "public_grounding",
    "public_graphrag",
    "protected_ops",
    "sensitive_external",
    "teacher_workflow",
)


@dataclass
class WaveResult:
    wave: str
    count: int
    ok: int
    quality_avg: float
    avg_latency_ms: float
    error_types: dict[str, int]


def _default_wave_path(wave: str, version: str) -> Path:
    return REPO_ROOT / f"docs/architecture/system_question_bank_wave_{wave}-report-final-{version}.json"


def _load_report(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _stack_results_by_wave(version: str, wave_paths: dict[str, Path]) -> dict[str, dict[str, WaveResult]]:
    matrix: dict[str, dict[str, WaveResult]] = {}
    for wave_name in DEFAULT_WAVE_NAMES:
        path = wave_paths.get(wave_name) or _default_wave_path(wave_name, version)
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


def _build_payload(version: str, wave_paths: dict[str, Path]) -> dict[str, Any]:
    matrix = _stack_results_by_wave(version, wave_paths)
    stacks: dict[str, Any] = {}
    for stack, waves in matrix.items():
        ordered = [waves[name] for name in DEFAULT_WAVE_NAMES]
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
        "version": version,
        "wave_order": list(DEFAULT_WAVE_NAMES),
        "quality_ranking": _quality_rank(matrix),
        "latency_ranking": _latency_rank(matrix),
        "stacks": stacks,
        "notes": [
            "O caminho legado do CrewAI foi arquivado; os caminhos ativos em evolucao sao langgraph, python_functions, llamaindex e specialist_supervisor.",
            "Os caminhos ativos em evolucao sao langgraph, python_functions, llamaindex e specialist_supervisor.",
            "Erros operacionais como *_pilot_unavailable e runtime_unconfigured devem ser lidos separadamente de qualidade semantica.",
            "O benchmark context de cada onda deve ser consultado junto com o scorecard para interpretar drift de ambiente e modo de execucao.",
        ],
    }


def _render_markdown(payload: dict[str, Any]) -> str:
    version = payload["version"]
    lines = [f"# Five-Path System Question Bank {version} Scorecard", ""]
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
    parser = argparse.ArgumentParser()
    parser.add_argument("--version", default="v5")
    parser.add_argument("--output-md", type=Path, default=None)
    parser.add_argument("--output-json", type=Path, default=None)
    parser.add_argument("--wave-path", action="append", default=[], help="wave=path.json")
    args = parser.parse_args()

    wave_paths: dict[str, Path] = {}
    for item in args.wave_path:
        if "=" not in item:
            raise SystemExit(f"invalid --wave-path value: {item}")
        wave, raw_path = item.split("=", 1)
        wave_paths[wave.strip()] = Path(raw_path.strip())

    payload = _build_payload(args.version, wave_paths)
    output_md = args.output_md or REPO_ROOT / f"docs/architecture/five-path-system-question-bank-{args.version}-scorecard.md"
    output_json = args.output_json or REPO_ROOT / f"docs/architecture/five-path-system-question-bank-{args.version}-scorecard.json"
    output_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    output_md.write_text(_render_markdown(payload) + "\n", encoding="utf-8")
    print(output_md)
    print(output_json)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
