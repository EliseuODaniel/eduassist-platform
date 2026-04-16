# Retrieval 30Q Combined Evaluation Report

Generated at: 2026-04-15T04:37:32.113624+00:00

Dataset: `tests/evals/datasets/retrieval_broad_30q_probe_cases.generated.20260415.cycle1.json`
Run prefix: `debug:four-path:normal:20260415T042421Z`
Guardian chat id: `1649845499`
Turn timeout: `60.0s`

## Final Outcome

| Stack | Keyword pass | Quality | Avg latency | Answerable | Avg coverage | Avg top_k |
| --- | --- | --- | --- | --- | --- | --- |
| `langgraph` | `19/30` | `88.3` | `7548.9 ms` | `0.0%` | `1.0` | `3.2` |
| `python_functions` | `15/30` | `84.5` | `7553.8 ms` | `0.0%` | `1.0` | `5.5` |
| `llamaindex` | `15/30` | `85.0` | `7000.3 ms` | `0.0%` | `1.0` | `4.0` |
| `specialist_supervisor` | `23/30` | `91.4` | `4222.3 ms` | `0.0%` | `0.0` | `0.0` |

## Automated Recommendations

- Nenhum ajuste forte recomendado nesta rodada.

## Artifact Paths

- `comparison_report`: `docs/architecture/retrieval-broad-30q-cycle1-seq-cross-path-report.md`
- `comparison_json`: `docs/architecture/retrieval-broad-30q-cycle1-seq-cross-path-report.json`
- `trace_report`: `docs/architecture/retrieval-broad-30q-cycle1-seq-trace-report.md`
- `trace_json`: `docs/architecture/retrieval-broad-30q-cycle1-seq-trace-report.json`

