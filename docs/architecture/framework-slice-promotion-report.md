# Framework Slice Promotion Report

Date: 2026-03-27T17:27:40.589600+00:00

## Summary

- intent: `promotion`
- slice: `protected`
- before rollout: `1%`
- after rollout: `100%`
- mode: `execute`
- apply requested: `True`
- result: `passed`
- operator: `codex`
- reason: `Drill controlado do protected em 100% com allowlist sintetica`
- env file: `artifacts/tmp-protected-canary.env`
- proposed slices: `protected,public,support,workflow`
- proposed slice rollouts: `protected:100,public:5,support:100,workflow:100`
- proposed allowlist slices: `protected,support,workflow`
- proposed telegram chat allowlist: ``
- proposed conversation allowlist: `protected-canary-drill-1`
- proposed CrewAI protected user-traffic HITL: `True`
- proposed CrewAI HITL slices: `protected`
- nested report: `/home/edann/projects/eduassist-platform/docs/architecture/framework-rollout-execution-report.md`

## STDERR

```text
 Container eduassist-ai-orchestrator-crewai Running 
 Container eduassist-ai-orchestrator Recreate 
 Container eduassist-ai-orchestrator Recreated 
 Container eduassist-ai-orchestrator Starting 
 Container eduassist-ai-orchestrator Started 

```
