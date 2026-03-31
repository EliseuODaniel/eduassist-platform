# Five-Path Chatbot Smoke Report

Date: 2026-03-30T23:45:09.721538+00:00

Dataset: `/home/edann/projects/eduassist-platform/tests/evals/datasets/four_path_chatbot_smoke_cases.json`

Run prefix: `debug:five-path-smoke:20260330T234505Z`

## Goal

Validate the first five chatbot paths side by side under strict framework isolation:

- `langgraph`
- `crewai`
- `python_functions`
- `llamaindex`
- `specialist_supervisor`

## Stack Summary

| Stack | Passed | Avg latency |
| --- | --- | --- |
| `langgraph` | `4/4` | `193.2 ms` |
| `crewai` | `4/4` | `457.9 ms` |
| `python_functions` | `4/4` | `162.5 ms` |
| `llamaindex` | `4/4` | `161.3 ms` |
| `specialist_supervisor` | `4/4` | `102.6 ms` |

## Case Details

| Case | Stack | Result | Mode | Access tier | Latency | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| `public_pedagogy` | `langgraph` | passed | `structured_tool` | `public` | `300.1 ms` | fato institucional canonico deve vir de fonte estruturada |
| `protected_docs` | `langgraph` | passed | `structured_tool` | `authenticated` | `167.6 ms` | status administrativo autenticado exige service deterministico |
| `support_finance` | `langgraph` | passed | `handoff` | `public` | `139.8 ms` | o usuario demonstrou necessidade de atendimento humano ou operacional |
| `workflow_visit` | `langgraph` | passed | `structured_tool` | `public` | `165.1 ms` | a solicitacao pode ser executada por workflow estruturado com protocolo |
| `public_pedagogy` | `crewai` | passed | `structured_tool` | `public` | `962.7 ms` | crewai_public_fast_path |
| `protected_docs` | `crewai` | passed | `structured_tool` | `authenticated` | `432.7 ms` | crewai_protected_fast_path |
| `support_finance` | `crewai` | passed | `structured_tool` | `public` | `220.7 ms` | support_handoff_created |
| `workflow_visit` | `crewai` | passed | `structured_tool` | `public` | `215.4 ms` | workflow_visit_create |
| `public_pedagogy` | `python_functions` | passed | `structured_tool` | `public` | `138.6 ms` | python_functions_native_structured:institution |
| `protected_docs` | `python_functions` | passed | `structured_tool` | `authenticated` | `173.3 ms` | python_functions_native_structured:institution |
| `support_finance` | `python_functions` | passed | `handoff` | `public` | `148.5 ms` | o usuario demonstrou necessidade de atendimento humano ou operacional |
| `workflow_visit` | `python_functions` | passed | `structured_tool` | `public` | `189.7 ms` | python_functions_native_structured:support |
| `public_pedagogy` | `llamaindex` | passed | `structured_tool` | `public` | `146.0 ms` | llamaindex_public_profile |
| `protected_docs` | `llamaindex` | passed | `structured_tool` | `authenticated` | `171.5 ms` | status administrativo autenticado exige service deterministico |
| `support_finance` | `llamaindex` | passed | `handoff` | `public` | `145.9 ms` | o usuario demonstrou necessidade de atendimento humano ou operacional |
| `workflow_visit` | `llamaindex` | passed | `structured_tool` | `public` | `181.7 ms` | a solicitacao pode ser executada por workflow estruturado com protocolo |
| `public_pedagogy` | `specialist_supervisor` | passed | `structured_tool` | `public` | `80.4 ms` | specialist_supervisor_fast_path:pedagogical_proposal |
| `protected_docs` | `specialist_supervisor` | passed | `structured_tool` | `authenticated` | `118.9 ms` | specialist_supervisor_tool_first:administrative_status |
| `support_finance` | `specialist_supervisor` | passed | `handoff` | `public` | `105.0 ms` | specialist_supervisor_tool_first:support_handoff |
| `workflow_visit` | `specialist_supervisor` | passed | `structured_tool` | `public` | `106.2 ms` | specialist_supervisor_tool_first:visit_booking |

## Interpretation

- `python_functions` is the lean code-first baseline with a planner/executor/reflection loop.
- `llamaindex` pushes native workflow, retrieval, citation, and document lifecycle capabilities further.
- `specialist_supervisor` is the quality-first path with manager pattern and specialists-as-tools on top of the shared truth sources.
- `langgraph` and `crewai` remain the original framework-native paths, which keeps the comparison fair.

