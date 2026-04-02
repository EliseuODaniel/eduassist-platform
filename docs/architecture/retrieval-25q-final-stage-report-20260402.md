# Retrieval 25Q Final Stage Report

Date: 2026-04-02

Dataset:
- [retrieval_25q_probe_cases.generated.20260402.json](/home/edann/projects/eduassist-platform/tests/evals/datasets/retrieval_25q_probe_cases.generated.20260402.json)

Raw reports:
- [retrieval-25q-cross-path-report-20260402.md](/home/edann/projects/eduassist-platform/docs/architecture/retrieval-25q-cross-path-report-20260402.md)
- [retrieval-25q-cross-path-report-20260402.json](/home/edann/projects/eduassist-platform/docs/architecture/retrieval-25q-cross-path-report-20260402.json)

## Scope

This run evaluated the four active orchestration paths:

- `langgraph`
- `python_functions`
- `llamaindex`
- `specialist_supervisor`

The battery used `25` fresh prompts with `exact_overlap = 0` against previous datasets in `tests/evals/datasets`.

Coverage:

- `25` unique prompts
- `22` retrieval categories
- `16` public prompts
- `4` protected prompts
- `5` restricted prompts

Retrieval types covered:

- `public_policy_bridge`
- `public_timeline`
- `public_documents_credentials`
- `public_family_new_bundle`
- `public_permanence_support`
- `public_process_compare`
- `public_first_month_risks`
- `public_deep_multi_doc`
- `public_section_aware`
- `public_visibility_boundary`
- `public_service_routing`
- `public_teacher_directory`
- `public_calendar_week`
- `public_year_three_phases`
- `public_academic_policy_overview`
- `protected_structured_academic`
- `protected_structured_followup`
- `protected_structured_finance`
- `protected_structured_admin`
- `restricted_doc_positive`
- `restricted_doc_negative`
- `restricted_doc_denied`

## Final Ranking

By quality:

1. `langgraph`: `93.4`
2. `specialist_supervisor`: `92.1`
3. `llamaindex`: `91.8`
4. `python_functions`: `91.3`

By keyword pass:

1. `langgraph`: `18/25`
2. `specialist_supervisor`: `17/25`
3. `python_functions`: `16/25`
4. `llamaindex`: `16/25`

By latency:

1. `python_functions`: `151.4 ms`
2. `specialist_supervisor`: `1627.9 ms`
3. `llamaindex`: `1737.0 ms`
4. `langgraph`: `1814.8 ms`

By practical balance:

1. `python_functions`
2. `langgraph`
3. `specialist_supervisor`
4. `llamaindex`

## Stack Summary

| Stack | OK | Keyword pass | Quality | Avg latency | Median | P95 | Max |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `langgraph` | `25/25` | `18/25` | `93.4` | `1814.8 ms` | `405.0 ms` | `5533.9 ms` | `6246.6 ms` |
| `python_functions` | `25/25` | `16/25` | `91.3` | `151.4 ms` | `141.5 ms` | `230.7 ms` | `279.5 ms` |
| `llamaindex` | `25/25` | `16/25` | `91.8` | `1737.0 ms` | `143.5 ms` | `10532.6 ms` | `21158.5 ms` |
| `specialist_supervisor` | `25/25` | `17/25` | `92.1` | `1627.9 ms` | `112.9 ms` | `11937.4 ms` | `18011.6 ms` |

## Main Findings

### 1. `python_functions` remains the best overall production baseline

Why:

- lowest average latency by far
- lowest `P95`
- no request failures
- perfect `restricted` slice
- public canonical bundles remain strong

What still hurts:

- `Q207` `public_first_month_risks` still falls into unnecessary clarification
- `Q222` `public_teacher_directory` still leaks the wrong entity/channel boundary
- `Q214`, `Q215`, `Q223`, `Q224` are still losing expected wording in the rubric

Assessment:

- best practical path for default traffic today
- most mature low-latency path

### 2. `langgraph` achieved the best quality score, but still pays too much for public canonicity

Why it won quality:

- strongest public slice overall
- `12/16` keyword pass in public
- perfect `restricted` slice
- better public canonical coverage than the other non-specialist paths

What still hurts:

- public canonicity is still expensive:
  - `Q204`: `6246.6 ms`
  - `Q223`: `5588.8 ms`
  - `Q211`: `5314.4 ms`
- `Q222` `teacher_directory` still leaks a forbidden value
- protected wording is still slightly too generic for admin/finance/follow-up

Assessment:

- highest quality path today
- still not the best ROI for default traffic because canonical public answers cost too much

### 3. `llamaindex` is competitive in quality but still has the worst latency tail

Strengths:

- quality is close to the leaders
- median latency is low
- perfect `restricted` slice
- several canonical public answers are now deterministic and fast

What still hurts:

- severe `P95` instability:
  - `Q207`: `21158.5 ms`
  - `Q211`: `11106.5 ms`
  - `Q223`: `8237.2 ms`
