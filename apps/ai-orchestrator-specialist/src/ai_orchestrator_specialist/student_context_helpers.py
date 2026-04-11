from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Awaitable, Callable

from .models import OperationalMemory

_SUBJECT_ALIASES = {
    "fisica",
    "física",
    "matematica",
    "matemática",
    "portugues",
    "português",
    "quimica",
    "química",
    "biologia",
    "historia",
    "história",
    "geografia",
    "ingles",
    "inglês",
    "english",
    "lingua inglesa",
    "língua inglesa",
    "educacao fisica",
    "educação física",
    "projeto de vida",
}

_UNKNOWN_STUDENT_STOPWORDS = {
    "nota",
    "notas",
    "media",
    "média",
    "prova",
    "provas",
    "avaliacao",
    "avaliação",
    "avaliacoes",
    "avaliações",
    "entrega",
    "entregas",
    "frequencia",
    "frequência",
    "financeiro",
    "mensalidade",
    "mensalidades",
    "pagamento",
    "pagamentos",
    "taxa",
    "taxas",
    "desconto",
    "descontos",
    "atraso",
    "atrasos",
    "restante",
    "fatura",
    "faturas",
    "boleto",
    "boletos",
    "historia",
    "história",
    "matematica",
    "matemática",
    "fisica",
    "física",
    "geografia",
    "ingles",
    "inglês",
    "english",
    "serve",
    "como",
    "esta",
    "está",
    "esta?",
    "está?",
    "dele",
    "dela",
    "ele",
    "ela",
    "aluno",
    "aluna",
    "estudante",
    "disciplina",
    "disciplinas",
    "olhando",
    "registradas",
    "registrados",
    "registrada",
    "registrado",
}


@dataclass(frozen=True)
class StudentContextDeps:
    normalize_text: Callable[[str | None], str]
    linked_students: Callable[..., list[dict[str, Any]]]
    http_get: Callable[..., Awaitable[dict[str, Any] | None]]


_FOCUS_MARKERS = (
    "so para o",
    "so para a",
    "só para o",
    "só para a",
    "corta so para o",
    "corta so para a",
    "corta só para o",
    "corta só para a",
    "fique so com o",
    "fique so com a",
    "fique só com o",
    "fique só com a",
)


def student_from_memory(
    actor: dict[str, Any] | None,
    memory: OperationalMemory | None,
    *,
    capability: str,
    deps: StudentContextDeps,
) -> dict[str, Any] | None:
    if memory is None:
        return None
    student_id = str(memory.active_student_id or "").strip()
    student_name = deps.normalize_text(memory.active_student_name)
    for student in deps.linked_students(actor, capability=capability):
        if student_id and str(student.get("student_id") or "").strip() == student_id:
            return student
        full_name = deps.normalize_text(student.get("full_name"))
        if student_name and student_name == full_name:
            return student
    return None


def other_linked_student(
    actor: dict[str, Any] | None,
    *,
    capability: str,
    current_student_id: str | None,
    deps: StudentContextDeps,
) -> dict[str, Any] | None:
    students = deps.linked_students(actor, capability=capability)
    if len(students) < 2:
        return None
    for student in students:
        if str(student.get("student_id") or "").strip() != str(current_student_id or "").strip():
            return student
    return None


def looks_like_other_student_followup(message: str, *, deps: StudentContextDeps) -> bool:
    normalized = deps.normalize_text(message)
    return any(
        term in normalized
        for term in {
            "outro aluno",
            "outra aluna",
            "outro estudante",
            "e do outro",
            "e da outra",
        }
    )


