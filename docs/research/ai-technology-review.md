# Pesquisa de Tecnologias de IA para o Projeto

## 1. Objetivo

Mapear tecnologias atuais e decidir a estratégia de IA mais adequada para uma plataforma escolar com dados documentais e estruturados, operando via Telegram e com forte necessidade de segurança e governança.

## 2. Conclusão executiva

A melhor abordagem para este projeto não é um sistema de agentes autônomos livres. A melhor abordagem é um `orquestrador governado`, com:

- retrieval híbrido;
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

### Tecnologia escolhida

- `LangGraph`

Justificativa:

- suporte a workflows com estado;
- boa aderência a tool calling;
- facilidade para human-in-the-loop;
- melhor controle do que arquiteturas “multiagente” abertas.

## 5. Retrieval

### Estratégia escolhida

- `hybrid retrieval`

Componentes:

- PostgreSQL Full Text Search
- `pgvector`
- reranking

### Contextual Retrieval

Recomendação:

- incorporar a ideia de `Contextual Retrieval` no pipeline de chunking e indexação;
- útil para documentos escolares longos com forte dependência de contexto institucional.

### GraphRAG

Decisão:

- não usar como padrão inicial;
- considerar apenas em fase posterior, se surgirem consultas relacionais complexas multi-documento.

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
- orquestração: `LangGraph`
- interface OpenAI preferida quando aplicável: `Responses API`
- retrieval: `FTS + pgvector + reranking`
- dados estruturados: tools determinísticas
- avaliação: datasets + evals contínuos
- segurança: `OPA + RLS + audit trail`
- workflow de engenharia: `AGENTS.md + Docs MCP + skills + custom agents`

## 11. Fontes pesquisadas

- OpenAI Models: https://developers.openai.com/api/docs/models
- OpenAI Retrieval: https://developers.openai.com/api/docs/guides/retrieval
- OpenAI Evals: https://developers.openai.com/api/docs/guides/evals
- OpenAI MCP: https://developers.openai.com/api/docs/mcp
- OpenAI Responses API: https://developers.openai.com/api/docs/guides/migrate-to-responses
- Codex AGENTS.md: https://developers.openai.com/codex/guides/agents-md
- Codex MCP: https://developers.openai.com/codex/mcp
- Codex Skills: https://developers.openai.com/codex/skills
- Codex Subagents: https://developers.openai.com/codex/subagents
- Docs MCP: https://developers.openai.com/learn/docs-mcp
- LangGraph overview: https://docs.langchain.com/oss/python/langgraph/overview
- Anthropic Contextual Retrieval: https://www.anthropic.com/engineering/contextual-retrieval
- Vertex grounding: https://docs.cloud.google.com/vertex-ai/generative-ai/docs/grounding/grounding-with-vertex-ai-search
- PostgreSQL Full Text Search: https://www.postgresql.org/docs/current/textsearch.html
- pgvector: https://github.com/pgvector/pgvector
- OPA: https://www.openpolicyagent.org/docs
- Keycloak Authorization Services: https://www.keycloak.org/docs/latest/authorization_services/index.html
- Telegram Bot API: https://core.telegram.org/bots/api
- Telegram Login/OIDC: https://core.telegram.org/bots/telegram-login
- Telegram Secret Chats/E2E: https://core.telegram.org/api/end-to-end
