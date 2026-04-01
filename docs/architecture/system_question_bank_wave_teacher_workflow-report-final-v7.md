# Five-Path Chatbot Comparison Report

Date: 2026-04-01T20:29:31.491966+00:00

Dataset: `/home/edann/projects/eduassist-platform/tests/evals/datasets/system_question_bank_wave_teacher_workflow.json`

Run prefix: `debug:five-path:20260401T202644Z`

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
| `langgraph` | `16/16` | `16/16` | `99.4` | `703.3 ms` |
| `crewai` | `16/16` | `16/16` | `99.4` | `3065.4 ms` |
| `python_functions` | `16/16` | `16/16` | `100.0` | `160.2 ms` |
| `llamaindex` | `16/16` | `16/16` | `100.0` | `1679.7 ms` |
| `specialist_supervisor` | `16/16` | `16/16` | `100.0` | `4753.5 ms` |

## By Slice

- `protected`
  - `langgraph`: ok 7/7, keyword pass 7/7, quality 98.6, latency 657.2ms
  - `crewai`: ok 7/7, keyword pass 7/7, quality 98.6, latency 4928.6ms
  - `python_functions`: ok 7/7, keyword pass 7/7, quality 100.0, latency 148.8ms
  - `llamaindex`: ok 7/7, keyword pass 7/7, quality 100.0, latency 158.3ms
  - `specialist_supervisor`: ok 7/7, keyword pass 7/7, quality 100.0, latency 5458.9ms
- `public`
  - `langgraph`: ok 1/1, keyword pass 1/1, quality 100.0, latency 3793.6ms
  - `crewai`: ok 1/1, keyword pass 1/1, quality 100.0, latency 163.7ms
  - `python_functions`: ok 1/1, keyword pass 1/1, quality 100.0, latency 161.2ms
  - `llamaindex`: ok 1/1, keyword pass 1/1, quality 100.0, latency 10307.8ms
  - `specialist_supervisor`: ok 1/1, keyword pass 1/1, quality 100.0, latency 8610.4ms
- `workflow`
  - `langgraph`: ok 8/8, keyword pass 8/8, quality 100.0, latency 357.4ms
  - `crewai`: ok 8/8, keyword pass 8/8, quality 100.0, latency 1797.9ms
  - `python_functions`: ok 8/8, keyword pass 8/8, quality 100.0, latency 170.1ms
  - `llamaindex`: ok 8/8, keyword pass 8/8, quality 100.0, latency 1932.5ms
  - `specialist_supervisor`: ok 8/8, keyword pass 8/8, quality 100.0, latency 3654.1ms

## Error Types

- `langgraph`: repetitive_reply=1
- `crewai`: repetitive_reply=1
- `python_functions`: nenhum
- `llamaindex`: nenhum
- `specialist_supervisor`: nenhum

## Prompt Results

### Quais turmas e disciplinas eu tenho neste ano?

- Slice: `protected`
- Thread: `system_bank:professor_e_grade_docente:Q065` turn `1`
- `langgraph`: status 200, latency 223.7ms, keyword pass `True`, quality `100`, reason `teacher_role_rescue`
  answer: Voce esta falando aqui como Fernando Azevedo, no perfil de professor do Colegio Horizonte. No Telegram, nesta etapa eu consigo consultar sua grade docente, turmas e disciplinas. A situacao individual dos alunos ainda nao esta liberada por este canal. Se quiser, me pergunte "qual meu horario?", "quais sao minhas turmas?" ou "quais disciplinas eu ministro?".
- `crewai`: status 200, latency 13475.3ms, keyword pass `True`, quality `100`, reason `crewai_protected_flow_completed`
  answer: Para qual aluno você gostaria de saber as turmas e disciplinas?
- `python_functions`: status 200, latency 144.4ms, keyword pass `True`, quality `100`, reason `python_functions_native_teacher_schedule`
  answer: Grade docente de Fernando Azevedo:
- 1o Ano A - Fisica (2026)
- 1o Ano A - Quimica (2026)
- 1o Ano B - Filosofia (2026)
- 1o Ano B - Historia (2026)
- 2o Ano A - Filosofia (2026)
- 2o Ano A - Fisica (2026)
- 2o Ano A - Quimica (2026)
- 2o Ano B - Filosofia (2026)
- `llamaindex`: status 200, latency 124.8ms, keyword pass `True`, quality `100`, reason `dados estruturados devem passar por service deterministico`
  answer: Voce esta falando aqui como Fernando Azevedo, no perfil de professor do Colegio Horizonte. No Telegram, nesta etapa eu consigo consultar sua grade docente, turmas e disciplinas. A situacao individual dos alunos ainda nao esta liberada por este canal. Se quiser, me pergunte "qual meu horario?", "quais sao minhas turmas?" ou "quais disciplinas eu ministro?".
