# Retrieval 28Q Final Stage Report

Date: 2026-04-02

Dataset:
- `/home/edann/projects/eduassist-platform/tests/evals/datasets/retrieval_28q_probe_cases.generated.20260402.json`

Raw reports:
- `/home/edann/projects/eduassist-platform/docs/architecture/retrieval-28q-cross-path-report-20260402.md`
- `/home/edann/projects/eduassist-platform/docs/architecture/retrieval-28q-cross-path-report-20260402.json`

## Scope

- 28 perguntas inéditas
- 25 categorias
- zero overlap exato com datasets anteriores
- 19 casos públicos
- 4 casos protegidos
- 5 casos restritos
- 4 caminhos ativos:
  - `langgraph`
  - `python_functions`
  - `llamaindex`
  - `specialist_supervisor`

## Executive Summary

Os quatro caminhos fecharam a rodada sem falhas de runtime: `28/28 ok`.

O resultado mais forte desta bateria foi:
- `langgraph` e `specialist_supervisor` lideraram em qualidade média: `97.9`
- `python_functions` manteve a melhor eficiência operacional: `201.0 ms`
- `llamaindex` ficou competitivo em qualidade (`97.1`) e mostrou boa mediana (`142.9 ms`), mas ainda teve um outlier severo que puxou a média

## Scorecard

| Stack | OK | Keyword pass | Quality | Avg latency | Median | P95 | Max |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `langgraph` | `28/28` | `25/28` | `97.9` | `334.2 ms` | `185.4 ms` | `1179.4 ms` | `1807.0 ms` |
| `python_functions` | `28/28` | `24/28` | `96.7` | `201.0 ms` | `170.1 ms` | `313.7 ms` | `370.7 ms` |
| `llamaindex` | `28/28` | `24/28` | `97.1` | `376.7 ms` | `142.9 ms` | `425.6 ms` | `5601.0 ms` |
| `specialist_supervisor` | `28/28` | `25/28` | `97.9` | `235.1 ms` | `87.5 ms` | `625.8 ms` | `2062.7 ms` |

## Slice Analysis

### Public

`public` continua sendo o principal diferenciador.

| Stack | Keyword pass | Quality | Avg latency |
| --- | --- | --- | --- |
| `langgraph` | `17/19` | `97.9` | `273.6 ms` |
| `python_functions` | `16/19` | `96.2` | `160.1 ms` |
| `llamaindex` | `16/19` | `96.8` | `409.8 ms` |
| `specialist_supervisor` | `16/19` | `96.8` | `203.9 ms` |

Leitura:
- `langgraph` foi o melhor caminho público desta rodada
- `python_functions` segue o mais leve
- `specialist_supervisor` ficou muito rápido na mediana, mas ainda mostrou cauda em alguns casos públicos
- `llamaindex` melhorou estruturalmente, mas ainda precisa matar um outlier público sério

### Protected

| Stack | Keyword pass | Quality | Avg latency |
| --- | --- | --- | --- |
| `langgraph` | `3/4` | `95.0` | `275.4 ms` |
| `python_functions` | `3/4` | `95.0` | `297.7 ms` |
| `llamaindex` | `3/4` | `95.0` | `289.3 ms` |
| `specialist_supervisor` | `4/4` | `100.0` | `189.3 ms` |

Leitura:
- o `specialist_supervisor` foi o único a fechar `protected` perfeito
- os outros três ainda falharam no mesmo follow-up protegido

### Restricted

Todos os caminhos fecharam `restricted` em `100.0`.

Leitura:
- policy e retrieval restrito continuam fortes e estáveis
- não apareceu regressão de deny/no-match nesta rodada

## Main Residuals

### Shared residual

`protected_structured_followup`
- `langgraph`
- `python_functions`
- `llamaindex`

Sintoma:
- responderam com negação de permissão para um follow-up que deveria permanecer no escopo da conta vinculada

### Public residual cluster

`public_calendar_week`
- `python_functions`
- `llamaindex`
- `specialist_supervisor`

Sintomas:
- `python_functions`: clarificação desnecessária
- `llamaindex`: fallback de perfil público em vez de linha do tempo
- `specialist_supervisor`: fast path genérico demais

`public_bolsas_and_processes`
- todos os caminhos ficaram abaixo do rubric lexical completo
- a resposta ficou funcional, mas o wording não refletiu bem o vínculo entre `bolsas/descontos` e `processos`

### Pricing residual

`public_pricing_projection`
- `langgraph`
- `python_functions`
- `llamaindex`

Sintoma:
- a pergunta de simulação pública de custo ainda escapou para resposta fora do domínio ou boundary incorreto

## Operational Notes

- `python_functions` foi o caminho mais previsível: melhor `P95` e ausência de cauda longa problemática
- `llamaindex` teve a melhor mediana depois do `specialist_supervisor`, mas um único outlier público (`5601.0 ms`) ainda compromete a média
- `specialist_supervisor` continua muito forte, porém ainda precisa de mais proteção em `general_knowledge`/`public preflight`
- `langgraph` ficou muito competitivo e com qualidade alta, mas seu `P95` ainda é maior do que o ideal para casos públicos canônicos

## Ranking

### Melhor equilíbrio geral

1. `python_functions`
2. `langgraph`
3. `specialist_supervisor`
4. `llamaindex`

### Maior qualidade média

1. `langgraph` / `specialist_supervisor`
2. `llamaindex`
3. `python_functions`

### Menor latência média

1. `python_functions`
2. `specialist_supervisor`
3. `langgraph`
4. `llamaindex`

## Recommended Next Steps

1. Corrigir o follow-up protegido compartilhado em `langgraph`, `python_functions` e `llamaindex`
2. Fechar `public_calendar_week` com lane pública determinística nos três caminhos residuais
3. Ajustar `public_pricing_projection` para não cair em boundary ou answer lane errados
4. Refinar `public_bolsas_and_processes` para incluir explicitamente a conexão entre bolsas/descontos e os processos comparados
5. Rerodar uma bateria `30Q` inédita depois dessas correções para confirmar se o cluster público foi eliminado
