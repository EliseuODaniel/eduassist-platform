# Retrieval Trace Calibration Report

Generated at: 2026-04-15T13:59:08.378827+00:00

Run prefix: `debug:four-path:normal:20260415T134623Z`

Eval JSON: `docs/architecture/retrieval-broad-30q-cycle1-fixval8-cross-path-report.json`

## Stack Summary

| Stack | Count | Retrieval traces | Answerable | Quality | Avg top_k | Avg hits | Avg selected | Coverage | Latency |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `langgraph` | `30` | `5` | `0.0%` | `100.0` | `3.0` | `0.0` | `0.8` | `1.0` | `6818.8 ms` |
| `python_functions` | `30` | `5` | `0.0%` | `100.0` | `6.6` | `0.0` | `0.8` | `1.0` | `6790.2 ms` |
| `llamaindex` | `30` | `0` | `0.0%` | `99.6` | `0.0` | `0.0` | `0.0` | `0.0` | `7063.7 ms` |
| `specialist_supervisor` | `0` | `0` | `0.0%` | `0.0` | `0.0` | `0.0` | `0.0` | `0.0` | `0.0 ms` |

## Capability Highlights

| Capability | Count | Retrieval traces | Answerable | Quality | Avg top_k | Avg hits | Coverage | Stacks |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `llamaindex_turn_frame:protected.academic.attendance` | `1` | `0` | `0.0%` | `0.0` | `0.0` | `0.0` | `0.0` | `llamaindex` |
| `python_functions_turn_frame:protected.academic.attendance` | `1` | `0` | `0.0%` | `0.0` | `0.0` | `0.0` | `0.0` | `python_functions` |
| `public_bundle.academic_policy_overview` | `3` | `0` | `0.0%` | `96.7` | `0.0` | `0.0` | `0.0` | `langgraph, llamaindex, python_functions` |
| `protected.documents.restricted_lookup` | `10` | `10` | `0.0%` | `100.0` | `4.8` | `0.0` | `1.0` | `langgraph, python_functions` |
| `llamaindex_local_protected:academic` | `7` | `0` | `0.0%` | `100.0` | `0.0` | `0.0` | `0.0` | `llamaindex` |
| `dados estruturados devem passar por service deterministico` | `6` | `0` | `0.0%` | `100.0` | `0.0` | `0.0` | `0.0` | `langgraph` |
| `llamaindex_local_restricted_documents;turn_frame=protected.documents.restricted_lookup` | `4` | `0` | `0.0%` | `100.0` | `0.0` | `0.0` | `0.0` | `llamaindex` |
| `python_functions_local_protected:academic` | `4` | `0` | `0.0%` | `100.0` | `0.0` | `0.0` | `0.0` | `python_functions` |
| `auth_guidance` | `3` | `0` | `0.0%` | `100.0` | `0.0` | `0.0` | `0.0` | `langgraph, llamaindex, python_functions` |
| `leadership` | `3` | `0` | `0.0%` | `100.0` | `0.0` | `0.0` | `0.0` | `langgraph, llamaindex` |
| `public_bundle.facilities_study_support` | `3` | `0` | `0.0%` | `100.0` | `0.0` | `0.0` | `0.0` | `langgraph, llamaindex, python_functions` |
| `public_bundle.family_new_calendar_assessment_enrollment` | `3` | `0` | `0.0%` | `100.0` | `0.0` | `0.0` | `0.0` | `langgraph, llamaindex, python_functions` |
| `public_bundle.governance_protocol` | `3` | `0` | `0.0%` | `100.0` | `0.0` | `0.0` | `0.0` | `langgraph, llamaindex, python_functions` |
| `public_bundle.secretaria_portal_credentials` | `3` | `0` | `0.0%` | `100.0` | `0.0` | `0.0` | `0.0` | `langgraph, llamaindex, python_functions` |
| `langgraph_turn_frame:scope_boundary` | `2` | `0` | `0.0%` | `100.0` | `0.0` | `0.0` | `0.0` | `langgraph` |

## Recommendations

- `protected.documents.restricted_lookup` está com `answerable_rate=0.0%` sem saturar `top_k`; vale revisar query variants, metadata e chunking.

## Trace Samples

### `llamaindex` `public_bundle.academic_policy_overview` `retrieval_public_discipline_recovery`

