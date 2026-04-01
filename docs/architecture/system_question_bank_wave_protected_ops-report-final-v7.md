# Five-Path Chatbot Comparison Report

Date: 2026-04-01T20:26:41.959167+00:00

Dataset: `/home/edann/projects/eduassist-platform/tests/evals/datasets/system_question_bank_wave_protected_ops.json`

Run prefix: `debug:five-path:20260401T202130Z`

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
| `langgraph` | `32/32` | `32/32` | `100.0` | `337.9 ms` |
| `crewai` | `32/32` | `32/32` | `100.0` | `3818.9 ms` |
| `python_functions` | `32/32` | `32/32` | `100.0` | `146.4 ms` |
| `llamaindex` | `32/32` | `32/32` | `100.0` | `935.6 ms` |
| `specialist_supervisor` | `32/32` | `32/32` | `100.0` | `4443.1 ms` |

## By Slice

- `protected`
  - `langgraph`: ok 30/30, keyword pass 30/30, quality 100.0, latency 351.8ms
  - `crewai`: ok 30/30, keyword pass 30/30, quality 100.0, latency 4061.8ms
  - `python_functions`: ok 30/30, keyword pass 30/30, quality 100.0, latency 147.3ms
  - `llamaindex`: ok 30/30, keyword pass 30/30, quality 100.0, latency 987.6ms
  - `specialist_supervisor`: ok 30/30, keyword pass 30/30, quality 100.0, latency 4213.3ms
- `workflow`
  - `langgraph`: ok 2/2, keyword pass 2/2, quality 100.0, latency 129.5ms
  - `crewai`: ok 2/2, keyword pass 2/2, quality 100.0, latency 175.7ms
  - `python_functions`: ok 2/2, keyword pass 2/2, quality 100.0, latency 133.0ms
  - `llamaindex`: ok 2/2, keyword pass 2/2, quality 100.0, latency 155.7ms
  - `specialist_supervisor`: ok 2/2, keyword pass 2/2, quality 100.0, latency 7890.4ms

## Error Types

- `langgraph`: nenhum
- `crewai`: nenhum
- `python_functions`: nenhum
- `llamaindex`: nenhum
- `specialist_supervisor`: nenhum

## Prompt Results

### Quero ver minhas notas.

- Slice: `protected`
- Thread: `system_bank:identidade_autenticacao_vinculo_e_policy:Q033` turn `1`
- `langgraph`: status 200, latency 264.9ms, keyword pass `True`, quality `100`, reason `dados estruturados devem passar por service deterministico`
  answer: Essa consulta depende de autenticacao e vinculo da sua conta no Telegram. Use o portal da escola para gerar o codigo de vinculacao e depois envie o comando `/start link_<codigo>` ao bot.
- `crewai`: status 200, latency 162.0ms, keyword pass `True`, quality `100`, reason `crewai_protected_auth_required`
  answer: Essa consulta depende de autenticacao e vinculo da sua conta no Telegram. Use o portal da escola para gerar o codigo de vinculacao e depois envie o comando /start link_<codigo> ao bot.
- `python_functions`: status 200, latency 144.9ms, keyword pass `True`, quality `100`, reason `python_functions_native_structured:academic`
  answer: Essa consulta depende de autenticacao e vinculo da sua conta no Telegram. Use o portal da escola para gerar o codigo de vinculacao e depois envie o comando `/start link_<codigo>` ao bot.
- `llamaindex`: status 200, latency 162.2ms, keyword pass `True`, quality `100`, reason `dados estruturados devem passar por service deterministico`
  answer: Essa consulta depende de autenticacao e vinculo da sua conta no Telegram. Use o portal da escola para gerar o codigo de vinculacao e depois envie o comando `/start link_<codigo>` ao bot.
- `specialist_supervisor`: status 200, latency 8455.5ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_direct:academic_specialist`
  answer: Não consegui encontrar suas informações. Por favor, poderia me dizer o seu nome completo ou o nome do aluno que você gostaria de consultar?

### Como eu vinculo meu Telegram a minha conta da escola?

- Slice: `protected`
- Thread: `system_bank:identidade_autenticacao_vinculo_e_policy:Q034` turn `1`
- `langgraph`: status 200, latency 146.3ms, keyword pass `True`, quality `100`, reason `dados estruturados devem passar por service deterministico`
  answer: Essa consulta depende de autenticacao e vinculo da sua conta no Telegram. Use o portal da escola para gerar o codigo de vinculacao e depois envie o comando `/start link_<codigo>` ao bot.
- `crewai`: status 200, latency 157.2ms, keyword pass `True`, quality `100`, reason `crewai_public_fast_path`
  answer: Para vincular o Telegram a sua conta da escola, entre no portal autenticado, gere o codigo de vinculacao e depois envie aqui o comando /start link_<codigo>.
- `python_functions`: status 200, latency 131.5ms, keyword pass `True`, quality `100`, reason `python_functions_native_structured:finance`
  answer: Essa consulta depende de autenticacao e vinculo da sua conta no Telegram. Use o portal da escola para gerar o codigo de vinculacao e depois envie o comando `/start link_<codigo>` ao bot.
- `llamaindex`: status 200, latency 148.3ms, keyword pass `True`, quality `100`, reason `dados estruturados devem passar por service deterministico`
  answer: Essa consulta depende de autenticacao e vinculo da sua conta no Telegram. Use o portal da escola para gerar o codigo de vinculacao e depois envie o comando `/start link_<codigo>` ao bot.
- `specialist_supervisor`: status 200, latency 1862.5ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_fast_path:auth_guidance`
  answer: Para consultas protegidas, como notas, faltas e financeiro, voce precisa vincular sua conta do Telegram ao portal do Colegio Horizonte. No portal autenticado, gere o codigo de vinculacao e depois envie aqui o comando `/start link_<codigo>`. Depois disso, eu passo a consultar seus dados autorizados por este canal.

### Estou logado como quem e quais alunos eu tenho vinculados?

- Slice: `protected`
- Thread: `system_bank:identidade_autenticacao_vinculo_e_policy:Q035` turn `1`
- `langgraph`: status 200, latency 106.6ms, keyword pass `True`, quality `100`, reason `identidade da conta autenticada exige leitura protegida e minimizada`
  answer: Voce esta falando aqui como Maria Oliveira, no perfil de responsavel. Sua conta esta vinculada a Lucas Oliveira e Ana Oliveira. Por aqui eu consigo consultar notas, faltas, proximas provas, matricula, financeiro, boletos, dentro das permissoes dessa vinculacao.
- `crewai`: status 200, latency 166.6ms, keyword pass `True`, quality `100`, reason `crewai_protected_identity_backstop`
  answer: Voce esta autenticado aqui como Maria Oliveira. Sua conta esta vinculada a Lucas Oliveira, Ana Oliveira e pode consultar notas, frequencia, avaliacoes, documentacao e financeiro desses alunos.
- `python_functions`: status 200, latency 95.3ms, keyword pass `True`, quality `100`, reason `python_functions_native_authenticated_account_scope`
  answer: Voce esta falando aqui como Maria Oliveira, no perfil de responsavel. Sua conta esta vinculada a Lucas Oliveira e Ana Oliveira. Por aqui eu consigo consultar notas, faltas, proximas provas, matricula, financeiro, boletos, dentro das permissoes dessa vinculacao.
- `llamaindex`: status 200, latency 135.1ms, keyword pass `True`, quality `100`, reason `identidade da conta autenticada exige leitura protegida e minimizada`
  answer: Voce esta falando aqui como Maria Oliveira, no perfil de responsavel. Sua conta esta vinculada a Lucas Oliveira e Ana Oliveira. Por aqui eu consigo consultar notas, faltas, proximas provas, matricula, financeiro, boletos, dentro das permissoes dessa vinculacao.
- `specialist_supervisor`: status 200, latency 9081.8ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_direct:institution_specialist`
  answer: Não consigo te informar como você está logado ou quais alunos estão vinculados à sua conta. Minhas funcionalidades são restritas a fornecer informações públicas sobre a instituição de ensino, suas políticas, calendário e serviços gerais. Não tenho acesso a dados de usuários logados ou a informações pessoais e específicas de matrícula.

### Qual e exatamente o meu escopo: posso ver academico, financeiro ou os dois para cada filho?

- Slice: `protected`
- Thread: `system_bank:identidade_autenticacao_vinculo_e_policy:Q036` turn `1`
- `langgraph`: status 200, latency 107.9ms, keyword pass `True`, quality `100`, reason `dados estruturados devem passar por service deterministico`
  answer: Voce ja esta autenticado por aqui e sua conta esta vinculada a Lucas Oliveira e Ana Oliveira. Por este canal eu consigo consultar notas, faltas, proximas provas, matricula, financeiro, boletos, dentro das permissoes dessa vinculacao.  Escopo atual:
- Lucas Oliveira: academico, financeiro
- Ana Oliveira: academico, financeiro Se quiser, me diga algo como "notas do Lucas", "faltas da Ana" ou "financeiro do Lucas".
- `crewai`: status 200, latency 169.4ms, keyword pass `True`, quality `100`, reason `crewai_protected_identity_backstop`
  answer: Voce esta autenticado aqui como Maria Oliveira. Sua conta esta vinculada a Lucas Oliveira, Ana Oliveira. Hoje eu consigo consultar exatamente: notas, frequencia, avaliacoes, documentacao e financeiro desses alunos.
Escopo atual:
- Lucas Oliveira: academico, financeiro
- Ana Oliveira: academico, financeiro
Se quiser, ja posso abrir um desses assuntos agora.
- `python_functions`: status 200, latency 90.6ms, keyword pass `True`, quality `100`, reason `python_functions_native_authenticated_account_scope`
  answer: Voce ja esta autenticado por aqui e sua conta esta vinculada a Lucas Oliveira e Ana Oliveira. Por este canal eu consigo consultar notas, faltas, proximas provas, matricula, financeiro, boletos, dentro das permissoes dessa vinculacao.  Escopo atual:
- Lucas Oliveira: academico, financeiro
- Ana Oliveira: academico, financeiro Se quiser, me diga algo como "notas do Lucas", "faltas da Ana" ou "financeiro do Lucas".
- `llamaindex`: status 200, latency 116.2ms, keyword pass `True`, quality `100`, reason `dados estruturados devem passar por service deterministico`
  answer: Voce ja esta autenticado por aqui e sua conta esta vinculada a Lucas Oliveira e Ana Oliveira. Por este canal eu consigo consultar notas, faltas, proximas provas, matricula, financeiro, boletos, dentro das permissoes dessa vinculacao.  Escopo atual:
- Lucas Oliveira: academico, financeiro
- Ana Oliveira: academico, financeiro Se quiser, me diga algo como "notas do Lucas", "faltas da Ana" ou "financeiro do Lucas".
- `specialist_supervisor`: status 200, latency 1834.4ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_fast_path:access_scope`
  answer: Voce ja esta autenticado por aqui e sua conta esta vinculada a Lucas Oliveira e Ana Oliveira. Neste canal eu consigo consultar academico e financeiro dos alunos vinculados dentro das permissoes da conta.  Escopo atual:
