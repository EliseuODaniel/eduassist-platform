# Fluxo Detalhado do LangGraph

## 1. Planejamento do grafo

![diagram](./mermaid-assets/langgraph/dual-stack-langgraph-visual-flow-1.svg)

## 2. O que acontece depois do preview

![diagram](./mermaid-assets/langgraph/dual-stack-langgraph-visual-flow-2.svg)

## 3. Decisao de retrieval no slice publico

![diagram](./mermaid-assets/langgraph/dual-stack-langgraph-visual-flow-3.svg)

Notas:

- `protected` e `support` podem entrar em `HITL`
- `structured_tool` e preferido quando ha fonte estruturada confiavel
- `GraphRAG` nao e o default; ele entra quando a pergunta exige visao global do corpus
