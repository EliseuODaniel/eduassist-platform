# Final Polish And LLM-Forced Assessment

Date: `2026-04-03`

## Objective

Validate the new state-of-the-art final output architecture:

- shared `final polish` policy
- stack-specific execution
- deterministic answers skipped by policy
- eval-only `llm-forced` mode for controlled diagnostics

This assessment compares:

- normal product behavior
- `llm-forced` behavior that disables canonical shortcuts where safe and pushes the stack toward model-backed composition

## Artifacts

- [normal vs forced four-path report (normal)](/home/edann/projects/eduassist-platform/docs/architecture/retrieval-10q-llm-targeted-normal-vs-forced-normal-20260403.md)
- [normal vs forced four-path report (forced)](/home/edann/projects/eduassist-platform/docs/architecture/retrieval-10q-llm-targeted-normal-vs-forced-forced-20260403.md)
- [langgraph isolated normal vs forced report](/home/edann/projects/eduassist-platform/docs/architecture/langgraph-10q-normal-vs-forced-20260403.md)

Dataset:

- [retrieval_10q_llm_targeted.generated.20260403.json](/home/edann/projects/eduassist-platform/tests/evals/datasets/retrieval_10q_llm_targeted.generated.20260403.json)

## Real Runtime Smoke

`/v1/messages/respond` was exercised against the live local stack after rebuild.

Observed:

- the response payload exposes `used_llm`, `llm_stages`, and `final_polish_*` metadata
- normal mode stayed on deterministic behavior for the smoke prompt
- forced mode changed routing behavior only when the stack truly had a model-backed branch available

## Four-Path Comparison

### Normal

- `langgraph`: `10/10`, quality `92.0`, avg latency `365.9 ms`, `used_llm 0/10`
- `python_functions`: `10/10`, quality `92.0`, avg latency `322.4 ms`, `used_llm 0/10`
- `llamaindex`: `10/10`, quality `92.0`, avg latency `208.4 ms`, `used_llm 0/10`
- `specialist_supervisor`: `10/10`, quality `92.0`, avg latency `0.3 ms`, `used_llm 0/10`

### LLM-forced

- `langgraph`: `10/10`, quality `92.0`, avg latency `324.9 ms`, `used_llm 0/10`
- `python_functions`: `10/10`, quality `88.0`, avg latency `3221.9 ms`, `used_llm 7/10`
- `llamaindex`: `10/10`, quality `86.0`, avg latency `9904.4 ms`, `used_llm 8/10`
- `specialist_supervisor`: `10/10`, quality `87.2`, avg latency `9475.0 ms`, `used_llm 3/10`

## LangGraph Isolated Recheck

After removing the remaining canonical-lane short-circuit from the main runtime only under `llm-forced`, the isolated rerun showed:

- normal: `10/10`, quality `92.0`, avg latency `251.6 ms`, `used_llm 0/10`
- forced: `10/10`, quality `88.0`, avg latency `5660.5 ms`, `used_llm 9/10`

This confirms that the `llm-forced` switch now penetrates the `langgraph` path as intended.

## Findings

1. The final-polish architecture is correct.

Normal mode continues to preserve the system's strongest behavior:

- deterministic/canonical answers remain fast
- model usage is avoided when it adds no value
- product quality remains stable

2. Forcing more LLM usage makes the product worse.

Across the benchmark, the forced mode:

- increased latency dramatically
- reduced quality in three of the four stacks
- re-exposed operational fragility in premium/model-heavy paths

3. `llm-forced` is valuable as a diagnostic mode, not as a serving policy.

It successfully exposes:

- `llamaindex` workflow fragility and long-tail latency
- `specialist_supervisor` pilot instability and fallback behavior
- the quality gap between canonical deterministic answers and model-heavy paraphrasing

4. The specialist path is best when it stays local for canonical public answers.

When forced deeper into the remote pilot, it re-opened:

- `ReadTimeout`
- `500` responses from `/v1/respond-raw`
- costly fallback to `langgraph`

5. The llamaindex path still needs reliability hardening under stress.

The forced mode surfaced:

- very high latency
- workflow cancellation churn
- quality loss when the path leaves its canonical/document-summary strengths

## Architecture Conclusion

The gold-standard design for this repo is:

- shared output policy
- no mandatory final rewrite
- conditional polish only
- rollback-safe postprocessing
- stack-specific execution
- `llm-forced` available only for evaluation and diagnosis

The benchmark evidence does not support universal final LLM rewriting.

Instead, it supports:

- deterministic-first product behavior
- model-backed composition only where it materially improves the answer
- explicit observability of `used_llm`, `llm_stages`, and `final_polish_*`

## Recommended Next Step

The next high-value follow-up is not broader rollout.

It is:

1. keep `llm-forced` as an eval-only feature
2. harden `llamaindex` and `specialist_supervisor` under forced stress
3. preserve the current normal-mode policy as the production default
