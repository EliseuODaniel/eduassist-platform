# Retrieval 30Q Combined Evaluation Report

Generated at: 2026-04-15T06:05:23.828860+00:00

Dataset: `tests/evals/datasets/retrieval_broad_30q_probe_cases.generated.20260415.cycle1.json`
Run prefix: `debug:four-path:normal:20260415T055537Z`
Guardian chat id: `1649845499`
Turn timeout: `35.0s`

## Final Outcome

| Stack | Keyword pass | Quality | Avg latency | Answerable | Avg coverage | Avg top_k |
| --- | --- | --- | --- | --- | --- | --- |
| `langgraph` | `22/30` | `89.4` | `5308.5 ms` | `0.0%` | `1.0` | `3.0` |
| `python_functions` | `21/30` | `90.5` | `6134.2 ms` | `0.0%` | `1.0` | `6.2` |
| `llamaindex` | `19/30` | `84.6` | `6191.3 ms` | `0.0%` | `1.0` | `4.0` |
| `specialist_supervisor` | `25/30` | `94.4` | `1893.9 ms` | `0.0%` | `0.0` | `0.0` |

## Automated Recommendations

- `protected.documents.restricted_lookup` está com `answerable_rate=0.0%` sem saturar `top_k`; vale revisar query variants, metadata e chunking.

## Artifact Paths

- `comparison_report`: `docs/architecture/retrieval-broad-30q-cycle1-rerun-cross-path-report.md`
- `comparison_json`: `docs/architecture/retrieval-broad-30q-cycle1-rerun-cross-path-report.json`
- `trace_report`: `docs/architecture/retrieval-broad-30q-cycle1-rerun-trace-calibration-report.md`
- `trace_json`: `docs/architecture/retrieval-broad-30q-cycle1-rerun-trace-calibration-report.json`

