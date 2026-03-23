# Operação Local e Estratégia de Desenvolvimento

## 1. Objetivo

Definir como o sistema deve ser executado localmente durante desenvolvimento e testes.

## 2. Perfil da máquina observado

Durante o planejamento, o ambiente local reportou:

- `Ubuntu 24.04.3 LTS`
- `WSL2`
- `32 vCPUs`
- `~15 GiB` de RAM visível ao Linux
- `NVIDIA RTX 4070 Laptop GPU` com `8 GiB` de VRAM
- `~893 GiB` livres em disco

Observação:

- o usuário informou `32 GiB` de RAM na máquina;
- o Linux no WSL estava vendo aproximadamente `15 GiB`;
- portanto, o planejamento local deve caber no orçamento efetivamente visível no ambiente Linux.

## 3. Estado atual do runtime

Estado validado:

- `git` e `gh` funcionais;
- `docker` e `docker compose` funcionais no ambiente atual;
- bootstrap local validado com build e subida completa da stack base;
- o runtime foi considerado estável o suficiente para seguir para as próximas fases.

Observação:

- a etapa de bootstrap já foi executada e testada;
- `Qdrant` ja foi integrado a stack local como base da fase de retrieval;
- a fundacao documental ja sincroniza corpus mockado para `MinIO`, `Postgres` e `Qdrant`;
- o backend padrao local de parsing documental esta em `markdown`, com interface preparada para um backend `Docling` opcional nas fases seguintes.

## 4. Estratégia de ambientes

### `compose:core`

Serviços:

- postgres
- qdrant
- redis
- minio
- keycloak
- opa
- api-core
- telegram-gateway
- ai-orchestrator
- worker
- admin-web

Uso:

- desenvolvimento diário;
- testes funcionais essenciais.

Status atual:

- bootstrap implementado em [compose.yaml](/home/edann/projects/eduassist-platform/infra/compose/compose.yaml);
- os serviços já possuem esqueletos executáveis e healthchecks básicos;
- `Qdrant` já foi adicionado ao Compose e validado junto do `ai-orchestrator`;
- o `ai-orchestrator` já possui preview de grafo, capacidades e contratos de tools;
- o `api-core` já possui base relacional inicial, migracao Alembic e seed foundation;
- o `api-core` já expõe resolução de identidade, checagem de policy via `OPA` e consultas protegidas com auditoria básica;
- o `Keycloak` já importa automaticamente o realm `eduassist` com usuários mockados;
- o `api-core` já valida bearer tokens reais do `Keycloak` e expõe challenge de vínculo com Telegram;
- o `telegram-gateway` já processa `/start link_<codigo>` e conclui o vínculo pelo endpoint interno;
- o `api-core` já expõe `GET /v1/calendar/public` e `GET /v1/internal/identity/context`;
- o `worker` já faz sync idempotente do corpus documental mockado e reconstrói a coleção `school_documents` no `Qdrant`;
- o `ai-orchestrator` já expõe `retrieval/status` e `retrieval/search` com fusão de `Qdrant` e `PostgreSQL FTS`;
- o `ai-orchestrator` já expõe `POST /v1/messages/respond` para FAQ pública, calendário público e negações seguras;
- o `telegram-gateway` já encaminha mensagens públicas ao `ai-orchestrator` e responde `/help`, FAQ e calendário pelo webhook;
- o fluxo protegido do Telegram já responde resumo acadêmico com filtros por disciplina e bimestre, resumo financeiro com filtros por status e panorama consolidado para responsáveis, além de grade docente por turmas, disciplinas e horário para contas vinculadas;
- o `admin-web` já expõe login real via `Keycloak` com OIDC + PKCE, leitura de sessão autenticada do `api-core` e emissão de challenge de vínculo em `/api/telegram-link/challenge`;
- o `api-core` já expõe `GET /v1/operations/overview` com visão pessoal para responsáveis, alunos e professores, e visão global para secretaria, financeiro, coordenação e administração, incluindo agregados operacionais de handoff no escopo global;
- o `admin-web` roda em modo estável de produção dentro do Compose e a home autenticada já mostra métricas operacionais, feed de auditoria, feed de decisões de acesso e um painel de saúde da fila humana por setor, operador e exceções críticas, com links diretos para drill-down filtrado e uma leitura temporal de volume/tempo dos handoffs;
- o `api-core` já expõe `GET /v1/support/handoffs`, `GET /v1/support/handoffs/{handoff_id}` e `PATCH /v1/support/handoffs/{handoff_id}` para operação humana autenticada, com prioridade, SLA mockado e atribuição;
- o `api-core` já expõe `POST /v1/internal/support/handoffs` para criação interna de tickets/handoffs por serviços confiáveis;
- o `ai-orchestrator` já cria handoffs reais quando a classificação cai em `support` e a política do fluxo permite encaminhamento humano;
- o `admin-web` já exibe a fila de handoffs com filtros por status, fila, atribuição, SLA e texto livre, abre o detalhe completo da conversa e permite registrar nota operacional, assumir atribuição, iniciar ou resolver tickets via sessão autenticada;
- `telegram_chat_id` em rotas protegidas do `api-core` e `POST /v1/messages/respond` no `ai-orchestrator` agora exigem `X-Internal-Api-Token`;
- observabilidade distribuida base já esta ativa no Compose, com tracing entre `telegram-gateway`, `ai-orchestrator` e `api-core`.

