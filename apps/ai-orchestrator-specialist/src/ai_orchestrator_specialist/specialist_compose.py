from __future__ import annotations

import json
from typing import Any, Callable

from .answer_payloads import (
    access_tier_for_domain as _access_tier_for_domain,
)
from .answer_payloads import (
    aggregate_citations as _aggregate_citations,
)
from .answer_payloads import (
    default_suggested_replies as _default_suggested_replies,
)
from .answer_payloads import (
    mode_from_strategy as _mode_from_strategy,
)
from .answer_payloads import (
    retrieval_backend_from_strategy as _retrieval_backend_from_strategy,
)
from .models import (
    MessageEvidencePack,
    MessageEvidenceSupport,
    MessageIntentClassification,
    MessageResponseSuggestedReply,
    SpecialistResult,
    SupervisorAnswerPayload,
    SupervisorPlan,
)


def parse_specialist_results(trace: Any) -> list[SpecialistResult]:
    items: list[SpecialistResult] = []
    for event in trace.tool_events:
        if event.get("event") != "tool_end":
            continue
        tool_name = str(event.get("tool", "") or "")
        if tool_name not in {
            "institution_specialist",
            "academic_specialist",
            "finance_specialist",
            "workflow_specialist",
            "document_specialist",
        }:
            continue
        raw = event.get("result")
        if not isinstance(raw, str):
            continue
        try:
            payload = json.loads(raw)
        except Exception:
            continue
        try:
            items.append(SpecialistResult.model_validate(payload))
        except Exception:
            continue
    deduped: dict[str, SpecialistResult] = {}
    for item in items:
        deduped[item.specialist_id] = item
    return list(deduped.values())


def merge_specialist_results(
    precomputed_results: list[SpecialistResult],
    traced_results: list[SpecialistResult],
) -> list[SpecialistResult]:
    merged: dict[str, SpecialistResult] = {}
    for item in precomputed_results:
        merged[item.specialist_id] = item
    for item in traced_results:
        merged[item.specialist_id] = item
    return list(merged.values())


def result_looks_negative(
    result: SpecialistResult,
    *,
    normalize_text: Callable[[str | None], str],
) -> bool:
    normalized = normalize_text(result.answer_text)
    return any(
        token in normalized
        for token in {
            "nao foi possivel encontrar",
            "não foi possível encontrar",
            "nao consegui encontrar",
            "não consegui encontrar",
            "nao encontrei",
            "não encontrei",
        }
    )


def _specialist_spec(ctx: Any, specialist_id: str) -> Any | None:
    return ctx.specialist_registry.get(specialist_id)


def direct_compose_candidate(
    ctx: Any,
    *,
    plan: SupervisorPlan,
    specialist_results: list[SpecialistResult],
    normalize_text: Callable[[str | None], str],
) -> SpecialistResult | None:
    if not specialist_results:
        return None
    if plan.request_kind == "multi_domain":
        return None
    ordered = sorted(
        specialist_results,
        key=lambda item: (
            result_looks_negative(item, normalize_text=normalize_text),
            -item.confidence,
            int(getattr(_specialist_spec(ctx, item.specialist_id), "execution_priority", 100)),
        ),
    )
    candidate = ordered[0]
    spec = _specialist_spec(ctx, candidate.specialist_id)
    if spec is None or getattr(spec, "manager_policy", "always") != "prefer_direct":
        return None
    if candidate.confidence < 0.7:
        return None
    return candidate


def _specialist_compose_label(ctx: Any, specialist_id: str) -> str:
    spec = _specialist_spec(ctx, specialist_id)
    label = str(getattr(spec, "compose_label", "") or "").strip()
    if label:
        return label
    return str(getattr(spec, "name", specialist_id) or specialist_id).strip()


def _supports_multi_specialist_compose(
    ctx: Any,
    specialist_results: list[SpecialistResult],
    *,
    normalize_text: Callable[[str | None], str],
) -> bool:
    if len(specialist_results) < 2:
        return False
    specialist_ids = [item.specialist_id for item in specialist_results]
    for result in specialist_results:
        spec = _specialist_spec(ctx, result.specialist_id)
        if spec is None:
            return False
        if getattr(spec, "manager_policy", "always") != "prefer_direct":
            return False
        combinable_with = set(getattr(spec, "combinable_with", []) or [])
        if not set(item for item in specialist_ids if item != result.specialist_id).issubset(combinable_with):
            return False
        if result.confidence < 0.7 or result_looks_negative(result, normalize_text=normalize_text):
            return False
    return True


def _compose_specialist_block(ctx: Any, result: SpecialistResult) -> str:
    spec = _specialist_spec(ctx, result.specialist_id)
    template = str(getattr(spec, "compose_template", "paragraph") or "paragraph").strip().lower()
    label = _specialist_compose_label(ctx, result.specialist_id)
    text = str(result.answer_text or "").strip()
    if template == "bullet":
        lines = [f"{label}:"]
        body_lines = [line.strip() for line in text.splitlines() if line.strip()]
        if body_lines:
            for line in body_lines:
                if line.startswith("- "):
                    lines.append(line)
                else:
                    lines.append(f"- {line}")
        else:
            lines.append(f"- {text}")
        return "\n".join(lines)
    return f"{label}: {text}"


def _merge_domain_suggested_replies(domains: list[str]) -> list[MessageResponseSuggestedReply]:
    merged: list[MessageResponseSuggestedReply] = []
    seen: set[str] = set()
    for domain in domains:
        for item in _default_suggested_replies(domain):
            text = str(item.text).strip()
            if not text or text in seen:
                continue
            seen.add(text)
            merged.append(item)
            if len(merged) >= 4:
                return merged
    return merged[:4]


