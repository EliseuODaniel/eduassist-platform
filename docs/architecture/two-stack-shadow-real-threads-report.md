# Two-Stack Shadow Comparison Report

## Summary

- Total prompts: 15
- `protected`: baseline ok 10/10, CrewAI ok 10/10, baseline keyword pass 10/10, CrewAI keyword pass 9/10, quality 95.5 vs 96.0, latency 172.8ms vs 3553.9ms
- `public`: baseline ok 5/5, CrewAI ok 5/5, baseline keyword pass 2/5, CrewAI keyword pass 3/5, quality 71.6 vs 83.0, latency 4576.7ms vs 11111.0ms

## By Category

- `threaded_real_transcript`: baseline ok 15/15, CrewAI ok 15/15, baseline keyword pass 12/15, CrewAI keyword pass 12/15, quality 87.5 vs 91.7

## Error Types

- `baseline`: followup_context_drop=1, forbidden_entity_or_value=2, missing_expected_keyword=3, unnecessary_clarification=1
- `crewai`: followup_context_drop=1, missing_expected_keyword=3, repetitive_reply=4

## By Thread

- `real_guardian_identity_and_student_scope` (protected/threaded_real_transcript): baseline keyword pass 9/9, CrewAI keyword pass 8/9, quality 95.0 vs 95.6
- `real_document_channels_conflict` (protected/threaded_real_transcript): baseline keyword pass 3/6, CrewAI keyword pass 4/6, quality 76.3 vs 85.8

## Prompt Results

### estou logado como?

- Slice: `protected`
- Category: `threaded_real_transcript`
- Thread: `real_guardian_identity_and_student_scope` turn `1`
- Baseline: status 200, latency 184.2ms, keyword pass `True`, quality `100`
- CrewAI: status 200, latency 25.8ms, keyword pass `True`, quality `100`
- Baseline answer: Voce esta falando aqui como Maria Oliveira, no perfil de responsavel. Sua conta esta vinculada a Lucas Oliveira e Ana Oliveira. Por aqui eu consigo consultar notas, faltas, proximas provas, matricula, financeiro, boletos, dentro das permissoes dessa vinculacao.
- CrewAI answer: Voce esta autenticado aqui como Maria Oliveira. Sua conta esta vinculada a Lucas Oliveira, Ana Oliveira e pode consultar notas, frequencia, avaliacoes, documentacao e financeiro desses alunos.

### quais notas do meu filho lucas

- Slice: `protected`
- Category: `threaded_real_transcript`
- Thread: `real_guardian_identity_and_student_scope` turn `2`
- Baseline: status 200, latency 190.5ms, keyword pass `True`, quality `100`
- CrewAI: status 200, latency 21.2ms, keyword pass `True`, quality `100`
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
- Baseline: status 200, latency 132.8ms, keyword pass `True`, quality `100`
- CrewAI: status 200, latency 20.1ms, keyword pass `False`, quality `70`
- CrewAI errors: missing_expected_keyword, repetitive_reply
- Baseline answer: Hoje eu nao encontrei Joao entre os alunos vinculados a esta conta. No momento, os alunos que aparecem aqui sao: Lucas Oliveira (MAT-2026-001), Ana Oliveira (MAT-2026-002). Se quiser, me diga qual deles voce quer consultar.
- CrewAI answer: Sua conta esta vinculada a Lucas Oliveira, Ana Oliveira.

### qual situação de documentação do lucas?

- Slice: `protected`
- Category: `threaded_real_transcript`
- Thread: `real_guardian_identity_and_student_scope` turn `4`
- Baseline: status 200, latency 166.2ms, keyword pass `True`, quality `100`
- CrewAI: status 200, latency 234.5ms, keyword pass `True`, quality `100`
- Baseline answer: Situacao documental de Lucas Oliveira hoje: regular.
- CrewAI answer: A situacao documental de Lucas Oliveira hoje esta regular e completa.

### lucas oliveira, o luquinha

- Slice: `protected`
- Category: `threaded_real_transcript`
- Thread: `real_guardian_identity_and_student_scope` turn `5`
- Note: real transcript disambiguation turn
- Baseline: status 200, latency 139.3ms, keyword pass `True`, quality `100`
- CrewAI: status 200, latency 34015.3ms, keyword pass `True`, quality `100`
- Baseline answer: Perfeito, seguimos com Lucas Oliveira. Posso te ajudar com notas, faltas, proximas provas, matricula, financeiro, boletos. Se quiser, ja me diga o que voce quer ver primeiro.
- CrewAI answer: Para o aluno Lucas Oliveira (MAT-2026-001), o sistema pode fornecer uma visão geral que inclui informações de avaliações, frequência, dados administrativos, identidade, situação financeira e desempenho acadêmico.

### quais próximas provas do lucas

- Slice: `protected`
- Category: `threaded_real_transcript`
- Thread: `real_guardian_identity_and_student_scope` turn `6`
- Baseline: status 200, latency 239.4ms, keyword pass `True`, quality `100`
- CrewAI: status 200, latency 233.5ms, keyword pass `True`, quality `100`
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
- Baseline: status 200, latency 177.2ms, keyword pass `True`, quality `100`
- CrewAI: status 200, latency 265.4ms, keyword pass `True`, quality `100`
- Baseline answer: A matricula de Lucas Oliveira e MAT-2026-001. Turma atual: 1o Ano A.
- CrewAI answer: A matricula de Lucas Oliveira e MAT-2026-001.

