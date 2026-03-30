# Next-Gen Chatbot Comparison Plan

## Objetivo

Este documento atualiza o plano do projeto a partir de tres coisas:

1. o objetivo central do produto: comparar `LangGraph` e `CrewAI` em um caso educacional real;
2. o estado atual do runtime e da camada de retrieval ja implementados no repositorio;
3. a conversa registrada em [tmp/resposta_chatpg.txt](../../tmp/resposta_chatpg.txt), que traz um ponto correto: qualidade vem mais de `arquitetura`, `tooling`, `memory`, `retrieval` e `evals` do que do framework isolado.

O foco aqui e responder com rigor a estas perguntas:

- o que daquele texto ja existe hoje no sistema;
- o que ainda falta;
- se vale abrir um terceiro e quarto caminho de chatbot;
- quais caminhos realmente podem dar salto de qualidade;
- em que ordem vale implementar.

## Conclusao executiva

Se o objetivo e buscar o melhor resultado tecnico possivel sem perder a comparacao justa, a recomendacao e:

1. manter `LangGraph` e `CrewAI`;
2. abrir um terceiro caminho com `Python puro + functions`, sem framework pesado;
3. abrir um quarto caminho com `LlamaIndex Workflows`;
4. tratar `OpenAI Agents SDK` como trilha opcional de benchmark vendor-native, nao como prioridade acima dessas duas;
5. nao usar `Codex subagents` como runtime do chatbot;
6. nao tratar `Claude Agent SDK` como uma das duas proximas apostas principais para este produto.

Resumo pratico:

- `terceiro caminho recomendado`: `Python puro + functions`
- `quarto caminho recomendado`: `LlamaIndex Workflows`
- `quinto caminho opcional`: `OpenAI Agents SDK`
- `nao recomendado como caminho principal agora`: `Claude Agent SDK`, `Codex subagents`

## Status de implementacao em 30 de marco de 2026

Hoje o projeto ja saiu do plano e entrou em execucao inicial:

- `1o caminho`: `LangGraph` ja existe e segue operativo;
- `2o caminho`: `CrewAI` ja existe e segue operativo;
- `3o caminho`: `Python puro + functions` ja foi implementado de forma experimental, usando o kernel comum;
- `4o caminho`: `LlamaIndex Workflows` ja foi implementado de forma experimental, tambem sobre o kernel comum;
- `5o caminho opcional`: `OpenAI Agents SDK` ainda nao foi aberto.

Importante:

- os caminhos `3` e `4` ainda estao em fase `experimental`;
- eles ja passam em smoke local;
- eles agora tambem contam com benchmark comparativo amplo e preflight operacional para runtime override;
- eles ainda nao estao em rollout real continuo, mas ja ficaram prontos para `trafego controlado` com validacao.

## Leitura do arquivo tmp/resposta_chatpg.txt

O texto em [tmp/resposta_chatpg.txt](../../tmp/resposta_chatpg.txt) faz 6 afirmacoes principais. Abaixo esta o diagnostico honesto do estado atual do repo.

### 1. "Qualidade nao vem do framework, vem do design"

Isso esta `correto`.

O repositorio ja foi na direcao certa em varias frentes:

- isolamento estrito para benchmark puro;
- retrieval compartilhada e mais forte;
- traces e scorecards;
- evaluacao comparativa por datasets;
- guardrails e backstops;
- tools deterministicas para dados estruturados.

Mas ainda existe espaco para subir o nivel do design:

- falta um `kernel comum` de `plan -> execute -> reflect`;
- falta uma `memoria explicita compartilhada` mais forte;
- falta uma camada de `entity resolution` comum;
- falta uma camada de `retrieval intelligence` ainda mais avancada.

### 2. "Plan -> Execute -> Reflect"

Estado atual: `parcial`.

Ja existe hoje:

- `query planning` em [retrieval.py](../../apps/ai-orchestrator/src/ai_orchestrator/retrieval.py);
- `planner/composer/judge` no caminho publico do `CrewAI`;
- guardrails e backstops em varias trilhas;
- traces que permitem revisar a execucao.

Ainda falta:

