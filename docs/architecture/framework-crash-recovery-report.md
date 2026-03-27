# Framework Crash Recovery Report

Date: 2026-03-27T13:38:18.740343+00:00

## Scope

This benchmark validates crash-level recovery, not only clean restart, for the strongest framework-native durability paths currently implemented.

- LangGraph protected HITL pause -> kill/start -> inspect pending -> resume
- CrewAI `public` Flow follow-up continuity after container kill/start
- CrewAI `protected` Flow student follow-up continuity after container kill/start

Dataset: [framework_crash_recovery_cases.json](/home/edann/projects/eduassist-platform/tests/evals/datasets/framework_crash_recovery_cases.json)

## Summary

- Passed cases: `3/3`

| Case | Framework | Slice | Result | Crash recovery | Key evidence |
| --- | --- | --- | --- | ---: | --- |
| `langgraph_protected_hitl_crash_recovery` | `langgraph` | `protected` | passed | `5669.8` ms | pending interrupt survived crash; hitl_status=approved |
| `crewai_public_flow_crash_recovery` | `crewai` | `public` | passed | `2612.2` ms | stable flow_state_id; sqlite state file present |
| `crewai_protected_flow_crash_recovery` | `crewai` | `protected` | passed | `2568.9` ms | stable flow_state_id; sqlite state file present |

## langgraph_protected_hitl_crash_recovery

- Framework: `langgraph`
- Slice: `protected`
- Result: `passed`
- Crash recovery duration: `5669.8` ms
- Pending after recovery: `True`
- Resume status: `completed`
- HITL status: `approved`
- Graph path after resume: `classify_request -> security_gate -> route_request -> select_slice -> protected_slice -> structured_tool_call -> protected_human_review -> protected_review_approved`

## crewai_public_flow_crash_recovery

- Framework: `crewai`
- Slice: `public`
- Result: `passed`
- Crash recovery duration: `2612.2` ms
- Flow state before crash: `public:telegram:conversation:benchmark-crash-crewai-public-library-1`
- Flow state after recovery: `public:telegram:conversation:benchmark-crash-crewai-public-library-1`
- Flow persistence available: `True`
- SQLite state file present: `True`
- Before answer: `Sim, a escola tem a Biblioteca Aurora, com atendimento das 7h30 as 18h00.`
- After answer: `A Biblioteca Aurora atende ao publico de segunda a sexta, das 7h30 as 18h00.`

## crewai_protected_flow_crash_recovery

- Framework: `crewai`
- Slice: `protected`
- Result: `passed`
- Crash recovery duration: `2568.9` ms
- Flow state before crash: `protected:telegram:conversation:benchmark-crash-crewai-protected-lucas-1`
- Flow state after recovery: `protected:telegram:conversation:benchmark-crash-crewai-protected-lucas-1`
- Flow persistence available: `True`
- SQLite state file present: `True`
- Before answer: `Perfeito, seguimos com Lucas Oliveira. Posso te ajudar com notas, frequencia, faltas, proximas provas, documentacao, matricula e financeiro.`
- After answer: `A situacao documental de Lucas Oliveira hoje esta regular e completa.`

## Readout

Evidence from this run suggests:

- LangGraph persistence is now strong enough to survive a hard process kill on the protected HITL path and still resume the same review thread.
- CrewAI `Flow` state for `public` and `protected` survives kill/start recovery with the same state identity and follow-up continuity.
- The two stacks are now comparable not only on quality and latency, but on crash-level continuity in their strongest native durability paths.
