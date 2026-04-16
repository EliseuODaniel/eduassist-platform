# Retrieval Trace Calibration Report

Generated at: 2026-04-16T07:00:05.764139+00:00

Run prefix: `debug:four-path:normal:20260416T064210Z`

Eval JSON: `docs/architecture/retrieval-broad-30q-cycle6-fixval1-cross-path-report.json`

## Stack Summary

| Stack | Count | Retrieval traces | Answerable | Quality | Avg top_k | Avg hits | Avg selected | Coverage | Latency |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `langgraph` | `27` | `5` | `0.0%` | `95.8` | `3.0` | `0.0` | `0.8` | `1.0` | `9872.1 ms` |
| `python_functions` | `28` | `4` | `0.0%` | `96.0` | `7.0` | `0.0` | `0.75` | `1.0` | `11224.1 ms` |
| `llamaindex` | `28` | `0` | `0.0%` | `100.0` | `0.0` | `0.0` | `0.0` | `0.0` | `5600.9 ms` |
| `specialist_supervisor` | `0` | `0` | `0.0%` | `0.0` | `0.0` | `0.0` | `0.0` | `0.0` | `0.0 ms` |

## Capability Highlights

| Capability | Count | Retrieval traces | Answerable | Quality | Avg top_k | Avg hits | Coverage | Stacks |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `authenticated_public_profile_rescue` | `1` | `0` | `0.0%` | `0.0` | `0.0` | `0.0` | `0.0` | `langgraph` |
| `deterministic_public_known_unknown` | `1` | `0` | `0.0%` | `0.0` | `0.0` | `0.0` | `0.0` | `python_functions` |
| `llamaindex_local_clarify` | `1` | `0` | `0.0%` | `0.0` | `0.0` | `0.0` | `0.0` | `llamaindex` |
| `llamaindex_native_protected_focus:academic` | `1` | `0` | `0.0%` | `0.0` | `0.0` | `0.0` | `0.0` | `llamaindex` |
| `status administrativo autenticado exige service deterministico` | `2` | `0` | `0.0%` | `50.0` | `0.0` | `0.0` | `0.0` | `langgraph` |
| `protected.documents.restricted_lookup` | `9` | `9` | `0.0%` | `100.0` | `4.78` | `0.0` | `1.0` | `langgraph, python_functions` |
| `dados estruturados devem passar por service deterministico` | `6` | `0` | `0.0%` | `100.0` | `0.0` | `0.0` | `0.0` | `langgraph` |
| `python_functions_native_protected_focus:academic` | `5` | `0` | `0.0%` | `100.0` | `0.0` | `0.0` | `0.0` | `python_functions` |
| `curriculum` | `4` | `0` | `0.0%` | `100.0` | `0.0` | `0.0` | `0.0` | `langgraph, python_functions` |
| `llamaindex_local_protected:academic` | `4` | `0` | `0.0%` | `100.0` | `0.0` | `0.0` | `0.0` | `llamaindex` |
| `auth_guidance` | `3` | `0` | `0.0%` | `100.0` | `0.0` | `0.0` | `0.0` | `langgraph, llamaindex, python_functions` |
| `llamaindex_local_public_fact:institution` | `3` | `0` | `0.0%` | `100.0` | `0.0` | `0.0` | `0.0` | `llamaindex` |
| `llamaindex_local_public_unknown_safe_clarify` | `3` | `0` | `0.0%` | `100.0` | `0.0` | `0.0` | `0.0` | `llamaindex` |
| `llamaindex_local_restricted_documents;turn_frame=protected.documents.restricted_lookup` | `3` | `0` | `0.0%` | `100.0` | `0.0` | `0.0` | `0.0` | `llamaindex` |
| `public_bundle.family_new_calendar_assessment_enrollment` | `3` | `0` | `0.0%` | `100.0` | `0.0` | `0.0` | `0.0` | `langgraph, llamaindex, python_functions` |

## Recommendations

- `protected.documents.restricted_lookup` está com `answerable_rate=0.0%` sem saturar `top_k`; vale revisar query variants, metadata e chunking.

## Trace Samples

### `langgraph` `status administrativo autenticado exige service deterministico` `retrieval_protected_admin_finance_combo`

- Turn: `1`
- Prompt: De forma bem objetiva, tem algo na minha documentacao ou no cadastro que esteja travando o financeiro? Me de a visao combinada.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `0`, keyword pass `False`, latency `101887.2 ms`
- Reason: `exception`
- Errors: `request_failed`

