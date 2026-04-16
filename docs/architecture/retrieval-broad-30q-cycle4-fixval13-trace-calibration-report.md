# Retrieval Trace Calibration Report

Generated at: 2026-04-16T05:46:16.308937+00:00

Run prefix: `debug:four-path:normal:20260416T053741Z`

Eval JSON: `docs/architecture/retrieval-broad-30q-cycle4-fixval13-cross-path-report.json`

## Stack Summary

| Stack | Count | Retrieval traces | Answerable | Quality | Avg top_k | Avg hits | Avg selected | Coverage | Latency |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `langgraph` | `26` | `5` | `0.0%` | `99.6` | `3.0` | `0.0` | `1.2` | `1.0` | `4916.9 ms` |
| `python_functions` | `30` | `5` | `0.0%` | `99.6` | `6.8` | `0.0` | `1.2` | `1.0` | `5835.9 ms` |
| `llamaindex` | `30` | `0` | `0.0%` | `99.6` | `0.0` | `0.0` | `0.0` | `0.0` | `5220.5 ms` |
| `specialist_supervisor` | `0` | `0` | `0.0%` | `0.0` | `0.0` | `0.0` | `0.0` | `0.0` | `0.0 ms` |

## Capability Highlights

| Capability | Count | Retrieval traces | Answerable | Quality | Avg top_k | Avg hits | Coverage | Stacks |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `llamaindex_local_clarify` | `1` | `0` | `0.0%` | `0.0` | `0.0` | `0.0` | `0.0` | `llamaindex` |
| `llamaindex_local_protected:academic` | `3` | `0` | `0.0%` | `95.0` | `0.0` | `0.0` | `0.0` | `llamaindex` |
| `python_functions_native_protected_focus:academic` | `5` | `0` | `0.0%` | `96.7` | `0.0` | `0.0` | `0.0` | `python_functions` |
| `dados estruturados devem passar por service deterministico` | `6` | `0` | `0.0%` | `98.0` | `0.0` | `0.0` | `0.0` | `langgraph` |
| `protected.documents.restricted_lookup` | `10` | `10` | `0.0%` | `100.0` | `4.9` | `0.0` | `1.0` | `langgraph, python_functions` |
| `llamaindex_local_restricted_documents;turn_frame=protected.documents.restricted_lookup` | `5` | `0` | `0.0%` | `100.0` | `0.0` | `0.0` | `0.0` | `llamaindex` |
| `auth_guidance` | `3` | `0` | `0.0%` | `100.0` | `0.0` | `0.0` | `0.0` | `langgraph, llamaindex, python_functions` |
| `llamaindex_local_public_fact:institution` | `3` | `0` | `0.0%` | `100.0` | `0.0` | `0.0` | `0.0` | `llamaindex` |
| `llamaindex_local_public_unknown_safe_clarify` | `3` | `0` | `0.0%` | `100.0` | `0.0` | `0.0` | `0.0` | `llamaindex` |
| `public_bundle.academic_policy_overview` | `3` | `0` | `0.0%` | `100.0` | `0.0` | `0.0` | `0.0` | `langgraph, llamaindex, python_functions` |
| `public_bundle.facilities_study_support` | `3` | `0` | `0.0%` | `100.0` | `0.0` | `0.0` | `0.0` | `langgraph, llamaindex, python_functions` |
| `public_bundle.family_new_calendar_assessment_enrollment` | `3` | `0` | `0.0%` | `100.0` | `0.0` | `0.0` | `0.0` | `langgraph, llamaindex, python_functions` |
| `public_bundle.secretaria_portal_credentials` | `3` | `0` | `0.0%` | `100.0` | `0.0` | `0.0` | `0.0` | `langgraph, llamaindex, python_functions` |
| `leadership` | `2` | `0` | `0.0%` | `100.0` | `0.0` | `0.0` | `0.0` | `langgraph` |
| `llamaindex_turn_frame:protected.academic.family_comparison` | `2` | `0` | `0.0%` | `100.0` | `0.0` | `0.0` | `0.0` | `llamaindex` |

## Recommendations

- `protected.documents.restricted_lookup` está com `answerable_rate=0.0%` sem saturar `top_k`; vale revisar query variants, metadata e chunking.

## Trace Samples

### `langgraph` `dados estruturados devem passar por service deterministico` `retrieval_student_academic_self`

- Turn: `1`
- Prompt: Como aluno autenticado, me diga qual materia esta melhor, qual esta pior e o que falta para fechar a media em fisica.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `90`, keyword pass `True`, latency `1607.5 ms`
- Reason: `dados estruturados devem passar por service deterministico`
- Errors: `weak_actionability`

