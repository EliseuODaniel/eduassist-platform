# Two-Stack Shadow Comparison Report

## Summary

- Total prompts: 40
- `protected`: baseline ok 13/13, CrewAI ok 13/13, baseline keyword pass 13/13, CrewAI keyword pass 10/13, quality 100.0 vs 93.8, latency 160.4ms vs 149.7ms
- `public`: baseline ok 13/13, CrewAI ok 13/13, baseline keyword pass 13/13, CrewAI keyword pass 13/13, quality 100.0 vs 100.0, latency 4327.2ms vs 42.1ms
- `workflow`: baseline ok 7/7, CrewAI ok 7/7, baseline keyword pass 7/7, CrewAI keyword pass 7/7, quality 100.0 vs 100.0, latency 1916.2ms vs 50.9ms
- `support`: baseline ok 7/7, CrewAI ok 7/7, baseline keyword pass 7/7, CrewAI keyword pass 7/7, quality 100.0 vs 100.0, latency 397.1ms vs 46.9ms

## By Category

- `threaded_real_transcript`: baseline ok 40/40, CrewAI ok 40/40, baseline keyword pass 40/40, CrewAI keyword pass 37/40, quality 100.0 vs 98.0

## Error Types

- `baseline`: nenhum
- `crewai`: missing_expected_keyword=3, repetitive_reply=2

## Quality Signals

- `baseline`: repair_ack 2/2, followup_adaptation 5/5, personalization 17/17
- `crewai`: repair_ack 2/2, followup_adaptation 5/5, personalization 14/17

## By Thread

- `real_guardian_identity_and_student_scope` (protected/threaded_real_transcript): baseline keyword pass 9/9, CrewAI keyword pass 9/9, quality 100.0 vs 100.0
- `real_document_channels_conflict` (protected/threaded_real_transcript): baseline keyword pass 6/6, CrewAI keyword pass 6/6, quality 100.0 vs 100.0
- `real_guardian_grades_and_finance_555001` (protected/threaded_real_transcript): baseline keyword pass 3/3, CrewAI keyword pass 0/3, quality 100.0 vs 73.3
- `real_public_catalog_777001` (public/threaded_real_transcript): baseline keyword pass 4/4, CrewAI keyword pass 4/4, quality 100.0 vs 100.0
- `real_public_after_protocol_777053` (public/threaded_real_transcript): baseline keyword pass 2/2, CrewAI keyword pass 2/2, quality 100.0 vs 100.0
- `real_public_after_protocol_777054` (public/threaded_real_transcript): baseline keyword pass 2/2, CrewAI keyword pass 2/2, quality 100.0 vs 100.0
- `real_visit_lifecycle_777052` (workflow/threaded_real_transcript): baseline keyword pass 4/4, CrewAI keyword pass 4/4, quality 100.0 vs 100.0
- `real_request_lifecycle_777051` (workflow/threaded_real_transcript): baseline keyword pass 3/3, CrewAI keyword pass 3/3, quality 100.0 vs 100.0
- `real_support_finance_handoff_1649845499` (support/threaded_real_transcript): baseline keyword pass 3/3, CrewAI keyword pass 3/3, quality 100.0 vs 100.0
- `real_support_handoff_repair_1649845499` (support/threaded_real_transcript): baseline keyword pass 2/2, CrewAI keyword pass 2/2, quality 100.0 vs 100.0
- `real_support_secretaria_handoff_555001` (support/threaded_real_transcript): baseline keyword pass 2/2, CrewAI keyword pass 2/2, quality 100.0 vs 100.0

## Prompt Results

### estou logado como?

- Slice: `protected`
- Category: `threaded_real_transcript`
- Thread: `real_guardian_identity_and_student_scope` turn `1`
- Baseline: status 200, latency 137.4ms, keyword pass `True`, quality `100`
- CrewAI: status 200, latency 45.0ms, keyword pass `True`, quality `100`
- Baseline quality signals: repair_ack=None, followup_adaptation=None, personalization=True
- CrewAI quality signals: repair_ack=None, followup_adaptation=None, personalization=True
- Baseline answer: Voce esta falando aqui como Maria Oliveira, no perfil de responsavel. Sua conta esta vinculada a Lucas Oliveira e Ana Oliveira. Por aqui eu consigo consultar notas, faltas, proximas provas, matricula, financeiro, boletos, dentro das permissoes dessa vinculacao.
- CrewAI answer: Voce esta autenticado aqui como Maria Oliveira. Sua conta esta vinculada a Lucas Oliveira, Ana Oliveira e pode consultar notas, frequencia, avaliacoes, documentacao e financeiro desses alunos.

### quais notas do meu filho lucas

- Slice: `protected`
- Category: `threaded_real_transcript`
- Thread: `real_guardian_identity_and_student_scope` turn `2`
- Baseline: status 200, latency 170.5ms, keyword pass `True`, quality `100`
- CrewAI: status 200, latency 243.4ms, keyword pass `True`, quality `100`
- Baseline quality signals: repair_ack=None, followup_adaptation=None, personalization=True
- CrewAI quality signals: repair_ack=None, followup_adaptation=None, personalization=True
- Baseline answer: Notas de Lucas Oliveira:
- Biologia - Avaliacao B1: 8.40/10.00
- Biologia - Avaliacao 2026-B1 - BIO: 7.00/10.00
- Biologia - Trabalho B1: 8.10/10.00
- Biologia - Avaliacao B2: 8.60/10.00
- CrewAI answer: As notas mais recentes de Lucas Oliveira incluem Biologia: 8.40/10.00; Biologia: 7.00/10.00; Biologia: 8.10/10.00.

