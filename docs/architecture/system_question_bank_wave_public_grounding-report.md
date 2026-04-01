# Five-Path Chatbot Comparison Report

Date: 2026-04-01T04:13:38.052977+00:00

Dataset: `tests/evals/datasets/system_question_bank_wave_public_grounding.json`

Run prefix: `debug:five-path:20260401T040505Z`

## Stack Summary

| Stack | OK | Keyword pass | Quality | Avg latency |
| --- | --- | --- | --- | --- |
| `langgraph` | `24/24` | `24/24` | `100.0` | `3898.3 ms` |
| `crewai` | `24/24` | `24/24` | `100.0` | `5982.7 ms` |
| `python_functions` | `24/24` | `24/24` | `100.0` | `293.4 ms` |
| `llamaindex` | `24/24` | `24/24` | `100.0` | `10445.9 ms` |
| `specialist_supervisor` | `24/24` | `24/24` | `100.0` | `649.8 ms` |

## By Slice

- `public`
  - `langgraph`: ok 24/24, keyword pass 24/24, quality 100.0, latency 3898.3ms
  - `crewai`: ok 24/24, keyword pass 24/24, quality 100.0, latency 5982.7ms
  - `python_functions`: ok 24/24, keyword pass 24/24, quality 100.0, latency 293.4ms
  - `llamaindex`: ok 24/24, keyword pass 24/24, quality 100.0, latency 10445.9ms
  - `specialist_supervisor`: ok 24/24, keyword pass 24/24, quality 100.0, latency 649.8ms

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
- `langgraph`: status 200, latency 4115.3ms, keyword pass `True`, quality `100`, reason `fato institucional canonico deve vir de fonte estruturada`
  answer: Olá! O Colégio Horizonte está localizado na Rua das Acácias, 1450, Vila Mariana, São Paulo, SP, CEP 04567-120. Para falar conosco, o telefone principal é (11) 3333-4200, e o canal mais direto para a secretaria hoje é o WhatsApp, no número (11) 97500-2041.
- `crewai`: status 200, latency 238.1ms, keyword pass `True`, quality `100`, reason `crewai_public_fast_path`
  answer: Endereco: Rua das Acacias, 1450, Vila Mariana, Sao Paulo/SP, CEP 04567-120 O telefone principal hoje e (11) 3333-4200. O melhor canal para a secretaria hoje e (11) 97500-2040.
- `python_functions`: status 200, latency 136.5ms, keyword pass `True`, quality `100`, reason `python_functions_native_contextual_public_answer`
  answer: O endereco publicado de Colegio Horizonte hoje e Rua das Acacias, 1450, Vila Mariana, Sao Paulo, SP, CEP 04567-120. O telefone principal hoje e (11) 3333-4200. O canal mais direto para falar com a secretaria hoje e o WhatsApp (11) 97500-2041.
- `llamaindex`: status 200, latency 10700.3ms, keyword pass `True`, quality `100`, reason `llamaindex_public_profile`
  answer: O endereco publicado de Colegio Horizonte hoje e Rua das Acacias, 1450, Vila Mariana, Sao Paulo, SP, CEP 04567-120. O telefone principal hoje e (11) 3333-4200. O canal mais direto para falar com a secretaria hoje e o WhatsApp (11) 97500-2041.
- `specialist_supervisor`: status 200, latency 136.4ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_fast_path:contact_bundle`
  answer: O endereco completo da escola hoje e Rua das Acacias, 1450, Vila Mariana, Sao Paulo, SP, CEP 04567-120. O telefone principal e (11) 3333-4200. O melhor canal para a secretaria hoje e o WhatsApp (11) 97500-2041.

### Essa escola tem biblioteca de verdade ou so fala que tem? Qual e o nome e o horario?

- Slice: `public`
- Thread: `system_bank:publico_estruturado_institucional:Q002` turn `1`
- `langgraph`: status 200, latency 5676.8ms, keyword pass `True`, quality `100`, reason `fato institucional canonico deve vir de fonte estruturada`
  answer: Que bom que você perguntou! Sim, temos uma biblioteca de verdade, a Biblioteca Aurora, e ela está aberta de segunda a sexta-feira, das 7h30 às 18h00, para atender a todos.
- `crewai`: status 200, latency 186.6ms, keyword pass `True`, quality `100`, reason `crewai_public_fast_path`
  answer: Sim. Biblioteca Aurora: biblioteca   Biblioteca Aurora   service   True   Atendimento ao publico de segunda a sexta, das 7h30 as 18h00..
- `python_functions`: status 200, latency 161.9ms, keyword pass `True`, quality `100`, reason `python_functions_native_structured:institution`
  answer: O horario de Biblioteca Aurora hoje funciona assim: Atendimento ao publico de segunda a sexta, das 7h30 as 18h00.

Turnos e horarios documentados:
- Ensino Fundamental II (Manha): 07:15 as 12:30. Oficinas, plantoes, esportes e estudo orientado no contraturno em dias alternados.
- Ensino Medio (Manha): 07:15 as 12:50. Trilhas eletivas, monitorias e laboratorios no contraturno a partir das 14h00.
- Fundamental II e Ensino Medio (Integral opcional): 07:00 as 17:30. Inclui estudo orientado, almoco, oficinas, esportes e acompanhamento no contraturno.
- `llamaindex`: status 200, latency 10896.6ms, keyword pass `True`, quality `100`, reason `llamaindex_public_profile`
  answer: O horario de Biblioteca Aurora hoje funciona assim: Atendimento ao publico de segunda a sexta, das 7h30 as 18h00.

Turnos e horarios documentados:
- Ensino Fundamental II (Manha): 07:15 as 12:30. Oficinas, plantoes, esportes e estudo orientado no contraturno em dias alternados.
- Ensino Medio (Manha): 07:15 as 12:50. Trilhas eletivas, monitorias e laboratorios no contraturno a partir das 14h00.
- Fundamental II e Ensino Medio (Integral opcional): 07:00 as 17:30. Inclui estudo orientado, almoco, oficinas, esportes e acompanhamento no contraturno.
- `specialist_supervisor`: status 200, latency 120.5ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_fast_path:library_hours`
  answer: A biblioteca se chama Biblioteca Aurora e funciona Atendimento ao publico de segunda a sexta, das 7h30 as 18h00.

### Quem responde por direcao, orientacao educacional e atendimento comercial?

- Slice: `public`
- Thread: `system_bank:publico_estruturado_institucional:Q003` turn `1`
- `langgraph`: status 200, latency 4007.1ms, keyword pass `True`, quality `100`, reason `fato institucional canonico deve vir de fonte estruturada`
  answer: Olá! No Colégio Horizonte, a nossa diretora geral é a Helena Martins, e você pode entrar em contato com ela pelo e-mail direcao@colegiohorizonte.edu.br. Para assuntos de orientação educacional, você pode falar com o nosso bot, o setor de orientação educacional ou a secretaria. Já para atendimento comercial e admissões, temos o bot, o setor de admissões, nosso WhatsApp comercial ou você pode agendar uma visita guiada.
- `crewai`: status 200, latency 183.2ms, keyword pass `True`, quality `100`, reason `crewai_public_fast_path`
  answer: Direcao geral: Helena Martins.
Para bolsa, desconto e matricula, o melhor canal hoje e Atendimento comercial / Admissoes. Admissoes (telefone): (11) 3333-4201
Para bullying, convivencia e apoio escolar, o canal indicado e a orientacao educacional. Orientacao educacional (telefone): (11) 3333-4202
- `python_functions`: status 200, latency 125.9ms, keyword pass `True`, quality `100`, reason `python_functions_native_contextual_public_answer`
  answer: Hoje estes sao os responsaveis e canais mais diretos por assunto:
- Diretora geral: Helena Martins. Canal institucional: direcao@colegiohorizonte.edu.br.
- Atendimento comercial / Admissoes: bot, admissions, whatsapp comercial ou visita guiada.
- Orientacao educacional: bot, orientacao educacional ou secretaria.
- `llamaindex`: status 200, latency 21839.0ms, keyword pass `True`, quality `100`, reason `llamaindex_public_profile`
  answer: Hoje estes sao os responsaveis e canais mais diretos por assunto:
- Diretora geral: Helena Martins. Canal institucional: direcao@colegiohorizonte.edu.br.
- Atendimento comercial / Admissoes: bot, admissions, whatsapp comercial ou visita guiada.
- Orientacao educacional: bot, orientacao educacional ou secretaria.
- `specialist_supervisor`: status 200, latency 152.3ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_fast_path:service_routing`
  answer: Hoje estes sao os responsaveis e canais mais diretos por assunto:
- Diretora geral: Helena Martins. Canal institucional: direcao@colegiohorizonte.edu.br.
- Atendimento comercial / Admissoes: bot, admissions, whatsapp comercial ou visita guiada.
- Orientacao educacional: bot, orientacao educacional ou secretaria.
- Direcao: bot, ouvidoria ou protocolo institucional.

### Se eu fosse uma familia nova e tivesse so 30 segundos, o que voce me diria sobre essa escola?

- Slice: `public`
- Thread: `system_bank:publico_estruturado_institucional:Q004` turn `1`
- `langgraph`: status 200, latency 2249.7ms, keyword pass `True`, quality `100`, reason `fato institucional canonico deve vir de fonte estruturada`
  answer: Se eu tivesse 30 segundos para resumir Colegio Horizonte, eu diria isto: Escola laica com Ensino Fundamental II e Ensino Medio, acompanhamento tutorial e trilhas academicas no contraturno. Os diferenciais publicados com mais clareza hoje passam por Tutoria academica e projeto de vida, Espaco Maker integrado ao curriculo, Acolhimento estruturado para familias e estudantes. A proposta pedagogica publicada combina Projeto pedagogico laico, com foco em aprendizagem por projetos, cultura digital responsavel, acompanhamento socioemocional e preparacao academica progressiva.. Na pratica, isso aparece em aprendizagem por projetos, acompanhamento mais proximo, estudo orientado e contraturno com referencias claras para familias.
- `crewai`: status 200, latency 206.4ms, keyword pass `True`, quality `100`, reason `crewai_public_fast_path`
  answer: Se eu tivesse 30 segundos para resumir esta escola, eu diria isto: ela combina aprendizagem por projetos, acompanhamento mais proximo e trilhas academicas no contraturno. No que esta publicado aqui, os diferenciais mais claros passam por Tutoria academica e projeto de vida, Espaco Maker integrado ao curriculo. Colegio Horizonte em Sao Paulo/SP. Escola laica com Ensino Fundamental II e Ensino Medio, acompanhamento tutorial e trilhas academicas no contraturno. Projeto pedagogico laico, com foco em aprendizagem por projetos, cultura digital responsavel, acompanhamento socioemocional e preparacao academica progressiva.
- `python_functions`: status 200, latency 129.8ms, keyword pass `True`, quality `100`, reason `python_functions_native_contextual_public_answer`
  answer: Se eu tivesse 30 segundos para resumir Colegio Horizonte, eu diria isto: Escola laica com Ensino Fundamental II e Ensino Medio, acompanhamento tutorial e trilhas academicas no contraturno. Os diferenciais publicados com mais clareza hoje passam por Tutoria academica e projeto de vida, Espaco Maker integrado ao curriculo, Acolhimento estruturado para familias e estudantes. A proposta pedagogica publicada combina Projeto pedagogico laico, com foco em aprendizagem por projetos, cultura digital responsavel, acompanhamento socioemocional e preparacao academica progressiva.. Na pratica, isso aparece em aprendizagem por projetos, acompanhamento mais proximo, estudo orientado e contraturno com referencias claras para familias.
- `llamaindex`: status 200, latency 19381.4ms, keyword pass `True`, quality `100`, reason `llamaindex_public_profile`
  answer: Se eu tivesse 30 segundos para resumir Colegio Horizonte, eu diria isto: Escola laica com Ensino Fundamental II e Ensino Medio, acompanhamento tutorial e trilhas academicas no contraturno. Os diferenciais publicados com mais clareza hoje passam por Tutoria academica e projeto de vida, Espaco Maker integrado ao curriculo, Acolhimento estruturado para familias e estudantes. A proposta pedagogica publicada combina Projeto pedagogico laico, com foco em aprendizagem por projetos, cultura digital responsavel, acompanhamento socioemocional e preparacao academica progressiva.. Na pratica, isso aparece em aprendizagem por projetos, acompanhamento mais proximo, estudo orientado e contraturno com referencias claras para familias.
- `specialist_supervisor`: status 200, latency 125.7ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_fast_path:public_pitch`
  answer: Se eu tivesse 30 segundos para resumir esta escola, eu diria isto: ela combina aprendizagem por projetos, acompanhamento mais proximo e trilhas academicas no contraturno. A proposta pedagogica publicada hoje combina Projeto pedagogico laico, com foco em aprendizagem por projetos, cultura digital responsavel, acompanhamento socioemocional e preparacao academica progressiva.. No Ensino Medio, isso aparece junto de A escola segue a BNCC e o curriculo do Ensino Medio articulado com projeto de vida, producao textual, cultura digital e aprofundamento academico progressivo.. Escola laica com Ensino Fundamental II e Ensino Medio, acompanhamento tutorial e trilhas academicas no contraturno. Na pratica, isso aparece em acompanhamento mais proximo da aprendizagem, projeto de vida e uma rotina pedagogica mais explicita no dia a dia.

### O colegio divulga nomes e contatos diretos de professores por disciplina?

- Slice: `public`
- Thread: `system_bank:publico_estruturado_institucional:Q005` turn `1`
- `langgraph`: status 200, latency 131.4ms, keyword pass `True`, quality `100`, reason `a consulta exige autenticacao ou vinculo antes de qualquer acesso`
  answer: Aqui e o Colegio Horizonte. Se voce esta procurando o Divulga Nomes E Contatos, eu nao tenho acesso ao atendimento dessa outra instituicao. Se quiser, sigo te ajudando com o Colegio Horizonte por aqui.
- `crewai`: status 200, latency 209.3ms, keyword pass `True`, quality `100`, reason `crewai_public_fast_path`
  answer: Hoje a escola divulga atividades e espacos complementares como Biblioteca Aurora, Espaco Maker, futsal, volei escolar. Se quiser, eu tambem posso detalhar Biblioteca Aurora, Laboratorio de Ciencias, Espaco Maker, Quadra Poliesportiva Coberta.
- `python_functions`: status 200, latency 136.4ms, keyword pass `True`, quality `100`, reason `a consulta exige autenticacao ou vinculo antes de qualquer acesso`
  answer: Essa consulta depende de autenticacao e vinculo da sua conta no Telegram. Use o portal da escola para gerar o codigo de vinculacao e depois envie o comando `/start link_<codigo>` ao bot.
- `llamaindex`: status 200, latency 138.6ms, keyword pass `True`, quality `100`, reason `a consulta exige autenticacao ou vinculo antes de qualquer acesso`
  answer: Essa consulta depende de autenticacao e vinculo da sua conta no Telegram. Use o portal da escola para gerar o codigo de vinculacao e depois envie o comando `/start link_<codigo>` ao bot.
- `specialist_supervisor`: status 200, latency 9671.3ms, keyword pass `True`, quality `100`, reason `A consulta solicita informações sensíveis (contatos diretos de professores) que são protegidas por políticas de privacidade institucionais. O Colégio Horizonte provavelmente não divulga tais dados publicamente. A estratégia de negação é apropriada, alinhada com a decisão de segurança do sistema (preview) que indica a necessidade de autenticação ou vínculo para acesso a informações desta natureza.`
  answer: A divulgação de nomes e contatos diretos de professores por disciplina é uma informação sensível e protegida por políticas de privacidade institucionais, que geralmente não são divulgadas publicamente e podem exigir autenticação ou um vínculo específico para acesso.

### Em qual bairro de Sao Paulo a escola fica e quais sao os principais referenciais de acesso?

- Slice: `public`
- Thread: `system_bank:publico_estruturado_institucional:Q006` turn `1`
- `langgraph`: status 200, latency 5876.3ms, keyword pass `True`, quality `100`, reason `fato institucional canonico deve vir de fonte estruturada`
  answer: Olá! O Colégio Horizonte está localizado na Rua das Acácias, 1450, na Vila Mariana, em São Paulo. É um bairro de fácil acesso, com diversas opções de transporte público e próximo a importantes vias da cidade.
