from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date
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
    _timeline_entry,
)
from .public_bundle_fast_paths import (
    _looks_like_family_new_calendar_enrollment_query,
    _looks_like_first_month_risks_query,
    _looks_like_health_authorization_bridge_query,
    _looks_like_permanence_family_query,
    _looks_like_process_compare_query,
)
from .public_doc_knowledge import (
    compose_public_canonical_lane_answer,
    compose_public_family_new_calendar_assessment_enrollment,
    compose_public_first_month_risks,
    compose_public_health_authorizations_bridge,
    compose_public_health_second_call,
    compose_public_permanence_and_family_support,
    compose_public_process_compare,
    compose_public_timeline_lifecycle_bundle,
    match_public_canonical_lane,
)
from .public_known_unknowns import compose_public_known_unknown_answer, detect_public_known_unknown_key
from .public_query_patterns import (
    _looks_like_access_scope_query,
    _looks_like_bolsas_and_processes_query,
    _looks_like_cross_document_public_query,
    _looks_like_health_second_call_query,
    _looks_like_public_leadership_contact_query,
    _looks_like_policy_compare_query,
    _looks_like_public_teacher_identity_query,
    _looks_like_service_credentials_bundle_query,
    _looks_like_service_routing_query,
)
from .semantic_ingress_runtime import semantic_ingress_act


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
    format_brl: Callable[[Any], str]
    hypothetical_children_quantity: Callable[[str], int | None]
    pricing_projection: Callable[..., dict[str, Any]]
    compose_public_bolsas_and_processes: Callable[[dict[str, Any] | None], str | None]


def _looks_like_public_pricing_query(normalized: str) -> bool:
    pricing_anchor_terms = {
        'mensalidade',
        'mensalidades',
        'valor',
        'valores',
        'preco',
        'preços',
        'preco',
        'custa',
        'custaria',
        'custo',
        'investimento',
        'taxa',
        'quanto',
        'pagaria',
        'pagar',
        'bolsa',
        'bolsas',
        'desconto',
        'descontos',
    }
    if not any(term in normalized for term in pricing_anchor_terms):
        return False
    if 'matricula' not in normalized and 'matrícula' not in normalized and 'mensalidade' not in normalized and 'mensalidades' not in normalized:
        return False
    return not any(
        term in normalized
        for term in {
            'fatura',
            'faturas',
            'boleto',
            'boletos',
            'em aberto',
            'vencimento',
            'vencida',
            'vencidas',
            'do lucas',
            'da ana',
            'meu filho',
            'minha filha',
        }
    )


def _public_pricing_segment_hint(normalized_messages: list[str]) -> str | None:
    for message in normalized_messages:
        if any(term in message for term in {'ensino medio', 'ensino médio', '1o ano', '2o ano', '3o ano'}):
            return 'Ensino Medio'
        if any(term in message for term in {'fundamental ii', '6o ano', '7o ano', '8o ano', '9o ano'}):
            return 'Ensino Fundamental II'
        if any(term in message for term in {'fundamental i', '1o ano do fundamental', '2o ano do fundamental', '3o ano do fundamental', '4o ano do fundamental', '5o ano do fundamental'}):
            return 'Ensino Fundamental I'
    return None


def _public_pricing_context_follow_up(normalized: str, recent_user_messages: list[str]) -> bool:
    if _looks_like_public_pricing_query(normalized):
        return False
    pricing_context_active = any(_looks_like_public_pricing_query(message) for message in recent_user_messages)
    if not pricing_context_active:
        return False
    if normalized in {'1o', '2o', '3o', '6o', '7o', '8o', '9o'}:
        return True
    if re.fullmatch(r'(1o|2o|3o|6o|7o|8o|9o)\s+ano', normalized):
        return True
    return normalized.startswith('e para') or 'filhos' in normalized or 'alunos' in normalized


def _format_full_date_br(value: date) -> str:
    month_name = (
        'janeiro',
        'fevereiro',
        'março',
        'abril',
        'maio',
        'junho',
        'julho',
        'agosto',
        'setembro',
        'outubro',
        'novembro',
        'dezembro',
    )[value.month - 1]
    return f'{value.day} de {month_name} de {value.year}'


