from __future__ import annotations

# ruff: noqa: F401,F403,F405
"""Answer verification and polish guard helpers extracted from runtime.py."""

from . import runtime_core as _runtime_core


def _export_runtime_core_namespace() -> None:
    for name, value in vars(_runtime_core).items():
        if name.startswith('__'):
            continue
        globals()[name] = value


_export_runtime_core_namespace()


def _build_runtime_evidence_pack(
    *,
    request_message: str,
    message_text: str,
    preview: OrchestrationPreview,
    selected_tools: list[str],
    citations: list[MessageResponseCitation],
    school_profile: dict[str, Any] | None,
    actor: dict[str, Any] | None,
    conversation_context: dict[str, Any] | None,
    public_plan: PublicInstitutionPlan | None,
    retrieval_backend: RetrievalBackend,
) -> MessageEvidencePack | None:
    normalized_tools = list(dict.fromkeys(tool_name for tool_name in selected_tools if tool_name))
    if citations:
        return build_retrieval_evidence_pack(
            citations=citations,
            selected_tools=normalized_tools,
            retrieval_backend=retrieval_backend,
        )

    known_unknown_key = None
    if (
        preview.classification.access_tier is AccessTier.public
        and preview.classification.domain in {QueryDomain.institution, QueryDomain.calendar}
        and _looks_like_known_unknown_answer(message_text)
    ):
        known_unknown_key = detect_public_known_unknown_key(request_message)
    if known_unknown_key:
        return build_known_unknown_evidence_pack(
            requested_key=known_unknown_key,
            selected_tools=normalized_tools,
            school_name=_school_name_from_profile(school_profile),
        )

    public_supports = []
    if (
        preview.classification.access_tier is AccessTier.public
        and preview.classification.domain in {QueryDomain.institution, QueryDomain.calendar}
    ):
        public_supports = _build_runtime_public_supports(
            request_message=request_message,
            school_profile=school_profile,
            actor=actor,
            conversation_context=conversation_context,
            public_plan=public_plan,
            selected_tools=normalized_tools,
        )
    if public_supports:
        return build_direct_answer_evidence_pack(
            strategy='direct_answer',
            summary='Resposta grounded no perfil publico e nas politicas institucionais publicadas.',
            supports=public_supports,
        )

    if normalized_tools:
        return build_structured_tool_evidence_pack(
            selected_tools=normalized_tools,
            slice_name=preview.classification.domain.value,
        )

    fallback_supports: list[MessageEvidenceSupport] = []
    if preview.mode is OrchestrationMode.deny:
        fallback_supports.append(
            MessageEvidenceSupport(
                kind='guardrail',
                label='access_control',
                detail='A resposta foi bloqueada por regras de autenticacao ou acesso.',
            )
        )
    elif preview.mode is OrchestrationMode.clarify:
        fallback_supports.append(
            MessageEvidenceSupport(
                kind='clarify',
                label='needs_clarification',
                detail='O turno precisa de clarificacao antes de executar uma resposta grounded.',
            )
        )
    elif preview.mode is OrchestrationMode.graph_rag:
        fallback_supports.append(
            MessageEvidenceSupport(
                kind='tool',
                label='graph_rag',
                detail='Resposta sintetizada pela trilha GraphRAG.',
            )
        )
    else:
        fallback_supports.append(
            MessageEvidenceSupport(
                kind='deterministic',
                label='direct_answer',
                detail='Resposta emitida pelo caminho deterministico compartilhado.',
            )
        )
    return build_direct_answer_evidence_pack(
        strategy=preview.mode.value,
        summary='Resposta grounded pelo fluxo compartilhado de orquestracao.',
        supports=fallback_supports,
    )


def _build_runtime_risk_flags(
    *,
    request_message: str,
    message_text: str,
    preview: OrchestrationPreview,
) -> list[str]:
    risk_flags = list(getattr(preview, 'risk_flags', []) or [])
    if (
        preview.classification.access_tier is AccessTier.public
        and preview.classification.domain in {QueryDomain.institution, QueryDomain.calendar}
        and detect_public_known_unknown_key(request_message)
        and _looks_like_known_unknown_answer(message_text)
    ):
        risk_flags.append('valid_but_unpublished')
    return canonicalize_risk_flags(risk_flags)


