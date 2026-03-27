# Framework Rollout Readiness Report

Date: 2026-03-27T17:29:34.690901+00:00

## Goal

Summarize what can be promoted now, by slice, before any canary or feature-flag rollout change.

## Candidate Engine

- candidate engine: `crewai`
- scorecard loaded: `True`
- scorecard enforced: `False`
- pilot health enforced: `False`
- gate eligible: `True`
- primary-stack native path passed: `True`
- configured slices: `public, support, workflow`
- promotable now: `(none)`
- recommended next promotions: `(none)`
- telegram chat allowlist count: `1`
- conversation allowlist count: `0`
- proposed CrewAI protected user-traffic HITL: `False`

## Per Slice

| Slice | Eligible | Configured | Live | Rollout | Allowlist Only | Pilot Live Gate | Reason |
| --- | --- | --- | --- | ---: | --- | --- | --- |
| `public` | `no` | `yes` | `yes` | `5%` | `no` | `no` | CrewAI pilot status is not available right now. |
| `protected` | `no` | `no` | `no` | `0%` | `no` | `no` | CrewAI pilot status is not available right now. |
| `support` | `no` | `yes` | `yes` | `100%` | `yes` | `no` | CrewAI pilot status is not available right now. |
| `workflow` | `no` | `yes` | `yes` | `100%` | `yes` | `no` | CrewAI pilot status is not available right now. |

## Gate Snapshot

