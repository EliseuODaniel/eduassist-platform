# Five-Path Chatbot Comparison Report

Date: 2026-03-31T04:12:36.044318+00:00

Dataset: `tests/evals/datasets/specialist_supervisor_phase6_regressions.json`

Run prefix: `debug:five-path:20260331T041232Z`

## Stack Summary

| Stack | OK | Keyword pass | Quality | Avg latency |
| --- | --- | --- | --- | --- |
| `langgraph` | `3/3` | `3/3` | `100.0` | `195.3 ms` |
| `crewai` | `3/3` | `3/3` | `100.0` | `306.8 ms` |
| `python_functions` | `3/3` | `3/3` | `100.0` | `190.5 ms` |
| `llamaindex` | `3/3` | `3/3` | `100.0` | `183.0 ms` |
| `specialist_supervisor` | `3/3` | `3/3` | `100.0` | `174.1 ms` |

## By Slice

- `support`
  - `langgraph`: ok 3/3, keyword pass 3/3, quality 100.0, latency 195.3ms
  - `crewai`: ok 3/3, keyword pass 3/3, quality 100.0, latency 306.8ms
  - `python_functions`: ok 3/3, keyword pass 3/3, quality 100.0, latency 190.5ms
  - `llamaindex`: ok 3/3, keyword pass 3/3, quality 100.0, latency 183.0ms
  - `specialist_supervisor`: ok 3/3, keyword pass 3/3, quality 100.0, latency 174.1ms

## Error Types

- `langgraph`: nenhum
- `crewai`: nenhum
- `python_functions`: nenhum
- `llamaindex`: nenhum
- `specialist_supervisor`: nenhum

## Prompt Results

### quero falar com um atendente humano

- Slice: `support`
- Thread: `specialist_phase6_handoff_status` turn `1`
- `langgraph`: status 200, latency 229.0ms, keyword pass `True`, quality `100`, reason `o usuario demonstrou necessidade de atendimento humano ou operacional`
  answer: Encaminhei sua solicitacao para a fila de atendimento. Protocolo: ATD-20260331-B5E30DEE. Status atual: queued. A equipe humana pode continuar esse atendimento no portal operacional.
- `crewai`: status 200, latency 292.0ms, keyword pass `True`, quality `100`, reason `support_handoff_created`
  answer: Encaminhei sua solicitacao para a fila de atendimento. Protocolo: ATD-20260331-2A0B43D1. Status atual: queued. A equipe humana podera continuar esse atendimento no portal operacional.
- `python_functions`: status 200, latency 209.3ms, keyword pass `True`, quality `100`, reason `o usuario demonstrou necessidade de atendimento humano ou operacional`
  answer: Encaminhei sua solicitacao para a fila de atendimento. Protocolo: ATD-20260331-EBABDFC1. Status atual: queued. A equipe humana pode continuar esse atendimento no portal operacional.
- `llamaindex`: status 200, latency 188.4ms, keyword pass `True`, quality `100`, reason `o usuario demonstrou necessidade de atendimento humano ou operacional`
  answer: Encaminhei sua solicitacao para a fila de atendimento. Protocolo: ATD-20260331-996232B9. Status atual: queued. A equipe humana pode continuar esse atendimento no portal operacional.
- `specialist_supervisor`: status 200, latency 210.7ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_tool_first:human_handoff`
  answer: Encaminhei sua solicitacao para a fila de atendimento. Protocolo: ATD-20260331-2985CA83. Status atual: queued. Se preferir, voce tambem pode seguir pelo WhatsApp oficial (11) 97500-2040.

### qual o status do protocolo?

- Slice: `support`
- Thread: `specialist_phase6_handoff_status` turn `2`
- `langgraph`: status 200, latency 195.8ms, keyword pass `True`, quality `100`, reason `a solicitacao pode ser executada por workflow estruturado com protocolo`
  answer: Status do atendimento: ele segue em fila na fila de atendimento. Protocolo: ATD-20260331-B5E30DEE. Resumo: Atendimento institucional. Se quiser, eu tambem posso te orientar sobre o proximo setor ou resumir o que ja foi registrado.
- `crewai`: status 200, latency 262.3ms, keyword pass `True`, quality `100`, reason `workflow_status_lookup`
  answer: Sua solicitacao segue em fila com a area de atendimento. - Protocolo: ATD-20260331-2A0B43D1 - Ticket operacional: ATD-20260331-2A0B43D1 - Status atual: queued Proximo passo: a equipe responsavel recebe essa atualizacao e segue o retorno pelo fluxo institucional.
- `python_functions`: status 200, latency 193.0ms, keyword pass `True`, quality `100`, reason `python_functions_native_structured:support`
  answer: Status do atendimento: ele segue em fila na fila de atendimento. Protocolo: ATD-20260331-EBABDFC1. Resumo: Atendimento institucional. Se quiser, eu tambem posso te orientar sobre o proximo setor ou resumir o que ja foi registrado.
- `llamaindex`: status 200, latency 196.4ms, keyword pass `True`, quality `100`, reason `a solicitacao pode ser executada por workflow estruturado com protocolo`
  answer: Status do atendimento: ele segue em fila na fila de atendimento. Protocolo: ATD-20260331-996232B9. Resumo: Atendimento institucional. Se quiser, eu tambem posso te orientar sobre o proximo setor ou resumir o que ja foi registrado.
- `specialist_supervisor`: status 200, latency 151.3ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_tool_first:support_status`
  answer: O atendimento sobre Atendimento institucional esta com status queued. Protocolo: ATD-20260331-2985CA83. Fila: atendimento. Ticket operacional: ATD-20260331-2985CA83.

### quero falar com o financeiro

- Slice: `support`
- Thread: `specialist_phase6_finance_handoff` turn `1`
- `langgraph`: status 200, latency 161.1ms, keyword pass `True`, quality `100`, reason `o usuario demonstrou necessidade de atendimento humano ou operacional`
  answer: Encaminhei sua solicitacao para a fila de financeiro. Protocolo: ATD-20260331-E1A03812. Status atual: queued. A equipe humana pode continuar esse atendimento no portal operacional.
- `crewai`: status 200, latency 366.1ms, keyword pass `True`, quality `100`, reason `support_handoff_created`
  answer: Encaminhei sua solicitacao para a fila de financeiro. Protocolo: ATD-20260331-B80BF087. Status atual: queued. A equipe humana podera continuar esse atendimento no portal operacional.
- `python_functions`: status 200, latency 169.1ms, keyword pass `True`, quality `100`, reason `o usuario demonstrou necessidade de atendimento humano ou operacional`
  answer: Encaminhei sua solicitacao para a fila de financeiro. Protocolo: ATD-20260331-E3DB44D1. Status atual: queued. A equipe humana pode continuar esse atendimento no portal operacional.
- `llamaindex`: status 200, latency 164.2ms, keyword pass `True`, quality `100`, reason `o usuario demonstrou necessidade de atendimento humano ou operacional`
  answer: Encaminhei sua solicitacao para a fila de financeiro. Protocolo: ATD-20260331-D8A8858E. Status atual: queued. A equipe humana pode continuar esse atendimento no portal operacional.
- `specialist_supervisor`: status 200, latency 160.2ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_tool_first:human_handoff`
  answer: Encaminhei sua solicitacao para a fila de financeiro. Protocolo: ATD-20260331-C21AF98B. Status atual: queued. Se preferir, voce tambem pode seguir pelo WhatsApp oficial (11) 97500-2040.

