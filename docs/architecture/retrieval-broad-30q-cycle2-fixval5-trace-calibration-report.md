# Retrieval Trace Calibration Report

Generated at: 2026-04-15T17:32:25.108181+00:00

Run prefix: `debug:four-path:normal:20260415T172502Z`

Eval JSON: `docs/architecture/retrieval-broad-30q-cycle2-fixval5-cross-path-report.json`

## Stack Summary

| Stack | Count | Retrieval traces | Answerable | Quality | Avg top_k | Avg hits | Avg selected | Coverage | Latency |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `langgraph` | `29` | `5` | `0.0%` | `76.9` | `3.0` | `0.0` | `1.0` | `1.0` | `4653.7 ms` |
| `python_functions` | `30` | `5` | `0.0%` | `74.4` | `6.8` | `0.0` | `1.0` | `1.0` | `4488.6 ms` |
| `llamaindex` | `30` | `0` | `0.0%` | `74.4` | `0.0` | `0.0` | `0.0` | `0.0` | `5694.6 ms` |
| `specialist_supervisor` | `0` | `0` | `0.0%` | `0.0` | `0.0` | `0.0` | `0.0` | `0.0` | `0.0 ms` |

## Capability Highlights

| Capability | Count | Retrieval traces | Answerable | Quality | Avg top_k | Avg hits | Coverage | Stacks |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `a intencao esta ambigua e exige clarificacao antes de recuperar contexto` | `2` | `0` | `0.0%` | `0.0` | `0.0` | `0.0` | `0.0` | `langgraph` |
| `llamaindex_turn_frame:protected.teacher.schedule` | `2` | `0` | `0.0%` | `0.0` | `0.0` | `0.0` | `0.0` | `llamaindex` |
| `python_functions_native_teacher_schedule` | `2` | `0` | `0.0%` | `0.0` | `0.0` | `0.0` | `0.0` | `python_functions` |
| `teacher_role_rescue` | `2` | `0` | `0.0%` | `0.0` | `0.0` | `0.0` | `0.0` | `langgraph` |
| `llamaindex_local_clarify` | `1` | `0` | `0.0%` | `0.0` | `0.0` | `0.0` | `0.0` | `llamaindex` |
| `llamaindex_local_protected:academic` | `1` | `0` | `0.0%` | `0.0` | `0.0` | `0.0` | `0.0` | `llamaindex` |
| `llamaindex_local_public_default:institution` | `1` | `0` | `0.0%` | `0.0` | `0.0` | `0.0` | `0.0` | `llamaindex` |
| `llamaindex_turn_frame:protected.academic.attendance` | `1` | `0` | `0.0%` | `0.0` | `0.0` | `0.0` | `0.0` | `llamaindex` |
| `llamaindex_turn_frame:protected.institution.admin_finance_status` | `1` | `0` | `0.0%` | `0.0` | `0.0` | `0.0` | `0.0` | `llamaindex` |
| `python_functions_local_protected:academic` | `1` | `0` | `0.0%` | `0.0` | `0.0` | `0.0` | `0.0` | `python_functions` |
| `python_functions_native_contextual_public_answer` | `1` | `0` | `0.0%` | `0.0` | `0.0` | `0.0` | `0.0` | `python_functions` |
| `python_functions_turn_frame:protected.academic.attendance` | `1` | `0` | `0.0%` | `0.0` | `0.0` | `0.0` | `0.0` | `python_functions` |
| `python_functions_turn_frame:protected.institution.admin_finance_status` | `1` | `0` | `0.0%` | `0.0` | `0.0` | `0.0` | `0.0` | `python_functions` |
| `status administrativo autenticado exige service deterministico` | `1` | `0` | `0.0%` | `0.0` | `0.0` | `0.0` | `0.0` | `langgraph` |
| `auth_guidance` | `5` | `0` | `0.0%` | `40.0` | `0.0` | `0.0` | `0.0` | `langgraph, llamaindex, python_functions` |

## Recommendations

- `protected.documents.restricted_lookup` está com `answerable_rate=0.0%` sem saturar `top_k`; vale revisar query variants, metadata e chunking.

## Trace Samples

### `langgraph` `status administrativo autenticado exige service deterministico` `retrieval_protected_admin_finance_combo`

