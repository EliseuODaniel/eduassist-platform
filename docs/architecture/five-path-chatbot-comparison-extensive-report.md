# Five-Path Chatbot Comparison Report

Date: 2026-03-31T00:17:34.483066+00:00

Dataset: `tests/evals/datasets/five_path_extended_probe_cases.json`

Run prefix: `debug:five-path:20260331T000816Z`

## Stack Summary

| Stack | OK | Keyword pass | Quality | Avg latency |
| --- | --- | --- | --- | --- |
| `langgraph` | `53/53` | `42/53` | `93.6` | `211.2 ms` |
| `crewai` | `48/53` | `10/53` | `73.5` | `4322.0 ms` |
| `python_functions` | `53/53` | `39/53` | `92.6` | `174.5 ms` |
| `llamaindex` | `53/53` | `38/53` | `92.1` | `177.7 ms` |
| `specialist_supervisor` | `31/53` | `18/53` | `52.2` | `5637.6 ms` |

## By Slice

- `protected`
  - `langgraph`: ok 18/18, keyword pass 11/18, quality 85.6, latency 161.3ms
  - `crewai`: ok 17/18, keyword pass 4/18, quality 74.4, latency 2813.8ms
  - `python_functions`: ok 18/18, keyword pass 11/18, quality 86.1, latency 159.1ms
  - `llamaindex`: ok 18/18, keyword pass 11/18, quality 85.6, latency 163.0ms
  - `specialist_supervisor`: ok 14/18, keyword pass 5/18, quality 65.1, latency 2971.7ms
- `public`
  - `langgraph`: ok 27/27, keyword pass 23/27, quality 97.0, latency 260.9ms
  - `crewai`: ok 23/27, keyword pass 3/27, quality 68.6, latency 6081.7ms
  - `python_functions`: ok 27/27, keyword pass 23/27, quality 97.0, latency 195.1ms
  - `llamaindex`: ok 27/27, keyword pass 22/27, quality 96.3, latency 196.0ms
  - `specialist_supervisor`: ok 11/27, keyword pass 9/27, quality 38.4, latency 8012.5ms
- `support`
  - `langgraph`: ok 6/6, keyword pass 6/6, quality 100.0, latency 164.2ms
  - `crewai`: ok 6/6, keyword pass 1/6, quality 83.3, latency 2308.8ms
  - `python_functions`: ok 6/6, keyword pass 3/6, quality 90.0, latency 144.7ms
  - `llamaindex`: ok 6/6, keyword pass 3/6, quality 90.0, latency 151.7ms
  - `specialist_supervisor`: ok 4/6, keyword pass 2/6, quality 60.0, latency 4789.2ms
- `workflow`
  - `langgraph`: ok 2/2, keyword pass 2/2, quality 100.0, latency 131.2ms
  - `crewai`: ok 2/2, keyword pass 2/2, quality 100.0, latency 179.9ms
  - `python_functions`: ok 2/2, keyword pass 2/2, quality 100.0, latency 124.2ms
  - `llamaindex`: ok 2/2, keyword pass 2/2, quality 100.0, latency 141.4ms
  - `specialist_supervisor`: ok 2/2, keyword pass 2/2, quality 100.0, latency 114.6ms

## Error Types

- `langgraph`: followup_context_drop=4, missing_expected_keyword=11, repetitive_reply=2
- `crewai`: followup_context_drop=5, missing_expected_keyword=38, repetitive_reply=1, request_failed=5, unnecessary_clarification=1
- `python_functions`: followup_context_drop=4, missing_expected_keyword=14, repetitive_reply=1
- `llamaindex`: followup_context_drop=4, missing_expected_keyword=15, repetitive_reply=2
- `specialist_supervisor`: followup_context_drop=1, missing_expected_keyword=13, request_failed=22, unnecessary_clarification=4

## Prompt Results

### a escola fica em qual bairro de sao paulo?

- Slice: `public`
- Thread: `random_public_location` turn `1`
- `langgraph`: status 200, latency 186.4ms, keyword pass `True`, quality `100`, reason `fato institucional canonico deve vir de fonte estruturada`
  answer: Colegio Horizonte fica em Rua das Acacias, 1450, Vila Mariana, Sao Paulo, SP, CEP 04567-120.
- `crewai`: status 200, latency 11879.1ms, keyword pass `False`, quality `80`, reason `crewai_public_flow_completed`
  errors: missing_expected_keyword
  answer: Nao consegui concluir essa resposta agora pelo caminho principal configurado. Tente reformular em uma frase mais direta ou repetir em instantes.
- `python_functions`: status 200, latency 130.3ms, keyword pass `True`, quality `100`, reason `python_functions_native_structured:institution`
  answer: Colegio Horizonte fica em Rua das Acacias, 1450, Vila Mariana, Sao Paulo, SP, CEP 04567-120.
- `llamaindex`: status 200, latency 140.9ms, keyword pass `True`, quality `100`, reason `llamaindex_public_profile`
  answer: Colegio Horizonte fica em Rua das Acacias, 1450, Vila Mariana, Sao Paulo, SP, CEP 04567-120.
- `specialist_supervisor`: status 200, latency 71.2ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_fast_path:district`
  answer: A escola fica no bairro Vila Mariana, Sao Paulo/SP.

### o ensino medio segue a bncc?

- Slice: `public`
- Thread: `random_public_curriculum` turn `1`
- `langgraph`: status 200, latency 146.8ms, keyword pass `True`, quality `100`, reason `fato institucional canonico deve vir de fonte estruturada`
  answer: No Ensino Medio, Colegio Horizonte segue a BNCC e um curriculo proprio de aprofundamento academico. Os componentes que aparecem hoje na base publica incluem Lingua Portuguesa e producao textual, Matematica, Biologia, Fisica, Quimica, Historia, Geografia, Lingua Inglesa, alem de projeto de vida, monitorias e trilhas eletivas.
- `crewai`: status 200, latency 839.5ms, keyword pass `True`, quality `100`, reason `crewai_public_fast_path`
  answer: No Ensino Medio, a escola segue a BNCC e o curriculo do Ensino Medio articulado com projeto de vida, producao textual, cultura digital e aprofundamento academico progressivo.
- `python_functions`: status 200, latency 128.9ms, keyword pass `True`, quality `100`, reason `python_functions_native_structured:institution`
  answer: No Ensino Medio, Colegio Horizonte segue a BNCC e um curriculo proprio de aprofundamento academico. Os componentes que aparecem hoje na base publica incluem Lingua Portuguesa e producao textual, Matematica, Biologia, Fisica, Quimica, Historia, Geografia, Lingua Inglesa, alem de projeto de vida, monitorias e trilhas eletivas.
- `llamaindex`: status 200, latency 131.4ms, keyword pass `True`, quality `100`, reason `llamaindex_public_profile`
  answer: No Ensino Medio, Colegio Horizonte segue a BNCC e um curriculo proprio de aprofundamento academico. Os componentes que aparecem hoje na base publica incluem Lingua Portuguesa e producao textual, Matematica, Biologia, Fisica, Quimica, Historia, Geografia, Lingua Inglesa, alem de projeto de vida, monitorias e trilhas eletivas.
- `specialist_supervisor`: status 200, latency 62.9ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_fast_path:bncc`
  answer: Sim. A escola trabalha com base curricular alinhada a A escola segue a BNCC e o curriculo do Ensino Medio articulado com projeto de vida, producao textual, cultura digital e aprofundamento academico progressivo..

### quais canais eu posso usar para mandar documentos?

- Slice: `public`
- Thread: `random_public_documents` turn `1`
- `langgraph`: status 200, latency 124.3ms, keyword pass `True`, quality `100`, reason `fato institucional canonico deve vir de fonte estruturada`
  answer: Sim. O envio inicial de documentos pode ser feito por canal digital.
Hoje os canais mais diretos publicados para isso sao:
- portal institucional
- email da secretaria
- secretaria presencial
No processo de matricula, o envio inicial pode ser digital. A validacao final continua com a secretaria.
O chat aberto nao deve receber documentos completos ou dados sensiveis. Quando possivel, use o portal autenticado ou o email institucional.
- `crewai`: status 200, latency 152.8ms, keyword pass `False`, quality `80`, reason `crewai_protected_auth_required`
  errors: missing_expected_keyword
  answer: Essa consulta depende de autenticacao e vinculo da sua conta no Telegram. Use o portal da escola para gerar o codigo de vinculacao e depois envie o comando /start link_<codigo> ao bot.
- `python_functions`: status 200, latency 94.7ms, keyword pass `True`, quality `100`, reason `python_functions_native_contextual_public_answer`
  answer: Sim. O envio inicial de documentos pode ser feito por canal digital.
Hoje os canais mais diretos publicados para isso sao:
- portal institucional
- email da secretaria
- secretaria presencial
No processo de matricula, o envio inicial pode ser digital. A validacao final continua com a secretaria.
O chat aberto nao deve receber documentos completos ou dados sensiveis. Quando possivel, use o portal autenticado ou o email institucional.
- `llamaindex`: status 200, latency 116.9ms, keyword pass `True`, quality `100`, reason `llamaindex_public_profile`
  answer: Sim. O envio inicial de documentos pode ser feito por canal digital.
Hoje os canais mais diretos publicados para isso sao:
- portal institucional
- email da secretaria
- secretaria presencial
No processo de matricula, o envio inicial pode ser digital. A validacao final continua com a secretaria.
O chat aberto nao deve receber documentos completos ou dados sensiveis. Quando possivel, use o portal autenticado ou o email institucional.
- `specialist_supervisor`: status 200, latency 65.3ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_tool_first:document_submission_policy`
  answer: Voce pode mandar documentos pelo portal institucional, pelo email da secretaria ou levar na secretaria presencial para conferencia final. No processo de matricula, o envio inicial pode ser digital. A validacao final continua com a secretaria. O chat aberto nao deve receber documentos completos ou dados sensiveis. Quando possivel, use o portal autenticado ou o email institucional.

### a biblioteca tem nome e horario ou e so marketing?

- Slice: `public`
- Thread: `random_public_library` turn `1`
- `langgraph`: status 200, latency 133.6ms, keyword pass `True`, quality `100`, reason `fato institucional canonico deve vir de fonte estruturada`
  answer: O horario de Biblioteca Aurora hoje funciona assim: Atendimento ao publico de segunda a sexta, das 7h30 as 18h00.

Turnos e horarios documentados:
- Ensino Fundamental II (Manha): 07:15 as 12:30. Oficinas, plantoes, esportes e estudo orientado no contraturno em dias alternados.
- Ensino Medio (Manha): 07:15 as 12:50. Trilhas eletivas, monitorias e laboratorios no contraturno a partir das 14h00.
- Fundamental II e Ensino Medio (Integral opcional): 07:00 as 17:30. Inclui estudo orientado, almoco, oficinas, esportes e acompanhamento no contraturno.
- `crewai`: status 200, latency 11833.1ms, keyword pass `False`, quality `80`, reason `crewai_public_flow_completed`
  errors: missing_expected_keyword
  answer: Nao consegui concluir essa resposta agora pelo caminho principal configurado. Tente reformular em uma frase mais direta ou repetir em instantes.
- `python_functions`: status 200, latency 107.4ms, keyword pass `True`, quality `100`, reason `python_functions_native_contextual_public_answer`
  answer: A biblioteca se chama Biblioteca Aurora e funciona de segunda a sexta, das 7h30 as 18h00.
- `llamaindex`: status 200, latency 139.0ms, keyword pass `True`, quality `100`, reason `llamaindex_public_profile`
  answer: O horario de Biblioteca Aurora hoje funciona assim: Atendimento ao publico de segunda a sexta, das 7h30 as 18h00.

Turnos e horarios documentados:
- Ensino Fundamental II (Manha): 07:15 as 12:30. Oficinas, plantoes, esportes e estudo orientado no contraturno em dias alternados.
- Ensino Medio (Manha): 07:15 as 12:50. Trilhas eletivas, monitorias e laboratorios no contraturno a partir das 14h00.
- Fundamental II e Ensino Medio (Integral opcional): 07:00 as 17:30. Inclui estudo orientado, almoco, oficinas, esportes e acompanhamento no contraturno.
- `specialist_supervisor`: status 200, latency 64.6ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_fast_path:library_hours`
  answer: A biblioteca se chama Biblioteca Aurora e funciona Atendimento ao publico de segunda a sexta, das 7h30 as 18h00.

### quando abre a matricula de 2026?

- Slice: `public`
- Thread: `random_public_timeline` turn `1`
- `langgraph`: status 200, latency 146.5ms, keyword pass `True`, quality `100`, reason `datas institucionais publicas devem vir de leitura estruturada e auditavel`
  answer: O ciclo publico de matricula para 2026 foi aberto em 6 de outubro de 2025, com pre-cadastro, visita orientada opcional e triagem inicial de documentos. O atendimento comercial segue enquanto houver vagas por segmento.
- `crewai`: status 200, latency 162.3ms, keyword pass `False`, quality `80`, reason `crewai_protected_auth_required`
  errors: missing_expected_keyword
  answer: Essa consulta depende de autenticacao e vinculo da sua conta no Telegram. Use o portal da escola para gerar o codigo de vinculacao e depois envie o comando /start link_<codigo> ao bot.
- `python_functions`: status 200, latency 129.6ms, keyword pass `True`, quality `100`, reason `python_functions_native_structured:calendar`
  answer: O ciclo publico de matricula para 2026 foi aberto em 6 de outubro de 2025, com pre-cadastro, visita orientada opcional e triagem inicial de documentos. O atendimento comercial segue enquanto houver vagas por segmento.
- `llamaindex`: status 200, latency 127.5ms, keyword pass `True`, quality `100`, reason `llamaindex_public_profile`
  answer: O ciclo publico de matricula para 2026 foi aberto em 6 de outubro de 2025, com pre-cadastro, visita orientada opcional e triagem inicial de documentos. O atendimento comercial segue enquanto houver vagas por segmento.
