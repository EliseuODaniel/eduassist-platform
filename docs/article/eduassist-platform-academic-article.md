# EduAssist Platform: arquitetura segura e local-first para atendimento escolar com IA conversacional via Telegram

## Resumo

Este artigo apresenta a `EduAssist Platform`, uma proposta arquitetural e uma implementação funcional de referência para atendimento escolar com IA conversacional, orientada a uma escola fictícia de ensino médio. O sistema combina atendimento público e consultas protegidas via Telegram com dados inteiramente mockados, mas armazenados e operados sobre infraestrutura real. O problema central tratado é a tensão entre flexibilidade conversacional e governança de acesso em um domínio que reúne informações institucionais, acadêmicas, financeiras e operacionais. Para responder a esse desafio, a plataforma foi organizada com separação explícita entre canal de entrada, regras de negócio, orquestração de IA, plano transacional, plano de retrieval, observabilidade e operação humana. A solução emprega `FastAPI`, `LangGraph`, `Qdrant`, `PostgreSQL`, `Keycloak`, `OPA`, `MinIO` e uma pilha de observabilidade com `OpenTelemetry`, `Tempo`, `Loki`, `Prometheus` e `Grafana`. O trabalho descreve requisitos do domínio, decisões arquiteturais, estratégia de IA, mecanismos de segurança, dados mockados, operação local e plano experimental. Também registra o estado real da implementação, incluindo FAQ pública, calendário, consultas protegidas, `RLS`, handoff humano, suites de regressão e gate operacional de prontidão. Como continuidade, é mantida uma trilha seletiva para benchmark de `GraphRAG`, já preparada no repositório e compatível tanto com provider remoto quanto com endpoint local compativel com OpenAI.

**Palavras-chave:** IA conversacional; Telegram; segurança da informação; atendimento escolar; RAG; GraphRAG.

## Abstract

This paper presents `EduAssist Platform`, a reference implementation and architectural proposal for school service automation with conversational AI, targeting a fictional high school environment. The system combines public service and protected queries through Telegram while using fully mocked data stored on real infrastructure. The central challenge addressed is the tension between conversational flexibility and access governance in a domain that concentrates institutional, academic, financial, and operational information. To address this problem, the platform is organized with explicit separation between channel handling, business rules, AI orchestration, transactional storage, retrieval layer, observability, and human handoff. The solution adopts `FastAPI`, `LangGraph`, `Qdrant`, `PostgreSQL`, `Keycloak`, `OPA`, `MinIO`, and an observability stack based on `OpenTelemetry`, `Tempo`, `Loki`, `Prometheus`, and `Grafana`. The paper describes domain requirements, architectural choices, AI strategy, security mechanisms, mock-data design, local-first operation, and the evaluation plan. It also reports the current implementation status, including public FAQ, calendar responses, protected academic and financial queries, `RLS`, human handoff, regression suites, and an operational readiness gate. As future work, a selective `GraphRAG` benchmark path is maintained in the repository and can be executed either with a remote provider or a local OpenAI-compatible endpoint.

**Keywords:** conversational AI; Telegram; information security; school service; retrieval-augmented generation; GraphRAG.

## 1. Introdução

Escolas operam fluxos contínuos de atendimento relacionados a matrículas, calendário letivo, regras institucionais, comunicação com famílias, desempenho acadêmico, cobrança e suporte administrativo. Em muitos casos, esses fluxos se distribuem de forma fragmentada entre secretaria, coordenação, financeiro e canais digitais pouco integrados. Como consequência, a instituição acumula gargalos, inconsistência de respostas e baixa rastreabilidade.

O avanço recente dos modelos de linguagem torna atraente a ideia de um chatbot escolar capaz de responder perguntas em linguagem natural e intermediar acesso a dados internos. No entanto, esse domínio impõe uma restrição crítica: nem toda pergunta deve ser tratada como FAQ pública. Informações sobre notas, frequência, contratos, faturas, vínculos familiares ou tickets operacionais dependem de autenticação, autorização contextual e trilha auditável. Portanto, um chatbot escolar não pode ser desenhado apenas como uma interface generativa sobre documentos, nem como um agente autônomo com acesso amplo às bases internas.

Este trabalho parte dessa constatação e propõe uma plataforma de atendimento escolar com IA em que a camada conversacional é subordinada a regras explícitas de segurança, identidade, retrieval e governança. Em vez de assumir a IA como fonte primária de decisão, a arquitetura define limites claros entre plano documental, plano transacional, tools determinísticas, políticas de acesso e handoff humano.

