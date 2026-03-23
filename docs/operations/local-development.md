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
- a proxima expansao operacional prevista e a entrada do pipeline documental com `Docling`.

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
- observabilidade dedicada ainda ficará para a próxima etapa do roadmap.

### `compose:observability`

Serviços:

- otel-collector
- grafana
- loki
- tempo

Uso:

- tracing, logs e debugging operacional.

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

## 10. Critérios de pronto para desenvolvimento

- docker funcional no WSL;
- compose sobe stack mínima;
- banco recebe seed;
- keycloak sobe realm inicial;
- webhook local consegue ser exposto;
- logs e traces mínimos aparecem corretamente.

## 11. Comandos úteis desta fase

- `make db-upgrade`
- `make db-seed-foundation`
- `make db-seed-auth-bindings`
- `GET /v1/foundation/summary` no `api-core`
- `GET /v1/identity/context?telegram_chat_id=987654321`
- `GET /v1/identity/context?user_external_code=USR-TEACH-001`
- `GET /v1/auth/session` com `Authorization: Bearer <token>`
- `POST /v1/auth/telegram-link/challenges` com `Authorization: Bearer <token>`
- `POST /webhooks/telegram` no `telegram-gateway` com `/start link_<codigo>`
- `GET /v1/students/{student_id}/academic-summary?...`
- `GET /v1/students/{student_id}/financial-summary?...`
- `GET /v1/teachers/me/schedule?user_external_code=USR-TEACH-001`
- `POST /v1/authz/check`

Identidades mockadas úteis nesta fase:

- `telegram_chat_id=987654321` para `Maria Oliveira` (`guardian`)
- `user_external_code=USR-STUD-001` para `Lucas Oliveira` (`student`)
- `user_external_code=USR-TEACH-001` para `Helena Rocha` (`teacher`)
- `user_external_code=USR-FIN-001` para `Carla Nogueira` (`finance`)

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
