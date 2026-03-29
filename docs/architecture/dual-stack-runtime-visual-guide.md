# Guia Visual do Runtime Dual Stack

Este documento explica, de forma didatica e visual, como o runtime atual do EduAssist decide entre `LangGraph` e `CrewAI`, como cada stack executa os fluxos conversacionais e onde cada resposta busca seus dados nas fontes de verdade.

Objetivos:

- mostrar o caminho real da request;
- deixar claro onde entra `feature flag`, `runtime override`, canario e shadow;
- explicar quando o sistema usa tool deterministica, `hybrid retrieval` ou `GraphRAG`;
- reforcar que `LLM`, `LangGraph` e `CrewAI` nao sao fonte de verdade.

## 1. Visao Geral

```mermaid
flowchart LR
    User["Usuario<br/>Telegram / Portal / Admin"] --> Gateway["telegram-gateway<br/>canal + normalizacao"]
    Gateway --> API["api-core<br/>dominio + auth + policies"]
    API --> Orch["ai-orchestrator<br/>entrypoint unico"]

    Orch -->|stack resolvida = langgraph| LG["LangGraph runtime"]
    Orch -->|stack resolvida = crewai| CE["CrewAIEngine"]

    CE --> Pilot["ai-orchestrator-crewai<br/>pilot isolado"]

    LG --> Truth["Fontes de verdade"]
    Pilot --> Truth

    Truth --> API
    API --> Gateway
    Gateway --> User
```

Leitura rapida:

- toda conversa entra pelo `ai-orchestrator`;
- o orquestrador resolve qual stack responde aquela request;
- as duas stacks compartilham a mesma superficie de produto;
- os dados continuam vindo de `api-core`, `Postgres`, `Qdrant` e artefatos de `GraphRAG`.

## 2. Como a Stack Primaria e Resolvida

Hoje a ordem de prioridade e:

1. `runtime override`
2. `feature flag`
3. `orchestrator_engine` do ambiente

Separadamente, existe o experimento por slice, que pode mandar algumas requests para `CrewAI` mesmo quando o primario continua `LangGraph`.

```mermaid
flowchart TD
    A["Nova request<br/>/v1/messages/respond"] --> B{"Slice entrou no experimento<br/>por allowlist / rollout / scorecard?"}
    B -- Sim --> C["Primary = CrewAI<br/>mode = experiment:slice:crewai"]
    B -- Nao --> D{"Ha runtime override?"}
    D -- Sim --> E["Usa runtime override<br/>langgraph | crewai | shadow"]
    D -- Nao --> F{"Feature flag definida?"}
    F -- Sim --> G["Usa FEATURE_FLAG_PRIMARY_ORCHESTRATION_STACK"]
    F -- Nao --> H["Usa orchestrator_engine do startup"]

    C --> I["Executa stack escolhida"]
    E --> I
    G --> I
    H --> I
```

## 3. O Que e Fonte de Verdade Neste Repo

```mermaid
flowchart LR
    subgraph Truth["Fontes de verdade reais"]
        PG["Postgres<br/>dados estruturados + RLS + FTS"]
        API["api-core interno<br/>contracts e services"]
        QD["Qdrant<br/>dense + sparse retrieval"]
        GR["Workspace GraphRAG<br/>artefatos gerados offline"]
    end

    subgraph Runtime["Camada de orquestracao"]
        LG["LangGraph"]
        CE["CrewAI Flows"]
        LLM["LLM provider"]
    end

    LG --> API
    LG --> QD
    LG --> PG
    LG --> GR
    CE --> API
    CE --> LLM
    LG --> LLM

    LLM -. nao e source of truth .-> Truth
    CE -. nao e source of truth .-> Truth
    LG -. nao e source of truth .-> Truth
```

Regra pratica:

- dados estruturados de aluno, financeiro, identidade, protocolo e workflow: `api-core` + `Postgres`;
- fatos publicos canonicamente publicados: endpoints publicos do `api-core`;
- perguntas documentais: `Qdrant + PostgreSQL FTS`;
- perguntas multi-documento e corpus-level: `GraphRAG`, quando habilitado;
- `LLM` apenas compoe, resume ou melhora a linguagem dentro desses limites.

## 4. Fluxo LangGraph

### 4.1 Planejamento do grafo

O `LangGraph` faz primeiro o planejamento do turno, e so depois executa a estrategia escolhida.

