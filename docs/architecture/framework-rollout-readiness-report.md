# Framework Rollout Readiness Report

Date: 2026-03-27T15:07:07.536679+00:00

## Goal

Summarize what can be promoted now, by slice, before any canary or feature-flag rollout change.

## Candidate Engine

- candidate engine: `crewai`
- scorecard loaded: `True`
- scorecard enforced: `False`
- pilot health enforced: `False`
- gate eligible: `True`
- primary-stack native path passed: `True`
- configured slices: `public, support, workflow`
- promotable now: `public, support, workflow`
- recommended next promotions: `(none)`

## Per Slice

| Slice | Eligible | Configured | Live | Rollout | Allowlist Only | Reason |
| --- | --- | --- | --- | ---: | --- | --- |
| `public` | `yes` | `yes` | `yes` | `1%` | `no` | public is allowed for crewai under the current scorecard gate. |
| `protected` | `no` | `no` | `no` | `0%` | `no` | protected still trails LangGraph in operator-facing control primitives and should stay behind manual review. |
| `support` | `yes` | `yes` | `yes` | `100%` | `yes` | support is allowed for crewai under the current scorecard gate. |
| `workflow` | `yes` | `yes` | `yes` | `100%` | `yes` | workflow is allowed for crewai under the current scorecard gate. |

## Gate Snapshot

```json
{
  "loaded": true,
  "generated_at": "2026-03-27T14:38:46.020428+00:00",
  "primary_engine": "crewai",
  "primary_score": 27,
  "primary_max_score": 30,
  "primary_stack_native_path_passed": true,
  "promotion_gate": {
    "eligible": true,
    "minimum_score_for_canary": 20,
    "primary_stack_native_path_required": true,
    "recommended_canary_slices": [
      "public",
      "support",
      "workflow"
    ],
    "blocked_canary_slices": [
      "protected"
    ],
    "slice_eligibility": {
      "public": {
        "eligible": true,
        "reason": "public is allowed for crewai under the current scorecard gate."
      },
      "protected": {
        "eligible": false,
        "reason": "protected still trails LangGraph in operator-facing control primitives and should stay behind manual review."
      },
      "support": {
        "eligible": true,
        "reason": "support is allowed for crewai under the current scorecard gate."
      },
      "workflow": {
        "eligible": true,
        "reason": "workflow is allowed for crewai under the current scorecard gate."
      }
    }
  },
  "frameworks": {
    "langgraph": {
      "total_score": 29,
      "max_score": 30,
      "primary_stack_native_path_passed": true,
      "restart_recovery_passed": true,
      "crash_recovery_passed": true,
      "recommended_canary_slices": [
        "public",
        "protected",
        "support",
        "workflow"
      ],
      "blocked_canary_slices": [],
      "trace_sample": {
        "thread_id": "conversation:scorecard-topline-langgraph-1",
        "created_at": "2026-03-27T13:38:23.699812+00:00",
        "next_nodes": [],
        "task_names": [],
        "hitl_status": null,
        "state_route": "structured_tool",
        "checkpoint_id": "1f129e23-9f67-6ae0-8005-890a0437d5c8",
        "state_available": true,
        "state_slice_name": "public",
        "snapshot_metadata": {
          "step": 5,
          "source": "loop"
        },
        "checkpointer_backend": "postgres",
        "checkpointer_enabled": true,
        "task_interrupt_count": 0,
        "has_pending_interrupt": false,
        "top_level_interrupt_count": 0
      }
    },
    "crewai": {
      "total_score": 27,
      "max_score": 30,
      "primary_stack_native_path_passed": true,
      "restart_recovery_passed": true,
      "crash_recovery_passed": true,
      "trace_sample": {
        "request": {
          "slice_name": "support",
          "flow_enabled": true,
          "flow_state_id": "2cc869d9-85cf-405a-a336-d4ea317ea22f",
          "validation_stack": [
            "flow_router",
            "deterministic_support"
          ]
        },
        "response": {
          "latency_ms": 60.7
        }
      },
      "recommended_canary_slices": [
        "public",
        "support",
        "workflow"
      ],
      "blocked_canary_slices": [
        "protected"
      ],
      "blocked_reasons": {
        "protected": "protected still trails LangGraph in operator-facing control primitives and should stay behind manual review."
      }
    }
  }
}
```
