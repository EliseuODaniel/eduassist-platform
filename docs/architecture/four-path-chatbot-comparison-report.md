# Four-Path Chatbot Comparison Report

Date: 2026-03-30T20:45:31.192423+00:00

Dataset: `/home/edann/projects/eduassist-platform/artifacts/two_stack_random_strict_llm_live_20260327_v1_dataset.json`

Run prefix: `debug:four-path:20260330T204321Z`

## Stack Summary

| Stack | OK | Keyword pass | Quality | Avg latency |
| --- | --- | --- | --- | --- |
| `langgraph` | `32/32` | `31/32` | `98.8` | `189.1 ms` |
| `crewai` | `32/32` | `18/32` | `87.3` | `3599.6 ms` |
| `python_functions` | `32/32` | `32/32` | `100.0` | `135.4 ms` |
| `llamaindex` | `32/32` | `32/32` | `100.0` | `138.1 ms` |

## By Slice

- `protected`
  - `langgraph`: ok 10/10, keyword pass 10/10, quality 100.0, latency 142.1ms
  - `crewai`: ok 10/10, keyword pass 6/10, quality 82.3, latency 3822.9ms
  - `python_functions`: ok 10/10, keyword pass 10/10, quality 100.0, latency 153.0ms
  - `llamaindex`: ok 10/10, keyword pass 10/10, quality 100.0, latency 152.4ms
- `public`
  - `langgraph`: ok 10/10, keyword pass 9/10, quality 98.0, latency 303.6ms
  - `crewai`: ok 10/10, keyword pass 5/10, quality 89.0, latency 1659.6ms
  - `python_functions`: ok 10/10, keyword pass 10/10, quality 100.0, latency 118.3ms
  - `llamaindex`: ok 10/10, keyword pass 10/10, quality 100.0, latency 125.5ms
- `support`
  - `langgraph`: ok 5/5, keyword pass 5/5, quality 96.4, latency 130.1ms
  - `crewai`: ok 5/5, keyword pass 3/5, quality 90.0, latency 4831.1ms
  - `python_functions`: ok 5/5, keyword pass 5/5, quality 100.0, latency 123.5ms
  - `llamaindex`: ok 5/5, keyword pass 5/5, quality 100.0, latency 131.6ms
- `workflow`
  - `langgraph`: ok 7/7, keyword pass 7/7, quality 100.0, latency 135.1ms
  - `crewai`: ok 7/7, keyword pass 4/7, quality 90.0, latency 5172.4ms
  - `python_functions`: ok 7/7, keyword pass 7/7, quality 100.0, latency 143.3ms
  - `llamaindex`: ok 7/7, keyword pass 7/7, quality 100.0, latency 140.1ms

## Error Types

- `langgraph`: missing_expected_keyword=1, repair_miss=1
- `crewai`: followup_context_drop=3, missing_expected_keyword=14, repetitive_reply=4, unnecessary_clarification=1
- `python_functions`: nenhum
- `llamaindex`: nenhum

## Prompt Results

### sendo bem sincero, por que eu colocaria meu filho ai e nao na publica?

- Slice: `public`
- Thread: `rand_public_value_compare` turn `1`
- `langgraph`: status 200, latency 181.7ms, keyword pass `True`, quality `100`, reason `fato institucional canonico deve vir de fonte estruturada`
  answer: Estudar em uma escola publica pode ser uma boa escolha para muitas familias, e eu nao vou te vender uma comparacao vazia. No que esta publicado aqui, os diferenciais desta escola passam por Tutoria academica e projeto de vida, Espaco Maker integrado ao curriculo, Acolhimento estruturado para familias e estudantes. A proposta pedagogica publicada hoje combina Projeto pedagogico laico, com foco em aprendizagem por projetos, cultura digital responsavel, acompanhamento socioemocional e preparacao academica progressiva.. Na pratica, isso aparece em acompanhamento mais proximo da aprendizagem, projeto de vida e combinados pedagogicos mais claros. Escola laica com Ensino Fundamental II e Ensino Medio, acompanhamento tutorial e trilhas academicas no contraturno. Se quiser, eu posso te mostrar isso de forma mais pratica na rotina, na proposta pedagogica ou no contraturno.
- `crewai`: status 200, latency 162.6ms, keyword pass `False`, quality `80`, reason `crewai_protected_auth_required`
  errors: missing_expected_keyword
  answer: Essa consulta depende de autenticacao e vinculo da sua conta no Telegram. Use o portal da escola para gerar o codigo de vinculacao e depois envie o comando /start link_<codigo> ao bot.
- `python_functions`: status 200, latency 122.2ms, keyword pass `True`, quality `100`, reason `python_functions_native_structured:institution`
  answer: Estudar em uma escola publica pode ser uma boa escolha para muitas familias, e eu nao vou te vender uma comparacao vazia. No que esta publicado aqui, os diferenciais desta escola passam por Tutoria academica e projeto de vida, Espaco Maker integrado ao curriculo, Acolhimento estruturado para familias e estudantes. A proposta pedagogica publicada hoje combina Projeto pedagogico laico, com foco em aprendizagem por projetos, cultura digital responsavel, acompanhamento socioemocional e preparacao academica progressiva.. Na pratica, isso aparece em acompanhamento mais proximo da aprendizagem, projeto de vida e combinados pedagogicos mais claros. Escola laica com Ensino Fundamental II e Ensino Medio, acompanhamento tutorial e trilhas academicas no contraturno. Se quiser, eu posso te mostrar isso de forma mais pratica na rotina, na proposta pedagogica ou no contraturno.
- `llamaindex`: status 200, latency 120.6ms, keyword pass `True`, quality `100`, reason `llamaindex_public_profile`
  answer: Estudar em uma escola publica pode ser uma boa escolha para muitas familias, e eu nao vou te vender uma comparacao vazia. No que esta publicado aqui, os diferenciais desta escola passam por Tutoria academica e projeto de vida, Espaco Maker integrado ao curriculo, Acolhimento estruturado para familias e estudantes. A proposta pedagogica publicada hoje combina Projeto pedagogico laico, com foco em aprendizagem por projetos, cultura digital responsavel, acompanhamento socioemocional e preparacao academica progressiva.. Na pratica, isso aparece em acompanhamento mais proximo da aprendizagem, projeto de vida e combinados pedagogicos mais claros. Escola laica com Ensino Fundamental II e Ensino Medio, acompanhamento tutorial e trilhas academicas no contraturno. Se quiser, eu posso te mostrar isso de forma mais pratica na rotina, na proposta pedagogica ou no contraturno.

### mas o que isso muda na pratica no dia a dia?

- Slice: `public`
- Thread: `rand_public_value_compare` turn `2`
- `langgraph`: status 200, latency 123.0ms, keyword pass `True`, quality `100`, reason `fato institucional canonico deve vir de fonte estruturada`
  answer: Na pratica, isso muda em uma rotina com aprendizagem por projetos, acompanhamento mais proximo e referencias claras de tutoria academica. Os pontos que aparecem hoje de forma mais concreta sao Tutoria academica e projeto de vida, Espaco Maker integrado ao curriculo, Acolhimento estruturado para familias e estudantes. Isso aparece no dia a dia em projeto de vida, acompanhamento mais proximo e referencias mais visiveis para familias e estudantes. Isso conversa com uma proposta pedagogica que combina Projeto pedagogico laico, com foco em aprendizagem por projetos, cultura digital responsavel, acompanhamento socioemocional e preparacao academica progressiva..
