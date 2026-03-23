# Compose Stack

Este diretório contém o bootstrap da stack local do projeto.

Arquivos principais:

- `compose.yaml`: stack principal do ambiente local
- `postgres/init/01-create-databases.sh`: criação das bases iniciais
- `opa/policy.rego`: política bootstrap do OPA

Uso rápido:

1. `cp .env.example .env`
2. `make compose-config`
3. `make compose-up`

