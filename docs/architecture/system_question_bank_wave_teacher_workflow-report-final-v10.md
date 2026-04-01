# Five-Path Chatbot Comparison Report

Date: 2026-04-01T22:50:47.712179+00:00

Dataset: `/home/edann/projects/eduassist-platform/tests/evals/datasets/system_question_bank_wave_teacher_workflow.json`

Run prefix: `debug:five-path:20260401T224906Z`

Stack execution mode: `sequential`

## Benchmark Context

- specialist benchmark mode: `source`
- api-core: `http://127.0.0.1:8001`
- ai-orchestrator: `http://127.0.0.1:8002`
- crewai pilot: `http://127.0.0.1:8004`
- specialist pilot: `http://127.0.0.1:8005`

## Stack Summary

| Stack | OK | Keyword pass | Quality | Avg latency |
| --- | --- | --- | --- | --- |
| `langgraph` | `16/16` | `16/16` | `100.0` | `673.6 ms` |
| `crewai` | `16/16` | `16/16` | `100.0` | `3467.2 ms` |
| `python_functions` | `16/16` | `16/16` | `100.0` | `179.2 ms` |
| `llamaindex` | `16/16` | `16/16` | `100.0` | `1710.7 ms` |
| `specialist_supervisor` | `16/16` | `16/16` | `100.0` | `231.4 ms` |

## By Slice

- `protected`
  - `langgraph`: ok 7/7, keyword pass 7/7, quality 100.0, latency 611.2ms
  - `crewai`: ok 7/7, keyword pass 7/7, quality 100.0, latency 5263.4ms
  - `python_functions`: ok 7/7, keyword pass 7/7, quality 100.0, latency 162.0ms
  - `llamaindex`: ok 7/7, keyword pass 7/7, quality 100.0, latency 177.4ms
  - `specialist_supervisor`: ok 7/7, keyword pass 7/7, quality 100.0, latency 375.7ms
- `public`
  - `langgraph`: ok 1/1, keyword pass 1/1, quality 100.0, latency 3500.2ms
  - `crewai`: ok 1/1, keyword pass 1/1, quality 100.0, latency 170.6ms
  - `python_functions`: ok 1/1, keyword pass 1/1, quality 100.0, latency 187.4ms
  - `llamaindex`: ok 1/1, keyword pass 1/1, quality 100.0, latency 8182.0ms
  - `specialist_supervisor`: ok 1/1, keyword pass 1/1, quality 100.0, latency 100.1ms
- `workflow`
  - `langgraph`: ok 8/8, keyword pass 8/8, quality 100.0, latency 374.9ms
  - `crewai`: ok 8/8, keyword pass 8/8, quality 100.0, latency 2307.6ms
  - `python_functions`: ok 8/8, keyword pass 8/8, quality 100.0, latency 193.3ms
  - `llamaindex`: ok 8/8, keyword pass 8/8, quality 100.0, latency 2243.5ms
  - `specialist_supervisor`: ok 8/8, keyword pass 8/8, quality 100.0, latency 121.5ms

## Error Types

- `langgraph`: nenhum
- `crewai`: nenhum
- `python_functions`: nenhum
- `llamaindex`: nenhum
- `specialist_supervisor`: nenhum

## Prompt Results

### Quais turmas e disciplinas eu tenho neste ano?

- Slice: `protected`
- Thread: `system_bank:professor_e_grade_docente:Q065` turn `1`
- `langgraph`: status 200, latency 289.4ms, keyword pass `True`, quality `100`, reason `teacher_role_rescue`
  answer: Grade docente de Fernando Azevedo:
- 1o Ano A - Fisica (2026)
- 1o Ano A - Quimica (2026)
- 1o Ano B - Filosofia (2026)
- 1o Ano B - Historia (2026)
- 2o Ano A - Filosofia (2026)
- 2o Ano A - Fisica (2026)
- 2o Ano A - Quimica (2026)
- 2o Ano B - Filosofia (2026)
- `crewai`: status 200, latency 16033.3ms, keyword pass `True`, quality `100`, reason `crewai_protected_flow_completed`
  answer: Para qual aluno você gostaria de saber as turmas e disciplinas?
- `python_functions`: status 200, latency 163.1ms, keyword pass `True`, quality `100`, reason `python_functions_native_teacher_schedule`
  answer: Grade docente de Fernando Azevedo:
- 1o Ano A - Fisica (2026)
- 1o Ano A - Quimica (2026)
- 1o Ano B - Filosofia (2026)
- 1o Ano B - Historia (2026)
- 2o Ano A - Filosofia (2026)
- 2o Ano A - Fisica (2026)
- 2o Ano A - Quimica (2026)
- 2o Ano B - Filosofia (2026)
- `llamaindex`: status 200, latency 191.4ms, keyword pass `True`, quality `100`, reason `dados estruturados devem passar por service deterministico`
  answer: Grade docente de Fernando Azevedo:
