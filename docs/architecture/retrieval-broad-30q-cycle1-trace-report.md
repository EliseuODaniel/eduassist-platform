# Retrieval Trace Calibration Report

Generated at: 2026-04-15T04:16:05.659762+00:00

Run prefix: `debug:four-path:normal:20260415T040512Z`

Eval JSON: `docs/architecture/retrieval-broad-30q-cycle1-cross-path-report.json`

## Stack Summary

| Stack | Count | Retrieval traces | Answerable | Quality | Avg top_k | Avg hits | Avg selected | Coverage | Latency |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `langgraph` | `28` | `4` | `0.0%` | `59.0` | `3.0` | `0.0` | `0.0` | `1.0` | `19068.5 ms` |
| `python_functions` | `29` | `2` | `0.0%` | `64.0` | `7.0` | `0.0` | `0.0` | `1.0` | `18523.6 ms` |
| `llamaindex` | `28` | `1` | `0.0%` | `66.2` | `4.0` | `4.0` | `4.0` | `1.0` | `15861.9 ms` |
| `specialist_supervisor` | `0` | `0` | `0.0%` | `0.0` | `0.0` | `0.0` | `0.0` | `0.0` | `0.0 ms` |

## Capability Highlights

| Capability | Count | Retrieval traces | Answerable | Quality | Avg top_k | Avg hits | Coverage | Stacks |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `llamaindex_local_public_fact:institution` | `2` | `0` | `0.0%` | `0.0` | `0.0` | `0.0` | `0.0` | `llamaindex` |
| `teacher_directory` | `2` | `0` | `0.0%` | `0.0` | `0.0` | `0.0` | `0.0` | `langgraph, llamaindex` |
| `leadership` | `1` | `0` | `0.0%` | `0.0` | `0.0` | `0.0` | `0.0` | `langgraph` |
| `llamaindex_local_protected:institution` | `1` | `0` | `0.0%` | `0.0` | `0.0` | `0.0` | `0.0` | `llamaindex` |
| `llamaindex_local_public_default:academic` | `1` | `1` | `0.0%` | `0.0` | `4.0` | `4.0` | `1.0` | `llamaindex` |
| `llamaindex_turn_frame:protected.academic.attendance` | `1` | `0` | `0.0%` | `0.0` | `0.0` | `0.0` | `0.0` | `llamaindex` |
| `public_bundle.teacher_directory_boundary` | `1` | `0` | `0.0%` | `0.0` | `0.0` | `0.0` | `0.0` | `python_functions` |
| `python_functions_local_clarify` | `1` | `0` | `0.0%` | `0.0` | `0.0` | `0.0` | `0.0` | `python_functions` |
| `python_functions_local_protected:institution` | `1` | `0` | `0.0%` | `0.0` | `0.0` | `0.0` | `0.0` | `python_functions` |
| `python_functions_native_contextual_public_answer` | `1` | `0` | `0.0%` | `0.0` | `0.0` | `0.0` | `0.0` | `python_functions` |
| `python_functions_turn_frame:input_clarification` | `1` | `0` | `0.0%` | `0.0` | `0.0` | `0.0` | `0.0` | `python_functions` |
| `python_functions_turn_frame:protected.academic.attendance` | `1` | `0` | `0.0%` | `0.0` | `0.0` | `0.0` | `0.0` | `python_functions` |
| `status administrativo autenticado exige service deterministico` | `1` | `0` | `0.0%` | `0.0` | `0.0` | `0.0` | `0.0` | `langgraph` |
| `python_functions_native_public_compound` | `3` | `0` | `0.0%` | `11.7` | `0.0` | `0.0` | `0.0` | `python_functions` |
| `a intencao esta ambigua e exige clarificacao antes de recuperar contexto` | `3` | `0` | `0.0%` | `26.7` | `0.0` | `0.0` | `0.0` | `langgraph` |

## Recommendations

- Nenhum ajuste forte recomendado nesta janela.

## Trace Samples

### `langgraph` `a intencao esta ambigua e exige clarificacao antes de recuperar contexto` `retrieval_protected_access_scope`

