from __future__ import annotations

import re
from typing import Any

import httpx

from .answer_payloads import default_suggested_replies
from .models import (
    MessageEvidencePack,
    MessageEvidenceSupport,
    MessageIntentClassification,
    SupervisorAnswerPayload,
)
from .runtime_io import _http_get


def _normalize_text(value: str | None) -> str:
    return re.sub(r"\s+", " ", str(value or "").strip().lower())


def _safe_excerpt(value: str | None, *, limit: int = 220) -> str | None:
    text = str(value or "").strip()
    if not text:
        return None
    if len(text) <= limit:
        return text
    return f"{text[: limit - 3].rstrip()}..."


def _school_name(profile: dict[str, Any] | None) -> str:
    return str((profile or {}).get("school_name") or "Colegio Horizonte").strip() or "Colegio Horizonte"


def _extract_recent_user_messages(conversation_context: dict[str, Any] | None) -> list[str]:
    items = conversation_context.get("recent_messages") if isinstance(conversation_context, dict) else None
    if not isinstance(items, list):
        return []
    return [str(item.get("content") or "").strip() for item in items if isinstance(item, dict) and item.get("sender_type") == "user"]


def _normalized_recent_user_messages(conversation_context: dict[str, Any] | None) -> list[str]:
    return [_normalize_text(item) for item in _extract_recent_user_messages(conversation_context)]


def _teacher_session_active(ctx: Any) -> bool:
    actor_role = str((ctx.actor or {}).get("role_code", "") or "").strip().lower()
    return actor_role == "teacher" or (
        ctx.request.user.authenticated and str(ctx.request.user.role or "").strip().lower() == "teacher"
    )


def _looks_like_teacher_scope_query(message: str, recent_user_messages: list[str]) -> bool:
    normalized = _normalize_text(message)
    if _looks_like_teacher_summary_request(message):
        return True
    direct_terms = {
        "ja sou professor",
        "já sou professor",
        "ja sou professora",
        "já sou professora",
        "meu horario",
        "meu horário",
        "meus horarios",
        "meus horários",
        "meu horario de aula",
        "meu horário de aula",
        "minhas turmas",
        "minhas disciplinas",
        "meus alunos",
        "grade docente",
        "minha grade docente",
        "minha grade",
        "quais turmas eu tenho",
        "quais turmas eu atendo",
        "quais disciplinas eu tenho",
        "quais disciplinas eu atendo",
        "quais turmas e disciplinas eu tenho",
        "quais turmas e disciplinas eu atendo",
        "rotina docente",
    }
    if any(term in normalized for term in direct_terms):
        return True
    teacher_thread_active = any(_looks_like_teacher_scope_query(item, []) for item in recent_user_messages[-4:])
    if not teacher_thread_active:
        return False
    return any(
        term in normalized
        for term in {
            "ensino medio",
            "ensino médio",
            "medio",
            "médio",
            "fundamental",
            "turmas",
            "disciplinas",
            "classes",
            "grade",
        }
    )


def _compose_teacher_access_scope_answer(actor: dict[str, Any] | None, *, school_name: str) -> str:
    actor_name = str((actor or {}).get("full_name", "Professor")).strip() or "Professor"
    role_code = str((actor or {}).get("role_code", "") or "").strip().lower()
    if role_code == "teacher":
        return (
            f"Voce esta falando aqui como {actor_name}, no perfil de professor do {school_name}. "
            "Neste canal eu consigo consultar sua grade docente, turmas e disciplinas. "
            "A situacao individual dos alunos ainda nao fica exposta por aqui. "
            'Se quiser, me pergunte "qual meu horario?", "quais sao minhas turmas?" ou "quais disciplinas eu ministro?".'
        )
    return (
        f"Se voce ja e professor do {school_name}, o acesso docente depende da vinculacao da conta institucional correta no Telegram. "
        "Nesta conta atual eu nao identifiquei um perfil docente ativo. "
        "Quando a vinculacao de professor estiver correta, por aqui eu consigo consultar horario, turmas e disciplinas."
    )


def _segment_filter_for_teacher_message(message: str) -> str | None:
    normalized = _normalize_text(message)
    if any(term in normalized for term in {"ensino medio", "ensino médio", "medio", "médio"}):
        return "medio"
    if "fundamental" in normalized or any(token in normalized for token in {"6o", "7o", "8o", "9o"}):
        return "fundamental"
    return None


