from __future__ import annotations

# ruff: noqa: F401,F403,F405

"""Public profile routing helpers extracted from public_profile_runtime.py."""

LOCAL_EXTRACTED_NAMES = {'_compose_public_feature_answer', '_try_public_channel_fast_answer', '_build_public_profile_context', '_handle_public_contacts', '_handle_public_timeline', '_compose_public_pricing_projection_answer'}

from . import public_profile_runtime as _native
from .intent_analysis_runtime import _detect_public_pricing_price_kind, _is_auth_guidance_query, _is_follow_up_query, _is_positive_requirement_query, _message_matches_term, _normalize_text, _should_reuse_public_pricing_slots
from .public_act_rules_runtime import (
    _is_comparative_query,
    _is_cross_document_public_query,
    _is_public_bolsas_and_processes_query,
    _is_public_calendar_visibility_query,
    _is_public_curriculum_query,
    _is_public_document_submission_query,
    _is_public_family_new_calendar_enrollment_query,
    _is_public_feature_query,
    _is_public_first_month_risks_query,
    _is_public_health_authorization_bridge_query,
    _is_public_health_second_call_query,
    _is_public_permanence_family_query,
    _is_public_policy_compare_query,
    _is_public_policy_query,
    _is_public_pricing_navigation_query,
    _is_public_process_compare_query,
    _is_public_service_credentials_bundle_query,
    _is_public_timeline_before_after_query,
    _is_public_timeline_lifecycle_query,
    _is_public_timeline_query,
    _is_public_travel_planning_query,
    _is_public_year_three_phase_query,
    _is_service_routing_query,
    _matches_public_location_rule,
)

def _refresh_native_namespace() -> None:
    for name, value in vars(_native).items():
        if name.startswith('__') or name in LOCAL_EXTRACTED_NAMES:
            continue
        globals()[name] = value

