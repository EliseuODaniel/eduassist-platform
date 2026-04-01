# Five-Path Chatbot Comparison Report

Date: 2026-04-01T21:38:45.073894+00:00

Dataset: `/home/edann/projects/eduassist-platform/tests/evals/datasets/system_question_bank_wave_teacher_workflow.json`

Run prefix: `debug:five-path:20260401T213556Z`

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
| `langgraph` | `16/16` | `16/16` | `100.0` | `751.7 ms` |
| `crewai` | `16/16` | `16/16` | `100.0` | `3350.2 ms` |
| `python_functions` | `16/16` | `16/16` | `100.0` | `233.0 ms` |
| `llamaindex` | `16/16` | `16/16` | `100.0` | `1360.6 ms` |
| `specialist_supervisor` | `16/16` | `16/16` | `100.0` | `4743.2 ms` |

## By Slice

- `protected`
  - `langgraph`: ok 7/7, keyword pass 7/7, quality 100.0, latency 738.8ms
  - `crewai`: ok 7/7, keyword pass 7/7, quality 100.0, latency 5844.6ms
  - `python_functions`: ok 7/7, keyword pass 7/7, quality 100.0, latency 217.6ms
  - `llamaindex`: ok 7/7, keyword pass 7/7, quality 100.0, latency 242.1ms
  - `specialist_supervisor`: ok 7/7, keyword pass 7/7, quality 100.0, latency 6043.7ms
- `public`
  - `langgraph`: ok 1/1, keyword pass 1/1, quality 100.0, latency 3632.6ms
  - `crewai`: ok 1/1, keyword pass 1/1, quality 100.0, latency 302.8ms
  - `python_functions`: ok 1/1, keyword pass 1/1, quality 100.0, latency 392.9ms
  - `llamaindex`: ok 1/1, keyword pass 1/1, quality 100.0, latency 8621.9ms
  - `specialist_supervisor`: ok 1/1, keyword pass 1/1, quality 100.0, latency 7736.4ms
- `workflow`
  - `langgraph`: ok 8/8, keyword pass 8/8, quality 100.0, latency 402.9ms
  - `crewai`: ok 8/8, keyword pass 8/8, quality 100.0, latency 1548.5ms
  - `python_functions`: ok 8/8, keyword pass 8/8, quality 100.0, latency 226.5ms
  - `llamaindex`: ok 8/8, keyword pass 8/8, quality 100.0, latency 1431.6ms
  - `specialist_supervisor`: ok 8/8, keyword pass 8/8, quality 100.0, latency 3231.1ms

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
- `langgraph`: status 200, latency 339.0ms, keyword pass `True`, quality `100`, reason `teacher_role_rescue`
  answer: Grade docente de Fernando Azevedo:
- 1o Ano A - Fisica (2026)
- 1o Ano A - Quimica (2026)
- 1o Ano B - Filosofia (2026)
- 1o Ano B - Historia (2026)
- 2o Ano A - Filosofia (2026)
- 2o Ano A - Fisica (2026)
- 2o Ano A - Quimica (2026)
- 2o Ano B - Filosofia (2026)
- `crewai`: status 200, latency 19372.9ms, keyword pass `True`, quality `100`, reason `crewai_protected_flow_completed`
  answer: Para qual aluno você gostaria de saber as turmas e disciplinas?
- `python_functions`: status 200, latency 255.1ms, keyword pass `True`, quality `100`, reason `python_functions_native_teacher_schedule`
  answer: Grade docente de Fernando Azevedo:
- 1o Ano A - Fisica (2026)
- 1o Ano A - Quimica (2026)
- 1o Ano B - Filosofia (2026)
- 1o Ano B - Historia (2026)
- 2o Ano A - Filosofia (2026)
- 2o Ano A - Fisica (2026)
- 2o Ano A - Quimica (2026)
- 2o Ano B - Filosofia (2026)
- `llamaindex`: status 200, latency 258.4ms, keyword pass `True`, quality `100`, reason `dados estruturados devem passar por service deterministico`
  answer: Grade docente de Fernando Azevedo:
