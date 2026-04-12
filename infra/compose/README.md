# Compose Stack

Este diretório contém o bootstrap da stack local do projeto.

Arquivos principais:

- `compose.yaml`: stack principal do ambiente local
- `postgres/init/01-create-databases.sh`: criação das bases iniciais
- `postgres/init/02-create-app-role.sh`: bootstrap do papel de aplicação do Postgres
- `opa/policy.rego`: política bootstrap do OPA
- `tools/ops/backup_local_stack.sh`: backup local de Postgres, Qdrant e MinIO
- `tools/ops/verify_local_backup.sh`: drill seguro de restore em banco, coleção e bucket temporários

Serviços-base já contemplados:

- `postgres`
- `redis`
- `qdrant`
- `minio`
- `keycloak`
- `opa`
- `api-core`
- `ai-orchestrator`
- `telegram-gateway`
- `worker`
- `admin-web`

Arquitetura atual relevante:

- o `ai-orchestrator` central opera como `control plane/router`;
- o serving principal de usuário sai dos runtimes dedicados:
  - `ai-orchestrator-langgraph`
  - `ai-orchestrator-python-functions`
  - `ai-orchestrator-llamaindex`
  - `ai-orchestrator-specialist`
- o `telegram-gateway` deve apontar para um runtime dedicado, não para o control plane, salvo em modo explícito de compatibilidade.

Uso rápido:

1. `cp .env.example .env`
2. `make compose-config`
3. `make compose-up`
4. `make db-bootstrap-app-role`

Fluxo dedicado-first mais comum:

1. `make compose-up-dedicated-core`
2. `make compose-up-telegram-python-functions` ou outro target equivalente por stack
3. `make smoke-dedicated`
4. `make smoke-telegram-dedicated`
