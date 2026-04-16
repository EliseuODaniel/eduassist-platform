# SOTA Chatbot Hardening Manual Analysis

Date: 2026-04-16

Branch: `feat/sota-chatbot-hardening-30q-x6`

Status: final

## Purpose

This note captures the human reading of the final chatbot hardening wave beyond automated rubric scores.

## Manual Reading Principles

- answers must adapt to the original user question rather than dump a generic fact block;
- protected answers must stay deterministic and auditable;
- public grounded answers should stay human and specific without hallucinating;
- open-world questions should be declined clearly without swallowing legitimate school-domain requests;
- cross-stack comparison should remain fair on task and policy, not on internal implementation symmetry.

## Final 60Q Reading

The final `60Q` run confirmed that the project is no longer dominated by “obvious chatbot mistakes”. The four stacks answered the broad benchmark with full keyword pass and `quality 100.0`, which means the remaining issues after that point were not about missing basic school facts, broken auth boundaries or weak protected determinism.

From a human reading perspective:

- answers adapted well to the original question instead of just dumping a generic fact block;
- protected answers stayed deterministic, specific and audit-friendly;
- public grounded answers became noticeably less robotic after the grounded answer composer and semantic-router hardening waves;
- the strongest remaining differences between stacks became style, latency and resilience, not correctness.

## Final 40Q Stress Reading

The final valid `40Q` stress run is strong enough to support a nuanced conclusion.

What improved:

- the earlier false `scope_boundary` on the calendar-family bundle disappeared as a functional issue;
- the public known-unknown minimum-age answer became aligned across all stacks and now mentions `admissions` when the user explicitly frames the question that way;
- the invalid stress artifact generated during rollout was clearly separated from the valid result, which keeps the closing interpretation methodologically honest.

What the valid run shows:

- `specialist_supervisor` is the most robust stack under load by a large margin;
- `langgraph`, `python_functions` and `llamaindex` remain solid at low and moderate concurrency;
- at high concurrency, the residual failures cluster on public multi-document or policy-heavy prompts, not on protected SQL-backed flows.

This matters because it changes the interpretation of the problem. The next bottleneck is not “the chatbot still does not understand users well enough”. The next bottleneck is “the non-specialist public bundle paths still saturate under heavier parallelism”.

## Residual UX Notes

Residual UX observations that remain acceptable as next-phase work:

- the non-specialist stacks are still more vulnerable to long public bundle composition under high concurrency;
- some public answers outside the `specialist` still lean slightly more formal or documentary than the most human-like phrasing;
- `specialist_supervisor` remains the closest to a “human concierge” answer style, while the others are now better interpreted as high-quality deterministic/grounded paths.

These are improvement opportunities, not blockers for the closing assessment of this hardening wave.

## Closing Assessment

Closing assessment:

- yes, the four stacks reached the intended gold-standard bar for this hardening wave on correctness, policy safety, groundedness and comparative fairness;
- no, that does not mean all four stacks are equally strong under concurrency pressure;
- the final benchmark state is mature enough to move from semantic hardening into throughput and operational resilience work.

In practical terms, the chatbot architecture is now in a good place to stop chasing isolated wording defects and start treating load behavior, queueing and public-bundle scaling as the main frontier for the next phase.
