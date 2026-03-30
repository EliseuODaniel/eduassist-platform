# Four-Path Chatbot Comparison Report

Date: 2026-03-30T12:57:55.434564+00:00

Dataset: `/home/edann/projects/eduassist-platform/artifacts/two_stack_random_strict_llm_live_20260327_v1_dataset.json`

## Stack Summary

| Stack | OK | Keyword pass | Quality | Avg latency |
| --- | --- | --- | --- | --- |
| `langgraph` | `32/32` | `29/32` | `97.6` | `279.7 ms` |
| `crewai` | `32/32` | `17/32` | `87.3` | `3804.5 ms` |
| `python_functions` | `32/32` | `31/32` | `99.4` | `215.8 ms` |
| `llamaindex` | `32/32` | `31/32` | `99.4` | `224.8 ms` |

## By Slice

- `protected`
  - `langgraph`: ok 10/10, keyword pass 9/10, quality 98.0, latency 211.8ms
  - `crewai`: ok 10/10, keyword pass 5/10, quality 81.5, latency 3963.9ms
  - `python_functions`: ok 10/10, keyword pass 9/10, quality 98.0, latency 214.0ms
  - `llamaindex`: ok 10/10, keyword pass 9/10, quality 98.0, latency 212.9ms
- `public`
  - `langgraph`: ok 10/10, keyword pass 8/10, quality 96.0, latency 382.9ms
  - `crewai`: ok 10/10, keyword pass 5/10, quality 89.0, latency 1800.8ms
  - `python_functions`: ok 10/10, keyword pass 10/10, quality 100.0, latency 182.7ms
  - `llamaindex`: ok 10/10, keyword pass 10/10, quality 100.0, latency 184.2ms
- `support`
  - `langgraph`: ok 5/5, keyword pass 5/5, quality 96.4, latency 210.9ms
  - `crewai`: ok 5/5, keyword pass 3/5, quality 92.0, latency 5069.9ms
  - `python_functions`: ok 5/5, keyword pass 5/5, quality 100.0, latency 213.6ms
  - `llamaindex`: ok 5/5, keyword pass 5/5, quality 100.0, latency 218.0ms
- `workflow`
  - `langgraph`: ok 7/7, keyword pass 7/7, quality 100.0, latency 278.6ms
  - `crewai`: ok 7/7, keyword pass 4/7, quality 89.7, latency 5535.4ms
  - `python_functions`: ok 7/7, keyword pass 7/7, quality 100.0, latency 267.1ms
  - `llamaindex`: ok 7/7, keyword pass 7/7, quality 100.0, latency 304.7ms

## Error Types

- `langgraph`: missing_expected_keyword=3, repair_miss=1
- `crewai`: followup_context_drop=3, missing_expected_keyword=15, repetitive_reply=2, unnecessary_clarification=1
- `python_functions`: missing_expected_keyword=1
- `llamaindex`: missing_expected_keyword=1

## Prompt Results

### sendo bem sincero, por que eu colocaria meu filho ai e nao na publica?

- Slice: `public`
- Thread: `rand_public_value_compare` turn `1`
- `langgraph`: status 200, latency 250.2ms, keyword pass `True`, quality `100`, reason `fato institucional canonico deve vir de fonte estruturada`
  answer: Estudar em uma escola publica pode ser uma boa escolha para muitas familias, e eu nao vou te vender uma comparacao vazia. No que esta publicado aqui, os diferenciais desta escola passam por Tutoria academica e projeto de vida, Espaco Maker integrado ao curriculo, Acolhimento estruturado para familias e estudantes. A proposta pedagogica publicada hoje combina Projeto pedagogico laico, com foco em aprendizagem por projetos, cultura digital responsavel, acompanhamento socioemocional e preparacao academica progressiva.. Na pratica, isso aparece em acompanhamento mais proximo da aprendizagem, projeto de vida e combinados pedagogicos mais claros. Escola laica com Ensino Fundamental II e Ensino Medio, acompanhamento tutorial e trilhas academicas no contraturno. Se quiser, eu posso te mostrar isso de forma mais pratica na rotina, na proposta pedagogica ou no contraturno.
- `crewai`: status 200, latency 229.7ms, keyword pass `False`, quality `80`, reason `crewai_protected_auth_required`
  errors: missing_expected_keyword
  answer: Essa consulta depende de autenticacao e vinculo da sua conta no Telegram. Use o portal da escola para gerar o codigo de vinculacao e depois envie o comando /start link_<codigo> ao bot.
- `python_functions`: status 200, latency 170.5ms, keyword pass `True`, quality `100`, reason `fato institucional canonico deve vir de fonte estruturada`
  answer: Estudar em uma escola publica pode ser uma boa escolha para muitas familias, e eu nao vou te vender uma comparacao vazia. No que esta publicado aqui, os diferenciais desta escola passam por Tutoria academica e projeto de vida, Espaco Maker integrado ao curriculo, Acolhimento estruturado para familias e estudantes. A proposta pedagogica publicada hoje combina Projeto pedagogico laico, com foco em aprendizagem por projetos, cultura digital responsavel, acompanhamento socioemocional e preparacao academica progressiva.. Na pratica, isso aparece em acompanhamento mais proximo da aprendizagem, projeto de vida e combinados pedagogicos mais claros. Escola laica com Ensino Fundamental II e Ensino Medio, acompanhamento tutorial e trilhas academicas no contraturno. Se quiser, eu posso te mostrar isso de forma mais pratica na rotina, na proposta pedagogica ou no contraturno.
- `llamaindex`: status 200, latency 185.1ms, keyword pass `True`, quality `100`, reason `fato institucional canonico deve vir de fonte estruturada`
  answer: Estudar em uma escola publica pode ser uma boa escolha para muitas familias, e eu nao vou te vender uma comparacao vazia. No que esta publicado aqui, os diferenciais desta escola passam por Tutoria academica e projeto de vida, Espaco Maker integrado ao curriculo, Acolhimento estruturado para familias e estudantes. A proposta pedagogica publicada hoje combina Projeto pedagogico laico, com foco em aprendizagem por projetos, cultura digital responsavel, acompanhamento socioemocional e preparacao academica progressiva.. Na pratica, isso aparece em acompanhamento mais proximo da aprendizagem, projeto de vida e combinados pedagogicos mais claros. Escola laica com Ensino Fundamental II e Ensino Medio, acompanhamento tutorial e trilhas academicas no contraturno. Se quiser, eu posso te mostrar isso de forma mais pratica na rotina, na proposta pedagogica ou no contraturno.

### mas o que isso muda na pratica no dia a dia?

- Slice: `public`
- Thread: `rand_public_value_compare` turn `2`
- `langgraph`: status 200, latency 186.2ms, keyword pass `True`, quality `100`, reason `fato institucional canonico deve vir de fonte estruturada`
  answer: Na pratica, isso muda em uma rotina com aprendizagem por projetos, acompanhamento mais proximo e referencias claras de tutoria academica. Os pontos que aparecem hoje de forma mais concreta sao Tutoria academica e projeto de vida, Espaco Maker integrado ao curriculo, Acolhimento estruturado para familias e estudantes. Isso aparece no dia a dia em projeto de vida, acompanhamento mais proximo e referencias mais visiveis para familias e estudantes. Isso conversa com uma proposta pedagogica que combina Projeto pedagogico laico, com foco em aprendizagem por projetos, cultura digital responsavel, acompanhamento socioemocional e preparacao academica progressiva..
