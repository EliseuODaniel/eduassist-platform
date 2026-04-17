# Specialist Model A/B Report

Date: 2026-04-17T06:11:28.969791+00:00

Arm A: `gemma4e4b_local_postfix`
Arm B: `qwen3_4b_instruct_local`

## Automated Summary

| Arm | OK | Keyword pass | Quality | Avg latency | P95 latency |
| --- | --- | --- | --- | --- | --- |
| `gemma4e4b_local_postfix` | `15/15` | `15/15` | `100.0` | `10862.3 ms` | `19554.8 ms` |
| `qwen3_4b_instruct_local` | `15/15` | `8/15` | `84.3` | `3684.1 ms` | `16227.2 ms` |

## Win Count

- quality winner count: `gemma4e4b_local_postfix` `7`, `qwen3_4b_instruct_local` `0`, tie `8`
- latency winner count: `gemma4e4b_local_postfix` `2`, `qwen3_4b_instruct_local` `13`, tie `0`

## Case-by-Case Comparison

### AB01 `public` `identity`

- prompt: `quem é você e como pode me ajudar?`
- quality winner: `tie`
- latency winner: `b`
- `gemma4e4b_local_postfix` quality `100`, latency `25026.6 ms`
- `qwen3_4b_instruct_local` quality `100`, latency `3995.0 ms`
- `gemma4e4b_local_postfix` answer: Voce esta falando com o EduAssist, o assistente institucional do Colegio Horizonte. Eu consigo te orientar por aqui, consultar informacoes da escola e abrir solicitacoes com protocolo. Se precisar, eu tambem te encaminho para secretaria, matricula e atendimento comercial, coordenacao, orientacao educacional, financeiro ou direcao.
- `qwen3_4b_instruct_local` answer: Voce esta falando com o EduAssist, o assistente institucional do Colegio Horizonte. Eu consigo te orientar por aqui, consultar informacoes da escola e abrir solicitacoes com protocolo. Se precisar, eu tambem te encaminho para secretaria, matricula e atendimento comercial, coordenacao, orientacao educacional, financeiro ou direcao.

### AB02 `public` `library_hours`

- prompt: `qual o horário da biblioteca?`
- quality winner: `tie`
- latency winner: `b`
- `gemma4e4b_local_postfix` quality `100`, latency `6677.7 ms`
- `qwen3_4b_instruct_local` quality `100`, latency `4612.8 ms`
- `gemma4e4b_local_postfix` answer: A biblioteca funciona de segunda a sexta, das 7h30 às 18h00.
- `qwen3_4b_instruct_local` answer: A biblioteca funciona das 7h30 as 18h00.

### AB03 `public` `library_hours`

- prompt: `e que horas fecha?`
- quality winner: `a`
- latency winner: `b`
- `gemma4e4b_local_postfix` quality `100`, latency `16343.4 ms`
- `qwen3_4b_instruct_local` quality `60`, latency `2555.2 ms`
- `gemma4e4b_local_postfix` answer: A biblioteca fecha às 18h00.
- `qwen3_4b_instruct_local` answer: Nao tenho base confiavel aqui no EduAssist do Colegio Horizonte para responder esse tema fora do escopo da escola. Se quiser, eu posso ajudar com matricula, calendario, regras publicas, visitas, notas, frequencia ou financeiro.

### AB04 `public` `enrollment`

- prompt: `quais documentos preciso para matrícula?`
- quality winner: `tie`
- latency winner: `b`
- `gemma4e4b_local_postfix` quality `100`, latency `7861.7 ms`
- `qwen3_4b_instruct_local` quality `100`, latency `2285.5 ms`
- `gemma4e4b_local_postfix` answer: Para realizar a matrícula, você precisará apresentar os seguintes documentos: o formulário cadastral preenchido, o documento de identificação do aluno, o CPF do aluno (caso tenha), o histórico escolar, um comprovante de residência atualizado e o documento de identificação do responsável legal.
- `qwen3_4b_instruct_local` answer: Para matrícula, é necessário apresentar: formulário cadastral preenchido, documento de identificação do aluno, CPF do aluno (quando houver), histórico escolar, comprovante de residência atualizado e documento de identificação do responsável legal.

### AB05 `public` `academic_policy`

