from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Any, Callable

from .models import (
    MessageEvidencePack,
    MessageEvidenceSupport,
    MessageIntentClassification,
    MessageResponseSuggestedReply,
    OperationalMemory,
    ResolvedTurnIntent,
    SupervisorAnswerPayload,
)


@dataclass(frozen=True)
class ProtectedAnswerDeps:
    normalize_text: Callable[[str | None], str]
    linked_students: Callable[..., list[dict[str, Any]]]
    subject_hint_from_text: Callable[[str | None], str | None]
    subject_code_from_hint: Callable[..., tuple[str | None, str | None]]
    access_tier_for_domain: Callable[[str, bool], str]
    default_suggested_replies: Callable[[str], list[MessageResponseSuggestedReply]]
    student_hint_from_message: Callable[..., str | None]
    unknown_explicit_student_reference: Callable[..., str | None]
    is_student_name_only_followup: Callable[..., str | None]
    looks_like_student_pronoun_followup: Callable[[str], bool]
    looks_like_subject_followup: Callable[[str], bool]
    recent_subject_from_context: Callable[..., str | None]
    format_brl: Callable[[Any], str]
    passing_grade_target: Decimal


def subject_grade_snapshot(
    summary: dict[str, Any],
    *,
    deps: ProtectedAnswerDeps,
    preferred_subjects: tuple[str, ...] = ("Historia", "Fisica", "Matematica", "Portugues"),
) -> list[tuple[str, Decimal]]:
    grades = summary.get("grades")
    if not isinstance(grades, list):
        return []
    grouped: dict[str, list[Decimal]] = {}
    display_names: dict[str, str] = {}
    for row in grades:
        if not isinstance(row, dict):
            continue
        subject_name = str(row.get("subject_name") or "").strip()
        if not subject_name:
            continue
        try:
            score = Decimal(str(row.get("score")))
        except Exception:
            continue
        key = deps.normalize_text(subject_name)
        grouped.setdefault(key, []).append(score)
        display_names[key] = subject_name
    averages: list[tuple[str, Decimal]] = []
    for key, scores in grouped.items():
        avg = (sum(scores) / Decimal(len(scores))).quantize(Decimal("0.1"))
        averages.append((display_names[key], avg))
    ordered: list[tuple[str, Decimal]] = []
    for preferred in preferred_subjects:
        for name, avg in averages:
            if deps.normalize_text(name) == deps.normalize_text(preferred):
                ordered.append((name, avg))
                break
    if len(ordered) < 3:
        for name, avg in sorted(averages, key=lambda item: item[0]):
            if (name, avg) not in ordered:
                ordered.append((name, avg))
            if len(ordered) >= 4:
                break
    return ordered[:4]


def compose_academic_snapshot_lines(summary: dict[str, Any], *, deps: ProtectedAnswerDeps) -> list[str]:
    student_name = str(summary.get("student_name") or "Aluno").strip()
    snapshots = subject_grade_snapshot(summary, deps=deps)
    if not snapshots:
        return [f"- {student_name}: sem notas consolidadas neste recorte."]
    preview = "; ".join(f"{name} {str(avg).replace('.', ',')}" for name, avg in snapshots[:4])
    return [f"- {student_name}: {preview}"]


def compose_academic_aggregate_answer(
    summaries: list[dict[str, Any]],
    *,
    deps: ProtectedAnswerDeps,
) -> str:
    if not summaries:
        return "Nao encontrei resumo academico consolidado das contas vinculadas neste recorte."

    lines = ["Panorama academico das contas vinculadas:"]
    highest_risk_student: str | None = None
    highest_risk_subject: str | None = None
    highest_risk_signature: tuple[int, Decimal, str] | None = None

    for summary in summaries:
        student_name = str(summary.get("student_name") or "Aluno").strip() or "Aluno"
        lines.extend(compose_academic_snapshot_lines(summary, deps=deps))
        snapshots = subject_grade_snapshot(summary, deps=deps, preferred_subjects=())
        if not snapshots:
            continue
        below_target = [(name, avg) for name, avg in snapshots if avg < deps.passing_grade_target]
        if below_target:
            subject_name, average = min(
                below_target,
                key=lambda item: (item[1], deps.normalize_text(item[0])),
            )
            signature = (1, deps.passing_grade_target - average, student_name)
        else:
            subject_name, average = min(
                snapshots,
                key=lambda item: (abs(item[1] - deps.passing_grade_target), deps.normalize_text(item[0])),
            )
            signature = (0, deps.passing_grade_target - average, student_name)
        if highest_risk_signature is None or signature > highest_risk_signature:
            highest_risk_signature = signature
            highest_risk_student = student_name
            highest_risk_subject = subject_name

    if highest_risk_student and highest_risk_subject:
        lines.append(
            f"Quem hoje exige maior atencao academica e {highest_risk_student}, principalmente em {highest_risk_subject}."
        )
    return "\n".join(lines)


