# Retrieval Trace Calibration Report

Generated at: 2026-04-15T06:05:23.808362+00:00

Run prefix: `debug:four-path:normal:20260415T055537Z`

Eval JSON: `docs/architecture/retrieval-broad-30q-cycle1-rerun-cross-path-report.json`

## Stack Summary

| Stack | Count | Retrieval traces | Answerable | Quality | Avg top_k | Avg hits | Avg selected | Coverage | Latency |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `langgraph` | `30` | `4` | `0.0%` | `89.0` | `3.0` | `0.0` | `0.75` | `1.0` | `5530.3 ms` |
| `python_functions` | `30` | `5` | `0.0%` | `89.4` | `6.2` | `0.8` | `1.4` | `1.0` | `6469.2 ms` |
| `llamaindex` | `29` | `1` | `0.0%` | `84.0` | `4.0` | `4.0` | `4.0` | `1.0` | `6560.9 ms` |
| `specialist_supervisor` | `0` | `0` | `0.0%` | `0.0` | `0.0` | `0.0` | `0.0` | `0.0` | `0.0 ms` |

## Capability Highlights

| Capability | Count | Retrieval traces | Answerable | Quality | Avg top_k | Avg hits | Coverage | Stacks |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `llamaindex_turn_frame:protected.academic.attendance` | `1` | `0` | `0.0%` | `0.0` | `0.0` | `0.0` | `0.0` | `llamaindex` |
| `python_functions_turn_frame:protected.academic.attendance` | `1` | `0` | `0.0%` | `0.0` | `0.0` | `0.0` | `0.0` | `python_functions` |
| `consulta publica de navegacao e canais foi resgatada do dominio support` | `1` | `0` | `0.0%` | `19.0` | `0.0` | `0.0` | `0.0` | `langgraph` |
| `langgraph_turn_frame:public.facilities.library.hours` | `1` | `0` | `0.0%` | `35.0` | `0.0` | `0.0` | `0.0` | `langgraph` |
| `llamaindex_local_public_fact:institution;turn_frame=public.facilities.library.hours` | `1` | `0` | `0.0%` | `35.0` | `0.0` | `0.0` | `0.0` | `llamaindex` |
| `teacher_directory` | `2` | `0` | `0.0%` | `50.0` | `0.0` | `0.0` | `0.0` | `llamaindex` |
| `llamaindex_local_protected:institution` | `1` | `0` | `0.0%` | `54.0` | `0.0` | `0.0` | `0.0` | `llamaindex` |
| `python_functions_local_protected:institution` | `1` | `0` | `0.0%` | `54.0` | `0.0` | `0.0` | `0.0` | `python_functions` |
| `status administrativo autenticado exige service deterministico` | `1` | `0` | `0.0%` | `54.0` | `0.0` | `0.0` | `0.0` | `langgraph` |
| `python_functions_native_public_compound` | `3` | `0` | `0.0%` | `65.0` | `0.0` | `0.0` | `0.0` | `python_functions` |
| `langgraph_turn_frame:scope_boundary` | `2` | `0` | `0.0%` | `67.5` | `0.0` | `0.0` | `0.0` | `langgraph` |
| `llamaindex_local_public_unknown_safe_clarify` | `2` | `0` | `0.0%` | `67.5` | `0.0` | `0.0` | `0.0` | `llamaindex` |
| `python_functions_turn_frame:scope_boundary` | `3` | `0` | `0.0%` | `78.3` | `0.0` | `0.0` | `0.0` | `python_functions` |
| `llamaindex_local_public_fact:institution` | `2` | `0` | `0.0%` | `80.0` | `0.0` | `0.0` | `0.0` | `llamaindex` |
| `python_functions_native_teacher_schedule` | `2` | `0` | `0.0%` | `80.0` | `0.0` | `0.0` | `0.0` | `python_functions` |

## Recommendations

- `protected.documents.restricted_lookup` está com `answerable_rate=0.0%` sem saturar `top_k`; vale revisar query variants, metadata e chunking.

## Trace Samples

### `llamaindex` `teacher_directory` `retrieval_public_teacher_directory`

- Turn: `1`
- Prompt: Sem sair do escopo do projeto, existe canal publico com nome ou contato do professor de matematica, ou isso vai pela coordenacao pedagogica?
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `0`, keyword pass `False`, latency `35056.0 ms`
- Reason: `exception`
- Errors: `request_failed`

### `langgraph` `consulta publica de navegacao e canais foi resgatada do dominio support` `retrieval_public_governance_protocol`

