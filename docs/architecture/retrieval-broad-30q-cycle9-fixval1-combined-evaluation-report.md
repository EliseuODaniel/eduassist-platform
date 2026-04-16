# Retrieval 30Q Combined Evaluation Report

Generated at: 2026-04-16T16:13:40.639034+00:00

Dataset: `tests/evals/datasets/retrieval_broad_30q_probe_cases.generated.20260416.cycle9.json`
Run prefix: `debug:four-path:normal:20260416T160828Z`
Guardian chat id: `1649845499`
Turn timeout: `90.0s`

## Final Outcome

| Stack | Keyword pass | Quality | Avg latency | Answerable | Avg coverage | Avg top_k |
| --- | --- | --- | --- | --- | --- | --- |
| `langgraph` | `30/30` | `100.0` | `2711.6 ms` | `0.0%` | `1.0` | `3.0` |
| `python_functions` | `30/30` | `100.0` | `3666.5 ms` | `0.0%` | `1.0` | `6.8` |
| `llamaindex` | `30/30` | `100.0` | `3385.9 ms` | `0.0%` | `0.0` | `0.0` |
| `specialist_supervisor` | `30/30` | `100.0` | `613.4 ms` | `0.0%` | `0.0` | `0.0` |

## Automated Recommendations

- `protected.documents.restricted_lookup` está com `answerable_rate=0.0%` sem saturar `top_k`; vale revisar query variants, metadata e chunking.

## Artifact Paths

- `comparison_report`: `docs/architecture/retrieval-broad-30q-cycle9-fixval1-cross-path-report.md`
- `comparison_json`: `docs/architecture/retrieval-broad-30q-cycle9-fixval1-cross-path-report.json`
- `trace_report`: `docs/architecture/retrieval-broad-30q-cycle9-fixval1-trace-calibration-report.md`
- `trace_json`: `docs/architecture/retrieval-broad-30q-cycle9-fixval1-trace-calibration-report.json`

