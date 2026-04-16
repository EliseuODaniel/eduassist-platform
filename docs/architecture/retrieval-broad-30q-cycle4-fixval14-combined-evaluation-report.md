# Retrieval 30Q Combined Evaluation Report

Generated at: 2026-04-16T05:59:57.033602+00:00

Dataset: `tests/evals/datasets/retrieval_broad_30q_probe_cases.generated.20260415.cycle4.json`
Run prefix: `debug:four-path:normal:20260416T055059Z`
Guardian chat id: `1649845499`
Turn timeout: `90.0s`

## Final Outcome

| Stack | Keyword pass | Quality | Avg latency | Answerable | Avg coverage | Avg top_k |
| --- | --- | --- | --- | --- | --- | --- |
| `langgraph` | `30/30` | `99.7` | `4467.2 ms` | `0.0%` | `1.0` | `3.0` |
| `python_functions` | `30/30` | `99.7` | `5759.7 ms` | `0.0%` | `1.0` | `6.8` |
| `llamaindex` | `30/30` | `99.7` | `5818.1 ms` | `0.0%` | `0.0` | `0.0` |
| `specialist_supervisor` | `30/30` | `99.7` | `1813.9 ms` | `0.0%` | `0.0` | `0.0` |

## Automated Recommendations

- `protected.documents.restricted_lookup` está com `answerable_rate=0.0%` sem saturar `top_k`; vale revisar query variants, metadata e chunking.

## Artifact Paths

- `comparison_report`: `docs/architecture/retrieval-broad-30q-cycle4-fixval14-cross-path-report.md`
- `comparison_json`: `docs/architecture/retrieval-broad-30q-cycle4-fixval14-cross-path-report.json`
- `trace_report`: `docs/architecture/retrieval-broad-30q-cycle4-fixval14-trace-calibration-report.md`
- `trace_json`: `docs/architecture/retrieval-broad-30q-cycle4-fixval14-trace-calibration-report.json`

