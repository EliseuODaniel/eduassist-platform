# Retrieval Trace Calibration Report

Generated at: 2026-04-16T16:22:09.657327+00:00

Run prefix: `debug:four-path:normal:20260416T161420Z`

Eval JSON: `docs/architecture/retrieval-broad-30q-cycle10-baseline-cross-path-report.json`

## Stack Summary

| Stack | Count | Retrieval traces | Answerable | Quality | Avg top_k | Avg hits | Avg selected | Coverage | Latency |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `langgraph` | `27` | `5` | `0.0%` | `98.2` | `3.0` | `0.0` | `1.0` | `1.0` | `4518.4 ms` |
| `python_functions` | `30` | `5` | `0.0%` | `97.9` | `6.6` | `0.0` | `1.0` | `1.0` | `5646.0 ms` |
| `llamaindex` | `30` | `0` | `0.0%` | `98.4` | `0.0` | `0.0` | `0.0` | `0.0` | `5392.8 ms` |
| `specialist_supervisor` | `0` | `0` | `0.0%` | `0.0` | `0.0` | `0.0` | `0.0` | `0.0` | `0.0 ms` |

## Capability Highlights

| Capability | Count | Retrieval traces | Answerable | Quality | Avg top_k | Avg hits | Coverage | Stacks |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `llamaindex_local_clarify` | `1` | `0` | `0.0%` | `0.0` | `0.0` | `0.0` | `0.0` | `llamaindex` |
| `llamaindex_turn_frame:protected.academic.attendance` | `1` | `0` | `0.0%` | `0.0` | `0.0` | `0.0` | `0.0` | `llamaindex` |
| `canonical_fact` | `3` | `0` | `0.0%` | `63.3` | `0.0` | `0.0` | `0.0` | `langgraph, llamaindex, python_functions` |
| `llamaindex_local_protected:academic` | `2` | `0` | `0.0%` | `95.0` | `0.0` | `0.0` | `0.0` | `llamaindex` |
| `python_functions_native_protected_focus:academic` | `5` | `0` | `0.0%` | `96.7` | `0.0` | `0.0` | `0.0` | `python_functions` |
| `dados estruturados devem passar por service deterministico` | `7` | `0` | `0.0%` | `98.0` | `0.0` | `0.0` | `0.0` | `langgraph` |
| `protected.documents.restricted_lookup` | `10` | `10` | `0.0%` | `100.0` | `4.8` | `0.0` | `1.0` | `langgraph, python_functions` |
| `auth_guidance` | `5` | `0` | `0.0%` | `100.0` | `0.0` | `0.0` | `0.0` | `langgraph, llamaindex, python_functions` |
| `llamaindex_local_public_unknown_safe_clarify` | `3` | `0` | `0.0%` | `100.0` | `0.0` | `0.0` | `0.0` | `llamaindex` |
| `llamaindex_local_restricted_documents;turn_frame=protected.documents.restricted_lookup` | `3` | `0` | `0.0%` | `100.0` | `0.0` | `0.0` | `0.0` | `llamaindex` |
| `public_bundle.academic_policy_overview` | `3` | `0` | `0.0%` | `100.0` | `0.0` | `0.0` | `0.0` | `langgraph, llamaindex, python_functions` |
| `public_bundle.facilities_study_support` | `3` | `0` | `0.0%` | `100.0` | `0.0` | `0.0` | `0.0` | `langgraph, llamaindex, python_functions` |
| `public_bundle.governance_protocol` | `3` | `0` | `0.0%` | `100.0` | `0.0` | `0.0` | `0.0` | `langgraph, llamaindex, python_functions` |
| `public_bundle.secretaria_portal_credentials` | `3` | `0` | `0.0%` | `100.0` | `0.0` | `0.0` | `0.0` | `langgraph, llamaindex, python_functions` |
| `llamaindex_local_clarify;turn_frame=protected.documents.restricted_lookup` | `2` | `0` | `0.0%` | `100.0` | `0.0` | `0.0` | `0.0` | `llamaindex` |

## Recommendations

- `protected.documents.restricted_lookup` está com `answerable_rate=0.0%` sem saturar `top_k`; vale revisar query variants, metadata e chunking.

## Trace Samples

### `python_functions` `canonical_fact` `retrieval_protected_access_scope`

- Turn: `1`
- Prompt: Sem sair do escopo do projeto, o que eu consigo consultar aqui no Telegram? Quero meu escopo exato entre academico e financeiro.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `54`, keyword pass `False`, latency `2838.7 ms`
- Reason: `python_functions_native_structured:institution`
- Errors: `missing_expected_keyword, multi_intent_partial_collapse`

### `langgraph` `canonical_fact` `retrieval_protected_access_scope`

