# Retrieval 30Q Combined Evaluation Report

Generated at: 2026-04-16T12:59:34.589449+00:00

Dataset: `tests/evals/datasets/retrieval_broad_30q_probe_cases.generated.20260416.cycle6.json`
Run prefix: `debug:four-path:normal:20260416T125438Z`
Guardian chat id: `1649845499`
Turn timeout: `90.0s`

## Final Outcome

| Stack | Keyword pass | Quality | Avg latency | Answerable | Avg coverage | Avg top_k |
| --- | --- | --- | --- | --- | --- | --- |
| `langgraph` | `30/30` | `100.0` | `2458.3 ms` | `0.0%` | `1.0` | `3.0` |
| `python_functions` | `30/30` | `100.0` | `3528.8 ms` | `0.0%` | `1.0` | `7.0` |
| `llamaindex` | `30/30` | `100.0` | `3311.2 ms` | `0.0%` | `0.0` | `0.0` |
| `specialist_supervisor` | `30/30` | `100.0` | `552.7 ms` | `0.0%` | `0.0` | `0.0` |

## Automated Recommendations

- `protected.documents.restricted_lookup` está com `answerable_rate=0.0%` sem saturar `top_k`; vale revisar query variants, metadata e chunking.

## Artifact Paths

- `comparison_report`: `docs/architecture/retrieval-broad-30q-cycle6-fixval4-cross-path-report.md`
- `comparison_json`: `docs/architecture/retrieval-broad-30q-cycle6-fixval4-cross-path-report.json`
- `trace_report`: `docs/architecture/retrieval-broad-30q-cycle6-fixval4-trace-calibration-report.md`
- `trace_json`: `docs/architecture/retrieval-broad-30q-cycle6-fixval4-trace-calibration-report.json`