- 1o Ano A - Fisica (2026)
- 1o Ano A - Quimica (2026)
- 1o Ano B - Filosofia (2026)
- 1o Ano B - Historia (2026)
- 2o Ano A - Filosofia (2026)
- 2o Ano A - Fisica (2026)
- 2o Ano A - Quimica (2026)
- 2o Ano B - Filosofia (2026)
- `specialist_supervisor`: status 200, latency 1767.9ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_fast_path:teacher_schedule`
  answer: Grade docente de Fernando Azevedo:
- 1o Ano A - Fisica (2026)
- 1o Ano A - Quimica (2026)
- 1o Ano B - Filosofia (2026)
- 1o Ano B - Historia (2026)
- 2o Ano A - Filosofia (2026)
- 2o Ano A - Fisica (2026)
- 2o Ano A - Quimica (2026)
- 2o Ano B - Filosofia (2026)

### Qual e a minha grade docente completa?

- Slice: `protected`
- Thread: `system_bank:professor_e_grade_docente:Q066` turn `1`
- `langgraph`: status 200, latency 174.2ms, keyword pass `True`, quality `100`, reason `teacher_role_rescue`
  answer: Grade docente de Fernando Azevedo:
- 1o Ano A - Fisica (2026)
- 1o Ano A - Quimica (2026)
- 1o Ano B - Filosofia (2026)
- 1o Ano B - Historia (2026)
- 2o Ano A - Filosofia (2026)
- 2o Ano A - Fisica (2026)
- 2o Ano A - Quimica (2026)
- 2o Ano B - Filosofia (2026)
- `crewai`: status 200, latency 159.4ms, keyword pass `True`, quality `100`, reason `crewai_protected_teacher_scope_preflow`
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
- `python_functions`: status 200, latency 190.5ms, keyword pass `True`, quality `100`, reason `python_functions_native_teacher_schedule`
  answer: Grade docente de Fernando Azevedo:
- 1o Ano A - Fisica (2026)
- 1o Ano A - Quimica (2026)
- 1o Ano B - Filosofia (2026)
- 1o Ano B - Historia (2026)
- 2o Ano A - Filosofia (2026)
- 2o Ano A - Fisica (2026)
- 2o Ano A - Quimica (2026)
- 2o Ano B - Filosofia (2026)
- `llamaindex`: status 200, latency 191.4ms, keyword pass `True`, quality `100`, reason `llamaindex_teacher_schedule_direct`
  answer: Grade docente de Fernando Azevedo:
- 1o Ano A - Fisica (2026)
- 1o Ano A - Quimica (2026)
- 1o Ano B - Filosofia (2026)
- 1o Ano B - Historia (2026)
- 2o Ano A - Filosofia (2026)
- 2o Ano A - Fisica (2026)
- 2o Ano A - Quimica (2026)
- 2o Ano B - Filosofia (2026)
- `specialist_supervisor`: status 200, latency 146.1ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_fast_path:teacher_schedule`
  answer: Grade docente de Fernando Azevedo:
- 1o Ano A - Fisica (2026)
- 1o Ano A - Quimica (2026)
- 1o Ano B - Filosofia (2026)
- 1o Ano B - Historia (2026)
- 2o Ano A - Filosofia (2026)
- 2o Ano A - Fisica (2026)
- 2o Ano A - Quimica (2026)
- 2o Ano B - Filosofia (2026)

### E so do ensino medio?

- Slice: `protected`
- Thread: `system_bank:professor_e_grade_docente:Q066` turn `2`
- `langgraph`: status 200, latency 187.2ms, keyword pass `True`, quality `100`, reason `teacher_role_rescue`
  answer: Nao. Sua grade atual nao e so do Ensino Medio.
- `crewai`: status 200, latency 177.4ms, keyword pass `True`, quality `100`, reason `crewai_protected_teacher_scope_preflow`
  answer: Nao. Sua grade atual nao e so do Ensino Medio.
- `python_functions`: status 200, latency 185.4ms, keyword pass `True`, quality `100`, reason `python_functions_native_teacher_schedule`
  answer: Nao. Sua grade atual nao e so do Ensino Medio.
- `llamaindex`: status 200, latency 201.7ms, keyword pass `True`, quality `100`, reason `llamaindex_teacher_schedule_direct`
  answer: Nao. Sua grade atual nao e so do Ensino Medio.