def recent_student_from_context_with_memory(
    actor: dict[str, Any] | None,
    conversation_context: dict[str, Any] | None,
    *,
    operational_memory: OperationalMemory | None,
    capability: str = "academic",
    deps: StudentContextDeps,
) -> dict[str, Any] | None:
    students = deps.linked_students(actor, capability=capability)
    if len(students) <= 1:
        return students[0] if students else None
    memory_student = student_from_memory(actor, operational_memory, capability=capability, deps=deps)
    if isinstance(memory_student, dict):
        return memory_student
    haystack = " ".join(
        str(item.get("content", ""))
        for item in (conversation_context or {}).get("recent_messages", [])
        if isinstance(item, dict)
    )
    normalized_haystack = deps.normalize_text(haystack)
    for student in students:
        full_name = deps.normalize_text(student.get("full_name"))
        first_name = full_name.split(" ")[0] if full_name else ""
        if full_name and full_name in normalized_haystack:
            return student
        if first_name and re.search(rf"\b{re.escape(first_name)}\b", normalized_haystack):
            return student
    return None


def _focus_marked_student_from_message(
    actor: dict[str, Any] | None,
    message: str,
    *,
    deps: StudentContextDeps,
) -> str | None:
    normalized_message = deps.normalize_text(message)
    if not normalized_message:
        return None
    for student in deps.linked_students(actor, capability="academic"):
        rendered_name = str(student.get("full_name") or "").strip()
        full_name = deps.normalize_text(rendered_name)
        first_name = full_name.split(" ")[0] if full_name else ""
        candidate_names = tuple(
            candidate
            for candidate in (full_name, first_name)
            if candidate
        )
        for marker in _FOCUS_MARKERS:
            marker_pattern = re.escape(deps.normalize_text(marker).strip()).replace(r"\ ", r"\s+")
            for candidate in candidate_names:
                candidate_pattern = re.escape(candidate).replace(r"\ ", r"\s+")
                if re.search(rf"{marker_pattern}\s+{candidate_pattern}\b", normalized_message):
                    return rendered_name or None
    return None


def student_hint_from_message(
    actor: dict[str, Any] | None,
    message: str,
    *,
    deps: StudentContextDeps,
) -> str | None:
    focus_marked = _focus_marked_student_from_message(actor, message, deps=deps)
    if focus_marked:
        return focus_marked
    normalized_message = deps.normalize_text(message)
    for student in deps.linked_students(actor, capability="academic"):
        full_name = deps.normalize_text(student.get("full_name"))
        first_name = full_name.split(" ")[0] if full_name else ""
        if full_name and full_name in normalized_message:
            return str(student.get("full_name") or "").strip() or None
        if first_name and re.search(rf"\b{re.escape(first_name)}\b", normalized_message):
            return str(student.get("full_name") or "").strip() or None
    return None


def unknown_explicit_student_reference(
    actor: dict[str, Any] | None,
    message: str,
    *,
    deps: StudentContextDeps,
) -> str | None:
    normalized_message = deps.normalize_text(message)
    if not normalized_message or not any(
        term in normalized_message
        for term in {
            "nota",
            "notas",
            "media",
            "média",
            "prova",
            "provas",
            "avaliac",
            "frequ",
            "fatura",
            "boleto",
            "financeiro",
            "mensalidade",
            "pagamento",
            "pagamentos",
            "negociar",
            "negociacao",
            "negociação",
        }
    ):
        return None
    academic_students = deps.linked_students(actor, capability="academic")
    finance_students = deps.linked_students(actor, capability="finance")
    if not academic_students and not finance_students:
        return None
    if re.search(r"\b(?:notas?|provas?|avaliacoes?|avaliações|aulas?)\s+de\b", normalized_message):
        return None

    known_names = {
        deps.normalize_text(student.get("full_name"))
        for student in academic_students + finance_students
        if isinstance(student, dict)
    }
    known_first_names = {name.split(" ")[0] for name in known_names if name}
    patterns = (
        r"\b(?:da|do|de|para|pro|pra)\s+([a-z]{3,}(?:\s+[a-z]{3,})?)\b",
        r"\b(?:aluno|aluna|estudante)\s+([a-z]{3,}(?:\s+[a-z]{3,})?)\b",
    )
    for pattern in patterns:
        for match in re.finditer(pattern, normalized_message):
            candidate = deps.normalize_text(match.group(1))
            if not candidate:
                continue
            if candidate in known_names or candidate in known_first_names:
                continue
            if candidate in _UNKNOWN_STUDENT_STOPWORDS or candidate in _SUBJECT_ALIASES:
                continue
            if any(candidate.startswith(stopword) for stopword in _UNKNOWN_STUDENT_STOPWORDS):
                continue
            return candidate
    return None


