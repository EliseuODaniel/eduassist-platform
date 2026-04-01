# Five-Path Chatbot Comparison Report

Date: 2026-04-01T03:07:43.567583+00:00

Dataset: `tests/evals/datasets/system_question_bank_wave_teacher_workflow.json`

Run prefix: `debug:five-path:20260401T030630Z`

## Stack Summary

| Stack | OK | Keyword pass | Quality | Avg latency |
| --- | --- | --- | --- | --- |
| `langgraph` | `16/16` | `16/16` | `99.4` | `536.4 ms` |
| `crewai` | `16/16` | `16/16` | `99.4` | `2945.7 ms` |
| `python_functions` | `16/16` | `16/16` | `100.0` | `610.6 ms` |
| `llamaindex` | `16/16` | `16/16` | `98.8` | `467.9 ms` |
| `specialist_supervisor` | `16/16` | `16/16` | `96.9` | `17.4 ms` |

## By Slice

- `protected`
  - `langgraph`: ok 7/7, keyword pass 7/7, quality 98.6, latency 816.8ms
  - `crewai`: ok 7/7, keyword pass 7/7, quality 98.6, latency 2270.8ms
  - `python_functions`: ok 7/7, keyword pass 7/7, quality 100.0, latency 725.3ms
  - `llamaindex`: ok 7/7, keyword pass 7/7, quality 98.6, latency 555.9ms
  - `specialist_supervisor`: ok 7/7, keyword pass 7/7, quality 98.6, latency 17.3ms
- `public`
  - `langgraph`: ok 1/1, keyword pass 1/1, quality 100.0, latency 218.4ms
  - `crewai`: ok 1/1, keyword pass 1/1, quality 100.0, latency 817.2ms
  - `python_functions`: ok 1/1, keyword pass 1/1, quality 100.0, latency 170.5ms
  - `llamaindex`: ok 1/1, keyword pass 1/1, quality 100.0, latency 180.5ms
  - `specialist_supervisor`: ok 1/1, keyword pass 1/1, quality 100.0, latency 18.6ms
- `workflow`
  - `langgraph`: ok 8/8, keyword pass 8/8, quality 100.0, latency 330.9ms
  - `crewai`: ok 8/8, keyword pass 8/8, quality 100.0, latency 3802.4ms
  - `python_functions`: ok 8/8, keyword pass 8/8, quality 100.0, latency 565.1ms
  - `llamaindex`: ok 8/8, keyword pass 8/8, quality 98.8, latency 426.8ms
  - `specialist_supervisor`: ok 8/8, keyword pass 8/8, quality 95.0, latency 17.4ms

## Error Types

- `langgraph`: repetitive_reply=1
- `crewai`: repetitive_reply=1
- `python_functions`: nenhum
- `llamaindex`: repetitive_reply=2
- `specialist_supervisor`: repetitive_reply=5

## Prompt Results

### Quais turmas e disciplinas eu tenho neste ano?

- Slice: `protected`
- Thread: `system_bank:professor_e_grade_docente:Q065` turn `1`
- `langgraph`: status 200, latency 1569.9ms, keyword pass `True`, quality `100`, reason `teacher_role_rescue`
  answer: Voce esta falando aqui como Fernando Azevedo, no perfil de professor do Colegio Horizonte. No Telegram, nesta etapa eu consigo consultar sua grade docente, turmas e disciplinas. A situacao individual dos alunos ainda nao esta liberada por este canal. Se quiser, me pergunte "qual meu horario?", "quais sao minhas turmas?" ou "quais disciplinas eu ministro?".
- `crewai`: status 200, latency 5685.9ms, keyword pass `True`, quality `100`, reason `crewai_llm_not_configured`
  answer: Nao consegui consolidar essa consulta com seguranca agora. Se quiser, me diga exatamente se voce quer ver notas, frequencia, documentacao ou financeiro.
- `python_functions`: status 200, latency 530.5ms, keyword pass `True`, quality `100`, reason `python_functions_native_structured:academic`
  answer: Voce esta falando aqui como Fernando Azevedo, no perfil de professor do Colegio Horizonte. No Telegram, nesta etapa eu consigo consultar sua grade docente, turmas e disciplinas. A situacao individual dos alunos ainda nao esta liberada por este canal. Se quiser, me pergunte "qual meu horario?", "quais sao minhas turmas?" ou "quais disciplinas eu ministro?".
- `llamaindex`: status 200, latency 414.3ms, keyword pass `True`, quality `100`, reason `dados estruturados devem passar por service deterministico`
  answer: Voce esta falando aqui como Fernando Azevedo, no perfil de professor do Colegio Horizonte. No Telegram, nesta etapa eu consigo consultar sua grade docente, turmas e disciplinas. A situacao individual dos alunos ainda nao esta liberada por este canal. Se quiser, me pergunte "qual meu horario?", "quais sao minhas turmas?" ou "quais disciplinas eu ministro?".
