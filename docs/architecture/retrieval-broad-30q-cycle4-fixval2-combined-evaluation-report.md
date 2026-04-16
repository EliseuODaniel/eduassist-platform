# Retrieval 30Q Combined Evaluation Report

Generated at: 2026-04-15T23:47:06.216123+00:00

Dataset: `tests/evals/datasets/retrieval_broad_30q_probe_cases.generated.20260415.cycle4.json`
Run prefix: `debug:four-path:normal:20260415T233640Z`
Guardian chat id: `1649845499`
Turn timeout: `90.0s`

## Final Outcome

| Stack | Keyword pass | Quality | Avg latency | Answerable | Avg coverage | Avg top_k |
| --- | --- | --- | --- | --- | --- | --- |
| `langgraph` | `23/30` | `83.8` | `15471.6 ms` | `0.0%` | `1.0` | `3.0` |
| `python_functions` | `22/30` | `83.1` | `11216.7 ms` | `0.0%` | `1.0` | `7.0` |
| `llamaindex` | `23/30` | `83.4` | `13514.4 ms` | `0.0%` | `0.0` | `0.0` |
| `specialist_supervisor` | `26/30` | `88.2` | `8125.4 ms` | `0.0%` | `0.0` | `0.0` |

## Automated Recommendations

- `protected.documents.restricted_lookup` está com `answerable_rate=0.0%` sem saturar `top_k`; vale revisar query variants, metadata e chunking.

## Artifact Paths

- `comparison_report`: `docs/architecture/retrieval-broad-30q-cycle4-fixval2-cross-path-report.md`
- `comparison_json`: `docs/architecture/retrieval-broad-30q-cycle4-fixval2-cross-path-report.json`
- `trace_report`: `docs/architecture/retrieval-broad-30q-cycle4-fixval2-trace-calibration-report.md`
- `trace_json`: `docs/architecture/retrieval-broad-30q-cycle4-fixval2-trace-calibration-report.json`