- `specialist_supervisor`: status 200, latency 69.2ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_tool_first:public_timeline`
  answer: O ciclo publico de matricula para 2026 foi aberto em 6 de outubro de 2025, com pre-cadastro, visita orientada opcional e triagem inicial de documentos. O atendimento comercial segue enquanto houver vagas por segmento.

### e quando comecam as aulas?

- Slice: `public`
- Thread: `random_public_timeline` turn `2`
- `langgraph`: status 200, latency 150.2ms, keyword pass `True`, quality `100`, reason `datas institucionais publicas devem vir de leitura estruturada e auditavel`
  answer: As aulas do Ensino Fundamental II e do Ensino Medio comecam em 2 de fevereiro de 2026. A semana de acolhimento do 6o ano e da primeira serie ocorre entre 2 e 6 de fevereiro.
- `crewai`: status 200, latency 691.2ms, keyword pass `True`, quality `100`, reason `crewai_public_fast_path`
  answer: As aulas do Ensino Fundamental II e do Ensino Medio comecam em 2 de fevereiro de 2026.
- `python_functions`: status 200, latency 102.1ms, keyword pass `True`, quality `100`, reason `python_functions_native_contextual_public_answer`
  answer: As aulas do Ensino Fundamental II e do Ensino Medio comecam em 2 de fevereiro de 2026. A semana de acolhimento do 6o ano e da primeira serie ocorre entre 2 e 6 de fevereiro.
- `llamaindex`: status 200, latency 144.1ms, keyword pass `True`, quality `100`, reason `llamaindex_public_profile`
  answer: As aulas do Ensino Fundamental II e do Ensino Medio comecam em 2 de fevereiro de 2026. A semana de acolhimento do 6o ano e da primeira serie ocorre entre 2 e 6 de fevereiro.
- `specialist_supervisor`: status 200, latency 74.7ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_tool_first:public_timeline`
  answer: As aulas do Ensino Fundamental II e do Ensino Medio comecam em 2 de fevereiro de 2026. A semana de acolhimento do 6o ano e da primeira serie ocorre entre 2 e 6 de fevereiro.

### qual a mensalidade do ensino medio?

- Slice: `public`
- Thread: `random_public_pricing` turn `1`
- `langgraph`: status 200, latency 146.2ms, keyword pass `True`, quality `100`, reason `fato institucional canonico deve vir de fonte estruturada`
  answer: Para Ensino Medio no turno Manha, a mensalidade publica de referencia em 2026 e R$ 1.450,00 e a taxa de matricula e R$ 350,00. Valor comercial publico de referencia para 2026. Ha politica comercial para irmaos e pagamento pontual. Se quiser, eu tambem posso resumir bolsas, descontos comerciais e canais de matricula.
- `crewai`: status 200, latency 816.7ms, keyword pass `True`, quality `100`, reason `crewai_public_fast_path`
  answer: A mensalidade de referencia para Ensino Medio e R$ 1450.00, com taxa de matricula de R$ 350.00.
- `python_functions`: status 200, latency 133.9ms, keyword pass `True`, quality `100`, reason `python_functions_native_structured:institution`
  answer: Para Ensino Medio no turno Manha, a mensalidade publica de referencia em 2026 e R$ 1.450,00 e a taxa de matricula e R$ 350,00. Valor comercial publico de referencia para 2026. Ha politica comercial para irmaos e pagamento pontual. Se quiser, eu tambem posso resumir bolsas, descontos comerciais e canais de matricula.
- `llamaindex`: status 200, latency 138.4ms, keyword pass `True`, quality `100`, reason `llamaindex_public_profile`
  answer: Para Ensino Medio no turno Manha, a mensalidade publica de referencia em 2026 e R$ 1.450,00 e a taxa de matricula e R$ 350,00. Valor comercial publico de referencia para 2026. Ha politica comercial para irmaos e pagamento pontual. Se quiser, eu tambem posso resumir bolsas, descontos comerciais e canais de matricula.
- `specialist_supervisor`: status 200, latency 65.3ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_tool_first:public_pricing_reference`
  answer: Para Ensino Medio no turno Manha, a mensalidade publica de referencia em 2026 e R$ 1.450,00 e a taxa de matricula e R$ 350,00. Valor comercial publico de referencia para 2026. Ha politica comercial para irmaos e pagamento pontual.

### se eu matricular 3 filhos, quanto fica so a matricula?

- Slice: `public`
- Thread: `random_public_pricing` turn `2`
- `langgraph`: status 200, latency 146.6ms, keyword pass `True`, quality `100`, reason `fato institucional canonico deve vir de fonte estruturada`
  answer: Se eu usar a taxa publica de matricula hoje publicada nos segmentos publicados que usam essa mesma referencia, a simulacao fica 3 x R$ 350,00 = R$ 1.050,00.
Essa conta usa apenas os valores publicos de referencia e nao inclui material, uniforme ou condicao comercial nao detalhada na base.
A base publica tambem menciona: Valor comercial publico de referencia para 2026. Ha politica comercial para irmaos e pagamento pontual.
- `crewai`: status 200, latency 158.4ms, keyword pass `False`, quality `80`, reason `crewai_protected_auth_required`
  errors: missing_expected_keyword
  answer: Essa consulta depende de autenticacao e vinculo da sua conta no Telegram. Use o portal da escola para gerar o codigo de vinculacao e depois envie o comando /start link_<codigo> ao bot.
- `python_functions`: status 200, latency 112.9ms, keyword pass `True`, quality `100`, reason `python_functions_native_pricing_projection`
  answer: Se eu usar a taxa publica de matricula hoje publicada nos segmentos publicados que usam essa mesma referencia, a simulacao fica 3 x R$ 350,00 = R$ 1.050,00.
Essa conta usa apenas os valores publicos de referencia e nao inclui material, uniforme ou condicao comercial nao detalhada na base.
A base publica tambem menciona: Valor comercial publico de referencia para 2026. Ha politica comercial para irmaos e pagamento pontual.
- `llamaindex`: status 200, latency 129.6ms, keyword pass `True`, quality `100`, reason `llamaindex_public_pricing_projection`
  answer: Se eu usar a taxa publica de matricula hoje publicada nos segmentos publicados que usam essa mesma referencia, a simulacao fica 3 x R$ 350,00 = R$ 1.050,00.
Essa conta usa apenas os valores publicos de referencia e nao inclui material, uniforme ou condicao comercial nao detalhada na base.
A base publica tambem menciona: Valor comercial publico de referencia para 2026. Ha politica comercial para irmaos e pagamento pontual.
- `specialist_supervisor`: status 200, latency 69.8ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_fast_path:pricing_projection`
  answer: Usando a referencia publica atual para Ensino Fundamental II. 3 aluno(s) dariam R$ 1.050,00 de matricula e R$ 3.840,00 por mes,

### como estao meus pagamentos?

- Slice: `protected`
- Thread: `random_protected_finance_academic` turn `1`
- `langgraph`: status 200, latency 212.2ms, keyword pass `True`, quality `100`, reason `dados estruturados devem passar por service deterministico`
  answer: Resumo financeiro das contas vinculadas:
- Total de faturas em aberto: 1
- Total de faturas vencidas: 0
- Lucas Oliveira: 0 em aberto, 0 vencidas
  2026-03: vencimento 2026-03-10, status paga, valor 1450.00
- Ana Oliveira: 1 em aberto, 0 vencidas
- `crewai`: status 200, latency 11871.5ms, keyword pass `False`, quality `80`, reason `crewai_public_flow_completed`
  errors: missing_expected_keyword
  answer: Nao consegui concluir essa resposta agora pelo caminho principal configurado. Tente reformular em uma frase mais direta ou repetir em instantes.
- `python_functions`: status 200, latency 188.6ms, keyword pass `True`, quality `100`, reason `python_functions_native_structured:finance`
  answer: Resumo financeiro das contas vinculadas:
- Total de faturas em aberto: 1
- Total de faturas vencidas: 0
- Lucas Oliveira: 0 em aberto, 0 vencidas
  2026-03: vencimento 2026-03-10, status paga, valor 1450.00
- Ana Oliveira: 1 em aberto, 0 vencidas
- `llamaindex`: status 200, latency 188.3ms, keyword pass `True`, quality `100`, reason `dados estruturados devem passar por service deterministico`
  answer: Resumo financeiro das contas vinculadas:
- Total de faturas em aberto: 1
- Total de faturas vencidas: 0
- Lucas Oliveira: 0 em aberto, 0 vencidas
  2026-03: vencimento 2026-03-10, status paga, valor 1450.00
- Ana Oliveira: 1 em aberto, 0 vencidas
- `specialist_supervisor`: status 200, latency 129.8ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_tool_first:financial_summary_aggregate`
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
- `langgraph`: status 200, latency 119.9ms, keyword pass `True`, quality `100`, reason `o turno atual trouxe pistas explicitas de outro dominio protegido e o roteamento foi corrigido`
  answer: Sua conta tem mais de um aluno vinculado. Diga qual aluno deseja consultar: Lucas Oliveira (MAT-2026-001), Ana Oliveira (MAT-2026-002).
- `crewai`: status 200, latency 157.7ms, keyword pass `True`, quality `100`, reason `protected_shadow_needs_student_clarification`
  answer: Posso te ajudar com Lucas Oliveira, Ana Oliveira. Me diga qual aluno voce quer consultar.
- `python_functions`: status 200, latency 130.5ms, keyword pass `True`, quality `100`, reason `python_functions_native_structured:academic`
  answer: Sua conta tem mais de um aluno vinculado. Diga qual aluno deseja consultar: Lucas Oliveira (MAT-2026-001), Ana Oliveira (MAT-2026-002).
- `llamaindex`: status 200, latency 139.6ms, keyword pass `True`, quality `100`, reason `dados estruturados devem passar por service deterministico`
  answer: Sua conta tem mais de um aluno vinculado. Diga qual aluno deseja consultar: Lucas Oliveira (MAT-2026-001), Ana Oliveira (MAT-2026-002).
- `specialist_supervisor`: status 200, latency 149.5ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_tool_first:academic_summary_aggregate`
  answer: Panorama academico das contas vinculadas:
- Lucas Oliveira: Fisica 5,9; Matematica 7,7; Portugues 8,3
- Ana Oliveira: Fisica 6,4; Matematica 7,4; Portugues 8,4

### ana, notas

- Slice: `protected`
- Thread: `random_protected_finance_academic` turn `3`
- `langgraph`: status 200, latency 202.0ms, keyword pass `True`, quality `100`, reason `dados estruturados devem passar por service deterministico`
  answer: Notas de Ana Oliveira:
- Biologia - Avaliacao B1: 8.20/10.00
- Educacao Fisica - Avaliacao 2026-B1 - EF: 6.90/10.00
- Filosofia - Avaliacao 2026-B1 - FIL: 7.40/10.00
- Fisica - Avaliacao 2026-B1 - FIS: 6.30/10.00
- Geografia - Avaliacao 2026-B1 - GEO: 6.90/10.00
- Historia - Avaliacao 2026-B1 - HIS: 7.20/10.00
- Ingles - Avaliacao B1: 9.30/10.00
- Matematica - Avaliacao B1: 7.80/10.00
- `crewai`: status 200, latency 396.0ms, keyword pass `False`, quality `80`, reason `crewai_protected_fast_path`
  errors: missing_expected_keyword
  answer: As notas mais recentes de Ana Oliveira incluem Biologia: 8.20/10.00; Educacao Fisica: 6.90/10.00; Filosofia: 7.40/10.00; Fisica: 6.30/10.00; Geografia: 6.90/10.00; Historia: 7.20/10.00; Ingles: 9.30/10.00; Matematica: 7.80/10.00.
- `python_functions`: status 200, latency 173.1ms, keyword pass `True`, quality `100`, reason `python_functions_native_structured:academic`
  answer: Notas de Ana Oliveira:
- Biologia - Avaliacao B1: 8.20/10.00
- Educacao Fisica - Avaliacao 2026-B1 - EF: 6.90/10.00
- Filosofia - Avaliacao 2026-B1 - FIL: 7.40/10.00
- Fisica - Avaliacao 2026-B1 - FIS: 6.30/10.00
- Geografia - Avaliacao 2026-B1 - GEO: 6.90/10.00
- Historia - Avaliacao 2026-B1 - HIS: 7.20/10.00
- Ingles - Avaliacao B1: 9.30/10.00
- Matematica - Avaliacao B1: 7.80/10.00
- `llamaindex`: status 200, latency 181.3ms, keyword pass `True`, quality `100`, reason `dados estruturados devem passar por service deterministico`
  answer: Notas de Ana Oliveira:
- Biologia - Avaliacao B1: 8.20/10.00
- Educacao Fisica - Avaliacao 2026-B1 - EF: 6.90/10.00
- Filosofia - Avaliacao 2026-B1 - FIL: 7.40/10.00
- Fisica - Avaliacao 2026-B1 - FIS: 6.30/10.00
- Geografia - Avaliacao 2026-B1 - GEO: 6.90/10.00
- Historia - Avaliacao 2026-B1 - HIS: 7.20/10.00
- Ingles - Avaliacao B1: 9.30/10.00
- Matematica - Avaliacao B1: 7.80/10.00
- `specialist_supervisor`: status 200, latency 100.1ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_tool_first:academic_summary`
  answer: Notas de Ana Oliveira:
- Fisica: media parcial 6,4
- Matematica: media parcial 7,4
- Portugues: media parcial 8,4

### quanto falta pra ana passar em fisica?

- Slice: `protected`
- Thread: `random_protected_finance_academic` turn `4`
- `langgraph`: status 200, latency 179.4ms, keyword pass `True`, quality `100`, reason `dados estruturados devem passar por service deterministico`
  answer: Com as notas lancadas ate agora, Ana Oliveira esta com media parcial de 6,4/10 em Fisica. Se a referencia de aprovacao for 7,0, faltam 0,6 ponto(s) para atingir essa media.
- `crewai`: status 200, latency 11680.7ms, keyword pass `False`, quality `80`, reason `crewai_protected_flow_timeout`
  errors: missing_expected_keyword
  answer: Eu nao consegui consolidar essa consulta protegida com seguranca agora sobre Ana Oliveira. Se quiser, me diga exatamente se voce quer notas, faltas, provas, documentacao, matricula ou financeiro.
- `python_functions`: status 200, latency 197.7ms, keyword pass `True`, quality `100`, reason `python_functions_native_structured:academic`
  answer: Com as notas lancadas ate agora, Ana Oliveira esta com media parcial de 6,4/10 em Fisica. Se a referencia de aprovacao for 7,0, faltam 0,6 ponto(s) para atingir essa media.
- `llamaindex`: status 200, latency 172.1ms, keyword pass `True`, quality `100`, reason `dados estruturados devem passar por service deterministico`
  answer: Com as notas lancadas ate agora, Ana Oliveira esta com media parcial de 6,4/10 em Fisica. Se a referencia de aprovacao for 7,0, faltam 0,6 ponto(s) para atingir essa media.
- `specialist_supervisor`: status 200, latency 107.1ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_fast_path:academic_grade_requirement`
  answer: Hoje Ana Oliveira esta com media parcial 6,4 em Fisica. Para chegar a 7,0, faltam 0,6 ponto(s).

