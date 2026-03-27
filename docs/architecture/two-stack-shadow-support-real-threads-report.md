# Two-Stack Shadow Comparison Report

## Summary

- Total prompts: 7
- `support`: baseline ok 7/7, CrewAI ok 7/7, baseline keyword pass 7/7, CrewAI keyword pass 7/7, quality 100.0 vs 100.0, latency 446.9ms vs 53.5ms

## By Category

- `threaded_real_transcript`: baseline ok 7/7, CrewAI ok 7/7, baseline keyword pass 7/7, CrewAI keyword pass 7/7, quality 100.0 vs 100.0

## Error Types

- `baseline`: nenhum
- `crewai`: nenhum

## Quality Signals

- `baseline`: repair_ack 1/1, followup_adaptation 1/1, personalization 1/1
- `crewai`: repair_ack 1/1, followup_adaptation 1/1, personalization 1/1

## By Thread

- `real_support_finance_handoff_1649845499` (support/threaded_real_transcript): baseline keyword pass 3/3, CrewAI keyword pass 3/3, quality 100.0 vs 100.0
- `real_support_handoff_repair_1649845499` (support/threaded_real_transcript): baseline keyword pass 2/2, CrewAI keyword pass 2/2, quality 100.0 vs 100.0
- `real_support_secretaria_handoff_555001` (support/threaded_real_transcript): baseline keyword pass 2/2, CrewAI keyword pass 2/2, quality 100.0 vs 100.0

## Prompt Results

### quero falar com um humano sobre o financeiro

- Slice: `support`
- Category: `threaded_real_transcript`
- Thread: `real_support_finance_handoff_1649845499` turn `1`
- Baseline: status 200, latency 370.1ms, keyword pass `True`, quality `100`
- CrewAI: status 200, latency 70.1ms, keyword pass `True`, quality `100`
- Baseline quality signals: repair_ack=None, followup_adaptation=None, personalization=None
- CrewAI quality signals: repair_ack=None, followup_adaptation=None, personalization=None
- Baseline answer: Encaminhei sua solicitacao para a fila de financeiro. Protocolo: ATD-20260327-E2AEC2CA. Status atual: queued. A equipe humana podera continuar esse atendimento no portal operacional.
- CrewAI answer: Sua solicitacao ja estava registrada na fila de financeiro. Protocolo: ATD-20260327-E2AEC2CA. Status atual: queued.

### qual o protocolo?

- Slice: `support`
- Category: `threaded_real_transcript`
- Thread: `real_support_finance_handoff_1649845499` turn `2`
- Baseline: status 200, latency 185.3ms, keyword pass `True`, quality `100`
- CrewAI: status 200, latency 35.9ms, keyword pass `True`, quality `100`
- Baseline quality signals: repair_ack=None, followup_adaptation=None, personalization=None
- CrewAI quality signals: repair_ack=None, followup_adaptation=None, personalization=None
- Baseline answer: O protocolo do seu atendimento e ATD-20260327-E2AEC2CA. Se quiser, posso verificar o status atual ou te dar um resumo do que ja foi registrado.
- CrewAI answer: O protocolo do seu atendimento e ATD-20260327-E2AEC2CA. Se quiser, posso verificar o status atual ou te dar um resumo do que ja foi registrado.

### qual o status?

- Slice: `support`
- Category: `threaded_real_transcript`
- Thread: `real_support_finance_handoff_1649845499` turn `3`
- Baseline: status 200, latency 197.0ms, keyword pass `True`, quality `100`
- CrewAI: status 200, latency 39.1ms, keyword pass `True`, quality `100`
- Baseline quality signals: repair_ack=None, followup_adaptation=None, personalization=None
- CrewAI quality signals: repair_ack=None, followup_adaptation=None, personalization=None
- Baseline answer: O protocolo do seu atendimento e ATD-20260327-E2AEC2CA. O status atual e "queued", o que significa que sua solicitacao esta na fila para ser atendida pela equipe de financeiro.
- CrewAI answer: O protocolo do seu atendimento e ATD-20260327-E2AEC2CA. O status atual e "queued", o que significa que sua solicitacao esta na fila para ser atendida pela equipe de financeiro.

