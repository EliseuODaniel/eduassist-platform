# Retrieval 30Q Combined Evaluation Report

Generated at: 2026-04-16T17:11:07.924005+00:00

Dataset: `tests/evals/datasets/retrieval_broad_30q_probe_cases.generated.20260416.cycle11.json`
Run prefix: `debug:four-path:normal:20260416T170131Z`
Guardian chat id: `1649845499`
Turn timeout: `90.0s`

## Final Outcome

| Stack | Keyword pass | Quality | Avg latency | Answerable | Avg coverage | Avg top_k |
| --- | --- | --- | --- | --- | --- | --- |
| `langgraph` | `30/30` | `99.6` | `5948.8 ms` | `0.0%` | `1.0` | `3.0` |
| `python_functions` | `30/30` | `99.6` | `4078.9 ms` | `0.0%` | `1.0` | `6.6` |
| `llamaindex` | `29/30` | `96.7` | `4160.3 ms` | `0.0%` | `0.0` | `0.0` |
| `specialist_supervisor` | `28/30` | `96.0` | `4977.9 ms` | `0.0%` | `0.0` | `0.0` |

## Automated Recommendations

- `protected.documents.restricted_lookup` está com `answerable_rate=0.0%` sem saturar `top_k`; vale revisar query variants, metadata e chunking.

## Artifact Paths

- `comparison_report`: `docs/architecture/retrieval-broad-30q-cycle11-baseline-cross-path-report.md`
- `comparison_json`: `docs/architecture/retrieval-broad-30q-cycle11-baseline-cross-path-report.json`
- `trace_report`: `docs/architecture/retrieval-broad-30q-cycle11-baseline-trace-calibration-report.md`
- `trace_json`: `docs/architecture/retrieval-broad-30q-cycle11-baseline-trace-calibration-report.json`

