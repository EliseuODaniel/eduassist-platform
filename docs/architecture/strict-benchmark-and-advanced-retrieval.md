# Strict Benchmark Mode And Advanced Retrieval

## Objetivo

Este documento explica duas mudanças arquiteturais feitas para o experimento entre `LangGraph` e `CrewAI`:

1. garantir uma comparacao justa entre as stacks, sem uma request comecar em uma e terminar na outra;
2. elevar a camada de busca para um pipeline mais moderno, com planejamento de query, fusao de candidatos, reranking e contexto compartilhado.

O objetivo do projeto continua o mesmo: comparar os frameworks em um caso educacional real, sem misturar o papel de cada um.

## O problema que existia antes

Antes desta rodada, a comparacao ainda tinha tres pontos de contaminacao:

- `experimento por tipo de conversa`: uma parte do trafego podia ser desviada para `CrewAI` quando o primario ainda era `LangGraph`;
- `shadow mode`: as duas stacks podiam rodar para a mesma request, mesmo quando so uma respondia ao usuario;
- `fallback CrewAI -> LangGraph`: se o piloto do `CrewAI` falhasse, o orquestrador principal podia cair para o `LangGraph`.

Isso era bom para seguranca operacional, mas ruim para benchmark puro.

## O que foi implementado

### 1. Strict framework isolation mode

Foi adicionado um modo de isolamento estrito controlado por configuracao:

- `STRICT_FRAMEWORK_ISOLATION_ENABLED`

Quando esse modo esta ligado:

- o desvio de experimento por slice fica desligado;
- o `shadow mode` deixa de rodar;
- o `CrewAI` deixa de cair para o `LangGraph` quando falha.

Nesse caso, se o `CrewAI` nao conseguir responder, ele devolve uma resposta segura dele mesmo, sem terceirizar a conclusao para a outra stack.

Arquivos principais:

- [engine_selector.py](../../apps/ai-orchestrator/src/ai_orchestrator/engine_selector.py)
- [crewai_engine.py](../../apps/ai-orchestrator/src/ai_orchestrator/engines/crewai_engine.py)
- [main.py](../../apps/ai-orchestrator/src/ai_orchestrator/main.py)

### 2. Retrieval em duas etapas

A camada de retrieval foi reestruturada para um pipeline mais forte:

1. `query planning`
   - identifica se a pergunta parece contato, timeline, documentos, preco ou visao geral;
   - gera variantes da pergunta;
   - marca quando a pergunta parece candidata a `GraphRAG`.

2. `candidate generation`
   - busca lexical no Postgres FTS;
   - busca vetorial no Qdrant;
   - faz isso com mais de uma variante da query quando faz sentido.

3. `fusion`
   - combina os resultados com `RRF`;
   - aplica pequenos boosts por intencao e categoria;
   - evita excesso de chunks do mesmo documento.

4. `late interaction reranking`
   - reranqueia os melhores candidatos com `ColBERT-style late interaction`;
   - usa `answerdotai/answerai-colbert-small-v1` via `fastembed`.

5. `context pack`
   - monta um pacote curto de contexto para a camada de resposta consumir com menos ruido.

Arquivos principais:

- [retrieval.py](../../apps/ai-orchestrator/src/ai_orchestrator/retrieval.py)
- [models.py](../../apps/ai-orchestrator/src/ai_orchestrator/models.py)
- [main.py](../../apps/ai-orchestrator/src/ai_orchestrator/main.py)

### 3. Retrieval compartilhada para as duas stacks

O `LangGraph` ja usava a retrieval do orquestrador principal.

Agora o `CrewAI` publico tambem consegue consumir essa retrieval compartilhada, sem deixar de ser `CrewAI` no caminho final de resposta.

Isso preserva a comparacao correta:

- mesma fonte de dados;
- mesmo mecanismo de busca;
- frameworks diferentes apenas na orquestracao e composicao da resposta.

Arquivos principais:

- [public_pilot.py](../../apps/ai-orchestrator-crewai/src/ai_orchestrator_crewai/public_pilot.py)
- [public_flow.py](../../apps/ai-orchestrator-crewai/src/ai_orchestrator_crewai/public_flow.py)
- [main.py](../../apps/ai-orchestrator-crewai/src/ai_orchestrator_crewai/main.py)

## Como pensar nessa arquitetura

### O que continua compartilhado

Estas partes podem ser compartilhadas sem estragar a comparacao:

- fontes de verdade;
- autenticacao;
- contratos;
- traces;
- banco;
- Qdrant;
- API Core;
- retrieval.

### O que nao pode ser hibrido no benchmark

Estas partes precisam ser de uma stack so:

- planejamento final da resposta;
- execucao da resposta;
- composicao final do texto;
- fallback principal.

Em outras palavras:

- compartilhar `dados` e `busca` e aceitavel;
- compartilhar `resposta final` entre stacks nao e aceitavel para benchmark puro.

## Estado atual do sistema

Hoje o sistema tem estes tipos principais de recuperacao:

### Structured retrieval

Busca por tools deterministicas e endpoints estruturados.

Exemplos:

- notas;
- frequencia;
- financeiro;
- protocolos;
- agenda de visita.

### Hybrid retrieval

Busca lexical + vetorial com fusao.

Essa e a camada padrao para documentos publicos.

### GraphRAG

Ja existe no codigo, e o runtime consegue decidir quando uma pergunta parece mais global ou relacional.

Hoje ele continua sendo mais usado no lado do orquestrador principal, e nao como servico compartilhado completo para as duas stacks.

## O que isso melhora na pratica

### Para benchmark

- comparacao mais justa;
- menos contaminacao entre stacks;
- traces mais honestos;
- conclusao mais clara sobre qual framework foi melhor.

### Para qualidade de resposta

- melhora de recall;
- melhora de ranking;
- contexto mais enxuto e relevante;
- menos respostas baseadas no chunk errado;
- melhor suporte a perguntas abertas e de visao geral.

### Para latencia

O reranking adiciona custo, mas ele roda so nos melhores candidatos.

Na pratica, a ideia e esta:

- nao gastar modelo forte com o corpus inteiro;
- gastar mais inteligencia apenas no topo mais promissor.

## Proximos passos recomendados

Se quisermos levar isso ainda mais perto do estado da arte:

1. expor `GraphRAG` como servico compartilhado para as duas stacks;
2. adicionar uma camada de `entity resolution` compartilhada para aluno, segmento, protocolo e servico;
3. evoluir para `sparse + dense + late interaction`, se optarmos por reindexar o Qdrant;
4. criar evals dedicadas de retrieval, separadas das evals de orquestracao.

## Referencias usadas

Estas foram as referencias principais que guiaram a arquitetura:

- Qdrant hybrid search e multi-stage retrieval:
  - https://qdrant.tech/course/essentials/day-3/hybrid-search/
  - https://qdrant.tech/documentation/concepts/hybrid-queries/
- Microsoft GraphRAG:
  - https://github.com/microsoft/graphrag
- OpenAI practical guide to building agents:
  - https://openai.com/business/guides-and-resources/a-practical-guide-to-building-ai-agents/
- Anthropic context engineering:
  - https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
- CrewAI Flows and Tasks:
  - https://docs.crewai.com/en/concepts/flows
  - https://docs.crewai.com/en/concepts/tasks
