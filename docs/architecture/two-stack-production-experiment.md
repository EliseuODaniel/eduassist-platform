# Two-Stack Production Experiment

The production canary is implemented in the main orchestrator and is disabled by default.

The primary stack is now also controllable by feature flag:

- `FEATURE_FLAG_PRIMARY_ORCHESTRATION_STACK=langgraph|crewai`

## Goals

- keep `LangGraph` as the safe default
- allow a narrow `CrewAI` primary experiment by slice
- make rollout deterministic by conversation
- avoid accidental global cutover

## Current Controls

Environment variables in `ai-orchestrator`:

- `FEATURE_FLAG_PRIMARY_ORCHESTRATION_STACK`
- `ORCHESTRATOR_EXPERIMENT_ENABLED`
- `ORCHESTRATOR_EXPERIMENT_PRIMARY_ENGINE`
- `ORCHESTRATOR_EXPERIMENT_SLICES`
- `ORCHESTRATOR_EXPERIMENT_ROLLOUT_PERCENT`
- `ORCHESTRATOR_EXPERIMENT_SLICE_ROLLOUTS`
- `ORCHESTRATOR_EXPERIMENT_TELEGRAM_CHAT_ALLOWLIST`
- `ORCHESTRATOR_EXPERIMENT_CONVERSATION_ALLOWLIST`
- `ORCHESTRATOR_EXPERIMENT_ALLOWLIST_SLICES`
- `ORCHESTRATOR_EXPERIMENT_REQUIRE_SCORECARD`
- `ORCHESTRATOR_EXPERIMENT_SCORECARD_PATH`
- `ORCHESTRATOR_EXPERIMENT_MIN_PRIMARY_ENGINE_SCORE`
- `ORCHESTRATOR_EXPERIMENT_REQUIRE_HEALTHY_PILOT`
- `ORCHESTRATOR_EXPERIMENT_HEALTH_TTL_SECONDS`

The runtime exposes these flags in:

- [main.py](/home/edann/projects/eduassist-platform/apps/ai-orchestrator/src/ai_orchestrator/main.py)
- `/meta`
- `/v1/status`

## Selection Rules

- the primary stack is resolved from `FEATURE_FLAG_PRIMARY_ORCHESTRATION_STACK` first, then falls back to `ORCHESTRATOR_ENGINE`
- the experiment only applies when the resolved primary stack is `langgraph`
- the pilot URL must be configured
- the request slice must match `ORCHESTRATOR_EXPERIMENT_SLICES`
- if an allowlist is configured for the slice, the request must match it
- rollout is deterministic by hashed conversation bucket
- conversation affinity can keep follow-up turns in the same experiment slice for `support` and `workflow`
- per-slice rollout overrides can be applied through `ORCHESTRATOR_EXPERIMENT_SLICE_ROLLOUTS`
- when enabled, a scorecard artifact and a healthy CrewAI pilot can be required before the selector routes traffic

## Recommended First Canary

Start with one of these:

- `support` at `5%`
- `public` at `1%`

Avoid starting with:

- `protected`
- mixed multi-intent traffic
- broad traffic without allowlist

## Example Safe Start

```env
FEATURE_FLAG_PRIMARY_ORCHESTRATION_STACK=langgraph
ORCHESTRATOR_ENGINE=langgraph
CREWAI_PILOT_URL=http://ai-orchestrator-crewai:8000
ORCHESTRATOR_EXPERIMENT_ENABLED=true
ORCHESTRATOR_EXPERIMENT_PRIMARY_ENGINE=crewai
ORCHESTRATOR_EXPERIMENT_SLICES=support,public
ORCHESTRATOR_EXPERIMENT_ROLLOUT_PERCENT=0
ORCHESTRATOR_EXPERIMENT_SLICE_ROLLOUTS=support:100,public:1
ORCHESTRATOR_EXPERIMENT_TELEGRAM_CHAT_ALLOWLIST=1649845499
ORCHESTRATOR_EXPERIMENT_ALLOWLIST_SLICES=support
ORCHESTRATOR_EXPERIMENT_REQUIRE_SCORECARD=true
ORCHESTRATOR_EXPERIMENT_SCORECARD_PATH=/workspace/artifacts/framework-native-scorecard.json
ORCHESTRATOR_EXPERIMENT_MIN_PRIMARY_ENGINE_SCORE=20
ORCHESTRATOR_EXPERIMENT_REQUIRE_HEALTHY_PILOT=true
ORCHESTRATOR_EXPERIMENT_HEALTH_TTL_SECONDS=15
```

