# SOTA Chatbot Hardening Closeout

Date: 2026-04-16

Branch: `feat/sota-chatbot-hardening-30q-x6`

Status: final

## Scope

This closeout captures the final state of the multi-cycle chatbot hardening wave that pushed the four benchmarked stacks toward a gold-standard operating baseline under Gemma:

- `langgraph`
- `python_functions`
- `llamaindex`
- `specialist_supervisor`

It consolidates:

- the final broad `60Q` quality run;
- the final `40Q` stress run with concurrency levels `1, 2, 4`;
- the architectural changes that generalized fixes across stacks;
- the remaining operational gaps that should be treated as next-phase work instead of stack-specific patches.

## Final Broad 60Q

Final quality validation for the broadened `60Q` battery was recorded in:

- [retrieval-broad-60q-final-cross-path-report.md](/home/edann/projects/eduassist-platform/docs/architecture/retrieval-broad-60q-final-cross-path-report.md)
- [retrieval-broad-60q-final-combined-evaluation-report.md](/home/edann/projects/eduassist-platform/docs/architecture/retrieval-broad-60q-final-combined-evaluation-report.md)
- [retrieval-broad-60q-final-trace-calibration-report.md](/home/edann/projects/eduassist-platform/docs/architecture/retrieval-broad-60q-final-trace-calibration-report.md)

The final broad run closed at full quality across the four benchmarked stacks:

| Stack | OK | Keyword pass | Quality | Avg latency |
| --- | --- | --- | --- | --- |
| `langgraph` | `60/60` | `60/60` | `100.0` | `2564.4 ms` |
| `python_functions` | `60/60` | `60/60` | `100.0` | `3768.5 ms` |
| `llamaindex` | `60/60` | `60/60` | `100.0` | `3413.0 ms` |
| `specialist_supervisor` | `60/60` | `60/60` | `100.0` | `524.7 ms` |

This mattered for the hardening wave because it established that the residual work was no longer about broad correctness or policy alignment. After the `60Q` closure, the remaining work shifted to:

- concurrency robustness;
- queueing pressure on public multi-document answers;
- and final wording gaps that only appeared under stress or niche public-known-unknown slices.

## Stress Method

The final stress battery used the balanced `40Q` suite:

- dataset: `tests/evals/datasets/retrieval_40q_stress_suite.generated.20260416.final.json`
- slices:
  - `16` public
  - `16` protected
  - `8` restricted
- concurrency levels: `1`, `2`, `4`
- timeout budget: `45.0s`
- rounds: `1`
- user/auth context kept aligned with the same fairness rules used in the official four-path comparison runner

The stress harness reused the same scoring helpers as the standard evaluation path:

- status success
- keyword pass
- quality score
- latency distribution
- throughput
- dominant error types

This kept the stress findings directly comparable to the broader quality benchmark instead of turning the load test into a separate ad hoc rubric.

## Invalid Stress Attempt

One intermediate `40Q` stress report was intentionally excluded from final interpretation.

That run was started while the compose rebuild of the non-specialist services was still in progress. The evidence for contamination was direct:

- the report timestamp was earlier than the final `StartedAt` timestamps of the recreated non-specialist containers;
- the non-specialist stacks collapsed to widespread `599 / exception` responses with very low latency;
- the service logs did not show a matching volume of request execution;
- a later sanity check through the same `_run_turn` harness worked normally once the rollout had finished.

In other words, that intermediate artifact measured rollout churn, not chatbot robustness. It was kept as an operational note but not used as the closing stress benchmark.

## Final Stress Findings

The final valid stress run was recorded in:

- [four-path-chatbot-stress-report.md](/home/edann/projects/eduassist-platform/docs/architecture/four-path-chatbot-stress-report.md)
- [four-path-chatbot-stress-report.json](/home/edann/projects/eduassist-platform/docs/architecture/four-path-chatbot-stress-report.json)

Summary:

| Stack | c1 | c2 | c4 |
| --- | --- | --- | --- |
| `langgraph` | `40/40`, quality `100.0`, avg `3779.0 ms` | `40/40`, quality `100.0`, avg `6209.4 ms` | `36/40`, quality `90.0`, avg `8962.7 ms`, p95 `45037.2 ms` |
| `python_functions` | `40/40`, quality `100.0`, avg `4089.3 ms` | `39/40`, quality `97.5`, avg `6940.9 ms`, p95 `37556.7 ms` | `34/40`, quality `85.0`, avg `10969.3 ms`, p95 `45047.8 ms` |
| `llamaindex` | `40/40`, quality `100.0`, avg `3529.4 ms` | `40/40`, quality `100.0`, avg `7073.0 ms` | `35/40`, quality `87.5`, avg `8831.2 ms`, p95 `45037.7 ms` |
| `specialist_supervisor` | `40/40`, quality `100.0`, avg `375.5 ms` | `40/40`, quality `100.0`, avg `365.7 ms` | `40/40`, quality `100.0`, avg `637.4 ms`, p95 `1410.0 ms` |

