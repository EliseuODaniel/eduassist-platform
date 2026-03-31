from __future__ import annotations

import asyncio
import json
from types import SimpleNamespace

from ai_orchestrator_specialist.models import (
    OperationalMemory,
    SpecialistSupervisorRequest,
    UserContext,
)
from ai_orchestrator_specialist.runtime import (
    SupervisorRunContext,
    _operational_memory_follow_up_answer,
    _resolve_turn_intent,
    _resolved_academic_student_grades_answer,
)


ACTOR = {
    "user_id": "guardian-1",
    "linked_students": [
        {
            "student_id": "stu-lucas",
            "full_name": "Lucas Oliveira",
            "can_view_academic": True,
            "can_view_finance": True,
        },
        {
            "student_id": "stu-ana",
            "full_name": "Ana Oliveira",
            "can_view_academic": True,
            "can_view_finance": True,
        },
    ],
}

ACADEMIC_SUMMARIES = {
    "Lucas Oliveira": {
        "student_name": "Lucas Oliveira",
        "grades": [
            {"subject_code": "HIS", "subject_name": "Historia", "score": "6.6"},
            {"subject_code": "HIS", "subject_name": "Historia", "score": "7.0"},
            {"subject_code": "MAT", "subject_name": "Matematica", "score": "8.2"},
        ],
    },
    "Ana Oliveira": {
        "student_name": "Ana Oliveira",
        "grades": [
            {"subject_code": "HIS", "subject_name": "Historia", "score": "9.0"},
            {"subject_code": "HIS", "subject_name": "Historia", "score": "8.0"},
        ],
    },
}


async def _fake_fetch_academic_summary_payload(ctx, *, student_name_hint: str | None = None):
    name = str(student_name_hint or "").strip()
    summary = ACADEMIC_SUMMARIES.get(name)
    if summary is None:
        return {"error": "student_not_found"}
    student = next(item for item in ACTOR["linked_students"] if item["full_name"] == name)
    return {"student": student, "summary": summary, "decision": {}}


async def main() -> None:
    import ai_orchestrator_specialist.runtime as specialist_runtime

    original_fetch = specialist_runtime._fetch_academic_summary_payload
    specialist_runtime._fetch_academic_summary_payload = _fake_fetch_academic_summary_payload
    try:
        ctx_pronoun = SupervisorRunContext(
            request=SpecialistSupervisorRequest(
                message="e quais as notas dele?",
                conversation_id="probe-1",
                user=UserContext(authenticated=True),
            ),
            settings=SimpleNamespace(),
            http_client=None,
            actor=ACTOR,
            conversation_context={},
            operational_memory=OperationalMemory(
                active_domain="finance",
                active_student_id="stu-lucas",
                active_student_name="Lucas Oliveira",
                active_topic="finance_summary",
            ),
            retrieval_advice=None,
            school_profile={},
            preview_hint={"classification": {"domain": "academic"}},
            resolved_turn=None,
            specialist_registry={},
        )
        ctx_pronoun.resolved_turn = _resolve_turn_intent(ctx_pronoun)
        answer_pronoun = await _resolved_academic_student_grades_answer(ctx_pronoun, ctx_pronoun.resolved_turn)

        ctx_subject = SupervisorRunContext(
            request=SpecialistSupervisorRequest(
                message="e de historia?",
                conversation_id="probe-2",
                user=UserContext(authenticated=True),
            ),
            settings=SimpleNamespace(),
            http_client=None,
            actor=ACTOR,
            conversation_context={},
            operational_memory=OperationalMemory(
                active_domain="academic",
                active_student_id="stu-lucas",
                active_student_name="Lucas Oliveira",
                active_subject="Historia",
                active_topic="grades",
            ),
            retrieval_advice=None,
            school_profile={},
            preview_hint={"classification": {"domain": "academic"}},
            resolved_turn=None,
            specialist_registry={},
        )
        answer_subject = await _operational_memory_follow_up_answer(ctx_subject)

        ctx_specific = SupervisorRunContext(
            request=SpecialistSupervisorRequest(
                message="qual a nota media do lucas em historia?",
                conversation_id="probe-3",
                user=UserContext(authenticated=True),
            ),
            settings=SimpleNamespace(),
            http_client=None,
            actor=ACTOR,
            conversation_context={},
            operational_memory=OperationalMemory(),
            retrieval_advice=None,
            school_profile={},
            preview_hint={"classification": {"domain": "academic"}},
            resolved_turn=None,
            specialist_registry={},
        )
        ctx_specific.resolved_turn = _resolve_turn_intent(ctx_specific)
        answer_specific = await _resolved_academic_student_grades_answer(ctx_specific, ctx_specific.resolved_turn)

        results = {
            "pronoun_followup_resolved_turn": ctx_pronoun.resolved_turn.model_dump(mode="json"),
            "pronoun_followup_answer": answer_pronoun.message_text if answer_pronoun else None,
            "subject_followup_answer": answer_subject.message_text if answer_subject else None,
            "specific_subject_answer": answer_specific.message_text if answer_specific else None,
        }

        assert answer_pronoun is not None and "Lucas Oliveira" in answer_pronoun.message_text
        assert answer_subject is not None and "Historia" in answer_subject.message_text and "Lucas Oliveira" in answer_subject.message_text
        assert answer_specific is not None and "Lucas Oliveira" in answer_specific.message_text and "Historia" in answer_specific.message_text

        print(json.dumps(results, ensure_ascii=False, indent=2))
    finally:
        specialist_runtime._fetch_academic_summary_payload = original_fetch


if __name__ == "__main__":
    asyncio.run(main())
