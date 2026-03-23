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
