# Next-Gen Stack Runtime Observation Report

Date: 2026-03-30T14:31:01.384607+00:00

Base URL: `http://127.0.0.1:8002`

Dataset: `/home/edann/projects/eduassist-platform/tests/evals/datasets/nextgen_runtime_observation_cases.json`

## Summary

| Stack | OK | Keyword pass | Quality | Avg latency | Stable window | Latency watch |
| --- | --- | --- | --- | --- | --- | --- |
| `python_functions` | `16/16` | `16/16` | `100.0` | `148.7 ms` | `True` | `False` |
| `llamaindex` | `16/16` | `16/16` | `100.0` | `147.6 ms` | `True` | `False` |

## Runtime State

- Before: `resolved=langgraph` from `orchestrator_engine`
- After restore: `resolved=langgraph` from `orchestrator_engine`

## By Slice

- `protected` (4 turns)
  - `python_functions`: ok 4/4, keyword pass 4/4, quality 100.0, latency 165.6ms
  - `llamaindex`: ok 4/4, keyword pass 4/4, quality 100.0, latency 167.2ms
- `public` (5 turns)
  - `python_functions`: ok 5/5, keyword pass 5/5, quality 100.0, latency 132.6ms
  - `llamaindex`: ok 5/5, keyword pass 5/5, quality 100.0, latency 125.5ms
- `support` (3 turns)
  - `python_functions`: ok 3/3, keyword pass 3/3, quality 100.0, latency 141.9ms
  - `llamaindex`: ok 3/3, keyword pass 3/3, quality 100.0, latency 145.2ms
- `workflow` (4 turns)
  - `python_functions`: ok 4/4, keyword pass 4/4, quality 100.0, latency 156.8ms
  - `llamaindex`: ok 4/4, keyword pass 4/4, quality 100.0, latency 157.3ms

## By Thread

- `obs_protected_docs_focus` (protected, 4 turns)
  - `python_functions`: ok 4/4, keyword pass 4/4, quality 100.0, latency 165.6ms
  - `llamaindex`: ok 4/4, keyword pass 4/4, quality 100.0, latency 167.2ms
- `obs_public_channels_docs` (public, 3 turns)
  - `python_functions`: ok 3/3, keyword pass 3/3, quality 100.0, latency 136.2ms
  - `llamaindex`: ok 3/3, keyword pass 3/3, quality 100.0, latency 125.6ms
- `obs_public_library_realism` (public, 2 turns)
  - `python_functions`: ok 2/2, keyword pass 2/2, quality 100.0, latency 127.2ms
  - `llamaindex`: ok 2/2, keyword pass 2/2, quality 100.0, latency 125.3ms
- `obs_support_reroute` (support, 3 turns)
  - `python_functions`: ok 3/3, keyword pass 3/3, quality 100.0, latency 141.9ms
  - `llamaindex`: ok 3/3, keyword pass 3/3, quality 100.0, latency 145.2ms
- `obs_workflow_visit` (workflow, 4 turns)
  - `python_functions`: ok 4/4, keyword pass 4/4, quality 100.0, latency 156.8ms
  - `llamaindex`: ok 4/4, keyword pass 4/4, quality 100.0, latency 157.3ms

## Error Types

- `python_functions`: nenhum
- `llamaindex`: nenhum

## Operational Notes

- `python_functions` ficou estavel e sem alerta de latencia relevante nesta janela curta.
- `llamaindex` ficou estavel e sem alerta de latencia relevante nesta janela curta.

## Prompt Results

### posso enviar documentos por fax ou isso nao existe mais?

- Stack: `python_functions`
- Slice: `public`
- Thread: `obs_public_channels_docs` turn `1`
- Status: `200`
- Latency: `152.9 ms`
- Mode: `structured_tool`
- Reason: `contextual_public_direct_answer`
- Access tier: `public`
- Expected kernel: `kernel:python_functions`
- Observed kernel: `kernel:python_functions`
- Kernel consistency: `True`
- Keyword pass: `True`
- Quality score: `100`
- Answer: Hoje a escola nao utiliza fax para envio de documentos. Para isso, use portal institucional, email da secretaria, secretaria presencial.

