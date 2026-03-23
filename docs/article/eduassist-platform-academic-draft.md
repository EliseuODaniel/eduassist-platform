# EduAssist Platform: proposta arquitetural de uma plataforma escolar segura, auditável e local-first com IA conversacional via Telegram

## Resumo

Este documento apresenta a proposta arquitetural e o estado atual de implementação da `EduAssist Platform`, uma plataforma de atendimento escolar com IA conversacional voltada a uma escola fictícia de ensino médio. O sistema combina atendimento público e consultas protegidas via Telegram, dados 100% mockados sobre infraestrutura real, controle de acesso em múltiplas camadas, observabilidade ponta a ponta e orquestração governada de modelos de linguagem. A proposta parte do reconhecimento de que chatbots escolares não podem ser tratados apenas como interfaces de FAQ, pois também precisam lidar com dados acadêmicos, financeiros e operacionais sujeitos a restrições de identidade, vínculo e finalidade. Para responder a esse problema, a plataforma foi estruturada com separação explícita entre canal, regras de negócio, orquestração de IA, plano transacional, plano de retrieval e operação humana. O texto descreve requisitos do domínio, arquitetura, estratégia de IA, modelo de segurança, dados mockados, operação local e plano experimental. Também registra o que já foi efetivamente implementado no repositório e o que permanece como trilha avançada, com destaque para o benchmark seletivo de `GraphRAG`, já preparado, mas ainda dependente de chave de API para execução completa.

## 1. Introdução

Instituições escolares concentram fluxos intensivos de atendimento relacionados a calendário letivo, matrículas, dúvidas institucionais, desempenho acadêmico, comunicação com famílias, cobrança e suporte administrativo. Em muitos cenários, essas interações são fragmentadas entre secretaria, coordenação, financeiro e canais informais, o que aumenta o custo operacional e reduz a previsibilidade do atendimento.

O uso de IA conversacional nesse domínio parece promissor, mas envolve um desafio central: a coexistência entre informação pública e informação sensível. Um bot escolar pode responder dúvidas sobre matrícula e calendário de forma aberta, mas não pode tratar do mesmo modo notas, frequência, contratos, boletos ou vínculos familiares. Isso exige uma arquitetura em que a camada de IA seja subordinada a políticas de acesso, contratos determinísticos e rastreabilidade.

Este trabalho propõe uma plataforma escolar conversacional que simula um ecossistema institucional completo de ensino médio com dados mockados, mas construída sobre infraestrutura real, autenticação efetiva, autorização contextual, auditoria e observabilidade. O sistema opera localmente em `Docker Compose`, utiliza o Telegram como canal principal, integra `Keycloak`, `OPA`, `PostgreSQL`, `Qdrant`, `MinIO` e uma camada de orquestração de IA controlada, com foco em segurança, grounding e reprodutibilidade.

## 2. Problema e motivação

O problema abordado por este projeto pode ser resumido em três tensões principais:

- escolas precisam de atendimento rápido, contínuo e multissetorial;
- usuários esperam linguagem natural e resposta contextual;
- dados escolares exigem controles fortes de identidade, vínculo e auditoria.

Uma solução centrada apenas em FAQ documental é insuficiente. Por outro lado, uma solução centrada em agentes autônomos com acesso amplo a dados é inadequada para um domínio com informação pessoal, acadêmica e financeira. A motivação do projeto é, portanto, projetar uma arquitetura que ofereça flexibilidade conversacional sem abrir mão de governança.

Além da motivação aplicada, o projeto também serve como base de pesquisa técnica em três frentes:

- avaliação de arquiteturas seguras para IA conversacional em contexto escolar;
- comparação entre retrieval híbrido e modos avançados como `GraphRAG`;
- construção de um ambiente local-first, auditável e reproduzível para experimentação.

## 3. Objetivos

### 3.1 Objetivo geral

