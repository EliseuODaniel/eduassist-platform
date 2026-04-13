from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any, Callable

from agents import Agent, ModelSettings, RunContextWrapper, Runner

from .models import ManagerDraft, RepairDraft, RetrievalPlannerAdvice, SpecialistResult, SupervisorPlan


@dataclass(frozen=True)
class PlannerSupportDeps:
    normalize_text: Callable[[str | None], str]
    stringify_payload_value: Callable[..., str]
    normalize_string_list: Callable[..., list[str]]
    school_name: Callable[[dict[str, Any] | None], str]
    preview_classification_dict: Callable[[dict[str, Any] | None], dict[str, Any]]
    effective_multi_intent_domains: Callable[[Any, str], list[str]]
    run_config: Callable[..., Any]
    effective_conversation_id: Callable[[Any], str]
    agent_model_for_role: Callable[..., Any]


def json_block(value: str) -> str:
    text = str(value or "").strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    match = re.search(r"\{[\s\S]*\}$", text)
    return match.group(0) if match else text


def normalize_citation_payload(payload: Any) -> dict[str, Any] | None:
    if not isinstance(payload, dict):
        return None
    document_title = str(
        payload.get("document_title")
        or payload.get("title")
        or payload.get("document")
        or payload.get("source")
        or "fonte"
    ).strip()
    version_label = str(payload.get("version_label") or payload.get("version") or "atual").strip()
    storage_path = str(payload.get("storage_path") or payload.get("path") or payload.get("source_path") or "inline").strip()
    chunk_id = str(payload.get("chunk_id") or payload.get("id") or payload.get("section_title") or "inline").strip()
    excerpt = str(payload.get("excerpt") or payload.get("detail") or payload.get("summary") or "").strip()
    if not excerpt:
        section_title = str(payload.get("section_title") or "").strip()
        page_number = payload.get("page_number")
        if section_title and page_number:
            excerpt = f"{section_title} (pagina {page_number})"
        elif section_title:
            excerpt = section_title
        elif page_number:
            excerpt = f"pagina {page_number}"
    return {
        "document_title": document_title or "fonte",
        "version_label": version_label or "atual",
        "storage_path": storage_path or "inline",
        "chunk_id": chunk_id or "inline",
        "excerpt": excerpt or "evidencia resumida",
    }


def normalize_result_payload(
    payload: Any,
    *,
    deps: PlannerSupportDeps,
) -> Any:
    if not isinstance(payload, dict):
        return payload
    normalized = dict(payload)
    confidence = normalized.get("confidence")
    if isinstance(confidence, str):
        confidence_token = confidence.strip().lower()
        confidence_map = {
            "very_high": 0.98,
            "high": 0.9,
            "medium": 0.7,
            "low": 0.45,
            "very_low": 0.2,
        }
        if confidence_token in confidence_map:
            normalized["confidence"] = confidence_map[confidence_token]
        else:
            try:
                confidence = float(confidence_token)
            except Exception:
                confidence = None
    if isinstance(confidence, (int, float)) and not isinstance(confidence, bool):
        numeric_confidence = float(confidence)
        if 1.0 < numeric_confidence <= 5.0:
            numeric_confidence = numeric_confidence / 5.0
        normalized["confidence"] = max(0.0, min(1.0, numeric_confidence))
    for text_key in ("answer_text", "answer_summary", "evidence_summary", "denial_reason", "clarification_question"):
        if normalized.get(text_key) is None:
            normalized[text_key] = ""
        elif not isinstance(normalized.get(text_key), str):
            normalized[text_key] = deps.stringify_payload_value(
                normalized.get(text_key),
                preferred_keys=("text", "answer_text", "answer_summary", "summary", "detail", "message"),
            )
    string_list_keys: dict[str, tuple[str, ...]] = {
        "tool_names": ("tool_name", "name", "id", "label"),
        "support_points": ("text", "summary", "detail", "excerpt", "message", "reason"),
        "specialists_used": ("id", "specialist_id", "name"),
        "suggested_replies": ("text", "label", "title"),
        "repair_notes": ("note", "summary", "detail", "message", "reason"),
        "secondary_domains": ("domain", "name", "id"),
        "recommended_specialists": ("id", "specialist_id", "name"),
        "evidence_queries": ("query", "text", "summary"),
        "issues": ("issue", "reason", "message", "detail", "summary"),
    }
    for list_key, preferred_keys in string_list_keys.items():
        normalized[list_key] = deps.normalize_string_list(normalized.get(list_key), preferred_keys=preferred_keys)
    citations = normalized.get("citations")
    if isinstance(citations, str):
        citations = [citations]
    if isinstance(citations, list):
        normalized["citations"] = [
            normalized_citation
            for item in citations
            if (normalized_citation := normalize_citation_payload(item)) is not None
        ]
    elif citations is None:
        normalized["citations"] = []
    return normalized


