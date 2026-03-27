# Two-Stack Comparison Plan

## Objective

Build a fair, production-safe comparison between:

- the current `LangGraph + custom runtime` orchestrator
- a concurrent `CrewAI Flow + Crew` orchestrator

The goal is not framework shopping. The goal is to compare:

- semantic accuracy
- entity and attribute resolution
- conversational naturalness
- latency
- cost
- operational debuggability

on the same real Telegram and eval workloads.

## Sources

This plan follows current primary guidance and framework docs:

- OpenAI, practical guide to building agents
  - <https://openai.com/business/guides-and-resources/a-practical-guide-to-building-ai-agents/>
- Anthropic, writing effective tools for agents
  - <https://www.anthropic.com/engineering/writing-tools-for-agents>
- Anthropic, effective context engineering for AI agents
  - <https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents>
- Anthropic, demystifying evals for AI agents
  - <https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents>
- CrewAI flows
  - <https://docs.crewai.com/concepts/flows>
- CrewAI agents
  - <https://docs.crewai.com/en/concepts/agents>
- CrewAI tasks
  - <https://docs.crewai.com/en/concepts/tasks>
- CrewAI processes
  - <https://docs.crewai.com/en/concepts/processes>
- CrewAI event listeners
  - <https://docs.crewai.com/en/concepts/event-listener>
- AWS Prescriptive Guidance on CrewAI
  - <https://docs.aws.amazon.com/prescriptive-guidance/latest/agentic-ai-frameworks/crewai.html>

## Comparison Principles

To keep the experiment honest, both stacks must share the same:

- internal APIs and tools
- auth and authorization rules
- conversation state schema
- response contract
- trace fields
- transcript eval suite
- model family and model settings where possible

We should vary only the orchestration engine.

This means:

- do not let CrewAI bypass `api-core`
- do not move authorization into prompts
- do not give CrewAI private tools that LangGraph does not have
- do not compare different transcripts or different output contracts

## Recommended Shape

### Stack A. Current Baseline

Keep the current orchestrator as the baseline:

- `LangGraph` graph in `graph.py`
- custom execution and response assembly in `runtime.py`
- current provider layer in `llm_provider.py`
- current internal tools in `api-core`

### Stack B. CrewAI Concurrent Stack

Implement CrewAI as:

- `Flow` as the outer stateful shell
- a small `Crew` for bounded reasoning only

Recommended crew roles:

- `planner`
- `composer`
- `judge`

Recommended process:

- `Process.sequential`

Do not start with:

- large autonomous crews
- hierarchical process
- agent-to-agent free delegation
- agent-owned persistence

That would make the comparison noisier, slower, and less safe.

## Architecture

### Shared Interface

Create a common engine contract:

```python
class ResponseEngine(Protocol):
    async def respond(
        self,
        *,
        request: MessageResponseRequest,
        settings: Settings,
    ) -> MessageResponse: ...
```

Implementations:

- `LangGraphEngine`
- `CrewAIEngine`

### Shared State Contract

Both engines should consume and emit the same typed state kernel:

- `conversation_id`
- `active_task`
- `active_domain`
- `active_student`
- `pending_disambiguation`
- `actor_identity`
- `actor_access_scope`
- `public_entity`
- `public_attribute`
- `tool_trace`
- `judge_result`

The current runtime already contains much of this logic. The CrewAI pilot should adapt to it, not invent another schema.

### Shared Tool Contract

Both engines must call the same tool surface, especially for protected flows:

- `get_actor_identity_context`
- `get_student_administrative_status`
- `get_student_grades`
- `get_student_attendance`
- `get_student_upcoming_assessments`
- `get_financial_summary`
- public school profile and timeline tools

CrewAI agents should never call the database directly.

### Shared Response Contract

Both engines must return the existing `MessageResponse` shape:

- `message_text`
- `mode`
- `classification`
- `selected_tools`
- `suggested_replies`
- `citations`
- `visual_assets`
- `calendar_events`

## Recommended CrewAI Design

### Flow State

Use a typed Pydantic flow state with only the fields needed for parity:

- request
- normalized message
- resolved actor context
- conversation context
- semantic plan
- selected tools
- evidence bundle
- candidate answer
- judged answer
- final response

### Flow Steps

Recommended sequence:

1. `load_context`
2. `classify`
3. `plan`
4. `execute_tools`
5. `compose`
6. `judge`
7. `finalize`

### Crew Responsibilities

Planner:

- resolve intent
- resolve entity
- resolve attribute
- decide whether clarification is needed
- choose required tools

Composer:

- turn the evidence bundle into a grounded answer
- stay concise and natural
- avoid adjacent-domain leakage

Judge:

- verify the answer covers the asked attribute
- verify entity correctness
- verify no unsupported claims
- recommend fallback or revision when needed