### quais notas do meu filho joão

- Slice: `protected`
- Category: `threaded_real_transcript`
- Thread: `real_guardian_identity_and_student_scope` turn `3`
- Baseline: status 200, latency 134.9ms, keyword pass `True`, quality `100`
- CrewAI: status 200, latency 37.5ms, keyword pass `True`, quality `100`
- Baseline quality signals: repair_ack=None, followup_adaptation=None, personalization=True
- CrewAI quality signals: repair_ack=None, followup_adaptation=None, personalization=True
- Baseline answer: Hoje eu nao encontrei Joao entre os alunos vinculados a esta conta. No momento, os alunos que aparecem aqui sao: Lucas Oliveira (MAT-2026-001), Ana Oliveira (MAT-2026-002). Se quiser, me diga qual deles voce quer consultar.
- CrewAI answer: Hoje eu nao encontrei Joao entre os alunos vinculados a esta conta. No momento, os alunos que aparecem aqui sao: Lucas Oliveira, Ana Oliveira. Se quiser, me diga qual deles voce quer consultar.

### qual situação de documentação do lucas?

- Slice: `protected`
- Category: `threaded_real_transcript`
- Thread: `real_guardian_identity_and_student_scope` turn `4`
- Baseline: status 200, latency 193.3ms, keyword pass `True`, quality `100`
- CrewAI: status 200, latency 236.6ms, keyword pass `True`, quality `100`
- Baseline quality signals: repair_ack=None, followup_adaptation=None, personalization=True
- CrewAI quality signals: repair_ack=None, followup_adaptation=None, personalization=True
- Baseline answer: Situacao documental de Lucas Oliveira hoje: regular.
- CrewAI answer: A situacao documental de Lucas Oliveira hoje esta regular e completa.

### lucas oliveira, o luquinha

- Slice: `protected`
- Category: `threaded_real_transcript`
- Thread: `real_guardian_identity_and_student_scope` turn `5`
- Note: real transcript disambiguation turn
- Baseline: status 200, latency 138.7ms, keyword pass `True`, quality `100`
- CrewAI: status 200, latency 34.0ms, keyword pass `True`, quality `100`
- Baseline quality signals: repair_ack=None, followup_adaptation=None, personalization=True
- CrewAI quality signals: repair_ack=None, followup_adaptation=None, personalization=True
- Baseline answer: Perfeito, seguimos com Lucas Oliveira. Posso te ajudar com notas, faltas, proximas provas, matricula, financeiro, boletos. Se quiser, ja me diga o que voce quer ver primeiro.
- CrewAI answer: Perfeito, seguimos com Lucas Oliveira. Posso te ajudar com notas, frequencia, faltas, proximas provas, documentacao, matricula e financeiro.

### quais próximas provas do lucas

- Slice: `protected`
- Category: `threaded_real_transcript`
- Thread: `real_guardian_identity_and_student_scope` turn `6`
- Baseline: status 200, latency 231.3ms, keyword pass `True`, quality `100`
- CrewAI: status 200, latency 233.5ms, keyword pass `True`, quality `100`
- Baseline quality signals: repair_ack=None, followup_adaptation=None, personalization=True
- CrewAI quality signals: repair_ack=None, followup_adaptation=None, personalization=True
- Baseline answer: Proximas avaliacoes de Lucas Oliveira:
- Turma: 1o Ano A
- Biologia - Avaliacao B1: 2026-04-10
- Fisica - Avaliacao 2026-B1 - FIS: 2026-04-10
- Historia - Avaliacao B1: 2026-04-10
- Ingles - Avaliacao B1: 2026-04-10
- Matematica - Avaliacao 2026-B1 - MAT: 2026-04-10
- Matematica - Avaliacao B1: 2026-04-10
- CrewAI answer: A proxima avaliacao registrada de Lucas Oliveira e Avaliacao B1 em 2026-04-10.

### qual a matricula do lucas

- Slice: `protected`
- Category: `threaded_real_transcript`
- Thread: `real_guardian_identity_and_student_scope` turn `7`
- Baseline: status 200, latency 163.6ms, keyword pass `True`, quality `100`
- CrewAI: status 200, latency 250.9ms, keyword pass `True`, quality `100`
- Baseline quality signals: repair_ack=None, followup_adaptation=None, personalization=True
- CrewAI quality signals: repair_ack=None, followup_adaptation=None, personalization=True
- Baseline answer: A matricula de Lucas Oliveira e MAT-2026-001. Turma atual: 1o Ano A.
- CrewAI answer: A matricula de Lucas Oliveira e MAT-2026-001.

### e como estão as faltas do lucas

- Slice: `protected`
- Category: `threaded_real_transcript`
- Thread: `real_guardian_identity_and_student_scope` turn `8`
- Note: real transcript regression: previously echoed enrollment instead of attendance
- Baseline: status 200, latency 183.5ms, keyword pass `True`, quality `100`
- CrewAI: status 200, latency 283.3ms, keyword pass `True`, quality `100`
- Baseline quality signals: repair_ack=None, followup_adaptation=True, personalization=True
- CrewAI quality signals: repair_ack=None, followup_adaptation=True, personalization=True
- Baseline answer: No recorte de faltas de Lucas Oliveira, eu encontrei 6 falta(s) e 7 atraso(s).
- CrewAI answer: Lucas Oliveira tem 3 falta(s) e 3 registro(s) de atraso neste recorte.

