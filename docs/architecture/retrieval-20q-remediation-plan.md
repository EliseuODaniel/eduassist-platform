# Retrieval 20Q Remediation Plan

Date: 2026-04-02

This plan turns the `20Q` diagnosis into an implementation roadmap grounded in:

- repo evidence from [retrieval-20q-five-path-diagnosis.md](/home/edann/projects/eduassist-platform/docs/architecture/retrieval-20q-five-path-diagnosis.md)
- current path-specific code in:
  - [agent_kernel.py](/home/edann/projects/eduassist-platform/apps/ai-orchestrator/src/ai_orchestrator/agent_kernel.py)
  - [kernel_runtime.py](/home/edann/projects/eduassist-platform/apps/ai-orchestrator/src/ai_orchestrator/kernel_runtime.py)
  - [retrieval.py](/home/edann/projects/eduassist-platform/apps/ai-orchestrator/src/ai_orchestrator/retrieval.py)
  - [graph.py](/home/edann/projects/eduassist-platform/apps/ai-orchestrator/src/ai_orchestrator/graph.py)
  - [llamaindex_native_runtime.py](/home/edann/projects/eduassist-platform/apps/ai-orchestrator/src/ai_orchestrator/llamaindex_native_runtime.py)
  - [public_flow.py](/home/edann/projects/eduassist-platform/apps/ai-orchestrator-crewai/src/ai_orchestrator_crewai/public_flow.py)
  - [restricted_doc_tool_first.py](/home/edann/projects/eduassist-platform/apps/ai-orchestrator-specialist/src/ai_orchestrator_specialist/restricted_doc_tool_first.py)

Official references consulted:

- Qdrant payload indexing, filtered HNSW, hybrid queries, and search grouping:
  - https://qdrant.tech/documentation/concepts/indexing/
  - https://qdrant.tech/documentation/concepts/hybrid-queries/
  - https://qdrant.tech/documentation/concepts/search/
- LlamaIndex retriever modules and AutoMergingRetriever:
  - https://docs.llamaindex.ai/en/stable/module_guides/querying/retriever/retrievers/
  - https://developers.llamaindex.ai/python/framework/integrations/retrievers/auto_merging_retriever/
- LangGraph graph API and durable execution:
  - https://docs.langchain.com/oss/python/langgraph/use-graph-api
  - https://docs.langchain.com/oss/python/langgraph/durable-execution
- CrewAI production architecture:
  - https://docs.crewai.com/en/concepts/production-architecture
- OpenAI Agents SDK sessions, guardrails, tracing:
  - https://openai.github.io/openai-agents-python/sessions/
  - https://openai.github.io/openai-agents-python/guardrails/
  - https://openai.github.io/openai-agents-python/tracing/
- Pydantic models and validators:
  - https://docs.pydantic.dev/latest/concepts/models/
  - https://docs.pydantic.dev/latest/concepts/validators/

## Evidence Summary

Evidence from the `20Q` battery:

- `Q205` crashes in both `python_functions` and `llamaindex` with a `KernelRunResult` validation error.
- restricted positive internal-document retrieval is weak across all paths, with `specialist_supervisor` returning `restricted_document_no_match` on `Q216`–`Q218`.
- deep public multi-doc prompts are over-canonicalized or clarified too early in almost every path.
- `specialist_supervisor` showed the best semantic coverage but severe operational fragility and inflated latency.
- `crewai` misclassified public prompts as protected and timed out too often to be treated as a serious retrieval path.

## Gold-Standard Solution Shapes

### 1. Shared contract bugs should be fixed with typed constructors, not path-by-path patching

Two possible approaches:

- `Option A`: patch each path separately where it returns malformed data.
- `Option B`: centralize public canonical execution behind a shared constructor/factory that always returns a valid `KernelRunResult`, then validate at the boundary.

Decision:
- choose `Option B`

Why:
- Pydantic’s model-first pattern is the right fit for enforcing required fields and preventing malformed payloads from crossing boundaries.
- The failure in `Q205` is shared, which strongly suggests a shared abstraction problem, not a path-local problem.

### 2. Restricted internal-doc retrieval should become metadata-first and policy-first

Two possible approaches:

- `Option A`: loosen the similarity thresholds and hope hybrid retrieval surfaces the right internal docs.
- `Option B`: add an explicit restricted-doc planner with:
  - policy gate
  - title/alias expansion
  - metadata filters
  - grouped retrieval by document
  - separate `denied`, `no_match`, and `positive_match` outputs