### `python_functions` `deterministic_public_known_unknown` `retrieval_public_known_unknown_total_teachers`

- Turn: `1`
- Prompt: Quantos professores a escola tem hoje? Se isso nao estiver publicado, deixe claro. Traga a resposta de forma concreta.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `0`, keyword pass `False`, latency `94802.3 ms`
- Reason: `exception`
- Errors: `request_failed`

### `langgraph` `dados estruturados devem passar por service deterministico` `retrieval_protected_access_scope`

- Turn: `1`
- Prompt: De forma bem objetiva, quero confirmar meu escopo no Telegram: estou autenticado e consigo ver o que de academico e financeiro?
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `100`, keyword pass `True`, latency `593.0 ms`
- Reason: `dados estruturados devem passar por service deterministico`

### `llamaindex` `llamaindex_local_clarify;turn_frame=protected.account.access_scope` `retrieval_protected_access_scope`

- Turn: `1`
- Prompt: De forma bem objetiva, quero confirmar meu escopo no Telegram: estou autenticado e consigo ver o que de academico e financeiro?
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `100`, keyword pass `True`, latency `386.0 ms`
- Reason: `llamaindex_protected_records_fast_path`

### `python_functions` `python_functions_native_authenticated_account_scope` `retrieval_protected_access_scope`

- Turn: `1`
- Prompt: De forma bem objetiva, quero confirmar meu escopo no Telegram: estou autenticado e consigo ver o que de academico e financeiro?
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `100`, keyword pass `True`, latency `383.5 ms`
- Reason: `python_functions_native_authenticated_account_scope`

### `langgraph` `status administrativo autenticado exige service deterministico` `retrieval_protected_admin_docs`

- Turn: `1`
- Prompt: Pensando no caso pratico, quero um retrato das pendencias documentais da Ana e do proximo passo para regularizar tudo.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `100`, keyword pass `True`, latency `2805.6 ms`
- Reason: `status administrativo autenticado exige service deterministico`

### `llamaindex` `llamaindex_turn_frame:protected.administrative.status` `retrieval_protected_admin_docs`

- Turn: `1`
- Prompt: Pensando no caso pratico, quero um retrato das pendencias documentais da Ana e do proximo passo para regularizar tudo.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `100`, keyword pass `True`, latency `1733.9 ms`
- Reason: `llamaindex_turn_frame:protected.administrative.status`

### `python_functions` `python_functions_turn_frame:protected.administrative.status` `retrieval_protected_admin_docs`

- Turn: `1`
- Prompt: Pensando no caso pratico, quero um retrato das pendencias documentais da Ana e do proximo passo para regularizar tudo.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `100`, keyword pass `True`, latency `2165.7 ms`
- Reason: `python_functions_native_structured:institution`

### `llamaindex` `llamaindex_turn_frame:protected.institution.admin_finance_status` `retrieval_protected_admin_finance_combo`

- Turn: `1`
- Prompt: De forma bem objetiva, tem algo na minha documentacao ou no cadastro que esteja travando o financeiro? Me de a visao combinada.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `100`, keyword pass `True`, latency `1216.0 ms`
- Reason: `llamaindex_turn_frame:protected.institution.admin_finance_status`

### `python_functions` `python_functions_turn_frame:protected.institution.admin_finance_status` `retrieval_protected_admin_finance_combo`

- Turn: `1`
- Prompt: De forma bem objetiva, tem algo na minha documentacao ou no cadastro que esteja travando o financeiro? Me de a visao combinada.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `100`, keyword pass `True`, latency `85254.2 ms`
- Reason: `python_functions_native_structured:institution`

### `langgraph` `dados estruturados devem passar por service deterministico` `retrieval_protected_attendance_panorama`

- Turn: `1`
- Prompt: De forma bem objetiva, continuando a analise, isole o Lucas e mostre por que a frequencia dele preocupa mais ou menos.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `100`, keyword pass `True`, latency `2293.2 ms`
- Reason: `dados estruturados devem passar por service deterministico`

### `llamaindex` `llamaindex_turn_frame:protected.academic.family_comparison` `retrieval_protected_attendance_panorama`

- Turn: `1`
- Prompt: De forma bem objetiva, continuando a analise, isole o Lucas e mostre por que a frequencia dele preocupa mais ou menos.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `100`, keyword pass `True`, latency `14798.9 ms`
- Reason: `llamaindex_local_protected:academic`