def _should_run_response_critic(*, preview: Any, request: MessageResponseRequest) -> bool:
    if preview.needs_authentication:
        return False
    if preview.mode is OrchestrationMode.deny:
        return False
    if preview.classification.domain in {QueryDomain.academic, QueryDomain.finance}:
        return False
    if preview.mode in {
        OrchestrationMode.structured_tool,
        OrchestrationMode.hybrid_retrieval,
        OrchestrationMode.clarify,
    }:
        return request.channel.value in {'telegram', 'web'}
    return False


def _should_polish_structured_answer(*, preview: Any, request: MessageResponseRequest) -> bool:
    if preview.mode is not OrchestrationMode.structured_tool:
        return False
    if str(getattr(preview, 'reason', '') or '').startswith('langgraph_public_canonical_lane:'):
        return False
    if preview.needs_authentication:
        return False
    if request.channel.value not in {'telegram', 'web'}:
        return False
    if preview.classification.domain is QueryDomain.support:
        return False
    if (
        preview.classification.access_tier is AccessTier.public
        and preview.classification.domain in {QueryDomain.institution, QueryDomain.calendar}
    ):
        return True
    return False


def _preserve_capability_anchor_terms(
    *,
    original_text: str,
    polished_text: str | None,
    request_message: str,
) -> str | None:
    if not polished_text:
        return polished_text

    original_trimmed = original_text.strip()
    polished_trimmed = polished_text.strip()
    if original_trimmed:
        if len(original_trimmed) >= 80 and len(polished_trimmed) < max(
            48, int(len(original_trimmed) * 0.7)
        ):
            return original_text
        if original_trimmed[-1] in '.!?' and polished_trimmed and polished_trimmed[-1] not in '.!?':
            return original_text

    original_codes = {
        match.group(0).upper() for match in PROTOCOL_CODE_PATTERN.finditer(original_text)
    }
    polished_normalized = _normalize_text(polished_text)
    if original_codes:
        if not all(code.lower() in polished_text.lower() for code in original_codes):
            return original_text
        if (
            'ticket operacional' in _normalize_text(original_text)
            and 'ticket operacional' not in polished_normalized
        ):
            return original_text
        if 'fila' in _normalize_text(original_text) and 'fila' not in polished_normalized:
            return original_text

    normalized_message = _normalize_text(request_message)
    capability_like_query = any(
        _message_matches_term(normalized_message, term)
        for term in {
            'quais opcoes de assuntos',
            'opcoes de assuntos',
            'opções de assuntos',
            'o que voce faz',
            'como voce pode me ajudar',
        }
    ) or any(
        _message_matches_term(normalized_message, term)
        for term in {
            'oi',
            'ola',
            'olá',
            'bom dia',
            'boa tarde',
            'boa noite',
            'com quem eu falo',
            'pra quem eu falo',
            'para quem eu falo',
            'quem e voce',
            'quem é você',
            'voce e quem',
            'você é quem',
        }
    )
    if capability_like_query:
        for required_phrase in ('eduassist', 'colegio horizonte'):
            if (
                required_phrase in _normalize_text(original_text)
                and required_phrase not in polished_normalized
            ):
                return original_text
        original_terms = [
            term
            for term in ('matricula', 'financeiro', 'secretaria', 'visita', 'notas', 'faltas')
            if term in _normalize_text(original_text)
        ]
        if original_terms:
            preserved_count = sum(term in polished_normalized for term in original_terms)
            if preserved_count < min(3, len(original_terms)):
                return original_text

    if any(
        _message_matches_term(normalized_message, term)
        for term in PUBLIC_LEADERSHIP_TERMS | PUBLIC_CONTACT_TERMS | ASSISTANT_IDENTITY_TERMS
    ):
        email_pattern = re.compile(r'[\w.\-+]+@[\w.\-]+\.\w+')
        original_emails = {
            match.group(0).lower() for match in email_pattern.finditer(original_text)
        }
        if original_emails and not all(email in polished_text.lower() for email in original_emails):
            return original_text

        proper_name_pattern = re.compile(
            r'\b[A-ZÁÉÍÓÚÂÊÔÃÕÇ][A-Za-zÁÉÍÓÚÂÊÔÃÕÇáéíóúâêôãõç]+(?:\s+[A-ZÁÉÍÓÚÂÊÔÃÕÇ][A-Za-zÁÉÍÓÚÂÊÔÃÕÇáéíóúâêôãõç]+)+\b'
        )
        ignored_names = {
            'colegio horizonte',
            'eduassist',
            'canal institucional',
            'lideranca institucional',
            'diretora geral',
            'diretor geral',
        }
        original_names = {
            _normalize_text(match.group(0))
            for match in proper_name_pattern.finditer(original_text)
            if _normalize_text(match.group(0)) not in ignored_names
        }
        if original_names and not all(name in polished_normalized for name in original_names):
            return original_text
    return polished_text


