# Retrieval Trace Calibration Report

Generated at: 2026-04-15T16:00:54.049449+00:00

Run prefix: `debug:four-path:normal:20260415T155030Z`

Eval JSON: `docs/architecture/retrieval-broad-30q-cycle2-fixval1-cross-path-report.json`

## Stack Summary

| Stack | Count | Retrieval traces | Answerable | Quality | Avg top_k | Avg hits | Avg selected | Coverage | Latency |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `langgraph` | `30` | `5` | `0.0%` | `97.3` | `3.0` | `0.0` | `1.0` | `1.0` | `6854.6 ms` |
| `python_functions` | `30` | `5` | `0.0%` | `95.7` | `6.8` | `0.0` | `1.0` | `1.0` | `7558.8 ms` |
| `llamaindex` | `29` | `0` | `0.0%` | `93.1` | `0.0` | `0.0` | `0.0` | `0.0` | `4855.3 ms` |
| `specialist_supervisor` | `0` | `0` | `0.0%` | `0.0` | `0.0` | `0.0` | `0.0` | `0.0` | `0.0 ms` |

## Capability Highlights

| Capability | Count | Retrieval traces | Answerable | Quality | Avg top_k | Avg hits | Coverage | Stacks |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `llamaindex_turn_frame:protected.academic.attendance` | `1` | `0` | `0.0%` | `0.0` | `0.0` | `0.0` | `0.0` | `llamaindex` |
| `python_functions_local_clarify` | `1` | `0` | `0.0%` | `0.0` | `0.0` | `0.0` | `0.0` | `python_functions` |
| `python_functions_turn_frame:protected.academic.attendance` | `1` | `0` | `0.0%` | `0.0` | `0.0` | `0.0` | `0.0` | `python_functions` |
| `segments` | `1` | `0` | `0.0%` | `0.0` | `0.0` | `0.0` | `0.0` | `langgraph` |
| `llamaindex_local_protected:academic` | `5` | `0` | `0.0%` | `63.8` | `0.0` | `0.0` | `0.0` | `llamaindex` |
| `authenticated_public_profile_rescue` | `1` | `0` | `0.0%` | `68.0` | `0.0` | `0.0` | `0.0` | `langgraph` |
| `python_functions_native_teacher_schedule` | `1` | `0` | `0.0%` | `68.0` | `0.0` | `0.0` | `0.0` | `python_functions` |
| `a intencao esta ambigua e exige clarificacao antes de recuperar contexto` | `2` | `0` | `0.0%` | `80.0` | `0.0` | `0.0` | `0.0` | `langgraph` |
| `llamaindex_local_public_default:institution` | `1` | `0` | `0.0%` | `80.0` | `0.0` | `0.0` | `0.0` | `llamaindex` |
| `python_functions_native_contextual_public_answer` | `1` | `0` | `0.0%` | `80.0` | `0.0` | `0.0` | `0.0` | `python_functions` |
| `python_functions_turn_frame:input_clarification` | `1` | `0` | `0.0%` | `80.0` | `0.0` | `0.0` | `0.0` | `python_functions` |
| `status administrativo autenticado exige service deterministico` | `1` | `0` | `0.0%` | `80.0` | `0.0` | `0.0` | `0.0` | `langgraph` |
| `python_functions_local_protected:academic` | `4` | `0` | `0.0%` | `85.0` | `0.0` | `0.0` | `0.0` | `python_functions` |
| `o turno atual trouxe pistas explicitas de outro dominio protegido e o roteamento foi corrigido` | `3` | `0` | `0.0%` | `93.3` | `0.0` | `0.0` | `0.0` | `langgraph, llamaindex` |
| `protected.documents.restricted_lookup` | `10` | `10` | `0.0%` | `100.0` | `4.9` | `0.0` | `1.0` | `langgraph, python_functions` |

## Recommendations

- `protected.documents.restricted_lookup` está com `answerable_rate=0.0%` sem saturar `top_k`; vale revisar query variants, metadata e chunking.

## Trace Samples

### `llamaindex` `llamaindex_local_protected:academic` `retrieval_teacher_schedule_panorama`

- Turn: `1`
- Prompt: Mantendo o contexto anterior, quero apenas a parte do ensino medio.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `0`, keyword pass `False`, latency `466.2 ms`
- Reason: `exception`
- Errors: `request_failed`

### `llamaindex` `llamaindex_local_protected:academic` `retrieval_protected_family_panorama`