def _compose_public_feature_answer_impl(
    *,
    profile: dict[str, Any],
    original_message: str,
    analysis_message: str,
    conversation_context: dict[str, Any] | None = None,
) -> str | None:
    _refresh_native_namespace()
    feature_map = _feature_inventory_map(profile)
    school_name = str(profile.get('school_name', 'Colegio Horizonte'))
    requested_features = _requested_public_features(original_message)
    requested_attributes = set(_requested_public_attributes(original_message))
    recent_focus = _recent_trace_focus(conversation_context) or {}
    feature_followup_context = (
        isinstance(recent_focus, dict)
        and str(recent_focus.get('active_task', '')).strip() == 'public:features'
    )
    if (
        not requested_features
        and 'name' in requested_attributes
        and _is_follow_up_query(original_message)
    ):
        recent_feature = _recent_public_feature_key(conversation_context)
        if recent_feature:
            requested_features = [recent_feature]
    if (
        not requested_features
        and _is_follow_up_query(original_message)
        and not _is_public_feature_query(original_message)
    ):
        focus = _extract_feature_gap_focus(original_message)
        if (
            feature_followup_context
            and focus
            and focus not in {'atividade', 'atividades', 'contraturno'}
        ):
            return (
                f'Nao vi uma referencia oficial sobre {focus} no perfil publico do {school_name}. '
                'Se quiser, eu posso te mostrar o que esta documentado sobre estrutura e atividades.'
            )
        requested_features = _requested_public_features(analysis_message)
    if not requested_features and _is_follow_up_query(original_message):
        recent_feature = _recent_public_feature_key(conversation_context)
        if recent_feature:
            requested_features = [recent_feature]
    asks_why_absent = _asks_why_feature_is_missing(original_message)
    if not requested_features and _is_public_feature_query(original_message):
        generic_activity_query = any(
            _message_matches_term(_normalize_text(original_message), term)
            for term in {'atividade', 'atividades', 'contraturno'}
        ) and not any(
            _message_matches_term(_normalize_text(original_message), term)
            for term in {'aula de', 'oficina de', 'curso de', 'clube de', 'atividade de'}
        )
        generic_structure_query = any(
            _message_matches_term(_normalize_text(original_message), term)
            for term in {
                'estrutura',
                'infraestrutura',
                'espaco',
                'espaço',
                'espacos',
                'espaços',
                'campus',
            }
        )
        focus = _extract_feature_gap_focus(original_message)
        if (
            focus
            and not generic_activity_query
            and not generic_structure_query
            and focus not in {'atividade', 'atividades', 'contraturno'}
        ):
            return (
                f'Nao vi uma referencia oficial sobre {focus} no perfil publico do {school_name}. '
                'Se voce quiser, eu posso te dizer quais atividades e espacos aparecem oficialmente.'
            )
        available_items: list[str] = []
        for feature_key in (
            'biblioteca',
            'maker',
            'quadra',
            'futebol',
            'volei',
            'danca',
            'teatro',
            'cantina',
            'orientacao educacional',
        ):
            item = feature_map.get(feature_key)
            if not item or not bool(item.get('available')):
                continue
            label = str(item.get('label', feature_key)).strip().lower()
            if label and label not in available_items:
                available_items.append(label)
        if available_items:
            preview = ', '.join(available_items[:5])
            return (
                f'Hoje, a estrutura do {school_name} inclui atividades e espacos como {preview}. '
                'Se quiser, eu posso te detalhar qualquer um deles.'
            )
        return (
            f'Hoje o perfil publico do {school_name} nao traz esse detalhe de estrutura ou atividade. '
            'Se quiser, eu posso te mostrar o que esta oficialmente documentado.'
        )
    if not requested_features:
        return None
    if len(requested_features) == 1:
        feature_key = requested_features[0]
        item = feature_map.get(feature_key)
        if item is None:
            return (
                f'Nao vi uma referencia oficial sobre {feature_key} no perfil publico do {school_name}. '
                'Se quiser, eu posso te mostrar o que esta documentado sobre estrutura e atividades.'
            )
        label = str(item.get('label', feature_key)).strip()
        notes = str(item.get('notes', '')).strip()
        available = bool(item.get('available'))
        if available and 'name' in requested_attributes:
            return f'O nome desse espaco e {label}.'
        if available:
            if asks_why_absent:
                return f'Na verdade, o {school_name} tem sim {label}. {notes}'.strip()
            if feature_key == 'biblioteca':
                return f'Sim. O {school_name} tem a {label}. {notes}'.strip()
            return f'Sim. O {school_name} oferece {label}. {notes}'.strip()
        if asks_why_absent:
            return f'Hoje o {school_name} nao oferece {label}. {notes}'.strip()
        return f'Nao. O {school_name} nao oferece {label}. {notes}'.strip()

    lines = [f'Sobre estrutura e atividades do {school_name}:']
    for feature_key in requested_features:
        item = feature_map.get(feature_key)
        if item is None:
            lines.append(f'- Ainda nao encontrei uma informacao oficial sobre {feature_key}.')
            continue
        label = str(item.get('label', feature_key)).strip()
        notes = str(item.get('notes', '')).strip()
        available = bool(item.get('available'))
        if available:
            lines.append(f'- Sim: {label}. {notes}'.rstrip())
        else:
            lines.append(f'- Nao: {label}. {notes}'.rstrip())
    return '\n'.join(lines)


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
            'Para consultas protegidas, como notas, faltas e financeiro, voce precisa vincular sua conta do Telegram ao portal da escola. '
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
    if _is_public_pricing_navigation_query(message):
        pricing_answer = _handle_public_pricing(public_context)
        if pricing_answer:
            return pricing_answer
    if _is_public_timeline_query(message):
        timeline_answer = _handle_public_timeline(public_context)
        if timeline_answer:
            return timeline_answer
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
    if _is_positive_requirement_query(message) or (
        any(_message_matches_term(normalized, term) for term in {'documento', 'documentos'})
        and any(
            _message_matches_term(normalized, term)
            for term in {'matricula', 'matrícula', 'exigido', 'exigidos'}
        )
    ):
        return _compose_required_documents_answer(profile)
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
    _refresh_native_namespace()
    effective_conversation_context = conversation_context
    if semantic_plan is not None and semantic_plan.conversation_act == 'greeting':
        # A terminal greeting classified at ingress should not inherit the
        # previous workflow as if it were a follow-up.
        effective_conversation_context = None
    source_message = original_message or message
    normalized = _normalize_text(source_message)
    analysis_normalized = _normalize_text(message)
    slot_memory = _build_conversation_slot_memory(
        actor=None,
        profile=profile,
        conversation_context=effective_conversation_context,
        request_message=source_message,
        public_plan=semantic_plan,
    )
    school_name = str(profile.get('school_name', 'Colegio Horizonte'))
    school_reference = (
        'a escola' if _assistant_already_introduced(effective_conversation_context) else school_name
    )
    school_reference_capitalized = (
        'A escola' if school_reference == 'a escola' else school_reference
    )
    postal_code_raw = profile.get('postal_code')
    website_url_raw = profile.get('website_url')
    fax_number_raw = profile.get('fax_number')
    curriculum_basis_raw = profile.get('curriculum_basis')
    segment = _select_public_segment(message) or _select_public_segment(source_message)
    if segment is None and _should_reuse_public_pricing_slots(source_message):
        segment = slot_memory.public_pricing_segment
    schedule_context_normalized = normalized
    if _is_follow_up_query(source_message) and any(
        _message_matches_term(analysis_normalized, term) for term in PUBLIC_SCHEDULE_TERMS
    ):
        schedule_context_normalized = analysis_normalized
    contact_reference_message = _public_contact_reference_message(
        profile=profile,
        source_message=source_message,
        analysis_message=message,
        conversation_context=effective_conversation_context,
    )
    preferred_contact_labels = tuple(
        _preferred_contact_labels_from_context(
            profile,
            source_message,
            effective_conversation_context,
        )
    )
    if _contact_is_general_school_query(contact_reference_message):
        preferred_contact_labels = ()
    return PublicProfileContext(
        profile=profile,
        actor=actor,
        message=message,
        source_message=source_message,
        normalized=normalized,
        analysis_normalized=analysis_normalized,
        school_name=school_name,
        school_reference=school_reference,
        school_reference_capitalized=school_reference_capitalized,
        city=str(profile.get('city', '')),
        state=str(profile.get('state', '')),
        district=str(profile.get('district', '')),
        address_line=str(profile.get('address_line', '')),
        postal_code=postal_code_raw.strip() if isinstance(postal_code_raw, str) else '',
        website_url=website_url_raw.strip() if isinstance(website_url_raw, str) else '',
        fax_number=fax_number_raw.strip() if isinstance(fax_number_raw, str) else '',
        curriculum_basis=curriculum_basis_raw.strip()
        if isinstance(curriculum_basis_raw, str)
        else '',
        curriculum_components=tuple(
            str(item).strip()
            for item in profile.get('curriculum_components', [])
            if isinstance(item, str) and str(item).strip()
        ),
        confessional_status=str(profile.get('confessional_status', '')).strip().lower(),
        segment=segment,
        schedule_context_normalized=schedule_context_normalized,
        shift_offers=tuple(row for row in profile.get('shift_offers', []) if isinstance(row, dict)),
        tuition_reference=tuple(
            row for row in profile.get('tuition_reference', []) if isinstance(row, dict)
        ),
        semantic_act=semantic_plan.conversation_act if semantic_plan else None,
        contact_reference_message=contact_reference_message,
        preferred_contact_labels=preferred_contact_labels,
        requested_channel=(
            semantic_plan.requested_channel
            if semantic_plan and semantic_plan.requested_channel
            else _requested_contact_channel(contact_reference_message)
        ),
        requested_attribute_override=(
            semantic_plan.requested_attribute
            if semantic_plan and semantic_plan.requested_attribute
            else None
        ),
        slot_memory=slot_memory,
        conversation_context=effective_conversation_context,
        semantic_plan=semantic_plan,
    )


