from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any

from .context_budget import (
    ContextBudgetSnapshot,
    build_context_section_budget,
    estimate_text_tokens,
    pack_context_items,
    record_context_budget,
)
from .grounded_public_answer import (
    _google_text_call,
    _openai_text_call,
    _resolve_provider,
)
from .runtime import _extract_json_object


_PROJECT_CONTEXT = (
    "Contexto do projeto EduAssist: voce atua no acabamento final de respostas de um assistente escolar "
    "seguro, auditavel e grounded. O sistema pode produzir respostas deterministicas, mas a superficie final "
    "deve soar humana, personalizada e fiel a pergunta do usuario."
)

_SUBJECT_NAMES = (
    "matematica",
    "matemática",
    "portugues",
    "português",
    "lingua portuguesa",
    "língua portuguesa",
    "fisica",
    "física",
    "quimica",
    "química",
    "biologia",
    "historia",
    "história",
    "geografia",
    "educacao fisica",
    "educação física",
)

_QUESTION_FINANCE_HINTS = (
    "financeir",
    "fatura",
    "boleto",
    "mensalidade",
    "venc",
    "pagamento",
    "desconto",
    "taxa",
    "parcela",
)

_QUESTION_ATTENDANCE_HINTS = (
    "frequ",
    "falta",
    "atras",
    "presen",
    "ausen",
)

_QUESTION_TIME_HINTS = (
    "que horas",
    "horario",
    "horário",
    "abre",
    "fecha",
    "ate que horas",
    "até que horas",
)

_QUESTION_DATE_HINTS = (
    "quando",
    "data",
    "cronograma",
    "vence",
    "vencimento",
    "dia",
    "agenda",
)

_LIMITATION_TERMS = (
    "nao tenho base",
    "não tenho base",
    "fora do escopo",
    "nao consigo",
    "não consigo",
    "nao posso",
    "não posso",
    "nao encontrei",
    "não encontrei",
    "preciso que voce",
    "preciso que você",
)

_TIME_RE = re.compile(r"\b\d{1,2}h\d{2}\b", flags=re.IGNORECASE)
_DATE_RE = re.compile(
    r"\b\d{1,2}/\d{1,2}(?:/\d{2,4})?\b|\b\d{4}-\d{2}-\d{2}\b|\b\d{1,2}\s+de\s+[a-zç]+\s+de\s+\d{4}\b",
    flags=re.IGNORECASE,
)
_MONEY_RE = re.compile(r"R\$\s?\d[\d\.\,]*|\b\d+[.,]\d{2}\b", flags=re.IGNORECASE)
_PROTOCOL_RE = re.compile(r"\b[A-Z]{2,6}-\d{6,}-[A-Z0-9]{4,}\b", flags=re.IGNORECASE)


@dataclass(frozen=True)
class AnswerSurfaceRefinementResult:
    answer_text: str
    used_llm: bool
    changed: bool
    preserved_fallback: bool
    reason: str


def _normalize_text(value: str | None) -> str:
    return " ".join(str(value or "").strip().split()).casefold()


def _plain_text(value: str | None) -> str:
    return _normalize_text(value)


def _looks_like_limitation_text(text: str) -> bool:
    normalized = _plain_text(text)
    return any(term in normalized for term in _LIMITATION_TERMS)


def _specialist_refiner_history_budget_tokens(settings: Any) -> int:
    return max(64, int(getattr(settings, "grounded_public_history_budget_tokens", 180) or 180))


def _specialist_refiner_evidence_budget_tokens(settings: Any) -> int:
    return max(96, int(getattr(settings, "grounded_public_evidence_budget_tokens", 320) or 320))


def _recent_message_lines(conversation_context: dict[str, Any] | None) -> list[str]:
    lines: list[str] = []
    if isinstance(conversation_context, dict):
        for item in conversation_context.get("recent_messages") or []:
            if not isinstance(item, dict):
                continue
            sender = str(item.get("sender_type", "desconhecido")).strip()
            content = str(item.get("content", "")).strip()
            if content:
                lines.append(f"- {sender}: {content}")
    return lines


def _extract_requested_subject(question: str, original_text: str, active_subject: str | None) -> str | None:
    active = _plain_text(active_subject)
    if active:
        return active
    combined = f"{_plain_text(question)} {_plain_text(original_text)}"
    for subject in _SUBJECT_NAMES:
        if subject in combined:
            return subject
    return None


