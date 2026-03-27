# Framework Merge Preparation Report

Date: 2026-03-27T17:33:35.426556+00:00

## Summary

- classification: `ready`
- merge-ready: `True`
- source branch: `feature/two-stack-shadow-comparison`
- target branch: `origin/main`
- ahead of target: `95` commits
- behind target: `0` commits

## Preconditions

- release snapshot ready: `True`
- merge checklist ready: `True`
- working tree clean: `True`

## Diff Summary

```text
.env.example                                       |     7 +
 Makefile                                           |    10 +-
 apps/admin-web/app/auth/refresh/route.ts           |    30 +
 apps/admin-web/app/conversation-history-panel.tsx  |   207 +
 apps/admin-web/app/globals.css                     |   683 +-
 apps/admin-web/app/layout.tsx                      |     4 +-
 apps/admin-web/app/link-challenge-panel.tsx        |    16 +-
 apps/admin-web/app/not-found.tsx                   |     8 +-
 apps/admin-web/app/page.tsx                        |   751 +-
 apps/admin-web/lib/auth.ts                         |   285 +-
 apps/ai-orchestrator-crewai/Dockerfile             |    14 +
 apps/ai-orchestrator-crewai/pyproject.toml         |    19 +
 .../src/ai_orchestrator_crewai/__init__.py         |     1 +
 .../ai_orchestrator_crewai/agentic_rendering.py    |   191 +
 .../src/ai_orchestrator_crewai/crewai_hitl.py      |    78 +
 .../src/ai_orchestrator_crewai/flow_persistence.py |    43 +
 .../src/ai_orchestrator_crewai/guardrails.py       |   177 +
 .../src/ai_orchestrator_crewai/listeners.py        |   652 +
 .../src/ai_orchestrator_crewai/main.py             |   324 +
 .../src/ai_orchestrator_crewai/protected_flow.py   |   705 ++
 .../src/ai_orchestrator_crewai/protected_pilot.py  |   794 ++
 .../src/ai_orchestrator_crewai/public_flow.py      |   415 +
 .../src/ai_orchestrator_crewai/public_pilot.py     |   706 ++
 .../src/ai_orchestrator_crewai/support_flow.py     |   306 +
 .../src/ai_orchestrator_crewai/support_pilot.py    |   197 +
 .../src/ai_orchestrator_crewai/workflow_flow.py    |   424 +
 .../src/ai_orchestrator_crewai/workflow_pilot.py   |   266 +
 apps/ai-orchestrator-crewai/uv.lock                |  3279 +++++
 apps/ai-orchestrator/pyproject.toml                |     2 +
 .../src/ai_orchestrator/crewai/__init__.py         |     4 +
 .../src/ai_orchestrator/crewai/agents.py           |    30 +
 .../src/ai_orchestrator/crewai/flow.py             |    68 +
 .../src/ai_orchestrator/crewai/state.py            |    26 +
 .../src/ai_orchestrator/crewai/tasks.py            |    26 +
 .../src/ai_orchestrator/crewai_trace.py            |   118 +
 .../src/ai_orchestrator/engine_selector.py         |   665 +
 .../src/ai_orchestrator/engines/__init__.py        |     6 +
 .../src/ai_orchestrator/engines/base.py            |    28 +
 .../src/ai_orchestrator/engines/crewai_engine.py   |   491 +
 .../ai_orchestrator/engines/langgraph_engine.py    |    20 +
 apps/ai-orchestrator/src/ai_orchestrator/graph.py  |  1668 ++-
 .../src/ai_orchestrator/langgraph_runtime.py       |   253 +
 .../src/ai_orchestrator/langgraph_trace.py         |    89 +
 .../src/ai_orchestrator/llm_provider.py            |  1010 +-
 apps/ai-orchestrator/src/ai_orchestrator/main.py   |   426 +-
 apps/ai-orchestrator/src/ai_orchestrator/models.py |    14 +
 .../src/ai_orchestrator/public_agentic_engine.py   |   364 +
 .../ai-orchestrator/src/ai_orchestrator/runtime.py | 12167 +++++++++++++++++--
 apps/ai-orchestrator/src/ai_orchestrator/tools.py  |   254 +
 .../src/ai_orchestrator/trace_bridge.py            |   108 +
 apps/ai-orchestrator/uv.lock                       |    31 +
 ...e9a_add_visit_booking_and_institutional_requ.py |   131 +
 apps/api-core/src/api_core/contracts.py            |   364 +-
 apps/api-core/src/api_core/db/models/__init__.py   |     4 +-
 .../src/api_core/db/models/conversation.py         |    59 +-
 apps/api-core/src/api_core/main.py                 |   728 +-
 .../src/api_core/services/conversation_memory.py   |    92 +-
 apps/api-core/src/api_core/services/domain.py      |   582 +-
 .../api_core/services/institutional_workflows.py   |   711 ++
 apps/api-core/src/api_core/services/support.py     |   219 +
 .../src/api_core/services/telegram_link.py         |    26 +-
 apps/telegram-gateway/src/telegram_gateway/main.py |   107 +-
 data/corpus/public/calendario-letivo-2026.md       |     8 +
 data/corpus/public/contatos-e-canais-oficiais.md   |     3 +-
 data/corpus/public/governanca-e-lideranca.md       |    40 +
 data/corpus/public/indicadores-e-diferenciais.md   |    37 +
 .../corpus/public/manual-matricula-ensino-medio.md |     4 +
 data/corpus/public/proposta-pedagogica.md          |     5 +-
 data/corpus/public/tecnologia-e-canais.md          |     5 +-
 data/corpus/public/visitas-e-relacionamento.md     |    30 +
 docs/architecture/agentic-dual-track-plan.md       |   339 +
 docs/architecture/agentic-framework-comparison.md  |   380 +
 docs/architecture/crewai-best-practices-audit.md   |   104 +
 .../framework-crash-recovery-report.md             |    98 +
 .../framework-crewai-protected-hitl-report.json    |    32 +
 .../framework-crewai-protected-hitl-report.md      |    56 +
 ...amework-langgraph-user-traffic-hitl-report.json |   110 +
 ...framework-langgraph-user-traffic-hitl-report.md |   134 +
 .../framework-live-promotion-summary-report.json   |   101 +
 .../framework-live-promotion-summary-report.md     |    31 +
 .../framework-merge-preparation-report.json        |    19 +
 .../framework-merge-preparation-report.md          |   190 +
 .../framework-merge-release-checklist-report.json  |    70 +
 .../framework-merge-release-checklist-report.md    |    27 +
 docs/architecture/framework-native-scorecard.json  |   376 +
 docs/architecture/framework-native-scorecard.md    |   362 +
 ...ework-post-rollout-live-observation-report.json |   756 ++
 ...amework-post-rollout-live-observation-report.md |    46 +
 .../framework-primary-stack-flag-report.md         |    29 +
 ...k-protected-canary-live-observation-report.json |   645 +
 ...ork-protected-canary-live-observation-report.md |    66 +
 ...amework-recommended-slice-promotion-report.json |    28 +
 ...framework-recommended-slice-promotion-report.md |    15 +
 .../framework-release-snapshot-report.json         |   424 +
 .../framework-release-snapshot-report.md           |    49 +
 .../framework-restart-recovery-report.md           |    98 +
 .../framework-rollout-apply-report.json            |   173 +
 .../architecture/framework-rollout-apply-report.md |    35 +
 ...ork-rollout-changelog-normalization-report.json |    26 +
 ...ework-rollout-changelog-normalization-report.md |    16 +
 docs/architecture/framework-rollout-changelog.json |   184 +
 docs/architecture/framework-rollout-changelog.md   |    12 +
 .../framework-rollout-execution-report.json        |   852 ++
 .../framework-rollout-execution-report.md          |   142 +
 .../framework-rollout-preflight-report.json        |   243 +
 .../framework-rollout-preflight-report.md          |    44 +
 .../framework-rollout-readiness-report.json        |   425 +
 .../framework-rollout-readiness-report.md          |   385 +
 .../framework-slice-promotion-report.json          |    24 +
 .../framework-slice-promotion-report.md            |    35 +
 .../framework-slice-rollback-report.json           |    35 +
 .../framework-slice-rollback-report.md             |    40 +
 docs/architecture/framework-top-line-roadmap.md    |   403 +
 docs/architecture/institutional-copilot-roadmap.md |   188 +
 docs/architecture/telegram-recent-threads.json     |   239 +
 docs/architecture/telegram-recent-threads.md       |    37 +
 docs/architecture/telegram-thread-1649845499.json  |  2286 ++++
 docs/architecture/telegram-thread-1649845499.md    |  1524 +++
 docs/architecture/two-stack-comparison-plan.md     |   448 +
 .../two-stack-production-experiment.md             |   474 +
 ...wo-stack-shadow-extended-real-threads-report.md |   384 +
 .../two-stack-shadow-master-real-threads-report.md |   574 +
 .../two-stack-shadow-real-threads-report.md        |   206 +
 docs/architecture/two-stack-shadow-report.md       |   145 +
 ...two-stack-shadow-support-real-threads-report.md |   113 +
 .../two-stack-shadow-threads-report.md             |   203 +
 ...wo-stack-shadow-workflow-real-threads-report.md |   122 +
 .../two-stack-support-canary-live-check.md         |   181 +
 .../two-stack-workflow-canary-live-check.md        |    90 +
 infra/compose/compose.yaml                         |    56 +-
 infra/compose/opa/policy.rego                      |    38 +
 infra/compose/postgres/init/02-create-app-role.sh  |     6 +-
 tests/e2e/_common.py                               |    16 +-
 tests/e2e/adversarial_regression.py                |     2 +-
 tests/e2e/authz_regression.py                      |     2 +-
 tests/e2e/local_smoke.py                           |  2148 +++-
 .../datasets/framework_crash_recovery_cases.json   |   111 +
 .../framework_primary_stack_flag_cases.json        |   106 +
 .../datasets/framework_restart_recovery_cases.json |   111 +
 tests/evals/datasets/orchestrator_cases.json       |  2371 +++-
 tests/evals/datasets/two_stack_shadow_cases.json   |    75 +
 .../two_stack_shadow_extended_real_threads.json    |   203 +
 .../two_stack_shadow_master_real_threads.json      |   446 +
 .../datasets/two_stack_shadow_real_threads.json    |   107 +
 .../two_stack_shadow_support_real_threads.json     |    59 +
 tests/evals/datasets/two_stack_shadow_threads.json |   114 +
 .../two_stack_shadow_workflow_real_threads.json    |    51 +
 tests/evals/orchestrator_quality.py                |    39 +-
 tools/evals/apply_framework_rollout_promotion.py   |   483 +
 tools/evals/benchmark_crewai_protected_hitl.py     |   178 +
 tools/evals/benchmark_framework_crash_recovery.py  |   386 +
 .../evals/benchmark_framework_restart_recovery.py  |   400 +
 .../evals/benchmark_langgraph_user_traffic_hitl.py |   241 +
 .../evals/benchmark_primary_stack_feature_flag.py  |   216 +
 .../build_framework_live_promotion_summary.py      |   169 +
 tools/evals/build_framework_merge_preparation.py   |   178 +
 .../build_framework_merge_release_checklist.py     |   279 +
 ...uild_framework_post_rollout_live_observation.py |   196 +
 ..._framework_protected_canary_live_observation.py |   112 +
 tools/evals/build_framework_release_snapshot.py    |   266 +
 tools/evals/build_framework_rollout_readiness.py   |   169 +
 tools/evals/compare_orchestrator_stacks.py         |   682 ++
 tools/evals/execute_framework_rollout_promotion.py |   430 +
 tools/evals/export_telegram_thread.py              |   183 +
 tools/evals/list_recent_telegram_threads.py        |   193 +
 .../evals/normalize_framework_rollout_changelog.py |   102 +
 .../evals/preflight_framework_rollout_promotion.py |   382 +
 tools/evals/promote_framework_slice.py             |   328 +
 tools/evals/promote_recommended_framework_slice.py |   193 +
 tools/evals/rollback_framework_slice.py            |   184 +
 tools/evals/score_framework_native_capabilities.py |   593 +
 tools/ops/check_db_rls.py                          |    39 +-
 tools/ops/telegram_webhook.py                      |   159 +
 173 files changed, 57583 insertions(+), 1707 deletions(-)
```

## Recommended Next Actions

- open or finalize the merge from `feature/two-stack-shadow-comparison` into `origin/main`.
- keep protected blocked unless a separate protected promotion decision is made later.