- tornar `plan -> execute -> reflect` um contrato obrigatorio para todas as stacks;
- usar o mesmo esquema de plano, execucao e reflexao em `LangGraph`, `CrewAI` e qualquer novo caminho;
- separar melhor `reflexao de qualidade` de `resposta final`, para nao depender de heuristica espalhada.

### 3. "Tool-first, nao chat-first"

Estado atual: `bom, mas nao uniforme`.

Ja existe hoje:

- tools deterministicas para notas, financeiro, agenda, protocolos e operacoes;
- `structured retrieval` e `hybrid retrieval`;
- `GraphRAG` e retrieval avancada;
- flows operacionais com forte peso de ferramenta.

Ainda falta:

- tornar o `tool-first` padrao tambem para consultas publicas mais complexas;
- criar um `planner` que decida de forma sistematica quando uma pergunta deve ir para:
  - tool estruturada;
  - hybrid retrieval;
  - GraphRAG;
  - resposta curta de seguranca;
- reduzir caminhos em que o modelo improvisa antes de consultar a fonte certa.

### 4. "Structured outputs"

Estado atual: `forte`.

Ja existe hoje:

- modelos `Pydantic` em [models.py](../../apps/ai-orchestrator/src/ai_orchestrator/models.py);
- estado tipado em `CrewAI Flows`;
- guardrails em [guardrails.py](../../apps/ai-orchestrator-crewai/src/ai_orchestrator_crewai/guardrails.py);
- query plan, retrieval hits, response contracts e traces estruturados.

Ainda falta:

- unificar um `schema canonico` para:
  - plano;
  - execucao de tools;
  - reflexao;
  - resposta final;
- exigir esse contrato tambem no `LangGraph` de ponta a ponta;
- padronizar o mesmo contrato para o futuro caminho `Python puro + functions`.

### 5. "Memory explicita"

Estado atual: `parcial`.

Ja existe hoje:

- memoria curta de conversa e afinidade de experimento;
- estado persistido nos `Flows` do `CrewAI`;
- contexto conversacional e focos recentes no `LangGraph`;
- memoria vetorial via `Qdrant`;
- workspace e runtime de `GraphRAG`.

Ainda falta:

- uma memoria de entidades e sessoes mais explicita e compartilhada;
- memoria episodica resumida por conversa;
- memoria semantica separada por:
  - `short-term`: contexto do thread;
  - `entity memory`: aluno, protocolo, servico, segmento;
  - `long-term memory`: corpus vetorial e grafico;
- uma API unificada para leitura e escrita dessa memoria por qualquer stack.

### 6. "Eval loop"

Estado atual: `forte`.

Ja existe hoje:

- muitos datasets e benchmarks em `tests/evals` e `tools/evals`;
- scorecards;
- readiness gates;
- relatorios de benchmark e comparacao entre stacks;
- benchmark puro com isolamento estrito.

Ainda falta:

- evals dedicadas de retrieval;
- evals de entity resolution;
- evals de groundedness com verificacao de fonte;
- evals online mais sistematicas por slice e por stack;
- um loop de melhoria automatizado ligando:
  - novo prompt/flow/retrieval;
  - benchmark;
  - scorecard;
  - decisao de rollout.

## O que ja foi otimizado no sistema

Estas areas ja estao em bom estado relativo:

### Benchmark justo

O repositorio ja implementou `strict framework isolation mode`:

- uma request nao precisa mais comecar em uma stack e terminar na outra;
- experiment e shadow podem ser desligados para benchmark puro;
- fallback cruzado pode ser bloqueado.

Referencia local:

- [strict-benchmark-and-advanced-retrieval.md](./strict-benchmark-and-advanced-retrieval.md)

### Retrieval baseline forte

Hoje o sistema ja tem uma base melhor do que um RAG simples:

- busca lexical no Postgres;
- busca vetorial no Qdrant;
- fusao por `RRF`;
- query variants;
- reranking por `late interaction`;
- `context_pack`;
- `GraphRAG` ja implementado.

### Dados estruturados

O sistema ja esta correto ao preferir tools deterministicas para:

- notas;
- financeiro;
- frequencia;
- agenda;
- protocolos;
- operacoes administrativas.

Isso e exatamente o que um sistema educacional serio deveria fazer.

### Saida estruturada e tracing

O runtime ja esta acima da media em:

- contratos de resposta;
- metadata;
- tracing;
- scorecards;
- backstops;
- guardrails.

## O que ainda falta para um salto de qualidade real

Estas sao as lacunas mais importantes.

### 1. Agent kernel comum

Hoje cada stack tem seus proprios jeitos de planejar, executar e revisar.

O proximo salto vem de criar um `kernel comum`, com estes objetos:

- `PlanSchema`
- `ExecutionStepSchema`
- `ToolCallSchema`
- `EvidencePackSchema`
- `ReflectionSchema`
- `FinalAnswerSchema`

Esse kernel deve valer para:

- `LangGraph`
- `CrewAI`
- `Python puro + functions`
- `LlamaIndex Workflows`
- e, se entrar depois, `OpenAI Agents SDK`

### 2. Entity resolution compartilhada

No dominio escolar, qualidade despenca quando o sistema nao entende direito:

- qual aluno o usuario quer;
- se ele esta falando de `matricula`, `mensalidade`, `protocolo` ou `documentacao`;
- se a pergunta e hipotetica ou se e uma consulta real;
- se o assunto e publico ou protegido.

O proximo salto precisa de um servico compartilhado para:

- detectar entidades;
- resolver ambiguidades;
- manter foco ativo;
- validar referencias antes de chamar tool ou retrieval.

### 3. Retrieval ainda mais inteligente

Ja temos uma boa camada de retrieval, mas ainda ha espaco claro de evolucao:

- `contextual retrieval` no pipeline de ingestao;
- `query decomposition` para perguntas compostas;
- `router retrieval` entre:
  - structured tools
  - hybrid retrieval
  - GraphRAG
  - summary/global search
- `citation validation` antes da resposta final;
- `answer grounding judge` separado do compositor;
- cache de embeddings e de planos de retrieval;
- retrieval evals independentes da orquestracao.

### 4. Memoria explicita de alto nivel

Hoje a memoria existe, mas ainda e mais distribuida do que deveria.

O proximo salto exige uma memoria com tres camadas:

- `thread memory`: estado curto da conversa;
- `entity memory`: aluno, servico, protocolo, tarefa ativa;
- `knowledge memory`: retrieval vetorial e grafica.

### 5. Reflect loop padronizado

O sistema precisa de uma etapa clara de `reflect`, que revise:

- groundedness;
- cobertura da pergunta;
- policy de acesso;
- consistencia com a entidade ativa;
- se a resposta final esta curta, correta e completa.

Isso nao e o modelo "pensando solto". E um contrato estruturado de verificacao final.

## Pesquisa de ferramentas adicionais

Esta secao resume as opcoes extras pesquisadas nas fontes oficiais.

### Python puro + functions

Veredito: `sim, vale muito a pena`

Motivo:

- e a melhor forma de testar a tese do arquivo `tmp/resposta_chatpg.txt`: qualidade vem de design, nao de framework;
- da controle total de:
  - estado;
  - tool calls;
  - retries;
  - planejamento;
  - reflexao;
  - benchmark puro;
- serve como baseline honesto e de alto teto tecnico.

Quando esse caminho costuma ficar melhor que frameworks pesados:

- quando o dominio tem muitas tools deterministicas;
- quando seguranca e auditabilidade importam;
- quando o fluxo precisa de alta previsibilidade;
- quando voce quer comparar arquiteturas com pouca magia.

Recomendacao:

- abrir como `terceira stack`.

### OpenAI Agents SDK

Veredito: `sim, mas como trilha opcional e vendor-native`

Pontos fortes nas docs oficiais:

- handoffs;
- sessions como camada de memoria;
- function tools;
- agents as tools;
- traces;
- human-in-the-loop;
- runtime relativamente leve.

Fontes:

- https://openai.github.io/openai-agents-python/
- https://openai.github.io/openai-agents-python/quickstart/
- https://openai.github.io/openai-agents-python/tools/
- https://openai.github.io/openai-agents-python/handoffs/
- https://openai.github.io/openai-agents-python/sessions/

Leitura pragmatica:

- e forte se voce quiser um caminho `OpenAI-native`;
- pode render um benchmark muito bom com `Responses API`, tools e sessions;
- mas adiciona `vendor lock-in`;
- e sobrepoe varias coisas que um bom caminho `Python puro + functions` ja pode fazer.

