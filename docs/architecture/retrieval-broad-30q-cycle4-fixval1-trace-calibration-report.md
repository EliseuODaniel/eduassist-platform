# Retrieval Trace Calibration Report

Generated at: 2026-04-15T23:13:14.995269+00:00

Run prefix: `debug:four-path:normal:20260415T230130Z`

Eval JSON: `docs/architecture/retrieval-broad-30q-cycle4-fixval1-cross-path-report.json`

## Stack Summary

| Stack | Count | Retrieval traces | Answerable | Quality | Avg top_k | Avg hits | Avg selected | Coverage | Latency |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `langgraph` | `30` | `5` | `0.0%` | `92.7` | `3.2` | `0.8` | `2.0` | `1.0` | `21928.1 ms` |
| `python_functions` | `30` | `4` | `0.0%` | `91.4` | `6.75` | `0.0` | `1.5` | `1.0` | `16884.6 ms` |
| `llamaindex` | `29` | `0` | `0.0%` | `92.9` | `0.0` | `0.0` | `0.0` | `0.0` | `16423.5 ms` |
| `specialist_supervisor` | `0` | `0` | `0.0%` | `0.0` | `0.0` | `0.0` | `0.0` | `0.0` | `0.0 ms` |

## Capability Highlights

| Capability | Count | Retrieval traces | Answerable | Quality | Avg top_k | Avg hits | Coverage | Stacks |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `public_bundle.conduct_frequency_punctuality` | `2` | `0` | `0.0%` | `0.0` | `0.0` | `0.0` | `0.0` | `langgraph, llamaindex` |
| `teacher_directory` | `2` | `0` | `0.0%` | `0.0` | `0.0` | `0.0` | `0.0` | `langgraph, llamaindex` |
| `leadership` | `1` | `0` | `0.0%` | `0.0` | `0.0` | `0.0` | `0.0` | `python_functions` |
| `llamaindex_turn_frame:protected.academic.family_comparison` | `1` | `0` | `0.0%` | `0.0` | `0.0` | `0.0` | `0.0` | `llamaindex` |
| `python_functions_turn_frame:protected.academic.family_comparison` | `1` | `0` | `0.0%` | `0.0` | `0.0` | `0.0` | `0.0` | `python_functions` |
| `python_functions_turn_frame:protected.teacher.schedule` | `1` | `0` | `0.0%` | `54.0` | `0.0` | `0.0` | `0.0` | `python_functions` |
| `python_functions_native_contextual_public_answer` | `1` | `0` | `0.0%` | `55.0` | `0.0` | `0.0` | `0.0` | `python_functions` |
| `langgraph_turn_frame:input_clarification` | `2` | `1` | `0.0%` | `71.5` | `4.0` | `4.0` | `1.0` | `langgraph` |
| `llamaindex_local_public_unknown_safe_clarify` | `2` | `0` | `0.0%` | `77.5` | `0.0` | `0.0` | `0.0` | `llamaindex` |
| `llamaindex_local_protected:academic` | `2` | `0` | `0.0%` | `80.0` | `0.0` | `0.0` | `0.0` | `llamaindex` |
| `python_functions_local_protected:academic` | `1` | `0` | `0.0%` | `80.0` | `0.0` | `0.0` | `0.0` | `python_functions` |
| `python_functions_native_family_attendance_aggregate` | `1` | `0` | `0.0%` | `80.0` | `0.0` | `0.0` | `0.0` | `python_functions` |
| `dados estruturados devem passar por service deterministico` | `6` | `0` | `0.0%` | `92.0` | `0.0` | `0.0` | `0.0` | `langgraph` |
| `protected.documents.restricted_lookup` | `8` | `8` | `0.0%` | `100.0` | `4.88` | `0.0` | `1.0` | `langgraph, python_functions` |
| `auth_guidance` | `5` | `0` | `0.0%` | `100.0` | `0.0` | `0.0` | `0.0` | `langgraph, llamaindex, python_functions` |

## Recommendations

- `protected.documents.restricted_lookup` está com `answerable_rate=0.0%` sem saturar `top_k`; vale revisar query variants, metadata e chunking.

## Trace Samples

### `llamaindex` `teacher_directory` `retrieval_public_known_unknown_total_teachers`

- Turn: `1`
- Prompt: Quero saber se a escola publica a quantidade total de professores ou se esse dado nao esta disponivel. Traga a resposta de forma concreta.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `0`, keyword pass `False`, latency `90050.6 ms`
- Reason: `exception`
- Errors: `request_failed`

### `langgraph` `teacher_directory` `retrieval_public_teacher_directory`

