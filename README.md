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
- `OpenTelemetry + Grafana + Loki + Tempo` para observabilidade.
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
- seed foundation idempotente já disponível em `tools/mockgen`;
- `Makefile`, `.env.example`, Dockerfiles e healthchecks;
- base documental sincronizada com a direção arquitetural atual.

Expansões já aprovadas para a próxima etapa:

- introduzir pipeline documental com `Docling`;
- integrar `Keycloak` ao fluxo de identidade e vínculo com Telegram;
- preparar modo avançado de retrieval com `GraphRAG` somente após baseline híbrido estar medido.

## Próximos passos imediatos

1. Preparar a fundação do pipeline documental com `Docling`.
2. Integrar `Keycloak` e o fluxo de vínculo seguro entre identidade escolar e canal Telegram.
3. Conectar `Qdrant` e services ao fluxo completo de ingestão e retrieval.
4. Subir a primeira vertical funcional de FAQ pública com retrieval híbrido e citações.
5. Expandir a seed para cenários mais amplos de acadêmico, financeiro e handoff.
