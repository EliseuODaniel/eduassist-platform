# Retrieval Trace Calibration Report

Generated at: 2026-04-15T13:29:36.937013+00:00

Run prefix: `debug:four-path:normal:20260415T131911Z`

Eval JSON: `docs/architecture/retrieval-broad-30q-cycle1-fixval7-cross-path-report.json`

## Stack Summary

| Stack | Count | Retrieval traces | Answerable | Quality | Avg top_k | Avg hits | Avg selected | Coverage | Latency |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `langgraph` | `30` | `5` | `0.0%` | `97.8` | `3.0` | `0.0` | `0.8` | `1.0` | `6950.4 ms` |
| `python_functions` | `30` | `5` | `0.0%` | `98.9` | `6.6` | `0.0` | `0.8` | `1.0` | `6494.0 ms` |
| `llamaindex` | `30` | `0` | `0.0%` | `98.9` | `0.0` | `0.0` | `0.0` | `0.0` | `6653.4 ms` |
| `specialist_supervisor` | `0` | `0` | `0.0%` | `0.0` | `0.0` | `0.0` | `0.0` | `0.0` | `0.0 ms` |

## Capability Highlights

| Capability | Count | Retrieval traces | Answerable | Quality | Avg top_k | Avg hits | Coverage | Stacks |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `llamaindex_turn_frame:protected.academic.attendance` | `1` | `0` | `0.0%` | `0.0` | `0.0` | `0.0` | `0.0` | `llamaindex` |
| `python_functions_turn_frame:protected.academic.attendance` | `1` | `0` | `0.0%` | `0.0` | `0.0` | `0.0` | `0.0` | `python_functions` |
| `public_bundle.governance_protocol` | `3` | `0` | `0.0%` | `86.7` | `0.0` | `0.0` | `0.0` | `langgraph, llamaindex, python_functions` |
| `o turno atual trouxe pistas explicitas de outro dominio protegido e o roteamento foi corrigido` | `2` | `0` | `0.0%` | `90.0` | `0.0` | `0.0` | `0.0` | `langgraph` |
| `pricing` | `2` | `0` | `0.0%` | `90.0` | `0.0` | `0.0` | `0.0` | `langgraph, python_functions` |
| `auth_guidance` | `3` | `0` | `0.0%` | `93.3` | `0.0` | `0.0` | `0.0` | `langgraph, llamaindex, python_functions` |
| `public_bundle.facilities_study_support` | `3` | `0` | `0.0%` | `93.3` | `0.0` | `0.0` | `0.0` | `langgraph, llamaindex, python_functions` |
| `protected.documents.restricted_lookup` | `10` | `10` | `0.0%` | `100.0` | `4.8` | `0.0` | `1.0` | `langgraph, python_functions` |
| `llamaindex_local_protected:academic` | `7` | `0` | `0.0%` | `100.0` | `0.0` | `0.0` | `0.0` | `llamaindex` |
| `dados estruturados devem passar por service deterministico` | `6` | `0` | `0.0%` | `100.0` | `0.0` | `0.0` | `0.0` | `langgraph` |
| `llamaindex_local_restricted_documents;turn_frame=protected.documents.restricted_lookup` | `4` | `0` | `0.0%` | `100.0` | `0.0` | `0.0` | `0.0` | `llamaindex` |
| `python_functions_local_protected:academic` | `4` | `0` | `0.0%` | `100.0` | `0.0` | `0.0` | `0.0` | `python_functions` |
| `public_bundle.academic_policy_overview` | `3` | `0` | `0.0%` | `100.0` | `0.0` | `0.0` | `0.0` | `langgraph, llamaindex, python_functions` |
| `public_bundle.family_new_calendar_assessment_enrollment` | `3` | `0` | `0.0%` | `100.0` | `0.0` | `0.0` | `0.0` | `langgraph, llamaindex, python_functions` |
| `public_bundle.secretaria_portal_credentials` | `3` | `0` | `0.0%` | `100.0` | `0.0` | `0.0` | `0.0` | `langgraph, llamaindex, python_functions` |

## Recommendations

- `protected.documents.restricted_lookup` está com `answerable_rate=0.0%` sem saturar `top_k`; vale revisar query variants, metadata e chunking.

## Trace Samples

### `langgraph` `o turno atual trouxe pistas explicitas de outro dominio protegido e o roteamento foi corrigido` `retrieval_protected_admin_docs`

- Turn: `1`
- Prompt: Pensando no caso pratico, no cadastro da Ana, quais pendencias administrativas continuam abertas e que acao vem agora?
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `80`, keyword pass `False`, latency `1581.5 ms`
- Reason: `o turno atual trouxe pistas explicitas de outro dominio protegido e o roteamento foi corrigido`
- Errors: `missing_expected_keyword`