### `compose:observability`

Serviços:

- `otel-collector`
- `tempo`
- `loki`
- `promtail`
- `prometheus`
- `grafana`

Uso:

- tracing distribuido;
- metricas OTEL e consultas PromQL;
- consulta de traces por `trace_id`;
- debugging operacional do fluxo `telegram-gateway -> ai-orchestrator -> api-core`.

Status atual:

- `otel-collector`, `tempo`, `prometheus` e `grafana` já sobem no mesmo `compose.yaml`;
- `loki` e `promtail` completam a agregacao central de logs dos containers do Compose;
- os serviços Python instrumentados já exportam spans e metricas OTLP via `HTTP` para o collector;
- o `Tempo` já persiste traces e responde `GET /api/traces/{trace_id}` em `http://localhost:3200`;
- o `Prometheus` já responde em `http://localhost:9090` e raspa o endpoint de metricas do collector;
- o `Loki` já responde em `http://localhost:3100` e recebe logs dos containers via `Promtail`;
- o `Grafana` já sobe com datasources de `Tempo`, `Loki` e `Prometheus` provisionados em `http://localhost:3004`;
- o `Grafana` agora também provisiona os dashboards `EduAssist Tracing Overview` e `EduAssist Metrics Overview`;
- `X-Trace-Id` e `X-Span-Id` já são devolvidos nas respostas dos serviços Python instrumentados;
- a observabilidade local agora cobre traces, logs e metricas centralizadas.

### `compose:full`

Combina:

- `core + observability + tunnel helper`

## 5. Orçamento de recursos

Meta de memória:

- `core`: 6-8 GiB
- `observability`: +2-3 GiB
- `full`: 9-11 GiB

Isso preserva margem de segurança no ambiente atual.

## 6. Exposição do Telegram webhook

Opções:

- `Cloudflare Tunnel`
- `ngrok`

Recomendação inicial:

- usar o mais simples e estável no ambiente local;
- versionar instruções, não credenciais.

## 7. Kubernetes local

Uso posterior:

- `k3d` ou `kind`

Condição:

- somente após o stack Compose estar estável;
- não é requisito para a primeira entrega funcional.

## 8. Estrutura operacional desejada

- `Makefile` ou task runner único
- perfis de ambiente
- seed data reproduzível
- bootstrap de auth
- bootstrap de docs
- smoke tests

Status atual do bootstrap:

