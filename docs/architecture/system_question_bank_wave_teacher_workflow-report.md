# Five-Path Chatbot Comparison Report

Date: 2026-04-01T04:57:41.162528+00:00

Dataset: `tests/evals/datasets/system_question_bank_wave_teacher_workflow.json`

Run prefix: `debug:five-path:20260401T045541Z`

## Stack Summary

| Stack | OK | Keyword pass | Quality | Avg latency |
| --- | --- | --- | --- | --- |
| `langgraph` | `16/16` | `16/16` | `100.0` | `1992.9 ms` |
| `python_functions` | `16/16` | `16/16` | `99.4` | `579.7 ms` |
| `llamaindex` | `16/16` | `16/16` | `99.4` | `484.5 ms` |
| `specialist_supervisor` | `16/16` | `16/16` | `96.9` | `4354.7 ms` |

## By Slice

- `protected`
  - `langgraph`: ok 7/7, keyword pass 7/7, quality 100.0, latency 2700.5ms
  - `python_functions`: ok 7/7, keyword pass 7/7, quality 100.0, latency 1091.7ms
  - `llamaindex`: ok 7/7, keyword pass 7/7, quality 100.0, latency 869.4ms
  - `specialist_supervisor`: ok 7/7, keyword pass 7/7, quality 98.6, latency 4328.3ms
- `public`
  - `langgraph`: ok 1/1, keyword pass 1/1, quality 100.0, latency 6050.7ms
  - `python_functions`: ok 1/1, keyword pass 1/1, quality 100.0, latency 190.7ms
  - `llamaindex`: ok 1/1, keyword pass 1/1, quality 100.0, latency 245.3ms
  - `specialist_supervisor`: ok 1/1, keyword pass 1/1, quality 100.0, latency 5042.4ms
- `workflow`
  - `langgraph`: ok 8/8, keyword pass 8/8, quality 100.0, latency 866.6ms
  - `python_functions`: ok 8/8, keyword pass 8/8, quality 98.8, latency 180.3ms
  - `llamaindex`: ok 8/8, keyword pass 8/8, quality 98.8, latency 177.6ms
  - `specialist_supervisor`: ok 8/8, keyword pass 8/8, quality 95.0, latency 4291.7ms

## Error Types

- `langgraph`: nenhum
- `python_functions`: repetitive_reply=1
- `llamaindex`: repetitive_reply=1
- `specialist_supervisor`: repetitive_reply=5

## Prompt Results

### Quais turmas e disciplinas eu tenho neste ano?

- Slice: `protected`
- Thread: `system_bank:professor_e_grade_docente:Q065` turn `1`
- `langgraph`: status 200, latency 309.9ms, keyword pass `True`, quality `100`, reason `dados estruturados devem passar por service deterministico`
  answer: Se voce ja e professor do Colegio Horizonte, o acesso docente depende da vinculacao da conta institucional correta no Telegram. Nesta conta atual eu nao identifiquei um perfil docente ativo. Quando a vinculacao de professor estiver correta, por aqui eu consigo consultar horario, turmas e disciplinas; a situacao individual dos alunos continua fora do escopo deste canal nesta etapa.
- `python_functions`: status 200, latency 139.4ms, keyword pass `True`, quality `100`, reason `python_functions_native_structured:academic`
  answer: Se voce ja e professor do Colegio Horizonte, o acesso docente depende da vinculacao da conta institucional correta no Telegram. Nesta conta atual eu nao identifiquei um perfil docente ativo. Quando a vinculacao de professor estiver correta, por aqui eu consigo consultar horario, turmas e disciplinas; a situacao individual dos alunos continua fora do escopo deste canal nesta etapa.
- `llamaindex`: status 200, latency 140.3ms, keyword pass `True`, quality `100`, reason `dados estruturados devem passar por service deterministico`
  answer: Se voce ja e professor do Colegio Horizonte, o acesso docente depende da vinculacao da conta institucional correta no Telegram. Nesta conta atual eu nao identifiquei um perfil docente ativo. Quando a vinculacao de professor estiver correta, por aqui eu consigo consultar horario, turmas e disciplinas; a situacao individual dos alunos continua fora do escopo deste canal nesta etapa.
