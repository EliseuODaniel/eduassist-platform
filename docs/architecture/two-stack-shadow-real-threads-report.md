# Two-Stack Shadow Comparison Report

## Summary

- Total prompts: 15
- `protected`: baseline ok 10/10, CrewAI ok 10/10, baseline keyword pass 10/10, CrewAI keyword pass 10/10, quality 99.0 vs 100.0, latency 168.9ms vs 178.5ms
- `public`: baseline ok 5/5, CrewAI ok 5/5, baseline keyword pass 5/5, CrewAI keyword pass 5/5, quality 100.0 vs 96.0, latency 2795.0ms vs 25.1ms

## By Category

- `threaded_real_transcript`: baseline ok 15/15, CrewAI ok 15/15, baseline keyword pass 15/15, CrewAI keyword pass 15/15, quality 99.3 vs 98.7

## Error Types

- `baseline`: repetitive_reply=1
- `crewai`: repetitive_reply=2

## By Thread

- `real_guardian_identity_and_student_scope` (protected/threaded_real_transcript): baseline keyword pass 9/9, CrewAI keyword pass 9/9, quality 98.9 vs 100.0
- `real_document_channels_conflict` (protected/threaded_real_transcript): baseline keyword pass 6/6, CrewAI keyword pass 6/6, quality 100.0 vs 96.7

## Prompt Results

### estou logado como?

- Slice: `protected`
- Category: `threaded_real_transcript`
- Thread: `real_guardian_identity_and_student_scope` turn `1`
- Baseline: status 200, latency 132.7ms, keyword pass `True`, quality `100`
- CrewAI: status 200, latency 21.3ms, keyword pass `True`, quality `100`
- Baseline answer: Voce esta falando aqui como Maria Oliveira, no perfil de responsavel. Sua conta esta vinculada a Lucas Oliveira e Ana Oliveira. Por aqui eu consigo consultar notas, faltas, proximas provas, matricula, financeiro, boletos, dentro das permissoes dessa vinculacao.
- CrewAI answer: Voce esta autenticado aqui como Maria Oliveira. Sua conta esta vinculada a Lucas Oliveira, Ana Oliveira e pode consultar notas, frequencia, avaliacoes, documentacao e financeiro desses alunos.

### quais notas do meu filho lucas

- Slice: `protected`
- Category: `threaded_real_transcript`
- Thread: `real_guardian_identity_and_student_scope` turn `2`
- Baseline: status 200, latency 180.2ms, keyword pass `True`, quality `100`
- CrewAI: status 200, latency 245.8ms, keyword pass `True`, quality `100`
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
- Baseline: status 200, latency 137.2ms, keyword pass `True`, quality `100`
- CrewAI: status 200, latency 19.4ms, keyword pass `True`, quality `100`
- Baseline answer: Hoje eu nao encontrei Joao entre os alunos vinculados a esta conta. No momento, os alunos que aparecem aqui sao: Lucas Oliveira (MAT-2026-001), Ana Oliveira (MAT-2026-002). Se quiser, me diga qual deles voce quer consultar.
- CrewAI answer: Hoje eu nao encontrei Joao entre os alunos vinculados a esta conta. No momento, os alunos que aparecem aqui sao: Lucas Oliveira, Ana Oliveira. Se quiser, me diga qual deles voce quer consultar.

### qual situação de documentação do lucas?

- Slice: `protected`
- Category: `threaded_real_transcript`
- Thread: `real_guardian_identity_and_student_scope` turn `4`
- Baseline: status 200, latency 171.6ms, keyword pass `True`, quality `100`
- CrewAI: status 200, latency 235.9ms, keyword pass `True`, quality `100`
- Baseline answer: Situacao documental de Lucas Oliveira hoje: regular.
- CrewAI answer: A situacao documental de Lucas Oliveira hoje esta regular e completa.

### lucas oliveira, o luquinha

- Slice: `protected`
- Category: `threaded_real_transcript`
- Thread: `real_guardian_identity_and_student_scope` turn `5`
- Note: real transcript disambiguation turn
- Baseline: status 200, latency 133.0ms, keyword pass `True`, quality `100`
- CrewAI: status 200, latency 20.5ms, keyword pass `True`, quality `100`
- Baseline answer: Perfeito, seguimos com Lucas Oliveira. Posso te ajudar com notas, faltas, proximas provas, matricula, financeiro, boletos. Se quiser, ja me diga o que voce quer ver primeiro.
- CrewAI answer: Perfeito, seguimos com Lucas Oliveira. Posso te ajudar com notas, frequencia, faltas, proximas provas, documentacao, matricula e financeiro.

### quais próximas provas do lucas

