from __future__ import annotations

import hashlib
import re
import unicodedata
from dataclasses import dataclass
from typing import Any


def _normalize_text(value: str) -> str:
    text = unicodedata.normalize("NFKD", str(value or ""))
    text = "".join(char for char in text if not unicodedata.combining(char))
    return re.sub(r"\s+", " ", text.lower()).strip()


def _message_matches_term(message: str, term: str) -> bool:
    normalized = _normalize_text(message)
    target = _normalize_text(term)
    if not target:
        return False
    pattern = r"(?<!\w)" + r"\s+".join(re.escape(part) for part in target.split()) + r"(?!\w)"
    return re.search(pattern, normalized) is not None


def _topic_terms() -> dict[str, tuple[str, ...]]:
    return {
        "extended_day_ecosystem": (
            "turno estendido",
            "contraturno",
            "periodo integral",
            "período integral",
            "oficinas",
            "estudo acompanhado",
            "estudo guiado",
            "permanencia",
            "permanência",
            "refeicao",
            "refeição",
        ),
        "governance_channels": (
            "secretaria",
            "coordenacao",
            "coordenação",
            "direcao",
            "direção",
            "canais oficiais",
            "trilha institucional",
            "encaminhamento",
            "escalonamento",
            "protocolo",
        ),
        "health_reorganization": (
            "saude",
            "saúde",
            "atestado",
            "comprovacao de saude",
            "comprovação de saúde",
            "atividade avaliativa",
            "segunda chamada",
            "reorganizacao",
            "reorganização",
            "comunicacao com a familia",
            "comunicação com a família",
        ),
        "visibility_boundary": (
            "portal",
            "login",
            "conta vinculada",
            "canais oficiais",
            "fronteira",
            "aberto",
            "autenticado",
        ),
    }


def topic_terms_for(topic: str | None) -> tuple[str, ...]:
    if not topic:
        return ()
    return _topic_terms().get(topic, ())


def _topic_match_score(*, topic: str | None, texts: list[str]) -> float:
    terms = topic_terms_for(topic)
    if not terms:
        return 0.0
    normalized_text = " ".join(_normalize_text(text) for text in texts if str(text or "").strip())
    if not normalized_text:
        return 0.0
    hits = sum(1 for term in terms if _normalize_text(term) in normalized_text)
    target = max(1, min(4, len(terms)))
    return min(1.0, hits / target)


def _evidence_fingerprint(
    *,
    topic: str | None,
    canonical_lane: str | None,
    labels: set[str],
    parent_ref_keys: set[str],
    query_intent: str | None,
) -> str:
    payload = "|".join(
        [
            topic or "-",
            canonical_lane or "-",
            query_intent or "-",
            ",".join(sorted(label for label in labels if label)[:6]),
            ",".join(sorted(parent_ref_keys)[:4]),
        ]
    )
    if not payload.strip("|- ,"):
        return ""
    return hashlib.sha1(payload.encode("utf-8")).hexdigest()[:16]


@dataclass(frozen=True)
class EvidenceProbe:
    canonical_lane: str | None
    topic: str | None
    document_group_count: int
    section_diversity: int
    support_count: int
    source_count: int
    anchor_hits: int
    profile_bias_score: float
    bundle_confidence: float
    summary_store_hits: int = 0
    parent_ref_key_count: int = 0
    labels: tuple[str, ...] = ()
    hit_count: int = 0
    average_fused_score: float = 0.0
    top_document_score: float = 0.0
    topic_match_score: float = 0.0
    bundle_mismatch_risk: float = 0.0
    evidence_fingerprint: str = ""
    query_intent: str | None = None


@dataclass(frozen=True)
class RoutingDecision:
    prefer_deterministic: bool
    allow_documentary_synthesis: bool
    block_profile_fallback: bool
    reason: str