- `specialist_supervisor`: status 200, latency 17.8ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_llm_unconfigured`
  answer: O caminho specialist_supervisor ainda nao esta com um provider LLM configurado neste ambiente.

### Qual e a minha grade docente completa?

- Slice: `protected`
- Thread: `system_bank:professor_e_grade_docente:Q066` turn `1`
- `langgraph`: status 200, latency 620.0ms, keyword pass `True`, quality `100`, reason `teacher_role_rescue`
  answer: Voce esta falando aqui como Fernando Azevedo, no perfil de professor do Colegio Horizonte. No Telegram, nesta etapa eu consigo consultar sua grade docente, turmas e disciplinas. A situacao individual dos alunos ainda nao esta liberada por este canal. Se quiser, me pergunte "qual meu horario?", "quais sao minhas turmas?" ou "quais disciplinas eu ministro?".
- `crewai`: status 200, latency 3763.2ms, keyword pass `True`, quality `100`, reason `crewai_protected_teacher_scope_preflow`
  answer: Grade docente de Fernando Azevedo:
- Fisica em 1o Ano A (2026).
- Quimica em 1o Ano A (2026).
- Filosofia em 1o Ano B (2026).
- Historia em 1o Ano B (2026).
- Filosofia em 2o Ano A (2026).
- Fisica em 2o Ano A (2026).
- Quimica em 2o Ano A (2026).
- Filosofia em 2o Ano B (2026).
- Sociologia em 2o Ano B (2026).
- Filosofia em 3o Ano A (2026).
- Fisica em 3o Ano A (2026).
- Quimica em 3o Ano A (2026).
- Sociologia em 3o Ano B (2026).
- Historia em 6o Ano B (2026).
- Geografia em 7o Ano B (2026).
- Geografia em 8o Ano B (2026).
- Historia em 8o Ano B (2026).
- Geografia em 9o Ano B (2026).
- Historia em 9o Ano B (2026).
- `python_functions`: status 200, latency 383.2ms, keyword pass `True`, quality `100`, reason `a intencao esta ambigua e exige clarificacao antes de recuperar contexto`
  answer: Posso ajudar com informacoes publicas da escola, como calendario, matricula, documentos exigidos e regras de atendimento digital. Se quiser, pergunte por exemplo: "quais documentos preciso para a matricula?" ou "quando acontece a reuniao de pais?".
- `llamaindex`: status 200, latency 692.2ms, keyword pass `True`, quality `100`, reason `llamaindex_public_profile`
  answer: Voce esta falando aqui como Fernando Azevedo, no perfil de professor do Colegio Horizonte. No Telegram, nesta etapa eu consigo consultar sua grade docente, turmas e disciplinas. A situacao individual dos alunos ainda nao esta liberada por este canal. Se quiser, me pergunte "qual meu horario?", "quais sao minhas turmas?" ou "quais disciplinas eu ministro?".
- `specialist_supervisor`: status 200, latency 17.3ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_llm_unconfigured`
  answer: O caminho specialist_supervisor ainda nao esta com um provider LLM configurado neste ambiente.

### E so do ensino medio?

- Slice: `protected`
- Thread: `system_bank:professor_e_grade_docente:Q066` turn `2`
- `langgraph`: status 200, latency 1129.9ms, keyword pass `True`, quality `90`, reason `teacher_role_rescue`
  errors: repetitive_reply
  answer: Voce esta falando aqui como Fernando Azevedo, no perfil de professor do Colegio Horizonte. No Telegram, nesta etapa eu consigo consultar sua grade docente, turmas e disciplinas. A situacao individual dos alunos ainda nao esta liberada por este canal. Se quiser, me pergunte "qual meu horario?", "quais sao minhas turmas?" ou "quais disciplinas eu ministro?".
- `crewai`: status 200, latency 601.8ms, keyword pass `True`, quality `90`, reason `crewai_protected_teacher_scope_preflow`
  errors: repetitive_reply
  answer: Grade docente de Fernando Azevedo:
- Fisica em 1o Ano A (2026).
- Quimica em 1o Ano A (2026).
- Filosofia em 1o Ano B (2026).
- Historia em 1o Ano B (2026).
- Filosofia em 2o Ano A (2026).
- Fisica em 2o Ano A (2026).
- Quimica em 2o Ano A (2026).
- Filosofia em 2o Ano B (2026).
- Sociologia em 2o Ano B (2026).
- Filosofia em 3o Ano A (2026).
- Fisica em 3o Ano A (2026).
- Quimica em 3o Ano A (2026).
- Sociologia em 3o Ano B (2026).
- Historia em 6o Ano B (2026).
- Geografia em 7o Ano B (2026).
- Geografia em 8o Ano B (2026).
- Historia em 8o Ano B (2026).
- Geografia em 9o Ano B (2026).
- Historia em 9o Ano B (2026).
- `python_functions`: status 200, latency 604.5ms, keyword pass `True`, quality `100`, reason `python_functions_native_structured:institution`
  answer: Voce esta falando aqui como Fernando Azevedo, no perfil de professor do Colegio Horizonte. No Telegram, nesta etapa eu consigo consultar sua grade docente, turmas e disciplinas. A situacao individual dos alunos ainda nao esta liberada por este canal. Se quiser, me pergunte "qual meu horario?", "quais sao minhas turmas?" ou "quais disciplinas eu ministro?".
