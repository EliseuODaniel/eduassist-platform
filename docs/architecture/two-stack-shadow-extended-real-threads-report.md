# Two-Stack Shadow Comparison Report

## Summary

- Total prompts: 22
- `protected`: baseline ok 13/13, CrewAI ok 13/13, baseline keyword pass 13/13, CrewAI keyword pass 13/13, quality 97.7 vs 98.5, latency 161.4ms vs 141.3ms
- `public`: baseline ok 9/9, CrewAI ok 9/9, baseline keyword pass 9/9, CrewAI keyword pass 9/9, quality 100.0 vs 95.8, latency 3900.8ms vs 28.2ms

## By Category

- `threaded_real_transcript`: baseline ok 22/22, CrewAI ok 22/22, baseline keyword pass 22/22, CrewAI keyword pass 22/22, quality 98.6 vs 97.4

## Error Types

- `baseline`: repetitive_reply=3
- `crewai`: repair_miss=1, repetitive_reply=4

## By Thread

- `real_guardian_identity_and_student_scope` (protected/threaded_real_transcript): baseline keyword pass 9/9, CrewAI keyword pass 9/9, quality 98.9 vs 100.0
- `real_document_channels_conflict` (protected/threaded_real_transcript): baseline keyword pass 6/6, CrewAI keyword pass 6/6, quality 100.0 vs 93.7
- `real_guardian_grades_and_finance_555001` (protected/threaded_real_transcript): baseline keyword pass 3/3, CrewAI keyword pass 3/3, quality 93.3 vs 93.3
- `real_public_catalog_777001` (public/threaded_real_transcript): baseline keyword pass 4/4, CrewAI keyword pass 4/4, quality 100.0 vs 100.0

## Prompt Results

### estou logado como?

- Slice: `protected`
- Category: `threaded_real_transcript`
- Thread: `real_guardian_identity_and_student_scope` turn `1`
- Baseline: status 200, latency 141.0ms, keyword pass `True`, quality `100`
- CrewAI: status 200, latency 36.9ms, keyword pass `True`, quality `100`
- Baseline answer: Voce esta falando aqui como Maria Oliveira, no perfil de responsavel. Sua conta esta vinculada a Lucas Oliveira e Ana Oliveira. Por aqui eu consigo consultar notas, faltas, proximas provas, matricula, financeiro, boletos, dentro das permissoes dessa vinculacao.
- CrewAI answer: Voce esta autenticado aqui como Maria Oliveira. Sua conta esta vinculada a Lucas Oliveira, Ana Oliveira e pode consultar notas, frequencia, avaliacoes, documentacao e financeiro desses alunos.

### quais notas do meu filho lucas

- Slice: `protected`
- Category: `threaded_real_transcript`
- Thread: `real_guardian_identity_and_student_scope` turn `2`
- Baseline: status 200, latency 178.4ms, keyword pass `True`, quality `100`
- CrewAI: status 200, latency 233.8ms, keyword pass `True`, quality `100`
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
- Baseline: status 200, latency 140.7ms, keyword pass `True`, quality `100`
- CrewAI: status 200, latency 20.9ms, keyword pass `True`, quality `100`
- Baseline answer: Hoje eu nao encontrei Joao entre os alunos vinculados a esta conta. No momento, os alunos que aparecem aqui sao: Lucas Oliveira (MAT-2026-001), Ana Oliveira (MAT-2026-002). Se quiser, me diga qual deles voce quer consultar.
- CrewAI answer: Hoje eu nao encontrei Joao entre os alunos vinculados a esta conta. No momento, os alunos que aparecem aqui sao: Lucas Oliveira, Ana Oliveira. Se quiser, me diga qual deles voce quer consultar.

### qual situação de documentação do lucas?

- Slice: `protected`
- Category: `threaded_real_transcript`
- Thread: `real_guardian_identity_and_student_scope` turn `4`
- Baseline: status 200, latency 172.9ms, keyword pass `True`, quality `100`
- CrewAI: status 200, latency 248.1ms, keyword pass `True`, quality `100`
- Baseline answer: Situacao documental de Lucas Oliveira hoje: regular.
- CrewAI answer: A situacao documental de Lucas Oliveira hoje esta regular e completa.