- prompt: `a escola segue a BNCC?`
- quality winner: `tie`
- latency winner: `b`
- `gemma4e4b_local_postfix` quality `100`, latency `7245.7 ms`
- `qwen3_4b_instruct_local` quality `100`, latency `1255.0 ms`
- `gemma4e4b_local_postfix` answer: Sim, a escola segue a BNCC, e o currículo do Ensino Médio é articulado com projeto de vida, produção textual, cultura digital e aprofundamento acadêmico progressivo.
- `qwen3_4b_instruct_local` answer: Sim, a escola segue a BNCC.

### AB06 `public` `governance_protocol`

- prompt: `sem sair do escopo da escola, explique em linguagem simples como a direção formaliza pedidos de inclusão e por onde eu começo`
- quality winner: `a`
- latency winner: `a`
- `gemma4e4b_local_postfix` quality `100`, latency `9373.9 ms`
- `qwen3_4b_instruct_local` quality `70`, latency `17112.0 ms`
- `gemma4e4b_local_postfix` answer: No material publico do Colegio Horizonte, pedidos de inclusao aparecem como um fluxo institucional que cruza acolhimento pedagogico, acessibilidade, registro formal e escalonamento. A base publica trata inclusao, acessibilidade e protecao do estudante como um mesmo compromisso institucional. # Inclusao e acessibilidade O Colegio Horizonte adota rotinas de atendimento inclusivo com apoio pedagogico, adequacoes de material quando necessario e canal para comunicacao de necessidades especificas. Nos recursos de apoio, a escola cita atendimento educacional especializado quando previsto - mediacao de rotina para estudantes com necessidades especificas - orientacao com equipe pedagogica - priorizacao de acessibilidade em eventos e comunicacoes. O colegio possui normas contra bullying, assedio e uso indevido de imagem. Ha protocolo para ocorrencias leves, contato imediato com responsaveis e acionamento de apoio externo quando necessario. Na base publica do Colegio Horizonte, a trilha institucional fica mais clara quando secretaria, coordenacao, direcao e canais oficiais aparecem como etapas complementares de encaminhamento e protocolo. Na pratica, o protocolo formal costuma seguir esta ordem: secretaria para registrar e orientar, coordenacao para acompanhar o tema pedagogico ou de convivio, e direcao como instancia de escalonamento institucional quando o assunto sai da rotina normal. O envio inicial de documentos pode ocorrer pelo portal institucional, pelo e-mail da secretaria ou presencialmente, conforme o tipo de documento e o grau de sensibilidade da informacao. A diretora geral do Colegio Horizonte e Helena Martins. A lideranca atende familias por agenda institucional. Direcao geral: direcao@colegiohorizonte.edu.br Coordenacao Fundamental II: fundamental2@colegiohorizonte.edu.br Coordenacao Ensino Medio: ensinomedio@colegiohorizonte.edu.br. A diretora participa de encontros institucionais com familias ao longo do ano, especialmente nas reunioes de acolhimento, eventos gerais e marcos bimestrais de acompanhamento da comunidade escolar. Se a familia precisar formalizar um impasse, o proximo passo e abrir o protocolo pelo canal oficial e guardar o registro para o escalonamento ate a direcao. Em linguagem simples, o melhor ponto de partida e levar a demanda ao canal oficial da secretaria ou coordenacao com o contexto do estudante; se o tema exigir formalizacao institucional, o registro segue para protocolo e pode ser escalado ate a direcao.
- `qwen3_4b_instruct_local` answer: Para formalizar um pedido de inclusão, comece entrando em contato com a coordenação pedagógica. Ela é o ponto de entrada para o processo e fará a avaliação necessária, podendo convocar uma reunião com a família para definir o apoio adequado.

### AB07 `public` `out_of_scope`

- prompt: `me ajuda a escolher um filme para ver hoje?`
- quality winner: `tie`
- latency winner: `b`
- `gemma4e4b_local_postfix` quality `100`, latency `6303.0 ms`
- `qwen3_4b_instruct_local` quality `100`, latency `301.3 ms`
- `gemma4e4b_local_postfix` answer: Nao tenho base confiavel aqui no EduAssist do Colegio Horizonte para responder esse tema fora do escopo da escola. Se quiser, eu posso ajudar com matricula, calendario, regras publicas, visitas, notas, frequencia ou financeiro.
- `qwen3_4b_instruct_local` answer: Nao tenho base confiavel aqui no EduAssist do Colegio Horizonte para responder esse tema fora do escopo da escola. Se quiser, eu posso ajudar com matricula, calendario, regras publicas, visitas, notas, frequencia ou financeiro.

### AB08 `public` `external_entity_boundary`