- 1o Ano A - Fisica (2026)
- 1o Ano A - Quimica (2026)
- 1o Ano B - Filosofia (2026)
- 1o Ano B - Historia (2026)
- 2o Ano A - Filosofia (2026)
- 2o Ano A - Fisica (2026)
- 2o Ano A - Quimica (2026)
- 2o Ano B - Filosofia (2026)
- `specialist_supervisor`: status 200, latency 2492.5ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_fast_path:teacher_schedule`
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
- `langgraph`: status 200, latency 234.6ms, keyword pass `True`, quality `100`, reason `teacher_role_rescue`
  answer: Grade docente de Fernando Azevedo:
- 1o Ano A - Fisica (2026)
- 1o Ano A - Quimica (2026)
- 1o Ano B - Filosofia (2026)
- 1o Ano B - Historia (2026)
- 2o Ano A - Filosofia (2026)
- 2o Ano A - Fisica (2026)
- 2o Ano A - Quimica (2026)
- 2o Ano B - Filosofia (2026)
- `crewai`: status 200, latency 203.8ms, keyword pass `True`, quality `100`, reason `crewai_protected_teacher_scope_preflow`
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
- `python_functions`: status 200, latency 210.3ms, keyword pass `True`, quality `100`, reason `python_functions_native_teacher_schedule`
  answer: Grade docente de Fernando Azevedo:
- 1o Ano A - Fisica (2026)
- 1o Ano A - Quimica (2026)
- 1o Ano B - Filosofia (2026)
- 1o Ano B - Historia (2026)
- 2o Ano A - Filosofia (2026)
- 2o Ano A - Fisica (2026)
- 2o Ano A - Quimica (2026)
- 2o Ano B - Filosofia (2026)
- `llamaindex`: status 200, latency 228.1ms, keyword pass `True`, quality `100`, reason `llamaindex_teacher_schedule_direct`
  answer: Grade docente de Fernando Azevedo:
- 1o Ano A - Fisica (2026)
- 1o Ano A - Quimica (2026)
- 1o Ano B - Filosofia (2026)
- 1o Ano B - Historia (2026)
- 2o Ano A - Filosofia (2026)
- 2o Ano A - Fisica (2026)
- 2o Ano A - Quimica (2026)
- 2o Ano B - Filosofia (2026)
- `specialist_supervisor`: status 200, latency 174.8ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_fast_path:teacher_schedule`
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
- `langgraph`: status 200, latency 221.5ms, keyword pass `True`, quality `100`, reason `teacher_role_rescue`
  answer: Nao. Sua grade atual nao e so do Ensino Medio.
- `crewai`: status 200, latency 225.3ms, keyword pass `True`, quality `100`, reason `crewai_protected_teacher_scope_preflow`
  answer: Nao. Sua grade atual nao e so do Ensino Medio.
- `python_functions`: status 200, latency 232.5ms, keyword pass `True`, quality `100`, reason `python_functions_native_teacher_schedule`
  answer: Nao. Sua grade atual nao e so do Ensino Medio.
- `llamaindex`: status 200, latency 238.2ms, keyword pass `True`, quality `100`, reason `llamaindex_teacher_schedule_direct`
  answer: Nao. Sua grade atual nao e so do Ensino Medio.
- `specialist_supervisor`: status 200, latency 185.2ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_fast_path:teacher_schedule`
  answer: Nao. Sua grade atual nao e so do Ensino Medio.

### Quais turmas eu atendo em Filosofia e em que classes?

- Slice: `protected`
- Thread: `system_bank:professor_e_grade_docente:Q068` turn `1`
- `langgraph`: status 200, latency 203.1ms, keyword pass `True`, quality `100`, reason `teacher_role_rescue`
  answer: Turmas de Fernando Azevedo:
- 1o Ano B
- 2o Ano A
- 2o Ano B
- 3o Ano A
- `crewai`: status 200, latency 20330.9ms, keyword pass `True`, quality `100`, reason `crewai_protected_flow_timeout`
  answer: Eu nao consegui consolidar essa consulta protegida com seguranca agora. Se quiser, me diga qual aluno e qual dado voce quer consultar.
- `python_functions`: status 200, latency 246.2ms, keyword pass `True`, quality `100`, reason `python_functions_native_teacher_schedule`
  answer: Turmas de Fernando Azevedo:
- 1o Ano B
- 2o Ano A
- 2o Ano B
- 3o Ano A
- `llamaindex`: status 200, latency 292.4ms, keyword pass `True`, quality `100`, reason `dados estruturados devem passar por service deterministico`
  answer: Turmas de Fernando Azevedo:
- 1o Ano B
- 2o Ano A
- 2o Ano B
- 3o Ano A
- `specialist_supervisor`: status 200, latency 217.2ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_fast_path:teacher_schedule`
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
- `langgraph`: status 200, latency 2105.8ms, keyword pass `True`, quality `100`, reason `teacher_role_rescue`
  answer: Resumo docente de Fernando Azevedo: 10 turma(s) e 6 disciplina(s) ativas nesta base. Disciplinas: Fisica, Quimica, Filosofia, Historia. Turmas: 1o Ano A, 1o Ano B, 2o Ano A, 2o Ano B. Para comunicacao escolar geral, a secretaria e o canal institucional mais seguro; para alinhamentos pedagogicos, siga com coordenacao e orientacao conforme o assunto.