### E a frequencia do Lucas?

- Slice: `protected`
- Category: `threaded_real_transcript`
- Thread: `real_guardian_identity_and_student_scope` turn `9`
- Note: real transcript regression: previously treated frequencia as student name
- Baseline: status 200, latency 219.1ms, keyword pass `True`, quality `100`
- CrewAI: status 200, latency 242.6ms, keyword pass `True`, quality `100`
- Baseline quality signals: repair_ack=None, followup_adaptation=True, personalization=True
- CrewAI quality signals: repair_ack=None, followup_adaptation=True, personalization=True
- Baseline answer: Panorama de frequencia de Lucas Oliveira:
Resumo geral:
- Presencas registradas: 15
- Faltas registradas: 6
- Atrasos registrados: 7
- Minutos somados de ausencia: 370
- CrewAI answer: Na frequencia de Lucas Oliveira, eu encontrei 12 registro(s) neste recorte: 6 presenca(s), 3 falta(s) e 3 atraso(s).

### quais documentos faltam pra ana

- Slice: `protected`
- Category: `threaded_real_transcript`
- Thread: `real_document_channels_conflict` turn `1`
- Note: real transcript regression: previously answered the guardian admin profile instead of Ana
- Baseline: status 200, latency 159.3ms, keyword pass `True`, quality `100`
- CrewAI: status 200, latency 239.6ms, keyword pass `True`, quality `100`
- Baseline quality signals: repair_ack=None, followup_adaptation=None, personalization=True
- CrewAI quality signals: repair_ack=None, followup_adaptation=None, personalization=True
- Baseline answer: Situacao documental de Ana Oliveira hoje: com pendencias.
- Identificacao escolar do aluno: regular. Codigo de matricula: MAT-2026-002
- Responsavel vinculado: regular. Maria Oliveira
- Documentacao escolar do aluno: com pendencias. Ainda falta anexar um comprovante de residencia atualizado para Ana Oliveira concluir a conferencia documental.
Proximo passo: Envie o comprovante atualizado pelo portal autenticado ou pela secretaria escolar para concluir a analise.
- CrewAI answer: A situacao documental de Ana Oliveira hoje esta com pendencias.

### posso enviar por fax?

- Slice: `public`
- Category: `threaded_real_transcript`
- Thread: `real_document_channels_conflict` turn `2`
- Note: real transcript regression: previously implied fax was accepted
- Baseline: status 200, latency 1582.6ms, keyword pass `True`, quality `100`
- CrewAI: status 200, latency 44.3ms, keyword pass `True`, quality `100`
- Baseline quality signals: repair_ack=None, followup_adaptation=None, personalization=None
- CrewAI quality signals: repair_ack=None, followup_adaptation=None, personalization=None
- Baseline answer: Hoje a escola nao utiliza fax para envio de documentos. Para isso, use portal institucional, email da secretaria, secretaria presencial.
- CrewAI answer: Hoje a escola nao utiliza fax para envio de documentos. Para isso, use portal institucional, email da secretaria ou secretaria presencial.

### qual o número do fax?

- Slice: `public`
- Category: `threaded_real_transcript`
- Thread: `real_document_channels_conflict` turn `3`
- Baseline: status 200, latency 1705.5ms, keyword pass `True`, quality `100`
- CrewAI: status 200, latency 40.0ms, keyword pass `True`, quality `100`
- Baseline quality signals: repair_ack=None, followup_adaptation=None, personalization=None
- CrewAI quality signals: repair_ack=None, followup_adaptation=None, personalization=None
- Baseline answer: Hoje a escola não utiliza fax. Para entrar em contato por telefone, o número da secretaria é (11) 3333-4200.
- CrewAI answer: Hoje nao existe numero de fax publicado, porque a escola nao utiliza fax institucional.

### mas antes você respondeu que eu podia enviar por fax

- Slice: `public`
- Category: `threaded_real_transcript`
- Thread: `real_document_channels_conflict` turn `4`
- Note: repair turn from real transcript
- Baseline: status 200, latency 3536.1ms, keyword pass `True`, quality `100`
- CrewAI: status 200, latency 45.8ms, keyword pass `True`, quality `100`
- Baseline quality signals: repair_ack=True, followup_adaptation=True, personalization=None
- CrewAI quality signals: repair_ack=True, followup_adaptation=True, personalization=None
- Baseline answer: Peço desculpas pela confusão! O Colégio Horizonte não utiliza fax atualmente. Para enviar documentos, você pode usar nosso portal institucional, o e-mail da secretaria ou ir diretamente à secretaria presencial.
- CrewAI answer: Voce esta certo em cobrar essa correcao. Corrigindo: hoje a escola nao utiliza fax institucional. Para documentos, use portal institucional, email da secretaria ou secretaria presencial.

### e se eu mandar por telegrama, serve?

- Slice: `public`
- Category: `threaded_real_transcript`
- Thread: `real_document_channels_conflict` turn `5`
- Note: real transcript regression: previously repeated generic digital-channel copy
- Baseline: status 200, latency 1550.3ms, keyword pass `True`, quality `100`
- CrewAI: status 200, latency 40.0ms, keyword pass `True`, quality `100`
- Baseline quality signals: repair_ack=None, followup_adaptation=True, personalization=None
- CrewAI quality signals: repair_ack=None, followup_adaptation=True, personalization=None
- Baseline answer: Hoje a escola nao publica telegrama como canal valido para documentos. Para isso, use portal institucional, email da secretaria, secretaria presencial.
- CrewAI answer: Hoje a escola nao publica telegrama como canal valido. Para documentos, use portal institucional, email da secretaria ou secretaria presencial.

