from __future__ import annotations

# ruff: noqa: F401,F403,F405

"""Large fast-path execution flow extracted from fast_path_answers.py."""

LOCAL_EXTRACTED_NAMES = {'build_fast_path_answer'}

from . import fast_path_answers as _native

def _refresh_native_namespace() -> None:
    for name, value in vars(_native).items():
        if name.startswith('__') or name in LOCAL_EXTRACTED_NAMES:
            continue
        globals()[name] = value

def build_fast_path_answer(ctx: Any, deps: FastPathDeps) -> SupervisorAnswerPayload | None:
    _refresh_native_namespace()
    profile = ctx.school_profile if isinstance(ctx.school_profile, dict) else {}
    normalized = deps.normalize_text(ctx.request.message)
    recent_user_messages = deps.normalized_recent_user_messages(ctx.conversation_context)
    contextual_message = _augment_public_followup_message(
        ctx.request.message,
        recent_user_messages,
        deps=deps,
    )
    contextual_normalized = deps.normalize_text(contextual_message)
    contextual_canonical_lane = match_public_canonical_lane(contextual_message) if contextual_message.strip() != str(ctx.request.message).strip() else None
    pricing_segment_hint = _public_pricing_segment_hint([normalized, *recent_user_messages])
    pricing_query_active = _looks_like_public_pricing_query(normalized) or _public_pricing_context_follow_up(
        normalized,
        recent_user_messages,
    )
    linked_finance_students = (
        deps.linked_students(ctx.actor, capability="finance")
        if bool(getattr(ctx.request.user, "authenticated", False))
        else []
    )
    recent_finance_context_active = any(
        any(
            marker in item
            for marker in {
                "meu financeiro",
                "financeiro",
                "fatura",
                "faturas",
                "boleto",
                "boletos",
                "mensalidade",
                "vencimento",
                "em aberto",
            }
        )
        for item in recent_user_messages
    )
    protected_finance_followup_active = bool(linked_finance_students) and (
        any(
            term in normalized
            for term in {
                "quero ver meu financeiro",
                "meu financeiro",
                "meus pagamentos",
                "financeiro da familia",
                "financeiro da família",
                "contas vinculadas",
                "fatura",
                "faturas",
                "boleto",
                "boletos",
                "em aberto",
                "proximo vencimento",
                "próximo vencimento",
                "proxima fatura",
                "próxima fatura",
                "vence primeiro",
                "mensalidade vencida",
                "mensalidades vencidas",
            }
        )
        or (
            recent_finance_context_active
            and any(
                term in normalized
                for term in {
                    "proximo vencimento",
                    "próximo vencimento",
                    "proxima fatura",
                    "próxima fatura",
                    "vence primeiro",
                    "em aberto",
                    "vencimento",
                    "vencida",
                    "vencidas",
                }
            )
        )
    )
    if profile and any(
        term in normalized
        for term in {
            "antes ou depois",
            "primeira reuniao",
            "primeira reunião",
            "so esse recorte",
            "só esse recorte",
            "nao quero o calendario inteiro",
            "não quero o calendário inteiro",
            "recorte em ordem",
        }
    ) and any(
        any(marker in item for marker in {"matricula", "aulas", "reuniao", "reunião", "responsaveis", "responsáveis", "marcos"})
        for item in recent_user_messages
    ):
        early_timeline_followup_answer = _compose_timeline_bundle_answer(
            profile,
            ctx.request.message,
            recent_user_messages=recent_user_messages,
        )
        if early_timeline_followup_answer:
            return _build_fast_path_payload(
                message_text=early_timeline_followup_answer,
                domain="institution",
                access_tier="public",
                confidence=0.99,
                reason="specialist_supervisor_fast_path:timeline_followup_repair",
                summary="Follow-up curto de timeline resolvido antes do roteamento mais pesado.",
                supports=[MessageEvidenceSupport(kind="timeline", label="Timeline publica", detail="recorte contextual do calendario escolar")],
                graph_leaf="timeline_followup_repair",
            )

    ingress_act = semantic_ingress_act(getattr(ctx, "preview_hint", None))

    if ingress_act == "greeting" or deps.is_simple_greeting(ctx.request.message):
        return _build_fast_path_payload(
            message_text=f"Olá! Eu sou o EduAssist do {deps.school_name(profile)}. Como posso ajudar você hoje?",
            domain="institution",
            access_tier=_access_tier_for_domain("institution", ctx.request.user.authenticated),
            confidence=0.99,
            reason="specialist_supervisor_fast_path:greeting",
            summary="Saudacao institucional curta e consistente.",
            supports=[MessageEvidenceSupport(kind="assistant_identity", label="EduAssist", detail=deps.school_name(profile))],
            graph_leaf="greeting",
        )

    if ingress_act == "input_clarification":
        return _build_fast_path_payload(
            message_text=(
                "Nao consegui interpretar essa mensagem com seguranca. "
                "Se quiser, reformule em uma frase curta dizendo o que voce precisa. "
                "Eu consigo seguir em portugues e normalmente tambem entendo ingles e espanhol."
            ),
            domain="institution",
            access_tier="public",
            confidence=0.99,
            reason="specialist_supervisor_fast_path:input_clarification",
            summary="Entrada curta pouco clara resolvida como pedido de reformulacao segura antes do roteamento protegido.",
            supports=[MessageEvidenceSupport(kind="assistant_identity", label="EduAssist", detail=deps.school_name(profile))],
            graph_leaf="input_clarification",
        )

    if ingress_act == "scope_boundary":
        school_name = deps.school_name(profile)
        return _build_fast_path_payload(
            message_text=(
                f"Nao tenho base confiavel aqui no EduAssist do {school_name} para responder esse tema fora do escopo da escola. "
                "Se quiser, eu posso ajudar com matricula, calendario, regras publicas, visitas, notas, frequencia ou financeiro."
            ),
            domain="institution",
            access_tier="public",
            confidence=0.99,
            reason="specialist_supervisor_fast_path:scope_boundary",
            summary="Pergunta fora do escopo escolar encerrada com boundary seguro antes da malha de specialists.",
            supports=[MessageEvidenceSupport(kind="assistant_identity", label="EduAssist", detail=school_name)],
            graph_leaf="scope_boundary",
        )

    if ingress_act == "language_preference":
        school_name = deps.school_name(profile)
        return _build_fast_path_payload(
            message_text=_compose_language_preference_fast_answer(
                school_name=school_name,
                message=ctx.request.message,
            ),
            domain="institution",
            access_tier="public",
            confidence=0.99,
            reason="specialist_supervisor_fast_path:language_preference",
            summary="Preferencia de idioma ou feedback metalinguistico resolvido antes do roteamento de dominio.",
            supports=[MessageEvidenceSupport(kind="assistant_identity", label="EduAssist", detail=school_name)],
            graph_leaf="language_preference",
        )

    if ingress_act == "capabilities" or _looks_like_capabilities_query(normalized):
        school_name = deps.school_name(profile)
        return _build_fast_path_payload(
            message_text=_compose_capabilities_fast_answer(profile, school_name=school_name),
            domain="institution",
            access_tier=_access_tier_for_domain("institution", ctx.request.user.authenticated),
            confidence=0.99,
            reason="specialist_supervisor_fast_path:capabilities",
            summary="Menu direto de capacidades publicas e protegidas do assistente.",
            supports=[MessageEvidenceSupport(kind="assistant_identity", label="EduAssist", detail=school_name)],
            graph_leaf="capabilities",
        )

    if ingress_act == "auth_guidance" or deps.is_auth_guidance_query(ctx.request.message):
        return _build_fast_path_payload(
            message_text=deps.compose_auth_guidance_answer(profile),
            domain="institution",
            access_tier="public",
            confidence=0.99,
            reason="specialist_supervisor_fast_path:auth_guidance",
            summary="Orientacao deterministica para vinculacao da conta no Telegram.",
            supports=[
                MessageEvidenceSupport(
                    kind="auth_guidance",
                    label="Vinculacao Telegram",
                    detail="Use `/start link_<codigo>` depois de gerar o codigo no portal autenticado.",
                )
            ],
            graph_leaf="auth_guidance",
            suggested_replies=[
                MessageResponseSuggestedReply(text="Quero vincular minha conta"),
                MessageResponseSuggestedReply(text="O que consigo consultar aqui?"),
                MessageResponseSuggestedReply(text="Como vejo minhas notas?"),
                MessageResponseSuggestedReply(text="Como acompanho pagamentos?"),
            ],
        )

    if (
        deps.linked_students(ctx.actor, capability="academic")
        or deps.linked_students(ctx.actor, capability="finance")
    ) and any(
        term in normalized
        for term in {"sobre cada um", "sobre cada aluno", "o que eu consigo ver sobre cada um"}
    ):
        scoped_lines: list[str] = ["Por aluno vinculado, hoje o seu escopo fica assim:"]
        for student in deps.linked_students(ctx.actor, capability="academic") or deps.linked_students(ctx.actor, capability="finance"):
            if not isinstance(student, dict):
                continue
            student_name = str(student.get("full_name") or "Aluno").strip() or "Aluno"
            student_scopes: list[str] = []
            if bool(student.get("can_view_academic", False)):
                student_scopes.append("academico")
            if bool(student.get("can_view_finance", False)):
                student_scopes.append("financeiro")
            if student_scopes:
                scoped_lines.append(f"- {student_name}: {', '.join(student_scopes)}")
        return _build_fast_path_payload(
            message_text="\n".join(scoped_lines),
            domain="institution",
            access_tier="authenticated",
            confidence=0.98,
            reason="specialist_supervisor_fast_path:access_scope_followup",
            summary="Follow-up autenticado sobre o escopo de cada aluno vinculado.",
            supports=[MessageEvidenceSupport(kind="account_scope", label="Conta vinculada", detail="academico e financeiro por aluno vinculado")],
            graph_leaf="access_scope_followup",
        )
    if (
        deps.linked_students(ctx.actor, capability="academic")
        or deps.linked_students(ctx.actor, capability="finance")
    ) and _looks_like_access_scope_query(ctx.request.message):
        return _build_fast_path_payload(
            message_text=deps.compose_authenticated_scope_answer(ctx.actor),
            domain="institution",
            access_tier="authenticated",
            confidence=0.99,
            reason="specialist_supervisor_fast_path:access_scope",
            summary="Escopo autenticado da conta com alunos vinculados.",
            supports=[MessageEvidenceSupport(kind="account_scope", label="Conta vinculada", detail="academico e financeiro conforme permissao")],
            graph_leaf="access_scope",
        )

    if profile and not protected_finance_followup_active:
        multi_intent_public_answer = _compose_public_multi_intent_fast_answer(
            profile=profile,
            message=contextual_message,
            normalized=contextual_normalized,
            pricing_query_active=pricing_query_active,
            pricing_segment_hint=pricing_segment_hint,
            deps=deps,
        )
        if multi_intent_public_answer:
            return _build_fast_path_payload(
                message_text=multi_intent_public_answer,
                domain="institution",
                access_tier="public",
                confidence=0.99,
                reason="specialist_supervisor_fast_path:public_multi_intent",
                summary="Resposta publica composta por decomposicao deterministica em mais de uma frente.",
                supports=[
                    MessageEvidenceSupport(
                        kind="public_bundle",
                        label="Pedido multiassunto",
                        detail="setores, canais e precificacao publica respondidos em conjunto",
                    )
                ],
                graph_leaf="public_multi_intent",
            )

    if _looks_like_service_routing_query(contextual_message) and profile and not protected_finance_followup_active:
        routing_answer = _compose_service_routing_fast_answer(profile, contextual_message)
        if routing_answer:
            return _build_fast_path_payload(
                message_text=routing_answer,
                domain="institution",
                access_tier="public",
                confidence=0.99,
                reason="specialist_supervisor_fast_path:service_routing",
                summary="Roteamento publico deterministico por setor institucional.",
                supports=[MessageEvidenceSupport(kind="service_routing", label="Setores", detail="admissoes, financeiro, orientacao educacional e direcao")],
                graph_leaf="service_routing",
            )

    teacher_directory_message = contextual_message if contextual_message.strip() else ctx.request.message
    if profile and _looks_like_public_teacher_identity_query(teacher_directory_message):
        teacher_directory_answer = _compose_public_teacher_directory_answer(profile, teacher_directory_message)
        if teacher_directory_answer:
            return _build_fast_path_payload(
                message_text=teacher_directory_answer,
                domain="institution",
                access_tier="public",
                confidence=0.99,
                reason="specialist_supervisor_fast_path:teacher_directory",
                summary="Politica publica de nao divulgacao de contatos individuais de professores.",
                supports=[
                    MessageEvidenceSupport(
                        kind="teacher_directory",
                        label="Diretorio docente publico",
                        detail=deps.safe_excerpt(teacher_directory_answer, limit=180),
                    )
                ],
                graph_leaf="teacher_directory",
            )

    if profile and _looks_like_service_credentials_bundle_query(ctx.request.message):
        return _build_fast_path_payload(
            message_text=_compose_service_credentials_bundle_answer(profile),
            domain="institution",
            access_tier="public",
            confidence=0.99,
            reason="specialist_supervisor_fast_path:service_credentials_bundle",
            summary="Resumo publico deterministico sobre secretaria, portal, credenciais e documentos.",
            supports=[
                MessageEvidenceSupport(
                    kind="service_overview",
                    label="Secretaria e portal",
                    detail="secretaria, portal institucional, credenciais e documentos",
                )
            ],
            graph_leaf="service_credentials_bundle",
        )

    if profile and _looks_like_policy_compare_query(ctx.request.message):
        compare_answer = _compose_policy_compare_answer(profile)
        if compare_answer:
            return _build_fast_path_payload(
                message_text=compare_answer,
                domain="institution",
                access_tier="public",
                confidence=0.99,
                reason="specialist_supervisor_fast_path:policy_compare",
                summary="Comparacao deterministica entre regulamentos gerais e politica de avaliacao.",
                supports=[
                    MessageEvidenceSupport(
                        kind="policy",
                        label="Frequencia, aprovacao e recuperacao",
                        detail="manual de regulamentos + academic_policy",
                    )
                ],
                graph_leaf="policy_compare",
            )

    if (
        profile
        and _looks_like_family_new_calendar_enrollment_query(contextual_message)
        and not _looks_like_first_month_risks_query(ctx.request.message)
        and not _looks_like_service_routing_query(contextual_message)
        and not any(term in contextual_normalized for term in {"contatos", "contato", "financeiro", "secretaria"})
    ):
        family_new_answer = compose_public_family_new_calendar_assessment_enrollment()
        if family_new_answer:
            return _build_fast_path_payload(
                message_text=family_new_answer,
                domain="institution",
                access_tier="public",
                confidence=0.99,
                reason="specialist_supervisor_fast_path:family_new_calendar_enrollment",
                summary="Sintese deterministica para familia nova cruzando calendario, agenda de avaliacoes e matricula.",
                supports=[
                    MessageEvidenceSupport(
                        kind="calendar_enrollment",
                        label="Calendario + agenda + matricula",
                        detail="calendario letivo, agenda de avaliacoes e manual de matricula",
                    )
                ],
                graph_leaf="family_new_calendar_enrollment",
            )

    if profile and any(
        term in normalized
        for term in {
            "antes ou depois",
            "primeira reuniao",
            "primeira reunião",
            "so esse recorte",
            "só esse recorte",
            "nao quero o calendario inteiro",
            "não quero o calendário inteiro",
            "recorte em ordem",
        }
    ) and any(
        any(marker in item for marker in {"matricula", "aulas", "reuniao", "reunião", "responsaveis", "responsáveis", "marcos"})
        for item in recent_user_messages
    ):
        timeline_followup_answer = _compose_timeline_bundle_answer(
            profile,
            ctx.request.message,
            recent_user_messages=recent_user_messages,
        )
        if timeline_followup_answer:
            return _build_fast_path_payload(
                message_text=timeline_followup_answer,
                domain="institution",
                access_tier="public",
                confidence=0.98,
                reason="specialist_supervisor_fast_path:timeline_followup_repair",
                summary="Follow-up curto resolvido com base na timeline publica recente.",
                supports=[MessageEvidenceSupport(kind="timeline", label="Timeline publica", detail="recorte contextual do calendario escolar")],
                graph_leaf="timeline_followup_repair",
            )

    if any(
        term in contextual_normalized
        for term in {
            "so o calendario publico",
            "quero so o calendario publico",
            "calendario publico da escola",
        }
    ):
        direct_timeline_answer = _compose_timeline_bundle_answer(
            profile,
            contextual_message,
            recent_user_messages=recent_user_messages,
        ) or compose_public_timeline_lifecycle_bundle()
        if direct_timeline_answer:
            return _build_fast_path_payload(
                message_text=direct_timeline_answer,
                domain="calendar",
                access_tier="public",
                confidence=0.99,
                reason="specialist_supervisor_fast_path:public_calendar_reset",
                summary="Retorno deterministico ao calendario publico apos uma digressao protegida.",
                supports=[MessageEvidenceSupport(kind="timeline", label="Calendario publico", detail=deps.safe_excerpt(direct_timeline_answer, limit=180))],
                graph_leaf="public_calendar_reset",
                suggested_domain="institution",
            )

    if ingress_act == "assistant_identity" or deps.is_assistant_identity_query(ctx.request.message):
        return _build_fast_path_payload(
            message_text=deps.compose_assistant_identity_answer(profile),
            domain="institution",
            access_tier=_access_tier_for_domain("institution", ctx.request.user.authenticated),
            confidence=0.99,
            reason="specialist_supervisor_fast_path:assistant_identity",
            summary="Identidade institucional do assistente com grounding no produto.",
            supports=[MessageEvidenceSupport(kind="assistant_identity", label="EduAssist", detail=deps.school_name(profile))],
            graph_leaf="assistant_identity",
        )

    if (
        "da escola que voce trabalha" in normalized
        or "da escola que você trabalha" in normalized
        or "da escola que voce atua" in normalized
    ):
        if any("materia" in item or "disciplina" in item or "ensino medio" in item or "ensino médio" in item for item in recent_user_messages):
            curriculum_answer = _compose_curriculum_components_answer(profile, segment_hint="Ensino Medio")
            if curriculum_answer:
                return _build_fast_path_payload(
                    message_text=curriculum_answer,
                    domain="institution",
                    access_tier=_access_tier_for_domain("institution", ctx.request.user.authenticated),
                    confidence=0.99,
                    reason="specialist_supervisor_fast_path:curriculum_followup",
                    summary="Follow-up resolvido com base curricular publica da escola.",
                    supports=[MessageEvidenceSupport(kind="curriculum", label="Ensino Medio", detail=deps.safe_excerpt(curriculum_answer, limit=180))],
                    graph_leaf="curriculum_followup",
                )
        return _build_fast_path_payload(
            message_text=deps.compose_assistant_identity_answer(profile),
            domain="institution",
            access_tier=_access_tier_for_domain("institution", ctx.request.user.authenticated),
            confidence=0.96,
            reason="specialist_supervisor_fast_path:assistant_identity_followup",
            summary="Follow-up benigno sobre identidade do assistente.",
            supports=[MessageEvidenceSupport(kind="assistant_identity", label="EduAssist", detail=deps.school_name(profile))],
            graph_leaf="assistant_identity_followup",
        )

    if not profile:
        return None

    if any(term in normalized for term in {"endereco completo", "telefone principal", "melhor canal"}) and "secretaria" in normalized:
        contact_bundle = _compose_contact_bundle_answer(profile, message=contextual_message)
        if contact_bundle:
            return _build_fast_path_payload(
                message_text=contact_bundle,
                domain="institution",
                access_tier="public",
                confidence=0.99,
                reason="specialist_supervisor_fast_path:contact_bundle",
                summary="Endereco, telefone principal e melhor canal da secretaria.",
                supports=[MessageEvidenceSupport(kind="contact", label="Secretaria", detail=deps.safe_excerpt(contact_bundle, limit=180))],
                graph_leaf="contact_bundle",
            )

    if (
        not _looks_like_cross_document_public_query(ctx.request.message)
        and any(term in normalized for term in {"30 segundos", "30s", "familia nova", "família nova", "por que deveria", "por que escolher"})
    ):
        pitch_answer = _compose_public_pitch_answer(profile)
        if pitch_answer:
            return _build_fast_path_payload(
                message_text=pitch_answer,
                domain="institution",
                access_tier="public",
                confidence=0.99,
                reason="specialist_supervisor_fast_path:public_pitch",
                summary="Pitch institucional curto grounded no perfil publico.",
                supports=[MessageEvidenceSupport(kind="highlight", label="Pitch institucional", detail=deps.safe_excerpt(pitch_answer, limit=180))],
                graph_leaf="public_pitch",
            )

    if not ctx.request.user.authenticated and _looks_like_bolsas_and_processes_query(ctx.request.message):
        answer_text = deps.compose_public_bolsas_and_processes(profile)
        if answer_text:
            return _build_fast_path_payload(
                message_text=answer_text,
                domain="institution",
                access_tier="public",
                confidence=0.99,
                reason="specialist_supervisor_fast_path:bolsas_and_processes",
                summary="Resposta documental deterministica sobre bolsas, rematricula, transferencia e cancelamento.",
                supports=[
                    MessageEvidenceSupport(kind="document", label="Edital de Bolsas e Descontos 2026", detail="data/corpus/public/edital-bolsas-e-descontos-2026.md"),
                    MessageEvidenceSupport(kind="document", label="Rematricula, Transferencia e Cancelamento 2026", detail="data/corpus/public/rematricula-transferencia-e-cancelamento-2026.md"),
                ],
                graph_leaf="bolsas_and_processes",
            )

    if not ctx.request.user.authenticated and _looks_like_health_second_call_query(ctx.request.message):
        answer_text = compose_public_health_second_call()
        if answer_text:
            return _build_fast_path_payload(
                message_text=answer_text,
                domain="academic",
                access_tier="public",
                confidence=0.99,
                reason="specialist_supervisor_fast_path:health_second_call",
                summary="Resposta documental deterministica para saude, atestado e segunda chamada.",
                supports=[
                    MessageEvidenceSupport(kind="document", label="Protocolo de Saude, Medicacao e Emergencias", detail="data/corpus/public/protocolo-saude-medicacao-e-emergencias.md"),
                    MessageEvidenceSupport(kind="document", label="Politica de Avaliacao, Recuperacao e Promocao", detail="data/corpus/public/politica-avaliacao-recuperacao-e-promocao.md"),
                ],
                graph_leaf="health_second_call",
                suggested_domain="academic",
            )

    if _looks_like_permanence_family_query(ctx.request.message):
        answer_text = compose_public_permanence_and_family_support(profile)
        if answer_text:
            return _build_fast_path_payload(
                message_text=answer_text,
                domain="institution",
                access_tier="public",
                confidence=0.99,
                reason="specialist_supervisor_fast_path:permanence_family_support",
                summary="Resposta documental deterministica sobre permanencia escolar e acompanhamento da familia.",
                supports=[
                    MessageEvidenceSupport(kind="document", label="Orientacao, Apoio e Vida Escolar", detail="data/corpus/public/orientacao-apoio-e-vida-escolar.md"),
                    MessageEvidenceSupport(kind="document", label="Politica de Avaliacao, Recuperacao e Promocao", detail="data/corpus/public/politica-avaliacao-recuperacao-e-promocao.md"),
                    MessageEvidenceSupport(kind="policy", label="Projeto de vida", detail="academic_policy.project_of_life_summary"),
                ],
                graph_leaf="permanence_family_support",
            )

    if _looks_like_health_authorization_bridge_query(ctx.request.message):
        answer_text = compose_public_health_authorizations_bridge()
        if answer_text:
            return _build_fast_path_payload(
                message_text=answer_text,
                domain="institution",
                access_tier="public",
                confidence=0.99,
                reason="specialist_supervisor_fast_path:health_authorizations_bridge",
                summary="Resposta documental deterministica cruzando saude, segunda chamada e autorizacoes.",
                supports=[
                    MessageEvidenceSupport(kind="document", label="Protocolo de Saude, Medicacao e Emergencias", detail="data/corpus/public/protocolo-saude-medicacao-e-emergencias.md"),
                    MessageEvidenceSupport(kind="document", label="Politica de Avaliacao, Recuperacao e Promocao", detail="data/corpus/public/politica-avaliacao-recuperacao-e-promocao.md"),
                    MessageEvidenceSupport(kind="document", label="Saidas Pedagogicas, Eventos e Autorizacoes", detail="data/corpus/public/saidas-pedagogicas-eventos-e-autorizacoes.md"),
                ],
                graph_leaf="health_authorizations_bridge",
            )

    if _looks_like_first_month_risks_query(ctx.request.message):
        answer_text = compose_public_first_month_risks(profile)
        if answer_text:
            return _build_fast_path_payload(
                message_text=answer_text,
                domain="institution",
                access_tier="public",
                confidence=0.99,
                reason="specialist_supervisor_fast_path:first_month_risks",
                summary="Resposta documental deterministica para riscos operacionais do primeiro mes.",
                supports=[
                    MessageEvidenceSupport(kind="document", label="Secretaria, Documentacao e Prazos", detail="data/corpus/public/secretaria-documentacao-e-prazos.md"),
                    MessageEvidenceSupport(kind="document", label="Politica de Uso do Portal, Aplicativo e Credenciais", detail="data/corpus/public/politica-uso-do-portal-aplicativo-e-credenciais.md"),
                    MessageEvidenceSupport(kind="document", label="Manual de Regulamentos Gerais", detail="data/corpus/public/manual-regulamentos-gerais.md"),
                ],
                graph_leaf="first_month_risks",
            )

    if _looks_like_process_compare_query(ctx.request.message):
        answer_text = compose_public_process_compare()
        if answer_text:
            return _build_fast_path_payload(
                message_text=answer_text,
                domain="institution",
                access_tier="public",
                confidence=0.99,
                reason="specialist_supervisor_fast_path:process_compare",
                summary="Resposta documental deterministica para rematricula, transferencia e cancelamento.",
                supports=[
                    MessageEvidenceSupport(kind="document", label="Rematricula, Transferencia e Cancelamento 2026", detail="data/corpus/public/rematricula-transferencia-e-cancelamento-2026.md"),
                ],
                graph_leaf="process_compare",
            )

    combined_timeline = _compose_timeline_bundle_answer(
        profile,
        contextual_message,
        recent_user_messages=recent_user_messages,
    )
    if combined_timeline:
        return _build_fast_path_payload(
            message_text=combined_timeline,
            domain="calendar",
            access_tier="public",
            confidence=0.99,
            reason="specialist_supervisor_fast_path:timeline_bundle",
            summary="Resumo deterministico de matricula e inicio das aulas.",
            supports=[MessageEvidenceSupport(kind="timeline", label="Linha do tempo publica", detail=deps.safe_excerpt(combined_timeline, limit=180))],
            graph_leaf="timeline_bundle",
            suggested_domain="institution",
        )

    if all(term in normalized for term in {"protocolo", "chamado", "handoff"}):
        return _build_fast_path_payload(
            message_text=_compose_support_process_boundary_answer(),
            domain="support",
            access_tier=_access_tier_for_domain("support", ctx.request.user.authenticated),
            confidence=0.98,
            reason="specialist_supervisor_fast_path:support_process_boundary",
            summary="Explicacao deterministica dos fluxos de protocolo, chamado e handoff humano.",
            supports=[MessageEvidenceSupport(kind="workflow", label="Fluxos operacionais", detail="protocolo, chamado e handoff humano")],
            graph_leaf="support_process_boundary",
        )

    if any(term in normalized for term in {"atendente humano", "atendimento humano", "falar com humano", "falar com um humano"}):
        return _build_fast_path_payload(
            message_text=_compose_human_handoff_answer(profile),
            domain="support",
            access_tier=_access_tier_for_domain("support", ctx.request.user.authenticated),
            confidence=0.99,
            reason="specialist_supervisor_fast_path:human_handoff_channels",
            summary="Canais humanos oficiais do colegio com grounding no perfil publico.",
            supports=[
                MessageEvidenceSupport(kind="contact", label="Secretaria", detail=str((_select_contact_channel(profile, label_contains=("secretaria",), channel_equals=("telefone",)) or {}).get("value") or "").strip() or None),
                MessageEvidenceSupport(kind="contact", label="Secretaria digital", detail=str((_select_contact_channel(profile, label_contains=("secretaria",), channel_equals=("whatsapp",)) or {}).get("value") or "").strip() or None),
            ],
            graph_leaf="human_handoff_channels",
            suggested_domain="support",
        )

    if (
        any(term in normalized for term in {"ligar para a escola", "ninguem me atende", "ninguém me atende", "problema para ligar"})
        or ("recepcao" in normalized and "falar" in normalized)
        or ("recepção" in normalized and "falar" in normalized)
    ):
        return _build_fast_path_payload(
            message_text=_compose_human_handoff_answer(profile),
            domain="support",
            access_tier=_access_tier_for_domain("support", ctx.request.user.authenticated),
            confidence=0.97,
            reason="specialist_supervisor_fast_path:contact_issue_channels",
            summary="Orientacao grounded para problema de contato com a escola.",
            supports=[MessageEvidenceSupport(kind="contact", label="Canais oficiais", detail="Telefone, WhatsApp e email da secretaria")],
            graph_leaf="contact_issue_channels",
            suggested_domain="support",
        )

    if ("horario" in normalized or "horário" in normalized) and any(term in normalized for term in {"escola atende", "a escola atende", "atende", "funciona"}):
        hours_answer = _compose_public_attendance_hours_answer(profile)
        if hours_answer:
            return _build_fast_path_payload(
                message_text=hours_answer,
                domain="institution",
                access_tier="public",
                confidence=0.98,
                reason="specialist_supervisor_fast_path:attendance_hours",
                summary="Horarios publicos grounded no perfil institucional.",
                supports=[MessageEvidenceSupport(kind="profile_fact", label="Horarios letivos", detail="shift_offers + biblioteca")],
                graph_leaf="attendance_hours",
            )

    if "matematica" in normalized or "matemática" in normalized:
        curriculum_answer = _compose_curriculum_components_answer(profile, segment_hint="Ensino Medio")
        if curriculum_answer and any(term in normalized for term in {"tem aula", "tem matéria", "tem materia", "tem "}):
            return _build_fast_path_payload(
                message_text="Sim. No Colegio Horizonte, Matematica faz parte da base curricular do Ensino Medio e tambem aparece articulada com monitorias e trilhas academicas no contraturno.",
                domain="institution",
                access_tier="public",
                confidence=0.98,
                reason="specialist_supervisor_fast_path:math_curriculum",
                summary="Confirmação grounded de componente curricular publico.",
                supports=[MessageEvidenceSupport(kind="curriculum", label="Matematica", detail="Componente listado no curriculo publico da escola.")],
                graph_leaf="math_curriculum",
            )

    if any(term in normalized for term in {"quais as materias", "quais as matérias", "quais materias", "quais disciplinas", "disciplinas"}) and any(
        term in normalized for term in {"ensino medio", "ensino médio"}
    ):
        curriculum_answer = _compose_curriculum_components_answer(profile, segment_hint="Ensino Medio")
        if curriculum_answer:
            return _build_fast_path_payload(
                message_text=curriculum_answer,
                domain="institution",
                access_tier="public",
                confidence=0.99,
                reason="specialist_supervisor_fast_path:curriculum_components",
                summary="Lista grounded dos componentes curriculares publicos.",
                supports=[MessageEvidenceSupport(kind="curriculum", label="Ensino Medio", detail="curriculum_components + curriculum_basis")],
                graph_leaf="curriculum_components",
            )

    if _looks_like_visit_reschedule_follow_up(normalized, recent_user_messages):
        visit_service = next(
            (
                item
                for item in (profile.get("service_catalog") or [])
                if isinstance(item, dict) and str(item.get("service_key") or "").strip() == "visita_institucional"
            ),
            None,
        )
        request_channel = str((visit_service or {}).get("request_channel") or "bot, admissions ou whatsapp comercial").strip()
        typical_eta = str((visit_service or {}).get("typical_eta") or "confirmacao em ate 1 dia util").strip()
        return _build_fast_path_payload(
            message_text=(
                "Se voce precisar remarcar a visita, me passe o protocolo do pedido ou o novo dia e horario desejados. "
                f"Hoje o canal institucional para isso e {request_channel}, com {typical_eta}."
            ),
            domain="support",
            access_tier=_access_tier_for_domain("support", ctx.request.user.authenticated),
            confidence=0.98,
            reason="specialist_supervisor_fast_path:visit_reschedule",
            summary="Orientacao direta de remarcacao de visita com protocolo e canal oficial.",
            supports=[MessageEvidenceSupport(kind="workflow_intent", label="Remarcacao de visita", detail="protocolo + novo horario desejado")],
            graph_leaf="visit_reschedule",
            suggested_domain="support",
        )

    if _looks_like_visit_resume_follow_up(normalized, recent_user_messages):
        visit_service = next(
            (
                item
                for item in (profile.get("service_catalog") or [])
                if isinstance(item, dict) and str(item.get("service_key") or "").strip() == "visita_institucional"
            ),
            None,
        )
        request_channel = str((visit_service or {}).get("request_channel") or "bot, admissions ou whatsapp comercial").strip()
        return _build_fast_path_payload(
            message_text=(
                "Se voce quiser retomar a visita depois, volte por este mesmo canal institucional "
                f"ou por {request_channel}. Se preferir, ja me diga o novo dia e horario desejados "
                "que eu abro outro pedido de visita."
            ),
            domain="support",
            access_tier=_access_tier_for_domain("support", ctx.request.user.authenticated),
            confidence=0.98,
            reason="specialist_supervisor_fast_path:visit_resume",
            summary="Orientacao direta para retomar um fluxo de visita apos pausa ou cancelamento.",
            supports=[MessageEvidenceSupport(kind="workflow_intent", label="Retomada de visita", detail="mesmo canal institucional ou novo pedido com dia e horario")],
            graph_leaf="visit_resume",
            suggested_domain="support",
        )

    if "visita" in normalized and any(term in normalized for term in {"agendar", "marcar"}):
        weekday = next((item for item in ("segunda", "terca", "quarta", "quinta", "sexta", "sabado") if item in normalized), None)
        has_explicit_date = bool(re.search(r"\b\d{1,2}/\d{1,2}(?:/\d{2,4})?\b", normalized))
        if weekday and not has_explicit_date:
            period = "de tarde" if "tarde" in normalized else "de manha" if "manha" in normalized else ""
            friendly_weekday = weekday + ("-feira" if weekday != "sabado" else "")
            return _build_fast_path_payload(
                message_text=(
                    f"Perfeito. Para qual {friendly_weekday} voce quer a visita{f' {period}' if period else ''}? "
                    "Assim que voce confirmar a data, eu sigo com o pedido e te devolvo o protocolo."
                ),
                domain="support",
                access_tier=_access_tier_for_domain("support", ctx.request.user.authenticated),
                confidence=0.98,
                reason="specialist_supervisor_fast_path:workflow_date_clarify",
                summary="Clarificacao de data antes de abrir o agendamento.",
                supports=[
                    MessageEvidenceSupport(
                        kind="workflow_intent",
                        label="Agendamento de visita",
                        detail=f"Dia da semana detectado: {friendly_weekday}",
                    )
                ],
                graph_leaf="workflow_date_clarify",
                suggested_replies=[
                    MessageResponseSuggestedReply(text="Nesta quinta"),
                    MessageResponseSuggestedReply(text="Na proxima quinta"),
                    MessageResponseSuggestedReply(text="Quinta, 03/04"),
                    MessageResponseSuggestedReply(text="Pode ser outro dia"),
                ],
                mode="clarify",
            )

    if "biblioteca" in normalized and any(
        term in normalized
        for term in {
            "tem biblioteca",
            "ha biblioteca",
            "há biblioteca",
            "possui biblioteca",
            "existe biblioteca",
            "biblioteca nessa escola",
        }
    ):
        label = _feature_label(profile, name_hint="biblioteca") or "Biblioteca Aurora"
        note = _feature_note(profile, name_hint="biblioteca") or "Atendimento ao publico de segunda a sexta, das 7h30 as 18h00."
        return _build_fast_path_payload(
            message_text=f"Sim. O colegio tem a {label}. {note}",
            domain="institution",
            access_tier="public",
            confidence=0.99,
            reason="specialist_supervisor_fast_path:library_exists",
            summary="Resposta direta grounded sobre a existencia da biblioteca institucional.",
            supports=[MessageEvidenceSupport(kind="profile_fact", label=label, detail=note)],
            graph_leaf="library_exists",
        )

    if "biblioteca" in normalized and any(
        term in normalized
        for term in {
            "horario",
            "horário",
            "funciona",
            "abre",
            "fecha",
            "fecha a biblioteca",
            "que horas fecha",
            "ate que horas",
            "até que horas",
            "nome",
            "marketing",
        }
    ):
        label = _feature_label(profile, name_hint="biblioteca") or "Biblioteca Aurora"
        note = _feature_note(profile, name_hint="biblioteca") or "Atendimento ao publico de segunda a sexta, das 7h30 as 18h00."
        return _build_fast_path_payload(
            message_text=f"A biblioteca se chama {label} e funciona {note}",
            domain="institution",
            access_tier="public",
            confidence=0.99,
            reason="specialist_supervisor_fast_path:library_hours",
            summary="Resposta direta grounded no perfil institucional publico.",
            supports=[MessageEvidenceSupport(kind="profile_fact", label=label, detail=note)],
            graph_leaf="library_hours",
        )

    if any(term in normalized for term in {"proposta pedagogica", "projeto pedagogico", "pedagogica da escola", "pedagogico da escola"}):
        pedagogical_answer = _compose_public_pedagogical_answer(profile)
        if pedagogical_answer:
            return _build_fast_path_payload(
                message_text=pedagogical_answer,
                domain="institution",
                access_tier="public",
                confidence=0.99,
                reason="specialist_supervisor_fast_path:pedagogical_proposal",
                summary="Resposta pedagogica grounded no perfil institucional publico.",
                supports=[
                    MessageEvidenceSupport(kind="profile_fact", label="Modelo educacional", detail=deps.safe_excerpt(str(profile.get("education_model", "") or ""), limit=220)),
                    MessageEvidenceSupport(kind="profile_fact", label="Base curricular", detail=deps.safe_excerpt(str(profile.get("curriculum_basis", "") or ""), limit=220)),
                    MessageEvidenceSupport(kind="profile_fact", label="Headline institucional", detail=deps.safe_excerpt(str(profile.get("short_headline", "") or ""), limit=180)),
                ],
                graph_leaf="pedagogical_proposal",
            )

    if "bncc" in normalized:
        basis = str(profile.get("curriculum_basis", "") or "").strip()
        if basis:
            return _build_fast_path_payload(
                message_text=f"Sim. A escola trabalha com base curricular alinhada a {basis}.",
                domain="institution",
                access_tier="public",
                confidence=0.98,
                reason="specialist_supervisor_fast_path:bncc",
                summary="Resposta direta grounded no perfil institucional publico.",
                supports=[MessageEvidenceSupport(kind="profile_fact", label="Curriculo", detail=deps.safe_excerpt(basis, limit=180))],
                graph_leaf="curriculum",
            )

    if any(term in normalized for term in {"bairro", "regiao"}) and any(term in normalized for term in {"escola", "fica", "endereco"}):
        district = str(profile.get("district", "") or "").strip()
        city = str(profile.get("city", "") or "").strip()
        state = str(profile.get("state", "") or "").strip()
        if district:
            locality = ", ".join(part for part in [district, city, state] if part)
            return _build_fast_path_payload(
                message_text=f"A escola fica no bairro {district}{f', {city}/{state}' if city and state else ''}.",
                domain="institution",
                access_tier="public",
                confidence=0.98,
                reason="specialist_supervisor_fast_path:district",
                summary="Resposta direta grounded no perfil institucional publico.",
                supports=[MessageEvidenceSupport(kind="profile_fact", label="Localizacao", detail=locality)],
                graph_leaf="district",
            )

    if any(term in normalized for term in {"site oficial", "website", "link do site", "site da escola"}) or (
        "site" in normalized and any(term in normalized for term in {"escola", "colegio", "colégio"})
    ):
        website_url = str(profile.get("website_url", "") or "").strip()
        if website_url:
            return _build_fast_path_payload(
                message_text=f"O site oficial do {deps.school_name(profile)} hoje e {website_url}.",
                domain="institution",
                access_tier="public",
                confidence=0.98,
                reason="specialist_supervisor_fast_path:website",
                summary="Resposta direta grounded no site institucional publico.",
                supports=[MessageEvidenceSupport(kind="profile_fact", label="Website", detail=website_url)],
                graph_leaf="website",
            )

    if (
        not _looks_like_service_routing_query(contextual_message)
        and any(term in normalized for term in {"diretora", "diretor", "direcao", "direção", "diretoria"})
        and (
            any(term in normalized for term in {"quem", "nome", "comando", "manda", "lidera"})
            or _looks_like_public_leadership_contact_query(contextual_message)
        )
    ):
        leadership_team = profile.get("leadership_team")
        if isinstance(leadership_team, list):
            for member in leadership_team:
                if not isinstance(member, dict):
                    continue
                title = str(member.get("title", "") or "").strip()
                if "diretor" not in deps.normalize_text(title) and "direcao" not in deps.normalize_text(title):
                    continue
                name = str(member.get("name", "") or "").strip()
                contact_channel = str(member.get("contact_channel", "") or "").strip()
                if name:
                    message_text = f"{title}: {name}."
                    if contact_channel:
                        message_text += f" Canal institucional: {contact_channel}."
                    return _build_fast_path_payload(
                        message_text=message_text,
                        domain="institution",
                        access_tier="public",
                        confidence=0.98,
                        reason="specialist_supervisor_fast_path:leadership_name",
                        summary="Resposta direta grounded na lideranca institucional publica.",
                        supports=[MessageEvidenceSupport(kind="profile_fact", label=title or "Direcao", detail=name)],
                        graph_leaf="leadership_name",
                    )

    admissions_entry = _timeline_entry(profile.get("public_timeline") or [], topic_fragment="admissions_opening")
    if (
        any(term in normalized for term in {"matricula de 2026", "matrícula de 2026", "abertura da matricula", "abertura da matrícula"})
        or (
            any(term in normalized for term in {"matricula", "matrícula"})
            and any(term in normalized for term in {"quando abre", "quando comeca", "quando começa", "abre"})
        )
    ) and isinstance(admissions_entry, dict):
        entry_date = _timeline_entry_date_label(admissions_entry)
        summary = str(admissions_entry.get("summary", "") or "").strip()
        if entry_date and summary:
            return _build_fast_path_payload(
                message_text=f"No calendario publico atual, a matricula de 2026 abre em {entry_date}. {summary}",
                domain="institution",
                access_tier="public",
                confidence=0.99,
                reason="specialist_supervisor_fast_path:admissions_opening",
                summary="Resposta direta grounded na timeline publica de matricula.",
                supports=[MessageEvidenceSupport(kind="timeline", label="Abertura da matricula", detail=entry_date)],
                graph_leaf="admissions_opening",
            )

    school_year_entry = _timeline_entry(profile.get("public_timeline") or [], topic_fragment="school_year_start")
    if any(
        term in normalized
        for term in {
            "quando comecam as aulas",
            "quando começam as aulas",
            "quando iniciam as aulas",
            "inicio das aulas",
            "início das aulas",
            "inicio do ano letivo",
            "início do ano letivo",
        }
    ) and isinstance(school_year_entry, dict):
        entry_date = _timeline_entry_date_label(school_year_entry)
        summary = str(school_year_entry.get("summary", "") or "").strip()
        if entry_date and summary:
            return _build_fast_path_payload(
                message_text=f"No calendario publico atual, as aulas comecam em {entry_date}. {summary}",
                domain="calendar",
                access_tier="public",
                confidence=0.99,
                reason="specialist_supervisor_fast_path:school_year_start",
                summary="Resposta direta grounded no inicio do ano letivo.",
                supports=[MessageEvidenceSupport(kind="timeline", label="Inicio das aulas", detail=entry_date)],
                graph_leaf="school_year_start",
            )

    family_meeting_entry = _timeline_entry(profile.get("public_timeline") or [], topic_fragment="family_meeting")
    if any(
        term in normalized
        for term in {"reuniao de pais", "reunião de pais", "reuniao de responsaveis", "reunião de responsáveis"}
    ) and isinstance(family_meeting_entry, dict):
        entry_date = _timeline_entry_date_label(family_meeting_entry)
        summary = str(family_meeting_entry.get("summary", "") or "").strip()
        if entry_date and summary:
            return _build_fast_path_payload(
                message_text=f"No calendario publico atual, a reuniao de pais acontece em {entry_date}. {summary}",
                domain="calendar",
                access_tier="public",
                confidence=0.99,
                reason="specialist_supervisor_fast_path:family_meeting",
                summary="Resposta direta grounded no calendario publico de reunioes.",
                supports=[MessageEvidenceSupport(kind="timeline", label="Reuniao de pais", detail=entry_date)],
                graph_leaf="family_meeting",
            )

    quantity = deps.hypothetical_children_quantity(ctx.request.message)
    if quantity is not None and (
        any(term in normalized for term in {"matricula", "mensalidade", "pagar", "pagaria"})
        or pricing_query_active
    ):
        projection = deps.pricing_projection(profile, quantity=quantity, segment_hint=pricing_segment_hint)
        total_enrollment = Decimal(str(projection.get("total_enrollment_fee", "0") or "0")).quantize(Decimal("0.01"))
        total_monthly = Decimal(str(projection.get("total_monthly_amount", "0") or "0")).quantize(Decimal("0.01"))
        segment = str(projection.get("segment", "") or "segmento publico de referencia").strip()
        return _build_fast_path_payload(
            message_text=(
                f"Usando a referencia publica atual para {segment}, {quantity} aluno(s) dariam "
                f"R$ {total_enrollment:,.2f} de matricula e R$ {total_monthly:,.2f} de mensalidade por mes."
            ).replace(",", "X").replace(".", ",").replace("X", "."),
            domain="finance",
            access_tier="public",
            confidence=0.99,
            reason="specialist_supervisor_fast_path:pricing_projection",
            summary="Projecao publica deterministica baseada na tabela de referencia institucional.",
            supports=[
                MessageEvidenceSupport(
                    kind="pricing_reference",
                    label=segment or "Tabela publica",
                    detail=f"matricula por aluno: R$ {Decimal(str(projection.get('per_student_enrollment_fee', '0') or '0')).quantize(Decimal('0.01'))}",
                ),
                MessageEvidenceSupport(kind="pricing_reference", label="Quantidade simulada", detail=str(quantity)),
            ],
            graph_leaf="pricing_projection",
            suggested_domain="finance",
        )

    if profile and pricing_query_active and pricing_segment_hint:
        rows = profile.get("tuition_reference")
        if isinstance(rows, list):
            chosen = next(
                (
                    row
                    for row in rows
                    if isinstance(row, dict)
                    and deps.normalize_text(pricing_segment_hint) in deps.normalize_text(row.get("segment"))
                ),
                None,
            )
            if isinstance(chosen, dict):
                monthly = deps.format_brl(chosen.get("monthly_amount"))
                enrollment = deps.format_brl(chosen.get("enrollment_fee"))
                notes = str(chosen.get("notes") or "").strip()
                return _build_fast_path_payload(
                    message_text=(
                        f"Para {pricing_segment_hint} no turno {chosen.get('shift_label', 'Manha')}, "
                        f"a mensalidade publica de referencia em 2026 e {monthly} "
                        f"e a taxa de matricula e {enrollment}. {notes}"
                    ).strip(),
                    domain="finance",
                    access_tier="public",
                    confidence=0.99,
                    reason="specialist_supervisor_fast_path:public_pricing_reference",
                    summary="Resposta publica deterministica baseada na tabela de valores.",
                    supports=[
                        MessageEvidenceSupport(
                            kind="pricing_reference",
                            label=str(chosen.get("segment") or "Tabela publica"),
                            detail=f"mensalidade {monthly} · matricula {enrollment}",
                        ),
                    ],
                    graph_leaf="public_pricing_reference",
                    suggested_domain="finance",
                )

    if profile and pricing_query_active:
        rows = profile.get("tuition_reference")
        if isinstance(rows, list) and rows:
            lines = ["Valores publicos de referencia:"]
            for row in rows[:3]:
                if not isinstance(row, dict):
                    continue
                lines.append(
                    "- {segment} ({shift_label}): mensalidade {monthly_amount} e taxa de matricula {enrollment_fee}. {notes}".format(
                        segment=str(row.get("segment") or "segmento").strip(),
                        shift_label=str(row.get("shift_label") or "Manha").strip(),
                        monthly_amount=deps.format_brl(row.get("monthly_amount")),
                        enrollment_fee=deps.format_brl(row.get("enrollment_fee")),
                        notes=str(row.get("notes") or "").strip(),
                    ).strip()
                )
            lines.append("Se quiser, eu tambem posso simular a matricula para 2 ou 3 alunos.")
            return _build_fast_path_payload(
                message_text="\n".join(lines),
                domain="finance",
                access_tier="public",
                confidence=0.99,
                reason="specialist_supervisor_fast_path:public_pricing_overview",
                summary="Resumo publico deterministico da tabela de referencia institucional.",
                supports=[
                    MessageEvidenceSupport(
                        kind="pricing_reference",
                        label="Tabela publica de valores",
                        detail="mensalidade e taxa de matricula por segmento",
                    )
                ],
                graph_leaf="public_pricing_overview",
                suggested_domain="finance",
            )

    if contextual_canonical_lane:
        contextual_public_answer = compose_public_canonical_lane_answer(contextual_canonical_lane, profile=profile)
        if contextual_public_answer:
            contextual_normalized = deps.normalize_text(contextual_message)
            if (
                contextual_canonical_lane == "public_bundle.outings_authorizations"
                and any(
                    term in contextual_normalized
                    for term in {
                        "dois passos praticos",
                        "dois passos práticos",
                        "resuma em dois passos",
                        "resume isso em dois passos",
                    }
                )
            ):
                contextual_public_answer = (
                    "Primeiro, confirme pelo canal oficial a atividade, a data e as regras publicas da saida pedagogica. "
                    "Depois, envie a autorizacao da familia no prazo e acompanhe as orientacoes de uniforme, saida e retorno."
                )
            if "apenas o que e publico nesse tema" in normalized or "apenas o que é publico nesse tema" in normalized:
                contextual_public_answer = (
                    "Restrito: eu continuo sem acesso ao protocolo interno desse tema. "
                    f"Publico: {contextual_public_answer}"
                )
            return _build_fast_path_payload(
                message_text=contextual_public_answer,
                domain="institution",
                access_tier="public",
                confidence=0.99,
                reason="specialist_supervisor_fast_path:contextual_public_lane",
                summary="Follow-up publico resolvido por canonical lane contextual sem depender do loop premium.",
                supports=[MessageEvidenceSupport(kind="public_bundle", label="Canonical lane contextual", detail=contextual_canonical_lane)],
                graph_leaf="contextual_public_lane",
            )
    contextual_known_unknown_key = (
        detect_public_known_unknown_key(contextual_message)
        if contextual_message.strip() != str(ctx.request.message).strip()
        else None
    )
    if contextual_known_unknown_key:
        known_unknown_answer = compose_public_known_unknown_answer(
            key=contextual_known_unknown_key,
            school_name=deps.school_name(profile),
        )
        if known_unknown_answer:
            return _build_fast_path_payload(
                message_text=known_unknown_answer,
                domain="institution",
                access_tier="public",
                confidence=0.99,
                reason="specialist_supervisor_fast_path:contextual_known_unknown",
                summary="Follow-up publico resolvido como dado valido, mas nao publicado oficialmente.",
                supports=[MessageEvidenceSupport(kind="known_unknown", label=contextual_known_unknown_key, detail="dado publico nao publicado")],
                graph_leaf="contextual_known_unknown",
            )

    return None
