from __future__ import annotations

from typing import TYPE_CHECKING

from .answer_payloads import access_tier_for_domain as _access_tier_for_domain, default_suggested_replies as _default_suggested_replies
from .models import MessageEvidencePack, MessageEvidenceSupport, MessageIntentClassification, SupervisorAnswerPayload
from .public_doc_knowledge import compose_public_health_second_call
from .public_query_patterns import _looks_like_health_second_call_query
from .restricted_doc_matching import _looks_like_internal_document_query

if TYPE_CHECKING:
    from .runtime import SupervisorRunContext


def _can_read_restricted_documents(user: object) -> bool:
    scopes = {
        str(item).strip().lower()
        for item in getattr(user, "scopes", []) or []
        if str(item).strip()
    }
    role = str(getattr(getattr(user, "role", None), "value", getattr(user, "role", "")) or "").strip().lower()
    return bool(getattr(user, "authenticated", False)) and (
        "documents:private:read" in scopes
        or "documents:restricted:read" in scopes
        or role in {"staff", "teacher"}
    )


def _internal_doc_domain_hint(message: str) -> str:
    normalized = str(message or "").casefold()
    if any(term in normalized for term in ("financeiro", "quitacao", "quitação", "negociacao", "negociação", "pagamento")):
        return "finance"
    if any(term in normalized for term in ("professor", "segunda chamada", "saude", "saúde", "frequencia", "frequência")):
        return "academic"
    if any(term in normalized for term in ("transferencia", "transferência", "secretaria", "documento")):
        return "workflow"
    return "institution"


