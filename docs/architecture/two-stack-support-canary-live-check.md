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

## Live Baseline vs Canary Compare

A direct live compare was run through the same main orchestrator endpoint.

### Fresh support creation

- baseline, non-allowlisted chat:
  - request: `quero falar com a secretaria`
  - latency: `178.3ms`
  - result: created a new `secretaria` handoff
- canary, allowlisted chat with fresh conversation id:
  - request: `quero falar com a secretaria`
  - latency: `214.4ms`
  - result: created a new `secretaria` handoff through the CrewAI support pilot

Observed interpretation:

- correctness matched in both paths
- latency was close in the live end-to-end path
- this is expected because the main orchestrator still pays shared costs outside the slice-specific engine, such as request handling and persistence

### Public control on the same endpoint

- baseline, non-allowlisted chat:
  - request: `qual o horario da biblioteca?`
  - latency: `7254.3ms`
- allowlisted chat:
  - request: `qual o horario da biblioteca?`
  - latency: `6970.9ms`

Observed interpretation:

- both requests stayed on the baseline public path
- the support canary did not contaminate the public slice
- the public latency gap remains a separate baseline optimization problem

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
