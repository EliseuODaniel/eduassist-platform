from __future__ import annotations

import re
from dataclasses import dataclass

from .candidate_builder import ResponseCandidate
from .retrieval_aware_router import EvidenceProbe, topic_terms_for
from .serving_policy import ServingDecision


@dataclass(frozen=True)
class ChosenCandidate:
    candidate: ResponseCandidate
    chooser_reason: str
    scores: dict[str, float]


def _topic_coverage_score(*, candidate: ResponseCandidate, probe: EvidenceProbe) -> float:
    topic_terms = topic_terms_for(probe.topic)
    if not topic_terms:
        return 0.0
    normalized_text = candidate.text.lower()
    hits = 0
    for term in topic_terms:
        normalized_term = term.lower()
        if normalized_term in normalized_text:
            hits += 1
    target = max(1, min(4, len(topic_terms)))
    return min(1.0, hits / target)


def _anchor_overlap_score(*, candidate: ResponseCandidate, probe: EvidenceProbe) -> float:
    if probe.anchor_hits <= 0:
        return 0.0
    tokens = set(re.findall(r"[a-z0-9]{4,}", candidate.text.lower()))
    if not tokens:
        return 0.0
    return min(1.0, len(tokens) / max(12, probe.anchor_hits * 2))


def _score_candidate(*, candidate: ResponseCandidate, probe: EvidenceProbe, policy: ServingDecision) -> float:
    topic_coverage = _topic_coverage_score(candidate=candidate, probe=probe)
    anchor_overlap = _anchor_overlap_score(candidate=candidate, probe=probe)
    score = 0.0
    if candidate.kind == "deterministic":
        score += 2.0
        score += probe.bundle_confidence * 2.0
        if probe.canonical_lane:
            score += 1.0
        if policy.prefer_low_latency:
            score += 0.5
        score += topic_coverage * 1.2
    elif candidate.kind == "documentary_synthesis":
        score += 1.5
        score += min(probe.document_group_count, 3) * 0.9
        score += min(probe.section_diversity, 3) * 0.5
        score += min(probe.summary_store_hits, 2) * 0.8
        score += topic_coverage * 2.2
        score += probe.topic_match_score * 0.9
        if probe.topic in {"extended_day_ecosystem", "governance_channels", "health_reorganization"}:
            score += 1.2
        if candidate.used_llm:
            score += 0.3
        score -= policy.documentary_cost_penalty
    elif candidate.kind == "premium":
        score += 1.0
        score += 0.5 if policy.allow_premium_candidate else -10.0
        score -= policy.premium_cost_penalty
    if probe.profile_bias_score >= 0.75 and "profile" in candidate.reason:
        score -= 2.0
    if probe.bundle_mismatch_risk >= 0.5 and candidate.kind == "deterministic":
        score -= 1.2
    if probe.topic in {"extended_day_ecosystem", "governance_channels", "health_reorganization"}:
        if topic_coverage < 0.35:
            score -= 1.6
        elif topic_coverage >= 0.75:
            score += 0.8
    if candidate.support_count:
        score += min(candidate.support_count, 4) * 0.2
    if candidate.source_count:
        score += min(candidate.source_count, 4) * 0.2
    score += anchor_overlap * 0.4
    if policy.prefer_deterministic and candidate.kind != "deterministic":
        score -= 0.8
    return score


def choose_best_candidate(
    *,
    candidates: list[ResponseCandidate],
    probe: EvidenceProbe,
    policy: ServingDecision,
) -> ChosenCandidate | None:
    valid_candidates = [candidate for candidate in candidates if candidate.text.strip()]
    if not valid_candidates:
        return None
    scored = {
        f"{candidate.kind}:{candidate.reason}": _score_candidate(
            candidate=candidate,
            probe=probe,
            policy=policy,
        )
        for candidate in valid_candidates
    }
    chosen = max(
        valid_candidates,
        key=lambda candidate: (
            _score_candidate(candidate=candidate, probe=probe, policy=policy),
            1 if candidate.kind == "deterministic" else 0,
        ),
    )
    if chosen.kind == "deterministic":
        chooser_reason = "deterministic_candidate_selected"
    elif chosen.kind == "documentary_synthesis":
        chooser_reason = "documentary_candidate_selected"
    else:
        chooser_reason = "premium_candidate_selected"
    if probe.topic in {"extended_day_ecosystem", "governance_channels", "health_reorganization"}:
        chosen_coverage = _topic_coverage_score(candidate=chosen, probe=probe)
        chooser_reason = f"{chooser_reason}:topic_coverage={chosen_coverage:.2f}"
    return ChosenCandidate(
        candidate=chosen,
        chooser_reason=chooser_reason,
        scores=scored,
    )