def compose_named_grade_answer(summary: dict[str, Any], *, deps: ProtectedAnswerDeps) -> str:
    student_name = str(summary.get("student_name") or "Aluno").strip()
    snapshots = subject_grade_snapshot(summary, deps=deps)
    lines = [f"Notas de {student_name}:"]
    for name, avg in snapshots:
        lines.append(f"- {name}: media parcial {str(avg).replace('.', ',')}")
    return "\n".join(lines)


def looks_like_academic_risk_followup(message: str, *, deps: ProtectedAnswerDeps) -> bool:
    normalized = deps.normalize_text(message)
    if any(
        term in normalized
        for term in {
            "por faltas",
            "por frequencia",
            "por frequência",
            "frequencia",
            "frequência",
            "faltas",
            "atrasos",
            "presenca",
            "presença",
            "ausencias",
            "ausências",
        }
    ):
        return False
    return any(
        term in normalized
        for term in {
            "qual disciplina preocupa mais",
            "que disciplina preocupa mais",
            "disciplina preocupa mais",
            "quais disciplinas preocupam mais",
            "qual disciplina merece mais atencao",
            "qual disciplina merece mais atenção",
            "qual foi a menor nota",
            "qual e a menor nota",
            "qual é a menor nota",
            "qual foi a menor media",
            "qual foi a menor média",
            "qual e a menor media",
            "qual é a menor média",
            "menor media",
            "menor média",
            "menores medias",
            "menores médias",
            "onde esta a menor nota",
            "onde está a menor nota",
            "em que componente isso aparece",
            "em que componentes isso aparece",
            "em quais componentes isso aparece",
            "em que componente isso aparece com mais clareza",
            "em que componentes isso aparece com mais clareza",
            "em quais componentes isso aparece com mais clareza",
            "pontos academicos que mais preocupam",
            "pontos acadêmicos que mais preocupam",
            "o que mais preocupa academicamente",
            "o que mais preocupa academicamente nela",
            "o que mais preocupa academicamente nele",
            "risco academico",
            "risco acadêmico",
            "maior risco",
            "corre mais risco",
            "correm mais risco",
            "pontos de maior risco",
            "pontos mais sensiveis",
            "pontos mais sensíveis",
            "mais perto do limite",
            "mais perto da media",
            "mais perto da média",
            "mais proximo do limite",
            "mais próximo do limite",
            "mais vulneravel",
            "mais vulnerável",
            "mais exposta",
            "mais exposto",
            "mais expostas",
            "mais expostos",
            "componentes merecem mais atencao",
            "componentes merecem mais atenção",
            "componentes merecem acompanhamento",
            "componentes exigem mais atencao",
            "componentes exigem mais atenção",
            "acende mais alerta",
            "acendem mais alerta",
            "qual componente dela acende mais alerta",
            "qual componente dele acende mais alerta",
            "qual componente acende mais alerta",
        }
    )


def compose_academic_risk_answer(summary: dict[str, Any], *, deps: ProtectedAnswerDeps) -> str | None:
    student_name = str(summary.get("student_name") or "Aluno").strip()
    snapshots = sorted(
        subject_grade_snapshot(summary, deps=deps, preferred_subjects=()),
        key=lambda item: (item[1], deps.normalize_text(item[0])),
    )
    if not snapshots:
        return None
    lines = [f"As disciplinas que mais preocupam academicamente em {student_name} hoje sao:"]
    for name, avg in snapshots[:3]:
        lines.append(f"- {name}: media parcial {str(avg).replace('.', ',')}")
    top_subject, top_avg = snapshots[0]
    lines.append(
        f"A menor nota parcial neste recorte aparece em {top_subject}, com media {str(top_avg).replace('.', ',')}."
    )
    lines.append("Esses componentes merecem acompanhamento primeiro no proximo ciclo de estudo.")
    return "\n".join(lines)


def looks_like_academic_progression_followup(message: str, *, deps: ProtectedAnswerDeps) -> bool:
    normalized = deps.normalize_text(message)
    best_terms = {
        "melhor disciplina",
        "melhor materia",
        "melhor matéria",
        "melhor componente",
        "mais forte",
        "a melhor",
    }
    worst_terms = {
        "pior disciplina",
        "pior materia",
        "pior matéria",
        "pior componente",
        "mais fraca",
        "mais fraco",
        "a pior",
    }
    gap_terms = {
        "quanto falta",
        "falta quanto",
        "fechar a media",
        "fechar a média",
        "atingir 7",
        "atingir sete",
        "passar de ano",
        "fechar media",
        "fechar média",
    }
    best = any(term in normalized for term in best_terms)
    worst = any(term in normalized for term in worst_terms)
    gap = any(term in normalized for term in gap_terms)
    return (best and worst) or (gap and (best or worst))


