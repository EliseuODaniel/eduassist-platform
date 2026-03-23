# EduAssist Platform

Plataforma de atendimento escolar com IA, Telegram, dados mockados sobre infraestrutura real e foco explícito em segurança da informação.

## Status

Este repositório nasce como um `greenfield rebuild`. O objetivo é substituir integralmente o protótipo anterior por uma plataforma nova, com arquitetura adequada para:

- atendimento de `pais`, `alunos`, `professores`, `secretaria`, `financeiro`, `coordenação` e `direção`;
- uso de `Telegram` como canal principal;
- consulta segura a dados escolares reais em bancos reais, mas com conteúdo `100% mockado`;
- uso de IA generativa com `RAG`, `GraphRAG` seletivo, tool calling, grounding, citações e forte governança;
- execução local via `Docker Compose`, com caminho opcional para `k3d` depois.

## Nome do projeto

Nome adotado para o novo repositório: `eduassist-platform`

Justificativa:

- preserva continuidade semântica com o domínio do projeto;
- é mais preciso do que `studio`;
- comunica que o escopo é uma plataforma, não só um protótipo ou bot isolado.

## Visão

Construir uma plataforma robusta e funcional de atendimento escolar com IA para uma escola fictícia de ensino médio, capaz de responder perguntas institucionais, consultar dados acadêmicos e financeiros mockados, intermediar processos internos e operar com autenticação, autorização, auditoria e observabilidade desde o início.

## Objetivos estratégicos

- Prover atendimento conversacional confiável via Telegram.
- Separar rigorosamente conteúdo público, autenticado e sensível.
- Garantir que o LLM nunca acesse o banco diretamente.
- Tornar todo acesso a dados sensíveis auditável.
- Manter ambiente local completo, reproduzível e utilizável em máquina pessoal.
- Criar uma base documental e arquitetural apta a orientar implementação, pesquisa e redação acadêmica.

## Decisões de alto nível

- `Python + FastAPI` no backend principal.
- `LangGraph` como motor principal de orquestração controlada, com trilha OpenAI nativa em `Responses API` e padrões do `Agents SDK` quando fizer sentido.
- `Next.js` para painel administrativo.
- `PostgreSQL` como source of truth transacional.
- `Qdrant + PostgreSQL Full Text Search` como plano principal de retrieval para documentos e conhecimento institucional.
- `Docling` para parsing, normalização e enriquecimento documental.
- `pgvector` apenas como fallback de experimentação local e não como plano principal de retrieval.
- `Keycloak + OPA + PostgreSQL RLS` para identidade e autorização.
- `MinIO` para documentos e objetos.
- `Redis` para cache, locks, idempotência e filas leves.
- `OpenTelemetry + Grafana + Tempo + Loki` para tracing distribuido, logs centralizados e investigacao operacional.
- quando a trilha OpenAI for adotada, `Responses API` como interface preferencial para fluxos agentic e tool-using.
- LLM remota via API paga, com benchmark inicial em `GPT-5.4` e benchmark paralelo em `Gemini 2.5 Pro`.

## Índice da documentação

- [PRD](/home/edann/projects/eduassist-platform/docs/prd/product-requirements.md)
- [Arquitetura do sistema](/home/edann/projects/eduassist-platform/docs/architecture/system-architecture.md)
- [Segurança da informação](/home/edann/projects/eduassist-platform/docs/security/security-architecture.md)
- [Modelo de dados](/home/edann/projects/eduassist-platform/docs/data/data-model.md)
- [Operação local](/home/edann/projects/eduassist-platform/docs/operations/local-development.md)
- [Workflow de Codex e MCP](/home/edann/projects/eduassist-platform/docs/operations/codex-workflow.md)
- [Pesquisa de tecnologias de IA](/home/edann/projects/eduassist-platform/docs/research/ai-technology-review.md)
- [Roadmap de implementação](/home/edann/projects/eduassist-platform/docs/roadmap/implementation-roadmap.md)
- [ADR 0001 - Rebuild do zero](/home/edann/projects/eduassist-platform/docs/adr/0001-greenfield-rebuild.md)
- [ADR 0002 - Retrieval e runtime agentic](/home/edann/projects/eduassist-platform/docs/adr/0002-retrieval-and-agent-runtime.md)
- [Plano de refatoração do documento acadêmico](/home/edann/projects/eduassist-platform/docs/article/refactor-outline.md)

