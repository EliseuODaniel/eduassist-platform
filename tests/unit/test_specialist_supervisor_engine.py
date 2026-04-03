from __future__ import annotations

from types import SimpleNamespace

from ai_orchestrator.engines.specialist_supervisor_engine import _local_public_canonical_lane_response
from ai_orchestrator.models import QueryDomain


def test_local_public_canonical_lane_response_handles_visibility_boundary() -> None:
    request = SimpleNamespace(message='Para quem chegou agora, que fronteira aparece entre orientacoes abertas nos canais da escola e aquilo que so ganha detalhe depois da conta vinculada?')
    response = _local_public_canonical_lane_response(
        request=request,
        lane='public_bundle.visibility_boundary',
    )
    assert response is not None
    assert response.classification.domain is QueryDomain.institution
    assert response.used_llm is False
    assert response.final_polish_mode == 'skip'
    assert response.final_polish_reason == 'deterministic_answer'
    lowered = response.message_text.lower()
    assert 'portal' in lowered
    assert 'login' in lowered