def _requested_focus_targets(
    request_message: str,
    original_text: str,
    target_names: list[str] | None,
) -> list[str]:
    combined = f"{_plain_text(request_message)} {_plain_text(original_text)}"
    targets: list[str] = []
    for item in target_names or []:
        cleaned = str(item or "").strip()
        if not cleaned:
            continue
        first_name = _plain_text(cleaned).split(" ")[0]
        if first_name and first_name in combined:
            targets.append(cleaned)
            continue
        normalized_full = _plain_text(cleaned)
        if normalized_full and normalized_full in combined:
            targets.append(cleaned)
    deduped: list[str] = []
    seen: set[str] = set()
    for item in targets:
        key = _plain_text(item)
        if key in seen:
            continue
        seen.add(key)
        deduped.append(item)
    return deduped


def _refiner_prompt_sections(
    *,
    settings: Any,
    stack_label: str,
    request_message: str,
    original_text: str,
    answer_mode: str,
    answer_reason: str,
    domain: str,
    access_tier: str,
    evidence_lines: list[str],
    conversation_context: dict[str, Any] | None,
    target_names: list[str] | None,
    active_subject: str | None,
) -> tuple[str, str, Any, Any]:
    history_budget = pack_context_items(
        _recent_message_lines(conversation_context),
        token_budget=_specialist_refiner_history_budget_tokens(settings),
        empty_text="- nenhum",
        keep_last=True,
    )
    evidence_budget = pack_context_items(
        [f"- {line}" for line in evidence_lines if str(line).strip()],
        token_budget=_specialist_refiner_evidence_budget_tokens(settings),
        empty_text="- nenhuma evidencia",
    )
    instructions = (
        f"Voce e o answer surface refiner do caminho {stack_label} no EduAssist. "
        f"{_PROJECT_CONTEXT} "
        "Sua tarefa e refinar a superficie final da resposta, deixando-a mais natural e personalizada para a pergunta atual, "
        "sem mudar o sentido, o escopo, a seguranca ou os fatos do rascunho original. "
        "Nunca invente fatos, datas, horarios, valores, nomes, protocolos, setores, notas ou orientacoes. "
        "Se o rascunho original ja estiver bom, mantenha-o. "
        "Se o modo original for clarify, mantenha a resposta como pedido de esclarecimento. "
        "Se o modo original for deny, boundary ou auth guidance, preserve explicitamente o limite e o proximo passo seguro. "
        "Se a resposta mencionar aluno, disciplina, horario, data, valor, vencimento ou canal oficial, preserve esses elementos. "
        "Se houver recorte explicito na pergunta, responda no mesmo recorte e nao abra o escopo. "
        "Prefira portugues do Brasil, tom humano, claro e direto. "
        "Nao acrescente perguntas de continuidade, convites genericos ou call-to-action desnecessario se a resposta original ja resolver a pergunta. "
        "Evite cara de template, mas nao troque dados concretos por texto vago. "
        "Devolva somente JSON valido com as chaves: answer_text, preserve_original, enough_evidence, style_mode. "
        "answer_text deve conter apenas a mensagem final ao usuario. "
        "preserve_original deve ser true quando a resposta original ja for a melhor opcao segura. "
        "enough_evidence deve ser true quando a evidencia sustenta o texto final. "
        "style_mode pode ser concise, empathetic, clarify, boundary, protected ou public."
    )
    prompt = (
        f"Pergunta do usuario:\n{request_message}\n\n"
        f"Modo original:\n{answer_mode}\n\n"
        f"Dominio e acesso:\n{json.dumps({'domain': domain, 'access_tier': access_tier, 'reason': answer_reason}, ensure_ascii=False)}\n\n"
        f"Alvos ativos:\n{json.dumps({'target_names': target_names or [], 'active_subject': active_subject}, ensure_ascii=False)}\n\n"
        f"Historico recente:\n{history_budget.rendered_text}\n\n"
        f"Evidencias:\n{evidence_budget.rendered_text}\n\n"
        f"Resposta original:\n{original_text}"
    )
    return instructions, prompt, history_budget, evidence_budget