def parse_result_model(
    result: Any,
    model_cls: type[Any],
    *,
    deps: PlannerSupportDeps,
) -> Any:
    try:
        return result.final_output_as(model_cls, raise_if_incorrect_type=True)
    except Exception:
        pass
    payload = getattr(result, "final_output", None)
    if isinstance(payload, model_cls):
        return payload
    if isinstance(payload, str):
        try:
            payload = json.loads(json_block(payload))
        except Exception:
            text = str(payload).strip()
            if model_cls is ManagerDraft:
                return ManagerDraft(
                    answer_text=text or "Nao consegui consolidar a resposta premium agora.",
                    answer_summary=(text or "fallback_manager_plain_text")[:240],
                    specialists_used=[],
                    citations=[],
                    suggested_replies=[],
                )
            if model_cls is RepairDraft:
                return RepairDraft(
                    answer_text=text or "Nao consegui reparar a resposta premium agora.",
                    answer_summary=(text or "fallback_repair_plain_text")[:240],
                    specialists_used=[],
                    citations=[],
                    suggested_replies=[],
                    repair_notes=["fallback_plain_text_parse"],
                )
            if model_cls is SpecialistResult:
                return SpecialistResult(
                    specialist_id="institution_specialist",
                    answer_text=text or "Nao consegui estruturar a resposta do especialista.",
                    evidence_summary="fallback_plain_text_parse",
                    tool_names=[],
                    support_points=[],
                    citations=[],
                    confidence=0.4,
                )
    payload = normalize_result_payload(payload, deps=deps)
    return model_cls.model_validate(payload)


def fallback_specialists_for_domain(domain: str, retrieval_backend: str) -> tuple[list[str], str]:
    normalized_domain = str(domain or "institution").strip().lower() or "institution"
    normalized_backend = str(retrieval_backend or "none").strip().lower()
    if normalized_domain == "academic":
        return ["academic_specialist"], "structured_tools"
    if normalized_domain == "finance":
        return ["finance_specialist"], "structured_tools"
    if normalized_domain in {"support", "workflow"}:
        return ["workflow_specialist"], "structured_tools"
    if normalized_backend == "graph_rag":
        return ["document_specialist"], "graph_rag"
    if normalized_backend == "qdrant_hybrid":
        return ["document_specialist"], "hybrid_retrieval"
    return ["institution_specialist"], "direct_answer"


def _supports_structured_planner_outputs(settings: Any) -> bool:
    provider = str(getattr(settings, "llm_provider", "auto") or "auto").strip().lower()
    model_profile = str(getattr(settings, "llm_model_profile", "") or "").strip().lower()
    openai_base_url = str(getattr(settings, "openai_base_url", "") or "").strip().lower()
    openai_model = str(getattr(settings, "openai_model", "") or "").strip().lower()
    if provider != "openai":
        return False
    if model_profile.startswith("gemma"):
        return False
    if openai_base_url and openai_base_url != "https://api.openai.com/v1":
        return False
    if openai_model.startswith("ggml-org") or openai_model.endswith(".gguf"):
        return False
    return True


def preferred_direct_specialist_for_category(
    ctx: Any,
    *,
    execution_specialists: set[str],
    primary_domain: str,
    preferred_category: str | None,
) -> str | None:
    category = str(preferred_category or "").strip().lower()
    if not category:
        return None
    for specialist_id, spec in ctx.specialist_registry.items():
        if specialist_id not in execution_specialists:
            continue
        if primary_domain not in getattr(spec, "supported_domains", []):
            continue
        if getattr(spec, "manager_policy", "always") != "prefer_direct":
            continue
        preferred_categories = [str(item).strip().lower() for item in getattr(spec, "preferred_categories", [])]
        if category in preferred_categories:
            return specialist_id
    return None


