# Two-Stack Shadow Comparison Report

## Summary

- Total prompts: 10
- `public`: baseline ok 4/4, CrewAI ok 4/4, baseline keyword pass 3/4, CrewAI keyword pass 4/4, latency 6846.9ms vs 26.0ms
- `protected`: baseline ok 6/6, CrewAI ok 6/6, baseline keyword pass 6/6, CrewAI keyword pass 6/6, latency 163.3ms vs 162.7ms

## By Category

- `threaded_public_context`: baseline ok 4/4, CrewAI ok 4/4, baseline keyword pass 3/4, CrewAI keyword pass 4/4
- `threaded_protected_context`: baseline ok 6/6, CrewAI ok 6/6, baseline keyword pass 6/6, CrewAI keyword pass 6/6

## Error Types

- `baseline`: canned_tone=1, followup_context_drop=1, missing_expected_keyword=1
- `crewai`: nenhum

## By Thread

- `public_biblioteca_followup` (public/threaded_public_context): baseline keyword pass 1/2, CrewAI keyword pass 2/2
- `public_contact_followup` (public/threaded_public_context): baseline keyword pass 2/2, CrewAI keyword pass 2/2
- `protected_lucas_followup` (protected/threaded_protected_context): baseline keyword pass 3/3, CrewAI keyword pass 3/3
- `protected_admin_followup` (protected/threaded_protected_context): baseline keyword pass 3/3, CrewAI keyword pass 3/3

## Prompt Results

### essa escola tem biblioteca?

- Slice: `public`
- Category: `threaded_public_context`
- Thread: `public_biblioteca_followup` turn `1`
- Baseline: status 200, latency 7049.5ms, keyword pass `True`
- CrewAI: status 200, latency 26.6ms, keyword pass `True`
- Baseline answer: Sim, o Colégio Horizonte tem a Biblioteca Aurora! Ela funciona de segunda a sexta-feira, com atendimento ao público das 7h30 às 18h.
- CrewAI answer: Sim, a escola tem a Biblioteca Aurora, com atendimento das 7h30 as 18h00.

### e qual o horario?

- Slice: `public`
- Category: `threaded_public_context`
- Thread: `public_biblioteca_followup` turn `2`
- Note: follow-up eliptico sobre a biblioteca
- Baseline: status 200, latency 6704.7ms, keyword pass `False`
- CrewAI: status 200, latency 26.6ms, keyword pass `True`
- Baseline errors: followup_context_drop, missing_expected_keyword
- Baseline answer: A Biblioteca Aurora, aqui no Colégio Horizonte, funciona de segunda a sexta-feira, com atendimento ao público das 7h30 às 18h.
- CrewAI answer: A Biblioteca Aurora atende ao publico de segunda a sexta, das 7h30 as 18h00.

### como ligo pra escola?

- Slice: `public`
- Category: `threaded_public_context`
- Thread: `public_contact_followup` turn `1`
- Baseline: status 200, latency 7263.4ms, keyword pass `True`
- CrewAI: status 200, latency 25.9ms, keyword pass `True`
- Baseline answer: Para falar com a gente por telefone, o número da secretaria do Colégio Horizonte é (11) 3333-4200. Se precisar de outros setores, como Admissões ou Financeiro, temos números específicos e posso te passar se desejar.
- CrewAI answer: Secretaria (telefone): (11) 3333-4200

### e o fax?

- Slice: `public`
- Category: `threaded_public_context`
- Thread: `public_contact_followup` turn `2`
- Note: follow-up curto sobre o canal anterior
- Baseline: status 200, latency 6370.2ms, keyword pass `True`
- CrewAI: status 200, latency 24.8ms, keyword pass `True`
- Baseline answer: Hoje o Colégio Horizonte não utiliza fax. Se precisar ligar, o telefone da Orientação Educacional é (11) 3333-4202.
- CrewAI answer: Hoje a escola nao utiliza fax institucional.

### quais meus filhos?

- Slice: `protected`
- Category: `threaded_protected_context`
- Thread: `protected_lucas_followup` turn `1`
- Baseline: status 200, latency 123.0ms, keyword pass `True`
- CrewAI: status 200, latency 20.6ms, keyword pass `True`
- Baseline errors: canned_tone
- Baseline answer: Sua conta esta vinculada a Lucas Oliveira e Ana Oliveira. Por aqui eu consigo te ajudar com notas, faltas, proximas provas, matricula, financeiro, boletos, dentro do que sua vinculacao permitir. Se quiser, pode me dizer direto algo como "notas do Lucas" ou "financeiro da Ana".
- CrewAI answer: Sua conta esta vinculada a Lucas Oliveira, Ana Oliveira.

### notas do Lucas

- Slice: `protected`
- Category: `threaded_protected_context`
- Thread: `protected_lucas_followup` turn `2`
- Baseline: status 200, latency 181.9ms, keyword pass `True`
- CrewAI: status 200, latency 229.6ms, keyword pass `True`
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
- Baseline: status 200, latency 185.2ms, keyword pass `True`
- CrewAI: status 200, latency 237.9ms, keyword pass `True`
- Baseline answer: Frequencia de Lucas Oliveira:
- Biologia: 2 presencas, 0 atrasos, 1 faltas (50 min)
- Educacao Fisica: 1 presencas, 0 atrasos, 1 faltas (50 min)
- Filosofia: 1 presencas, 1 atrasos, 0 faltas (10 min)
- Fisica: 1 presencas, 1 atrasos, 0 faltas (10 min)
- CrewAI answer: Lucas Oliveira tem 3 falta(s) e 3 registro(s) de atraso neste recorte.

### estou logado como?

- Slice: `protected`
- Category: `threaded_protected_context`
- Thread: `protected_admin_followup` turn `1`
- Baseline: status 200, latency 130.4ms, keyword pass `True`
- CrewAI: status 200, latency 20.4ms, keyword pass `True`
- Baseline answer: Voce esta falando aqui como Maria Oliveira, no perfil de responsavel. Sua conta esta vinculada a Lucas Oliveira e Ana Oliveira. Por aqui eu consigo consultar notas, faltas, proximas provas, matricula, financeiro, boletos, dentro das permissoes dessa vinculacao.
- CrewAI answer: Voce esta autenticado aqui como Maria Oliveira. Sua conta esta vinculada a Lucas Oliveira, Ana Oliveira e pode consultar notas, frequencia, avaliacoes, documentacao e financeiro desses alunos.

### e a documentacao do Lucas?

- Slice: `protected`
- Category: `threaded_protected_context`
- Thread: `protected_admin_followup` turn `2`
- Baseline: status 200, latency 185.4ms, keyword pass `True`
- CrewAI: status 200, latency 240.1ms, keyword pass `True`
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
- Baseline: status 200, latency 174.1ms, keyword pass `True`
- CrewAI: status 200, latency 227.7ms, keyword pass `True`
- Baseline answer: Hoje nao encontrei um proximo pagamento pendente de Lucas Oliveira.
- CrewAI answer: No momento, nao vejo fatura em aberto para Lucas Oliveira neste recorte.
