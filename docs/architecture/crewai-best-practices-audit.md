# CrewAI Best-Practices Audit

Date: 2026-03-26

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
- event-listener telemetry in the public and protected pilots
- real CrewAI `Flow` wrappers for `public` and `protected`, with typed state and explicit routing labels
- deterministic validation stack:
  - Pydantic output validation
  - judge step
  - deterministic backstop for critical factual answers
- slice-specific pilots instead of one oversized general-purpose crew

## What We Intentionally Did Not Force

### Task-level guardrails inside CrewAI

We tested CrewAI task guardrails directly in this pilot, but in `crewai==1.12.2` they proved brittle for our public slice because validation did not receive the full evidence context needed to check source-bound constraints reliably.

For this project, the more reliable stack is:

- `output_pydantic`
- judge task
- deterministic backstop
- runtime-level safety checks

This is a pragmatic deviation from the idealized example usage, but it is the safer choice for this codebase and version.

### Flow wrapper around every slice

CrewAI `Flow` is now in place for the slices that benefit most from stateful semantic routing:

- `public`
- `protected`

We still intentionally do not force `Flow` into every slice.

For the current comparison phase, the remaining simpler shape is intentional:

- public/protected use real flows plus real crews
- support/workflow stay narrower and more deterministic
- stateful experimentation is handled first in the main orchestrator

That keeps the comparison fair and limits production risk.

## Remaining Gap To Reach Fullest CrewAI Usage

If we decide to promote CrewAI beyond canary, the next architectural upgrades should be:

1. Expand `Flow` deeper into multi-turn follow-up handling for `support` and parts of `workflow`.
2. Move more conversation-affinity and state transitions closer to the CrewAI side.
3. Expand event-listener telemetry into a more complete per-task trace schema.
4. Revisit CrewAI-native guardrails only if evidence-aware validation becomes stable in the selected version.

## Final Assessment

The current implementation is aligned with modern CrewAI practice in the places where CrewAI is genuinely adding value:

- structured semantic planning
- grounded composition
- output judging
- event telemetry

And it deliberately keeps deterministic rails where this product still needs stronger operational control:

- support handoff
- workflow protocols
- factual safety backstops

That tradeoff is appropriate for a production comparison phase.