- `llamaindex`: status 200, latency 2099.0ms, keyword pass `True`, quality `90`, reason `llamaindex_public_profile`
  errors: repetitive_reply
  answer: Voce esta falando aqui como Fernando Azevedo, no perfil de professor do Colegio Horizonte. No Telegram, nesta etapa eu consigo consultar sua grade docente, turmas e disciplinas. A situacao individual dos alunos ainda nao esta liberada por este canal. Se quiser, me pergunte "qual meu horario?", "quais sao minhas turmas?" ou "quais disciplinas eu ministro?".
- `specialist_supervisor`: status 200, latency 16.0ms, keyword pass `True`, quality `90`, reason `specialist_supervisor_llm_unconfigured`
  errors: repetitive_reply
  answer: O caminho specialist_supervisor ainda nao esta com um provider LLM configurado neste ambiente.

### Quais turmas eu atendo em Filosofia e em que classes?

- Slice: `protected`
- Thread: `system_bank:professor_e_grade_docente:Q068` turn `1`
- `langgraph`: status 200, latency 1894.8ms, keyword pass `True`, quality `100`, reason `teacher_role_rescue`
  answer: Voce esta falando aqui como Fernando Azevedo, no perfil de professor do Colegio Horizonte. No Telegram, nesta etapa eu consigo consultar sua grade docente, turmas e disciplinas. A situacao individual dos alunos ainda nao esta liberada por este canal. Se quiser, me pergunte "qual meu horario?", "quais sao minhas turmas?" ou "quais disciplinas eu ministro?".
- `crewai`: status 200, latency 4184.5ms, keyword pass `True`, quality `100`, reason `crewai_llm_not_configured`
  answer: Nao consegui consolidar essa consulta com seguranca agora. Se quiser, me diga exatamente se voce quer ver notas, frequencia, documentacao ou financeiro.
- `python_functions`: status 200, latency 332.4ms, keyword pass `True`, quality `100`, reason `python_functions_native_structured:academic`
  answer: Voce esta falando aqui como Fernando Azevedo, no perfil de professor do Colegio Horizonte. No Telegram, nesta etapa eu consigo consultar sua grade docente, turmas e disciplinas. A situacao individual dos alunos ainda nao esta liberada por este canal. Se quiser, me pergunte "qual meu horario?", "quais sao minhas turmas?" ou "quais disciplinas eu ministro?".
- `llamaindex`: status 200, latency 188.0ms, keyword pass `True`, quality `100`, reason `dados estruturados devem passar por service deterministico`
  answer: Voce esta falando aqui como Fernando Azevedo, no perfil de professor do Colegio Horizonte. No Telegram, nesta etapa eu consigo consultar sua grade docente, turmas e disciplinas. A situacao individual dos alunos ainda nao esta liberada por este canal. Se quiser, me pergunte "qual meu horario?", "quais sao minhas turmas?" ou "quais disciplinas eu ministro?".
