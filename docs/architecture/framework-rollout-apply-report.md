# Framework Rollout Apply Report

Date: 2026-03-27T15:23:01.868102+00:00

## Goal

Record a rollout change that was preflighted before applying environment updates.

## Apply Result

- overall verdict: `approve`
- safe to apply: `True`
- applied: `True`
- env file: `artifacts/tmp-rollout.env`
- backup path: `/home/edann/projects/eduassist-platform/artifacts/env-snapshots/tmp-rollout-rollout-20260327T152301Z.bak`
- updated keys: `ORCHESTRATOR_EXPERIMENT_ALLOWLIST_SLICES, ORCHESTRATOR_EXPERIMENT_SLICES, ORCHESTRATOR_EXPERIMENT_SLICE_ROLLOUTS`

## Requested Live Slices

- `public`

## Slice Changes

| Slice | Configured Before | Configured After | Rollout Before | Rollout After |
| --- | --- | --- | ---: | ---: |
| `public` | `yes` | `yes` | `1%` | `2%` |

## Per Slice Verdict

| Slice | Decision | Action | Blocked Reasons |
| --- | --- | --- | --- |
| `public` | `approve` | `expand_gradually` |  |
| `protected` | `reject` | `blocked` | protected still trails LangGraph in operator-facing control primitives and should stay behind manual review. |
| `support` | `maintain` | `maintain_controlled` |  |
| `workflow` | `maintain` | `maintain_controlled` |  |
