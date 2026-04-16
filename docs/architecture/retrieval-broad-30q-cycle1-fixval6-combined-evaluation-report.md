# Retrieval 30Q Combined Evaluation Report

Generated at: 2026-04-15T12:59:18.458975+00:00

Dataset: `tests/evals/datasets/retrieval_broad_30q_probe_cases.generated.20260415.cycle1.json`
Run prefix: `debug:four-path:normal:20260415T125004Z`
Guardian chat id: `1649845499`
Turn timeout: `90.0s`

## Final Outcome

| Stack | Keyword pass | Quality | Avg latency | Answerable | Avg coverage | Avg top_k |
| --- | --- | --- | --- | --- | --- | --- |
| `langgraph` | `28/30` | `98.7` | `5591.8 ms` | `0.0%` | `1.0` | `3.0` |
| `python_functions` | `26/30` | `89.0` | `5699.2 ms` | `0.0%` | `1.0` | `6.6` |
| `llamaindex` | `28/30` | `93.0` | `5804.5 ms` | `0.0%` | `0.0` | `0.0` |
| `specialist_supervisor` | `27/30` | `96.3` | `1348.2 ms` | `0.0%` | `0.0` | `0.0` |

## Automated Recommendations

- `protected.documents.restricted_lookup` está com `answerable_rate=0.0%` sem saturar `top_k`; vale revisar query variants, metadata e chunking.

## Artifact Paths

- `comparison_report`: `docs/architecture/retrieval-broad-30q-cycle1-fixval6-cross-path-report.md`
- `comparison_json`: `docs/architecture/retrieval-broad-30q-cycle1-fixval6-cross-path-report.json`
- `trace_report`: `docs/architecture/retrieval-broad-30q-cycle1-fixval6-trace-calibration-report.md`
- `trace_json`: `docs/architecture/retrieval-broad-30q-cycle1-fixval6-trace-calibration-report.json`

