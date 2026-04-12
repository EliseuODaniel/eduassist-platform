from __future__ import annotations

from types import SimpleNamespace

from ai_orchestrator.models import (
    AccessTier,
    IntentClassification,
    OrchestrationMode,
    OrchestrationPreview,
    QueryDomain,
    RetrievalBackend,
)
from ai_orchestrator.semantic_ingress_runtime import apply_semantic_ingress_preview
from eduassist_semantic_ingress.runtime import (
    _validated_conversation_act,
    IngressSemanticPlan,
    is_terminal_ingress_act,
    looks_like_high_confidence_public_school_faq,
    looks_like_language_preference_feedback,
    looks_like_opaque_short_input,
    looks_like_scope_boundary_candidate,
    looks_like_school_scope_message,
    normalize_ingress_text,
    resolve_semantic_ingress_with_provider,
    should_run_semantic_ingress_classifier,
)


def _preview() -> OrchestrationPreview:
    return OrchestrationPreview(
        mode=OrchestrationMode.structured_tool,
        classification=IntentClassification(
            domain=QueryDomain.institution,
            access_tier=AccessTier.public,
            confidence=0.62,
            reason="local_preview",
        ),
        retrieval_backend=RetrievalBackend.none,
        selected_tools=[],
        graph_path=["test"],
        reason="local_preview",
        output_contract="teste",
    )


def test_normalize_ingress_text_collapses_accents_and_noise() -> None:
    assert normalize_ingress_text("  Boa   Madrugá!!  ") == "boa madruga"


def test_normalize_ingress_text_preserves_non_latin_letters() -> None:
    assert normalize_ingress_text("Привет") == "привет"


def test_normalize_ingress_text_preserves_non_latin_marks() -> None:
    assert normalize_ingress_text("नमस्ते") == "नमस्ते"


def test_should_run_semantic_ingress_classifier_accepts_informal_greeting() -> None:
    assert (
        should_run_semantic_ingress_classifier(
            message="oooie, boa madruga",
            current_domain="institution",
            current_access_tier="public",
            current_mode="structured_tool",
        )
        is True
    )


def test_should_run_semantic_ingress_classifier_accepts_short_non_latin_message() -> None:
    assert (
        should_run_semantic_ingress_classifier(
            message="Привет",
            current_domain="institution",
            current_access_tier="authenticated",
            current_mode="structured_tool",
        )
        is True
    )


def test_should_run_semantic_ingress_classifier_accepts_language_preference_even_when_preview_looks_academic() -> None:
    assert (
        should_run_semantic_ingress_classifier(
            message="Por que admissions ta em ingles",
            current_domain="academic",
            current_access_tier="authenticated",
            current_mode="structured_tool",
        )
        is True
    )


def test_should_run_semantic_ingress_classifier_rejects_real_content_query() -> None:
    assert (
        should_run_semantic_ingress_classifier(
            message="bom comportamento",
            current_domain="institution",
            current_access_tier="public",
            current_mode="structured_tool",
        )
        is False
    )


def test_looks_like_language_preference_feedback_detects_metalinguistic_complaint() -> None:
    assert looks_like_language_preference_feedback("Quero que so fale portugues") is True
    assert looks_like_language_preference_feedback("Por que admissions ta em ingles") is True


def test_looks_like_language_preference_feedback_rejects_real_subject_query() -> None:
    assert looks_like_language_preference_feedback("qual a nota de ingles do Lucas?") is False


def test_looks_like_opaque_short_input_detects_low_signal_token() -> None:
    assert looks_like_opaque_short_input("rai") is True
    assert looks_like_opaque_short_input("hdirlff") is True


def test_looks_like_opaque_short_input_rejects_known_greeting_and_content() -> None:
    assert looks_like_opaque_short_input("oi") is False
    assert looks_like_opaque_short_input("bom dia") is False
    assert looks_like_opaque_short_input("notas") is False


def test_looks_like_school_scope_message_detects_school_policy_query() -> None:
    assert looks_like_school_scope_message("posso fumar maconha nessa escola?") is True
    assert looks_like_school_scope_message("qual a mensalidade da escola?") is True
    assert looks_like_school_scope_message("qual o melhor filme do ano?") is False


def test_looks_like_school_scope_message_detects_public_school_information_queries() -> None:
    assert looks_like_school_scope_message("Qual o horario da biblioteca?") is True
    assert looks_like_school_scope_message("qual contato do diretor?") is True
    assert looks_like_school_scope_message("Qual o proximo vencimento?") is True