- `crewai`: status 200, latency 12181.2ms, keyword pass `False`, quality `80`, reason `crewai_public_flow_completed`
  errors: missing_expected_keyword
  answer: Nao consegui concluir essa resposta agora pelo caminho principal configurado. Tente reformular em uma frase mais direta ou repetir em instantes.
- `python_functions`: status 200, latency 183.2ms, keyword pass `True`, quality `100`, reason `fato institucional canonico deve vir de fonte estruturada`
  answer: Na pratica, isso muda em uma rotina com aprendizagem por projetos, acompanhamento mais proximo e referencias claras de tutoria academica. Os pontos que aparecem hoje de forma mais concreta sao Tutoria academica e projeto de vida, Espaco Maker integrado ao curriculo, Acolhimento estruturado para familias e estudantes. Isso aparece no dia a dia em projeto de vida, acompanhamento mais proximo e referencias mais visiveis para familias e estudantes. Isso conversa com uma proposta pedagogica que combina Projeto pedagogico laico, com foco em aprendizagem por projetos, cultura digital responsavel, acompanhamento socioemocional e preparacao academica progressiva..
- `llamaindex`: status 200, latency 192.7ms, keyword pass `True`, quality `100`, reason `fato institucional canonico deve vir de fonte estruturada`
  answer: Na pratica, isso muda em uma rotina com aprendizagem por projetos, acompanhamento mais proximo e referencias claras de tutoria academica. Os pontos que aparecem hoje de forma mais concreta sao Tutoria academica e projeto de vida, Espaco Maker integrado ao curriculo, Acolhimento estruturado para familias e estudantes. Isso aparece no dia a dia em projeto de vida, acompanhamento mais proximo e referencias mais visiveis para familias e estudantes. Isso conversa com uma proposta pedagogica que combina Projeto pedagogico laico, com foco em aprendizagem por projetos, cultura digital responsavel, acompanhamento socioemocional e preparacao academica progressiva..

### entao a base curricular de voces continua seguindo a bncc?

- Slice: `public`
- Thread: `rand_public_value_compare` turn `3`
- `langgraph`: status 200, latency 212.7ms, keyword pass `True`, quality `100`, reason `fato institucional canonico deve vir de fonte estruturada`
  answer: No Ensino Medio, Colegio Horizonte segue a BNCC e um curriculo proprio de aprofundamento academico. Os componentes que aparecem hoje na base publica incluem Lingua Portuguesa e producao textual, Matematica, Biologia, Fisica, Quimica, Historia, Geografia, Lingua Inglesa, alem de projeto de vida, monitorias e trilhas eletivas.
- `crewai`: status 200, latency 1019.5ms, keyword pass `True`, quality `100`, reason `crewai_public_fast_path`
  answer: A base curricular publicada pela escola hoje e a BNCC e o curriculo do Ensino Medio articulado com projeto de vida, producao textual, cultura digital e aprofundamento academico progressivo.
- `python_functions`: status 200, latency 187.3ms, keyword pass `True`, quality `100`, reason `fato institucional canonico deve vir de fonte estruturada`
  answer: No Ensino Medio, Colegio Horizonte segue a BNCC e um curriculo proprio de aprofundamento academico. Os componentes que aparecem hoje na base publica incluem Lingua Portuguesa e producao textual, Matematica, Biologia, Fisica, Quimica, Historia, Geografia, Lingua Inglesa, alem de projeto de vida, monitorias e trilhas eletivas.
- `llamaindex`: status 200, latency 188.6ms, keyword pass `True`, quality `100`, reason `fato institucional canonico deve vir de fonte estruturada`
  answer: No Ensino Medio, Colegio Horizonte segue a BNCC e um curriculo proprio de aprofundamento academico. Os componentes que aparecem hoje na base publica incluem Lingua Portuguesa e producao textual, Matematica, Biologia, Fisica, Quimica, Historia, Geografia, Lingua Inglesa, alem de projeto de vida, monitorias e trilhas eletivas.

### posso enviar documentos por fax ou isso nao existe mais?

- Slice: `public`
- Thread: `rand_public_channels_docs` turn `1`
- `langgraph`: status 200, latency 206.4ms, keyword pass `True`, quality `100`, reason `fato institucional canonico deve vir de fonte estruturada`
  answer: Hoje a escola nao utiliza fax para envio de documentos. Para isso, use portal institucional, email da secretaria, secretaria presencial.
- `crewai`: status 200, latency 229.2ms, keyword pass `False`, quality `80`, reason `crewai_protected_auth_required`
  errors: missing_expected_keyword
  answer: Essa consulta depende de autenticacao e vinculo da sua conta no Telegram. Use o portal da escola para gerar o codigo de vinculacao e depois envie o comando /start link_<codigo> ao bot.
- `python_functions`: status 200, latency 171.6ms, keyword pass `True`, quality `100`, reason `contextual_public_direct_answer`
  answer: Hoje a escola nao utiliza fax para envio de documentos. Para isso, use portal institucional, email da secretaria, secretaria presencial.
- `llamaindex`: status 200, latency 158.9ms, keyword pass `True`, quality `100`, reason `contextual_public_direct_answer`
  answer: Hoje a escola nao utiliza fax para envio de documentos. Para isso, use portal institucional, email da secretaria, secretaria presencial.

### e por telegrama, serve?

- Slice: `public`
- Thread: `rand_public_channels_docs` turn `2`
- `langgraph`: status 200, latency 1973.9ms, keyword pass `True`, quality `100`, reason `retrieval hibrido e o caminho padrao para faq e documentos`
  answer: Hoje a escola nao publica telegrama como canal valido para documentos. Para isso, use portal institucional, email da secretaria, secretaria presencial.
- `crewai`: status 200, latency 984.0ms, keyword pass `True`, quality `100`, reason `crewai_public_fast_path`
  answer: Hoje a escola nao publica telegrama como canal valido. Para documentos, use portal institucional, email da secretaria ou secretaria presencial.
- `python_functions`: status 200, latency 160.1ms, keyword pass `True`, quality `100`, reason `contextual_public_direct_answer`
  answer: Hoje a escola nao publica telegrama como canal valido para documentos. Para isso, use portal institucional, email da secretaria, secretaria presencial.
- `llamaindex`: status 200, latency 180.9ms, keyword pass `True`, quality `100`, reason `contextual_public_direct_answer`
  answer: Hoje a escola nao publica telegrama como canal valido para documentos. Para isso, use portal institucional, email da secretaria, secretaria presencial.

### qual e o caminho certo pra mandar a documentacao?

- Slice: `public`
- Thread: `rand_public_channels_docs` turn `3`
- `langgraph`: status 200, latency 154.7ms, keyword pass `True`, quality `100`, reason `a intencao esta ambigua e exige clarificacao antes de recuperar contexto`
  answer: Sim. O envio inicial de documentos pode ser feito por canal digital.
Hoje os canais mais diretos publicados para isso sao:
- portal institucional
- email da secretaria
- secretaria presencial
No processo de matricula, o envio inicial pode ser digital. A validacao final continua com a secretaria.
O chat aberto nao deve receber documentos completos ou dados sensiveis. Quando possivel, use o portal autenticado ou o email institucional.
- `crewai`: status 200, latency 236.8ms, keyword pass `False`, quality `80`, reason `crewai_protected_auth_required`
  errors: missing_expected_keyword
  answer: Essa consulta depende de autenticacao e vinculo da sua conta no Telegram. Use o portal da escola para gerar o codigo de vinculacao e depois envie o comando /start link_<codigo> ao bot.