def _assignment_matches_segment(assignment: dict[str, Any], segment_filter: str | None) -> bool:
    if not segment_filter:
        return True
    class_name = _normalize_text(str(assignment.get("class_name", "") or ""))
    structured_segment = _normalize_text(
        str(
            assignment.get("segment")
            or assignment.get("grade_segment")
            or assignment.get("education_stage")
            or ""
        )
    )
    try:
        grade_level = int(assignment.get("grade_level") or 0)
    except Exception:
        grade_level = 0
    if segment_filter == "medio":
        if "medio" in structured_segment or "médio" in structured_segment:
            return True
        if grade_level >= 10:
            return True
        return any(
            token in class_name
            for token in {"medio", "médio", "1a serie", "2a serie", "3a serie", "1a série", "2a série", "3a série", "1em", "2em", "3em"}
        )
    if "fundamental" in structured_segment:
        return True
    if 6 <= grade_level <= 9:
        return True
    return any(
        token in class_name for token in {"fundamental", "6o", "7o", "8o", "9o", "6 ano", "7 ano", "8 ano", "9 ano"}
    )


def _teacher_subject_filter(assignments: list[dict[str, Any]], *, message: str) -> str | None:
    normalized = _normalize_text(message)
    for item in assignments:
        subject_name = str(item.get("subject_name", "") or "").strip()
        if not subject_name:
            continue
        subject_normalized = _normalize_text(subject_name)
        if subject_normalized and subject_normalized in normalized:
            return subject_name
    return None


def _render_teacher_schedule_answer(summary: dict[str, Any], *, message: str) -> str:
    teacher_name = str(summary.get("teacher_name", "Professor")).strip() or "Professor"
    assignments = summary.get("assignments") if isinstance(summary.get("assignments"), list) else []
    segment_filter = _segment_filter_for_teacher_message(message)
    subject_filter = _teacher_subject_filter(assignments, message=message)
    filtered = [
        item
        for item in assignments
        if isinstance(item, dict)
        and _assignment_matches_segment(item, segment_filter)
        and (not subject_filter or str(item.get("subject_name", "") or "").strip() == subject_filter)
    ]
    normalized = _normalize_text(message)
    asks_schedule = any(term in normalized for term in {"horario", "horário", "grade", "agenda", "hoje"})
    asks_classes_only = ("turma" in normalized or "classe" in normalized) and "disciplin" not in normalized
    segment_label = (
        "Ensino Medio"
        if segment_filter == "medio"
        else "Ensino Fundamental II"
        if segment_filter == "fundamental"
        else None
    )
    asks_panorama = any(
        term in normalized
        for term in {
            "panorama",
            "resumo",
            "rotina docente",
            "deste ano",
        }
    ) or ("turma" in normalized and "disciplin" in normalized)
    if asks_panorama:
        classes: list[str] = []
        subjects: list[str] = []
        seen_classes: set[str] = set()
        seen_subjects: set[str] = set()
        for item in filtered:
            class_name = str(item.get("class_name", "") or "").strip()
            subject_name = str(item.get("subject_name", "") or "").strip()
            if class_name and class_name not in seen_classes:
                seen_classes.add(class_name)
                classes.append(class_name)
            if subject_name and subject_name not in seen_subjects:
                seen_subjects.add(subject_name)
                subjects.append(subject_name)
        scope_label = f" no {segment_label}" if segment_label else ""
        parts = [
            f"Resumo docente de {teacher_name}{scope_label}: {len(classes)} turma(s) e {len(subjects)} disciplina(s) ativas nesta base."
        ]
        if subjects:
            parts.append("Disciplinas: " + ", ".join(subjects[:4]) + ".")
        if classes:
            parts.append("Turmas: " + ", ".join(classes[:4]) + ".")
        return " ".join(parts)
    if ("so do ensino medio" in normalized or "só do ensino médio" in normalized) and assignments:
        return "Sim, sua grade atual fica concentrada no Ensino Medio." if len(filtered) == len(assignments) else "Nao. Sua grade atual nao e so do Ensino Medio."
    if ("so do fundamental" in normalized or "só do fundamental" in normalized) and assignments:
        return "Sim, sua grade atual fica concentrada no Ensino Fundamental II." if len(filtered) == len(assignments) else "Nao. Sua grade atual nao e so do Ensino Fundamental II."
    if "disciplin" in normalized and "turma" not in normalized and "classe" not in normalized:
        seen: set[str] = set()
        lines: list[str] = []
        for item in filtered:
            subject_name = str(item.get("subject_name", "Disciplina")).strip()
            if subject_name and subject_name not in seen:
                seen.add(subject_name)
                lines.append(f"- {subject_name}")
        return "\n".join([f"Disciplinas de {teacher_name}:", *(lines or ["- Nenhuma disciplina encontrada."])])
    if asks_schedule and asks_classes_only:
        schedule_lines = [
            "- {class_name} - {subject_name} ({academic_year})".format(
                class_name=item.get("class_name", "Turma"),
                subject_name=item.get("subject_name", "Disciplina"),
                academic_year=item.get("academic_year", "---"),
            )
            for item in filtered[:6]
        ]
        class_seen: set[str] = set()
        class_lines: list[str] = []
        for item in filtered:
            class_name = str(item.get("class_name", "Turma")).strip()
            if class_name and class_name not in class_seen:
                class_seen.add(class_name)
                class_lines.append(f"- {class_name}")
        heading = (
            f"Horario de hoje e turmas de {teacher_name} no {segment_label}:"
            if segment_label
            else f"Horario de hoje e turmas de {teacher_name}:"
        )
        return "\n".join(
            [
                heading,
                *(schedule_lines or ["- Nenhuma alocacao docente encontrada."]),
                f"Turmas de {teacher_name}:",
                *(class_lines or ["- Nenhuma turma encontrada."]),
            ]
        )
    if asks_classes_only:
        seen: set[str] = set()
        lines: list[str] = []
        for item in filtered:
            class_name = str(item.get("class_name", "Turma")).strip()
            if class_name and class_name not in seen:
                seen.add(class_name)
                lines.append(f"- {class_name}")
        return "\n".join([f"Turmas de {teacher_name}:", *(lines or ["- Nenhuma turma encontrada."])])
    if subject_filter and ("turma" in normalized or "classe" in normalized):
        seen: set[str] = set()
        lines: list[str] = []
        for item in filtered:
            class_name = str(item.get("class_name", "Turma")).strip()
            if class_name and class_name not in seen:
                seen.add(class_name)
                lines.append(f"- {class_name}")
        return "\n".join([f"Turmas de {teacher_name} em {subject_filter}:", *(lines or ["- Nenhuma turma encontrada."])])
    lines = [
        "- {class_name} - {subject_name} ({academic_year})".format(
            class_name=item.get("class_name", "Turma"),
            subject_name=item.get("subject_name", "Disciplina"),
            academic_year=item.get("academic_year", "---"),
        )
        for item in filtered[:8]
    ]
    heading = (
        f"Horario de hoje de {teacher_name} no {segment_label}:"
        if asks_schedule and segment_label
        else f"Horario de hoje de {teacher_name}:"
        if asks_schedule
        else f"Grade docente de {teacher_name} no {segment_label}:"
        if segment_label
        else f"Grade docente de {teacher_name}:"
    )
    return "\n".join(
        [
            heading,
            *(lines or ["- Nenhuma alocacao docente encontrada."]),
        ]
    )


