# Retrieval Trace Calibration Report

Generated at: 2026-04-15T12:59:18.443285+00:00

Run prefix: `debug:four-path:normal:20260415T125004Z`

Eval JSON: `docs/architecture/retrieval-broad-30q-cycle1-fixval6-cross-path-report.json`

## Stack Summary

| Stack | Count | Retrieval traces | Answerable | Quality | Avg top_k | Avg hits | Avg selected | Coverage | Latency |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `langgraph` | `30` | `5` | `0.0%` | `98.5` | `3.0` | `0.0` | `0.8` | `1.0` | `5846.2 ms` |
| `python_functions` | `27` | `5` | `0.0%` | `98.8` | `6.6` | `0.0` | `0.8` | `1.0` | `5335.6 ms` |
| `llamaindex` | `28` | `0` | `0.0%` | `99.6` | `0.0` | `0.0` | `0.0` | `0.0` | `5181.3 ms` |
| `specialist_supervisor` | `0` | `0` | `0.0%` | `0.0` | `0.0` | `0.0` | `0.0` | `0.0` | `0.0 ms` |

## Capability Highlights

| Capability | Count | Retrieval traces | Answerable | Quality | Avg top_k | Avg hits | Coverage | Stacks |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `llamaindex_turn_frame:protected.academic.attendance` | `1` | `0` | `0.0%` | `0.0` | `0.0` | `0.0` | `0.0` | `llamaindex` |
| `python_functions_turn_frame:protected.academic.attendance` | `1` | `0` | `0.0%` | `0.0` | `0.0` | `0.0` | `0.0` | `python_functions` |
| `langgraph_turn_frame:protected.administrative.status` | `1` | `0` | `0.0%` | `80.0` | `0.0` | `0.0` | `0.0` | `langgraph` |
| `pricing` | `1` | `0` | `0.0%` | `80.0` | `0.0` | `0.0` | `0.0` | `langgraph` |
| `python_functions_turn_frame:scope_boundary` | `2` | `0` | `0.0%` | `90.0` | `0.0` | `0.0` | `0.0` | `python_functions` |
| `public_bundle.facilities_study_support` | `3` | `0` | `0.0%` | `93.3` | `0.0` | `0.0` | `0.0` | `langgraph, llamaindex, python_functions` |
| `protected.documents.restricted_lookup` | `10` | `10` | `0.0%` | `100.0` | `4.8` | `0.0` | `1.0` | `langgraph, python_functions` |
| `llamaindex_local_protected:academic` | `7` | `0` | `0.0%` | `100.0` | `0.0` | `0.0` | `0.0` | `llamaindex` |
| `dados estruturados devem passar por service deterministico` | `6` | `0` | `0.0%` | `100.0` | `0.0` | `0.0` | `0.0` | `langgraph` |
| `llamaindex_local_restricted_documents;turn_frame=protected.documents.restricted_lookup` | `4` | `0` | `0.0%` | `100.0` | `0.0` | `0.0` | `0.0` | `llamaindex` |
| `python_functions_local_protected:academic` | `4` | `0` | `0.0%` | `100.0` | `0.0` | `0.0` | `0.0` | `python_functions` |
| `public_bundle.academic_policy_overview` | `3` | `0` | `0.0%` | `100.0` | `0.0` | `0.0` | `0.0` | `langgraph, llamaindex, python_functions` |
| `public_bundle.family_new_calendar_assessment_enrollment` | `3` | `0` | `0.0%` | `100.0` | `0.0` | `0.0` | `0.0` | `langgraph, llamaindex, python_functions` |
| `public_bundle.governance_protocol` | `3` | `0` | `0.0%` | `100.0` | `0.0` | `0.0` | `0.0` | `langgraph, llamaindex, python_functions` |
| `public_bundle.secretaria_portal_credentials` | `3` | `0` | `0.0%` | `100.0` | `0.0` | `0.0` | `0.0` | `langgraph, llamaindex, python_functions` |

## Recommendations

- `protected.documents.restricted_lookup` está com `answerable_rate=0.0%` sem saturar `top_k`; vale revisar query variants, metadata e chunking.

## Trace Samples

### `langgraph` `langgraph_turn_frame:protected.administrative.status` `retrieval_protected_admin_docs`

- Turn: `1`
- Prompt: Pensando no caso pratico, no cadastro da Ana, quais pendencias administrativas continuam abertas e que acao vem agora?
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `80`, keyword pass `False`, latency `768.5 ms`
- Reason: `langgraph_turn_frame:scope_boundary`
- Errors: `missing_expected_keyword`