- `specialist_supervisor`: status 200, latency 16.2ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_llm_unconfigured`
  answer: O caminho specialist_supervisor ainda nao esta com um provider LLM configurado neste ambiente.

### Resuma minha rotina docente junto com orientacoes publicas sobre calendario e comunicacao escolar.

- Slice: `protected`
- Thread: `system_bank:professor_e_grade_docente:Q069` turn `1`
- `langgraph`: status 200, latency 163.4ms, keyword pass `True`, quality `100`, reason `teacher_role_rescue`
  answer: Voce esta falando aqui como Fernando Azevedo, no perfil de professor do Colegio Horizonte. No Telegram, nesta etapa eu consigo consultar sua grade docente, turmas e disciplinas. A situacao individual dos alunos ainda nao esta liberada por este canal. Se quiser, me pergunte "qual meu horario?", "quais sao minhas turmas?" ou "quais disciplinas eu ministro?".
- `crewai`: status 200, latency 237.9ms, keyword pass `True`, quality `100`, reason `crewai_protected_teacher_scope_preflow`
  answer: Grade docente de Fernando Azevedo:
- Fisica em 1o Ano A (2026).
- Quimica em 1o Ano A (2026).
- Filosofia em 1o Ano B (2026).
- Historia em 1o Ano B (2026).
- Filosofia em 2o Ano A (2026).
- Fisica em 2o Ano A (2026).
- Quimica em 2o Ano A (2026).
- Filosofia em 2o Ano B (2026).
- Sociologia em 2o Ano B (2026).
- Filosofia em 3o Ano A (2026).
- Fisica em 3o Ano A (2026).
- Quimica em 3o Ano A (2026).
- Sociologia em 3o Ano B (2026).
- Historia em 6o Ano B (2026).
- Geografia em 7o Ano B (2026).
- Geografia em 8o Ano B (2026).
- Historia em 8o Ano B (2026).
- Geografia em 9o Ano B (2026).
- Historia em 9o Ano B (2026).
- `python_functions`: status 200, latency 2910.9ms, keyword pass `True`, quality `100`, reason `python_functions_native_public_retrieval`
  answer: Encontrei estes proximos eventos publicos no calendario escolar:
- 06/04/2026 09:00 a 06/04/2026 11:00: Visita guiada para familias interessadas. Apresentacao institucional do Fundamental II e Ensino Medio com tour pelos espacos.
- 11/04/2026 08:00 a 11/04/2026 12:00: Plantao pedagogico do primeiro bimestre. Atendimento com professores para esclarecimento de notas e frequencia.
- 18/04/2026 10:00 a 18/04/2026 11:30: Oficina aberta sobre bolsas e descontos. Encontro com admissoes e financeiro para explicar edital de bolsas e regras comerciais.
Tambem localizei estas referencias na base documental:
- - rotina academica organizada por turnos - biblioteca com atendimento ampliado - apoio de orientacao educacional - laboratorios e espacos de estudo acompanhados - comunicacao digital centralizada no portal e no bot oficial - calendario escolar publicado com antecedencia
- O dia escolar combina acolhimento, aulas regulares, intervalos, uso de espacos pedagógicos e fechamento com orientacoes de rotina.
Fontes:
- Apresentacao Institucional do Colegio Horizonte (v2026.2)
- Rotina e Vida Escolar (v2026.2)
- Inclusao, Acessibilidade e Seguranca (v2026.2)
- `llamaindex`: status 200, latency 166.4ms, keyword pass `True`, quality `100`, reason `llamaindex_public_profile`
  answer: Voce esta falando aqui como Fernando Azevedo, no perfil de professor do Colegio Horizonte. No Telegram, nesta etapa eu consigo consultar sua grade docente, turmas e disciplinas. A situacao individual dos alunos ainda nao esta liberada por este canal. Se quiser, me pergunte "qual meu horario?", "quais sao minhas turmas?" ou "quais disciplinas eu ministro?".
- `specialist_supervisor`: status 200, latency 18.0ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_llm_unconfigured`
  answer: O caminho specialist_supervisor ainda nao esta com um provider LLM configurado neste ambiente.

### Sou professor de Filosofia e quero trabalhar ai; como faco para entrar em contato?

- Slice: `public`
- Thread: `system_bank:professor_e_grade_docente:Q070` turn `1`
- `langgraph`: status 200, latency 218.4ms, keyword pass `True`, quality `100`, reason `fato institucional canonico deve vir de fonte estruturada`
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
- `crewai`: status 200, latency 817.2ms, keyword pass `True`, quality `100`, reason `crewai_public_fast_path`
  answer: Secretaria (telefone): (11) 3333-4200
- `python_functions`: status 200, latency 170.5ms, keyword pass `True`, quality `100`, reason `python_functions_native_structured:institution`
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
- `llamaindex`: status 200, latency 180.5ms, keyword pass `True`, quality `100`, reason `llamaindex_public_profile`
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
- `specialist_supervisor`: status 200, latency 18.6ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_llm_unconfigured`
  answer: O caminho specialist_supervisor ainda nao esta com um provider LLM configurado neste ambiente.

### Me diga o nome e o telefone do professor de Educacao Fisica.

- Slice: `protected`
- Thread: `system_bank:professor_e_grade_docente:Q071` turn `1`
- `langgraph`: status 200, latency 177.0ms, keyword pass `True`, quality `100`, reason `status administrativo autenticado exige service deterministico`
  answer: Essa consulta depende de autenticacao e vinculo da sua conta no Telegram. Use o portal da escola para gerar o codigo de vinculacao e depois envie o comando `/start link_<codigo>` ao bot.
- `crewai`: status 200, latency 975.9ms, keyword pass `True`, quality `100`, reason `crewai_protected_auth_required`
  answer: Essa consulta depende de autenticacao e vinculo da sua conta no Telegram. Use o portal da escola para gerar o codigo de vinculacao e depois envie o comando /start link_<codigo> ao bot.
- `python_functions`: status 200, latency 162.7ms, keyword pass `True`, quality `100`, reason `python_functions_native_structured:institution`
  answer: Essa consulta depende de autenticacao e vinculo da sua conta no Telegram. Use o portal da escola para gerar o codigo de vinculacao e depois envie o comando `/start link_<codigo>` ao bot.
- `llamaindex`: status 200, latency 178.9ms, keyword pass `True`, quality `100`, reason `status administrativo autenticado exige service deterministico`
  answer: Essa consulta depende de autenticacao e vinculo da sua conta no Telegram. Use o portal da escola para gerar o codigo de vinculacao e depois envie o comando `/start link_<codigo>` ao bot.
- `specialist_supervisor`: status 200, latency 18.2ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_llm_unconfigured`
  answer: O caminho specialist_supervisor ainda nao esta com um provider LLM configurado neste ambiente.

### Gere um resumo enxuto da minha alocacao para eu revisar antes da reuniao pedagogica.

