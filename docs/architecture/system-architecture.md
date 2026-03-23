# Arquitetura do Sistema

## 1. Visão arquitetural

O sistema será estruturado como um monólito modular com workers auxiliares, e não como um conjunto de microserviços independentes desde o início. Isso reduz complexidade de operação local sem sacrificar separação lógica entre domínios.

Arquitetura lógica:

- `telegram-gateway`
- `api-core`
- `ai-orchestrator`
- `worker`
- `admin-web`
- `postgres`
- `redis`
- `minio`
- `keycloak`
- `opa`
- `otel-collector`
- `grafana`, `loki`, `tempo`

## 2. Princípios

- canal desacoplado do domínio;
- IA desacoplada do banco;
- autorização centralizada e reforçada no banco;
- contexto mínimo para a LLM;
- respostas documentais com citações;
- respostas estruturadas por serviços determinísticos;
- observabilidade desde o primeiro deploy local.

## 3. Fluxo de FAQ pública

1. Usuário envia mensagem ao bot.
2. `telegram-gateway` valida webhook e normaliza o evento.
3. `api-core` classifica a mensagem como pública.
4. `ai-orchestrator` executa retrieval híbrido.
5. chunks aprovados por visibilidade entram no contexto.
6. LLM gera resposta com referências.
7. `api-core` registra trilha e envia resposta ao Telegram.

## 4. Fluxo de consulta protegida

1. Usuário envia mensagem ao bot.
2. `telegram-gateway` recebe e normaliza.
3. `api-core` detecta que a pergunta exige autenticação.
4. sistema verifica vínculo do usuário com conta escolar.
5. `OPA` avalia a policy da ação solicitada.
6. `api-core` chama serviço interno autorizado.
7. serviço consulta Postgres sob `RLS`.
8. `ai-orchestrator` recebe só os dados mínimos necessários para formular a resposta.
9. resposta é enviada com escopo adequado e trilha de auditoria.

## 5. Fronteiras entre módulos

### `telegram-gateway`

- responsabilidade exclusiva de canal;
- não contém lógica de domínio;
- gerencia webhook, idempotência e rate limit.

### `api-core`

- ponto central de regras de negócio;
- autenticação, autorização e integração entre módulos;
- coordena chamadas de IA e services.

### `ai-orchestrator`

- classifica intenção;
- seleciona tools;
- executa fluxo LangGraph;
- gera resposta final com grounding.

### `worker`

- tarefas assíncronas e batch;
- ingestão documental;
- embeddings;
- geração de dados mockados;
- avaliações offline.

### `admin-web`

- curadoria, operação, auditoria e supervisão;
- não deve encapsular regras críticas de autorização sem backend.

## 6. Serviços de dados

Os domínios serão expostos por services internos:

- `document-service`
- `calendar-service`
- `academic-service`
- `finance-service`
- `identity-service`
- `ticket-service`

Cada service deve:

- validar input;
- solicitar decisão de policy quando necessário;
- devolver apenas contratos mínimos;
- registrar eventos relevantes.

## 7. Orquestração de IA

Estratégia:

- um único orquestrador principal;
- tools fechadas e auditáveis;
- sem SQL livre;
- sem múltiplos agentes autônomos no MVP.
- se o provedor OpenAI for o escolhido na implementação, preferir `Responses API` como interface principal para tool use e workflows agentic.

Tools previstas:

- `search_public_documents`
- `search_private_documents`
- `get_school_calendar`
- `get_student_academic_summary`
- `get_student_attendance`
- `get_student_grades`
- `get_financial_summary`
- `get_invoice_details`
- `get_teacher_schedule`
- `create_support_ticket`
- `handoff_to_human`

## 8. Topologias de execução

### 8.1 Local padrão

- `Docker Compose`
- perfis `core`, `observability` e `full`

### 8.2 Local avançado

- `k3d` ou `kind`
- usado apenas após estabilização em Compose

## 9. Diagrama lógico em texto

```text
Telegram
  -> telegram-gateway
  -> api-core
     -> keycloak / opa
     -> ai-orchestrator
        -> retrieval over postgres + minio metadata
        -> llm remote api
     -> academic-service / finance-service / calendar-service
        -> postgres
     -> redis
  -> response to Telegram

admin-web
  -> api-core
  -> observability stack
```

## 10. Critérios arquiteturais de aprovação

- nenhum fluxo sensível sem policy check;
- nenhum acesso direto do modelo ao banco;
- nenhum documento privado entrando em retrieval público;
- toda ação sensível com trilha auditável;
- decisões específicas de OpenAI/Codex documentadas e mantidas atrás de abstração de provedor;
- stack local executável dentro do orçamento de memória observado.