- `specialist_supervisor`: status 200, latency 5045.4ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_strict_safe_fallback`
  answer: Nao consegui consolidar essa resposta premium com seguranca agora. Se quiser, me diga exatamente se voce quer ver notas, frequencia, documentacao, financeiro ou status de protocolo.

### Qual e a minha grade docente completa?

- Slice: `protected`
- Thread: `system_bank:professor_e_grade_docente:Q066` turn `1`
- `langgraph`: status 200, latency 1974.8ms, keyword pass `True`, quality `100`, reason `a intencao esta ambigua e exige clarificacao antes de recuperar contexto`
  answer: Para acessar sua grade docente completa, que inclui informações detalhadas sobre seus professores e horários, é necessário que você faça login no nosso portal do aluno. Lá, você encontrará todas as informações personalizadas.

Se precisar de ajuda para acessar o portal ou tiver alguma dúvida, por favor, me avise!
- `python_functions`: status 200, latency 158.1ms, keyword pass `True`, quality `100`, reason `a intencao esta ambigua e exige clarificacao antes de recuperar contexto`
  answer: Posso ajudar com informacoes publicas da escola, como calendario, matricula, documentos exigidos e regras de atendimento digital. Se quiser, pergunte por exemplo: "quais documentos preciso para a matricula?" ou "quando acontece a reuniao de pais?".
- `llamaindex`: status 200, latency 163.2ms, keyword pass `True`, quality `100`, reason `a intencao esta ambigua e exige clarificacao antes de recuperar contexto`
  answer: Posso ajudar com informacoes publicas da escola, como calendario, matricula, documentos exigidos e regras de atendimento digital. Se quiser, pergunte por exemplo: "quais documentos preciso para a matricula?" ou "quando acontece a reuniao de pais?".
- `specialist_supervisor`: status 200, latency 5038.9ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_strict_safe_fallback`
  answer: Nao consegui consolidar essa resposta premium com seguranca agora. Se quiser, me diga exatamente se voce quer ver notas, frequencia, documentacao, financeiro ou status de protocolo.

### E so do ensino medio?

- Slice: `protected`
- Thread: `system_bank:professor_e_grade_docente:Q066` turn `2`
- `langgraph`: status 200, latency 3841.5ms, keyword pass `True`, quality `100`, reason `fato institucional canonico deve vir de fonte estruturada`
  answer: Olá! Para que eu possa te ajudar melhor, você poderia, por favor, reformular sua pergunta usando termos como "matrícula", "calendário", "secretaria" ou "atendimento"? Assim consigo buscar a informação que você precisa com mais precisão.
- `python_functions`: status 200, latency 161.3ms, keyword pass `True`, quality `100`, reason `python_functions_native_structured:institution`
  answer: Ainda nao encontrei uma resposta suficientemente suportada na base publica. Tente reformular a pergunta com termos como matricula, calendario, secretaria ou atendimento.
- `llamaindex`: status 200, latency 213.5ms, keyword pass `True`, quality `100`, reason `fato institucional canonico deve vir de fonte estruturada`
  answer: Ainda nao encontrei uma resposta suficientemente suportada na base publica. Tente reformular a pergunta com termos como matricula, calendario, secretaria ou atendimento.
- `specialist_supervisor`: status 200, latency 5037.5ms, keyword pass `True`, quality `90`, reason `specialist_supervisor_strict_safe_fallback`
  errors: repetitive_reply
  answer: Nao consegui consolidar essa resposta premium com seguranca agora. Se quiser, me diga exatamente se voce quer ver notas, frequencia, documentacao, financeiro ou status de protocolo.

### Quais turmas eu atendo em Filosofia e em que classes?

- Slice: `protected`
- Thread: `system_bank:professor_e_grade_docente:Q068` turn `1`
- `langgraph`: status 200, latency 138.1ms, keyword pass `True`, quality `100`, reason `dados estruturados devem passar por service deterministico`
  answer: Se voce ja e professor do Colegio Horizonte, o acesso docente depende da vinculacao da conta institucional correta no Telegram. Nesta conta atual eu nao identifiquei um perfil docente ativo. Quando a vinculacao de professor estiver correta, por aqui eu consigo consultar horario, turmas e disciplinas; a situacao individual dos alunos continua fora do escopo deste canal nesta etapa.
- `python_functions`: status 200, latency 139.5ms, keyword pass `True`, quality `100`, reason `python_functions_native_structured:academic`
  answer: Se voce ja e professor do Colegio Horizonte, o acesso docente depende da vinculacao da conta institucional correta no Telegram. Nesta conta atual eu nao identifiquei um perfil docente ativo. Quando a vinculacao de professor estiver correta, por aqui eu consigo consultar horario, turmas e disciplinas; a situacao individual dos alunos continua fora do escopo deste canal nesta etapa.