- prompt: `qual horário de fechamento da biblioteca pública da cidade?`
- quality winner: `tie`
- latency winner: `b`
- `gemma4e4b_local_postfix` quality `100`, latency `6461.9 ms`
- `qwen3_4b_instruct_local` quality `100`, latency `267.0 ms`
- `gemma4e4b_local_postfix` answer: No EduAssist do Colegio Horizonte, eu consigo responder apenas sobre servicos e canais da escola. Como sua pergunta fala de uma biblioteca publica externa, esse assunto fica fora do escopo da escola e eu nao tenho base aqui para informar esse horario. Se quiser, eu posso te dizer o horario da biblioteca do colegio.
- `qwen3_4b_instruct_local` answer: No EduAssist do Colegio Horizonte, eu consigo responder apenas sobre servicos e canais da escola. Como sua pergunta fala de uma biblioteca publica externa, esse assunto fica fora do escopo da escola e eu nao tenho base aqui para informar esse horario. Se quiser, eu posso te dizer o horario da biblioteca do colegio.

### AB09 `protected` `academic_followup`

- prompt: `quero um resumo acadêmico do Lucas Oliveira`
- quality winner: `a`
- latency winner: `a`
- `gemma4e4b_local_postfix` quality `100`, latency `15458.4 ms`
- `qwen3_4b_instruct_local` quality `60`, latency `15848.0 ms`
- `gemma4e4b_local_postfix` answer: Resumo academico de Lucas Oliveira:
- Historia: media parcial 6,8
- Fisica: media parcial 5,9
- Matematica: media parcial 7,7
- Portugues: media parcial 8,3
- `qwen3_4b_instruct_local` answer: Não há registros acadêmicos públicos disponíveis sobre Lucas Oliveira. A pesquisa realizada em fontes institucionais e documentos acadêmicos não encontrou informações sobre um resumo acadêmico ou publicações relacionadas a esse nome.

### AB10 `protected` `academic_followup`

- prompt: `agora foque só em matemática`
- quality winner: `a`
- latency winner: `b`
- `gemma4e4b_local_postfix` quality `100`, latency `11100.1 ms`
- `qwen3_4b_instruct_local` quality `35`, latency `2880.8 ms`
- `gemma4e4b_local_postfix` answer: A media parcial de Lucas Oliveira em Matematica e 7,7.
- `qwen3_4b_instruct_local` answer: Nao tenho base confiavel aqui no EduAssist do Colegio Horizonte para responder esse tema fora do escopo da escola. Se quiser, eu posso ajudar com matricula, calendario, regras publicas, visitas, notas, frequencia ou financeiro.

### AB11 `protected` `finance_due`

- prompt: `qual é o próximo vencimento da Ana Oliveira?`
- quality winner: `a`
- latency winner: `b`
- `gemma4e4b_local_postfix` quality `100`, latency `9128.3 ms`
- `qwen3_4b_instruct_local` quality `80`, latency `289.1 ms`
- `gemma4e4b_local_postfix` answer: Hoje nao ha bloqueio financeiro por atraso vencido no recorte da familia.
Resumo financeiro das contas vinculadas:
- Total de faturas em aberto: 2
- Total de faturas vencidas: 0
- Mensalidade: neste recorte, o financeiro mostra 2 cobranca(s) em aberto e 0 vencida(s) nas faturas escolares.
- Taxa: nao apareceu taxa separada neste recorte financeiro das contas vinculadas.
- Atraso: nao ha fatura vencida agora, so acompanhamento dos proximos vencimentos.
- Desconto: nao apareceu desconto separado nas faturas deste recorte; se existir negociacao comercial, ela precisa ser confirmada com o financeiro.
- Ana Oliveira: 2 em aberto, 0 vencidas
  2026-01: vencimento 2026-01-10, status paid, valor 1450.00
  2026-02: vencimento 2026-02-10, status paid, valor 1450.00
Proximo passo: acompanhar os vencimentos mais proximos e manter os comprovantes em dia.
- `qwen3_4b_instruct_local` answer: Consigo verificar o financeiro por aluno, mas aqui ainda faltou dizer qual recorte voce quer. Se a ideia for um panorama da familia, eu separo mensalidade, taxa, atraso e desconto no conjunto. Se voce quiser um aluno especifico, me diga qual deles.

### AB12 `protected` `attendance_compare`