- `crewai`: status 200, latency 11876.2ms, keyword pass `False`, quality `80`, reason `crewai_public_flow_completed`
  errors: missing_expected_keyword
  answer: Nao consegui concluir essa resposta agora pelo caminho principal configurado. Tente reformular em uma frase mais direta ou repetir em instantes.
- `python_functions`: status 200, latency 127.9ms, keyword pass `True`, quality `100`, reason `fato institucional canonico deve vir de fonte estruturada`
  answer: Na pratica, isso muda em uma rotina com aprendizagem por projetos, acompanhamento mais proximo e referencias claras de tutoria academica. Os pontos que aparecem hoje de forma mais concreta sao Tutoria academica e projeto de vida, Espaco Maker integrado ao curriculo, Acolhimento estruturado para familias e estudantes. Isso aparece no dia a dia em projeto de vida, acompanhamento mais proximo e referencias mais visiveis para familias e estudantes. Isso conversa com uma proposta pedagogica que combina Projeto pedagogico laico, com foco em aprendizagem por projetos, cultura digital responsavel, acompanhamento socioemocional e preparacao academica progressiva..
- `llamaindex`: status 200, latency 151.3ms, keyword pass `True`, quality `100`, reason `fato institucional canonico deve vir de fonte estruturada`
  answer: Na pratica, isso muda em uma rotina com aprendizagem por projetos, acompanhamento mais proximo e referencias claras de tutoria academica. Os pontos que aparecem hoje de forma mais concreta sao Tutoria academica e projeto de vida, Espaco Maker integrado ao curriculo, Acolhimento estruturado para familias e estudantes. Isso aparece no dia a dia em projeto de vida, acompanhamento mais proximo e referencias mais visiveis para familias e estudantes. Isso conversa com uma proposta pedagogica que combina Projeto pedagogico laico, com foco em aprendizagem por projetos, cultura digital responsavel, acompanhamento socioemocional e preparacao academica progressiva..

### entao a base curricular de voces continua seguindo a bncc?

- Slice: `public`
- Thread: `rand_public_value_compare` turn `3`
- `langgraph`: status 200, latency 132.7ms, keyword pass `True`, quality `100`, reason `fato institucional canonico deve vir de fonte estruturada`
  answer: No Ensino Medio, Colegio Horizonte segue a BNCC e um curriculo proprio de aprofundamento academico. Os componentes que aparecem hoje na base publica incluem Lingua Portuguesa e producao textual, Matematica, Biologia, Fisica, Quimica, Historia, Geografia, Lingua Inglesa, alem de projeto de vida, monitorias e trilhas eletivas.
- `crewai`: status 200, latency 867.5ms, keyword pass `True`, quality `100`, reason `crewai_public_fast_path`
  answer: A base curricular publicada pela escola hoje e a BNCC e o curriculo do Ensino Medio articulado com projeto de vida, producao textual, cultura digital e aprofundamento academico progressivo.
- `python_functions`: status 200, latency 130.6ms, keyword pass `True`, quality `100`, reason `python_functions_native_structured:institution`
  answer: No Ensino Medio, Colegio Horizonte segue a BNCC e um curriculo proprio de aprofundamento academico. Os componentes que aparecem hoje na base publica incluem Lingua Portuguesa e producao textual, Matematica, Biologia, Fisica, Quimica, Historia, Geografia, Lingua Inglesa, alem de projeto de vida, monitorias e trilhas eletivas.
- `llamaindex`: status 200, latency 137.2ms, keyword pass `True`, quality `100`, reason `llamaindex_public_profile`
  answer: No Ensino Medio, Colegio Horizonte segue a BNCC e um curriculo proprio de aprofundamento academico. Os componentes que aparecem hoje na base publica incluem Lingua Portuguesa e producao textual, Matematica, Biologia, Fisica, Quimica, Historia, Geografia, Lingua Inglesa, alem de projeto de vida, monitorias e trilhas eletivas.

### posso enviar documentos por fax ou isso nao existe mais?

- Slice: `public`
- Thread: `rand_public_channels_docs` turn `1`
- `langgraph`: status 200, latency 117.8ms, keyword pass `True`, quality `100`, reason `fato institucional canonico deve vir de fonte estruturada`
  answer: Hoje a escola nao utiliza fax para envio de documentos. Para isso, use portal institucional, email da secretaria, secretaria presencial.
- `crewai`: status 200, latency 150.3ms, keyword pass `False`, quality `80`, reason `crewai_protected_auth_required`
  errors: missing_expected_keyword
  answer: Essa consulta depende de autenticacao e vinculo da sua conta no Telegram. Use o portal da escola para gerar o codigo de vinculacao e depois envie o comando /start link_<codigo> ao bot.
- `python_functions`: status 200, latency 87.3ms, keyword pass `True`, quality `100`, reason `python_functions_native_contextual_public_answer`
  answer: Hoje a escola nao utiliza fax para envio de documentos. Para isso, use portal institucional, email da secretaria, secretaria presencial.
- `llamaindex`: status 200, latency 114.8ms, keyword pass `True`, quality `100`, reason `llamaindex_public_profile`
  answer: Hoje a escola nao utiliza fax para envio de documentos. Para isso, use portal institucional, email da secretaria, secretaria presencial.

### e por telegrama, serve?

- Slice: `public`
- Thread: `rand_public_channels_docs` turn `2`
- `langgraph`: status 200, latency 1816.3ms, keyword pass `True`, quality `100`, reason `retrieval hibrido e o caminho padrao para faq e documentos`
  answer: Hoje a escola nao publica telegrama como canal valido para documentos. Para isso, use portal institucional, email da secretaria, secretaria presencial.
- `crewai`: status 200, latency 833.3ms, keyword pass `True`, quality `100`, reason `crewai_public_fast_path`
  answer: Hoje a escola nao publica telegrama como canal valido. Para documentos, use portal institucional, email da secretaria ou secretaria presencial.
- `python_functions`: status 200, latency 119.7ms, keyword pass `True`, quality `100`, reason `contextual_public_direct_answer`
  answer: Hoje a escola nao publica telegrama como canal valido para documentos. Para isso, use portal institucional, email da secretaria, secretaria presencial.
- `llamaindex`: status 200, latency 111.0ms, keyword pass `True`, quality `100`, reason `contextual_public_direct_answer`
  answer: Hoje a escola nao publica telegrama como canal valido para documentos. Para isso, use portal institucional, email da secretaria, secretaria presencial.

### qual e o caminho certo pra mandar a documentacao?

- Slice: `public`
- Thread: `rand_public_channels_docs` turn `3`
- `langgraph`: status 200, latency 111.0ms, keyword pass `True`, quality `100`, reason `a intencao esta ambigua e exige clarificacao antes de recuperar contexto`
  answer: Sim. O envio inicial de documentos pode ser feito por canal digital.
Hoje os canais mais diretos publicados para isso sao:
- portal institucional
- email da secretaria
- secretaria presencial
No processo de matricula, o envio inicial pode ser digital. A validacao final continua com a secretaria.
O chat aberto nao deve receber documentos completos ou dados sensiveis. Quando possivel, use o portal autenticado ou o email institucional.
- `crewai`: status 200, latency 156.9ms, keyword pass `False`, quality `80`, reason `crewai_protected_auth_required`
  errors: missing_expected_keyword
  answer: Essa consulta depende de autenticacao e vinculo da sua conta no Telegram. Use o portal da escola para gerar o codigo de vinculacao e depois envie o comando /start link_<codigo> ao bot.