def _timeline_entry_date_label(entry: dict[str, Any] | None) -> str:
    if not isinstance(entry, dict):
        return ''
    raw = str(entry.get('event_date') or '').strip()
    if raw:
        try:
            return _format_full_date_br(date.fromisoformat(raw))
        except ValueError:
            pass
    summary = str(entry.get('summary') or '').strip()
    match = re.search(r'\b\d{1,2}\s+de\s+[a-zç]+\s+de\s+\d{4}\b', str(summary).lower())
    return match.group(0) if match else ''


def _looks_like_capabilities_query(normalized: str) -> bool:
    return any(
        term in normalized
        for term in {
            'quais opcoes de assuntos',
            'opcoes de assuntos',
            'opções de assuntos',
            'o que voce faz',
            'o que você faz',
            'como voce pode me ajudar',
            'como você pode me ajudar',
            'quais assuntos',
        }
    )


def _compose_capabilities_fast_answer(profile: dict[str, Any] | None, *, school_name: str) -> str:
    capability_model = (profile or {}).get('assistant_capabilities') if isinstance(profile, dict) else None
    public_topics = [
        str(item).strip()
        for item in ((capability_model or {}).get('public_topics') or [])
        if isinstance(item, str) and str(item).strip()
    ]
    protected_topics = [
        str(item).strip()
        for item in ((capability_model or {}).get('protected_topics') or [])
        if isinstance(item, str) and str(item).strip()
    ]
    public_summary = '; '.join(public_topics[:3]) if public_topics else 'matricula, secretaria, financeiro e visitas'
    protected_summary = '; '.join(protected_topics[:2]) if protected_topics else 'notas, faltas e pagamentos'
    return (
        f'Por aqui eu consigo te ajudar com {public_summary} no {school_name}. '
        f'Se sua conta estiver vinculada, eu tambem consigo consultar {protected_summary}.'
    )


def _compose_language_preference_fast_answer(*, school_name: str, message: str) -> str:
    normalized = str(message or '').casefold()
    if 'admissions' in normalized and any(term in normalized for term in {'ingles', 'inglês', 'english'}):
        return (
            f'Voce tem razao em estranhar isso. Aqui no EduAssist do {school_name}, eu vou responder em portugues. '
            'Quando eu mencionar admissions, leia como matricula e atendimento comercial.'
        )
    return (
        f'Perfeito. Eu sigo em portugues aqui no EduAssist do {school_name}. '
        'Se algum termo sair em ingles, eu reformulo em portugues e explico o setor com nomes locais.'
    )


def _looks_like_visit_reschedule_follow_up(normalized: str, recent_user_messages: list[str]) -> bool:
    asks_reschedule = any(
        term in normalized
        for term in {'remarcar', 'reagendar', 'mudar horario', 'mudar horário', 'trocar horario', 'trocar horário', 'se eu precisar remarcar'}
    )
    if not asks_reschedule:
        return False
    if any(term in normalized for term in {'visita', 'tour'}):
        return True
    recent_blob = ' '.join(recent_user_messages[-4:])
    return any(term in recent_blob for term in {'visita', 'tour', 'agendar uma visita'})


def _looks_like_visit_resume_follow_up(normalized: str, recent_user_messages: list[str]) -> bool:
    asks_resume = any(
        term in normalized
        for term in {
            'retomar',
            'retomar depois',
            'por onde volto',
            'como volto',
            'volto por onde',
            'abrir outro pedido',
            'abrir outro agendamento',
            'novo agendamento',
        }
    )
    if not asks_resume:
        return False
    if any(term in normalized for term in {'visita', 'tour'}):
        return True
    recent_blob = ' '.join(recent_user_messages[-4:])
    return any(term in recent_blob for term in {'visita', 'tour', 'agendar uma visita', 'protocolo'})


