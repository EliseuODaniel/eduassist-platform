# Retrieval Trace Calibration Report

Generated at: 2026-04-15T12:19:08.100115+00:00

Run prefix: `debug:four-path:normal:20260415T120853Z`

Eval JSON: `docs/architecture/retrieval-broad-30q-cycle1-fixval5-cross-path-report.json`

## Stack Summary

| Stack | Count | Retrieval traces | Answerable | Quality | Avg top_k | Avg hits | Avg selected | Coverage | Latency |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `langgraph` | `30` | `5` | `0.0%` | `97.8` | `3.0` | `0.0` | `0.8` | `1.0` | `6840.4 ms` |
| `python_functions` | `30` | `5` | `0.0%` | `97.4` | `6.6` | `0.0` | `0.8` | `1.0` | `5906.0 ms` |
| `llamaindex` | `30` | `1` | `0.0%` | `96.7` | `4.0` | `4.0` | `4.0` | `1.0` | `6724.8 ms` |
| `specialist_supervisor` | `0` | `0` | `0.0%` | `0.0` | `0.0` | `0.0` | `0.0` | `0.0` | `0.0 ms` |

## Capability Highlights

| Capability | Count | Retrieval traces | Answerable | Quality | Avg top_k | Avg hits | Coverage | Stacks |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `llamaindex_turn_frame:protected.academic.attendance` | `1` | `0` | `0.0%` | `0.0` | `0.0` | `0.0` | `0.0` | `llamaindex` |
| `python_functions_turn_frame:protected.academic.attendance` | `1` | `0` | `0.0%` | `0.0` | `0.0` | `0.0` | `0.0` | `python_functions` |
| `llamaindex_local_public_fact:institution` | `2` | `0` | `0.0%` | `80.0` | `0.0` | `0.0` | `0.0` | `llamaindex` |
| `langgraph_turn_frame:protected.administrative.status` | `1` | `0` | `0.0%` | `80.0` | `0.0` | `0.0` | `0.0` | `langgraph` |
| `llamaindex_local_public_default:academic` | `1` | `1` | `0.0%` | `80.0` | `4.0` | `4.0` | `1.0` | `llamaindex` |
| `llamaindex_local_public_fact:unknown` | `1` | `0` | `0.0%` | `80.0` | `0.0` | `0.0` | `0.0` | `llamaindex` |
| `python_functions_local_clarify` | `1` | `0` | `0.0%` | `80.0` | `0.0` | `0.0` | `0.0` | `python_functions` |
| `python_functions_native_external_public_facility_boundary` | `1` | `0` | `0.0%` | `80.0` | `0.0` | `0.0` | `0.0` | `python_functions` |
| `langgraph_turn_frame:scope_boundary` | `2` | `0` | `0.0%` | `90.0` | `0.0` | `0.0` | `0.0` | `langgraph` |
| `pricing` | `2` | `0` | `0.0%` | `90.0` | `0.0` | `0.0` | `0.0` | `langgraph, python_functions` |
| `python_functions_turn_frame:scope_boundary` | `2` | `0` | `0.0%` | `90.0` | `0.0` | `0.0` | `0.0` | `python_functions` |
| `public_bundle.facilities_study_support` | `3` | `0` | `0.0%` | `93.3` | `0.0` | `0.0` | `0.0` | `langgraph, llamaindex, python_functions` |
| `protected.documents.restricted_lookup` | `10` | `10` | `0.0%` | `100.0` | `4.8` | `0.0` | `1.0` | `langgraph, python_functions` |
| `llamaindex_local_protected:academic` | `7` | `0` | `0.0%` | `100.0` | `0.0` | `0.0` | `0.0` | `llamaindex` |
| `dados estruturados devem passar por service deterministico` | `6` | `0` | `0.0%` | `100.0` | `0.0` | `0.0` | `0.0` | `langgraph` |

## Recommendations

- `protected.documents.restricted_lookup` está com `answerable_rate=0.0%` sem saturar `top_k`; vale revisar query variants, metadata e chunking.

## Trace Samples

### `langgraph` `langgraph_turn_frame:protected.administrative.status` `retrieval_protected_admin_docs`

- Turn: `1`
- Prompt: Pensando no caso pratico, no cadastro da Ana, quais pendencias administrativas continuam abertas e que acao vem agora?
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `80`, keyword pass `False`, latency `903.8 ms`
- Reason: `langgraph_turn_frame:scope_boundary`
- Errors: `missing_expected_keyword`

### `python_functions` `python_functions_turn_frame:scope_boundary` `retrieval_protected_admin_docs`

