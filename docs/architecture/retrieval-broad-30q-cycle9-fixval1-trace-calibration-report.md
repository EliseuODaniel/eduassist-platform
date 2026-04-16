# Retrieval Trace Calibration Report

Generated at: 2026-04-16T16:13:40.623846+00:00

Run prefix: `debug:four-path:normal:20260416T160828Z`

Eval JSON: `docs/architecture/retrieval-broad-30q-cycle9-fixval1-cross-path-report.json`

## Stack Summary

| Stack | Count | Retrieval traces | Answerable | Quality | Avg top_k | Avg hits | Avg selected | Coverage | Latency |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `langgraph` | `27` | `5` | `0.0%` | `100.0` | `3.0` | `0.0` | `0.8` | `1.0` | `2980.0 ms` |
| `python_functions` | `30` | `5` | `0.0%` | `100.0` | `6.8` | `0.0` | `0.8` | `1.0` | `3776.2 ms` |
| `llamaindex` | `30` | `0` | `0.0%` | `100.0` | `0.0` | `0.0` | `0.0` | `0.0` | `3461.4 ms` |
| `specialist_supervisor` | `0` | `0` | `0.0%` | `0.0` | `0.0` | `0.0` | `0.0` | `0.0` | `0.0 ms` |

## Capability Highlights

| Capability | Count | Retrieval traces | Answerable | Quality | Avg top_k | Avg hits | Coverage | Stacks |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `llamaindex_turn_frame:protected.academic.family_comparison` | `1` | `0` | `0.0%` | `0.0` | `0.0` | `0.0` | `0.0` | `llamaindex` |
| `llamaindex_turn_frame:protected.teacher.schedule` | `1` | `0` | `0.0%` | `0.0` | `0.0` | `0.0` | `0.0` | `llamaindex` |
| `protected.documents.restricted_lookup` | `10` | `10` | `0.0%` | `100.0` | `4.9` | `0.0` | `1.0` | `langgraph, python_functions` |
| `dados estruturados devem passar por service deterministico` | `6` | `0` | `0.0%` | `100.0` | `0.0` | `0.0` | `0.0` | `langgraph` |
| `llamaindex_local_restricted_documents;turn_frame=protected.documents.restricted_lookup` | `5` | `0` | `0.0%` | `100.0` | `0.0` | `0.0` | `0.0` | `llamaindex` |
| `o turno atual trouxe pistas explicitas de outro dominio protegido e o roteamento foi corrigido` | `5` | `0` | `0.0%` | `100.0` | `0.0` | `0.0` | `0.0` | `langgraph, llamaindex` |
| `python_functions_native_protected_focus:academic` | `5` | `0` | `0.0%` | `100.0` | `0.0` | `0.0` | `0.0` | `python_functions` |
| `llamaindex_local_protected:academic` | `4` | `0` | `0.0%` | `100.0` | `0.0` | `0.0` | `0.0` | `llamaindex` |
| `auth_guidance` | `3` | `0` | `0.0%` | `100.0` | `0.0` | `0.0` | `0.0` | `langgraph, llamaindex, python_functions` |
| `llamaindex_local_public_unknown_safe_clarify` | `3` | `0` | `0.0%` | `100.0` | `0.0` | `0.0` | `0.0` | `llamaindex` |
| `public_bundle.academic_policy_overview` | `3` | `0` | `0.0%` | `100.0` | `0.0` | `0.0` | `0.0` | `langgraph, llamaindex, python_functions` |
| `public_bundle.facilities_study_support` | `3` | `0` | `0.0%` | `100.0` | `0.0` | `0.0` | `0.0` | `langgraph, llamaindex, python_functions` |
| `public_bundle.governance_protocol` | `3` | `0` | `0.0%` | `100.0` | `0.0` | `0.0` | `0.0` | `langgraph, llamaindex, python_functions` |
| `public_bundle.secretaria_portal_credentials` | `3` | `0` | `0.0%` | `100.0` | `0.0` | `0.0` | `0.0` | `langgraph, llamaindex, python_functions` |
| `llamaindex_local_public_fact:institution` | `2` | `0` | `0.0%` | `100.0` | `0.0` | `0.0` | `0.0` | `llamaindex` |

## Recommendations

- `protected.documents.restricted_lookup` está com `answerable_rate=0.0%` sem saturar `top_k`; vale revisar query variants, metadata e chunking.

## Trace Samples

### `langgraph` `o turno atual trouxe pistas explicitas de outro dominio protegido e o roteamento foi corrigido` `retrieval_protected_access_scope`

- Turn: `1`
- Prompt: Quais dados dos meus filhos eu consigo acessar por aqui, e se o meu acesso cobre academico e financeiro. Responda de forma direta.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `100`, keyword pass `True`, latency `1201.9 ms`
- Reason: `o turno atual trouxe pistas explicitas de outro dominio protegido e o roteamento foi corrigido`