```mermaid
flowchart TD
    A["Request"] --> B["classify_request"]
    B --> C["security_gate"]
    C --> D["route_request"]
    D --> E["select_slice"]

    E -->|public| P["public_slice"]
    E -->|protected| R["protected_slice"]
    E -->|support| S["support_slice"]
    E -->|deny| X["deny"]
    E -->|clarify| Y["clarify"]

    P --> P1["structured_tool_call"]
    P --> P2["hybrid_retrieval"]
    P --> P3["graph_rag_retrieval"]

    R --> R1["structured_tool_call"]
    R1 --> R2{"HITL habilitado e elegivel?"}
    R2 -- Sim --> R3["protected_human_review"]
    R2 -- Nao --> R4["complete"]

    S --> S1{"handoff ou structured_tool?"}
    S1 --> S2["handoff"]
    S1 --> S3["structured_tool_call"]
    S2 --> S4{"HITL support?"}
    S3 --> S4
    S4 -- Sim --> S5["support_human_review"]
    S4 -- Nao --> S6["complete"]
```

### 4.2 O que acontece depois do preview

Depois que o preview do grafo define o modo, o runtime executa uma de quatro familias:

```mermaid
flowchart LR
    Preview["Preview LangGraph"] --> A{"mode"}
    A -->|structured_tool| B["Chama tools internas<br/>via api-core"]
    A -->|hybrid_retrieval| C["Busca em Qdrant + PostgreSQL FTS"]
    A -->|graph_rag| D["Consulta artefatos GraphRAG"]
    A -->|clarify| E["Resposta curta de clarificacao"]
    A -->|deny| F["Negacao segura"]
    A -->|handoff| G["Abre ticket e encaminha humano"]

    B --> H["Composicao final"]
    C --> H
    D --> H
    E --> H
    F --> H
    G --> H

    H --> I["Persistencia de trace + memoria curta + resposta"]
```

### 4.3 Quando LangGraph usa retrieval

```mermaid
flowchart TD
    Q["Pergunta publica"] --> A{"Fato publico canonicamente estruturado?"}
    A -- Sim --> B["structured_tool_call<br/>profile / timeline / directory / calendar"]
    A -- Nao --> C{"Pergunta exige visao multi-documento?"}
    C -- Sim --> D["graph_rag_retrieval"]
    C -- Nao --> E["hybrid_retrieval"]

    E --> E1["lexical_search no Postgres FTS"]
    E --> E2["vector_search no Qdrant"]
    E1 --> E3["fusao por RRF"]
    E2 --> E3
    E3 --> E4["citacoes + answerability checks"]
    E4 --> F["composicao final"]

    D --> D1["run_graph_rag_query"]
    D1 --> D2{"retornou resposta?"}
    D2 -- Sim --> F
    D2 -- Nao --> E
```

### 4.4 Fontes de verdade do LangGraph

```mermaid
flowchart LR
    LG["LangGraph runtime"] -->|structured tools| API["api-core interno"]
    API --> ID["identity-service"]
    API --> AC["academic-service"]
    API --> FI["finance-service"]
    API --> CA["calendar-service"]
    API --> TK["ticket/workflow services"]
    ID --> PG["Postgres + RLS"]
    AC --> PG
    FI --> PG
    CA --> PG
    TK --> PG

    LG -->|hybrid retrieval| QD["Qdrant"]
    LG -->|lexical retrieval| FTS["Postgres FTS"]
    LG -->|advanced mode| GR["GraphRAG workspace"]
```

## 5. Fluxo CrewAI

No runtime principal, o `CrewAI` entra por um engine adapter que escolhe o slice e chama o piloto remoto isolado.

```mermaid
flowchart TD
    A["/v1/messages/respond"] --> B["CrewAIEngine"]
    B --> C["infer_request_slice"]
    C --> D["POST /v1/shadow/public"]
    C --> E["POST /v1/shadow/protected"]
    C --> F["POST /v1/shadow/support"]
    C --> G["POST /v1/shadow/workflow"]

    D --> H["ai-orchestrator-crewai"]
    E --> H
    F --> H
    G --> H

    H --> I{"answer_text valido?"}
    I -- Sim --> J["persist trace + resposta"]
    I -- Nao --> K["fallback explicito para LangGraph"]
```

### 5.1 Slice `public` no CrewAI

```mermaid
flowchart TD
    A["PublicShadowFlow.prepare_context"] --> B["Busca evidencias publicas<br/>school-profile / org-directory / timeline / calendar"]
    B --> C{"Fast path stateful ou deterministico?"}
    C -- Sim --> D["handle_fast_path"]
    C -- Nao --> E["Monta shortlist de evidencias"]
    E --> F["planner task"]
    F --> G["composer task"]
    G --> H["judge task"]
    H --> I{"guardrails passaram?"}
    I -- Sim --> J["resposta grounded"]
    I -- Nao --> K["deterministic backstop"]
```

