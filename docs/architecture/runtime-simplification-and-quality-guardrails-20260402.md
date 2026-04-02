# Runtime Simplification And Quality Guardrails

## Summary

This wave simplified the active orchestration surface of EduAssist and tightened repository-level quality guardrails.

Implemented outcomes:

- archived the legacy `CrewAI` path from the active runtime, compose stack, and live experiment routing
- kept four active orchestration paths:
  - `langgraph`
  - `python_functions`
  - `llamaindex`
  - `specialist_supervisor`
- extracted specialist-public and restricted-document heuristics out of the `specialist_supervisor` runtime into focused modules
- expanded deterministic public canonical lanes and protected routing corrections across the active paths
- added repository CI in `.github/workflows/ci.yml`
- added classic `pytest` unit coverage for fast paths, slice inference, public knowledge composition, and specialist helper policies

## Specialist Decomposition

The `specialist_supervisor` runtime was partially decomposed to reduce the God-file problem without breaking behavior:

- `public_query_patterns.py`
  - public intent detectors
  - teacher-directory extraction helpers
  - cross-document bundle heuristics
- `restricted_doc_matching.py`
  - restricted-document stopwords
  - anchor-term logic
  - restricted hit scoring helpers

This keeps the main runtime focused on orchestration while moving lexical heuristics into smaller modules.

## CrewAI Decommissioning

The following changes were applied:

- removed `apps/ai-orchestrator-crewai`
- removed active `CrewAI` engine wiring from `ai-orchestrator`
- removed `CrewAI` pilot routing from compose and runtime diagnostics
- archived legacy eval/promotion scripts that existed only for the old framework rollout path

`CrewAI` remains only in historical scorecards and explicit archival notes where past benchmark history matters.

## Quality Guardrails

The repository now has three lightweight but real safety nets:

1. Focused Ruff gate for changed runtime and eval surfaces
2. `compileall` over active Python source directories
3. `pytest` unit coverage under `tests/unit`

These checks are designed to be realistic for the current monorepo instead of pretending the full historical tree is already globally lint-clean.

## Remaining Follow-Up

This wave intentionally did not try to finish every structural cleanup item in one shot. The main follow-up still worth doing is:

- continue decomposing `apps/ai-orchestrator-specialist/src/ai_orchestrator_specialist/runtime.py`
- add more unit coverage around protected follow-up policy and canonical lane regressions
- optionally remove or archive historical docs that still reference the old five-path era
