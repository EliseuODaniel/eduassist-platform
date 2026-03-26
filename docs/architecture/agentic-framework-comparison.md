# Agentic Framework Comparison

## Objective

Compare the current EduAssist orchestrator against a second implementation option using CrewAI, based on current best practice and the repo's real pain points:

- brittle clarify behavior
- state leakage between turns
- wrong entity reuse, especially students
- overly templated final responses
- weak semantic verification of "did we answer the actual question?"

This document is meant to support a practical decision, not framework shopping.

## Sources

Primary and near-primary guidance used for this comparison:

- OpenAI, practical guide to building agents
  - <https://openai.com/business/guides-and-resources/a-practical-guide-to-building-ai-agents/>
- Anthropic, writing effective tools for agents
  - <https://www.anthropic.com/engineering/writing-tools-for-agents>
- Anthropic, effective context engineering for AI agents
  - <https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents>
- Anthropic, demystifying evals for AI agents
  - <https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents>
- CrewAI, concepts and event listeners
  - <https://docs.crewai.com/en/concepts/agents>
  - <https://docs.crewai.com/en/concepts/tasks>
  - <https://docs.crewai.com/en/concepts/processes>
  - <https://docs.crewai.com/en/concepts/flows>
  - <https://docs.crewai.com/en/concepts/event-listener>
- AWS Prescriptive Guidance, CrewAI
  - <https://docs.aws.amazon.com/prescriptive-guidance/latest/agentic-ai-frameworks/crewai.html>

## Current Architecture

EduAssist today is closest to this shape:

- one FastAPI-based orchestrator
- semantic planner plus deterministic routing
- typed tools over internal APIs
- slot memory and conversation traces in Postgres
- grounded composer and semantic verifier
- transcript-driven evals

This is directionally aligned with current best practice:

- one orchestrator, not a free-form swarm
- typed tools and explicit state
- authorization outside the LLM
- real transcript evals
- flexible generation inside grounded constraints

The remaining problems are not "we need more agents."
They are mostly:

- task state and discourse repair
- entity and attribute resolution
- tool contracts that are too coarse
- final-response naturalness
- verifier relevance, not just factual grounding

## What CrewAI Is Best At

CrewAI is strongest when used in its modern shape, not as a giant free-form multi-agent chat:

- `Flow` for stateful, event-driven control
- `Crew` for bounded multi-agent collaboration
- `Task` guardrails and structured outputs
- event listeners for telemetry and evaluation

For this repo, the best CrewAI pattern would be:

- `Flow` as the outer controller
- narrow `Crew`s only for bounded planning or composition steps
- typed internal tools kept outside the agents
- access control still enforced in `api-core`
- transcript traces still persisted in our existing schema

This is the only CrewAI shape that is realistically comparable to what we already have.

## What Not To Do With CrewAI

Avoid these anti-patterns:

- replacing all current orchestration with a large autonomous crew
- moving authorization or student selection safety into agent prompts
- using many collaborating agents for routine public and protected questions
- rebuilding the entire runtime before running a shadow pilot

For our case, a large open crew would likely worsen:

- latency
- cost
- observability clarity
- deterministic safety
- debugging of wrong-student and wrong-channel issues

## Best-Fit CrewAI Design For EduAssist

### Option A. Keep Current Runtime and Harden It

Shape:

- current orchestrator remains primary
- continue hardening state kernel, tool contracts, judge, and composer

Pros:

- least operational risk
- no second runtime to maintain
- current traces and evals stay intact
- fastest path to better production behavior

Cons:

- slower comparative learning against a second framework
- more custom orchestration code remains in-house

### Option B. Add a CrewAI Shadow Pilot

Shape:

- current runtime remains production path
- CrewAI runs side-by-side in shadow mode for selected prompts
- compare outputs, tool usage, latency, and error classes

Recommended CrewAI mapping:

- `Flow`: conversation state kernel
  - actor
  - linked students
  - active task
  - pending disambiguation
  - retrieved evidence
  - final answer draft
- `Crew`: used only when the prompt is genuinely complex
  - planner agent
  - evidence synthesizer agent
  - answer judge agent
- `Tasks`:
  - plan intent and entity/attribute
  - select tools
  - compose grounded answer
  - verify semantic coverage
- `Event listeners`:
  - bridge CrewAI events into `orchestration.trace`
  - persist crew metadata for later diffing