### e por telegrama, serve?

- Stack: `python_functions`
- Slice: `public`
- Thread: `obs_public_channels_docs` turn `2`
- Status: `200`
- Latency: `137.9 ms`
- Mode: `structured_tool`
- Reason: `contextual_public_direct_answer`
- Access tier: `public`
- Expected kernel: `kernel:python_functions`
- Observed kernel: `kernel:python_functions`
- Kernel consistency: `True`
- Keyword pass: `True`
- Quality score: `100`
- Answer: Hoje a escola nao publica telegrama como canal valido para documentos. Para isso, use portal institucional, email da secretaria, secretaria presencial.

### qual e o caminho certo pra mandar a documentacao?

- Stack: `python_functions`
- Slice: `public`
- Thread: `obs_public_channels_docs` turn `3`
- Status: `200`
- Latency: `117.8 ms`
- Mode: `structured_tool`
- Reason: `contextual_public_direct_answer`
- Access tier: `public`
- Expected kernel: `kernel:python_functions`
- Observed kernel: `kernel:python_functions`
- Kernel consistency: `True`
- Keyword pass: `True`
- Quality score: `100`
- Answer: Sim. O envio inicial de documentos pode ser feito por canal digital.
Hoje os canais mais diretos publicados para isso sao:
- portal institucional
- email da secretaria
- secretaria presencial
No processo de matricula, o envio inicial pode ser digital. A validacao final continua com a secretaria.
O chat aberto nao deve receber documentos completos ou dados sensiveis. Quando possivel, use o portal autenticado ou o email institucional.

### voces realmente tem biblioteca ou e so folheto bonito?

- Stack: `python_functions`
- Slice: `public`
- Thread: `obs_public_library_realism` turn `1`
- Status: `200`
- Latency: `144.1 ms`
- Mode: `structured_tool`
- Reason: `fato institucional canonico deve vir de fonte estruturada`
- Access tier: `public`
- Expected kernel: `kernel:python_functions`
- Observed kernel: `kernel:python_functions`
- Kernel consistency: `True`
- Keyword pass: `True`
- Quality score: `100`
- Answer: Sim. O Colegio Horizonte tem a Biblioteca Aurora. Atendimento ao publico de segunda a sexta, das 7h30 as 18h00.

### como ela se chama e ate que horas funciona?

- Stack: `python_functions`
- Slice: `public`
- Thread: `obs_public_library_realism` turn `2`
- Status: `200`
- Latency: `110.3 ms`
- Mode: `structured_tool`
- Reason: `contextual_public_direct_answer`
- Access tier: `public`
- Expected kernel: `kernel:python_functions`
- Observed kernel: `kernel:python_functions`
- Kernel consistency: `True`
- Keyword pass: `True`
- Quality score: `100`
- Answer: A biblioteca se chama Biblioteca Aurora e funciona de segunda a sexta, das 7h30 as 18h00.

### como esta a documentacao da ana?

- Stack: `python_functions`
- Slice: `protected`
- Thread: `obs_protected_docs_focus` turn `1`
- Status: `200`
- Latency: `155.8 ms`
- Mode: `structured_tool`
- Reason: `status administrativo autenticado exige service deterministico`
- Access tier: `authenticated`
- Expected kernel: `kernel:python_functions`
- Observed kernel: `kernel:python_functions`
- Kernel consistency: `True`
- Keyword pass: `True`
- Quality score: `100`
- Answer: Situacao documental de Ana Oliveira hoje: com pendencias.

### o que falta?