def infer_public_topic(*, message: str, primary_act: str, secondary_acts: tuple[str, ...] = ()) -> str | None:
    normalized = _normalize_text(message)
    matched: dict[str, int] = {}
    for topic, terms in _topic_terms().items():
        hits = sum(1 for term in terms if _message_matches_term(normalized, term))
        if hits:
            matched[topic] = hits
    if matched:
        return max(matched.items(), key=lambda item: item[1])[0]
    if primary_act in {"service_routing", "contacts", "leadership"}:
        return "governance_channels"
    if primary_act in {"features", "schedule", "operating_hours"} and any(
        act in secondary_acts for act in {"features", "schedule"}
    ):
        return "extended_day_ecosystem"
    if primary_act == "policy":
        return "health_reorganization"
    return None


def build_public_evidence_probe(
    *,
    message: str,
    canonical_lane: str | None,
    primary_act: str,
    secondary_acts: tuple[str, ...],
    evidence_pack: Any | None = None,
    retrieval_search: Any | None = None,
    summary_store_hits: int = 0,
) -> EvidenceProbe:
    supports = list(getattr(evidence_pack, "supports", []) or [])
    document_groups = list(getattr(retrieval_search, "document_groups", []) or [])
    hits = list(getattr(retrieval_search, "hits", []) or [])
    query_plan = getattr(retrieval_search, "query_plan", None)
    section_titles: set[str] = set()
    labels: set[str] = set()
    parent_ref_keys: set[str] = set()
    anchor_hits = 0
    message_normalized = _normalize_text(message)
    evidence_texts: list[str] = []
    fused_scores: list[float] = []
    document_scores: list[float] = []

    for support in supports:
        excerpt = str(getattr(support, "excerpt", "") or "")
        detail = str(getattr(support, "detail", "") or "")
        text = f"{excerpt} {detail}".strip()
        if text:
            evidence_texts.append(text)
        if text:
            for token in re.findall(r"[a-z0-9]{4,}", message_normalized):
                if token in _normalize_text(text):
                    anchor_hits += 1
        label = str(getattr(support, "label", "") or "").strip()
        if label:
            labels.add(_normalize_text(label))

    for group in document_groups:
        for title in list(getattr(group, "section_titles", []) or []):
            cleaned = str(title or "").strip()
            if cleaned:
                section_titles.add(cleaned)
                evidence_texts.append(cleaned)
        parent_ref_key = str(getattr(group, "parent_ref_key", "") or "").strip()
        if parent_ref_key:
            parent_ref_keys.add(parent_ref_key)
        category = str(getattr(group, "category", "") or "").strip()
        if category:
            labels.add(_normalize_text(category))
        primary_excerpt = str(getattr(group, "primary_excerpt", "") or "").strip()
        primary_summary = str(getattr(group, "primary_summary", "") or "").strip()
        if primary_excerpt:
            evidence_texts.append(primary_excerpt)
        if primary_summary:
            evidence_texts.append(primary_summary)
        try:
            document_scores.append(float(getattr(group, "document_score", 0.0) or 0.0))
        except Exception:
            pass

    for hit in hits:
        section_title = str(getattr(hit, "section_title", "") or "").strip()
        if section_title:
            section_titles.add(section_title)
            evidence_texts.append(section_title)
        parent_ref_key = str(getattr(hit, "parent_ref_key", "") or "").strip()
        if parent_ref_key:
            parent_ref_keys.add(parent_ref_key)
        text_excerpt = str(getattr(hit, "text_excerpt", "") or "").strip()
        contextual_summary = str(getattr(hit, "contextual_summary", "") or "").strip()
        if text_excerpt:
            evidence_texts.append(text_excerpt)
        if contextual_summary:
            evidence_texts.append(contextual_summary)
        for key, values in dict(getattr(hit, "labels", {}) or {}).items():
            labels.add(_normalize_text(key))
            for value in values or []:
                labels.add(_normalize_text(str(value or "")))
                evidence_texts.append(str(value or ""))
        try:
            fused_scores.append(float(getattr(hit, "fused_score", 0.0) or 0.0))
        except Exception:
            pass
        try:
            document_scores.append(float(getattr(hit, "document_score", 0.0) or 0.0))
        except Exception:
            pass

    topic = infer_public_topic(
        message=message,
        primary_act=primary_act,
        secondary_acts=secondary_acts,
    )
    query_intent = str(getattr(query_plan, "intent", "") or "").strip() or None
    profile_bias_score = 0.0
    if primary_act in {"highlight", "comparative", "curriculum", "features"}:
        profile_bias_score += 0.6
    if topic in {"governance_channels", "health_reorganization", "extended_day_ecosystem"} and primary_act in {
        "highlight",
        "comparative",
        "curriculum",
    }:
        profile_bias_score += 0.4
    bundle_confidence = 0.0
    if canonical_lane:
        bundle_confidence += 0.55
    if topic:
        bundle_confidence += 0.2
    if len(supports) >= 2:
        bundle_confidence += 0.15
    if document_groups:
        bundle_confidence += 0.1
    topic_match_score = _topic_match_score(topic=topic, texts=evidence_texts)
    bundle_mismatch_risk = 0.0
    if canonical_lane and topic in {"extended_day_ecosystem", "governance_channels", "health_reorganization"}:
        if topic_match_score < 0.25 and (document_groups or hits):
            bundle_mismatch_risk += 0.45
        if profile_bias_score >= 0.75:
            bundle_mismatch_risk += 0.2
    return EvidenceProbe(
        canonical_lane=canonical_lane,
        topic=topic,
        document_group_count=len(document_groups),
        section_diversity=len(section_titles),
        support_count=len(supports),
        source_count=max(len(document_groups), len(parent_ref_keys), len(supports)),
        anchor_hits=anchor_hits,
        profile_bias_score=min(profile_bias_score, 1.0),
        bundle_confidence=min(bundle_confidence, 1.0),
        summary_store_hits=max(0, summary_store_hits),
        parent_ref_key_count=len(parent_ref_keys),
        labels=tuple(sorted(label for label in labels if label)),
        hit_count=len(hits),
        average_fused_score=sum(fused_scores) / len(fused_scores) if fused_scores else 0.0,
        top_document_score=max(document_scores) if document_scores else 0.0,
        topic_match_score=topic_match_score,
        bundle_mismatch_risk=min(bundle_mismatch_risk, 1.0),
        evidence_fingerprint=_evidence_fingerprint(
            topic=topic,
            canonical_lane=canonical_lane,
            labels=labels,
            parent_ref_keys=parent_ref_keys,
            query_intent=query_intent,
        ),
        query_intent=query_intent,
    )


