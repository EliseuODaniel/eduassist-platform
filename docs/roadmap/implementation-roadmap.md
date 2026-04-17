# Roadmap de Implementação

## 1. Estratégia geral

O projeto será construído em fases, com marcos claros e validação contínua. A ordem prioriza fundação técnica, segurança, dados e só então capacidades conversacionais mais profundas.

## 1.1 Programa prioritário atual - Modernização do entendimento do turno

O programa prioritário atual do EduAssist é substituir a expansão incremental de heurísticas locais por um desenho canônico de:

- `semantic router` compartilhado;
- contrato estruturado de turno (`TurnFrame`);
- memória curta explícita para follow-up (`FocusFrame`);
- adapters de execução por stack;
- regressão cross-stack obrigatória.

### Resultado esperado

- a mesma pergunta, sob a mesma autenticação, deve convergir para a mesma `capability` final nas quatro stacks;
- perguntas públicas fortes não podem cair em domínio protegido por causa do estado autenticado;
- follow-ups curtos como “e que horas fecha?” ou “qual o próximo vencimento?” devem herdar contexto só quando a pergunta atual for realmente elíptica;
- `scope_boundary` e `safe_fallback` deixam de ser mecanismos de compensação para perguntas que o sistema deveria entender.

### Arquitetura de rollout

O rollout deve seguir esta ordem:

1. baseline e dataset de regressão compartilhados;
2. ontologia canônica de `capabilities`;
3. `TurnFrame` compartilhado;
4. geração de candidatos `top-k`;
5. classificador estruturado;
6. adapter `python_functions`;
7. adapter `langgraph`;
8. adapter `llamaindex`;
9. adapter `specialist_supervisor`;
10. remoção controlada das heurísticas legadas.

### Fases detalhadas do programa

#### Fase A - Baseline e regressão

- consolidar dataset de perguntas reais e adversariais;
- marcar `capability`, `scope`, `access_tier` e comportamento esperado;
- tornar a regressão cross-stack um gate de mudança arquitetural.

#### Fase B - Ontologia canônica

- consolidar `intent_registry`, lanes públicas, sinais de kernel e `semantic-ingress` em um único catálogo;
- publicar aliases, exemplos positivos e negativos por `capability`.

#### Fase C - Contrato estruturado

- criar `TurnFrame` compartilhado;
- criar `FocusFrame` com TTL explícito;
- expor ambos em traces, debug footer e avaliação.

#### Fase D - Candidate generation

- promover `candidate_builder` e `candidate_chooser` para a camada de roteamento;
- gerar candidatos por ontologia, auth, memória curta e sinais do turno;
- reduzir o espaço de decisão da LLM antes da classificação.

#### Fase E - Classificador semântico

- usar LLM rápida com saída estrita em schema;
- classificar apenas, sem compor resposta final;
- cair em `clarify` ou `scope_boundary` só com baixa confiança real.

#### Fase F - Adapter `python_functions`

- mapear `TurnFrame.capability` para handlers tipados;
- manter a stack como referência de execução determinística e baixa latência.

#### Fase G - Adapter `langgraph`

- criar subgrafo `semantic_router`;
- usar edges condicionais e estado explícito para follow-up;
- reduzir heurísticas locais no workflow.

#### Fase H - Adapter `llamaindex`

- usar o `TurnFrame` para escolher o conjunto pequeno de query engines elegíveis;
- deixar a stack explorar melhor routing documental e síntese por fonte.

#### Fase I - Adapter `specialist_supervisor`

- reservar o orçamento premium para ambiguidade real, multi-intent, repair e composição rica;
- evitar gastar supervisor/specialists em perguntas cuja `capability` já ficou clara no núcleo compartilhado.

#### Fase J - Desligamento das heurísticas legadas

- manter só `policy`, `auth`, `precedence`, safety e rendering como regras duras;
- remover gradualmente classificações semânticas duplicadas e drift local.

### Critérios de aceite do programa

- `capability` correta nas quatro stacks para o dataset compartilhado;
- ganho consistente em follow-ups curtos;
- redução de falsos `scope_boundary`;
- redução de falsos `safe_fallback`;
- redução de divergência entre stack autenticada e pública;
- manutenção do budget/latência dentro dos limites atuais por stack.

### Fatiamento sugerido por PR

1. `capability registry + TurnFrame`
2. `FocusFrame + carryover policy`
3. `candidate generation`
4. `structured classifier`
5. `python_functions adapter`
6. `langgraph adapter`
7. `llamaindex adapter`
8. `specialist adapter`
9. `legacy heuristic cleanup`