- `python_functions`: status 200, latency 128.0ms, keyword pass `True`, quality `100`, reason `contextual_public_direct_answer`
  answer: Sim. O envio inicial de documentos pode ser feito por canal digital.
Hoje os canais mais diretos publicados para isso sao:
- portal institucional
- email da secretaria
- secretaria presencial
No processo de matricula, o envio inicial pode ser digital. A validacao final continua com a secretaria.
O chat aberto nao deve receber documentos completos ou dados sensiveis. Quando possivel, use o portal autenticado ou o email institucional.
- `llamaindex`: status 200, latency 117.4ms, keyword pass `True`, quality `100`, reason `contextual_public_direct_answer`
  answer: Sim. O envio inicial de documentos pode ser feito por canal digital.
Hoje os canais mais diretos publicados para isso sao:
- portal institucional
- email da secretaria
- secretaria presencial
No processo de matricula, o envio inicial pode ser digital. A validacao final continua com a secretaria.
O chat aberto nao deve receber documentos completos ou dados sensiveis. Quando possivel, use o portal autenticado ou o email institucional.

### voces realmente tem biblioteca ou e so folheto bonito?

- Slice: `public`
- Thread: `rand_public_library_realism` turn `1`
- `langgraph`: status 200, latency 129.8ms, keyword pass `True`, quality `100`, reason `fato institucional canonico deve vir de fonte estruturada`
  answer: Sim. O Colegio Horizonte tem a Biblioteca Aurora. Atendimento ao publico de segunda a sexta, das 7h30 as 18h00.
- `crewai`: status 200, latency 843.9ms, keyword pass `True`, quality `100`, reason `crewai_public_fast_path`
  answer: Sim, a escola tem a Biblioteca Aurora, com atendimento das 7h30 as 18h00.
- `python_functions`: status 200, latency 123.1ms, keyword pass `True`, quality `100`, reason `python_functions_native_structured:institution`
  answer: Sim. O Colegio Horizonte tem a Biblioteca Aurora. Atendimento ao publico de segunda a sexta, das 7h30 as 18h00.
- `llamaindex`: status 200, latency 121.3ms, keyword pass `True`, quality `100`, reason `llamaindex_public_profile`
  answer: Sim. O Colegio Horizonte tem a Biblioteca Aurora. Atendimento ao publico de segunda a sexta, das 7h30 as 18h00.

### como ela se chama e ate que horas funciona?

- Slice: `public`
- Thread: `rand_public_library_realism` turn `2`
- `langgraph`: status 200, latency 132.3ms, keyword pass `True`, quality `100`, reason `fato institucional canonico deve vir de fonte estruturada`
  answer: Nao vi uma referencia oficial sobre como ela se chama e ate que horas funciona no perfil publico do Colegio Horizonte. Se quiser, eu posso te mostrar o que esta documentado sobre estrutura e atividades.

A Biblioteca Biblioteca Aurora funciona das 7h30 as 18h00.
- `crewai`: status 200, latency 770.3ms, keyword pass `True`, quality `90`, reason `crewai_public_fast_path`
  errors: repetitive_reply
  answer: Sim, a escola tem a Biblioteca Aurora, com atendimento das 7h30 as 18h00.
- `python_functions`: status 200, latency 103.9ms, keyword pass `True`, quality `100`, reason `python_functions_native_contextual_public_answer`
  answer: A biblioteca se chama Biblioteca Aurora e funciona de segunda a sexta, das 7h30 as 18h00.
- `llamaindex`: status 200, latency 137.6ms, keyword pass `True`, quality `100`, reason `llamaindex_public_profile`
  answer: Nao vi uma referencia oficial sobre como ela se chama e ate que horas funciona no perfil publico do Colegio Horizonte. Se quiser, eu posso te mostrar o que esta documentado sobre estrutura e atividades.

A Biblioteca Biblioteca Aurora funciona das 7h30 as 18h00.

### quando comeca a matricula do proximo ciclo?

- Slice: `public`
- Thread: `rand_public_timeline_visit` turn `1`
- `langgraph`: status 200, latency 148.0ms, keyword pass `True`, quality `100`, reason `datas institucionais publicas devem vir de leitura estruturada e auditavel`
  answer: O ciclo publico de matricula para 2026 foi aberto em 6 de outubro de 2025, com pre-cadastro, visita orientada opcional e triagem inicial de documentos. O atendimento comercial segue enquanto houver vagas por segmento.
- `crewai`: status 200, latency 160.5ms, keyword pass `False`, quality `80`, reason `crewai_protected_auth_required`
  errors: missing_expected_keyword
  answer: Essa consulta depende de autenticacao e vinculo da sua conta no Telegram. Use o portal da escola para gerar o codigo de vinculacao e depois envie o comando /start link_<codigo> ao bot.
- `python_functions`: status 200, latency 124.0ms, keyword pass `True`, quality `100`, reason `python_functions_native_structured:calendar`
  answer: O ciclo publico de matricula para 2026 foi aberto em 6 de outubro de 2025, com pre-cadastro, visita orientada opcional e triagem inicial de documentos. O atendimento comercial segue enquanto houver vagas por segmento.
- `llamaindex`: status 200, latency 129.4ms, keyword pass `True`, quality `100`, reason `llamaindex_public_profile`
  answer: O ciclo publico de matricula para 2026 foi aberto em 6 de outubro de 2025, com pre-cadastro, visita orientada opcional e triagem inicial de documentos. O atendimento comercial segue enquanto houver vagas por segmento.

### depois disso, quando as aulas comecam?

- Slice: `public`
- Thread: `rand_public_timeline_visit` turn `2`
- `langgraph`: status 200, latency 143.6ms, keyword pass `False`, quality `80`, reason `fato institucional canonico deve vir de fonte estruturada`
  errors: missing_expected_keyword
  answer: Colegio Horizonte: Escola laica com Ensino Fundamental II e Ensino Medio, acompanhamento tutorial e trilhas academicas no contraturno.
- `crewai`: status 200, latency 774.7ms, keyword pass `True`, quality `100`, reason `crewai_public_fast_path`
  answer: As aulas do Ensino Fundamental II e do Ensino Medio comecam em 2 de fevereiro de 2026.
- `python_functions`: status 200, latency 116.2ms, keyword pass `True`, quality `100`, reason `contextual_public_direct_answer`
  answer: As aulas do Ensino Fundamental II e do Ensino Medio comecam em 2 de fevereiro de 2026. A semana de acolhimento do 6o ano e da primeira serie ocorre entre 2 e 6 de fevereiro.
- `llamaindex`: status 200, latency 114.6ms, keyword pass `True`, quality `100`, reason `contextual_public_direct_answer`
  answer: As aulas do Ensino Fundamental II e do Ensino Medio comecam em 2 de fevereiro de 2026. A semana de acolhimento do 6o ano e da primeira serie ocorre entre 2 e 6 de fevereiro.

### estou logado como?

- Slice: `protected`
- Thread: `rand_protected_identity_scope` turn `1`
- `langgraph`: status 200, latency 100.9ms, keyword pass `True`, quality `100`, reason `identidade da conta autenticada exige leitura protegida e minimizada`
  answer: Voce esta falando aqui como Maria Oliveira, no perfil de responsavel. Sua conta esta vinculada a Lucas Oliveira e Ana Oliveira. Por aqui eu consigo consultar notas, faltas, proximas provas, matricula, financeiro, boletos, dentro das permissoes dessa vinculacao.
- `crewai`: status 200, latency 155.0ms, keyword pass `True`, quality `100`, reason `crewai_protected_identity_backstop`
  answer: Voce esta autenticado aqui como Maria Oliveira. Sua conta esta vinculada a Lucas Oliveira, Ana Oliveira e pode consultar notas, frequencia, avaliacoes, documentacao e financeiro desses alunos.
