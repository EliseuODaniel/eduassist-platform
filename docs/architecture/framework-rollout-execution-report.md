# Framework Rollout Execution Report

Date: 2026-03-27T16:01:18.883395+00:00

## Goal

Record a full rollout operation: preflight, apply to env, service restart, and live status validation.

## Execution Summary

- preflight verdict: `approve`
- preflight safe_to_apply: `True`
- restart attempted: `True`
- services restarted: `ai-orchestrator`
- env file: `.env`
- backup path: `/home/edann/projects/eduassist-platform/artifacts/env-snapshots/.env-execute-20260327T160057Z.bak`
- compose file: `/home/edann/projects/eduassist-platform/infra/compose/compose.yaml`
- status url: `http://127.0.0.1:8002/v1/status`
- live validation passed: `False`

## Requested Live Slices

- `public`

## Live Validation Errors

- experimentLivePromotionSummary missing from live status

## Slice Changes

| Slice | Configured Before | Configured After | Rollout Before | Rollout After |
| --- | --- | --- | ---: | ---: |
| `public` | `yes` | `yes` | `1%` | `2%` |

## Live Status Snapshot

```json
{
  "resolvedPrimaryStack": "langgraph",
  "experimentPrimaryEngine": "crewai",
  "experimentSlices": "public,support,workflow",
  "experimentSliceRollouts": "public:2,support:100,workflow:100",
  "experimentAllowlistSlices": "support,workflow",
  "experimentLivePromotionSummary": null
}
```

