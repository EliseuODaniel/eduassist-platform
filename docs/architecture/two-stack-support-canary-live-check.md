# Support Canary Live Check

Date: 2026-03-26

## Canary Scope

- baseline default: `LangGraph`
- experiment enabled: `true`
- experiment primary engine: `CrewAI`
- enrolled slices: `support`
- rollout percent: `100`
- allowlisted Telegram chat: `1649845499`

This means only `support` traffic from the allowlisted chat is routed to the isolated CrewAI pilot. All other slices remain on the baseline stack.

## Runtime Validation

The running orchestrator reports:

- `orchestratorEngine=langgraph`
- `experimentEnabled=true`
- `experimentSlices=support`
- `experimentRolloutPercent=100`

The selector was validated inside the running container:

- `quero falar com o setor financeiro` -> `crewai`, `experiment:support:crewai`
- `qual o horario da biblioteca?` -> `langgraph`, `langgraph`

## Live Checks

### Support prompt on allowlisted chat

Request:

- `quero falar com a secretaria`

Observed response:

- `Sua solicitacao ja estava registrada na fila de secretaria. Protocolo: ATD-20260325-BA3D79BE. Status atual: queued.`

Interpretation:

- the request was routed to the CrewAI support pilot
- the pilot reused the existing support protocol correctly

### Non-support prompt on the same chat

Request:

- `qual o horario da biblioteca?`

Observed response:

- `A Biblioteca Aurora do Colégio Horizonte está aberta de segunda a sexta-feira, das 7h30 às 18h.`

Interpretation:

- the request stayed on the LangGraph baseline
- the canary did not leak into the public slice

## Fix Applied During Live Validation

The first live check exposed a gap in support-slice detection:

- `quero falar com a secretaria` was not initially recognized as `support`

Fix:

- broadened support canary detection in [crewai_engine.py](/home/edann/projects/eduassist-platform/apps/ai-orchestrator/src/ai_orchestrator/engines/crewai_engine.py)
- commit: `036b162` `Broaden support canary slice detection`

After the fix, the live check passed.

## Operational Note

Conversation persistence tables are empty in this local environment, so the canary was validated by:

- runtime status endpoints
- in-container selector checks
- direct live responses from the orchestrator
- CrewAI pilot access logs

Before widening the canary, it is worth restoring end-to-end persisted trace inspection in the local stack as an extra operational guardrail.
