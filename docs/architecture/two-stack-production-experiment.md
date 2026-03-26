# Two-Stack Production Experiment

The production canary is implemented in the main orchestrator and is disabled by default.

## Goals

- keep `LangGraph` as the safe default
- allow a narrow `CrewAI` primary experiment by slice
- make rollout deterministic by conversation
- avoid accidental global cutover

## Current Controls

Environment variables in `ai-orchestrator`:

- `ORCHESTRATOR_EXPERIMENT_ENABLED`
- `ORCHESTRATOR_EXPERIMENT_PRIMARY_ENGINE`
- `ORCHESTRATOR_EXPERIMENT_SLICES`
- `ORCHESTRATOR_EXPERIMENT_ROLLOUT_PERCENT`
- `ORCHESTRATOR_EXPERIMENT_TELEGRAM_CHAT_ALLOWLIST`
- `ORCHESTRATOR_EXPERIMENT_CONVERSATION_ALLOWLIST`

The runtime exposes these flags in:

- [main.py](/home/edann/projects/eduassist-platform/apps/ai-orchestrator/src/ai_orchestrator/main.py)
- `/meta`
- `/v1/status`

## Selection Rules

- the experiment only applies when `ORCHESTRATOR_ENGINE=langgraph`
- the pilot URL must be configured
- the request slice must match `ORCHESTRATOR_EXPERIMENT_SLICES`
- if an allowlist is configured, the request must match it
- rollout is deterministic by hashed conversation bucket

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
ORCHESTRATOR_ENGINE=langgraph
CREWAI_PILOT_URL=http://ai-orchestrator-crewai:8000
ORCHESTRATOR_EXPERIMENT_ENABLED=true
ORCHESTRATOR_EXPERIMENT_PRIMARY_ENGINE=crewai
ORCHESTRATOR_EXPERIMENT_SLICES=support
ORCHESTRATOR_EXPERIMENT_ROLLOUT_PERCENT=5
ORCHESTRATOR_EXPERIMENT_TELEGRAM_CHAT_ALLOWLIST=1649845499
```

## Operational Reading

- if the slice is not enrolled, the baseline stays primary
- if the slice is enrolled, the CrewAI pilot becomes primary for that request
- the final runtime trace keeps the chosen `engine_name` and `engine_mode`

## Current Recommendation

- keep the canary disabled in shared environments until a small allowlisted rollout is intentionally approved
- prefer `support` before `public`
