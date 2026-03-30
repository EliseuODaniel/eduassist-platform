# Four-Path Chatbot Smoke Report

Date: 2026-03-30T12:58:25.030994+00:00

## Goal

Validate the first four chatbot paths side by side under strict framework isolation:

- `langgraph`
- `crewai`
- `python_functions`
- `llamaindex`

## Stack Summary

| Stack | Passed | Avg latency |
| --- | --- | --- |
| `langgraph` | `4/4` | `274.3 ms` |
| `crewai` | `4/4` | `717.2 ms` |
| `python_functions` | `4/4` | `238.0 ms` |
| `llamaindex` | `4/4` | `255.3 ms` |

## Case Details

| Case | Stack | Result | Mode | Access tier | Latency | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| `public_pedagogy` | `langgraph` | passed | `structured_tool` | `public` | `312.4 ms` | fato institucional canonico deve vir de fonte estruturada |
| `protected_docs` | `langgraph` | passed | `structured_tool` | `authenticated` | `282.6 ms` | status administrativo autenticado exige service deterministico |
| `support_finance` | `langgraph` | passed | `handoff` | `public` | `235.4 ms` | o usuario demonstrou necessidade de atendimento humano ou operacional |
| `workflow_visit` | `langgraph` | passed | `structured_tool` | `public` | `266.8 ms` | a solicitacao pode ser executada por workflow estruturado com protocolo |
| `public_pedagogy` | `crewai` | passed | `structured_tool` | `public` | `1368.6 ms` | crewai_public_fast_path |
| `protected_docs` | `crewai` | passed | `structured_tool` | `authenticated` | `854.6 ms` | crewai_protected_fast_path |
| `support_finance` | `crewai` | passed | `structured_tool` | `public` | `340.3 ms` | support_handoff_reused |
| `workflow_visit` | `crewai` | passed | `structured_tool` | `public` | `305.1 ms` | workflow_visit_create |
| `public_pedagogy` | `python_functions` | passed | `structured_tool` | `public` | `206.0 ms` | fato institucional canonico deve vir de fonte estruturada |
| `protected_docs` | `python_functions` | passed | `structured_tool` | `authenticated` | `266.1 ms` | status administrativo autenticado exige service deterministico |
| `support_finance` | `python_functions` | passed | `handoff` | `public` | `216.6 ms` | o usuario demonstrou necessidade de atendimento humano ou operacional |
| `workflow_visit` | `python_functions` | passed | `structured_tool` | `public` | `263.5 ms` | a solicitacao pode ser executada por workflow estruturado com protocolo |
| `public_pedagogy` | `llamaindex` | passed | `structured_tool` | `public` | `209.8 ms` | fato institucional canonico deve vir de fonte estruturada |
| `protected_docs` | `llamaindex` | passed | `structured_tool` | `authenticated` | `293.1 ms` | status administrativo autenticado exige service deterministico |
| `support_finance` | `llamaindex` | passed | `handoff` | `public` | `242.9 ms` | o usuario demonstrou necessidade de atendimento humano ou operacional |
| `workflow_visit` | `llamaindex` | passed | `structured_tool` | `public` | `275.4 ms` | a solicitacao pode ser executada por workflow estruturado com protocolo |

## Interpretation

- `python_functions` is the lean baseline: shared planner and executor, no heavy orchestration framework around the control loop.
- `llamaindex` uses the same planner/executor kernel but runs it inside a native LlamaIndex Workflow with explicit `plan -> execute -> reflect` steps.
- `langgraph` and `crewai` remain the original framework-native paths, which keeps the comparison fair.