def _refiner_fallback_prompt(
    *,
    request_message: str,
    original_text: str,
    answer_mode: str,
    answer_reason: str,
    domain: str,
    access_tier: str,
    evidence_lines: list[str],
    conversation_context: dict[str, Any] | None,
    target_names: list[str] | None,
    active_subject: str | None,
    settings: Any,
) -> tuple[str, str, Any, Any]:
    history_budget = pack_context_items(
        _recent_message_lines(conversation_context),
        token_budget=_specialist_refiner_history_budget_tokens(settings),
        empty_text="- nenhum",
        keep_last=True,
    )
    evidence_budget = pack_context_items(
        [f"- {line}" for line in evidence_lines if str(line).strip()],
        token_budget=_specialist_refiner_evidence_budget_tokens(settings),
        empty_text="- nenhuma evidencia",
    )
    instructions = (
        f"{_PROJECT_CONTEXT} "
        "Voce e a ultima etapa de acabamento de uma resposta escolar segura. "
        "Refine apenas a forma da resposta final para ficar mais natural, personalizada e alinhada a pergunta. "
        "Nao invente fatos. Nao mude nomes, horarios, datas, valores, notas, protocolos, canais ou limites de acesso. "
        "Se a pergunta pedir resumo academico, deixe isso explicito. "
        "Se a pergunta pedir horario, deixe isso explicito. "
        "Nao acrescente pergunta de continuidade se a resposta original ja resolver o pedido. "
        "Se a melhor opcao for manter o texto original, devolva o proprio texto original. "
        "Devolva apenas a resposta final ao usuario, sem JSON, sem comentarios extras e sem markdown."
    )
    prompt = (
        f"Pergunta do usuario:\n{request_message}\n\n"
        f"Modo e contexto:\n{json.dumps({'mode': answer_mode, 'reason': answer_reason, 'domain': domain, 'access_tier': access_tier}, ensure_ascii=False)}\n\n"
        f"Alvos ativos:\n{json.dumps({'target_names': target_names or [], 'active_subject': active_subject}, ensure_ascii=False)}\n\n"
        f"Historico recente:\n{history_budget.rendered_text}\n\n"
        f"Evidencias:\n{evidence_budget.rendered_text}\n\n"
        f"Resposta original:\n{original_text}"
    )
    return instructions, prompt, history_budget, evidence_budget


def _record_answer_refiner_context_budget(
    *,
    stack_label: str,
    request_message: str,
    original_text: str,
    instructions: str,
    prompt: str,
    history_budget: Any,
    evidence_budget: Any,
) -> None:
    snapshot = ContextBudgetSnapshot(
        pipeline="answer_surface_refiner",
        stack_label=stack_label,
        estimated_prompt_tokens=estimate_text_tokens(prompt),
        estimated_instruction_tokens=estimate_text_tokens(instructions),
        estimated_request_tokens=estimate_text_tokens(request_message),
        estimated_draft_tokens=estimate_text_tokens(original_text),
        history=build_context_section_budget(
            rendered_text=history_budget.rendered_text,
            total_items=history_budget.total_items,
            used_items=history_budget.used_items,
        ),
        evidence=build_context_section_budget(
            rendered_text=evidence_budget.rendered_text,
            total_items=evidence_budget.total_items,
            used_items=evidence_budget.used_items,
        ),
    )
    record_context_budget(snapshot)


def _answer_text_from_model_output(raw_text: str | None) -> dict[str, Any] | None:
    cleaned = str(raw_text or "").strip()
    if not cleaned:
        return None
    payload = _extract_json_object(cleaned)
    if isinstance(payload, dict):
        return payload
    return {"answer_text": cleaned, "preserve_original": False, "enough_evidence": False, "style_mode": "fallback"}


def _question_requests_time(question: str) -> bool:
    normalized = _plain_text(question)
    return any(term in normalized for term in _QUESTION_TIME_HINTS)


def _question_requests_date(question: str) -> bool:
    normalized = _plain_text(question)
    return any(term in normalized for term in _QUESTION_DATE_HINTS)


def _question_requests_finance(question: str, original_text: str) -> bool:
    normalized = f"{_plain_text(question)} {_plain_text(original_text)}"
    return any(term in normalized for term in _QUESTION_FINANCE_HINTS)


def _question_requests_attendance(question: str, original_text: str) -> bool:
    normalized = f"{_plain_text(question)} {_plain_text(original_text)}"
    return any(term in normalized for term in _QUESTION_ATTENDANCE_HINTS)


def _question_requests_academic_summary(question: str, original_text: str) -> bool:
    normalized = f"{_plain_text(question)} {_plain_text(original_text)}"
    return (
        "academ" in normalized
        and any(term in normalized for term in ("resumo", "panorama", "notas", "desempenho"))
    )


def _question_requests_schedule_label(question: str, original_text: str, answer_reason: str) -> bool:
    normalized = f"{_plain_text(question)} {_plain_text(original_text)}"
    return "teacher_schedule" in _plain_text(answer_reason) or any(
        term in normalized for term in ("horario", "horário", "agenda", "grade docente", "grade de hoje")
    )


