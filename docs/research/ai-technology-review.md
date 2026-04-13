# Pesquisa de Tecnologias de IA para o Projeto

## 1. Objetivo

Mapear tecnologias atuais e decidir a estratégia de IA mais adequada para uma plataforma escolar com dados documentais e estruturados, operando via Telegram e com forte necessidade de segurança e governança.

## 2. Conclusão executiva

A melhor abordagem para este projeto não é um sistema de agentes autônomos livres. A melhor abordagem é um `orquestrador governado`, com:

- parsing documental forte antes do retrieval;
- plano de retrieval dedicado;
- retrieval híbrido;
- late interaction nos corpora certos;
- `GraphRAG` seletivo;
- grounding com citações;
- tool calling com contratos rígidos;
- services determinísticos para dados estruturados;
- avaliação contínua;
- política explícita de acesso.

## 3. Modelos de linguagem

### Opção principal

- `GPT-5.4`

Motivo:

- a documentação oficial da OpenAI posiciona `gpt-5.4` como modelo recomendado para raciocínio complexo e workflows agentic.

### Benchmark paralelo

- `Gemini 2.5 Pro`

Motivo:

- a documentação do Vertex AI destaca suporte forte a contextos extensos e grounding com dados próprios, o que é útil para documentos institucionais longos.

### Estratégia recomendada

- manter camada de abstração por provedor;
- rodar benchmark comparativo em datasets do domínio escolar;
- escolher por combinação de qualidade, custo e latência.
- se OpenAI for o provedor selecionado para a primeira implementação, preferir `Responses API` em vez de interfaces legadas para fluxos tool-using e agentic.

## 4. Orquestração

### Tecnologia escolhida para o controle principal

- `LangGraph`

Justificativa:

- suporte a workflows com estado;
- boa aderência a tool calling;
- facilidade para human-in-the-loop;
- melhor controle do que arquiteturas “multiagente” abertas.

### Tecnologia complementar para a trilha OpenAI

- `Responses API`
- padrões do `OpenAI Agents SDK`

Justificativa:

- a documentação oficial da OpenAI hoje centraliza modelos, tool use e estado de conversa na `Responses API`;
- o `Agents SDK` já formaliza ferramentas, handoffs e traces, então é útil como adapter OpenAI-native para workflows específicos e benchmarking;
- manter `LangGraph` como camada principal preserva portabilidade entre provedores e maior controle arquitetural.

## 4.1 Estratégia recomendada para entendimento do turno

### Conclusão executiva

A melhor prática atual para este projeto não é continuar expandindo `if/else` por stack para entender o que o usuário quis dizer.

A abordagem recomendada é um modelo híbrido:

- `guardrails` determinísticos para `policy`, `auth` e `precedence`;
- um classificador semântico com saída estruturada;
- geração prévia de candidatos de `capability` antes da decisão da LLM;
- roteamento determinístico para a stack depois da classificação;
- memória curta explícita para follow-ups elípticos.

### Por que não usar heurística como estratégia principal

Heurísticas locais continuam úteis para:

- segurança;
- regras duras;
- fallback conservador;
- formatação da resposta;
- compatibilidade temporária.

Mas elas são fracas como mecanismo principal de interpretação porque:

- escalam mal com sinônimos e variações naturais;
- geram drift entre stacks;
- ficam frágeis a follow-ups curtos;
- degradam a experiência para um comportamento “robótico”.

### Padrão alvo

O padrão alvo para o EduAssist é:

1. gerar um pequeno conjunto de `capabilities` candidatas;
2. pedir que uma LLM rápida escolha entre elas em schema rígido;
3. consolidar o resultado em um `TurnFrame` canônico;
4. deixar cada stack resolver do jeito que faz melhor.

Estado atual do projeto:

- esse desenho já foi implementado para a primeira onda de capabilities de FAQ pública e consultas protegidas de maior recorrência;
- o próximo ganho de ROI vem menos da arquitetura-base e mais da ampliação do catálogo canônico e das evals E2E sobre o novo contrato.

