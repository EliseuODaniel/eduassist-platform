# Retrieval 30Q Combined Evaluation Report

Generated at: 2026-04-15T12:19:08.117903+00:00

Dataset: `tests/evals/datasets/retrieval_broad_30q_probe_cases.generated.20260415.cycle1.json`
Run prefix: `debug:four-path:normal:20260415T120853Z`
Guardian chat id: `1649845499`
Turn timeout: `90.0s`

## Final Outcome

| Stack | Keyword pass | Quality | Avg latency | Answerable | Avg coverage | Avg top_k |
| --- | --- | --- | --- | --- | --- | --- |
| `langgraph` | `26/30` | `97.3` | `6489.2 ms` | `0.0%` | `1.0` | `3.0` |
| `python_functions` | `27/30` | `97.7` | `5609.6 ms` | `0.0%` | `1.0` | `6.6` |
| `llamaindex` | `26/30` | `97.0` | `6340.0 ms` | `0.0%` | `1.0` | `4.0` |
| `specialist_supervisor` | `26/30` | `97.3` | `2025.4 ms` | `0.0%` | `0.0` | `0.0` |

## Automated Recommendations

- `protected.documents.restricted_lookup` está com `answerable_rate=0.0%` sem saturar `top_k`; vale revisar query variants, metadata e chunking.

## Artifact Paths

- `comparison_report`: `docs/architecture/retrieval-broad-30q-cycle1-fixval5-cross-path-report.md`
- `comparison_json`: `docs/architecture/retrieval-broad-30q-cycle1-fixval5-cross-path-report.json`
- `trace_report`: `docs/architecture/retrieval-broad-30q-cycle1-fixval5-trace-calibration-report.md`
- `trace_json`: `docs/architecture/retrieval-broad-30q-cycle1-fixval5-trace-calibration-report.json`

