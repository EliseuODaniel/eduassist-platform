# CrewAI Best-Practices Audit

Date: 2026-03-27

## Sources Reviewed

- CrewAI Flows: https://docs.crewai.com/en/concepts/flows
- CrewAI Tasks: https://docs.crewai.com/en/concepts/tasks
- CrewAI Agents: https://docs.crewai.com/en/concepts/agents
- CrewAI Event Listeners: https://docs.crewai.com/en/concepts/event-listener
- AWS guidance on CrewAI: https://docs.aws.amazon.com/prescriptive-guidance/latest/agentic-ai-frameworks/crewai.html

## Practical Conclusion

The current pilot is using CrewAI in a way that is strong enough for a fair production-style comparison, but not every slice should be forced into a fully free-form multi-agent shape.

The best-fit pattern for this product is:

- isolated CrewAI service
- narrow slice-specific pilots
- small `planner -> composer -> judge` crews where semantic composition adds value
- deterministic control-plane behavior for support and workflow handoffs
- structured outputs, external validation, and strong backstops

That is closer to current best practice than trying to turn every request into a large, fully autonomous crew.

## What Is Aligned Today

- isolated dependency boundary for CrewAI in `ai-orchestrator-crewai`
- bounded crews with explicit roles
- structured task outputs via `output_pydantic`
- native task guardrails in the `public` and `protected` flows
- event-listener telemetry in the public and protected pilots
- stable per-task event telemetry surfaced back in `event_summary` and `task_trace`
- real CrewAI `Flow` wrappers for all comparison slices, with typed state and explicit routing labels
- persisted `Flow` state for `public`, `protected`, `support`, and `workflow` using `SQLiteFlowPersistence`
- deterministic validation stack:
  - Pydantic output validation
  - task guardrails where evidence-aware validation is stable
  - judge step
  - deterministic backstop for critical factual answers
- slice-specific pilots instead of one oversized general-purpose crew
- agentic rendering on top of deterministic support/workflow operations when the LLM path is available

## What We Intentionally Did Not Force

### Free-form agentic execution on every slice

We still intentionally do not force every slice into the same degree of free-form multi-agent behavior.

That is aligned with the CrewAI production guidance for this product shape:

- `public` and `protected` now use real `Flow` state, `planner -> composer -> judge`, `output_pydantic`, and native task guardrails.
- `support` and `workflow` now also use real `Flow`, but the operational side effects remain deterministic first, with an optional native agentic rendering/judge layer on top.
- this keeps rollback safety and auditability strong where side effects matter most.

### Flow wrapper around every slice

CrewAI `Flow` is now in place across all comparison slices:

- `public`
- `protected`
- `support`
- `workflow`

For the current comparison phase, the remaining simpler shape is intentional:

- public/protected use real flows plus real crews plus native task guardrails
- support/workflow use real flows with deterministic control-plane handlers and an agentic renderer/judge layer
- stateful persistence is active in all four slices
- support/workflow still rely more heavily on the main orchestrator for broader conversation affinity
- interactive tracing prompts are suppressed in service mode
- in the current local environment, `llmConfigured=false`, so the live validations mainly exercised deterministic fast paths even though the native agentic layer is already implemented

That keeps the comparison fair and limits production risk.

## Remaining Gap To Reach Fullest CrewAI Usage

If we decide to promote CrewAI beyond canary, the next architectural upgrades should be:

1. Expand persisted multi-turn follow-up memory deeper into `support` and `workflow` state.
2. Move more conversation-affinity and state transitions closer to the CrewAI side, instead of depending on outer runtime shims.
3. Exercise the native task guardrails and agentic renderer under a live configured LLM in the same environment used for rollout decisions.
4. Keep `protected` live rollout tied to the explicit user-traffic HITL gate, so parity on replay never bypasses operator-review policy in the pilot runtime.

## Final Assessment

The current implementation is aligned with modern CrewAI practice in the places where CrewAI is genuinely adding value:

- structured semantic planning
- grounded composition
- output judging
- native task guardrails in the evidence-heavy slices
- event telemetry
- surfaced task-level timing and agent/crew traces
- flow-owned state persistence in all comparison slices

And it deliberately keeps deterministic rails where this product still needs stronger operational control:

- support handoff
- workflow protocols
- factual safety backstops

That tradeoff is appropriate for a production comparison phase.
