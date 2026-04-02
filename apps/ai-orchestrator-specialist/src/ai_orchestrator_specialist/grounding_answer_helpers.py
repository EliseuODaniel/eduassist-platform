from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from .models import MessageEvidenceSupport


@dataclass(frozen=True)
class GroundingAnswerDeps:
    normalize_text: Callable[[str | None], str]
    safe_excerpt: Callable[..., str | None]
    school_name: Callable[[dict[str, Any] | None], str]
    looks_like_health_second_call_query: Callable[[str], bool]
    compose_public_health_second_call: Callable[[], str]


def compose_public_graph_rag_fallback_answer(
    query: str,
    hits: list[dict[str, Any]],
    *,
    deps: GroundingAnswerDeps,
) -> str:
    normalized = deps.normalize_text(query)
    lines = [
        "Nao fechei a sintese transversal completa em GraphRAG a tempo, mas os documentos publicos mais relevantes apontam um encadeamento claro entre prazos, regras, rotinas e canais digitais."
    ]
    if any(term in normalized for term in ("portal", "credenciais", "canais digitais", "comunicacao", "comunicação")):
        lines.append(
            "Calendario, orientacoes complementares e comunicacao com as familias funcionam como um circuito unico: quando a escola ajusta um prazo ou uma rotina, ela tende a atualizar o portal e reforcar isso pelos canais oficiais."
        )
    if any(term in normalized for term in ("avaliac", "recuperac", "prova", "simulado")):
        lines.append(
            "Isso repercute em avaliacoes, recuperacoes e justificativas: perder um aviso ou uma regra costuma afetar segunda chamada, acompanhamento pedagogico e organizacao do estudante."
        )
    if any(term in normalized for term in ("biblioteca", "laboratorio", "laboratorios", "recursos", "espacos de estudo")):
        lines.append(
            "Biblioteca, laboratorios e espacos de estudo entram como apoio operacional: acesso, uso correto e comunicados dependem de regulamentos e do acompanhamento digital ao longo do ano."
        )
    lines.append("Os documentos que mais sustentam essa relacao foram:")
    for hit in hits:
        title = str(hit.get("document_title") or "Documento publico").strip()
        excerpt = deps.safe_excerpt(str(hit.get("text_excerpt") or hit.get("contextual_summary") or "").strip(), limit=220)
        if excerpt:
            lines.append(f"- {title}: {excerpt}")
    lines.append(
        "Na pratica, o risco para a familia e tratar cada documento como isolado: um atraso em credenciais, uma leitura incompleta do calendario ou um regulamento ignorado tende a repercutir em comunicados, prazos, avaliacoes, autorizacoes e acesso a servicos de apoio."
    )
    return "\n".join(lines)


def supports_from_public_graph_rag_fallback_hits(
    hits: list[dict[str, Any]],
    *,
    deps: GroundingAnswerDeps,
) -> list[MessageEvidenceSupport]:
    supports: list[MessageEvidenceSupport] = []
    for hit in hits:
        title = str(hit.get("document_title") or "Documento publico").strip()
        excerpt = deps.safe_excerpt(str(hit.get("text_excerpt") or hit.get("contextual_summary") or "").strip(), limit=180)
        supports.append(
            MessageEvidenceSupport(
                kind="document",
                label=title,
                detail=excerpt or "evidencia publica relevante",
            )
        )
    return supports


def compose_internal_doc_grounded_answer(
    query: str,
    hits: list[dict[str, Any]],
) -> str:
    primary = hits[0]
    primary_title = str(primary.get("document_title") or "documento interno").strip()
    primary_excerpt = str(primary.get("text_excerpt") or primary.get("contextual_summary") or "").strip()
    primary_section = " - ".join(
        str(part).strip()
        for part in (primary.get("section_parent"), primary.get("section_title"))
        if str(part or "").strip()
    )
    normalized_query = query.casefold()
    if "professor" in normalized_query and "avaliac" in normalized_query:
        lines = [
            "Para o pedido sobre o manual interno do professor, o trecho mais relevante sobre registro de avaliacoes e comunicacao pedagogica e este:",
            f"Documento principal: {primary_title}.",
        ]
    elif "telegram" in normalized_query and "escopo" in normalized_query:
        lines = [
            "Para o pedido sobre limites de acesso no Telegram para responsaveis com escopo parcial, o protocolo interno mais relevante e este:",
            f"Documento principal: {primary_title}.",
        ]
    elif ("negoci" in normalized_query or "financeir" in normalized_query) and ("familia" in normalized_query or "família" in normalized_query):
        lines = [
            "Para o pedido sobre o playbook interno de negociacao financeira com a familia, a orientacao mais relevante e esta:",
            f"Documento principal: {primary_title}.",
        ]
    else:
        lines = [f"Nos documentos internos consultados, a orientacao mais relevante aparece em {primary_title}:"]
    if primary_section:
        lines.append(f"Secao relevante: {primary_section}.")
    if primary_excerpt:
        lines.append(primary_excerpt)
    seen_titles = {primary_title}
    for hit in hits[1:]:
        title = str(hit.get("document_title") or "").strip()
        excerpt = str(hit.get("text_excerpt") or hit.get("contextual_summary") or "").strip()
        section = " - ".join(
            str(part).strip()
            for part in (hit.get("section_parent"), hit.get("section_title"))
            if str(part or "").strip()
        )
        if not excerpt:
            continue
        label = title if title and title not in seen_titles else "Complemento interno"
        if section:
            lines.append(f"{label} ({section}): {excerpt}")
        else:
            lines.append(f"{label}: {excerpt}")
        if title:
            seen_titles.add(title)
    return "\n".join(lines)


def compose_internal_doc_no_match_answer(
    message: str,
    profile: dict[str, Any] | None,
    *,
    deps: GroundingAnswerDeps,
) -> str:
    if deps.looks_like_health_second_call_query(message):
        public_answer = deps.compose_public_health_second_call()
        if public_answer:
            return (
                "Consultei os documentos internos disponiveis e nao encontrei uma orientacao adicional especifica "
                "sobre segunda chamada por motivo de saude alem do que ja aparece no material publico.\n\n"
                f"{public_answer}"
            )
    school_name = deps.school_name(profile)
    quoted_message = str(message or "").strip().rstrip(' ?!.')
    normalized = deps.normalize_text(quoted_message)
    if (
        any(term in normalized for term in ("viagem internacional", "excursao internacional", "excursão internacional"))
        and any(term in normalized for term in ("hospedagem", "pernoite"))
    ):
        return (
            f"Consultei os documentos internos disponiveis do {school_name}, mas nao encontrei uma orientacao restrita "
            "especifica sobre excursao ou viagem internacional com hospedagem para o ensino medio."
        )
    return (
        f'Consultei os documentos internos disponiveis do {school_name}, mas nao encontrei uma orientacao restrita '
        f'especifica para: "{quoted_message}".'
    )