- `python_functions`: status 200, latency 93.8ms, keyword pass `True`, quality `100`, reason `python_functions_native_structured:institution`
  answer: Voce esta falando aqui como Maria Oliveira, no perfil de responsavel. Sua conta esta vinculada a Lucas Oliveira e Ana Oliveira. Por aqui eu consigo consultar notas, faltas, proximas provas, matricula, financeiro, boletos, dentro das permissoes dessa vinculacao.
- `llamaindex`: status 200, latency 99.1ms, keyword pass `True`, quality `100`, reason `identidade da conta autenticada exige leitura protegida e minimizada`
  answer: Voce esta falando aqui como Maria Oliveira, no perfil de responsavel. Sua conta esta vinculada a Lucas Oliveira e Ana Oliveira. Por aqui eu consigo consultar notas, faltas, proximas provas, matricula, financeiro, boletos, dentro das permissoes dessa vinculacao.

### e eu consigo ver o que exatamente por aqui?

- Slice: `protected`
- Thread: `rand_protected_identity_scope` turn `2`
- `langgraph`: status 200, latency 117.9ms, keyword pass `True`, quality `100`, reason `dados estruturados devem passar por service deterministico`
  answer: Voce ja esta autenticado por aqui e sua conta esta vinculada a Lucas Oliveira e Ana Oliveira. Por este canal eu consigo consultar notas, faltas, proximas provas, matricula, financeiro, boletos, dentro das permissoes dessa vinculacao. Se quiser, me diga algo como "notas do Lucas", "faltas da Ana" ou "financeiro do Lucas".
- `crewai`: status 200, latency 11933.6ms, keyword pass `False`, quality `55`, reason `crewai_public_flow_completed`
  errors: followup_context_drop, missing_expected_keyword
  answer: Nao consegui concluir essa resposta agora pelo caminho principal configurado. Tente reformular em uma frase mais direta ou repetir em instantes.
- `python_functions`: status 200, latency 128.9ms, keyword pass `True`, quality `100`, reason `dados estruturados devem passar por service deterministico`
  answer: Voce ja esta autenticado por aqui e sua conta esta vinculada a Lucas Oliveira e Ana Oliveira. Por este canal eu consigo consultar notas, faltas, proximas provas, matricula, financeiro, boletos, dentro das permissoes dessa vinculacao. Se quiser, me diga algo como "notas do Lucas", "faltas da Ana" ou "financeiro do Lucas".
- `llamaindex`: status 200, latency 137.8ms, keyword pass `True`, quality `100`, reason `dados estruturados devem passar por service deterministico`
  answer: Voce ja esta autenticado por aqui e sua conta esta vinculada a Lucas Oliveira e Ana Oliveira. Por este canal eu consigo consultar notas, faltas, proximas provas, matricula, financeiro, boletos, dentro das permissoes dessa vinculacao. Se quiser, me diga algo como "notas do Lucas", "faltas da Ana" ou "financeiro do Lucas".

### quais filhos eu tenho matriculados nessa conta?

- Slice: `protected`
- Thread: `rand_protected_identity_scope` turn `3`
- `langgraph`: status 200, latency 201.8ms, keyword pass `True`, quality `100`, reason `dados estruturados devem passar por service deterministico`
  answer: Resumo financeiro das contas vinculadas:
- Total de faturas em aberto: 1
- Total de faturas vencidas: 0
- Lucas Oliveira: 0 em aberto, 0 vencidas
  2026-03: vencimento 2026-03-10, status paga, valor 1450.00
- Ana Oliveira: 1 em aberto, 0 vencidas
  2026-03: vencimento 2026-03-10, status em aberto, valor 1450.00
- `crewai`: status 200, latency 11874.0ms, keyword pass `False`, quality `70`, reason `crewai_public_flow_completed`
  errors: missing_expected_keyword, repetitive_reply
  answer: Nao consegui concluir essa resposta agora pelo caminho principal configurado. Tente reformular em uma frase mais direta ou repetir em instantes.
- `python_functions`: status 200, latency 245.1ms, keyword pass `True`, quality `100`, reason `python_functions_native_structured:finance`
  answer: Resumo financeiro das contas vinculadas:
- Total de faturas em aberto: 1
- Total de faturas vencidas: 0
- Lucas Oliveira: 0 em aberto, 0 vencidas
  2026-03: vencimento 2026-03-10, status paga, valor 1450.00
- Ana Oliveira: 1 em aberto, 0 vencidas
  2026-03: vencimento 2026-03-10, status em aberto, valor 1450.00
- `llamaindex`: status 200, latency 191.1ms, keyword pass `True`, quality `100`, reason `dados estruturados devem passar por service deterministico`
  answer: Resumo financeiro das contas vinculadas:
- Total de faturas em aberto: 1
- Total de faturas vencidas: 0
- Lucas Oliveira: 0 em aberto, 0 vencidas
  2026-03: vencimento 2026-03-10, status paga, valor 1450.00
- Ana Oliveira: 1 em aberto, 0 vencidas
  2026-03: vencimento 2026-03-10, status em aberto, valor 1450.00

### como esta a documentacao da ana?

- Slice: `protected`
- Thread: `rand_protected_docs_focus` turn `1`
- `langgraph`: status 200, latency 135.1ms, keyword pass `True`, quality `100`, reason `status administrativo autenticado exige service deterministico`
  answer: Situacao documental de Ana Oliveira hoje: com pendencias.
- `crewai`: status 200, latency 366.1ms, keyword pass `True`, quality `100`, reason `crewai_protected_fast_path`
  answer: A situacao documental de Ana Oliveira hoje esta com pendencias.
- `python_functions`: status 200, latency 133.4ms, keyword pass `True`, quality `100`, reason `python_functions_native_structured:institution`
  answer: Situacao documental de Ana Oliveira hoje: com pendencias.
- `llamaindex`: status 200, latency 148.5ms, keyword pass `True`, quality `100`, reason `status administrativo autenticado exige service deterministico`
  answer: Situacao documental de Ana Oliveira hoje: com pendencias.

### o que falta?

- Slice: `protected`
- Thread: `rand_protected_docs_focus` turn `2`
- `langgraph`: status 200, latency 151.5ms, keyword pass `True`, quality `100`, reason `status administrativo autenticado exige service deterministico`
  answer: Hoje, o proximo passo do seu cadastro e este: Envie o comprovante atualizado pela secretaria ou pelo canal de documentos para concluir a conferência.
- `crewai`: status 200, latency 383.2ms, keyword pass `True`, quality `100`, reason `crewai_protected_fast_path`
  answer: No momento, ainda falta para Ana Oliveira: Documentacao escolar do aluno. Ainda falta anexar um comprovante de residencia atualizado para Ana Oliveira concluir a conferencia documental.
- `python_functions`: status 200, latency 170.0ms, keyword pass `True`, quality `100`, reason `python_functions_native_structured:academic`
  answer: No recorte de faltas de Ana Oliveira, eu encontrei 6 falta(s) e 8 atraso(s).
- `llamaindex`: status 200, latency 183.6ms, keyword pass `True`, quality `100`, reason `dados estruturados devem passar por service deterministico`
  answer: No recorte de faltas de Ana Oliveira, eu encontrei 6 falta(s) e 8 atraso(s).

### e a documentacao do lucas?