- `llamaindex`: status 200, latency 120.7ms, keyword pass `True`, quality `100`, reason `dados estruturados devem passar por service deterministico`
  answer: Se voce ja e professor do Colegio Horizonte, o acesso docente depende da vinculacao da conta institucional correta no Telegram. Nesta conta atual eu nao identifiquei um perfil docente ativo. Quando a vinculacao de professor estiver correta, por aqui eu consigo consultar horario, turmas e disciplinas; a situacao individual dos alunos continua fora do escopo deste canal nesta etapa.
- `specialist_supervisor`: status 200, latency 5037.7ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_strict_safe_fallback`
  answer: Nao consegui consolidar essa resposta premium com seguranca agora. Se quiser, me diga exatamente se voce quer ver notas, frequencia, documentacao, financeiro ou status de protocolo.

### Resuma minha rotina docente junto com orientacoes publicas sobre calendario e comunicacao escolar.

- Slice: `protected`
- Thread: `system_bank:professor_e_grade_docente:Q069` turn `1`
- `langgraph`: status 200, latency 6032.3ms, keyword pass `True`, quality `100`, reason `planejamento semantico publico encontrou um ato estruturado mais adequado ao turno`
  answer: Para acessar sua rotina docente completa, incluindo horários, turmas e disciplinas, é importante que sua conta institucional do Telegram esteja vinculada corretamente. No momento, não identifiquei um perfil docente ativo com esta conta. Assim que a vinculação for confirmada, terei prazer em ajudar com essas informações!
- `python_functions`: status 200, latency 5859.7ms, keyword pass `True`, quality `100`, reason `python_functions_native_public_retrieval`
  answer: Olá! Para resumir sua rotina docente e as orientações públicas, posso dizer que o Colégio Horizonte organiza a rotina acadêmica por turnos, combinando acolhimento, aulas regulares, intervalos, uso de espaços pedagógicos e fechamento com orientações de rotina.

Em relação ao calendário e à comunicação, o calendário escolar é publicado com antecedência e a comunicação digital é centralizada no portal e no bot oficial. Além disso, a escola oferece apoio de orientação educacional, laboratórios e espaços de estudo acompanhados, e atendimento educacional especializado quando previsto.

Fontes:
- Apresentacao Institucional do Colegio Horizonte (v2026.2)
- Rotina e Vida Escolar (v2026.2)
- Inclusao, Acessibilidade e Seguranca (v2026.2)
- `llamaindex`: status 200, latency 4244.0ms, keyword pass `True`, quality `100`, reason `retrieval hibrido e o caminho padrao para faq e documentos`
  answer: Olá! Para resumir sua rotina docente e as orientações públicas, posso dizer que o dia escolar no Colégio Horizonte é organizado por turnos, combinando acolhimento, aulas regulares, intervalos, uso de espaços pedagógicos e fechamento com orientações de rotina.

Em relação às orientações públicas, nosso calendário escolar é publicado com antecedência e a comunicação digital é centralizada no portal e no nosso bot oficial. Além disso, a escola oferece apoio de orientação educacional, laboratórios e espaços de estudo acompanhados, e uma biblioteca com atendimento ampliado.

Se precisar de mais detalhes sobre algum ponto, é só me dizer!

Fontes:
- Apresentacao Institucional do Colegio Horizonte (v2026.2)
- Rotina e Vida Escolar (v2026.2)
- Inclusao, Acessibilidade e Seguranca (v2026.2)
- `specialist_supervisor`: status 200, latency 5037.5ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_strict_safe_fallback`
  answer: Nao consegui consolidar essa resposta premium com seguranca agora. Se quiser, me diga exatamente se voce quer ver notas, frequencia, documentacao, financeiro ou status de protocolo.

### Sou professor de Filosofia e quero trabalhar ai; como faco para entrar em contato?

- Slice: `public`
- Thread: `system_bank:professor_e_grade_docente:Q070` turn `1`
- `langgraph`: status 200, latency 6050.7ms, keyword pass `True`, quality `100`, reason `fato institucional canonico deve vir de fonte estruturada`
  answer: Olá! Entendo seu interesse em fazer parte da nossa equipe. No momento, não temos um processo de contato direto para envio de currículos ou candidaturas abertas na base pública. Sugiro que você fique atento ao nosso site oficial e redes sociais, onde divulgamos futuras oportunidades de trabalho.