- `public_profile` / fallback behavior still explodes on some public prompts
- `teacher_directory` still leaks forbidden entity/channel data

Assessment:

- quality is solid
- tail latency is still too unstable to promote it over `python_functions`

### 4. `specialist_supervisor` is semantically strong, but still has premium-tail behavior on hard public prompts

Strengths:

- best median among the non-`python_functions` paths
- strong public canonical lanes when they hit preflight or tool-first
- perfect `restricted` slice in this fair run
- good keyword pass overall: `17/25`

What still hurts:

- public complex prompts still trigger expensive safe fallbacks:
  - `Q207`: `18011.6 ms`
  - `Q211`: `14036.4 ms`
  - `Q224`: `3541.2 ms`
  - `Q223`: `3119.4 ms`
- protected structured prompts still lose wording quality
- `teacher_directory` is the worst path-specific wording issue in this run:
  - `Q222`: quality `43`

Assessment:

- very strong premium path
- still needs P95 work before it can be treated as the default operational winner

## Slice Analysis

### Public

Public slice summary:

- `langgraph`: `93.4`, `12/16`, `2649.7 ms`
- `specialist_supervisor`: `92.7`, `12/16`, `2485.0 ms`
- `llamaindex`: `90.9`, `10/16`, `2606.3 ms`
- `python_functions`: `90.2`, `10/16`, `125.2 ms`

Interpretation:

- `langgraph` and `specialist_supervisor` lead public quality
- `python_functions` is still the only path with truly low public latency
- `llamaindex` is quality-competitive but hurt by public outliers

### Protected

Protected slice summary:

- `langgraph`: `85.0`, `1/4`, `261.9 ms`
- `python_functions`: `85.0`, `1/4`, `202.3 ms`
- `llamaindex`: `85.0`, `1/4`, `201.4 ms`
- `specialist_supervisor`: `80.0`, `0/4`, `105.3 ms`

Interpretation:

- protected retrieval itself is not broken
- the main gap is `wording / rubric alignment`, not data access
- all four paths still need a stronger protected answer contract for:
  - academic family summary
  - finance summary
  - admin/documental next step
  - follow-up focus retention

### Restricted

Restricted slice summary:

- `langgraph`: `100.0`, `5/5`, `385.3 ms`
- `python_functions`: `100.0`, `5/5`, `194.8 ms`
- `llamaindex`: `100.0`, `5/5`, `183.7 ms`
- `specialist_supervisor`: `100.0`, `5/5`, `103.4 ms`

Interpretation:

- the restricted-document work paid off
- positive, negative and denied paths are now all working across the four stacks
- `specialist_supervisor` was the fastest restricted path in this run

## Important Residuals

### Shared residuals

- `Q222` `public_teacher_directory`
  - all stacks still mishandle the public teacher-contact boundary
  - this is the clearest shared bug left in public wording/policy

- protected structured wording
  - `Q214` and `Q215` still lose expected wording in all paths
  - this looks like answer-contract/rubric alignment, not retrieval failure

- `Q224` `public_year_three_phases`
  - `langgraph`, `python_functions`, and `llamaindex` still miss expected wording
  - `specialist_supervisor` was the only path to close this one at `100`

### Path-specific residuals

`python_functions`

- `Q207` public-first-month-risks clarification should become deterministic
- `Q222` teacher-directory boundary needs stronger deny/routing wording

`langgraph`

- public canonical lanes still overpay latency for deterministic facts
- `Q204`, `Q211`, `Q223` remain too expensive

`llamaindex`

- `public_profile` is still a tail-latency hazard
- `Q207`, `Q211`, `Q223` confirm the issue

`specialist_supervisor`

- strict safe fallback remains too expensive on hard public prompts
- `Q207` and `Q211` are the biggest P95 anchors
- teacher-directory fast path still needs policy-safe wording

## ROI Roadmap After This 25Q

1. `python_functions`
- promote `Q207` first-month-risks to deterministic canonical lane
- fix teacher-directory boundary wording
- tighten protected admin/finance wording contract

2. `specialist_supervisor`
- cut `strict_safe_fallback` for public complex prompts
- force cheaper deterministic fallback earlier on `Q207` and `Q211`
- harden teacher-directory policy wording

3. `langgraph`
- convert more canonical public bundles into direct deterministic answers before graph execution
- reduce latency of `Q204`, `Q211`, `Q223`

4. `llamaindex`
- remove or heavily constrain `llamaindex_public_profile` on public complex prompts
- prefer deterministic or cheaper retrieval fallback earlier

## Final Conclusion

This 25Q run closes the current phase with a clear picture:

- `python_functions` is still the best default operational path
- `langgraph` is the best quality path
- `specialist_supervisor` is the strongest premium semantic path but still needs P95 work
- `llamaindex` is competitive but still too unstable in latency tail

The project is now in a good state to move from broad architecture changes to focused path-by-path optimization.