### lucas oliveira, o luquinha

- Slice: `protected`
- Category: `threaded_real_transcript`
- Thread: `real_guardian_identity_and_student_scope` turn `5`
- Note: real transcript disambiguation turn
- Baseline: status 200, latency 139.9ms, keyword pass `True`, quality `100`
- CrewAI: status 200, latency 19.9ms, keyword pass `True`, quality `100`
- Baseline answer: Perfeito, seguimos com Lucas Oliveira. Posso te ajudar com notas, faltas, proximas provas, matricula, financeiro, boletos. Se quiser, ja me diga o que voce quer ver primeiro.
- CrewAI answer: Perfeito, seguimos com Lucas Oliveira. Posso te ajudar com notas, frequencia, faltas, proximas provas, documentacao, matricula e financeiro.

### quais próximas provas do lucas

- Slice: `protected`
- Category: `threaded_real_transcript`
- Thread: `real_guardian_identity_and_student_scope` turn `6`
- Baseline: status 200, latency 224.4ms, keyword pass `True`, quality `100`
- CrewAI: status 200, latency 237.2ms, keyword pass `True`, quality `100`
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
- Baseline: status 200, latency 172.9ms, keyword pass `True`, quality `100`
- CrewAI: status 200, latency 247.4ms, keyword pass `True`, quality `100`
- Baseline answer: A matricula de Lucas Oliveira e MAT-2026-001. Turma atual: 1o Ano A.
- CrewAI answer: A matricula de Lucas Oliveira e MAT-2026-001.

### e como estão as faltas do lucas

- Slice: `protected`
- Category: `threaded_real_transcript`
- Thread: `real_guardian_identity_and_student_scope` turn `8`
- Note: real transcript regression: previously echoed enrollment instead of attendance
- Baseline: status 200, latency 198.8ms, keyword pass `True`, quality `100`
- CrewAI: status 200, latency 269.1ms, keyword pass `True`, quality `100`
- Baseline answer: Frequencia de Lucas Oliveira:
- Biologia: 2 presencas, 0 atrasos, 1 faltas (50 min)
- Educacao Fisica: 1 presencas, 0 atrasos, 1 faltas (50 min)
- Filosofia: 1 presencas, 1 atrasos, 0 faltas (10 min)
- Fisica: 1 presencas, 1 atrasos, 0 faltas (10 min)
- CrewAI answer: Lucas Oliveira tem 3 falta(s) e 3 registro(s) de atraso neste recorte.

### E a frequencia do Lucas?

- Slice: `protected`
- Category: `threaded_real_transcript`
- Thread: `real_guardian_identity_and_student_scope` turn `9`
- Note: real transcript regression: previously treated frequencia as student name
- Baseline: status 200, latency 189.1ms, keyword pass `True`, quality `90`
- CrewAI: status 200, latency 232.1ms, keyword pass `True`, quality `100`
- Baseline errors: repetitive_reply
- Baseline answer: Frequencia de Lucas Oliveira:
- Biologia: 2 presencas, 0 atrasos, 1 faltas (50 min)
- Educacao Fisica: 1 presencas, 0 atrasos, 1 faltas (50 min)
- Filosofia: 1 presencas, 1 atrasos, 0 faltas (10 min)
- Fisica: 1 presencas, 1 atrasos, 0 faltas (10 min)
- CrewAI answer: Na frequencia de Lucas Oliveira, eu encontrei 12 registro(s) neste recorte: 6 presenca(s), 3 falta(s) e 3 atraso(s).

### quais documentos faltam pra ana

- Slice: `protected`
- Category: `threaded_real_transcript`
- Thread: `real_document_channels_conflict` turn `1`
- Note: real transcript regression: previously answered the guardian admin profile instead of Ana
- Baseline: status 200, latency 181.9ms, keyword pass `True`, quality `100`
- CrewAI: status 200, latency 238.1ms, keyword pass `True`, quality `100`
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
- Baseline: status 200, latency 1576.5ms, keyword pass `True`, quality `100`
- CrewAI: status 200, latency 26.2ms, keyword pass `True`, quality `100`
- Baseline answer: Hoje a escola nao utiliza fax para envio de documentos. Para isso, use portal institucional, email da secretaria, secretaria presencial.
- CrewAI answer: Hoje a escola nao utiliza fax institucional.

