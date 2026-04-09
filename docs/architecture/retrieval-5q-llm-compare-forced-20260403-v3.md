# Four-Path Chatbot Comparison Report

Date: 2026-04-03T19:52:03.861039+00:00

Dataset: `/home/edann/projects/eduassist-platform/tests/evals/datasets/retrieval_5q_llm_compare.generated.20260403.json`

LLM forced: `True`

Run prefix: `debug:four-path:llm-forced:20260403T194919Z`

## Stack Summary

| Stack | OK | Keyword pass | Quality | Avg latency | Final polish |
| --- | --- | --- | --- | --- | --- |
| `langgraph` | `5/5` | `4/5` | `93.6` | `6746.9 ms` | `2/5` |
| `python_functions` | `5/5` | `4/5` | `96.0` | `3979.9 ms` | `0/5` |
| `llamaindex` | `4/5` | `3/5` | `76.0` | `13421.1 ms` | `3/5` |
| `specialist_supervisor` | `5/5` | `2/5` | `83.2` | `8508.8 ms` | `0/5` |

## By Slice

- `public`
  - `langgraph`: ok 5/5, keyword pass 4/5, quality 93.6, latency 6746.9ms, final polish 2/5
  - `python_functions`: ok 5/5, keyword pass 4/5, quality 96.0, latency 3979.9ms, final polish 0/5
  - `llamaindex`: ok 4/5, keyword pass 3/5, quality 76.0, latency 13421.1ms, final polish 3/5
  - `specialist_supervisor`: ok 5/5, keyword pass 2/5, quality 83.2, latency 8508.8ms, final polish 0/5

## Error Types

- `langgraph`: missing_expected_keyword=1, unnecessary_clarification=1
- `python_functions`: missing_expected_keyword=1
- `llamaindex`: missing_expected_keyword=1, request_failed=1
- `specialist_supervisor`: missing_expected_keyword=3, strict_safe_fallback_excess=1

## Prompt Results

### Olhando apenas para a base publica da escola, que continuidade de apoio aparece quando se cruzam orientacao educacional, mediacao de convivio, estudo guiado e relacao com a familia?

- Slice: `public`
- Thread: `retrieval_5q_llm_compare_support_continuum_open` turn `1`
- `langgraph`: status 200, latency 2694.2ms, keyword pass `False`, quality `80`, used_llm `True`, llm_stages `structured_polish`, final_polish_applied `True`, final_polish_mode `light_polish`, final_polish_reason `langgraph_public_noncanonical`, reason `bundle publico canonico deve seguir lane publica mesmo se a classificacao superestimar autenticacao`
  errors: missing_expected_keyword
  answer: Estudar em uma escola publica pode ser uma boa escolha para muitas familias, e eu nao vou te vender uma comparacao vazia. No que esta publicado aqui, os diferenciais desta escola passam por Tutoria academica e projeto de vida, Espaco Maker integrado ao curriculo, Acolhimento estruturado para familias e estudantes. A proposta pedagogica publicada hoje combina Projeto pedagogico laico, com foco em aprendizagem por projetos, cultura digital responsavel, acompanhamento socioemocional e preparacao academica progressiva.. Na pratica, isso aparece em acompanhamento mais proximo da aprendizagem, projeto de vida e combinados pedagogicos mais claros. Escola laica com Ensino Fundamental II e Ensino Medio, acompanhamento tutorial e trilhas academicas no contraturno. Se quiser, eu posso te mostrar isso de forma mais pratica na rotina, na proposta pedagogica ou no contraturno.
- `python_functions`: status 200, latency 311.8ms, keyword pass `False`, quality `80`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `python_functions_prefers_deterministic`, reason `python_functions_native_structured:institution`
  errors: missing_expected_keyword
  answer: Estudar em uma escola publica pode ser uma boa escolha para muitas familias, e eu nao vou te vender uma comparacao vazia. No que esta publicado aqui, os diferenciais desta escola passam por Tutoria academica e projeto de vida, Espaco Maker integrado ao curriculo, Acolhimento estruturado para familias e estudantes. A proposta pedagogica publicada hoje combina Projeto pedagogico laico, com foco em aprendizagem por projetos, cultura digital responsavel, acompanhamento socioemocional e preparacao academica progressiva.. Na pratica, isso aparece em acompanhamento mais proximo da aprendizagem, projeto de vida e combinados pedagogicos mais claros. Escola laica com Ensino Fundamental II e Ensino Medio, acompanhamento tutorial e trilhas academicas no contraturno. Se quiser, eu posso te mostrar isso de forma mais pratica na rotina, na proposta pedagogica ou no contraturno.
