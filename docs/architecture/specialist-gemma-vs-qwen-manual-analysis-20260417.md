# Specialist Gemma vs Qwen Manual Analysis

Date: 2026-04-17

Scope:

- stack avaliada: `specialist_supervisor`
- baseline operacional final: `gemma4e4b_local_postfix`
- experimento: `qwen3_4b_instruct_local`
- dataset: [specialist_model_ab_cases.20260417.json](/home/edann/projects/eduassist-platform/tests/evals/datasets/specialist_model_ab_cases.20260417.json)
- relatório automatizado: [specialist-gemma-vs-qwen-ab-report-20260417.md](/home/edann/projects/eduassist-platform/docs/architecture/specialist-gemma-vs-qwen-ab-report-20260417.md)

## Leitura executiva

O resultado final desta rodada não é mais o mesmo da primeira passada crua do A/B.

Na fotografia intermediária, o `Qwen3-4B-Instruct-2507 Q5_K_M` parecia melhor do que o `Gemma 4 E4B Q4_K_M` porque:

- ficou muito mais rápido;
- evitou `timeouts`;
- e evidenciou vários resíduos arquiteturais do `specialist_supervisor`.

Depois que esses resíduos foram corrigidos e a arquitetura ganhou o `answer surface refiner` validado, o quadro final mudou:

- `gemma4e4b_local_postfix`: `15/15 ok`, `keyword_pass 15/15`, `quality_avg 100.0`
- `qwen3_4b_instruct_local`: `15/15 ok`, `keyword_pass 8/15`, `quality_avg 84.3`

Conclusão humana final:

- o `Qwen` continua sendo um excelente profile experimental de baixa latência;
- mas o `Gemma` endurecido ficou claramente melhor em qualidade conversacional agregada dentro da arquitetura real do `specialist`;
- portanto, a recomendação final do repositório continua sendo manter `Gemma` como baseline e `Qwen` como feature flag experimental.

## O que realmente mudou nesta wave

O ganho não veio de trocar o modelo e sim de melhorar a arquitetura da resposta final. A stack agora:

- preserva melhor carryover e follow-up curto em trilhas protegidas;
- reconhece melhor bundles públicos multiassunto;
- corrige precedência de aluno nomeado, comparação protegida e agenda docente;
- e verbaliza respostas prontas via um `answer surface refiner` validado, em vez de devolver só templates rígidos.

Esse refino final trouxe um equilíbrio melhor entre:

- grounding;
- personalização;
- aderência à pergunta;
- e preservação de segurança.

## Onde o Gemma final ficou claramente melhor

### AB03 - follow-up da biblioteca

Pergunta:

`e que horas fecha?`

Gemma final:

- entendeu o carryover da biblioteca;
- respondeu diretamente `A biblioteca fecha às 18h00.`

Qwen:

- perdeu o contexto;
- caiu em `scope_boundary`.

Leitura humana:

- este é um ganho arquitetural importante, porque o usuário fez um follow-up curtíssimo e natural;
- a resposta do `Gemma` final ficou precisa, humana e proporcional à pergunta;
- a do `Qwen` ficou claramente errada para o contexto.

### AB06 - governança e inclusão

Pergunta:

`sem sair do escopo da escola, explique em linguagem simples como a direção formaliza pedidos de inclusão e por onde eu começo`

Gemma final:

- trouxe a resposta mais completa e mais institucionalmente útil;
- explicou canais, escalonamento e ponto de partida;
- ainda ficou longa, mas respondeu bem ao pedido.

Qwen:

- entregou um resumo mais curto e mais rápido;
- porém simplificou demais o fluxo e perdeu parte importante do protocolo.

Leitura humana:

- no estado final, o `Gemma` não só alcançou o `Qwen`; ele passou a entregar a melhor resposta.

### AB09 e AB10 - resumo acadêmico e follow-up protegido

Perguntas:

