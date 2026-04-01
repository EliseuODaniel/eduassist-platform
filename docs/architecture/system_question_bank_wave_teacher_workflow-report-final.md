# Five-Path Chatbot Comparison Report

Date: 2026-04-01T05:24:41.176898+00:00

Dataset: `tests/evals/datasets/system_question_bank_wave_teacher_workflow.json`

Run prefix: `debug:five-path:20260401T052003Z`

## Stack Summary

| Stack | OK | Keyword pass | Quality | Avg latency |
| --- | --- | --- | --- | --- |
| `langgraph` | `16/16` | `16/16` | `99.4` | `1372.3 ms` |
| `python_functions` | `16/16` | `16/16` | `99.4` | `1772.2 ms` |
| `llamaindex` | `16/16` | `16/16` | `99.4` | `4375.4 ms` |
| `crewai` | `16/16` | `16/16` | `97.5` | `143.4 ms` |
| `specialist_supervisor` | `16/16` | `16/16` | `100.0` | `9655.8 ms` |

## By Slice

- `protected`
  - `langgraph`: ok 7/7, keyword pass 7/7, quality 98.6, latency 690.7ms
  - `python_functions`: ok 7/7, keyword pass 7/7, quality 98.6, latency 3762.2ms
  - `llamaindex`: ok 7/7, keyword pass 7/7, quality 98.6, latency 2315.5ms
  - `crewai`: ok 7/7, keyword pass 7/7, quality 98.6, latency 144.4ms
  - `specialist_supervisor`: ok 7/7, keyword pass 7/7, quality 100.0, latency 19201.4ms
- `public`
  - `langgraph`: ok 1/1, keyword pass 1/1, quality 100.0, latency 3648.4ms
  - `python_functions`: ok 1/1, keyword pass 1/1, quality 100.0, latency 211.8ms
  - `llamaindex`: ok 1/1, keyword pass 1/1, quality 100.0, latency 10098.6ms
  - `crewai`: ok 1/1, keyword pass 1/1, quality 100.0, latency 143.7ms
  - `specialist_supervisor`: ok 1/1, keyword pass 1/1, quality 100.0, latency 6914.5ms
- `workflow`
  - `langgraph`: ok 8/8, keyword pass 8/8, quality 100.0, latency 1684.2ms
  - `python_functions`: ok 8/8, keyword pass 8/8, quality 100.0, latency 225.9ms
  - `llamaindex`: ok 8/8, keyword pass 8/8, quality 100.0, latency 5462.3ms
  - `crewai`: ok 8/8, keyword pass 8/8, quality 96.2, latency 142.4ms
  - `specialist_supervisor`: ok 8/8, keyword pass 8/8, quality 100.0, latency 1646.1ms

## Error Types

- `langgraph`: repetitive_reply=1
- `python_functions`: repetitive_reply=1
- `llamaindex`: repetitive_reply=1
- `crewai`: repetitive_reply=4
- `specialist_supervisor`: nenhum

## Prompt Results

### Quais turmas e disciplinas eu tenho neste ano?

- Slice: `protected`
- Thread: `system_bank:professor_e_grade_docente:Q065` turn `1`
- `langgraph`: status 200, latency 324.0ms, keyword pass `True`, quality `100`, reason `teacher_role_rescue`
  answer: Voce esta falando aqui como Fernando Azevedo, no perfil de professor do Colegio Horizonte. No Telegram, nesta etapa eu consigo consultar sua grade docente, turmas e disciplinas. A situacao individual dos alunos ainda nao esta liberada por este canal. Se quiser, me pergunte "qual meu horario?", "quais sao minhas turmas?" ou "quais disciplinas eu ministro?".
- `python_functions`: status 200, latency 5205.1ms, keyword pass `True`, quality `100`, reason `python_functions_native_teacher_schedule`
  answer: Nao consegui consultar sua grade docente agora. Tente novamente em instantes.
- `llamaindex`: status 200, latency 152.9ms, keyword pass `True`, quality `100`, reason `dados estruturados devem passar por service deterministico`
  answer: Voce esta falando aqui como Fernando Azevedo, no perfil de professor do Colegio Horizonte. No Telegram, nesta etapa eu consigo consultar sua grade docente, turmas e disciplinas. A situacao individual dos alunos ainda nao esta liberada por este canal. Se quiser, me pergunte "qual meu horario?", "quais sao minhas turmas?" ou "quais disciplinas eu ministro?".
- `crewai`: status 200, latency 142.5ms, keyword pass `True`, quality `100`, reason `crewai_primary_strict_safe_fallback`
  answer: Nao consegui consolidar essa consulta com seguranca agora. Se quiser, me diga exatamente se voce quer ver notas, frequencia, documentacao ou financeiro.
