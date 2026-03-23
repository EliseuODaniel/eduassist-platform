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
- criação de handoffs humanos reais no `api-core` quando o fluxo entrar em suporte operacional;
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
- login web autenticado com `Keycloak`;
- leitura de sessão autenticada no `api-core`;
- leitura de overview operacional autenticado no `api-core`, incluindo agregados globais da fila humana, alertas críticos e tendências recentes de volume/tempo;
- leitura e gestão da fila de handoffs humanos no `api-core`, com detalhe da conversa, nota operacional, atribuição, SLA mockado e filtros operacionais por status, fila, atribuição e criticidade;
- leitura e gestão da fila de handoffs humanos com paginação explícita para suportar volume operacional crescente no painel;
- leitura detalhada do transcript da conversa com exploração local por remetente, busca textual e navegação por janela no painel operacional;
- geração de challenge de vínculo para o Telegram;
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
- controlar status de atendimento humano;
- devolver protocolo operacional e fila ao bot e ao painel;
- permitir visão pessoal para usuários finais autenticados e visão global para perfis internos.

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

### `otel-collector`

- recebe spans OTLP dos serviços instrumentados;
- faz batch e exporta traces para o `tempo`;
- permite observabilidade distribuida sem acoplar os apps ao backend final.

### `tempo`

- armazena traces distribuidos;
- permite busca por `trace_id` e consulta operacional do fluxo entre serviços;
- sustenta a investigacao do caminho `telegram-gateway -> ai-orchestrator -> api-core`.

### `grafana`

- expõe a visualização dos traces armazenados no `tempo`;
- hospeda dashboards e drill-down operacional do ambiente local;
- já sobe com datasources de `tempo`, `loki` e `prometheus` provisionados;
- já inclui dashboards provisionados para tracing e metricas do fluxo `Telegram -> AI -> API Core`.

### `loki`

- agrega logs centralizados do ambiente local;
- serve como backend de investigacao textual no `Grafana`.

### `promtail`

- coleta logs dos containers do Docker local;
- publica esses logs no `loki` com labels de container e serviço do Compose.

### `prometheus`

- raspa o endpoint de metricas do `otel-collector`;
- expõe PromQL para leitura analitica das metricas OTEL do dominio;
- sustenta o dashboard de metricas operacionais no `Grafana`.
