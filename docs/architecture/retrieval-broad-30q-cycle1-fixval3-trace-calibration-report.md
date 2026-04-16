# Retrieval Trace Calibration Report

Generated at: 2026-04-15T07:54:21.742480+00:00

Run prefix: `debug:four-path:normal:20260415T074433Z`

Eval JSON: `docs/architecture/retrieval-broad-30q-cycle1-fixval3-cross-path-report.json`

## Stack Summary

| Stack | Count | Retrieval traces | Answerable | Quality | Avg top_k | Avg hits | Avg selected | Coverage | Latency |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `langgraph` | `30` | `5` | `0.0%` | `96.1` | `3.0` | `0.0` | `0.8` | `1.0` | `6617.7 ms` |
| `python_functions` | `30` | `4` | `0.0%` | `93.6` | `6.75` | `0.0` | `0.75` | `1.0` | `6042.1 ms` |
| `llamaindex` | `30` | `1` | `0.0%` | `93.9` | `4.0` | `4.0` | `4.0` | `1.0` | `6199.3 ms` |
| `specialist_supervisor` | `0` | `0` | `0.0%` | `0.0` | `0.0` | `0.0` | `0.0` | `0.0` | `0.0 ms` |

## Capability Highlights

| Capability | Count | Retrieval traces | Answerable | Quality | Avg top_k | Avg hits | Coverage | Stacks |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `llamaindex_turn_frame:protected.academic.attendance` | `1` | `0` | `0.0%` | `0.0` | `0.0` | `0.0` | `0.0` | `llamaindex` |
| `python_functions_turn_frame:protected.academic.attendance` | `1` | `0` | `0.0%` | `0.0` | `0.0` | `0.0` | `0.0` | `python_functions` |
| `llamaindex_local_public_fact:institution` | `2` | `0` | `0.0%` | `80.0` | `0.0` | `0.0` | `0.0` | `llamaindex` |
| `python_functions_native_teacher_schedule` | `2` | `0` | `0.0%` | `80.0` | `0.0` | `0.0` | `0.0` | `python_functions` |
| `langgraph_turn_frame:protected.administrative.status` | `1` | `0` | `0.0%` | `80.0` | `0.0` | `0.0` | `0.0` | `langgraph` |
| `leadership` | `1` | `0` | `0.0%` | `80.0` | `0.0` | `0.0` | `0.0` | `langgraph` |
| `llamaindex_local_public_default:academic` | `1` | `1` | `0.0%` | `80.0` | `4.0` | `4.0` | `1.0` | `llamaindex` |
| `llamaindex_local_public_fact:unknown` | `1` | `0` | `0.0%` | `80.0` | `0.0` | `0.0` | `0.0` | `llamaindex` |
| `python_functions_local_clarify` | `1` | `0` | `0.0%` | `80.0` | `0.0` | `0.0` | `0.0` | `python_functions` |
| `python_functions_native_external_public_facility_boundary` | `1` | `0` | `0.0%` | `80.0` | `0.0` | `0.0` | `0.0` | `python_functions` |
| `python_functions_native_public_compound` | `1` | `0` | `0.0%` | `80.0` | `0.0` | `0.0` | `0.0` | `python_functions` |
| `public_bundle.governance_protocol` | `3` | `0` | `0.0%` | `86.7` | `0.0` | `0.0` | `0.0` | `langgraph, llamaindex, python_functions` |
| `python_functions_turn_frame:scope_boundary` | `3` | `0` | `0.0%` | `86.7` | `0.0` | `0.0` | `0.0` | `python_functions` |
| `langgraph_turn_frame:scope_boundary` | `2` | `0` | `0.0%` | `90.0` | `0.0` | `0.0` | `0.0` | `langgraph` |
| `pricing` | `2` | `0` | `0.0%` | `90.0` | `0.0` | `0.0` | `0.0` | `langgraph, python_functions` |

## Recommendations

- `protected.documents.restricted_lookup` está com `answerable_rate=0.0%` sem saturar `top_k`; vale revisar query variants, metadata e chunking.

## Trace Samples

### `langgraph` `dados estruturados devem passar por service deterministico` `retrieval_student_academic_self`

- Turn: `1`
- Prompt: Sem tabela, diga minha melhor disciplina, a pior e quanto ainda falta para eu fechar a media em fisica.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `76`, keyword pass `True`, latency `8471.9 ms`
- Reason: `dados estruturados devem passar por service deterministico`
- Errors: `attendance_metric_misroute`