- `specialist_supervisor`: status 200, latency 12246.2ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_direct:academic_specialist`
  answer: Você, Fernando Azevedo, tem as seguintes turmas e disciplinas neste ano:

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
- `langgraph`: status 200, latency 144.8ms, keyword pass `True`, quality `100`, reason `teacher_role_rescue`
  answer: Voce esta falando aqui como Fernando Azevedo, no perfil de professor do Colegio Horizonte. No Telegram, nesta etapa eu consigo consultar sua grade docente, turmas e disciplinas. A situacao individual dos alunos ainda nao esta liberada por este canal. Se quiser, me pergunte "qual meu horario?", "quais sao minhas turmas?" ou "quais disciplinas eu ministro?".
- `python_functions`: status 200, latency 5197.4ms, keyword pass `True`, quality `100`, reason `python_functions_native_teacher_schedule`
  answer: Nao consegui consultar sua grade docente agora. Tente novamente em instantes.
- `llamaindex`: status 200, latency 5198.4ms, keyword pass `True`, quality `100`, reason `llamaindex_teacher_schedule_direct`
  answer: Nao consegui consultar sua grade docente agora. Tente novamente em instantes.
- `crewai`: status 200, latency 139.8ms, keyword pass `True`, quality `100`, reason `crewai_primary_strict_safe_fallback`
  answer: Nao consegui consolidar essa consulta com seguranca agora. Se quiser, me diga exatamente se voce quer ver notas, frequencia, documentacao ou financeiro.
- `specialist_supervisor`: status 200, latency 6664.3ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_fast_path:general_knowledge`
  answer: Prefiro não responder a perguntas que envolvam informações pessoais ou específicas de um contexto individual.

### E so do ensino medio?

- Slice: `protected`
- Thread: `system_bank:professor_e_grade_docente:Q066` turn `2`
- `langgraph`: status 200, latency 178.8ms, keyword pass `True`, quality `90`, reason `teacher_role_rescue`
  errors: repetitive_reply
  answer: Voce esta falando aqui como Fernando Azevedo, no perfil de professor do Colegio Horizonte. No Telegram, nesta etapa eu consigo consultar sua grade docente, turmas e disciplinas. A situacao individual dos alunos ainda nao esta liberada por este canal. Se quiser, me pergunte "qual meu horario?", "quais sao minhas turmas?" ou "quais disciplinas eu ministro?".
- `python_functions`: status 200, latency 5228.1ms, keyword pass `True`, quality `90`, reason `python_functions_native_teacher_schedule`
  errors: repetitive_reply
  answer: Nao consegui consultar sua grade docente agora. Tente novamente em instantes.
- `llamaindex`: status 200, latency 5223.6ms, keyword pass `True`, quality `90`, reason `llamaindex_teacher_schedule_direct`
  errors: repetitive_reply
  answer: Nao consegui consultar sua grade docente agora. Tente novamente em instantes.
- `crewai`: status 200, latency 144.4ms, keyword pass `True`, quality `90`, reason `crewai_primary_strict_safe_fallback`
  errors: repetitive_reply
  answer: Nao consegui consolidar essa consulta com seguranca agora. Se quiser, me diga exatamente se voce quer ver notas, frequencia, documentacao ou financeiro.
- `specialist_supervisor`: status 200, latency 13723.1ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_direct:institution_specialist`
  answer: Não, o Colégio Horizonte oferece o Ensino Fundamental II (do 6º ao 9º ano) e o Ensino Médio (da 1ª à 3ª série).

### Quais turmas eu atendo em Filosofia e em que classes?

- Slice: `protected`
- Thread: `system_bank:professor_e_grade_docente:Q068` turn `1`
- `langgraph`: status 200, latency 126.0ms, keyword pass `True`, quality `100`, reason `teacher_role_rescue`
  answer: Voce esta falando aqui como Fernando Azevedo, no perfil de professor do Colegio Horizonte. No Telegram, nesta etapa eu consigo consultar sua grade docente, turmas e disciplinas. A situacao individual dos alunos ainda nao esta liberada por este canal. Se quiser, me pergunte "qual meu horario?", "quais sao minhas turmas?" ou "quais disciplinas eu ministro?".
- `python_functions`: status 200, latency 5187.6ms, keyword pass `True`, quality `100`, reason `python_functions_native_teacher_schedule`
  answer: Nao consegui consultar sua grade docente agora. Tente novamente em instantes.
- `llamaindex`: status 200, latency 147.8ms, keyword pass `True`, quality `100`, reason `dados estruturados devem passar por service deterministico`
  answer: Voce esta falando aqui como Fernando Azevedo, no perfil de professor do Colegio Horizonte. No Telegram, nesta etapa eu consigo consultar sua grade docente, turmas e disciplinas. A situacao individual dos alunos ainda nao esta liberada por este canal. Se quiser, me pergunte "qual meu horario?", "quais sao minhas turmas?" ou "quais disciplinas eu ministro?".
- `crewai`: status 200, latency 146.2ms, keyword pass `True`, quality `100`, reason `crewai_primary_strict_safe_fallback`
  answer: Nao consegui consolidar essa consulta com seguranca agora. Se quiser, me diga exatamente se voce quer ver notas, frequencia, documentacao ou financeiro.
- `specialist_supervisor`: status 200, latency 5127.8ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_resolved_intent:shift_offers`
  answer: Hoje o Colegio Horizonte publica estes turnos de atendimento escolar:
- Ensino Fundamental II: Manha (07:15 as 12:30).
- Ensino Medio: Manha (07:15 as 12:50).
- Fundamental II e Ensino Medio: Integral opcional (07:00 as 17:30).

### Resuma minha rotina docente junto com orientacoes publicas sobre calendario e comunicacao escolar.

- Slice: `protected`
- Thread: `system_bank:professor_e_grade_docente:Q069` turn `1`
- `langgraph`: status 200, latency 2036.7ms, keyword pass `True`, quality `100`, reason `teacher_role_rescue`
  answer: Voce esta falando aqui como Fernando Azevedo, no perfil de professor do Colegio Horizonte. No Telegram, nesta etapa eu consigo consultar sua grade docente, turmas e disciplinas. A situacao individual dos alunos ainda nao esta liberada por este canal. Se quiser, me pergunte "qual meu horario?", "quais sao minhas turmas?" ou "quais disciplinas eu ministro?".
- `python_functions`: status 200, latency 5216.2ms, keyword pass `True`, quality `100`, reason `python_functions_native_teacher_schedule`
  answer: Nao consegui consultar sua grade docente agora. Tente novamente em instantes.
- `llamaindex`: status 200, latency 5194.4ms, keyword pass `True`, quality `100`, reason `llamaindex_teacher_schedule_direct`
  answer: Nao consegui consultar sua grade docente agora. Tente novamente em instantes.
- `crewai`: status 200, latency 153.8ms, keyword pass `True`, quality `100`, reason `crewai_primary_strict_safe_fallback`
  answer: Nao consegui consolidar essa consulta com seguranca agora. Se quiser, me diga exatamente se voce quer ver notas, frequencia, documentacao ou financeiro.
- `specialist_supervisor`: status 200, latency 72433.2ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_manager_judge:academic:structured_tools`
  answer: Sua rotina docente é estruturada dentro dos horários públicos do Colégio Horizonte, com as seguintes orientações gerais de calendário e comunicação:

**Rotina Docente (Orientações Públicas de Horário):**
*   **Ensino Fundamental II (6º ao 9º ano):** O turno regular da manhã ocorre das 07h15 às 12h30, com intervalo das 09h35 às 09h55. Atividades de contraturno, como oficinas, plantões, esportes e estudo orientado, são oferecidas em dias alternados.
*   **Ensino Médio (1ª a 3ª série):** O turno regular da manhã vai das 07h15 às 12h50, com intervalo das 09h40 às 10h00. O contraturno, a partir das 14h00, inclui trilhas eletivas, monitorias e laboratórios.
*   **Período Integral Opcional:** Para estudantes que aderem, o período integral vai das 07h00 às 17h30, com pausa para almoço e convívio das 12h50 às 13h40. Esta opção organiza um dia estendido com estudo orientado, almoço, oficinas, esportes e acompanhamento.

**Orientações Públicas sobre o Calendário Escolar (Ano Letivo 2026):**
O calendário público do Colégio Horizonte destaca os seguintes eventos e marcos:
*   **Início das aulas:** 02 de fevereiro de 2026 para Ensino Fundamental II e Ensino Médio.
*   **Reunião geral de pais e responsáveis:** 28 de março de 2026, com apresentações específicas para Fundamental II (28 de março) e Ensino Médio (29 de março).
*   **Plantão pedagógico do primeiro bimestre:** 11 de abril de 2026, para atendimento com professores sobre notas e frequência.
*   **Mostra de Ciências e Tecnologia / Mostra de Projetos e Feira de Ciências:** Eventos públicos previstos para 16 e 23 de maio de 2026.
*   **Feira de Orientação Acadêmica e Vocacional:** 06 de junho de 2026.
*   **Festival Esportivo da Comunidade Escolar:** 13 de junho de 2026.

**Orientações Públicas sobre Comunicação Escolar:**
Embora não haja um documento específico público denominado 'orientações de comunicação escolar para professores' em nossos registros, a comunicação institucional é facilitada através de diversos canais e serviços que também se aplicam aos docentes:
*   **Canais de Contato:** A escola disponibiliza canais de telefone (Secretaria, Orientação Educacional, Financeiro), WhatsApp (Secretaria digital) e e-mail (Secretaria, Orientação Educacional, Financeiro, Direção, Suporte Digital) para diferentes necessidades de comunicação.
*   **Suporte Digital:** Existe um serviço de Suporte de portal, acesso e atendimento digital que atende professores, estudantes e famílias, com retorno em até 1 dia útil.
*   **Secretaria Escolar:** Para assuntos administrativos e documentação, a Secretaria Escolar pode ser contatada via bot, presencialmente, por e-mail institucional ou pelo portal.
*   **Reunião com Coordenação Pedagógica:** Para discussões sobre rotina e acompanhamento escolar, é possível agendar reuniões com a coordenação pedagógica.
*   **Política de Submissão de Documentos:** A escola aceita o envio digital de documentos através do portal institucional ou do e-mail da secretaria, com a ressalva de não enviar dados sensíveis ou documentos completos via chat aberto.

Em resumo, sua rotina é moldada pelos horários de turno e calendário acadêmico, e a comunicação é suportada pelos canais institucionais e serviços listados.

### Sou professor de Filosofia e quero trabalhar ai; como faco para entrar em contato?

- Slice: `public`
- Thread: `system_bank:professor_e_grade_docente:Q070` turn `1`
- `langgraph`: status 200, latency 3648.4ms, keyword pass `True`, quality `100`, reason `fato institucional canonico deve vir de fonte estruturada`
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
- `python_functions`: status 200, latency 211.8ms, keyword pass `True`, quality `100`, reason `python_functions_native_structured:institution`
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
- `llamaindex`: status 200, latency 10098.6ms, keyword pass `True`, quality `100`, reason `llamaindex_public_profile`
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
- `crewai`: status 200, latency 143.7ms, keyword pass `True`, quality `100`, reason `crewai_primary_strict_safe_fallback`
  answer: Nao consegui concluir essa resposta agora pelo caminho principal configurado. Tente reformular em uma frase mais direta ou repetir em instantes.
- `specialist_supervisor`: status 200, latency 6914.5ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_direct:institution_specialist`
  answer: Para entrar em contato sobre oportunidades de trabalho como professor de Filosofia, você pode enviar seu currículo para o e-mail de talentos do Colégio Horizonte: **talentos@colegiohorizonte.edu.br**. A equipe de talentos recebe currículos e orienta sobre os processos seletivos quando há vagas abertas, com um prazo de retorno de até 5 dias úteis.

