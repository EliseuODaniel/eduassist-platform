# Five-Path Chatbot Comparison Report

Date: 2026-04-01T05:00:53.005661+00:00

Dataset: `tests/evals/datasets/system_question_bank_wave_teacher_workflow.json`

Run prefix: `debug:five-path:20260401T045656Z`

## Stack Summary

| Stack | OK | Keyword pass | Quality | Avg latency |
| --- | --- | --- | --- | --- |
| `langgraph` | `16/16` | `16/16` | `99.4` | `1410.7 ms` |
| `python_functions` | `16/16` | `16/16` | `99.4` | `1797.4 ms` |
| `llamaindex` | `16/16` | `16/16` | `99.4` | `3303.4 ms` |
| `specialist_supervisor` | `16/16` | `16/16` | `100.0` | `8190.5 ms` |

## By Slice

- `protected`
  - `langgraph`: ok 7/7, keyword pass 7/7, quality 98.6, latency 721.5ms
  - `python_functions`: ok 7/7, keyword pass 7/7, quality 98.6, latency 3794.5ms
  - `llamaindex`: ok 7/7, keyword pass 7/7, quality 98.6, latency 2318.9ms
  - `specialist_supervisor`: ok 7/7, keyword pass 7/7, quality 100.0, latency 14117.4ms
- `public`
  - `langgraph`: ok 1/1, keyword pass 1/1, quality 100.0, latency 4102.9ms
  - `python_functions`: ok 1/1, keyword pass 1/1, quality 100.0, latency 252.1ms
  - `llamaindex`: ok 1/1, keyword pass 1/1, quality 100.0, latency 10824.0ms
  - `specialist_supervisor`: ok 1/1, keyword pass 1/1, quality 100.0, latency 13262.0ms
- `workflow`
  - `langgraph`: ok 8/8, keyword pass 8/8, quality 100.0, latency 1677.3ms
  - `python_functions`: ok 8/8, keyword pass 8/8, quality 100.0, latency 243.0ms
  - `llamaindex`: ok 8/8, keyword pass 8/8, quality 100.0, latency 3224.8ms
  - `specialist_supervisor`: ok 8/8, keyword pass 8/8, quality 100.0, latency 2370.5ms

## Error Types

- `langgraph`: repetitive_reply=1
- `python_functions`: repetitive_reply=1
- `llamaindex`: repetitive_reply=1
- `specialist_supervisor`: nenhum

## Prompt Results

### Quais turmas e disciplinas eu tenho neste ano?

- Slice: `protected`
- Thread: `system_bank:professor_e_grade_docente:Q065` turn `1`
- `langgraph`: status 200, latency 385.5ms, keyword pass `True`, quality `100`, reason `teacher_role_rescue`
  answer: Voce esta falando aqui como Fernando Azevedo, no perfil de professor do Colegio Horizonte. No Telegram, nesta etapa eu consigo consultar sua grade docente, turmas e disciplinas. A situacao individual dos alunos ainda nao esta liberada por este canal. Se quiser, me pergunte "qual meu horario?", "quais sao minhas turmas?" ou "quais disciplinas eu ministro?".
- `python_functions`: status 200, latency 5381.5ms, keyword pass `True`, quality `100`, reason `python_functions_native_teacher_schedule`
  answer: Nao consegui consultar sua grade docente agora. Tente novamente em instantes.
- `llamaindex`: status 200, latency 147.2ms, keyword pass `True`, quality `100`, reason `dados estruturados devem passar por service deterministico`
  answer: Voce esta falando aqui como Fernando Azevedo, no perfil de professor do Colegio Horizonte. No Telegram, nesta etapa eu consigo consultar sua grade docente, turmas e disciplinas. A situacao individual dos alunos ainda nao esta liberada por este canal. Se quiser, me pergunte "qual meu horario?", "quais sao minhas turmas?" ou "quais disciplinas eu ministro?".