Recomendacao:

- nao escolher como terceiro caminho;
- considerar como `quinto caminho opcional`, depois de `Python puro` e `LlamaIndex`.

### Claude Agent SDK

Veredito: `tecnicamente serio, mas nao e a melhor proxima aposta principal`

Pontos fortes nas docs oficiais:

- loop agentico nativo;
- hooks;
- permissions;
- subagents;
- MCP;
- compaction;
- skills.

Fontes:

- https://platform.claude.com/docs/en/agent-sdk/quickstart
- https://platform.claude.com/docs/en/agent-sdk/agent-loop
- https://platform.claude.com/docs/en/agent-sdk/hooks
- https://platform.claude.com/docs/en/agent-sdk/subagents

Leitura pragmatica:

- e bom para workflows tool-using;
- tem controles interessantes de permissao e hooks;
- mas o encaixe atual do projeto e mais forte em `Python server + retrieval propria + benchmark cross-provider`;
- ele nao entrega um ganho unico tao grande quanto `Python puro` ou `LlamaIndex Workflows` neste dominio.

Recomendacao:

- manter como referencia de arquitetura;
- nao abrir como uma das duas proximas stacks principais.

### Codex subagents

Veredito: `nao como runtime do chatbot`

Motivo:

- faz muito sentido para engenharia, desenvolvimento, revisao, pesquisa e automacao interna;
- nao e a melhor escolha como `engine` de um chatbot educacional de producao.

Uso recomendado:

- gerar datasets;
- automatizar evals;
- revisar prompts, flows e traces;
- comparar resultados em pipeline de engenharia.

Uso nao recomendado:

- colocar como stack de conversa do usuario final.

### LlamaIndex Workflows

Veredito: `sim, vale muito a pena`

Pontos fortes nas docs oficiais:

- workflows event-driven e step-based;
- forte em RAG, query planning, routing e retrieval;
- `FunctionAgent`, `AgentWorkflow`, `RouterRetriever`, query transformations;
- observabilidade e boa afinidade com pipelines complexos de dados.

Fontes:

- https://docs.llamaindex.ai/en/stable/understanding/workflows/
- https://docs.llamaindex.ai/en/stable/workflows/
- https://docs.llamaindex.ai/en/stable/understanding/agent/
- https://docs.llamaindex.ai/en/stable/use_cases/agents/
- https://docs.llamaindex.ai/en/stable/examples/retrievers/router_retriever/

Leitura pragmatica:

- o projeto e fortemente orientado a retrieval;
- esse e exatamente o tipo de sistema em que `LlamaIndex Workflows` pode trazer ganho real;
- ele acrescenta algo que `CrewAI` e `LangGraph` nao cobrem tao bem: um ecossistema muito forte para retrieval/routing/query planning.

Recomendacao:

- abrir como `quarta stack`.

## Qual e a melhor combinacao de caminhos

Se o projeto for abrir mais dois caminhos alem de `LangGraph` e `CrewAI`, a melhor combinacao e:

### Caminho 3: Python puro + functions

Papel:

- baseline de controle maximo;
- stack de referencia para provar que design vale mais que framework;
- candidato forte para alta qualidade e auditabilidade.

### Caminho 4: LlamaIndex Workflows

Papel:

- stack de retrieval-first;
- candidato forte para perguntas abertas, complexas e multi-documento;
- trilha mais promissora para elevar "inteligencia de busca".

## O que eu nao abriria primeiro

### Nao abriria primeiro: OpenAI Agents SDK

Nao porque seja ruim. Pelo contrario: as docs oficiais mostram um produto forte.

Mas, neste contexto, ele vem depois de:

- `Python puro`, porque queremos medir o efeito da arquitetura sem magia;
- `LlamaIndex`, porque retrieval e um eixo central do produto.

### Nao abriria primeiro: Claude Agent SDK

Pelo mesmo motivo:

- e interessante;
- mas nao entrega o melhor ganho marginal para este repositorio agora.

## Arquitetura alvo recomendada

Independentemente da stack, o sistema deveria convergir para esta arquitetura:

1. `Input classifier`
   - publico, protegido, suporte, workflow
   - pergunta simples, composta, global, operacional