- Stack: `python_functions`
- Slice: `protected`
- Thread: `obs_protected_docs_focus` turn `2`
- Status: `200`
- Latency: `220.5 ms`
- Mode: `structured_tool`
- Reason: `status administrativo autenticado exige service deterministico`
- Access tier: `authenticated`
- Expected kernel: `kernel:python_functions`
- Observed kernel: `kernel:python_functions`
- Kernel consistency: `True`
- Keyword pass: `True`
- Quality score: `100`
- Answer: Hoje, o proximo passo do seu cadastro e este: Envie o comprovante atualizado pela secretaria ou pelo canal de documentos para concluir a conferência.

### e a documentacao do lucas?

- Stack: `python_functions`
- Slice: `protected`
- Thread: `obs_protected_docs_focus` turn `3`
- Status: `200`
- Latency: `156.2 ms`
- Mode: `structured_tool`
- Reason: `status administrativo autenticado exige service deterministico`
- Access tier: `authenticated`
- Expected kernel: `kernel:python_functions`
- Observed kernel: `kernel:python_functions`
- Kernel consistency: `True`
- Keyword pass: `True`
- Quality score: `100`
- Answer: Situacao documental de Lucas Oliveira hoje: regular.
- Identificacao escolar do aluno: regular. Codigo de matricula: MAT-2026-001
- Responsavel vinculado: regular. Maria Oliveira
- Documentacao escolar do aluno: regular. A documentacao escolar de Lucas Oliveira esta conferida e sem pendencias relevantes nesta base de testes.

### e se eu perguntar do joao?

- Stack: `python_functions`
- Slice: `protected`
- Thread: `obs_protected_docs_focus` turn `4`
- Status: `200`
- Latency: `129.9 ms`
- Mode: `structured_tool`
- Reason: `status administrativo autenticado exige service deterministico`
- Access tier: `authenticated`
- Expected kernel: `kernel:python_functions`
- Observed kernel: `kernel:python_functions`
- Kernel consistency: `True`
- Keyword pass: `True`
- Quality score: `100`
- Answer: Hoje eu nao encontrei Joao entre os alunos vinculados a esta conta. No momento, os alunos que aparecem aqui sao: Lucas Oliveira (MAT-2026-001), Ana Oliveira (MAT-2026-002). Se quiser, me diga qual deles voce quer consultar.

### preciso falar com o financeiro

- Stack: `python_functions`
- Slice: `support`
- Thread: `obs_support_reroute` turn `1`
- Status: `200`
- Latency: `133.6 ms`
- Mode: `handoff`
- Reason: `o usuario demonstrou necessidade de atendimento humano ou operacional`
- Access tier: `public`
- Expected kernel: `kernel:python_functions`
- Observed kernel: `kernel:python_functions`
- Kernel consistency: `True`
- Keyword pass: `True`
- Quality score: `100`
- Answer: Sua solicitacao ja estava registrada na fila de financeiro. Protocolo: ATD-20260330-FDF65462. Status atual: queued.

### qual o protocolo?

- Stack: `python_functions`
- Slice: `support`
- Thread: `obs_support_reroute` turn `2`
- Status: `200`
- Latency: `158.2 ms`
- Mode: `structured_tool`
- Reason: `a solicitacao pode ser executada por workflow estruturado com protocolo`
- Access tier: `public`
- Expected kernel: `kernel:python_functions`
- Observed kernel: `kernel:python_functions`
- Kernel consistency: `True`
- Keyword pass: `True`
- Quality score: `100`
- Answer: O protocolo atual do seu atendimento e ATD-20260330-FDF65462. Se quiser, eu posso te dizer o status atual ou resumir o que ja foi registrado.

### mudei de ideia, quero secretaria

- Stack: `python_functions`
- Slice: `support`
- Thread: `obs_support_reroute` turn `3`
- Status: `200`
- Latency: `133.9 ms`
- Mode: `handoff`
- Reason: `o usuario demonstrou necessidade de atendimento humano ou operacional`
- Access tier: `public`
- Expected kernel: `kernel:python_functions`
- Observed kernel: `kernel:python_functions`
- Kernel consistency: `True`
- Keyword pass: `True`
- Quality score: `100`
- Answer: Sem problema, ajustei isso por aqui.

