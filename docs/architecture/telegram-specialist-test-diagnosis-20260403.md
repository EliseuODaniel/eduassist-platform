# Telegram Specialist Test Diagnosis

Date: `2026-04-03`
Thread: `telegram:1649845499`
Serving path during capture: `langgraph`

## Overall read

The real Telegram session showed a stronger backbone than the raw user experience.

What worked well:
- broad protected academic family panorama
- broad protected family finance panorama
- broad grade listing for a named student
- attendance sensitivity answer reached the right domain

What failed materially:
- public onboarding-style family planning question misrouted to high-school curriculum/profile
- finance detail by named student failed
- explicit finance query for `Lucas Oliveira` misrouted into academic grades
- subject-specific narrowing for `Historia` did not apply
- upcoming assessments for `Ana` failed with broken entity extraction
- combined admin + finance prompt failed with broken entity extraction
- public comparative process question returned a generic documentary cluster answer instead of a comparison

## Highest-priority failures seen in real chat

1. `qual o valor da próxima fatura do lucas?`
- bad entity/slot handling
- system asked which student despite explicit reference

2. `qual o valor da próxima fatura do lucas oliveira?`
- critical domain misroute
- finance question returned academic grades

3. `qual a nota em história do lucas?`
- narrowing by subject did not apply
- system kept returning broad grade table

4. `Recorte só a Ana e me mostre as próximas provas, entregas ou avaliações...`
- broken entity extraction
- system interpreted phrase fragments as student target

5. `Minha documentação cadastral... administrativo ou financeiro?`
- broken entity extraction again
- combined admin+finance intent did not survive parsing

6. `rematrícula, transferência de entrada e cancelamento...`
- answer was generic and documentary
- did not actually compare the three processes

## Product judgment

Platform/architecture quality is ahead of current Telegram user experience.

If judged as engineering progress:
- around `8/10`

If judged as real Telegram experience in this session:
- around `5.5/10` to `6/10`

## Why switch to specialist now

The specialist path should be tested next because:
- it already performs better on tool-first protected SQL cases in recent controlled batteries
- it tends to produce more explicit structured summaries when the intent is resolved correctly
- we need a real-user comparison against the current `langgraph` default

## Test objective

Use a targeted runtime override for this chat only, with `specialist_supervisor`, and observe:
- whether protected finance detail by student improves
- whether protected admin+finance combined view improves
- whether subject-specific narrowing improves
- whether public comparative/documentary prompts improve or at least fail more honestly