### Me diga o nome e o telefone do professor de Educacao Fisica.

- Slice: `protected`
- Thread: `system_bank:professor_e_grade_docente:Q071` turn `1`
- `langgraph`: status 200, latency 201.8ms, keyword pass `True`, quality `100`, reason `status administrativo autenticado exige service deterministico`
  answer: Essa consulta depende de autenticacao e vinculo da sua conta no Telegram. Use o portal da escola para gerar o codigo de vinculacao e depois envie o comando `/start link_<codigo>` ao bot.
- `python_functions`: status 200, latency 170.7ms, keyword pass `True`, quality `100`, reason `python_functions_native_structured:institution`
  answer: Essa consulta depende de autenticacao e vinculo da sua conta no Telegram. Use o portal da escola para gerar o codigo de vinculacao e depois envie o comando `/start link_<codigo>` ao bot.
- `llamaindex`: status 200, latency 166.9ms, keyword pass `True`, quality `100`, reason `status administrativo autenticado exige service deterministico`
  answer: Essa consulta depende de autenticacao e vinculo da sua conta no Telegram. Use o portal da escola para gerar o codigo de vinculacao e depois envie o comando `/start link_<codigo>` ao bot.
- `crewai`: status 200, latency 145.0ms, keyword pass `True`, quality `100`, reason `crewai_primary_strict_safe_fallback`
  answer: Nao consegui consolidar essa consulta com seguranca agora. Se quiser, me diga exatamente se voce quer ver notas, frequencia, documentacao ou financeiro.
- `specialist_supervisor`: status 200, latency 7980.2ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_direct:institution_specialist`
  answer: Não tenho a informação específica sobre o nome e o telefone do professor de Educação Física. O perfil institucional público não detalha os contatos individuais dos professores.

### Gere um resumo enxuto da minha alocacao para eu revisar antes da reuniao pedagogica.

- Slice: `protected`
- Thread: `system_bank:professor_e_grade_docente:Q072` turn `1`
- `langgraph`: status 200, latency 1822.8ms, keyword pass `True`, quality `100`, reason `teacher_role_rescue`
  answer: Voce esta falando aqui como Fernando Azevedo, no perfil de professor do Colegio Horizonte. No Telegram, nesta etapa eu consigo consultar sua grade docente, turmas e disciplinas. A situacao individual dos alunos ainda nao esta liberada por este canal. Se quiser, me pergunte "qual meu horario?", "quais sao minhas turmas?" ou "quais disciplinas eu ministro?".
- `python_functions`: status 200, latency 130.6ms, keyword pass `True`, quality `100`, reason `python_functions_native_teacher_scope_guidance`
  answer: Voce esta falando aqui como Fernando Azevedo, no perfil de professor do Colegio Horizonte. No Telegram, nesta etapa eu consigo consultar sua grade docente, turmas e disciplinas. A situacao individual dos alunos ainda nao esta liberada por este canal. Se quiser, me pergunte "qual meu horario?", "quais sao minhas turmas?" ou "quais disciplinas eu ministro?".
- `llamaindex`: status 200, latency 124.8ms, keyword pass `True`, quality `100`, reason `llamaindex_teacher_scope_guidance`
  answer: Voce esta falando aqui como Fernando Azevedo, no perfil de professor do Colegio Horizonte. No Telegram, nesta etapa eu consigo consultar sua grade docente, turmas e disciplinas. A situacao individual dos alunos ainda nao esta liberada por este canal. Se quiser, me pergunte "qual meu horario?", "quais sao minhas turmas?" ou "quais disciplinas eu ministro?".
- `crewai`: status 200, latency 139.1ms, keyword pass `True`, quality `100`, reason `crewai_primary_strict_safe_fallback`
  answer: Nao consegui concluir essa resposta agora pelo caminho principal configurado. Tente reformular em uma frase mais direta ou repetir em instantes.
- `specialist_supervisor`: status 200, latency 16235.1ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_multi_direct:academic_specialist+workflow_specialist`
  answer: Acadêmico:
- Não consigo gerar um resumo da sua alocação. Minhas funcionalidades são restritas a informações sobre notas, frequência, provas futuras e aprovação.

Atendimento: Sua solicitação para um resumo de alocação para revisão antes da reunião pedagógica foi encaminhada para a Coordenação Pedagógica. O número do seu protocolo de atendimento é ATD-20260401-D26870DA. A equipe responsável entrará em contato em breve para fornecer as informações solicitadas.

### Quero agendar uma visita para conhecer a escola.

- Slice: `workflow`
- Thread: `system_bank:workflow_protocolos_visitas_e_handoff:Q073` turn `1`
- `langgraph`: status 200, latency 221.9ms, keyword pass `True`, quality `100`, reason `consulta publica de navegacao e canais foi resgatada do dominio support`
  answer: Pedido de visita registrado para o Colegio Horizonte. Protocolo: VIS-20260401-B93809. Preferencia informada: janela a confirmar. Fila responsavel: admissoes. Ticket operacional: ATD-20260401-64EDEE1C. A equipe comercial valida a janela e retorna com a confirmacao.
- `python_functions`: status 200, latency 217.2ms, keyword pass `True`, quality `100`, reason `python_functions_native_structured:support`
  answer: Pedido de visita registrado para o Colegio Horizonte. Protocolo: VIS-20260401-6D0DFF. Preferencia informada: janela a confirmar. Fila responsavel: admissoes. Ticket operacional: ATD-20260401-492F132A. A equipe comercial valida a janela e retorna com a confirmacao.
- `llamaindex`: status 200, latency 208.3ms, keyword pass `True`, quality `100`, reason `consulta publica de navegacao e canais foi resgatada do dominio support`
  answer: Pedido de visita registrado para o Colegio Horizonte. Protocolo: VIS-20260401-1F1238. Preferencia informada: janela a confirmar. Fila responsavel: admissoes. Ticket operacional: ATD-20260401-8E4683FD. A equipe comercial valida a janela e retorna com a confirmacao.
- `crewai`: status 200, latency 120.7ms, keyword pass `True`, quality `100`, reason `crewai_primary_strict_safe_fallback`
  answer: Nao consegui concluir essa acao agora. Se quiser, me diga se voce quer consultar status, protocolo, remarcar ou cancelar.
- `specialist_supervisor`: status 200, latency 102.9ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_tool_first:visit_booking`
  answer: Pedido de visita registrado. Protocolo: VIS-20260401-DCDDB8. Preferencia registrada: janela a confirmar. Ticket operacional: ATD-20260401-912E4826. Se quiser, eu tambem posso acompanhar o status ou remarcar a visita.

### Pode ser na quinta a tarde?

- Slice: `workflow`
- Thread: `system_bank:workflow_protocolos_visitas_e_handoff:Q073` turn `2`
- `langgraph`: status 200, latency 212.5ms, keyword pass `True`, quality `100`, reason `workflow_follow_up_rescue:visit_update`
  answer: Pedido de visita atualizado com a fila de admissions. Protocolo: VIS-20260401-B93809. Ticket operacional: ATD-20260401-64EDEE1C. Nova preferencia: quinta-feira - tarde (02/04/2026 - 14:30). Admissions valida a nova janela e retorna com a confirmacao.
- `python_functions`: status 200, latency 293.8ms, keyword pass `True`, quality `100`, reason `consulta publica de navegacao e canais foi resgatada do dominio support`
  answer: Pedido de visita atualizado com a fila de admissions. Protocolo: VIS-20260401-6D0DFF. Ticket operacional: ATD-20260401-492F132A. Nova preferencia: quinta-feira - tarde (02/04/2026 - 14:30). Admissions valida a nova janela e retorna com a confirmacao.
- `llamaindex`: status 200, latency 271.2ms, keyword pass `True`, quality `100`, reason `consulta publica de navegacao e canais foi resgatada do dominio support`
  answer: Pedido de visita atualizado com a fila de admissions. Protocolo: VIS-20260401-1F1238. Ticket operacional: ATD-20260401-8E4683FD. Nova preferencia: quinta-feira - tarde (02/04/2026 - 14:30). Admissions valida a nova janela e retorna com a confirmacao.
- `crewai`: status 200, latency 135.7ms, keyword pass `True`, quality `90`, reason `crewai_primary_strict_safe_fallback`
  errors: repetitive_reply
  answer: Nao consegui concluir essa acao agora. Se quiser, me diga se voce quer consultar status, protocolo, remarcar ou cancelar.
- `specialist_supervisor`: status 200, latency 102.2ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_tool_first:visit_reschedule`
  answer: Pedido de visita atualizado. Protocolo: VIS-20260401-DCDDB8. Nova preferencia: quinta-feira, 14:30. Admissions valida a nova janela e retorna com a confirmacao.

