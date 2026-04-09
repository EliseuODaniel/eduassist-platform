from __future__ import annotations

import asyncio
from types import SimpleNamespace

from ai_orchestrator.llamaindex_kernel_runtime import (
    _maybe_contextual_public_direct_answer,
    _should_skip_contextual_replan_for_authenticated_combo_followup,
)
from ai_orchestrator.models import AccessTier


def test_contextual_public_direct_answer_prioritizes_canonical_lane_over_fast_public(monkeypatch) -> None:
    monkeypatch.setattr(
        'ai_orchestrator.llamaindex_kernel_runtime.match_public_canonical_lane',
        lambda message: 'public_bundle.process_compare' if 'rematricula' in message else None,
    )
    monkeypatch.setattr(
        'ai_orchestrator.llamaindex_kernel_runtime.compose_public_canonical_lane_answer',
        lambda lane, profile=None: 'Comparacao canonica de processo.' if lane == 'public_bundle.process_compare' else None,
    )
    monkeypatch.setattr(
        'ai_orchestrator.llamaindex_kernel_runtime.rt._llm_forced_mode_enabled',
        lambda **kwargs: False,
    )
    monkeypatch.setattr(
        'ai_orchestrator.llamaindex_kernel_runtime.rt._compose_contextual_public_boundary_answer',
        lambda **kwargs: None,
    )
    monkeypatch.setattr(
        'ai_orchestrator.llamaindex_kernel_runtime.rt._compose_contextual_public_timeline_followup_answer',
        lambda **kwargs: None,
    )
    monkeypatch.setattr(
        'ai_orchestrator.llamaindex_kernel_runtime.rt._is_public_timeline_query',
        lambda message: False,
    )
    monkeypatch.setattr(
        'ai_orchestrator.llamaindex_kernel_runtime.rt._should_prefer_raw_public_followup_message',
        lambda **kwargs: False,
    )
    monkeypatch.setattr(
        'ai_orchestrator.llamaindex_kernel_runtime.rt._must_preserve_contextual_public_followup_message',
        lambda **kwargs: False,
    )
    monkeypatch.setattr(
        'ai_orchestrator.llamaindex_kernel_runtime.rt._is_service_routing_query',
        lambda message: True,
    )
    monkeypatch.setattr(
        'ai_orchestrator.llamaindex_kernel_runtime.rt._has_public_multi_intent_signal',
        lambda message: True,
    )
    monkeypatch.setattr(
        'ai_orchestrator.llamaindex_kernel_runtime.rt._is_public_timeline_lifecycle_query',
        lambda message: False,
    )
    monkeypatch.setattr(
        'ai_orchestrator.llamaindex_kernel_runtime.rt._is_public_year_three_phase_query',
        lambda message: False,
    )
    monkeypatch.setattr(
        'ai_orchestrator.llamaindex_kernel_runtime.rt._is_access_scope_query',
        lambda message: False,
    )
    monkeypatch.setattr(
        'ai_orchestrator.llamaindex_kernel_runtime.rt._base_profile_supports_fast_public_answer',
        lambda **kwargs: True,
    )
    monkeypatch.setattr(
        'ai_orchestrator.llamaindex_kernel_runtime.rt._try_public_channel_fast_answer',
        lambda **kwargs: 'Resposta publica generica.',
    )
    monkeypatch.setattr(
        'ai_orchestrator.llamaindex_kernel_runtime.rt._message_matches_term',
        lambda normalized, term: False,
    )
    monkeypatch.setattr(
        'ai_orchestrator.llamaindex_kernel_runtime.rt._normalize_text',
        lambda message: str(message).lower(),
    )

    request = SimpleNamespace(
        message='Compare rematricula, transferencia e cancelamento destacando o que muda na pratica.',
        user=SimpleNamespace(authenticated=True),
    )
    preview = SimpleNamespace(
        classification=SimpleNamespace(access_tier=AccessTier.public),
    )

    answer = asyncio.run(
        _maybe_contextual_public_direct_answer(
            request=request,
            analysis_message=request.message,
            preview=preview,
            settings=SimpleNamespace(),
            school_profile={'school_name': 'Colegio Horizonte'},
            conversation_context=None,
        )
    )

    assert answer == 'Comparacao canonica de processo.'


