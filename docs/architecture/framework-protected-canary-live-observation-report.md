# Framework Protected Canary Live Observation Report

Date: 2026-03-27T17:28:22.370800+00:00

## Summary

- classification: `ready`
- protected configured: `True`
- protected live: `True`
- protected allowlist only: `True`
- protected pilot live gate ok: `True`
- pilot user-traffic HITL enabled: `True`
- pilot user-traffic HITL slices: `protected`
- telegram chat allowlist count: `0`
- conversation allowlist count: `1`

## Protected Advisory

```json
{
  "eligible": true,
  "configured": true,
  "live": true,
  "allowlist_only": true,
  "configured_rollout_percent": 100,
  "action": "maintain_controlled",
  "pilot_live_gate_ok": true,
  "pilot_live_gate_reason": "",
  "blocked_reasons": []
}
```

## Pilot Status

```json
{
  "service": "ai-orchestrator-crewai",
  "ready": true,
  "crewaiInstalled": true,
  "crewaiVersion": "1.12.2",
  "slice": "public+protected+workflow+support",
  "mode": "pilot",
  "googleModel": "gemini-2.5-flash-preview",
  "llmConfigured": true,
  "capabilities": [
    "public-shadow-flow",
    "protected-shadow-flow",
    "workflow-shadow-flow",
    "support-shadow-flow",
    "isolated-dependencies",
    "planner-composer-judge",
    "flow-state-routing",
    "flow-state-persistence",
    "task-trace-telemetry",
    "task-guardrails",
    "agentic-rendering-for-support-workflow",
    "crewai-hitl-internal",
    "crewai-hitl-user-traffic"
  ],
  "flowStateDir": "/workspace/artifacts/crewai-flow-state",
  "crewaiHitlEnabled": true,
  "crewaiHitlDefaultSlices": "protected",
  "crewaiHitlUserTrafficEnabled": true,
  "crewaiHitlUserTrafficSlices": "protected"
}
```
