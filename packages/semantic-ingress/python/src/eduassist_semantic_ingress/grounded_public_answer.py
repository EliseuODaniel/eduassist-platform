from __future__ import annotations

import json
import re
from typing import Any

import httpx
from openai import AsyncOpenAI

from .context_budget import (
    ContextBudgetSnapshot,
    build_context_section_budget,
    estimate_text_tokens,
    pack_context_items,
    record_context_budget,
)
from eduassist_observability import (
    extract_google_usage,
    extract_openai_usage,
    normalize_gen_ai_provider_name,
    start_gen_ai_client_operation,
)
from .runtime import _extract_json_object


_PROJECT_CONTEXT = (
    "Contexto do projeto EduAssist: voce atua como assistente institucional de uma escola de ensino "
    "fundamental II e ensino medio. O sistema tem foco em atendimento escolar seguro, auditavel e "
    "baseado em fontes. Perguntas publicas devem priorizar fatos canonicos, documentos institucionais "
    "e calendario oficial. Responda com base apenas nas evidencias disponiveis."
)


def _llm_model_profile(settings: Any) -> str | None:
    return str(getattr(settings, "llm_model_profile", "") or "").strip() or None


def _normalize_google_model(value: str | None) -> str:
    normalized = str(value or "").strip()
    if normalized.startswith("models/"):
        return normalized.split("/", 1)[1]
    return normalized or "gemini-2.5-flash"


def _resolve_provider(settings: Any) -> str:
    configured = str(
        getattr(settings, "answer_experience_provider", None)
        or getattr(settings, "llm_provider", "auto")
        or "auto"
    ).strip().lower()
    openai_api_key = str(
        getattr(settings, "answer_experience_openai_api_key", None)
        or getattr(settings, "openai_api_key", "")
        or ""
    ).strip()
    google_api_key = str(
        getattr(settings, "answer_experience_google_api_key", None)
        or getattr(settings, "google_api_key", "")
        or ""
    ).strip()
    if configured == "openai":
        return "openai" if openai_api_key else "unconfigured"
    if configured in {"google", "gemini", "litellm"}:
        return "google" if google_api_key else "unconfigured"
    if openai_api_key:
        return "openai"
    if google_api_key:
        return "google"
    return "unconfigured"


def _openai_api_key(settings: Any) -> str | None:
    value = getattr(settings, "answer_experience_openai_api_key", None) or getattr(
        settings, "openai_api_key", None
    )
    cleaned = str(value or "").strip()
    return cleaned or None


def _openai_base_url(settings: Any) -> str:
    value = getattr(settings, "answer_experience_openai_base_url", None) or getattr(
        settings, "openai_base_url", "https://api.openai.com/v1"
    )
    return str(value or "https://api.openai.com/v1").strip()


def _openai_model(settings: Any) -> str:
    value = getattr(settings, "answer_experience_openai_model", None) or getattr(
        settings, "openai_model", "gpt-5.4"
    )
    return str(value or "gpt-5.4").strip()


def _openai_api_mode(settings: Any) -> str:
    raw = str(
        getattr(settings, "answer_experience_openai_api_mode", None)
        or getattr(settings, "openai_api_mode", "responses")
        or "responses"
    ).strip().lower()
    if raw in {"chat", "chat_completions", "chat-completions"}:
        return "chat_completions"
    if raw == "auto":
        base_url = _openai_base_url(settings).lower()
        return "responses" if "api.openai.com" in base_url else "chat_completions"
    return "responses"


def _google_api_key(settings: Any) -> str | None:
    value = getattr(settings, "answer_experience_google_api_key", None) or getattr(
        settings, "google_api_key", None
    )
    cleaned = str(value or "").strip()
    return cleaned or None


def _google_api_base_url(settings: Any) -> str:
    value = getattr(settings, "answer_experience_google_api_base_url", None) or getattr(
        settings, "google_api_base_url", "https://generativelanguage.googleapis.com/v1beta"
    )
    return str(value or "https://generativelanguage.googleapis.com/v1beta").strip()


def _google_model(settings: Any) -> str:
    value = getattr(settings, "answer_experience_google_model", None) or getattr(
        settings, "google_model", "gemini-2.5-flash"
    )
    return _normalize_google_model(str(value or "gemini-2.5-flash"))


def _openai_message_text(message_content: Any) -> str | None:
    if isinstance(message_content, str):
        cleaned = message_content.strip()
        return cleaned or None
    if not isinstance(message_content, list):
        return None
    parts: list[str] = []
    for item in message_content:
        if isinstance(item, dict):
            if str(item.get("type") or "").strip().lower() == "text":
                text = str(item.get("text") or "").strip()
                if text:
                    parts.append(text)
            continue
        text = str(getattr(item, "text", "") or "").strip()
        if text:
            parts.append(text)
    merged = "\n".join(part for part in parts if part).strip()
    return merged or None