Sua solicitacao ja estava registrada na fila de secretaria. Protocolo: ATD-20260330-FDF65462. Status atual: queued.

### da pra marcar uma visita na quinta a tarde?

- Stack: `python_functions`
- Slice: `workflow`
- Thread: `obs_workflow_visit` turn `1`
- Status: `200`
- Latency: `151.4 ms`
- Mode: `structured_tool`
- Reason: `a solicitacao pode ser executada por workflow estruturado com protocolo`
- Access tier: `public`
- Expected kernel: `kernel:python_functions`
- Observed kernel: `kernel:python_functions`
- Kernel consistency: `True`
- Keyword pass: `True`
- Quality score: `100`
- Answer: Pedido de visita registrado para o Colegio Horizonte. Protocolo: VIS-20260330-2D2416. Preferencia informada: 2026-04-02 - tarde. Fila responsavel: admissoes. Ticket operacional: ATD-20260330-88979DB2. A equipe comercial valida a janela e retorna com a confirmacao.

### me fala o protocolo dessa visita

- Stack: `python_functions`
- Slice: `workflow`
- Thread: `obs_workflow_visit` turn `2`
- Status: `200`
- Latency: `151.8 ms`
- Mode: `structured_tool`
- Reason: `a solicitacao pode ser executada por workflow estruturado com protocolo`
- Access tier: `public`
- Expected kernel: `kernel:python_functions`
- Observed kernel: `kernel:python_functions`
- Kernel consistency: `True`
- Keyword pass: `True`
- Quality score: `100`
- Answer: O protocolo da sua visita e VIS-20260330-2D2416. Ticket operacional: ATD-20260330-88979DB2. Preferencia registrada: 02/04/2026 - tarde. Se quiser, eu tambem posso te dizer o status, remarcar ou cancelar a visita.

### e se eu precisar remarcar?

- Stack: `python_functions`
- Slice: `workflow`
- Thread: `obs_workflow_visit` turn `3`
- Status: `200`
- Latency: `150.1 ms`
- Mode: `structured_tool`
- Reason: `a solicitacao pode ser executada por workflow estruturado com protocolo`
- Access tier: `public`
- Expected kernel: `kernel:python_functions`
- Observed kernel: `kernel:python_functions`
- Kernel consistency: `True`
- Keyword pass: `True`
- Quality score: `100`
- Answer: Consigo remarcar a visita por aqui. Protocolo: VIS-20260330-2D2416. Ticket operacional: ATD-20260330-88979DB2. Me diga pelo menos o novo dia ou a janela desejada, por exemplo: "remarque para sexta de manha" ou "troque para 28/03 as 10h".

### entao remarca pra sexta de manha

- Stack: `python_functions`
- Slice: `workflow`
- Thread: `obs_workflow_visit` turn `4`
- Status: `200`
- Latency: `174.0 ms`
- Mode: `structured_tool`
- Reason: `a solicitacao pode ser executada por workflow estruturado com protocolo`
- Access tier: `public`
- Expected kernel: `kernel:python_functions`
- Observed kernel: `kernel:python_functions`
- Kernel consistency: `True`
- Keyword pass: `True`
- Quality score: `100`
- Answer: Pedido de visita atualizado com a fila de admissions. Protocolo: VIS-20260330-2D2416. Ticket operacional: ATD-20260330-88979DB2. Nova preferencia: 03/04/2026 - manha. Admissions valida a nova janela e retorna com a confirmacao.

### posso enviar documentos por fax ou isso nao existe mais?