- `python_functions`: status 200, latency 190.7ms, keyword pass `True`, quality `100`, reason `python_functions_native_structured:institution`
  answer: Ainda nao encontrei uma resposta suficientemente suportada na base publica. Tente reformular a pergunta com termos como matricula, calendario, secretaria ou atendimento.
- `llamaindex`: status 200, latency 245.3ms, keyword pass `True`, quality `100`, reason `fato institucional canonico deve vir de fonte estruturada`
  answer: Ainda nao encontrei uma resposta suficientemente suportada na base publica. Tente reformular a pergunta com termos como matricula, calendario, secretaria ou atendimento.
- `specialist_supervisor`: status 200, latency 5042.4ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_strict_safe_fallback`
  answer: Nao consegui concluir essa resposta premium agora. Se quiser, reformule em uma frase mais direta ou repita em instantes.

### Me diga o nome e o telefone do professor de Educacao Fisica.

- Slice: `protected`
- Thread: `system_bank:professor_e_grade_docente:Q071` turn `1`
- `langgraph`: status 200, latency 156.4ms, keyword pass `True`, quality `100`, reason `status administrativo autenticado exige service deterministico`
  answer: Essa consulta depende de autenticacao e vinculo da sua conta no Telegram. Use o portal da escola para gerar o codigo de vinculacao e depois envie o comando `/start link_<codigo>` ao bot.
- `python_functions`: status 200, latency 137.8ms, keyword pass `True`, quality `100`, reason `python_functions_native_structured:institution`
  answer: Essa consulta depende de autenticacao e vinculo da sua conta no Telegram. Use o portal da escola para gerar o codigo de vinculacao e depois envie o comando `/start link_<codigo>` ao bot.
- `llamaindex`: status 200, latency 133.6ms, keyword pass `True`, quality `100`, reason `status administrativo autenticado exige service deterministico`
  answer: Essa consulta depende de autenticacao e vinculo da sua conta no Telegram. Use o portal da escola para gerar o codigo de vinculacao e depois envie o comando `/start link_<codigo>` ao bot.
- `specialist_supervisor`: status 200, latency 5038.7ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_strict_safe_fallback`
  answer: Nao consegui consolidar essa resposta premium com seguranca agora. Se quiser, me diga exatamente se voce quer ver notas, frequencia, documentacao, financeiro ou status de protocolo.

### Gere um resumo enxuto da minha alocacao para eu revisar antes da reuniao pedagogica.

- Slice: `protected`
- Thread: `system_bank:professor_e_grade_docente:Q072` turn `1`
- `langgraph`: status 200, latency 6450.6ms, keyword pass `True`, quality `100`, reason `planejamento semantico publico encontrou um ato estruturado mais adequado ao turno`
  answer: Para que eu possa te ajudar com a sua alocação, preciso que você se identifique. Por favor, faça login ou me informe seu nome completo e número de matrícula.
- `python_functions`: status 200, latency 1045.9ms, keyword pass `True`, quality `100`, reason `python_functions_native_public_retrieval`
  answer: A base publica atual nao sustenta com seguranca todos os pontos dessa pergunta, especialmente sobre: alocacao, antes, enxuto, gere, resumo, reuniao, revisar. Para evitar uma orientacao incorreta, prefiro nao inferir alem do que esta documentado. Se quiser, eu posso responder apenas o que esta explicitamente registrado na base atual.

Fontes:
- Politica de Avaliacao, Recuperacao e Promocao (v2026.3)
- Agenda de Avaliacoes, Recuperacoes e Simulados 2026 (v2026.3)
- Proposta Pedagogica (v2026.2)
- `llamaindex`: status 200, latency 1070.6ms, keyword pass `True`, quality `100`, reason `retrieval hibrido e o caminho padrao para faq e documentos`
  answer: A base publica atual nao sustenta com seguranca todos os pontos dessa pergunta, especialmente sobre: alocacao, antes, enxuto, gere, resumo, reuniao, revisar. Para evitar uma orientacao incorreta, prefiro nao inferir alem do que esta documentado. Se quiser, eu posso responder apenas o que esta explicitamente registrado na base atual.