def _looks_like_teacher_directory_follow_up(normalized: str, recent_user_messages: list[str]) -> bool:
    asks_boundary = any(
        term in normalized
        for term in {
            'esse contato',
            'esse canal',
            'a escola divulga',
            'divulga esse contato',
            'divulga esse canal',
            'coordenação',
            'coordenacao',
            'procurar a coordenação',
            'procurar a coordenacao',
            'manda procurar',
        }
    )
    if not asks_boundary:
        return False
    recent_blob = ' '.join(recent_user_messages[-4:])
    return any(term in recent_blob for term in {'professor', 'professora', 'docente', 'teacher_directory'})


def _compose_public_pricing_fast_text(
    *,
    profile: dict[str, Any] | None,
    message: str,
    normalized: str,
    pricing_query_active: bool,
    pricing_segment_hint: str | None,
    deps: FastPathDeps,
) -> str | None:
    quantity = deps.hypothetical_children_quantity(message)
    if quantity is not None and (
        any(term in normalized for term in {"matricula", "mensalidade", "pagar", "pagaria"})
        or pricing_query_active
    ):
        projection = deps.pricing_projection(profile, quantity=quantity, segment_hint=pricing_segment_hint)
        total_enrollment = Decimal(str(projection.get("total_enrollment_fee", "0") or "0")).quantize(Decimal("0.01"))
        total_monthly = Decimal(str(projection.get("total_monthly_amount", "0") or "0")).quantize(Decimal("0.01"))
        segment = str(projection.get("segment", "") or "segmento publico de referencia").strip()
        return (
            f"Usando a referencia publica atual para {segment}, {quantity} aluno(s) dariam "
            f"R$ {total_enrollment:,.2f} de matricula e R$ {total_monthly:,.2f} de mensalidade por mes."
        ).replace(",", "X").replace(".", ",").replace("X", ".")

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
                segment = str(chosen.get("segment") or pricing_segment_hint).strip()
                return (
                    f"Para {segment}, a mensalidade publica de referencia e {monthly} "
                    f"e a matricula e {enrollment}."
                )

    if profile and _looks_like_bolsas_and_processes_query(message):
        return deps.compose_public_bolsas_and_processes(profile)
    return None


def _compose_public_multi_intent_fast_answer(
    *,
    profile: dict[str, Any] | None,
    message: str,
    normalized: str,
    pricing_query_active: bool,
    pricing_segment_hint: str | None,
    deps: FastPathDeps,
) -> str | None:
    sections: list[tuple[str, str]] = []

    if _looks_like_service_routing_query(message):
        routing_answer = _compose_service_routing_fast_answer(profile, message)
        if routing_answer:
            sections.append(("Setor certo por assunto", routing_answer.replace("\n", " ")))

    wants_general_contacts = any(
        term in normalized
        for term in {"contato", "contatos", "secretaria", "telefone", "whatsapp", "email", "endereco", "endereço"}
    )
    if wants_general_contacts:
        contact_answer = _compose_contact_bundle_answer(profile, message=message)
        if contact_answer:
            sections.append(("Canais gerais da escola", contact_answer.replace("\n", " ")))

    pricing_answer = _compose_public_pricing_fast_text(
        profile=profile,
        message=message,
        normalized=normalized,
        pricing_query_active=pricing_query_active,
        pricing_segment_hint=pricing_segment_hint,
        deps=deps,
    )
    if pricing_answer:
        sections.append(("Valores publicos e simulacao", pricing_answer.replace("\n", " ")))

    deduped_sections: list[tuple[str, str]] = []
    seen_answers: set[str] = set()
    for label, answer in sections:
        if answer in seen_answers:
            continue
        seen_answers.add(answer)
        deduped_sections.append((label, answer))
    if len(deduped_sections) < 2:
        return None

    intro = (
        "Posso separar esse pedido em duas frentes complementares:"
        if len(deduped_sections) == 2
        else "Posso separar esse pedido em frentes complementares:"
    )
    lines = [intro]
    lines.extend(f"- {label}: {answer}" for label, answer in deduped_sections[:3])
    return "\n".join(lines)


