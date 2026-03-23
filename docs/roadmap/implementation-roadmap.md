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

## 5. Fase 3 - FAQ pública e calendário

Objetivos:

- pipeline de ingestão documental;
- retrieval híbrido;
- respostas com citações;
- calendário escolar como serviço estruturado.

Entregáveis:

- FAQ pública funcional;
- calendário público e autenticado;
- evals iniciais.

## 6. Fase 4 - Acadêmico

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

## 7. Fase 5 - Financeiro

Objetivos:

- implementar `finance-service`;
- contratos, mensalidades, pagamentos, bolsas;
- fluxo protegido.

Entregáveis:

- resumo financeiro;
- detalhes de cobrança autorizados;
- trilha de auditoria reforçada.

## 8. Fase 6 - Operação e handoff

Objetivos:

- tickets;
- handoff humano;
- fila de revisão;
- feedback.

Entregáveis:

- painel operacional;
- fluxo de escalonamento;
- métricas de atendimento.

## 9. Fase 7 - Hardening

Objetivos:

- testes adversariais;
- revisão de LGPD;
- backup/restore;
- carga e resiliência;
- observabilidade completa.

Entregáveis:

- baseline de segurança;
- baseline de performance;
- gates mínimos de release.

## 10. Fase 8 - Kubernetes local

Objetivos:

- portar stack para `k3d` ou `kind`;
- validar manifests e operação local mais próxima de produção.

Entregáveis:

- ambiente alternativo em Kubernetes;
- documentação de operação local avançada.

## 11. Roadmap por sprints sugerido

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

- Keycloak + vínculo Telegram
- OPA + RLS base

### Sprint 4

- ingestão documental
- FAQ pública

### Sprint 5

- calendário
- observabilidade v1

### Sprint 6

- academic-service
- tools acadêmicas

### Sprint 7

- finance-service
- tools financeiras

### Sprint 8

- handoff humano
- painel operacional

### Sprint 9

- evals
- testes adversariais
- hardening

