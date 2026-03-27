# Framework Top-Line Roadmap

Date: 2026-03-27

## Goal

Raise both orchestration stacks toward a more top-line implementation of their own framework best practices while preserving fair comparison conditions.

This roadmap distinguishes:

- fair product comparison
- maximum framework-native usage
- pragmatic rollout safety for this codebase

## Evidence Base

Current local evidence:

- [two-stack-shadow-master-real-threads-report.md](/home/edann/projects/eduassist-platform/docs/architecture/two-stack-shadow-master-real-threads-report.md)
- [crewai-best-practices-audit.md](/home/edann/projects/eduassist-platform/docs/architecture/crewai-best-practices-audit.md)
- [graph.py](/home/edann/projects/eduassist-platform/apps/ai-orchestrator/src/ai_orchestrator/graph.py)
- [public_flow.py](/home/edann/projects/eduassist-platform/apps/ai-orchestrator-crewai/src/ai_orchestrator_crewai/public_flow.py)
- [protected_flow.py](/home/edann/projects/eduassist-platform/apps/ai-orchestrator-crewai/src/ai_orchestrator_crewai/protected_flow.py)

Official guidance reviewed:

- LangGraph overview: https://docs.langchain.com/oss/python/langgraph
- LangGraph persistence: https://docs.langchain.com/oss/python/langgraph/persistence
- LangGraph durable execution: https://docs.langchain.com/oss/python/langgraph/durable-execution
- LangGraph human-in-the-loop: https://docs.langchain.com/oss/python/langgraph/human-in-the-loop
- LangGraph subgraphs: https://docs.langchain.com/oss/python/langgraph/use-subgraphs
- CrewAI flows: https://docs.crewai.com/en/concepts/flows
- CrewAI tasks: https://docs.crewai.com/en/concepts/tasks
- CrewAI event listeners: https://docs.crewai.com/en/concepts/event-listener
- CrewAI production architecture: https://docs.crewai.com/en/concepts/production-architecture

## Current Assessment

### LangGraph

What is strong today:

- explicit `StateGraph`
- deterministic routing and safety rails
- production-hardened runtime around auth, tools, traces, and canary selection
- native `thread_id` mapping tied to conversation identity
- Postgres-backed LangGraph checkpointer runtime, already validated in the local environment

Main gap versus top-line LangGraph usage:

- support-slice HITL now exists natively with `interrupt()` / `Command`, but is exposed through internal review endpoints only and not yet promoted into normal user traffic
- no checkpoint id / node-path metadata bridged into the existing trace surface yet
- no LangGraph-native durable execution story beyond checkpointed state recovery

### CrewAI

What is strong today:

- isolated service boundary
- `Flow` in all comparison slices
- typed state
- `planner -> composer -> judge`
- `output_pydantic`
- event listeners
- persisted `Flow` state in `public` and `protected`

Main gap versus top-line CrewAI usage:

- guardrails rely more on judge plus deterministic backstop than on stable CrewAI-native task guardrails
- support/workflow still lean heavily on deterministic handlers
- support/workflow do not persist their `Flow` state yet
- conversation affinity and longer-lived state still live partly outside the CrewAI side
- service logs still include CrewAI Flow console panels even though the interactive trace prompt is now suppressed

## Progress Snapshot

Validated in this round:

- LangGraph now runs with a native Postgres-backed checkpointer and stable `thread_id` mapping.
- LangGraph now exposes a native HITL review path for the `support` slice through internal review/state/resume endpoints backed by the checkpointer.
- LangGraph checkpointer serialization warnings are now isolated as a remaining version-specific follow-up item; the safe runtime path stays enabled, but the msgpack allowlist is not yet fully solved in this stack version.
- CrewAI now persists `Flow` state for `public` and `protected` through SQLite.
- LangGraph now delegates through slice subgraphs for `public`, `protected`, and `support`.
- CrewAI now emits per-task event telemetry with task, agent, crew, and timing summaries on agentic paths.
- CrewAI no longer blocks on the interactive tracing prompt during service requests.

Concrete local evidence:

- `GET /v1/status` on the main orchestrator reports:
  - `langgraphCheckpointerReady = true`
  - `langgraphCheckpointerBackend = postgres`
  - `langgraphThreadIdEnabled = true`
- `langgraph_checkpoint.checkpoints` already contains checkpoints for `conversation:topline-public-1`
- `GET /v1/internal/hitl/review` can pause a `support` handoff, and `GET /v1/internal/hitl/state` plus `POST /v1/internal/hitl/resume` can inspect and continue the paused thread
- `/workspace/artifacts/crewai-flow-state/public.sqlite3` and `protected.sqlite3` exist in the CrewAI pilot container
- both CrewAI SQLite databases already contain persisted `flow_states`
- public graph paths now include `select_slice -> public_slice`
- protected graph paths now include `select_slice -> protected_slice`
- support graph paths now include `select_slice -> support_slice`
- `event_summary` and `task_trace` now appear in agentic CrewAI responses for `public` and `protected`

## Upgrade Principles

