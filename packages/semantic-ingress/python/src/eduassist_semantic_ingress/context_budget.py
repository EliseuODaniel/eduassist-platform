from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
import re
from typing import Any

from eduassist_observability import record_counter, record_histogram, set_span_attributes

try:  # pragma: no cover - optional runtime optimization
    import tiktoken
except Exception:  # pragma: no cover - fallback for environments without tiktoken
    tiktoken = None  # type: ignore[assignment]


_TOKEN_ESTIMATE_ENCODING = "o200k_base"


@dataclass(frozen=True)
class ContextSectionBudget:
    estimated_tokens: int
    total_items: int | None = None
    used_items: int | None = None
    truncated: bool = False


@dataclass(frozen=True)
class PackedContextSection:
    rendered_text: str
    estimated_tokens: int
    total_items: int
    used_items: int
    truncated: bool


@dataclass(frozen=True)
class ContextBudgetSnapshot:
    pipeline: str
    stack_label: str
    estimated_prompt_tokens: int
    estimated_instruction_tokens: int
    estimated_request_tokens: int
    estimated_draft_tokens: int | None = None
    estimated_candidate_tokens: int | None = None
    candidate_count: int | None = None
    history: ContextSectionBudget | None = None
    evidence: ContextSectionBudget | None = None


@lru_cache(maxsize=1)
def _token_encoding() -> Any | None:
    if tiktoken is None:
        return None
    try:
        return tiktoken.get_encoding(_TOKEN_ESTIMATE_ENCODING)
    except Exception:
        return None


def estimate_text_tokens(text: str | None) -> int:
    cleaned = str(text or "").strip()
    if not cleaned:
        return 0
    encoding = _token_encoding()
    if encoding is not None:
        try:
            return len(encoding.encode(cleaned, disallowed_special=()))
        except Exception:
            pass
    lexical_units = len(re.findall(r"\w+|[^\w\s]", cleaned, flags=re.UNICODE))
    return max(1, int(round(max(len(cleaned) / 4.0, lexical_units * 1.1))))


def build_context_section_budget(
    *,
    rendered_text: str | None,
    total_items: int | None,
    used_items: int | None,
) -> ContextSectionBudget:
    total = int(total_items) if total_items is not None else None
    used = int(used_items) if used_items is not None else None
    return ContextSectionBudget(
        estimated_tokens=estimate_text_tokens(rendered_text),
        total_items=total,
        used_items=used,
        truncated=bool(total is not None and used is not None and total > used),
    )


def pack_context_items(
    items: list[str] | tuple[str, ...] | None,
    *,
    token_budget: int,
    empty_text: str,
    keep_last: bool = False,
) -> PackedContextSection:
    clean_items = [str(item).strip() for item in (items or []) if str(item).strip()]
    total_items = len(clean_items)
    if total_items == 0:
        return PackedContextSection(
            rendered_text=empty_text,
            estimated_tokens=estimate_text_tokens(empty_text),
            total_items=0,
            used_items=0,
            truncated=False,
        )

    budget = max(1, int(token_budget))
    ordered_items = list(reversed(clean_items)) if keep_last else list(clean_items)
    selected: list[str] = []
    selected_tokens = 0
    for index, item in enumerate(ordered_items):
        item_tokens = estimate_text_tokens(item)
        if selected and selected_tokens + item_tokens > budget:
            break
        if not selected and item_tokens > budget:
            selected.append(item)
            selected_tokens = item_tokens
            break
        selected.append(item)
        selected_tokens += item_tokens
        if index == len(ordered_items) - 1:
            break
    if keep_last:
        selected.reverse()
    rendered_text = "\n".join(selected) if selected else empty_text
    return PackedContextSection(
        rendered_text=rendered_text,
        estimated_tokens=estimate_text_tokens(rendered_text),
        total_items=total_items,
        used_items=len(selected),
        truncated=len(selected) < total_items,
    )


