# Retrieval Trace Calibration Report

Generated at: 2026-04-13T13:21:10.368131+00:00

Run prefix: `debug:four-path:normal:20260413T125823Z`

Eval JSON: `docs/architecture/retrieval-60q-cross-path-report.json`

## Stack Summary

| Stack | Count | Retrieval traces | Answerable | Quality | Avg top_k | Avg hits | Avg selected | Coverage | Latency |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `langgraph` | `56` | `9` | `0.0%` | `97.0` | `3.0` | `0.0` | `0.0` | `1.0` | `5756.4 ms` |
| `python_functions` | `60` | `4` | `0.0%` | `87.8` | `6.75` | `0.0` | `0.0` | `1.0` | `9490.7 ms` |
| `llamaindex` | `60` | `0` | `0.0%` | `91.9` | `0.0` | `0.0` | `0.0` | `0.0` | `7237.4 ms` |
| `specialist_supervisor` | `0` | `0` | `0.0%` | `0.0` | `0.0` | `0.0` | `0.0` | `0.0` | `0.0 ms` |

## Capability Highlights

| Capability | Count | Retrieval traces | Answerable | Quality | Avg top_k | Avg hits | Coverage | Stacks |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `llamaindex_turn_frame:input_clarification` | `1` | `0` | `0.0%` | `0.0` | `0.0` | `0.0` | `0.0` | `llamaindex` |
| `python_functions_turn_frame:input_clarification` | `3` | `0` | `0.0%` | `16.0` | `0.0` | `0.0` | `0.0` | `python_functions` |
| `canonical_fact` | `4` | `0` | `0.0%` | `65.0` | `0.0` | `0.0` | `0.0` | `langgraph, python_functions` |
| `teacher_directory` | `3` | `0` | `0.0%` | `66.7` | `0.0` | `0.0` | `0.0` | `langgraph, llamaindex` |
| `python_functions_native_contextual_public_answer` | `3` | `0` | `0.0%` | `71.7` | `0.0` | `0.0` | `0.0` | `python_functions` |
| `public_bundle.facilities_study_support` | `5` | `0` | `0.0%` | `76.0` | `0.0` | `0.0` | `0.0` | `langgraph, llamaindex, python_functions` |
| `public_bundle.governance_protocol` | `2` | `0` | `0.0%` | `76.0` | `0.0` | `0.0` | `0.0` | `llamaindex, python_functions` |
| `llamaindex_turn_frame:protected.administrative.status` | `3` | `0` | `0.0%` | `78.0` | `0.0` | `0.0` | `0.0` | `llamaindex` |
| `auth_guidance` | `1` | `0` | `0.0%` | `80.0` | `0.0` | `0.0` | `0.0` | `llamaindex` |
| `public_bundle.first_month_risks` | `1` | `0` | `0.0%` | `80.0` | `0.0` | `0.0` | `0.0` | `python_functions` |
| `public_bundle.first_month_risks;turn_frame=public.calendar.year_start` | `1` | `0` | `0.0%` | `80.0` | `0.0` | `0.0` | `0.0` | `llamaindex` |
| `python_functions_local_clarify` | `1` | `0` | `0.0%` | `80.0` | `0.0` | `0.0` | `0.0` | `python_functions` |
| `segments` | `1` | `0` | `0.0%` | `80.0` | `0.0` | `0.0` | `0.0` | `llamaindex` |
| `fato institucional canonico deve vir de fonte estruturada` | `6` | `0` | `0.0%` | `90.0` | `0.0` | `0.0` | `0.0` | `langgraph` |
| `consulta autenticada de documento interno deve usar retrieval restrito com grounding` | `4` | `4` | `0.0%` | `90.0` | `3.0` | `0.0` | `1.0` | `langgraph` |

## Recommendations

- `consulta autenticada de documento interno deve usar retrieval restrito com grounding` está com `answerable_rate=0.0%` sem saturar `top_k`; vale revisar query variants, metadata e chunking.

## Trace Samples

### `python_functions` `public_bundle.facilities_study_support` `retrieval_public_facilities_actionable_path`

- Turn: `1`
- Prompt: Na pratica, como a familia deve usar biblioteca, laboratorios e estudo orientado sem se perder?
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `0`, keyword pass `False`, latency `40035.2 ms`
- Reason: `exception`
- Errors: `request_failed`

### `llamaindex` `teacher_directory` `retrieval_public_teacher_directory`

