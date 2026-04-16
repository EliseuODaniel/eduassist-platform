# Retrieval Trace Calibration Report

Generated at: 2026-04-16T13:04:45.706727+00:00

Run prefix: `debug:four-path:normal:20260416T130030Z`

Eval JSON: `docs/architecture/retrieval-broad-30q-cycle7-baseline-cross-path-report.json`

## Stack Summary

| Stack | Count | Retrieval traces | Answerable | Quality | Avg top_k | Avg hits | Avg selected | Coverage | Latency |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `langgraph` | `27` | `5` | `0.0%` | `98.2` | `3.0` | `0.0` | `1.0` | `1.0` | `2198.0 ms` |
| `python_functions` | `30` | `5` | `0.0%` | `98.4` | `6.8` | `0.0` | `1.0` | `1.0` | `2897.4 ms` |
| `llamaindex` | `30` | `0` | `0.0%` | `100.0` | `0.0` | `0.0` | `0.0` | `0.0` | `2656.7 ms` |
| `specialist_supervisor` | `0` | `0` | `0.0%` | `0.0` | `0.0` | `0.0` | `0.0` | `0.0` | `0.0 ms` |

## Capability Highlights

| Capability | Count | Retrieval traces | Answerable | Quality | Avg top_k | Avg hits | Coverage | Stacks |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `llamaindex_turn_frame:protected.academic.attendance` | `1` | `0` | `0.0%` | `0.0` | `0.0` | `0.0` | `0.0` | `llamaindex` |
| `python_functions_turn_frame:scope_boundary` | `1` | `0` | `0.0%` | `0.0` | `0.0` | `0.0` | `0.0` | `python_functions` |
| `python_functions_native_protected_focus:academic` | `4` | `0` | `0.0%` | `86.0` | `0.0` | `0.0` | `0.0` | `python_functions` |
| `dados estruturados devem passar por service deterministico` | `6` | `0` | `0.0%` | `91.6` | `0.0` | `0.0` | `0.0` | `langgraph` |
| `protected.documents.restricted_lookup` | `10` | `10` | `0.0%` | `100.0` | `4.9` | `0.0` | `1.0` | `langgraph, python_functions` |
| `llamaindex_local_restricted_documents;turn_frame=protected.documents.restricted_lookup` | `5` | `0` | `0.0%` | `100.0` | `0.0` | `0.0` | `0.0` | `llamaindex` |
| `auth_guidance` | `3` | `0` | `0.0%` | `100.0` | `0.0` | `0.0` | `0.0` | `langgraph, llamaindex, python_functions` |
| `llamaindex_local_public_fact:institution` | `3` | `0` | `0.0%` | `100.0` | `0.0` | `0.0` | `0.0` | `llamaindex` |
| `llamaindex_local_public_unknown_safe_clarify` | `3` | `0` | `0.0%` | `100.0` | `0.0` | `0.0` | `0.0` | `llamaindex` |
| `public_bundle.academic_policy_overview` | `3` | `0` | `0.0%` | `100.0` | `0.0` | `0.0` | `0.0` | `langgraph, llamaindex, python_functions` |
| `public_bundle.facilities_study_support` | `3` | `0` | `0.0%` | `100.0` | `0.0` | `0.0` | `0.0` | `langgraph, llamaindex, python_functions` |
| `public_bundle.family_new_calendar_assessment_enrollment` | `3` | `0` | `0.0%` | `100.0` | `0.0` | `0.0` | `0.0` | `langgraph, llamaindex, python_functions` |
| `public_bundle.governance_protocol` | `3` | `0` | `0.0%` | `100.0` | `0.0` | `0.0` | `0.0` | `langgraph, llamaindex, python_functions` |
| `public_bundle.secretaria_portal_credentials` | `3` | `0` | `0.0%` | `100.0` | `0.0` | `0.0` | `0.0` | `langgraph, llamaindex, python_functions` |
| `langgraph_turn_frame:scope_boundary` | `2` | `0` | `0.0%` | `100.0` | `0.0` | `0.0` | `0.0` | `langgraph` |

## Recommendations

- `protected.documents.restricted_lookup` está com `answerable_rate=0.0%` sem saturar `top_k`; vale revisar query variants, metadata e chunking.

## Trace Samples

### `langgraph` `dados estruturados devem passar por service deterministico` `retrieval_protected_family_panorama`

- Turn: `1`
- Prompt: Pensando no caso pratico, agora quero apenas a Ana: em quais materias ela aparece mais exposta?
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `58`, keyword pass `False`, latency `550.5 ms`
- Reason: `langgraph_turn_frame:scope_boundary`
- Errors: `missing_expected_keyword, partial_scope_loss`

