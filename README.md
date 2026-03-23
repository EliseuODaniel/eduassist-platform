# EduAssist Platform

Plataforma de atendimento escolar com IA, Telegram, dados mockados sobre infraestrutura real e foco explícito em segurança da informação.

## Status

Este repositório nasce como um `greenfield rebuild`. O objetivo é substituir integralmente o protótipo anterior por uma plataforma nova, com arquitetura adequada para:

- atendimento de `pais`, `alunos`, `professores`, `secretaria`, `financeiro`, `coordenação` e `direção`;
- uso de `Telegram` como canal principal;
- consulta segura a dados escolares reais em bancos reais, mas com conteúdo `100% mockado`;
- uso de IA generativa com `RAG`, tool calling, grounding, citações e forte governança;
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
- `LangGraph` para orquestração controlada da IA.
- `Next.js` para painel administrativo.
- `PostgreSQL + pgvector + Full Text Search` para dados estruturados e retrieval híbrido.
- `Keycloak + OPA + PostgreSQL RLS` para identidade e autorização.
- `MinIO` para documentos e objetos.
- `Redis` para cache, locks, idempotência e filas leves.
- `OpenTelemetry + Grafana + Loki + Tempo` para observabilidade.
- LLM remota via API paga, com benchmark inicial em `GPT-5.4` e benchmark paralelo em `Gemini 2.5 Pro`.

## Índice da documentação

- [PRD](/home/edann/projects/eduassist-platform/docs/prd/product-requirements.md)
- [Arquitetura do sistema](/home/edann/projects/eduassist-platform/docs/architecture/system-architecture.md)
- [Segurança da informação](/home/edann/projects/eduassist-platform/docs/security/security-architecture.md)
- [Modelo de dados](/home/edann/projects/eduassist-platform/docs/data/data-model.md)
- [Operação local](/home/edann/projects/eduassist-platform/docs/operations/local-development.md)
- [Pesquisa de tecnologias de IA](/home/edann/projects/eduassist-platform/docs/research/ai-technology-review.md)
- [Roadmap de implementação](/home/edann/projects/eduassist-platform/docs/roadmap/implementation-roadmap.md)
- [ADR 0001 - Rebuild do zero](/home/edann/projects/eduassist-platform/docs/adr/0001-greenfield-rebuild.md)
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

Este repositório contém apenas a base documental e a estrutura inicial. A implementação do sistema deverá seguir o roadmap definido na documentação.

## Próximos passos imediatos

1. Corrigir a integração `Docker Desktop <-> WSL2` no ambiente local.
2. Bootstrapar a infraestrutura base em `Compose`.
3. Definir schemas iniciais do banco.
4. Implementar identidade, policy engine e auditoria mínima.
5. Subir a primeira versão do fluxo de FAQ pública.

