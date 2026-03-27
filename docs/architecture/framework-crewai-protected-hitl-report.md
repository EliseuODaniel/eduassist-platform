# CrewAI Protected HITL Report

Date: 2026-03-27T17:01:55.717709+00:00

## Goal

Validate that the CrewAI protected slice can pause for operator review, expose pending state, and resume with approve/reject outcomes on the same persisted flow id.

## Summary

- Passed: `2/2`
- All passed: `yes`

## Cases

| Case | Result | Evidence |
| --- | --- | --- |
| `crewai-protected-hitl-approved-1` | `passed` | started=`pending`, pending_before=`True`, pending_after=`False`, reason=`crewai_protected_review_approved` |
| `crewai-protected-hitl-rejected-1` | `passed` | started=`pending`, pending_before=`True`, pending_after=`False`, reason=`crewai_protected_review_rejected` |

## Raw JSON

```json
{
  "generated_at": "2026-03-27T17:01:55.717709+00:00",
  "summary": {
    "passed": 2,
    "total": 2,
    "all_passed": true
  },
  "cases": [
    {
      "case_id": "crewai-protected-hitl-approved-1",
      "message": "qual meu acesso? a que dados",
      "feedback": "approved",
      "passed": true,
      "started_status": "pending",
      "pending_before_resume": true,
      "pending_after_resume": false,
      "resumed_reason": "crewai_protected_review_approved",
      "resumed_text": "Voce esta autenticado aqui como Maria Oliveira. Sua conta esta vinculada a Lucas Oliveira, Ana Oliveira e pode consultar notas, frequencia, avaliacoes, documentacao e financeiro desses alunos."
    },
    {
      "case_id": "crewai-protected-hitl-rejected-1",
      "message": "qual situacao de documentacao do Lucas?",
      "feedback": "rejected",
      "passed": true,
      "started_status": "pending",
      "pending_before_resume": true,
      "pending_after_resume": false,
      "resumed_reason": "crewai_protected_review_rejected",
      "resumed_text": "Essa consulta protegida nao foi liberada apos a revisao humana, entao eu nao vou expor o dado por aqui. Feedback registrado: rejected."
    }
  ]
}
```
