# Four-Path Chatbot Smoke Report

Date: 2026-03-30T05:41:25.591950+00:00

## Goal

Validate the first four chatbot paths side by side under strict framework isolation:

- `langgraph`
- `crewai`
- `python_functions`
- `llamaindex`

## Stack Summary

| Stack | Passed | Avg latency |
| --- | --- | --- |
| `langgraph` | `4/4` | `165.5 ms` |
| `crewai` | `4/4` | `403.3 ms` |
| `python_functions` | `4/4` | `154.4 ms` |
| `llamaindex` | `4/4` | `149.2 ms` |

## Case Details

| Case | Stack | Result | Mode | Access tier | Latency | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| `public_pedagogy` | `langgraph` | passed | `structured_tool` | `public` | `174.5 ms` | fato institucional canonico deve vir de fonte estruturada |
| `protected_docs` | `langgraph` | passed | `structured_tool` | `authenticated` | `173.7 ms` | status administrativo autenticado exige service deterministico |
| `support_finance` | `langgraph` | passed | `handoff` | `public` | `144.4 ms` | o usuario demonstrou necessidade de atendimento humano ou operacional |
| `workflow_visit` | `langgraph` | passed | `structured_tool` | `public` | `169.2 ms` | a solicitacao pode ser executada por workflow estruturado com protocolo |
| `public_pedagogy` | `crewai` | passed | `structured_tool` | `public` | `822.4 ms` | crewai_public_fast_path |
| `protected_docs` | `crewai` | passed | `structured_tool` | `authenticated` | `412.7 ms` | crewai_protected_fast_path |
| `support_finance` | `crewai` | passed | `structured_tool` | `public` | `180.0 ms` | support_handoff_reused |
| `workflow_visit` | `crewai` | passed | `structured_tool` | `public` | `198.0 ms` | workflow_visit_create |
| `public_pedagogy` | `python_functions` | passed | `structured_tool` | `public` | `123.0 ms` | fato institucional canonico deve vir de fonte estruturada |
| `protected_docs` | `python_functions` | passed | `structured_tool` | `authenticated` | `154.4 ms` | status administrativo autenticado exige service deterministico |
| `support_finance` | `python_functions` | passed | `handoff` | `public` | `191.0 ms` | o usuario demonstrou necessidade de atendimento humano ou operacional |
| `workflow_visit` | `python_functions` | passed | `structured_tool` | `public` | `149.3 ms` | a solicitacao pode ser executada por workflow estruturado com protocolo |
| `public_pedagogy` | `llamaindex` | passed | `structured_tool` | `public` | `124.0 ms` | fato institucional canonico deve vir de fonte estruturada |
| `protected_docs` | `llamaindex` | passed | `structured_tool` | `authenticated` | `165.5 ms` | status administrativo autenticado exige service deterministico |
| `support_finance` | `llamaindex` | passed | `handoff` | `public` | `129.7 ms` | o usuario demonstrou necessidade de atendimento humano ou operacional |
| `workflow_visit` | `llamaindex` | passed | `structured_tool` | `public` | `177.7 ms` | a solicitacao pode ser executada por workflow estruturado com protocolo |

## Interpretation

- `python_functions` is the lean baseline: shared planner and executor, no heavy orchestration framework around the control loop.
- `llamaindex` uses the same planner/executor kernel but runs it inside a native LlamaIndex Workflow with explicit `plan -> execute -> reflect` steps.
- `langgraph` and `crewai` remain the original framework-native paths, which keeps the comparison fair.