### qual sua caixa postal?

- Slice: `public`
- Category: `threaded_real_transcript`
- Thread: `real_document_channels_conflict` turn `6`
- Baseline: status 200, latency 3352.0ms, keyword pass `True`, quality `100`
- CrewAI: status 200, latency 45.6ms, keyword pass `True`, quality `100`
- Baseline quality signals: repair_ack=None, followup_adaptation=None, personalization=True
- CrewAI quality signals: repair_ack=None, followup_adaptation=None, personalization=True
- Baseline answer: Hoje a escola não utiliza caixa postal para o envio de documentos. Para isso, você pode usar nosso portal institucional, o e-mail da secretaria ou ir diretamente à secretaria presencial.
- CrewAI answer: Hoje a escola nao trabalha com caixa postal para esse tipo de envio. Para documentos, use portal institucional, email da secretaria ou secretaria presencial.

### quero ver minhas notas

- Slice: `protected`
- Category: `threaded_real_transcript`
- Thread: `real_guardian_grades_and_finance_555001` turn `1`
- Note: real transcript prompt under current state drift: this chat is no longer linked in the current environment
- Baseline: status 200, latency 119.1ms, keyword pass `True`, quality `100`
- CrewAI: status 200, latency 32.4ms, keyword pass `False`, quality `80`
- CrewAI errors: missing_expected_keyword
- Baseline quality signals: repair_ack=None, followup_adaptation=None, personalization=True
- CrewAI quality signals: repair_ack=None, followup_adaptation=None, personalization=False
- Baseline answer: Essa consulta depende de autenticacao e vinculo da sua conta no Telegram. Use o portal da escola para gerar o codigo de vinculacao e depois envie o comando `/start link_<codigo>` ao bot.
- CrewAI answer: Para continuar por aqui, eu preciso que sua conta do Telegram esteja vinculada a um responsavel autenticado.

### quero ver as notas do Lucas Oliveira

- Slice: `protected`
- Category: `threaded_real_transcript`
- Thread: `real_guardian_grades_and_finance_555001` turn `2`
- Note: real transcript prompt under current state drift: this chat is no longer linked in the current environment
- Baseline: status 200, latency 117.0ms, keyword pass `True`, quality `100`
- CrewAI: status 200, latency 33.8ms, keyword pass `False`, quality `70`
- CrewAI errors: missing_expected_keyword, repetitive_reply
- Baseline quality signals: repair_ack=None, followup_adaptation=None, personalization=True
- CrewAI quality signals: repair_ack=None, followup_adaptation=None, personalization=False
- Baseline answer: Essa consulta depende de autenticacao e vinculo da sua conta no Telegram. Use o portal da escola para gerar o codigo de vinculacao e depois envie o comando `/start link_<codigo>` ao bot.
- CrewAI answer: Para continuar por aqui, eu preciso que sua conta do Telegram esteja vinculada a um responsavel autenticado.

### quero ver o financeiro da Ana Oliveira

- Slice: `protected`
- Category: `threaded_real_transcript`
- Thread: `real_guardian_grades_and_finance_555001` turn `3`
- Note: real transcript prompt under current state drift: this chat is no longer linked in the current environment
- Baseline: status 200, latency 117.8ms, keyword pass `True`, quality `100`
- CrewAI: status 200, latency 33.1ms, keyword pass `False`, quality `70`
- CrewAI errors: missing_expected_keyword, repetitive_reply
- Baseline quality signals: repair_ack=None, followup_adaptation=None, personalization=True
- CrewAI quality signals: repair_ack=None, followup_adaptation=None, personalization=False
- Baseline answer: Essa consulta depende de autenticacao e vinculo da sua conta no Telegram. Use o portal da escola para gerar o codigo de vinculacao e depois envie o comando `/start link_<codigo>` ao bot.
- CrewAI answer: Para continuar por aqui, eu preciso que sua conta do Telegram esteja vinculada a um responsavel autenticado.

### quais documentos sao exigidos para matricula?

- Slice: `public`
- Category: `threaded_real_transcript`
- Thread: `real_public_catalog_777001` turn `1`
- Baseline: status 200, latency 5423.5ms, keyword pass `True`, quality `100`
- CrewAI: status 200, latency 40.9ms, keyword pass `True`, quality `100`
- Baseline quality signals: repair_ack=None, followup_adaptation=None, personalization=None
- CrewAI quality signals: repair_ack=None, followup_adaptation=None, personalization=None
- Baseline answer: Para a matrícula, precisamos do formulário cadastral preenchido, documento de identificação e CPF do aluno (se tiver), histórico escolar e comprovante de residência. Também é necessário o documento de identificação do responsável legal. Se precisar, posso detalhar as etapas da matrícula ou como enviar esses documentos.
- CrewAI answer: Hoje os documentos exigidos para a matricula publicados pela escola sao:
- Formulario cadastral preenchido
- Documento de identificacao do aluno
- CPF do aluno, quando houver
- Historico escolar
- Comprovante de residencia atualizado
- Documento de identificacao do responsavel legal

