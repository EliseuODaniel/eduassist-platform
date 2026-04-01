from __future__ import annotations

import json
from typing import Any


def _compact_operational_memory(memory: Any) -> dict[str, Any]:
    if memory is None or not hasattr(memory, "model_dump"):
        return {}
    payload = memory.model_dump(mode="json")
    return {
        key: value
        for key, value in payload.items()
        if value not in (None, "", [], {})
        and key in {
            "active_domain",
            "active_domains",
            "active_student_name",
            "alternate_student_name",
            "active_subject",
            "active_topic",
            "pending_kind",
            "multi_intent_domains",
            "last_specialists",
            "last_route",
            "last_reason",
        }
    }


def _compact_retrieval_advice(advice: Any) -> dict[str, Any]:
    if advice is None or not hasattr(advice, "model_dump"):
        return {}
    payload = advice.model_dump(mode="json")
    return {
        key: value
        for key, value in payload.items()
        if value not in (None, "", [], {})
        and key in {
            "primary_domain",
            "secondary_domains",
            "retrieval_strategy",
            "recommended_specialists",
            "preferred_category",
            "requires_grounding",
            "requires_clarification",
            "should_deny",
            "evidence_queries",
            "rationale",
            "confidence",
        }
    }


def _compact_specialist_results(results: list[Any]) -> list[dict[str, Any]]:
    compacted: list[dict[str, Any]] = []
    for item in results:
        if item is None or not hasattr(item, "model_dump"):
            continue
        payload = item.model_dump(mode="json")
        compacted.append(
            {
                "specialist_id": payload.get("specialist_id"),
                "answer_text": str(payload.get("answer_text") or "").strip(),
                "evidence_summary": payload.get("evidence_summary"),
                "tool_names": list(payload.get("tool_names") or [])[:6],
                "support_points": list(payload.get("support_points") or [])[:4],
                "citations": [
                    {
                        "document_title": citation.get("document_title"),
                        "chunk_id": citation.get("chunk_id"),
                    }
                    for citation in list(payload.get("citations") or [])[:4]
                    if isinstance(citation, dict)
                ],
                "confidence": payload.get("confidence"),
            }
        )
    return compacted


def build_specialist_execution_prompt(
    ctx: Any,
    *,
    specialist_id: str,
    plan: Any,
) -> str:
    compact_advice = _compact_retrieval_advice(getattr(ctx, "retrieval_advice", None))
    compact_memory = _compact_operational_memory(getattr(ctx, "operational_memory", None))
    return (
        f"Especialista alvo: {specialist_id}\n"
        f"Mensagem do usuario: {ctx.request.message}\n\n"
        f"Plano atual: {plan.model_dump_json(ensure_ascii=False)}\n\n"
        f"Advice do retrieval planner: {json.dumps(compact_advice, ensure_ascii=False)}\n\n"
        f"Memoria operacional relevante: {json.dumps(compact_memory, ensure_ascii=False)}\n\n"
        "Use suas tools, busque apenas o necessario e devolva um SpecialistResult grounded."
    )


def build_manager_prompt(
    ctx: Any,
    *,
    plan: Any,
    precomputed_specialist_results: list[Any] | None = None,
) -> str:
    compact_advice = _compact_retrieval_advice(getattr(ctx, "retrieval_advice", None))
    compact_memory = _compact_operational_memory(getattr(ctx, "operational_memory", None))
    compact_results = _compact_specialist_results(precomputed_specialist_results or [])
    preview_hint = getattr(ctx, "preview_hint", None) or {}
    preview_compact = {
        key: value
        for key, value in preview_hint.items()
        if value not in (None, "", [], {})
        and key in {"classification", "retrieval_backend", "allow_graph_rag", "suggested_tools"}
    }
    return (
        "Usuario:\n"
        f"{ctx.request.message}\n\n"
        f"Plano do turno:\n{plan.model_dump_json(ensure_ascii=False)}\n\n"
        f"Advice do retrieval planner:\n{json.dumps(compact_advice, ensure_ascii=False)}\n\n"
        f"Memoria operacional relevante:\n{json.dumps(compact_memory, ensure_ascii=False)}\n\n"
        f"Preview compartilhado:\n{json.dumps(preview_compact, ensure_ascii=False)}\n\n"
        f"Specialist results preexecutados:\n{json.dumps(compact_results, ensure_ascii=False)}\n\n"
        "Voce continua dono da resposta. Use especialistas como tools apenas se faltar evidência. "
        "Priorize uma resposta grounded, humana, objetiva e dinamica."
    )
