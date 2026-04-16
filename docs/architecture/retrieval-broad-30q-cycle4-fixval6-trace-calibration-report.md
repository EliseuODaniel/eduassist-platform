# Retrieval Trace Calibration Report

Generated at: 2026-04-16T01:43:15.006134+00:00

Run prefix: `debug:four-path:normal:20260416T013502Z`

Eval JSON: `docs/architecture/retrieval-broad-30q-cycle4-fixval6-cross-path-report.json`

## Stack Summary

| Stack | Count | Retrieval traces | Answerable | Quality | Avg top_k | Avg hits | Avg selected | Coverage | Latency |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `langgraph` | `30` | `4` | `0.0%` | `96.9` | `3.0` | `0.0` | `1.25` | `1.0` | `10329.8 ms` |
| `python_functions` | `30` | `5` | `0.0%` | `94.8` | `6.8` | `0.0` | `1.2` | `1.0` | `11884.6 ms` |
| `llamaindex` | `30` | `0` | `0.0%` | `96.1` | `0.0` | `0.0` | `0.0` | `0.0` | `11954.1 ms` |
| `specialist_supervisor` | `0` | `0` | `0.0%` | `0.0` | `0.0` | `0.0` | `0.0` | `0.0` | `0.0 ms` |

## Capability Highlights

| Capability | Count | Retrieval traces | Answerable | Quality | Avg top_k | Avg hits | Coverage | Stacks |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `public_bundle.conduct_frequency_punctuality` | `3` | `0` | `0.0%` | `0.0` | `0.0` | `0.0` | `0.0` | `langgraph, llamaindex, python_functions` |
| `deterministic_teacher_directory_boundary` | `1` | `0` | `0.0%` | `0.0` | `0.0` | `0.0` | `0.0` | `python_functions` |
| `llamaindex_local_clarify` | `1` | `0` | `0.0%` | `0.0` | `0.0` | `0.0` | `0.0` | `llamaindex` |
| `llamaindex_turn_frame:protected.academic.family_comparison` | `1` | `0` | `0.0%` | `0.0` | `0.0` | `0.0` | `0.0` | `llamaindex` |
| `python_functions_turn_frame:protected.academic.family_comparison` | `1` | `0` | `0.0%` | `0.0` | `0.0` | `0.0` | `0.0` | `python_functions` |
| `retrieval hibrido e o caminho padrao para faq e documentos` | `1` | `0` | `0.0%` | `55.0` | `0.0` | `0.0` | `0.0` | `langgraph` |
| `llamaindex_local_protected:academic` | `2` | `0` | `0.0%` | `80.0` | `0.0` | `0.0` | `0.0` | `llamaindex` |
| `python_functions_local_protected:academic` | `1` | `0` | `0.0%` | `80.0` | `0.0` | `0.0` | `0.0` | `python_functions` |
| `python_functions_native_family_attendance_aggregate` | `1` | `0` | `0.0%` | `80.0` | `0.0` | `0.0` | `0.0` | `python_functions` |
| `llamaindex_local_public_unknown_safe_clarify` | `3` | `0` | `0.0%` | `85.0` | `0.0` | `0.0` | `0.0` | `llamaindex` |
| `dados estruturados devem passar por service deterministico` | `6` | `0` | `0.0%` | `92.0` | `0.0` | `0.0` | `0.0` | `langgraph` |
| `auth_guidance` | `3` | `0` | `0.0%` | `93.3` | `0.0` | `0.0` | `0.0` | `langgraph, llamaindex, python_functions` |
| `protected.documents.restricted_lookup` | `9` | `9` | `0.0%` | `100.0` | `5.11` | `0.0` | `1.0` | `langgraph, python_functions` |
| `llamaindex_local_restricted_documents;turn_frame=protected.documents.restricted_lookup` | `5` | `0` | `0.0%` | `100.0` | `0.0` | `0.0` | `0.0` | `llamaindex` |
| `llamaindex_local_public_fact:institution` | `3` | `0` | `0.0%` | `100.0` | `0.0` | `0.0` | `0.0` | `llamaindex` |

## Recommendations

- `protected.documents.restricted_lookup` está com `answerable_rate=0.0%` sem saturar `top_k`; vale revisar query variants, metadata e chunking.

## Trace Samples

### `python_functions` `deterministic_teacher_directory_boundary` `retrieval_public_teacher_directory`

- Turn: `1`
- Prompt: Pensando no caso pratico, existe canal publico com nome ou contato do professor de matematica, ou isso vai pela coordenacao pedagogica?
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `0`, keyword pass `False`, latency `90067.7 ms`
- Reason: `exception`
- Errors: `request_failed`