def normalize_retrieval_advice(
    ctx: Any,
    advice: RetrievalPlannerAdvice,
    *,
    deps: PlannerSupportDeps,
    execution_specialists: set[str],
) -> RetrievalPlannerAdvice:
    preview = ctx.preview_hint or {}
    preview_classification = deps.preview_classification_dict(ctx.preview_hint)
    preview_domain = str(preview_classification.get("domain") or "institution").strip().lower() or "institution"
    preview_backend = str(preview.get("retrieval_backend") or "none").strip().lower()
    default_specialists, default_strategy = fallback_specialists_for_domain(preview_domain, preview_backend)
    specialists = [item for item in advice.recommended_specialists if item in execution_specialists]
    if not specialists and advice.retrieval_strategy not in {"clarify", "deny"}:
        specialists = default_specialists
    strategy = advice.retrieval_strategy
    if strategy == "direct_answer" and advice.requires_grounding:
        strategy = default_strategy
    if advice.primary_domain in {"academic", "finance", "support", "workflow"} and strategy == "direct_answer":
        strategy = "structured_tools"
    primary_domain = str(advice.primary_domain or preview_domain).strip().lower() or preview_domain
    secondary_domains = [item for item in advice.secondary_domains if item and item != primary_domain]
    detected_multi_domains = deps.effective_multi_intent_domains(ctx.operational_memory, ctx.request.message)
    if "academic" in detected_multi_domains and "finance" in detected_multi_domains:
        for domain in ("academic", "finance"):
            if domain != primary_domain and domain not in secondary_domains:
                secondary_domains.append(domain)
        for specialist_id in ("academic_specialist", "finance_specialist"):
            if specialist_id not in specialists:
                specialists.append(specialist_id)
        strategy = "structured_tools"
    evidence_queries = [str(item).strip() for item in advice.evidence_queries if str(item).strip()]
    if not evidence_queries:
        evidence_queries = [ctx.request.message]
    direct_specialist = preferred_direct_specialist_for_category(
        ctx,
        execution_specialists=execution_specialists,
        primary_domain=primary_domain,
        preferred_category=advice.preferred_category,
    )
    if (
        direct_specialist is not None
        and primary_domain in {"institution", "academic", "finance", "support"}
        and strategy in {"direct_answer", "document_search", "hybrid_retrieval", "structured_tools"}
        and len(specialists) >= 1
    ):
        specialists = [direct_specialist]
        strategy = "structured_tools" if primary_domain in {"academic", "finance", "support", "institution"} else strategy
    if len(specialists) == 1 and len(detected_multi_domains) <= 1:
        secondary_domains = []
    return advice.model_copy(
        update={
            "primary_domain": primary_domain,
            "secondary_domains": secondary_domains,
            "retrieval_strategy": strategy,
            "recommended_specialists": specialists,
            "evidence_queries": evidence_queries[:3],
            "requires_grounding": advice.requires_grounding
            or strategy in {"structured_tools", "hybrid_retrieval", "graph_rag", "document_search", "workflow_status", "pricing_projection"},
        }
    )