def _looks_like_teacher_summary_request(message: str) -> bool:
    normalized = _normalize_text(message)
    return any(
        term in normalized
        for term in {
            "panorama",
            "resumo",
            "deste ano",
            "turmas e disciplinas",
            "rotina docente",
            "resuma minha rotina docente",
            "resumo enxuto",
            "alocacao",
            "alocação",
            "reuniao pedagogica",
            "reunião pedagógica",
        }
    )


def _compose_teacher_summary_answer(summary: dict[str, Any], *, profile: dict[str, Any] | None, message: str) -> str:
    teacher_name = str(summary.get("teacher_name", "Professor")).strip() or "Professor"
    assignments = summary.get("assignments") if isinstance(summary.get("assignments"), list) else []
    segment_filter = _segment_filter_for_teacher_message(message)
    filtered = [
        item
        for item in assignments
        if isinstance(item, dict) and _assignment_matches_segment(item, segment_filter)
    ]
    segment_label = (
        "Ensino Medio"
        if segment_filter == "medio"
        else "Ensino Fundamental II"
        if segment_filter == "fundamental"
        else None
    )
    classes: list[str] = []
    subjects: list[str] = []
    seen_classes: set[str] = set()
    seen_subjects: set[str] = set()
    for item in filtered:
        class_name = str(item.get("class_name", "") or "").strip()
        subject_name = str(item.get("subject_name", "") or "").strip()
        if class_name and class_name not in seen_classes:
            seen_classes.add(class_name)
            classes.append(class_name)
        if subject_name and subject_name not in seen_subjects:
            seen_subjects.add(subject_name)
            subjects.append(subject_name)
    public_events = (profile or {}).get("public_calendar_events") if isinstance(profile, dict) else None
    event_titles: list[str] = []
    if isinstance(public_events, list):
        for item in public_events:
            if not isinstance(item, dict):
                continue
            title = str(item.get("title", "") or "").strip()
            if title and title not in event_titles:
                event_titles.append(title)
    scope_label = f" no {segment_label}" if segment_label else ""
    parts = [
        f"Resumo docente de {teacher_name}{scope_label}: {len(classes)} turma(s) e {len(subjects)} disciplina(s) ativas nesta base."
    ]
    if subjects:
        parts.append("Disciplinas: " + ", ".join(subjects[:4]) + ".")
    if classes:
        parts.append("Turmas: " + ", ".join(classes[:4]) + ".")
    if event_titles:
        parts.append("No calendario publico, vale acompanhar marcos como " + ", ".join(event_titles[:3]) + ".")
    parts.append("No uso do calendario, priorize datas institucionais abertas a familias e equipe, como reunioes, simulados, conselhos e janelas letivas publicadas.")
    parts.append("Para comunicacao escolar geral, a secretaria e o canal institucional mais seguro; para alinhamentos pedagogicos, o fluxo correto passa por coordenacao e orientacao conforme o assunto.")
    return " ".join(part for part in parts if part).strip()


