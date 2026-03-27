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

Current recommended canary slices from the scorecard:

- `support`
- `workflow`
- `public`

Current blocked slice from the scorecard:

- `protected`

Artifacts:

- [framework-native-scorecard.md](/home/edann/projects/eduassist-platform/docs/architecture/framework-native-scorecard.md)
- [framework-native-scorecard.json](/home/edann/projects/eduassist-platform/docs/architecture/framework-native-scorecard.json)

Runtime default path:

- `/workspace/artifacts/framework-native-scorecard.json`
