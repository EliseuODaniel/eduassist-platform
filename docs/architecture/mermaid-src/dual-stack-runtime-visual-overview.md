# Visao Geral e Resolucao de Stack

## 1. Visao Geral

```mermaid
graph LR
    User["Usuario: Telegram, Portal ou Admin"] --> Gateway["telegram-gateway: canal e normalizacao"]
    Gateway --> API["api-core: dominio, auth e policies"]
    API --> Orch["ai-orchestrator: entrypoint unico"]

    Orch -->|langgraph| LG["LangGraph runtime"]
    Orch -->|crewai| CE["CrewAIEngine"]
    CE --> Pilot["ai-orchestrator-crewai: pilot isolado"]

    LG --> Truth["Fontes de verdade"]
    Pilot --> Truth
    Truth --> API
```

## 2. Como a stack primaria e resolvida

```mermaid
graph TD
    A["Nova request: /v1/messages/respond"] --> B{"Entrou no experimento por slice?"}
    B -- Sim --> C["Primary = CrewAI; mode = experiment:slice:crewai"]
    B -- Nao --> D{"Ha runtime override?"}
    D -- Sim --> E["Usa runtime override"]
    D -- Nao --> F{"Feature flag definida?"}
    F -- Sim --> G["Usa FEATURE_FLAG_PRIMARY_ORCHESTRATION_STACK"]
    F -- Nao --> H["Usa orchestrator_engine do startup"]

    C --> I["Executa stack escolhida"]
    E --> I
    G --> I
    H --> I
```

## 3. O que e fonte de verdade

```mermaid
graph LR
    PG["Postgres: dados estruturados, RLS e FTS"]
    API["api-core interno: contracts e services"]
    QD["Qdrant: dense e sparse retrieval"]
    GR["Workspace GraphRAG: artefatos offline"]
    LG["LangGraph"]
    CE["CrewAI Flows"]
    LLM["LLM provider"]

    LG --> API
    LG --> QD
    LG --> PG
    LG --> GR
    CE --> API
    CE --> LLM
    LG --> LLM
```

Resumo:

- dados estruturados: `api-core` + `Postgres`
- dados documentais: `Qdrant + PostgreSQL FTS`
- corpus-level: `GraphRAG`
- `LLM`, `LangGraph` e `CrewAI` nao sao fonte de verdade
