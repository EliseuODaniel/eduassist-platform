# Retrieval Trace Calibration Report

Generated at: 2026-04-15T04:37:32.094848+00:00

Run prefix: `debug:four-path:normal:20260415T042421Z`

Eval JSON: `docs/architecture/retrieval-broad-30q-cycle1-seq-cross-path-report.json`

## Stack Summary

| Stack | Count | Retrieval traces | Answerable | Quality | Avg top_k | Avg hits | Avg selected | Coverage | Latency |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `langgraph` | `29` | `5` | `0.0%` | `91.6` | `3.2` | `0.8` | `0.8` | `1.0` | `7914.4 ms` |
| `python_functions` | `30` | `2` | `0.0%` | `84.3` | `5.5` | `2.0` | `2.0` | `1.0` | `8078.6 ms` |
| `llamaindex` | `29` | `2` | `0.0%` | `88.0` | `4.0` | `4.0` | `4.0` | `1.0` | `6577.3 ms` |
| `specialist_supervisor` | `0` | `0` | `0.0%` | `0.0` | `0.0` | `0.0` | `0.0` | `0.0` | `0.0 ms` |

## Capability Highlights

| Capability | Count | Retrieval traces | Answerable | Quality | Avg top_k | Avg hits | Coverage | Stacks |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `public_bundle.conduct_frequency_punctuality` | `2` | `0` | `0.0%` | `0.0` | `0.0` | `0.0` | `0.0` | `llamaindex, python_functions` |
| `bundle publico canonico deve seguir lane publica mesmo se a classificacao superestimar autenticacao` | `1` | `0` | `0.0%` | `0.0` | `0.0` | `0.0` | `0.0` | `langgraph` |
| `llamaindex_local_clarify` | `1` | `0` | `0.0%` | `0.0` | `0.0` | `0.0` | `0.0` | `llamaindex` |
| `python_functions_turn_frame:input_clarification` | `3` | `0` | `0.0%` | `51.7` | `0.0` | `0.0` | `0.0` | `python_functions` |
| `python_functions_native_contextual_public_answer` | `2` | `0` | `0.0%` | `57.5` | `0.0` | `0.0` | `0.0` | `python_functions` |
| `a intencao esta ambigua e exige clarificacao antes de recuperar contexto` | `2` | `0` | `0.0%` | `68.0` | `0.0` | `0.0` | `0.0` | `langgraph` |
| `llamaindex_local_public_default:institution` | `1` | `0` | `0.0%` | `68.0` | `0.0` | `0.0` | `0.0` | `llamaindex` |
| `python_functions_local_protected:academic` | `3` | `0` | `0.0%` | `77.5` | `0.0` | `0.0` | `0.0` | `python_functions` |
| `llamaindex_local_protected:academic` | `5` | `0` | `0.0%` | `78.8` | `0.0` | `0.0` | `0.0` | `llamaindex` |
| `authenticated_public_profile_rescue` | `2` | `0` | `0.0%` | `80.0` | `0.0` | `0.0` | `0.0` | `langgraph` |
| `python_functions_local_restricted_documents` | `2` | `2` | `0.0%` | `80.0` | `5.5` | `2.0` | `1.0` | `python_functions` |
| `python_functions_native_teacher_schedule` | `2` | `0` | `0.0%` | `80.0` | `0.0` | `0.0` | `0.0` | `python_functions` |
| `consulta autenticada de documento interno deve usar retrieval restrito com grounding` | `1` | `1` | `0.0%` | `80.0` | `3.0` | `0.0` | `1.0` | `langgraph` |
| `llamaindex_local_protected:finance` | `1` | `0` | `0.0%` | `80.0` | `0.0` | `0.0` | `0.0` | `llamaindex` |
| `llamaindex_local_public_default:academic` | `1` | `1` | `0.0%` | `80.0` | `4.0` | `4.0` | `1.0` | `llamaindex` |

## Recommendations

- Nenhum ajuste forte recomendado nesta janela.

## Trace Samples

### `python_functions` `python_functions_turn_frame:input_clarification` `retrieval_restricted_teacher_manual`

- Turn: `1`
- Prompt: Sem sair do escopo do projeto, segundo o Manual interno do professor, como a escola orienta registro de avaliacoes e comunicacao pedagogica?
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `32`, keyword pass `False`, latency `20472.7 ms`
- Reason: `python_functions_turn_frame:input_clarification`
- Errors: `missing_expected_keyword, multi_intent_partial_collapse, unnecessary_clarification, weak_actionability`

### `python_functions` `python_functions_native_contextual_public_answer` `retrieval_public_external_library_boundary`