### como falo com um atendente humano?

- Slice: `support`
- Category: `threaded_real_transcript`
- Thread: `real_support_handoff_repair_1649845499` turn `1`
- Baseline: status 200, latency 202.4ms, keyword pass `True`, quality `100`
- CrewAI: status 200, latency 98.3ms, keyword pass `True`, quality `100`
- Baseline quality signals: repair_ack=None, followup_adaptation=None, personalization=None
- CrewAI quality signals: repair_ack=None, followup_adaptation=None, personalization=None
- Baseline answer: Encaminhei sua solicitacao para a fila de atendimento. Protocolo: ATD-20260327-C9232C61. Status atual: queued. A equipe humana podera continuar esse atendimento no portal operacional.
- CrewAI answer: Sua solicitacao ja estava registrada na fila de atendimento. Protocolo: ATD-20260327-C9232C61. Status atual: queued.

### mas eu cheguei agora

- Slice: `support`
- Category: `threaded_real_transcript`
- Thread: `real_support_handoff_repair_1649845499` turn `2`
- Note: repair turn after existing support handoff
- Baseline: status 200, latency 178.1ms, keyword pass `True`, quality `100`
- CrewAI: status 200, latency 36.4ms, keyword pass `True`, quality `100`
- Baseline quality signals: repair_ack=True, followup_adaptation=True, personalization=True
- CrewAI quality signals: repair_ack=True, followup_adaptation=True, personalization=True
- Baseline answer: Sem problema, vamos comecar do zero entao e abrir um novo atendimento a partir daqui. Se voce quiser atendimento humano por aqui, me diga em uma frase curta qual e o assunto como financeiro, secretaria, matricula ou direcao, e eu sigo desse ponto.
- CrewAI answer: Sem problema, vamos comecar do zero entao e abrir um novo atendimento a partir daqui. Se voce quiser atendimento humano por aqui, me diga em uma frase curta qual e o assunto como financeiro, secretaria, matricula ou direcao, e eu sigo desse ponto.

### quero falar com um humano sobre a secretaria

- Slice: `support`
- Category: `threaded_real_transcript`
- Thread: `real_support_secretaria_handoff_555001` turn `1`
- Baseline: status 200, latency 186.1ms, keyword pass `True`, quality `100`
- CrewAI: status 200, latency 58.1ms, keyword pass `True`, quality `100`
- Baseline quality signals: repair_ack=None, followup_adaptation=None, personalization=None
- CrewAI quality signals: repair_ack=None, followup_adaptation=None, personalization=None
- Baseline answer: Encaminhei sua solicitacao para a fila de secretaria. Protocolo: ATD-20260327-FE5FCE3E. Status atual: queued. A equipe humana podera continuar esse atendimento no portal operacional.
- CrewAI answer: Sua solicitacao ja estava registrada na fila de secretaria. Protocolo: ATD-20260327-FE5FCE3E. Status atual: queued.

### qual o protocolo?

- Slice: `support`
- Category: `threaded_real_transcript`
- Thread: `real_support_secretaria_handoff_555001` turn `2`
- Baseline: status 200, latency 1809.6ms, keyword pass `True`, quality `100`
- CrewAI: status 200, latency 36.5ms, keyword pass `True`, quality `100`
- Baseline quality signals: repair_ack=None, followup_adaptation=None, personalization=None
- CrewAI quality signals: repair_ack=None, followup_adaptation=None, personalization=None
- Baseline answer: O protocolo do seu atendimento é ATD-20260327-FE5FCE3E. Posso verificar o status atual ou resumir o que já foi registrado, se desejar.
- CrewAI answer: O protocolo do seu atendimento e ATD-20260327-FE5FCE3E. Se quiser, posso verificar o status atual ou te dar um resumo do que ja foi registrado.
