# Framework Live Promotion Summary

Date: 2026-03-27T17:07:27.973328+00:00

## Goal

Summarize the live rollout posture before any canary promotion by slice.

## Live Summary

- resolved primary stack: `langgraph`
- experiment enabled: `True`
- experiment active: `True`
- candidate engine: `crewai`
- pilot configured: `True`
- pilot ready: `True`
- scorecard loaded: `True`
- primary-stack native path passed: `True`
- promotable now: `public`
- maintain now: `support, workflow`

## Per Slice Advisory

| Slice | Action | Eligible | Live | Rollout | Allowlist Only | Blocked Reasons |
| --- | --- | --- | --- | ---: | --- | --- |
| `public` | `expand_gradually` | `yes` | `yes` | `5%` | `no` |  |
| `protected` | `blocked` | `no` | `no` | `0%` | `no` | CrewAI protected live routing requires `CREWAI_HITL_USER_TRAFFIC_ENABLED=true` in the pilot. |
| `support` | `maintain_controlled` | `yes` | `yes` | `100%` | `yes` |  |
| `workflow` | `maintain_controlled` | `yes` | `yes` | `100%` | `yes` |  |