Decision:
- choose `Option B`

Why:
- Qdrant recommends indexing filtered fields early and explicitly.
- Qdrant search groups are a better primitive for document-level retrieval than ad-hoc chunk stitching when the user is asking for a named internal document or playbook.
- The current code in [restricted_doc_tool_first.py](/home/edann/projects/eduassist-platform/apps/ai-orchestrator-specialist/src/ai_orchestrator_specialist/restricted_doc_tool_first.py) already separates `denied` vs `no_match`; it now needs stronger positive matching rather than looser fallback.

### 3. Deep public multi-doc prompts should escalate into document synthesis only when confidence justifies it

Two possible approaches:

- `Option A`: keep adding more public canonical lanes.
- `Option B`: keep canonical lanes for low-entropy prompts, but add a score-based escalation rule into deeper retrieval when the question is comparative, relational, or multi-document.

Decision:
- choose `Option B`

Why:
- LlamaIndex’s retriever guidance points toward composed/hierarchical retrieval for harder cases, not forcing every question into a direct fact path.
- AutoMergingRetriever is directly aligned with the problem shape here: it merges smaller child chunks into larger parent context to improve synthesis.
- Qdrant grouping by `document_id` or equivalent payload key is also a strong fit for document-level evidence packs before answer generation.

### 4. Clarification overuse should be fixed with guardrails and state, not more prompt text

Two possible approaches:

- `Option A`: tweak prompts and classifier wording.
- `Option B`: formalize a query-boundary policy with:
  - blocking input guardrails for access/policy
  - tool guardrails on restricted tools
  - thread-aware follow-up resolution
  - deterministic deny/clarify selection by typed state

Decision:
- choose `Option B`

Why:
- OpenAI Agents SDK guardrails guidance explicitly recommends tool guardrails when managers, delegated specialists, or multiple tools are involved.
- LangGraph’s docs emphasize conditional edges and deterministic/idempotent state transitions, which is a better fit than free-form clarifier behavior.

### 5. Path 5 operational fragility should be treated as an architecture problem, not a timeout problem

Two possible approaches:

- `Option A`: increase timeouts and retry more.
- `Option B`: harden dependency boundaries with health gating, explicit degraded modes, persistent sessions, and traceable dependency-unavailable states.

Decision:
- choose `Option B`

Why:
- LangGraph durable execution and OpenAI Agents sessions/tracing both reinforce the same pattern: persistent state and deterministic resumption matter more than retrying opaque side effects.
- CrewAI’s production architecture guidance also reinforces state schema, structured outputs, async execution, and persistence over ad-hoc retries.

## Implementation Plan

### Phase 0: Shared Contract Hardening

Goal:
- eliminate `Q205`-style malformed kernel results

Changes:
- create a shared builder for canonical public lane execution that returns a fully populated `KernelRunResult`
- add a `model_validator` or explicit factory guard around `KernelRunResult`
- move canonical public lane response assembly out of path-local branches into one shared helper

Files:
- [agent_kernel.py](/home/edann/projects/eduassist-platform/apps/ai-orchestrator/src/ai_orchestrator/agent_kernel.py)
- [kernel_runtime.py](/home/edann/projects/eduassist-platform/apps/ai-orchestrator/src/ai_orchestrator/kernel_runtime.py)
- [python_functions_native_runtime.py](/home/edann/projects/eduassist-platform/apps/ai-orchestrator/src/ai_orchestrator/python_functions_native_runtime.py)
- [llamaindex_native_runtime.py](/home/edann/projects/eduassist-platform/apps/ai-orchestrator/src/ai_orchestrator/llamaindex_native_runtime.py)
- [public_doc_knowledge.py](/home/edann/projects/eduassist-platform/apps/ai-orchestrator/src/ai_orchestrator/public_doc_knowledge.py)

Definition of done:
- `Q205` returns `200` and `quality=100` in `python_functions` and `llamaindex`
- no path can emit a kernel result missing `plan`, `reflection`, or `response`

### Phase 1: Restricted-Doc Retrieval That Can Actually Positively Match

Goal:
- make internal-document retrieval succeed when scope and evidence exist

Changes:
- introduce a restricted-doc query planner that extracts:
  - explicit doc title candidates
  - domain hint
  - document-set aliases
  - policy target
