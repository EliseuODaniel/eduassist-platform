# Retrieval 30Q Combined Evaluation Report

Generated at: 2026-04-15T17:13:06.525649+00:00

Dataset: `tests/evals/datasets/retrieval_broad_30q_probe_cases.generated.20260415.cycle2.json`
Run prefix: `debug:four-path:normal:20260415T170303Z`
Guardian chat id: `1649845499`
Turn timeout: `90.0s`

## Final Outcome

| Stack | Keyword pass | Quality | Avg latency | Answerable | Avg coverage | Avg top_k |
| --- | --- | --- | --- | --- | --- | --- |
| `langgraph` | `24/30` | `91.3` | `6416.0 ms` | `0.0%` | `1.0` | `3.0` |
| `python_functions` | `23/30` | `91.6` | `5726.9 ms` | `0.0%` | `1.0` | `6.8` |
| `llamaindex` | `23/30` | `91.6` | `6659.5 ms` | `0.0%` | `0.0` | `0.0` |
| `specialist_supervisor` | `29/30` | `98.5` | `1233.5 ms` | `0.0%` | `0.0` | `0.0` |

## Automated Recommendations

- `protected.documents.restricted_lookup` está com `answerable_rate=0.0%` sem saturar `top_k`; vale revisar query variants, metadata e chunking.

## Artifact Paths

- `comparison_report`: `docs/architecture/retrieval-broad-30q-cycle2-fixval4-cross-path-report.md`
- `comparison_json`: `docs/architecture/retrieval-broad-30q-cycle2-fixval4-cross-path-report.json`
- `trace_report`: `docs/architecture/retrieval-broad-30q-cycle2-fixval4-trace-calibration-report.md`
- `trace_json`: `docs/architecture/retrieval-broad-30q-cycle2-fixval4-trace-calibration-report.json`

