# Four-Path Chatbot Comparison Report

Date: 2026-04-03T19:26:11.923325+00:00

Dataset: `/home/edann/projects/eduassist-platform/tests/evals/datasets/retrieval_5q_llm_compare.generated.20260403.json`

LLM forced: `True`

Run prefix: `debug:four-path:llm-forced:20260403T192332Z`

## Stack Summary

| Stack | OK | Keyword pass | Quality | Avg latency | Final polish |
| --- | --- | --- | --- | --- | --- |
| `langgraph` | `5/5` | `2/5` | `85.6` | `8001.2 ms` | `5/5` |
| `python_functions` | `5/5` | `3/5` | `92.0` | `2972.0 ms` | `0/5` |
| `llamaindex` | `5/5` | `1/5` | `84.0` | `8791.2 ms` | `4/5` |
| `specialist_supervisor` | `4/5` | `1/5` | `68.0` | `11889.7 ms` | `0/5` |

## By Slice

- `public`
  - `langgraph`: ok 5/5, keyword pass 2/5, quality 85.6, latency 8001.2ms, final polish 5/5
  - `python_functions`: ok 5/5, keyword pass 3/5, quality 92.0, latency 2972.0ms, final polish 0/5
  - `llamaindex`: ok 5/5, keyword pass 1/5, quality 84.0, latency 8791.2ms, final polish 4/5
  - `specialist_supervisor`: ok 4/5, keyword pass 1/5, quality 68.0, latency 11889.7ms, final polish 0/5

## Error Types

- `langgraph`: missing_expected_keyword=3, unnecessary_clarification=1
- `python_functions`: missing_expected_keyword=2
- `llamaindex`: missing_expected_keyword=4
- `specialist_supervisor`: missing_expected_keyword=3, request_failed=1

## Prompt Results

### Olhando apenas para a base publica da escola, que continuidade de apoio aparece quando se cruzam orientacao educacional, mediacao de convivio, estudo guiado e relacao com a familia?

- Slice: `public`
- Thread: `retrieval_5q_llm_compare_support_continuum_open` turn `1`
- `langgraph`: status 200, latency 2363.9ms, keyword pass `False`, quality `80`, used_llm `True`, llm_stages `structured_polish`, final_polish_applied `True`, final_polish_mode `light_polish`, final_polish_reason `langgraph_public_noncanonical`, reason `bundle publico canonico deve seguir lane publica mesmo se a classificacao superestimar autenticacao`
  errors: missing_expected_keyword
  answer: Estudar em uma escola publica pode ser uma boa escolha para muitas familias, e eu nao vou te vender uma comparacao vazia. No que esta publicado aqui, os diferenciais desta escola passam por Tutoria academica e projeto de vida, Espaco Maker integrado ao curriculo, Acolhimento estruturado para familias e estudantes. A proposta pedagogica publicada hoje combina Projeto pedagogico laico, com foco em aprendizagem por projetos, cultura digital responsavel, acompanhamento socioemocional e preparacao academica progressiva.. Na pratica, isso aparece em acompanhamento mais proximo da aprendizagem, projeto de vida e combinados pedagogicos mais claros. Escola laica com Ensino Fundamental II e Ensino Medio, acompanhamento tutorial e trilhas academicas no contraturno. Se quiser, eu posso te mostrar isso de forma mais pratica na rotina, na proposta pedagogica ou no contraturno.
- `python_functions`: status 200, latency 195.8ms, keyword pass `False`, quality `80`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `python_functions_prefers_deterministic`, reason `python_functions_native_structured:institution`
  errors: missing_expected_keyword
  answer: Estudar em uma escola publica pode ser uma boa escolha para muitas familias, e eu nao vou te vender uma comparacao vazia. No que esta publicado aqui, os diferenciais desta escola passam por Tutoria academica e projeto de vida, Espaco Maker integrado ao curriculo, Acolhimento estruturado para familias e estudantes. A proposta pedagogica publicada hoje combina Projeto pedagogico laico, com foco em aprendizagem por projetos, cultura digital responsavel, acompanhamento socioemocional e preparacao academica progressiva.. Na pratica, isso aparece em acompanhamento mais proximo da aprendizagem, projeto de vida e combinados pedagogicos mais claros. Escola laica com Ensino Fundamental II e Ensino Medio, acompanhamento tutorial e trilhas academicas no contraturno. Se quiser, eu posso te mostrar isso de forma mais pratica na rotina, na proposta pedagogica ou no contraturno.
