from __future__ import annotations

from ai_orchestrator.models import (
    AccessTier,
    IntentClassification,
    MessageResponseRequest,
    OrchestrationMode,
    OrchestrationPreview,
    QueryDomain,
    RetrievalBackend,
)
from ai_orchestrator import runtime as rt


def test_build_suggested_replies_supports_institution_preview_after_runtime_refactor() -> None:
    preview = OrchestrationPreview(
        mode=OrchestrationMode.structured_tool,
        classification=IntentClassification(
            domain=QueryDomain.institution,
            access_tier=AccessTier.public,
            confidence=0.95,
            reason="public_institution_test",
        ),
        retrieval_backend=RetrievalBackend.none,
        selected_tools=["get_public_school_profile"],
        reason="public_institution_test",
        output_contract="teste",
    )
    request = MessageResponseRequest(message="qual o horario da biblioteca?")

    replies = rt._build_suggested_replies(
        request=request,
        preview=preview,
        actor=None,
        school_profile={"name": "Colegio Horizonte"},
        conversation_context=None,
    )

    assert replies
    assert all(reply.text for reply in replies)