Projetar e implementar uma plataforma robusta de atendimento escolar com IA conversacional, operando via Telegram, com dados mockados, infraestrutura real e forte controle de acesso.

### 3.2 Objetivos específicos

- responder perguntas institucionais com grounding e citações;
- permitir consultas protegidas de dados acadêmicos e financeiros mediante autenticação e autorização;
- separar explicitamente canal, domínio, IA, retrieval e enforcement de segurança;
- suportar handoff humano, fila operacional e observabilidade ponta a ponta;
- rodar integralmente em máquina local por meio de containers;
- preparar uma trilha de benchmark para avaliar `GraphRAG` de forma seletiva e comparativa.

## 4. Requisitos do domínio escolar

O domínio modelado representa uma escola fictícia de ensino médio com múltiplos perfis de acesso:

- responsável;
- aluno;
- professor;
- secretaria;
- financeiro;
- coordenação;
- direção;
- operador do sistema.

As capacidades esperadas incluem:

- FAQ institucional pública;
- calendário escolar público e autenticado;
- consulta de notas e frequência;
- consulta de situação financeira;
- consulta de horários e turmas;
- abertura de ticket e handoff para atendimento humano;
- operação interna com fila, SLA mockado e auditoria.

Os dados são integralmente mockados, porém coerentes entre si. Isso permite simular cenários próximos aos de produção sem expor informação real.

## 5. Arquitetura proposta

### 5.1 Visão geral

A solução foi estruturada como um monólito modular com workers auxiliares, privilegiando simplicidade operacional local sem sacrificar separação lógica entre responsabilidades. A topologia principal contém:

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
- `otel-collector`, `tempo`, `loki`, `prometheus` e `grafana`.

Essa organização reflete três separações fundamentais:

- o canal é desacoplado do domínio;
- a IA é desacoplada do banco;
- o plano transacional é desacoplado do plano de retrieval.

### 5.2 Fluxo público

No fluxo público, o `telegram-gateway` valida o webhook, normaliza a mensagem e a encaminha ao `ai-orchestrator`. O orquestrador classifica a intenção, seleciona o modo de resposta e, quando necessário, aciona retrieval híbrido sobre o corpus institucional indexado. A resposta final retorna ao Telegram com grounding documental e referências.

### 5.3 Fluxo protegido

No fluxo protegido, a mesma mensagem passa por resolução de identidade, verificação de vínculo e decisão de policy. O `api-core` consulta o `OPA`, injeta contexto de ator no banco e delega a services determinísticos. O modelo de linguagem recebe apenas o payload mínimo necessário para formulação da resposta. Essa separação impede que a LLM se torne um vetor de acesso direto a dados sensíveis.

## 6. Estratégia de IA

### 6.1 Princípio de orquestração

A abordagem adotada não é um sistema de agentes autônomos livres. O núcleo da solução é um `orquestrador governado`, implementado com `LangGraph`, em que os caminhos possíveis são explícitos e as capacidades do modelo são limitadas por tools, policies e contratos de saída.

### 6.2 Retrieval baseline

O baseline do projeto usa:

- `Qdrant` como motor principal de retrieval documental;
- `PostgreSQL Full Text Search` como componente lexical e relacional complementar;
- composição híbrida com grounding e citações.

Essa decisão foi tomada porque perguntas institucionais e de calendário são bem resolvidas por retrieval híbrido com baixo custo operacional, enquanto o banco transacional permanece responsável por dados estruturados.

### 6.3 Dados estruturados

Consultas acadêmicas, financeiras e docentes não são resolvidas por geração livre de SQL. Em vez disso, o sistema usa tools fechadas, como:

- `get_student_academic_summary`;
- `get_student_attendance`;
- `get_student_grades`;
- `get_financial_summary`;
- `get_teacher_schedule`;
- `create_support_ticket`;
- `handoff_to_human`.

Essa estratégia reduz superfície de vazamento e facilita auditoria.

### 6.4 GraphRAG como modo avançado