### qual o número do fax?

- Slice: `public`
- Category: `threaded_real_transcript`
- Thread: `real_document_channels_conflict` turn `3`
- Baseline: status 200, latency 1682.5ms, keyword pass `True`, quality `100`
- CrewAI: status 200, latency 41.6ms, keyword pass `True`, quality `90`
- CrewAI errors: repetitive_reply
- Baseline answer: Hoje a escola não utiliza fax. Para entrar em contato por telefone, o número da secretaria é (11) 3333-4200.
- CrewAI answer: Hoje a escola nao utiliza fax institucional.

### mas antes você respondeu que eu podia enviar por fax

- Slice: `public`
- Category: `threaded_real_transcript`
- Thread: `real_document_channels_conflict` turn `4`
- Note: repair turn from real transcript
- Baseline: status 200, latency 3580.3ms, keyword pass `True`, quality `100`
- CrewAI: status 200, latency 26.6ms, keyword pass `True`, quality `72`
- CrewAI errors: repair_miss, repetitive_reply
- Baseline answer: Peço desculpas pela confusão! O Colégio Horizonte não utiliza fax atualmente. Para enviar documentos, você pode usar nosso portal institucional, o e-mail da secretaria ou ir diretamente à secretaria presencial.
- CrewAI answer: Hoje a escola nao utiliza fax institucional.

### e se eu mandar por telegrama, serve?

- Slice: `public`
- Category: `threaded_real_transcript`
- Thread: `real_document_channels_conflict` turn `5`
- Note: real transcript regression: previously repeated generic digital-channel copy
- Baseline: status 200, latency 1627.4ms, keyword pass `True`, quality `100`
- CrewAI: status 200, latency 26.3ms, keyword pass `True`, quality `100`
- Baseline answer: Hoje a escola nao publica telegrama como canal valido para documentos. Para isso, use portal institucional, email da secretaria, secretaria presencial.
- CrewAI answer: Hoje a escola nao publica telegrama como canal valido. Para documentos, use portal institucional, email da secretaria ou secretaria presencial.

### qual sua caixa postal?

- Slice: `public`
- Category: `threaded_real_transcript`
- Thread: `real_document_channels_conflict` turn `6`
- Baseline: status 200, latency 3267.1ms, keyword pass `True`, quality `100`
- CrewAI: status 200, latency 24.1ms, keyword pass `True`, quality `100`
- Baseline answer: Hoje a escola não utiliza caixa postal para o envio de documentos. Para isso, você pode usar nosso portal institucional, o e-mail da secretaria ou ir diretamente à secretaria presencial.
- CrewAI answer: Hoje a escola nao trabalha com caixa postal para esse tipo de envio. Para documentos, use portal institucional, email da secretaria ou secretaria presencial.

### quero ver minhas notas

- Slice: `protected`
- Category: `threaded_real_transcript`
- Thread: `real_guardian_grades_and_finance_555001` turn `1`
- Note: real transcript prompt under current state drift: this chat is no longer linked in the current environment
- Baseline: status 200, latency 119.6ms, keyword pass `True`, quality `100`
- CrewAI: status 200, latency 17.1ms, keyword pass `True`, quality `100`
- Baseline answer: Essa consulta depende de autenticacao e vinculo da sua conta no Telegram. Use o portal da escola para gerar o codigo de vinculacao e depois envie o comando `/start link_<codigo>` ao bot.
- CrewAI answer: Essa consulta depende de autenticacao e vinculo da sua conta no Telegram. Use o portal da escola para gerar o codigo de vinculacao e depois envie o comando /start link_<codigo> ao bot.

### quero ver as notas do Lucas Oliveira