### como esta a documentacao da ana?

- Slice: `protected`
- Thread: `random_protected_documents` turn `1`
- `langgraph`: status 200, latency 149.8ms, keyword pass `True`, quality `100`, reason `status administrativo autenticado exige service deterministico`
  answer: Situacao documental de Ana Oliveira hoje: com pendencias.
- `crewai`: status 200, latency 386.1ms, keyword pass `True`, quality `100`, reason `crewai_protected_fast_path`
  answer: A situacao documental de Ana Oliveira hoje esta com pendencias.
- `python_functions`: status 200, latency 139.3ms, keyword pass `True`, quality `100`, reason `python_functions_native_structured:institution`
  answer: Situacao documental de Ana Oliveira hoje: com pendencias.
- `llamaindex`: status 200, latency 144.7ms, keyword pass `True`, quality `100`, reason `status administrativo autenticado exige service deterministico`
  answer: Situacao documental de Ana Oliveira hoje: com pendencias.
- `specialist_supervisor`: status 200, latency 100.6ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_tool_first:administrative_status`
  answer: Hoje Ana Oliveira esta com pendencias na documentacao. Ainda falta anexar um comprovante de residencia atualizado para Ana Oliveira concluir a conferencia documental. Envie o comprovante atualizado pelo portal autenticado ou pela secretaria escolar para concluir a analise.

### quero falar com o financeiro

- Slice: `support`
- Thread: `random_support` turn `1`
- `langgraph`: status 200, latency 131.7ms, keyword pass `True`, quality `100`, reason `o usuario demonstrou necessidade de atendimento humano ou operacional`
  answer: Encaminhei sua solicitacao para a fila de financeiro. Protocolo: ATD-20260331-038C8364. Status atual: queued. A equipe humana pode continuar esse atendimento no portal operacional.
- `crewai`: status 200, latency 254.4ms, keyword pass `True`, quality `100`, reason `support_handoff_created`
  answer: Encaminhei sua solicitacao para a fila de financeiro. Protocolo: ATD-20260331-55A27285. Status atual: queued. A equipe humana podera continuar esse atendimento no portal operacional.
- `python_functions`: status 200, latency 125.0ms, keyword pass `True`, quality `100`, reason `o usuario demonstrou necessidade de atendimento humano ou operacional`
  answer: Encaminhei sua solicitacao para a fila de financeiro. Protocolo: ATD-20260331-02A7185F. Status atual: queued. A equipe humana pode continuar esse atendimento no portal operacional.
- `llamaindex`: status 200, latency 131.5ms, keyword pass `True`, quality `100`, reason `o usuario demonstrou necessidade de atendimento humano ou operacional`
  answer: Encaminhei sua solicitacao para a fila de financeiro. Protocolo: ATD-20260331-9599B2E6. Status atual: queued. A equipe humana pode continuar esse atendimento no portal operacional.
- `specialist_supervisor`: status 200, latency 87.3ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_tool_first:support_handoff`
  answer: Acionei o financeiro para voce. Protocolo: REQ-20260331-A6C982. Fila responsavel: financeiro. Ticket operacional: ATD-20260331-FE40632C. Se quiser, eu tambem posso acompanhar o status deste atendimento.

### como esta esse atendimento?

- Slice: `support`
- Thread: `random_support` turn `2`
- `langgraph`: status 200, latency 132.9ms, keyword pass `True`, quality `100`, reason `a solicitacao pode ser executada por workflow estruturado com protocolo`
  answer: Status do atendimento: ele segue em fila na fila de financeiro. Protocolo: ATD-20260331-038C8364. Resumo: Atendimento institucional. Se quiser, eu tambem posso te orientar sobre o proximo setor ou resumir o que ja foi registrado.
- `crewai`: status 200, latency 11911.2ms, keyword pass `False`, quality `80`, reason `crewai_public_flow_completed`
  errors: missing_expected_keyword
  answer: Nao consegui concluir essa resposta agora pelo caminho principal configurado. Tente reformular em uma frase mais direta ou repetir em instantes.
- `python_functions`: status 200, latency 144.7ms, keyword pass `True`, quality `100`, reason `python_functions_native_structured:support`
  answer: Status do atendimento: ele segue em fila na fila de financeiro. Protocolo: ATD-20260331-02A7185F. Resumo: Atendimento institucional. Se quiser, eu tambem posso te orientar sobre o proximo setor ou resumir o que ja foi registrado.
- `llamaindex`: status 200, latency 142.0ms, keyword pass `True`, quality `100`, reason `a solicitacao pode ser executada por workflow estruturado com protocolo`
  answer: Status do atendimento: ele segue em fila na fila de financeiro. Protocolo: ATD-20260331-9599B2E6. Resumo: Atendimento institucional. Se quiser, eu tambem posso te orientar sobre o proximo setor ou resumir o que ja foi registrado.
- `specialist_supervisor`: status 200, latency 69.8ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_tool_first:support_status`
  answer: O atendimento sobre quero falar com o financeiro esta com status queued. Protocolo: REQ-20260331-A6C982. Fila: financeiro. Ticket operacional: ATD-20260331-FE40632C.

### quero agendar uma visita na quinta a tarde

- Slice: `workflow`
- Thread: `random_workflow` turn `1`
- `langgraph`: status 200, latency 136.6ms, keyword pass `True`, quality `100`, reason `a solicitacao pode ser executada por workflow estruturado com protocolo`
  answer: Pedido de visita registrado para o Colegio Horizonte. Protocolo: VIS-20260331-FEC62F. Preferencia informada: 2026-04-02 - tarde. Fila responsavel: admissoes. Ticket operacional: ATD-20260331-B9DDE858. A equipe comercial valida a janela e retorna com a confirmacao.
- `crewai`: status 200, latency 193.1ms, keyword pass `True`, quality `100`, reason `workflow_visit_create`
  answer: Pedido de visita registrado para o Colegio Horizonte. Protocolo: VIS-20260331-A6E4A3. Preferencia informada: 02/04/2026 - tarde. Fila responsavel: admissoes. Ticket operacional: ATD-20260331-E1098F2F. A equipe comercial valida a janela e retorna com a confirmacao.
- `python_functions`: status 200, latency 127.9ms, keyword pass `True`, quality `100`, reason `python_functions_native_structured:support`
  answer: Pedido de visita registrado para o Colegio Horizonte. Protocolo: VIS-20260331-167873. Preferencia informada: 2026-04-02 - tarde. Fila responsavel: admissoes. Ticket operacional: ATD-20260331-B9EB1BFD. A equipe comercial valida a janela e retorna com a confirmacao.
- `llamaindex`: status 200, latency 152.8ms, keyword pass `True`, quality `100`, reason `a solicitacao pode ser executada por workflow estruturado com protocolo`
  answer: Pedido de visita registrado para o Colegio Horizonte. Protocolo: VIS-20260331-B7EF5A. Preferencia informada: 2026-04-02 - tarde. Fila responsavel: admissoes. Ticket operacional: ATD-20260331-E1D707CA. A equipe comercial valida a janela e retorna com a confirmacao.
- `specialist_supervisor`: status 200, latency 163.9ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_tool_first:visit_booking`
  answer: Pedido de visita registrado. Protocolo: VIS-20260331-554FBB. Preferencia registrada: quinta a tarde. Ticket operacional: ATD-20260331-378FAB2F. Se quiser, eu tambem posso acompanhar o status ou remarcar a visita.

### se eu precisar remarcar, como faco?

- Slice: `workflow`
- Thread: `random_workflow` turn `2`
- `langgraph`: status 200, latency 125.9ms, keyword pass `True`, quality `100`, reason `a solicitacao pode ser executada por workflow estruturado com protocolo`
  answer: Consigo remarcar a visita por aqui. Protocolo: VIS-20260331-FEC62F. Ticket operacional: ATD-20260331-B9DDE858. Me diga pelo menos o novo dia ou a janela desejada, por exemplo: "remarque para sexta de manha" ou "troque para 28/03 as 10h".
- `crewai`: status 200, latency 166.8ms, keyword pass `True`, quality `100`, reason `workflow_visit_reschedule_guidance`
  answer: Se voce precisar remarcar, me passe o protocolo VIS-20260331-A6E4A3 ou o novo horario desejado que eu sigo com essa atualizacao para a fila de admissoes.
- `python_functions`: status 200, latency 120.5ms, keyword pass `True`, quality `100`, reason `python_functions_native_structured:support`
  answer: Consigo remarcar a visita por aqui. Protocolo: VIS-20260331-167873. Ticket operacional: ATD-20260331-B9EB1BFD. Me diga pelo menos o novo dia ou a janela desejada, por exemplo: "remarque para sexta de manha" ou "troque para 28/03 as 10h".
- `llamaindex`: status 200, latency 130.1ms, keyword pass `True`, quality `100`, reason `a solicitacao pode ser executada por workflow estruturado com protocolo`
  answer: Consigo remarcar a visita por aqui. Protocolo: VIS-20260331-B7EF5A. Ticket operacional: ATD-20260331-E1D707CA. Me diga pelo menos o novo dia ou a janela desejada, por exemplo: "remarque para sexta de manha" ou "troque para 28/03 as 10h".
- `specialist_supervisor`: status 200, latency 65.2ms, keyword pass `True`, quality `100`, reason `specialist_supervisor_tool_first:visit_reschedule_guidance`
  answer: Para remarcar a visita, eu sigo pelo protocolo VIS-20260331-554FBB. A preferencia atual registrada e quinta a tarde. Me diga o novo dia ou janela desejada e eu atualizo o pedido. Ticket operacional: ATD-20260331-378FAB2F.

### ola

- Slice: `public`
- Thread: `eval:public-greeting-thread` turn `1`
- `langgraph`: status 200, latency 176.5ms, keyword pass `True`, quality `100`, reason `fato institucional canonico deve vir de fonte estruturada`
  answer: Oi. Voce esta falando com o EduAssist do Colegio Horizonte. Posso te ajudar com matricula, bolsas, descontos e visitas, turnos, horarios, calendario e rotina escolar, biblioteca, uniforme, transporte e estrutura da escola e canais oficiais, secretaria e orientacao por setor. Se sua conta estiver vinculada, eu tambem consigo consultar notas, faltas e financeiro.
- `crewai`: status 200, latency 764.0ms, keyword pass `False`, quality `80`, reason `crewai_public_fast_path`
  errors: missing_expected_keyword
  answer: Oi. Eu posso te ajudar por aqui com informacoes da escola, canais oficiais, matricula, visitas, biblioteca, atividades e rotina escolar.
- `python_functions`: status 200, latency 124.0ms, keyword pass `True`, quality `100`, reason `python_functions_native_structured:institution`
  answer: Oi. Voce esta falando com o EduAssist do Colegio Horizonte. Posso te ajudar com matricula, bolsas, descontos e visitas, turnos, horarios, calendario e rotina escolar, biblioteca, uniforme, transporte e estrutura da escola e canais oficiais, secretaria e orientacao por setor. Se sua conta estiver vinculada, eu tambem consigo consultar notas, faltas e financeiro.
- `llamaindex`: status 200, latency 126.3ms, keyword pass `True`, quality `100`, reason `llamaindex_public_profile`
  answer: Oi. Voce esta falando com o EduAssist do Colegio Horizonte. Posso te ajudar com matricula, bolsas, descontos e visitas, turnos, horarios, calendario e rotina escolar, biblioteca, uniforme, transporte e estrutura da escola e canais oficiais, secretaria e orientacao por setor. Se sua conta estiver vinculada, eu tambem consigo consultar notas, faltas e financeiro.
- `specialist_supervisor`: status 599, latency 12012.5ms, keyword pass `False`, quality `0`, reason `exception`
  errors: request_failed
  answer: 

### com quem eu falo?

- Slice: `public`
- Thread: `eval:public-identity-thread` turn `1`
- `langgraph`: status 200, latency 142.9ms, keyword pass `True`, quality `100`, reason `fato institucional canonico deve vir de fonte estruturada`
  answer: Voce esta falando com o EduAssist, o assistente institucional do Colegio Horizonte. Eu consigo te orientar por aqui, consultar informacoes da escola e abrir solicitacoes com protocolo. Se precisar, eu tambem te encaminho para secretaria, admissions, coordenacao, orientacao educacional, financeiro ou direcao.
- `crewai`: status 200, latency 11972.7ms, keyword pass `False`, quality `68`, reason `crewai_public_flow_timeout`
  errors: missing_expected_keyword, unnecessary_clarification
  answer: Para te ajudar melhor, sobre qual assunto você gostaria de falar?
- `python_functions`: status 200, latency 130.3ms, keyword pass `True`, quality `100`, reason `python_functions_native_structured:institution`
  answer: Voce esta falando com o EduAssist, o assistente institucional do Colegio Horizonte. Eu consigo te orientar por aqui, consultar informacoes da escola e abrir solicitacoes com protocolo. Se precisar, eu tambem te encaminho para secretaria, admissions, coordenacao, orientacao educacional, financeiro ou direcao.
- `llamaindex`: status 200, latency 184.3ms, keyword pass `True`, quality `100`, reason `llamaindex_public_profile`
  answer: Voce esta falando com o EduAssist, o assistente institucional do Colegio Horizonte. Eu consigo te orientar por aqui, consultar informacoes da escola e abrir solicitacoes com protocolo. Se precisar, eu tambem te encaminho para secretaria, admissions, coordenacao, orientacao educacional, financeiro ou direcao.
- `specialist_supervisor`: status 599, latency 12013.0ms, keyword pass `False`, quality `0`, reason `exception`
  errors: request_failed
  answer: 

### quais opcoes de assuntos eu tenho aqui?

- Slice: `public`
- Thread: `eval:public-capabilities-thread` turn `1`
- `langgraph`: status 200, latency 148.1ms, keyword pass `True`, quality `100`, reason `fato institucional canonico deve vir de fonte estruturada`
  answer: Eu consigo te ajudar com matricula, bolsas, descontos e visitas, turnos, horarios, calendario e rotina escolar e biblioteca, uniforme, transporte e estrutura da escola. Tambem consigo seguir com secretaria e documentos quando isso entrar no caminho. Se sua conta estiver vinculada, eu tambem posso consultar notas, faltas e o financeiro escolar. Se fizer sentido, eu ainda abro visita, protocolo ou te direciono para o setor certo.