- `specialist_supervisor`: status 200, latency 1981.9ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_fast_path:teacher_schedule`
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
- `langgraph`: status 200, latency 112.4ms, keyword pass `True`, quality `100`, reason `teacher_role_rescue`
  answer: Voce esta falando aqui como Fernando Azevedo, no perfil de professor do Colegio Horizonte. No Telegram, nesta etapa eu consigo consultar sua grade docente, turmas e disciplinas. A situacao individual dos alunos ainda nao esta liberada por este canal. Se quiser, me pergunte "qual meu horario?", "quais sao minhas turmas?" ou "quais disciplinas eu ministro?".
- `crewai`: status 200, latency 150.8ms, keyword pass `True`, quality `100`, reason `crewai_protected_teacher_scope_preflow`
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
- `python_functions`: status 200, latency 163.8ms, keyword pass `True`, quality `100`, reason `python_functions_native_teacher_schedule`
  answer: Grade docente de Fernando Azevedo:
- 1o Ano A - Fisica (2026)
- 1o Ano A - Quimica (2026)
- 1o Ano B - Filosofia (2026)
- 1o Ano B - Historia (2026)
- 2o Ano A - Filosofia (2026)
- 2o Ano A - Fisica (2026)
- 2o Ano A - Quimica (2026)
- 2o Ano B - Filosofia (2026)
- `llamaindex`: status 200, latency 207.3ms, keyword pass `True`, quality `100`, reason `llamaindex_teacher_schedule_direct`
  answer: Grade docente de Fernando Azevedo:
- 1o Ano A - Fisica (2026)
- 1o Ano A - Quimica (2026)
- 1o Ano B - Filosofia (2026)
- 1o Ano B - Historia (2026)
- 2o Ano A - Filosofia (2026)
- 2o Ano A - Fisica (2026)
- 2o Ano A - Quimica (2026)
- 2o Ano B - Filosofia (2026)
- `specialist_supervisor`: status 200, latency 2017.5ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_fast_path:teacher_schedule`
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
- `langgraph`: status 200, latency 117.5ms, keyword pass `True`, quality `90`, reason `teacher_role_rescue`
  errors: repetitive_reply
  answer: Voce esta falando aqui como Fernando Azevedo, no perfil de professor do Colegio Horizonte. No Telegram, nesta etapa eu consigo consultar sua grade docente, turmas e disciplinas. A situacao individual dos alunos ainda nao esta liberada por este canal. Se quiser, me pergunte "qual meu horario?", "quais sao minhas turmas?" ou "quais disciplinas eu ministro?".
- `crewai`: status 200, latency 156.3ms, keyword pass `True`, quality `90`, reason `crewai_protected_teacher_scope_preflow`
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
- `python_functions`: status 200, latency 161.0ms, keyword pass `True`, quality `100`, reason `python_functions_native_teacher_schedule`
  answer: Nao. Sua grade atual nao e so do Ensino Medio.
- `llamaindex`: status 200, latency 179.2ms, keyword pass `True`, quality `100`, reason `llamaindex_teacher_schedule_direct`
  answer: Nao. Sua grade atual nao e so do Ensino Medio.
- `specialist_supervisor`: status 200, latency 2093.1ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_fast_path:teacher_schedule`
  answer: Nao. Sua grade atual nao e so do Ensino Medio.

### Quais turmas eu atendo em Filosofia e em que classes?

- Slice: `protected`
- Thread: `system_bank:professor_e_grade_docente:Q068` turn `1`
- `langgraph`: status 200, latency 97.7ms, keyword pass `True`, quality `100`, reason `teacher_role_rescue`
  answer: Voce esta falando aqui como Fernando Azevedo, no perfil de professor do Colegio Horizonte. No Telegram, nesta etapa eu consigo consultar sua grade docente, turmas e disciplinas. A situacao individual dos alunos ainda nao esta liberada por este canal. Se quiser, me pergunte "qual meu horario?", "quais sao minhas turmas?" ou "quais disciplinas eu ministro?".
- `crewai`: status 200, latency 20213.2ms, keyword pass `True`, quality `100`, reason `crewai_protected_flow_timeout`
  answer: Eu nao consegui consolidar essa consulta protegida com seguranca agora. Se quiser, me diga qual aluno e qual dado voce quer consultar.
- `python_functions`: status 200, latency 141.9ms, keyword pass `True`, quality `100`, reason `python_functions_native_teacher_schedule`
  answer: Turmas de Fernando Azevedo:
- 1o Ano B
- 2o Ano A
- 2o Ano B
- 3o Ano A
- `llamaindex`: status 200, latency 127.1ms, keyword pass `True`, quality `100`, reason `dados estruturados devem passar por service deterministico`
  answer: Voce esta falando aqui como Fernando Azevedo, no perfil de professor do Colegio Horizonte. No Telegram, nesta etapa eu consigo consultar sua grade docente, turmas e disciplinas. A situacao individual dos alunos ainda nao esta liberada por este canal. Se quiser, me pergunte "qual meu horario?", "quais sao minhas turmas?" ou "quais disciplinas eu ministro?".
- `specialist_supervisor`: status 200, latency 1947.5ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_fast_path:teacher_schedule`
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
- `langgraph`: status 200, latency 1871.7ms, keyword pass `True`, quality `100`, reason `teacher_role_rescue`
  answer: Voce esta falando aqui como Fernando Azevedo, no perfil de professor do Colegio Horizonte. No Telegram, nesta etapa eu consigo consultar sua grade docente, turmas e disciplinas. A situacao individual dos alunos ainda nao esta liberada por este canal. Se quiser, me pergunte "qual meu horario?", "quais sao minhas turmas?" ou "quais disciplinas eu ministro?".
