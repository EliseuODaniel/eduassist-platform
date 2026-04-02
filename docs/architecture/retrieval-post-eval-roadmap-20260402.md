# Retrieval Post-Eval Roadmap

Date: 2026-04-02

Base de evidência:
- [retrieval-30q-cross-path-report-20260402.md](/home/edann/projects/eduassist-platform/docs/architecture/retrieval-30q-cross-path-report-20260402.md)
- [retrieval-30q-cross-path-report-20260402.json](/home/edann/projects/eduassist-platform/docs/architecture/retrieval-30q-cross-path-report-20260402.json)
- [retrieval-30q-final-stage-report-20260402.md](/home/edann/projects/eduassist-platform/docs/architecture/retrieval-30q-final-stage-report-20260402.md)

## Objective

Fechar o gap restante entre qualidade, latência e robustez operacional nos caminhos:
- `specialist_supervisor`
- `python_functions`
- `langgraph`
- `llamaindex`

Sem reinvestimento principal em `crewai`, que fica como baseline comparativa.

## How To Read This Roadmap

- `P0`: maior ROI imediato
- `P1`: próximo degrau que melhora qualidade sem destruir latência
- `P2`: refinamentos estruturais depois que os gaps mais óbvios estiverem fechados

Critérios de ROI:
- frequência do problema no 30Q
- impacto na experiência
- chance de corrigir com mudança localizada
- risco de regressão
- impacto em múltiplos caminhos

## Cross-Stack Priorities

### `P0` Teacher directory boundary

Problema:
- `Q222` falhou nos 4 caminhos prioritários.
- Em alguns casos houve vazamento de canais gerais ou resposta errada em vez de boundary pública clara.

Solução:
- transformar `teacher_directory` em lane canônica compartilhada de boundary
- resposta padrão:
  - não divulga contato direto de professor
  - encaminha para coordenação pedagógica ou setor institucional correto
- impedir fallback para diretório genérico ou canais institucionais amplos quando a pergunta for sobre contato individual de docente

Arquivos candidatos:
- [public_doc_knowledge.py](/home/edann/projects/eduassist-platform/apps/ai-orchestrator/src/ai_orchestrator/public_doc_knowledge.py)
- [runtime.py](/home/edann/projects/eduassist-platform/apps/ai-orchestrator/src/ai_orchestrator/runtime.py)
- [graph.py](/home/edann/projects/eduassist-platform/apps/ai-orchestrator/src/ai_orchestrator/graph.py)
- [python_functions_native_runtime.py](/home/edann/projects/eduassist-platform/apps/ai-orchestrator/src/ai_orchestrator/python_functions_native_runtime.py)
- [llamaindex_native_runtime.py](/home/edann/projects/eduassist-platform/apps/ai-orchestrator/src/ai_orchestrator/llamaindex_native_runtime.py)

### `P0` Follow-up protected disambiguation

Problema:
- `Q213` ainda falhou em `specialist_supervisor`, `python_functions`, `langgraph` e `llamaindex`.
- O problema restante não é retrieval; é policy de clarificação excessiva em follow-up protegido.

Solução:
- quando a thread anterior já fixou o aluno e o domínio, follow-up tipo:
  - "agora foque só na Ana"
  - "isole a Ana"
  - "pontos que mais preocupam"
  deve reciclar contexto em vez de clarificar
- fortalecer a política de `resolved_turn + operational memory` antes de qualquer fallback de ambiguidade

Arquivos candidatos:
- [runtime.py](/home/edann/projects/eduassist-platform/apps/ai-orchestrator/src/ai_orchestrator/runtime.py)
- [graph.py](/home/edann/projects/eduassist-platform/apps/ai-orchestrator/src/ai_orchestrator/graph.py)
- [kernel_runtime.py](/home/edann/projects/eduassist-platform/apps/ai-orchestrator/src/ai_orchestrator/kernel_runtime.py)
- [runtime.py](/home/edann/projects/eduassist-platform/apps/ai-orchestrator-specialist/src/ai_orchestrator_specialist/runtime.py)