- Turn: `1`
- Prompt: Sem sair do escopo do projeto, o que eu consigo consultar aqui no Telegram? Quero meu escopo exato entre academico e financeiro.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `68`, keyword pass `False`, latency `10997.5 ms`
- Reason: `authenticated_public_profile_rescue`
- Errors: `missing_expected_keyword, unnecessary_clarification`

### `llamaindex` `canonical_fact` `retrieval_protected_access_scope`

- Turn: `1`
- Prompt: Sem sair do escopo do projeto, o que eu consigo consultar aqui no Telegram? Quero meu escopo exato entre academico e financeiro.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `68`, keyword pass `False`, latency `17173.7 ms`
- Reason: `llamaindex_public_profile`
- Errors: `missing_expected_keyword, unnecessary_clarification`

### `langgraph` `dados estruturados devem passar por service deterministico` `retrieval_student_academic_self`

- Turn: `1`
- Prompt: Como aluno autenticado, me diga qual materia esta melhor, qual esta pior e o que falta para fechar a media em fisica. Seja objetivo e grounded.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `90`, keyword pass `True`, latency `2052.3 ms`
- Reason: `dados estruturados devem passar por service deterministico`
- Errors: `weak_actionability`

### `llamaindex` `llamaindex_local_protected:academic` `retrieval_student_academic_self`

- Turn: `1`
- Prompt: Como aluno autenticado, me diga qual materia esta melhor, qual esta pior e o que falta para fechar a media em fisica. Seja objetivo e grounded.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `90`, keyword pass `True`, latency `1084.0 ms`
- Reason: `llamaindex_local_protected:academic`
- Errors: `weak_actionability`

### `python_functions` `python_functions_native_protected_focus:academic` `retrieval_student_academic_self`

- Turn: `1`
- Prompt: Como aluno autenticado, me diga qual materia esta melhor, qual esta pior e o que falta para fechar a media em fisica. Seja objetivo e grounded.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `90`, keyword pass `True`, latency `1082.7 ms`
- Reason: `python_functions_native_structured:academic`
- Errors: `weak_actionability`

### `langgraph` `o turno atual trouxe pistas explicitas de outro dominio protegido e o roteamento foi corrigido` `retrieval_protected_admin_docs`

- Turn: `1`
- Prompt: Hoje, o que ainda falta na parte administrativa da Ana e como a familia deve agir em seguida. Traga a resposta de forma concreta.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `100`, keyword pass `True`, latency `1929.3 ms`
- Reason: `o turno atual trouxe pistas explicitas de outro dominio protegido e o roteamento foi corrigido`

### `llamaindex` `o turno atual trouxe pistas explicitas de outro dominio protegido e o roteamento foi corrigido` `retrieval_protected_admin_docs`

- Turn: `1`
- Prompt: Hoje, o que ainda falta na parte administrativa da Ana e como a familia deve agir em seguida. Traga a resposta de forma concreta.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `100`, keyword pass `True`, latency `994.1 ms`
- Reason: `o turno atual trouxe pistas explicitas de outro dominio protegido e o roteamento foi corrigido`

### `python_functions` `python_functions_native_family_attendance_aggregate` `retrieval_protected_admin_docs`

- Turn: `1`
- Prompt: Hoje, o que ainda falta na parte administrativa da Ana e como a familia deve agir em seguida. Traga a resposta de forma concreta.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `100`, keyword pass `True`, latency `1255.2 ms`
- Reason: `python_functions_native_family_attendance_aggregate`

### `langgraph` `status administrativo autenticado exige service deterministico` `retrieval_protected_admin_finance_combo`

- Turn: `1`
- Prompt: Tem algo na minha documentacao ou no cadastro que esteja travando o financeiro? Me de a visao combinada. Seja objetivo e grounded.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `100`, keyword pass `True`, latency `1874.8 ms`
- Reason: `status administrativo autenticado exige service deterministico`

### `llamaindex` `llamaindex_turn_frame:protected.institution.admin_finance_status` `retrieval_protected_admin_finance_combo`

- Turn: `1`
- Prompt: Tem algo na minha documentacao ou no cadastro que esteja travando o financeiro? Me de a visao combinada. Seja objetivo e grounded.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `100`, keyword pass `True`, latency `1708.8 ms`
- Reason: `llamaindex_turn_frame:protected.institution.admin_finance_status`

### `python_functions` `python_functions_turn_frame:protected.institution.admin_finance_status` `retrieval_protected_admin_finance_combo`

- Turn: `1`
- Prompt: Tem algo na minha documentacao ou no cadastro que esteja travando o financeiro? Me de a visao combinada. Seja objetivo e grounded.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `100`, keyword pass `True`, latency `1851.0 ms`
- Reason: `python_functions_native_structured:institution`

