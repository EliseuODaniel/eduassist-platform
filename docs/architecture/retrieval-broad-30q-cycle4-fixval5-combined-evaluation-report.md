# Retrieval 30Q Combined Evaluation Report

Generated at: 2026-04-16T01:19:41.537210+00:00

Dataset: `tests/evals/datasets/retrieval_broad_30q_probe_cases.generated.20260415.cycle4.json`
Run prefix: `debug:four-path:normal:20260416T011258Z`
Guardian chat id: `1649845499`
Turn timeout: `90.0s`

## Final Outcome

| Stack | Keyword pass | Quality | Avg latency | Answerable | Avg coverage | Avg top_k |
| --- | --- | --- | --- | --- | --- | --- |
| `langgraph` | `27/30` | `97.2` | `11648.4 ms` | `0.0%` | `1.0` | `3.0` |
| `python_functions` | `27/30` | `98.0` | `8161.6 ms` | `0.0%` | `1.0` | `6.8` |
| `llamaindex` | `27/30` | `97.2` | `9389.8 ms` | `0.0%` | `0.0` | `0.0` |
| `specialist_supervisor` | `30/30` | `99.7` | `3706.4 ms` | `0.0%` | `0.0` | `0.0` |

## Automated Recommendations

- `protected.documents.restricted_lookup` está com `answerable_rate=0.0%` sem saturar `top_k`; vale revisar query variants, metadata e chunking.

## Artifact Paths

- `comparison_report`: `docs/architecture/retrieval-broad-30q-cycle4-fixval5-cross-path-report.md`
- `comparison_json`: `docs/architecture/retrieval-broad-30q-cycle4-fixval5-cross-path-report.json`
- `trace_report`: `docs/architecture/retrieval-broad-30q-cycle4-fixval5-trace-calibration-report.md`
- `trace_json`: `docs/architecture/retrieval-broad-30q-cycle4-fixval5-trace-calibration-report.json`

