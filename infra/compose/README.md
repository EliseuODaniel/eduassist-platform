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

## Perfil experimental de LLM local

O Compose agora inclui um perfil opcional para servir `Gemma 4 E4B` localmente em um endpoint `OpenAI-compatible`, sem mexer no baseline hospedado do projeto.

Serviço:

- `local-llm-gemma4e4b`

Stack de serving:

- imagem: `ghcr.io/ggml-org/llama.cpp:server-cuda`
- modelo: `ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M`
- endpoint local exposto: `http://localhost:18081/v1`

Targets úteis:

1. baseline com `Gemini 2.5 Flash-Lite`
   - `make compose-up-dedicated-core-gemini-flash-lite`
2. experimento local com `Gemma 4 E4B`
   - `make compose-up-dedicated-core-gemma4e4b-local`
3. logs do modelo local
   - `make local-llm-gemma4e4b-logs`
4. parada isolada do modelo local
   - `make local-llm-gemma4e4b-down`

Feature flag principal:

- `LLM_MODEL_PROFILE=gemini_flash_lite`
- `LLM_MODEL_PROFILE=gemma4e4b_local`

Quando o profile `gemma4e4b_local` estiver ativo:

- o runtime principal muda para `LLM_PROVIDER=openai`;
- `OPENAI_API_MODE=chat_completions`;
- `OPENAI_BASE_URL` passa a apontar para `local-llm-gemma4e4b`;
- o `semantic ingress`, o serving principal e a camada de `answer_experience` usam o endpoint local compatível.
