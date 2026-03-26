# Two-Stack Shadow Comparison Report

## Summary

- Total prompts: 10
- `public`: baseline ok 3/4, CrewAI ok 4/4, baseline keyword pass 2/4, CrewAI keyword pass 3/4, latency 5380.2ms vs 8573.9ms
- `protected`: baseline ok 6/6, CrewAI ok 6/6, baseline keyword pass 5/6, CrewAI keyword pass 6/6, latency 168.0ms vs 92.4ms

## By Category

- `threaded_public_context`: baseline ok 3/4, CrewAI ok 4/4, baseline keyword pass 2/4, CrewAI keyword pass 3/4
- `threaded_protected_context`: baseline ok 6/6, CrewAI ok 6/6, baseline keyword pass 5/6, CrewAI keyword pass 6/6

## Error Types

- `baseline`: canned_tone=1, followup_context_drop=2, forbidden_entity_or_value=1, missing_expected_keyword=2, request_failed=1
- `crewai`: forbidden_entity_or_value=2, missing_expected_keyword=1

## By Thread

- `public_biblioteca_followup` (public/threaded_public_context): baseline keyword pass 0/2, CrewAI keyword pass 2/2
- `public_contact_followup` (public/threaded_public_context): baseline keyword pass 2/2, CrewAI keyword pass 1/2
- `protected_lucas_followup` (protected/threaded_protected_context): baseline keyword pass 3/3, CrewAI keyword pass 3/3
- `protected_admin_followup` (protected/threaded_protected_context): baseline keyword pass 2/3, CrewAI keyword pass 3/3

## Prompt Results

### essa escola tem biblioteca?

- Slice: `public`
- Category: `threaded_public_context`
- Thread: `public_biblioteca_followup` turn `1`
- Baseline: status 500, latency 150.4ms, keyword pass `False`
- CrewAI: status 200, latency 18436.8ms, keyword pass `True`
- Baseline errors: request_failed
- Baseline answer: Internal Server Error
- CrewAI answer: Olá! Não encontrei informações específicas sobre a biblioteca da escola nos documentos que consultei. Para obter esses detalhes, sugiro que entre em contato diretamente com a escola.

### e qual o horario?

- Slice: `public`
- Category: `threaded_public_context`
- Thread: `public_biblioteca_followup` turn `2`
- Note: follow-up eliptico sobre a biblioteca
- Baseline: status 200, latency 7134.9ms, keyword pass `False`
- CrewAI: status 200, latency 25.8ms, keyword pass `True`
- Baseline errors: followup_context_drop, missing_expected_keyword
- Baseline answer: Que bom que você perguntou! Nosso atendimento presencial no Colégio Horizonte funciona de segunda a sexta-feira, a partir das 7h. Se você estiver pensando na Biblioteca Aurora, ela abre um pouquinho mais tarde, às 7h30.
- CrewAI answer: A Biblioteca Aurora atende ao publico de segunda a sexta, das 7h30 as 18h00.

### como ligo pra escola?

- Slice: `public`
- Category: `threaded_public_context`
- Thread: `public_contact_followup` turn `1`
- Baseline: status 200, latency 7404.4ms, keyword pass `True`
- CrewAI: status 200, latency 15807.1ms, keyword pass `False`
- CrewAI errors: missing_expected_keyword
- Baseline answer: Para falar com a gente por telefone, o número da secretaria do Colégio Horizonte é (11) 3333-4200. Se precisar de outros setores, temos também telefones específicos para Admissões, Orientação Educacional e Financeiro, e podemos te passar se desejar.
- CrewAI answer: Não encontrei as informações de contato da escola que você procura. Para obter essa informação, sugiro que você entre em contato diretamente com a instituição.

### e o fax?

- Slice: `public`
- Category: `threaded_public_context`
- Thread: `public_contact_followup` turn `2`
- Note: follow-up curto sobre o canal anterior
- Baseline: status 200, latency 6831.3ms, keyword pass `True`
- CrewAI: status 200, latency 26.1ms, keyword pass `True`
- Baseline answer: Hoje Colegio Horizonte nao publica numero de fax. Se quiser ligar, o telefone principal e (11) 3333-4202.
- CrewAI answer: Hoje a escola nao utiliza fax institucional.

### quais meus filhos?

