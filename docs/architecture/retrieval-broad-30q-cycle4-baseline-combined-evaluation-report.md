# Retrieval 30Q Combined Evaluation Report

Generated at: 2026-04-15T21:38:22.016087+00:00

Dataset: `tests/evals/datasets/retrieval_broad_30q_probe_cases.generated.20260415.cycle4.json`
Run prefix: `debug:four-path:normal:20260415T212355Z`
Guardian chat id: `1649845499`
Turn timeout: `90.0s`

## Final Outcome

| Stack | Keyword pass | Quality | Avg latency | Answerable | Avg coverage | Avg top_k |
| --- | --- | --- | --- | --- | --- | --- |
| `langgraph` | `26/30` | `95.2` | `6760.4 ms` | `0.0%` | `1.0` | `3.2` |
| `python_functions` | `24/30` | `89.3` | `8532.8 ms` | `0.0%` | `1.0` | `6.75` |
| `llamaindex` | `25/30` | `89.4` | `8165.9 ms` | `0.0%` | `0.0` | `0.0` |
| `specialist_supervisor` | `27/30` | `94.7` | `5435.1 ms` | `0.0%` | `0.0` | `0.0` |

## Automated Recommendations

- `protected.documents.restricted_lookup` está com `answerable_rate=0.0%` sem saturar `top_k`; vale revisar query variants, metadata e chunking.

## Artifact Paths

- `comparison_report`: `docs/architecture/retrieval-broad-30q-cycle4-baseline-cross-path-report.md`
- `comparison_json`: `docs/architecture/retrieval-broad-30q-cycle4-baseline-cross-path-report.json`
- `trace_report`: `docs/architecture/retrieval-broad-30q-cycle4-baseline-trace-calibration-report.md`
- `trace_json`: `docs/architecture/retrieval-broad-30q-cycle4-baseline-trace-calibration-report.json`

