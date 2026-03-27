# Framework Rollout Preflight Report

Date: 2026-03-27T17:25:42.754133+00:00

## Goal

Validate a proposed canary rollout change before applying environment or rollout updates.

## Verdict

- overall verdict: `approve`
- safe to apply: `True`
- requested live slices: `protected`
- candidate engine: `crewai`
- proposed telegram chat allowlist count: `0`
- proposed conversation allowlist count: `1`
- proposed CrewAI protected user-traffic HITL: `True`
- proposed CrewAI HITL slices: `protected`

## Proposed Changes

| Slice | Configured Before | Configured After | Rollout Before | Rollout After |
| --- | --- | --- | ---: | ---: |
| `protected` | `no` | `yes` | `0%` | `1%` |

## Proposed Slice Decisions

| Slice | Decision | Action | Blocked Reasons |
| --- | --- | --- | --- |
| `public` | `approve` | `expand_gradually` |  |
| `protected` | `maintain` | `maintain_controlled` |  |
| `support` | `maintain` | `maintain_controlled` |  |
| `workflow` | `maintain` | `maintain_controlled` |  |

## Current Live Summary

- promotable now: `public`
- maintain now: `support, workflow`

## Proposed Live Summary

- promotable now: `public`
- maintain now: `protected, support, workflow`