### e como estão as faltas do lucas

- Slice: `protected`
- Category: `threaded_real_transcript`
- Thread: `real_guardian_identity_and_student_scope` turn `8`
- Note: real transcript regression: previously echoed enrollment instead of attendance
- Baseline: status 200, latency 183.3ms, keyword pass `True`, quality `100`
- CrewAI: status 200, latency 243.4ms, keyword pass `True`, quality `100`
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
- Baseline: status 200, latency 152.2ms, keyword pass `True`, quality `55`
- CrewAI: status 200, latency 228.7ms, keyword pass `True`, quality `90`
- Baseline errors: forbidden_entity_or_value
- CrewAI errors: repetitive_reply
- Baseline answer: Hoje eu nao encontrei Frequencia entre os alunos vinculados a esta conta. No momento, os alunos que aparecem aqui sao: Lucas Oliveira (MAT-2026-001), Ana Oliveira (MAT-2026-002). Se quiser, me diga qual deles voce quer consultar.
- CrewAI answer: Lucas Oliveira tem 3 falta(s) e 3 registro(s) de atraso neste recorte.

### quais documentos faltam pra ana

- Slice: `protected`
- Category: `threaded_real_transcript`
- Thread: `real_document_channels_conflict` turn `1`
- Note: real transcript regression: previously answered the guardian admin profile instead of Ana
- Baseline: status 200, latency 162.9ms, keyword pass `True`, quality `100`
- CrewAI: status 200, latency 250.9ms, keyword pass `True`, quality `100`
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
- Baseline: status 200, latency 3897.6ms, keyword pass `False`, quality `35`
- CrewAI: status 200, latency 25.6ms, keyword pass `True`, quality `100`
- Baseline errors: forbidden_entity_or_value, missing_expected_keyword
- Baseline answer: Sim. O envio inicial de documentos pode ser feito por canal digital.
Hoje os canais mais diretos publicados para isso sao:
- portal institucional
- email da secretaria
- secretaria presencial para conferencia final
No processo de matricula, o envio inicial pode ser digital. A validacao final continua com a secretaria.
O chat aberto nao deve receber documentos completos ou dados sensiveis. Quando possivel, use o portal autenticado ou o email institucional.
- CrewAI answer: Hoje a escola nao utiliza fax institucional.

### qual o número do fax?

- Slice: `public`
- Category: `threaded_real_transcript`
- Thread: `real_document_channels_conflict` turn `3`
- Baseline: status 200, latency 6821.5ms, keyword pass `True`, quality `100`
- CrewAI: status 200, latency 28.2ms, keyword pass `True`, quality `90`
- CrewAI errors: repetitive_reply
- Baseline answer: O Colégio Horizonte não utiliza fax para comunicação, mas você pode entrar em contato com a secretaria pelo telefone (11) 3333-4200.
- CrewAI answer: Hoje a escola nao utiliza fax institucional.

### mas antes você respondeu que eu podia enviar por fax

- Slice: `public`
- Category: `threaded_real_transcript`
- Thread: `real_document_channels_conflict` turn `4`
- Note: repair turn from real transcript
- Baseline: status 200, latency 8200.9ms, keyword pass `False`, quality `80`
- CrewAI: status 200, latency 24.6ms, keyword pass `True`, quality `90`
- Baseline errors: missing_expected_keyword
- CrewAI errors: repetitive_reply
- Baseline answer: Peço desculpas pela confusão anterior. O Colégio Horizonte é uma escola laica, com uma proposta institucional plural e não confessional.
- CrewAI answer: Hoje a escola nao utiliza fax institucional.

### e se eu mandar por telegrama, serve?

- Slice: `public`
- Category: `threaded_real_transcript`
- Thread: `real_document_channels_conflict` turn `5`
- Note: real transcript regression: previously repeated generic digital-channel copy
- Baseline: status 200, latency 1882.0ms, keyword pass `False`, quality `43`
- CrewAI: status 200, latency 34706.2ms, keyword pass `False`, quality `55`
- Baseline errors: followup_context_drop, missing_expected_keyword, unnecessary_clarification
- CrewAI errors: followup_context_drop, missing_expected_keyword
- Baseline answer: Posso ajudar com informacoes publicas da escola, como calendario, matricula, documentos exigidos e regras de atendimento digital. Se quiser, pergunte por exemplo: "quais documentos preciso para a matricula?" ou "quando acontece a reuniao de pais?".
- CrewAI answer: Olá! Não encontramos informações sobre o uso de telegrama como forma de contato nos nossos documentos. No entanto, você pode entrar em contato conosco por e-mail.

### qual sua caixa postal?

- Slice: `public`
- Category: `threaded_real_transcript`
- Thread: `real_document_channels_conflict` turn `6`
- Baseline: status 200, latency 2081.6ms, keyword pass `True`, quality `100`
- CrewAI: status 200, latency 20770.4ms, keyword pass `False`, quality `80`
- CrewAI errors: missing_expected_keyword
- Baseline answer: Como assistente virtual, eu não tenho uma caixa postal física. Se você precisa enviar algum documento ou correspondência para o Colégio Horizonte, por favor, entre em contato com a secretaria da escola para verificar o endereço e a melhor forma de envio. Você pode ligar para (11) 3333-4200 ou enviar um e-mail para o endereço institucional.
- CrewAI answer: Poxa, não consegui encontrar o endereço da escola nas informações que tenho aqui.
