# Retrieval 30Q Combined Evaluation Report

Generated at: 2026-04-15T14:31:43.387587+00:00

Dataset: `tests/evals/datasets/retrieval_broad_30q_probe_cases.generated.20260415.cycle2.json`
Run prefix: `debug:four-path:normal:20260415T141948Z`
Guardian chat id: `1649845499`
Turn timeout: `90.0s`

## Final Outcome

| Stack | Keyword pass | Quality | Avg latency | Answerable | Avg coverage | Avg top_k |
| --- | --- | --- | --- | --- | --- | --- |
| `langgraph` | `26/30` | `96.5` | `8294.6 ms` | `0.0%` | `1.0` | `3.0` |
| `python_functions` | `24/30` | `94.8` | `7500.8 ms` | `0.0%` | `1.0` | `6.8` |
| `llamaindex` | `24/30` | `92.5` | `5600.1 ms` | `0.0%` | `0.0` | `0.0` |
| `specialist_supervisor` | `26/30` | `95.4` | `2379.0 ms` | `0.0%` | `0.0` | `0.0` |

## Automated Recommendations

- `protected.documents.restricted_lookup` está com `answerable_rate=0.0%` sem saturar `top_k`; vale revisar query variants, metadata e chunking.

## Artifact Paths

- `comparison_report`: `docs/architecture/retrieval-broad-30q-cycle2-baseline-cross-path-report.md`
- `comparison_json`: `docs/architecture/retrieval-broad-30q-cycle2-baseline-cross-path-report.json`
- `trace_report`: `docs/architecture/retrieval-broad-30q-cycle2-baseline-trace-calibration-report.md`
- `trace_json`: `docs/architecture/retrieval-broad-30q-cycle2-baseline-trace-calibration-report.json`

