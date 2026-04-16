# Retrieval Trace Calibration Report

Generated at: 2026-04-15T06:53:45.193814+00:00

Run prefix: `debug:four-path:normal:20260415T064405Z`

Eval JSON: `docs/architecture/retrieval-broad-30q-cycle1-fixval-cross-path-report.json`

## Stack Summary

| Stack | Count | Retrieval traces | Answerable | Quality | Avg top_k | Avg hits | Avg selected | Coverage | Latency |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `langgraph` | `29` | `5` | `0.0%` | `88.1` | `3.0` | `0.0` | `0.8` | `1.0` | `5837.9 ms` |
| `python_functions` | `29` | `4` | `0.0%` | `85.3` | `6.75` | `0.0` | `0.75` | `1.0` | `6429.8 ms` |
| `llamaindex` | `29` | `1` | `0.0%` | `85.2` | `4.0` | `4.0` | `4.0` | `1.0` | `6399.3 ms` |
| `specialist_supervisor` | `0` | `0` | `0.0%` | `0.0` | `0.0` | `0.0` | `0.0` | `0.0` | `0.0 ms` |

## Capability Highlights

| Capability | Count | Retrieval traces | Answerable | Quality | Avg top_k | Avg hits | Coverage | Stacks |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `python_functions_native_family_attendance_aggregate` | `1` | `0` | `0.0%` | `0.0` | `0.0` | `0.0` | `0.0` | `python_functions` |
| `llamaindex_local_public_fact:unknown` | `1` | `0` | `0.0%` | `35.0` | `0.0` | `0.0` | `0.0` | `llamaindex` |
| `python_functions_native_external_public_facility_boundary` | `1` | `0` | `0.0%` | `35.0` | `0.0` | `0.0` | `0.0` | `python_functions` |
| `langgraph_turn_frame:scope_boundary` | `2` | `0` | `0.0%` | `45.0` | `0.0` | `0.0` | `0.0` | `langgraph` |
| `llamaindex_local_protected:institution` | `1` | `0` | `0.0%` | `54.0` | `0.0` | `0.0` | `0.0` | `llamaindex` |
| `python_functions_local_protected:institution` | `1` | `0` | `0.0%` | `54.0` | `0.0` | `0.0` | `0.0` | `python_functions` |
| `status administrativo autenticado exige service deterministico` | `1` | `0` | `0.0%` | `54.0` | `0.0` | `0.0` | `0.0` | `langgraph` |
| `dados estruturados devem passar por service deterministico` | `5` | `0` | `0.0%` | `69.0` | `0.0` | `0.0` | `0.0` | `langgraph` |
| `llamaindex_local_protected:academic` | `7` | `0` | `0.0%` | `71.2` | `0.0` | `0.0` | `0.0` | `llamaindex` |
| `llamaindex_local_public_unknown_safe_clarify` | `2` | `0` | `0.0%` | `77.5` | `0.0` | `0.0` | `0.0` | `llamaindex` |
| `python_functions_turn_frame:scope_boundary` | `2` | `0` | `0.0%` | `77.5` | `0.0` | `0.0` | `0.0` | `python_functions` |
| `llamaindex_local_public_fact:institution` | `2` | `0` | `0.0%` | `80.0` | `0.0` | `0.0` | `0.0` | `llamaindex` |
| `python_functions_native_public_compound` | `2` | `0` | `0.0%` | `80.0` | `0.0` | `0.0` | `0.0` | `python_functions` |
| `python_functions_native_teacher_schedule` | `2` | `0` | `0.0%` | `80.0` | `0.0` | `0.0` | `0.0` | `python_functions` |
| `llamaindex_local_public_default:academic` | `1` | `1` | `0.0%` | `80.0` | `4.0` | `4.0` | `1.0` | `llamaindex` |

## Recommendations

- `protected.documents.restricted_lookup` está com `answerable_rate=0.0%` sem saturar `top_k`; vale revisar query variants, metadata e chunking.

## Trace Samples

### `langgraph` `dados estruturados devem passar por service deterministico` `retrieval_protected_attendance_panorama`

- Turn: `1`
- Prompt: Agora foque so no Lucas e diga o que mais preocupa na frequencia dele.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `0`, keyword pass `False`, latency `8358.5 ms`
- Reason: `exception`
- Errors: `request_failed`

### `llamaindex` `llamaindex_local_protected:academic` `retrieval_protected_attendance_panorama`

