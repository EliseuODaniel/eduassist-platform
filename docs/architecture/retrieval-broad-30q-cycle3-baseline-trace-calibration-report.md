# Retrieval Trace Calibration Report

Generated at: 2026-04-15T19:50:37.604510+00:00

Run prefix: `debug:four-path:normal:20260415T194135Z`

Eval JSON: `docs/architecture/retrieval-broad-30q-cycle3-baseline-cross-path-report.json`

## Stack Summary

| Stack | Count | Retrieval traces | Answerable | Quality | Avg top_k | Avg hits | Avg selected | Coverage | Latency |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `langgraph` | `30` | `5` | `0.0%` | `99.3` | `3.0` | `0.0` | `0.8` | `1.0` | `5190.1 ms` |
| `python_functions` | `30` | `6` | `100.0%` | `98.5` | `6.17` | `0.67` | `1.33` | `1.0` | `5697.1 ms` |
| `llamaindex` | `29` | `0` | `0.0%` | `99.2` | `0.0` | `0.0` | `0.0` | `0.0` | `6522.2 ms` |
| `specialist_supervisor` | `0` | `0` | `0.0%` | `0.0` | `0.0` | `0.0` | `0.0` | `0.0` | `0.0 ms` |

## Capability Highlights

| Capability | Count | Retrieval traces | Answerable | Quality | Avg top_k | Avg hits | Coverage | Stacks |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `llamaindex_local_protected:finance` | `1` | `0` | `0.0%` | `80.0` | `0.0` | `0.0` | `0.0` | `llamaindex` |
| `python_functions_local_protected:finance` | `1` | `0` | `0.0%` | `80.0` | `0.0` | `0.0` | `0.0` | `python_functions` |
| `dados estruturados devem passar por service deterministico` | `6` | `0` | `0.0%` | `96.0` | `0.0` | `0.0` | `0.0` | `langgraph` |
| `protected.documents.restricted_lookup` | `10` | `10` | `0.0%` | `100.0` | `4.8` | `0.0` | `1.0` | `langgraph, python_functions` |
| `auth_guidance` | `5` | `0` | `0.0%` | `100.0` | `0.0` | `0.0` | `0.0` | `langgraph, llamaindex, python_functions` |
| `llamaindex_local_restricted_documents;turn_frame=protected.documents.restricted_lookup` | `5` | `0` | `0.0%` | `100.0` | `0.0` | `0.0` | `0.0` | `llamaindex` |
| `leadership` | `4` | `0` | `0.0%` | `100.0` | `0.0` | `0.0` | `0.0` | `langgraph, python_functions` |
| `llamaindex_local_protected:academic` | `3` | `0` | `0.0%` | `100.0` | `0.0` | `0.0` | `0.0` | `llamaindex` |
| `public_bundle.academic_policy_overview` | `3` | `0` | `0.0%` | `100.0` | `0.0` | `0.0` | `0.0` | `langgraph, llamaindex, python_functions` |
| `public_bundle.family_new_calendar_assessment_enrollment` | `3` | `0` | `0.0%` | `100.0` | `0.0` | `0.0` | `0.0` | `langgraph, llamaindex, python_functions` |
| `public_bundle.secretaria_portal_credentials` | `3` | `0` | `0.0%` | `100.0` | `0.0` | `0.0` | `0.0` | `langgraph, llamaindex, python_functions` |
| `python_functions_local_protected:academic` | `3` | `0` | `0.0%` | `100.0` | `0.0` | `0.0` | `0.0` | `python_functions` |
| `langgraph_turn_frame:scope_boundary` | `2` | `0` | `0.0%` | `100.0` | `0.0` | `0.0` | `0.0` | `langgraph` |
| `llamaindex_local_public_unknown_safe_clarify` | `2` | `0` | `0.0%` | `100.0` | `0.0` | `0.0` | `0.0` | `llamaindex` |
| `llamaindex_turn_frame:protected.academic.family_comparison` | `2` | `0` | `0.0%` | `100.0` | `0.0` | `0.0` | `0.0` | `llamaindex` |

## Recommendations

- `protected.documents.restricted_lookup` está com `answerable_rate=0.0%` sem saturar `top_k`; vale revisar query variants, metadata e chunking.

## Trace Samples

### `langgraph` `dados estruturados devem passar por service deterministico` `retrieval_protected_access_scope`

- Turn: `1`
- Prompt: Quais dados dos meus filhos eu consigo acessar por aqui, e se o meu acesso cobre academico e financeiro?
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `80`, keyword pass `False`, latency `867.7 ms`
- Reason: `dados estruturados devem passar por service deterministico`
- Errors: `missing_expected_keyword`