- `llamaindex`: status 599, latency 23397.4ms, keyword pass `False`, quality `0`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `none`, final_polish_reason `none`, reason `exception`
  errors: request_failed
  answer: 
- `specialist_supervisor`: status 200, latency 261.0ms, keyword pass `True`, quality `100`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `deterministic_answer`, reason `specialist_supervisor_local_public_canonical_lane:public_bundle.permanence_family_support`
  answer: Para a familia acompanhar permanencia, apoio e vida escolar sem se perder, a escola combina orientacao, monitorias, comunicacao recorrente e acompanhamento de frequencia. A equipe de orientacao acompanha adaptacao, rotina de estudo, organizacao de agenda e desenvolvimento de habitos de aprendizagem. Ha monitorias agendadas, plantao de duvidas e apoio em componentes com maior incidencia de dificuldade. A escola utiliza comunicados digitais, reunioes periodicas e chamadas de acompanhamento quando o estudante precisa de suporte adicional. A promocao do estudante depende nao apenas do desempenho academico, mas tambem do cumprimento da frequencia minima institucional e legal.

### Sem repetir slogans, que arquitetura de rotina escolar aparece quando se combinam turno estendido, oficinas, refeicao, estudo acompanhado e permanencia no contraturno?

- Slice: `public`
- Thread: `retrieval_5q_llm_compare_extended_day_ecosystem_open` turn `1`
- `langgraph`: status 200, latency 8254.0ms, keyword pass `True`, quality `100`, used_llm `True`, llm_stages `answer_composition, answer_verifier_judge`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `langgraph_candidate_synthesis_already_used`, reason `bundle publico canonico deve seguir lane publica mesmo se a classificacao superestimar autenticacao`
  answer: No Colégio Horizonte, a combinação de turno estendido, oficinas, refeição, estudo acompanhado e permanência no contraturno forma uma rotina de período integral. Essa opção complementar oferece aos estudantes um acompanhamento mais próximo, uma rotina organizada e atividades formativas adicionais. A tarde geralmente inclui acolhimento, almoço ou lanche, um bloco de estudo e uma atividade complementar, como oficinas de leitura, projetos maker, cultura digital, práticas artísticas ou monitorias.
- `python_functions`: status 200, latency 4563.1ms, keyword pass `True`, quality `100`, used_llm `True`, llm_stages `answer_verifier_judge`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `python_functions_prefers_deterministic`, reason `python_functions_native_structured:institution`
  answer: No Colégio Horizonte, a combinação de turno estendido, oficinas, refeição, estudo acompanhado e permanência no contraturno forma uma rotina de período integral. Essa opção complementar oferece aos estudantes um acompanhamento mais próximo, uma rotina organizada e atividades formativas adicionais. A tarde geralmente inclui acolhimento, almoço ou lanche, um bloco de estudo e uma atividade complementar, como oficinas de leitura, projetos maker, cultura digital, práticas artísticas ou monitorias.
- `llamaindex`: status 200, latency 5517.9ms, keyword pass `False`, quality `80`, used_llm `True`, llm_stages `answer_composition, structured_polish`, final_polish_applied `True`, final_polish_mode `light_polish`, final_polish_reason `llamaindex_documentary_synthesis`, reason `llamaindex_public_profile`
  errors: missing_expected_keyword
  answer: Fora da sala regular, o material publico mostra que periodo integral e estudo orientado se completam como camadas de apoio ao estudante. O periodo integral e uma opcao complementar destinada a familias que desejam ampliar a permanencia do estudante na escola com acompanhamento, rotina organizada e atividades formativas adicionais. O estudo orientado oferece apoio para organizacao de tarefas, acompanhamento de prazos, leitura orientada e consolidacao de habitos academicos. Em geral, a rotina da tarde combina acolhimento, almoco ou lanche conforme o plano contratado, bloco de estudo, atividade complementar e horario de saida definido. Entre as atividades possiveis estao oficinas de leitura, projetos maker, cultura digital, praticas artisticas, monitorias e recomposicao de aprendizagem. O estudo orientado ajuda o aluno a manter rotina e prioridade, mas nao garante, por si so, desempenho academico especifico.
- `specialist_supervisor`: status 200, latency 12402.1ms, keyword pass `False`, quality `80`, used_llm `True`, llm_stages `specialist_execution`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `quality_first_path`, reason `specialist_supervisor_budget_safe_fallback`
  errors: missing_expected_keyword
  answer: Nao consegui concluir essa resposta premium agora. Se quiser, reformule em uma frase mais direta ou repita em instantes.