## Operational Reading

- if the slice is not enrolled, the baseline stays primary
- if the slice is enrolled, the CrewAI pilot becomes primary for that request
- if a support/workflow conversation is already enrolled, follow-up turns can stay on that slice even when the wording becomes short or ambiguous
- the final runtime trace keeps the chosen `engine_name` and `engine_mode`
- `/v1/status` now also exposes:
  - `primaryStackFeatureFlag`
  - `resolvedPrimaryStack`
  - `experimentScorecardGate`

## Native-Path Rule

When `FEATURE_FLAG_PRIMARY_ORCHESTRATION_STACK=crewai`, the primary response path must stay native to the CrewAI side:

- `Flow` remains the primary state machine
- task/listener metadata remains the primary trace surface
- the main orchestrator must not invoke the LangGraph runtime just to shape preview, graph path, or suggested replies

LangGraph remains available as:

- explicit fallback if the CrewAI primary call fails
- the separate baseline when the feature flag resolves to `langgraph`

## Current Recommendation

- keep `support` controlled first, then open `public` with a tiny percentage
- after `workflow` reaches parity in replay and latency stays stable, open `workflow` in allowlisted canary before any broader rollout
- use allowlist scoping so `support` and `workflow` can stay controlled while `public` rolls out slowly

## Recommended Next Safe Step

```env
ORCHESTRATOR_ENGINE=langgraph
CREWAI_PILOT_URL=http://ai-orchestrator-crewai:8000
ORCHESTRATOR_EXPERIMENT_ENABLED=true
ORCHESTRATOR_EXPERIMENT_PRIMARY_ENGINE=crewai
ORCHESTRATOR_EXPERIMENT_SLICES=support,public,workflow
ORCHESTRATOR_EXPERIMENT_ROLLOUT_PERCENT=0
ORCHESTRATOR_EXPERIMENT_SLICE_ROLLOUTS=support:100,public:1,workflow:100
ORCHESTRATOR_EXPERIMENT_TELEGRAM_CHAT_ALLOWLIST=1649845499
ORCHESTRATOR_EXPERIMENT_ALLOWLIST_SLICES=support,workflow
```

This keeps:

- `support` fully controlled on the allowlisted chat
- `workflow` fully controlled on the allowlisted chat
- `public` still tiny and gradual

## Promotion Gate

The current master replay keeps the promotion rule simple:

- `support`: allowed for controlled canary
- `workflow`: allowed for controlled canary
- `public`: allowed for tiny gradual rollout
- `protected`: **not** promoted yet

Reason:

- `protected` is back at replay parity in the current master benchmark
- even so, `protected` carries the highest sensitivity because it handles identity, grades, documentation, and finance
- before any protected canary, we still want a dedicated live gate with stricter review of auth, student focus, and leakage risk
- until that gate is explicitly opened, canary scope stays limited to `support`, `public`, and `workflow`

## Scorecard-Backed Promotion Gate

The selector can now read a runtime-visible scorecard artifact and combine it with pilot health.

The scorecard now also requires proof that the selected framework can run as the true primary path under `FEATURE_FLAG_PRIMARY_ORCHESTRATION_STACK`, using the versioned benchmark in [framework-primary-stack-flag-report.md](/home/edann/projects/eduassist-platform/docs/architecture/framework-primary-stack-flag-report.md).

Current recommended canary slices from the scorecard:

- `support`
- `workflow`
- `public`

