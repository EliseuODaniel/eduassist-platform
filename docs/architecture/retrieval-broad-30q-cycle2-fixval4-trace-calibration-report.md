# Retrieval Trace Calibration Report

Generated at: 2026-04-15T17:13:06.506357+00:00

Run prefix: `debug:four-path:normal:20260415T170303Z`

Eval JSON: `docs/architecture/retrieval-broad-30q-cycle2-fixval4-cross-path-report.json`

## Stack Summary

| Stack | Count | Retrieval traces | Answerable | Quality | Avg top_k | Avg hits | Avg selected | Coverage | Latency |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `langgraph` | `29` | `5` | `0.0%` | `94.6` | `3.0` | `0.0` | `1.0` | `1.0` | `6242.7 ms` |
| `python_functions` | `30` | `5` | `0.0%` | `91.4` | `6.8` | `0.0` | `1.0` | `1.0` | `6031.9 ms` |
| `llamaindex` | `30` | `0` | `0.0%` | `91.4` | `0.0` | `0.0` | `0.0` | `0.0` | `7058.6 ms` |
| `specialist_supervisor` | `0` | `0` | `0.0%` | `0.0` | `0.0` | `0.0` | `0.0` | `0.0` | `0.0 ms` |

## Capability Highlights

| Capability | Count | Retrieval traces | Answerable | Quality | Avg top_k | Avg hits | Coverage | Stacks |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `llamaindex_turn_frame:protected.academic.attendance` | `1` | `0` | `0.0%` | `0.0` | `0.0` | `0.0` | `0.0` | `llamaindex` |
| `python_functions_turn_frame:protected.academic.attendance` | `1` | `0` | `0.0%` | `0.0` | `0.0` | `0.0` | `0.0` | `python_functions` |
| `llamaindex_local_protected:academic` | `1` | `0` | `0.0%` | `31.0` | `0.0` | `0.0` | `0.0` | `llamaindex` |
| `llamaindex_local_clarify;turn_frame=protected.account.access_scope` | `1` | `0` | `0.0%` | `54.0` | `0.0` | `0.0` | `0.0` | `llamaindex` |
| `python_functions_native_authenticated_account_scope` | `1` | `0` | `0.0%` | `54.0` | `0.0` | `0.0` | `0.0` | `python_functions` |
| `llamaindex_turn_frame:protected.academic.family_comparison` | `2` | `0` | `0.0%` | `55.0` | `0.0` | `0.0` | `0.0` | `llamaindex` |
| `python_functions_turn_frame:protected.academic.family_comparison` | `2` | `0` | `0.0%` | `55.0` | `0.0` | `0.0` | `0.0` | `python_functions` |
| `python_functions_native_family_attendance_aggregate` | `2` | `0` | `0.0%` | `65.5` | `0.0` | `0.0` | `0.0` | `python_functions` |
| `a intencao esta ambigua e exige clarificacao antes de recuperar contexto` | `2` | `0` | `0.0%` | `80.0` | `0.0` | `0.0` | `0.0` | `langgraph` |
| `llamaindex_local_public_default:institution` | `1` | `0` | `0.0%` | `80.0` | `0.0` | `0.0` | `0.0` | `llamaindex` |
| `llamaindex_turn_frame:protected.institution.admin_finance_status` | `1` | `0` | `0.0%` | `80.0` | `0.0` | `0.0` | `0.0` | `llamaindex` |
| `python_functions_native_contextual_public_answer` | `1` | `0` | `0.0%` | `80.0` | `0.0` | `0.0` | `0.0` | `python_functions` |
| `python_functions_turn_frame:protected.institution.admin_finance_status` | `1` | `0` | `0.0%` | `80.0` | `0.0` | `0.0` | `0.0` | `python_functions` |
| `status administrativo autenticado exige service deterministico` | `1` | `0` | `0.0%` | `80.0` | `0.0` | `0.0` | `0.0` | `langgraph` |
| `dados estruturados devem passar por service deterministico` | `5` | `0` | `0.0%` | `82.8` | `0.0` | `0.0` | `0.0` | `langgraph` |

## Recommendations

- `protected.documents.restricted_lookup` está com `answerable_rate=0.0%` sem saturar `top_k`; vale revisar query variants, metadata e chunking.

## Trace Samples

### `langgraph` `dados estruturados devem passar por service deterministico` `retrieval_protected_attendance_panorama`

- Turn: `1`
- Prompt: Agora ignora a Ana e me da so o alerta principal do Lucas por frequencia, sem repetir o panorama todo.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `31`, keyword pass `False`, latency `18279.3 ms`
- Reason: `dados estruturados devem passar por service deterministico`
- Errors: `attendance_metric_misroute, forbidden_entity_or_value`

### `llamaindex` `llamaindex_local_protected:academic` `retrieval_protected_attendance_panorama`

- Turn: `1`
- Prompt: Agora ignora a Ana e me da so o alerta principal do Lucas por frequencia, sem repetir o panorama todo.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `31`, keyword pass `False`, latency `26243.0 ms`
- Reason: `llamaindex_turn_frame:protected.academic.attendance`
- Errors: `attendance_metric_misroute, forbidden_entity_or_value`