def normalize_plan_with_retrieval_advice(
    ctx: Any,
    plan: SupervisorPlan,
    retrieval_advice: RetrievalPlannerAdvice | None,
    *,
    deps: PlannerSupportDeps,
    execution_specialists: set[str],
) -> SupervisorPlan:
    preview = ctx.preview_hint or {}
    preview_classification = deps.preview_classification_dict(ctx.preview_hint)
    preview_domain = str(preview_classification.get("domain") or "institution").strip().lower() or "institution"
    preview_backend = str(preview.get("retrieval_backend") or "none").strip().lower()
    fallback_specialists, fallback_strategy = fallback_specialists_for_domain(preview_domain, preview_backend)
    primary_domain = str(plan.primary_domain or preview_domain).strip().lower() or preview_domain
    retrieval_strategy = plan.retrieval_strategy
    specialists = [item for item in plan.specialists if item in execution_specialists]
    secondary_domains = [item for item in plan.secondary_domains if item and item != primary_domain]
    confidence = plan.confidence
    reasoning_summary = plan.reasoning_summary
    requires_clarification = plan.requires_clarification
    clarification_question = plan.clarification_question
    should_deny = plan.should_deny
    denial_reason = plan.denial_reason
    request_kind = plan.request_kind
    if retrieval_advice is not None:
        primary_domain = retrieval_advice.primary_domain or primary_domain
        for item in retrieval_advice.secondary_domains:
            if item and item != primary_domain and item not in secondary_domains:
                secondary_domains.append(item)
        if retrieval_advice.recommended_specialists:
            for item in retrieval_advice.recommended_specialists:
                if item in execution_specialists and item not in specialists:
                    specialists.append(item)
        if retrieval_advice.retrieval_strategy != "direct_answer" or retrieval_advice.requires_grounding:
            retrieval_strategy = retrieval_advice.retrieval_strategy
        if retrieval_advice.requires_clarification:
            requires_clarification = True
            clarification_question = retrieval_advice.clarification_question or clarification_question
        if retrieval_advice.should_deny:
            should_deny = True
            denial_reason = retrieval_advice.denial_reason or denial_reason
        if retrieval_advice.secondary_domains:
            request_kind = "multi_domain" if len(retrieval_advice.secondary_domains) >= 1 else request_kind
        confidence = max(confidence, retrieval_advice.confidence)
        reasoning_summary = retrieval_advice.rationale or reasoning_summary
    if not specialists and retrieval_strategy not in {"clarify", "deny"}:
        specialists = fallback_specialists
    if primary_domain in {"academic", "finance"} and retrieval_strategy == "direct_answer":
        retrieval_strategy = "structured_tools"
    if "academic" in secondary_domains and "finance" in secondary_domains:
        request_kind = "multi_domain"
        retrieval_strategy = "structured_tools"
        for item in ("academic_specialist", "finance_specialist"):
            if item not in specialists:
                specialists.append(item)
    if primary_domain == "finance" and "academic" in secondary_domains:
        request_kind = "multi_domain"
        retrieval_strategy = "structured_tools"
        if "academic_specialist" not in specialists:
            specialists.append("academic_specialist")
    if primary_domain == "academic" and "finance" in secondary_domains:
        request_kind = "multi_domain"
        retrieval_strategy = "structured_tools"
        if "finance_specialist" not in specialists:
            specialists.append("finance_specialist")
    return plan.model_copy(
        update={
            "request_kind": request_kind,
            "primary_domain": primary_domain,
            "secondary_domains": secondary_domains,
            "specialists": specialists,
            "retrieval_strategy": retrieval_strategy if not should_deny else "deny",
            "requires_clarification": requires_clarification,
            "clarification_question": clarification_question,
            "should_deny": should_deny,
            "denial_reason": denial_reason,
            "reasoning_summary": reasoning_summary,
            "confidence": confidence,
        }
    )


def planner_instructions(
    context: RunContextWrapper[Any],
    agent: Agent[Any],
    *,
    deps: PlannerSupportDeps,
    execution_specialists: set[str],
) -> str:
    ctx = context.context
    preview = ctx.preview_hint or {}
    operational_memory = ctx.operational_memory.model_dump(mode="json") if ctx.operational_memory is not None else {}
    retrieval_advice = ctx.retrieval_advice.model_dump(mode="json") if ctx.retrieval_advice is not None else {}
    resolved_turn = ctx.resolved_turn.model_dump(mode="json") if ctx.resolved_turn is not None else {}
    school_name = deps.school_name(ctx.school_profile)
    recent_messages = [
        f"{item.get('sender_type')}: {item.get('content')}"
        for item in (ctx.conversation_context or {}).get("recent_messages", [])
        if isinstance(item, dict)
    ][:6]
    registry_lines = [
        f"- {spec.name} ({spec.id}): {spec.description}"
        for spec in ctx.specialist_registry.values()
        if spec.id in execution_specialists
    ]
    return (
        "Voce e o retrieval planner do caminho quality-first. "
        "Escolha a menor combinacao de especialistas que maximize qualidade e grounding. "
        f"O chatbot ja esta no contexto do {school_name}; nao peca o nome da escola quando a pergunta for sobre a propria instituicao atual. "
        "Prefira structured tools para dados transacionais; use hybrid retrieval para documentos; "
        "use GraphRAG para panorama multi-documento; use pricing_projection para simulacoes publicas. "
        "Se a pergunta estiver ambigua, peca clarificacao. "
        f"\n\nPreview compartilhado: {json.dumps(preview, ensure_ascii=False)}"
        f"\nTurno resolvido: {json.dumps(resolved_turn, ensure_ascii=False)}"
        f"\nMemoria operacional: {json.dumps(operational_memory, ensure_ascii=False)}"
        f"\nAdvice do retrieval planner especialista: {json.dumps(retrieval_advice, ensure_ascii=False)}"
        f"\nMensagens recentes: {json.dumps(recent_messages, ensure_ascii=False)}"
        f"\nEspecialistas disponiveis:\n" + "\n".join(registry_lines)
    )


