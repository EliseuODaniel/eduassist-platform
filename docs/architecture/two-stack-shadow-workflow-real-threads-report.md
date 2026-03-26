# Two-Stack Shadow Comparison Report

## Summary

- Total prompts: 7
- `workflow`: baseline ok 7/7, CrewAI ok 7/7, baseline keyword pass 7/7, CrewAI keyword pass 7/7, quality 100.0 vs 100.0, latency 2036.5ms vs 39.4ms

## By Category

- `threaded_real_transcript`: baseline ok 7/7, CrewAI ok 7/7, baseline keyword pass 7/7, CrewAI keyword pass 7/7, quality 100.0 vs 100.0

## Error Types

- `baseline`: nenhum
- `crewai`: nenhum

## Quality Signals

- `baseline`: repair_ack 0/0, followup_adaptation 0/0, personalization 1/1
- `crewai`: repair_ack 0/0, followup_adaptation 0/0, personalization 1/1

## By Thread

- `real_visit_lifecycle_777052` (workflow/threaded_real_transcript): baseline keyword pass 4/4, CrewAI keyword pass 4/4, quality 100.0 vs 100.0
- `real_request_lifecycle_777051` (workflow/threaded_real_transcript): baseline keyword pass 3/3, CrewAI keyword pass 3/3, quality 100.0 vs 100.0

## Prompt Results

### quero agendar uma visita para conhecer a escola na quinta a tarde

- Slice: `workflow`
- Category: `threaded_real_transcript`
- Thread: `real_visit_lifecycle_777052` turn `1`
- Baseline: status 200, latency 2075.1ms, keyword pass `True`, quality `100`
- CrewAI: status 200, latency 67.2ms, keyword pass `True`, quality `100`
- Baseline quality signals: repair_ack=None, followup_adaptation=None, personalization=None
- CrewAI quality signals: repair_ack=None, followup_adaptation=None, personalization=None
- Baseline answer: Pedido de visita registrado para o Colegio Horizonte. Protocolo: VIS-20260326-DC40EC. Preferencia informada: 2026-04-02 - tarde. Fila responsavel: admissoes. Ticket operacional: ATD-20260326-32F1C6ED. A equipe comercial valida a janela e retorna com a confirmacao.
- CrewAI answer: Pedido de visita registrado para o Colegio Horizonte. Protocolo: VIS-20260326-DC40EC. Preferencia informada: 26/03/2026 - tarde. Fila responsavel: admissoes. Ticket operacional: ATD-20260326-32F1C6ED. A equipe comercial valida a janela e retorna com a confirmacao.

### qual o protocolo da visita?

- Slice: `workflow`
- Category: `threaded_real_transcript`
- Thread: `real_visit_lifecycle_777052` turn `2`
- Baseline: status 200, latency 1936.6ms, keyword pass `True`, quality `100`
- CrewAI: status 200, latency 20.7ms, keyword pass `True`, quality `100`
- Baseline quality signals: repair_ack=None, followup_adaptation=None, personalization=None
- CrewAI quality signals: repair_ack=None, followup_adaptation=None, personalization=None
- Baseline answer: O protocolo da sua visita e VIS-20260326-DC40EC.
- Ticket operacional: ATD-20260326-32F1C6ED
- Preferencia registrada: 26/03/2026 - tarde
Se quiser, eu tambem posso te dizer o status, remarcar ou cancelar a visita.
- CrewAI answer: O protocolo da sua visita e VIS-20260326-DC40EC. - Ticket operacional: ATD-20260326-32F1C6ED - Preferencia registrada: 26/03/2026 - tarde Se quiser, eu tambem posso te dizer o status, remarcar ou cancelar a visita.

### quero remarcar a visita para sexta de manha

- Slice: `workflow`
- Category: `threaded_real_transcript`
- Thread: `real_visit_lifecycle_777052` turn `3`
- Baseline: status 200, latency 2084.5ms, keyword pass `True`, quality `100`
- CrewAI: status 200, latency 44.3ms, keyword pass `True`, quality `100`
- Baseline quality signals: repair_ack=None, followup_adaptation=None, personalization=None
- CrewAI quality signals: repair_ack=None, followup_adaptation=None, personalization=None
- Baseline answer: Pedido de visita atualizado com a fila de admissions.
- Protocolo: VIS-20260326-DC40EC
- Ticket operacional: ATD-20260326-32F1C6ED
- Nova preferencia: 27/03/2026 - manha
Proximo passo: admissions valida a nova janela e retorna com a confirmacao.
- CrewAI answer: Pedido de visita atualizado com a fila de admissoes. - Protocolo: VIS-20260326-DC40EC - Ticket operacional: ATD-20260326-32F1C6ED - Nova preferencia: 27/03/2026 - manha Proximo passo: admissions valida a nova janela e retorna com a confirmacao.

