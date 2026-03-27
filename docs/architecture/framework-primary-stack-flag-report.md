# Framework Primary Stack Feature Flag Report

Date: 2026-03-27T14:24:14.849999+00:00

## Goal

Validate that `FEATURE_FLAG_PRIMARY_ORCHESTRATION_STACK` can switch the primary path to either framework natively, without leaking the alternate runtime metadata into the canonical trace.

## Results

| Case | Primary | Slice | Result | Notes |
| --- | --- | --- | --- | --- |
| `crewai_primary_public_native_path` | `crewai` | `public` | passed | engine `crewai`, mode `crewai`, timeline `crewai_stage_task_path` |
| `crewai_primary_protected_native_path` | `crewai` | `protected` | passed | engine `crewai`, mode `crewai`, timeline `crewai_stage_task_path` |
| `crewai_primary_support_native_path` | `crewai` | `support` | passed | engine `crewai`, mode `crewai`, timeline `crewai_stage_task_path` |
| `crewai_primary_workflow_native_path` | `crewai` | `workflow` | passed | engine `crewai`, mode `crewai`, timeline `crewai_stage_task_path` |
| `langgraph_primary_public_native_path` | `langgraph` | `public` | passed | engine `langgraph`, mode `langgraph`, timeline `langgraph_node_path` |
| `langgraph_primary_protected_native_path` | `langgraph` | `protected` | passed | engine `langgraph`, mode `langgraph`, timeline `langgraph_node_path` |
| `langgraph_primary_support_native_path` | `langgraph` | `support` | passed | engine `langgraph`, mode `langgraph`, timeline `langgraph_node_path` |
| `langgraph_primary_workflow_native_path` | `langgraph` | `workflow` | passed | engine `langgraph`, mode `langgraph`, timeline `langgraph_node_path` |

## Summary

- passed `8/8` cases
- `crewai` passed `4/4` native-path cases
- `langgraph` passed `4/4` native-path cases
- canonical traces stayed on the selected framework metadata only for these primary-path runs
- `graph_path` and response shaping stayed native to the selected framework under the feature flag