- Slice: `protected`
- Category: `threaded_real_transcript`
- Thread: `real_guardian_grades_and_finance_555001` turn `2`
- Note: real transcript prompt under current state drift: this chat is no longer linked in the current environment
- Baseline: status 200, latency 118.5ms, keyword pass `True`, quality `90`
- CrewAI: status 200, latency 18.2ms, keyword pass `True`, quality `90`
- Baseline errors: repetitive_reply
- CrewAI errors: repetitive_reply
- Baseline answer: Essa consulta depende de autenticacao e vinculo da sua conta no Telegram. Use o portal da escola para gerar o codigo de vinculacao e depois envie o comando `/start link_<codigo>` ao bot.
- CrewAI answer: Essa consulta depende de autenticacao e vinculo da sua conta no Telegram. Use o portal da escola para gerar o codigo de vinculacao e depois envie o comando /start link_<codigo> ao bot.

### quero ver o financeiro da Ana Oliveira

- Slice: `protected`
- Category: `threaded_real_transcript`
- Thread: `real_guardian_grades_and_finance_555001` turn `3`
- Note: real transcript prompt under current state drift: this chat is no longer linked in the current environment
- Baseline: status 200, latency 120.6ms, keyword pass `True`, quality `90`
- CrewAI: status 200, latency 17.5ms, keyword pass `True`, quality `90`
- Baseline errors: repetitive_reply
- CrewAI errors: repetitive_reply
- Baseline answer: Essa consulta depende de autenticacao e vinculo da sua conta no Telegram. Use o portal da escola para gerar o codigo de vinculacao e depois envie o comando `/start link_<codigo>` ao bot.
- CrewAI answer: Essa consulta depende de autenticacao e vinculo da sua conta no Telegram. Use o portal da escola para gerar o codigo de vinculacao e depois envie o comando /start link_<codigo> ao bot.

### quais documentos sao exigidos para matricula?

- Slice: `public`
- Category: `threaded_real_transcript`
- Thread: `real_public_catalog_777001` turn `1`
- Baseline: status 200, latency 5259.8ms, keyword pass `True`, quality `100`
- CrewAI: status 200, latency 30.3ms, keyword pass `True`, quality `100`
- Baseline answer: Olá! Para a matrícula no Colégio Horizonte, os documentos que precisamos são: o formulário cadastral preenchido, o documento de identificação e CPF do aluno (se tiver), o histórico escolar e um comprovante de residência atualizado. Também pedimos o documento de identificação do responsável legal. Se precisar, posso te explicar as etapas da matrícula ou como enviar esses documentos.
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
- Baseline: status 200, latency 7074.7ms, keyword pass `True`, quality `100`
- CrewAI: status 200, latency 26.0ms, keyword pass `True`, quality `100`
- Baseline answer: Que bom que você perguntou! A nossa biblioteca se chama Biblioteca Aurora e está aberta de segunda a sexta-feira, das 7h30 às 18h00, para todos os alunos.
- CrewAI answer: A Biblioteca Aurora atende ao publico de segunda a sexta, das 7h30 as 18h00.

### qual o telefone e o fax?

- Slice: `public`
- Category: `threaded_real_transcript`
- Thread: `real_public_catalog_777001` turn `3`
- Baseline: status 200, latency 3653.6ms, keyword pass `True`, quality `100`
- CrewAI: status 200, latency 28.0ms, keyword pass `True`, quality `100`
- Baseline answer: Olá! No Colégio Horizonte, não utilizamos mais o fax. Para falar conosco por telefone, o número da secretaria é (11) 3333-4200.
- CrewAI answer: Secretaria (telefone): (11) 3333-4200 Hoje a escola nao utiliza fax institucional.

### qual a mensalidade do ensino medio?

- Slice: `public`
- Category: `threaded_real_transcript`
- Thread: `real_public_catalog_777001` turn `4`
- Baseline: status 200, latency 7385.4ms, keyword pass `True`, quality `100`
- CrewAI: status 200, latency 25.0ms, keyword pass `True`, quality `100`
- Baseline answer: Olá! A mensalidade de referência para o Ensino Médio (turno da manhã) em 2026 é de R$ 1.450,00, e a taxa de matrícula é de R$ 350,00. Temos condições especiais para irmãos e para quem paga em dia. Se precisar de mais informações sobre bolsas ou o processo de matrícula, é só me dizer!
- CrewAI answer: A mensalidade de referencia para Ensino Medio e R$ 1450.00, com taxa de matricula de R$ 350.00.
