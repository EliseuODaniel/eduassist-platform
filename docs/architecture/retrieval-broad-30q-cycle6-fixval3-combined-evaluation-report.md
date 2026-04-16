# Retrieval 30Q Combined Evaluation Report

Generated at: 2026-04-16T12:38:54.868795+00:00

Dataset: `tests/evals/datasets/retrieval_broad_30q_probe_cases.generated.20260416.cycle6.json`
Run prefix: `debug:four-path:normal:20260416T123037Z`
Guardian chat id: `1649845499`
Turn timeout: `90.0s`

## Final Outcome

| Stack | Keyword pass | Quality | Avg latency | Answerable | Avg coverage | Avg top_k |
| --- | --- | --- | --- | --- | --- | --- |
| `langgraph` | `30/30` | `100.0` | `5095.4 ms` | `0.0%` | `1.0` | `3.0` |
| `python_functions` | `30/30` | `100.0` | `4104.7 ms` | `0.0%` | `1.0` | `7.0` |
| `llamaindex` | `30/30` | `99.7` | `3693.8 ms` | `0.0%` | `0.0` | `0.0` |
| `specialist_supervisor` | `29/30` | `96.7` | `3651.4 ms` | `0.0%` | `0.0` | `0.0` |

## Automated Recommendations

- `protected.documents.restricted_lookup` está com `answerable_rate=0.0%` sem saturar `top_k`; vale revisar query variants, metadata e chunking.

## Artifact Paths

- `comparison_report`: `docs/architecture/retrieval-broad-30q-cycle6-fixval3-cross-path-report.md`
- `comparison_json`: `docs/architecture/retrieval-broad-30q-cycle6-fixval3-cross-path-report.json`
- `trace_report`: `docs/architecture/retrieval-broad-30q-cycle6-fixval3-trace-calibration-report.md`
- `trace_json`: `docs/architecture/retrieval-broad-30q-cycle6-fixval3-trace-calibration-report.json`

