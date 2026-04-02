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


def compose_named_grade_answer(summary: dict[str, Any], *, deps: ProtectedAnswerDeps) -> str:
    student_name = str(summary.get("student_name") or "Aluno").strip()
    snapshots = subject_grade_snapshot(summary, deps=deps)
    lines = [f"Notas de {student_name}:"]
    for name, avg in snapshots:
        lines.append(f"- {name}: media parcial {str(avg).replace('.', ',')}")
    return "\n".join(lines)


def looks_like_academic_risk_followup(message: str, *, deps: ProtectedAnswerDeps) -> bool:
    normalized = deps.normalize_text(message)
    return any(
        term in normalized
        for term in {
            "maior risco",
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
        }
    )


def compose_academic_risk_answer(summary: dict[str, Any], *, deps: ProtectedAnswerDeps) -> str | None:
    student_name = str(summary.get("student_name") or "Aluno").strip()
    snapshots = subject_grade_snapshot(summary, deps=deps)
    if not snapshots:
        return None
    lines = [f"Os pontos de maior risco academico de {student_name} hoje sao:"]
    for name, avg in snapshots[:3]:
        lines.append(f"- {name}: media parcial {str(avg).replace('.', ',')}")
    lines.append("Esses componentes merecem acompanhamento primeiro no proximo ciclo de estudo.")
    return "\n".join(lines)


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
    explicit_hint = deps.student_hint_from_message(ctx.actor, ctx.request.message) or deps.is_student_name_only_followup(
        ctx.actor,
        ctx.request.message,
    )
    if explicit_hint:
        return explicit_hint
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
    lines = [
        "Resumo financeiro das contas vinculadas:",
        f"- Total de faturas em aberto: {total_open}",
        f"- Total de faturas vencidas: {total_overdue}",
    ]
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
    return "\n".join(lines)


def looks_like_family_finance_aggregate_query(message: str, *, deps: ProtectedAnswerDeps) -> bool:
    normalized = deps.normalize_text(message)
    explicit_terms = {
        "como esta o financeiro da familia",
        "como está o financeiro da família",
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
    }
    if any(term in normalized for term in explicit_terms):
        return True
    return any(term in normalized for term in {"familia", "família", "filhos", "responsavel", "responsável"}) and any(
        term in normalized
        for term in {"financeiro", "mensalidade", "boleto", "vencimentos", "atrasos", "proximos passos", "próximos passos"}
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
