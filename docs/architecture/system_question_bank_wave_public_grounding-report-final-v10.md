# Five-Path Chatbot Comparison Report

Date: 2026-04-01T22:39:11.761247+00:00

Dataset: `/home/edann/projects/eduassist-platform/tests/evals/datasets/system_question_bank_wave_public_grounding.json`

Run prefix: `debug:five-path:20260401T223520Z`

Stack execution mode: `sequential`

## Benchmark Context

- specialist benchmark mode: `source`
- api-core: `http://127.0.0.1:8001`
- ai-orchestrator: `http://127.0.0.1:8002`
- crewai pilot: `http://127.0.0.1:8004`
- specialist pilot: `http://127.0.0.1:8005`

## Stack Summary

| Stack | OK | Keyword pass | Quality | Avg latency |
| --- | --- | --- | --- | --- |
| `langgraph` | `24/24` | `24/24` | `100.0` | `2150.0 ms` |
| `crewai` | `24/24` | `24/24` | `100.0` | `5685.3 ms` |
| `python_functions` | `24/24` | `24/24` | `100.0` | `113.9 ms` |
| `llamaindex` | `24/24` | `24/24` | `100.0` | `1437.9 ms` |
| `specialist_supervisor` | `24/24` | `24/24` | `100.0` | `171.1 ms` |

## By Slice

- `public`
  - `langgraph`: ok 24/24, keyword pass 24/24, quality 100.0, latency 2150.0ms
  - `crewai`: ok 24/24, keyword pass 24/24, quality 100.0, latency 5685.3ms
  - `python_functions`: ok 24/24, keyword pass 24/24, quality 100.0, latency 113.9ms
  - `llamaindex`: ok 24/24, keyword pass 24/24, quality 100.0, latency 1437.9ms
  - `specialist_supervisor`: ok 24/24, keyword pass 24/24, quality 100.0, latency 171.1ms

## Error Types

- `langgraph`: nenhum
- `crewai`: nenhum
- `python_functions`: nenhum
- `llamaindex`: nenhum
- `specialist_supervisor`: nenhum

## Prompt Results

### Qual e o endereco completo da escola, o telefone principal e o melhor canal para falar com a secretaria hoje?

- Slice: `public`
- Thread: `system_bank:publico_estruturado_institucional:Q001` turn `1`
- `langgraph`: status 200, latency 279.4ms, keyword pass `True`, quality `100`, reason `fato institucional canonico deve vir de fonte estruturada`
  answer: O endereco publicado de Colegio Horizonte hoje e Rua das Acacias, 1450, Vila Mariana, Sao Paulo, SP, CEP 04567-120. O telefone principal hoje e (11) 3333-4200. O canal mais direto para falar com a secretaria hoje e o WhatsApp (11) 97500-2041.
- `crewai`: status 200, latency 309.3ms, keyword pass `True`, quality `100`, reason `crewai_public_fast_path`
  answer: Endereco: Rua das Acacias, 1450, Vila Mariana, Sao Paulo/SP, CEP 04567-120 O telefone principal hoje e (11) 3333-4200. O melhor canal para a secretaria hoje e (11) 97500-2040.
- `python_functions`: status 200, latency 98.5ms, keyword pass `True`, quality `100`, reason `python_functions_native_contextual_public_answer`
  answer: O endereco publicado de Colegio Horizonte hoje e Rua das Acacias, 1450, Vila Mariana, Sao Paulo, SP, CEP 04567-120. O telefone principal hoje e (11) 3333-4200. O canal mais direto para falar com a secretaria hoje e o WhatsApp (11) 97500-2041.
- `llamaindex`: status 200, latency 121.2ms, keyword pass `True`, quality `100`, reason `contextual_public_direct_answer`
  answer: O endereco publicado de Colegio Horizonte hoje e Rua das Acacias, 1450, Vila Mariana, Sao Paulo, SP, CEP 04567-120. O telefone principal hoje e (11) 3333-4200. O canal mais direto para falar com a secretaria hoje e o WhatsApp (11) 97500-2041.
- `specialist_supervisor`: status 200, latency 1721.4ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_fast_path:contact_bundle`
  answer: O endereco completo da escola hoje e Rua das Acacias, 1450, Vila Mariana, Sao Paulo, SP, CEP 04567-120. O telefone principal e (11) 3333-4200. O melhor canal para a secretaria hoje e o WhatsApp (11) 97500-2041.

### Essa escola tem biblioteca de verdade ou so fala que tem? Qual e o nome e o horario?

- Slice: `public`
- Thread: `system_bank:publico_estruturado_institucional:Q002` turn `1`
- `langgraph`: status 200, latency 4803.9ms, keyword pass `True`, quality `100`, reason `fato institucional canonico deve vir de fonte estruturada`
  answer: Que bom que você perguntou! Sim, temos uma biblioteca de verdade, a Biblioteca Aurora, e ela está aberta de segunda a sexta-feira, das 7h30 às 18h00, para atender a todos.
- `crewai`: status 200, latency 186.5ms, keyword pass `True`, quality `100`, reason `crewai_public_fast_path`
  answer: Sim. Biblioteca Aurora: biblioteca   Biblioteca Aurora   service   True   Atendimento ao publico de segunda a sexta, das 7h30 as 18h00..
- `python_functions`: status 200, latency 132.4ms, keyword pass `True`, quality `100`, reason `python_functions_native_structured:institution`
  answer: O horario de Biblioteca Aurora hoje funciona assim: Atendimento ao publico de segunda a sexta, das 7h30 as 18h00.

Turnos e horarios documentados:
- Ensino Fundamental II (Manha): 07:15 as 12:30. Oficinas, plantoes, esportes e estudo orientado no contraturno em dias alternados.
- Ensino Medio (Manha): 07:15 as 12:50. Trilhas eletivas, monitorias e laboratorios no contraturno a partir das 14h00.
- Fundamental II e Ensino Medio (Integral opcional): 07:00 as 17:30. Inclui estudo orientado, almoco, oficinas, esportes e acompanhamento no contraturno.
- `llamaindex`: status 200, latency 11468.8ms, keyword pass `True`, quality `100`, reason `llamaindex_public_profile`
  answer: O horario de Biblioteca Aurora hoje funciona assim: Atendimento ao publico de segunda a sexta, das 7h30 as 18h00.

Turnos e horarios documentados:
- Ensino Fundamental II (Manha): 07:15 as 12:30. Oficinas, plantoes, esportes e estudo orientado no contraturno em dias alternados.
- Ensino Medio (Manha): 07:15 as 12:50. Trilhas eletivas, monitorias e laboratorios no contraturno a partir das 14h00.
- Fundamental II e Ensino Medio (Integral opcional): 07:00 as 17:30. Inclui estudo orientado, almoco, oficinas, esportes e acompanhamento no contraturno.
- `specialist_supervisor`: status 200, latency 101.0ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_fast_path:library_hours`
  answer: A biblioteca se chama Biblioteca Aurora e funciona Atendimento ao publico de segunda a sexta, das 7h30 as 18h00.

### Quem responde por direcao, orientacao educacional e atendimento comercial?

- Slice: `public`
- Thread: `system_bank:publico_estruturado_institucional:Q003` turn `1`
- `langgraph`: status 200, latency 96.4ms, keyword pass `True`, quality `100`, reason `fato institucional canonico deve vir de fonte estruturada`
  answer: Hoje estes sao os responsaveis e canais mais diretos por assunto:
- Diretora geral: Helena Martins. Canal institucional: direcao@colegiohorizonte.edu.br.
- Atendimento comercial / Admissoes: bot, admissions, whatsapp comercial ou visita guiada.
- Orientacao educacional: bot, orientacao educacional ou secretaria.
- `crewai`: status 200, latency 164.3ms, keyword pass `True`, quality `100`, reason `crewai_public_fast_path`
  answer: Direcao geral: Helena Martins.
Para bolsa, desconto e matricula, o melhor canal hoje e Atendimento comercial / Admissoes. Admissoes (telefone): (11) 3333-4201
Para bullying, convivencia e apoio escolar, o canal indicado e a orientacao educacional. Orientacao educacional (telefone): (11) 3333-4202
- `python_functions`: status 200, latency 158.6ms, keyword pass `True`, quality `100`, reason `python_functions_native_contextual_public_answer`
  answer: Hoje estes sao os responsaveis e canais mais diretos por assunto:
- Diretora geral: Helena Martins. Canal institucional: direcao@colegiohorizonte.edu.br.
- Atendimento comercial / Admissoes: bot, admissions, whatsapp comercial ou visita guiada.
- Orientacao educacional: bot, orientacao educacional ou secretaria.
- `llamaindex`: status 200, latency 106.0ms, keyword pass `True`, quality `100`, reason `contextual_public_direct_answer`
  answer: Hoje estes sao os responsaveis e canais mais diretos por assunto:
- Diretora geral: Helena Martins. Canal institucional: direcao@colegiohorizonte.edu.br.
- Atendimento comercial / Admissoes: bot, admissions, whatsapp comercial ou visita guiada.
- Orientacao educacional: bot, orientacao educacional ou secretaria.
- `specialist_supervisor`: status 200, latency 98.1ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_fast_path:service_routing`
  answer: Hoje estes sao os responsaveis e canais mais diretos por assunto:
- Diretora geral: Helena Martins. Canal institucional: direcao@colegiohorizonte.edu.br.
- Atendimento comercial / Admissoes: bot, admissions, whatsapp comercial ou visita guiada.
- Orientacao educacional: bot, orientacao educacional ou secretaria.
- Direcao: bot, ouvidoria ou protocolo institucional.

### Se eu fosse uma familia nova e tivesse so 30 segundos, o que voce me diria sobre essa escola?

- Slice: `public`
- Thread: `system_bank:publico_estruturado_institucional:Q004` turn `1`
- `langgraph`: status 200, latency 106.1ms, keyword pass `True`, quality `100`, reason `fato institucional canonico deve vir de fonte estruturada`
  answer: Se eu tivesse 30 segundos para resumir Colegio Horizonte, eu diria isto: Escola laica com Ensino Fundamental II e Ensino Medio, acompanhamento tutorial e trilhas academicas no contraturno. Os diferenciais publicados com mais clareza hoje passam por Tutoria academica e projeto de vida, Espaco Maker integrado ao curriculo, Acolhimento estruturado para familias e estudantes. A proposta pedagogica publicada combina Projeto pedagogico laico, com foco em aprendizagem por projetos, cultura digital responsavel, acompanhamento socioemocional e preparacao academica progressiva.. Na pratica, isso aparece em aprendizagem por projetos, acompanhamento mais proximo, estudo orientado e contraturno com referencias claras para familias.
- `crewai`: status 200, latency 159.6ms, keyword pass `True`, quality `100`, reason `crewai_public_fast_path`
  answer: Se eu tivesse 30 segundos para resumir esta escola, eu diria isto: ela combina aprendizagem por projetos, acompanhamento mais proximo e trilhas academicas no contraturno. No que esta publicado aqui, os diferenciais mais claros passam por Tutoria academica e projeto de vida, Espaco Maker integrado ao curriculo. Colegio Horizonte em Sao Paulo/SP. Escola laica com Ensino Fundamental II e Ensino Medio, acompanhamento tutorial e trilhas academicas no contraturno. Projeto pedagogico laico, com foco em aprendizagem por projetos, cultura digital responsavel, acompanhamento socioemocional e preparacao academica progressiva.
- `python_functions`: status 200, latency 110.6ms, keyword pass `True`, quality `100`, reason `python_functions_native_contextual_public_answer`
  answer: Se eu tivesse 30 segundos para resumir Colegio Horizonte, eu diria isto: Escola laica com Ensino Fundamental II e Ensino Medio, acompanhamento tutorial e trilhas academicas no contraturno. Os diferenciais publicados com mais clareza hoje passam por Tutoria academica e projeto de vida, Espaco Maker integrado ao curriculo, Acolhimento estruturado para familias e estudantes. A proposta pedagogica publicada combina Projeto pedagogico laico, com foco em aprendizagem por projetos, cultura digital responsavel, acompanhamento socioemocional e preparacao academica progressiva.. Na pratica, isso aparece em aprendizagem por projetos, acompanhamento mais proximo, estudo orientado e contraturno com referencias claras para familias.
- `llamaindex`: status 200, latency 120.0ms, keyword pass `True`, quality `100`, reason `contextual_public_direct_answer`
  answer: Se eu tivesse 30 segundos para resumir Colegio Horizonte, eu diria isto: Escola laica com Ensino Fundamental II e Ensino Medio, acompanhamento tutorial e trilhas academicas no contraturno. Os diferenciais publicados com mais clareza hoje passam por Tutoria academica e projeto de vida, Espaco Maker integrado ao curriculo, Acolhimento estruturado para familias e estudantes. A proposta pedagogica publicada combina Projeto pedagogico laico, com foco em aprendizagem por projetos, cultura digital responsavel, acompanhamento socioemocional e preparacao academica progressiva.. Na pratica, isso aparece em aprendizagem por projetos, acompanhamento mais proximo, estudo orientado e contraturno com referencias claras para familias.
- `specialist_supervisor`: status 200, latency 102.5ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_fast_path:public_pitch`
  answer: Se eu tivesse 30 segundos para resumir esta escola, eu diria isto: ela combina aprendizagem por projetos, acompanhamento mais proximo e trilhas academicas no contraturno. A proposta pedagogica publicada hoje combina Projeto pedagogico laico, com foco em aprendizagem por projetos, cultura digital responsavel, acompanhamento socioemocional e preparacao academica progressiva.. No Ensino Medio, isso aparece junto de A escola segue a BNCC e o curriculo do Ensino Medio articulado com projeto de vida, producao textual, cultura digital e aprofundamento academico progressivo.. Escola laica com Ensino Fundamental II e Ensino Medio, acompanhamento tutorial e trilhas academicas no contraturno. Na pratica, isso aparece em acompanhamento mais proximo da aprendizagem, projeto de vida e uma rotina pedagogica mais explicita no dia a dia.

### O colegio divulga nomes e contatos diretos de professores por disciplina?

- Slice: `public`
- Thread: `system_bank:publico_estruturado_institucional:Q005` turn `1`
- `langgraph`: status 200, latency 102.8ms, keyword pass `True`, quality `100`, reason `a consulta exige autenticacao ou vinculo antes de qualquer acesso`
  answer: Aqui e o Colegio Horizonte. Se voce esta procurando o Divulga Nomes E Contatos, eu nao tenho acesso ao atendimento dessa outra instituicao. Se quiser, sigo te ajudando com o Colegio Horizonte por aqui.
- `crewai`: status 200, latency 168.5ms, keyword pass `True`, quality `100`, reason `crewai_public_fast_path`
  answer: Hoje a escola divulga atividades e espacos complementares como Biblioteca Aurora, Espaco Maker, futsal, volei escolar. Se quiser, eu tambem posso detalhar Biblioteca Aurora, Laboratorio de Ciencias, Espaco Maker, Quadra Poliesportiva Coberta.
- `python_functions`: status 200, latency 107.6ms, keyword pass `True`, quality `100`, reason `a consulta exige autenticacao ou vinculo antes de qualquer acesso`
  answer: Essa consulta depende de autenticacao e vinculo da sua conta no Telegram. Use o portal da escola para gerar o codigo de vinculacao e depois envie o comando `/start link_<codigo>` ao bot.
- `llamaindex`: status 200, latency 128.1ms, keyword pass `True`, quality `100`, reason `a consulta exige autenticacao ou vinculo antes de qualquer acesso`
  answer: Essa consulta depende de autenticacao e vinculo da sua conta no Telegram. Use o portal da escola para gerar o codigo de vinculacao e depois envie o comando `/start link_<codigo>` ao bot.
- `specialist_supervisor`: status 200, latency 81.2ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_fast_path:teacher_directory`
  answer: O Colegio Horizonte nao divulga nomes nem contatos diretos de professores individualmente. Se quiser, eu posso te indicar a coordenacao pedagogica ou o setor certo.

### Em qual bairro de Sao Paulo a escola fica e quais sao os principais referenciais de acesso?

- Slice: `public`
- Thread: `system_bank:publico_estruturado_institucional:Q006` turn `1`
- `langgraph`: status 200, latency 5474.1ms, keyword pass `True`, quality `100`, reason `fato institucional canonico deve vir de fonte estruturada`
  answer: Colegio Horizonte fica em Rua das Acacias, 1450, Vila Mariana, Sao Paulo, SP, CEP 04567-120.
- `crewai`: status 200, latency 19994.9ms, keyword pass `True`, quality `100`, reason `crewai_public_flow_completed`
  answer: Para te ajudar com o endereço da escola, preciso de mais informações. Não encontrei o endereço nos documentos disponíveis. Você poderia me dizer qual escola você procura?
- `python_functions`: status 200, latency 148.2ms, keyword pass `True`, quality `100`, reason `python_functions_native_structured:institution`
  answer: Colegio Horizonte fica em Rua das Acacias, 1450, Vila Mariana, Sao Paulo, SP, CEP 04567-120.
- `llamaindex`: status 200, latency 8613.5ms, keyword pass `True`, quality `100`, reason `llamaindex_public_profile`
  answer: Colegio Horizonte fica em Rua das Acacias, 1450, Vila Mariana, Sao Paulo, SP, CEP 04567-120.
- `specialist_supervisor`: status 200, latency 95.8ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_fast_path:district`
  answer: A escola fica no bairro Vila Mariana, Sao Paulo/SP.