- `crewai`: status 200, latency 148.2ms, keyword pass `True`, quality `100`, reason `crewai_protected_teacher_scope_preflow`
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
- `python_functions`: status 200, latency 153.2ms, keyword pass `True`, quality `100`, reason `python_functions_native_teacher_schedule`
  answer: Resumo docente de Fernando Azevedo: 10 turma(s) e 6 disciplina(s) ativas nesta base. Disciplinas: Fisica, Quimica, Filosofia, Historia. Turmas: 1o Ano A, 1o Ano B, 2o Ano A, 2o Ano B. Para comunicacao escolar geral, a secretaria e o canal institucional mais seguro; para alinhamentos pedagogicos, siga com coordenacao e orientacao conforme o assunto.
- `llamaindex`: status 200, latency 210.6ms, keyword pass `True`, quality `100`, reason `llamaindex_teacher_schedule_direct`
  answer: Resumo docente de Fernando Azevedo: 10 turma(s) e 6 disciplina(s) ativas nesta base. Disciplinas: Fisica, Quimica, Filosofia, Historia. Turmas: 1o Ano A, 1o Ano B, 2o Ano A, 2o Ano B. Para comunicacao escolar geral, a secretaria e o canal institucional mais seguro; para alinhamentos pedagogicos, siga com coordenacao e orientacao conforme o assunto.
- `specialist_supervisor`: status 200, latency 1968.7ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_fast_path:teacher_schedule`
  answer: Resumo docente de Fernando Azevedo: 10 turma(s) e 6 disciplina(s) ativas nesta base. Disciplinas: Fisica, Quimica, Filosofia, Historia. Turmas: 1o Ano A, 1o Ano B, 2o Ano A, 2o Ano B. Para comunicacao escolar geral, a secretaria e o canal institucional mais seguro; para alinhamentos pedagogicos, siga com coordenacao e orientacao conforme o assunto.

### Sou professor de Filosofia e quero trabalhar ai; como faco para entrar em contato?

- Slice: `public`
- Thread: `system_bank:professor_e_grade_docente:Q070` turn `1`
- `langgraph`: status 200, latency 3793.6ms, keyword pass `True`, quality `100`, reason `fato institucional canonico deve vir de fonte estruturada`
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
- `crewai`: status 200, latency 163.7ms, keyword pass `True`, quality `100`, reason `crewai_public_fast_path`
  answer: Secretaria (telefone): (11) 3333-4200
- `python_functions`: status 200, latency 161.2ms, keyword pass `True`, quality `100`, reason `python_functions_native_structured:institution`
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
- `llamaindex`: status 200, latency 10307.8ms, keyword pass `True`, quality `100`, reason `llamaindex_public_profile`
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
- `specialist_supervisor`: status 200, latency 8610.4ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_direct:institution_specialist`
  answer: Para oportunidades de carreira docente no Colégio Horizonte, você pode enviar seu currículo para o e-mail talentos@colegiohorizonte.edu.br. O retorno para estas solicitações é de até 5 dias úteis.

### Me diga o nome e o telefone do professor de Educacao Fisica.

- Slice: `protected`
- Thread: `system_bank:professor_e_grade_docente:Q071` turn `1`
- `langgraph`: status 200, latency 123.7ms, keyword pass `True`, quality `100`, reason `status administrativo autenticado exige service deterministico`
  answer: Essa consulta depende de autenticacao e vinculo da sua conta no Telegram. Use o portal da escola para gerar o codigo de vinculacao e depois envie o comando `/start link_<codigo>` ao bot.
