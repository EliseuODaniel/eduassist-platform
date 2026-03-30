# Fluxo Detalhado do CrewAI

## 1. Adapter no runtime principal

```mermaid
graph TD
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
```

## 2. Slice public

```mermaid
graph TD
    A["PublicShadowFlow.prepare_context"] --> B["Busca evidencias publicas"]
    B --> C{"Fast path stateful ou deterministico?"}
    C -- Sim --> D["handle_fast_path"]
    C -- Nao --> E["shortlist de evidencias"]
    E --> F["planner"]
    F --> G["composer"]
    G --> H["judge"]
    H --> I{"guardrails passaram?"}
    I -- Sim --> J["resposta grounded"]
    I -- Nao --> K["deterministic backstop"]
```

## 3. Slice protected

```mermaid
graph TD
    A["ProtectedShadowFlow.prepare_context"] --> B["Carrega identity context via api-core"]
    B --> C["Resolve aluno em foco"]
    C --> D["Enriquece mensagem com memoria curta"]
    D --> E{"Auth, identity ou student fast path?"}
    E -- Sim --> F["backstop protegido deterministico"]
    E -- Nao --> G["evidencias protegidas minimizadas"]
    G --> H["planner"]
    H --> I["composer"]
    I --> J["judge + guardrails"]
    J --> K{"precisa HITL?"}
    K -- Sim --> L["pending review / resume"]
    K -- Nao --> M["resposta final"]
```

Notas:

- o `CrewAI` roda em servico isolado
- `Flow` e persistido por slice
- quando o piloto nao consegue devolver `answer_text`, o adapter pode cair em fallback explicito