Pros:

- gives a fair comparison without destabilizing production
- lets us compare real transcripts side by side
- makes CrewAI evaluation measurable instead of speculative

Cons:

- introduces dual maintenance for a while
- requires a trace bridge and adapter layer
- still needs custom safety logic around auth and student identity

### Option C. Full CrewAI Replacement

Shape:

- CrewAI becomes the main orchestrator
- current runtime becomes a compatibility layer or is retired

Pros:

- simpler conceptual story if fully successful
- standard framework semantics for crews, flows, tasks

Cons:

- highest migration risk
- largest rewrite
- most difficult to keep parity on safety and traces
- likely the wrong first move for this repo

Recommendation:

- do not do this first

## Complexity Assessment

### 1. Public-only CrewAI pilot

Scope:

- greetings
- school profile
- contacts
- hours
- public documents and highlights

Complexity: `medium`

Estimated effort:

- 3 to 5 engineering days

Main work:

- add CrewAI dependency and packaging
- wrap existing public tools
- create one `Flow` and one small `Crew`
- map event listeners to our traces
- add eval harness branch

### 2. Protected-records CrewAI pilot

Scope:

- linked student disambiguation
- grades
- attendance
- finance summary

Complexity: `high`

Estimated effort:

- 6 to 10 engineering days

Why it is harder:

- student selection safety must remain deterministic
- auth and permissions cannot move into prompt logic
- wrong-entity reuse is one of our current top risks

### 3. Workflow and support CrewAI pilot

Scope:

- visit booking
- institutional requests
- human handoff
- protocol follow-up

Complexity: `high`

Estimated effort:

- 7 to 12 engineering days

Why it is harder:

- stateful follow-up is the core challenge
- protocol continuity requires durable state mapping
- our current workflow traces are already tightly integrated

### 4. Full side-by-side comparison framework

Scope:

- public
- protected
- workflow
- shared traces
- common eval harness

Complexity: `very high`

Estimated effort:

- 2 to 3 weeks for a serious shadow pilot
- 5 to 7 weeks for production-level parity

## Integration Risks Specific To Our Repo

### Async and service shape

Our orchestrator is a FastAPI service with explicit async paths and custom response shaping.

CrewAI can be embedded, but we still need:

- request-to-flow adapter
- flow-to-trace adapter
- response normalization into our current contract

### Tooling and auth

Our most important safety properties live outside the model:

- actor resolution
- student linkage
- permission checks
- internal API boundaries

CrewAI does not remove that need. It still requires the same deterministic tooling surface.

### Observability

CrewAI has event listeners and observability integrations, which is good.

But to compare fairly, we still need:

- stable `trace_id`
- mapping to `conversation.tool_calls`
- parity with current trace fields
- transcript-level diffing

### Evaluation

The only fair comparison is transcript-driven.

We should compare:

- wrong-student rate
- wrong-channel rate
- clarification overuse
- answer redundancy
- semantic coverage
- latency
- token cost
- human preference on tone and usefulness

## Recommendation

### Near term

Keep the current runtime as primary and continue hardening:

- state kernel
- student/entity safety
- channel policies
- semantic verifier
- grounded composer

### In parallel

Run a narrow CrewAI shadow pilot, not a replacement.

Best pilot slice:

- one public conversational slice
  - contacts, hours, school profile, "what can you help with?"
- one protected slice
  - student focus activation and academic summary
- no workflows in phase 1

### Why this is the best comparison

It compares frameworks on the part that matters:

- planning quality
- contextual composition
- tool usage discipline
- state handling

without risking:

- authorization regressions
- workflow corruption
- protocol continuity issues

## Proposed Shadow-Pilot Success Criteria

Pilot should only continue if CrewAI beats or matches the current runtime on:

- lower wrong-entity rate
- lower clarify rate
- better human-rated tone
- equal or better grounding
- equal or acceptable latency
- manageable operational traces

If it loses on safety or observability, keep CrewAI as a research track only.

## Practical Decision

Best pragmatic path for EduAssist:

1. keep the current orchestrator as the production baseline
2. fix the remaining high-severity state and tooling bugs here first
3. build a CrewAI shadow pilot for a narrow slice
4. compare on real transcripts, not demos
5. only then decide whether CrewAI deserves expansion
