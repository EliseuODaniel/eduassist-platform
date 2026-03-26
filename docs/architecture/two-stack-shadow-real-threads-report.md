# Two-Stack Shadow Comparison Report

## Summary

- Total prompts: 15
- `protected`: baseline ok 10/10, CrewAI ok 10/10, baseline keyword pass 10/10, CrewAI keyword pass 8/10, quality 99.0 vs 95.0, latency 178.1ms vs 109.7ms
- `public`: baseline ok 5/5, CrewAI ok 5/5, baseline keyword pass 5/5, CrewAI keyword pass 5/5, quality 100.0 vs 96.0, latency 5227.9ms vs 26.4ms

## By Category

- `threaded_real_transcript`: baseline ok 15/15, CrewAI ok 15/15, baseline keyword pass 15/15, CrewAI keyword pass 13/15, quality 99.3 vs 95.3

## Error Types

- `baseline`: repetitive_reply=1
- `crewai`: missing_expected_keyword=2, repetitive_reply=3

## By Thread

- `real_guardian_identity_and_student_scope` (protected/threaded_real_transcript): baseline keyword pass 9/9, CrewAI keyword pass 7/9, quality 98.9 vs 94.4
- `real_document_channels_conflict` (protected/threaded_real_transcript): baseline keyword pass 6/6, CrewAI keyword pass 6/6, quality 100.0 vs 96.7

## Prompt Results

### estou logado como?

- Slice: `protected`
- Category: `threaded_real_transcript`
- Thread: `real_guardian_identity_and_student_scope` turn `1`
- Baseline: status 200, latency 156.2ms, keyword pass `True`, quality `100`
- CrewAI: status 200, latency 24.2ms, keyword pass `True`, quality `100`
- Baseline answer: Voce esta falando aqui como Maria Oliveira, no perfil de responsavel. Sua conta esta vinculada a Lucas Oliveira e Ana Oliveira. Por aqui eu consigo consultar notas, faltas, proximas provas, matricula, financeiro, boletos, dentro das permissoes dessa vinculacao.
- CrewAI answer: Voce esta autenticado aqui como Maria Oliveira. Sua conta esta vinculada a Lucas Oliveira, Ana Oliveira e pode consultar notas, frequencia, avaliacoes, documentacao e financeiro desses alunos.

### quais notas do meu filho lucas

- Slice: `protected`
- Category: `threaded_real_transcript`
- Thread: `real_guardian_identity_and_student_scope` turn `2`
- Baseline: status 200, latency 186.3ms, keyword pass `True`, quality `100`
- CrewAI: status 200, latency 20.1ms, keyword pass `True`, quality `100`
- Baseline answer: Notas de Lucas Oliveira:
- Biologia - Avaliacao B1: 8.40/10.00
- Biologia - Avaliacao 2026-B1 - BIO: 7.00/10.00
- Biologia - Trabalho B1: 8.10/10.00
- Biologia - Avaliacao B2: 8.60/10.00
- CrewAI answer: Sua conta esta vinculada a Lucas Oliveira, Ana Oliveira.

### quais notas do meu filho joão

- Slice: `protected`
- Category: `threaded_real_transcript`
- Thread: `real_guardian_identity_and_student_scope` turn `3`
- Baseline: status 200, latency 145.6ms, keyword pass `True`, quality `100`
- CrewAI: status 200, latency 20.1ms, keyword pass `False`, quality `70`
- CrewAI errors: missing_expected_keyword, repetitive_reply
- Baseline answer: Hoje eu nao encontrei Joao entre os alunos vinculados a esta conta. No momento, os alunos que aparecem aqui sao: Lucas Oliveira (MAT-2026-001), Ana Oliveira (MAT-2026-002). Se quiser, me diga qual deles voce quer consultar.
- CrewAI answer: Sua conta esta vinculada a Lucas Oliveira, Ana Oliveira.

### qual situação de documentação do lucas?

- Slice: `protected`
- Category: `threaded_real_transcript`
- Thread: `real_guardian_identity_and_student_scope` turn `4`
- Baseline: status 200, latency 167.2ms, keyword pass `True`, quality `100`
- CrewAI: status 200, latency 228.6ms, keyword pass `True`, quality `100`
- Baseline answer: Situacao documental de Lucas Oliveira hoje: regular.
- CrewAI answer: A situacao documental de Lucas Oliveira hoje esta regular e completa.

### lucas oliveira, o luquinha

- Slice: `protected`
- Category: `threaded_real_transcript`
- Thread: `real_guardian_identity_and_student_scope` turn `5`
- Note: real transcript disambiguation turn
- Baseline: status 200, latency 145.9ms, keyword pass `True`, quality `100`
- CrewAI: status 200, latency 20.0ms, keyword pass `True`, quality `100`
- Baseline answer: Perfeito, seguimos com Lucas Oliveira. Posso te ajudar com notas, faltas, proximas provas, matricula, financeiro, boletos. Se quiser, ja me diga o que voce quer ver primeiro.
- CrewAI answer: Perfeito, seguimos com Lucas Oliveira. Posso te ajudar com notas, frequencia, faltas, proximas provas, documentacao, matricula e financeiro.

### quais próximas provas do lucas