- Turn: `1`
- Prompt: Pensando no caso pratico, no cadastro da Ana, quais pendencias administrativas continuam abertas e que acao vem agora?
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `80`, keyword pass `False`, latency `614.4 ms`
- Reason: `python_functions_turn_frame:scope_boundary`
- Errors: `missing_expected_keyword`

### `python_functions` `python_functions_local_clarify` `retrieval_protected_boundary_auth_needed`

- Turn: `1`
- Prompt: Nao estou autenticado e mesmo assim quero consultar meu boletim aqui pelo bot.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `80`, keyword pass `False`, latency `10342.8 ms`
- Reason: `python_functions_local_clarify`
- Errors: `missing_expected_keyword`

### `langgraph` `langgraph_turn_frame:scope_boundary` `retrieval_public_external_library_boundary`

- Turn: `1`
- Prompt: Fora do Colegio Horizonte, qual e o horario da biblioteca publica da cidade?
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `80`, keyword pass `False`, latency `9733.6 ms`
- Reason: `langgraph_turn_frame:external_public_facility_boundary`
- Errors: `missing_expected_keyword`

### `llamaindex` `llamaindex_local_public_fact:unknown` `retrieval_public_external_library_boundary`

- Turn: `1`
- Prompt: Fora do Colegio Horizonte, qual e o horario da biblioteca publica da cidade?
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `80`, keyword pass `False`, latency `325.6 ms`
- Reason: `llamaindex_external_public_facility_boundary_fast_path`
- Errors: `missing_expected_keyword`

### `python_functions` `python_functions_native_external_public_facility_boundary` `retrieval_public_external_library_boundary`

- Turn: `1`
- Prompt: Fora do Colegio Horizonte, qual e o horario da biblioteca publica da cidade?
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `80`, keyword pass `False`, latency `290.8 ms`
- Reason: `python_functions_native_external_public_facility_boundary`
- Errors: `missing_expected_keyword`

### `langgraph` `pricing` `retrieval_public_pricing_projection`

- Turn: `1`
- Prompt: Pela referencia publica de precos, qual seria a matricula total e o valor mensal para 3 filhos. Traga a resposta de forma concreta.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `80`, keyword pass `False`, latency `18493.1 ms`
- Reason: `langgraph_turn_frame:public_answer`
- Errors: `missing_expected_keyword`

### `llamaindex` `llamaindex_local_public_fact:institution` `retrieval_public_pricing_projection`

- Turn: `1`
- Prompt: Pela referencia publica de precos, qual seria a matricula total e o valor mensal para 3 filhos. Traga a resposta de forma concreta.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `80`, keyword pass `False`, latency `13325.4 ms`
- Reason: `llamaindex_contextual_public_pricing_fast_path`
- Errors: `missing_expected_keyword`

### `llamaindex` `llamaindex_local_public_fact:institution` `retrieval_public_service_routing`

- Turn: `1`
- Prompt: Por qual canal eu falo com o setor de bolsas, com o financeiro e com a direcao da escola. Seja objetivo e grounded.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `80`, keyword pass `False`, latency `15526.4 ms`
- Reason: `llamaindex_contextual_public_direct_fast_path`
- Errors: `missing_expected_keyword`

### `llamaindex` `llamaindex_local_public_default:academic` `retrieval_protected_boundary_auth_needed`

- Turn: `1`
- Prompt: Nao estou autenticado e mesmo assim quero consultar meu boletim aqui pelo bot.
- Policy: `baseline` / `top_k=4` / `baseline_default`
- Retrieval: hits `4/4`, coverage `1.0`, answerable `False`
- Eval: quality `80`, keyword pass `False`, latency `1515.1 ms`
- Reason: `llamaindex_local_public_default:academic`
- Errors: `missing_expected_keyword`

### `llamaindex` `public_bundle.facilities_study_support` `retrieval_public_facilities_study`

- Turn: `1`
- Prompt: De que forma os documentos publicos ligam biblioteca, laboratorios e estudo orientado como suporte ao ensino medio. Responda de forma direta.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `90`, keyword pass `True`, latency `2520.3 ms`
- Reason: `llamaindex_public_canonical_lane:public_bundle.facilities_study_support`
- Errors: `weak_actionability`

### `python_functions` `public_bundle.facilities_study_support` `retrieval_public_facilities_study`

- Turn: `1`
- Prompt: De que forma os documentos publicos ligam biblioteca, laboratorios e estudo orientado como suporte ao ensino medio. Responda de forma direta.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `90`, keyword pass `True`, latency `6066.8 ms`
- Reason: `python_functions_native_canonical_lane:public_bundle.facilities_study_support`
- Errors: `weak_actionability`

