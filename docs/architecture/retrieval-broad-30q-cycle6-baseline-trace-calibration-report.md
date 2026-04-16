# Retrieval Trace Calibration Report

Generated at: 2026-04-16T06:28:16.047763+00:00

Run prefix: `debug:four-path:normal:20260416T062135Z`

Eval JSON: `docs/architecture/retrieval-broad-30q-cycle6-baseline-cross-path-report.json`

## Stack Summary

| Stack | Count | Retrieval traces | Answerable | Quality | Avg top_k | Avg hits | Avg selected | Coverage | Latency |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `langgraph` | `27` | `5` | `0.0%` | `100.0` | `3.0` | `0.0` | `0.8` | `1.0` | `3264.0 ms` |
| `python_functions` | `30` | `4` | `0.0%` | `97.6` | `7.0` | `0.0` | `0.75` | `1.0` | `4825.0 ms` |
| `llamaindex` | `30` | `0` | `0.0%` | `97.6` | `0.0` | `0.0` | `0.0` | `0.0` | `4263.1 ms` |
| `specialist_supervisor` | `0` | `0` | `0.0%` | `0.0` | `0.0` | `0.0` | `0.0` | `0.0` | `0.0 ms` |

## Capability Highlights

| Capability | Count | Retrieval traces | Answerable | Quality | Avg top_k | Avg hits | Coverage | Stacks |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `authenticated_public_profile_rescue` | `1` | `0` | `0.0%` | `0.0` | `0.0` | `0.0` | `0.0` | `langgraph` |
| `llamaindex_local_clarify` | `1` | `0` | `0.0%` | `0.0` | `0.0` | `0.0` | `0.0` | `llamaindex` |
| `llamaindex_native_protected_focus:academic` | `1` | `0` | `0.0%` | `0.0` | `0.0` | `0.0` | `0.0` | `llamaindex` |
| `python_functions_native_teacher_schedule` | `1` | `0` | `0.0%` | `0.0` | `0.0` | `0.0` | `0.0` | `python_functions` |
| `llamaindex_turn_frame:protected.documents.restricted_lookup` | `1` | `0` | `0.0%` | `54.0` | `0.0` | `0.0` | `0.0` | `llamaindex` |
| `python_functions_native_protected_focus:finance` | `2` | `0` | `0.0%` | `77.0` | `0.0` | `0.0` | `0.0` | `python_functions` |
| `python_functions_local_protected:academic` | `1` | `0` | `0.0%` | `80.0` | `0.0` | `0.0` | `0.0` | `python_functions` |
| `llamaindex_local_protected:academic` | `4` | `0` | `0.0%` | `93.3` | `0.0` | `0.0` | `0.0` | `llamaindex` |
| `protected.documents.restricted_lookup` | `9` | `9` | `0.0%` | `100.0` | `4.78` | `0.0` | `1.0` | `langgraph, python_functions` |
| `dados estruturados devem passar por service deterministico` | `7` | `0` | `0.0%` | `100.0` | `0.0` | `0.0` | `0.0` | `langgraph` |
| `python_functions_native_protected_focus:academic` | `5` | `0` | `0.0%` | `100.0` | `0.0` | `0.0` | `0.0` | `python_functions` |
| `curriculum` | `4` | `0` | `0.0%` | `100.0` | `0.0` | `0.0` | `0.0` | `langgraph, python_functions` |
| `llamaindex_local_public_unknown_safe_clarify` | `4` | `0` | `0.0%` | `100.0` | `0.0` | `0.0` | `0.0` | `llamaindex` |
| `auth_guidance` | `3` | `0` | `0.0%` | `100.0` | `0.0` | `0.0` | `0.0` | `langgraph, llamaindex, python_functions` |
| `llamaindex_local_public_fact:institution` | `3` | `0` | `0.0%` | `100.0` | `0.0` | `0.0` | `0.0` | `llamaindex` |

## Recommendations

- `protected.documents.restricted_lookup` está com `answerable_rate=0.0%` sem saturar `top_k`; vale revisar query variants, metadata e chunking.

## Trace Samples

### `llamaindex` `llamaindex_turn_frame:protected.documents.restricted_lookup` `retrieval_staff_finance_protocol`

- Turn: `1`
- Prompt: Quero o trecho operacional: no fluxo interno de pagamento parcial, o que precisa ser validado antes de prometer quitacao?
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `54`, keyword pass `False`, latency `12938.1 ms`
- Reason: `llamaindex_turn_frame:protected.documents.restricted_lookup`
- Errors: `missing_expected_keyword, multi_intent_partial_collapse`