def _handle_public_contacts_impl(context: PublicProfileContext) -> str:
    _refresh_native_namespace()
    wants_location = _matches_public_location_rule(context.source_message)
    wants_secretaria_guidance = any(
        _message_matches_term(context.normalized, term)
        for term in {'secretaria', 'secretaria escolar', 'atendimento da secretaria'}
    )
    wants_finance_guidance = any(
        _message_matches_term(context.normalized, term)
        for term in {'financeiro', 'tesouraria', 'cobranca', 'cobrança', 'mensalidade', 'boleto'}
    )
    if wants_location or wants_secretaria_guidance:
        lines: list[str] = []
        if wants_location:
            location = ', '.join(
                part
                for part in [context.address_line, context.district, context.city, context.state]
                if part
            )
            if context.postal_code:
                location = f'{location}, CEP {context.postal_code}'
            if location:
                lines.append(
                    f'O endereco publicado de {context.school_reference} hoje e {location}.'
                )
        primary_phone = _select_primary_contact_entry(
            context.profile,
            'telefone',
            context.contact_reference_message,
            preferred_labels=['Secretaria'],
        )
        if primary_phone:
            lines.append(f'O telefone principal hoje e {primary_phone.get("value")}.')
        if wants_secretaria_guidance:
            secretaria_whatsapp = _select_primary_contact_entry(
                context.profile,
                'whatsapp',
                context.contact_reference_message,
                preferred_labels=['Secretaria digital', 'Atendimento comercial'],
            )
            secretaria_email = _select_primary_contact_entry(
                context.profile,
                'email',
                context.contact_reference_message,
                preferred_labels=['Secretaria'],
            )
            if secretaria_whatsapp:
                lines.append(
                    f'O canal mais direto para falar com a secretaria hoje e o WhatsApp {secretaria_whatsapp.get("value")}.'
                )
            elif secretaria_email:
                lines.append(
                    f'O canal mais direto para a secretaria hoje e o email {secretaria_email.get("value")}.'
                )
        if wants_finance_guidance:
            finance_phone = _select_primary_contact_entry(
                context.profile,
                'telefone',
                context.contact_reference_message,
                preferred_labels=['Financeiro'],
            )
            finance_whatsapp = _select_primary_contact_entry(
                context.profile,
                'whatsapp',
                context.contact_reference_message,
                preferred_labels=['Financeiro'],
            )
            finance_email = _select_primary_contact_entry(
                context.profile,
                'email',
                context.contact_reference_message,
                preferred_labels=['Financeiro'],
            )
            if finance_whatsapp:
                lines.append(
                    f'O canal mais direto do financeiro hoje e o WhatsApp {finance_whatsapp.get("value")}.'
                )
            elif finance_email:
                lines.append(
                    f'O canal mais direto do financeiro hoje e o email {finance_email.get("value")}.'
                )
            elif finance_phone:
                lines.append(
                    f'O telefone mais direto do financeiro hoje e {finance_phone.get("value")}.'
                )
        if lines:
            return ' '.join(lines)

    phone_lines = _contact_value(context.profile, 'telefone')
    whatsapp_lines = _contact_value(context.profile, 'whatsapp')
    email_lines = _contact_value(context.profile, 'email')
    if _message_matches_term(context.normalized, 'caixa postal'):
        primary_phone = _select_primary_contact_entry(
            context.profile,
            'telefone',
            context.contact_reference_message,
            preferred_labels=context.preferred_contact_labels,
        )
        if primary_phone:
            return (
                f'Hoje {context.school_reference} nao trabalha com caixa postal como canal institucional. '
                f'Se precisar de contato, o telefone principal e {primary_phone.get("value")}.'
            )
        return f'Hoje {context.school_reference} nao trabalha com caixa postal como canal institucional.'
    fax_only_query = _message_matches_term(context.normalized, 'fax') and not any(
        _message_matches_term(context.normalized, term)
        for term in {'telefone', 'fone', 'ligar', 'ligo', 'whatsapp', 'email'}
    )
    if fax_only_query:
        if context.fax_number:
            return f'O fax institucional publicado de {context.school_reference} hoje e {context.fax_number}.'
        primary_phone = _select_primary_contact_entry(
            context.profile,
            'telefone',
            context.contact_reference_message,
            preferred_labels=context.preferred_contact_labels,
        )
        if primary_phone:
            return (
                f'Hoje {context.school_reference} nao publica numero de fax. '
                f'Se quiser ligar, o telefone principal e {primary_phone.get("value")}.'
            )
        return f'Hoje {context.school_reference} nao publica numero de fax.'
    if context.requested_channel == 'telefone':
        primary_phone = _select_primary_contact_entry(
            context.profile,
            'telefone',
            context.contact_reference_message,
            preferred_labels=context.preferred_contact_labels,
        )
        if primary_phone and (
            _contact_is_general_school_query(context.contact_reference_message)
            or not _wants_contact_list(context.contact_reference_message)
        ):
            label = primary_phone.get('label')
            value = primary_phone.get('value')
            if label:
                response = (
                    f'O telefone principal {_school_object_reference(context.school_reference)} hoje e {value}, '
                    f'{_format_contact_origin(label, "telefone")}.'
                )
            else:
                response = f'O telefone principal {_school_object_reference(context.school_reference)} hoje e {value}.'
            if _message_matches_term(context.normalized, 'fax'):
                response += (
                    f' O fax publicado e {context.fax_number}.'
                    if context.fax_number
                    else ' Hoje a escola nao publica numero de fax.'
                )
            return response
        if len(phone_lines) == 1:
            response = f'O telefone oficial de {context.school_reference} e {phone_lines[0]}.'
            if _message_matches_term(context.normalized, 'fax'):
                response += ' Hoje a escola nao publica numero de fax.'
            return response
        lines = [f'Os telefones oficiais de {context.school_reference} hoje sao:']
        lines.extend(f'- {item}' for item in phone_lines)
        if _message_matches_term(context.normalized, 'fax'):
            lines.append('- Fax: nao publicado')
        return '\n'.join(lines)
    if context.requested_channel == 'whatsapp':
        primary_whatsapp = _select_primary_contact_entry(
            context.profile,
            'whatsapp',
            context.contact_reference_message,
            preferred_labels=context.preferred_contact_labels,
        )
        if primary_whatsapp and (
            _contact_is_general_school_query(context.contact_reference_message)
            or not _wants_contact_list(context.contact_reference_message)
        ):
            label = primary_whatsapp.get('label')
            value = primary_whatsapp.get('value')
            if label:
                return (
                    f'O WhatsApp mais direto {_school_object_reference(context.school_reference)} hoje e {value}, '
                    f'{_format_contact_origin(label, "whatsapp")}.'
                )
            return f'O WhatsApp oficial {_school_object_reference(context.school_reference)} hoje e {value}.'
        if len(whatsapp_lines) == 1:
            return f'O WhatsApp oficial de {context.school_reference} hoje e {whatsapp_lines[0]}.'
        lines = [f'Os canais de WhatsApp publicados por {context.school_reference} hoje sao:']
        lines.extend(f'- {item}' for item in whatsapp_lines)
        return '\n'.join(lines)
    if context.requested_channel == 'email':
        primary_email = _select_primary_contact_entry(
            context.profile,
            'email',
            context.contact_reference_message,
            preferred_labels=context.preferred_contact_labels,
        )
        if primary_email and (
            _contact_is_general_school_query(context.contact_reference_message)
            or not _wants_contact_list(context.contact_reference_message)
        ):
            label = primary_email.get('label')
            value = primary_email.get('value')
            if label:
                return (
                    f'O email mais direto {_school_object_reference(context.school_reference)} hoje e {value}, '
                    f'{_format_contact_origin(label, "email")}.'
                )
            return f'O email institucional publicado de {context.school_reference} e {value}.'
        if len(email_lines) == 1:
            return (
                f'O email institucional publicado de {context.school_reference} e {email_lines[0]}.'
            )
        lines = [f'Os emails institucionais publicados de {context.school_reference} hoje sao:']
        lines.extend(f'- {item}' for item in email_lines)
        return '\n'.join(lines)
    lines = [f'Voce pode falar com {context.school_reference} por estes canais oficiais:']
    lines.extend(f'- {item}' for item in [*phone_lines, *whatsapp_lines, *email_lines])
    if _message_matches_term(context.normalized, 'fax'):
        lines.append('- Fax: nao publicado')
    return '\n'.join(lines)