def compose_academic_progression_answer(
    summary: dict[str, Any],
    *,
    message: str,
    deps: ProtectedAnswerDeps,
) -> str | None:
    student_name = str(summary.get("student_name") or "Aluno").strip() or "Aluno"
    snapshots = sorted(
        subject_grade_snapshot(summary, deps=deps, preferred_subjects=()),
        key=lambda item: (item[1], deps.normalize_text(item[0])),
    )
    if not snapshots:
        return None
    worst_subject, worst_average = snapshots[0]
    best_subject, best_average = max(
        snapshots,
        key=lambda item: (item[1], item[0]),
    )
    parts = [
        f"Hoje, a melhor disciplina de {student_name} e {best_subject}, com media parcial {str(best_average).replace('.', ',')}.",
        f"A pior disciplina aparece em {worst_subject}, com media parcial {str(worst_average).replace('.', ',')}.",
    ]
    subject_hint = deps.subject_hint_from_text(message)
    subject_code, subject_name = deps.subject_code_from_hint(summary, subject_hint)
    if subject_code or subject_name:
        grades = summary.get("grades")
        scores: list[Decimal] = []
        resolved_subject_name = subject_name or subject_hint or "a disciplina"
        if isinstance(grades, list):
            for row in grades:
                if not isinstance(row, dict):
                    continue
                row_subject_code = str(row.get("subject_code") or "").strip()
                row_subject_name = str(row.get("subject_name") or "").strip()
                if subject_code and row_subject_code != subject_code:
                    continue
                if not subject_code and subject_name and deps.normalize_text(row_subject_name) != deps.normalize_text(subject_name):
                    continue
                try:
                    scores.append(Decimal(str(row.get("score"))))
                except Exception:
                    continue
                if row_subject_name:
                    resolved_subject_name = row_subject_name
        if scores:
            average = (sum(scores) / Decimal(len(scores))).quantize(Decimal("0.1"))
            target = Decimal(str(deps.passing_grade_target)).quantize(Decimal("0.1"))
            gap = max(Decimal("0.0"), target - average).quantize(Decimal("0.1"))
            if gap <= Decimal("0.0"):
                parts.append(
                    f"Em {resolved_subject_name}, a media parcial atual ja esta em {str(average).replace('.', ',')}. Nao falta mais nada para fechar a media: a meta minima de {str(target).replace('.', ',')} ja foi alcancada."
                )
            else:
                parts.append(
                    f"Em {resolved_subject_name}, a media parcial atual e {str(average).replace('.', ',')}; faltam {str(gap).replace('.', ',')} ponto(s) para atingir {str(target).replace('.', ',')}."
                )
    return " ".join(parts)


def compose_named_subject_grade_answer(
    summary: dict[str, Any],
    *,
    subject_hint: str | None,
    deps: ProtectedAnswerDeps,
) -> str | None:
    subject_code, subject_name = deps.subject_code_from_hint(summary, subject_hint)
    if not subject_code and not subject_name:
        return None
    grades = summary.get("grades")
    if not isinstance(grades, list):
        return None
    scores: list[Decimal] = []
    resolved_subject_name = subject_name
    for row in grades:
        if not isinstance(row, dict):
            continue
        row_subject_code = str(row.get("subject_code") or "").strip()
        row_subject_name = str(row.get("subject_name") or "").strip()
        if subject_code and row_subject_code != subject_code:
            continue
        if not subject_code and subject_name and deps.normalize_text(row_subject_name) != deps.normalize_text(subject_name):
            continue
        try:
            scores.append(Decimal(str(row.get("score"))))
        except Exception:
            continue
        if row_subject_name:
            resolved_subject_name = row_subject_name
    if not scores:
        return None
    student_name = str(summary.get("student_name") or "Aluno").strip()
    average = (sum(scores) / Decimal(len(scores))).quantize(Decimal("0.1"))
    return (
        f"A media parcial de {student_name} em {resolved_subject_name or subject_hint or 'a disciplina'} "
        f"e {str(average).replace('.', ',')}."
    )


def compose_named_attendance_answer(
    summary: dict[str, Any],
    *,
    subject_hint: str | None = None,
    deps: ProtectedAnswerDeps,
) -> str | None:
    attendance = summary.get("attendance")
    if not isinstance(attendance, list):
        return None
    subject_code, subject_name = deps.subject_code_from_hint(summary, subject_hint)
    present_total = 0
    late_total = 0
    absent_total = 0
    absent_minutes_total = 0
    resolved_subject_name = subject_name
    for row in attendance:
        if not isinstance(row, dict):
            continue
        row_subject_code = str(row.get("subject_code") or "").strip()
        row_subject_name = str(row.get("subject_name") or "").strip()
        if subject_code and row_subject_code != subject_code:
            continue
        if not subject_code and subject_name and deps.normalize_text(row_subject_name) != deps.normalize_text(subject_name):
            continue
        present_total += int(row.get("present_count") or 0)
        late_total += int(row.get("late_count") or 0)
        absent_total += int(row.get("absent_count") or 0)
        absent_minutes_total += int(row.get("absent_minutes") or 0)
        if row_subject_name:
            resolved_subject_name = row_subject_name
    if present_total == late_total == absent_total == absent_minutes_total == 0:
        return None
    student_name = str(summary.get("student_name") or "Aluno").strip()
    scope_label = f" em {resolved_subject_name}" if resolved_subject_name else ""
    return (
        f"Na frequencia de {student_name}{scope_label}, eu encontrei {absent_total} faltas, "
        f"{late_total} atraso(s) e {present_total} presenca(s) neste recorte."
    )


