# Retrieval Trace Calibration Report

Generated at: 2026-04-16T17:11:07.911198+00:00

Run prefix: `debug:four-path:normal:20260416T170131Z`

Eval JSON: `docs/architecture/retrieval-broad-30q-cycle11-baseline-cross-path-report.json`

## Stack Summary

| Stack | Count | Retrieval traces | Answerable | Quality | Avg top_k | Avg hits | Avg selected | Coverage | Latency |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `langgraph` | `28` | `5` | `0.0%` | `99.5` | `3.0` | `0.0` | `0.8` | `1.0` | `6762.0 ms` |
| `python_functions` | `30` | `5` | `0.0%` | `99.6` | `6.6` | `0.0` | `0.8` | `1.0` | `4239.1 ms` |
| `llamaindex` | `29` | `0` | `0.0%` | `100.0` | `0.0` | `0.0` | `0.0` | `0.0` | `3779.4 ms` |
| `specialist_supervisor` | `0` | `0` | `0.0%` | `0.0` | `0.0` | `0.0` | `0.0` | `0.0` | `0.0 ms` |

## Capability Highlights

| Capability | Count | Retrieval traces | Answerable | Quality | Avg top_k | Avg hits | Coverage | Stacks |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `a intencao esta ambigua e exige clarificacao antes de recuperar contexto` | `1` | `0` | `0.0%` | `88.0` | `0.0` | `0.0` | `0.0` | `langgraph` |
| `python_functions_local_public_unknown_safe_clarify` | `2` | `0` | `0.0%` | `94.0` | `0.0` | `0.0` | `0.0` | `python_functions` |
| `protected.documents.restricted_lookup` | `10` | `10` | `0.0%` | `100.0` | `4.8` | `0.0` | `1.0` | `langgraph, python_functions` |
| `dados estruturados devem passar por service deterministico` | `7` | `0` | `0.0%` | `100.0` | `0.0` | `0.0` | `0.0` | `langgraph` |
| `python_functions_native_protected_focus:academic` | `5` | `0` | `0.0%` | `100.0` | `0.0` | `0.0` | `0.0` | `python_functions` |
| `llamaindex_local_restricted_documents;turn_frame=protected.documents.restricted_lookup` | `4` | `0` | `0.0%` | `100.0` | `0.0` | `0.0` | `0.0` | `llamaindex` |
| `auth_guidance` | `3` | `0` | `0.0%` | `100.0` | `0.0` | `0.0` | `0.0` | `langgraph, llamaindex, python_functions` |
| `llamaindex_local_public_unknown_safe_clarify` | `3` | `0` | `0.0%` | `100.0` | `0.0` | `0.0` | `0.0` | `llamaindex` |
| `public_bundle.academic_policy_overview` | `3` | `0` | `0.0%` | `100.0` | `0.0` | `0.0` | `0.0` | `langgraph, llamaindex, python_functions` |
| `public_bundle.family_new_calendar_assessment_enrollment` | `3` | `0` | `0.0%` | `100.0` | `0.0` | `0.0` | `0.0` | `langgraph, llamaindex, python_functions` |
| `public_bundle.governance_protocol` | `3` | `0` | `0.0%` | `100.0` | `0.0` | `0.0` | `0.0` | `langgraph, llamaindex, python_functions` |
| `leadership` | `2` | `0` | `0.0%` | `100.0` | `0.0` | `0.0` | `0.0` | `langgraph, python_functions` |
| `llamaindex_local_protected:academic` | `2` | `0` | `0.0%` | `100.0` | `0.0` | `0.0` | `0.0` | `llamaindex` |
| `llamaindex_local_public_documentary:institution` | `2` | `0` | `0.0%` | `100.0` | `0.0` | `0.0` | `0.0` | `llamaindex` |
| `llamaindex_local_public_fact:institution` | `2` | `0` | `0.0%` | `100.0` | `0.0` | `0.0` | `0.0` | `llamaindex` |

## Recommendations

- `protected.documents.restricted_lookup` está com `answerable_rate=0.0%` sem saturar `top_k`; vale revisar query variants, metadata e chunking.

## Trace Samples

### `langgraph` `a intencao esta ambigua e exige clarificacao antes de recuperar contexto` `retrieval_public_open_world_out_of_scope`

- Turn: `1`
- Prompt: Me ajuda a escolher um filme para o fim de semana. Responda de forma direta.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `88`, keyword pass `True`, latency `84848.7 ms`
- Reason: `a intencao esta ambigua e exige clarificacao antes de recuperar contexto`
- Errors: `unnecessary_clarification`