- `crewai`: status 200, latency 280.3ms, keyword pass `True`, quality `100`, reason `crewai_protected_teacher_scope_preflow`
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
- `python_functions`: status 200, latency 270.8ms, keyword pass `True`, quality `100`, reason `python_functions_native_teacher_schedule`
  answer: Resumo docente de Fernando Azevedo: 10 turma(s) e 6 disciplina(s) ativas nesta base. Disciplinas: Fisica, Quimica, Filosofia, Historia. Turmas: 1o Ano A, 1o Ano B, 2o Ano A, 2o Ano B. Para comunicacao escolar geral, a secretaria e o canal institucional mais seguro; para alinhamentos pedagogicos, siga com coordenacao e orientacao conforme o assunto.
- `llamaindex`: status 200, latency 336.9ms, keyword pass `True`, quality `100`, reason `llamaindex_teacher_schedule_direct`
  answer: Resumo docente de Fernando Azevedo: 10 turma(s) e 6 disciplina(s) ativas nesta base. Disciplinas: Fisica, Quimica, Filosofia, Historia. Turmas: 1o Ano A, 1o Ano B, 2o Ano A, 2o Ano B. Para comunicacao escolar geral, a secretaria e o canal institucional mais seguro; para alinhamentos pedagogicos, siga com coordenacao e orientacao conforme o assunto.
- `specialist_supervisor`: status 200, latency 267.2ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_fast_path:teacher_schedule`
  answer: Resumo docente de Fernando Azevedo: 10 turma(s) e 6 disciplina(s) ativas nesta base. Disciplinas: Fisica, Quimica, Filosofia, Historia. Turmas: 1o Ano A, 1o Ano B, 2o Ano A, 2o Ano B. Para comunicacao escolar geral, a secretaria e o canal institucional mais seguro; para alinhamentos pedagogicos, siga com coordenacao e orientacao conforme o assunto.

### Sou professor de Filosofia e quero trabalhar ai; como faco para entrar em contato?

- Slice: `public`
- Thread: `system_bank:professor_e_grade_docente:Q070` turn `1`
- `langgraph`: status 200, latency 3632.6ms, keyword pass `True`, quality `100`, reason `fato institucional canonico deve vir de fonte estruturada`
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
- `crewai`: status 200, latency 302.8ms, keyword pass `True`, quality `100`, reason `crewai_public_fast_path`
  answer: Secretaria (telefone): (11) 3333-4200
- `python_functions`: status 200, latency 392.9ms, keyword pass `True`, quality `100`, reason `python_functions_native_structured:institution`
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
- `llamaindex`: status 200, latency 8621.9ms, keyword pass `True`, quality `100`, reason `llamaindex_public_profile`
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
- `specialist_supervisor`: status 200, latency 7736.4ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_direct:institution_specialist`
  answer: Para entrar em contato sobre oportunidades de trabalho como professor(a) de Filosofia no Colégio Horizonte, você pode enviar seu currículo e suas dúvidas para o e-mail: talentos@colegiohorizonte.edu.br. O retorno para esta solicitação ocorre em até 5 dias úteis.

### Me diga o nome e o telefone do professor de Educacao Fisica.

- Slice: `protected`
- Thread: `system_bank:professor_e_grade_docente:Q071` turn `1`
- `langgraph`: status 200, latency 172.9ms, keyword pass `True`, quality `100`, reason `status administrativo autenticado exige service deterministico`
  answer: Essa consulta depende de autenticacao e vinculo da sua conta no Telegram. Use o portal da escola para gerar o codigo de vinculacao e depois envie o comando `/start link_<codigo>` ao bot.
- `crewai`: status 200, latency 283.9ms, keyword pass `True`, quality `100`, reason `crewai_protected_auth_required`
  answer: Essa consulta depende de autenticacao e vinculo da sua conta no Telegram. Use o portal da escola para gerar o codigo de vinculacao e depois envie o comando /start link_<codigo> ao bot.
