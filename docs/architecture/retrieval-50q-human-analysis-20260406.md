# Leitura Humana da Bateria 50Q Complementar

## Contexto

Este relatório registra a leitura humana da bateria `50Q` inédita rodada em `2026-04-06` como validação complementar de estresse do EduAssistAI. A `30Q v4` continua sendo o benchmark principal de referência do TCC. A `50Q` foi usada aqui para ampliar variedade de slices, aumentar a presença de casos restritos e tensionar follow-ups, agregados protegidos, `known unknowns` e perguntas sobre conteúdos que o sistema não deveria possuir ou não deveria expor.

Artefatos-base:

- dataset: [retrieval_50q_probe_cases.generated.20260406.json](/home/edann/projects/eduassist-platform/tests/evals/datasets/retrieval_50q_probe_cases.generated.20260406.json)
- relatório quantitativo: [retrieval-50q-cross-path-report-20260406.md](/home/edann/projects/eduassist-platform/docs/architecture/retrieval-50q-cross-path-report-20260406.md)
- relatório quantitativo json: [retrieval-50q-cross-path-report-20260406.json](/home/edann/projects/eduassist-platform/docs/architecture/retrieval-50q-cross-path-report-20260406.json)

## Resultado quantitativo resumido

- `langgraph`: `50/50`, `keyword pass 38/50`, `quality_avg 91.8`, `1251.2 ms`
- `python_functions`: `50/50`, `keyword pass 41/50`, `quality_avg 93.0`, `1082.2 ms`
- `llamaindex`: `50/50`, `keyword pass 38/50`, `quality_avg 92.0`, `1184.4 ms`
- `specialist_supervisor`: `50/50`, `keyword pass 39/50`, `quality_avg 92.4`, `1955.2 ms`

Distribuição da bateria:

- `29` casos públicos
- `12` casos protegidos
- `9` casos restritos

Leitura global importante:

- `34` prompts ficaram com `quality 100` nos quatro caminhos.
- `16` prompts concentraram todo o backlog residual da rodada.
- Não houve falha de runtime em nenhum dos quatro stacks.

## Método de leitura humana

As `200` respostas finais foram revisadas a partir do JSON e do markdown gerados pelo runner oficial. A leitura humana foi organizada em dois níveis:

1. leitura global das respostas convergentes, para verificar se os `100` automáticos correspondiam a respostas realmente boas e grounded;
2. leitura detalhada de todos os casos com `quality < 100`, para separar:
   - mismatch lexical de rubric;
   - clarificação excessiva;
   - erro real de domínio;
   - falha de agregação;
   - regressão de policy ou restricted access.

Essa distinção importa porque a `50Q` expôs tanto resíduos reais de produto quanto perdas de score que, para um humano, são menores e não invalidam totalmente a resposta.

## Leitura geral das 200 respostas

Em `136` respostas distribuídas em `34` prompts, houve convergência semântica forte entre os quatro caminhos. Esses casos cobriram:

- políticas públicas e encadeamentos institucionais;
- timeline pública e onboarding;
- bundles públicos profundos;
- `known unknowns` públicos;
- upcoming assessments protegidas;
- panorama financeiro familiar;
- negativas seguras em casos restritos claramente proibidos.

Nesses blocos, a arquitetura final se comportou de forma madura. As respostas ficaram concretas, grounded, adaptadas ao que foi perguntado e sem vazamento de assunto anterior. Em outras palavras, a `50Q` confirma que o sistema não depende mais de “acertar por sorte” em slices fáceis: ele sustenta um corpo amplo de respostas boas em público e protegido.

## Principais padrões positivos

### 1. Público aberto amadurecido

Casos como `public_policy_bridge`, `public_family_new_bundle`, `public_visibility_boundary`, `public_health_emergency_bundle`, `public_integral_study_support`, `public_inclusion_accessibility` e `public_known_unknown_*` ficaram bons de verdade. A resposta final explica processo, fronteira de acesso e política pública sem inventar detalhes privados.

### 2. Protected SQL-backed já não colapsa

Casos como `protected_structured_finance`, `protected_structured_followup`, `protected_structured_upcoming_assessments`, `protected_structured_upcoming_assessments_followup`, `protected_structured_grade_components` e `protected_structured_finance_detail` ficaram corretos e úteis. O sistema finalmente consegue:

