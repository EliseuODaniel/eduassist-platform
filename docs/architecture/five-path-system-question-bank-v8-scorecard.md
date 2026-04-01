# Five-Path System Question Bank v8 Scorecard

## Overall

| Stack | OK | Quality | Avg latency | Error types |
| --- | --- | --- | --- | --- |
| `langgraph` | `96/96` | `100.0` | `924.8 ms` | `nenhum` |
| `crewai` | `96/96` | `99.9` | `4963.6 ms` | `repetitive_reply=1` |
| `python_functions` | `96/96` | `100.0` | `149.7 ms` | `nenhum` |
| `llamaindex` | `96/96` | `100.0` | `1584.1 ms` | `nenhum` |
| `specialist_supervisor` | `96/96` | `100.0` | `4076.8 ms` | `nenhum` |

## Rankings

- qualidade: `python_functions`, `langgraph`, `llamaindex`, `specialist_supervisor`, `crewai`
- latencia: `python_functions`, `langgraph`, `llamaindex`, `specialist_supervisor`, `crewai`

## By Wave

### public_grounding

| Stack | OK | Quality | Avg latency |
| --- | --- | --- | --- |
| `langgraph` | `24/24` | `100.0` | `2026.1 ms` |
| `crewai` | `24/24` | `100.0` | `5616.8 ms` |
| `python_functions` | `24/24` | `100.0` | `138.0 ms` |
| `llamaindex` | `24/24` | `100.0` | `1551.1 ms` |
| `specialist_supervisor` | `24/24` | `100.0` | `2852.9 ms` |

### public_graphrag

| Stack | OK | Quality | Avg latency |
| --- | --- | --- | --- |
| `langgraph` | `8/8` | `100.0` | `374.3 ms` |
| `crewai` | `8/8` | `100.0` | `7624.2 ms` |
| `python_functions` | `8/8` | `100.0` | `132.0 ms` |
| `llamaindex` | `8/8` | `100.0` | `150.7 ms` |
| `specialist_supervisor` | `8/8` | `100.0` | `2260.0 ms` |

### protected_ops

| Stack | OK | Quality | Avg latency |
| --- | --- | --- | --- |
| `langgraph` | `32/32` | `100.0` | `337.9 ms` |
| `crewai` | `32/32` | `100.0` | `3818.9 ms` |
| `python_functions` | `32/32` | `100.0` | `146.4 ms` |
| `llamaindex` | `32/32` | `100.0` | `935.6 ms` |
| `specialist_supervisor` | `32/32` | `100.0` | `4443.1 ms` |

### sensitive_external

| Stack | OK | Quality | Avg latency |
| --- | --- | --- | --- |
| `langgraph` | `16/16` | `100.0` | `980.9 ms` |
| `crewai` | `16/16` | `100.0` | `6220.1 ms` |
| `python_functions` | `16/16` | `100.0` | `172.4 ms` |
| `llamaindex` | `16/16` | `100.0` | `3824.7 ms` |
| `specialist_supervisor` | `16/16` | `100.0` | `3609.7 ms` |

### teacher_workflow

| Stack | OK | Quality | Avg latency |
| --- | --- | --- | --- |
| `langgraph` | `16/16` | `100.0` | `665.6 ms` |
| `crewai` | `16/16` | `99.4` | `3686.5 ms` |
| `python_functions` | `16/16` | `100.0` | `160.2 ms` |
| `llamaindex` | `16/16` | `100.0` | `1406.8 ms` |
| `specialist_supervisor` | `16/16` | `100.0` | `6555.4 ms` |

## Notes

- CrewAI permanece no scorecard como baseline comparativa funcional, sem novos investimentos de arquitetura.
- Os caminhos ativos em evolucao sao langgraph, python_functions, llamaindex e specialist_supervisor.
- Erros operacionais como *_pilot_unavailable e runtime_unconfigured devem ser lidos separadamente de qualidade semantica.
- O benchmark context de cada onda deve ser consultado junto com o scorecard para interpretar drift de ambiente e modo de execucao.