- `specialist_supervisor`: status 200, latency 23856.8ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_direct:academic_specialist`
  answer: Desculpe, só consigo responder a perguntas sobre notas, frequência, provas futuras e aprovação.

### Qual e a minha grade docente completa?

- Slice: `protected`
- Thread: `system_bank:professor_e_grade_docente:Q066` turn `1`
- `langgraph`: status 200, latency 157.8ms, keyword pass `True`, quality `100`, reason `teacher_role_rescue`
  answer: Voce esta falando aqui como Fernando Azevedo, no perfil de professor do Colegio Horizonte. No Telegram, nesta etapa eu consigo consultar sua grade docente, turmas e disciplinas. A situacao individual dos alunos ainda nao esta liberada por este canal. Se quiser, me pergunte "qual meu horario?", "quais sao minhas turmas?" ou "quais disciplinas eu ministro?".
- `python_functions`: status 200, latency 5217.9ms, keyword pass `True`, quality `100`, reason `python_functions_native_teacher_schedule`
  answer: Nao consegui consultar sua grade docente agora. Tente novamente em instantes.
- `llamaindex`: status 200, latency 5230.2ms, keyword pass `True`, quality `100`, reason `llamaindex_teacher_schedule_direct`
  answer: Nao consegui consultar sua grade docente agora. Tente novamente em instantes.
- `specialist_supervisor`: status 200, latency 6936.5ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_fast_path:general_knowledge`
  answer: Prefiro não responder a perguntas que envolvam informações pessoais ou específicas de um contexto individual.

### E so do ensino medio?

- Slice: `protected`
- Thread: `system_bank:professor_e_grade_docente:Q066` turn `2`
- `langgraph`: status 200, latency 175.2ms, keyword pass `True`, quality `90`, reason `teacher_role_rescue`
  errors: repetitive_reply
  answer: Voce esta falando aqui como Fernando Azevedo, no perfil de professor do Colegio Horizonte. No Telegram, nesta etapa eu consigo consultar sua grade docente, turmas e disciplinas. A situacao individual dos alunos ainda nao esta liberada por este canal. Se quiser, me pergunte "qual meu horario?", "quais sao minhas turmas?" ou "quais disciplinas eu ministro?".
- `python_functions`: status 200, latency 5238.1ms, keyword pass `True`, quality `90`, reason `python_functions_native_teacher_schedule`
  errors: repetitive_reply
  answer: Nao consegui consultar sua grade docente agora. Tente novamente em instantes.
- `llamaindex`: status 200, latency 5218.4ms, keyword pass `True`, quality `90`, reason `llamaindex_teacher_schedule_direct`
  errors: repetitive_reply
  answer: Nao consegui consultar sua grade docente agora. Tente novamente em instantes.
- `specialist_supervisor`: status 200, latency 11245.0ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_direct:institution_specialist`
  answer: Não, o Colégio Horizonte oferece o Ensino Fundamental II (do 6º ao 9º ano) e o Ensino Médio (da 1ª à 3ª série).

### Quais turmas eu atendo em Filosofia e em que classes?

- Slice: `protected`
- Thread: `system_bank:professor_e_grade_docente:Q068` turn `1`
- `langgraph`: status 200, latency 145.1ms, keyword pass `True`, quality `100`, reason `teacher_role_rescue`
  answer: Voce esta falando aqui como Fernando Azevedo, no perfil de professor do Colegio Horizonte. No Telegram, nesta etapa eu consigo consultar sua grade docente, turmas e disciplinas. A situacao individual dos alunos ainda nao esta liberada por este canal. Se quiser, me pergunte "qual meu horario?", "quais sao minhas turmas?" ou "quais disciplinas eu ministro?".
- `python_functions`: status 200, latency 5215.9ms, keyword pass `True`, quality `100`, reason `python_functions_native_teacher_schedule`
  answer: Nao consegui consultar sua grade docente agora. Tente novamente em instantes.
- `llamaindex`: status 200, latency 142.8ms, keyword pass `True`, quality `100`, reason `dados estruturados devem passar por service deterministico`
  answer: Voce esta falando aqui como Fernando Azevedo, no perfil de professor do Colegio Horizonte. No Telegram, nesta etapa eu consigo consultar sua grade docente, turmas e disciplinas. A situacao individual dos alunos ainda nao esta liberada por este canal. Se quiser, me pergunte "qual meu horario?", "quais sao minhas turmas?" ou "quais disciplinas eu ministro?".
- `specialist_supervisor`: status 200, latency 5593.7ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_resolved_intent:shift_offers`
  answer: Hoje o Colegio Horizonte publica estes turnos de atendimento escolar:
