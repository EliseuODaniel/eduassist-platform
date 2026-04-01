# Five-Path Chatbot Comparison Report

Date: 2026-04-01T05:28:04.015916+00:00

Dataset: `tests/evals/datasets/system_question_bank_wave_teacher_workflow.json`

Run prefix: `debug:five-path:20260401T052108Z`

## Stack Summary

| Stack | OK | Keyword pass | Quality | Avg latency |
| --- | --- | --- | --- | --- |
| `langgraph` | `16/16` | `16/16` | `99.4` | `1442.0 ms` |
| `python_functions` | `16/16` | `16/16` | `99.4` | `1771.1 ms` |
| `llamaindex` | `16/16` | `16/16` | `98.8` | `3328.3 ms` |
| `crewai` | `16/16` | `16/16` | `100.0` | `8905.6 ms` |
| `specialist_supervisor` | `16/16` | `16/16` | `100.0` | `10452.4 ms` |

## By Slice

- `protected`
  - `langgraph`: ok 7/7, keyword pass 7/7, quality 98.6, latency 693.4ms
  - `python_functions`: ok 7/7, keyword pass 7/7, quality 98.6, latency 3759.3ms
  - `llamaindex`: ok 7/7, keyword pass 7/7, quality 98.6, latency 2328.6ms
  - `crewai`: ok 7/7, keyword pass 7/7, quality 100.0, latency 17502.1ms
  - `specialist_supervisor`: ok 7/7, keyword pass 7/7, quality 100.0, latency 18551.0ms
- `public`
  - `langgraph`: ok 1/1, keyword pass 1/1, quality 100.0, latency 4379.5ms
  - `python_functions`: ok 1/1, keyword pass 1/1, quality 100.0, latency 257.2ms
  - `llamaindex`: ok 1/1, keyword pass 1/1, quality 100.0, latency 10505.8ms
  - `crewai`: ok 1/1, keyword pass 1/1, quality 100.0, latency 207.2ms
  - `specialist_supervisor`: ok 1/1, keyword pass 1/1, quality 100.0, latency 20291.2ms
- `workflow`
  - `langgraph`: ok 8/8, keyword pass 8/8, quality 100.0, latency 1729.9ms
  - `python_functions`: ok 8/8, keyword pass 8/8, quality 100.0, latency 220.8ms
  - `llamaindex`: ok 8/8, keyword pass 8/8, quality 98.8, latency 3305.8ms
  - `crewai`: ok 8/8, keyword pass 8/8, quality 100.0, latency 2471.0ms
  - `specialist_supervisor`: ok 8/8, keyword pass 8/8, quality 100.0, latency 2136.2ms

## Error Types

- `langgraph`: repetitive_reply=1
- `python_functions`: repetitive_reply=1
- `llamaindex`: repetitive_reply=2
- `crewai`: nenhum
- `specialist_supervisor`: nenhum

## Prompt Results

### Quais turmas e disciplinas eu tenho neste ano?

- Slice: `protected`
- Thread: `system_bank:professor_e_grade_docente:Q065` turn `1`
- `langgraph`: status 200, latency 346.0ms, keyword pass `True`, quality `100`, reason `teacher_role_rescue`
  answer: Voce esta falando aqui como Fernando Azevedo, no perfil de professor do Colegio Horizonte. No Telegram, nesta etapa eu consigo consultar sua grade docente, turmas e disciplinas. A situacao individual dos alunos ainda nao esta liberada por este canal. Se quiser, me pergunte "qual meu horario?", "quais sao minhas turmas?" ou "quais disciplinas eu ministro?".
- `python_functions`: status 200, latency 5198.1ms, keyword pass `True`, quality `100`, reason `python_functions_native_teacher_schedule`
  answer: Nao consegui consultar sua grade docente agora. Tente novamente em instantes.
- `llamaindex`: status 200, latency 147.6ms, keyword pass `True`, quality `100`, reason `dados estruturados devem passar por service deterministico`
  answer: Voce esta falando aqui como Fernando Azevedo, no perfil de professor do Colegio Horizonte. No Telegram, nesta etapa eu consigo consultar sua grade docente, turmas e disciplinas. A situacao individual dos alunos ainda nao esta liberada por este canal. Se quiser, me pergunte "qual meu horario?", "quais sao minhas turmas?" ou "quais disciplinas eu ministro?".
- `crewai`: status 200, latency 14186.1ms, keyword pass `True`, quality `100`, reason `crewai_protected_flow_completed`
  answer: Para qual aluno você gostaria de saber as turmas e disciplinas?
