# Framework Primary Stack Feature Flag Report

Date: 2026-03-27T14:19:46.998220+00:00

## Goal

Validate that `FEATURE_FLAG_PRIMARY_ORCHESTRATION_STACK=crewai` switches the primary path to CrewAI natively, without leaking LangGraph runtime metadata into the canonical trace.

## Results

| Case | Slice | Result | Notes |
| --- | --- | --- | --- |
| `crewai_primary_public_native_path` | `public` | passed | engine `crewai`, mode `crewai`, timeline `crewai_stage_task_path` |
| `crewai_primary_protected_native_path` | `protected` | passed | engine `crewai`, mode `crewai`, timeline `crewai_stage_task_path` |
| `crewai_primary_support_native_path` | `support` | passed | engine `crewai`, mode `crewai`, timeline `crewai_stage_task_path` |
| `crewai_primary_workflow_native_path` | `workflow` | passed | engine `crewai`, mode `crewai`, timeline `crewai_stage_task_path` |

## Summary

- passed `4/4` cases
- canonical traces stayed on `crewai` request metadata only for these primary-path runs
- `graph_path` and `suggested_replies` came from the CrewAI-native path under the feature flag