1. Keep safety and authorization deterministic.
2. Improve each framework using its native strengths, not by forcing symmetry where it hurts product quality.
3. Preserve one shared evaluation surface:
   - same tools
   - same datasets
   - same auth rules
   - same trace schema
4. Upgrade in phases so we can compare after every step.

## Phase 1: LangGraph To Strong Native Production Shape

### 1. Add a real checkpointer

Target:

- introduce `AsyncPostgresSaver` or another durable checkpointer for the orchestrator graph
- execute the graph with `thread_id` bound to conversation identity

Why:

- aligns with LangGraph persistence and durable execution guidance
- enables native checkpoint recovery and state inspection

Success criteria:

- graph state can be resumed by thread
- checkpoints survive process restarts
- traces can correlate app conversation id with LangGraph thread id

Status:

- implemented in this round

### 2. Add human-in-the-loop using `interrupt()` for sensitive slices

Target slices:

- `support`
- selected `protected` actions

Why:

- LangGraph explicitly treats HITL as a first-class pattern built on persistence
- improves the fidelity of framework-native comparison

Success criteria:

- selected tool/action approvals pause the graph
- operators can resume with `Command`
- app can observe and render pending interrupt state

Status:

- implemented in this round for the `support` slice via internal review/state/resume endpoints

### 3. Split the large graph into subgraphs by slice

Suggested subgraphs:

- `public`
- `protected`
- `workflow`
- `support`

Why:

- closer to LangGraph modular best practice
- easier state isolation
- easier per-slice checkpoint and replay inspection

Success criteria:

- parent router delegates to named subgraphs
- per-slice state inspection is simpler
- no regression in current benchmark suite

Status:

- implemented in this round

### 4. Add native graph-state observability

Target:

- persist graph state metadata and checkpoint ids into the existing trace bridge

Why:

- makes LangGraph comparison about the graph runtime itself, not only the outer app

Success criteria:

- each run stores thread id, checkpoint id, node path, and terminal node

Status:

- implemented in best-effort mode in this round:
  - `orchestration.trace` now carries `langgraph.thread_id`, checkpointer backend, and graph-state fetch results
  - when snapshot inspection works, the trace can carry native state metadata
  - when checkpoint deserialization fails, the trace records the failure without breaking the user response path

## Phase 2: CrewAI To Strong Native Production Shape

### 1. Persist Flow state for public and protected

Target:

- persist state where multi-turn continuity matters most

Why:

- aligns with CrewAI Flow-first production guidance
- reduces dependence on external affinity hacks

Success criteria:

- public/protected follow-ups can recover flow state across restarts
- replay can confirm stable state continuation

Status:

- implemented in this round

### 2. Move more conversation affinity into Flow state

Target fields:

- active slice context
- active student
- pending clarification
- last resolved attribute
- last support/workflow protocol where relevant

Why:

- brings the pilot closer to true Flow-owned orchestration

Success criteria:

- fewer external state shims in the orchestrator bridge
- improved follow-up behavior without extra deterministic patches

### 3. Re-evaluate CrewAI-native guardrails in a narrow slice

Target:

- retry task guardrails only on one low-risk factual public slice

Why:

- current version showed brittleness
- still worth retesting in a tightly scoped context for top-line adoption

Success criteria:

- guardrail catches a meaningful class of errors without evidence loss
- no reliability drop compared with judge plus backstop

### 4. Expand event-listener telemetry into a stable per-task trace contract

Target:

- record task timing, retry counts, validation outcomes, and tool/evidence references

Why:

- aligns with CrewAI event-bus strengths
- makes CrewAI debugging more first-class

Success criteria:

- task-level replay artifacts can be compared with LangGraph node-level traces

Status:

- implemented in this round for agentic `public` and `protected` paths

## Phase 3: Make The Comparison Top-Line, Not Only Fair

### 1. Add a framework-native capability scorecard

Measure separately from response quality:

- persistence depth
- native HITL support
- state introspection
- recovery after crash
- task/node trace richness
- per-slice modularity

### 2. Add failure-mode benchmarks

New benchmark classes:

- restart mid-thread
- recovery after process crash
- approval-required handoff
- long follow-up chain with topic switch
- multi-turn ambiguity with explicit repair

### 3. Run live canaries with framework-specific telemetry

Keep response evaluation common, but also compare:

- LangGraph checkpoint behavior
- CrewAI Flow persistence behavior
- operator debugging ergonomics

## Recommended Execution Order

1. LangGraph subgraphs by slice
2. CrewAI richer per-task telemetry
3. LangGraph HITL for sensitive operations
4. Narrow CrewAI-native guardrail re-test
5. Framework-native scorecard and failure-mode benchmarks

Completed already:

- LangGraph checkpointer + thread ids
- CrewAI persisted Flow state for `public` and `protected`

## Why This Order

- it raises both stacks in ways that are native to each framework
- it preserves today’s fair benchmark surface
- it avoids prematurely opening risky canaries on `protected`

## Practical Outcome We Want

At the end of this roadmap, the answer to:

- “is the product comparison fair?” should be yes
- “is each framework being used near its own modern best practice?” should also be much closer to yes

Without that, we are only comparing two application shapes. With it, we are comparing two framework-native orchestration strategies under the same product constraints.