def _grounded_public_history_budget_tokens(settings: Any) -> int:
    return max(64, int(getattr(settings, "grounded_public_history_budget_tokens", 180) or 180))


def _grounded_public_evidence_budget_tokens(settings: Any) -> int:
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


def _school_name(school_profile: dict[str, Any] | None) -> str:
    return str((school_profile or {}).get("school_name") or "Colegio Horizonte")


def _build_sections(
    *,
    settings: Any,
    stack_label: str,
    request_message: str,
    draft_text: str,
    public_plan: dict[str, Any] | None,
    evidence_lines: list[str],
    conversation_context: dict[str, Any] | None,
    school_profile: dict[str, Any] | None,
) -> tuple[str, str, Any, Any]:
    history_budget = pack_context_items(
        _recent_message_lines(conversation_context),
        token_budget=_grounded_public_history_budget_tokens(settings),
        empty_text="- nenhum",
        keep_last=True,
    )
    evidence_budget = pack_context_items(
        [f"- {line}" for line in evidence_lines if str(line).strip()],
        token_budget=_grounded_public_evidence_budget_tokens(settings),
        empty_text="- nenhuma evidencia",
    )
    requested_attribute = str((public_plan or {}).get("requested_attribute") or "").strip().lower() or "none"
    instructions = (
        f"Voce e o compositor grounded de respostas publicas do caminho {stack_label} no EduAssist. "
        f"{_PROJECT_CONTEXT} "
        "Sua tarefa e adaptar a resposta final ao foco exato da pergunta do usuario, sem inventar fatos. "
        "Use apenas a pergunta, o plano semantico, o historico curto, as evidencias e o rascunho grounded atual. "
        "Se a pergunta pedir apenas um recorte especifico, responda so esse recorte. "
        "Nao transforme toda evidencia disponivel em resposta se o usuario pediu apenas uma parte dela. "
        "Se a evidencia trouxer um intervalo como 'das 7h30 as 18h00' e a pergunta pedir quando abre, responda o horario inicial. "
        "Se pedir quando fecha, responda o horario final. "
        "Quando o usuario perguntar de forma generica por 'biblioteca', 'direcao', 'secretaria' ou servicos parecidos, "
        "prefira responder com o referente generico ('A biblioteca...', 'A direcao...') e nao injete o nome proprio da entidade, "
        "a menos que o usuario tenha pedido explicitamente o nome ou que o nome seja necessario para evitar ambiguidade. "
        "Exemplo: pergunta 'que horas abre a biblioteca?' => 'A biblioteca abre as 7h30.' "
        "Exemplo: pergunta 'que horas fecha a biblioteca?' => 'A biblioteca fecha as 18h00.' "
        "Exemplo: pergunta 'qual o horario da biblioteca?' => 'A biblioteca funciona das 7h30 as 18h00.' "
        "Exemplo: pergunta 'que horas abre a biblioteca?' com evidencia rotulada como 'Biblioteca Aurora' => "
        "'A biblioteca abre as 7h30.' e nao 'A Biblioteca Aurora abre as 7h30.' "
        "Se a pergunta pedir existencia, responda primeiro sim ou nao e acrescente no maximo um detalhe util. "
        "Nao injete nomes proprios, slogans ou detalhes extras quando eles nao forem necessarios para responder. "
        "Preserve nomes, horarios, datas, valores, canais oficiais e entidades quando eles forem parte da resposta certa. "
        "Trate o rascunho grounded atual apenas como ponto de partida: se ele estiver mais amplo do que a pergunta, enxugue a resposta final. "
        "Se a evidencia nao permitir responder exatamente o recorte pedido, seja honesto sobre o limite e diga apenas o que ela de fato sustenta. "
        "Responda em portugues do Brasil, com tom humano, direto e natural. "
        "Prefira 1 a 3 frases curtas. "
        "Devolva somente JSON valido, sem markdown, com as chaves: "
        "answer_text, answer_focus, used_entity_name, enough_evidence. "
        "answer_text deve conter apenas a resposta final ao usuario. "
        "answer_focus deve resumir o recorte atendido, por exemplo open_time, close_time, hours, existence, contact, name ou summary. "
        "used_entity_name deve ser false quando voce usar referente generico como 'A biblioteca'. "
        "enough_evidence deve ser true quando a evidencia sustenta a resposta final. "
        f"O requested_attribute atual do plano e: {requested_attribute}."
    )
    prompt = (
        f"Escola:\n{_school_name(school_profile)}\n\n"
        f"Pergunta do usuario:\n{request_message}\n\n"
        f"Plano publico:\n{json.dumps(public_plan or {}, ensure_ascii=False)}\n\n"
        f"Historico recente:\n{history_budget.rendered_text}\n\n"
        f"Evidencias:\n{evidence_budget.rendered_text}\n\n"
        f"Rascunho grounded atual:\n{draft_text}"
    )
    return instructions, prompt, history_budget, evidence_budget