- add document-level grouping in retrieval using a stable payload key
- add metadata filters for restricted retrieval:
  - `visibility`
  - `category`
  - `document_set_slug`
  - `audience`
  - `section_parent`
  - `section_title`
- separate `restricted_document_denied`, `restricted_document_no_match`, and `restricted_document_search` before answer composition
- add a title/alias expansion table for the known internal-doc catalog

Files:
- [retrieval.py](/home/edann/projects/eduassist-platform/apps/ai-orchestrator/src/ai_orchestrator/retrieval.py)
- [pipeline.py](/home/edann/projects/eduassist-platform/apps/worker/src/worker_app/pipeline.py)
- [restricted_doc_tool_first.py](/home/edann/projects/eduassist-platform/apps/ai-orchestrator-specialist/src/ai_orchestrator_specialist/restricted_doc_tool_first.py)
- [llamaindex_native_runtime.py](/home/edann/projects/eduassist-platform/apps/ai-orchestrator/src/ai_orchestrator/llamaindex_native_runtime.py)
- [graph.py](/home/edann/projects/eduassist-platform/apps/ai-orchestrator/src/ai_orchestrator/graph.py)

Definition of done:
- `Q216`–`Q218` positively match for authorized users in at least `specialist_supervisor` and `python_functions`
- `Q220` denies deterministically in every path that supports restricted-doc access control

### Phase 2: Deep Public Multi-Doc Without Over-Canonicalization

Goal:
- stop collapsing comparative/document-synthesis prompts into shallow canonical replies

Changes:
- formalize a `public_deep_doc_synthesis` retrieval profile
- raise retrieval budget only when:
  - the query is comparative, relational, or multi-document
  - canonical lane confidence is below the high-confidence threshold
- add document-group aggregation using grouped hits instead of only top chunks
- add parent/section-aware escalation:
  - when multiple sibling chunks from one document win, upgrade to parent section context
- in the `llamaindex` path, add a path-specific documentary retriever shaped like:
  - hierarchical nodes
  - AutoMerging-style section merge for public multi-doc

Files:
- [retrieval.py](/home/edann/projects/eduassist-platform/apps/ai-orchestrator/src/ai_orchestrator/retrieval.py)
- [kernel_runtime.py](/home/edann/projects/eduassist-platform/apps/ai-orchestrator/src/ai_orchestrator/kernel_runtime.py)
- [public_doc_knowledge.py](/home/edann/projects/eduassist-platform/apps/ai-orchestrator/src/ai_orchestrator/public_doc_knowledge.py)
- [llamaindex_native_runtime.py](/home/edann/projects/eduassist-platform/apps/ai-orchestrator/src/ai_orchestrator/llamaindex_native_runtime.py)
- [graph.py](/home/edann/projects/eduassist-platform/apps/ai-orchestrator/src/ai_orchestrator/graph.py)

Definition of done:
- `Q208` and `Q211` improve materially in `python_functions`, `langgraph`, and `llamaindex`
- canonical lanes still win on low-entropy public questions such as `Q203`

### Phase 3: Clarify vs Deny vs Structured Answer Policy

Goal:
- cut unnecessary clarification and boundary mistakes

Changes:
- add a shared boundary policy object for:
  - public
  - protected structured
  - restricted doc
  - denied restricted
- require authenticated-thread and entity-state checks before any protected clarification
- add blocking input guardrails for access-tier mismatches
- add tool guardrails for restricted document tools
- separate:
  - `not enough context`
  - `not authorized`
  - `no matching document`
  - `structured data available`

Files:
- [graph.py](/home/edann/projects/eduassist-platform/apps/ai-orchestrator/src/ai_orchestrator/graph.py)
- [python_functions_native_runtime.py](/home/edann/projects/eduassist-platform/apps/ai-orchestrator/src/ai_orchestrator/python_functions_native_runtime.py)
- [llamaindex_native_runtime.py](/home/edann/projects/eduassist-platform/apps/ai-orchestrator/src/ai_orchestrator/llamaindex_native_runtime.py)
- [protected_flow.py](/home/edann/projects/eduassist-platform/apps/ai-orchestrator-crewai/src/ai_orchestrator_crewai/protected_flow.py)
- [public_flow.py](/home/edann/projects/eduassist-platform/apps/ai-orchestrator-crewai/src/ai_orchestrator_crewai/public_flow.py)