### Com quem eu falo sobre bolsa, com quem eu falo sobre boletos e com quem eu falo sobre bullying?

- Slice: `public`
- Thread: `system_bank:publico_estruturado_institucional:Q007` turn `1`
- `langgraph`: status 200, latency 100.2ms, keyword pass `True`, quality `100`, reason `fato institucional canonico deve vir de fonte estruturada`
  answer: Hoje estes sao os responsaveis e canais mais diretos por assunto:
- Atendimento comercial / Admissoes: bot, admissions, whatsapp comercial ou visita guiada.
- Financeiro: bot, financeiro, portal autenticado ou email institucional.
- Orientacao educacional: bot, orientacao educacional ou secretaria.
- `crewai`: status 200, latency 160.1ms, keyword pass `True`, quality `100`, reason `crewai_public_fast_path`
  answer: Para bolsa, desconto e matricula, o melhor canal hoje e Atendimento comercial / Admissoes. Admissoes (telefone): (11) 3333-4201
Para boletos, vencimentos e contratos, o melhor canal hoje e o financeiro. Financeiro (telefone): (11) 3333-4203
Para bullying, convivencia e apoio escolar, o canal indicado e a orientacao educacional. Orientacao educacional (telefone): (11) 3333-4202
- `python_functions`: status 200, latency 106.0ms, keyword pass `True`, quality `100`, reason `python_functions_native_contextual_public_answer`
  answer: Hoje estes sao os responsaveis e canais mais diretos por assunto:
- Atendimento comercial / Admissoes: bot, admissions, whatsapp comercial ou visita guiada.
- Financeiro: bot, financeiro, portal autenticado ou email institucional.
- Orientacao educacional: bot, orientacao educacional ou secretaria.
- `llamaindex`: status 200, latency 119.8ms, keyword pass `True`, quality `100`, reason `contextual_public_direct_answer`
  answer: Hoje estes sao os responsaveis e canais mais diretos por assunto:
- Atendimento comercial / Admissoes: bot, admissions, whatsapp comercial ou visita guiada.
- Financeiro: bot, financeiro, portal autenticado ou email institucional.
- Orientacao educacional: bot, orientacao educacional ou secretaria.
- `specialist_supervisor`: status 200, latency 101.7ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_fast_path:service_routing`
  answer: Hoje estes sao os responsaveis e canais mais diretos por assunto:
- Atendimento comercial / Admissoes: bot, admissions, whatsapp comercial ou visita guiada.
- Financeiro: bot, financeiro, portal autenticado ou email institucional.
- Orientacao educacional: bot, orientacao educacional ou secretaria.

### Qual a diferenca entre falar com secretaria, coordenacao e orientacao educacional?

- Slice: `public`
- Thread: `system_bank:publico_estruturado_institucional:Q008` turn `1`
- `langgraph`: status 200, latency 102.4ms, keyword pass `True`, quality `100`, reason `fato institucional canonico deve vir de fonte estruturada`
  answer: Hoje estes sao os responsaveis e canais mais diretos por assunto:
- Orientacao educacional: bot, orientacao educacional ou secretaria.
- Secretaria: bot, secretaria presencial, email institucional ou portal.
- `crewai`: status 200, latency 15520.4ms, keyword pass `True`, quality `100`, reason `crewai_public_flow_completed`
  answer: Os departamentos escolares têm papéis bem definidos para apoiar os estudantes! O Departamento de Educação garante a qualidade do ensino, desenvolve currículos, gerencia as escolas e promove a formação contínua dos professores. Já o Departamento de Saúde Escolar cuida do bem-estar dos alunos com programas de saúde preventiva, acompanhamento médico e psicológico, e campanhas de vacinação. E para enriquecer a experiência educacional, o Departamento de Esportes e Cultura organiza atividades extracurriculares, eventos esportivos, oficinas de arte e projetos culturais.
- `python_functions`: status 200, latency 96.9ms, keyword pass `True`, quality `100`, reason `python_functions_native_contextual_public_answer`
  answer: Hoje estes sao os responsaveis e canais mais diretos por assunto:
- Orientacao educacional: bot, orientacao educacional ou secretaria.
- Secretaria: bot, secretaria presencial, email institucional ou portal.
- `llamaindex`: status 200, latency 109.4ms, keyword pass `True`, quality `100`, reason `contextual_public_direct_answer`
  answer: Hoje estes sao os responsaveis e canais mais diretos por assunto:
- Orientacao educacional: bot, orientacao educacional ou secretaria.
- Secretaria: bot, secretaria presencial, email institucional ou portal.
- `specialist_supervisor`: status 200, latency 117.1ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_tool_first:human_handoff`
  answer: Encaminhei sua solicitacao para a fila de coordenacao. Protocolo: ATD-20260401-7D7D5352. Status atual: queued. Se preferir, voce tambem pode seguir pelo WhatsApp oficial (11) 97500-2040.

### Quando abre a matricula de 2026 e quando comecam as aulas?

- Slice: `public`
- Thread: `system_bank:timeline_e_calendario_publico:Q009` turn `1`
- `langgraph`: status 200, latency 5024.5ms, keyword pass `True`, quality `100`, reason `datas institucionais publicas devem vir de leitura estruturada e auditavel`
  answer: Que bom que você está se planejando com antecedência! As matrículas para 2026 no Colégio Horizonte abriram em 6 de outubro de 2025, com pré-cadastro e visita orientada. As aulas para o Ensino Fundamental II e Ensino Médio começarão em 2 de fevereiro de 2026, e teremos uma semana especial de acolhimento para o 6º ano e a 1ª série entre 2 e 6 de fevereiro.
- `crewai`: status 200, latency 178.5ms, keyword pass `True`, quality `100`, reason `crewai_public_fast_path`
  answer: O ciclo publico de matricula para 2026 foi aberto em 6 de outubro de 2025, com pre-cadastro, visita orientada opcional e triagem inicial de documentos. | 2025-10-06 | familias interessadas | O atendimento comercial segue enquanto houver vagas por segmento.
As aulas do Ensino Fundamental II e do Ensino Medio comecam em 2 de fevereiro de 2026. | 2026-02-02 | alunos e familias | A semana de acolhimento do 6o ano e da primeira serie ocorre entre 2 e 6 de fevereiro.
- `python_functions`: status 200, latency 104.1ms, keyword pass `True`, quality `100`, reason `python_functions_native_contextual_public_answer`
  answer: O ciclo publico de matricula para 2026 foi aberto em 6 de outubro de 2025, com pre-cadastro, visita orientada opcional e triagem inicial de documentos. O atendimento comercial segue enquanto houver vagas por segmento.
As aulas do Ensino Fundamental II e do Ensino Medio comecam em 2 de fevereiro de 2026. A semana de acolhimento do 6o ano e da primeira serie ocorre entre 2 e 6 de fevereiro.
- `llamaindex`: status 200, latency 111.5ms, keyword pass `True`, quality `100`, reason `contextual_public_direct_answer`
  answer: Hoje a base publica de Colegio Horizonte nao traz um marco institucional estruturado para essa data.
