# Infra

Diretório reservado para infraestrutura do projeto:

- `compose/`
- `k8s/`
- templates de ambiente
- scripts de bootstrap

O bootstrap inicial está implementado em:

- [compose.yaml](/home/edann/projects/eduassist-platform/infra/compose/compose.yaml)
- [01-create-databases.sh](/home/edann/projects/eduassist-platform/infra/compose/postgres/init/01-create-databases.sh)
- [policy.rego](/home/edann/projects/eduassist-platform/infra/compose/opa/policy.rego)

Estado atual relevante:

- `Qdrant` ja integrado ao ambiente local;
- foundation transacional do `api-core` ja validada em `PostgreSQL`;
- `Postgres`, `Redis`, `MinIO`, `Keycloak`, `OPA` e apps bootstrapados;
- bootstrap do papel `eduassist_app` versionado em `postgres/init/02-create-app-role.sh`;
- observabilidade dedicada ja integrada ao Compose com `OpenTelemetry`, `Tempo`, `Prometheus`, `Loki` e `Grafana`.
- backup operacional local de `Postgres`, `Qdrant` e `MinIO` disponivel em `tools/ops`, com restore de verificacao nao-destrutivo.
- o Compose principal já contempla a arquitetura `dedicated-first`, com runtimes dedicados, `telegram-gateway` apontando para stack dedicada e `ai-orchestrator` central em papel de `control plane`.
