# Framework Rollout Changelog

| Date | Intent | Slice | Before | After | Mode | Result | Operator | Reason | Env File |
| --- | --- | --- | ---: | ---: | --- | --- | --- | --- | --- |
| `2026-03-27T16:01:18.904547+00:00` | `promotion` | `public` | `1%` | `2%` | `execute` | `failed` | `codex` | Expandir public de 1% para 2% conforme recomendacao do gate live | `.env` |
| `2026-03-27T15:39:44.095113+00:00` | `rollback` | `public` | `2%` | `1%` | `preflight` | `passed` | `codex` | Reverter public para o nivel anterior do canario | `artifacts/tmp-rollback.env` |
| `2026-03-27T15:37:33.016974+00:00` | `promotion` | `public` | `1%` | `2%` | `preflight` | `passed` | `codex` | Expandir public de 1% para 2% apos estabilidade do canario | `artifacts/tmp-slice.env` |
| `2026-03-27T15:33:33.005730+00:00` | `promotion` | `public` | `1%` | `2%` | `preflight` | `passed` | `legacy-unknown` | Legacy changelog entry normalized after operator/reason became required audit fields. | `artifacts/tmp-slice.env` |
