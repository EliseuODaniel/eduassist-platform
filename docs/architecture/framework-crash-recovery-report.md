# Framework Crash Recovery Report

Date: 2026-03-27T13:47:24.224105+00:00

## Scope

This benchmark validates crash-level recovery, not only clean restart, for the strongest framework-native durability paths currently implemented.

- LangGraph protected HITL pause -> kill/start -> inspect pending -> resume
- CrewAI `public` Flow follow-up continuity after container kill/start
- CrewAI `protected` Flow student follow-up continuity after container kill/start
- CrewAI `support` Flow follow-up continuity after container kill/start
- CrewAI `workflow` Flow follow-up continuity after container kill/start

Dataset: [framework_crash_recovery_cases.json](/home/edann/projects/eduassist-platform/tests/evals/datasets/framework_crash_recovery_cases.json)

## Summary

- Passed cases: `5/5`

| Case | Framework | Slice | Result | Crash recovery | Key evidence |
| --- | --- | --- | --- | ---: | --- |
| `langgraph_protected_hitl_crash_recovery` | `langgraph` | `protected` | passed | `5661.2` ms | pending interrupt survived crash; hitl_status=approved |
| `crewai_public_flow_crash_recovery` | `crewai` | `public` | passed | `2595.4` ms | stable flow_state_id; sqlite state file present |
| `crewai_protected_flow_crash_recovery` | `crewai` | `protected` | passed | `2558.9` ms | stable flow_state_id; sqlite state file present |
| `crewai_support_flow_crash_recovery` | `crewai` | `support` | passed | `2565.2` ms | stable flow_state_id; sqlite state file present |
| `crewai_workflow_flow_crash_recovery` | `crewai` | `workflow` | passed | `2616.7` ms | stable flow_state_id; sqlite state file present |

## langgraph_protected_hitl_crash_recovery

- Framework: `langgraph`
- Slice: `protected`
- Result: `passed`
- Crash recovery duration: `5661.2` ms
- Pending after recovery: `True`
- Resume status: `completed`
- HITL status: `approved`
- Graph path after resume: `classify_request -> security_gate -> route_request -> select_slice -> protected_slice -> structured_tool_call -> protected_human_review -> protected_review_approved -> classify_request -> security_gate -> route_request -> select_slice -> classify_request -> security_gate -> route_request -> select_slice -> protected_slice -> structured_tool_call -> protected_human_review -> protected_review_approved -> classify_request -> security_gate -> route_request -> select_slice -> protected_slice -> structured_tool_call -> protected_human_review -> protected_review_approved`

## crewai_public_flow_crash_recovery

- Framework: `crewai`
- Slice: `public`
- Result: `passed`
- Crash recovery duration: `2595.4` ms
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
- Crash recovery duration: `2558.9` ms
- Flow state before crash: `protected:telegram:conversation:benchmark-crash-crewai-protected-lucas-1`
- Flow state after recovery: `protected:telegram:conversation:benchmark-crash-crewai-protected-lucas-1`
- Flow persistence available: `True`
- SQLite state file present: `True`
- Before answer: `Perfeito, seguimos com Lucas Oliveira. Posso te ajudar com notas, frequencia, faltas, proximas provas, documentacao, matricula e financeiro.`
- After answer: `A situacao documental de Lucas Oliveira hoje esta regular e completa.`

## crewai_support_flow_crash_recovery

- Framework: `crewai`
- Slice: `support`
- Result: `passed`
- Crash recovery duration: `2565.2` ms
- Flow state before crash: `support:telegram:conversation:benchmark-crash-crewai-support-secretaria-1`
- Flow state after recovery: `support:telegram:conversation:benchmark-crash-crewai-support-secretaria-1`
- Flow persistence available: `True`
- SQLite state file present: `True`
- Before answer: `Sua solicitacao ja estava registrada na fila de secretaria. Protocolo: ATD-20260327-A226E914. Status atual: queued.`
- After answer: `O protocolo do seu atendimento e ATD-20260327-A226E914. O status atual e "queued", o que significa que sua solicitacao esta na fila para ser atendida pela equipe de secretaria.`

## crewai_workflow_flow_crash_recovery

- Framework: `crewai`
- Slice: `workflow`
- Result: `passed`
- Crash recovery duration: `2616.7` ms
- Flow state before crash: `workflow:telegram:conversation:benchmark-crash-crewai-workflow-visit-1`
- Flow state after recovery: `workflow:telegram:conversation:benchmark-crash-crewai-workflow-visit-1`
- Flow persistence available: `True`
- SQLite state file present: `True`
- Before answer: `Pedido de visita registrado para o Colegio Horizonte. Protocolo: VIS-20260327-A1EF85. Preferencia informada: 02/04/2026 - tarde. Fila responsavel: admissoes. Ticket operacional: ATD-20260327-9EAB997C. A equipe comercial valida a janela e retorna com a confirmacao.`
- After answer: `O protocolo da sua visita e VIS-20260327-A1EF85. - Ticket operacional: ATD-20260327-9EAB997C - Preferencia registrada: 02/04/2026 - tarde Se quiser, eu tambem posso te dizer o status, remarcar ou cancelar a visita.`

## Readout

Evidence from this run suggests:

- LangGraph persistence is now strong enough to survive a hard process kill on the protected HITL path and still resume the same review thread.
- CrewAI `Flow` state for `public`, `protected`, `support`, and `workflow` survives kill/start recovery with the same state identity and follow-up continuity.
- The two stacks are now comparable not only on quality and latency, but on crash-level continuity in their strongest native durability paths.
