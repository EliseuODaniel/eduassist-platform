from __future__ import annotations

from typing import Any

from .flow_persistence import get_sqlite_flow_persistence

try:
    from crewai.flow.async_feedback.types import HumanFeedbackPending, PendingFeedbackContext
except Exception:  # pragma: no cover - defensive import
    HumanFeedbackPending = PendingFeedbackContext = None  # type: ignore[assignment]


APPROVAL_TERMS = {
    'approve',
    'approved',
    'aprovar',
    'aprovado',
    'aprovada',
    'sim',
    'ok',
    'prosseguir',
    'seguir',
    'autorizar',
    'autorizado',
}

REJECTION_TERMS = {
    'reject',
    'rejected',
    'reprovar',
    'reprovado',
    'reprovada',
    'nao',
    'não',
    'cancelar',
    'cancelado',
    'cancelada',
    'bloquear',
    'negar',
    'negado',
    'negada',
}


def async_feedback_supported() -> bool:
    return HumanFeedbackPending is not None and PendingFeedbackContext is not None


def normalize_feedback_text(value: Any) -> str:
    return ' '.join(str(value or '').strip().lower().split())


def feedback_is_approved(value: Any) -> bool:
    normalized = normalize_feedback_text(value)
    return normalized in APPROVAL_TERMS


def feedback_is_rejected(value: Any) -> bool:
    normalized = normalize_feedback_text(value)
    return normalized in REJECTION_TERMS


def load_pending_feedback_snapshot(*, slice_name: str, flow_id: str) -> dict[str, Any] | None:
    persistence = get_sqlite_flow_persistence(slice_name)
    if persistence is None:
        return None
    loaded = persistence.load_pending_feedback(flow_id)
    if loaded is None:
        return None
    state_data, context = loaded
    context_dict = context.to_dict() if hasattr(context, 'to_dict') else {}
    return {
        'flow_id': flow_id,
        'slice_name': slice_name,
        'state': state_data,
        'context': context_dict,
        'pending': True,
    }