def _extract_verification_anchors(text: str) -> set[str]:
    anchors: set[str] = set()
    normalized_text = _normalize_text(text)
    for pattern in (
        URL_PATTERN,
        EMAIL_PATTERN,
        PHONE_PATTERN,
        PROTOCOL_CODE_PATTERN,
        UUID_PATTERN,
        ENROLLMENT_CODE_PATTERN,
        CONTRACT_CODE_PATTERN,
        DATE_PATTERN,
        TEXTUAL_DATE_PATTERN,
        TIME_PATTERN,
    ):
        for match in pattern.finditer(text):
            anchors.add(_normalize_text(match.group(0)))
    if 'cep ' in normalized_text:
        cep_match = re.search(r'cep\s+\d{5}-\d{3}', normalized_text)
        if cep_match:
            anchors.add(cep_match.group(0))
    return anchors


def _extract_fallback_named_entities(text: str) -> set[str]:
    entities: set[str] = set()
    for match in PROPER_NAME_PATTERN.finditer(text):
        normalized = _normalize_text(match.group(0))
        if normalized in IGNORED_VERIFIER_NAMES:
            continue
        entities.add(normalized)
    return entities


def _unexpected_protected_entities(
    *,
    preview: Any,
    candidate_text: str,
    fallback_text: str,
) -> set[str]:
    if preview.classification.access_tier is AccessTier.public:
        return set()
    if preview.mode is not OrchestrationMode.structured_tool:
        return set()
    if preview.classification.domain not in {
        QueryDomain.institution,
        QueryDomain.academic,
        QueryDomain.finance,
    }:
        return set()

    fallback_entities = _extract_fallback_named_entities(fallback_text)
    if not fallback_entities:
        return set()
    candidate_entities = _extract_fallback_named_entities(candidate_text)
    if not candidate_entities:
        return set()
    return {
        entity
        for entity in candidate_entities - fallback_entities
        if entity not in IGNORED_VERIFIER_NAMES
    }


