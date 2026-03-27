# Framework Restart Recovery Report

Date: 2026-03-27T13:33:20.516286+00:00

## Scope

This benchmark validates native restart/recovery behavior for the strongest framework-native durability paths currently implemented:

- LangGraph protected HITL resume after process restart
- CrewAI `Flow` continuity for `public` follow-up after process restart
- CrewAI `Flow` continuity for `protected` student follow-up after process restart

Dataset: [framework_restart_recovery_cases.json](/home/edann/projects/eduassist-platform/tests/evals/datasets/framework_restart_recovery_cases.json)

## Summary

- Passed cases: `3/3`

| Case | Framework | Slice | Result | Restart | Key evidence |
| --- | --- | --- | --- | ---: | --- |
| `langgraph_protected_hitl_restart_recovery` | `langgraph` | `protected` | passed | `5678.8` ms | pending interrupt survived restart; hitl_status=approved |
| `crewai_public_flow_restart_recovery` | `crewai` | `public` | passed | `3338.5` ms | stable flow_state_id; sqlite state file present |
| `crewai_protected_flow_restart_recovery` | `crewai` | `protected` | passed | `3239.8` ms | stable flow_state_id; sqlite state file present |

## langgraph_protected_hitl_restart_recovery

- Framework: `langgraph`
- Slice: `protected`
- Result: `passed`
- Restart duration: `5678.8` ms
- Pending after restart: `True`
- Resume status: `completed`
- Graph path after resume: `classify_request -> security_gate -> route_request -> select_slice -> classify_request -> security_gate -> route_request -> select_slice -> protected_slice -> structured_tool_call -> protected_human_review -> protected_review_approved`
- HITL status: `approved`

## crewai_public_flow_restart_recovery

- Framework: `crewai`
- Slice: `public`
- Result: `passed`
- Restart duration: `3338.5` ms
- Flow state before restart: `public:telegram:conversation:benchmark-crewai-public-library-1`
- Flow state after restart: `public:telegram:conversation:benchmark-crewai-public-library-1`
- Flow persistence available: `True`
- SQLite state file present: `True`
- Before answer: `Sim, a escola tem a Biblioteca Aurora, com atendimento das 7h30 as 18h00.`
- After answer: `A Biblioteca Aurora atende ao publico de segunda a sexta, das 7h30 as 18h00.`

## crewai_protected_flow_restart_recovery

- Framework: `crewai`
- Slice: `protected`
- Result: `passed`
- Restart duration: `3239.8` ms
- Flow state before restart: `protected:telegram:conversation:benchmark-crewai-protected-lucas-1`
- Flow state after restart: `protected:telegram:conversation:benchmark-crewai-protected-lucas-1`
- Flow persistence available: `True`
- SQLite state file present: `True`
- Before answer: `Perfeito, seguimos com Lucas Oliveira. Posso te ajudar com notas, frequencia, faltas, proximas provas, documentacao, matricula e financeiro.`
- After answer: `A situacao documental de Lucas Oliveira hoje esta regular e completa.`

## Readout

Evidence from this run suggests:

- LangGraph checkpoint-backed HITL is now durable enough to pause, restart, inspect pending state, and resume the exact protected review thread.
- CrewAI `Flow` state for `public` and `protected` now survives service restart strongly enough to keep follow-up continuity with the same `flow_state_id`.
- This closes the most important durability gap in the top-line roadmap before broader crash/recovery comparisons.
