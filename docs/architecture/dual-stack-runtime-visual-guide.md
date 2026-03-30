# Guia Visual do Runtime Dual Stack

Este arquivo ficou em formato `preview-safe` para o `Open Preview` do VS Code: os diagramas aparecem como SVGs gerados a partir do Mermaid, em vez de Mermaid inline.

## O que voce vai encontrar

- como a request entra pelo `ai-orchestrator`
- como o sistema decide entre `LangGraph`, `CrewAI`, `runtime override`, feature flag e experimento por slice
- como o `LangGraph` escolhe entre `structured_tool`, `hybrid_retrieval`, `GraphRAG`, `handoff`, `deny` e `clarify`
- como o `CrewAI` passa pelo `engine adapter`, escolhe slice e executa `Flow` no servico isolado
- onde os dados realmente sao buscados nas fontes de verdade

## 1. Visao Geral e Resolucao de Stack

### 1.1 Visao geral

![Visao geral](./mermaid-assets/overview/dual-stack-runtime-visual-overview-1.svg)

### 1.2 Como a stack primaria e resolvida

![Resolucao de stack](./mermaid-assets/overview/dual-stack-runtime-visual-overview-2.svg)

### 1.3 O que e fonte de verdade

![Fontes de verdade](./mermaid-assets/overview/dual-stack-runtime-visual-overview-3.svg)

Resumo:

- dados estruturados: `api-core` + `Postgres`
- dados documentais: `Qdrant + PostgreSQL FTS`
- corpus-level: `GraphRAG`
- `LLM`, `LangGraph` e `CrewAI` nao sao fonte de verdade

## 2. Fluxo Detalhado do LangGraph

### 2.1 Planejamento do grafo

![Planejamento LangGraph](./mermaid-assets/langgraph/dual-stack-langgraph-visual-flow-1.svg)

### 2.2 O que acontece depois do preview

![Execucao LangGraph](./mermaid-assets/langgraph/dual-stack-langgraph-visual-flow-2.svg)

### 2.3 Decisao de retrieval no slice publico

![Retrieval LangGraph](./mermaid-assets/langgraph/dual-stack-langgraph-visual-flow-3.svg)

Notas:

- `protected` e `support` podem entrar em `HITL`
- `structured_tool` e preferido quando ha fonte estruturada confiavel
- `GraphRAG` nao e o default; ele entra quando a pergunta exige visao global do corpus

## 3. Fluxo Detalhado do CrewAI

### 3.1 Adapter no runtime principal

![Adapter CrewAI](./mermaid-assets/crewai/dual-stack-crewai-visual-flow-1.svg)

### 3.2 Slice public

![Public Flow CrewAI](./mermaid-assets/crewai/dual-stack-crewai-visual-flow-2.svg)

### 3.3 Slice protected

![Protected Flow CrewAI](./mermaid-assets/crewai/dual-stack-crewai-visual-flow-3.svg)

Notas:

- o `CrewAI` roda em servico isolado
- `Flow` e persistido por slice
- quando o piloto nao consegue devolver `answer_text`, o adapter pode cair em fallback explicito

## 4. Operacao, Fontes de Verdade e Estrategia de Dados

### 4.1 Support e workflow no CrewAI

![Support e workflow CrewAI](./mermaid-assets/data/dual-stack-data-retrieval-visual-flow-1.svg)

### 4.2 Fontes de verdade por stack

![Fontes por stack](./mermaid-assets/data/dual-stack-data-retrieval-visual-flow-2.svg)

### 4.3 Quando o sistema usa cada estrategia

![Estrategia de dados](./mermaid-assets/data/dual-stack-data-retrieval-visual-flow-3.svg)

Resumo:

- `LangGraph` concentra o plano de retrieval avancado
- `CrewAI` concentra `Flow`, estado por slice e composicao agentic
- ambos compartilham contratos, auth, traces e fontes de verdade

## Regra de Ouro

Se surgir duvida sobre "de onde veio essa resposta?", siga esta ordem:

1. verifique qual stack respondeu
2. descubra o slice
3. descubra o modo
4. so depois olhe para a LLM

Na maior parte dos casos, o erro esta em:

- roteamento errado
- contexto errado
- fonte de verdade errada
- retrieval inadequado

Nao comeca na LLM.

## Onde procurar no codigo

- entrada principal: [main.py](../../apps/ai-orchestrator/src/ai_orchestrator/main.py)
- selecao de stack e canario: [engine_selector.py](../../apps/ai-orchestrator/src/ai_orchestrator/engine_selector.py)
- grafo LangGraph: [graph.py](../../apps/ai-orchestrator/src/ai_orchestrator/graph.py)
- runtime LangGraph e composicao: [runtime.py](../../apps/ai-orchestrator/src/ai_orchestrator/runtime.py)
- runtime de checkpoint/HITL LangGraph: [langgraph_runtime.py](../../apps/ai-orchestrator/src/ai_orchestrator/langgraph_runtime.py)
- adapter CrewAI no orquestrador: [crewai_engine.py](../../apps/ai-orchestrator/src/ai_orchestrator/engines/crewai_engine.py)
- servico isolado CrewAI: [main.py](../../apps/ai-orchestrator-crewai/src/ai_orchestrator_crewai/main.py)
- flow publico CrewAI: [public_flow.py](../../apps/ai-orchestrator-crewai/src/ai_orchestrator_crewai/public_flow.py)
- flow protegido CrewAI: [protected_flow.py](../../apps/ai-orchestrator-crewai/src/ai_orchestrator_crewai/protected_flow.py)
- flow de suporte CrewAI: [support_flow.py](../../apps/ai-orchestrator-crewai/src/ai_orchestrator_crewai/support_flow.py)
- flow de workflow CrewAI: [workflow_flow.py](../../apps/ai-orchestrator-crewai/src/ai_orchestrator_crewai/workflow_flow.py)
- ADR de retrieval: [0002-retrieval-and-agent-runtime.md](../adr/0002-retrieval-and-agent-runtime.md)

## Fontes Mermaid

Os fontes originais dos diagramas continuam versionados aqui:

- [mermaid-src/dual-stack-runtime-visual-overview.md](./mermaid-src/dual-stack-runtime-visual-overview.md)
- [mermaid-src/dual-stack-langgraph-visual-flow.md](./mermaid-src/dual-stack-langgraph-visual-flow.md)
- [mermaid-src/dual-stack-crewai-visual-flow.md](./mermaid-src/dual-stack-crewai-visual-flow.md)
- [mermaid-src/dual-stack-data-retrieval-visual-flow.md](./mermaid-src/dual-stack-data-retrieval-visual-flow.md)
