# Four-Path 40Q Three-Model Manual Analysis

Date: 2026-04-18

Dataset:
- `tests/evals/datasets/retrieval_40q_probe_cases.generated.20260417.final.json`

Models compared:
- `Gemma 4 E4B` local
- `Qwen3-4B-Instruct-2507` local
- `Gemini 2.5 Flash-Lite` cloud

Stacks compared:
- `langgraph`
- `python_functions`
- `llamaindex`
- `specialist_supervisor`

## Executive reading

The final 40Q battery supports a clear ranking when the comparison target is the best final user outcome across all four stacks.

1. `Gemini 2.5 Flash-Lite` produced the best system-level balance.
   - It completed `160/160` responses.
   - It reached the highest aggregate quality (`95.8`).
   - It was also the fastest model in the benchmark (`2845.4 ms` average across stacks).
2. `Qwen3-4B-Instruct-2507` was the best local-only operational profile.
   - It also completed `160/160`.
   - It kept strong average quality (`95.6`).
   - It was much faster than `Gemma`, though slower than `Gemini`.
3. `Gemma 4 E4B` remained the strongest model in institutionally delicate wording.
   - It achieved the highest isolated stack score with `LlamaIndex` (`96.8`).
   - It was the cleanest model in public known-unknown answers, pricing projection, and conservative boundary wording.
   - Its main weakness in this final comparison was operational fragility in two non-specialist runs, which reduced the aggregate result to `157/160`.

## Model-by-model reading

### Gemini 2.5 Flash-Lite

Main strengths:
- best global tradeoff between quality, completion, and latency;
- strongest recovery in prompts that required direct explanation instead of clarification, especially in `langgraph`;
- best overall specialist balance: `40/40`, `35/40` keyword pass, `96.5` average quality, `1961.2 ms`.

Main weakness:
- repeated surface leakage of structured output in some public explanatory answers, with responses beginning as `json { "answer_text": ... }` or fenced JSON-like content;
- this did not usually break factual grounding, but it is clearly worse for end-user experience than plain prose.

Interpretation:
- `Gemini` behaved like the best production model in the benchmark when the decision criterion values user-visible completion, fast turnaround, and stable behavior across stacks.

### Qwen3-4B-Instruct-2507

Main strengths:
- best local-only tradeoff;
- full benchmark completion (`160/160`);
- strong latency for a local model (`5073.6 ms` average across stacks);
- very solid in explanatory public answers and in stabilizing the non-specialist paths.

Main weakness:
- it compressed some institutionally sensitive answers more than desired;
- it lost quality in cases where the response needed stricter wording for public limits or official absence of information;
- in pricing projection it was the weakest of the three models because it made the answer less precise and less institutionally framed.

Interpretation:
- `Qwen` is the most practical local option when the deployment constraint is local-only operation and the decision criterion favors completion plus latency.

### Gemma 4 E4B

Main strengths:
- best semantic conservatism in institutionally delicate prompts;
- strongest wording in public pricing simulation and known-unknown answers;
- cleanest answer surface among the three, without the structured-output leakage seen in `Gemini`.

Main weakness:
- highest latency in the final benchmark (`15635.8 ms`);
- two non-specialist failures reduced global completion to `157/160`;
- the model remained usable and often semantically excellent, but less robust operationally in this final cross-stack run.

Interpretation:
- `Gemma` remains the best model when the priority is conservative institutional language and careful handling of public-answer boundaries, but it is no longer the best overall choice in the full benchmark.

## Representative cases

### Case A: public login boundary
Prompt:
- `Sem olhar meu caso particular, o que qualquer familia ve sem login e o que ja depende de autenticacao?`

Reading:
- `Gemini` was clearly the best model in `langgraph`, answering directly and correctly.
- `Gemma` failed in `langgraph` and `python_functions` in this benchmark.
- `Qwen` stayed up, but often shifted into clarification instead of answering directly.
- In `specialist_supervisor`, the three models behaved similarly and too defensively.

Conclusion:
- This case strongly favors `Gemini` on system-level robustness.

### Case B: protected documentary pending status
Prompt:
- `Sem sair do escopo do projeto, quero um retrato das pendencias documentais da Ana e do proximo passo para regularizar tudo.`

Reading:
- `Gemma` and `Qwen` were more explicit in the non-specialist stacks.
- `Gemini` was slightly shorter in those stacks, which cost keyword/rubric strength.
- In `specialist_supervisor`, `Gemini` matched `Gemma` in quality and preserved the needed concreteness.

Conclusion:
- `Gemini` is good enough here, but `Gemma` and `Qwen` had cleaner wording in some non-specialist paths.

### Case C: restricted teacher-manual query with insufficient evidence
Prompt:
- `Pensando no caso pratico, pelo manual interno do professor, qual e a regra para registro de avaliacoes e comunicacao com foco pedagogico?`

Reading:
- The best behavior is not to hallucinate and to acknowledge insufficient restricted evidence.
- `Gemma` and `Qwen` were generally stronger in keeping the “not found safely” stance with clearer next-step guidance.
- `Gemini` was still safe, but some answers became slightly less rubric-aligned because they softened the official insufficiency wording.

Conclusion:
- This case favors `Gemma`, with `Qwen` close behind.

### Case D: public pricing projection
Prompt:
- `Sem sair do escopo do projeto, pela referencia publica de precos, qual seria a matricula total e o valor mensal para 3 filhos?`

Reading:
- `Gemma` was the cleanest model and used the best institutional framing.
- `Gemini` answered correctly and kept the arithmetic grounded, but several paths leaked JSON-like formatting.
- `Qwen` was the weakest because it made the answer less precise in wording and, in one path, less useful in presentation.

Conclusion:
- `Gemma` is the best model in this case; `Gemini` is correct but cosmetically worse; `Qwen` is the weakest.

### Case E: public known-unknown about total teacher count
Prompt:
- `De forma bem objetiva, existe numero publico de professores na escola ou esse dado nao e informado oficialmente?`

Reading:
- `Gemma` was the strongest model in the four stacks because it used the clearest official known-unknown wording.
- `Gemini` was correct, but usually shorter and slightly less explicit.
- `Qwen` was also correct, but weaker in institutional phrasing.

Conclusion:
- This case favors `Gemma`.

### Case F: protected follow-up isolating one student
Prompt:
- `Continuando a consulta, isole a Ana e me mostre apenas as avaliacoes dela.`

Reading:
- In the three non-specialist stacks, the three models converged to the same correct answer.
- In `specialist_supervisor`, `Gemini` was better than `Gemma` and `Qwen`, because it at least gave a bounded explanation instead of the weaker premium-consolidation fallback.
- Even so, the non-specialist answer remained better than the specialist answer in this prompt.

Conclusion:
- This case favors `Gemini` within the specialist stack and shows that the model can improve follow-up handling, even when the architecture still constrains the final answer.

## Final conclusion for the benchmark

The most defensible reading of the final benchmark is:

- **Overall winner:** `Gemini 2.5 Flash-Lite + Specialist Supervisor`
- **Best local-only tradeoff:** `Qwen3-4B-Instruct-2507 + Specialist Supervisor`
- **Best semantic conservatism in institutionally delicate public wording:** `Gemma 4 E4B`, especially with `LlamaIndex` and `Specialist Supervisor`

This means the platform now has three different but legitimate takeaways:

1. If the goal is the best global benchmark result, use `Gemini`.
2. If the goal is local-only serving with strong operational balance, use `Qwen`.
3. If the goal is maximum caution in public institutional wording, `Gemma` still matters.