- `specialist_supervisor`: status 200, latency 164.0ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_fast_path:teacher_schedule`
  answer: Nao. Sua grade atual nao e so do Ensino Medio.

### Quais turmas eu atendo em Filosofia e em que classes?

- Slice: `protected`
- Thread: `system_bank:professor_e_grade_docente:Q068` turn `1`
- `langgraph`: status 200, latency 149.3ms, keyword pass `True`, quality `100`, reason `teacher_role_rescue`
  answer: Turmas de Fernando Azevedo:
- 1o Ano B
- 2o Ano A
- 2o Ano B
- 3o Ano A
- `crewai`: status 200, latency 19923.7ms, keyword pass `True`, quality `100`, reason `crewai_protected_flow_completed`
  answer: Não consigo encontrar informações sobre as turmas que você atende em Filosofia, pois os documentos disponíveis são sobre o resumo acadêmico e frequência de alunos, e não contêm dados sobre a grade de aulas de professores. Você gostaria de saber algo sobre um aluno específico?
- `python_functions`: status 200, latency 158.7ms, keyword pass `True`, quality `100`, reason `python_functions_native_teacher_schedule`
  answer: Turmas de Fernando Azevedo:
- 1o Ano B
- 2o Ano A
- 2o Ano B
- 3o Ano A
- `llamaindex`: status 200, latency 182.9ms, keyword pass `True`, quality `100`, reason `dados estruturados devem passar por service deterministico`
  answer: Turmas de Fernando Azevedo:
- 1o Ano B
- 2o Ano A
- 2o Ano B
- 3o Ano A
- `specialist_supervisor`: status 200, latency 150.4ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_fast_path:teacher_schedule`
  answer: Turmas de Fernando Azevedo:
- 1o Ano A
- 1o Ano B
- 2o Ano A
- 2o Ano B
- 3o Ano A
- 3o Ano B
- 6o Ano B
- 7o Ano B
- 8o Ano B
- 9o Ano B

### Resuma minha rotina docente junto com orientacoes publicas sobre calendario e comunicacao escolar.

- Slice: `protected`
- Thread: `system_bank:professor_e_grade_docente:Q069` turn `1`
- `langgraph`: status 200, latency 1426.7ms, keyword pass `True`, quality `100`, reason `teacher_role_rescue`
  answer: Resumo docente de Fernando Azevedo: 10 turma(s) e 6 disciplina(s) ativas nesta base. Disciplinas: Fisica, Quimica, Filosofia, Historia. Turmas: 1o Ano A, 1o Ano B, 2o Ano A, 2o Ano B. Para comunicacao escolar geral, a secretaria e o canal institucional mais seguro; para alinhamentos pedagogicos, siga com coordenacao e orientacao conforme o assunto.
- `crewai`: status 200, latency 158.5ms, keyword pass `True`, quality `100`, reason `crewai_protected_teacher_scope_preflow`
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
- `python_functions`: status 200, latency 168.9ms, keyword pass `True`, quality `100`, reason `python_functions_native_teacher_schedule`
  answer: Resumo docente de Fernando Azevedo: 10 turma(s) e 6 disciplina(s) ativas nesta base. Disciplinas: Fisica, Quimica, Filosofia, Historia. Turmas: 1o Ano A, 1o Ano B, 2o Ano A, 2o Ano B. Para comunicacao escolar geral, a secretaria e o canal institucional mais seguro; para alinhamentos pedagogicos, siga com coordenacao e orientacao conforme o assunto.
- `llamaindex`: status 200, latency 176.7ms, keyword pass `True`, quality `100`, reason `llamaindex_teacher_schedule_direct`
  answer: Resumo docente de Fernando Azevedo: 10 turma(s) e 6 disciplina(s) ativas nesta base. Disciplinas: Fisica, Quimica, Filosofia, Historia. Turmas: 1o Ano A, 1o Ano B, 2o Ano A, 2o Ano B. Para comunicacao escolar geral, a secretaria e o canal institucional mais seguro; para alinhamentos pedagogicos, siga com coordenacao e orientacao conforme o assunto.
- `specialist_supervisor`: status 200, latency 150.8ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_fast_path:teacher_schedule`
  answer: Resumo docente de Fernando Azevedo: 10 turma(s) e 6 disciplina(s) ativas nesta base. Disciplinas: Fisica, Quimica, Filosofia, Historia. Turmas: 1o Ano A, 1o Ano B, 2o Ano A, 2o Ano B. Para comunicacao escolar geral, a secretaria e o canal institucional mais seguro; para alinhamentos pedagogicos, siga com coordenacao e orientacao conforme o assunto.

### Sou professor de Filosofia e quero trabalhar ai; como faco para entrar em contato?

- Slice: `public`
- Thread: `system_bank:professor_e_grade_docente:Q070` turn `1`
- `langgraph`: status 200, latency 3500.2ms, keyword pass `True`, quality `100`, reason `fato institucional canonico deve vir de fonte estruturada`
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
- `crewai`: status 200, latency 170.6ms, keyword pass `True`, quality `100`, reason `crewai_public_fast_path`
  answer: Secretaria (telefone): (11) 3333-4200
- `python_functions`: status 200, latency 187.4ms, keyword pass `True`, quality `100`, reason `python_functions_native_structured:institution`
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
- `llamaindex`: status 200, latency 8182.0ms, keyword pass `True`, quality `100`, reason `llamaindex_public_profile`
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
- `specialist_supervisor`: status 200, latency 100.1ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_fast_path:service_routing`
  answer: Hoje estes sao os responsaveis e canais mais diretos por assunto:
