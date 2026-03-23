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
- encaminhar mensagens para `api-core`.

### Dependências

- `api-core`
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
- composição da resposta final;
- emissão de metadados de confiança e fontes.

### Dependências

- API remota de LLM
- `postgres`
- `minio`
- `redis`

### Regras

- não acessa banco diretamente fora de contracts aprovados;
- não executa SQL livre;
- só recebe dados mínimos por tool.

## 5. `worker`

### Responsabilidades

- ingestão documental;
- embeddings;
- reindexação;
- mock data generation;
- backfills;
- jobs de avaliação offline.

### Dependências

- `postgres`
- `minio`
- `redis`
- APIs de modelo/embedding

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
- resolver visibilidade;
- devolver chunks elegíveis;
- gerenciar versões e metadados.

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
- embeddings via `pgvector`.

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

