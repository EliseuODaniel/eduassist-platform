# Independent Orchestrators Architecture

## Goal

This branch changes the comparison from "one platform orchestrator with multiple engines" to "four end-to-end orchestration services that share the same school, policy, and infrastructure constraints but keep their reasoning paths separate."

The practical goal is to make the comparison fairer without turning the project into four unrelated products.

## What Used To Be Shared

Before this branch, the system had one stronger common orchestration layer that still influenced:

- request routing
- some public fast paths
- post-retrieval answer shaping
- context repair
- final polish
- candidate choice between alternative answers

That design was good for product consistency, but it reduced the experimental distance between stacks.

## What Is Now Separated

Each stack now has its own public service entrypoint:

- `apps/ai-orchestrator/src/ai_orchestrator/main_langgraph.py`
- `apps/ai-orchestrator/src/ai_orchestrator/main_python_functions.py`
- `apps/ai-orchestrator/src/ai_orchestrator/main_llamaindex.py`
- `apps/ai-orchestrator-specialist/src/ai_orchestrator_specialist/main.py`

Each path also keeps local decisions for:

- planning
- retrieval use
- post-retrieval composition
- runtime-specific answer verification
- stack-local fast paths

The specialist path additionally uses local retrieval instead of consuming the other service as a retrieval facade.

## Stack-Specific Character

### LangGraph

LangGraph now uses a dedicated message workflow with explicit nodes for:

- bootstrap
- public compound handling
- public retrieval
- restricted retrieval
- runtime delegation when needed

This keeps the stack closer to state-machine orchestration instead of hiding most behavior in a single common runtime.

### Python Functions

The Python Functions path keeps deterministic routing as its main strength:

- typed tool selection
- semantic gating before deterministic execution
- low-latency public and protected direct answers

The goal of this path is not maximal expressive power, but reliable and auditable execution.

### LlamaIndex

The LlamaIndex path keeps the most framework-native retrieval composition:

- router query engine
- citation query engine
- recursive retrieval
- response synthesis

This branch also keeps citation-aware retrieval metadata so the path can prefer document-grounded answers when the query requires cross-document synthesis.

### Specialist Supervisor

The specialist path keeps its quality-first structure:

- dedicated runtime
- local retrieval
- public and protected fast paths
- specialist-specific decision helpers

The trade-off remains higher conceptual complexity, but this path is the most independent from the core orchestrator code.

## Retrieval: Shared Infrastructure, Separate Strategy

The project still shares the same infrastructure:

- PostgreSQL for lexical/document metadata access
- Qdrant for vector retrieval
- the same document corpus
- the same policy and access rules

What is now more separate is the retrieval strategy around that infrastructure:

- stack-local wrappers
- stack-local use of retrieval outputs
- stack-local answer composition after retrieval
- stack-local confidence and fallback decisions

This preserves fairness while avoiding four duplicated corpora.

## Retrieval Improvements in This Branch

The retrieval layer now exposes stronger planning signals:

- query variants
- subqueries for compound requests
- coverage by subquery
- corrective retry when coverage is weak
- recommendation for citation-first answering

These signals are especially useful for:

- long compound public questions
- policy synthesis across multiple documents
- process comparisons
- calendar and timeline composition

## What Still Stays Shared

Some things remain shared by design:

- authentication and access policy
- API contract
- school data sources
- database and vector index infrastructure
- channel formatting

This is intentional. The comparison should isolate orchestration differences, not create four different schools or four different policy systems.

## Why This Makes the Comparison Fairer

This architecture is fairer because:

- each stack can now express its native strengths more directly
- there is no longer one central post-processing LLM shaping all answers
- retrieval and synthesis are no longer funneled through one shared answer layer
- the benchmark calls each service directly

At the same time, it stays controlled because:

- the same problem is being solved
- the same permissions apply
- the same corpus is available
- the same benchmark and human review process can be reused

## Operational Note

The recommended evaluation flow for this branch is:

1. run single-turn `30Q` and `50Q`
2. run the threaded multi-turn battery
3. generate the blind review packet
4. compare automatic and qualitative findings before any merge