- `specialist_supervisor`: status 200, latency 11600.3ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_direct:academic_specialist`
  answer: Você, Fernando Azevedo, é professor e suas turmas e disciplinas neste ano são:

*   **1o Ano A**: Química, Física
*   **2o Ano A**: Química, Física, Filosofia
*   **3o Ano A**: Química, Física, Filosofia
*   **6o Ano B**: História
*   **7o Ano B**: Geografia
*   **8o Ano B**: História, Geografia
*   **9o Ano B**: História, Geografia
*   **1o Ano B**: História, Filosofia
*   **2o Ano B**: Sociologia, Filosofia
*   **3o Ano B**: Sociologia

### Qual e a minha grade docente completa?

- Slice: `protected`
- Thread: `system_bank:professor_e_grade_docente:Q066` turn `1`
- `langgraph`: status 200, latency 127.8ms, keyword pass `True`, quality `100`, reason `teacher_role_rescue`
  answer: Voce esta falando aqui como Fernando Azevedo, no perfil de professor do Colegio Horizonte. No Telegram, nesta etapa eu consigo consultar sua grade docente, turmas e disciplinas. A situacao individual dos alunos ainda nao esta liberada por este canal. Se quiser, me pergunte "qual meu horario?", "quais sao minhas turmas?" ou "quais disciplinas eu ministro?".
- `python_functions`: status 200, latency 5204.4ms, keyword pass `True`, quality `100`, reason `python_functions_native_teacher_schedule`
  answer: Nao consegui consultar sua grade docente agora. Tente novamente em instantes.
- `llamaindex`: status 200, latency 5234.4ms, keyword pass `True`, quality `100`, reason `llamaindex_teacher_schedule_direct`
  answer: Nao consegui consultar sua grade docente agora. Tente novamente em instantes.
- `crewai`: status 200, latency 30052.7ms, keyword pass `True`, quality `100`, reason `crewai_protected_flow_completed`
  answer: Não consigo acessar a grade de horários dos professores no momento.
- `specialist_supervisor`: status 200, latency 6481.5ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_fast_path:general_knowledge`
  answer: Prefiro não responder a perguntas que envolvam informações pessoais ou específicas de um contexto individual.

### E so do ensino medio?

- Slice: `protected`
- Thread: `system_bank:professor_e_grade_docente:Q066` turn `2`
- `langgraph`: status 200, latency 180.1ms, keyword pass `True`, quality `90`, reason `teacher_role_rescue`
  errors: repetitive_reply
  answer: Voce esta falando aqui como Fernando Azevedo, no perfil de professor do Colegio Horizonte. No Telegram, nesta etapa eu consigo consultar sua grade docente, turmas e disciplinas. A situacao individual dos alunos ainda nao esta liberada por este canal. Se quiser, me pergunte "qual meu horario?", "quais sao minhas turmas?" ou "quais disciplinas eu ministro?".
- `python_functions`: status 200, latency 5221.6ms, keyword pass `True`, quality `90`, reason `python_functions_native_teacher_schedule`
  errors: repetitive_reply
  answer: Nao consegui consultar sua grade docente agora. Tente novamente em instantes.
- `llamaindex`: status 200, latency 5226.3ms, keyword pass `True`, quality `90`, reason `llamaindex_teacher_schedule_direct`
  errors: repetitive_reply
  answer: Nao consegui consultar sua grade docente agora. Tente novamente em instantes.
- `crewai`: status 200, latency 30159.7ms, keyword pass `True`, quality `100`, reason `crewai_primary_strict_safe_fallback`
  answer: Nao consegui consolidar essa consulta com seguranca agora. Se quiser, me diga exatamente se voce quer ver notas, frequencia, documentacao ou financeiro.
- `specialist_supervisor`: status 200, latency 10875.2ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_direct:institution_specialist`
  answer: Não, o Colégio Horizonte oferece tanto o Ensino Fundamental II (do 6º ao 9º ano) quanto o Ensino Médio (da 1ª à 3ª série).

### Quais turmas eu atendo em Filosofia e em que classes?

- Slice: `protected`
- Thread: `system_bank:professor_e_grade_docente:Q068` turn `1`
- `langgraph`: status 200, latency 150.8ms, keyword pass `True`, quality `100`, reason `teacher_role_rescue`
  answer: Voce esta falando aqui como Fernando Azevedo, no perfil de professor do Colegio Horizonte. No Telegram, nesta etapa eu consigo consultar sua grade docente, turmas e disciplinas. A situacao individual dos alunos ainda nao esta liberada por este canal. Se quiser, me pergunte "qual meu horario?", "quais sao minhas turmas?" ou "quais disciplinas eu ministro?".
- `python_functions`: status 200, latency 5191.5ms, keyword pass `True`, quality `100`, reason `python_functions_native_teacher_schedule`
  answer: Nao consegui consultar sua grade docente agora. Tente novamente em instantes.
- `llamaindex`: status 200, latency 147.5ms, keyword pass `True`, quality `100`, reason `dados estruturados devem passar por service deterministico`
  answer: Voce esta falando aqui como Fernando Azevedo, no perfil de professor do Colegio Horizonte. No Telegram, nesta etapa eu consigo consultar sua grade docente, turmas e disciplinas. A situacao individual dos alunos ainda nao esta liberada por este canal. Se quiser, me pergunte "qual meu horario?", "quais sao minhas turmas?" ou "quais disciplinas eu ministro?".
- `crewai`: status 200, latency 20274.7ms, keyword pass `True`, quality `100`, reason `crewai_protected_flow_timeout`
  answer: Eu nao consegui consolidar essa consulta protegida com seguranca agora. Se quiser, me diga qual aluno e qual dado voce quer consultar.
- `specialist_supervisor`: status 200, latency 5104.6ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_resolved_intent:shift_offers`
  answer: Hoje o Colegio Horizonte publica estes turnos de atendimento escolar:
- Ensino Fundamental II: Manha (07:15 as 12:30).
- Ensino Medio: Manha (07:15 as 12:50).
- Fundamental II e Ensino Medio: Integral opcional (07:00 as 17:30).

### Resuma minha rotina docente junto com orientacoes publicas sobre calendario e comunicacao escolar.

- Slice: `protected`
- Thread: `system_bank:professor_e_grade_docente:Q069` turn `1`
- `langgraph`: status 200, latency 1877.0ms, keyword pass `True`, quality `100`, reason `teacher_role_rescue`
  answer: Voce esta falando aqui como Fernando Azevedo, no perfil de professor do Colegio Horizonte. No Telegram, nesta etapa eu consigo consultar sua grade docente, turmas e disciplinas. A situacao individual dos alunos ainda nao esta liberada por este canal. Se quiser, me pergunte "qual meu horario?", "quais sao minhas turmas?" ou "quais disciplinas eu ministro?".
- `python_functions`: status 200, latency 5203.9ms, keyword pass `True`, quality `100`, reason `python_functions_native_teacher_schedule`
  answer: Nao consegui consultar sua grade docente agora. Tente novamente em instantes.
- `llamaindex`: status 200, latency 5251.3ms, keyword pass `True`, quality `100`, reason `llamaindex_teacher_schedule_direct`
  answer: Nao consegui consultar sua grade docente agora. Tente novamente em instantes.
- `crewai`: status 200, latency 27367.9ms, keyword pass `True`, quality `100`, reason `crewai_protected_flow_completed`
  answer: Não encontrei informações sobre sua rotina docente ou orientações públicas sobre calendário e comunicação escolar nos documentos disponíveis. Você gostaria de saber sobre outro tópico ou tem outras fontes de informação?
- `specialist_supervisor`: status 200, latency 60330.2ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_manager_judge:academic:structured_tools`
  answer: Não consegui obter um resumo da sua rotina docente específica, pois minhas ferramentas não acessam dados personalizados de professores. No entanto, posso fornecer as orientações públicas sobre o calendário escolar e os canais de comunicação institucional do Colégio Horizonte.

**Calendário Escolar Público (2026):**

*   **02 de fevereiro:** Início do ano letivo para o Ensino Fundamental II e Ensino Médio.
*   **28 de março:** Reunião geral de pais e responsáveis (apresentação do planejamento do primeiro bimestre).
*   **28 de março:** Reunião de responsáveis do 6º ao 9º ano.
*   **29 de março:** Reunião de responsáveis do Ensino Médio.
*   **11 de abril:** Plantão pedagógico do primeiro bimestre.
*   **16 de maio:** Mostra de ciências e tecnologia.
*   **23 de maio:** Mostra de projetos e feira de ciências.
*   **06 de junho:** Feira de orientação acadêmica e vocacional.
*   **13 de junho:** Festival esportivo da comunidade escolar.

**Canais e Orientações de Comunicação Escolar:**

O Colégio Horizonte disponibiliza diversos canais de comunicação para a comunidade escolar:

*   **Telefones:** Secretaria (11) 3333-4200, Orientação Educacional (11) 3333-4202, Financeiro (11) 3333-4203.
*   **WhatsApp:** Atendimento comercial (11) 97500-2040, Secretaria digital (11) 97500-2041.
*   **E-mails:** Secretaria (secretaria@colegiohorizonte.edu.br), Orientação Educacional (orientacao@colegiohorizonte.edu.br), Financeiro (financeiro@colegiohorizonte.edu.br), Direção (direcao@colegiohorizonte.edu.br), Suporte digital (suporte.digital@colegiohorizonte.edu.br).
*   **Instagram institucional:** @colegiohorizonte.

**Serviços de Comunicação e Suporte Relevantes:**

*   **Secretaria escolar e documentos:** Para declarações, histórico, transferência, comprovantes, uniformes e orientações administrativas. Canais: bot, secretaria presencial, e-mail institucional ou portal. Retorno em até 2 dias úteis. O envio inicial de documentos pode ser digital (portal institucional ou e-mail da secretaria), mas a validação final ocorre presencialmente na secretaria.
*   **Reunião com coordenação pedagógica:** Para transição de série, adaptação, rotina e acompanhamento escolar. Canais: bot, secretaria ou portal. Retorno em até 2 dias úteis.
*   **Orientação educacional e acompanhamento socioemocional:** Para adaptação escolar, convivência, bem-estar, rotina de estudo e apoio a famílias. Canais: bot, orientação educacional ou secretaria. Retorno em até 2 dias úteis.
*   **Suporte de portal, acesso e atendimento digital:** Para portal escolar, acesso, senha, dificuldades com o bot e orientação sobre canais digitais. Canais: bot, secretaria digital ou suporte digital. Retorno em até 1 dia útil.

É importante notar que, para envio de documentos completos ou dados sensíveis, o chat aberto não deve ser utilizado. Prefira o portal autenticado ou o e-mail institucional.

### Sou professor de Filosofia e quero trabalhar ai; como faco para entrar em contato?

- Slice: `public`
- Thread: `system_bank:professor_e_grade_docente:Q070` turn `1`
- `langgraph`: status 200, latency 4379.5ms, keyword pass `True`, quality `100`, reason `fato institucional canonico deve vir de fonte estruturada`
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
- `python_functions`: status 200, latency 257.2ms, keyword pass `True`, quality `100`, reason `python_functions_native_structured:institution`
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
- `llamaindex`: status 200, latency 10505.8ms, keyword pass `True`, quality `100`, reason `llamaindex_public_profile`
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
- `crewai`: status 200, latency 207.2ms, keyword pass `True`, quality `100`, reason `crewai_public_fast_path`
  answer: Secretaria (telefone): (11) 3333-4200
- `specialist_supervisor`: status 200, latency 20291.2ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_manager_judge:institution:structured_tools`
  answer: Para entrar em contato e se candidatar a uma vaga de professor(a) de Filosofia no Colégio Horizonte, você pode enviar seu currículo para o e-mail de talentos da escola: talentos@colegiohorizonte.edu.br. Este é o canal oficial para oportunidades docentes, onde eles recebem currículos e fornecem orientações sobre os processos seletivos. O tempo de retorno típico é de até 5 dias úteis.