- Turn: `1`
- Prompt: Agora foque so no Lucas e diga o que mais preocupa na frequencia dele.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `0`, keyword pass `False`, latency `11819.0 ms`
- Reason: `exception`
- Errors: `request_failed`

### `python_functions` `python_functions_native_family_attendance_aggregate` `retrieval_protected_attendance_panorama`

- Turn: `1`
- Prompt: Agora foque so no Lucas e diga o que mais preocupa na frequencia dele.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `0`, keyword pass `False`, latency `8474.8 ms`
- Reason: `exception`
- Errors: `request_failed`

### `langgraph` `langgraph_turn_frame:scope_boundary` `retrieval_public_external_library_boundary`

- Turn: `1`
- Prompt: Fora do Colegio Horizonte, qual e o horario da biblioteca publica da cidade?
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `35`, keyword pass `False`, latency `10039.8 ms`
- Reason: `langgraph_turn_frame:external_public_facility_boundary`
- Errors: `forbidden_entity_or_value, missing_expected_keyword`

### `llamaindex` `llamaindex_local_public_fact:unknown` `retrieval_public_external_library_boundary`

- Turn: `1`
- Prompt: Fora do Colegio Horizonte, qual e o horario da biblioteca publica da cidade?
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `35`, keyword pass `False`, latency `284.8 ms`
- Reason: `llamaindex_contextual_public_boundary_fast_path`
- Errors: `forbidden_entity_or_value, missing_expected_keyword`

### `python_functions` `python_functions_native_external_public_facility_boundary` `retrieval_public_external_library_boundary`

- Turn: `1`
- Prompt: Fora do Colegio Horizonte, qual e o horario da biblioteca publica da cidade?
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `35`, keyword pass `False`, latency `267.1 ms`
- Reason: `python_functions_native_external_public_facility_boundary`
- Errors: `forbidden_entity_or_value, missing_expected_keyword`

### `langgraph` `status administrativo autenticado exige service deterministico` `retrieval_protected_admin_finance_combo`

- Turn: `1`
- Prompt: Tem algo na minha documentacao ou no cadastro que esteja travando o financeiro? Me de a visao combinada.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `54`, keyword pass `False`, latency `11758.1 ms`
- Reason: `status administrativo autenticado exige service deterministico`
- Errors: `missing_expected_keyword, multi_intent_partial_collapse`

### `llamaindex` `llamaindex_local_protected:institution` `retrieval_protected_admin_finance_combo`

- Turn: `1`
- Prompt: Tem algo na minha documentacao ou no cadastro que esteja travando o financeiro? Me de a visao combinada.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `54`, keyword pass `False`, latency `11079.1 ms`
- Reason: `llamaindex_protected_records_fast_path`
- Errors: `missing_expected_keyword, multi_intent_partial_collapse`

### `python_functions` `python_functions_local_protected:institution` `retrieval_protected_admin_finance_combo`

- Turn: `1`
- Prompt: Tem algo na minha documentacao ou no cadastro que esteja travando o financeiro? Me de a visao combinada.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `54`, keyword pass `False`, latency `11249.5 ms`
- Reason: `python_functions_native_structured:institution`
- Errors: `missing_expected_keyword, multi_intent_partial_collapse`

### `langgraph` `langgraph_turn_frame:scope_boundary` `retrieval_public_open_world_out_of_scope`

- Turn: `1`
- Prompt: Fora do tema escolar, qual filme voce acha que mais vale a pena ver agora?
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `55`, keyword pass `False`, latency `1734.1 ms`
- Reason: `langgraph_turn_frame:scope_boundary`
- Errors: `forbidden_entity_or_value`

### `llamaindex` `llamaindex_local_public_unknown_safe_clarify` `retrieval_public_open_world_out_of_scope`

- Turn: `1`
- Prompt: Fora do tema escolar, qual filme voce acha que mais vale a pena ver agora?
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `55`, keyword pass `False`, latency `3032.3 ms`
- Reason: `llamaindex_contextual_public_direct_fast_path`
- Errors: `forbidden_entity_or_value`

### `python_functions` `python_functions_turn_frame:scope_boundary` `retrieval_public_open_world_out_of_scope`

- Turn: `1`
- Prompt: Fora do tema escolar, qual filme voce acha que mais vale a pena ver agora?
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `55`, keyword pass `False`, latency `1865.6 ms`
- Reason: `python_functions_turn_frame:scope_boundary`
- Errors: `forbidden_entity_or_value`

