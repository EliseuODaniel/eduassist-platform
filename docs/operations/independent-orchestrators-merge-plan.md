# Merge Plan For `feature/independent-orchestrators`

## Goal

Turn the current local branch into a mergeable sequence of small, explainable publication units for `main`, without mixing runtime logic, eval evidence, generated reports, and docs into a single unclear change.

## Current State

The branch is technically ahead of `main` for the dedicated-first architecture, but the worktree still mixes:

- runtime and serving logic
- compose and ops changes
- eval tooling
- unit and E2E coverage
- generated benchmark waves and replay reports

This plan treats merge readiness as a Git hygiene problem, not a product-quality problem.

## What Should Ship

### Slice 1. Dedicated-first architecture

Include:

- dedicated runtime entrypoints
- shared control-plane guards
- serving policy and telemetry
- stack-local runtime settings
- debug footer and reply formatting
- shared public-knowledge/runtime helpers that are part of the product path

Examples:

- `apps/ai-orchestrator/src/ai_orchestrator/main.py`
- `apps/ai-orchestrator/src/ai_orchestrator/dedicated_stack_app.py`
- `apps/ai-orchestrator/src/ai_orchestrator/service_settings.py`
- `apps/ai-orchestrator/src/ai_orchestrator/serving_policy.py`
- `apps/ai-orchestrator/src/ai_orchestrator/serving_telemetry.py`
- `apps/ai-orchestrator/src/ai_orchestrator/stack_runtime_profiles.py`

### Slice 2. Specialist and stack-quality improvements

Include:

- specialist runtime modules and quality fixes
- routing, retrieval, answer-experience, and follow-up fixes that materially improve the 4 dedicated paths

Examples:

- `apps/ai-orchestrator-specialist/src/ai_orchestrator_specialist/*`
- `apps/ai-orchestrator/src/ai_orchestrator/runtime.py`
- `apps/ai-orchestrator/src/ai_orchestrator/retrieval.py`
- `apps/ai-orchestrator/src/ai_orchestrator/grounded_answer_experience.py`
- `apps/ai-orchestrator/src/ai_orchestrator/*_public_knowledge.py`

### Slice 3. Dedicated-first ops and compose

Include:

- `compose` changes
- tunnel/webhook tooling
- Makefile dedicated-first targets
- runtime parity and gateway smoke helpers

Examples:

- `infra/compose/compose.yaml`
- `infra/compose/cloudflared/*`
- `infra/compose/telegram-*.override.yaml`
- `tools/ops/telegram_webhook.py`
- `Makefile`

### Slice 4. Tests and eval tooling

Include:

- unit tests
- dedicated E2E smoke and multi-turn
- dedicated runtime parity and gateway smoke
- eval runners and tooling needed to keep the branch maintainable

Examples:

- `tests/unit/*`
- `tests/e2e/*`
- `tests/evals/dedicated_runtime_quality.py`
- `tests/evals/datasets/dedicated_runtime_cases.json`
- `tools/evals/*`

### Slice 5. Docs

Include only curated documentation that explains the architecture and operation:

- `README.md`
- `docs/operations/local-development.md`
- `tests/README.md`
- any explicit TCC or architecture doc that is intentionally curated, not generated

## What Should Not Ship In The Merge PR

Unless explicitly requested as evidence:

- generated benchmark waves in `docs/architecture/independent-orchestrators-*`
- generated replay reports
- generated probe datasets with `.generated.` in the filename
- local runtime artifacts under `artifacts/`

These files are useful locally, but they should not be mixed into the core merge by default.

## Recommended Commit Sequence

1. `Refactor control plane into dedicated-first serving model`
2. `Improve dedicated runtimes and specialist quality paths`
3. `Harden dedicated-first ops, tunnel, and webhook tooling`
4. `Add dedicated-first unit, E2E, and parity coverage`
5. `Update docs for dedicated-first architecture`

## Validation Before Opening The PR

Run:

```bash
make smoke-dedicated
make smoke-dedicated-multiturn
make smoke-telegram-dedicated
make runtime-parity-check
```

If the PR includes control-plane compatibility changes, also run:

```bash
make compose-up-control-plane-compat
make smoke-local
```

## Merge Recommendation

Do not merge from the current dirty worktree as-is.

Merge when:

- generated waves are excluded from scope
- the remaining code and docs are sliced into the commit sequence above
- the dedicated-first validations are rerun on the exact commit set that will be published
