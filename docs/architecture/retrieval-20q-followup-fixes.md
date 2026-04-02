# Retrieval 20Q Follow-up Fixes

Date: 2026-04-02

Dataset: [retrieval_20q_probe_cases.json](/home/edann/projects/eduassist-platform/tests/evals/datasets/retrieval_20q_probe_cases.json)

Scope:
- first diagnostic pass on `python_functions`
- first diagnostic pass on `specialist_supervisor`
- goal: register concrete follow-up fixes before expanding the same 20-question set to the remaining paths

## Summary

The first pass exposed real product bugs and also a large operational distortion on the 5th path.

What is bug-level:
- `python_functions` crashes on the permanence/family-support canonical case.
- `python_functions` over-clarifies protected and restricted questions that already have enough context.
- `python_functions` misroutes protected administrative-documentation status into support/protocol behavior.
- `specialist_supervisor` misses positive matches on 3 restricted-document cases that should succeed.

What is operational noise but still important:
- `specialist_supervisor` suffered repeated local dependency failures while trying preview and retrieval via the orchestrator.
- this inflated latency heavily and should be treated as an operational defect, not only a model/runtime quality issue

## Path 3 Findings

### P3-01

- Path: `python_functions`
- Case: `Q205`
- Symptom: hard failure
- Reason: `ValidationError` building `KernelRunResult`
- Impact: canonical public retrieval path is broken for the permanence/family-support bundle

Evidence:
- `ValidationError: 3 validation errors for KernelRunResult`
- missing fields:
  - `plan`
  - `reflection`
  - `response`

Recommended fix:
- patch the canonical permanence/family-support return shape in [python_functions_native_runtime.py](/home/edann/projects/eduassist-platform/apps/ai-orchestrator/src/ai_orchestrator/python_functions_native_runtime.py)
- add a regression probe for this exact bundle

### P3-02

- Path: `python_functions`
- Cases:
  - `Q212`
  - `Q213`
  - `Q214`
  - `Q216`
  - `Q220`
- Symptom: unnecessary clarification
- Impact: protected and restricted retrieval quality drops even when context and access are already sufficient

Observed behavior:
- repeated generic clarification about public information
- follow-up context drop on protected thread
- weak deny behavior for restricted document request

Recommended fix:
- reduce clarify threshold for authenticated/protected questions with clear entity context
- add explicit restricted-document deny path for guardian users
- add follow-up-aware protected routing before generic clarify

### P3-03

- Path: `python_functions`
- Case: `Q215`
- Symptom: routed to support/protocol status instead of administrative-documentation status
- Impact: wrong product behavior on protected administrative retrieval

Recommended fix:
- strengthen administrative-documentation intent routing
- separate `document_status` from `support_protocol_status` earlier in the plan

### P3-04

- Path: `python_functions`
- Cases:
  - `Q204`
  - `Q208`
  - `Q209`
  - `Q211`
- Symptom: semantically acceptable but shallow public answers
- Impact: keyword score drops on deeper public retrieval types

Recommended fix:
- improve public deep-multi-doc planning and section-aware grounding
- prefer retrieval/doc-bundle path over generic structured summary on these cases

## Path 5 Findings

### P5-01

- Path: `specialist_supervisor`
- Cases:
  - multiple across public and protected slices
- Symptom: repeated operational degradation
- Impact: latency exploded and some grounded behaviors degraded to clarify/fallback

Observed runtime errors:
- `specialist_orchestrator_preview_unavailable`
- `specialist_orchestrator_retrieval_unavailable`
- `specialist_orchestrator_graphrag_unavailable`
- `MaxTurnsExceeded`

Recommended fix:
- harden local source-mode dependency strategy for preview and retrieval
- reduce dependency on remote orchestrator for source-mode evals where possible
- bound specialist turns more aggressively on eval traffic

### P5-02

- Path: `specialist_supervisor`
- Cases:
  - `Q216`
  - `Q217`
  - `Q218`
- Symptom: restricted positive cases returned `restricted_document_no_match`
- Impact: authorized staff retrieval is underperforming on internal documents

Recommended fix:
- review internal-doc query normalization and match threshold in [restricted_doc_tool_first.py](/home/edann/projects/eduassist-platform/apps/ai-orchestrator-specialist/src/ai_orchestrator_specialist/restricted_doc_tool_first.py)
- add exact-title and high-confidence alias matching for restricted internal docs
- add regression cases for these 3 prompts

### P5-03

- Path: `specialist_supervisor`
- Case: `Q205`
- Symptom: safe clarify on a case that should likely hit the permanence/family-support public bundle
- Impact: quality loss on a canonical public query

Recommended fix:
- widen canonical/permanence matching coverage in the public fast-path layer

### P5-04

- Path: `specialist_supervisor`
- Case: `Q211`
- Symptom: clarify on deep public multi-doc synthesis
- Impact: quality loss on expensive overview-style retrieval

Recommended fix:
- improve grounding gate criteria so supported deep-public synthesis is answered instead of clarified away

## Priority

1. Fix `python_functions` crash on `Q205`
2. Fix `specialist_supervisor` restricted positive internal-doc matches
3. Reduce over-clarification on `python_functions` protected/restricted traffic
4. Harden `specialist_supervisor` source-mode preview/retrieval dependencies
5. Re-run the 20Q battery on paths 3 and 5 after those fixes
