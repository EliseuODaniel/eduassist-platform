# 10Q LLM-Focus Executive Report

Dataset: `/home/edann/projects/eduassist-platform/tests/evals/datasets/retrieval_10q_llm_focus.generated.20260403.json`

## Stack Summary

| Stack | OK | Keyword pass | Quality | Avg latency | used_llm |
| --- | --- | --- | --- | --- | --- |
| `langgraph` | `10/10` | `5/10` | `90.0` | `2138.8 ms` | `3/10` |
| `python_functions` | `10/10` | `4/10` | `86.8` | `1019.0 ms` | `1/10` |
| `llamaindex` | `10/10` | `4/10` | `88.0` | `2885.7 ms` | `4/10` |
| `specialist_supervisor` | `10/10` | `5/10` | `90.0` | `8926.6 ms` | `4/10` |

## Prompt-by-Prompt LLM Usage

| Category | langgraph | python_functions | llamaindex | specialist_supervisor |
| --- | --- | --- | --- | --- |
| `public_inclusion_accessibility` | `yes (structured_polish, answer_verifier_judge)` | `no (none)` | `yes (answer_composition)` | `yes (specialist_execution)` |
| `public_integral_study_support` | `no (none)` | `no (none)` | `no (none)` | `no (none)` |
| `public_health_emergency_bundle` | `no (none)` | `yes (answer_composition, answer_verifier_judge)` | `yes (answer_composition)` | `no (none)` |
| `public_outings_authorizations` | `yes (answer_composition)` | `no (none)` | `yes (answer_composition)` | `yes (specialist_execution)` |
| `public_year_three_phases` | `no (none)` | `no (none)` | `no (none)` | `yes (specialist_execution)` |
| `public_transport_uniform_bundle` | `yes (structured_polish)` | `no (none)` | `yes (answer_composition)` | `yes (general_knowledge_fast_path)` |
| `public_governance_protocol` | `no (none)` | `no (none)` | `no (none)` | `no (none)` |
| `public_academic_policy_overview` | `no (none)` | `no (none)` | `no (none)` | `no (none)` |
| `public_conduct_frequency_punctuality` | `no (none)` | `no (none)` | `no (none)` | `no (none)` |
| `public_deep_multi_doc` | `no (none)` | `no (none)` | `no (none)` | `no (none)` |

## High-Signal Findings

- `4/4` caminhos usando LLM: nenhum
- `>=3/4` caminhos usando LLM: `public_inclusion_accessibility` (3/4), `public_outings_authorizations` (3/4), `public_transport_uniform_bundle` (3/4)
- Mesmo com prompts desenhados para cair na LLM, a camada deterministica do produto ainda capturou parte relevante da bateria, especialmente em `python_functions` e `langgraph`.
- O `specialist_supervisor` continua sendo o caminho que mais efetivamente entra em LLM nesta rodada.
- `llamaindex` ficou no meio: mais LLM que `langgraph/python_functions`, menos que `specialist_supervisor`.

## Residual Issues

- `langgraph`: `missing_expected_keyword`=5
- `python_functions`: `missing_expected_keyword`=6, `unnecessary_clarification`=1
- `llamaindex`: `missing_expected_keyword`=6
- `specialist_supervisor`: `missing_expected_keyword`=5