- Slice: `protected`
- Thread: `rand_protected_docs_focus` turn `3`
- `langgraph`: status 200, latency 157.2ms, keyword pass `True`, quality `100`, reason `status administrativo autenticado exige service deterministico`
  answer: Situacao documental de Lucas Oliveira hoje: regular.
- Identificacao escolar do aluno: regular. Codigo de matricula: MAT-2026-001
- Responsavel vinculado: regular. Maria Oliveira
- Documentacao escolar do aluno: regular. A documentacao escolar de Lucas Oliveira esta conferida e sem pendencias relevantes nesta base de testes.
- `crewai`: status 200, latency 404.1ms, keyword pass `True`, quality `100`, reason `crewai_protected_fast_path`
  answer: A situacao documental de Lucas Oliveira hoje esta regular e completa.
- `python_functions`: status 200, latency 173.4ms, keyword pass `True`, quality `100`, reason `python_functions_native_structured:institution`
  answer: Situacao documental de Lucas Oliveira hoje: regular.
- Identificacao escolar do aluno: regular. Codigo de matricula: MAT-2026-001
- Responsavel vinculado: regular. Maria Oliveira
- Documentacao escolar do aluno: regular. A documentacao escolar de Lucas Oliveira esta conferida e sem pendencias relevantes nesta base de testes.
- `llamaindex`: status 200, latency 176.1ms, keyword pass `True`, quality `100`, reason `status administrativo autenticado exige service deterministico`
  answer: Situacao documental de Lucas Oliveira hoje: regular.
- Identificacao escolar do aluno: regular. Codigo de matricula: MAT-2026-001
- Responsavel vinculado: regular. Maria Oliveira
- Documentacao escolar do aluno: regular. A documentacao escolar de Lucas Oliveira esta conferida e sem pendencias relevantes nesta base de testes.

### e se eu perguntar do joao?

- Slice: `protected`
- Thread: `rand_protected_docs_focus` turn `4`
- `langgraph`: status 200, latency 107.0ms, keyword pass `True`, quality `100`, reason `status administrativo autenticado exige service deterministico`
  answer: Hoje eu nao encontrei Joao entre os alunos vinculados a esta conta. No momento, os alunos que aparecem aqui sao: Lucas Oliveira (MAT-2026-001), Ana Oliveira (MAT-2026-002). Se quiser, me diga qual deles voce quer consultar.
- `crewai`: status 200, latency 11907.0ms, keyword pass `False`, quality `43`, reason `crewai_public_flow_timeout`
  errors: followup_context_drop, missing_expected_keyword, unnecessary_clarification
  answer: Para que eu possa te ajudar melhor, você poderia especificar quem é João no contexto da escola? Por exemplo, ele é um aluno, professor, funcionário, ou você está procurando informações sobre um departamento ou serviço específico?
- `python_functions`: status 200, latency 115.6ms, keyword pass `True`, quality `100`, reason `status administrativo autenticado exige service deterministico`
  answer: Hoje eu nao encontrei Joao entre os alunos vinculados a esta conta. No momento, os alunos que aparecem aqui sao: Lucas Oliveira (MAT-2026-001), Ana Oliveira (MAT-2026-002). Se quiser, me diga qual deles voce quer consultar.
- `llamaindex`: status 200, latency 123.5ms, keyword pass `True`, quality `100`, reason `status administrativo autenticado exige service deterministico`
  answer: Hoje eu nao encontrei Joao entre os alunos vinculados a esta conta. No momento, os alunos que aparecem aqui sao: Lucas Oliveira (MAT-2026-001), Ana Oliveira (MAT-2026-002). Se quiser, me diga qual deles voce quer consultar.

### quero ver as notas do lucas

- Slice: `protected`
- Thread: `rand_protected_academic_finance` turn `1`
- `langgraph`: status 200, latency 154.2ms, keyword pass `True`, quality `100`, reason `dados estruturados devem passar por service deterministico`
  answer: Notas de Lucas Oliveira:
- Biologia - Avaliacao B1: 8.40/10.00
- Educacao Fisica - Avaliacao 2026-B1 - EF: 6.40/10.00
- Filosofia - Avaliacao 2026-B1 - FIL: 7.00/10.00
- Fisica - Avaliacao 2026-B1 - FIS: 5.80/10.00
- Geografia - Avaliacao 2026-B1 - GEO: 6.40/10.00
- Historia - Avaliacao 2026-B1 - HIS: 6.70/10.00
- Ingles - Avaliacao B1: 8.90/10.00
- Matematica - Avaliacao B1: 8.70/10.00
- `crewai`: status 200, latency 404.9ms, keyword pass `True`, quality `100`, reason `crewai_protected_fast_path`
  answer: As notas mais recentes de Lucas Oliveira incluem Biologia: 8.40/10.00; Educacao Fisica: 6.40/10.00; Filosofia: 7.00/10.00; Fisica: 5.80/10.00; Geografia: 6.40/10.00; Historia: 6.70/10.00; Ingles: 8.90/10.00; Matematica: 8.70/10.00.
- `python_functions`: status 200, latency 156.5ms, keyword pass `True`, quality `100`, reason `python_functions_native_structured:academic`
  answer: Notas de Lucas Oliveira:
- Biologia - Avaliacao B1: 8.40/10.00
- Educacao Fisica - Avaliacao 2026-B1 - EF: 6.40/10.00
- Filosofia - Avaliacao 2026-B1 - FIL: 7.00/10.00
- Fisica - Avaliacao 2026-B1 - FIS: 5.80/10.00
- Geografia - Avaliacao 2026-B1 - GEO: 6.40/10.00
- Historia - Avaliacao 2026-B1 - HIS: 6.70/10.00
- Ingles - Avaliacao B1: 8.90/10.00
- Matematica - Avaliacao B1: 8.70/10.00
- `llamaindex`: status 200, latency 161.3ms, keyword pass `True`, quality `100`, reason `dados estruturados devem passar por service deterministico`
  answer: Notas de Lucas Oliveira:
- Biologia - Avaliacao B1: 8.40/10.00
- Educacao Fisica - Avaliacao 2026-B1 - EF: 6.40/10.00
- Filosofia - Avaliacao 2026-B1 - FIL: 7.00/10.00
- Fisica - Avaliacao 2026-B1 - FIS: 5.80/10.00
- Geografia - Avaliacao 2026-B1 - GEO: 6.40/10.00
- Historia - Avaliacao 2026-B1 - HIS: 6.70/10.00
- Ingles - Avaliacao B1: 8.90/10.00
- Matematica - Avaliacao B1: 8.70/10.00

### e quanto esta em aberto?

- Slice: `protected`
- Thread: `rand_protected_academic_finance` turn `2`
- `langgraph`: status 200, latency 156.3ms, keyword pass `True`, quality `100`, reason `dados estruturados devem passar por service deterministico`
  answer: Hoje nao encontrei valor em aberto para Lucas Oliveira neste recorte.
- `crewai`: status 200, latency 406.7ms, keyword pass `True`, quality `100`, reason `crewai_protected_fast_path`
  answer: No momento, nao encontrei valor em aberto para Lucas Oliveira neste recorte.
- `python_functions`: status 200, latency 153.6ms, keyword pass `True`, quality `100`, reason `python_functions_native_structured:finance`
  answer: Hoje nao encontrei valor em aberto para Lucas Oliveira neste recorte.
- `llamaindex`: status 200, latency 152.0ms, keyword pass `True`, quality `100`, reason `dados estruturados devem passar por service deterministico`
  answer: Hoje nao encontrei valor em aberto para Lucas Oliveira neste recorte.