async def maybe_restricted_document_tool_first_answer(
    ctx: SupervisorRunContext,
    *,
    profile: dict[str, object],
) -> SupervisorAnswerPayload | None:
    if not _looks_like_internal_document_query(ctx.request.message):
        return None

    authorized_for_restricted = _can_read_restricted_documents(ctx.request.user)
    domain_hint = _internal_doc_domain_hint(ctx.request.message)
    if not authorized_for_restricted:
        normalized_message = ctx.request.message.casefold()
        topic_hint = 'sobre esse tema'
        if 'playbook' in normalized_message or 'negoci' in normalized_message:
            topic_hint = 'sobre playbook interno ou negociacao com familias'
        elif 'viagem internacional' in normalized_message:
            topic_hint = 'sobre viagem internacional de alunos'
        elif 'manual interno do professor' in normalized_message:
            topic_hint = 'sobre manual interno do professor'
        elif 'escopo parcial' in normalized_message:
            topic_hint = 'sobre responsaveis com escopo parcial'
        public_bridge = ""
        if _looks_like_health_second_call_query(ctx.request.message):
            public_answer = compose_public_health_second_call()
            if public_answer:
                public_bridge = f"\n\nPosso, no entanto, te orientar pelo material publico:\n{public_answer}"
        elif 'escopo parcial' in normalized_message:
            public_bridge = (
                "\n\nNo que e publico, a base aberta cobre apenas orientacoes gerais; "
                "regras operacionais de permissao, restricao e encaminhamento continuam internas. "
                "Na pratica, o proximo passo e pedir ao setor responsavel que confirme o procedimento aplicavel ao perfil autorizado."
            )
        return SupervisorAnswerPayload(
            message_text=(
                f"Nao posso compartilhar procedimentos, protocolos, manuais ou playbooks internos da escola {topic_hint}. "
                "Seu perfil nao tem acesso a esse material restrito. Se voce quiser, eu posso explicar apenas o que e publico sobre esse mesmo tema ou abrir um handoff."
            )
            + public_bridge,
            mode="deny",
            classification=MessageIntentClassification(
                domain=domain_hint,
                access_tier=_access_tier_for_domain(domain_hint, ctx.request.user.authenticated),
                confidence=0.99,
                reason="specialist_supervisor_tool_first:restricted_document_denied",
            ),
            evidence_pack=MessageEvidencePack(
                strategy="deny",
                summary="Pedido de acesso a documento restrito negado por politica de acesso.",
                source_count=1,
                support_count=1,
                supports=[
                    MessageEvidenceSupport(kind="policy", label="Documento restrito", detail="Acesso limitado a staff e perfis autorizados"),
                ],
            ),
            suggested_replies=_default_suggested_replies(domain_hint),
            graph_path=["specialist_supervisor", "tool_first", "restricted_document_denied"],
            reason="specialist_supervisor_tool_first:restricted_document_denied",
        )

    from .runtime import (
        _citation_from_retrieval_hit,
        _compose_internal_doc_grounded_answer,
        _compose_internal_doc_no_match_answer,
        _orchestrator_retrieval_search,
        _safe_excerpt,
        _select_relevant_internal_doc_hits,
    )

    try:
        retrieval_payload = await _orchestrator_retrieval_search(
            ctx,
            query=ctx.request.message,
            visibility="restricted",
            category="private_docs",
            top_k=5,
        )
    except Exception:
        return SupervisorAnswerPayload(
            message_text=_compose_internal_doc_no_match_answer(ctx.request.message, profile),
            mode="hybrid_retrieval",
            classification=MessageIntentClassification(
                domain=domain_hint,
                access_tier=_access_tier_for_domain(domain_hint, ctx.request.user.authenticated),
                confidence=0.8,
                reason="specialist_supervisor_tool_first:restricted_document_search_fallback",
            ),
            retrieval_backend="qdrant_hybrid",
            evidence_pack=MessageEvidencePack(
                strategy="document_search",
                summary="Busca em documentos restritos falhou e caiu para fallback deterministico seguro.",
                source_count=0,
                support_count=1,
                supports=[
                    MessageEvidenceSupport(kind="retrieval", label="Documentos restritos", detail="falha temporaria na busca interna, com fallback seguro"),
                ],
            ),
            suggested_replies=_default_suggested_replies(domain_hint),
            graph_path=["specialist_supervisor", "tool_first", "restricted_document_search_fallback"],
            reason="specialist_supervisor_tool_first:restricted_document_search_fallback",
        )
    hits = retrieval_payload.get("hits") if isinstance(retrieval_payload, dict) else []
    normalized_hits = hits if isinstance(hits, list) else []
    relevant_hits = _select_relevant_internal_doc_hits(ctx.request.message, normalized_hits)
    if relevant_hits:
        citations = [
            citation
            for hit in relevant_hits
            if (citation := _citation_from_retrieval_hit(hit)) is not None
        ][:4]
        supports = [
            MessageEvidenceSupport(
                kind="citation",
                label=citation.document_title,
                detail=f"{citation.version_label} · {citation.chunk_id}",
                excerpt=_safe_excerpt(citation.excerpt),
            )
            for citation in citations[:3]
        ]
        return SupervisorAnswerPayload(
            message_text=_compose_internal_doc_grounded_answer(ctx.request.message, relevant_hits),
            mode="hybrid_retrieval",
            classification=MessageIntentClassification(
                domain=domain_hint,
                access_tier=_access_tier_for_domain(domain_hint, ctx.request.user.authenticated),
                confidence=0.94,
                reason="specialist_supervisor_tool_first:restricted_document_search",
            ),
            retrieval_backend="qdrant_hybrid",
            citations=citations,
            evidence_pack=MessageEvidencePack(
                strategy="document_search",
                summary="Resposta grounded diretamente em documentos restritos recuperados do acervo interno.",
                source_count=len(citations) or 1,
                support_count=len(supports),
                supports=supports,
            ),
            suggested_replies=_default_suggested_replies(domain_hint),
            graph_path=["specialist_supervisor", "tool_first", "restricted_document_search"],
            reason="specialist_supervisor_tool_first:restricted_document_search",
        )

    return SupervisorAnswerPayload(
        message_text=_compose_internal_doc_no_match_answer(ctx.request.message, profile),
        mode="hybrid_retrieval",
        classification=MessageIntentClassification(
            domain=domain_hint,
            access_tier=_access_tier_for_domain(domain_hint, ctx.request.user.authenticated),
            confidence=0.82,
            reason="specialist_supervisor_tool_first:restricted_document_no_match",
        ),
        retrieval_backend="qdrant_hybrid",
        evidence_pack=MessageEvidencePack(
            strategy="document_search",
            summary="Busca em documentos restritos sem encontrar evidencias suficientemente especificas para ampliar a resposta.",
            source_count=1 if normalized_hits else 0,
            support_count=1,
            supports=[
                MessageEvidenceSupport(kind="retrieval", label="Documentos restritos", detail="Busca executada sem match especifico suficiente"),
            ],
        ),
        suggested_replies=_default_suggested_replies(domain_hint),
        graph_path=["specialist_supervisor", "tool_first", "restricted_document_no_match"],
        reason="specialist_supervisor_tool_first:restricted_document_no_match",
    )