### Qual e o protocolo dessa visita?

- Slice: `workflow`
- Thread: `system_bank:workflow_protocolos_visitas_e_handoff:Q073` turn `3`
- `langgraph`: status 200, latency 202.0ms, keyword pass `True`, quality `100`, reason `workflow_follow_up_rescue:visit_update`
  answer: Nao consegui atualizar a visita agora. Se quiser, me passe novamente o protocolo da visita ou o novo horario desejado.
- `python_functions`: status 200, latency 253.5ms, keyword pass `True`, quality `100`, reason `python_functions_native_structured:support`
  answer: Solicitacao institucional registrada para direcao. Protocolo: REQ-20260401-4BE6FF. Assunto: Qual e o protocolo dessa visita? Fila responsavel: direcao. Ticket operacional: ATD-20260401-492F132A. A equipe faz a triagem inicial e segue o retorno pelo fluxo institucional.
- `llamaindex`: status 200, latency 229.8ms, keyword pass `True`, quality `100`, reason `consulta publica de navegacao e canais foi resgatada do dominio support`
  answer: Solicitacao institucional registrada para direcao. Protocolo: REQ-20260401-A53618. Assunto: Qual e o protocolo dessa visita? Fila responsavel: direcao. Ticket operacional: ATD-20260401-8E4683FD. A equipe faz a triagem inicial e segue o retorno pelo fluxo institucional.
- `crewai`: status 200, latency 145.4ms, keyword pass `True`, quality `90`, reason `crewai_primary_strict_safe_fallback`
  errors: repetitive_reply
  answer: Nao consegui concluir essa acao agora. Se quiser, me diga se voce quer consultar status, protocolo, remarcar ou cancelar.
- `specialist_supervisor`: status 200, latency 6099.7ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_direct:workflow_specialist`
  answer: O protocolo da sua visita é **VIS-20260401-DCDDB8** e a situação atual é **queued**. A visita está agendada para o dia **02/04/2026 às 14:30**.

### Preciso remarcar para a semana que vem.

- Slice: `workflow`
- Thread: `system_bank:workflow_protocolos_visitas_e_handoff:Q073` turn `4`
- `langgraph`: status 200, latency 2060.3ms, keyword pass `True`, quality `100`, reason `a intencao esta ambigua e exige clarificacao antes de recuperar contexto`
  answer: Para remarcar sua visita, preciso do protocolo dela. Você poderia me informar o número do protocolo, por favor? Assim consigo verificar e te ajudar a agendar para a semana que vem.
- `python_functions`: status 200, latency 215.0ms, keyword pass `True`, quality `100`, reason `a intencao esta ambigua e exige clarificacao antes de recuperar contexto`
  answer: Posso ajudar com informacoes publicas da escola, como calendario, matricula, documentos exigidos e regras de atendimento digital. Se quiser, pergunte por exemplo: "quais documentos preciso para a matricula?" ou "quando acontece a reuniao de pais?".
- `llamaindex`: status 200, latency 6580.2ms, keyword pass `True`, quality `100`, reason `llamaindex_public_profile`
  answer: Hoje o Colegio Horizonte publica estas janelas de visita:
- Visita guiada ao campus: terca-feira, das 09:00 as 10:15, em Recepcao principal e circuito pedagogico. Inclui apresentacao institucional, visita aos espacos e conversa curta com admissions.
- Visita guiada com foco pedagogico: quinta-feira, das 14:30 as 15:45, em Recepcao principal e salas de projeto. Janela pensada para familias que desejam conhecer infraestrutura, rotina e proposta pedagogica.
Agendamento: bot, whatsapp comercial ou admissions. Prazo de confirmacao: confirmacao em ate 1 dia util.
- `crewai`: status 200, latency 129.9ms, keyword pass `True`, quality `90`, reason `crewai_primary_strict_safe_fallback`
  errors: repetitive_reply
  answer: Nao consegui concluir essa acao agora. Se quiser, me diga se voce quer consultar status, protocolo, remarcar ou cancelar.
- `specialist_supervisor`: status 200, latency 97.2ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_tool_first:visit_reschedule_guidance`
  answer: Para remarcar a visita, eu sigo pelo protocolo VIS-20260401-DCDDB8. A preferencia atual registrada e 02/04/2026 - 14:30. Me diga o novo dia ou janela desejada e eu atualizo o pedido. Ticket operacional: ATD-20260401-912E4826.