### `python_functions` `python_functions_turn_frame:scope_boundary` `retrieval_protected_admin_docs`

- Turn: `1`
- Prompt: Pensando no caso pratico, no cadastro da Ana, quais pendencias administrativas continuam abertas e que acao vem agora?
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `80`, keyword pass `False`, latency `575.0 ms`
- Reason: `python_functions_turn_frame:scope_boundary`
- Errors: `missing_expected_keyword`

### `langgraph` `pricing` `retrieval_public_pricing_projection`

- Turn: `1`
- Prompt: Pela referencia publica de precos, qual seria a matricula total e o valor mensal para 3 filhos. Traga a resposta de forma concreta.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `80`, keyword pass `False`, latency `13882.9 ms`
- Reason: `langgraph_turn_frame:public_answer`
- Errors: `missing_expected_keyword`

### `llamaindex` `public_bundle.facilities_study_support` `retrieval_public_facilities_study`

- Turn: `1`
- Prompt: De que forma os documentos publicos ligam biblioteca, laboratorios e estudo orientado como suporte ao ensino medio. Responda de forma direta.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `90`, keyword pass `True`, latency `2573.8 ms`
- Reason: `llamaindex_public_canonical_lane:public_bundle.facilities_study_support`
- Errors: `weak_actionability`

### `python_functions` `public_bundle.facilities_study_support` `retrieval_public_facilities_study`

- Turn: `1`
- Prompt: De que forma os documentos publicos ligam biblioteca, laboratorios e estudo orientado como suporte ao ensino medio. Responda de forma direta.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `90`, keyword pass `True`, latency `5404.6 ms`
- Reason: `python_functions_native_canonical_lane:public_bundle.facilities_study_support`
- Errors: `weak_actionability`

### `langgraph` `a intencao esta ambigua e exige clarificacao antes de recuperar contexto` `retrieval_protected_access_scope`

- Turn: `1`
- Prompt: Qual e exatamente o meu escopo aqui? Quero saber se estou autenticado e quais dados academicos e financeiros consigo ver.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `100`, keyword pass `True`, latency `19300.9 ms`
- Reason: `a intencao esta ambigua e exige clarificacao antes de recuperar contexto`

### `llamaindex` `llamaindex_local_protected:finance` `retrieval_protected_access_scope`

- Turn: `1`
- Prompt: Qual e exatamente o meu escopo aqui? Quero saber se estou autenticado e quais dados academicos e financeiros consigo ver.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `100`, keyword pass `True`, latency `557.0 ms`
- Reason: `llamaindex_local_protected:finance`

### `python_functions` `python_functions_native_authenticated_account_scope` `retrieval_protected_access_scope`

- Turn: `1`
- Prompt: Qual e exatamente o meu escopo aqui? Quero saber se estou autenticado e quais dados academicos e financeiros consigo ver.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `100`, keyword pass `True`, latency `501.6 ms`
- Reason: `python_functions_native_authenticated_account_scope`

### `llamaindex` `contextual_public_direct_answer` `retrieval_protected_admin_docs`

- Turn: `1`
- Prompt: Pensando no caso pratico, no cadastro da Ana, quais pendencias administrativas continuam abertas e que acao vem agora?
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `100`, keyword pass `True`, latency `566.7 ms`
- Reason: `contextual_public_direct_answer`

### `langgraph` `status administrativo autenticado exige service deterministico` `retrieval_protected_admin_finance_combo`

- Turn: `1`
- Prompt: Tem algo na minha documentacao ou no cadastro que esteja travando o financeiro? Me de a visao combinada.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `100`, keyword pass `True`, latency `8078.6 ms`
- Reason: `status administrativo autenticado exige service deterministico`

### `llamaindex` `llamaindex_local_protected:institution` `retrieval_protected_admin_finance_combo`

- Turn: `1`
- Prompt: Tem algo na minha documentacao ou no cadastro que esteja travando o financeiro? Me de a visao combinada.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `100`, keyword pass `True`, latency `7195.5 ms`
- Reason: `llamaindex_protected_records_fast_path`

### `python_functions` `python_functions_local_protected:institution` `retrieval_protected_admin_finance_combo`

- Turn: `1`
- Prompt: Tem algo na minha documentacao ou no cadastro que esteja travando o financeiro? Me de a visao combinada.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `100`, keyword pass `True`, latency `8999.5 ms`
- Reason: `python_functions_native_structured:institution`

