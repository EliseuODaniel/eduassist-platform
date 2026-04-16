# Retrieval 30Q Combined Evaluation Report

Generated at: 2026-04-15T18:08:55.929470+00:00

Dataset: `tests/evals/datasets/retrieval_broad_30q_probe_cases.generated.20260415.cycle2.json`
Run prefix: `debug:four-path:normal:20260415T175956Z`
Guardian chat id: `1649845499`
Turn timeout: `90.0s`

## Final Outcome

| Stack | Keyword pass | Quality | Avg latency | Answerable | Avg coverage | Avg top_k |
| --- | --- | --- | --- | --- | --- | --- |
| `langgraph` | `28/30` | `97.9` | `6399.1 ms` | `0.0%` | `1.0` | `3.0` |
| `python_functions` | `29/30` | `99.3` | `4941.1 ms` | `0.0%` | `1.0` | `6.8` |
| `llamaindex` | `29/30` | `99.3` | `5613.4 ms` | `0.0%` | `0.0` | `0.0` |
| `specialist_supervisor` | `30/30` | `100.0` | `991.6 ms` | `0.0%` | `0.0` | `0.0` |

## Automated Recommendations

- `protected.documents.restricted_lookup` está com `answerable_rate=0.0%` sem saturar `top_k`; vale revisar query variants, metadata e chunking.

## Artifact Paths

- `comparison_report`: `docs/architecture/retrieval-broad-30q-cycle2-fixval7-cross-path-report.md`
- `comparison_json`: `docs/architecture/retrieval-broad-30q-cycle2-fixval7-cross-path-report.json`
- `trace_report`: `docs/architecture/retrieval-broad-30q-cycle2-fixval7-trace-calibration-report.md`
- `trace_json`: `docs/architecture/retrieval-broad-30q-cycle2-fixval7-trace-calibration-report.json`

