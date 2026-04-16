# Retrieval Trace Calibration Report

Generated at: 2026-04-15T21:38:22.002432+00:00

Run prefix: `debug:four-path:normal:20260415T212355Z`

Eval JSON: `docs/architecture/retrieval-broad-30q-cycle4-baseline-cross-path-report.json`

## Stack Summary

| Stack | Count | Retrieval traces | Answerable | Quality | Avg top_k | Avg hits | Avg selected | Coverage | Latency |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `langgraph` | `30` | `5` | `0.0%` | `94.7` | `3.2` | `0.8` | `2.0` | `1.0` | `7123.5 ms` |
| `python_functions` | `30` | `4` | `0.0%` | `88.1` | `6.75` | `0.0` | `1.5` | `1.0` | `9182.1 ms` |
| `llamaindex` | `29` | `0` | `0.0%` | `91.7` | `0.0` | `0.0` | `0.0` | `0.0` | `7823.0 ms` |
| `specialist_supervisor` | `0` | `0` | `0.0%` | `0.0` | `0.0` | `0.0` | `0.0` | `0.0` | `0.0 ms` |

## Capability Highlights

| Capability | Count | Retrieval traces | Answerable | Quality | Avg top_k | Avg hits | Coverage | Stacks |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `public_bundle.conduct_frequency_punctuality` | `3` | `0` | `0.0%` | `0.0` | `0.0` | `0.0` | `0.0` | `langgraph, llamaindex, python_functions` |
| `llamaindex_turn_frame:protected.academic.family_comparison` | `1` | `0` | `0.0%` | `0.0` | `0.0` | `0.0` | `0.0` | `llamaindex` |
| `python_functions_local_protected:academic` | `1` | `0` | `0.0%` | `0.0` | `0.0` | `0.0` | `0.0` | `python_functions` |
| `python_functions_turn_frame:protected.academic.family_comparison` | `1` | `0` | `0.0%` | `0.0` | `0.0` | `0.0` | `0.0` | `python_functions` |
| `segments` | `1` | `0` | `0.0%` | `0.0` | `0.0` | `0.0` | `0.0` | `langgraph` |
| `llamaindex_local_public_fact:institution;turn_frame=public.facilities.library.hours` | `1` | `0` | `0.0%` | `35.0` | `0.0` | `0.0` | `0.0` | `llamaindex` |
| `operating_hours` | `1` | `0` | `0.0%` | `35.0` | `0.0` | `0.0` | `0.0` | `python_functions` |
| `llamaindex_local_protected:academic` | `2` | `0` | `0.0%` | `40.0` | `0.0` | `0.0` | `0.0` | `llamaindex` |
| `langgraph_turn_frame:input_clarification` | `1` | `1` | `0.0%` | `43.0` | `4.0` | `4.0` | `1.0` | `langgraph` |
| `python_functions_turn_frame:input_clarification` | `1` | `0` | `0.0%` | `43.0` | `0.0` | `0.0` | `0.0` | `python_functions` |
| `python_functions_turn_frame:protected.teacher.schedule` | `2` | `0` | `0.0%` | `54.0` | `0.0` | `0.0` | `0.0` | `python_functions` |
| `authenticated_public_profile_rescue` | `1` | `0` | `0.0%` | `54.0` | `0.0` | `0.0` | `0.0` | `langgraph` |
| `llamaindex_turn_frame:protected.teacher.schedule` | `2` | `0` | `0.0%` | `68.0` | `0.0` | `0.0` | `0.0` | `llamaindex` |
| `python_functions_native_teacher_schedule` | `1` | `0` | `0.0%` | `68.0` | `0.0` | `0.0` | `0.0` | `python_functions` |
| `python_functions_native_family_attendance_aggregate` | `1` | `0` | `0.0%` | `80.0` | `0.0` | `0.0` | `0.0` | `python_functions` |

## Recommendations

- `protected.documents.restricted_lookup` está com `answerable_rate=0.0%` sem saturar `top_k`; vale revisar query variants, metadata e chunking.

## Trace Samples

### `llamaindex` `llamaindex_local_protected:academic` `retrieval_student_academic_self`

- Turn: `1`
- Prompt: Como aluno autenticado, me diga qual materia esta melhor, qual esta pior e o que falta para fechar a media em fisica.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `0`, keyword pass `False`, latency `90112.2 ms`
- Reason: `exception`
- Errors: `request_failed`

### `python_functions` `python_functions_local_protected:academic` `retrieval_student_academic_self`