- `crewai`: status 200, latency 192.5ms, keyword pass `True`, quality `100`, reason `crewai_protected_auth_required`
  answer: Essa consulta depende de autenticacao e vinculo da sua conta no Telegram. Use o portal da escola para gerar o codigo de vinculacao e depois envie o comando /start link_<codigo> ao bot.
- `python_functions`: status 200, latency 180.7ms, keyword pass `True`, quality `100`, reason `python_functions_native_structured:institution`
  answer: Essa consulta depende de autenticacao e vinculo da sua conta no Telegram. Use o portal da escola para gerar o codigo de vinculacao e depois envie o comando `/start link_<codigo>` ao bot.
- `llamaindex`: status 200, latency 142.2ms, keyword pass `True`, quality `100`, reason `status administrativo autenticado exige service deterministico`
  answer: Essa consulta depende de autenticacao e vinculo da sua conta no Telegram. Use o portal da escola para gerar o codigo de vinculacao e depois envie o comando `/start link_<codigo>` ao bot.
- `specialist_supervisor`: status 200, latency 10750.3ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_direct:institution_specialist`
  answer: Não consegui encontrar o nome e o telefone do professor de Educação Física nas informações públicas disponíveis. O Colégio Horizonte não divulga os contatos diretos de seus professores de forma pública. Sugiro que você entre em contato com a secretaria da escola para obter essa informação, através do telefone (11) 3333-4200 ou pelo e-mail secretaria@colegiohorizonte.edu.br.

### Gere um resumo enxuto da minha alocacao para eu revisar antes da reuniao pedagogica.

- Slice: `protected`
- Thread: `system_bank:professor_e_grade_docente:Q072` turn `1`
- `langgraph`: status 200, latency 2053.6ms, keyword pass `True`, quality `100`, reason `teacher_role_rescue`
  answer: Voce esta falando aqui como Fernando Azevedo, no perfil de professor do Colegio Horizonte. No Telegram, nesta etapa eu consigo consultar sua grade docente, turmas e disciplinas. A situacao individual dos alunos ainda nao esta liberada por este canal. Se quiser, me pergunte "qual meu horario?", "quais sao minhas turmas?" ou "quais disciplinas eu ministro?".
- `crewai`: status 200, latency 163.8ms, keyword pass `True`, quality `100`, reason `crewai_public_fast_path`
  answer: A proposta pedagogica publicada hoje combina A escola segue a BNCC e o curriculo do Ensino Medio articulado com projeto de vida, producao textual, cultura digital e aprofundamento academico progressivo. Na pratica, isso aparece em frentes como Tutoria academica e projeto de vida, Espaco Maker integrado ao curriculo, Acolhimento estruturado para familias e estudantes.
- `python_functions`: status 200, latency 96.5ms, keyword pass `True`, quality `100`, reason `python_functions_native_teacher_scope_guidance`
  answer: Voce esta falando aqui como Fernando Azevedo, no perfil de professor do Colegio Horizonte. No Telegram, nesta etapa eu consigo consultar sua grade docente, turmas e disciplinas. A situacao individual dos alunos ainda nao esta liberada por este canal. Se quiser, me pergunte "qual meu horario?", "quais sao minhas turmas?" ou "quais disciplinas eu ministro?".
- `llamaindex`: status 200, latency 117.2ms, keyword pass `True`, quality `100`, reason `llamaindex_teacher_scope_guidance`
  answer: Voce esta falando aqui como Fernando Azevedo, no perfil de professor do Colegio Horizonte. No Telegram, nesta etapa eu consigo consultar sua grade docente, turmas e disciplinas. A situacao individual dos alunos ainda nao esta liberada por este canal. Se quiser, me pergunte "qual meu horario?", "quais sao minhas turmas?" ou "quais disciplinas eu ministro?".
- `specialist_supervisor`: status 200, latency 17453.2ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_multi_direct:academic_specialist+workflow_specialist`
  answer: Acadêmico:
- Não consigo gerar um resumo da sua alocação, pois minhas funcionalidades se restringem a informações sobre notas, frequência, provas futuras e aprovação de alunos.

Atendimento: Sua solicitação para um resumo de alocação para revisão antes da reunião pedagógica foi encaminhada para a equipe de Suporte Acadêmico. Um de nossos atendentes entrará em contato com você o mais breve possível para ajudar. Seu protocolo de atendimento é ATD-20260401-35380480.

### Quero agendar uma visita para conhecer a escola.