- `quero um resumo acadêmico do Lucas Oliveira`
- `agora foque só em matemática`

Gemma final:

- produziu o resumo acadêmico correto do aluno;
- manteve o contexto no follow-up;
- respondeu a matemática diretamente.

Qwen:

- em `AB09`, tratou a pergunta como se fosse documental pública;
- em `AB10`, caiu em `scope_boundary`.

Leitura humana:

- estes foram os casos mais importantes da rodada;
- eles mostram que, na arquitetura final, o `Gemma` deixou de ter o passivo mais grave da primeira rodada;
- e o `Qwen` passou a ficar claramente atrás no que mais importa para a experiência protegida.

### AB11 e AB12 - financeiro nomeado e comparação de frequência

Perguntas:

- `qual é o próximo vencimento da Ana Oliveira?`
- `compare a frequência do Lucas e da Ana de forma objetiva`

Gemma final:

- respeitou o aluno nomeado;
- produziu a comparação entre os dois alunos;
- respondeu de forma mais alinhada ao que foi pedido.

Qwen:

- ainda clarificou demais o financeiro nomeado;
- ainda colapsou a comparação de frequência para uma única visão.

Leitura humana:

- aqui o `Gemma` final ficou materialmente melhor;
- o problema já não é “modelo mais rápido ou mais lento”, mas “qual stack entrega a resposta certa no fluxo real”.

### AB15 - horário docente

Pergunta:

`sou professor, qual é meu horário de hoje e minhas turmas?`

Gemma final:

- devolveu horário e turmas;
- respondeu exatamente ao pedido.

Qwen:

- listou apenas turmas;
- deixou o horário de fora.

Leitura humana:

- o `Gemma` final ficou mais completo e mais aderente à pergunta.

## Onde eles ficaram equivalentes

Os dois modelos ficaram essencialmente empatados quando a stack já tinha:

- fato público simples;
- boundary externo bem decidido;
- handoff humano bem estruturado;
- ou resposta curta praticamente determinada antes do refino.

Casos representativos:

- `AB01` identidade institucional;
- `AB02` horário geral da biblioteca;
- `AB04` documentos de matrícula;
- `AB05` BNCC;
- `AB07` fora de escopo;
- `AB08` entidade externa;
- `AB13` disciplina mais exposta;
- `AB14` handoff humano.

Leitura humana:

- nesses casos, o ganho do modelo é pequeno porque a arquitetura já chega muito perto da resposta final antes da verbalização.

## O que o Qwen ainda faz melhor

O `Qwen` continua melhor em um ponto relevante:

- latência média e p95.

Leitura humana:

- para uso local exploratório, depuração e prototipagem, isso é valioso;
- ele continua sendo um bom candidato para piloto controlado ou fallback experimental;
- mas isso não compensa a perda de qualidade final observada nesta rodada.

## Conclusão final

O experimento A/B serviu para duas coisas diferentes:

1. mostrar que o `Qwen` é um profile local viável, rápido e útil para benchmark;
2. mostrar que a melhor saída para o produto não era trocar de modelo às cegas, e sim corrigir a arquitetura da stack e o tratamento da superfície final.

Depois dessas correções, o resultado final ficou claro:

- `Gemma` continua como melhor baseline operacional do `specialist_supervisor`;
- `Qwen` permanece como feature flag experimental;
- a principal vitória desta wave não foi “trocar de LLM”, mas construir um caminho de refino final mais robusto, mais humano e ainda seguro.

## Recomendação final

Para o repositório hoje:

- manter `gemma4e4b_local` como baseline/default;
- manter `qwen3_4b_instruct_local` como feature flag experimental;
- preservar o `answer surface refiner` como parte do baseline do `specialist_supervisor`;
- só reconsiderar uma troca de default se uma nova rodada A/B superar o `Gemma` final no mesmo dataset, na mesma stack e sob os mesmos contratos de segurança.