- Slice: `protected`
- Category: `threaded_protected_context`
- Thread: `protected_lucas_followup` turn `1`
- Baseline: status 200, latency 114.4ms, keyword pass `True`
- CrewAI: status 200, latency 20.7ms, keyword pass `True`
- Baseline errors: canned_tone
- Baseline answer: Sua conta esta vinculada a Lucas Oliveira e Ana Oliveira. Por aqui eu consigo te ajudar com notas, faltas, proximas provas, matricula, financeiro, boletos, dentro do que sua vinculacao permitir. Se quiser, pode me dizer direto algo como "notas do Lucas" ou "financeiro da Ana".
- CrewAI answer: Sua conta esta vinculada a Lucas Oliveira, Ana Oliveira.

### notas do Lucas

- Slice: `protected`
- Category: `threaded_protected_context`
- Thread: `protected_lucas_followup` turn `2`
- Baseline: status 200, latency 185.4ms, keyword pass `True`
- CrewAI: status 200, latency 227.0ms, keyword pass `True`
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
- Baseline: status 200, latency 184.4ms, keyword pass `True`
- CrewAI: status 200, latency 20.5ms, keyword pass `True`
- CrewAI errors: forbidden_entity_or_value
- Baseline answer: Frequencia de Lucas Oliveira:
- Biologia: 2 presencas, 0 atrasos, 1 faltas (50 min)
- Educacao Fisica: 1 presencas, 0 atrasos, 1 faltas (50 min)
- Filosofia: 1 presencas, 1 atrasos, 0 faltas (10 min)
- Fisica: 1 presencas, 1 atrasos, 0 faltas (10 min)
- CrewAI answer: Posso te ajudar com Lucas Oliveira, Ana Oliveira. Me diga qual aluno voce quer consultar.

### estou logado como?

- Slice: `protected`
- Category: `threaded_protected_context`
- Thread: `protected_admin_followup` turn `1`
- Baseline: status 200, latency 119.4ms, keyword pass `True`
- CrewAI: status 200, latency 21.1ms, keyword pass `True`
- Baseline answer: Voce esta falando aqui como Maria Oliveira, no perfil de responsavel. Sua conta esta vinculada a Lucas Oliveira e Ana Oliveira. Por aqui eu consigo consultar notas, faltas, proximas provas, matricula, financeiro, boletos, dentro das permissoes dessa vinculacao.
- CrewAI answer: Voce esta autenticado aqui como Maria Oliveira. Sua conta esta vinculada a Lucas Oliveira, Ana Oliveira e pode consultar notas, frequencia, avaliacoes, documentacao e financeiro desses alunos.

### e a documentacao do Lucas?

- Slice: `protected`
- Category: `threaded_protected_context`
- Thread: `protected_admin_followup` turn `2`
- Baseline: status 200, latency 192.9ms, keyword pass `False`
- CrewAI: status 200, latency 245.0ms, keyword pass `True`
- Baseline errors: followup_context_drop, missing_expected_keyword
- Baseline answer: Resumo financeiro de Lucas Oliveira:
- Contrato: CTR-2026-001
- Responsavel financeiro: Maria Oliveira
- Mensalidade base: 1450.00
- Faturas em aberto: 0
- Faturas vencidas: 0
Ultimas faturas:
- 2026-03: vencimento 2026-03-10, status paga, valor 1450.00
- CrewAI answer: A situacao documental de Lucas Oliveira hoje esta regular e completa.

### e o proximo pagamento?

- Slice: `protected`
- Category: `threaded_protected_context`
- Thread: `protected_admin_followup` turn `3`
- Note: follow-up financeiro no mesmo aluno
- Baseline: status 200, latency 211.4ms, keyword pass `True`
- CrewAI: status 200, latency 20.0ms, keyword pass `True`
- Baseline errors: forbidden_entity_or_value
- CrewAI errors: forbidden_entity_or_value
- Baseline answer: Resumo financeiro das contas vinculadas:
- Total de faturas em aberto: 1
- Total de faturas vencidas: 0
- Lucas Oliveira: 0 em aberto, 0 vencidas
  2026-03: vencimento 2026-03-10, status paga, valor 1450.00
- Ana Oliveira: 1 em aberto, 0 vencidas
  2026-03: vencimento 2026-03-10, status em aberto, valor 1450.00
- CrewAI answer: Posso te ajudar com Lucas Oliveira, Ana Oliveira. Me diga qual aluno voce quer consultar.