def _validate_refined_answer_text(
    *,
    request_message: str,
    original_text: str,
    candidate_text: str,
    answer_mode: str,
    answer_reason: str,
    access_tier: str,
    target_names: list[str] | None,
    active_subject: str | None,
) -> str | None:
    candidate = str(candidate_text or "").strip()
    if not candidate:
        return None
    original = str(original_text or "").strip()
    question_plain = _plain_text(request_message)
    original_plain = _plain_text(original)
    candidate_plain = _plain_text(candidate)
    if not candidate_plain:
        return None
    if len(candidate) > max(int(len(original or candidate) * 2.0), len(original) + 220):
        return None
    if answer_mode == "clarify" and not (
        "?" in candidate
        or any(term in candidate_plain for term in ("voce quer", "você quer", "me diga", "confirme", "qual "))
    ):
        return None
    if answer_mode != "clarify" and "como posso te ajudar" in candidate_plain and "como posso te ajudar" not in original_plain:
        return None
    if any(token in answer_reason for token in ("assistant_identity", "capabilities")) and "?" in candidate and "?" not in original:
        return None
    if any(token in answer_reason for token in ("assistant_identity", "capabilities")):
        if candidate_plain.startswith("ola") and not original_plain.startswith("ola"):
            return None
        if candidate.count("!") > original.count("!"):
            return None
    if answer_mode == "deny" and not any(
        term in candidate_plain for term in ("nao posso", "não posso", "nao consigo", "não consigo", "nao tenho base", "não tenho base")
    ):
        return None
    if "scope_boundary" in answer_reason and not any(
        term in candidate_plain for term in ("fora do escopo", "nao tenho base", "não tenho base", "consigo ajudar com")
    ):
        return None
    if "auth_guidance" in answer_reason and not any(
        term in candidate_plain for term in ("portal", "codigo", "código", "/start", "vincul")
    ):
        return None

    requested_subject = _extract_requested_subject(request_message, original_text, active_subject)
    if requested_subject and requested_subject in f"{question_plain} {original_plain}" and requested_subject not in candidate_plain:
        if not _looks_like_limitation_text(candidate):
            return None
    requested_targets = _requested_focus_targets(request_message, original_text, target_names)
    if access_tier != "public":
        for target in requested_targets[:2]:
            first_name = _plain_text(target).split(" ")[0]
            if first_name and first_name not in candidate_plain and not _looks_like_limitation_text(candidate):
                if answer_mode != "clarify":
                    return None
    if _TIME_RE.search(original) and _question_requests_time(request_message):
        if not _TIME_RE.search(candidate) and not _looks_like_limitation_text(candidate):
            return None
    if _DATE_RE.search(original) and _question_requests_date(request_message):
        if not _DATE_RE.search(candidate) and not _looks_like_limitation_text(candidate):
            return None
    if _MONEY_RE.search(original) and _question_requests_finance(request_message, original_text):
        if not _MONEY_RE.search(candidate) and not _looks_like_limitation_text(candidate):
            return None
    if _PROTOCOL_RE.search(original):
        if not _PROTOCOL_RE.search(candidate) and not _looks_like_limitation_text(candidate):
            return None
    if _question_requests_attendance(request_message, original_text):
        if "frequ" not in candidate_plain and "falta" not in candidate_plain and "atras" not in candidate_plain:
            if not _looks_like_limitation_text(candidate):
                return None
    if _question_requests_academic_summary(request_message, original_text):
        if "acad" not in candidate_plain and "resumo" not in candidate_plain:
            if not _looks_like_limitation_text(candidate):
                return None
    if _question_requests_schedule_label(request_message, original_text, answer_reason):
        if "hor" not in candidate_plain and "agenda" not in candidate_plain and "grade" not in candidate_plain:
            if not _looks_like_limitation_text(candidate):
                return None
    if _question_requests_finance(request_message, original_text):
        if any(subject in candidate_plain for subject in _SUBJECT_NAMES):
            return None
    if _question_requests_attendance(request_message, original_text) and any(
        signal in candidate_plain for signal in ("nota", "media", "média")
    ):
        return None
    return candidate