- Ensino Fundamental II: Manha (07:15 as 12:30).
- Ensino Medio: Manha (07:15 as 12:50).
- Fundamental II e Ensino Medio: Integral opcional (07:00 as 17:30).

### Resuma minha rotina docente junto com orientacoes publicas sobre calendario e comunicacao escolar.

- Slice: `protected`
- Thread: `system_bank:professor_e_grade_docente:Q069` turn `1`
- `langgraph`: status 200, latency 2147.5ms, keyword pass `True`, quality `100`, reason `teacher_role_rescue`
  answer: Voce esta falando aqui como Fernando Azevedo, no perfil de professor do Colegio Horizonte. No Telegram, nesta etapa eu consigo consultar sua grade docente, turmas e disciplinas. A situacao individual dos alunos ainda nao esta liberada por este canal. Se quiser, me pergunte "qual meu horario?", "quais sao minhas turmas?" ou "quais disciplinas eu ministro?".
- `python_functions`: status 200, latency 5195.4ms, keyword pass `True`, quality `100`, reason `python_functions_native_teacher_schedule`
  answer: Nao consegui consultar sua grade docente agora. Tente novamente em instantes.
- `llamaindex`: status 200, latency 5196.9ms, keyword pass `True`, quality `100`, reason `llamaindex_teacher_schedule_direct`
  answer: Nao consegui consultar sua grade docente agora. Tente novamente em instantes.
- `specialist_supervisor`: status 200, latency 24888.9ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_manager_safe_fallback`
  answer: Nao consegui consolidar essa resposta premium com seguranca agora. Se quiser, me diga exatamente se voce quer ver notas, frequencia, documentacao, financeiro ou status de protocolo.

### Sou professor de Filosofia e quero trabalhar ai; como faco para entrar em contato?

- Slice: `public`
- Thread: `system_bank:professor_e_grade_docente:Q070` turn `1`
- `langgraph`: status 200, latency 4102.9ms, keyword pass `True`, quality `100`, reason `fato institucional canonico deve vir de fonte estruturada`
  answer: Voce pode falar com Colegio Horizonte por estes canais oficiais:
- Secretaria: (11) 3333-4200
- Admissoes: (11) 3333-4201
- Orientacao educacional: (11) 3333-4202
- Financeiro: (11) 3333-4203
- Atendimento comercial: (11) 97500-2040
- Secretaria digital: (11) 97500-2041
- Secretaria: secretaria@colegiohorizonte.edu.br
- Admissoes: admissoes@colegiohorizonte.edu.br
- Orientacao educacional: orientacao@colegiohorizonte.edu.br
- Financeiro: financeiro@colegiohorizonte.edu.br
- Direcao: direcao@colegiohorizonte.edu.br
- Suporte digital: suporte.digital@colegiohorizonte.edu.br
- Talentos: talentos@colegiohorizonte.edu.br

O Colegio Horizonte nao divulga nomes nem contatos diretos de professores por disciplina, como filosofia e quero trabalhar ai; como faco para entrar em contato. Se quiser, eu posso te indicar a coordenacao pedagogica ou o setor certo para seguir com isso.
- `python_functions`: status 200, latency 252.1ms, keyword pass `True`, quality `100`, reason `python_functions_native_structured:institution`
  answer: Voce pode falar com Colegio Horizonte por estes canais oficiais:
- Secretaria: (11) 3333-4200
- Admissoes: (11) 3333-4201
- Orientacao educacional: (11) 3333-4202
- Financeiro: (11) 3333-4203
- Atendimento comercial: (11) 97500-2040
- Secretaria digital: (11) 97500-2041
- Secretaria: secretaria@colegiohorizonte.edu.br
- Admissoes: admissoes@colegiohorizonte.edu.br
- Orientacao educacional: orientacao@colegiohorizonte.edu.br
- Financeiro: financeiro@colegiohorizonte.edu.br
- Direcao: direcao@colegiohorizonte.edu.br
- Suporte digital: suporte.digital@colegiohorizonte.edu.br
- Talentos: talentos@colegiohorizonte.edu.br

O Colegio Horizonte nao divulga nomes nem contatos diretos de professores por disciplina, como filosofia e quero trabalhar ai; como faco para entrar em contato. Se quiser, eu posso te indicar a coordenacao pedagogica ou o setor certo para seguir com isso.
- `llamaindex`: status 200, latency 10824.0ms, keyword pass `True`, quality `100`, reason `llamaindex_public_profile`
  answer: Voce pode falar com Colegio Horizonte por estes canais oficiais:
- Secretaria: (11) 3333-4200
- Admissoes: (11) 3333-4201
- Orientacao educacional: (11) 3333-4202
- Financeiro: (11) 3333-4203
- Atendimento comercial: (11) 97500-2040
- Secretaria digital: (11) 97500-2041
- Secretaria: secretaria@colegiohorizonte.edu.br
- Admissoes: admissoes@colegiohorizonte.edu.br
- Orientacao educacional: orientacao@colegiohorizonte.edu.br
- Financeiro: financeiro@colegiohorizonte.edu.br
- Direcao: direcao@colegiohorizonte.edu.br
- Suporte digital: suporte.digital@colegiohorizonte.edu.br
- Talentos: talentos@colegiohorizonte.edu.br

O Colegio Horizonte nao divulga nomes nem contatos diretos de professores por disciplina, como filosofia e quero trabalhar ai; como faco para entrar em contato. Se quiser, eu posso te indicar a coordenacao pedagogica ou o setor certo para seguir com isso.
- `specialist_supervisor`: status 200, latency 13262.0ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_direct:institution_specialist`
  answer: Para entrar em contato com o Colégio Horizonte a respeito de oportunidades de trabalho como professor de Filosofia, você pode enviar seu currículo e informações para o e-mail do departamento de Talentos: talentos@colegiohorizonte.edu.br. Eles recebem currículos e orientam sobre os processos seletivos quando há vagas abertas.