- Carreiras docentes: email talentos@colegiohorizonte.edu.br.

### Me diga o nome e o telefone do professor de Educacao Fisica.

- Slice: `protected`
- Thread: `system_bank:professor_e_grade_docente:Q071` turn `1`
- `langgraph`: status 200, latency 136.4ms, keyword pass `True`, quality `100`, reason `status administrativo autenticado exige service deterministico`
  answer: Essa consulta depende de autenticacao e vinculo da sua conta no Telegram. Use o portal da escola para gerar o codigo de vinculacao e depois envie o comando `/start link_<codigo>` ao bot.
- `crewai`: status 200, latency 218.2ms, keyword pass `True`, quality `100`, reason `crewai_protected_auth_required`
  answer: Essa consulta depende de autenticacao e vinculo da sua conta no Telegram. Use o portal da escola para gerar o codigo de vinculacao e depois envie o comando /start link_<codigo> ao bot.
- `python_functions`: status 200, latency 146.6ms, keyword pass `True`, quality `100`, reason `python_functions_native_structured:institution`
  answer: Essa consulta depende de autenticacao e vinculo da sua conta no Telegram. Use o portal da escola para gerar o codigo de vinculacao e depois envie o comando `/start link_<codigo>` ao bot.
- `llamaindex`: status 200, latency 156.8ms, keyword pass `True`, quality `100`, reason `status administrativo autenticado exige service deterministico`
  answer: Essa consulta depende de autenticacao e vinculo da sua conta no Telegram. Use o portal da escola para gerar o codigo de vinculacao e depois envie o comando `/start link_<codigo>` ao bot.
- `specialist_supervisor`: status 200, latency 110.7ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_fast_path:teacher_directory`
  answer: O Colegio Horizonte nao divulga nomes nem contatos diretos de professores por disciplina, como educacao fisica. Se quiser, eu posso te indicar a coordenacao pedagogica ou o setor certo para seguir com isso.

### Gere um resumo enxuto da minha alocacao para eu revisar antes da reuniao pedagogica.

- Slice: `protected`
- Thread: `system_bank:professor_e_grade_docente:Q072` turn `1`
- `langgraph`: status 200, latency 1915.3ms, keyword pass `True`, quality `100`, reason `teacher_role_rescue`
  answer: Voce esta falando aqui como Fernando Azevedo, no perfil de professor do Colegio Horizonte. No Telegram, nesta etapa eu consigo consultar sua grade docente, turmas e disciplinas. A situacao individual dos alunos ainda nao esta liberada por este canal. Se quiser, me pergunte "qual meu horario?", "quais sao minhas turmas?" ou "quais disciplinas eu ministro?".
- `crewai`: status 200, latency 173.4ms, keyword pass `True`, quality `100`, reason `crewai_public_fast_path`
  answer: A proposta pedagogica publicada hoje combina A escola segue a BNCC e o curriculo do Ensino Medio articulado com projeto de vida, producao textual, cultura digital e aprofundamento academico progressivo. Na pratica, isso aparece em frentes como Tutoria academica e projeto de vida, Espaco Maker integrado ao curriculo, Acolhimento estruturado para familias e estudantes.
- `python_functions`: status 200, latency 121.0ms, keyword pass `True`, quality `100`, reason `python_functions_native_teacher_scope_guidance`
  answer: Voce esta falando aqui como Fernando Azevedo, no perfil de professor do Colegio Horizonte. No Telegram, nesta etapa eu consigo consultar sua grade docente, turmas e disciplinas. A situacao individual dos alunos ainda nao esta liberada por este canal. Se quiser, me pergunte "qual meu horario?", "quais sao minhas turmas?" ou "quais disciplinas eu ministro?".
- `llamaindex`: status 200, latency 140.9ms, keyword pass `True`, quality `100`, reason `llamaindex_teacher_scope_guidance`
  answer: Voce esta falando aqui como Fernando Azevedo, no perfil de professor do Colegio Horizonte. No Telegram, nesta etapa eu consigo consultar sua grade docente, turmas e disciplinas. A situacao individual dos alunos ainda nao esta liberada por este canal. Se quiser, me pergunte "qual meu horario?", "quais sao minhas turmas?" ou "quais disciplinas eu ministro?".
- `specialist_supervisor`: status 200, latency 139.7ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_fast_path:teacher_schedule`
  answer: Resumo docente de Fernando Azevedo: 10 turma(s) e 6 disciplina(s) ativas nesta base. Disciplinas: Fisica, Quimica, Filosofia, Historia. Turmas: 1o Ano A, 1o Ano B, 2o Ano A, 2o Ano B. Para comunicacao escolar geral, a secretaria e o canal institucional mais seguro; para alinhamentos pedagogicos, siga com coordenacao e orientacao conforme o assunto.