- Turn: `1`
- Prompt: Cruze regulamentos gerais, politica de avaliacao e orientacao ao estudante para explicar como disciplina, frequencia e recuperacao se influenciam. Traga a resposta de forma concreta.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `90`, keyword pass `True`, latency `3469.6 ms`
- Reason: `llamaindex_public_canonical_lane:public_bundle.academic_policy_overview`
- Errors: `weak_actionability`

### `langgraph` `a intencao esta ambigua e exige clarificacao antes de recuperar contexto` `retrieval_protected_access_scope`

- Turn: `1`
- Prompt: Qual e exatamente o meu escopo aqui? Quero saber se estou autenticado e quais dados academicos e financeiros consigo ver.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `100`, keyword pass `True`, latency `21107.6 ms`
- Reason: `a intencao esta ambigua e exige clarificacao antes de recuperar contexto`

### `llamaindex` `llamaindex_local_protected:finance` `retrieval_protected_access_scope`

- Turn: `1`
- Prompt: Qual e exatamente o meu escopo aqui? Quero saber se estou autenticado e quais dados academicos e financeiros consigo ver.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `100`, keyword pass `True`, latency `479.3 ms`
- Reason: `llamaindex_local_protected:finance`

### `python_functions` `python_functions_native_authenticated_account_scope` `retrieval_protected_access_scope`

- Turn: `1`
- Prompt: Qual e exatamente o meu escopo aqui? Quero saber se estou autenticado e quais dados academicos e financeiros consigo ver.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `100`, keyword pass `True`, latency `433.8 ms`
- Reason: `python_functions_native_authenticated_account_scope`

### `langgraph` `status administrativo autenticado exige service deterministico` `retrieval_protected_admin_docs`

- Turn: `1`
- Prompt: Pensando no caso pratico, no cadastro da Ana, quais pendencias administrativas continuam abertas e que acao vem agora?
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `100`, keyword pass `True`, latency `1152.4 ms`
- Reason: `status administrativo autenticado exige service deterministico`

### `llamaindex` `contextual_public_direct_answer` `retrieval_protected_admin_docs`

- Turn: `1`
- Prompt: Pensando no caso pratico, no cadastro da Ana, quais pendencias administrativas continuam abertas e que acao vem agora?
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `100`, keyword pass `True`, latency `821.2 ms`
- Reason: `contextual_public_direct_answer`

### `python_functions` `python_functions_native_public_compound` `retrieval_protected_admin_docs`

- Turn: `1`
- Prompt: Pensando no caso pratico, no cadastro da Ana, quais pendencias administrativas continuam abertas e que acao vem agora?
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `100`, keyword pass `True`, latency `5796.5 ms`
- Reason: `python_functions_native_public_compound`

### `langgraph` `status administrativo autenticado exige service deterministico` `retrieval_protected_admin_finance_combo`

- Turn: `1`
- Prompt: Tem algo na minha documentacao ou no cadastro que esteja travando o financeiro? Me de a visao combinada.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `100`, keyword pass `True`, latency `8928.0 ms`
- Reason: `status administrativo autenticado exige service deterministico`

### `llamaindex` `llamaindex_local_protected:institution` `retrieval_protected_admin_finance_combo`

- Turn: `1`
- Prompt: Tem algo na minha documentacao ou no cadastro que esteja travando o financeiro? Me de a visao combinada.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `100`, keyword pass `True`, latency `9082.1 ms`
- Reason: `llamaindex_protected_records_fast_path`

### `python_functions` `python_functions_local_protected:institution` `retrieval_protected_admin_finance_combo`

- Turn: `1`
- Prompt: Tem algo na minha documentacao ou no cadastro que esteja travando o financeiro? Me de a visao combinada.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `100`, keyword pass `True`, latency `8655.2 ms`
- Reason: `python_functions_native_structured:institution`

### `langgraph` `dados estruturados devem passar por service deterministico` `retrieval_protected_attendance_panorama`

- Turn: `1`
- Prompt: Agora foque so no Lucas e diga o que mais preocupa na frequencia dele.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `100`, keyword pass `True`, latency `15433.6 ms`
- Reason: `dados estruturados devem passar por service deterministico`

### `llamaindex` `llamaindex_local_protected:academic` `retrieval_protected_attendance_panorama`

- Turn: `1`
- Prompt: Agora foque so no Lucas e diga o que mais preocupa na frequencia dele.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `100`, keyword pass `True`, latency `16514.4 ms`
- Reason: `llamaindex_turn_frame:protected.academic.attendance`