- `python_functions`: status 200, latency 158.5ms, keyword pass `True`, quality `100`, reason `contextual_public_direct_answer`
  answer: Sim. O envio inicial de documentos pode ser feito por canal digital.
Hoje os canais mais diretos publicados para isso sao:
- portal institucional
- email da secretaria
- secretaria presencial
No processo de matricula, o envio inicial pode ser digital. A validacao final continua com a secretaria.
O chat aberto nao deve receber documentos completos ou dados sensiveis. Quando possivel, use o portal autenticado ou o email institucional.
- `llamaindex`: status 200, latency 158.3ms, keyword pass `True`, quality `100`, reason `contextual_public_direct_answer`
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
- `langgraph`: status 200, latency 202.6ms, keyword pass `True`, quality `100`, reason `fato institucional canonico deve vir de fonte estruturada`
  answer: Sim. O Colegio Horizonte tem a Biblioteca Aurora. Atendimento ao publico de segunda a sexta, das 7h30 as 18h00.
- `crewai`: status 200, latency 949.3ms, keyword pass `True`, quality `100`, reason `crewai_public_fast_path`
  answer: Sim, a escola tem a Biblioteca Aurora, com atendimento das 7h30 as 18h00.
- `python_functions`: status 200, latency 195.4ms, keyword pass `True`, quality `100`, reason `fato institucional canonico deve vir de fonte estruturada`
  answer: Sim. O Colegio Horizonte tem a Biblioteca Aurora. Atendimento ao publico de segunda a sexta, das 7h30 as 18h00.
- `llamaindex`: status 200, latency 204.6ms, keyword pass `True`, quality `100`, reason `fato institucional canonico deve vir de fonte estruturada`
  answer: Sim. O Colegio Horizonte tem a Biblioteca Aurora. Atendimento ao publico de segunda a sexta, das 7h30 as 18h00.

### como ela se chama e ate que horas funciona?

- Slice: `public`
- Thread: `rand_public_library_realism` turn `2`
- `langgraph`: status 200, latency 207.5ms, keyword pass `False`, quality `80`, reason `fato institucional canonico deve vir de fonte estruturada`
  errors: missing_expected_keyword
  answer: O atendimento presencial de Colegio Horizonte abre as 7h00 e segue ate as 17h30, de segunda a sexta-feira. Se voce estiver falando da biblioteca, ela funciona das 7h30 as 18h00.
- `crewai`: status 200, latency 1025.8ms, keyword pass `True`, quality `90`, reason `crewai_public_fast_path`
  errors: repetitive_reply
  answer: Sim, a escola tem a Biblioteca Aurora, com atendimento das 7h30 as 18h00.
- `python_functions`: status 200, latency 162.1ms, keyword pass `True`, quality `100`, reason `contextual_public_direct_answer`
  answer: A biblioteca se chama Biblioteca Aurora e funciona de segunda a sexta, das 7h30 as 18h00.
- `llamaindex`: status 200, latency 151.6ms, keyword pass `True`, quality `100`, reason `contextual_public_direct_answer`
  answer: A biblioteca se chama Biblioteca Aurora e funciona de segunda a sexta, das 7h30 as 18h00.

### quando comeca a matricula do proximo ciclo?

- Slice: `public`
- Thread: `rand_public_timeline_visit` turn `1`
- `langgraph`: status 200, latency 211.6ms, keyword pass `True`, quality `100`, reason `datas institucionais publicas devem vir de leitura estruturada e auditavel`
  answer: O ciclo publico de matricula para 2026 foi aberto em 6 de outubro de 2025, com pre-cadastro, visita orientada opcional e triagem inicial de documentos. O atendimento comercial segue enquanto houver vagas por segmento.
- `crewai`: status 200, latency 246.6ms, keyword pass `False`, quality `80`, reason `crewai_protected_auth_required`
  errors: missing_expected_keyword
  answer: Essa consulta depende de autenticacao e vinculo da sua conta no Telegram. Use o portal da escola para gerar o codigo de vinculacao e depois envie o comando /start link_<codigo> ao bot.
- `python_functions`: status 200, latency 238.8ms, keyword pass `True`, quality `100`, reason `datas institucionais publicas devem vir de leitura estruturada e auditavel`
  answer: O ciclo publico de matricula para 2026 foi aberto em 6 de outubro de 2025, com pre-cadastro, visita orientada opcional e triagem inicial de documentos. O atendimento comercial segue enquanto houver vagas por segmento.
- `llamaindex`: status 200, latency 230.3ms, keyword pass `True`, quality `100`, reason `datas institucionais publicas devem vir de leitura estruturada e auditavel`
  answer: O ciclo publico de matricula para 2026 foi aberto em 6 de outubro de 2025, com pre-cadastro, visita orientada opcional e triagem inicial de documentos. O atendimento comercial segue enquanto houver vagas por segmento.

### depois disso, quando as aulas comecam?

- Slice: `public`
- Thread: `rand_public_timeline_visit` turn `2`
- `langgraph`: status 200, latency 223.1ms, keyword pass `False`, quality `80`, reason `fato institucional canonico deve vir de fonte estruturada`
  errors: missing_expected_keyword
  answer: Colegio Horizonte: Escola laica com Ensino Fundamental II e Ensino Medio, acompanhamento tutorial e trilhas academicas no contraturno.
- `crewai`: status 200, latency 905.7ms, keyword pass `True`, quality `100`, reason `crewai_public_fast_path`
  answer: As aulas do Ensino Fundamental II e do Ensino Medio comecam em 2 de fevereiro de 2026.
- `python_functions`: status 200, latency 199.3ms, keyword pass `True`, quality `100`, reason `contextual_public_direct_answer`
  answer: As aulas do Ensino Fundamental II e do Ensino Medio comecam em 2 de fevereiro de 2026. A semana de acolhimento do 6o ano e da primeira serie ocorre entre 2 e 6 de fevereiro.
- `llamaindex`: status 200, latency 190.8ms, keyword pass `True`, quality `100`, reason `contextual_public_direct_answer`
  answer: As aulas do Ensino Fundamental II e do Ensino Medio comecam em 2 de fevereiro de 2026. A semana de acolhimento do 6o ano e da primeira serie ocorre entre 2 e 6 de fevereiro.

### estou logado como?

- Slice: `protected`
- Thread: `rand_protected_identity_scope` turn `1`
- `langgraph`: status 200, latency 165.3ms, keyword pass `True`, quality `100`, reason `identidade da conta autenticada exige leitura protegida e minimizada`
  answer: Voce esta falando aqui como Maria Oliveira, no perfil de responsavel. Sua conta esta vinculada a Lucas Oliveira e Ana Oliveira. Por aqui eu consigo consultar notas, faltas, proximas provas, matricula, financeiro, boletos, dentro das permissoes dessa vinculacao.
- `crewai`: status 200, latency 243.4ms, keyword pass `True`, quality `100`, reason `crewai_protected_identity_backstop`
  answer: Voce esta autenticado aqui como Maria Oliveira. Sua conta esta vinculada a Lucas Oliveira, Ana Oliveira e pode consultar notas, frequencia, avaliacoes, documentacao e financeiro desses alunos.
