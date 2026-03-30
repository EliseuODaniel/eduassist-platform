# Fluxo Detalhado do LangGraph

## 1. Planejamento do grafo

```mermaid
graph TD
    A["Request"] --> B["classify_request"]
    B --> C["security_gate"]
    C --> D["route_request"]
    D --> E["select_slice"]

    E -->|public| P["public_slice"]
    E -->|protected| R["protected_slice"]
    E -->|support| S["support_slice"]
    E -->|deny| X["deny"]
    E -->|clarify| Y["clarify"]
```

## 2. O que acontece depois do preview

```mermaid
graph LR
    Preview["Preview LangGraph"] --> A{"mode"}
    A -->|structured_tool| B["Tools internas via api-core"]
    A -->|hybrid_retrieval| C["Qdrant + PostgreSQL FTS"]
    A -->|graph_rag| D["Workspace GraphRAG"]
    A -->|clarify| E["Clarificacao curta"]
    A -->|deny| F["Negacao segura"]
    A -->|handoff| G["Ticket e encaminhamento humano"]

    B --> H["Composicao final"]
    C --> H
    D --> H
    E --> H
    F --> H
    G --> H
```

## 3. Decisao de retrieval no slice publico

```mermaid
graph TD
    Q["Pergunta publica"] --> A{"Fato publico canonico?"}
    A -- Sim --> B["structured_tool_call"]
    A -- Nao --> C{"Precisa visao multi-documento?"}
    C -- Sim --> D["graph_rag_retrieval"]
    C -- Nao --> E["hybrid_retrieval"]

    E --> E1["lexical_search no Postgres FTS"]
    E --> E2["vector_search no Qdrant"]
    E1 --> E3["fusao por RRF"]
    E2 --> E3
```

Notas:

- `protected` e `support` podem entrar em `HITL`
- `structured_tool` e preferido quando ha fonte estruturada confiavel
- `GraphRAG` nao e o default; ele entra quando a pergunta exige visao global do corpus
