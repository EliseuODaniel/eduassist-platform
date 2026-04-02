## Retrieval 26Q Final Stage Report

Date: `2026-04-02`

Dataset:
- [retrieval_26q_probe_cases.generated.20260402.json](/home/edann/projects/eduassist-platform/tests/evals/datasets/retrieval_26q_probe_cases.generated.20260402.json)

Raw artifacts:
- [retrieval-26q-cross-path-report-20260402.md](/home/edann/projects/eduassist-platform/docs/architecture/retrieval-26q-cross-path-report-20260402.md)
- [retrieval-26q-cross-path-report-20260402.json](/home/edann/projects/eduassist-platform/docs/architecture/retrieval-26q-cross-path-report-20260402.json)

### Executive Summary

A rodada `26Q` terminou com os `4` caminhos ativos em `100%` de qualidade média e `100%` de `keyword pass`.

Os quatro resíduos que estavam abertos foram corrigidos:
- `protected_structured_followup`
- `protected_structured_finance`
- `protected_structured_admin`
- `public_calendar_week`

Também corrigi duas regressões que apareceram na primeira rerrodada:
- `restricted_doc_positive` deixando de ser roubado por rescue protegido
- `restricted_doc_negative` deixando de escalar para `human_handoff` no `specialist_supervisor`

### Final Scoreboard

| Stack | OK | Keyword pass | Quality avg | Avg latency |
| --- | --- | --- | --- | --- |
| `langgraph` | `26/26` | `26/26` | `100.0` | `211.9 ms` |
| `python_functions` | `26/26` | `26/26` | `100.0` | `151.2 ms` |
| `llamaindex` | `26/26` | `26/26` | `100.0` | `131.3 ms` |
| `specialist_supervisor` | `26/26` | `26/26` | `100.0` | `1042.9 ms` |

### Tail Profile

| Stack | Median | P95 | Max |
| --- | --- | --- | --- |
| `langgraph` | `146.2 ms` | `289.6 ms` | `1278.2 ms` |
| `python_functions` | `123.0 ms` | `238.3 ms` | `240.4 ms` |
| `llamaindex` | `96.7 ms` | `239.7 ms` | `251.5 ms` |
| `specialist_supervisor` | `73.0 ms` | `8247.2 ms` | `16582.9 ms` |

### What Changed

Shared fixes:
- fortaleci o `protected domain rescue` para sair de `clarify/unknown` com segurança
- passei a tratar `institution` corretamente no rescue, sem cair no override financeiro
- endureci o matcher de `calendar_week` para o phrasing com `marcos` e `falam mais diretamente`
- removi `restricted document queries` da família de rescues protegidos

Path-specific fixes:
- `python_functions`: rescue protegido antes do fallback público contextual
- `langgraph`: passou a herdar o rescue protegido corrigido no runtime principal
- `llamaindex`: fast path protegido ampliado para follow-up acadêmico e agregado financeiro
- `specialist_supervisor`: heurística de `human_handoff` ficou mais estrita e parou de capturar consultas documentais

### Residual Technical Debt

Mesmo com `100/100`, ainda sobra um ponto de engenharia importante:
- `specialist_supervisor` continua com `tail latency` alta demais para alguns casos complexos

Top outliers do caminho 5 nesta rodada:
- `public_process_compare`: `16582.9 ms`
- `protected_structured_followup`: `8247.2 ms`

Então o problema restante já não é qualidade de resposta; é `P95/P99`.

### Final Practical Reading

Se a prioridade for `qualidade + velocidade + previsibilidade`, o ranking fica:
1. `llamaindex`
2. `python_functions`
3. `langgraph`
4. `specialist_supervisor`

Se a prioridade for `qualidade com espaço para raciocínio premium`, o caminho 5 continua forte, mas agora o gargalo está isolado em latência de cauda, não em roteamento ou grounding.
