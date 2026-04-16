# Retrieval 30Q Combined Evaluation Report

Generated at: 2026-04-16T01:43:15.022574+00:00

Dataset: `tests/evals/datasets/retrieval_broad_30q_probe_cases.generated.20260415.cycle4.json`
Run prefix: `debug:four-path:normal:20260416T013502Z`
Guardian chat id: `1649845499`
Turn timeout: `90.0s`

## Final Outcome

| Stack | Keyword pass | Quality | Avg latency | Answerable | Avg coverage | Avg top_k |
| --- | --- | --- | --- | --- | --- | --- |
| `langgraph` | `27/30` | `97.2` | `10255.7 ms` | `0.0%` | `1.0` | `3.0` |
| `python_functions` | `26/30` | `94.7` | `11026.1 ms` | `0.0%` | `1.0` | `6.8` |
| `llamaindex` | `26/30` | `96.5` | `11296.8 ms` | `0.0%` | `0.0` | `0.0` |
| `specialist_supervisor` | `30/30` | `99.7` | `6202.5 ms` | `0.0%` | `0.0` | `0.0` |

## Automated Recommendations

- `protected.documents.restricted_lookup` está com `answerable_rate=0.0%` sem saturar `top_k`; vale revisar query variants, metadata e chunking.

## Artifact Paths

- `comparison_report`: `docs/architecture/retrieval-broad-30q-cycle4-fixval6-cross-path-report.md`
- `comparison_json`: `docs/architecture/retrieval-broad-30q-cycle4-fixval6-cross-path-report.json`
- `trace_report`: `docs/architecture/retrieval-broad-30q-cycle4-fixval6-trace-calibration-report.md`
- `trace_json`: `docs/architecture/retrieval-broad-30q-cycle4-fixval6-trace-calibration-report.json`