- `python_functions`: status 200, latency 178.3ms, keyword pass `True`, quality `100`, reason `python_functions_native_structured:institution`
  answer: Essa consulta depende de autenticacao e vinculo da sua conta no Telegram. Use o portal da escola para gerar o codigo de vinculacao e depois envie o comando `/start link_<codigo>` ao bot.
- `llamaindex`: status 200, latency 190.6ms, keyword pass `True`, quality `100`, reason `status administrativo autenticado exige service deterministico`
  answer: Essa consulta depende de autenticacao e vinculo da sua conta no Telegram. Use o portal da escola para gerar o codigo de vinculacao e depois envie o comando `/start link_<codigo>` ao bot.
- `specialist_supervisor`: status 200, latency 11976.9ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_direct:institution_specialist`
  answer: Não consegui encontrar o nome e o telefone específico do professor de Educação Física nas informações públicas disponíveis. No entanto, você pode entrar em contato com a secretaria da escola através do telefone (11) 3333-4200 ou pelo e-mail secretaria@colegiohorizonte.edu.br para obter essa informação.

### Gere um resumo enxuto da minha alocacao para eu revisar antes da reuniao pedagogica.

- Slice: `protected`
- Thread: `system_bank:professor_e_grade_docente:Q072` turn `1`
- `langgraph`: status 200, latency 1894.9ms, keyword pass `True`, quality `100`, reason `teacher_role_rescue`
  answer: Voce esta falando aqui como Fernando Azevedo, no perfil de professor do Colegio Horizonte. No Telegram, nesta etapa eu consigo consultar sua grade docente, turmas e disciplinas. A situacao individual dos alunos ainda nao esta liberada por este canal. Se quiser, me pergunte "qual meu horario?", "quais sao minhas turmas?" ou "quais disciplinas eu ministro?".
- `crewai`: status 200, latency 215.4ms, keyword pass `True`, quality `100`, reason `crewai_public_fast_path`
  answer: A proposta pedagogica publicada hoje combina A escola segue a BNCC e o curriculo do Ensino Medio articulado com projeto de vida, producao textual, cultura digital e aprofundamento academico progressivo. Na pratica, isso aparece em frentes como Tutoria academica e projeto de vida, Espaco Maker integrado ao curriculo, Acolhimento estruturado para familias e estudantes.
- `python_functions`: status 200, latency 130.3ms, keyword pass `True`, quality `100`, reason `python_functions_native_teacher_scope_guidance`
  answer: Voce esta falando aqui como Fernando Azevedo, no perfil de professor do Colegio Horizonte. No Telegram, nesta etapa eu consigo consultar sua grade docente, turmas e disciplinas. A situacao individual dos alunos ainda nao esta liberada por este canal. Se quiser, me pergunte "qual meu horario?", "quais sao minhas turmas?" ou "quais disciplinas eu ministro?".
- `llamaindex`: status 200, latency 150.1ms, keyword pass `True`, quality `100`, reason `llamaindex_teacher_scope_guidance`
  answer: Voce esta falando aqui como Fernando Azevedo, no perfil de professor do Colegio Horizonte. No Telegram, nesta etapa eu consigo consultar sua grade docente, turmas e disciplinas. A situacao individual dos alunos ainda nao esta liberada por este canal. Se quiser, me pergunte "qual meu horario?", "quais sao minhas turmas?" ou "quais disciplinas eu ministro?".
- `specialist_supervisor`: status 200, latency 26992.1ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_multi_direct:academic_specialist+workflow_specialist`
  answer: Acadêmico:
- Como especialista acadêmico, estou configurado para fornecer informações sobre notas, frequência, provas futuras e aprovação de alunos. No momento, não consigo gerar um resumo da sua alocação profissional, Fernando Azevedo, pois essa funcionalidade está fora do meu escopo de atuação. Para informações sobre sua alocação de classes e horários, você precisaria consultar um especialista de workflow ou um sistema de gestão de recursos humanos.

Atendimento: Sua solicitação para um resumo de alocação para revisão antes da reunião pedagógica foi encaminhada para a equipe de suporte. Um atendente entrará em contato com você em breve. O código do seu ticket é ATD-20260401-1166E7D9.

### Quero agendar uma visita para conhecer a escola.