### `llamaindex` `llamaindex_local_protected:academic` `retrieval_student_academic_self`

- Turn: `1`
- Prompt: Sem tabela, diga minha melhor disciplina, a pior e quanto ainda falta para eu fechar a media em fisica.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `76`, keyword pass `True`, latency `7355.3 ms`
- Reason: `llamaindex_local_protected:academic`
- Errors: `attendance_metric_misroute`

### `python_functions` `python_functions_local_protected:academic` `retrieval_student_academic_self`

- Turn: `1`
- Prompt: Sem tabela, diga minha melhor disciplina, a pior e quanto ainda falta para eu fechar a media em fisica.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `76`, keyword pass `True`, latency `7577.6 ms`
- Reason: `python_functions_native_structured:academic`
- Errors: `attendance_metric_misroute`

### `langgraph` `langgraph_turn_frame:protected.administrative.status` `retrieval_protected_admin_docs`

- Turn: `1`
- Prompt: Pensando no caso pratico, no cadastro da Ana, quais pendencias administrativas continuam abertas e que acao vem agora?
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `80`, keyword pass `False`, latency `974.9 ms`
- Reason: `langgraph_turn_frame:scope_boundary`
- Errors: `missing_expected_keyword`

### `python_functions` `python_functions_turn_frame:scope_boundary` `retrieval_protected_admin_docs`

- Turn: `1`
- Prompt: Pensando no caso pratico, no cadastro da Ana, quais pendencias administrativas continuam abertas e que acao vem agora?
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `80`, keyword pass `False`, latency `761.7 ms`
- Reason: `python_functions_turn_frame:scope_boundary`
- Errors: `missing_expected_keyword`

### `python_functions` `python_functions_local_clarify` `retrieval_protected_boundary_auth_needed`

- Turn: `1`
- Prompt: Nao estou autenticado e mesmo assim quero consultar meu boletim aqui pelo bot.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `80`, keyword pass `False`, latency `10613.4 ms`
- Reason: `python_functions_local_clarify`
- Errors: `missing_expected_keyword`

### `langgraph` `langgraph_turn_frame:scope_boundary` `retrieval_public_external_library_boundary`

- Turn: `1`
- Prompt: Fora do Colegio Horizonte, qual e o horario da biblioteca publica da cidade?
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `80`, keyword pass `False`, latency `7739.4 ms`
- Reason: `langgraph_turn_frame:external_public_facility_boundary`
- Errors: `missing_expected_keyword`

### `llamaindex` `llamaindex_local_public_fact:unknown` `retrieval_public_external_library_boundary`

- Turn: `1`
- Prompt: Fora do Colegio Horizonte, qual e o horario da biblioteca publica da cidade?
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `80`, keyword pass `False`, latency `370.0 ms`
- Reason: `llamaindex_external_public_facility_boundary_fast_path`
- Errors: `missing_expected_keyword`

### `python_functions` `python_functions_native_external_public_facility_boundary` `retrieval_public_external_library_boundary`

- Turn: `1`
- Prompt: Fora do Colegio Horizonte, qual e o horario da biblioteca publica da cidade?
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `80`, keyword pass `False`, latency `324.4 ms`
- Reason: `python_functions_native_external_public_facility_boundary`
- Errors: `missing_expected_keyword`

### `llamaindex` `public_bundle.governance_protocol` `retrieval_public_governance_protocol`

- Turn: `1`
- Prompt: Na base publica, como aparecem conectados direcao, atendimento formal e numero de protocolo?
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `80`, keyword pass `False`, latency `2266.0 ms`
- Reason: `llamaindex_public_canonical_lane:public_bundle.governance_protocol`
- Errors: `missing_expected_keyword`

### `python_functions` `public_bundle.governance_protocol` `retrieval_public_governance_protocol`

- Turn: `1`
- Prompt: Na base publica, como aparecem conectados direcao, atendimento formal e numero de protocolo?
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `80`, keyword pass `False`, latency `4906.3 ms`
- Reason: `python_functions_native_canonical_lane:public_bundle.governance_protocol`
- Errors: `missing_expected_keyword`

### `langgraph` `pricing` `retrieval_public_pricing_projection`

- Turn: `1`
- Prompt: Pela referencia publica de precos, qual seria a matricula total e o valor mensal para 3 filhos. Traga a resposta de forma concreta.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `80`, keyword pass `False`, latency `18733.2 ms`
- Reason: `langgraph_turn_frame:public_answer`
- Errors: `missing_expected_keyword`

