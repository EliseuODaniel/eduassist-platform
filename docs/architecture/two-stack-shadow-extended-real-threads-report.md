# Two-Stack Shadow Comparison Report

## Summary

- Total prompts: 22
- `protected`: baseline ok 13/13, CrewAI ok 13/13, baseline keyword pass 13/13, CrewAI keyword pass 13/13, quality 100.0 vs 100.0, latency 156.5ms vs 133.6ms
- `public`: baseline ok 9/9, CrewAI ok 9/9, baseline keyword pass 9/9, CrewAI keyword pass 9/9, quality 100.0 vs 100.0, latency 3818.3ms vs 26.1ms

## By Category

- `threaded_real_transcript`: baseline ok 22/22, CrewAI ok 22/22, baseline keyword pass 22/22, CrewAI keyword pass 22/22, quality 100.0 vs 100.0

## Error Types

- `baseline`: nenhum
- `crewai`: nenhum

## By Thread

- `real_guardian_identity_and_student_scope` (protected/threaded_real_transcript): baseline keyword pass 9/9, CrewAI keyword pass 9/9, quality 100.0 vs 100.0
- `real_document_channels_conflict` (protected/threaded_real_transcript): baseline keyword pass 6/6, CrewAI keyword pass 6/6, quality 100.0 vs 100.0
- `real_guardian_grades_and_finance_555001` (protected/threaded_real_transcript): baseline keyword pass 3/3, CrewAI keyword pass 3/3, quality 100.0 vs 100.0
- `real_public_catalog_777001` (public/threaded_real_transcript): baseline keyword pass 4/4, CrewAI keyword pass 4/4, quality 100.0 vs 100.0

## Prompt Results

### estou logado como?

- Slice: `protected`
- Category: `threaded_real_transcript`
- Thread: `real_guardian_identity_and_student_scope` turn `1`
- Baseline: status 200, latency 153.7ms, keyword pass `True`, quality `100`
- CrewAI: status 200, latency 39.9ms, keyword pass `True`, quality `100`
- Baseline answer: Voce esta falando aqui como Maria Oliveira, no perfil de responsavel. Sua conta esta vinculada a Lucas Oliveira e Ana Oliveira. Por aqui eu consigo consultar notas, faltas, proximas provas, matricula, financeiro, boletos, dentro das permissoes dessa vinculacao.
- CrewAI answer: Voce esta autenticado aqui como Maria Oliveira. Sua conta esta vinculada a Lucas Oliveira, Ana Oliveira e pode consultar notas, frequencia, avaliacoes, documentacao e financeiro desses alunos.

### quais notas do meu filho lucas

- Slice: `protected`
- Category: `threaded_real_transcript`
- Thread: `real_guardian_identity_and_student_scope` turn `2`
- Baseline: status 200, latency 188.5ms, keyword pass `True`, quality `100`
- CrewAI: status 200, latency 226.1ms, keyword pass `True`, quality `100`
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
- Baseline: status 200, latency 133.2ms, keyword pass `True`, quality `100`
- CrewAI: status 200, latency 19.9ms, keyword pass `True`, quality `100`
- Baseline answer: Hoje eu nao encontrei Joao entre os alunos vinculados a esta conta. No momento, os alunos que aparecem aqui sao: Lucas Oliveira (MAT-2026-001), Ana Oliveira (MAT-2026-002). Se quiser, me diga qual deles voce quer consultar.
- CrewAI answer: Hoje eu nao encontrei Joao entre os alunos vinculados a esta conta. No momento, os alunos que aparecem aqui sao: Lucas Oliveira, Ana Oliveira. Se quiser, me diga qual deles voce quer consultar.

### qual situação de documentação do lucas?

- Slice: `protected`
- Category: `threaded_real_transcript`
- Thread: `real_guardian_identity_and_student_scope` turn `4`
- Baseline: status 200, latency 160.0ms, keyword pass `True`, quality `100`
- CrewAI: status 200, latency 236.0ms, keyword pass `True`, quality `100`
- Baseline answer: Situacao documental de Lucas Oliveira hoje: regular.
- CrewAI answer: A situacao documental de Lucas Oliveira hoje esta regular e completa.

### lucas oliveira, o luquinha

- Slice: `protected`
- Category: `threaded_real_transcript`
- Thread: `real_guardian_identity_and_student_scope` turn `5`
- Note: real transcript disambiguation turn
- Baseline: status 200, latency 133.6ms, keyword pass `True`, quality `100`
- CrewAI: status 200, latency 20.0ms, keyword pass `True`, quality `100`
- Baseline answer: Perfeito, seguimos com Lucas Oliveira. Posso te ajudar com notas, faltas, proximas provas, matricula, financeiro, boletos. Se quiser, ja me diga o que voce quer ver primeiro.
- CrewAI answer: Perfeito, seguimos com Lucas Oliveira. Posso te ajudar com notas, frequencia, faltas, proximas provas, documentacao, matricula e financeiro.

### quais próximas provas do lucas