O projeto adota `GraphRAG` apenas como trilha avançada e seletiva. A justificativa é dupla:

- perguntas simples já são resolvidas adequadamente pelo baseline híbrido;
- modos globais, locais e multi-documento podem justificar `GraphRAG`, mas apenas quando os evals demonstrarem ganho real.

Na implementação atual, essa trilha já foi preparada como experimento separado em [tools/graphrag-benchmark](/home/edann/projects/eduassist-platform/tools/graphrag-benchmark), sem acoplar o produto principal a um custo ou complexidade ainda não validados.

## 7. Segurança da informação e controle de acesso

O modelo de segurança combina três camadas:

- `Keycloak` para identidade e papéis;
- `OPA` para decisão contextual de policy;
- `PostgreSQL RLS` para enforcement adicional na base transacional.

As premissas centrais são:

- `default deny`;
- menor privilégio;
- contexto mínimo para o modelo;
- auditoria explícita de decisões e acessos.

O Telegram é tratado apenas como canal, não como fronteira suficiente de segurança. Perguntas públicas podem ser respondidas sem autenticação, mas perguntas sensíveis exigem vínculo prévio entre a conta Telegram e a identidade escolar, realizado via portal autenticado.

No estado atual do sistema, o banco já aplica `RLS` em tabelas acadêmicas, financeiras, auxiliares e de atendimento humano. Além disso, o runtime dos serviços de aplicação utiliza um papel de banco não-superuser, separado do papel administrativo de migração e seed.

## 8. Modelo de dados e estratégia de dados mockados

O modelo de dados foi organizado em schemas separados:

- `identity`;
- `school`;
- `academic`;
- `finance`;
- `calendar`;
- `documents`;
- `conversation`;
- `audit`.

Essa organização permite modelar simultaneamente:

- usuários e identidades federadas;
- alunos, responsáveis, professores e turmas;
- notas, avaliações e frequência;
- contratos, invoices e pagamentos;
- calendário letivo e comunicados;
- documentos institucionais versionados;
- conversas, handoffs e trilha de auditoria.

Os dados são gerados por seeds determinísticas e ferramentas próprias em `tools/mockgen`. O objetivo é manter consistência entre vínculos familiares, matrículas, contratos, notas, eventos e filas humanas, criando um ecossistema crível para demonstração e testes.

## 9. Operação local, observabilidade e handoff humano

Um dos diferenciais do projeto é o foco `local-first`. A plataforma foi desenhada para rodar em máquina local via `Docker Compose`, inclusive com:

- autenticação real;
- retrieval real;
- bancos reais;
- storage real;
- observabilidade distribuída;
- backup e restore drill;
- fila humana operacional.

O sistema já conta com:

- `Tempo` para tracing distribuído;
- `Loki` para agregação de logs;
- `Prometheus` para métricas;
- `Grafana` para dashboards;
- painel `admin-web` com visão operacional, paginação, filtros, detalhe de transcript e monitoramento da fila humana.

O handoff humano já está implementado com prioridade, SLA mockado, atribuição de operador, auditoria de notas internas e separação entre escopo pessoal e escopo global.

## 10. Plano experimental e avaliação

O projeto foi estruturado para validar não apenas funcionalidade, mas também correção operacional e segurança. Para isso, o repositório já contém:

- smoke tests ponta a ponta;
- regressões de autorização;
- suíte adversarial de exfiltração e prompt disclosure;
- suíte formal de evals do orquestrador;
- gate operacional final em `make release-readiness`.

Esses mecanismos permitem verificar:

- groundedness com citações;
- negação correta de fluxos protegidos;
- ambiguidade controlada para responsáveis com múltiplos alunos;
- resistência a consultas maliciosas;
- integridade da observabilidade;
- funcionamento do runtime seguro no banco;
- estado geral de prontidão local.