- Slice: `workflow`
- Thread: `system_bank:workflow_protocolos_visitas_e_handoff:Q073` turn `1`
- `langgraph`: status 200, latency 206.9ms, keyword pass `True`, quality `100`, reason `consulta publica de navegacao e canais foi resgatada do dominio support`
  answer: Pedido de visita registrado para o Colegio Horizonte. Protocolo: VIS-20260401-0439FD. Preferencia informada: janela a confirmar. Fila responsavel: admissoes. Ticket operacional: ATD-20260401-0DB09FB2. A equipe comercial valida a janela e retorna com a confirmacao.
- `crewai`: status 200, latency 258.2ms, keyword pass `True`, quality `100`, reason `workflow_visit_create`
  answer: Pedido de visita registrado para o Colegio Horizonte. Protocolo: VIS-20260401-A20A17. Preferencia informada: janela a confirmar. Fila responsavel: admissoes. Ticket operacional: ATD-20260401-00507DC5. A equipe comercial valida a janela e retorna com a confirmacao.
- `python_functions`: status 200, latency 259.7ms, keyword pass `True`, quality `100`, reason `python_functions_native_structured:support`
  answer: Pedido de visita registrado para o Colegio Horizonte. Protocolo: VIS-20260401-D093B9. Preferencia informada: janela a confirmar. Fila responsavel: admissoes. Ticket operacional: ATD-20260401-E176B8D1. A equipe comercial valida a janela e retorna com a confirmacao.
- `llamaindex`: status 200, latency 280.6ms, keyword pass `True`, quality `100`, reason `consulta publica de navegacao e canais foi resgatada do dominio support`
  answer: Pedido de visita registrado para o Colegio Horizonte. Protocolo: VIS-20260401-E59BD1. Preferencia informada: janela a confirmar. Fila responsavel: admissoes. Ticket operacional: ATD-20260401-235F5D1F. A equipe comercial valida a janela e retorna com a confirmacao.
- `specialist_supervisor`: status 200, latency 180.8ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_tool_first:visit_booking`
  answer: Pedido de visita registrado. Protocolo: VIS-20260401-30EAE9. Preferencia registrada: janela a confirmar. Ticket operacional: ATD-20260401-90D3FDC9. Se quiser, eu tambem posso acompanhar o status ou remarcar a visita.

### Pode ser na quinta a tarde?

- Slice: `workflow`
- Thread: `system_bank:workflow_protocolos_visitas_e_handoff:Q073` turn `2`
- `langgraph`: status 200, latency 209.1ms, keyword pass `True`, quality `100`, reason `workflow_follow_up_rescue:visit_update`
  answer: Pedido de visita atualizado com a fila de admissions. Protocolo: VIS-20260401-0439FD. Ticket operacional: ATD-20260401-0DB09FB2. Nova preferencia: quinta-feira - tarde (02/04/2026 - 14:30). Admissions valida a nova janela e retorna com a confirmacao.
- `crewai`: status 200, latency 240.0ms, keyword pass `True`, quality `100`, reason `workflow_visit_reschedule`
  answer: Pedido de visita atualizado com a fila de admissoes. - Protocolo: VIS-20260401-A20A17 - Ticket operacional: ATD-20260401-00507DC5 - Nova preferencia: quinta-feira - tarde (02/04/2026 - 14:30) Proximo passo: admissions valida a nova janela e retorna com a confirmacao.
- `python_functions`: status 200, latency 296.5ms, keyword pass `True`, quality `100`, reason `consulta publica de navegacao e canais foi resgatada do dominio support`
  answer: Pedido de visita atualizado com a fila de admissions. Protocolo: VIS-20260401-D093B9. Ticket operacional: ATD-20260401-E176B8D1. Nova preferencia: quinta-feira - tarde (02/04/2026 - 14:30). Admissions valida a nova janela e retorna com a confirmacao.
- `llamaindex`: status 200, latency 294.3ms, keyword pass `True`, quality `100`, reason `consulta publica de navegacao e canais foi resgatada do dominio support`
  answer: Pedido de visita atualizado com a fila de admissions. Protocolo: VIS-20260401-E59BD1. Ticket operacional: ATD-20260401-235F5D1F. Nova preferencia: quinta-feira - tarde (02/04/2026 - 14:30). Admissions valida a nova janela e retorna com a confirmacao.
- `specialist_supervisor`: status 200, latency 133.1ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_tool_first:visit_reschedule`
  answer: Pedido de visita atualizado. Protocolo: VIS-20260401-30EAE9. Nova preferencia: quinta-feira, 14:30. Admissions valida a nova janela e retorna com a confirmacao.

