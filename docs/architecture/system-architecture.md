# Arquitetura do Sistema

## Visao arquitetural atual

O EduAssist nao opera mais como um único orquestrador de serving. O estado canônico do projeto é `dedicated-first`:

- `telegram-gateway` recebe e normaliza o canal;
- `api-core` mantém identidade, autorização, trilha operacional e dados canônicos;
- `ai-orchestrator` atua como `control plane/router` e superfície administrativa;
- quatro runtimes dedicados executam o serving principal:
  - `ai-orchestrator-langgraph`
  - `ai-orchestrator-python-functions`
  - `ai-orchestrator-llamaindex`
  - `ai-orchestrator-specialist`
- o plano de dados é sustentado por `postgres`, `qdrant`, `redis` e `minio`.

## Principios

- canal desacoplado de domínio;
- `LLM de entrada -> stack -> LLM de saída`;
- dados protegidos nunca entram no modelo sem contrato mínimo e autorização;
- toda resposta protegida parte de ferramentas e serviços auditáveis;
- retrieval híbrido e políticas de visibilidade antecedem qualquer composição final;
- o `control plane` existe para governança, diagnóstico, scorecard e roteamento, não como entrypoint normal de produto.

## Fluxo de serving dedicado

1. `telegram-gateway` recebe webhook, valida token interno e normaliza o update.
2. O gateway encaminha a requisição para um runtime dedicado.
3. O runtime executa `semantic ingress` compartilhado para atos de alta precedência.
4. A stack escolhida resolve a solicitação via:
   - lane determinística;
   - retrieval híbrido;
   - workflow nativo da stack;
   - ou handoff controlado.
5. `api-core` é consultado para fatos públicos canônicos e dados protegidos mínimos.
6. A resposta é lapidada apenas dentro dos limites de grounding, policy e superfície sensível.
7. O resultado volta ao canal com `debug trace` opcional e trilha OTEL completa.

## Responsabilidades por plano

### Data plane

- `ai-orchestrator-langgraph`
- `ai-orchestrator-python-functions`
- `ai-orchestrator-llamaindex`
- `ai-orchestrator-specialist`

Esses serviços respondem mensagens e concentram a lógica de execução por stack.

### Control plane

- `ai-orchestrator`

Esse serviço concentra:

- status agregado;
- scorecard e promotion gate;
- diagnóstico entre stacks;
- capacidades e metadados de serving;
- compat mode apenas quando explicitamente habilitado.

## Retrieval

A arquitetura de retrieval atual combina:

- vetorial e lexical;
- filtragem por visibilidade e vigência;
- query variants;
- late interaction rerank quando habilitado;
- fatos canônicos públicos estruturados para perguntas simples em que retrieval documental seria custo desnecessário.

`GraphRAG` continua seletivo, nunca padrão cego.

## Observabilidade

O stack observável atual é:

- OpenTelemetry nos serviços Python;
- `otel-collector` com tail-based sampling;
- `Tempo` para traces;
- `Prometheus` para métricas;
- `Grafana` com dashboards operacionais e de GenAI;
- `Loki` para logs.

Além das métricas de domínio, o projeto agora emite:

- spans com semântica GenAI do OpenTelemetry;
- uso de tokens de entrada e saída;
- latência por operação de modelo;
- custo estimado por request quando o provider suportado permite cálculo simples.

## Criterios arquiteturais de aprovacao

- nenhum fluxo sensível sem policy check e contrato mínimo;
- nenhum fallback administrativo para pergunta semanticamente incerta;
- nenhum serving principal pelo control plane;
- nenhuma resposta protegida sem superfície de dados auditável;
- documentação oficial e estado de execução sempre alinhados.
