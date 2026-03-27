# Framework Native Scorecard

Date: 2026-03-27T13:56:19.007818+00:00

## Goal

Score the two orchestration stacks on framework-native durability and debug capabilities, not only answer quality.

## Evidence Used

- [framework-restart-recovery-report.md](/home/edann/projects/eduassist-platform/docs/architecture/framework-restart-recovery-report.md)
- [framework-crash-recovery-report.md](/home/edann/projects/eduassist-platform/docs/architecture/framework-crash-recovery-report.md)
- live `orchestration.trace` samples for one `LangGraph` path and one `CrewAI` path

## Totals

- `LangGraph`: `24/25`
- `CrewAI`: `22/25`

## LangGraph

| Capability | Score | Evidence |
| --- | ---: | --- |
| Checkpointed persistence | `5/5` | Live `orchestration.trace` carries `thread_id`, `checkpoint_id`, `state_available=true`, and `checkpointer_backend=postgres`. |
| HITL durability after restart | `5/5` | Validated by [framework-restart-recovery-report.md](/home/edann/projects/eduassist-platform/docs/architecture/framework-restart-recovery-report.md). |
| HITL durability after crash | `5/5` | Validated by [framework-crash-recovery-report.md](/home/edann/projects/eduassist-platform/docs/architecture/framework-crash-recovery-report.md). |
| Native graph introspection | `5/5` | Trace already exposes `checkpoint_id`, `state_route`, interrupt counts, and snapshot metadata. |
| Operator debug ergonomics | `4/5` | Internal review/state/resume endpoints plus checkpoint-backed thread inspection are already live. |

## CrewAI

| Capability | Score | Evidence |
| --- | ---: | --- |
| Flow persistence | `5/5` | Live `orchestration.trace` carries `flow_enabled=true` and `flow_state_id` for the CrewAI path. |
| Restart continuity | `5/5` | Validated by [framework-restart-recovery-report.md](/home/edann/projects/eduassist-platform/docs/architecture/framework-restart-recovery-report.md). |
| Crash continuity | `5/5` | Validated by [framework-crash-recovery-report.md](/home/edann/projects/eduassist-platform/docs/architecture/framework-crash-recovery-report.md). |
| Task/flow trace richness | `4/5` | Canonical trace now exposes normalized CrewAI request/response metadata, and agentic paths emit `event_summary`/`task_trace` in pilot metadata. |
| Operator debug ergonomics | `3/5` | Good flow-state visibility, but no CrewAI-native HITL equivalent and some deterministic slices still expose thinner traces than agentic ones. |

## Readout

Current inference from the evidence:

- `LangGraph` leads in native persistence + HITL + checkpoint/state introspection with a score of `24/25`.
- `CrewAI` is now strong on Flow continuity and good on canonical trace visibility, with `22/25`, but still trails in operator-facing control primitives.
- The comparison is now top-line enough for durability/debug to be a real architectural differentiator, not just a qualitative impression.

## Trace Samples

### LangGraph

```json
{
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
```

### CrewAI

```json
{
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
}
```