def retrieval_planner_instructions(
    context: RunContextWrapper[Any],
    agent: Agent[Any],
    *,
    deps: PlannerSupportDeps,
) -> str:
    ctx = context.context
    preview = ctx.preview_hint or {}
    operational_memory = ctx.operational_memory.model_dump(mode="json") if ctx.operational_memory is not None else {}
    resolved_turn = ctx.resolved_turn.model_dump(mode="json") if ctx.resolved_turn is not None else {}
    school_name = deps.school_name(ctx.school_profile)
    recent_messages = [
        f"{item.get('sender_type')}: {item.get('content')}"
        for item in (ctx.conversation_context or {}).get("recent_messages", [])
        if isinstance(item, dict)
    ][:6]
    return (
        "Voce e o Retrieval Planner Specialist do caminho quality-first. "
        "Sua funcao e decidir a melhor estrategia de evidencia antes da composicao final. "
        f"O chatbot ja esta operando no contexto do {school_name}; nao peca o nome da escola quando a pergunta for sobre a instituicao atual. "
        "Escolha entre direct_answer, structured_tools, hybrid_retrieval, graph_rag, document_search, pricing_projection, workflow_status, clarify ou deny. "
        "Perguntas escolares, institucionais, academicas, financeiras, de suporte ou workflow normalmente exigem grounding. "
        "Nao trate perguntas da escola como conhecimento geral quando houver sinal de dominio escolar. "
        "Se a mensagem combinar dois dominios, como notas e boletos, marque academic e finance juntos e recomende ambos os especialistas. "
        "Quando a pergunta pedir regra institucional, frequencia, BNCC, projeto de vida, aprovacao ou recuperacao, preserve grounding forte e favoreca get_public_profile_bundle/fetch_academic_policy ou especialistas apropriados. "
        "Retorne tambem queries uteis para evidencias quando isso ajudar a busca documental. "
        f"\n\nMensagem atual: {ctx.request.message}"
        f"\nPreview compartilhado: {json.dumps(preview, ensure_ascii=False)}"
        f"\nTurno resolvido: {json.dumps(resolved_turn, ensure_ascii=False)}"
        f"\nMemoria operacional: {json.dumps(operational_memory, ensure_ascii=False)}"
        f"\nMensagens recentes: {json.dumps(recent_messages, ensure_ascii=False)}"
    )


async def run_retrieval_planner(
    ctx: Any,
    *,
    deps: PlannerSupportDeps,
    execution_specialists: set[str],
    logger: Any,
) -> RetrievalPlannerAdvice:
    structured = _supports_structured_planner_outputs(ctx.settings)
    if not structured:
        preview = ctx.preview_hint or {}
        classification = deps.preview_classification_dict(ctx.preview_hint)
        domain = str(classification.get("domain") or "institution").strip().lower() or "institution"
        retrieval_backend = str(preview.get("retrieval_backend") or "none").strip().lower()
        specialists, strategy = fallback_specialists_for_domain(domain, retrieval_backend)
        advice = RetrievalPlannerAdvice(
            normalized_query=ctx.request.message.strip(),
            primary_domain=domain,
            retrieval_strategy=strategy,
            recommended_specialists=specialists,
            preferred_category=None,
            evidence_queries=[ctx.request.message.strip()],
            requires_grounding=strategy != "direct_answer",
            rationale="retrieval_planner_preview_fallback_local_llm",
            confidence=0.35,
        )
        normalized = normalize_retrieval_advice(ctx, advice, deps=deps, execution_specialists=execution_specialists)
        ctx.retrieval_advice = normalized
        return normalized
    agent = Agent(
        name="Retrieval Planner Specialist",
        model=deps.agent_model_for_role(ctx.settings, role="planner"),
        model_settings=ModelSettings(temperature=0.0, verbosity="low"),
        instructions=lambda context, agent: retrieval_planner_instructions(context, agent, deps=deps),
        output_type=RetrievalPlannerAdvice,
    )
    try:
        result = await Runner.run(
            agent,
            f"Mensagem do usuario: {ctx.request.message}",
            context=ctx,
            max_turns=3,
            run_config=deps.run_config(ctx.settings, conversation_id=deps.effective_conversation_id(ctx.request)),
        )
        advice = result.final_output_as(RetrievalPlannerAdvice, raise_if_incorrect_type=True)
    except Exception:
        logger.exception("specialist_supervisor_retrieval_planner_failed")
        preview = ctx.preview_hint or {}
        classification = deps.preview_classification_dict(ctx.preview_hint)
        domain = str(classification.get("domain") or "institution").strip().lower() or "institution"
        retrieval_backend = str(preview.get("retrieval_backend") or "none").strip().lower()
        specialists, strategy = fallback_specialists_for_domain(domain, retrieval_backend)
        advice = RetrievalPlannerAdvice(
            normalized_query=ctx.request.message.strip(),
            primary_domain=domain,
            retrieval_strategy=strategy,
            recommended_specialists=specialists,
            preferred_category=None,
            evidence_queries=[ctx.request.message.strip()],
            requires_grounding=strategy != "direct_answer",
            rationale="retrieval_planner_fallback_from_preview_hint",
            confidence=0.35,
        )
    normalized = normalize_retrieval_advice(ctx, advice, deps=deps, execution_specialists=execution_specialists)
    ctx.retrieval_advice = normalized
    return normalized