def _linked_student_names(actor: dict[str, Any] | None, *, capability: str, deps: ProtectedAnswerDeps) -> list[str]:
    names: list[str] = []
    for student in deps.linked_students(actor, capability=capability):
        name = str(student.get("full_name") or "").strip()
        if name:
            names.append(name)
    return names


def build_academic_student_selection_clarify(
    ctx: Any,
    *,
    reason: str,
    graph_path: list[str],
    deps: ProtectedAnswerDeps,
    confidence: float = 0.97,
) -> SupervisorAnswerPayload:
    names = _linked_student_names(ctx.actor, capability="academic", deps=deps)
    if len(names) >= 2:
        student_list = " ou ".join(names[:2])
        message_text = f"Consigo consultar isso, mas preciso que voce confirme qual aluno: {student_list}?"
    else:
        message_text = "Consigo consultar isso, mas preciso que voce confirme qual aluno."
    return SupervisorAnswerPayload(
        message_text=message_text,
        mode="clarify",
        classification=MessageIntentClassification(
            domain="academic",
            access_tier=deps.access_tier_for_domain("academic", True),
            confidence=confidence,
            reason=reason,
        ),
        evidence_pack=MessageEvidencePack(
            strategy="structured_tools",
            summary="Clarificacao necessaria para fixar o aluno correto antes da consulta academica.",
            source_count=1,
            support_count=1,
            supports=[
                MessageEvidenceSupport(
                    kind="student_context",
                    label="Alunos vinculados",
                    detail=", ".join(names[:4]) or "Aluno nao resolvido",
                )
            ],
        ),
        suggested_replies=[MessageResponseSuggestedReply(text=name) for name in names[:2]] or deps.default_suggested_replies("academic"),
        graph_path=graph_path,
        reason=reason,
    )


def resolved_academic_target_name(
    ctx: Any,
    *,
    resolved: ResolvedTurnIntent | None = None,
    deps: ProtectedAnswerDeps,
) -> str | None:
    memory = ctx.operational_memory or OperationalMemory()
    if resolved is not None and str(resolved.referenced_student_name or "").strip():
        return str(resolved.referenced_student_name or "").strip()
    if deps.unknown_explicit_student_reference(ctx.actor, ctx.request.message):
        return None
    explicit_hint = deps.student_hint_from_message(ctx.actor, ctx.request.message) or deps.is_student_name_only_followup(
        ctx.actor,
        ctx.request.message,
    )
    if explicit_hint:
        return explicit_hint
    alternate_name = str((getattr(resolved, 'alternate_student_name', None) if resolved is not None else None) or "").strip()
    if not alternate_name:
        alternate_name = str(memory.alternate_student_name or "").strip()
    if alternate_name:
        normalized_message = deps.normalize_text(ctx.request.message)
        alternate_tokens = [deps.normalize_text(token) for token in alternate_name.split() if token.strip()]
        if any(token and token in normalized_message for token in alternate_tokens):
            return alternate_name
    if str(memory.active_student_name or "").strip() and (
        deps.looks_like_student_pronoun_followup(ctx.request.message)
        or deps.looks_like_subject_followup(ctx.request.message)
        or bool(deps.subject_hint_from_text(ctx.request.message))
    ):
        return str(memory.active_student_name or "").strip()
    return None


def needs_specific_academic_student_clarification(
    ctx: Any,
    *,
    target_name: str | None,
    subject_hint: str | None,
    deps: ProtectedAnswerDeps,
) -> bool:
    if target_name:
        return False
    if len(deps.linked_students(ctx.actor, capability="academic")) < 2:
        return False
    return (
        bool(deps.unknown_explicit_student_reference(ctx.actor, ctx.request.message))
        or
        bool(subject_hint)
        or deps.looks_like_student_pronoun_followup(ctx.request.message)
        or deps.looks_like_subject_followup(ctx.request.message)
    )