Caracteristicas:

- usa `Flow` com estado persistido;
- usa evidencias publicas do `api-core`, nao banco direto;
- faz `planner -> composer -> judge` apenas quando fast path nao resolve;
- usa guardrails e backstop para evitar drift.

### 5.2 Slice `protected` no CrewAI

```mermaid
flowchart TD
    A["ProtectedShadowFlow.prepare_context"] --> B["Carrega identity context<br/>via api-core"]
    B --> C["Resolve aluno em foco"]
    C --> D["Enriquece mensagem com memoria curta"]
    D --> E{"Auth / identity / student fast path?"}
    E -- Sim --> F["backstop protegido deterministico"]
    E -- Nao --> G["Busca evidencias protegidas minimizadas"]
    G --> H["planner"]
    H --> I["composer"]
    I --> J["judge + guardrails"]
    J --> K{"precisa HITL?"}
    K -- Sim --> L["pending review / resume"]
    K -- Nao --> M["resposta final"]
```

Caracteristicas:

- fonte de verdade continua sendo `api-core`;
- o flow persiste `student focus`, `domain` e `attribute`;
- quando o caso e sensivel, entra `HITL` em vez de arriscar resposta errada;
- se o caminho agentic falha, o piloto devolve fallback seguro, nao `500`.

### 5.3 Slice `support` no CrewAI

```mermaid
flowchart TD
    A["SupportShadowFlow.prepare_context"] --> B["Le ticket/protocolo atual<br/>/v1/internal/workflows/status"]
    B --> C{"repair / handoff / protocolo / status / resumo"}
    C --> D["repair"]
    C --> E["handoff"]
    C --> F["protocol"]
    C --> G["status"]
    C --> H["summary"]
    E --> I["POST interno para abrir ou atualizar handoff"]
    D --> J["deterministic_render_result"]
    F --> J
    G --> J
    H --> J
    I --> J
```

Caracteristicas:

- `support` usa `Flow` para continuidade de estado;
- mas a linguagem final e leve e deterministica, para latencia baixa;
- nao usa crew pesado quando a operacao ja esta resolvida pelo `api-core`.

### 5.4 Slice `workflow` no CrewAI

```mermaid
flowchart TD
    A["WorkflowShadowFlow.prepare_context"] --> B["Le protocolo atual<br/>/v1/internal/workflows/status"]
    B --> C{"visita / protocolo / status / resumo / remarcar / cancelar / pedido"}
    C --> D["visit_create"]
    C --> E["visit_reschedule"]
    C --> F["visit_cancel"]
    C --> G["protocol_lookup"]
    C --> H["status_lookup"]
    C --> I["summary_lookup"]
    C --> J["request_create / request_update"]
    D --> K["POST interno no api-core"]
    E --> K
    F --> K
    J --> K
    G --> L["render deterministico"]
    H --> L
    I --> L
    K --> L
```

## 6. CrewAI e Fontes de Verdade

```mermaid
flowchart LR
    CE["CrewAI pilot"] --> PUB["public endpoints do api-core"]
    CE --> PROT["identity + dados protegidos minimizados"]
    CE --> WF["workflow/status/handoff endpoints"]

    PUB --> API["api-core"]
    PROT --> API
    WF --> API

    API --> PG["Postgres + RLS"]
    API --> CAL["Calendario / services internos"]

    CE --> LLM["Gemini / provider configurado"]
    LLM -. apenas compoe .-> API
```

Ponto importante:

- no desenho atual, o `CrewAI` nao faz `hybrid retrieval` em `Qdrant` para o slice publico;
- ele usa evidencias publicas canonicamente montadas pelo `api-core`;
- o modo `GraphRAG` tambem nao roda dentro do piloto `CrewAI` hoje;
- ou seja, o piloto e forte em `Flow`, estado, guardrails e composicao, mas o plano de retrieval avancado continua concentrado no runtime `LangGraph`.

## 7. Quando o Sistema Usa Cada Estrategia de Dados