Fontes:
- Politica de Avaliacao, Recuperacao e Promocao (v2026.3)
- Agenda de Avaliacoes, Recuperacoes e Simulados 2026 (v2026.3)
- Proposta Pedagogica (v2026.2)
- `specialist_supervisor`: status 200, latency 62.7ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_strict_safe_fallback`
  answer: Nao consegui consolidar essa resposta premium com seguranca agora. Se quiser, me diga exatamente se voce quer ver notas, frequencia, documentacao, financeiro ou status de protocolo.

### Quero agendar uma visita para conhecer a escola.

- Slice: `workflow`
- Thread: `system_bank:workflow_protocolos_visitas_e_handoff:Q073` turn `1`
- `langgraph`: status 200, latency 243.7ms, keyword pass `True`, quality `100`, reason `consulta publica de navegacao e canais foi resgatada do dominio support`
  answer: Posso orientar sobre visitas ao Colegio Horizonte, mas nao consegui registrar o pedido agora. Tente novamente em instantes ou use o canal de admissions.
- `python_functions`: status 200, latency 179.0ms, keyword pass `True`, quality `100`, reason `python_functions_native_structured:support`
  answer: Posso orientar sobre visitas ao Colegio Horizonte, mas nao consegui registrar o pedido agora. Tente novamente em instantes ou use o canal de admissions.
- `llamaindex`: status 200, latency 188.5ms, keyword pass `True`, quality `100`, reason `consulta publica de navegacao e canais foi resgatada do dominio support`
  answer: Posso orientar sobre visitas ao Colegio Horizonte, mas nao consegui registrar o pedido agora. Tente novamente em instantes ou use o canal de admissions.
- `specialist_supervisor`: status 200, latency 50.8ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_strict_safe_fallback`
  answer: Nao consegui consolidar essa resposta premium com seguranca agora. Se quiser, me diga exatamente se voce quer ver notas, frequencia, documentacao, financeiro ou status de protocolo.

### Pode ser na quinta a tarde?

- Slice: `workflow`
- Thread: `system_bank:workflow_protocolos_visitas_e_handoff:Q073` turn `2`
- `langgraph`: status 200, latency 1923.4ms, keyword pass `True`, quality `100`, reason `a intencao esta ambigua e exige clarificacao antes de recuperar contexto`
  answer: Para que eu possa te ajudar melhor, preciso de um pouco mais de contexto. Você poderia me dizer a que "quinta à tarde" você se refere? Assim consigo verificar a disponibilidade ou a informação que você precisa.
- `python_functions`: status 200, latency 182.1ms, keyword pass `True`, quality `100`, reason `a intencao esta ambigua e exige clarificacao antes de recuperar contexto`
  answer: Posso ajudar com informacoes publicas da escola, como calendario, matricula, documentos exigidos e regras de atendimento digital. Se quiser, pergunte por exemplo: "quais documentos preciso para a matricula?" ou "quando acontece a reuniao de pais?".
- `llamaindex`: status 200, latency 167.9ms, keyword pass `True`, quality `100`, reason `a intencao esta ambigua e exige clarificacao antes de recuperar contexto`
  answer: Posso ajudar com informacoes publicas da escola, como calendario, matricula, documentos exigidos e regras de atendimento digital. Se quiser, pergunte por exemplo: "quais documentos preciso para a matricula?" ou "quando acontece a reuniao de pais?".
- `specialist_supervisor`: status 200, latency 4033.9ms, keyword pass `True`, quality `90`, reason `specialist_supervisor_strict_safe_fallback`
  errors: repetitive_reply
  answer: Nao consegui consolidar essa resposta premium com seguranca agora. Se quiser, me diga exatamente se voce quer ver notas, frequencia, documentacao, financeiro ou status de protocolo.

### Qual e o protocolo dessa visita?

- Slice: `workflow`
- Thread: `system_bank:workflow_protocolos_visitas_e_handoff:Q073` turn `3`
- `langgraph`: status 200, latency 152.7ms, keyword pass `True`, quality `100`, reason `consulta publica de navegacao e canais foi resgatada do dominio support`
  answer: Posso orientar sobre protocolos institucionais, mas nao consegui registrar a solicitacao agora. Tente novamente em instantes ou use a secretaria.
- `python_functions`: status 200, latency 202.0ms, keyword pass `True`, quality `100`, reason `python_functions_native_structured:support`
  answer: Posso orientar sobre protocolos institucionais, mas nao consegui registrar a solicitacao agora. Tente novamente em instantes ou use a secretaria.
