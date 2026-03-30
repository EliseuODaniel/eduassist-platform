# Operacao, Fontes de Verdade e Estrategia de Dados

## 1. Support e workflow no CrewAI

![diagram](./mermaid-assets/data/dual-stack-data-retrieval-visual-flow-1.svg)

## 2. Fontes de verdade por stack

![diagram](./mermaid-assets/data/dual-stack-data-retrieval-visual-flow-2.svg)

## 3. Quando o sistema usa cada estrategia

![diagram](./mermaid-assets/data/dual-stack-data-retrieval-visual-flow-3.svg)

Resumo:

- `LangGraph` concentra o plano de retrieval avancado
- `CrewAI` concentra `Flow`, estado por slice e composicao agentic
- ambos compartilham contratos, auth, traces e fontes de verdade