### Se uma familia precisa entender por onde um tema caminha dentro da escola, que trilha institucional os documentos publicos sugerem entre secretaria, coordenacao, direcao e canais oficiais?

- Slice: `public`
- Thread: `retrieval_5q_llm_compare_governance_channels_open` turn `1`
- `langgraph`: status 200, latency 8467.9ms, keyword pass `True`, quality `100`, used_llm `True`, llm_stages `answer_composition, answer_verifier_judge`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `langgraph_candidate_synthesis_already_used`, reason `bundle publico canonico deve seguir lane publica mesmo se a classificacao superestimar autenticacao`
  answer: Na base publica do Colegio Horizonte, a trilha institucional fica mais clara quando secretaria, coordenacao, direcao e canais oficiais aparecem como etapas complementares de encaminhamento e protocolo. Na pratica, a secretaria funciona como porta de entrada operacional para documentos, orientacoes iniciais e registros; a coordenacao assume o acompanhamento pedagogico e de convivio; e a direcao aparece como instancia de escalonamento institucional quando o tema exige alinhamento maior. O envio inicial de documentos pode ocorrer pelo portal institucional, pelo email da secretaria ou presencialmente, conforme o tipo de documento e o grau de sensibilidade da informacao. A diretora geral do Colegio Horizonte e Helena Martins. A lideranca atende familias por agenda institucional. Direcao geral: direcao@colegiohorizonte.edu.br Coordenacao Fundamental II: fundamental2@colegiohorizonte.edu.br Coordenacao Ensino Medio: ensinomedio@colegiohorizonte.edu.br. A diretora participa de encontros institucionais com familias ao longo do ano, especialmente nas reunioes de acolhimento, eventos gerais e marcos bimestrais de acompanhamento da comunidade escolar.
- `python_functions`: status 200, latency 5107.7ms, keyword pass `True`, quality `100`, used_llm `True`, llm_stages `answer_verifier_judge`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `python_functions_prefers_deterministic`, reason `python_functions_native_structured:institution`
  answer: Na base publica do Colegio Horizonte, a trilha institucional fica mais clara quando secretaria, coordenacao, direcao e canais oficiais aparecem como etapas complementares de encaminhamento e protocolo. Na pratica, a secretaria funciona como porta de entrada operacional para documentos, orientacoes iniciais e registros; a coordenacao assume o acompanhamento pedagogico e de convivio; e a direcao aparece como instancia de escalonamento institucional quando o tema exige alinhamento maior. O envio inicial de documentos pode ocorrer pelo portal institucional, pelo email da secretaria ou presencialmente, conforme o tipo de documento e o grau de sensibilidade da informacao. A diretora geral do Colegio Horizonte e Helena Martins. A lideranca atende familias por agenda institucional. Direcao geral: direcao@colegiohorizonte.edu.br Coordenacao Fundamental II: fundamental2@colegiohorizonte.edu.br Coordenacao Ensino Medio: ensinomedio@colegiohorizonte.edu.br. A diretora participa de encontros institucionais com familias ao longo do ano, especialmente nas reunioes de acolhimento, eventos gerais e marcos bimestrais de acompanhamento da comunidade escolar.
- `llamaindex`: status 200, latency 16284.0ms, keyword pass `True`, quality `100`, used_llm `True`, llm_stages `answer_composition, structured_polish`, final_polish_applied `True`, final_polish_mode `light_polish`, final_polish_reason `llamaindex_documentary_synthesis`, reason `llamaindex_public_profile`
  answer: Na base publica do Colegio Horizonte, a trilha institucional fica mais clara quando secretaria, coordenacao, direcao e canais oficiais aparecem como etapas complementares de encaminhamento e protocolo. Na pratica, a secretaria funciona como porta de entrada operacional para documentos, orientacoes iniciais e registros; a coordenacao assume o acompanhamento pedagogico e de convivio; e a direcao aparece como instancia de escalonamento institucional quando o tema exige alinhamento maior. O envio inicial de documentos pode ocorrer pelo portal institucional, pelo email da secretaria ou presencialmente, conforme o tipo de documento e o grau de sensibilidade da informacao. A diretora geral do Colegio Horizonte e Helena Martins. A lideranca atende familias por agenda institucional. Direcao geral: direcao@colegiohorizonte.edu.br Coordenacao Fundamental II: fundamental2@colegiohorizonte.edu.br Coordenacao Ensino Medio: ensinomedio@colegiohorizonte.edu.br. A diretora participa de encontros institucionais com familias ao longo do ano, especialmente nas reunioes de acolhimento, eventos gerais e marcos bimestrais de acompanhamento da comunidade escolar.

