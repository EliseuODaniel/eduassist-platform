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
- seleção e contrato mínimo dos dados sensíveis antes de qualquer verbalização final.

### Refino final validado de superfície

No estado atual do `specialist_supervisor`, a arquitetura não trata mais caminhos determinísticos e caminhos LLM-driven como duas superfícies finais completamente diferentes. A regra passou a ser:

- toda resposta elegível pode passar por um `answer surface refiner`;
- o refino tenta primeiro uma saída estruturada e validável;
- se o modelo local falhar no schema, a arquitetura usa um fallback controlado em texto livre;
- a nova superfície só é aceita quando um validador local confirma preservação de fatos, nomes, disciplinas, datas, valores, escopo e ato conversacional;
- se a validação falhar, a arquitetura preserva literalmente a resposta original.

Nas stacks non-specialist, a mesma lógica foi promovida para o pós-processamento compartilhado. Isso garante que `langgraph`, `python_functions` e `llamaindex` também passem por uma etapa final de verbalização orientada por LLM, sem perder o comportamento atual quando o validador conclui que a melhor resposta continua sendo a superfície determinística original.

Guardrails:

- bloqueios de privacidade, negação por terceiro e `input guardrail blocked` não entram nesse refino livre;
- o refino pode melhorar tom, fluidez e aderência à pergunta, mas não pode inventar novos fatos nem ampliar o escopo permitido;
- a superfície final deixa de ser mero template rígido, sem abrir mão de grounding e auditabilidade.

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
- rerank semântico em duas camadas quando habilitado;
- fatos canônicos públicos estruturados para perguntas simples em que retrieval documental seria custo desnecessário.

No baseline atual, essa camada combina:

- `late interaction` com `answerdotai/answerai-colbert-small-v1`;
- `cross-encoder` multilíngue com `jinaai/jina-reranker-v2-base-multilingual`;
- fusão ponderada com o score híbrido original antes da composição grounded.

`GraphRAG` continua seletivo, nunca padrão cego.

## Identidade de workload interna

O plano interno entre serviços deixou de depender exclusivamente de token estático na camada de aplicação.

Estado atual:

- o baseline local ainda usa `X-Internal-Api-Token` como mecanismo default;
- `api-core`, `ai-orchestrator`, runtimes dedicados, `specialist_supervisor` e `telegram-gateway` agora também aceitam um `SPIFFE ID` encaminhado por proxy confiável;
- quando o `SPIFFE ID` pertence a uma allowlist explícita, o runtime faz a ponte para o enforcement atual de token interno sem abrir um caminho implícito novo de autorização;
- isso torna a arquitetura `SPIFFE-ready` sem fingir que um rollout completo de `SPIRE` já está ativo no Compose local.

Leitura honesta:

- o débito “adotar SPIFFE/SPIRE” deixa de ser lacuna no nível do código de aplicação;
- o que permanece opcional e dependente de ambiente é a implantação da malha/attestation completa de `SPIRE`.

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

## Perfis locais de LLM

O baseline local do projeto continua centrado em `Gemma 4 E4B`, mas o runtime agora aceita um segundo profile local explícito para benchmark controlado:

- `gemma4e4b_local`
  - serviço: `local-llm-gemma4e4b`
  - engine: `llama.cpp`
  - artefato padrão: `Q4_K_M`
- `qwen3_4b_instruct_local`
  - serviço: `local-llm-qwen3-4b`
  - engine: `llama.cpp`
  - artefato padrão: `Qwen3-4B-Instruct-2507 Q5_K_M`

Regra arquitetural:

- o profile alternativo deve ser ativado apenas por feature flag (`LLM_MODEL_PROFILE`);
- o baseline operacional não muda automaticamente;
- comparações entre modelos devem ocorrer na mesma stack e sob o mesmo dataset, preferencialmente no `specialist_supervisor`.

Leitura consolidada da rodada A/B local (`2026-04-17`):

- a primeira passada crua favoreceu `Qwen` em latência e estabilidade, mas expôs resíduos arquiteturais no `specialist_supervisor`;
- depois da wave de correções compartilhadas e do `answer surface refiner`, o `Gemma` endurecido (`gemma4e4b_local_postfix`) fechou em `15/15`, `keyword_pass 15/15` e `quality 100.0`;
- o `Qwen` permaneceu melhor em latência, mas terminou em `quality 84.3` e `keyword_pass 8/15` sob o mesmo dataset;
- decisão arquitetural atual: manter `Gemma` como baseline operacional e `Qwen` como feature flag experimental para A/B local controlado.

Estado operacional do hardening em 2026-04-16:

- o benchmark amplo `60Q` fechou com `quality 100.0` e `keyword_pass 100%` nas quatro stacks;
- o benchmark de stress `40Q` também fechou com `quality 100.0` em `c1` nas quatro stacks e em `c2` para `langgraph`, `llamaindex` e `specialist_supervisor`;
- o principal gap remanescente deixou de ser semântico e passou a ser operacional: sob `c4`, os non-specialists ainda sofrem `request_failed` em bundles públicos multi-documento, enquanto o `specialist_supervisor` permanece estável;
- a próxima frente arquitetural, portanto, é throughput e queueing para caminhos públicos pesados, não novo endurecimento de roteamento básico.

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
