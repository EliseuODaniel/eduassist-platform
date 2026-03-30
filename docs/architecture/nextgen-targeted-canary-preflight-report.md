# Next-Gen Targeted Canary Preflight Report

Date: 2026-03-30T14:46:21.491010+00:00

Base URL: `http://127.0.0.1:8002`

Dataset: `/home/edann/projects/eduassist-platform/tests/evals/datasets/nextgen_targeted_canary_cases.json`

## Summary

| Stack | Allowlisted lane | Control lane | Ready for targeted canary |
| --- | --- | --- | --- |
| `python_functions` | `2/2` | `2/2` | `True` |
| `llamaindex` | `2/2` | `2/2` | `True` |

## Runtime State

- Before: `resolved=langgraph` from `orchestrator_engine`
- Baseline during preflight: `resolved=langgraph` from `orchestrator_engine`
- Targeted before: `None`
- After restore: `resolved=langgraph` from `orchestrator_engine`
- Targeted after restore: `None`

## Why this drill uses `protected`

- O objetivo aqui e provar que so a conversa allowlisted entra na stack nova.
- O slice `protected` foi escolhido porque o baseline atual fica em `LangGraph`, sem ruido do experimento vivo que ainda existe em outros slices.
- O drill usa o mesmo chat autenticado nos dois lados e muda apenas o `conversation_id`, para isolar a regra de canario sem perder o contexto real de autenticacao.

## Probe Results

| Case | Stack | Lane | Result | Mode | Targeted hit | Access tier | Reason |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `protected_lucas_docs` | `python_functions` | `allowlisted` | passed | `structured_tool` | `True` | `authenticated` | `status administrativo autenticado exige service deterministico` |
| `protected_lucas_docs` | `python_functions` | `control` | passed | `structured_tool` | `False` | `authenticated` | `status administrativo autenticado exige service deterministico` |
| `protected_ana_docs` | `python_functions` | `allowlisted` | passed | `structured_tool` | `True` | `authenticated` | `status administrativo autenticado exige service deterministico` |
| `protected_ana_docs` | `python_functions` | `control` | passed | `structured_tool` | `False` | `authenticated` | `status administrativo autenticado exige service deterministico` |
| `protected_lucas_docs` | `llamaindex` | `allowlisted` | passed | `structured_tool` | `True` | `authenticated` | `status administrativo autenticado exige service deterministico` |
| `protected_lucas_docs` | `llamaindex` | `control` | passed | `structured_tool` | `False` | `authenticated` | `status administrativo autenticado exige service deterministico` |
| `protected_ana_docs` | `llamaindex` | `allowlisted` | passed | `structured_tool` | `True` | `authenticated` | `status administrativo autenticado exige service deterministico` |
| `protected_ana_docs` | `llamaindex` | `control` | passed | `structured_tool` | `False` | `authenticated` | `status administrativo autenticado exige service deterministico` |