- Lucas Oliveira: academico, financeiro
- Ana Oliveira: academico, financeiroSe quiser, me diga algo como "notas do Lucas", "faltas da Ana" ou "financeiro da Ana".

### Quero ver minhas notas.

- Slice: `protected`
- Thread: `system_bank:identidade_autenticacao_vinculo_e_policy:Q037` turn `1`
- `langgraph`: status 200, latency 128.4ms, keyword pass `True`, quality `100`, reason `dados estruturados devem passar por service deterministico`
  answer: Sua conta tem mais de um aluno vinculado. Diga qual aluno deseja consultar: Lucas Oliveira (MAT-2026-001), Ana Oliveira (MAT-2026-002).
- `crewai`: status 200, latency 170.4ms, keyword pass `True`, quality `100`, reason `protected_shadow_needs_student_clarification`
  answer: Posso te ajudar com Lucas Oliveira, Ana Oliveira. Me diga qual aluno voce quer consultar.
- `python_functions`: status 200, latency 109.8ms, keyword pass `True`, quality `100`, reason `python_functions_native_structured:academic`
  answer: Sua conta tem mais de um aluno vinculado. Diga qual aluno deseja consultar: Lucas Oliveira (MAT-2026-001), Ana Oliveira (MAT-2026-002).
- `llamaindex`: status 200, latency 130.1ms, keyword pass `True`, quality `100`, reason `dados estruturados devem passar por service deterministico`
  answer: Sua conta tem mais de um aluno vinculado. Diga qual aluno deseja consultar: Lucas Oliveira (MAT-2026-001), Ana Oliveira (MAT-2026-002).
- `specialist_supervisor`: status 200, latency 1934.3ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_resolved_intent:academic_summary_aggregate`
  answer: Panorama academico das contas vinculadas:
- Lucas Oliveira: Historia 6,8; Fisica 5,9; Matematica 7,7; Portugues 8,3
- Ana Oliveira: Historia 7,3; Fisica 6,4; Matematica 7,4; Portugues 8,4

### Lucas, eu falei.

- Slice: `protected`
- Thread: `system_bank:identidade_autenticacao_vinculo_e_policy:Q037` turn `2`
- `langgraph`: status 200, latency 178.4ms, keyword pass `True`, quality `100`, reason `o usuario respondeu a desambiguacao do aluno e o fluxo protegido pode continuar`
  answer: Perfeito, seguimos com Lucas Oliveira. Posso te ajudar com notas, faltas, proximas provas, matricula, financeiro, boletos. Se quiser, ja me diga o que voce quer ver primeiro.
- `crewai`: status 200, latency 182.6ms, keyword pass `True`, quality `100`, reason `protected_shadow_student_selection`
  answer: Perfeito, seguimos com Lucas Oliveira. Posso te ajudar com notas, frequencia, faltas, proximas provas, documentacao, matricula e financeiro.
- `python_functions`: status 200, latency 164.5ms, keyword pass `True`, quality `100`, reason `a intencao esta ambigua e exige clarificacao antes de recuperar contexto`
  answer: Posso ajudar com informacoes publicas da escola, como calendario, matricula, documentos exigidos e regras de atendimento digital. Se quiser, pergunte por exemplo: "quais documentos preciso para a matricula?" ou "quando acontece a reuniao de pais?".
- `llamaindex`: status 200, latency 118.5ms, keyword pass `True`, quality `100`, reason `llamaindex_student_focus_fast_path`
  answer: Perfeito, seguimos com Lucas Oliveira. Posso te ajudar com notas, faltas, proximas provas, matricula, financeiro, boletos. Se quiser, ja me diga o que voce quer ver primeiro.
- `specialist_supervisor`: status 200, latency 1879.6ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_resolved_intent:student_grades`
  answer: Notas de Lucas Oliveira:
- Historia: media parcial 6,8
- Fisica: media parcial 5,9
- Matematica: media parcial 7,7
- Portugues: media parcial 8,3

### Meu ex-conjuge tambem e responsavel. O que exatamente eu nao posso ver aqui?

- Slice: `protected`
- Thread: `system_bank:identidade_autenticacao_vinculo_e_policy:Q039` turn `1`
- `langgraph`: status 200, latency 2291.3ms, keyword pass `True`, quality `100`, reason `a intencao esta ambigua e exige clarificacao antes de recuperar contexto`
  answer: Olá! Como assistente EduAssist, meu foco é em informações gerais e públicas da escola. Para acessar dados específicos de alunos, como notas, frequência ou informações financeiras, é necessário que o responsável esteja autenticado em nosso portal.

Se o seu ex-cônjuge também é responsável legal, ele terá acesso às mesmas informações que você, uma vez que ambos estejam autenticados.

Para informações sobre o que cada responsável pode ou não ver, especialmente em casos de responsabilidade compartilhada, sugiro que entre em contato diretamente com a Secretaria Escolar. Eles poderão esclarecer todos os detalhes sobre o acesso a informações do aluno.
- `crewai`: status 200, latency 20210.1ms, keyword pass `True`, quality `100`, reason `crewai_public_flow_timeout`
  answer: Não encontrei informações específicas sobre quais dados do aluno não são acessíveis a um responsável legal, especialmente em casos de ex-cônjuges também responsáveis, nos documentos que consultei. Para obter essa informação detalhada, sugiro que entre em contato diretamente com a secretaria ou o setor responsável da instituição.
- `python_functions`: status 200, latency 153.6ms, keyword pass `True`, quality `100`, reason `a intencao esta ambigua e exige clarificacao antes de recuperar contexto`
  answer: Posso ajudar com informacoes publicas da escola, como calendario, matricula, documentos exigidos e regras de atendimento digital. Se quiser, pergunte por exemplo: "quais documentos preciso para a matricula?" ou "quando acontece a reuniao de pais?".
- `llamaindex`: status 200, latency 18559.0ms, keyword pass `True`, quality `100`, reason `a intencao esta ambigua e exige clarificacao antes de recuperar contexto`
  answer: Posso ajudar com informacoes publicas da escola, como calendario, matricula, documentos exigidos e regras de atendimento digital. Se quiser, pergunte por exemplo: "quais documentos preciso para a matricula?" ou "quando acontece a reuniao de pais?".
- `specialist_supervisor`: status 200, latency 3994.6ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_fast_path:general_knowledge`
  answer: Prefiro não responder a perguntas que envolvam questões jurídicas ou de responsabilidade legal, pois fogem do meu domínio de conhecimento geral.

### Se eu souber o nome de um aluno da escola, consigo consultar notas ou boletos sem me autenticar?

- Slice: `protected`
- Thread: `system_bank:identidade_autenticacao_vinculo_e_policy:Q040` turn `1`
- `langgraph`: status 200, latency 133.3ms, keyword pass `True`, quality `100`, reason `o turno atual trouxe pistas explicitas de outro dominio protegido e o roteamento foi corrigido`
  answer: Essa consulta depende de autenticacao e vinculo da sua conta no Telegram. Use o portal da escola para gerar o codigo de vinculacao e depois envie o comando `/start link_<codigo>` ao bot.
- `crewai`: status 200, latency 163.9ms, keyword pass `True`, quality `100`, reason `crewai_protected_auth_required`
  answer: Essa consulta depende de autenticacao e vinculo da sua conta no Telegram. Use o portal da escola para gerar o codigo de vinculacao e depois envie o comando /start link_<codigo> ao bot.
- `python_functions`: status 200, latency 140.1ms, keyword pass `True`, quality `100`, reason `python_functions_native_structured:finance`
  answer: Essa consulta depende de autenticacao e vinculo da sua conta no Telegram. Use o portal da escola para gerar o codigo de vinculacao e depois envie o comando `/start link_<codigo>` ao bot.
- `llamaindex`: status 200, latency 152.1ms, keyword pass `True`, quality `100`, reason `dados estruturados devem passar por service deterministico`
  answer: Essa consulta depende de autenticacao e vinculo da sua conta no Telegram. Use o portal da escola para gerar o codigo de vinculacao e depois envie o comando `/start link_<codigo>` ao bot.
- `specialist_supervisor`: status 200, latency 6129.2ms, keyword pass `True`, quality `100`, reason `A solicitação implica acesso a dados sensíveis (notas e boletos) sem autenticação, o que viola diretamente as políticas de privacidade e segurança de dados do Colégio Horizonte. A estratégia é negar o acesso e informar a necessidade de autenticação.`
  answer: O acesso a dados sensíveis de alunos, como notas e boletos, é restrito e requer autenticação para garantir a privacidade e segurança das informações, conforme as políticas do Colégio Horizonte. Não é possível consultar essas informações apenas com o nome do aluno e sem autenticação.

### Quero ver as notas do Lucas Oliveira.

- Slice: `protected`
- Thread: `system_bank:academico_protegido:Q041` turn `1`
- `langgraph`: status 200, latency 176.7ms, keyword pass `True`, quality `100`, reason `dados estruturados devem passar por service deterministico`
  answer: Notas de Lucas Oliveira:
- Biologia - Avaliacao B1: 8.40/10.00
- Educacao Fisica - Avaliacao 2026-B1 - EF: 6.40/10.00
- Filosofia - Avaliacao 2026-B1 - FIL: 7.00/10.00
- Fisica - Avaliacao 2026-B1 - FIS: 5.80/10.00
- Geografia - Avaliacao 2026-B1 - GEO: 6.40/10.00
- Historia - Avaliacao 2026-B1 - HIS: 6.70/10.00
- Ingles - Avaliacao B1: 8.90/10.00
- Matematica - Avaliacao B1: 8.70/10.00
- `crewai`: status 200, latency 394.7ms, keyword pass `True`, quality `100`, reason `crewai_protected_fast_path`
  answer: As notas mais recentes de Lucas Oliveira incluem Biologia: 8.40/10.00; Educacao Fisica: 6.40/10.00; Filosofia: 7.00/10.00; Fisica: 5.80/10.00; Geografia: 6.40/10.00; Historia: 6.70/10.00; Ingles: 8.90/10.00; Matematica: 8.70/10.00.
- `python_functions`: status 200, latency 160.1ms, keyword pass `True`, quality `100`, reason `python_functions_native_structured:academic`
  answer: Notas de Lucas Oliveira:
- Biologia - Avaliacao B1: 8.40/10.00
- Educacao Fisica - Avaliacao 2026-B1 - EF: 6.40/10.00
- Filosofia - Avaliacao 2026-B1 - FIL: 7.00/10.00
- Fisica - Avaliacao 2026-B1 - FIS: 5.80/10.00
- Geografia - Avaliacao 2026-B1 - GEO: 6.40/10.00
- Historia - Avaliacao 2026-B1 - HIS: 6.70/10.00
- Ingles - Avaliacao B1: 8.90/10.00
- Matematica - Avaliacao B1: 8.70/10.00
- `llamaindex`: status 200, latency 192.0ms, keyword pass `True`, quality `100`, reason `dados estruturados devem passar por service deterministico`
  answer: Notas de Lucas Oliveira:
- Biologia - Avaliacao B1: 8.40/10.00
- Educacao Fisica - Avaliacao 2026-B1 - EF: 6.40/10.00
- Filosofia - Avaliacao 2026-B1 - FIL: 7.00/10.00
- Fisica - Avaliacao 2026-B1 - FIS: 5.80/10.00
- Geografia - Avaliacao 2026-B1 - GEO: 6.40/10.00
- Historia - Avaliacao 2026-B1 - HIS: 6.70/10.00
- Ingles - Avaliacao B1: 8.90/10.00
- Matematica - Avaliacao B1: 8.70/10.00
- `specialist_supervisor`: status 200, latency 1923.0ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_resolved_intent:student_grades`
  answer: Notas de Lucas Oliveira:
- Historia: media parcial 6,8
- Fisica: media parcial 5,9
- Matematica: media parcial 7,7
- Portugues: media parcial 8,3

### E a frequencia?

- Slice: `protected`
- Thread: `system_bank:academico_protegido:Q041` turn `2`
- `langgraph`: status 200, latency 178.6ms, keyword pass `True`, quality `100`, reason `dados estruturados devem passar por service deterministico`
  answer: Panorama de frequencia de Lucas Oliveira:
Resumo geral:
- Presencas registradas: 19
- Faltas registradas: 6
- Atrasos registrados: 7
- Minutos somados de ausencia: 370
- `crewai`: status 200, latency 406.2ms, keyword pass `True`, quality `100`, reason `crewai_protected_fast_path`
  answer: Na frequencia de Lucas Oliveira, eu encontrei 12 registros neste recorte: 7 presencas, 2 faltas e 3 atrasos.
- `python_functions`: status 200, latency 174.5ms, keyword pass `True`, quality `100`, reason `python_functions_native_structured:academic`
  answer: Panorama de frequencia de Lucas Oliveira:
Resumo geral:
- Presencas registradas: 19
- Faltas registradas: 6
- Atrasos registrados: 7
- Minutos somados de ausencia: 370
- `llamaindex`: status 200, latency 207.7ms, keyword pass `True`, quality `100`, reason `dados estruturados devem passar por service deterministico`
  answer: Panorama de frequencia de Lucas Oliveira:
Resumo geral:
- Presencas registradas: 19
- Faltas registradas: 6
- Atrasos registrados: 7
- Minutos somados de ausencia: 370
- `specialist_supervisor`: status 200, latency 1942.2ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_resolved_intent:attendance_summary`
  answer: Na frequencia de Lucas Oliveira em Tecnologia e Cultura Digital, eu encontrei 6 faltas, 7 atraso(s) e 19 presenca(s) neste recorte.

### Quais sao as proximas provas do Lucas Oliveira?

- Slice: `protected`
- Thread: `system_bank:academico_protegido:Q043` turn `1`
- `langgraph`: status 200, latency 211.7ms, keyword pass `True`, quality `100`, reason `dados estruturados devem passar por service deterministico`
  answer: Proximas avaliacoes de Lucas Oliveira:
- Turma: 1o Ano A
- Biologia - Avaliacao B1: 2026-04-10
- Fisica - Avaliacao 2026-B1 - FIS: 2026-04-10
- Historia - Avaliacao B1: 2026-04-10
- Ingles - Avaliacao B1: 2026-04-10
- Matematica - Avaliacao 2026-B1 - MAT: 2026-04-10
- Matematica - Avaliacao B1: 2026-04-10
- `crewai`: status 200, latency 409.3ms, keyword pass `True`, quality `100`, reason `crewai_protected_fast_path`
  answer: A proxima avaliacao registrada de Lucas Oliveira e Avaliacao B1 em 2026-04-10.
- `python_functions`: status 200, latency 215.9ms, keyword pass `True`, quality `100`, reason `python_functions_native_structured:academic`
  answer: Proximas avaliacoes de Lucas Oliveira:
- Turma: 1o Ano A
- Biologia - Avaliacao B1: 2026-04-10
- Fisica - Avaliacao 2026-B1 - FIS: 2026-04-10
- Historia - Avaliacao B1: 2026-04-10
- Ingles - Avaliacao B1: 2026-04-10
- Matematica - Avaliacao 2026-B1 - MAT: 2026-04-10
- Matematica - Avaliacao B1: 2026-04-10
- `llamaindex`: status 200, latency 228.7ms, keyword pass `True`, quality `100`, reason `dados estruturados devem passar por service deterministico`
  answer: Proximas avaliacoes de Lucas Oliveira:
- Turma: 1o Ano A
- Biologia - Avaliacao B1: 2026-04-10
- Fisica - Avaliacao 2026-B1 - FIS: 2026-04-10
- Historia - Avaliacao B1: 2026-04-10
- Ingles - Avaliacao B1: 2026-04-10
- Matematica - Avaliacao 2026-B1 - MAT: 2026-04-10
- Matematica - Avaliacao B1: 2026-04-10
- `specialist_supervisor`: status 200, latency 1931.4ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_tool_first:academic_summary`
  answer: Notas de Lucas Oliveira:
- Historia: media parcial 6,8
- Fisica: media parcial 5,9
- Matematica: media parcial 7,7
- Portugues: media parcial 8,3

### Em quais datas o Lucas faltou e em quais disciplinas isso aconteceu?

- Slice: `protected`
- Thread: `system_bank:academico_protegido:Q044` turn `1`
- `langgraph`: status 200, latency 173.0ms, keyword pass `True`, quality `100`, reason `dados estruturados devem passar por service deterministico`
  answer: Resumo academico de Lucas Oliveira:
- Turma: 1o Ano A
- Serie atual: 1
Notas mais recentes:
- Biologia - Avaliacao B1: 8.40/10.00
- Educacao Fisica - Avaliacao 2026-B1 - EF: 6.40/10.00
- Filosofia - Avaliacao 2026-B1 - FIL: 7.00/10.00
- Fisica - Avaliacao 2026-B1 - FIS: 5.80/10.00
- Geografia - Avaliacao 2026-B1 - GEO: 6.40/10.00
- Historia - Avaliacao 2026-B1 - HIS: 6.70/10.00
- Ingles - Avaliacao B1: 8.90/10.00
- Matematica - Avaliacao B1: 8.70/10.00
Frequencia:
- Biologia: 3 presencas, 0 atrasos, 1 faltas (50 min)
- Educacao Fisica: 1 presencas, 0 atrasos, 1 faltas (50 min)
- Filosofia: 1 presencas, 1 atrasos, 0 faltas (10 min)
- Fisica: 1 presencas, 1 atrasos, 0 faltas (10 min)
- `crewai`: status 200, latency 19446.2ms, keyword pass `True`, quality `100`, reason `crewai_protected_flow_completed`
  answer: As faltas de Lucas Oliveira (MAT-2026-001) são: 2 em Matemática Discreta, 1 em Programação I e 3 em Estruturas de Dados.
- `python_functions`: status 200, latency 187.7ms, keyword pass `True`, quality `100`, reason `python_functions_native_structured:academic`
  answer: Resumo academico de Lucas Oliveira:
- Turma: 1o Ano A
- Serie atual: 1
Notas mais recentes:
- Biologia - Avaliacao B1: 8.40/10.00
- Educacao Fisica - Avaliacao 2026-B1 - EF: 6.40/10.00
- Filosofia - Avaliacao 2026-B1 - FIL: 7.00/10.00
- Fisica - Avaliacao 2026-B1 - FIS: 5.80/10.00
- Geografia - Avaliacao 2026-B1 - GEO: 6.40/10.00
- Historia - Avaliacao 2026-B1 - HIS: 6.70/10.00
- Ingles - Avaliacao B1: 8.90/10.00
- Matematica - Avaliacao B1: 8.70/10.00
Frequencia:
- Biologia: 3 presencas, 0 atrasos, 1 faltas (50 min)
- Educacao Fisica: 1 presencas, 0 atrasos, 1 faltas (50 min)
- Filosofia: 1 presencas, 1 atrasos, 0 faltas (10 min)
- Fisica: 1 presencas, 1 atrasos, 0 faltas (10 min)
- `llamaindex`: status 200, latency 214.0ms, keyword pass `True`, quality `100`, reason `dados estruturados devem passar por service deterministico`
  answer: Resumo academico de Lucas Oliveira:
- Turma: 1o Ano A
- Serie atual: 1
Notas mais recentes:
- Biologia - Avaliacao B1: 8.40/10.00
- Educacao Fisica - Avaliacao 2026-B1 - EF: 6.40/10.00
- Filosofia - Avaliacao 2026-B1 - FIL: 7.00/10.00
- Fisica - Avaliacao 2026-B1 - FIS: 5.80/10.00
- Geografia - Avaliacao 2026-B1 - GEO: 6.40/10.00
- Historia - Avaliacao 2026-B1 - HIS: 6.70/10.00
- Ingles - Avaliacao B1: 8.90/10.00
- Matematica - Avaliacao B1: 8.70/10.00
Frequencia:
- Biologia: 3 presencas, 0 atrasos, 1 faltas (50 min)
- Educacao Fisica: 1 presencas, 0 atrasos, 1 faltas (50 min)
- Filosofia: 1 presencas, 1 atrasos, 0 faltas (10 min)
- Fisica: 1 presencas, 1 atrasos, 0 faltas (10 min)
- `specialist_supervisor`: status 200, latency 3799.6ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_tool_first:academic_summary`
  answer: Notas de Lucas Oliveira:
- Historia: media parcial 6,8
- Fisica: media parcial 5,9
- Matematica: media parcial 7,7
- Portugues: media parcial 8,3

### Compare o desempenho do Rafael e da Manuela neste bimestre e diga quem precisa de mais atencao.

- Slice: `protected`
- Thread: `system_bank:academico_protegido:Q045` turn `1`
- `langgraph`: status 200, latency 136.9ms, keyword pass `True`, quality `100`, reason `dados estruturados devem passar por service deterministico`
  answer: Estudar em uma escola publica pode ser uma boa escolha para muitas familias, e eu nao vou te vender uma comparacao vazia. No que esta publicado aqui, os diferenciais desta escola passam por Tutoria academica e projeto de vida, Espaco Maker integrado ao curriculo, Acolhimento estruturado para familias e estudantes. A proposta pedagogica publicada hoje combina Projeto pedagogico laico, com foco em aprendizagem por projetos, cultura digital responsavel, acompanhamento socioemocional e preparacao academica progressiva.. Na pratica, isso aparece em acompanhamento mais proximo da aprendizagem, projeto de vida e combinados pedagogicos mais claros. Escola laica com Ensino Fundamental II e Ensino Medio, acompanhamento tutorial e trilhas academicas no contraturno. Se quiser, eu posso te mostrar isso de forma mais pratica na rotina, na proposta pedagogica ou no contraturno.
- `crewai`: status 200, latency 20312.9ms, keyword pass `True`, quality `100`, reason `crewai_protected_flow_timeout`
  answer: Eu nao consegui consolidar essa consulta protegida com seguranca agora. Se quiser, me diga qual aluno e qual dado voce quer consultar.
- `python_functions`: status 200, latency 163.4ms, keyword pass `True`, quality `100`, reason `python_functions_native_structured:academic`
  answer: Estudar em uma escola publica pode ser uma boa escolha para muitas familias, e eu nao vou te vender uma comparacao vazia. No que esta publicado aqui, os diferenciais desta escola passam por Tutoria academica e projeto de vida, Espaco Maker integrado ao curriculo, Acolhimento estruturado para familias e estudantes. A proposta pedagogica publicada hoje combina Projeto pedagogico laico, com foco em aprendizagem por projetos, cultura digital responsavel, acompanhamento socioemocional e preparacao academica progressiva.. Na pratica, isso aparece em acompanhamento mais proximo da aprendizagem, projeto de vida e combinados pedagogicos mais claros. Escola laica com Ensino Fundamental II e Ensino Medio, acompanhamento tutorial e trilhas academicas no contraturno. Se quiser, eu posso te mostrar isso de forma mais pratica na rotina, na proposta pedagogica ou no contraturno.
- `llamaindex`: status 200, latency 204.5ms, keyword pass `True`, quality `100`, reason `dados estruturados devem passar por service deterministico`
  answer: Estudar em uma escola publica pode ser uma boa escolha para muitas familias, e eu nao vou te vender uma comparacao vazia. No que esta publicado aqui, os diferenciais desta escola passam por Tutoria academica e projeto de vida, Espaco Maker integrado ao curriculo, Acolhimento estruturado para familias e estudantes. A proposta pedagogica publicada hoje combina Projeto pedagogico laico, com foco em aprendizagem por projetos, cultura digital responsavel, acompanhamento socioemocional e preparacao academica progressiva.. Na pratica, isso aparece em acompanhamento mais proximo da aprendizagem, projeto de vida e combinados pedagogicos mais claros. Escola laica com Ensino Fundamental II e Ensino Medio, acompanhamento tutorial e trilhas academicas no contraturno. Se quiser, eu posso te mostrar isso de forma mais pratica na rotina, na proposta pedagogica ou no contraturno.
- `specialist_supervisor`: status 200, latency 3697.4ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_resolved_intent:academic_summary_aggregate`
  answer: Panorama academico das contas vinculadas:
- Lucas Oliveira: Historia 6,8; Fisica 5,9; Matematica 7,7; Portugues 8,3
- Ana Oliveira: Historia 7,3; Fisica 6,4; Matematica 7,4; Portugues 8,4

### O Joao ainda consegue recuperar a disciplina ou ja passou do ponto segundo as regras da escola?

- Slice: `protected`
- Thread: `system_bank:academico_protegido:Q046` turn `1`
- `langgraph`: status 200, latency 183.0ms, keyword pass `True`, quality `100`, reason `dados estruturados devem passar por service deterministico`
  answer: Sua conta tem mais de um aluno vinculado. Diga qual aluno deseja consultar: Lucas Oliveira (MAT-2026-001), Ana Oliveira (MAT-2026-002).
- `crewai`: status 200, latency 272.2ms, keyword pass `True`, quality `100`, reason `crewai_public_fast_path`
  answer: A proposta pedagogica publicada hoje combina A escola segue a BNCC e o curriculo do Ensino Medio articulado com projeto de vida, producao textual, cultura digital e aprofundamento academico progressivo. Na pratica, isso aparece em frentes como Tutoria academica e projeto de vida, Espaco Maker integrado ao curriculo, Acolhimento estruturado para familias e estudantes.
- `python_functions`: status 200, latency 172.4ms, keyword pass `True`, quality `100`, reason `python_functions_native_structured:academic`
  answer: Sua conta tem mais de um aluno vinculado. Diga qual aluno deseja consultar: Lucas Oliveira (MAT-2026-001), Ana Oliveira (MAT-2026-002).
- `llamaindex`: status 200, latency 184.1ms, keyword pass `True`, quality `100`, reason `dados estruturados devem passar por service deterministico`
  answer: Sua conta tem mais de um aluno vinculado. Diga qual aluno deseja consultar: Lucas Oliveira (MAT-2026-001), Ana Oliveira (MAT-2026-002).
- `specialist_supervisor`: status 200, latency 3557.9ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_tool_first:academic_summary_aggregate`
  answer: Panorama academico das contas vinculadas:
- Lucas Oliveira: Historia 6,8; Fisica 5,9; Matematica 7,7; Portugues 8,3
- Ana Oliveira: Historia 7,3; Fisica 6,4; Matematica 7,4; Portugues 8,4

### Qual e a minha melhor disciplina, qual e a pior e quanto falta para eu fechar a media em Fisica?

- Slice: `protected`
- Thread: `system_bank:academico_protegido:Q047` turn `1`
- `langgraph`: status 200, latency 164.3ms, keyword pass `True`, quality `100`, reason `dados estruturados devem passar por service deterministico`
  answer: Estudar em uma escola publica pode ser uma boa escolha para muitas familias, e eu nao vou te vender uma comparacao vazia. No que esta publicado aqui, os diferenciais desta escola passam por Tutoria academica e projeto de vida, Espaco Maker integrado ao curriculo, Acolhimento estruturado para familias e estudantes. A proposta pedagogica publicada hoje combina Projeto pedagogico laico, com foco em aprendizagem por projetos, cultura digital responsavel, acompanhamento socioemocional e preparacao academica progressiva.. Na pratica, isso aparece em acompanhamento mais proximo da aprendizagem, projeto de vida e combinados pedagogicos mais claros. Escola laica com Ensino Fundamental II e Ensino Medio, acompanhamento tutorial e trilhas academicas no contraturno. Se quiser, eu posso te mostrar isso de forma mais pratica na rotina, na proposta pedagogica ou no contraturno.
- `crewai`: status 200, latency 232.7ms, keyword pass `True`, quality `100`, reason `crewai_protected_auth_required`
  answer: Essa consulta depende de autenticacao e vinculo da sua conta no Telegram. Use o portal da escola para gerar o codigo de vinculacao e depois envie o comando /start link_<codigo> ao bot.
- `python_functions`: status 200, latency 190.3ms, keyword pass `True`, quality `100`, reason `python_functions_native_structured:academic`
  answer: Estudar em uma escola publica pode ser uma boa escolha para muitas familias, e eu nao vou te vender uma comparacao vazia. No que esta publicado aqui, os diferenciais desta escola passam por Tutoria academica e projeto de vida, Espaco Maker integrado ao curriculo, Acolhimento estruturado para familias e estudantes. A proposta pedagogica publicada hoje combina Projeto pedagogico laico, com foco em aprendizagem por projetos, cultura digital responsavel, acompanhamento socioemocional e preparacao academica progressiva.. Na pratica, isso aparece em acompanhamento mais proximo da aprendizagem, projeto de vida e combinados pedagogicos mais claros. Escola laica com Ensino Fundamental II e Ensino Medio, acompanhamento tutorial e trilhas academicas no contraturno. Se quiser, eu posso te mostrar isso de forma mais pratica na rotina, na proposta pedagogica ou no contraturno.
- `llamaindex`: status 200, latency 217.9ms, keyword pass `True`, quality `100`, reason `dados estruturados devem passar por service deterministico`
  answer: Sem problema, ajustei isso por aqui.

Estudar em uma escola publica pode ser uma boa escolha para muitas familias, e eu nao vou te vender uma comparacao vazia. No que esta publicado aqui, os diferenciais desta escola passam por Tutoria academica e projeto de vida, Espaco Maker integrado ao curriculo, Acolhimento estruturado para familias e estudantes. A proposta pedagogica publicada hoje combina Projeto pedagogico laico, com foco em aprendizagem por projetos, cultura digital responsavel, acompanhamento socioemocional e preparacao academica progressiva.. Na pratica, isso aparece em acompanhamento mais proximo da aprendizagem, projeto de vida e combinados pedagogicos mais claros. Escola laica com Ensino Fundamental II e Ensino Medio, acompanhamento tutorial e trilhas academicas no contraturno. Se quiser, eu posso te mostrar isso de forma mais pratica na rotina, na proposta pedagogica ou no contraturno.
- `specialist_supervisor`: status 200, latency 11248.0ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_direct:academic_specialist`
  answer: Não consegui identificar qual aluno você gostaria de consultar. Por favor, especifique o nome do aluno.

### Monte um resumo academico curto para eu mandar no grupo da familia sem expor nada desnecessario.

- Slice: `protected`
- Thread: `system_bank:academico_protegido:Q048` turn `1`
- `langgraph`: status 200, latency 2156.9ms, keyword pass `True`, quality `100`, reason `a intencao esta ambigua e exige clarificacao antes de recuperar contexto`
  answer: Olá! Que ótima ideia compartilhar um resumo acadêmico com a família. Para te ajudar a montar algo curto e sem expor nada desnecessário, preciso de um pouco mais de informação.

Você gostaria de um resumo sobre o quê exatamente? Por exemplo:

*   **Sobre o desempenho geral da escola?** (Nesse caso, posso destacar os diferenciais do Colégio Horizonte, como a tutoria acadêmica e o Espaço Maker).
*   **Sobre o seu próprio desempenho ou de um estudante específico?** (Para isso, seria necessário acessar informações que exigem autenticação, e o EduAssist não tem acesso direto a dados individuais de alunos. Você pode verificar o portal do aluno para essas informações).
*   **Sobre alguma novidade ou evento acadêmico da escola?** (Se houver algum evento no calendário oficial, posso te ajudar com isso).