- `crewai`: status 200, latency 11901.4ms, keyword pass `False`, quality `80`, reason `crewai_public_flow_completed`
  errors: missing_expected_keyword
  answer: Nao consegui concluir essa resposta agora pelo caminho principal configurado. Tente reformular em uma frase mais direta ou repetir em instantes.
- `python_functions`: status 200, latency 126.9ms, keyword pass `True`, quality `100`, reason `python_functions_native_structured:institution`
  answer: Eu consigo te ajudar com matricula, bolsas, descontos e visitas, turnos, horarios, calendario e rotina escolar e biblioteca, uniforme, transporte e estrutura da escola. Tambem consigo seguir com secretaria e documentos quando isso entrar no caminho. Se sua conta estiver vinculada, eu tambem posso consultar notas, faltas e o financeiro escolar. Se fizer sentido, eu ainda abro visita, protocolo ou te direciono para o setor certo.
- `llamaindex`: status 200, latency 128.6ms, keyword pass `True`, quality `100`, reason `llamaindex_public_profile`
  answer: Eu consigo te ajudar com matricula, bolsas, descontos e visitas, turnos, horarios, calendario e rotina escolar e biblioteca, uniforme, transporte e estrutura da escola. Tambem consigo seguir com secretaria e documentos quando isso entrar no caminho. Se sua conta estiver vinculada, eu tambem posso consultar notas, faltas e o financeiro escolar. Se fizer sentido, eu ainda abro visita, protocolo ou te direciono para o setor certo.
- `specialist_supervisor`: status 599, latency 12013.3ms, keyword pass `False`, quality `0`, reason `exception`
  errors: request_failed
  answer: 

### com quem eu falo sobre boletos?

- Slice: `public`
- Thread: `eval:service-routing-thread` turn `1`
- `langgraph`: status 200, latency 130.2ms, keyword pass `True`, quality `100`, reason `fato institucional canonico deve vir de fonte estruturada`
  answer: Para tratar esse assunto, o caminho mais direto e Financeiro escolar e contratos. Voce pode acionar por bot, financeiro, portal autenticado ou email institucional, e o prazo tipico e retorno em ate 1 dia util. Atende boletos, vencimentos, contratos, acordos e esclarecimentos financeiros. Se preferir, eu mesmo ja posso seguir por aqui com a solicitacao certa.
- `crewai`: status 200, latency 11906.6ms, keyword pass `False`, quality `80`, reason `crewai_public_flow_completed`
  errors: missing_expected_keyword
  answer: Nao consegui concluir essa resposta agora pelo caminho principal configurado. Tente reformular em uma frase mais direta ou repetir em instantes.
- `python_functions`: status 200, latency 139.9ms, keyword pass `True`, quality `100`, reason `python_functions_native_structured:institution`
  answer: Para tratar esse assunto, o caminho mais direto e Financeiro escolar e contratos. Voce pode acionar por bot, financeiro, portal autenticado ou email institucional, e o prazo tipico e retorno em ate 1 dia util. Atende boletos, vencimentos, contratos, acordos e esclarecimentos financeiros. Se preferir, eu mesmo ja posso seguir por aqui com a solicitacao certa.
- `llamaindex`: status 200, latency 135.7ms, keyword pass `True`, quality `100`, reason `llamaindex_public_profile`
  answer: Para tratar esse assunto, o caminho mais direto e Financeiro escolar e contratos. Voce pode acionar por bot, financeiro, portal autenticado ou email institucional, e o prazo tipico e retorno em ate 1 dia util. Atende boletos, vencimentos, contratos, acordos e esclarecimentos financeiros. Se preferir, eu mesmo ja posso seguir por aqui com a solicitacao certa.
- `specialist_supervisor`: status 599, latency 12012.7ms, keyword pass `False`, quality `0`, reason `exception`
  errors: request_failed
  answer: 

### como reporto um bullying?

- Slice: `public`
- Thread: `eval:bullying-routing-thread` turn `1`
- `langgraph`: status 200, latency 132.7ms, keyword pass `True`, quality `100`, reason `fato institucional canonico deve vir de fonte estruturada`
  answer: Para tratar esse assunto, o caminho mais direto e Orientacao educacional e acompanhamento socioemocional. Voce pode acionar por bot, orientacao educacional ou secretaria, e o prazo tipico e retorno em ate 2 dias uteis. Indicado para adaptacao escolar, convivencia, bem-estar, rotina de estudo e apoio a familias. Se preferir, eu mesmo ja posso seguir por aqui com a solicitacao certa.
- `crewai`: status 200, latency 11877.8ms, keyword pass `False`, quality `80`, reason `crewai_public_flow_completed`
  errors: missing_expected_keyword
  answer: Nao consegui concluir essa resposta agora pelo caminho principal configurado. Tente reformular em uma frase mais direta ou repetir em instantes.
- `python_functions`: status 200, latency 124.4ms, keyword pass `True`, quality `100`, reason `python_functions_native_structured:institution`
  answer: Para tratar esse assunto, o caminho mais direto e Orientacao educacional e acompanhamento socioemocional. Voce pode acionar por bot, orientacao educacional ou secretaria, e o prazo tipico e retorno em ate 2 dias uteis. Indicado para adaptacao escolar, convivencia, bem-estar, rotina de estudo e apoio a familias. Se preferir, eu mesmo ja posso seguir por aqui com a solicitacao certa.
- `llamaindex`: status 200, latency 132.4ms, keyword pass `True`, quality `100`, reason `llamaindex_public_profile`
  answer: Para tratar esse assunto, o caminho mais direto e Orientacao educacional e acompanhamento socioemocional. Voce pode acionar por bot, orientacao educacional ou secretaria, e o prazo tipico e retorno em ate 2 dias uteis. Indicado para adaptacao escolar, convivencia, bem-estar, rotina de estudo e apoio a familias. Se preferir, eu mesmo ja posso seguir por aqui com a solicitacao certa.
- `specialist_supervisor`: status 599, latency 12012.9ms, keyword pass `False`, quality `0`, reason `exception`
  errors: request_failed
  answer: 

### mas com qual contato eu devo falar

- Slice: `public`
- Thread: `eval:bullying-routing-thread` turn `2`
- `langgraph`: status 200, latency 138.9ms, keyword pass `False`, quality `80`, reason `fato institucional canonico deve vir de fonte estruturada`
  errors: missing_expected_keyword
  answer: Voce pode falar com Colegio Horizonte por estes canais oficiais:
- Secretaria: (11) 3333-4200
- Admissoes: (11) 3333-4201
- Orientacao educacional: (11) 3333-4202
- Financeiro: (11) 3333-4203
- Atendimento comercial: (11) 97500-2040
- Secretaria digital: (11) 97500-2041
- Secretaria: secretaria@colegiohorizonte.edu.br
- Admissoes: admissoes@colegiohorizonte.edu.br
- Orientacao educacional: orientacao@colegiohorizonte.edu.br
- Financeiro: financeiro@colegiohorizonte.edu.br
- Direcao: direcao@colegiohorizonte.edu.br
- Suporte digital: suporte.digital@colegiohorizonte.edu.br
- Talentos: talentos@colegiohorizonte.edu.br
- `crewai`: status 200, latency 845.0ms, keyword pass `False`, quality `80`, reason `crewai_public_fast_path`
  errors: missing_expected_keyword
  answer: Secretaria (telefone): (11) 3333-4200
- `python_functions`: status 200, latency 133.2ms, keyword pass `False`, quality `80`, reason `python_functions_native_structured:institution`
  errors: missing_expected_keyword
  answer: Voce pode falar com Colegio Horizonte por estes canais oficiais:
- Secretaria: (11) 3333-4200
- Admissoes: (11) 3333-4201
- Orientacao educacional: (11) 3333-4202
- Financeiro: (11) 3333-4203
- Atendimento comercial: (11) 97500-2040
- Secretaria digital: (11) 97500-2041
- Secretaria: secretaria@colegiohorizonte.edu.br
- Admissoes: admissoes@colegiohorizonte.edu.br
- Orientacao educacional: orientacao@colegiohorizonte.edu.br
- Financeiro: financeiro@colegiohorizonte.edu.br
- Direcao: direcao@colegiohorizonte.edu.br
- Suporte digital: suporte.digital@colegiohorizonte.edu.br
- Talentos: talentos@colegiohorizonte.edu.br
- `llamaindex`: status 200, latency 144.6ms, keyword pass `False`, quality `80`, reason `llamaindex_public_profile`
  errors: missing_expected_keyword
  answer: Voce pode falar com Colegio Horizonte por estes canais oficiais:
- Secretaria: (11) 3333-4200
- Admissoes: (11) 3333-4201
- Orientacao educacional: (11) 3333-4202
- Financeiro: (11) 3333-4203
- Atendimento comercial: (11) 97500-2040
- Secretaria digital: (11) 97500-2041
- Secretaria: secretaria@colegiohorizonte.edu.br
- Admissoes: admissoes@colegiohorizonte.edu.br
- Orientacao educacional: orientacao@colegiohorizonte.edu.br
- Financeiro: financeiro@colegiohorizonte.edu.br
- Direcao: direcao@colegiohorizonte.edu.br
- Suporte digital: suporte.digital@colegiohorizonte.edu.br
- Talentos: talentos@colegiohorizonte.edu.br
- `specialist_supervisor`: status 599, latency 12011.2ms, keyword pass `False`, quality `0`, reason `exception`
  errors: request_failed
  answer: 

### e o telefone?

- Slice: `public`
- Thread: `eval:bullying-routing-thread` turn `3`
- `langgraph`: status 200, latency 271.9ms, keyword pass `True`, quality `100`, reason `fato institucional canonico deve vir de fonte estruturada`
  answer: O telefone principal de Colegio Horizonte hoje e (11) 3333-4202, na orientacao educacional.
- `crewai`: status 200, latency 912.0ms, keyword pass `False`, quality `45`, reason `crewai_public_fast_path`
  errors: followup_context_drop, missing_expected_keyword, repetitive_reply
  answer: Secretaria (telefone): (11) 3333-4200
- `python_functions`: status 200, latency 163.1ms, keyword pass `True`, quality `100`, reason `python_functions_native_structured:institution`
  answer: O telefone principal de Colegio Horizonte hoje e (11) 3333-4202, na orientacao educacional.
- `llamaindex`: status 200, latency 163.9ms, keyword pass `True`, quality `100`, reason `llamaindex_public_profile`
  answer: O telefone principal de Colegio Horizonte hoje e (11) 3333-4202, na orientacao educacional.
- `specialist_supervisor`: status 200, latency 5454.9ms, keyword pass `False`, quality `68`, reason `A solicitação do usuário 'e o telefone?' é ambígua. Com base no contexto recente sobre 'reporte de bullying' e no output do turno anterior que incluía 'navegação de atendimento e orientação de concierge', é provável que o usuário esteja buscando um telefone de contato institucional. É necessária uma clarificação para entender a finalidade específica do telefone desejado.`
  errors: missing_expected_keyword, unnecessary_clarification
  answer: Você gostaria do telefone para qual finalidade? Para reportar bullying, para contato geral com a instituição ou para outro assunto?

### quais documentos sao exigidos para matricula?

- Slice: `public`
- Thread: `ext:public_faq_admissions` turn `1`
- `langgraph`: status 200, latency 1985.3ms, keyword pass `True`, quality `100`, reason `retrieval hibrido e o caminho padrao para faq e documentos`
  answer: Segundo a base institucional atual:
- Sao exigidos documento de identidade do aluno, CPF quando houver, historico escolar, comprovante de residencia atualizado, documento de identificacao do responsavel legal e formulario cadastral preenchido. Casos de transferencia podem exigir declaracao adicional da escola de o...
- O processo de matricula do ensino fundamental II e do ensino medio exige ficha cadastral, documento de identificacao do aluno, documento do responsavel legal, historico escolar e comprovante de residencia. A confirmacao da vaga depende de analise documental e assinatura do con...
Fontes:
- Manual de Matricula do Ensino Medio (v2026.2)
- FAQ Institucional do Colegio Horizonte (v2026.2)
- Tecnologia e Canais Digitais (v2026.2)
- `crewai`: status 200, latency 187.8ms, keyword pass `False`, quality `80`, reason `crewai_protected_auth_required`
  errors: missing_expected_keyword
  answer: Essa consulta depende de autenticacao e vinculo da sua conta no Telegram. Use o portal da escola para gerar o codigo de vinculacao e depois envie o comando /start link_<codigo> ao bot.
- `python_functions`: status 200, latency 902.1ms, keyword pass `True`, quality `100`, reason `python_functions_native_public_retrieval`
  answer: Segundo a base institucional atual:
- Sao exigidos documento de identidade do aluno, CPF quando houver, historico escolar, comprovante de residencia atualizado, documento de identificacao do responsavel legal e formulario cadastral preenchido. Casos de transferencia podem exigir declaracao adicional da escola de o...
- O processo de matricula do ensino fundamental II e do ensino medio exige ficha cadastral, documento de identificacao do aluno, documento do responsavel legal, historico escolar e comprovante de residencia. A confirmacao da vaga depende de analise documental e assinatura do con...
Fontes:
- Manual de Matricula do Ensino Medio (v2026.2)
- FAQ Institucional do Colegio Horizonte (v2026.2)
- Tecnologia e Canais Digitais (v2026.2)
- `llamaindex`: status 200, latency 1264.3ms, keyword pass `True`, quality `100`, reason `llamaindex_public_profile`
  answer: Hoje os documentos exigidos para a matricula publicados pela escola sao:
- Formulario cadastral preenchido
- Documento de identificacao do aluno
- CPF do aluno, quando houver
- Historico escolar
- Comprovante de residencia atualizado
- Documento de identificacao do responsavel legal
Se quiser, eu tambem posso explicar as etapas da matricula ou como funciona o envio inicial desses documentos.
- `specialist_supervisor`: status 599, latency 12014.0ms, keyword pass `False`, quality `0`, reason `exception`
  errors: request_failed
  answer: 

### qual o telefone e o fax?

- Slice: `public`
- Thread: `ext:public_phone_and_fax_multi_attribute` turn `1`
- `langgraph`: status 200, latency 143.8ms, keyword pass `False`, quality `80`, reason `fato institucional canonico deve vir de fonte estruturada`
  errors: missing_expected_keyword
  answer: Hoje a escola nao utiliza fax. Para entrar em contato por telefone, o numero da secretaria e (11) 3333-4200.
- `crewai`: status 200, latency 999.0ms, keyword pass `False`, quality `80`, reason `crewai_public_fast_path`
  errors: missing_expected_keyword
  answer: Secretaria (telefone): (11) 3333-4200 Hoje a escola nao utiliza fax institucional.