### qual o horario da biblioteca? qual o nome da biblioteca?

- Slice: `public`
- Category: `threaded_real_transcript`
- Thread: `real_public_catalog_777001` turn `2`
- Baseline: status 200, latency 6684.7ms, keyword pass `True`, quality `100`
- CrewAI: status 200, latency 40.4ms, keyword pass `True`, quality `100`
- Baseline quality signals: repair_ack=None, followup_adaptation=None, personalization=True
- CrewAI quality signals: repair_ack=None, followup_adaptation=None, personalization=True
- Baseline answer: A nossa Biblioteca Aurora está aberta de segunda a sexta-feira, das 7h30 às 18h00, pronta para receber você!
- CrewAI answer: A Biblioteca Aurora atende ao publico de segunda a sexta, das 7h30 as 18h00.

### qual o telefone e o fax?

- Slice: `public`
- Category: `threaded_real_transcript`
- Thread: `real_public_catalog_777001` turn `3`
- Baseline: status 200, latency 3829.4ms, keyword pass `True`, quality `100`
- CrewAI: status 200, latency 43.1ms, keyword pass `True`, quality `100`
- Baseline quality signals: repair_ack=None, followup_adaptation=None, personalization=None
- CrewAI quality signals: repair_ack=None, followup_adaptation=None, personalization=None
- Baseline answer: Olá! Atualmente, não utilizamos fax aqui no Colégio Horizonte. Para falar conosco por telefone, o número da secretaria é (11) 3333-4200. Estamos à disposição para ajudar!
- CrewAI answer: Secretaria (telefone): (11) 3333-4200 Hoje a escola nao utiliza fax institucional.

### qual a mensalidade do ensino medio?

- Slice: `public`
- Category: `threaded_real_transcript`
- Thread: `real_public_catalog_777001` turn `4`
- Baseline: status 200, latency 7169.8ms, keyword pass `True`, quality `100`
- CrewAI: status 200, latency 41.8ms, keyword pass `True`, quality `100`
- Baseline quality signals: repair_ack=None, followup_adaptation=None, personalization=None
- CrewAI quality signals: repair_ack=None, followup_adaptation=None, personalization=None
- Baseline answer: Olá! A mensalidade de referência para o Ensino Médio (turno da manhã) em 2026 é de R$ 1.450,00, e a taxa de matrícula é de R$ 350,00. Temos condições especiais para irmãos e para pagamentos feitos em dia. Se precisar de mais informações sobre bolsas, descontos ou o processo de matrícula, é só me perguntar!
- CrewAI answer: A mensalidade de referencia para Ensino Medio e R$ 1450.00, com taxa de matricula de R$ 350.00.

### oi

- Slice: `public`
- Category: `threaded_real_transcript`
- Thread: `real_public_after_protocol_777053` turn `1`
- Note: workflow contamination check after older protocol thread
- Baseline: status 200, latency 3695.3ms, keyword pass `True`, quality `100`
- CrewAI: status 200, latency 42.0ms, keyword pass `True`, quality `100`
- Baseline quality signals: repair_ack=None, followup_adaptation=None, personalization=None
- CrewAI quality signals: repair_ack=None, followup_adaptation=None, personalization=None
- Baseline answer: Olá! Que bom ter você por aqui. Sou o EduAssist, seu assistente no Colégio Horizonte. Posso te ajudar com informações sobre matrículas, bolsas, descontos, visitas, horários, calendário escolar, biblioteca, uniforme, transporte e a estrutura da escola. Se você tiver sua conta vinculada, também consigo consultar notas, faltas e informações financeiras.
- CrewAI answer: Oi. Eu posso te ajudar por aqui com informacoes da escola, canais oficiais, matricula, visitas, biblioteca, atividades e rotina escolar.

### qual instagram do colégio?

- Slice: `public`
- Category: `threaded_real_transcript`
- Thread: `real_public_after_protocol_777053` turn `2`
- Note: workflow contamination check after older protocol thread
- Baseline: status 200, latency 6554.8ms, keyword pass `True`, quality `100`
- CrewAI: status 200, latency 41.4ms, keyword pass `True`, quality `100`
- Baseline quality signals: repair_ack=None, followup_adaptation=None, personalization=None
- CrewAI quality signals: repair_ack=None, followup_adaptation=None, personalization=None
- Baseline answer: O Instagram oficial do Colégio Horizonte é @colegiohorizonte. Se precisar de mais alguma informação, como nosso site ou outros canais de contato, é só me avisar!
- CrewAI answer: O Instagram institucional e @colegiohorizonte.

### oi

- Slice: `public`
- Category: `threaded_real_transcript`
- Thread: `real_public_after_protocol_777054` turn `1`
- Note: workflow contamination check after older protocol thread
- Baseline: status 200, latency 3639.7ms, keyword pass `True`, quality `100`
- CrewAI: status 200, latency 40.6ms, keyword pass `True`, quality `100`
- Baseline quality signals: repair_ack=None, followup_adaptation=None, personalization=None
- CrewAI quality signals: repair_ack=None, followup_adaptation=None, personalization=None
- Baseline answer: Oi. Voce esta falando com o EduAssist do Colegio Horizonte. Posso te ajudar com matricula, bolsas, descontos e visitas, turnos, horarios, calendario e rotina escolar, biblioteca, uniforme, transporte e estrutura da escola e canais oficiais, secretaria e orientacao por setor. Se sua conta estiver vinculada, eu tambem consigo consultar notas, faltas e financeiro.
- CrewAI answer: Oi. Eu posso te ajudar por aqui com informacoes da escola, canais oficiais, matricula, visitas, biblioteca, atividades e rotina escolar.