- Slice: `workflow`
- Thread: `system_bank:workflow_protocolos_visitas_e_handoff:Q073` turn `1`
- `langgraph`: status 200, latency 163.8ms, keyword pass `True`, quality `100`, reason `consulta publica de navegacao e canais foi resgatada do dominio support`
  answer: Pedido de visita registrado para o Colegio Horizonte. Protocolo: VIS-20260401-8B6348. Preferencia informada: janela a confirmar. Fila responsavel: admissoes. Ticket operacional: ATD-20260401-9F9AE0C1. A equipe comercial valida a janela e retorna com a confirmacao.
- `crewai`: status 200, latency 211.7ms, keyword pass `True`, quality `100`, reason `workflow_visit_create`
  answer: Pedido de visita registrado para o Colegio Horizonte. Protocolo: VIS-20260401-117DCE. Preferencia informada: janela a confirmar. Fila responsavel: admissoes. Ticket operacional: ATD-20260401-B87315B0. A equipe comercial valida a janela e retorna com a confirmacao.
- `python_functions`: status 200, latency 155.1ms, keyword pass `True`, quality `100`, reason `python_functions_native_structured:support`
  answer: Pedido de visita registrado para o Colegio Horizonte. Protocolo: VIS-20260401-43391E. Preferencia informada: janela a confirmar. Fila responsavel: admissoes. Ticket operacional: ATD-20260401-9312FE31. A equipe comercial valida a janela e retorna com a confirmacao.
- `llamaindex`: status 200, latency 174.9ms, keyword pass `True`, quality `100`, reason `consulta publica de navegacao e canais foi resgatada do dominio support`
  answer: Pedido de visita registrado para o Colegio Horizonte. Protocolo: VIS-20260401-A379AB. Preferencia informada: janela a confirmar. Fila responsavel: admissoes. Ticket operacional: ATD-20260401-8EAF87F9. A equipe comercial valida a janela e retorna com a confirmacao.
- `specialist_supervisor`: status 200, latency 1966.5ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_tool_first:visit_booking`
  answer: Pedido de visita registrado. Protocolo: VIS-20260401-4C52CF. Preferencia registrada: janela a confirmar. Ticket operacional: ATD-20260401-1E156FCA. Se quiser, eu tambem posso acompanhar o status ou remarcar a visita.

### Pode ser na quinta a tarde?

- Slice: `workflow`
- Thread: `system_bank:workflow_protocolos_visitas_e_handoff:Q073` turn `2`
- `langgraph`: status 200, latency 157.8ms, keyword pass `True`, quality `100`, reason `workflow_follow_up_rescue:visit_update`
  answer: Pedido de visita atualizado com a fila de admissions. Protocolo: VIS-20260401-8B6348. Ticket operacional: ATD-20260401-9F9AE0C1. Nova preferencia: quinta-feira - tarde (02/04/2026 - 14:30). Admissions valida a nova janela e retorna com a confirmacao.
- `crewai`: status 200, latency 183.8ms, keyword pass `True`, quality `100`, reason `workflow_visit_reschedule`
  answer: Pedido de visita atualizado com a fila de admissoes. - Protocolo: VIS-20260401-117DCE - Ticket operacional: ATD-20260401-B87315B0 - Nova preferencia: quinta-feira - tarde (02/04/2026 - 14:30) Proximo passo: admissions valida a nova janela e retorna com a confirmacao.
- `python_functions`: status 200, latency 217.6ms, keyword pass `True`, quality `100`, reason `consulta publica de navegacao e canais foi resgatada do dominio support`
  answer: Pedido de visita atualizado com a fila de admissions. Protocolo: VIS-20260401-43391E. Ticket operacional: ATD-20260401-9312FE31. Nova preferencia: quinta-feira - tarde (02/04/2026 - 14:30). Admissions valida a nova janela e retorna com a confirmacao.
- `llamaindex`: status 200, latency 223.5ms, keyword pass `True`, quality `100`, reason `consulta publica de navegacao e canais foi resgatada do dominio support`
  answer: Pedido de visita atualizado com a fila de admissions. Protocolo: VIS-20260401-A379AB. Ticket operacional: ATD-20260401-8EAF87F9. Nova preferencia: quinta-feira - tarde (02/04/2026 - 14:30). Admissions valida a nova janela e retorna com a confirmacao.
- `specialist_supervisor`: status 200, latency 1941.2ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_tool_first:visit_reschedule`
  answer: Pedido de visita atualizado. Protocolo: VIS-20260401-4C52CF. Nova preferencia: quinta-feira, 14:30. Admissions valida a nova janela e retorna com a confirmacao.

### Qual e o protocolo dessa visita?

