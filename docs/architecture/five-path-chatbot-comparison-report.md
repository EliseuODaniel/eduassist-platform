# Five-Path Chatbot Comparison Report

Date: 2026-03-30T23:46:34.229029+00:00

Dataset: `/home/edann/projects/eduassist-platform/tests/evals/datasets/five_path_random_probe_cases.json`

Run prefix: `debug:five-path:20260330T234519Z`

## Stack Summary

| Stack | OK | Keyword pass | Quality | Avg latency |
| --- | --- | --- | --- | --- |
| `langgraph` | `17/17` | `17/17` | `100.0` | `173.8 ms` |
| `crewai` | `17/17` | `8/17` | `89.4` | `3797.0 ms` |
| `python_functions` | `17/17` | `17/17` | `100.0` | `158.8 ms` |
| `llamaindex` | `17/17` | `17/17` | `100.0` | `173.8 ms` |
| `specialist_supervisor` | `17/17` | `17/17` | `100.0` | `105.9 ms` |

## By Slice

- `protected`
  - `langgraph`: ok 5/5, keyword pass 5/5, quality 100.0, latency 194.0ms
  - `crewai`: ok 5/5, keyword pass 2/5, quality 88.0, latency 4956.9ms
  - `python_functions`: ok 5/5, keyword pass 5/5, quality 100.0, latency 185.9ms
  - `llamaindex`: ok 5/5, keyword pass 5/5, quality 100.0, latency 197.7ms
  - `specialist_supervisor`: ok 5/5, keyword pass 5/5, quality 100.0, latency 138.7ms
- `public`
  - `langgraph`: ok 8/8, keyword pass 8/8, quality 100.0, latency 169.8ms
  - `crewai`: ok 8/8, keyword pass 3/8, quality 87.5, latency 3381.1ms
  - `python_functions`: ok 8/8, keyword pass 8/8, quality 100.0, latency 141.4ms
  - `llamaindex`: ok 8/8, keyword pass 8/8, quality 100.0, latency 155.7ms
  - `specialist_supervisor`: ok 8/8, keyword pass 8/8, quality 100.0, latency 86.5ms
- `support`
  - `langgraph`: ok 2/2, keyword pass 2/2, quality 100.0, latency 155.4ms
  - `crewai`: ok 2/2, keyword pass 1/2, quality 90.0, latency 6134.4ms
  - `python_functions`: ok 2/2, keyword pass 2/2, quality 100.0, latency 162.8ms
  - `llamaindex`: ok 2/2, keyword pass 2/2, quality 100.0, latency 156.1ms
  - `specialist_supervisor`: ok 2/2, keyword pass 2/2, quality 100.0, latency 95.2ms
- `workflow`
  - `langgraph`: ok 2/2, keyword pass 2/2, quality 100.0, latency 158.0ms
  - `crewai`: ok 2/2, keyword pass 2/2, quality 100.0, latency 223.2ms
  - `python_functions`: ok 2/2, keyword pass 2/2, quality 100.0, latency 156.9ms
  - `llamaindex`: ok 2/2, keyword pass 2/2, quality 100.0, latency 204.5ms
  - `specialist_supervisor`: ok 2/2, keyword pass 2/2, quality 100.0, latency 112.0ms

## Error Types

- `langgraph`: nenhum
- `crewai`: missing_expected_keyword=9
- `python_functions`: nenhum
- `llamaindex`: nenhum
- `specialist_supervisor`: nenhum

## Prompt Results

### a escola fica em qual bairro de sao paulo?

- Slice: `public`
- Thread: `random_public_location` turn `1`
- `langgraph`: status 200, latency 201.4ms, keyword pass `True`, quality `100`, reason `fato institucional canonico deve vir de fonte estruturada`
  answer: Colegio Horizonte fica em Rua das Acacias, 1450, Vila Mariana, Sao Paulo, SP, CEP 04567-120.
- `crewai`: status 200, latency 12001.8ms, keyword pass `False`, quality `80`, reason `crewai_public_flow_completed`
  errors: missing_expected_keyword
  answer: Nao consegui concluir essa resposta agora pelo caminho principal configurado. Tente reformular em uma frase mais direta ou repetir em instantes.
- `python_functions`: status 200, latency 154.1ms, keyword pass `True`, quality `100`, reason `python_functions_native_structured:institution`
  answer: Colegio Horizonte fica em Rua das Acacias, 1450, Vila Mariana, Sao Paulo, SP, CEP 04567-120.
- `llamaindex`: status 200, latency 201.4ms, keyword pass `True`, quality `100`, reason `llamaindex_public_profile`
  answer: Colegio Horizonte fica em Rua das Acacias, 1450, Vila Mariana, Sao Paulo, SP, CEP 04567-120.