2. `Entity resolver`
   - aluno
   - protocolo
   - servico
   - segmento
   - periodo

3. `Plan`
   - escolher o melhor caminho:
     - tool estruturada
     - hybrid retrieval
     - GraphRAG
     - multi-step workflow

4. `Execute`
   - chamar tools e retrieval
   - montar `evidence pack`
   - registrar tudo em trace

5. `Reflect`
   - groundedness
   - acesso
   - cobertura
   - consistencia com a entidade ativa

6. `Compose`
   - resposta final curta, humana e auditavel

## Plano recomendado: plan -> execute -> reflect

### Fase 1: consolidar o kernel comum

Implementar um `agent kernel` compartilhado para todas as stacks, com:

- `PlanSchema`
- `ToolCallSchema`
- `EvidencePackSchema`
- `ReflectionSchema`
- `FinalAnswerSchema`

Meta:

- tornar comparacao entre stacks mais justa;
- facilitar traces e evals comparaveis.

### Fase 2: reforcar a retrieval state-of-the-art

Implementacoes recomendadas:

- `entity resolution` compartilhada;
- `query decomposition`;
- `router retrieval`;
- `contextual retrieval` na indexacao;
- `GraphRAG` como servico compartilhado;
- retrieval evals dedicadas;
- grounding judge separado.

### Fase 3: abrir o caminho Python puro + functions

Implementar uma nova stack com:

- orquestracao manual em Python;
- `plan -> execute -> reflect` obrigatorio;
- function calling tipado;
- sem framework pesado;
- mesma camada compartilhada de:
  - auth
  - tools
  - retrieval
  - traces
  - evals

Meta:

- medir o teto tecnico de uma arquitetura enxuta e controlada.

### Fase 4: abrir o caminho LlamaIndex Workflows

Implementar uma nova stack com:

- `Workflow` event-driven;
- `RouterRetriever`;
- query planning;
- retrieval-first orchestration;
- a mesma camada compartilhada de dados, tools e traces.

Meta:

- medir se o melhor ecossistema de retrieval do mercado traz ganho real aqui.

### Fase 5: opcionalmente abrir OpenAI Agents SDK

Implementar somente se, depois das fases anteriores, quisermos medir:

- uma stack OpenAI-native;
- sessions/handoffs/traces nativos;
- comparacao orientada ao provedor OpenAI.

Meta:

- medir performance vendor-native, nao substituir o baseline principal.

### Fase 6: usar Claude Agent SDK como referencia e benchmark secundario

Nao como prioridade de runtime principal, mas como fonte de patterns para:

- hooks;
- permissions;
- subagents;
- compaction;
- controles de sessao.

## O que deve ser implementado primeiro para dar salto real de qualidade

Se a pergunta for "qual mudanca traz mais qualidade no menor prazo?", a ordem recomendada e:

1. `entity resolution compartilhada`
2. `plan -> execute -> reflect` como contrato comum
3. `Python puro + functions`
4. `retrieval evals + grounding judge`
5. `LlamaIndex Workflows`
6. `GraphRAG compartilhado`

## O que significa "estado da arte" neste projeto

Para este caso educacional, "estado da arte" nao e "mais agentes" nem "mais framework".

Estado da arte aqui significa:

- retrieval em varias etapas;
- roteamento explicito;
- tools deterministicas para dados estruturados;
- schemas fortes;
- memoria explicita;
- traces bons;
- eval loop continuo;
- benchmark puro entre stacks;
- reflexao final grounded e auditavel.

## Recomendacao final

Se o projeto quiser realmente comparar "as melhores ferramentas possiveis" sem virar uma colecao desorganizada de frameworks, a recomendacao e:

- manter `LangGraph`;
- manter `CrewAI`;
- adicionar `Python puro + functions`;
- adicionar `LlamaIndex Workflows`;
- deixar `OpenAI Agents SDK` como trilha opcional depois;
- usar `Claude Agent SDK` como referencia de padroes, nao como uma das duas primeiras novas stacks;
- usar `Codex subagents` so no workflow de engenharia, nunca como engine principal do chatbot.

Essa combinacao e a que melhor equilibra:

- comparacao justa;
- ganho tecnico real;
- maturidade de retrieval;
- controle de producao;
- potencial de qualidade.