### `llamaindex` `llamaindex_local_protected:finance` `retrieval_protected_access_scope`

- Turn: `1`
- Prompt: Quais dados dos meus filhos eu consigo acessar por aqui, e se o meu acesso cobre academico e financeiro?
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `80`, keyword pass `False`, latency `693.1 ms`
- Reason: `llamaindex_local_protected:finance`
- Errors: `missing_expected_keyword`

### `python_functions` `python_functions_local_protected:finance` `retrieval_protected_access_scope`

- Turn: `1`
- Prompt: Quais dados dos meus filhos eu consigo acessar por aqui, e se o meu acesso cobre academico e financeiro?
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `80`, keyword pass `False`, latency `766.1 ms`
- Reason: `python_functions_native_structured:finance`
- Errors: `missing_expected_keyword`

### `python_functions` `python_functions_local_public_explanatory:institution` `retrieval_public_governance_protocol`

- Turn: `1`
- Prompt: Pelos documentos publicos, como uma familia deve escalar um tema da rotina para direcao e protocolo formal?
- Policy: `baseline` / `top_k=4` / `baseline_default`
- Retrieval: hits `4/4`, coverage `1.0`, answerable `True`
- Eval: quality `80`, keyword pass `False`, latency `18647.0 ms`
- Reason: `python_functions_native_public_retrieval`
- Errors: `missing_expected_keyword`

### `langgraph` `status administrativo autenticado exige service deterministico` `retrieval_protected_admin_docs`

- Turn: `1`
- Prompt: Pensando no caso pratico, quero o status documental da Ana com as pendencias e o proximo passo recomendado.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `100`, keyword pass `True`, latency `2061.7 ms`
- Reason: `status administrativo autenticado exige service deterministico`

### `llamaindex` `llamaindex_turn_frame:protected.administrative.status` `retrieval_protected_admin_docs`

- Turn: `1`
- Prompt: Pensando no caso pratico, quero o status documental da Ana com as pendencias e o proximo passo recomendado.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `100`, keyword pass `True`, latency `8762.9 ms`
- Reason: `llamaindex_turn_frame:protected.administrative.status`

### `python_functions` `python_functions_turn_frame:protected.administrative.status` `retrieval_protected_admin_docs`

- Turn: `1`
- Prompt: Pensando no caso pratico, quero o status documental da Ana com as pendencias e o proximo passo recomendado.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `100`, keyword pass `True`, latency `8740.6 ms`
- Reason: `python_functions_native_structured:institution`

### `langgraph` `status administrativo autenticado exige service deterministico` `retrieval_protected_admin_finance_combo`

- Turn: `1`
- Prompt: Junte documentacao administrativa e financeiro das contas vinculadas e diga se ha bloqueio de atendimento. Seja objetivo e grounded.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `100`, keyword pass `True`, latency `688.6 ms`
- Reason: `status administrativo autenticado exige service deterministico`

### `llamaindex` `llamaindex_turn_frame:protected.institution.admin_finance_status` `retrieval_protected_admin_finance_combo`

- Turn: `1`
- Prompt: Junte documentacao administrativa e financeiro das contas vinculadas e diga se ha bloqueio de atendimento. Seja objetivo e grounded.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `100`, keyword pass `True`, latency `580.0 ms`
- Reason: `llamaindex_turn_frame:protected.institution.admin_finance_status`

### `python_functions` `python_functions_turn_frame:protected.institution.admin_finance_status` `retrieval_protected_admin_finance_combo`

- Turn: `1`
- Prompt: Junte documentacao administrativa e financeiro das contas vinculadas e diga se ha bloqueio de atendimento. Seja objetivo e grounded.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `100`, keyword pass `True`, latency `578.8 ms`
- Reason: `python_functions_native_structured:institution`

### `langgraph` `dados estruturados devem passar por service deterministico` `retrieval_protected_attendance_panorama`

- Turn: `1`
- Prompt: Continuando a analise, isole o Lucas e mostre por que a frequencia dele preocupa mais ou menos.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `100`, keyword pass `True`, latency `794.5 ms`
- Reason: `dados estruturados devem passar por service deterministico`

### `llamaindex` `llamaindex_turn_frame:protected.academic.family_comparison` `retrieval_protected_attendance_panorama`

- Turn: `1`
- Prompt: Continuando a analise, isole o Lucas e mostre por que a frequencia dele preocupa mais ou menos.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `100`, keyword pass `True`, latency `581.8 ms`
- Reason: `llamaindex_local_protected:academic`

