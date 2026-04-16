# Retrieval 30Q Combined Evaluation Report

Generated at: 2026-04-15T08:22:45.401238+00:00

Dataset: `tests/evals/datasets/retrieval_broad_30q_probe_cases.generated.20260415.cycle1.json`
Run prefix: `debug:four-path:normal:20260415T081243Z`
Guardian chat id: `1649845499`
Turn timeout: `90.0s`

## Final Outcome

| Stack | Keyword pass | Quality | Avg latency | Answerable | Avg coverage | Avg top_k |
| --- | --- | --- | --- | --- | --- | --- |
| `langgraph` | `26/30` | `96.5` | `6034.2 ms` | `0.0%` | `1.0` | `3.0` |
| `python_functions` | `23/30` | `93.9` | `5384.8 ms` | `0.0%` | `1.0` | `6.75` |
| `llamaindex` | `24/30` | `94.5` | `6363.0 ms` | `0.0%` | `1.0` | `4.0` |
| `specialist_supervisor` | `27/30` | `97.2` | `2250.2 ms` | `0.0%` | `0.0` | `0.0` |

## Automated Recommendations

- `protected.documents.restricted_lookup` está com `answerable_rate=0.0%` sem saturar `top_k`; vale revisar query variants, metadata e chunking.

## Artifact Paths

- `comparison_report`: `docs/architecture/retrieval-broad-30q-cycle1-fixval4-cross-path-report.md`
- `comparison_json`: `docs/architecture/retrieval-broad-30q-cycle1-fixval4-cross-path-report.json`
- `trace_report`: `docs/architecture/retrieval-broad-30q-cycle1-fixval4-trace-calibration-report.md`
- `trace_json`: `docs/architecture/retrieval-broad-30q-cycle1-fixval4-trace-calibration-report.json`