### e a proxima data de pagamento?

- Slice: `protected`
- Thread: `rand_protected_academic_finance` turn `3`
- `langgraph`: status 200, latency 138.6ms, keyword pass `True`, quality `100`, reason `dados estruturados devem passar por service deterministico`
  answer: Hoje a cobranca pendente mais imediata de Lucas Oliveira e a referencia 2026-03, com vencimento em 10 de marco de 2026 e valor 1450.00. Status atual: paga.
- `crewai`: status 200, latency 394.6ms, keyword pass `False`, quality `55`, reason `crewai_protected_fast_path`
  errors: followup_context_drop, missing_expected_keyword
  answer: O proximo pagamento de Lucas Oliveira vence em 2026-03-10 no valor de 1450.00.
- `python_functions`: status 200, latency 159.7ms, keyword pass `True`, quality `100`, reason `python_functions_native_structured:finance`
  answer: Hoje a cobranca pendente mais imediata de Lucas Oliveira e a referencia 2026-03, com vencimento em 10 de marco de 2026 e valor 1450.00. Status atual: paga.
- `llamaindex`: status 200, latency 151.4ms, keyword pass `True`, quality `100`, reason `dados estruturados devem passar por service deterministico`
  answer: Hoje a cobranca pendente mais imediata de Lucas Oliveira e a referencia 2026-03, com vencimento em 10 de marco de 2026 e valor 1450.00. Status atual: paga.

### preciso falar com o financeiro

- Slice: `support`
- Thread: `rand_support_reroute` turn `1`
- `langgraph`: status 200, latency 123.0ms, keyword pass `True`, quality `100`, reason `o usuario demonstrou necessidade de atendimento humano ou operacional`
  answer: Encaminhei sua solicitacao para a fila de financeiro. Protocolo: ATD-20260330-F87D3E67. Status atual: queued. A equipe humana pode continuar esse atendimento no portal operacional.
- `crewai`: status 200, latency 185.7ms, keyword pass `True`, quality `100`, reason `support_handoff_created`
  answer: Encaminhei sua solicitacao para a fila de financeiro. Protocolo: ATD-20260330-00D9CDCF. Status atual: queued. A equipe humana podera continuar esse atendimento no portal operacional.
- `python_functions`: status 200, latency 115.2ms, keyword pass `True`, quality `100`, reason `o usuario demonstrou necessidade de atendimento humano ou operacional`
  answer: Encaminhei sua solicitacao para a fila de financeiro. Protocolo: ATD-20260330-6C56E5DD. Status atual: queued. A equipe humana pode continuar esse atendimento no portal operacional.
- `llamaindex`: status 200, latency 117.1ms, keyword pass `True`, quality `100`, reason `o usuario demonstrou necessidade de atendimento humano ou operacional`
  answer: Encaminhei sua solicitacao para a fila de financeiro. Protocolo: ATD-20260330-26EA162E. Status atual: queued. A equipe humana pode continuar esse atendimento no portal operacional.

### qual o protocolo?

- Slice: `support`
- Thread: `rand_support_reroute` turn `2`
- `langgraph`: status 200, latency 137.7ms, keyword pass `True`, quality `100`, reason `a solicitacao pode ser executada por workflow estruturado com protocolo`
  answer: O protocolo atual do seu atendimento e ATD-20260330-F87D3E67. Se quiser, eu posso te dizer o status atual ou resumir o que ja foi registrado.
- `crewai`: status 200, latency 151.1ms, keyword pass `True`, quality `100`, reason `workflow_protocol_lookup`
  answer: O protocolo da sua solicitacao e ATD-20260330-00D9CDCF. - Ticket operacional: ATD-20260330-00D9CDCF - Area responsavel: None Se quiser, eu tambem posso resumir o pedido ou verificar o status atual.
- `python_functions`: status 200, latency 132.5ms, keyword pass `True`, quality `100`, reason `python_functions_native_structured:support`
  answer: O protocolo atual do seu atendimento e ATD-20260330-6C56E5DD. Se quiser, eu posso te dizer o status atual ou resumir o que ja foi registrado.
- `llamaindex`: status 200, latency 142.4ms, keyword pass `True`, quality `100`, reason `a solicitacao pode ser executada por workflow estruturado com protocolo`
  answer: O protocolo atual do seu atendimento e ATD-20260330-26EA162E. Se quiser, eu posso te dizer o status atual ou resumir o que ja foi registrado.

### mudei de ideia, quero secretaria

- Slice: `support`
- Thread: `rand_support_reroute` turn `3`
- `langgraph`: status 200, latency 140.6ms, keyword pass `True`, quality `82`, reason `o usuario demonstrou necessidade de atendimento humano ou operacional`
  errors: repair_miss
  answer: Sua solicitacao ja estava registrada na fila de secretaria. Protocolo: ATD-20260330-F87D3E67. Status atual: queued.
- `crewai`: status 200, latency 171.8ms, keyword pass `True`, quality `100`, reason `support_handoff_rerouted`
  answer: Sem problema, agora segui com a fila de secretaria. Sua solicitacao ja estava registrada na fila de secretaria. Protocolo: ATD-20260330-00D9CDCF. Status atual: queued.
- `python_functions`: status 200, latency 123.9ms, keyword pass `True`, quality `100`, reason `o usuario demonstrou necessidade de atendimento humano ou operacional`
  answer: Sem problema, ajustei isso por aqui.

Sua solicitacao ja estava registrada na fila de secretaria. Protocolo: ATD-20260330-6C56E5DD. Status atual: queued.
- `llamaindex`: status 200, latency 133.0ms, keyword pass `True`, quality `100`, reason `o usuario demonstrou necessidade de atendimento humano ou operacional`
  answer: Sem problema, ajustei isso por aqui.

Sua solicitacao ja estava registrada na fila de secretaria. Protocolo: ATD-20260330-26EA162E. Status atual: queued.

### e como esta esse atendimento?

- Slice: `support`
- Thread: `rand_support_status_summary` turn `1`
- `langgraph`: status 200, latency 124.0ms, keyword pass `True`, quality `100`, reason `a solicitacao pode ser executada por workflow estruturado com protocolo`
  answer: Ainda nao encontrei um protocolo recente nesta conversa para consultar o status da fila. Se quiser, me diga o codigo que comeca com VIS, REQ ou ATD, ou me lembre se o assunto era visita, direcao, financeiro ou secretaria.
- `crewai`: status 200, latency 11828.4ms, keyword pass `False`, quality `80`, reason `crewai_public_flow_completed`
  errors: missing_expected_keyword
  answer: Nao consegui concluir essa resposta agora pelo caminho principal configurado. Tente reformular em uma frase mais direta ou repetir em instantes.
- `python_functions`: status 200, latency 120.1ms, keyword pass `True`, quality `100`, reason `python_functions_native_structured:support`
  answer: Ainda nao encontrei um protocolo recente nesta conversa para consultar o status da fila. Se quiser, me diga o codigo que comeca com VIS, REQ ou ATD, ou me lembre se o assunto era visita, direcao, financeiro ou secretaria.
- `llamaindex`: status 200, latency 131.7ms, keyword pass `True`, quality `100`, reason `a solicitacao pode ser executada por workflow estruturado com protocolo`
  answer: Ainda nao encontrei um protocolo recente nesta conversa para consultar o status da fila. Se quiser, me diga o codigo que comeca com VIS, REQ ou ATD, ou me lembre se o assunto era visita, direcao, financeiro ou secretaria.

### resume pra mim

