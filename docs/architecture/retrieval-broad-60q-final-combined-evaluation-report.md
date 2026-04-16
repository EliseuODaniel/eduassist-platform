# Retrieval 60Q Combined Evaluation Report

Generated at: 2026-04-16T20:02:34.466057+00:00

Dataset: `tests/evals/datasets/retrieval_broad_60q_probe_cases.generated.20260416.final.json`
Run prefix: `debug:four-path:normal:20260416T195216Z`
Guardian chat id: `1649845499`
Turn timeout: `90.0s`

## Final Outcome

| Stack | Keyword pass | Quality | Avg latency | Answerable | Avg coverage | Avg top_k |
| --- | --- | --- | --- | --- | --- | --- |
| `langgraph` | `60/60` | `100.0` | `2564.4 ms` | `0.0%` | `1.0` | `3.0` |
| `python_functions` | `60/60` | `100.0` | `3768.5 ms` | `0.0%` | `1.0` | `6.56` |
| `llamaindex` | `60/60` | `100.0` | `3413.0 ms` | `0.0%` | `0.0` | `0.0` |
| `specialist_supervisor` | `60/60` | `100.0` | `524.7 ms` | `0.0%` | `0.0` | `0.0` |

## Automated Recommendations

- `protected.documents.restricted_lookup` está com `answerable_rate=0.0%` sem saturar `top_k`; vale revisar query variants, metadata e chunking.

## Artifact Paths

- `comparison_report`: `docs/architecture/retrieval-broad-60q-final-cross-path-report.md`
- `comparison_json`: `docs/architecture/retrieval-broad-60q-final-cross-path-report.json`
- `trace_report`: `docs/architecture/retrieval-broad-60q-final-trace-calibration-report.md`
- `trace_json`: `docs/architecture/retrieval-broad-60q-final-trace-calibration-report.json`