### Me diga o nome e o telefone do professor de Educacao Fisica.

- Slice: `protected`
- Thread: `system_bank:professor_e_grade_docente:Q071` turn `1`
- `langgraph`: status 200, latency 166.1ms, keyword pass `True`, quality `100`, reason `status administrativo autenticado exige service deterministico`
  answer: Essa consulta depende de autenticacao e vinculo da sua conta no Telegram. Use o portal da escola para gerar o codigo de vinculacao e depois envie o comando `/start link_<codigo>` ao bot.
- `python_functions`: status 200, latency 168.9ms, keyword pass `True`, quality `100`, reason `python_functions_native_structured:institution`
  answer: Essa consulta depende de autenticacao e vinculo da sua conta no Telegram. Use o portal da escola para gerar o codigo de vinculacao e depois envie o comando `/start link_<codigo>` ao bot.
- `llamaindex`: status 200, latency 163.2ms, keyword pass `True`, quality `100`, reason `status administrativo autenticado exige service deterministico`
  answer: Essa consulta depende de autenticacao e vinculo da sua conta no Telegram. Use o portal da escola para gerar o codigo de vinculacao e depois envie o comando `/start link_<codigo>` ao bot.
- `specialist_supervisor`: status 200, latency 8045.9ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_direct:institution_specialist`
  answer: Não consegui encontrar o nome e o telefone do professor de Educação Física nas informações públicas disponíveis. As informações de contato fornecidas são para a secretaria, admissões, orientação educacional e financeiro.

### Gere um resumo enxuto da minha alocacao para eu revisar antes da reuniao pedagogica.

- Slice: `protected`
- Thread: `system_bank:professor_e_grade_docente:Q072` turn `1`
- `langgraph`: status 200, latency 1873.3ms, keyword pass `True`, quality `100`, reason `teacher_role_rescue`
  answer: Voce esta falando aqui como Fernando Azevedo, no perfil de professor do Colegio Horizonte. No Telegram, nesta etapa eu consigo consultar sua grade docente, turmas e disciplinas. A situacao individual dos alunos ainda nao esta liberada por este canal. Se quiser, me pergunte "qual meu horario?", "quais sao minhas turmas?" ou "quais disciplinas eu ministro?".
- `python_functions`: status 200, latency 143.6ms, keyword pass `True`, quality `100`, reason `python_functions_native_teacher_scope_guidance`
  answer: Voce esta falando aqui como Fernando Azevedo, no perfil de professor do Colegio Horizonte. No Telegram, nesta etapa eu consigo consultar sua grade docente, turmas e disciplinas. A situacao individual dos alunos ainda nao esta liberada por este canal. Se quiser, me pergunte "qual meu horario?", "quais sao minhas turmas?" ou "quais disciplinas eu ministro?".
- `llamaindex`: status 200, latency 133.6ms, keyword pass `True`, quality `100`, reason `llamaindex_teacher_scope_guidance`
  answer: Voce esta falando aqui como Fernando Azevedo, no perfil de professor do Colegio Horizonte. No Telegram, nesta etapa eu consigo consultar sua grade docente, turmas e disciplinas. A situacao individual dos alunos ainda nao esta liberada por este canal. Se quiser, me pergunte "qual meu horario?", "quais sao minhas turmas?" ou "quais disciplinas eu ministro?".
- `specialist_supervisor`: status 200, latency 18254.9ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_manager_safe_fallback`
  answer: Nao consegui consolidar essa resposta premium com seguranca agora. Se quiser, me diga exatamente se voce quer ver notas, frequencia, documentacao, financeiro ou status de protocolo.

