# Framework Release Snapshot Report

Date: 2026-03-27T17:33:35.302157+00:00

## Goal

Capture a single operational snapshot before merge or rollout promotion, using live runtime state plus framework rollout artifacts.

## Release Posture

- classification: `ready`
- ready for guarded release: `True`
- branch: `feature/two-stack-shadow-comparison`
- commit: `8c4addb17ce9f3801603994e808efa62e9d2b617`
- working tree clean: `True`
- working tree release-ready: `True`

## Runtime Snapshot

- resolved primary stack: `langgraph`
- experiment primary engine: `crewai`
- experiment slices: `public,support,workflow`
- experiment slice rollouts: `public:5,support:100,workflow:100`
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
- keep protected blocked: CrewAI protected live routing requires `CREWAI_HITL_USER_TRAFFIC_ENABLED=true` in the pilot.

## Latest Rollout Changelog Entries

| Date | Intent | Slice | Before | After | Result | Operator | Reason |
| --- | --- | --- | ---: | ---: | --- | --- | --- |
| `2026-03-27T17:27:40.589600+00:00` | `promotion` | `protected` | `1%` | `100%` | `passed` | `codex` | Drill controlado do protected em 100% com allowlist sintetica |
| `2026-03-27T17:26:17.986764+00:00` | `promotion` | `protected` | `0%` | `1%` | `passed` | `codex` | Ativar canario protegido controlado do CrewAI com HITL |
| `2026-03-27T17:25:42.785370+00:00` | `promotion` | `protected` | `0%` | `1%` | `passed` | `codex` | Ativar canario protegido controlado do CrewAI com HITL |
| `2026-03-27T16:12:28.601970+00:00` | `promotion` | `public` | `2%` | `5%` | `passed` | `codex` | Expandir public de 2% para 5% conforme recomendacao do gate live |
| `2026-03-27T16:01:18.904547+00:00` | `promotion` | `public` | `1%` | `2%` | `failed` | `codex` | Expandir public de 1% para 2% conforme recomendacao do gate live |
