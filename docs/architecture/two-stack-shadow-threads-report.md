# Two-Stack Shadow Comparison Report

## Summary

- Total prompts: 15
- `public`: baseline ok 6/6, CrewAI ok 6/6, baseline keyword pass 6/6, CrewAI keyword pass 6/6, latency 7207.3ms vs 28.0ms
- `protected`: baseline ok 9/9, CrewAI ok 9/9, baseline keyword pass 9/9, CrewAI keyword pass 9/9, latency 158.7ms vs 143.6ms

## By Category

- `threaded_public_context`: baseline ok 6/6, CrewAI ok 6/6, baseline keyword pass 6/6, CrewAI keyword pass 6/6
- `threaded_protected_context`: baseline ok 9/9, CrewAI ok 9/9, baseline keyword pass 9/9, CrewAI keyword pass 9/9

## Error Types

- `baseline`: nenhum
- `crewai`: nenhum

## By Thread

- `public_biblioteca_followup` (public/threaded_public_context): baseline keyword pass 2/2, CrewAI keyword pass 2/2
- `public_contact_followup` (public/threaded_public_context): baseline keyword pass 2/2, CrewAI keyword pass 2/2
- `public_feature_followup` (public/threaded_public_context): baseline keyword pass 2/2, CrewAI keyword pass 2/2
- `protected_lucas_followup` (protected/threaded_protected_context): baseline keyword pass 3/3, CrewAI keyword pass 3/3
- `protected_student_repair` (protected/threaded_protected_context): baseline keyword pass 3/3, CrewAI keyword pass 3/3
- `protected_admin_followup` (protected/threaded_protected_context): baseline keyword pass 3/3, CrewAI keyword pass 3/3

## Prompt Results

### essa escola tem biblioteca?

- Slice: `public`
- Category: `threaded_public_context`
- Thread: `public_biblioteca_followup` turn `1`
- Baseline: status 200, latency 7498.6ms, keyword pass `True`
- CrewAI: status 200, latency 26.9ms, keyword pass `True`
- Baseline answer: Sim, o Colégio Horizonte tem uma biblioteca, a Biblioteca Aurora! Ela funciona de segunda a sexta-feira, das 7h30 às 18h00, e está sempre de portas abertas para nossos alunos.
- CrewAI answer: Sim, a escola tem a Biblioteca Aurora, com atendimento das 7h30 as 18h00.

### e qual o horario?

- Slice: `public`
- Category: `threaded_public_context`
- Thread: `public_biblioteca_followup` turn `2`
- Note: follow-up eliptico sobre a biblioteca
- Baseline: status 200, latency 6757.5ms, keyword pass `True`
- CrewAI: status 200, latency 28.2ms, keyword pass `True`
- Baseline answer: A Biblioteca Aurora funciona de segunda a sexta-feira, das 7h30 às 18h00.
- CrewAI answer: A Biblioteca Aurora atende ao publico de segunda a sexta, das 7h30 as 18h00.

### como ligo pra escola?

- Slice: `public`
- Category: `threaded_public_context`
- Thread: `public_contact_followup` turn `1`
- Baseline: status 200, latency 7029.6ms, keyword pass `True`
- CrewAI: status 200, latency 27.7ms, keyword pass `True`
- Baseline answer: Olá! Para falar com a secretaria do Colégio Horizonte por telefone, você pode ligar para o número (11) 3333-4200. Estamos à disposição para ajudar!
- CrewAI answer: Secretaria (telefone): (11) 3333-4200

### e o fax?

- Slice: `public`
- Category: `threaded_public_context`
- Thread: `public_contact_followup` turn `2`
- Note: follow-up curto sobre o canal anterior
- Baseline: status 200, latency 7081.4ms, keyword pass `True`
- CrewAI: status 200, latency 26.7ms, keyword pass `True`
- Baseline answer: Olá! O Colégio Horizonte não utiliza fax atualmente. Se precisar falar conosco por telefone, o número da secretaria é (11) 3333-4200.
- CrewAI answer: Hoje a escola nao utiliza fax institucional.

### quais aulas complementares essa escola oferece?