- `crewai`: status 200, latency 20241.4ms, keyword pass `True`, quality `100`, reason `crewai_public_flow_timeout`
  answer: Para te ajudar com o endereço da escola, preciso de mais informações. Não encontrei o endereço nos documentos disponíveis. Você poderia me dizer o nome da escola ou onde você viu essa informação?
- `python_functions`: status 200, latency 173.6ms, keyword pass `True`, quality `100`, reason `python_functions_native_structured:institution`
  answer: Colegio Horizonte fica em Rua das Acacias, 1450, Vila Mariana, Sao Paulo, SP, CEP 04567-120.
- `llamaindex`: status 200, latency 11328.2ms, keyword pass `True`, quality `100`, reason `llamaindex_public_profile`
  answer: Colegio Horizonte fica em Rua das Acacias, 1450, Vila Mariana, Sao Paulo, SP, CEP 04567-120.
- `specialist_supervisor`: status 200, latency 123.6ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_fast_path:district`
  answer: A escola fica no bairro Vila Mariana, Sao Paulo/SP.

### Com quem eu falo sobre bolsa, com quem eu falo sobre boletos e com quem eu falo sobre bullying?

- Slice: `public`
- Thread: `system_bank:publico_estruturado_institucional:Q007` turn `1`
- `langgraph`: status 200, latency 1907.9ms, keyword pass `True`, quality `100`, reason `fato institucional canonico deve vir de fonte estruturada`
  answer: Hoje estes sao os responsaveis e canais mais diretos por assunto:
- Atendimento comercial / Admissoes: bot, admissions, whatsapp comercial ou visita guiada.
- Financeiro: bot, financeiro, portal autenticado ou email institucional.
- Orientacao educacional: bot, orientacao educacional ou secretaria.
- `crewai`: status 200, latency 235.5ms, keyword pass `True`, quality `100`, reason `crewai_public_fast_path`
  answer: Para bolsa, desconto e matricula, o melhor canal hoje e Atendimento comercial / Admissoes. Admissoes (telefone): (11) 3333-4201
Para boletos, vencimentos e contratos, o melhor canal hoje e o financeiro. Financeiro (telefone): (11) 3333-4203
Para bullying, convivencia e apoio escolar, o canal indicado e a orientacao educacional. Orientacao educacional (telefone): (11) 3333-4202
- `python_functions`: status 200, latency 140.8ms, keyword pass `True`, quality `100`, reason `python_functions_native_contextual_public_answer`
  answer: Hoje estes sao os responsaveis e canais mais diretos por assunto:
- Atendimento comercial / Admissoes: bot, admissions, whatsapp comercial ou visita guiada.
- Financeiro: bot, financeiro, portal autenticado ou email institucional.
- Orientacao educacional: bot, orientacao educacional ou secretaria.
- `llamaindex`: status 200, latency 6258.8ms, keyword pass `True`, quality `100`, reason `llamaindex_public_profile`
  answer: Hoje estes sao os responsaveis e canais mais diretos por assunto:
- Atendimento comercial / Admissoes: bot, admissions, whatsapp comercial ou visita guiada.
- Financeiro: bot, financeiro, portal autenticado ou email institucional.
- Orientacao educacional: bot, orientacao educacional ou secretaria.
- `specialist_supervisor`: status 200, latency 181.3ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_fast_path:service_routing`
  answer: Hoje estes sao os responsaveis e canais mais diretos por assunto:
- Atendimento comercial / Admissoes: bot, admissions, whatsapp comercial ou visita guiada.
- Financeiro: bot, financeiro, portal autenticado ou email institucional.
- Orientacao educacional: bot, orientacao educacional ou secretaria.

### Qual a diferenca entre falar com secretaria, coordenacao e orientacao educacional?

- Slice: `public`
- Thread: `system_bank:publico_estruturado_institucional:Q008` turn `1`
- `langgraph`: status 200, latency 6632.6ms, keyword pass `True`, quality `100`, reason `fato institucional canonico deve vir de fonte estruturada`
  answer: Olá! Para te ajudar a falar com a pessoa certa, vou explicar as diferenças:

A Secretaria cuida de toda a parte administrativa e de documentos, como matrículas, transferências e históricos. A Coordenação Pedagógica é responsável pelo acompanhamento do aprendizado e do currículo, além de dar suporte aos professores. Já a Orientação Educacional foca no desenvolvimento socioemocional dos alunos, auxiliando em questões de comportamento, adaptação e escolha profissional.

No momento, não encontrei informações detalhadas sobre a Orientação Educacional no perfil público do Colégio Horizonte. Se desejar, posso te mostrar o que está documentado sobre a estrutura e as atividades da escola.

Para falar com a diretora geral, o canal é direcao@colegiohorizonte.edu.br. Ela atende por agenda e participa dos encontros de famílias a cada bimestre.
- `crewai`: status 200, latency 18137.5ms, keyword pass `True`, quality `100`, reason `crewai_public_flow_completed`
  answer: Claro! Os departamentos escolares têm funções distintas para atender às diferentes etapas da educação. O Departamento de Educação Infantil (DEI) planeja, coordena e supervisiona as ações pedagógicas e administrativas da educação infantil, incluindo a elaboração de propostas curriculares, a formação de professores e o acompanhamento do desenvolvimento das crianças. Já o Departamento de Ensino Fundamental (DEF) coordena e supervisiona as atividades pedagógicas e administrativas do ensino fundamental, como a elaboração de currículos, a formação continuada de professores e a avaliação do processo de ensino-aprendizagem. Por fim, o Departamento de Educação Especial (DEE) garante o acesso, a participação e a aprendizagem de estudantes com deficiência, transtornos globais do desenvolvimento e altas habilidades/superdotação, oferecendo apoio pedagógico especializado, recursos e serviços para a inclusão educacional.
- `python_functions`: status 200, latency 164.7ms, keyword pass `True`, quality `100`, reason `python_functions_native_structured:institution`
  answer: Sim. O Colegio Horizonte oferece Orientacao educacional. Acompanhamento socioemocional, mediacao escolar e apoio a familias.

Voce pode falar com a diretora geral pelo canal institucional direcao@colegiohorizonte.edu.br. Atende por agenda institucional e participa dos encontros de familias a cada bimestre.
- `llamaindex`: status 200, latency 10615.2ms, keyword pass `True`, quality `100`, reason `fato institucional canonico deve vir de fonte estruturada`
  answer: Sim. O Colegio Horizonte oferece Orientacao educacional. Acompanhamento socioemocional, mediacao escolar e apoio a familias.

Voce pode falar com a diretora geral pelo canal institucional direcao@colegiohorizonte.edu.br. Atende por agenda institucional e participa dos encontros de familias a cada bimestre.
- `specialist_supervisor`: status 200, latency 189.3ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_tool_first:human_handoff`
  answer: Encaminhei sua solicitacao para a fila de coordenacao. Protocolo: ATD-20260401-2296223A. Status atual: queued. Se preferir, voce tambem pode seguir pelo WhatsApp oficial (11) 97500-2040.

### Quando abre a matricula de 2026 e quando comecam as aulas?

- Slice: `public`
- Thread: `system_bank:timeline_e_calendario_publico:Q009` turn `1`
- `langgraph`: status 200, latency 5743.2ms, keyword pass `True`, quality `100`, reason `datas institucionais publicas devem vir de leitura estruturada e auditavel`
  answer: Olá! As matrículas para 2026 no Colégio Horizonte abriram em 6 de outubro de 2025, com pré-cadastro e visita orientada. As aulas para o Ensino Fundamental II e Ensino Médio começam em 2 de fevereiro de 2026, e a semana de acolhimento para o 6º ano e 1ª série será de 2 a 6 de fevereiro.
- `crewai`: status 200, latency 199.9ms, keyword pass `True`, quality `100`, reason `crewai_public_fast_path`
  answer: O ciclo publico de matricula para 2026 foi aberto em 6 de outubro de 2025, com pre-cadastro, visita orientada opcional e triagem inicial de documentos. | 2025-10-06 | familias interessadas | O atendimento comercial segue enquanto houver vagas por segmento.
As aulas do Ensino Fundamental II e do Ensino Medio comecam em 2 de fevereiro de 2026. | 2026-02-02 | alunos e familias | A semana de acolhimento do 6o ano e da primeira serie ocorre entre 2 e 6 de fevereiro.
- `python_functions`: status 200, latency 117.0ms, keyword pass `True`, quality `100`, reason `python_functions_native_contextual_public_answer`
  answer: O ciclo publico de matricula para 2026 foi aberto em 6 de outubro de 2025, com pre-cadastro, visita orientada opcional e triagem inicial de documentos. O atendimento comercial segue enquanto houver vagas por segmento.
As aulas do Ensino Fundamental II e do Ensino Medio comecam em 2 de fevereiro de 2026. A semana de acolhimento do 6o ano e da primeira serie ocorre entre 2 e 6 de fevereiro.
- `llamaindex`: status 200, latency 10316.5ms, keyword pass `True`, quality `100`, reason `llamaindex_public_profile`
  answer: O ciclo publico de matricula para 2026 foi aberto em 6 de outubro de 2025, com pre-cadastro, visita orientada opcional e triagem inicial de documentos. O atendimento comercial segue enquanto houver vagas por segmento.
As aulas do Ensino Fundamental II e do Ensino Medio comecam em 2 de fevereiro de 2026. A semana de acolhimento do 6o ano e da primeira serie ocorre entre 2 e 6 de fevereiro.
- `specialist_supervisor`: status 200, latency 125.8ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_tool_first:public_timeline_bundle`
  answer: O ciclo publico de matricula para 2026 foi aberto em 6 de outubro de 2025, com pre-cadastro, visita orientada opcional e triagem inicial de documentos. O atendimento comercial segue enquanto houver vagas por segmento.