- `python_functions`: status 200, latency 152.6ms, keyword pass `True`, quality `100`, reason `identidade da conta autenticada exige leitura protegida e minimizada`
  answer: Voce esta falando aqui como Maria Oliveira, no perfil de responsavel. Sua conta esta vinculada a Lucas Oliveira e Ana Oliveira. Por aqui eu consigo consultar notas, faltas, proximas provas, matricula, financeiro, boletos, dentro das permissoes dessa vinculacao.
- `llamaindex`: status 200, latency 162.3ms, keyword pass `True`, quality `100`, reason `identidade da conta autenticada exige leitura protegida e minimizada`
  answer: Voce esta falando aqui como Maria Oliveira, no perfil de responsavel. Sua conta esta vinculada a Lucas Oliveira e Ana Oliveira. Por aqui eu consigo consultar notas, faltas, proximas provas, matricula, financeiro, boletos, dentro das permissoes dessa vinculacao.

### e eu consigo ver o que exatamente por aqui?

- Slice: `protected`
- Thread: `rand_protected_identity_scope` turn `2`
- `langgraph`: status 200, latency 178.8ms, keyword pass `True`, quality `100`, reason `dados estruturados devem passar por service deterministico`
  answer: Voce ja esta autenticado por aqui e sua conta esta vinculada a Lucas Oliveira e Ana Oliveira. Por este canal eu consigo consultar notas, faltas, proximas provas, matricula, financeiro, boletos, dentro das permissoes dessa vinculacao. Se quiser, me diga algo como "notas do Lucas", "faltas da Ana" ou "financeiro do Lucas".
- `crewai`: status 200, latency 12049.8ms, keyword pass `False`, quality `55`, reason `crewai_public_flow_completed`
  errors: followup_context_drop, missing_expected_keyword
  answer: Nao consegui concluir essa resposta agora pelo caminho principal configurado. Tente reformular em uma frase mais direta ou repetir em instantes.
- `python_functions`: status 200, latency 180.2ms, keyword pass `True`, quality `100`, reason `dados estruturados devem passar por service deterministico`
  answer: Voce ja esta autenticado por aqui e sua conta esta vinculada a Lucas Oliveira e Ana Oliveira. Por este canal eu consigo consultar notas, faltas, proximas provas, matricula, financeiro, boletos, dentro das permissoes dessa vinculacao. Se quiser, me diga algo como "notas do Lucas", "faltas da Ana" ou "financeiro do Lucas".
- `llamaindex`: status 200, latency 196.0ms, keyword pass `True`, quality `100`, reason `dados estruturados devem passar por service deterministico`
  answer: Voce ja esta autenticado por aqui e sua conta esta vinculada a Lucas Oliveira e Ana Oliveira. Por este canal eu consigo consultar notas, faltas, proximas provas, matricula, financeiro, boletos, dentro das permissoes dessa vinculacao. Se quiser, me diga algo como "notas do Lucas", "faltas da Ana" ou "financeiro do Lucas".

### quais filhos eu tenho matriculados nessa conta?

- Slice: `protected`
- Thread: `rand_protected_identity_scope` turn `3`
- `langgraph`: status 200, latency 281.7ms, keyword pass `True`, quality `100`, reason `dados estruturados devem passar por service deterministico`
  answer: Resumo financeiro das contas vinculadas:
- Total de faturas em aberto: 1
- Total de faturas vencidas: 0
- Lucas Oliveira: 0 em aberto, 0 vencidas
  2026-03: vencimento 2026-03-10, status paga, valor 1450.00
- Ana Oliveira: 1 em aberto, 0 vencidas
  2026-03: vencimento 2026-03-10, status em aberto, valor 1450.00
- `crewai`: status 200, latency 12013.6ms, keyword pass `False`, quality `70`, reason `crewai_public_flow_completed`
  errors: missing_expected_keyword, repetitive_reply
  answer: Nao consegui concluir essa resposta agora pelo caminho principal configurado. Tente reformular em uma frase mais direta ou repetir em instantes.
- `python_functions`: status 200, latency 294.9ms, keyword pass `True`, quality `100`, reason `dados estruturados devem passar por service deterministico`
  answer: Resumo financeiro das contas vinculadas:
- Total de faturas em aberto: 1
- Total de faturas vencidas: 0
- Lucas Oliveira: 0 em aberto, 0 vencidas
  2026-03: vencimento 2026-03-10, status paga, valor 1450.00
- Ana Oliveira: 1 em aberto, 0 vencidas
  2026-03: vencimento 2026-03-10, status em aberto, valor 1450.00
- `llamaindex`: status 200, latency 277.6ms, keyword pass `True`, quality `100`, reason `dados estruturados devem passar por service deterministico`
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
- `langgraph`: status 200, latency 231.0ms, keyword pass `False`, quality `80`, reason `status administrativo autenticado exige service deterministico`
  errors: missing_expected_keyword
  answer: Situacao documental de Ana Oliveira hoje: com pendencias.
- `crewai`: status 200, latency 554.5ms, keyword pass `False`, quality `80`, reason `crewai_protected_fast_path`
  errors: missing_expected_keyword
  answer: A situacao documental de Ana Oliveira hoje esta com pendencias.
- `python_functions`: status 200, latency 208.0ms, keyword pass `False`, quality `80`, reason `status administrativo autenticado exige service deterministico`
  errors: missing_expected_keyword
  answer: Situacao documental de Ana Oliveira hoje: com pendencias.
- `llamaindex`: status 200, latency 217.8ms, keyword pass `False`, quality `80`, reason `status administrativo autenticado exige service deterministico`
  errors: missing_expected_keyword
  answer: Situacao documental de Ana Oliveira hoje: com pendencias.

### o que falta?

- Slice: `protected`
- Thread: `rand_protected_docs_focus` turn `2`
- `langgraph`: status 200, latency 214.6ms, keyword pass `True`, quality `100`, reason `status administrativo autenticado exige service deterministico`
  answer: Hoje, o proximo passo do seu cadastro e este: Envie o comprovante atualizado pela secretaria ou pelo canal de documentos para concluir a conferência.
- `crewai`: status 200, latency 497.1ms, keyword pass `True`, quality `100`, reason `crewai_protected_fast_path`
  answer: No momento, ainda falta para Ana Oliveira: Documentacao escolar do aluno. Ainda falta anexar um comprovante de residencia atualizado para Ana Oliveira concluir a conferencia documental.
- `python_functions`: status 200, latency 228.3ms, keyword pass `True`, quality `100`, reason `status administrativo autenticado exige service deterministico`
  answer: Hoje, o proximo passo do seu cadastro e este: Envie o comprovante atualizado pela secretaria ou pelo canal de documentos para concluir a conferência.
- `llamaindex`: status 200, latency 229.2ms, keyword pass `True`, quality `100`, reason `status administrativo autenticado exige service deterministico`
  answer: Hoje, o proximo passo do seu cadastro e este: Envie o comprovante atualizado pela secretaria ou pelo canal de documentos para concluir a conferência.

### e a documentacao do lucas?

- Slice: `protected`
- Thread: `rand_protected_docs_focus` turn `3`
- `langgraph`: status 200, latency 221.0ms, keyword pass `True`, quality `100`, reason `status administrativo autenticado exige service deterministico`
  answer: Situacao documental de Lucas Oliveira hoje: regular.