- Turn: `1`
- Prompt: Esquece a escola por um momento: a biblioteca publica da cidade fecha que horas?
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `35`, keyword pass `False`, latency `16554.8 ms`
- Reason: `python_functions_native_contextual_public_answer`
- Errors: `forbidden_entity_or_value, missing_expected_keyword`

### `python_functions` `python_functions_turn_frame:input_clarification` `retrieval_public_open_world_out_of_scope`

- Turn: `1`
- Prompt: Quero uma recomendacao de filme, sem relacao com escola.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `43`, keyword pass `False`, latency `19337.5 ms`
- Reason: `python_functions_turn_frame:input_clarification`
- Errors: `forbidden_entity_or_value, unnecessary_clarification`

### `langgraph` `dados estruturados devem passar por service deterministico` `retrieval_staff_finance_protocol`

- Turn: `1`
- Prompt: Quero o trecho operacional: no fluxo interno de pagamento parcial, o que precisa ser validado antes de prometer quitacao?
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `54`, keyword pass `False`, latency `11281.6 ms`
- Reason: `dados estruturados devem passar por service deterministico`
- Errors: `missing_expected_keyword, multi_intent_partial_collapse`

### `llamaindex` `llamaindex_local_protected:academic` `retrieval_protected_family_panorama`

- Turn: `1`
- Prompt: Mantendo a comparacao anterior, tira o Lucas da conversa e mostra so o ponto academico mais fraco da Ana.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `55`, keyword pass `False`, latency `7117.2 ms`
- Reason: `llamaindex_local_protected:academic`
- Errors: `forbidden_entity_or_value`

### `python_functions` `python_functions_local_protected:academic` `retrieval_protected_family_panorama`

- Turn: `1`
- Prompt: Mantendo a comparacao anterior, tira o Lucas da conversa e mostra so o ponto academico mais fraco da Ana.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `55`, keyword pass `False`, latency `7310.0 ms`
- Reason: `python_functions_native_structured:academic`
- Errors: `forbidden_entity_or_value`

### `llamaindex` `public_bundle.academic_policy_overview` `retrieval_public_discipline_recovery`

- Turn: `1`
- Prompt: Sem um resumao generico, como convivencia, frequencia e recuperacao se encadeiam quando o aluno comeca a derrapar academicamente?
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `56`, keyword pass `False`, latency `3482.9 ms`
- Reason: `llamaindex_public_canonical_lane:public_bundle.academic_policy_overview`
- Errors: `attendance_metric_misroute, missing_expected_keyword`

### `langgraph` `a intencao esta ambigua e exige clarificacao antes de recuperar contexto` `retrieval_protected_family_panorama`

- Turn: `1`
- Prompt: Mantendo a comparacao anterior, tira o Lucas da conversa e mostra so o ponto academico mais fraco da Ana.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `68`, keyword pass `False`, latency `23172.1 ms`
- Reason: `a intencao esta ambigua e exige clarificacao antes de recuperar contexto`
- Errors: `missing_expected_keyword, unnecessary_clarification`

### `llamaindex` `llamaindex_local_public_default:institution` `retrieval_public_external_library_boundary`

- Turn: `1`
- Prompt: Esquece a escola por um momento: a biblioteca publica da cidade fecha que horas?
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `68`, keyword pass `False`, latency `16759.6 ms`
- Reason: `llamaindex_contextual_public_boundary_fast_path`
- Errors: `missing_expected_keyword, unnecessary_clarification`

### `langgraph` `dados estruturados devem passar por service deterministico` `retrieval_protected_access_scope`

- Turn: `1`
- Prompt: Quais dados dos meus filhos eu consigo acessar por aqui, e se o meu acesso cobre academico e financeiro?
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `80`, keyword pass `False`, latency `2093.3 ms`
- Reason: `dados estruturados devem passar por service deterministico`
- Errors: `missing_expected_keyword`

### `llamaindex` `llamaindex_local_protected:finance` `retrieval_protected_access_scope`

- Turn: `1`
- Prompt: Quais dados dos meus filhos eu consigo acessar por aqui, e se o meu acesso cobre academico e financeiro?
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `80`, keyword pass `False`, latency `1159.3 ms`
- Reason: `llamaindex_local_protected:finance`
- Errors: `missing_expected_keyword`

### `python_functions` `python_functions_local_protected:finance` `retrieval_protected_access_scope`

- Turn: `1`
- Prompt: Quais dados dos meus filhos eu consigo acessar por aqui, e se o meu acesso cobre academico e financeiro?
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `80`, keyword pass `False`, latency `1336.2 ms`
- Reason: `python_functions_native_structured:finance`
- Errors: `missing_expected_keyword`