- Turn: `1`
- Prompt: Na base publica, como aparecem conectados direcao, atendimento formal e numero de protocolo?
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `19`, keyword pass `False`, latency `2013.0 ms`
- Reason: `consulta publica de navegacao e canais foi resgatada do dominio support`
- Errors: `missing_expected_keyword, multi_intent_partial_collapse, public_explanatory_misroute`

### `langgraph` `langgraph_turn_frame:public.facilities.library.hours` `retrieval_public_external_library_boundary`

- Turn: `1`
- Prompt: Fora do Colegio Horizonte, qual e o horario da biblioteca publica da cidade?
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `35`, keyword pass `False`, latency `433.8 ms`
- Reason: `langgraph_turn_frame:scope_boundary`
- Errors: `forbidden_entity_or_value, missing_expected_keyword`

### `llamaindex` `llamaindex_local_public_fact:institution;turn_frame=public.facilities.library.hours` `retrieval_public_external_library_boundary`

- Turn: `1`
- Prompt: Fora do Colegio Horizonte, qual e o horario da biblioteca publica da cidade?
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `35`, keyword pass `False`, latency `295.1 ms`
- Reason: `llamaindex_contextual_public_boundary_fast_path`
- Errors: `forbidden_entity_or_value, missing_expected_keyword`

### `python_functions` `python_functions_native_public_compound` `retrieval_public_external_library_boundary`

- Turn: `1`
- Prompt: Fora do Colegio Horizonte, qual e o horario da biblioteca publica da cidade?
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `35`, keyword pass `False`, latency `3857.8 ms`
- Reason: `python_functions_native_public_compound`
- Errors: `forbidden_entity_or_value, missing_expected_keyword`

### `llamaindex` `llamaindex_local_public_unknown_safe_clarify` `retrieval_public_open_world_out_of_scope`

- Turn: `1`
- Prompt: Fora do tema escolar, qual filme voce acha que mais vale a pena ver agora?
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `35`, keyword pass `False`, latency `2582.7 ms`
- Reason: `llamaindex_contextual_public_direct_fast_path`
- Errors: `forbidden_entity_or_value, missing_expected_keyword`

### `langgraph` `status administrativo autenticado exige service deterministico` `retrieval_protected_admin_finance_combo`

- Turn: `1`
- Prompt: Tem algo na minha documentacao ou no cadastro que esteja travando o financeiro? Me de a visao combinada.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `54`, keyword pass `False`, latency `11339.3 ms`
- Reason: `status administrativo autenticado exige service deterministico`
- Errors: `missing_expected_keyword, multi_intent_partial_collapse`

### `llamaindex` `llamaindex_local_protected:institution` `retrieval_protected_admin_finance_combo`

- Turn: `1`
- Prompt: Tem algo na minha documentacao ou no cadastro que esteja travando o financeiro? Me de a visao combinada.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `54`, keyword pass `False`, latency `10972.1 ms`
- Reason: `llamaindex_protected_records_fast_path`
- Errors: `missing_expected_keyword, multi_intent_partial_collapse`

### `python_functions` `python_functions_local_protected:institution` `retrieval_protected_admin_finance_combo`

- Turn: `1`
- Prompt: Tem algo na minha documentacao ou no cadastro que esteja travando o financeiro? Me de a visao combinada.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `54`, keyword pass `False`, latency `11152.6 ms`
- Reason: `python_functions_native_structured:institution`
- Errors: `missing_expected_keyword, multi_intent_partial_collapse`

### `langgraph` `langgraph_turn_frame:scope_boundary` `retrieval_public_open_world_out_of_scope`

- Turn: `1`
- Prompt: Fora do tema escolar, qual filme voce acha que mais vale a pena ver agora?
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `55`, keyword pass `False`, latency `2098.4 ms`
- Reason: `langgraph_turn_frame:scope_boundary`
- Errors: `forbidden_entity_or_value`

### `python_functions` `python_functions_turn_frame:scope_boundary` `retrieval_public_open_world_out_of_scope`

- Turn: `1`
- Prompt: Fora do tema escolar, qual filme voce acha que mais vale a pena ver agora?
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `55`, keyword pass `False`, latency `5528.3 ms`
- Reason: `python_functions_turn_frame:scope_boundary`
- Errors: `forbidden_entity_or_value`

### `python_functions` `python_functions_local_clarify` `retrieval_protected_boundary_auth_needed`

- Turn: `1`
- Prompt: Nao estou autenticado e mesmo assim quero consultar meu boletim aqui pelo bot.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `80`, keyword pass `False`, latency `10580.7 ms`
- Reason: `python_functions_local_clarify`
- Errors: `missing_expected_keyword`