def _augment_public_followup_message(
    message: str,
    recent_user_messages: list[str],
    *,
    deps: FastPathDeps,
) -> str:
    normalized = deps.normalize_text(message)
    recent_blob = " ".join(recent_user_messages)
    if (
        any(term in normalized for term in {"uma linha por setor", "sem explicar o resto da escola", "reduz para uma linha"})
        and any(term in recent_blob for term in {"bolsa", "bolsas", "financeiro", "direcao", "direção"})
    ):
        return "Me diga so os canais de bolsas, financeiro e direcao. Uma linha por setor, sem explicar o resto da escola."
    if (
        any(term in normalized for term in {"qual desses setores entra primeiro", "qual setor entra primeiro", "entra primeiro"})
        and "bolsa" in recent_blob
    ):
        return "Se o tema for bolsa com documento pendente, qual desses setores entra primeiro entre bolsas, financeiro e direcao? Seja objetivo."
    if (
        any(term in normalized for term in {"contatos", "contato", "secretaria", "financeiro", "junto com isso"})
        and any(term in recent_blob for term in {"portal", "documentos", "secretaria", "matricula", "matrícula"})
    ):
        return (
            "como entrar em contato com a secretaria e com o financeiro "
            "no fluxo publico de portal, secretaria e envio de documentos"
        )
    if (
        any(term in normalized for term in {"depois disso", "proximo marco", "próximo marco"})
        and any(term in normalized for term in {"familias", "famílias", "responsaveis", "responsáveis", "reuniao", "reunião"})
        and any(term in recent_blob for term in {"portal", "documentos", "secretaria", "matricula", "matrícula", "inicio das aulas", "início das aulas"})
    ):
        return (
            "ordenar a linha do tempo publica entre matricula, envio de documentos, "
            "inicio das aulas e o proximo marco com as familias"
        )
    if (
        any(term in normalized for term in {"so o calendario publico", "só o calendário público", "quero so o calendario publico", "quero só o calendário público"})
        and any(term in recent_blob for term in {"quando comecam as aulas", "quando começam as aulas", "calendario", "calendário", "notas da ana", "notas"})
    ):
        return "Me diga so o calendario publico da escola, com inicio das aulas e eventos abertos para familias."
    if (
        any(term in normalized for term in {"apenas o que e publico nesse tema", "apenas o que é publico nesse tema", "so o que e publico nesse tema", "só o que é público nesse tema"})
        and any(term in recent_blob for term in {"viagem internacional", "viagem", "saidas pedagogicas", "saídas pedagógicas", "autorizacao", "autorização", "protocolo interno"})
    ):
        return f"{message} sobre saidas pedagogicas, viagens e autorizacoes na documentacao publica da escola"
    if (
        any(term in normalized for term in {"o que existe de publico", "o que existe de público", "esse tipo de saida", "esse tipo de saída", "protocolo"})
        and any(term in recent_blob for term in {"excursao", "excursão", "saidas pedagogicas", "saídas pedagógicas", "viagem", "autorizacao", "autorização"})
    ):
        return "Me diga so o que existe de publico sobre saidas pedagogicas, viagens e protocolo de autorizacao da escola."
    if (
        any(term in normalized for term in {"resume isso em dois passos praticos", "resuma isso em dois passos praticos", "resume em dois passos praticos"})
        and any(term in recent_blob for term in {"excursao", "excursão", "saidas pedagogicas", "saídas pedagógicas", "viagem", "autorizacao", "autorização"})
    ):
        return "Resuma em dois passos praticos o que existe de publico sobre saidas pedagogicas, viagens e autorizacoes da escola."
    if _looks_like_teacher_directory_follow_up(normalized, recent_user_messages):
        return (
            "A escola divulga contato direto de professor por disciplina, "
            "ou manda procurar a coordenacao pedagogica pelo canal institucional?"
        )
    return message


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
    from .fast_path_answer_runtime import build_fast_path_answer as _impl

    return _impl(ctx, deps)
