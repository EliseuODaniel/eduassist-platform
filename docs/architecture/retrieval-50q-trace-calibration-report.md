# Retrieval Trace Calibration Report

Generated at: 2026-04-13T10:20:42.972871+00:00

Run prefix: `debug:four-path:normal:20260413T100503Z`

Eval JSON: `/home/edann/projects/eduassist-platform/docs/architecture/retrieval-50q-cross-path-report.json`

## Stack Summary

| Stack | Count | Retrieval traces | Answerable | Quality | Avg top_k | Avg hits | Avg selected | Coverage | Latency |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `langgraph` | `48` | `5` | `0.0%` | `96.1` | `3.0` | `0.0` | `0.0` | `1.0` | `5319.4 ms` |
| `python_functions` | `48` | `6` | `0.0%` | `91.9` | `4.17` | `3.33` | `3.33` | `1.0` | `7586.5 ms` |
| `llamaindex` | `44` | `0` | `0.0%` | `93.1` | `0.0` | `0.0` | `0.0` | `0.0` | `6121.0 ms` |
| `specialist_supervisor` | `0` | `0` | `0.0%` | `0.0` | `0.0` | `0.0` | `0.0` | `0.0` | `0.0 ms` |

## Capability Highlights

| Capability | Count | Retrieval traces | Answerable | Quality | Avg top_k | Avg hits | Coverage | Stacks |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `llamaindex_turn_frame:protected.academic.attendance` | `1` | `0` | `0.0%` | `56.0` | `0.0` | `0.0` | `0.0` | `llamaindex` |
| `python_functions_turn_frame:protected.academic.attendance` | `1` | `0` | `0.0%` | `56.0` | `0.0` | `0.0` | `0.0` | `python_functions` |
| `contacts` | `1` | `0` | `0.0%` | `80.0` | `0.0` | `0.0` | `0.0` | `llamaindex` |
| `python_functions_local_public_explanatory:institution` | `1` | `1` | `0.0%` | `80.0` | `4.0` | `4.0` | `1.0` | `python_functions` |
| `python_functions_turn_frame:input_clarification` | `1` | `0` | `0.0%` | `80.0` | `0.0` | `0.0` | `0.0` | `python_functions` |
| `retrieval hibrido e o caminho padrao para faq e documentos` | `1` | `0` | `0.0%` | `80.0` | `0.0` | `0.0` | `0.0` | `langgraph` |
| `status administrativo autenticado exige service deterministico` | `1` | `0` | `0.0%` | `80.0` | `0.0` | `0.0` | `0.0` | `langgraph` |
| `public_bundle.academic_policy_overview` | `5` | `0` | `0.0%` | `82.4` | `0.0` | `0.0` | `0.0` | `langgraph, llamaindex, python_functions` |
| `python_functions_local_protected:academic` | `6` | `0` | `0.0%` | `85.0` | `0.0` | `0.0` | `0.0` | `python_functions` |
| `python_functions_local_restricted_documents` | `4` | `4` | `0.0%` | `85.0` | `4.0` | `4.0` | `1.0` | `python_functions` |
| `public_bundle.first_month_risks` | `3` | `0` | `0.0%` | `86.7` | `0.0` | `0.0` | `0.0` | `langgraph, llamaindex, python_functions` |
| `public_bundle.permanence_family_support` | `3` | `0` | `0.0%` | `86.7` | `0.0` | `0.0` | `0.0` | `langgraph, llamaindex, python_functions` |
| `llamaindex_local_protected:academic` | `7` | `0` | `0.0%` | `88.8` | `0.0` | `0.0` | `0.0` | `llamaindex` |
| `python_functions_local_public_unknown_safe_clarify` | `3` | `0` | `0.0%` | `89.3` | `0.0` | `0.0` | `0.0` | `python_functions` |
| `a intencao esta ambigua e exige clarificacao antes de recuperar contexto` | `5` | `0` | `0.0%` | `90.0` | `0.0` | `0.0` | `0.0` | `langgraph` |

## Recommendations

- `consulta autenticada de documento interno deve usar retrieval restrito com grounding` está com `answerable_rate=0.0%` sem saturar `top_k`; vale revisar query variants, metadata e chunking.
- `python_functions_local_restricted_documents` está com `answerable_rate=0.0%` e saturando `top_k`; vale testar `top_k` maior ou profile mais profundo.

## Trace Samples

### `llamaindex` `llamaindex_local_protected:academic` `retrieval_protected_family_panorama`

- Turn: `1`
- Prompt: Mantendo a comparacao anterior, tira o Lucas da conversa e mostra so o ponto academico mais fraco da Ana.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `55`, keyword pass `False`, latency `6486.5 ms`
- Reason: `llamaindex_local_protected:academic`
- Errors: `forbidden_entity_or_value`

### `python_functions` `python_functions_local_protected:academic` `retrieval_protected_family_panorama`