- Slice: `protected`
- Thread: `system_bank:professor_e_grade_docente:Q072` turn `1`
- `langgraph`: status 200, latency 162.7ms, keyword pass `True`, quality `100`, reason `teacher_role_rescue`
  answer: Voce esta falando aqui como Fernando Azevedo, no perfil de professor do Colegio Horizonte. No Telegram, nesta etapa eu consigo consultar sua grade docente, turmas e disciplinas. A situacao individual dos alunos ainda nao esta liberada por este canal. Se quiser, me pergunte "qual meu horario?", "quais sao minhas turmas?" ou "quais disciplinas eu ministro?".
- `crewai`: status 200, latency 446.6ms, keyword pass `True`, quality `100`, reason `crewai_public_fast_path`
  answer: A proposta pedagogica publicada hoje combina A escola segue a BNCC e o curriculo do Ensino Medio articulado com projeto de vida, producao textual, cultura digital e aprofundamento academico progressivo. Na pratica, isso aparece em frentes como Tutoria academica e projeto de vida, Espaco Maker integrado ao curriculo, Acolhimento estruturado para familias e estudantes.
- `python_functions`: status 200, latency 153.0ms, keyword pass `True`, quality `100`, reason `python_functions_native_teacher_scope_guidance`
  answer: Voce esta falando aqui como Fernando Azevedo, no perfil de professor do Colegio Horizonte. No Telegram, nesta etapa eu consigo consultar sua grade docente, turmas e disciplinas. A situacao individual dos alunos ainda nao esta liberada por este canal. Se quiser, me pergunte "qual meu horario?", "quais sao minhas turmas?" ou "quais disciplinas eu ministro?".
- `llamaindex`: status 200, latency 152.8ms, keyword pass `True`, quality `100`, reason `llamaindex_public_profile`
  answer: Voce esta falando aqui como Fernando Azevedo, no perfil de professor do Colegio Horizonte. No Telegram, nesta etapa eu consigo consultar sua grade docente, turmas e disciplinas. A situacao individual dos alunos ainda nao esta liberada por este canal. Se quiser, me pergunte "qual meu horario?", "quais sao minhas turmas?" ou "quais disciplinas eu ministro?".
- `specialist_supervisor`: status 200, latency 17.8ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_llm_unconfigured`
  answer: O caminho specialist_supervisor ainda nao esta com um provider LLM configurado neste ambiente.

### Quero agendar uma visita para conhecer a escola.

- Slice: `workflow`
- Thread: `system_bank:workflow_protocolos_visitas_e_handoff:Q073` turn `1`
- `langgraph`: status 200, latency 230.4ms, keyword pass `True`, quality `100`, reason `consulta publica de navegacao e canais foi resgatada do dominio support`
  answer: Pedido de visita registrado para o Colegio Horizonte. Protocolo: VIS-20260401-2D997E. Preferencia informada: janela a confirmar. Fila responsavel: admissoes. Ticket operacional: ATD-20260401-A5E8ED4E. A equipe comercial valida a janela e retorna com a confirmacao.
- `crewai`: status 200, latency 300.0ms, keyword pass `True`, quality `100`, reason `workflow_visit_create`
  answer: Pedido de visita registrado para o Colegio Horizonte. Protocolo: VIS-20260401-16B022. Preferencia informada: janela a confirmar. Fila responsavel: admissoes. Ticket operacional: ATD-20260401-68BAFCB3. A equipe comercial valida a janela e retorna com a confirmacao.
- `python_functions`: status 200, latency 209.0ms, keyword pass `True`, quality `100`, reason `python_functions_native_structured:support`
  answer: Pedido de visita registrado para o Colegio Horizonte. Protocolo: VIS-20260401-820F1D. Preferencia informada: janela a confirmar. Fila responsavel: admissoes. Ticket operacional: ATD-20260401-D14F192B. A equipe comercial valida a janela e retorna com a confirmacao.
- `llamaindex`: status 200, latency 215.9ms, keyword pass `True`, quality `100`, reason `consulta publica de navegacao e canais foi resgatada do dominio support`
  answer: Pedido de visita registrado para o Colegio Horizonte. Protocolo: VIS-20260401-4F62AE. Preferencia informada: janela a confirmar. Fila responsavel: admissoes. Ticket operacional: ATD-20260401-E61C31DC. A equipe comercial valida a janela e retorna com a confirmacao.
- `specialist_supervisor`: status 200, latency 17.8ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_llm_unconfigured`
  answer: O caminho specialist_supervisor ainda nao esta com um provider LLM configurado neste ambiente.

### Pode ser na quinta a tarde?

- Slice: `workflow`
- Thread: `system_bank:workflow_protocolos_visitas_e_handoff:Q073` turn `2`
- `langgraph`: status 200, latency 212.0ms, keyword pass `True`, quality `100`, reason `workflow_follow_up_rescue:visit_update`
  answer: Pedido de visita atualizado com a fila de admissions. Protocolo: VIS-20260401-2D997E. Ticket operacional: ATD-20260401-A5E8ED4E. Nova preferencia: quinta-feira - tarde (02/04/2026 - 14:30). Admissions valida a nova janela e retorna com a confirmacao.