### Quero agendar uma visita para conhecer a escola.

- Slice: `workflow`
- Thread: `system_bank:workflow_protocolos_visitas_e_handoff:Q073` turn `1`
- `langgraph`: status 200, latency 180.1ms, keyword pass `True`, quality `100`, reason `consulta publica de navegacao e canais foi resgatada do dominio support`
  answer: Pedido de visita registrado para o Colegio Horizonte. Protocolo: VIS-20260401-B810A1. Preferencia informada: janela a confirmar. Fila responsavel: admissoes. Ticket operacional: ATD-20260401-A9586DD1. A equipe comercial valida a janela e retorna com a confirmacao.
- `crewai`: status 200, latency 225.0ms, keyword pass `True`, quality `100`, reason `workflow_visit_create`
  answer: Pedido de visita registrado para o Colegio Horizonte. Protocolo: VIS-20260401-883511. Preferencia informada: janela a confirmar. Fila responsavel: admissoes. Ticket operacional: ATD-20260401-F4FB823A. A equipe comercial valida a janela e retorna com a confirmacao.
- `python_functions`: status 200, latency 197.7ms, keyword pass `True`, quality `100`, reason `python_functions_native_structured:support`
  answer: Pedido de visita registrado para o Colegio Horizonte. Protocolo: VIS-20260401-FEFF46. Preferencia informada: janela a confirmar. Fila responsavel: admissoes. Ticket operacional: ATD-20260401-53027937. A equipe comercial valida a janela e retorna com a confirmacao.
- `llamaindex`: status 200, latency 194.0ms, keyword pass `True`, quality `100`, reason `consulta publica de navegacao e canais foi resgatada do dominio support`
  answer: Pedido de visita registrado para o Colegio Horizonte. Protocolo: VIS-20260401-BCDFB5. Preferencia informada: janela a confirmar. Fila responsavel: admissoes. Ticket operacional: ATD-20260401-2A699EA1. A equipe comercial valida a janela e retorna com a confirmacao.
- `specialist_supervisor`: status 200, latency 157.0ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_tool_first:visit_booking`
  answer: Pedido de visita registrado. Protocolo: VIS-20260401-5AA40A. Preferencia registrada: janela a confirmar. Ticket operacional: ATD-20260401-85A18098. Se quiser, eu tambem posso acompanhar o status ou remarcar a visita.

### Pode ser na quinta a tarde?

- Slice: `workflow`
- Thread: `system_bank:workflow_protocolos_visitas_e_handoff:Q073` turn `2`
- `langgraph`: status 200, latency 194.2ms, keyword pass `True`, quality `100`, reason `workflow_follow_up_rescue:visit_update`
  answer: Pedido de visita atualizado com a fila de admissions. Protocolo: VIS-20260401-B810A1. Ticket operacional: ATD-20260401-A9586DD1. Nova preferencia: quinta-feira - tarde (02/04/2026 - 14:30). Admissions valida a nova janela e retorna com a confirmacao.
- `crewai`: status 200, latency 217.3ms, keyword pass `True`, quality `100`, reason `workflow_visit_reschedule`
  answer: Pedido de visita atualizado com a fila de admissoes. - Protocolo: VIS-20260401-883511 - Ticket operacional: ATD-20260401-F4FB823A - Nova preferencia: quinta-feira - tarde (02/04/2026 - 14:30) Proximo passo: admissions valida a nova janela e retorna com a confirmacao.
- `python_functions`: status 200, latency 250.5ms, keyword pass `True`, quality `100`, reason `consulta publica de navegacao e canais foi resgatada do dominio support`
  answer: Pedido de visita atualizado com a fila de admissions. Protocolo: VIS-20260401-FEFF46. Ticket operacional: ATD-20260401-53027937. Nova preferencia: quinta-feira - tarde (02/04/2026 - 14:30). Admissions valida a nova janela e retorna com a confirmacao.
- `llamaindex`: status 200, latency 254.1ms, keyword pass `True`, quality `100`, reason `consulta publica de navegacao e canais foi resgatada do dominio support`
  answer: Pedido de visita atualizado com a fila de admissions. Protocolo: VIS-20260401-BCDFB5. Ticket operacional: ATD-20260401-2A699EA1. Nova preferencia: quinta-feira - tarde (02/04/2026 - 14:30). Admissions valida a nova janela e retorna com a confirmacao.
- `specialist_supervisor`: status 200, latency 107.1ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_tool_first:visit_reschedule`
  answer: Pedido de visita atualizado. Protocolo: VIS-20260401-5AA40A. Nova preferencia: quinta-feira, 14:30. Admissions valida a nova janela e retorna com a confirmacao.