def _handle_public_timeline_impl(context: PublicProfileContext) -> str:
    _refresh_native_namespace()
    entries = context.profile.get('public_timeline')
    if not isinstance(entries, list) or not entries:
        return f'Hoje a base publica de {context.school_reference} nao traz um marco institucional estruturado para essa data.'

    normalized = context.normalized

    if _is_public_timeline_lifecycle_query(context.source_message):
        lifecycle_answer = _compose_public_timeline_lifecycle_answer(context.profile)
        if lifecycle_answer:
            return lifecycle_answer
    if _is_public_travel_planning_query(context.source_message):
        travel_answer = _compose_public_travel_planning_answer(context.profile)
        if travel_answer:
            return travel_answer
    if _is_public_year_three_phase_query(context.source_message):
        phases_answer = _compose_public_year_three_phases_answer(context.profile)
        if phases_answer:
            return phases_answer

    def _pick(topic_fragment: str) -> dict[str, Any] | None:
        for item in entries:
            if not isinstance(item, dict):
                continue
            if topic_fragment in str(item.get('topic_key', '')):
                return item
        return None

    wants_enrollment = _message_matches_term(normalized, 'matricula') or _message_matches_term(
        normalized, 'matrícula'
    )
    wants_school_year_start = any(
        _message_matches_term(normalized, term)
        for term in {
            'inicio das aulas',
            'início das aulas',
            'comecam as aulas',
            'começam as aulas',
            'ano letivo',
        }
    )
    wants_family = any(
        _message_matches_term(normalized, term)
        for term in {'responsaveis', 'responsáveis', 'reuniao', 'reunião', 'familia', 'família'}
    )
    if wants_enrollment and wants_school_year_start:
        lines: list[str] = []
        topics: list[str] = ['admissions_opening', 'school_year_start']
        if wants_family:
            topics.append('family_meeting')
        for topic in topics:
            item = _pick(topic)
            if not isinstance(item, dict):
                continue
            summary = str(item.get('summary', '')).strip()
            notes = str(item.get('notes', '')).strip()
            line = f'{summary} {notes}'.strip()
            if line:
                lines.append(line)
        if lines:
            return '\n'.join(lines)

    chosen: dict[str, Any] | None = None
    recent_focus = _recent_conversation_focus(context.conversation_context) or {}
    if _is_follow_up_query(context.source_message):
        if _recent_messages_mention(
            context.conversation_context,
            {'comecam as aulas', 'começam as aulas', 'aulas', 'ano letivo'},
        ):
            chosen = _pick('school_year_start')
        elif _recent_messages_mention(
            context.conversation_context,
            {'formatura', 'cerimonia de conclusao', 'cerimônia de conclusão'},
        ):
            chosen = _pick('graduation')
        elif _recent_messages_mention(
            context.conversation_context,
            {'matricula', 'matrícula', 'pre cadastro', 'pré-cadastro'},
        ):
            chosen = _pick('admissions_opening')
    if (
        _is_follow_up_query(context.source_message)
        and str(recent_focus.get('kind', '') or '').strip() == 'admissions'
        and any(
            _message_matches_term(normalized, term)
            for term in {
                'inicio das aulas',
                'início das aulas',
                'comecam as aulas',
                'começam as aulas',
                'aulas',
            }
        )
    ):
        chosen = _pick('school_year_start')
    elif chosen is None and (
        _message_matches_term(normalized, 'matricula')
        or _message_matches_term(normalized, 'matrícula')
    ):
        chosen = _pick('admissions_opening')
    elif chosen is None and _message_matches_term(normalized, 'formatura'):
        chosen = _pick('graduation')
    elif chosen is None and any(
        _message_matches_term(normalized, term)
        for term in {
            'inicio das aulas',
            'início das aulas',
            'comecam as aulas',
            'começam as aulas',
            'ano letivo',
        }
    ):
        chosen = _pick('school_year_start')

    if chosen is None:
        chosen = next((item for item in entries if isinstance(item, dict)), None)
    if chosen is None:
        return f'Hoje a base publica de {context.school_reference} nao traz um marco institucional estruturado para essa data.'

    summary = str(chosen.get('summary', '')).strip()
    notes = str(chosen.get('notes', '')).strip()
    if notes:
        return f'{summary} {notes}'.strip()
    return summary