### `P1` Rubric-aware public canonical expansion

Problema:
- vários `80` do 30Q foram casos em que o caminho acertou a resposta, mas deixou de verbalizar um termo esperado do rubric novo:
  - `public_academic_policy_overview`
  - `public_conduct_frequency_punctuality`
  - `public_year_three_phases`
  - `public_bolsas_and_processes`
  - `public_pricing_projection`

Solução:
- expandir bundles públicos canônicos já existentes
- preservar o factual atual, mas incluir wording mais completo e estável para:
  - `media`
  - `frequencia`
  - `pontualidade`
  - `bolsas`
  - `cancelamento`
  - `por mes`
  - `admissao / rotina academica / fechamento`

Arquivos candidatos:
- [public_doc_knowledge.py](/home/edann/projects/eduassist-platform/apps/ai-orchestrator/src/ai_orchestrator/public_doc_knowledge.py)
- [public_doc_knowledge.py](/home/edann/projects/eduassist-platform/apps/ai-orchestrator-specialist/src/ai_orchestrator_specialist/public_doc_knowledge.py)

## Path-Specific Roadmap

### `specialist_supervisor`

Status atual:
- melhor qualidade geral: `96.1`
- melhor keyword pass: `26/30`
- mediana muito boa: `125.1 ms`
- problema restante: cauda longa pública

Principais falhas:
- `Q206` `public_process_compare`
- `Q213` `protected_structured_followup`
- `Q222` `public_teacher_directory`
- `Q226` `public_conduct_frequency_punctuality`

#### `P0`
- adicionar preflight/fast path para:
  - `public_process_compare`
  - `public_calendar_week`
  - `public_visibility_boundary`
  - `public_teacher_directory`
- impedir que esses casos caiam em `institution_specialist` quando já existe bundle público suficiente

#### `P1`
- endurecer reuse de contexto para `protected_structured_followup`
- se a memória já fixou `Ana Oliveira`, responder direto

#### `P1`
- reduzir ainda mais cauda longa de público canônico:
  - fail-fast de `institution_specialist`
  - budget mais curto para `public_documental_complex`
  - degrade para resposta grounded canônica antes de especialista premium

#### `P2`
- tracing por estágio no relatório oficial dos 5 caminhos:
  - planner
  - tool_first
  - specialist
  - manager
  - judge
- usar isso para matar o `P95`, não só a média

ROI:
- muito alto para `P95`
- médio para qualidade absoluta, que já está alta

### `python_functions`

Status atual:
- melhor latência do projeto: `165.0 ms`
- boa qualidade geral: `91.7`
- principal valor: melhor equilíbrio produção síncrona

Principais falhas:
- `Q213` `protected_structured_followup`
- `Q222` `public_teacher_directory`
- `Q223` `public_calendar_week`
- `Q224` `public_year_three_phases`
- `Q225` `public_academic_policy_overview`
- `Q226` `public_conduct_frequency_punctuality`
- `Q227` `public_bolsas_and_processes`
- `Q228` `public_pricing_projection`
- `Q230` `protected_admin_finance_combo`

#### `P0`
- ampliar lanes determinísticas públicas para os 6 novos tipos:
  - `calendar_week`
  - `year_three_phases`
  - `academic_policy_overview`
  - `conduct_frequency_punctuality`
  - `bolsas_and_processes`
  - `pricing_projection`

#### `P0`
- corrigir `teacher_directory` com deny/boundary explícito compartilhado

#### `P1`
- corrigir `protected_admin_finance_combo`
- hoje ele responde só a parte administrativa em alguns casos
- deve usar serviço combinado, como já faz o caminho 5

#### `P1`
- reduzir clarificação indevida no follow-up protegido

ROI:
- altíssimo
- esse é o caminho com melhor chance de subir qualidade sem pagar custo estrutural

### `langgraph`

Status atual:
- qualidade sólida: `92.5`
- latência intermediária: `1178.1 ms`
- melhor stack “intermediária” do projeto