Current blocked slice from the scorecard:

- `protected`

The runtime status surface now exposes the resolved scorecard gate, including per-slice eligibility and reasons:

- `/v1/status -> experimentScorecardGate`
- `/meta -> experimentScorecardGate`

The runtime also exposes a rollout-oriented summary of the current configuration and what can be promoted now:

- `/v1/status -> experimentRolloutReadiness`
- `/meta -> experimentRolloutReadiness`

The runtime also exposes a live promotion summary that combines current config, pilot health, and gate state into an action per slice:

- `/v1/status -> experimentLivePromotionSummary`
- `/meta -> experimentLivePromotionSummary`

Versioned operational snapshot:

- [framework-rollout-readiness-report.md](/home/edann/projects/eduassist-platform/docs/architecture/framework-rollout-readiness-report.md)
- [framework-live-promotion-summary-report.md](/home/edann/projects/eduassist-platform/docs/architecture/framework-live-promotion-summary-report.md)

## Rollout Preflight

Before applying any rollout change, run the preflight script against the proposed config.

Example:

```bash
python3 tools/evals/preflight_framework_rollout_promotion.py \
  --slices support,public,workflow \
  --slice-rollouts support:100,public:2,workflow:100 \
  --allowlist-slices support,workflow
```

Versioned example output:

- [framework-rollout-preflight-report.md](/home/edann/projects/eduassist-platform/docs/architecture/framework-rollout-preflight-report.md)

Expected use:

- reject a proposed change if any requested live slice is blocked
- approve a small public expansion only when the live summary keeps `public` on `expand_gradually`
- maintain `support/workflow` under allowlist control unless the scorecard and live signals change

## Rollout Apply

After a proposal is approved, use the apply script to mutate an env file only through the same preflight gate.

Safe validation example against a temporary env copy:

```bash
cp .env artifacts/tmp-rollout.env
python3 tools/evals/apply_framework_rollout_promotion.py \
  --env-file artifacts/tmp-rollout.env \
  --slices support,public,workflow \
  --slice-rollouts support:100,public:2,workflow:100 \
  --allowlist-slices support,workflow \
  --apply
```

Versioned example output:

- [framework-rollout-apply-report.md](/home/edann/projects/eduassist-platform/docs/architecture/framework-rollout-apply-report.md)

Expected use:

- never mutate the real env file without a successful preflight verdict
- keep a backup snapshot of the previous env before writing
- use the apply report as the audited record of what changed

## Rollout Execute

For a full operational run, use the execution script to:

- preflight the proposal
- apply it to the target env file
- restart only the required services
- validate the live `/v1/status`
- register a post-apply execution report

Safe validation example:

```bash
cp .env artifacts/tmp-execution.env
python3 tools/evals/execute_framework_rollout_promotion.py \
  --env-file artifacts/tmp-execution.env \
  --services ai-orchestrator \
  --apply
```

Versioned example output:

- [framework-rollout-execution-report.md](/home/edann/projects/eduassist-platform/docs/architecture/framework-rollout-execution-report.md)

## Slice Promotion Wrapper

For the safest day-to-day operation, prefer the slice wrapper instead of hand-writing rollout strings.

Dry-run example:

```bash
cp .env artifacts/tmp-slice.env
python3 tools/evals/promote_framework_slice.py \
  --env-file artifacts/tmp-slice.env \
  --slice public \
  --to-rollout-percent 2 \
  --reason "Expandir public de 1% para 2% apos estabilidade do canario"
```

This wrapper:

- calculates `before` and `after` automatically
- preserves the other configured slices
- adjusts allowlist scope safely in `auto` mode
- requires an explicit operational reason
- records every attempt in the rollout changelog

Artifacts:

- [framework-slice-promotion-report.md](/home/edann/projects/eduassist-platform/docs/architecture/framework-slice-promotion-report.md)
- [framework-rollout-changelog.md](/home/edann/projects/eduassist-platform/docs/architecture/framework-rollout-changelog.md)

