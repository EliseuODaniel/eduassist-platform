# Two-Stack Shadow Comparison Report

## Summary

- Total prompts: 12
- `public`: baseline ok 5/5, CrewAI ok 5/5, baseline keyword pass 5/5, CrewAI keyword pass 5/5, quality 100.0 vs 100.0, latency 7330.2ms vs 26.5ms
- `protected`: baseline ok 7/7, CrewAI ok 7/7, baseline keyword pass 7/7, CrewAI keyword pass 7/7, quality 100.0 vs 100.0, latency 154.4ms vs 139.9ms

## By Category

- `public_facts`: baseline ok 1/1, CrewAI ok 1/1, baseline keyword pass 1/1, CrewAI keyword pass 1/1, quality 100.0 vs 100.0
- `public_timeline`: baseline ok 1/1, CrewAI ok 1/1, baseline keyword pass 1/1, CrewAI keyword pass 1/1, quality 100.0 vs 100.0
- `public_contacts`: baseline ok 2/2, CrewAI ok 2/2, baseline keyword pass 2/2, CrewAI keyword pass 2/2, quality 100.0 vs 100.0
- `public_features`: baseline ok 1/1, CrewAI ok 1/1, baseline keyword pass 1/1, CrewAI keyword pass 1/1, quality 100.0 vs 100.0
- `protected_identity`: baseline ok 2/2, CrewAI ok 2/2, baseline keyword pass 2/2, CrewAI keyword pass 2/2, quality 100.0 vs 100.0
- `protected_admin`: baseline ok 1/1, CrewAI ok 1/1, baseline keyword pass 1/1, CrewAI keyword pass 1/1, quality 100.0 vs 100.0
- `protected_financial`: baseline ok 1/1, CrewAI ok 1/1, baseline keyword pass 1/1, CrewAI keyword pass 1/1, quality 100.0 vs 100.0
- `protected_academic`: baseline ok 2/2, CrewAI ok 2/2, baseline keyword pass 2/2, CrewAI keyword pass 2/2, quality 100.0 vs 100.0
- `protected_clarify_repair`: baseline ok 1/1, CrewAI ok 1/1, baseline keyword pass 1/1, CrewAI keyword pass 1/1, quality 100.0 vs 100.0

## Error Types

- `baseline`: nenhum
- `crewai`: nenhum

## By Thread


## Prompt Results

### qual o horario da biblioteca?

- Slice: `public`
- Category: `public_facts`
- Baseline: status 200, latency 7073.1ms, keyword pass `True`, quality `100`
- CrewAI: status 200, latency 29.9ms, keyword pass `True`, quality `100`
- Baseline answer: Que bom que você quer usar a nossa biblioteca! A Biblioteca Aurora funciona de segunda a sexta-feira, das 7h30 às 18h00. Estamos te esperando!
- CrewAI answer: A Biblioteca Aurora atende ao publico de segunda a sexta, das 7h30 as 18h00.

### quando comeca a matricula?

- Slice: `public`
- Category: `public_timeline`
- Baseline: status 200, latency 7489.0ms, keyword pass `True`, quality `100`
- CrewAI: status 200, latency 24.5ms, keyword pass `True`, quality `100`
- Baseline answer: Olá! As matrículas para o ano letivo de 2026 do Colégio Horizonte começaram em 6 de outubro de 2025. O processo inclui pré-cadastro, visita orientada (opcional) e uma triagem inicial de documentos. Nosso atendimento comercial segue enquanto houver vagas disponíveis para cada segmento.
- CrewAI answer: O ciclo publico de matricula para 2026 foi aberto em 6 de outubro de 2025, com pre-cadastro, visita orientada opcional e triagem inicial de documentos.

### qual o telefone e o fax?

- Slice: `public`
- Category: `public_contacts`
- Baseline: status 200, latency 7061.0ms, keyword pass `True`, quality `100`
- CrewAI: status 200, latency 26.9ms, keyword pass `True`, quality `100`
- Baseline answer: Olá! O telefone principal do Colégio Horizonte é o da secretaria, (11) 3333-4200. No momento, não utilizamos fax, então não temos um número divulgado para esse serviço.
- CrewAI answer: Secretaria (telefone): (11) 3333-4200 Hoje a escola nao utiliza fax institucional.

### qual instagram do colegio?

- Slice: `public`
- Category: `public_contacts`
- Baseline: status 200, latency 6833.7ms, keyword pass `True`, quality `100`
- CrewAI: status 200, latency 25.6ms, keyword pass `True`, quality `100`
- Baseline answer: O Instagram oficial do Colégio Horizonte é @colegiohorizonte. Se precisar de mais alguma informação, como nosso site ou outros canais de atendimento, é só me avisar!
- CrewAI answer: O Instagram institucional e @colegiohorizonte.

### quais aulas complementares essa escola oferece?