- Slice: `support`
- Thread: `rand_support_status_summary` turn `2`
- `langgraph`: status 200, latency 125.3ms, keyword pass `True`, quality `100`, reason `a solicitacao pode ser executada por workflow estruturado com protocolo`
  answer: Ainda nao encontrei um protocolo recente nesta conversa para montar o resumo do pedido. Se quiser, me diga o codigo que comeca com VIS, REQ ou ATD, ou me lembre se o assunto era visita, direcao, financeiro ou secretaria.
- `crewai`: status 200, latency 11818.5ms, keyword pass `False`, quality `70`, reason `crewai_public_flow_completed`
  errors: missing_expected_keyword, repetitive_reply
  answer: Nao consegui concluir essa resposta agora pelo caminho principal configurado. Tente reformular em uma frase mais direta ou repetir em instantes.
- `python_functions`: status 200, latency 125.9ms, keyword pass `True`, quality `100`, reason `python_functions_native_structured:support`
  answer: Ainda nao encontrei um protocolo recente nesta conversa para montar o resumo do pedido. Se quiser, me diga o codigo que comeca com VIS, REQ ou ATD, ou me lembre se o assunto era visita, direcao, financeiro ou secretaria.
- `llamaindex`: status 200, latency 133.6ms, keyword pass `True`, quality `100`, reason `a solicitacao pode ser executada por workflow estruturado com protocolo`
  answer: Ainda nao encontrei um protocolo recente nesta conversa para montar o resumo do pedido. Se quiser, me diga o codigo que comeca com VIS, REQ ou ATD, ou me lembre se o assunto era visita, direcao, financeiro ou secretaria.

### da pra marcar uma visita na quinta a tarde?

- Slice: `workflow`
- Thread: `rand_workflow_visit` turn `1`
- `langgraph`: status 200, latency 139.9ms, keyword pass `True`, quality `100`, reason `a solicitacao pode ser executada por workflow estruturado com protocolo`
  answer: Pedido de visita registrado para o Colegio Horizonte. Protocolo: VIS-20260330-DE76EE. Preferencia informada: 2026-04-02 - tarde. Fila responsavel: admissoes. Ticket operacional: ATD-20260330-D04F9571. A equipe comercial valida a janela e retorna com a confirmacao.
- `crewai`: status 200, latency 184.6ms, keyword pass `True`, quality `100`, reason `workflow_visit_create`
  answer: Pedido de visita registrado para o Colegio Horizonte. Protocolo: VIS-20260330-DA0665. Preferencia informada: 02/04/2026 - tarde. Fila responsavel: admissoes. Ticket operacional: ATD-20260330-D9A1931D. A equipe comercial valida a janela e retorna com a confirmacao.
- `python_functions`: status 200, latency 137.1ms, keyword pass `True`, quality `100`, reason `python_functions_native_structured:support`
  answer: Pedido de visita registrado para o Colegio Horizonte. Protocolo: VIS-20260330-BDEB47. Preferencia informada: 2026-04-02 - tarde. Fila responsavel: admissoes. Ticket operacional: ATD-20260330-B5E28260. A equipe comercial valida a janela e retorna com a confirmacao.
- `llamaindex`: status 200, latency 147.8ms, keyword pass `True`, quality `100`, reason `a solicitacao pode ser executada por workflow estruturado com protocolo`
  answer: Pedido de visita registrado para o Colegio Horizonte. Protocolo: VIS-20260330-6F0F90. Preferencia informada: 2026-04-02 - tarde. Fila responsavel: admissoes. Ticket operacional: ATD-20260330-C894112F. A equipe comercial valida a janela e retorna com a confirmacao.

### me fala o protocolo dessa visita

- Slice: `workflow`
- Thread: `rand_workflow_visit` turn `2`
- `langgraph`: status 200, latency 149.1ms, keyword pass `True`, quality `100`, reason `a solicitacao pode ser executada por workflow estruturado com protocolo`
  answer: O protocolo da sua visita e VIS-20260330-DE76EE. Ticket operacional: ATD-20260330-D04F9571. Preferencia registrada: 02/04/2026 - tarde. Se quiser, eu tambem posso te dizer o status, remarcar ou cancelar a visita.
- `crewai`: status 200, latency 179.8ms, keyword pass `True`, quality `100`, reason `workflow_protocol_lookup`
  answer: O protocolo da sua visita e VIS-20260330-DA0665. - Ticket operacional: ATD-20260330-D9A1931D - Preferencia registrada: 02/04/2026 - tarde Se quiser, eu tambem posso te dizer o status, remarcar ou cancelar a visita.
- `python_functions`: status 200, latency 136.9ms, keyword pass `True`, quality `100`, reason `python_functions_native_structured:support`
  answer: O protocolo da sua visita e VIS-20260330-BDEB47. Ticket operacional: ATD-20260330-B5E28260. Preferencia registrada: 02/04/2026 - tarde. Se quiser, eu tambem posso te dizer o status, remarcar ou cancelar a visita.
- `llamaindex`: status 200, latency 143.6ms, keyword pass `True`, quality `100`, reason `a solicitacao pode ser executada por workflow estruturado com protocolo`
  answer: O protocolo da sua visita e VIS-20260330-6F0F90. Ticket operacional: ATD-20260330-C894112F. Preferencia registrada: 02/04/2026 - tarde. Se quiser, eu tambem posso te dizer o status, remarcar ou cancelar a visita.

### e se eu precisar remarcar?

- Slice: `workflow`
- Thread: `rand_workflow_visit` turn `3`
- `langgraph`: status 200, latency 131.4ms, keyword pass `True`, quality `100`, reason `a solicitacao pode ser executada por workflow estruturado com protocolo`
  answer: Consigo remarcar a visita por aqui. Protocolo: VIS-20260330-DE76EE. Ticket operacional: ATD-20260330-D04F9571. Me diga pelo menos o novo dia ou a janela desejada, por exemplo: "remarque para sexta de manha" ou "troque para 28/03 as 10h".
- `crewai`: status 200, latency 159.3ms, keyword pass `True`, quality `100`, reason `workflow_visit_reschedule_guidance`
  answer: Se voce precisar remarcar, me passe o protocolo VIS-20260330-DA0665 ou o novo horario desejado que eu sigo com essa atualizacao para a fila de admissoes.
- `python_functions`: status 200, latency 181.3ms, keyword pass `True`, quality `100`, reason `python_functions_native_structured:support`
  answer: Consigo remarcar a visita por aqui. Protocolo: VIS-20260330-BDEB47. Ticket operacional: ATD-20260330-B5E28260. Me diga pelo menos o novo dia ou a janela desejada, por exemplo: "remarque para sexta de manha" ou "troque para 28/03 as 10h".
- `llamaindex`: status 200, latency 128.9ms, keyword pass `True`, quality `100`, reason `a solicitacao pode ser executada por workflow estruturado com protocolo`
  answer: Consigo remarcar a visita por aqui. Protocolo: VIS-20260330-6F0F90. Ticket operacional: ATD-20260330-C894112F. Me diga pelo menos o novo dia ou a janela desejada, por exemplo: "remarque para sexta de manha" ou "troque para 28/03 as 10h".

### entao remarca pra sexta de manha

- Slice: `workflow`
- Thread: `rand_workflow_visit` turn `4`
- `langgraph`: status 200, latency 133.5ms, keyword pass `True`, quality `100`, reason `a solicitacao pode ser executada por workflow estruturado com protocolo`
  answer: Pedido de visita atualizado com a fila de admissions. Protocolo: VIS-20260330-DE76EE. Ticket operacional: ATD-20260330-D04F9571. Nova preferencia: 03/04/2026 - manha. Admissions valida a nova janela e retorna com a confirmacao.