- Slice: `protected`
- Category: `threaded_real_transcript`
- Thread: `real_guardian_identity_and_student_scope` turn `6`
- Baseline: status 200, latency 229.5ms, keyword pass `True`, quality `100`
- CrewAI: status 200, latency 251.5ms, keyword pass `True`, quality `100`
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
- Baseline: status 200, latency 182.9ms, keyword pass `True`, quality `100`
- CrewAI: status 200, latency 21.1ms, keyword pass `False`, quality `80`
- CrewAI errors: missing_expected_keyword
- Baseline answer: A matricula de Lucas Oliveira e MAT-2026-001. Turma atual: 1o Ano A.
- CrewAI answer: Perfeito, seguimos com Lucas Oliveira. Posso te ajudar com notas, frequencia, faltas, proximas provas, documentacao, matricula e financeiro.

### e como estão as faltas do lucas

- Slice: `protected`
- Category: `threaded_real_transcript`
- Thread: `real_guardian_identity_and_student_scope` turn `8`
- Note: real transcript regression: previously echoed enrollment instead of attendance
- Baseline: status 200, latency 172.5ms, keyword pass `True`, quality `100`
- CrewAI: status 200, latency 238.0ms, keyword pass `True`, quality `100`
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
- Baseline: status 200, latency 206.9ms, keyword pass `True`, quality `90`
- CrewAI: status 200, latency 23.4ms, keyword pass `True`, quality `100`
- Baseline errors: repetitive_reply
- Baseline answer: Frequencia de Lucas Oliveira:
- Biologia: 2 presencas, 0 atrasos, 1 faltas (50 min)
- Educacao Fisica: 1 presencas, 0 atrasos, 1 faltas (50 min)
- Filosofia: 1 presencas, 1 atrasos, 0 faltas (10 min)
- Fisica: 1 presencas, 1 atrasos, 0 faltas (10 min)
- CrewAI answer: Perfeito, seguimos com Lucas Oliveira. Posso te ajudar com notas, frequencia, faltas, proximas provas, documentacao, matricula e financeiro.

### quais documentos faltam pra ana

- Slice: `protected`
- Category: `threaded_real_transcript`
- Thread: `real_document_channels_conflict` turn `1`
- Note: real transcript regression: previously answered the guardian admin profile instead of Ana
- Baseline: status 200, latency 188.2ms, keyword pass `True`, quality `100`
- CrewAI: status 200, latency 249.9ms, keyword pass `True`, quality `100`
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
- Baseline: status 200, latency 3319.7ms, keyword pass `True`, quality `100`
- CrewAI: status 200, latency 25.6ms, keyword pass `True`, quality `100`
- Baseline answer: Hoje a escola nao utiliza fax para envio de documentos. Para isso, use portal institucional, email da secretaria, secretaria presencial.
- CrewAI answer: Hoje a escola nao utiliza fax institucional.

### qual o número do fax?

- Slice: `public`
- Category: `threaded_real_transcript`
- Thread: `real_document_channels_conflict` turn `3`
- Baseline: status 200, latency 6776.0ms, keyword pass `True`, quality `100`
- CrewAI: status 200, latency 28.4ms, keyword pass `True`, quality `90`
- CrewAI errors: repetitive_reply
- Baseline answer: O Colégio Horizonte não utiliza fax atualmente. Para contato telefônico, o número da secretaria é (11) 3333-4200.
- CrewAI answer: Hoje a escola nao utiliza fax institucional.

### mas antes você respondeu que eu podia enviar por fax

- Slice: `public`
- Category: `threaded_real_transcript`
- Thread: `real_document_channels_conflict` turn `4`
- Note: repair turn from real transcript
- Baseline: status 200, latency 5426.0ms, keyword pass `True`, quality `100`
- CrewAI: status 200, latency 25.3ms, keyword pass `True`, quality `90`
- CrewAI errors: repetitive_reply
- Baseline answer: Peço desculpas pela confusão! O Colégio Horizonte não utiliza fax para envio de documentos atualmente. Para sua comodidade, você pode usar nosso portal institucional, o e-mail da secretaria ou o atendimento presencial.
- CrewAI answer: Hoje a escola nao utiliza fax institucional.

### e se eu mandar por telegrama, serve?

- Slice: `public`
- Category: `threaded_real_transcript`
- Thread: `real_document_channels_conflict` turn `5`
- Note: real transcript regression: previously repeated generic digital-channel copy
- Baseline: status 200, latency 5200.7ms, keyword pass `True`, quality `100`
- CrewAI: status 200, latency 26.6ms, keyword pass `True`, quality `100`
- Baseline answer: Entendo sua dúvida! No momento, o Colégio Horizonte não aceita documentos via telegrama. Para garantir que sua solicitação seja processada, por favor, utilize nosso portal institucional, o e-mail da secretaria ou o atendimento presencial.
- CrewAI answer: Hoje a escola nao publica telegrama como canal valido. Para documentos, use portal institucional, email da secretaria ou secretaria presencial.

### qual sua caixa postal?

- Slice: `public`
- Category: `threaded_real_transcript`
- Thread: `real_document_channels_conflict` turn `6`
- Baseline: status 200, latency 5417.2ms, keyword pass `True`, quality `100`
- CrewAI: status 200, latency 26.3ms, keyword pass `True`, quality `100`
- Baseline answer: Olá! O Colégio Horizonte não utiliza caixa postal para o envio de documentos. Para sua comodidade, você pode usar nosso portal institucional, o e-mail da secretaria ou o atendimento presencial.
- CrewAI answer: Hoje a escola nao trabalha com caixa postal para esse tipo de envio. Para documentos, use portal institucional, email da secretaria ou secretaria presencial.
