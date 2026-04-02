# Retrieval 30Q Final Stage Report

Date: 2026-04-02T13:42:14.048277+00:00

Dataset: `/home/edann/projects/eduassist-platform/tests/evals/datasets/retrieval_30q_probe_cases.generated.20260402.json`

## Dataset

- Questions: `30`
- Exact overlap with prior datasets: `0`
- Categories covered: `27`
- Public / Protected / Restricted: `19` / `6` / `5`

## Leaderboards

- Quality leader: `specialist_supervisor`
- Best latency leader: `python_functions`
- Best quality/latency balance: `specialist_supervisor`

## Stack Summary

| Stack | Keyword pass | Quality | Avg | Median | P95 | Max |
| --- | --- | --- | --- | --- | --- | --- |
| `langgraph` | `21/30` | `92.5` | `1178.1 ms` | `230.1 ms` | `3978.6 ms` | `5408.2 ms` |
| `crewai` | `10/30` | `84.0` | `3425.2 ms` | `192.2 ms` | `20264.0 ms` | `20672.8 ms` |
| `python_functions` | `21/30` | `91.7` | `165.0 ms` | `122.2 ms` | `412.6 ms` | `505.7 ms` |
| `llamaindex` | `21/30` | `92.5` | `1652.7 ms` | `139.9 ms` | `11658.2 ms` | `17177.7 ms` |
| `specialist_supervisor` | `26/30` | `96.1` | `1686.1 ms` | `125.1 ms` | `11073.4 ms` | `18033.4 ms` |

## Slice Summary

### `protected`

| Stack | Keyword pass | Quality | Avg latency |
| --- | --- | --- | --- |
| `langgraph` | `4/6` | `93.3` | `555.1 ms` |
| `crewai` | `3/6` | `90.0` | `3665.6 ms` |
| `python_functions` | `4/6` | `91.3` | `162.2 ms` |
| `llamaindex` | `4/6` | `93.3` | `2757.5 ms` |
| `specialist_supervisor` | `5/6` | `94.7` | `705.1 ms` |

### `public`

| Stack | Keyword pass | Quality | Avg latency |
| --- | --- | --- | --- |
| `langgraph` | `12/19` | `90.3` | `1326.0 ms` |
| `crewai` | `5/19` | `81.6` | `3243.0 ms` |
| `python_functions` | `12/19` | `89.6` | `115.2 ms` |
| `llamaindex` | `12/19` | `90.3` | `1638.2 ms` |
| `specialist_supervisor` | `16/19` | `95.5` | `2344.5 ms` |

### `restricted`

| Stack | Keyword pass | Quality | Avg latency |
| --- | --- | --- | --- |
| `langgraph` | `5/5` | `100.0` | `1363.6 ms` |
| `crewai` | `2/5` | `85.6` | `3829.2 ms` |
| `python_functions` | `5/5` | `100.0` | `357.7 ms` |
| `llamaindex` | `5/5` | `100.0` | `381.9 ms` |
| `specialist_supervisor` | `5/5` | `100.0` | `361.1 ms` |

## High-Signal Findings

- `specialist_supervisor` terminou com a melhor qualidade média (`96.1`) e o melhor keyword pass (`26/30`).
- `python_functions` continuou como o caminho mais rápido, com média de `165.0 ms` e mediana de `122.2 ms`.
- `specialist_supervisor` fechou com qualidade líder, mas ainda paga cauda longa em público complexo: P95 `11073.4 ms`, com outliers em `Q206`, `Q223` e `Q210`.
- `llamaindex` empatou com `langgraph` em qualidade (`92.5`), mas teve cauda bem pior: P95 `11658.2 ms` e max `17177.7 ms`.
- `crewai` terminou claramente atrás: qualidade `84.0`, keyword pass `10/30`, P95 `20264.0 ms`.

## Path Backlog

### `langgraph`

- `public_permanence_support` apareceu em `1` falha(s) desta rodada.
- `protected_structured_followup` apareceu em `1` falha(s) desta rodada.
- `protected_structured_admin` apareceu em `1` falha(s) desta rodada.
- `public_teacher_directory` apareceu em `1` falha(s) desta rodada.
- `public_year_three_phases` apareceu em `1` falha(s) desta rodada.
- Outlier: `Q216` `restricted_doc_positive` em `5408.2 ms` com reason `langgraph_restricted_document_search`.
- Outlier: `Q202` `public_timeline` em `3998.0 ms` com reason `bundle publico canonico deve seguir lane publica mesmo se a classificacao superestimar autenticacao`.
- Outlier: `Q221` `public_service_routing` em `3954.8 ms` com reason `fato institucional canonico deve vir de fonte estruturada`.

### `crewai`

