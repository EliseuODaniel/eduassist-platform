# Retrieval 20Q Improvement Plan 2026-04-02

This document captures the improvement plan derived from the last two fresh 20Q retrieval runs:

- previous fresh run: `retrieval-20q-cross-path-report-20260404.json`
- current fresh run after remediation: `retrieval-20q-cross-path-report-20260402d.json`

Scope intentionally focused on:

- `python_functions`
- `langgraph`
- `llamaindex`
- `specialist_supervisor`

`CrewAI` remained out of implementation scope and was rerun only as a comparison baseline.

## Plan

1. Fix shared protected-state regressions before path-specific tuning.
2. Harden public canonical lane matching so deep public prompts do not fall into the wrong bundle.
3. Make restricted-document retrieval query-aware and precision-first.
4. Expand family-level protected aggregates for academic and finance queries.
5. Re-test with a fresh no-overlap dataset and compare against the previous fresh run.

## Implemented

- Shared runtime/kernel:
  - fixed family finance aggregate detection and the `FINANCE_TERMS` regression
  - widened family academic aggregate detection
  - switched restricted-document answers to query-aware wording in shared paths
- Public retrieval/canonical lanes:
  - broadened family-new bundle matching
  - added public timeline bundle handling
  - narrowed visibility-boundary routing to require a real public-vs-authentication contrast
  - prioritized `secretaria + portal + credenciais` before visibility-boundary matching
  - strengthened first-month risks wording to mention `credenciais`, `documentacao` and `rotina`
- Restricted-document retrieval:
  - added stronger generic-term filtering
  - added rare-anchor gating for terms like `telegram`, `escopo`, `avaliac`, `hospedagem`, `internacional`, `excursao`
  - added query-aware lead wording for:
    - teacher manual / evaluations
    - Telegram scope protocol
    - finance negotiation playbook
- Specialist-specific:
  - expanded family finance aggregate phrasing
  - added family academic aggregate detection
  - prevented finance tool-first from hijacking admin/documentation queries
  - rebuilt `ai-orchestrator` and `ai-orchestrator-specialist` containers so pilot-mode measurement used current code
- Eval tooling:
  - expanded the official 20Q generator with fresh phrasings across all 20 categories
  - preserved exact-prompt no-overlap

## Before vs After

Comparison baseline: `retrieval-20q-cross-path-report-20260404.json`

| Stack | Quality Before | Quality After | Delta | Latency Before | Latency After | Delta | Keyword Before | Keyword After |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `python_functions` | `90.4` | `96.4` | `+6.0` | `205.4 ms` | `291.4 ms` | `+86.0 ms` | `11/20` | `17/20` |
| `langgraph` | `92.0` | `97.4` | `+5.4` | `1992.5 ms` | `2096.1 ms` | `+103.6 ms` | `12/20` | `18/20` |
| `llamaindex` | `86.2` | `93.4` | `+7.2` | `3321.0 ms` | `516.2 ms` | `-2804.8 ms` | `8/20` | `14/20` |
| `specialist_supervisor` | `90.4` | `96.0` | `+5.6` | `6643.2 ms` | `5478.9 ms` | `-1164.3 ms` | `15/20` | `16/20` |

## Remaining Gaps

### `python_functions`

- `Q207`: first-month risks answer is good but still misses one rubric keyword in some phrasings.
- `Q213`: follow-up to a family academic aggregate still loses protected conversational context.
- `Q214`: family finance summary still falls back to support/protocol wording in some phrasings.
- `Q219`: restricted no-match is now correct, but wording still scores `88` rather than `100`.

### `langgraph`

- `Q213`: same protected follow-up context gap as `python_functions`.
- `Q214`: family finance summary still routes to protocol/status wording in some phrasings.
- `Q219`: restricted no-match is correct but still slightly under the strict rubric.

### `llamaindex`

- `Q204`, `Q207`, `Q208`, `Q209`: still overuses `contextual_public_direct_answer` for deeper public-document prompts.
- `Q213`: follow-up protected context still collapses into a weaker public/profile fallback.
- `Q214`: same family-finance wording gap.
- `Q219`: correct no-match, but still under the strict rubric.

### `specialist_supervisor`

- `Q204`: family-new bundle still routes through a timeline-oriented branch rather than the intended family-new bundle.
- `Q206`: public process compare still degrades to a cautious clarify/grounding gate in some phrasings.
- `Q207`: first-month risks still chooses a service/credentials bundle that is semantically close but not rubric-perfect.
- `Q219`: no-match now lands on the correct route but wording still scores `80`.
- Latency remains much higher than the other non-CrewAI paths even after the pilot refresh.

## Next Best Improvements

1. Shared protected follow-up memory:
   carry forward the selected protected student across academic aggregate -> single-student follow-up.
2. Shared family-finance aggregate routing:
   add a dedicated aggregate-first lane before support/protocol status handling.
3. LlamaIndex public-depth routing:
   reduce `contextual_public_direct_answer` for deeper public-document prompts and prefer canonical/public hybrid bundles.
4. Specialist public bundle ordering:
   route family-new, process-compare and first-month prompts earlier in tool-first/preflight.
5. Restricted no-match wording:
   make all paths answer with the exact negative pattern expected by the eval rubric when no restricted evidence exists.