- `specialist_supervisor`: status 200, latency 111.6ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_fast_path:district`
  answer: A escola fica no bairro Vila Mariana, Sao Paulo/SP.

### o ensino medio segue a bncc?

- Slice: `public`
- Thread: `random_public_curriculum` turn `1`
- `langgraph`: status 200, latency 194.2ms, keyword pass `True`, quality `100`, reason `fato institucional canonico deve vir de fonte estruturada`
  answer: No Ensino Medio, Colegio Horizonte segue a BNCC e um curriculo proprio de aprofundamento academico. Os componentes que aparecem hoje na base publica incluem Lingua Portuguesa e producao textual, Matematica, Biologia, Fisica, Quimica, Historia, Geografia, Lingua Inglesa, alem de projeto de vida, monitorias e trilhas eletivas.
- `crewai`: status 200, latency 846.1ms, keyword pass `True`, quality `100`, reason `crewai_public_fast_path`
  answer: No Ensino Medio, a escola segue a BNCC e o curriculo do Ensino Medio articulado com projeto de vida, producao textual, cultura digital e aprofundamento academico progressivo.
- `python_functions`: status 200, latency 142.6ms, keyword pass `True`, quality `100`, reason `python_functions_native_structured:institution`
  answer: No Ensino Medio, Colegio Horizonte segue a BNCC e um curriculo proprio de aprofundamento academico. Os componentes que aparecem hoje na base publica incluem Lingua Portuguesa e producao textual, Matematica, Biologia, Fisica, Quimica, Historia, Geografia, Lingua Inglesa, alem de projeto de vida, monitorias e trilhas eletivas.
- `llamaindex`: status 200, latency 153.7ms, keyword pass `True`, quality `100`, reason `llamaindex_public_profile`
  answer: No Ensino Medio, Colegio Horizonte segue a BNCC e um curriculo proprio de aprofundamento academico. Os componentes que aparecem hoje na base publica incluem Lingua Portuguesa e producao textual, Matematica, Biologia, Fisica, Quimica, Historia, Geografia, Lingua Inglesa, alem de projeto de vida, monitorias e trilhas eletivas.
- `specialist_supervisor`: status 200, latency 86.0ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_fast_path:bncc`
  answer: Sim. A escola trabalha com base curricular alinhada a A escola segue a BNCC e o curriculo do Ensino Medio articulado com projeto de vida, producao textual, cultura digital e aprofundamento academico progressivo..

### quais canais eu posso usar para mandar documentos?

- Slice: `public`
- Thread: `random_public_documents` turn `1`
- `langgraph`: status 200, latency 145.4ms, keyword pass `True`, quality `100`, reason `fato institucional canonico deve vir de fonte estruturada`
  answer: Sim. O envio inicial de documentos pode ser feito por canal digital.
Hoje os canais mais diretos publicados para isso sao:
- portal institucional
- email da secretaria
- secretaria presencial
No processo de matricula, o envio inicial pode ser digital. A validacao final continua com a secretaria.
O chat aberto nao deve receber documentos completos ou dados sensiveis. Quando possivel, use o portal autenticado ou o email institucional.
- `crewai`: status 200, latency 193.1ms, keyword pass `False`, quality `80`, reason `crewai_protected_auth_required`
  errors: missing_expected_keyword
  answer: Essa consulta depende de autenticacao e vinculo da sua conta no Telegram. Use o portal da escola para gerar o codigo de vinculacao e depois envie o comando /start link_<codigo> ao bot.
- `python_functions`: status 200, latency 112.6ms, keyword pass `True`, quality `100`, reason `python_functions_native_contextual_public_answer`
  answer: Sim. O envio inicial de documentos pode ser feito por canal digital.
Hoje os canais mais diretos publicados para isso sao:
- portal institucional
- email da secretaria
- secretaria presencial
No processo de matricula, o envio inicial pode ser digital. A validacao final continua com a secretaria.
O chat aberto nao deve receber documentos completos ou dados sensiveis. Quando possivel, use o portal autenticado ou o email institucional.
- `llamaindex`: status 200, latency 147.0ms, keyword pass `True`, quality `100`, reason `llamaindex_public_profile`
  answer: Sim. O envio inicial de documentos pode ser feito por canal digital.