- Turn: `1`
- Prompt: Como aluno autenticado, me diga qual materia esta melhor, qual esta pior e o que falta para fechar a media em fisica.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `0`, keyword pass `False`, latency `97097.7 ms`
- Reason: `exception`
- Errors: `request_failed`

### `llamaindex` `llamaindex_local_public_fact:institution;turn_frame=public.facilities.library.hours` `retrieval_public_external_library_boundary`

- Turn: `1`
- Prompt: Nao e a biblioteca da escola: me diga o horario da biblioteca publica municipal.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `35`, keyword pass `False`, latency `312.4 ms`
- Reason: `llamaindex_contextual_public_boundary_fast_path`
- Errors: `forbidden_entity_or_value, missing_expected_keyword`

### `python_functions` `operating_hours` `retrieval_public_external_library_boundary`

- Turn: `1`
- Prompt: Nao e a biblioteca da escola: me diga o horario da biblioteca publica municipal.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `35`, keyword pass `False`, latency `3982.0 ms`
- Reason: `python_functions_native_semantic_ingress:operating_hours`
- Errors: `forbidden_entity_or_value, missing_expected_keyword`

### `python_functions` `python_functions_turn_frame:input_clarification` `retrieval_public_open_world_out_of_scope`

- Turn: `1`
- Prompt: Quero uma recomendacao de filme, sem relacao com escola.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `43`, keyword pass `False`, latency `32704.1 ms`
- Reason: `python_functions_turn_frame:input_clarification`
- Errors: `forbidden_entity_or_value, unnecessary_clarification`

### `langgraph` `langgraph_turn_frame:input_clarification` `retrieval_public_open_world_out_of_scope`

- Turn: `1`
- Prompt: Quero uma recomendacao de filme, sem relacao com escola.
- Policy: `baseline` / `top_k=4` / `baseline_default`
- Retrieval: hits `4/4`, coverage `1.0`, answerable `None`
- Eval: quality `43`, keyword pass `False`, latency `35550.8 ms`
- Reason: `langgraph_native_public_retrieval`
- Errors: `forbidden_entity_or_value, unnecessary_clarification`

### `langgraph` `authenticated_public_profile_rescue` `retrieval_restricted_no_match`

- Turn: `1`
- Prompt: Sem sair do escopo do projeto, os documentos internos mencionam algum protocolo para excursao internacional com pernoite no ensino medio?
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `54`, keyword pass `False`, latency `805.4 ms`
- Reason: `authenticated_public_profile_rescue`
- Errors: `missing_expected_keyword, multi_intent_partial_collapse`

### `python_functions` `python_functions_turn_frame:protected.teacher.schedule` `retrieval_restricted_no_match`

- Turn: `1`
- Prompt: Sem sair do escopo do projeto, os documentos internos mencionam algum protocolo para excursao internacional com pernoite no ensino medio?
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `54`, keyword pass `False`, latency `447.3 ms`
- Reason: `python_functions_native_structured:academic`
- Errors: `missing_expected_keyword, multi_intent_partial_collapse`

### `llamaindex` `llamaindex_turn_frame:protected.teacher.schedule` `retrieval_teacher_schedule_panorama`

- Turn: `1`
- Prompt: Agora recorte so o que eu tenho no ensino medio.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `68`, keyword pass `False`, latency `6658.9 ms`
- Reason: `llamaindex_turn_frame:protected.teacher.schedule`
- Errors: `missing_expected_keyword, unnecessary_clarification`

### `python_functions` `python_functions_native_teacher_schedule` `retrieval_teacher_schedule_panorama`

- Turn: `1`
- Prompt: Agora recorte so o que eu tenho no ensino medio.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `68`, keyword pass `False`, latency `6814.9 ms`
- Reason: `python_functions_native_structured:academic`
- Errors: `missing_expected_keyword, unnecessary_clarification`

### `langgraph` `dados estruturados devem passar por service deterministico` `retrieval_protected_attendance_panorama`

- Turn: `1`
- Prompt: Mantendo o contexto, corta para o Lucas e resume qual e o risco mais concreto dele em frequencia.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `80`, keyword pass `False`, latency `567.4 ms`
- Reason: `langgraph_public_canonical_lane:public_bundle.conduct_frequency_punctuality`
- Errors: `missing_expected_keyword`

### `llamaindex` `llamaindex_local_protected:academic` `retrieval_protected_attendance_panorama`

- Turn: `1`
- Prompt: Mantendo o contexto, corta para o Lucas e resume qual e o risco mais concreto dele em frequencia.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `80`, keyword pass `False`, latency `1497.3 ms`
- Reason: `llamaindex_public_canonical_lane:public_bundle.conduct_frequency_punctuality`
- Errors: `missing_expected_keyword`

