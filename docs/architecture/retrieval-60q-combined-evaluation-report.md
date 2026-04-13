# Retrieval 60Q Combined Evaluation Report

Generated at: 2026-04-13T13:21:10.383663+00:00

Dataset: `/home/edann/projects/eduassist-platform/tests/evals/datasets/retrieval_50q_probe_cases.generated.json`
Run prefix: `debug:four-path:normal:20260413T125823Z`
Guardian chat id: `1649845499`
Turn timeout: `40.0s`

## Final Outcome

| Stack | Keyword pass | Quality | Avg latency | Answerable | Avg coverage | Avg top_k |
| --- | --- | --- | --- | --- | --- | --- |
| `langgraph` | `48/60` | `90.7` | `5621.2 ms` | `0.0%` | `1.0` | `3.0` |
| `python_functions` | `45/60` | `88.4` | `9062.7 ms` | `0.0%` | `1.0` | `6.75` |
| `llamaindex` | `46/60` | `92.3` | `6919.6 ms` | `0.0%` | `0.0` | `0.0` |
| `specialist_supervisor` | `52/60` | `95.4` | `1147.1 ms` | `0.0%` | `0.0` | `0.0` |

## Automated Recommendations

- `consulta autenticada de documento interno deve usar retrieval restrito com grounding` está com `answerable_rate=0.0%` sem saturar `top_k`; vale revisar query variants, metadata e chunking.

## Artifact Paths

- `comparison_report`: `docs/architecture/retrieval-60q-cross-path-report.md`
- `comparison_json`: `docs/architecture/retrieval-60q-cross-path-report.json`
- `trace_report`: `docs/architecture/retrieval-60q-trace-calibration-report.md`
- `trace_json`: `docs/architecture/retrieval-60q-trace-calibration-report.json`