- `crewai`: status 200, latency 904.7ms, keyword pass `True`, quality `100`, reason `workflow_visit_reschedule`
  answer: Pedido de visita atualizado com a fila de admissoes. - Protocolo: VIS-20260401-16B022 - Ticket operacional: ATD-20260401-68BAFCB3 - Nova preferencia: quinta-feira - tarde (02/04/2026 - 14:30) Proximo passo: admissions valida a nova janela e retorna com a confirmacao.
- `python_functions`: status 200, latency 2204.4ms, keyword pass `True`, quality `100`, reason `consulta publica de navegacao e canais foi resgatada do dominio support`
  answer: Pedido de visita atualizado com a fila de admissions. Protocolo: VIS-20260401-820F1D. Ticket operacional: ATD-20260401-D14F192B. Nova preferencia: quinta-feira - tarde (02/04/2026 - 14:30). Admissions valida a nova janela e retorna com a confirmacao.
- `llamaindex`: status 200, latency 1327.4ms, keyword pass `True`, quality `100`, reason `consulta publica de navegacao e canais foi resgatada do dominio support`
  answer: Pedido de visita atualizado com a fila de admissions. Protocolo: VIS-20260401-4F62AE. Ticket operacional: ATD-20260401-E61C31DC. Nova preferencia: quinta-feira - tarde (02/04/2026 - 14:30). Admissions valida a nova janela e retorna com a confirmacao.
- `specialist_supervisor`: status 200, latency 15.1ms, keyword pass `True`, quality `90`, reason `specialist_supervisor_llm_unconfigured`
  errors: repetitive_reply
  answer: O caminho specialist_supervisor ainda nao esta com um provider LLM configurado neste ambiente.

### Qual e o protocolo dessa visita?

- Slice: `workflow`
- Thread: `system_bank:workflow_protocolos_visitas_e_handoff:Q073` turn `3`
- `langgraph`: status 200, latency 511.5ms, keyword pass `True`, quality `100`, reason `workflow_follow_up_rescue:visit_update`
  answer: Nao consegui atualizar a visita agora. Se quiser, me passe novamente o protocolo da visita ou o novo horario desejado.
- `crewai`: status 200, latency 5917.7ms, keyword pass `True`, quality `100`, reason `workflow_protocol_lookup`
  answer: O protocolo da sua visita e VIS-20260401-16B022. - Ticket operacional: ATD-20260401-68BAFCB3 - Preferencia registrada: quinta-feira - 14:30 (02/04/2026 - 14:30) Se quiser, eu tambem posso te dizer o status, remarcar ou cancelar a visita.
- `python_functions`: status 200, latency 944.5ms, keyword pass `True`, quality `100`, reason `python_functions_native_structured:support`
  answer: Solicitacao institucional registrada para direcao. Protocolo: REQ-20260401-86939F. Assunto: Qual e o protocolo dessa visita? Fila responsavel: direcao. Ticket operacional: ATD-20260401-D14F192B. A equipe faz a triagem inicial e segue o retorno pelo fluxo institucional.
- `llamaindex`: status 200, latency 972.8ms, keyword pass `True`, quality `100`, reason `consulta publica de navegacao e canais foi resgatada do dominio support`
  answer: Solicitacao institucional registrada para direcao. Protocolo: REQ-20260401-3D92F2. Assunto: Qual e o protocolo dessa visita? Fila responsavel: direcao. Ticket operacional: ATD-20260401-E61C31DC. A equipe faz a triagem inicial e segue o retorno pelo fluxo institucional.
- `specialist_supervisor`: status 200, latency 16.4ms, keyword pass `True`, quality `90`, reason `specialist_supervisor_llm_unconfigured`
  errors: repetitive_reply
  answer: O caminho specialist_supervisor ainda nao esta com um provider LLM configurado neste ambiente.

### Preciso remarcar para a semana que vem.

- Slice: `workflow`
- Thread: `system_bank:workflow_protocolos_visitas_e_handoff:Q073` turn `4`
- `langgraph`: status 200, latency 927.9ms, keyword pass `True`, quality `100`, reason `a intencao esta ambigua e exige clarificacao antes de recuperar contexto`
  answer: Posso ajudar com informacoes publicas da escola, como calendario, matricula, documentos exigidos e regras de atendimento digital. Se quiser, pergunte por exemplo: "quais documentos preciso para a matricula?" ou "quando acontece a reuniao de pais?".
- `crewai`: status 200, latency 22367.0ms, keyword pass `True`, quality `100`, reason `workflow_visit_reschedule`
  answer: Pedido de visita atualizado com a fila de admissoes. - Protocolo: VIS-20260401-16B022 - Ticket operacional: ATD-20260401-68BAFCB3 - Nova preferencia: quinta-feira - 14:30 (09/04/2026 - 14:30) Proximo passo: admissions valida a nova janela e retorna com a confirmacao.