- Turn: `1`
- Prompt: Pensando no caso pratico, existe canal publico com nome ou contato do professor de matematica, ou isso vai pela coordenacao pedagogica?
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `0`, keyword pass `False`, latency `90141.6 ms`
- Reason: `exception`
- Errors: `request_failed`

### `python_functions` `leadership` `retrieval_public_teacher_directory`

- Turn: `1`
- Prompt: Pensando no caso pratico, existe canal publico com nome ou contato do professor de matematica, ou isso vai pela coordenacao pedagogica?
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `0`, keyword pass `False`, latency `90126.9 ms`
- Reason: `exception`
- Errors: `request_failed`

### `langgraph` `langgraph_turn_frame:input_clarification` `retrieval_public_open_world_out_of_scope`

- Turn: `1`
- Prompt: Quero uma recomendacao de filme, sem relacao com escola.
- Policy: `baseline` / `top_k=4` / `baseline_default`
- Retrieval: hits `4/4`, coverage `1.0`, answerable `None`
- Eval: quality `43`, keyword pass `False`, latency `89623.1 ms`
- Reason: `langgraph_native_public_retrieval`
- Errors: `forbidden_entity_or_value, unnecessary_clarification`

### `python_functions` `python_functions_turn_frame:protected.teacher.schedule` `retrieval_restricted_no_match`

- Turn: `1`
- Prompt: Sem sair do escopo do projeto, os documentos internos mencionam algum protocolo para excursao internacional com pernoite no ensino medio?
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `54`, keyword pass `False`, latency `1590.6 ms`
- Reason: `python_functions_native_structured:academic`
- Errors: `missing_expected_keyword, multi_intent_partial_collapse`

### `llamaindex` `llamaindex_local_public_unknown_safe_clarify` `retrieval_public_open_world_out_of_scope`

- Turn: `1`
- Prompt: Quero uma recomendacao de filme, sem relacao com escola.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `55`, keyword pass `False`, latency `67517.3 ms`
- Reason: `llamaindex_contextual_public_direct_fast_path`
- Errors: `forbidden_entity_or_value`

### `python_functions` `python_functions_native_contextual_public_answer` `retrieval_public_open_world_out_of_scope`

- Turn: `1`
- Prompt: Quero uma recomendacao de filme, sem relacao com escola.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `55`, keyword pass `False`, latency `57328.2 ms`
- Reason: `python_functions_native_contextual_public_answer`
- Errors: `forbidden_entity_or_value`

### `langgraph` `dados estruturados devem passar por service deterministico` `retrieval_protected_attendance_panorama`

- Turn: `1`
- Prompt: Mantendo o contexto, corta para o Lucas e resume qual e o risco mais concreto dele em frequencia.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `80`, keyword pass `False`, latency `1271.8 ms`
- Reason: `langgraph_public_canonical_lane:public_bundle.conduct_frequency_punctuality`
- Errors: `missing_expected_keyword`

### `llamaindex` `llamaindex_local_protected:academic` `retrieval_protected_attendance_panorama`

- Turn: `1`
- Prompt: Mantendo o contexto, corta para o Lucas e resume qual e o risco mais concreto dele em frequencia.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `80`, keyword pass `False`, latency `4621.7 ms`
- Reason: `llamaindex_public_canonical_lane:public_bundle.conduct_frequency_punctuality`
- Errors: `missing_expected_keyword`

### `python_functions` `python_functions_native_family_attendance_aggregate` `retrieval_protected_attendance_panorama`

- Turn: `1`
- Prompt: Mantendo o contexto, corta para o Lucas e resume qual e o risco mais concreto dele em frequencia.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `80`, keyword pass `False`, latency `8143.8 ms`
- Reason: `python_functions_native_public_compound`
- Errors: `missing_expected_keyword`

### `langgraph` `dados estruturados devem passar por service deterministico` `retrieval_student_academic_self`

- Turn: `1`
- Prompt: Como aluno autenticado, me diga qual materia esta melhor, qual esta pior e o que falta para fechar a media em fisica.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `80`, keyword pass `False`, latency `83546.8 ms`
- Reason: `dados estruturados devem passar por service deterministico`
- Errors: `missing_expected_keyword`

### `llamaindex` `llamaindex_local_protected:academic` `retrieval_student_academic_self`

- Turn: `1`
- Prompt: Como aluno autenticado, me diga qual materia esta melhor, qual esta pior e o que falta para fechar a media em fisica.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `80`, keyword pass `False`, latency `69318.2 ms`
- Reason: `llamaindex_local_protected:academic`
- Errors: `missing_expected_keyword`

