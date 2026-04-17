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

## Perfil de LLM local padrão

O Compose agora sobe `Gemma 4 E4B` localmente por padrão em um endpoint `OpenAI-compatible`. `Gemini` continua disponível como override explícito por feature flag.

Serviço:

- `local-llm-gemma4e4b`
- `local-llm-qwen3-4b`

Stack de serving:

- imagem: `ghcr.io/ggml-org/llama.cpp:server-cuda`
- modelo: `ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M`
- endpoint local exposto: `http://localhost:18081/v1`
- alternativa experimental: `bartowski/Qwen_Qwen3-4B-Instruct-2507-GGUF` com `Qwen_Qwen3-4B-Instruct-2507-Q5_K_M.gguf`
- endpoint experimental: `http://localhost:18082/v1`

Targets úteis:

1. baseline local com `Gemma 4 E4B`
   - `make compose-up-dedicated-core`
2. override com `Gemini 2.5 Flash-Lite`
   - `make compose-up-dedicated-core-gemini-flash-lite`
3. bootstrap explícito do local LLM com `Gemma 4 E4B`
   - `make compose-up-dedicated-core-gemma4e4b-local`
4. bootstrap explícito do local LLM com `Qwen3-4B-Instruct-2507`
   - `make compose-up-dedicated-core-qwen3-4b-local`
5. logs do modelo local Gemma
   - `make local-llm-gemma4e4b-logs`
6. logs do modelo local Qwen
   - `make local-llm-qwen3-4b-logs`
7. parada isolada do modelo local
   - `make local-llm-gemma4e4b-down`
   - `make local-llm-qwen3-4b-down`

Feature flag principal:

- padrão: `LLM_MODEL_PROFILE=gemma4e4b_local`
- experimento local Qwen: `LLM_MODEL_PROFILE=qwen3_4b_instruct_local`
- override: `LLM_MODEL_PROFILE=gemini_flash_lite`
- refino final do `specialist`: `FEATURE_FLAG_SPECIALIST_ANSWER_REFINER_ENABLED=true`

Quando o profile `gemma4e4b_local` estiver ativo:

- o runtime principal muda para `LLM_PROVIDER=openai`;
- `OPENAI_API_MODE=chat_completions`;
- `OPENAI_BASE_URL` passa a apontar para `local-llm-gemma4e4b`;
- o `semantic ingress`, o serving principal e a camada de `answer_experience` usam o endpoint local compatível.

Quando o profile `qwen3_4b_instruct_local` estiver ativo:

- o runtime principal também muda para `LLM_PROVIDER=openai`;
- `OPENAI_API_MODE=chat_completions`;
- `OPENAI_BASE_URL` passa a apontar para `local-llm-qwen3-4b`;
- o artefato padrão é o `Q5_K_M` do `Qwen3-4B-Instruct-2507`;
- o uso recomendado é A/B controlado, não substituição silenciosa do baseline.

Resultado consolidado do A/B local mais recente:

- `Gemma 4 E4B` endurecido com o `answer surface refiner` validado fechou em `15/15`, `keyword_pass 15/15` e `quality 100.0`;
- `Qwen3-4B-Instruct-2507` permaneceu melhor em latência, mas abaixo em qualidade agregada no `specialist_supervisor`;
- decisão operacional: `Gemma` segue como baseline do Compose, e `Qwen` continua como profile experimental.
