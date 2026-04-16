# Four-Path Chatbot Stress Report

Date: 2026-04-16T22:23:11.759634+00:00

Dataset: `tests/evals/datasets/retrieval_40q_stress_suite.generated.20260416.final.json`
Guardian chat id: `1649845499`
Timeout: `45.0s`
Rounds: `1`
Concurrency levels: `1, 2, 4`

## Stack Summary

| Stack | Concurrency | OK | Keyword pass | Quality | Avg latency | P95 | Max | Throughput |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `langgraph` | `1` | `40/40` | `40/40` | `100.0` | `3779.0 ms` | `17443.7 ms` | `22393.4 ms` | `0.26 rps` |
| `langgraph` | `2` | `40/40` | `40/40` | `100.0` | `6209.4 ms` | `30446.3 ms` | `39266.8 ms` | `0.32 rps` |
| `langgraph` | `4` | `36/40` | `36/40` | `90.0` | `8962.7 ms` | `45037.2 ms` | `45118.8 ms` | `0.44 rps` |
| `python_functions` | `1` | `40/40` | `40/40` | `100.0` | `4089.3 ms` | `18240.3 ms` | `23357.2 ms` | `0.24 rps` |
| `python_functions` | `2` | `39/40` | `39/40` | `97.5` | `6940.9 ms` | `37556.7 ms` | `45062.4 ms` | `0.29 rps` |
| `python_functions` | `4` | `34/40` | `34/40` | `85.0` | `10969.3 ms` | `45047.8 ms` | `45131.7 ms` | `0.36 rps` |
| `llamaindex` | `1` | `40/40` | `40/40` | `100.0` | `3529.4 ms` | `15446.3 ms` | `17334.0 ms` | `0.28 rps` |
| `llamaindex` | `2` | `40/40` | `40/40` | `100.0` | `7073.0 ms` | `35359.1 ms` | `44178.1 ms` | `0.28 rps` |
| `llamaindex` | `4` | `35/40` | `35/40` | `87.5` | `8831.2 ms` | `45037.7 ms` | `45082.1 ms` | `0.43 rps` |
| `specialist_supervisor` | `1` | `40/40` | `40/40` | `100.0` | `375.5 ms` | `1047.1 ms` | `1926.0 ms` | `2.64 rps` |
| `specialist_supervisor` | `2` | `40/40` | `40/40` | `100.0` | `365.7 ms` | `603.0 ms` | `1195.0 ms` | `5.36 rps` |
| `specialist_supervisor` | `4` | `40/40` | `40/40` | `100.0` | `637.4 ms` | `1410.0 ms` | `1672.1 ms` | `6.07 rps` |

## Recommendations

- `langgraph` reached p95 `45037.2 ms` at concurrency `4`; inspect slowest routes and queueing.
- `langgraph` dropped successful responses under concurrency `4` (`36/40`); inspect timeouts and retries.
- `langgraph` lost grounding quality under concurrency `4` (`keyword_pass 36/40`).
- `python_functions` reached p95 `45047.8 ms` at concurrency `4`; inspect slowest routes and queueing.
- `python_functions` dropped successful responses under concurrency `4` (`34/40`); inspect timeouts and retries.
- `python_functions` lost grounding quality under concurrency `4` (`keyword_pass 34/40`).
- `llamaindex` reached p95 `45037.7 ms` at concurrency `4`; inspect slowest routes and queueing.
- `llamaindex` dropped successful responses under concurrency `4` (`35/40`); inspect timeouts and retries.
- `llamaindex` lost grounding quality under concurrency `4` (`keyword_pass 35/40`).

## Dominant Error Types

- `langgraph` @ `1`: `none`
- `langgraph` @ `2`: `none`
- `langgraph` @ `4`: `request_failed` x4
- `python_functions` @ `1`: `none`
- `python_functions` @ `2`: `request_failed` x1
- `python_functions` @ `4`: `request_failed` x6
- `llamaindex` @ `1`: `none`
- `llamaindex` @ `2`: `none`
- `llamaindex` @ `4`: `request_failed` x5
- `specialist_supervisor` @ `1`: `none`
- `specialist_supervisor` @ `2`: `none`
- `specialist_supervisor` @ `4`: `none`