- `specialist_supervisor`: status 200, latency 104.1ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_tool_first:public_timeline_bundle`
  answer: O ciclo publico de matricula para 2026 foi aberto em 6 de outubro de 2025, com pre-cadastro, visita orientada opcional e triagem inicial de documentos. O atendimento comercial segue enquanto houver vagas por segmento.
As aulas do Ensino Fundamental II e do Ensino Medio comecam em 2 de fevereiro de 2026. A semana de acolhimento do 6o ano e da primeira serie ocorre entre 2 e 6 de fevereiro.

### Quais sao os principais eventos publicos desta semana para familias e responsaveis?

- Slice: `public`
- Thread: `system_bank:timeline_e_calendario_publico:Q010` turn `1`
- `langgraph`: status 200, latency 1440.4ms, keyword pass `True`, quality `100`, reason `a intencao esta ambigua e exige clarificacao antes de recuperar contexto`
  answer: Olá! No momento, não tenho informações sobre eventos públicos específicos para famílias e responsáveis nesta semana.

Para ficar por dentro de todas as novidades e o calendário completo de eventos, sugiro que consulte o nosso portal oficial ou entre em contato com a Secretaria Escolar. Eles poderão te ajudar com as informações mais atualizadas.
- `crewai`: status 200, latency 20217.8ms, keyword pass `True`, quality `100`, reason `crewai_public_flow_timeout`
  answer: Olá! Encontrei a Visita Guiada para famílias interessadas, que está agendada para 06 de abril de 2026. Você gostaria de saber sobre eventos em outra data ou sobre o processo de acolhimento para famílias?
- `python_functions`: status 200, latency 143.2ms, keyword pass `True`, quality `100`, reason `a intencao esta ambigua e exige clarificacao antes de recuperar contexto`
  answer: Posso ajudar com informacoes publicas da escola, como calendario, matricula, documentos exigidos e regras de atendimento digital. Se quiser, pergunte por exemplo: "quais documentos preciso para a matricula?" ou "quando acontece a reuniao de pais?".
- `llamaindex`: status 200, latency 6003.5ms, keyword pass `True`, quality `100`, reason `llamaindex_public_profile`
  answer: Hoje a base publica de eventos de Colegio Horizonte nao trouxe agenda estruturada para esse pedido.
- `specialist_supervisor`: status 200, latency 99.4ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_tool_first:calendar_week`
  answer: Os principais eventos publicos para familias e responsaveis nesta base sao:
- Reuniao geral de pais e responsaveis (28/03/2026) · publico: public. Apresentacao do planejamento do primeiro bimestre.
- Reuniao de responsaveis do 6o ao 9o ano (28/03/2026) · publico: public. Apresentacao das rotinas do Fundamental II, canais oficiais e acompanhamento pedagógico.
- Reuniao de responsaveis do Ensino Medio (29/03/2026) · publico: public. Apresentacao das rotinas do Ensino Medio, avaliacao e apoio a vestibulares.
- Visita guiada para familias interessadas (06/04/2026) · publico: public. Apresentacao institucional do Fundamental II e Ensino Medio com tour pelos espacos.

### Monte uma linha do tempo do primeiro bimestre com datas que importam para pais e alunos.

- Slice: `public`
- Thread: `system_bank:timeline_e_calendario_publico:Q011` turn `1`
- `langgraph`: status 200, latency 111.7ms, keyword pass `True`, quality `100`, reason `a consulta exige autenticacao ou vinculo antes de qualquer acesso`
  answer: Essa consulta depende de autenticacao e vinculo da sua conta no Telegram. Use o portal da escola para gerar o codigo de vinculacao e depois envie o comando `/start link_<codigo>` ao bot.
- `crewai`: status 200, latency 16353.2ms, keyword pass `True`, quality `100`, reason `crewai_public_flow_completed`
  answer: Que bom que você perguntou! O calendário escolar de 2024 já está disponível. As aulas começam em 5 de fevereiro de 2024, o recesso de meio de ano será de 15 a 26 de julho de 2024 e o último dia de aula está previsto para 13 de dezembro de 2024.
- `python_functions`: status 200, latency 107.1ms, keyword pass `True`, quality `100`, reason `a consulta exige autenticacao ou vinculo antes de qualquer acesso`
  answer: Essa consulta depende de autenticacao e vinculo da sua conta no Telegram. Use o portal da escola para gerar o codigo de vinculacao e depois envie o comando `/start link_<codigo>` ao bot.
- `llamaindex`: status 200, latency 129.5ms, keyword pass `True`, quality `100`, reason `a consulta exige autenticacao ou vinculo antes de qualquer acesso`
  answer: Essa consulta depende de autenticacao e vinculo da sua conta no Telegram. Use o portal da escola para gerar o codigo de vinculacao e depois envie o comando `/start link_<codigo>` ao bot.
- `specialist_supervisor`: status 200, latency 95.8ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_tool_first:first_bimester_timeline`
  answer: Linha do tempo publica do primeiro bimestre:
- O ciclo publico de matricula para 2026 foi aberto em 6 de outubro de 2025, com pre-cadastro, visita orientada opcional e triagem inicial de documentos.
- As aulas do Ensino Fundamental II e do Ensino Medio comecam em 2 de fevereiro de 2026.
- A cerimonia interna de conclusao do Ensino Fundamental II esta prevista para 12 de dezembro de 2026, no fim da tarde, apos o encerramento do ano letivo.
- Inicio do ano letivo Fundamental II e Ensino Medio (02/02/2026) · publico: public. Recepcao das turmas com orientacoes iniciais, entrega de horarios e apresentacao da equipe.
- Reuniao geral de pais e responsaveis (28/03/2026) · publico: public. Apresentacao do planejamento do primeiro bimestre.
- Reuniao de responsaveis do 6o ao 9o ano (28/03/2026) · publico: public. Apresentacao das rotinas do Fundamental II, canais oficiais e acompanhamento pedagógico.

### Quando acontecem reunioes de pais, simulados e semanas de prova no ano letivo?

- Slice: `public`
- Thread: `system_bank:timeline_e_calendario_publico:Q012` turn `1`
- `langgraph`: status 200, latency 5490.9ms, keyword pass `True`, quality `100`, reason `datas institucionais publicas devem vir de leitura estruturada e auditavel`
  answer: As aulas do Ensino Fundamental II e do Ensino Medio comecam em 2 de fevereiro de 2026. A semana de acolhimento do 6o ano e da primeira serie ocorre entre 2 e 6 de fevereiro.
- `crewai`: status 200, latency 160.0ms, keyword pass `True`, quality `100`, reason `crewai_protected_auth_required`
  answer: Essa consulta depende de autenticacao e vinculo da sua conta no Telegram. Use o portal da escola para gerar o codigo de vinculacao e depois envie o comando /start link_<codigo> ao bot.
- `python_functions`: status 200, latency 104.5ms, keyword pass `True`, quality `100`, reason `python_functions_native_contextual_public_answer`
  answer: As aulas do Ensino Fundamental II e do Ensino Medio comecam em 2 de fevereiro de 2026. A semana de acolhimento do 6o ano e da primeira serie ocorre entre 2 e 6 de fevereiro.
- `llamaindex`: status 200, latency 110.8ms, keyword pass `True`, quality `100`, reason `contextual_public_direct_answer`
  answer: Hoje a base publica de Colegio Horizonte nao traz um marco institucional estruturado para essa data.
- `specialist_supervisor`: status 200, latency 107.4ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_tool_first:eval_calendar`
  answer: No calendario publico atual, estes sao os marcos mais relevantes para reunioes, simulados e semanas de prova:
- Reuniao geral de pais e responsaveis (28/03/2026) · publico: public. Apresentacao do planejamento do primeiro bimestre.
- Reuniao de responsaveis do 6o ao 9o ano (28/03/2026) · publico: public. Apresentacao das rotinas do Fundamental II, canais oficiais e acompanhamento pedagógico.
- Reuniao de responsaveis do Ensino Medio (29/03/2026) · publico: public. Apresentacao das rotinas do Ensino Medio, avaliacao e apoio a vestibulares.
- Plantao pedagogico do primeiro bimestre (11/04/2026) · publico: public. Atendimento com professores para esclarecimento de notas e frequencia.

### O que acontece antes da confirmacao da vaga e o que acontece depois do inicio das aulas?

- Slice: `public`
- Thread: `system_bank:timeline_e_calendario_publico:Q013` turn `1`
- `langgraph`: status 200, latency 5585.3ms, keyword pass `True`, quality `100`, reason `datas institucionais publicas devem vir de leitura estruturada e auditavel`
  answer: Que bom que você está se informando sobre o processo! Antes da confirmação da vaga, nosso ciclo de matrículas para 2026 começou em 6 de outubro de 2025, com pré-cadastro, visita orientada opcional e triagem de documentos. Nosso atendimento comercial continua enquanto houver vagas.

Após o início das aulas, que para o Ensino Fundamental II e Médio será em 2 de fevereiro de 2026, teremos uma semana de acolhimento especial para o 6º ano e a 1ª série, entre os dias 2 e 6 de fevereiro.
- `crewai`: status 200, latency 163.5ms, keyword pass `True`, quality `100`, reason `crewai_public_fast_path`
  answer: As aulas do Ensino Fundamental II e do Ensino Medio comecam em 2 de fevereiro de 2026.
