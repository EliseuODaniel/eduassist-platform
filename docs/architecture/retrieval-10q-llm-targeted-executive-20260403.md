# Retrieval 10Q LLM-Targeted Executive Report

Date: 2026-04-03

Dataset:
- [retrieval_10q_llm_targeted.generated.20260403.json](/home/edann/projects/eduassist-platform/tests/evals/datasets/retrieval_10q_llm_targeted.generated.20260403.json)

Raw reports:
- [retrieval-10q-llm-targeted-report-20260403.md](/home/edann/projects/eduassist-platform/docs/architecture/retrieval-10q-llm-targeted-report-20260403.md)
- [retrieval-10q-llm-targeted-report-20260403.json](/home/edann/projects/eduassist-platform/docs/architecture/retrieval-10q-llm-targeted-report-20260403.json)

## Goal

This battery was intentionally written to avoid the strongest canonical lanes and to provoke actual LLM usage in the four active paths.

## High-Level Result

The battery succeeded only partially in its main goal.

- `langgraph` used LLM in `4/10` prompts
- `python_functions` used LLM in `0/10`
- `llamaindex` used LLM in `4/10`
- `specialist_supervisor` used LLM in `1/10`
- prompts with any LLM usage: `6/10`
- prompts with LLM usage in all four paths: `0/10`

This means the platform still routes a large share of open public prompts to deterministic or semi-deterministic layers, even when the phrasing is designed to be less canonical.

## Human Reading

The automatic scores in this run are not the main signal. Human reading is more informative here.

### Strong or Acceptable Answers

- `public_visibility_boundary_open`
  - `langgraph`, `python_functions`, and `llamaindex` gave materially good answers.
  - They missed the lexical rubric, but semantically the boundary between public information and authenticated detail was explained well.
- `public_student_support_ecosystem`
  - `langgraph`, `python_functions`, and `llamaindex` were good.
  - The shared canonical layer answered this well even under changed phrasing.
- `public_authority_channels_image`
  - `python_functions` and `llamaindex` were good concise answers.
  - `langgraph` was also acceptable, but more verbose than necessary.
- `public_extended_day_design`
  - `langgraph` and `python_functions` were acceptable.
  - They did not fully capture the “design” framing, but they stayed on topic.

### Partial Answers

- `public_health_assessment_reorganization`
  - `llamaindex` was the only path with a partially useful answer.
  - It connected health restrictions and family communication, but did not fully address absence on assessment day and academic reorganization.
- `public_family_time_architecture`
  - `langgraph` was partially useful.
  - It explained the pieces and their relation, but drifted into hedging instead of giving a tighter synthesis.

### Clear Failures

- `public_support_safety_balance`
  - `langgraph`, `python_functions`, and `llamaindex` leaked into generic school-profile text.
  - `specialist_supervisor` used LLM and still returned a false negative, claiming there was no evidence in the public base.
- `public_external_activity_risk_management`
  - `langgraph`, `python_functions`, and `llamaindex` all missed the topic badly.
  - `specialist_supervisor` failed safe.
- `public_governance_escalation_path`
  - `langgraph`, `python_functions`, and `llamaindex` again leaked to generic profile text.
  - `specialist_supervisor` failed safe.
- `public_operational_experience_bundle`
  - `langgraph`, `python_functions`, and `llamaindex` leaked to generic institutional pitch.
  - `specialist_supervisor` failed safe.

## What LLM Usage Actually Did

The most important finding of this battery is that LLM usage did not reliably improve quality.

### `langgraph`

LLM stages appeared in:
- `public_extended_day_design`
- `public_external_activity_risk_management`
- `public_family_time_architecture`
- `public_authority_channels_image`

Human reading:
- helped somewhat in `public_extended_day_design`
- helped somewhat in `public_family_time_architecture`
- did not help in `public_external_activity_risk_management`
- was acceptable in `public_authority_channels_image`

### `llamaindex`

LLM stages appeared in:
- `public_external_activity_risk_management`
- `public_health_assessment_reorganization`
- `public_family_time_architecture`
- `public_authority_channels_image`

Human reading:
- failed in `public_external_activity_risk_management`
- was partial in `public_health_assessment_reorganization`
- failed badly in `public_family_time_architecture` with `Empty Response`
- was good in `public_authority_channels_image`

### `specialist_supervisor`

LLM usage appeared only in:
- `public_support_safety_balance`

Human reading:
- it still failed semantically by asserting lack of evidence where the public corpus actually contains relevant material.

### `python_functions`

- LLM usage did not appear in this battery.
- This path remained deterministic and conservative.

## Main Conclusions

1. The battery did what it needed to do: it exposed which prompts still escape to weak generic-profile answers instead of grounded synthesis.
2. The biggest problem is not “too little LLM” by itself.
3. The biggest problem is:
   - generic profile leakage
   - weak documentary routing for non-canonical public synthesis
   - safe fallback overuse in `specialist_supervisor`
   - occasional instability in `llamaindex` and `specialist_supervisor`
4. `python_functions` remains the least likely to use LLM in this kind of prompt.
5. `langgraph` and `llamaindex` are currently the most useful paths for probing true LLM behavior, even though the quality is still inconsistent.

## Recommended Next Step

If the objective is to evaluate LLM quality itself rather than product quality, the next experiment should temporarily disable:

- public canonical lanes
- contextual public direct answers
- profile fallback shortcuts

for a controlled benchmark run.

Without that, most of the system will continue doing the correct product behavior: avoiding the LLM whenever deterministic grounded answers are available.