def compose_academic_finance_combo_answer(
    *,
    academic_summary: dict[str, Any],
    finance_summary: dict[str, Any],
    deps: ProtectedAnswerDeps,
) -> str:
    student_name = str(academic_summary.get("student_name") or finance_summary.get("student_name") or "Aluno").strip()
    lines = [f"Resumo combinado de {student_name}:"]
    snapshots = subject_grade_snapshot(academic_summary, deps=deps)
    if snapshots:
        preview = "; ".join(f"{name} {str(avg).replace('.', ',')}" for name, avg in snapshots[:3])
        lines.append(f"- Academico: {preview}")
    open_count = int(finance_summary.get("open_invoice_count", 0) or 0)
    overdue_count = int(finance_summary.get("overdue_invoice_count", 0) or 0)
    lines.append(f"- Financeiro: {open_count} em aberto, {overdue_count} vencidas")
    invoices = finance_summary.get("invoices")
    if isinstance(invoices, list):
        unpaid = [
            item
            for item in invoices
            if isinstance(item, dict) and str(item.get("status") or "").strip().lower() in {"open", "overdue", "pending"}
        ]
        if unpaid:
            next_invoice = sorted(unpaid, key=lambda item: str(item.get("due_date") or "9999-99-99"))[0]
            lines.append(
                f"- Proximo vencimento deste recorte: {next_invoice.get('due_date', '--')} no valor de {deps.format_brl(next_invoice.get('amount_due'))}"
            )
    return "\n".join(lines)


def merge_domain_suggested_replies(
    domains: list[str],
    *,
    deps: ProtectedAnswerDeps,
) -> list[MessageResponseSuggestedReply]:
    merged: list[MessageResponseSuggestedReply] = []
    seen: set[str] = set()
    for domain in domains:
        for item in deps.default_suggested_replies(domain):
            text = str(item.text).strip()
            if not text or text in seen:
                continue
            seen.add(text)
            merged.append(item)
            if len(merged) >= 4:
                return merged
    return merged[:4]


def build_academic_finance_combo_payload(
    *,
    academic_summary: dict[str, Any],
    finance_summary: dict[str, Any],
    reason: str,
    graph_path: list[str],
    deps: ProtectedAnswerDeps,
) -> SupervisorAnswerPayload:
    student_name = str(academic_summary.get("student_name") or finance_summary.get("student_name") or "Aluno").strip()
    return SupervisorAnswerPayload(
        message_text=compose_academic_finance_combo_answer(
            academic_summary=academic_summary,
            finance_summary=finance_summary,
            deps=deps,
        ),
        mode="structured_tool",
        classification=MessageIntentClassification(
            domain="academic",
            access_tier="authenticated",
            confidence=0.99,
            reason=reason,
        ),
        evidence_pack=MessageEvidencePack(
            strategy="structured_tools",
            summary="Composicao deterministica de resumo academico e financeiro no mesmo turno.",
            source_count=2,
            support_count=2,
            supports=[
                MessageEvidenceSupport(kind="academic_summary", label=student_name, detail="Notas consolidadas do aluno."),
                MessageEvidenceSupport(kind="finance_summary", label=student_name, detail="Resumo de boletos e vencimentos do aluno."),
            ],
        ),
        suggested_replies=merge_domain_suggested_replies(["academic", "finance"], deps=deps) or deps.default_suggested_replies("academic"),
        graph_path=graph_path,
        reason=reason,
    )


def academic_grade_requirement(
    summary: dict[str, Any],
    *,
    subject_hint: str | None,
    deps: ProtectedAnswerDeps,
) -> dict[str, Any]:
    subject_code, subject_name = deps.subject_code_from_hint(summary, subject_hint)
    if not subject_code and not subject_name:
        return {"error": "subject_not_found", "subject_hint": subject_hint}
    grades = summary.get("grades")
    if not isinstance(grades, list):
        return {"error": "grades_unavailable"}
    relevant_scores: list[Decimal] = []
    for item in grades:
        if not isinstance(item, dict):
            continue
        if subject_code and str(item.get("subject_code", "")).strip() != subject_code:
            continue
        score = item.get("score")
        if score is None:
            continue
        try:
            relevant_scores.append(Decimal(str(score)))
        except Exception:
            continue
    if not relevant_scores:
        return {"error": "subject_not_found", "subject_hint": subject_hint}
    average = sum(relevant_scores) / Decimal(len(relevant_scores))
    needed = deps.passing_grade_target - average
    if needed < Decimal("0"):
        needed = Decimal("0")
    return {
        "subject_name": subject_name or subject_hint,
        "current_average": str(average.quantize(Decimal("0.1"))),
        "passing_target": str(deps.passing_grade_target),
        "points_needed": str(needed.quantize(Decimal("0.1"))),
        "evidence_count": len(relevant_scores),
    }


