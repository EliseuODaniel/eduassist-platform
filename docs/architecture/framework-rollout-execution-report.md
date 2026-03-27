# Framework Rollout Execution Report

Date: 2026-03-27T17:27:40.561575+00:00

## Goal

Record a full rollout operation: preflight, apply to env, service restart, and live status validation.

## Execution Summary

- preflight verdict: `approve`
- preflight safe_to_apply: `True`
- restart attempted: `True`
- services restarted: `ai-orchestrator, ai-orchestrator-crewai`
- env file: `artifacts/tmp-protected-canary.env`
- backup path: `/home/edann/projects/eduassist-platform/artifacts/env-snapshots/tmp-protected-canary-execute-20260327T172719Z.bak`
- compose file: `/home/edann/projects/eduassist-platform/infra/compose/compose.yaml`
- status url: `http://127.0.0.1:8002/v1/status`
- synced runtime artifacts: `framework-native-scorecard.json`
- live validation passed: `True`

## Requested Live Slices

- `protected`

## Live Validation Errors

- `(none)`

## Slice Changes

| Slice | Configured Before | Configured After | Rollout Before | Rollout After |
| --- | --- | --- | ---: | ---: |
| `protected` | `yes` | `yes` | `1%` | `100%` |

## Live Status Snapshot

```json
{
  "resolvedPrimaryStack": "langgraph",
  "experimentPrimaryEngine": "crewai",
  "experimentSlices": "protected,public,support,workflow",
  "experimentSliceRollouts": "protected:100,public:5,support:100,workflow:100",
  "experimentAllowlistSlices": "protected,support,workflow",
  "experimentLivePromotionSummary": {
    "resolved_primary_stack": "langgraph",
    "experiment_enabled": true,
    "experiment_active": true,
    "candidate_engine": "crewai",
    "pilot_configured": true,
    "pilot_ready": true,
    "pilot_status": {
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
    },
    "scorecard_loaded": true,
    "primary_stack_native_path_passed": true,
    "promotable_now": [
      "public"
    ],
    "maintain_now": [
      "protected",
      "support",
      "workflow"
    ],
    "blocked_now": {},
    "advisory_by_slice": {
      "protected": {
        "eligible": true,
        "configured": true,
        "live": true,
        "allowlist_only": true,
        "configured_rollout_percent": 100,
        "action": "maintain_controlled",
        "pilot_live_gate_ok": true,
        "pilot_live_gate_reason": "",
        "blocked_reasons": []
      },
      "public": {
        "eligible": true,
        "configured": true,
        "live": true,
        "allowlist_only": false,
        "configured_rollout_percent": 5,
        "action": "expand_gradually",
        "pilot_live_gate_ok": true,
        "pilot_live_gate_reason": "",
        "blocked_reasons": []
      },
      "support": {
        "eligible": true,
        "configured": true,
        "live": true,
        "allowlist_only": true,
        "configured_rollout_percent": 100,
        "action": "maintain_controlled",
        "pilot_live_gate_ok": true,
        "pilot_live_gate_reason": "",
        "blocked_reasons": []
      },
      "workflow": {
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
    }
  }
}
```