### `langgraph` `auth_guidance` `retrieval_protected_boundary_auth_needed`

- Turn: `1`
- Prompt: Nao estou autenticado e mesmo assim quero consultar meu boletim aqui pelo bot.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `80`, keyword pass `False`, latency `3381.3 ms`
- Reason: `langgraph_turn_frame:public_answer`
- Errors: `missing_expected_keyword`

### `llamaindex` `public_bundle.governance_protocol` `retrieval_public_governance_protocol`

- Turn: `1`
- Prompt: Na base publica, como aparecem conectados direcao, atendimento formal e numero de protocolo?
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `80`, keyword pass `False`, latency `2294.8 ms`
- Reason: `llamaindex_public_canonical_lane:public_bundle.governance_protocol`
- Errors: `missing_expected_keyword`

### `python_functions` `public_bundle.governance_protocol` `retrieval_public_governance_protocol`

- Turn: `1`
- Prompt: Na base publica, como aparecem conectados direcao, atendimento formal e numero de protocolo?
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `80`, keyword pass `False`, latency `4972.8 ms`
- Reason: `python_functions_native_canonical_lane:public_bundle.governance_protocol`
- Errors: `missing_expected_keyword`

### `langgraph` `pricing` `retrieval_public_pricing_projection`

- Turn: `1`
- Prompt: Pela referencia publica de precos, qual seria a matricula total e o valor mensal para 3 filhos. Traga a resposta de forma concreta.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `80`, keyword pass `False`, latency `14578.7 ms`
- Reason: `langgraph_turn_frame:public_answer`
- Errors: `missing_expected_keyword`

### `llamaindex` `public_bundle.facilities_study_support` `retrieval_public_facilities_study`

- Turn: `1`
- Prompt: De que forma os documentos publicos ligam biblioteca, laboratorios e estudo orientado como suporte ao ensino medio. Responda de forma direta.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `90`, keyword pass `True`, latency `2643.8 ms`
- Reason: `llamaindex_public_canonical_lane:public_bundle.facilities_study_support`
- Errors: `weak_actionability`

### `python_functions` `public_bundle.facilities_study_support` `retrieval_public_facilities_study`

- Turn: `1`
- Prompt: De que forma os documentos publicos ligam biblioteca, laboratorios e estudo orientado como suporte ao ensino medio. Responda de forma direta.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `90`, keyword pass `True`, latency `6592.9 ms`
- Reason: `python_functions_native_canonical_lane:public_bundle.facilities_study_support`
- Errors: `weak_actionability`

### `langgraph` `a intencao esta ambigua e exige clarificacao antes de recuperar contexto` `retrieval_protected_access_scope`

- Turn: `1`
- Prompt: Qual e exatamente o meu escopo aqui? Quero saber se estou autenticado e quais dados academicos e financeiros consigo ver.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `100`, keyword pass `True`, latency `22668.4 ms`
- Reason: `a intencao esta ambigua e exige clarificacao antes de recuperar contexto`

### `llamaindex` `llamaindex_local_protected:finance` `retrieval_protected_access_scope`

- Turn: `1`
- Prompt: Qual e exatamente o meu escopo aqui? Quero saber se estou autenticado e quais dados academicos e financeiros consigo ver.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `100`, keyword pass `True`, latency `775.6 ms`
- Reason: `llamaindex_local_protected:finance`

### `python_functions` `python_functions_native_authenticated_account_scope` `retrieval_protected_access_scope`

- Turn: `1`
- Prompt: Qual e exatamente o meu escopo aqui? Quero saber se estou autenticado e quais dados academicos e financeiros consigo ver.
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `100`, keyword pass `True`, latency `818.7 ms`
- Reason: `python_functions_native_authenticated_account_scope`

### `llamaindex` `contextual_public_direct_answer` `retrieval_protected_admin_docs`

- Turn: `1`
- Prompt: Pensando no caso pratico, no cadastro da Ana, quais pendencias administrativas continuam abertas e que acao vem agora?
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `100`, keyword pass `True`, latency `857.2 ms`
- Reason: `contextual_public_direct_answer`

### `python_functions` `python_functions_native_public_compound` `retrieval_protected_admin_docs`

- Turn: `1`
- Prompt: Pensando no caso pratico, no cadastro da Ana, quais pendencias administrativas continuam abertas e que acao vem agora?
- Policy: `unknown` / `top_k=0` / `unknown`
- Retrieval: hits `0/0`, coverage `0.0`, answerable `None`
- Eval: quality `100`, keyword pass `True`, latency `5444.9 ms`
- Reason: `python_functions_native_public_compound`