def test_looks_like_high_confidence_public_school_faq_detects_public_faq_families() -> None:
    assert looks_like_high_confidence_public_school_faq("tem biblioteca nessa escola?") is True
    assert looks_like_high_confidence_public_school_faq("qual valor da matricula?") is True
    assert looks_like_high_confidence_public_school_faq("quando iniciam as aulas?") is True
    assert looks_like_high_confidence_public_school_faq("quais documentos preciso para matricula?") is True
    assert looks_like_high_confidence_public_school_faq("qual o proximo vencimento?") is False
    assert (
        looks_like_high_confidence_public_school_faq(
            "Explique a minha situacao financeira como se eu fosse leigo, separando mensalidade, taxa, atraso e desconto."
        )
        is False
    )


def test_looks_like_scope_boundary_candidate_detects_out_of_scope_question() -> None:
    assert looks_like_scope_boundary_candidate("Qual o melhor filme do ano?") is True
    assert looks_like_scope_boundary_candidate("Como faco lasanha?") is True
    assert looks_like_scope_boundary_candidate("Posso fumar maconha nessa escola?") is False
    assert looks_like_scope_boundary_candidate("Qual o horario da biblioteca?") is False
    assert looks_like_scope_boundary_candidate("qual contato do diretor?") is False


def test_resolve_semantic_ingress_with_provider_parses_structured_payload(monkeypatch) -> None:
    async def fake_text_call(**_kwargs) -> str:
        return (
            '{"conversation_act":"greeting","use_conversation_context":false,'
            '"confidence_bucket":"high","reason":"saudacao informal"}'
        )

    monkeypatch.setattr("eduassist_semantic_ingress.runtime._text_call", fake_text_call)

    import asyncio

    plan = asyncio.run(
        resolve_semantic_ingress_with_provider(
            settings=SimpleNamespace(),
            stack_label="python_functions",
            request_message="boa madruga",
            conversation_context=None,
            preview={"mode": "structured_tool", "domain": "institution", "access_tier": "public"},
        )
    )

    assert plan is not None
    assert plan.conversation_act == "greeting"
    assert plan.confidence_bucket == "high"
    assert plan.terminal_fast_path is True


def test_resolve_semantic_ingress_with_provider_coerces_language_preference_when_model_returns_input_clarification(
    monkeypatch,
) -> None:
    async def fake_text_call(**_kwargs) -> str:
        return (
            '{"conversation_act":"input_clarification","use_conversation_context":false,'
            '"confidence_bucket":"low","reason":"mensagem curta"}'
        )

    monkeypatch.setattr("eduassist_semantic_ingress.runtime._text_call", fake_text_call)

    import asyncio

    plan = asyncio.run(
        resolve_semantic_ingress_with_provider(
            settings=SimpleNamespace(),
            stack_label="langgraph",
            request_message="Por que admissions ta em ingles",
            conversation_context=None,
            preview={"mode": "structured_tool", "domain": "academic", "access_tier": "public"},
        )
    )

    assert plan is not None
    assert plan.conversation_act == "language_preference"
    assert plan.confidence_bucket == "high"
    assert "metalingu" in plan.reason


def test_resolve_semantic_ingress_with_provider_falls_back_to_input_clarification_for_opaque_short_input(
    monkeypatch,
) -> None:
    async def fake_text_call(**_kwargs) -> str | None:
        return None

    monkeypatch.setattr("eduassist_semantic_ingress.runtime._text_call", fake_text_call)

    import asyncio

    plan = asyncio.run(
        resolve_semantic_ingress_with_provider(
            settings=SimpleNamespace(),
            stack_label="python_functions",
            request_message="rai",
            conversation_context=None,
            preview={"mode": "structured_tool", "domain": "academic", "access_tier": "authenticated"},
        )
    )

    assert plan is not None
    assert plan.conversation_act == "input_clarification"
    assert plan.reason == "opaque_short_input_fallback"


def test_resolve_semantic_ingress_with_provider_falls_back_to_input_clarification_for_public_opaque_short_input(
    monkeypatch,
) -> None:
    async def fake_text_call(**_kwargs) -> str | None:
        return None

    monkeypatch.setattr("eduassist_semantic_ingress.runtime._text_call", fake_text_call)

    import asyncio

    plan = asyncio.run(
        resolve_semantic_ingress_with_provider(
            settings=SimpleNamespace(),
            stack_label="python_functions",
            request_message="rai",
            conversation_context=None,
            preview={"mode": "structured_tool", "domain": "institution", "access_tier": "public"},
        )
    )

    assert plan is not None
    assert plan.conversation_act == "input_clarification"
    assert plan.reason == "opaque_short_input_fallback"


