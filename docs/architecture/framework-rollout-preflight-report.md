# Framework Rollout Preflight Report

Date: 2026-03-27T15:37:32.984742+00:00

## Goal

Validate a proposed canary rollout change before applying environment or rollout updates.

## Verdict

- overall verdict: `approve`
- safe to apply: `True`
- requested live slices: `public`
- candidate engine: `crewai`

## Proposed Changes

| Slice | Configured Before | Configured After | Rollout Before | Rollout After |
| --- | --- | --- | ---: | ---: |
| `public` | `yes` | `yes` | `1%` | `2%` |

## Proposed Slice Decisions

| Slice | Decision | Action | Blocked Reasons |
| --- | --- | --- | --- |
| `public` | `approve` | `expand_gradually` |  |
| `protected` | `reject` | `blocked` | protected still trails LangGraph in operator-facing control primitives and should stay behind manual review. |
| `support` | `maintain` | `maintain_controlled` |  |
| `workflow` | `maintain` | `maintain_controlled` |  |

## Current Live Summary

- promotable now: `public`
- maintain now: `support, workflow`

## Proposed Live Summary

- promotable now: `public`
- maintain now: `support, workflow`