### `python_functions` `python_functions_local_public_unknown_safe_clarify` `retrieval_public_open_world_out_of_scope`

- Turn: `1`
- Prompt: Me ajuda a escolher um filme para o fim de semana. Responda de forma direta.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `88`, keyword pass `True`, latency `20822.6 ms`
- Reason: `python_functions_local_public_unknown_safe_clarify`
- Errors: `unnecessary_clarification`

### `langgraph` `o turno atual trouxe pistas explicitas de outro dominio protegido e o roteamento foi corrigido` `retrieval_protected_access_scope`

- Turn: `1`
- Prompt: Pensando no caso pratico, quais dados dos meus filhos eu consigo acessar por aqui, e se o meu acesso cobre academico e financeiro?
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `100`, keyword pass `True`, latency `1008.2 ms`
- Reason: `o turno atual trouxe pistas explicitas de outro dominio protegido e o roteamento foi corrigido`

### `llamaindex` `o turno atual trouxe pistas explicitas de outro dominio protegido e o roteamento foi corrigido` `retrieval_protected_access_scope`

- Turn: `1`
- Prompt: Pensando no caso pratico, quais dados dos meus filhos eu consigo acessar por aqui, e se o meu acesso cobre academico e financeiro?
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `100`, keyword pass `True`, latency `649.4 ms`
- Reason: `o turno atual trouxe pistas explicitas de outro dominio protegido e o roteamento foi corrigido`

### `python_functions` `python_functions_native_authenticated_account_scope` `retrieval_protected_access_scope`

- Turn: `1`
- Prompt: Pensando no caso pratico, quais dados dos meus filhos eu consigo acessar por aqui, e se o meu acesso cobre academico e financeiro?
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `100`, keyword pass `True`, latency `616.2 ms`
- Reason: `python_functions_native_authenticated_account_scope`

### `langgraph` `status administrativo autenticado exige service deterministico` `retrieval_protected_admin_docs`

- Turn: `1`
- Prompt: De forma bem objetiva, quero um retrato das pendencias documentais da Ana e do proximo passo para regularizar tudo.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `100`, keyword pass `True`, latency `2294.1 ms`
- Reason: `status administrativo autenticado exige service deterministico`

### `llamaindex` `llamaindex_turn_frame:protected.administrative.status` `retrieval_protected_admin_docs`

- Turn: `1`
- Prompt: De forma bem objetiva, quero um retrato das pendencias documentais da Ana e do proximo passo para regularizar tudo.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `100`, keyword pass `True`, latency `1380.8 ms`
- Reason: `llamaindex_turn_frame:protected.administrative.status`

### `python_functions` `python_functions_turn_frame:protected.administrative.status` `retrieval_protected_admin_docs`

- Turn: `1`
- Prompt: De forma bem objetiva, quero um retrato das pendencias documentais da Ana e do proximo passo para regularizar tudo.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `100`, keyword pass `True`, latency `1467.6 ms`
- Reason: `python_functions_native_structured:institution`

### `langgraph` `status administrativo autenticado exige service deterministico` `retrieval_protected_admin_finance_combo`

- Turn: `1`
- Prompt: Minha documentacao ou cadastro esta bloqueando atendimento financeiro? Quero um panorama combinado de documentacao e financeiro. Responda de forma direta.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `100`, keyword pass `True`, latency `1247.5 ms`
- Reason: `status administrativo autenticado exige service deterministico`

### `llamaindex` `llamaindex_turn_frame:protected.institution.admin_finance_status` `retrieval_protected_admin_finance_combo`

- Turn: `1`
- Prompt: Minha documentacao ou cadastro esta bloqueando atendimento financeiro? Quero um panorama combinado de documentacao e financeiro. Responda de forma direta.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `100`, keyword pass `True`, latency `1119.8 ms`
- Reason: `llamaindex_turn_frame:protected.institution.admin_finance_status`

### `python_functions` `python_functions_turn_frame:protected.institution.admin_finance_status` `retrieval_protected_admin_finance_combo`

- Turn: `1`
- Prompt: Minha documentacao ou cadastro esta bloqueando atendimento financeiro? Quero um panorama combinado de documentacao e financeiro. Responda de forma direta.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `100`, keyword pass `True`, latency `981.0 ms`
- Reason: `python_functions_native_structured:institution`

### `langgraph` `dados estruturados devem passar por service deterministico` `retrieval_protected_attendance_panorama`

- Turn: `1`
- Prompt: Sem sair do escopo do projeto, agora foque so no Lucas e diga o que mais preocupa na frequencia dele.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `100`, keyword pass `True`, latency `873.5 ms`
- Reason: `dados estruturados devem passar por service deterministico`

