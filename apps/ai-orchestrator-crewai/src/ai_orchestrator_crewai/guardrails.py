from __future__ import annotations

from collections.abc import Callable, Iterable
import re
import unicodedata
from typing import Any

from pydantic import BaseModel

try:
    from crewai.tasks.task_output import TaskOutput  # type: ignore
except Exception:  # pragma: no cover
    TaskOutput = Any  # type: ignore


Guardrail = Callable[[TaskOutput], tuple[bool, Any]]


def _normalize_text(value: str) -> str:
    text = unicodedata.normalize('NFKD', str(value or ''))
    text = ''.join(ch for ch in text if not unicodedata.combining(ch))
    return ' '.join(text.lower().split())


def _extract_candidate(output: TaskOutput, model_type: type[BaseModel]) -> BaseModel | None:
    candidate = getattr(output, 'pydantic', None)
    if isinstance(candidate, model_type):
        return candidate
    return None


def _extract_text(output: TaskOutput) -> str:
    candidate = getattr(output, 'pydantic', None)
    if isinstance(candidate, BaseModel):
        answer_text = getattr(candidate, 'answer_text', None)
        if isinstance(answer_text, str) and answer_text.strip():
            return answer_text.strip()
    raw = getattr(output, 'raw', None)
    return str(raw or '').strip()


def _contains_any(normalized_text: str, anchors: Iterable[str]) -> bool:
    for anchor in anchors:
        normalized_anchor = _normalize_text(str(anchor or ''))
        if normalized_anchor and normalized_anchor in normalized_text:
            return True
    return False


def _citation_subset(candidate: BaseModel, *, valid_source_ids: set[str]) -> tuple[bool, str]:
    citations = getattr(candidate, 'citations', None)
    if not isinstance(citations, list):
        return True, ''
    invalid = [str(item) for item in citations if str(item) and str(item) not in valid_source_ids]
    if invalid:
        return False, f'invalid_citation:{invalid[0]}'
    return True, ''


def require_pydantic_model(model_type: type[BaseModel]) -> Guardrail:
    def _guardrail(output: TaskOutput) -> tuple[bool, Any]:
        if _extract_candidate(output, model_type) is None:
            return False, f'expected_pydantic:{model_type.__name__}'
        return True, output

    return _guardrail


def require_sources_subset(*, model_type: type[BaseModel], field_name: str, valid_source_ids: Iterable[str]) -> Guardrail:
    valid = {str(item) for item in valid_source_ids if str(item).strip()}

    def _guardrail(output: TaskOutput) -> tuple[bool, Any]:
        candidate = _extract_candidate(output, model_type)
        if candidate is None:
            return False, f'expected_pydantic:{model_type.__name__}'
        values = getattr(candidate, field_name, None)
        if not isinstance(values, list):
            return True, output
        invalid = [str(item) for item in values if str(item) and str(item) not in valid]
        if invalid:
            return False, f'invalid_source:{invalid[0]}'
        return True, output

    return _guardrail


def require_answer_citations_subset(*, model_type: type[BaseModel], valid_source_ids: Iterable[str]) -> Guardrail:
    valid = {str(item) for item in valid_source_ids if str(item).strip()}

    def _guardrail(output: TaskOutput) -> tuple[bool, Any]:
        candidate = _extract_candidate(output, model_type)
        if candidate is None:
            return False, f'expected_pydantic:{model_type.__name__}'
        ok, reason = _citation_subset(candidate, valid_source_ids=valid)
        if not ok:
            return False, reason
        answer_text = getattr(candidate, 'answer_text', None)
        if not isinstance(answer_text, str) or not answer_text.strip():
            return False, 'empty_answer_text'
        return True, output

    return _guardrail


def require_anchor_overlap(
    *,
    model_type: type[BaseModel],
    anchors: Iterable[str],
    allow_if_no_anchors: bool = True,
) -> Guardrail:
    normalized_anchors = [anchor for anchor in (_normalize_text(item) for item in anchors) if anchor]

    def _guardrail(output: TaskOutput) -> tuple[bool, Any]:
        candidate = _extract_candidate(output, model_type)
        if candidate is None:
            return False, f'expected_pydantic:{model_type.__name__}'
        if not normalized_anchors:
            return (True, output) if allow_if_no_anchors else (False, 'missing_required_anchor_set')
        normalized_text = _normalize_text(_extract_text(output))
        if _contains_any(normalized_text, normalized_anchors):
            return True, output
        return False, f'missing_anchor:{normalized_anchors[0]}'

    return _guardrail


def require_no_forbidden_entities(
    *,
    model_type: type[BaseModel],
    forbidden_names: Iterable[str],
) -> Guardrail:
    forbidden = [name for name in (_normalize_text(item) for item in forbidden_names) if name]

    def _guardrail(output: TaskOutput) -> tuple[bool, Any]:
        candidate = _extract_candidate(output, model_type)
        if candidate is None:
            return False, f'expected_pydantic:{model_type.__name__}'
        normalized_text = _normalize_text(_extract_text(output))
        for name in forbidden:
            if name and name in normalized_text:
                return False, f'forbidden_entity:{name}'
        return True, output

    return _guardrail


def require_nonempty_reason_when_invalid(model_type: type[BaseModel]) -> Guardrail:
    def _guardrail(output: TaskOutput) -> tuple[bool, Any]:
        candidate = _extract_candidate(output, model_type)
        if candidate is None:
            return False, f'expected_pydantic:{model_type.__name__}'
        valid = getattr(candidate, 'valid', None)
        reason = str(getattr(candidate, 'reason', '') or '').strip()
        if valid is False and not reason:
            return False, 'invalid_without_reason'
        return True, output

    return _guardrail


def extract_literal_anchors(text: str) -> list[str]:
    if not text:
        return []
    anchors: list[str] = []
    patterns = (
        r'@[a-z0-9_.]+',
        r'\(\d{2}\)\s*\d{4,5}-\d{4}',
        r'\b[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}\b',
        r'\bhttps?://\S+\b',
        r'\b[A-Z]{3}-\d{8}-[A-Z0-9]+\b',
        r'\b\d{1,2}/\d{1,2}/\d{4}\b',
        r'\b\d{1,2}h\d{2}\b',
        r'R\$\s*\d+[.,]?\d*',
    )
    for pattern in patterns:
        anchors.extend(match.group(0) for match in re.finditer(pattern, text))
    return list(dict.fromkeys(anchors))