### por que esse colégio é melhor que a concorrencia

- Slice: `public`
- Category: `threaded_real_transcript`
- Thread: `real_public_after_protocol_777054` turn `2`
- Note: public comparative turn after earlier workflow thread
- Baseline: status 200, latency 7529.5ms, keyword pass `True`, quality `100`
- CrewAI: status 200, latency 40.9ms, keyword pass `True`, quality `100`
- Baseline quality signals: repair_ack=None, followup_adaptation=None, personalization=None
- CrewAI quality signals: repair_ack=None, followup_adaptation=None, personalization=None
- Baseline answer: Que ótima pergunta! No Colégio Horizonte, focamos em oferecer uma experiência educacional única. Nossos diferenciais incluem a tutoria acadêmica e o projeto de vida para cada estudante do Ensino Médio, o Espaço Maker integrado ao currículo em projetos interdisciplinares, e um acolhimento estruturado para famílias e estudantes. Se você tiver alguma escola específica em mente, posso te ajudar a comparar alguns pontos, se as informações forem públicas.
- CrewAI answer: Os diferenciais publicados desta escola hoje incluem Biblioteca Aurora, Laboratorio de Ciencias. Eu nao consigo afirmar que ela seja melhor do que uma concorrente especifica sem fontes comparativas confiaveis, mas posso te explicar esses diferenciais com clareza.

### quero agendar uma visita para conhecer a escola na quinta a tarde

- Slice: `workflow`
- Category: `threaded_real_transcript`
- Thread: `real_visit_lifecycle_777052` turn `1`
- Baseline: status 200, latency 1996.6ms, keyword pass `True`, quality `100`
- CrewAI: status 200, latency 65.6ms, keyword pass `True`, quality `100`
- Baseline quality signals: repair_ack=None, followup_adaptation=None, personalization=None
- CrewAI quality signals: repair_ack=None, followup_adaptation=None, personalization=None
- Baseline answer: Pedido de visita registrado para o Colegio Horizonte. Protocolo: VIS-20260327-707B70. Preferencia informada: 2026-04-02 - tarde. Fila responsavel: admissoes. Ticket operacional: ATD-20260327-8FE0FDBE. A equipe comercial valida a janela e retorna com a confirmacao.
- CrewAI answer: Pedido de visita registrado para o Colegio Horizonte. Protocolo: VIS-20260327-707B70. Preferencia informada: 02/04/2026 - tarde. Fila responsavel: admissoes. Ticket operacional: ATD-20260327-8FE0FDBE. A equipe comercial valida a janela e retorna com a confirmacao.

### qual o protocolo da visita?

- Slice: `workflow`
- Category: `threaded_real_transcript`
- Thread: `real_visit_lifecycle_777052` turn `2`
- Baseline: status 200, latency 1881.2ms, keyword pass `True`, quality `100`
- CrewAI: status 200, latency 40.5ms, keyword pass `True`, quality `100`
- Baseline quality signals: repair_ack=None, followup_adaptation=None, personalization=None
- CrewAI quality signals: repair_ack=None, followup_adaptation=None, personalization=None
- Baseline answer: O protocolo da sua visita e VIS-20260327-707B70.
- Ticket operacional: ATD-20260327-8FE0FDBE
- Preferencia registrada: 02/04/2026 - tarde
Se quiser, eu tambem posso te dizer o status, remarcar ou cancelar a visita.
- CrewAI answer: O protocolo da sua visita e VIS-20260327-707B70. - Ticket operacional: ATD-20260327-8FE0FDBE - Preferencia registrada: 02/04/2026 - tarde Se quiser, eu tambem posso te dizer o status, remarcar ou cancelar a visita.

### quero remarcar a visita para sexta de manha

- Slice: `workflow`
- Category: `threaded_real_transcript`
- Thread: `real_visit_lifecycle_777052` turn `3`
- Baseline: status 200, latency 1885.5ms, keyword pass `True`, quality `100`
- CrewAI: status 200, latency 54.5ms, keyword pass `True`, quality `100`
- Baseline quality signals: repair_ack=None, followup_adaptation=None, personalization=None
- CrewAI quality signals: repair_ack=None, followup_adaptation=None, personalization=None
- Baseline answer: Pedido de visita atualizado com a fila de admissions.
- Protocolo: VIS-20260327-707B70
- Ticket operacional: ATD-20260327-8FE0FDBE
- Nova preferencia: 03/04/2026 - manha
Proximo passo: admissions valida a nova janela e retorna com a confirmacao.
- CrewAI answer: Pedido de visita atualizado com a fila de admissoes. - Protocolo: VIS-20260327-707B70 - Ticket operacional: ATD-20260327-8FE0FDBE - Nova preferencia: 27/03/2026 - manha Proximo passo: admissions valida a nova janela e retorna com a confirmacao.

### quero cancelar a visita