- `python_functions`: status 200, latency 99.7ms, keyword pass `True`, quality `100`, reason `python_functions_native_contextual_public_answer`
  answer: Antes da confirmacao da vaga: O ciclo publico de matricula para 2026 foi aberto em 6 de outubro de 2025, com pre-cadastro, visita orientada opcional e triagem inicial de documentos. O atendimento comercial segue enquanto houver vagas por segmento. Depois do inicio das aulas: As aulas do Ensino Fundamental II e do Ensino Medio comecam em 2 de fevereiro de 2026. A semana de acolhimento do 6o ano e da primeira serie ocorre entre 2 e 6 de fevereiro.
- `llamaindex`: status 200, latency 109.8ms, keyword pass `True`, quality `100`, reason `contextual_public_direct_answer`
  answer: Hoje a base publica de Colegio Horizonte nao traz um marco institucional estruturado para essa data.
- `specialist_supervisor`: status 200, latency 99.1ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_tool_first:public_timeline`
  answer: As aulas do Ensino Fundamental II e do Ensino Medio comecam em 2 de fevereiro de 2026. A semana de acolhimento do 6o ano e da primeira serie ocorre entre 2 e 6 de fevereiro.

### Se eu quiser planejar uma viagem sem atrapalhar a vida escolar, quais marcos do calendario eu deveria observar?

- Slice: `public`
- Thread: `system_bank:timeline_e_calendario_publico:Q014` turn `1`
- `langgraph`: status 200, latency 3966.9ms, keyword pass `True`, quality `100`, reason `datas institucionais publicas devem vir de leitura estruturada e auditavel`
  answer: Que ótima iniciativa planejar com antecedência! Para que sua viagem não atrapalhe os estudos, sugiro que você observe as seguintes datas importantes do nosso calendário: o início das aulas em 2 de fevereiro de 2026 e a cerimônia de conclusão do Ensino Fundamental II, que será em 12 de dezembro de 2026. O ciclo de matrículas para 2026, que começou em 6 de outubro de 2025, também é um bom período para se atentar.
- `crewai`: status 200, latency 20216.4ms, keyword pass `True`, quality `100`, reason `crewai_public_flow_completed`
  answer: Nao consegui concluir essa resposta agora pelo caminho principal configurado. Tente reformular em uma frase mais direta ou repetir em instantes.
- `python_functions`: status 200, latency 107.7ms, keyword pass `True`, quality `100`, reason `python_functions_native_contextual_public_answer`
  answer: Para planejar uma viagem sem atrapalhar a vida escolar, vale observar estes marcos publicos antes de fechar datas:
- O ciclo publico de matricula para 2026 foi aberto em 6 de outubro de 2025, com pre-cadastro, visita orientada opcional e triagem inicial de documentos.
- As aulas do Ensino Fundamental II e do Ensino Medio comecam em 2 de fevereiro de 2026.
- A cerimonia interna de conclusao do Ensino Fundamental II esta prevista para 12 de dezembro de 2026, no fim da tarde, apos o encerramento do ano letivo.
- `llamaindex`: status 200, latency 120.6ms, keyword pass `True`, quality `100`, reason `contextual_public_direct_answer`
  answer: Hoje a base publica de Colegio Horizonte nao traz um marco institucional estruturado para essa data.
- `specialist_supervisor`: status 200, latency 98.4ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_tool_first:travel_planning`
  answer: Para planejar uma viagem sem atrapalhar a vida escolar, vale observar estes marcos publicos antes de fechar datas:
- O ciclo publico de matricula para 2026 foi aberto em 6 de outubro de 2025, com pre-cadastro, visita orientada opcional e triagem inicial de documentos.
- As aulas do Ensino Fundamental II e do Ensino Medio comecam em 2 de fevereiro de 2026.
- A cerimonia interna de conclusao do Ensino Fundamental II esta prevista para 12 de dezembro de 2026, no fim da tarde, apos o encerramento do ano letivo.
- Reuniao geral de pais e responsaveis (28/03/2026) · publico: public. Apresentacao do planejamento do primeiro bimestre.
- Reuniao de responsaveis do 6o ao 9o ano (28/03/2026) · publico: public. Apresentacao das rotinas do Fundamental II, canais oficiais e acompanhamento pedagógico.
- Reuniao de responsaveis do Ensino Medio (29/03/2026) · publico: public. Apresentacao das rotinas do Ensino Medio, avaliacao e apoio a vestibulares.
- Visita guiada para familias interessadas (06/04/2026) · publico: public. Apresentacao institucional do Fundamental II e Ensino Medio com tour pelos espacos.

### Quais eventos do calendario sao realmente publicos e quais dependem de autenticacao ou contexto interno?

- Slice: `public`
- Thread: `system_bank:timeline_e_calendario_publico:Q015` turn `1`
- `langgraph`: status 200, latency 5126.5ms, keyword pass `True`, quality `100`, reason `planejamento semantico publico encontrou um ato estruturado mais adequado ao turno`
  answer: Olá! No nosso calendário, os marcos institucionais e eventos coletivos são sempre abertos para toda a comunidade. Já os detalhes individuais de cada aluno, convites específicos, protocolos e informações financeiras são acessíveis apenas com autenticação, para garantir a segurança e privacidade. Fique tranquilo(a), qualquer ajuste importante no calendário de avaliações é sempre atualizado no portal e comunicado pelos nossos canais oficiais.
- `crewai`: status 200, latency 20221.9ms, keyword pass `True`, quality `100`, reason `crewai_public_flow_timeout`
  answer: Para te ajudar melhor, você está buscando informações sobre eventos específicos ou uma lista completa de todos os eventos do calendário e suas condições de acesso?
- `python_functions`: status 200, latency 99.9ms, keyword pass `True`, quality `100`, reason `python_functions_native_contextual_public_answer`
  answer: No calendario publico, o que costuma ficar aberto para familias sao marcos institucionais gerais e eventos coletivos. O que depende de autenticacao ou contexto interno sao detalhes individuais por aluno, convites direcionados, protocolos, situacoes financeiras e acompanhamentos protegidos. Sempre que houver ajuste relevante no calendario de avaliacao, a escola atualiza o portal e reforca a comunicacao pelos canais oficiais. O ambiente digital amplia o atendimento, mas nao substitui todos os processos formais.
- `llamaindex`: status 200, latency 109.4ms, keyword pass `True`, quality `100`, reason `contextual_public_direct_answer`
  answer: No calendario publico, o que costuma ficar aberto para familias sao marcos institucionais gerais e eventos coletivos. O que depende de autenticacao ou contexto interno sao detalhes individuais por aluno, convites direcionados, protocolos, situacoes financeiras e acompanhamentos protegidos. Sempre que houver ajuste relevante no calendario de avaliacao, a escola atualiza o portal e reforca a comunicacao pelos canais oficiais. O ambiente digital amplia o atendimento, mas nao substitui todos os processos formais.
- `specialist_supervisor`: status 200, latency 105.2ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_tool_first:restricted_document_denied`
  answer: Nao posso compartilhar procedimentos, protocolos, manuais ou playbooks internos da escola. Se voce precisa de orientacao oficial, eu posso explicar a politica publica correspondente ou abrir um handoff.

### Resuma o ano escolar em tres fases: admissao, rotina academica e fechamento.

- Slice: `public`
- Thread: `system_bank:timeline_e_calendario_publico:Q016` turn `1`
- `langgraph`: status 200, latency 5944.8ms, keyword pass `True`, quality `100`, reason `datas institucionais publicas devem vir de leitura estruturada e auditavel`
  answer: Que bom que você se interessa pelo nosso calendário! O ano escolar no Colégio Horizonte se organiza assim: a admissão para 2026 começou em 6 de outubro de 2025, com pré-cadastro e visita. As aulas do Ensino Fundamental II e Médio iniciam em 2 de fevereiro de 2026, e a cerimônia de conclusão do Fundamental II será em 12 de dezembro de 2026.
- `crewai`: status 200, latency 20203.9ms, keyword pass `True`, quality `100`, reason `crewai_public_flow_completed`
  answer: Nao consegui concluir essa resposta agora pelo caminho principal configurado. Tente reformular em uma frase mais direta ou repetir em instantes.
- `python_functions`: status 200, latency 111.5ms, keyword pass `True`, quality `100`, reason `python_functions_native_contextual_public_answer`
  answer: Admissao: O ciclo publico de matricula para 2026 foi aberto em 6 de outubro de 2025, com pre-cadastro, visita orientada opcional e triagem inicial de documentos.
Rotina academica: As aulas do Ensino Fundamental II e do Ensino Medio comecam em 2 de fevereiro de 2026.
Fechamento: A cerimonia interna de conclusao do Ensino Fundamental II esta prevista para 12 de dezembro de 2026, no fim da tarde, apos o encerramento do ano letivo.
- `llamaindex`: status 200, latency 109.9ms, keyword pass `True`, quality `100`, reason `contextual_public_direct_answer`
  answer: Hoje a base publica de Colegio Horizonte nao traz um marco institucional estruturado para essa data.
- `specialist_supervisor`: status 200, latency 103.0ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_tool_first:year_three_phases`
  answer: Admissao: O ciclo publico de matricula para 2026 foi aberto em 6 de outubro de 2025, com pre-cadastro, visita orientada opcional e triagem inicial de documentos.
