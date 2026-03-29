# Guia Visual do Runtime Dual Stack

Este guia foi dividido em paginas menores porque alguns renderizadores do VS Code `Open Preview` ficam instaveis quando ha muitos blocos Mermaid no mesmo Markdown.

Use este arquivo como indice principal.

## Leitura recomendada

1. [Visao geral e resolucao de stack](./dual-stack-runtime-visual-overview.md)
2. [Fluxo detalhado do LangGraph](./dual-stack-langgraph-visual-flow.md)
3. [Fluxo detalhado do CrewAI](./dual-stack-crewai-visual-flow.md)
4. [Operacao, fontes de verdade e estrategia de dados](./dual-stack-data-retrieval-visual-flow.md)

## O que voce vai encontrar

- como a request entra pelo `ai-orchestrator`
- como o sistema decide entre `LangGraph`, `CrewAI`, `runtime override`, feature flag e experimento por slice
- como o `LangGraph` escolhe entre `structured_tool`, `hybrid_retrieval`, `GraphRAG`, `handoff`, `deny` e `clarify`
- como o `CrewAI` passa pelo `engine adapter`, escolhe slice e executa `Flow` no servico isolado
- onde os dados realmente sao buscados nas fontes de verdade

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