As aulas do Ensino Fundamental II e do Ensino Medio comecam em 2 de fevereiro de 2026. A semana de acolhimento do 6o ano e da primeira serie ocorre entre 2 e 6 de fevereiro.

### Quais sao os principais eventos publicos desta semana para familias e responsaveis?

- Slice: `public`
- Thread: `system_bank:timeline_e_calendario_publico:Q010` turn `1`
- `langgraph`: status 200, latency 2070.4ms, keyword pass `True`, quality `100`, reason `a intencao esta ambigua e exige clarificacao antes de recuperar contexto`
  answer: No momento, não tenho informações sobre os eventos públicos desta semana para famílias e responsáveis.

Para ter acesso ao calendário completo e atualizado, sugiro que verifique o portal da escola ou entre em contato com a Secretaria Escolar. Eles poderão te informar sobre os próximos eventos.
- `crewai`: status 200, latency 20249.9ms, keyword pass `True`, quality `100`, reason `crewai_public_flow_timeout`
  answer: Olá! A data do evento "Visita guiada para famílias interessadas" é 06 de abril de 2026. Você gostaria de saber sobre eventos em uma semana específica ou este evento é relevante para sua consulta?
- `python_functions`: status 200, latency 179.7ms, keyword pass `True`, quality `100`, reason `a intencao esta ambigua e exige clarificacao antes de recuperar contexto`
  answer: Posso ajudar com informacoes publicas da escola, como calendario, matricula, documentos exigidos e regras de atendimento digital. Se quiser, pergunte por exemplo: "quais documentos preciso para a matricula?" ou "quando acontece a reuniao de pais?".
- `llamaindex`: status 200, latency 6880.0ms, keyword pass `True`, quality `100`, reason `llamaindex_public_profile`
  answer: Hoje a base publica de eventos de Colegio Horizonte nao trouxe agenda estruturada para esse pedido.
- `specialist_supervisor`: status 200, latency 107.0ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_tool_first:calendar_week`
  answer: Os principais eventos publicos para familias e responsaveis nesta base sao:
- Reuniao geral de pais e responsaveis (28/03/2026) · publico: public. Apresentacao do planejamento do primeiro bimestre.
- Reuniao de responsaveis do 6o ao 9o ano (28/03/2026) · publico: public. Apresentacao das rotinas do Fundamental II, canais oficiais e acompanhamento pedagógico.
- Reuniao de responsaveis do Ensino Medio (29/03/2026) · publico: public. Apresentacao das rotinas do Ensino Medio, avaliacao e apoio a vestibulares.
- Visita guiada para familias interessadas (06/04/2026) · publico: public. Apresentacao institucional do Fundamental II e Ensino Medio com tour pelos espacos.

### Monte uma linha do tempo do primeiro bimestre com datas que importam para pais e alunos.

- Slice: `public`
- Thread: `system_bank:timeline_e_calendario_publico:Q011` turn `1`
- `langgraph`: status 200, latency 124.8ms, keyword pass `True`, quality `100`, reason `a consulta exige autenticacao ou vinculo antes de qualquer acesso`
  answer: Essa consulta depende de autenticacao e vinculo da sua conta no Telegram. Use o portal da escola para gerar o codigo de vinculacao e depois envie o comando `/start link_<codigo>` ao bot.
- `crewai`: status 200, latency 19578.0ms, keyword pass `True`, quality `100`, reason `crewai_public_flow_completed`
  answer: O primeiro bimestre letivo de 2024 vai de 19 de fevereiro a 26 de abril. Espero que ajude a se organizar!
- `python_functions`: status 200, latency 134.5ms, keyword pass `True`, quality `100`, reason `a consulta exige autenticacao ou vinculo antes de qualquer acesso`
  answer: Essa consulta depende de autenticacao e vinculo da sua conta no Telegram. Use o portal da escola para gerar o codigo de vinculacao e depois envie o comando `/start link_<codigo>` ao bot.
- `llamaindex`: status 200, latency 176.2ms, keyword pass `True`, quality `100`, reason `a consulta exige autenticacao ou vinculo antes de qualquer acesso`
  answer: Essa consulta depende de autenticacao e vinculo da sua conta no Telegram. Use o portal da escola para gerar o codigo de vinculacao e depois envie o comando `/start link_<codigo>` ao bot.
- `specialist_supervisor`: status 200, latency 122.4ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_tool_first:first_bimester_timeline`
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
- `langgraph`: status 200, latency 5765.2ms, keyword pass `True`, quality `100`, reason `datas institucionais publicas devem vir de leitura estruturada e auditavel`
  answer: As aulas do Ensino Fundamental II e do Ensino Medio comecam em 2 de fevereiro de 2026. A semana de acolhimento do 6o ano e da primeira serie ocorre entre 2 e 6 de fevereiro.
- `crewai`: status 200, latency 206.7ms, keyword pass `True`, quality `100`, reason `crewai_protected_auth_required`
  answer: Essa consulta depende de autenticacao e vinculo da sua conta no Telegram. Use o portal da escola para gerar o codigo de vinculacao e depois envie o comando /start link_<codigo> ao bot.
- `python_functions`: status 200, latency 148.5ms, keyword pass `True`, quality `100`, reason `python_functions_native_contextual_public_answer`
  answer: As aulas do Ensino Fundamental II e do Ensino Medio comecam em 2 de fevereiro de 2026. A semana de acolhimento do 6o ano e da primeira serie ocorre entre 2 e 6 de fevereiro.
- `llamaindex`: status 200, latency 8683.6ms, keyword pass `True`, quality `100`, reason `llamaindex_public_profile`
  answer: As aulas do Ensino Fundamental II e do Ensino Medio comecam em 2 de fevereiro de 2026. A semana de acolhimento do 6o ano e da primeira serie ocorre entre 2 e 6 de fevereiro.