- `llamaindex`: status 200, latency 11694.9ms, keyword pass `False`, quality `80`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `llamaindex_not_eligible`, reason `bundle publico canonico deve seguir lane publica mesmo se a classificacao superestimar autenticacao`
  errors: missing_expected_keyword
  answer: Estudar em uma escola publica pode ser uma boa escolha para muitas familias, e eu nao vou te vender uma comparacao vazia. No que esta publicado aqui, os diferenciais desta escola passam por Tutoria academica e projeto de vida, Espaco Maker integrado ao curriculo, Acolhimento estruturado para familias e estudantes. A proposta pedagogica publicada hoje combina Projeto pedagogico laico, com foco em aprendizagem por projetos, cultura digital responsavel, acompanhamento socioemocional e preparacao academica progressiva.. Na pratica, isso aparece em acompanhamento mais proximo da aprendizagem, projeto de vida e combinados pedagogicos mais claros. Escola laica com Ensino Fundamental II e Ensino Medio, acompanhamento tutorial e trilhas academicas no contraturno. Se quiser, eu posso te mostrar isso de forma mais pratica na rotina, na proposta pedagogica ou no contraturno.
- `specialist_supervisor`: status 200, latency 351.0ms, keyword pass `False`, quality `80`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `stack_not_enabled`, reason `bundle publico canonico deve seguir lane publica mesmo se a classificacao superestimar autenticacao`
  errors: missing_expected_keyword
  answer: Estudar em uma escola publica pode ser uma boa escolha para muitas familias, e eu nao vou te vender uma comparacao vazia. No que esta publicado aqui, os diferenciais desta escola passam por Tutoria academica e projeto de vida, Espaco Maker integrado ao curriculo, Acolhimento estruturado para familias e estudantes. A proposta pedagogica publicada hoje combina Projeto pedagogico laico, com foco em aprendizagem por projetos, cultura digital responsavel, acompanhamento socioemocional e preparacao academica progressiva.. Na pratica, isso aparece em acompanhamento mais proximo da aprendizagem, projeto de vida e combinados pedagogicos mais claros. Escola laica com Ensino Fundamental II e Ensino Medio, acompanhamento tutorial e trilhas academicas no contraturno. Se quiser, eu posso te mostrar isso de forma mais pratica na rotina, na proposta pedagogica ou no contraturno.

### Sem repetir slogans, que arquitetura de rotina escolar aparece quando se combinam turno estendido, oficinas, refeicao, estudo acompanhado e permanencia no contraturno?

- Slice: `public`
- Thread: `retrieval_5q_llm_compare_extended_day_ecosystem_open` turn `1`
- `langgraph`: status 200, latency 8510.0ms, keyword pass `True`, quality `100`, used_llm `True`, llm_stages `structured_polish, answer_verifier_judge`, final_polish_applied `True`, final_polish_mode `light_polish`, final_polish_reason `langgraph_public_noncanonical`, reason `bundle publico canonico deve seguir lane publica mesmo se a classificacao superestimar autenticacao`
  answer: Que ótima pergunta! No Colégio Horizonte, quando combinamos o turno estendido com oficinas, refeição, estudo acompanhado e a permanência no contraturno, o que temos é uma rotina de período integral. É uma opção bem completa, que oferece aos nossos estudantes um acompanhamento mais próximo, uma rotina organizada e muitas atividades formativas adicionais. Geralmente, a tarde inclui um momento de acolhimento, almoço ou lanche, um bloco dedicado aos estudos e uma atividade complementar, como nossas oficinas de leitura, projetos maker, cultura digital, práticas artísticas, monitorias ou até mesmo a recomposição de aprendizagem.
- `python_functions`: status 200, latency 4471.7ms, keyword pass `True`, quality `100`, used_llm `True`, llm_stages `answer_verifier_judge`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `python_functions_prefers_deterministic`, reason `python_functions_native_structured:institution`
  answer: No Colégio Horizonte, a combinação de turno estendido, oficinas, refeição, estudo acompanhado e permanência no contraturno forma uma rotina de período integral. Essa opção complementar oferece aos estudantes um acompanhamento mais próximo, uma rotina organizada e atividades formativas adicionais. A tarde geralmente inclui acolhimento, almoço ou lanche, um bloco de estudo e uma atividade complementar, como oficinas de leitura, projetos maker, cultura digital, práticas artísticas, monitorias ou recomposição de aprendizagem.