### Qual e o protocolo dessa visita?

- Slice: `workflow`
- Thread: `system_bank:workflow_protocolos_visitas_e_handoff:Q073` turn `3`
- `langgraph`: status 200, latency 202.7ms, keyword pass `True`, quality `100`, reason `workflow_follow_up_rescue:visit_update`
  answer: Nao consegui atualizar a visita agora. Se quiser, me passe novamente o protocolo da visita ou o novo horario desejado.
- `crewai`: status 200, latency 212.5ms, keyword pass `True`, quality `100`, reason `workflow_protocol_lookup`
  answer: O protocolo da sua visita e VIS-20260401-A20A17. - Ticket operacional: ATD-20260401-00507DC5 - Preferencia registrada: quinta-feira - 14:30 (02/04/2026 - 14:30) Se quiser, eu tambem posso te dizer o status, remarcar ou cancelar a visita.
- `python_functions`: status 200, latency 239.6ms, keyword pass `True`, quality `100`, reason `python_functions_native_structured:support`
  answer: Solicitacao institucional registrada para direcao. Protocolo: REQ-20260401-A805DD. Assunto: Qual e o protocolo dessa visita? Fila responsavel: direcao. Ticket operacional: ATD-20260401-E176B8D1. A equipe faz a triagem inicial e segue o retorno pelo fluxo institucional.
- `llamaindex`: status 200, latency 245.9ms, keyword pass `True`, quality `100`, reason `consulta publica de navegacao e canais foi resgatada do dominio support`
  answer: Solicitacao institucional registrada para direcao. Protocolo: REQ-20260401-50F699. Assunto: Qual e o protocolo dessa visita? Fila responsavel: direcao. Ticket operacional: ATD-20260401-235F5D1F. A equipe faz a triagem inicial e segue o retorno pelo fluxo institucional.
- `specialist_supervisor`: status 200, latency 18353.4ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_direct:workflow_specialist`
  answer: Sua solicitação de atendimento foi recebida. Um de nossos atendentes entrará em contato em breve para auxiliar com o protocolo da visita.

### Preciso remarcar para a semana que vem.

- Slice: `workflow`
- Thread: `system_bank:workflow_protocolos_visitas_e_handoff:Q073` turn `4`
- `langgraph`: status 200, latency 1791.6ms, keyword pass `True`, quality `100`, reason `a intencao esta ambigua e exige clarificacao antes de recuperar contexto`
  answer: Para remarcar sua visita para a semana que vem, por favor, me informe o protocolo da visita ou o novo horário desejado. Assim consigo ajudar a equipe de admissões a fazer a alteração.
- `crewai`: status 200, latency 258.2ms, keyword pass `True`, quality `100`, reason `workflow_visit_reschedule`
  answer: Pedido de visita atualizado com a fila de admissoes. - Protocolo: VIS-20260401-A20A17 - Ticket operacional: ATD-20260401-00507DC5 - Nova preferencia: quinta-feira - 14:30 (09/04/2026 - 14:30) Proximo passo: admissions valida a nova janela e retorna com a confirmacao.
- `python_functions`: status 200, latency 221.1ms, keyword pass `True`, quality `100`, reason `a intencao esta ambigua e exige clarificacao antes de recuperar contexto`
  answer: Posso ajudar com informacoes publicas da escola, como calendario, matricula, documentos exigidos e regras de atendimento digital. Se quiser, pergunte por exemplo: "quais documentos preciso para a matricula?" ou "quando acontece a reuniao de pais?".
- `llamaindex`: status 200, latency 4365.2ms, keyword pass `True`, quality `100`, reason `llamaindex_public_profile`
  answer: Hoje o Colegio Horizonte publica estas janelas de visita:
- Visita guiada ao campus: terca-feira, das 09:00 as 10:15, em Recepcao principal e circuito pedagogico. Inclui apresentacao institucional, visita aos espacos e conversa curta com admissions.
- Visita guiada com foco pedagogico: quinta-feira, das 14:30 as 15:45, em Recepcao principal e salas de projeto. Janela pensada para familias que desejam conhecer infraestrutura, rotina e proposta pedagogica.
Agendamento: bot, whatsapp comercial ou admissions. Prazo de confirmacao: confirmacao em ate 1 dia util.
- `specialist_supervisor`: status 200, latency 121.6ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_tool_first:visit_reschedule_guidance`
  answer: Para remarcar a visita, eu sigo pelo protocolo VIS-20260401-30EAE9. A preferencia atual registrada e 02/04/2026 - 14:30. Me diga o novo dia ou janela desejada e eu atualizo o pedido. Ticket operacional: ATD-20260401-90D3FDC9.