### Ajuste por stack

- `python_functions`: melhor como executor determinístico do `TurnFrame`.
- `langgraph`: melhor como workflow stateful para follow-up e branching.
- `llamaindex`: melhor quando o `TurnFrame` já restringe qual engine documental usar.
- `specialist_supervisor`: melhor quando entra depois da classificação, para casos ambíguos, compostos ou de maior valor.

## 5. Retrieval

### Estratégia escolhida para o baseline forte

- `hybrid retrieval`

Componentes:

- `Qdrant` como engine principal de dense + sparse retrieval
- PostgreSQL Full Text Search para plano lexical e filtros relacionais
- reranking

### Banco vetorial recomendado

- `Qdrant`

Motivo:

- oferece hybrid search, multivectors e estratégias de late interaction, o que o torna mais forte do que usar apenas `pgvector` como plano principal;
- roda localmente em container com baixo atrito, o que combina com o objetivo `local-first`;
- separa o plano de retrieval do banco transacional sem exigir infraestrutura pesada demais.

### Papel de `pgvector`

Decisão:

- manter `pgvector` apenas como fallback experimental, utilidade local e comparação de baseline;
- não tratá-lo como engine principal do produto.

### Parsing e preparação documental

Tecnologia recomendada:

- `Docling`

Motivo:

- parsing multimodal e forte entendimento de PDF, layout, reading order e tabelas;
- capacidade de execução local, importante para dados sensíveis e ambiente controlado;
- encaixa muito bem na fase de ingestão institucional deste projeto.

### Contextual Retrieval

Recomendação:

- incorporar a ideia de `Contextual Retrieval` no pipeline de chunking e indexação;
- útil para documentos escolares longos com forte dependência de contexto institucional.

### GraphRAG

Decisão:

- não usar como padrão cego para todas as consultas;
- adotar `Microsoft GraphRAG` como modo avançado de recuperação para perguntas globais, locais e multi-documento complexas;
- habilitar somente depois que o baseline híbrido estiver medido e quando houver ganho comprovado nos evals.
- manter uma trilha experimental separada do runtime principal para benchmark seletivo, usando o corpus institucional publico e comparando `basic`, `local`, `global` e `drift` contra o baseline atual.

Motivo:

- a documentação do GraphRAG mostra modos distintos como `Global Search`, `Local Search`, `DRIFT Search` e `Basic Search`;
- isso o torna valioso para raciocínio sobre o corpus como um todo, mas desnecessário para perguntas simples que já são bem resolvidas por retrieval híbrido.
- para um corpus majoritariamente em portugues, o benchmark principal deve preferir indexacao `standard`; inferencia a partir da documentacao oficial e do CLI atual: o modo `fast` usa extracao NLP padrao `regex_english`, o que tende a ser mais adequado a ingles do que ao nosso corpus escolar.
- a documentacao oficial tambem deixa claro que o `GraphRAG` usa `LiteLLM`, aceita modelos alem de OpenAI e pode operar via proxy APIs como `Ollama`, desde que o provider consiga devolver saídas estruturadas de forma confiavel.

## 6. Dados estruturados

Decisão:

- não usar geração livre de SQL pelo modelo no MVP;
- usar tools fechadas como `get_student_grades`, `get_financial_summary`, `get_school_calendar`.

Benefícios:

- auditabilidade;
- previsibilidade;
- menor superfície de vazamento;
- maior aderência à policy.

## 7. Segurança de contexto

Medidas:

- documentos filtrados por visibilidade antes do contexto;
- payload mínimo para tools;
- nada de contexto bruto com tabelas inteiras;
- negação explícita quando policy não permitir.

## 8. Evals

A literatura e a documentação atual reforçam que sistemas de IA confiáveis exigem avaliação contínua.

Para este projeto:

- evals offline com datasets escolares;
- evals online em tráfego de teste;
- casos adversariais;
- groundedness;
- negação correta;
- teste de regressão ao trocar modelo.