- Slice: `workflow`
- Thread: `system_bank:workflow_protocolos_visitas_e_handoff:Q073` turn `3`
- `langgraph`: status 200, latency 149.6ms, keyword pass `True`, quality `100`, reason `workflow_follow_up_rescue:visit_update`
  answer: Nao consegui atualizar a visita agora. Se quiser, me passe novamente o protocolo da visita ou o novo horario desejado.
- `crewai`: status 200, latency 169.1ms, keyword pass `True`, quality `100`, reason `workflow_protocol_lookup`
  answer: O protocolo da sua visita e VIS-20260401-117DCE. - Ticket operacional: ATD-20260401-B87315B0 - Preferencia registrada: quinta-feira - 14:30 (02/04/2026 - 14:30) Se quiser, eu tambem posso te dizer o status, remarcar ou cancelar a visita.
- `python_functions`: status 200, latency 183.4ms, keyword pass `True`, quality `100`, reason `python_functions_native_structured:support`
  answer: Solicitacao institucional registrada para direcao. Protocolo: REQ-20260401-274EF3. Assunto: Qual e o protocolo dessa visita? Fila responsavel: direcao. Ticket operacional: ATD-20260401-9312FE31. A equipe faz a triagem inicial e segue o retorno pelo fluxo institucional.
- `llamaindex`: status 200, latency 186.7ms, keyword pass `True`, quality `100`, reason `consulta publica de navegacao e canais foi resgatada do dominio support`
  answer: Solicitacao institucional registrada para direcao. Protocolo: REQ-20260401-28D5B0. Assunto: Qual e o protocolo dessa visita? Fila responsavel: direcao. Ticket operacional: ATD-20260401-8EAF87F9. A equipe faz a triagem inicial e segue o retorno pelo fluxo institucional.
- `specialist_supervisor`: status 200, latency 9220.2ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_direct:workflow_specialist`
  answer: O protocolo da sua visita é VIS-20260401-4C52CF.

### Preciso remarcar para a semana que vem.

- Slice: `workflow`
- Thread: `system_bank:workflow_protocolos_visitas_e_handoff:Q073` turn `4`
- `langgraph`: status 200, latency 1795.5ms, keyword pass `True`, quality `100`, reason `a intencao esta ambigua e exige clarificacao antes de recuperar contexto`
  answer: Compreendo que você deseja remarcar a visita. Para que eu possa te ajudar, por favor, me informe o protocolo da visita ou o novo horário desejado. Assim, consigo verificar as opções e te auxiliar com a remarcação.
- `crewai`: status 200, latency 185.4ms, keyword pass `True`, quality `100`, reason `workflow_visit_reschedule`
  answer: Pedido de visita atualizado com a fila de admissoes. - Protocolo: VIS-20260401-117DCE - Ticket operacional: ATD-20260401-B87315B0 - Nova preferencia: quinta-feira - 14:30 (09/04/2026 - 14:30) Proximo passo: admissions valida a nova janela e retorna com a confirmacao.
- `python_functions`: status 200, latency 179.2ms, keyword pass `True`, quality `100`, reason `a intencao esta ambigua e exige clarificacao antes de recuperar contexto`
  answer: Posso ajudar com informacoes publicas da escola, como calendario, matricula, documentos exigidos e regras de atendimento digital. Se quiser, pergunte por exemplo: "quais documentos preciso para a matricula?" ou "quando acontece a reuniao de pais?".
- `llamaindex`: status 200, latency 8306.4ms, keyword pass `True`, quality `100`, reason `llamaindex_public_profile`
  answer: Hoje o Colegio Horizonte publica estas janelas de visita:
- Visita guiada ao campus: terca-feira, das 09:00 as 10:15, em Recepcao principal e circuito pedagogico. Inclui apresentacao institucional, visita aos espacos e conversa curta com admissions.
- Visita guiada com foco pedagogico: quinta-feira, das 14:30 as 15:45, em Recepcao principal e salas de projeto. Janela pensada para familias que desejam conhecer infraestrutura, rotina e proposta pedagogica.
Agendamento: bot, whatsapp comercial ou admissions. Prazo de confirmacao: confirmacao em ate 1 dia util.
- `specialist_supervisor`: status 200, latency 1898.4ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_tool_first:visit_reschedule_guidance`
  answer: Para remarcar a visita, eu sigo pelo protocolo VIS-20260401-4C52CF. A preferencia atual registrada e 02/04/2026 - 14:30. Me diga o novo dia ou janela desejada e eu atualizo o pedido. Ticket operacional: ATD-20260401-1E156FCA.

### Agora cancela, por favor.

