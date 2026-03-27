# Agentic Dual-Track Plan

## Context

This plan is based on the latest real Telegram battery from `telegram:1649845499`, not on synthetic demos.

Observed improvements:

- public greeting is more natural
- authenticated student lookup is safer
- unmatched student names are rejected correctly
- student focus activation is working
- upcoming assessments and enrollment identity answers are working

Observed failures:

- account identity questions are still not modeled as a first-class capability
- student-specific administrative/document questions are misrouted
- protected answers can still over-answer the question
- one recent turn showed duplicated persistence of the previous assistant response
- the semantic verifier is still weak in protected flows

## Evidence Summary

Recent battery highlights:

- `ola`
  - good
- `estou logado como`
  - bad
- `quais notas do meu filho lucas`
  - partial, because it returned notes plus attendance summary
- `quais notas do meu filho joão`
  - good, safe rejection
- `quero deslogar`
  - partial, generic explanation
- `qual situação de documentação do lucas?`
  - bad, wrong domain and wrong follow-up
- `lucas oliveira, o luquinha`
  - good, focus activation
- `quais próximas provas do lucas`
  - good
- `qual a matricula do lucas`
  - good
- `e como estão as faltas do lucas`
  - bad, persisted duplicate of the previous response

## Diagnosis

The current architecture is now "mostly right, but incomplete".

The dominant problems are no longer:

- generic chatbot behavior everywhere
- wrong-student leakage in every protected turn

The dominant problems now are:

- missing capability models
- coarse tool contracts
- answer composition over-including adjacent data
- weak protected-flow judging
- response persistence/idempotency issues

This means we should not restart from zero.
We should harden the current architecture where it is still under-modeled, and compare it to a narrow alternative architecture in shadow mode.

## Track A. Improve The Current Architecture

### Objective

Turn the current orchestrator into a more complete stateful copilot without adding more brittle local rules.

### A1. State Kernel V3

Add explicit state slots for:

- `actor_identity`
- `actor_access_scope`
- `active_student`
- `active_student_claim`
- `active_protected_attribute`
- `active_workflow`
- `pending_repair_type`
- `last_answer_fingerprint`

Why:

- `estou logado como`
- `quero deslogar`
- `qual situação de documentação do lucas?`
- `e como estão as faltas do lucas`

all need state that is more specific than the current generic slot memory.

### A2. Capability Registry For Protected Self-Service

Create explicit protected acts for:

- `actor_identity`
- `access_scope`
- `linked_students_overview`
- `student_admin_status`
- `student_document_status`
- `student_academic_attribute`
- `student_finance_attribute`
- `session_capability_limits`

Why:

Right now, some of these are implicit, rescued, or approximated by adjacent acts.

### A3. Tool Surface V2

Add or refactor typed tools so the model does not need to improvise:

- `get_actor_identity_context`
- `get_linked_students_overview`
- `get_student_document_status`
- `get_student_admin_status`
- `get_student_academic_attribute`
  - attribute selector: `grades`, `attendance`, `upcoming_assessments`, `enrollment_identity`
- `get_financial_next_due`
- `get_financial_overdue_summary`

Why:

The current tools are still too coarse for:

- `estou logado como`
- `qual situação de documentação do lucas?`
- `qual a próxima data de pagamento`
- `quais notas`
  versus
- `como estão as faltas`

### A4. Evidence Pack Composer

Move protected answers to the same pattern already improving public answers:

- semantic plan
- typed evidence pack
- grounded composer
- semantic judge

For protected answers, the composer must be attribute-aware:

- `grades` should not automatically dump attendance
- `attendance` should not replay enrollment identity
- `student_document_status` should not become actor-level admin status

### A5. Protected Semantic Judge

Expand the judge to verify:

- correct actor versus student entity
- correct requested attribute
- no adjacent-domain leakage
- no previous-answer replay

The judge should explicitly fail cases like:

- asked for attendance, returned enrollment code
- asked for actor identity, returned linked student
- asked for student document status, returned guardian admin status

### A6. Delivery And Persistence Guard

Add an answer-write guard to prevent:

- same assistant payload being persisted again for a new user turn
- stale response reuse when the tool execution path changed

Suggested mechanism:

- persist `assistant_message_fingerprint`
- compare with previous assistant turn
- if same fingerprint but different user turn and different semantic plan, flag and block write

### A7. Transcript-Driven Eval Expansion

Add eval classes for:

- actor identity
- logout/helpful limitation
- student admin status
- student document status
- protected attribute purity
- duplicate-response persistence

## Track B. Concurrent Architecture For Comparison

### Objective

Build a second architecture that is genuinely comparable without replacing production.

### Recommendation

Use a `shadow pilot`, not a rewrite.

### Preferred Concurrent Option

CrewAI in this repo should use:

- `Flow` as the outer stateful shell
- a very small bounded `Crew` only for:
  - planner
  - grounded composer
  - semantic judge

Do not use:

- a large many-agent autonomous crew
- agent-level authorization
- prompt-only student resolution

### B1. CrewAI Pilot Scope

Phase 1 comparison slice:

- `ola`
- `estou logado como`
- `quais meus filhos`
- `notas do Lucas`
- `faltas do Lucas`
- `próximas provas do Lucas`
- `qual a matricula do Lucas`

This is intentionally narrow:

- enough to compare state, entity resolution, tone, and attribute purity
- not large enough to create workflow risk

### B2. CrewAI Mapping

#### Flow state

- actor
- linked students
- active student
- requested attribute
- pending repair
- evidence bundle
- answer draft

#### Crew roles

- `planner`
  - resolve domain, entity, attribute, and needed tools
- `composer`
  - write a concise grounded answer
- `judge`
  - verify semantic coverage and entity correctness

#### Shared constraints

- tools still come from our internal APIs
- auth still enforced outside CrewAI
- traces still written into `conversation.tool_calls`

### B3. Comparison Metrics

Compare the current runtime and the CrewAI pilot on:

- wrong-entity rate
- wrong-attribute rate
- clarify rate
- duplicate-response rate
- human tone score
- groundedness
- latency
- token cost

### B4. Complexity

Public/protected comparison pilot:

- `medium-high`
- estimated effort: `1 to 2 weeks`

Why:

- tool wrappers are straightforward
- trace integration and side-by-side evals are not
- the state model must be explicit to make comparison fair

Production-parity CrewAI track:

- `high`
- estimated effort: `4 to 6 weeks`

Why:

- workflows, handoff, and observability raise the cost significantly

## Comparative Recommendation

### Current architecture

Best fit for near-term production improvement:

- lower risk
- easier to harden
- already integrated with traces, evals, and contracts

### CrewAI shadow pilot

Best fit for structured comparison:

- tests whether a Flow-plus-small-Crew design improves tone and attribute fidelity
- gives objective data instead of intuition

### Do not do now

- full framework switch
- workflow migration to CrewAI before the protected comparison slice is validated

## Immediate Next Steps

1. Implement Track A items A1 to A4 first.
2. Add the missing typed tools for actor identity and student document status.
3. Add protected semantic-judge checks for attribute purity.
4. Add response persistence guard.
5. Build the CrewAI shadow pilot for the protected comparison slice only after those tools exist.

## Decision Rule

Promote CrewAI beyond the pilot only if it beats the current runtime on:

- entity correctness
- attribute correctness
- human-rated tone

while staying acceptable on:

- latency
- cost
- observability
- operational safety