### Quero agendar uma visita para conhecer a escola.

- Slice: `workflow`
- Thread: `system_bank:workflow_protocolos_visitas_e_handoff:Q073` turn `1`
- `langgraph`: status 200, latency 221.9ms, keyword pass `True`, quality `100`, reason `consulta publica de navegacao e canais foi resgatada do dominio support`
  answer: Pedido de visita registrado para o Colegio Horizonte. Protocolo: VIS-20260401-1B6530. Preferencia informada: janela a confirmar. Fila responsavel: admissoes. Ticket operacional: ATD-20260401-F741E73F. A equipe comercial valida a janela e retorna com a confirmacao.
- `python_functions`: status 200, latency 228.3ms, keyword pass `True`, quality `100`, reason `python_functions_native_structured:support`
  answer: Pedido de visita registrado para o Colegio Horizonte. Protocolo: VIS-20260401-A44041. Preferencia informada: janela a confirmar. Fila responsavel: admissoes. Ticket operacional: ATD-20260401-9D804ADF. A equipe comercial valida a janela e retorna com a confirmacao.
- `llamaindex`: status 200, latency 220.0ms, keyword pass `True`, quality `100`, reason `consulta publica de navegacao e canais foi resgatada do dominio support`
  answer: Pedido de visita registrado para o Colegio Horizonte. Protocolo: VIS-20260401-DCA5A2. Preferencia informada: janela a confirmar. Fila responsavel: admissoes. Ticket operacional: ATD-20260401-688E6FAA. A equipe comercial valida a janela e retorna com a confirmacao.
- `specialist_supervisor`: status 200, latency 590.1ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_tool_first:visit_booking`
  answer: Pedido de visita registrado. Protocolo: VIS-20260401-99D054. Preferencia registrada: janela a confirmar. Ticket operacional: ATD-20260401-45E2F230. Se quiser, eu tambem posso acompanhar o status ou remarcar a visita.

### Pode ser na quinta a tarde?

- Slice: `workflow`
- Thread: `system_bank:workflow_protocolos_visitas_e_handoff:Q073` turn `2`
- `langgraph`: status 200, latency 204.5ms, keyword pass `True`, quality `100`, reason `workflow_follow_up_rescue:visit_update`
  answer: Pedido de visita atualizado com a fila de admissions. Protocolo: VIS-20260401-1B6530. Ticket operacional: ATD-20260401-F741E73F. Nova preferencia: quinta-feira - tarde (02/04/2026 - 14:30). Admissions valida a nova janela e retorna com a confirmacao.
- `python_functions`: status 200, latency 328.9ms, keyword pass `True`, quality `100`, reason `consulta publica de navegacao e canais foi resgatada do dominio support`
  answer: Pedido de visita atualizado com a fila de admissions. Protocolo: VIS-20260401-A44041. Ticket operacional: ATD-20260401-9D804ADF. Nova preferencia: quinta-feira - tarde (02/04/2026 - 14:30). Admissions valida a nova janela e retorna com a confirmacao.
- `llamaindex`: status 200, latency 278.2ms, keyword pass `True`, quality `100`, reason `consulta publica de navegacao e canais foi resgatada do dominio support`
  answer: Pedido de visita atualizado com a fila de admissions. Protocolo: VIS-20260401-DCA5A2. Ticket operacional: ATD-20260401-688E6FAA. Nova preferencia: quinta-feira - tarde (02/04/2026 - 14:30). Admissions valida a nova janela e retorna com a confirmacao.
- `specialist_supervisor`: status 200, latency 579.6ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_tool_first:visit_reschedule`
  answer: Pedido de visita atualizado. Protocolo: VIS-20260401-99D054. Nova preferencia: quinta-feira, 14:30. Admissions valida a nova janela e retorna com a confirmacao.

