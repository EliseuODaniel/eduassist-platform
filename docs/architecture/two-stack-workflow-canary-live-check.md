# Workflow Canary Live Check

Date: 2026-03-27

## Canary Scope

- baseline default: `LangGraph`
- experiment enabled: `true`
- experiment primary engine: `CrewAI`
- enrolled slices: `support,public,workflow`
- per-slice rollout: `support:100`, `public:1`, `workflow:100`
- allowlisted Telegram chat: `1649845499`
- allowlist-scoped slices: `support,workflow`

This means:

- `support` and `workflow` run as controlled canaries only on the allowlisted chat
- `public` keeps a tiny gradual rollout
- `protected` is not promoted

## Runtime Validation

The running orchestrator reports:

- `orchestratorEngine=langgraph`
- `experimentEnabled=true`
- `experimentSlices=support,public,workflow`
- `experimentSliceRollouts=support:100,public:1,workflow:100`
- `experimentAllowlistSlices=support,workflow`

The selector was validated inside the running container:

- `quero agendar uma visita na quinta a tarde` -> `experiment:workflow:crewai`
- `qual o horario da biblioteca?` -> `langgraph`

## Live Check Through Main Orchestrator

### Workflow prompt on allowlisted chat

Request:

- `quero agendar uma visita na quinta a tarde`

Observed response:

- `Pedido de visita registrado para o Colegio Horizonte. Protocolo: VIS-20260327-CABA79. Preferencia informada: 02/04/2026 - tarde. Fila responsavel: admissoes. Ticket operacional: ATD-20260327-D38E33CF. A equipe comercial valida a janela e retorna com a confirmacao.`

Interpretation:

- the request was routed to the CrewAI workflow pilot
- the pilot created the visit workflow correctly
- the response came back through the main orchestrator without affecting the default baseline

### Public control on the same allowlisted chat

Request:

- `qual o horario da biblioteca?`

Observed response:

- `Que bom que você quer usar a nossa biblioteca! A Biblioteca Aurora funciona de segunda a sexta-feira, das 7h30 às 18h00, e está sempre pronta para te receber.`

Interpretation:

- the request stayed on the LangGraph baseline
- the workflow canary did not leak into the public slice

## Replay Evidence Behind Promotion

From the current replay reports:

- [two-stack-shadow-workflow-real-threads-report.md](/home/edann/projects/eduassist-platform/docs/architecture/two-stack-shadow-workflow-real-threads-report.md)
  - baseline: `7/7`, quality `100.0`, average latency `2062.9ms`
  - CrewAI: `7/7`, quality `100.0`, average latency `52.6ms`
- [two-stack-shadow-master-real-threads-report.md](/home/edann/projects/eduassist-platform/docs/architecture/two-stack-shadow-master-real-threads-report.md)
  - `workflow`: baseline `7/7`, CrewAI `7/7`, quality `100.0` vs `100.0`
  - `protected`: CrewAI still below baseline, so protected remains outside the canary

## Operational Conclusion

`workflow` is now in the same operational state that `support` reached earlier:

- good replay parity
- strong latency advantage
- controlled allowlisted rollout
- no change to the default baseline path

The next safe step is to observe a handful of real allowlisted workflow turns before considering any broader rollout than the current controlled scope.
