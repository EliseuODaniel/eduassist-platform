# Five-Path System Question Bank v5 Scorecard

## Overall

| Stack | OK | Quality | Avg latency | Error types |
| --- | --- | --- | --- | --- |
| `langgraph` | `96/96` | `99.9` | `966.1 ms` | `repetitive_reply=1` |
| `crewai` | `96/96` | `99.9` | `4844.8 ms` | `repetitive_reply=1` |
| `python_functions` | `96/96` | `100.0` | `136.7 ms` | `nenhum` |
| `llamaindex` | `93/96` | `96.8` | `5809.5 ms` | `repetitive_reply=1, request_failed=3` |
| `specialist_supervisor` | `96/96` | `100.0` | `4053.4 ms` | `nenhum` |

## Rankings

- qualidade: `python_functions`, `specialist_supervisor`, `langgraph`, `crewai`, `llamaindex`
- latencia: `python_functions`, `langgraph`, `specialist_supervisor`, `crewai`, `llamaindex`

## By Wave

### public_grounding

| Stack | OK | Quality | Avg latency |
| --- | --- | --- | --- |
| `langgraph` | `24/24` | `100.0` | `2271.2 ms` |
| `crewai` | `24/24` | `100.0` | `5777.9 ms` |
| `python_functions` | `24/24` | `100.0` | `112.1 ms` |
| `llamaindex` | `24/24` | `100.0` | `3637.5 ms` |
| `specialist_supervisor` | `24/24` | `100.0` | `2529.8 ms` |

### public_graphrag

| Stack | OK | Quality | Avg latency |
| --- | --- | --- | --- |
| `langgraph` | `8/8` | `100.0` | `385.0 ms` |
| `crewai` | `8/8` | `100.0` | `7794.3 ms` |
| `python_functions` | `8/8` | `100.0` | `117.5 ms` |
| `llamaindex` | `8/8` | `100.0` | `104.8 ms` |
| `specialist_supervisor` | `8/8` | `100.0` | `1892.9 ms` |

### protected_ops

| Stack | OK | Quality | Avg latency |
| --- | --- | --- | --- |
| `langgraph` | `32/32` | `100.0` | `322.6 ms` |
| `crewai` | `32/32` | `100.0` | `3611.8 ms` |
| `python_functions` | `32/32` | `100.0` | `145.7 ms` |
| `llamaindex` | `30/32` | `93.8` | `6213.7 ms` |
| `specialist_supervisor` | `32/32` | `100.0` | `5542.6 ms` |

### sensitive_external

| Stack | OK | Quality | Avg latency |
| --- | --- | --- | --- |
| `langgraph` | `16/16` | `100.0` | `850.5 ms` |
| `crewai` | `16/16` | `100.0` | `5631.2 ms` |
| `python_functions` | `16/16` | `100.0` | `138.2 ms` |
| `llamaindex` | `15/16` | `93.8` | `11311.5 ms` |
| `specialist_supervisor` | `16/16` | `100.0` | `3104.7 ms` |

### teacher_workflow

| Stack | OK | Quality | Avg latency |
| --- | --- | --- | --- |
| `langgraph` | `16/16` | `99.4` | `701.9 ms` |
| `crewai` | `16/16` | `99.4` | `3649.9 ms` |
| `python_functions` | `16/16` | `100.0` | `163.6 ms` |
| `llamaindex` | `16/16` | `99.4` | `5609.5 ms` |
| `specialist_supervisor` | `16/16` | `100.0` | `5389.4 ms` |

## Notes

- CrewAI permanece no scorecard como baseline comparativa funcional, sem novos investimentos de arquitetura.
- Os caminhos ativos em evolucao sao langgraph, python_functions, llamaindex e specialist_supervisor.
- Erros operacionais como *_pilot_unavailable e runtime_unconfigured devem ser lidos separadamente de qualidade semantica.
- O benchmark context de cada onda deve ser consultado junto com o scorecard para interpretar drift de ambiente e modo de execucao.