- Stack: `llamaindex`
- Slice: `public`
- Thread: `obs_public_channels_docs` turn `1`
- Status: `200`
- Latency: `133.6 ms`
- Mode: `structured_tool`
- Reason: `contextual_public_direct_answer`
- Access tier: `public`
- Expected kernel: `kernel:llamaindex`
- Observed kernel: `kernel:llamaindex`
- Kernel consistency: `True`
- Keyword pass: `True`
- Quality score: `100`
- Answer: Hoje a escola nao utiliza fax para envio de documentos. Para isso, use portal institucional, email da secretaria, secretaria presencial.

### e por telegrama, serve?

- Stack: `llamaindex`
- Slice: `public`
- Thread: `obs_public_channels_docs` turn `2`
- Status: `200`
- Latency: `135.8 ms`
- Mode: `structured_tool`
- Reason: `contextual_public_direct_answer`
- Access tier: `public`
- Expected kernel: `kernel:llamaindex`
- Observed kernel: `kernel:llamaindex`
- Kernel consistency: `True`
- Keyword pass: `True`
- Quality score: `100`
- Answer: Hoje a escola nao publica telegrama como canal valido para documentos. Para isso, use portal institucional, email da secretaria, secretaria presencial.

### qual e o caminho certo pra mandar a documentacao?

- Stack: `llamaindex`
- Slice: `public`
- Thread: `obs_public_channels_docs` turn `3`
- Status: `200`
- Latency: `107.5 ms`
- Mode: `structured_tool`
- Reason: `contextual_public_direct_answer`
- Access tier: `public`
- Expected kernel: `kernel:llamaindex`
- Observed kernel: `kernel:llamaindex`
- Kernel consistency: `True`
- Keyword pass: `True`
- Quality score: `100`
- Answer: Sim. O envio inicial de documentos pode ser feito por canal digital.
Hoje os canais mais diretos publicados para isso sao:
- portal institucional
- email da secretaria
- secretaria presencial
No processo de matricula, o envio inicial pode ser digital. A validacao final continua com a secretaria.
O chat aberto nao deve receber documentos completos ou dados sensiveis. Quando possivel, use o portal autenticado ou o email institucional.

### voces realmente tem biblioteca ou e so folheto bonito?

- Stack: `llamaindex`
- Slice: `public`
- Thread: `obs_public_library_realism` turn `1`
- Status: `200`
- Latency: `138.2 ms`
- Mode: `structured_tool`
- Reason: `fato institucional canonico deve vir de fonte estruturada`
- Access tier: `public`
- Expected kernel: `kernel:llamaindex`
- Observed kernel: `kernel:llamaindex`
- Kernel consistency: `True`
- Keyword pass: `True`
- Quality score: `100`
- Answer: Sim. O Colegio Horizonte tem a Biblioteca Aurora. Atendimento ao publico de segunda a sexta, das 7h30 as 18h00.

### como ela se chama e ate que horas funciona?

- Stack: `llamaindex`
- Slice: `public`
- Thread: `obs_public_library_realism` turn `2`
- Status: `200`
- Latency: `112.4 ms`
- Mode: `structured_tool`
- Reason: `contextual_public_direct_answer`
- Access tier: `public`
- Expected kernel: `kernel:llamaindex`
- Observed kernel: `kernel:llamaindex`
- Kernel consistency: `True`
- Keyword pass: `True`
- Quality score: `100`
- Answer: A biblioteca se chama Biblioteca Aurora e funciona de segunda a sexta, das 7h30 as 18h00.

### como esta a documentacao da ana?

- Stack: `llamaindex`
- Slice: `protected`
- Thread: `obs_protected_docs_focus` turn `1`
- Status: `200`
- Latency: `191.2 ms`
- Mode: `structured_tool`
- Reason: `status administrativo autenticado exige service deterministico`
- Access tier: `authenticated`
- Expected kernel: `kernel:llamaindex`
- Observed kernel: `kernel:llamaindex`
- Kernel consistency: `True`
- Keyword pass: `True`
- Quality score: `100`
- Answer: Situacao documental de Ana Oliveira hoje: com pendencias.

### o que falta?