- Identificacao escolar do aluno: regular. Codigo de matricula: MAT-2026-001
- Responsavel vinculado: regular. Maria Oliveira
- Documentacao escolar do aluno: regular. A documentacao escolar de Lucas Oliveira esta conferida e sem pendencias relevantes nesta base de testes.
- `crewai`: status 200, latency 647.1ms, keyword pass `True`, quality `100`, reason `crewai_protected_fast_path`
  answer: A situacao documental de Lucas Oliveira hoje esta regular e completa.
- `python_functions`: status 200, latency 216.3ms, keyword pass `True`, quality `100`, reason `status administrativo autenticado exige service deterministico`
  answer: Situacao documental de Lucas Oliveira hoje: regular.
- Identificacao escolar do aluno: regular. Codigo de matricula: MAT-2026-001
- Responsavel vinculado: regular. Maria Oliveira
- Documentacao escolar do aluno: regular. A documentacao escolar de Lucas Oliveira esta conferida e sem pendencias relevantes nesta base de testes.
- `llamaindex`: status 200, latency 207.4ms, keyword pass `True`, quality `100`, reason `status administrativo autenticado exige service deterministico`
  answer: Situacao documental de Lucas Oliveira hoje: regular.
- Identificacao escolar do aluno: regular. Codigo de matricula: MAT-2026-001
- Responsavel vinculado: regular. Maria Oliveira
- Documentacao escolar do aluno: regular. A documentacao escolar de Lucas Oliveira esta conferida e sem pendencias relevantes nesta base de testes.

### e se eu perguntar do joao?

- Slice: `protected`
- Thread: `rand_protected_docs_focus` turn `4`
- `langgraph`: status 200, latency 154.1ms, keyword pass `True`, quality `100`, reason `status administrativo autenticado exige service deterministico`
  answer: Hoje eu nao encontrei Joao entre os alunos vinculados a esta conta. No momento, os alunos que aparecem aqui sao: Lucas Oliveira (MAT-2026-001), Ana Oliveira (MAT-2026-002). Se quiser, me diga qual deles voce quer consultar.
- `crewai`: status 200, latency 12106.5ms, keyword pass `False`, quality `55`, reason `crewai_public_flow_completed`
  errors: followup_context_drop, missing_expected_keyword
  answer: Nao consegui concluir essa resposta agora pelo caminho principal configurado. Tente reformular em uma frase mais direta ou repetir em instantes.
- `python_functions`: status 200, latency 176.4ms, keyword pass `True`, quality `100`, reason `status administrativo autenticado exige service deterministico`
  answer: Hoje eu nao encontrei Joao entre os alunos vinculados a esta conta. No momento, os alunos que aparecem aqui sao: Lucas Oliveira (MAT-2026-001), Ana Oliveira (MAT-2026-002). Se quiser, me diga qual deles voce quer consultar.
- `llamaindex`: status 200, latency 175.5ms, keyword pass `True`, quality `100`, reason `status administrativo autenticado exige service deterministico`
  answer: Hoje eu nao encontrei Joao entre os alunos vinculados a esta conta. No momento, os alunos que aparecem aqui sao: Lucas Oliveira (MAT-2026-001), Ana Oliveira (MAT-2026-002). Se quiser, me diga qual deles voce quer consultar.

### quero ver as notas do lucas

- Slice: `protected`
- Thread: `rand_protected_academic_finance` turn `1`
- `langgraph`: status 200, latency 234.6ms, keyword pass `True`, quality `100`, reason `dados estruturados devem passar por service deterministico`
  answer: Notas de Lucas Oliveira:
- Biologia - Avaliacao B1: 8.40/10.00
- Educacao Fisica - Avaliacao 2026-B1 - EF: 6.40/10.00
- Filosofia - Avaliacao 2026-B1 - FIL: 7.00/10.00
- Fisica - Avaliacao 2026-B1 - FIS: 5.80/10.00
- Geografia - Avaliacao 2026-B1 - GEO: 6.40/10.00
- Historia - Avaliacao 2026-B1 - HIS: 6.70/10.00
- Ingles - Avaliacao B1: 8.90/10.00
- Matematica - Avaliacao B1: 8.70/10.00
- `crewai`: status 200, latency 490.5ms, keyword pass `True`, quality `100`, reason `crewai_protected_fast_path`
  answer: As notas mais recentes de Lucas Oliveira incluem Biologia: 8.40/10.00; Educacao Fisica: 6.40/10.00; Filosofia: 7.00/10.00; Fisica: 5.80/10.00; Geografia: 6.40/10.00; Historia: 6.70/10.00; Ingles: 8.90/10.00; Matematica: 8.70/10.00.
- `python_functions`: status 200, latency 242.7ms, keyword pass `True`, quality `100`, reason `dados estruturados devem passar por service deterministico`
  answer: Notas de Lucas Oliveira:
- Biologia - Avaliacao B1: 8.40/10.00
- Educacao Fisica - Avaliacao 2026-B1 - EF: 6.40/10.00
- Filosofia - Avaliacao 2026-B1 - FIL: 7.00/10.00
- Fisica - Avaliacao 2026-B1 - FIS: 5.80/10.00
- Geografia - Avaliacao 2026-B1 - GEO: 6.40/10.00
- Historia - Avaliacao 2026-B1 - HIS: 6.70/10.00
- Ingles - Avaliacao B1: 8.90/10.00
- Matematica - Avaliacao B1: 8.70/10.00
- `llamaindex`: status 200, latency 241.1ms, keyword pass `True`, quality `100`, reason `dados estruturados devem passar por service deterministico`
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
- `langgraph`: status 200, latency 225.7ms, keyword pass `True`, quality `100`, reason `dados estruturados devem passar por service deterministico`
  answer: Hoje nao encontrei valor em aberto para Lucas Oliveira neste recorte.
- `crewai`: status 200, latency 518.5ms, keyword pass `True`, quality `100`, reason `crewai_protected_fast_path`
  answer: No momento, nao encontrei valor em aberto para Lucas Oliveira neste recorte.
- `python_functions`: status 200, latency 217.4ms, keyword pass `True`, quality `100`, reason `dados estruturados devem passar por service deterministico`
  answer: Hoje nao encontrei valor em aberto para Lucas Oliveira neste recorte.
- `llamaindex`: status 200, latency 207.7ms, keyword pass `True`, quality `100`, reason `dados estruturados devem passar por service deterministico`
  answer: Hoje nao encontrei valor em aberto para Lucas Oliveira neste recorte.

### e a proxima data de pagamento?

- Slice: `protected`
- Thread: `rand_protected_academic_finance` turn `3`
- `langgraph`: status 200, latency 211.2ms, keyword pass `True`, quality `100`, reason `dados estruturados devem passar por service deterministico`
  answer: Hoje a cobranca pendente mais imediata de Lucas Oliveira e a referencia 2026-03, com vencimento em 10 de marco de 2026 e valor 1450.00. Status atual: paga.
- `crewai`: status 200, latency 517.7ms, keyword pass `False`, quality `55`, reason `crewai_protected_fast_path`
  errors: followup_context_drop, missing_expected_keyword
  answer: O proximo pagamento de Lucas Oliveira vence em 2026-03-10 no valor de 1450.00.
- `python_functions`: status 200, latency 222.9ms, keyword pass `True`, quality `100`, reason `dados estruturados devem passar por service deterministico`
  answer: Hoje a cobranca pendente mais imediata de Lucas Oliveira e a referencia 2026-03, com vencimento em 10 de marco de 2026 e valor 1450.00. Status atual: paga.