Interpretation:

- the four stacks now sustain full quality in `c1`;
- `langgraph`, `llamaindex` and `specialist_supervisor` also hold full quality in `c2`;
- `python_functions` shows a small `c2` residual, limited to one request failure;
- under `c4`, the residuals are no longer semantic mismatches or policy leaks; they are concentrated request failures on heavier public documentary bundles in the three non-specialist stacks;
- `specialist_supervisor` remained fully stable at `c4`, with the best latency profile and no residual request failures.

## Architectural Fixes Completed

The closing patch waves of this hardening cycle generalized the remaining issues instead of solving them with stack-local branching:

1. Shared public calendar-family recognition
- public questions such as “Quais eventos publicos para familias e responsaveis aparecem nesta base agora?” were promoted to high-confidence school-scope signals in the semantic ingress layer;
- the canonical public lane matcher was expanded to accept broader calendar-family wording such as “aparecem nesta base agora”.

2. Shared public known-unknown wording
- minimum-age responses were aligned around the same grounded contract across stacks;
- the answer now explicitly references `admissions` when that term is part of the user prompt, instead of only saying `matricula e atendimento comercial`.

3. Retrieval fallback hardening
- restricted lookup fallback expanded beyond the earlier limited retry set;
- semantic finance retries and bigram hints were strengthened to improve restricted documental coverage without resorting to direct model-database access.

4. Explicit open-world boundary handling
- long prompts that explicitly said the request was outside school scope, such as `fora do tema escolar`, were promoted to strong open-world markers;
- this reduced false attempts to answer off-topic prompts as if they were school requests.

5. Family/protected follow-up preservation
- the protected/family routing layers were hardened in prior waves to preserve comparison, attendance, finance aggregation and admin+finance bundle semantics across turns;
- this was one of the key reasons the broad quality benchmark reached `100.0` in all four stacks before the final stress phase.

## Remaining Gaps

After the last valid stress run, the remaining gaps were purely operational and concentrated under concurrency `4`.

Residual cases:

- `T001` `public_academic_policy_overview`
- `T003` `public_calendar_week`
- `T004` `public_conduct_frequency_punctuality`
- `T009` `public_governance_protocol`
- `T011` `public_inclusion_accessibility`
- `T012` `public_integral_study_support`
- `T016` `public_known_unknown_total_teachers`

Observed pattern:

- `langgraph` failed on `T001`, `T003`, `T009`, `T012` at `c4`
- `python_functions` failed on `T009` at `c2`, and on `T001`, `T003`, `T004`, `T011`, `T012`, `T016` at `c4`
- `llamaindex` failed on `T003`, `T004`, `T009`, `T011`, `T016` at `c4`
- `specialist_supervisor` had no residual failures

These failures are best interpreted as queueing and timeout pressure on public, multi-document or policy-heavy answers rather than unresolved routing or grounding defects. This conclusion is supported by two facts:

1. the same categories already closed at `100.0` in the broad `60Q` benchmark;
2. after the last semantic fixes, the earlier functional gaps (`T003` calendar-family bundle and `T015` minimum-age wording) disappeared from the valid stress result.

## Practical Recommendation

Practical recommendation:

1. Treat the hardening wave as functionally closed.
   The four stacks reached the intended quality bar on the broad `60Q` benchmark, and the remaining stress residuals are operational rather than semantic.

2. Keep `specialist_supervisor` as the strongest premium reference path.
   It is now clearly the most resilient path under concurrency pressure while staying grounded and policy-safe.

3. Treat non-specialist `c4` public-bundle failures as the next phase.
   The next step should be throughput and queueing hardening for public multi-document answers, not more turn-level heuristics.

4. Prioritize operational work that generalizes:
- request queueing and backpressure visibility;
- concurrency-aware caching for public documentary bundles;
- selective pre-composition or deterministic short-circuiting for heavy public bundle prompts;
- service-level telemetry around `request_failed` and near-timeout p95 routes.

5. Do not regress fairness by forcing architectural symmetry.
   The closing evidence reinforces the intended design principle of the repo: same task and policy surface, different internal paths when that produces the best final answer.
