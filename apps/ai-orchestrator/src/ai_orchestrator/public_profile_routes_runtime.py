from __future__ import annotations

"""Public profile routing helpers extracted from public_profile_runtime.py."""

LOCAL_EXTRACTED_NAMES = {'_compose_public_feature_answer', '_try_public_channel_fast_answer', '_build_public_profile_context', '_handle_public_contacts', '_handle_public_timeline', '_compose_public_pricing_projection_answer'}

from . import public_profile_runtime as _native
from .extracted_module_contracts import refresh_extracted_module_contract
from .intent_analysis_runtime import _compose_required_documents_answer, _detect_public_pricing_price_kind, _is_auth_guidance_query, _is_follow_up_query, _is_positive_requirement_query, _is_public_pricing_navigation_query, _message_matches_term, _normalize_text, _should_reuse_public_pricing_slots
from .public_act_rules_runtime import (
    _is_comparative_query,
    _is_cross_document_public_query,
    _is_public_service_credentials_bundle_query,
    _is_service_routing_query,
    _matches_public_location_rule,
    _matches_public_schedule_rule,
)
from .public_profile_intent_runtime import (
    _is_public_bolsas_and_processes_query,
    _is_public_calendar_visibility_query,
    _is_public_family_new_calendar_enrollment_query,
    _is_public_first_month_risks_query,
    _is_public_health_authorization_bridge_query,
    _is_public_health_second_call_query,
    _is_public_operating_hours_query,
    _is_public_permanence_family_query,
    _is_public_process_compare_query,
)
from .public_curriculum_runtime import _is_public_curriculum_query
from .public_document_policy_runtime import (
    _is_public_document_submission_query,
    _is_public_policy_compare_query,
    _is_public_policy_query,
)
from .public_feature_runtime import _is_public_feature_query
from .public_profile_routes_contact_runtime import _handle_public_contacts_impl
from .public_profile_routes_contract import PUBLIC_PROFILE_ROUTES_CONTRACT
from .public_profile_routes_context_runtime import (
    _build_public_profile_context_impl as _build_public_profile_context_extracted_impl,
)
from .public_profile_routes_feature_runtime import _compose_public_feature_answer_impl
from .public_profile_routes_pricing_runtime import _compose_public_pricing_projection_answer_impl
from .public_profile_routes_timeline_runtime import _handle_public_timeline_impl
from .public_timeline_runtime import (
    _is_public_timeline_before_after_query,
    _is_public_timeline_lifecycle_query,
    _is_public_timeline_query,
    _is_public_travel_planning_query,
    _is_public_year_three_phase_query,
)

def _refresh_native_namespace() -> None:
    refresh_extracted_module_contract(
        native_module=_native,
        namespace=globals(),
        contract_names=PUBLIC_PROFILE_ROUTES_CONTRACT,
        local_extracted_names=LOCAL_EXTRACTED_NAMES,
        contract_label='public_profile_routes_runtime',
    )