- Turn: `1`
- Prompt: Mantendo a comparacao anterior, tira o Lucas da conversa e mostra so o ponto academico mais fraco da Ana.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `55`, keyword pass `False`, latency `6619.9 ms`
- Reason: `python_functions_native_structured:academic`
- Errors: `forbidden_entity_or_value`

### `langgraph` `dados estruturados devem passar por service deterministico` `retrieval_protected_attendance_detail`

- Turn: `1`
- Prompt: Quero ver o ponto mais critico da frequencia do Lucas e em quais componentes as ausencias pesam mais.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `56`, keyword pass `False`, latency `876.7 ms`
- Reason: `dados estruturados devem passar por service deterministico`
- Errors: `attendance_metric_misroute, missing_expected_keyword`

### `llamaindex` `llamaindex_turn_frame:protected.academic.attendance` `retrieval_protected_attendance_detail`

- Turn: `1`
- Prompt: Quero ver o ponto mais critico da frequencia do Lucas e em quais componentes as ausencias pesam mais.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `56`, keyword pass `False`, latency `761.8 ms`
- Reason: `llamaindex_turn_frame:protected.academic.attendance`
- Errors: `attendance_metric_misroute, missing_expected_keyword`

### `python_functions` `python_functions_turn_frame:protected.academic.attendance` `retrieval_protected_attendance_detail`

- Turn: `1`
- Prompt: Quero ver o ponto mais critico da frequencia do Lucas e em quais componentes as ausencias pesam mais.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `56`, keyword pass `False`, latency `743.7 ms`
- Reason: `python_functions_native_structured:academic`
- Errors: `attendance_metric_misroute, missing_expected_keyword`

### `llamaindex` `public_bundle.academic_policy_overview` `retrieval_public_discipline_recovery`

- Turn: `1`
- Prompt: Sem um resumao generico, como convivencia, frequencia e recuperacao se encadeiam quando o aluno comeca a derrapar academicamente?
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `56`, keyword pass `False`, latency `2023.2 ms`
- Reason: `llamaindex_public_canonical_lane:public_bundle.academic_policy_overview`
- Errors: `attendance_metric_misroute, missing_expected_keyword`

### `python_functions` `public_bundle.academic_policy_overview` `retrieval_public_discipline_recovery`

- Turn: `1`
- Prompt: Sem um resumao generico, como convivencia, frequencia e recuperacao se encadeiam quando o aluno comeca a derrapar academicamente?
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `56`, keyword pass `False`, latency `4437.5 ms`
- Reason: `python_functions_native_canonical_lane:public_bundle.academic_policy_overview`
- Errors: `attendance_metric_misroute, missing_expected_keyword`

### `python_functions` `python_functions_local_public_unknown_safe_clarify` `retrieval_public_visibility_boundary`

- Turn: `1`
- Prompt: Sem olhar meu caso particular, o que qualquer familia ve sem login e o que ja depende de autenticacao?
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `68`, keyword pass `False`, latency `19970.6 ms`
- Reason: `python_functions_local_public_unknown_safe_clarify`
- Errors: `missing_expected_keyword, unnecessary_clarification`

### `langgraph` `status administrativo autenticado exige service deterministico` `retrieval_protected_admin_finance_combo`

- Turn: `1`
- Prompt: Resuma junto documentacao administrativa e financeiro das contas vinculadas para eu saber se ha impedimento de atendimento.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `80`, keyword pass `False`, latency `18866.4 ms`
- Reason: `status administrativo autenticado exige service deterministico`
- Errors: `missing_expected_keyword`

### `llamaindex` `o turno atual trouxe pistas explicitas de outro dominio protegido e o roteamento foi corrigido` `retrieval_protected_admin_finance_combo`

- Turn: `1`
- Prompt: Resuma junto documentacao administrativa e financeiro das contas vinculadas para eu saber se ha impedimento de atendimento.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `80`, keyword pass `False`, latency `677.9 ms`
- Reason: `llamaindex_protected_records_fast_path`
- Errors: `missing_expected_keyword`

### `python_functions` `python_functions_turn_frame:input_clarification` `retrieval_protected_admin_finance_combo`

- Turn: `1`
- Prompt: Resuma junto documentacao administrativa e financeiro das contas vinculadas para eu saber se ha impedimento de atendimento.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `80`, keyword pass `False`, latency `26412.9 ms`
- Reason: `python_functions_turn_frame:input_clarification`
- Errors: `missing_expected_keyword`

### `langgraph` `a intencao esta ambigua e exige clarificacao antes de recuperar contexto` `retrieval_protected_family_panorama`

- Turn: `1`
- Prompt: Mantendo a comparacao anterior, tira o Lucas da conversa e mostra so o ponto academico mais fraco da Ana.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `80`, keyword pass `False`, latency `17714.2 ms`
- Reason: `a intencao esta ambigua e exige clarificacao antes de recuperar contexto`
- Errors: `missing_expected_keyword`