async def _call_refiner_provider(
    *,
    provider: str,
    settings: Any,
    instructions: str,
    prompt: str,
    max_output_tokens: int,
) -> str | None:
    if provider == "openai":
        return await _openai_text_call(
            settings=settings,
            instructions=instructions,
            prompt=prompt,
            temperature=0.0,
            max_output_tokens=max_output_tokens,
            top_p=0.9,
        )
    if provider == "google":
        return await _google_text_call(
            settings=settings,
            instructions=instructions,
            prompt=prompt,
            temperature=0.0,
            max_output_tokens=max_output_tokens,
            top_p=0.9,
        )
    return None


async def refine_answer_surface_with_provider(
    *,
    settings: Any,
    stack_label: str,
    request_message: str,
    original_text: str,
    answer_mode: str,
    answer_reason: str,
    domain: str,
    access_tier: str,
    evidence_lines: list[str],
    conversation_context: dict[str, Any] | None,
    target_names: list[str] | None = None,
    active_subject: str | None = None,
) -> AnswerSurfaceRefinementResult:
    if not str(request_message or "").strip() or not str(original_text or "").strip():
        return AnswerSurfaceRefinementResult(
            answer_text=str(original_text or ""),
            used_llm=False,
            changed=False,
            preserved_fallback=False,
            reason="ineligible",
        )
    rendered_evidence = [str(line or "").strip() for line in evidence_lines if str(line or "").strip()]
    if not rendered_evidence:
        rendered_evidence = [str(original_text or "").strip()]
    instructions, prompt, history_budget, evidence_budget = _refiner_prompt_sections(
        settings=settings,
        stack_label=stack_label,
        request_message=request_message,
        original_text=original_text,
        answer_mode=answer_mode,
        answer_reason=answer_reason,
        domain=domain,
        access_tier=access_tier,
        evidence_lines=rendered_evidence,
        conversation_context=conversation_context,
        target_names=target_names,
        active_subject=active_subject,
    )
    _record_answer_refiner_context_budget(
        stack_label=stack_label,
        request_message=request_message,
        original_text=original_text,
        instructions=instructions,
        prompt=prompt,
        history_budget=history_budget,
        evidence_budget=evidence_budget,
    )
    provider = _resolve_provider(settings)
    raw_payload: dict[str, Any] | None = _answer_text_from_model_output(
        await _call_refiner_provider(
            provider=provider,
            settings=settings,
            instructions=instructions,
            prompt=prompt,
            max_output_tokens=260,
        )
    )
    if not raw_payload or not str(raw_payload.get("answer_text") or "").strip():
        fallback_instructions, fallback_prompt, _, _ = _refiner_fallback_prompt(
            request_message=request_message,
            original_text=original_text,
            answer_mode=answer_mode,
            answer_reason=answer_reason,
            domain=domain,
            access_tier=access_tier,
            evidence_lines=rendered_evidence,
            conversation_context=conversation_context,
            target_names=target_names,
            active_subject=active_subject,
            settings=settings,
        )
        fallback_text = await _call_refiner_provider(
            provider=provider,
            settings=settings,
            instructions=fallback_instructions,
            prompt=fallback_prompt,
            max_output_tokens=220,
        )
        if str(fallback_text or "").strip():
            raw_payload = {
                "answer_text": str(fallback_text).strip(),
                "preserve_original": False,
                "enough_evidence": True,
                "style_mode": "fallback_text",
            }
    if not raw_payload:
        return AnswerSurfaceRefinementResult(
            answer_text=original_text,
            used_llm=False,
            changed=False,
            preserved_fallback=False,
            reason="provider_unavailable",
        )
    if bool(raw_payload.get("preserve_original")):
        return AnswerSurfaceRefinementResult(
            answer_text=original_text,
            used_llm=True,
            changed=False,
            preserved_fallback=False,
            reason="preserve_original",
        )
    candidate_text = str(raw_payload.get("answer_text") or "").strip()
    validated = _validate_refined_answer_text(
        request_message=request_message,
        original_text=original_text,
        candidate_text=candidate_text,
        answer_mode=answer_mode,
        answer_reason=answer_reason,
        access_tier=access_tier,
        target_names=target_names,
        active_subject=active_subject,
    )
    if not validated:
        return AnswerSurfaceRefinementResult(
            answer_text=original_text,
            used_llm=True,
            changed=False,
            preserved_fallback=True,
            reason="validation_rejected",
        )
    changed = _normalize_text(validated) != _normalize_text(original_text)
    return AnswerSurfaceRefinementResult(
        answer_text=validated,
        used_llm=True,
        changed=changed,
        preserved_fallback=False,
        reason="answer_surface_refiner",
    )
