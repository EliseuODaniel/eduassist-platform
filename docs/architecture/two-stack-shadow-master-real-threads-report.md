# Two-Stack Shadow Master Report

## Scope

This master view consolidates the validated real-thread shadow reports for:

- `public` + `protected` from [two-stack-shadow-extended-real-threads-report.md](/home/edann/projects/eduassist-platform/docs/architecture/two-stack-shadow-extended-real-threads-report.md)
- `workflow` from [two-stack-shadow-workflow-real-threads-report.md](/home/edann/projects/eduassist-platform/docs/architecture/two-stack-shadow-workflow-real-threads-report.md)
- `support` from [two-stack-shadow-support-real-threads-report.md](/home/edann/projects/eduassist-platform/docs/architecture/two-stack-shadow-support-real-threads-report.md)

This is the current apples-to-apples comparison across the four slices that matter most in the product today.

## Consolidated Summary

- Total prompts covered: `40`
- Baseline total keyword pass: `40/40`
- CrewAI total keyword pass: `40/40`
- Baseline quality average: `100.0`
- CrewAI quality average: `100.0`
- Weighted average latency:
  - baseline: `2196.4ms`
  - CrewAI: `64.8ms`

## By Slice

- `public`
  - prompts: `13`
  - baseline: `13/13`, quality `100.0`, latency `5052.9ms`
  - CrewAI: `13/13`, quality `100.0`, latency `25.9ms`
- `protected`
  - prompts: `13`
  - baseline: `13/13`, quality `100.0`, latency `158.5ms`
  - CrewAI: `13/13`, quality `100.0`, latency `134.0ms`
- `workflow`
  - prompts: `7`
  - baseline: `7/7`, quality `100.0`, latency `2036.5ms`
  - CrewAI: `7/7`, quality `100.0`, latency `39.4ms`
- `support`
  - prompts: `7`
  - baseline: `7/7`, quality `100.0`, latency `835.8ms`
  - CrewAI: `7/7`, quality `100.0`, latency `34.1ms`

## Reading

- `correctness`
  - In the current validated real-thread benchmark, the two stacks are tied.
- `latency`
  - CrewAI is clearly faster in `public`, `workflow`, and `support`.
  - In `protected`, the two are already close.
- `style`
  - Baseline still tends to sound warmer and more product-like.
  - CrewAI still tends to be drier and more telegraphic, although it is now operationally competitive.
- `maturity`
  - Baseline remains the safer production default because it is the primary stack and covers more behavior outside the comparison pilot.
  - CrewAI is now strong enough to be considered a credible comparative engine, not just a stub or lab toy.

## Recommendation

- Keep `LangGraph` as the production default for now.
- Keep `CrewAI` running as the shadow comparison stack.
- Use the current four-slice benchmark as the decision baseline.
- The next promotion decision should depend on broader real-thread coverage, especially:
  - longer mixed-topic conversations
  - broader support and administrative repair
  - cost stability under repeated runs
  - tone quality beyond keyword correctness

## Current Decision

- `production default`: baseline `LangGraph`
- `comparison challenger`: `CrewAI`
- `decision status`: `not ready to replace the baseline globally, but ready for serious comparative evaluation and possibly a slice-specific experiment later`
