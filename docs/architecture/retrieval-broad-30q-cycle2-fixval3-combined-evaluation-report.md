# Retrieval 30Q Combined Evaluation Report

Generated at: 2026-04-15T16:41:29.579320+00:00

Dataset: `tests/evals/datasets/retrieval_broad_30q_probe_cases.generated.20260415.cycle2.json`
Run prefix: `debug:four-path:normal:20260415T163141Z`
Guardian chat id: `1649845499`
Turn timeout: `90.0s`

## Final Outcome

| Stack | Keyword pass | Quality | Avg latency | Answerable | Avg coverage | Avg top_k |
| --- | --- | --- | --- | --- | --- | --- |
| `langgraph` | `25/30` | `93.8` | `6324.9 ms` | `0.0%` | `1.0` | `3.0` |
| `python_functions` | `23/30` | `85.7` | `5531.6 ms` | `0.0%` | `1.0` | `6.8` |
| `llamaindex` | `23/30` | `85.7` | `5832.1 ms` | `0.0%` | `0.0` | `0.0` |
| `specialist_supervisor` | `28/30` | `98.7` | `1884.9 ms` | `0.0%` | `0.0` | `0.0` |

## Automated Recommendations

- `protected.documents.restricted_lookup` está com `answerable_rate=0.0%` sem saturar `top_k`; vale revisar query variants, metadata e chunking.

## Artifact Paths

- `comparison_report`: `docs/architecture/retrieval-broad-30q-cycle2-fixval3-cross-path-report.md`
- `comparison_json`: `docs/architecture/retrieval-broad-30q-cycle2-fixval3-cross-path-report.json`
- `trace_report`: `docs/architecture/retrieval-broad-30q-cycle2-fixval3-trace-calibration-report.md`
- `trace_json`: `docs/architecture/retrieval-broad-30q-cycle2-fixval3-trace-calibration-report.json`

