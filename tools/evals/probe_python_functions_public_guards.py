from __future__ import annotations

import asyncio
import json

from ai_orchestrator import kernel_runtime as kr
from ai_orchestrator.agent_kernel import KernelPlan
from ai_orchestrator.entity_resolution import ResolvedEntityHints
from ai_orchestrator.models import (
    AccessTier,
    IntentClassification,
    MessageResponseRequest,
    OrchestrationMode,
    OrchestrationPreview,
    QueryDomain,
    RetrievalBackend,
    UserContext,
)
from ai_orchestrator.python_functions_native_runtime import _should_use_python_functions_native_path


def _preview(*, mode: OrchestrationMode, domain: QueryDomain) -> OrchestrationPreview:
    return OrchestrationPreview(
        mode=mode,
        classification=IntentClassification(
            domain=domain,
            access_tier=AccessTier.public,
            confidence=0.7,
            reason="probe",
        ),
        retrieval_backend=RetrievalBackend.none,
        selected_tools=[],
        citations_required=False,
        needs_authentication=False,
        graph_path=[],
        risk_flags=[],
        reason="probe",
        output_contract="text",
    )


async def main() -> None:
    results: dict[str, object] = {}

    request_director = MessageResponseRequest(
        message="qual o nome do diretor da escola?",
        user=UserContext(authenticated=False),
    )
    preview_public = _preview(mode=OrchestrationMode.structured_tool, domain=QueryDomain.institution)
    contextual_director = await kr._maybe_contextual_public_direct_answer(
        request=request_director,
        analysis_message="Contexto recente: biblioteca aurora. Pedido atual: qual o nome do diretor da escola?",
        preview=preview_public,
        settings=None,
        school_profile={},
        conversation_context={
            "recent_messages": [
                {"sender_type": "user", "content": "qual o horario da biblioteca?"},
                {"sender_type": "assistant", "content": "A Biblioteca Aurora funciona das 7h30 as 18h00."},
            ]
        },
    )
    results["director_after_library_context"] = contextual_director

    request_library = MessageResponseRequest(
        message="como ela se chama?",
        user=UserContext(authenticated=False),
    )
    contextual_library = await kr._maybe_contextual_public_direct_answer(
        request=request_library,
        analysis_message="Contexto recente: biblioteca aurora. Pedido atual: como ela se chama?",
        preview=preview_public,
        settings=None,
        school_profile={},
        conversation_context={
            "recent_messages": [
                {"sender_type": "user", "content": "qual o horario da biblioteca?"},
                {"sender_type": "assistant", "content": "A Biblioteca Aurora funciona das 7h30 as 18h00."},
            ]
        },
    )
    results["library_pronoun_followup"] = contextual_library

    request_students = MessageResponseRequest(
        message="quantos alunos tem no colégio?",
        user=UserContext(authenticated=False),
    )
    preview_unknown = _preview(mode=OrchestrationMode.clarify, domain=QueryDomain.unknown)
    unpublished_students = kr._maybe_public_unpublished_direct_answer(
        request=request_students,
        preview=preview_unknown,
    )
    results["public_unpublished_students"] = unpublished_students

    plan = KernelPlan(
        stack_name="python_functions",
        mode="python_functions",
        slice_name="public",
        preview=preview_unknown,
        entities=ResolvedEntityHints(),
        execution_steps=[],
        plan_notes=[],
    )
    results["native_path_on_public_clarify"] = _should_use_python_functions_native_path(plan)

    assert contextual_director is None
    assert contextual_library == "A biblioteca se chama Biblioteca Aurora e funciona de segunda a sexta, das 7h30 as 18h00."
    assert isinstance(unpublished_students, str) and "nao esta publicado oficialmente" in unpublished_students
    assert results["native_path_on_public_clarify"] is True

    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