O objetivo é duplo. Em termos práticos, construir uma base robusta para demonstração e operação local de um ecossistema escolar fictício. Em termos acadêmicos, oferecer um artefato de arquitetura aplicada capaz de sustentar pesquisa, avaliação e evolução controlada do uso de IA conversacional em contexto escolar.

## 2. Contexto, requisitos e problema de pesquisa

O contexto de uso da plataforma é uma escola fictícia de ensino médio com múltiplos perfis:

- responsáveis legais;
- alunos;
- professores;
- secretaria;
- financeiro;
- coordenação;
- direção;
- operadores do sistema.

Esses perfis compartilham o mesmo canal de entrada, mas não o mesmo direito de acesso. Um responsável pode consultar dados de alunos vinculados, um aluno apenas os próprios dados, um professor apenas turmas atribuídas e o setor financeiro apenas informações compatíveis com seu papel. Ao mesmo tempo, parte relevante do atendimento permanece pública, como processos de matrícula, calendário institucional e regras gerais de atendimento digital.

Diante disso, o problema de pesquisa pode ser formulado da seguinte forma: como projetar uma plataforma de atendimento escolar com IA que preserve naturalidade conversacional sem abrir mão de autenticação, autorização, grounding, auditabilidade e operação local reproduzível?

Para responder a essa questão, o projeto adota os seguintes requisitos centrais:

- atendimento via Telegram como canal principal;
- separação estrita entre conteúdo público, autenticado e sensível;
- inexistência de acesso direto da LLM ao banco;
- uso de dados 100% mockados sobre infraestrutura real;
- observabilidade ponta a ponta desde a fase local;
- reprodutibilidade por `Docker Compose`;
- caminho explícito para avaliação comparativa entre retrieval híbrido e `GraphRAG`.

## 3. Metodologia de projeto

A metodologia adotada combina engenharia orientada a arquitetura com implementação incremental baseada em gates operacionais. Em vez de começar pela interface conversacional e “descobrir” segurança depois, o trabalho foi conduzido em fases que priorizaram fundação técnica, identidade, autorização, dados mockados, retrieval, operação humana e observabilidade.

O processo seguiu quatro princípios:

1. `local-first`: tudo o que fosse essencial ao sistema deveria rodar localmente, inclusive autenticação, retrieval, storage, métricas e tracing.
2. `security-by-default`: todo fluxo sensível deveria nascer com policy explícita, negação segura e trilha de auditoria.
3. `controlled AI`: a IA deveria operar por tools e contratos, não por acesso irrestrito a dados.
4. `evidence-driven evolution`: capacidades avançadas, como `GraphRAG`, só deveriam ser consideradas para o runtime principal após benchmark comparativo e evidência de ganho.

Essa metodologia resultou numa base funcional organizada em documentação formal, suites de teste, operações de backup e restore, benchmark seletivo de retrieval avançado e um gate final de readiness.

## 4. Arquitetura da plataforma

### 4.1 Visão geral

A solução foi implementada como um monólito modular com serviços auxiliares, o que reduz complexidade operacional local sem eliminar separação lógica entre domínios. A topologia principal contém:

- `telegram-gateway`;
- `api-core`;
- `ai-orchestrator`;
- `worker`;
- `admin-web`;
- `postgres`;
- `qdrant`;
- `redis`;
- `minio`;
- `keycloak`;
- `opa`;
- `otel-collector`;
- `tempo`, `loki`, `prometheus` e `grafana`.

Essa topologia foi escolhida para preservar três fronteiras essenciais:

- o canal de entrada não concentra regras de domínio;
- a camada de IA não opera diretamente sobre o banco;
- o plano transacional é distinto do plano de retrieval.

### 4.2 Fluxo público

No fluxo público, o usuário envia a mensagem ao bot do Telegram. O `telegram-gateway` valida o webhook, aplica idempotência, correlaciona o evento e o encaminha ao `ai-orchestrator`. O orquestrador classifica a intenção, seleciona o modo de resposta e, quando necessário, aciona retrieval híbrido sobre o corpus institucional indexado em `Qdrant` e apoiado por `PostgreSQL Full Text Search`. A resposta final retorna ao usuário com grounding e citações.

### 4.3 Fluxo protegido