- Slice: `public`
- Category: `threaded_public_context`
- Thread: `public_feature_followup` turn `1`
- Baseline: status 200, latency 7515.4ms, keyword pass `True`
- CrewAI: status 200, latency 33.2ms, keyword pass `True`
- Baseline answer: Que bom que você perguntou! No Colégio Horizonte, temos uma variedade de atividades complementares para enriquecer o aprendizado dos nossos alunos. Para o Ensino Fundamental II, oferecemos oficinas, plantões de dúvidas, esportes e estudo orientado em dias alternados. Já os alunos do Ensino Médio podem aproveitar trilhas eletivas, monitorias e laboratórios a partir das 14h. E para todos, temos futsal, vôlei escolar, acesso ao Espaço Maker e ao Laboratório de Ciências.
- CrewAI answer: Hoje a escola divulga atividades e espacos complementares como Biblioteca Aurora, Espaco Maker, futsal, volei escolar. Se quiser, eu tambem posso detalhar Biblioteca Aurora, Laboratorio de Ciencias, Espaco Maker, Quadra Poliesportiva Coberta.

### e a biblioteca?

- Slice: `public`
- Category: `threaded_public_context`
- Thread: `public_feature_followup` turn `2`
- Note: follow-up curto sobre estrutura apos atividades
- Baseline: status 200, latency 7361.6ms, keyword pass `True`
- CrewAI: status 200, latency 25.2ms, keyword pass `True`
- Baseline answer: Que bom que você perguntou sobre a biblioteca! A nossa Biblioteca Aurora está aberta de segunda a sexta-feira, das 7h30 às 18h00. É um espaço super tranquilo e completo para os estudos e pesquisas dos nossos alunos.
- CrewAI answer: Sim, a escola tem a Biblioteca Aurora, com atendimento das 7h30 as 18h00.

### quais meus filhos?

- Slice: `protected`
- Category: `threaded_protected_context`
- Thread: `protected_lucas_followup` turn `1`
- Baseline: status 200, latency 117.9ms, keyword pass `True`
- CrewAI: status 200, latency 21.3ms, keyword pass `True`
- Baseline answer: Os alunos vinculados a esta conta hoje sao Lucas Oliveira e Ana Oliveira. Eu posso consultar notas, faltas, proximas provas, matricula, financeiro, boletos, dentro do que sua vinculacao permitir. Se quiser, me diga direto algo como "notas do Lucas" ou "financeiro da Ana".
- CrewAI answer: Sua conta esta vinculada a Lucas Oliveira, Ana Oliveira.

### notas do Lucas

- Slice: `protected`
- Category: `threaded_protected_context`
- Thread: `protected_lucas_followup` turn `2`
- Baseline: status 200, latency 183.2ms, keyword pass `True`
- CrewAI: status 200, latency 266.9ms, keyword pass `True`
- Baseline answer: Notas de Lucas Oliveira:
- Biologia - Avaliacao B1: 8.40/10.00
- Biologia - Avaliacao 2026-B1 - BIO: 7.00/10.00
- Biologia - Trabalho B1: 8.10/10.00
- Biologia - Avaliacao B2: 8.60/10.00
- CrewAI answer: As notas mais recentes de Lucas Oliveira incluem Biologia: 8.40/10.00; Biologia: 7.00/10.00; Biologia: 8.10/10.00.

### e como estao as faltas dele?

- Slice: `protected`
- Category: `threaded_protected_context`
- Thread: `protected_lucas_followup` turn `3`
- Note: follow-up por pronome
- Baseline: status 200, latency 183.4ms, keyword pass `True`
- CrewAI: status 200, latency 228.6ms, keyword pass `True`
- Baseline answer: Frequencia de Lucas Oliveira:
- Biologia: 2 presencas, 0 atrasos, 1 faltas (50 min)
- Educacao Fisica: 1 presencas, 0 atrasos, 1 faltas (50 min)
- Filosofia: 1 presencas, 1 atrasos, 0 faltas (10 min)
- Fisica: 1 presencas, 1 atrasos, 0 faltas (10 min)
- CrewAI answer: Lucas Oliveira tem 3 falta(s) e 3 registro(s) de atraso neste recorte.

### quais meus filhos?

