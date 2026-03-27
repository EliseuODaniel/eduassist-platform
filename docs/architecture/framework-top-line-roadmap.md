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
- [framework-primary-stack-flag-report.md](/home/edann/projects/eduassist-platform/docs/architecture/framework-primary-stack-flag-report.md)
- [framework-restart-recovery-report.md](/home/edann/projects/eduassist-platform/docs/architecture/framework-restart-recovery-report.md)
- [framework-crash-recovery-report.md](/home/edann/projects/eduassist-platform/docs/architecture/framework-crash-recovery-report.md)
- [framework-native-scorecard.md](/home/edann/projects/eduassist-platform/docs/architecture/framework-native-scorecard.md)
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

- the hardest remaining gap is not core framework usage anymore, but expanding native operator workflows beyond the currently validated low-risk slices
- no broader durable execution story yet beyond checkpoint-backed recovery plus HITL review/resume

### CrewAI

What is strong today:

- isolated service boundary
- `Flow` in all comparison slices
- typed state
- `planner -> composer -> judge`
- `output_pydantic`
- event listeners
- persisted `Flow` state in `public`, `protected`, `support`, and `workflow`

Main gap versus top-line CrewAI usage:

- support/workflow still lean heavily on deterministic handlers for side-effect safety
- conversation affinity and longer-lived state still live partly outside the CrewAI side
- the current local environment is not exercising the LLM-backed agentic path live because `llmConfigured=false`
- protected live rollout on the CrewAI side should stay behind the explicit user-traffic HITL gate until `CREWAI_HITL_USER_TRAFFIC_ENABLED=true` is intentionally enabled in the pilot

## Progress Snapshot

Validated in this round:

- LangGraph now runs with a native Postgres-backed checkpointer and stable `thread_id` mapping.
- LangGraph now exposes native HITL review paths for the `support` slice and for low-risk `protected` reads through internal review/state/resume endpoints backed by the checkpointer.
- LangGraph now also supports HITL on normal user-traffic execution paths when the feature flag is enabled, returning a safe pending-review response while persisting the interruptible thread state.
- LangGraph checkpointer serializer compatibility is now fixed for the current typed checkpoint payloads; native snapshot reads are working again through the Postgres checkpointer.
- LangGraph runtime no longer tries to bootstrap the checkpoint schema on startup; schema ownership stays in the database init/migration layer, which removes a recurring privilege warning from service logs.
- CrewAI now persists `Flow` state for `public`, `protected`, `support`, and `workflow` through SQLite.
- CrewAI now uses native task guardrails in the `public` and `protected` flows.
- CrewAI now exposes native async human-feedback review for low-risk `protected` reads, with pending-state inspection plus approve/reject resume on the same persisted `flow_state_id`.
- CrewAI now wraps `support` and `workflow` deterministic operations in an optional native agentic rendering/judge layer, preserving a deterministic factual backstop.
- LangGraph now delegates through slice subgraphs for `public`, `protected`, and `support`.
- CrewAI now emits per-task event telemetry with task, agent, crew, and timing summaries on agentic paths.
- CrewAI no longer blocks on the interactive tracing prompt during service requests.
- CrewAI pilot metadata now bridges into the main orchestrator trace surface, so `orchestration.trace` and `orchestration.shadow` can carry normalized `crewai` request/response telemetry when that engine is exercised.
- Restart/recovery durability is now benchmarked with a versioned dataset and report, and the current run passed `5/5` cases across LangGraph protected HITL plus CrewAI public/protected/support/workflow Flow continuity.
- Crash/recovery durability is now benchmarked separately with hard `kill/start`, and the current run also passed `5/5`.
- Canonical traces now expose normalized per-run timelines for both frameworks:
  - LangGraph via `langgraph.timeline`
  - CrewAI via `crewai.timeline`
- A framework-native durability/debug scorecard now exists in both docs and a runtime-readable artifact, so canary promotion can be gated by scorecard plus pilot health instead of only static config.
- The primary-stack feature flag now has a versioned regression benchmark that verifies both `CrewAI` and `LangGraph` can run as the real primary path, with native trace metadata and without leaking alternate-runtime fields.
- The scorecard and canary gate can now incorporate that primary-stack native-path benchmark as an explicit promotion requirement, instead of relying only on total durability/debug score.
- Runtime status surfaces can now expose the resolved scorecard gate, including per-slice eligibility and blocking reasons, so promotion state is inspectable without opening the raw JSON artifact.
- A rollout-readiness summary can now be derived from the same gate, making “what can be promoted now” explicit before any canary or feature-flag change.
- A live promotion summary can now combine that gate with current pilot health and rollout config, so “maintain, start, expand, or block” is explicit per slice before a production change.
- A rollout preflight can now simulate a proposed env change before applying it, turning promotion into an explicit approve/reject step instead of a manual read of multiple reports.
- A rollout apply routine can now sit behind that preflight, so env mutation happens only through an auditable gate with backup and snapshot output.
- A rollout execution routine can now extend that apply step into service restart and live status validation, closing the loop from proposal to verified runtime state.
- A single-command slice wrapper can now sit on top of preflight and execution, removing manual rollout-string editing and creating an operational changelog by default.
- The slice wrapper can now require an explicit human reason/operator, raising the audit quality of every promotion attempt instead of logging anonymous rollout changes.
- A symmetric rollback wrapper can now reuse the same audited promotion path, so rollback is no longer a manual special case.
- A release snapshot can now consolidate git state, live runtime state, service health, and rollout history into one final operational checkpoint before merge or broader rollout.
- The rollout changelog can now be normalized against the current audit contract, so legacy entries no longer weaken merge/release readiness.
- A merge/release checklist can now verify snapshot freshness, health, scorecard gates, and changelog hygiene in one pass before promotion or merge.
- A recommendation wrapper can now promote the next slice suggested by the live gate using the same audited rollout path, reducing operator guesswork while preserving the existing controls.
- The rollout execution path can now resync runtime scorecard artifacts after restart and wait for full validated status, avoiding false-negative live checks caused by boot-time partial status surfaces.
- A post-rollout live observation report can now confirm the real runtime posture after promotion before the next expansion.
- A merge-preparation report can now turn the final handoff into an explicit gate against the target branch, instead of relying only on ad-hoc Git inspection.