- `llamaindex`: status 200, latency 214.0ms, keyword pass `True`, quality `100`, reason `dados estruturados devem passar por service deterministico`
  answer: Hoje a cobranca pendente mais imediata de Lucas Oliveira e a referencia 2026-03, com vencimento em 10 de marco de 2026 e valor 1450.00. Status atual: paga.

### preciso falar com o financeiro

- Slice: `support`
- Thread: `rand_support_reroute` turn `1`
- `langgraph`: status 200, latency 185.4ms, keyword pass `True`, quality `100`, reason `o usuario demonstrou necessidade de atendimento humano ou operacional`
  answer: Sua solicitacao ja estava registrada na fila de financeiro. Protocolo: ATD-20260330-2DCEFBD7. Status atual: queued.
- `crewai`: status 200, latency 257.8ms, keyword pass `True`, quality `100`, reason `support_handoff_rerouted`
  answer: Sem problema, agora segui com a fila de financeiro. Sua solicitacao ja estava registrada na fila de financeiro. Protocolo: ATD-20260330-B8BEEDE3. Status atual: queued.
- `python_functions`: status 200, latency 193.0ms, keyword pass `True`, quality `100`, reason `o usuario demonstrou necessidade de atendimento humano ou operacional`
  answer: Sua solicitacao ja estava registrada na fila de financeiro. Protocolo: ATD-20260330-186E5165. Status atual: queued.
- `llamaindex`: status 200, latency 186.0ms, keyword pass `True`, quality `100`, reason `o usuario demonstrou necessidade de atendimento humano ou operacional`
  answer: Sua solicitacao ja estava registrada na fila de financeiro. Protocolo: ATD-20260330-F7DF9A0F. Status atual: queued.

### qual o protocolo?

- Slice: `support`
- Thread: `rand_support_reroute` turn `2`
- `langgraph`: status 200, latency 203.3ms, keyword pass `True`, quality `100`, reason `a solicitacao pode ser executada por workflow estruturado com protocolo`
  answer: O protocolo atual do seu atendimento e ATD-20260330-2DCEFBD7. Se quiser, eu posso te dizer o status atual ou resumir o que ja foi registrado.
- `crewai`: status 200, latency 220.4ms, keyword pass `True`, quality `100`, reason `workflow_protocol_lookup`
  answer: O protocolo da sua solicitacao e ATD-20260330-B8BEEDE3. - Ticket operacional: ATD-20260330-B8BEEDE3 - Area responsavel: None Se quiser, eu tambem posso resumir o pedido ou verificar o status atual.
- `python_functions`: status 200, latency 202.6ms, keyword pass `True`, quality `100`, reason `a solicitacao pode ser executada por workflow estruturado com protocolo`
  answer: O protocolo atual do seu atendimento e ATD-20260330-186E5165. Se quiser, eu posso te dizer o status atual ou resumir o que ja foi registrado.
- `llamaindex`: status 200, latency 197.8ms, keyword pass `True`, quality `100`, reason `a solicitacao pode ser executada por workflow estruturado com protocolo`
  answer: O protocolo atual do seu atendimento e ATD-20260330-F7DF9A0F. Se quiser, eu posso te dizer o status atual ou resumir o que ja foi registrado.

### mudei de ideia, quero secretaria

- Slice: `support`
- Thread: `rand_support_reroute` turn `3`
- `langgraph`: status 200, latency 189.5ms, keyword pass `True`, quality `82`, reason `o usuario demonstrou necessidade de atendimento humano ou operacional`
  errors: repair_miss
  answer: Sua solicitacao ja estava registrada na fila de secretaria. Protocolo: ATD-20260330-2DCEFBD7. Status atual: queued.
- `crewai`: status 200, latency 246.7ms, keyword pass `True`, quality `100`, reason `support_handoff_rerouted`
  answer: Sem problema, agora segui com a fila de secretaria. Sua solicitacao ja estava registrada na fila de secretaria. Protocolo: ATD-20260330-B8BEEDE3. Status atual: queued.
- `python_functions`: status 200, latency 182.1ms, keyword pass `True`, quality `100`, reason `o usuario demonstrou necessidade de atendimento humano ou operacional`
  answer: Sem problema, ajustei isso por aqui.

Sua solicitacao ja estava registrada na fila de secretaria. Protocolo: ATD-20260330-186E5165. Status atual: queued.
- `llamaindex`: status 200, latency 178.5ms, keyword pass `True`, quality `100`, reason `o usuario demonstrou necessidade de atendimento humano ou operacional`
  answer: Sem problema, ajustei isso por aqui.

Sua solicitacao ja estava registrada na fila de secretaria. Protocolo: ATD-20260330-F7DF9A0F. Status atual: queued.

### e como esta esse atendimento?

- Slice: `support`
- Thread: `rand_support_status_summary` turn `1`
- `langgraph`: status 200, latency 196.0ms, keyword pass `True`, quality `100`, reason `a solicitacao pode ser executada por workflow estruturado com protocolo`
  answer: Ainda nao encontrei um protocolo recente nesta conversa para consultar o status da fila. Se quiser, me diga o codigo que comeca com VIS, REQ ou ATD, ou me lembre se o assunto era visita, direcao, financeiro ou secretaria.
- `crewai`: status 200, latency 12138.3ms, keyword pass `False`, quality `80`, reason `crewai_public_flow_timeout`
  errors: missing_expected_keyword
  answer: A Secretaria e Protocolo do Colégio Pedro II funciona de segunda a sexta-feira, das 9h às 16h, para atendimento ao público, oferecendo informações e recebimento de documentos.
- `python_functions`: status 200, latency 246.6ms, keyword pass `True`, quality `100`, reason `a solicitacao pode ser executada por workflow estruturado com protocolo`
  answer: Ainda nao encontrei um protocolo recente nesta conversa para consultar o status da fila. Se quiser, me diga o codigo que comeca com VIS, REQ ou ATD, ou me lembre se o assunto era visita, direcao, financeiro ou secretaria.
- `llamaindex`: status 200, latency 275.1ms, keyword pass `True`, quality `100`, reason `a solicitacao pode ser executada por workflow estruturado com protocolo`
  answer: Ainda nao encontrei um protocolo recente nesta conversa para consultar o status da fila. Se quiser, me diga o codigo que comeca com VIS, REQ ou ATD, ou me lembre se o assunto era visita, direcao, financeiro ou secretaria.

### resume pra mim

- Slice: `support`
- Thread: `rand_support_status_summary` turn `2`
- `langgraph`: status 200, latency 280.3ms, keyword pass `True`, quality `100`, reason `a solicitacao pode ser executada por workflow estruturado com protocolo`
  answer: Ainda nao encontrei um protocolo recente nesta conversa para montar o resumo do pedido. Se quiser, me diga o codigo que comeca com VIS, REQ ou ATD, ou me lembre se o assunto era visita, direcao, financeiro ou secretaria.
- `crewai`: status 200, latency 12486.4ms, keyword pass `False`, quality `80`, reason `crewai_public_flow_completed`
  errors: missing_expected_keyword
  answer: Nao consegui concluir essa resposta agora pelo caminho principal configurado. Tente reformular em uma frase mais direta ou repetir em instantes.
