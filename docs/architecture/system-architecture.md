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
3. O runtime executa um `semantic router` compartilhado para atos de alta precedência, classificação estruturada do turno e reconciliação de follow-up curto.
4. O `semantic router` produz um `TurnFrame` canônico com:
   - `conversation_act`;
   - `capability`;
   - `scope`;
   - `access_tier`;
   - `entities`;
   - `follow_up_of`;
   - `needs_clarification`;
   - `confidence`.
5. A stack escolhida resolve a solicitação via adapter próprio, usando o `TurnFrame` como contrato de entrada:
   - lane determinística;
   - retrieval híbrido;
   - workflow nativo da stack;
   - ou handoff controlado.
6. `api-core` é consultado para fatos públicos canônicos e dados protegidos mínimos.
7. A resposta é lapidada apenas dentro dos limites de grounding, policy e superfície sensível.
8. O resultado volta ao canal com `debug trace` opcional e trilha OTEL completa.

## Arquitetura alvo de interpretação do turno

O projeto deixa de evoluir por expansão incremental de heurísticas locais por stack. O alvo arquitetural é:

- uma camada compartilhada de interpretação do turno;
- seguida por execução específica por stack;
- com regras determinísticas restritas a `policy`, `auth`, `precedence` e `safety`.

### Núcleo compartilhado

O núcleo compartilhado deve concentrar:

- ontologia canônica de `capabilities`;
- geração de candidatos semânticos `top-k`;
- classificação estruturada do turno via LLM com schema rígido;
- memória curta canônica de follow-up (`FocusFrame`);
- reconciliação entre pergunta atual e contexto recente;
- política de precedência entre superfícies públicas e protegidas.

No estado atual do repositório, esse núcleo já existe dentro de `packages/semantic-ingress` e expõe:

- catálogo canônico de `CapabilitySpec`;
- `FocusFrame`;
- `CapabilityCandidate`;
- `TurnFrame`;
- candidate generation heurístico-controlada;
- classificador estruturado por provider;
- metadata serializável para preview/debug.

### O que continua determinístico

As seguintes decisões permanecem fora da liberdade da LLM:

- autorização;
- limites público/protegido;
- `scope_boundary`;
- `input_clarification` quando a confiança cair abaixo do mínimo;
- bloqueios de vazamento;
- renderização final de dados sensíveis.

### O que cada stack faz melhor

- `python_functions`: dispatch determinístico, baixa latência e handlers tipados.
- `langgraph`: workflow com estado, `thread_id`, edges condicionais e follow-up robusto.
- `llamaindex`: query routing e síntese documental orientada a fontes.
- `specialist_supervisor`: execução quality-first, repair, multi-intent e composição mais rica quando isso realmente agrega valor.

No estado atual:

- `python_functions` já consome `TurnFrame` no planner e no native runtime;
- `langgraph` já injeta `TurnFrame` no bootstrap do workflow e usa isso para preferir o caminho público estruturado;
- `llamaindex` já usa `TurnFrame` no planner e no native plan runtime;
- `specialist_supervisor` já usa `TurnFrame` no preview e na resolução de intent antes do supervisor premium.

### Regra de projeto

O núcleo compartilhado interpreta. A stack executa.

Isso evita dois anti-padrões:

- reimplementar entendimento semântico completo em cada stack;
- forçar as quatro stacks a terem a mesma execução interna.

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

## Estratégia de contexto local com Gemma

O projeto não trata a janela máxima do modelo como objetivo em si. A estratégia arquitetural para `Gemma 4 E4B` local é:

- `retrieval-first`, não `stuff-everything-in-context`;
- histórico curto e memória explícita antes de histórico bruto longo;
- packing de evidência por budget de tokens, não por contagem fixa de linhas;
- aumento gradual de contexto apenas nas rotas em que isso mostrar ganho mensurável.

Isso implica:

- telemetria de contexto e truncamento por stack;
- `evidence packing` compartilhado e orientado a resposta;
- memória curta/episódica compartilhada para follow-up;
- rerank e seleção de trechos calibrados por capability;
- composição grounded que adapte a resposta ao foco da pergunta sem despejar toda a evidência disponível.

Baseline atual implementado:

- `turn_router` com packing por budget para histórico e candidatas;
- `public_answer_composer` com packing por budget para histórico e evidência;
- adapters locais com packing compartilhado para histórico, evidência e blocos estruturados;
- `FocusFrame` enriquecido com memória episódica vinda de `recent_tool_calls` e `slot_memory`;
- política compartilhada de retrieval por capability, calibrando `retrieval_profile`, `top-k` e categoria documental antes do dispatch por stack;
- traces operacionais agora também registram a política escolhida e o resultado efetivo do retrieval por capability, preparando tuning com `answerable@k`, cobertura e latência por família;
- budgets iniciais explícitos e configuráveis nas settings dos runtimes.

Técnicas de memória longa baseadas em compressão de `KV cache`, como `TurboQuant` e `TriAttention`, ficam fora do baseline atual. Elas só entram em avaliação se os ganhos acima se esgotarem e o sistema passar a depender materialmente de janelas muito maiores no serving local.

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