def test_resolve_semantic_ingress_with_provider_falls_back_to_scope_boundary_for_out_of_scope_question(
    monkeypatch,
) -> None:
    async def fake_text_call(**_kwargs) -> str | None:
        return None

    monkeypatch.setattr("eduassist_semantic_ingress.runtime._text_call", fake_text_call)

    import asyncio

    plan = asyncio.run(
        resolve_semantic_ingress_with_provider(
            settings=SimpleNamespace(),
            stack_label="python_functions",
            request_message="Qual o melhor filme do ano?",
            conversation_context=None,
            preview={"mode": "structured_tool", "domain": "unknown", "access_tier": "authenticated"},
        )
    )

    assert plan is not None
    assert plan.conversation_act == "scope_boundary"
    assert plan.reason == "scope_boundary_fallback"


def test_validated_conversation_act_rejects_scope_boundary_for_school_scope_message() -> None:
    assert _validated_conversation_act(
        request_message="Posso fumar maconha nessa escola?",
        act="scope_boundary",
    ) == "none"
    assert _validated_conversation_act(
        request_message="Qual o horario da biblioteca?",
        act="scope_boundary",
    ) == "none"
    assert _validated_conversation_act(
        request_message="qual contato do diretor?",
        act="scope_boundary",
    ) == "none"


def test_should_run_semantic_ingress_classifier_accepts_opaque_short_input_even_when_preview_looks_academic() -> None:
    assert (
        should_run_semantic_ingress_classifier(
            message="rai",
            current_domain="academic",
            current_access_tier="authenticated",
            current_mode="structured_tool",
        )
        is True
    )


def test_should_run_semantic_ingress_classifier_skips_school_scope_content_query() -> None:
    assert (
        should_run_semantic_ingress_classifier(
            message="Posso fumar maconha nessa escola?",
            current_domain="institution",
            current_access_tier="public",
            current_mode="structured_tool",
        )
        is False
    )


def test_terminal_ingress_helper_marks_terminal_acts() -> None:
    assert is_terminal_ingress_act("greeting") is True
    assert is_terminal_ingress_act("assistant_identity") is True
    assert is_terminal_ingress_act("capabilities") is True
    assert is_terminal_ingress_act("auth_guidance") is True
    assert is_terminal_ingress_act("input_clarification") is True
    assert is_terminal_ingress_act("language_preference") is True
    assert is_terminal_ingress_act("scope_boundary") is True
    assert is_terminal_ingress_act("none") is False


def test_apply_semantic_ingress_preview_rewrites_to_public_structured_tool() -> None:
    preview = _preview()
    preview.selected_tools = ["get_administrative_status"]
    preview = apply_semantic_ingress_preview(
        preview=preview,
        plan=IngressSemanticPlan(conversation_act="greeting", reason="saudacao informal"),
        stack_name="python_functions",
    )

    assert preview.mode is OrchestrationMode.structured_tool
    assert preview.classification.domain is QueryDomain.institution
    assert preview.classification.access_tier is AccessTier.public
    assert preview.reason == "python_functions_semantic_ingress:greeting"
    assert "semantic_ingress:greeting" in preview.graph_path
    assert "get_public_school_profile" in preview.selected_tools
    assert "get_administrative_status" not in preview.selected_tools


def test_apply_semantic_ingress_preview_rewrites_unclear_input_to_safe_public_path() -> None:
    preview = _preview()
    preview.selected_tools = ["get_administrative_status"]
    preview = apply_semantic_ingress_preview(
        preview=preview,
        plan=IngressSemanticPlan(conversation_act="input_clarification", reason="idioma incerto"),
        stack_name="python_functions",
    )

    assert preview.reason == "python_functions_semantic_ingress:input_clarification"
    assert "semantic_ingress:input_clarification" in preview.graph_path
    assert "get_public_school_profile" in preview.selected_tools
    assert "get_administrative_status" not in preview.selected_tools


def test_apply_semantic_ingress_preview_rewrites_language_preference_to_safe_public_path() -> None:
    preview = _preview()
    preview.selected_tools = ["get_student_grades"]
    preview = apply_semantic_ingress_preview(
        preview=preview,
        plan=IngressSemanticPlan(conversation_act="language_preference", reason="metalinguagem"),
        stack_name="python_functions",
    )

    assert preview.reason == "python_functions_semantic_ingress:language_preference"
    assert "semantic_ingress:language_preference" in preview.graph_path
    assert "get_public_school_profile" in preview.selected_tools
    assert "get_student_grades" not in preview.selected_tools


def test_apply_semantic_ingress_preview_rewrites_scope_boundary_to_safe_public_path() -> None:
    preview = _preview()
    preview.selected_tools = ["get_administrative_status"]
    preview = apply_semantic_ingress_preview(
        preview=preview,
        plan=IngressSemanticPlan(conversation_act="scope_boundary", reason="fora do escopo"),
        stack_name="python_functions",
    )

    assert preview.reason == "python_functions_semantic_ingress:scope_boundary"
    assert "semantic_ingress:scope_boundary" in preview.graph_path
    assert "get_public_school_profile" in preview.selected_tools
    assert "get_administrative_status" not in preview.selected_tools