### Qual e o protocolo dessa visita?

- Slice: `workflow`
- Thread: `system_bank:workflow_protocolos_visitas_e_handoff:Q073` turn `3`
- `langgraph`: status 200, latency 177.0ms, keyword pass `True`, quality `100`, reason `workflow_follow_up_rescue:visit_update`
  answer: Nao consegui atualizar a visita agora. Se quiser, me passe novamente o protocolo da visita ou o novo horario desejado.
- `crewai`: status 200, latency 256.9ms, keyword pass `True`, quality `100`, reason `workflow_protocol_lookup`
  answer: O protocolo da sua visita e VIS-20260401-883511. - Ticket operacional: ATD-20260401-F4FB823A - Preferencia registrada: quinta-feira - 14:30 (02/04/2026 - 14:30) Se quiser, eu tambem posso te dizer o status, remarcar ou cancelar a visita.
- `python_functions`: status 200, latency 226.9ms, keyword pass `True`, quality `100`, reason `python_functions_native_structured:support`
  answer: Solicitacao institucional registrada para direcao. Protocolo: REQ-20260401-0CCBE9. Assunto: Qual e o protocolo dessa visita? Fila responsavel: direcao. Ticket operacional: ATD-20260401-53027937. A equipe faz a triagem inicial e segue o retorno pelo fluxo institucional.
- `llamaindex`: status 200, latency 222.7ms, keyword pass `True`, quality `100`, reason `consulta publica de navegacao e canais foi resgatada do dominio support`
  answer: Solicitacao institucional registrada para direcao. Protocolo: REQ-20260401-9DD2ED. Assunto: Qual e o protocolo dessa visita? Fila responsavel: direcao. Ticket operacional: ATD-20260401-2A699EA1. A equipe faz a triagem inicial e segue o retorno pelo fluxo institucional.
- `specialist_supervisor`: status 200, latency 125.1ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_tool_first:visit_status`
  answer: Seu pedido de visita segue queued. Protocolo: VIS-20260401-5AA40A. Preferencia registrada: 02/04/2026 - 14:30. Ticket operacional: ATD-20260401-85A18098.

### Preciso remarcar para a semana que vem.

- Slice: `workflow`
- Thread: `system_bank:workflow_protocolos_visitas_e_handoff:Q073` turn `4`
- `langgraph`: status 200, latency 1738.6ms, keyword pass `True`, quality `100`, reason `a intencao esta ambigua e exige clarificacao antes de recuperar contexto`
  answer: Para remarcar sua visita, por favor, me informe o protocolo da visita ou o novo horário desejado. Assim, consigo verificar a disponibilidade e fazer a alteração para você.
- `crewai`: status 200, latency 216.9ms, keyword pass `True`, quality `100`, reason `workflow_visit_reschedule`
  answer: Pedido de visita atualizado com a fila de admissoes. - Protocolo: VIS-20260401-883511 - Ticket operacional: ATD-20260401-F4FB823A - Nova preferencia: quinta-feira - 14:30 (09/04/2026 - 14:30) Proximo passo: admissions valida a nova janela e retorna com a confirmacao.
- `python_functions`: status 200, latency 186.9ms, keyword pass `True`, quality `100`, reason `a intencao esta ambigua e exige clarificacao antes de recuperar contexto`
  answer: Posso ajudar com informacoes publicas da escola, como calendario, matricula, documentos exigidos e regras de atendimento digital. Se quiser, pergunte por exemplo: "quais documentos preciso para a matricula?" ou "quando acontece a reuniao de pais?".
- `llamaindex`: status 200, latency 3745.6ms, keyword pass `True`, quality `100`, reason `llamaindex_public_profile`
  answer: Hoje o Colegio Horizonte publica estas janelas de visita:
- Visita guiada ao campus: terca-feira, das 09:00 as 10:15, em Recepcao principal e circuito pedagogico. Inclui apresentacao institucional, visita aos espacos e conversa curta com admissions.
- Visita guiada com foco pedagogico: quinta-feira, das 14:30 as 15:45, em Recepcao principal e salas de projeto. Janela pensada para familias que desejam conhecer infraestrutura, rotina e proposta pedagogica.
Agendamento: bot, whatsapp comercial ou admissions. Prazo de confirmacao: confirmacao em ate 1 dia util.
- `specialist_supervisor`: status 200, latency 97.4ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_tool_first:visit_reschedule_guidance`
  answer: Para remarcar a visita, eu sigo pelo protocolo VIS-20260401-5AA40A. A preferencia atual registrada e 02/04/2026 - 14:30. Me diga o novo dia ou janela desejada e eu atualizo o pedido. Ticket operacional: ATD-20260401-85A18098.

### Agora cancela, por favor.

