# Retrieval 20Q Five-Path Diagnosis

Date: 2026-04-02

This diagnosis consolidates the first-pass `python_functions` vs `specialist_supervisor` run with the follow-up run for `langgraph`, `crewai`, and `llamaindex`, all using the same 20-question probe dataset in [retrieval_20q_probe_cases.json](/home/edann/projects/eduassist-platform/tests/evals/datasets/retrieval_20q_probe_cases.json).

Source artifacts:
- [retrieval-20q-followup-fixes.md](/home/edann/projects/eduassist-platform/docs/architecture/retrieval-20q-followup-fixes.md)
- [retrieval-20q-python-functions-specialist-report.md](/home/edann/projects/eduassist-platform/docs/architecture/retrieval-20q-python-functions-specialist-report.md)
- [retrieval-20q-python-functions-specialist-report.json](/home/edann/projects/eduassist-platform/docs/architecture/retrieval-20q-python-functions-specialist-report.json)
- [retrieval-20q-remaining-paths-report.md](/home/edann/projects/eduassist-platform/docs/architecture/retrieval-20q-remaining-paths-report.md)
- [retrieval-20q-remaining-paths-report.json](/home/edann/projects/eduassist-platform/docs/architecture/retrieval-20q-remaining-paths-report.json)

## Scoreboard

| Path | OK | Keyword pass | Quality | Avg latency |
| --- | --- | --- | --- | --- |
| `python_functions` | `19/20` | `6/20` | `78.5` | `354.2 ms` |
| `specialist_supervisor` | `20/20` | `11/20` | `89.8` | `13428.5 ms` |
| `langgraph` | `20/20` | `6/20` | `83.2` | `2502.8 ms` |
| `crewai` | `20/20` | `5/20` | `80.3` | `7860.8 ms` |
| `llamaindex` | `19/20` | `6/20` | `79.7` | `6271.6 ms` |

## Executive Read

- `specialist_supervisor` had the strongest semantic coverage, especially on protected context retention and deny behavior for restricted documents, but the run was heavily distorted by source-mode operational degradation and very high latency.
- `python_functions` remained the most efficient path by far and stayed strong on deterministic public and tool-first retrieval, but it over-clarified too often and still has a shared crash on `Q205`.
- `langgraph` was more robust than `crewai` and `llamaindex`, but it still leaned too hard into structured/canonical paths on deep public prompts and mishandled the restricted deny case.
- `crewai` underperformed on retrieval-heavy probes. It denied or timed out on several public and restricted cases and never exercised real retrieval in this battery.
- `llamaindex` was competitive on simple public retrieval and some restricted positive cases, but it shared the `Q205` crash and remained too clarification-prone on protected follow-ups.

## Cross-Path Findings

### 1. `Q205` is a shared kernel contract bug

Two paths crashed on the same question:
- `python_functions`
- `llamaindex`

Both failed with a `KernelRunResult` validation error missing:
- `plan`
- `reflection`
- `response`

This indicates a shared canonical-public response path is returning an incomplete payload for the permanence/family-support bundle.

### 2. Deep public multi-doc is still too canonicalized

The deep public probes (`Q208`, `Q211`) were weak across all paths:
- `python_functions`, `langgraph`, and `llamaindex` tended to collapse to canonical public answers
- `specialist_supervisor` improved quality but still clarified on `Q211`
- `crewai` stayed shallow or denied

This suggests the new retrieval stack is stronger, but the runtime planners still over-prefer deterministic public bundles even when the prompt asks for multi-document synthesis.

### 3. Restricted positive internal-document retrieval is not solved yet

The positive restricted-doc probes (`Q216`–`Q218`) showed no consistently strong path:
- `specialist_supervisor`: all three degraded to `restricted_document_no_match`
- `python_functions`: clarify or route to structured academic instead of internal-doc retrieval
- `langgraph`: clarify or structured-tool substitution
- `crewai`: deny, timeout, or workflow mismatch
- `llamaindex`: partial positive behavior, but only `1/3` keyword pass

The stack can deny restricted access, but positive retrieval of internal documents remains weak.

### 4. Restricted deny is still fragile outside path 5

`Q220` was the strongest evidence:
- `specialist_supervisor` was the only path that passed cleanly in the first-pass run
- `langgraph` and `crewai` produced very low-quality responses (`23.0`)
- `python_functions` and `llamaindex` clarified when a deny was expected