def _required_verifier_terms(
    *,
    preview: Any,
    public_plan: PublicInstitutionPlan | None,
    slot_memory: ConversationSlotMemory,
    request_message: str,
    fallback_text: str,
) -> set[str]:
    required_terms: set[str] = set()
    normalized_message = _normalize_text(request_message)
    fallback_normalized = _normalize_text(fallback_text)
    selected_tool_names = set(getattr(preview, 'selected_tools', []) or [])

    requested_attribute = (
        public_plan.requested_attribute
        if public_plan and public_plan.requested_attribute
        else slot_memory.public_attribute
    )
    requested_channel = (
        public_plan.requested_channel
        if public_plan and public_plan.requested_channel
        else slot_memory.requested_channel
    )

    if requested_attribute == 'age':
        required_terms.add('idade')
    elif requested_attribute == 'whatsapp':
        required_terms.add('whatsapp')
    elif requested_attribute == 'phone':
        required_terms.add('telefone')
    elif requested_attribute == 'email':
        required_terms.add('email')

    if requested_channel == 'telefone':
        required_terms.add('telefone')
    elif requested_channel == 'whatsapp':
        required_terms.add('whatsapp')
    elif requested_channel == 'email':
        required_terms.add('email')

    if slot_memory.academic_attribute == 'enrollment_code':
        required_terms.add('matricula')

    if slot_memory.finance_attribute == 'contract_code':
        required_terms.add('contrato')
    elif slot_memory.finance_attribute == 'invoice_id':
        required_terms.add('fatura')

    if slot_memory.finance_action == 'second_copy' or any(
        _message_matches_term(normalized_message, term) for term in FINANCE_SECOND_COPY_TERMS
    ):
        if 'segunda via' in fallback_normalized:
            required_terms.add('segunda via')

    if preview.classification.access_tier is not AccessTier.public and selected_tool_names & {
        'get_actor_identity_context',
        'get_student_academic_summary',
        'get_student_attendance',
        'get_student_grades',
        'get_student_upcoming_assessments',
        'get_student_attendance_timeline',
        'get_financial_summary',
        'get_student_administrative_status',
    }:
        required_terms.update(_extract_fallback_named_entities(fallback_text))

    if 'get_student_administrative_status' in selected_tool_names:
        required_terms.add('documentacao')
    elif 'get_actor_identity_context' in selected_tool_names:
        required_terms.add('perfil')

    if public_plan and public_plan.conversation_act == 'assistant_identity':
        required_terms.add('eduassist')
    if requested_attribute == 'name' or any(
        _message_matches_term(normalized_message, term)
        for term in {'qual o nome', 'nome da', 'nome do', 'como se chama'}
    ):
        required_terms.update(_extract_fallback_named_entities(fallback_text))

    return {term for term in required_terms if term}


def _extract_time_anchors(text: str) -> list[str]:
    return [_normalize_text(match.group(0)) for match in TIME_PATTERN.finditer(text)]


def _critical_verification_anchors(
    *,
    fallback_text: str,
    public_plan: PublicInstitutionPlan | None,
    slot_memory: ConversationSlotMemory,
) -> set[str]:
    anchors = _extract_verification_anchors(fallback_text)
    if not anchors:
        return anchors

    conversation_act = public_plan.conversation_act if public_plan is not None else None
    requested_attribute = (
        public_plan.requested_attribute
        if public_plan and public_plan.requested_attribute
        else slot_memory.public_attribute
    )

    if conversation_act == 'operating_hours':
        time_anchors = _extract_time_anchors(fallback_text)
        non_time_anchors = {anchor for anchor in anchors if anchor not in time_anchors}
        if requested_attribute == 'open_time' and time_anchors:
            return {*non_time_anchors, time_anchors[0]}
        if requested_attribute == 'close_time' and time_anchors:
            return {*non_time_anchors, time_anchors[-1]}
        if time_anchors:
            return {*non_time_anchors, time_anchors[0], time_anchors[-1]}
    return anchors


def _verify_answer_against_contract(
    *,
    request_message: str,
    preview: Any,
    candidate_text: str,
    deterministic_fallback_text: str | None,
    public_plan: PublicInstitutionPlan | None,
    slot_memory: ConversationSlotMemory,
) -> AnswerVerificationResult:
    if not deterministic_fallback_text:
        return AnswerVerificationResult(valid=True)

    candidate_normalized = _normalize_text(candidate_text)
    fallback_normalized = _normalize_text(deterministic_fallback_text)
    if candidate_normalized == fallback_normalized:
        return AnswerVerificationResult(valid=True)

    fallback_anchors = _critical_verification_anchors(
        fallback_text=deterministic_fallback_text,
        public_plan=public_plan,
        slot_memory=slot_memory,
    )
    missing_anchors = sorted(
        anchor for anchor in fallback_anchors if anchor not in candidate_normalized
    )
    if missing_anchors:
        return AnswerVerificationResult(valid=False, reason=f'missing_anchor:{missing_anchors[0]}')

    required_terms = _required_verifier_terms(
        preview=preview,
        public_plan=public_plan,
        slot_memory=slot_memory,
        request_message=request_message,
        fallback_text=deterministic_fallback_text,
    )
    missing_terms = sorted(term for term in required_terms if term not in candidate_normalized)
    if missing_terms:
        return AnswerVerificationResult(valid=False, reason=f'missing_term:{missing_terms[0]}')

    unexpected_entities = sorted(
        _unexpected_protected_entities(
            preview=preview,
            candidate_text=candidate_text,
            fallback_text=deterministic_fallback_text,
        )
    )
    if unexpected_entities:
        return AnswerVerificationResult(
            valid=False, reason=f'unexpected_entity:{unexpected_entities[0]}'
        )

    return AnswerVerificationResult(valid=True)