Concrete local evidence:

- `GET /v1/status` on the main orchestrator reports:
  - `langgraphCheckpointerReady = true`
  - `langgraphCheckpointerBackend = postgres`
  - `langgraphThreadIdEnabled = true`
- `langgraph_checkpoint.checkpoints` already contains checkpoints for `conversation:topline-public-1`
- `GET /v1/internal/hitl/review` can pause a `support` handoff, and `GET /v1/internal/hitl/state` plus `POST /v1/internal/hitl/resume` can inspect and continue the paused thread
- `/workspace/artifacts/crewai-flow-state/public.sqlite3`, `protected.sqlite3`, `support.sqlite3`, and `workflow.sqlite3` exist in the CrewAI pilot container
- all four CrewAI SQLite databases already contain persisted `flow_states`
- public graph paths now include `select_slice -> public_slice`
- protected graph paths now include `select_slice -> protected_slice`
- support graph paths now include `select_slice -> support_slice`
- workflow graph paths now include `select_slice -> workflow_slice`
- `event_summary` and `task_trace` now appear in agentic CrewAI responses for `public` and `protected`
- both frameworks now persist normalized trace timelines for direct comparison:
  - `response_payload.langgraph.timeline_kind = langgraph_node_path`
  - `response_payload.crewai.timeline_kind = crewai_stage_task_path`
- the latest [framework-langgraph-user-traffic-hitl-report.md](/home/edann/projects/eduassist-platform/docs/architecture/framework-langgraph-user-traffic-hitl-report.md) validates that both `support` and low-risk `protected` requests can enter native LangGraph user-traffic HITL, persist the pending interrupt, and resume safely.
- the latest [framework-crewai-protected-hitl-report.md](/home/edann/projects/eduassist-platform/docs/architecture/framework-crewai-protected-hitl-report.md) validates that `CrewAI` can persist a protected review, inspect the pending state, and resume the same flow on both approval and rejection.
- the latest [framework-restart-recovery-report.md](/home/edann/projects/eduassist-platform/docs/architecture/framework-restart-recovery-report.md) shows:
  - LangGraph protected HITL can survive restart and resume the exact review thread
  - CrewAI `public`, `protected`, `support`, and `workflow` Flow follow-ups survive restart with stable `flow_state_id`
- the latest [framework-crash-recovery-report.md](/home/edann/projects/eduassist-platform/docs/architecture/framework-crash-recovery-report.md) shows:
  - LangGraph protected HITL can survive hard process kill and still resume the same review thread
  - CrewAI `public`, `protected`, `support`, and `workflow` Flow continuity also survives hard process kill with stable `flow_state_id`
- the latest [framework-native-scorecard.md](/home/edann/projects/eduassist-platform/docs/architecture/framework-native-scorecard.md) tracks the current top-line native capability totals for both frameworks
- the runtime-readable scorecard artifact now lives at `/workspace/artifacts/framework-native-scorecard.json` inside the orchestrator container

## Upgrade Principles

1. Keep safety and authorization deterministic.
2. Improve each framework using its native strengths, not by forcing symmetry where it hurts product quality.
3. Select the primary orchestration stack through an explicit feature flag and keep canary/shadow controls separate.
3. Preserve one shared evaluation surface:
   - same tools
   - same datasets
   - same auth rules
   - same trace schema
4. When one framework is primary, avoid hidden dependence on the other framework's runtime in the primary response path.
5. Upgrade in phases so we can compare after every step.

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

- implemented in this round for:
  - the `support` slice via internal review/state/resume endpoints
  - low-risk `protected` reads such as access scope and administrative/documentation status before tool execution

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

- implemented in this round:
  - `orchestration.trace` now carries `langgraph.thread_id`, checkpointer backend, and graph-state fetch results
  - native snapshot inspection is now working again for newly written conversations through the Postgres checkpointer
  - `state_available=true` and checkpoint metadata are now visible in persisted traces for validated live threads

## Phase 2: CrewAI To Strong Native Production Shape

### 1. Persist Flow state for public, protected, support, and workflow

Target:

- persist state where multi-turn continuity matters most

Why:

- aligns with CrewAI Flow-first production guidance
- reduces dependence on external affinity hacks

Success criteria:

- public/protected/support/workflow follow-ups can recover flow state across restarts
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

Status:

- implemented in this round via [framework-native-scorecard.md](/home/edann/projects/eduassist-platform/docs/architecture/framework-native-scorecard.md)

### 2. Add failure-mode benchmarks

New benchmark classes:

- restart mid-thread
- recovery after process crash
- approval-required handoff
- long follow-up chain with topic switch
- multi-turn ambiguity with explicit repair

Status:

- implemented in this round for restart/recovery durability:
  - LangGraph protected HITL pause -> restart -> inspect -> resume
  - CrewAI `public` Flow restart continuity
  - CrewAI `protected` Flow restart continuity
- extended in this round to crash/recovery durability:
  - LangGraph protected HITL pause -> kill/start -> inspect -> resume
  - CrewAI `public` Flow crash continuity
  - CrewAI `protected` Flow crash continuity

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
