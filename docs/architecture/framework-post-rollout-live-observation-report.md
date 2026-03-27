# Framework Post-Rollout Live Observation Report

Date: 2026-03-27T17:29:35.382805+00:00

## Summary

- classification: `healthy`
- observation healthy: `True`
- resolved primary stack: `langgraph`
- experiment primary engine: `crewai`
- experiment slice rollouts: `public:5,support:100,workflow:100`
- telegram chat allowlist count: `1`
- conversation allowlist count: `0`

## Live Advisory

- promotable now: `public`
- maintain now: `support, workflow`

## Blocked Slices

- `protected`: CrewAI protected live routing requires `CREWAI_HITL_USER_TRAFFIC_ENABLED=true` in the pilot.

## CrewAI Pilot Review Gate

- user-traffic HITL enabled: `False`
- user-traffic HITL slices: `protected`

## Service Health

| Service | Running | Health | Started At |
| --- | --- | --- | --- |
| `ai-orchestrator` | `yes` | `healthy` | `2026-03-27T17:28:41.087092308Z` |
| `ai-orchestrator-crewai` | `yes` | `healthy` | `2026-03-27T17:28:40.495173426Z` |
| `api-core` | `yes` | `healthy` | `2026-03-26T16:51:57.183119439Z` |
| `telegram-gateway` | `yes` | `healthy` | `2026-03-26T03:43:36.151886071Z` |

## Latest Rollout Entry

- timestamp: `2026-03-27T17:27:40.589600+00:00`
- intent: `promotion`
- slice: `protected`
- before: `1%`
- after: `100%`
- result: `passed`
- reason: `Drill controlado do protected em 100% com allowlist sintetica`