### Agora cancela, por favor.

- Slice: `workflow`
- Thread: `system_bank:workflow_protocolos_visitas_e_handoff:Q073` turn `5`
- `langgraph`: status 200, latency 201.7ms, keyword pass `True`, quality `100`, reason `workflow_follow_up_rescue:visit_update`
  answer: Nao consegui atualizar a visita agora. Se quiser, me passe novamente o protocolo da visita ou o novo horario desejado.
- `crewai`: status 200, latency 10702.5ms, keyword pass `True`, quality `100`, reason `crewai_public_flow_completed`
  answer: O que você gostaria de cancelar?
- `python_functions`: status 200, latency 297.8ms, keyword pass `True`, quality `100`, reason `consulta publica de navegacao e canais foi resgatada do dominio support`
  answer: Nao consegui atualizar a visita agora. Se quiser, me passe novamente o protocolo da visita ou o novo horario desejado.
- `llamaindex`: status 200, latency 2582.6ms, keyword pass `True`, quality `100`, reason `llamaindex_public_profile`
  answer: Hoje e 1 de abril de 2026.
- `specialist_supervisor`: status 200, latency 6668.1ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_direct:workflow_specialist`
  answer: Para cancelar, preciso do código do protocolo. Você pode me informar qual é o código e o que você gostaria de cancelar?

### Preciso emitir documentos finais e concluir a transferencia do Diego.

- Slice: `workflow`
- Thread: `system_bank:workflow_protocolos_visitas_e_handoff:Q078` turn `1`
- `langgraph`: status 200, latency 147.1ms, keyword pass `True`, quality `100`, reason `status administrativo autenticado exige service deterministico`
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
- `python_functions`: status 200, latency 120.9ms, keyword pass `True`, quality `100`, reason `python_functions_native_structured:institution`
  answer: Hoje os documentos exigidos para a matricula publicados pela escola sao:
- Formulario cadastral preenchido
- Documento de identificacao do aluno
- CPF do aluno, quando houver
- Historico escolar
- Comprovante de residencia atualizado
- Documento de identificacao do responsavel legal
Se quiser, eu tambem posso explicar as etapas da matricula ou como funciona o envio inicial desses documentos.
- `llamaindex`: status 200, latency 150.0ms, keyword pass `True`, quality `100`, reason `status administrativo autenticado exige service deterministico`
  answer: Hoje os documentos exigidos para a matricula publicados pela escola sao:
- Formulario cadastral preenchido
- Documento de identificacao do aluno
- CPF do aluno, quando houver
- Historico escolar
- Comprovante de residencia atualizado
- Documento de identificacao do responsavel legal
Se quiser, eu tambem posso explicar as etapas da matricula ou como funciona o envio inicial desses documentos.
- `specialist_supervisor`: status 200, latency 146.1ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_tool_first:human_handoff`
  answer: Encaminhei sua solicitacao para a fila de secretaria. Protocolo: ATD-20260401-711908BD. Status atual: queued. Se preferir, voce tambem pode seguir pelo WhatsApp oficial (11) 97500-2040.

### Quero abrir um atendimento com o financeiro para negociar uma mensalidade parcialmente paga.

- Slice: `workflow`
- Thread: `system_bank:workflow_protocolos_visitas_e_handoff:Q079` turn `1`
- `langgraph`: status 200, latency 268.0ms, keyword pass `True`, quality `100`, reason `o turno atual trouxe pistas explicitas de outro dominio protegido e o roteamento foi corrigido`
  answer: Resumo financeiro das contas vinculadas:
- Total de faturas em aberto: 3
- Total de faturas vencidas: 0
- Lucas Oliveira: 1 em aberto, 0 vencidas
  2026-01: vencimento 2026-01-10, status paga, valor 1450.00
  2026-02: vencimento 2026-02-10, status paga, valor 1450.00
- Ana Oliveira: 2 em aberto, 0 vencidas
  2026-01: vencimento 2026-01-10, status paga, valor 1450.00
  2026-02: vencimento 2026-02-10, status paga, valor 1450.00
