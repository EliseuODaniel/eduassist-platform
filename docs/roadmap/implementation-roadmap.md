# Roadmap de Implementação

## 1. Estratégia geral

O projeto será construído em fases, com marcos claros e validação contínua. A ordem prioriza fundação técnica, segurança, dados e só então capacidades conversacionais mais profundas.

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