- prompt: `compare a frequência do Lucas e da Ana de forma objetiva`
- quality winner: `a`
- latency winner: `b`
- `gemma4e4b_local_postfix` quality `100`, latency `9174.8 ms`
- `qwen3_4b_instruct_local` quality `80`, latency `506.3 ms`
- `gemma4e4b_local_postfix` answer: Panorama de faltas e frequencia das contas vinculadas:
- Na frequencia de Lucas Oliveira em Tecnologia e Cultura Digital, eu encontrei 6 faltas, 7 atraso(s) e 19 presenca(s) neste recorte.
- Na frequencia de Ana Oliveira em Tecnologia e Cultura Digital, eu encontrei 6 faltas, 9 atraso(s) e 17 presenca(s) neste recorte.
Quem exige maior atencao agora: Ana Oliveira.
Esse alerta pesa mais para Ana Oliveira porque o maior impacto hoje aparece em Ingles, com 6 falta(s), 9 atraso(s), 410 minuto(s) de ausencia.
- `qwen3_4b_instruct_local` answer: Na frequencia de Lucas Oliveira em Tecnologia e Cultura Digital, eu encontrei 6 faltas, 7 atraso(s) e 19 presenca(s) neste recorte.

### AB13 `protected` `attendance_compare`

- prompt: `agora quero apenas a Ana: em quais matérias ela aparece mais exposta?`
- quality winner: `tie`
- latency winner: `b`
- `gemma4e4b_local_postfix` quality `100`, latency `6985.2 ms`
- `qwen3_4b_instruct_local` quality `100`, latency `363.0 ms`
- `gemma4e4b_local_postfix` answer: As disciplinas que mais preocupam academicamente em Ana Oliveira hoje sao:
- Fisica: media parcial 6,4
- Educacao Fisica: media parcial 7,0
- Filosofia: media parcial 7,5
A menor nota parcial neste recorte aparece em Fisica, com media 6,4.
Esses componentes merecem acompanhamento primeiro no proximo ciclo de estudo.
- `qwen3_4b_instruct_local` answer: As disciplinas que mais preocupam academicamente em Ana Oliveira hoje sao:
- Fisica: media parcial 6,4
- Educacao Fisica: media parcial 7,0
- Filosofia: media parcial 7,5
A menor nota parcial neste recorte aparece em Fisica, com media 6,4.
Esses componentes merecem acompanhamento primeiro no proximo ciclo de estudo.

### AB14 `support` `support_handoff`

- prompt: `quero falar com a secretaria sobre bolsa`
- quality winner: `tie`
- latency winner: `b`
- `gemma4e4b_local_postfix` quality `100`, latency `17209.7 ms`
- `qwen3_4b_instruct_local` quality `100`, latency `2659.8 ms`
- `gemma4e4b_local_postfix` answer: Encaminhei sua solicitação para a fila da secretaria. Seu protocolo é ATD-20260417-D541BB71 e o status atual é "queued". Se preferir, você também pode acompanhar por lá pelo WhatsApp oficial: (11) 97500-2040.
- `qwen3_4b_instruct_local` answer: Encaminhei sua solicitacao para a fila de secretaria. Protocolo: ATD-20260417-B76C6960. Status atual: queued. Se preferir, voce tambem pode seguir pelo WhatsApp oficial (11) 97500-2040.

### AB15 `protected` `teacher_schedule`

- prompt: `sou professor, qual é meu horário de hoje e minhas turmas?`
- quality winner: `a`
- latency winner: `b`
- `gemma4e4b_local_postfix` quality `100`, latency `8584.6 ms`
- `qwen3_4b_instruct_local` quality `80`, latency `330.5 ms`
- `gemma4e4b_local_postfix` answer: Horario de hoje e turmas de Fernando Azevedo:
- 1o Ano A - Fisica (2026)
- 1o Ano A - Quimica (2026)
- 1o Ano B - Filosofia (2026)
- 1o Ano B - Historia (2026)
- 2o Ano A - Filosofia (2026)
- 2o Ano A - Fisica (2026)
Turmas de Fernando Azevedo:
- 1o Ano A
- 1o Ano B
- 2o Ano A
- 2o Ano B
- 3o Ano A
- 3o Ano B
- 6o Ano B
- 7o Ano B
- 8o Ano B
- 9o Ano B
- `qwen3_4b_instruct_local` answer: Turmas de Fernando Azevedo:
- 1o Ano A
- 1o Ano B
- 2o Ano A
- 2o Ano B
- 3o Ano A
- 3o Ano B
- 6o Ano B
- 7o Ano B
- 8o Ano B
- 9o Ano B