- `restricted_doc_positive` apareceu em `2` falha(s) desta rodada.
- `public_policy_bridge` apareceu em `1` falha(s) desta rodada.
- `public_timeline` apareceu em `1` falha(s) desta rodada.
- `public_permanence_support` apareceu em `1` falha(s) desta rodada.
- `public_process_compare` apareceu em `1` falha(s) desta rodada.
- Outlier: `Q213` `protected_structured_followup` em `20672.8 ms` com reason `crewai_protected_flow_timeout`.
- Outlier: `Q206` `public_process_compare` em `20301.6 ms` com reason `crewai_public_flow_timeout`.
- Outlier: `Q227` `public_bolsas_and_processes` em `20218.1 ms` com reason `crewai_public_flow_timeout`.

### `python_functions`

- `protected_structured_followup` apareceu em `1` falha(s) desta rodada.
- `public_teacher_directory` apareceu em `1` falha(s) desta rodada.
- `public_calendar_week` apareceu em `1` falha(s) desta rodada.
- `public_year_three_phases` apareceu em `1` falha(s) desta rodada.
- `public_academic_policy_overview` apareceu em `1` falha(s) desta rodada.
- Outlier: `Q218` `restricted_doc_positive` em `505.7 ms` com reason `python_functions_native_restricted_document_search`.
- Outlier: `Q217` `restricted_doc_positive` em `421.8 ms` com reason `python_functions_native_restricted_document_search`.
- Outlier: `Q216` `restricted_doc_positive` em `401.3 ms` com reason `python_functions_native_restricted_document_search`.

### `llamaindex`

- `protected_structured_followup` apareceu em `1` falha(s) desta rodada.
- `public_teacher_directory` apareceu em `1` falha(s) desta rodada.
- `public_calendar_week` apareceu em `1` falha(s) desta rodada.
- `public_year_three_phases` apareceu em `1` falha(s) desta rodada.
- `public_academic_policy_overview` apareceu em `1` falha(s) desta rodada.
- Outlier: `Q222` `public_teacher_directory` em `17177.7 ms` com reason `fato institucional canonico deve vir de fonte estruturada`.
- Outlier: `Q213` `protected_structured_followup` em `15671.5 ms` com reason `llamaindex_public_profile`.
- Outlier: `Q221` `public_service_routing` em `6753.0 ms` com reason `llamaindex_public_profile`.

### `specialist_supervisor`

- `public_process_compare` apareceu em `1` falha(s) desta rodada.
- `protected_structured_followup` apareceu em `1` falha(s) desta rodada.
- `public_teacher_directory` apareceu em `1` falha(s) desta rodada.
- `public_conduct_frequency_punctuality` apareceu em `1` falha(s) desta rodada.
- Outlier: `Q206` `public_process_compare` em `18033.4 ms` com reason `specialist_supervisor_strict_safe_fallback`.
- Outlier: `Q223` `public_calendar_week` em `11123.9 ms` com reason `specialist_supervisor_direct:institution_specialist`.
- Outlier: `Q210` `public_visibility_boundary` em `11011.7 ms` com reason `specialist_supervisor_direct:institution_specialist`.

## Notable New 30Q Cases

- `Q221` `public_service_routing`: Como entrar em contato com admissoes, financeiro e direcao quando o assunto mistura bolsa e mensalidade?
- `Q222` `public_teacher_directory`: O colegio passa contato direto do professor de matematica ou orienta a familia pela coordenacao?
- `Q223` `public_calendar_week`: Quero os principais eventos publicos para familias e responsaveis nesta base escolar.
- `Q224` `public_year_three_phases`: Se eu dividir o ano em admissao, rotina academica e fechamento, como isso aparece na linha do tempo publica?
- `Q225` `public_academic_policy_overview`: Na escola, como a politica de avaliacao, recuperacao e promocao conversa com media e frequencia minima?
- `Q226` `public_conduct_frequency_punctuality`: Quero entender como a escola amarra convivencia, pontualidade e frequencia no regulamento publico.
- `Q227` `public_bolsas_and_processes`: Como a escola conecta edital de bolsas com rematricula, transferencia e cancelamento?
- `Q228` `public_pricing_projection`: Usando a tabela publica, quanto dariam matricula e mensalidade para 3 filhos?
- `Q229` `protected_access_scope`: Me diga o escopo atual da minha conta neste canal, incluindo acesso academico e financeiro.
- `Q230` `protected_admin_finance_combo`: Quero um quadro unico de documentacao e financeiro para saber se alguma pendencia esta bloqueando atendimento.

## Final Reading

- Se a prioridade for `melhor qualidade absoluta`, o fechamento desta etapa favorece `specialist_supervisor`.
- Se a prioridade for `melhor equilibrio entre qualidade e latencia`, o fechamento desta etapa favorece `python_functions`.
- Se a prioridade for `stack intermediaria mais estavel`, `langgraph` continua sendo a melhor opcao.
- `llamaindex` melhorou muito em qualidade, mas ainda precisa de trabalho de P95 e de roteamento publico canonico.
- `crewai` deve permanecer como baseline comparativa, nao como melhor candidato para otimizacao principal nesta fase.