### Qual e o protocolo dessa visita?

- Slice: `workflow`
- Thread: `system_bank:workflow_protocolos_visitas_e_handoff:Q073` turn `3`
- `langgraph`: status 200, latency 205.7ms, keyword pass `True`, quality `100`, reason `workflow_follow_up_rescue:visit_update`
  answer: Nao consegui atualizar a visita agora. Se quiser, me passe novamente o protocolo da visita ou o novo horario desejado.
- `python_functions`: status 200, latency 244.6ms, keyword pass `True`, quality `100`, reason `python_functions_native_structured:support`
  answer: Solicitacao institucional registrada para direcao. Protocolo: REQ-20260401-F04070. Assunto: Qual e o protocolo dessa visita? Fila responsavel: direcao. Ticket operacional: ATD-20260401-9D804ADF. A equipe faz a triagem inicial e segue o retorno pelo fluxo institucional.
- `llamaindex`: status 200, latency 221.7ms, keyword pass `True`, quality `100`, reason `consulta publica de navegacao e canais foi resgatada do dominio support`
  answer: Solicitacao institucional registrada para direcao. Protocolo: REQ-20260401-60896E. Assunto: Qual e o protocolo dessa visita? Fila responsavel: direcao. Ticket operacional: ATD-20260401-688E6FAA. A equipe faz a triagem inicial e segue o retorno pelo fluxo institucional.
- `specialist_supervisor`: status 200, latency 8427.0ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_direct:workflow_specialist`
  answer: O protocolo da sua visita é **VIS-20260401-99D054**. Ela está atualmente **em fila (queued)** para a área de **admissões**, com data preferencial para **02/04/2026 às 14:30**. O assunto é "Visita institucional" e o resumo da solicitação é "Pode ser na quinta a tarde?". Existe um ticket de atendimento vinculado: **ATD-20260401-45E2F230**.

### Preciso remarcar para a semana que vem.

- Slice: `workflow`
- Thread: `system_bank:workflow_protocolos_visitas_e_handoff:Q073` turn `4`
- `langgraph`: status 200, latency 2003.7ms, keyword pass `True`, quality `100`, reason `a intencao esta ambigua e exige clarificacao antes de recuperar contexto`
  answer: Olá! Para que eu possa te ajudar a remarcar, por favor, me informe o protocolo da visita que você quer alterar. Assim consigo localizar e verificar a disponibilidade para a semana que vem.
- `python_functions`: status 200, latency 288.5ms, keyword pass `True`, quality `100`, reason `a intencao esta ambigua e exige clarificacao antes de recuperar contexto`
  answer: Posso ajudar com informacoes publicas da escola, como calendario, matricula, documentos exigidos e regras de atendimento digital. Se quiser, pergunte por exemplo: "quais documentos preciso para a matricula?" ou "quando acontece a reuniao de pais?".
- `llamaindex`: status 200, latency 13356.2ms, keyword pass `True`, quality `100`, reason `llamaindex_public_profile`
  answer: Hoje o Colegio Horizonte publica estas janelas de visita:
- Visita guiada ao campus: terca-feira, das 09:00 as 10:15, em Recepcao principal e circuito pedagogico. Inclui apresentacao institucional, visita aos espacos e conversa curta com admissions.
- Visita guiada com foco pedagogico: quinta-feira, das 14:30 as 15:45, em Recepcao principal e salas de projeto. Janela pensada para familias que desejam conhecer infraestrutura, rotina e proposta pedagogica.
Agendamento: bot, whatsapp comercial ou admissions. Prazo de confirmacao: confirmacao em ate 1 dia util.
- `specialist_supervisor`: status 200, latency 566.6ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_tool_first:visit_reschedule_guidance`
  answer: Para remarcar a visita, eu sigo pelo protocolo VIS-20260401-99D054. A preferencia atual registrada e 02/04/2026 - 14:30. Me diga o novo dia ou janela desejada e eu atualizo o pedido. Ticket operacional: ATD-20260401-45E2F230.