- `python_functions`: status 200, latency 139.7ms, keyword pass `False`, quality `80`, reason `python_functions_native_structured:institution`
  errors: missing_expected_keyword
  answer: Hoje a escola nao utiliza fax. Para entrar em contato por telefone, o numero da secretaria e (11) 3333-4200.
- `llamaindex`: status 200, latency 148.2ms, keyword pass `False`, quality `80`, reason `llamaindex_public_profile`
  errors: missing_expected_keyword
  answer: Hoje a escola nao utiliza fax. Para entrar em contato por telefone, o numero da secretaria e (11) 3333-4200.
- `specialist_supervisor`: status 599, latency 12012.6ms, keyword pass `False`, quality `0`, reason `exception`
  errors: request_failed
  answer: 

### qual site do colegio?

- Slice: `public`
- Thread: `ext:public_school_website` turn `1`
- `langgraph`: status 200, latency 159.4ms, keyword pass `True`, quality `100`, reason `fato institucional canonico deve vir de fonte estruturada`
  answer: O site oficial de Colegio Horizonte hoje e https://www.colegiohorizonte.edu.br.
- `crewai`: status 599, latency 12000.5ms, keyword pass `False`, quality `0`, reason `exception`
  errors: request_failed
  answer: 
- `python_functions`: status 200, latency 185.4ms, keyword pass `True`, quality `100`, reason `python_functions_native_structured:institution`
  answer: O site oficial de Colegio Horizonte hoje e https://www.colegiohorizonte.edu.br.
- `llamaindex`: status 200, latency 163.5ms, keyword pass `True`, quality `100`, reason `llamaindex_public_profile`
  answer: O site oficial de Colegio Horizonte hoje e https://www.colegiohorizonte.edu.br.
- `specialist_supervisor`: status 200, latency 10921.3ms, keyword pass `True`, quality `100`, reason `The manager's draft provides a specific website, but the 'specialist_results' array is empty. This indicates that the information was not retrieved or verified by any specialist, making the answer ungrounded. Therefore, the answer cannot be approved.`
  answer: O site do Colégio Horizonte é https://www.colegiohorizonte.edu.br.

### quando e a reuniao de pais?

- Slice: `public`
- Thread: `eval:calendar-event-thread` turn `1`
- `langgraph`: status 200, latency 189.5ms, keyword pass `False`, quality `80`, reason `datas institucionais publicas devem vir de leitura estruturada e auditavel`
  errors: missing_expected_keyword
  answer: Feira de orientacao academica e vocacional: 06/06/2026 às 09h00 até 12h00. Encontro com responsaveis e estudantes sobre trajetorias no Ensino Medio.
- `crewai`: status 200, latency 11911.3ms, keyword pass `False`, quality `80`, reason `crewai_public_flow_completed`
  errors: missing_expected_keyword
  answer: Nao consegui concluir essa resposta agora pelo caminho principal configurado. Tente reformular em uma frase mais direta ou repetir em instantes.
- `python_functions`: status 200, latency 152.9ms, keyword pass `False`, quality `80`, reason `python_functions_native_structured:calendar`
  errors: missing_expected_keyword
  answer: Feira de orientacao academica e vocacional: 06/06/2026 às 09h00 até 12h00. Encontro com responsaveis e estudantes sobre trajetorias no Ensino Medio.
- `llamaindex`: status 200, latency 161.3ms, keyword pass `False`, quality `80`, reason `llamaindex_public_profile`
  errors: missing_expected_keyword
  answer: Feira de orientacao academica e vocacional: 06/06/2026 às 09h00 até 12h00. Encontro com responsaveis e estudantes sobre trajetorias no Ensino Medio.
- `specialist_supervisor`: status 599, latency 12012.7ms, keyword pass `False`, quality `0`, reason `exception`
  errors: request_failed
  answer: 

### qual o nome da diretora?

- Slice: `public`
- Thread: `ext:public_director_name` turn `1`
- `langgraph`: status 200, latency 213.8ms, keyword pass `True`, quality `100`, reason `fato institucional canonico deve vir de fonte estruturada`
  answer: Diretora geral: Helena Martins.
- `crewai`: status 599, latency 12013.0ms, keyword pass `False`, quality `0`, reason `exception`
  errors: request_failed
  answer: 
- `python_functions`: status 200, latency 150.3ms, keyword pass `True`, quality `100`, reason `python_functions_native_structured:institution`
  answer: Diretora geral: Helena Martins.
- `llamaindex`: status 200, latency 162.3ms, keyword pass `True`, quality `100`, reason `llamaindex_public_profile`
  answer: Diretora geral: Helena Martins.
- `specialist_supervisor`: status 599, latency 12013.4ms, keyword pass `False`, quality `0`, reason `exception`
  errors: request_failed
  answer: 

### qual o nome da diretora?

- Slice: `public`
- Thread: `eval:leadership-followup-thread` turn `1`
- `langgraph`: status 200, latency 235.0ms, keyword pass `True`, quality `100`, reason `fato institucional canonico deve vir de fonte estruturada`
  answer: Diretora geral: Helena Martins.
- `crewai`: status 599, latency 12013.5ms, keyword pass `False`, quality `0`, reason `exception`
  errors: request_failed
  answer: 
- `python_functions`: status 200, latency 171.5ms, keyword pass `True`, quality `100`, reason `python_functions_native_structured:institution`
  answer: Diretora geral: Helena Martins.
- `llamaindex`: status 200, latency 168.4ms, keyword pass `True`, quality `100`, reason `llamaindex_public_profile`
  answer: Diretora geral: Helena Martins.
- `specialist_supervisor`: status 599, latency 12013.1ms, keyword pass `False`, quality `0`, reason `exception`
  errors: request_failed
  answer: 

### e o email?

- Slice: `public`
- Thread: `eval:leadership-followup-thread` turn `2`
- `langgraph`: status 200, latency 175.6ms, keyword pass `True`, quality `100`, reason `fato institucional canonico deve vir de fonte estruturada`
  answer: O email mais direto de Colegio Horizonte hoje e direcao@colegiohorizonte.edu.br, pela direcao.
- `crewai`: status 200, latency 1028.8ms, keyword pass `False`, quality `80`, reason `crewai_public_fast_path`
  errors: missing_expected_keyword
  answer: O nome desse espaco e Biblioteca Aurora.
- `python_functions`: status 200, latency 164.6ms, keyword pass `True`, quality `100`, reason `python_functions_native_structured:institution`
  answer: O email mais direto de Colegio Horizonte hoje e direcao@colegiohorizonte.edu.br, pela direcao.
- `llamaindex`: status 200, latency 188.4ms, keyword pass `True`, quality `100`, reason `llamaindex_public_profile`
  answer: O email mais direto de Colegio Horizonte hoje e direcao@colegiohorizonte.edu.br, pela direcao.
- `specialist_supervisor`: status 599, latency 12013.4ms, keyword pass `False`, quality `0`, reason `exception`
  errors: request_failed
  answer: 

### qual a media de aprovacao?

- Slice: `public`
- Thread: `ext:public_approval_kpi` turn `1`
- `langgraph`: status 200, latency 154.8ms, keyword pass `True`, quality `100`, reason `fato institucional canonico deve vir de fonte estruturada`
  answer: Os indicadores publicos mais recentes de Colegio Horizonte sao:
- Aprovacao global: 96.4% (ano letivo 2025)
- Frequencia media: 97.1% (ano letivo 2025)
- Familias que avaliaram o atendimento como bom ou excelente: 92.0% (pesquisa institucional 2025)
- `crewai`: status 200, latency 11998.8ms, keyword pass `False`, quality `80`, reason `crewai_public_flow_completed`
  errors: missing_expected_keyword
  answer: Nao consegui concluir essa resposta agora pelo caminho principal configurado. Tente reformular em uma frase mais direta ou repetir em instantes.
- `python_functions`: status 200, latency 213.2ms, keyword pass `True`, quality `100`, reason `python_functions_native_structured:institution`
  answer: Os indicadores publicos mais recentes de Colegio Horizonte sao:
- Aprovacao global: 96.4% (ano letivo 2025)
- Frequencia media: 97.1% (ano letivo 2025)
- Familias que avaliaram o atendimento como bom ou excelente: 92.0% (pesquisa institucional 2025)
- `llamaindex`: status 200, latency 214.2ms, keyword pass `False`, quality `80`, reason `llamaindex_public_pricing_projection`
  errors: missing_expected_keyword
  answer: Valores publicos de referencia para 2026:
- Ensino Fundamental II (Manha): mensalidade R$ 1.280,00 e taxa de matricula R$ 350,00. Valor comercial publico de referencia para 2026. Material didatico e uniforme sao cobrados a parte.
- Ensino Medio (Manha): mensalidade R$ 1.450,00 e taxa de matricula R$ 350,00. Valor comercial publico de referencia para 2026. Ha politica comercial para irmaos e pagamento pontual.
- Periodo integral opcional (Complemento contraturno): mensalidade R$ 480,00 e taxa de matricula R$ 0,00. Adicional mensal aplicado ao estudante matriculado no turno regular que aderir ao periodo integral.
Se quiser, eu tambem posso resumir bolsas, descontos comerciais e canais de matricula.
- `specialist_supervisor`: status 599, latency 12007.8ms, keyword pass `False`, quality `0`, reason `exception`
  errors: request_failed
  answer: 

### quais documentos nao preciso para a matricula?

- Slice: `public`
- Thread: `ext:public_negative_requirements_abstention` turn `1`
- `langgraph`: status 200, latency 948.2ms, keyword pass `True`, quality `100`, reason `retrieval hibrido e o caminho padrao para faq e documentos`
  answer: A base atual informa os documentos exigidos para a matricula, mas nao lista explicitamente quais documentos sao dispensaveis.
Por isso, nao e seguro afirmar o que voce "nao precisa" levar.
O que esta explicitamente exigido hoje e:
- ficha cadastral ou formulario cadastral preenchido
- documento de identificacao do aluno
- CPF do aluno, quando houver
- historico escolar
- comprovante de residencia
- documento de identificacao do responsavel legal
Se quiser, eu posso resumir apenas os documentos exigidos ou explicar as etapas da matricula.

Fontes:
- Tecnologia e Canais Digitais (v2026.2)
- Manual de Matricula do Ensino Medio (v2026.2)
- FAQ Institucional do Colegio Horizonte (v2026.2)
- `crewai`: status 200, latency 196.9ms, keyword pass `False`, quality `80`, reason `crewai_protected_auth_required`
  errors: missing_expected_keyword
  answer: Essa consulta depende de autenticacao e vinculo da sua conta no Telegram. Use o portal da escola para gerar o codigo de vinculacao e depois envie o comando /start link_<codigo> ao bot.
- `python_functions`: status 200, latency 846.2ms, keyword pass `False`, quality `80`, reason `python_functions_native_public_retrieval`
  errors: missing_expected_keyword
  answer: Segundo a base institucional atual:
- Para triagem documental de matricula ou orientacoes administrativas, a escola aceita envio inicial pelo portal institucional e pelo email da secretaria. O bot aberto nao deve receber documentos completos, dados sensiveis ou arquivos que dependam de validacao autenticada.
- Sao exigidos documento de identidade do aluno, CPF quando houver, historico escolar, comprovante de residencia atualizado, documento de identificacao do responsavel legal e formulario cadastral preenchido. Casos de transferencia podem exigir declaracao adicional da escola de o...
Fontes:
- Tecnologia e Canais Digitais (v2026.2)
- Manual de Matricula do Ensino Medio (v2026.2)
- FAQ Institucional do Colegio Horizonte (v2026.2)
- `llamaindex`: status 200, latency 229.1ms, keyword pass `False`, quality `80`, reason `llamaindex_public_profile`
  errors: missing_expected_keyword
  answer: Hoje os documentos exigidos para a matricula publicados pela escola sao:
- Formulario cadastral preenchido
- Documento de identificacao do aluno
- CPF do aluno, quando houver
- Historico escolar
- Comprovante de residencia atualizado
- Documento de identificacao do responsavel legal
Se quiser, eu tambem posso explicar as etapas da matricula ou como funciona o envio inicial desses documentos.
- `specialist_supervisor`: status 599, latency 12001.9ms, keyword pass `False`, quality `0`, reason `exception`
  errors: request_failed
  answer: 

### e uma escola confessional?

- Slice: `public`
- Thread: `ext:public_confessional_gap` turn `1`
- `langgraph`: status 200, latency 125.5ms, keyword pass `False`, quality `80`, reason `fato institucional canonico deve vir de fonte estruturada`
  errors: missing_expected_keyword
  answer: Aqui e o Colegio Horizonte. Se voce esta procurando o Confessional, eu nao tenho acesso ao atendimento dessa outra instituicao. Se quiser, sigo te ajudando com o Colegio Horizonte por aqui.
- `crewai`: status 599, latency 12003.6ms, keyword pass `False`, quality `0`, reason `exception`
  errors: request_failed
  answer: 
- `python_functions`: status 200, latency 142.0ms, keyword pass `True`, quality `100`, reason `python_functions_native_structured:institution`
  answer: Colegio Horizonte e uma escola laica. A proposta institucional e plural e nao confessional.
- `llamaindex`: status 200, latency 160.9ms, keyword pass `True`, quality `100`, reason `llamaindex_public_profile`
  answer: Colegio Horizonte e uma escola laica. A proposta institucional e plural e nao confessional.
- `specialist_supervisor`: status 599, latency 12012.9ms, keyword pass `False`, quality `0`, reason `exception`
  errors: request_failed
  answer: 

### bom dia

- Slice: `public`
- Thread: `eval:public-structure-after-greeting-thread` turn `1`
- `langgraph`: status 200, latency 213.5ms, keyword pass `True`, quality `100`, reason `fato institucional canonico deve vir de fonte estruturada`
  answer: Bom dia. Voce esta falando com o EduAssist do Colegio Horizonte. Posso te ajudar com matricula, bolsas, descontos e visitas, turnos, horarios, calendario e rotina escolar, biblioteca, uniforme, transporte e estrutura da escola e canais oficiais, secretaria e orientacao por setor. Se sua conta estiver vinculada, eu tambem consigo consultar notas, faltas e financeiro.
- `crewai`: status 200, latency 1036.1ms, keyword pass `False`, quality `80`, reason `crewai_public_fast_path`
  errors: missing_expected_keyword
  answer: Oi. Eu posso te ajudar por aqui com informacoes da escola, canais oficiais, matricula, visitas, biblioteca, atividades e rotina escolar.