def compose_authenticated_scope_answer(actor: dict[str, Any] | None, *, deps: ProtectedAnswerDeps) -> str:
    academic_students = deps.linked_students(actor, capability="academic")
    finance_students = deps.linked_students(actor, capability="finance")
    merged: dict[str, dict[str, Any]] = {}
    academic_ids = {str(student.get("student_id") or "").strip() for student in academic_students}
    finance_ids = {str(student.get("student_id") or "").strip() for student in finance_students}
    for student in [*academic_students, *finance_students]:
        student_id = str(student.get("student_id") or "").strip()
        if student_id:
            merged[student_id] = student
    if not merged:
        return (
            "Para consultas protegidas, como notas, faltas e financeiro, voce precisa vincular sua conta do Telegram ao portal da escola. "
            "No portal autenticado, gere o codigo de vinculacao e depois envie aqui o comando `/start link_<codigo>`."
        )
    names = [str(item.get("full_name") or "Aluno").strip() for item in merged.values()]
    rendered_names = ", ".join(names[:-1]) + f" e {names[-1]}" if len(names) > 1 else names[0]
    scope_lines: list[str] = []
    for student_id, student in merged.items():
        student_name = str(student.get("full_name") or "Aluno").strip() or "Aluno"
        scopes: list[str] = []
        if student_id in academic_ids:
            scopes.append("academico")
        if student_id in finance_ids:
            scopes.append("financeiro")
        if scopes:
            scope_lines.append(f"- {student_name}: {', '.join(scopes)}")
    scope_block = f" Escopo atual:\n{'\n'.join(scope_lines)}" if scope_lines else ""
    return (
        f"Voce ja esta autenticado por aqui e sua conta esta vinculada a {rendered_names}. "
        "Neste canal eu consigo consultar academico e financeiro dos alunos vinculados dentro das permissoes da conta. "
        f"{scope_block}"
        'Se quiser, me diga algo como "notas do Lucas", "faltas da Ana" ou "financeiro da Ana".'
    )


def looks_like_third_party_student_data_request(message: str, *, deps: ProtectedAnswerDeps) -> bool:
    normalized = deps.normalize_text(message)
    relationship_terms = {
        "vizinha",
        "vizinho",
        "colega",
        "amigo",
        "amiga",
        "sobrinho",
        "sobrinha",
        "afilhado",
        "afilhada",
        "filho da minha",
        "filha da minha",
        "filho do meu",
        "filha do meu",
        "outra familia",
        "outra família",
        "outra pessoa",
        "outro aluno",
        "outra aluna",
    }
    if not any(term in normalized for term in relationship_terms):
        return False
    return any(
        term in normalized
        for term in {
            "nota",
            "notas",
            "falta",
            "faltas",
            "financeiro",
            "mensalidade",
            "boleto",
            "boletos",
            "fatura",
            "faturas",
            "documentacao",
            "documentação",
            "historico",
            "histórico",
        }
    )


def compose_finance_aggregate_answer(
    summaries: list[dict[str, Any]],
    *,
    deps: ProtectedAnswerDeps,
) -> str:
    total_open = sum(int(item.get("open_invoice_count", 0) or 0) for item in summaries)
    total_overdue = sum(int(item.get("overdue_invoice_count", 0) or 0) for item in summaries)
    lines: list[str] = []
    if total_overdue > 0:
        lines.append("Hoje existe bloqueio financeiro por atraso vencido no recorte da familia.")
    elif total_open > 0:
        lines.append("Hoje nao ha bloqueio financeiro por atraso vencido no recorte da familia.")
    else:
        lines.append("Hoje nao ha pendencia financeira aberta no recorte da familia.")
    lines.extend(
        [
            "Resumo financeiro das contas vinculadas:",
            f"- Total de faturas em aberto: {total_open}",
            f"- Total de faturas vencidas: {total_overdue}",
        ]
    )
    if total_open or total_overdue:
        lines.append(
            f"- Mensalidade: neste recorte, o financeiro mostra {total_open} cobranca(s) em aberto e {total_overdue} vencida(s) nas faturas escolares."
        )
        lines.append("- Taxa: nao apareceu taxa separada neste recorte financeiro das contas vinculadas.")
        lines.append(
            "- Atraso: "
            + (
                "ha faturas vencidas que pedem regularizacao imediata."
                if total_overdue > 0
                else "nao ha fatura vencida agora, so acompanhamento dos proximos vencimentos."
            )
        )
        lines.append(
            "- Desconto: nao apareceu desconto separado nas faturas deste recorte; se existir negociacao comercial, ela precisa ser confirmada com o financeiro."
        )
    for summary in summaries:
        student_name = str(summary.get("student_name") or "Aluno").strip()
        open_count = int(summary.get("open_invoice_count", 0) or 0)
        overdue_count = int(summary.get("overdue_invoice_count", 0) or 0)
        lines.append(f"- {student_name}: {open_count} em aberto, {overdue_count} vencidas")
        invoices = summary.get("invoices")
        if not isinstance(invoices, list):
            continue
        for invoice in invoices[:2]:
            if not isinstance(invoice, dict):
                continue
            lines.append(
                f"  {invoice.get('reference_month', '--')}: vencimento {invoice.get('due_date', '--')}, "
                f"status {invoice.get('status', '--')}, valor {invoice.get('amount_due', '--')}"
            )
        next_step = str(summary.get("next_step") or "").strip()
        if next_step:
            lines.append(f"  Proximo passo: {next_step}")
    if total_overdue > 0:
        lines.append("Proximo passo: priorizar as faturas vencidas e regularizar o financeiro antes de um atendimento mais sensivel.")
    elif total_open > 0:
        lines.append("Proximo passo: acompanhar os vencimentos mais proximos e manter os comprovantes em dia.")
    return "\n".join(lines)