def pack_context_json_items(
    items: list[dict[str, Any]] | tuple[dict[str, Any], ...] | None,
    *,
    token_budget: int,
    empty_text: str,
) -> tuple[list[dict[str, Any]], PackedContextSection]:
    clean_items = [item for item in (items or []) if isinstance(item, dict)]
    total_items = len(clean_items)
    if total_items == 0:
        packed = PackedContextSection(
            rendered_text=empty_text,
            estimated_tokens=estimate_text_tokens(empty_text),
            total_items=0,
            used_items=0,
            truncated=False,
        )
        return [], packed

    budget = max(1, int(token_budget))
    selected: list[dict[str, Any]] = []
    selected_tokens = 0
    for item in clean_items:
        serialized = json_dumps(item)
        item_tokens = estimate_text_tokens(serialized)
        if selected and selected_tokens + item_tokens > budget:
            break
        if not selected and item_tokens > budget:
            selected.append(item)
            selected_tokens = item_tokens
            break
        selected.append(item)
        selected_tokens += item_tokens
    rendered_text = (
        json_dumps(selected, sort_keys=True)
        if selected
        else empty_text
    )
    packed = PackedContextSection(
        rendered_text=rendered_text,
        estimated_tokens=estimate_text_tokens(rendered_text),
        total_items=total_items,
        used_items=len(selected),
        truncated=len(selected) < total_items,
    )
    return selected, packed


def json_dumps(value: Any, *, sort_keys: bool = False) -> str:
    import json

    return json.dumps(value, ensure_ascii=False, sort_keys=sort_keys)


def record_context_budget(snapshot: ContextBudgetSnapshot) -> None:
    attrs = {
        "eduassist.context.pipeline": snapshot.pipeline,
        "eduassist.context.stack": snapshot.stack_label,
    }
    span_attributes: dict[str, Any] = {
        **attrs,
        "eduassist.context.prompt_tokens_estimated": snapshot.estimated_prompt_tokens,
        "eduassist.context.instructions_tokens_estimated": snapshot.estimated_instruction_tokens,
        "eduassist.context.request_tokens_estimated": snapshot.estimated_request_tokens,
    }
    if snapshot.estimated_draft_tokens is not None:
        span_attributes["eduassist.context.draft_tokens_estimated"] = snapshot.estimated_draft_tokens
    if snapshot.estimated_candidate_tokens is not None:
        span_attributes["eduassist.context.candidate_tokens_estimated"] = (
            snapshot.estimated_candidate_tokens
        )
    if snapshot.candidate_count is not None:
        span_attributes["eduassist.context.candidate_count"] = snapshot.candidate_count
    if snapshot.history is not None:
        span_attributes["eduassist.context.history_tokens_estimated"] = (
            snapshot.history.estimated_tokens
        )
        if snapshot.history.total_items is not None:
            span_attributes["eduassist.context.history_items_total"] = snapshot.history.total_items
        if snapshot.history.used_items is not None:
            span_attributes["eduassist.context.history_items_used"] = snapshot.history.used_items
        span_attributes["eduassist.context.history_truncated"] = snapshot.history.truncated
    if snapshot.evidence is not None:
        span_attributes["eduassist.context.evidence_tokens_estimated"] = (
            snapshot.evidence.estimated_tokens
        )
        if snapshot.evidence.total_items is not None:
            span_attributes["eduassist.context.evidence_items_total"] = snapshot.evidence.total_items
        if snapshot.evidence.used_items is not None:
            span_attributes["eduassist.context.evidence_items_used"] = snapshot.evidence.used_items
        span_attributes["eduassist.context.evidence_truncated"] = snapshot.evidence.truncated
    set_span_attributes(**span_attributes)

    sections: list[tuple[str, int | None]] = [
        ("prompt", snapshot.estimated_prompt_tokens),
        ("instructions", snapshot.estimated_instruction_tokens),
        ("request", snapshot.estimated_request_tokens),
        ("draft", snapshot.estimated_draft_tokens),
        ("candidates", snapshot.estimated_candidate_tokens),
        ("history", snapshot.history.estimated_tokens if snapshot.history is not None else None),
        ("evidence", snapshot.evidence.estimated_tokens if snapshot.evidence is not None else None),
    ]
    for section, value in sections:
        if value is None:
            continue
        record_histogram(
            "eduassist.context.estimated_tokens",
            value,
            meter_name="eduassist.context",
            unit="{token}",
            description="Estimated tokens assembled before provider dispatch.",
            attributes={**attrs, "eduassist.context.section": section},
        )
    if snapshot.history is not None and snapshot.history.truncated:
        record_counter(
            "eduassist.context.truncation",
            meter_name="eduassist.context",
            description="Prompt sections truncated before provider dispatch.",
            attributes={**attrs, "eduassist.context.section": "history"},
        )
    if snapshot.evidence is not None and snapshot.evidence.truncated:
        record_counter(
            "eduassist.context.truncation",
            meter_name="eduassist.context",
            description="Prompt sections truncated before provider dispatch.",
            attributes={**attrs, "eduassist.context.section": "evidence"},
        )