Me diga qual o foco do resumo que você precisa, e eu te ajudo a formular algo!
- `crewai`: status 200, latency 20347.1ms, keyword pass `True`, quality `100`, reason `crewai_public_flow_timeout`
  answer: A Escola Bosque oferece um ambiente acolhedor e inovador, focado no desenvolvimento integral dos alunos, com destaque para a educação bilíngue e diversas atividades extracurriculares. Nossas turmas são pequenas, oferecemos um programa de mentoria individualizada e contamos com uma infraestrutura moderna, incluindo laboratórios de ciências e artes, além de quadras esportivas. O ano letivo de 2024 começa em 29 de janeiro e vai até 13 de dezembro, com férias de julho de 15 a 26 de julho.
- `python_functions`: status 200, latency 156.1ms, keyword pass `True`, quality `100`, reason `a intencao esta ambigua e exige clarificacao antes de recuperar contexto`
  answer: Posso ajudar com informacoes publicas da escola, como calendario, matricula, documentos exigidos e regras de atendimento digital. Se quiser, pergunte por exemplo: "quais documentos preciso para a matricula?" ou "quando acontece a reuniao de pais?".
- `llamaindex`: status 200, latency 6424.5ms, keyword pass `True`, quality `100`, reason `a intencao esta ambigua e exige clarificacao antes de recuperar contexto`
  answer: Posso ajudar com informacoes publicas da escola, como calendario, matricula, documentos exigidos e regras de atendimento digital. Se quiser, pergunte por exemplo: "quais documentos preciso para a matricula?" ou "quando acontece a reuniao de pais?".
- `specialist_supervisor`: status 200, latency 6738.2ms, keyword pass `True`, quality `100`, reason `A solicitação de um 'resumo acadêmico curto' com a restrição de 'não expor nada desnecessário' é ambígua. É preciso clarificar quais aspectos acadêmicos o usuário deseja incluir no resumo para garantir que a informação seja relevante e atenda aos requisitos de privacidade.`
  answer: Para montar um resumo acadêmico, você gostaria de incluir informações sobre o desempenho geral, notas em disciplinas específicas, participação em projetos, frequência ou outros aspectos?

### Quero ver o financeiro da Ana Oliveira.

- Slice: `protected`
- Thread: `system_bank:financeiro_protegido:Q049` turn `1`
- `langgraph`: status 200, latency 169.9ms, keyword pass `True`, quality `100`, reason `dados estruturados devem passar por service deterministico`
  answer: Resumo financeiro de Ana Oliveira:
- Contrato: CTR-2026-002
- Responsavel financeiro: Maria Oliveira
- Mensalidade base: 1450.00
- Faturas em aberto: 2
- Faturas vencidas: 0
Ultimas faturas:
- 2026-01: vencimento 2026-01-10, status paga, valor 1450.00
- 2026-02: vencimento 2026-02-10, status paga, valor 1450.00
- 2026-03: vencimento 2026-03-10, status em aberto, valor 1450.00
- 2026-04: vencimento 2026-04-10, status em aberto, valor 1450.00
- `crewai`: status 200, latency 381.3ms, keyword pass `True`, quality `100`, reason `crewai_protected_fast_path`
  answer: Resumo financeiro de Ana Oliveira: a mensalidade de referencia e 1450.00 e ha 2 fatura(s) em aberto, sendo 0 vencida(s).
- `python_functions`: status 200, latency 169.0ms, keyword pass `True`, quality `100`, reason `python_functions_native_structured:finance`
  answer: Resumo financeiro de Ana Oliveira:
- Contrato: CTR-2026-002
- Responsavel financeiro: Maria Oliveira
- Mensalidade base: 1450.00
- Faturas em aberto: 2
- Faturas vencidas: 0
Ultimas faturas:
- 2026-01: vencimento 2026-01-10, status paga, valor 1450.00
- 2026-02: vencimento 2026-02-10, status paga, valor 1450.00
- 2026-03: vencimento 2026-03-10, status em aberto, valor 1450.00
- 2026-04: vencimento 2026-04-10, status em aberto, valor 1450.00
- `llamaindex`: status 200, latency 183.7ms, keyword pass `True`, quality `100`, reason `dados estruturados devem passar por service deterministico`
  answer: Resumo financeiro de Ana Oliveira:
- Contrato: CTR-2026-002
- Responsavel financeiro: Maria Oliveira
- Mensalidade base: 1450.00
- Faturas em aberto: 2
- Faturas vencidas: 0
Ultimas faturas:
- 2026-01: vencimento 2026-01-10, status paga, valor 1450.00
- 2026-02: vencimento 2026-02-10, status paga, valor 1450.00
- 2026-03: vencimento 2026-03-10, status em aberto, valor 1450.00
- 2026-04: vencimento 2026-04-10, status em aberto, valor 1450.00
- `specialist_supervisor`: status 200, latency 1999.0ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_resolved_intent:finance_student_summary`
  answer: Resumo financeiro das contas vinculadas:
- Total de faturas em aberto: 2
- Total de faturas vencidas: 0
- Ana Oliveira: 2 em aberto, 0 vencidas
  2026-01: vencimento 2026-01-10, status paid, valor 1450.00
  2026-02: vencimento 2026-02-10, status paid, valor 1450.00

### Tenho boletos atrasados?

- Slice: `protected`
- Thread: `system_bank:financeiro_protegido:Q050` turn `1`
- `langgraph`: status 200, latency 211.9ms, keyword pass `True`, quality `100`, reason `dados estruturados devem passar por service deterministico`
  answer: Resumo financeiro das contas vinculadas:
- Total de faturas em aberto: 3
- Total de faturas vencidas: 0
- Lucas Oliveira: 1 em aberto, 0 vencidas
- Ana Oliveira: 2 em aberto, 0 vencidas
- Hoje nao ha faturas vencidas neste recorte.
- `crewai`: status 200, latency 20234.4ms, keyword pass `True`, quality `100`, reason `crewai_public_flow_timeout`
  answer: Para verificar seus boletos atrasados, por favor, entre em contato com o setor financeiro através do bot, portal autenticado ou email institucional.
- `python_functions`: status 200, latency 206.0ms, keyword pass `True`, quality `100`, reason `python_functions_native_structured:finance`
  answer: Resumo financeiro das contas vinculadas:
- Total de faturas em aberto: 3
- Total de faturas vencidas: 0
- Lucas Oliveira: 1 em aberto, 0 vencidas
- Ana Oliveira: 2 em aberto, 0 vencidas
- Hoje nao ha faturas vencidas neste recorte.
- `llamaindex`: status 200, latency 225.5ms, keyword pass `True`, quality `100`, reason `dados estruturados devem passar por service deterministico`
  answer: Resumo financeiro das contas vinculadas:
- Total de faturas em aberto: 3
- Total de faturas vencidas: 0
- Lucas Oliveira: 1 em aberto, 0 vencidas
- Ana Oliveira: 2 em aberto, 0 vencidas
- Hoje nao ha faturas vencidas neste recorte.
- `specialist_supervisor`: status 200, latency 2006.8ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_resolved_intent:finance_student_clarify`
  answer: Consigo verificar a situacao financeira, mas preciso que voce me diga qual aluno: Lucas Oliveira ou Ana Oliveira?

### Qual e o proximo pagamento pendente e qual e a data de vencimento?

- Slice: `protected`
- Thread: `system_bank:financeiro_protegido:Q051` turn `1`
- `langgraph`: status 200, latency 118.8ms, keyword pass `True`, quality `100`, reason `dados estruturados devem passar por service deterministico`
  answer: Hoje eu nao encontrei Pendente entre os alunos vinculados a esta conta. No momento, os alunos que aparecem aqui sao: Lucas Oliveira (MAT-2026-001), Ana Oliveira (MAT-2026-002). Se quiser, me diga qual deles voce quer consultar.
- `crewai`: status 200, latency 159.0ms, keyword pass `True`, quality `100`, reason `protected_shadow_needs_student_clarification`
  answer: Posso te ajudar com Lucas Oliveira, Ana Oliveira. Me diga qual aluno voce quer consultar.
- `python_functions`: status 200, latency 108.1ms, keyword pass `True`, quality `100`, reason `python_functions_native_structured:finance`
  answer: Hoje eu nao encontrei Pendente entre os alunos vinculados a esta conta. No momento, os alunos que aparecem aqui sao: Lucas Oliveira (MAT-2026-001), Ana Oliveira (MAT-2026-002). Se quiser, me diga qual deles voce quer consultar.
- `llamaindex`: status 200, latency 131.4ms, keyword pass `True`, quality `100`, reason `dados estruturados devem passar por service deterministico`
  answer: Hoje eu nao encontrei Pendente entre os alunos vinculados a esta conta. No momento, os alunos que aparecem aqui sao: Lucas Oliveira (MAT-2026-001), Ana Oliveira (MAT-2026-002). Se quiser, me diga qual deles voce quer consultar.
- `specialist_supervisor`: status 200, latency 1982.9ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_resolved_intent:finance_student_clarify`
  answer: Consigo verificar a situacao financeira, mas preciso que voce me diga qual aluno: Lucas Oliveira ou Ana Oliveira?

### Qual e o codigo do contrato e o identificador da fatura que esta em aberto?

- Slice: `protected`
- Thread: `system_bank:financeiro_protegido:Q052` turn `1`
- `langgraph`: status 200, latency 119.2ms, keyword pass `True`, quality `100`, reason `dados estruturados devem passar por service deterministico`
  answer: Hoje eu nao encontrei Fatura Que Esta entre os alunos vinculados a esta conta. No momento, os alunos que aparecem aqui sao: Lucas Oliveira (MAT-2026-001), Ana Oliveira (MAT-2026-002). Se quiser, me diga qual deles voce quer consultar.
- `crewai`: status 200, latency 181.6ms, keyword pass `True`, quality `100`, reason `protected_shadow_unmatched_student_reference`
  answer: Hoje eu nao encontrei Codigo entre os alunos vinculados a esta conta. No momento, os alunos que aparecem aqui sao: Lucas Oliveira, Ana Oliveira. Se quiser, me diga qual deles voce quer consultar.
- `python_functions`: status 200, latency 107.8ms, keyword pass `True`, quality `100`, reason `python_functions_native_structured:finance`
  answer: Hoje eu nao encontrei Fatura Que Esta entre os alunos vinculados a esta conta. No momento, os alunos que aparecem aqui sao: Lucas Oliveira (MAT-2026-001), Ana Oliveira (MAT-2026-002). Se quiser, me diga qual deles voce quer consultar.
- `llamaindex`: status 200, latency 133.1ms, keyword pass `True`, quality `100`, reason `dados estruturados devem passar por service deterministico`
  answer: Hoje eu nao encontrei Fatura Que Esta entre os alunos vinculados a esta conta. No momento, os alunos que aparecem aqui sao: Lucas Oliveira (MAT-2026-001), Ana Oliveira (MAT-2026-002). Se quiser, me diga qual deles voce quer consultar.
- `specialist_supervisor`: status 200, latency 2004.4ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_resolved_intent:finance_student_clarify`
  answer: Consigo verificar a situacao financeira, mas preciso que voce me diga qual aluno: Lucas Oliveira ou Ana Oliveira?