- `Makefile` criado em [Makefile](/home/edann/projects/eduassist-platform/Makefile)
- arquivo de ambiente base em [.env.example](/home/edann/projects/eduassist-platform/.env.example)
- Dockerfiles iniciais nos apps
- stack Compose pronta para validação local
- runtime validado após reinicialização e atualização do Docker Desktop
- fundação inicial de retrieval e orquestração agentica já implementada
- foundation transacional validada com migração e seed mockada
- identity and policy base validadas com smoke tests de responsável, aluno, professor e financeiro
- auth federada e vínculo Telegram validados com token real do `Keycloak` local
- corpus documental mockado validado com 4 documentos e 21 chunks indexados

## 9. Variáveis de ambiente previstas

- `DATABASE_URL`
- `REDIS_URL`
- `QDRANT_URL`
- `QDRANT_DOCUMENTS_COLLECTION`
- `MINIO_ENDPOINT`
- `KEYCLOAK_*`
- `OPA_URL`
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_WEBHOOK_SECRET`
- `LLM_PROVIDER`
- `OPENAI_API_KEY`
- `GOOGLE_API_KEY`
- `GRAPH_RAG_ENABLED`
- `DOCUMENT_PIPELINE_BACKEND`
- `DATABASE_URL_LOCAL`
- `FOUNDATION_SEED`
- `OTEL_ENABLED`
- `OTEL_SERVICE_NAMESPACE`
- `OTEL_EXPORTER_OTLP_ENDPOINT`
- `OTEL_PROMETHEUS_PORT`
- `OTEL_GRPC_PORT`
- `OTEL_HTTP_PORT`
- `PROMETHEUS_PORT`
- `TEMPO_PORT`
- `LOKI_PORT`
- `GRAFANA_PORT`

## 10. Critérios de pronto para desenvolvimento

- docker funcional no WSL;
- compose sobe stack mínima;
- banco recebe seed;
- keycloak sobe realm inicial;
- webhook local consegue ser exposto;
- logs e traces mínimos aparecem corretamente;
- respostas instrumentadas devolvem `X-Trace-Id` para drill-down.

## 11. Comandos úteis desta fase

- `make db-upgrade`
- `make db-seed-foundation`
- `make db-seed-auth-bindings`
- `make documents-sync`
- `make observability-up`
- `make observability-down`
- `make observability-logs`
- `make smoke-local`
- `make smoke-authz`
- `make smoke-adversarial`
- `make smoke-all`
- `GET /v1/foundation/summary` no `api-core`
- `GET /v1/identity/context?user_external_code=USR-TEACH-001`
- `GET /v1/internal/identity/context?telegram_chat_id=<chat_id>` com `X-Internal-Api-Token`
- `GET /v1/auth/session` com `Authorization: Bearer <token>`
- `GET /v1/operations/overview` com `Authorization: Bearer <token>`
- `GET /v1/support/handoffs` com `Authorization: Bearer <token>`
- `GET /v1/support/handoffs/{handoff_id}` com `Authorization: Bearer <token>`
- `PATCH /v1/support/handoffs/{handoff_id}` com `Authorization: Bearer <token>` para nota, atribuição e status
- `POST /v1/auth/telegram-link/challenges` com `Authorization: Bearer <token>`
- `GET /v1/calendar/public?date_from=2026-03-01&date_to=2026-04-30`
- `POST /webhooks/telegram` no `telegram-gateway` com `/start link_<codigo>`
- `POST /webhooks/telegram` no `telegram-gateway` com perguntas como `quais documentos sao exigidos para matricula?`
- `POST /webhooks/telegram` no `telegram-gateway` com `quero ver as notas do Lucas Oliveira`
- `POST /webhooks/telegram` no `telegram-gateway` com `quero ver notas de portugues da Ana Oliveira`
- `POST /webhooks/telegram` no `telegram-gateway` com `quero ver notas do 1o bimestre do Lucas Oliveira`
- `POST /webhooks/telegram` no `telegram-gateway` com `quero ver o financeiro da Ana Oliveira`
- `POST /webhooks/telegram` no `telegram-gateway` com `quero ver boletos em aberto`
- `POST /webhooks/telegram` no `telegram-gateway` com `quero ver faturas pagas do Lucas Oliveira`
- `POST /webhooks/telegram` no `telegram-gateway` com `qual meu horario e minhas turmas?`
- `POST /webhooks/telegram` no `telegram-gateway` com `quais sao minhas disciplinas?`
- `POST /webhooks/telegram` no `telegram-gateway` com `quero falar com um humano sobre a secretaria`
- `GET /auth/login` no `admin-web` para iniciar o fluxo OIDC com `Keycloak`
- `GET /` no `admin-web` com cookie `eduassist_access_token=<token>` para validar a visao operacional autenticada
- `GET /?handoff={handoff_id}` no `admin-web` com cookie `eduassist_access_token=<token>` para validar o detalhe da conversa
- `GET /?handoffStatus=queued&handoffSla=breached` no `admin-web` com cookie `eduassist_access_token=<token>` para validar os filtros operacionais da fila
- `PATCH /api/support-handoffs/{handoff_id}` no `admin-web` com cookie de sessão autenticada
- `POST /api/telegram-link/challenge` no `admin-web` com cookie de sessão autenticada
- `GET /v1/students/{student_id}/academic-summary?...`
- `GET /v1/students/{student_id}/financial-summary?...`
- `GET /v1/teachers/me/schedule?user_external_code=USR-TEACH-001`
- `POST /v1/authz/check`
- `GET /v1/retrieval/status` no `ai-orchestrator`
- `POST /v1/retrieval/search` no `ai-orchestrator`
- `POST /v1/messages/respond` no `ai-orchestrator` com `X-Internal-Api-Token`
- `GET /api/traces/{trace_id}` no `Tempo` em `http://localhost:3200`
- `GET /-/ready` no `Prometheus` em `http://localhost:9090`
- `GET /ready` no `Loki` em `http://localhost:3100`
- `GET /` no `Grafana` em `http://localhost:3004`
- dashboard provisionado: `EduAssist / EduAssist Tracing Overview` no `Grafana`
- dashboard provisionado: `EduAssist / EduAssist Metrics Overview` no `Grafana`