## 1.2 Programa complementar atual - Eficiência de contexto local com Gemma

O baseline local com `Gemma 4 E4B` não deve evoluir por expansão cega de `ctx-size`. O ganho de ROI mais forte vem de usar melhor o contexto disponível com medição explícita, packing melhor, memória curta mais forte e retrieval calibrado por capability.

### Resultado esperado

- mais groundedness e menos truncamento silencioso;
- melhor aproveitamento do `Gemma` local sem sacrificar latência ou estabilidade;
- follow-ups mais robustos sem depender de histórico bruto longo;
- base técnica preparada para, só depois, testar contexto maior ou compressão de KV cache.

### Ordem de rollout

1. telemetria de contexto e truncamento;
2. evidence packing orientado a budget de tokens;
3. memória curta e episódica explícita;
4. tuning de retrieval e rerank por capability;
5. composição grounded estruturada;
6. aumento gradual de `ctx-size` por rota;
7. reavaliação de `TurboQuant` apenas se os passos anteriores saturarem.

### Fase K - Telemetria de contexto

- registrar `prompt_tokens`, `completion_tokens`, `history_tokens`, `evidence_tokens` e truncamento por stack;
- distinguir custo de histórico, evidência, tools e polish final;
- expor no trace quando o budget de contexto foi insuficiente para a resposta ideal.

Status atual:

- implementada no `turn_router` e no `public_answer_composer`;
- o trace agora registra estimativas de tokens para `prompt`, `instructions`, `request`, `history`, `evidence`, `draft` e `candidates`;
- truncamento de histórico e evidência já é sinalizado como evento operacional explícito.

### Fase L - Evidence packing

- trocar limites implícitos por budget explícito de tokens;
- deduplicar trechos por documento e fundir chunks adjacentes;
- priorizar sentenças answer-bearing e evidências com maior valor para a pergunta atual.

Status atual:

- baseline compartilhado implementado no pacote `semantic-ingress`;
- `turn_router` usa budget de tokens para histórico e payload de candidatas;
- `public_answer_composer` usa budget de tokens para histórico curto e evidência pública grounded;
- os adapters locais de `langgraph`, `python_functions` e `llamaindex` já usam o mesmo baseline de packing para histórico, evidência e eventos estruturados;
- defaults atuais do baseline:
  - `semantic_router_history_budget_tokens=180`
  - `semantic_router_candidate_budget_tokens=220`
  - `grounded_public_history_budget_tokens=180`
  - `grounded_public_evidence_budget_tokens=320`
  - `stack_local_llm_history_budget_tokens=220`
  - `stack_local_llm_evidence_budget_tokens=360`
  - `stack_local_llm_calendar_budget_tokens=140`

### Fase M - Memória curta e episódica

- consolidar memória curta compartilhada por conversa com entidade ativa, capability ativa, ator/aluno ativo, fatos grounded recentes e slots pendentes;
- usar resumo episódico curto em vez de histórico bruto sempre que possível;
- manter fronteira explícita entre memória pública, protegida e operacional.

Status atual:

- `FocusFrame` agora absorve sinais episódicos vindos de `recent_tool_calls`/`orchestration.trace`;
- o semantic router já preserva `active_entity`, `active_attribute`, `active_actor`, `requested_channel`, `time_reference` e `pending_question_type`;
- follow-ups curtos agora podem herdar capability e slots recentes com mais precisão, sem depender apenas de match lexical do último turno.

### Fase N - Retrieval e rerank por capability

- calibrar `top-k`, query variants e rerank por família de capability;
- separar melhor fato direto, síntese documental e busca multi-documento;
- medir `answerable@k`, groundedness e latência por capability, não apenas score agregado.

Estado atual:

- a base compartilhada já possui `RetrievalExecutionPolicy` por capability;
- `python_functions`, `langgraph`, `llamaindex` e os kernels públicos já consomem essa política antes do retrieval híbrido;
- o baseline já passou a registrar nos traces a policy escolhida e o resultado efetivo da busca, por engine e por capability;
- o retrieval híbrido agora combina o score original com `late interaction` e `cross-encoder` multilíngue, elevando o baseline de precisão antes da composição grounded;
- o próximo passo desta fase deixa de ser "introduzir capability-aware retrieval" e passa a ser calibração fina por família, com métricas reais de `answerable@k` e latência.