- `llamaindex`: status 200, latency 4788.4ms, keyword pass `False`, quality `80`, used_llm `True`, llm_stages `answer_composition, structured_polish`, final_polish_applied `True`, final_polish_mode `light_polish`, final_polish_reason `llamaindex_documentary_synthesis`, reason `llamaindex_public_profile`
  errors: missing_expected_keyword
  answer: Fora da sala regular, o material publico mostra que periodo integral e estudo orientado se completam como camadas de apoio ao estudante. O periodo integral e uma opcao complementar destinada a familias que desejam ampliar a permanencia do estudante na escola com acompanhamento, rotina organizada e atividades formativas adicionais. O estudo orientado oferece apoio para organizacao de tarefas, acompanhamento de prazos, leitura orientada e consolidacao de habitos academicos. Em geral, a rotina da tarde combina acolhimento, almoco ou lanche conforme o plano contratado, bloco de estudo, atividade complementar e horario de saida definido. Entre as atividades possiveis estao oficinas de leitura, projetos maker, cultura digital, praticas artisticas, monitorias e recomposicao de aprendizagem. O estudo orientado ajuda o aluno a manter rotina e prioridade, mas nao garante, por si so, desempenho academico especifico.
- `specialist_supervisor`: status 200, latency 8494.8ms, keyword pass `False`, quality `80`, used_llm `True`, llm_stages `specialist_execution`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `quality_first_path`, reason `specialist_supervisor_budget_safe_fallback`
  errors: missing_expected_keyword
  answer: Nao consegui concluir essa resposta premium agora. Se quiser, reformule em uma frase mais direta ou repita em instantes.

### Se uma familia precisa entender por onde um tema caminha dentro da escola, que trilha institucional os documentos publicos sugerem entre secretaria, coordenacao, direcao e canais oficiais?

- Slice: `public`
- Thread: `retrieval_5q_llm_compare_governance_channels_open` turn `1`
- `langgraph`: status 200, latency 8863.6ms, keyword pass `False`, quality `80`, used_llm `True`, llm_stages `structured_polish, answer_verifier_judge`, final_polish_applied `True`, final_polish_mode `light_polish`, final_polish_reason `langgraph_public_noncanonical`, reason `bundle publico canonico deve seguir lane publica mesmo se a classificacao superestimar autenticacao`
  errors: missing_expected_keyword
  answer: Na base publica do Colegio Horizonte, coordenacao e direcao aparecem em uma trilha clara de governanca e protocolo. A diretora geral do Colegio Horizonte e Helena Martins. A lideranca atende familias por agenda institucional. Direcao geral: direcao@colegiohorizonte.edu.br Coordenacao Fundamental II: fundamental2@colegiohorizonte.edu.br Coordenacao Ensino Medio: ensinomedio@colegiohorizonte.edu.br. A diretora participa de encontros institucionais com familias ao longo do ano, especialmente nas reunioes de acolhimento, eventos gerais e marcos bimestrais de acompanhamento da comunidade escolar.
- `python_functions`: status 200, latency 5047.5ms, keyword pass `False`, quality `80`, used_llm `True`, llm_stages `answer_verifier_judge`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `python_functions_prefers_deterministic`, reason `python_functions_native_structured:institution`
  errors: missing_expected_keyword
  answer: Na base publica do Colegio Horizonte, coordenacao e direcao aparecem em uma trilha clara de governanca e protocolo. A diretora geral do Colegio Horizonte e Helena Martins. A lideranca atende familias por agenda institucional. Direcao geral: direcao@colegiohorizonte.edu.br Coordenacao Fundamental II: fundamental2@colegiohorizonte.edu.br Coordenacao Ensino Medio: ensinomedio@colegiohorizonte.edu.br. A diretora participa de encontros institucionais com familias ao longo do ano, especialmente nas reunioes de acolhimento, eventos gerais e marcos bimestrais de acompanhamento da comunidade escolar.
- `llamaindex`: status 200, latency 13057.4ms, keyword pass `False`, quality `80`, used_llm `True`, llm_stages `answer_composition, structured_polish`, final_polish_applied `True`, final_polish_mode `light_polish`, final_polish_reason `llamaindex_documentary_synthesis`, reason `llamaindex_public_profile`
  errors: missing_expected_keyword
  answer: Na base publica do Colegio Horizonte, coordenacao e direcao aparecem em uma trilha clara de governanca e protocolo. A diretora geral do Colegio Horizonte e Helena Martins. A lideranca atende familias por agenda institucional. Direcao geral: direcao@colegiohorizonte.edu.br Coordenacao Fundamental II: fundamental2@colegiohorizonte.edu.br Coordenacao Ensino Medio: ensinomedio@colegiohorizonte.edu.br. A diretora participa de encontros institucionais com familias ao longo do ano, especialmente nas reunioes de acolhimento, eventos gerais e marcos bimestrais de acompanhamento da comunidade escolar.