Observacao sobre o pipeline documental local:

- o corpus inicial versionado em [data/corpus/public](/home/edann/projects/eduassist-platform/data/corpus/public) e composto por documentos `Markdown` com frontmatter;
- o `worker` envia os arquivos fonte para `MinIO`, replica metadados e chunks no schema `documents` e reconstrói a coleção `school_documents` no `Qdrant`;
- o primeiro boot baixa o modelo multilíngue de embeddings do `FastEmbed`, o que torna a primeira sincronização mais lenta;
- por padrao, o parsing local usa o backend `markdown`; a interface continua pronta para um backend `Docling` posterior sem alterar os contratos do sistema.

Identidades mockadas úteis nesta fase:

- `user_external_code=USR-STUD-001` para `Lucas Oliveira` (`student`)
- `user_external_code=USR-TEACH-001` para `Helena Rocha` (`teacher`)
- `user_external_code=USR-FIN-001` para `Carla Nogueira` (`finance`)
- para obter um `telegram_chat_id` funcional, gere o challenge no portal ou por token e conclua o fluxo `/start link_<codigo>` no `telegram-gateway`

Credenciais mockadas do `Keycloak` local:

- realm: `eduassist`
- client de teste por senha: `eduassist-cli`
- senha padrao dos usuarios importados: `Eduassist123!`
- exemplos de username:
  - `maria.oliveira`
  - `lucas.oliveira`
  - `helena.rocha`
  - `carla.nogueira`

Exemplo de obtenção de token local:

```bash
curl -s http://localhost:8080/realms/eduassist/protocol/openid-connect/token \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'client_id=eduassist-cli' \
  -d 'grant_type=password' \
  -d 'username=maria.oliveira' \
  -d 'password=Eduassist123!'
```