def _record_public_answer_context_budget(
    *,
    stack_label: str,
    request_message: str,
    draft_text: str,
    instructions: str,
    prompt: str,
    history_budget: Any,
    evidence_budget: Any,
) -> None:
    snapshot = ContextBudgetSnapshot(
        pipeline="public_answer_composer",
        stack_label=stack_label,
        estimated_prompt_tokens=estimate_text_tokens(prompt),
        estimated_instruction_tokens=estimate_text_tokens(instructions),
        estimated_request_tokens=estimate_text_tokens(request_message),
        estimated_draft_tokens=estimate_text_tokens(draft_text),
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


def _answer_text_from_model_output(raw_text: str | None) -> str | None:
    cleaned = str(raw_text or "").strip()
    if not cleaned:
        return None
    payload = _extract_json_object(cleaned)
    if isinstance(payload, dict):
        answer_text = str(payload.get("answer_text") or "").strip()
        if answer_text:
            return answer_text
    return cleaned


def _generic_subject(
    *,
    request_message: str,
    public_plan: dict[str, Any] | None,
) -> str:
    normalized = str(request_message or "").casefold()
    focus_hint = str((public_plan or {}).get("focus_hint") or "").strip().lower()
    if "biblioteca" in normalized or focus_hint == "library":
        return "A biblioteca"
    if "secretaria" in normalized:
        return "A secretaria"
    if "cantina" in normalized:
        return "A cantina"
    return "O atendimento"


def _extract_hours_range(text: str) -> tuple[str | None, str | None]:
    cleaned = str(text or "").strip()
    if not cleaned:
        return None, None
    interval_match = re.search(
        r"das?\s+(\d{1,2}h\d{2})\s+(?:as|às)\s+(\d{1,2}h\d{2})",
        cleaned,
        flags=re.IGNORECASE,
    )
    if interval_match:
        return interval_match.group(1), interval_match.group(2)
    until_match = re.search(r"até\s+as?\s+(\d{1,2}h\d{2})", cleaned, flags=re.IGNORECASE)
    if until_match:
        return None, until_match.group(1)
    at_match = re.search(r"\bàs?\s+(\d{1,2}h\d{2})", cleaned, flags=re.IGNORECASE)
    if at_match:
        value = at_match.group(1)
        return value, value
    return None, None


def _normalize_attribute_focused_answer(
    *,
    answer_text: str | None,
    request_message: str,
    public_plan: dict[str, Any] | None,
    evidence_lines: list[str],
) -> str | None:
    cleaned = str(answer_text or "").strip()
    if not cleaned:
        return None
    requested_attribute = str((public_plan or {}).get("requested_attribute") or "").strip().lower()
    if requested_attribute not in {"open_time", "close_time"}:
        return cleaned

    start_time, end_time = _extract_hours_range(cleaned)
    if not start_time or not end_time:
        evidence_text = " ".join(str(line or "").strip() for line in evidence_lines[:5])
        evidence_start, evidence_end = _extract_hours_range(evidence_text)
        start_time = start_time or evidence_start
        end_time = end_time or evidence_end

    subject = _generic_subject(request_message=request_message, public_plan=public_plan)
    if requested_attribute == "open_time" and start_time:
        return f"{subject} abre às {start_time}."
    if requested_attribute == "close_time" and end_time:
        return f"{subject} fecha às {end_time}."
    return cleaned


async def _openai_text_call(
    *,
    settings: Any,
    instructions: str,
    prompt: str,
    temperature: float,
    max_output_tokens: int,
    top_p: float,
) -> str | None:
    api_key = _openai_api_key(settings)
    if not api_key:
        return None
    base_url = _openai_base_url(settings)
    model = _openai_model(settings)
    mode = _openai_api_mode(settings)
    provider_name = normalize_gen_ai_provider_name("openai", base_url=base_url)
    with start_gen_ai_client_operation(
        provider_name=provider_name,
        operation_name="public_answer_composition",
        request_model=model,
        base_url=base_url,
        request_temperature=temperature,
        request_max_tokens=max_output_tokens,
        request_top_p=top_p,
        llm_model_profile=_llm_model_profile(settings),
    ) as operation:
        try:
            client = AsyncOpenAI(api_key=api_key, base_url=base_url, timeout=20.0)
            if mode == "chat_completions":
                response = await client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": instructions},
                        {"role": "user", "content": prompt},
                    ],
                    temperature=temperature,
                    max_tokens=max_output_tokens,
                    top_p=top_p,
                )
                operation.finish(
                    usage=extract_openai_usage(
                        response,
                        request_model=model,
                        provider_name=provider_name,
                    )
                )
                choices = getattr(response, "choices", None) or []
                if not choices:
                    return None
                message = getattr(choices[0], "message", None)
                if message is None:
                    return None
                return _answer_text_from_model_output(
                    _openai_message_text(getattr(message, "content", None))
                )
            response = await client.responses.create(
                model=model,
                instructions=instructions,
                input=prompt,
                temperature=temperature,
                max_output_tokens=max_output_tokens,
                top_p=top_p,
            )
            operation.finish(
                usage=extract_openai_usage(
                    response,
                    request_model=model,
                    provider_name=provider_name,
                )
            )
            return _answer_text_from_model_output(response.output_text)
        except Exception as exc:
            operation.finish(error_type=exc.__class__.__name__)
            return None


