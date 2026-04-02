from __future__ import annotations

from types import SimpleNamespace

from ai_orchestrator.models import AccessTier, OrchestrationMode, QueryDomain
from ai_orchestrator.runtime import _should_polish_structured_answer


def _preview(*, reason: str, domain: QueryDomain = QueryDomain.institution) -> SimpleNamespace:
    return SimpleNamespace(
        mode=OrchestrationMode.structured_tool,
        reason=reason,
        needs_authentication=False,
        classification=SimpleNamespace(
            domain=domain,
            access_tier=AccessTier.public,
        ),
    )


def test_langgraph_public_canonical_lane_skips_polish() -> None:
    request = SimpleNamespace(channel=SimpleNamespace(value="telegram"))
    preview = _preview(reason="langgraph_public_canonical_lane:public_bundle.year_three_phases")
    assert _should_polish_structured_answer(preview=preview, request=request) is False


def test_public_institution_structured_answer_still_polishes_when_not_canonical_lane() -> None:
    request = SimpleNamespace(channel=SimpleNamespace(value="telegram"))
    preview = _preview(reason="structured_tool:public_profile")
    assert _should_polish_structured_answer(preview=preview, request=request) is True