### Me diga o nome e o telefone do professor de Educacao Fisica.

- Slice: `protected`
- Thread: `system_bank:professor_e_grade_docente:Q071` turn `1`
- `langgraph`: status 200, latency 181.0ms, keyword pass `True`, quality `100`, reason `status administrativo autenticado exige service deterministico`
  answer: Essa consulta depende de autenticacao e vinculo da sua conta no Telegram. Use o portal da escola para gerar o codigo de vinculacao e depois envie o comando `/start link_<codigo>` ao bot.
- `python_functions`: status 200, latency 167.1ms, keyword pass `True`, quality `100`, reason `python_functions_native_structured:institution`
  answer: Essa consulta depende de autenticacao e vinculo da sua conta no Telegram. Use o portal da escola para gerar o codigo de vinculacao e depois envie o comando `/start link_<codigo>` ao bot.
- `llamaindex`: status 200, latency 162.2ms, keyword pass `True`, quality `100`, reason `status administrativo autenticado exige service deterministico`
  answer: Essa consulta depende de autenticacao e vinculo da sua conta no Telegram. Use o portal da escola para gerar o codigo de vinculacao e depois envie o comando `/start link_<codigo>` ao bot.
- `crewai`: status 200, latency 244.8ms, keyword pass `True`, quality `100`, reason `crewai_protected_auth_required`
  answer: Essa consulta depende de autenticacao e vinculo da sua conta no Telegram. Use o portal da escola para gerar o codigo de vinculacao e depois envie o comando /start link_<codigo> ao bot.
- `specialist_supervisor`: status 200, latency 8860.1ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_direct:institution_specialist`
  answer: Não tenho disponível o nome e o telefone individual do professor de Educação Física nas informações públicas da escola. As informações de contato disponíveis são para os canais gerais da instituição, como a secretaria e coordenação.

### Gere um resumo enxuto da minha alocacao para eu revisar antes da reuniao pedagogica.

- Slice: `protected`
- Thread: `system_bank:professor_e_grade_docente:Q072` turn `1`
- `langgraph`: status 200, latency 1991.1ms, keyword pass `True`, quality `100`, reason `teacher_role_rescue`
  answer: Voce esta falando aqui como Fernando Azevedo, no perfil de professor do Colegio Horizonte. No Telegram, nesta etapa eu consigo consultar sua grade docente, turmas e disciplinas. A situacao individual dos alunos ainda nao esta liberada por este canal. Se quiser, me pergunte "qual meu horario?", "quais sao minhas turmas?" ou "quais disciplinas eu ministro?".
- `python_functions`: status 200, latency 128.5ms, keyword pass `True`, quality `100`, reason `python_functions_native_teacher_scope_guidance`
  answer: Voce esta falando aqui como Fernando Azevedo, no perfil de professor do Colegio Horizonte. No Telegram, nesta etapa eu consigo consultar sua grade docente, turmas e disciplinas. A situacao individual dos alunos ainda nao esta liberada por este canal. Se quiser, me pergunte "qual meu horario?", "quais sao minhas turmas?" ou "quais disciplinas eu ministro?".
- `llamaindex`: status 200, latency 130.8ms, keyword pass `True`, quality `100`, reason `llamaindex_teacher_scope_guidance`
  answer: Voce esta falando aqui como Fernando Azevedo, no perfil de professor do Colegio Horizonte. No Telegram, nesta etapa eu consigo consultar sua grade docente, turmas e disciplinas. A situacao individual dos alunos ainda nao esta liberada por este canal. Se quiser, me pergunte "qual meu horario?", "quais sao minhas turmas?" ou "quais disciplinas eu ministro?".
- `crewai`: status 200, latency 228.6ms, keyword pass `True`, quality `100`, reason `crewai_public_fast_path`
  answer: A proposta pedagogica publicada hoje combina A escola segue a BNCC e o curriculo do Ensino Medio articulado com projeto de vida, producao textual, cultura digital e aprofundamento academico progressivo. Na pratica, isso aparece em frentes como Tutoria academica e projeto de vida, Espaco Maker integrado ao curriculo, Acolhimento estruturado para familias e estudantes.
- `specialist_supervisor`: status 200, latency 26605.4ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_manager_judge:academic:structured_tools`
  answer: Fernando Azevedo, aqui está um resumo da sua alocação para revisão antes da reunião pedagógica:

Você está alocado para as seguintes turmas e disciplinas:

*   **1º Ano A:** Química, Física
*   **2º Ano A:** Química, Física, Filosofia
*   **3º Ano A:** Química, Física, Filosofia
*   **6º Ano B:** História
*   **7º Ano B:** Geografia
*   **8º Ano B:** História, Geografia
*   **9º Ano B:** História, Geografia
*   **1º Ano B:** História, Filosofia
*   **2º Ano B:** Sociologia, Filosofia
*   **3º Ano B:** Sociologia

### Quero agendar uma visita para conhecer a escola.

- Slice: `workflow`
- Thread: `system_bank:workflow_protocolos_visitas_e_handoff:Q073` turn `1`
- `langgraph`: status 200, latency 226.4ms, keyword pass `True`, quality `100`, reason `consulta publica de navegacao e canais foi resgatada do dominio support`
  answer: Pedido de visita registrado para o Colegio Horizonte. Protocolo: VIS-20260401-CF04FF. Preferencia informada: janela a confirmar. Fila responsavel: admissoes. Ticket operacional: ATD-20260401-EEE9EFA5. A equipe comercial valida a janela e retorna com a confirmacao.
- `python_functions`: status 200, latency 216.6ms, keyword pass `True`, quality `100`, reason `python_functions_native_structured:support`
  answer: Pedido de visita registrado para o Colegio Horizonte. Protocolo: VIS-20260401-71A0B4. Preferencia informada: janela a confirmar. Fila responsavel: admissoes. Ticket operacional: ATD-20260401-B4EF454A. A equipe comercial valida a janela e retorna com a confirmacao.
- `llamaindex`: status 200, latency 226.3ms, keyword pass `True`, quality `100`, reason `consulta publica de navegacao e canais foi resgatada do dominio support`
  answer: Pedido de visita registrado para o Colegio Horizonte. Protocolo: VIS-20260401-71E03A. Preferencia informada: janela a confirmar. Fila responsavel: admissoes. Ticket operacional: ATD-20260401-7BAD3B78. A equipe comercial valida a janela e retorna com a confirmacao.
- `crewai`: status 200, latency 248.3ms, keyword pass `True`, quality `100`, reason `workflow_visit_create`
  answer: Pedido de visita registrado para o Colegio Horizonte. Protocolo: VIS-20260401-FF6FB1. Preferencia informada: janela a confirmar. Fila responsavel: admissoes. Ticket operacional: ATD-20260401-490BA087. A equipe comercial valida a janela e retorna com a confirmacao.
- `specialist_supervisor`: status 200, latency 101.2ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_tool_first:visit_booking`
  answer: Pedido de visita registrado. Protocolo: VIS-20260401-B06D91. Preferencia registrada: janela a confirmar. Ticket operacional: ATD-20260401-57942DC7. Se quiser, eu tambem posso acompanhar o status ou remarcar a visita.

### Pode ser na quinta a tarde?

- Slice: `workflow`
- Thread: `system_bank:workflow_protocolos_visitas_e_handoff:Q073` turn `2`
- `langgraph`: status 200, latency 204.2ms, keyword pass `True`, quality `100`, reason `workflow_follow_up_rescue:visit_update`
  answer: Pedido de visita atualizado com a fila de admissions. Protocolo: VIS-20260401-CF04FF. Ticket operacional: ATD-20260401-EEE9EFA5. Nova preferencia: quinta-feira - tarde (02/04/2026 - 14:30). Admissions valida a nova janela e retorna com a confirmacao.
- `python_functions`: status 200, latency 297.9ms, keyword pass `True`, quality `100`, reason `consulta publica de navegacao e canais foi resgatada do dominio support`
  answer: Pedido de visita atualizado com a fila de admissions. Protocolo: VIS-20260401-71A0B4. Ticket operacional: ATD-20260401-B4EF454A. Nova preferencia: quinta-feira - tarde (02/04/2026 - 14:30). Admissions valida a nova janela e retorna com a confirmacao.
- `llamaindex`: status 200, latency 274.6ms, keyword pass `True`, quality `100`, reason `consulta publica de navegacao e canais foi resgatada do dominio support`
  answer: Pedido de visita atualizado com a fila de admissions. Protocolo: VIS-20260401-71E03A. Ticket operacional: ATD-20260401-7BAD3B78. Nova preferencia: quinta-feira - tarde (02/04/2026 - 14:30). Admissions valida a nova janela e retorna com a confirmacao.
- `crewai`: status 200, latency 308.9ms, keyword pass `True`, quality `100`, reason `workflow_visit_reschedule`
  answer: Pedido de visita atualizado com a fila de admissoes. - Protocolo: VIS-20260401-FF6FB1 - Ticket operacional: ATD-20260401-490BA087 - Nova preferencia: quinta-feira - tarde (02/04/2026 - 14:30) Proximo passo: admissions valida a nova janela e retorna com a confirmacao.
- `specialist_supervisor`: status 200, latency 102.0ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_tool_first:visit_reschedule`
  answer: Pedido de visita atualizado. Protocolo: VIS-20260401-B06D91. Nova preferencia: quinta-feira, 14:30. Admissions valida a nova janela e retorna com a confirmacao.

