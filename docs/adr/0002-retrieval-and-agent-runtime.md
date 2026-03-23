# ADR 0002: Separar plano transacional, plano de retrieval e modo avançado de GraphRAG

## Status

Aceito

## Contexto

O planejamento inicial colocava `PostgreSQL + pgvector + FTS` como base suficiente para retrieval. Após revisão das tecnologias mais atuais e adequadas para este domínio, ficou claro que:

- o banco transacional e o plano de retrieval têm requisitos diferentes;
- perguntas documentais e institucionais se beneficiam de um engine especializado em retrieval híbrido;
- nem toda pergunta justifica `GraphRAG`, mas algumas perguntas globais e multi-documento podem se beneficiar dele;
- a trilha OpenAI evoluiu para uma combinação mais forte de `Responses API` e padrões do `Agents SDK`, enquanto o projeto ainda precisa preservar portabilidade.

## Decisão

O projeto adotará as seguintes diretrizes:

- `PostgreSQL` permanece como source of truth para dados estruturados e trilha lexical/relacional.
- `Qdrant` passa a ser o engine principal de retrieval vetorial e híbrido para o corpus documental.
- `Docling` passa a ser o parser documental padrão para ingestão e normalização.
- `pgvector` permanece apenas como fallback experimental e baseline de comparação.
- `Microsoft GraphRAG` entra como modo avançado de retrieval, habilitado somente em fluxos onde os evals comprovarem ganho.
- `LangGraph` permanece como motor principal de orquestração.
- Quando a trilha OpenAI for adotada, `Responses API` e padrões do `Agents SDK` serão usados como adapter OpenAI-native para tools, handoffs estreitos e tracing.

## Consequências

### Positivas

- melhora a qualidade potencial do retrieval documental;
- permite retrieval híbrido, sparse, dense e multivector sem sobrecarregar o banco transacional;
- cria caminho formal para `GraphRAG` sem transformar complexidade em default;
- mantém a arquitetura governada e ainda alinhada com as práticas agentic mais atuais.

### Negativas

- adiciona mais um componente à stack local;
- aumenta o custo de integração e observabilidade;
- exige uma fase explícita de avaliação entre baseline híbrido e `GraphRAG`.

## Diretrizes derivadas

- perguntas simples devem usar retrieval híbrido antes de considerar `GraphRAG`;
- `GraphRAG` não deve ser usado para consultas estruturadas já resolvidas por services;
- toda tecnologia nova de retrieval só entra em produção se mostrar ganho mensurável em evals do domínio escolar;
- a abstração de provedor deve impedir acoplamento excessivo a um único runtime agentic.