### Compare a situacao financeira do Rafael, da Manuela e do Joao e destaque onde ha atraso ou pagamento parcial.

- Slice: `protected`
- Thread: `system_bank:financeiro_protegido:Q053` turn `1`
- `langgraph`: status 200, latency 114.8ms, keyword pass `True`, quality `100`, reason `dados estruturados devem passar por service deterministico`
  answer: Estudar em uma escola publica pode ser uma boa escolha para muitas familias, e eu nao vou te vender uma comparacao vazia. No que esta publicado aqui, os diferenciais desta escola passam por Tutoria academica e projeto de vida, Espaco Maker integrado ao curriculo, Acolhimento estruturado para familias e estudantes. A proposta pedagogica publicada hoje combina Projeto pedagogico laico, com foco em aprendizagem por projetos, cultura digital responsavel, acompanhamento socioemocional e preparacao academica progressiva.. Na pratica, isso aparece em acompanhamento mais proximo da aprendizagem, projeto de vida e combinados pedagogicos mais claros. Escola laica com Ensino Fundamental II e Ensino Medio, acompanhamento tutorial e trilhas academicas no contraturno. Se quiser, eu posso te mostrar isso de forma mais pratica na rotina, na proposta pedagogica ou no contraturno.
- `crewai`: status 200, latency 191.5ms, keyword pass `True`, quality `100`, reason `protected_shadow_unmatched_student_reference`
  answer: Hoje eu nao encontrei Joao entre os alunos vinculados a esta conta. No momento, os alunos que aparecem aqui sao: Lucas Oliveira, Ana Oliveira. Se quiser, me diga qual deles voce quer consultar.
- `python_functions`: status 200, latency 113.7ms, keyword pass `True`, quality `100`, reason `python_functions_native_structured:finance`
  answer: Estudar em uma escola publica pode ser uma boa escolha para muitas familias, e eu nao vou te vender uma comparacao vazia. No que esta publicado aqui, os diferenciais desta escola passam por Tutoria academica e projeto de vida, Espaco Maker integrado ao curriculo, Acolhimento estruturado para familias e estudantes. A proposta pedagogica publicada hoje combina Projeto pedagogico laico, com foco em aprendizagem por projetos, cultura digital responsavel, acompanhamento socioemocional e preparacao academica progressiva.. Na pratica, isso aparece em acompanhamento mais proximo da aprendizagem, projeto de vida e combinados pedagogicos mais claros. Escola laica com Ensino Fundamental II e Ensino Medio, acompanhamento tutorial e trilhas academicas no contraturno. Se quiser, eu posso te mostrar isso de forma mais pratica na rotina, na proposta pedagogica ou no contraturno.
- `llamaindex`: status 200, latency 136.7ms, keyword pass `True`, quality `100`, reason `dados estruturados devem passar por service deterministico`
  answer: Estudar em uma escola publica pode ser uma boa escolha para muitas familias, e eu nao vou te vender uma comparacao vazia. No que esta publicado aqui, os diferenciais desta escola passam por Tutoria academica e projeto de vida, Espaco Maker integrado ao curriculo, Acolhimento estruturado para familias e estudantes. A proposta pedagogica publicada hoje combina Projeto pedagogico laico, com foco em aprendizagem por projetos, cultura digital responsavel, acompanhamento socioemocional e preparacao academica progressiva.. Na pratica, isso aparece em acompanhamento mais proximo da aprendizagem, projeto de vida e combinados pedagogicos mais claros. Escola laica com Ensino Fundamental II e Ensino Medio, acompanhamento tutorial e trilhas academicas no contraturno. Se quiser, eu posso te mostrar isso de forma mais pratica na rotina, na proposta pedagogica ou no contraturno.
- `specialist_supervisor`: status 200, latency 2003.7ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_resolved_intent:finance_student_clarify`
  answer: Consigo verificar a situacao financeira, mas preciso que voce me diga qual aluno: Lucas Oliveira ou Ana Oliveira?

### Sou a Helena e quero ver o financeiro do Rafael.

- Slice: `protected`
- Thread: `system_bank:financeiro_protegido:Q054` turn `1`
- `langgraph`: status 200, latency 116.3ms, keyword pass `True`, quality `100`, reason `dados estruturados devem passar por service deterministico`
  answer: Hoje eu nao encontrei Rafael entre os alunos vinculados a esta conta. No momento, os alunos que aparecem aqui sao: Lucas Oliveira (MAT-2026-001), Ana Oliveira (MAT-2026-002). Se quiser, me diga qual deles voce quer consultar.
- `crewai`: status 200, latency 178.7ms, keyword pass `True`, quality `100`, reason `protected_shadow_needs_student_clarification`
  answer: Posso te ajudar com Lucas Oliveira, Ana Oliveira. Me diga qual aluno voce quer consultar.
- `python_functions`: status 200, latency 106.6ms, keyword pass `True`, quality `100`, reason `python_functions_native_structured:finance`
  answer: Hoje eu nao encontrei Rafael entre os alunos vinculados a esta conta. No momento, os alunos que aparecem aqui sao: Lucas Oliveira (MAT-2026-001), Ana Oliveira (MAT-2026-002). Se quiser, me diga qual deles voce quer consultar.
- `llamaindex`: status 200, latency 136.0ms, keyword pass `True`, quality `100`, reason `dados estruturados devem passar por service deterministico`
  answer: Hoje eu nao encontrei Rafael entre os alunos vinculados a esta conta. No momento, os alunos que aparecem aqui sao: Lucas Oliveira (MAT-2026-001), Ana Oliveira (MAT-2026-002). Se quiser, me diga qual deles voce quer consultar.
- `specialist_supervisor`: status 200, latency 1984.3ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_resolved_intent:finance_student_clarify`
  answer: Consigo verificar a situacao financeira, mas preciso que voce me diga qual aluno: Lucas Oliveira ou Ana Oliveira?

### Paguei parte da mensalidade do Joao e preciso negociar o restante; o que ja aparece e qual o proximo passo?

- Slice: `workflow`
- Thread: `system_bank:financeiro_protegido:Q055` turn `1`
- `langgraph`: status 200, latency 129.3ms, keyword pass `True`, quality `100`, reason `consulta publica de navegacao e canais foi resgatada do dominio support`
  answer: Ainda nao encontrei um protocolo recente nesta conversa para consultar o status da fila. Se quiser, me diga o codigo que comeca com VIS, REQ ou ATD, ou me lembre se o assunto era visita, direcao, financeiro ou secretaria.
- `crewai`: status 200, latency 175.3ms, keyword pass `True`, quality `100`, reason `protected_shadow_needs_student_clarification`
  answer: Posso te ajudar com Lucas Oliveira, Ana Oliveira. Me diga qual aluno voce quer consultar.
- `python_functions`: status 200, latency 129.9ms, keyword pass `True`, quality `100`, reason `python_functions_native_structured:support`
  answer: Ainda nao encontrei um protocolo recente nesta conversa para consultar o status da fila. Se quiser, me diga o codigo que comeca com VIS, REQ ou ATD, ou me lembre se o assunto era visita, direcao, financeiro ou secretaria.
- `llamaindex`: status 200, latency 156.0ms, keyword pass `True`, quality `100`, reason `consulta publica de navegacao e canais foi resgatada do dominio support`
  answer: Ainda nao encontrei um protocolo recente nesta conversa para consultar o status da fila. Se quiser, me diga o codigo que comeca com VIS, REQ ou ATD, ou me lembre se o assunto era visita, direcao, financeiro ou secretaria.
- `specialist_supervisor`: status 200, latency 2011.2ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_resolved_intent:finance_student_clarify`
  answer: Consigo verificar a situacao financeira, mas preciso que voce me diga qual aluno: Lucas Oliveira ou Ana Oliveira?

### Explique a minha situacao financeira como se eu fosse leigo, separando mensalidade, taxa, atraso e desconto.

- Slice: `protected`
- Thread: `system_bank:financeiro_protegido:Q056` turn `1`
- `langgraph`: status 200, latency 117.0ms, keyword pass `True`, quality `100`, reason `dados estruturados devem passar por service deterministico`
  answer: Hoje eu nao encontrei Mensalidade entre os alunos vinculados a esta conta. No momento, os alunos que aparecem aqui sao: Lucas Oliveira (MAT-2026-001), Ana Oliveira (MAT-2026-002). Se quiser, me diga qual deles voce quer consultar.
- `crewai`: status 200, latency 174.6ms, keyword pass `True`, quality `100`, reason `protected_shadow_needs_student_clarification`
  answer: Posso te ajudar com Lucas Oliveira, Ana Oliveira. Me diga qual aluno voce quer consultar.
- `python_functions`: status 200, latency 110.6ms, keyword pass `True`, quality `100`, reason `python_functions_native_structured:finance`
  answer: Hoje eu nao encontrei Mensalidade entre os alunos vinculados a esta conta. No momento, os alunos que aparecem aqui sao: Lucas Oliveira (MAT-2026-001), Ana Oliveira (MAT-2026-002). Se quiser, me diga qual deles voce quer consultar.
- `llamaindex`: status 200, latency 133.7ms, keyword pass `True`, quality `100`, reason `dados estruturados devem passar por service deterministico`
  answer: Hoje eu nao encontrei Mensalidade entre os alunos vinculados a esta conta. No momento, os alunos que aparecem aqui sao: Lucas Oliveira (MAT-2026-001), Ana Oliveira (MAT-2026-002). Se quiser, me diga qual deles voce quer consultar.
- `specialist_supervisor`: status 200, latency 1977.0ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_resolved_intent:finance_student_clarify`
  answer: Consigo verificar a situacao financeira, mas preciso que voce me diga qual aluno: Lucas Oliveira ou Ana Oliveira?

### Minha documentacao e cadastro estao atualizados?