async def maybe_teacher_scope_fast_path_answer(ctx: Any) -> SupervisorAnswerPayload | None:
    recent_user_messages = _normalized_recent_user_messages(ctx.conversation_context)
    if not _teacher_session_active(ctx):
        return None
    if not _looks_like_teacher_scope_query(ctx.request.message, recent_user_messages):
        return None
    school_name = _school_name(ctx.school_profile if isinstance(ctx.school_profile, dict) else {})
    actor_role = str((ctx.actor or {}).get("role_code", "") or "").strip().lower()
    if actor_role != "teacher" or ctx.request.telegram_chat_id is None:
        answer_text = _compose_teacher_access_scope_answer(ctx.actor, school_name=school_name)
        return SupervisorAnswerPayload(
            message_text=answer_text,
            mode="structured_tool",
            classification=MessageIntentClassification(
                domain="academic",
                access_tier="authenticated",
                confidence=0.94,
                reason="specialist_supervisor_fast_path:teacher_scope_guidance",
            ),
            evidence_pack=MessageEvidencePack(
                strategy="structured_tools",
                summary="Escopo docente protegido orientado por identidade de professor na sessao atual.",
                source_count=1,
                support_count=1,
                supports=[MessageEvidenceSupport(kind="teacher_scope", label="Escopo docente", detail="grade, turmas e disciplinas")],
            ),
            suggested_replies=default_suggested_replies("academic"),
            graph_path=["specialist_supervisor", "fast_path", "teacher_scope_guidance"],
            reason="specialist_supervisor_fast_path:teacher_scope_guidance",
        )
    try:
        payload = await _http_get(
            ctx.http_client,
            base_url=ctx.settings.api_core_url,
            path="/v1/teachers/me/schedule",
            token=ctx.settings.internal_api_token,
            params={"telegram_chat_id": ctx.request.telegram_chat_id},
        )
    except httpx.HTTPError:
        payload = None
    summary = payload.get("summary") if isinstance(payload, dict) else None
    if not isinstance(summary, dict):
        return None
    if _looks_like_teacher_summary_request(ctx.request.message):
        answer_text = _compose_teacher_summary_answer(
            summary,
            profile=ctx.school_profile if isinstance(ctx.school_profile, dict) else None,
            message=ctx.request.message,
        )
    else:
        answer_text = _render_teacher_schedule_answer(summary, message=ctx.request.message)
    return SupervisorAnswerPayload(
        message_text=answer_text,
        mode="structured_tool",
        classification=MessageIntentClassification(
            domain="academic",
            access_tier="authenticated",
            confidence=0.97,
            reason="specialist_supervisor_fast_path:teacher_schedule",
        ),
        evidence_pack=MessageEvidencePack(
            strategy="structured_tools",
            summary="Grade docente lida do servico protegido de agenda do professor.",
            source_count=1,
            support_count=1,
            supports=[MessageEvidenceSupport(kind="teacher_schedule", label="Grade docente", detail=_safe_excerpt(answer_text, limit=180))],
        ),
        suggested_replies=default_suggested_replies("academic"),
        graph_path=["specialist_supervisor", "fast_path", "teacher_schedule"],
        reason="specialist_supervisor_fast_path:teacher_schedule",
    )