- `python_functions`: status 200, latency 160.9ms, keyword pass `True`, quality `100`, reason `python_functions_native_structured:institution`
  answer: Bom dia. Voce esta falando com o EduAssist do Colegio Horizonte. Posso te ajudar com matricula, bolsas, descontos e visitas, turnos, horarios, calendario e rotina escolar, biblioteca, uniforme, transporte e estrutura da escola e canais oficiais, secretaria e orientacao por setor. Se sua conta estiver vinculada, eu tambem consigo consultar notas, faltas e financeiro.
- `llamaindex`: status 200, latency 165.7ms, keyword pass `True`, quality `100`, reason `llamaindex_public_profile`
  answer: Bom dia. Voce esta falando com o EduAssist do Colegio Horizonte. Posso te ajudar com matricula, bolsas, descontos e visitas, turnos, horarios, calendario e rotina escolar, biblioteca, uniforme, transporte e estrutura da escola e canais oficiais, secretaria e orientacao por setor. Se sua conta estiver vinculada, eu tambem consigo consultar notas, faltas e financeiro.
- `specialist_supervisor`: status 200, latency 7227.2ms, keyword pass `False`, quality `68`, reason `A resposta do gerente é apropriada e completa para uma saudação simples. Não há necessidade de revisão ou clarificação. As respostas sugeridas são relevantes para um contexto institucional.`
  errors: missing_expected_keyword, unnecessary_clarification
  answer: Bom dia! Como posso ajudar você hoje?

### qual a estrutura da escola?

- Slice: `public`
- Thread: `eval:public-structure-after-greeting-thread` turn `2`
- `langgraph`: status 200, latency 178.4ms, keyword pass `True`, quality `100`, reason `fato institucional canonico deve vir de fonte estruturada`
  answer: Hoje, a estrutura do Colegio Horizonte inclui atividades e espacos como biblioteca aurora, espaco maker, quadra poliesportiva coberta, futsal e treinos esportivos, volei escolar. Se quiser, eu posso te detalhar qualquer um deles.
- `crewai`: status 200, latency 12103.7ms, keyword pass `False`, quality `80`, reason `crewai_public_flow_completed`
  errors: missing_expected_keyword
  answer: Nao consegui concluir essa resposta agora pelo caminho principal configurado. Tente reformular em uma frase mais direta ou repetir em instantes.
- `python_functions`: status 200, latency 157.1ms, keyword pass `True`, quality `100`, reason `python_functions_native_structured:institution`
  answer: Hoje, a estrutura do Colegio Horizonte inclui atividades e espacos como biblioteca aurora, espaco maker, quadra poliesportiva coberta, futsal e treinos esportivos, volei escolar. Se quiser, eu posso te detalhar qualquer um deles.
- `llamaindex`: status 200, latency 182.0ms, keyword pass `True`, quality `100`, reason `llamaindex_public_profile`
  answer: Hoje, a estrutura do Colegio Horizonte inclui atividades e espacos como biblioteca aurora, espaco maker, quadra poliesportiva coberta, futsal e treinos esportivos, volei escolar. Se quiser, eu posso te detalhar qualquer um deles.
- `specialist_supervisor`: status 599, latency 12013.4ms, keyword pass `False`, quality `0`, reason `exception`
  errors: request_failed
  answer: 

### qual meu acesso? a que dados

- Slice: `protected`
- Thread: `eval:guardian-access-scope-thread` turn `1`
- `langgraph`: status 200, latency 106.7ms, keyword pass `True`, quality `100`, reason `capacidade da conta autenticada e alunos vinculados exigem leitura protegida e minimizada`
  answer: Voce ja esta autenticado por aqui e sua conta esta vinculada a Lucas Oliveira e Ana Oliveira. Por este canal eu consigo consultar notas, faltas, proximas provas, matricula, financeiro, boletos, dentro das permissoes dessa vinculacao. Se quiser, me diga algo como "notas do Lucas", "faltas da Ana" ou "financeiro do Lucas".
- `crewai`: status 200, latency 179.4ms, keyword pass `True`, quality `100`, reason `crewai_protected_identity_backstop`
  answer: Voce esta autenticado aqui como Maria Oliveira. Sua conta esta vinculada a Lucas Oliveira, Ana Oliveira e pode consultar notas, frequencia, avaliacoes, documentacao e financeiro desses alunos.
- `python_functions`: status 200, latency 105.2ms, keyword pass `True`, quality `100`, reason `python_functions_native_structured:institution`
  answer: Voce ja esta autenticado por aqui e sua conta esta vinculada a Lucas Oliveira e Ana Oliveira. Por este canal eu consigo consultar notas, faltas, proximas provas, matricula, financeiro, boletos, dentro das permissoes dessa vinculacao. Se quiser, me diga algo como "notas do Lucas", "faltas da Ana" ou "financeiro do Lucas".
- `llamaindex`: status 200, latency 114.1ms, keyword pass `True`, quality `100`, reason `capacidade da conta autenticada e alunos vinculados exigem leitura protegida e minimizada`
  answer: Voce ja esta autenticado por aqui e sua conta esta vinculada a Lucas Oliveira e Ana Oliveira. Por este canal eu consigo consultar notas, faltas, proximas provas, matricula, financeiro, boletos, dentro das permissoes dessa vinculacao. Se quiser, me diga algo como "notas do Lucas", "faltas da Ana" ou "financeiro do Lucas".
- `specialist_supervisor`: status 599, latency 12012.3ms, keyword pass `False`, quality `0`, reason `exception`
  errors: request_failed
  answer: 

### estou logado como?

- Slice: `protected`
- Thread: `eval:guardian-actor-identity-thread` turn `1`
- `langgraph`: status 200, latency 105.2ms, keyword pass `True`, quality `100`, reason `identidade da conta autenticada exige leitura protegida e minimizada`
  answer: Voce esta falando aqui como Maria Oliveira, no perfil de responsavel. Sua conta esta vinculada a Lucas Oliveira e Ana Oliveira. Por aqui eu consigo consultar notas, faltas, proximas provas, matricula, financeiro, boletos, dentro das permissoes dessa vinculacao.
- `crewai`: status 200, latency 176.8ms, keyword pass `True`, quality `100`, reason `crewai_protected_identity_backstop`
  answer: Voce esta autenticado aqui como Maria Oliveira. Sua conta esta vinculada a Lucas Oliveira, Ana Oliveira e pode consultar notas, frequencia, avaliacoes, documentacao e financeiro desses alunos.
- `python_functions`: status 200, latency 102.4ms, keyword pass `True`, quality `100`, reason `python_functions_native_structured:institution`
  answer: Voce esta falando aqui como Maria Oliveira, no perfil de responsavel. Sua conta esta vinculada a Lucas Oliveira e Ana Oliveira. Por aqui eu consigo consultar notas, faltas, proximas provas, matricula, financeiro, boletos, dentro das permissoes dessa vinculacao.
- `llamaindex`: status 200, latency 112.5ms, keyword pass `True`, quality `100`, reason `identidade da conta autenticada exige leitura protegida e minimizada`
  answer: Voce esta falando aqui como Maria Oliveira, no perfil de responsavel. Sua conta esta vinculada a Lucas Oliveira e Ana Oliveira. Por aqui eu consigo consultar notas, faltas, proximas provas, matricula, financeiro, boletos, dentro das permissoes dessa vinculacao.
- `specialist_supervisor`: status 599, latency 12003.5ms, keyword pass `False`, quality `0`, reason `exception`
  errors: request_failed
  answer: 

### quero ver as notas do Lucas Oliveira

- Slice: `protected`
- Thread: `eval:guardian-lucas-thread` turn `1`
- `langgraph`: status 200, latency 191.7ms, keyword pass `False`, quality `80`, reason `dados estruturados devem passar por service deterministico`
  errors: missing_expected_keyword
  answer: Notas de Lucas Oliveira:
- Biologia - Avaliacao B1: 8.40/10.00
- Educacao Fisica - Avaliacao 2026-B1 - EF: 6.40/10.00
- Filosofia - Avaliacao 2026-B1 - FIL: 7.00/10.00
- Fisica - Avaliacao 2026-B1 - FIS: 5.80/10.00
- Geografia - Avaliacao 2026-B1 - GEO: 6.40/10.00
- Historia - Avaliacao 2026-B1 - HIS: 6.70/10.00
- Ingles - Avaliacao B1: 8.90/10.00
- Matematica - Avaliacao B1: 8.70/10.00
- `crewai`: status 200, latency 461.0ms, keyword pass `False`, quality `80`, reason `crewai_protected_fast_path`
  errors: missing_expected_keyword
  answer: As notas mais recentes de Lucas Oliveira incluem Biologia: 8.40/10.00; Educacao Fisica: 6.40/10.00; Filosofia: 7.00/10.00; Fisica: 5.80/10.00; Geografia: 6.40/10.00; Historia: 6.70/10.00; Ingles: 8.90/10.00; Matematica: 8.70/10.00.
- `python_functions`: status 200, latency 184.9ms, keyword pass `False`, quality `80`, reason `python_functions_native_structured:academic`
  errors: missing_expected_keyword
  answer: Notas de Lucas Oliveira:
- Biologia - Avaliacao B1: 8.40/10.00
- Educacao Fisica - Avaliacao 2026-B1 - EF: 6.40/10.00
- Filosofia - Avaliacao 2026-B1 - FIL: 7.00/10.00
- Fisica - Avaliacao 2026-B1 - FIS: 5.80/10.00
- Geografia - Avaliacao 2026-B1 - GEO: 6.40/10.00
- Historia - Avaliacao 2026-B1 - HIS: 6.70/10.00
- Ingles - Avaliacao B1: 8.90/10.00
- Matematica - Avaliacao B1: 8.70/10.00
- `llamaindex`: status 200, latency 213.1ms, keyword pass `False`, quality `80`, reason `dados estruturados devem passar por service deterministico`
  errors: missing_expected_keyword
  answer: Notas de Lucas Oliveira:
- Biologia - Avaliacao B1: 8.40/10.00
- Educacao Fisica - Avaliacao 2026-B1 - EF: 6.40/10.00
- Filosofia - Avaliacao 2026-B1 - FIL: 7.00/10.00
- Fisica - Avaliacao 2026-B1 - FIS: 5.80/10.00
- Geografia - Avaliacao 2026-B1 - GEO: 6.40/10.00
- Historia - Avaliacao 2026-B1 - HIS: 6.70/10.00
- Ingles - Avaliacao B1: 8.90/10.00
- Matematica - Avaliacao B1: 8.70/10.00
- `specialist_supervisor`: status 200, latency 145.7ms, keyword pass `False`, quality `80`, reason `specialist_supervisor_tool_first:academic_summary`
  errors: missing_expected_keyword
  answer: Notas de Lucas Oliveira:
- Fisica: media parcial 5,9
- Matematica: media parcial 7,7
- Portugues: media parcial 8,3

### e a frequencia?

- Slice: `protected`
- Thread: `eval:guardian-lucas-thread` turn `2`
- `langgraph`: status 200, latency 141.5ms, keyword pass `False`, quality `55`, reason `dados estruturados devem passar por service deterministico`
  errors: followup_context_drop, missing_expected_keyword
  answer: Hoje eu nao encontrei Frequencia entre os alunos vinculados a esta conta. No momento, os alunos que aparecem aqui sao: Lucas Oliveira (MAT-2026-001), Ana Oliveira (MAT-2026-002). Se quiser, me diga qual deles voce quer consultar.
- `crewai`: status 200, latency 488.4ms, keyword pass `False`, quality `55`, reason `crewai_protected_fast_path`
  errors: followup_context_drop, missing_expected_keyword
  answer: Na frequencia de Lucas Oliveira, eu encontrei 12 registro(s) neste recorte: 6 presenca(s), 3 falta(s) e 3 atraso(s).
- `python_functions`: status 200, latency 136.2ms, keyword pass `False`, quality `55`, reason `python_functions_native_structured:academic`
  errors: followup_context_drop, missing_expected_keyword
  answer: Hoje eu nao encontrei Frequencia entre os alunos vinculados a esta conta. No momento, os alunos que aparecem aqui sao: Lucas Oliveira (MAT-2026-001), Ana Oliveira (MAT-2026-002). Se quiser, me diga qual deles voce quer consultar.
- `llamaindex`: status 200, latency 142.0ms, keyword pass `False`, quality `55`, reason `dados estruturados devem passar por service deterministico`
  errors: followup_context_drop, missing_expected_keyword
  answer: Hoje eu nao encontrei Frequencia entre os alunos vinculados a esta conta. No momento, os alunos que aparecem aqui sao: Lucas Oliveira (MAT-2026-001), Ana Oliveira (MAT-2026-002). Se quiser, me diga qual deles voce quer consultar.
- `specialist_supervisor`: status 200, latency 157.2ms, keyword pass `False`, quality `55`, reason `specialist_supervisor_tool_first:academic_summary_aggregate`
  errors: followup_context_drop, missing_expected_keyword
  answer: Panorama academico das contas vinculadas:
- Lucas Oliveira: Fisica 5,9; Matematica 7,7; Portugues 8,3
- Ana Oliveira: Fisica 6,4; Matematica 7,4; Portugues 8,4

### quero ver o financeiro da Ana Oliveira

- Slice: `protected`
- Thread: `ext:guardian_finance_student_summary` turn `1`
- `langgraph`: status 200, latency 170.6ms, keyword pass `True`, quality `100`, reason `dados estruturados devem passar por service deterministico`
  answer: Resumo financeiro de Ana Oliveira:
- Contrato: CTR-2026-002
- Responsavel financeiro: Maria Oliveira
- Mensalidade base: 1450.00
- Faturas em aberto: 1
- Faturas vencidas: 0
Ultimas faturas:
- 2026-03: vencimento 2026-03-10, status em aberto, valor 1450.00
- `crewai`: status 200, latency 247.0ms, keyword pass `False`, quality `80`, reason `support_handoff_created`
  errors: missing_expected_keyword
  answer: Encaminhei sua solicitacao para a fila de financeiro. Protocolo: ATD-20260331-34857610. Status atual: queued. A equipe humana podera continuar esse atendimento no portal operacional.
- `python_functions`: status 200, latency 181.0ms, keyword pass `True`, quality `100`, reason `python_functions_native_structured:finance`
  answer: Resumo financeiro de Ana Oliveira:
- Contrato: CTR-2026-002
- Responsavel financeiro: Maria Oliveira
- Mensalidade base: 1450.00
- Faturas em aberto: 1
- Faturas vencidas: 0
Ultimas faturas:
- 2026-03: vencimento 2026-03-10, status em aberto, valor 1450.00
- `llamaindex`: status 200, latency 173.5ms, keyword pass `True`, quality `100`, reason `dados estruturados devem passar por service deterministico`
  answer: Resumo financeiro de Ana Oliveira:
- Contrato: CTR-2026-002
- Responsavel financeiro: Maria Oliveira
- Mensalidade base: 1450.00
- Faturas em aberto: 1
- Faturas vencidas: 0
Ultimas faturas:
- 2026-03: vencimento 2026-03-10, status em aberto, valor 1450.00
- `specialist_supervisor`: status 200, latency 109.7ms, keyword pass `False`, quality `80`, reason `specialist_supervisor_tool_first:financial_summary`
  errors: missing_expected_keyword
  answer: Resumo financeiro das contas vinculadas:
- Total de faturas em aberto: 1
- Total de faturas vencidas: 0
- Ana Oliveira: 1 em aberto, 0 vencidas
  2026-03: vencimento 2026-03-10, status open, valor 1450.00

### tenho boletos atrasados?

- Slice: `protected`
- Thread: `eval:guardian-finance-status-thread` turn `1`
- `langgraph`: status 200, latency 238.6ms, keyword pass `True`, quality `100`, reason `dados estruturados devem passar por service deterministico`
  answer: Resumo financeiro das contas vinculadas:
- Total de faturas em aberto: 1
- Total de faturas vencidas: 0
- Lucas Oliveira: 0 em aberto, 0 vencidas
- Ana Oliveira: 1 em aberto, 0 vencidas
- Hoje nao ha faturas vencidas neste recorte.
- `crewai`: status 599, latency 12001.3ms, keyword pass `False`, quality `0`, reason `exception`
  errors: request_failed
  answer: 
- `python_functions`: status 200, latency 208.0ms, keyword pass `True`, quality `100`, reason `python_functions_native_structured:finance`
  answer: Resumo financeiro das contas vinculadas:
- Total de faturas em aberto: 1
- Total de faturas vencidas: 0
- Lucas Oliveira: 0 em aberto, 0 vencidas
- Ana Oliveira: 1 em aberto, 0 vencidas
- Hoje nao ha faturas vencidas neste recorte.
- `llamaindex`: status 200, latency 224.5ms, keyword pass `True`, quality `100`, reason `dados estruturados devem passar por service deterministico`
  answer: Resumo financeiro das contas vinculadas:
- Total de faturas em aberto: 1
- Total de faturas vencidas: 0
- Lucas Oliveira: 0 em aberto, 0 vencidas
- Ana Oliveira: 1 em aberto, 0 vencidas
- Hoje nao ha faturas vencidas neste recorte.
- `specialist_supervisor`: status 200, latency 146.1ms, keyword pass `False`, quality `80`, reason `specialist_supervisor_tool_first:financial_summary_aggregate`
  errors: missing_expected_keyword
  answer: Resumo financeiro das contas vinculadas:
- Total de faturas em aberto: 1
- Total de faturas vencidas: 0
- Lucas Oliveira: 0 em aberto, 0 vencidas
  2026-03: vencimento 2026-03-10, status paid, valor 1450.00
- Ana Oliveira: 1 em aberto, 0 vencidas
  2026-03: vencimento 2026-03-10, status open, valor 1450.00

### preciso da segunda via do boleto da Ana Oliveira

- Slice: `protected`
- Thread: `eval:guardian-finance-identifier-thread` turn `1`
- `langgraph`: status 200, latency 129.5ms, keyword pass `False`, quality `80`, reason `dados estruturados devem passar por service deterministico`
  errors: missing_expected_keyword
  answer: Hoje eu nao encontrei Segunda Via entre os alunos vinculados a esta conta. No momento, os alunos que aparecem aqui sao: Lucas Oliveira (MAT-2026-001), Ana Oliveira (MAT-2026-002). Se quiser, me diga qual deles voce quer consultar.
- `crewai`: status 200, latency 413.9ms, keyword pass `False`, quality `80`, reason `crewai_protected_fast_path`
  errors: missing_expected_keyword
  answer: No financeiro de Ana Oliveira, a mensalidade de referencia e 1450.00 e ha 1 fatura(s) em aberto, sendo 0 vencida(s).
- `python_functions`: status 200, latency 115.8ms, keyword pass `False`, quality `80`, reason `python_functions_native_structured:finance`
  errors: missing_expected_keyword
  answer: Hoje eu nao encontrei Segunda Via entre os alunos vinculados a esta conta. No momento, os alunos que aparecem aqui sao: Lucas Oliveira (MAT-2026-001), Ana Oliveira (MAT-2026-002). Se quiser, me diga qual deles voce quer consultar.
- `llamaindex`: status 200, latency 119.0ms, keyword pass `False`, quality `80`, reason `dados estruturados devem passar por service deterministico`
  errors: missing_expected_keyword
  answer: Hoje eu nao encontrei Segunda Via entre os alunos vinculados a esta conta. No momento, os alunos que aparecem aqui sao: Lucas Oliveira (MAT-2026-001), Ana Oliveira (MAT-2026-002). Se quiser, me diga qual deles voce quer consultar.
- `specialist_supervisor`: status 200, latency 103.8ms, keyword pass `False`, quality `80`, reason `specialist_supervisor_tool_first:financial_summary`
  errors: missing_expected_keyword
  answer: Resumo financeiro das contas vinculadas:
- Total de faturas em aberto: 1
- Total de faturas vencidas: 0
- Ana Oliveira: 1 em aberto, 0 vencidas
  2026-03: vencimento 2026-03-10, status open, valor 1450.00

### qual o numero do boleto?

- Slice: `protected`
- Thread: `eval:guardian-finance-identifier-thread` turn `2`
- `langgraph`: status 200, latency 170.0ms, keyword pass `True`, quality `100`, reason `dados estruturados devem passar por service deterministico`
  answer: O identificador da fatura mais relevante de Ana Oliveira hoje e 4a935c4e-eafd-405e-8a54-007ae82f6698.
- Referencia: 2026-03
- Vencimento: 2026-03-10
- Status: em aberto
Se quiser a segunda via, eu sigo usando esse identificador como referencia da fatura.
- `crewai`: status 200, latency 184.1ms, keyword pass `False`, quality `80`, reason `protected_shadow_needs_student_clarification`
  errors: missing_expected_keyword
  answer: Posso te ajudar com Lucas Oliveira, Ana Oliveira. Me diga qual aluno voce quer consultar.
- `python_functions`: status 200, latency 161.6ms, keyword pass `True`, quality `100`, reason `python_functions_native_structured:finance`
  answer: O identificador da fatura mais relevante de Ana Oliveira hoje e 4a935c4e-eafd-405e-8a54-007ae82f6698.
- Referencia: 2026-03
- Vencimento: 2026-03-10
- Status: em aberto
Se quiser a segunda via, eu sigo usando esse identificador como referencia da fatura.
- `llamaindex`: status 200, latency 169.4ms, keyword pass `True`, quality `100`, reason `dados estruturados devem passar por service deterministico`
  answer: O identificador da fatura mais relevante de Ana Oliveira hoje e 4a935c4e-eafd-405e-8a54-007ae82f6698.
- Referencia: 2026-03
- Vencimento: 2026-03-10
- Status: em aberto
Se quiser a segunda via, eu sigo usando esse identificador como referencia da fatura.
- `specialist_supervisor`: status 200, latency 141.6ms, keyword pass `False`, quality `80`, reason `specialist_supervisor_tool_first:financial_summary_aggregate`
  errors: missing_expected_keyword
  answer: Resumo financeiro das contas vinculadas:
- Total de faturas em aberto: 1
- Total de faturas vencidas: 0
- Lucas Oliveira: 0 em aberto, 0 vencidas
  2026-03: vencimento 2026-03-10, status paid, valor 1450.00
- Ana Oliveira: 1 em aberto, 0 vencidas
  2026-03: vencimento 2026-03-10, status open, valor 1450.00

### quero saber se estou com a documentacao atualizada e completa e se meus boletos estao pagos ou atrasados

- Slice: `protected`
- Thread: `eval:guardian-admin-finance-thread` turn `1`
- `langgraph`: status 200, latency 267.7ms, keyword pass `True`, quality `100`, reason `dados estruturados devem passar por service deterministico`
  answer: Resumo financeiro das contas vinculadas:
- Total de faturas em aberto: 1
- Total de faturas vencidas: 0
- Lucas Oliveira: 0 em aberto, 0 vencidas
- Ana Oliveira: 1 em aberto, 0 vencidas
- Hoje nao ha faturas vencidas neste recorte.

Cadastro e documentacao:
Situacao administrativa do seu cadastro hoje: com pendencias.
Situacao documental do seu cadastro hoje:
- Email cadastral: regular. maria.oliveira@mock.eduassist.local
- Telefone cadastral: regular. +55 11 98888-1001
- Documentacao administrativa: com pendencias. Ainda falta reenviar um comprovante de residencia atualizado para concluir a conferência documental.
Proximo passo: Envie o comprovante atualizado pela secretaria ou pelo canal de documentos para concluir a conferência.
- `crewai`: status 200, latency 191.9ms, keyword pass `False`, quality `80`, reason `protected_shadow_needs_student_clarification`
  errors: missing_expected_keyword
  answer: Posso te ajudar com Lucas Oliveira, Ana Oliveira. Me diga qual aluno voce quer consultar.
- `python_functions`: status 200, latency 275.1ms, keyword pass `True`, quality `100`, reason `python_functions_native_structured:finance`
  answer: Resumo financeiro das contas vinculadas:
- Total de faturas em aberto: 1
- Total de faturas vencidas: 0
- Lucas Oliveira: 0 em aberto, 0 vencidas
- Ana Oliveira: 1 em aberto, 0 vencidas
- Hoje nao ha faturas vencidas neste recorte.

Cadastro e documentacao:
Situacao administrativa do seu cadastro hoje: com pendencias.
Situacao documental do seu cadastro hoje:
- Email cadastral: regular. maria.oliveira@mock.eduassist.local
- Telefone cadastral: regular. +55 11 98888-1001
- Documentacao administrativa: com pendencias. Ainda falta reenviar um comprovante de residencia atualizado para concluir a conferência documental.
Proximo passo: Envie o comprovante atualizado pela secretaria ou pelo canal de documentos para concluir a conferência.
- `llamaindex`: status 200, latency 337.6ms, keyword pass `True`, quality `100`, reason `dados estruturados devem passar por service deterministico`
  answer: Resumo financeiro das contas vinculadas:
- Total de faturas em aberto: 1
- Total de faturas vencidas: 0
- Lucas Oliveira: 0 em aberto, 0 vencidas
- Ana Oliveira: 1 em aberto, 0 vencidas
- Hoje nao ha faturas vencidas neste recorte.

Cadastro e documentacao:
Situacao administrativa do seu cadastro hoje: com pendencias.
Situacao documental do seu cadastro hoje:
- Email cadastral: regular. maria.oliveira@mock.eduassist.local
- Telefone cadastral: regular. +55 11 98888-1001
- Documentacao administrativa: com pendencias. Ainda falta reenviar um comprovante de residencia atualizado para concluir a conferência documental.
Proximo passo: Envie o comprovante atualizado pela secretaria ou pelo canal de documentos para concluir a conferência.
- `specialist_supervisor`: status 200, latency 138.0ms, keyword pass `False`, quality `80`, reason `specialist_supervisor_tool_first:financial_summary_aggregate`
  errors: missing_expected_keyword
  answer: Resumo financeiro das contas vinculadas:
- Total de faturas em aberto: 1
- Total de faturas vencidas: 0
- Lucas Oliveira: 0 em aberto, 0 vencidas
  2026-03: vencimento 2026-03-10, status paid, valor 1450.00
- Ana Oliveira: 1 em aberto, 0 vencidas
  2026-03: vencimento 2026-03-10, status open, valor 1450.00

### como altero o endereco de email no meu cadastro?

- Slice: `protected`
- Thread: `eval:guardian-profile-update-thread` turn `1`
- `langgraph`: status 200, latency 108.9ms, keyword pass `False`, quality `80`, reason `status administrativo autenticado exige service deterministico`
  errors: missing_expected_keyword
  answer: Sim. O envio inicial de documentos pode ser feito por canal digital.
Hoje os canais mais diretos publicados para isso sao:
- portal institucional
- email da secretaria
- secretaria presencial
No processo de matricula, o envio inicial pode ser digital. A validacao final continua com a secretaria.
O chat aberto nao deve receber documentos completos ou dados sensiveis. Quando possivel, use o portal autenticado ou o email institucional.
- `crewai`: status 200, latency 184.7ms, keyword pass `False`, quality `80`, reason `crewai_protected_identity_backstop`
  errors: missing_expected_keyword
  answer: Para atualizar seu cadastro, o caminho mais seguro e revisar os dados no portal e, se precisar de alteracao assistida, falar com a secretaria. Se quiser, eu posso te orientar sobre qual dado voce precisa ajustar primeiro.
- `python_functions`: status 200, latency 104.9ms, keyword pass `False`, quality `80`, reason `python_functions_native_structured:institution`
  errors: missing_expected_keyword
  answer: Sim. O envio inicial de documentos pode ser feito por canal digital.
Hoje os canais mais diretos publicados para isso sao:
- portal institucional
- email da secretaria
- secretaria presencial
No processo de matricula, o envio inicial pode ser digital. A validacao final continua com a secretaria.
O chat aberto nao deve receber documentos completos ou dados sensiveis. Quando possivel, use o portal autenticado ou o email institucional.
- `llamaindex`: status 200, latency 109.2ms, keyword pass `False`, quality `80`, reason `status administrativo autenticado exige service deterministico`
  errors: missing_expected_keyword
  answer: Sim. O envio inicial de documentos pode ser feito por canal digital.
Hoje os canais mais diretos publicados para isso sao:
- portal institucional
- email da secretaria
- secretaria presencial
No processo de matricula, o envio inicial pode ser digital. A validacao final continua com a secretaria.
O chat aberto nao deve receber documentos completos ou dados sensiveis. Quando possivel, use o portal autenticado ou o email institucional.
- `specialist_supervisor`: status 599, latency 12012.6ms, keyword pass `False`, quality `0`, reason `exception`
  errors: request_failed
  answer: 

### e o telefone?