### `python_functions` `python_functions_native_family_attendance_aggregate` `retrieval_protected_attendance_panorama`

- Turn: `1`
- Prompt: Agora ignora a Ana e me da so o alerta principal do Lucas por frequencia, sem repetir o panorama todo.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `31`, keyword pass `False`, latency `21895.8 ms`
- Reason: `python_functions_native_structured:academic`
- Errors: `attendance_metric_misroute, forbidden_entity_or_value`

### `llamaindex` `llamaindex_local_clarify;turn_frame=protected.account.access_scope` `retrieval_protected_access_scope`

- Turn: `1`
- Prompt: O que eu consigo consultar aqui no Telegram? Quero meu escopo exato entre academico e financeiro.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `54`, keyword pass `False`, latency `700.5 ms`
- Reason: `llamaindex_protected_records_fast_path`
- Errors: `missing_expected_keyword, multi_intent_partial_collapse`

### `python_functions` `python_functions_native_authenticated_account_scope` `retrieval_protected_access_scope`

- Turn: `1`
- Prompt: O que eu consigo consultar aqui no Telegram? Quero meu escopo exato entre academico e financeiro.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `54`, keyword pass `False`, latency `767.4 ms`
- Reason: `python_functions_native_authenticated_account_scope`
- Errors: `missing_expected_keyword, multi_intent_partial_collapse`

### `llamaindex` `llamaindex_turn_frame:protected.academic.family_comparison` `retrieval_protected_family_panorama`

- Turn: `1`
- Prompt: Mantendo a comparacao anterior, tira o Lucas da conversa e mostra so o ponto academico mais fraco da Ana.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `55`, keyword pass `False`, latency `1050.6 ms`
- Reason: `llamaindex_turn_frame:protected.academic.family_comparison`
- Errors: `forbidden_entity_or_value`

### `python_functions` `python_functions_turn_frame:protected.academic.family_comparison` `retrieval_protected_family_panorama`

- Turn: `1`
- Prompt: Mantendo a comparacao anterior, tira o Lucas da conversa e mostra so o ponto academico mais fraco da Ana.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `55`, keyword pass `False`, latency `1106.6 ms`
- Reason: `python_functions_native_structured:academic`
- Errors: `forbidden_entity_or_value`

### `llamaindex` `llamaindex_local_restricted_documents;turn_frame=protected.documents.restricted_lookup` `retrieval_restricted_finance_playbook`

- Turn: `1`
- Prompt: No playbook interno de negociacao financeira, quais criterios orientam uma negociacao com a familia. Seja objetivo e grounded.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `68`, keyword pass `False`, latency `5405.9 ms`
- Reason: `llamaindex_restricted_doc_fast_path`
- Errors: `missing_expected_keyword, unnecessary_clarification`

### `langgraph` `protected.documents.restricted_lookup` `retrieval_restricted_finance_playbook`

- Turn: `1`
- Prompt: No playbook interno de negociacao financeira, quais criterios orientam uma negociacao com a familia. Seja objetivo e grounded.
- Policy: `deep` / `top_k=3` / `explicit_override`
- Retrieval: hits `1/0`, coverage `1.0`, answerable `None`
- Eval: quality `68`, keyword pass `False`, latency `5708.4 ms`
- Reason: `langgraph_restricted_doc_grounded`
- Errors: `missing_expected_keyword, unnecessary_clarification`

### `python_functions` `protected.documents.restricted_lookup` `retrieval_restricted_finance_playbook`

- Turn: `1`
- Prompt: No playbook interno de negociacao financeira, quais criterios orientam uma negociacao com a familia. Seja objetivo e grounded.
- Policy: `deep` / `top_k=6` / `restricted_visibility:complex_query`
- Retrieval: hits `1/0`, coverage `1.0`, answerable `None`
- Eval: quality `68`, keyword pass `False`, latency `5561.7 ms`
- Reason: `python_functions_native_restricted_document_search`
- Errors: `missing_expected_keyword, unnecessary_clarification`

### `langgraph` `status administrativo autenticado exige service deterministico` `retrieval_protected_admin_finance_combo`

- Turn: `1`
- Prompt: Resuma junto documentacao administrativa e financeiro das contas vinculadas para eu saber se ha impedimento de atendimento.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `80`, keyword pass `False`, latency `1180.5 ms`
- Reason: `status administrativo autenticado exige service deterministico`
- Errors: `missing_expected_keyword`

### `llamaindex` `llamaindex_turn_frame:protected.institution.admin_finance_status` `retrieval_protected_admin_finance_combo`

- Turn: `1`
- Prompt: Resuma junto documentacao administrativa e financeiro das contas vinculadas para eu saber se ha impedimento de atendimento.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `80`, keyword pass `False`, latency `866.7 ms`
- Reason: `llamaindex_turn_frame:protected.institution.admin_finance_status`
- Errors: `missing_expected_keyword`