### Estado dos débitos arquiteturais antigos

- `runtime_core.py` como god module: resolvido por decomposição estrutural, com constantes e expressões extraídas para `runtime_core_constants.py` e orçamento de módulo reforçado em teste;
- `cross-encoder reranker`: resolvido no baseline atual do retrieval híbrido;
- `tail-based sampling OTEL`: já estava resolvido na infraestrutura Compose;
- `SPIFFE/SPIRE`: resolvido no nível da aplicação por bridge `SPIFFE-ready`; rollout completo de `SPIRE` continua como maturidade operacional opcional.

## 1.3 Programa complementar atual - Benchmark A/B local de modelos

O projeto agora mantém um segundo profile local de LLM para comparação controlada com o baseline:

- baseline: `gemma4e4b_local`
- experimento: `qwen3_4b_instruct_local`

Princípios:

- mesma stack para comparação;
- mesmo dataset;
- mesma política de auth, retrieval, grounding e rendering;
- sem troca silenciosa do default do repositório.

Sequência recomendada:

1. subir `specialist_supervisor` com `gemma4e4b_local`;
2. rodar dataset A/B e salvar artefatos;
3. subir `specialist_supervisor` com `qwen3_4b_instruct_local`;
4. rodar exatamente o mesmo dataset;
5. comparar qualidade, personalização, grounding, latência e análise humana;
6. só então decidir se o experimento merece piloto maior.

Status da primeira rodada (`2026-04-17`):

- implementação concluída com o profile `qwen3_4b_instruct_local` em `llama.cpp`;
- A/B executado no `specialist_supervisor` com o mesmo dataset e o mesmo harness;
- a primeira passada favoreceu `Qwen` em estabilidade e latência, mas revelou resíduos arquiteturais acima da troca de modelo;
- depois da wave de correções e do `answer surface refiner`, `gemma4e4b_local_postfix` fechou em `15/15`, `keyword_pass 15/15` e `quality 100.0`;
- decisão: manter `Gemma` como baseline, preservar `Qwen` como feature flag experimental e tratar o A/B como ferramenta contínua de diagnóstico.

### Fase O - Composição grounded mais forte

- evoluir a composição final para um `AnswerFrame` com `direct_answer`, `supported_claims`, `omitted_context` e `uncertainty`;
- deixar a LLM adaptar a resposta só em cima de evidência auditável;
- preservar respostas determinísticas em domínios sensíveis.

Status atual:

- a primeira etapa desta fase foi implementada no `specialist_supervisor` via `answer surface refiner` validado e depois promovida ao pós-processamento compartilhado das stacks non-specialist;
- respostas elegíveis, inclusive determinísticas, já passam por verbalização final com fallback preservado tanto no `specialist` quanto em `langgraph`, `python_functions` e `llamaindex`;
- o próximo avanço dessa fase deixa de ser "ligar a LLM no final" e passa a ser enriquecer o contrato explícito do refino com campos mais próximos de um `AnswerFrame`.

### Fase P - Contexto maior, com perfilamento

- subir `ctx-size` de forma gradual e reversível, começando por rotas documentais e multi-documento;
- testar `8K -> 12K -> 16K` antes de qualquer salto maior;
- só considerar técnicas como `TurboQuant` depois que packing, memória e retrieval estiverem maduros.

### Critérios de aceite do programa complementar

- ganho mensurável de groundedness e answerability sem regressão material de latência;
- menor taxa de truncamento silencioso;
- melhora de follow-up curto sem ampliar falsos cruzamentos de domínio;
- evidência melhor compactada antes de qualquer aumento agressivo de contexto.

## 2. Fase 0 - Fundação

Objetivos:

- corrigir `Docker Desktop/WSL2`;
- inicializar monorepo;
- definir ADRs principais;
- definir classificação de dados;
- definir matriz de acesso;
- fechar threat model inicial.

Entregáveis:

- repositório novo;
- documentação base;
- decisões arquiteturais aprovadas.

## 3. Fase 1 - Infraestrutura base

Objetivos:

- subir stack mínima em Compose;
- configurar Postgres, Redis, MinIO, Keycloak, OPA;
- bootstrapar backend e painel.

Entregáveis:

- `compose:core` funcional;
- healthchecks;
- logging básico;
- pipeline local reproduzível.

## 4. Fase 2 - Dados e identidade

Objetivos:

- modelar schemas;
- criar gerador de mock data;
- carregar base inicial;
- implementar fluxo de login e vínculo.