So the system is much better at "public vs protected" than at "allowed restricted vs denied restricted."

### 5. Operational maturity still matters as much as retrieval logic

The path 5 run surfaced repeated operational failures:
- `specialist_orchestrator_preview_unavailable`
- `specialist_orchestrator_retrieval_unavailable`
- `specialist_orchestrator_graphrag_unavailable`
- `MaxTurnsExceeded`

These did not fully collapse quality, but they massively inflated latency and make path-to-path comparison less fair until the local dependencies are hardened.

## Path-by-Path Follow-Up

### `python_functions`

Strengths:
- best latency by a large margin
- strong deterministic public answers
- strong tool-first behavior

Main problems:
- `Q205` crash
- over-clarification on `Q212`, `Q213`, `Q214`, `Q216`, `Q220`
- misrouting on `Q215`
- shallow answers on public deep/section-aware prompts

Best next improvements:
- fix the shared `Q205` kernel payload bug
- reduce protected clarification when thread context is already sufficient
- add explicit restricted-positive doc routing
- allow deeper retrieval profiles for public multi-doc prompts before falling back to canonical public bundles

### `specialist_supervisor`

Strengths:
- best semantic coverage in this battery
- best handling of protected follow-up context
- correct deny behavior on restricted denied content

Main problems:
- extremely high latency in this run
- local operational degradation
- all three restricted positive internal-doc probes came back as `no_match`
- still clarifies on some deep public prompts

Best next improvements:
- harden local source-mode dependencies so quality is not paid for with operational fragility
- fix restricted-positive internal-doc matching
- let deep public non-canonical prompts escalate into richer retrieval before the grounding gate clarifies

### `langgraph`

Strengths:
- no hard crashes
- better latency than `crewai` and `llamaindex`
- reasonable overall robustness

Main problems:
- over-canonicalized public answers on `Q202`, `Q204`, `Q205`, `Q208`, `Q209`, `Q211`
- clarify on protected academic/finance when structured context should have been enough
- very poor restricted deny behavior on `Q220`

Best next improvements:
- widen the retrieval budget for deep public prompts before picking structured public fast paths
- reduce protected clarifications when authenticated context already resolves the target
- add a strict deny lane for restricted-doc requests without proper scope

### `crewai`

Strengths:
- some good protected structured answers
- acceptable performance on a few simple public fast paths

Main problems:
- weakest overall semantic coverage
- very high latency
- public prompts sometimes misclassified as protected (`Q201`, `Q204`, `Q211`)
- timeouts on visibility/finance cases
- no meaningful retrieval behavior surfaced in this run

Best next improvements:
- keep as baseline only
- fix the public/protected boundary misclassification
- reduce timeout fallback noise
- do not invest in deeper retrieval architecture unless project priorities change

### `llamaindex`

Strengths:
- good latency on simple public and some restricted positive cases
- some effective restricted-doc fast-path behavior

Main problems:
- shared `Q205` crash
- too much clarification on protected context retention
- weak deep public synthesis
- high latency spikes on some protected/public cases

Best next improvements:
- fix the shared `Q205` kernel contract bug
- reduce clarification on authenticated follow-ups
- let the native documentary path stay native on deeper public synthesis instead of snapping back to canonical public answers

## Priority Order For Future Fixes

1. Fix the shared `Q205` kernel payload bug affecting `python_functions` and `llamaindex`.
2. Fix restricted positive internal-document retrieval, starting with `specialist_supervisor` and `python_functions`.
3. Add stronger restricted deny lanes for `langgraph`, `python_functions`, and `llamaindex`.
4. Reduce unnecessary clarification in protected flows across `python_functions`, `langgraph`, and `llamaindex`.
5. Rebalance public deep multi-doc routing so canonical public bundles do not suppress valid retrieval synthesis.
6. Harden `specialist_supervisor` source-mode dependencies before using this battery as a latency benchmark again.

## Practical Conclusion

The new retrieval stack improvements are already visible: the system is better at public deterministic answers, hybrid retrieval, and section-aware/document-aware context than before. But the 20-question battery shows the next ceiling clearly:

- the hardest remaining problem is not basic public retrieval
- it is the boundary between `structured protected data`, `restricted internal documents`, and `deep multi-document public synthesis`

That is where the next round of engineering will pay off most.