- Stack: `llamaindex`
- Slice: `protected`
- Thread: `obs_protected_docs_focus` turn `2`
- Status: `200`
- Latency: `182.4 ms`
- Mode: `structured_tool`
- Reason: `status administrativo autenticado exige service deterministico`
- Access tier: `authenticated`
- Expected kernel: `kernel:llamaindex`
- Observed kernel: `kernel:llamaindex`
- Kernel consistency: `True`
- Keyword pass: `True`
- Quality score: `100`
- Answer: Hoje, o proximo passo do seu cadastro e este: Envie o comprovante atualizado pela secretaria ou pelo canal de documentos para concluir a conferência.

### e a documentacao do lucas?

- Stack: `llamaindex`
- Slice: `protected`
- Thread: `obs_protected_docs_focus` turn `3`
- Status: `200`
- Latency: `162.5 ms`
- Mode: `structured_tool`
- Reason: `status administrativo autenticado exige service deterministico`
- Access tier: `authenticated`
- Expected kernel: `kernel:llamaindex`
- Observed kernel: `kernel:llamaindex`
- Kernel consistency: `True`
- Keyword pass: `True`
- Quality score: `100`
- Answer: Situacao documental de Lucas Oliveira hoje: regular.
- Identificacao escolar do aluno: regular. Codigo de matricula: MAT-2026-001
- Responsavel vinculado: regular. Maria Oliveira
- Documentacao escolar do aluno: regular. A documentacao escolar de Lucas Oliveira esta conferida e sem pendencias relevantes nesta base de testes.

### e se eu perguntar do joao?

- Stack: `llamaindex`
- Slice: `protected`
- Thread: `obs_protected_docs_focus` turn `4`
- Status: `200`
- Latency: `132.5 ms`
- Mode: `structured_tool`
- Reason: `status administrativo autenticado exige service deterministico`
- Access tier: `authenticated`
- Expected kernel: `kernel:llamaindex`
- Observed kernel: `kernel:llamaindex`
- Kernel consistency: `True`
- Keyword pass: `True`
- Quality score: `100`
- Answer: Hoje eu nao encontrei Joao entre os alunos vinculados a esta conta. No momento, os alunos que aparecem aqui sao: Lucas Oliveira (MAT-2026-001), Ana Oliveira (MAT-2026-002). Se quiser, me diga qual deles voce quer consultar.

### preciso falar com o financeiro

- Stack: `llamaindex`
- Slice: `support`
- Thread: `obs_support_reroute` turn `1`
- Status: `200`
- Latency: `144.7 ms`
- Mode: `handoff`
- Reason: `o usuario demonstrou necessidade de atendimento humano ou operacional`
- Access tier: `public`
- Expected kernel: `kernel:llamaindex`
- Observed kernel: `kernel:llamaindex`
- Kernel consistency: `True`
- Keyword pass: `True`
- Quality score: `100`
- Answer: Sua solicitacao ja estava registrada na fila de financeiro. Protocolo: ATD-20260330-2D2B72E6. Status atual: queued.

### qual o protocolo?

- Stack: `llamaindex`
- Slice: `support`
- Thread: `obs_support_reroute` turn `2`
- Status: `200`
- Latency: `159.6 ms`
- Mode: `structured_tool`
- Reason: `a solicitacao pode ser executada por workflow estruturado com protocolo`
- Access tier: `public`
- Expected kernel: `kernel:llamaindex`
- Observed kernel: `kernel:llamaindex`
- Kernel consistency: `True`
- Keyword pass: `True`
- Quality score: `100`
- Answer: O protocolo atual do seu atendimento e ATD-20260330-2D2B72E6. Se quiser, eu posso te dizer o status atual ou resumir o que ja foi registrado.

### mudei de ideia, quero secretaria

