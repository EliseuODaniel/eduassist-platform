# Framework Release Snapshot Report

Date: 2026-03-27T15:49:07.130835+00:00

## Goal

Capture a single operational snapshot before merge or rollout promotion, using live runtime state plus framework rollout artifacts.

## Release Posture

- classification: `ready`
- ready for guarded release: `True`
- branch: `feature/two-stack-shadow-comparison`
- commit: `2f40971d1d9324a4ed4b4f77f2c44a1e1ed64fd4`
- working tree clean: `True`

## Runtime Snapshot

- resolved primary stack: `langgraph`
- experiment primary engine: `crewai`
- experiment slices: `support,public,workflow`
- experiment slice rollouts: `support:100,public:1,workflow:100`
- experiment allowlist slices: `support,workflow`

## Service Health

| Service | Running | Health |
| --- | --- | --- |
| `ai-orchestrator` | `yes` | `healthy` |
| `ai-orchestrator-crewai` | `yes` | `healthy` |
| `api-core` | `yes` | `healthy` |
| `telegram-gateway` | `yes` | `healthy` |

## Next Operator Actions

- consider gradual promotion for public
- maintain current controlled posture for support
- maintain current controlled posture for workflow
- keep protected blocked: protected still trails LangGraph in operator-facing control primitives and should stay behind manual review.

## Latest Rollout Changelog Entries

| Date | Intent | Slice | Before | After | Result | Operator | Reason |
| --- | --- | --- | ---: | ---: | --- | --- | --- |
| `2026-03-27T15:39:44.095113+00:00` | `rollback` | `public` | `2%` | `1%` | `passed` | `codex` | Reverter public para o nivel anterior do canario |
| `2026-03-27T15:37:33.016974+00:00` | `promotion` | `public` | `1%` | `2%` | `passed` | `codex` | Expandir public de 1% para 2% apos estabilidade do canario |
| `2026-03-27T15:33:33.005730+00:00` | `promotion` | `public` | `1%` | `2%` | `passed` | `` |  |