Hoje os canais mais diretos publicados para isso sao:
- portal institucional
- email da secretaria
- secretaria presencial
No processo de matricula, o envio inicial pode ser digital. A validacao final continua com a secretaria.
O chat aberto nao deve receber documentos completos ou dados sensiveis. Quando possivel, use o portal autenticado ou o email institucional.
- `specialist_supervisor`: status 200, latency 77.1ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_tool_first:document_submission_policy`
  answer: Voce pode mandar documentos pelo portal institucional, pelo email da secretaria ou levar na secretaria presencial para conferencia final. No processo de matricula, o envio inicial pode ser digital. A validacao final continua com a secretaria. O chat aberto nao deve receber documentos completos ou dados sensiveis. Quando possivel, use o portal autenticado ou o email institucional.

### a biblioteca tem nome e horario ou e so marketing?

- Slice: `public`
- Thread: `random_public_library` turn `1`
- `langgraph`: status 200, latency 144.7ms, keyword pass `True`, quality `100`, reason `fato institucional canonico deve vir de fonte estruturada`
  answer: O horario de Biblioteca Aurora hoje funciona assim: Atendimento ao publico de segunda a sexta, das 7h30 as 18h00.

Turnos e horarios documentados:
- Ensino Fundamental II (Manha): 07:15 as 12:30. Oficinas, plantoes, esportes e estudo orientado no contraturno em dias alternados.
- Ensino Medio (Manha): 07:15 as 12:50. Trilhas eletivas, monitorias e laboratorios no contraturno a partir das 14h00.
- Fundamental II e Ensino Medio (Integral opcional): 07:00 as 17:30. Inclui estudo orientado, almoco, oficinas, esportes e acompanhamento no contraturno.
- `crewai`: status 200, latency 11954.0ms, keyword pass `False`, quality `80`, reason `crewai_public_flow_completed`
  errors: missing_expected_keyword
  answer: Nao consegui concluir essa resposta agora pelo caminho principal configurado. Tente reformular em uma frase mais direta ou repetir em instantes.
- `python_functions`: status 200, latency 159.7ms, keyword pass `True`, quality `100`, reason `python_functions_native_contextual_public_answer`
  answer: A biblioteca se chama Biblioteca Aurora e funciona de segunda a sexta, das 7h30 as 18h00.
- `llamaindex`: status 200, latency 142.1ms, keyword pass `True`, quality `100`, reason `llamaindex_public_profile`
  answer: O horario de Biblioteca Aurora hoje funciona assim: Atendimento ao publico de segunda a sexta, das 7h30 as 18h00.

Turnos e horarios documentados:
- Ensino Fundamental II (Manha): 07:15 as 12:30. Oficinas, plantoes, esportes e estudo orientado no contraturno em dias alternados.
- Ensino Medio (Manha): 07:15 as 12:50. Trilhas eletivas, monitorias e laboratorios no contraturno a partir das 14h00.
- Fundamental II e Ensino Medio (Integral opcional): 07:00 as 17:30. Inclui estudo orientado, almoco, oficinas, esportes e acompanhamento no contraturno.
- `specialist_supervisor`: status 200, latency 72.7ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_fast_path:library_hours`
  answer: A biblioteca se chama Biblioteca Aurora e funciona Atendimento ao publico de segunda a sexta, das 7h30 as 18h00.

### quando abre a matricula de 2026?

- Slice: `public`
- Thread: `random_public_timeline` turn `1`
- `langgraph`: status 200, latency 163.5ms, keyword pass `True`, quality `100`, reason `datas institucionais publicas devem vir de leitura estruturada e auditavel`
  answer: O ciclo publico de matricula para 2026 foi aberto em 6 de outubro de 2025, com pre-cadastro, visita orientada opcional e triagem inicial de documentos. O atendimento comercial segue enquanto houver vagas por segmento.
- `crewai`: status 200, latency 175.3ms, keyword pass `False`, quality `80`, reason `crewai_protected_auth_required`
  errors: missing_expected_keyword
  answer: Essa consulta depende de autenticacao e vinculo da sua conta no Telegram. Use o portal da escola para gerar o codigo de vinculacao e depois envie o comando /start link_<codigo> ao bot.
- `python_functions`: status 200, latency 138.9ms, keyword pass `True`, quality `100`, reason `python_functions_native_structured:calendar`
  answer: O ciclo publico de matricula para 2026 foi aberto em 6 de outubro de 2025, com pre-cadastro, visita orientada opcional e triagem inicial de documentos. O atendimento comercial segue enquanto houver vagas por segmento.
- `llamaindex`: status 200, latency 155.2ms, keyword pass `True`, quality `100`, reason `llamaindex_public_profile`
  answer: O ciclo publico de matricula para 2026 foi aberto em 6 de outubro de 2025, com pre-cadastro, visita orientada opcional e triagem inicial de documentos. O atendimento comercial segue enquanto houver vagas por segmento.