def resolve_student(
    actor: dict[str, Any] | None,
    *,
    capability: str,
    student_name_hint: str | None,
    conversation_context: dict[str, Any] | None,
    operational_memory: OperationalMemory | None,
    current_message: str | None,
    deps: StudentContextDeps,
) -> dict[str, Any] | None:
    students = deps.linked_students(actor, capability=capability)
    if not students:
        return None
    if len(students) == 1 and not student_name_hint:
        return students[0]
    if current_message and looks_like_other_student_followup(current_message, deps=deps):
        current_student = student_from_memory(actor, operational_memory, capability=capability, deps=deps)
        return other_linked_student(
            actor,
            capability=capability,
            current_student_id=str(current_student.get("student_id") or "") if isinstance(current_student, dict) else None,
            deps=deps,
        )
    normalized_hint = deps.normalize_text(student_name_hint)
    if normalized_hint:
        for student in students:
            full_name = deps.normalize_text(student.get("full_name"))
            first_name = full_name.split(" ")[0] if full_name else ""
            if normalized_hint == full_name or normalized_hint == first_name:
                return student
            if normalized_hint and normalized_hint in full_name:
                return student
    return recent_student_from_context_with_memory(
        actor,
        conversation_context,
        operational_memory=operational_memory,
        capability=capability,
        deps=deps,
    )


def subject_code_from_hint(
    summary: dict[str, Any],
    subject_hint: str | None,
    *,
    deps: StudentContextDeps,
) -> tuple[str | None, str | None]:
    normalized_hint = deps.normalize_text(subject_hint)
    if not normalized_hint:
        return None, None
    grades = summary.get("grades")
    if not isinstance(grades, list):
        return None, None
    exact_matches: list[tuple[str | None, str | None]] = []
    prefix_matches: list[tuple[str | None, str | None]] = []
    for item in grades:
        if not isinstance(item, dict):
            continue
        subject_name = str(item.get("subject_name", "")).strip()
        subject_code = str(item.get("subject_code", "")).strip()
        normalized_name = deps.normalize_text(subject_name)
        if normalized_hint == normalized_name or normalized_hint == deps.normalize_text(subject_code):
            exact_matches.append((subject_code or None, subject_name or None))
            continue
        if normalized_name.startswith(f"{normalized_hint} "):
            prefix_matches.append((subject_code or None, subject_name or None))
            continue
        if " " in normalized_hint and normalized_hint in normalized_name:
            prefix_matches.append((subject_code or None, subject_name or None))
    if exact_matches:
        return exact_matches[0]
    if len(prefix_matches) == 1:
        return prefix_matches[0]
    return None, None


def subject_hint_from_text(message: str, *, deps: StudentContextDeps) -> str | None:
    normalized = deps.normalize_text(message)
    subject_aliases = {
        "fisica": "Fisica",
        "física": "Fisica",
        "matematica": "Matematica",
        "matemática": "Matematica",
        "portugues": "Lingua Portuguesa",
        "português": "Lingua Portuguesa",
        "quimica": "Quimica",
        "química": "Quimica",
        "biologia": "Biologia",
        "historia": "Historia",
        "história": "Historia",
        "geografia": "Geografia",
        "ingles": "Lingua Inglesa",
        "inglesa": "Lingua Inglesa",
        "inglês": "Lingua Inglesa",
        "english": "Lingua Inglesa",
        "educacao fisica": "Educacao Fisica",
        "educação física": "Educacao Fisica",
        "projeto de vida": "Projeto de vida",
        "danca": "Danca",
        "dança": "Danca",
    }
    for alias, canonical in sorted(subject_aliases.items(), key=lambda item: len(item[0]), reverse=True):
        if alias in normalized:
            if re.search(rf"\b(?:nao e|não é|nao eh|não eh)\s+{re.escape(alias)}\b", normalized):
                continue
            return canonical
    return None


