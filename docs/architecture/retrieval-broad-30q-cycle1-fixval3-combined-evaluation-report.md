# Retrieval 30Q Combined Evaluation Report

Generated at: 2026-04-15T07:54:21.765691+00:00

Dataset: `tests/evals/datasets/retrieval_broad_30q_probe_cases.generated.20260415.cycle1.json`
Run prefix: `debug:four-path:normal:20260415T074433Z`
Guardian chat id: `1649845499`
Turn timeout: `90.0s`

## Final Outcome

| Stack | Keyword pass | Quality | Avg latency | Answerable | Avg coverage | Avg top_k |
| --- | --- | --- | --- | --- | --- | --- |
| `langgraph` | `25/30` | `95.9` | `6336.4 ms` | `0.0%` | `1.0` | `3.0` |
| `python_functions` | `23/30` | `94.2` | `5748.7 ms` | `0.0%` | `1.0` | `6.75` |
| `llamaindex` | `24/30` | `94.5` | `5892.6 ms` | `0.0%` | `1.0` | `4.0` |
| `specialist_supervisor` | `25/30` | `95.9` | `1597.4 ms` | `0.0%` | `0.0` | `0.0` |

## Automated Recommendations

- `protected.documents.restricted_lookup` está com `answerable_rate=0.0%` sem saturar `top_k`; vale revisar query variants, metadata e chunking.

## Artifact Paths

- `comparison_report`: `docs/architecture/retrieval-broad-30q-cycle1-fixval3-cross-path-report.md`
- `comparison_json`: `docs/architecture/retrieval-broad-30q-cycle1-fixval3-cross-path-report.json`
- `trace_report`: `docs/architecture/retrieval-broad-30q-cycle1-fixval3-trace-calibration-report.md`
- `trace_json`: `docs/architecture/retrieval-broad-30q-cycle1-fixval3-trace-calibration-report.json`