- `crewai`: status 200, latency 226.8ms, keyword pass `True`, quality `100`, reason `protected_shadow_needs_student_clarification`
  answer: Posso te ajudar com Lucas Oliveira, Ana Oliveira. Me diga qual aluno voce quer consultar.
- `python_functions`: status 200, latency 181.6ms, keyword pass `True`, quality `100`, reason `python_functions_native_structured:institution`
  answer: Valores publicos de referencia para 2026:
- Ensino Fundamental II (Manha): mensalidade R$ 1.280,00 e taxa de matricula R$ 350,00. Valor comercial publico de referencia para 2026. Material didatico e uniforme sao cobrados a parte.
- Ensino Medio (Manha): mensalidade R$ 1.450,00 e taxa de matricula R$ 350,00. Valor comercial publico de referencia para 2026. Ha politica comercial para irmaos e pagamento pontual.
- Periodo integral opcional (Complemento contraturno): mensalidade R$ 480,00 e taxa de matricula R$ 0,00. Adicional mensal aplicado ao estudante matriculado no turno regular que aderir ao periodo integral.
Se quiser, eu tambem posso resumir bolsas, descontos comerciais e canais de matricula.
- `llamaindex`: status 200, latency 3322.5ms, keyword pass `True`, quality `100`, reason `llamaindex_public_profile`
  answer: Valores publicos de referencia para 2026:
- Ensino Fundamental II (Manha): mensalidade R$ 1.280,00 e taxa de matricula R$ 350,00. Valor comercial publico de referencia para 2026. Material didatico e uniforme sao cobrados a parte.
- Ensino Medio (Manha): mensalidade R$ 1.450,00 e taxa de matricula R$ 350,00. Valor comercial publico de referencia para 2026. Ha politica comercial para irmaos e pagamento pontual.
- Periodo integral opcional (Complemento contraturno): mensalidade R$ 480,00 e taxa de matricula R$ 0,00. Adicional mensal aplicado ao estudante matriculado no turno regular que aderir ao periodo integral.
Se quiser, eu tambem posso resumir bolsas, descontos comerciais e canais de matricula.
- `specialist_supervisor`: status 200, latency 122.8ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_resolved_intent:finance_student_clarify`
  answer: Consigo verificar a situacao financeira, mas preciso que voce me diga qual aluno: Lucas Oliveira ou Ana Oliveira?

### Qual a diferenca entre abrir um protocolo, um chamado e um handoff humano?

- Slice: `workflow`
- Thread: `system_bank:workflow_protocolos_visitas_e_handoff:Q080` turn `1`
- `langgraph`: status 200, latency 196.1ms, keyword pass `True`, quality `100`, reason `o usuario demonstrou necessidade de atendimento humano ou operacional`
  answer: Encaminhei sua solicitacao para a fila de atendimento. Protocolo: ATD-20260401-85CA60F0. Status atual: queued. A equipe humana pode continuar esse atendimento no portal operacional.
- `crewai`: status 200, latency 278.9ms, keyword pass `True`, quality `100`, reason `support_handoff_created`
  answer: Encaminhei sua solicitacao para a fila de atendimento. Protocolo: ATD-20260401-2C33CC37. Status atual: queued. A equipe humana podera continuar esse atendimento no portal operacional.
- `python_functions`: status 200, latency 194.5ms, keyword pass `True`, quality `100`, reason `o usuario demonstrou necessidade de atendimento humano ou operacional`
  answer: Encaminhei sua solicitacao para a fila de atendimento. Protocolo: ATD-20260401-DB005DBD. Status atual: queued. A equipe humana pode continuar esse atendimento no portal operacional.
- `llamaindex`: status 200, latency 211.4ms, keyword pass `True`, quality `100`, reason `o usuario demonstrou necessidade de atendimento humano ou operacional`
  answer: Encaminhei sua solicitacao para a fila de atendimento. Protocolo: ATD-20260401-5731F646. Status atual: queued. A equipe humana pode continuar esse atendimento no portal operacional.
- `specialist_supervisor`: status 200, latency 123.0ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_fast_path:support_process_boundary`
  answer: Hoje eu trato esses tres fluxos de forma diferente: protocolo registra uma solicitacao institucional rastreavel; chamado costuma ser o ticket operacional associado ao atendimento; e handoff humano e o encaminhamento real para uma fila ou equipe, normalmente com protocolo e status para acompanhamento.