- Slice: `protected`
- Category: `threaded_real_transcript`
- Thread: `real_guardian_identity_and_student_scope` turn `6`
- Baseline: status 200, latency 228.3ms, keyword pass `True`, quality `100`
- CrewAI: status 200, latency 221.6ms, keyword pass `True`, quality `100`
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
- Baseline: status 200, latency 164.7ms, keyword pass `True`, quality `100`
- CrewAI: status 200, latency 227.8ms, keyword pass `True`, quality `100`
- Baseline answer: A matricula de Lucas Oliveira e MAT-2026-001. Turma atual: 1o Ano A.
- CrewAI answer: A matricula de Lucas Oliveira e MAT-2026-001.

### e como estão as faltas do lucas

- Slice: `protected`
- Category: `threaded_real_transcript`
- Thread: `real_guardian_identity_and_student_scope` turn `8`
- Note: real transcript regression: previously echoed enrollment instead of attendance
- Baseline: status 200, latency 161.3ms, keyword pass `True`, quality `100`
- CrewAI: status 200, latency 239.4ms, keyword pass `True`, quality `100`
- Baseline answer: No recorte de faltas de Lucas Oliveira, eu encontrei 6 falta(s) e 7 atraso(s).
- CrewAI answer: Lucas Oliveira tem 3 falta(s) e 3 registro(s) de atraso neste recorte.

### E a frequencia do Lucas?

- Slice: `protected`
- Category: `threaded_real_transcript`
- Thread: `real_guardian_identity_and_student_scope` turn `9`
- Note: real transcript regression: previously treated frequencia as student name
- Baseline: status 200, latency 198.8ms, keyword pass `True`, quality `100`
- CrewAI: status 200, latency 226.2ms, keyword pass `True`, quality `100`
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
- Baseline: status 200, latency 170.2ms, keyword pass `True`, quality `100`
- CrewAI: status 200, latency 227.9ms, keyword pass `True`, quality `100`
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
- Baseline: status 200, latency 1567.9ms, keyword pass `True`, quality `100`
- CrewAI: status 200, latency 27.8ms, keyword pass `True`, quality `100`
- Baseline answer: Hoje a escola nao utiliza fax para envio de documentos. Para isso, use portal institucional, email da secretaria, secretaria presencial.
- CrewAI answer: Hoje a escola nao utiliza fax para envio de documentos. Para isso, use portal institucional, email da secretaria ou secretaria presencial.

### qual o número do fax?

- Slice: `public`
- Category: `threaded_real_transcript`
- Thread: `real_document_channels_conflict` turn `3`
- Baseline: status 200, latency 3602.0ms, keyword pass `True`, quality `100`
- CrewAI: status 200, latency 28.0ms, keyword pass `True`, quality `100`
- Baseline answer: Hoje a escola não utiliza fax. Para falar conosco por telefone, o número da secretaria é (11) 3333-4200.
- CrewAI answer: Hoje nao existe numero de fax publicado, porque a escola nao utiliza fax institucional.

### mas antes você respondeu que eu podia enviar por fax

- Slice: `public`
- Category: `threaded_real_transcript`
- Thread: `real_document_channels_conflict` turn `4`
- Note: repair turn from real transcript
- Baseline: status 200, latency 3506.3ms, keyword pass `True`, quality `100`
- CrewAI: status 200, latency 24.6ms, keyword pass `True`, quality `100`
- Baseline answer: Peço desculpas pela confusão! O Colégio Horizonte não utiliza fax atualmente. Para enviar documentos, você pode usar nosso portal institucional, o e-mail da secretaria ou ir diretamente à secretaria presencial.
- CrewAI answer: Voce esta certo em cobrar essa correcao. Corrigindo: hoje a escola nao utiliza fax institucional. Para documentos, use portal institucional, email da secretaria ou secretaria presencial.

### e se eu mandar por telegrama, serve?

- Slice: `public`
- Category: `threaded_real_transcript`
- Thread: `real_document_channels_conflict` turn `5`
- Note: real transcript regression: previously repeated generic digital-channel copy
- Baseline: status 200, latency 1652.0ms, keyword pass `True`, quality `100`
- CrewAI: status 200, latency 25.5ms, keyword pass `True`, quality `100`
- Baseline answer: Hoje a escola nao publica telegrama como canal valido para documentos. Para isso, use portal institucional, email da secretaria, secretaria presencial.
- CrewAI answer: Hoje a escola nao publica telegrama como canal valido. Para documentos, use portal institucional, email da secretaria ou secretaria presencial.

### qual sua caixa postal?

- Slice: `public`
- Category: `threaded_real_transcript`
- Thread: `real_document_channels_conflict` turn `6`
- Baseline: status 200, latency 1618.0ms, keyword pass `True`, quality `100`
- CrewAI: status 200, latency 23.7ms, keyword pass `True`, quality `100`
- Baseline answer: Hoje a escola nao trabalha com caixa postal para esse tipo de envio. Para documentos, use portal institucional, email da secretaria, secretaria presencial.
- CrewAI answer: Hoje a escola nao trabalha com caixa postal para esse tipo de envio. Para documentos, use portal institucional, email da secretaria ou secretaria presencial.