- Slice: `protected`
- Category: `threaded_real_transcript`
- Thread: `real_guardian_identity_and_student_scope` turn `6`
- Baseline: status 200, latency 219.3ms, keyword pass `True`, quality `100`
- CrewAI: status 200, latency 229.6ms, keyword pass `True`, quality `100`
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
- Baseline: status 200, latency 166.5ms, keyword pass `True`, quality `100`
- CrewAI: status 200, latency 229.9ms, keyword pass `True`, quality `100`
- Baseline answer: A matricula de Lucas Oliveira e MAT-2026-001. Turma atual: 1o Ano A.
- CrewAI answer: A matricula de Lucas Oliveira e MAT-2026-001.

### e como estão as faltas do lucas

- Slice: `protected`
- Category: `threaded_real_transcript`
- Thread: `real_guardian_identity_and_student_scope` turn `8`
- Note: real transcript regression: previously echoed enrollment instead of attendance
- Baseline: status 200, latency 191.3ms, keyword pass `True`, quality `100`
- CrewAI: status 200, latency 263.6ms, keyword pass `True`, quality `100`
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
- Baseline: status 200, latency 193.6ms, keyword pass `True`, quality `90`
- CrewAI: status 200, latency 289.1ms, keyword pass `True`, quality `100`
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
- Baseline: status 200, latency 163.3ms, keyword pass `True`, quality `100`
- CrewAI: status 200, latency 230.0ms, keyword pass `True`, quality `100`
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
- Baseline: status 200, latency 3699.4ms, keyword pass `True`, quality `100`
- CrewAI: status 200, latency 25.0ms, keyword pass `True`, quality `100`
- Baseline answer: Hoje a escola nao utiliza fax para envio de documentos. Para isso, use portal institucional, email da secretaria, secretaria presencial.
- CrewAI answer: Hoje a escola nao utiliza fax institucional.

### qual o número do fax?

- Slice: `public`
- Category: `threaded_real_transcript`
- Thread: `real_document_channels_conflict` turn `3`
- Baseline: status 200, latency 1726.6ms, keyword pass `True`, quality `100`
- CrewAI: status 200, latency 26.5ms, keyword pass `True`, quality `90`
- CrewAI errors: repetitive_reply
- Baseline answer: Hoje a escola não utiliza fax. Para entrar em contato por telefone, o número da secretaria é (11) 3333-4200.
- CrewAI answer: Hoje a escola nao utiliza fax institucional.

### mas antes você respondeu que eu podia enviar por fax

- Slice: `public`
- Category: `threaded_real_transcript`
- Thread: `real_document_channels_conflict` turn `4`
- Note: repair turn from real transcript
- Baseline: status 200, latency 3540.3ms, keyword pass `True`, quality `100`
- CrewAI: status 200, latency 24.6ms, keyword pass `True`, quality `90`
- CrewAI errors: repetitive_reply
- Baseline answer: Peço desculpas pela confusão! Houve um engano na minha resposta anterior. O Colégio Horizonte não utiliza fax para envio de documentos atualmente. Para sua comodidade, você pode usar nosso portal institucional, o e-mail da secretaria ou ir diretamente à secretaria presencial.
- CrewAI answer: Hoje a escola nao utiliza fax institucional.

### e se eu mandar por telegrama, serve?

- Slice: `public`
- Category: `threaded_real_transcript`
- Thread: `real_document_channels_conflict` turn `5`
- Note: real transcript regression: previously repeated generic digital-channel copy
- Baseline: status 200, latency 1556.1ms, keyword pass `True`, quality `100`
- CrewAI: status 200, latency 25.6ms, keyword pass `True`, quality `100`
- Baseline answer: Hoje a escola nao publica telegrama como canal valido para documentos. Para isso, use portal institucional, email da secretaria, secretaria presencial.
- CrewAI answer: Hoje a escola nao publica telegrama como canal valido. Para documentos, use portal institucional, email da secretaria ou secretaria presencial.

### qual sua caixa postal?

- Slice: `public`
- Category: `threaded_real_transcript`
- Thread: `real_document_channels_conflict` turn `6`
- Baseline: status 200, latency 3452.7ms, keyword pass `True`, quality `100`
- CrewAI: status 200, latency 23.9ms, keyword pass `True`, quality `100`
- Baseline answer: Hoje a escola não utiliza caixa postal para o envio de documentos. Para sua comodidade, você pode usar nosso portal institucional, o e-mail da secretaria ou ir diretamente à secretaria presencial.
- CrewAI answer: Hoje a escola nao trabalha com caixa postal para esse tipo de envio. Para documentos, use portal institucional, email da secretaria ou secretaria presencial.
