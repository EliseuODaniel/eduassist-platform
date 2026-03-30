# Visao Geral e Resolucao de Stack

## 1. Visao Geral

![diagram](./mermaid-assets/overview/dual-stack-runtime-visual-overview-1.svg)

## 2. Como a stack primaria e resolvida

![diagram](./mermaid-assets/overview/dual-stack-runtime-visual-overview-2.svg)

## 3. O que e fonte de verdade

![diagram](./mermaid-assets/overview/dual-stack-runtime-visual-overview-3.svg)

Resumo:

- dados estruturados: `api-core` + `Postgres`
- dados documentais: `Qdrant + PostgreSQL FTS`
- corpus-level: `GraphRAG`
- `LLM`, `LangGraph` e `CrewAI` nao sao fonte de verdade
