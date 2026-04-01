from __future__ import annotations

from typing import Iterable


def canonicalize_evidence_strategy(
    value: str | None,
    *,
    retrieval_backend: str | None = None,
) -> str:
    raw = str(value or "").strip().lower()
    backend = str(retrieval_backend or "").strip().lower()
    if raw in {"structured_tool", "structured_tools", "tool_first", "structured"}:
        return "structured_tool"
    if raw in {"graph_rag", "graphrag"}:
        return "graph_rag"
    if raw in {"hybrid_retrieval", "document_search"}:
        return raw
    if raw in {"pricing_projection", "workflow_status", "clarify", "deny", "direct_answer"}:
        return raw
    if raw == "retrieval":
        if backend == "graph_rag":
            return "graph_rag"
        if backend in {"qdrant_hybrid", "hybrid_retrieval"}:
            return "hybrid_retrieval"
    if backend == "graph_rag":
        return "graph_rag"
    if backend in {"qdrant_hybrid", "hybrid_retrieval"}:
        return "hybrid_retrieval"
    return raw or "none"


def canonicalize_risk_flags(flags: Iterable[str] | None) -> list[str]:
    normalized: list[str] = []
    seen: set[str] = set()
    for item in flags or ():
        token = str(item or "").strip()
        if not token or token in seen:
            continue
        seen.add(token)
        normalized.append(token)
    return normalized
