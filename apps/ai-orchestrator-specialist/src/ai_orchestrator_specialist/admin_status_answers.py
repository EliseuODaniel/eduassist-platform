from __future__ import annotations

from typing import Any


def _compose_admin_status_answer(summary: dict[str, Any]) -> str:
    student_name = str(summary.get("student_name") or "Aluno").strip()
    overall_status = str(summary.get("overall_status") or "").strip().lower()
    checklist = summary.get("checklist")
    pending_note = ""
    if isinstance(checklist, list):
        for item in checklist:
            if not isinstance(item, dict):
                continue
            if str(item.get("status") or "").strip().lower() == "pending":
                pending_note = str(item.get("notes") or "").strip()
                break
    next_step = str(summary.get("next_step") or "").strip()
    if overall_status == "pending":
        lines = [f"Hoje {student_name} ainda tem pendencias na documentacao."]
        if pending_note:
            lines.append(pending_note)
        if next_step:
            lines.append(next_step)
        return " ".join(lines)
    return f"Hoje a documentacao de {student_name} aparece como {overall_status or 'regular'}."


def _compose_actor_admin_status_answer(summary: dict[str, Any]) -> str:
    status_labels = {
        "complete": "regular",
        "completed": "regular",
        "pending": "com pendencias",
        "review": "em revisao",
        "incomplete": "incompleto",
        "missing": "com pendencias",
    }
    overall_status = status_labels.get(str(summary.get("overall_status") or "").strip().lower(), "em analise")
    lines = [f"Situacao administrativa do seu cadastro hoje: {overall_status}."]
    checklist = summary.get("checklist")
    if isinstance(checklist, list):
        lines.append("Situacao documental do seu cadastro hoje:")
        for item in checklist:
            if not isinstance(item, dict):
                continue
            label = str(item.get("label") or "Item").strip() or "Item"
            raw_status = str(item.get("status") or "").strip().lower()
            status = status_labels.get(raw_status, raw_status or "em analise")
            notes = str(item.get("notes") or "").strip()
            line = f"- {label}: {status}"
            if notes:
                line += f". {notes}"
            lines.append(line)
    next_step = str(summary.get("next_step") or "").strip()
    if next_step:
        lines.append(f"Proximo passo: {next_step}")
    return "\n".join(lines)