def build_routing_decision(*, probe: EvidenceProbe, llm_forced_mode: bool) -> RoutingDecision:
    documentary_signal = (
        probe.summary_store_hits >= 1
        or probe.document_group_count >= 2
        or probe.section_diversity >= 2
        or probe.hit_count >= 3
        or probe.topic_match_score >= 0.35
        or probe.topic in {"extended_day_ecosystem", "governance_channels", "health_reorganization"}
    )
    allow_documentary = documentary_signal or llm_forced_mode
    prefer_deterministic = bool(
        probe.canonical_lane
        and probe.bundle_confidence >= 0.6
        and probe.bundle_mismatch_risk < 0.5
        and not (
            probe.profile_bias_score >= 0.8
            and probe.topic in {"extended_day_ecosystem", "governance_channels", "health_reorganization"}
        )
    )
    if llm_forced_mode and probe.topic is not None:
        prefer_deterministic = False
    block_profile_fallback = bool(
        probe.topic in {"extended_day_ecosystem", "governance_channels", "health_reorganization"}
        or probe.profile_bias_score >= 0.75
    )
    reason_parts: list[str] = []
    if prefer_deterministic:
        reason_parts.append("deterministic_bundle_confident")
    if allow_documentary:
        reason_parts.append("documentary_enabled")
    if probe.topic_match_score >= 0.35:
        reason_parts.append("topic_match_supported")
    if probe.bundle_mismatch_risk >= 0.5:
        reason_parts.append("bundle_mismatch_risk")
    if block_profile_fallback:
        reason_parts.append("profile_fallback_blocked")
    return RoutingDecision(
        prefer_deterministic=prefer_deterministic,
        allow_documentary_synthesis=allow_documentary,
        block_profile_fallback=block_profile_fallback,
        reason=",".join(reason_parts) or "default_public_routing",
    )