## Slice Rollback Wrapper

Rollback uses the same audited path as promotion.

Safe dry-run example using the changelog as the target source:

```bash
cp .env artifacts/tmp-rollback.env
python3 tools/evals/rollback_framework_slice.py \
  --env-file artifacts/tmp-rollback.env \
  --slice public \
  --reason "Reverter public para o nivel anterior do canario" \
  --operator codex \
  --allow-preflight-fallback
```

Artifacts:

- [framework-slice-rollback-report.md](/home/edann/projects/eduassist-platform/docs/architecture/framework-slice-rollback-report.md)

## Changelog Normalization

Legacy rollout entries can now be normalized to the current audit contract before merge or release:

```bash
python3 tools/evals/normalize_framework_rollout_changelog.py
```

Artifacts:

- [framework-rollout-changelog-normalization-report.md](/home/edann/projects/eduassist-platform/docs/architecture/framework-rollout-changelog-normalization-report.md)

## Release Snapshot

Before merge or a broader rollout decision, generate one consolidated release snapshot:

```bash
python3 tools/evals/build_framework_release_snapshot.py
```

Artifacts:

- [framework-release-snapshot-report.md](/home/edann/projects/eduassist-platform/docs/architecture/framework-release-snapshot-report.md)

This snapshot consolidates:

- git cleanliness
- live `/v1/status`
- orchestrator and pilot health
- current rollout posture
- latest audited rollout entries

## Merge / Release Checklist

Before merge or guarded promotion, run the checklist that verifies snapshot freshness, health, scorecard gates, and changelog hygiene:

```bash
python3 tools/evals/build_framework_merge_release_checklist.py
```

Artifacts:

- [framework-merge-release-checklist-report.md](/home/edann/projects/eduassist-platform/docs/architecture/framework-merge-release-checklist-report.md)

## Recommended Slice Promotion

When the live summary already points to a clear next slice, prefer the recommendation wrapper instead of manually choosing the target:

```bash
cp .env artifacts/tmp-recommended.env
python3 tools/evals/promote_recommended_framework_slice.py \
  --env-file artifacts/tmp-recommended.env \
  --reason "Aplicar a proxima promocao sugerida pelo gate operacional" \
  --operator codex
```

This wrapper:

- reads the same live promotion summary and scorecard gate already exposed by the runtime
- chooses the next promotable slice using the current advisory state
- computes the next rollout step conservatively
- reuses the audited slice wrapper underneath, preserving the same changelog and reports

Artifacts:

- [framework-recommended-slice-promotion-report.md](/home/edann/projects/eduassist-platform/docs/architecture/framework-recommended-slice-promotion-report.md)

Artifacts:

- [framework-native-scorecard.md](/home/edann/projects/eduassist-platform/docs/architecture/framework-native-scorecard.md)
- [framework-native-scorecard.json](/home/edann/projects/eduassist-platform/docs/architecture/framework-native-scorecard.json)

Runtime default path:

- `/workspace/artifacts/framework-native-scorecard.json`

## Primary-Stack Regression

The primary-stack feature flag now has a dedicated regression benchmark to verify that either framework can become the true primary path without leaking the alternate framework runtime metadata.

Artifacts:

- [framework-primary-stack-flag-report.md](/home/edann/projects/eduassist-platform/docs/architecture/framework-primary-stack-flag-report.md)
- [framework_primary_stack_flag_cases.json](/home/edann/projects/eduassist-platform/tests/evals/datasets/framework_primary_stack_flag_cases.json)
- [benchmark_primary_stack_feature_flag.py](/home/edann/projects/eduassist-platform/tools/evals/benchmark_primary_stack_feature_flag.py)

Current expectation:

- `FEATURE_FLAG_PRIMARY_ORCHESTRATION_STACK=crewai|langgraph`
- `ORCHESTRATOR_EXPERIMENT_ENABLED=false`
- `engine_name` and `engine_mode` match the selected primary stack
- no alternate-framework request metadata in the canonical trace for those primary-path runs