- Slice: `protected`
- Category: `threaded_protected_context`
- Thread: `protected_student_repair` turn `1`
- Baseline: status 200, latency 121.8ms, keyword pass `True`
- CrewAI: status 200, latency 20.8ms, keyword pass `True`
- Baseline answer: Os alunos vinculados a esta conta hoje sao Lucas Oliveira e Ana Oliveira. Eu posso consultar notas, faltas, proximas provas, matricula, financeiro, boletos, dentro do que sua vinculacao permitir. Se quiser, me diga direto algo como "notas do Lucas" ou "financeiro da Ana".
- CrewAI answer: Sua conta esta vinculada a Lucas Oliveira, Ana Oliveira.

### notas do Lucas

- Slice: `protected`
- Category: `threaded_protected_context`
- Thread: `protected_student_repair` turn `2`
- Baseline: status 200, latency 202.4ms, keyword pass `True`
- CrewAI: status 200, latency 231.2ms, keyword pass `True`
- Baseline answer: Notas de Lucas Oliveira:
- Biologia - Avaliacao B1: 8.40/10.00
- Biologia - Avaliacao 2026-B1 - BIO: 7.00/10.00
- Biologia - Trabalho B1: 8.10/10.00
- Biologia - Avaliacao B2: 8.60/10.00
- CrewAI answer: As notas mais recentes de Lucas Oliveira incluem Biologia: 8.40/10.00; Biologia: 7.00/10.00; Biologia: 8.10/10.00.

### lucas eu falei

- Slice: `protected`
- Category: `threaded_protected_context`
- Thread: `protected_student_repair` turn `3`
- Note: retomada curta do aluno em foco
- Baseline: status 200, latency 144.8ms, keyword pass `True`
- CrewAI: status 200, latency 20.2ms, keyword pass `True`
- Baseline answer: Perfeito, seguimos com Lucas Oliveira. Posso te ajudar com notas, faltas, proximas provas, matricula, financeiro, boletos. Se quiser, ja me diga o que voce quer ver primeiro.
- CrewAI answer: Perfeito, seguimos com Lucas Oliveira. Posso te ajudar com notas, faltas, proximas provas, documentacao, matricula e financeiro.

### estou logado como?

- Slice: `protected`
- Category: `threaded_protected_context`
- Thread: `protected_admin_followup` turn `1`
- Baseline: status 200, latency 121.2ms, keyword pass `True`
- CrewAI: status 200, latency 20.3ms, keyword pass `True`
- Baseline answer: Voce esta falando aqui como Maria Oliveira, no perfil de responsavel. Sua conta esta vinculada a Lucas Oliveira e Ana Oliveira. Por aqui eu consigo consultar notas, faltas, proximas provas, matricula, financeiro, boletos, dentro das permissoes dessa vinculacao.
- CrewAI answer: Voce esta autenticado aqui como Maria Oliveira. Sua conta esta vinculada a Lucas Oliveira, Ana Oliveira e pode consultar notas, frequencia, avaliacoes, documentacao e financeiro desses alunos.

### e a documentacao do Lucas?

- Slice: `protected`
- Category: `threaded_protected_context`
- Thread: `protected_admin_followup` turn `2`
- Baseline: status 200, latency 177.7ms, keyword pass `True`
- CrewAI: status 200, latency 226.2ms, keyword pass `True`
- Baseline answer: Situacao documental de Lucas Oliveira hoje: regular.
- Identificacao escolar do aluno: regular. Codigo de matricula: MAT-2026-001
- Responsavel vinculado: regular. Maria Oliveira
- Documentacao escolar do aluno: regular. A documentacao escolar de Lucas Oliveira esta conferida e sem pendencias relevantes nesta base de testes.
- CrewAI answer: A situacao documental de Lucas Oliveira hoje esta regular e completa.

### e o proximo pagamento?

- Slice: `protected`
- Category: `threaded_protected_context`
- Thread: `protected_admin_followup` turn `3`
- Note: follow-up financeiro no mesmo aluno
- Baseline: status 200, latency 176.1ms, keyword pass `True`
- CrewAI: status 200, latency 256.8ms, keyword pass `True`
- Baseline answer: Hoje nao encontrei um proximo pagamento pendente de Lucas Oliveira.
- CrewAI answer: No momento, nao vejo fatura em aberto para Lucas Oliveira neste recorte.
