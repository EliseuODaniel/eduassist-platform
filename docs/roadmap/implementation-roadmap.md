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