- Slice: `protected`
- Thread: `system_bank:administrativo_e_documental_protegido:Q057` turn `1`
- `langgraph`: status 200, latency 162.0ms, keyword pass `True`, quality `100`, reason `status administrativo autenticado exige service deterministico`
  answer: Situacao administrativa do seu cadastro hoje: com pendencias.
Situacao documental do seu cadastro hoje:
- Email cadastral: regular. maria.oliveira@mock.eduassist.local
- Telefone cadastral: regular. +55 11 98888-1001
- Documentacao administrativa: com pendencias. Ainda falta reenviar um comprovante de residencia atualizado para concluir a conferência documental.
Proximo passo: Envie o comprovante atualizado pela secretaria ou pelo canal de documentos para concluir a conferência.
- `crewai`: status 200, latency 172.9ms, keyword pass `True`, quality `100`, reason `crewai_protected_identity_backstop`
  answer: Para atualizar seu cadastro, o caminho mais seguro e revisar os dados no portal e, se precisar de alteracao assistida, falar com a secretaria. Se quiser, eu posso te orientar sobre qual dado voce precisa ajustar primeiro.
- `python_functions`: status 200, latency 143.0ms, keyword pass `True`, quality `100`, reason `python_functions_native_structured:institution`
  answer: Situacao administrativa do seu cadastro hoje: com pendencias.
Situacao documental do seu cadastro hoje:
- Email cadastral: regular. maria.oliveira@mock.eduassist.local
- Telefone cadastral: regular. +55 11 98888-1001
- Documentacao administrativa: com pendencias. Ainda falta reenviar um comprovante de residencia atualizado para concluir a conferência documental.
Proximo passo: Envie o comprovante atualizado pela secretaria ou pelo canal de documentos para concluir a conferência.
- `llamaindex`: status 200, latency 163.9ms, keyword pass `True`, quality `100`, reason `status administrativo autenticado exige service deterministico`
  answer: Situacao administrativa do seu cadastro hoje: com pendencias.
Situacao documental do seu cadastro hoje:
- Email cadastral: regular. maria.oliveira@mock.eduassist.local
- Telefone cadastral: regular. +55 11 98888-1001
- Documentacao administrativa: com pendencias. Ainda falta reenviar um comprovante de residencia atualizado para concluir a conferência documental.
Proximo passo: Envie o comprovante atualizado pela secretaria ou pelo canal de documentos para concluir a conferência.
- `specialist_supervisor`: status 200, latency 14080.5ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_direct:institution_specialist`
  answer: Como EduAssist, assistente institucional da escola, não tenho acesso direto a informações pessoais para verificar o status da sua documentação e cadastro. Para obter essa informação, por favor, entre em contato diretamente com a Secretaria da escola, que é o canal adequado para consultas sobre documentos e assuntos administrativos. 

Você pode contatá-los pelos seguintes canais:
*   **Telefone da Secretaria:** (11) 3333-4200
*   **WhatsApp da Secretaria Digital:** (11) 97500-2041
*   **E-mail da Secretaria:** secretaria@colegiohorizonte.edu.br

Além disso, o envio inicial de documentos pode ser feito pelo portal institucional ou pelo e-mail da secretaria. Lembre-se que o chat aberto não deve ser utilizado para o envio de documentos completos ou dados sensíveis; sempre use o portal autenticado ou o e-mail institucional para essas finalidades, quando possível.

### Qual e a situacao documental do Lucas?

- Slice: `protected`
- Thread: `system_bank:administrativo_e_documental_protegido:Q058` turn `1`
- `langgraph`: status 200, latency 1986.3ms, keyword pass `True`, quality `100`, reason `a intencao esta ambigua e exige clarificacao antes de recuperar contexto`
  answer: Para verificar a situação documental de um estudante específico, como o Lucas, é necessário acessar informações que são confidenciais. Por isso, preciso que você se autentique no nosso portal. Lá, você terá acesso a todos os detalhes sobre a documentação do aluno.

Se precisar de ajuda para acessar o portal ou tiver alguma dúvida sobre o processo, posso te orientar.
- `crewai`: status 200, latency 15888.3ms, keyword pass `True`, quality `100`, reason `crewai_protected_flow_completed`
  answer: Lucas Oliveira (MAT-2026-001) está atualmente matriculado e ativo.
- `python_functions`: status 200, latency 159.4ms, keyword pass `True`, quality `100`, reason `a intencao esta ambigua e exige clarificacao antes de recuperar contexto`
  answer: Posso ajudar com informacoes publicas da escola, como calendario, matricula, documentos exigidos e regras de atendimento digital. Se quiser, pergunte por exemplo: "quais documentos preciso para a matricula?" ou "quando acontece a reuniao de pais?".
- `llamaindex`: status 200, latency 177.2ms, keyword pass `True`, quality `100`, reason `llamaindex_protected_records_fast_path`
  answer: Situacao documental de Lucas Oliveira hoje: regular.
- `specialist_supervisor`: status 200, latency 5904.4ms, keyword pass `True`, quality `100`, reason `A pergunta sobre a 'situação documental' de Lucas é ambígua e pode se referir a diferentes tipos de documentos (acadêmicos, financeiros, de matrícula, etc.). É necessária uma clarificação para direcionar a busca corretamente.`
  answer: Você poderia especificar a qual tipo de situação documental do Lucas você se refere? Por exemplo, documentos acadêmicos, financeiros, de matrícula ou outros?

### Compare a documentacao dos meus filhos e diga qual deles ainda tem pendencia.

- Slice: `protected`
- Thread: `system_bank:administrativo_e_documental_protegido:Q059` turn `1`
- `langgraph`: status 200, latency 109.1ms, keyword pass `True`, quality `100`, reason `dados estruturados devem passar por service deterministico`
  answer: Estudar em uma escola publica pode ser uma boa escolha para muitas familias, e eu nao vou te vender uma comparacao vazia. No que esta publicado aqui, os diferenciais desta escola passam por Tutoria academica e projeto de vida, Espaco Maker integrado ao curriculo, Acolhimento estruturado para familias e estudantes. A proposta pedagogica publicada hoje combina Projeto pedagogico laico, com foco em aprendizagem por projetos, cultura digital responsavel, acompanhamento socioemocional e preparacao academica progressiva.. Na pratica, isso aparece em acompanhamento mais proximo da aprendizagem, projeto de vida e combinados pedagogicos mais claros. Escola laica com Ensino Fundamental II e Ensino Medio, acompanhamento tutorial e trilhas academicas no contraturno. Se quiser, eu posso te mostrar isso de forma mais pratica na rotina, na proposta pedagogica ou no contraturno.
- `crewai`: status 200, latency 180.4ms, keyword pass `True`, quality `100`, reason `protected_shadow_unmatched_student_reference`
  answer: Hoje eu nao encontrei Compare entre os alunos vinculados a esta conta. No momento, os alunos que aparecem aqui sao: Lucas Oliveira, Ana Oliveira. Se quiser, me diga qual deles voce quer consultar.
- `python_functions`: status 200, latency 99.6ms, keyword pass `True`, quality `100`, reason `python_functions_native_structured:finance`
  answer: Estudar em uma escola publica pode ser uma boa escolha para muitas familias, e eu nao vou te vender uma comparacao vazia. No que esta publicado aqui, os diferenciais desta escola passam por Tutoria academica e projeto de vida, Espaco Maker integrado ao curriculo, Acolhimento estruturado para familias e estudantes. A proposta pedagogica publicada hoje combina Projeto pedagogico laico, com foco em aprendizagem por projetos, cultura digital responsavel, acompanhamento socioemocional e preparacao academica progressiva.. Na pratica, isso aparece em acompanhamento mais proximo da aprendizagem, projeto de vida e combinados pedagogicos mais claros. Escola laica com Ensino Fundamental II e Ensino Medio, acompanhamento tutorial e trilhas academicas no contraturno. Se quiser, eu posso te mostrar isso de forma mais pratica na rotina, na proposta pedagogica ou no contraturno.
- `llamaindex`: status 200, latency 126.5ms, keyword pass `True`, quality `100`, reason `dados estruturados devem passar por service deterministico`
  answer: Estudar em uma escola publica pode ser uma boa escolha para muitas familias, e eu nao vou te vender uma comparacao vazia. No que esta publicado aqui, os diferenciais desta escola passam por Tutoria academica e projeto de vida, Espaco Maker integrado ao curriculo, Acolhimento estruturado para familias e estudantes. A proposta pedagogica publicada hoje combina Projeto pedagogico laico, com foco em aprendizagem por projetos, cultura digital responsavel, acompanhamento socioemocional e preparacao academica progressiva.. Na pratica, isso aparece em acompanhamento mais proximo da aprendizagem, projeto de vida e combinados pedagogicos mais claros. Escola laica com Ensino Fundamental II e Ensino Medio, acompanhamento tutorial e trilhas academicas no contraturno. Se quiser, eu posso te mostrar isso de forma mais pratica na rotina, na proposta pedagogica ou no contraturno.
- `specialist_supervisor`: status 200, latency 1992.3ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_tool_first:financial_summary_aggregate`
  answer: Resumo financeiro das contas vinculadas:
- Total de faturas em aberto: 3
- Total de faturas vencidas: 0
- Lucas Oliveira: 1 em aberto, 0 vencidas
  2026-01: vencimento 2026-01-10, status paid, valor 1450.00
  2026-02: vencimento 2026-02-10, status paid, valor 1450.00
- Ana Oliveira: 2 em aberto, 0 vencidas
  2026-01: vencimento 2026-01-10, status paid, valor 1450.00
  2026-02: vencimento 2026-02-10, status paid, valor 1450.00

### Quero saber se minha documentacao esta regular e se ha algo financeiro bloqueando atendimento.

- Slice: `protected`
- Thread: `system_bank:administrativo_e_documental_protegido:Q060` turn `1`
- `langgraph`: status 200, latency 233.4ms, keyword pass `True`, quality `100`, reason `dados estruturados devem passar por service deterministico`
  answer: Cadastro e documentacao:
Situacao administrativa do seu cadastro hoje: com pendencias.
Situacao documental do seu cadastro hoje:
- Email cadastral: regular. maria.oliveira@mock.eduassist.local
- Telefone cadastral: regular. +55 11 98888-1001
- Documentacao administrativa: com pendencias. Ainda falta reenviar um comprovante de residencia atualizado para concluir a conferência documental.
Proximo passo: Envie o comprovante atualizado pela secretaria ou pelo canal de documentos para concluir a conferência.

Financeiro:
- Lucas Oliveira: 1 fatura(s) em aberto e 0 vencida(s).
- Ana Oliveira: 2 fatura(s) em aberto e 0 vencida(s).
- `crewai`: status 200, latency 406.3ms, keyword pass `True`, quality `100`, reason `crewai_protected_fast_path`
  answer: Panorama combinado de documentacao e financeiro das contas vinculadas:
- Lucas Oliveira: documentacao regular e completa; financeiro com 1 fatura(s) em aberto e 0 vencida(s).
- Ana Oliveira: documentacao com pendencias; financeiro com 2 fatura(s) em aberto e 0 vencida(s).
- `python_functions`: status 200, latency 266.1ms, keyword pass `True`, quality `100`, reason `python_functions_native_structured:finance`
  answer: Cadastro e documentacao:
Situacao administrativa do seu cadastro hoje: com pendencias.
Situacao documental do seu cadastro hoje:
- Email cadastral: regular. maria.oliveira@mock.eduassist.local
- Telefone cadastral: regular. +55 11 98888-1001
- Documentacao administrativa: com pendencias. Ainda falta reenviar um comprovante de residencia atualizado para concluir a conferência documental.
Proximo passo: Envie o comprovante atualizado pela secretaria ou pelo canal de documentos para concluir a conferência.

Financeiro:
- Lucas Oliveira: 1 fatura(s) em aberto e 0 vencida(s).
- Ana Oliveira: 2 fatura(s) em aberto e 0 vencida(s).
- `llamaindex`: status 200, latency 254.5ms, keyword pass `True`, quality `100`, reason `dados estruturados devem passar por service deterministico`
  answer: Cadastro e documentacao:
Situacao administrativa do seu cadastro hoje: com pendencias.
Situacao documental do seu cadastro hoje:
- Email cadastral: regular. maria.oliveira@mock.eduassist.local
- Telefone cadastral: regular. +55 11 98888-1001
- Documentacao administrativa: com pendencias. Ainda falta reenviar um comprovante de residencia atualizado para concluir a conferência documental.
Proximo passo: Envie o comprovante atualizado pela secretaria ou pelo canal de documentos para concluir a conferência.

Financeiro:
- Lucas Oliveira: 1 fatura(s) em aberto e 0 vencida(s).
- Ana Oliveira: 2 fatura(s) em aberto e 0 vencida(s).
- `specialist_supervisor`: status 200, latency 2050.1ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_tool_first:admin_finance_overview`
  answer: Situacao administrativa do seu cadastro hoje: com pendencias.
Situacao documental do seu cadastro hoje:
- Email cadastral: regular. maria.oliveira@mock.eduassist.local
- Telefone cadastral: regular. +55 11 98888-1001
- Documentacao administrativa: com pendencias. Ainda falta reenviar um comprovante de residencia atualizado para concluir a conferência documental.
Proximo passo: Envie o comprovante atualizado pela secretaria ou pelo canal de documentos para concluir a conferência.

Financeiro:
- Lucas Oliveira: 1 fatura(s) em aberto e 0 vencida(s).
- Ana Oliveira: 2 fatura(s) em aberto e 0 vencida(s).

### Quais documentos eu ainda preciso enviar e por qual canal a escola aceita esse envio?

- Slice: `protected`
- Thread: `system_bank:administrativo_e_documental_protegido:Q061` turn `1`
- `langgraph`: status 200, latency 98.2ms, keyword pass `True`, quality `100`, reason `status administrativo autenticado exige service deterministico`
  answer: Hoje estes sao os responsaveis e canais mais diretos por assunto:
- Secretaria: bot, secretaria presencial, email institucional ou portal.
- `crewai`: status 200, latency 175.2ms, keyword pass `True`, quality `100`, reason `protected_shadow_needs_student_clarification`
  answer: Posso te ajudar com Lucas Oliveira, Ana Oliveira. Me diga qual aluno voce quer consultar.
- `python_functions`: status 200, latency 92.2ms, keyword pass `True`, quality `100`, reason `python_functions_native_structured:institution`
  answer: Hoje estes sao os responsaveis e canais mais diretos por assunto:
- Secretaria: bot, secretaria presencial, email institucional ou portal.
- `llamaindex`: status 200, latency 114.5ms, keyword pass `True`, quality `100`, reason `status administrativo autenticado exige service deterministico`
  answer: Hoje estes sao os responsaveis e canais mais diretos por assunto:
- Secretaria: bot, secretaria presencial, email institucional ou portal.
- `specialist_supervisor`: status 200, latency 2054.4ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_tool_first:human_handoff`
  answer: Encaminhei sua solicitacao para a fila de secretaria. Protocolo: ATD-20260401-06EDAED6. Status atual: queued. Se preferir, voce tambem pode seguir pelo WhatsApp oficial (11) 97500-2040.

### Entao abra um protocolo para eu regularizar isso com a secretaria.

- Slice: `workflow`
- Thread: `system_bank:administrativo_e_documental_protegido:Q061` turn `2`
- `langgraph`: status 200, latency 129.7ms, keyword pass `True`, quality `100`, reason `status administrativo autenticado exige service deterministico`
  answer: Sua conta tem mais de um aluno vinculado. Diga qual aluno deseja consultar: Lucas Oliveira (MAT-2026-001), Ana Oliveira (MAT-2026-002).
- `crewai`: status 200, latency 176.0ms, keyword pass `True`, quality `100`, reason `workflow_not_found`
  answer: Nao encontrei um protocolo ativo nesta conversa para retomar agora. Se voce quiser, eu posso abrir o pedido, te dizer o protocolo, consultar o status ou montar um resumo quando houver um fluxo ativo.
- `python_functions`: status 200, latency 136.1ms, keyword pass `True`, quality `100`, reason `status administrativo autenticado exige service deterministico`
  answer: Sua conta tem mais de um aluno vinculado. Diga qual aluno deseja consultar: Lucas Oliveira (MAT-2026-001), Ana Oliveira (MAT-2026-002).
- `llamaindex`: status 200, latency 155.3ms, keyword pass `True`, quality `100`, reason `status administrativo autenticado exige service deterministico`
  answer: Sua conta tem mais de um aluno vinculado. Diga qual aluno deseja consultar: Lucas Oliveira (MAT-2026-001), Ana Oliveira (MAT-2026-002).
- `specialist_supervisor`: status 200, latency 13769.6ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_direct:workflow_specialist`
  answer: Entendi! Um protocolo para regularização com a secretaria já está sendo tratado. O código do seu ticket é **ATD-20260401-06EDAED6**. A secretaria entrará em contato em breve para dar andamento à sua solicitação.

### Meu cadastro esta regular para fazer provas e atividades?

- Slice: `protected`
- Thread: `system_bank:administrativo_e_documental_protegido:Q063` turn `1`
- `langgraph`: status 200, latency 134.6ms, keyword pass `True`, quality `100`, reason `o turno atual trouxe pistas explicitas de outro dominio protegido e o roteamento foi corrigido`
  answer: Essa consulta depende de autenticacao e vinculo da sua conta no Telegram. Use o portal da escola para gerar o codigo de vinculacao e depois envie o comando `/start link_<codigo>` ao bot.
- `crewai`: status 200, latency 169.0ms, keyword pass `True`, quality `100`, reason `crewai_protected_auth_required`
  answer: Essa consulta depende de autenticacao e vinculo da sua conta no Telegram. Use o portal da escola para gerar o codigo de vinculacao e depois envie o comando /start link_<codigo> ao bot.
- `python_functions`: status 200, latency 126.6ms, keyword pass `True`, quality `100`, reason `python_functions_native_structured:institution`
  answer: Essa consulta depende de autenticacao e vinculo da sua conta no Telegram. Use o portal da escola para gerar o codigo de vinculacao e depois envie o comando `/start link_<codigo>` ao bot.
- `llamaindex`: status 200, latency 145.3ms, keyword pass `True`, quality `100`, reason `status administrativo autenticado exige service deterministico`
  answer: Essa consulta depende de autenticacao e vinculo da sua conta no Telegram. Use o portal da escola para gerar o codigo de vinculacao e depois envie o comando `/start link_<codigo>` ao bot.
- `specialist_supervisor`: status 200, latency 3683.0ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_fast_path:general_knowledge`
  answer: Não tenho acesso a informações pessoais ou cadastros. Para verificar a situação do seu cadastro, você deve consultar o sistema ou a instituição responsável pelas provas e atividades.

### Resuma minha situacao cadastral em linguagem de checklist, com o que esta ok e o que falta.

- Slice: `protected`
- Thread: `system_bank:administrativo_e_documental_protegido:Q064` turn `1`
- `langgraph`: status 200, latency 125.5ms, keyword pass `True`, quality `100`, reason `o turno atual trouxe pistas explicitas de outro dominio protegido e o roteamento foi corrigido`
  answer: Sua conta tem mais de um aluno vinculado. Diga qual aluno deseja consultar: Lucas Oliveira (MAT-2026-001), Ana Oliveira (MAT-2026-002).
- `crewai`: status 200, latency 158.0ms, keyword pass `True`, quality `100`, reason `protected_shadow_unmatched_student_reference`
  answer: Hoje eu nao encontrei Que entre os alunos vinculados a esta conta. No momento, os alunos que aparecem aqui sao: Lucas Oliveira, Ana Oliveira. Se quiser, me diga qual deles voce quer consultar.
- `python_functions`: status 200, latency 158.3ms, keyword pass `True`, quality `100`, reason `python_functions_native_structured:institution`
  answer: Por nada. Se quiser, pode seguir com a proxima duvida que eu continuo com voce por aqui.
- `llamaindex`: status 200, latency 170.0ms, keyword pass `True`, quality `100`, reason `llamaindex_protected_records_fast_path`
  answer: Hoje, o proximo passo do seu cadastro e este: Envie o comprovante atualizado pela secretaria ou pelo canal de documentos para concluir a conferência.
- `specialist_supervisor`: status 200, latency 12667.4ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_multi_direct:institution_specialist+workflow_specialist`
  answer: Institucional: Como EduAssist, seu assistente institucional, eu não consigo acessar dados pessoais de matrícula ou cadastro para resumir sua situação em uma checklist. Minhas ferramentas me permitem apenas fornecer informações públicas gerais sobre a escola, como o perfil institucional, diretórios e calendários. Para verificar sua situação cadastral, por favor, entre em contato diretamente com a secretaria da escola através dos canais de atendimento disponíveis no site ou ligue para (11) 3333-4200.

Atendimento: Para que eu possa te ajudar a resumir sua situação cadastral em formato de checklist, preciso transferir seu atendimento para um de nossos especialistas. Eles terão acesso às informações necessárias para detalhar o que está ok e o que falta. Já abri um chamado para você com o número de protocolo **ATD-20260401-2C825BB0** na fila de **Atendimento**.

