# Catálogo de Serviços

## Objetivo

Registrar as fronteiras reais do sistema no estado `dedicated-first` atual.

## `telegram-gateway`

### Responsabilidades

- receber webhook do Telegram;
- validar segredo do canal e token interno de serviço;
- normalizar update, idempotência e serialização por chat;
- encaminhar a mensagem para um runtime dedicado configurado;
- expor diagnósticos operacionais mínimos para troubleshooting.

### Não responsabilidades

- roteamento profundo de domínio;
- autorização escolar;
- acesso direto a dados acadêmicos ou financeiros.

## `api-core`

### Responsabilidades

- autenticação e resolução de ator;
- consulta a `OPA`;
- aplicação de contexto de sessão para `RLS`;
- serviços canônicos públicos e protegidos;
- auditoria, fila operacional e memória persistida do produto.

## `ai-orchestrator`

### Papel real atual

`ai-orchestrator` é `control plane/router`.

### Responsabilidades

- status agregado das stacks;
- scorecard, promotion gate e rollout controlado;
- metadados e comparações cross-stack;
- compat mode apenas quando explicitamente habilitado.

### Não responsabilidades

- serving principal do usuário final em produção local normal;
- competir semanticamente com os runtimes dedicados como “quinta stack”.

## `ai-orchestrator-langgraph`

### Responsabilidades

- workflow nativo `LangGraph`;
- checkpoints, governança de estado e routing por grafo;
- serving dedicado por `FastAPI`.

## `ai-orchestrator-python-functions`

### Responsabilidades

- resolução determinística e lanes tipadas;
- paths curtos de baixa latência;
- abstention e clarificação seguras para entradas incertas.

## `ai-orchestrator-llamaindex`

### Responsabilidades

- workflow nativo do `LlamaIndex`;
- respostas documentais e de recuperação orientada a fontes;
- serving dedicado via runtime próprio.

## `ai-orchestrator-specialist`

### Responsabilidades

- caminho quality-first especializado;
- coordenação supervisor/specialists;
- refino final validado de superfície para respostas elegíveis, inclusive as vindas de caminhos determinísticos;
- fallback preservado quando a LLM não conseguir refinar sem violar grounding, policy ou intenção original;
- serving dedicado isolado do control plane.

## `local-llm-gemma4e4b`

### Responsabilidades

- servir `Gemma 4 E4B` localmente em endpoint `OpenAI-compatible`;
- sustentar o baseline local do repositório para benchmark e operação local.

## `local-llm-qwen3-4b`

### Responsabilidades

- servir `Qwen3-4B-Instruct-2507` localmente em endpoint `OpenAI-compatible`;
- permitir benchmark A/B controlado sem alterar o baseline do repositório;
- permanecer como profile experimental por feature flag enquanto o baseline operacional segue em `Gemma 4 E4B`.

## `worker`

### Responsabilidades

- parsing e ingestão documental;
- embeddings, indexação e artefatos de retrieval;
- jobs offline e evals.

## `admin-web`

### Responsabilidades

- operação do sistema;
- revisão de conversas e fila humana;
- visão administrativa do estado do produto.

## Infra dados

### `postgres`

- source of truth relacional;
- `RLS`;
- auditoria;
- busca textual;
- persistência operacional.

### `qdrant`

- retrieval vetorial e híbrido;
- late interaction quando habilitado;
- coleções documentais e auxiliares.

### `redis`

- locks, cache, idempotência e coordenação leve.

### `minio`

- objetos, anexos e documentos brutos.

## Observabilidade

### `otel-collector`

- recebe OTLP;
- aplica `tail sampling`;
- exporta traces e métricas.

### `tempo`

- armazenamento e consulta de traces distribuídos.

### `prometheus`

- métricas OTEL e métricas de domínio/GenAI.

### `grafana`

- dashboards operacionais, tracing e GenAI.

### `loki` e `promtail`

- logs centralizados e investigação textual.