- `python_functions`: status 200, latency 243.8ms, keyword pass `True`, quality `100`, reason `a solicitacao pode ser executada por workflow estruturado com protocolo`
  answer: Ainda nao encontrei um protocolo recente nesta conversa para montar o resumo do pedido. Se quiser, me diga o codigo que comeca com VIS, REQ ou ATD, ou me lembre se o assunto era visita, direcao, financeiro ou secretaria.
- `llamaindex`: status 200, latency 252.5ms, keyword pass `True`, quality `100`, reason `a solicitacao pode ser executada por workflow estruturado com protocolo`
  answer: Ainda nao encontrei um protocolo recente nesta conversa para montar o resumo do pedido. Se quiser, me diga o codigo que comeca com VIS, REQ ou ATD, ou me lembre se o assunto era visita, direcao, financeiro ou secretaria.

### da pra marcar uma visita na quinta a tarde?

- Slice: `workflow`
- Thread: `rand_workflow_visit` turn `1`
- `langgraph`: status 200, latency 260.6ms, keyword pass `True`, quality `100`, reason `a solicitacao pode ser executada por workflow estruturado com protocolo`
  answer: Pedido de visita atualizado com a fila de admissions. Protocolo: VIS-20260330-E6B93B. Ticket operacional: ATD-20260330-4FEEAD3E. Nova preferencia: 02/04/2026 - tarde. Admissions valida a nova janela e retorna com a confirmacao.
- `crewai`: status 200, latency 323.3ms, keyword pass `True`, quality `100`, reason `workflow_visit_create`
  answer: Pedido de visita registrado para o Colegio Horizonte. Protocolo: VIS-20260330-A39E9E. Preferencia informada: 02/04/2026 - tarde. Fila responsavel: admissoes. Ticket operacional: ATD-20260330-711EC5B4. A equipe comercial valida a janela e retorna com a confirmacao.
- `python_functions`: status 200, latency 280.5ms, keyword pass `True`, quality `100`, reason `a solicitacao pode ser executada por workflow estruturado com protocolo`
  answer: Pedido de visita registrado para o Colegio Horizonte. Protocolo: VIS-20260330-7754B4. Preferencia informada: 2026-04-02 - tarde. Fila responsavel: admissoes. Ticket operacional: ATD-20260330-6267A8A9. A equipe comercial valida a janela e retorna com a confirmacao.
- `llamaindex`: status 200, latency 280.2ms, keyword pass `True`, quality `100`, reason `a solicitacao pode ser executada por workflow estruturado com protocolo`
  answer: Pedido de visita registrado para o Colegio Horizonte. Protocolo: VIS-20260330-2E3086. Preferencia informada: 2026-04-02 - tarde. Fila responsavel: admissoes. Ticket operacional: ATD-20260330-5ECB0956. A equipe comercial valida a janela e retorna com a confirmacao.

### me fala o protocolo dessa visita

- Slice: `workflow`
- Thread: `rand_workflow_visit` turn `2`
- `langgraph`: status 200, latency 267.5ms, keyword pass `True`, quality `100`, reason `a solicitacao pode ser executada por workflow estruturado com protocolo`
  answer: O protocolo da sua visita e VIS-20260330-E6B93B. Ticket operacional: ATD-20260330-4FEEAD3E. Preferencia registrada: 02/04/2026 - tarde. Se quiser, eu tambem posso te dizer o status, remarcar ou cancelar a visita.
- `crewai`: status 200, latency 268.0ms, keyword pass `True`, quality `100`, reason `workflow_protocol_lookup`
  answer: O protocolo da sua visita e VIS-20260330-A39E9E. - Ticket operacional: ATD-20260330-711EC5B4 - Preferencia registrada: 02/04/2026 - tarde Se quiser, eu tambem posso te dizer o status, remarcar ou cancelar a visita.
- `python_functions`: status 200, latency 276.2ms, keyword pass `True`, quality `100`, reason `a solicitacao pode ser executada por workflow estruturado com protocolo`
  answer: O protocolo da sua visita e VIS-20260330-7754B4. Ticket operacional: ATD-20260330-6267A8A9. Preferencia registrada: 02/04/2026 - tarde. Se quiser, eu tambem posso te dizer o status, remarcar ou cancelar a visita.
- `llamaindex`: status 200, latency 251.3ms, keyword pass `True`, quality `100`, reason `a solicitacao pode ser executada por workflow estruturado com protocolo`
  answer: O protocolo da sua visita e VIS-20260330-2E3086. Ticket operacional: ATD-20260330-5ECB0956. Preferencia registrada: 02/04/2026 - tarde. Se quiser, eu tambem posso te dizer o status, remarcar ou cancelar a visita.

### e se eu precisar remarcar?

- Slice: `workflow`
- Thread: `rand_workflow_visit` turn `3`
- `langgraph`: status 200, latency 266.1ms, keyword pass `True`, quality `100`, reason `a solicitacao pode ser executada por workflow estruturado com protocolo`
  answer: Consigo remarcar a visita por aqui. Protocolo: VIS-20260330-E6B93B. Ticket operacional: ATD-20260330-4FEEAD3E. Me diga pelo menos o novo dia ou a janela desejada, por exemplo: "remarque para sexta de manha" ou "troque para 28/03 as 10h".
- `crewai`: status 200, latency 255.4ms, keyword pass `True`, quality `100`, reason `workflow_visit_reschedule_guidance`
  answer: Se voce precisar remarcar, me passe o protocolo VIS-20260330-A39E9E ou o novo horario desejado que eu sigo com essa atualizacao para a fila de admissoes.
- `python_functions`: status 200, latency 264.5ms, keyword pass `True`, quality `100`, reason `a solicitacao pode ser executada por workflow estruturado com protocolo`
  answer: Consigo remarcar a visita por aqui. Protocolo: VIS-20260330-7754B4. Ticket operacional: ATD-20260330-6267A8A9. Me diga pelo menos o novo dia ou a janela desejada, por exemplo: "remarque para sexta de manha" ou "troque para 28/03 as 10h".
- `llamaindex`: status 200, latency 321.3ms, keyword pass `True`, quality `100`, reason `a solicitacao pode ser executada por workflow estruturado com protocolo`
  answer: Consigo remarcar a visita por aqui. Protocolo: VIS-20260330-2E3086. Ticket operacional: ATD-20260330-5ECB0956. Me diga pelo menos o novo dia ou a janela desejada, por exemplo: "remarque para sexta de manha" ou "troque para 28/03 as 10h".

### entao remarca pra sexta de manha

- Slice: `workflow`
- Thread: `rand_workflow_visit` turn `4`
- `langgraph`: status 200, latency 265.2ms, keyword pass `True`, quality `100`, reason `a solicitacao pode ser executada por workflow estruturado com protocolo`
  answer: Pedido de visita atualizado com a fila de admissions. Protocolo: VIS-20260330-E6B93B. Ticket operacional: ATD-20260330-4FEEAD3E. Nova preferencia: 03/04/2026 - manha. Admissions valida a nova janela e retorna com a confirmacao.
- `crewai`: status 200, latency 12545.9ms, keyword pass `False`, quality `80`, reason `crewai_public_flow_completed`
  errors: missing_expected_keyword
  answer: Nao consegui concluir essa resposta agora pelo caminho principal configurado. Tente reformular em uma frase mais direta ou repetir em instantes.
