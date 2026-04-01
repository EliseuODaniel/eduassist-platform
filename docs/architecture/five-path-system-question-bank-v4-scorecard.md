# Five-Path System Question Bank v4 Scorecard

## Overall

| Stack | OK | Quality | Avg latency | Error types |
| --- | --- | --- | --- | --- |
| `langgraph` | `96/96` | `99.9` | `1039.0 ms` | `repetitive_reply=1` |
| `crewai` | `96/96` | `99.9` | `5004.2 ms` | `repetitive_reply=1` |
| `python_functions` | `96/96` | `100.0` | `170.6 ms` | `nenhum` |
| `llamaindex` | `96/96` | `100.0` | `3107.8 ms` | `nenhum` |
| `specialist_supervisor` | `94/96` | `97.9` | `132.2 ms` | `request_failed=2` |

## Rankings

- qualidade: `python_functions`, `llamaindex`, `langgraph`, `crewai`, `specialist_supervisor`
- latencia: `specialist_supervisor`, `python_functions`, `langgraph`, `llamaindex`, `crewai`

## By Wave

### public_grounding

| Stack | OK | Quality | Avg latency |
| --- | --- | --- | --- |
| `langgraph` | `24/24` | `100.0` | `2314.9 ms` |
| `crewai` | `24/24` | `100.0` | `5945.7 ms` |
| `python_functions` | `24/24` | `100.0` | `149.1 ms` |
| `llamaindex` | `24/24` | `100.0` | `1457.9 ms` |
| `specialist_supervisor` | `24/24` | `100.0` | `126.0 ms` |

### public_graphrag

| Stack | OK | Quality | Avg latency |
| --- | --- | --- | --- |
| `langgraph` | `8/8` | `100.0` | `406.6 ms` |
| `crewai` | `8/8` | `100.0` | `7888.9 ms` |
| `python_functions` | `8/8` | `100.0` | `151.2 ms` |
| `llamaindex` | `8/8` | `100.0` | `138.0 ms` |
| `specialist_supervisor` | `8/8` | `100.0` | `89.8 ms` |

### protected_ops

| Stack | OK | Quality | Avg latency |
| --- | --- | --- | --- |
| `langgraph` | `32/32` | `100.0` | `372.6 ms` |
| `crewai` | `32/32` | `100.0` | `3759.0 ms` |
| `python_functions` | `32/32` | `100.0` | `178.3 ms` |
| `llamaindex` | `32/32` | `100.0` | `3821.8 ms` |
| `specialist_supervisor` | `30/32` | `93.8` | `146.8 ms` |

### sensitive_external

| Stack | OK | Quality | Avg latency |
| --- | --- | --- | --- |
| `langgraph` | `16/16` | `100.0` | `1011.0 ms` |
| `crewai` | `16/16` | `100.0` | `5897.1 ms` |
| `python_functions` | `16/16` | `100.0` | `170.0 ms` |
| `llamaindex` | `16/16` | `100.0` | `7184.3 ms` |
| `specialist_supervisor` | `16/16` | `100.0` | `135.8 ms` |

### teacher_workflow

| Stack | OK | Quality | Avg latency |
| --- | --- | --- | --- |
| `langgraph` | `16/16` | `99.4` | `801.9 ms` |
| `crewai` | `16/16` | `99.4` | `3746.9 ms` |
| `python_functions` | `16/16` | `100.0` | `197.9 ms` |
| `llamaindex` | `16/16` | `100.0` | `1562.9 ms` |
| `specialist_supervisor` | `16/16` | `100.0` | `129.8 ms` |

## Notes

- CrewAI permanece no scorecard como baseline comparativa funcional, sem novos investimentos de arquitetura.
- Os caminhos ativos em evolucao sao langgraph, python_functions, llamaindex e specialist_supervisor.
- Se um stack tiver request_failed ou *_pilot_unavailable, trate isso como sinal operacional separado de qualidade semantica.
- No protected_ops v4, a anomalia residual do specialist_supervisor vem do artifacto anterior ao carregamento automatico do .env no harness source-mode.
- Os casos Q039 e Q063 do specialist_supervisor foram retestados depois da correcao do harness e passaram com status 200.