### Task Guardrails

Each CrewAI task should use:

- structured output where possible
- guardrails for invalid or incomplete outputs
- deterministic fallback when structured validation fails

Examples:

- planner task returns Pydantic plan
- judge task returns `valid`, `reason`, `revision_needed`

## Routing Strategy

Add an engine selector:

- `ORCHESTRATOR_ENGINE=langgraph`
- `ORCHESTRATOR_ENGINE=crewai`
- `ORCHESTRATOR_ENGINE=shadow`

Behavior:

- `langgraph`: current production path
- `crewai`: full request handled by CrewAI engine
- `shadow`: LangGraph response is returned to the user; CrewAI runs in parallel and only logs traces and outputs

`shadow` is the safest and recommended initial mode.

## Measurement Plan

### Offline Replay

Run both stacks on:

- `tests/evals/datasets/orchestrator_cases.json`
- curated real Telegram transcripts

Capture for each engine:

- final answer
- tool sequence
- classification
- latency
- token use if available
- judge result

### Online Shadow

For selected Telegram traffic:

- send the user only the baseline response
- run the CrewAI engine in background
- persist both traces under the same conversation turn id

### Decision Metrics

Primary:

- answered the right question
- correct entity
- correct attribute
- no wrong-student leakage
- no duplicated stale answer

Secondary:

- naturalness
- shorter but complete answer
- lower `clarify` rate
- latency
- cost

## Implementation Phases

### Phase 0. Baseline Readiness

Goal:

- stabilize current traces and engine boundaries before adding the second stack

Work:

- extract engine interface
- centralize shared tool adapters
- centralize state loading and response persistence
- ensure trace payload is engine-agnostic

Deliverables:

- `engines/base.py`
- `engines/langgraph_engine.py`
- shared state loader and trace writer

### Phase 1. CrewAI Skeleton

Goal:

- get a no-op but valid `CrewAIEngine` into the repo

Work:

- add dependency and config
- create `crewai/flow.py`
- create `crewai/agents.py`
- create `crewai/tasks.py`
- wire engine selector in main response path

Deliverables:

- engine bootstraps
- smoke test for `ORCHESTRATOR_ENGINE=crewai`

### Phase 2. Public Slice Pilot

Goal:

- compare public institutional questions first

Scope:

- greeting
- identity
- contacts
- hours
- timeline
- structure/features

Why first:

- lower auth risk
- lower tool complexity
- fast comparison on naturalness and semantic coverage

Success criteria:

- parity or improvement on public evals
- acceptable latency and cost

### Phase 3. Protected Slice Pilot

Goal:

- compare the hardest protected questions safely

Scope:

- actor identity
- linked students
- grades
- attendance
- upcoming assessments
- student administrative/document status

Success criteria:

- no wrong-student leakage
- no attribute drift
- lower generic `clarify`

### Phase 4. Judge and Shadow Mode

Goal:

- run CrewAI side-by-side without affecting production users

Work:

- shadow execution in the background
- trace both outputs
- build comparison report

### Phase 5. Decision Review

Possible outcomes:

- keep LangGraph and borrow ideas from CrewAI pilot
- keep both, with CrewAI for selected domains
- migrate some slices if CrewAI clearly wins

## Repo Changes To Plan

Recommended files:

- `apps/ai-orchestrator/src/ai_orchestrator/engines/base.py`
- `apps/ai-orchestrator/src/ai_orchestrator/engines/langgraph_engine.py`
- `apps/ai-orchestrator/src/ai_orchestrator/engines/crewai_engine.py`
- `apps/ai-orchestrator/src/ai_orchestrator/crewai/flow.py`
- `apps/ai-orchestrator/src/ai_orchestrator/crewai/agents.py`
- `apps/ai-orchestrator/src/ai_orchestrator/crewai/tasks.py`
- `apps/ai-orchestrator/src/ai_orchestrator/crewai/listeners.py`
- `apps/ai-orchestrator/src/ai_orchestrator/engine_selector.py`

Likely supporting changes:

- `pyproject.toml`
- env settings for engine mode
- tests for engine parity
- trace schema additions for `engine_name`

## Risks

Main risks:

- unfair comparison due to different tool surfaces
- higher latency from over-using agents
- duplicated business logic between engines
- drifting state semantics across stacks

Mitigations:

- strict shared adapters
- sequential three-agent crew only
- shadow mode first
- transcript-driven evaluation

## Recommendation

The best implementation strategy is:

1. extract a shared engine interface
2. keep LangGraph as baseline
3. build a narrow CrewAI `Flow + Crew` pilot
4. run it in `shadow` mode
5. compare on real transcripts before any production switch

This gives the fairest comparison while preserving safety, observability, and development velocity.