Rotina academica: As aulas do Ensino Fundamental II e do Ensino Medio comecam em 2 de fevereiro de 2026. Eventos publicos ao longo do ano incluem Inicio do ano letivo Fundamental II e Ensino Medio (02/02/2026) · publico: public. Recepcao das turmas com orientacoes iniciais, entrega de horarios e apresentacao da equipe; Reuniao geral de pais e responsaveis (28/03/2026) · publico: public. Apresentacao do planejamento do primeiro bimestre.
Fechamento: A cerimonia interna de conclusao do Ensino Fundamental II esta prevista para 12 de dezembro de 2026, no fim da tarde, apos o encerramento do ano letivo.

### Quais documentos sao exigidos para matricula no ensino medio?

- Slice: `public`
- Thread: `system_bank:retrieval_hibrido_sobre_documentos_publicos:Q017` turn `1`
- `langgraph`: status 200, latency 120.9ms, keyword pass `True`, quality `100`, reason `o turno atual trouxe pistas explicitas de outro dominio protegido e o roteamento foi corrigido`
  answer: Hoje os documentos exigidos para a matricula publicados pela escola sao:
- Formulario cadastral preenchido
- Documento de identificacao do aluno
- CPF do aluno, quando houver
- Historico escolar
- Comprovante de residencia atualizado
- Documento de identificacao do responsavel legal
Se quiser, eu tambem posso explicar as etapas da matricula ou como funciona o envio inicial desses documentos.
- `crewai`: status 200, latency 609.4ms, keyword pass `True`, quality `100`, reason `crewai_public_fast_path`
  answer: Hoje os documentos exigidos para a matricula publicados pela escola sao:
- Formulario cadastral preenchido
- Documento de identificacao do aluno
- CPF do aluno, quando houver
- Historico escolar
- Comprovante de residencia atualizado
- Documento de identificacao do responsavel legal
- `python_functions`: status 200, latency 139.6ms, keyword pass `True`, quality `100`, reason `python_functions_native_contextual_public_answer`
  answer: Hoje os documentos exigidos para a matricula publicados pela escola sao:
- Formulario cadastral preenchido
- Documento de identificacao do aluno
- CPF do aluno, quando houver
- Historico escolar
- Comprovante de residencia atualizado
- Documento de identificacao do responsavel legal
Se quiser, eu tambem posso explicar as etapas da matricula ou como funciona o envio inicial desses documentos.
- `llamaindex`: status 200, latency 141.2ms, keyword pass `True`, quality `100`, reason `contextual_public_direct_answer`
  answer: Hoje os documentos exigidos para a matricula publicados pela escola sao:
- Formulario cadastral preenchido
- Documento de identificacao do aluno
- CPF do aluno, quando houver
- Historico escolar
- Comprovante de residencia atualizado
- Documento de identificacao do responsavel legal
Se quiser, eu tambem posso explicar as etapas da matricula ou como funciona o envio inicial desses documentos.
- `specialist_supervisor`: status 200, latency 107.0ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_tool_first:admissions_documents`
  answer: Hoje os documentos exigidos para matricula publicados pela escola sao:
- Formulario cadastral preenchido
- Documento de identificacao do aluno
- CPF do aluno, quando houver
- Historico escolar
- Comprovante de residencia atualizado
- Documento de identificacao do responsavel legal

### Como funciona a politica de avaliacao, recuperacao e promocao da escola?

- Slice: `public`
- Thread: `system_bank:retrieval_hibrido_sobre_documentos_publicos:Q018` turn `1`
- `langgraph`: status 200, latency 104.8ms, keyword pass `True`, quality `100`, reason `fato institucional canonico deve vir de fonte estruturada`
  answer: No Colegio Horizonte, a referencia publica de aprovacao e media 7,0/10. Quando a media fica abaixo da referencia, a escola combina monitorias, plantoes e orientacoes de recuperacao conforme o calendario pedagogico. A referencia publica de aprovacao usada nas orientacoes do colegio e 7,0, com fechamento final sempre acompanhado pela equipe pedagogica no periodo letivo.
- `crewai`: status 200, latency 525.6ms, keyword pass `True`, quality `100`, reason `crewai_public_fast_path`
  answer: A referencia publica de aprovacao hoje e media 7.0 na escala 0-10. Quando a media fica abaixo da referencia, a escola combina monitorias, plantoes e orientacoes de recuperacao conforme o calendario pedagogico.
- `python_functions`: status 200, latency 132.3ms, keyword pass `True`, quality `100`, reason `python_functions_native_contextual_public_answer`
  answer: No Colegio Horizonte, a referencia publica de aprovacao e media 7,0/10. Quando a media fica abaixo da referencia, a escola combina monitorias, plantoes e orientacoes de recuperacao conforme o calendario pedagogico. A referencia publica de aprovacao usada nas orientacoes do colegio e 7,0, com fechamento final sempre acompanhado pela equipe pedagogica no periodo letivo.
- `llamaindex`: status 200, latency 136.0ms, keyword pass `True`, quality `100`, reason `contextual_public_direct_answer`
  answer: No Colegio Horizonte, a referencia publica de aprovacao e media 7,0/10. Quando a media fica abaixo da referencia, a escola combina monitorias, plantoes e orientacoes de recuperacao conforme o calendario pedagogico. A referencia publica de aprovacao usada nas orientacoes do colegio e 7,0, com fechamento final sempre acompanhado pela equipe pedagogica no periodo letivo.
- `specialist_supervisor`: status 200, latency 158.4ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_tool_first:academic_policy_overview`
  answer: O processo avaliativo combina instrumentos formativos e somativos, como atividades em aula, projetos, producoes textuais, simulados e provas bimestrais. Resultados parciais sao apresentados ao estudante e a familia por meio do portal academico, reunioes e devolutivas pedagogicas. Quando houver desempenho abaixo do esperado, a escola pode oferecer recuperacao paralela, atividades orientadas, monitoria, estudo dirigido ou avaliacao substitutiva, conforme o componente e o periodo do ano. Pedidos de segunda chamada exigem justificativa no prazo orientado pela escola. Na referencia publica atual, a escola trabalha com media 7,0/10 e frequencia minima de 75,0% por componente. A promocao considera desempenho global, trajetoria do estudante, recuperacao realizada e frequencia.

### Quais sao as regras gerais de convivencia, frequencia e pontualidade?

- Slice: `public`
- Thread: `system_bank:retrieval_hibrido_sobre_documentos_publicos:Q019` turn `1`
- `langgraph`: status 200, latency 122.6ms, keyword pass `True`, quality `100`, reason `fato institucional canonico deve vir de fonte estruturada`
  answer: No Colegio Horizonte, a referencia publica minima de frequencia e 75,0% por componente. Se a frequencia de um componente cair abaixo de 75%, o estudante entra em alerta academico e a coordenacao pode acionar a familia. A permanencia abaixo desse limite pode comprometer a aprovacao por frequencia. A escola acompanha justificativas, recorrencia e necessidade de plano de recomposicao junto a familia e ao estudante.
- `crewai`: status 200, latency 172.8ms, keyword pass `True`, quality `100`, reason `crewai_protected_auth_required`
  answer: Essa consulta depende de autenticacao e vinculo da sua conta no Telegram. Use o portal da escola para gerar o codigo de vinculacao e depois envie o comando /start link_<codigo> ao bot.
- `python_functions`: status 200, latency 103.1ms, keyword pass `True`, quality `100`, reason `python_functions_native_contextual_public_answer`
  answer: No Colegio Horizonte, a referencia publica minima de frequencia e 75,0% por componente. Se a frequencia de um componente cair abaixo de 75%, o estudante entra em alerta academico e a coordenacao pode acionar a familia. A permanencia abaixo desse limite pode comprometer a aprovacao por frequencia. A escola acompanha justificativas, recorrencia e necessidade de plano de recomposicao junto a familia e ao estudante.
