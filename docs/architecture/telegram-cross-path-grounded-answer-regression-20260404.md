# Telegram Cross-Path Grounded Answer Regression - 2026-04-04

## Context

This regression focused on real Telegram failures observed in protected guardian conversations:

- student/entity carry-over was brittle across follow-up turns
- some replies leaked previous topics into new questions
- Telegram formatting degraded multiline grade summaries into ugly single-line markdown
- finance follow-ups sometimes parsed trailing words as part of the student name
- clarification-style replies were too mechanical and not adapted to the user's focus

## Root Causes

1. Final answer serving optimized too much for direct deterministic output and not enough for user-facing conversational adaptation.
2. Follow-up focus resolution relied on weak implicit memory for student/topic reuse.
3. Student name extraction tolerated trailing prompt fragments such as `Lucas Como`.
4. Telegram channel formatting did not normalize inline markdown bullet lists into readable plain text.
5. Clarification answers did not receive a grounded repair pass when the current focus was obvious from the recent thread.

## Fixes Applied

- Shared conversational focus resolver added in `conversation_answer_state.py`
- Shared final grounded answer layer strengthened in `grounded_answer_experience.py`
- Channel-specific Telegram formatting strengthened in `channel_reply_formatting.py`
- Follow-up student extraction tightened in `runtime.py`
- Clarification repair path added in `main.py`
- Supplemental direct focused drafts added for:
  - subject grade
  - all grades
  - finance summary
  - attendance justification

## Validation Sequence

Sequence replayed against all four stacks:

1. `do lucas oliveira então`
2. `quais as notas do lucas`
3. `quais as notas de história do lucas?`
4. `é atestado de ficar dormindo, serve?`
5. `e o financeiro do lucas como está?`

## Final Outcome

### Shared Result

All four stacks now:

- keep `Lucas Oliveira` as the active student across the follow-up sequence
- answer only the requested subject when asked about `História`
- do not leak grade content into the attendance-justification question
- answer the finance follow-up in the finance domain instead of misparsing `Lucas Como`
- render grade lists in readable multiline Telegram plain text

### Stack Notes

- `langgraph`
  - best overall conversational quality
  - final answer layer actively improves clarity and specificity

- `python_functions`
  - now preserves student context and answers both attendance justification and finance follow-up correctly
  - remains deterministic in the core tool path, with grounded repair only at the answer layer

- `llamaindex`
  - now behaves correctly on the full regression sequence
  - subject narrowing and finance follow-up are both correct

- `specialist_supervisor`
  - no longer gets stuck on the previous `História` answer
  - follow-up memory remains useful without leaking stale academic content

## User-Visible Examples After Fix

- `quais as notas de história do lucas?`
  - `A média parcial de Lucas Oliveira em História é 6,8/10.`

- `é atestado de ficar dormindo, serve?`
  - `Para justificar faltas, a escola aceita atestado médico ou odontológico formal. Um atestado de "ficar dormindo" não serve como justificativa válida.`

- `e o financeiro do lucas como está?`
  - `Lucas Oliveira está com 1 fatura(s) em aberto. A mais próxima está em R$ 1.450,00 e vence em 10/04/2026.`

