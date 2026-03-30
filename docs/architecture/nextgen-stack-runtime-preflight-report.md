# Next-Gen Stack Runtime Preflight Report

Date: 2026-03-30T13:32:37.604769+00:00

Base URL: `http://127.0.0.1:8002`

Dataset: `/home/edann/projects/eduassist-platform/tests/evals/datasets/four_path_chatbot_smoke_cases.json`

## Summary

| Stack | Passed | Ready for controlled runtime |
| --- | --- | --- |
| `python_functions` | `4/4` | `True` |
| `llamaindex` | `4/4` | `True` |

## Runtime State

- Before: `resolved=langgraph` from `orchestrator_engine`
- After restore: `resolved=langgraph` from `orchestrator_engine`

## Case Results

| Case | Stack | Result | Mode | Access tier | Reason |
| --- | --- | --- | --- | --- | --- |
| `public_pedagogy` | `python_functions` | passed | `structured_tool` | `public` | `fato institucional canonico deve vir de fonte estruturada` |
| `protected_docs` | `python_functions` | passed | `structured_tool` | `authenticated` | `status administrativo autenticado exige service deterministico` |
| `support_finance` | `python_functions` | passed | `handoff` | `public` | `o usuario demonstrou necessidade de atendimento humano ou operacional` |
| `workflow_visit` | `python_functions` | passed | `structured_tool` | `public` | `a solicitacao pode ser executada por workflow estruturado com protocolo` |
| `public_pedagogy` | `llamaindex` | passed | `structured_tool` | `public` | `fato institucional canonico deve vir de fonte estruturada` |
| `protected_docs` | `llamaindex` | passed | `structured_tool` | `authenticated` | `status administrativo autenticado exige service deterministico` |
| `support_finance` | `llamaindex` | passed | `handoff` | `public` | `o usuario demonstrou necessidade de atendimento humano ou operacional` |
| `workflow_visit` | `llamaindex` | passed | `structured_tool` | `public` | `a solicitacao pode ser executada por workflow estruturado com protocolo` |