- `specialist_supervisor`: status 200, latency 129.3ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_tool_first:eval_calendar`
  answer: No calendario publico atual, estes sao os marcos mais relevantes para reunioes, simulados e semanas de prova:
- Reuniao geral de pais e responsaveis (28/03/2026) · publico: public. Apresentacao do planejamento do primeiro bimestre.
- Reuniao de responsaveis do 6o ao 9o ano (28/03/2026) · publico: public. Apresentacao das rotinas do Fundamental II, canais oficiais e acompanhamento pedagógico.
- Reuniao de responsaveis do Ensino Medio (29/03/2026) · publico: public. Apresentacao das rotinas do Ensino Medio, avaliacao e apoio a vestibulares.
- Plantao pedagogico do primeiro bimestre (11/04/2026) · publico: public. Atendimento com professores para esclarecimento de notas e frequencia.

### O que acontece antes da confirmacao da vaga e o que acontece depois do inicio das aulas?

- Slice: `public`
- Thread: `system_bank:timeline_e_calendario_publico:Q013` turn `1`
- `langgraph`: status 200, latency 6348.6ms, keyword pass `True`, quality `100`, reason `datas institucionais publicas devem vir de leitura estruturada e auditavel`
  answer: Para a confirmação da vaga, o processo de matrícula é finalizado antes do início das aulas. As aulas do Ensino Fundamental II e Médio começam em 2 de fevereiro de 2026, e a semana de acolhimento para o 6º ano e a 1ª série será de 2 a 6 de fevereiro.
- `crewai`: status 200, latency 197.5ms, keyword pass `True`, quality `100`, reason `crewai_public_fast_path`
  answer: As aulas do Ensino Fundamental II e do Ensino Medio comecam em 2 de fevereiro de 2026.
- `python_functions`: status 200, latency 111.1ms, keyword pass `True`, quality `100`, reason `python_functions_native_contextual_public_answer`
  answer: As aulas do Ensino Fundamental II e do Ensino Medio comecam em 2 de fevereiro de 2026. A semana de acolhimento do 6o ano e da primeira serie ocorre entre 2 e 6 de fevereiro.
- `llamaindex`: status 200, latency 23473.6ms, keyword pass `True`, quality `100`, reason `contextual_public_direct_answer`
  answer: As aulas do Ensino Fundamental II e do Ensino Medio comecam em 2 de fevereiro de 2026. A semana de acolhimento do 6o ano e da primeira serie ocorre entre 2 e 6 de fevereiro.
- `specialist_supervisor`: status 200, latency 150.1ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_tool_first:public_timeline`
  answer: As aulas do Ensino Fundamental II e do Ensino Medio comecam em 2 de fevereiro de 2026. A semana de acolhimento do 6o ano e da primeira serie ocorre entre 2 e 6 de fevereiro.

### Se eu quiser planejar uma viagem sem atrapalhar a vida escolar, quais marcos do calendario eu deveria observar?

- Slice: `public`
- Thread: `system_bank:timeline_e_calendario_publico:Q014` turn `1`
- `langgraph`: status 200, latency 5957.2ms, keyword pass `True`, quality `100`, reason `planejamento semantico publico encontrou um ato estruturado mais adequado ao turno`
  answer: O ciclo publico de matricula para 2026 foi aberto em 6 de outubro de 2025, com pre-cadastro, visita orientada opcional e triagem inicial de documentos. O atendimento comercial segue enquanto houver vagas por segmento.
- `crewai`: status 200, latency 20239.0ms, keyword pass `True`, quality `100`, reason `crewai_public_flow_completed`
  answer: Nao consegui concluir essa resposta agora pelo caminho principal configurado. Tente reformular em uma frase mais direta ou repetir em instantes.
- `python_functions`: status 200, latency 2885.0ms, keyword pass `True`, quality `100`, reason `python_functions_native_public_retrieval`
  answer: A base publica atual nao sustenta com seguranca todos os pontos dessa pergunta, especialmente sobre: atrapalhar, calendario, deveria, marcos, planejar, quiser, viagem. Para evitar uma orientacao incorreta, prefiro nao inferir alem do que esta documentado. Se quiser, eu posso responder apenas o que esta explicitamente registrado na base atual.

Fontes:
- Manual de Regulamentos Gerais (v2026.3)
- Agenda de Avaliacoes, Recuperacoes e Simulados 2026 (v2026.3)
- Rotina e Vida Escolar (v2026.2)
- `llamaindex`: status 200, latency 12088.6ms, keyword pass `True`, quality `100`, reason `retrieval hibrido e o caminho padrao para faq e documentos`
  answer: A base publica atual nao sustenta com seguranca todos os pontos dessa pergunta, especialmente sobre: atrapalhar, calendario, deveria, marcos, planejar, quiser, viagem. Para evitar uma orientacao incorreta, prefiro nao inferir alem do que esta documentado. Se quiser, eu posso responder apenas o que esta explicitamente registrado na base atual.

Fontes:
- Manual de Regulamentos Gerais (v2026.3)
- Agenda de Avaliacoes, Recuperacoes e Simulados 2026 (v2026.3)
- Rotina e Vida Escolar (v2026.2)
- `specialist_supervisor`: status 200, latency 159.9ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_tool_first:travel_planning`
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
- `langgraph`: status 200, latency 5687.3ms, keyword pass `True`, quality `100`, reason `planejamento semantico publico encontrou um ato estruturado mais adequado ao turno`
  answer: Entendo sua dúvida! Para que eu possa te ajudar com mais precisão sobre os eventos do calendário, por favor, tente reformular sua pergunta usando termos como "matrícula", "calendário", "secretaria" ou "atendimento". Assim, consigo buscar as informações mais relevantes para você.
- `crewai`: status 200, latency 20250.3ms, keyword pass `True`, quality `100`, reason `crewai_public_flow_completed`
  answer: Nao consegui concluir essa resposta agora pelo caminho principal configurado. Tente reformular em uma frase mais direta ou repetir em instantes.
- `python_functions`: status 200, latency 465.8ms, keyword pass `True`, quality `100`, reason `python_functions_native_public_retrieval`
  answer: Ainda nao encontrei evidencia publica suficiente para responder isso com seguranca do jeito que a pergunta foi feita. Se quiser, eu posso tentar por outro caminho, como o setor responsavel, o canal oficial ou a politica institucional relacionada.

Fontes:
- Saidas Pedagogicas, Eventos e Autorizacoes (v2026.3)
- FAQ Institucional do Colegio Horizonte (v2026.2)
- Programa de Periodo Integral e Estudo Orientado (v2026.3)
- `llamaindex`: status 200, latency 13750.5ms, keyword pass `True`, quality `100`, reason `retrieval hibrido e o caminho padrao para faq e documentos`
  answer: Ainda nao encontrei evidencia publica suficiente para responder isso com seguranca do jeito que a pergunta foi feita. Se quiser, eu posso tentar por outro caminho, como o setor responsavel, o canal oficial ou a politica institucional relacionada.

Fontes:
- Saidas Pedagogicas, Eventos e Autorizacoes (v2026.3)
- FAQ Institucional do Colegio Horizonte (v2026.2)
- Programa de Periodo Integral e Estudo Orientado (v2026.3)
- `specialist_supervisor`: status 200, latency 2835.8ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_fast_path:general_knowledge`
  answer: Eventos públicos são aqueles amplamente divulgados e acessíveis a qualquer pessoa, como feriados nacionais, eventos esportivos de grande porte, festivais culturais ou reuniões governamentais abertas ao público.

Eventos que dependem de autenticação ou contexto interno são aqueles restritos a um grupo específico de pessoas ou a um indivíduo, como reuniões de trabalho, compromissos pessoais, eventos corporativos internos ou aulas particulares. Para acessá-los, geralmente é necessário um login, uma permissão específica ou um convite.

### Resuma o ano escolar em tres fases: admissao, rotina academica e fechamento.

- Slice: `public`
- Thread: `system_bank:timeline_e_calendario_publico:Q016` turn `1`
- `langgraph`: status 200, latency 2892.7ms, keyword pass `True`, quality `100`, reason `a intencao esta ambigua e exige clarificacao antes de recuperar contexto`
  answer: Olá! Para resumir o ano escolar no Colégio Horizonte em três fases, podemos organizar da seguinte forma:

1.  **Admissão:** Esta fase envolve todo o processo de matrícula, desde o primeiro contato com a escola, agendamento de visitas, até a efetivação da matrícula. Nossos canais de atendimento para isso são o bot, o setor de admissões, o WhatsApp comercial ou a visita guiada.

2.  **Rotina Acadêmica:** Aqui se concentra o dia a dia de aulas e atividades. Inclui a tutoria acadêmica e o projeto de vida, o uso do nosso Espaço Maker integrado ao currículo, e o acompanhamento socioemocional. Para assuntos relacionados à secretaria escolar, documentos, reuniões com a coordenação pedagógica ou orientação educacional, você pode usar o bot, a secretaria presencial, o e-mail institucional ou o portal.