- Turn: `1`
- Prompt: Quero entender o limite publico: falar com o professor de matematica passa por contato direto ou obrigatoriamente pela coordenacao?
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `0`, keyword pass `False`, latency `40021.0 ms`
- Reason: `exception`
- Errors: `request_failed`

### `python_functions` `canonical_fact` `retrieval_restricted_denied_playbook`

- Turn: `1`
- Prompt: Pode abrir para mim o playbook interno de negociacao financeira?
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `0`, keyword pass `False`, latency `40061.0 ms`
- Reason: `exception`
- Errors: `request_failed`

### `python_functions` `python_functions_turn_frame:input_clarification` `retrieval_restricted_teacher_feedback`

- Turn: `1`
- Prompt: Segundo o manual interno do professor, como a escola trata comunicacao pedagogica e feedback ao aluno?
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `0`, keyword pass `False`, latency `40036.5 ms`
- Reason: `exception`
- Errors: `request_failed`

### `python_functions` `python_functions_turn_frame:input_clarification` `retrieval_restricted_teacher_feedback_longform`

- Turn: `1`
- Prompt: Segundo o manual interno do professor, como a escola orienta comunicacao pedagogica, avaliacao registrada e devolutiva ao aluno?
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `32`, keyword pass `False`, latency `17681.2 ms`
- Reason: `python_functions_turn_frame:input_clarification`
- Errors: `missing_expected_keyword, multi_intent_partial_collapse, unnecessary_clarification, weak_actionability`

### `python_functions` `python_functions_native_contextual_public_answer` `retrieval_public_external_library_boundary`

- Turn: `1`
- Prompt: A biblioteca publica da cidade fecha que horas? Se isso fugir da escola, diga claramente.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `35`, keyword pass `False`, latency `20520.0 ms`
- Reason: `python_functions_native_contextual_public_answer`
- Errors: `forbidden_entity_or_value, missing_expected_keyword`

### `llamaindex` `llamaindex_turn_frame:protected.administrative.status` `retrieval_protected_admin_finance_combo`

- Turn: `1`
- Prompt: Cruze meu status documental com o financeiro e diga se existe bloqueio ou pendencia relevante.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `54`, keyword pass `False`, latency `5548.5 ms`
- Reason: `llamaindex_turn_frame:protected.administrative.status`
- Errors: `missing_expected_keyword, multi_intent_partial_collapse`

### `llamaindex` `public_bundle.governance_protocol` `retrieval_public_governance_protocol`

- Turn: `1`
- Prompt: Na governanca publica da escola, como demandas formais chegam a direcao e viram protocolo?
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `76`, keyword pass `True`, latency `19471.8 ms`
- Reason: `llamaindex_public_canonical_lane:public_bundle.governance_protocol`
- Errors: `ungrounded_general_knowledge`

### `python_functions` `public_bundle.governance_protocol` `retrieval_public_governance_protocol`

- Turn: `1`
- Prompt: Na governanca publica da escola, como demandas formais chegam a direcao e viram protocolo?
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `76`, keyword pass `True`, latency `21675.3 ms`
- Reason: `python_functions_native_canonical_lane:public_bundle.governance_protocol`
- Errors: `ungrounded_general_knowledge`

### `llamaindex` `llamaindex_turn_frame:protected.administrative.status` `retrieval_protected_administrative_self_status`

- Turn: `1`
- Prompt: Hoje existe alguma pendencia administrativa no meu cadastro pessoal aqui na escola?
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `80`, keyword pass `False`, latency `2948.5 ms`
- Reason: `llamaindex_turn_frame:protected.administrative.status`
- Errors: `missing_expected_keyword`

### `langgraph` `dados estruturados devem passar por service deterministico` `retrieval_protected_attendance_component_pressure`

- Turn: `1`
- Prompt: Recorte o Lucas e diga onde as ausencias dele mais pressionam a frequencia agora.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `80`, keyword pass `False`, latency `989.3 ms`
- Reason: `dados estruturados devem passar por service deterministico`
- Errors: `missing_expected_keyword`

### `llamaindex` `llamaindex_local_protected:academic` `retrieval_protected_attendance_component_pressure`

- Turn: `1`
- Prompt: Recorte o Lucas e diga onde as ausencias dele mais pressionam a frequencia agora.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `80`, keyword pass `False`, latency `811.9 ms`
- Reason: `llamaindex_local_protected:academic`
- Errors: `missing_expected_keyword`