```json
{
  "loaded": true,
  "generated_at": "2026-03-27T17:01:56.429893+00:00",
  "primary_engine": "crewai",
  "primary_score": 30,
  "primary_max_score": 30,
  "primary_stack_native_path_passed": true,
  "promotion_gate": {
    "eligible": true,
    "minimum_score_for_canary": 20,
    "primary_stack_native_path_required": true,
    "recommended_canary_slices": [
      "public",
      "protected",
      "support",
      "workflow"
    ],
    "blocked_canary_slices": [],
    "slice_eligibility": {
      "public": {
        "eligible": true,
        "reason": "public is allowed for crewai under the current scorecard gate."
      },
      "protected": {
        "eligible": true,
        "reason": "protected is allowed for crewai under the current scorecard gate."
      },
      "support": {
        "eligible": true,
        "reason": "support is allowed for crewai under the current scorecard gate."
      },
      "workflow": {
        "eligible": true,
        "reason": "workflow is allowed for crewai under the current scorecard gate."
      }
    }
  },
  "frameworks": {
    "langgraph": {
      "total_score": 30,
      "max_score": 30,
      "primary_stack_native_path_passed": true,
      "restart_recovery_passed": true,
      "crash_recovery_passed": true,
      "recommended_canary_slices": [
        "public",
        "protected",
        "support",
        "workflow"
      ],
      "blocked_canary_slices": [],
      "trace_sample": {
        "thread_id": "conversation:scorecard-topline-langgraph-1",
        "created_at": "2026-03-27T13:38:23.699812+00:00",
        "next_nodes": [],
        "task_names": [],
        "hitl_status": null,
        "state_route": "structured_tool",
        "checkpoint_id": "1f129e23-9f67-6ae0-8005-890a0437d5c8",
        "state_available": true,
        "state_slice_name": "public",
        "snapshot_metadata": {
          "step": 5,
          "source": "loop"
        },
        "checkpointer_backend": "postgres",
        "checkpointer_enabled": true,
        "task_interrupt_count": 0,
        "has_pending_interrupt": false,
        "top_level_interrupt_count": 0
      }
    },
    "crewai": {
      "total_score": 30,
      "max_score": 30,
      "primary_stack_native_path_passed": true,
      "restart_recovery_passed": true,
      "crash_recovery_passed": true,
      "trace_sample": {
        "request": {
          "slice_name": "support",
          "flow_enabled": true,
          "flow_state_id": "2cc869d9-85cf-405a-a336-d4ea317ea22f",
          "validation_stack": [
            "flow_router",
            "deterministic_support"
          ]
        },
        "response": {
          "latency_ms": 60.7
        },
        "live": {
          "status": {
            "service": "ai-orchestrator-crewai",
            "ready": true,
            "crewaiInstalled": true,
            "crewaiVersion": "1.12.2",
            "slice": "public+protected+workflow+support",
            "mode": "pilot",
            "googleModel": "gemini-2.5-flash-preview",
            "llmConfigured": false,
            "capabilities": [
              "public-shadow-flow",
              "protected-shadow-flow",
              "workflow-shadow-flow",
              "support-shadow-flow",
              "isolated-dependencies",
              "planner-composer-judge",
              "flow-state-routing",
              "flow-state-persistence",
              "task-trace-telemetry",
              "task-guardrails",
              "agentic-rendering-for-support-workflow",
              "crewai-hitl-internal",
              "crewai-hitl-user-traffic"
            ],
            "flowStateDir": "/workspace/artifacts/crewai-flow-state",
            "crewaiHitlEnabled": true,
            "crewaiHitlDefaultSlices": "protected",
            "crewaiHitlUserTrafficEnabled": false,
            "crewaiHitlUserTrafficSlices": "protected"
          },
          "public": {
            "conversation_id": "scorecard-crewai-public-live-1",
            "slice_name": "public",
            "normalized_message": "qual o horario da biblioteca?",
            "crewai_installed": true,
            "crewai_version": "1.12.2",
            "agent_roles": [],
            "task_names": [],
            "latency_ms": 34.3,
            "plan": null,
            "answer": {
              "answer_text": "A Biblioteca Aurora atende ao publico de segunda a sexta, das 7h30 as 18h00.",
              "citations": [
                "feature.1"
              ]
            },
            "judge": {
              "valid": true,
              "reason": "deterministic_fast_path",
              "revision_needed": false
            },
            "evidence_sources": [
              "feature.1"
            ],
            "deterministic_backstop_used": true,
            "validation_stack": [
              "flow_router",
              "deterministic_fast_path"
            ],
            "flow_enabled": true,
            "flow_state_id": "public:telegram:conversation:scorecard-crewai-public-live-1",
            "event_listener": {
              "counts": {},
              "events": [],
              "summary": {},
              "task_trace": {
                "tasks": {},
                "agents": {},
                "crews": {},
                "tools": {}
              }
            },
            "event_summary": {},
            "task_trace": {
              "tasks": {},
              "agents": {},
              "crews": {},
              "tools": {}
            }
          },
          "protected": {
            "conversation_id": "scorecard-crewai-protected-live-1",
            "slice_name": "protected",
            "normalized_message": "qual situacao de documentacao do lucas?",
            "resolved_student_name": "Lucas Oliveira",
            "flow_enabled": true,
            "flow_state_id": "protected:telegram:conversation:scorecard-crewai-protected-live-1",
            "event_listener": {
              "counts": {},
              "events": [],
              "summary": {},
              "task_trace": {
                "tasks": {},
                "agents": {},
                "crews": {},
                "tools": {}
              }
            },
            "event_summary": {},
            "task_trace": {
              "tasks": {},
              "agents": {},
              "crews": {},
              "tools": {}
            },
            "crewai_installed": true,
            "crewai_version": "1.12.2",
            "agent_roles": [],
            "task_names": [],
            "latency_ms": 249.4,
            "plan": {
              "intent": "student_admin",
              "student_name": "Lucas Oliveira",
              "student_id": "53d70582-36f3-4052-b29c-ede23dec42ff",
              "domain": "institution",
              "attribute": "documents",
              "needs_clarification": false,
              "clarification_question": null,
              "relevant_sources": [
                "admin.overview"
              ]
            },
            "answer": {
              "answer_text": "A situacao documental de Lucas Oliveira hoje esta regular e completa.",
              "citations": [
                "admin.overview"
              ]
            },
            "judge": {
              "valid": true,
              "reason": "deterministic_fast_path",
              "revision_needed": false
            },
            "evidence_sources": [
              "admin.overview",
              "admin.check.3",
              "admin.check.2",
              "admin.check.1",
              "assessments.overview",
              "attendance.overview",
              "identity.student.1",
              "financial.overview"
            ],
            "deterministic_backstop_used": true,
            "validation_stack": [
              "flow_router",
              "deterministic_fast_path"
            ]
          },
          "support": {
            "slice_name": "support",
            "conversation_id": "scorecard-crewai-support-live-1",
            "normalized_message": "quero falar com a secretaria",
            "flow_enabled": true,
            "flow_state_id": "support:telegram:conversation:scorecard-crewai-support-live-1",
            "flow_state_persisted": true,
            "active_ticket_code": "ATD-20260327-3AB07787",
            "active_queue_name": "secretaria",
            "latency_ms": 61.4,
            "validation_stack": [
              "operation_result",
              "deterministic_backstop"
            ],
            "answer": {
              "answer_text": "Sua solicitacao ja estava registrada na fila de secretaria. Protocolo: ATD-20260327-3AB07787. Status atual: queued."
            },
            "crewai_installed": true,
            "agent_roles": [],
            "task_names": [],
            "event_listener": {
              "counts": {},
              "events": [],
              "summary": {},
              "task_trace": {
                "tasks": {},
                "agents": {},
                "crews": {},
                "tools": {}
              }
            },
            "event_summary": {},
            "task_trace": {
              "tasks": {},
              "agents": {},
              "crews": {},
              "tools": {}
            },
            "judge": {
              "valid": true,
              "reason": "llm_unavailable_backstop",
              "revision_needed": false
            },
            "deterministic_backstop_used": true,
            "crewai_version": "1.12.2",
            "queue_name": "secretaria",
            "created": false
          },
          "workflow": {
            "slice_name": "workflow",
            "conversation_id": "scorecard-crewai-workflow-live-1",
            "normalized_message": "quero agendar uma visita na quinta a tarde",
            "workflow_type": "visit",
            "flow_enabled": true,
            "flow_state_id": "workflow:telegram:conversation:scorecard-crewai-workflow-live-1",
            "flow_state_persisted": true,
            "active_protocol_code": "VIS-20260327-D5147C",
            "active_workflow_type": "visit_booking",
            "latency_ms": 70.5,
            "validation_stack": [
              "operation_result",
              "deterministic_backstop"
            ],
            "answer": {
              "answer_text": "Pedido de visita registrado para o Colegio Horizonte. Protocolo: VIS-20260327-D5147C. Preferencia informada: 02/04/2026 - tarde. Fila responsavel: admissoes. Ticket operacional: ATD-20260327-286F7834. A equipe comercial valida a janela e retorna com a confirmacao."
            },
            "crewai_installed": true,
            "agent_roles": [],
            "task_names": [],
            "event_listener": {
              "counts": {},
              "events": [],
              "summary": {},
              "task_trace": {
                "tasks": {},
                "agents": {},
                "crews": {},
                "tools": {}
              }
            },
            "event_summary": {},
            "task_trace": {
              "tasks": {},
              "agents": {},
              "crews": {},
              "tools": {}
            },
            "judge": {
              "valid": true,
              "reason": "llm_unavailable_backstop",
              "revision_needed": false
            },
            "deterministic_backstop_used": true,
            "crewai_version": "1.12.2"
          }
        }
      },
      "recommended_canary_slices": [
        "public",
        "protected",
        "support",
        "workflow"
      ],
      "blocked_canary_slices": [],
      "blocked_reasons": {}
    }
  }
}
```
