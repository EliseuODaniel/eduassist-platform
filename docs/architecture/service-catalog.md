# Catálogo de Serviços

## 1. Objetivo

Definir responsabilidades, fronteiras e dependências dos principais serviços planejados no sistema.

## 2. `telegram-gateway`

### Responsabilidades

- receber webhook do Telegram;
- validar `secret_token`;
- normalizar eventos;
- controlar idempotência;
- aplicar rate limiting;
- resolver contexto de ator via `api-core`;
- encaminhar mensagens conversacionais para o `ai-orchestrator` com token interno de serviço.

### Dependências

- `api-core`
- `ai-orchestrator`
- `redis`

### Não responsabilidades

- lógica de domínio;
- consultas a dados escolares;
- decisão de autorização.

## 3. `api-core`

### Responsabilidades

- autenticação e sessão;
- integração com `Keycloak`;
- consulta a `OPA`;
- coordenação de workflows;
- chamada ao `ai-orchestrator`;
- acesso a services de domínio;
- registro de auditoria.

### Dependências

- `postgres`
- `redis`
- `keycloak`
- `opa`
- `ai-orchestrator`

## 4. `ai-orchestrator`

### Responsabilidades

- classificação de intenção;
- execução de fluxo LangGraph;
- tool calling;
- retrieval documental;
- consulta a calendário público estruturado no `api-core`;
- consulta a dados protegidos do `api-core` por rotas internas autenticadas entre serviços;
- composição da resposta final;
- emissão de metadados de confiança e fontes.

### Dependências

- API remota de LLM
- `postgres`
- `qdrant`
- `minio`
- `redis`
- `api-core`

### Regras

- não acessa banco diretamente fora de contracts aprovados;
- não executa SQL livre;
- só recebe dados mínimos por tool.

## 5. `worker`

### Responsabilidades

- ingestão documental;
- parsing documental por backend configurável, com baseline local em `Markdown` e interface pronta para `Docling`;
- embeddings densos para recuperação vetorial local;
- publicação de chunks e metadados em `Postgres`;
- indexação vetorial em `Qdrant`;
- geração de artefatos de `GraphRAG`;
- reindexação;
- mock data generation;
- backfills;
- jobs de avaliação offline.

### Dependências

- `postgres`
- `minio`
- `qdrant`
- APIs de modelo/embedding quando a trilha remota for habilitada

## 6. `admin-web`

### Responsabilidades

- operação do sistema;
- curadoria documental;
- revisão de conversas;
- dashboards;
- visualização de auditoria;
- gestão de handoff.

### Dependências

- `api-core`
- `keycloak`

## 7. `document-service`

### Responsabilidades

- catalogar documentos;
- normalizar documentos processados pelo pipeline;
- resolver visibilidade;
- devolver chunks elegíveis;
- gerenciar versões e metadados;
- publicar material pronto para indexação híbrida e pipelines de `GraphRAG`.

## 8. `academic-service`

### Responsabilidades

- consultar notas, frequência, boletins, horários e avaliações;
- aplicar filtros por vínculo e papel;
- devolver contratos mínimos para tools.

## 9. `finance-service`

### Responsabilidades

- consultar contratos, cobranças, pagamentos e bolsas;
- aplicar políticas de acesso;
- registrar consultas sensíveis.

## 10. `calendar-service`

### Responsabilidades

- responder consultas de calendário letivo, provas, reuniões e eventos;
- distinguir informações públicas e internas.

## 11. `ticket-service`

### Responsabilidades

- abrir chamados;
- registrar encaminhamentos;
- controlar status de atendimento humano.

## 12. Infra serviços

### `postgres`

- source of truth relacional;
- RLS;
- auditoria;
- busca textual;
- suporte a metadata filtering e fallback experimental via `pgvector`.

### `qdrant`

- engine principal de retrieval vetorial e híbrido;
- suporte a dense + sparse retrieval;
- suporte a multivectors e estratégias de late interaction;
- coleções de documentos institucionais e índices auxiliares de conhecimento.

### `redis`

- cache;
- locks;
- idempotência;
- filas leves.

### `minio`

- documentos;
- anexos;
- objetos de ingestão.

### `keycloak`

- identidade;
- SSO;
- papéis;
- OIDC/OAuth2.

### `opa`

- decisão de autorização contextual.

### `otel-collector`, `grafana`, `loki`, `tempo`

- observabilidade ponta a ponta.