- `llamaindex`: status 200, latency 123.7ms, keyword pass `True`, quality `100`, reason `contextual_public_direct_answer`
  answer: No Colegio Horizonte, a referencia publica minima de frequencia e 75,0% por componente. Se a frequencia de um componente cair abaixo de 75%, o estudante entra em alerta academico e a coordenacao pode acionar a familia. A permanencia abaixo desse limite pode comprometer a aprovacao por frequencia. A escola acompanha justificativas, recorrencia e necessidade de plano de recomposicao junto a familia e ao estudante.
- `specialist_supervisor`: status 200, latency 100.2ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_tool_first:conduct_frequency_punctuality`
  answer: O estudante deve comparecer pontualmente as atividades letivas e cumprir a frequencia minima definida pela escola e pela legislacao aplicavel. A convivencia escolar deve observar respeito mutuo, cuidado com o patrimonio e linguagem adequada. Faltas em dias de avaliacao seguem a politica especifica de segunda chamada e recuperacao. A politica publica de frequencia reforca presenca minima de 75,0% por componente e alerta academico quando a recorrencia de faltas compromete a aprovacao. Se a frequencia de um componente cair abaixo de 75%, o estudante entra em alerta academico e a coordenacao pode acionar a familia.

### Como funciona o uso da biblioteca, dos laboratorios e dos recursos digitais?

- Slice: `public`
- Thread: `system_bank:retrieval_hibrido_sobre_documentos_publicos:Q020` turn `1`
- `langgraph`: status 200, latency 5359.4ms, keyword pass `True`, quality `100`, reason `fato institucional canonico deve vir de fonte estruturada`
  answer: Sim. O Colegio Horizonte tem a Biblioteca Aurora. Atendimento ao publico de segunda a sexta, das 7h30 as 18h00.
- `crewai`: status 200, latency 156.0ms, keyword pass `True`, quality `100`, reason `crewai_public_fast_path`
  answer: Sim. Biblioteca Aurora: biblioteca   Biblioteca Aurora   service   True   Atendimento ao publico de segunda a sexta, das 7h30 as 18h00..
- `python_functions`: status 200, latency 111.0ms, keyword pass `True`, quality `100`, reason `python_functions_native_contextual_public_answer`
  answer: A biblioteca se chama Biblioteca Aurora e funciona de segunda a sexta, das 7h30 as 18h00.
- `llamaindex`: status 200, latency 6043.3ms, keyword pass `True`, quality `100`, reason `llamaindex_public_profile`
  answer: Sim. O Colegio Horizonte tem a Biblioteca Aurora. Atendimento ao publico de segunda a sexta, das 7h30 as 18h00.
- `specialist_supervisor`: status 200, latency 100.1ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_fast_path:library_hours`
  answer: A biblioteca se chama Biblioteca Aurora e funciona Atendimento ao publico de segunda a sexta, das 7h30 as 18h00.

### Quais os prazos e canais para secretaria receber documentos, declaracoes e atualizacoes cadastrais?

- Slice: `public`
- Thread: `system_bank:retrieval_hibrido_sobre_documentos_publicos:Q021` turn `1`
- `langgraph`: status 200, latency 103.1ms, keyword pass `True`, quality `100`, reason `fato institucional canonico deve vir de fonte estruturada`
  answer: Sim. O envio inicial de documentos pode ser feito por canal digital.
Hoje os canais mais diretos publicados para isso sao:
- portal institucional
- email da secretaria
- secretaria presencial
Prazo esperado da secretaria: retorno em ate 2 dias uteis.
No processo de matricula, o envio inicial pode ser digital. A validacao final continua com a secretaria.
O chat aberto nao deve receber documentos completos ou dados sensiveis. Quando possivel, use o portal autenticado ou o email institucional.
- `crewai`: status 200, latency 141.5ms, keyword pass `True`, quality `100`, reason `crewai_public_fast_path`
  answer: Hoje a secretaria recebe documentos, declaracoes e atualizacoes cadastrais pelo portal institucional, pelo email da secretaria e pela secretaria presencial. Prazo esperado da secretaria: retorno em ate 2 dias uteis.
- `python_functions`: status 200, latency 102.9ms, keyword pass `True`, quality `100`, reason `python_functions_native_contextual_public_answer`
  answer: Sim. O envio inicial de documentos pode ser feito por canal digital.
Hoje os canais mais diretos publicados para isso sao:
- portal institucional
- email da secretaria
- secretaria presencial
Prazo esperado da secretaria: retorno em ate 2 dias uteis.
No processo de matricula, o envio inicial pode ser digital. A validacao final continua com a secretaria.
O chat aberto nao deve receber documentos completos ou dados sensiveis. Quando possivel, use o portal autenticado ou o email institucional.
- `llamaindex`: status 200, latency 120.1ms, keyword pass `True`, quality `100`, reason `contextual_public_direct_answer`
  answer: Sim. O envio inicial de documentos pode ser feito por canal digital.
Hoje os canais mais diretos publicados para isso sao:
- portal institucional
- email da secretaria
- secretaria presencial
Prazo esperado da secretaria: retorno em ate 2 dias uteis.
No processo de matricula, o envio inicial pode ser digital. A validacao final continua com a secretaria.
O chat aberto nao deve receber documentos completos ou dados sensiveis. Quando possivel, use o portal autenticado ou o email institucional.
- `specialist_supervisor`: status 200, latency 104.6ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_tool_first:document_submission_policy`
  answer: Voce pode mandar documentos pelo portal institucional, pelo email da secretaria ou levar na secretaria presencial para conferencia final. Prazo esperado da secretaria: retorno em ate 2 dias uteis. No processo de matricula, o envio inicial pode ser digital. A validacao final continua com a secretaria. O chat aberto nao deve receber documentos completos ou dados sensiveis. Quando possivel, use o portal autenticado ou o email institucional.

### O que a escola orienta sobre portal, aplicativo, senha, login e seguranca das credenciais?

- Slice: `public`
- Thread: `system_bank:retrieval_hibrido_sobre_documentos_publicos:Q022` turn `1`
- `langgraph`: status 200, latency 105.3ms, keyword pass `True`, quality `100`, reason `fato institucional canonico deve vir de fonte estruturada`
  answer: Aqui e o Colegio Horizonte. Se voce esta procurando o Orienta Sobre Portal, eu nao tenho acesso ao atendimento dessa outra instituicao. Se quiser, sigo te ajudando com o Colegio Horizonte por aqui.
- `crewai`: status 200, latency 140.1ms, keyword pass `True`, quality `100`, reason `crewai_public_fast_path`
  answer: Hoje a familia precisa entender quatro frentes publicas deste fluxo: Secretaria recebe declaracoes, historico, atualizacoes cadastrais e orientacoes administrativas. Portal institucional centraliza protocolo e envio digital inicial de documentos. Credenciais significam login e senha do portal; se voce perder o acesso, o melhor caminho e a secretaria ou o suporte digital. Documentos podem ser enviados pelo portal institucional, pelo email da secretaria ou pela secretaria presencial.
- `python_functions`: status 200, latency 106.5ms, keyword pass `True`, quality `100`, reason `python_functions_native_contextual_public_answer`
  answer: Hoje a familia precisa entender quatro frentes publicas deste fluxo:
- Secretaria: recebe declaracoes, historico, atualizacoes cadastrais e orientacoes administrativas.
- Portal institucional: centraliza protocolo e envio digital inicial de documentos.
- Credenciais: login e senha do portal continuam sendo a base de acesso; se precisar recuperar acesso, o melhor caminho e a secretaria ou o suporte digital.
- Documentos: o envio inicial pode ser feito por portal institucional, email da secretaria ou secretaria presencial.
O chat aberto nao deve receber documentos completos ou dados sensiveis. Quando possivel, use o portal autenticado ou o email institucional.
- `llamaindex`: status 200, latency 125.5ms, keyword pass `True`, quality `100`, reason `contextual_public_direct_answer`
  answer: Hoje a familia precisa entender quatro frentes publicas deste fluxo:
- Secretaria: recebe declaracoes, historico, atualizacoes cadastrais e orientacoes administrativas.
- Portal institucional: centraliza protocolo e envio digital inicial de documentos.
- Credenciais: login e senha do portal continuam sendo a base de acesso; se precisar recuperar acesso, o melhor caminho e a secretaria ou o suporte digital.
- Documentos: o envio inicial pode ser feito por portal institucional, email da secretaria ou secretaria presencial.
O chat aberto nao deve receber documentos completos ou dados sensiveis. Quando possivel, use o portal autenticado ou o email institucional.
- `specialist_supervisor`: status 200, latency 100.3ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_fast_path:service_credentials_bundle`
  answer: Hoje a familia precisa entender quatro frentes publicas deste fluxo:
- Secretaria: recebe declaracoes, historico, atualizacoes cadastrais e orientacoes administrativas.
- Portal institucional: centraliza protocolo e envio digital inicial de documentos.
- Credenciais: login e senha do portal continuam sendo a base de acesso; se voce perder o acesso, o melhor caminho e a secretaria ou o suporte digital.
- Documentos: o envio inicial pode ser feito por portal institucional, email da secretaria ou secretaria presencial.
O chat aberto nao deve receber documentos completos ou dados sensiveis. Quando possivel, use o portal autenticado ou o email institucional.

### Como funcionam bolsas, descontos e regras de rematricula, transferencia e cancelamento?

- Slice: `public`
- Thread: `system_bank:retrieval_hibrido_sobre_documentos_publicos:Q023` turn `1`
- `langgraph`: status 200, latency 112.0ms, keyword pass `True`, quality `100`, reason `fato institucional canonico deve vir de fonte estruturada`
  answer: O edital disciplina pedidos de bolsa social, desconto institucional, politica para irmaos e condicoes de manutencao do beneficio no ano letivo de 2026. Pedidos devem ser feitos dentro da janela informada pela escola, com envio de documentacao socioeconomica e demais comprovantes solicitados no regulamento especifico. A concessao de bolsas e descontos depende de analise documental, criterios internos, disponibilidade orcamentaria e validacao administrativa. Beneficios podem depender de cumprimento das condicoes previstas, como adimplencia, atualizacao cadastral e apresentacao tempestiva de documentos complementares quando solicitados. A rematricula para estudantes ja vinculados ao Colegio Horizonte ocorre em janela administrativa propria, divulgada no portal e reforcada pelos canais oficiais. Pedidos de transferencia para ingresso durante o ano letivo dependem de vaga, analise academica, conferencia documental e alinhamento com a serie pretendida. Quando a familia deseja transferir o aluno para outra instituicao, a solicitacao deve ser formalizada junto a secretaria. Pedidos de cancelamento devem ser apresentados pelo responsavel legal por canal oficial e podem exigir confirmacao adicional da secretaria ou do financeiro. Declaracoes simples costumam ser liberadas em ate dois dias uteis.
- `crewai`: status 200, latency 157.1ms, keyword pass `True`, quality `100`, reason `crewai_public_fast_path`
  answer: A mensalidade de referencia para Ensino Fundamental II e R$ 1280.00, com taxa de matricula de R$ 350.00.
- `python_functions`: status 200, latency 100.7ms, keyword pass `True`, quality `100`, reason `python_functions_native_contextual_public_answer`
  answer: O edital disciplina pedidos de bolsa social, desconto institucional, politica para irmaos e condicoes de manutencao do beneficio no ano letivo de 2026. Pedidos devem ser feitos dentro da janela informada pela escola, com envio de documentacao socioeconomica e demais comprovantes solicitados no regulamento especifico. A concessao de bolsas e descontos depende de analise documental, criterios internos, disponibilidade orcamentaria e validacao administrativa. Beneficios podem depender de cumprimento das condicoes previstas, como adimplencia, atualizacao cadastral e apresentacao tempestiva de documentos complementares quando solicitados. A rematricula para estudantes ja vinculados ao Colegio Horizonte ocorre em janela administrativa propria, divulgada no portal e reforcada pelos canais oficiais. Pedidos de transferencia para ingresso durante o ano letivo dependem de vaga, analise academica, conferencia documental e alinhamento com a serie pretendida. Quando a familia deseja transferir o aluno para outra instituicao, a solicitacao deve ser formalizada junto a secretaria. Pedidos de cancelamento devem ser apresentados pelo responsavel legal por canal oficial e podem exigir confirmacao adicional da secretaria ou do financeiro. Declaracoes simples costumam ser liberadas em ate dois dias uteis.
- `llamaindex`: status 200, latency 112.6ms, keyword pass `True`, quality `100`, reason `contextual_public_direct_answer`
  answer: O edital disciplina pedidos de bolsa social, desconto institucional, politica para irmaos e condicoes de manutencao do beneficio no ano letivo de 2026. Pedidos devem ser feitos dentro da janela informada pela escola, com envio de documentacao socioeconomica e demais comprovantes solicitados no regulamento especifico. A concessao de bolsas e descontos depende de analise documental, criterios internos, disponibilidade orcamentaria e validacao administrativa. Beneficios podem depender de cumprimento das condicoes previstas, como adimplencia, atualizacao cadastral e apresentacao tempestiva de documentos complementares quando solicitados. A rematricula para estudantes ja vinculados ao Colegio Horizonte ocorre em janela administrativa propria, divulgada no portal e reforcada pelos canais oficiais. Pedidos de transferencia para ingresso durante o ano letivo dependem de vaga, analise academica, conferencia documental e alinhamento com a serie pretendida. Quando a familia deseja transferir o aluno para outra instituicao, a solicitacao deve ser formalizada junto a secretaria. Pedidos de cancelamento devem ser apresentados pelo responsavel legal por canal oficial e podem exigir confirmacao adicional da secretaria ou do financeiro. Declaracoes simples costumam ser liberadas em ate dois dias uteis.
- `specialist_supervisor`: status 200, latency 103.0ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_fast_path:bolsas_and_processes`
  answer: O edital disciplina pedidos de bolsa social, desconto institucional, politica para irmaos e condicoes de manutencao do beneficio no ano letivo de 2026. Pedidos devem ser feitos dentro da janela informada pela escola, com envio de documentacao socioeconomica e demais comprovantes solicitados no regulamento especifico. A concessao de bolsas e descontos depende de analise documental, criterios internos, disponibilidade orcamentaria e validacao administrativa. Beneficios podem depender de cumprimento das condicoes previstas, como adimplencia, atualizacao cadastral e apresentacao tempestiva de documentos complementares quando solicitados. A rematricula para estudantes ja vinculados ao Colegio Horizonte ocorre em janela administrativa propria, divulgada no portal e reforcada pelos canais oficiais. Pedidos de transferencia para ingresso durante o ano letivo dependem de vaga, analise academica, conferencia documental e alinhamento com a serie pretendida. Quando a familia deseja transferir o aluno para outra instituicao, a solicitacao deve ser formalizada junto a secretaria. Pedidos de cancelamento devem ser apresentados pelo responsavel legal por canal oficial e podem exigir confirmacao adicional da secretaria ou do financeiro. Declaracoes simples costumam ser liberadas em ate dois dias uteis.

### Se eu faltar por motivo de saude e perder uma prova, onde a escola explica o que devo fazer?

- Slice: `public`
- Thread: `system_bank:retrieval_hibrido_sobre_documentos_publicos:Q024` turn `1`
- `langgraph`: status 200, latency 1816.5ms, keyword pass `True`, quality `100`, reason `planejamento semantico publico encontrou um ato estruturado mais adequado ao turno`
  answer: Aqui e o Colegio Horizonte. Se voce esta procurando o Explica Que Devo, eu nao tenho acesso ao atendimento dessa outra instituicao. Se quiser, sigo te ajudando com o Colegio Horizonte por aqui.
- `crewai`: status 200, latency 165.8ms, keyword pass `True`, quality `100`, reason `crewai_protected_auth_required`
  answer: Essa consulta depende de autenticacao e vinculo da sua conta no Telegram. Use o portal da escola para gerar o codigo de vinculacao e depois envie o comando /start link_<codigo> ao bot.
- `python_functions`: status 200, latency 101.1ms, keyword pass `True`, quality `100`, reason `python_functions_native_contextual_public_answer`
  answer: Atestados medicos e justificativas formais podem ser usados para apoiar analise de ausencia, segunda chamada ou adaptacao temporaria de rotina. Pedidos de segunda chamada exigem justificativa no prazo orientado pela escola.
- `llamaindex`: status 200, latency 114.5ms, keyword pass `True`, quality `100`, reason `contextual_public_direct_answer`
  answer: Atestados medicos e justificativas formais podem ser usados para apoiar analise de ausencia, segunda chamada ou adaptacao temporaria de rotina. Pedidos de segunda chamada exigem justificativa no prazo orientado pela escola.
- `specialist_supervisor`: status 200, latency 100.6ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_fast_path:health_second_call`
  answer: Atestados medicos e justificativas formais podem ser usados para apoiar analise de ausencia, segunda chamada ou adaptacao temporaria de rotina. Pedidos de segunda chamada exigem justificativa no prazo orientado pela escola.

