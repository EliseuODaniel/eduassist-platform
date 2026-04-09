# Relatório Executivo Final da Rodada 50Q

## 1. Escopo da rodada

- bateria: `50Q`
- data-base do dataset: `2026-04-02`
- dataset: [retrieval_50q_probe_cases.generated.20260402.json](/home/edann/projects/eduassist-platform/tests/evals/datasets/retrieval_50q_probe_cases.generated.20260402.json)
- relatório bruto: [retrieval-50q-cross-path-report-20260402.md](/home/edann/projects/eduassist-platform/docs/architecture/retrieval-50q-cross-path-report-20260402.md)
- relatório bruto JSON: [retrieval-50q-cross-path-report-20260402.json](/home/edann/projects/eduassist-platform/docs/architecture/retrieval-50q-cross-path-report-20260402.json)

Composição do benchmark:
- `50` perguntas inéditas
- `47` categorias
- `29` casos públicos
- `12` casos protegidos
- `9` casos restritos
- `0` overlap exato com datasets anteriores

Esta rodada deve ser tratada como a evidência principal do fechamento do projeto. Ela é mais ampla e mais discriminativa do que as baterias `26Q`, `28Q` e `30Q`, e por isso revela melhor os resíduos arquiteturais ainda presentes.

## 2. Resumo executivo

Os quatro caminhos ativos concluíram `50/50` casos sem falhas de runtime, o que confirma maturidade operacional do baseline compartilhado. A diferença entre eles apareceu principalmente em `keyword pass`, qualidade média e latência de cauda.

O `Specialist Supervisor` obteve a maior qualidade média global (`91,5`), mas pagou o maior custo de latência, com média de `3524,9 ms` e `P95` de `17360,4 ms`, fortemente influenciado por cauda longa e timeouts do pilot remoto em perguntas públicas complexas. O `Python puro + functions` manteve o melhor perfil operacional, com média de `325,4 ms` e `P95` de `364,0 ms`, além de empatar no maior `keyword pass` global (`36/50`). O `LangGraph` ficou com o melhor equilíbrio geral entre qualidade, governança do fluxo e latência, alcançando `91,1` de qualidade média, `35/50` em `keyword pass` e `719,4 ms` de média. O `LlamaIndex` empatou em qualidade com o `LangGraph` (`91,1`), consolidando-se como caminho retrieval-first competitivo, porém com cauda pública mais pesada (`P95` de `7566,0 ms`).

O ponto mais importante da rodada final não é apenas o ranking. A `50Q` mostrou que o sistema amadureceu a ponto de deslocar o problema principal de “falha estrutural” para “gaps compartilhados de policy, roteamento e fronteira entre público, protegido e restrito”.

## 3. Resultado global

| Caminho | OK | Keyword pass | Qualidade média | Latência média | Mediana | P95 | Máximo |
| --- | --- | --- | --- | --- | --- | --- | --- |
| LangGraph | 50/50 | 35/50 | 91,1 | 719,4 ms | 257,8 ms | 3034,7 ms | 4289,5 ms |
| Python puro + functions | 50/50 | 36/50 | 90,5 | 325,4 ms | 212,8 ms | 364,0 ms | 4915,8 ms |
| LlamaIndex | 50/50 | 35/50 | 91,1 | 1222,8 ms | 262,0 ms | 7566,0 ms | 13175,4 ms |
| Specialist Supervisor | 50/50 | 36/50 | 91,5 | 3524,9 ms | 195,0 ms | 17360,4 ms | 18018,5 ms |

## 4. Resultado por slice

### 4.1 Public

| Caminho | Keyword pass | Qualidade média | Latência média | Leitura |
| --- | --- | --- | --- | --- |
| LangGraph | 20/29 | 93,4 | 981,4 ms | melhor equilíbrio público entre qualidade e governança |
| Python puro + functions | 21/29 | 92,4 | 361,3 ms | melhor operação pública e maior `keyword pass` do slice |
| LlamaIndex | 20/29 | 93,4 | 1887,9 ms | competitivo em qualidade, ainda caro em cauda |
| Specialist Supervisor | 20/29 | 93,8 | 5726,6 ms | maior qualidade pública, mas latência inviável como default |

### 4.2 Protected

| Caminho | Keyword pass | Qualidade média | Latência média | Leitura |
| --- | --- | --- | --- | --- |
| LangGraph | 9/12 | 95,0 | 285,2 ms | robusto, mas ainda com gap em agregados protegidos |
| Python puro + functions | 9/12 | 95,0 | 289,9 ms | eficiente, porém com o mesmo gap de follow-up agregado |
| LlamaIndex | 9/12 | 95,0 | 309,1 ms | competitivo e estável no protegido |
| Specialist Supervisor | 10/12 | 95,7 | 694,7 ms | melhor protegido da rodada, com pequena vantagem real |

### 4.3 Restricted

| Caminho | Keyword pass | Qualidade média | Latência média | Leitura |
| --- | --- | --- | --- | --- |
| LangGraph | 6/9 | 78,3 | 454,0 ms | seguro, mas ainda incompleto para novos casos internos |
| Python puro + functions | 6/9 | 78,3 | 256,7 ms | mais leve, porém com o mesmo gap de policy |
| LlamaIndex | 6/9 | 78,3 | 298,0 ms | retrieval consistente, mas não resolve a policy sozinho |
| Specialist Supervisor | 6/9 | 78,3 | 204,2 ms | melhor latência restrita, mesmo gap funcional compartilhado |