def compose_family_next_due_answer(
    summaries: list[dict[str, Any]],
    *,
    deps: ProtectedAnswerDeps,
) -> str | None:
    candidates: list[tuple[str, dict[str, Any]]] = []
    for summary in summaries:
        if not isinstance(summary, dict):
            continue
        invoices = summary.get("invoices")
        if not isinstance(invoices, list):
            continue
        pending = [
            item
            for item in invoices
            if isinstance(item, dict)
            and str(item.get("status") or "").strip().lower() in {"open", "overdue", "pending"}
        ]
        if not pending:
            continue
        pending.sort(key=lambda item: str(item.get("due_date") or "9999-99-99"))
        candidates.append((str(summary.get("student_name") or "Aluno").strip() or "Aluno", pending[0]))
    if not candidates:
        return None
    candidates.sort(
        key=lambda item: (
            str(item[1].get("status") or "").strip().lower() not in {"open", "overdue"},
            str(item[1].get("due_date") or "9999-99-99"),
            item[0].lower(),
        )
    )
    student_name, invoice = candidates[0]
    reference_month = str(invoice.get("reference_month") or "---").strip()
    due_date = str(invoice.get("due_date") or "--").strip()
    amount_due = deps.format_brl(invoice.get("amount_due"))
    status = str(invoice.get("status") or "desconhecido").strip().lower()
    status_label = {
        "open": "em aberto",
        "overdue": "vencida",
        "pending": "pendente",
        "paid": "paga",
    }.get(status, status or "desconhecido")
    return (
        "O proximo vencimento mais imediato no recorte da familia hoje "
        f"e de {student_name}, na referencia {reference_month}, com vencimento em {due_date} "
        f"e valor {amount_due}. Status atual: {status_label}."
    )


def looks_like_family_finance_aggregate_query(message: str, *, deps: ProtectedAnswerDeps) -> bool:
    normalized = deps.normalize_text(message)
    explicit_terms = {
        "meu financeiro",
        "quero ver meu financeiro",
        "quero ver o meu financeiro",
        "me mostra meu financeiro",
        "mostrar meu financeiro",
        "ver meu financeiro",
        "como esta o financeiro da familia",
        "como está o financeiro da família",
        "como estao meus pagamentos",
        "como estão meus pagamentos",
        "meus pagamentos",
        "meus boletos",
        "situacao financeira da familia",
        "situação financeira da família",
        "situacao financeira atual da familia",
        "situação financeira atual da família",
        "resuma a situacao financeira",
        "resuma a situação financeira",
        "resumo financeiro da familia",
        "resumo financeiro da família",
        "financeiro da familia",
        "financeiro da familia hoje",
        "financeiro da família",
        "financeiro da família hoje",
        "quadro financeiro da familia",
        "quadro financeiro da família",
        "vencimentos e proximos passos",
        "vencimentos e próximos passos",
        "contas vinculadas",
        "minha situacao financeira",
        "minha situação financeira",
        "situacao financeira como se eu fosse leigo",
        "situação financeira como se eu fosse leigo",
        "separando mensalidade, taxa, atraso e desconto",
        "separando mensalidade taxa atraso e desconto",
    }
    if any(term in normalized for term in explicit_terms):
        return True
    has_family_anchor = any(
        term in normalized for term in {"familia", "família", "filhos", "responsavel", "responsável", "contas vinculadas"}
    )
    if has_family_anchor and any(
        term in normalized
        for term in {"mensalidade parcialmente paga", "negociar o restante", "o que ja aparece", "o que já aparece"}
    ):
        return True
    return has_family_anchor and any(
        term in normalized
        for term in {"financeiro", "mensalidade", "boleto", "vencimentos", "atrasos", "proximos passos", "próximos passos", "taxa", "desconto", "descontos"}
    )


def looks_like_family_academic_aggregate_query(message: str, *, deps: ProtectedAnswerDeps) -> bool:
    normalized = deps.normalize_text(message)
    explicit_terms = {
        "panorama academico",
        "panorama acadêmico",
        "quadro academico",
        "quadro acadêmico",
        "meus dois filhos",
        "meus filhos",
        "mais perto do limite de aprovacao",
        "mais perto do limite de aprovação",
        "corte de aprovacao",
        "corte de aprovação",
    }
    if any(term in normalized for term in explicit_terms):
        return True
    return any(term in normalized for term in {"familia", "família", "filhos", "responsavel", "responsável"}) and any(
        term in normalized
        for term in {"quadro academico", "quadro acadêmico", "panorama academico", "panorama acadêmico", "aprovacao", "aprovação"}
    )


