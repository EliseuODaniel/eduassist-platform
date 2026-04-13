from __future__ import annotations

# ruff: noqa: F401,F403,F405

"""Legacy public profile answer composer extracted from public_profile_runtime.py."""

LOCAL_EXTRACTED_NAMES = {'_compose_public_profile_answer_legacy'}

from . import public_profile_runtime as _native


def _intent_analysis_impl(name: str):
    from . import intent_analysis_runtime as _intent_analysis_runtime

    return getattr(_intent_analysis_runtime, name)


def _is_auth_guidance_query(message: str) -> bool:
    return _intent_analysis_impl('_is_auth_guidance_query')(message)


def _is_language_preference_query(message: str) -> bool:
    return _intent_analysis_impl('_is_language_preference_query')(message)

def _refresh_native_namespace() -> None:
    for name, value in vars(_native).items():
        if name.startswith('__') or name in LOCAL_EXTRACTED_NAMES:
            continue
        globals()[name] = value

def _compose_public_profile_answer_legacy(
    profile: dict[str, Any],
    message: str,
    *,
    original_message: str | None = None,
    conversation_context: dict[str, Any] | None = None,
    semantic_plan: PublicInstitutionPlan | None = None,
) -> str:
    _refresh_native_namespace()
    source_message = original_message or message
    normalized = _normalize_text(source_message)
    analysis_normalized = _normalize_text(message)
    school_name = str(profile.get('school_name', 'Colegio Horizonte'))
    school_reference = (
        'a escola' if _assistant_already_introduced(conversation_context) else school_name
    )
    school_reference_capitalized = (
        'A escola' if school_reference == 'a escola' else school_reference
    )
    city = str(profile.get('city', ''))
    state = str(profile.get('state', ''))
    district = str(profile.get('district', ''))
    address_line = str(profile.get('address_line', ''))
    postal_code_raw = profile.get('postal_code')
    website_url_raw = profile.get('website_url')
    fax_number_raw = profile.get('fax_number')
    curriculum_basis_raw = profile.get('curriculum_basis')
    postal_code = postal_code_raw.strip() if isinstance(postal_code_raw, str) else ''
    website_url = website_url_raw.strip() if isinstance(website_url_raw, str) else ''
    fax_number = fax_number_raw.strip() if isinstance(fax_number_raw, str) else ''
    curriculum_basis = curriculum_basis_raw.strip() if isinstance(curriculum_basis_raw, str) else ''
    curriculum_components = [
        str(item).strip()
        for item in profile.get('curriculum_components', [])
        if isinstance(item, str) and str(item).strip()
    ]
    confessional_status = str(profile.get('confessional_status', '')).strip().lower()
    segment = _select_public_segment(message)
    if segment is None:
        segment = _select_public_segment(source_message)
    schedule_context_normalized = normalized
    if _is_follow_up_query(source_message) and any(
        _message_matches_term(analysis_normalized, term) for term in PUBLIC_SCHEDULE_TERMS
    ):
        schedule_context_normalized = analysis_normalized
    shift_offers = (
        profile.get('shift_offers') if isinstance(profile.get('shift_offers'), list) else []
    )
    tuition_reference = (
        profile.get('tuition_reference')
        if isinstance(profile.get('tuition_reference'), list)
        else []
    )
    semantic_act = semantic_plan.conversation_act if semantic_plan else None
    contact_reference_message = _public_contact_reference_message(
        profile=profile,
        source_message=source_message,
        analysis_message=message,
        conversation_context=conversation_context,
    )
    preferred_contact_labels = _preferred_contact_labels_from_context(
        profile,
        source_message,
        conversation_context,
    )
    requested_channel = (
        semantic_plan.requested_channel
        if semantic_plan and semantic_plan.requested_channel
        else _requested_contact_channel(contact_reference_message)
    )
    requested_attribute_override = (
        semantic_plan.requested_attribute
        if semantic_plan and semantic_plan.requested_attribute
        else None
    )

    if _is_acknowledgement_query(source_message):
        return _compose_concierge_acknowledgement(conversation_context=conversation_context)

    if semantic_act == 'greeting' or _is_greeting_only(source_message):
        return _compose_concierge_greeting(profile, source_message, conversation_context)

    if semantic_act == 'input_clarification':
        return _compose_input_clarification_answer(
            profile,
            conversation_context=conversation_context,
        )

    if semantic_act == 'scope_boundary':
        return _compose_scope_boundary_answer(
            profile,
            conversation_context=conversation_context,
        )

    if semantic_act == 'utility_date' or _is_public_date_query(source_message):
        return f'Hoje e {_format_brazilian_date(date.today())}.'

    if semantic_act == 'auth_guidance' or _is_auth_guidance_query(source_message):
        return (
            'Para consultas protegidas, como notas, faltas e financeiro, voce precisa vincular sua conta do Telegram ao portal da escola. '
            'No portal autenticado, gere o codigo de vinculacao e depois envie aqui o comando `/start link_<codigo>`. '
            'Depois disso, eu passo a consultar seus dados autorizados por este canal.'
        )

    if semantic_act == 'language_preference' or _is_language_preference_query(source_message):
        return _compose_language_preference_answer(
            profile,
            source_message,
            conversation_context=conversation_context,
        )

    if semantic_act == 'assistant_identity' or _is_assistant_identity_query(source_message):
        return _compose_assistant_identity_answer(
            profile,
            conversation_context=conversation_context,
        )

    if semantic_act == 'service_routing' or _is_service_routing_query(source_message):
        return _compose_service_routing_answer(
            profile,
            source_message,
            conversation_context=conversation_context,
        )

    if semantic_act == 'capabilities' or _is_capability_query(source_message):
        return _compose_capability_answer(
            profile,
            conversation_context=conversation_context,
        )

    if _is_public_document_submission_query(source_message):
        return _compose_public_document_submission_answer(profile, message=source_message)

    if _is_public_teacher_identity_query(source_message):
        return _compose_public_teacher_directory_answer(profile, source_message)

    if semantic_act == 'leadership' or _is_leadership_specific_query(source_message):
        return _compose_public_leadership_answer(
            profile,
            source_message,
            requested_attribute_override=requested_attribute_override,
        )

    if semantic_act == 'web_presence' or _is_public_web_query(source_message):
        if website_url:
            return f'O site oficial de {school_reference} hoje e {website_url}.'
        return (
            f'Hoje eu nao tenho um site oficial publicado no perfil canonico de {school_reference}. '
            'Se quiser, eu posso te passar o telefone ou o email da secretaria.'
        )

    if semantic_act == 'contacts' or any(
        _message_matches_term(normalized, term) for term in PUBLIC_CONTACT_TERMS
    ):
        phone_lines = _contact_value(profile, 'telefone')
        whatsapp_lines = _contact_value(profile, 'whatsapp')
        email_lines = _contact_value(profile, 'email')
        fax_only_query = _message_matches_term(normalized, 'fax') and not any(
            _message_matches_term(normalized, term)
            for term in {'telefone', 'fone', 'ligar', 'ligo', 'whatsapp', 'email'}
        )
        if fax_only_query:
            if fax_number:
                return f'O fax institucional publicado de {school_reference} hoje e {fax_number}.'
            primary_phone = _select_primary_contact_entry(
                profile,
                'telefone',
                contact_reference_message,
                preferred_labels=preferred_contact_labels,
            )
            if primary_phone:
                return (
                    f'Hoje {school_reference} nao publica numero de fax. '
                    f'Se quiser ligar, o telefone principal e {primary_phone.get("value")}.'
                )
            return f'Hoje {school_reference} nao publica numero de fax.'
        if requested_channel == 'telefone':
            primary_phone = _select_primary_contact_entry(
                profile,
                'telefone',
                contact_reference_message,
                preferred_labels=preferred_contact_labels,
            )
            if primary_phone and (
                _contact_is_general_school_query(contact_reference_message)
                or not _wants_contact_list(contact_reference_message)
            ):
                label = primary_phone.get('label')
                value = primary_phone.get('value')
                if label:
                    response = f'O telefone principal {_school_object_reference(school_reference)} hoje e {value}, {_format_contact_origin(label, "telefone")}.'
                else:
                    response = f'O telefone principal {_school_object_reference(school_reference)} hoje e {value}.'
                if _message_matches_term(normalized, 'fax'):
                    if fax_number:
                        response += f' O fax publicado e {fax_number}.'
                    else:
                        response += ' Hoje a escola nao publica numero de fax.'
                return response
            if len(phone_lines) == 1:
                response = f'O telefone oficial de {school_reference} e {phone_lines[0]}.'
                if _message_matches_term(normalized, 'fax'):
                    response += ' Hoje a escola nao publica numero de fax.'
                return response
            lines = [f'Os telefones oficiais de {school_reference} hoje sao:']
            lines.extend(f'- {item}' for item in phone_lines)
            if _message_matches_term(normalized, 'fax'):
                lines.append('- Fax: nao publicado')
            return _render_structured_answer_lines(lines)
        if requested_channel == 'whatsapp':
            primary_whatsapp = _select_primary_contact_entry(
                profile,
                'whatsapp',
                contact_reference_message,
                preferred_labels=preferred_contact_labels,
            )
            if primary_whatsapp and (
                _contact_is_general_school_query(contact_reference_message)
                or not _wants_contact_list(contact_reference_message)
            ):
                label = primary_whatsapp.get('label')
                value = primary_whatsapp.get('value')
                if label:
                    return f'O WhatsApp mais direto {_school_object_reference(school_reference)} hoje e {value}, {_format_contact_origin(label, "whatsapp")}.'
                return f'O WhatsApp oficial {_school_object_reference(school_reference)} hoje e {value}.'
            if len(whatsapp_lines) == 1:
                return f'O WhatsApp oficial de {school_reference} hoje e {whatsapp_lines[0]}.'
            lines = [f'Os canais de WhatsApp publicados por {school_reference} hoje sao:']
            lines.extend(f'- {item}' for item in whatsapp_lines)
            return _render_structured_answer_lines(lines)
        if requested_channel == 'email':
            primary_email = _select_primary_contact_entry(
                profile,
                'email',
                contact_reference_message,
                preferred_labels=preferred_contact_labels,
            )
            if primary_email and (
                _contact_is_general_school_query(contact_reference_message)
                or not _wants_contact_list(contact_reference_message)
            ):
                label = primary_email.get('label')
                value = primary_email.get('value')
                if label:
                    return f'O email mais direto {_school_object_reference(school_reference)} hoje e {value}, {_format_contact_origin(label, "email")}.'
                return f'O email institucional publicado de {school_reference} e {value}.'
            if len(email_lines) == 1:
                return f'O email institucional publicado de {school_reference} e {email_lines[0]}.'
            lines = [f'Os emails institucionais publicados de {school_reference} hoje sao:']
            lines.extend(f'- {item}' for item in email_lines)
            return _render_structured_answer_lines(lines)
        lines = [f'Voce pode falar com {school_reference} por estes canais oficiais:']
        lines.extend(f'- {item}' for item in [*phone_lines, *whatsapp_lines, *email_lines])
        if _message_matches_term(normalized, 'fax'):
            lines.append('- Fax: nao publicado')
        return '\n'.join(lines)

    if semantic_act == 'operating_hours' or _is_public_operating_hours_query(source_message):
        return (
            f'O atendimento presencial {_school_object_reference(school_reference)} abre as 7h00 e segue ate as 17h30, de segunda a sexta-feira. '
            'Se voce estiver falando da biblioteca, ela funciona das 7h30 as 18h00.'
        )

    if semantic_act == 'location' or any(
        _message_matches_term(normalized, term) for term in PUBLIC_LOCATION_TERMS
    ):
        location = ', '.join(part for part in [address_line, district, city, state] if part)
        if postal_code:
            location = f'{location}, CEP {postal_code}'
        return f'{school_reference_capitalized} fica em {location}.'

    if semantic_act == 'confessional' or any(
        _message_matches_term(normalized, term) for term in PUBLIC_CONFESSIONAL_TERMS
    ):
        if confessional_status == 'laica':
            return (
                f'{school_reference_capitalized} e uma escola laica. '
                'A proposta institucional e plural e nao confessional.'
            )
        return f'Hoje o perfil publico classifica {school_reference} como {confessional_status}.'

    if any(_message_matches_term(normalized, term) for term in PUBLIC_LEADERSHIP_TERMS):
        return _compose_public_leadership_answer(
            profile,
            source_message,
            requested_attribute_override=requested_attribute_override,
        )

    if semantic_act == 'curriculum' or _is_public_curriculum_query(source_message):
        if curriculum_basis and curriculum_components:
            components = ', '.join(curriculum_components[:8])
            extra = ''
            if len(curriculum_components) > 8:
                extra = ', alem de projeto de vida, monitorias e trilhas eletivas'
            return (
                f'No Ensino Medio, {school_reference} segue a BNCC e um curriculo proprio de aprofundamento academico. '
                f'Os componentes que aparecem hoje na base publica incluem {components}{extra}.'
            )
        if curriculum_basis:
            return (
                f'Hoje a base curricular publica de {school_reference} e esta: {curriculum_basis}'
            )
        return (
            f'Hoje eu nao encontrei um detalhamento curricular estruturado de {school_reference}. '
            'Se quiser, eu posso resumir a proposta pedagogica publicada.'
        )

    if semantic_act == 'kpi' or any(
        _message_matches_term(normalized, term) for term in PUBLIC_KPI_TERMS
    ):
        entries = _select_public_kpis(profile, message)
        if not entries:
            return f'Hoje o perfil publico de {school_reference} nao traz indicadores institucionais publicados.'
        if len(entries) == 1:
            item = entries[0]
            notes = str(item.get('notes', '')).strip()
            return (
                f'Hoje, {item.get("label", "o indicador institucional")} esta em {item.get("value", "--")}{item.get("unit", "")} '
                f'({item.get("reference_period", "periodo nao informado")}). {notes}'.strip()
            )
        lines = [f'Os indicadores publicos mais recentes de {school_reference} sao:']
        for item in entries:
            lines.append(
                f'- {item.get("label", "Indicador")}: {item.get("value", "--")}{item.get("unit", "")} '
                f'({item.get("reference_period", "periodo nao informado")})'
            )
        return '\n'.join(lines)

    if semantic_act == 'highlight' or any(
        _message_matches_term(normalized, term) for term in PUBLIC_HIGHLIGHT_TERMS
    ):
        item = _select_public_highlight(profile, message)
        if item is None:
            return f'Hoje o perfil publico de {school_reference} nao traz diferenciais institucionais consolidados.'
        evidence_line = str(item.get('evidence_line', '')).strip()
        intro = 'Um dos diferenciais documentados desta escola'
        if any(
            _message_matches_term(normalized, term)
            for term in {'curiosidade', 'curiosidades', 'unica', 'única'}
        ):
            intro = 'Uma curiosidade documentada desta escola'
        title = str(item.get('title', 'Diferencial institucional')).strip()
        description = str(item.get('description', '')).strip()
        lines = [f'{intro} e {title}. {description}'.strip()]
        if evidence_line:
            lines.append(
                f'Isso aparece de forma bem clara na proposta institucional: {evidence_line}'
            )
        return ' '.join(line for line in lines if line)

    if semantic_act == 'visit' or any(
        _message_matches_term(normalized, term) for term in PUBLIC_VISIT_TERMS
    ):
        offers = _public_visit_offers(profile)
        services = _public_service_catalog(profile)
        if not offers:
            return f'Hoje o perfil publico de {school_reference} nao traz janelas de visita institucional.'
        lines = [
            f'Hoje {_school_subject_reference(school_reference)} publica estas janelas de visita:'
        ]
        for item in offers:
            lines.append(
                '- {title}: {day_label}, das {start_time} as {end_time}, em {location}. {notes}'.format(
                    title=item.get('title', 'Visita institucional'),
                    day_label=item.get('day_label', 'dia util'),
                    start_time=item.get('start_time', '--:--'),
                    end_time=item.get('end_time', '--:--'),
                    location=item.get('location', 'local a confirmar'),
                    notes=str(item.get('notes', '')).strip(),
                ).rstrip()
            )
        visit_service = next(
            (item for item in services if str(item.get('service_key')) == 'visita_institucional'),
            None,
        )
        if visit_service is not None:
            lines.append(
                'Agendamento: {request_channel}. Prazo de confirmacao: {typical_eta}.'.format(
                    request_channel=visit_service.get('request_channel', 'canal institucional'),
                    typical_eta=visit_service.get('typical_eta', 'ate 1 dia util'),
                )
            )
        return '\n'.join(lines)

    if semantic_act == 'pricing' or _is_public_pricing_navigation_query(message):
        relevant_rows = [
            row
            for row in tuition_reference
            if isinstance(row, dict) and (segment is None or str(row.get('segment')) == segment)
        ]
        if not relevant_rows:
            relevant_rows = [row for row in tuition_reference if isinstance(row, dict)]
        if len(relevant_rows) == 1:
            row = relevant_rows[0]
            return (
                f'Para {row.get("segment", "esse segmento")} no turno {row.get("shift_label", "regular")}, '
                f'a mensalidade publica de referencia em 2026 e {row.get("monthly_amount", "0.00")} '
                f'e a taxa de matricula e {row.get("enrollment_fee", "0.00")}. '
                f'{str(row.get("notes", "")).strip()} '
                'Se quiser, eu tambem posso resumir bolsas, descontos comerciais e canais de matricula.'
            ).strip()
        lines = ['Valores publicos de referencia para 2026:']
        for row in relevant_rows:
            lines.append(
                '- {segment} ({shift_label}): mensalidade {monthly_amount} e taxa de matricula {enrollment_fee}. {notes}'.format(
                    segment=row.get('segment', 'Segmento'),
                    shift_label=row.get('shift_label', 'turno'),
                    monthly_amount=row.get('monthly_amount', '0.00'),
                    enrollment_fee=row.get('enrollment_fee', '0.00'),
                    notes=row.get('notes', '').strip(),
                ).rstrip()
            )
        lines.append(
            'Se quiser, eu tambem posso resumir bolsas, descontos comerciais e canais de matricula.'
        )
        return '\n'.join(lines)

    feature_schedule_follow_up = _compose_public_feature_schedule_follow_up(
        profile=profile,
        original_message=source_message,
        analysis_message=message,
        conversation_context=conversation_context,
    )
    if feature_schedule_follow_up:
        return feature_schedule_follow_up

    feature_answer = _compose_public_feature_answer(
        profile=profile,
        original_message=source_message,
        analysis_message=message,
        conversation_context=conversation_context,
    )
    if semantic_act == 'features' and feature_answer:
        return feature_answer
    if feature_answer:
        return feature_answer

    if semantic_act == 'schedule' or any(
        _message_matches_term(schedule_context_normalized, term) for term in PUBLIC_SCHEDULE_TERMS
    ):
        relevant_rows = [
            row
            for row in shift_offers
            if isinstance(row, dict) and (segment is None or str(row.get('segment')) == segment)
        ]
        if not relevant_rows:
            relevant_rows = [row for row in shift_offers if isinstance(row, dict)]
        if len(relevant_rows) == 1:
            row = relevant_rows[0]
            grade_reference = _extract_grade_reference(source_message)
            if grade_reference:
                return (
                    f'O {grade_reference} fica em {row.get("segment", "esse segmento")}. '
                    f'As atividades do turno {row.get("shift_label", "regular").lower()} vao de {row.get("starts_at", "--:--")} a {row.get("ends_at", "--:--")}. '
                    f'{str(row.get("notes", "")).strip()}'
                ).strip()
            return (
                f'Para {row.get("segment", "esse segmento")}, as atividades no turno {row.get("shift_label", "regular").lower()} '
                f'vao de {row.get("starts_at", "--:--")} a {row.get("ends_at", "--:--")}. '
                f'{str(row.get("notes", "")).strip()}'
            ).strip()
        lines = ['Turnos e horarios documentados:']
        for row in relevant_rows:
            lines.append(
                '- {segment} ({shift_label}): {starts_at} as {ends_at}. {notes}'.format(
                    segment=row.get('segment', 'Segmento'),
                    shift_label=row.get('shift_label', 'turno'),
                    starts_at=row.get('starts_at', '--:--'),
                    ends_at=row.get('ends_at', '--:--'),
                    notes=row.get('notes', '').strip(),
                ).rstrip()
            )
        return '\n'.join(lines)

    if any(_message_matches_term(normalized, term) for term in PUBLIC_SEGMENT_TERMS):
        segments = profile.get('segments')
        if not isinstance(segments, list) or not segments:
            return f'Hoje o perfil publico de {school_reference} nao traz os segmentos atendidos.'
        lines = [f'Hoje {school_reference} atende estes segmentos:']
        lines.extend(f'- {item}' for item in segments if isinstance(item, str))
        return '\n'.join(lines)

    if _is_public_school_name_query(message):
        return f'O nome oficial da escola e {school_name}.'

    headline = str(profile.get('short_headline', '')).strip()
    if headline:
        return f'{school_name}: {headline}'
    return f'O nome oficial da escola e {school_name}.'