No fluxo protegido, o `api-core` verifica o vínculo entre a conta do Telegram e a identidade escolar. A partir daí, a decisão de acesso passa por `OPA`, e o banco reforça esse resultado com `PostgreSQL RLS`. Services determinísticos consultam apenas os dados permitidos e devolvem payloads mínimos. O `ai-orchestrator` recebe somente o contexto estritamente necessário para formular a resposta. Esse desenho evita a delegação de autorização à LLM.

### 4.4 Operação humana

Quando a conversa exige intervenção humana, o sistema aciona handoff controlado. O ticket entra na fila operacional, com prioridade e SLA mockados, podendo ser visualizado no `admin-web`. O painel administrativo já permite filtrar a fila, paginar tickets, navegar no transcript, registrar notas de operação e acompanhar a saúde da fila por setor e operador.

## 5. Estratégia de IA e recuperação de conhecimento

### 5.1 Orquestração governada

A plataforma foi desenhada deliberadamente para evitar o uso de múltiplos agentes autônomos livres como arquitetura principal. Em seu lugar, adota-se um `orquestrador governado` implementado com `LangGraph`, em que os caminhos possíveis são definidos por estado, tools, políticas e contratos de saída.

Esse orquestrador pode operar em diferentes modos:

- `hybrid_retrieval`;
- `structured_tool`;
- `handoff`;
- `deny`;
- `clarify`;
- trilha avançada de `graph_rag`.

### 5.2 Retrieval baseline

O baseline documental usa:

- `Qdrant` como engine principal de dense retrieval;
- `PostgreSQL Full Text Search` para plano lexical e filtros complementares;
- grounding com citações no texto final.

Essa combinação foi preferida ao uso de `pgvector` como engine principal porque permite maior especialização do plano de retrieval sem transferir ao banco transacional a responsabilidade pela camada semântica.

### 5.3 Dados estruturados

Consultas acadêmicas, financeiras e docentes não usam geração livre de SQL. Em vez disso, o sistema chama tools determinísticas como:

- `get_student_academic_summary`;
- `get_student_attendance`;
- `get_student_grades`;
- `get_financial_summary`;
- `get_teacher_schedule`;
- `create_support_ticket`;
- `handoff_to_human`.

Essa escolha melhora previsibilidade, auditabilidade e segurança.

### 5.4 GraphRAG como trilha seletiva

O trabalho assume que `GraphRAG` pode ser valioso para perguntas globais, locais e multi-documento complexas, mas não o trata como padrão automático. A documentação oficial da ferramenta mostra modos distintos como `basic`, `local`, `global` e `drift`, o que favorece um uso comparativo e seletivo.

Por isso, a implementação atual mantém `GraphRAG` numa trilha experimental isolada em [tools/graphrag-benchmark](/home/edann/projects/eduassist-platform/tools/graphrag-benchmark). O benchmark já possui workspace bootstrapado, dataset de comparação e runner para contrastar o baseline atual com respostas de `GraphRAG`. A incorporação dessa técnica ao runtime principal permanece condicionada a benchmark completo e ganho medido.

## 6. Segurança, identidade e governança

O modelo de segurança integra `Keycloak`, `OPA` e `PostgreSQL RLS`. O `Keycloak` atua como provedor de identidade, o `OPA` decide políticas contextuais de acesso e o banco reforça a decisão com `RLS`.

As premissas de segurança são:

- `default deny`;
- menor privilégio;
- contexto mínimo para o modelo;
- logs estruturados sem PII crua;
- auditoria de decisões e acessos sensíveis;
- segregação entre papel administrativo e papel de runtime no banco.

O Telegram não é tratado como fronteira suficiente de segurança. Perguntas públicas podem ser respondidas sem autenticação, mas consultas sensíveis exigem vínculo prévio entre a conta Telegram e a identidade escolar, realizado por meio de portal autenticado.

No estado atual do projeto, o banco já aplica `RLS` sobre tabelas acadêmicas, financeiras, auxiliares e de atendimento humano. Além disso, as notas internas do operador não aparecem no detalhe do handoff para o solicitante final, preservando segregação entre escopo pessoal e escopo global interno.

## 7. Modelo de dados e dados mockados

O modelo de dados foi distribuído em schemas especializados:

- `identity`;
- `school`;
- `academic`;
- `finance`;
- `calendar`;
- `documents`;
- `conversation`;
- `audit`.

