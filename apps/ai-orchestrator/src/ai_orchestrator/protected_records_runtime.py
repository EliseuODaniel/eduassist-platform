from __future__ import annotations

# ruff: noqa: F401,F403,F405

"""Protected specialist execution helpers extracted from runtime.py.

This module is imported lazily from runtime.py after the shared helper surface is
already defined. It intentionally reuses the legacy runtime namespace during the
ongoing decomposition, so extracted functions keep behavior while the monolith
is split into focused modules.
"""

from . import runtime_core as _runtime_core


def _export_runtime_core_namespace() -> None:
    for name, value in vars(_runtime_core).items():
        if name.startswith('__'):
            continue
        globals()[name] = value


_export_runtime_core_namespace()


def _build_protected_record_specialists(
    *, preview: Any, role_code: str
) -> tuple[InternalSpecialistPlan, ...]:
    if preview.classification.domain is QueryDomain.institution and {
        'get_administrative_status',
        'get_student_administrative_status',
        'get_actor_identity_context',
    } & set(preview.selected_tools):
        return (
            InternalSpecialistPlan(
                name='protected_records',
                purpose='consultas protegidas de identidade da conta, cadastro e documentacao por aluno vinculado',
                tool_names=tuple(
                    tool_name
                    for tool_name in (
                        'get_actor_identity_context',
                        'get_administrative_status',
                        'get_student_administrative_status',
                    )
                    if tool_name in set(preview.selected_tools)
                ),
            ),
        )

    if preview.classification.domain is QueryDomain.academic and role_code == 'teacher':
        return (
            InternalSpecialistPlan(
                name='protected_records',
                purpose='consultas protegidas de agenda, turmas e disciplinas docentes',
                tool_names=('get_teacher_schedule',),
            ),
        )

    if preview.classification.domain is QueryDomain.academic:
        return (
            InternalSpecialistPlan(
                name='protected_records',
                purpose='consultas protegidas de notas, frequencia e vida academica por aluno vinculado',
                tool_names=(
                    'get_student_academic_summary',
                    'get_student_upcoming_assessments',
                    'get_student_attendance_timeline',
                ),
            ),
        )

    if preview.classification.domain is QueryDomain.finance:
        return (
            InternalSpecialistPlan(
                name='protected_records',
                purpose='consultas protegidas de faturas, contrato e situacao financeira por aluno vinculado',
                tool_names=(
                    'get_student_financial_summary',
                    'get_administrative_status',
                ),
            ),
        )

    return ()


async def _execute_teacher_protected_specialist(
    *,
    settings: Any,
    request: MessageResponseRequest,
    actor: dict[str, Any],
    conversation_context: dict[str, Any] | None = None,
) -> str:
    if request.telegram_chat_id is None:
        return _compose_structured_deny(actor)

    message = request.message
    normalized_message = _normalize_text(message)
    if not _should_fetch_teacher_schedule(
        message,
        actor=actor,
        user=request.user,
        conversation_context=conversation_context,
    ):
        return _compose_teacher_access_scope_answer(actor)

    payload: dict[str, Any] | None = None
    status_code: int | None = None
    for attempt in range(2):
        payload, status_code = await _api_core_get(
            settings=settings,
            path='/v1/teachers/me/schedule',
            params={'telegram_chat_id': request.telegram_chat_id},
        )
        if status_code == 200 and isinstance(payload, dict):
            break
        if attempt == 0:
            await asyncio.sleep(0.15)
    if status_code != 200 or payload is None:
        return (
            'Nao consegui abrir sua grade docente agora. '
            'Eu reconheci seu perfil de professor, mas a consulta protegida de agenda nao respondeu a tempo. '
            'Tente novamente em instantes.'
        )

    summary = payload.get('summary', {})
    if not isinstance(summary, dict):
        return 'Nao consegui interpretar o retorno da grade docente.'
    if any(
        term in normalized_message
        for term in {
            'rotina docente',
            'resuma minha rotina docente',
            'resumo enxuto',
            'alocacao',
            'alocação',
        }
    ):
        return _compose_teacher_schedule_summary_answer(
            summary,
            profile=await _fetch_public_school_profile(settings=settings),
            message=message,
        )
    answer_text = _render_teacher_schedule_answer(summary, message=message)
    if 'horario' in normalized_message or 'agenda' in normalized_message:
        return (
            f'{answer_text}\n'
            'Nesta base atual, o detalhamento por bloco de horario ainda nao foi modelado; '
            'por enquanto eu mostro suas alocacoes de turmas e disciplinas.'
        )
    return answer_text