- Slice: `workflow`
- Thread: `system_bank:workflow_protocolos_visitas_e_handoff:Q073` turn `5`
- `langgraph`: status 200, latency 170.6ms, keyword pass `True`, quality `100`, reason `workflow_follow_up_rescue:visit_update`
  answer: Nao consegui atualizar a visita agora. Se quiser, me passe novamente o protocolo da visita ou o novo horario desejado.
- `crewai`: status 200, latency 16919.2ms, keyword pass `True`, quality `100`, reason `crewai_public_flow_completed`
  answer: Para te ajudar melhor, o que exatamente você gostaria de cancelar?
- `python_functions`: status 200, latency 251.6ms, keyword pass `True`, quality `100`, reason `consulta publica de navegacao e canais foi resgatada do dominio support`
  answer: Nao consegui atualizar a visita agora. Se quiser, me passe novamente o protocolo da visita ou o novo horario desejado.
- `llamaindex`: status 200, latency 9949.1ms, keyword pass `True`, quality `100`, reason `llamaindex_public_pricing_projection`
  answer: Valores publicos de referencia para 2026:
- Ensino Fundamental II (Manha): mensalidade R$ 1.280,00 e taxa de matricula R$ 350,00. Valor comercial publico de referencia para 2026. Material didatico e uniforme sao cobrados a parte.
- Ensino Medio (Manha): mensalidade R$ 1.450,00 e taxa de matricula R$ 350,00. Valor comercial publico de referencia para 2026. Ha politica comercial para irmaos e pagamento pontual.
- Periodo integral opcional (Complemento contraturno): mensalidade R$ 480,00 e taxa de matricula R$ 0,00. Adicional mensal aplicado ao estudante matriculado no turno regular que aderir ao periodo integral.
Se quiser, eu tambem posso resumir bolsas, descontos comerciais e canais de matricula.
- `specialist_supervisor`: status 200, latency 119.5ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_tool_first:visit_cancel`
  answer: Pedido de visita cancelado. Protocolo: VIS-20260401-5AA40A. Se quiser, eu posso abrir um novo agendamento com outra data.

### Preciso emitir documentos finais e concluir a transferencia do Diego.

- Slice: `workflow`
- Thread: `system_bank:workflow_protocolos_visitas_e_handoff:Q078` turn `1`
- `langgraph`: status 200, latency 119.5ms, keyword pass `True`, quality `100`, reason `status administrativo autenticado exige service deterministico`
  answer: Hoje os documentos exigidos para a matricula publicados pela escola sao:
- Formulario cadastral preenchido
- Documento de identificacao do aluno
- CPF do aluno, quando houver
- Historico escolar
- Comprovante de residencia atualizado
- Documento de identificacao do responsavel legal
Se quiser, eu tambem posso explicar as etapas da matricula ou como funciona o envio inicial desses documentos.
- `crewai`: status 200, latency 182.8ms, keyword pass `True`, quality `100`, reason `protected_shadow_needs_student_clarification`
  answer: Posso te ajudar com Lucas Oliveira, Ana Oliveira. Me diga qual aluno voce quer consultar.
- `python_functions`: status 200, latency 110.5ms, keyword pass `True`, quality `100`, reason `python_functions_native_structured:institution`
  answer: Hoje os documentos exigidos para a matricula publicados pela escola sao:
- Formulario cadastral preenchido
- Documento de identificacao do aluno
- CPF do aluno, quando houver
- Historico escolar
- Comprovante de residencia atualizado
- Documento de identificacao do responsavel legal
Se quiser, eu tambem posso explicar as etapas da matricula ou como funciona o envio inicial desses documentos.
- `llamaindex`: status 200, latency 128.6ms, keyword pass `True`, quality `100`, reason `status administrativo autenticado exige service deterministico`
  answer: Hoje os documentos exigidos para a matricula publicados pela escola sao:
- Formulario cadastral preenchido
- Documento de identificacao do aluno
- CPF do aluno, quando houver
- Historico escolar
- Comprovante de residencia atualizado
- Documento de identificacao do responsavel legal
Se quiser, eu tambem posso explicar as etapas da matricula ou como funciona o envio inicial desses documentos.
- `specialist_supervisor`: status 200, latency 124.3ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_tool_first:human_handoff`
  answer: Encaminhei sua solicitacao para a fila de secretaria. Protocolo: ATD-20260401-5B79D266. Status atual: queued. Se preferir, voce tambem pode seguir pelo WhatsApp oficial (11) 97500-2040.

### Quero abrir um atendimento com o financeiro para negociar uma mensalidade parcialmente paga.

- Slice: `workflow`
- Thread: `system_bank:workflow_protocolos_visitas_e_handoff:Q079` turn `1`
- `langgraph`: status 200, latency 226.8ms, keyword pass `True`, quality `100`, reason `o turno atual trouxe pistas explicitas de outro dominio protegido e o roteamento foi corrigido`
  answer: Resumo financeiro das contas vinculadas:
- Total de faturas em aberto: 3
- Total de faturas vencidas: 0
- Lucas Oliveira: 1 em aberto, 0 vencidas
  2026-01: vencimento 2026-01-10, status paga, valor 1450.00
  2026-02: vencimento 2026-02-10, status paga, valor 1450.00
- Ana Oliveira: 2 em aberto, 0 vencidas
  2026-01: vencimento 2026-01-10, status paga, valor 1450.00
  2026-02: vencimento 2026-02-10, status paga, valor 1450.00
- `crewai`: status 200, latency 197.1ms, keyword pass `True`, quality `100`, reason `protected_shadow_needs_student_clarification`
  answer: Posso te ajudar com Lucas Oliveira, Ana Oliveira. Me diga qual aluno voce quer consultar.
- `python_functions`: status 200, latency 151.9ms, keyword pass `True`, quality `100`, reason `python_functions_native_structured:institution`
  answer: Valores publicos de referencia para 2026:
- Ensino Fundamental II (Manha): mensalidade R$ 1.280,00 e taxa de matricula R$ 350,00. Valor comercial publico de referencia para 2026. Material didatico e uniforme sao cobrados a parte.
- Ensino Medio (Manha): mensalidade R$ 1.450,00 e taxa de matricula R$ 350,00. Valor comercial publico de referencia para 2026. Ha politica comercial para irmaos e pagamento pontual.
- Periodo integral opcional (Complemento contraturno): mensalidade R$ 480,00 e taxa de matricula R$ 0,00. Adicional mensal aplicado ao estudante matriculado no turno regular que aderir ao periodo integral.
Se quiser, eu tambem posso resumir bolsas, descontos comerciais e canais de matricula.
- `llamaindex`: status 200, latency 3264.1ms, keyword pass `True`, quality `100`, reason `llamaindex_public_profile`
  answer: Valores publicos de referencia para 2026:
- Ensino Fundamental II (Manha): mensalidade R$ 1.280,00 e taxa de matricula R$ 350,00. Valor comercial publico de referencia para 2026. Material didatico e uniforme sao cobrados a parte.
- Ensino Medio (Manha): mensalidade R$ 1.450,00 e taxa de matricula R$ 350,00. Valor comercial publico de referencia para 2026. Ha politica comercial para irmaos e pagamento pontual.
- Periodo integral opcional (Complemento contraturno): mensalidade R$ 480,00 e taxa de matricula R$ 0,00. Adicional mensal aplicado ao estudante matriculado no turno regular que aderir ao periodo integral.
Se quiser, eu tambem posso resumir bolsas, descontos comerciais e canais de matricula.
- `specialist_supervisor`: status 200, latency 118.0ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_resolved_intent:finance_student_clarify`
  answer: Consigo verificar a situacao financeira, mas preciso que voce me diga qual aluno: Lucas Oliveira ou Ana Oliveira?

### Qual a diferenca entre abrir um protocolo, um chamado e um handoff humano?

- Slice: `workflow`
- Thread: `system_bank:workflow_protocolos_visitas_e_handoff:Q080` turn `1`
- `langgraph`: status 200, latency 192.8ms, keyword pass `True`, quality `100`, reason `o usuario demonstrou necessidade de atendimento humano ou operacional`
  answer: Encaminhei sua solicitacao para a fila de atendimento. Protocolo: ATD-20260401-F3765B59. Status atual: queued. A equipe humana pode continuar esse atendimento no portal operacional.
- `crewai`: status 200, latency 245.2ms, keyword pass `True`, quality `100`, reason `support_handoff_created`
  answer: Encaminhei sua solicitacao para a fila de atendimento. Protocolo: ATD-20260401-4A67433D. Status atual: queued. A equipe humana podera continuar esse atendimento no portal operacional.
- `python_functions`: status 200, latency 170.3ms, keyword pass `True`, quality `100`, reason `o usuario demonstrou necessidade de atendimento humano ou operacional`
  answer: Encaminhei sua solicitacao para a fila de atendimento. Protocolo: ATD-20260401-7A556DD8. Status atual: queued. A equipe humana pode continuar esse atendimento no portal operacional.
- `llamaindex`: status 200, latency 189.7ms, keyword pass `True`, quality `100`, reason `o usuario demonstrou necessidade de atendimento humano ou operacional`
  answer: Encaminhei sua solicitacao para a fila de atendimento. Protocolo: ATD-20260401-3043954B. Status atual: queued. A equipe humana pode continuar esse atendimento no portal operacional.
- `specialist_supervisor`: status 200, latency 123.6ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_fast_path:support_process_boundary`
  answer: Hoje eu trato esses tres fluxos de forma diferente: protocolo registra uma solicitacao institucional rastreavel; chamado costuma ser o ticket operacional associado ao atendimento; e handoff humano e o encaminhamento real para uma fila ou equipe, normalmente com protocolo e status para acompanhamento.

