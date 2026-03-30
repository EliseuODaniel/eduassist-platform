from __future__ import annotations

from typing import Iterable

from .models import MessageEvidencePack, MessageEvidenceSupport, MessageResponseCitation, RetrievalBackend


def _trim_excerpt(text: str | None, *, limit: int = 220) -> str | None:
    cleaned = str(text or '').strip()
    if not cleaned:
        return None
    if len(cleaned) <= limit:
        return cleaned
    return f'{cleaned[: limit - 3].rstrip()}...'


def build_structured_tool_evidence_pack(
    *,
    selected_tools: Iterable[str],
    slice_name: str,
    summary: str | None = None,
) -> MessageEvidencePack:
    supports = [
        MessageEvidenceSupport(
            kind='tool',
            label=str(tool_name),
            detail='Structured source of truth tool',
        )
        for tool_name in dict.fromkeys(str(tool_name).strip() for tool_name in selected_tools if str(tool_name).strip())
    ]
    source_count = len(supports)
    summary_text = summary or (
        f'Resposta grounded em ferramentas estruturadas do slice {slice_name}.'
        if slice_name
        else 'Resposta grounded em ferramentas estruturadas.'
    )
    return MessageEvidencePack(
        strategy='structured_tool',
        summary=summary_text,
        source_count=source_count,
        support_count=source_count,
        supports=supports[:6],
    )


def build_retrieval_evidence_pack(
    *,
    citations: Iterable[MessageResponseCitation],
    selected_tools: Iterable[str],
    retrieval_backend: RetrievalBackend,
    summary: str | None = None,
) -> MessageEvidencePack:
    citation_list = list(citations)
    supports = [
        MessageEvidenceSupport(
            kind='citation',
            label=citation.document_title,
            detail=f'{citation.version_label} · {citation.chunk_id}',
            excerpt=_trim_excerpt(citation.excerpt),
        )
        for citation in citation_list[:6]
    ]
    if not supports:
        supports.extend(
            MessageEvidenceSupport(
                kind='tool',
                label=str(tool_name),
                detail='Retrieval orchestration tool',
            )
            for tool_name in dict.fromkeys(str(tool_name).strip() for tool_name in selected_tools if str(tool_name).strip())
        )
    summary_text = summary or (
        f'Resposta grounded em retrieval {retrieval_backend.value} com {len(citation_list)} evidencia(s).'
    )
    return MessageEvidencePack(
        strategy='retrieval',
        summary=summary_text,
        source_count=len(citation_list) or len(supports),
        support_count=len(supports),
        supports=supports[:6],
    )