- `specialist_supervisor`: status 200, latency 89.5ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_tool_first:public_timeline`
  answer: O ciclo publico de matricula para 2026 foi aberto em 6 de outubro de 2025, com pre-cadastro, visita orientada opcional e triagem inicial de documentos. O atendimento comercial segue enquanto houver vagas por segmento.

### e quando comecam as aulas?

- Slice: `public`
- Thread: `random_public_timeline` turn `2`
- `langgraph`: status 200, latency 177.8ms, keyword pass `True`, quality `100`, reason `datas institucionais publicas devem vir de leitura estruturada e auditavel`
  answer: As aulas do Ensino Fundamental II e do Ensino Medio comecam em 2 de fevereiro de 2026. A semana de acolhimento do 6o ano e da primeira serie ocorre entre 2 e 6 de fevereiro.
- `crewai`: status 200, latency 774.1ms, keyword pass `True`, quality `100`, reason `crewai_public_fast_path`
  answer: As aulas do Ensino Fundamental II e do Ensino Medio comecam em 2 de fevereiro de 2026.
- `python_functions`: status 200, latency 149.0ms, keyword pass `True`, quality `100`, reason `python_functions_native_contextual_public_answer`
  answer: As aulas do Ensino Fundamental II e do Ensino Medio comecam em 2 de fevereiro de 2026. A semana de acolhimento do 6o ano e da primeira serie ocorre entre 2 e 6 de fevereiro.
- `llamaindex`: status 200, latency 155.5ms, keyword pass `True`, quality `100`, reason `llamaindex_public_profile`
  answer: As aulas do Ensino Fundamental II e do Ensino Medio comecam em 2 de fevereiro de 2026. A semana de acolhimento do 6o ano e da primeira serie ocorre entre 2 e 6 de fevereiro.
- `specialist_supervisor`: status 200, latency 85.8ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_tool_first:public_timeline`
  answer: As aulas do Ensino Fundamental II e do Ensino Medio comecam em 2 de fevereiro de 2026. A semana de acolhimento do 6o ano e da primeira serie ocorre entre 2 e 6 de fevereiro.

### qual a mensalidade do ensino medio?

- Slice: `public`
- Thread: `random_public_pricing` turn `1`
- `langgraph`: status 200, latency 167.4ms, keyword pass `True`, quality `100`, reason `fato institucional canonico deve vir de fonte estruturada`
  answer: Para Ensino Medio no turno Manha, a mensalidade publica de referencia em 2026 e R$ 1.450,00 e a taxa de matricula e R$ 350,00. Valor comercial publico de referencia para 2026. Ha politica comercial para irmaos e pagamento pontual. Se quiser, eu tambem posso resumir bolsas, descontos comerciais e canais de matricula.
- `crewai`: status 200, latency 919.8ms, keyword pass `True`, quality `100`, reason `crewai_public_fast_path`
  answer: A mensalidade de referencia para Ensino Medio e R$ 1450.00, com taxa de matricula de R$ 350.00.
- `python_functions`: status 200, latency 142.9ms, keyword pass `True`, quality `100`, reason `python_functions_native_structured:institution`
  answer: Para Ensino Medio no turno Manha, a mensalidade publica de referencia em 2026 e R$ 1.450,00 e a taxa de matricula e R$ 350,00. Valor comercial publico de referencia para 2026. Ha politica comercial para irmaos e pagamento pontual. Se quiser, eu tambem posso resumir bolsas, descontos comerciais e canais de matricula.
- `llamaindex`: status 200, latency 151.9ms, keyword pass `True`, quality `100`, reason `llamaindex_public_profile`
  answer: Para Ensino Medio no turno Manha, a mensalidade publica de referencia em 2026 e R$ 1.450,00 e a taxa de matricula e R$ 350,00. Valor comercial publico de referencia para 2026. Ha politica comercial para irmaos e pagamento pontual. Se quiser, eu tambem posso resumir bolsas, descontos comerciais e canais de matricula.
- `specialist_supervisor`: status 200, latency 83.8ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_tool_first:public_pricing_reference`
  answer: Para Ensino Medio no turno Manha, a mensalidade publica de referencia em 2026 e R$ 1.450,00 e a taxa de matricula e R$ 350,00. Valor comercial publico de referencia para 2026. Ha politica comercial para irmaos e pagamento pontual.

### se eu matricular 3 filhos, quanto fica so a matricula?

- Slice: `public`
- Thread: `random_public_pricing` turn `2`
- `langgraph`: status 200, latency 164.0ms, keyword pass `True`, quality `100`, reason `fato institucional canonico deve vir de fonte estruturada`
  answer: Se eu usar a taxa publica de matricula hoje publicada nos segmentos publicados que usam essa mesma referencia, a simulacao fica 3 x R$ 350,00 = R$ 1.050,00.
Essa conta usa apenas os valores publicos de referencia e nao inclui material, uniforme ou condicao comercial nao detalhada na base.
A base publica tambem menciona: Valor comercial publico de referencia para 2026. Ha politica comercial para irmaos e pagamento pontual.
- `crewai`: status 200, latency 184.5ms, keyword pass `False`, quality `80`, reason `crewai_protected_auth_required`
  errors: missing_expected_keyword
  answer: Essa consulta depende de autenticacao e vinculo da sua conta no Telegram. Use o portal da escola para gerar o codigo de vinculacao e depois envie o comando /start link_<codigo> ao bot.
- `python_functions`: status 200, latency 131.1ms, keyword pass `True`, quality `100`, reason `python_functions_native_pricing_projection`
  answer: Se eu usar a taxa publica de matricula hoje publicada nos segmentos publicados que usam essa mesma referencia, a simulacao fica 3 x R$ 350,00 = R$ 1.050,00.
Essa conta usa apenas os valores publicos de referencia e nao inclui material, uniforme ou condicao comercial nao detalhada na base.
A base publica tambem menciona: Valor comercial publico de referencia para 2026. Ha politica comercial para irmaos e pagamento pontual.
- `llamaindex`: status 200, latency 138.9ms, keyword pass `True`, quality `100`, reason `llamaindex_public_pricing_projection`
  answer: Se eu usar a taxa publica de matricula hoje publicada nos segmentos publicados que usam essa mesma referencia, a simulacao fica 3 x R$ 350,00 = R$ 1.050,00.
Essa conta usa apenas os valores publicos de referencia e nao inclui material, uniforme ou condicao comercial nao detalhada na base.
A base publica tambem menciona: Valor comercial publico de referencia para 2026. Ha politica comercial para irmaos e pagamento pontual.
- `specialist_supervisor`: status 200, latency 85.8ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_fast_path:pricing_projection`
  answer: Usando a referencia publica atual para Ensino Fundamental II. 3 aluno(s) dariam R$ 1.050,00 de matricula e R$ 3.840,00 por mes,