Fontes:
- Governanca e Lideranca Institucional (v2026.2)
- FAQ de Secretaria e Vida Academica (v2026.3)
- `specialist_supervisor`: status 200, latency 1703.3ms, keyword pass `True`, quality `100`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `deterministic_answer`, reason `specialist_supervisor_local_public_canonical_lane:public_bundle.governance_protocol`
  answer: Na base publica do Colegio Horizonte, a trilha institucional fica mais clara quando secretaria, coordenacao, direcao e canais oficiais aparecem como etapas complementares de encaminhamento e protocolo. Na pratica, a secretaria funciona como porta de entrada operacional para documentos, orientacoes iniciais e registros; a coordenacao assume o acompanhamento pedagogico e de convivio; e a direcao aparece como instancia de escalonamento institucional quando o tema exige alinhamento maior. O envio inicial de documentos pode ocorrer pelo portal institucional, pelo e-mail da secretaria ou presencialmente, conforme o tipo de documento e o grau de sensibilidade da informacao. A diretora geral do Colegio Horizonte e Helena Martins. A lideranca atende familias por agenda institucional. Direcao geral: direcao@colegiohorizonte.edu.br Coordenacao Fundamental II: fundamental2@colegiohorizonte.edu.br Coordenacao Ensino Medio: ensinomedio@colegiohorizonte.edu.br. A diretora participa de encontros institucionais com familias ao longo do ano, especialmente nas reunioes de acolhimento, eventos gerais e marcos bimestrais de acompanhamento da comunidade escolar.

### Que logica institucional aparece quando a escola conecta comprovacao de saude, ausencia em atividade avaliativa, comunicacao com a familia e reorganizacao pedagogica?

- Slice: `public`
- Thread: `retrieval_5q_llm_compare_health_reorganization_open` turn `1`
- `langgraph`: status 200, latency 9410.1ms, keyword pass `True`, quality `100`, used_llm `True`, llm_stages `answer_composition, answer_verifier_judge`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `langgraph_candidate_synthesis_already_used`, reason `bundle publico canonico deve seguir lane publica mesmo se a classificacao superestimar autenticacao`
  answer: No Colégio Horizonte, a lógica institucional conecta a comprovação de saúde, a comunicação com a família e a reorganização pedagógica para garantir o bem-estar e o acompanhamento do estudante. Atestados médicos e justificativas formais são importantes para analisar ausências, solicitar segunda chamada ou adaptar temporariamente a rotina. Em casos de desempenho abaixo do esperado, a escola pode oferecer recuperação paralela, atividades orientadas ou avaliações substitutivas, sempre considerando a justificativa e o prazo estabelecido.
- `python_functions`: status 200, latency 9612.7ms, keyword pass `True`, quality `100`, used_llm `True`, llm_stages `answer_verifier_judge`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `python_functions_prefers_deterministic`, reason `python_functions_native_structured:institution`
  answer: No Colégio Horizonte, a lógica institucional conecta a comprovação de saúde, a comunicação com a família e a reorganização pedagógica para garantir o bem-estar e o acompanhamento do estudante. Atestados médicos e justificativas formais são importantes para analisar ausências, solicitar segunda chamada ou adaptar temporariamente a rotina. Em casos de desempenho abaixo do esperado, a escola pode oferecer recuperação paralela, atividades orientadas ou avaliações substitutivas, sempre com a família informada.
- `llamaindex`: status 200, latency 15465.3ms, keyword pass `True`, quality `100`, used_llm `True`, llm_stages `answer_verifier_judge`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `llamaindex_not_eligible`, reason `bundle publico canonico deve seguir lane publica mesmo se a classificacao superestimar autenticacao`
  answer: No Colégio Horizonte, a lógica institucional conecta a comprovação de saúde, a comunicação com a família e a reorganização pedagógica para garantir o bem-estar e o acompanhamento do estudante. Atestados médicos e justificativas formais são importantes para analisar ausências, solicitar segunda chamada ou adaptar temporariamente a rotina. Em casos de desempenho abaixo do esperado, a escola pode oferecer recuperação paralela, atividades orientadas ou avaliações substitutivas, sempre considerando a justificativa e o prazo orientado.