def _compose_public_pricing_projection_answer_impl(context: PublicProfileContext) -> str | None:
    _refresh_native_namespace()
    hints = resolve_entity_hints(context.source_message)
    quantity = hints.quantity_hint
    if quantity is None:
        numeric_match = re.search(r'\b(\d{1,4})\b', context.normalized)
        if numeric_match:
            quantity = int(numeric_match.group(1))
    reuse_pricing_slots = _should_reuse_public_pricing_slots(context.source_message)
    if quantity is None and reuse_pricing_slots:
        slot_quantity = str(context.slot_memory.public_pricing_quantity or '').strip()
        if slot_quantity.isdigit():
            quantity = int(slot_quantity)
    normalized = context.normalized
    explicit_projection_request = quantity is not None and any(
        _message_matches_term(normalized, term)
        for term in {
            'mensalidade',
            'mensalidades',
            'matricula',
            'matrícula',
            'pagar',
            'pagaria',
            'filhos',
            'alunos',
        }
    )
    if (
        (not hints.is_hypothetical and not reuse_pricing_slots and not explicit_projection_request)
        or quantity is None
        or quantity <= 0
    ):
        return None

    amount_key = (
        _detect_public_pricing_price_kind(context.source_message)
        or context.slot_memory.public_pricing_price_kind
    )
    wants_enrollment_fee = any(
        _message_matches_term(normalized, term)
        for term in {'matricula', 'matrícula', 'taxa de matricula', 'taxa de matrícula'}
    )
    wants_monthly_amount = any(
        _message_matches_term(normalized, term)
        for term in {
            'mensalidade',
            'mensalidades',
            'por mes',
            'por mês',
            'total por mes',
            'total por mês',
            'mensal',
            'todo mes',
            'todo mês',
            'manter',
        }
    )
    wants_both_amounts = wants_enrollment_fee and wants_monthly_amount
    if (
        not wants_both_amounts
        and quantity is not None
        and any(
            _message_matches_term(normalized, term)
            for term in {
                'matricula e o total por mes',
                'matrícula e o total por mês',
                'matricular e manter',
                'matricula e mensalidade',
                'matrícula e mensalidade',
            }
        )
    ):
        wants_both_amounts = True
    if amount_key not in {'monthly_amount', 'enrollment_fee'}:
        amount_key = (
            'monthly_amount'
            if wants_monthly_amount and not wants_enrollment_fee
            else 'enrollment_fee'
        )
    amount_label = (
        'mensalidade publica de referencia'
        if amount_key == 'monthly_amount'
        else 'taxa publica de matricula'
    )

    requested_segment = context.segment or context.slot_memory.public_pricing_segment
    requested_grade_year = context.slot_memory.public_pricing_grade_year
    if not requested_segment and requested_grade_year in {'1o ano', '2o ano', '3o ano'}:
        requested_segment = 'Ensino Medio'
    if not requested_segment and requested_grade_year in {'6o ano', '7o ano', '8o ano', '9o ano'}:
        requested_segment = 'Ensino Fundamental II'
    relevant_rows = [
        row
        for row in context.tuition_reference
        if isinstance(row, dict)
        and _public_segment_matches(str(row.get('segment')), requested_segment)
    ]
    if not relevant_rows:
        relevant_rows = [row for row in context.tuition_reference if isinstance(row, dict)]

    projected_rows: list[dict[str, Any]] = []
    sibling_discount_note: str | None = None
    for row in relevant_rows:
        monthly_amount = _parse_public_money(row.get('monthly_amount'))
        enrollment_fee = _parse_public_money(row.get('enrollment_fee'))
        requested_amount = monthly_amount if amount_key == 'monthly_amount' else enrollment_fee
        if wants_both_amounts:
            if (
                monthly_amount is None
                or monthly_amount <= 0
                or enrollment_fee is None
                or enrollment_fee <= 0
            ):
                continue
        elif requested_amount is None or requested_amount <= 0:
            continue
        notes = str(row.get('notes', '')).strip()
        if not sibling_discount_note and any(
            _message_matches_term(_normalize_text(notes), term)
            for term in {
                'irmaos',
                'irmãos',
                'pagamento pontual',
                'politica comercial',
                'política comercial',
                'desconto',
            }
        ):
            sibling_discount_note = notes
        projected_rows.append(
            {
                'segment': str(row.get('segment', 'Segmento')).strip(),
                'shift_label': str(row.get('shift_label', 'turno')).strip(),
                'amount': requested_amount,
                'monthly_amount': monthly_amount,
                'enrollment_fee': enrollment_fee,
                'notes': notes,
            }
        )

    if not projected_rows:
        return None

    if wants_both_amounts:
        unique_pairs = {(row['monthly_amount'], row['enrollment_fee']) for row in projected_rows}
        if len(unique_pairs) == 1:
            per_student_monthly, per_student_enrollment = next(iter(unique_pairs))
            assert per_student_monthly is not None
            assert per_student_enrollment is not None
            total_monthly = per_student_monthly * quantity
            total_enrollment = per_student_enrollment * quantity
            shared_scope = 'nos segmentos publicados que usam essa mesma referencia'
            if len(projected_rows) == 1:
                shared_scope = f'em {projected_rows[0]["segment"]}'
                if requested_grade_year:
                    shared_scope = f'no {requested_grade_year} de {projected_rows[0]["segment"]}'
            lines = [
                (
                    f'Para {quantity} aluno(s), se eu usar os valores publicos hoje publicados {shared_scope}, '
                    f'a matricula fica {quantity} x {_format_brl(per_student_enrollment)} = {_format_brl(total_enrollment)} '
                    f'e a mensalidade por mes fica {quantity} x {_format_brl(per_student_monthly)} = {_format_brl(total_monthly)}.'
                )
            ]
        else:
            lines = [
                'Hoje a escola publica mais de uma referencia combinada de matricula e mensalidade. Para essa simulacao, os totais por segmento ficam assim:'
            ]
            for row in projected_rows[:4]:
                monthly_amount = row['monthly_amount']
                enrollment_fee = row['enrollment_fee']
                if monthly_amount is None or enrollment_fee is None:
                    continue
                lines.append(
                    f'- {row["segment"]} ({row["shift_label"]}): matricula {quantity} x {_format_brl(enrollment_fee)} = {_format_brl(enrollment_fee * quantity)}; '
                    f'mensalidade por mes {quantity} x {_format_brl(monthly_amount)} = {_format_brl(monthly_amount * quantity)}.'
                )
    else:
        unique_amounts = {row['amount'] for row in projected_rows}
        if len(unique_amounts) == 1:
            per_student = projected_rows[0]['amount']
            total_amount = per_student * quantity
            shared_scope = 'nos segmentos publicados que usam essa mesma referencia'
            if len(projected_rows) == 1:
                shared_scope = f'em {projected_rows[0]["segment"]}'
                if requested_grade_year:
                    shared_scope = f'no {requested_grade_year} de {projected_rows[0]["segment"]}'
            lines = [
                f'Para {quantity} aluno(s), se eu usar a {amount_label} hoje publicada {shared_scope}, a simulacao fica {quantity} x {_format_brl(per_student)} = {_format_brl(total_amount)}.'
            ]
        else:
            lines = [
                f'Hoje a escola publica mais de uma referencia de {amount_label}. Para {quantity} alunos, a simulacao por segmento fica assim:'
            ]
            for row in projected_rows[:4]:
                total_amount = row['amount'] * quantity
                lines.append(
                    f'- {row["segment"]} ({row["shift_label"]}): {quantity} x {_format_brl(row["amount"])} = {_format_brl(total_amount)}.'
                )

    lines.append(
        'Essa conta usa apenas os valores publicos de referencia e nao inclui material, uniforme ou condicao comercial nao detalhada na base.'
    )
    if sibling_discount_note:
        lines.append(f'A base publica tambem menciona: {sibling_discount_note}')
    return '\n'.join(lines)

# Compatibility aliases while public_profile_runtime keeps facade imports.
_compose_public_feature_answer = _compose_public_feature_answer_impl
_try_public_channel_fast_answer = _try_public_channel_fast_answer_impl
_build_public_profile_context = _build_public_profile_context_impl
_handle_public_contacts = _handle_public_contacts_impl
_handle_public_timeline = _handle_public_timeline_impl
_compose_public_pricing_projection_answer = _compose_public_pricing_projection_answer_impl
