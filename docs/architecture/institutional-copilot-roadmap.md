# Institutional Copilot Roadmap

## Objective

Transform EduAssist from a secure FAQ-and-workflow assistant into a full institutional copilot that can:

- converse naturally in public and authenticated channels
- navigate sectors and services like a front-desk concierge
- answer public, protected, and operational questions with grounded data
- execute workflows such as visits, protocols, and institutional requests
- generate visual artifacts such as charts and summary cards
- escalate safely to human operators when autonomy is not enough

## State-of-the-Art Principles

The target architecture follows current best practice for institutional assistants:

- one manager-style orchestrator, not a free-form swarm
- structured tools before open-ended retrieval when the answer is in a system of record
- agentic retrieval for document questions that need search planning
- selective GraphRAG only for global and multi-document synthesis
- self-critique and answerability checks before final response
- role-aware access control enforced outside the LLM
- human handoff for sensitive or unresolved requests

## Phases

### Phase 1. Concierge Layer

Status: implemented

- public capability discovery
- assistant identity and service navigation
- routing by sector for public queries
- less repetitive greetings in Telegram and orchestrator
- conversation memory reuse for short follow-ups

Key capabilities:

- `ola`
- `com quem eu falo?`
- `quais assuntos eu tenho aqui?`
- `com quem eu falo sobre boletos?`

### Phase 2. Knowledge OS

Status: partially implemented

- canonical public facts
- public leadership directory
- public KPI registry
- public highlights and differentiators
- derived facts for segments, grades, shifts, and schedules

Next work:

- expand canonical public facts into separate read models
- add service catalog coverage for every major school process
- expose leadership, coordination, and support inventories by area
- enrich public commercial and institutional profiles

### Phase 3. Action OS

Status: partially implemented

- visit workflow
- institutional request workflow
- support ticket workflow

Next work:

- real slot inventory for visits and meetings
- request status tracking by protocol
- approval-aware workflows for leadership and finance
- document request workflows with lifecycle updates

### Phase 4. Protected Records Copilot

Status: partially implemented

- academic summary
- attendance
- grades
- finance summary
- teacher schedule

Next work:

- explicit tool routing for second-copy invoices, declarations, and history requests
- richer teacher and staff operational tools
- protected charts for guardian and staff views
- better ambiguity resolution when multiple linked students exist

### Phase 5. Agentic Retrieval

Status: early implementation

- hybrid retrieval
- selective GraphRAG runtime path
- abstention policies for unsupported negative, exception, and comparative queries

Next work:

- query decomposition for complex document requests
- evidence scoring and citation pruning
- retrieval critique before answer composition
- multi-step retrieval plan for broad institutional questions

### Phase 6. Manager Loop and Specialists

Status: planned

Target specialist set:

- Concierge Agent
- Public Knowledge Agent
- Protected Records Agent
- Workflow Agent
- Critic Agent
- Visual Agent

Execution model:

- one manager orchestrator coordinates specialists
- specialists act as bounded tools with narrow responsibilities
- every specialist returns structured evidence or action output
- the critic checks usefulness, grounding, and tone before the final answer

### Phase 7. Multimodal and Visual Delivery

Status: partially implemented

- PNG chart generation
- Telegram photo delivery

Next work:

- cards for protocols and appointments
- tabular summaries for grades and finance
- richer operator-facing visual dashboards
- PDF/attachment-aware conversational flows

### Phase 8. Evaluation and Governance

Status: implemented and expanding

- smoke suite
- orchestrator eval suite
- adversarial and authz regressions
- tracing, logs, and dashboards

Next work:

- multi-turn conversation evals per persona
- naturalness and redundancy checks
- service-routing evals by domain
- workflow completion and operator handoff success metrics

## Immediate Next Sprint

1. Introduce a real service directory API in `api-core` instead of relying only on profile composition.
2. Split the current public school profile into smaller toolable read models:
   - school profile
   - org directory
   - service directory
   - public KPIs
   - public highlights
3. Add a manager loop in the orchestrator for:
   - plan
   - call tools
   - verify
   - respond
4. Add a critic step for tone, grounding, and next-step usefulness.
5. Expand Telegram UX with:
   - better progressive disclosures
   - contextual prompts
   - clearer action suggestions

## Success Criteria

The assistant should feel successful when it:

- sounds like a competent institutional attendant, not a fixed-rule bot
- answers public questions directly when the institution knows the answer
- routes users to the right sector without exposing protected data
- resolves protected requests after authentication with minimal friction
- opens and tracks workflows instead of pushing users back to the portal
- explains limits honestly without sounding robotic or evasive