def looks_like_family_attendance_aggregate_query(message: str, *, deps: ProtectedAnswerDeps) -> bool:
    normalized = deps.normalize_text(message)
    explicit_terms = {
        "resumo de frequencia dos meus dois filhos",
        "resumo de frequência dos meus dois filhos",
        "resumo de frequencia dos meus filhos",
        "resumo de frequência dos meus filhos",
        "panorama de faltas e frequencia",
        "panorama de faltas e frequência",
        "faltas e frequencia dos meus filhos",
        "faltas e frequência dos meus filhos",
        "frequencia dos meus filhos",
        "frequência dos meus filhos",
        "frequencia dos meus dois filhos",
        "frequência dos meus dois filhos",
        "frequencia dos alunos vinculados",
        "frequência dos alunos vinculados",
        "quem exige maior atencao agora",
        "quem exige maior atenção agora",
        "quem exige mais atencao agora",
        "quem exige mais atenção agora",
        "quem inspira mais atencao",
        "quem inspira mais atenção",
        "principal alerta de frequencia dos meus filhos",
        "principal alerta de frequência dos meus filhos",
    }
    if any(term in normalized for term in explicit_terms):
        return True
    has_family_anchor = any(
        term in normalized
        for term in {"meus dois filhos", "dos meus dois filhos", "meus filhos", "familia", "família", "alunos vinculados", "contas vinculadas"}
    )
    has_attendance_focus = any(
        term in normalized
        for term in {"frequencia", "frequência", "faltas", "falta", "atrasos", "presenca", "presença", "ausencias", "ausências"}
    )
    has_explicit_academic_focus = any(
        term in normalized
        for term in {
            "componente",
            "componentes",
            "disciplina",
            "disciplinas",
            "materia",
            "materias",
            "nota",
            "notas",
            "media",
            "média",
            "academico",
            "acadêmico",
        }
    )
    has_explicit_finance_focus = any(
        term in normalized
        for term in {
            "financeiro",
            "financeira",
            "situacao financeira",
            "situação financeira",
            "mensalidade",
            "mensalidades",
            "boleto",
            "boletos",
            "fatura",
            "faturas",
            "pagamento",
            "pagamentos",
            "vencimento",
            "vencimentos",
            "proximos passos",
            "próximos passos",
            "comprovantes",
        }
    )
    has_non_ambiguous_attendance_focus = any(
        term in normalized
        for term in {"frequencia", "frequência", "faltas", "falta", "presenca", "presença", "ausencias", "ausências"}
    )
    has_attention_focus = any(
        term in normalized
        for term in {
            "quem inspira mais atencao",
            "quem inspira mais atenção",
            "quem exige maior atencao",
            "quem exige maior atenção",
            "quem exige mais atencao",
            "quem exige mais atenção",
            "maior atencao",
            "maior atenção",
            "mais atencao",
            "mais atenção",
            "principal alerta",
        }
    )
    if has_explicit_academic_focus and not has_attendance_focus:
        return False
    if has_explicit_finance_focus and not has_non_ambiguous_attendance_focus:
        return False
    return has_family_anchor and (has_attendance_focus or has_attention_focus)


def compose_finance_installments_answer(summary: dict[str, Any], *, deps: ProtectedAnswerDeps) -> str:
    student_name = str(summary.get("student_name") or "Aluno").strip()
    invoices = summary.get("invoices")
    if not isinstance(invoices, list):
        invoices = []
    unpaid_statuses = {"open", "overdue", "pending"}
    unpaid = [item for item in invoices if isinstance(item, dict) and str(item.get("status") or "").strip().lower() in unpaid_statuses]
    overdue = [item for item in unpaid if str(item.get("status") or "").strip().lower() == "overdue"]
    if not unpaid:
        return f"No recorte atual, nao encontrei parcelas em aberto ou vencidas para {student_name}."
    next_invoice = sorted(unpaid, key=lambda item: str(item.get("due_date") or "9999-99-99"))[0]
    next_due_date = str(next_invoice.get("due_date") or "--").strip()
    next_amount = deps.format_brl(next_invoice.get("amount_due"))
    total_unpaid = len(unpaid)
    overdue_count = len(overdue)
    message = f"No recorte atual, {student_name} tem {total_unpaid} parcela(s) em aberto."
    if overdue_count:
        message += f" Destas, {overdue_count} esta(o) vencida(s)."
    message += f" A proxima referencia deste recorte vence em {next_due_date} no valor de {next_amount}."
    return message


def build_third_party_student_data_denial() -> SupervisorAnswerPayload:
    return SupervisorAnswerPayload(
        message_text=(
            "Nao posso expor notas, faltas, financeiro ou documentacao de um aluno que nao esteja vinculado a esta conta. "
            "Se voce for o responsavel autorizado, vincule a conta correta ou informe um aluno vinculado desta sessao."
        ),
        mode="deny",
        classification=MessageIntentClassification(
            domain="academic",
            access_tier="authenticated",
            confidence=1.0,
            reason="specialist_supervisor_third_party_student_data_denied",
        ),
        graph_path=["specialist_supervisor", "guardrail", "third_party_student_data"],
        risk_flags=["privacy_guardrail"],
        reason="specialist_supervisor_third_party_student_data_denied",
    )
