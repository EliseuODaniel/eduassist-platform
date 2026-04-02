from __future__ import annotations

import re
from dataclasses import dataclass
from decimal import Decimal
from typing import Any, Callable

from .answer_payloads import (
    access_tier_for_domain as _access_tier_for_domain,
)
from .answer_payloads import (
    default_suggested_replies as _default_suggested_replies,
)
from .models import (
    MessageEvidencePack,
    MessageEvidenceSupport,
    MessageIntentClassification,
    MessageResponseSuggestedReply,
    SupervisorAnswerPayload,
)
from .public_profile_answers import (
    _compose_contact_bundle_answer,
    _compose_curriculum_components_answer,
    _compose_human_handoff_answer,
    _compose_policy_compare_answer,
    _compose_public_attendance_hours_answer,
    _compose_public_pedagogical_answer,
    _compose_public_pitch_answer,
    _compose_public_teacher_directory_answer,
    _compose_service_credentials_bundle_answer,
    _compose_service_routing_fast_answer,
    _compose_support_process_boundary_answer,
    _compose_timeline_bundle_answer,
    _feature_label,
    _feature_note,
    _select_contact_channel,
)
from .public_bundle_fast_paths import (
    _looks_like_family_new_calendar_enrollment_query,
    _looks_like_first_month_risks_query,
    _looks_like_health_authorization_bridge_query,
    _looks_like_permanence_family_query,
    _looks_like_process_compare_query,
)
from .public_doc_knowledge import (
    compose_public_family_new_calendar_assessment_enrollment,
    compose_public_first_month_risks,
    compose_public_health_authorizations_bridge,
    compose_public_health_second_call,
    compose_public_permanence_and_family_support,
    compose_public_process_compare,
)
from .public_query_patterns import (
    _looks_like_access_scope_query,
    _looks_like_bolsas_and_processes_query,
    _looks_like_cross_document_public_query,
    _looks_like_health_second_call_query,
    _looks_like_policy_compare_query,
    _looks_like_public_teacher_identity_query,
    _looks_like_service_credentials_bundle_query,
    _looks_like_service_routing_query,
)


@dataclass(frozen=True)
class FastPathDeps:
    normalize_text: Callable[[str | None], str]
    normalized_recent_user_messages: Callable[[dict[str, Any] | None], list[str]]
    is_simple_greeting: Callable[[str], bool]
    is_auth_guidance_query: Callable[[str], bool]
    compose_auth_guidance_answer: Callable[[dict[str, Any] | None], str]
    linked_students: Callable[..., list[dict[str, Any]]]
    compose_authenticated_scope_answer: Callable[[dict[str, Any] | None], str]
    is_assistant_identity_query: Callable[[str], bool]
    compose_assistant_identity_answer: Callable[[dict[str, Any] | None], str]
    school_name: Callable[[dict[str, Any] | None], str]
    safe_excerpt: Callable[..., str]
    hypothetical_children_quantity: Callable[[str], int | None]
    pricing_projection: Callable[..., dict[str, Any]]
    compose_public_bolsas_and_processes: Callable[[dict[str, Any] | None], str | None]


def _build_fast_path_payload(
    *,
    message_text: str,
    domain: str,
    access_tier: str,
    confidence: float,
    reason: str,
    summary: str,
    supports: list[MessageEvidenceSupport],
    graph_leaf: str,
    suggested_domain: str | None = None,
    suggested_replies: list[MessageResponseSuggestedReply] | None = None,
    mode: str = "structured_tool",
) -> SupervisorAnswerPayload:
    return SupervisorAnswerPayload(
        message_text=message_text,
        mode=mode,
        classification=MessageIntentClassification(
            domain=domain,
            access_tier=access_tier,
            confidence=confidence,
            reason=reason,
        ),
        evidence_pack=MessageEvidencePack(
            strategy="direct_answer",
            summary=summary,
            source_count=max(len(supports), 1),
            support_count=len(supports),
            supports=supports,
        ),
        suggested_replies=suggested_replies or _default_suggested_replies(suggested_domain or domain),
        graph_path=["specialist_supervisor", "fast_path", graph_leaf],
        reason=reason,
    )


def build_fast_path_answer(ctx: Any, deps: FastPathDeps) -> SupervisorAnswerPayload | None:
    profile = ctx.school_profile if isinstance(ctx.school_profile, dict) else {}
    normalized = deps.normalize_text(ctx.request.message)
    recent_user_messages = deps.normalized_recent_user_messages(ctx.conversation_context)

    if deps.is_simple_greeting(ctx.request.message):
        return _build_fast_path_payload(
            message_text="Olá! Eu sou o EduAssist. Como posso ajudar você hoje?",
            domain="institution",
            access_tier=_access_tier_for_domain("institution", ctx.request.user.authenticated),
            confidence=0.99,
            reason="specialist_supervisor_fast_path:greeting",
            summary="Saudacao institucional curta e consistente.",
            supports=[MessageEvidenceSupport(kind="assistant_identity", label="EduAssist", detail=deps.school_name(profile))],
            graph_leaf="greeting",
        )

    if deps.is_auth_guidance_query(ctx.request.message):
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

    if _looks_like_service_routing_query(ctx.request.message) and profile:
        routing_answer = _compose_service_routing_fast_answer(profile, ctx.request.message)
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

    if profile and _looks_like_public_teacher_identity_query(ctx.request.message):
        teacher_directory_answer = _compose_public_teacher_directory_answer(profile, ctx.request.message)
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

    if profile and _looks_like_family_new_calendar_enrollment_query(ctx.request.message):
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

    if deps.is_assistant_identity_query(ctx.request.message):
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
        contact_bundle = _compose_contact_bundle_answer(profile)
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

    combined_timeline = _compose_timeline_bundle_answer(profile, ctx.request.message)
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

    if "visita" in normalized and any(term in normalized for term in {"agendar", "marcar"}):
        weekday = next((item for item in ("segunda", "terca", "quarta", "quinta", "sexta", "sabado") if item in normalized), None)
        has_explicit_date = bool(re.search(r"\b\d{1,2}/\d{1,2}(?:/\d{2,4})?\b", normalized))
        if weekday and not has_explicit_date:
            period = "de tarde" if "tarde" in normalized else "de manha" if "manha" in normalized else ""
            friendly_weekday = weekday + ("-feira" if weekday != "sabado" else "")
            return _build_fast_path_payload(
                message_text=f"Perfeito. Para qual {friendly_weekday} voce quer a visita{f' {period}' if period else ''}?",
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

    if "biblioteca" in normalized and any(term in normalized for term in {"horario", "funciona", "abre", "nome", "marketing"}):
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

    quantity = deps.hypothetical_children_quantity(ctx.request.message)
    if quantity is not None and any(term in normalized for term in {"matricula", "mensalidade", "pagar", "pagaria"}):
        projection = deps.pricing_projection(profile, quantity=quantity)
        total_enrollment = Decimal(str(projection.get("total_enrollment_fee", "0") or "0")).quantize(Decimal("0.01"))
        total_monthly = Decimal(str(projection.get("total_monthly_amount", "0") or "0")).quantize(Decimal("0.01"))
        segment = str(projection.get("segment", "") or "segmento publico de referencia").strip()
        return _build_fast_path_payload(
            message_text=(
                f"Usando a referencia publica atual para {segment}, {quantity} aluno(s) dariam "
                f"R$ {total_enrollment:,.2f} de matricula e R$ {total_monthly:,.2f} por mes."
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

    return None
