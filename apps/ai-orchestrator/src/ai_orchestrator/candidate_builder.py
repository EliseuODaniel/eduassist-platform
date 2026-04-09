from __future__ import annotations

from dataclasses import dataclass, field

from .models import RetrievalBackend


@dataclass(frozen=True)
class ResponseCandidate:
    kind: str
    text: str
    reason: str
    used_llm: bool = False
    llm_stages: tuple[str, ...] = ()
    retrieval_backend: RetrievalBackend = RetrievalBackend.none
    selected_tools: tuple[str, ...] = ()
    source_count: int = 0
    support_count: int = 0
    cacheable: bool = True
    metadata: dict[str, object] = field(default_factory=dict)


def build_response_candidate(
    *,
    kind: str,
    text: str,
    reason: str,
    used_llm: bool = False,
    llm_stages: tuple[str, ...] = (),
    retrieval_backend: RetrievalBackend = RetrievalBackend.none,
    selected_tools: tuple[str, ...] = (),
    source_count: int = 0,
    support_count: int = 0,
    cacheable: bool = True,
    metadata: dict[str, object] | None = None,
) -> ResponseCandidate | None:
    cleaned = str(text or "").strip()
    if not cleaned:
        return None
    return ResponseCandidate(
        kind=kind,
        text=cleaned,
        reason=reason,
        used_llm=used_llm,
        llm_stages=tuple(llm_stages),
        retrieval_backend=retrieval_backend,
        selected_tools=tuple(selected_tools),
        source_count=max(0, int(source_count)),
        support_count=max(0, int(support_count)),
        cacheable=cacheable,
        metadata=dict(metadata or {}),
    )