def recent_subject_from_context(
    summary: dict[str, Any],
    conversation_context: dict[str, Any] | None,
    *,
    operational_memory: OperationalMemory | None = None,
    deps: StudentContextDeps,
) -> str | None:
    grades = summary.get("grades")
    if not isinstance(grades, list):
        return None
    memory_subject = deps.normalize_text((operational_memory.active_subject if operational_memory else None))
    if memory_subject:
        for item in grades:
            if not isinstance(item, dict):
                continue
            subject_name = str(item.get("subject_name") or "").strip()
            if memory_subject == deps.normalize_text(subject_name):
                return subject_name
    haystack_items = (conversation_context or {}).get("recent_messages")
    if not isinstance(haystack_items, list):
        return None
    haystack = " ".join(str(item.get("content") or "") for item in haystack_items if isinstance(item, dict))
    normalized_haystack = deps.normalize_text(haystack)
    for item in grades:
        if not isinstance(item, dict):
            continue
        subject_name = str(item.get("subject_name") or "").strip()
        normalized_name = deps.normalize_text(subject_name)
        if normalized_name and normalized_name in normalized_haystack:
            return subject_name
    return None


async def fetch_academic_summary_payload(
    ctx: Any,
    *,
    student_name_hint: str | None = None,
    deps: StudentContextDeps,
) -> dict[str, Any]:
    student = resolve_student(
        ctx.actor,
        capability="academic",
        student_name_hint=student_name_hint,
        conversation_context=ctx.conversation_context,
        operational_memory=ctx.operational_memory,
        current_message=ctx.request.message,
        deps=deps,
    )
    if not isinstance(student, dict):
        return {"error": "student_not_found", "linked_students": deps.linked_students(ctx.actor, capability="academic")}
    payload = await deps.http_get(
        ctx.http_client,
        base_url=ctx.settings.api_core_url,
        path=f"/v1/students/{student['student_id']}/academic-summary",
        token=ctx.settings.internal_api_token,
        params={"telegram_chat_id": ctx.request.telegram_chat_id},
    )
    return {
        "student": student,
        "summary": payload.get("summary") if isinstance(payload, dict) else None,
        "decision": payload.get("decision") if isinstance(payload, dict) else None,
    }


async def fetch_financial_summary_payload(
    ctx: Any,
    *,
    student_name_hint: str | None = None,
    deps: StudentContextDeps,
) -> dict[str, Any]:
    student = resolve_student(
        ctx.actor,
        capability="finance",
        student_name_hint=student_name_hint,
        conversation_context=ctx.conversation_context,
        operational_memory=ctx.operational_memory,
        current_message=ctx.request.message,
        deps=deps,
    )
    if not isinstance(student, dict):
        return {"error": "student_not_found", "linked_students": deps.linked_students(ctx.actor, capability="finance")}
    payload = await deps.http_get(
        ctx.http_client,
        base_url=ctx.settings.api_core_url,
        path=f"/v1/students/{student['student_id']}/financial-summary",
        token=ctx.settings.internal_api_token,
        params={"telegram_chat_id": ctx.request.telegram_chat_id},
    )
    return {
        "student": student,
        "summary": payload.get("summary") if isinstance(payload, dict) else None,
        "decision": payload.get("decision") if isinstance(payload, dict) else None,
    }