- Slice: `public`
- Category: `public_features`
- Baseline: status 200, latency 8194.2ms, keyword pass `True`, quality `100`
- CrewAI: status 200, latency 25.4ms, keyword pass `True`, quality `100`
- Baseline answer: Que bom que você perguntou! No Colégio Horizonte, temos uma variedade de aulas complementares para enriquecer o aprendizado dos nossos alunos. Para o Ensino Fundamental II, oferecemos oficinas, plantões, esportes e estudo orientado em dias alternados. Já para o Ensino Médio, temos trilhas eletivas, monitorias e laboratórios a partir das 14h. Além disso, para todos, há estudo orientado, almoço, oficinas, esportes como futsal e vôlei escolar, e o uso do nosso Espaço Maker e Laboratório de Ciências.
- CrewAI answer: Hoje a escola divulga atividades e espacos complementares como Biblioteca Aurora, Espaco Maker, futsal, volei escolar. Se quiser, eu tambem posso detalhar Biblioteca Aurora, Laboratorio de Ciencias, Espaco Maker, Quadra Poliesportiva Coberta.

### quais meus filhos?

- Slice: `protected`
- Category: `protected_identity`
- Baseline: status 200, latency 115.5ms, keyword pass `True`, quality `100`
- CrewAI: status 200, latency 19.7ms, keyword pass `True`, quality `100`
- Baseline answer: Os alunos vinculados a esta conta hoje sao Lucas Oliveira e Ana Oliveira. Eu posso consultar notas, faltas, proximas provas, matricula, financeiro, boletos, dentro do que sua vinculacao permitir. Se quiser, me diga direto algo como "notas do Lucas" ou "financeiro da Ana".
- CrewAI answer: Sua conta esta vinculada a Lucas Oliveira, Ana Oliveira.

### estou logado como?

- Slice: `protected`
- Category: `protected_identity`
- Baseline: status 200, latency 118.1ms, keyword pass `True`, quality `100`
- CrewAI: status 200, latency 19.7ms, keyword pass `True`, quality `100`
- Baseline answer: Voce esta falando aqui como Maria Oliveira, no perfil de responsavel. Sua conta esta vinculada a Lucas Oliveira e Ana Oliveira. Por aqui eu consigo consultar notas, faltas, proximas provas, matricula, financeiro, boletos, dentro das permissoes dessa vinculacao.
- CrewAI answer: Voce esta autenticado aqui como Maria Oliveira. Sua conta esta vinculada a Lucas Oliveira, Ana Oliveira e pode consultar notas, frequencia, avaliacoes, documentacao e financeiro desses alunos.

### qual situacao de documentacao do Lucas?

- Slice: `protected`
- Category: `protected_admin`
- Baseline: status 200, latency 163.1ms, keyword pass `True`, quality `100`
- CrewAI: status 200, latency 224.0ms, keyword pass `True`, quality `100`
- Baseline answer: Situacao documental de Lucas Oliveira hoje: regular.
- CrewAI answer: A situacao documental de Lucas Oliveira hoje esta regular e completa.

### qual proximo pagamento do Lucas?

- Slice: `protected`
- Category: `protected_financial`
- Baseline: status 200, latency 169.6ms, keyword pass `True`, quality `100`
- CrewAI: status 200, latency 230.4ms, keyword pass `True`, quality `100`
- Baseline answer: Hoje nao encontrei um proximo pagamento pendente de Lucas Oliveira.
- CrewAI answer: No momento, nao vejo fatura em aberto para Lucas Oliveira neste recorte.

### quais as notas do Lucas?

- Slice: `protected`
- Category: `protected_academic`
- Baseline: status 200, latency 190.9ms, keyword pass `True`, quality `100`
- CrewAI: status 200, latency 235.0ms, keyword pass `True`, quality `100`
- Baseline answer: Notas de Lucas Oliveira:
- Biologia - Avaliacao B1: 8.40/10.00
- Biologia - Avaliacao 2026-B1 - BIO: 7.00/10.00
- Biologia - Trabalho B1: 8.10/10.00
- Biologia - Avaliacao B2: 8.60/10.00
- CrewAI answer: As notas mais recentes de Lucas Oliveira incluem Biologia: 8.40/10.00; Biologia: 7.00/10.00; Biologia: 8.10/10.00.

### e como estao as faltas do Lucas?

- Slice: `protected`
- Category: `protected_academic`
- Baseline: status 200, latency 183.1ms, keyword pass `True`, quality `100`
- CrewAI: status 200, latency 230.9ms, keyword pass `True`, quality `100`
- Baseline answer: Frequencia de Lucas Oliveira:
- Biologia: 2 presencas, 0 atrasos, 1 faltas (50 min)
- Educacao Fisica: 1 presencas, 0 atrasos, 1 faltas (50 min)
- Filosofia: 1 presencas, 1 atrasos, 0 faltas (10 min)
- Fisica: 1 presencas, 1 atrasos, 0 faltas (10 min)
- CrewAI answer: Lucas Oliveira tem 3 falta(s) e 3 registro(s) de atraso neste recorte.

### lucas eu falei

- Slice: `protected`
- Category: `protected_clarify_repair`
- Baseline: status 200, latency 140.8ms, keyword pass `True`, quality `100`
- CrewAI: status 200, latency 19.9ms, keyword pass `True`, quality `100`
- Baseline answer: Perfeito, seguimos com Lucas Oliveira. Posso te ajudar com notas, faltas, proximas provas, matricula, financeiro, boletos. Se quiser, ja me diga o que voce quer ver primeiro.
- CrewAI answer: Perfeito, seguimos com Lucas Oliveira. Posso te ajudar com notas, faltas, proximas provas, documentacao, matricula e financeiro.