### Qual e o protocolo dessa visita?

- Slice: `workflow`
- Thread: `system_bank:workflow_protocolos_visitas_e_handoff:Q073` turn `3`
- `langgraph`: status 200, latency 210.9ms, keyword pass `True`, quality `100`, reason `workflow_follow_up_rescue:visit_update`
  answer: Nao consegui atualizar a visita agora. Se quiser, me passe novamente o protocolo da visita ou o novo horario desejado.
- `python_functions`: status 200, latency 241.4ms, keyword pass `True`, quality `100`, reason `python_functions_native_structured:support`
  answer: Solicitacao institucional registrada para direcao. Protocolo: REQ-20260401-4DB04B. Assunto: Qual e o protocolo dessa visita? Fila responsavel: direcao. Ticket operacional: ATD-20260401-B4EF454A. A equipe faz a triagem inicial e segue o retorno pelo fluxo institucional.
- `llamaindex`: status 200, latency 230.5ms, keyword pass `True`, quality `100`, reason `consulta publica de navegacao e canais foi resgatada do dominio support`
  answer: Solicitacao institucional registrada para direcao. Protocolo: REQ-20260401-A7D4AE. Assunto: Qual e o protocolo dessa visita? Fila responsavel: direcao. Ticket operacional: ATD-20260401-7BAD3B78. A equipe faz a triagem inicial e segue o retorno pelo fluxo institucional.
- `crewai`: status 200, latency 210.0ms, keyword pass `True`, quality `100`, reason `workflow_protocol_lookup`
  answer: O protocolo da sua visita e VIS-20260401-FF6FB1. - Ticket operacional: ATD-20260401-490BA087 - Preferencia registrada: quinta-feira - 14:30 (02/04/2026 - 14:30) Se quiser, eu tambem posso te dizer o status, remarcar ou cancelar a visita.
- `specialist_supervisor`: status 200, latency 7759.4ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_direct:workflow_specialist`
  answer: O protocolo da sua visita é **VIS-20260401-B06D91**. A solicitação está com o status de **em fila (queued)** para agendamento na área de **admissões**, com data preferencial para **02/04/2026 às 14:30**. O resumo da sua solicitação é: "Pode ser na quinta a tarde?".

### Preciso remarcar para a semana que vem.

- Slice: `workflow`
- Thread: `system_bank:workflow_protocolos_visitas_e_handoff:Q073` turn `4`
- `langgraph`: status 200, latency 2216.3ms, keyword pass `True`, quality `100`, reason `a intencao esta ambigua e exige clarificacao antes de recuperar contexto`
  answer: Compreendo que você deseja remarcar a visita. Para que eu possa ajudar, por favor, me informe o protocolo da visita que você quer remarcar. Assim, consigo verificar as opções e te auxiliar com a nova data.
- `python_functions`: status 200, latency 216.0ms, keyword pass `True`, quality `100`, reason `a intencao esta ambigua e exige clarificacao antes de recuperar contexto`
  answer: Posso ajudar com informacoes publicas da escola, como calendario, matricula, documentos exigidos e regras de atendimento digital. Se quiser, pergunte por exemplo: "quais documentos preciso para a matricula?" ou "quando acontece a reuniao de pais?".
- `llamaindex`: status 200, latency 10010.3ms, keyword pass `True`, quality `100`, reason `llamaindex_public_profile`
  answer: Hoje o Colegio Horizonte publica estas janelas de visita:
- Visita guiada ao campus: terca-feira, das 09:00 as 10:15, em Recepcao principal e circuito pedagogico. Inclui apresentacao institucional, visita aos espacos e conversa curta com admissions.
- Visita guiada com foco pedagogico: quinta-feira, das 14:30 as 15:45, em Recepcao principal e salas de projeto. Janela pensada para familias que desejam conhecer infraestrutura, rotina e proposta pedagogica.
Agendamento: bot, whatsapp comercial ou admissions. Prazo de confirmacao: confirmacao em ate 1 dia util.
- `crewai`: status 200, latency 302.5ms, keyword pass `True`, quality `100`, reason `workflow_visit_reschedule`
  answer: Pedido de visita atualizado com a fila de admissoes. - Protocolo: VIS-20260401-FF6FB1 - Ticket operacional: ATD-20260401-490BA087 - Nova preferencia: quinta-feira - 14:30 (09/04/2026 - 14:30) Proximo passo: admissions valida a nova janela e retorna com a confirmacao.
- `specialist_supervisor`: status 200, latency 90.8ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_tool_first:visit_reschedule_guidance`
  answer: Para remarcar a visita, eu sigo pelo protocolo VIS-20260401-B06D91. A preferencia atual registrada e 02/04/2026 - 14:30. Me diga o novo dia ou janela desejada e eu atualizo o pedido. Ticket operacional: ATD-20260401-57942DC7.