- Turn: `1`
- Prompt: Qual e exatamente o meu escopo aqui? Quero saber se estou autenticado e quais dados academicos e financeiros consigo ver.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `0`, keyword pass `False`, latency `40157.6 ms`
- Reason: `exception`
- Errors: `request_failed`

### `langgraph` `status administrativo autenticado exige service deterministico` `retrieval_protected_admin_finance_combo`

- Turn: `1`
- Prompt: Tem algo na minha documentacao ou no cadastro que esteja travando o financeiro? Me de a visao combinada.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `0`, keyword pass `False`, latency `40142.1 ms`
- Reason: `exception`
- Errors: `request_failed`

### `llamaindex` `llamaindex_local_protected:institution` `retrieval_protected_admin_finance_combo`

- Turn: `1`
- Prompt: Tem algo na minha documentacao ou no cadastro que esteja travando o financeiro? Me de a visao combinada.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `0`, keyword pass `False`, latency `40085.3 ms`
- Reason: `exception`
- Errors: `request_failed`

### `python_functions` `python_functions_local_protected:institution` `retrieval_protected_admin_finance_combo`

- Turn: `1`
- Prompt: Tem algo na minha documentacao ou no cadastro que esteja travando o financeiro? Me de a visao combinada.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `0`, keyword pass `False`, latency `40111.1 ms`
- Reason: `exception`
- Errors: `request_failed`

### `langgraph` `o turno atual trouxe pistas explicitas de outro dominio protegido e o roteamento foi corrigido` `retrieval_protected_boundary_auth_needed`

- Turn: `1`
- Prompt: Quero minhas notas sem passar por login. O que acontece nesse caso?
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `0`, keyword pass `False`, latency `40204.3 ms`
- Reason: `exception`
- Errors: `request_failed`

### `python_functions` `python_functions_local_clarify` `retrieval_protected_boundary_auth_needed`

- Turn: `1`
- Prompt: Quero minhas notas sem passar por login. O que acontece nesse caso?
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `0`, keyword pass `False`, latency `40165.3 ms`
- Reason: `exception`
- Errors: `request_failed`

### `python_functions` `public_bundle.academic_policy_overview` `retrieval_public_discipline_recovery`

- Turn: `1`
- Prompt: Cruze regulamentos gerais, politica de avaliacao e orientacao ao estudante para explicar como disciplina, frequencia e recuperacao se influenciam. Traga a resposta de forma concreta.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `0`, keyword pass `False`, latency `40120.3 ms`
- Reason: `exception`
- Errors: `request_failed`

### `langgraph` `langgraph_turn_frame:input_clarification` `retrieval_public_known_unknown_total_teachers`

- Turn: `1`
- Prompt: Existe numero publico de professores na escola ou esse dado nao e informado oficialmente?
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `0`, keyword pass `False`, latency `40144.9 ms`
- Reason: `exception`
- Errors: `request_failed`

### `llamaindex` `teacher_directory` `retrieval_public_known_unknown_total_teachers`

- Turn: `1`
- Prompt: Existe numero publico de professores na escola ou esse dado nao e informado oficialmente?
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `0`, keyword pass `False`, latency `40082.4 ms`
- Reason: `exception`
- Errors: `request_failed`

### `langgraph` `a intencao esta ambigua e exige clarificacao antes de recuperar contexto` `retrieval_public_open_world_out_of_scope`

- Turn: `1`
- Prompt: Fora do tema escolar, qual filme voce acha que mais vale a pena ver agora?
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `0`, keyword pass `False`, latency `40172.5 ms`
- Reason: `exception`
- Errors: `request_failed`

### `llamaindex` `llamaindex_local_public_unknown_safe_clarify` `retrieval_public_open_world_out_of_scope`

- Turn: `1`
- Prompt: Fora do tema escolar, qual filme voce acha que mais vale a pena ver agora?
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `0`, keyword pass `False`, latency `40116.4 ms`
- Reason: `exception`
- Errors: `request_failed`

### `python_functions` `python_functions_native_contextual_public_answer` `retrieval_public_open_world_out_of_scope`

- Turn: `1`
- Prompt: Fora do tema escolar, qual filme voce acha que mais vale a pena ver agora?
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `0`, keyword pass `False`, latency `40143.1 ms`
- Reason: `exception`
- Errors: `request_failed`

