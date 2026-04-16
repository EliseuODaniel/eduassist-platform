# Retrieval 30Q Combined Evaluation Report

Generated at: 2026-04-15T04:16:05.678883+00:00

Dataset: `tests/evals/datasets/retrieval_broad_30q_probe_cases.generated.20260415.cycle1.json`
Run prefix: `debug:four-path:normal:20260415T040512Z`
Guardian chat id: `1649845499`
Turn timeout: `40.0s`

## Final Outcome

| Stack | Keyword pass | Quality | Avg latency | Answerable | Avg coverage | Avg top_k |
| --- | --- | --- | --- | --- | --- | --- |
| `langgraph` | `14/30` | `58.5` | `17046.9 ms` | `0.0%` | `1.0` | `3.0` |
| `python_functions` | `17/30` | `65.5` | `17880.1 ms` | `0.0%` | `1.0` | `7.0` |
| `llamaindex` | `17/30` | `65.2` | `16477.6 ms` | `0.0%` | `1.0` | `4.0` |
| `specialist_supervisor` | `21/30` | `79.2` | `8537.5 ms` | `0.0%` | `0.0` | `0.0` |

## Automated Recommendations

- Nenhum ajuste forte recomendado nesta rodada.

## Artifact Paths

- `comparison_report`: `docs/architecture/retrieval-broad-30q-cycle1-cross-path-report.md`
- `comparison_json`: `docs/architecture/retrieval-broad-30q-cycle1-cross-path-report.json`
- `trace_report`: `docs/architecture/retrieval-broad-30q-cycle1-trace-report.md`
- `trace_json`: `docs/architecture/retrieval-broad-30q-cycle1-trace-report.json`