3.  **Fechamento:** Esta fase abrange o encerramento do ano letivo, incluindo avaliações finais e a preparação para o próximo ano. Questões financeiras e de contratos podem ser tratadas com o bot, o setor financeiro, o portal autenticado ou por e-mail institucional.

Espero que este resumo ajude a entender melhor o fluxo do ano escolar no Colégio Horizonte!
- `crewai`: status 200, latency 20307.6ms, keyword pass `True`, quality `100`, reason `crewai_public_flow_timeout`
  answer: Olá! As informações disponíveis detalham as fases de admissão e a rotina acadêmica do ano escolar. No entanto, não encontramos detalhes específicos sobre a fase de fechamento do ano escolar nos documentos.
- `python_functions`: status 200, latency 172.7ms, keyword pass `True`, quality `100`, reason `a intencao esta ambigua e exige clarificacao antes de recuperar contexto`
  answer: Posso ajudar com informacoes publicas da escola, como calendario, matricula, documentos exigidos e regras de atendimento digital. Se quiser, pergunte por exemplo: "quais documentos preciso para a matricula?" ou "quando acontece a reuniao de pais?".
- `llamaindex`: status 200, latency 6740.2ms, keyword pass `True`, quality `100`, reason `a intencao esta ambigua e exige clarificacao antes de recuperar contexto`
  answer: Posso ajudar com informacoes publicas da escola, como calendario, matricula, documentos exigidos e regras de atendimento digital. Se quiser, pergunte por exemplo: "quais documentos preciso para a matricula?" ou "quando acontece a reuniao de pais?".
- `specialist_supervisor`: status 200, latency 162.5ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_tool_first:year_three_phases`
  answer: Admissao: O ciclo publico de matricula para 2026 foi aberto em 6 de outubro de 2025, com pre-cadastro, visita orientada opcional e triagem inicial de documentos.
Rotina academica: As aulas do Ensino Fundamental II e do Ensino Medio comecam em 2 de fevereiro de 2026. Eventos publicos ao longo do ano incluem Inicio do ano letivo Fundamental II e Ensino Medio (02/02/2026) · publico: public. Recepcao das turmas com orientacoes iniciais, entrega de horarios e apresentacao da equipe; Reuniao geral de pais e responsaveis (28/03/2026) · publico: public. Apresentacao do planejamento do primeiro bimestre.
Fechamento: A cerimonia interna de conclusao do Ensino Fundamental II esta prevista para 12 de dezembro de 2026, no fim da tarde, apos o encerramento do ano letivo.

### Quais documentos sao exigidos para matricula no ensino medio?

- Slice: `public`
- Thread: `system_bank:retrieval_hibrido_sobre_documentos_publicos:Q017` turn `1`
- `langgraph`: status 200, latency 201.2ms, keyword pass `True`, quality `100`, reason `o turno atual trouxe pistas explicitas de outro dominio protegido e o roteamento foi corrigido`
  answer: Hoje os documentos exigidos para a matricula publicados pela escola sao:
- Formulario cadastral preenchido
- Documento de identificacao do aluno
- CPF do aluno, quando houver
- Historico escolar
- Comprovante de residencia atualizado
- Documento de identificacao do responsavel legal
Se quiser, eu tambem posso explicar as etapas da matricula ou como funciona o envio inicial desses documentos.
- `crewai`: status 200, latency 661.7ms, keyword pass `True`, quality `100`, reason `crewai_public_fast_path`
  answer: Hoje os documentos exigidos para a matricula publicados pela escola sao:
- Formulario cadastral preenchido
- Documento de identificacao do aluno
- CPF do aluno, quando houver
- Historico escolar
- Comprovante de residencia atualizado
- Documento de identificacao do responsavel legal
- `python_functions`: status 200, latency 183.6ms, keyword pass `True`, quality `100`, reason `python_functions_native_contextual_public_answer`
  answer: Hoje os documentos exigidos para a matricula publicados pela escola sao:
- Formulario cadastral preenchido
- Documento de identificacao do aluno
- CPF do aluno, quando houver
- Historico escolar
- Comprovante de residencia atualizado
- Documento de identificacao do responsavel legal
Se quiser, eu tambem posso explicar as etapas da matricula ou como funciona o envio inicial desses documentos.
- `llamaindex`: status 200, latency 2473.6ms, keyword pass `True`, quality `100`, reason `llamaindex_public_profile`
  answer: Hoje os documentos exigidos para a matricula publicados pela escola sao:
- Formulario cadastral preenchido
- Documento de identificacao do aluno
- CPF do aluno, quando houver
- Historico escolar
- Comprovante de residencia atualizado
- Documento de identificacao do responsavel legal
Se quiser, eu tambem posso explicar as etapas da matricula ou como funciona o envio inicial desses documentos.
- `specialist_supervisor`: status 200, latency 128.4ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_tool_first:admissions_documents`
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
- `langgraph`: status 200, latency 4052.7ms, keyword pass `True`, quality `100`, reason `fato institucional canonico deve vir de fonte estruturada`
  answer: No Colégio Horizonte, a média para aprovação é 7,0. Se a média ficar abaixo disso, oferecemos monitorias, plantões e orientações de recuperação, tudo conforme o nosso calendário pedagógico. A equipe pedagógica acompanha de perto todo o processo até o fechamento final do período letivo.
- `crewai`: status 200, latency 808.5ms, keyword pass `True`, quality `100`, reason `crewai_public_fast_path`
  answer: A referencia publica de aprovacao hoje e media 7.0 na escala 0-10. Quando a media fica abaixo da referencia, a escola combina monitorias, plantoes e orientacoes de recuperacao conforme o calendario pedagogico.
- `python_functions`: status 200, latency 139.4ms, keyword pass `True`, quality `100`, reason `python_functions_native_contextual_public_answer`
  answer: No Colegio Horizonte, a referencia publica de aprovacao e media 7,0/10. Quando a media fica abaixo da referencia, a escola combina monitorias, plantoes e orientacoes de recuperacao conforme o calendario pedagogico. A referencia publica de aprovacao usada nas orientacoes do colegio e 7,0, com fechamento final sempre acompanhado pela equipe pedagogica no periodo letivo.
- `llamaindex`: status 200, latency 4520.9ms, keyword pass `True`, quality `100`, reason `llamaindex_public_profile`
  answer: No Colegio Horizonte, a referencia publica de aprovacao e media 7,0/10. Quando a media fica abaixo da referencia, a escola combina monitorias, plantoes e orientacoes de recuperacao conforme o calendario pedagogico. A referencia publica de aprovacao usada nas orientacoes do colegio e 7,0, com fechamento final sempre acompanhado pela equipe pedagogica no periodo letivo.