### como estao meus pagamentos?

- Slice: `protected`
- Thread: `random_protected_finance_academic` turn `1`
- `langgraph`: status 200, latency 248.3ms, keyword pass `True`, quality `100`, reason `dados estruturados devem passar por service deterministico`
  answer: Resumo financeiro das contas vinculadas:
- Total de faturas em aberto: 1
- Total de faturas vencidas: 0
- Lucas Oliveira: 0 em aberto, 0 vencidas
  2026-03: vencimento 2026-03-10, status paga, valor 1450.00
- Ana Oliveira: 1 em aberto, 0 vencidas
- `crewai`: status 200, latency 11924.3ms, keyword pass `False`, quality `80`, reason `crewai_public_flow_completed`
  errors: missing_expected_keyword
  answer: Nao consegui concluir essa resposta agora pelo caminho principal configurado. Tente reformular em uma frase mais direta ou repetir em instantes.
- `python_functions`: status 200, latency 216.3ms, keyword pass `True`, quality `100`, reason `python_functions_native_structured:finance`
  answer: Resumo financeiro das contas vinculadas:
- Total de faturas em aberto: 1
- Total de faturas vencidas: 0
- Lucas Oliveira: 0 em aberto, 0 vencidas
  2026-03: vencimento 2026-03-10, status paga, valor 1450.00
- Ana Oliveira: 1 em aberto, 0 vencidas
- `llamaindex`: status 200, latency 247.0ms, keyword pass `True`, quality `100`, reason `dados estruturados devem passar por service deterministico`
  answer: Resumo financeiro das contas vinculadas:
- Total de faturas em aberto: 1
- Total de faturas vencidas: 0
- Lucas Oliveira: 0 em aberto, 0 vencidas
  2026-03: vencimento 2026-03-10, status paga, valor 1450.00
- Ana Oliveira: 1 em aberto, 0 vencidas
- `specialist_supervisor`: status 200, latency 153.1ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_tool_first:financial_summary_aggregate`
  answer: Resumo financeiro das contas vinculadas:
- Total de faturas em aberto: 1
- Total de faturas vencidas: 0
- Lucas Oliveira: 0 em aberto, 0 vencidas
  2026-03: vencimento 2026-03-10, status paid, valor 1450.00
- Ana Oliveira: 1 em aberto, 0 vencidas
  2026-03: vencimento 2026-03-10, status open, valor 1450.00

### e as notas?

- Slice: `protected`
- Thread: `random_protected_finance_academic` turn `2`
- `langgraph`: status 200, latency 143.7ms, keyword pass `True`, quality `100`, reason `o turno atual trouxe pistas explicitas de outro dominio protegido e o roteamento foi corrigido`
  answer: Sua conta tem mais de um aluno vinculado. Diga qual aluno deseja consultar: Lucas Oliveira (MAT-2026-001), Ana Oliveira (MAT-2026-002).
- `crewai`: status 200, latency 182.6ms, keyword pass `True`, quality `100`, reason `protected_shadow_needs_student_clarification`
  answer: Posso te ajudar com Lucas Oliveira, Ana Oliveira. Me diga qual aluno voce quer consultar.
- `python_functions`: status 200, latency 148.2ms, keyword pass `True`, quality `100`, reason `python_functions_native_structured:academic`
  answer: Sua conta tem mais de um aluno vinculado. Diga qual aluno deseja consultar: Lucas Oliveira (MAT-2026-001), Ana Oliveira (MAT-2026-002).
- `llamaindex`: status 200, latency 154.2ms, keyword pass `True`, quality `100`, reason `dados estruturados devem passar por service deterministico`
  answer: Sua conta tem mais de um aluno vinculado. Diga qual aluno deseja consultar: Lucas Oliveira (MAT-2026-001), Ana Oliveira (MAT-2026-002).
- `specialist_supervisor`: status 200, latency 171.8ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_tool_first:academic_summary_aggregate`
  answer: Panorama academico das contas vinculadas:
- Lucas Oliveira: Fisica 5,9; Matematica 7,7; Portugues 8,3
- Ana Oliveira: Fisica 6,4; Matematica 7,4; Portugues 8,4

### ana, notas

- Slice: `protected`
- Thread: `random_protected_finance_academic` turn `3`
- `langgraph`: status 200, latency 201.8ms, keyword pass `True`, quality `100`, reason `dados estruturados devem passar por service deterministico`
  answer: Notas de Ana Oliveira:
- Biologia - Avaliacao B1: 8.20/10.00
- Educacao Fisica - Avaliacao 2026-B1 - EF: 6.90/10.00
- Filosofia - Avaliacao 2026-B1 - FIL: 7.40/10.00
- Fisica - Avaliacao 2026-B1 - FIS: 6.30/10.00
- Geografia - Avaliacao 2026-B1 - GEO: 6.90/10.00
- Historia - Avaliacao 2026-B1 - HIS: 7.20/10.00
- Ingles - Avaliacao B1: 9.30/10.00
- Matematica - Avaliacao B1: 7.80/10.00
- `crewai`: status 200, latency 451.4ms, keyword pass `False`, quality `80`, reason `crewai_protected_fast_path`
  errors: missing_expected_keyword
  answer: As notas mais recentes de Ana Oliveira incluem Biologia: 8.20/10.00; Educacao Fisica: 6.90/10.00; Filosofia: 7.40/10.00; Fisica: 6.30/10.00; Geografia: 6.90/10.00; Historia: 7.20/10.00; Ingles: 9.30/10.00; Matematica: 7.80/10.00.
- `python_functions`: status 200, latency 212.2ms, keyword pass `True`, quality `100`, reason `python_functions_native_structured:academic`
  answer: Notas de Ana Oliveira:
- Biologia - Avaliacao B1: 8.20/10.00
- Educacao Fisica - Avaliacao 2026-B1 - EF: 6.90/10.00
- Filosofia - Avaliacao 2026-B1 - FIL: 7.40/10.00
- Fisica - Avaliacao 2026-B1 - FIS: 6.30/10.00
- Geografia - Avaliacao 2026-B1 - GEO: 6.90/10.00
- Historia - Avaliacao 2026-B1 - HIS: 7.20/10.00
- Ingles - Avaliacao B1: 9.30/10.00
- Matematica - Avaliacao B1: 7.80/10.00
- `llamaindex`: status 200, latency 204.3ms, keyword pass `True`, quality `100`, reason `dados estruturados devem passar por service deterministico`
  answer: Notas de Ana Oliveira:
- Biologia - Avaliacao B1: 8.20/10.00
- Educacao Fisica - Avaliacao 2026-B1 - EF: 6.90/10.00
- Filosofia - Avaliacao 2026-B1 - FIL: 7.40/10.00
- Fisica - Avaliacao 2026-B1 - FIS: 6.30/10.00
- Geografia - Avaliacao 2026-B1 - GEO: 6.90/10.00
- Historia - Avaliacao 2026-B1 - HIS: 7.20/10.00
- Ingles - Avaliacao B1: 9.30/10.00
- Matematica - Avaliacao B1: 7.80/10.00
- `specialist_supervisor`: status 200, latency 126.0ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_tool_first:academic_summary`
  answer: Notas de Ana Oliveira:
- Fisica: media parcial 6,4
- Matematica: media parcial 7,4
- Portugues: media parcial 8,4

### quanto falta pra ana passar em fisica?

- Slice: `protected`
- Thread: `random_protected_finance_academic` turn `4`
- `langgraph`: status 200, latency 201.2ms, keyword pass `True`, quality `100`, reason `dados estruturados devem passar por service deterministico`
  answer: Com as notas lancadas ate agora, Ana Oliveira esta com media parcial de 6,4/10 em Fisica. Se a referencia de aprovacao for 7,0, faltam 0,6 ponto(s) para atingir essa media.
- `crewai`: status 200, latency 11776.0ms, keyword pass `False`, quality `80`, reason `crewai_protected_flow_timeout`
  errors: missing_expected_keyword
  answer: Eu nao consegui consolidar essa consulta protegida com seguranca agora sobre Ana Oliveira. Se quiser, me diga exatamente se voce quer notas, faltas, provas, documentacao, matricula ou financeiro.
- `python_functions`: status 200, latency 198.2ms, keyword pass `True`, quality `100`, reason `python_functions_native_structured:academic`
  answer: Com as notas lancadas ate agora, Ana Oliveira esta com media parcial de 6,4/10 em Fisica. Se a referencia de aprovacao for 7,0, faltam 0,6 ponto(s) para atingir essa media.
- `llamaindex`: status 200, latency 212.2ms, keyword pass `True`, quality `100`, reason `dados estruturados devem passar por service deterministico`
  answer: Com as notas lancadas ate agora, Ana Oliveira esta com media parcial de 6,4/10 em Fisica. Se a referencia de aprovacao for 7,0, faltam 0,6 ponto(s) para atingir essa media.
- `specialist_supervisor`: status 200, latency 118.9ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_fast_path:academic_grade_requirement`
  answer: Hoje Ana Oliveira esta com media parcial 6,4 em Fisica. Para chegar a 7,0, faltam 0,6 ponto(s).

