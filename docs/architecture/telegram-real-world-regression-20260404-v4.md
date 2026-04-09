# Telegram Real-World Regression v4

Date: 2026-04-04

Scenarios replayed across the four paths:
- academic_finance_followup
- public_pricing_followup

## Summary

All four paths now pass the two critical real-world conversation sequences without the previous failures:
- no cross-domain leak from grades into attendance justification
- no public-pricing leak into finance/attendance followups
- no year-as-quantity bug on direct pricing questions
- no loss of `Ensino Medio` across pricing followups
- subject followup stays narrowed to `Historia`

## Human Reading

### langgraph
- Strongest overall UX balance.
- Academic/finance followup: good clarifying opener, good full grade list, good narrow History answer, good atestado answer, good finance answer.
- Pricing followup: all four turns stayed on Ensino Medio and produced the right public pricing simulation.

### python_functions
- Very strong and stable.
- Slightly more mechanical clarification wording than langgraph, but answers stayed correct and scoped.
- Pricing followup also preserved Ensino Medio correctly.

### llamaindex
- Improved substantially.
- Student activation opener is the most natural of the four.
- The old residuals are gone: atestado no longer leaks grades, and pricing followups keep Ensino Medio.
- Internal reasons still show some legacy path names like `llamaindex_public_profile`, but final user-facing answers are now good.

### specialist_supervisor
- Now behaves correctly on both sequences as well.
- Still the most operationally fragile path because remote pilot fallback can add latency, but user-facing outputs on these scenarios are good.
- Pricing followups stayed coherent and did not route into private finance.

## Remaining Residuals

- Clarification openers could still be a bit more concise and consistent across stacks.
- `specialist_supervisor` remains more exposed to remote timeout than the others, even though the fallback path now preserves answer quality much better.
- The regression suite should keep growing with new real Telegram escapes whenever they appear.