Essa modelagem permite manter coerência entre usuários, papéis, turmas, matrículas, notas, frequência, contratos, faturas, eventos, documentos, conversas e handoffs.

Os dados são integralmente mockados, mas operam sob premissas realistas de consistência. A geração é feita por ferramentas próprias em `tools/mockgen`, com seeds determinísticas e cenários de carga operacional incremental. Isso permite demonstrar o sistema em ambiente controlado sem recorrer a dados reais.

## 8. Implementação atual e operação local

Um dos objetivos centrais do projeto foi provar que uma plataforma desse tipo pode ser executada de forma robusta em ambiente local. No momento da redação deste artigo, a solução já oferece:

- FAQ pública via Telegram;
- calendário escolar estruturado;
- vínculo Telegram-usuário;
- consultas protegidas acadêmicas, financeiras e docentes;
- enforcement por `OPA` e `RLS`;
- painel administrativo autenticado;
- handoff humano com prioridade e SLA mockado;
- observabilidade distribuída com traces, métricas e logs;
- backup e restore de verificação para `Postgres`, `Qdrant` e `MinIO`;
- suites de regressão e gate final de prontidão.

O comando [release-readiness.md](/home/edann/projects/eduassist-platform/docs/operations/release-readiness.md) já passa no modo padrão. Isso indica que o sistema está pronto para demo e operação local, ainda que o benchmark completo de `GraphRAG` continue pendente de provider configurado.

## 9. Avaliação e evidências

O projeto já incorpora evidência operacional em três camadas:

1. `smoke tests` ponta a ponta para os fluxos principais;
2. regressões de autorização e cenários adversariais;
3. evals formais do `ai-orchestrator`.

Esses mecanismos verificam, entre outros pontos:

- groundedness com citações;
- negação segura em fluxos protegidos;
- ambiguidade controlada para responsáveis com múltiplos alunos;
- resistência a tentativas de exfiltração e prompt disclosure;
- integridade da observabilidade;
- uso de papel não-superuser no runtime do banco;
- reforço de `RLS` nas tabelas sensíveis.

Como complemento, a trilha de benchmark seletivo de `GraphRAG` produz baseline comparativo e prepara o terreno para avaliação futura de retrieval avançado.

## 10. Limitações e trabalhos futuros

Apesar do estágio avançado da implementação, permanecem limitações relevantes:

- o corpus documental público ainda é pequeno;
- o parsing local atual usa baseline `markdown`, embora a arquitetura preserve espaço para `Docling`;
- o benchmark completo de `GraphRAG` ainda não foi executado;
- o caminho para Kubernetes local ainda não foi priorizado sobre o fluxo estável em `Docker Compose`;
- o uso de dados mockados limita a avaliação de ruído institucional real.

Como trabalhos futuros, destacam-se:

- executar o benchmark completo de `GraphRAG` com chave válida;
- ampliar o corpus e comparar qualidade entre provedores de LLM;
- expandir as políticas de retenção e cenários de recuperação;
- evoluir a exportação acadêmica e a versão final em `.docx`.

## 11. Conclusão

Este artigo apresentou a `EduAssist Platform` como uma arquitetura de referência para atendimento escolar com IA em contexto sensível. A principal contribuição do trabalho é mostrar que a camada conversacional precisa ser apenas um componente de uma plataforma maior, subordinada a identidade, políticas de acesso, services determinísticos, observabilidade e operação humana.

Ao separar canal, domínio, retrieval, orquestração, enforcement e handoff, o projeto construiu uma base robusta para uso local, demonstração técnica e pesquisa aplicada. O sistema já funciona em ambiente local com autenticação, autorização, retrieval híbrido, consultas protegidas, handoff humano, auditoria e gates de readiness.

O fechamento estrito do trabalho depende apenas da execução completa do benchmark seletivo de `GraphRAG`. Até lá, a plataforma já se sustenta como um artefato técnico coerente, reproduzível e academicamente defensável para o estudo de IA conversacional segura em contexto escolar.

## Referências

ANTHROPIC. Contextual retrieval. Disponível em: <https://www.anthropic.com/engineering/contextual-retrieval>. Acesso em: 23 mar. 2026.

GOOGLE CLOUD. Grounding with Vertex AI Search. Disponível em: <https://docs.cloud.google.com/vertex-ai/generative-ai/docs/grounding/grounding-with-vertex-ai-search>. Acesso em: 23 mar. 2026.