### quero cancelar a visita

- Slice: `workflow`
- Category: `threaded_real_transcript`
- Thread: `real_visit_lifecycle_777052` turn `4`
- Baseline: status 200, latency 2137.5ms, keyword pass `True`, quality `100`
- CrewAI: status 200, latency 44.5ms, keyword pass `True`, quality `100`
- Baseline quality signals: repair_ack=None, followup_adaptation=None, personalization=None
- CrewAI quality signals: repair_ack=None, followup_adaptation=None, personalization=None
- Baseline answer: Entendido! Sua visita com o protocolo VIS-20260326-DC40EC foi cancelada. O ticket operacional ATD-20260326-32F1C6ED também foi atualizado. Se precisar, é só me avisar para agendarmos uma nova visita no futuro.
- CrewAI answer: Visita cancelada no fluxo de admissoes. - Protocolo: VIS-20260326-DC40EC - Ticket operacional: ATD-20260326-32F1C6ED Se quiser, eu tambem posso registrar um novo pedido de visita quando voce preferir.

### quero protocolar uma solicitacao para a direcao sobre ampliacao do horario da biblioteca

- Slice: `workflow`
- Category: `threaded_real_transcript`
- Thread: `real_request_lifecycle_777051` turn `1`
- Baseline: status 200, latency 1986.0ms, keyword pass `True`, quality `100`
- CrewAI: status 200, latency 56.7ms, keyword pass `True`, quality `100`
- Baseline quality signals: repair_ack=None, followup_adaptation=None, personalization=None
- CrewAI quality signals: repair_ack=None, followup_adaptation=None, personalization=None
- Baseline answer: Solicitacao institucional registrada para direcao. Protocolo: REQ-20260326-E8A119. Assunto: quero protocolar uma solicitacao para a direcao sobre ampliacao do horario da biblioteca. Fila responsavel: direcao. Ticket operacional: ATD-20260326-2D065C80. A equipe faz a triagem inicial e segue o retorno pelo fluxo institucional.
- CrewAI answer: Solicitacao institucional registrada para direcao. Protocolo: REQ-20260326-E8A119. Assunto: quero protocolar uma solicitacao para a direcao sobre ampliacao do horario da biblioteca. Fila responsavel: direcao. Ticket operacional: ATD-20260326-2D065C80. A equipe faz a triagem inicial e segue o retorno pelo fluxo institucional.

### qual o protocolo?

- Slice: `workflow`
- Category: `threaded_real_transcript`
- Thread: `real_request_lifecycle_777051` turn `2`
- Baseline: status 200, latency 1907.9ms, keyword pass `True`, quality `100`
- CrewAI: status 200, latency 21.3ms, keyword pass `True`, quality `100`
- Baseline quality signals: repair_ack=None, followup_adaptation=None, personalization=None
- CrewAI quality signals: repair_ack=None, followup_adaptation=None, personalization=None
- Baseline answer: Claro! O protocolo da sua solicitação é REQ-20260326-E8A119, e o ticket operacional é ATD-20260326-2D065C80. A área responsável é a direção. Se precisar, posso resumir o pedido ou verificar o status para você.
- CrewAI answer: O protocolo da sua solicitacao e REQ-20260326-E8A119. - Ticket operacional: ATD-20260326-2D065C80 - Area responsavel: direcao Se quiser, eu tambem posso resumir o pedido ou verificar o status atual.

### resume meu pedido

- Slice: `workflow`
- Category: `threaded_real_transcript`
- Thread: `real_request_lifecycle_777051` turn `3`
- Baseline: status 200, latency 2128.1ms, keyword pass `True`, quality `100`
- CrewAI: status 200, latency 21.4ms, keyword pass `True`, quality `100`
- Baseline quality signals: repair_ack=None, followup_adaptation=None, personalization=True
- CrewAI quality signals: repair_ack=None, followup_adaptation=None, personalization=True
- Baseline answer: Resumo da sua solicitacao institucional:
- Assunto: quero protocolar uma solicitacao para a direcao sobre ampliacao do horario da biblioteca
- Area responsavel: direcao
- Detalhes registrados: quero protocolar uma solicitacao para a direcao sobre ampliacao do horario da biblioteca
- Protocolo: REQ-20260326-E8A119
- Ticket operacional: ATD-20260326-2D065C80
- Status atual: em fila
Se quiser, eu tambem posso te dizer o prazo estimado ou quem responde por essa fila.
- CrewAI answer: Resumo da sua solicitacao institucional: - Assunto: quero protocolar uma solicitacao para a direcao sobre ampliacao do horario da biblioteca - Area responsavel: direcao - Protocolo: REQ-20260326-E8A119 - Ticket operacional: ATD-20260326-2D065C80 - Status atual: queued Se quiser, eu tambem posso te dizer o prazo estimado ou quem responde por essa fila.