## Estrutura inicial do repositório

```text
eduassist-platform/
├── apps/
├── docs/
│   ├── adr/
│   ├── architecture/
│   ├── article/
│   ├── data/
│   ├── operations/
│   ├── prd/
│   ├── research/
│   ├── roadmap/
│   └── security/
├── .agents/
├── .codex/
├── .vscode/
├── infra/
├── packages/
├── tests/
└── tools/
```

## Componentes planejados

- `admin-web`: painel de operação, auditoria, curadoria documental e acompanhamento de qualidade.
- `api-core`: regras de negócio, autenticação, autorização, workflows e integração entre domínio, IA e dados.
- `telegram-gateway`: webhook do Telegram, normalização de mensagens, idempotência e rate limiting.
- `ai-orchestrator`: orquestração LangGraph, retrieval, tool calling, grounding e composição de respostas.
- `worker`: jobs assíncronos, mock data generation, ingestão documental, embeddings e evals.
- `AGENTS.md`, skills, custom agents e Docs MCP: governança de desenvolvimento e pesquisa para manter o projeto alinhado às práticas atuais do ecossistema Codex/OpenAI.

## Fluxos principais planejados

- FAQ institucional pública com citações.
- Calendário escolar público e autenticado.
- Consulta acadêmica protegida por vínculo de acesso.
- Consulta financeira protegida por vínculo de acesso.
- Handoff para atendimento humano.
- Trilha de auditoria para acessos sensíveis.

## Ambiente local alvo

Ambiente observado durante o planejamento:

- `Ubuntu 24.04` em `WSL2`
- `32 vCPUs`
- `~15 GiB` de RAM visível no Linux
- `RTX 4070 Laptop GPU` com `8 GiB` de VRAM
- `~893 GiB` livres

Estratégia:

- `Docker Compose` como padrão de desenvolvimento.
- `k3d` ou `kind` apenas em etapa posterior.
- Perfil `core` e perfil `full` para caber com folga na RAM disponível.

## Estado atual

Este repositório já contém o bootstrap técnico inicial do projeto:

- stack local em [compose.yaml](/home/edann/projects/eduassist-platform/infra/compose/compose.yaml);
- `Qdrant` já integrado ao ambiente local para a fundação do retrieval;
- esqueletos executáveis para `api-core`, `ai-orchestrator`, `telegram-gateway`, `worker` e `admin-web`;
- `ai-orchestrator` já expõe preview do grafo, capabilities e contratos de tools;
- `api-core` já possui foundation transacional com `SQLAlchemy + Alembic`, migração inicial e endpoint de resumo;
- `api-core` já resolve contexto de identidade, consulta o `OPA`, aplica autorização contextual e registra trilha de auditoria básica para acessos protegidos;
- `api-core` já valida `JWT` do `Keycloak` via `JWKS`, resolve sessão autenticada por identidade federada e emite challenges de vínculo com Telegram;
- `telegram-gateway` já consome `/start link_<codigo>` e conclui o vínculo via endpoint interno autenticado;
- `api-core` já expõe calendário público estruturado e resolução interna de ator por `telegram_chat_id` para uso seguro do gateway;
- `Keycloak` já sobe com import automático do realm `eduassist` e usuários mockados para testes locais;
- o `worker` já sincroniza corpus documental mockado para `MinIO`, `Postgres` e `Qdrant`;
- o `ai-orchestrator` já expõe busca híbrida real via `Qdrant + PostgreSQL FTS` com citações;
- o `ai-orchestrator` já responde mensagens reais com FAQ pública, calendário público, negação segura de fluxos protegidos e fallback determinístico quando não houver chave de LLM configurada;
- o `telegram-gateway` já encaminha mensagens públicas ao `ai-orchestrator` e devolve respostas úteis no formato do Telegram;
- o `telegram-gateway`, o `ai-orchestrator` e o `api-core` agora trocam chamadas internas protegidas por `X-Internal-Api-Token`;
- o `telegram-gateway` já responde consultas protegidas reais para contas vinculadas: resumo acadêmico com filtros por disciplina e bimestre, resumo financeiro com filtros por status e panorama multi-aluno para responsáveis, além de grade docente com consultas por turmas, disciplinas e horário para professores;
- o `admin-web` já expõe login real via `Keycloak` com OIDC + PKCE, leitura de sessão autenticada no `api-core`, emissão de challenge de vínculo para o Telegram e overview operacional autenticado com visão pessoal ou global conforme o papel;
- o `api-core` já expõe `GET /v1/operations/overview` com métricas, feed de auditoria, feed de decisões de acesso, contagens estruturais e agregados operacionais de handoff para papéis internos;
- o `api-core` já expõe a fila de `handoffs` humanos com escopo pessoal ou global, incluindo prioridade, SLA mockado e atribuição operacional;
- o `ai-orchestrator` já cria handoffs reais ao entrar em modo `handoff`, devolvendo protocolo e fila ao usuário no Telegram;
- o `admin-web` já roda em modo estável de produção dentro do `Docker Compose`, renderiza a fila de handoffs com filtros por status, fila, atribuição, SLA e texto livre, abre o detalhe completo da conversa e mostra saúde operacional da fila humana com visão por setor, operador, exceções críticas, atalhos diretos de drill-down e uma leitura temporal de volume/tempo operacional;
- o stack local já inclui `OpenTelemetry Collector`, `Tempo` e `Grafana`, com propagacao de trace context entre `telegram-gateway`, `ai-orchestrator` e `api-core`;
- o stack local agora também inclui `Prometheus`, alimentado por metricas OTEL exportadas via collector;
- o tracing distribuido já foi validado ponta a ponta via webhook do Telegram, incluindo spans HTTP entre serviços, spans SQLAlchemy no `api-core` e consulta direta do trace no `Tempo`;
- os serviços Python instrumentados já devolvem `X-Trace-Id` e `X-Span-Id` nas respostas, facilitando o drill-down operacional no ambiente local;
- o tracing agora também inclui spans de dominio para policy, retrieval híbrido e operacoes de handoff, com dashboard provisionado em `Grafana` para cribsheet de TraceQL e runbook local;
- a stack de observabilidade agora também expõe metricas de dominio para `policy`, `retrieval`, `handoff` e `orquestracao`, com dashboard provisionado em `Grafana` para acompanhamento analitico;
- o stack local agora também inclui `Loki + Promtail`, com ingestao dos logs dos containers do Compose para investigacao centralizada no `Grafana`;
- existe uma suite de smoke local em `tests/e2e/local_smoke.py` para validar os fluxos principais e a pilha de observabilidade;
- existe uma suite de regressao de autorizacao em `tests/e2e/authz_regression.py` para validar negativas, ambiguidades, bearer ausente e segredos invalidos;
- existe uma suite adversarial em `tests/e2e/adversarial_regression.py` para validar tentativas de exfiltracao, prompt disclosure e resistencia operacional a consultas maliciosas;
- seed foundation idempotente já disponível em `tools/mockgen`;
- sincronização de identidades federadas disponível em `tools/mockgen/sync_auth_bindings.py`;
- `Makefile`, `.env.example`, Dockerfiles e healthchecks;
- base documental sincronizada com a direção arquitetural atual.

Expansões já aprovadas para a próxima etapa:

- preparar modo avançado de retrieval com `GraphRAG` somente após baseline híbrido estar medido.

## Próximos passos imediatos

1. Expandir os dashboards do `Grafana` com leituras mais profundas de SLA operacional, filas, attribution e logs correlacionados.
2. Expandir a suite de testes e evals com cenarios adversariais adicionais, casos de exfiltracao e regressao operacional.
3. Expandir a seed para cenários mais amplos de tickets, filas, operadores e resoluções.
4. Expandir a revisão detalhada do atendimento com histórico mais rico, paginação e buscas mais profundas no `admin-web`.
5. Preparar benchmark comparativo para `GraphRAG` seletivo sobre o corpus institucional.