async def _execute_protected_records_specialist(
    *,
    settings: Any,
    request: MessageResponseRequest,
    preview: Any,
    actor: dict[str, Any],
    conversation_context: dict[str, Any] | None = None,
) -> str:
    if request.telegram_chat_id is None:
        return _compose_structured_deny(actor)

    message = request.message
    if _is_meta_repair_context_query(message):
        meta_repair_answer = _compose_meta_repair_follow_up_answer(conversation_context)
        if meta_repair_answer:
            return meta_repair_answer
    if _is_public_pricing_navigation_query(message) or _is_public_pricing_context_follow_up(
        message,
        conversation_context=conversation_context,
    ):
        profile = await _fetch_public_school_profile(settings=settings)
        if isinstance(profile, dict):
            public_plan = _build_public_institution_plan(
                message,
                ['get_public_school_profile'],
                semantic_plan=None,
                conversation_context=conversation_context,
                school_profile=profile,
            )
            return _compose_public_profile_answer(
                profile,
                message,
                actor=actor,
                original_message=message,
                conversation_context=conversation_context,
                semantic_plan=public_plan,
            )
    normalized_message = _normalize_text(message)
    wants_admin_status = _mentions_personal_admin_status(message)
    wants_profile_update = _wants_profile_update_guidance(message)
    requested_admin_attribute = _detect_admin_attribute_request(
        message,
        conversation_context=conversation_context,
    )
    force_family_admin_aggregate = _looks_like_family_admin_aggregate_query(message)
    force_family_finance_aggregate = _looks_like_family_finance_aggregate_query(message)
    recent_focus = _recent_trace_focus(conversation_context) or {}
    recent_active_task = str(recent_focus.get('active_task', '') or '').strip()
    wants_family_next_due = any(
        _message_matches_term(normalized_message, term)
        for term in {
            'proximo vencimento',
            'próximo vencimento',
            'proxima fatura',
            'próxima fatura',
            'vence primeiro',
        }
    )
    if not force_family_finance_aggregate and wants_family_next_due and recent_active_task.startswith('finance:'):
        force_family_finance_aggregate = True
    force_family_attendance_aggregate = _looks_like_family_attendance_aggregate_query(message)
    force_family_academic_aggregate = _looks_like_family_academic_aggregate_query(message)
    explicit_academic_student = (
        len(_matching_students_in_text(_eligible_students(actor, capability='academic'), message))
        == 1
    )
    if explicit_academic_student:
        force_family_academic_aggregate = False
    admin_finance_follow_up = _recent_admin_finance_combo_context(conversation_context) and any(
        _message_matches_term(normalized_message, term)
        for term in {
            'regularizar',
            'proximo passo',
            'próximo passo',
            'em aberto',
            'bloqueio',
            'bloqueando atendimento',
            'nada estiver bloqueando',
            'se nada estiver bloqueando',
            'fala isso de forma direta',
        }
    )
    finance_only_follow_up = admin_finance_follow_up and any(
        _message_matches_term(normalized_message, term)
        for term in {
            'o que esta em aberto no financeiro',
            'o que está em aberto no financeiro',
            'em aberto no financeiro',
            'financeiro dela',
            'financeiro dele',
            'financeiro da ana',
            'financeiro do lucas',
            'faturas em aberto',
            'boletos em aberto',
        }
    )
    direct_block_follow_up = admin_finance_follow_up and any(
        _message_matches_term(normalized_message, term)
        for term in {
            'nada estiver bloqueando',
            'se nada estiver bloqueando',
            'fala isso de forma direta',
            'fala isso direto',
            'se houver bloqueio fala direto',
        }
    )
    explicit_student_admin_request = (
        requested_admin_attribute is not None
        and not any(
            _message_matches_term(normalized_message, term)
            for term in {'financeiro', 'boleto', 'boletos', 'fatura', 'faturas', 'mensalidade'}
        )
        and _effective_finance_attribute_request(
            message,
            conversation_context=conversation_context,
        )
        is None
        and not admin_finance_follow_up
        and _should_use_student_administrative_status(
            actor,
            message,
            conversation_context=conversation_context,
        )
    )
    if (
        _is_access_scope_query(message)
        or _is_access_scope_repair_query(
            message,
            actor,
            conversation_context,
        )
    ) and not _should_prioritize_protected_sql_query(
        message,
        actor=actor,
        conversation_context=conversation_context,
    ):
        return _compose_account_context_answer(
            actor,
            request_message=message,
            conversation_context=conversation_context,
        )
    if _is_actor_identity_query(message):
        return _compose_actor_identity_answer(actor)
    if force_family_admin_aggregate:
        summaries: list[dict[str, Any]] = []
        for candidate in _linked_students(actor):
            candidate_id = candidate.get('student_id')
            if not isinstance(candidate_id, str):
                continue
            payload, status_code = await _api_core_get(
                settings=settings,
                path=f'/v1/students/{candidate_id}/administrative-status',
                params={'telegram_chat_id': request.telegram_chat_id},
            )
            summary = payload.get('summary') if isinstance(payload, dict) else None
            if status_code == 200 and isinstance(summary, dict):
                summaries.append(summary)
        if summaries:
            return _compose_family_admin_aggregate_answer(summaries)
    if _is_public_document_submission_query(message):
        if _message_matches_term(normalized_message, 'fax'):
            return (
                'Hoje a escola nao utiliza fax para envio de documentos. '
                'Para isso, use portal institucional, email da secretaria, secretaria presencial.'
            )
        if _message_matches_term(normalized_message, 'telegrama'):
            return (
                'Hoje a escola nao publica telegrama como canal valido para documentos. '
                'Para isso, use portal institucional, email da secretaria, secretaria presencial.'
            )
        if _message_matches_term(normalized_message, 'caixa postal'):
            return (
                'Hoje a escola nao trabalha com caixa postal para esse tipo de envio. '
                'Para documentos, use portal institucional, email da secretaria, secretaria presencial.'
            )
        return 'Para enviar documentos hoje, use portal institucional, email da secretaria ou secretaria presencial.'
    linked_students = _linked_students(actor)
    unmatched_student_name = None
    if (
        not force_family_finance_aggregate
        and not force_family_attendance_aggregate
        and not force_family_academic_aggregate
    ):
        unmatched_student_name = _explicit_unmatched_student_reference(
            linked_students,
            message,
            conversation_context=conversation_context,
        )
    if linked_students and unmatched_student_name:
        return _compose_unmatched_student_reference_answer(
            requested_name=unmatched_student_name,
            students=linked_students,
        )

    slot_memory = _build_conversation_slot_memory(
        actor=actor,
        profile=None,
        conversation_context=conversation_context,
        request_message=message,
        preview=preview,
    )

    explicit_guardian_admin_request = (
        wants_admin_status
        and requested_admin_attribute is not None
        and _effective_finance_attribute_request(
            message,
            conversation_context=conversation_context,
        )
        is None
        and not any(
            _message_matches_term(normalized_message, term)
            for term in {
                'financeiro',
                'boleto',
                'boletos',
                'fatura',
                'faturas',
                'mensalidade',
                'pagamento',
            }
        )
    )

    if force_family_attendance_aggregate:
        academic_students = _eligible_students(actor, capability='academic')
        summaries: list[dict[str, Any]] = []
        for candidate in academic_students:
            candidate_id = candidate.get('student_id')
            if not isinstance(candidate_id, str):
                continue
            payload, status_code = await _api_core_get(
                settings=settings,
                path=f'/v1/students/{candidate_id}/academic-summary',
                params={'telegram_chat_id': request.telegram_chat_id},
            )
            if status_code == 200 and isinstance(payload, dict):
                summary = payload.get('summary')
                if isinstance(summary, dict):
                    summaries.append(summary)
        if summaries:
            return _compose_family_attendance_aggregate_answer(summaries)
        academic_names = [
            str(student.get('full_name') or '').strip()
            for student in academic_students
            if str(student.get('full_name') or '').strip()
        ]
        if academic_names:
            return (
                'Panorama de frequencia das contas vinculadas: '
                + ', '.join(academic_names)
                + '. Nao consegui carregar agora o detalhamento objetivo de faltas e atrasos.'
            )

    if force_family_academic_aggregate:
        academic_students = _eligible_students(actor, capability='academic')
        if _wants_upcoming_assessments(message) and academic_students:
            upcoming_summaries: list[tuple[str, dict[str, Any], dict[str, Any]]] = []
            for candidate in academic_students:
                candidate_id = candidate.get('student_id')
                candidate_name = str(candidate.get('full_name') or 'Aluno').strip() or 'Aluno'
                if not isinstance(candidate_id, str):
                    continue
                academic_payload, academic_status = await _api_core_get(
                    settings=settings,
                    path=f'/v1/students/{candidate_id}/academic-summary',
                    params={'telegram_chat_id': request.telegram_chat_id},
                )
                academic_summary = (
                    academic_payload.get('summary') if isinstance(academic_payload, dict) else None
                )
                upcoming_payload, upcoming_status = await _api_core_get(
                    settings=settings,
                    path=f'/v1/students/{candidate_id}/upcoming-assessments',
                    params={'telegram_chat_id': request.telegram_chat_id},
                )
                upcoming_summary = (
                    upcoming_payload.get('summary') if isinstance(upcoming_payload, dict) else None
                )
                if (
                    academic_status == 200
                    and upcoming_status == 200
                    and isinstance(academic_summary, dict)
                    and isinstance(upcoming_summary, dict)
                ):
                    upcoming_summaries.append((candidate_name, academic_summary, upcoming_summary))
            if upcoming_summaries:
                return _compose_family_upcoming_assessments_answer(upcoming_summaries)
        summaries: list[dict[str, Any]] = []
        for candidate in academic_students:
            candidate_id = candidate.get('student_id')
            if not isinstance(candidate_id, str):
                continue
            payload, status_code = await _api_core_get(
                settings=settings,
                path=f'/v1/students/{candidate_id}/academic-summary',
                params={'telegram_chat_id': request.telegram_chat_id},
            )
            if status_code == 200 and isinstance(payload, dict):
                summary = payload.get('summary')
                if isinstance(summary, dict):
                    summaries.append(summary)
        if summaries:
            return _compose_academic_aggregate_answer(summaries)
        academic_names = [
            str(student.get('full_name') or '').strip()
            for student in academic_students
            if str(student.get('full_name') or '').strip()
        ]
        if academic_names:
            return (
                'Panorama academico das contas vinculadas: '
                f'{", ".join(academic_names)}. '
                'Nao consegui carregar agora o detalhamento objetivo por disciplina, '
                'mas o foco continua sendo comparar os alunos vinculados desta conta.'
            )

    if (
        preview.classification.domain is QueryDomain.institution
        and 'get_actor_identity_context' in preview.selected_tools
    ):
        return _compose_account_context_answer(
            actor,
            request_message=message,
            conversation_context=conversation_context,
        )

    if explicit_guardian_admin_request:
        payload, status_code = await _api_core_get(
            settings=settings,
            path='/v1/actors/me/administrative-status',
            params={'telegram_chat_id': request.telegram_chat_id},
        )
        if status_code == 403:
            return 'Seu perfil nao tem permissao para consultar esse status administrativo.'
        if status_code != 200 or payload is None:
            return 'Nao consegui consultar seu cadastro administrativo agora. Tente novamente em instantes.'
        summary = payload.get('summary', {})
        if not isinstance(summary, dict):
            return 'Nao consegui interpretar o retorno administrativo desta consulta.'
        return '\n'.join(
            _format_administrative_status(
                summary,
                profile_update=wants_profile_update,
                requested_attribute=requested_admin_attribute,
            )
        )

    if explicit_student_admin_request:
        preview.classification = IntentClassification(
            domain=QueryDomain.institution,
            access_tier=AccessTier.authenticated,
            confidence=0.9,
            reason='follow-up administrativo de aluno exige service deterministico e estado tipado',
        )
        preview.selected_tools = ['get_administrative_status', 'get_student_administrative_status']
        return await _compose_student_administrative_status_answer(
            settings=settings,
            request=request,
            actor=actor,
            message=message,
            conversation_context=conversation_context,
            requested_attribute=requested_admin_attribute,
        )

    if _is_admin_finance_combined_query(message) or admin_finance_follow_up:
        scoped_finance_student, scoped_finance_error = _select_linked_student(
            actor,
            message,
            capability='finance',
            conversation_context=conversation_context,
        )
        if scoped_finance_student is None and admin_finance_follow_up:
            scoped_finance_student = _student_from_slot_memory(
                actor,
                capability='finance',
                slot_memory=slot_memory,
            ) or _recent_student_from_context(
                actor,
                capability='finance',
                conversation_context=conversation_context,
            )
            if scoped_finance_student is not None:
                scoped_finance_error = None
        if scoped_finance_error and bool(
            _matching_students_in_text(_eligible_students(actor, capability='finance'), message)
        ):
            return scoped_finance_error
        if isinstance(scoped_finance_student, dict):
            student_id = scoped_finance_student.get('student_id')
            if isinstance(student_id, str):
                admin_payload, admin_status_code = await _api_core_get(
                    settings=settings,
                    path=f'/v1/students/{student_id}/administrative-status',
                    params={'telegram_chat_id': request.telegram_chat_id},
                )
                admin_summary = (
                    admin_payload.get('summary') if isinstance(admin_payload, dict) else None
                )
                finance_payload, finance_status_code = await _api_core_get(
                    settings=settings,
                    path=f'/v1/students/{student_id}/financial-summary',
                    params={'telegram_chat_id': request.telegram_chat_id},
                )
                finance_summary = (
                    finance_payload.get('summary') if isinstance(finance_payload, dict) else None
                )
                finance_summaries = (
                    [finance_summary]
                    if finance_status_code == 200 and isinstance(finance_summary, dict)
                    else []
                )
                direct_block_answer = _compose_admin_finance_block_status_answer(
                    admin_summary=admin_summary
                    if admin_status_code == 200 and isinstance(admin_summary, dict)
                    else None,
                    finance_summaries=finance_summaries,
                )
                if direct_block_follow_up and direct_block_answer:
                    return direct_block_answer
                if finance_only_follow_up and finance_summaries:
                    return _compose_finance_aggregate_answer(finance_summaries)
                scoped_combined_answer = _compose_admin_finance_combined_answer(
                    admin_summary=admin_summary
                    if admin_status_code == 200 and isinstance(admin_summary, dict)
                    else None,
                    finance_summaries=finance_summaries,
                    requested_admin_attribute=requested_admin_attribute,
                )
                if scoped_combined_answer:
                    return scoped_combined_answer
        admin_payload, admin_status_code = await _api_core_get(
            settings=settings,
            path='/v1/actors/me/administrative-status',
            params={'telegram_chat_id': request.telegram_chat_id},
        )
        admin_summary = admin_payload.get('summary') if isinstance(admin_payload, dict) else None
        finance_summaries: list[dict[str, Any]] = []
        for student in _eligible_students(actor, capability='finance'):
            student_id = student.get('student_id')
            if not isinstance(student_id, str):
                continue
            payload, status_code = await _api_core_get(
                settings=settings,
                path=f'/v1/students/{student_id}/financial-summary',
                params={'telegram_chat_id': request.telegram_chat_id},
            )
            summary = payload.get('summary') if isinstance(payload, dict) else None
            if status_code == 200 and isinstance(summary, dict):
                finance_summaries.append(summary)
        combined_answer = _compose_admin_finance_combined_answer(
            admin_summary=admin_summary if admin_status_code == 200 else None,
            finance_summaries=finance_summaries,
            requested_admin_attribute=requested_admin_attribute,
        )
        if direct_block_follow_up:
            direct_block_answer = _compose_admin_finance_block_status_answer(
                admin_summary=admin_summary
                if admin_status_code == 200 and isinstance(admin_summary, dict)
                else None,
                finance_summaries=finance_summaries,
            )
            if direct_block_answer:
                return direct_block_answer
        if finance_only_follow_up and finance_summaries:
            return _compose_finance_aggregate_answer(finance_summaries)
        if combined_answer:
            return combined_answer

    if preview.classification.domain is QueryDomain.institution and (
        'get_administrative_status' in preview.selected_tools
        or 'get_student_administrative_status' in preview.selected_tools
    ):
        if (
            'get_student_administrative_status' in preview.selected_tools
            and _should_use_student_administrative_status(
                actor,
                message,
                conversation_context=conversation_context,
            )
        ):
            return await _compose_student_administrative_status_answer(
                settings=settings,
                request=request,
                actor=actor,
                message=message,
                conversation_context=conversation_context,
                requested_attribute=requested_admin_attribute,
            )

        payload, status_code = await _api_core_get(
            settings=settings,
            path='/v1/actors/me/administrative-status',
            params={'telegram_chat_id': request.telegram_chat_id},
        )
        if status_code == 403:
            return 'Seu perfil nao tem permissao para consultar esse status administrativo.'
        if status_code != 200 or payload is None:
            return 'Nao consegui consultar seu cadastro administrativo agora. Tente novamente em instantes.'

        summary = payload.get('summary', {})
        if not isinstance(summary, dict):
            return 'Nao consegui interpretar o retorno administrativo desta consulta.'
        return '\n'.join(
            _format_administrative_status(
                summary,
                profile_update=wants_profile_update,
                requested_attribute=requested_admin_attribute,
            )
        )

    if preview.classification.domain is QueryDomain.finance:
        requested_status = _effective_finance_status_filter(
            message,
            conversation_context=conversation_context,
        )
        finance_attribute_request = _effective_finance_attribute_request(
            message,
            conversation_context=conversation_context,
        )
        wants_second_copy = _wants_finance_second_copy(
            message,
            conversation_context=conversation_context,
        )
        include_admin_section = 'get_administrative_status' in preview.selected_tools and (
            wants_admin_status or wants_profile_update
        )
        finance_students = _eligible_students(actor, capability='finance')
        if force_family_finance_aggregate and finance_students:
            summaries: list[dict[str, Any]] = []
            for candidate in finance_students:
                candidate_id = candidate.get('student_id')
                if not isinstance(candidate_id, str):
                    continue
                payload, status_code = await _api_core_get(
                    settings=settings,
                    path=f'/v1/students/{candidate_id}/financial-summary',
                    params={'telegram_chat_id': request.telegram_chat_id},
                )
                if status_code == 200 and isinstance(payload, dict):
                    summary = payload.get('summary')
                    if isinstance(summary, dict):
                        summaries.append(summary)
            if summaries:
                if finance_attribute_request is not None and finance_attribute_request.attribute == 'next_due':
                    family_next_due_answer = _compose_family_next_due_answer(summaries)
                    if family_next_due_answer:
                        return family_next_due_answer
                return _compose_finance_aggregate_answer(summaries)
            finance_names = [
                str(student.get('full_name') or '').strip()
                for student in finance_students
                if str(student.get('full_name') or '').strip()
            ]
            if finance_names:
                return (
                    'Resumo financeiro da familia hoje: '
                    f'{", ".join(finance_names)}. '
                    'Nao consegui carregar agora os vencimentos e proximos passos detalhados, '
                    'mas o recorte continua sendo o financeiro das contas vinculadas.'
                )
        if len(finance_students) > 1:
            student, clarification = _select_linked_student(
                actor,
                message,
                capability='finance',
                conversation_context=conversation_context,
            )
            if student is None:
                student = _student_from_slot_memory(
                    actor,
                    capability='finance',
                    slot_memory=slot_memory,
                )
                if student is not None:
                    clarification = None
            if student is None and clarification is not None:
                if finance_attribute_request is not None:
                    return clarification
                summaries: list[dict[str, Any]] = []
                for candidate in finance_students:
                    candidate_id = candidate.get('student_id')
                    if not isinstance(candidate_id, str):
                        continue
                    payload, status_code = await _api_core_get(
                        settings=settings,
                        path=f'/v1/students/{candidate_id}/financial-summary',
                        params={'telegram_chat_id': request.telegram_chat_id},
                    )
                    if status_code == 200 and isinstance(payload, dict):
                        summary = payload.get('summary')
                        if isinstance(summary, dict):
                            summaries.append(summary)

                if summaries and not any(
                    _normalize_text(str(student.get('full_name', ''))) in normalized_message
                    for student in finance_students
                ):
                    if finance_attribute_request is not None and finance_attribute_request.attribute == 'next_due':
                        family_next_due_answer = _compose_family_next_due_answer(summaries)
                        if family_next_due_answer:
                            return family_next_due_answer
                    lines = _compose_finance_aggregate_answer(summaries).splitlines()
                    filtered_any = any(
                        _filter_invoice_rows(summary, status_filter=requested_status)
                        for summary in summaries
                    )
                    if requested_status and not filtered_any:
                        lines.extend(_finance_empty_lines(requested_status))
                    if wants_second_copy:
                        lines.append(
                            'A emissao automatica de segunda via ainda entra na proxima etapa; '
                            'por enquanto eu consigo informar a situacao das faturas.'
                        )
                    if include_admin_section:
                        admin_payload, admin_status_code = await _api_core_get(
                            settings=settings,
                            path='/v1/actors/me/administrative-status',
                            params={'telegram_chat_id': request.telegram_chat_id},
                        )
                        admin_summary = (
                            admin_payload.get('summary')
                            if isinstance(admin_payload, dict)
                            else None
                        )
                        if admin_status_code == 200 and isinstance(admin_summary, dict):
                            lines.append('')
                            lines.append('Cadastro e documentacao:')
                            lines.extend(
                                _format_administrative_status(
                                    admin_summary,
                                    profile_update=wants_profile_update,
                                    requested_attribute=requested_admin_attribute,
                                )
                            )
                    return '\n'.join(lines)

    requested_capability = (
        'finance' if preview.classification.domain is QueryDomain.finance else 'academic'
    )
    student, clarification = _select_linked_student(
        actor,
        message,
        capability=requested_capability,
        conversation_context=conversation_context,
    )
    if student is None:
        student = _student_from_slot_memory(
            actor,
            capability=requested_capability,
            slot_memory=slot_memory,
        )
        if student is not None:
            clarification = None
    if clarification is not None:
        return clarification
    if student is None:
        return 'Nao encontrei um aluno elegivel para essa consulta no Telegram.'

    student_id = student.get('student_id')
    student_name = student.get('full_name', 'Aluno')
    if not isinstance(student_id, str):
        return 'Nao consegui identificar o aluno desta consulta. Tente novamente pelo portal.'

    if preview.classification.domain is QueryDomain.academic:
        recent_missing_subject = _recent_missing_academic_subject_context(conversation_context)
        if (
            _wants_missing_subject_explanation_follow_up(
                message,
                conversation_context=conversation_context,
            )
            and recent_missing_subject is not None
        ):
            return _compose_missing_subject_explanation_answer(
                student_name=recent_missing_subject['student_name'],
                subject_label=recent_missing_subject['subject_label'],
            )
        academic_attribute_request = _effective_academic_attribute_request(
            message,
            conversation_context=conversation_context,
        )
        academic_family_focus_follow_up = _looks_like_family_academic_student_focus_followup(
            actor,
            message,
            conversation_context=conversation_context,
        )
        academic_risk_follow_up = any(
            _message_matches_term(normalized_message, term)
            for term in {
                'risco academico',
                'risco acadêmico',
                'maior risco',
                'pontos academicos que mais preocupam',
                'pontos acadêmicos que mais preocupam',
                'pontos academicos',
                'pontos acadêmicos',
                'mais preocupam',
                'mais vulneravel',
                'mais vulnerável',
                'mais perto da media',
                'mais perto da média',
                'menores medias',
                'menores médias',
                'menor media',
                'menor média',
                'piores medias',
                'piores médias',
                'preocupacao academica',
                'preocupação acadêmica',
                'preocupacoes academicas',
                'preocupações acadêmicas',
            }
        )
        academic_difficulty_follow_up = _looks_like_academic_difficulty_query(
            message,
            conversation_context=conversation_context,
        )
        if academic_family_focus_follow_up:
            academic_attribute_request = None
            academic_difficulty_follow_up = True
        payload, status_code = await _api_core_get(
            settings=settings,
            path=f'/v1/students/{student_id}/academic-summary',
            params={'telegram_chat_id': request.telegram_chat_id},
        )
        if status_code == 403:
            if (
                academic_attribute_request is not None
                or academic_risk_follow_up
                or academic_difficulty_follow_up
            ):
                return (
                    f'{student_name} e o foco desta consulta academica. '
                    'Nao consegui carregar agora o resumo academico detalhado para apontar com seguranca os maiores riscos.'
                )
            return 'Seu perfil nao tem permissao para consultar esses dados academicos.'
        if status_code != 200 or payload is None:
            if (
                academic_attribute_request is not None
                or academic_risk_follow_up
                or academic_difficulty_follow_up
            ):
                return (
                    f'{student_name} e o foco desta consulta academica. '
                    'Nao consegui carregar agora o resumo academico detalhado para apontar com seguranca os maiores riscos.'
                )
            return 'Nao consegui consultar os dados academicos agora. Tente novamente em instantes.'

        summary = payload.get('summary', {})
        if not isinstance(summary, dict):
            return 'Nao consegui interpretar o retorno academico desta consulta.'

        if academic_attribute_request is not None and (
            _wants_upcoming_assessments(message) or _wants_attendance_timeline(message)
        ):
            academic_attribute_request = None
        if academic_attribute_request is not None:
            return _compose_academic_attribute_answer(
                summary,
                attribute_request=academic_attribute_request,
                student_name=student_name,
                message=message,
                conversation_context=conversation_context,
            )
        if academic_risk_follow_up:
            return _compose_academic_risk_answer(summary, student_name=student_name)
        if academic_difficulty_follow_up:
            return _compose_academic_difficulty_answer(summary, student_name=student_name)

        focus_kind = _detect_academic_focus_kind(message) or _recent_slot_value(
            conversation_context,
            'academic_focus_kind',
        )
        term_filter = _extract_term_filter(message)
        context_focus = focus_kind
        if focus_kind == 'upcoming' and not _is_follow_up_query(message):
            context_focus = None
        subject_filter = _detect_subject_filter(
            message,
            summary,
            conversation_context=conversation_context,
            focus_kind=context_focus,
        )
        requested_subject_label = _requested_subject_label_from_message(message)
        unknown_subject_label = (
            None
            if requested_subject_label
            else _extract_unknown_subject_reference(
                message,
                summary=summary,
            )
        )
        missing_subject_label = requested_subject_label or unknown_subject_label
        subject_code = _subject_code_for_filter(summary, subject_filter)
        if missing_subject_label and not subject_filter:
            if _wants_upcoming_assessments(message):
                return (
                    f'Hoje eu nao encontrei proximas avaliacoes de {student_name} em {missing_subject_label} '
                    'no recorte academico desta conta.'
                )
            if _wants_attendance_timeline(message) or (
                _contains_any(message, ATTENDANCE_TERMS) and not _contains_any(message, GRADE_TERMS)
            ):
                return (
                    f'Hoje eu nao encontrei registros de frequencia de {student_name} em {missing_subject_label} '
                    'no recorte academico desta conta.'
                )
            if (
                _contains_any(message, GRADE_TERMS)
                or _effective_academic_attribute_request(
                    message,
                    conversation_context=conversation_context,
                )
                is not None
            ):
                return (
                    f'Hoje eu nao encontrei notas de {student_name} em {missing_subject_label} '
                    'no recorte academico desta conta.'
                )

        if _wants_upcoming_assessments(message) or focus_kind == 'upcoming':
            upcoming_payload, upcoming_status_code = await _api_core_get(
                settings=settings,
                path=f'/v1/students/{student_id}/upcoming-assessments',
                params={
                    'telegram_chat_id': request.telegram_chat_id,
                    **({'subject_code': subject_code} if subject_code else {}),
                },
            )
            if upcoming_status_code == 403:
                return 'Seu perfil nao tem permissao para consultar as proximas avaliacoes deste aluno.'
            if upcoming_status_code != 200 or upcoming_payload is None:
                return 'Nao consegui consultar as proximas avaliacoes agora. Tente novamente em instantes.'
            upcoming_summary = upcoming_payload.get('summary', {})
            if not isinstance(upcoming_summary, dict):
                return 'Nao consegui interpretar o retorno das proximas avaliacoes.'
            lines = [
                f'Proximas avaliacoes de {student_name}:',
                f'- Turma: {summary.get("class_name", "nao informada")}',
            ]
            if subject_filter:
                lines.append(f'- Disciplina filtrada: {subject_filter.title()}')
            lines.extend(_format_upcoming_assessments(upcoming_summary))
            return '\n'.join(lines)

        if _wants_attendance_timeline(message) or focus_kind == 'attendance_timeline':
            timeline_payload, timeline_status_code = await _api_core_get(
                settings=settings,
                path=f'/v1/students/{student_id}/attendance-timeline',
                params={
                    'telegram_chat_id': request.telegram_chat_id,
                    **({'subject_code': subject_code} if subject_code else {}),
                },
            )
            if timeline_status_code == 403:
                return (
                    'Seu perfil nao tem permissao para consultar as faltas detalhadas deste aluno.'
                )
            if timeline_status_code != 200 or timeline_payload is None:
                return (
                    'Nao consegui consultar as faltas com data agora. Tente novamente em instantes.'
                )
            timeline_summary = timeline_payload.get('summary', {})
            if not isinstance(timeline_summary, dict):
                return 'Nao consegui interpretar o retorno detalhado de frequencia.'
            lines = [
                f'Registros de frequencia de {student_name}:',
                f'- Turma: {summary.get("class_name", "nao informada")}',
            ]
            if subject_filter:
                lines.append(f'- Disciplina filtrada: {subject_filter.title()}')
            lines.extend(_format_attendance_timeline(timeline_summary))
            return '\n'.join(lines)

        filtered_grades = _filter_grade_rows(
            summary, subject_filter=subject_filter, term_filter=term_filter
        )
        filtered_attendance = _filter_attendance_rows(summary, subject_filter=subject_filter)
        filtered_summary = dict(summary)
        filtered_summary['grades'] = filtered_grades
        filtered_summary['attendance'] = filtered_attendance

        focus_attendance = _contains_any(message, ATTENDANCE_TERMS) and not _contains_any(
            message, GRADE_TERMS
        )
        lines = [
            f'Resumo academico de {student_name}:',
            f'- Turma: {summary.get("class_name", "nao informada")}',
            f'- Serie atual: {summary.get("grade_level", "nao informada")}',
        ]
        if subject_filter:
            lines.append(f'- Disciplina filtrada: {subject_filter.title()}')
        if term_filter:
            lines.append(f'- Bimestre filtrado: {term_filter[-1]}')
        if focus_attendance:
            if _message_matches_term(_normalize_text(message), 'frequencia') and not _contains_any(
                message, {'falta', 'faltas'}
            ):
                lines[0] = f'Panorama de frequencia de {student_name}:'
                lines.append('Resumo geral:')
                lines.extend(_format_attendance_overview(filtered_summary))
            else:
                lines.append('Frequencia:')
                lines.extend(_format_attendance(filtered_summary))
            lines.append('Notas mais recentes:')
            lines.extend(_format_grades(filtered_summary))
        else:
            lines.append('Notas mais recentes:')
            lines.extend(_format_grades(filtered_summary))
            lines.append('Frequencia:')
            lines.extend(_format_attendance(filtered_summary))
        return '\n'.join(lines)

    payload, status_code = await _api_core_get(
        settings=settings,
        path=f'/v1/students/{student_id}/financial-summary',
        params={'telegram_chat_id': request.telegram_chat_id},
    )
    if status_code == 403:
        return 'Seu perfil nao tem permissao para consultar esses dados financeiros.'
    if status_code != 200 or payload is None:
        return 'Nao consegui consultar o resumo financeiro agora. Tente novamente em instantes.'

    summary = payload.get('summary', {})
    if not isinstance(summary, dict):
        return 'Nao consegui interpretar o retorno financeiro desta consulta.'

    requested_status = _effective_finance_status_filter(
        message,
        conversation_context=conversation_context,
    )
    wants_second_copy = _wants_finance_second_copy(
        message,
        conversation_context=conversation_context,
    )
    finance_attribute_request = _effective_finance_attribute_request(
        message,
        conversation_context=conversation_context,
    )
    if finance_attribute_request is not None:
        return _compose_finance_attribute_answer(
            summary,
            attribute_request=finance_attribute_request,
            status_filter=requested_status,
            wants_second_copy=wants_second_copy,
        )
    filtered_invoices = _filter_invoice_rows(summary, status_filter=requested_status)
    if _wants_finance_count_summary(message) and requested_status == {'overdue'}:
        overdue_count = len(filtered_invoices)
        if overdue_count == 0:
            return f'Hoje {student_name} nao tem mensalidades vencidas.'
        plural = 'mensalidade vencida' if overdue_count == 1 else 'mensalidades vencidas'
        return f'Hoje {student_name} tem {overdue_count} {plural}.'
    include_admin_section = 'get_administrative_status' in preview.selected_tools and (
        wants_admin_status or wants_profile_update
    )
    lines = [
        f'Resumo financeiro de {summary.get("student_name", student_name)}:',
        f'- Contrato: {summary.get("contract_code", "nao informado")}',
        f'- Responsavel financeiro: {summary.get("guardian_name", "nao informado")}',
        f'- Mensalidade base: {summary.get("monthly_amount", "0.00")}',
        f'- Faturas em aberto: {summary.get("open_invoice_count", 0)}',
        f'- Faturas vencidas: {summary.get("overdue_invoice_count", 0)}',
    ]
    if requested_status == {'paid'}:
        lines.append('Faturas pagas:')
    elif requested_status == {'overdue'}:
        lines.append('Faturas vencidas:')
    elif requested_status == {'open', 'overdue'}:
        lines.append('Faturas em aberto ou vencidas:')
    else:
        lines.append('Ultimas faturas:')
    lines.extend(_format_invoice_lines(filtered_invoices, status_filter=requested_status))
    if wants_second_copy:
        lines.append(
            'A emissao automatica de segunda via ainda entra na proxima etapa; '
            'por enquanto eu consigo informar a situacao e os vencimentos.'
        )
    if include_admin_section:
        admin_payload, admin_status_code = await _api_core_get(
            settings=settings,
            path='/v1/actors/me/administrative-status',
            params={'telegram_chat_id': request.telegram_chat_id},
        )
        admin_summary = admin_payload.get('summary') if isinstance(admin_payload, dict) else None
        if admin_status_code == 200 and isinstance(admin_summary, dict):
            lines.append('')
            lines.append('Cadastro e documentacao:')
            lines.extend(
                _format_administrative_status(
                    admin_summary,
                    profile_update=wants_profile_update,
                    requested_attribute=requested_admin_attribute,
                )
            )
    return '\n'.join(lines)
