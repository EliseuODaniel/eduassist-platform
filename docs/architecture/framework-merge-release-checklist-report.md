# Framework Merge Release Checklist Report

Date: 2026-03-27T16:06:40.915801+00:00

## Summary

- classification: `ready`
- ready to merge/release: `True`
- passed checks: `12`
- failed checks: `0`

## Checklist

| Item | Status | Detail |
| --- | --- | --- |
| `git_clean` | `pass` | working tree differs only by governance report files. |
| `release_snapshot_exists` | `pass` | release snapshot JSON is present. |
| `release_snapshot_matches_head` | `pass` | snapshot commit matches HEAD exactly. |
| `release_snapshot_ready` | `pass` | {"ready_for_guarded_release": true, "classification": "ready", "errors": []} |
| `runtime_status_ready` | `pass` | status.ready=True |
| `services_healthy` | `pass` | all tracked services are healthy. |
| `scorecard_gate_loaded` | `pass` | {"loaded": true, "generated_at": "2026-03-27T14:38:46.020428+00:00", "primary_engine": "langgraph", "primary_score": 29, "primary_max_score": 30, "primary_stack_native_path_passed": true, "promotion_gate": {"eligible": true, "minimum_score_for_canary": 20, "primary_stack_native_path_required": true, "recommended_canary_slices": ["public", "protected", "support", "workflow"], "blocked_canary_slices": [], "slice_eligibility": {"public": {"eligible": true, "reason": "public is allowed for langgraph under the current scorecard gate."}, "protected": {"eligible": true, "reason": "protected is allowed for langgraph under the current scorecard gate."}, "support": {"eligible": true, "reason": "support is allowed for langgraph under the current scorecard gate."}, "workflow": {"eligible": true, "reason": "workflow is allowed for langgraph under the current scorecard gate."}}}, "frameworks": {"langgraph": {"total_score": 29, "max_score": 30, "primary_stack_native_path_passed": true, "restart_recovery_passed": true, "crash_recovery_passed": true, "recommended_canary_slices": ["public", "protected", "support", "workflow"], "blocked_canary_slices": [], "trace_sample": {"thread_id": "conversation:scorecard-topline-langgraph-1", "created_at": "2026-03-27T13:38:23.699812+00:00", "next_nodes": [], "task_names": [], "hitl_status": null, "state_route": "structured_tool", "checkpoint_id": "1f129e23-9f67-6ae0-8005-890a0437d5c8", "state_available": true, "state_slice_name": "public", "snapshot_metadata": {"step": 5, "source": "loop"}, "checkpointer_backend": "postgres", "checkpointer_enabled": true, "task_interrupt_count": 0, "has_pending_interrupt": false, "top_level_interrupt_count": 0}}, "crewai": {"total_score": 27, "max_score": 30, "primary_stack_native_path_passed": true, "restart_recovery_passed": true, "crash_recovery_passed": true, "trace_sample": {"request": {"slice_name": "support", "flow_enabled": true, "flow_state_id": "2cc869d9-85cf-405a-a336-d4ea317ea22f", "validation_stack": ["flow_router", "deterministic_support"]}, "response": {"latency_ms": 60.7}}, "recommended_canary_slices": ["public", "support", "workflow"], "blocked_canary_slices": ["protected"], "blocked_reasons": {"protected": "protected still trails LangGraph in operator-facing control primitives and should stay behind manual review."}}}} |
| `primary_stack_native_path_passed` | `pass` | primary_stack_native_path_passed=True |
| `live_promotion_summary_present` | `pass` | experimentLivePromotionSummary available. |
| `changelog_normalized` | `pass` | all changelog entries contain intent, operator, and reason. |
| `protected_blocked_for_crewai_candidate` | `pass` | protected remains blocked for crewai candidate engine. |
| `core_artifacts_present` | `pass` | framework-rollout-readiness-report.json=yes, framework-live-promotion-summary-report.json=yes, framework-native-scorecard.json=yes, framework-release-snapshot-report.json=yes |
