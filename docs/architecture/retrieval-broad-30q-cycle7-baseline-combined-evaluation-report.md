# Retrieval 30Q Combined Evaluation Report

Generated at: 2026-04-16T13:04:45.719212+00:00

Dataset: `tests/evals/datasets/retrieval_broad_30q_probe_cases.generated.20260416.cycle7.json`
Run prefix: `debug:four-path:normal:20260416T130030Z`
Guardian chat id: `1649845499`
Turn timeout: `90.0s`

## Final Outcome

| Stack | Keyword pass | Quality | Avg latency | Answerable | Avg coverage | Avg top_k |
| --- | --- | --- | --- | --- | --- | --- |
| `langgraph` | `29/30` | `98.6` | `2077.9 ms` | `0.0%` | `1.0` | `3.0` |
| `python_functions` | `29/30` | `98.6` | `2879.3 ms` | `0.0%` | `1.0` | `6.8` |
| `llamaindex` | `30/30` | `100.0` | `2652.3 ms` | `0.0%` | `0.0` | `0.0` |
| `specialist_supervisor` | `30/30` | `100.0` | `892.6 ms` | `0.0%` | `0.0` | `0.0` |

## Automated Recommendations

- `protected.documents.restricted_lookup` está com `answerable_rate=0.0%` sem saturar `top_k`; vale revisar query variants, metadata e chunking.

## Artifact Paths

- `comparison_report`: `docs/architecture/retrieval-broad-30q-cycle7-baseline-cross-path-report.md`
- `comparison_json`: `docs/architecture/retrieval-broad-30q-cycle7-baseline-cross-path-report.json`
- `trace_report`: `docs/architecture/retrieval-broad-30q-cycle7-baseline-trace-calibration-report.md`
- `trace_json`: `docs/architecture/retrieval-broad-30q-cycle7-baseline-trace-calibration-report.json`