- `specialist_supervisor`: status 200, latency 14083.5ms, keyword pass `False`, quality `80`, used_llm `True`, llm_stages `specialist_execution`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `quality_first_path`, reason `specialist_supervisor_budget_direct:academic_specialist`
  errors: missing_expected_keyword
  answer: A lógica institucional do Colégio Horizonte conecta comprovantes de saúde, ausência em atividades avaliativas, comunicação com a família e reorganização pedagógica através de sua política acadêmica. Quando há uma ausência, a escola acompanha as justificativas (que incluiriam comprovantes de saúde). Em caso de falta isolada, o professor pode orientar a recomposição ou acompanhamento. Se a frequência de um componente curricular cai abaixo de 75%, o estudante entra em alerta acadêmico, e a coordenação pode acionar a família. A escola mantém um acompanhamento conjunto com a família e o estudante para justificativas, recorrência de ausências e a necessidade de planos de recomposição, que são parte da reorganização pedagógica. Além disso, a política de aprovação prevê suporte de recuperação (monitorias, plantões) quando a média fica abaixo da referência, o que indiretamente pode estar ligado à necessidade de reorganização pedagógica decorrente de ausências.

### Para uma familia que ainda esta conhecendo a escola, como a base publica deixa clara a fronteira entre o que ja se entende por calendarios e orientacoes abertas e o que so aparece com portal, login e conta vinculada?

- Slice: `public`
- Thread: `retrieval_5q_llm_compare_visibility_boundary_onboarding_open` turn `1`
- `langgraph`: status 200, latency 4908.1ms, keyword pass `True`, quality `88`, used_llm `True`, llm_stages `structured_polish, answer_verifier_judge`, final_polish_applied `True`, final_polish_mode `light_polish`, final_polish_reason `langgraph_public_noncanonical`, reason `bundle publico canonico deve seguir lane publica mesmo se a classificacao superestimar autenticacao`
  errors: unnecessary_clarification
  answer: Olá! Para as famílias que estão nos conhecendo, é importante saber que temos algumas frentes de comunicação. A Secretaria cuida de declarações, históricos e orientações administrativas. Já o Portal Institucional é o lugar para protocolos e envio digital de documentos, e o acesso é feito com login e senha. Se precisar de ajuda com as credenciais, a Secretaria ou o suporte digital podem auxiliar. Para o envio de documentos, você pode usar o portal, o email da secretaria ou ir presencialmente. Lembre-se que o chat aberto não é o canal para documentos completos ou dados sensíveis, ok?
- `python_functions`: status 200, latency 304.3ms, keyword pass `True`, quality `100`, used_llm `False`, llm_stages `none`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `python_functions_prefers_deterministic`, reason `python_functions_native_structured:institution`
  answer: Hoje a familia precisa entender quatro frentes publicas deste fluxo:
- Secretaria: recebe declaracoes, historico, atualizacoes cadastrais e orientacoes administrativas.
- Portal institucional: centraliza protocolo e envio digital inicial de documentos.
- Credenciais: login e senha do portal continuam sendo a base de acesso; se precisar recuperar acesso, o melhor caminho e a secretaria ou o suporte digital.
- Documentos: o envio inicial pode ser feito por portal institucional, email da secretaria ou secretaria presencial.
O chat aberto nao deve receber documentos completos ou dados sensiveis. Quando possivel, use o portal autenticado ou o email institucional.
- `llamaindex`: status 200, latency 6440.7ms, keyword pass `True`, quality `100`, used_llm `True`, llm_stages `answer_composition, structured_polish`, final_polish_applied `True`, final_polish_mode `light_polish`, final_polish_reason `llamaindex_documentary_synthesis`, reason `llamaindex_public_profile`
  answer: No calendario publico, o que costuma ficar aberto para familias sao marcos institucionais gerais e eventos coletivos. A fronteira pratica aparece assim: orientacoes abertas circulam no calendario publico, no portal institucional aberto e nos canais oficiais; o que so ganha detalhe depois do login e da conta vinculada no portal sao informacoes individuais por aluno, convites direcionados, protocolos, situacoes financeiras e acompanhamentos protegidos. Sempre que houver ajuste relevante no calendario de avaliacao, a escola atualiza o portal e reforca a comunicacao pelos canais oficiais. O ambiente digital amplia o atendimento, mas nao substitui todos os processos formais.
- `specialist_supervisor`: status 200, latency 14094.2ms, keyword pass `False`, quality `56`, used_llm `True`, llm_stages `specialist_execution`, final_polish_applied `False`, final_polish_mode `skip`, final_polish_reason `quality_first_path`, reason `specialist_supervisor_budget_safe_fallback`
  errors: missing_expected_keyword, strict_safe_fallback_excess
  answer: Nao consegui concluir essa resposta premium agora. Se quiser, reformule em uma frase mais direta ou repita em instantes.