Principais falhas:
- `Q205` `public_permanence_support`
- `Q213` `protected_structured_followup`
- `Q215` `protected_structured_admin`
- `Q222` `public_teacher_directory`
- `Q224` `public_year_three_phases`
- `Q225` `public_academic_policy_overview`
- `Q226` `public_conduct_frequency_punctuality`
- `Q227` `public_bolsas_and_processes`
- `Q228` `public_pricing_projection`

#### `P0`
- expandir `public canonical lanes` antes do grafo para os novos tipos públicos
- o grafo não deve entrar onde já existe fato institucional canônico e barato

#### `P0`
- corrigir teacher-directory boundary compartilhado

#### `P1`
- revisar o bridge entre classificação protegida e lanes públicas
- no 30Q ainda há sinais de “superestimar autenticação” em perguntas públicas

#### `P1`
- follow-up protegido:
  - reusar `resolved_turn`
  - evitar correção excessiva do domínio que apaga contexto anterior

#### `P2`
- restricted positive search ainda tem cauda alta
- vale aplicar cache/warm path semelhante ao caminho 5

ROI:
- alto
- bom candidato para continuar como stack intermediária robusta

### `llamaindex`

Status atual:
- qualidade empatada com `langgraph`: `92.5`
- mediana boa: `139.9 ms`
- problema principal: `P95` muito ruim

Principais falhas:
- `Q213` `protected_structured_followup`
- `Q222` `public_teacher_directory`
- `Q223` `public_calendar_week`
- `Q224` `public_year_three_phases`
- `Q225` `public_academic_policy_overview`
- `Q226` `public_conduct_frequency_punctuality`
- `Q227` `public_bolsas_and_processes`
- `Q228` `public_pricing_projection`
- `Q230` `protected_admin_finance_combo`

#### `P0`
- impedir fallback para `public_profile` em casos públicos canônicos que agora já têm lane clara
- teacher-directory, service-routing, calendar-week e year-three-phases devem resolver por lane determinística antes de qualquer caminho mais pesado

#### `P0`
- corrigir `teacher_directory` boundary compartilhado

#### `P1`
- follow-up protegido:
  - herdar aluno já resolvido
  - evitar cair em `public_profile` em thread protegida

#### `P1`
- `protected_admin_finance_combo`
- chamar serviço combinado ou compor dois serviços determinísticos
- não devolver só o bloco administrativo

#### `P2`
- atacar P95:
  - warm cache do embedder
  - evitar query stack pesada em bundles públicos simples
  - revisar path de `public_profile`

ROI:
- alto para robustez
- médio para latência média
- muito alto para `P95`

## Execution Order

### Wave 1
- teacher-directory boundary compartilhado
- follow-up protegido sem clarificação indevida
- expansão de lanes públicas canônicas em `python_functions`, `langgraph` e `llamaindex`

### Wave 2
- `specialist_supervisor`:
  - `public_process_compare`
  - `public_calendar_week`
  - `public_visibility_boundary`
- `python_functions` e `llamaindex`:
  - `protected_admin_finance_combo`

### Wave 3
- `P95` hardening:
  - `specialist_supervisor` público complexo
  - `langgraph` restricted positive
  - `llamaindex` public_profile fallback

## Success Criteria

- `specialist_supervisor`
  - manter `quality >= 96`
  - baixar `p95` de público canônico para abaixo de `2.5s`

- `python_functions`
  - subir para `quality >= 94`
  - manter média abaixo de `220 ms`

- `langgraph`
  - subir para `quality >= 94`
  - manter média abaixo de `1.2s`

- `llamaindex`
  - manter `quality >= 93`
  - baixar `p95` para abaixo de `4s`

## Final Recommendation

Se o projeto for atacar apenas um caminho por vez:
1. `python_functions`
2. `specialist_supervisor`
3. `langgraph`
4. `llamaindex`

Se o projeto quiser atacar primeiro o maior risco de experiência:
1. `teacher_directory` compartilhado
2. `follow-up protegido`
3. `specialist_supervisor` P95 público
4. `llamaindex` P95 público