### Agora cancela, por favor.

- Slice: `workflow`
- Thread: `system_bank:workflow_protocolos_visitas_e_handoff:Q073` turn `5`
- `langgraph`: status 200, latency 202.3ms, keyword pass `True`, quality `100`, reason `workflow_follow_up_rescue:visit_update`
  answer: Nao consegui atualizar a visita agora. Se quiser, me passe novamente o protocolo da visita ou o novo horario desejado.
- `python_functions`: status 200, latency 297.3ms, keyword pass `True`, quality `100`, reason `consulta publica de navegacao e canais foi resgatada do dominio support`
  answer: Nao consegui atualizar a visita agora. Se quiser, me passe novamente o protocolo da visita ou o novo horario desejado.
- `llamaindex`: status 200, latency 4514.0ms, keyword pass `True`, quality `100`, reason `llamaindex_public_profile`
  answer: Hoje e 1 de abril de 2026.
- `specialist_supervisor`: status 200, latency 7091.8ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_direct:workflow_specialist`
  answer: Para cancelar sua visita, preciso do código do protocolo. Você poderia me informar, por favor?

### Preciso emitir documentos finais e concluir a transferencia do Diego.

- Slice: `workflow`
- Thread: `system_bank:workflow_protocolos_visitas_e_handoff:Q078` turn `1`
- `langgraph`: status 200, latency 146.3ms, keyword pass `True`, quality `100`, reason `status administrativo autenticado exige service deterministico`
  answer: Hoje os documentos exigidos para a matricula publicados pela escola sao:
- Formulario cadastral preenchido
- Documento de identificacao do aluno
- CPF do aluno, quando houver
- Historico escolar
- Comprovante de residencia atualizado
- Documento de identificacao do responsavel legal
Se quiser, eu tambem posso explicar as etapas da matricula ou como funciona o envio inicial desses documentos.
- `python_functions`: status 200, latency 183.5ms, keyword pass `True`, quality `100`, reason `python_functions_native_structured:institution`
  answer: Hoje os documentos exigidos para a matricula publicados pela escola sao:
- Formulario cadastral preenchido
- Documento de identificacao do aluno
- CPF do aluno, quando houver
- Historico escolar
- Comprovante de residencia atualizado
- Documento de identificacao do responsavel legal
Se quiser, eu tambem posso explicar as etapas da matricula ou como funciona o envio inicial desses documentos.
- `llamaindex`: status 200, latency 129.7ms, keyword pass `True`, quality `100`, reason `status administrativo autenticado exige service deterministico`
  answer: Hoje os documentos exigidos para a matricula publicados pela escola sao:
- Formulario cadastral preenchido
- Documento de identificacao do aluno
- CPF do aluno, quando houver
- Historico escolar
- Comprovante de residencia atualizado
- Documento de identificacao do responsavel legal
Se quiser, eu tambem posso explicar as etapas da matricula ou como funciona o envio inicial desses documentos.
- `specialist_supervisor`: status 200, latency 590.3ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_tool_first:human_handoff`
  answer: Encaminhei sua solicitacao para a fila de secretaria. Protocolo: ATD-20260401-0F3C8832. Status atual: queued. Se preferir, voce tambem pode seguir pelo WhatsApp oficial (11) 97500-2040.

### Quero abrir um atendimento com o financeiro para negociar uma mensalidade parcialmente paga.

