# Two-Stack Shadow Comparison Report

## Summary

- Total prompts: 10
- `public`: baseline ok 4/4, CrewAI ok 4/4, baseline keyword pass 2/4, CrewAI keyword pass 4/4, latency 4997.0ms vs 43.4ms
- `protected`: baseline ok 6/6, CrewAI ok 6/6, baseline keyword pass 5/6, CrewAI keyword pass 6/6, latency 150.8ms vs 157.4ms

## By Category

- `public_facts`: baseline ok 1/1, CrewAI ok 1/1, baseline keyword pass 1/1, CrewAI keyword pass 1/1
- `public_timeline`: baseline ok 1/1, CrewAI ok 1/1, baseline keyword pass 0/1, CrewAI keyword pass 1/1
- `public_contacts`: baseline ok 2/2, CrewAI ok 2/2, baseline keyword pass 1/2, CrewAI keyword pass 2/2
- `protected_identity`: baseline ok 2/2, CrewAI ok 2/2, baseline keyword pass 2/2, CrewAI keyword pass 2/2
- `protected_admin`: baseline ok 1/1, CrewAI ok 1/1, baseline keyword pass 0/1, CrewAI keyword pass 1/1
- `protected_financial`: baseline ok 1/1, CrewAI ok 1/1, baseline keyword pass 1/1, CrewAI keyword pass 1/1
- `protected_academic`: baseline ok 2/2, CrewAI ok 2/2, baseline keyword pass 2/2, CrewAI keyword pass 2/2

## Prompt Results

### qual o horario da biblioteca?

- Slice: `public`
- Category: `public_facts`
- Baseline: status 200, latency 6111.8ms, keyword pass `True`
- CrewAI: status 200, latency 97.4ms, keyword pass `True`
- Baseline answer: A Biblioteca Aurora está aberta de segunda a sexta-feira, das 7h30 às 18h00.
- CrewAI answer: A Biblioteca Aurora atende ao publico de segunda a sexta, das 7h30 as 18h00.

### quando comeca a matricula?

- Slice: `public`
- Category: `public_timeline`
- Baseline: status 200, latency 7091.2ms, keyword pass `False`
- CrewAI: status 200, latency 25.4ms, keyword pass `True`
- Baseline answer: Ah, desculpe se não fui clara antes! As matrículas para o ano letivo de 2026 do Colégio Horizonte começaram em 6 de outubro de 2025. O processo inclui pré-cadastro, visita orientada (se desejar) e a triagem inicial dos documentos. Nosso atendimento comercial continua enquanto houver vagas disponíveis para cada segmento.
- CrewAI answer: O ciclo publico de matricula para 2026 foi aberto em 6 de outubro de 2025, com pre-cadastro, visita orientada opcional e triagem inicial de documentos.

### qual o telefone e o fax?

- Slice: `public`
- Category: `public_contacts`
- Baseline: status 200, latency 159.5ms, keyword pass `False`
- CrewAI: status 200, latency 25.2ms, keyword pass `True`
- Baseline answer: O telefone cadastral atual e +55 11 98888-1001.
Se precisar atualizar esse dado, o caminho mais seguro continua sendo a secretaria escolar, com confirmacao do titular.
- CrewAI answer: Secretaria (telefone): (11) 3333-4200 Hoje a escola nao utiliza fax institucional.

### qual instagram do colegio?

- Slice: `public`
- Category: `public_contacts`
- Baseline: status 200, latency 6625.6ms, keyword pass `True`
- CrewAI: status 200, latency 25.5ms, keyword pass `True`
- Baseline answer: O Instagram oficial do Colégio Horizonte é @colegiohorizonte. Se precisar de mais alguma informação, como nosso site ou outros canais de atendimento, é só me avisar!
- CrewAI answer: O Instagram institucional e @colegiohorizonte.

### quais meus filhos?

- Slice: `protected`
- Category: `protected_identity`
- Baseline: status 200, latency 113.6ms, keyword pass `True`
- CrewAI: status 200, latency 20.2ms, keyword pass `True`
- Baseline answer: Sua conta esta vinculada a Lucas Oliveira e Ana Oliveira. Por aqui eu consigo te ajudar com notas, faltas, proximas provas, matricula, financeiro, boletos, dentro do que sua vinculacao permitir. Se quiser, pode me dizer direto algo como "notas do Lucas" ou "financeiro da Ana".
- CrewAI answer: Sua conta esta vinculada a Lucas Oliveira, Ana Oliveira.

### estou logado como?

- Slice: `protected`
- Category: `protected_identity`
- Baseline: status 200, latency 112.1ms, keyword pass `True`
- CrewAI: status 200, latency 19.2ms, keyword pass `True`
- Baseline answer: Voce esta falando aqui como Maria Oliveira, no perfil de responsavel. Sua conta esta vinculada a Lucas Oliveira e Ana Oliveira. Por aqui eu consigo consultar notas, faltas, proximas provas, matricula, financeiro, boletos, dentro das permissoes dessa vinculacao.
- CrewAI answer: Voce esta autenticado aqui como Maria Oliveira. Sua conta esta vinculada a Lucas Oliveira, Ana Oliveira e pode consultar notas, frequencia, avaliacoes, documentacao e financeiro desses alunos.

### qual situacao de documentacao do Lucas?

- Slice: `protected`
- Category: `protected_admin`
- Baseline: status 200, latency 157.7ms, keyword pass `False`
- CrewAI: status 200, latency 230.8ms, keyword pass `True`
- Baseline answer: Situacao documental de Lucas Oliveira hoje: regular.
- CrewAI answer: A situacao documental de Lucas Oliveira hoje esta regular e completa.

### qual proximo pagamento do Lucas?

- Slice: `protected`
- Category: `protected_financial`
- Baseline: status 200, latency 161.0ms, keyword pass `True`
- CrewAI: status 200, latency 223.3ms, keyword pass `True`
- Baseline answer: Hoje nao encontrei um proximo pagamento pendente de Lucas Oliveira.
- CrewAI answer: No momento, nao vejo fatura em aberto para Lucas Oliveira neste recorte.

### quais as notas do Lucas?

- Slice: `protected`
- Category: `protected_academic`
- Baseline: status 200, latency 177.5ms, keyword pass `True`
- CrewAI: status 200, latency 226.3ms, keyword pass `True`
- Baseline answer: Notas de Lucas Oliveira:
- Biologia - Avaliacao B1: 8.40/10.00
- Biologia - Avaliacao 2026-B1 - BIO: 7.00/10.00
- Biologia - Trabalho B1: 8.10/10.00
- Biologia - Avaliacao B2: 8.60/10.00
- CrewAI answer: As notas mais recentes de Lucas Oliveira incluem Biologia: 8.40/10.00; Biologia: 7.00/10.00; Biologia: 8.10/10.00.

### e como estao as faltas do Lucas?

- Slice: `protected`
- Category: `protected_academic`
- Baseline: status 200, latency 182.6ms, keyword pass `True`
- CrewAI: status 200, latency 224.7ms, keyword pass `True`
- Baseline answer: Frequencia de Lucas Oliveira:
- Biologia: 2 presencas, 0 atrasos, 1 faltas (50 min)
- Educacao Fisica: 1 presencas, 0 atrasos, 1 faltas (50 min)
- Filosofia: 1 presencas, 1 atrasos, 0 faltas (10 min)
- Fisica: 1 presencas, 1 atrasos, 0 faltas (10 min)
- CrewAI answer: Lucas Oliveira tem 3 falta(s) e 3 registro(s) de atraso neste recorte.