- Slice: `workflow`
- Category: `threaded_real_transcript`
- Thread: `real_visit_lifecycle_777052` turn `4`
- Baseline: status 200, latency 1888.1ms, keyword pass `True`, quality `100`
- CrewAI: status 200, latency 52.7ms, keyword pass `True`, quality `100`
- Baseline quality signals: repair_ack=None, followup_adaptation=None, personalization=None
- CrewAI quality signals: repair_ack=None, followup_adaptation=None, personalization=None
- Baseline answer: Sua visita foi cancelada com sucesso no fluxo de admissions. O protocolo é VIS-20260327-707B70 e o ticket operacional é ATD-20260327-8FE0FDBE. Se precisar, posso registrar um novo pedido de visita para você quando for mais conveniente.
- CrewAI answer: Visita cancelada no fluxo de admissoes. - Protocolo: VIS-20260327-707B70 - Ticket operacional: ATD-20260327-8FE0FDBE Se quiser, eu tambem posso registrar um novo pedido de visita quando voce preferir.

### quero protocolar uma solicitacao para a direcao sobre ampliacao do horario da biblioteca

- Slice: `workflow`
- Category: `threaded_real_transcript`
- Thread: `real_request_lifecycle_777051` turn `1`
- Baseline: status 200, latency 1947.6ms, keyword pass `True`, quality `100`
- CrewAI: status 200, latency 63.3ms, keyword pass `True`, quality `100`
- Baseline quality signals: repair_ack=None, followup_adaptation=None, personalization=None
- CrewAI quality signals: repair_ack=None, followup_adaptation=None, personalization=None
- Baseline answer: Solicitacao institucional registrada para direcao. Protocolo: REQ-20260327-D39CD3. Assunto: quero protocolar uma solicitacao para a direcao sobre ampliacao do horario da biblioteca. Fila responsavel: direcao. Ticket operacional: ATD-20260327-DE037E46. A equipe faz a triagem inicial e segue o retorno pelo fluxo institucional.
- CrewAI answer: Solicitacao institucional registrada para direcao. Protocolo: REQ-20260327-D39CD3. Assunto: quero protocolar uma solicitacao para a direcao sobre ampliacao do horario da biblioteca. Fila responsavel: direcao. Ticket operacional: ATD-20260327-DE037E46. A equipe faz a triagem inicial e segue o retorno pelo fluxo institucional.

### qual o protocolo?

- Slice: `workflow`
- Category: `threaded_real_transcript`
- Thread: `real_request_lifecycle_777051` turn `2`
- Baseline: status 200, latency 1893.8ms, keyword pass `True`, quality `100`
- CrewAI: status 200, latency 43.4ms, keyword pass `True`, quality `100`
- Baseline quality signals: repair_ack=None, followup_adaptation=None, personalization=None
- CrewAI quality signals: repair_ack=None, followup_adaptation=None, personalization=None
- Baseline answer: Claro! O protocolo da sua solicitação é REQ-20260327-D39CD3. A área responsável é a direção e o ticket operacional é ATD-20260327-DE037E46. Se precisar, posso resumir o pedido ou verificar o status para você.
- CrewAI answer: O protocolo da sua solicitacao e REQ-20260327-D39CD3. - Ticket operacional: ATD-20260327-DE037E46 - Area responsavel: direcao Se quiser, eu tambem posso resumir o pedido ou verificar o status atual.

### resume meu pedido

- Slice: `workflow`
- Category: `threaded_real_transcript`
- Thread: `real_request_lifecycle_777051` turn `3`
- Baseline: status 200, latency 1920.5ms, keyword pass `True`, quality `100`
- CrewAI: status 200, latency 36.0ms, keyword pass `True`, quality `100`
- Baseline quality signals: repair_ack=None, followup_adaptation=None, personalization=True
- CrewAI quality signals: repair_ack=None, followup_adaptation=None, personalization=True
- Baseline answer: Resumo da sua solicitacao institucional:
- Assunto: quero protocolar uma solicitacao para a direcao sobre ampliacao do horario da biblioteca
- Area responsavel: direcao
- Detalhes registrados: quero protocolar uma solicitacao para a direcao sobre ampliacao do horario da biblioteca
- Protocolo: REQ-20260327-D39CD3
- Ticket operacional: ATD-20260327-DE037E46
- Status atual: em fila
Se quiser, eu tambem posso te dizer o prazo estimado ou quem responde por essa fila.
- CrewAI answer: Resumo da sua solicitacao institucional: - Assunto: quero protocolar uma solicitacao para a direcao sobre ampliacao do horario da biblioteca - Area responsavel: direcao - Protocolo: REQ-20260327-D39CD3 - Ticket operacional: ATD-20260327-DE037E46 - Status atual: queued Se quiser, eu tambem posso te dizer o prazo estimado ou quem responde por essa fila.

### quero falar com um humano sobre o financeiro

- Slice: `support`
- Category: `threaded_real_transcript`
- Thread: `real_support_finance_handoff_1649845499` turn `1`
- Baseline: status 200, latency 192.8ms, keyword pass `True`, quality `100`
- CrewAI: status 200, latency 60.7ms, keyword pass `True`, quality `100`
- Baseline quality signals: repair_ack=None, followup_adaptation=None, personalization=None
- CrewAI quality signals: repair_ack=None, followup_adaptation=None, personalization=None
- Baseline answer: Encaminhei sua solicitacao para a fila de financeiro. Protocolo: ATD-20260327-E190E1B5. Status atual: queued. A equipe humana podera continuar esse atendimento no portal operacional.
- CrewAI answer: Sua solicitacao ja estava registrada na fila de financeiro. Protocolo: ATD-20260327-E190E1B5. Status atual: queued.

### qual o protocolo?

