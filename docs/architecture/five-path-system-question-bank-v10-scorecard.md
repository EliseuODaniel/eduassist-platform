# Five-Path System Question Bank v10 Scorecard

## Overall

| Stack | OK | Quality | Avg latency | Error types |
| --- | --- | --- | --- | --- |
| `langgraph` | `96/96` | `100.0` | `982.8 ms` | `nenhum` |
| `crewai` | `96/96` | `100.0` | `4774.6 ms` | `nenhum` |
| `python_functions` | `96/96` | `100.0` | `148.6 ms` | `nenhum` |
| `llamaindex` | `96/96` | `100.0` | `1462.9 ms` | `nenhum` |
| `specialist_supervisor` | `96/96` | `100.0` | `1070.3 ms` | `nenhum` |

## Rankings

- qualidade: `python_functions`, `langgraph`, `specialist_supervisor`, `llamaindex`, `crewai`
- latencia: `python_functions`, `langgraph`, `specialist_supervisor`, `llamaindex`, `crewai`

## By Wave

### public_grounding

| Stack | OK | Quality | Avg latency |
| --- | --- | --- | --- |
| `langgraph` | `24/24` | `100.0` | `2150.0 ms` |
| `crewai` | `24/24` | `100.0` | `5685.3 ms` |
| `python_functions` | `24/24` | `100.0` | `113.9 ms` |
| `llamaindex` | `24/24` | `100.0` | `1437.9 ms` |
| `specialist_supervisor` | `24/24` | `100.0` | `171.1 ms` |

### public_graphrag

| Stack | OK | Quality | Avg latency |
| --- | --- | --- | --- |
| `langgraph` | `8/8` | `100.0` | `393.6 ms` |
| `crewai` | `8/8` | `100.0` | `7343.1 ms` |
| `python_functions` | `8/8` | `100.0` | `115.8 ms` |
| `llamaindex` | `8/8` | `100.0` | `128.8 ms` |
| `specialist_supervisor` | `8/8` | `100.0` | `250.0 ms` |

### protected_ops

| Stack | OK | Quality | Avg latency |
| --- | --- | --- | --- |
| `langgraph` | `32/32` | `100.0` | `354.5 ms` |
| `crewai` | `32/32` | `100.0` | `3596.3 ms` |
| `python_functions` | `32/32` | `100.0` | `166.3 ms` |
| `llamaindex` | `32/32` | `100.0` | `927.9 ms` |
| `specialist_supervisor` | `32/32` | `100.0` | `1873.8 ms` |

### sensitive_external

| Stack | OK | Quality | Avg latency |
| --- | --- | --- | --- |
| `langgraph` | `16/16` | `100.0` | `1092.1 ms` |
| `crewai` | `16/16` | `100.0` | `5788.2 ms` |
| `python_functions` | `16/16` | `100.0` | `151.3 ms` |
| `llamaindex` | `16/16` | `100.0` | `2989.8 ms` |
| `specialist_supervisor` | `16/16` | `100.0` | `2060.9 ms` |

### teacher_workflow

| Stack | OK | Quality | Avg latency |
| --- | --- | --- | --- |
| `langgraph` | `16/16` | `100.0` | `673.6 ms` |
| `crewai` | `16/16` | `100.0` | `3467.2 ms` |
| `python_functions` | `16/16` | `100.0` | `179.2 ms` |
| `llamaindex` | `16/16` | `100.0` | `1710.7 ms` |
| `specialist_supervisor` | `16/16` | `100.0` | `231.4 ms` |

## Notes

- CrewAI permanece no scorecard como baseline comparativa funcional, sem novos investimentos de arquitetura.
- Os caminhos ativos em evolucao sao langgraph, python_functions, llamaindex e specialist_supervisor.
- Erros operacionais como *_pilot_unavailable e runtime_unconfigured devem ser lidos separadamente de qualidade semantica.
- O benchmark context de cada onda deve ser consultado junto com o scorecard para interpretar drift de ambiente e modo de execucao.