```mermaid
flowchart TD
    Q["Pergunta do usuario"] --> A{"Dado estruturado e de sistema?"}
    A -- Sim --> B["Tool deterministica via api-core"]
    A -- Nao --> C{"E um fato publico canonico?"}
    C -- Sim --> D["Public endpoint canonico"]
    C -- Nao --> E{"Precisa busca documental?"}
    E -- Sim --> F{"Pergunta simples ou media?"}
    F -- Sim --> G["Hybrid retrieval<br/>Qdrant + Postgres FTS"]
    F -- Nao --> H["GraphRAG<br/>se habilitado"]
    E -- Nao --> I["Resposta curta / clarify / deny / handoff"]
```

Resumo pratico:

- `tool deterministica`: notas, faltas, financeiro, identidade, protocolo, visita, handoff;
- `public endpoint canonico`: perfil da escola, diretorio, timeline, calendario publico;
- `hybrid retrieval`: documentos institucionais e FAQ mais aberta;
- `GraphRAG`: visao global do corpus, conexao entre varios documentos.

## 8. Diferenca Conceitual Entre as Duas Stacks

```mermaid
flowchart LR
    subgraph LG["LangGraph"]
        LG1["State machine principal"]
        LG2["Subgraphs por slice"]
        LG3["Hybrid retrieval + GraphRAG"]
        LG4["HITL nativo com interrupt/resume"]
    end

    subgraph CE["CrewAI"]
        CE1["Servico isolado"]
        CE2["Flow persistido por slice"]
        CE3["planner / composer / judge"]
        CE4["guardrails + listeners + backstops"]
    end

    LG1 --> LG2 --> LG3 --> LG4
    CE1 --> CE2 --> CE3 --> CE4
```

Leitura curta:

- `LangGraph` concentra o plano completo de orquestracao e retrieval;
- `CrewAI` concentra `Flow`, continuidade de estado, composicao agentic e guardrails por slice;
- ambos compartilham contratos, auth, traces e fontes de verdade.

## 9. Onde Procurar no Codigo

- entrada principal: [main.py](/home/edann/projects/eduassist-platform/apps/ai-orchestrator/src/ai_orchestrator/main.py)
- selecao de stack e canario: [engine_selector.py](/home/edann/projects/eduassist-platform/apps/ai-orchestrator/src/ai_orchestrator/engine_selector.py)
- grafo LangGraph: [graph.py](/home/edann/projects/eduassist-platform/apps/ai-orchestrator/src/ai_orchestrator/graph.py)
- runtime LangGraph e composicao: [runtime.py](/home/edann/projects/eduassist-platform/apps/ai-orchestrator/src/ai_orchestrator/runtime.py)
- runtime de checkpoint/HITL LangGraph: [langgraph_runtime.py](/home/edann/projects/eduassist-platform/apps/ai-orchestrator/src/ai_orchestrator/langgraph_runtime.py)
- adapter CrewAI no orquestrador: [crewai_engine.py](/home/edann/projects/eduassist-platform/apps/ai-orchestrator/src/ai_orchestrator/engines/crewai_engine.py)
- servico isolado CrewAI: [main.py](/home/edann/projects/eduassist-platform/apps/ai-orchestrator-crewai/src/ai_orchestrator_crewai/main.py)
- flow publico CrewAI: [public_flow.py](/home/edann/projects/eduassist-platform/apps/ai-orchestrator-crewai/src/ai_orchestrator_crewai/public_flow.py)
- flow protegido CrewAI: [protected_flow.py](/home/edann/projects/eduassist-platform/apps/ai-orchestrator-crewai/src/ai_orchestrator_crewai/protected_flow.py)
- flow de suporte CrewAI: [support_flow.py](/home/edann/projects/eduassist-platform/apps/ai-orchestrator-crewai/src/ai_orchestrator_crewai/support_flow.py)
- flow de workflow CrewAI: [workflow_flow.py](/home/edann/projects/eduassist-platform/apps/ai-orchestrator-crewai/src/ai_orchestrator_crewai/workflow_flow.py)
- ADR de retrieval: [0002-retrieval-and-agent-runtime.md](/home/edann/projects/eduassist-platform/docs/adr/0002-retrieval-and-agent-runtime.md)

## 10. Regra de Ouro

Se surgir duvida sobre "de onde veio essa resposta?", siga esta ordem:

1. verifique qual stack respondeu;
2. descubra o slice;
3. descubra o modo:
   - `structured_tool`
   - `hybrid_retrieval`
   - `graph_rag`
   - `clarify`
   - `handoff`
4. so depois olhe para a LLM.

Na maior parte dos casos, o erro esta em:

- roteamento errado;
- contexto errado;
- fonte de verdade errada;
- ou retrieval inadequado para a pergunta.

Nao comeca na LLM.