### `python_functions` `python_functions_native_protected_focus:finance` `retrieval_staff_finance_protocol`

- Turn: `1`
- Prompt: Quero o trecho operacional: no fluxo interno de pagamento parcial, o que precisa ser validado antes de prometer quitacao?
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `54`, keyword pass `False`, latency `13319.8 ms`
- Reason: `python_functions_native_structured:finance`
- Errors: `missing_expected_keyword, multi_intent_partial_collapse`

### `llamaindex` `llamaindex_local_protected:academic` `retrieval_teacher_schedule_panorama`

- Turn: `1`
- Prompt: Filtre a minha alocacao e deixe so as turmas do ensino medio.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `80`, keyword pass `False`, latency `6520.3 ms`
- Reason: `llamaindex_teacher_schedule_direct`
- Errors: `missing_expected_keyword`

### `python_functions` `python_functions_local_protected:academic` `retrieval_teacher_schedule_panorama`

- Turn: `1`
- Prompt: Filtre a minha alocacao e deixe so as turmas do ensino medio.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `80`, keyword pass `False`, latency `7012.7 ms`
- Reason: `python_functions_native_teacher_schedule`
- Errors: `missing_expected_keyword`

### `langgraph` `dados estruturados devem passar por service deterministico` `retrieval_protected_access_scope`

- Turn: `1`
- Prompt: De forma bem objetiva, quero confirmar meu escopo no Telegram: estou autenticado e consigo ver o que de academico e financeiro?
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `100`, keyword pass `True`, latency `660.9 ms`
- Reason: `dados estruturados devem passar por service deterministico`

### `llamaindex` `llamaindex_local_clarify;turn_frame=protected.account.access_scope` `retrieval_protected_access_scope`

- Turn: `1`
- Prompt: De forma bem objetiva, quero confirmar meu escopo no Telegram: estou autenticado e consigo ver o que de academico e financeiro?
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `100`, keyword pass `True`, latency `418.5 ms`
- Reason: `llamaindex_protected_records_fast_path`

### `python_functions` `python_functions_native_authenticated_account_scope` `retrieval_protected_access_scope`

- Turn: `1`
- Prompt: De forma bem objetiva, quero confirmar meu escopo no Telegram: estou autenticado e consigo ver o que de academico e financeiro?
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `100`, keyword pass `True`, latency `407.9 ms`
- Reason: `python_functions_native_authenticated_account_scope`

### `langgraph` `status administrativo autenticado exige service deterministico` `retrieval_protected_admin_docs`

- Turn: `1`
- Prompt: Pensando no caso pratico, quero um retrato das pendencias documentais da Ana e do proximo passo para regularizar tudo.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `100`, keyword pass `True`, latency `3969.0 ms`
- Reason: `status administrativo autenticado exige service deterministico`

### `llamaindex` `llamaindex_turn_frame:protected.administrative.status` `retrieval_protected_admin_docs`

- Turn: `1`
- Prompt: Pensando no caso pratico, quero um retrato das pendencias documentais da Ana e do proximo passo para regularizar tudo.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `100`, keyword pass `True`, latency `1654.3 ms`
- Reason: `llamaindex_turn_frame:protected.administrative.status`

### `python_functions` `python_functions_turn_frame:protected.administrative.status` `retrieval_protected_admin_docs`

- Turn: `1`
- Prompt: Pensando no caso pratico, quero um retrato das pendencias documentais da Ana e do proximo passo para regularizar tudo.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `100`, keyword pass `True`, latency `2048.1 ms`
- Reason: `python_functions_native_structured:institution`

### `langgraph` `status administrativo autenticado exige service deterministico` `retrieval_protected_admin_finance_combo`

- Turn: `1`
- Prompt: De forma bem objetiva, tem algo na minha documentacao ou no cadastro que esteja travando o financeiro? Me de a visao combinada.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `100`, keyword pass `True`, latency `1843.1 ms`
- Reason: `status administrativo autenticado exige service deterministico`

### `llamaindex` `llamaindex_turn_frame:protected.institution.admin_finance_status` `retrieval_protected_admin_finance_combo`

- Turn: `1`
- Prompt: De forma bem objetiva, tem algo na minha documentacao ou no cadastro que esteja travando o financeiro? Me de a visao combinada.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `100`, keyword pass `True`, latency `1288.4 ms`
- Reason: `llamaindex_turn_frame:protected.institution.admin_finance_status`

