from __future__ import annotations

from typing import Any

from eduassist_semantic_ingress.context_budget import pack_context_items


def _history_budget_tokens(settings: Any) -> int:
    return max(
        96,
        int(
            getattr(settings, "stack_local_llm_history_budget_tokens", None)
            or getattr(settings, "grounded_public_history_budget_tokens", 180)
            or 180
        ),
    )


def _evidence_budget_tokens(settings: Any) -> int:
    return max(
        128,
        int(
            getattr(settings, "stack_local_llm_evidence_budget_tokens", None)
            or getattr(settings, "grounded_public_evidence_budget_tokens", 320)
            or 320
        ),
    )


def _calendar_budget_tokens(settings: Any) -> int:
    return max(
        96,
        int(getattr(settings, "stack_local_llm_calendar_budget_tokens", 140) or 140),
    )


def recent_message_lines(conversation_context: dict[str, Any] | None) -> list[str]:
    lines: list[str] = []
    if not isinstance(conversation_context, dict):
        return lines
    for item in conversation_context.get("recent_messages") or []:
        if not isinstance(item, dict):
            continue
        sender = str(item.get("sender_type", "desconhecido")).strip()
        content = str(item.get("content", "")).strip()
        if content:
            lines.append(f"- {sender}: {content}")
    return lines


def pack_recent_history(
    *,
    settings: Any,
    conversation_context: dict[str, Any] | None,
) -> str:
    return pack_context_items(
        recent_message_lines(conversation_context),
        token_budget=_history_budget_tokens(settings),
        empty_text="- nenhum",
        keep_last=True,
    ).rendered_text


def pack_recent_history_lines(
    *,
    settings: Any,
    recent_messages: list[str],
) -> str:
    return pack_context_items(
        [f"- {line}" for line in recent_messages if str(line).strip()],
        token_budget=_history_budget_tokens(settings),
        empty_text="- nenhum",
        keep_last=True,
    ).rendered_text


def pack_evidence_lines(
    *,
    settings: Any,
    evidence_lines: list[str],
    empty_text: str,
) -> str:
    return pack_context_items(
        [f"- {line}" for line in evidence_lines if str(line).strip()],
        token_budget=_evidence_budget_tokens(settings),
        empty_text=empty_text,
    ).rendered_text


def pack_calendar_lines(
    *,
    settings: Any,
    calendar_lines: list[str],
    empty_text: str,
) -> str:
    return pack_context_items(
        [line for line in calendar_lines if str(line).strip()],
        token_budget=_calendar_budget_tokens(settings),
        empty_text=empty_text,
    ).rendered_text