## 5. O que a 50Q revelou

### 5.1 Forças consolidadas

- os quatro caminhos estão operacionalmente estáveis: `50/50` casos concluídos;
- a arquitetura compartilhada de identidade, policy, tools e retrieval continua sendo o principal estabilizador do sistema;
- o `Python puro + functions` confirmou o menor custo operacional;
- o `LangGraph` confirmou o melhor equilíbrio arquitetural;
- o `LlamaIndex` mostrou que a estratégia retrieval-first evoluiu de forma real;
- o `Specialist Supervisor` continuou forte em qualidade e protegido.

### 5.2 Gaps compartilhados mais importantes

As categorias abaixo falharam em `todos os quatro caminhos`:
- `protected_admin_finance_combo`
- `protected_structured_upcoming_assessments`
- `restricted_doc_negative_exchange_program`
- `restricted_doc_positive_scope_protocol_variant`
- `restricted_doc_positive_teacher_feedback`

Isso indica que o próximo backlog não é “trocar framework”. O backlog é:
- melhorar requests agregados protegidos sem clarificação excessiva;
- separar melhor no restrito o que é `deny`, `authorized no-match` e `authorized positive retrieval`;
- corrigir policy e roteamento para documentos internos com escopo autenticado variante.

### 5.3 Gaps públicos mais recorrentes

As categorias públicas com maior recorrência de falha foram:
- `public_bolsas_and_processes`
- `public_calendar_week`
- `public_health_emergency_bundle`
- `public_inclusion_accessibility`
- `public_outings_authorizations`
- `public_pricing_projection`
- `public_transport_uniform_bundle`

Esses casos têm uma característica comum: exigem resposta documental mais integrada, sem virar abertura de workflow nem cair em lane excessivamente genérica.

## 6. Latência e comportamento operacional

### 6.1 Leitura correta da latência

O caminho mais eficiente segue sendo o `Python puro + functions`. Ele não venceu em qualidade média, mas manteve a melhor relação entre previsibilidade, throughput e custo de cauda.

O `Specialist Supervisor` teve boa mediana (`195,0 ms`), mas péssimo `P95` e `máximo`. Isso significa que o problema do caminho não é o tempo basal; é a cauda longa. Durante a rodada apareceram `ReadTimeouts` do pilot remoto, o que ajuda a explicar os outliers públicos.

O `LlamaIndex` ficou no meio do caminho: qualidade competitiva, mas com uma cauda pública ainda alta demais para ser default universal.

### 6.2 Maiores outliers por caminho

- `LangGraph`: `public_integral_study_support`, `public_outings_authorizations`, `public_known_unknown_library_books`, `public_year_three_phases`
- `Python puro + functions`: outlier principal em `public_outings_authorizations`
- `LlamaIndex`: `public_year_three_phases`, `public_inclusion_accessibility`, `public_health_emergency_bundle`, `public_calendar_week`
- `Specialist Supervisor`: `public_governance_protocol`, `public_health_emergency_bundle`, `public_inclusion_accessibility`, `public_process_compare`, `public_visibility_boundary`

## 7. Leitura final por caminho

### LangGraph

Melhor leitura atual:
- caminho mais equilibrado entre qualidade, governança de fluxo e latência;
- boa escolha quando a prioridade é observabilidade do processo e leitura arquitetural clara.

### Python puro + functions

Melhor leitura atual:
- melhor caminho operacional do sistema;
- mais rápido, mais previsível e suficientemente forte em qualidade para produção.

### LlamaIndex

Melhor leitura atual:
- caminho retrieval-first mais sofisticado do projeto;
- competitivo em qualidade, mas ainda penalizado por cauda pública e por alguns resíduos de roteamento documental.

### Specialist Supervisor

Melhor leitura atual:
- melhor qualidade média da rodada;
- melhor desempenho protegido;
- ainda caro em latência de cauda, especialmente quando o pilot remoto entra em timeout ou quando o caso público escapa dos fast paths.

## 8. Implicações para o TCC

A bateria `50Q` deve substituir a `28Q` como benchmark principal do texto final por três razões:

1. é mais ampla;
2. é mais discriminativa;
3. revela não apenas forças, mas também o backlog residual do sistema.

A narrativa correta para o TCC não é “a plataforma ficou perfeita”. A narrativa correta é:

- os quatro caminhos amadureceram o suficiente para operar sem falhas de runtime;
- a comparação tornou-se arquiteturalmente justa e metodologicamente útil;
- o benchmark final revelou que os principais problemas restantes são compartilhados;
- portanto, a qualidade final depende tanto do framework quanto da engenharia comum de produto, segurança, retrieval e policy.

## 9. Conclusão executiva

O fechamento do projeto não aponta um vencedor absoluto. Ele aponta um conjunto de leituras complementares:

- `Python puro + functions` é a melhor escolha operacional;
- `LangGraph` é a melhor escolha de equilíbrio global;
- `Specialist Supervisor` é a melhor escolha quando a prioridade é qualidade premium e protegido, aceitando maior custo;
- `LlamaIndex` é o caminho mais promissor quando o eixo dominante é retrieval documental sofisticado.

O dado metodológico mais forte da `50Q` é outro: a comparação entre caminhos só se torna intelectualmente honesta quando todos compartilham a mesma verdade de domínio, a mesma política de acesso, o mesmo baseline de retrieval e o mesmo regime de avaliação. É essa superfície comum que dá validade ao experimento.