### quero ver minhas notas

- Slice: `protected`
- Category: `threaded_real_transcript`
- Thread: `real_guardian_grades_and_finance_555001` turn `1`
- Note: real transcript prompt under current state drift: this chat is no longer linked in the current environment
- Baseline: status 200, latency 116.4ms, keyword pass `True`, quality `100`
- CrewAI: status 200, latency 17.6ms, keyword pass `True`, quality `100`
- Baseline answer: Essa consulta depende de autenticacao e vinculo da sua conta no Telegram. Use o portal da escola para gerar o codigo de vinculacao e depois envie o comando `/start link_<codigo>` ao bot.
- CrewAI answer: Essa consulta depende de autenticacao e vinculo da sua conta no Telegram. Use o portal da escola para gerar o codigo de vinculacao e depois envie o comando /start link_<codigo> ao bot.

### quero ver as notas do Lucas Oliveira

- Slice: `protected`
- Category: `threaded_real_transcript`
- Thread: `real_guardian_grades_and_finance_555001` turn `2`
- Note: real transcript prompt under current state drift: this chat is no longer linked in the current environment
- Baseline: status 200, latency 114.5ms, keyword pass `True`, quality `100`
- CrewAI: status 200, latency 17.3ms, keyword pass `True`, quality `100`
- Baseline answer: Essa consulta depende de autenticacao e vinculo da sua conta no Telegram. Use o portal da escola para gerar o codigo de vinculacao e depois envie o comando `/start link_<codigo>` ao bot.
- CrewAI answer: Essa consulta depende de autenticacao e vinculo da sua conta no Telegram. Use o portal da escola para gerar o codigo de vinculacao e depois envie o comando /start link_<codigo> ao bot.

### quero ver o financeiro da Ana Oliveira

- Slice: `protected`
- Category: `threaded_real_transcript`
- Thread: `real_guardian_grades_and_finance_555001` turn `3`
- Note: real transcript prompt under current state drift: this chat is no longer linked in the current environment
- Baseline: status 200, latency 111.8ms, keyword pass `True`, quality `100`
- CrewAI: status 200, latency 16.9ms, keyword pass `True`, quality `100`
- Baseline answer: Essa consulta depende de autenticacao e vinculo da sua conta no Telegram. Use o portal da escola para gerar o codigo de vinculacao e depois envie o comando `/start link_<codigo>` ao bot.
- CrewAI answer: Essa consulta depende de autenticacao e vinculo da sua conta no Telegram. Use o portal da escola para gerar o codigo de vinculacao e depois envie o comando /start link_<codigo> ao bot.

### quais documentos sao exigidos para matricula?

- Slice: `public`
- Category: `threaded_real_transcript`
- Thread: `real_public_catalog_777001` turn `1`
- Baseline: status 200, latency 5369.9ms, keyword pass `True`, quality `100`
- CrewAI: status 200, latency 27.6ms, keyword pass `True`, quality `100`
- Baseline answer: Para a matrícula, precisamos do formulário cadastral preenchido, documento de identificação e CPF do aluno (se tiver), histórico escolar e comprovante de residência. Também é necessário o documento de identificação do responsável legal. Se precisar, posso te explicar as etapas da matrícula ou como enviar esses documentos.
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
- Baseline: status 200, latency 6252.1ms, keyword pass `True`, quality `100`
- CrewAI: status 200, latency 24.8ms, keyword pass `True`, quality `100`
- Baseline answer: A nossa Biblioteca Aurora está aberta de segunda a sexta-feira, das 7h30 às 18h.
- CrewAI answer: A Biblioteca Aurora atende ao publico de segunda a sexta, das 7h30 as 18h00.

### qual o telefone e o fax?

- Slice: `public`
- Category: `threaded_real_transcript`
- Thread: `real_public_catalog_777001` turn `3`
- Baseline: status 200, latency 3647.5ms, keyword pass `True`, quality `100`
- CrewAI: status 200, latency 26.8ms, keyword pass `True`, quality `100`
- Baseline answer: O Colégio Horizonte não utiliza fax atualmente. Para falar conosco por telefone, o número da secretaria é (11) 3333-4200.
- CrewAI answer: Secretaria (telefone): (11) 3333-4200 Hoje a escola nao utiliza fax institucional.

### qual a mensalidade do ensino medio?

- Slice: `public`
- Category: `threaded_real_transcript`
- Thread: `real_public_catalog_777001` turn `4`
- Baseline: status 200, latency 7148.9ms, keyword pass `True`, quality `100`
- CrewAI: status 200, latency 25.8ms, keyword pass `True`, quality `100`
- Baseline answer: Para o Ensino Médio no turno da manhã, a mensalidade de referência para 2026 é de R$ 1.450,00 e a taxa de matrícula é de R$ 350,00. Temos políticas comerciais para irmãos e para pagamento pontual. Se precisar, posso te dar mais detalhes sobre bolsas, descontos e os canais para matrícula.
- CrewAI answer: A mensalidade de referencia para Ensino Medio e R$ 1450.00, com taxa de matricula de R$ 350.00.
