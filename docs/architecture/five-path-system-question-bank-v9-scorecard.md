# Five-Path System Question Bank v9 Scorecard

## Overall

| Stack | OK | Quality | Avg latency | Error types |
| --- | --- | --- | --- | --- |
| `langgraph` | `96/96` | `100.0` | `1030.9 ms` | `nenhum` |
| `crewai` | `96/96` | `100.0` | `4957.2 ms` | `nenhum` |
| `python_functions` | `96/96` | `100.0` | `173.6 ms` | `nenhum` |
| `llamaindex` | `96/96` | `100.0` | `1483.6 ms` | `nenhum` |
| `specialist_supervisor` | `96/96` | `100.0` | `2610.9 ms` | `nenhum` |

## Rankings

- qualidade: `python_functions`, `langgraph`, `llamaindex`, `specialist_supervisor`, `crewai`
- latencia: `python_functions`, `langgraph`, `llamaindex`, `specialist_supervisor`, `crewai`

## By Wave

### public_grounding

| Stack | OK | Quality | Avg latency |
| --- | --- | --- | --- |
| `langgraph` | `24/24` | `100.0` | `2264.9 ms` |
| `crewai` | `24/24` | `100.0` | `5905.9 ms` |
| `python_functions` | `24/24` | `100.0` | `151.7 ms` |
| `llamaindex` | `24/24` | `100.0` | `1485.1 ms` |
| `specialist_supervisor` | `24/24` | `100.0` | `774.4 ms` |

### public_graphrag

| Stack | OK | Quality | Avg latency |
| --- | --- | --- | --- |
| `langgraph` | `8/8` | `100.0` | `397.0 ms` |
| `crewai` | `8/8` | `100.0` | `7810.5 ms` |
| `python_functions` | `8/8` | `100.0` | `130.9 ms` |
| `llamaindex` | `8/8` | `100.0` | `152.9 ms` |
| `specialist_supervisor` | `8/8` | `100.0` | `290.6 ms` |

### protected_ops

| Stack | OK | Quality | Avg latency |
| --- | --- | --- | --- |
| `langgraph` | `32/32` | `100.0` | `386.9 ms` |
| `crewai` | `32/32` | `100.0` | `3745.7 ms` |
| `python_functions` | `32/32` | `100.0` | `178.9 ms` |
| `llamaindex` | `32/32` | `100.0` | `1111.4 ms` |
| `specialist_supervisor` | `32/32` | `100.0` | `3500.4 ms` |

### sensitive_external

| Stack | OK | Quality | Avg latency |
| --- | --- | --- | --- |
| `langgraph` | `16/16` | `100.0` | `1063.8 ms` |
| `crewai` | `16/16` | `100.0` | `6137.5 ms` |
| `python_functions` | `16/16` | `100.0` | `157.6 ms` |
| `llamaindex` | `16/16` | `100.0` | `3014.4 ms` |
| `specialist_supervisor` | `16/16` | `100.0` | `2614.6 ms` |

### teacher_workflow

| Stack | OK | Quality | Avg latency |
| --- | --- | --- | --- |
| `langgraph` | `16/16` | `100.0` | `751.7 ms` |
| `crewai` | `16/16` | `100.0` | `3350.2 ms` |
| `python_functions` | `16/16` | `100.0` | `233.0 ms` |
| `llamaindex` | `16/16` | `100.0` | `1360.6 ms` |
| `specialist_supervisor` | `16/16` | `100.0` | `4743.2 ms` |

## Notes

- CrewAI permanece no scorecard como baseline comparativa funcional, sem novos investimentos de arquitetura.
- Os caminhos ativos em evolucao sao langgraph, python_functions, llamaindex e specialist_supervisor.
- Erros operacionais como *_pilot_unavailable e runtime_unconfigured devem ser lidos separadamente de qualidade semantica.
- O benchmark context de cada onda deve ser consultado junto com o scorecard para interpretar drift de ambiente e modo de execucao.
