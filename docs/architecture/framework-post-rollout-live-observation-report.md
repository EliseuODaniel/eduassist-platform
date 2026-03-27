# Framework Post-Rollout Live Observation Report

Date: 2026-03-27T16:11:39.283931+00:00

## Summary

- classification: `healthy`
- observation healthy: `True`
- resolved primary stack: `langgraph`
- experiment primary engine: `crewai`
- experiment slice rollouts: `public:2,support:100,workflow:100`

## Live Advisory

- promotable now: `public`
- maintain now: `support, workflow`

## Blocked Slices

- `protected`: protected still trails LangGraph in operator-facing control primitives and should stay behind manual review.

## Service Health

| Service | Running | Health | Started At |
| --- | --- | --- | --- |
| `ai-orchestrator` | `yes` | `healthy` | `2026-03-27T16:04:39.926021032Z` |
| `ai-orchestrator-crewai` | `yes` | `healthy` | `2026-03-27T14:18:56.12672449Z` |
| `api-core` | `yes` | `healthy` | `2026-03-26T16:51:57.183119439Z` |
| `telegram-gateway` | `yes` | `healthy` | `2026-03-26T03:43:36.151886071Z` |

## Latest Rollout Entry

- timestamp: `2026-03-27T16:01:18.904547+00:00`
- intent: `promotion`
- slice: `public`
- before: `1%`
- after: `2%`
- result: `failed`
- reason: `Expandir public de 1% para 2% conforme recomendacao do gate live`
