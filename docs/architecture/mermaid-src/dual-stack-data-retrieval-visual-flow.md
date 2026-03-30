# Operacao, Fontes de Verdade e Estrategia de Dados

## 1. Support e workflow no CrewAI

```mermaid
graph TD
    A["Flow support ou workflow"] --> B["Le estado atual no api-core"]
    B --> C{"pedido operacional conhecido?"}
    C -- Sim --> D["render deterministico e rapido"]
    C -- Nao --> E["abrir ou atualizar handoff ou workflow"]
    E --> D
```

## 2. Fontes de verdade por stack

```mermaid
graph LR
    LG["LangGraph"] --> API["api-core"]
    LG --> QD["Qdrant"]
    LG --> FTS["Postgres FTS"]
    LG --> GR["GraphRAG"]

    CE["CrewAI pilot"] --> API
    API --> PG["Postgres + RLS"]
```

## 3. Quando o sistema usa cada estrategia

```mermaid
graph TD
    Q["Pergunta do usuario"] --> A{"Dado estruturado de sistema?"}
    A -- Sim --> B["Tool deterministica via api-core"]
    A -- Nao --> C{"Fato publico canonico?"}
    C -- Sim --> D["Public endpoint canonico"]
    C -- Nao --> E{"Precisa busca documental?"}
    E -- Sim --> F{"Pergunta simples ou media?"}
    F -- Sim --> G["Hybrid retrieval"]
    F -- Nao --> H["GraphRAG, se habilitado"]
    E -- Nao --> I["Clarify, deny ou handoff"]
```

Resumo:

- `LangGraph` concentra o plano de retrieval avancado
- `CrewAI` concentra `Flow`, estado por slice e composicao agentic
- ambos compartilham contratos, auth, traces e fontes de verdade