Entregáveis:

- seed determinística;
- vínculo Telegram-usuário;
- roles e policies básicas.

## 5. Fase 3 - Inteligência documental e retrieval

Objetivos:

- pipeline de parsing com `Docling`;
- pipeline de ingestão documental;
- `Qdrant` na stack;
- retrieval híbrido com dense + sparse + reranking;
- respostas com citações;
- baseline de avaliação de retrieval.

Entregáveis:

- corpus institucional processado;
- índices híbridos prontos;
- evals iniciais de groundedness e retrieval.

## 6. Fase 4 - FAQ pública e calendário

Objetivos:

- FAQ institucional pública sobre a base documental;
- calendário escolar como serviço estruturado;
- integração Telegram + retrieval.

Entregáveis:

- FAQ pública funcional;
- calendário público e autenticado;
- citações e respostas auditáveis.

## 7. Fase 5 - Acadêmico

Objetivos:

- implementar `academic-service`;
- tools acadêmicas;
- policy fina por perfil;
- fluxo no Telegram.

Entregáveis:

- consulta de notas;
- consulta de frequência;
- horários e avaliações;
- negação correta para acessos indevidos.

## 8. Fase 6 - Financeiro

Objetivos:

- implementar `finance-service`;
- contratos, mensalidades, pagamentos, bolsas;
- fluxo protegido.

Entregáveis:

- resumo financeiro;
- detalhes de cobrança autorizados;
- trilha de auditoria reforçada.

## 9. Fase 7 - Operação e handoff

Objetivos:

- tickets;
- handoff humano;
- fila de revisão;
- feedback.

Entregáveis:

- painel operacional;
- fluxo de escalonamento;
- métricas de atendimento.

## 10. Fase 8 - Retrieval avançado e hardening

Objetivos:

- habilitar `late interaction` e multivectors nos corpora de maior valor;
- pilotar `GraphRAG` para perguntas globais, locais e multi-documento complexas;
- testes adversariais;
- revisão de LGPD;
- backup/restore;
- carga e resiliência;
- observabilidade completa.

Entregáveis:

- baseline comparativa entre retrieval híbrido e `GraphRAG`;
- baseline de segurança;
- baseline de performance;
- gates mínimos de release.

Estado atual:

- o programa prioritário de modernização do entendimento do turno já possui implementação ativa no código:
  - ontologia canônica inicial de `capabilities`;
  - `TurnFrame` e `FocusFrame`;
  - candidate generation `top-k`;
  - classificador estruturado por provider;
  - adapters integrados em `python_functions`, `langgraph`, `llamaindex` e `specialist_supervisor`;
  - gate unitário cross-stack para consistência de `capability`.
- a fase atual do programa deixa de ser “criar a fundação” e passa a ser “expandir cobertura de capabilities e mover regressões E2E para cima do novo contrato”.
- depois do fechamento do hardening amplo em `2026-04-16`, o próximo passo do roadmap deixa de ser qualidade semântica básica e passa a ser resiliência operacional dos caminhos públicos pesados sob concorrência, especialmente em `langgraph`, `python_functions` e `llamaindex`.

- os gates minimos de release ja existem em `make release-readiness`;
- o benchmark seletivo de `GraphRAG` ja possui trilha experimental pronta;
- o fechamento estrito dessa fase ainda depende de executar o benchmark completo com provider valido, remoto ou local compativel.

## 11. Fase 9 - Kubernetes local

Objetivos:

- portar stack para `k3d` ou `kind`;
- validar manifests e operação local mais próxima de produção.

Entregáveis:

- ambiente alternativo em Kubernetes;
- documentação de operação local avançada.

## 12. Roadmap por sprints sugerido

### Sprint 0

- bootstrap documental
- correção do runtime local

### Sprint 1

- compose base
- healthchecks
- skeleton dos apps

### Sprint 2

- schemas e migrações iniciais
- mock generator v1

### Sprint 3

- qdrant na stack
- pipeline Docling v1

### Sprint 4

- Keycloak + vínculo Telegram
- OPA + RLS base

### Sprint 5

- ingestão documental
- retrieval híbrido
- FAQ pública

### Sprint 6

- calendário
- observabilidade v1

### Sprint 7

- academic-service
- tools acadêmicas

### Sprint 8

- finance-service
- tools financeiras

### Sprint 9

- handoff humano
- painel operacional

### Sprint 10

- late interaction
- piloto GraphRAG
- evals
- testes adversariais
- hardening