- Stack: `llamaindex`
- Slice: `support`
- Thread: `obs_support_reroute` turn `3`
- Status: `200`
- Latency: `131.4 ms`
- Mode: `handoff`
- Reason: `o usuario demonstrou necessidade de atendimento humano ou operacional`
- Access tier: `public`
- Expected kernel: `kernel:llamaindex`
- Observed kernel: `kernel:llamaindex`
- Kernel consistency: `True`
- Keyword pass: `True`
- Quality score: `100`
- Answer: Sem problema, ajustei isso por aqui.

Sua solicitacao ja estava registrada na fila de secretaria. Protocolo: ATD-20260330-2D2B72E6. Status atual: queued.

### da pra marcar uma visita na quinta a tarde?

- Stack: `llamaindex`
- Slice: `workflow`
- Thread: `obs_workflow_visit` turn `1`
- Status: `200`
- Latency: `161.8 ms`
- Mode: `structured_tool`
- Reason: `a solicitacao pode ser executada por workflow estruturado com protocolo`
- Access tier: `public`
- Expected kernel: `kernel:llamaindex`
- Observed kernel: `kernel:llamaindex`
- Kernel consistency: `True`
- Keyword pass: `True`
- Quality score: `100`
- Answer: Pedido de visita registrado para o Colegio Horizonte. Protocolo: VIS-20260330-6FAB31. Preferencia informada: 2026-04-02 - tarde. Fila responsavel: admissoes. Ticket operacional: ATD-20260330-2B72DD56. A equipe comercial valida a janela e retorna com a confirmacao.

### me fala o protocolo dessa visita

- Stack: `llamaindex`
- Slice: `workflow`
- Thread: `obs_workflow_visit` turn `2`
- Status: `200`
- Latency: `143.8 ms`
- Mode: `structured_tool`
- Reason: `a solicitacao pode ser executada por workflow estruturado com protocolo`
- Access tier: `public`
- Expected kernel: `kernel:llamaindex`
- Observed kernel: `kernel:llamaindex`
- Kernel consistency: `True`
- Keyword pass: `True`
- Quality score: `100`
- Answer: O protocolo da sua visita e VIS-20260330-6FAB31. Ticket operacional: ATD-20260330-2B72DD56. Preferencia registrada: 02/04/2026 - tarde. Se quiser, eu tambem posso te dizer o status, remarcar ou cancelar a visita.

### e se eu precisar remarcar?

- Stack: `llamaindex`
- Slice: `workflow`
- Thread: `obs_workflow_visit` turn `3`
- Status: `200`
- Latency: `167.8 ms`
- Mode: `structured_tool`
- Reason: `a solicitacao pode ser executada por workflow estruturado com protocolo`
- Access tier: `public`
- Expected kernel: `kernel:llamaindex`
- Observed kernel: `kernel:llamaindex`
- Kernel consistency: `True`
- Keyword pass: `True`
- Quality score: `100`
- Answer: Consigo remarcar a visita por aqui. Protocolo: VIS-20260330-6FAB31. Ticket operacional: ATD-20260330-2B72DD56. Me diga pelo menos o novo dia ou a janela desejada, por exemplo: "remarque para sexta de manha" ou "troque para 28/03 as 10h".

### entao remarca pra sexta de manha

- Stack: `llamaindex`
- Slice: `workflow`
- Thread: `obs_workflow_visit` turn `4`
- Status: `200`
- Latency: `155.9 ms`
- Mode: `structured_tool`
- Reason: `a solicitacao pode ser executada por workflow estruturado com protocolo`
- Access tier: `public`
- Expected kernel: `kernel:llamaindex`
- Observed kernel: `kernel:llamaindex`
- Kernel consistency: `True`
- Keyword pass: `True`
- Quality score: `100`
- Answer: Pedido de visita atualizado com a fila de admissions. Protocolo: VIS-20260330-6FAB31. Ticket operacional: ATD-20260330-2B72DD56. Nova preferencia: 03/04/2026 - manha. Admissions valida a nova janela e retorna com a confirmacao.