- `python_functions`: status 200, latency 278.0ms, keyword pass `True`, quality `100`, reason `a solicitacao pode ser executada por workflow estruturado com protocolo`
  answer: Pedido de visita atualizado com a fila de admissions. Protocolo: VIS-20260330-7754B4. Ticket operacional: ATD-20260330-6267A8A9. Nova preferencia: 03/04/2026 - manha. Admissions valida a nova janela e retorna com a confirmacao.
- `llamaindex`: status 200, latency 388.5ms, keyword pass `True`, quality `100`, reason `a solicitacao pode ser executada por workflow estruturado com protocolo`
  answer: Pedido de visita atualizado com a fila de admissions. Protocolo: VIS-20260330-2E3086. Ticket operacional: ATD-20260330-5ECB0956. Nova preferencia: 03/04/2026 - manha. Admissions valida a nova janela e retorna com a confirmacao.

### quero protocolar um pedido pra direcao sobre reforco de seguranca na saida

- Slice: `workflow`
- Thread: `rand_workflow_request` turn `1`
- `langgraph`: status 200, latency 359.1ms, keyword pass `True`, quality `100`, reason `a solicitacao pode ser executada por workflow estruturado com protocolo`
  answer: Solicitacao institucional registrada para direcao. Protocolo: REQ-20260330-E70B0C. Assunto: quero protocolar um pedido pra direcao sobre reforco de seguranca na saida. Fila responsavel: direcao. Ticket operacional: ATD-20260330-7E9C3A29. A equipe faz a triagem inicial e segue o retorno pelo fluxo institucional.
- `crewai`: status 200, latency 327.5ms, keyword pass `True`, quality `100`, reason `support_handoff_reused`
  answer: Sua solicitacao ja estava registrada na fila de direcao. Protocolo: ATD-20260330-38DD7C4C. Status atual: queued.
- `python_functions`: status 200, latency 283.3ms, keyword pass `True`, quality `100`, reason `a solicitacao pode ser executada por workflow estruturado com protocolo`
  answer: Solicitacao institucional registrada para direcao. Protocolo: REQ-20260330-444286. Assunto: quero protocolar um pedido pra direcao sobre reforco de seguranca na saida. Fila responsavel: direcao. Ticket operacional: ATD-20260330-EA1B5AA8. A equipe faz a triagem inicial e segue o retorno pelo fluxo institucional.
- `llamaindex`: status 200, latency 272.6ms, keyword pass `True`, quality `100`, reason `a solicitacao pode ser executada por workflow estruturado com protocolo`
  answer: Solicitacao institucional registrada para direcao. Protocolo: REQ-20260330-4BB00C. Assunto: quero protocolar um pedido pra direcao sobre reforco de seguranca na saida. Fila responsavel: direcao. Ticket operacional: ATD-20260330-7653B5BB. A equipe faz a triagem inicial e segue o retorno pelo fluxo institucional.

### complementa dizendo que isso pesa mais nas sextas

- Slice: `workflow`
- Thread: `rand_workflow_request` turn `2`
- `langgraph`: status 200, latency 264.5ms, keyword pass `True`, quality `100`, reason `a solicitacao pode ser executada por workflow estruturado com protocolo`
  answer: Complemento registrado na fila de direcao. Protocolo: REQ-20260330-E70B0C. Ticket operacional: ATD-20260330-7E9C3A29. Novo complemento: isso pesa mais nas sextas. A equipe responsavel recebe essa atualizacao no mesmo fluxo do pedido.
- `crewai`: status 200, latency 12484.5ms, keyword pass `False`, quality `68`, reason `crewai_public_flow_timeout`
  errors: missing_expected_keyword, unnecessary_clarification
  answer: Para que eu possa te ajudar melhor, você poderia me explicar o que significa "pesa mais nas sextas"? Assim consigo entender o que você precisa saber.
- `python_functions`: status 200, latency 242.8ms, keyword pass `True`, quality `100`, reason `a solicitacao pode ser executada por workflow estruturado com protocolo`
  answer: Complemento registrado na fila de direcao. Protocolo: REQ-20260330-444286. Ticket operacional: ATD-20260330-EA1B5AA8. Novo complemento: isso pesa mais nas sextas. A equipe responsavel recebe essa atualizacao no mesmo fluxo do pedido.
- `llamaindex`: status 200, latency 267.0ms, keyword pass `True`, quality `100`, reason `a solicitacao pode ser executada por workflow estruturado com protocolo`
  answer: Complemento registrado na fila de direcao. Protocolo: REQ-20260330-4BB00C. Ticket operacional: ATD-20260330-7653B5BB. Novo complemento: isso pesa mais nas sextas. A equipe responsavel recebe essa atualizacao no mesmo fluxo do pedido.

### faz um resumo do meu pedido

- Slice: `workflow`
- Thread: `rand_workflow_request` turn `3`
- `langgraph`: status 200, latency 267.5ms, keyword pass `True`, quality `100`, reason `a solicitacao pode ser executada por workflow estruturado com protocolo`
  answer: Resumo da sua solicitacao institucional:. Assunto: quero protocolar um pedido pra direcao sobre reforco de seguranca na saida. Area responsavel: direcao. Detalhes registrados: quero protocolar um pedido pra direcao sobre reforco de seguranca na saida

Complemento registrado: isso pesa mais nas sextas. Protocolo: REQ-20260330-E70B0C. Ticket operacional: ATD-20260330-7E9C3A29. Status atual: em fila. Se quiser, eu tambem posso te dizer o prazo estimado ou quem responde por essa fila.
- `crewai`: status 200, latency 12543.1ms, keyword pass `False`, quality `80`, reason `crewai_public_flow_timeout`
  errors: missing_expected_keyword
  answer: A Escola Municipal de Educação Infantil (EMEI) Professor Florestan Fernandes foi inaugurada em 20 de maio de 2023. Ela está localizada na Rua Dr. João Batista de Lacerda, 580, no bairro do Limão, zona norte de São Paulo. A escola tem capacidade para atender 188 crianças de 0 a 5 anos e 11 meses, e funciona das 7h às 19h.
- `python_functions`: status 200, latency 244.1ms, keyword pass `True`, quality `100`, reason `a solicitacao pode ser executada por workflow estruturado com protocolo`
  answer: Resumo da sua solicitacao institucional:. Assunto: quero protocolar um pedido pra direcao sobre reforco de seguranca na saida. Area responsavel: direcao. Detalhes registrados: quero protocolar um pedido pra direcao sobre reforco de seguranca na saida

Complemento registrado: isso pesa mais nas sextas. Protocolo: REQ-20260330-444286. Ticket operacional: ATD-20260330-EA1B5AA8. Status atual: em fila. Se quiser, eu tambem posso te dizer o prazo estimado ou quem responde por essa fila.
- `llamaindex`: status 200, latency 351.7ms, keyword pass `True`, quality `100`, reason `a solicitacao pode ser executada por workflow estruturado com protocolo`
  answer: Resumo da sua solicitacao institucional:. Assunto: quero protocolar um pedido pra direcao sobre reforco de seguranca na saida. Area responsavel: direcao. Detalhes registrados: quero protocolar um pedido pra direcao sobre reforco de seguranca na saida

Complemento registrado: isso pesa mais nas sextas. Protocolo: REQ-20260330-4BB00C. Ticket operacional: ATD-20260330-7653B5BB. Status atual: em fila. Se quiser, eu tambem posso te dizer o prazo estimado ou quem responde por essa fila.