def build_multi_specialist_answer_from_results(
    ctx: Any,
    *,
    plan: SupervisorPlan,
    specialist_results: list[SpecialistResult],
    normalize_text: Callable[[str | None], str],
    safe_excerpt: Callable[..., str | None],
) -> SupervisorAnswerPayload | None:
    if plan.request_kind != "multi_domain":
        return None
    if not _supports_multi_specialist_compose(ctx, specialist_results, normalize_text=normalize_text):
        return None
    ordered = sorted(
        specialist_results,
        key=lambda item: int(getattr(_specialist_spec(ctx, item.specialist_id), "execution_priority", 100)),
    )
    blocks = [_compose_specialist_block(ctx, item) for item in ordered]
    message_text = "\n\n".join(block for block in blocks if block.strip())
    if not message_text.strip():
        return None
    composed_domains = [plan.primary_domain, *plan.secondary_domains]
    supports: list[MessageEvidenceSupport] = []
    for item in ordered:
        supports.append(
            MessageEvidenceSupport(
                kind="specialist",
                label=item.specialist_id,
                detail=item.evidence_summary,
                excerpt=safe_excerpt(item.answer_text),
            )
        )
    return SupervisorAnswerPayload(
        message_text=message_text,
        mode=_mode_from_strategy(plan.retrieval_strategy),
        classification=MessageIntentClassification(
            domain=plan.primary_domain,
            access_tier=_access_tier_for_domain(plan.primary_domain, ctx.request.user.authenticated),
            confidence=max([plan.confidence, *[item.confidence for item in ordered]]),
            reason=f"specialist_supervisor_multi_direct:{'+'.join(item.specialist_id for item in ordered)}",
        ),
        retrieval_backend=_retrieval_backend_from_strategy(plan.retrieval_strategy),
        selected_tools=sorted({tool for item in ordered for tool in item.tool_names}),
        citations=_aggregate_citations(ordered),
        suggested_replies=_merge_domain_suggested_replies(composed_domains) or _default_suggested_replies(plan.primary_domain),
        evidence_pack=MessageEvidencePack(
            strategy=plan.retrieval_strategy,
            summary=f"Resposta composta diretamente a partir de {len(ordered)} especialistas grounded.",
            source_count=max(1, len(ordered)),
            support_count=len(supports),
            supports=supports[:8],
        ),
        needs_authentication=not ctx.request.user.authenticated and any(domain in {"academic", "finance"} for domain in composed_domains),
        graph_path=["specialist_supervisor", "retrieval_planner", "multi_specialist_direct", *[item.specialist_id for item in ordered]],
        reason=f"specialist_supervisor_multi_direct:{'+'.join(item.specialist_id for item in ordered)}",
    )


def build_direct_answer_from_specialist(
    ctx: Any,
    *,
    plan: SupervisorPlan,
    result: SpecialistResult,
    safe_excerpt: Callable[..., str | None],
) -> SupervisorAnswerPayload:
    citations = result.citations[:6]
    supports = [
        MessageEvidenceSupport(
            kind="specialist",
            label=result.specialist_id,
            detail=result.evidence_summary,
            excerpt=safe_excerpt(result.answer_text),
        )
    ]
    for point in result.support_points[:2]:
        supports.append(
            MessageEvidenceSupport(
                kind="support_point",
                label=result.specialist_id,
                excerpt=safe_excerpt(point),
            )
        )
    for citation in citations[:2]:
        supports.append(
            MessageEvidenceSupport(
                kind="citation",
                label=citation.document_title,
                detail=f"{citation.version_label} · {citation.chunk_id}",
                excerpt=safe_excerpt(citation.excerpt),
            )
        )
    return SupervisorAnswerPayload(
        message_text=result.answer_text,
        mode=_mode_from_strategy(plan.retrieval_strategy),
        classification=MessageIntentClassification(
            domain=plan.primary_domain,
            access_tier=_access_tier_for_domain(plan.primary_domain, ctx.request.user.authenticated),
            confidence=max(plan.confidence, result.confidence),
            reason=f"specialist_supervisor_direct:{result.specialist_id}",
        ),
        retrieval_backend=_retrieval_backend_from_strategy(plan.retrieval_strategy),
        selected_tools=result.tool_names,
        citations=citations,
        suggested_replies=_default_suggested_replies(plan.primary_domain),
        evidence_pack=MessageEvidencePack(
            strategy=plan.retrieval_strategy,
            summary=f"Resposta direta a partir de {result.specialist_id} com grounding suficiente.",
            source_count=len(citations) or 1,
            support_count=len(supports),
            supports=supports[:8],
        ),
        needs_authentication=not ctx.request.user.authenticated and plan.primary_domain in {"academic", "finance"},
        graph_path=["specialist_supervisor", "retrieval_planner", "specialist_direct", result.specialist_id],
        reason=f"specialist_supervisor_direct:{result.specialist_id}",
    )


def budgeted_no_manager_candidate(
    ctx: Any,
    *,
    specialist_results: list[SpecialistResult],
    normalize_text: Callable[[str | None], str],
) -> SpecialistResult | None:
    if not specialist_results:
        return None
    ordered = sorted(
        specialist_results,
        key=lambda item: (
            result_looks_negative(item, normalize_text=normalize_text),
            -item.confidence,
            int(getattr(_specialist_spec(ctx, item.specialist_id), "execution_priority", 100)),
        ),
    )
    candidate = ordered[0]
    if result_looks_negative(candidate, normalize_text=normalize_text):
        return None
    if candidate.confidence < 0.55:
        return None
    return candidate
