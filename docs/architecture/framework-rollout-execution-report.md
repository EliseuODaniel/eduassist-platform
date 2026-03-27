# Framework Rollout Execution Report

Date: 2026-03-27T16:12:28.577072+00:00

## Goal

Record a full rollout operation: preflight, apply to env, service restart, and live status validation.

## Execution Summary

- preflight verdict: `approve`
- preflight safe_to_apply: `True`
- restart attempted: `True`
- services restarted: `ai-orchestrator`
- env file: `.env`
- backup path: `/home/edann/projects/eduassist-platform/artifacts/env-snapshots/.env-execute-20260327T161200Z.bak`
- compose file: `/home/edann/projects/eduassist-platform/infra/compose/compose.yaml`
- status url: `http://127.0.0.1:8002/v1/status`
- synced runtime artifacts: `framework-native-scorecard.json`
- live validation passed: `True`

## Requested Live Slices

- `public`

## Live Validation Errors

- `(none)`

## Slice Changes

| Slice | Configured Before | Configured After | Rollout Before | Rollout After |
| --- | --- | --- | ---: | ---: |
| `public` | `yes` | `yes` | `2%` | `5%` |

## Live Status Snapshot

```json
{
  "resolvedPrimaryStack": "langgraph",
  "experimentPrimaryEngine": "crewai",
  "experimentSlices": "public,support,workflow",
  "experimentSliceRollouts": "public:5,support:100,workflow:100",
  "experimentAllowlistSlices": "support,workflow",
  "experimentLivePromotionSummary": {
    "resolved_primary_stack": "langgraph",
    "experiment_enabled": true,
    "experiment_active": true,
    "candidate_engine": "crewai",
    "pilot_configured": true,
    "pilot_ready": true,
    "scorecard_loaded": true,
    "primary_stack_native_path_passed": true,
    "promotable_now": [
      "public"
    ],
    "maintain_now": [
      "support",
      "workflow"
    ],
    "blocked_now": {
      "protected": "protected still trails LangGraph in operator-facing control primitives and should stay behind manual review."
    },
    "advisory_by_slice": {
      "protected": {
        "eligible": false,
        "configured": false,
        "live": false,
        "allowlist_only": false,
        "configured_rollout_percent": 0,
        "action": "blocked",
        "blocked_reasons": [
          "protected still trails LangGraph in operator-facing control primitives and should stay behind manual review."
        ]
      },
      "public": {
        "eligible": true,
        "configured": true,
        "live": true,
        "allowlist_only": false,
        "configured_rollout_percent": 5,
        "action": "expand_gradually",
        "blocked_reasons": []
      },
      "support": {
        "eligible": true,
        "configured": true,
        "live": true,
        "allowlist_only": true,
        "configured_rollout_percent": 100,
        "action": "maintain_controlled",
        "blocked_reasons": []
      },
      "workflow": {
        "eligible": true,
        "configured": true,
        "live": true,
        "allowlist_only": true,
        "configured_rollout_percent": 100,
        "action": "maintain_controlled",
        "blocked_reasons": []
      }
    }
  }
}
```