### `langgraph` `retrieval hibrido e o caminho padrao para faq e documentos` `retrieval_public_open_world_out_of_scope`

- Turn: `1`
- Prompt: Quero uma recomendacao de filme, sem relacao com escola.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `55`, keyword pass `False`, latency `29281.2 ms`
- Reason: `retrieval hibrido e o caminho padrao para faq e documentos`
- Errors: `forbidden_entity_or_value`

### `llamaindex` `llamaindex_local_public_unknown_safe_clarify` `retrieval_public_open_world_out_of_scope`

- Turn: `1`
- Prompt: Quero uma recomendacao de filme, sem relacao com escola.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `55`, keyword pass `False`, latency `30210.1 ms`
- Reason: `llamaindex_deterministic_public_guardrail_fast_path`
- Errors: `forbidden_entity_or_value`

### `langgraph` `dados estruturados devem passar por service deterministico` `retrieval_protected_attendance_panorama`

- Turn: `1`
- Prompt: Mantendo o contexto, corta para o Lucas e resume qual e o risco mais concreto dele em frequencia.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `80`, keyword pass `False`, latency `1334.2 ms`
- Reason: `langgraph_public_canonical_lane:public_bundle.conduct_frequency_punctuality`
- Errors: `missing_expected_keyword`

### `llamaindex` `llamaindex_local_protected:academic` `retrieval_protected_attendance_panorama`

- Turn: `1`
- Prompt: Mantendo o contexto, corta para o Lucas e resume qual e o risco mais concreto dele em frequencia.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `80`, keyword pass `False`, latency `2498.1 ms`
- Reason: `llamaindex_public_canonical_lane:public_bundle.conduct_frequency_punctuality`
- Errors: `missing_expected_keyword`

### `python_functions` `python_functions_native_family_attendance_aggregate` `retrieval_protected_attendance_panorama`

- Turn: `1`
- Prompt: Mantendo o contexto, corta para o Lucas e resume qual e o risco mais concreto dele em frequencia.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `80`, keyword pass `False`, latency `1313.0 ms`
- Reason: `python_functions_native_structured:institution`
- Errors: `missing_expected_keyword`

### `llamaindex` `auth_guidance` `retrieval_protected_boundary_auth_needed`

- Turn: `1`
- Prompt: Sem autenticar, eu consigo puxar minhas notas por este chat?
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `80`, keyword pass `False`, latency `6474.8 ms`
- Reason: `llamaindex_semantic_ingress:auth_guidance`
- Errors: `missing_expected_keyword`

### `langgraph` `dados estruturados devem passar por service deterministico` `retrieval_student_academic_self`

- Turn: `1`
- Prompt: Como aluno autenticado, me diga qual materia esta melhor, qual esta pior e o que falta para fechar a media em fisica.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `80`, keyword pass `False`, latency `26896.0 ms`
- Reason: `dados estruturados devem passar por service deterministico`
- Errors: `missing_expected_keyword`

### `llamaindex` `llamaindex_local_protected:academic` `retrieval_student_academic_self`

- Turn: `1`
- Prompt: Como aluno autenticado, me diga qual materia esta melhor, qual esta pior e o que falta para fechar a media em fisica.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `80`, keyword pass `False`, latency `39144.9 ms`
- Reason: `llamaindex_local_protected:academic`
- Errors: `missing_expected_keyword`

### `python_functions` `python_functions_local_protected:academic` `retrieval_student_academic_self`

- Turn: `1`
- Prompt: Como aluno autenticado, me diga qual materia esta melhor, qual esta pior e o que falta para fechar a media em fisica.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `80`, keyword pass `False`, latency `20899.2 ms`
- Reason: `python_functions_native_structured:institution`
- Errors: `missing_expected_keyword`

### `langgraph` `capacidade da conta autenticada e alunos vinculados exigem leitura protegida e minimizada` `retrieval_protected_access_scope`

- Turn: `1`
- Prompt: Estou autenticado como quem e com qual escopo? Quero saber o que consigo ver de academico e financeiro.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `100`, keyword pass `True`, latency `1491.8 ms`
- Reason: `capacidade da conta autenticada e alunos vinculados exigem leitura protegida e minimizada`

### `llamaindex` `llamaindex_local_clarify;turn_frame=protected.account.access_scope` `retrieval_protected_access_scope`

- Turn: `1`
- Prompt: Estou autenticado como quem e com qual escopo? Quero saber o que consigo ver de academico e financeiro.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `100`, keyword pass `True`, latency `1184.9 ms`
- Reason: `llamaindex_protected_records_fast_path`

