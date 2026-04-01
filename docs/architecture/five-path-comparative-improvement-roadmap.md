# Five-Path Comparative Improvement Roadmap

Updated: 2026-04-01

## Objective

Improve the four actively evolving paths while preserving `crewai` as a functional comparison baseline, and strengthen retrieval plus the shared comparative architecture so the project can answer a fair question:

- which path is best suited for an educational chatbot
- under which query/profile/risk/latency conditions
- with the strongest architecture each path can reasonably support

## Guardrails

- Do not optimize the system around a single general-purpose winner.
- Keep `crewai` working and benchmarkable, but do not invest in feature improvements beyond operational upkeep.
- Share only what must be shared:
  - auth and access rules
  - response contracts
  - evidence/citation contracts
  - datasets, eval harnesses, and scorecards
  - security rules
  - trace schema
- Allow path-specific ingress, planning, and retrieval orchestration when a unified layer limits a path's evolution.
- For every non-trivial phase, re-check the latest official documentation for the relevant frameworks and retrieval components before implementation.

## Comparative Roles

- `langgraph`: graph-native orchestration, stateful control, structured routing
- `crewai`: secondary comparison baseline, kept healthy but not expanded
- `python_functions`: deterministic/native orchestration and lowest-latency baseline
- `llamaindex`: document-native and retrieval-native path
- `specialist_supervisor`: quality-first premium path with specialist coordination

## Phase 0: Comparative Baseline Freeze

1. Maintain a canonical scorecard per path:
   - quality
   - latency
   - grounding
   - cost estimate
   - operational stability
   - suitability by slice
2. Publish fairness rules:
   - same corpus
   - same profiles
   - same benchmark datasets
   - same scoring rules
   - same trace/evidence expectations where feasible
3. Keep `crewai` in the benchmark matrix, but classify it as a maintained comparison baseline rather than an active innovation target.

## Phase 1: Shared Contract Layer vs Path-Specific Internals

1. Harden the shared contract layer:
   - auth/access behavior
   - response payload shape
   - evidence/citation payloads
   - benchmark harness
   - trace schema
2. Audit where shared ingress or shared retrieval is constraining a path.
3. Permit path-specific internals when justified:
   - `llamaindex` may keep a more native document/retrieval path
   - `specialist_supervisor` may keep a retrieval planner and tool-first path
   - `python_functions` may stay deterministic-first
   - `langgraph` may keep graph-native public/protected nodes

## Phase 2: Retrieval and Grounding Core

1. Consolidate retrieval policy:
   - deterministic structured tool first for canonical institutional/protected facts
   - hybrid retrieval for normal document lookup
   - GraphRAG only for genuine multi-document synthesis
   - explicit `valid_but_unpublished`
   - explicit restricted deny / no-match / grounded internal answer
2. Standardize retrieval observability:
   - strategy
   - reason
   - backend
   - source count
   - support count
   - citations
   - fallback path
3. Add regression packs for:
   - public multi-doc synthesis
   - restricted authorized retrieval
   - restricted deny
   - no published answer
   - false public/protected routing

## Phase 3: Deterministic-First Reinforcement

Apply to `langgraph`, `python_functions`, `llamaindex`, and `specialist_supervisor`.

1. Expand public/institutional deterministic fast paths.
2. Standardize escalation order:
   - deterministic answer builder
   - structured tool
   - hybrid retrieval
   - GraphRAG
   - agentic multi-step
3. Add category-specific answer builders for recurring public bundles.

## Phase 4: Path-Specific Architecture Improvement

### LangGraph

- reduce public latency outliers
- push more public known bundles into explicit nodes
- preserve graph-native tracing and state control

### Python Functions

- continue as deterministic/native speed baseline
- reduce context leakage and over-clarify behavior
- strengthen typed follow-up and `not_published` states

### LlamaIndex

- make document-native behavior more idiomatic
- reduce dependence on shared preview when it hurts document reasoning
- improve citation/evidence usage and keep non-document traffic cheap

### Specialist Supervisor

- keep quality-first behavior
- decompose the oversized runtime into modules
- preserve retrieval planner, tool-first, and multi-intent strengths
- continue hardening memory, session behavior, and malformed payload normalization

## Phase 5: Operational Hardening

These items must be treated as first-class engineering work, not cleanup.

1. Eliminate config/runtime drift:
   - source-based vs container-based parity
   - env loading parity
   - pilot URL consistency
   - local vs compose dependency parity
2. Remove env-driven service breakage:
   - fail-fast config validation
   - correct `extra='ignore'` or equivalent where needed
   - explicit startup diagnostics
3. Harden pilot operations:
   - health endpoints
   - readiness checks
   - fail-closed behavior
   - bounded timeouts
   - clean remote failure reporting
4. Reduce multi-stack rollout complexity:
   - separate primary/canary/shadow controls
   - clearer status endpoints
   - consistent runtime override visibility

## Phase 6: Specialist Supervisor Reliability

1. Improve latency for premium path where possible without removing quality-first behavior.
2. Continue session and memory hardening:
   - durable creation of session tables for sqlite-backed local memory
   - stable fallback when session store is unavailable
   - memory behavior under concurrent load
3. Continue malformed payload defense:
   - normalize text fields
   - normalize list fields
   - normalize nested payload fragments
4. Add dedicated stress and load-oriented probes.

## Phase 7: Tracing and Observability Consistency

1. Normalize trace shape across paths:
   - path
   - strategy
   - backend
   - reason
   - tools
   - evidence counts
   - fallback/deny metadata
2. Ensure parity across:
   - success
   - deny
   - clarify
   - fallback
   - timeout
   - remote pilot failure
3. Keep benchmark and runtime traces linkable by path and dataset slice.

## Phase 8: Benchmark and Research Discipline

1. Before each major phase, consult the latest official docs for:
   - LangGraph
   - CrewAI
   - LlamaIndex
   - OpenAI Agents SDK
   - Qdrant
   - GraphRAG
2. Document:
   - what guidance was checked
   - what was adopted
   - what was rejected and why
3. Update datasets whenever a real bug or transcript reveals a new failure mode.

## Priority Order

1. config/runtime drift and pilot fragility
2. shared retrieval/grounding hardening
3. deterministic-first reinforcement in the four active paths
4. `specialist_supervisor` decomposition and reliability
5. path-specific architecture upgrades where the shared layer is limiting evolution
6. trace/observability consistency
7. benchmark consolidation and comparative scorecard refresh

## Definition of Done

The roadmap is considered substantively complete when:

- all five paths remain benchmarkable
- `crewai` remains functional as a baseline
- the other four paths improve in quality, latency, or grounding without losing fairness of comparison
- source-based and container-based results stop drifting materially
- tracing is consistent enough to compare failure modes across paths
- retrieval decisions are observable and justified
- official documentation checks are part of the implementation workflow, not an afterthought
