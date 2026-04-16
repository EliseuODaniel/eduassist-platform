# Retrieval 30Q Combined Evaluation Report

Generated at: 2026-04-15T06:53:45.212374+00:00

Dataset: `tests/evals/datasets/retrieval_broad_30q_probe_cases.generated.20260415.cycle1.json`
Run prefix: `debug:four-path:normal:20260415T064405Z`
Guardian chat id: `1649845499`
Turn timeout: `90.0s`

## Final Outcome

| Stack | Keyword pass | Quality | Avg latency | Answerable | Avg coverage | Avg top_k |
| --- | --- | --- | --- | --- | --- | --- |
| `langgraph` | `23/30` | `88.7` | `5607.8 ms` | `0.0%` | `1.0` | `3.0` |
| `python_functions` | `20/30` | `86.8` | `6108.2 ms` | `0.0%` | `1.0` | `6.75` |
| `llamaindex` | `21/30` | `86.7` | `6062.9 ms` | `0.0%` | `1.0` | `4.0` |
| `specialist_supervisor` | `25/30` | `95.9` | `1529.3 ms` | `0.0%` | `0.0` | `0.0` |

## Automated Recommendations

- `protected.documents.restricted_lookup` está com `answerable_rate=0.0%` sem saturar `top_k`; vale revisar query variants, metadata e chunking.

## Artifact Paths

- `comparison_report`: `docs/architecture/retrieval-broad-30q-cycle1-fixval-cross-path-report.md`
- `comparison_json`: `docs/architecture/retrieval-broad-30q-cycle1-fixval-cross-path-report.json`
- `trace_report`: `docs/architecture/retrieval-broad-30q-cycle1-fixval-trace-calibration-report.md`
- `trace_json`: `docs/architecture/retrieval-broad-30q-cycle1-fixval-trace-calibration-report.json`