- Slice: `protected`
- Thread: `eval:guardian-profile-update-thread` turn `2`
- `langgraph`: status 200, latency 147.4ms, keyword pass `False`, quality `55`, reason `status administrativo autenticado exige service deterministico`
  errors: followup_context_drop, missing_expected_keyword
  answer: Sua conta tem mais de um aluno vinculado. Diga qual aluno deseja consultar: Lucas Oliveira (MAT-2026-001), Ana Oliveira (MAT-2026-002).
- `crewai`: status 200, latency 167.6ms, keyword pass `False`, quality `55`, reason `protected_shadow_unmatched_student_reference`
  errors: followup_context_drop, missing_expected_keyword
  answer: Hoje eu nao encontrei Telefone entre os alunos vinculados a esta conta. No momento, os alunos que aparecem aqui sao: Lucas Oliveira, Ana Oliveira. Se quiser, me diga qual deles voce quer consultar.
- `python_functions`: status 200, latency 132.6ms, keyword pass `False`, quality `55`, reason `python_functions_native_structured:institution`
  errors: followup_context_drop, missing_expected_keyword
  answer: Sua conta tem mais de um aluno vinculado. Diga qual aluno deseja consultar: Lucas Oliveira (MAT-2026-001), Ana Oliveira (MAT-2026-002).
- `llamaindex`: status 200, latency 126.7ms, keyword pass `False`, quality `55`, reason `status administrativo autenticado exige service deterministico`
  errors: followup_context_drop, missing_expected_keyword
  answer: Sua conta tem mais de um aluno vinculado. Diga qual aluno deseja consultar: Lucas Oliveira (MAT-2026-001), Ana Oliveira (MAT-2026-002).
- `specialist_supervisor`: status 200, latency 4175.7ms, keyword pass `False`, quality `68`, reason `A pergunta do usuário "e o telefone?" é ambígua e não especifica qual telefone é necessário. É preciso pedir clarificação para entender se ele busca um contato geral da instituição, de um departamento específico ou outra informação.`
  errors: missing_expected_keyword, unnecessary_clarification
  answer: De qual telefone você precisa? Você se refere a um departamento específico, contato geral da instituição ou outra coisa?

### e os documentos?

- Slice: `protected`
- Thread: `eval:guardian-profile-update-thread` turn `3`
- `langgraph`: status 200, latency 121.9ms, keyword pass `False`, quality `45`, reason `status administrativo autenticado exige service deterministico`
  errors: followup_context_drop, missing_expected_keyword, repetitive_reply
  answer: Sua conta tem mais de um aluno vinculado. Diga qual aluno deseja consultar: Lucas Oliveira (MAT-2026-001), Ana Oliveira (MAT-2026-002).
- `crewai`: status 200, latency 195.2ms, keyword pass `False`, quality `55`, reason `protected_shadow_needs_student_clarification`
  errors: followup_context_drop, missing_expected_keyword
  answer: Posso te ajudar com Lucas Oliveira, Ana Oliveira. Me diga qual aluno voce quer consultar.
- `python_functions`: status 200, latency 138.2ms, keyword pass `False`, quality `45`, reason `python_functions_native_structured:institution`
  errors: followup_context_drop, missing_expected_keyword, repetitive_reply
  answer: Sua conta tem mais de um aluno vinculado. Diga qual aluno deseja consultar: Lucas Oliveira (MAT-2026-001), Ana Oliveira (MAT-2026-002).
- `llamaindex`: status 200, latency 123.6ms, keyword pass `False`, quality `45`, reason `status administrativo autenticado exige service deterministico`
  errors: followup_context_drop, missing_expected_keyword, repetitive_reply
  answer: Sua conta tem mais de um aluno vinculado. Diga qual aluno deseja consultar: Lucas Oliveira (MAT-2026-001), Ana Oliveira (MAT-2026-002).
- `specialist_supervisor`: status 599, latency 4933.4ms, keyword pass `False`, quality `0`, reason `exception`
  errors: request_failed
  answer: 

### e o proximo passo?

- Slice: `protected`
- Thread: `eval:guardian-profile-update-thread` turn `4`
- `langgraph`: status 200, latency 139.6ms, keyword pass `False`, quality `45`, reason `status administrativo autenticado exige service deterministico`
  errors: followup_context_drop, missing_expected_keyword, repetitive_reply
  answer: Sua conta tem mais de um aluno vinculado. Diga qual aluno deseja consultar: Lucas Oliveira (MAT-2026-001), Ana Oliveira (MAT-2026-002).
- `crewai`: status 200, latency 11264.8ms, keyword pass `False`, quality `55`, reason `crewai_protected_flow_timeout`
  errors: followup_context_drop, missing_expected_keyword
  answer: Eu nao consegui consolidar essa consulta protegida com seguranca agora. Se quiser, me diga qual aluno e qual dado voce quer consultar.
- `python_functions`: status 200, latency 187.8ms, keyword pass `False`, quality `55`, reason `python_functions_native_structured:support`
  errors: followup_context_drop, missing_expected_keyword
  answer: Ainda nao encontrei um protocolo recente nesta conversa para consultar o status da fila. Se quiser, me diga o codigo que comeca com VIS, REQ ou ATD, ou me lembre se o assunto era visita, direcao, financeiro ou secretaria.
- `llamaindex`: status 200, latency 143.0ms, keyword pass `False`, quality `45`, reason `status administrativo autenticado exige service deterministico`
  errors: followup_context_drop, missing_expected_keyword, repetitive_reply
  answer: Sua conta tem mais de um aluno vinculado. Diga qual aluno deseja consultar: Lucas Oliveira (MAT-2026-001), Ana Oliveira (MAT-2026-002).
- `specialist_supervisor`: status 200, latency 6824.3ms, keyword pass `False`, quality `68`, reason `A pergunta do usuário 'e o proximo passo?' é ambígua e não fornece contexto suficiente para determinar a intenção. Com base nas interações anteriores, o usuário pode estar se referindo a um processo de visita, protocolo ou documentos. É necessário pedir clarificação para direcionar a solicitação ao especialista correto.`
  errors: missing_expected_keyword, unnecessary_clarification
  answer: Você se refere ao próximo passo de qual processo ou solicitação? Por exemplo, uma visita, um protocolo, ou algo relacionado aos documentos que mencionamos antes?

### quero protocolar uma solicitacao para a direcao sobre ampliacao do horario da biblioteca

- Slice: `support`
- Thread: `eval:request-thread` turn `1`
- `langgraph`: status 200, latency 182.7ms, keyword pass `True`, quality `100`, reason `a solicitacao pode ser executada por workflow estruturado com protocolo`
  answer: Solicitacao institucional registrada para direcao. Protocolo: REQ-20260331-CDD9B3. Assunto: quero protocolar uma solicitacao para a direcao sobre ampliacao do horario da biblioteca. Fila responsavel: direcao. Ticket operacional: ATD-20260331-1A7ABE1C. A equipe faz a triagem inicial e segue o retorno pelo fluxo institucional.
- `crewai`: status 200, latency 238.7ms, keyword pass `False`, quality `80`, reason `support_handoff_created`
  errors: missing_expected_keyword
  answer: Encaminhei sua solicitacao para a fila de direcao. Protocolo: ATD-20260331-CBAB1AC7. Status atual: queued. A equipe humana podera continuar esse atendimento no portal operacional.
- `python_functions`: status 200, latency 108.8ms, keyword pass `False`, quality `80`, reason `python_functions_native_contextual_public_answer`
  errors: missing_expected_keyword
  answer: A biblioteca se chama Biblioteca Aurora e funciona de segunda a sexta, das 7h30 as 18h00.
- `llamaindex`: status 200, latency 117.5ms, keyword pass `False`, quality `80`, reason `contextual_public_direct_answer`
  errors: missing_expected_keyword
  answer: A biblioteca se chama Biblioteca Aurora e funciona de segunda a sexta, das 7h30 as 18h00.
- `specialist_supervisor`: status 200, latency 89.9ms, keyword pass `False`, quality `80`, reason `specialist_supervisor_fast_path:library_hours`
  errors: missing_expected_keyword
  answer: A biblioteca se chama Biblioteca Aurora e funciona Atendimento ao publico de segunda a sexta, das 7h30 as 18h00.

### quero complementar meu pedido dizendo que preciso de resposta ainda esta semana

- Slice: `support`
- Thread: `eval:request-thread` turn `2`
- `langgraph`: status 200, latency 191.7ms, keyword pass `True`, quality `100`, reason `a solicitacao pode ser executada por workflow estruturado com protocolo`
  answer: Complemento registrado na fila de direcao. Protocolo: REQ-20260331-CDD9B3. Ticket operacional: ATD-20260331-1A7ABE1C. Novo complemento: preciso de resposta ainda esta semana. A equipe responsavel recebe essa atualizacao no mesmo fluxo do pedido.
- `crewai`: status 200, latency 1088.0ms, keyword pass `False`, quality `80`, reason `crewai_public_fast_path`
  errors: missing_expected_keyword
  answer: Hoje a escola divulga atividades e espacos complementares como Biblioteca Aurora, Espaco Maker, futsal, volei escolar. Se quiser, eu tambem posso detalhar Biblioteca Aurora, Laboratorio de Ciencias, Espaco Maker, Quadra Poliesportiva Coberta.
- `python_functions`: status 200, latency 159.6ms, keyword pass `False`, quality `80`, reason `python_functions_native_structured:support`
  errors: missing_expected_keyword
  answer: Nao consegui complementar a solicitacao agora. Se quiser, me passe novamente o protocolo ou reescreva o complemento em uma frase curta.
- `llamaindex`: status 200, latency 175.3ms, keyword pass `False`, quality `80`, reason `a solicitacao pode ser executada por workflow estruturado com protocolo`
  errors: missing_expected_keyword
  answer: Nao consegui complementar a solicitacao agora. Se quiser, me passe novamente o protocolo ou reescreva o complemento em uma frase curta.
- `specialist_supervisor`: status 599, latency 12013.1ms, keyword pass `False`, quality `0`, reason `exception`
  errors: request_failed
  answer: 

### qual o status do meu protocolo?

- Slice: `support`
- Thread: `eval:request-thread` turn `3`
- `langgraph`: status 200, latency 170.9ms, keyword pass `True`, quality `100`, reason `a solicitacao pode ser executada por workflow estruturado com protocolo`
  answer: Sua solicitacao institucional segue em fila na fila de direcao. Protocolo: REQ-20260331-CDD9B3. Assunto: quero protocolar uma solicitacao para a direcao sobre ampliacao do horario da biblioteca. Area responsavel: direcao. Ticket operacional: ATD-20260331-1A7ABE1C. Ultima movimentacao registrada: 31/03/2026 as 00:17. Proximo passo: a equipe responsavel analisa o contexto e devolve o retorno pelo fluxo institucional.
- `crewai`: status 200, latency 185.1ms, keyword pass `False`, quality `80`, reason `workflow_status_lookup`
  errors: missing_expected_keyword
  answer: Sua solicitacao segue em fila com a area de direcao. - Protocolo: ATD-20260331-CBAB1AC7 - Ticket operacional: ATD-20260331-CBAB1AC7 - Status atual: queued Proximo passo: a equipe responsavel recebe essa atualizacao e segue o retorno pelo fluxo institucional.
- `python_functions`: status 200, latency 152.0ms, keyword pass `True`, quality `100`, reason `python_functions_native_structured:support`
  answer: Ainda nao encontrei um protocolo recente nesta conversa para consultar o status da fila. Se quiser, me diga o codigo que comeca com VIS, REQ ou ATD, ou me lembre se o assunto era visita, direcao, financeiro ou secretaria.
- `llamaindex`: status 200, latency 176.1ms, keyword pass `True`, quality `100`, reason `a solicitacao pode ser executada por workflow estruturado com protocolo`
  answer: Ainda nao encontrei um protocolo recente nesta conversa para consultar o status da fila. Se quiser, me diga o codigo que comeca com VIS, REQ ou ATD, ou me lembre se o assunto era visita, direcao, financeiro ou secretaria.
- `specialist_supervisor`: status 599, latency 11359.5ms, keyword pass `False`, quality `0`, reason `exception`
  errors: request_failed
  answer: 

### resume meu pedido

- Slice: `support`
- Thread: `eval:request-thread` turn `4`
- `langgraph`: status 200, latency 175.2ms, keyword pass `True`, quality `100`, reason `a solicitacao pode ser executada por workflow estruturado com protocolo`
  answer: Resumo da sua solicitacao institucional:. Assunto: quero protocolar uma solicitacao para a direcao sobre ampliacao do horario da biblioteca. Area responsavel: direcao. Detalhes registrados: quero protocolar uma solicitacao para a direcao sobre ampliacao do horario da biblioteca

Complemento registrado: preciso de resposta ainda esta semana. Protocolo: REQ-20260331-CDD9B3. Ticket operacional: ATD-20260331-1A7ABE1C. Status atual: em fila. Se quiser, eu tambem posso te dizer o prazo estimado ou quem responde por essa fila.
- `crewai`: status 200, latency 175.3ms, keyword pass `False`, quality `80`, reason `workflow_summary_lookup`
  errors: missing_expected_keyword
  answer: Seu pedido de visita segue em fila com a fila de direcao. - Protocolo: ATD-20260331-CBAB1AC7 - Ticket operacional: ATD-20260331-CBAB1AC7 - Preferencia registrada: janela a confirmar Proximo passo: a equipe comercial valida a janela e retorna com a confirmacao.
- `python_functions`: status 200, latency 178.3ms, keyword pass `False`, quality `80`, reason `python_functions_native_structured:support`
  errors: missing_expected_keyword
  answer: Ainda nao encontrei um protocolo recente nesta conversa para montar o resumo do pedido. Se quiser, me diga o codigo que comeca com VIS, REQ ou ATD, ou me lembre se o assunto era visita, direcao, financeiro ou secretaria.
- `llamaindex`: status 200, latency 167.6ms, keyword pass `False`, quality `80`, reason `a solicitacao pode ser executada por workflow estruturado com protocolo`
  errors: missing_expected_keyword
  answer: Ainda nao encontrei um protocolo recente nesta conversa para montar o resumo do pedido. Se quiser, me diga o codigo que comeca com VIS, REQ ou ATD, ou me lembre se o assunto era visita, direcao, financeiro ou secretaria.
- `specialist_supervisor`: status 200, latency 5115.4ms, keyword pass `False`, quality `80`, reason `specialist_supervisor_strict_safe_fallback`
  errors: missing_expected_keyword
  answer: Nao consegui consolidar essa resposta premium com seguranca agora. Se quiser, me diga exatamente se voce quer ver notas, frequencia, documentacao, financeiro ou status de protocolo.