- Slice: `support`
- Category: `threaded_real_transcript`
- Thread: `real_support_finance_handoff_1649845499` turn `2`
- Baseline: status 200, latency 165.1ms, keyword pass `True`, quality `100`
- CrewAI: status 200, latency 34.5ms, keyword pass `True`, quality `100`
- Baseline quality signals: repair_ack=None, followup_adaptation=None, personalization=None
- CrewAI quality signals: repair_ack=None, followup_adaptation=None, personalization=None
- Baseline answer: O protocolo do seu atendimento e ATD-20260327-E190E1B5. Se quiser, posso verificar o status atual ou te dar um resumo do que ja foi registrado.
- CrewAI answer: O protocolo do seu atendimento e ATD-20260327-E190E1B5. Se quiser, posso verificar o status atual ou te dar um resumo do que ja foi registrado.

### qual o status?

- Slice: `support`
- Category: `threaded_real_transcript`
- Thread: `real_support_finance_handoff_1649845499` turn `3`
- Baseline: status 200, latency 176.2ms, keyword pass `True`, quality `100`
- CrewAI: status 200, latency 34.3ms, keyword pass `True`, quality `100`
- Baseline quality signals: repair_ack=None, followup_adaptation=None, personalization=None
- CrewAI quality signals: repair_ack=None, followup_adaptation=None, personalization=None
- Baseline answer: O protocolo do seu atendimento e ATD-20260327-E190E1B5. O status atual e "queued", o que significa que sua solicitacao esta na fila para ser atendida pela equipe de financeiro.
- CrewAI answer: O protocolo do seu atendimento e ATD-20260327-E190E1B5. O status atual e "queued", o que significa que sua solicitacao esta na fila para ser atendida pela equipe de financeiro.

### como falo com um atendente humano?

- Slice: `support`
- Category: `threaded_real_transcript`
- Thread: `real_support_handoff_repair_1649845499` turn `1`
- Baseline: status 200, latency 194.6ms, keyword pass `True`, quality `100`
- CrewAI: status 200, latency 67.7ms, keyword pass `True`, quality `100`
- Baseline quality signals: repair_ack=None, followup_adaptation=None, personalization=None
- CrewAI quality signals: repair_ack=None, followup_adaptation=None, personalization=None
- Baseline answer: Encaminhei sua solicitacao para a fila de atendimento. Protocolo: ATD-20260327-D83E3FDD. Status atual: queued. A equipe humana podera continuar esse atendimento no portal operacional.
- CrewAI answer: Sua solicitacao ja estava registrada na fila de atendimento. Protocolo: ATD-20260327-D83E3FDD. Status atual: queued.

### mas eu cheguei agora

- Slice: `support`
- Category: `threaded_real_transcript`
- Thread: `real_support_handoff_repair_1649845499` turn `2`
- Note: repair turn after existing support handoff
- Baseline: status 200, latency 175.3ms, keyword pass `True`, quality `100`
- CrewAI: status 200, latency 36.9ms, keyword pass `True`, quality `100`
- Baseline quality signals: repair_ack=True, followup_adaptation=True, personalization=True
- CrewAI quality signals: repair_ack=True, followup_adaptation=True, personalization=True
- Baseline answer: Sem problema, vamos comecar do zero entao e abrir um novo atendimento a partir daqui. Se voce quiser atendimento humano por aqui, me diga em uma frase curta qual e o assunto como financeiro, secretaria, matricula ou direcao, e eu sigo desse ponto.
- CrewAI answer: Sem problema, vamos comecar do zero entao e abrir um novo atendimento a partir daqui. Se voce quiser atendimento humano por aqui, me diga em uma frase curta qual e o assunto como financeiro, secretaria, matricula ou direcao, e eu sigo desse ponto.

### quero falar com um humano sobre a secretaria

- Slice: `support`
- Category: `threaded_real_transcript`
- Thread: `real_support_secretaria_handoff_555001` turn `1`
- Baseline: status 200, latency 152.2ms, keyword pass `True`, quality `100`
- CrewAI: status 200, latency 60.3ms, keyword pass `True`, quality `100`
- Baseline quality signals: repair_ack=None, followup_adaptation=None, personalization=None
- CrewAI quality signals: repair_ack=None, followup_adaptation=None, personalization=None
- Baseline answer: Encaminhei sua solicitacao para a fila de secretaria. Protocolo: ATD-20260327-6447DE40. Status atual: queued. A equipe humana podera continuar esse atendimento no portal operacional.
- CrewAI answer: Sua solicitacao ja estava registrada na fila de secretaria. Protocolo: ATD-20260327-6447DE40. Status atual: queued.

### qual o protocolo?

- Slice: `support`
- Category: `threaded_real_transcript`
- Thread: `real_support_secretaria_handoff_555001` turn `2`
- Baseline: status 200, latency 1723.7ms, keyword pass `True`, quality `100`
- CrewAI: status 200, latency 34.0ms, keyword pass `True`, quality `100`
- Baseline quality signals: repair_ack=None, followup_adaptation=None, personalization=None
- CrewAI quality signals: repair_ack=None, followup_adaptation=None, personalization=None
- Baseline answer: O protocolo do seu atendimento é ATD-20260327-6447DE40. Se precisar, posso verificar o status atual ou resumir o que já foi registrado até agora.
- CrewAI answer: O protocolo do seu atendimento e ATD-20260327-6447DE40. Se quiser, posso verificar o status atual ou te dar um resumo do que ja foi registrado.
