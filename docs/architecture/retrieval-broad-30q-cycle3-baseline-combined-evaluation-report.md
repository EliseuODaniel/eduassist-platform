# Retrieval 30Q Combined Evaluation Report

Generated at: 2026-04-15T19:50:37.615357+00:00

Dataset: `tests/evals/datasets/retrieval_broad_30q_probe_cases.generated.20260415.cycle3.json`
Run prefix: `debug:four-path:normal:20260415T194135Z`
Guardian chat id: `1649845499`
Turn timeout: `90.0s`

## Final Outcome

| Stack | Keyword pass | Quality | Avg latency | Answerable | Avg coverage | Avg top_k |
| --- | --- | --- | --- | --- | --- | --- |
| `langgraph` | `29/30` | `98.5` | `5051.8 ms` | `0.0%` | `1.0` | `3.0` |
| `python_functions` | `28/30` | `97.9` | `5474.5 ms` | `100.0%` | `1.0` | `6.17` |
| `llamaindex` | `29/30` | `98.5` | `6273.9 ms` | `0.0%` | `0.0` | `0.0` |
| `specialist_supervisor` | `28/30` | `97.8` | `1270.6 ms` | `0.0%` | `0.0` | `0.0` |

## Automated Recommendations

- `protected.documents.restricted_lookup` está com `answerable_rate=0.0%` sem saturar `top_k`; vale revisar query variants, metadata e chunking.

## Artifact Paths

- `comparison_report`: `docs/architecture/retrieval-broad-30q-cycle3-baseline-cross-path-report.md`
- `comparison_json`: `docs/architecture/retrieval-broad-30q-cycle3-baseline-cross-path-report.json`
- `trace_report`: `docs/architecture/retrieval-broad-30q-cycle3-baseline-trace-calibration-report.md`
- `trace_json`: `docs/architecture/retrieval-broad-30q-cycle3-baseline-trace-calibration-report.json`