- Turn: `1`
- Prompt: Mantendo a comparacao anterior, tira o Lucas da conversa e mostra so o ponto academico mais fraco da Ana.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `55`, keyword pass `False`, latency `1039.8 ms`
- Reason: `llamaindex_local_protected:academic`
- Errors: `forbidden_entity_or_value`

### `python_functions` `python_functions_local_protected:academic` `retrieval_protected_family_panorama`

- Turn: `1`
- Prompt: Mantendo a comparacao anterior, tira o Lucas da conversa e mostra so o ponto academico mais fraco da Ana.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `55`, keyword pass `False`, latency `1219.3 ms`
- Reason: `python_functions_native_structured:academic`
- Errors: `forbidden_entity_or_value`

### `langgraph` `authenticated_public_profile_rescue` `retrieval_protected_access_scope`

- Turn: `1`
- Prompt: O que eu consigo consultar aqui no Telegram? Quero meu escopo exato entre academico e financeiro.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `68`, keyword pass `False`, latency `13570.5 ms`
- Reason: `authenticated_public_profile_rescue`
- Errors: `missing_expected_keyword, unnecessary_clarification`

### `python_functions` `python_functions_native_teacher_schedule` `retrieval_teacher_schedule_panorama`

- Turn: `1`
- Prompt: Mantendo o contexto anterior, quero apenas a parte do ensino medio.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `68`, keyword pass `False`, latency `20068.3 ms`
- Reason: `python_functions_local_clarify`
- Errors: `missing_expected_keyword, unnecessary_clarification`

### `langgraph` `status administrativo autenticado exige service deterministico` `retrieval_protected_admin_finance_combo`

- Turn: `1`
- Prompt: Resuma junto documentacao administrativa e financeiro das contas vinculadas para eu saber se ha impedimento de atendimento.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `80`, keyword pass `False`, latency `12802.8 ms`
- Reason: `status administrativo autenticado exige service deterministico`
- Errors: `missing_expected_keyword`

### `llamaindex` `o turno atual trouxe pistas explicitas de outro dominio protegido e o roteamento foi corrigido` `retrieval_protected_admin_finance_combo`

- Turn: `1`
- Prompt: Resuma junto documentacao administrativa e financeiro das contas vinculadas para eu saber se ha impedimento de atendimento.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `80`, keyword pass `False`, latency `1044.4 ms`
- Reason: `llamaindex_protected_records_fast_path`
- Errors: `missing_expected_keyword`

### `python_functions` `python_functions_turn_frame:input_clarification` `retrieval_protected_admin_finance_combo`

- Turn: `1`
- Prompt: Resuma junto documentacao administrativa e financeiro das contas vinculadas para eu saber se ha impedimento de atendimento.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `80`, keyword pass `False`, latency `36682.0 ms`
- Reason: `python_functions_turn_frame:input_clarification`
- Errors: `missing_expected_keyword`

### `langgraph` `a intencao esta ambigua e exige clarificacao antes de recuperar contexto` `retrieval_protected_family_panorama`

- Turn: `1`
- Prompt: Mantendo a comparacao anterior, tira o Lucas da conversa e mostra so o ponto academico mais fraco da Ana.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `80`, keyword pass `False`, latency `14220.0 ms`
- Reason: `a intencao esta ambigua e exige clarificacao antes de recuperar contexto`
- Errors: `missing_expected_keyword`

### `llamaindex` `llamaindex_local_public_default:institution` `retrieval_public_external_library_boundary`

- Turn: `1`
- Prompt: Quero saber da biblioteca publica municipal, nao da escola: que horas ela fecha?
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `80`, keyword pass `False`, latency `15370.3 ms`
- Reason: `llamaindex_contextual_public_boundary_fast_path`
- Errors: `missing_expected_keyword`

### `python_functions` `python_functions_native_contextual_public_answer` `retrieval_public_external_library_boundary`

- Turn: `1`
- Prompt: Quero saber da biblioteca publica municipal, nao da escola: que horas ela fecha?
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `80`, keyword pass `False`, latency `17224.4 ms`
- Reason: `python_functions_native_contextual_public_answer`
- Errors: `missing_expected_keyword`

### `llamaindex` `llamaindex_local_protected:finance` `retrieval_protected_access_scope`

- Turn: `1`
- Prompt: O que eu consigo consultar aqui no Telegram? Quero meu escopo exato entre academico e financeiro.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `100`, keyword pass `True`, latency `559.7 ms`
- Reason: `llamaindex_local_protected:finance`

