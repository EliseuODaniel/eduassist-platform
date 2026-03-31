# Next-Gen Targeted Canary Activation Report

Date: 2026-03-31T00:43:26.045231+00:00

Base URL: `http://127.0.0.1:8002`

Action: `activated`

## Runtime State

- Before primary: `resolved=langgraph` from `orchestrator_engine`
- Before targeted: `None`
- After primary: `resolved=langgraph` from `orchestrator_engine`
- After targeted: `specialist_supervisor`

## Activated Window

- Stack: `specialist_supervisor`
- TTL seconds: `1800`
- Expires at: `2026-03-31T01:13:26.040589+00:00`
- Slices: `workflow`
- Telegram chat allowlist: `1649845499`
- Conversation allowlist: `none`

## Practical Meaning

- So as conversas allowlisted entram na stack nova durante essa janela.
- O resto do trafego continua no baseline atual.
- Ao expirar o TTL, o override direcionado deixa de valer automaticamente.