### Agora cancela, por favor.

- Slice: `workflow`
- Thread: `system_bank:workflow_protocolos_visitas_e_handoff:Q073` turn `5`
- `langgraph`: status 200, latency 215.3ms, keyword pass `True`, quality `100`, reason `workflow_follow_up_rescue:visit_update`
  answer: Nao consegui atualizar a visita agora. Se quiser, me passe novamente o protocolo da visita ou o novo horario desejado.
- `python_functions`: status 200, latency 290.6ms, keyword pass `True`, quality `100`, reason `consulta publica de navegacao e canais foi resgatada do dominio support`
  answer: Nao consegui atualizar a visita agora. Se quiser, me passe novamente o protocolo da visita ou o novo horario desejado.
- `llamaindex`: status 200, latency 12077.8ms, keyword pass `True`, quality `90`, reason `llamaindex_public_profile`
  errors: repetitive_reply
  answer: Hoje o Colegio Horizonte publica estas janelas de visita:
- Visita guiada ao campus: terca-feira, das 09:00 as 10:15, em Recepcao principal e circuito pedagogico. Inclui apresentacao institucional, visita aos espacos e conversa curta com admissions.
- Visita guiada com foco pedagogico: quinta-feira, das 14:30 as 15:45, em Recepcao principal e salas de projeto. Janela pensada para familias que desejam conhecer infraestrutura, rotina e proposta pedagogica.
Agendamento: bot, whatsapp comercial ou admissions. Prazo de confirmacao: confirmacao em ate 1 dia util.
- `crewai`: status 200, latency 17926.1ms, keyword pass `True`, quality `100`, reason `crewai_public_flow_completed`
  answer: O que você gostaria de cancelar em relação à escola?
- `specialist_supervisor`: status 200, latency 8772.8ms, keyword pass `True`, quality `100`, reason `A mensagem do usuário indica uma intenção de cancelamento. Com base no histórico da conversa, o fluxo de trabalho ativo mais recente é o agendamento de uma visita. É necessária uma clarificação para confirmar qual item específico o usuário deseja cancelar antes de prosseguir com a ação.`
  answer: Você gostaria de cancelar a visita agendada para o dia 02/04/2026 às 14:30 (Protocolo: VIS-20260401-B06D91)?

### Preciso emitir documentos finais e concluir a transferencia do Diego.

- Slice: `workflow`
- Thread: `system_bank:workflow_protocolos_visitas_e_handoff:Q078` turn `1`
- `langgraph`: status 200, latency 142.8ms, keyword pass `True`, quality `100`, reason `status administrativo autenticado exige service deterministico`
  answer: Hoje os documentos exigidos para a matricula publicados pela escola sao:
- Formulario cadastral preenchido
- Documento de identificacao do aluno
- CPF do aluno, quando houver
- Historico escolar
- Comprovante de residencia atualizado
- Documento de identificacao do responsavel legal
Se quiser, eu tambem posso explicar as etapas da matricula ou como funciona o envio inicial desses documentos.
- `python_functions`: status 200, latency 128.6ms, keyword pass `True`, quality `100`, reason `python_functions_native_structured:institution`
  answer: Hoje os documentos exigidos para a matricula publicados pela escola sao:
- Formulario cadastral preenchido
- Documento de identificacao do aluno
- CPF do aluno, quando houver
- Historico escolar
- Comprovante de residencia atualizado
- Documento de identificacao do responsavel legal
Se quiser, eu tambem posso explicar as etapas da matricula ou como funciona o envio inicial desses documentos.
- `llamaindex`: status 200, latency 127.9ms, keyword pass `True`, quality `100`, reason `status administrativo autenticado exige service deterministico`
  answer: Hoje os documentos exigidos para a matricula publicados pela escola sao:
- Formulario cadastral preenchido
- Documento de identificacao do aluno
- CPF do aluno, quando houver
- Historico escolar
- Comprovante de residencia atualizado
- Documento de identificacao do responsavel legal
Se quiser, eu tambem posso explicar as etapas da matricula ou como funciona o envio inicial desses documentos.
- `crewai`: status 200, latency 211.2ms, keyword pass `True`, quality `100`, reason `protected_shadow_needs_student_clarification`
  answer: Posso te ajudar com Lucas Oliveira, Ana Oliveira. Me diga qual aluno voce quer consultar.