- `specialist_supervisor`: status 200, latency 129.6ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_tool_first:academic_policy_overview`
  answer: O processo avaliativo combina instrumentos formativos e somativos, como atividades em aula, projetos, producoes textuais, simulados e provas bimestrais. Resultados parciais sao apresentados ao estudante e a familia por meio do portal academico, reunioes e devolutivas pedagogicas. Quando houver desempenho abaixo do esperado, a escola pode oferecer recuperacao paralela, atividades orientadas, monitoria, estudo dirigido ou avaliacao substitutiva, conforme o componente e o periodo do ano. Pedidos de segunda chamada exigem justificativa no prazo orientado pela escola. Na referencia publica atual, a escola trabalha com media 7,0/10 e frequencia minima de 75,0% por componente. A promocao considera desempenho global, trajetoria do estudante, recuperacao realizada e frequencia.

### Quais sao as regras gerais de convivencia, frequencia e pontualidade?

- Slice: `public`
- Thread: `system_bank:retrieval_hibrido_sobre_documentos_publicos:Q019` turn `1`
- `langgraph`: status 200, latency 3961.2ms, keyword pass `True`, quality `100`, reason `fato institucional canonico deve vir de fonte estruturada`
  answer: No Colegio Horizonte, a referencia publica minima de frequencia e 75,0% por componente. Se a frequencia de um componente cair abaixo de 75%, o estudante entra em alerta academico e a coordenacao pode acionar a familia. A permanencia abaixo desse limite pode comprometer a aprovacao por frequencia. A escola acompanha justificativas, recorrencia e necessidade de plano de recomposicao junto a familia e ao estudante.
- `crewai`: status 200, latency 185.0ms, keyword pass `True`, quality `100`, reason `crewai_protected_auth_required`
  answer: Essa consulta depende de autenticacao e vinculo da sua conta no Telegram. Use o portal da escola para gerar o codigo de vinculacao e depois envie o comando /start link_<codigo> ao bot.
- `python_functions`: status 200, latency 133.0ms, keyword pass `True`, quality `100`, reason `python_functions_native_contextual_public_answer`
  answer: No Colegio Horizonte, a referencia publica minima de frequencia e 75,0% por componente. Se a frequencia de um componente cair abaixo de 75%, o estudante entra em alerta academico e a coordenacao pode acionar a familia. A permanencia abaixo desse limite pode comprometer a aprovacao por frequencia. A escola acompanha justificativas, recorrencia e necessidade de plano de recomposicao junto a familia e ao estudante.
- `llamaindex`: status 200, latency 9853.0ms, keyword pass `True`, quality `100`, reason `contextual_public_direct_answer`
  answer: No Colegio Horizonte, a referencia publica minima de frequencia e 75,0% por componente. Se a frequencia de um componente cair abaixo de 75%, o estudante entra em alerta academico e a coordenacao pode acionar a familia. A permanencia abaixo desse limite pode comprometer a aprovacao por frequencia. A escola acompanha justificativas, recorrencia e necessidade de plano de recomposicao junto a familia e ao estudante.
- `specialist_supervisor`: status 200, latency 131.2ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_tool_first:conduct_frequency_punctuality`
  answer: O estudante deve comparecer pontualmente as atividades letivas e cumprir a frequencia minima definida pela escola e pela legislacao aplicavel. A convivencia escolar deve observar respeito mutuo, cuidado com o patrimonio e linguagem adequada. Faltas em dias de avaliacao seguem a politica especifica de segunda chamada e recuperacao. A politica publica de frequencia reforca presenca minima de 75,0% por componente e alerta academico quando a recorrencia de faltas compromete a aprovacao. Se a frequencia de um componente cair abaixo de 75%, o estudante entra em alerta academico e a coordenacao pode acionar a familia.

### Como funciona o uso da biblioteca, dos laboratorios e dos recursos digitais?

- Slice: `public`
- Thread: `system_bank:retrieval_hibrido_sobre_documentos_publicos:Q020` turn `1`
- `langgraph`: status 200, latency 5793.1ms, keyword pass `True`, quality `100`, reason `fato institucional canonico deve vir de fonte estruturada`
  answer: Sim. O Colegio Horizonte tem a Biblioteca Aurora. Atendimento ao publico de segunda a sexta, das 7h30 as 18h00.
- `crewai`: status 200, latency 203.2ms, keyword pass `True`, quality `100`, reason `crewai_public_fast_path`
  answer: Sim. Biblioteca Aurora: biblioteca   Biblioteca Aurora   service   True   Atendimento ao publico de segunda a sexta, das 7h30 as 18h00..
- `python_functions`: status 200, latency 132.7ms, keyword pass `True`, quality `100`, reason `python_functions_native_contextual_public_answer`
  answer: A biblioteca se chama Biblioteca Aurora e funciona de segunda a sexta, das 7h30 as 18h00.
- `llamaindex`: status 200, latency 6557.3ms, keyword pass `True`, quality `100`, reason `llamaindex_public_profile`
  answer: Sim. O Colegio Horizonte tem a Biblioteca Aurora. Atendimento ao publico de segunda a sexta, das 7h30 as 18h00.
- `specialist_supervisor`: status 200, latency 126.4ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_fast_path:library_hours`
  answer: A biblioteca se chama Biblioteca Aurora e funciona Atendimento ao publico de segunda a sexta, das 7h30 as 18h00.

### Quais os prazos e canais para secretaria receber documentos, declaracoes e atualizacoes cadastrais?

- Slice: `public`
- Thread: `system_bank:retrieval_hibrido_sobre_documentos_publicos:Q021` turn `1`
- `langgraph`: status 200, latency 4219.1ms, keyword pass `True`, quality `100`, reason `fato institucional canonico deve vir de fonte estruturada`
  answer: Olá! Para o envio de documentos, declarações e atualizações cadastrais, você pode utilizar nosso portal institucional, o email da secretaria ou, se preferir, entregar presencialmente. A secretaria tem um prazo de até 2 dias úteis para dar o retorno. Lembre-se que, para a matrícula, o envio inicial pode ser digital, mas a validação final é feita presencialmente na secretaria. Por segurança, evite enviar documentos completos ou dados sensíveis pelo chat, ok?
- `crewai`: status 200, latency 180.7ms, keyword pass `True`, quality `100`, reason `crewai_public_fast_path`
  answer: Hoje a secretaria recebe documentos, declaracoes e atualizacoes cadastrais pelo portal institucional, pelo email da secretaria e pela secretaria presencial. Prazo esperado da secretaria: retorno em ate 2 dias uteis.
- `python_functions`: status 200, latency 142.1ms, keyword pass `True`, quality `100`, reason `python_functions_native_contextual_public_answer`
  answer: Sim. O envio inicial de documentos pode ser feito por canal digital.
Hoje os canais mais diretos publicados para isso sao:
- portal institucional
- email da secretaria
- secretaria presencial
Prazo esperado da secretaria: retorno em ate 2 dias uteis.
No processo de matricula, o envio inicial pode ser digital. A validacao final continua com a secretaria.
O chat aberto nao deve receber documentos completos ou dados sensiveis. Quando possivel, use o portal autenticado ou o email institucional.
- `llamaindex`: status 200, latency 11917.6ms, keyword pass `True`, quality `100`, reason `llamaindex_public_profile`
  answer: Sim. O envio inicial de documentos pode ser feito por canal digital.
Hoje os canais mais diretos publicados para isso sao:
- portal institucional
- email da secretaria
- secretaria presencial
Prazo esperado da secretaria: retorno em ate 2 dias uteis.
No processo de matricula, o envio inicial pode ser digital. A validacao final continua com a secretaria.
O chat aberto nao deve receber documentos completos ou dados sensiveis. Quando possivel, use o portal autenticado ou o email institucional.
- `specialist_supervisor`: status 200, latency 129.4ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_tool_first:document_submission_policy`
  answer: Voce pode mandar documentos pelo portal institucional, pelo email da secretaria ou levar na secretaria presencial para conferencia final. Prazo esperado da secretaria: retorno em ate 2 dias uteis. No processo de matricula, o envio inicial pode ser digital. A validacao final continua com a secretaria. O chat aberto nao deve receber documentos completos ou dados sensiveis. Quando possivel, use o portal autenticado ou o email institucional.

### O que a escola orienta sobre portal, aplicativo, senha, login e seguranca das credenciais?

- Slice: `public`
- Thread: `system_bank:retrieval_hibrido_sobre_documentos_publicos:Q022` turn `1`
- `langgraph`: status 200, latency 1984.4ms, keyword pass `True`, quality `100`, reason `retrieval hibrido e o caminho padrao para faq e documentos`
  answer: Aqui e o Colegio Horizonte. Se voce esta procurando o Orienta Sobre Portal, eu nao tenho acesso ao atendimento dessa outra instituicao. Se quiser, sigo te ajudando com o Colegio Horizonte por aqui.
- `crewai`: status 200, latency 172.7ms, keyword pass `True`, quality `100`, reason `crewai_public_fast_path`
  answer: Hoje a familia precisa entender quatro frentes publicas deste fluxo: Secretaria recebe declaracoes, historico, atualizacoes cadastrais e orientacoes administrativas. Portal institucional centraliza protocolo e envio digital inicial de documentos. Credenciais significam login e senha do portal; se voce perder o acesso, o melhor caminho e a secretaria ou o suporte digital. Documentos podem ser enviados pelo portal institucional, pelo email da secretaria ou pela secretaria presencial.
- `python_functions`: status 200, latency 129.8ms, keyword pass `True`, quality `100`, reason `python_functions_native_contextual_public_answer`
  answer: Hoje a familia precisa entender quatro frentes publicas deste fluxo:
- Secretaria: recebe declaracoes, historico, atualizacoes cadastrais e orientacoes administrativas.
- Portal institucional: centraliza protocolo e envio digital inicial de documentos.
- Credenciais: login e senha do portal continuam sendo a base de acesso; se precisar recuperar acesso, o melhor caminho e a secretaria ou o suporte digital.
- Documentos: o envio inicial pode ser feito por portal institucional, email da secretaria ou secretaria presencial.
O chat aberto nao deve receber documentos completos ou dados sensiveis. Quando possivel, use o portal autenticado ou o email institucional.
- `llamaindex`: status 200, latency 8597.5ms, keyword pass `True`, quality `100`, reason `contextual_public_direct_answer`
  answer: Hoje a familia precisa entender quatro frentes publicas deste fluxo:
- Secretaria: recebe declaracoes, historico, atualizacoes cadastrais e orientacoes administrativas.
- Portal institucional: centraliza protocolo e envio digital inicial de documentos.
- Credenciais: login e senha do portal continuam sendo a base de acesso; se precisar recuperar acesso, o melhor caminho e a secretaria ou o suporte digital.
- Documentos: o envio inicial pode ser feito por portal institucional, email da secretaria ou secretaria presencial.
O chat aberto nao deve receber documentos completos ou dados sensiveis. Quando possivel, use o portal autenticado ou o email institucional.
- `specialist_supervisor`: status 200, latency 160.2ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_fast_path:service_credentials_bundle`
  answer: Hoje a familia precisa entender quatro frentes publicas deste fluxo:
- Secretaria: recebe declaracoes, historico, atualizacoes cadastrais e orientacoes administrativas.
- Portal institucional: centraliza protocolo e envio digital inicial de documentos.
- Credenciais: login e senha do portal continuam sendo a base de acesso; se voce perder o acesso, o melhor caminho e a secretaria ou o suporte digital.
- Documentos: o envio inicial pode ser feito por portal institucional, email da secretaria ou secretaria presencial.
O chat aberto nao deve receber documentos completos ou dados sensiveis. Quando possivel, use o portal autenticado ou o email institucional.

### Como funcionam bolsas, descontos e regras de rematricula, transferencia e cancelamento?

- Slice: `public`
- Thread: `system_bank:retrieval_hibrido_sobre_documentos_publicos:Q023` turn `1`
- `langgraph`: status 200, latency 6055.4ms, keyword pass `True`, quality `100`, reason `fato institucional canonico deve vir de fonte estruturada`
  answer: Olá! Para entender melhor sobre bolsas, descontos, e as regras de rematrícula, transferência e cancelamento, o ideal é conversar diretamente com nossa equipe comercial. Eles podem te explicar tudo sobre as políticas para irmãos e pagamento pontual, além de fazer uma simulação financeira inicial. Você pode entrar em contato pelo nosso WhatsApp comercial, agendar uma visita guiada ou usar nosso bot de admissões, e eles te retornarão em até 1 dia útil.
- `crewai`: status 200, latency 236.3ms, keyword pass `True`, quality `100`, reason `crewai_public_fast_path`
  answer: A mensalidade de referencia para Ensino Fundamental II e R$ 1280.00, com taxa de matricula de R$ 350.00.
- `python_functions`: status 200, latency 173.3ms, keyword pass `True`, quality `100`, reason `python_functions_native_structured:institution`
  answer: Hoje, pelo que Colegio Horizonte publica, bolsas e descontos entram no atendimento comercial de matricula. A referencia comercial atual tambem menciona valor comercial publico de referencia para 2026. ha politica comercial para irmaos e pagamento pontual. O caminho mais direto hoje e Matricula, bolsas e atendimento comercial por bot, admissions, whatsapp comercial ou visita guiada, com retorno em ate 1 dia util. Atende duvidas sobre processo de ingresso, documentos, bolsas, descontos e simulacao financeira inicial.
- `llamaindex`: status 200, latency 20151.3ms, keyword pass `True`, quality `100`, reason `llamaindex_public_profile`
  answer: Hoje, pelo que Colegio Horizonte publica, bolsas e descontos entram no atendimento comercial de matricula. A referencia comercial atual tambem menciona valor comercial publico de referencia para 2026. ha politica comercial para irmaos e pagamento pontual. O caminho mais direto hoje e Matricula, bolsas e atendimento comercial por bot, admissions, whatsapp comercial ou visita guiada, com retorno em ate 1 dia util. Atende duvidas sobre processo de ingresso, documentos, bolsas, descontos e simulacao financeira inicial.
- `specialist_supervisor`: status 200, latency 124.2ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_tool_first:bolsas_and_processes`
  answer: O edital disciplina pedidos de bolsa social, desconto institucional, politica para irmaos e condicoes de manutencao do beneficio no ano letivo de 2026. Pedidos devem ser feitos dentro da janela informada pela escola, com envio de documentacao socioeconomica e demais comprovantes solicitados no regulamento especifico. A concessao de bolsas e descontos depende de analise documental, criterios internos, disponibilidade orcamentaria e validacao administrativa. Beneficios podem depender de cumprimento das condicoes previstas, como adimplencia, atualizacao cadastral e apresentacao tempestiva de documentos complementares quando solicitados. A rematricula para estudantes ja vinculados ao Colegio Horizonte ocorre em janela administrativa propria, divulgada no portal e reforcada pelos canais oficiais. Pedidos de transferencia para ingresso durante o ano letivo dependem de vaga, analise academica, conferencia documental e alinhamento com a serie pretendida. Quando a familia deseja transferir o aluno para outra instituicao, a solicitacao deve ser formalizada junto a secretaria. Pedidos de cancelamento devem ser apresentados pelo responsavel legal por canal oficial e podem exigir confirmacao adicional da secretaria ou do financeiro. Declaracoes simples costumam ser liberadas em ate dois dias uteis.

### Se eu faltar por motivo de saude e perder uma prova, onde a escola explica o que devo fazer?

- Slice: `public`
- Thread: `system_bank:retrieval_hibrido_sobre_documentos_publicos:Q024` turn `1`
- `langgraph`: status 200, latency 2105.3ms, keyword pass `True`, quality `100`, reason `planejamento semantico publico encontrou um ato estruturado mais adequado ao turno`
  answer: Aqui e o Colegio Horizonte. Se voce esta procurando o Explica Que Devo, eu nao tenho acesso ao atendimento dessa outra instituicao. Se quiser, sigo te ajudando com o Colegio Horizonte por aqui.
- `crewai`: status 200, latency 268.8ms, keyword pass `True`, quality `100`, reason `crewai_protected_auth_required`
  answer: Essa consulta depende de autenticacao e vinculo da sua conta no Telegram. Use o portal da escola para gerar o codigo de vinculacao e depois envie o comando /start link_<codigo> ao bot.
- `python_functions`: status 200, latency 623.1ms, keyword pass `True`, quality `100`, reason `python_functions_native_public_retrieval`
  answer: A base publica atual nao sustenta com seguranca todos os pontos dessa pergunta, especialmente sobre: devo, explica, faltar, fazer, motivo, perder, prova. Para evitar uma orientacao incorreta, prefiro nao inferir alem do que esta documentado. Se quiser, eu posso responder apenas o que esta explicitamente registrado na base atual.

Fontes:
- Manual de Regulamentos Gerais (v2026.3)
- Protocolo de Saude, Medicacao e Emergencias (v2026.3)
- Politica de Avaliacao, Recuperacao e Promocao (v2026.3)
- `llamaindex`: status 200, latency 13362.2ms, keyword pass `True`, quality `100`, reason `retrieval hibrido e o caminho padrao para faq e documentos`
  answer: A base publica atual nao sustenta com seguranca todos os pontos dessa pergunta, especialmente sobre: devo, explica, faltar, fazer, motivo, perder, prova. Para evitar uma orientacao incorreta, prefiro nao inferir alem do que esta documentado. Se quiser, eu posso responder apenas o que esta explicitamente registrado na base atual.

Fontes:
- Manual de Regulamentos Gerais (v2026.3)
- Protocolo de Saude, Medicacao e Emergencias (v2026.3)
- Politica de Avaliacao, Recuperacao e Promocao (v2026.3)
- `specialist_supervisor`: status 200, latency 171.5ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_tool_first:health_second_call`
  answer: Atestados medicos e justificativas formais podem ser usados para apoiar analise de ausencia, segunda chamada ou adaptacao temporaria de rotina. Pedidos de segunda chamada exigem justificativa no prazo orientado pela escola.