- `python_functions`: status 200, latency 435.6ms, keyword pass `True`, quality `100`, reason `a intencao esta ambigua e exige clarificacao antes de recuperar contexto`
  answer: Posso ajudar com informacoes publicas da escola, como calendario, matricula, documentos exigidos e regras de atendimento digital. Se quiser, pergunte por exemplo: "quais documentos preciso para a matricula?" ou "quando acontece a reuniao de pais?".
- `llamaindex`: status 200, latency 204.6ms, keyword pass `True`, quality `100`, reason `llamaindex_public_profile`
  answer: Colegio Horizonte: Escola laica com Ensino Fundamental II e Ensino Medio, acompanhamento tutorial e trilhas academicas no contraturno.
- `specialist_supervisor`: status 200, latency 16.6ms, keyword pass `True`, quality `90`, reason `specialist_supervisor_llm_unconfigured`
  errors: repetitive_reply
  answer: O caminho specialist_supervisor ainda nao esta com um provider LLM configurado neste ambiente.

### Agora cancela, por favor.

- Slice: `workflow`
- Thread: `system_bank:workflow_protocolos_visitas_e_handoff:Q073` turn `5`
- `langgraph`: status 200, latency 191.6ms, keyword pass `True`, quality `100`, reason `workflow_follow_up_rescue:visit_update`
  answer: Nao consegui atualizar a visita agora. Se quiser, me passe novamente o protocolo da visita ou o novo horario desejado.
- `crewai`: status 200, latency 247.2ms, keyword pass `True`, quality `100`, reason `crewai_llm_not_configured`
  answer: Nao consegui concluir essa resposta agora pelo caminho principal configurado. Tente reformular em uma frase mais direta ou repetir em instantes.
- `python_functions`: status 200, latency 271.9ms, keyword pass `True`, quality `100`, reason `consulta publica de navegacao e canais foi resgatada do dominio support`
  answer: Nao consegui atualizar a visita agora. Se quiser, me passe novamente o protocolo da visita ou o novo horario desejado.
- `llamaindex`: status 200, latency 197.6ms, keyword pass `True`, quality `90`, reason `llamaindex_public_profile`
  errors: repetitive_reply
  answer: Colegio Horizonte: Escola laica com Ensino Fundamental II e Ensino Medio, acompanhamento tutorial e trilhas academicas no contraturno.
- `specialist_supervisor`: status 200, latency 19.3ms, keyword pass `True`, quality `90`, reason `specialist_supervisor_llm_unconfigured`
  errors: repetitive_reply
  answer: O caminho specialist_supervisor ainda nao esta com um provider LLM configurado neste ambiente.

### Preciso emitir documentos finais e concluir a transferencia do Diego.

- Slice: `workflow`
- Thread: `system_bank:workflow_protocolos_visitas_e_handoff:Q078` turn `1`
- `langgraph`: status 200, latency 130.3ms, keyword pass `True`, quality `100`, reason `status administrativo autenticado exige service deterministico`
  answer: Hoje os documentos exigidos para a matricula publicados pela escola sao:
- Formulario cadastral preenchido
- Documento de identificacao do aluno
- CPF do aluno, quando houver
- Historico escolar
- Comprovante de residencia atualizado
- Documento de identificacao do responsavel legal
Se quiser, eu tambem posso explicar as etapas da matricula ou como funciona o envio inicial desses documentos.
- `crewai`: status 200, latency 203.4ms, keyword pass `True`, quality `100`, reason `protected_shadow_needs_student_clarification`
  answer: Posso te ajudar com Lucas Oliveira, Ana Oliveira. Me diga qual aluno voce quer consultar.
- `python_functions`: status 200, latency 116.4ms, keyword pass `True`, quality `100`, reason `python_functions_native_structured:institution`
  answer: Hoje os documentos exigidos para a matricula publicados pela escola sao:
- Formulario cadastral preenchido
- Documento de identificacao do aluno
- CPF do aluno, quando houver
- Historico escolar
- Comprovante de residencia atualizado
- Documento de identificacao do responsavel legal
Se quiser, eu tambem posso explicar as etapas da matricula ou como funciona o envio inicial desses documentos.
- `llamaindex`: status 200, latency 121.4ms, keyword pass `True`, quality `100`, reason `status administrativo autenticado exige service deterministico`
  answer: Hoje os documentos exigidos para a matricula publicados pela escola sao:
- Formulario cadastral preenchido
- Documento de identificacao do aluno
- CPF do aluno, quando houver
- Historico escolar
- Comprovante de residencia atualizado
- Documento de identificacao do responsavel legal
Se quiser, eu tambem posso explicar as etapas da matricula ou como funciona o envio inicial desses documentos.
- `specialist_supervisor`: status 200, latency 17.8ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_llm_unconfigured`
  answer: O caminho specialist_supervisor ainda nao esta com um provider LLM configurado neste ambiente.

### Quero abrir um atendimento com o financeiro para negociar uma mensalidade parcialmente paga.

- Slice: `workflow`
- Thread: `system_bank:workflow_protocolos_visitas_e_handoff:Q079` turn `1`
- `langgraph`: status 200, latency 260.4ms, keyword pass `True`, quality `100`, reason `o turno atual trouxe pistas explicitas de outro dominio protegido e o roteamento foi corrigido`
  answer: Resumo financeiro das contas vinculadas:
- Total de faturas em aberto: 3
- Total de faturas vencidas: 0
- Lucas Oliveira: 1 em aberto, 0 vencidas
  2026-01: vencimento 2026-01-10, status paga, valor 1450.00
  2026-02: vencimento 2026-02-10, status paga, valor 1450.00
- Ana Oliveira: 2 em aberto, 0 vencidas
  2026-01: vencimento 2026-01-10, status paga, valor 1450.00
  2026-02: vencimento 2026-02-10, status paga, valor 1450.00
- `crewai`: status 200, latency 215.3ms, keyword pass `True`, quality `100`, reason `protected_shadow_needs_student_clarification`
  answer: Posso te ajudar com Lucas Oliveira, Ana Oliveira. Me diga qual aluno voce quer consultar.
- `python_functions`: status 200, latency 161.8ms, keyword pass `True`, quality `100`, reason `python_functions_native_structured:institution`
  answer: Valores publicos de referencia para 2026:
- Ensino Fundamental II (Manha): mensalidade R$ 1.280,00 e taxa de matricula R$ 350,00. Valor comercial publico de referencia para 2026. Material didatico e uniforme sao cobrados a parte.
- Ensino Medio (Manha): mensalidade R$ 1.450,00 e taxa de matricula R$ 350,00. Valor comercial publico de referencia para 2026. Ha politica comercial para irmaos e pagamento pontual.
- Periodo integral opcional (Complemento contraturno): mensalidade R$ 480,00 e taxa de matricula R$ 0,00. Adicional mensal aplicado ao estudante matriculado no turno regular que aderir ao periodo integral.
Se quiser, eu tambem posso resumir bolsas, descontos comerciais e canais de matricula.
- `llamaindex`: status 200, latency 169.1ms, keyword pass `True`, quality `100`, reason `llamaindex_public_profile`
  answer: Valores publicos de referencia para 2026:
- Ensino Fundamental II (Manha): mensalidade R$ 1.280,00 e taxa de matricula R$ 350,00. Valor comercial publico de referencia para 2026. Material didatico e uniforme sao cobrados a parte.
- Ensino Medio (Manha): mensalidade R$ 1.450,00 e taxa de matricula R$ 350,00. Valor comercial publico de referencia para 2026. Ha politica comercial para irmaos e pagamento pontual.
- Periodo integral opcional (Complemento contraturno): mensalidade R$ 480,00 e taxa de matricula R$ 0,00. Adicional mensal aplicado ao estudante matriculado no turno regular que aderir ao periodo integral.
Se quiser, eu tambem posso resumir bolsas, descontos comerciais e canais de matricula.
- `specialist_supervisor`: status 200, latency 17.5ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_llm_unconfigured`
  answer: O caminho specialist_supervisor ainda nao esta com um provider LLM configurado neste ambiente.

### Qual a diferenca entre abrir um protocolo, um chamado e um handoff humano?

- Slice: `workflow`
- Thread: `system_bank:workflow_protocolos_visitas_e_handoff:Q080` turn `1`
- `langgraph`: status 200, latency 182.7ms, keyword pass `True`, quality `100`, reason `o usuario demonstrou necessidade de atendimento humano ou operacional`
  answer: Encaminhei sua solicitacao para a fila de atendimento. Protocolo: ATD-20260401-35BABF8E. Status atual: queued. A equipe humana pode continuar esse atendimento no portal operacional.
- `crewai`: status 200, latency 263.6ms, keyword pass `True`, quality `100`, reason `support_handoff_created`
  answer: Encaminhei sua solicitacao para a fila de atendimento. Protocolo: ATD-20260401-78CCBA43. Status atual: queued. A equipe humana podera continuar esse atendimento no portal operacional.
- `python_functions`: status 200, latency 177.6ms, keyword pass `True`, quality `100`, reason `o usuario demonstrou necessidade de atendimento humano ou operacional`
  answer: Encaminhei sua solicitacao para a fila de atendimento. Protocolo: ATD-20260401-22376F14. Status atual: queued. A equipe humana pode continuar esse atendimento no portal operacional.
- `llamaindex`: status 200, latency 205.3ms, keyword pass `True`, quality `100`, reason `o usuario demonstrou necessidade de atendimento humano ou operacional`
  answer: Encaminhei sua solicitacao para a fila de atendimento. Protocolo: ATD-20260401-14D2E9BD. Status atual: queued. A equipe humana pode continuar esse atendimento no portal operacional.
- `specialist_supervisor`: status 200, latency 18.3ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_llm_unconfigured`
  answer: O caminho specialist_supervisor ainda nao esta com um provider LLM configurado neste ambiente.