- trabalhar com agregados familiares;
- recortar o follow-up para um aluno;
- responder com base em dados transacionais sem virar SQL cru ou texto genérico.

### 3. Known unknown honesto

A bateria confirma uma virtude importante: quando o dado não está publicado, o sistema agora tende a dizer isso explicitamente. Isso apareceu bem em `public_known_unknown_total_teachers`, `public_known_unknown_library_books`, `public_known_unknown_minimum_age` e `public_known_unknown_cafeteria_menu`.

## Backlog residual: análise detalhada

Os `16` prompts abaixo de `100` se concentram em seis famílias de problema.

### 1. Colisão entre processos públicos e pricing

Casos:

- `public_process_compare`
- `public_pricing_projection`

Leitura humana:

- `public_process_compare` falhou de forma real nos quatro caminhos. A pergunta comparava `rematrícula`, `transferência` e `cancelamento`, mas todos responderam com tabela pública de preços.
- `public_pricing_projection` também falhou nos quatro caminhos. O sistema respondeu apenas a taxa de matrícula, assumiu `Ensino Fundamental II` como default e não entregou o `total por mês para 3 filhos`, que era o centro da pergunta.

Causa provável:

- há um atrator compartilhado excessivamente forte em torno de `matrícula`;
- a resolução pública ainda cola `matrícula` com `pricing` cedo demais;
- falta distinguir melhor `processo administrativo` de `simulação financeira pública`.

Classificação:

- erro real de domínio, não apenas mismatch de rubric.

### 2. Agregados protegidos ainda incompletos em alguns casos

Casos:

- `protected_structured_academic`
- `protected_structured_attendance_family`
- `protected_admin_finance_combo`
- `protected_administrative_self_status`
- `protected_structured_attendance_detail`

Leitura humana:

- `protected_structured_academic`: `llamaindex` e `specialist_supervisor` responderam melhor; `langgraph` e `python_functions` acertaram quem é mais vulnerável, mas omitiram `Ana`, perdendo o caráter comparativo do panorama.
- `protected_structured_attendance_family`: os quatro caminhos fizeram clarificação desnecessária em vez de resumir os dois filhos.
- `protected_admin_finance_combo`: os quatro caminhos responderam só o financeiro, ignorando o bloco administrativo e a pergunta sobre `bloqueio de atendimento`.
- `protected_administrative_self_status`: `langgraph` e `llamaindex` caíram em financeiro, enquanto `python_functions` e `specialist_supervisor` responderam corretamente.
- `protected_structured_attendance_detail`: os quatro caminhos trouxeram contagens de presença/falta/atraso, mas não transformaram isso em “principal alerta”, que era o recorte pedido.

Causa provável:

- os reducers agregados protegidos ainda não estão consistentes em todos os domínios;
- o sistema resolve bem `panorama por aluno`, mas ainda não interpreta de forma uniforme perguntas do tipo `junte`, `resuma`, `diga o principal alerta`;
- ainda falta um passo interpretativo leve sobre dados estruturados em alguns caminhos.

Classificação:

- erro real de produto, com gravidade moderada.

### 3. Público bom semanticamente, mas com perdas lexicais ou clarificação excessiva

Casos:

- `public_documents_credentials`
- `public_calendar_week`
- `public_governance_protocol`

Leitura humana:

- `public_documents_credentials`: `langgraph`, `llamaindex` e `specialist_supervisor` ficaram semanticamente corretos, mas perderam no rubric por não explicitar tão bem `credenciais`; o `python_functions` foi o melhor wording do grupo.
- `public_calendar_week`: `langgraph` e `python_functions` pediram clarificação demais para uma pergunta que já permitia responder; `llamaindex` ficou fraco demais e tratou a agenda como inexistente; `specialist_supervisor` acertou.
- `public_governance_protocol`: o `llamaindex` respondeu algo útil, mas abriu demais o escopo e perdeu aderência lexical; os demais ficaram melhores.

Causa provável:

- a camada final grounded está boa para adaptação, mas alguns caminhos ainda subestimam perguntas públicas curtas ou pouco específicas;
- o rubric capturou parte disso, mas nem todo caso abaixo de `100` aqui representa erro grave.