### `python_functions` `python_functions_native_protected_focus:academic` `retrieval_protected_family_panorama`

- Turn: `1`
- Prompt: Pensando no caso pratico, agora quero apenas a Ana: em quais materias ela aparece mais exposta?
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `58`, keyword pass `False`, latency `562.1 ms`
- Reason: `python_functions_turn_frame:scope_boundary`
- Errors: `missing_expected_keyword, partial_scope_loss`

### `langgraph` `o turno atual trouxe pistas explicitas de outro dominio protegido e o roteamento foi corrigido` `retrieval_protected_access_scope`

- Turn: `1`
- Prompt: De forma bem objetiva, quais dados dos meus filhos eu consigo acessar por aqui, e se o meu acesso cobre academico e financeiro?
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `100`, keyword pass `True`, latency `1130.2 ms`
- Reason: `o turno atual trouxe pistas explicitas de outro dominio protegido e o roteamento foi corrigido`

### `llamaindex` `o turno atual trouxe pistas explicitas de outro dominio protegido e o roteamento foi corrigido` `retrieval_protected_access_scope`

- Turn: `1`
- Prompt: De forma bem objetiva, quais dados dos meus filhos eu consigo acessar por aqui, e se o meu acesso cobre academico e financeiro?
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `100`, keyword pass `True`, latency `592.1 ms`
- Reason: `o turno atual trouxe pistas explicitas de outro dominio protegido e o roteamento foi corrigido`

### `python_functions` `python_functions_native_authenticated_account_scope` `retrieval_protected_access_scope`

- Turn: `1`
- Prompt: De forma bem objetiva, quais dados dos meus filhos eu consigo acessar por aqui, e se o meu acesso cobre academico e financeiro?
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `100`, keyword pass `True`, latency `552.9 ms`
- Reason: `python_functions_native_authenticated_account_scope`

### `langgraph` `status administrativo autenticado exige service deterministico` `retrieval_protected_admin_docs`

- Turn: `1`
- Prompt: De forma bem objetiva, quais pendencias documentais da Ana ainda pedem acao e qual e o proximo passo recomendado?
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `100`, keyword pass `True`, latency `1940.0 ms`
- Reason: `status administrativo autenticado exige service deterministico`

### `llamaindex` `llamaindex_turn_frame:protected.administrative.status` `retrieval_protected_admin_docs`

- Turn: `1`
- Prompt: De forma bem objetiva, quais pendencias documentais da Ana ainda pedem acao e qual e o proximo passo recomendado?
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `100`, keyword pass `True`, latency `1584.8 ms`
- Reason: `llamaindex_turn_frame:protected.administrative.status`

### `python_functions` `python_functions_turn_frame:protected.administrative.status` `retrieval_protected_admin_docs`

- Turn: `1`
- Prompt: De forma bem objetiva, quais pendencias documentais da Ana ainda pedem acao e qual e o proximo passo recomendado?
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `100`, keyword pass `True`, latency `6536.5 ms`
- Reason: `python_functions_native_structured:institution`

### `langgraph` `status administrativo autenticado exige service deterministico` `retrieval_protected_admin_finance_combo`

- Turn: `1`
- Prompt: Tem algo na minha documentacao ou no cadastro que esteja travando o financeiro? Me de a visao combinada. Traga a resposta de forma concreta.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `100`, keyword pass `True`, latency `1362.3 ms`
- Reason: `status administrativo autenticado exige service deterministico`

### `llamaindex` `llamaindex_turn_frame:protected.institution.admin_finance_status` `retrieval_protected_admin_finance_combo`

- Turn: `1`
- Prompt: Tem algo na minha documentacao ou no cadastro que esteja travando o financeiro? Me de a visao combinada. Traga a resposta de forma concreta.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `100`, keyword pass `True`, latency `1089.2 ms`
- Reason: `llamaindex_turn_frame:protected.institution.admin_finance_status`

### `python_functions` `python_functions_turn_frame:protected.institution.admin_finance_status` `retrieval_protected_admin_finance_combo`

- Turn: `1`
- Prompt: Tem algo na minha documentacao ou no cadastro que esteja travando o financeiro? Me de a visao combinada. Traga a resposta de forma concreta.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `100`, keyword pass `True`, latency `1067.6 ms`
- Reason: `python_functions_native_structured:institution`

### `langgraph` `dados estruturados devem passar por service deterministico` `retrieval_protected_attendance_panorama`

- Turn: `1`
- Prompt: Agora foque so no Lucas e diga o que mais preocupa na frequencia dele. Responda de forma direta.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `100`, keyword pass `True`, latency `9417.7 ms`
- Reason: `dados estruturados devem passar por service deterministico`