async def run_planner(
    ctx: Any,
    *,
    deps: PlannerSupportDeps,
    execution_specialists: set[str],
    logger: Any,
) -> SupervisorPlan:
    structured = _supports_structured_planner_outputs(ctx.settings)
    if not structured:
        advice = ctx.retrieval_advice
        if advice is not None:
            specialists = [item for item in advice.recommended_specialists if item in execution_specialists]
            strategy = advice.retrieval_strategy
            domain = advice.primary_domain
            secondary_domains = [item for item in advice.secondary_domains if item and item != advice.primary_domain]
        else:
            preview = ctx.preview_hint or {}
            classification = deps.preview_classification_dict(ctx.preview_hint)
            domain = str(classification.get("domain") or "institution").strip().lower() or "institution"
            retrieval_backend = str(preview.get("retrieval_backend") or "none").strip().lower()
            specialists, strategy = fallback_specialists_for_domain(domain, retrieval_backend)
            secondary_domains = []
        return normalize_plan(
            ctx,
            SupervisorPlan(
                request_kind="question",
                primary_domain=domain,
                secondary_domains=secondary_domains,
                specialists=specialists,
                retrieval_strategy=strategy,
                requires_clarification=False,
                clarification_question=None,
                should_deny=False,
                denial_reason=None,
                reasoning_summary="planner_preview_fallback_local_llm",
                confidence=0.35,
            ),
            deps=deps,
            execution_specialists=execution_specialists,
        )
    agent = Agent(
        name="Retrieval Planner",
        model=deps.agent_model_for_role(ctx.settings, role="planner"),
        model_settings=ModelSettings(temperature=0.0, verbosity="low"),
        instructions=lambda context, agent: planner_instructions(
            context,
            agent,
            deps=deps,
            execution_specialists=execution_specialists,
        ),
        output_type=SupervisorPlan,
    )
    try:
        result = await Runner.run(
            agent,
            f"Mensagem do usuario: {ctx.request.message}",
            context=ctx,
            max_turns=3,
            run_config=deps.run_config(ctx.settings, conversation_id=deps.effective_conversation_id(ctx.request)),
        )
        plan = result.final_output_as(SupervisorPlan, raise_if_incorrect_type=True)
    except Exception:
        logger.exception("specialist_supervisor_planner_failed")
        advice = ctx.retrieval_advice
        if advice is not None:
            specialists = [item for item in advice.recommended_specialists if item in execution_specialists]
            strategy = advice.retrieval_strategy
            domain = advice.primary_domain
        else:
            preview = ctx.preview_hint or {}
            classification = deps.preview_classification_dict(ctx.preview_hint)
            domain = str(classification.get("domain") or "institution").strip().lower() or "institution"
            retrieval_backend = str(preview.get("retrieval_backend") or "none").strip().lower()
            specialists, strategy = fallback_specialists_for_domain(domain, retrieval_backend)
        plan = SupervisorPlan(
            request_kind="multi_domain" if advice is not None and advice.secondary_domains else "simple",
            primary_domain=domain,
            secondary_domains=advice.secondary_domains if advice is not None else [],
            specialists=specialists,
            retrieval_strategy=strategy,
            requires_clarification=bool(advice.requires_clarification) if advice is not None else False,
            clarification_question=advice.clarification_question if advice is not None else None,
            should_deny=bool(advice.should_deny) if advice is not None else False,
            denial_reason=advice.denial_reason if advice is not None else None,
            reasoning_summary=advice.rationale if advice is not None and advice.rationale else "planner_fallback_from_preview_hint",
            confidence=advice.confidence if advice is not None else 0.35,
        )
    return normalize_plan_with_retrieval_advice(ctx, plan, ctx.retrieval_advice, deps=deps, execution_specialists=execution_specialists)