KEYCLOAK. Authorization services. Disponível em: <https://www.keycloak.org/docs/latest/authorization_services/index.html>. Acesso em: 23 mar. 2026.

LANGCHAIN. LangGraph overview. Disponível em: <https://docs.langchain.com/oss/python/langgraph/overview>. Acesso em: 23 mar. 2026.

MICROSOFT. GraphRAG documentation. Disponível em: <https://microsoft.github.io/graphrag/>. Acesso em: 23 mar. 2026.

OPENAI. Evals guide. Disponível em: <https://developers.openai.com/api/docs/guides/evals>. Acesso em: 23 mar. 2026.

OPENAI. Models. Disponível em: <https://developers.openai.com/api/docs/models>. Acesso em: 23 mar. 2026.

OPENAI. Responses API migration guide. Disponível em: <https://developers.openai.com/api/docs/guides/migrate-to-responses>. Acesso em: 23 mar. 2026.

OPEN POLICY AGENT. Documentation. Disponível em: <https://www.openpolicyagent.org/docs>. Acesso em: 23 mar. 2026.

POSTGRESQL. Full text search. Disponível em: <https://www.postgresql.org/docs/current/textsearch.html>. Acesso em: 23 mar. 2026.

QDRANT. Hybrid queries. Disponível em: <https://qdrant.tech/documentation/concepts/hybrid-queries/>. Acesso em: 23 mar. 2026.

TELEGRAM. Bot API. Disponível em: <https://core.telegram.org/bots/api>. Acesso em: 23 mar. 2026.

TELEGRAM. End-to-end encryption and secret chats. Disponível em: <https://core.telegram.org/api/end-to-end>. Acesso em: 23 mar. 2026.
diff? We can use this as article file. Need export tool. Need maybe metadata YAML. Let's patch. Also update docs/README and maybe README index. Let's craft script. Need handle markdown lines. Use python-docx. We'll need maybe check if dependency installs. Script could parse file line by line.
Let's create metadata YAML with placeholders. Could be:
title etc author "Autor a definir". Another fields maybe institution/program/advisor/location/date. Fine.
Script algorithm:
load yaml metadata.
create Document()
set defaults for Normal, Heading1 etc.
cover page: centered title, subtitle, author, institution, program, location/date.
add page break.
Then parse markdown:
for each line:
 skip title line if starts with '# ' maybe since already on cover and add maybe again as article title? perhaps maybe keep after cover? Could start from `## Resumo` etc.
 handle blank lines accumulate paragraph.
 if line starts with '## ' or '### ' etc create heading
 if line matches bullet `- ` create bullet style `List Bullet`
 if line matches ordered `1. ` create list number style maybe `List Number`
 bold? use simple clean function remove markdown.
 support `**text:**` etc just strip markup and convert links.
 Maybe preserve in-line code ticks and emphasis by removing formatting. That's enough.
 maybe generate docx file in artifacts/article. Could include metadata in core properties.
 maybe add abstract and keywords from metadata? Actually article markdown already has. fine.

Need maybe create `tools/article-export/pyproject.toml`, `uv lock`. Add target to Makefile `article-docx` maybe also `article-docx-draft`? maybe just formal article. Could also add `article-docx- draft` but not needed.
Need maybe maybe add `tools/article-export/README.md` maybe maybe not necessary. But could helpful. Could skip maybe use docs. But nice.
Need maybe create `docs/article/article-export-metadata.yaml`. Then actual output path `artifacts/article/eduassist-platform-academic-article.docx`. Maybe commit binary? Need use command to generate after script and commit? It's an artifact generated. We can commit it if user asked save. Hmm maybe yes. But binary commit might be okay. We'll decide later after generate. We'll need check size. Probably small (<50KB). Could commit. Since user asked "save everything" earlier. Let's commit .docx maybe yes.
Need maybe update `docs/article/refactor-outline.md` state mentions article and docx pipeline.
Need maybe update `docs/README.md` and root README index to include article formal and maybe docx pipeline doc.
Maybe also add `docs/article/README` no need.

Let's patch accordingly. Need maybe maybe use apply_patch large add file. Let's do.
Need maybe maintain ascii only. Our content can be Portuguese without accents? Current repo docs mostly ascii removed accents. We should use ascii. We'll keep ascii.
Let's patch with article file content, metadata file, tool project, script, Makefile, docs updates. Since large maybe okay.
 