- Slice: `workflow`
- Thread: `system_bank:workflow_protocolos_visitas_e_handoff:Q079` turn `1`
- `langgraph`: status 200, latency 10247.9ms, keyword pass `True`, quality `100`, reason `o turno atual trouxe pistas explicitas de outro dominio protegido e o roteamento foi corrigido`
  answer: Sua conta tem mais de um aluno vinculado. Diga qual aluno deseja consultar: Lucas Oliveira (MAT-2026-001), Ana Oliveira (MAT-2026-002).
- `python_functions`: status 200, latency 169.5ms, keyword pass `True`, quality `100`, reason `python_functions_native_structured:institution`
  answer: Valores publicos de referencia para 2026:
- Ensino Fundamental II (Manha): mensalidade R$ 1.280,00 e taxa de matricula R$ 350,00. Valor comercial publico de referencia para 2026. Material didatico e uniforme sao cobrados a parte.
- Ensino Medio (Manha): mensalidade R$ 1.450,00 e taxa de matricula R$ 350,00. Valor comercial publico de referencia para 2026. Ha politica comercial para irmaos e pagamento pontual.
- Periodo integral opcional (Complemento contraturno): mensalidade R$ 480,00 e taxa de matricula R$ 0,00. Adicional mensal aplicado ao estudante matriculado no turno regular que aderir ao periodo integral.
Se quiser, eu tambem posso resumir bolsas, descontos comerciais e canais de matricula.
- `llamaindex`: status 200, latency 6881.1ms, keyword pass `True`, quality `100`, reason `llamaindex_public_profile`
  answer: Valores publicos de referencia para 2026:
- Ensino Fundamental II (Manha): mensalidade R$ 1.280,00 e taxa de matricula R$ 350,00. Valor comercial publico de referencia para 2026. Material didatico e uniforme sao cobrados a parte.
- Ensino Medio (Manha): mensalidade R$ 1.450,00 e taxa de matricula R$ 350,00. Valor comercial publico de referencia para 2026. Ha politica comercial para irmaos e pagamento pontual.
- Periodo integral opcional (Complemento contraturno): mensalidade R$ 480,00 e taxa de matricula R$ 0,00. Adicional mensal aplicado ao estudante matriculado no turno regular que aderir ao periodo integral.
Se quiser, eu tambem posso resumir bolsas, descontos comerciais e canais de matricula.
- `specialist_supervisor`: status 200, latency 558.3ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_resolved_intent:finance_student_clarify`
  answer: Consigo verificar a situacao financeira, mas preciso que voce me diga qual aluno: Lucas Oliveira ou Ana Oliveira?

### Qual a diferenca entre abrir um protocolo, um chamado e um handoff humano?

- Slice: `workflow`
- Thread: `system_bank:workflow_protocolos_visitas_e_handoff:Q080` turn `1`
- `langgraph`: status 200, latency 186.2ms, keyword pass `True`, quality `100`, reason `o usuario demonstrou necessidade de atendimento humano ou operacional`
  answer: Encaminhei sua solicitacao para a fila de atendimento. Protocolo: ATD-20260401-E8DA7B5C. Status atual: queued. A equipe humana pode continuar esse atendimento no portal operacional.
- `python_functions`: status 200, latency 203.7ms, keyword pass `True`, quality `100`, reason `o usuario demonstrou necessidade de atendimento humano ou operacional`
  answer: Encaminhei sua solicitacao para a fila de atendimento. Protocolo: ATD-20260401-70A9DDC5. Status atual: queued. A equipe humana pode continuar esse atendimento no portal operacional.
- `llamaindex`: status 200, latency 197.4ms, keyword pass `True`, quality `100`, reason `o usuario demonstrou necessidade de atendimento humano ou operacional`
  answer: Encaminhei sua solicitacao para a fila de atendimento. Protocolo: ATD-20260401-0DCC8D12. Status atual: queued. A equipe humana pode continuar esse atendimento no portal operacional.
- `specialist_supervisor`: status 200, latency 560.2ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_fast_path:support_process_boundary`
  answer: Hoje eu trato esses tres fluxos de forma diferente: protocolo registra uma solicitacao institucional rastreavel; chamado costuma ser o ticket operacional associado ao atendimento; e handoff humano e o encaminhamento real para uma fila ou equipe, normalmente com protocolo e status para acompanhamento.