def _should_run_semantic_answer_judge(
    *,
    preview: Any,
    deterministic_fallback_text: str | None,
    candidate_text: str,
    public_plan: PublicInstitutionPlan | None,
) -> bool:
    if not deterministic_fallback_text:
        return False
    if _normalize_text(candidate_text) == _normalize_text(deterministic_fallback_text):
        return False
    if preview.classification.access_tier is AccessTier.public:
        if preview.classification.domain not in {QueryDomain.institution, QueryDomain.calendar}:
            return False
        if preview.mode not in {
            OrchestrationMode.structured_tool,
            OrchestrationMode.hybrid_retrieval,
            OrchestrationMode.clarify,
        }:
            return False
        if public_plan is not None and public_plan.conversation_act in {'greeting', 'capabilities'}:
            return False
        return True

    if preview.mode is not OrchestrationMode.structured_tool:
        return False
    return preview.classification.domain in {
        QueryDomain.institution,
        QueryDomain.academic,
        QueryDomain.finance,
    }


async def _verify_answer_against_contract_async(
    *,
    settings: Any,
    request_message: str,
    preview: Any,
    candidate_text: str,
    deterministic_fallback_text: str | None,
    public_plan: PublicInstitutionPlan | None,
    slot_memory: ConversationSlotMemory,
) -> tuple[AnswerVerificationResult, bool]:
    deterministic_result = _verify_answer_against_contract(
        request_message=request_message,
        preview=preview,
        candidate_text=candidate_text,
        deterministic_fallback_text=deterministic_fallback_text,
        public_plan=public_plan,
        slot_memory=slot_memory,
    )
    should_run_judge = _should_run_semantic_answer_judge(
        preview=preview,
        deterministic_fallback_text=deterministic_fallback_text,
        candidate_text=candidate_text,
        public_plan=public_plan,
    )
    if not deterministic_result.valid and (
        deterministic_result.reason is None
        or not deterministic_result.reason.startswith(('missing_anchor:', 'missing_term:'))
    ):
        return deterministic_result, False
    if not should_run_judge:
        return deterministic_result, False

    public_plan_payload = None
    if public_plan is not None:
        public_plan_payload = {
            'conversation_act': public_plan.conversation_act,
            'secondary_acts': list(public_plan.secondary_acts),
            'requested_attribute': public_plan.requested_attribute,
            'requested_channel': public_plan.requested_channel,
            'focus_hint': public_plan.focus_hint,
            'semantic_source': public_plan.semantic_source,
            'use_conversation_context': public_plan.use_conversation_context,
        }
    judge_payload = await judge_answer_relevance_with_provider(
        settings=settings,
        request_message=request_message,
        preview=preview,
        candidate_text=candidate_text,
        fallback_text=deterministic_fallback_text or '',
        public_plan=public_plan_payload,
        slot_memory=_serialize_slot_memory(slot_memory),
    )
    if not isinstance(judge_payload, dict):
        return deterministic_result, False
    judge_valid = judge_payload.get('valid')
    judge_reason = str(judge_payload.get('reason', '')).strip()
    if judge_valid is False:
        if deterministic_result.valid:
            return AnswerVerificationResult(
                valid=False, reason=f'semantic_judge:{judge_reason or "mismatch"}'
            ), True
        return deterministic_result, True
    if judge_valid is True and not deterministic_result.valid:
        return AnswerVerificationResult(valid=True), True
    return deterministic_result, True