### `llamaindex` `o turno atual trouxe pistas explicitas de outro dominio protegido e o roteamento foi corrigido` `retrieval_protected_access_scope`

- Turn: `1`
- Prompt: Quais dados dos meus filhos eu consigo acessar por aqui, e se o meu acesso cobre academico e financeiro. Responda de forma direta.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `100`, keyword pass `True`, latency `922.0 ms`
- Reason: `o turno atual trouxe pistas explicitas de outro dominio protegido e o roteamento foi corrigido`

### `python_functions` `python_functions_native_authenticated_account_scope` `retrieval_protected_access_scope`

- Turn: `1`
- Prompt: Quais dados dos meus filhos eu consigo acessar por aqui, e se o meu acesso cobre academico e financeiro. Responda de forma direta.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `100`, keyword pass `True`, latency `928.1 ms`
- Reason: `python_functions_native_authenticated_account_scope`

### `langgraph` `o turno atual trouxe pistas explicitas de outro dominio protegido e o roteamento foi corrigido` `retrieval_protected_admin_docs`

- Turn: `1`
- Prompt: Sem sair do escopo do projeto, hoje, o que ainda falta na parte administrativa da Ana e como a familia deve agir em seguida?
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `100`, keyword pass `True`, latency `957.3 ms`
- Reason: `o turno atual trouxe pistas explicitas de outro dominio protegido e o roteamento foi corrigido`

### `llamaindex` `o turno atual trouxe pistas explicitas de outro dominio protegido e o roteamento foi corrigido` `retrieval_protected_admin_docs`

- Turn: `1`
- Prompt: Sem sair do escopo do projeto, hoje, o que ainda falta na parte administrativa da Ana e como a familia deve agir em seguida?
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `100`, keyword pass `True`, latency `712.5 ms`
- Reason: `o turno atual trouxe pistas explicitas de outro dominio protegido e o roteamento foi corrigido`

### `python_functions` `python_functions_native_family_attendance_aggregate` `retrieval_protected_admin_docs`

- Turn: `1`
- Prompt: Sem sair do escopo do projeto, hoje, o que ainda falta na parte administrativa da Ana e como a familia deve agir em seguida?
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `100`, keyword pass `True`, latency `613.1 ms`
- Reason: `python_functions_native_family_attendance_aggregate`

### `langgraph` `status administrativo autenticado exige service deterministico` `retrieval_protected_admin_finance_combo`

- Turn: `1`
- Prompt: Minha documentacao ou cadastro esta bloqueando atendimento financeiro? Quero um panorama combinado de documentacao e financeiro. Seja objetivo e grounded.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `100`, keyword pass `True`, latency `1662.6 ms`
- Reason: `status administrativo autenticado exige service deterministico`

### `llamaindex` `llamaindex_turn_frame:protected.institution.admin_finance_status` `retrieval_protected_admin_finance_combo`

- Turn: `1`
- Prompt: Minha documentacao ou cadastro esta bloqueando atendimento financeiro? Quero um panorama combinado de documentacao e financeiro. Seja objetivo e grounded.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `100`, keyword pass `True`, latency `889.6 ms`
- Reason: `llamaindex_turn_frame:protected.institution.admin_finance_status`

### `python_functions` `python_functions_turn_frame:protected.institution.admin_finance_status` `retrieval_protected_admin_finance_combo`

- Turn: `1`
- Prompt: Minha documentacao ou cadastro esta bloqueando atendimento financeiro? Quero um panorama combinado de documentacao e financeiro. Seja objetivo e grounded.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `100`, keyword pass `True`, latency `1301.2 ms`
- Reason: `python_functions_native_structured:institution`

### `langgraph` `dados estruturados devem passar por service deterministico` `retrieval_protected_attendance_panorama`

- Turn: `1`
- Prompt: Mantendo o contexto, corta para o Lucas e resume qual e o risco mais concreto dele em frequencia. Responda de forma direta.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `100`, keyword pass `True`, latency `901.8 ms`
- Reason: `dados estruturados devem passar por service deterministico`

### `llamaindex` `llamaindex_local_protected:academic` `retrieval_protected_attendance_panorama`

- Turn: `1`
- Prompt: Mantendo o contexto, corta para o Lucas e resume qual e o risco mais concreto dele em frequencia. Responda de forma direta.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `100`, keyword pass `True`, latency `632.8 ms`
- Reason: `llamaindex_local_protected:academic`

### `python_functions` `python_functions_native_family_attendance_aggregate` `retrieval_protected_attendance_panorama`

- Turn: `1`
- Prompt: Mantendo o contexto, corta para o Lucas e resume qual e o risco mais concreto dele em frequencia. Responda de forma direta.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `100`, keyword pass `True`, latency `713.6 ms`
- Reason: `python_functions_native_structured:academic`

