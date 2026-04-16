# Retrieval 30Q Combined Evaluation Report

Generated at: 2026-04-16T07:00:05.852531+00:00

Dataset: `tests/evals/datasets/retrieval_broad_30q_probe_cases.generated.20260416.cycle6.json`
Run prefix: `debug:four-path:normal:20260416T064210Z`
Guardian chat id: `1649845499`
Turn timeout: `90.0s`

## Final Outcome

| Stack | Keyword pass | Quality | Avg latency | Answerable | Avg coverage | Avg top_k |
| --- | --- | --- | --- | --- | --- | --- |
| `langgraph` | `29/30` | `96.7` | `12594.8 ms` | `0.0%` | `1.0` | `3.0` |
| `python_functions` | `27/30` | `90.0` | `10579.2 ms` | `0.0%` | `1.0` | `7.0` |
| `llamaindex` | `28/30` | `93.3` | `5843.0 ms` | `0.0%` | `0.0` | `0.0` |
| `specialist_supervisor` | `28/30` | `93.3` | `6611.5 ms` | `0.0%` | `0.0` | `0.0` |

## Automated Recommendations

- `protected.documents.restricted_lookup` está com `answerable_rate=0.0%` sem saturar `top_k`; vale revisar query variants, metadata e chunking.

## Artifact Paths

- `comparison_report`: `docs/architecture/retrieval-broad-30q-cycle6-fixval1-cross-path-report.md`
- `comparison_json`: `docs/architecture/retrieval-broad-30q-cycle6-fixval1-cross-path-report.json`
- `trace_report`: `docs/architecture/retrieval-broad-30q-cycle6-fixval1-trace-calibration-report.md`
- `trace_json`: `docs/architecture/retrieval-broad-30q-cycle6-fixval1-trace-calibration-report.json`