Definition of done:
- `Q212`, `Q213`, and `Q214` stop over-clarifying in `python_functions`
- `Q220` no longer clarifies in `langgraph` or `llamaindex`
- `crewai` stops denying clearly public prompts such as `Q201` and `Q204`

### Phase 4: Path-5 Operational Hardening

Goal:
- make `specialist_supervisor` quality observable without paying for fragility and inflated latency

Changes:
- add explicit health gating and dependency states for:
  - preview
  - retrieval
  - GraphRAG
  - specialist execution
- persist and expose dependency-unavailable traces consistently
- convert fragile side-effect calls into smaller bounded units with more deterministic fallback behavior
- tighten session storage and recovery behavior

Files:
- [runtime.py](/home/edann/projects/eduassist-platform/apps/ai-orchestrator-specialist/src/ai_orchestrator_specialist/runtime.py)
- [runtime_io.py](/home/edann/projects/eduassist-platform/apps/ai-orchestrator-specialist/src/ai_orchestrator_specialist/runtime_io.py)
- [session_memory.py](/home/edann/projects/eduassist-platform/apps/ai-orchestrator-specialist/src/ai_orchestrator_specialist/session_memory.py)
- [specialist_trace.py](/home/edann/projects/eduassist-platform/apps/ai-orchestrator/src/ai_orchestrator/specialist_trace.py)

Definition of done:
- path 5 no longer emits repeated `preview/retrieval/graphrag unavailable` for a healthy local run
- latency becomes benchmarkable again without hiding real semantic cost

### Phase 5: CrewAI Fair-Baseline Cleanup

Goal:
- keep `CrewAI` healthy and honest as a baseline, without over-investing in it

Changes:
- keep the `Flow` as the primary state container
- fix public/protected misclassification at the flow boundary
- use structured outputs and guardrails consistently for public path decisions
- convert long public operations to async kickoff where appropriate

Files:
- [public_flow.py](/home/edann/projects/eduassist-platform/apps/ai-orchestrator-crewai/src/ai_orchestrator_crewai/public_flow.py)
- [protected_flow.py](/home/edann/projects/eduassist-platform/apps/ai-orchestrator-crewai/src/ai_orchestrator_crewai/protected_flow.py)

Definition of done:
- `crewai` stops denying obviously public prompts in the 20Q battery
- timeout fallback is observable and rarer, but the path remains intentionally secondary

## Validation Plan

### Regression battery

Keep the `20Q` dataset as a standing regression:
- [retrieval_20q_probe_cases.json](/home/edann/projects/eduassist-platform/tests/evals/datasets/retrieval_20q_probe_cases.json)
- [compare_retrieval_20q_paths.py](/home/edann/projects/eduassist-platform/tools/evals/compare_retrieval_20q_paths.py)

### Required checkpoints

1. Re-run `python_functions` and `llamaindex` after Phase 0.
2. Re-run `python_functions`, `specialist_supervisor`, and `llamaindex` after Phase 1.
3. Re-run all five paths after Phase 3.
4. Treat Phase 4 as complete only after a clean local-source run and one container-based run.

### Promotion criteria

- no shared contract crashes
- no clarify on `Q220`
- at least two paths positively match restricted docs for `Q216`–`Q218`
- improved quality on `Q208` and `Q211` without regressing `Q203`
- path 5 operational traces are stable enough that latency is not dominated by dependency failures

## Recommended Execution Order

1. Phase 0
2. Phase 1
3. Phase 3
4. Phase 2
5. Phase 4
6. Phase 5

Why this order:
- first remove the shared crash
- then fix the most important policy/retrieval boundary
- then reduce noisy clarifications and deny mistakes
- then improve deeper documentary synthesis
- then harden path 5 so the comparison becomes honest again
- lastly keep `CrewAI` healthy as a baseline without distorting priorities

## Final Recommendation

The best next implementation cycle is:

- `P0`: shared contract hardening + restricted positive retrieval
- `P1`: deny/clarify policy cleanup
- `P2`: deep public multi-doc synthesis improvements

That is the smallest sequence that moves the project toward the gold standard for this repo:
- typed contracts
- metadata-aware restricted retrieval
- document-aware public synthesis
- path-specific internals with shared evidence semantics
- fair, benchmarkable multi-path comparison