### `llamaindex` `llamaindex_local_protected:academic` `retrieval_student_academic_self`

- Turn: `1`
- Prompt: Como aluno autenticado, me diga qual materia esta melhor, qual esta pior e o que falta para fechar a media em fisica.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `90`, keyword pass `True`, latency `968.2 ms`
- Reason: `llamaindex_local_protected:academic`
- Errors: `weak_actionability`

### `python_functions` `python_functions_native_protected_focus:academic` `retrieval_student_academic_self`

- Turn: `1`
- Prompt: Como aluno autenticado, me diga qual materia esta melhor, qual esta pior e o que falta para fechar a media em fisica.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `90`, keyword pass `True`, latency `997.7 ms`
- Reason: `python_functions_native_structured:academic`
- Errors: `weak_actionability`

### `langgraph` `capacidade da conta autenticada e alunos vinculados exigem leitura protegida e minimizada` `retrieval_protected_access_scope`

- Turn: `1`
- Prompt: Estou autenticado como quem e com qual escopo? Quero saber o que consigo ver de academico e financeiro.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `100`, keyword pass `True`, latency `717.6 ms`
- Reason: `capacidade da conta autenticada e alunos vinculados exigem leitura protegida e minimizada`

### `llamaindex` `llamaindex_local_clarify;turn_frame=protected.account.access_scope` `retrieval_protected_access_scope`

- Turn: `1`
- Prompt: Estou autenticado como quem e com qual escopo? Quero saber o que consigo ver de academico e financeiro.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `100`, keyword pass `True`, latency `506.2 ms`
- Reason: `llamaindex_protected_records_fast_path`

### `python_functions` `python_functions_native_authenticated_account_scope` `retrieval_protected_access_scope`

- Turn: `1`
- Prompt: Estou autenticado como quem e com qual escopo? Quero saber o que consigo ver de academico e financeiro.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `100`, keyword pass `True`, latency `464.8 ms`
- Reason: `python_functions_native_authenticated_account_scope`

### `langgraph` `status administrativo autenticado exige service deterministico` `retrieval_protected_admin_docs`

- Turn: `1`
- Prompt: Quero ver o quadro documental da Ana: o que esta pendente e o que a familia precisa fazer em seguida. Seja objetivo e grounded.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `100`, keyword pass `True`, latency `1352.9 ms`
- Reason: `status administrativo autenticado exige service deterministico`

### `llamaindex` `llamaindex_local_protected:institution` `retrieval_protected_admin_docs`

- Turn: `1`
- Prompt: Quero ver o quadro documental da Ana: o que esta pendente e o que a familia precisa fazer em seguida. Seja objetivo e grounded.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `100`, keyword pass `True`, latency `1141.0 ms`
- Reason: `llamaindex_local_protected:institution`

### `python_functions` `python_functions_local_protected:institution` `retrieval_protected_admin_docs`

- Turn: `1`
- Prompt: Quero ver o quadro documental da Ana: o que esta pendente e o que a familia precisa fazer em seguida. Seja objetivo e grounded.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `100`, keyword pass `True`, latency `1031.6 ms`
- Reason: `python_functions_native_structured:institution`

### `langgraph` `status administrativo autenticado exige service deterministico` `retrieval_protected_admin_finance_combo`

- Turn: `1`
- Prompt: Resuma junto documentacao administrativa e financeiro das contas vinculadas para eu saber se ha impedimento de atendimento. Seja objetivo e grounded.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `100`, keyword pass `True`, latency `1065.5 ms`
- Reason: `status administrativo autenticado exige service deterministico`

### `llamaindex` `llamaindex_turn_frame:protected.institution.admin_finance_status` `retrieval_protected_admin_finance_combo`

- Turn: `1`
- Prompt: Resuma junto documentacao administrativa e financeiro das contas vinculadas para eu saber se ha impedimento de atendimento. Seja objetivo e grounded.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `100`, keyword pass `True`, latency `750.9 ms`
- Reason: `llamaindex_turn_frame:protected.institution.admin_finance_status`

### `python_functions` `python_functions_turn_frame:protected.institution.admin_finance_status` `retrieval_protected_admin_finance_combo`

- Turn: `1`
- Prompt: Resuma junto documentacao administrativa e financeiro das contas vinculadas para eu saber se ha impedimento de atendimento. Seja objetivo e grounded.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `100`, keyword pass `True`, latency `809.2 ms`
- Reason: `python_functions_native_structured:institution`