Classificação:

- mistura de mismatch lexical com resíduos pequenos de UX.

### 4. Restricted com policy e no-match ainda instáveis

Casos:

- `restricted_doc_positive` sobre manual do professor
- `restricted_doc_positive_teacher_feedback`
- `restricted_doc_positive_scope_protocol_variant`
- `restricted_doc_negative_exchange_program`
- parte de `restricted_doc_negative`

Leitura humana:

- `restricted_doc_positive` sobre `Manual interno do professor` falhou nos quatro caminhos por um motivo ruim: `Professor` foi tratado como se fosse um aluno não vinculado.
- `restricted_doc_positive_teacher_feedback` e `restricted_doc_positive_scope_protocol_variant` foram negados pelos quatro caminhos, embora o contexto do dataset trouxesse escopo restrito positivo. Isso sugere regressão de policy resolution ou priorização excessiva do deny path.
- `restricted_doc_negative_exchange_program` também caiu em negação de acesso nos quatro caminhos, quando a melhor resposta seria: “com o escopo atual, não encontrei esse material interno”.
- no caso `restricted_doc_negative`, `python_functions` e `llamaindex` entregaram o wording mais preciso; `langgraph` e `specialist_supervisor` ficaram corretos para humano, mas lexicalmente mais fracos.

Causa provável:

- o slice restrito continua sendo o mais frágil;
- há uma mistura de:
  - entity parsing indevido;
  - policy path agressivo demais;
  - pouca diferenciação entre `restricted positive no-match` e `restricted denied`.

Classificação:

- esse é o backlog residual mais importante da `50Q`.

### 5. Specialist forte no protegido, mas não dominante no restante

Leitura humana:

- `specialist_supervisor` teve a melhor média no slice protegido (`95.7`), o que confirma sua vocação `quality-first` em perguntas estruturadas e contextualizadas.
- No slice restrito, porém, ele foi o pior (`70.3`) e isso enfraquece a ideia de usá-lo como caminho universal.
- Em público, continuou bom, mas com latência significativamente maior.

Classificação:

- o specialist ficou forte onde há benefício claro de raciocínio e contexto, mas não é o caminho mais equilibrado para tudo.

### 6. Python puro teve a melhor rodada agregada

Leitura humana:

- `python_functions` terminou esta `50Q` com a maior média global (`93.0`) e a menor latência média (`1082.2 ms`).
- Isso não invalida o papel do `langgraph` como caminho mais auditável e bem equilibrado na narrativa principal do TCC, mas mostra que a rodada complementar de estresse favoreceu o baseline code-first.

Classificação:

- isso deve aparecer no texto acadêmico como nuance importante, e não como contradição.

## Síntese interpretativa

A `50Q` complementar mostra um sistema que já está sólido em `public` e `protected`, mas ainda incompleto em `restricted` e em algumas perguntas compostas que exigem:

- melhor diferenciação entre processo público e pricing;
- agregação protegida mais rica;
- interpretação mais semântica de alertas estruturados;
- distinção mais clara entre `deny`, `no-match` e `allowed but unavailable` no slice restrito.

O mais importante é que a `50Q` não desmonta a tese do trabalho. Ao contrário, ela a refina. O experimento mostra que:

- a arquitetura final resolveu a maioria dos problemas reais que apareciam no Telegram e nos ciclos anteriores;
- a `30Q v4` continua válida como benchmark de referência;
- a `50Q` é útil como rodada de estresse porque expõe onde a robustez ainda não é uniforme.

## Veredito humano

Como leitura humana das `200` respostas:

- a plataforma está madura para slices públicos e protegidos;
- a comparação entre quatro caminhos continua válida e informativa;
- o backlog residual agora está concentrado e compreensível, não espalhado de forma caótica;
- o slice restrito e alguns casos compostos ainda requerem trabalho adicional antes de se poder afirmar robustez homogênea em toda a superfície experimental.

Em termos práticos, a `50Q` complementar não substitui a `30Q v4` como benchmark principal do TCC. Ela cumpre melhor um papel de validação ampla e de identificação honesta do backlog restante.
