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
- a próxima expansão operacional prevista é a entrada de `Qdrant` na stack local quando a fase de retrieval começar.

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
- `Qdrant` já está aprovado no planejamento, mas ainda não foi adicionado ao Compose nesta fase de bootstrap;
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

## 9. Variáveis de ambiente previstas

- `DATABASE_URL`
- `REDIS_URL`
- `MINIO_ENDPOINT`
- `KEYCLOAK_*`
- `OPA_URL`
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_WEBHOOK_SECRET`
- `LLM_PROVIDER`
- `OPENAI_API_KEY`
- `GOOGLE_API_KEY`

## 10. Critérios de pronto para desenvolvimento

- docker funcional no WSL;
- compose sobe stack mínima;
- banco recebe seed;
- keycloak sobe realm inicial;
- webhook local consegue ser exposto;
- logs e traces mínimos aparecem corretamente.