### como esta a documentacao da ana?

- Slice: `protected`
- Thread: `random_protected_documents` turn `1`
- `langgraph`: status 200, latency 174.8ms, keyword pass `True`, quality `100`, reason `status administrativo autenticado exige service deterministico`
  answer: Situacao documental de Ana Oliveira hoje: com pendencias.
- `crewai`: status 200, latency 450.3ms, keyword pass `True`, quality `100`, reason `crewai_protected_fast_path`
  answer: A situacao documental de Ana Oliveira hoje esta com pendencias.
- `python_functions`: status 200, latency 154.6ms, keyword pass `True`, quality `100`, reason `python_functions_native_structured:institution`
  answer: Situacao documental de Ana Oliveira hoje: com pendencias.
- `llamaindex`: status 200, latency 170.6ms, keyword pass `True`, quality `100`, reason `status administrativo autenticado exige service deterministico`
  answer: Situacao documental de Ana Oliveira hoje: com pendencias.
- `specialist_supervisor`: status 200, latency 123.9ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_tool_first:administrative_status`
  answer: Hoje Ana Oliveira esta com pendencias na documentacao. Ainda falta anexar um comprovante de residencia atualizado para Ana Oliveira concluir a conferencia documental. Envie o comprovante atualizado pelo portal autenticado ou pela secretaria escolar para concluir a analise.

### quero falar com o financeiro

- Slice: `support`
- Thread: `random_support` turn `1`
- `langgraph`: status 200, latency 158.5ms, keyword pass `True`, quality `100`, reason `o usuario demonstrou necessidade de atendimento humano ou operacional`
  answer: Encaminhei sua solicitacao para a fila de financeiro. Protocolo: ATD-20260330-BD2E43FD. Status atual: queued. A equipe humana pode continuar esse atendimento no portal operacional.
- `crewai`: status 200, latency 232.8ms, keyword pass `True`, quality `100`, reason `support_handoff_created`
  answer: Encaminhei sua solicitacao para a fila de financeiro. Protocolo: ATD-20260330-5B0B4357. Status atual: queued. A equipe humana podera continuar esse atendimento no portal operacional.
- `python_functions`: status 200, latency 163.4ms, keyword pass `True`, quality `100`, reason `o usuario demonstrou necessidade de atendimento humano ou operacional`
  answer: Encaminhei sua solicitacao para a fila de financeiro. Protocolo: ATD-20260330-8A9AC386. Status atual: queued. A equipe humana pode continuar esse atendimento no portal operacional.
- `llamaindex`: status 200, latency 149.5ms, keyword pass `True`, quality `100`, reason `o usuario demonstrou necessidade de atendimento humano ou operacional`
  answer: Encaminhei sua solicitacao para a fila de financeiro. Protocolo: ATD-20260330-DF4D512D. Status atual: queued. A equipe humana pode continuar esse atendimento no portal operacional.
- `specialist_supervisor`: status 200, latency 104.3ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_tool_first:support_handoff`
  answer: Acionei o financeiro para voce. Protocolo: REQ-20260330-26E0E5. Fila responsavel: financeiro. Ticket operacional: ATD-20260330-078CFB82. Se quiser, eu tambem posso acompanhar o status deste atendimento.

### como esta esse atendimento?

- Slice: `support`
- Thread: `random_support` turn `2`
- `langgraph`: status 200, latency 152.3ms, keyword pass `True`, quality `100`, reason `a solicitacao pode ser executada por workflow estruturado com protocolo`
  answer: Status do atendimento: ele segue em fila na fila de financeiro. Protocolo: ATD-20260330-BD2E43FD. Resumo: Atendimento institucional. Se quiser, eu tambem posso te orientar sobre o proximo setor ou resumir o que ja foi registrado.
- `crewai`: status 200, latency 12036.1ms, keyword pass `False`, quality `80`, reason `crewai_public_flow_completed`
  errors: missing_expected_keyword
  answer: Nao consegui concluir essa resposta agora pelo caminho principal configurado. Tente reformular em uma frase mais direta ou repetir em instantes.
- `python_functions`: status 200, latency 162.1ms, keyword pass `True`, quality `100`, reason `python_functions_native_structured:support`
  answer: Status do atendimento: ele segue em fila na fila de financeiro. Protocolo: ATD-20260330-8A9AC386. Resumo: Atendimento institucional. Se quiser, eu tambem posso te orientar sobre o proximo setor ou resumir o que ja foi registrado.
- `llamaindex`: status 200, latency 162.6ms, keyword pass `True`, quality `100`, reason `a solicitacao pode ser executada por workflow estruturado com protocolo`
  answer: Status do atendimento: ele segue em fila na fila de financeiro. Protocolo: ATD-20260330-DF4D512D. Resumo: Atendimento institucional. Se quiser, eu tambem posso te orientar sobre o proximo setor ou resumir o que ja foi registrado.
