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
- reranking em duas etapas

Estado atual do baseline:

- `late interaction` com `answerdotai/answerai-colbert-small-v1`
- `cross-encoder` multilíngue com `jinaai/jina-reranker-v2-base-multilingual`

Observação arquitetural:

- o débito original citava `bge-reranker-v2`, mas no baseline atual a escolha foi `jinaai/jina-reranker-v2-base-multilingual` por melhor adequação ao corpus escolar em português e suporte direto no stack atual `FastEmbed/Qdrant`.

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

## 7.1 Contexto longo local com Gemma

Para o baseline local atual, a recomendação não é perseguir imediatamente técnicas frontier de compressão de `KV cache`.

Leitura atual:

- `Gemma 4 E4B` oferece uma janela nativa muito maior do que a atualmente exposta no serving local;
- o repositório, porém, opera em modo `retrieval-first`, com histórico curto, `TurnFrame`, `FocusFrame` e evidência selecionada;
- por isso, o principal limitante hoje tende a ser `packing`, memória curta, retrieval e composição grounded, e não apenas a memória bruta de `KV cache`.

Implicação arquitetural:

- primeiro: telemetria de uso real de contexto;
- depois: packing de evidência, memória episódica e tuning de retrieval/rerank;
- só depois: aumento gradual de `ctx-size`;
- e apenas como trilha posterior: avaliação de `TurboQuant`.

Estado atual no repositório:

- telemetria de contexto já entrou no baseline compartilhado;
- packing por budget de tokens já está ativo no `turn_router` e no `public_answer_composer`;
- os adapters locais e a camada de answer experience já começaram a convergir para o mesmo baseline de packing;
- a memória episódica de curto prazo já aproveita `recent_tool_calls` e `slot_memory` para reforçar follow-up e carryover;
- retrieval por capability já entrou no baseline com política compartilhada de `retrieval_profile`, `top-k` e categoria antes do dispatch por stack;
- o retrieval híbrido já aplica rerank semântico em duas camadas, combinando `late interaction` e `cross-encoder` antes da resposta grounded;
- a próxima fronteira de ROI continua sendo memória episódica e tuning de retrieval, não compressão avançada de `KV cache`.

### Avaliação de `TurboQuant`

- forte como técnica de compressão de `KV cache`;
- promissora para Gemma em contextos realmente longos;
- mas ainda de baixo ROI imediato para o baseline local atual, que não depende de prompts enormes na maior parte dos turnos.

### Avaliação de `TriAttention`

- forte como pesquisa para `long reasoning`;
- pior ajuste pragmático para o projeto hoje, por depender de stack e calibração mais especializados;
- deve ser tratada como trilha experimental separada, não como próximo passo natural do baseline.

## 7.1 Observabilidade e identidade interna

Dois débitos antigos mudaram de status:

- `tail-based sampling OTEL`: resolvido no baseline local do collector;
- `SPIFFE/SPIRE`: a aplicação ficou `SPIFFE-ready` por bridge de identidade interna, mas o rollout completo da malha `SPIRE` continua sendo decisão de ambiente enterprise.

## 7.2 Avaliação local de `Qwen3-4B-Instruct-2507`

Para a máquina local-alvo do projeto, com `32 GB` de RAM e `8 GB` de VRAM, o melhor candidato adicional para benchmark local deixou de ser um segundo modelo hospedado e passou a ser um profile local alternativo em `llama.cpp`.

Decisão arquitetural:

- manter `Gemma 4 E4B` como baseline local do repositório;
- adicionar `Qwen3-4B-Instruct-2507` como profile experimental com feature flag explícita;
- comparar os dois na mesma stack, sob o mesmo harness e o mesmo dataset, antes de qualquer mudança de default.

Justificativa:

- o card oficial do `Qwen3-4B-Instruct-2507` traz bom desempenho em `IFEval`, `WritingBench`, `BFCL-v3`, `TAU` e benchmarks gerais de instrução;
- o ecossistema do `Qwen3` possui caminho claro para `GGUF` e `llama.cpp`;
- o artefato `Q5_K_M` fica dentro do envelope realista da GPU local;
- o modelo suporta apenas `non-thinking mode`, o que combina bem com o desenho grounded e determinístico do EduAssist.

Configuração experimental atual:

- profile: `qwen3_4b_instruct_local`
- runtime: `llama.cpp` com endpoint `OpenAI-compatible`
- artefato local: `bartowski/Qwen_Qwen3-4B-Instruct-2507-GGUF`
- arquivo padrão: `Qwen_Qwen3-4B-Instruct-2507-Q5_K_M.gguf`
- `ctx-size` inicial: `12288`

Boas práticas adotadas para o experimento:

- manter `Gemma` como baseline, sem troca silenciosa do default;
- usar a mesma stack `specialist_supervisor` para o A/B;
- não ativar modo de reasoning/thinking explícito;
- comparar qualidade, grounding, personalização, latência e robustez da resposta final, não só benchmark bruto de modelo.

Resultado do A/B local em `2026-04-17`:

- a primeira passada crua favoreceu `Qwen` em latência e disponibilidade, mas também expôs que os principais resíduos estavam acima da troca de modelo;
- a correção arquitetural seguinte introduziu um `answer surface refiner` validado primeiro no `specialist_supervisor` e depois no pós-processamento compartilhado das stacks non-specialist, preservando a resposta original sempre que a LLM não conseguisse verbalizar com segurança;
- no estado final da rodada, `gemma4e4b_local_postfix` fechou em `15/15`, `keyword_pass 15/15` e `quality 100.0`;
- `qwen3_4b_instruct_local` permaneceu melhor em latência, porém terminou em `quality 84.3` e `keyword_pass 8/15`;
- conclusão: `Gemma` continua como baseline operacional do repositório, e `Qwen` permanece como profile experimental com feature flag para benchmark e diagnóstico.

Padrão arquitetural adotado para o refino final:

- tentativa inicial de verbalização estruturada;
- fallback controlado em texto livre para modelos locais menos estáveis em schema;
- validação local obrigatória de fatos, escopo, nomes, datas, valores e intenção;
- preservação literal da resposta original quando o refino não passa na validação.

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