### Agora cancela, por favor.

- Slice: `workflow`
- Thread: `system_bank:workflow_protocolos_visitas_e_handoff:Q073` turn `5`
- `langgraph`: status 200, latency 192.6ms, keyword pass `True`, quality `100`, reason `workflow_follow_up_rescue:visit_update`
  answer: Nao consegui atualizar a visita agora. Se quiser, me passe novamente o protocolo da visita ou o novo horario desejado.
- `python_functions`: status 200, latency 347.0ms, keyword pass `True`, quality `100`, reason `consulta publica de navegacao e canais foi resgatada do dominio support`
  answer: Nao consegui atualizar a visita agora. Se quiser, me passe novamente o protocolo da visita ou o novo horario desejado.
- `llamaindex`: status 200, latency 32303.1ms, keyword pass `True`, quality `100`, reason `a intencao esta ambigua e exige clarificacao antes de recuperar contexto`
  answer: Posso ajudar com informacoes publicas da escola, como calendario, matricula, documentos exigidos e regras de atendimento digital. Se quiser, pergunte por exemplo: "quais documentos preciso para a matricula?" ou "quando acontece a reuniao de pais?".
- `crewai`: status 200, latency 146.2ms, keyword pass `True`, quality `100`, reason `crewai_primary_strict_safe_fallback`
  answer: Nao consegui concluir essa resposta agora pelo caminho principal configurado. Tente reformular em uma frase mais direta ou repetir em instantes.
- `specialist_supervisor`: status 200, latency 6486.2ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_direct:workflow_specialist`
  answer: Para que eu possa cancelar a sua visita, por favor, me informe o código do protocolo.

### Preciso emitir documentos finais e concluir a transferencia do Diego.

- Slice: `workflow`
- Thread: `system_bank:workflow_protocolos_visitas_e_handoff:Q078` turn `1`
- `langgraph`: status 200, latency 146.9ms, keyword pass `True`, quality `100`, reason `status administrativo autenticado exige service deterministico`
  answer: Hoje os documentos exigidos para a matricula publicados pela escola sao:
- Formulario cadastral preenchido
- Documento de identificacao do aluno
- CPF do aluno, quando houver
- Historico escolar
- Comprovante de residencia atualizado
- Documento de identificacao do responsavel legal
Se quiser, eu tambem posso explicar as etapas da matricula ou como funciona o envio inicial desses documentos.
- `python_functions`: status 200, latency 125.6ms, keyword pass `True`, quality `100`, reason `python_functions_native_structured:institution`
  answer: Hoje os documentos exigidos para a matricula publicados pela escola sao:
- Formulario cadastral preenchido
- Documento de identificacao do aluno
- CPF do aluno, quando houver
- Historico escolar
- Comprovante de residencia atualizado
- Documento de identificacao do responsavel legal
Se quiser, eu tambem posso explicar as etapas da matricula ou como funciona o envio inicial desses documentos.
- `llamaindex`: status 200, latency 125.7ms, keyword pass `True`, quality `100`, reason `status administrativo autenticado exige service deterministico`
  answer: Hoje os documentos exigidos para a matricula publicados pela escola sao:
- Formulario cadastral preenchido
- Documento de identificacao do aluno
- CPF do aluno, quando houver
- Historico escolar
- Comprovante de residencia atualizado
- Documento de identificacao do responsavel legal
Se quiser, eu tambem posso explicar as etapas da matricula ou como funciona o envio inicial desses documentos.
- `crewai`: status 200, latency 137.6ms, keyword pass `True`, quality `100`, reason `crewai_primary_strict_safe_fallback`
  answer: Nao consegui consolidar essa consulta com seguranca agora. Se quiser, me diga exatamente se voce quer ver notas, frequencia, documentacao ou financeiro.
- `specialist_supervisor`: status 200, latency 106.2ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_tool_first:human_handoff`
  answer: Encaminhei sua solicitacao para a fila de secretaria. Protocolo: ATD-20260401-F6F1B6B5. Status atual: queued. Se preferir, voce tambem pode seguir pelo WhatsApp oficial (11) 97500-2040.

### Quero abrir um atendimento com o financeiro para negociar uma mensalidade parcialmente paga.