def test_contextual_public_direct_answer_short_circuits_objective_service_routing_bundle(monkeypatch) -> None:
    monkeypatch.setattr(
        'ai_orchestrator.llamaindex_kernel_runtime.rt._llm_forced_mode_enabled',
        lambda **kwargs: False,
    )
    monkeypatch.setattr(
        'ai_orchestrator.llamaindex_kernel_runtime.rt._compose_contextual_public_boundary_answer',
        lambda **kwargs: None,
    )
    monkeypatch.setattr(
        'ai_orchestrator.llamaindex_kernel_runtime.rt._compose_contextual_public_timeline_followup_answer',
        lambda **kwargs: None,
    )
    monkeypatch.setattr(
        'ai_orchestrator.llamaindex_kernel_runtime.match_public_canonical_lane',
        lambda message: None,
    )
    monkeypatch.setattr(
        'ai_orchestrator.llamaindex_kernel_runtime.rt._is_public_timeline_query',
        lambda message: False,
    )
    monkeypatch.setattr(
        'ai_orchestrator.llamaindex_kernel_runtime.rt._should_prefer_raw_public_followup_message',
        lambda **kwargs: False,
    )
    monkeypatch.setattr(
        'ai_orchestrator.llamaindex_kernel_runtime.rt._must_preserve_contextual_public_followup_message',
        lambda **kwargs: False,
    )
    monkeypatch.setattr(
        'ai_orchestrator.llamaindex_kernel_runtime.rt._is_direct_service_routing_bundle_query',
        lambda message: 'direcao' in str(message).lower() and 'financeiro' in str(message).lower(),
    )
    monkeypatch.setattr(
        'ai_orchestrator.llamaindex_kernel_runtime.rt._compose_service_routing_answer',
        lambda profile, message, conversation_context=None: 'Resposta curta de canais por assunto.',
    )
    monkeypatch.setattr(
        'ai_orchestrator.llamaindex_kernel_runtime.rt._base_profile_supports_fast_public_answer',
        lambda **kwargs: True,
    )
    monkeypatch.setattr(
        'ai_orchestrator.llamaindex_kernel_runtime.rt._try_public_channel_fast_answer',
        lambda **kwargs: 'Resposta publica rica demais.',
    )

    request = SimpleNamespace(
        message='Por qual canal eu falo com o setor de bolsas, com o financeiro e com a direcao da escola. Seja objetivo e grounded.',
        user=SimpleNamespace(authenticated=False),
    )
    preview = SimpleNamespace(
        classification=SimpleNamespace(access_tier=AccessTier.public),
    )

    answer = asyncio.run(
        _maybe_contextual_public_direct_answer(
            request=request,
            analysis_message=request.message,
            preview=preview,
            settings=SimpleNamespace(),
            school_profile={'school_name': 'Colegio Horizonte'},
            conversation_context=None,
        )
    )

    assert answer == 'Resposta curta de canais por assunto.'


def test_skip_contextual_replan_for_authenticated_admin_finance_combo_followup() -> None:
    request = SimpleNamespace(
        message='Se nada estiver bloqueando, fala isso de forma direta.',
        user=SimpleNamespace(authenticated=True),
    )
    conversation_context = {
        'recent_messages': [
            {'sender_type': 'user', 'content': 'Resume documentacao, cadastro e faturas em aberto da Ana.'},
            {'sender_type': 'assistant', 'content': 'Panorama combinado de documentacao e financeiro da Ana Oliveira.'},
        ]
    }

    assert _should_skip_contextual_replan_for_authenticated_combo_followup(
        request=request,
        conversation_context=conversation_context,
    ) is True


def test_skip_contextual_replan_does_not_trigger_without_combo_context() -> None:
    request = SimpleNamespace(
        message='Se nada estiver bloqueando, fala isso de forma direta.',
        user=SimpleNamespace(authenticated=True),
    )

    assert _should_skip_contextual_replan_for_authenticated_combo_followup(
        request=request,
        conversation_context={'recent_messages': [{'sender_type': 'user', 'content': 'Quando comecam as aulas?'}]},
    ) is False