Além disso, foi criada uma trilha específica para benchmark seletivo de `GraphRAG`, com dataset próprio, bootstrap automatizado do corpus institucional público e comparação com o baseline híbrido atual.

## 11. Estado atual da implementação

No momento da redação deste texto, o sistema já possui implementação funcional e validada nos seguintes pontos:

- atendimento público via Telegram;
- FAQ institucional com grounding;
- calendário escolar estruturado;
- vínculo Telegram-usuário via portal e `Keycloak`;
- consultas protegidas acadêmicas, financeiras e docentes;
- enforcement por `OPA` e `RLS`;
- painel operacional autenticado;
- handoff humano com fila e SLA mockado;
- tracing, métricas e logs centralizados;
- backup e restore de verificação;
- gates formais de readiness.

O gate [release-readiness.md](/home/edann/projects/eduassist-platform/docs/operations/release-readiness.md) já passa no modo padrão, o que significa que o sistema está pronto para demo e operação local.

O principal item ainda não concluído em modo estrito é a execução completa do benchmark de `GraphRAG`, já que o workspace experimental depende de chave de API para indexação e consultas reais.

## 12. Limitações

As principais limitações atuais são:

- corpus documental público ainda pequeno;
- parsing local operando com baseline `markdown`, apesar da arquitetura manter espaço para `Docling`;
- benchmark completo de `GraphRAG` ainda não executado;
- ambiente Kubernetes local ainda não priorizado frente ao fluxo em Compose;
- dados totalmente mockados, o que limita avaliação de ruído institucional real.

Essas limitações são explícitas e não comprometem a utilidade do sistema como plataforma de demonstração, pesquisa aplicada e base arquitetural.

## 13. Considerações finais

Este trabalho propõe uma visão mais realista de chatbot escolar com IA: não um agente conversacional livre, mas uma plataforma governada, segura, auditável e operacionalmente observável. A principal contribuição está em mostrar que a camada de IA deve ser apenas um componente de uma arquitetura maior, orientada por políticas, contratos e trilhas de evidência.

O projeto demonstra que é possível construir localmente uma base técnica robusta para atendimento escolar com:

- canal conversacional real;
- autenticação e vínculo reais;
- retrieval documental moderno;
- consultas estruturadas seguras;
- operação humana integrada;
- observabilidade e gates de prontidão.

Como continuidade, a linha de trabalho mais importante é executar o benchmark completo de `GraphRAG` e decidir, com base em evidência, se ele agrega valor suficiente para integrar algum fluxo concreto do produto.

## Referências

- OpenAI. Models. Disponível em: https://developers.openai.com/api/docs/models
- OpenAI. Retrieval guide. Disponível em: https://developers.openai.com/api/docs/guides/retrieval
- OpenAI. Evals guide. Disponível em: https://developers.openai.com/api/docs/guides/evals
- OpenAI. Responses API migration guide. Disponível em: https://developers.openai.com/api/docs/guides/migrate-to-responses
- OpenAI. Agents SDK. Disponível em: https://openai.github.io/openai-agents-python/
- LangChain. LangGraph overview. Disponível em: https://docs.langchain.com/oss/python/langgraph/overview
- Microsoft. GraphRAG documentation. Disponível em: https://microsoft.github.io/graphrag/
- Microsoft. GraphRAG repository. Disponível em: https://github.com/microsoft/graphrag
- PostgreSQL. Full Text Search. Disponível em: https://www.postgresql.org/docs/current/textsearch.html
- Qdrant. Hybrid queries. Disponível em: https://qdrant.tech/documentation/concepts/hybrid-queries/
- Keycloak. Authorization Services. Disponível em: https://www.keycloak.org/docs/latest/authorization_services/index.html
- Open Policy Agent. Documentation. Disponível em: https://www.openpolicyagent.org/docs
- Telegram. Bot API. Disponível em: https://core.telegram.org/bots/api
- Telegram. End-to-end encryption and Secret Chats. Disponível em: https://core.telegram.org/api/end-to-end