- `specialist_supervisor`: status 200, latency 86.2ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_tool_first:support_status`
  answer: O atendimento sobre quero falar com o financeiro esta com status queued. Protocolo: REQ-20260330-26E0E5. Fila: financeiro. Ticket operacional: ATD-20260330-078CFB82.

### quero agendar uma visita na quinta a tarde

- Slice: `workflow`
- Thread: `random_workflow` turn `1`
- `langgraph`: status 200, latency 165.4ms, keyword pass `True`, quality `100`, reason `a solicitacao pode ser executada por workflow estruturado com protocolo`
  answer: Pedido de visita registrado para o Colegio Horizonte. Protocolo: VIS-20260330-5851DA. Preferencia informada: 2026-04-02 - tarde. Fila responsavel: admissoes. Ticket operacional: ATD-20260330-ECF4D07A. A equipe comercial valida a janela e retorna com a confirmacao.
- `crewai`: status 200, latency 242.4ms, keyword pass `True`, quality `100`, reason `workflow_visit_create`
  answer: Pedido de visita registrado para o Colegio Horizonte. Protocolo: VIS-20260330-D9C95A. Preferencia informada: 02/04/2026 - tarde. Fila responsavel: admissoes. Ticket operacional: ATD-20260330-663C78CC. A equipe comercial valida a janela e retorna com a confirmacao.
- `python_functions`: status 200, latency 176.4ms, keyword pass `True`, quality `100`, reason `python_functions_native_structured:support`
  answer: Pedido de visita registrado para o Colegio Horizonte. Protocolo: VIS-20260330-880884. Preferencia informada: 2026-04-02 - tarde. Fila responsavel: admissoes. Ticket operacional: ATD-20260330-7AB4B048. A equipe comercial valida a janela e retorna com a confirmacao.
- `llamaindex`: status 200, latency 253.4ms, keyword pass `True`, quality `100`, reason `a solicitacao pode ser executada por workflow estruturado com protocolo`
  answer: Pedido de visita registrado para o Colegio Horizonte. Protocolo: VIS-20260330-876C6C. Preferencia informada: 2026-04-02 - tarde. Fila responsavel: admissoes. Ticket operacional: ATD-20260330-AD944A01. A equipe comercial valida a janela e retorna com a confirmacao.
- `specialist_supervisor`: status 200, latency 127.3ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_tool_first:visit_booking`
  answer: Pedido de visita registrado. Protocolo: VIS-20260330-BBB542. Preferencia registrada: quinta a tarde. Ticket operacional: ATD-20260330-7031C2EA. Se quiser, eu tambem posso acompanhar o status ou remarcar a visita.

### se eu precisar remarcar, como faco?

- Slice: `workflow`
- Thread: `random_workflow` turn `2`
- `langgraph`: status 200, latency 150.6ms, keyword pass `True`, quality `100`, reason `a solicitacao pode ser executada por workflow estruturado com protocolo`
  answer: Consigo remarcar a visita por aqui. Protocolo: VIS-20260330-5851DA. Ticket operacional: ATD-20260330-ECF4D07A. Me diga pelo menos o novo dia ou a janela desejada, por exemplo: "remarque para sexta de manha" ou "troque para 28/03 as 10h".
- `crewai`: status 200, latency 203.9ms, keyword pass `True`, quality `100`, reason `workflow_visit_reschedule_guidance`
  answer: Se voce precisar remarcar, me passe o protocolo VIS-20260330-D9C95A ou o novo horario desejado que eu sigo com essa atualizacao para a fila de admissoes.
- `python_functions`: status 200, latency 137.4ms, keyword pass `True`, quality `100`, reason `python_functions_native_structured:support`
  answer: Consigo remarcar a visita por aqui. Protocolo: VIS-20260330-880884. Ticket operacional: ATD-20260330-7AB4B048. Me diga pelo menos o novo dia ou a janela desejada, por exemplo: "remarque para sexta de manha" ou "troque para 28/03 as 10h".
- `llamaindex`: status 200, latency 155.6ms, keyword pass `True`, quality `100`, reason `a solicitacao pode ser executada por workflow estruturado com protocolo`
  answer: Consigo remarcar a visita por aqui. Protocolo: VIS-20260330-876C6C. Ticket operacional: ATD-20260330-AD944A01. Me diga pelo menos o novo dia ou a janela desejada, por exemplo: "remarque para sexta de manha" ou "troque para 28/03 as 10h".
- `specialist_supervisor`: status 200, latency 96.7ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_tool_first:visit_reschedule_guidance`
  answer: Para remarcar a visita, eu sigo pelo protocolo VIS-20260330-BBB542. A preferencia atual registrada e quinta a tarde. Me diga o novo dia ou janela desejada e eu atualizo o pedido. Ticket operacional: ATD-20260330-7031C2EA.