- `llamaindex`: status 200, latency 169.3ms, keyword pass `True`, quality `100`, reason `consulta publica de navegacao e canais foi resgatada do dominio support`
  answer: Posso orientar sobre protocolos institucionais, mas nao consegui registrar a solicitacao agora. Tente novamente em instantes ou use a secretaria.
- `specialist_supervisor`: status 200, latency 5042.4ms, keyword pass `True`, quality `90`, reason `specialist_supervisor_strict_safe_fallback`
  errors: repetitive_reply
  answer: Nao consegui consolidar essa resposta premium com seguranca agora. Se quiser, me diga exatamente se voce quer ver notas, frequencia, documentacao, financeiro ou status de protocolo.

### Preciso remarcar para a semana que vem.

- Slice: `workflow`
- Thread: `system_bank:workflow_protocolos_visitas_e_handoff:Q073` turn `4`
- `langgraph`: status 200, latency 2126.7ms, keyword pass `True`, quality `100`, reason `a intencao esta ambigua e exige clarificacao antes de recuperar contexto`
  answer: Olá! Para que eu possa te ajudar com a remarcação, preciso saber qual é o compromisso ou evento que você deseja reagendar. Assim, consigo verificar as opções e te orientar da melhor forma.
- `python_functions`: status 200, latency 174.2ms, keyword pass `True`, quality `100`, reason `a intencao esta ambigua e exige clarificacao antes de recuperar contexto`
  answer: Posso ajudar com informacoes publicas da escola, como calendario, matricula, documentos exigidos e regras de atendimento digital. Se quiser, pergunte por exemplo: "quais documentos preciso para a matricula?" ou "quando acontece a reuniao de pais?".
- `llamaindex`: status 200, latency 169.4ms, keyword pass `True`, quality `100`, reason `a intencao esta ambigua e exige clarificacao antes de recuperar contexto`
  answer: Posso ajudar com informacoes publicas da escola, como calendario, matricula, documentos exigidos e regras de atendimento digital. Se quiser, pergunte por exemplo: "quais documentos preciso para a matricula?" ou "quando acontece a reuniao de pais?".
- `specialist_supervisor`: status 200, latency 5039.3ms, keyword pass `True`, quality `90`, reason `specialist_supervisor_strict_safe_fallback`
  errors: repetitive_reply
  answer: Nao consegui consolidar essa resposta premium com seguranca agora. Se quiser, me diga exatamente se voce quer ver notas, frequencia, documentacao, financeiro ou status de protocolo.

### Agora cancela, por favor.

- Slice: `workflow`
- Thread: `system_bank:workflow_protocolos_visitas_e_handoff:Q073` turn `5`
- `langgraph`: status 200, latency 1975.3ms, keyword pass `True`, quality `100`, reason `a intencao esta ambigua e exige clarificacao antes de recuperar contexto`
  answer: Para que eu possa ajudar com o cancelamento, preciso saber a qual serviço ou solicitação você se refere. Poderia me dar mais detalhes, por favor?
- `python_functions`: status 200, latency 257.2ms, keyword pass `True`, quality `90`, reason `a intencao esta ambigua e exige clarificacao antes de recuperar contexto`
  errors: repetitive_reply
  answer: Posso ajudar com informacoes publicas da escola, como calendario, matricula, documentos exigidos e regras de atendimento digital. Se quiser, pergunte por exemplo: "quais documentos preciso para a matricula?" ou "quando acontece a reuniao de pais?".
- `llamaindex`: status 200, latency 210.4ms, keyword pass `True`, quality `90`, reason `a intencao esta ambigua e exige clarificacao antes de recuperar contexto`
  errors: repetitive_reply
  answer: Posso ajudar com informacoes publicas da escola, como calendario, matricula, documentos exigidos e regras de atendimento digital. Se quiser, pergunte por exemplo: "quais documentos preciso para a matricula?" ou "quando acontece a reuniao de pais?".
- `specialist_supervisor`: status 200, latency 5041.7ms, keyword pass `True`, quality `90`, reason `specialist_supervisor_strict_safe_fallback`
  errors: repetitive_reply
  answer: Nao consegui consolidar essa resposta premium com seguranca agora. Se quiser, me diga exatamente se voce quer ver notas, frequencia, documentacao, financeiro ou status de protocolo.

### Preciso emitir documentos finais e concluir a transferencia do Diego.