- Turn: `1`
- Prompt: Resuma junto documentacao administrativa e financeiro das contas vinculadas para eu saber se ha impedimento de atendimento.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `0`, keyword pass `False`, latency `968.1 ms`
- Reason: `exception`
- Errors: `request_failed`

### `llamaindex` `llamaindex_turn_frame:protected.institution.admin_finance_status` `retrieval_protected_admin_finance_combo`

- Turn: `1`
- Prompt: Resuma junto documentacao administrativa e financeiro das contas vinculadas para eu saber se ha impedimento de atendimento.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `0`, keyword pass `False`, latency `698.2 ms`
- Reason: `exception`
- Errors: `request_failed`

### `python_functions` `python_functions_turn_frame:protected.institution.admin_finance_status` `retrieval_protected_admin_finance_combo`

- Turn: `1`
- Prompt: Resuma junto documentacao administrativa e financeiro das contas vinculadas para eu saber se ha impedimento de atendimento.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `0`, keyword pass `False`, latency `684.0 ms`
- Reason: `exception`
- Errors: `request_failed`

### `langgraph` `dados estruturados devem passar por service deterministico` `retrieval_protected_attendance_panorama`

- Turn: `1`
- Prompt: Agora ignora a Ana e me da so o alerta principal do Lucas por frequencia, sem repetir o panorama todo.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `0`, keyword pass `False`, latency `11887.6 ms`
- Reason: `exception`
- Errors: `request_failed`

### `llamaindex` `llamaindex_local_protected:academic` `retrieval_protected_attendance_panorama`

- Turn: `1`
- Prompt: Agora ignora a Ana e me da so o alerta principal do Lucas por frequencia, sem repetir o panorama todo.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `0`, keyword pass `False`, latency `12677.1 ms`
- Reason: `exception`
- Errors: `request_failed`

### `python_functions` `python_functions_native_family_attendance_aggregate` `retrieval_protected_attendance_panorama`

- Turn: `1`
- Prompt: Agora ignora a Ana e me da so o alerta principal do Lucas por frequencia, sem repetir o panorama todo.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `0`, keyword pass `False`, latency `10485.7 ms`
- Reason: `exception`
- Errors: `request_failed`

### `langgraph` `auth_guidance` `retrieval_protected_boundary_auth_needed`

- Turn: `1`
- Prompt: Se eu pedir minhas notas antes de autenticar, voce mostra ou bloqueia?
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `0`, keyword pass `False`, latency `783.3 ms`
- Reason: `exception`
- Errors: `request_failed`

### `llamaindex` `auth_guidance` `retrieval_protected_boundary_auth_needed`

- Turn: `1`
- Prompt: Se eu pedir minhas notas antes de autenticar, voce mostra ou bloqueia?
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `0`, keyword pass `False`, latency `718.1 ms`
- Reason: `exception`
- Errors: `request_failed`

### `python_functions` `auth_guidance` `retrieval_protected_boundary_auth_needed`

- Turn: `1`
- Prompt: Se eu pedir minhas notas antes de autenticar, voce mostra ou bloqueia?
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `0`, keyword pass `False`, latency `4751.0 ms`
- Reason: `exception`
- Errors: `request_failed`

### `langgraph` `a intencao esta ambigua e exige clarificacao antes de recuperar contexto` `retrieval_protected_family_panorama`

- Turn: `1`
- Prompt: Mantendo a comparacao anterior, tira o Lucas da conversa e mostra so o ponto academico mais fraco da Ana.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `0`, keyword pass `False`, latency `7598.0 ms`
- Reason: `exception`
- Errors: `request_failed`

### `langgraph` `fato institucional canonico deve vir de fonte estruturada` `retrieval_public_external_library_boundary`

- Turn: `1`
- Prompt: Quero saber da biblioteca publica municipal, nao da escola: que horas ela fecha?
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `0`, keyword pass `False`, latency `11813.0 ms`
- Reason: `exception`
- Errors: `request_failed`

### `llamaindex` `llamaindex_local_public_default:institution` `retrieval_public_external_library_boundary`

- Turn: `1`
- Prompt: Quero saber da biblioteca publica municipal, nao da escola: que horas ela fecha?
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `0`, keyword pass `False`, latency `15170.4 ms`
- Reason: `exception`
- Errors: `request_failed`