def _try_public_channel_fast_answer_impl(
    profile: dict[str, Any],
    message: str,
    *,
    original_message: str | None = None,
    conversation_context: dict[str, Any] | None = None,
    semantic_plan: PublicInstitutionPlan | None = None,
) -> str | None:
    _refresh_native_namespace()
    if not isinstance(profile, dict):
        return None
    normalized = _normalize_text(message)
    if 'biblioteca' in normalized and any(
        _message_matches_term(normalized, term)
        for term in {
            'biblioteca publica',
            'biblioteca pública',
            'publica da cidade',
            'pública da cidade',
            'da cidade',
            'municipal',
            'prefeitura',
        }
    ):
        return _compose_scope_boundary_answer(
            profile,
            conversation_context=conversation_context,
        )
    public_context = _build_public_profile_context_impl(
        profile,
        message,
        original_message=original_message or message,
        conversation_context=conversation_context,
        semantic_plan=semantic_plan,
    )
    if _is_public_timeline_before_after_query(message):
        before_after_answer = _compose_public_timeline_before_after_answer(profile)
        if before_after_answer:
            return before_after_answer
    if _is_auth_guidance_query(message):
        return (
            'Antes de autenticar e vincular sua conta do Telegram ao portal da escola, eu nao consigo abrir consultas protegidas como notas, faltas e financeiro. '
            'No portal autenticado, gere o codigo de vinculacao e depois envie aqui o comando `/start link_<codigo>`. '
            'Depois disso, eu passo a consultar seus dados autorizados por este canal.'
        )
    if _is_public_timeline_query(message) and any(
        _message_matches_term(normalized, term)
        for term in {
            'so esse recorte',
            'só esse recorte',
            'nao quero o calendario inteiro',
            'não quero o calendário inteiro',
            'recorte em ordem',
        }
    ):
        order_only_answer = _compose_public_timeline_order_only_answer(profile)
        if order_only_answer:
            return order_only_answer
    canonical_lane = match_public_canonical_lane(message)
    if canonical_lane:
        canonical_answer = (
            compose_public_conduct_policy_contextual_answer(
                message,
                profile=profile,
            )
            if canonical_lane == 'public_bundle.conduct_frequency_punctuality'
            else None
        ) or compose_public_canonical_lane_answer(canonical_lane, profile=profile)
        if canonical_answer:
            return canonical_answer
    if _has_public_multi_intent_signal(message):
        multi_intent_answer = _compose_public_multi_intent_answer(
            public_context,
            semantic_plan=None,
        )
        if multi_intent_answer:
            return multi_intent_answer
    if (
        _requested_contact_channel(message) is not None or _matches_public_location_rule(message)
    ) and (
        'secretaria' in normalized
        or 'telefone principal' in normalized
        or 'melhor canal' in normalized
        or 'endereco completo' in normalized
    ):
        contact_bundle_answer = _handle_public_contacts(public_context)
        if contact_bundle_answer:
            return contact_bundle_answer
    if _is_public_policy_compare_query(message):
        return _compose_public_policy_compare_answer(profile)
    if _is_public_bolsas_and_processes_query(message):
        bolsas_answer = compose_public_bolsas_and_processes(profile)
        if bolsas_answer:
            return bolsas_answer
    if _is_service_routing_query(message):
        routing_answer = _handle_public_service_routing(public_context)
        if routing_answer:
            return routing_answer
    if _is_positive_requirement_query(message) or (
        any(_message_matches_term(normalized, term) for term in {'documento', 'documentos'})
        and any(
            _message_matches_term(normalized, term)
            for term in {'matricula', 'matrícula', 'exigido', 'exigidos'}
        )
    ):
        return _compose_required_documents_answer(profile)
    if _is_public_document_submission_query(message) or (
        any(
            _message_matches_term(normalized, term)
            for term in {'documentacao', 'documentação', 'documentos'}
        )
        and any(
            _message_matches_term(normalized, term)
            for term in {'mandar', 'enviar', 'envio', 'caminho'}
        )
    ):
        return _compose_public_document_submission_answer(profile, message=message)
    if _is_public_pricing_navigation_query(message):
        pricing_answer = _handle_public_pricing(public_context)
        if pricing_answer:
            return pricing_answer
    if _is_public_timeline_query(message):
        timeline_answer = _handle_public_timeline(public_context)
        if timeline_answer:
            return timeline_answer
    if _matches_public_schedule_rule(message):
        schedule_answer = _handle_public_schedule(public_context)
        if schedule_answer:
            return schedule_answer
    if _is_public_operating_hours_query(message):
        operating_hours_answer = _handle_public_operating_hours(public_context)
        if operating_hours_answer:
            return operating_hours_answer
    if _is_public_feature_query(message):
        feature_answer = _handle_public_features(public_context)
        if feature_answer:
            return feature_answer
    if _is_public_timeline_lifecycle_query(message):
        lifecycle_answer = _compose_public_timeline_lifecycle_answer(profile)
        if lifecycle_answer:
            return lifecycle_answer
    if _is_public_travel_planning_query(message):
        travel_answer = _compose_public_travel_planning_answer(profile)
        if travel_answer:
            return travel_answer
    if _is_public_year_three_phase_query(message):
        phases_answer = _compose_public_year_three_phases_answer(profile)
        if phases_answer:
            return phases_answer
    if _is_public_calendar_visibility_query(message):
        calendar_visibility_answer = compose_public_calendar_visibility(profile)
        if calendar_visibility_answer:
            return calendar_visibility_answer
    if _is_public_family_new_calendar_enrollment_query(message):
        family_new_answer = compose_public_family_new_calendar_assessment_enrollment()
        if family_new_answer:
            return family_new_answer
    if _is_public_service_credentials_bundle_query(message):
        return _compose_public_service_credentials_bundle_answer(profile)
    if _is_public_health_second_call_query(message):
        health_second_call_answer = compose_public_health_second_call()
        if health_second_call_answer:
            return health_second_call_answer
    if _is_public_permanence_family_query(message):
        permanence_answer = compose_public_permanence_and_family_support(profile)
        if permanence_answer:
            return permanence_answer
    if _is_public_health_authorization_bridge_query(message):
        bridge_answer = compose_public_health_authorizations_bridge()
        if bridge_answer:
            return bridge_answer
    if _is_public_first_month_risks_query(message):
        first_month_answer = compose_public_first_month_risks(profile)
        if first_month_answer:
            return first_month_answer
    if _is_public_process_compare_query(message):
        process_compare_answer = compose_public_process_compare()
        if process_compare_answer:
            return process_compare_answer
    if _is_public_policy_query(message):
        policy_answer = _handle_public_policy(public_context)
        if policy_answer:
            return policy_answer
    if not _is_cross_document_public_query(message) and any(
        _message_matches_term(normalized, term)
        for term in {
            '30 segundos',
            '30s',
            'familia nova',
            'família nova',
            'por que escolher',
            'por que deveria',
        }
    ):
        highlight_answer = _handle_public_highlight(public_context)
        if highlight_answer:
            return highlight_answer
    if (
        any(
            _message_matches_term(normalized, term)
            for term in {
                'proposta pedagogica',
                'proposta pedagógica',
                'projeto pedagogico',
                'projeto pedagógico',
            }
        )
        or (
            _message_matches_term(normalized, 'acolhimento')
            and any(
                _message_matches_term(normalized, term)
                for term in {'disciplina', 'disciplinas', 'convivencia', 'convivência'}
            )
        )
        or _is_public_curriculum_query(message)
    ):
        pedagogical_answer = _compose_public_pedagogical_answer(profile, message)
        if pedagogical_answer:
            return pedagogical_answer
    if any(
        _message_matches_term(normalized, term)
        for term in {
            'o que isso muda na pratica',
            'o que isso muda na prática',
            'na pratica no dia a dia',
            'na prática no dia a dia',
        }
    ):
        practical_answer = _compose_public_comparative_practical_answer(profile)
        if practical_answer:
            return practical_answer
    if not _is_cross_document_public_query(message) and (
        _is_comparative_query(message)
        or (
            _message_matches_term(normalized, 'publica')
            and any(
                _message_matches_term(normalized, term) for term in {'pagar', 'pagando', 'estudar'}
            )
        )
    ):
        comparative_answer = _compose_public_comparative_answer(profile)
        if comparative_answer:
            return comparative_answer
    if _message_matches_term(normalized, 'caixa postal'):
        primary_phone = _select_primary_contact_entry(
            profile,
            'telefone',
            'telefone principal',
        )
        if primary_phone:
            return (
                'Hoje a escola nao trabalha com caixa postal para esse tipo de envio. '
                f'Para documentos, use portal institucional, email da secretaria, secretaria presencial. '
                f'Se precisar falar com a escola, o telefone principal e {primary_phone.get("value")}.'
            )
        return (
            'Hoje a escola nao trabalha com caixa postal para esse tipo de envio. '
            'Para documentos, use portal institucional, email da secretaria, secretaria presencial.'
        )
    if _requested_contact_channel(message) == 'telefone' and _message_matches_term(
        normalized, 'fax'
    ):
        primary_phone = _select_primary_contact_entry(
            profile,
            'telefone',
            'telefone principal',
        )
        if primary_phone:
            return (
                'Hoje a escola nao utiliza fax. '
                f'Para entrar em contato por telefone, o numero da secretaria e {primary_phone.get("value")}.'
            )
        return 'Hoje a escola nao utiliza fax.'
    if looks_like_scope_boundary_candidate(message) and not looks_like_school_scope_message(
        message
    ):
        return _compose_scope_boundary_answer(
            profile,
            conversation_context=None,
        )

    return None


def _build_public_profile_context_impl(
    profile: dict[str, Any],
    message: str,
    *,
    actor: dict[str, Any] | None = None,
    original_message: str | None = None,
    conversation_context: dict[str, Any] | None = None,
    semantic_plan: PublicInstitutionPlan | None = None,
) -> PublicProfileContext:
    return _build_public_profile_context_extracted_impl(
        profile,
        message,
        actor=actor,
        original_message=original_message,
        conversation_context=conversation_context,
        semantic_plan=semantic_plan,
        public_profile_context_cls=PublicProfileContext,
    )
# Compatibility aliases while public_profile_runtime keeps facade imports.
_compose_public_feature_answer = _compose_public_feature_answer_impl
_try_public_channel_fast_answer = _try_public_channel_fast_answer_impl
_build_public_profile_context = _build_public_profile_context_impl
_handle_public_contacts = _handle_public_contacts_impl
_handle_public_timeline = _handle_public_timeline_impl
_compose_public_pricing_projection_answer = _compose_public_pricing_projection_answer_impl
