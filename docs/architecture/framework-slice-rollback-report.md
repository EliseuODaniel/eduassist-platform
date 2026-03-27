# Framework Slice Rollback Report

Date: 2026-03-27T15:39:44.122003+00:00

## Summary

- slice: `public`
- current rollout: `2%`
- rollback target: `1%`
- apply requested: `False`
- result: `passed`
- operator: `codex`
- reason: `Reverter public para o nivel anterior do canario`
- source: `history`
- env file: `artifacts/tmp-rollback.env`
- nested promotion report: `/home/edann/projects/eduassist-platform/docs/architecture/framework-slice-promotion-report.md`

## History Reference

```json
{
  "timestamp": "2026-03-27T15:37:33.016974+00:00",
  "slice": "public",
  "before_rollout_percent": 1,
  "after_rollout_percent": 2,
  "mode": "preflight",
  "apply": false,
  "result": "passed",
  "operator": "codex",
  "reason": "Expandir public de 1% para 2% apos estabilidade do canario",
  "returncode": 0,
  "env_file": "artifacts/tmp-slice.env",
  "proposed_slices": "public,support,workflow",
  "proposed_slice_rollouts": "public:2,support:100,workflow:100",
  "proposed_allowlist_slices": "support,workflow",
  "nested_report": "/home/edann/projects/eduassist-platform/docs/architecture/framework-rollout-preflight-report.md",
  "stdout": "/home/edann/projects/eduassist-platform/docs/architecture/framework-rollout-preflight-report.md\n/home/edann/projects/eduassist-platform/docs/architecture/framework-rollout-preflight-report.json\n/home/edann/projects/eduassist-platform/artifacts/framework-rollout-preflight-report.json\n",
  "stderr": ""
}
```
