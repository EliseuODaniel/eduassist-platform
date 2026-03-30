# Next-Gen Targeted Canary Activation Report

Date: 2026-03-30T14:53:39.641317+00:00

Base URL: `http://127.0.0.1:8002`

Action: `activated`

## Runtime State

- Before primary: `resolved=langgraph` from `orchestrator_engine`
- Before targeted: `None`
- After primary: `resolved=langgraph` from `orchestrator_engine`
- After targeted: `python_functions`

## Activated Window

- Stack: `python_functions`
- TTL seconds: `900`
- Expires at: `2026-03-30T15:08:39.638413+00:00`
- Slices: `protected`
- Telegram chat allowlist: `1649845499`
- Conversation allowlist: `none`

## Practical Meaning

- So as conversas allowlisted entram na stack nova durante essa janela.
- O resto do trafego continua no baseline atual.
- Ao expirar o TTL, o override direcionado deixa de valer automaticamente.