async def _google_text_call(
    *,
    settings: Any,
    instructions: str,
    prompt: str,
    temperature: float,
    max_output_tokens: int,
    top_p: float,
) -> str | None:
    api_key = _google_api_key(settings)
    if not api_key:
        return None
    base_url = _google_api_base_url(settings).rstrip("/")
    model = _google_model(settings)
    payload = {
        "system_instruction": {"parts": [{"text": instructions}]},
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": temperature,
            "topP": top_p,
            "maxOutputTokens": max_output_tokens,
        },
    }
    provider_name = normalize_gen_ai_provider_name("google", base_url=base_url)
    with start_gen_ai_client_operation(
        provider_name=provider_name,
        operation_name="public_answer_composition",
        request_model=model,
        base_url=base_url,
        request_temperature=temperature,
        request_max_tokens=max_output_tokens,
        request_top_p=top_p,
        llm_model_profile=_llm_model_profile(settings),
    ) as operation:
        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                response = await client.post(
                    f"{base_url}/models/{model}:generateContent",
                    headers={"Content-Type": "application/json", "x-goog-api-key": api_key},
                    json=payload,
                )
                response.raise_for_status()
                body = response.json()
        except Exception as exc:
            operation.finish(error_type=exc.__class__.__name__)
            return None
        if not isinstance(body, dict):
            operation.finish(error_type="invalid_payload")
            return None
        operation.finish(usage=extract_google_usage(body, request_model=model))
    candidates = body.get("candidates")
    if not isinstance(candidates, list) or not candidates:
        return None
    parts = (
        candidates[0].get("content", {}).get("parts")
        if isinstance(candidates[0], dict)
        else None
    )
    if not isinstance(parts, list):
        return None
    texts = [str(part.get("text") or "").strip() for part in parts if isinstance(part, dict)]
    return _answer_text_from_model_output("\n".join(text for text in texts if text).strip())


async def compose_grounded_public_answer_with_provider(
    *,
    settings: Any,
    stack_label: str,
    request_message: str,
    draft_text: str,
    public_plan: dict[str, Any] | None,
    evidence_lines: list[str],
    conversation_context: dict[str, Any] | None,
    school_profile: dict[str, Any] | None,
) -> str | None:
    if not str(request_message or "").strip() or not str(draft_text or "").strip():
        return None
    if not [line for line in evidence_lines if str(line).strip()]:
        return None
    instructions, prompt, history_budget, evidence_budget = _build_sections(
        settings=settings,
        stack_label=stack_label,
        request_message=request_message,
        draft_text=draft_text,
        public_plan=public_plan,
        evidence_lines=evidence_lines,
        conversation_context=conversation_context,
        school_profile=school_profile,
    )
    _record_public_answer_context_budget(
        stack_label=stack_label,
        request_message=request_message,
        draft_text=draft_text,
        instructions=instructions,
        prompt=prompt,
        history_budget=history_budget,
        evidence_budget=evidence_budget,
    )
    provider = _resolve_provider(settings)
    answer_text: str | None = None
    if provider == "openai":
        answer_text = await _openai_text_call(
            settings=settings,
            instructions=instructions,
            prompt=prompt,
            temperature=0.0,
            max_output_tokens=220,
            top_p=0.9,
        )
    elif provider == "google":
        answer_text = await _google_text_call(
            settings=settings,
            instructions=instructions,
            prompt=prompt,
            temperature=0.0,
            max_output_tokens=220,
            top_p=0.9,
        )
    return _normalize_attribute_focused_answer(
        answer_text=answer_text,
        request_message=request_message,
        public_plan=public_plan,
        evidence_lines=evidence_lines,
    )