- `specialist_supervisor`: status 599, latency 20002.7ms, keyword pass `False`, quality `0`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `none`, final_polish_reason `none`, reason `exception`
  errors: request_failed
  answer: 

### Que logica institucional aparece quando a escola conecta comprovacao de saude, ausencia em atividade avaliativa, comunicacao com a familia e reorganizacao pedagogica?

- Slice: `public`
- Thread: `retrieval_5q_llm_compare_health_reorganization_open` turn `1`
- `langgraph`: status 200, latency 15839.8ms, keyword pass `False`, quality `80`, used_llm `True`, llm_stages `structured_polish, answer_verifier_judge`, final_polish_applied `True`, final_polish_mode `light_polish`, final_polish_reason `langgraph_public_noncanonical`, reason `bundle publico canonico deve seguir lane publica mesmo se a classificacao superestimar autenticacao`
  errors: missing_expected_keyword
  answer: Que bom que você perguntou! No Colégio Horizonte, quando um estudante precisa se ausentar por motivos de saúde, a gente conecta a comprovação médica com a comunicação à família para entender a situação. Isso nos permite reorganizar a parte pedagógica, oferecendo apoio como segunda chamada ou atividades de recuperação, sempre pensando no bem-estar e no aprendizado do aluno.
- `python_functions`: status 200, latency 4918.8ms, keyword pass `True`, quality `100`, used_llm `True`, llm_stages `answer_verifier_judge`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `python_functions_prefers_deterministic`, reason `python_functions_native_structured:institution`
  answer: No Colégio Horizonte, a lógica institucional conecta a comprovação de saúde, a justificativa de ausência em atividades avaliativas, a comunicação com a família e a reorganização pedagógica como partes de um mesmo protocolo. Atestados médicos e justificativas formais são importantes para apoiar a análise de ausências, pedidos de segunda chamada ou adaptações temporárias na rotina do estudante. Em casos de desempenho abaixo do esperado, a escola pode oferecer recuperação paralela, atividades orientadas ou avaliações substitutivas, sempre considerando a trajetória do aluno.
- `llamaindex`: status 200, latency 9368.4ms, keyword pass `False`, quality `80`, used_llm `True`, llm_stages `answer_composition, answer_verifier_judge, structured_polish`, final_polish_applied `True`, final_polish_mode `light_polish`, final_polish_reason `llamaindex_documentary_synthesis`, reason `llamaindex_public_direct_retrieval`
  errors: missing_expected_keyword
  answer: Olá! Quando a escola conecta a comprovação de saúde, a ausência em atividades avaliativas, a comunicação com a família e a reorganização pedagógica, a lógica institucional que aparece é a de **garantir o direito à educação e a recuperação da aprendizagem do estudante, mesmo diante de imprevistos de saúde**.

Isso significa que a escola busca:

1.  **Apoiar o estudante em sua recuperação:** Ao solicitar a comprovação de saúde, a escola entende a situação do aluno e pode oferecer o suporte necessário.
2.  **Manter a família informada:** A comunicação é essencial para que os pais ou responsáveis acompanhem o processo e colaborem com a escola.
3.  **Reorganizar o planejamento pedagógico:** Para que o aluno não seja prejudicado pela ausência, a escola adapta as atividades e avaliações, garantindo que ele tenha a oportunidade de aprender e demonstrar seu conhecimento.

Em resumo, a escola atua de forma **acolhedora e flexível**, priorizando o bem-estar e o desenvolvimento acadêmico do aluno.
- `specialist_supervisor`: status 200, latency 12387.3ms, keyword pass `False`, quality `80`, used_llm `True`, llm_stages `specialist_execution`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `quality_first_path`, reason `specialist_supervisor_budget_direct:institution_specialist`
  errors: missing_expected_keyword
  answer: A lógica institucional do Colégio Horizonte conecta a comprovação de saúde, ausência em atividades avaliativas, comunicação com a família e reorganização pedagógica por meio de sua política de frequência e acompanhamento. Em caso de ausência, incluindo aquelas justificadas (como por questões de saúde, implícito em 'justificativas'), o professor pode orientar a recomposição ou acompanhamento posterior da atividade ou conteúdo. Se a frequência do estudante cair abaixo de 75%, ele entra em alerta acadêmico e a coordenação pedagógica ou orientação educacional aciona a família. A escola acompanha as justificativas, a recorrência das ausências e, se necessário, estabelece um plano de recomposição junto à família e ao estudante para garantir a continuidade do aprendizado.

