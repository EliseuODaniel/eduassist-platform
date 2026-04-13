# Retrieval 50Q Combined Evaluation Report

Generated at: 2026-04-13T10:20:42.985969+00:00

Dataset: `/home/edann/projects/eduassist-platform/tests/evals/datasets/retrieval_50q_probe_cases.generated.json`
Run prefix: `debug:four-path:normal:20260413T100503Z`
Guardian chat id: `1649845499`
Turn timeout: `40.0s`

## Final Outcome

| Stack | Keyword pass | Quality | Avg latency | Answerable | Avg coverage | Avg top_k |
| --- | --- | --- | --- | --- | --- | --- |
| `langgraph` | `41/50` | `92.3` | `5254.7 ms` | `0.0%` | `1.0` | `3.0` |
| `python_functions` | `36/50` | `88.3` | `6923.5 ms` | `0.0%` | `1.0` | `4.17` |
| `llamaindex` | `34/50` | `83.0` | `5190.6 ms` | `0.0%` | `0.0` | `0.0` |
| `specialist_supervisor` | `41/50` | `94.8` | `1402.7 ms` | `0.0%` | `0.0` | `0.0` |

## Automated Recommendations

- `consulta autenticada de documento interno deve usar retrieval restrito com grounding` está com `answerable_rate=0.0%` sem saturar `top_k`; vale revisar query variants, metadata e chunking.
- `python_functions_local_restricted_documents` está com `answerable_rate=0.0%` e saturando `top_k`; vale testar `top_k` maior ou profile mais profundo.

## Artifact Paths

- `comparison_report`: `/home/edann/projects/eduassist-platform/docs/architecture/retrieval-50q-cross-path-report.md`
- `comparison_json`: `/home/edann/projects/eduassist-platform/docs/architecture/retrieval-50q-cross-path-report.json`
- `trace_report`: `/home/edann/projects/eduassist-platform/docs/architecture/retrieval-50q-trace-calibration-report.md`
- `trace_json`: `/home/edann/projects/eduassist-platform/docs/architecture/retrieval-50q-trace-calibration-report.json`