## 9. Padrões emergentes

### MCP

Útil em duas frentes distintas:

- no produto, como padrão emergente para integrações futuras, sem virar pilar do MVP;
- no workflow de desenvolvimento, como meio oficial de consultar documentação da OpenAI diretamente no editor e no Codex.

### A2A

Relevante como tendência de interoperabilidade, porém não prioritário para o MVP.

### AGENTS.md, skills e custom agents

Para o desenvolvimento deste repositório, eles devem ser tratados como recursos de engenharia, não como componentes do runtime:

- `AGENTS.md` como camada principal de instruções locais;
- `skills` para workflows repetíveis e sincronização documental;
- `custom agents` estreitos e opinados para pesquisa e revisão especializada.

## 10. Escolhas finais recomendadas

- modelo principal: `GPT-5.4`
- benchmark secundário: `Gemini 2.5 Pro`
- orquestração principal: `LangGraph`
- trilha OpenAI-native quando aplicável: `Responses API + Agents SDK`
- parsing documental: `Docling`
- retrieval baseline: `Qdrant + PostgreSQL FTS + reranking`
- retrieval avançado: `late interaction` e multivectors em `Qdrant`
- GraphRAG: `Microsoft GraphRAG` apenas em fluxos com ganho medido
- dados estruturados: tools determinísticas
- avaliação: datasets + evals contínuos
- segurança: `OPA + RLS + audit trail`
- workflow de engenharia: `AGENTS.md + Docs MCP + skills + custom agents`
- entendimento do turno: `semantic router` compartilhado + adapters por stack

## 11. Fontes pesquisadas

- OpenAI Models: https://developers.openai.com/api/docs/models
- OpenAI Retrieval: https://developers.openai.com/api/docs/guides/retrieval
- OpenAI Evals: https://developers.openai.com/api/docs/guides/evals
- OpenAI MCP: https://developers.openai.com/api/docs/mcp
- OpenAI Responses API: https://developers.openai.com/api/docs/guides/migrate-to-responses
- OpenAI Agents SDK: https://openai.github.io/openai-agents-python/quickstart/
- OpenAI Structured Outputs: https://openai.com/index/introducing-structured-outputs-in-the-api/
- OpenAI Guardrails: https://openai.github.io/openai-guardrails-js/quickstart/
- Codex AGENTS.md: https://developers.openai.com/codex/guides/agents-md
- Codex MCP: https://developers.openai.com/codex/mcp
- Codex Skills: https://developers.openai.com/codex/skills
- Codex Subagents: https://developers.openai.com/codex/subagents
- Docs MCP: https://developers.openai.com/learn/docs-mcp
- LangGraph overview: https://docs.langchain.com/oss/python/langgraph/overview
- LangGraph custom workflows: https://docs.langchain.com/oss/python/langchain/multi-agent/custom-workflow
- LangGraph memory: https://docs.langchain.com/oss/python/langgraph/add-memory
- Microsoft GraphRAG: https://microsoft.github.io/graphrag/
- Docling: https://docling-project.github.io/docling/
- Anthropic Contextual Retrieval: https://www.anthropic.com/engineering/contextual-retrieval
- Vertex grounding: https://docs.cloud.google.com/vertex-ai/generative-ai/docs/grounding/grounding-with-vertex-ai-search
- PostgreSQL Full Text Search: https://www.postgresql.org/docs/current/textsearch.html
- pgvector: https://github.com/pgvector/pgvector
- Qdrant: https://qdrant.tech/documentation/concepts/hybrid-queries/
- OPA: https://www.openpolicyagent.org/docs
- Keycloak Authorization Services: https://www.keycloak.org/docs/latest/authorization_services/index.html
- Telegram Bot API: https://core.telegram.org/bots/api
- Telegram Login/OIDC: https://core.telegram.org/bots/telegram-login
- Telegram Secret Chats/E2E: https://core.telegram.org/api/end-to-end
