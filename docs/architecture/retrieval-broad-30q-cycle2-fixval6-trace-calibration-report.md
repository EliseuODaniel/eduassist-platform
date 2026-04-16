# Retrieval Trace Calibration Report

Generated at: 2026-04-15T17:49:47.647982+00:00

Run prefix: `debug:four-path:normal:20260415T174041Z`

Eval JSON: `docs/architecture/retrieval-broad-30q-cycle2-fixval6-cross-path-report.json`

## Stack Summary

| Stack | Count | Retrieval traces | Answerable | Quality | Avg top_k | Avg hits | Avg selected | Coverage | Latency |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `langgraph` | `29` | `5` | `0.0%` | `95.8` | `3.0` | `0.0` | `1.0` | `1.0` | `5891.0 ms` |
| `python_functions` | `30` | `5` | `0.0%` | `93.3` | `6.8` | `0.0` | `1.0` | `1.0` | `5509.3 ms` |
| `llamaindex` | `30` | `0` | `0.0%` | `93.3` | `0.0` | `0.0` | `0.0` | `0.0` | `5914.3 ms` |
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
| `llamaindex_turn_frame:protected.institution.admin_finance_status` | `1` | `0` | `0.0%` | `80.0` | `0.0` | `0.0` | `0.0` | `llamaindex` |
| `python_functions_turn_frame:protected.institution.admin_finance_status` | `1` | `0` | `0.0%` | `80.0` | `0.0` | `0.0` | `0.0` | `python_functions` |
| `status administrativo autenticado exige service deterministico` | `1` | `0` | `0.0%` | `80.0` | `0.0` | `0.0` | `0.0` | `langgraph` |
| `dados estruturados devem passar por service deterministico` | `5` | `0` | `0.0%` | `82.8` | `0.0` | `0.0` | `0.0` | `langgraph` |
| `protected.documents.restricted_lookup` | `10` | `10` | `0.0%` | `100.0` | `4.9` | `0.0` | `1.0` | `langgraph, python_functions` |
| `auth_guidance` | `5` | `0` | `0.0%` | `100.0` | `0.0` | `0.0` | `0.0` | `langgraph, llamaindex, python_functions` |

## Recommendations

- `protected.documents.restricted_lookup` está com `answerable_rate=0.0%` sem saturar `top_k`; vale revisar query variants, metadata e chunking.

## Trace Samples

### `langgraph` `dados estruturados devem passar por service deterministico` `retrieval_protected_attendance_panorama`

- Turn: `1`
- Prompt: Agora ignora a Ana e me da so o alerta principal do Lucas por frequencia, sem repetir o panorama todo.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `31`, keyword pass `False`, latency `22505.0 ms`
- Reason: `dados estruturados devem passar por service deterministico`
- Errors: `attendance_metric_misroute, forbidden_entity_or_value`

### `llamaindex` `llamaindex_local_protected:academic` `retrieval_protected_attendance_panorama`

- Turn: `1`
- Prompt: Agora ignora a Ana e me da so o alerta principal do Lucas por frequencia, sem repetir o panorama todo.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `31`, keyword pass `False`, latency `20951.1 ms`
- Reason: `llamaindex_turn_frame:protected.academic.attendance`
- Errors: `attendance_metric_misroute, forbidden_entity_or_value`

### `python_functions` `python_functions_native_family_attendance_aggregate` `retrieval_protected_attendance_panorama`

- Turn: `1`
- Prompt: Agora ignora a Ana e me da so o alerta principal do Lucas por frequencia, sem repetir o panorama todo.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `31`, keyword pass `False`, latency `24037.4 ms`
- Reason: `python_functions_native_structured:academic`
- Errors: `attendance_metric_misroute, forbidden_entity_or_value`

### `llamaindex` `llamaindex_local_clarify;turn_frame=protected.account.access_scope` `retrieval_protected_access_scope`

- Turn: `1`
- Prompt: O que eu consigo consultar aqui no Telegram? Quero meu escopo exato entre academico e financeiro.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `54`, keyword pass `False`, latency `742.6 ms`
- Reason: `llamaindex_protected_records_fast_path`
- Errors: `missing_expected_keyword, multi_intent_partial_collapse`

### `python_functions` `python_functions_native_authenticated_account_scope` `retrieval_protected_access_scope`

- Turn: `1`
- Prompt: O que eu consigo consultar aqui no Telegram? Quero meu escopo exato entre academico e financeiro.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `54`, keyword pass `False`, latency `707.5 ms`
- Reason: `python_functions_native_authenticated_account_scope`
- Errors: `missing_expected_keyword, multi_intent_partial_collapse`

### `llamaindex` `llamaindex_turn_frame:protected.academic.family_comparison` `retrieval_protected_family_panorama`

- Turn: `1`
- Prompt: Mantendo a comparacao anterior, tira o Lucas da conversa e mostra so o ponto academico mais fraco da Ana.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `55`, keyword pass `False`, latency `1041.7 ms`
- Reason: `llamaindex_turn_frame:protected.academic.family_comparison`
- Errors: `forbidden_entity_or_value`

### `python_functions` `python_functions_turn_frame:protected.academic.family_comparison` `retrieval_protected_family_panorama`

- Turn: `1`
- Prompt: Mantendo a comparacao anterior, tira o Lucas da conversa e mostra so o ponto academico mais fraco da Ana.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `55`, keyword pass `False`, latency `1070.3 ms`
- Reason: `python_functions_native_structured:academic`
- Errors: `forbidden_entity_or_value`

### `langgraph` `status administrativo autenticado exige service deterministico` `retrieval_protected_admin_finance_combo`

- Turn: `1`
- Prompt: Resuma junto documentacao administrativa e financeiro das contas vinculadas para eu saber se ha impedimento de atendimento.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `80`, keyword pass `False`, latency `928.2 ms`
- Reason: `status administrativo autenticado exige service deterministico`
- Errors: `missing_expected_keyword`

### `llamaindex` `llamaindex_turn_frame:protected.institution.admin_finance_status` `retrieval_protected_admin_finance_combo`

- Turn: `1`
- Prompt: Resuma junto documentacao administrativa e financeiro das contas vinculadas para eu saber se ha impedimento de atendimento.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `80`, keyword pass `False`, latency `604.0 ms`
- Reason: `llamaindex_turn_frame:protected.institution.admin_finance_status`
- Errors: `missing_expected_keyword`

### `python_functions` `python_functions_turn_frame:protected.institution.admin_finance_status` `retrieval_protected_admin_finance_combo`

- Turn: `1`
- Prompt: Resuma junto documentacao administrativa e financeiro das contas vinculadas para eu saber se ha impedimento de atendimento.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `80`, keyword pass `False`, latency `757.7 ms`
- Reason: `python_functions_native_structured:institution`
- Errors: `missing_expected_keyword`

### `langgraph` `a intencao esta ambigua e exige clarificacao antes de recuperar contexto` `retrieval_protected_family_panorama`

- Turn: `1`
- Prompt: Mantendo a comparacao anterior, tira o Lucas da conversa e mostra so o ponto academico mais fraco da Ana.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `80`, keyword pass `False`, latency `14166.2 ms`
- Reason: `a intencao esta ambigua e exige clarificacao antes de recuperar contexto`
- Errors: `missing_expected_keyword`

### `langgraph` `dados estruturados devem passar por service deterministico` `retrieval_protected_access_scope`

- Turn: `1`
- Prompt: O que eu consigo consultar aqui no Telegram? Quero meu escopo exato entre academico e financeiro.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `100`, keyword pass `True`, latency `815.5 ms`
- Reason: `dados estruturados devem passar por service deterministico`