### Para uma familia que ainda esta conhecendo a escola, como a base publica deixa clara a fronteira entre o que ja se entende por calendarios e orientacoes abertas e o que so aparece com portal, login e conta vinculada?

- Slice: `public`
- Thread: `retrieval_5q_llm_compare_visibility_boundary_onboarding_open` turn `1`
- `langgraph`: status 200, latency 4428.6ms, keyword pass `True`, quality `88`, used_llm `True`, llm_stages `structured_polish, answer_verifier_judge`, final_polish_applied `True`, final_polish_mode `light_polish`, final_polish_reason `langgraph_public_noncanonical`, reason `bundle publico canonico deve seguir lane publica mesmo se a classificacao superestimar autenticacao`
  errors: unnecessary_clarification
  answer: Olá! Para as famílias que estão nos conhecendo, é importante saber que temos algumas frentes de comunicação. A Secretaria cuida de declarações, históricos e orientações administrativas. Já o Portal Institucional é o lugar para protocolos e envio digital de documentos, e o acesso é feito com login e senha. Se precisar de ajuda com as credenciais, a Secretaria ou o suporte digital podem auxiliar. Para o envio de documentos, você pode usar o portal, o email da secretaria ou ir presencialmente. Lembre-se que o chat aberto não é o canal para documentos completos ou dados sensíveis, ok?
- `python_functions`: status 200, latency 226.4ms, keyword pass `True`, quality `100`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `python_functions_prefers_deterministic`, reason `python_functions_native_structured:institution`
  answer: Hoje a familia precisa entender quatro frentes publicas deste fluxo:
- Secretaria: recebe declaracoes, historico, atualizacoes cadastrais e orientacoes administrativas.
- Portal institucional: centraliza protocolo e envio digital inicial de documentos.
- Credenciais: login e senha do portal continuam sendo a base de acesso; se precisar recuperar acesso, o melhor caminho e a secretaria ou o suporte digital.
- Documentos: o envio inicial pode ser feito por portal institucional, email da secretaria ou secretaria presencial.
O chat aberto nao deve receber documentos completos ou dados sensiveis. Quando possivel, use o portal autenticado ou o email institucional.
- `llamaindex`: status 200, latency 5046.9ms, keyword pass `True`, quality `100`, used_llm `True`, llm_stages `answer_composition, structured_polish`, final_polish_applied `True`, final_polish_mode `light_polish`, final_polish_reason `llamaindex_documentary_synthesis`, reason `llamaindex_public_profile`
  answer: No calendario publico, o que costuma ficar aberto para familias sao marcos institucionais gerais e eventos coletivos. A fronteira pratica aparece assim: orientacoes abertas circulam no calendario publico, no portal institucional aberto e nos canais oficiais; o que so ganha detalhe depois do login e da conta vinculada no portal sao informacoes individuais por aluno, convites direcionados, protocolos, situacoes financeiras e acompanhamentos protegidos. Sempre que houver ajuste relevante no calendario de avaliacao, a escola atualiza o portal e reforca a comunicacao pelos canais oficiais. O ambiente digital amplia o atendimento, mas nao substitui todos os processos formais.
- `specialist_supervisor`: status 200, latency 18212.9ms, keyword pass `True`, quality `100`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `stack_not_enabled`, reason `bundle publico canonico deve seguir lane publica mesmo se a classificacao superestimar autenticacao`
  answer: Hoje a familia precisa entender quatro frentes publicas deste fluxo:
- Secretaria: recebe declaracoes, historico, atualizacoes cadastrais e orientacoes administrativas.
- Portal institucional: centraliza protocolo e envio digital inicial de documentos.
- Credenciais: login e senha do portal continuam sendo a base de acesso; se precisar recuperar acesso, o melhor caminho e a secretaria ou o suporte digital.
- Documentos: o envio inicial pode ser feito por portal institucional, email da secretaria ou secretaria presencial.
O chat aberto nao deve receber documentos completos ou dados sensiveis. Quando possivel, use o portal autenticado ou o email institucional.