- `crewai`: status 200, latency 11851.6ms, keyword pass `False`, quality `80`, reason `crewai_public_flow_completed`
  errors: missing_expected_keyword
  answer: Nao consegui concluir essa resposta agora pelo caminho principal configurado. Tente reformular em uma frase mais direta ou repetir em instantes.
- `python_functions`: status 200, latency 137.8ms, keyword pass `True`, quality `100`, reason `a solicitacao pode ser executada por workflow estruturado com protocolo`
  answer: Pedido de visita atualizado com a fila de admissions. Protocolo: VIS-20260330-BDEB47. Ticket operacional: ATD-20260330-B5E28260. Nova preferencia: 03/04/2026 - manha. Admissions valida a nova janela e retorna com a confirmacao.
- `llamaindex`: status 200, latency 147.1ms, keyword pass `True`, quality `100`, reason `a solicitacao pode ser executada por workflow estruturado com protocolo`
  answer: Pedido de visita atualizado com a fila de admissions. Protocolo: VIS-20260330-6F0F90. Ticket operacional: ATD-20260330-C894112F. Nova preferencia: 03/04/2026 - manha. Admissions valida a nova janela e retorna com a confirmacao.

### quero protocolar um pedido pra direcao sobre reforco de seguranca na saida

- Slice: `workflow`
- Thread: `rand_workflow_request` turn `1`
- `langgraph`: status 200, latency 131.3ms, keyword pass `True`, quality `100`, reason `a solicitacao pode ser executada por workflow estruturado com protocolo`
  answer: Solicitacao institucional registrada para direcao. Protocolo: REQ-20260330-723FAA. Assunto: quero protocolar um pedido pra direcao sobre reforco de seguranca na saida. Fila responsavel: direcao. Ticket operacional: ATD-20260330-95539EC8. A equipe faz a triagem inicial e segue o retorno pelo fluxo institucional.
- `crewai`: status 200, latency 179.2ms, keyword pass `True`, quality `100`, reason `support_handoff_created`
  answer: Encaminhei sua solicitacao para a fila de direcao. Protocolo: ATD-20260330-8DE048B4. Status atual: queued. A equipe humana podera continuar esse atendimento no portal operacional.
- `python_functions`: status 200, latency 137.4ms, keyword pass `True`, quality `100`, reason `python_functions_native_structured:support`
  answer: Solicitacao institucional registrada para direcao. Protocolo: REQ-20260330-A7DC81. Assunto: quero protocolar um pedido pra direcao sobre reforco de seguranca na saida. Fila responsavel: direcao. Ticket operacional: ATD-20260330-24446371. A equipe faz a triagem inicial e segue o retorno pelo fluxo institucional.
- `llamaindex`: status 200, latency 141.0ms, keyword pass `True`, quality `100`, reason `a solicitacao pode ser executada por workflow estruturado com protocolo`
  answer: Solicitacao institucional registrada para direcao. Protocolo: REQ-20260330-DFDA16. Assunto: quero protocolar um pedido pra direcao sobre reforco de seguranca na saida. Fila responsavel: direcao. Ticket operacional: ATD-20260330-01C26A76. A equipe faz a triagem inicial e segue o retorno pelo fluxo institucional.

### complementa dizendo que isso pesa mais nas sextas

- Slice: `workflow`
- Thread: `rand_workflow_request` turn `2`
- `langgraph`: status 200, latency 132.1ms, keyword pass `True`, quality `100`, reason `a solicitacao pode ser executada por workflow estruturado com protocolo`
  answer: Complemento registrado na fila de direcao. Protocolo: REQ-20260330-723FAA. Ticket operacional: ATD-20260330-95539EC8. Novo complemento: isso pesa mais nas sextas. A equipe responsavel recebe essa atualizacao no mesmo fluxo do pedido.
- `crewai`: status 200, latency 11778.3ms, keyword pass `False`, quality `80`, reason `crewai_public_flow_completed`
  errors: missing_expected_keyword
  answer: Nao consegui concluir essa resposta agora pelo caminho principal configurado. Tente reformular em uma frase mais direta ou repetir em instantes.
- `python_functions`: status 200, latency 137.2ms, keyword pass `True`, quality `100`, reason `python_functions_native_structured:support`
  answer: Complemento registrado na fila de direcao. Protocolo: REQ-20260330-A7DC81. Ticket operacional: ATD-20260330-24446371. Novo complemento: isso pesa mais nas sextas. A equipe responsavel recebe essa atualizacao no mesmo fluxo do pedido.
- `llamaindex`: status 200, latency 129.8ms, keyword pass `True`, quality `100`, reason `a solicitacao pode ser executada por workflow estruturado com protocolo`
  answer: Complemento registrado na fila de direcao. Protocolo: REQ-20260330-DFDA16. Ticket operacional: ATD-20260330-01C26A76. Novo complemento: isso pesa mais nas sextas. A equipe responsavel recebe essa atualizacao no mesmo fluxo do pedido.

### faz um resumo do meu pedido

- Slice: `workflow`
- Thread: `rand_workflow_request` turn `3`
- `langgraph`: status 200, latency 128.1ms, keyword pass `True`, quality `100`, reason `a solicitacao pode ser executada por workflow estruturado com protocolo`
  answer: Resumo da sua solicitacao institucional:. Assunto: quero protocolar um pedido pra direcao sobre reforco de seguranca na saida. Area responsavel: direcao. Detalhes registrados: quero protocolar um pedido pra direcao sobre reforco de seguranca na saida

Complemento registrado: isso pesa mais nas sextas. Protocolo: REQ-20260330-723FAA. Ticket operacional: ATD-20260330-95539EC8. Status atual: em fila. Se quiser, eu tambem posso te dizer o prazo estimado ou quem responde por essa fila.
- `crewai`: status 200, latency 11873.9ms, keyword pass `False`, quality `70`, reason `crewai_public_flow_completed`
  errors: missing_expected_keyword, repetitive_reply
  answer: Nao consegui concluir essa resposta agora pelo caminho principal configurado. Tente reformular em uma frase mais direta ou repetir em instantes.
- `python_functions`: status 200, latency 135.5ms, keyword pass `True`, quality `100`, reason `python_functions_native_structured:support`
  answer: Resumo da sua solicitacao institucional:. Assunto: quero protocolar um pedido pra direcao sobre reforco de seguranca na saida. Area responsavel: direcao. Detalhes registrados: quero protocolar um pedido pra direcao sobre reforco de seguranca na saida

Complemento registrado: isso pesa mais nas sextas. Protocolo: REQ-20260330-A7DC81. Ticket operacional: ATD-20260330-24446371. Status atual: em fila. Se quiser, eu tambem posso te dizer o prazo estimado ou quem responde por essa fila.
- `llamaindex`: status 200, latency 142.3ms, keyword pass `True`, quality `100`, reason `a solicitacao pode ser executada por workflow estruturado com protocolo`
  answer: Resumo da sua solicitacao institucional:. Assunto: quero protocolar um pedido pra direcao sobre reforco de seguranca na saida. Area responsavel: direcao. Detalhes registrados: quero protocolar um pedido pra direcao sobre reforco de seguranca na saida

Complemento registrado: isso pesa mais nas sextas. Protocolo: REQ-20260330-DFDA16. Ticket operacional: ATD-20260330-01C26A76. Status atual: em fila. Se quiser, eu tambem posso te dizer o prazo estimado ou quem responde por essa fila.

