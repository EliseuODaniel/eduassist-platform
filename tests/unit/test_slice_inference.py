from __future__ import annotations

from types import SimpleNamespace

from ai_orchestrator.slice_inference import infer_request_slice


def _request(message: str, *, authenticated: bool = False, role: str = 'anonymous') -> SimpleNamespace:
    return SimpleNamespace(
        message=message,
        user=SimpleNamespace(authenticated=authenticated, role=role),
    )


def test_public_bundle_stays_public() -> None:
    request = _request('Compare o calendario letivo, agenda de avaliacoes e manual de matricula para uma familia nova.')
    assert infer_request_slice(request) == 'public'


def test_admin_finance_combo_routes_protected() -> None:
    request = _request(
        'Resuma minha documentacao pendente e a situacao financeira que pode bloquear atendimento.',
        authenticated=True,
        role='guardian',
    )
    assert infer_request_slice(request) == 'protected'


def test_human_handoff_routes_support() -> None:
    request = _request('Quero falar com a secretaria humana agora.')
    assert infer_request_slice(request) == 'support'