- Slice: `workflow`
- Thread: `system_bank:workflow_protocolos_visitas_e_handoff:Q073` turn `5`
- `langgraph`: status 200, latency 148.8ms, keyword pass `True`, quality `100`, reason `workflow_follow_up_rescue:visit_update`
  answer: Nao consegui atualizar a visita agora. Se quiser, me passe novamente o protocolo da visita ou o novo horario desejado.
- `crewai`: status 200, latency 13063.6ms, keyword pass `True`, quality `100`, reason `crewai_public_flow_completed`
  answer: O que você gostaria de cancelar?
- `python_functions`: status 200, latency 222.8ms, keyword pass `True`, quality `100`, reason `consulta publica de navegacao e canais foi resgatada do dominio support`
  answer: Nao consegui atualizar a visita agora. Se quiser, me passe novamente o protocolo da visita ou o novo horario desejado.
- `llamaindex`: status 200, latency 3094.0ms, keyword pass `True`, quality `100`, reason `llamaindex_public_profile`
  answer: Voce fala comigo, o EduAssist. Eu consigo te orientar e te encaminhar para secretaria, admissions, coordenacao, orientacao educacional, financeiro ou direcao. Hoje eu consigo te encaminhar por aqui para matricula, bolsas e atendimento comercial, agendamento de visita a escola, secretaria e documentos, coordenacao, orientacao educacional e financeiro e boletos. Se quiser, me diga o assunto em uma frase curta e eu te indico o melhor caminho sem voce precisar adivinhar o setor.
- `specialist_supervisor`: status 200, latency 8466.0ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_direct:workflow_specialist`
  answer: Para cancelar a visita, preciso do código do protocolo. Você pode me informar o código, por favor?

### Preciso emitir documentos finais e concluir a transferencia do Diego.

- Slice: `workflow`
- Thread: `system_bank:workflow_protocolos_visitas_e_handoff:Q078` turn `1`
- `langgraph`: status 200, latency 104.2ms, keyword pass `True`, quality `100`, reason `status administrativo autenticado exige service deterministico`
  answer: Hoje os documentos exigidos para a matricula publicados pela escola sao:
- Formulario cadastral preenchido
- Documento de identificacao do aluno
- CPF do aluno, quando houver
- Historico escolar
- Comprovante de residencia atualizado
- Documento de identificacao do responsavel legal
Se quiser, eu tambem posso explicar as etapas da matricula ou como funciona o envio inicial desses documentos.
- `crewai`: status 200, latency 179.0ms, keyword pass `True`, quality `100`, reason `protected_shadow_needs_student_clarification`
  answer: Posso te ajudar com Lucas Oliveira, Ana Oliveira. Me diga qual aluno voce quer consultar.
- `python_functions`: status 200, latency 102.8ms, keyword pass `True`, quality `100`, reason `python_functions_native_structured:institution`
  answer: Hoje os documentos exigidos para a matricula publicados pela escola sao:
- Formulario cadastral preenchido
- Documento de identificacao do aluno
- CPF do aluno, quando houver
- Historico escolar
- Comprovante de residencia atualizado
- Documento de identificacao do responsavel legal
Se quiser, eu tambem posso explicar as etapas da matricula ou como funciona o envio inicial desses documentos.
- `llamaindex`: status 200, latency 124.1ms, keyword pass `True`, quality `100`, reason `status administrativo autenticado exige service deterministico`
  answer: Hoje os documentos exigidos para a matricula publicados pela escola sao:
- Formulario cadastral preenchido
- Documento de identificacao do aluno
- CPF do aluno, quando houver
- Historico escolar
- Comprovante de residencia atualizado
- Documento de identificacao do responsavel legal
Se quiser, eu tambem posso explicar as etapas da matricula ou como funciona o envio inicial desses documentos.
- `specialist_supervisor`: status 200, latency 1912.0ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_tool_first:human_handoff`
  answer: Encaminhei sua solicitacao para a fila de secretaria. Protocolo: ATD-20260401-F0CEF1DF. Status atual: queued. Se preferir, voce tambem pode seguir pelo WhatsApp oficial (11) 97500-2040.

### Quero abrir um atendimento com o financeiro para negociar uma mensalidade parcialmente paga.

- Slice: `workflow`
- Thread: `system_bank:workflow_protocolos_visitas_e_handoff:Q079` turn `1`
- `langgraph`: status 200, latency 200.3ms, keyword pass `True`, quality `100`, reason `o turno atual trouxe pistas explicitas de outro dominio protegido e o roteamento foi corrigido`
  answer: Resumo financeiro das contas vinculadas:
- Total de faturas em aberto: 3
- Total de faturas vencidas: 0
- Lucas Oliveira: 1 em aberto, 0 vencidas
  2026-01: vencimento 2026-01-10, status paga, valor 1450.00
  2026-02: vencimento 2026-02-10, status paga, valor 1450.00