- `specialist_supervisor`: status 200, latency 104.4ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_tool_first:human_handoff`
  answer: Encaminhei sua solicitacao para a fila de secretaria. Protocolo: ATD-20260401-76F779C6. Status atual: queued. Se preferir, voce tambem pode seguir pelo WhatsApp oficial (11) 97500-2040.

### Quero abrir um atendimento com o financeiro para negociar uma mensalidade parcialmente paga.

- Slice: `workflow`
- Thread: `system_bank:workflow_protocolos_visitas_e_handoff:Q079` turn `1`
- `langgraph`: status 200, latency 10254.1ms, keyword pass `True`, quality `100`, reason `o turno atual trouxe pistas explicitas de outro dominio protegido e o roteamento foi corrigido`
  answer: Sua conta tem mais de um aluno vinculado. Diga qual aluno deseja consultar: Lucas Oliveira (MAT-2026-001), Ana Oliveira (MAT-2026-002).
- `python_functions`: status 200, latency 165.8ms, keyword pass `True`, quality `100`, reason `python_functions_native_structured:institution`
  answer: Valores publicos de referencia para 2026:
- Ensino Fundamental II (Manha): mensalidade R$ 1.280,00 e taxa de matricula R$ 350,00. Valor comercial publico de referencia para 2026. Material didatico e uniforme sao cobrados a parte.
- Ensino Medio (Manha): mensalidade R$ 1.450,00 e taxa de matricula R$ 350,00. Valor comercial publico de referencia para 2026. Ha politica comercial para irmaos e pagamento pontual.
- Periodo integral opcional (Complemento contraturno): mensalidade R$ 480,00 e taxa de matricula R$ 0,00. Adicional mensal aplicado ao estudante matriculado no turno regular que aderir ao periodo integral.
Se quiser, eu tambem posso resumir bolsas, descontos comerciais e canais de matricula.
- `llamaindex`: status 200, latency 3298.3ms, keyword pass `True`, quality `100`, reason `llamaindex_public_profile`
  answer: Valores publicos de referencia para 2026:
- Ensino Fundamental II (Manha): mensalidade R$ 1.280,00 e taxa de matricula R$ 350,00. Valor comercial publico de referencia para 2026. Material didatico e uniforme sao cobrados a parte.
- Ensino Medio (Manha): mensalidade R$ 1.450,00 e taxa de matricula R$ 350,00. Valor comercial publico de referencia para 2026. Ha politica comercial para irmaos e pagamento pontual.
- Periodo integral opcional (Complemento contraturno): mensalidade R$ 480,00 e taxa de matricula R$ 0,00. Adicional mensal aplicado ao estudante matriculado no turno regular que aderir ao periodo integral.
Se quiser, eu tambem posso resumir bolsas, descontos comerciais e canais de matricula.
- `crewai`: status 200, latency 218.5ms, keyword pass `True`, quality `100`, reason `protected_shadow_needs_student_clarification`
  answer: Posso te ajudar com Lucas Oliveira, Ana Oliveira. Me diga qual aluno voce quer consultar.
- `specialist_supervisor`: status 200, latency 78.3ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_resolved_intent:finance_student_clarify`
  answer: Consigo verificar a situacao financeira, mas preciso que voce me diga qual aluno: Lucas Oliveira ou Ana Oliveira?

### Qual a diferenca entre abrir um protocolo, um chamado e um handoff humano?

- Slice: `workflow`
- Thread: `system_bank:workflow_protocolos_visitas_e_handoff:Q080` turn `1`
- `langgraph`: status 200, latency 369.3ms, keyword pass `True`, quality `100`, reason `o usuario demonstrou necessidade de atendimento humano ou operacional`
  answer: Encaminhei sua solicitacao para a fila de atendimento. Protocolo: ATD-20260401-B4B17473. Status atual: queued. A equipe humana pode continuar esse atendimento no portal operacional.
- `python_functions`: status 200, latency 209.1ms, keyword pass `True`, quality `100`, reason `o usuario demonstrou necessidade de atendimento humano ou operacional`
  answer: Encaminhei sua solicitacao para a fila de atendimento. Protocolo: ATD-20260401-CAFD1F00. Status atual: queued. A equipe humana pode continuar esse atendimento no portal operacional.
- `llamaindex`: status 200, latency 200.8ms, keyword pass `True`, quality `100`, reason `o usuario demonstrou necessidade de atendimento humano ou operacional`
  answer: Encaminhei sua solicitacao para a fila de atendimento. Protocolo: ATD-20260401-98835BD7. Status atual: queued. A equipe humana pode continuar esse atendimento no portal operacional.
- `crewai`: status 200, latency 342.3ms, keyword pass `True`, quality `100`, reason `support_handoff_created`
  answer: Encaminhei sua solicitacao para a fila de atendimento. Protocolo: ATD-20260401-90132B20. Status atual: queued. A equipe humana podera continuar esse atendimento no portal operacional.
- `specialist_supervisor`: status 200, latency 80.4ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_fast_path:support_process_boundary`
  answer: Hoje eu trato esses tres fluxos de forma diferente: protocolo registra uma solicitacao institucional rastreavel; chamado costuma ser o ticket operacional associado ao atendimento; e handoff humano e o encaminhamento real para uma fila ou equipe, normalmente com protocolo e status para acompanhamento.