- Slice: `workflow`
- Thread: `system_bank:workflow_protocolos_visitas_e_handoff:Q079` turn `1`
- `langgraph`: status 200, latency 10247.8ms, keyword pass `True`, quality `100`, reason `o turno atual trouxe pistas explicitas de outro dominio protegido e o roteamento foi corrigido`
  answer: Sua conta tem mais de um aluno vinculado. Diga qual aluno deseja consultar: Lucas Oliveira (MAT-2026-001), Ana Oliveira (MAT-2026-002).
- `python_functions`: status 200, latency 164.6ms, keyword pass `True`, quality `100`, reason `python_functions_native_structured:institution`
  answer: Valores publicos de referencia para 2026:
- Ensino Fundamental II (Manha): mensalidade R$ 1.280,00 e taxa de matricula R$ 350,00. Valor comercial publico de referencia para 2026. Material didatico e uniforme sao cobrados a parte.
- Ensino Medio (Manha): mensalidade R$ 1.450,00 e taxa de matricula R$ 350,00. Valor comercial publico de referencia para 2026. Ha politica comercial para irmaos e pagamento pontual.
- Periodo integral opcional (Complemento contraturno): mensalidade R$ 480,00 e taxa de matricula R$ 0,00. Adicional mensal aplicado ao estudante matriculado no turno regular que aderir ao periodo integral.
Se quiser, eu tambem posso resumir bolsas, descontos comerciais e canais de matricula.
- `llamaindex`: status 200, latency 3780.7ms, keyword pass `True`, quality `100`, reason `llamaindex_public_profile`
  answer: Valores publicos de referencia para 2026:
- Ensino Fundamental II (Manha): mensalidade R$ 1.280,00 e taxa de matricula R$ 350,00. Valor comercial publico de referencia para 2026. Material didatico e uniforme sao cobrados a parte.
- Ensino Medio (Manha): mensalidade R$ 1.450,00 e taxa de matricula R$ 350,00. Valor comercial publico de referencia para 2026. Ha politica comercial para irmaos e pagamento pontual.
- Periodo integral opcional (Complemento contraturno): mensalidade R$ 480,00 e taxa de matricula R$ 0,00. Adicional mensal aplicado ao estudante matriculado no turno regular que aderir ao periodo integral.
Se quiser, eu tambem posso resumir bolsas, descontos comerciais e canais de matricula.
- `crewai`: status 200, latency 193.0ms, keyword pass `True`, quality `100`, reason `crewai_primary_strict_safe_fallback`
  answer: Nao consegui consolidar essa consulta com seguranca agora. Se quiser, me diga exatamente se voce quer ver notas, frequencia, documentacao ou financeiro.
- `specialist_supervisor`: status 200, latency 101.1ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_resolved_intent:finance_student_clarify`
  answer: Consigo verificar a situacao financeira, mas preciso que voce me diga qual aluno: Lucas Oliveira ou Ana Oliveira?

### Qual a diferenca entre abrir um protocolo, um chamado e um handoff humano?

- Slice: `workflow`
- Thread: `system_bank:workflow_protocolos_visitas_e_handoff:Q080` turn `1`
- `langgraph`: status 200, latency 189.6ms, keyword pass `True`, quality `100`, reason `o usuario demonstrou necessidade de atendimento humano ou operacional`
  answer: Encaminhei sua solicitacao para a fila de atendimento. Protocolo: ATD-20260401-59F02483. Status atual: queued. A equipe humana pode continuar esse atendimento no portal operacional.
- `python_functions`: status 200, latency 190.8ms, keyword pass `True`, quality `100`, reason `o usuario demonstrou necessidade de atendimento humano ou operacional`
  answer: Encaminhei sua solicitacao para a fila de atendimento. Protocolo: ATD-20260401-E1F3A7B6. Status atual: queued. A equipe humana pode continuar esse atendimento no portal operacional.
- `llamaindex`: status 200, latency 199.7ms, keyword pass `True`, quality `100`, reason `o usuario demonstrou necessidade de atendimento humano ou operacional`
  answer: Encaminhei sua solicitacao para a fila de atendimento. Protocolo: ATD-20260401-963B168E. Status atual: queued. A equipe humana pode continuar esse atendimento no portal operacional.
- `crewai`: status 200, latency 130.7ms, keyword pass `True`, quality `100`, reason `crewai_primary_strict_safe_fallback`
  answer: Nao consegui concluir esse atendimento agora. Se quiser, eu posso tentar de novo ou voce pode me dizer se quer secretaria, financeiro, orientacao ou direcao.
- `specialist_supervisor`: status 200, latency 73.3ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_fast_path:support_process_boundary`
  answer: Hoje eu trato esses tres fluxos de forma diferente: protocolo registra uma solicitacao institucional rastreavel; chamado costuma ser o ticket operacional associado ao atendimento; e handoff humano e o encaminhamento real para uma fila ou equipe, normalmente com protocolo e status para acompanhamento.