- Ana Oliveira: 2 em aberto, 0 vencidas
  2026-01: vencimento 2026-01-10, status paga, valor 1450.00
  2026-02: vencimento 2026-02-10, status paga, valor 1450.00
- `crewai`: status 200, latency 171.9ms, keyword pass `True`, quality `100`, reason `protected_shadow_needs_student_clarification`
  answer: Posso te ajudar com Lucas Oliveira, Ana Oliveira. Me diga qual aluno voce quer consultar.
- `python_functions`: status 200, latency 156.7ms, keyword pass `True`, quality `100`, reason `python_functions_native_structured:institution`
  answer: Valores publicos de referencia para 2026:
- Ensino Fundamental II (Manha): mensalidade R$ 1.280,00 e taxa de matricula R$ 350,00. Valor comercial publico de referencia para 2026. Material didatico e uniforme sao cobrados a parte.
- Ensino Medio (Manha): mensalidade R$ 1.450,00 e taxa de matricula R$ 350,00. Valor comercial publico de referencia para 2026. Ha politica comercial para irmaos e pagamento pontual.
- Periodo integral opcional (Complemento contraturno): mensalidade R$ 480,00 e taxa de matricula R$ 0,00. Adicional mensal aplicado ao estudante matriculado no turno regular que aderir ao periodo integral.
Se quiser, eu tambem posso resumir bolsas, descontos comerciais e canais de matricula.
- `llamaindex`: status 200, latency 3171.5ms, keyword pass `True`, quality `100`, reason `llamaindex_public_profile`
  answer: Valores publicos de referencia para 2026:
- Ensino Fundamental II (Manha): mensalidade R$ 1.280,00 e taxa de matricula R$ 350,00. Valor comercial publico de referencia para 2026. Material didatico e uniforme sao cobrados a parte.
- Ensino Medio (Manha): mensalidade R$ 1.450,00 e taxa de matricula R$ 350,00. Valor comercial publico de referencia para 2026. Ha politica comercial para irmaos e pagamento pontual.
- Periodo integral opcional (Complemento contraturno): mensalidade R$ 480,00 e taxa de matricula R$ 0,00. Adicional mensal aplicado ao estudante matriculado no turno regular que aderir ao periodo integral.
Se quiser, eu tambem posso resumir bolsas, descontos comerciais e canais de matricula.
- `specialist_supervisor`: status 200, latency 1895.1ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_resolved_intent:finance_student_clarify`
  answer: Consigo verificar a situacao financeira, mas preciso que voce me diga qual aluno: Lucas Oliveira ou Ana Oliveira?

### Qual a diferenca entre abrir um protocolo, um chamado e um handoff humano?

- Slice: `workflow`
- Thread: `system_bank:workflow_protocolos_visitas_e_handoff:Q080` turn `1`
- `langgraph`: status 200, latency 138.8ms, keyword pass `True`, quality `100`, reason `o usuario demonstrou necessidade de atendimento humano ou operacional`
  answer: Encaminhei sua solicitacao para a fila de atendimento. Protocolo: ATD-20260401-285CB5E7. Status atual: queued. A equipe humana pode continuar esse atendimento no portal operacional.
- `crewai`: status 200, latency 218.8ms, keyword pass `True`, quality `100`, reason `support_handoff_created`
  answer: Encaminhei sua solicitacao para a fila de atendimento. Protocolo: ATD-20260401-AFAB92A5. Status atual: queued. A equipe humana podera continuar esse atendimento no portal operacional.
- `python_functions`: status 200, latency 142.8ms, keyword pass `True`, quality `100`, reason `o usuario demonstrou necessidade de atendimento humano ou operacional`
  answer: Encaminhei sua solicitacao para a fila de atendimento. Protocolo: ATD-20260401-0C0AD061. Status atual: queued. A equipe humana pode continuar esse atendimento no portal operacional.
- `llamaindex`: status 200, latency 178.5ms, keyword pass `True`, quality `100`, reason `o usuario demonstrou necessidade de atendimento humano ou operacional`
  answer: Encaminhei sua solicitacao para a fila de atendimento. Protocolo: ATD-20260401-C3533E6E. Status atual: queued. A equipe humana pode continuar esse atendimento no portal operacional.
- `specialist_supervisor`: status 200, latency 1933.3ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_fast_path:support_process_boundary`
  answer: Hoje eu trato esses tres fluxos de forma diferente: protocolo registra uma solicitacao institucional rastreavel; chamado costuma ser o ticket operacional associado ao atendimento; e handoff humano e o encaminhamento real para uma fila ou equipe, normalmente com protocolo e status para acompanhamento.