- Slice: `workflow`
- Thread: `system_bank:workflow_protocolos_visitas_e_handoff:Q078` turn `1`
- `langgraph`: status 200, latency 158.9ms, keyword pass `True`, quality `100`, reason `status administrativo autenticado exige service deterministico`
  answer: Essa consulta depende de autenticacao e vinculo da sua conta no Telegram. Use o portal da escola para gerar o codigo de vinculacao e depois envie o comando `/start link_<codigo>` ao bot.
- `python_functions`: status 200, latency 138.0ms, keyword pass `True`, quality `100`, reason `python_functions_native_structured:institution`
  answer: Essa consulta depende de autenticacao e vinculo da sua conta no Telegram. Use o portal da escola para gerar o codigo de vinculacao e depois envie o comando `/start link_<codigo>` ao bot.
- `llamaindex`: status 200, latency 148.5ms, keyword pass `True`, quality `100`, reason `status administrativo autenticado exige service deterministico`
  answer: Essa consulta depende de autenticacao e vinculo da sua conta no Telegram. Use o portal da escola para gerar o codigo de vinculacao e depois envie o comando `/start link_<codigo>` ao bot.
- `specialist_supervisor`: status 200, latency 5042.6ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_strict_safe_fallback`
  answer: Nao consegui consolidar essa resposta premium com seguranca agora. Se quiser, me diga exatamente se voce quer ver notas, frequencia, documentacao, financeiro ou status de protocolo.

### Quero abrir um atendimento com o financeiro para negociar uma mensalidade parcialmente paga.

- Slice: `workflow`
- Thread: `system_bank:workflow_protocolos_visitas_e_handoff:Q079` turn `1`
- `langgraph`: status 200, latency 219.1ms, keyword pass `True`, quality `100`, reason `o turno atual trouxe pistas explicitas de outro dominio protegido e o roteamento foi corrigido`
  answer: Essa consulta depende de autenticacao e vinculo da sua conta no Telegram. Use o portal da escola para gerar o codigo de vinculacao e depois envie o comando `/start link_<codigo>` ao bot.
- `python_functions`: status 200, latency 177.5ms, keyword pass `True`, quality `100`, reason `python_functions_native_structured:institution`
  answer: Ainda nao encontrei uma resposta suficientemente suportada na base publica. Tente reformular a pergunta com termos como matricula, calendario, secretaria ou atendimento.
- `llamaindex`: status 200, latency 234.6ms, keyword pass `True`, quality `100`, reason `fato institucional canonico deve vir de fonte estruturada`
  answer: Ainda nao encontrei uma resposta suficientemente suportada na base publica. Tente reformular a pergunta com termos como matricula, calendario, secretaria ou atendimento.
- `specialist_supervisor`: status 200, latency 5040.9ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_strict_safe_fallback`
  answer: Nao consegui consolidar essa resposta premium com seguranca agora. Se quiser, me diga exatamente se voce quer ver notas, frequencia, documentacao, financeiro ou status de protocolo.

### Qual a diferenca entre abrir um protocolo, um chamado e um handoff humano?

- Slice: `workflow`
- Thread: `system_bank:workflow_protocolos_visitas_e_handoff:Q080` turn `1`
- `langgraph`: status 200, latency 133.0ms, keyword pass `True`, quality `100`, reason `o usuario demonstrou necessidade de atendimento humano ou operacional`
  answer: Posso seguir com orientacoes publicas por aqui, mas nao consegui registrar o encaminhamento humano agora. Tente novamente em instantes ou use a secretaria.
- `python_functions`: status 200, latency 132.3ms, keyword pass `True`, quality `100`, reason `o usuario demonstrou necessidade de atendimento humano ou operacional`
  answer: Posso seguir com orientacoes publicas por aqui, mas nao consegui registrar o encaminhamento humano agora. Tente novamente em instantes ou use a secretaria.
- `llamaindex`: status 200, latency 132.2ms, keyword pass `True`, quality `100`, reason `o usuario demonstrou necessidade de atendimento humano ou operacional`
  answer: Posso seguir com orientacoes publicas por aqui, mas nao consegui registrar o encaminhamento humano agora. Tente novamente em instantes ou use a secretaria.
- `specialist_supervisor`: status 200, latency 5042.2ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_strict_safe_fallback`
  answer: Nao consegui consolidar essa resposta premium com seguranca agora. Se quiser, me diga exatamente se voce quer ver notas, frequencia, documentacao, financeiro ou status de protocolo.

